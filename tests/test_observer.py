from fastapi.testclient import TestClient
from api.main import app


def test_monk_is_still_point():
    client = TestClient(app)
    payload = {
        "engine": {"z_grid": [0.0, 1.0], "eps_t_myr": 0.10},
        "observer": {
            "profile": "monk",
            # even if user provides UI/sensor inputs, monk should ignore them
            "ui_window": {"ui_actions": 50, "window_s": 10, "avg_param_delta": 1.0},
            "sensor": {"mode": "ambient", "ambient_flux": 1.0},
        },
    }
    r = client.post("/runs", json=payload)
    assert r.status_code == 200
    data = r.json()
    nis = data["nis"]
    assert nis["observer_profile"] == "monk"
    assert abs(nis["deltaS"]) < 1e-12
    assert abs(nis["ui_entropy"]) < 1e-12
    assert abs(nis["sensor_flux"]) < 1e-12


def test_participant_engagement_moves_deltaS():
    client = TestClient(app)
    payload = {
        "engine": {"z_grid": [0.0, 1.0], "eps_t_myr": 0.10},
        "observer": {
            "profile": "participant",
            "ui_window": {"ui_actions": 10, "window_s": 20, "avg_param_delta": 0.5},
            "sensor": {"mode": "ambient", "ambient_flux": 0.2},
            "info_cfg": {"eta": 1.0},
        },
    }
    r = client.post("/runs", json=payload)
    assert r.status_code == 200
    nis = r.json()["nis"]
    assert nis["observer_profile"] == "participant"
    assert nis["deltaS"] > 0.0
    assert nis["I_value"] >= 1.0
    assert nis["tension_score"] >= 0.0
