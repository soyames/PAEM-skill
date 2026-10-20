#!/usr/bin/env python3
"""Checkpoint health detection shared by provider Stop-hook adapters.

Managed checkpoints are bound to repository content and publication metadata.
Legacy checkpoints receive conservative schema, HEAD and mtime checks. Unexpected
I/O or Git failures propagate to adapters, which report unknown health and allow
stopping. A healthy checkpoint preserves self-reported verification; it does not
prove tests passed. Time budgets are advisory context for already-stale work.
"""

from __future__ import annotations

import re
import hashlib
import math
import subprocess
import time
from pathlib import Path

RATE_LIMIT_PHRASES = (
    "rate limit",
    "rate_limit",
    "quota exceeded",
    "usage limit",
    "usage cap",
    "429",
    "try again later",
    "you've hit your limit",
    "you have reached your",
)


def git_dirty_files(project_root: Path) -> list[str] | None:
    """Decode NUL-delimited status; spaces, Unicode and rename paths stay intact."""
    from paem_repository import dirty_entries
    try:
        return [entry["path"] for entry in dirty_entries(project_root)]
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def newest_mtime(project_root: Path, rel_paths: list[str]) -> float:
    newest = 0.0
    for rel in rel_paths:
        try:
            newest = max(newest, (project_root / rel).stat().st_mtime)
        except OSError:
            continue
    return newest


def session_elapsed_minutes(paem_dir: Path, session_id: str | None) -> float | None:
    """Wall-clock minutes since this session_id was first seen by any guard.

    Uses a marker file keyed by session_id rather than parsing any
    provider's transcript format for a start time - session_id is the one
    field several providers' hook payloads are documented to share, and
    writing our own marker means we never have to guess a timestamp field
    name we haven't verified.
    """
    if not isinstance(session_id, str) or not session_id:
        return None
    guard_dir = paem_dir / ".guard"
    from paem_fs import safe_path
    marker = safe_path(paem_dir, ".guard/session-" + hashlib.sha256(session_id.encode()).hexdigest() + ".start")
    now = time.time()
    try:
        if marker.is_file():
            started = float(marker.read_text(encoding="utf-8").strip())
        else:
            guard_dir.mkdir(parents=True, exist_ok=True)
            marker.write_text(str(now), encoding="utf-8")
            started = now
    except (OSError, ValueError):
        return None
    return (now - started) / 60.0 if math.isfinite(started) else None


def budget_threshold_minutes(project_root: Path, provider_key: str) -> float | None:
    """Read the soft checkpoint threshold for `provider_key` from
    .paem/provider_budgets.md, if the user has filled one in.

    Looks for a markdown table row starting with `| provider_key |` and
    pulls the first integer followed by "min" out of the row. Returns None
    (not "don't block") on anything it can't confidently parse - an absent
    or malformed budgets file should never be treated as "0 minutes."
    """
    path = project_root / ".paem" / "provider_budgets.md"
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or cells[0].lower() != provider_key.lower():
            continue
        match = re.search(r"(\d+)\s*min", stripped, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
    return None


def transcript_has_rate_limit_signal(transcript_path: str | None) -> bool:
    """Best-effort raw-text scan for rate-limit phrasing.

    Deliberately does not parse the transcript's structure (JSONL schema,
    field names) - those differ by provider and version, and getting them
    wrong would silently break this check. Scanning raw file text for known
    phrases works regardless of schema and only ever adds a nudge, never a
    hard requirement, so a false negative here just means one fewer signal,
    not an incorrect claim.
    """
    if not transcript_path:
        return False
    path = Path(transcript_path)
    try:
        if not path.is_file():
            return False
        with path.open("rb") as stream:
            stream.seek(max(0, path.stat().st_size - 20000))
            text = stream.read(20000).decode("utf-8", errors="ignore")
    except OSError:
        return False
    tail = text[-20000:].lower()  # only the recent tail is relevant
    return any(phrase in tail for phrase in RATE_LIMIT_PHRASES)


def evaluate(
    project_root: Path,
    provider_key: str,
    session_id: str | None = None,
    transcript_path: str | None = None,
) -> tuple[bool, str]:
    """Block known invalid/stale state; unexpected errors are handled by adapters.

    Allowing a stop is not proof of test success. Legacy checkpoints get schema,
    HEAD and conservative mtime checks; managed saves get content fingerprints.
    """
    from paem_checkpoint import inspect, read_json, validate_record
    from paem_fs import safe_path
    from paem_repository import snapshot

    paem_dir = safe_path(project_root, ".paem")
    if not paem_dir.is_dir():
        return False, ""
    elapsed = session_elapsed_minutes(paem_dir, session_id)
    if safe_path(paem_dir, "current.json").exists():
        result = inspect(project_root)
        if result["status"] == "current":
            return False, ""
        if result["status"] == "unavailable":
            raise ValueError("Checkpoint health unknown: " + "; ".join(result["reasons"]))
        return True, "PAEM: " + result["status"] + " checkpoint: " + "; ".join(result["reasons"]) + ". Inspect state before resuming."

    latest = safe_path(paem_dir, "latest_checkpoint.json")
    dirty_files = git_dirty_files(project_root)
    if not latest.is_file():
        return (True, "PAEM: no checkpoint has been published; save a checkpoint before ending this turn.") if dirty_files else (False, "")
    try:
        record = read_json(latest)
        errors = validate_record(record)
    except (ValueError, UnicodeError) as exc:
        errors = [str(exc)]
    if errors:
        return True, "PAEM: invalid checkpoint: " + "; ".join(errors) + ". Preserve the original and repair explicitly."
    try:
        observed = snapshot(project_root)
    except (OSError, ValueError) as exc:
        raise ValueError("Checkpoint health unknown: " + str(exc)) from exc
    if record.get("branch") is not None and record["branch"] != observed["branch"]:
        return True, "PAEM: checkpoint branch differs; inspect before continuing."
    saved_head = record.get("commit_hash")
    if saved_head and (not observed["head"] or not observed["head"].startswith(saved_head)):
        return True, "PAEM: checkpoint HEAD differs; verification belongs to an older revision."
    # mtime cannot prove deletion/rename/staged-only changes. Ask for a managed
    # save rather than silently considering these states fresh.
    from paem_repository import dirty_entries
    entries = dirty_entries(project_root)
    structurally_dirty = any(any(flag in entry["status"] for flag in "DRCU") or entry["status"][0] not in " ?" for entry in entries)
    stale = structurally_dirty or newest_mtime(project_root, dirty_files or []) > latest.stat().st_mtime
    if stale:
        message = "PAEM: working tree changed since the checkpoint; publish a checkpoint with scripts/paem_checkpoint.py save."
        threshold = budget_threshold_minutes(project_root, provider_key)
        if elapsed is not None and threshold is not None and elapsed > threshold:
            message += " The configured soft time threshold also elapsed; this is not quota telemetry."
        return True, message
    return False, ""
