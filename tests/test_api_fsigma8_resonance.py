from fastapi.testclient import TestClient
from api.main import app


def make_simple_fs8():
    z = [0.0, 0.1, 0.2, 0.5, 1.0]
    fs8 = [0.45, 0.47, 0.5, 0.55, 0.52]
    return {"z": z, "fsigma8": fs8}


def test_resonance_map_basic_and_loo():
    client = TestClient(app)
    payload = {
        "data": make_simple_fs8(),
        "dt_myr": 10.0,
        "tau_candidates_myr": [10.0, 30.0, 100.0],
        "n_kernel": 64,
        "prior": "smooth",
        "lam_smooth": 1e-3,
        "leave_one_out": True,
    }

    r = client.post('/anamnesis/fsigma8_resonance_map', json=payload)
    assert r.status_code == 200, r.text
    j = r.json()

    per_point = j.get('per_point')
    assert per_point and len(per_point) == len(payload['data']['z'])
    assert any(p.get('delta_tau_leave_one_out') is not None for p in per_point)
    assert j.get('adapter_diagnostic') is not None
    assert j.get('dataset_hash') is not None
    assert j.get('winner') in ("baseline", "grut", "tie")
    assert j.get('run_id')
