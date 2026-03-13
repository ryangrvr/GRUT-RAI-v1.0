#!/usr/bin/env python3
"""Quantum Boundary Test (Tier A).

Computes decoherence bounds using a controlled ω policy (primary)
or a self-consistent mock closure (secondary).
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.quantum import (
    G_SI,
    HBAR_SI,
    PI,
    PRESETS,
    QuantumBoundaryError,
    SEC_PER_YEAR,
    compute_boundary,
    compute_scan_rows_omega,
)
from grut.utils import stable_sha256
from tools.audit_schemas import QuantumBoundaryPacket


def _load_tau0_seconds(canon_path: str) -> Optional[float]:
    path = Path(canon_path)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
    consts = payload.get("constants", {}).get("by_id", {})
    tau0 = consts.get("CONST_TAU_0", {})
    value = tau0.get("value")
    units = tau0.get("units")
    if value is None:
        return None
    if units not in ("years", "year"):
        return None
    return float(value) * SEC_PER_YEAR


def build_packet(inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    packet = {
        "inputs": inputs,
        "outputs": outputs,
        "constants": {
            "G_SI": G_SI,
            "HBAR_SI": HBAR_SI,
            "PI": PI,
            "SEC_PER_YEAR": SEC_PER_YEAR,
        },
    }
    QuantumBoundaryPacket.model_validate(packet)
    return packet


def write_outputs(outdir: Path, packet: Dict[str, Any]) -> str:
    outdir.mkdir(parents=True, exist_ok=True)

    packet_path = outdir / "quantum_boundary_packet.json"
    packet_path.write_text(json.dumps(packet, sort_keys=True, separators=(",", ":")))

    digest = stable_sha256(packet)
    (outdir / "quantum_boundary_packet.sha256").write_text(digest)

    inputs = packet["inputs"]
    outputs = packet["outputs"]
    table_path = outdir / "quantum_boundary_table.csv"
    with table_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "m_kg",
                "l_m",
                "tau0_s",
                "omega",
                "policy",
                "alpha_vac",
                "X",
                "alpha_eff",
                "t_dp_s",
                "t_grut_s",
                "enhancement",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "m_kg": inputs["m_kg"],
                "l_m": inputs["l_m"],
                "tau0_s": inputs["tau0_s"],
                "omega": inputs.get("omega_exp"),
                "policy": inputs["omega_policy"],
                "alpha_vac": inputs["alpha_vac"],
                "X": outputs.get("X"),
                "alpha_eff": outputs.get("alpha_eff"),
                "t_dp_s": outputs["t_dp_s"],
                "t_grut_s": outputs["t_grut_s"],
                "enhancement": outputs["enhancement"],
            }
        )
    return digest


def write_scan(outdir: Path, rows: list[dict[str, float]]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    scan_path = outdir / "quantum_boundary_scan.csv"
    with scan_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["omega", "X", "alpha_eff", "t_grut_s", "enhancement"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_quantum_boundary(
    *,
    m_kg: Optional[float],
    l_m: Optional[float],
    tau0_s: Optional[float],
    omega_policy: str,
    omega_exp: Optional[float],
    alpha_vac: float,
    outdir: str,
    canon_path: str,
    preset: Optional[str],
    scan_omega_min: Optional[float],
    scan_omega_max: Optional[float],
    scan_points: Optional[int],
) -> Tuple[Dict[str, Any], str]:
    if preset:
        preset_key = preset.strip()
        if preset_key not in PRESETS:
            raise QuantumBoundaryError(f"unknown preset: {preset_key}")
        preset_values = PRESETS[preset_key]
        if m_kg is None:
            m_kg = preset_values["m_kg"]
        if l_m is None:
            l_m = preset_values["l_m"]
        if omega_exp is None and omega_policy == "controlled":
            omega_exp = preset_values["omega_exp"]

    if m_kg is None or l_m is None:
        raise QuantumBoundaryError("m_kg and l_m are required (or provide --preset)")

    if tau0_s is None:
        tau0_s = _load_tau0_seconds(canon_path)
        if tau0_s is None:
            raise QuantumBoundaryError("tau0_s is required when canon scaling is unavailable")

    inputs, outputs = compute_boundary(
        m_kg=m_kg,
        l_m=l_m,
        tau0_s=tau0_s,
        omega_policy=omega_policy,
        omega_exp=omega_exp,
        alpha_vac=alpha_vac,
    )
    packet = build_packet(inputs, outputs)
    digest = write_outputs(Path(outdir), packet)
    if scan_omega_min is not None or scan_omega_max is not None or scan_points is not None:
        if omega_policy != "controlled":
            raise QuantumBoundaryError("scan mode requires omega_policy=controlled")
        if scan_omega_min is None or scan_omega_max is None or scan_points is None:
            raise QuantumBoundaryError("scan_omega_min, scan_omega_max, scan_points are required")
        rows = compute_scan_rows_omega(
            m_kg=m_kg,
            l_m=l_m,
            tau0_s=tau0_s,
            alpha_vac=alpha_vac,
            omega_min=scan_omega_min,
            omega_max=scan_omega_max,
            scan_points=scan_points,
        )
        write_scan(Path(outdir), rows)
    return packet, digest


def main() -> int:
    parser = argparse.ArgumentParser(description="Quantum Boundary Test (Tier A).")
    parser.add_argument("--m_kg", type=float, default=None)
    parser.add_argument("--l_m", type=float, default=None)
    parser.add_argument("--tau0_s", type=float, default=None)
    parser.add_argument("--preset", type=str, choices=sorted(PRESETS.keys()), default=None)
    parser.add_argument(
        "--omega_policy",
        type=str,
        choices=["controlled", "self_consistent"],
        default="controlled",
    )
    parser.add_argument("--omega_exp", type=float, default=None)
    parser.add_argument("--alpha_vac", type=float, default=1.0 / 3.0)
    parser.add_argument("--scan_omega_min", type=float, default=None)
    parser.add_argument("--scan_omega_max", type=float, default=None)
    parser.add_argument("--scan_points", type=int, default=None)
    parser.add_argument("--outdir", type=str, default="artifacts/quantum_boundary")
    parser.add_argument("--canon_path", type=str, default="canon/grut_canon_v0.3.json")

    args = parser.parse_args()
    run_quantum_boundary(
        m_kg=args.m_kg,
        l_m=args.l_m,
        tau0_s=args.tau0_s,
        omega_policy=args.omega_policy,
        omega_exp=args.omega_exp,
        alpha_vac=args.alpha_vac,
        outdir=args.outdir,
        canon_path=args.canon_path,
        preset=args.preset,
        scan_omega_min=args.scan_omega_min,
        scan_omega_max=args.scan_omega_max,
        scan_points=args.scan_points,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())