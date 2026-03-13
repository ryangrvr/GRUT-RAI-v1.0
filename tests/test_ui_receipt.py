from fastapi.testclient import TestClient
from api.main import app


def test_ui_receipt_placeholders_exist():
    client = TestClient(app)
    r = client.get('/ui')
    assert r.status_code == 200
    text = r.text
    # Receipt elements
    assert 'runIdShort' in text
    assert 'resultStatusBadge' in text
    assert 'paramsHash' in text
    assert 'bundleHash' in text
    assert 'copy-run-btn' in text
    assert 'suggestedActions' in text
    # Accordion sections placeholders
    assert 'Certificate (NIS/RIS)' in text
    assert 'Key equations' in text
    assert 'Comparison (if present)' in text
    assert 'Engine outputs' in text
    assert 'Observer layer' in text
    assert 'Raw response JSON' in text
