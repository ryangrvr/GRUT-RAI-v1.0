from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.cluster_packet import com_positive, file_sha256, load_map, peak
from grut.grut_phi_eff import phi_eff_from_phi_baryon, phi_from_sigma_baryon_fft
from grut.lensing import ARCSEC_PER_RAD, ARCMIN_PER_RAD, compute_lensing_from_psi, compute_psi_from_phi
from grut.utils import stable_sha256


def _parse_grid(value: str) -> List[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def _median(values: List[float]) -> float:
    if not values:
        return 0.0
    arr = np.array(values, dtype=float)
    return float(np.median(arr))


def _profile_bins(nbins: int, r_max_px: float) -> np.ndarray:
    return np.linspace(0.0, float(r_max_px), nbins + 1)


def _radial_profile(values: np.ndarray, center: Tuple[float, float], bins: np.ndarray) -> List[float]:
    y_idx, x_idx = np.indices(values.shape)
    dx = x_idx - float(center[0])
    dy = y_idx - float(center[1])
    r_px = np.sqrt(dx * dx + dy * dy)
    profile: List[float] = []
    for i in range(len(bins) - 1):
        mask = (r_px >= bins[i]) & (r_px < bins[i + 1])
        if not np.any(mask):
            profile.append(float("nan"))
        else:
            profile.append(float(np.mean(values[mask])))
    return profile


def _gamma_t_map(gamma1: np.ndarray, gamma2: np.ndarray, center: Tuple[float, float]) -> np.ndarray:
    y_idx, x_idx = np.indices(gamma1.shape)
    dx = x_idx - float(center[0])
    dy = y_idx - float(center[1])
    phi = np.arctan2(dy, dx)
    cos2 = np.cos(2.0 * phi)
    sin2 = np.sin(2.0 * phi)
    return -(gamma1 * cos2 + gamma2 * sin2)


def _compute_center(values: np.ndarray, center_mode: str, threshold_frac: float) -> Tuple[float, float]:
    if center_mode == "peak":
        c = peak(values)
        return float(c["x_px"]), float(c["y_px"])
    if center_mode == "com_positive":
        c = com_positive(values, threshold_frac=threshold_frac)
        return float(c["x_px"]), float(c["y_px"])
    raise ValueError(f"Unknown center_mode: {center_mode}")


def _profile_metrics(a: List[float], b: List[float]) -> Dict[str, float]:
    arr_a = np.array(a, dtype=float)
    arr_b = np.array(b, dtype=float)
    diff = arr_b - arr_a
    return {
        "rms_diff": float(np.sqrt(np.nanmean(diff**2))),
        "max_abs_diff": float(np.nanmax(np.abs(diff))),
    }


def _predict_from_sigma(
    sigma_baryon: np.ndarray,
    *,
    fov_rad: float,
    kernel: str,
    response_model: str,
    alpha_mem: float,
    A_psi: float,
    band_gate_config: Optional[Dict[str, Any]],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    phi_b = phi_from_sigma_baryon_fft(sigma_baryon, fov_rad, kernel=kernel)
    phi_eff, _meta = phi_eff_from_phi_baryon(
        phi_b,
        alpha_mem,
        response_model=response_model,
        fov_rad=fov_rad,
        band_gate_config=band_gate_config,
        return_meta=True,
    )
    psi = compute_psi_from_phi(phi_eff, A_psi)
    _alpha_x, _alpha_y, kappa, gamma1, gamma2 = compute_lensing_from_psi(psi, fov_rad)
    return kappa, gamma1, gamma2


def run_cluster_profile_packet(config: Dict[str, Any], outdir: str) -> Dict[str, Any]:
    kappa_path = config.get("kappa_path")
    if not kappa_path:
        raise ValueError("kappa_path is required")

    gamma1_path = config.get("gamma1_path")
    gamma2_path = config.get("gamma2_path")
    sigma_baryon_path = config.get("sigma_baryon_path")

    center_mode = config.get("center_mode", "com_positive")
    threshold_frac = float(config.get("threshold_frac", 0.1))
    profile_bins = int(config.get("profile_bins", 20))
    r_max_arcsec = config.get("r_max_arcsec")
    compare_to_model = bool(config.get("compare_to_model", False))

    kernel = config.get("kernel", "k2")
    response_model = config.get("model_response", "grut_gate_kspace_v0")
    k0_policy = config.get("k0_policy", "r_smooth")
    k0_value = config.get("k0_value")
    smoothing_grid = config.get("smoothing_grid", [1.0])
    alpha_mem = float(config.get("alpha_mem", 0.333333333))
    A_psi = float(config.get("A_psi", 1.0))
    fov_arcmin = float(config.get("fov_arcmin", 20.0))
    pixel_scale_arcsec = float(config.get("pixel_scale_arcsec", 1.0))

    kappa_obs = load_map(kappa_path)
    gamma1_obs = load_map(gamma1_path) if gamma1_path else None
    gamma2_obs = load_map(gamma2_path) if gamma2_path else None

    n = kappa_obs.shape[0]
    fov_rad = fov_arcmin / ARCMIN_PER_RAD

    if r_max_arcsec is None:
        r_max_px = float(np.max(np.sqrt((np.indices(kappa_obs.shape)[0] - n / 2) ** 2)))
    else:
        r_max_px = float(r_max_arcsec) / pixel_scale_arcsec
    bins = _profile_bins(profile_bins, r_max_px)
    r_arcsec = (0.5 * (bins[:-1] + bins[1:]) * pixel_scale_arcsec).tolist()

    center_obs = _compute_center(kappa_obs, center_mode, threshold_frac)
    kappa_obs_profile = _radial_profile(kappa_obs, center_obs, bins)

    gamma_t_obs_profile = None
    if gamma1_obs is not None and gamma2_obs is not None:
        gamma_t_obs = _gamma_t_map(gamma1_obs, gamma2_obs, center_obs)
        gamma_t_obs_profile = _radial_profile(gamma_t_obs, center_obs, bins)

    if gamma_t_obs_profile is None:
        gamma_t_obs_profile = [None] * len(r_arcsec)

    profiles = {
        "r_arcsec": r_arcsec,
        "kappa_obs": kappa_obs_profile,
        "gamma_t_obs": gamma_t_obs_profile,
    }
    metrics: Dict[str, Any] = {}

    if compare_to_model:
        if not sigma_baryon_path:
            raise ValueError("sigma_baryon_path is required for compare_to_model")
        sigma_baryon = load_map(sigma_baryon_path)
        band_gate_config = {"k0_policy": k0_policy}
        if k0_value is not None:
            band_gate_config["k0_value"] = float(k0_value)
        if k0_policy == "r_smooth":
            pixel_scale_rad = float(pixel_scale_arcsec) / ARCSEC_PER_RAD
            sigma_ref = max(1.0, _median([float(v) for v in smoothing_grid]))
            r_smooth_rad = sigma_ref * pixel_scale_rad
            band_gate_config["r_smooth_rad"] = r_smooth_rad
            band_gate_config["sigma_ref_px"] = sigma_ref
            band_gate_config["pixel_scale_rad"] = pixel_scale_rad

        kappa_base, gamma1_base, gamma2_base = _predict_from_sigma(
            sigma_baryon,
            fov_rad=fov_rad,
            kernel=kernel,
            response_model="identity",
            alpha_mem=alpha_mem,
            A_psi=A_psi,
            band_gate_config=None,
        )
        kappa_grut, gamma1_grut, gamma2_grut = _predict_from_sigma(
            sigma_baryon,
            fov_rad=fov_rad,
            kernel=kernel,
            response_model=response_model,
            alpha_mem=alpha_mem,
            A_psi=A_psi,
            band_gate_config=band_gate_config,
        )

        center_base = _compute_center(kappa_base, center_mode, threshold_frac)
        center_grut = _compute_center(kappa_grut, center_mode, threshold_frac)
        kappa_base_profile = _radial_profile(kappa_base, center_base, bins)
        kappa_grut_profile = _radial_profile(kappa_grut, center_grut, bins)

        gamma_t_base = _gamma_t_map(gamma1_base, gamma2_base, center_base)
        gamma_t_grut = _gamma_t_map(gamma1_grut, gamma2_grut, center_grut)
        gamma_t_base_profile = _radial_profile(gamma_t_base, center_base, bins)
        gamma_t_grut_profile = _radial_profile(gamma_t_grut, center_grut, bins)

        profiles.update(
            {
                "kappa_baseline": kappa_base_profile,
                "kappa_grut": kappa_grut_profile,
                "kappa_ratio": (np.array(kappa_grut_profile) / np.array(kappa_base_profile)).tolist(),
                "gamma_t_baseline": gamma_t_base_profile,
                "gamma_t_grut": gamma_t_grut_profile,
                "gamma_t_ratio": (np.array(gamma_t_grut_profile) / np.array(gamma_t_base_profile)).tolist(),
            }
        )
        metrics["kappa"] = _profile_metrics(kappa_base_profile, kappa_grut_profile)
        metrics["gamma_t"] = _profile_metrics(gamma_t_base_profile, gamma_t_grut_profile)

    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    profiles_path = outdir_path / "profiles.csv"
    fieldnames = [
        "r_arcsec",
        "kappa_obs",
        "kappa_baseline",
        "kappa_grut",
        "kappa_ratio",
        "gamma_t_obs",
        "gamma_t_baseline",
        "gamma_t_grut",
        "gamma_t_ratio",
    ]
    with profiles_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(r_arcsec)):
            writer.writerow(
                {
                    "r_arcsec": r_arcsec[i],
                    "kappa_obs": profiles.get("kappa_obs")[i],
                    "kappa_baseline": profiles.get("kappa_baseline", [None] * len(r_arcsec))[i],
                    "kappa_grut": profiles.get("kappa_grut", [None] * len(r_arcsec))[i],
                    "kappa_ratio": profiles.get("kappa_ratio", [None] * len(r_arcsec))[i],
                    "gamma_t_obs": profiles.get("gamma_t_obs", [None] * len(r_arcsec))[i],
                    "gamma_t_baseline": profiles.get("gamma_t_baseline", [None] * len(r_arcsec))[i],
                    "gamma_t_grut": profiles.get("gamma_t_grut", [None] * len(r_arcsec))[i],
                    "gamma_t_ratio": profiles.get("gamma_t_ratio", [None] * len(r_arcsec))[i],
                }
            )

    metrics_path = outdir_path / "profile_metrics.json"
    metrics_payload = {
        "center_mode": center_mode,
        "threshold_frac": threshold_frac,
        "profile_bins": profile_bins,
        "r_max_arcsec": r_max_arcsec,
        "compare_to_model": compare_to_model,
        "model_response": response_model,
        "smoothing_grid": smoothing_grid,
        "k0_policy": k0_policy,
        "k0_value": k0_value,
        "metrics": metrics,
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2))

    output_hashes = {
        "profiles.csv": file_sha256(str(profiles_path)),
        "profile_metrics.json": file_sha256(str(metrics_path)),
    }
    input_hash = stable_sha256(
        {
            "config": config,
            "files": {
                "kappa": file_sha256(kappa_path),
                "gamma1": file_sha256(gamma1_path) if gamma1_path else None,
                "gamma2": file_sha256(gamma2_path) if gamma2_path else None,
                "sigma_baryon": file_sha256(sigma_baryon_path) if sigma_baryon_path else None,
            },
        }
    )
    output_digest = stable_sha256(output_hashes)

    certificate = {
        "tool_version": "v0.5",
        "determinism_mode": "STRICT",
        "input_hash": input_hash,
        "output_digest": output_digest,
        "output_hashes": output_hashes,
    }
    (outdir_path / "nis_profile_certificate.json").write_text(json.dumps(certificate, indent=2))

    return {"profiles": profiles, "metrics": metrics_payload, "certificate": certificate}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cluster profile falsifier packet v0.5")
    parser.add_argument("--kappa_path", required=True)
    parser.add_argument("--gamma1_path")
    parser.add_argument("--gamma2_path")
    parser.add_argument("--sigma_baryon_path")
    parser.add_argument("--center_mode", choices=["peak", "com_positive"], default="com_positive")
    parser.add_argument("--threshold_frac", type=float, default=0.1)
    parser.add_argument("--profile_bins", type=int, default=20)
    parser.add_argument("--r_max_arcsec", type=float, default=None)
    parser.add_argument("--compare_to_model", action="store_true")
    parser.add_argument("--kernel", choices=["k1", "k2"], default="k2")
    parser.add_argument("--model_response", choices=["identity", "grut_gate_kspace_v0"], default="grut_gate_kspace_v0")
    parser.add_argument("--k0_policy", choices=["r_smooth", "fov"], default="r_smooth")
    parser.add_argument("--k0_value", type=float, default=None)
    parser.add_argument("--smoothing_grid", default="1")
    parser.add_argument("--alpha_mem", type=float, default=0.333333333)
    parser.add_argument("--A_psi", type=float, default=1.0)
    parser.add_argument("--fov_arcmin", type=float, default=20.0)
    parser.add_argument("--pixel_scale_arcsec", type=float, default=1.0)
    parser.add_argument("--outdir", default="artifacts/cluster_profile_v0_5")
    args = parser.parse_args()

    config = {
        "kappa_path": args.kappa_path,
        "gamma1_path": args.gamma1_path,
        "gamma2_path": args.gamma2_path,
        "sigma_baryon_path": args.sigma_baryon_path,
        "center_mode": args.center_mode,
        "threshold_frac": args.threshold_frac,
        "profile_bins": args.profile_bins,
        "r_max_arcsec": args.r_max_arcsec,
        "compare_to_model": args.compare_to_model,
        "kernel": args.kernel,
        "model_response": args.model_response,
        "k0_policy": args.k0_policy,
        "k0_value": args.k0_value,
        "smoothing_grid": _parse_grid(args.smoothing_grid),
        "alpha_mem": args.alpha_mem,
        "A_psi": args.A_psi,
        "fov_arcmin": args.fov_arcmin,
        "pixel_scale_arcsec": args.pixel_scale_arcsec,
    }
    run_cluster_profile_packet(config, args.outdir)


if __name__ == "__main__":
    main()
