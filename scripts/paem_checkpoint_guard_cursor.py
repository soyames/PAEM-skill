#!/usr/bin/env python3
"""PAEM checkpoint guard - Cursor `stop` hook adapter (best-effort, NOT a hard block).

Important honesty note: unlike Claude Code, Codex CLI, and Gemini CLI,
Cursor's own docs and community reports describe `stop` hooks as running
*after* the agent has already reached a terminal UI state - the turn can
finish while the hook is still executing in the background. Exiting 2 here
may not reliably prevent the session from ending the way it does on the
other three providers. Treat this adapter as a nudge, not an enforcement
mechanism.

Given that, this adapter uses Cursor's documented `followup_message`
mechanism instead of trying to block: when PAEM's shared detection logic
says there's uncheckpointed work, it asks Cursor to enqueue one more agent
turn with an instruction to checkpoint, rather than claiming to stop
anything.

Confidence note: the input schema (`conversation_id`, `workspace_roots`,
etc.) matches Cursor's documented `stop` event fields, but this has not been
run against a live Cursor install. Please verify and report back if your
version differs.

Wire this in `.cursor/hooks.json` under the `stop` event - see
examples/cursor.md.

Opt-out: set PAEM_SKIP_GUARD=1 in the environment.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paem_guard_core import evaluate  # noqa: E402


def _warn_if_unmatched(payload: dict, cwd_matched: bool, session_matched: bool) -> None:
    """Make best-effort field guessing observable instead of silently guessing.

    Writes to stderr (hook logs) only, never to the followup_message the
    agent sees. Fires whenever a non-empty stdin payload lacked the fields
    this adapter was written against.
    """
    if not payload:
        return
    missing = []
    if not cwd_matched:
        missing.append("non-empty 'workspace_roots' array")
    if not session_matched:
        missing.append("'conversation_id' key")
    if missing:
        sys.stderr.write(
            "PAEM cursor guard: stdin payload was missing the expected "
            + " and ".join(missing)
            + ". Falling back to a safe default (cwd via os.getcwd(), no "
            "session id). This adapter's field names are best-effort - please "
            "open the 'Hook adapter field verification' issue with your "
            "actual payload keys so this can be corrected.\n"
        )


def main() -> int:
    if os.environ.get("PAEM_SKIP_GUARD") == "1":
        print("{}")
        return 0

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    workspace_roots = payload.get("workspace_roots") or []
    session_id = payload.get("conversation_id")
    _warn_if_unmatched(payload, bool(workspace_roots), session_id is not None)
    cwd = workspace_roots[0] if workspace_roots else os.getcwd()

    try:
        should_block, message = evaluate(
            Path(cwd),
            provider_key="cursor",
            session_id=session_id,
            transcript_path=None,  # not exposed in Cursor's stop payload
        )
    except Exception as exc:  # noqa: BLE001 - fail open
        sys.stderr.write(f"PAEM checkpoint guard skipped due to an error: {exc}\n")
        print("{}")
        return 0

    if should_block:
        print(json.dumps({"followup_message": message}))
    else:
        print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
