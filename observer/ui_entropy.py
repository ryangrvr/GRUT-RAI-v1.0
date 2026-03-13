from __future__ import annotations

from dataclasses import dataclass


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))


@dataclass(frozen=True)
class UIInteractionWindow:
    """Minimal, transparent UI telemetry window.

    ui_actions: number of discrete actions in the window (slider moves, toggles, run triggers)
    window_s: window duration in seconds
    avg_param_delta: average normalized parameter delta per action (0..1)

    This is a *model input* for ObserverState (not a claim about thermodynamic entropy).
    """

    ui_actions: int = 0
    window_s: float = 30.0
    avg_param_delta: float = 0.0


@dataclass(frozen=True)
class UIEntropyConfig:
    k_rate: float = 0.4
    k_mag: float = 0.6
    max_actions_per_s: float = 3.0  # normalization ceiling


def compute_ui_entropy(window: UIInteractionWindow, cfg: UIEntropyConfig = UIEntropyConfig()) -> dict:
    """Compute a bounded UI_entropy score in [0,1] plus components.

    rate_norm = min(1, (actions/window_s) / max_actions_per_s)
    mag_norm = clamp(avg_param_delta, 0, 1)
    ui_entropy = clamp(k_rate*rate_norm + k_mag*mag_norm, 0, 1)

    Returns a dict for easy logging.
    """

    w_s = max(float(window.window_s), 1e-6)
    rate = float(window.ui_actions) / w_s
    rate_norm = clamp(rate / max(cfg.max_actions_per_s, 1e-6), 0.0, 1.0)
    mag_norm = clamp(window.avg_param_delta, 0.0, 1.0)
    ui_entropy = clamp(cfg.k_rate * rate_norm + cfg.k_mag * mag_norm, 0.0, 1.0)

    return {
        "ui_entropy": ui_entropy,
        "ui_rate_per_s": rate,
        "ui_rate_norm": rate_norm,
        "ui_magnitude_norm": mag_norm,
        "window_s": w_s,
        "ui_actions": int(window.ui_actions),
        "avg_param_delta": float(window.avg_param_delta),
        "k_rate": float(cfg.k_rate),
        "k_mag": float(cfg.k_mag),
        "max_actions_per_s": float(cfg.max_actions_per_s),
    }
