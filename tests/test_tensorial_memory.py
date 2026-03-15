"""Phase IV Package 2: Tensorial Memory-Field Program — Tests.

Verifies that the tensorial memory-field landscape is honestly classified:
- Five candidates built with correct structure
- Scalar sufficiency confirmed for all Phase III results
- Symmetry reductions verified (FRW, spherical, axisymmetric, general)
- Anisotropic stress estimates in both sectors
- Phase III survival correctly assessed
- Extension path recommended
- No overclaiming
"""

import math
import pytest

M_SUN = 1.989e30


# ============================================================================
# 1. CANDIDATE STRUCTURES
# ============================================================================

class TestTensorCandidates:
    """All five tensor candidates must be built with correct metadata."""

    def test_five_candidates_built(self) -> None:
        from grut.tensorial_memory import build_all_tensor_candidates
        candidates = build_all_tensor_candidates()
        assert len(candidates) == 5

    def test_candidate_names(self) -> None:
        from grut.tensorial_memory import build_all_tensor_candidates
        names = [c.name for c in build_all_tensor_candidates()]
        assert "scalar_only" in names
        assert "scalar_plus_aniso" in names
        assert "scalar_plus_vector" in names
        assert "rank2_tensor" in names
        assert "constitutive_aniso" in names

    def test_scalar_only_is_sufficient(self) -> None:
        from grut.tensorial_memory import build_candidate_scalar_only
        c = build_candidate_scalar_only()
        assert c.classification == "sufficient"
        assert c.total_dof == 1
        assert c.phase3_results_unchanged is True

    def test_scalar_plus_aniso_is_minimal(self) -> None:
        from grut.tensorial_memory import build_candidate_scalar_plus_aniso
        c = build_candidate_scalar_plus_aniso()
        assert c.classification == "minimal_extension"
        assert c.total_dof == 6
        assert c.reduces_to_scalar is True

    def test_vector_is_plausible(self) -> None:
        from grut.tensorial_memory import build_candidate_scalar_plus_vector
        c = build_candidate_scalar_plus_vector()
        assert c.classification == "plausible_intermediate"
        assert c.total_dof == 4

    def test_rank2_is_maximal(self) -> None:
        from grut.tensorial_memory import build_candidate_rank2_tensor
        c = build_candidate_rank2_tensor()
        assert c.classification == "maximal_extension"
        assert c.total_dof == 10

    def test_constitutive_aniso_is_effective_limit(self) -> None:
        from grut.tensorial_memory import build_candidate_constitutive_aniso
        c = build_candidate_constitutive_aniso()
        assert c.classification == "effective_limit"
        assert c.total_dof == 1  # no new DOF

    def test_all_reduce_to_scalar(self) -> None:
        """Every candidate must reduce to scalar in appropriate symmetry limit."""
        from grut.tensorial_memory import build_all_tensor_candidates
        for c in build_all_tensor_candidates():
            assert c.reduces_to_scalar, f"{c.name} does not reduce to scalar"

    def test_all_preserve_phase3(self) -> None:
        """All candidates must leave Phase III results unchanged."""
        from grut.tensorial_memory import build_all_tensor_candidates
        for c in build_all_tensor_candidates():
            assert c.phase3_results_unchanged, f"{c.name} breaks Phase III"

    def test_all_have_nonclaims(self) -> None:
        from grut.tensorial_memory import build_all_tensor_candidates
        for c in build_all_tensor_candidates():
            assert len(c.nonclaims) >= 3, f"{c.name} has only {len(c.nonclaims)} nonclaims"

    def test_dof_ordering(self) -> None:
        """DOF count must be: scalar(1) < vector(4) < aniso(6) <= rank2(10)."""
        from grut.tensorial_memory import build_all_tensor_candidates
        candidates = {c.name: c for c in build_all_tensor_candidates()}
        assert candidates["scalar_only"].total_dof < candidates["scalar_plus_vector"].total_dof
        assert candidates["scalar_plus_vector"].total_dof < candidates["scalar_plus_aniso"].total_dof
        assert candidates["scalar_plus_aniso"].total_dof <= candidates["rank2_tensor"].total_dof

    def test_rank2_decomposes(self) -> None:
        """Rank-2 tensor must decompose into scalar + vector + tensor sectors."""
        from grut.tensorial_memory import build_candidate_rank2_tensor
        c = build_candidate_rank2_tensor()
        # Check components include scalar, vector, and tensor sectors
        components_str = " ".join(c.components).lower()
        assert "scalar" in components_str
        assert "vector" in components_str
        assert "tensor" in components_str or "trace-free" in components_str


