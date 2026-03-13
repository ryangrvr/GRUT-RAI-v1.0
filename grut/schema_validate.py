"""JSON Schema validation utilities.

Phase 2 contract: canon and NIS certificates are machine-validated against the
checked-in JSON Schemas in /canon.

This intentionally fails fast on schema errors to prevent silent drift.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .exceptions import ValidationError


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise ValidationError(f"Schema file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ValidationError(f"Schema JSON parse error: {path}: {e}") from e


def validate_json_schema(instance: Any, schema_path: str | Path) -> None:
    """Validate instance against the JSON schema at schema_path.

    Raises ValidationError on any schema or instance violation.
    """
    try:
        from jsonschema import Draft202012Validator
    except Exception as e:
        raise ValidationError(
            "jsonschema dependency is required for schema validation. "
            "Install requirements.txt (includes jsonschema==4.23.0)."
        ) from e

    schema_path = Path(schema_path)
    schema = _load_json(schema_path)

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as e:
        raise ValidationError(f"Invalid JSON Schema: {schema_path}: {e}") from e

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda er: list(er.path))
    if errors:
        # Show the first error with a readable JSON pointer.
        er = errors[0]
        pointer = "/" + "/".join(str(p) for p in er.path) if er.path else "/"
        raise ValidationError(
            f"Schema validation failed at {pointer}: {er.message} (schema: {schema_path})"
        )
