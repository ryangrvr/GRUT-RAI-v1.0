from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from tools.build_quantum_evidence_packet import build_quantum_evidence_packet


def _read_summary(path: Path) -> dict:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    return rows[0]


def test_quantum_evidence_packet_smoke(tmp_path: Path) -> None:
    outdir1 = tmp_path / "run1"
    outdir2 = tmp_path / "run2"

    config = {
        "tau0_s": 1.0,
        "alpha_vac": 1.0 / 3.0,
        "l_m": 1e-6,
        "m_benchmark_kg": 1e-9,
        "omega_benchmark": 1e3,
        "omega_scan_min": 1e2,
        "omega_scan_max": 1e4,
        "omega_scan_points": 5,
        "mass_scan_min": 1e-18,
        "mass_scan_max": 1e-12,
        "mass_scan_points": 6,
        "determinism_mode": "STRICT",
        "canon_path": "canon/grut_canon_v0.3.json",
    }

    result1 = build_quantum_evidence_packet(config, str(outdir1))
    result2 = build_quantum_evidence_packet(config, str(outdir2))

    cert1 = result1["certificate"]
    cert2 = result2["certificate"]
    assert cert1["output_digest"] == cert2["output_digest"]

    required = [
        "README_DATA.md",
        "PACKET_INDEX.json",
        "nis_quantum_certificate.json",
        "summary.csv",
        "benchmarks/benchmark_controlled.json",
        "benchmarks/benchmark_self_consistent.json",
        "scans/scan_omega_controlled.csv",
        "scans/scan_mass_controlled.csv",
        "scans/scan_mass_self_consistent.csv",
    ]
    for rel in required:
        assert (outdir1 / rel).exists()

    summary = _read_summary(outdir1 / "summary.csv")
    slope_self = float(summary["slope_self_consistent"])
    slope_controlled = float(summary["slope_controlled"])
    slope_dp = float(summary["slope_dp_reference"])

    assert np.isclose(slope_self, -2.0 / 3.0, atol=0.05)
    assert np.isclose(slope_controlled, -2.0, atol=0.05)
    assert np.isclose(slope_dp, -2.0, atol=0.05)
