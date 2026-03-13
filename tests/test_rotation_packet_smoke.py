from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from tools.run_rotation_packet import run_rotation_packet


def _write_csv(path: Path, rows: list[tuple[float, ...]]) -> None:
    header = "r_kpc,v_obs,v_err,v_gas,v_star\n"
    lines = [header]
    for r in rows:
        lines.append(",".join(str(x) for x in r) + "\n")
    path.write_text("".join(lines))


def test_rotation_packet_smoke(tmp_path: Path) -> None:
    r = np.linspace(1, 10, 10)
    v_gas = np.full_like(r, 60.0)
    v_star = np.full_like(r, 80.0)
    v_obs = np.sqrt(v_gas**2 + v_star**2) + 5.0
    v_err = np.full_like(r, 5.0)

    rows = list(zip(r, v_obs, v_err, v_gas, v_star))
    data_path = tmp_path / "galaxy.csv"
    _write_csv(data_path, rows)

    config = {
        "data_path": str(data_path),
        "response_model": "radial_gate_v0",
        "alpha_mem": 0.2,
        "r0_policy": "median_radius",
    }
    outdir = tmp_path / "packet"
    result1 = run_rotation_packet(config, str(outdir))
    result2 = run_rotation_packet(config, str(outdir))

    assert result1["certificate"]["output_digest"] == result2["certificate"]["output_digest"]

    metrics = json.loads((outdir / "metrics.json").read_text())
    assert "baseline" in metrics and "grut" in metrics
    assert (outdir / "curves.csv").exists()
