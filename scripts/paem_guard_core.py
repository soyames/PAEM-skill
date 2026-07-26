#!/usr/bin/env python3
"""Shared detection logic for PAEM's per-provider checkpoint guards.

This module has no provider-specific code in it - it does not know what
"exit code 2" or a JSON `decision` field mean to any particular host. Each
`paem_checkpoint_guard_<provider>.py` adapter is a thin wrapper that reads
that provider's hook payload, calls `evaluate()` here, and translates the
result into whatever that provider's hook contract expects. Keeping the
detection logic in one place means it only needs to be correct once, and
every adapter stays honest about what it actually checked.

What evaluate() checks, in order:

1. Is `.paem/` even present? If not, PAEM isn't active for this project -
   nothing to enforce.
2. Is the git working tree clean? If so, there's nothing to checkpoint -
   allow.
3. Does a checkpoint exist at all? If there's dirty work and no checkpoint
   has ever been written, block.
4. Is the latest checkpoint stale relative to the dirtiest file? If the
   working tree changed after the last checkpoint was written, block.
5. Elapsed-time budget (best-effort, opt-in): if `.paem/provider_budgets.md`
   defines a soft threshold for this provider and the session has been
   running longer than that with dirty, uncheckpointed work, block with a
   proactive "you're likely approaching a limit" message. This never claims
   to know real quota - see templates/provider_budgets.md for why that's
   not possible.
6. Rate-limit phrase scan (best-effort, opt-in): if a transcript path is
   given and its raw text contains a known rate-limit/quota phrase, and
   there's dirty uncheckpointed work, block immediately - this signal beats
   the time budget because it's an observed fact, not a heuristic.

Every check fails open: a missing file, unreadable transcript, malformed
provider_budgets.md, or any other unexpected condition is treated as "don't
know, don't block" rather than raising. A guard should never be able to trap
a session because of its own bug.
"""

from __future__ import annotations

import re
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
    """Paths with uncommitted/untracked changes, or None if not a git repo."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    files = []
    for line in result.stdout.splitlines():
        path = line[3:].split(" -> ")[-1].strip()
        if path and not path.startswith(".paem/"):
            files.append(path)
    return files


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
    if not session_id:
        return None
    guard_dir = paem_dir / ".guard"
    marker = guard_dir / f"session-{session_id}.start"
    now = time.time()
    try:
        if marker.is_file():
            started = float(marker.read_text(encoding="utf-8").strip())
        else:
            guard_dir.mkdir(parents=True, exist_ok=True)
            marker.write_text(str(now), encoding="utf-8")
            started = now
    except OSError:
        return None
    return (now - started) / 60.0


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
        text = path.read_text(encoding="utf-8", errors="ignore")
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
    """Returns (should_block, message). message is empty when not blocking."""
    paem_dir = project_root / ".paem"
    if not paem_dir.is_dir():
        return False, ""

    latest_checkpoint = paem_dir / "latest_checkpoint.json"
    dirty_files = git_dirty_files(project_root)

    if dirty_files is None:
        if not latest_checkpoint.is_file():
            return False, ""  # can't assess staleness without git; don't guess
        return False, ""

    if not dirty_files:
        return False, ""  # clean tree, nothing to checkpoint

    if not latest_checkpoint.is_file():
        return True, (
            "PAEM: there are uncommitted changes but no checkpoint has ever "
            "been written. Write .paem/latest_checkpoint.json "
            "(see prompts/checkpoint.md) before ending this turn."
        )

    checkpoint_mtime = latest_checkpoint.stat().st_mtime
    newest_change = newest_mtime(project_root, dirty_files)

    if newest_change > checkpoint_mtime:
        return True, (
            "PAEM: working tree has changes newer than the last checkpoint "
            f"({len(dirty_files)} file(s) modified since). Update "
            ".paem/latest_checkpoint.json and companion files (see "
            "prompts/checkpoint.md) before ending this turn, or set "
            "PAEM_SKIP_GUARD=1 if this work is intentionally uncheckpointed."
        )

    if transcript_has_rate_limit_signal(transcript_path):
        return True, (
            "PAEM: this session's transcript mentions a rate limit or quota "
            "signal. Checkpoint now (even if the last checkpoint isn't "
            "technically stale) so recovery is ready before the session ends."
        )

    elapsed = session_elapsed_minutes(paem_dir, session_id)
    threshold = budget_threshold_minutes(project_root, provider_key)
    if elapsed is not None and threshold is not None and elapsed > threshold:
        return True, (
            f"PAEM: this session has been running ~{elapsed:.0f} min, past "
            f"the {threshold:.0f} min soft threshold you set in "
            ".paem/provider_budgets.md for this provider. This is a "
            "heuristic, not a real quota check, but checkpoint now while "
            "you can - see prompts/checkpoint.md."
        )

    return False, ""
