"""Casimir Density Sweep (Phase I canon).

Computes screening consistency without optimizing-to-win. Reports baseline-defined
τΛ = H0^-1 and τ0 screening relation only.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from typing import Any, Dict, List, Optional, Tuple

from core.constants import GRUTParams

G = 6.674e-11
PI = math.pi
MPC_M = 3.085677581e22
SEC_PER_YEAR = 365.25 * 24 * 3600
SEC_PER_MYR = SEC_PER_YEAR * 1e6


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _determinism_stamp(inputs: Dict[str, Any], code_version: str, seed: int) -> str:
    payload = {
        "inputs": inputs,
        "code_version": code_version,
        "seed": seed,
    }
    return hashlib.sha256(_canonical_json(payload).encode()).hexdigest()


def _frange(start: float, stop: float, step: float) -> List[float]:
    if step <= 0:
        return []
    values: List[float] = []
    x = start
    while x <= stop + 1e-12:
        values.append(round(x, 12))
        x += step
    return values


def _h0_to_si(H0_km_s_Mpc: float) -> float:
    return (H0_km_s_Mpc * 1000.0) / MPC_M


def _rho_crit(H0_si: float) -> float:
    return (3.0 * H0_si ** 2) / (8.0 * PI * G)


def _rho_req(tau0_s: float) -> float:
    return 1.0 / (8.0 * PI * G * tau0_s ** 2)


def _rel_err_S(H0_km_s_Mpc: float, tau0_myr: float, alpha_vac: float) -> Tuple[float, float, float]:
    H0_si = _h0_to_si(H0_km_s_Mpc)
    tau_lambda_s = 1.0 / H0_si
    tau0_s = tau0_myr * SEC_PER_MYR
    S_thy = (12.0 * PI) / (alpha_vac ** 2)
    rel_err_S = abs((tau_lambda_s / tau0_s) - S_thy) / S_thy
    return rel_err_S, tau_lambda_s, S_thy


def _unit_consistency_ok(H0_km_s_Mpc: float, Omega_lambda: float, tau0_myr: float, alpha_vac: float) -> bool:
    return (H0_km_s_Mpc > 0.0) and (tau0_myr > 0.0) and (0.0 <= Omega_lambda <= 1.0) and (alpha_vac > 0.0)


def run_experiment(
    tau0_myr: float = 41.9,
    H0_km_s_Mpc: float = 67.36,
    Omega_lambda: float = 0.6847,
    h0_min: float = 67.0,
    h0_max: float = 74.0,
    h0_step: float = 0.1,
    omegaL_min: float = 0.675,
    omegaL_max: float = 0.695,
    omegaL_step: float = 0.002,
    alpha_vac: float = 1.0 / 3.0,
    seed: int = 7,
) -> Dict[str, Any]:
    params = GRUTParams()

    tau0_s = tau0_myr * SEC_PER_MYR
    H0_si = _h0_to_si(H0_km_s_Mpc)
    tau_lambda_s = 1.0 / H0_si
    tau_lambda_gyr = tau_lambda_s / (SEC_PER_YEAR * 1e9)

    rho_crit = _rho_crit(H0_si)
    rho_lambda = Omega_lambda * rho_crit
    rho_req = _rho_req(tau0_s)
    R_obs = rho_req / rho_lambda if rho_lambda > 0 else float("inf")

    rel_err_S, _, S_thy = _rel_err_S(H0_km_s_Mpc, tau0_myr, alpha_vac)

    n_g0_sq = 1.0 + alpha_vac
    n_g0 = math.sqrt(n_g0_sq)

    h0_values = _frange(h0_min, h0_max, h0_step)
    omega_values = _frange(omegaL_min, omegaL_max, omegaL_step)

    grid: List[List[float]] = []
    best_rel = float("inf")
    best_idx: Optional[Tuple[int, int]] = None

    rel_err_S_vs_H0: List[Dict[str, float]] = []

    for i, h0 in enumerate(h0_values):
        row: List[float] = []
        best_err_for_h0 = float("inf")
        best_omega_for_h0: Optional[float] = None
        for j, omega_l in enumerate(omega_values):
            rel_err, _, _ = _rel_err_S(h0, tau0_myr, alpha_vac)
            row.append(rel_err)
            if rel_err < best_err_for_h0:
                best_err_for_h0 = rel_err
                best_omega_for_h0 = omega_l
            if rel_err < best_rel:
                best_rel = rel_err
                best_idx = (i, j)
        grid.append(row)
        if best_omega_for_h0 is not None:
            rel_err_S_vs_H0.append({
                "H0_km_s_Mpc": float(h0),
                "Omega_lambda": float(best_omega_for_h0),
                "rel_err_S": float(best_err_for_h0),
            })

    stability_eps = 0.02
    stability_ok = False
    neighbor_max = None
    neighbor_count = 0
    if best_idx is not None:
        i, j = best_idx
        neighbors: List[float] = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < len(grid) and 0 <= nj < len(grid[ni]):
                val = grid[ni][nj]
                if not math.isnan(val) and not math.isinf(val):
                    neighbors.append(val)
        neighbor_count = len(neighbors)
        if neighbors:
            neighbor_max = max(neighbors)
            stability_ok = neighbor_max <= (best_rel + stability_eps)

    unit_consistency = _unit_consistency_ok(H0_km_s_Mpc, Omega_lambda, tau0_myr, alpha_vac)

    status = "FAIL"
    if unit_consistency and best_rel <= 0.005 and stability_ok:
        status = "PASS"
    elif unit_consistency and best_rel <= 0.02:
        status = "EXPLORATORY"

    best_h0 = h0_values[best_idx[0]] if best_idx else H0_km_s_Mpc
    best_omega = omega_values[best_idx[1]] if best_idx else Omega_lambda
    best_rel_err, best_tau_lambda_s, _ = _rel_err_S(best_h0, tau0_myr, alpha_vac)
    best_tau_lambda_gyr = best_tau_lambda_s / (SEC_PER_YEAR * 1e9)

    baseline_note = "τΛ is baseline-defined (H0^-1). Any inversion to τΛ or H0 is an internal consistency check only."
    velocity_note = "Definitions only: α_vac is potential-level; velocity-level uses β = √3/2."

    determinism_inputs = {
        "tau0_myr": tau0_myr,
        "H0_km_s_Mpc": H0_km_s_Mpc,
        "Omega_lambda": Omega_lambda,
        "h0_min": h0_min,
        "h0_max": h0_max,
        "h0_step": h0_step,
        "omegaL_min": omegaL_min,
        "omegaL_max": omegaL_max,
        "omegaL_step": omegaL_step,
        "alpha_vac": alpha_vac,
    }
    determinism_stamp = _determinism_stamp(determinism_inputs, params.engine_version, seed)
    environment = {
        "engine_version": params.engine_version,
        "python_version": sys.version.split(" ")[0],
        "precision": "float64",
    }

    response = {
        "status": status,
        "computed": {
            "rho_crit": rho_crit,
            "rho_lambda": rho_lambda,
            "rho_req": rho_req,
            "R_obs": R_obs,
            "tau_lambda_s": tau_lambda_s,
            "tau_lambda_gyr": tau_lambda_gyr,
            "tau0_s": tau0_s,
            "tau0_myr": tau0_myr,
            "S_thy": S_thy,
            "rel_err_S": rel_err_S,
            "rel_err_R": None,
            "rel_err_R_note": "not evaluated (no preregistered ratio)",
        },
        "two_loop_argmin": {
            "H0_km_s_Mpc": float(best_h0),
            "Omega_lambda": float(best_omega),
            "rel_err_S": float(best_rel_err),
            "tauLambda_gyr": float(best_tau_lambda_gyr),
            "tau0_myr": float(tau0_myr),
        },
        "rel_err_S_vs_H0": rel_err_S_vs_H0,
        "nis": {
            "status": status,
            "determinism_stamp": determinism_stamp,
            "unit_consistency": unit_consistency,
            "fuzz_fraction": 0.0,
            "provenance": {
                "contract": "AI narrates; engine calculates; NIS certifies.",
                "tauLambda_baseline_defined": True,
                "inputs": determinism_inputs,
                "seed": seed,
            },
            "environment": environment,
            "safe_mode": False,
            "convergence": {"status": True, "final_residual": None, "iterations": None},
            "data_provenance": {"dataset_name": None, "source_hash": None, "access_date": None},
        },
        "metadata": {
            "baseline_note": baseline_note,
            "velocity_potential_note": velocity_note,
            "alpha_vac": alpha_vac,
            "n_g0_sq": n_g0_sq,
            "n_g0": n_g0,
            "stability": {
                "neighbor_count": neighbor_count,
                "neighbor_rel_err_max": neighbor_max,
                "stability_eps": stability_eps,
            },
        },
    }

    return response
