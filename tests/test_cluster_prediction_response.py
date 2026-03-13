import json
import numpy as np

from tools.run_cluster_prediction import run_cluster_prediction


def _gaussian_map(n: int, x0: float, y0: float, sigma: float) -> np.ndarray:
    y, x = np.indices((n, n))
    dx = x - x0
    dy = y - y0
    return np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))


def test_response_shape_changes(tmp_path):
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
        "kernel": "k2",
        "response_model": "grut_gate_kspace_v0",
        "alpha_mem": 0.5,
        "A_psi": 1.0,
        "fov_arcmin": 10.0,
        "smoothing_grid": [1.0],
        "threshold_grid": [0.1],
        "peak_mode": "com_positive_kappa",
        "gas_centroid_mode": "com_positive",
        "normalize_mode": "none",
        "pixel_scale_arcsec": 60.0,
        "band_gate_config": {"k0_policy": "fov"},
        "compare_to_baseline": True,
    }

    result = run_cluster_prediction(config, str(outdir))
    assert result["certificate"]["output_digest"]

    comparison = json.loads((outdir / "comparison.json").read_text())
    assert comparison["rms_kappa_diff"] > 0.0
    assert comparison["corr_kappa"] < 1.0


def test_k0_policy_logging(tmp_path):
    n = 64
    sigma_b = _gaussian_map(n, x0=32.0, y0=32.0, sigma=6.0)
    sigma_b_path = tmp_path / "sigma_b.npy"
    np.save(sigma_b_path, sigma_b)

    outdir = tmp_path / "prediction"
    config = {
        "sigma_baryon_path": str(sigma_b_path),
        "mode": "predict_kappa",
        "kernel": "k1",
        "response_model": "grut_gate_kspace_v0",
        "alpha_mem": 0.25,
        "A_psi": 1.0,
        "fov_arcmin": 10.0,
        "smoothing_grid": [1.0],
        "threshold_grid": [0.1],
        "peak_mode": "com_positive_kappa",
        "gas_centroid_mode": "com_positive",
        "normalize_mode": "none",
        "pixel_scale_arcsec": 60.0,
        "band_gate_config": {"k0_policy": "fov"},
    }

    run_cluster_prediction(config, str(outdir))
    summary = json.loads((outdir / "centroids_summary.json").read_text())
    gate_meta = summary["response_meta"]["grut_gate_kspace_v0"]
    assert gate_meta["k0_policy"] == "fov"
    assert gate_meta["k0_value_used"] > 0.0


def test_k0_r_smooth_reasonable(tmp_path):
    n = 64
    sigma_b = _gaussian_map(n, x0=32.0, y0=32.0, sigma=6.0)
    sigma_b_path = tmp_path / "sigma_b.npy"
    np.save(sigma_b_path, sigma_b)

    outdir = tmp_path / "prediction"
    config = {
        "sigma_baryon_path": str(sigma_b_path),
        "mode": "predict_kappa",
        "kernel": "k2",
        "response_model": "grut_gate_kspace_v0",
        "alpha_mem": 0.5,
        "A_psi": 1.0,
        "fov_arcmin": 10.0,
        "smoothing_grid": [0.0, 1.0, 2.0],
        "threshold_grid": [0.1],
        "peak_mode": "com_positive_kappa",
        "gas_centroid_mode": "com_positive",
        "normalize_mode": "none",
        "pixel_scale_arcsec": 60.0,
        "band_gate_config": {"k0_policy": "r_smooth"},
    }

    run_cluster_prediction(config, str(outdir))
    summary = json.loads((outdir / "centroids_summary.json").read_text())
    gate_meta = summary["response_meta"]["grut_gate_kspace_v0"]
    k0_value = float(gate_meta["k0_value_used"])

    fov_rad = float(summary["fov_rad"])
    dtheta = fov_rad / float(summary["grid_n"])
    k_max = np.pi / dtheta
    assert 0.01 * k_max <= k0_value <= 100.0 * k_max


def test_transfer_not_global(tmp_path):
    n = 64
    sigma_b = _gaussian_map(n, x0=32.0, y0=32.0, sigma=6.0)
    sigma_b_path = tmp_path / "sigma_b.npy"
    np.save(sigma_b_path, sigma_b)

    outdir = tmp_path / "prediction"
    config = {
        "sigma_baryon_path": str(sigma_b_path),
        "mode": "predict_kappa",
        "kernel": "k2",
        "response_model": "grut_gate_kspace_v0",
        "alpha_mem": 0.5,
        "A_psi": 1.0,
        "fov_arcmin": 10.0,
        "smoothing_grid": [1.0],
        "threshold_grid": [0.1],
        "peak_mode": "com_positive_kappa",
        "gas_centroid_mode": "com_positive",
        "normalize_mode": "none",
        "pixel_scale_arcsec": 60.0,
        "band_gate_config": {"k0_policy": "fov"},
    }

    run_cluster_prediction(config, str(outdir))
    summary = json.loads((outdir / "centroids_summary.json").read_text())
    gate_meta = summary["response_meta"]["grut_gate_kspace_v0"]
    transfer_min = float(gate_meta["transfer_min"])
    transfer_max = float(gate_meta["transfer_max"])
    assert (transfer_max - transfer_min) > 0.01 * float(summary["alpha_mem"])
