#!/usr/bin/env python3
"""PAEM checkpoint guard - Gemini CLI hook adapter.

Confidence note: Gemini CLI's hook exit-code contract is documented (exit 0
= continue, exit 2 = block, stderr used as the reason - or JSON on stdout
with `{"decision": "deny", "reason": ...}` / `{"continue": false}`), and
this adapter uses the plain exit-code form since it matches Claude Code's
and Codex's contract exactly. The stdin field names for working directory
and session identifier are NOT independently verified against a live Gemini
CLI install - this tries several plausible key names and falls back to
`os.getcwd()` rather than guessing wrong silently. If your Gemini CLI
version differs, please open an issue so this can be corrected.

IMPORTANT: Gemini CLI hooks require stdout to contain nothing but valid JSON
when you emit JSON at all - even a stray print() breaks parsing. This
adapter avoids that entirely by only ever writing to stderr and using bare
exit codes, which is documented as a valid alternative to JSON output.

Wire this as a Stop-equivalent hook in your project's `.gemini/settings.json`
- see examples/gemini.md.

Opt-out: set PAEM_SKIP_GUARD=1 in the environment.
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

_CWD_KEYS = ("cwd", "workspace_root", "working_directory", "project_root")
_SESSION_KEYS = ("session_id", "thread_id", "conversation_id")


def _first_present(payload: dict, keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = payload.get(key)
        if value:
            return value
    return None


def main() -> int:
    if os.environ.get("PAEM_SKIP_GUARD") == "1":
        return EXIT_ALLOW

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    if payload.get("stop_hook_active") or payload.get("hook_already_active"):
        return EXIT_ALLOW

    cwd = _first_present(payload, _CWD_KEYS) or os.getcwd()
    session_id = _first_present(payload, _SESSION_KEYS)
    transcript_path = payload.get("transcript_path")

    try:
        should_block, message = evaluate(
            Path(cwd),
            provider_key="gemini-cli",
            session_id=session_id,
            transcript_path=transcript_path,
        )
    except Exception as exc:  # noqa: BLE001 - fail open
        sys.stderr.write(f"PAEM checkpoint guard skipped due to an error: {exc}\n")
        return EXIT_ALLOW

    if should_block:
        sys.stderr.write(message + "\n")
        return EXIT_BLOCK
    return EXIT_ALLOW


if __name__ == "__main__":
    sys.exit(main())
