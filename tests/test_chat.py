from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_chat_only_path():
    resp = client.post("/rai/chat", json={"message": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("assistant_message")
    assert data.get("grut_outputs") is None
    assert data.get("nis_certificate") is None

    session_id = data.get("session_id")
    assert session_id

    session_resp = client.get(f"/rai/session/{session_id}")
    assert session_resp.status_code == 200
    session_data = session_resp.json()
    assert session_data["state"]["last_user_message"] == "hello"
    event_types = [e["type"] for e in session_data.get("events", [])]
    assert "USER_MESSAGE" in event_types
    assert "ASSISTANT_MESSAGE" in event_types


def test_chat_grut_run_path_and_determinism():
    resp1 = client.post("/rai/chat", json={"message": "run H(z)"})
    assert resp1.status_code == 200
    data1 = resp1.json()
    cert1 = data1.get("nis_certificate")
    assert cert1
    assert cert1.get("repro_hash")
    assert cert1.get("engine_signature", {}).get("canon_hash")
    assert cert1.get("outputs", {}).get("output_digest")

    session_id = data1.get("session_id")
    assert session_id

    session_resp = client.get(f"/rai/session/{session_id}")
    assert session_resp.status_code == 200
    session_data = session_resp.json()
    event_types = [e["type"] for e in session_data.get("events", [])]
    assert "GRUT_RUN_COMPLETED" in event_types

    resp2 = client.post("/rai/chat", json={"session_id": session_id, "message": "run H(z)"})
    assert resp2.status_code == 200
    data2 = resp2.json()
    cert2 = data2.get("nis_certificate")
    assert cert2

    assert cert1.get("repro_hash") == cert2.get("repro_hash")
    assert cert1.get("outputs", {}).get("output_digest") == cert2.get("outputs", {}).get("output_digest")
