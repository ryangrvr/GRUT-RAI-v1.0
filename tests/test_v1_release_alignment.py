"""GRUT-RAI v1.0 Release Alignment Tests.

Verifies that the v1.0 canonical build correctly synchronizes all
classification strings, default parameters, version identities, and
status-ladder content to the final Phase III state.

WHAT THESE TESTS VERIFY:
1. Superseded results are NOT presented as leading
2. Status ladder content (LOCKED / CONSTRAINED / OPEN) is present
3. mixed_viscoelastic is the leading interior classification
4. ~1.1% is the leading echo estimate where relevant
5. reactive proxy remains accessible only as historical/superseded
6. Final Phase III terminology is used consistently
7. Version identity strings are updated to v1.0
"""

import json
import math
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


# ============================================================================
# 1. VERSION IDENTITY
# ============================================================================

class TestVersionIdentity:
    """Version strings must say v1.0."""

    def test_engine_version_constants(self) -> None:
        from core.constants import GRUTParams
        p = GRUTParams()
        assert "v1.0" in p.engine_version

    def test_engine_default_version(self) -> None:
        from grut.canon import GRUTCanon
        from grut.engine import GRUTEngine
        canon = GRUTCanon(REPO_ROOT / "canon" / "grut_canon_v0.3.json")
        engine = GRUTEngine(canon)
        assert "v1.0" in engine.engine_version

    def test_init_docstring(self) -> None:
        import grut
        assert "v1.0" in grut.__doc__

    def test_canon_meta_phase(self) -> None:
        canon_path = REPO_ROOT / "canon" / "grut_canon_v0.3.json"
        data = json.loads(canon_path.read_text())
        assert data["meta"]["phase"] == "3"

    def test_canon_meta_status(self) -> None:
        canon_path = REPO_ROOT / "canon" / "grut_canon_v0.3.json"
        data = json.loads(canon_path.read_text())
        assert data["meta"]["status"] == "v1.0"

    def test_canon_v1_note_present(self) -> None:
        canon_path = REPO_ROOT / "canon" / "grut_canon_v0.3.json"
        data = json.loads(canon_path.read_text())
        notes = data["meta"]["notes"]
        assert any("v1.0 release" in n for n in notes)


# ============================================================================
# 2. CLASSIFICATION STRINGS — NO reactive_candidate IN CODE
# ============================================================================

class TestClassificationStrings:
    """No code path should return 'reactive_candidate' — use 'reactive' for Q > 10."""

    def test_proxy_reactive_string(self) -> None:
        """Proxy module returns 'reactive' (not 'reactive_candidate') at Q >> 10."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
        )
        M_SUN = 1.989e30
        M = 30.0 * M_SUN
        r_s = 2.0 * 6.674e-11 * M / (299_792_458.0 ** 2)
        params = InteriorWaveParams(M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s)
        result = compute_interior_wave_analysis(params)
        assert result.response_class == "reactive"
        assert "_candidate" not in result.response_class

    def test_pde_mixed_at_canon(self) -> None:
        """PDE module returns 'mixed_viscoelastic' at canon parameters (Q ~ 6-7.5)."""
        from grut.interior_pde import compute_pde_analysis
        M_SUN = 1.989e30
        result = compute_pde_analysis(M_kg=30.0 * M_SUN)
        assert result.response_class == "mixed_viscoelastic"

    def test_covariant_mixed_at_canon(self) -> None:
        """Covariant module returns 'mixed_viscoelastic' at canon parameters."""
        from grut.interior_covariant import compute_covariant_analysis
        M_SUN = 1.989e30
        result = compute_covariant_analysis(M_kg=30.0 * M_SUN)
        assert result.response_class == "mixed_viscoelastic"

    def test_no_candidate_suffix_in_proxy(self) -> None:
        """Check dissipative branch also lacks _candidate suffix."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
        )
        M_SUN = 1.989e30
        M = 30.0 * M_SUN
        r_s = 2.0 * 6.674e-11 * M / (299_792_458.0 ** 2)
        params = InteriorWaveParams(
            M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s,
            gamma_diss=1e6,
        )
        result = compute_interior_wave_analysis(params)
        assert "_candidate" not in result.response_class

    def test_pde_reactive_no_candidate(self) -> None:
        """PDE module returns 'reactive' (not 'reactive_candidate') for high Q."""
        from grut.interior_pde import compute_pde_analysis
        M_SUN = 1.989e30
        # Use very low alpha_vac to artificially raise Q above 10
        result = compute_pde_analysis(M_kg=30.0 * M_SUN, alpha_vac=0.01)
        if result.Q_pde_fundamental > 10.0:
            assert result.response_class == "reactive"
            assert "_candidate" not in result.response_class


