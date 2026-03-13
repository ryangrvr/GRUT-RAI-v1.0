from fastapi.testclient import TestClient
from api.main import app


def test_ui_title_and_header():
    client = TestClient(app)
    r = client.get('/ui')
    assert r.status_code == 200
    text = r.text
    assert 'GRUT Force RAI' in text
    assert 'Anamnesis' in text
    # header subtitle is present
    assert 'Narrative + Receipt' in text
