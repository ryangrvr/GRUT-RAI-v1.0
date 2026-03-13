import math

from grut.lensing import run_lensing


def test_lensing_bullet_toy_offset():
    config = {
        "n": 64,
        "fov_arcmin": 20.0,
        "sigma_crit": 1.0,
        "preset": "bullet_toy",
        "delta_arcmin": 2.0,
    }
    result = run_lensing(config)
    offset = result.summary["offset"]
    expected = 2.0 * config["delta_arcmin"]
    assert offset is not None
    assert math.isclose(offset["magnitude_arcmin"], expected, rel_tol=0.2, abs_tol=0.3)


def test_lensing_determinism():
    config = {
        "n": 64,
        "fov_arcmin": 20.0,
        "sigma_crit": 1.0,
        "preset": "bullet_toy",
        "delta_arcmin": 2.0,
    }
    r1 = run_lensing(config)
    r2 = run_lensing(config)
    assert r1.certificate["output_digest"] == r2.certificate["output_digest"]
