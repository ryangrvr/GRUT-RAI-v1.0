import time
import uuid
from typing import Any, Dict, List

from .utils import stable_sha256


def init_certificate(
    *,
    engine_version: str,
    canon_hash: str,
    determinism_mode: str,
    input_state: Dict[str, Any],
    run_config: Dict[str, Any],
    assumption_toggles: Dict[str, Any],
    operator_stack_keys: List[str],
) -> Dict[str, Any]:
    return {
        "certificate_id": str(uuid.uuid4()),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engine_signature": {
            "version": engine_version,
            "canon_hash": canon_hash,
            "determinism_mode": determinism_mode,
        },
        "inputs": {
            "input_state_hash": stable_sha256(input_state),
            "run_config_hash": stable_sha256(run_config),
            "assumption_toggles": assumption_toggles,
        },
        "run_trace": {
            "operator_stack_keys": operator_stack_keys,
            "operators_executed_ids": [],
            "operator_execution_counts": {},
            "steps_computed": 0,
            "dt_years": float(run_config["dt_years"]),
            "integrator": run_config["integrator"],
            "convergence_metric": None,
            "warnings": [],
        },
        "outputs": {
            "observables_emitted": [],
            "output_digest": None,
        },
        "falsification_check": None,
    }


def finalize_certificate(
    cert: Dict[str, Any], outputs: Dict[str, Any], observables_emitted: List[str]
) -> Dict[str, Any]:
    cert["outputs"]["observables_emitted"] = list(observables_emitted)
    cert["outputs"]["output_digest"] = stable_sha256(outputs)
    return cert


def add_repro_hash(cert: Dict[str, Any]) -> Dict[str, Any]:
    stable = {
        "canon_hash": cert["engine_signature"]["canon_hash"],
        "input_state_hash": cert["inputs"]["input_state_hash"],
        "run_config_hash": cert["inputs"]["run_config_hash"],
        "assumption_toggles": cert["inputs"]["assumption_toggles"],
        "operators_executed_ids": cert["run_trace"]["operators_executed_ids"],
        "operator_execution_counts": cert["run_trace"].get("operator_execution_counts", {}),
        "output_digest": cert["outputs"]["output_digest"],
        "initial_conditions": cert.get("initial_conditions"),
    }
    cert["repro_hash"] = stable_sha256(stable)
    return cert
