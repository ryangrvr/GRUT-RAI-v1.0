from __future__ import annotations

from typing import Dict, Any, List, Optional
import hashlib
import json
import sys

from .constants import GRUTParams
from .schemas import NISIntegrityFailure, CFLErrorDiagnostic, CFLCorrectionLogic

MYR_IN_S = 1_000_000 * 365.25 * 24 * 3600

class SovereignCausalError(Exception):
    """Raised when causal integrity (CFL) fails; payload is a structured correction."""
    def __init__(self, payload: Dict[str, Any]):
        super().__init__("CFL_VIOLATION")
        self.payload = payload

def compute_cfl(v_in_m_s: float, dt_used_s: float, L_char_m: float) -> float:
    if L_char_m <= 0:
        return float("inf")
    return abs(float(v_in_m_s)) * abs(float(dt_used_s)) / float(L_char_m)


def compute_determinism_stamp(inputs: Dict[str, Any], code_version: str, seed: int) -> str:
    payload = {
        "inputs": inputs,
        "code_version": code_version,
        "seed": seed,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def cfl_gate_or_raise(
    v_in_m_s: float,
    dt_used_s: float,
    params: GRUTParams,
    current_eps_t_myr: float,
    frame_factor: float = 1.0,
) -> None:
    """Hard-stop CFL gate. On violation, raises SovereignCausalError with a Metabolic Correction payload.

    Note: dt_used_s is the effective sampling window used by the observer layer.
    frame_factor maps eps_t -> eps_user (dt_used = eps_t * frame_factor).
    """
    cfl = compute_cfl(v_in_m_s, dt_used_s, params.L_char_m)
    if cfl <= params.CFL_max:
        return

    # Diamond Lock-aligned elastic response scale (engine stability proxy)
    v_limit = params.beta_lock * params.c_vacuum

    required_dt = (params.CFL_max * params.L_char_m) / max(abs(float(v_in_m_s)), 1e-12)

    # Convert required dt back into eps_t using frame_factor
    ff = max(float(frame_factor), 1e-9)
    required_eps_myr = (required_dt / MYR_IN_S) / ff

    failure = NISIntegrityFailure(
        diagnostic=CFLErrorDiagnostic(
            cfl_value=float(cfl),
            cfl_max=float(params.CFL_max),
            v_in_m_s=float(v_in_m_s),
            v_limit_m_s=float(v_limit),
            dt_used_s=float(dt_used_s),
            L_char_m=float(params.L_char_m),
            frame_factor=float(frame_factor),
            message="Causal integrity gate failed: implied change rate outruns sampling window (CFL violation).",
        ),
        correction_logic=CFLCorrectionLogic(
            required_dt_s=float(required_dt),
            required_eps_t_myr=float(required_eps_myr),
            current_eps_t_myr=float(current_eps_t_myr),
            slider_min_eps_t_myr=float(min(current_eps_t_myr, required_eps_myr)),
            slider_target_eps_t_myr=float(required_eps_myr),
            recommendations=[
                "Decrease ε (increase sampling resolution)",
                "Reduce v_obs / velocity delta",
                "Increase L_char (coarser characteristic step) only if physically intended",
            ],
        ),
    )
    raise SovereignCausalError(failure.model_dump())


def handoff_accounting_check(W_phase: float, D_eff: float, kappa: float) -> bool:
    return float(D_eff) >= float(kappa) * float(W_phase)


def build_nis_report(
    internal: Dict[str, Any],
    params: GRUTParams,
    hz_model: str,
    cfl_value: float,
    determinism_stamp: Optional[str] = None,
    unit_consistency: Optional[bool] = None,
    provenance: Optional[Dict[str, Any]] = None,
    safe_mode: Optional[bool] = None,
    convergence: Optional[Dict[str, Any]] = None,
    environment: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a Phase D NIS report from engine diagnostics + observer diagnostics."""
    warnings: List[str] = []

    # Handoff accounting
    W_phase = float(internal.get("W_phase", 0.0))
    D_eff = float(internal.get("D_eff", 0.0))
    handoff_required = float(params.handoff_kappa) * float(W_phase)
    handoff_pass = float(D_eff) >= handoff_required
    if not handoff_pass:
        warnings.append("PHASE_HANDOFF_BUDGET: dissipation below kappa*W_phase")

    # Information heat
    I_heat = float(internal.get("D_max", 0.0))
    if I_heat > 0.10:
        warnings.append("INFO_HEAT_HIGH: D_max > 0.10")

    # Bounded gain invariant
    g_min = float(internal.get("g_min", 0.0))
    g_max_obs = float(internal.get("g_max_obs", 0.0))
    tol = 1e-6
    if g_min < 1.0 - tol or g_max_obs > params.g_max + tol:
        warnings.append("GAIN_BOUNDS: g outside [1, 4/3] within tolerance")

    # Smoothness diagnostic
    kink_metric = float(internal.get("kink_metric", 0.0))
    z_len = int(internal.get("z_len", 0))
    if z_len >= int(params.min_z_for_smoothness) and kink_metric > float(params.kink_thresh):
        warnings.append("SMOOTHNESS_WARN: high second-derivative magnitude near pivot")

    # Observer layer warnings passthrough
    for w in internal.get("observer_warnings", []) or []:
        warnings.append(str(w))

    # Status selection
    status = "PASS"
    if any(w.startswith("GAIN_BOUNDS") for w in warnings):
        status = "FAIL"
    elif len(warnings) > 0:
        status = "WARN"

    env = environment or {
        "engine_version": params.engine_version,
        "python_version": sys.version.split(" ")[0],
        "precision": "float64",
    }
    report = {
        "status": status,

        "determinism_stamp": determinism_stamp,
        "unit_consistency": unit_consistency,
        "provenance": provenance,
        "environment": env,
        "safe_mode": safe_mode,
        "convergence": convergence,

        # Core
        "eps_t_myr": float(internal["eps_t_myr"]),
        "fuzz_fraction": float(internal["fuzz_fraction"]),
        "cap_engaged_frac": float(internal.get("cap_engaged_frac", 0.0)),
        "pivot_intensity": float(internal.get("pivot_intensity", 0.0)),
        "I_heat": float(I_heat),
        "cfl_value": float(cfl_value),
        "cfl_max": float(params.CFL_max),
        "W_phase": float(W_phase),
        "D_eff": float(D_eff),
        "handoff_pass": bool(handoff_pass),
        "handoff_required": float(handoff_required),
        "handoff_margin": float(D_eff - handoff_required),
        "g_min": float(g_min),
        "g_max_obs": float(g_max_obs),
        "kink_metric": float(kink_metric),
        "z_len": int(z_len),

        # Observer layer
        "observer_profile": internal.get("observer_profile", "monk"),
        "eps_user_s": float(internal.get("eps_user_s", 0.0)),
        "deltaS": float(internal.get("deltaS", 0.0)),
        "I_value": float(internal.get("I_value", 1.0)),
        "P_lock": float(internal.get("P_lock", 0.0)),
        "tension_score": float(internal.get("tension_score", 0.0)),
        "tension_color": internal.get("tension_color", "green"),
        "metabolic_state": internal.get("metabolic_state", "CALM"),
        "ui_entropy": float(internal.get("ui_entropy", 0.0)),
        "sensor_mode": internal.get("sensor_mode", "off"),
        "sensor_flux": float(internal.get("sensor_flux", 0.0)),
        "sensor_snapshot_hash": internal.get("sensor_snapshot_hash"),
        "sensor_reproducible": bool(internal.get("sensor_reproducible", True)),

        "warnings": warnings,
        "engine_version": params.engine_version,
        "params_hash": params.params_hash(),
        "hz_model": hz_model,
    }
    return report
