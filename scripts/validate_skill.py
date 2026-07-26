#!/usr/bin/env python3
"""Smoke-test the PAEM skill package.

Validates required files, metadata, templates, and a dry-run .paem/ init.
Exit code 0 = pass, 1 = fail.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []


def error(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def require_file(rel: str) -> Path | None:
    path = ROOT / rel
    if not path.is_file():
        error(f"Missing required file: {rel}")
        return None
    return path


def require_dir(rel: str) -> Path | None:
    path = ROOT / rel
    if not path.is_dir():
        error(f"Missing required directory: {rel}")
        return None
    return path


def check_layout() -> None:
    required_files = [
        "README.md",
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        ".gitignore",
        "skill.yaml",
        "SKILL.md",
        "paem.md",
        "docs/architecture.md",
        "docs/checkpointing.md",
        "docs/recovery.md",
        "docs/examples.md",
        "docs/roadmap.md",
        "docs/faq.md",
        "examples/claude.md",
        "examples/codex.md",
        "examples/cursor.md",
        "examples/gemini.md",
        "examples/antigravity.md",
        "examples/openhands.md",
        "prompts/resume.md",
        "prompts/checkpoint.md",
        "prompts/summarize.md",
        "prompts/recover.md",
        "prompts/verify.md",
        "prompts/execute.md",
        "templates/checkpoint.json",
        "templates/project_summary.md",
        "templates/execution_report.md",
        "templates/resume_prompt.md",
        "templates/task_list.md",
        "templates/completed_tasks.md",
        "templates/agents_md_snippet.md",
        "templates/provider_budgets.md",
        "scripts/paem_guard_core.py",
        "scripts/paem_checkpoint_guard.py",
        "scripts/paem_checkpoint_guard_codex.py",
        "scripts/paem_checkpoint_guard_gemini.py",
        "scripts/paem_checkpoint_guard_cursor.py",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/CODEOWNERS",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/ISSUE_TEMPLATE/question.yml",
    ]
    for rel in required_files:
        require_file(rel)

    # Must not ship generic CoC we intentionally removed
    if (ROOT / "CODE_OF_CONDUCT.md").exists():
        error("CODE_OF_CONDUCT.md should not exist (removed by project choice)")

    for name in ("docs", "examples", "prompts", "templates", "scripts", ".github"):
        require_dir(name)


def check_no_em_dashes_in_core() -> None:
    """Project style: plain hyphen, not em dash."""
    core = [
        "README.md",
        "SKILL.md",
        "paem.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
    ]
    em = "\u2014"
    for rel in core:
        path = ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if em in text:
            error(f"Em dash found in {rel} (use plain hyphen '-')")


def check_skill_md() -> None:
    path = require_file("SKILL.md")
    if not path:
        return
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        error("SKILL.md must start with YAML frontmatter (---)")
        return
    parts = text.split("---", 2)
    if len(parts) < 3:
        error("SKILL.md frontmatter is malformed")
        return
    fm = parts[1]
    if not re.search(r"(?m)^name:\s*paem\s*$", fm):
        error("SKILL.md frontmatter must include name: paem")
    if not re.search(r"(?m)^description:\s*", fm):
        error("SKILL.md frontmatter must include description:")
    body = parts[2]
    for needle in (".paem/", "checkpoint", "resume", "Verify"):
        if needle.lower() not in body.lower():
            error(f"SKILL.md body missing expected concept: {needle}")


def check_skill_yaml() -> None:
    path = require_file("skill.yaml")
    if not path:
        return
    text = path.read_text(encoding="utf-8")
    required_keys = [
        "name:",
        "id:",
        "version:",
        "author:",
        "license:",
        "description:",
        "entry:",
        "homepage:",
    ]
    for key in required_keys:
        if key not in text:
            error(f"skill.yaml missing key marker: {key}")
    if "soyames/PAEM-skill" not in text:
        error("skill.yaml homepage should point to github.com/soyames/PAEM-skill")
    if "paem.md" not in text:
        error("skill.yaml entry should reference paem.md")
    # Lightweight YAML: reject tabs
    if "\t" in text:
        warn("skill.yaml contains tabs; prefer spaces")


def check_checkpoint_template() -> None:
    path = require_file("templates/checkpoint.json")
    if not path:
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(f"templates/checkpoint.json is not valid JSON: {exc}")
        return
    required = [
        "schema_version",
        "checkpoint_id",
        "timestamp",
        "current_task",
        "completed_since_last",
        "modified_files",
        "architectural_decisions",
        "remaining_work",
        "known_issues",
        "verification",
        "recovery",
        "next_action",
    ]
    for key in required:
        if key not in data:
            error(f"checkpoint template missing field: {key}")
    if data.get("schema_version") != "1.0.0":
        warn(f"checkpoint schema_version is {data.get('schema_version')!r}, expected '1.0.0'")


def check_readme_links() -> None:
    path = require_file("README.md")
    if not path:
        return
    text = path.read_text(encoding="utf-8")
    # relative markdown links
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        href = match.group(2)
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        # strip anchors
        file_part = href.split("#", 1)[0]
        if not file_part:
            continue
        target = (ROOT / file_part).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            error(f"README link escapes repo: {href}")
            continue
        if not target.exists():
            error(f"README broken link: {href}")
    if "CODE_OF_CONDUCT" in text:
        error("README still references CODE_OF_CONDUCT")
    if "github.com/soyames/PAEM-skill" not in text:
        error("README should reference https://github.com/soyames/PAEM-skill")


def check_gitignore() -> None:
    path = require_file(".gitignore")
    if not path:
        return
    text = path.read_text(encoding="utf-8")
    if ".paem/" not in text and ".paem" not in text:
        error(".gitignore should ignore runtime .paem/ in this skill repo")
    if ".env" not in text:
        warn(".gitignore does not mention .env")


def check_checkpoint_guard_compiles() -> None:
    """The Stop-hook guard scripts must at least be syntactically valid."""
    import py_compile

    guard_scripts = [
        "scripts/paem_guard_core.py",
        "scripts/paem_checkpoint_guard.py",
        "scripts/paem_checkpoint_guard_codex.py",
        "scripts/paem_checkpoint_guard_gemini.py",
        "scripts/paem_checkpoint_guard_cursor.py",
    ]
    for rel in guard_scripts:
        path = ROOT / rel
        if not path.is_file():
            continue  # already reported by check_layout()
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            error(f"{rel} does not compile: {exc}")


def dry_run_paem_init() -> None:
    """Simulate initializing .paem/ from templates (what an agent should do)."""
    templates = ROOT / "templates"
    if not templates.is_dir():
        error("templates/ missing; skip dry-run")
        return

    tmp = Path(tempfile.mkdtemp(prefix="paem-dryrun-"))
    try:
        paem = tmp / ".paem"
        (paem / "checkpoints").mkdir(parents=True)
        (paem / "reports").mkdir(parents=True)

        mapping = {
            "project_summary.md": "project_summary.md",
            "task_list.md": "task_list.md",
            "completed_tasks.md": "completed_tasks.md",
            "resume_prompt.md": "resume_prompt.md",
            "checkpoint.json": "latest_checkpoint.json",
        }
        for src_name, dest_name in mapping.items():
            src = templates / src_name
            if not src.is_file():
                error(f"dry-run missing template: {src_name}")
                continue
            dest = paem / dest_name
            shutil.copy2(src, dest)

        # Also store numbered checkpoint
        shutil.copy2(templates / "checkpoint.json", paem / "checkpoints" / "checkpoint-000.json")

        # Minimal architecture / issues / conventions
        (paem / "architecture.md").write_text(
            "# Architecture\n\nDry-run baseline.\n", encoding="utf-8"
        )
        (paem / "known_issues.md").write_text("# Known issues\n\nNone.\n", encoding="utf-8")
        (paem / "conventions.md").write_text("# Conventions\n\nFollow project norms.\n", encoding="utf-8")

        # Validate latest checkpoint still JSON
        latest = paem / "latest_checkpoint.json"
        json.loads(latest.read_text(encoding="utf-8"))

        required_runtime = [
            "project_summary.md",
            "architecture.md",
            "task_list.md",
            "completed_tasks.md",
            "known_issues.md",
            "conventions.md",
            "latest_checkpoint.json",
            "resume_prompt.md",
            "checkpoints/checkpoint-000.json",
        ]
        for rel in required_runtime:
            if not (paem / rel).exists():
                error(f"dry-run .paem/ missing: {rel}")

        # Resume prompt should mention PAEM
        resume = (paem / "resume_prompt.md").read_text(encoding="utf-8")
        if "PAEM" not in resume and "paem" not in resume.lower():
            error("resume_prompt template should mention PAEM")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_license() -> None:
    path = require_file("LICENSE")
    if not path:
        return
    text = path.read_text(encoding="utf-8")
    if "MIT License" not in text:
        error("LICENSE does not look like MIT")
    if "Yao Amevi Amessinou Sossou" not in text:
        warn("LICENSE copyright name may be unexpected")


def main() -> int:
    print(f"PAEM skill validation")
    print(f"Root: {ROOT}")
    print("-" * 60)

    check_layout()
    check_license()
    check_skill_md()
    check_skill_yaml()
    check_checkpoint_template()
    check_checkpoint_guard_compiles()
    check_readme_links()
    check_gitignore()
    check_no_em_dashes_in_core()
    dry_run_paem_init()

    print("-" * 60)
    if WARNINGS:
        print(f"Warnings ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"  ! {w}")
    if ERRORS:
        print(f"FAILED with {len(ERRORS)} error(s):")
        for e in ERRORS:
            print(f"  x {e}")
        return 1

    print("OK - all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
