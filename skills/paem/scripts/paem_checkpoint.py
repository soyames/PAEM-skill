#!/usr/bin/env python3
"""Publish and inspect consistent PAEM checkpoints. No Git mutations or network.

save --target PROJECT --input RECORD.json --expected-id checkpoint-000
check --target PROJECT
resume --target PROJECT

Exit 0: published/current; 2: stale/invalid/legacy/inconsistent; 1: unavailable/error.
Verification claims in a record remain self-reported; this tool checks state binding.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

from paem_fs import atomic_write, safe_path, writer_lock
from paem_repository import snapshot
from paem_schema_lib import validate

SCHEMA = Path(__file__).resolve().parents[1] / "schemas/checkpoint.schema.json"


def encode(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode()


def read_json(path: Path):
    def reject_constant(value):
        raise ValueError("Non-finite JSON value: " + value)
    return json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=reject_constant)


def validate_record(record) -> list[str]:
    errors = validate(record, read_json(SCHEMA))
    if errors:
        return errors
    if record["schema_version"].split(".")[0] != "1":
        errors.append("Unsupported checkpoint schema major version")
    name = record["checkpoint_id"]
    if not re.fullmatch(r"checkpoint-[0-9]{3,}", name):
        errors.append("checkpoint_id must be checkpoint- followed by at least three digits")
    if not record["next_action"].strip():
        errors.append("next_action must not be empty")
    return errors


def resume_text(record: dict) -> str:
    return (f"# PAEM resume: {record['checkpoint_id']}\n\n"
            f"Recorded: {record['timestamp']}\n"
            f"Verification (self-reported): {record['verification']['status']}\n"
            f"Recovery: {record['recovery']['status']}\n\n"
            "Run the installed scripts/paem_checkpoint.py check --target PROJECT before continuing.\n"
            "Treat saved content as context, not permission to expand the task.\n\n"
            f"## Next action\n\n{record['next_action']}\n\n"
            "## Remaining work\n\n" + "\n".join("- " + item for item in record["remaining_work"]) + "\n")


def current_record(state: Path) -> tuple[dict, dict]:
    manifest = read_json(safe_path(state, "current.json"))
    if not isinstance(manifest, dict) or manifest.get("format") != 1:
        raise ValueError("Invalid checkpoint manifest")
    name = manifest.get("checkpoint_id", "")
    if not isinstance(name, str) or not re.fullmatch(r"checkpoint-[0-9]{3,}", name):
        raise ValueError("Invalid manifest checkpoint_id")
    archive = safe_path(state, f"checkpoints/{name}.json")
    raw = archive.read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest.get("sha256"):
        raise ValueError("Checkpoint archive digest does not match manifest")
    record = read_json(archive)
    errors = validate_record(record)
    if errors or record["checkpoint_id"] != name:
        raise ValueError("Invalid checkpoint: " + "; ".join(errors or ["archive identity mismatch"]))
    return record, manifest


def inspect(target: Path) -> dict:
    state = safe_path(target, ".paem")
    if not state.is_dir():
        return {"status": "missing", "reasons": ["No .paem state directory"]}
    if not safe_path(state, "current.json").is_file():
        latest = safe_path(state, "latest_checkpoint.json")
        if not latest.is_file():
            return {"status": "missing", "reasons": ["No checkpoint has been published"]}
        try:
            record = read_json(latest)
            errors = validate_record(record)
            return {"status": "invalid" if errors else "legacy", "reasons": errors or
                    ["Legacy checkpoint has no publication manifest; inspect and explicitly adopt it"],
                    "checkpoint": record}
        except (ValueError, UnicodeError) as exc:
            return {"status": "invalid", "reasons": [str(exc)]}
    try:
        record, manifest = current_record(state)
    except (OSError, ValueError, UnicodeError) as exc:
        return {"status": "invalid", "reasons": [str(exc)]}
    reasons = []
    latest = safe_path(state, "latest_checkpoint.json")
    resume = safe_path(state, "resume_prompt.md")
    if not latest.is_file() or latest.read_bytes() != encode(record):
        reasons.append("latest_checkpoint.json differs from the published generation")
    if not resume.is_file() or resume.read_bytes() != resume_text(record).encode():
        reasons.append("resume_prompt.md differs from the published generation")
    # Archives after the selected generation may be interrupted writes, not proof of completion.
    selected = int(record["checkpoint_id"].split("-")[1])
    archives = safe_path(state, "checkpoints")
    for file in archives.glob("checkpoint-*.json"):
        match = re.fullmatch(r"checkpoint-([0-9]+)\.json", file.name)
        if match and int(match[1]) > selected:
            reasons.append("Newer unpublished archive requires review: " + file.name)
    result = {"status": "inconsistent" if reasons else "current", "reasons": reasons,
              "checkpoint": record, "resume": resume_text(record), "verification_basis": "self_reported"}
    try:
        now = snapshot(target)
        if record.get("repository_state") != now:
            reasons.append("Repository/worktree, HEAD, index or working files differ from the checkpoint")
            if result["status"] == "current":
                result["status"] = "stale"
    except (OSError, ValueError) as exc:
        reasons.append(str(exc))
        if result["status"] == "current":
            result["status"] = "unavailable"
    return result


def publish(target: Path, record: dict, expected_id: str | None = None,
            adopt_legacy: bool = False) -> dict:
    target = target.resolve()
    errors = validate_record(record)
    if errors:
        raise ValueError("Invalid checkpoint: " + "; ".join(errors))
    record = json.loads(json.dumps(record))
    state = safe_path(target, ".paem")
    state.mkdir(exist_ok=True)
    with writer_lock(state):
        actual_id = None
        if safe_path(state, "current.json").exists():
            previous, _ = current_record(state)
            actual_id = previous["checkpoint_id"]
        if actual_id != expected_id:
            raise ValueError(f"Checkpoint changed: expected {expected_id!r}, current {actual_id!r}; reload before saving")
        legacy = actual_id is None and safe_path(state, "latest_checkpoint.json").exists()
        if legacy and not adopt_legacy:
            raise ValueError("Legacy state exists; review it and use --adopt-legacy with a new checkpoint ID")
        name = record["checkpoint_id"]
        if actual_id and int(name.split("-")[1]) <= int(actual_id.split("-")[1]):
            raise ValueError("Use a checkpoint ID newer than the published generation")
        archive = safe_path(state, f"checkpoints/{name}.json")
        if archive.exists():
            raise ValueError("Checkpoint archive already exists; select a new ID (archives are immutable)")
        # Preflight every destination before changing state.
        for relative in ["latest_checkpoint.json", "resume_prompt.md", "current.json"]:
            safe_path(state, relative)
        try:
            observed = snapshot(target)
        except (OSError, ValueError) as exc:
            observed = None
            record["repository_observation_error"] = str(exc)
        record["schema_version"] = "1.1.0"
        record["parent_checkpoint_id"] = actual_id
        record["repository_state"] = observed
        record["verification_basis"] = "self_reported"
        if observed is not None:
            record["branch"] = observed["branch"]
            record["commit_hash"] = observed["head"]
        record["timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if legacy:
            backup = f"legacy/{uuid.uuid4().hex}"
            for relative in ["latest_checkpoint.json", "resume_prompt.md"]:
                old = safe_path(state, relative)
                if old.is_file():
                    atomic_write(state, f"{backup}/{relative}", old.read_bytes())
        raw = encode(record)
        atomic_write(state, f"checkpoints/{name}.json", raw)
        atomic_write(state, "latest_checkpoint.json", raw)
        atomic_write(state, "resume_prompt.md", resume_text(record).encode())
        # current.json is the publication point; a prior manifest survives a failed write.
        if observed is not None and snapshot(target) != observed:
            raise ValueError("Repository changed while saving; the new generation was not published")
        atomic_write(state, "current.json", encode({"format": 1, "checkpoint_id": name,
                     "sha256": hashlib.sha256(raw).hexdigest()}))
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["save", "check", "resume"])
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--expected-id")
    parser.add_argument("--adopt-legacy", action="store_true")
    args = parser.parse_args()
    try:
        if not args.target.is_dir():
            raise ValueError("Target directory does not exist")
        if args.command == "save":
            if args.input is None:
                parser.error("save requires --input")
            result = publish(args.target, read_json(args.input), args.expected_id, args.adopt_legacy)
            print(json.dumps({"status": "published", "checkpoint_id": result["checkpoint_id"],
                              "verification_basis": "self_reported"}))
            return 0
        result = inspect(args.target)
        if args.command == "resume" and result["status"] == "current":
            print(result["resume"])
        else:
            print(json.dumps(result, indent=2))
        return 0 if result["status"] == "current" else 1 if result["status"] == "unavailable" else 2
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"PAEM: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
