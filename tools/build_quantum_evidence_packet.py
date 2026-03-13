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
from grut.cluster_packet import file_sha256
from grut.quantum import G_SI, HBAR_SI, PI, SEC_PER_YEAR, compute_boundary, fit_loglog_slope
from grut.utils import stable_sha256

OMEGA_UNITS = "rad_per_s"
L_UNITS = "m"
M_UNITS = "kg"


def _load_tau0_seconds(canon_path: str) -> Tuple[float, str, Optional[str]]:
    canon = GRUTCanon(canon_path)
    tau0_years = canon.get_value("CONST_TAU_0")
    return float(tau0_years) * SEC_PER_YEAR, "canon", canon.canon_hash


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2))


def _write_scan_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _logspace(min_val: float, max_val: float, points: int) -> np.ndarray:
    if min_val <= 0 or max_val <= 0 or points < 2:
        raise ValueError("logspace requires positive bounds and points>=2")
    return np.logspace(math.log10(min_val), math.log10(max_val), points)


def _fit_slope(rows: list[dict[str, Any]], value_key: str, mid_frac: float = 0.8) -> Tuple[float, float, Tuple[float, float]]:
    masses = np.array([float(row["m_kg"]) for row in rows], dtype=float)
    values = np.array([float(row[value_key]) for row in rows], dtype=float)
    if masses.size < 2:
        raise ValueError("Need at least two points for slope fit")

    order = np.argsort(masses)
    masses = masses[order]
    values = values[order]

    n = masses.size
    trim = int((1.0 - mid_frac) * n / 2.0)
    if trim > 0:
        masses = masses[trim:-trim]
        values = values[trim:-trim]

    slope, intercept = fit_loglog_slope(masses, values)
    return slope, intercept, (float(masses.min()), float(masses.max()))


def _build_benchmark(
    *,
    omega_policy: str,
    omega_exp: Optional[float],
    m_kg: float,
    l_m: float,
    tau0_s: float,
    alpha_vac: float,
    constants_source: Dict[str, Any],
) -> Dict[str, Any]:
    inputs, outputs = compute_boundary(
        m_kg=m_kg,
        l_m=l_m,
        tau0_s=tau0_s,
        omega_policy=omega_policy,
        omega_exp=omega_exp,
        alpha_vac=alpha_vac,
    )
    return {
        "inputs": {
            **inputs,
            "units": {"omega": OMEGA_UNITS, "l": L_UNITS, "m": M_UNITS},
        },
        "outputs": outputs,
        "constants": {
            "G_SI": G_SI,
            "HBAR_SI": HBAR_SI,
            "PI": PI,
            "SEC_PER_YEAR": SEC_PER_YEAR,
        },
        "policy": {
            "omega_policy": omega_policy,
            "omega_exp": omega_exp,
            "alpha_vac": alpha_vac,
            "tau0_s": tau0_s,
        },
        "sources": constants_source,
    }