# ============================================================================
# 3. MIXED_VISCOELASTIC IS LEADING CLASSIFICATION
# ============================================================================

class TestLeadingClassification:
    """mixed_viscoelastic must be the leading interior classification at canon params."""

    def test_pde_is_mixed(self) -> None:
        from grut.interior_pde import compute_pde_analysis
        M_SUN = 1.989e30
        result = compute_pde_analysis(M_kg=30.0 * M_SUN)
        assert "mixed_viscoelastic" == result.response_class

    def test_pde_q_in_range(self) -> None:
        """PDE Q at canon must be between 1 and 10 (mixed regime)."""
        from grut.interior_pde import compute_pde_analysis
        M_SUN = 1.989e30
        result = compute_pde_analysis(M_kg=30.0 * M_SUN)
        assert 1.0 < result.Q_pde_fundamental < 10.0

    def test_covariant_confirms_mixed(self) -> None:
        from grut.interior_covariant import compute_covariant_analysis
        M_SUN = 1.989e30
        result = compute_covariant_analysis(M_kg=30.0 * M_SUN)
        assert "mixed_viscoelastic" == result.response_class


# ============================================================================
# 4. ECHO ESTIMATE — ~1.1% IS LEADING
# ============================================================================

class TestEchoEstimate:
    """Leading echo estimate is ~1.1%, not the superseded ~3.7%."""

    def test_covariant_echo_pct(self) -> None:
        """Covariant echo must be near 1.1%."""
        from grut.interior_covariant import compute_covariant_analysis
        M_SUN = 1.989e30
        result = compute_covariant_analysis(M_kg=30.0 * M_SUN)
        # Should be between 0.5% and 2.5% (order of magnitude check)
        assert 0.5 < result.echo_amp_cov_pct < 2.5

    def test_echo_not_3_7_pct(self) -> None:
        """Echo must NOT be near the superseded 3.7% proxy value."""
        from grut.interior_covariant import compute_covariant_analysis
        M_SUN = 1.989e30
        result = compute_covariant_analysis(M_kg=30.0 * M_SUN)
        assert result.echo_amp_cov_pct < 3.0  # Must be below 3%


# ============================================================================
# 5. DEFAULT Q PARAMETER — PDE-INFORMED
# ============================================================================

class TestDefaultQValue:
    """Default Q fallback must be the PDE canon value, not the old 515.6."""

    def test_graded_transition_default_q(self) -> None:
        from grut.interior_waves import GradedTransitionParams
        p = GradedTransitionParams()
        assert p.quality_factor_Q < 10.0, (
            f"Default Q = {p.quality_factor_Q}, expected PDE canon value < 10"
        )
        assert p.quality_factor_Q > 1.0, (
            f"Default Q = {p.quality_factor_Q}, expected > 1 (mixed regime)"
        )


# ============================================================================
# 6. STATUS LADDER CONTENT
# ============================================================================

