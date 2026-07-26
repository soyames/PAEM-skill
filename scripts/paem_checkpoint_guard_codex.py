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


def _warn_if_unmatched(payload: dict, cwd_matched: bool, session_matched: bool) -> None:
    """Make best-effort field guessing observable instead of silently guessing.

    This only writes to stderr (hook logs), never to the blocking message the
    agent sees, so it does not spam the conversation. It fires whenever a
    non-empty stdin payload didn't contain any of the field names this
    adapter was written against - a strong signal the guess is wrong for your
    Codex CLI version.
    """
    if not payload:
        return  # no JSON on stdin at all; nothing to diagnose
    missing = []
    if not cwd_matched:
        missing.append(f"working-directory key (tried: {', '.join(_CWD_KEYS)})")
    if not session_matched:
        missing.append(f"session-id key (tried: {', '.join(_SESSION_KEYS)})")
    if missing:
        sys.stderr.write(
            "PAEM codex guard: stdin payload didn't match the expected "
            + " or ".join(missing)
            + ". Falling back to a safe default (cwd via os.getcwd(), no "
            "session id). This adapter's field names are best-effort - please "
            "open the 'Hook adapter field verification' issue with your "
            "actual payload keys so this can be corrected.\n"
        )


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

    cwd_value = _first_present(payload, _CWD_KEYS)
    session_id = _first_present(payload, _SESSION_KEYS)
    _warn_if_unmatched(payload, cwd_value is not None, session_id is not None)
    cwd = cwd_value or os.getcwd()
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
