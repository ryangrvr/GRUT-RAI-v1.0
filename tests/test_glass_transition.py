"""Tests for Glass Transition (Cosmological Deborah Sweep)."""

from fastapi.testclient import TestClient
from api.main import app


def test_glass_transition_sweep_basic():
    client = TestClient(app)
    payload = {
        "tau0_myr": 41.9,
        "H0_km_s_Mpc": 67.36,
        "Omega_m": 0.315,
        "Omega_lambda": 0.6847,
        "Omega_r": 9.24e-5,
        "T_cmb_K": 2.725,
        "z_min": 0.0,
        "z_max": 1.0e4,
        "n_samples": 300,
        "include_scan_data": False,
        "pass_z_min": 1100.0,
        "pass_z_max": 1300.0,
        "warn_z_max": 1e-6,
    }

    r = client.post("/experiments/glass_transition_sweep", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["status"] == "FAIL"
    crossing = data["crossing"]
    assert all(k in crossing for k in ("z_crit", "age_myr", "T_K", "De"))

    run_id = data.get("run_id")
    assert run_id is not None

    r2 = client.get(f"/runs/{run_id}")
    assert r2.status_code == 200
    run = r2.json()
    assert run["kind"] == "glass_transition_sweep"
