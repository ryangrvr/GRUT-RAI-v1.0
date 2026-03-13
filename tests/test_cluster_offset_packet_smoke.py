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


def test_cluster_offset_packet_smoke(tmp_path: Path) -> None:
    kappa = _gaussian(64, 32.0, 32.0, 6.0)
    gas = _gaussian(64, 36.0, 32.0, 6.0)

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
    }
    result1 = run_cluster_offset_packet(config, str(outdir))
    result2 = run_cluster_offset_packet(config, str(outdir))

    assert result1["certificate"]["output_digest"] == result2["certificate"]["output_digest"]

    summary = json.loads((outdir / "centroids_summary.json").read_text())
    assert abs(summary["robust_offset_arcsec"] - 4.0) < 0.2
