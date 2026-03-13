import json

from tools.build_cluster_evidence_packet import build_cluster_evidence_packet


def test_cluster_evidence_packet_smoke(tmp_path):

    outdir = tmp_path / "evidence"
    config = {
        "cluster": "A2744",
        "model": "CATS",
        "synthetic": True,
    }
    result = build_cluster_evidence_packet(config, str(outdir))
    packet_path = outdir / "A2744" / "CATS" / "PACKET_INDEX.json"
    assert packet_path.exists()
    packet = json.loads(packet_path.read_text())
    assert packet["output_digest"]
    assert result["output_digest"] == packet["output_digest"]
