from fastapi.testclient import TestClient
from api.main import app


def make_simple_fs8():
    return {
        "z": [0.0, 0.1, 0.2, 0.5, 1.0],
        "fsigma8": [0.45, 0.47, 0.50, 0.55, 0.52],
    }


def test_suggest_returns_topics_for_fsigma8_tau_search():
    client = TestClient(app)
    payload = {
        "data": make_simple_fs8(),
        "dt_myr": 10.0,
        "tau_candidates_myr": [10.0, 30.0, 100.0],
        "n_kernel": 64,
        "lam": 0.02,
    }

    r = client.post("/anamnesis/search_tau_fsigma8", json=payload)
    assert r.status_code == 200, r.text
    run_id = r.json().get("run_id")
    assert run_id

    s = client.get(f"/suggest/{run_id}")
    assert s.status_code == 200, s.text
    data = s.json()
    suggestions = data.get("suggestions", [])

    topics = [sug.get("to_topic") for sug in suggestions]
    for expected in ["tau0-memory-window", "seth-kernel", "ris-certificate"]:
        assert expected in topics

    assert len(suggestions) <= 3
    assert all(sug.get("type") == "topic_link" for sug in suggestions)
    assert suggestions[0].get("confidence") in ("high", "medium", "low")
