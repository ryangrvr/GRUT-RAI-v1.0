from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

import numpy as np


def emd_1d(a: np.ndarray, b: np.ndarray, *, dx: float = 1.0) -> float:
    """Compute a signal-safe 1D Earth Mover's Distance (Wasserstein-1).

    This treats inputs as nonnegative 'mass' (absolute values), normalizes
    each to unit mass (when possible), and computes the EMD between CDFs.
    Returns the normalized EMD (bounded and comparable across signals).

    If one of the signals has essentially zero mass (near numerical zero),
    we return a bounded penalty (1.0) and let the caller annotate a
    mass-warning rather than returning an astronomical constant.
    """
    a = np.asarray(a, dtype=float).reshape(-1)
    b = np.asarray(b, dtype=float).reshape(-1)
    if a.size != b.size:
        raise ValueError("a and b must have same length")

    # absolute mass
    a = np.maximum(np.abs(a), 0.0)
    b = np.maximum(np.abs(b), 0.0)

    sa = float(np.sum(a))
    sb = float(np.sum(b))

    eps = 1e-12
    if sa == 0.0 and sb == 0.0:
        return 0.0

    # If either mass is near-zero (but not both zero), return bounded penalty
    if sa < eps or sb < eps:
        return 1.0

    a_norm = a / sa
    b_norm = b / sb

    cdfa = np.cumsum(a_norm)
    cdfb = np.cumsum(b_norm)
    return float(np.sum(np.abs(cdfa - cdfb)) * dx)

def emd_with_mass_ratio(a: np.ndarray, b: np.ndarray, *, dx: float = 1.0) -> Tuple[float, float, float]:
    """Compute normalized EMD plus a mass-ratio penalty.

    Returns (emd_norm, mass_ratio, emd_penalized), where mass_ratio is
    min(total_a,total_b)/max(total_a,total_b) and emd_penalized =
    emd_norm + (1 - mass_ratio).

    Behaves safely when one signal has near-zero mass.
    """
    a = np.asarray(a, dtype=float).reshape(-1)
    b = np.asarray(b, dtype=float).reshape(-1)
    if a.size != b.size:
        raise ValueError("a and b must have same length")

    a = np.maximum(np.abs(a), 0.0)
    b = np.maximum(np.abs(b), 0.0)

    sa = float(np.sum(a))
    sb = float(np.sum(b))

    eps = 1e-12
    if sa == 0.0 and sb == 0.0:
        return 0.0, 1.0, 0.0

    # If either mass is near-zero (but not both zero), return bounded penalty
    if sa < eps or sb < eps:
        return 1.0, 0.0, 1.0

    emd_norm = emd_1d(a, b, dx=dx)

    mass_ratio = min(sa, sb) / max(sa, sb)

    emd_penalized = emd_norm + (1.0 - mass_ratio)
    return float(emd_norm), float(mass_ratio), float(emd_penalized)
@dataclass
class RISReport:
    """Reconstruction Integrity Standard (RIS) certificate."""

    status: str
    emd: float
    residual_norm: float
    converged: bool
    iters: int
    lam: float
    notes: Dict[str, float]
    warnings: list[str]
    message: str
    recovery: Optional[Dict[str, float]] = None


def build_ris_report(
    *,
    emd: float,
    residual_norm: float,
    converged: bool,
    iters: int,
    lam: float,
    emd_warn: float = 0.15,
    emd_fail: float = 0.35,
    mass_ratio: Optional[float] = None,
    spike_recovery: Optional[Dict[str, float]] = None,
) -> RISReport:
    warnings: list[str] = []

    # Sanity gate: if not converged, immediate FAIL
    if not converged:
        status = "FAIL"
        warnings.append("LCA did not converge within the configured iterations")

        notes = {"emd_warn": float(emd_warn), "emd_fail": float(emd_fail)}
        message = "; ".join(warnings)
        return RISReport(
            status=status,
            emd=float(emd),
            residual_norm=float(residual_norm),
            converged=bool(converged),
            iters=int(iters),
            lam=float(lam),
            notes=notes,
            warnings=warnings,
            message=message,
            recovery=spike_recovery,
        )

    # Primary criterion: penalized EMD (assumed passed in as 'emd')
    # Secondary: spike recovery sanity gate (if provided)
    if spike_recovery is not None:
        injected = int(spike_recovery.get("injected_count", 0))
        recovered = int(spike_recovery.get("recovered_topk_count", 0))
        if injected > 0:
            recall = float(recovered) / float(injected) if injected > 0 else 0.0
            # If less than half of spikes recovered, fail the demo as a sanity check
            if recall < 0.5:
                status = "FAIL"
                warnings.append("Spike recovery below sanity threshold")

    if not warnings:
        if emd >= emd_fail:
            status = "FAIL"
            warnings.append("EMD exceeds failure threshold")
        elif emd >= emd_warn:
            status = "WARN"
            warnings.append("EMD exceeds warning threshold")
        else:
            status = "PASS"

    notes = {
        "emd_warn": float(emd_warn),
        "emd_fail": float(emd_fail),
    }

    if mass_ratio is not None:
        notes["mass_ratio"] = float(mass_ratio)

    message = "; ".join(warnings) if warnings else "OK"

    return RISReport(
        status=status,
        emd=float(emd),
        residual_norm=float(residual_norm),
        converged=bool(converged),
        iters=int(iters),
        lam=float(lam),
        notes=notes,
        warnings=warnings,
        message=message,
        recovery=spike_recovery,
    )


