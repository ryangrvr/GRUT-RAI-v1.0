from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np


def soft_threshold(u: np.ndarray, lam: float) -> np.ndarray:
    """Soft-thresholding operator for L1 sparsity."""
    return np.sign(u) * np.maximum(np.abs(u) - lam, 0.0)


@dataclass
class LCAConfig:
    """Configuration for the Locally Competitive Algorithm (LCA).

    We solve a 1D sparse inverse problem (LASSO-like):
        argmin_x 0.5 ||y - A x||^2 + lam ||x||_1

    Notes
    -----
    This implementation is intentionally simple and dependency-free.
    """

    lam: float = 0.05
    max_iters: int = 2000
    dt: float = 0.2
    tau: float = 1.0
    tol: float = 1e-6
    min_iters: int = 25
    tol_res: float = 1e-6
    nonneg: bool = False


@dataclass
class LCAResult:
    x_hat: np.ndarray
    converged: bool
    iters: int
    residual_norm: float
    objective: float
    diagnostics: Dict[str, float]


def lca_reconstruct(
    y: np.ndarray,
    A: np.ndarray,
    cfg: Optional[LCAConfig] = None,
    x0: Optional[np.ndarray] = None,
    kernel_hash: Optional[str] = None,
) -> LCAResult:
    """Run LCA to reconstruct sparse x from y given forward matrix A.

    Parameters
    ----------
    kernel_hash:
        Optional sha256 hex digest of the kernel used to build A. When
        provided, it will be recorded in diagnostics as
        `kernel_hash_used_by_reconstructor` to allow downstream verification.
    """
    if cfg is None:
        cfg = LCAConfig()

    y = np.asarray(y, dtype=float).reshape(-1)
    A = np.asarray(A, dtype=float)
    if A.ndim != 2:
        raise ValueError("A must be 2D")

    m, n = A.shape
    if y.shape[0] != m:
        raise ValueError(f"y length ({y.shape[0]}) must match A rows ({m})")

    # Normalize columns of A for stability (common in sparse coding)
    col_norms = np.linalg.norm(A, axis=0)
    col_norms[col_norms == 0] = 1.0
    A_n = A / col_norms

    if x0 is None:
        u = np.zeros(n, dtype=float)
    else:
        x0 = np.asarray(x0, dtype=float).reshape(-1)
        if x0.shape[0] != n:
            raise ValueError("x0 must have length n")
        u = x0.copy()

    x = soft_threshold(u, cfg.lam)
    if cfg.nonneg:
        x = np.maximum(x, 0.0)

    # Precompute Gram matrix for speed
    At = A_n.T
    G = At @ A_n
    b = At @ y

    prev_obj = np.inf
    prev_res_norm = np.inf
    converged = False
    trace: list[Dict[str, float]] = []
    iter_trace: list[Dict[str, float]] = []

    for it in range(1, cfg.max_iters + 1):
        # u dynamics (Rozell et al.): du/dt = b - Gx - u + x
        du = (b - (G @ x) - u + x) / cfg.tau
        u = u + cfg.dt * du

        x_new = soft_threshold(u, cfg.lam)
        if cfg.nonneg:
            x_new = np.maximum(x_new, 0.0)

        r = y - (A_n @ x_new)
        res_norm = float(np.linalg.norm(r))
        obj = 0.5 * (res_norm**2) + cfg.lam * float(np.sum(np.abs(x_new)))

        # Record the lightweight trace (compatibility) for first 25 iters
        if len(trace) < 25:
            trace.append({"iter": it, "residual": res_norm, "objective": obj})

        # Record detailed iter_trace for first 10 iterations for debugging
        if len(iter_trace) < 10:
            x_l1 = float(np.sum(np.abs(x_new)))
            x_l2 = float(np.linalg.norm(x_new))
            max_abs_u = float(np.max(np.abs(u))) if u.size > 0 else 0.0
            max_abs_x = float(np.max(np.abs(x_new))) if x_new.size > 0 else 0.0
            nnz = int(np.sum(np.abs(x_new) > 1e-12))
            iter_trace.append(
                {
                    "iter": it,
                    "obj": obj,
                    "res_norm": res_norm,
                    "x_l1": x_l1,
                    "x_l2": x_l2,
                    "max_abs_u": max_abs_u,
                    "max_abs_x": max_abs_x,
                    "nnz": nnz,
                }
            )

        # Convergence criterion: require a minimum number of iterations and both
        # small relative change in x and stabilization of residual norm.
        if it >= int(getattr(cfg, "min_iters", 0)):
            dx_norm = float(np.linalg.norm(x_new - x))
            prev_x_norm = float(np.linalg.norm(x))
            dx_rel = dx_norm / max(prev_x_norm, 1e-12)

            if prev_res_norm != np.inf and prev_res_norm > 0:
                res_change_rel = abs(res_norm - prev_res_norm) / float(prev_res_norm)
            else:
                res_change_rel = float("inf")

            if dx_rel < float(cfg.tol) and res_change_rel < float(cfg.tol_res):
                converged = True
                x = x_new
                prev_obj = obj
                break

        # Not converged yet: update state
        x = x_new
        prev_obj = obj
        prev_res_norm = res_norm

    # Un-normalize back into original scale
    x_hat = x / col_norms

    r_final = y - (A @ x_hat)
    residual_norm = float(np.linalg.norm(r_final))
    objective = 0.5 * residual_norm**2 + cfg.lam * float(np.sum(np.abs(x_hat)))

    diagnostics = {
        "lam": float(cfg.lam),
        "dt": float(cfg.dt),
        "tau": float(cfg.tau),
        "tol": float(cfg.tol),
        "max_iters": float(cfg.max_iters),
        "trace": trace,
        "iter_trace": iter_trace,
        "kernel_hash_used_by_reconstructor": kernel_hash if kernel_hash is not None else None,
    }

    return LCAResult(
        x_hat=x_hat,
        converged=converged,
        iters=it,
        residual_norm=residual_norm,
        objective=objective,
        diagnostics=diagnostics,
    )


