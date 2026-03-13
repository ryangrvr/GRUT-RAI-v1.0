from pathlib import Path

from tools.audit_all import build_profile_packet_cmd


def test_build_profile_packet_cmd():
    outdir = Path("artifacts/_audit_profile_packet")
    cmd = build_profile_packet_cmd(outdir)
    assert "tools/run_cluster_profile_packet.py" in cmd
    assert "--kappa_path" in cmd
    assert "artifacts/cluster_sample/kappa.npy" in cmd
    assert "--compare_to_model" in cmd
    assert "--model_response" in cmd
    assert "grut_gate_kspace_v0" in cmd
    assert "--k0_policy" in cmd
    assert "r_smooth" in cmd
    assert str(outdir) in cmd
