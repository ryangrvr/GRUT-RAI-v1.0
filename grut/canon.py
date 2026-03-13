import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .utils import stable_sha256
from .exceptions import CanonError, ValidationError
from .schema_validate import validate_json_schema


@dataclass(frozen=True)
class OperatorSpec:
    stack_key: str
    op_id: str
    role: str
    parameters: List[str]
    math: List[str]


class GRUTCanon:
    def __init__(self, canon_path: str):
        self.canon_path = Path(canon_path)
        self.schema_dir = self.canon_path.resolve().parent

        with open(self.canon_path, "r", encoding="utf-8") as f:
            self.data: Dict[str, Any] = json.load(f)

        # Machine validation: ensure the canon matches the checked-in schema.
        schema_version = self.data.get("meta", {}).get("schema_version", "v0.2")
        if schema_version == "v0.3":
            schema_path = self.schema_dir / "grut_canon_schema_v0.3.json"
        else:
            schema_path = self.schema_dir / "grut_canon_schema_v0.2.json"
        validate_json_schema(self.data, schema_path)

        self._validate_minimal()

        self.constants_by_id: Dict[str, Any] = self.data["constants"]["by_id"]
        self.aliases: Dict[str, str] = self.data["constants"].get("aliases", {})
        self.stack_order: List[str] = self.data["operator_stack"]["execution_order"]
        self.operator_defs: Dict[str, Any] = self.data["operator_stack"]["definitions"]

        self.numeric_policy: Dict[str, Any] = self.data.get("numeric_policy", {})
        self.canon_hash: str = stable_sha256(self.data)
        self.schema_version: str = schema_version

        self.operators: List[OperatorSpec] = []
        for stack_key in self.stack_order:
            if stack_key not in self.operator_defs:
                raise CanonError(f"Operator stack key missing definition: {stack_key}")
            d = self.operator_defs[stack_key]
            self.operators.append(
                OperatorSpec(
                    stack_key=stack_key,
                    op_id=d["id"],
                    role=d.get("role", ""),
                    parameters=list(d.get("parameters", [])),
                    math=list(d.get("math", [])),
                )
            )

    def _validate_minimal(self) -> None:
        required = [
            "meta",
            "unit_system",
            "constants",
            "primitives",
            "memory_kernel",
            "operator_stack",
            "core_equations",
            "numeric_policy",
            "assumptions_registry",
            "observables",
        ]
        for k in required:
            if k not in self.data:
                raise ValidationError(f"Canon missing section: {k}")

        if "by_id" not in self.data["constants"]:
            raise ValidationError("Canon constants must include constants.by_id")
        if "execution_order" not in self.data["operator_stack"]:
            raise ValidationError("Canon operator_stack must include execution_order")
        if "definitions" not in self.data["operator_stack"]:
            raise ValidationError("Canon operator_stack must include definitions")

    def resolve_id(self, const_id_or_alias: str) -> str:
        return self.aliases.get(const_id_or_alias, const_id_or_alias)

    def get_value(self, const_id_or_alias: str) -> float:
        cid = self.resolve_id(const_id_or_alias)
        if cid not in self.constants_by_id:
            raise CanonError(f"Unknown constant/parameter id: {const_id_or_alias} -> {cid}")
        return float(self.constants_by_id[cid]["value"])

    def get_bounds(self, const_id_or_alias: str) -> Optional[tuple[float, float]]:
        cid = self.resolve_id(const_id_or_alias)
        entry = self.constants_by_id.get(cid)
        if not entry:
            return None
        b = entry.get("bounds")
        if not b:
            return None
        return float(b[0]), float(b[1])
