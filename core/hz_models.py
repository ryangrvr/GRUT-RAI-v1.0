from __future__ import annotations

import numpy as np

# SI conversions
MPC_IN_M = 3.0856775814913673e22

def H0_SI(H0_km_s_Mpc: float) -> float:
    return (H0_km_s_Mpc * 1000.0) / MPC_IN_M

def hz_lcdm_flat(z: np.ndarray, H0_km_s_Mpc: float, Omega_m: float, Omega_lambda: float) -> np.ndarray:
    """Flat LCDM H(z) in SI units (1/s)."""
    H0 = H0_SI(H0_km_s_Mpc)
    return H0 * np.sqrt(Omega_m * (1.0 + z) ** 3 + Omega_lambda)

def omega_m_z(z: np.ndarray, Omega_m0: float, Omega_lambda0: float) -> np.ndarray:
    """Matter fraction Omega_m(z) for flat LCDM (no radiation)."""
    Ez2 = Omega_m0 * (1.0 + z) ** 3 + Omega_lambda0
    return (Omega_m0 * (1.0 + z) ** 3) / np.clip(Ez2, 1e-30, 1e30)