def _build_omega_scan(
    *,
    m_kg: float,
    l_m: float,
    tau0_s: float,
    alpha_vac: float,
    omega_min: float,
    omega_max: float,
    omega_points: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for omega in _logspace(omega_min, omega_max, omega_points):
        _, outputs = compute_boundary(
            m_kg=m_kg,
            l_m=l_m,
            tau0_s=tau0_s,
            omega_policy="controlled",
            omega_exp=float(omega),
            alpha_vac=alpha_vac,
        )
        rows.append(
            {
                "omega": float(omega),
                "X": outputs["X"],
                "alpha_eff": outputs["alpha_eff"],
                "t_dp_s": outputs["t_dp_s"],
                "t_grut_s": outputs["t_grut_s"],
                "enhancement": outputs["enhancement"],
            }
        )
    return rows


def _build_mass_scan(
    *,
    omega_policy: str,
    omega_exp: Optional[float],
    l_m: float,
    tau0_s: float,
    alpha_vac: float,
    mass_min: float,
    mass_max: float,
    mass_points: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for mass in _logspace(mass_min, mass_max, mass_points):
        _, outputs = compute_boundary(
            m_kg=float(mass),
            l_m=l_m,
            tau0_s=tau0_s,
            omega_policy=omega_policy,
            omega_exp=omega_exp,
            alpha_vac=alpha_vac,
        )
        rows.append(
            {
                "m_kg": float(mass),
                "t_dp_s": outputs["t_dp_s"],
                "t_grut_s": outputs["t_grut_s"],
                "enhancement": outputs["enhancement"],
            }
        )
    return rows


def _load_existing(outdir: Path, input_hash: str) -> Optional[Dict[str, Any]]:
    cert_path = outdir / "nis_quantum_certificate.json"
    if not cert_path.exists():
        return None
    try:
        cert = json.loads(cert_path.read_text())
    except json.JSONDecodeError:
        return None
    if cert.get("input_hash") != input_hash:
        return None
    summary_path = outdir / "summary.csv"
    if not summary_path.exists():
        return None
    return {"certificate": cert}


def build_quantum_evidence_packet(config: Dict[str, Any], outdir: str, *, force: bool = False) -> Dict[str, Any]:
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    canon_path = str(config.get("canon_path", "canon/grut_canon_v0.3.json"))
    canon_hash = None

    tau0_override = config.get("tau0_s")
    if tau0_override is None:
        tau0_s, tau0_source, canon_hash = _load_tau0_seconds(canon_path)
    else:
        tau0_s = float(tau0_override)
        tau0_source = "override"

    alpha_vac = float(config.get("alpha_vac", 1.0 / 3.0))
    alpha_source = "override" if "alpha_vac" in config else "default"

    l_m = float(config.get("l_m", 1e-6))
    m_benchmark = float(config.get("m_benchmark_kg", 1e-6))
    omega_benchmark = float(config.get("omega_benchmark", 1000.0))

    omega_scan_min = float(config.get("omega_scan_min", 1e2))
    omega_scan_max = float(config.get("omega_scan_max", 1e6))
    omega_scan_points = int(config.get("omega_scan_points", 50))

    mass_scan_min = float(config.get("mass_scan_min", 1e-18))
    mass_scan_max = float(config.get("mass_scan_max", 1e-6))
    mass_scan_points = int(config.get("mass_scan_points", 40))

    determinism_mode = str(config.get("determinism_mode", "STRICT"))

    constants_source = {
        "tau0_s": {"source": tau0_source, "canon_hash": canon_hash},
        "alpha_vac": {"source": alpha_source},
    }

    input_payload = {
        "config": {
            "l_m": l_m,
            "m_benchmark_kg": m_benchmark,
            "omega_benchmark": omega_benchmark,
            "omega_scan_min": omega_scan_min,
            "omega_scan_max": omega_scan_max,
            "omega_scan_points": omega_scan_points,
            "mass_scan_min": mass_scan_min,
            "mass_scan_max": mass_scan_max,
            "mass_scan_points": mass_scan_points,
            "determinism_mode": determinism_mode,
        },
        "constants": {
            "tau0_s": tau0_s,
            "alpha_vac": alpha_vac,
            "units": {"omega": OMEGA_UNITS, "l": L_UNITS, "m": M_UNITS},
        },
        "canon_hash": canon_hash,
    }
    input_hash = stable_sha256(input_payload)

    if not force:
        existing = _load_existing(outdir_path, input_hash)
        if existing is not None:
            return existing
        if any(outdir_path.iterdir()):
            raise RuntimeError("Outdir is not empty and input_hash differs. Use --force to overwrite.")

    bench_dir = outdir_path / "benchmarks"
    scans_dir = outdir_path / "scans"
    bench_dir.mkdir(parents=True, exist_ok=True)
    scans_dir.mkdir(parents=True, exist_ok=True)

    benchmark_controlled = _build_benchmark(
        omega_policy="controlled",
        omega_exp=omega_benchmark,
        m_kg=m_benchmark,
        l_m=l_m,
        tau0_s=tau0_s,
        alpha_vac=alpha_vac,
        constants_source=constants_source,
    )
    _write_json(bench_dir / "benchmark_controlled.json", benchmark_controlled)

    benchmark_self = _build_benchmark(
        omega_policy="self_consistent",
        omega_exp=None,
        m_kg=m_benchmark,
        l_m=l_m,
        tau0_s=tau0_s,
        alpha_vac=alpha_vac,
        constants_source=constants_source,
    )
    _write_json(bench_dir / "benchmark_self_consistent.json", benchmark_self)

    omega_rows = _build_omega_scan(
        m_kg=m_benchmark,
        l_m=l_m,
        tau0_s=tau0_s,
        alpha_vac=alpha_vac,
        omega_min=omega_scan_min,
        omega_max=omega_scan_max,
        omega_points=omega_scan_points,
    )
    _write_scan_csv(
        scans_dir / "scan_omega_controlled.csv",
        omega_rows,
        ["omega", "X", "alpha_eff", "t_dp_s", "t_grut_s", "enhancement"],
    )

    mass_controlled = _build_mass_scan(
        omega_policy="controlled",
        omega_exp=omega_benchmark,
        l_m=l_m,
        tau0_s=tau0_s,
        alpha_vac=alpha_vac,
        mass_min=mass_scan_min,
        mass_max=mass_scan_max,
        mass_points=mass_scan_points,
    )
    _write_scan_csv(
        scans_dir / "scan_mass_controlled.csv",
        mass_controlled,
        ["m_kg", "t_dp_s", "t_grut_s", "enhancement"],
    )

    mass_self = _build_mass_scan(
        omega_policy="self_consistent",
        omega_exp=None,
        l_m=l_m,
        tau0_s=tau0_s,
        alpha_vac=alpha_vac,
        mass_min=mass_scan_min,
        mass_max=mass_scan_max,
        mass_points=mass_scan_points,
    )
    _write_scan_csv(
        scans_dir / "scan_mass_self_consistent.csv",
        mass_self,
        ["m_kg", "t_dp_s", "t_grut_s", "enhancement"],
    )

    slope_controlled, intercept_controlled, fit_range_controlled = _fit_slope(mass_controlled, "t_grut_s")
    slope_self, intercept_self, fit_range_self = _fit_slope(mass_self, "t_grut_s")
    slope_dp, intercept_dp, fit_range_dp = _fit_slope(mass_controlled, "t_dp_s")

    summary_path = outdir_path / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "tau0_s",
                "alpha_vac",
                "l_m",
                "omega_benchmark",
                "slope_self_consistent",
                "slope_controlled",
                "slope_dp_reference",
                "intercept_self_consistent",
                "intercept_controlled",
                "intercept_dp_reference",
                "fit_mass_min_kg",
                "fit_mass_max_kg",
                "benchmark_controlled_t_dp_s",
                "benchmark_controlled_t_grut_s",
                "benchmark_controlled_enhancement",
                "benchmark_self_consistent_t_dp_s",
                "benchmark_self_consistent_t_grut_s",
                "benchmark_self_consistent_enhancement",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "tau0_s": tau0_s,
                "alpha_vac": alpha_vac,
                "l_m": l_m,
                "omega_benchmark": omega_benchmark,
                "slope_self_consistent": slope_self,
                "slope_controlled": slope_controlled,
                "slope_dp_reference": slope_dp,
                "intercept_self_consistent": intercept_self,
                "intercept_controlled": intercept_controlled,
                "intercept_dp_reference": intercept_dp,
                "fit_mass_min_kg": fit_range_self[0],
                "fit_mass_max_kg": fit_range_self[1],
                "benchmark_controlled_t_dp_s": benchmark_controlled["outputs"]["t_dp_s"],
                "benchmark_controlled_t_grut_s": benchmark_controlled["outputs"]["t_grut_s"],
                "benchmark_controlled_enhancement": benchmark_controlled["outputs"]["enhancement"],
                "benchmark_self_consistent_t_dp_s": benchmark_self["outputs"]["t_dp_s"],
                "benchmark_self_consistent_t_grut_s": benchmark_self["outputs"]["t_grut_s"],
                "benchmark_self_consistent_enhancement": benchmark_self["outputs"]["enhancement"],
            }
        )

    readme_text = f"""# Quantum Evidence Packet v0.1

This packet provides deterministic, Tier A quantum decoherence benchmarks and scans for the $m^{{-2/3}}$ bridge.

Claims:
- Controlled $\\omega$ oracle and self-consistent closure.
- Slope falsifier (log-log mass scans) with explicit policy split.

Not claimed:
- No Tier B constants (no 3-loop residue, no r_sat).
- No particle-sector predictions.

Units:
- $\\omega$ in {OMEGA_UNITS}
- l in {L_UNITS}
- m in {M_UNITS}

Commands:
- python tools/build_quantum_evidence_packet.py --outdir artifacts/evidence_quantum_v0_1
"""
    (outdir_path / "README_DATA.md").write_text(readme_text)

    base_files = {
        "README_DATA.md": outdir_path / "README_DATA.md",
        "benchmarks/benchmark_controlled.json": bench_dir / "benchmark_controlled.json",
        "benchmarks/benchmark_self_consistent.json": bench_dir / "benchmark_self_consistent.json",
        "scans/scan_omega_controlled.csv": scans_dir / "scan_omega_controlled.csv",
        "scans/scan_mass_controlled.csv": scans_dir / "scan_mass_controlled.csv",
        "scans/scan_mass_self_consistent.csv": scans_dir / "scan_mass_self_consistent.csv",
        "summary.csv": summary_path,
    }
    base_hashes = {name: file_sha256(str(path)) for name, path in base_files.items() if path.exists()}

    file_hashes_path = outdir_path / "file_hashes.json"
    _write_json(file_hashes_path, base_hashes)

    output_digest = stable_sha256({"output_hashes": base_hashes, "input_hash": input_hash, "canon_hash": canon_hash})

    certificate = {
        "tool_version": "quantum_evidence_v0.1",
        "determinism_mode": determinism_mode,
        "canon_hash": canon_hash,
        "input_hash": input_hash,
        "output_digest": output_digest,
        "output_hashes": {},
        "timestamp_utc": None,
    }
    cert_path = outdir_path / "nis_quantum_certificate.json"
    _write_json(cert_path, certificate)

    packet_index = {
        "packet": "quantum_evidence_v0.1",
        "output_files": sorted(list(base_hashes.keys()) + ["file_hashes.json", "nis_quantum_certificate.json", "PACKET_INDEX.json"]),
        "output_hashes": base_hashes,
        "input_hash": input_hash,
        "canon_hash": canon_hash,
        "certificate": {"output_digest": output_digest, "input_hash": input_hash},
    }
    packet_index_path = outdir_path / "PACKET_INDEX.json"
    _write_json(packet_index_path, packet_index)

    output_files = {
        **base_files,
        "file_hashes.json": file_hashes_path,
        "nis_quantum_certificate.json": cert_path,
        "PACKET_INDEX.json": packet_index_path,
    }
    output_hashes = {name: file_sha256(str(path)) for name, path in output_files.items() if path.exists()}
    certificate["output_hashes"] = output_hashes
    _write_json(cert_path, certificate)

    return {"summary": summary_path, "certificate": certificate}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Quantum Evidence Packet v0.1")
    parser.add_argument("--outdir", default="artifacts/evidence_quantum_v0_1")
    parser.add_argument("--tau0_s", type=float, default=None)
    parser.add_argument("--alpha_vac", type=float, default=1.0 / 3.0)
    parser.add_argument("--l_m", type=float, default=1e-6)
    parser.add_argument("--m_benchmark_kg", type=float, default=1e-6)
    parser.add_argument("--omega_benchmark", type=float, default=1000.0)
    parser.add_argument("--omega_scan_min", type=float, default=1e2)
    parser.add_argument("--omega_scan_max", type=float, default=1e6)
    parser.add_argument("--omega_scan_points", type=int, default=50)
    parser.add_argument("--mass_scan_min", type=float, default=1e-18)
    parser.add_argument("--mass_scan_max", type=float, default=1e-6)
    parser.add_argument("--mass_scan_points", type=int, default=40)
    parser.add_argument("--determinism_mode", default="STRICT")
    parser.add_argument("--canon_path", default="canon/grut_canon_v0.3.json")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config = {
        "tau0_s": args.tau0_s,
        "alpha_vac": args.alpha_vac,
        "l_m": args.l_m,
        "m_benchmark_kg": args.m_benchmark_kg,
        "omega_benchmark": args.omega_benchmark,
        "omega_scan_min": args.omega_scan_min,
        "omega_scan_max": args.omega_scan_max,
        "omega_scan_points": args.omega_scan_points,
        "mass_scan_min": args.mass_scan_min,
        "mass_scan_max": args.mass_scan_max,
        "mass_scan_points": args.mass_scan_points,
        "determinism_mode": args.determinism_mode,
        "canon_path": args.canon_path,
    }
    build_quantum_evidence_packet(config, args.outdir, force=args.force)


if __name__ == "__main__":
    main()
