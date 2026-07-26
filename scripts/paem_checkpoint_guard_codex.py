#!/usr/bin/env python3
"""PAEM checkpoint guard - OpenAI Codex CLI `Stop` hook adapter.

Confidence note: Codex CLI hooks are experimental (opt-in via
`codex_hooks = true` in config.toml, not available on Windows) as of this
writing. Its exit-code contract for `Stop` is documented and matches Claude
Code's exactly (exit 0 = continue, exit 2 = block with the reason on
stderr), which is what this adapter relies on. The exact stdin field names
for the working directory and session identifier are NOT independently
verified against a live Codex install the way the Claude Code adapter is -
this tries several plausible key names and falls back to `os.getcwd()`
rather than guessing wrong silently. If your Codex version uses different
field names, please open an issue (or a PR) so this can be corrected instead
of quietly doing nothing.

Wire this as a `Stop` hook in your project's `.codex/hooks.json` (or the
`[hooks]` table in `config.toml`) - see examples/codex.md.

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

    # Mirror Claude Code's stop_hook_active loop guard in case Codex reports
    # an equivalent flag under either name; harmless no-op if it doesn't.
    if payload.get("stop_hook_active") or payload.get("hook_already_active"):
        return EXIT_ALLOW

    cwd = _first_present(payload, _CWD_KEYS) or os.getcwd()
    session_id = _first_present(payload, _SESSION_KEYS)
    transcript_path = payload.get("transcript_path")

    try:
        should_block, message = evaluate(
            Path(cwd),
            provider_key="codex",
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
