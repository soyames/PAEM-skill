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

Verified directories (each provider's own current public docs):
  claude-code   project: <target>/.claude/skills/paem/    global: ~/.claude/skills/paem/
  codex         project: <target>/.agents/skills/paem/    global: ~/.codex/skills/paem/
  gemini-cli    project: <target>/.gemini/skills/paem/    global: ~/.gemini/skills/paem/
  antigravity   project: <target>/.agents/skills/paem/    global: ~/.gemini/config/skills/paem/
  cursor        project: <target>/.cursor/skills/paem/    global: not supported by Cursor (project-only)

Note: codex and antigravity share the same project-level path (.agents/skills/)
- that's the shared open-standard convention, not a coincidence - so one
project-scope install with either --provider codex or --provider antigravity
covers both tools for that project.

This only copies files. It never touches your global git/tool config and
never overwrites files outside the destination skill folder.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RUNTIME_TOP_LEVEL_FILES = ["SKILL.md", "paem.md"]
RUNTIME_DIRS = ["prompts", "templates"]
RUNTIME_SCRIPTS = [
    "paem_guard_core.py",
    "paem_checkpoint_guard.py",
    "paem_checkpoint_guard_codex.py",
    "paem_checkpoint_guard_gemini.py",
    "paem_checkpoint_guard_cursor.py",
]

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
    actions = []

    def do_copy(src: Path, dst: Path, is_dir: bool) -> None:
        actions.append(f"{'[dry-run] ' if dry_run else ''}{src.relative_to(REPO_ROOT)} -> {dst}")
        if dry_run:
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        if is_dir:
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    for name in RUNTIME_TOP_LEVEL_FILES:
        do_copy(REPO_ROOT / name, dest / name, is_dir=False)
    for name in RUNTIME_DIRS:
        do_copy(REPO_ROOT / name, dest / name, is_dir=True)
    scripts_src_dir = REPO_ROOT / "scripts"
    for name in RUNTIME_SCRIPTS:
        src = scripts_src_dir / name
        if src.is_file():
            do_copy(src, dest / "scripts" / name, is_dir=False)
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
        dest = Path.home() / rel
    else:
        dest = Path(args.target).resolve() / rel

    print(f"Installing PAEM for {args.provider} ({args.scope} scope) into:\n  {dest}\n")
    actions = copy_runtime_files(dest, args.dry_run)
    for line in actions:
        print(f"  {line}")

    if args.dry_run:
        print("\nDry run - nothing was written. Re-run without --dry-run to install.")
    else:
        print(f"\nDone. {args.provider} should discover the skill on its next session.")
        if args.provider in ("codex", "antigravity") and args.scope == "project":
            other = "antigravity" if args.provider == "codex" else "codex"
            print(f"Note: this same .agents/skills/paem/ path is also where {other} looks - "
                  f"this install covers both.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
