from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.canon import GRUTCanon
from grut.cluster_packet import (
    com_positive,
    file_sha256,
    load_map,
    normalize_map,
    peak,
)
from grut.utils import stable_sha256

KPC_PER_M = 1.0 / 3.085677581e19


def _parse_grid(value: str) -> List[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


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


def _centroid_for_mode(
    values: np.ndarray,
    mode: str,
    smoothing_sigma_px: float,
    threshold_frac: float,
) -> Dict[str, Any]:
    if mode == "peak":
        return peak(values, smoothing_sigma_px=smoothing_sigma_px)
    if mode == "com_positive_kappa" or mode == "com_positive":
        return com_positive(
            values,
            threshold_frac=threshold_frac,
            smoothing_sigma_px=smoothing_sigma_px,
        )
    raise ValueError(f"Unknown centroid mode: {mode}")


def _load_tau0_seconds(canon_path: str) -> float:
    canon = GRUTCanon(canon_path)
    tau0_years = canon.get_value("CONST_TAU_0")
    return float(tau0_years) * 365.25 * 24.0 * 3600.0


def run_cluster_offset_packet(config: Dict[str, Any], outdir: str) -> Dict[str, Any]:
    kappa_path = config.get("kappa_path")
    gas_path = config.get("gas_path")
    if not kappa_path or not gas_path:
        raise ValueError("kappa_path and gas_path are required")

    smoothing_grid = config.get("smoothing_grid", [0.0])
    threshold_grid = config.get("threshold_grid", [0.1])
    peak_mode = config.get("peak_mode", "com_positive_kappa")
    gas_centroid_mode = config.get("gas_centroid_mode", "com_positive")
    normalize_mode = config.get("normalize_mode", "none")
    pixel_scale_arcsec = config.get("pixel_scale_arcsec")
    if pixel_scale_arcsec is None:
        raise ValueError("pixel_scale_arcsec is required when no WCS is available")
    pixel_scale_arcsec = float(pixel_scale_arcsec)

    kappa_raw = load_map(kappa_path)
    gas_raw = load_map(gas_path)
    nan_frac_kappa = float(np.isnan(kappa_raw).mean())
    nan_frac_gas = float(np.isnan(gas_raw).mean())
    kappa_map = normalize_map(np.nan_to_num(kappa_raw, nan=0.0), normalize_mode)
    gas_map = normalize_map(np.nan_to_num(gas_raw, nan=0.0), normalize_mode)

    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    offsets_rows: List[Dict[str, Any]] = []
    offset_magnitudes_arcmin: List[float] = []
    dx_arcsec_values: List[float] = []
    dy_arcsec_values: List[float] = []

    for smoothing_sigma in smoothing_grid:
        for threshold_frac in threshold_grid:
            lens_centroid = _centroid_for_mode(
                kappa_map,
                peak_mode,
                smoothing_sigma_px=float(smoothing_sigma),
                threshold_frac=float(threshold_frac),
            )
            gas_centroid = _centroid_for_mode(
                gas_map,
                gas_centroid_mode,
                smoothing_sigma_px=float(smoothing_sigma),
                threshold_frac=float(threshold_frac),
            )

            dx_px = float(lens_centroid["x_px"] - gas_centroid["x_px"])
            dy_px = float(lens_centroid["y_px"] - gas_centroid["y_px"])
            offset_px = float(np.hypot(dx_px, dy_px))
            offset_arcsec = offset_px * pixel_scale_arcsec
            offset_arcmin = offset_arcsec / 60.0

            dx_arcsec = dx_px * pixel_scale_arcsec
            dy_arcsec = dy_px * pixel_scale_arcsec

            offset_magnitudes_arcmin.append(offset_arcmin)
            dx_arcsec_values.append(dx_arcsec)
            dy_arcsec_values.append(dy_arcsec)

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
    with offsets_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(offsets_rows[0].keys()))
        writer.writeheader()
        for row in offsets_rows:
            writer.writerow(row)

    stats = _offsets_to_stats(offset_magnitudes_arcmin)
    robust_dx_arcsec = float(np.median(dx_arcsec_values)) if dx_arcsec_values else 0.0
    robust_dy_arcsec = float(np.median(dy_arcsec_values)) if dy_arcsec_values else 0.0
    robust_offset_arcsec = stats["median"] * 60.0

    summary = {
        "kappa_path": kappa_path,
        "gas_path": gas_path,
        "normalize_mode": normalize_mode,
        "pixel_scale_arcsec": pixel_scale_arcsec,
        "smoothing_grid": smoothing_grid,
        "threshold_grid": threshold_grid,
        "peak_mode": peak_mode,
        "gas_centroid_mode": gas_centroid_mode,
        "offset_stats_arcmin": stats,
        "robust_offset_arcmin": stats["median"],
        "robust_offset_arcsec": robust_offset_arcsec,
        "robust_vector_arcsec": {
            "dx_arcsec": robust_dx_arcsec,
            "dy_arcsec": robust_dy_arcsec,
        },
        "offset_count": len(offset_magnitudes_arcmin),
        "nan_fraction": {
            "kappa": nan_frac_kappa,
            "gas": nan_frac_gas,
        },
    }
    summary_path = outdir_path / "centroids_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    prediction_path = None
    v_coll_kms = config.get("v_coll_kms")
    prediction = None
    if v_coll_kms is not None:
        v_coll_kms = float(v_coll_kms)
        tau0_s = config.get("tau0_s")
        if tau0_s is None:
            tau0_s = _load_tau0_seconds(str(config.get("canon_path", "canon/grut_canon_v0.3.json")))
        tau0_s = float(tau0_s)

        angle_deg = config.get("v_coll_angle_deg")
        if angle_deg is None:
            angle_deg = 0.0
        angle_rad = math.radians(float(angle_deg))

        delta_pred_kpc = v_coll_kms * 1000.0 * tau0_s * KPC_PER_M
        pred_dx_kpc = delta_pred_kpc * math.cos(angle_rad)
        pred_dy_kpc = delta_pred_kpc * math.sin(angle_rad)

        kpc_per_arcsec = config.get("kpc_per_arcsec")
        delta_obs_kpc = None
        delta_residual = None
        delta_obs_arcsec = robust_offset_arcsec
        if kpc_per_arcsec is not None:
            kpc_per_arcsec = float(kpc_per_arcsec)
            delta_obs_kpc = delta_obs_arcsec * kpc_per_arcsec
            delta_residual = abs(delta_obs_kpc - delta_pred_kpc)

        prediction = {
            "v_coll_kms": v_coll_kms,
            "v_coll_angle_deg": float(angle_deg),
            "tau0_s": tau0_s,
            "delta_pred_kpc": delta_pred_kpc,
            "pred_vector_kpc": {"dx_kpc": pred_dx_kpc, "dy_kpc": pred_dy_kpc},
            "delta_obs_arcsec": delta_obs_arcsec,
            "kpc_per_arcsec": kpc_per_arcsec,
            "delta_obs_kpc": delta_obs_kpc,
            "delta_residual": delta_residual,
        }
        prediction_path = outdir_path / "prediction_summary.json"
        prediction_path.write_text(json.dumps(prediction, indent=2))

    input_hash = stable_sha256(
        {
            "config": config,
            "files": {
                "kappa": file_sha256(kappa_path),
                "gas": file_sha256(gas_path),
            },
        }
    )
    output_hashes = {
        "centroids_summary.json": file_sha256(str(summary_path)),
        "offsets.csv": file_sha256(str(offsets_path)),
    }
    if prediction_path is not None:
        output_hashes["prediction_summary.json"] = file_sha256(str(prediction_path))
    output_digest = stable_sha256(output_hashes)

    certificate = {
        "tool_version": "v0.1",
        "determinism_mode": "STRICT",
        "input_hash": input_hash,
        "output_digest": output_digest,
        "output_hashes": output_hashes,
        "config": {
            "peak_mode": peak_mode,
            "gas_centroid_mode": gas_centroid_mode,
            "normalize_mode": normalize_mode,
            "pixel_scale_arcsec": pixel_scale_arcsec,
            "smoothing_grid": smoothing_grid,
            "threshold_grid": threshold_grid,
            "v_coll_kms": v_coll_kms,
            "v_coll_angle_deg": config.get("v_coll_angle_deg"),
            "kpc_per_arcsec": config.get("kpc_per_arcsec"),
        },
    }
    (outdir_path / "nis_cluster_offset_certificate.json").write_text(
        json.dumps(certificate, indent=2)
    )

    return {"summary": summary, "prediction": prediction, "certificate": certificate}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cluster gas offset packet v0.1")
    parser.add_argument("--kappa_path", required=True)
    parser.add_argument("--gas_path", required=True)
    parser.add_argument("--pixel_scale_arcsec", type=float, default=None)
    parser.add_argument("--smoothing_grid", default="0,1,2,3")
    parser.add_argument("--threshold_grid", default="0.05,0.1,0.2")
    parser.add_argument("--peak_mode", choices=["peak", "com_positive_kappa"], default="com_positive_kappa")
    parser.add_argument("--gas_centroid_mode", choices=["peak", "com_positive"], default="com_positive")
    parser.add_argument("--normalize_mode", choices=["none", "zscore", "minmax"], default="none")
    parser.add_argument("--v_coll_kms", type=float, default=None)
    parser.add_argument("--v_coll_angle_deg", type=float, default=None)
    parser.add_argument("--tau0_s", type=float, default=None)
    parser.add_argument("--cluster_redshift", type=float, default=None)
    parser.add_argument("--kpc_per_arcsec", type=float, default=None)
    parser.add_argument("--canon_path", default="canon/grut_canon_v0.3.json")
    parser.add_argument("--outdir", default="artifacts/cluster_offset_packet_v0_1")
    args = parser.parse_args()

    config = {
        "kappa_path": args.kappa_path,
        "gas_path": args.gas_path,
        "pixel_scale_arcsec": args.pixel_scale_arcsec,
        "smoothing_grid": _parse_grid(args.smoothing_grid),
        "threshold_grid": _parse_grid(args.threshold_grid),
        "peak_mode": args.peak_mode,
        "gas_centroid_mode": args.gas_centroid_mode,
        "normalize_mode": args.normalize_mode,
        "v_coll_kms": args.v_coll_kms,
        "v_coll_angle_deg": args.v_coll_angle_deg,
        "tau0_s": args.tau0_s,
        "cluster_redshift": args.cluster_redshift,
        "kpc_per_arcsec": args.kpc_per_arcsec,
        "canon_path": args.canon_path,
    }
    run_cluster_offset_packet(config, args.outdir)


if __name__ == "__main__":
    main()
