import json
from pathlib import Path

from tools.build_evidence_packet import build_evidence_packet
from tools.summarize_evidence_packet import summarize_evidence_packet


def test_build_and_summarize_evidence_packet(tmp_path: Path):
    calib_dir = tmp_path / "calibration"
    calib_dir.mkdir()
    (calib_dir / "calibration_manifest.json").write_text(
        json.dumps({"status": "VIABLE", "preset": "matter_only"})
    )
    (calib_dir / "Hz_dimensionless_Ez.csv").write_text("z,H_code,E_z\n0,1,1\n")

    outdir = tmp_path / "packet"
    packet = build_evidence_packet(
        calibration_dir=str(calib_dir),
        sweep_dir=None,
        quantum_boundary_dir=None,
        outdir=str(outdir),
        notes=None,
    )
    assert packet.get("schema") == "grut-phase2-evidence-v1"

    summary_path = summarize_evidence_packet(
        packet_path=str(outdir / "phase2_evidence_packet.json"),
        outdir=str(outdir),
    )
    assert Path(summary_path).exists()
    header = Path(summary_path).read_text().splitlines()[0]
    assert "component" in header and "sha256" in header