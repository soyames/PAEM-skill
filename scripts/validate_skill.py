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
# The skill every installer copies. Repository-only files (tests, fixtures, CI,
# this validator, the installer) live outside it and must never ship.
SKILL_DIR = "skills/paem"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / SKILL_DIR / "scripts"))
import paem_schema_lib  # noqa: E402

ERRORS: list[str] = []
WARNINGS: list[str] = []


def skill(rel: str) -> str:
    return f"{SKILL_DIR}/{rel}"


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


RUNTIME_SCRIPTS = [
    "paem_guard_core.py",
    "paem_checkpoint_guard.py",
    "paem_checkpoint_guard_codex.py",
    "paem_checkpoint_guard_gemini.py",
    "paem_checkpoint_guard_cursor.py",
    "paem_schema_lib.py",
    "validate_checkpoint.py",
    "paem_init.py",
    "paem_hook_debug.py",
    "paem_fs.py",
    "paem_repository.py",
    "paem_checkpoint.py",
]


def check_layout() -> None:
    skill_files = [
        "LICENSE",
        "skill.yaml",
        "SKILL.md",
        "paem.md",
        "docs/architecture.md",
        "docs/checkpointing.md",
        "docs/recovery.md",
        "docs/examples.md",
        "docs/faq.md",
        "docs/schema-migration.md",
        "examples/claude.md",
        "examples/codex.md",
        "examples/cursor.md",
        "examples/gemini.md",
        "examples/antigravity.md",
        "examples/openhands.md",
        "examples/aider.md",
        "examples/continue.md",
        "examples/more-agents.md",
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
        "templates/project_agent_snippet.md",
        "templates/provider_budgets.md",
        "schemas/checkpoint.schema.json",
        "schemas/execution_report.schema.json",
        *(f"scripts/{name}" for name in RUNTIME_SCRIPTS),
    ]
    for rel in skill_files:
        require_file(skill(rel))

    required_files = [
        "README.md",
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "ROADMAP.md",
        ".gitignore",
        "scripts/install.py",
        "scripts/validate_skill.py",
        "fixtures/README.md",
        "fixtures/sample-project/.paem/project_summary.md",
        "fixtures/sample-project/.paem/architecture.md",
        "fixtures/sample-project/.paem/task_list.md",
        "fixtures/sample-project/.paem/completed_tasks.md",
        "fixtures/sample-project/.paem/known_issues.md",
        "fixtures/sample-project/.paem/conventions.md",
        "fixtures/sample-project/.paem/latest_checkpoint.json",
        "fixtures/sample-project/.paem/checkpoints/checkpoint-000.json",
        "fixtures/sample-project/.paem/checkpoints/checkpoint-001.json",
        "fixtures/sample-project/.paem/resume_prompt.md",
        "fixtures/sample-project/.paem/reports/execution_report-001.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/CODEOWNERS",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/ISSUE_TEMPLATE/question.yml",
        ".github/ISSUE_TEMPLATE/hook_field_verification.yml",
    ]
    for rel in required_files:
        require_file(rel)

    # Must not ship generic CoC we intentionally removed
    if (ROOT / "CODE_OF_CONDUCT.md").exists():
        error("CODE_OF_CONDUCT.md should not exist (removed by project choice)")

    for name in ("scripts", ".github", "fixtures", "tests"):
        require_dir(name)
    for name in ("docs", "examples", "prompts", "templates", "schemas", "scripts"):
        require_dir(skill(name))


def check_skill_folder_is_only_the_skill() -> None:
    """Installers copy skills/paem/ whole, so repository-only files must stay out of it."""
    root = ROOT / SKILL_DIR
    if not root.is_dir():
        return  # already reported by check_layout()
    allowed_top = {"SKILL.md", "paem.md", "skill.yaml", "LICENSE",
                   "docs", "examples", "prompts", "templates", "schemas", "scripts"}
    for entry in sorted(root.iterdir()):
        if entry.name not in allowed_top and entry.name != "__pycache__":
            error(f"{SKILL_DIR}/{entry.name} is not part of the skill; keep repository files outside {SKILL_DIR}/")
    for name in ("install.py", "validate_skill.py"):
        if (root / "scripts" / name).exists():
            error(f"{SKILL_DIR}/scripts/{name} is a repository tool and must not ship with the skill")
    for extra in sorted((root / "scripts").glob("*.py")):
        if extra.name not in RUNTIME_SCRIPTS:
            warn(f"{SKILL_DIR}/scripts/{extra.name} will ship with the skill; add it to RUNTIME_SCRIPTS if intended")
    repo_license, skill_license = ROOT / "LICENSE", root / "LICENSE"
    if repo_license.is_file() and skill_license.is_file():
        def normalized(path: Path) -> str:
            return path.read_text(encoding="utf-8").replace("\r\n", "\n")

        if normalized(repo_license) != normalized(skill_license):
            error(f"{SKILL_DIR}/LICENSE must match the repository LICENSE")