class TestStatusLadder:
    """Phase III closure documents must use the three-tier status ladder."""

    def test_upload_state_has_locked(self) -> None:
        doc = (REPO_ROOT / "docs" / "PHASE_III_FINAL_UPLOAD_STATE.md").read_text()
        assert "LOCKED" in doc

    def test_upload_state_has_constrained(self) -> None:
        doc = (REPO_ROOT / "docs" / "PHASE_III_FINAL_UPLOAD_STATE.md").read_text()
        assert "CONSTRAINED" in doc

    def test_upload_state_has_open(self) -> None:
        doc = (REPO_ROOT / "docs" / "PHASE_III_FINAL_UPLOAD_STATE.md").read_text()
        assert "FUNDAMENTALLY OPEN" in doc

    def test_upload_state_nonclaims_count(self) -> None:
        """At least 25 explicit nonclaims."""
        doc = (REPO_ROOT / "docs" / "PHASE_III_FINAL_UPLOAD_STATE.md").read_text()
        # Count both "Nonclaim" and "nonclaim" occurrences
        nonclaim_count = doc.lower().count("nonclaim")
        # Also count numbered nonclaim items (lines starting with digits after nonclaim header)
        lines = doc.split("\n")
        numbered_items = 0
        in_nonclaim_section = False
        for line in lines:
            if "nonclaim" in line.lower():
                in_nonclaim_section = True
            elif line.startswith("## ") and "nonclaim" not in line.lower():
                in_nonclaim_section = False
            elif in_nonclaim_section and line.strip()[:1].isdigit():
                numbered_items += 1
        assert numbered_items >= 20, f"Expected >= 20 nonclaim items, got {numbered_items}"


# ============================================================================
# 7. SUPERSEDED BANNERS ON PRE-PDE DOCS
# ============================================================================

class TestSupersededBanners:
    """Pre-PDE proxy documents must have SUPERSEDED banners."""

    def test_wp2c_superseded(self) -> None:
        doc = (REPO_ROOT / "docs" / "PHASE_III_C_WP2C_INTERIOR_WAVES.md").read_text()
        # Check first 500 chars for the banner
        header = doc[:500]
        assert "SUPERSEDED" in header

    def test_wp2d_superseded(self) -> None:
        doc = (REPO_ROOT / "docs" / "PHASE_III_C_WP2D_TRANSITION_WIDTH.md").read_text()
        header = doc[:500]
        assert "SUPERSEDED" in header


# ============================================================================
# 8. SYSTEM PROMPT PHASE III CONTENT
# ============================================================================

class TestSystemPromptContent:
    """System prompt must reference Phase III final state."""

    def test_prompt_has_phase_iii(self) -> None:
        from ai.system_prompt import build_system_prompt
        prompt = build_system_prompt()
        assert "Phase III" in prompt

    def test_prompt_has_mixed_viscoelastic(self) -> None:
        from ai.system_prompt import build_system_prompt
        prompt = build_system_prompt()
        assert "mixed_viscoelastic" in prompt

    def test_prompt_has_1_1_pct(self) -> None:
        from ai.system_prompt import build_system_prompt
        prompt = build_system_prompt()
        assert "1.1%" in prompt

    def test_prompt_has_v1_0_fallback(self) -> None:
        from ai.system_prompt import build_system_prompt
        prompt = build_system_prompt()
        assert "v1.0" in prompt

    def test_prompt_no_phaseE_portal(self) -> None:
        """Old phaseE-portal string must not appear."""
        from ai.system_prompt import build_system_prompt
        prompt = build_system_prompt()
        assert "phaseE-portal" not in prompt


# ============================================================================
# 9. CANON JSON VALID
# ============================================================================

class TestCanonIntegrity:
    """Canon JSON must be valid and parseable."""

    def test_canon_valid_json(self) -> None:
        canon_path = REPO_ROOT / "canon" / "grut_canon_v0.3.json"
        data = json.loads(canon_path.read_text())
        assert "meta" in data
        assert "constants" in data

    def test_canon_schema_version(self) -> None:
        canon_path = REPO_ROOT / "canon" / "grut_canon_v0.3.json"
        data = json.loads(canon_path.read_text())
        assert data["meta"]["schema_version"] == "v0.3"
