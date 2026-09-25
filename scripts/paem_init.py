#!/usr/bin/env python3
"""One-command `.paem/` initializer.

Copies templates/ into a project's .paem/ directory, filling in what it
safely can (project name, timestamp, a checkpoint-000 baseline) and leaving
the rest as the blank prompts already in templates/ for the agent or you to
fill in during the first real session. This does not read or write any
network service - it only touches files under --target. Still no cloud.

Usage:
    python scripts/paem_init.py --target /path/to/your/app
    python scripts/paem_init.py --target /path/to/your/app --project-name my-app
    python scripts/paem_init.py --target /path/to/your/app --force   # overwrite existing .paem/

Safe by default: refuses to touch an existing .paem/ unless --force is
passed, and never touches anything outside <target>/.paem/.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from paem_checkpoint import publish
from paem_fs import atomic_write, safe_path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = REPO_ROOT / "templates"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_baseline_checkpoint(project_name: str) -> dict:
    now = _now_iso()
    return {
        "schema_version": "1.0.0",
        "checkpoint_id": "checkpoint-000",
        "timestamp": now,
        "project_name": project_name,
        "branch": None,
        "commit_hash": None,
        "milestone": "Project initialized",
        "current_task": {
            "id": "T-000",
            "title": "Initialize PAEM state",
            "status": "complete",
        },
        "completed_since_last": ["Initialized .paem/ via scripts/paem_init.py"],
        "modified_files": [],
        "architectural_decisions": [],
        "remaining_work": ["Define first real task in .paem/task_list.md"],
        "known_issues": [],
        "verification": {
            "status": "unverified",
            "checks": [],
            "notes": "Baseline checkpoint - no project code has been touched yet.",
        },
        "recovery": {
            "status": "safe_to_resume",
            "manual_intervention_required": False,
            "notes": "Nothing in progress yet.",
        },
        "next_action": "Fill in .paem/project_summary.md and define the first task in .paem/task_list.md.",
        "session_notes": "Created by scripts/paem_init.py, not a real work session.",
    }


def init_paem(target: Path, project_name: str, force: bool) -> list[str]:
    """Create <target>/.paem/. Returns a list of relative paths written."""
    if not TEMPLATES.is_dir():
        raise SystemExit(f"templates/ not found next to this script (looked in {TEMPLATES})")

    paem = safe_path(target, ".paem")
    if paem.exists() and not force:
        raise SystemExit(f"{paem} already exists. --force fills missing skeleton files only; it never resets existing state.")

    written: list[str] = []
    for name in ["checkpoints", "reports", "project_summary.md", "task_list.md", "completed_tasks.md",
                 "resume_prompt.md", "provider_budgets.md", "architecture.md", "known_issues.md",
                 "conventions.md", "latest_checkpoint.json", "current.json"]:
        safe_path(paem, name)
    safe_path(paem, "checkpoints").mkdir(parents=True, exist_ok=True)
    safe_path(paem, "reports").mkdir(parents=True, exist_ok=True)

    # Blank skeleton files, copied as-is - the agent fills these in during
    # the first real session, same as templates/ always intended.
    skeleton = {
        "project_summary.md": "project_summary.md",
        "task_list.md": "task_list.md",
        "completed_tasks.md": "completed_tasks.md",
        "provider_budgets.md": "provider_budgets.md",
    }
    for src_name, dest_name in skeleton.items():
        src = TEMPLATES / src_name
        if not src.is_file():
            continue
        dest = safe_path(paem, dest_name)
        if not dest.exists():
            atomic_write(paem, dest_name, src.read_bytes())
            written.append(str(dest.relative_to(target)))

    # Minimal starting docs (not in templates/ as standalone files today).
    for name, content in {
        "architecture.md": f"# Architecture\n\n{project_name}: no architectural decisions recorded yet.\n",
        "known_issues.md": "# Known Issues\n\nNone yet.\n",
        "conventions.md": "# Conventions\n\n- Follow this project's existing style and tooling.\n",
    }.items():
        if not (paem / name).exists():
            atomic_write(paem, name, content.encode())
            written.append(str((paem / name).relative_to(target)))

    # Baseline checkpoint - the one thing worth actually filling in, so a
    # brand new .paem/ is immediately internally consistent instead of full
    # of empty placeholders that would fail schema validation.
    if not (paem / "latest_checkpoint.json").exists() and not (paem / "current.json").exists() and not any((paem / "checkpoints").iterdir()):
        publish(target, build_baseline_checkpoint(project_name))
        written.extend([".paem/checkpoints/checkpoint-000.json", ".paem/latest_checkpoint.json",
                        ".paem/resume_prompt.md", ".paem/current.json"])

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", required=True, type=Path, help="Project root to initialize .paem/ in")
    parser.add_argument("--project-name", default=None, help="Defaults to the target directory's name")
    parser.add_argument("--force", action="store_true", help="Fill missing skeleton files; preserve existing notes and checkpoints")
    args = parser.parse_args()

    target = args.target.expanduser().resolve()
    if not target.is_dir():
        print(f"Target directory does not exist: {target}", file=sys.stderr)
        return 1

    project_name = args.project_name or target.name

    try:
        written = init_paem(target, project_name, args.force)
    except (OSError, ValueError) as exc:
        print(f"Initialization refused: {exc}", file=sys.stderr)
        return 1

    print(f"Initialized .paem/ in {target}")
    for rel in written:
        print(f"  {rel}")
    print()
    print("Next: open a session and say")
    print('  "Use PAEM for this project. Goal: <describe the goal>."')
    print("or fill in .paem/project_summary.md and .paem/task_list.md yourself first.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
