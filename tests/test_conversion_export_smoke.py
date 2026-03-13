import csv
import json
from pathlib import Path

from tools.calibrate_and_export import calibrate_and_export


def _read_csv_rows(path: Path):
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        lines = [line for line in f if not line.startswith("#")]
    reader = csv.DictReader(lines)
    for row in reader:
        rows.append(row)
    return rows


def test_conversion_export_smoke(tmp_path):
    outdir1 = tmp_path / "calib1"
    outdir2 = tmp_path / "calib2"

    manifest1 = calibrate_and_export(
        canon_path="canon/grut_canon_v0.3.json",
        preset="matter_only",
        alpha_mem=0.333333333,
        start_z=2.0,
        dt_years=1e5,
        steps=30,
        outdir=str(outdir1),
    )
    manifest2 = calibrate_and_export(
        canon_path="canon/grut_canon_v0.3.json",
        preset="matter_only",
        alpha_mem=0.333333333,
        start_z=2.0,
        dt_years=1e5,
        steps=30,
        outdir=str(outdir2),
    )

    ez_path = outdir1 / "Hz_dimensionless_Ez.csv"
    assert ez_path.exists()
    rows = _read_csv_rows(ez_path)
    idx0 = manifest1["idx0"]
    assert idx0 < len(rows)
    e0 = float(rows[idx0]["E_z"])
    assert abs(e0 - 1.0) < 1e-12

    assert (outdir1 / "Hz_km_s_Mpc_Planck_67p4.csv").exists()
    assert (outdir1 / "Hz_km_s_Mpc_SH0ES_73p0.csv").exists()

    manifest_path = outdir1 / "calibration_manifest.json"
    assert manifest_path.exists()
    manifest_loaded = json.loads(manifest_path.read_text())
    for key in ("canon_hash", "repro_hash", "output_digest"):
        assert manifest_loaded.get(key)
    assert len(manifest_loaded.get("anchors", [])) == 2

    assert manifest1["H0_code"] == manifest2["H0_code"]
    assert manifest1["anchors"] == manifest2["anchors"]
