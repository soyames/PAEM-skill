#!/usr/bin/env python3
"""Install the PAEM skill package into a specific AI coding tool's skill directory.

By 2026 every major agentic coding tool converged on the same open packaging
format for this - a folder with a SKILL.md file plus optional scripts/
references/assets (see https://agentskills.io). They differ only in which
directory they scan for it. This script copies this repo's runtime files
(SKILL.md, paem.md, prompts/, templates/, the checkpoint-guard scripts) into
the correct directory for whichever tool you name, at project or global
scope - nothing more, no tool-specific magic, because none is needed.

Usage:
    python scripts/install.py --list
    python scripts/install.py --provider claude-code --scope project --target /path/to/your/app
    python scripts/install.py --provider codex --scope global
    python scripts/install.py --provider antigravity --scope project --target . --dry-run

Directories below match each provider's own current public docs. That is
NOT the same as confirmed working - see docs/schema-migration.md's sibling,
the SKILL DISCOVERY table in paem.md, for what has and hasn't been verified
against a real install. Short version: Claude Code is confirmed. Antigravity
is documented but failed in a controlled real-install test (files land in
the right place; the skill just doesn't show up) - see examples/antigravity.md
for a manual fallback. Codex, Gemini CLI, and Cursor are untested either way.

  claude-code   project: <target>/.claude/skills/paem/    global: ~/.claude/skills/paem/
  codex         project: <target>/.agents/skills/paem/    global: ~/.codex/skills/paem/
  gemini-cli    project: <target>/.gemini/skills/paem/    global: ~/.gemini/skills/paem/
  antigravity   project: <target>/.agents/skills/paem/    global: ~/.gemini/config/skills/paem/
  cursor        project: <target>/.cursor/skills/paem/    global: not supported by Cursor (project-only)

Note: codex and antigravity share the same project-level path (.agents/skills/)
- that's the shared open-standard convention, not a coincidence - so one
project-scope install with either --provider codex or --provider antigravity
covers both tools for that project (assuming the target host actually scans
that path - see above).

This only copies files. It never touches your global git/tool config and
never overwrites files outside the destination skill folder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

from paem_fs import atomic_write, safe_path

REPO_ROOT = Path(__file__).resolve().parent.parent

RUNTIME_TOP_LEVEL_FILES = ["SKILL.md", "paem.md", "skill.yaml", "LICENSE"]
RUNTIME_DIRS = ["prompts", "templates", "schemas", "docs", "examples"]
RUNTIME_SCRIPTS = [
    "paem_guard_core.py",
    "paem_checkpoint_guard.py",
    "paem_checkpoint_guard_codex.py",
    "paem_checkpoint_guard_gemini.py",
    "paem_checkpoint_guard_cursor.py",
    "paem_init.py",
    "validate_checkpoint.py",
    "paem_schema_lib.py",
    "paem_fs.py",
    "paem_repository.py",
    "paem_checkpoint.py",
    "paem_hook_debug.py",
]
MANIFEST = ".paem-install.json"

# rel path is relative to: project target dir (for "project") or home dir (for "global")
PATHS: dict[str, dict[str, str | None]] = {
    "claude-code": {"project": ".claude/skills/paem", "global": ".claude/skills/paem"},
    "codex": {"project": ".agents/skills/paem", "global": ".codex/skills/paem"},
    "gemini-cli": {"project": ".gemini/skills/paem", "global": ".gemini/skills/paem"},
    "antigravity": {"project": ".agents/skills/paem", "global": ".gemini/config/skills/paem"},
    "cursor": {"project": ".cursor/skills/paem", "global": None},
}


def print_table() -> None:
    print(__doc__.split("Usage:")[0].strip())
    print()
    print(f"{'provider':<14}{'project path':<32}{'global path'}")
    for name, scopes in PATHS.items():
        proj = scopes["project"]
        glob = scopes["global"] or "(not supported)"
        print(f"{name:<14}{proj:<32}{glob}")


def copy_runtime_files(dest: Path, dry_run: bool) -> list[str]:
    dest = Path(os.path.abspath(dest))
    safe_path(dest, ".")
    relative_files = list(RUNTIME_TOP_LEVEL_FILES) + [f"scripts/{name}" for name in RUNTIME_SCRIPTS]
    for directory in RUNTIME_DIRS:
        for source in sorted((REPO_ROOT / directory).rglob("*")):
            safe_path(REPO_ROOT, source.relative_to(REPO_ROOT))
            if source.is_file():
                relative_files.append(source.relative_to(REPO_ROOT).as_posix())
    payload = {}
    for relative in relative_files:
        payload[relative] = safe_path(REPO_ROOT, relative).read_bytes()
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()}
    marker = safe_path(dest, MANIFEST)
    owned = {}
    if marker.exists():
        metadata = json.loads(marker.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict) or metadata.get("package") != "paem" or not isinstance(metadata.get("files"), dict):
            raise ValueError("Invalid PAEM installation manifest; leave the directory intact and inspect it")
        owned = metadata["files"]
    # A prior unmarked manual install may be adopted only when colliding files
    # are byte-identical. Preflight the whole payload before the first write.
    for relative, data in payload.items():
        target = safe_path(dest, relative)
        if target.exists():
            if not target.is_file():
                raise ValueError(f"Destination is not a file: {target}")
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            if digest not in (hashes[relative], owned.get(relative)):
                raise ValueError(f"Refusing to overwrite foreign or edited file: {target}. Back it up outside this folder before retrying.")
    actions = []
    for relative, data in payload.items():
        actions.append(f"{'[dry-run] ' if dry_run else ''}{relative} -> {dest / relative}")
        if not dry_run:
            atomic_write(dest, relative, data)
    if not dry_run:
        atomic_write(dest, MANIFEST, (json.dumps({"package": "paem", "files": hashes}, indent=2) + "\n").encode())
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="Print the provider/path table and exit.")
    parser.add_argument("--provider", choices=sorted(PATHS.keys()), help="Which tool to install for.")
    parser.add_argument("--scope", choices=["project", "global"], default="project")
    parser.add_argument(
        "--target",
        default=".",
        help="Project root to install into (scope=project only). Defaults to the current directory - "
        "this should be YOUR application project, not this skill repo, unless you're testing.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be copied without writing anything.")
    args = parser.parse_args()

    if args.list or not args.provider:
        print_table()
        return 0

    scopes = PATHS[args.provider]
    rel = scopes[args.scope]
    if rel is None:
        print(
            f"error: {args.provider} does not support scope={args.scope} "
            f"(see --list for what it does support).",
            file=sys.stderr,
        )
        return 1

    if args.scope == "global":
        if args.provider == "codex" and os.environ.get("CODEX_HOME"):
            dest = Path(os.environ["CODEX_HOME"]).expanduser() / "skills/paem"
        else:
            dest = Path.home() / rel
    else:
        dest = Path(args.target).resolve() / rel

    print(f"Installing PAEM for {args.provider} ({args.scope} scope) into:\n  {dest}\n")
    try:
        actions = copy_runtime_files(dest, args.dry_run)
    except (OSError, ValueError) as exc:
        print(f"Installation refused: {exc}", file=sys.stderr)
        return 1
    for line in actions:
        print(f"  {line}")

    if args.dry_run:
        print("\nDry run - nothing was written. Re-run without --dry-run to install.")
    else:
        print(f"\nFiles installed. Verify PAEM discovery in a new {args.provider} session; installation alone does not prove host support.")
        if args.provider in ("codex", "antigravity") and args.scope == "project":
            other = "antigravity" if args.provider == "codex" else "codex"
            print(f"Note: this same .agents/skills/paem/ path is also where {other} looks - "
                  f"this install covers both.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
