import json
from pathlib import Path

from tools.sweep_cosmology import run_sweep


def test_sweep_runner_smoke(tmp_path):
    outdir1 = tmp_path / "sweep1"
    outdir2 = tmp_path / "sweep2"

    grid = [0.0, 0.1, 0.2]
    run_sweep(
        canon_path="canon/grut_canon_v0.3.json",
        param="alpha_mem",
        grid=grid,
        start_z=2.0,
        rho0=0.2,
        p=-0.2,
        rho_m0=None,
        dt_years=1e5,
        steps=20,
        outdir=str(outdir1),
    )

    run_sweep(
        canon_path="canon/grut_canon_v0.3.json",
        param="alpha_mem",
        grid=grid,
        start_z=2.0,
        rho0=0.2,
        p=-0.2,
        rho_m0=None,
        dt_years=1e5,
        steps=20,
        outdir=str(outdir2),
    )

    assert (outdir1 / "sweep_results.jsonl").exists()
    assert (outdir1 / "sweep_results.csv").exists()

    for idx, value in enumerate(grid):
        run_dir = outdir1 / f"run_{idx}_alpha_mem_{str(value).replace('-', 'm').replace('.', 'p')}"
        assert (run_dir / "certificate.json").exists()
        assert (run_dir / "outputs.json").exists()
        assert (run_dir / "summary.json").exists()

    rows1 = [json.loads(line) for line in (outdir1 / "sweep_results.jsonl").read_text().splitlines()]
    rows2 = [json.loads(line) for line in (outdir2 / "sweep_results.jsonl").read_text().splitlines()]

    def key_fn(r):
        return (r["param"], r["value"])

    map1 = {key_fn(r): r for r in rows1}
    map2 = {key_fn(r): r for r in rows2}

    for key in map1:
        assert map1[key]["output_digest"] == map2[key]["output_digest"]
        assert map1[key]["repro_hash"] == map2[key]["repro_hash"]
        for field in (
            "H_floor_count",
            "fs8_masked_count",
            "fs8_min_unmasked",
            "fs8_max_unmasked",
            "fs8_z0_unmasked",
            "fs8_min_compare",
            "fs8_max_compare",
            "fs8_z0_compare",
            "compare_point_count",
            "compare_definition",
            "H0_code",
            "idx0",
            "z0",
            "status",
            "failure_reason",
            "valid_z_max",
            "out_of_domain_fraction",
            "rms_H_vs_baseline",
            "rms_fs8_vs_baseline",
            "rms_definition",
            "rms_n_points",
            "rho_m0_input",
            "rho_m_init_used",
            "rho_m_end",
        ):
            assert field in map1[key]

    baseline = map1[("alpha_mem", 0.0)]
    assert baseline["rms_H_vs_baseline"] in (0.0, 0)


def test_sweep_runner_with_matter_growth(tmp_path):
    outdir = tmp_path / "sweep_growth"
    grid = [0.0, 0.1]
    run_sweep(
        canon_path="canon/grut_canon_v0.3.json",
        param="alpha_mem",
        grid=grid,
        start_z=2.0,
        rho0=0.2,
        p=-0.2,
        rho_m0=0.05,
        dt_years=1e5,
        steps=30,
        outdir=str(outdir),
    )

    rows = [json.loads(line) for line in (outdir / "sweep_results.jsonl").read_text().splitlines()]
    assert any((row.get("rms_n_points") or {}).get("fs8", 0) > 0 for row in rows)


def test_sweep_runner_matter_only_compare_window(tmp_path):
    outdir = tmp_path / "sweep_matter_only"
    grid = [0.0, 0.1]
    run_sweep(
        canon_path="canon/grut_canon_v0.3.json",
        param="alpha_mem",
        grid=grid,
        start_z=2.0,
        rho0=0.2,
        p=0.0,
        rho_m0=0.2,
        dt_years=1e5,
        steps=120,
        outdir=str(outdir),
    )

    rows = [json.loads(line) for line in (outdir / "sweep_results.jsonl").read_text().splitlines()]
    assert any((row.get("compare_point_count") or 0) > 50 for row in rows)
    assert any(row.get("fs8_z0_compare") is not None for row in rows)


def test_sweep_runner_out_of_domain_high_z(tmp_path):
    outdir = tmp_path / "sweep_domain"
    grid = [0.0]
    run_sweep(
        canon_path="canon/grut_canon_v0.3.json",
        param="alpha_mem",
        grid=grid,
        start_z=2.0,
        rho0=0.1,
        p=-0.1,
        rho_m0=0.0,
        rho0_vac=0.1,
        rho_total0=0.1,
        p_total0=-0.1,
        valid_z_max=1.0,
        dt_years=1e5,
        steps=30,
        outdir=str(outdir),
    )

    rows = [json.loads(line) for line in (outdir / "sweep_results.jsonl").read_text().splitlines()]
    assert rows[0]["status"] == "OUT_OF_DOMAIN_HIGH_Z"
