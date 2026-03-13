from __future__ import annotations

from dataclasses import dataclass


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))


@dataclass(frozen=True)
class InfoDensityConfig:
    I_base: float = 1.0
    eta: float = 1.0
    eps_min_s: float = 1.0  # safety floor in seconds
    I_max: float = 5.0      # policy cap


def compute_I_value(deltaS: float, eps_user_s: float, cfg: InfoDensityConfig) -> dict:
    eps_eff = max(float(eps_user_s), float(cfg.eps_min_s))
    I = cfg.I_base * (1.0 + cfg.eta * (float(deltaS) / eps_eff))
    I = clamp(I, 1.0, cfg.I_max)
    return {
        "I_base": float(cfg.I_base),
        "eta": float(cfg.eta),
        "eps_user_s": float(eps_user_s),
        "eps_eff_s": float(eps_eff),
        "deltaS": float(deltaS),
        "I_value": float(I),
        "I_max": float(cfg.I_max),
    }
