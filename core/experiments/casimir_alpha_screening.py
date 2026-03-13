"""Casimir Density / Alpha Screening Experiment.

Computes vacuum density ratios and tests preregistered candidate constants.
Reports numerical correspondence and robustness only (no mechanistic claims).
"""

from __future__ import annotations

import math
from typing import Dict, Any, List, Optional, Tuple

from core.constants import GRUTParams

# ----------------------------
# Constants (explicit per spec)
# ----------------------------

G = 6.674e-11
c = 2.99792458e8
SEC_PER_YEAR = 31557600.0
SEC_PER_MYR = SEC_PER_YEAR * 1_000_000
ALPHA_QED_INV = 137.035999084
ALPHA_QED = 1.0 / ALPHA_QED_INV
PI = math.pi
MPC_M = 3.085677581e22

params = GRUTParams()
ALPHA_VAC = params.alpha_vac
SCREENING_S = params.screening_S
N_G0_SQ = params.n_g0_sq
N_G0 = params.n_g0
HBAR_J_S = params.hbar_J_s


def _h0_to_si(H0_km_s_Mpc: float) -> float:
    return (H0_km_s_Mpc * 1000.0) / MPC_M


def _rho_lambda(H0_km_s_Mpc: float, Omega_m: float, Omega_lambda: Optional[float]) -> Tuple[float, float]:
    omega_l = (1.0 - Omega_m) if Omega_lambda is None else Omega_lambda
    H0_si = _h0_to_si(H0_km_s_Mpc)
    rho_crit = (3.0 * H0_si ** 2) / (8.0 * PI * G)
    rho_lambda = omega_l * rho_crit
    return rho_lambda, omega_l


def _rho_req(tau0_myr: float) -> float:
    tau_s = tau0_myr * SEC_PER_MYR
    return 1.0 / (8.0 * PI * G * (tau_s ** 2))


def _tau_lambda_gyr_from_h0(H0_km_s_Mpc: float) -> float:
    H0_si = _h0_to_si(H0_km_s_Mpc)
    tau_s = 1.0 / H0_si
    return tau_s / (SEC_PER_YEAR * 1e9)


def _frange(start: float, stop: float, step: float) -> List[float]:
    values: List[float] = []
    x = start
    if step <= 0:
        return values
    while x <= stop + 1e-12:
        values.append(round(x, 12))
        x += step
    return values


def _candidate_constants(include_qed: bool, include_exploratory: bool) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []

    if include_qed:
        candidates.extend([
            {"name": "pi_alpha_inv_sq_qed", "label": "π α_QED^-2 (non-canonical)", "value": PI * (ALPHA_QED_INV ** 2), "preregistered": False},
            {
                "name": "pi_alpha_inv_sq_two_loop_qed",
                "label": "π α_QED^-2 (1 - (4/3)α_QED) (non-canonical)",
                "value": (PI * (ALPHA_QED_INV ** 2)) * (1.0 - (4.0 / 3.0) * ALPHA_QED),
                "preregistered": False,
            },
            {"name": "alpha_inv_sq_qed", "label": "α_QED^-2 (non-canonical)", "value": (ALPHA_QED_INV ** 2), "preregistered": False},
            {"name": "pi_alpha_inv_qed", "label": "π α_QED^-1 (non-canonical)", "value": PI * ALPHA_QED_INV, "preregistered": False},
            {"name": "geom_4pi_over_3_alpha_inv_sq_qed", "label": "(4/3)π α_QED^-2 (non-canonical)", "value": (4.0 / 3.0) * PI * (ALPHA_QED_INV ** 2), "preregistered": False},
            {"name": "diamondlock_sq_alpha_inv_sq_qed", "label": "(2/√3)^2 α_QED^-2 (non-canonical)", "value": ((2.0 / math.sqrt(3.0)) ** 2) * (ALPHA_QED_INV ** 2), "preregistered": False},
        ])

        if include_exploratory:
            candidates.append({
                "name": "zeta_346_sq",
                "label": "346^2 (exploratory/post-hoc, non-canonical)",
                "value": 346.0 ** 2,
                "preregistered": False,
            })

    return candidates


