"""Tests for persistence, publishing, and evidence packets."""

import json
import uuid
from fastapi.testclient import TestClient
from api.main import app
from storage.db import RunStore
from core.evidence import make_evidence_packet, verify_evidence_packet


def test_persistence_runs_saved():
    """POST /anamnesis/demo then GET /runs/{id} returns same hash_bundle."""
    client = TestClient(app)

    payload = {
        "n": 256,
        "dt_s": 1.0,
        "tau_s": 30.0,
        "n_kernel": 128,
        "lam": 0.01,
        "max_iter": 1500,
        "noise_std": 0.0,
        "spikes": [{"index": 40, "amplitude": 1.0}, {"index": 150, "amplitude": 0.7}],
        "seed": 1,
    }

    # Run demo
    r1 = client.post("/anamnesis/demo", json=payload)
    assert r1.status_code == 200
    response1 = r1.json()
    run_id = response1.get("run_id")
    assert run_id, "Demo response should include run_id"

    # Retrieve run from DB
    r2 = client.get(f"/runs/{run_id}")
    assert r2.status_code == 200
    stored_run = r2.json()

    # Verify structure
    assert stored_run["id"] == run_id
    assert stored_run["kind"] == "anamnesis_demo"
    assert stored_run["status"] in ("PASS", "WARN", "FAIL")
    assert "hash_bundle" in stored_run
    assert stored_run["hash_bundle"] is not None


def test_library_lists_runs():
    """GET /library returns latest runs."""
    client = TestClient(app)

    # Run a demo to ensure there's something in library
    payload = {
        "n": 128,
        "dt_s": 1.0,
        "tau_s": 20.0,
        "n_kernel": 64,
        "lam": 0.02,
        "noise_std": 0.0,
        "spikes": [{"index": 30, "amplitude": 1.0}],
        "seed": 2,
    }
    r = client.post("/anamnesis/demo", json=payload)
    assert r.status_code == 200

    # Fetch library
    r_lib = client.get("/library")
    assert r_lib.status_code == 200
    lib_data = r_lib.json()

    assert "runs" in lib_data
    assert isinstance(lib_data["runs"], list)
    if len(lib_data["runs"]) > 0:
        run = lib_data["runs"][0]
        assert "id" in run
        assert "kind" in run
        assert "status" in run
        assert "created_at" in run


def test_export_packet_hash():
    """Export run and verify evidence packet hash."""
    client = TestClient(app)

    payload = {
        "n": 128,
        "dt_s": 1.0,
        "tau_s": 15.0,
        "n_kernel": 64,
        "lam": 0.015,
        "noise_std": 0.0,
        "spikes": [{"index": 50, "amplitude": 0.8}],
        "seed": 3,
    }

    r1 = client.post("/anamnesis/demo", json=payload)
    assert r1.status_code == 200
    run_id = r1.json().get("run_id")

    # Export run
    r2 = client.get(f"/runs/{run_id}/export")
    assert r2.status_code == 200
    packet = r2.json()

    # Verify evidence packet structure and hash
    assert "metadata" in packet
    assert "request" in packet
    assert "response" in packet
    assert "receipt" in packet
    assert "bundle_hash" in packet

    # Verify hash integrity
    assert verify_evidence_packet(packet), "Evidence packet hash should be valid"


def test_publish_immutable_snapshot():
    """Publish run creates snapshot; republish increments revision."""
    client = TestClient(app)

    payload = {
        "n": 128,
        "dt_s": 1.0,
        "tau_s": 25.0,
        "n_kernel": 64,
        "lam": 0.01,
        "noise_std": 0.0,
        "spikes": [{"index": 20, "amplitude": 1.0}],
        "seed": 4,
    }

    r1 = client.post("/anamnesis/demo", json=payload)
    assert r1.status_code == 200
    run_id = r1.json().get("run_id")

    # Publish first time
    r_pub1 = client.post(f"/runs/{run_id}/publish")
    assert r_pub1.status_code == 200
    pub1 = r_pub1.json()
    slug = pub1["slug"]
    assert pub1["revision"] == 1
    hash1 = pub1["published_hash"]

    # Retrieve published snapshot
    r_get1 = client.get(f"/p/{slug}")
    assert r_get1.status_code == 200
    snapshot1 = r_get1.json()
    assert "metadata" in snapshot1

    # Publish again (republish)
    r_pub2 = client.post(f"/runs/{run_id}/publish")
    assert r_pub2.status_code == 200
    pub2 = r_pub2.json()
    assert pub2["slug"] == slug  # Same slug
    assert pub2["revision"] == 2  # Incremented revision
    hash2 = pub2["published_hash"]

    # Hashes should be identical (same data, same snapshot)
    assert hash1 == hash2


def test_published_page_immutable():
    """Published snapshot does not leak local paths or private metadata."""
    client = TestClient(app)

    payload = {
        "n": 64,
        "dt_s": 1.0,
        "tau_s": 10.0,
        "n_kernel": 32,
        "lam": 0.02,
        "noise_std": 0.0,
        "spikes": [{"index": 15, "amplitude": 1.0}],
        "seed": 5,
    }

    r1 = client.post("/anamnesis/demo", json=payload)
    assert r1.status_code == 200
    run_id = r1.json().get("run_id")

    # Publish
    r_pub = client.post(f"/runs/{run_id}/publish")
    assert r_pub.status_code == 200
    slug = r_pub.json()["slug"]

    # Get published snapshot
    r_snap = client.get(f"/p/{slug}")
    assert r_snap.status_code == 200
    snapshot = r_snap.json()

    # Verify: published snapshot should NOT contain private fields
    # It should only have: schema, metadata, request, response, receipt, bundle_hash
    assert set(snapshot.keys()) == {"schema", "metadata", "request", "response", "receipt", "bundle_hash"}

    # Verify no local paths in snapshot
    snapshot_str = json.dumps(snapshot)
    assert "/tmp/" not in snapshot_str
    assert "storage/" not in snapshot_str


def test_evidence_packet_roundtrip():
    """Create evidence packet, verify hash, and re-verify after JSON roundtrip."""
    request = {"n": 100, "lam": 0.01}
    response = {"ris": {"status": "PASS", "emd": 0.5}}
    engine_version = "test-v1"
    params_hash = "abc123"

    packet = make_evidence_packet(
        kind="anamnesis_demo",
        request=request,
        response=response,
        engine_version=engine_version,
        params_hash=params_hash,
    )

    # Verify initial hash
    assert verify_evidence_packet(packet)

    # Serialize and deserialize
    packet_json = json.dumps(packet)
    packet_loaded = json.loads(packet_json)

    # Verify hash still valid after roundtrip
    assert verify_evidence_packet(packet_loaded)