def search_tau_grid(
    observed_y: np.ndarray,
    candidate_tau_s: Iterable[float],
    *,
    forward_fn,
    reconstruct_fn,
    dx: float = 1.0,
) -> Tuple[float, Dict[str, float]]:
    """Simple grid search over tau candidates.

    Parameters
    ----------
    observed_y:
        The observed shadow signal.
    candidate_tau_s:
        Candidate tau values to test.
    forward_fn:
        Callable(tau_s)->(A, meta) that returns the forward model matrix.
    reconstruct_fn:
        Callable(A)->x_hat that reconstructs the source from observed_y.

    Returns
    -------
    best_tau_s, diagnostics
    """
    observed_y = np.asarray(observed_y, dtype=float).reshape(-1)

    best_tau = None
    best_score = np.inf

    scores: list[float] = []
    taus: list[float] = []

    for tau in candidate_tau_s:
        A, _meta = forward_fn(float(tau))
        x_hat, residual_norm, converged, iters, lam = reconstruct_fn(A)
        y_hat_override = None
        if hasattr(res, "diagnostics") and isinstance(res.diagnostics, dict):
            y_hat_override = res.diagnostics.get("y_hat_override") or res.diagnostics.get("y_hat")

        if y_hat_override is not None:
            y_hat = np.asarray(y_hat_override, dtype=float).reshape(-1)
        else:
            y_hat = A @ x_hat
        score = emd_1d(observed_y, y_hat, dx=dx)
        scores.append(float(score))
        taus.append(float(tau))
        if score < best_score:
            best_score = score
            best_tau = float(tau)

    if best_tau is None:
        raise ValueError("No candidates provided")

    return best_tau, {"best_emd": float(best_score), "scores": scores, "taus": taus}


