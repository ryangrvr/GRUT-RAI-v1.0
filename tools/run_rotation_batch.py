from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.utils import stable_sha256
from grut.cluster_packet import file_sha256
from tools.run_rotation_packet import run_rotation_packet


def run_rotation_batch(paths: List[Path], config: Dict[str, Any], outdir: Path) -> Dict[str, Any]:
    outdir.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []

    for path in sorted(paths, key=lambda p: p.name):
        galaxy_name = path.stem
        packet_out = outdir / galaxy_name
        packet_config = dict(config)
        packet_config["data_path"] = str(path)
        result = run_rotation_packet(packet_config, str(packet_out))
        metrics = result["metrics"]
        baseline = metrics["baseline"]
        grut = metrics["grut"]
        rows.append(
            {
                "galaxy": galaxy_name,
                "n_points": metrics["data_stats"]["n_points"],
                "baseline_rms": baseline["rms_residual"],
                "grut_rms": grut["rms_residual"],
                "baseline_mean_abs_frac": baseline["mean_abs_frac_residual"],
                "grut_mean_abs_frac": grut["mean_abs_frac_residual"],
                "inner_rms_baseline": baseline["inner_disk_rms"],
                "inner_rms_grut": grut["inner_disk_rms"],
                "outer_rms_baseline": baseline["outer_disk_rms"],
                "outer_rms_grut": grut["outer_disk_rms"],
                "input_hash": result["certificate"]["input_hash"],
                "output_digest": result["certificate"]["output_digest"],
            }
        )

    summary_path = outdir / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "galaxy",
                "n_points",
                "baseline_rms",
                "grut_rms",
                "baseline_mean_abs_frac",
                "grut_mean_abs_frac",
                "inner_rms_baseline",
                "inner_rms_grut",
                "outer_rms_baseline",
                "outer_rms_grut",
                "input_hash",
                "output_digest",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    manifest = {
        "response_model": config.get("response_model"),
        "alpha_mem": config.get("alpha_mem"),
        "ups_star": config.get("ups_star"),
        "ups_bulge": config.get("ups_bulge"),
        "r0_policy": config.get("r0_policy"),
        "r0_kpc": config.get("r0_kpc"),
        "files": [p.name for p in sorted(paths, key=lambda p: p.name)],
        "summary_csv": str(summary_path),
        "summary_sha256": file_sha256(str(summary_path)),
    }
    manifest["summary_hash"] = stable_sha256(manifest)
    (outdir / "batch_manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Run rotation curve batch")
    parser.add_argument("--datadir", required=True)
    parser.add_argument("--glob", default="*.csv")
    parser.add_argument(
        "--response_model",
        choices=["identity", "radial_gate_v0", "memory_scale_boost_v0"],
        default="identity",
    )
    parser.add_argument("--alpha_mem", type=float, default=0.333333333)
    parser.add_argument("--ups_star", type=float, default=1.0)
    parser.add_argument("--ups_bulge", type=float, default=1.0)
    parser.add_argument("--r0_policy", choices=["median_radius", "fixed_kpc"], default="median_radius")
    parser.add_argument("--r0_kpc", type=float, default=None)
    parser.add_argument("--outdir", default="artifacts/rotation_batch_v0_1")
    args = parser.parse_args()

    data_dir = Path(args.datadir)
    paths = list(sorted(data_dir.glob(args.glob)))
    config = {
        "response_model": args.response_model,
        "alpha_mem": args.alpha_mem,
        "ups_star": args.ups_star,
        "ups_bulge": args.ups_bulge,
        "r0_policy": args.r0_policy,
        "r0_kpc": args.r0_kpc,
    }
    run_rotation_batch(paths, config, Path(args.outdir))


if __name__ == "__main__":
    main()
