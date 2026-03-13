"""Real data adapter: mapping z -> lookback time and resampling utilities.

Implements LCDM H(z) and lookback time integrand using trapezoid integration
and lightweight resampling with np.interp. Returns times in Gyr by default.
"""
from __future__ import annotations

from typing import Tuple, Iterable
import json
import hashlib

import numpy as np

# Physical conversions
SEC_PER_YEAR = 31557600.0
SEC_PER_MYR = SEC_PER_YEAR * 1_000_000.0
SEC_PER_GYR = SEC_PER_YEAR * 1_000_000_000.0
_MPC_IN_M = 3.085677581491367e22


def hz_lcdm(z: Iterable[float], H0_km_s_Mpc: float = 67.4, Omega_m: float = 0.315, Omega_lambda: float = 0.685) -> np.ndarray:
    """Return H(z) in same units as H0 (km/s/Mpc).

    E(z) = sqrt(Om(1+z)^3 + Ol) for flat LCDM; H(z) = H0 * E(z).
    """
    z = np.asarray(z, dtype=float)
    Ez = np.sqrt(Omega_m * (1.0 + z) ** 3 + Omega_lambda)
    return float(H0_km_s_Mpc) * Ez


def lookback_time_gyr(z_array: Iterable[float], H0_km_s_Mpc: float = 67.4, Omega_m: float = 0.315, Omega_lambda: float = 0.685) -> Tuple[np.ndarray, dict]:
    """Compute lookback time t_L(z) in Gyr for input z_array.

    Uses the integrand 1/((1+z) H(z)) and a cumulative trapezoid rule.
    Returns sorted t_gyr corresponding to sorted z and a diagnostic dict.
    """
    z = np.asarray(z_array, dtype=float).reshape(-1)
    if z.size == 0:
        return np.asarray([]), {"min_z": None, "max_z": None}

    # Sort by z (ascending) to ensure monotonic integrand
    order = np.argsort(z)
    z_sorted = z[order]

    # Build a fine grid if needed: here we'll integrate on the input z grid
    # and rely on trapezoid rule being adequate for instrument-only adapter.
    # Compute E(z)
    Ez = np.sqrt(Omega_m * (1.0 + z_sorted) ** 3 + Omega_lambda)

    # H0 in s^-1
    H0_s = float(H0_km_s_Mpc) * 1000.0 / _MPC_IN_M
    # H0 in Gyr^-1
    H0_gyr = H0_s * SEC_PER_GYR

    integrand = 1.0 / ((1.0 + z_sorted) * Ez)

    # cumulative integral using trapezoid rule: cumsum of area segments
    # area segments between z[i] and z[i+1] = 0.5*(f[i]+f[i+1])*(dz)
    dz = np.diff(z_sorted)
    # if only a single point, integral is zero at z=0 (but if z>0 with single point, treat as area zero)
    if dz.size == 0:
        cum = np.zeros_like(z_sorted)
    else:
        seg = 0.5 * (integrand[:-1] + integrand[1:]) * dz
        cum = np.concatenate(([0.0], np.cumsum(seg)))

    # Multiply by 1/H0 and convert to Gyr: t (Gyr) = (1/H0_gyr) * cum
    t_gyr = cum / H0_gyr

    diag = {
        "min_z": float(np.min(z_sorted)),
        "max_z": float(np.max(z_sorted)),
        "H0_km_s_Mpc": float(H0_km_s_Mpc),
        "Omega_m": float(Omega_m),
        "Omega_lambda": float(Omega_lambda),
    }

    # Return times in the original z order
    t_out = np.empty_like(t_gyr)
    t_out[order] = t_gyr

    return t_out, diag


def resample_uniform(t_gyr: Iterable[float], y: Iterable[float], dt_gyr: float) -> Tuple[np.ndarray, np.ndarray]:
    """Resample (t_gyr, y) to a uniform grid with spacing dt_gyr (in Gyr).

    Returns (t_uniform_gyr, y_resampled).
    Linear interpolation is used (np.interp). Extrapolation is disabled.
    """
    t = np.asarray(t_gyr, dtype=float).reshape(-1)
    y = np.asarray(y, dtype=float).reshape(-1)
    if t.size != y.size:
        raise ValueError("t and y must have same length")
    if t.size == 0:
        return np.asarray([]), np.asarray([])

    # Sort by t
    order = np.argsort(t)
    t_sorted = t[order]
    y_sorted = y[order]

    t_min = float(t_sorted[0])
    t_max = float(t_sorted[-1])

    if dt_gyr <= 0:
        raise ValueError("dt_gyr must be > 0")

    n = int(max(2, np.floor((t_max - t_min) / float(dt_gyr)) + 1))
    t_uniform = t_min + np.arange(n) * float(dt_gyr)
    # Ensure last point equals t_max
    if t_uniform[-1] < t_max:
        t_uniform = np.append(t_uniform, t_max)

    y_uniform = np.interp(t_uniform, t_sorted, y_sorted)
    return t_uniform, y_uniform


def myr_to_s(myr: float) -> float:
    return float(myr) * SEC_PER_MYR


def gyr_to_s(gyr: float) -> float:
    return float(gyr) * SEC_PER_GYR


def s_to_myr(sec: float) -> float:
    return float(sec) / SEC_PER_MYR


def gyr_to_myr(gyr: float) -> float:
    return float(gyr) * 1000.0


def canonical_dataset_hash(z, fs8, sigma, cosmo_params) -> str:
    # Build a canonical JSON and hash it
    payload = {
        "z": list(map(float, z)),
        "fsigma8": list(map(float, fs8)),
        "sigma": (list(map(float, sigma)) if sigma is not None else None),
        "cosmo": {"H0_km_s_Mpc": float(cosmo_params.get('H0_km_s_Mpc', 67.4)), "Omega_m": float(cosmo_params.get('Omega_m', 0.315))},
    }
    s = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
