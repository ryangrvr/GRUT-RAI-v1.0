from fastapi.testclient import TestClient
from api.main import app

def test_ask_returns_dual_path():
    client = TestClient(app)
    payload = {
        "prompt": "why is the answer 42?",
        "run": {
            "engine": {"z_grid": [0.0, 0.5], "eps_t_myr": 0.10},
            "observer": {
                "profile": "participant",
                "v_obs_m_s": 200000,
                "ui_window": {"ui_actions": 10, "window_s": 10, "avg_param_delta": 0.4},
                "sensor": {"mode": "recorded", "snapshot": {"ambient_flux": 0.03}},
                "enable_observer_modulation": True
            }
        }
    }
    r = client.post("/ask", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data and "expandable" in data
    assert "text_markdown" in data["answer"]
    assert "sections" in data["expandable"]
    # Ensure raw + certificate are present
    labels = [s["label"] for s in data["expandable"]["sections"]]
    assert "Engine outputs" in labels
    assert "NIS certificate" in labels
