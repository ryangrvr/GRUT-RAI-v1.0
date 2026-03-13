from __future__ import annotations

import io
import math
import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import numpy as np

from grut.utils import stable_sha256


ARCSEC_PER_RAD = 206264.806
ARCMIN_PER_RAD = ARCSEC_PER_RAD / 60.0


@dataclass(frozen=True)
class LensingRunResult:
    kappa: np.ndarray
    gamma1: np.ndarray
    gamma2: np.ndarray
    summary: Dict[str, Any]
    certificate: Dict[str, Any]
    psi: Optional[np.ndarray] = None
    alpha_x: Optional[np.ndarray] = None
    alpha_y: Optional[np.ndarray] = None


def make_grid(n: int, fov_rad: float) -> Tuple[np.ndarray, np.ndarray]:
    if n <= 0:
        raise ValueError("n must be positive")
    if fov_rad <= 0:
        raise ValueError("fov_rad must be positive")
    delta = fov_rad / float(n)
    coords = (np.arange(n) - (n - 1) / 2.0) * delta
    theta_x, theta_y = np.meshgrid(coords, coords, indexing="xy")
    return theta_x, theta_y


def sigma_elliptical_gaussian(
    params: Dict[str, float], grid: Tuple[np.ndarray, np.ndarray]
) -> np.ndarray:
    amp = float(params.get("amp", 1.0))
    sigma_x = float(params.get("sigma_x", 1.0))
    sigma_y = float(params.get("sigma_y", 1.0))
    x0 = float(params.get("x0", 0.0))
    y0 = float(params.get("y0", 0.0))
    theta = float(params.get("theta", 0.0))
    if sigma_x <= 0 or sigma_y <= 0:
        raise ValueError("sigma_x and sigma_y must be positive")

    theta_x, theta_y = grid
    dx = theta_x - x0
    dy = theta_y - y0
    c, s = math.cos(theta), math.sin(theta)
    xr = c * dx + s * dy
    yr = -s * dx + c * dy
    exponent = -0.5 * ((xr / sigma_x) ** 2 + (yr / sigma_y) ** 2)
    return amp * np.exp(exponent)


def compute_kappa(sigma_map: np.ndarray, sigma_crit: float) -> np.ndarray:
    if sigma_crit <= 0:
        raise ValueError("sigma_crit must be positive")
    return sigma_map / float(sigma_crit)


def compute_shear_fft(kappa_map: np.ndarray, fov_rad: float) -> Tuple[np.ndarray, np.ndarray]:
    n = kappa_map.shape[0]
    if kappa_map.shape[0] != kappa_map.shape[1]:
        raise ValueError("kappa_map must be square")
    if fov_rad <= 0:
        raise ValueError("fov_rad must be positive")

    delta = fov_rad / float(n)
    freqs = np.fft.fftfreq(n, d=delta)
    kx, ky = np.meshgrid(2.0 * np.pi * freqs, 2.0 * np.pi * freqs, indexing="xy")
    k2 = kx**2 + ky**2
    k2[0, 0] = np.inf

    kappa_ft = np.fft.fft2(kappa_map)
    gamma1_ft = (kx**2 - ky**2) / k2 * kappa_ft
    gamma2_ft = (2.0 * kx * ky) / k2 * kappa_ft

    gamma1 = np.fft.ifft2(gamma1_ft).real
    gamma2 = np.fft.ifft2(gamma2_ft).real
    return gamma1, gamma2


