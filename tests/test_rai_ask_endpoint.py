"""Tests for the /rai/ask and /rai/status endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from api.main import app
    return TestClient(app)


def test_rai_status(client):
    """GET /rai/status should return AI availability info."""
    r = client.get("/rai/status")
    assert r.status_code == 200
    d = r.json()
    assert "ai_available" in d
    assert "engine_version" in d
    assert "canon_hash" in d


def test_rai_ask_basic(client):
    """POST /rai/ask should accept a message and return a response."""
    r = client.post("/rai/ask", json={"message": "hello"})
    assert r.status_code == 200
    d = r.json()
    assert "session_id" in d
    assert "response" in d
    assert "text_markdown" in d["response"]


def test_rai_ask_theory_question(client):
    """POST /rai/ask with a theory question should return an explanation."""
    r = client.post("/rai/ask", json={"message": "What is tau0?"})
    assert r.status_code == 200
    d = r.json()
    text = d["response"]["text_markdown"].lower()
    assert "tau0" in text or "41.9" in text or "memory" in text


def test_rai_ask_run_request(client):
    """POST /rai/ask with a run request should return charts."""
    r = client.post("/rai/ask", json={"message": "run H(z)"})
    assert r.status_code == 200
    d = r.json()
    # Should have charts or certificate
    resp = d["response"]
    assert resp["text_markdown"]  # non-empty response


def test_rai_ask_session_persistence(client):
    """Session ID should persist across requests."""
    r1 = client.post("/rai/ask", json={"message": "hello"})
    sid = r1.json()["session_id"]

    r2 = client.post("/rai/ask", json={
        "session_id": sid,
        "message": "hello again"
    })
    assert r2.json()["session_id"] == sid


def test_rai_sessions_list(client):
    """GET /rai/sessions should return a list."""
    # Create a session first
    client.post("/rai/ask", json={"message": "hi"})
    r = client.get("/rai/sessions")
    assert r.status_code == 200
    d = r.json()
    assert "sessions" in d


def test_generate_sweep(client):
    """POST /generate/sweep should run a parameter sweep."""
    r = client.post("/generate/sweep", json={
        "preset": "matter_only",
        "grid": "0.0,0.1",
        "start_z": 2.0,
        "dt_years": 100000,
        "steps": 50,
    })
    assert r.status_code == 200
    d = r.json()
    assert d["completed"] == 2
    assert d["total"] == 2
    assert len(d["results"]) == 2


def test_chart_data_missing_run(client):
    """GET /runs/nonexistent/chart_data should 404."""
    r = client.get("/runs/nonexistent-id/chart_data")
    assert r.status_code == 404