# ============================================================================
# 2. SCALAR SUFFICIENCY
# ============================================================================

class TestScalarSufficiency:
    """Scalar must be sufficient for all Phase III results."""

    def test_all_checks_pass(self) -> None:
        from grut.tensorial_memory import check_scalar_sufficiency
        checks = check_scalar_sufficiency()
        for c in checks:
            assert c.scalar_sufficient, f"Scalar insufficient for: {c.result_name}"

    def test_check_count(self) -> None:
        """At least 7 Phase III results checked."""
        from grut.tensorial_memory import check_scalar_sufficiency
        checks = check_scalar_sufficiency()
        assert len(checks) >= 7

    def test_friedmann_is_scalar_sufficient(self) -> None:
        from grut.tensorial_memory import check_scalar_sufficiency
        checks = {c.result_name: c for c in check_scalar_sufficiency()}
        assert checks["Modified Friedmann equation"].scalar_sufficient

    def test_identity_is_scalar_sufficient(self) -> None:
        from grut.tensorial_memory import check_scalar_sufficiency
        checks = {c.result_name: c for c in check_scalar_sufficiency()}
        assert checks["Structural identity omega_0*tau=1"].scalar_sufficient

    def test_some_tensor_would_modify(self) -> None:
        """At least some results would be modified by tensor extension."""
        from grut.tensorial_memory import check_scalar_sufficiency
        checks = check_scalar_sufficiency()
        modified = [c for c in checks if c.tensor_would_modify]
        assert len(modified) >= 3


# ============================================================================
# 3. SYMMETRY REDUCTIONS
# ============================================================================

class TestSymmetryReductions:
    """Scalar must arise as symmetry reduction of tensor in each spacetime."""

    def test_four_spacetimes_checked(self) -> None:
        from grut.tensorial_memory import check_symmetry_reductions
        reductions = check_symmetry_reductions()
        assert len(reductions) == 4

    def test_all_reductions_consistent(self) -> None:
        from grut.tensorial_memory import check_symmetry_reductions
        for r in check_symmetry_reductions():
            assert r.reduction_is_consistent, f"Inconsistent reduction for {r.spacetime_symmetry}"

    def test_all_have_scalar_trace(self) -> None:
        from grut.tensorial_memory import check_symmetry_reductions
        for r in check_symmetry_reductions():
            assert r.scalar_trace_present, f"No scalar trace in {r.spacetime_symmetry}"

    def test_frw_has_one_component(self) -> None:
        """FRW isotropic: only 1 component (scalar trace) survives."""
        from grut.tensorial_memory import check_symmetry_reductions
        reductions = {r.spacetime_symmetry: r for r in check_symmetry_reductions()}
        assert reductions["FRW_isotropic"].surviving_components == 1
        assert reductions["FRW_isotropic"].additional_components == 0

    def test_spherical_has_two_components(self) -> None:
        """Spherical: 2 components (trace + anisotropy) survive."""
        from grut.tensorial_memory import check_symmetry_reductions
        reductions = {r.spacetime_symmetry: r for r in check_symmetry_reductions()}
        assert reductions["spherical"].surviving_components == 2

    def test_axisymmetric_has_four_components(self) -> None:
        """Axisymmetric (Kerr-like): 4 components survive."""
        from grut.tensorial_memory import check_symmetry_reductions
        reductions = {r.spacetime_symmetry: r for r in check_symmetry_reductions()}
        assert reductions["axisymmetric"].surviving_components == 4

    def test_general_has_ten_components(self) -> None:
        """General spacetime: all 10 components survive."""
        from grut.tensorial_memory import check_symmetry_reductions
        reductions = {r.spacetime_symmetry: r for r in check_symmetry_reductions()}
        assert reductions["general"].surviving_components == 10

    def test_component_count_monotonic(self) -> None:
        """More symmetry => fewer surviving components."""
        from grut.tensorial_memory import check_symmetry_reductions
        reductions = {r.spacetime_symmetry: r for r in check_symmetry_reductions()}
        assert reductions["FRW_isotropic"].surviving_components < \
               reductions["spherical"].surviving_components < \
               reductions["axisymmetric"].surviving_components < \
               reductions["general"].surviving_components


