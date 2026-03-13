from fastapi.testclient import TestClient
from api.main import app
import json

client = TestClient(app)


def test_runs_compare_enabled():
    payload = {
        "engine": {
            "z_grid": [0.0, 0.5, 1.0],
        },
        "compare": {"enabled": True, "models": ["lcdm"], "metric": "l2"}
    }

    r = client.post("/runs", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "run_id" in data
    assert "comparison" in data
    cmp = data["comparison"]
    assert cmp["metric"] == "l2"
    assert "baseline" in cmp and "grut" in cmp


def test_anamnesis_includes_baseline():
    payload = {
        "y_obs": [0,0,0,1,0,0,0,0,0,0],
        "dt_s": 1.0,
        "tau_candidates_s": [1.0, 2.0, 5.0],
        "n_kernel": 16,
        "lam": 0.05,
        "max_iter": 500,
        "tol": 1e-6,
        "nonnegative": True,
        "emd_warn": 2.0,
        "emd_fail": 5.0,
        "residual_warn": 0.10,
        "residual_fail": 0.25,
    }

    r = client.post("/anamnesis/search_tau", json=payload)
    assert r.status_code == 200
    data = r.json()
    # Kernel info present
    assert data.get("kernel_name") == "seth"
    assert data.get("kernel_family") == "causal_exponential"
    scores = data.get("scores", [])
    assert any(s.get("label") == "tau0_baseline" for s in scores)
    assert "comparison" in data
    cmp = data["comparison"]
    assert cmp.get("baseline") and cmp.get("best") and cmp.get("delta")


def test_baseline_fail_does_not_crash_selection():
    # Make baseline fail by setting residual_fail=0 (baseline residual > 0)
    payload = {
        "y_obs": [0,0,0,1,0,0,0,0,0,0],
        "dt_s": 1.0,
        "tau_candidates_s": [1.0, 2.0, 5.0],
        "n_kernel": 16,
        "lam": 0.05,
        "max_iter": 500,
        "tol": 1e-6,
        "nonnegative": True,
        "emd_warn": 2.0,
        "emd_fail": 5.0,
        "residual_warn": 0.10,
        "residual_fail": 0.0,
    }

    r = client.post("/anamnesis/search_tau", json=payload)
    assert r.status_code == 200
    data = r.json()
    # Even if baseline FAILs, best selection should exist or gracefully indicate fail
    assert "scores" in data


def test_published_snapshot_includes_comparison():
    # Run with compare enabled
    payload = {
        "engine": {"z_grid": [0.0, 0.5, 1.0]},
        "compare": {"enabled": True, "models": ["lcdm"], "metric": "l2"}
    }
    r = client.post("/runs", json=payload)
    assert r.status_code == 200
    run_id = r.json()["run_id"]
    cmp = r.json().get("comparison")
    assert cmp is not None

    pub = client.post(f"/runs/{run_id}/publish")
    assert pub.status_code == 200
    slug = pub.json()["slug"]

    info = client.get(f"/p/{slug}/info")
    assert info.status_code == 200
    evidence = info.json().get("evidence_packet")
    assert evidence is not None
    # response should include comparison block
    assert evidence.get("response", {}).get("comparison") is not None
