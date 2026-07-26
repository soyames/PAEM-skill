#!/usr/bin/env python3
"""PAEM checkpoint guard - optional Claude Code `Stop` hook.

This script does NOT run as part of this repo's own CI (that's
scripts/validate_skill.py). It is a runtime artifact meant to be copied into
a project PAEM is managing and wired into that project's
`.claude/settings.json` as a `Stop` hook, so that "write a checkpoint before
stopping" is enforced deterministically instead of relying on the model
remembering to do it every time. See examples/claude.md for the exact
settings.json snippet.

What it does, each time Claude Code is about to end a turn:
  1. Reads the hook's JSON payload from stdin.
  2. If a previous Stop hook already forced this same turn to continue once
     (`stop_hook_active`), let it stop now - never loop forever.
  3. If the project has no `.paem/` directory, PAEM isn't active here: allow
     the stop.
  4. Otherwise, compare `.paem/latest_checkpoint.json`'s mtime against the
     repo's working-tree changes. If there is uncommitted or untracked work
     newer than the last checkpoint (or no checkpoint exists at all despite
     changes), block the stop (exit 2) and tell Claude to write one.

Fails open: any unexpected error (missing git, unreadable files, malformed
checkpoint JSON) is reported but does not block the stop. A buggy guard
should never be able to trap a session - it should just skip the extra
safety check for that turn.

Opt-out: set PAEM_SKIP_GUARD=1 in the environment to always allow stopping
(e.g. when deliberately abandoning uncommitted exploratory work).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

EXIT_ALLOW = 0
EXIT_BLOCK = 2


def _git_dirty_files(project_root: Path) -> list[str] | None:
    """Return paths with uncommitted/untracked changes, or None if not a git repo."""
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
        # Porcelain format: "XY path" (rename lines use "XY old -> new").
        path = line[3:].split(" -> ")[-1].strip()
        if path and not path.startswith(".paem/"):
            files.append(path)
    return files


def _newest_mtime(project_root: Path, rel_paths: list[str]) -> float:
    newest = 0.0
    for rel in rel_paths:
        path = project_root / rel
        try:
            newest = max(newest, path.stat().st_mtime)
        except OSError:
            continue
    return newest


def main() -> int:
    if os.environ.get("PAEM_SKIP_GUARD") == "1":
        return EXIT_ALLOW

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    if payload.get("stop_hook_active"):
        return EXIT_ALLOW

    project_root = Path(payload.get("cwd") or os.getcwd())
    paem_dir = project_root / ".paem"

    if not paem_dir.is_dir():
        return EXIT_ALLOW  # PAEM isn't initialized for this project.

    latest_checkpoint = paem_dir / "latest_checkpoint.json"

    try:
        dirty_files = _git_dirty_files(project_root)

        if dirty_files is None:
            # No git available - only enforce the minimal bar: a checkpoint
            # must exist at all. We can't cheaply tell "stale" from "fresh"
            # without git, and scanning the whole tree is too expensive/noisy.
            if not latest_checkpoint.is_file():
                sys.stderr.write(
                    "PAEM: no .paem/latest_checkpoint.json exists yet. "
                    "Write an initial checkpoint (see prompts/checkpoint.md) "
                    "before ending this turn.\n"
                )
                return EXIT_BLOCK
            return EXIT_ALLOW

        if not dirty_files:
            return EXIT_ALLOW  # Clean working tree - nothing to checkpoint.

        if not latest_checkpoint.is_file():
            sys.stderr.write(
                "PAEM: there are uncommitted changes but no checkpoint has "
                "ever been written. Write .paem/latest_checkpoint.json "
                "(see prompts/checkpoint.md) before ending this turn.\n"
            )
            return EXIT_BLOCK

        checkpoint_mtime = latest_checkpoint.stat().st_mtime
        newest_change = _newest_mtime(project_root, dirty_files)

        if newest_change > checkpoint_mtime:
            sys.stderr.write(
                "PAEM: working tree has changes newer than the last "
                f"checkpoint ({len(dirty_files)} file(s) modified since). "
                "Update .paem/latest_checkpoint.json and companion files "
                "(see prompts/checkpoint.md) before ending this turn, or set "
                "PAEM_SKIP_GUARD=1 if this work is intentionally uncheckpointed.\n"
            )
            return EXIT_BLOCK

        return EXIT_ALLOW

    except Exception as exc:  # noqa: BLE001 - fail open, never trap the session
        sys.stderr.write(f"PAEM checkpoint guard skipped due to an error: {exc}\n")
        return EXIT_ALLOW


if __name__ == "__main__":
    sys.exit(main())
