from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))


MetabolicState = Literal["CALM", "STRESS", "PIVOT"]


@dataclass(frozen=True)
class MetabolicConfig:
    fuzz_calm_threshold: float = 0.01
    info_heat_warn: float = 0.10
    pivot_band_threshold: float = 0.25
    cap_engaged_calm_threshold: float = 0.10

    # Tension score weights
    a_ui: float = 0.30
    b_sensor: float = 0.25
    c_fuzz: float = 0.20
    d_cap: float = 0.10
    e_heat: float = 0.15


def classify_state(
    fuzz_fraction: float,
    pivot_intensity: float,
    cap_engaged_frac: float,
    I_heat: float,
    cfg: MetabolicConfig = MetabolicConfig(),
) -> MetabolicState:
    # PIVOT dominates if we are spending a lot of time in the transition band
    if float(pivot_intensity) >= cfg.pivot_band_threshold:
        return "PIVOT"

    # CALM is a strict control-like state
    if (
        float(fuzz_fraction) <= cfg.fuzz_calm_threshold
        and float(I_heat) <= cfg.info_heat_warn
        and float(cap_engaged_frac) <= cfg.cap_engaged_calm_threshold
    ):
        return "CALM"

    return "STRESS"


def compute_tension_score(
    ui_entropy: float,
    sensor_flux: float,
    fuzz_fraction: float,
    cap_engaged_frac: float,
    I_heat: float,
    cfg: MetabolicConfig = MetabolicConfig(),
) -> dict:
    fuzz_term = clamp(float(fuzz_fraction) / max(cfg.fuzz_calm_threshold, 1e-12), 0.0, 1.0)
    T = (
        cfg.a_ui * clamp(ui_entropy, 0.0, 1.0)
        + cfg.b_sensor * clamp(sensor_flux, 0.0, 1.0)
        + cfg.c_fuzz * fuzz_term
        + cfg.d_cap * clamp(cap_engaged_frac, 0.0, 1.0)
        + cfg.e_heat * clamp(I_heat, 0.0, 1.0)
    )
    T = clamp(T, 0.0, 1.0)

    color: str
    if T < 0.33:
        color = "green"
    elif T < 0.66:
        color = "amber"
    else:
        color = "red"

    return {
        "tension_score": float(T),
        "tension_color": color,
        "fuzz_term": float(fuzz_term),
        "weights": {
            "a_ui": cfg.a_ui,
            "b_sensor": cfg.b_sensor,
            "c_fuzz": cfg.c_fuzz,
            "d_cap": cfg.d_cap,
            "e_heat": cfg.e_heat,
        },
    }
