from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Tuple, List

import numpy as np

from core.data_adapter import lookback_time_gyr, myr_to_s
from core.reconstruction.simulator import make_seth_kernel, convolve_causal


@dataclass
class SyntheticFsigma8:
    dataset: Dict[str, List[float]]
    diagnostic: Dict[str, Any]
    x_true: List[float]
    y_time: List[float]


def _invert_time_to_z(target_t_gyr: float, *, H0_km_s_Mpc: float = 67.4, Omega_m: float = 0.315, Omega_lambda: float = 0.685, z_max: float = 5.0) -> float:
    """Monotone inversion: find z such that lookback_time_gyr(z) ~= target_t_gyr.

    Uses a simple binary search assuming t_L(z) is monotone increasing with z.
    """
    if target_t_gyr <= 0.0:
        return 0.0

    lo = 0.0
    hi = float(z_max)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        t_mid, _ = lookback_time_gyr([0.0, mid], H0_km_s_Mpc=H0_km_s_Mpc, Omega_m=Omega_m, Omega_lambda=Omega_lambda)
        t_val = float(t_mid[1])
        if t_val < target_t_gyr:
            lo = mid
        else:
            hi = mid
    return float(hi)


def generate_synthetic_fsigma8_dataset(
    *,
    planted_tau_myr: float = 41.9,
    dt_myr: float = 5.0,
    span_myr: float = 600.0,
    n_kernel: int = 128,
    n_points: int = 8,
    seed: int = 0,
    noise_std: float = 0.0,
) -> SyntheticFsigma8:
    """Generate a deterministic memory-positive fsigma8 dataset.

    Parameters
    ----------
    planted_tau_myr : float
        Memory decay time to inject (Myr)
    dt_myr : float
        Internal resampling time step (Myr) for high-res generation
    span_myr : float
        Total time span over which to generate data (Myr)
    n_kernel : int
        Seth kernel length (samples)
    n_points : int
        Number of observed data points to sample
    seed : int
        RNG seed for reproducibility
    noise_std : float
        Gaussian noise amplitude (optional)

    The returned dataset is synthetic and intended solely for instrument validation.
    """
    rng = np.random.default_rng(int(seed))

    dt_s = myr_to_s(dt_myr)
    tau_s = myr_to_s(planted_tau_myr)

    # High-resolution internal grid for forward model
    n_resampled = int(np.ceil(float(span_myr) / float(dt_myr)))
    t_myr = np.arange(int(n_resampled), dtype=float) * float(dt_myr)

    # Sparse source: three spikes at fixed fractions with slight amplitude jitter
    event_positions = [int(0.18 * n_resampled), int(0.48 * n_resampled), int(0.74 * n_resampled)]
    event_amplitudes = [1.0, -0.85, 0.65]
    jitter = rng.uniform(0.9, 1.1, size=len(event_amplitudes))
    x_true = np.zeros(int(n_resampled), dtype=float)
    for pos, amp, j in zip(event_positions, event_amplitudes, jitter):
        idx = min(max(int(pos), 0), int(n_resampled) - 1)
        x_true[idx] += float(amp * j)

    # Forward smear with Seth kernel
    k = make_seth_kernel(dt_s=dt_s, tau_s=tau_s, n_kernel=int(n_kernel))
    y_time = convolve_causal(x_true, k)

    # Add optional noise
    if noise_std > 0:
        y_time = y_time + rng.normal(0.0, float(noise_std), size=y_time.shape)

    # Normalize to a plausible fsigma8 range
    y_min = float(np.min(y_time))
    y_max = float(np.max(y_time))
    span = y_max - y_min
    if span <= 0.0:
        span = 1.0
    y_norm = (y_time - y_min) / span
    fs8_lo, fs8_hi = 0.41, 0.52
    fs8_time = fs8_lo + y_norm * (fs8_hi - fs8_lo)

    # Sample n_points observations across the span
    sample_idx = np.linspace(0, int(n_resampled) - 1, num=int(n_points), dtype=int)
    t_samples_myr = t_myr[sample_idx]
    t_samples_gyr = t_samples_myr / 1000.0

    z_values = [_invert_time_to_z(float(tg)) for tg in t_samples_gyr]
    fs8_samples = fs8_time[sample_idx]
    sigma_samples = np.full_like(fs8_samples, 0.01, dtype=float)

    dataset = {
        "z": list(map(float, z_values)),
        "fsigma8": list(map(float, fs8_samples)),
        "sigma": list(map(float, sigma_samples)),
        "dataset_label": "fsigma8_synth_memory_positive",
    }

    diagnostic = {
        "synthetic": True,
        "planted_tau_myr": float(planted_tau_myr),
        "dt_myr": float(dt_myr),
        "span_myr": float(span_myr),
        "n_resampled": int(n_resampled),
        "n_kernel": int(n_kernel),
        "n_points": int(n_points),
        "noise_std": float(noise_std),
        "z_range": [float(np.min(z_values)), float(np.max(z_values))],
        "t_range_myr": [float(t_myr[0]), float(t_myr[-1])],
    }

    return SyntheticFsigma8(
        dataset=dataset,
        diagnostic=diagnostic,
        x_true=list(map(float, x_true.tolist())),
        y_time=list(map(float, y_time.tolist())),
    )
