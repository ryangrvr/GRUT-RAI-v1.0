import json
from pathlib import Path

from tools.plot_shape_sanity import run_shape_sanity


def test_shape_sanity_smoke(tmp_path: Path):
    outdir = tmp_path / "shape"
    run_shape_sanity(
        canon_path="canon/grut_canon_v0.3.json",
        alpha_mem=0.333333333,
        start_z=2.0,
        dt_years=1e5,
        steps=30,
        outdir=str(outdir),
    )

    assert (outdir / "shape_sanity_manifest.json").exists()
    assert (outdir / "matter_only_Ez.csv").exists()
    assert (outdir / "matter_only_fs8_compare.csv").exists()
    manifest = json.loads((outdir / "shape_sanity_manifest.json").read_text())
    assert manifest["presets_status"]["matter_only"] == "VIABLE"
    assert manifest["presets_status"]["vacuum_plus_matter"] == "VIABLE"


def test_shape_sanity_vacuum_not_viable(tmp_path: Path):
    outdir = tmp_path / "shape_bad"
    run_shape_sanity(
        canon_path="canon/grut_canon_v0.3.json",
        alpha_mem=0.333333333,
        start_z=2.0,
        dt_years=1e5,
        steps=30,
        outdir=str(outdir),
        vacuum_rho0_vac=0.0,
        vacuum_rho_m0=0.0,
    )

    manifest = json.loads((outdir / "shape_sanity_manifest.json").read_text())
    assert manifest["presets_status"]["vacuum_plus_matter"] == "NOT_VIABLE_AT_Z0"
