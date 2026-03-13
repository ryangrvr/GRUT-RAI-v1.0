"""Baseline models for comparison (MVP).

Provides simple LCDM proxy baseline for GRUT f_sigma8 and a "tau0" no-memory
baseline for Anamnesis (delta kernel).
"""
from typing import Dict, Any, Optional
import numpy as np


def grut_f_sigma8_baseline(engine_out: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return baseline and grut f_sigma8 arrays if present in engine outputs.

    Returns None if growth proxy not enabled or arrays missing.
    """
    base = engine_out.get("f_sigma8_base")
    grut = engine_out.get("f_sigma8_grut")
    if base is None or grut is None:
        return None
    return {
        "name": "lcdm_proxy",
        "f_sigma8": list(base),
        "grut": list(grut),
    }


def anamnesis_tau0_baseline(y_obs: np.ndarray, reconstruct_fn, dx: float = 1.0, **kwargs) -> Dict[str, Any]:
    """Compute baseline candidate for anamnesis representing no-memory (delta kernel).

    reconstruct_fn: callable(A)->LCAResult or tuple. We support both signatures
    (reconstruct_fn(A) or reconstruct_fn(A, meta)). Returns dict conforming
    to score entries.
    """
    n = y_obs.size
    # Identity forward operator: kernel [1.0]
    A = np.eye(n, dtype=float)
    try:
        res = reconstruct_fn(A)
    except TypeError:
        res = reconstruct_fn(A, {})

    if hasattr(res, "x_hat"):
        x_hat = np.asarray(res.x_hat, dtype=float).reshape(-1)
        residual_norm = float(res.residual_norm)
        converged = bool(res.converged)
        iters = int(res.iters)
    else:
        x_hat, residual_norm, converged, iters, lam = res

    y_hat = A @ x_hat

    # EMD computed by caller; here we return reconstructed and diagnostics
    return {
        "tau_s": 0.0,
        "label": "tau0_baseline",
        "y_hat": list(y_hat),
        "residual_norm": float(residual_norm),
        "converged": bool(converged),
        "iters": int(iters),
    }