def search_tau_with_ris(
    observed_y: np.ndarray,
    candidate_tau_s: Iterable[float],
    *,
    forward_fn,
    reconstruct_fn,
    dx: float = 1.0,
    emd_warn: float = 2.0,
    emd_fail: float = 5.0,
    residual_warn: float = 0.10,
    residual_fail: float = 0.25,
    debug_trace: bool = False,
) -> Tuple[Optional[int], list[Dict[str, float]], Dict[str, str]]:
    """Grid search with RIS gating: only admissible candidates (PASS/WARN) are considered.

    Enhanced diagnostics per-candidate are emitted (max_abs_x, nnz_x,
    objective_first/last, residual_first/last, iters, converged). If
    `debug_trace` is True, the first 10 entries of `iter_trace` (if present)
    will be included in each candidate's dict.
    """
    observed_y = np.asarray(observed_y, dtype=float).reshape(-1)

    scores: list[Dict[str, float]] = []
    admissible_idxs: list[int] = []

    eps_mass = 1e-12

    for idx, tau in enumerate(candidate_tau_s):
        A, _meta = forward_fn(float(tau))
        # Support reconstruct_fn that accepts (A, meta) or just (A)
        try:
            res = reconstruct_fn(A, _meta)
        except TypeError:
            res = reconstruct_fn(A)

        # Normalize return types: accept LCAResult-like or tuple
        if hasattr(res, "x_hat"):
            x_hat = np.asarray(res.x_hat, dtype=float).reshape(-1)
            residual_norm = float(res.residual_norm)
            converged = bool(res.converged)
            iters = int(res.iters)
            lam = float(res.diagnostics.get("lam", res.diagnostics.get("lam_smooth", 0.0)))
            trace = res.diagnostics.get("trace", [])
            iter_trace = res.diagnostics.get("iter_trace", [])
            objective_val = float(getattr(res, "objective", 0.0))
        else:
            # tuple: x_hat, residual_norm, converged, iters, lam
            x_hat, residual_norm, converged, iters, lam = res
            x_hat = np.asarray(x_hat, dtype=float).reshape(-1)
            trace = []
            iter_trace = []
            objective_val = 0.5 * (residual_norm ** 2) + float(lam) * float(np.sum(np.abs(x_hat)))

        y_hat = A @ x_hat

        sa = float(np.sum(np.abs(observed_y)))
        sb = float(np.sum(np.abs(y_hat)))

        emd_mass_warning = False
        if (sa < eps_mass and sb < eps_mass):
            emd_shadow = 0.0
        elif sa < eps_mass or sb < eps_mass:
            emd_mass_warning = True
            emd_shadow = 1.0
        else:
            # Use normalized spacing (1/len) to keep EMD magnitude stable across resample lengths
            dx_norm = 1.0 / max(float(observed_y.size), 1.0)
            emd_shadow = emd_1d(observed_y, y_hat, dx=dx_norm)

        # Objective: EMD + 0.25 * residual
        objective = float(emd_shadow) + 0.25 * float(residual_norm)

        # RIS status for this tau
        if not converged:
            ris_status = "FAIL"
        elif emd_shadow >= emd_fail or residual_norm >= residual_fail:
            ris_status = "FAIL"
        elif emd_shadow >= emd_warn or residual_norm >= residual_warn:
            ris_status = "WARN"
        else:
            ris_status = "PASS"

        # Per-candidate diagnostics
        max_abs_x = float(np.max(np.abs(x_hat))) if x_hat.size > 0 else 0.0
        nnz_x = int(np.sum(np.abs(x_hat) > 1e-12)) if x_hat.size > 0 else 0

        objective_first = None
        objective_last = None
        residual_first = None
        residual_last = None

        if trace and isinstance(trace, list) and len(trace) > 0:
            objective_first = float(trace[0].get("objective", objective_val))
            objective_last = float(trace[-1].get("objective", objective_val))
            residual_first = float(trace[0].get("residual", 0.0))
            residual_last = float(trace[-1].get("residual", residual_norm))
        elif iter_trace and isinstance(iter_trace, list) and len(iter_trace) > 0:
            objective_first = float(iter_trace[0].get("obj", objective_val))
            objective_last = float(iter_trace[-1].get("obj", objective_val))
            residual_first = float(iter_trace[0].get("res_norm", 0.0))
            residual_last = float(iter_trace[-1].get("res_norm", residual_norm))
        else:
            objective_first = float(objective_val)
            objective_last = float(objective_val)
            residual_first = float(residual_norm)
            residual_last = float(residual_norm)

        entry = {
            "tau_s": float(tau),
            "emd_shadow": float(emd_shadow),
            "residual_norm": float(residual_norm),
            "objective": float(objective),
            "ris_status": ris_status,
            "converged": bool(converged),
            "iters": int(iters),
            "max_abs_x": float(max_abs_x),
            "nnz_x": int(nnz_x),
            "objective_first": float(objective_first),
            "objective_last": float(objective_last),
            "residual_first": float(residual_first),
            "residual_last": float(residual_last),
            "emd_mass_warning": bool(emd_mass_warning),
            "y_hat": list(map(float, y_hat.tolist())),
        }

        if debug_trace:
            entry["iter_trace"] = list(iter_trace)[:10]

        scores.append(entry)

        if ris_status in ("PASS", "WARN"):
            admissible_idxs.append(idx)

    # Choose best among admissible by objective
    if admissible_idxs:
        best_idx = min(admissible_idxs, key=lambda i: scores[i]["objective"])
        ris_summary = {
            "status": "PASS",
            "message": f"Found best tau at index {best_idx}",
            "best_tau_s": float(scores[best_idx]["tau_s"]),
        }
        return best_idx, scores, ris_summary
    else:
        ris_summary = {
            "status": "FAIL",
            "message": "No tau candidate achieved RIS_WARN; widen range / lower lam / increase n_kernel",
            "best_tau_s": None,
        }
        return None, scores, ris_summary