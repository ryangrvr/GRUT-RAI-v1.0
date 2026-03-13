"""Tests for Casimir Density / Alpha Screening sweep."""

from fastapi.testclient import TestClient
from api.main import app
import math


def _frange(start: float, stop: float, step: float):
    values = []
    x = start
    if step <= 0:
        return values
    while x <= stop + 1e-12:
        values.append(round(x, 12))
        x += step
    return values


def test_casimir_density_sweep_basic():
    client = TestClient(app)
    payload = {
        "tau0_myr": 41.9,
        "H0_km_s_Mpc": 67.36,
        "Omega_lambda": 0.6847,
        "h0_min": 67.0,
        "h0_max": 67.2,
        "h0_step": 0.1,
        "omegaL_min": 0.675,
        "omegaL_max": 0.685,
        "omegaL_step": 0.002,
        "alpha_vac": 1.0 / 3.0,
        "seed": 7,
    }

    r = client.post("/experiments/casimir_density_sweep", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["status"] in ("PASS", "EXPLORATORY", "FAIL")
    assert "computed" in data
    assert "rho_lambda" in data["computed"]
    assert "rho_req" in data["computed"]
    assert "R_obs" in data["computed"]
    assert "tau_lambda_s" in data["computed"]
    assert "S_thy" in data["computed"]

    assert "two_loop_argmin" in data
    argmin = data["two_loop_argmin"]
    assert all(k in argmin for k in ("H0_km_s_Mpc", "Omega_lambda", "rel_err_S", "tauLambda_gyr", "tau0_myr"))

    assert "rel_err_S_vs_H0" in data
    rel_err_vs_h0 = data["rel_err_S_vs_H0"]
    h0_values = _frange(payload["h0_min"], payload["h0_max"], payload["h0_step"])
    assert len(rel_err_vs_h0) == len(h0_values)

    assert "nis" in data
    assert "determinism_stamp" in data["nis"]
    assert "unit_consistency" in data["nis"]

    assert "metadata" in data
    assert "baseline_note" in data["metadata"]
    assert "velocity_potential_note" in data["metadata"]

    n_g0 = data["metadata"]["n_g0"]
    n_g0_sq = data["metadata"]["n_g0_sq"]
    assert math.isclose(n_g0_sq, 1.0 + payload["alpha_vac"], rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(n_g0, math.sqrt(1.0 + payload["alpha_vac"]), rel_tol=0.0, abs_tol=1e-12)

    run_id = data.get("run_id")
    assert run_id is not None

    # Verify run persisted
    r2 = client.get(f"/runs/{run_id}")
    assert r2.status_code == 200
    run = r2.json()
    assert run["kind"] == "casimir_density_sweep"

    # Determinism check (same inputs, same determinism stamp and argmin)
    r3 = client.post("/experiments/casimir_density_sweep", json=payload)
    assert r3.status_code == 200
    data2 = r3.json()
    assert data2["nis"]["determinism_stamp"] == data["nis"]["determinism_stamp"]
    assert data2["two_loop_argmin"] == data["two_loop_argmin"]
