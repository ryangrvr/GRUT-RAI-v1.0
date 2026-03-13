"""Canon override utilities for deterministic sweeps (no file mutation)."""

from __future__ import annotations

import copy
from typing import Any, Dict

from .canon import GRUTCanon, OperatorSpec
from .exceptions import CanonError, ValidationError
from .schema_validate import validate_json_schema
from .utils import stable_sha256


def override_canon(canon: GRUTCanon, overrides: Dict[str, Any]) -> GRUTCanon:
    data = copy.deepcopy(canon.data)
    constants_by_id = data["constants"]["by_id"]
    aliases = data["constants"].get("aliases", {})

    for key, value in (overrides or {}).items():
        const_id = aliases.get(key, key)
        if const_id not in constants_by_id:
            raise CanonError(f"Unknown constant/parameter id: {key} -> {const_id}")
        constants_by_id[const_id]["value"] = value

    schema_version = data.get("meta", {}).get("schema_version", "v0.2")
    if schema_version == "v0.3":
        schema_path = canon.schema_dir / "grut_canon_schema_v0.3.json"
    else:
        schema_path = canon.schema_dir / "grut_canon_schema_v0.2.json"
    validate_json_schema(data, schema_path)

    new_canon = object.__new__(GRUTCanon)
    new_canon.canon_path = canon.canon_path
    new_canon.schema_dir = canon.schema_dir
    new_canon.data = data
    new_canon._validate_minimal()

    new_canon.constants_by_id = data["constants"]["by_id"]
    new_canon.aliases = data["constants"].get("aliases", {})
    new_canon.stack_order = data["operator_stack"]["execution_order"]
    new_canon.operator_defs = data["operator_stack"]["definitions"]
    new_canon.numeric_policy = data.get("numeric_policy", {})
    new_canon.canon_hash = stable_sha256(data)
    new_canon.schema_version = schema_version

    new_canon.operators = []
    for stack_key in new_canon.stack_order:
        if stack_key not in new_canon.operator_defs:
            raise ValidationError(f"Canon missing operator definition: {stack_key}")
        d = new_canon.operator_defs[stack_key]
        new_canon.operators.append(
            OperatorSpec(
                stack_key=stack_key,
                op_id=d["id"],
                role=d.get("role", ""),
                parameters=list(d.get("parameters", [])),
                math=list(d.get("math", [])),
            )
        )

    return new_canon
