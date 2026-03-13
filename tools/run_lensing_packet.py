from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.canon import GRUTCanon
from grut.lensing import run_lensing


def run_lensing_packet(config: Dict[str, Any], outdir: str) -> Dict[str, Any]:
    canon_hash = "N/A"
    canon_path = config.get("canon_path")
    if canon_path:
        canon = GRUTCanon(canon_path)
        canon_hash = canon.meta.get("canon_hash")

    result = run_lensing(config, canon_hash=canon_hash)

    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    np.save(outdir_path / "kappa.npy", result.kappa)
    np.save(outdir_path / "gamma1.npy", result.gamma1)
    np.save(outdir_path / "gamma2.npy", result.gamma2)
    if result.psi is not None:
        np.save(outdir_path / "psi.npy", result.psi)
    if result.alpha_x is not None:
        np.save(outdir_path / "alpha_x.npy", result.alpha_x)
    if result.alpha_y is not None:
        np.save(outdir_path / "alpha_y.npy", result.alpha_y)

    (outdir_path / "summary.json").write_text(json.dumps(result.summary, indent=2))
    (outdir_path / "nis_lensing_certificate.json").write_text(
        json.dumps(result.certificate, indent=2)
    )
    return {"summary": result.summary, "certificate": result.certificate}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run lensing packet v0.1")
    parser.add_argument("--n", type=int, default=256)
    parser.add_argument("--fov_arcmin", type=float, default=20.0)
    parser.add_argument("--sigma_crit", type=float, default=1.0)
    parser.add_argument("--mode", choices=["sigma_to_kappa", "phi_to_psi"], default="sigma_to_kappa")
    parser.add_argument("--preset", choices=["single_halo", "bullet_toy"], default="single_halo")
    parser.add_argument(
        "--phi_preset",
        choices=["point_mass", "bullet_phi_toy", "from_npy"],
        default="bullet_phi_toy",
    )
    parser.add_argument("--phi_npy_path", default=None)
    parser.add_argument("--A_psi", type=float, default=1.0)
    parser.add_argument("--phi_mass_amp", type=float, default=1e-6)
    parser.add_argument("--phi_gas_amp", type=float, default=7e-7)
    parser.add_argument("--pad_factor", type=int, default=1)
    parser.add_argument(
        "--peak_mode",
        choices=["max_kappa", "smoothed_max_kappa", "com_positive_kappa"],
        default="max_kappa",
    )
    parser.add_argument("--smoothing_sigma_px", type=float, default=0.0)
    parser.add_argument("--delta_arcmin", type=float, default=2.0)
    parser.add_argument("--outdir", default="artifacts/lensing_packet_v0_1")
    parser.add_argument("--canon_path", default=None)
    args = parser.parse_args()

    config = {
        "n": args.n,
        "fov_arcmin": args.fov_arcmin,
        "sigma_crit": args.sigma_crit,
        "mode": args.mode,
        "preset": args.preset,
        "phi_preset": args.phi_preset,
        "phi_npy_path": args.phi_npy_path,
        "A_psi": args.A_psi,
        "phi_mass_amp": args.phi_mass_amp,
        "phi_gas_amp": args.phi_gas_amp,
        "pad_factor": args.pad_factor,
        "peak_mode": args.peak_mode,
        "smoothing_sigma_px": args.smoothing_sigma_px,
        "delta_arcmin": args.delta_arcmin,
        "canon_path": args.canon_path,
    }
    run_lensing_packet(config, args.outdir)


if __name__ == "__main__":
    main()
