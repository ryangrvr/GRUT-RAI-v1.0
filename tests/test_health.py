from fastapi.testclient import TestClient
from api.main import app

def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "engine_version" in data
    assert "params_hash" in data
