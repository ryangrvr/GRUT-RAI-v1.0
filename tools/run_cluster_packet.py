from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.cluster_packet import (
    aperture_com,
    com_positive,
    file_sha256,
    load_map,
    normalize_map,
    peak,
)
from grut.utils import stable_sha256


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


def run_cluster_packet(config: Dict[str, Any], outdir: str) -> Dict[str, Any]:
    kappa_path = config.get("kappa_path")
    gas_path = config.get("gas_path")
    if not kappa_path or not gas_path:
        raise ValueError("kappa_path and gas_path are required")

    smoothing_grid = config.get("smoothing_grid", [0.0])
    threshold_grid = config.get("threshold_grid", [0.1])
    peak_mode = config.get("peak_mode", "com_positive_kappa")
    gas_centroid_mode = config.get("gas_centroid_mode", "peak")
    normalize_mode = config.get("normalize_mode", "none")
    pixel_scale_arcsec = float(config.get("pixel_scale_arcsec", 1.0))

    kappa_map = normalize_map(load_map(kappa_path), normalize_mode)
    gas_map = normalize_map(load_map(gas_path), normalize_mode)

    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    offsets_rows: List[Dict[str, Any]] = []
    offset_magnitudes = []

    for smoothing_sigma in smoothing_grid:
        for threshold_frac in threshold_grid:
            if peak_mode == "peak":
                lens_centroid = peak(kappa_map, smoothing_sigma_px=smoothing_sigma)
            elif peak_mode == "com_positive_kappa":
                lens_centroid = com_positive(
                    kappa_map,
                    threshold_frac=threshold_frac,
                    smoothing_sigma_px=smoothing_sigma,
                )
            else:
                raise ValueError(f"Unknown peak_mode: {peak_mode}")

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
    with offsets_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(offsets_rows[0].keys()))
        writer.writeheader()
        for row in offsets_rows:
            writer.writerow(row)

    stats = _offsets_to_stats(offset_magnitudes)
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
        "offset_count": len(offset_magnitudes),
    }
    summary_path = outdir_path / "centroids_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

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
    output_digest = stable_sha256(output_hashes)

    certificate = {
        "tool_version": "v0.3",
        "determinism_mode": "STRICT",
        "input_hash": input_hash,
        "output_digest": output_digest,
        "output_hashes": output_hashes,
        "grid_counts": {
            "smoothing": len(smoothing_grid),
            "threshold": len(threshold_grid),
        },
    }
    (outdir_path / "nis_cluster_certificate.json").write_text(
        json.dumps(certificate, indent=2)
    )

    return {"summary": summary, "certificate": certificate}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cluster packet v0.3")
    parser.add_argument("--kappa_path", required=True)
    parser.add_argument("--gas_path", required=True)
    parser.add_argument("--outdir", default="artifacts/cluster_packet_v0_3")
    parser.add_argument("--smoothing_grid", default="0,1,2,3")
    parser.add_argument("--threshold_grid", default="0.05,0.1,0.2")
    parser.add_argument("--peak_mode", choices=["peak", "com_positive_kappa"], default="com_positive_kappa")
    parser.add_argument("--gas_centroid_mode", choices=["peak", "com_positive"], default="peak")
    parser.add_argument("--normalize_mode", choices=["none", "zscore", "minmax"], default="none")
    parser.add_argument("--pixel_scale_arcsec", type=float, default=1.0)
    args = parser.parse_args()

    config = {
        "kappa_path": args.kappa_path,
        "gas_path": args.gas_path,
        "smoothing_grid": _parse_grid(args.smoothing_grid),
        "threshold_grid": _parse_grid(args.threshold_grid),
        "peak_mode": args.peak_mode,
        "gas_centroid_mode": args.gas_centroid_mode,
        "normalize_mode": args.normalize_mode,
        "pixel_scale_arcsec": args.pixel_scale_arcsec,
    }
    run_cluster_packet(config, args.outdir)


if __name__ == "__main__":
    main()