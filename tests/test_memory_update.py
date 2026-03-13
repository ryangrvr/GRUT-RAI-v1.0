from pathlib import Path

from grut.canon import GRUTCanon
from grut.engine import GRUTEngine


def _make_engine():
    canon_path = Path(__file__).resolve().parents[1] / "canon" / "grut_canon_v0.2.json"
    canon = GRUTCanon(str(canon_path))
    return GRUTEngine(canon, determinism_mode="STRICT")


def test_memory_exact_update_avoids_freeze():
    engine = _make_engine()
    input_state = {
        "a": 1.0,
        "H": 1e-10,
        "rho": 0.2,
        "p": 0.0,
        "M_X": 0.0,
    }
    run_config = {
        "dt_years": 1.0,
        "steps": 200,
        "integrator": "RK4",
    }

    outputs, cert = engine.run(input_state, run_config=run_config, assumption_toggles={})
    hz = outputs.get("OBS_HZ_001", {})
    H_vals = hz.get("H", [])

    assert H_vals
    assert any(h > 0 for h in H_vals)
    assert cert.get("run_trace", {}).get("memory_update_scheme") == "EXACT_EXPONENTIAL_STRANG"
