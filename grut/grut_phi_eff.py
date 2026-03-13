from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np


def _validate_square(field: np.ndarray) -> int:
    if field.ndim != 2:
        raise ValueError("field must be 2D")
    if field.shape[0] != field.shape[1]:
        raise ValueError("field must be square")
    return field.shape[0]


def _kspace_grid(n: int, fov_rad: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if fov_rad <= 0:
        raise ValueError("fov_rad must be positive")
    delta = fov_rad / float(n)
    freqs = np.fft.fftfreq(n, d=delta)
    kx, ky = np.meshgrid(2.0 * np.pi * freqs, 2.0 * np.pi * freqs, indexing="xy")
    k = np.sqrt(kx * kx + ky * ky)
    return kx, ky, k


def phi_from_sigma_baryon_fft(
    sigma_b_map: np.ndarray,
    fov_rad: float,
    kernel: str = "k1",
    eps: float = 1e-6,
) -> np.ndarray:
    n = _validate_square(sigma_b_map)
    _, _, k = _kspace_grid(n, fov_rad)
    sigma_k = np.fft.fft2(sigma_b_map)

    kernel = kernel.lower().strip()
    if kernel == "k1":
        denom = k + eps
    elif kernel == "k2":
        denom = k * k + eps
    else:
        raise ValueError(f"Unknown kernel: {kernel}")

    denom[0, 0] = math.inf
    phi_k = -sigma_k / denom
    phi_k[0, 0] = 0.0
    return np.fft.ifft2(phi_k).real


def apply_band_gate_kspace(
    phi_b: np.ndarray,
    fov_rad: float,
    k_low_frac: float = 0.05,
    k_high_frac: float = 0.9,
    order: int = 4,
    eps: float = 1e-12,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    n = _validate_square(phi_b)
    _, _, k = _kspace_grid(n, fov_rad)
    delta = fov_rad / float(n)
    k_nyquist = math.pi / delta
    k_low = k_low_frac * k_nyquist
    k_high = k_high_frac * k_nyquist

    gate_low = 1.0 - np.exp(-((k / (k_low + eps)) ** (2 * order)))
    gate_high = np.exp(-((k / (k_high + eps)) ** (2 * order)))
    gate = gate_low * gate_high

    phi_k = np.fft.fft2(phi_b)
    phi_eff = np.fft.ifft2(phi_k * gate).real

    meta = {
        "k_low_frac": float(k_low_frac),
        "k_high_frac": float(k_high_frac),
        "order": int(order),
        "k_nyquist": float(k_nyquist),
    }
    return phi_eff, meta


def apply_grut_gate_kspace_v0(
    phi_b: np.ndarray,
    fov_rad: float,
    alpha_mem: float,
    *,
    k0_policy: str = "r_smooth",
    k0_value: Optional[float] = None,
    r_smooth_rad: Optional[float] = None,
    sigma_ref_px: Optional[float] = None,
    pixel_scale_rad: Optional[float] = None,
    eps: float = 1e-12,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    n = _validate_square(phi_b)
    _, _, k = _kspace_grid(n, fov_rad)

    k0_policy = k0_policy.lower().strip()
    k0_used: float
    if k0_value is not None:
        k0_used = float(k0_value)
    elif k0_policy == "r_smooth":
        if r_smooth_rad is None:
            raise ValueError("r_smooth_rad is required for k0_policy=r_smooth")
        k0_used = 1.0 / max(float(r_smooth_rad), eps)
    elif k0_policy == "fov":
        k0_used = (2.0 * math.pi) / float(fov_rad)
    else:
        raise ValueError(f"Unknown k0_policy: {k0_policy}")

    k0_used = max(k0_used, eps)
    transfer = 1.0 + (float(alpha_mem) / (1.0 + (k / k0_used) ** 2))

    phi_k = np.fft.fft2(phi_b)
    phi_eff = np.fft.ifft2(phi_k * transfer).real

    meta = {
        "k0_policy": k0_policy,
        "k0_value_used": float(k0_used),
        "alpha_mem": float(alpha_mem),
        "r_smooth_rad": float(r_smooth_rad) if r_smooth_rad is not None else None,
        "sigma_ref_px": float(sigma_ref_px) if sigma_ref_px is not None else None,
        "pixel_scale_rad": float(pixel_scale_rad) if pixel_scale_rad is not None else None,
        "transfer_min": float(np.min(transfer)),
        "transfer_max": float(np.max(transfer)),
    }
    return phi_eff, meta


def phi_eff_from_phi_baryon(
    phi_b: np.ndarray,
    alpha_mem: float,
    response_model: str = "identity",
    *,
    fov_rad: Optional[float] = None,
    band_gate_config: Optional[Dict[str, Any]] = None,
    return_meta: bool = False,
) -> Union[np.ndarray, Tuple[np.ndarray, Dict[str, Any]]]:
    response_model = response_model.lower().strip()
    meta: Dict[str, Any] = {"response_model": response_model}

    if response_model == "identity":
        phi_eff = phi_b
    elif response_model == "scaled":
        phi_eff = (1.0 + float(alpha_mem)) * phi_b
    elif response_model == "band_gate":
        if fov_rad is None:
            raise ValueError("fov_rad is required for band_gate")
        band_gate_config = band_gate_config or {}
        phi_eff, gate_meta = apply_band_gate_kspace(phi_b, fov_rad, **band_gate_config)
        meta["band_gate"] = gate_meta
    elif response_model == "grut_gate_kspace_v0":
        if fov_rad is None:
            raise ValueError("fov_rad is required for grut_gate_kspace_v0")
        r_smooth_rad = None
        if band_gate_config and "r_smooth_rad" in band_gate_config:
            r_smooth_rad = float(band_gate_config["r_smooth_rad"])
        gate_config = band_gate_config or {}
        phi_eff, gate_meta = apply_grut_gate_kspace_v0(
            phi_b,
            fov_rad,
            alpha_mem,
            k0_policy=gate_config.get("k0_policy", "r_smooth"),
            k0_value=gate_config.get("k0_value"),
            r_smooth_rad=r_smooth_rad,
            sigma_ref_px=gate_config.get("sigma_ref_px"),
            pixel_scale_rad=gate_config.get("pixel_scale_rad"),
        )
        meta["grut_gate_kspace_v0"] = gate_meta
    else:
        raise ValueError(f"Unknown response_model: {response_model}")

    if return_meta:
        return phi_eff, meta
    return phi_eff
