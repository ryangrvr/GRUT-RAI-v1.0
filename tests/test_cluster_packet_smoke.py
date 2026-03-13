import json
import numpy as np

from tools.run_cluster_packet import run_cluster_packet


def _gaussian_map(n: int, x0: float, y0: float, sigma: float) -> np.ndarray:
    y, x = np.indices((n, n))
    dx = x - x0
    dy = y - y0
    return np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))


def test_cluster_packet_smoke(tmp_path):
    n = 64
    kappa = _gaussian_map(n, x0=36, y0=32, sigma=5.0)
    gas = _gaussian_map(n, x0=28, y0=32, sigma=5.0)

    kappa_path = tmp_path / "kappa.npy"
    gas_path = tmp_path / "gas.npy"
    np.save(kappa_path, kappa)
    np.save(gas_path, gas)

    outdir = tmp_path / "cluster"
    config = {
        "kappa_path": str(kappa_path),
        "gas_path": str(gas_path),
        "smoothing_grid": [0.0, 1.0],
        "threshold_grid": [0.1],
        "peak_mode": "com_positive_kappa",
        "gas_centroid_mode": "peak",
        "normalize_mode": "none",
        "pixel_scale_arcsec": 60.0,
    }

    result1 = run_cluster_packet(config, str(outdir))
    result2 = run_cluster_packet(config, str(outdir))
    assert result1["certificate"]["output_digest"] == result2["certificate"]["output_digest"]

    summary = json.loads((outdir / "centroids_summary.json").read_text())
    robust_offset = summary["robust_offset_arcmin"]
    assert abs(robust_offset - 8.0) < 1.0