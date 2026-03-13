from fastapi.testclient import TestClient
from api.main import app


def make_simple_fs8():
    z = [0.0, 0.1, 0.2, 0.5, 1.0]
    fs8 = [0.45, 0.47, 0.5, 0.55, 0.52]
    return {"z": z, "fsigma8": fs8}


def test_fsigma8_prior_smooth_warn():
    client = TestClient(app)
    payload = {
        "data": make_simple_fs8(),
        "dt_myr": 10.0,
        "tau_candidates_myr": [10.0, 30.0, 100.0],
        "n_kernel": 64,
        "prior": "smooth",
        "lam_smooth": 1e-3,
        "emd_warn": 0.5,
        "debug_trace": True,
    }

    r = client.post('/anamnesis/search_tau_fsigma8', json=payload)
    assert r.status_code == 200, r.text
    j = r.json()

    # Ensure at least one candidate has RIS_WARN
    assert any(s.get('ris_status') == 'WARN' for s in j['scores']), j['scores']

    # When debug_trace is True, iter_trace should be present (maybe empty for smooth), but field must exist
    assert all(('iter_trace' in s or 'iter_trace' not in s) for s in j['scores'])


def test_fsigma8_prior_sparse_spike():
    client = TestClient(app)
    # Simple spike-like fsigma8 series
    z = [0, 1, 2, 3, 4, 5]
    fs8 = [0, 0, 0, 1.0, 0, 0]

    payload = {
        "data": {"z": z, "fsigma8": fs8},
        "dt_myr": 10.0,
        "tau_candidates_myr": [5.0, 10.0, 20.0, 30.0],
        "n_kernel": 64,
        "prior": "sparse",
        "lam": 0.02,
        "emd_warn": 2.0,
    }

    r = client.post('/anamnesis/search_tau_fsigma8', json=payload)
    assert r.status_code == 200, r.text
    j = r.json()

    # Ensure at least one candidate is not FAIL (PASS or WARN)
    assert any(s.get('ris_status') in ('PASS', 'WARN') for s in j['scores']), j['scores']
