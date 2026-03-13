from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def find_z0_index(z_values: Iterable[float]) -> Optional[int]:
    z_list = list(z_values)
    if not z_list:
        return None
    best_idx = 0
    best_val = abs(z_list[0])
    for i, z in enumerate(z_list[1:], start=1):
        val = abs(z)
        if val < best_val:
            best_val = val
            best_idx = i
    return best_idx


def compute_Ez(H_code: Iterable[float], idx0: int) -> List[float]:
    H_list = list(H_code)
    if idx0 is None or idx0 < 0 or idx0 >= len(H_list):
        raise ValueError("idx0 out of range for H_code")
    H0_code = H_list[idx0]
    if H0_code == 0:
        raise ValueError("H0_code is zero; cannot compute E(z)")
    return [h / H0_code for h in H_list]


def build_policy(H0_km_s_Mpc: float, H0_code: float, meta: Dict[str, Any]) -> Dict[str, Any]:
    if H0_code == 0:
        raise ValueError("H0_code is zero; cannot build scale policy")
    scale_H = H0_km_s_Mpc / H0_code
    return {
        "H0_km_s_Mpc": H0_km_s_Mpc,
        "H0_code": H0_code,
        "scale_H": scale_H,
        "meta": dict(meta),
    }


def convert_H(H_code: Iterable[float], scale_H: float) -> List[float]:
    return [h * scale_H for h in H_code]


def years_to_gyr(years: float) -> float:
    return years / 1e9
