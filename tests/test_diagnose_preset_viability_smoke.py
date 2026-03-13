import json
from pathlib import Path

from tools.diagnose_preset_viability import diagnose_preset_viability


def test_diagnose_preset_viability_high_z(tmp_path: Path):
    outdir = tmp_path / "diag"
    report = diagnose_preset_viability(
        canon_path="canon/grut_canon_v0.3.json",
        alpha_mem=0.333333333,
        start_z=2.0,
        dt_years=1e5,
        steps=60,
        outdir=str(outdir),
        vacuum_rho0_vac=0.0,
        vacuum_rho_m0=0.0,
        vacuum_valid_z_max=1.0,
    )

    vacuum = report["presets"]["vacuum_plus_matter"]
    assert vacuum["H2_negative_count_above_valid_z_max"] > 0
    assert (outdir / "preset_viability_report.json").exists()
