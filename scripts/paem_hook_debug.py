#!/usr/bin/env python3
"""Capture a hook's real stdin payload, for verifying adapter field names.

The Codex CLI, Gemini CLI, and Cursor guard adapters guess at stdin field
names (`cwd`, `session_id`, etc.) from public docs, not a live install -
this script exists to replace the guess with a fact. Wire it as the Stop
(or Stop-equivalent) hook instead of the real guard, trigger a stop, then
read the captured file to see the actual payload shape. It NEVER blocks -
safe to leave wired in while you're only trying to observe.

Usage (as a hook command):
    python3 scripts/paem_hook_debug.py <host-label>

Example wiring - Codex CLI .codex/hooks.json:
    { "Stop": [{ "command": "python3 scripts/paem_hook_debug.py codex" }] }

Where output goes:
    <cwd>/.paem/.guard/hook-debug/<host-label>-<timestamp>.json if
    <cwd>/.paem/ exists, otherwise the system temp directory (printed to
    stderr so you can find it either way).

What it captures per file: the host label you passed, an ISO timestamp,
process cwd, the raw stdin text exactly as received, and (if it parsed as
JSON) the top-level key names - the fastest way to compare against
_CWD_KEYS / _SESSION_KEYS in the relevant paem_checkpoint_guard_*.py and
correct them via the "Hook adapter field verification" issue form or a
direct PR.

Always exits 0. Never writes anything that could be mistaken for a block
signal (no exit 2, no `{"decision": ...}` JSON on stdout).
"""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def _debug_dir() -> Path:
    cwd = Path.cwd()
    paem = cwd / ".paem"
    if paem.is_dir():
        target = paem / ".guard" / "hook-debug"
    else:
        target = Path(tempfile.gettempdir()) / "paem-hook-debug"
    target.mkdir(parents=True, exist_ok=True)
    return target


def main() -> int:
    host_label = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    raw = sys.stdin.read()

    parsed_keys: list[str] | None = None
    try:
        parsed = json.loads(raw) if raw.strip() else {}
        if isinstance(parsed, dict):
            parsed_keys = sorted(parsed.keys())
    except (json.JSONDecodeError, ValueError):
        pass

    record = {
        "host_label": host_label,
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cwd": str(Path.cwd()),
        "top_level_keys": parsed_keys,
        "raw_stdin": raw,
    }

    out_dir = _debug_dir()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"{host_label}-{stamp}.json"
    out_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    sys.stderr.write(f"PAEM hook debug: captured {host_label} payload -> {out_path}\n")
    if parsed_keys is not None:
        sys.stderr.write(f"PAEM hook debug: top-level keys: {parsed_keys}\n")
    else:
        sys.stderr.write("PAEM hook debug: stdin was not a JSON object (see raw_stdin in the file)\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
