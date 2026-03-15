"""Phase IV Package 1: Action Principle Program — Tests.

Verifies that the action principle landscape is honestly classified:
- Four candidates built and evaluated
- Fundamental obstruction sharply identified
- Klein-Gordon overdamped limit verified in both sectors
- Auxiliary-field realization confirmed as preferred
- Structural identity omega_0*tau=1 preserved
- No overclaiming (constitutive-effective status maintained)
"""

import math
import pytest

M_SUN = 1.989e30


# ============================================================================
# 1. CANDIDATE FORMULATIONS
# ============================================================================

class TestCandidateFormulations:
    """All four action candidates must be built with correct metadata."""

    def test_four_candidates_built(self) -> None:
        """Exactly four candidates must be created."""
        from grut.action_principle import build_all_candidates
        candidates = build_all_candidates()
        assert len(candidates) == 4

    def test_candidate_names(self) -> None:
        """Candidates must have the expected names."""
        from grut.action_principle import build_all_candidates
        candidates = build_all_candidates()
        names = [c.name for c in candidates]
        assert "klein_gordon" in names
        assert "galley_doubled" in names
        assert "nonlocal_retarded" in names
        assert "auxiliary_field" in names

    def test_klein_gordon_is_quasi_action(self) -> None:
        """Klein-Gordon is quasi-action: produces second-order EOM, not first."""
        from grut.action_principle import build_candidate_klein_gordon
        c = build_candidate_klein_gordon()
        assert c.classification == "quasi_action"
        assert c.produces_second_order is True
        assert c.produces_first_order is False
        assert c.overdamped_limit_matches is True

    def test_galley_is_formal_framework(self) -> None:
        """Galley doubled-field is formal framework: applicable in principle."""
        from grut.action_principle import build_candidate_galley
        c = build_candidate_galley()
        assert c.classification == "formal_framework"
        assert c.produces_first_order is True
        assert c.requires_physical_limit is True

    def test_nonlocal_is_formal_parent(self) -> None:
        """Nonlocal retarded is formal parent of auxiliary-field."""
        from grut.action_principle import build_candidate_nonlocal
        c = build_candidate_nonlocal()
        assert c.classification == "formal_parent"
        assert c.introduces_extra_dof is False

    def test_auxiliary_field_is_preferred(self) -> None:
        """Auxiliary-field is the preferred effective formulation."""
        from grut.action_principle import build_candidate_auxiliary_field
        c = build_candidate_auxiliary_field()
        assert c.classification == "preferred_effective"
        assert c.bianchi_from_action is False
        assert c.bianchi_effective is True

    def test_all_candidates_recover_sectors(self) -> None:
        """All candidates must recover both weak and strong field sectors."""
        from grut.action_principle import build_all_candidates
        for c in build_all_candidates():
            assert c.weak_field_recovers, f"{c.name} fails weak-field recovery"
            assert c.strong_field_recovers, f"{c.name} fails strong-field recovery"

    def test_all_candidates_preserve_identity(self) -> None:
        """All candidates must preserve structural identity omega_0*tau=1."""
        from grut.action_principle import build_all_candidates
        for c in build_all_candidates():
            assert c.structural_identity_preserved, f"{c.name} breaks identity"

    def test_all_candidates_have_nonclaims(self) -> None:
        """Each candidate must have at least 3 nonclaims."""
        from grut.action_principle import build_all_candidates
        for c in build_all_candidates():
            assert len(c.nonclaims) >= 3, f"{c.name} has only {len(c.nonclaims)} nonclaims"

    def test_kg_introduces_extra_dof(self) -> None:
        """Klein-Gordon introduces propagating modes (extra DOF)."""
        from grut.action_principle import build_candidate_klein_gordon
        c = build_candidate_klein_gordon()
        assert c.introduces_extra_dof is True
        assert "propagating" in c.extra_dof_description.lower()

    def test_kg_has_bianchi_from_action(self) -> None:
        """Klein-Gordon has Bianchi guaranteed by diffeomorphism invariance."""
        from grut.action_principle import build_candidate_klein_gordon
        c = build_candidate_klein_gordon()
        assert c.bianchi_from_action is True


