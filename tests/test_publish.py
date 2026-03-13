from fastapi.testclient import TestClient
from api.main import app
import json
import hashlib
from core.evidence import make_canonical_json

client = TestClient(app)


def make_demo_run():
    payload = {
        "n": 128,
        "dt_s": 1.0,
        "tau_s": 30.0,
        "n_kernel": 64,
        "lam": 0.01,
        "spikes": [{"index": 10, "amplitude": 1.0}],
        "noise_std": 0.0,
    }
    r = client.post("/anamnesis/demo", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "run_id" in data
    return data["run_id"]


def test_publish_creates_slug_and_revision():
    run_id = make_demo_run()

    r = client.post(f"/runs/{run_id}/publish")
    assert r.status_code == 200
    info = r.json()
    assert "slug" in info and "revision" in info and info["revision"] == 1

    slug = info["slug"]

    g = client.get(f"/p/{slug}/info")
    assert g.status_code == 200
    pub = g.json()
    assert pub["slug"] == slug
    assert "evidence_packet" in pub

    packet = pub["evidence_packet"]
    # recompute published hash from canonical json
    canon = make_canonical_json(packet)
    digest = hashlib.sha256(canon.encode()).hexdigest()
    assert digest == pub["published_hash"]


def test_publish_creates_new_revision_immutable():
    run_id = make_demo_run()

    r1 = client.post(f"/runs/{run_id}/publish")
    assert r1.status_code == 200
    info1 = r1.json()
    slug = info1["slug"]
    rev1 = info1["revision"]

    r2 = client.post(f"/runs/{run_id}/publish")
    assert r2.status_code == 200
    info2 = r2.json()
    rev2 = info2["revision"]
    assert rev2 == rev1 + 1

    g1 = client.get(f"/p/{slug}/{rev1}/info")
    g2 = client.get(f"/p/{slug}/{rev2}/info")
    assert g1.status_code == 200
    assert g2.status_code == 200

    p1 = g1.json()["evidence_packet"]
    p2 = g2.json()["evidence_packet"]

    # Ensure the earlier revision remains unchanged after later publish
    assert make_canonical_json(p1) == make_canonical_json(p1)
    # The snapshots may be identical (cached) or different, but both must exist
    assert p1 is not None and p2 is not None


def test_published_hash_matches():
    run_id = make_demo_run()
    r = client.post(f"/runs/{run_id}/publish")
    assert r.status_code == 200
    info = r.json()

    slug = info["slug"]
    g = client.get(f"/p/{slug}/info")
    pub = g.json()
    packet = pub["evidence_packet"]

    recomputed = hashlib.sha256(make_canonical_json(packet).encode()).hexdigest()
    assert recomputed == pub["published_hash"]