def _evaluate_candidates(R: float, candidates: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for c in candidates:
        value = float(c["value"])
        rel_err = abs(R - value) / R
        rel_err_sqrt = abs(math.sqrt(R) - math.sqrt(value)) / math.sqrt(R)
        row = {
            "name": c["name"],
            "label": c["label"],
            "value": value,
            "rel_err": rel_err,
            "rel_err_sqrt": rel_err_sqrt,
            "preregistered": c.get("preregistered", True),
        }
        results.append(row)

    best = min(results, key=lambda r: r["rel_err"])
    return results, best


def _compute_R(tau0_myr: float, H0_km_s_Mpc: float, Omega_m: float, Omega_lambda: Optional[float]) -> Tuple[float, float, float, float, float, float]:
    rho_lambda, omega_l = _rho_lambda(H0_km_s_Mpc, Omega_m, Omega_lambda)
    rho_req = _rho_req(tau0_myr)
    R = rho_req / rho_lambda
    sqrtR = math.sqrt(R)
    tau_lambda_gyr = _tau_lambda_gyr_from_h0(H0_km_s_Mpc)
    return rho_lambda, rho_req, R, sqrtR, tau_lambda_gyr, omega_l


def _sweep(label: str, values: List[float],
           tau0_myr: float, H0_km_s_Mpc: float,
           Omega_m: float, Omega_lambda: Optional[float],
           cand_pi_alpha_inv_sq: float,
        cand_pi_alpha_inv_sq_two_loop: float,
           candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    min_R = float("inf")
    max_R = 0.0
    min_rel_err_pi = float("inf")
    max_rel_err_pi = 0.0
    min_rel_err_two_loop = float("inf")
    max_rel_err_two_loop = 0.0
    min_best_rel = float("inf")
    max_best_rel = 0.0

    for v in values:
        if label == "H0":
            _, _, R, _, _, _ = _compute_R(tau0_myr, v, Omega_m, Omega_lambda)
        elif label == "Omega_lambda":
            _, _, R, _, _, _ = _compute_R(tau0_myr, H0_km_s_Mpc, Omega_m, v)
        elif label == "tau0_myr":
            _, _, R, _, _, _ = _compute_R(v, H0_km_s_Mpc, Omega_m, Omega_lambda)
        else:
            continue

        rel_err_pi = abs(R - cand_pi_alpha_inv_sq) / R if cand_pi_alpha_inv_sq > 0 else float("nan")
        rel_err_two_loop = abs(R - cand_pi_alpha_inv_sq_two_loop) / R if cand_pi_alpha_inv_sq_two_loop > 0 else float("nan")
        best_rel = float("nan")
        if candidates:
            _, best = _evaluate_candidates(R, candidates)
            best_rel = float(best["rel_err"])

        min_R = min(min_R, R)
        max_R = max(max_R, R)
        if not math.isnan(rel_err_pi):
            min_rel_err_pi = min(min_rel_err_pi, rel_err_pi)
            max_rel_err_pi = max(max_rel_err_pi, rel_err_pi)
        if not math.isnan(rel_err_two_loop):
            min_rel_err_two_loop = min(min_rel_err_two_loop, rel_err_two_loop)
            max_rel_err_two_loop = max(max_rel_err_two_loop, rel_err_two_loop)
        if not math.isnan(best_rel):
            min_best_rel = min(min_best_rel, best_rel)
            max_best_rel = max(max_best_rel, best_rel)

    return {
        "label": label,
        "min_R": min_R,
        "max_R": max_R,
        "min_rel_err_pi_alpha_inv_sq": min_rel_err_pi,
        "max_rel_err_pi_alpha_inv_sq": max_rel_err_pi,
        "min_rel_err_pi_alpha_inv_sq_two_loop": min_rel_err_two_loop,
        "max_rel_err_pi_alpha_inv_sq_two_loop": max_rel_err_two_loop,
        "min_best_rel_err": min_best_rel,
        "max_best_rel_err": max_best_rel,
        "count": len(values),
    }


def run_experiment(
    tau0_myr: float = 41.9,
    H0_km_s_Mpc: float = 67.36,
    Omega_m: float = 0.315,
    Omega_lambda: Optional[float] = 0.6847,
    h0_min: float = 67.0,
    h0_max: float = 74.0,
    h0_step: float = 0.1,
    omegaL_min: float = 0.675,
    omegaL_max: float = 0.695,
    omegaL_step: float = 0.002,
    tau_frac: float = 0.01,
    match_eps_pass: float = 0.01,
    match_eps_warn: float = 0.02,
    include_qed_candidates: bool = False,
    include_exploratory_candidates: bool = False,
) -> Dict[str, Any]:
    """Run Casimir Density / Alpha Screening experiment."""

    rho_lambda, rho_req, R, sqrtR, tau_lambda_gyr, omega_l = _compute_R(
        tau0_myr, H0_km_s_Mpc, Omega_m, Omega_lambda
    )

    candidates = _candidate_constants(include_qed_candidates, include_exploratory_candidates)
    candidate_table: List[Dict[str, Any]] = []
    best: Optional[Dict[str, Any]] = None
    if candidates:
        candidate_table, best = _evaluate_candidates(R, candidates)

    cand_pi_alpha_inv_sq = next((c for c in candidates if c["name"] == "pi_alpha_inv_sq_qed"), None)
    cand_pi_alpha_inv_sq_two_loop = next((c for c in candidates if c["name"] == "pi_alpha_inv_sq_two_loop_qed"), None)
    cand_pi_alpha_inv_sq_val = float(cand_pi_alpha_inv_sq["value"]) if cand_pi_alpha_inv_sq else 0.0
    cand_pi_alpha_inv_sq_two_loop_val = float(cand_pi_alpha_inv_sq_two_loop["value"]) if cand_pi_alpha_inv_sq_two_loop else 0.0
    rel_err_pi = abs(R - cand_pi_alpha_inv_sq_val) / R if cand_pi_alpha_inv_sq_val > 0 else float("nan")
    rel_err_two_loop = abs(R - cand_pi_alpha_inv_sq_two_loop_val) / R if cand_pi_alpha_inv_sq_two_loop_val > 0 else float("nan")

    # Robustness checks for gating
    h0_minus = H0_km_s_Mpc * 0.98
    h0_plus = H0_km_s_Mpc * 1.02
    omega_minus = max(0.0, omega_l - 0.02)
    omega_plus = min(1.0, omega_l + 0.02)

    _, _, R_h0_minus, _, _, _ = _compute_R(tau0_myr, h0_minus, Omega_m, omega_l)
    _, _, R_h0_plus, _, _, _ = _compute_R(tau0_myr, h0_plus, Omega_m, omega_l)
    _, _, R_om_minus, _, _, _ = _compute_R(tau0_myr, H0_km_s_Mpc, Omega_m, omega_minus)
    _, _, R_om_plus, _, _, _ = _compute_R(tau0_myr, H0_km_s_Mpc, Omega_m, omega_plus)

    rel_err_h0_minus = abs(R_h0_minus - cand_pi_alpha_inv_sq_val) / R_h0_minus if cand_pi_alpha_inv_sq_val > 0 else float("nan")
    rel_err_h0_plus = abs(R_h0_plus - cand_pi_alpha_inv_sq_val) / R_h0_plus if cand_pi_alpha_inv_sq_val > 0 else float("nan")
    rel_err_om_minus = abs(R_om_minus - cand_pi_alpha_inv_sq_val) / R_om_minus if cand_pi_alpha_inv_sq_val > 0 else float("nan")
    rel_err_om_plus = abs(R_om_plus - cand_pi_alpha_inv_sq_val) / R_om_plus if cand_pi_alpha_inv_sq_val > 0 else float("nan")

    rel_err_two_loop_h0_minus = abs(R_h0_minus - cand_pi_alpha_inv_sq_two_loop_val) / R_h0_minus if cand_pi_alpha_inv_sq_two_loop_val > 0 else float("nan")
    rel_err_two_loop_h0_plus = abs(R_h0_plus - cand_pi_alpha_inv_sq_two_loop_val) / R_h0_plus if cand_pi_alpha_inv_sq_two_loop_val > 0 else float("nan")
    rel_err_two_loop_om_minus = abs(R_om_minus - cand_pi_alpha_inv_sq_two_loop_val) / R_om_minus if cand_pi_alpha_inv_sq_two_loop_val > 0 else float("nan")
    rel_err_two_loop_om_plus = abs(R_om_plus - cand_pi_alpha_inv_sq_two_loop_val) / R_om_plus if cand_pi_alpha_inv_sq_two_loop_val > 0 else float("nan")

    robust_ok_pi = False if math.isnan(rel_err_h0_minus) else all(err <= match_eps_warn for err in [rel_err_h0_minus, rel_err_h0_plus, rel_err_om_minus, rel_err_om_plus])
    robust_ok_two_loop = False if math.isnan(rel_err_two_loop_h0_minus) else all(err <= match_eps_warn for err in [rel_err_two_loop_h0_minus, rel_err_two_loop_h0_plus, rel_err_two_loop_om_minus, rel_err_two_loop_om_plus])

    # Status gating
    status = "FAIL"
    if best and best["name"] == "pi_alpha_inv_sq_qed" and rel_err_pi <= match_eps_pass and robust_ok_pi:
        status = "PASS"
    elif best and best["name"] == "pi_alpha_inv_sq_two_loop_qed" and rel_err_two_loop <= match_eps_pass and robust_ok_two_loop:
        status = "PASS"
    elif best and best["name"] in ("pi_alpha_inv_sq_qed", "pi_alpha_inv_sq_two_loop_qed") and float(best["rel_err"]) <= match_eps_warn:
        status = "WARN"

    message = (
        "PASS indicates a stable numerical correspondence under declared model assumptions; "
        "it does not establish mechanism."
    )

    # Sweeps
    h0_values = _frange(h0_min, h0_max, h0_step)
    omega_values = _frange(omegaL_min, omegaL_max, omegaL_step)
    tau_values = _frange(tau0_myr * (1.0 - tau_frac), tau0_myr * (1.0 + tau_frac), max(tau0_myr * tau_frac / 5.0, 1e-6))

    two_loop_argmin: Dict[str, float] = {}
    rel_err_vs_H0: List[Dict[str, float]] = []
    best_err = float("inf")
    best_h0 = None
    best_omega = None

    for h0 in h0_values:
        best_err_for_h0 = float("inf")
        best_omega_for_h0 = None
        for omega in omega_values:
            _, _, R_sweep, _, _, _ = _compute_R(tau0_myr, h0, Omega_m, omega)
            err = abs(R_sweep - cand_pi_alpha_inv_sq_two_loop_val) / R_sweep if cand_pi_alpha_inv_sq_two_loop_val > 0 else float("nan")
            if err < best_err_for_h0:
                best_err_for_h0 = err
                best_omega_for_h0 = omega
            if err < best_err:
                best_err = err
                best_h0 = h0
                best_omega = omega
        if best_err_for_h0 < float("inf"):
            rel_err_vs_H0.append({"H0": h0, "rel_err": best_err_for_h0})

    if best_h0 is None or best_omega is None:
        fallback_err = rel_err_two_loop
        two_loop_argmin = {"H0": float(H0_km_s_Mpc), "Omega_L": float(omega_l), "rel_err": float(fallback_err)}
        rel_err_vs_H0 = [{"H0": float(H0_km_s_Mpc), "rel_err": float(fallback_err)}]
    else:
        two_loop_argmin = {"H0": float(best_h0), "Omega_L": float(best_omega), "rel_err": float(best_err)}

    robustness = {
        "baseline_rel_err_pi_alpha_inv_sq_qed": rel_err_pi,
        "baseline_rel_err_pi_alpha_inv_sq_two_loop_qed": rel_err_two_loop,
        "rel_err_h0_minus": rel_err_h0_minus,
        "rel_err_h0_plus": rel_err_h0_plus,
        "rel_err_omega_minus": rel_err_om_minus,
        "rel_err_omega_plus": rel_err_om_plus,
        "rel_err_two_loop_h0_minus": rel_err_two_loop_h0_minus,
        "rel_err_two_loop_h0_plus": rel_err_two_loop_h0_plus,
        "rel_err_two_loop_omega_minus": rel_err_two_loop_om_minus,
        "rel_err_two_loop_omega_plus": rel_err_two_loop_om_plus,
        "match_eps_pass": match_eps_pass,
        "match_eps_warn": match_eps_warn,
        "h0_sweep": _sweep("H0", h0_values, tau0_myr, H0_km_s_Mpc, Omega_m, omega_l, cand_pi_alpha_inv_sq_val, cand_pi_alpha_inv_sq_two_loop_val, candidates),
        "omega_lambda_sweep": _sweep("Omega_lambda", omega_values, tau0_myr, H0_km_s_Mpc, Omega_m, omega_l, cand_pi_alpha_inv_sq_val, cand_pi_alpha_inv_sq_two_loop_val, candidates),
        "tau0_sweep": _sweep("tau0_myr", tau_values, tau0_myr, H0_km_s_Mpc, Omega_m, omega_l, cand_pi_alpha_inv_sq_val, cand_pi_alpha_inv_sq_two_loop_val, candidates),
    }

    tau0_s = tau0_myr * SEC_PER_MYR
    H0_si = _h0_to_si(H0_km_s_Mpc)
    tau_lambda_s = 1.0 / H0_si
    tau_lambda_gyr = tau_lambda_s / (SEC_PER_YEAR * 1e9)
    tau0_expected_s = tau_lambda_s / SCREENING_S
    tau0_expected_myr = tau0_expected_s / SEC_PER_MYR
    rel_err_tau0_expected = abs(tau0_myr - tau0_expected_myr) / tau0_myr
    ratio_expected_canon = (SCREENING_S ** 2) / (3.0 * omega_l)
    rel_err_ratio_canon = abs(R - ratio_expected_canon) / R

    certificate = {
        "name": "CASIMIR_CERT",
        "status": status,
        "message": message,
        "assumptions": {
            "tau0_myr": tau0_myr,
            "H0_km_s_Mpc": H0_km_s_Mpc,
            "Omega_m": Omega_m,
            "Omega_lambda": omega_l,
            "match_eps_pass": match_eps_pass,
            "match_eps_warn": match_eps_warn,
            "alpha_vac": ALPHA_VAC,
            "screening_S": SCREENING_S,
        },
    }

    return {
        "status": status,
        "computed": {
            "rho_lambda": rho_lambda,
            "rho_req": rho_req,
            "R": R,
            "sqrtR": sqrtR,
            "tau_lambda_gyr": tau_lambda_gyr,
            "tau_lambda_s": tau_lambda_s,
            "tau0_expected_myr": tau0_expected_myr,
            "rel_err_tau0_expected": rel_err_tau0_expected,
            "ratio_expected_canon": ratio_expected_canon,
            "rel_err_ratio_canon": rel_err_ratio_canon,
        },
        "best_candidate": {
            "name": best["name"] if best else "",
            "label": best["label"] if best else "",
            "value": best["value"] if best else 0.0,
            "rel_err": best["rel_err"] if best else float("nan"),
            "rel_err_sqrt": best["rel_err_sqrt"] if best else float("nan"),
        },
        "candidates": candidate_table,
        "two_loop_argmin": two_loop_argmin,
        "rel_err_vs_H0_marginalized": rel_err_vs_H0,
        "baseline_note": "H0 is baseline-defined (tau_Lambda = H0^{-1}). Any inversion tau_Lambda = tau0 * S is a consistency check only; this run does not derive H0.",
        "robustness": robustness,
        "certificate": certificate,
        "constants": {
            "G": G,
            "c": c,
            "SEC_PER_YEAR": SEC_PER_YEAR,
            "SEC_PER_MYR": SEC_PER_MYR,
            "ALPHA_QED_INV": ALPHA_QED_INV,
            "ALPHA_QED": ALPHA_QED,
            "ALPHA_VAC": ALPHA_VAC,
            "SCREENING_S": SCREENING_S,
            "N_G0_SQ": N_G0_SQ,
            "N_G0": N_G0,
            "PI": PI,
            "mu_lambda": HBAR_J_S / tau_lambda_s,
            "mu_0": HBAR_J_S / tau0_s,
        },
    }
