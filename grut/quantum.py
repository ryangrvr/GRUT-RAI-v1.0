from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

import numpy as np

G_SI = 6.674e-11
HBAR_SI = 1.054571817e-34
PI = math.pi
SEC_PER_YEAR = 365.25 * 24.0 * 3600.0

PRESETS = {
    "optomech_micro": {"m_kg": 1e-9, "l_m": 1e-6, "omega_exp": 1e5},
    "optomech_nano": {"m_kg": 1e-15, "l_m": 1e-7, "omega_exp": 1e6},
    "atom_interfer": {"m_kg": 1e-25, "l_m": 1e-6, "omega_exp": 1e3},
}


class QuantumBoundaryError(ValueError):
    pass


def compute_boundary(
    *,
    m_kg: float,
    l_m: float,
    tau0_s: float,
    omega_policy: str,
    omega_exp: Optional[float],
    alpha_vac: float,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if m_kg <= 0 or l_m <= 0 or tau0_s <= 0:
        raise QuantumBoundaryError("m_kg, l_m, and tau0_s must be positive")
    if alpha_vac <= 0:
        raise QuantumBoundaryError("alpha_vac must be positive")

    omega_policy = omega_policy.lower().strip()
    if omega_policy not in ("controlled", "self_consistent"):
        raise QuantumBoundaryError("omega_policy must be controlled or self_consistent")
    if omega_policy == "controlled" and omega_exp is None:
        raise QuantumBoundaryError("omega_exp is required for controlled policy")

    t_dp = (HBAR_SI * l_m) / (G_SI * (m_kg**2))
    if omega_policy == "controlled":
        x = float(omega_exp) * tau0_s
        alpha_eff = alpha_vac / (1.0 + x * x)
        t_grut = t_dp / alpha_eff
    else:
        x = None
        alpha_eff = None
        t_grut = (((2.0 * PI * tau0_s) ** 2) / alpha_vac * t_dp) ** (1.0 / 3.0)

    enhancement = t_grut / t_dp

    inputs = {
        "m_kg": float(m_kg),
        "l_m": float(l_m),
        "tau0_s": float(tau0_s),
        "omega_exp": None if omega_exp is None else float(omega_exp),
        "omega_policy": omega_policy,
        "alpha_vac": float(alpha_vac),
    }

    outputs = {
        "t_dp_s": float(t_dp),
        "t_grut_s": float(t_grut),
        "enhancement": float(enhancement),
        "X": None if x is None else float(x),
        "alpha_eff": None if alpha_eff is None else float(alpha_eff),
    }

    return inputs, outputs


def compute_scan_rows_omega(
    *,
    m_kg: float,
    l_m: float,
    tau0_s: float,
    alpha_vac: float,
    omega_min: float,
    omega_max: float,
    scan_points: int,
) -> list[dict[str, float]]:
    if scan_points < 2:
        raise QuantumBoundaryError("scan_points must be >= 2")
    if omega_min <= 0 or omega_max <= 0 or omega_max <= omega_min:
        raise QuantumBoundaryError("scan_omega_max must be > scan_omega_min > 0")

    t_dp = (HBAR_SI * l_m) / (G_SI * (m_kg**2))
    step = (omega_max - omega_min) / (scan_points - 1)
    rows: list[dict[str, float]] = []
    for i in range(scan_points):
        omega = omega_min + step * i
        x = omega * tau0_s
        alpha_eff = alpha_vac / (1.0 + x * x)
        t_grut = t_dp / alpha_eff
        enhancement = t_grut / t_dp
        if not math.isfinite(alpha_eff) or alpha_eff <= 0.0:
            raise QuantumBoundaryError("alpha_eff is non-finite or non-positive in scan")
        inv_alpha = 1.0 / alpha_eff
        if not math.isfinite(enhancement) or not math.isfinite(inv_alpha):
            raise QuantumBoundaryError("non-finite enhancement in scan")
        if not math.isclose(enhancement, inv_alpha, rel_tol=1e-10, abs_tol=0.0):
            raise QuantumBoundaryError("enhancement does not match 1/alpha_eff")
        rows.append(
            {
                "omega": float(omega),
                "X": float(x),
                "alpha_eff": float(alpha_eff),
                "t_grut_s": float(t_grut),
                "enhancement": float(enhancement),
            }
        )
    return rows


def compute_scan_rows_mass(
    *,
    m_min: float,
    m_max: float,
    scan_points: int,
    l_m: float,
    tau0_s: float,
    alpha_vac: float,
    omega_policy: str,
    omega_exp: Optional[float],
) -> list[dict[str, float]]:
    if scan_points < 2:
        raise QuantumBoundaryError("scan_points must be >= 2")
    if m_min <= 0 or m_max <= 0 or m_max <= m_min:
        raise QuantumBoundaryError("m_max must be > m_min > 0")

    masses = np.logspace(math.log10(m_min), math.log10(m_max), scan_points)
    rows: list[dict[str, float]] = []
    for m in masses:
        inputs, outputs = compute_boundary(
            m_kg=float(m),
            l_m=l_m,
            tau0_s=tau0_s,
            omega_policy=omega_policy,
            omega_exp=omega_exp,
            alpha_vac=alpha_vac,
        )
        rows.append(
            {
                "m_kg": inputs["m_kg"],
                "t_dp_s": outputs["t_dp_s"],
                "t_grut_s": outputs["t_grut_s"],
                "enhancement": outputs["enhancement"],
                "omega_exp": inputs["omega_exp"],
                "omega_policy": inputs["omega_policy"],
                "alpha_vac": inputs["alpha_vac"],
            }
        )
    return rows


def fit_loglog_slope(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    if x.size < 2:
        raise QuantumBoundaryError("Need at least two points for slope fit")
    if np.any(x <= 0) or np.any(y <= 0):
        raise QuantumBoundaryError("log-log fit requires positive x and y")
    logx = np.log10(x)
    logy = np.log10(y)
    slope, intercept = np.polyfit(logx, logy, 1)
    return float(slope), float(intercept)
