from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional, Tuple

import numpy as np


def load_map(path: str) -> np.ndarray:
    if path.endswith(".npy"):
        return np.load(path)
    if path.endswith(".fits") or path.endswith(".fit"):
        try:
            from astropy.io import fits  # type: ignore
        except Exception as exc:
            raise RuntimeError("FITS support requires astropy") from exc
        with fits.open(path) as hdul:
            data = hdul[0].data
            if data is None:
                raise ValueError("FITS file contains no data")
            return np.array(data, dtype=float)
    raise ValueError("Unsupported file format; use .npy or .fits")


def normalize_map(values: np.ndarray, mode: str = "none") -> np.ndarray:
    mode = mode.lower().strip()
    if mode == "none":
        return values
    if mode == "zscore":
        mean = float(np.mean(values))
        std = float(np.std(values))
        if std == 0:
            return values - mean
        return (values - mean) / std
    if mode == "minmax":
        vmin = float(np.min(values))
        vmax = float(np.max(values))
        if vmax == vmin:
            return values - vmin
        return (values - vmin) / (vmax - vmin)
    raise ValueError(f"Unknown normalize mode: {mode}")


def _smooth_map_fft(values: np.ndarray, sigma_px: Optional[float]) -> np.ndarray:
    if sigma_px is None or sigma_px <= 0:
        return values
    n = values.shape[0]
    if values.shape[0] != values.shape[1]:
        raise ValueError("values must be square")
    freqs = np.fft.fftfreq(n, d=1.0)
    kx, ky = np.meshgrid(2.0 * np.pi * freqs, 2.0 * np.pi * freqs, indexing="xy")
    kernel = np.exp(-0.5 * (sigma_px**2) * (kx**2 + ky**2))
    return np.fft.ifft2(np.fft.fft2(values) * kernel).real


def _centroid(weights: np.ndarray) -> Tuple[float, float]:
    total = float(np.sum(weights))
    if total <= 0:
        return float(weights.shape[1] / 2), float(weights.shape[0] / 2)
    y_idx, x_idx = np.indices(weights.shape)
    x_c = float(np.sum(weights * x_idx) / total)
    y_c = float(np.sum(weights * y_idx) / total)
    return x_c, y_c


def peak(values: np.ndarray, smoothing_sigma_px: Optional[float] = None) -> Dict[str, Any]:
    field = _smooth_map_fft(values, smoothing_sigma_px)
    idx = np.unravel_index(np.argmax(field), field.shape)
    return {
        "index": [int(idx[0]), int(idx[1])],
        "x_px": float(idx[1]),
        "y_px": float(idx[0]),
        "value": float(field[idx]),
        "smoothing_sigma_px": smoothing_sigma_px,
    }


def com_positive(
    values: np.ndarray,
    threshold_frac: float = 0.1,
    smoothing_sigma_px: Optional[float] = None,
) -> Dict[str, Any]:
    field = _smooth_map_fft(values, smoothing_sigma_px)
    vmax = float(np.max(field))
    threshold = vmax * float(threshold_frac)
    weights = np.clip(field - threshold, 0.0, None)
    x_c, y_c = _centroid(weights)
    return {
        "x_px": x_c,
        "y_px": y_c,
        "threshold_frac": threshold_frac,
        "smoothing_sigma_px": smoothing_sigma_px,
    }


def aperture_com(
    values: np.ndarray,
    center_guess: Tuple[float, float],
    radius_px: float,
    threshold_frac: float = 0.1,
    smoothing_sigma_px: Optional[float] = None,
) -> Dict[str, Any]:
    field = _smooth_map_fft(values, smoothing_sigma_px)
    y_idx, x_idx = np.indices(field.shape)
    dx = x_idx - float(center_guess[0])
    dy = y_idx - float(center_guess[1])
    mask = (dx * dx + dy * dy) <= (radius_px * radius_px)
    vmax = float(np.max(field[mask])) if np.any(mask) else float(np.max(field))
    threshold = vmax * float(threshold_frac)
    weights = np.where(mask, np.clip(field - threshold, 0.0, None), 0.0)
    x_c, y_c = _centroid(weights)
    return {
        "x_px": x_c,
        "y_px": y_c,
        "threshold_frac": threshold_frac,
        "radius_px": radius_px,
        "smoothing_sigma_px": smoothing_sigma_px,
    }


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()