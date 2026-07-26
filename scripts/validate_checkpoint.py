#!/usr/bin/env python3
"""Validate a PAEM checkpoint JSON file against schemas/checkpoint.schema.json.

Usage:
    python scripts/validate_checkpoint.py .paem/latest_checkpoint.json
    python scripts/validate_checkpoint.py .paem/checkpoints/*.json
    python scripts/validate_checkpoint.py --schema path/to/other.schema.json file.json

Exit code 0 = every file valid, 1 = at least one invalid or unreadable.
This is a small, dependency-free CLI wrapper around paem_schema_lib.py -
useful for a pre-commit hook, CI step, or the `Stronger verification`
guidance in prompts/verify.md when an agent wants to check its own
checkpoint before writing it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paem_schema_lib  # noqa: E402

DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "checkpoint.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", help="Checkpoint JSON file(s) to validate")
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help=f"Path to a JSON Schema file (default: {DEFAULT_SCHEMA.relative_to(DEFAULT_SCHEMA.parents[1])})",
    )
    args = parser.parse_args()

    try:
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"Cannot read schema {args.schema}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Schema {args.schema} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    exit_code = 0
    for file_arg in args.files:
        path = Path(file_arg)
        if not path.is_file():
            print(f"FAIL {path}: file not found")
            exit_code = 1
            continue
        try:
            instance = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"FAIL {path}: not valid JSON ({exc})")
            exit_code = 1
            continue

        errors = paem_schema_lib.validate(instance, schema)
        if errors:
            print(f"FAIL {path}")
            for err in errors:
                print(f"  - {err}")
            exit_code = 1
        else:
            print(f"OK   {path}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
