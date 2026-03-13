"""Tests for Zeta–Tau Scaling experiment."""

from fastapi.testclient import TestClient
from api.main import app


def test_zeta_tau_scaling_basic():
    """Test Zeta–Tau Scaling experiment returns valid structure."""
    client = TestClient(app)
    payload = {
        "tau0_myr": 41.9,
        "H0_km_s_Mpc": 67.4,
        "zeros_n": 10,
        "eps_hit": 0.01,
        "null_trials": 100,
        "h0_perturb_frac": 0.02,
        "seed": 7,
    }

    r = client.post("/experiments/zeta_tau_scaling", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()

    # Check status
    assert data["status"] in ("PASS", "WARN", "FAIL")

    # Check best match
    assert "best_match" in data
    bm = data["best_match"]
    assert "family" in bm
    assert "tau_pred_myr" in bm
    assert isinstance(bm["rel_err"], float)
    assert bm["rel_err"] >= 0.0

    # Check robustness
    assert "robustness" in data
    rob = data["robustness"]
    assert "h0_minus_ok" in rob
    assert "h0_plus_ok" in rob

    # Check null model
    assert "null_model" in data
    null = data["null_model"]
    assert null["null_trials"] == 100
    assert 0.0 <= null["p_value"] <= 1.0
    assert isinstance(null["observed_best_err"], float)

    # Check tested counts
    assert "tested_counts" in data
    assert "N_zeros" in data["tested_counts"]
    assert "K_hypotheses" in data["tested_counts"]

    # Check constants
    assert "constants" in data
    const = data["constants"]
    assert const["tau0_myr"] == 41.9
    assert const["H0_km_s_Mpc"] == 67.4

    # Check run saved
    assert "run_id" in data
    run_id = data["run_id"]

    # Verify run persisted
    r2 = client.get(f"/runs/{run_id}")
    assert r2.status_code == 200
    run = r2.json()
    assert run["kind"] == "zeta_tau_scaling"


def test_zeta_tau_scaling_determinism():
    """Test that same seed gives same results."""
    client = TestClient(app)
    payload = {
        "tau0_myr": 41.9,
        "H0_km_s_Mpc": 67.4,
        "zeros_n": 10,
        "eps_hit": 0.01,
        "null_trials": 100,
        "h0_perturb_frac": 0.02,
        "seed": 7,
    }

    r1 = client.post("/experiments/zeta_tau_scaling", json=payload)
    assert r1.status_code == 200
    data1 = r1.json()

    r2 = client.post("/experiments/zeta_tau_scaling", json=payload)
    assert r2.status_code == 200
    data2 = r2.json()

    # Compare key fields
    assert data1["best_match"]["tau_pred_myr"] == data2["best_match"]["tau_pred_myr"]
    assert data1["best_match"]["rel_err"] == data2["best_match"]["rel_err"]
    assert data1["null_model"]["p_value"] == data2["null_model"]["p_value"]


def test_zeta_tau_scaling_publishable():
    """Test that results can be published."""
    client = TestClient(app)
    payload = {
        "tau0_myr": 41.9,
        "H0_km_s_Mpc": 67.4,
        "zeros_n": 10,
        "eps_hit": 0.01,
        "null_trials": 100,
        "h0_perturb_frac": 0.02,
        "seed": 7,
    }

    r = client.post("/experiments/zeta_tau_scaling", json=payload)
    assert r.status_code == 200
    run_id = r.json()["run_id"]

    # Publish
    pub = client.post(f"/runs/{run_id}/publish")
    assert pub.status_code == 200
    pub_info = pub.json()
    assert "slug" in pub_info
    assert "revision" in pub_info

    slug = pub_info["slug"]

    # Retrieve published
    pub_get = client.get(f"/p/{slug}")
    assert pub_get.status_code == 200
    packet = pub_get.json()
    assert packet is not None


def test_zeta_tau_scaling_linked_to_topic():
    """Test that PASS results auto-link to zeta-operator topic."""
    client = TestClient(app)
    payload = {
        "tau0_myr": 41.9,
        "H0_km_s_Mpc": 67.4,
        "zeros_n": 10,
        "eps_hit": 0.1,  # Larger threshold for easier PASS in tests
        "null_trials": 100,
        "h0_perturb_frac": 0.02,
        "seed": 7,
    }

    r = client.post("/experiments/zeta_tau_scaling", json=payload)
    assert r.status_code == 200
    status = r.json()["status"]
    run_id = r.json()["run_id"]

    # Check zeta-operator topic has links if status is PASS or WARN
    if status in ("PASS", "WARN"):
        t = client.get("/grutipedia/zeta-operator")
        assert t.status_code == 200
        topic = t.json()
        links = topic.get("links", [])
        link_ids = [l.get("run_id") for l in links]
        # Should be linked
        assert run_id in link_ids
