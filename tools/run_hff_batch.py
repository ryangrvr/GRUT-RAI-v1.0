from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.cluster_packet import file_sha256
from grut.utils import stable_sha256


def _run_cmd(cmd: List[str]) -> None:
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def _parse_models(value: str) -> List[str]:
    return [m.strip() for m in value.split(",") if m.strip()]


def build_fetch_cmd(cluster: str, model: str) -> List[str]:
    return [
        sys.executable,
        "tools/fetch_hff_lensmodel.py",
        "--cluster",
        cluster,
        "--model",
        model,
    ]


def build_packet_cmd(cluster: str, model: str) -> List[str]:
    return [
        sys.executable,
        "tools/build_cluster_evidence_packet.py",
        "--cluster",
        cluster,
        "--model",
        model,
    ]


def run_hff_batch(cluster: str, models: List[str], outroot: Path) -> Dict[str, str]:
    outroot.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, str]] = []

    for model in sorted(models):
        _run_cmd(build_fetch_cmd(cluster, model))
        _run_cmd(build_packet_cmd(cluster, model))

        packet_dir = Path("artifacts/evidence_cluster_v0_6A") / cluster / model
        profile_metrics = json.loads(
            (packet_dir / "outputs/profile_packet/profile_metrics.json").read_text()
        )
        profile_cert = json.loads(
            (packet_dir / "outputs/profile_packet/nis_profile_certificate.json").read_text()
        )
        provenance = json.loads(
            (Path("artifacts/hff_raw") / cluster / model / "PROVENANCE.json").read_text()
        )

        metrics = profile_metrics.get("metrics", {})
        kappa = metrics.get("kappa", {})
        gamma = metrics.get("gamma_t", {})

        rows.append(
            {
                "model": model,
                "kappa_rms_diff": str(kappa.get("rms_diff")),
                "kappa_max_abs_diff": str(kappa.get("max_abs_diff")),
                "gamma_rms_diff": str(gamma.get("rms_diff")),
                "gamma_max_abs_diff": str(gamma.get("max_abs_diff")),
                "provenance_hash": str(provenance.get("stable_provenance_hash")),
                "input_hash": str(profile_cert.get("input_hash")),
                "output_digest": str(profile_cert.get("output_digest")),
            }
        )

    csv_path = outroot / "hff_batch_summary.csv"
    fieldnames = [
        "model",
        "kappa_rms_diff",
        "kappa_max_abs_diff",
        "gamma_rms_diff",
        "gamma_max_abs_diff",
        "provenance_hash",
        "input_hash",
        "output_digest",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    summary = {
        "cluster": cluster,
        "models": sorted(models),
        "summary_csv": str(csv_path),
        "summary_csv_sha256": file_sha256(str(csv_path)),
        "summary_hash": stable_sha256({"cluster": cluster, "models": sorted(models)}),
    }
    (outroot / "hff_batch_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run HFF batch evidence packets")
    parser.add_argument("--cluster", default="A2744")
    parser.add_argument("--models", default="CATS,GLAFIC,Sharon")
    parser.add_argument("--outroot", default="artifacts/evidence_cluster_v0_6A_batch/A2744")
    args = parser.parse_args()

    models = _parse_models(args.models)
    run_hff_batch(args.cluster, models, Path(args.outroot))


if __name__ == "__main__":
    main()
