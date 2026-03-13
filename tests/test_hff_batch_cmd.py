from tools.run_hff_batch import build_fetch_cmd, build_packet_cmd


def test_hff_batch_cmds():
    cluster = "A2744"
    model = "CATS"
    fetch_cmd = build_fetch_cmd(cluster, model)
    packet_cmd = build_packet_cmd(cluster, model)

    assert "tools/fetch_hff_lensmodel.py" in fetch_cmd
    assert "--cluster" in fetch_cmd
    assert "--model" in fetch_cmd
    assert cluster in fetch_cmd
    assert model in fetch_cmd

    assert "tools/build_cluster_evidence_packet.py" in packet_cmd
    assert "--cluster" in packet_cmd
    assert "--model" in packet_cmd
    assert cluster in packet_cmd
    assert model in packet_cmd
