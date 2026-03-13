from __future__ import annotations

from pathlib import Path

from tools.run_rotation_batch import run_rotation_batch


def test_rotation_batch_smoke(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    header = "r_kpc,v_obs,v_err,v_gas,v_star\n"
    (data_dir / "g1.csv").write_text(header + "1,100,5,60,80\n2,100,5,60,80\n")
    (data_dir / "g2.csv").write_text(header + "1,90,5,50,70\n2,90,5,50,70\n")

    outdir = tmp_path / "batch"
    manifest = run_rotation_batch(
        sorted(data_dir.glob("*.csv")),
        {"response_model": "identity", "r0_policy": "median_radius"},
        outdir,
    )

    summary_path = outdir / "summary.csv"
    assert summary_path.exists()
    rows = summary_path.read_text().splitlines()
    assert len(rows) == 3
    assert manifest["summary_hash"]