# ============================================================================
# 2. OBSTRUCTION ANALYSIS
# ============================================================================

class TestObstructionAnalysis:
    """The fundamental obstruction must be sharply identified."""

    def test_obstruction_is_order_mismatch(self) -> None:
        from grut.action_principle import analyze_obstruction
        obs = analyze_obstruction()
        assert obs.obstruction_type == "order_mismatch"

    def test_obstruction_is_theorem_level(self) -> None:
        from grut.action_principle import analyze_obstruction
        obs = analyze_obstruction()
        assert obs.is_theorem_level is True

    def test_obstruction_statement_exists(self) -> None:
        from grut.action_principle import analyze_obstruction
        obs = analyze_obstruction()
        assert len(obs.obstruction_statement) > 100

    def test_three_bypass_routes(self) -> None:
        from grut.action_principle import analyze_obstruction
        obs = analyze_obstruction()
        assert len(obs.bypass_overdamped) > 0
        assert len(obs.bypass_doubled_field) > 0
        assert len(obs.bypass_nonlocal) > 0

    def test_bypass_status_classified(self) -> None:
        from grut.action_principle import analyze_obstruction
        obs = analyze_obstruction()
        assert len(obs.bypass_status) == 4
        assert "quasi_action" in obs.bypass_status["overdamped_kg"]
        assert "formal_framework" in obs.bypass_status["galley_doubled"]
        assert "formal_parent" in obs.bypass_status["nonlocal_retarded"]
        assert "preferred_effective" in obs.bypass_status["auxiliary_field"]


# ============================================================================
# 3. OVERDAMPED LIMIT — COSMOLOGICAL SECTOR
# ============================================================================

class TestOverdampedCosmo:
    """Klein-Gordon overdamped limit must recover cosmological memory ODE."""

    def test_cosmo_is_overdamped(self) -> None:
        """System must be at least marginally overdamped in cosmo sector."""
        from grut.action_principle import check_overdamped_limit_cosmo
        check = check_overdamped_limit_cosmo()
        assert check.is_overdamped

    def test_cosmo_phi_moves_toward_driver(self) -> None:
        """Both KG overdamped and GRUT must evolve toward the driver."""
        from grut.action_principle import check_overdamped_limit_cosmo
        check = check_overdamped_limit_cosmo()
        H_base_sq = (1.0 / 4.19e7) ** 2
        assert check.phi_grut > H_base_sq  # moved toward X (which is 1.1*H_base_sq)
        assert check.phi_exact > H_base_sq

    def test_cosmo_tau_ratio_order_unity(self) -> None:
        """KG and GRUT timescales must be within order of magnitude."""
        from grut.action_principle import check_overdamped_limit_cosmo
        check = check_overdamped_limit_cosmo()
        assert 0.01 < check.tau_ratio < 100.0

    def test_cosmo_recovery_flag(self) -> None:
        """Recovery flag must be True."""
        from grut.action_principle import check_overdamped_limit_cosmo
        check = check_overdamped_limit_cosmo()
        assert check.recovered


# ============================================================================
# 4. OVERDAMPED LIMIT — COLLAPSE SECTOR
# ============================================================================

class TestOverdampedCollapse:
    """Klein-Gordon overdamped limit in collapse sector."""

    def test_collapse_structural_identity(self) -> None:
        """omega_0 * tau must be close to 1 (structural identity)."""
        from grut.action_principle import check_overdamped_limit_collapse
        check = check_overdamped_limit_collapse()
        # omega_0 * tau = 1 implies overdamped_ratio ~ 1 (critical damping)
        assert 0.5 < check.overdamped_ratio < 2.0

    def test_collapse_phi_moves_toward_driver(self) -> None:
        """Both KG and GRUT must evolve toward the perturbed driver."""
        from grut.action_principle import check_overdamped_limit_collapse
        check = check_overdamped_limit_collapse()
        assert check.phi_grut > 0
        assert check.phi_exact > 0

    def test_collapse_recovery_flag(self) -> None:
        """Recovery flag must be True."""
        from grut.action_principle import check_overdamped_limit_collapse
        check = check_overdamped_limit_collapse()
        assert check.recovered

    def test_collapse_notes_mention_critical_damping(self) -> None:
        """Notes must mention critical damping (not overdamped)."""
        from grut.action_principle import check_overdamped_limit_collapse
        check = check_overdamped_limit_collapse()
        combined = " ".join(check.notes).lower()
        assert "critical" in combined or "structural identity" in combined


