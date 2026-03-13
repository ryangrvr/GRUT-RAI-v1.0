from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.audit_schemas import EvidencePacketComponent, Phase2EvidencePacket


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _add_component(components: List[dict], name: str, path: Path, kind: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Missing component: {path}")
    components.append(
        EvidencePacketComponent(
            name=name,
            path=str(path),
            sha256=_sha256_file(path),
            kind=kind,
            size_bytes=path.stat().st_size,
        ).model_dump()
    )


def build_evidence_packet(
    *,
    calibration_dir: str,
    sweep_dir: Optional[str],
    quantum_boundary_dir: Optional[str],
    outdir: str,
    notes: Optional[str] = None,
) -> dict:
    components: List[dict] = []

    calib_path = Path(calibration_dir)
    _add_component(components, "calibration_manifest", calib_path / "calibration_manifest.json", "manifest")
    _add_component(components, "calibration_Ez", calib_path / "Hz_dimensionless_Ez.csv", "table")
    for anchor in ("Planck_67p4", "SH0ES_73p0"):
        csv_path = calib_path / f"Hz_km_s_Mpc_{anchor}.csv"
        if csv_path.exists():
            _add_component(components, f"calibration_Hz_{anchor}", csv_path, "table")
    fs8_path = calib_path / "fs8_compare_window.csv"
    if fs8_path.exists():
        _add_component(components, "calibration_fs8_compare", fs8_path, "table")

    if sweep_dir:
        sweep_path = Path(sweep_dir)
        _add_component(components, "sweep_manifest", sweep_path / "manifest.json", "manifest")
        jsonl_path = sweep_path / "sweep_results.jsonl"
        if jsonl_path.exists():
            _add_component(components, "sweep_results", jsonl_path, "table")

    if quantum_boundary_dir:
        qb_path = Path(quantum_boundary_dir)
        _add_component(components, "quantum_boundary_packet", qb_path / "quantum_boundary_packet.json", "packet")
        sha_path = qb_path / "quantum_boundary_packet.sha256"
        if sha_path.exists():
            _add_component(components, "quantum_boundary_hash", sha_path, "hash")
        table_path = qb_path / "quantum_boundary_table.csv"
        if table_path.exists():
            _add_component(components, "quantum_boundary_table", table_path, "table")
        scan_path = qb_path / "quantum_boundary_scan.csv"
        if scan_path.exists():
            _add_component(components, "quantum_boundary_scan", scan_path, "table")

    packet = {
        "schema": "grut-phase2-evidence-v1",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "components": components,
        "notes": notes,
    }
    Phase2EvidencePacket.model_validate(packet)

    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)
    packet_path = out_path / "phase2_evidence_packet.json"
    packet_path.write_text(json.dumps(packet, indent=2))
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Phase-2 cosmology evidence packet")
    parser.add_argument("--calibration_dir", default="artifacts/calibration")
    parser.add_argument("--sweep_dir", default=None)
    parser.add_argument("--quantum_boundary_dir", default=None)
    parser.add_argument("--outdir", default="artifacts/evidence_packet_phase2_cosmo_v0")
    parser.add_argument("--notes", default=None)
    args = parser.parse_args()

    build_evidence_packet(
        calibration_dir=args.calibration_dir,
        sweep_dir=args.sweep_dir,
        quantum_boundary_dir=args.quantum_boundary_dir,
        outdir=args.outdir,
        notes=args.notes,
    )


if __name__ == "__main__":
    main()