def pick_lambda_from_snr(y: np.ndarray, snr_db: float) -> float:
    """Heuristic lambda selection from an assumed SNR (dB)."""
    y = np.asarray(y, dtype=float).reshape(-1)
    power = float(np.mean(y**2))
    if power <= 0:
        return 0.0
    snr = 10 ** (snr_db / 10.0)
    noise_power = power / snr
    noise_sigma = np.sqrt(noise_power)
    # classic soft-threshold: sigma * sqrt(2 log n)
    return float(noise_sigma * np.sqrt(2.0 * np.log(max(2, y.size))))


def ridge_deconvolution(y: np.ndarray, k: np.ndarray, lam2: float = 1e-3, nonneg: bool = False, kernel_hash: Optional[str] = None):
    """Ridge (Tikhonov) deconvolution solved in Fourier domain.

    Solves x_hat = ifft(conj(K_fft) * Y_fft / (|K_fft|^2 + lam2))
    Ensures x_hat is real and finite. Optional nonnegativity enforced by clipping.

    Returns a LCAResult-like object for compatibility with reconstruction callers.
    """
    y = np.asarray(y, dtype=float).reshape(-1)
    k = np.asarray(k, dtype=float).reshape(-1)
    n = y.size

    # Pad kernel to signal length
    k_padded = np.zeros(n, dtype=float)
    k_padded[: min(k.size, n)] = k[:min(k.size, n)]

    # FFT-based deconvolution
    Y = np.fft.rfft(y)
    K = np.fft.rfft(k_padded)
    denom = (np.abs(K) ** 2) + float(lam2)

    # Avoid division by zero
    X_freq = np.conj(K) * Y / denom
    x_hat = np.fft.irfft(X_freq, n=n)

    # Ensure real/finite; clip tiny numerical noise
    x_hat = np.real_if_close(x_hat)
    x_hat = np.nan_to_num(x_hat, nan=0.0, posinf=0.0, neginf=0.0)

    if nonneg:
        x_hat = np.maximum(x_hat, 0.0)

    # Reconstruct observed via causal convolution (valid linear convolution truncated)
    y_hat = np.convolve(x_hat, k, mode='full')[:n]

    residual_norm = float(np.linalg.norm(y - y_hat))
    # Ridge objective: 0.5||y-Ax||^2 + lam2 * ||x||^2
    objective = 0.5 * (residual_norm ** 2) + float(lam2) * float(np.sum(x_hat ** 2))

    diagnostics = {
        "lam_smooth": float(lam2),
        "kernel_hash_used_by_reconstructor": kernel_hash,
        "trace": [],
        "iter_trace": [],
        "y_hat_override": y_hat,
    }

    return LCAResult(
        x_hat=x_hat,
        converged=True,
        iters=1,
        residual_norm=residual_norm,
        objective=objective,
        diagnostics=diagnostics,
    )


def ridge_deconv_fft(y: np.ndarray, kernel: np.ndarray, lam2: float = 1e-3, nonneg: bool = False):
    """Compatibility wrapper with the requested name `ridge_deconv_fft`.

    Simply calls `ridge_deconvolution` and returns x_hat array for quick use.
    """
    res = ridge_deconvolution(y, kernel, lam2=lam2, nonneg=nonneg)
    return res.x_hat