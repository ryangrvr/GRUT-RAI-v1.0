import math

from grut.canon import GRUTCanon
from grut.engine import GRUTEngine


def _make_engine():
    canon = GRUTCanon("canon/grut_canon_v0.3.json")
    return GRUTEngine(canon, determinism_mode="STRICT")


def test_fs8_emits_and_lengths_match():
    engine = _make_engine()
    init_state = {
        "rho": 0.2,
        "p": -0.2,
        "H": 1e-10,
        "M_X": 0.0,
    }
    config = {
        "dt_years": 1e5,
        "steps": 200,
        "integrator": "RK4",
        "start_z": 2.0,
    }

    outputs, cert = engine.run(init_state, run_config=config, assumption_toggles={"growth_enabled": True})
    assert cert.get("run_trace", {}).get("growth_enabled") is True

    fs8 = outputs.get("OBS_FS8_001")
    assert fs8 is not None
    z = fs8.get("z", [])
    fsigma8 = fs8.get("fsigma8", [])
    fs8_mask = fs8.get("fs8_mask", [])
    assert len(z) == config["steps"]
    assert len(fsigma8) == config["steps"]
    assert len(fs8_mask) == config["steps"]

    for series in (z, fs8.get("f", []), fs8.get("sigma8", []), fs8.get("D_over_D0", [])):
        assert len(series) == config["steps"]
        assert all(math.isfinite(x) for x in series)

    for value, masked in zip(fsigma8, fs8_mask):
        if masked:
            assert value is None
        else:
            assert value is not None
            assert math.isfinite(value)

    assert z[0] > 1.0
    assert min(abs(val) for val in z) < 0.2

    hz = outputs.get("OBS_HZ_001", {})
    H_vals = hz.get("H", [])
    if any(h < 1e-12 for h in H_vals):
        assert any(fs8_mask)


def test_fs8_determinism():
    engine = _make_engine()
    init_state = {
        "rho": 0.2,
        "p": -0.2,
        "H": 1e-10,
        "M_X": 0.0,
    }
    config = {
        "dt_years": 1e5,
        "steps": 200,
        "integrator": "RK4",
        "start_z": 2.0,
    }

    outputs1, cert1 = engine.run(init_state, run_config=config, assumption_toggles={"growth_enabled": True})
    outputs2, cert2 = engine.run(init_state, run_config=config, assumption_toggles={"growth_enabled": True})

    assert cert1.get("outputs", {}).get("output_digest") == cert2.get("outputs", {}).get("output_digest")
    assert cert1.get("repro_hash") == cert2.get("repro_hash")
    assert outputs1.get("OBS_FS8_001") == outputs2.get("OBS_FS8_001")


def test_growth_disable():
    engine = _make_engine()
    init_state = {
        "rho": 0.2,
        "p": -0.2,
        "H": 1e-10,
        "M_X": 0.0,
    }
    config = {
        "dt_years": 1e5,
        "steps": 200,
        "integrator": "RK4",
        "start_z": 2.0,
    }

    outputs, cert = engine.run(init_state, run_config=config, assumption_toggles={"growth_enabled": False})
    assert cert.get("run_trace", {}).get("growth_enabled") is False
    assert "OBS_FS8_001" not in outputs


def test_fs8_mask_when_H_zero():
    engine = _make_engine()
    init_state = {
        "rho": 0.0,
        "p": 0.0,
        "H": 0.0,
        "M_X": 0.0,
    }
    config = {
        "dt_years": 1e5,
        "steps": 5,
        "integrator": "RK4",
        "start_z": 2.0,
    }

    outputs, cert = engine.run(init_state, run_config=config, assumption_toggles={"growth_enabled": True})
    fs8 = outputs.get("OBS_FS8_001")
    assert fs8 is not None
    fsigma8 = fs8.get("fsigma8", [])
    fs8_mask = fs8.get("fs8_mask", [])
    assert fs8_mask
    assert fs8_mask[0] is True
    assert fsigma8[0] is None
    assert cert.get("run_trace", {}).get("fsigma8_masking_enabled") is True


def test_growth_with_explicit_rho_m():
    engine = _make_engine()
    init_state = {
        "rho": 0.2,
        "p": -0.2,
        "rho_m0": 0.2,
        "H": 1e-10,
        "M_X": 0.0,
    }
    config = {
        "dt_years": 1e5,
        "steps": 200,
        "integrator": "RK4",
        "start_z": 2.0,
    }

    outputs, cert = engine.run(init_state, run_config=config, assumption_toggles={"growth_enabled": True})
    fs8 = outputs.get("OBS_FS8_001")
    assert fs8 is not None
    fs8_mask = fs8.get("fs8_mask", [])
    assert sum(1 for m in fs8_mask if m) < config["steps"]
    D0 = cert.get("run_trace", {}).get("growth_D0")
    assert D0 is not None and math.isfinite(D0) and D0 > 0.0


def test_growth_vacuum_defaults_to_zero_matter():
    engine = _make_engine()
    init_state = {
        "rho": 0.2,
        "p": -0.2,
        "H": 1e-10,
        "M_X": 0.0,
    }
    config = {
        "dt_years": 1e5,
        "steps": 50,
        "integrator": "RK4",
        "start_z": 2.0,
    }

    outputs, cert = engine.run(init_state, run_config=config, assumption_toggles={"growth_enabled": True})
    fs8 = outputs.get("OBS_FS8_001")
    assert fs8 is not None
    fsigma8 = fs8.get("fsigma8", [])
    assert all((v is None) or abs(v) < 1e-8 for v in fsigma8)
    D0 = cert.get("run_trace", {}).get("growth_D0")
    assert D0 is not None and math.isfinite(D0) and D0 > 0.0
