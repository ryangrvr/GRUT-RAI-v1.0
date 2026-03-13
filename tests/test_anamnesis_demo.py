from fastapi.testclient import TestClient
from api.main import app


def test_anamnesis_demo_smoke():
    client = TestClient(app)
    payload = {
        "n": 128,
        "dt_s": 1.0,
        "tau_s": 30.0,
        "spikes": [{"index": 20, "amplitude": 1.0}, {"index": 80, "amplitude": 0.7}],
        "noise_std": 0.01,
        "lam": 0.02,
        "seed": 1,
    }
    r = client.post("/anamnesis/demo", json=payload)
    assert r.status_code == 200, r.text
    j = r.json()
    assert "kernel" in j
    assert "observed" in j
    assert "reconstructed_source" in j
    assert "reconstructed_observed" in j
    assert "ris" in j
    assert j["ris"]["status"] in ("PASS", "WARN", "FAIL")


def test_anamnesis_demo_high_lam_fails():
    client = TestClient(app)
    payload = {
        "n": 128,
        "dt_s": 1.0,
        "tau_s": 30.0,
        "spikes": [{"index": 20, "amplitude": 1.0}, {"index": 80, "amplitude": 0.7}],
        "noise_std": 0.0,
        "lam": 0.5,
        "seed": 1,
    }
    r = client.post("/anamnesis/demo", json=payload)
    assert r.status_code == 200, r.text
    j = r.json()
    # Expect the RIS to indicate a failing reconstruction with high lambda
    assert j["ris"]["status"] == "FAIL" or float(j["ris"]["emd"]) > 10.0


def test_anamnesis_demo_easy_pass():
    """Easy deterministic demo should PASS with aligned dt/tau and low lambda."""
    client = TestClient(app)
    payload = {
        "n": 256,
        "dt_s": 1.0,
        "tau_s": 30.0,
        "n_kernel": 128,
        "spikes": [{"index": 40, "amplitude": 1.0}, {"index": 150, "amplitude": 0.7}],
        "noise_std": 0.0,
        "lam": 0.01,
        "max_iter": 4000,
        "seed": 1,
    }
    r = client.post("/anamnesis/demo", json=payload)
    assert r.status_code == 200, r.text
    j = r.json()
    # With low noise and small lambda we expect a PASS
    assert j["ris"]["status"] == "PASS", j["ris"]

    # Ensure iter_trace exists and shows movement (nnz or max_abs_x > tiny)
    iter_trace = j["diagnostic"].get("iter_trace", [])
    assert len(iter_trace) > 0
    assert any(entry.get("nnz", 0) > 0 or entry.get("max_abs_x", 0.0) > 1e-6 for entry in iter_trace)

    # Diagnostics should report the effective kernel parameters and kernel hashes
    diag = j["diagnostic"]
    assert float(diag.get("effective_dt_s", 0.0)) == 1.0
    assert float(diag.get("effective_tau_s", 0.0)) == 30.0
    assert int(diag.get("effective_n_kernel", 0)) == 128
    assert "kernel_hash" in diag and "kernel_hash_used_by_reconstructor" in diag
    assert diag["kernel_hash"] == diag["kernel_hash_used_by_reconstructor"]

    # Recovery & solver expectations: ensure at least one spike recovered within ±2 bins
    recovery = diag.get("spike_recovery", {})
    assert recovery.get("recovered_topk_count", 0) >= 1 or recovery.get("recovered_topk_within_tol_count", 0) >= 1
    # Ensure solver actually iterated past min_iters and residual is small
    assert int(j["ris"]["iters"]) >= 25
    assert float(j["diagnostic"]["residual_norm"]) < 0.05


def test_anamnesis_demo_drm_mismatch(monkeypatch):
    """If the reconstructor reports a different kernel hash, we should FAIL with DRM_MISMATCH."""
    import api.main as api_main

    original = api_main.lca_reconstruct

    def fake_lca_reconstruct(y, A, cfg, kernel_hash=None):
        res = original(y, A, cfg, kernel_hash=kernel_hash)
        # force a mismatch
        res.diagnostics["kernel_hash_used_by_reconstructor"] = "badhash"
        return res

    monkeypatch.setattr(api_main, "lca_reconstruct", fake_lca_reconstruct)

    client = TestClient(app)
    payload = {
        "n": 256,
        "dt_s": 1.0,
        "tau_s": 30.0,
        "n_kernel": 128,
        "spikes": [{"index": 40, "amplitude": 1.0}, {"index": 150, "amplitude": 0.7}],
        "noise_std": 0.0,
        "lam": 0.005,
        "seed": 1,
    }
    r = client.post("/anamnesis/demo", json=payload)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["ris"]["status"] == "FAIL"
    assert j["ris"]["message"] == "DRM_MISMATCH"
    assert j["diagnostic"].get("error_code") == "DRM_MISMATCH"
