from grut.canon import GRUTCanon
from grut.engine import GRUTEngine


def _run_case(rho_is_rho0: bool) -> float:
    canon = GRUTCanon("canon/grut_canon_v0.3.json")
    engine = GRUTEngine(canon, determinism_mode="STRICT")
    init_state = {"rho": 0.2, "p": -0.2, "H": 1e-10, "M_X": 0.0}
    run_config = {"dt_years": 1e5, "steps": 10, "integrator": "RK4", "start_z": 2.0, "rho_is_rho0": rho_is_rho0}
    outputs, cert = engine.run(init_state, run_config=run_config, assumption_toggles={"deterministic_run": True})
    rho_used = cert.get("initial_conditions", {}).get("rho_init_used")
    return float(rho_used)


def test_start_z_rho_semantics_rho0_true():
    rho_used = _run_case(True)
    assert abs(rho_used - 0.2) < 1e-12


def test_start_z_rho_semantics_rho0_false():
    rho_used = _run_case(False)
    assert abs(rho_used - 0.2) < 1e-12