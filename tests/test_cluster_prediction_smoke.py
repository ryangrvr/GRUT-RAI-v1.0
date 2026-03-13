import csv
import json
import numpy as np

from tools.run_cluster_prediction import run_cluster_prediction


def _gaussian_map(n: int, x0: float, y0: float, sigma: float) -> np.ndarray:
    y, x = np.indices((n, n))
    dx = x - x0
    dy = y - y0
    return np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))


def test_cluster_prediction_smoke(tmp_path):
    n = 64
    sigma_b = _gaussian_map(n, x0=32.0, y0=32.0, sigma=6.0)
    gas = _gaussian_map(n, x0=28.0, y0=32.0, sigma=6.0)

    sigma_b_path = tmp_path / "sigma_b.npy"
    gas_path = tmp_path / "gas.npy"
    np.save(sigma_b_path, sigma_b)
    np.save(gas_path, gas)

    outdir = tmp_path / "prediction"
    config = {
        "sigma_baryon_path": str(sigma_b_path),
        "gas_path": str(gas_path),
        "mode": "predict_kappa",
        "kernel": "k1",
        "response_model": "identity",
        "alpha_mem": 0.0,
        "A_psi": 1.0,
        "fov_arcmin": 10.0,
        "smoothing_grid": [0.0],
        "threshold_grid": [0.1],
        "peak_mode": "com_positive_kappa",
        "gas_centroid_mode": "com_positive",
        "normalize_mode": "none",
        "pixel_scale_arcsec": 60.0,
    }

    result1 = run_cluster_prediction(config, str(outdir))
    result2 = run_cluster_prediction(config, str(outdir))
    assert result1["certificate"]["output_digest"] == result2["certificate"]["output_digest"]

    offsets_path = outdir / "offsets.csv"
    with offsets_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        row = next(reader)

    lens_x = float(row["lens_x_px"])
    lens_y = float(row["lens_y_px"])
    assert abs(lens_x - 32.0) < 0.5
    assert abs(lens_y - 32.0) < 0.5

    summary = json.loads((outdir / "centroids_summary.json").read_text())
    assert summary["response_model"] == "identity"
