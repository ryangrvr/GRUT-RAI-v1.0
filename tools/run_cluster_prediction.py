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

from grut.cluster_packet import (
    com_positive,
    file_sha256,
    load_map,
    normalize_map,
    peak,
)
from grut.grut_phi_eff import phi_eff_from_phi_baryon, phi_from_sigma_baryon_fft
from grut.lensing import ARCMIN_PER_RAD, ARCSEC_PER_RAD, compute_lensing_from_psi, compute_psi_from_phi
from grut.utils import stable_sha256


def _parse_grid(value: str) -> List[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def _median(values: List[float]) -> float:
    if not values:
        return 0.0
    arr = np.array(values, dtype=float)
    return float(np.median(arr))


def _parse_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    value = str(value).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def _offsets_to_stats(offsets: List[float]) -> Dict[str, float]:
    arr = np.array(offsets, dtype=float)
    if arr.size == 0:
        return {"median": 0.0, "iqr": 0.0, "min": 0.0, "max": 0.0}
    q75, q25 = np.percentile(arr, [75, 25])
    return {
        "median": float(np.median(arr)),
        "iqr": float(q75 - q25),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }


def _basic_stats(values: np.ndarray) -> Dict[str, float]:
    return {
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values)),
    }


def _pearson_corr(a: np.ndarray, b: np.ndarray) -> float:
    a_flat = a.ravel()
    b_flat = b.ravel()
    if a_flat.size == 0:
        return 0.0
    a_mean = float(np.mean(a_flat))
    b_mean = float(np.mean(b_flat))
    a_center = a_flat - a_mean
    b_center = b_flat - b_mean
    denom = float(np.linalg.norm(a_center) * np.linalg.norm(b_center))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a_center, b_center) / denom)


def _radial_profile(
    values: np.ndarray,
    center: Tuple[float, float],
    pixel_scale_arcsec: float,
    nbins: int = 20,
    r_max_px: Optional[float] = None,
) -> Dict[str, List[float]]:
    y_idx, x_idx = np.indices(values.shape)
    dx = x_idx - float(center[0])
    dy = y_idx - float(center[1])
    r_px = np.sqrt(dx * dx + dy * dy)
    if r_max_px is None:
        r_max_px = float(np.max(r_px))
    bins = np.linspace(0.0, r_max_px, nbins + 1)
    bin_centers_px = 0.5 * (bins[:-1] + bins[1:])
    profile = []
    for i in range(nbins):
        mask = (r_px >= bins[i]) & (r_px < bins[i + 1])
        if not np.any(mask):
            profile.append(float("nan"))
        else:
            profile.append(float(np.mean(values[mask])))
    r_arcsec = (bin_centers_px * float(pixel_scale_arcsec)).tolist()
    return {"r_arcsec": r_arcsec, "mean": profile}


def _gamma_t_map(
    gamma1: np.ndarray,
    gamma2: np.ndarray,
    center: Tuple[float, float],
) -> np.ndarray:
    y_idx, x_idx = np.indices(gamma1.shape)
    dx = x_idx - float(center[0])
    dy = y_idx - float(center[1])
    phi = np.arctan2(dy, dx)
    cos2 = np.cos(2.0 * phi)
    sin2 = np.sin(2.0 * phi)
    return -(gamma1 * cos2 + gamma2 * sin2)


def _compute_centroid_kappa(
    kappa: np.ndarray,
    peak_mode: str,
    smoothing_sigma_px: float,
    threshold_frac: float,
) -> Dict[str, Any]:
    if peak_mode == "peak":
        return peak(kappa, smoothing_sigma_px=smoothing_sigma_px)
    if peak_mode == "com_positive_kappa":
        return com_positive(
            kappa,
            threshold_frac=threshold_frac,
            smoothing_sigma_px=smoothing_sigma_px,
        )
    raise ValueError(f"Unknown peak_mode: {peak_mode}")


def _predict_kappa(
    sigma_b_map: np.ndarray,
    *,
    fov_rad: float,
    kernel: str,
    response_model: str,
    alpha_mem: float,
    A_psi: float,
    band_gate_config: Optional[Dict[str, Any]],
) -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    Dict[str, Any],
]:
    phi_b = phi_from_sigma_baryon_fft(sigma_b_map, fov_rad, kernel=kernel)
    phi_eff, response_meta = phi_eff_from_phi_baryon(
        phi_b,
        alpha_mem,
        response_model=response_model,
        fov_rad=fov_rad,
        band_gate_config=band_gate_config,
        return_meta=True,
    )
    psi = compute_psi_from_phi(phi_eff, A_psi)
    alpha_x, alpha_y, kappa, gamma1, gamma2 = compute_lensing_from_psi(psi, fov_rad)
    return phi_b, phi_eff, psi, alpha_x, alpha_y, kappa, gamma1, gamma2, response_meta


