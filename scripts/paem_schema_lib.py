#!/usr/bin/env python3
"""Shared, dependency-free JSON Schema (2020-12 subset) validator.

Used by scripts/validate_skill.py (CI) and scripts/validate_checkpoint.py
(standalone CLI) so the validation logic exists in exactly one place.

Supports exactly the keywords used under schemas/: type, required,
properties, additionalProperties (bool only), items, enum, pattern,
minimum, maximum. Deliberately not a general-purpose implementation - this
project stays dependency-free rather than pulling in the `jsonschema`
package for two small internal schemas. If the schemas grow to need more
of the spec, reconsider that tradeoff.
"""

from __future__ import annotations

import re

_TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "object": dict,
    "array": list,
    "null": type(None),
}


def _check_type(value: object, expected: str) -> bool:
    py_type = _TYPE_MAP.get(expected)
    if py_type is None:
        return True
    if expected in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, py_type)


def validate(instance: object, schema: dict, path: str = "$") -> list[str]:
    """Validate instance against schema, returning a list of error strings."""
    errors: list[str] = []

    expected_types = schema.get("type")
    if expected_types is not None:
        candidates = [expected_types] if isinstance(expected_types, str) else expected_types
        if not any(_check_type(instance, t) for t in candidates):
            errors.append(f"{path}: expected type {candidates}, got {type(instance).__name__}")
            return errors  # further checks would be meaningless

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} not in enum {schema['enum']}")

    if "pattern" in schema and isinstance(instance, str):
        if not re.match(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match pattern {schema['pattern']!r}")

    if "minimum" in schema and isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if instance < schema["minimum"]:
            errors.append(f"{path}: {instance} below minimum {schema['minimum']}")

    if "maximum" in schema and isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if instance > schema["maximum"]:
            errors.append(f"{path}: {instance} above maximum {schema['maximum']}")

    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required field '{req}'")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate(value, properties[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected additional property '{key}'")

    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            errors.extend(validate(item, schema["items"], f"{path}[{i}]"))

    return errors