def check_no_em_dashes_in_core() -> None:
    """Project style: plain hyphen, not em dash."""
    core = [
        "README.md",
        skill("SKILL.md"),
        skill("paem.md"),
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


SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def parse_frontmatter(fm: str) -> dict[str, str]:
    """Read top-level keys, folding `>` and `|` block scalars and nested maps into strings."""
    fields: dict[str, str] = {}
    key = None
    style = ""
    lines: list[str] = []

    def flush() -> None:
        if key is not None:
            joined = "\n".join(lines) if style == "|" else " ".join(lines)
            fields[key] = joined.strip()

    for raw in fm.splitlines():
        top = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if top:
            flush()
            key, value = top.group(1), top.group(2).strip()
            style = value[:1] if value[:1] in (">", "|") else ""
            lines = [] if style or not value else [value.strip("'\"")]
        elif key is not None and raw.strip():
            lines.append(raw.strip())
    flush()
    return fields


def check_agent_skills_spec(fields: dict[str, str]) -> None:
    """Enforce the agentskills.io constraints every compliant host relies on."""
    unknown = sorted(set(fields) - SPEC_KEYS)
    if unknown:
        error(f"SKILL.md frontmatter has keys outside the Agent Skills spec: {', '.join(unknown)}")
    name = fields.get("name", "")
    if not (1 <= len(name) <= 64 and re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name)):
        error("SKILL.md name must be 1-64 lowercase letters, digits and single hyphens")
    description = fields.get("description", "")
    if not 1 <= len(description) <= 1024:
        error(f"SKILL.md description must be 1-1024 characters (found {len(description)})")
    if "compatibility" in fields and not 1 <= len(fields["compatibility"]) <= 500:
        error("SKILL.md compatibility must be 1-500 characters")
    # Hosts expect the folder name to equal `name`; every install target must end in it.
    from install import PATHS  # noqa: E402

    for provider, scopes in PATHS.items():
        for scope, rel in scopes.items():
            if rel and Path(rel).name != name:
                error(f"install.py {provider} {scope} path {rel} does not end in the skill name {name!r}")


def check_skill_md() -> None:
    path = require_file(skill("SKILL.md"))
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
    fields = parse_frontmatter(fm)
    check_agent_skills_spec(fields)
    if fields.get("name") != Path(SKILL_DIR).name:
        error(f"SKILL.md name must match its folder name ({Path(SKILL_DIR).name})")
    body = parts[2]
    if len(body.splitlines()) > 500:
        warn("SKILL.md body is over 500 lines; the Agent Skills spec recommends moving detail into referenced files")
    for needle in (".paem/", "checkpoint", "resume", "Verify"):
        if needle.lower() not in body.lower():
            error(f"SKILL.md body missing expected concept: {needle}")


def check_skill_yaml() -> None:
    path = require_file(skill("skill.yaml"))
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
    path = require_file(skill("templates/checkpoint.json"))
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


def check_schemas_are_valid_json() -> None:
    """Both schema files must at least parse as JSON."""
    for rel in (skill("schemas/checkpoint.schema.json"), skill("schemas/execution_report.schema.json")):
        path = ROOT / rel
        if not path.is_file():
            continue  # already reported by check_layout()
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            error(f"{rel} is not valid JSON: {exc}")


def check_checkpoint_schema() -> None:
    """Validate checkpoint JSON files against schemas/checkpoint.schema.json."""
    schema_path = ROOT / skill("schemas/checkpoint.schema.json")
    if not schema_path.is_file():
        return  # already reported by check_layout()
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(f"{skill('schemas/checkpoint.schema.json')} is not valid JSON: {exc}")
        return

    candidates = [
        skill("templates/checkpoint.json"),
        "fixtures/sample-project/.paem/latest_checkpoint.json",
        "fixtures/sample-project/.paem/checkpoints/checkpoint-000.json",
        "fixtures/sample-project/.paem/checkpoints/checkpoint-001.json",
    ]
    for rel in candidates:
        path = ROOT / rel
        if not path.is_file():
            continue  # already reported by check_layout()
        try:
            instance = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            error(f"{rel} is not valid JSON: {exc}")
            continue
        for msg in paem_schema_lib.validate(instance, schema):
            error(f"{rel} fails schema: {msg}")


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

    guard_scripts = ["scripts/install.py", *(skill(f"scripts/{name}") for name in RUNTIME_SCRIPTS)]
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
    templates = ROOT / skill("templates")
    if not templates.is_dir():
        error(f"{skill('templates')}/ missing; skip dry-run")
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
    check_skill_folder_is_only_the_skill()
    check_license()
    check_skill_md()
    check_skill_yaml()
    check_checkpoint_template()
    check_schemas_are_valid_json()
    check_checkpoint_schema()
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
