import json
import numpy as np

from tools.run_cluster_profile_packet import run_cluster_profile_packet


def _gaussian_map(n: int, x0: float, y0: float, sigma: float) -> np.ndarray:
    y, x = np.indices((n, n))
    dx = x - x0
    dy = y - y0
    return np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))


def test_profile_packet_determinism(tmp_path):
    n = 64
    kappa = _gaussian_map(n, x0=32.0, y0=32.0, sigma=6.0)
    sigma_b = _gaussian_map(n, x0=32.0, y0=32.0, sigma=6.0)

    kappa_path = tmp_path / "kappa.npy"
    sigma_path = tmp_path / "sigma_b.npy"
    np.save(kappa_path, kappa)
    np.save(sigma_path, sigma_b)

    outdir = tmp_path / "profiles"
    config = {
        "kappa_path": str(kappa_path),
        "sigma_baryon_path": str(sigma_path),
        "compare_to_model": True,
        "model_response": "grut_gate_kspace_v0",
        "kernel": "k2",
        "k0_policy": "fov",
        "profile_bins": 10,
        "pixel_scale_arcsec": 60.0,
        "fov_arcmin": 10.0,
        "smoothing_grid": [1.0],
    }

    result1 = run_cluster_profile_packet(config, str(outdir))
    result2 = run_cluster_profile_packet(config, str(outdir))
    assert result1["certificate"]["output_digest"] == result2["certificate"]["output_digest"]

    metrics = json.loads((outdir / "profile_metrics.json").read_text())
    assert metrics["metrics"]["kappa"]["rms_diff"] > 0.0
