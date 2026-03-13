import math

from grut.lensing import run_lensing


def test_lensing_phi_bullet_offset():
    config = {
        "n": 64,
        "fov_arcmin": 20.0,
        "sigma_crit": 1.0,
        "mode": "phi_to_psi",
        "phi_preset": "bullet_phi_toy",
        "A_psi": 1.0,
        "delta_arcmin": 2.0,
    }
    result = run_lensing(config)
    offset = result.summary["offset"]
    expected = 2.0 * config["delta_arcmin"]
    assert offset is not None
    assert math.isclose(offset["magnitude_arcmin"], expected, rel_tol=0.2, abs_tol=0.3)


def test_lensing_phi_determinism():
    config = {
        "n": 64,
        "fov_arcmin": 20.0,
        "sigma_crit": 1.0,
        "mode": "phi_to_psi",
        "phi_preset": "bullet_phi_toy",
        "A_psi": 1.0,
        "delta_arcmin": 2.0,
    }
    r1 = run_lensing(config)
    r2 = run_lensing(config)
    assert r1.certificate["output_digest"] == r2.certificate["output_digest"]
    assert r1.psi is not None
    assert r1.alpha_x is not None
    assert r1.alpha_y is not None


def test_lensing_phi_symmetry_padded():
    config = {
        "n": 128,
        "fov_arcmin": 20.0,
        "sigma_crit": 1.0,
        "mode": "phi_to_psi",
        "phi_preset": "bullet_phi_toy",
        "A_psi": 1.0,
        "phi_mass_amp": 1e-6,
        "phi_gas_amp": 7e-7,
        "pad_factor": 2,
        "delta_arcmin": 2.0,
        "peak_mode": "com_positive_kappa",
    }
    result = run_lensing(config)
    peak_y = result.summary["peak_kappa"]["theta_y_arcmin"]
    assert abs(peak_y) <= 0.2

    kappa = result.kappa
    n = kappa.shape[0]
    for j in (10, 20, 30, 40):
        top = kappa[j, :]
        bottom = kappa[n - 1 - j, :]
        diff = abs(top - bottom)
        assert diff.mean() < 5e-2
