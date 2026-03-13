import csv
import json
import math
from pathlib import Path

from tools.build_hubble_tension_packet import build_hubble_tension_packet


def _read_csv(path: Path):
    return list(csv.DictReader(path.read_text().splitlines()))


def test_hubble_tension_packet_smoke(tmp_path: Path):
    out1 = tmp_path / "packet1"
    out2 = tmp_path / "packet2"

    res1 = build_hubble_tension_packet(
        outdir=str(out1),
        canon_path="canon/grut_canon_v0.3.json",
        alpha_mem=None,
        start_z=2.0,
        steps=60,
        dt_years=100000.0,
        integrator="RK4",
        include_vacuum_plus_matter=True,
        dataset_policy="all",
        eobs_anchor_policy="lowest_z",
        compare_window_policy="full",
        preset="both",
        recommendation_mode="configured_only",
        make_plots=False,
    )
    res2 = build_hubble_tension_packet(
        outdir=str(out2),
        canon_path="canon/grut_canon_v0.3.json",
        alpha_mem=None,
        start_z=2.0,
        steps=60,
        dt_years=100000.0,
        integrator="RK4",
        include_vacuum_plus_matter=True,
        dataset_policy="all",
        eobs_anchor_policy="lowest_z",
        compare_window_policy="full",
        preset="both",
        recommendation_mode="configured_only",
        make_plots=False,
    )

    assert res1["output_digest"] == res2["output_digest"]

    required = [
        out1 / "README_DATA.md",
        out1 / "PACKET_INDEX.json",
        out1 / "nis_hubble_certificate.json",
        out1 / "runs" / "grut_run.json",
        out1 / "runs" / "lcdm_reference.json",
        out1 / "data" / "hz_observations.csv",
        out1 / "data" / "sources.json",
        out1 / "outputs" / "Ez_grut.csv",
        out1 / "outputs" / "Ez_lcdm.csv",
        out1 / "outputs" / "Hz_grut_anchors.csv",
        out1 / "outputs" / "point_residuals.csv",
        out1 / "outputs" / "preset_window_summary.csv",
        out1 / "outputs" / "preset_window_summary.json",
        out1 / "outputs" / "late_time_recommendation.json",
        out1 / "outputs" / "residuals_vs_lcdm.json",
        out1 / "outputs" / "residuals_vs_data.json",
    ]
    for path in required:
        assert path.exists()

    grut_run = json.loads((out1 / "runs" / "grut_run.json").read_text())
    ez_lcdm_rows = _read_csv(out1 / "outputs" / "Ez_lcdm.csv")
    ez_grut_rows = _read_csv(out1 / "outputs" / "Ez_grut.csv")

    for preset, meta in grut_run["presets"].items():
        idx0 = int(meta["status"]["idx0"])
        z0 = float(meta["status"]["z0"]) if meta["status"]["z0"] is not None else None
        if z0 is None:
            continue
        lcdm_rows = [r for r in ez_lcdm_rows if r["preset"] == preset]
        grut_rows = [r for r in ez_grut_rows if r["preset"] == preset]
        lcdm_match = min(lcdm_rows, key=lambda r: abs(float(r["z"]) - z0))
        grut_match = min(grut_rows, key=lambda r: abs(float(r["z"]) - z0))
        assert math.isclose(float(lcdm_match["E_lcdm"]), 1.0, rel_tol=1e-2, abs_tol=1e-2)
        if grut_match["E_grut"] not in ("", "None"):
            assert math.isclose(float(grut_match["E_grut"]), 1.0, rel_tol=1e-2, abs_tol=1e-2)
        assert idx0 >= 0

    residuals_data = json.loads((out1 / "outputs" / "residuals_vs_data.json").read_text())
    presets_block = residuals_data.get("presets", {})
    assert "matter_only" in presets_block
    windows = presets_block["matter_only"].get("windows", {})
    assert "full" in windows
    anchors = windows["full"].get("anchors", {})
    assert "Planck_67p4" in anchors
    assert "SH0ES_73p0" in anchors
    planck = anchors["Planck_67p4"]
    assert "by_tracer" in planck
    assert "compare_report" in planck
    assert "chi2_E" in planck
    assert "by_tracer_E" in planck

    vacuum_block = presets_block.get("vacuum_plus_matter")
    if vacuum_block:
        assert "status" in vacuum_block

    recommendation = json.loads((out1 / "outputs" / "late_time_recommendation.json").read_text())
    assert "recommended_preset" in recommendation
    assert "recommended_compare_window_policy" in recommendation
    assert recommendation.get("candidates")


def test_hubble_tension_dataset_policy_cc_only(tmp_path: Path):
    outdir = tmp_path / "packet_cc"
    res = build_hubble_tension_packet(
        outdir=str(outdir),
        canon_path="canon/grut_canon_v0.3.json",
        alpha_mem=None,
        start_z=2.0,
        steps=40,
        dt_years=100000.0,
        integrator="RK4",
        include_vacuum_plus_matter=False,
        dataset_policy="cc_only",
        eobs_anchor_policy="lowest_z",
        compare_window_policy="full",
        preset="matter_only",
        recommendation_mode="configured_only",
        make_plots=False,
    )
    assert res["output_digest"]
    residuals_data = json.loads((outdir / "outputs" / "residuals_vs_data.json").read_text())
    presets_block = residuals_data.get("presets", {})
    matter = presets_block.get("matter_only", {})
    assert matter.get("dataset_policy") == "cc_only"
    n_points = matter.get("n_points_total")
    rows = _read_csv(Path("data/hz_observations_min.csv"))
    expected = sum(1 for r in rows if str(r.get("tracer", "")).strip().upper() == "CC")
    assert n_points == expected


def test_hubble_tension_recommendation_late_time_grid(tmp_path: Path):
    outdir = tmp_path / "packet_grid"
    build_hubble_tension_packet(
        outdir=str(outdir),
        canon_path="canon/grut_canon_v0.3.json",
        alpha_mem=None,
        start_z=2.0,
        steps=60,
        dt_years=100000.0,
        integrator="RK4",
        include_vacuum_plus_matter=True,
        dataset_policy="min",
        eobs_anchor_policy="lowest_z",
        compare_window_policy="full",
        preset="both",
        recommendation_mode="late_time_grid",
        make_plots=False,
    )
    recommendation = json.loads((outdir / "outputs" / "late_time_recommendation.json").read_text())
    candidates = recommendation.get("candidates", [])
    assert len(candidates) >= 3
    assert recommendation.get("recommended_preset") == "vacuum_plus_matter"
    assert recommendation.get("recommended_compare_window_policy") == "z_le_1_0"
