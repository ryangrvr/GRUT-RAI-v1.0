from __future__ import annotations

import numpy as np
from .constants import GRUTParams

def tau_eff_seconds(params: GRUTParams, z: np.ndarray, Hz: np.ndarray, H0: float, TAU_FACTOR: float, p: float) -> np.ndarray:
    """Canonical implementation: tau_eff(z) = tau0 * TAU_FACTOR * (H0/H(z))^p."""
    ratio = np.clip(H0 / np.clip(Hz, 1e-30, 1e30), 1e-12, 1e12)
    return params.tau0_seconds * TAU_FACTOR * (ratio ** p)

def S_phase(z: np.ndarray, x0: float, w: float) -> np.ndarray:
    """Sigmoid regime bridge centered at x0 in x=ln(1+z)."""
    x = np.log1p(np.clip(z, 0.0, 1e12))
    w_safe = max(float(w), 1e-9)
    return 1.0 / (1.0 + np.exp((x - float(x0)) / w_safe))

def L_stiff(chi: np.ndarray, g_max: float, sigma: float) -> np.ndarray:
    """Rational soft-cap approaching g_max as chi grows."""
    return 1.0 + ((g_max - 1.0) * chi) / (chi + max(float(sigma), 1e-12))

def smooth_min(a: np.ndarray, b: np.ndarray, k: float = 24.0) -> np.ndarray:
    """Smooth approximation of min(a,b) that preserves derivatives."""
    k = float(k)
    return -(1.0 / k) * np.log(np.exp(-k * a) + np.exp(-k * b))

def phi_z(z: np.ndarray, mode: str, s_phase: np.ndarray | None = None) -> np.ndarray:
    """Epoch-dependent damping term Phi(z). V1 supports:
    - unity: Phi=1
    - phase_weighted: Phi = 0.5 + 0.5*S_phase(z) (more dissipation near saturated regime)
    """
    mode = (mode or "unity").lower()
    if mode == "unity":
        return np.ones_like(z, dtype=float)
    if mode == "phase_weighted":
        if s_phase is None:
            raise ValueError("phase_weighted Phi(z) requires S_phase")
        return 0.5 + 0.5 * np.clip(s_phase, 0.0, 1.0)
    raise ValueError(f"Unsupported phi_mode: {mode}")
