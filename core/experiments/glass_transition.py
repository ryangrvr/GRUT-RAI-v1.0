"""Cosmological Deborah Sweep (Glass Transition Hypothesis).

Finds redshift where De = tau0 / age(z) crosses ~1 and reports argmin.
Reports numerical correspondence only (no mechanistic claims).
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

import numpy as np

MPC_M = 3.085677581e22
SEC_PER_YEAR = 31557600.0
SEC_PER_MYR = SEC_PER_YEAR * 1_000_000.0


def _E(z: np.ndarray, Omega_m: float, Omega_lambda: float, Omega_r: float) -> np.ndarray:
    return np.sqrt(Omega_r * (1.0 + z) ** 4 + Omega_m * (1.0 + z) ** 3 + Omega_lambda)


def _age_myr_grid(
    z_grid: np.ndarray,
    H0_km_s_Mpc: float,
    Omega_m: float,
    Omega_lambda: float,
    Omega_r: float,
) -> np.ndarray:
    H0_si = (H0_km_s_Mpc * 1000.0) / MPC_M
    f = 1.0 / ((1.0 + z_grid) * _E(z_grid, Omega_m, Omega_lambda, Omega_r))
    dz = np.diff(z_grid)
    f_mid = 0.5 * (f[:-1] + f[1:])
    cum = np.concatenate(([0.0], np.cumsum(f_mid * dz)))
    total = float(cum[-1])
    integral_from_z = total - cum
    age_s = (1.0 / H0_si) * integral_from_z
    return age_s / SEC_PER_MYR


def run_experiment(
    tau0_myr: float = 41.9,
    H0_km_s_Mpc: float = 67.36,
    Omega_m: float = 0.315,
    Omega_lambda: float = 0.6847,
    Omega_r: float = 9.24e-5,
    T_cmb_K: float = 2.725,
    z_min: float = 0.0,
    z_max: float = 1.0e4,
    n_samples: int = 500,
    include_scan_data: bool = False,
    scan_max_points: int = 200,
    pass_z_min: float = 10.0,
    pass_z_max: float = 100.0,
    warn_z_max: float = 1100.0,
) -> Dict[str, Any]:
    z_min_eff = max(z_min, 0.0)
    z_max_eff = max(z_max, z_min_eff + 1e-6)
    z_grid = np.logspace(np.log10(1.0 + z_min_eff), np.log10(1.0 + z_max_eff), int(n_samples)) - 1.0

    ages_myr = _age_myr_grid(z_grid, H0_km_s_Mpc, Omega_m, Omega_lambda, Omega_r)
    ages_myr = np.maximum(ages_myr, 1e-12)
    De = tau0_myr / ages_myr

    idx = int(np.argmin(np.abs(De - 1.0)))
    z_crit = float(z_grid[idx])
    t_crit = float(ages_myr[idx])
    T_crit = float(T_cmb_K * (1.0 + z_crit))
    De_crit = float(De[idx])

    status = "FAIL"
    if pass_z_min <= z_crit <= pass_z_max:
        status = "PASS"
    elif z_crit <= warn_z_max:
        status = "WARN"

    message = (
        "PASS indicates De≈1 occurs within the preregistered redshift band; "
        "this is a numerical correspondence only."
    )

    scan_points = None
    if include_scan_data:
        count = min(len(z_grid), int(scan_max_points))
        idxs = np.linspace(0, len(z_grid) - 1, num=count, dtype=int)
        scan_points = [
            {
                "z": float(z_grid[i]),
                "age_myr": float(ages_myr[i]),
                "T_K": float(T_cmb_K * (1.0 + z_grid[i])),
                "De": float(De[i]),
            }
            for i in idxs
        ]

    return {
        "status": status,
        "crossing": {
            "z_crit": z_crit,
            "age_myr": t_crit,
            "T_K": T_crit,
            "De": De_crit,
        },
        "scan_points": scan_points,
        "certificate": {
            "name": "GLASS_TRANSITION_CERT",
            "status": status,
            "message": message,
            "assumptions": {
                "tau0_myr": tau0_myr,
                "H0_km_s_Mpc": H0_km_s_Mpc,
                "Omega_m": Omega_m,
                "Omega_lambda": Omega_lambda,
                "Omega_r": Omega_r,
                "T_cmb_K": T_cmb_K,
                "z_min": z_min,
                "z_max": z_max,
                "n_samples": n_samples,
                "pass_z_min": pass_z_min,
                "pass_z_max": pass_z_max,
                "warn_z_max": warn_z_max,
            },
        },
        "constants": {
            "MPC_M": MPC_M,
            "SEC_PER_MYR": SEC_PER_MYR,
        },
    }
