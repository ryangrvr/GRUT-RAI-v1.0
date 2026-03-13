import json

import pytest

from grut.canon import GRUTCanon
from grut.engine import GRUTEngine


def test_same_inputs_same_repro_hash(tmp_path):
    canon = GRUTCanon("canon/grut_canon_v0.2.json")
    engine = GRUTEngine(canon, determinism_mode="STRICT")

    init = {"a": 1.0, "H": 1e-10, "rho": 1e-12, "p": 0.0, "M_X": 0.0}
    cfg = {"dt_years": 1e-3, "steps": 50, "integrator": "RK4"}

    out1, cert1 = engine.run(init, run_config=cfg, assumption_toggles={"deterministic_run": True})
    out2, cert2 = engine.run(init, run_config=cfg, assumption_toggles={"deterministic_run": True})

    assert cert1["outputs"]["output_digest"] == cert2["outputs"]["output_digest"]
    assert cert1["repro_hash"] == cert2["repro_hash"]


def test_missing_operator_raises():
    canon = GRUTCanon("canon/grut_canon_v0.2.json")
    canon.stack_order.append("OP_FAKE")
    with pytest.raises(Exception):
        GRUTEngine(canon, determinism_mode="STRICT")


def test_genesis_modes():
    canon = GRUTCanon("canon/grut_canon_v0.2.json")
    engine = GRUTEngine(canon, determinism_mode="STRICT")
    init = {"a": 1.0, "H": 1e-10, "rho": 1e-12, "p": 0.0, "M_X": 0.0}
    cfg = {"dt_years": 1e-3, "steps": 1, "integrator": "RK4"}

    out, cert = engine.run(init, run_config=cfg, assumption_toggles={})
    assert cert["initial_conditions"]["M_X_t0"] == cert["initial_conditions"]["H_base2_t0"]

    canon.data["genesis"]["memory_init"]["mode"] = "empty_history"
    engine2 = GRUTEngine(canon, determinism_mode="STRICT")
    out2, cert2 = engine2.run(init, run_config=cfg, assumption_toggles={})
    assert cert2["initial_conditions"]["M_X_t0"] == 0.0

    canon.data["genesis"]["memory_init"]["mode"] = "explicit"
    canon.data["genesis"]["memory_init"]["explicit_M_X"] = None
    engine3 = GRUTEngine(canon, determinism_mode="STRICT")
    with pytest.raises(ValueError):
        engine3.run(init, run_config=cfg, assumption_toggles={})


def test_gammaH_negative_raises():
    canon = GRUTCanon("canon/grut_canon_v0.2.json")
    canon.constants_by_id["NUM_GAMMA_H"]["value"] = -1.0
    engine = GRUTEngine(canon, determinism_mode="STRICT")
    init = {"a": 1.0, "H": 1e-10, "rho": 1e-12, "p": 0.0, "M_X": 0.0}
    cfg = {"dt_years": 1e-3, "steps": 1, "integrator": "RK4"}

    with pytest.raises(ValueError):
        engine.run(init, run_config=cfg, assumption_toggles={})


def test_rho_negative_raises():
    canon = GRUTCanon("canon/grut_canon_v0.2.json")
    engine = GRUTEngine(canon, determinism_mode="STRICT")
    init = {"a": 1.0, "H": 1e-10, "rho": -1.0, "p": 0.0, "M_X": 0.0}
    cfg = {"dt_years": 1e-3, "steps": 1, "integrator": "RK4"}

    with pytest.raises(ValueError):
        engine.run(init, run_config=cfg, assumption_toggles={})


def test_canon_hash_stable():
    canon = GRUTCanon("canon/grut_canon_v0.2.json")
    canon2 = GRUTCanon("canon/grut_canon_v0.2.json")
    assert canon.canon_hash == canon2.canon_hash