def run_cluster_prediction(config: Dict[str, Any], outdir: str) -> Dict[str, Any]:
    sigma_baryon_path = config.get("sigma_baryon_path")
    if not sigma_baryon_path:
        raise ValueError("sigma_baryon_path is required")

    gas_path = config.get("gas_path")
    mode = config.get("mode", "predict_kappa")
    kernel = config.get("kernel", "k1")
    response_model = config.get("response_model", "identity")
    alpha_mem = float(config.get("alpha_mem", 0.333333333))
    A_psi = float(config.get("A_psi", 1.0))
    fov_arcmin = float(config.get("fov_arcmin", 20.0))
    smoothing_grid = config.get("smoothing_grid", [0.0])
    threshold_grid = config.get("threshold_grid", [0.1])
    peak_mode = config.get("peak_mode", "com_positive_kappa")
    gas_centroid_mode = config.get("gas_centroid_mode", "peak")
    normalize_mode = config.get("normalize_mode", "none")
    pixel_scale_arcsec = float(config.get("pixel_scale_arcsec", 1.0))
    band_gate_config = config.get("band_gate_config", None)
    compare_to_baseline = bool(config.get("compare_to_baseline", False))

    if response_model == "grut_gate_kspace_v0":
        gate_cfg = band_gate_config or {}
        k0_policy = str(gate_cfg.get("k0_policy", "r_smooth")).lower().strip()
        if k0_policy == "r_smooth" and "r_smooth_rad" not in gate_cfg:
            sigma_ref = _median([float(v) for v in smoothing_grid])
            pixel_scale_rad = float(pixel_scale_arcsec) / ARCSEC_PER_RAD
            r_smooth_rad = max(sigma_ref, 1.0) * pixel_scale_rad
            gate_cfg["r_smooth_rad"] = r_smooth_rad
            gate_cfg["sigma_ref_px"] = sigma_ref
            gate_cfg["pixel_scale_rad"] = pixel_scale_rad
        band_gate_config = gate_cfg

    if mode != "predict_kappa":
        raise ValueError(f"Unknown mode: {mode}")

    sigma_b_map = normalize_map(load_map(sigma_baryon_path), normalize_mode)
    gas_map = None
    if gas_path:
        gas_map = normalize_map(load_map(gas_path), normalize_mode)

    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    n = sigma_b_map.shape[0]
    fov_rad = fov_arcmin / ARCMIN_PER_RAD
    dtheta = fov_rad / float(n)
    k_min = (2.0 * np.pi) / fov_rad
    k_max = np.pi / dtheta

    (
        phi_b,
        phi_eff,
        psi,
        alpha_x,
        alpha_y,
        kappa,
        gamma1,
        gamma2,
        response_meta,
    ) = _predict_kappa(
        sigma_b_map,
        fov_rad=fov_rad,
        kernel=kernel,
        response_model=response_model,
        alpha_mem=alpha_mem,
        A_psi=A_psi,
        band_gate_config=band_gate_config,
    )

    np.save(outdir_path / "phi_b.npy", phi_b)
    np.save(outdir_path / "phi_eff.npy", phi_eff)
    np.save(outdir_path / "psi.npy", psi)
    np.save(outdir_path / "alpha_x.npy", alpha_x)
    np.save(outdir_path / "alpha_y.npy", alpha_y)
    np.save(outdir_path / "kappa.npy", kappa)
    np.save(outdir_path / "gamma1.npy", gamma1)
    np.save(outdir_path / "gamma2.npy", gamma2)

    offsets_rows: List[Dict[str, Any]] = []
    offset_magnitudes: List[float] = []
    offsets_available = gas_map is not None

    for smoothing_sigma in smoothing_grid:
        for threshold_frac in threshold_grid:
            lens_centroid = _compute_centroid_kappa(
                kappa,
                peak_mode,
                smoothing_sigma_px=float(smoothing_sigma),
                threshold_frac=float(threshold_frac),
            )

            if gas_map is None:
                continue

            if gas_centroid_mode == "peak":
                gas_centroid = peak(gas_map, smoothing_sigma_px=smoothing_sigma)
            elif gas_centroid_mode == "com_positive":
                gas_centroid = com_positive(
                    gas_map,
                    threshold_frac=threshold_frac,
                    smoothing_sigma_px=smoothing_sigma,
                )
            else:
                raise ValueError(f"Unknown gas_centroid_mode: {gas_centroid_mode}")

            dx_px = float(lens_centroid["x_px"] - gas_centroid["x_px"])
            dy_px = float(lens_centroid["y_px"] - gas_centroid["y_px"])
            offset_px = float(np.hypot(dx_px, dy_px))
            offset_arcsec = offset_px * pixel_scale_arcsec
            offset_arcmin = offset_arcsec / 60.0
            offset_magnitudes.append(offset_arcmin)

            offsets_rows.append(
                {
                    "smoothing_sigma_px": smoothing_sigma,
                    "threshold_frac": threshold_frac,
                    "lens_x_px": float(lens_centroid["x_px"]),
                    "lens_y_px": float(lens_centroid["y_px"]),
                    "gas_x_px": float(gas_centroid["x_px"]),
                    "gas_y_px": float(gas_centroid["y_px"]),
                    "dx_px": dx_px,
                    "dy_px": dy_px,
                    "offset_px": offset_px,
                    "offset_arcsec": offset_arcsec,
                    "offset_arcmin": offset_arcmin,
                }
            )

    offsets_path = outdir_path / "offsets.csv"
    fieldnames = [
        "smoothing_sigma_px",
        "threshold_frac",
        "lens_x_px",
        "lens_y_px",
        "gas_x_px",
        "gas_y_px",
        "dx_px",
        "dy_px",
        "offset_px",
        "offset_arcsec",
        "offset_arcmin",
    ]
    with offsets_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in offsets_rows:
            writer.writerow(row)

    stats = _offsets_to_stats(offset_magnitudes)
    k0_warnings: List[str] = []
    gate_meta = response_meta.get("grut_gate_kspace_v0") if isinstance(response_meta, dict) else None
    if gate_meta and "k0_value_used" in gate_meta:
        k0_value = float(gate_meta["k0_value_used"])
        if k0_value > 100.0 * k_max:
            k0_warnings.append("K0_TOO_LARGE_EFFECTIVELY_GLOBAL")
        if k0_value < 0.01 * k_min:
            k0_warnings.append("K0_TOO_SMALL_OVERFILTER")
    comparison = None
    comparison_profiles = None
    if compare_to_baseline:
        baseline_config = {
            "kernel": kernel,
            "response_model": "identity",
            "alpha_mem": alpha_mem,
            "A_psi": A_psi,
            "band_gate_config": None,
        }
        (
            _phi_b_base,
            _phi_eff_base,
            _psi_base,
            _alpha_x_base,
            _alpha_y_base,
            kappa_base,
            _gamma1_base,
            _gamma2_base,
            _response_meta_base,
        ) = _predict_kappa(
            sigma_b_map,
            fov_rad=fov_rad,
            kernel=baseline_config["kernel"],
            response_model=baseline_config["response_model"],
            alpha_mem=baseline_config["alpha_mem"],
            A_psi=baseline_config["A_psi"],
            band_gate_config=baseline_config["band_gate_config"],
        )

        centroid_base = _compute_centroid_kappa(
            kappa_base,
            peak_mode,
            smoothing_sigma_px=float(smoothing_grid[0]),
            threshold_frac=float(threshold_grid[0]),
        )
        centroid_grut = _compute_centroid_kappa(
            kappa,
            peak_mode,
            smoothing_sigma_px=float(smoothing_grid[0]),
            threshold_frac=float(threshold_grid[0]),
        )
        center_base = (float(centroid_base["x_px"]), float(centroid_base["y_px"]))
        center_grut = (float(centroid_grut["x_px"]), float(centroid_grut["y_px"]))
        dx_px = float(centroid_grut["x_px"] - centroid_base["x_px"])
        dy_px = float(centroid_grut["y_px"] - centroid_base["y_px"])
        shift_px = float(np.hypot(dx_px, dy_px))
        shift_arcsec = shift_px * pixel_scale_arcsec
        rms_kappa_diff = float(np.sqrt(np.mean((kappa - kappa_base) ** 2)))
        corr_kappa = _pearson_corr(kappa_base, kappa)
        comparison = {
            "baseline_response_model": "identity",
            "centroid_shift_px": shift_px,
            "centroid_shift_arcsec": shift_arcsec,
            "rms_kappa_diff": rms_kappa_diff,
            "corr_kappa": corr_kappa,
        }

        profile_base = _radial_profile(kappa_base, center_base, pixel_scale_arcsec)
        profile_grut = _radial_profile(kappa, center_grut, pixel_scale_arcsec)
        profile_diff = np.array(profile_grut["mean"], dtype=float) - np.array(
            profile_base["mean"], dtype=float
        )
        rms_profile_diff = float(np.sqrt(np.nanmean(profile_diff**2)))
        max_abs_profile_diff = float(np.nanmax(np.abs(profile_diff)))

        gamma_t_base = _gamma_t_map(_gamma1_base, _gamma2_base, center_base)
        gamma_t_grut = _gamma_t_map(gamma1, gamma2, center_grut)
        profile_gamma_t_base = _radial_profile(
            gamma_t_base, center_base, pixel_scale_arcsec
        )
        profile_gamma_t_grut = _radial_profile(
            gamma_t_grut, center_grut, pixel_scale_arcsec
        )

        comparison_profiles = {
            "kappa": {
                "r_arcsec": profile_base["r_arcsec"],
                "baseline_mean": profile_base["mean"],
                "grut_mean": profile_grut["mean"],
                "rms_profile_diff": rms_profile_diff,
                "max_abs_profile_diff": max_abs_profile_diff,
            },
            "gamma_t": {
                "r_arcsec": profile_gamma_t_base["r_arcsec"],
                "baseline_mean": profile_gamma_t_base["mean"],
                "grut_mean": profile_gamma_t_grut["mean"],
            },
        }
    summary = {
        "sigma_baryon_path": sigma_baryon_path,
        "gas_path": gas_path,
        "mode": mode,
        "kernel": kernel,
        "response_model": response_model,
        "response_meta": response_meta,
        "alpha_mem": alpha_mem,
        "A_psi": A_psi,
        "fov_arcmin": fov_arcmin,
        "fov_rad": fov_rad,
        "grid_n": n,
        "normalize_mode": normalize_mode,
        "pixel_scale_arcsec": pixel_scale_arcsec,
        "smoothing_grid": smoothing_grid,
        "threshold_grid": threshold_grid,
        "peak_mode": peak_mode,
        "gas_centroid_mode": gas_centroid_mode,
        "offsets_available": offsets_available,
        "offset_stats_arcmin": stats,
        "robust_offset_arcmin": stats["median"] if offsets_available else None,
        "offset_count": len(offset_magnitudes),
        "k_grid": {
            "dtheta_rad": dtheta,
            "k_min": float(k_min),
            "k_max": float(k_max),
        },
        "k0_warnings": k0_warnings,
        "comparison": comparison,
        "map_stats": {
            "phi_b": _basic_stats(phi_b),
            "phi_eff": _basic_stats(phi_eff),
            "kappa": _basic_stats(kappa),
        },
    }
    summary_path = outdir_path / "centroids_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    input_hash = stable_sha256(
        {
            "config": config,
            "files": {
                "sigma_baryon": file_sha256(sigma_baryon_path),
                "gas": file_sha256(gas_path) if gas_path else None,
            },
        }
    )
    output_hashes = {
        "phi_b.npy": file_sha256(str(outdir_path / "phi_b.npy")),
        "phi_eff.npy": file_sha256(str(outdir_path / "phi_eff.npy")),
        "psi.npy": file_sha256(str(outdir_path / "psi.npy")),
        "alpha_x.npy": file_sha256(str(outdir_path / "alpha_x.npy")),
        "alpha_y.npy": file_sha256(str(outdir_path / "alpha_y.npy")),
        "kappa.npy": file_sha256(str(outdir_path / "kappa.npy")),
        "gamma1.npy": file_sha256(str(outdir_path / "gamma1.npy")),
        "gamma2.npy": file_sha256(str(outdir_path / "gamma2.npy")),
        "centroids_summary.json": file_sha256(str(summary_path)),
        "offsets.csv": file_sha256(str(offsets_path)),
    }
    if compare_to_baseline:
        comparison_path = outdir_path / "comparison.json"
        comparison_path.write_text(json.dumps(comparison, indent=2))
        output_hashes["comparison.json"] = file_sha256(str(comparison_path))
        comparison_profiles_path = outdir_path / "comparison_profiles.json"
        comparison_profiles_path.write_text(json.dumps(comparison_profiles, indent=2))
        output_hashes["comparison_profiles.json"] = file_sha256(
            str(comparison_profiles_path)
        )
    output_digest = stable_sha256(output_hashes)

    certificate = {
        "tool_version": "v0.4B",
        "determinism_mode": "STRICT",
        "input_hash": input_hash,
        "output_digest": output_digest,
        "output_hashes": output_hashes,
        "grid_counts": {
            "smoothing": len(smoothing_grid),
            "threshold": len(threshold_grid),
        },
        "warnings": k0_warnings,
    }
    (outdir_path / "nis_prediction_certificate.json").write_text(
        json.dumps(certificate, indent=2)
    )

    return {"summary": summary, "certificate": certificate}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cluster prediction packet v0.4A")
    parser.add_argument("--sigma_baryon_path", required=True)
    parser.add_argument("--gas_path")
    parser.add_argument("--mode", default="predict_kappa")
    parser.add_argument("--kernel", choices=["k1", "k2"], default="k1")
    parser.add_argument(
        "--response_model",
        choices=["identity", "scaled", "band_gate", "grut_gate_kspace_v0"],
        default="identity",
    )
    parser.add_argument("--alpha_mem", type=float, default=0.333333333)
    parser.add_argument("--A_psi", type=float, default=1.0)
    parser.add_argument("--fov_arcmin", type=float, default=20.0)
    parser.add_argument("--outdir", default="artifacts/cluster_prediction_v0_4A")
    parser.add_argument("--smoothing_grid", default="0,1,2")
    parser.add_argument("--threshold_grid", default="0.0,0.1")
    parser.add_argument("--peak_mode", choices=["peak", "com_positive_kappa"], default="com_positive_kappa")
    parser.add_argument("--gas_centroid_mode", choices=["peak", "com_positive"], default="com_positive")
    parser.add_argument("--normalize_mode", choices=["none", "zscore", "minmax"], default="none")
    parser.add_argument("--pixel_scale_arcsec", type=float, default=1.0)
    parser.add_argument("--band_gate_low", type=float, default=None)
    parser.add_argument("--band_gate_high", type=float, default=None)
    parser.add_argument("--band_gate_order", type=int, default=None)
    parser.add_argument("--k0_policy", choices=["r_smooth", "fov"], default="r_smooth")
    parser.add_argument("--k0_value", type=float, default=None)
    parser.add_argument("--compare_to_baseline", nargs="?", const="true", default="false")
    args = parser.parse_args()

    band_gate_config = None
    if args.response_model == "band_gate":
        band_gate_config = {}
        if args.band_gate_low is not None:
            band_gate_config["k_low_frac"] = args.band_gate_low
        if args.band_gate_high is not None:
            band_gate_config["k_high_frac"] = args.band_gate_high
        if args.band_gate_order is not None:
            band_gate_config["order"] = args.band_gate_order

    if args.k0_value is not None:
        band_gate_config = band_gate_config or {}
        band_gate_config["k0_value"] = args.k0_value
    if args.k0_policy:
        band_gate_config = band_gate_config or {}
        band_gate_config["k0_policy"] = args.k0_policy

    r_smooth_rad = None
    if args.k0_policy == "r_smooth":
        smoothing_values = _parse_grid(args.smoothing_grid)
        sigma_ref = _median(smoothing_values)
        pixel_scale_rad = float(args.pixel_scale_arcsec) / ARCSEC_PER_RAD
        r_smooth_rad = max(sigma_ref, 1.0) * pixel_scale_rad
        band_gate_config = band_gate_config or {}
        band_gate_config["r_smooth_rad"] = r_smooth_rad
        band_gate_config["sigma_ref_px"] = sigma_ref
        band_gate_config["pixel_scale_rad"] = pixel_scale_rad

    config = {
        "sigma_baryon_path": args.sigma_baryon_path,
        "gas_path": args.gas_path,
        "mode": args.mode,
        "kernel": args.kernel,
        "response_model": args.response_model,
        "alpha_mem": args.alpha_mem,
        "A_psi": args.A_psi,
        "fov_arcmin": args.fov_arcmin,
        "smoothing_grid": _parse_grid(args.smoothing_grid),
        "threshold_grid": _parse_grid(args.threshold_grid),
        "peak_mode": args.peak_mode,
        "gas_centroid_mode": args.gas_centroid_mode,
        "normalize_mode": args.normalize_mode,
        "pixel_scale_arcsec": args.pixel_scale_arcsec,
        "band_gate_config": band_gate_config,
        "compare_to_baseline": _parse_bool(args.compare_to_baseline),
    }
    run_cluster_prediction(config, args.outdir)


if __name__ == "__main__":
    main()
