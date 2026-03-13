from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from tools.run_cluster_offset_packet import run_cluster_offset_packet


def _gaussian(n: int, x0: float, y0: float, sigma: float) -> np.ndarray:
    y, x = np.indices((n, n))
    dx = x - x0
    dy = y - y0
    return np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))


def test_cluster_offset_prediction(tmp_path: Path) -> None:
    kappa = _gaussian(64, 32.0, 32.0, 6.0)
    gas = _gaussian(64, 34.0, 32.0, 6.0)

    kappa_path = tmp_path / "kappa.npy"
    gas_path = tmp_path / "gas.npy"
    np.save(kappa_path, kappa)
    np.save(gas_path, gas)

    outdir = tmp_path / "packet"
    config = {
        "kappa_path": str(kappa_path),
        "gas_path": str(gas_path),
        "pixel_scale_arcsec": 1.0,
        "smoothing_grid": [0.0],
        "threshold_grid": [0.1],
        "peak_mode": "peak",
        "gas_centroid_mode": "peak",
        "v_coll_kms": 1000.0,
        "tau0_s": 1.0,
        "kpc_per_arcsec": 1.0,
    }
    run_cluster_offset_packet(config, str(outdir))

    pred = json.loads((outdir / "prediction_summary.json").read_text())
    assert pred["delta_pred_kpc"]
    assert pred["delta_obs_kpc"] is not None
    assert pred["delta_residual"] is not None
