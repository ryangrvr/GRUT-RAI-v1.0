import json
import numpy as np

from tools.run_rotation_packet import run_rotation_packet


def _write_csv(path, rows):
    header = "r_kpc,v_obs,v_err,v_gas,v_star\n"
    lines = [header]
    for r in rows:
        lines.append(",".join(str(x) for x in r) + "\n")
    path.write_text("".join(lines))


def test_rotation_packet_smoke(tmp_path):
    r = np.linspace(1, 10, 10)
    v_bar = np.full_like(r, 100.0)
    v_obs = v_bar + 5.0
    v_err = np.full_like(r, 5.0)
    v_gas = np.full_like(r, 60.0)
    v_star = np.full_like(r, 80.0)

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
    assert metrics["baseline"]["rms_residual"] >= 0.0
    assert metrics["grut"]["rms_residual"] >= 0.0
