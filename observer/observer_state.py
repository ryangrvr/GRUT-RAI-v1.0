from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import math

from .profiles import ObserverProfile, PROFILE_WEIGHTS
from .ui_entropy import UIInteractionWindow, UIEntropyConfig, compute_ui_entropy
from .sensors import SensorConfig, compute_sensor_flux
from .info_density import InfoDensityConfig, compute_I_value
from .determination import compute_P_lock
from .metabolic import classify_state, compute_tension_score


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))


@dataclass(frozen=True)
class FrameConfig:
    F_min: float = 0.5
    F_max: float = 2.0


@dataclass(frozen=True)
class ObserverConfigV1:
    profile: ObserverProfile = "monk"

    # Optional frame inputs
    v_obs_m_s: float = 0.0
    phi_over_c2: float = 0.0  # dimensionless (Phi_local / c^2)

    # UI entropy
    ui_window: UIInteractionWindow = UIInteractionWindow()
    ui_cfg: UIEntropyConfig = UIEntropyConfig()

    # Sensors
    sensor: SensorConfig = SensorConfig()

    # Information density
    info_cfg: InfoDensityConfig = InfoDensityConfig()
    frame_cfg: FrameConfig = FrameConfig()

    # Research toggle: allow observer metrics to modulate dissipation in report
    enable_observer_modulation: bool = False


def compute_frame_factor(v_obs_m_s: float, phi_over_c2: float, cfg: FrameConfig) -> dict:
    c = 299_792_458.0
    v = abs(float(v_obs_m_s))
    beta2 = (v * v) / (c * c)
    beta2 = clamp(beta2, 0.0, 0.999999)

    # (1 + 2phi/c^2) / (1 - v^2/c^2)
    num = 1.0 + 2.0 * float(phi_over_c2)
    num = max(num, 1e-9)
    denom = 1.0 - beta2
    F = math.sqrt(num / denom)
    F = clamp(F, cfg.F_min, cfg.F_max)
    return {
        "frame_factor": float(F),
        "v_obs_m_s": float(v_obs_m_s),
        "phi_over_c2": float(phi_over_c2),
        "F_min": float(cfg.F_min),
        "F_max": float(cfg.F_max),
    }


def compute_observer_state(
    eps_t_myr: float,
    tau0_seconds: float,
    engine_v_grid_max_m_s: float,
    cap_engaged_frac: float,
    pivot_intensity: float,
    I_heat: float,
    fuzz_fraction: float,
    obs: Optional[ObserverConfigV1],
) -> Dict[str, Any]:
    """Compute observer-layer diagnostics.

    This is app-layer logic. By default it does not modify cosmology outputs.
    """

    if obs is None:
        obs = ObserverConfigV1(profile="monk")

    profile = obs.profile
    weights = PROFILE_WEIGHTS[profile]

    # Monk is absolute stillness baseline
    if profile == "monk":
        ui = {
            "ui_entropy": 0.0,
            "ui_rate_per_s": 0.0,
            "ui_rate_norm": 0.0,
            "ui_magnitude_norm": 0.0,
            "window_s": float(obs.ui_window.window_s),
            "ui_actions": 0,
            "avg_param_delta": 0.0,
        }
        sensor = {
            "sensor_mode": "off",
            "sensor_flux": 0.0,
            "sensor_snapshot_hash": None,
            "sensor_timestamp_utc": None,
            "sensor_source": None,
            "sensor_reproducible": True,
            "sensor_warnings": [],
        }
    else:
        ui = compute_ui_entropy(obs.ui_window, obs.ui_cfg)
        sensor = compute_sensor_flux(obs.sensor)

    # Frame factor and eps_user
    frame = compute_frame_factor(obs.v_obs_m_s, obs.phi_over_c2, obs.frame_cfg)
    MYR_IN_S = 1_000_000 * 365.25 * 24 * 3600
    eps_t_s = float(eps_t_myr) * MYR_IN_S
    eps_user_s = eps_t_s * float(frame["frame_factor"])

    # Hybrid ΔS
    deltaS = weights.w_ui * float(ui["ui_entropy"]) + weights.w_sensor * float(sensor["sensor_flux"])

    # I(t)
    I_dict = compute_I_value(deltaS, eps_user_s, obs.info_cfg)

    # Determination strength
    P = compute_P_lock(I_dict["I_value"], eps_user_s, tau0_seconds)

    # v_in for CFL
    v_in = max(float(engine_v_grid_max_m_s), abs(float(obs.v_obs_m_s)))

    # Metabolic labels
    metabolic_state = classify_state(
        fuzz_fraction=fuzz_fraction,
        pivot_intensity=pivot_intensity,
        cap_engaged_frac=cap_engaged_frac,
        I_heat=I_heat,
    )

    tension = compute_tension_score(
        ui_entropy=float(ui.get("ui_entropy", 0.0)),
        sensor_flux=float(sensor.get("sensor_flux", 0.0)),
        fuzz_fraction=fuzz_fraction,
        cap_engaged_frac=cap_engaged_frac,
        I_heat=I_heat,
    )

    return {
        "observer_profile": profile,
        "profile_weights": {"w_ui": weights.w_ui, "w_sensor": weights.w_sensor},
        "ui": ui,
        "sensor": sensor,
        "frame": frame,
        "eps_user_s": float(eps_user_s),
        "deltaS": float(deltaS),
        "I": I_dict,
        "P_lock": P,
        "v_in_m_s": float(v_in),
        "metabolic_state": metabolic_state,
        "tension": tension,
        "enable_observer_modulation": bool(obs.enable_observer_modulation),
    }
