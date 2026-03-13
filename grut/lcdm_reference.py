from __future__ import annotations

import math
from typing import Iterable, List


def Ez_lcdm(
    z: float,
    Omega_m: float,
    Omega_L: float,
    Omega_r: float = 0.0,
    Omega_k: float = 0.0,
) -> float:
    return math.sqrt(
        (Omega_m * ((1.0 + z) ** 3))
        + (Omega_r * ((1.0 + z) ** 4))
        + (Omega_k * ((1.0 + z) ** 2))
        + Omega_L
    )


def Ez_lcdm_series(
    z_values: Iterable[float],
    Omega_m: float,
    Omega_L: float,
    Omega_r: float = 0.0,
    Omega_k: float = 0.0,
) -> List[float]:
    return [Ez_lcdm(z, Omega_m, Omega_L, Omega_r=Omega_r, Omega_k=Omega_k) for z in z_values]
