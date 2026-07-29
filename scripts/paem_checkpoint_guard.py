#!/usr/bin/env python3
"""PAEM checkpoint guard - Claude Code `Stop` hook adapter.

Wire this into a project's `.claude/settings.json` as a `Stop` hook (see
examples/claude.md) so "save execution state before exiting" is enforced
deterministically instead of relying on the model remembering to do it every
time. All detection logic lives in scripts/paem_guard_core.py, shared with
the other providers' adapters - this file only knows Claude Code's specific
stdin/exit-code contract:

  - stdin: JSON with `cwd`, `session_id`, `transcript_path`,
    `stop_hook_active` (true if a previous Stop hook already forced this
    turn to continue once - checked to avoid an infinite loop).
  - exit 0 = allow the stop.
  - exit 2 = block; stderr is fed back to Claude as the reason.

This adapter is verified against Claude Code's documented hook behavior and
tested locally (staleness detection, budget threshold, loop guard, opt-out).

Opt-out: set PAEM_SKIP_GUARD=1 in the environment to always allow stopping.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paem_guard_core import evaluate  # noqa: E402

EXIT_ALLOW = 0
EXIT_BLOCK = 2


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

    try:
        should_block, message = evaluate(
            project_root,
            provider_key="claude-code",
            session_id=payload.get("session_id"),
            transcript_path=payload.get("transcript_path"),
        )
    except Exception as exc:  # noqa: BLE001 - fail open, never trap the session
        sys.stderr.write(f"PAEM checkpoint guard skipped due to an error: {exc}\n")
        return EXIT_ALLOW

    if should_block:
        sys.stderr.write(message + "\n")
        return EXIT_BLOCK
    return EXIT_ALLOW


if __name__ == "__main__":
    sys.exit(main())
