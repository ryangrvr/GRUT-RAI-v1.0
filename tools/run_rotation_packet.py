from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.canon import GRUTCanon
from grut.rotation_curves import (
    compute_v_bar,
    compute_v_grut,
    load_rotation_data,
    residual_metrics,
)
from grut.utils import stable_sha256
from grut.cluster_packet import file_sha256


def run_rotation_packet(config: Dict[str, Any], outdir: str) -> Dict[str, Any]:
    data_path = config.get("data_path")
    if not data_path:
        raise ValueError("data_path is required")

    response_model = config.get("response_model", "identity")
    alpha_mem = config.get("alpha_mem")
    if alpha_mem is None:
        try:
            canon = GRUTCanon("canon/grut_canon_v0.3.json")
            alpha_mem = canon.get_value("PARAM_ALPHA_MEM")
        except Exception:
            alpha_mem = 0.333333333
    alpha_mem = float(alpha_mem)
    ups_star = float(config.get("ups_star", 1.0))
    ups_bulge = float(config.get("ups_bulge", 1.0))
    r0_policy = str(config.get("r0_policy", "median_radius"))
    r0_kpc = config.get("r0_kpc")

    data = load_rotation_data(data_path)
    r_kpc = np.array(data["r_kpc"], dtype=float)
    v_obs = np.array(data["v_obs"], dtype=float)
    v_err = np.array(data.get("v_err", np.full_like(v_obs, np.nan)), dtype=float)
    if "v_gas" not in data or "v_star" not in data:
        raise ValueError("v_gas and v_star are required inputs")
    v_gas = np.array(data["v_gas"], dtype=float)
    v_star = np.array(data["v_star"], dtype=float)
    v_bulge = np.array(data["v_bulge"], dtype=float) if "v_bulge" in data else None

    v_bar = compute_v_bar(v_gas, v_star, v_bulge=v_bulge, ups_star=ups_star, ups_bulge=ups_bulge)
    v_grut, model_meta = compute_v_grut(
        v_bar,
        r_kpc,
        response_model=response_model,
        alpha_mem=alpha_mem,
        r0_policy=r0_policy,
        r0_kpc=r0_kpc,
    )
    baseline_metrics = residual_metrics(v_obs, v_bar, v_err=v_err, r_kpc=r_kpc)
    grut_metrics = residual_metrics(v_obs, v_grut, v_err=v_err, r_kpc=r_kpc)

    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    curves_path = outdir_path / "curves.csv"
    fieldnames = [
        "r_kpc",
        "v_obs",
        "v_err",
        "v_gas",
        "v_star",
        "v_bulge",
        "v_bar",
        "v_grut",
        "resid_bar",
        "resid_grut",
    ]
    with curves_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(r_kpc)):
            writer.writerow(
                {
                    "r_kpc": float(r_kpc[i]),
                    "v_obs": float(v_obs[i]),
                    "v_err": "" if np.isnan(v_err[i]) else float(v_err[i]),
                    "v_gas": float(v_gas[i]),
                    "v_star": float(v_star[i]),
                    "v_bulge": "" if v_bulge is None else float(v_bulge[i]),
                    "v_bar": float(v_bar[i]),
                    "v_grut": float(v_grut[i]),
                    "resid_bar": float(v_obs[i] - v_bar[i]),
                    "resid_grut": float(v_obs[i] - v_grut[i]),
                }
            )

    metrics_payload = {
        "response_model": response_model,
        "alpha_mem": alpha_mem,
        "r0_policy": model_meta.get("r0_policy"),
        "r0_value_used": model_meta.get("r0_kpc"),
        "ups_star": ups_star,
        "ups_bulge": ups_bulge,
        "baseline": baseline_metrics,
        "grut": grut_metrics,
        "data_stats": {
            "n_points": int(len(r_kpc)),
            "r_min": float(np.min(r_kpc)),
            "r_max": float(np.max(r_kpc)),
            "field_map": data.get("field_map", {}),
            "has_v_bulge": v_bulge is not None,
        },
    }
    metrics_path = outdir_path / "metrics.json"
    metrics_path.write_text(json.dumps(metrics_payload, indent=2))

    input_hash = stable_sha256(
        {
            "config": config,
            "data_hash": file_sha256(str(data_path)),
        }
    )
    output_hashes = {
        "curves.csv": file_sha256(str(curves_path)),
        "metrics.json": file_sha256(str(metrics_path)),
    }
    output_digest = stable_sha256(output_hashes)

    certificate = {
        "tool_version": "v0.1",
        "determinism_mode": "STRICT",
        "input_hash": input_hash,
        "output_digest": output_digest,
        "output_hashes": output_hashes,
        "config": {
            "response_model": response_model,
            "alpha_mem": alpha_mem,
            "r0_policy": r0_policy,
            "r0_kpc": r0_kpc,
            "ups_star": ups_star,
            "ups_bulge": ups_bulge,
        },
    }
    (outdir_path / "nis_rotation_certificate.json").write_text(
        json.dumps(certificate, indent=2)
    )

    return {"metrics": metrics_payload, "certificate": certificate}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run rotation curve packet v0.1")
    parser.add_argument("--data_path", required=True)
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
    parser.add_argument("--outdir", default="artifacts/rotation_packet_v0_1")
    args = parser.parse_args()

    galaxy_name = Path(args.data_path).stem
    outdir = Path(args.outdir) / galaxy_name
    config = {
        "data_path": args.data_path,
        "response_model": args.response_model,
        "alpha_mem": args.alpha_mem,
        "ups_star": args.ups_star,
        "ups_bulge": args.ups_bulge,
        "r0_policy": args.r0_policy,
        "r0_kpc": args.r0_kpc,
    }
    run_rotation_packet(config, str(outdir))


if __name__ == "__main__":
    main()