# ============================================================================
# 5. MASTER ANALYSIS
# ============================================================================

class TestMasterAnalysis:
    """The master analysis must produce a valid, complete result."""

    def test_result_is_valid(self) -> None:
        from grut.action_principle import compute_action_principle_analysis
        result = compute_action_principle_analysis()
        assert result.valid

    def test_preferred_is_auxiliary_field(self) -> None:
        from grut.action_principle import compute_action_principle_analysis
        result = compute_action_principle_analysis()
        assert result.preferred_name == "auxiliary_field"

    def test_no_confirmed_action(self) -> None:
        """Must honestly report that no confirmed action exists."""
        from grut.action_principle import compute_action_principle_analysis
        result = compute_action_principle_analysis()
        assert result.has_confirmed_action is False

    def test_classification_is_constitutive(self) -> None:
        from grut.action_principle import compute_action_principle_analysis
        result = compute_action_principle_analysis()
        assert "constitutive" in result.best_classification

    def test_scalar_field_status_is_effective(self) -> None:
        from grut.action_principle import compute_action_principle_analysis
        result = compute_action_principle_analysis()
        assert result.scalar_field_status == "effective"

    def test_locality_is_auxiliary_field(self) -> None:
        from grut.action_principle import compute_action_principle_analysis
        result = compute_action_principle_analysis()
        assert result.locality_status == "auxiliary_field"

    def test_resolved_closures_count(self) -> None:
        from grut.action_principle import compute_action_principle_analysis
        result = compute_action_principle_analysis()
        assert len(result.resolved_closures) >= 8

    def test_remaining_closures_count(self) -> None:
        from grut.action_principle import compute_action_principle_analysis
        result = compute_action_principle_analysis()
        assert len(result.remaining_closures) >= 5

    def test_nonclaims_minimum(self) -> None:
        from grut.action_principle import compute_action_principle_analysis
        result = compute_action_principle_analysis()
        assert len(result.nonclaims) >= 10


# ============================================================================
# 6. SERIALIZATION
# ============================================================================

class TestSerialization:
    """Serialization must produce valid dicts."""

    def test_candidate_to_dict(self) -> None:
        from grut.action_principle import build_candidate_klein_gordon, candidate_to_dict
        c = build_candidate_klein_gordon()
        d = candidate_to_dict(c)
        assert d["name"] == "klein_gordon"
        assert d["classification"] == "quasi_action"
        assert isinstance(d["nonclaims"], list)

    def test_overdamped_to_dict(self) -> None:
        from grut.action_principle import check_overdamped_limit_cosmo, overdamped_to_dict
        check = check_overdamped_limit_cosmo()
        d = overdamped_to_dict(check)
        assert d["sector"] == "cosmological"
        assert isinstance(d["recovered"], bool)

    def test_full_result_to_dict(self) -> None:
        from grut.action_principle import compute_action_principle_analysis, action_result_to_dict
        result = compute_action_principle_analysis()
        d = action_result_to_dict(result)
        assert d["valid"] is True
        assert d["preferred_name"] == "auxiliary_field"
        assert d["has_confirmed_action"] is False
        assert len(d["candidates"]) == 4

    def test_result_dict_has_obstruction(self) -> None:
        from grut.action_principle import compute_action_principle_analysis, action_result_to_dict
        result = compute_action_principle_analysis()
        d = action_result_to_dict(result)
        assert d["obstruction"]["is_theorem_level"] is True
        assert d["obstruction"]["type"] == "order_mismatch"
