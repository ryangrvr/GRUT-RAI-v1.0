from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class KernelSpec:
    """Defines the causal smear kernel (the "Mask" / DRM).

    Parameters
    ----------
    tau_s:
        Memory decay time (seconds). In GRUT this is typically tau0.
    dt_s:
        Sampling time step of the discretized signal.
    length:
        Number of samples in the kernel support.

    Notes
    -----
    We use a one-sided exponential by default:
        k[t] ∝ exp(-t*dt/tau) for t>=0.
    """

    tau_s: float
    dt_s: float
    length: int


def exponential_kernel(spec: KernelSpec) -> np.ndarray:
    """Create a normalized, one-sided exponential kernel."""
    if spec.tau_s <= 0:
        raise ValueError("tau_s must be > 0")
    if spec.dt_s <= 0:
        raise ValueError("dt_s must be > 0")
    if spec.length <= 1:
        raise ValueError("length must be > 1")

    t = np.arange(spec.length, dtype=float)
    k = np.exp(-(t * spec.dt_s) / spec.tau_s)
    k[0] = 1.0  # ensure causal impulse response starts at 1
    s = float(k.sum())
    if s == 0.0:
        raise ValueError("kernel sum is zero")
    return k / s


def convolve_causal(x: np.ndarray, k: np.ndarray) -> np.ndarray:
    """Causal convolution y[t] = sum_{i=0..t} k[i] x[t-i]."""
    x = np.asarray(x, dtype=float)
    k = np.asarray(k, dtype=float)
    if x.ndim != 1 or k.ndim != 1:
        raise ValueError("x and k must be 1D")

    # full convolution then truncate to length of x (causal response)
    y_full = np.convolve(x, k, mode="full")
    return y_full[: x.shape[0]]


def build_drm_matrix(k: np.ndarray, n: int) -> np.ndarray:
    """Build a (n x n) lower-triangular convolution matrix A such that y = A x."""
    k = np.asarray(k, dtype=float)
    if k.ndim != 1:
        raise ValueError("k must be 1D")
    if n <= 0:
        raise ValueError("n must be > 0")

    A = np.zeros((n, n), dtype=float)
    m = min(len(k), n)
    for col in range(n):
        # place kernel down the column starting at diagonal
        max_len = min(m, n - col)
        A[col : col + max_len, col] = k[:max_len]
    return A


@dataclass
class ForwardSimResult:
    source_x: np.ndarray
    shadow_y: np.ndarray
    kernel: np.ndarray
    dt_s: float


def make_seth_kernel(dt_s: float, tau_s: float, n_kernel: int) -> np.ndarray:
    """Alias: Seth Kernel (causal exponential) constructor.

    This keeps backward compatibility and provides a clear, named API for the
    kernel used by the Anamnesis reconstruction lens.
    """
    return exponential_kernel(KernelSpec(tau_s=tau_s, dt_s=dt_s, length=int(n_kernel)))


def simulate_shadow(
    source_x: np.ndarray,
    *,
    tau_s: float,
    dt_s: float,
    kernel_len: Optional[int] = None,
    noise_sigma: float = 0.0,
    rng: Optional[np.random.Generator] = None,
) -> ForwardSimResult:
    """Forward model: generate a "shadow" y from source x.

    This is the DRM (Detector Response Matrix) in 1D.
    """
    x = np.asarray(source_x, dtype=float)
    if x.ndim != 1:
        raise ValueError("source_x must be 1D")
    if kernel_len is None:
        # rule-of-thumb: cover ~6 tau for an exponential
        kernel_len = max(8, int(np.ceil(6.0 * tau_s / dt_s)))

    k = exponential_kernel(KernelSpec(tau_s=tau_s, dt_s=dt_s, length=kernel_len))
    y = convolve_causal(x, k)

    if noise_sigma > 0:
        if rng is None:
            rng = np.random.default_rng()
        y = y + rng.normal(0.0, noise_sigma, size=y.shape)

    return ForwardSimResult(source_x=x, shadow_y=y, kernel=k, dt_s=dt_s)


def make_sparse_events(
    n: int,
    event_positions: Tuple[int, ...],
    event_magnitudes: Tuple[float, ...],
) -> np.ndarray:
    """Utility: create a sparse 1D event vector."""
    if len(event_positions) != len(event_magnitudes):
        raise ValueError("event_positions and event_magnitudes must have same length")
    x = np.zeros(n, dtype=float)
    for p, a in zip(event_positions, event_magnitudes):
        if p < 0 or p >= n:
            raise ValueError(f"event position {p} out of range for n={n}")
        x[p] += float(a)
    return x
