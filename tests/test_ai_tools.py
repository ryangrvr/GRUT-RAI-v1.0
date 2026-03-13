"""Tests for AI tool definitions and executor."""

import pytest
from pathlib import Path


@pytest.fixture
def grut_engine():
    from grut.canon import GRUTCanon
    from grut.engine import GRUTEngine
    canon_path = str(Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json")
    canon = GRUTCanon(canon_path)
    return GRUTEngine(canon, determinism_mode="STRICT")


def test_tool_definitions_valid():
    """All tool definitions should have required fields."""
    from ai.tools import get_tool_definitions
    tools = get_tool_definitions()
    assert len(tools) >= 5
    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        assert tool["input_schema"]["type"] == "object"


def test_executor_run_cosmology(grut_engine):
    """run_cosmology tool should return valid results with certificate."""
    from ai.tool_executor import execute_tool
    result = execute_tool(
        "run_cosmology",
        {"rho0": 0.2, "p0": -0.2, "enable_growth": True},
        grut_engine=grut_engine,
    )
    assert result["status"] == "completed"
    assert "certificate" in result
    assert "charts" in result
    assert result["certificate"]["canon_hash"]


def test_executor_get_canon_value(grut_engine):
    """get_canon_value tool should return tau0 info."""
    from ai.tool_executor import execute_tool
    result = execute_tool(
        "get_canon_value",
        {"name": "tau0"},
        grut_engine=grut_engine,
    )
    assert "value" in result
    assert result["value"] == pytest.approx(4.19e7, rel=0.01)
    assert result["units"] == "years"


def test_executor_get_canon_value_alpha_mem(grut_engine):
    """get_canon_value should resolve alias alpha_mem."""
    from ai.tool_executor import execute_tool
    result = execute_tool(
        "get_canon_value",
        {"name": "alpha_mem"},
        grut_engine=grut_engine,
    )
    assert "value" in result
    assert result["id"] == "PARAM_ALPHA_MEM"


def test_executor_unknown_tool():
    """Unknown tool should return error."""
    from ai.tool_executor import execute_tool
    result = execute_tool("nonexistent_tool", {})
    assert "error" in result


def test_executor_run_cosmology_without_engine():
    """run_cosmology without engine should return error."""
    from ai.tool_executor import execute_tool
    result = execute_tool("run_cosmology", {}, grut_engine=None)
    assert "error" in result


def test_sovereign_firewall(grut_engine):
    """Engine results through tool executor should have same certificate hash
    as direct engine calls with the same inputs."""
    from ai.tool_executor import execute_tool

    # Run through tool executor
    tool_result = execute_tool(
        "run_cosmology",
        {"rho0": 0.2, "p0": -0.2, "steps": 100},
        grut_engine=grut_engine,
    )

    # Run directly
    input_state = {"a": 1.0, "H": 1e-10, "rho": 0.2, "p": -0.2, "M_X": 0.0}
    run_config = {"dt_years": 100000, "steps": 100, "integrator": "RK4"}
    direct_outputs, direct_cert = grut_engine.run(
        input_state, run_config=run_config, assumption_toggles={"growth_enabled": True}
    )

    # Certificate hashes must match (sovereign firewall proof)
    assert tool_result["certificate"]["canon_hash"] == direct_cert["engine_signature"]["canon_hash"]
    assert tool_result["certificate"]["repro_hash"] == direct_cert["repro_hash"]


# ── Hubble Tension Packet integration tests ──

def test_hubble_tension_packet_lowest_z(grut_engine):
    """build_hubble_tension_packet with eobs_anchor_policy=lowest_z should complete."""
    from ai.tool_executor import execute_tool
    result = execute_tool(
        "build_hubble_tension_packet",
        {
            "preset": "matter_only",
            "eobs_anchor_policy": "lowest_z",
            "recommendation_mode": "configured_only",
            "steps": 100,
        },
        grut_engine=grut_engine,
    )
    assert result["status"] == "completed"
    assert result["eobs_anchor_policy"] == "lowest_z"
    assert result["recommendation_mode"] == "configured_only"
    assert "nis_certificate" in result


def test_hubble_tension_packet_median_lowz(grut_engine):
    """build_hubble_tension_packet with eobs_anchor_policy=median_lowz should complete."""
    from ai.tool_executor import execute_tool
    result = execute_tool(
        "build_hubble_tension_packet",
        {
            "preset": "matter_only",
            "eobs_anchor_policy": "median_lowz",
            "recommendation_mode": "configured_only",
            "steps": 100,
        },
        grut_engine=grut_engine,
    )
    assert result["status"] == "completed"
    assert result["eobs_anchor_policy"] == "median_lowz"
    assert result["recommendation_mode"] == "configured_only"
    assert "nis_certificate" in result


def test_hubble_tension_packet_anchor_policies_differ(grut_engine):
    """Different eobs_anchor_policy values should produce different results."""
    from ai.tool_executor import execute_tool

    result_lowest = execute_tool(
        "build_hubble_tension_packet",
        {
            "preset": "matter_only",
            "eobs_anchor_policy": "lowest_z",
            "recommendation_mode": "configured_only",
            "steps": 100,
        },
        grut_engine=grut_engine,
    )
    result_median = execute_tool(
        "build_hubble_tension_packet",
        {
            "preset": "matter_only",
            "eobs_anchor_policy": "median_lowz",
            "recommendation_mode": "configured_only",
            "steps": 100,
        },
        grut_engine=grut_engine,
    )

    assert result_lowest["status"] == "completed"
    assert result_median["status"] == "completed"

    # Both should complete, but residuals should differ due to different anchoring
    # (Either the residuals or the preset_window_summary will differ)
    lowest_res = result_lowest.get("residuals_vs_data", {})
    median_res = result_median.get("residuals_vs_data", {})
    # They should not be identical (different anchoring produces different E(z))
    assert lowest_res != median_res or result_lowest.get("preset_window_summary") != result_median.get("preset_window_summary")


def test_hubble_tension_packet_determinism(grut_engine):
    """Same inputs to build_hubble_tension_packet should yield identical outputs."""
    from ai.tool_executor import execute_tool

    params = {
        "preset": "matter_only",
        "eobs_anchor_policy": "lowest_z",
        "recommendation_mode": "configured_only",
        "steps": 100,
    }

    result_a = execute_tool("build_hubble_tension_packet", params, grut_engine=grut_engine)
    result_b = execute_tool("build_hubble_tension_packet", params, grut_engine=grut_engine)

    assert result_a["status"] == "completed"
    assert result_b["status"] == "completed"
    # Determinism: same inputs → same certificate digests
    assert result_a.get("output_digest") == result_b.get("output_digest")


def test_hubble_tension_tool_schema_has_anchor_policy():
    """Tool schema should expose eobs_anchor_policy, recommendation_mode,
    and include_vacuum_plus_matter parameters."""
    from ai.tools import get_tool_definitions
    tools = get_tool_definitions()

    tension_tool = None
    for t in tools:
        if t["name"] == "build_hubble_tension_packet":
            tension_tool = t
            break

    assert tension_tool is not None, "build_hubble_tension_packet tool not found"
    props = tension_tool["input_schema"]["properties"]
    assert "eobs_anchor_policy" in props
    assert props["eobs_anchor_policy"]["enum"] == ["lowest_z", "median_lowz"]
    assert "recommendation_mode" in props
    assert props["recommendation_mode"]["enum"] == ["configured_only", "late_time_grid"]
    assert "include_vacuum_plus_matter" in props
    assert props["include_vacuum_plus_matter"]["type"] == "boolean"


def test_nis_expansion_correct():
    """NIS should be expanded as 'Numerical Integrity Standard', not 'Neutral Integrity System'."""
    from ai.system_prompt import build_system_prompt
    prompt = build_system_prompt()
    assert "Numerical Integrity Standard" in prompt
    assert "Neutral Integrity System" not in prompt


# ── Evidence Index Discovery Tests ──

def test_evidence_index_discovers_all_families():
    """Evidence index should discover packets across all major families."""
    from ai.tool_executor import _list_evidence_packets

    result = _list_evidence_packets({"include_audit": True})
    assert "evidence_index" in result
    assert result["total_packets"] >= 20  # broad minimum

    paths = [p["path"] for p in result["evidence_index"] if "error" not in p]

    # Must find hubble tension packets
    hubble = [p for p in paths if "hubble_tension" in p]
    assert len(hubble) >= 2, f"Expected >=2 hubble tension packets, got {len(hubble)}"

    # Must find quantum packets
    quantum = [p for p in paths if "quantum" in p]
    assert len(quantum) >= 1, f"Expected >=1 quantum packet, got {len(quantum)}"

    # Must find cluster evidence packets
    cluster_ev = [p for p in paths if "evidence_cluster" in p]
    assert len(cluster_ev) >= 3, f"Expected >=3 cluster evidence packets, got {len(cluster_ev)}"

    # Must find lensing packets
    lensing = [p for p in paths if "lensing_packet" in p]
    assert len(lensing) >= 1, f"Expected >=1 lensing packet, got {len(lensing)}"

    # Must find rotation packets
    rotation = [p for p in paths if "rotation" in p]
    assert len(rotation) >= 1, f"Expected >=1 rotation packet, got {len(rotation)}"


def test_evidence_index_metadata_fields():
    """Each packet entry should have all required metadata fields."""
    from ai.tool_executor import _list_evidence_packets

    result = _list_evidence_packets({"include_audit": True})
    required_keys = {
        "path", "packet_name", "packet_version", "tool_version",
        "input_hash", "output_digest", "canon_hash", "repro_hash",
        "provenance_hash", "certificate_relpath", "all_certificates",
        "status", "file_count", "file_list",
    }

    for pkt in result["evidence_index"]:
        if "error" in pkt:
            continue
        missing = required_keys - set(pkt.keys())
        assert not missing, f"Packet {pkt['path']} missing keys: {missing}"
        assert isinstance(pkt["file_list"], list)
        assert pkt["file_count"] == len(pkt["file_list"])


def test_evidence_index_packet_version_vs_tool_version():
    """evidence_cluster_v0_6A packets should show packet_version=v0.6A
    and tool_version=v0.5 (distinct values)."""
    from ai.tool_executor import _list_evidence_packets

    result = _list_evidence_packets({"include_audit": False})
    cluster_pkts = [
        p for p in result["evidence_index"]
        if "evidence_cluster_v0_6A" in p.get("path", "") and "error" not in p
    ]
    assert len(cluster_pkts) >= 1

    for pkt in cluster_pkts:
        assert pkt["packet_version"] == "v0.6A", (
            f"Expected packet_version v0.6A, got {pkt['packet_version']}"
        )
        assert pkt["tool_version"] == "v0.5", (
            f"Expected tool_version v0.5, got {pkt['tool_version']}"
        )


def test_evidence_index_pagination():
    """limit and offset should correctly paginate results."""
    from ai.tool_executor import _list_evidence_packets

    full = _list_evidence_packets({"include_audit": True})
    total = full["total_packets"]
    assert total >= 5

    # limit=3
    page1 = _list_evidence_packets({"include_audit": True, "limit": 3, "offset": 0})
    assert len(page1["evidence_index"]) == 3
    assert page1["total_packets"] == total  # total is unchanged
    assert page1["returned"] == 3

    # offset=3, limit=3
    page2 = _list_evidence_packets({"include_audit": True, "limit": 3, "offset": 3})
    assert len(page2["evidence_index"]) == 3
    assert page2["offset"] == 3

    # Entries should not overlap
    paths1 = {p["path"] for p in page1["evidence_index"]}
    paths2 = {p["path"] for p in page2["evidence_index"]}
    assert paths1.isdisjoint(paths2), "Pages should not overlap"


def test_evidence_index_certificate_relpath():
    """Every packet with an NIS cert should report its relative path."""
    from ai.tool_executor import _list_evidence_packets

    result = _list_evidence_packets({"include_audit": True})
    for pkt in result["evidence_index"]:
        if "error" in pkt:
            continue
        certs = pkt.get("all_certificates", [])
        if certs:
            assert pkt["certificate_relpath"], (
                f"Packet {pkt['path']} has certs but empty certificate_relpath"
            )
            assert pkt["certificate_relpath"].endswith(".json")
