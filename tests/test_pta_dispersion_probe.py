import math

from fastapi.testclient import TestClient

from api.main import app


def test_pta_dispersion_probe_schema_and_determinism():
    client = TestClient(app)
    mpc_over_c_s = 3.085677581e22 / 2.99792458e8
    payload = {
        "tau0_myr": 41.92,
        "alpha_scr": 1.0 / 3.0,
        "freqs_hz": [1e-9, 1e-8, 1e-7],
        "use_group_velocity": True,
        "apply_to_gw_propagation": True,
        "seed": 7,
    }

    r = client.post("/experiments/pta_dispersion_probe", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()

    assert "run_id" in data
    assert "timestamp" in data
    assert "status" in data
    assert "assumptions" in data
    assert "results" in data
    assert "comparisons" in data
    assert "hf_check_100Hz" in data
    assert "cited_limits" in data
    assert "conclusion" in data
    assert data["pta_direct_dispersion_bound_present"] is True
    assert data["exclusion_basis"] in ("PTA_SPEED_GATE_PRIMARY", "PTA_SPEED_GATE")
    assert data["worst_margin_over_band"] > 1.0
    assert data["min_v_phase_over_c_over_band"] > 0.87

    results = data["results"]
    assert len(results) == 3
    comparisons = data["comparisons"]
    assert len(comparisons) == 3

    # Monotonic behavior: Reχ decreases with frequency ⇒ ng2 decreases, n approaches 1
    ng2_vals = [row["ng2"] for row in results]
    n_vals = [row["n"] for row in results]
    assert ng2_vals[0] >= ng2_vals[1] >= ng2_vals[2]
    assert n_vals[0] >= n_vals[1] >= n_vals[2]
    assert n_vals[-1] >= 1.0
    assert n_vals[-1] - 1.0 < n_vals[0] - 1.0

    # delta_vg present and nonzero at low frequency
    assert abs(results[0]["delta_vg"]) > 0.0
    assert abs(results[1]["delta_vg"]) > 0.0
    assert "delay_sign" in results[0]
    assert math.isclose(
        results[1]["delay_s_per_Mpc"],
        -mpc_over_c_s * results[1]["delta_vg"],
        rel_tol=1e-12,
        abs_tol=0.0,
    )
    assert math.isclose(
        results[2]["delay_s_per_Mpc"],
        -mpc_over_c_s * results[2]["delta_vg"],
        rel_tol=1e-12,
        abs_tol=0.0,
    )

    # mg comparison present
    assert comparisons[0]["mg_equiv_abs_eV"] >= 0.0
    assert comparisons[0]["mg_mapping_mode"] in ("like_for_like", "magnitude_proxy_only")
    assert comparisons[0]["mg_limit_eV"] == 8.2e-24
    assert math.isfinite(comparisons[0]["mg_margin"])
    assert comparisons[0]["mg_exclusion_flag"] in (
        "EXCLUDED_BY_PTA_MG_PROXY",
        "NOT_EXCLUDED_BY_PTA_MG_PROXY",
    )

    # HF sanity check should pass for default parameters
    assert comparisons[0]["hf_sanity_flag"] == "PASS"
    assert data["status"] == "PASS_NOT_EXCLUDED"

    # Deterministic output
    r2 = client.post("/experiments/pta_dispersion_probe", json=payload)
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["results"] == data["results"]
    assert data2["status"] == data["status"]


def test_pta_dispersion_probe_status_gate_fail_sanity():
    client = TestClient(app)
    payload = {
        "tau0_myr": 41.92,
        "alpha_scr": 1.0 / 3.0,
        "freqs_hz": [1e-9],
        "use_group_velocity": True,
        "f_hf_hz": 1e-9,
        "apply_to_gw_propagation": True,
        "seed": 7,
    }

    r = client.post("/experiments/pta_dispersion_probe", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "FAIL_HF_SANITY"


def test_pta_dispersion_probe_hf_interval_gate():
    client = TestClient(app)
    payload = {
        "tau0_myr": 41.92,
        "alpha_scr": 1.0 / 3.0,
        "freqs_hz": [1e-9],
        "use_group_velocity": True,
        "f_hf_hz": 1e-9,
        "apply_to_gw_propagation": True,
        "seed": 7,
    }

    r = client.post("/experiments/pta_dispersion_probe", json=payload)
    assert r.status_code == 200
    data = r.json()

    hf_limit = next(
        limit for limit in data["cited_limits"] if "GW170817" in limit.get("name", "")
    )
    delta_vg_hf = data["hf_check_100Hz"]["delta_vg"]
    assert delta_vg_hf > hf_limit["value_high"]
    assert abs(delta_vg_hf) <= abs(hf_limit["value_low"])
    assert data["status"] == "FAIL_HF_SANITY"


def test_pta_dispersion_probe_speed_gate():
    client = TestClient(app)
    payload = {
        "tau0_myr": 41.92,
        "alpha_scr": 1.0e18,
        "freqs_hz": [1e-9, 1e-8],
        "use_group_velocity": True,
        "apply_to_gw_propagation": True,
        "seed": 7,
    }

    r = client.post("/experiments/pta_dispersion_probe", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "EXCLUDED_BY_PTA_SPEED"


def test_pta_dispersion_probe_not_applicable():
    client = TestClient(app)
    payload = {
        "tau0_myr": 41.92,
        "alpha_scr": 1.0 / 3.0,
        "freqs_hz": [1e-9],
        "use_group_velocity": True,
        "apply_to_gw_propagation": False,
        "seed": 7,
    }

    r = client.post("/experiments/pta_dispersion_probe", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "NOT_APPLICABLE"