# ============================================================================
# 4. ANISOTROPIC STRESS ESTIMATES
# ============================================================================

class TestAnisotropicEstimates:
    """Order-of-magnitude anisotropic stress estimates must be physically sensible."""

    def test_cosmo_is_subdominant(self) -> None:
        """Cosmological anisotropic memory must be subdominant."""
        from grut.tensorial_memory import estimate_anisotropic_stress_cosmo
        est = estimate_anisotropic_stress_cosmo()
        assert est.sigma_is_subdominant

    def test_cosmo_sigma_positive(self) -> None:
        from grut.tensorial_memory import estimate_anisotropic_stress_cosmo
        est = estimate_anisotropic_stress_cosmo()
        assert est.sigma_over_phi > 0

    def test_collapse_sigma_order_unity(self) -> None:
        """Collapse anisotropic stress should be order unity."""
        from grut.tensorial_memory import estimate_anisotropic_stress_collapse
        est = estimate_anisotropic_stress_collapse()
        assert 0.1 < est.sigma_over_phi < 10.0

    def test_collapse_not_subdominant(self) -> None:
        """Collapse anisotropy is NOT subdominant (order unity)."""
        from grut.tensorial_memory import estimate_anisotropic_stress_collapse
        est = estimate_anisotropic_stress_collapse()
        assert not est.sigma_is_subdominant


# ============================================================================
# 5. MASTER ANALYSIS
# ============================================================================

class TestMasterAnalysis:
    """The master analysis must produce a valid, complete result."""

    def test_result_is_valid(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert result.valid

    def test_scalar_sufficient_for_phase3(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert result.scalar_sufficient_for_phase3

    def test_scalar_is_symmetry_limit(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert result.scalar_is_symmetry_limit

    def test_scalar_ontology_undetermined(self) -> None:
        """Scalar ontology must be undetermined (honest)."""
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert result.scalar_field_ontology == "undetermined"

    def test_recommended_immediate(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert result.recommended_immediate == "constitutive_aniso"

    def test_recommended_next(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert result.recommended_next == "scalar_plus_aniso"

    def test_recommended_future(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert result.recommended_future == "rank2_tensor"

    def test_phase3_unchanged_count(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert len(result.phase3_unchanged) >= 6

    def test_phase3_modified_count(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert len(result.phase3_modified) >= 4

    def test_new_physics_count(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert len(result.new_physics_with_tensor) >= 4

    def test_nonclaims_minimum(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert len(result.nonclaims) >= 10

    def test_extension_path_three_stages(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis
        result = compute_tensorial_memory_analysis()
        assert len(result.extension_path) >= 3


# ============================================================================
# 6. SERIALIZATION
# ============================================================================

class TestSerialization:
    """Serialization must produce valid dicts."""

    def test_candidate_to_dict(self) -> None:
        from grut.tensorial_memory import build_candidate_scalar_only, tensor_candidate_to_dict
        c = build_candidate_scalar_only()
        d = tensor_candidate_to_dict(c)
        assert d["name"] == "scalar_only"
        assert d["total_dof"] == 1
        assert isinstance(d["nonclaims"], list)

    def test_full_result_to_dict(self) -> None:
        from grut.tensorial_memory import compute_tensorial_memory_analysis, tensorial_result_to_dict
        result = compute_tensorial_memory_analysis()
        d = tensorial_result_to_dict(result)
        assert d["valid"] is True
        assert d["scalar_sufficient_for_phase3"] is True
        assert len(d["candidates"]) == 5
        assert d["scalar_field_ontology"] == "undetermined"
