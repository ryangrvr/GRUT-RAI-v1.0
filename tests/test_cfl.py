from fastapi.testclient import TestClient
from api.main import app

def test_cfl_hard_stop():
    client = TestClient(app)
    payload = {
        "engine": {
            "z_grid": [0.0, 1.0],
            "v_grid": [1.0e9, 1.0e9],
            "eps_t_myr": 0.15
        }
    }
    r = client.post("/runs", json=payload)
    assert r.status_code == 422
    data = r.json()
    assert data["status"] == "NIS_INTEGRITY_FAILURE"
    assert data["error_code"] == "CFL_VIOLATION"
    assert "correction_logic" in data