def spectral_derivatives_2d(
    field: np.ndarray, fov_rad: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = field.shape[0]
    if field.shape[0] != field.shape[1]:
        raise ValueError("field must be square")
    if fov_rad <= 0:
        raise ValueError("fov_rad must be positive")

    delta = fov_rad / float(n)
    freqs = np.fft.fftfreq(n, d=delta)
    kx, ky = np.meshgrid(2.0 * np.pi * freqs, 2.0 * np.pi * freqs, indexing="xy")
    field_ft = np.fft.fft2(field)

    dx = np.fft.ifft2(1j * kx * field_ft).real
    dy = np.fft.ifft2(1j * ky * field_ft).real
    dxx = np.fft.ifft2(-(kx**2) * field_ft).real
    dyy = np.fft.ifft2(-(ky**2) * field_ft).real
    dxy = np.fft.ifft2(-(kx * ky) * field_ft).real
    return dx, dy, dxx, dyy, dxy


def compute_lensing_from_psi(
    psi: np.ndarray, fov_rad: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    dx, dy, dxx, dyy, dxy = spectral_derivatives_2d(psi, fov_rad)
    alpha_x = dx
    alpha_y = dy
    kappa = 0.5 * (dxx + dyy)
    gamma1 = 0.5 * (dxx - dyy)
    gamma2 = dxy
    return alpha_x, alpha_y, kappa, gamma1, gamma2


def compute_psi_from_phi(phi_eff_2d: np.ndarray, A_psi: float) -> np.ndarray:
    return float(A_psi) * phi_eff_2d


def _pad_and_crop(field: np.ndarray, pad_factor: int) -> Tuple[np.ndarray, Tuple[int, int]]:
    if pad_factor <= 1:
        return field, (0, 0)
    n = field.shape[0]
    if field.shape[0] != field.shape[1]:
        raise ValueError("field must be square for padding")
    n_pad = int(n * pad_factor)
    if n_pad <= n:
        raise ValueError("pad_factor must increase grid size")
    pad_total = n_pad - n
    pad_before = pad_total // 2
    pad_after = pad_total - pad_before
    padded = np.pad(field, ((pad_before, pad_after), (pad_before, pad_after)), mode="constant")
    return padded, (pad_before, n_pad)


def _crop_center(field: np.ndarray, n: int) -> np.ndarray:
    n_full = field.shape[0]
    if n_full == n:
        return field
    center = n_full // 2
    half = n // 2
    start = center - half
    end = start + n
    return field[start:end, start:end]


def _smooth_map_fft(values: np.ndarray, sigma_px: float) -> np.ndarray:
    if sigma_px <= 0:
        return values
    n = values.shape[0]
    if values.shape[0] != values.shape[1]:
        raise ValueError("values must be square")
    freqs = np.fft.fftfreq(n, d=1.0)
    kx, ky = np.meshgrid(2.0 * np.pi * freqs, 2.0 * np.pi * freqs, indexing="xy")
    kernel = np.exp(-0.5 * (sigma_px**2) * (kx**2 + ky**2))
    return np.fft.ifft2(np.fft.fft2(values) * kernel).real


def find_peak(map_2d: np.ndarray, theta_x: np.ndarray, theta_y: np.ndarray) -> Dict[str, Any]:
    idx = np.unravel_index(np.argmax(map_2d), map_2d.shape)
    peak_x = float(theta_x[idx])
    peak_y = float(theta_y[idx])
    return {
        "index": [int(idx[0]), int(idx[1])],
        "theta_x_rad": peak_x,
        "theta_y_rad": peak_y,
        "theta_x_arcmin": peak_x * ARCMIN_PER_RAD,
        "theta_y_arcmin": peak_y * ARCMIN_PER_RAD,
        "theta_x_arcsec": peak_x * ARCSEC_PER_RAD,
        "theta_y_arcsec": peak_y * ARCSEC_PER_RAD,
    }


def _centroid_positive(map_2d: np.ndarray, theta_x: np.ndarray, theta_y: np.ndarray) -> Dict[str, Any]:
    weights = np.clip(map_2d, 0.0, None)
    total = float(np.sum(weights))
    if total <= 0:
        return find_peak(map_2d, theta_x, theta_y)
    x_centroid = float(np.sum(weights * theta_x) / total)
    y_centroid = float(np.sum(weights * theta_y) / total)
    idx = np.unravel_index(
        np.argmin((theta_x - x_centroid) ** 2 + (theta_y - y_centroid) ** 2),
        map_2d.shape,
    )
    return {
        "index": [int(idx[0]), int(idx[1])],
        "theta_x_rad": x_centroid,
        "theta_y_rad": y_centroid,
        "theta_x_arcmin": x_centroid * ARCMIN_PER_RAD,
        "theta_y_arcmin": y_centroid * ARCMIN_PER_RAD,
        "theta_x_arcsec": x_centroid * ARCSEC_PER_RAD,
        "theta_y_arcsec": y_centroid * ARCSEC_PER_RAD,
    }


def compute_offset(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    dx = float(a["theta_x_rad"]) - float(b["theta_x_rad"])
    dy = float(a["theta_y_rad"]) - float(b["theta_y_rad"])
    magnitude = math.hypot(dx, dy)
    return {
        "dx_rad": dx,
        "dy_rad": dy,
        "magnitude_rad": magnitude,
        "dx_arcmin": dx * ARCMIN_PER_RAD,
        "dy_arcmin": dy * ARCMIN_PER_RAD,
        "magnitude_arcmin": magnitude * ARCMIN_PER_RAD,
        "dx_arcsec": dx * ARCSEC_PER_RAD,
        "dy_arcsec": dy * ARCSEC_PER_RAD,
        "magnitude_arcsec": magnitude * ARCSEC_PER_RAD,
    }


def _array_sha256(array: np.ndarray) -> str:
    buffer = io.BytesIO()
    np.save(buffer, array)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def _summary_hash(summary: Dict[str, Any]) -> str:
    return stable_sha256(summary)


def _basic_stats(values: np.ndarray) -> Dict[str, float]:
    return {
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values)),
    }


def run_lensing(
    config: Dict[str, Any],
    *,
    canon_hash: Optional[str] = None,
) -> LensingRunResult:
    n = int(config.get("n", 256))
    fov_arcmin = float(config.get("fov_arcmin", 20.0))
    sigma_crit = float(config.get("sigma_crit", 1.0))
    preset = str(config.get("preset", "single_halo"))
    mode = str(config.get("mode", "sigma_to_kappa"))
    delta_arcmin = float(config.get("delta_arcmin", 1.0))
    A_psi = float(config.get("A_psi", 1.0))
    phi_preset = str(config.get("phi_preset", "bullet_phi_toy"))
    phi_npy_path = config.get("phi_npy_path")
    pad_factor = int(config.get("pad_factor", 1))
    peak_mode = str(config.get("peak_mode", "max_kappa"))
    smoothing_sigma_px = float(config.get("smoothing_sigma_px", 0.0))

    fov_rad = fov_arcmin / ARCMIN_PER_RAD
    theta_x, theta_y = make_grid(n, fov_rad)

    sigma_map = None
    gas_map = None
    phi_map = None

    if mode == "sigma_to_kappa":
        if preset == "single_halo":
            params = {
                "amp": float(config.get("amp", 1.0)),
                "sigma_x": float(config.get("sigma_x", fov_rad / 20.0)),
                "sigma_y": float(config.get("sigma_y", fov_rad / 20.0)),
                "x0": 0.0,
                "y0": 0.0,
                "theta": float(config.get("theta", 0.0)),
            }
            sigma_map = sigma_elliptical_gaussian(params, (theta_x, theta_y))
        elif preset == "bullet_toy":
            delta_rad = delta_arcmin / ARCMIN_PER_RAD
            mass_params = {
                "amp": float(config.get("mass_amp", 1.0)),
                "sigma_x": float(config.get("mass_sigma_x", fov_rad / 20.0)),
                "sigma_y": float(config.get("mass_sigma_y", fov_rad / 25.0)),
                "x0": float(config.get("mass_x0", delta_rad)),
                "y0": float(config.get("mass_y0", 0.0)),
                "theta": float(config.get("mass_theta", 0.0)),
            }
            gas_params = {
                "amp": float(config.get("gas_amp", 0.7)),
                "sigma_x": float(config.get("gas_sigma_x", fov_rad / 18.0)),
                "sigma_y": float(config.get("gas_sigma_y", fov_rad / 22.0)),
                "x0": float(config.get("gas_x0", -delta_rad)),
                "y0": float(config.get("gas_y0", 0.0)),
                "theta": float(config.get("gas_theta", 0.0)),
            }
            sigma_map = sigma_elliptical_gaussian(mass_params, (theta_x, theta_y))
            gas_map = sigma_elliptical_gaussian(gas_params, (theta_x, theta_y))
        else:
            raise ValueError(f"Unknown preset: {preset}")
    elif mode == "phi_to_psi":
        if phi_preset == "from_npy":
            if not phi_npy_path:
                raise ValueError("phi_npy_path is required for from_npy")
            phi_map = np.load(phi_npy_path)
        elif phi_preset == "bullet_phi_toy":
            delta_rad = delta_arcmin / ARCMIN_PER_RAD
            mass_params = {
                "amp": float(config.get("phi_mass_amp", 1e-6)),
                "sigma_x": float(config.get("phi_mass_sigma_x", fov_rad / 20.0)),
                "sigma_y": float(config.get("phi_mass_sigma_y", fov_rad / 25.0)),
                "x0": float(config.get("phi_mass_x0", delta_rad)),
                "y0": float(config.get("phi_mass_y0", 0.0)),
                "theta": float(config.get("phi_mass_theta", 0.0)),
            }
            gas_params = {
                "amp": float(config.get("phi_gas_amp", 7e-7)),
                "sigma_x": float(config.get("phi_gas_sigma_x", fov_rad / 18.0)),
                "sigma_y": float(config.get("phi_gas_sigma_y", fov_rad / 22.0)),
                "x0": float(config.get("phi_gas_x0", -delta_rad)),
                "y0": float(config.get("phi_gas_y0", 0.0)),
                "theta": float(config.get("phi_gas_theta", 0.0)),
            }
            phi_map = sigma_elliptical_gaussian(mass_params, (theta_x, theta_y))
            gas_map = sigma_elliptical_gaussian(gas_params, (theta_x, theta_y))
        elif phi_preset == "point_mass":
            phi_map = np.zeros((n, n), dtype=float)
            phi_map[n // 2, n // 2] = float(config.get("phi_mass_amp", 1.0))
        else:
            raise ValueError(f"Unknown phi_preset: {phi_preset}")
    else:
        raise ValueError(f"Unknown mode: {mode}")

    psi = None
    alpha_x = None
    alpha_y = None
    pad_n = None
    crop_start = None
    crop_end = None
    if mode == "sigma_to_kappa":
        kappa = compute_kappa(sigma_map, sigma_crit)
        gamma1, gamma2 = compute_shear_fft(kappa, fov_rad)
    else:
        psi = compute_psi_from_phi(phi_map, A_psi)
        if pad_factor > 1:
            psi_padded, _ = _pad_and_crop(psi, pad_factor)
            fov_rad_padded = fov_rad * pad_factor
            pad_n = psi_padded.shape[0]
            crop_start = (pad_n // 2) - (n // 2)
            crop_end = crop_start + n
            alpha_x_p, alpha_y_p, kappa_p, gamma1_p, gamma2_p = compute_lensing_from_psi(
                psi_padded, fov_rad_padded
            )
            alpha_x = _crop_center(alpha_x_p, n)
            alpha_y = _crop_center(alpha_y_p, n)
            kappa = _crop_center(kappa_p, n)
            gamma1 = _crop_center(gamma1_p, n)
            gamma2 = _crop_center(gamma2_p, n)
        else:
            alpha_x, alpha_y, kappa, gamma1, gamma2 = compute_lensing_from_psi(psi, fov_rad)

    gamma_abs = np.sqrt(gamma1**2 + gamma2**2)
    alpha_abs = np.sqrt(alpha_x**2 + alpha_y**2) if alpha_x is not None else None

    peak_field = kappa
    if peak_mode == "smoothed_max_kappa":
        peak_field = _smooth_map_fft(kappa, smoothing_sigma_px)
        peak_kappa = find_peak(peak_field, theta_x, theta_y)
    elif peak_mode == "max_kappa":
        peak_kappa = find_peak(peak_field, theta_x, theta_y)
    elif peak_mode == "com_positive_kappa":
        peak_kappa = _centroid_positive(kappa, theta_x, theta_y)
    else:
        raise ValueError(f"Unknown peak_mode: {peak_mode}")
    peak_gas = find_peak(gas_map, theta_x, theta_y) if gas_map is not None else None
    offset = compute_offset(peak_kappa, peak_gas) if peak_gas is not None else None

    summary = {
        "grid": {
            "n": n,
            "fov_arcmin": fov_arcmin,
            "fov_rad": fov_rad,
        },
        "sigma_crit": sigma_crit,
        "preset": preset,
        "mode": mode,
        "A_psi": A_psi if mode == "phi_to_psi" else None,
        "phi_preset": phi_preset if mode == "phi_to_psi" else None,
        "pad_factor": pad_factor if mode == "phi_to_psi" else None,
        "pad_n": pad_n if mode == "phi_to_psi" else None,
        "crop_start": crop_start if mode == "phi_to_psi" else None,
        "crop_end": crop_end if mode == "phi_to_psi" else None,
        "phi_mass_amp": float(config.get("phi_mass_amp", 1e-6)) if mode == "phi_to_psi" else None,
        "phi_gas_amp": float(config.get("phi_gas_amp", 7e-7)) if mode == "phi_to_psi" else None,
        "delta_arcmin": delta_arcmin if preset == "bullet_toy" or phi_preset == "bullet_phi_toy" else None,
        "peak_mode": peak_mode,
        "smoothing_sigma_px": smoothing_sigma_px if peak_mode == "smoothed_max_kappa" else None,
        "peak_kappa": peak_kappa,
        "peak_gas": peak_gas,
        "offset": offset,
        "stats": {
            "kappa": _basic_stats(kappa),
            "gamma_abs": _basic_stats(gamma_abs),
            "alpha_abs": _basic_stats(alpha_abs) if alpha_abs is not None else None,
        },
    }

    output_hashes = {
        "kappa.npy": _array_sha256(kappa),
        "gamma1.npy": _array_sha256(gamma1),
        "gamma2.npy": _array_sha256(gamma2),
        "summary.json": _summary_hash(summary),
    }
    if psi is not None:
        output_hashes["psi.npy"] = _array_sha256(psi)
    if alpha_x is not None:
        output_hashes["alpha_x.npy"] = _array_sha256(alpha_x)
    if alpha_y is not None:
        output_hashes["alpha_y.npy"] = _array_sha256(alpha_y)
    output_digest = stable_sha256(output_hashes)

    certificate = {
        "canon_hash": canon_hash or "N/A",
        "tool_version": "v0.2",
        "determinism_mode": "STRICT",
        "input_hash": stable_sha256(config),
        "output_digest": output_digest,
        "mode": mode,
        "A_psi": A_psi if mode == "phi_to_psi" else None,
        "output_hashes": output_hashes,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    return LensingRunResult(
        kappa=kappa,
        gamma1=gamma1,
        gamma2=gamma2,
        summary=summary,
        certificate=certificate,
        psi=psi,
        alpha_x=alpha_x,
        alpha_y=alpha_y,
    )
