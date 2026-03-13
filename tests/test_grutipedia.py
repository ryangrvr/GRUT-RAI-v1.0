"""Tests for GRUTipedia MVP endpoints."""

from fastapi.testclient import TestClient
from api.main import app


def test_seed_topics_created():
    client = TestClient(app)
    r = client.get('/grutipedia')
    assert r.status_code == 200
    data = r.json()
    topics = data.get('topics', [])
    slugs = [t['slug'] for t in topics]
    # Ensure seeded topics exist
    assert 'tau0-memory-window' in slugs
    assert 'nis-and-ris-certificates' in slugs


def test_link_run_to_topic():
    client = TestClient(app)

    # Create a small demo run
    payload = {
        "n": 64,
        "dt_s": 1.0,
        "tau_s": 10.0,
        "n_kernel": 32,
        "lam": 0.02,
        "max_iter": 50,
        "noise_std": 0.0,
        "spikes": [{"index": 15, "amplitude": 1.0}],
        "seed": 2,
    }

    r1 = client.post('/anamnesis/demo', json=payload)
    assert r1.status_code == 200
    run_id = r1.json().get('run_id')
    assert run_id

    # Link the run to the topic
    r_link = client.post(f'/grutipedia/tau0-memory-window/link', json={"run_id": run_id, "note_md": "Test link"})
    assert r_link.status_code == 200

    # Verify topic returns the link
    r_topic = client.get('/grutipedia/tau0-memory-window')
    assert r_topic.status_code == 200
    data = r_topic.json()
    links = data.get('links', [])
    ids = [l['run_id'] for l in links]
    assert run_id in ids


def test_get_topic_returns_links():
    client = TestClient(app)
    r = client.get('/grutipedia/tau0-memory-window')
    assert r.status_code == 200
    data = r.json()
    # links present (may be empty but structure should exist)
    assert 'links' in data
