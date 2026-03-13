"""Tests for grut.field_equations — Covariant GRUT Field Equation Analysis.

Verification matrix
-------------------
1. Candidate formulations: 3 candidates built with correct properties
2. Weak-field reduction: cosmological memory ODE recovered at effective level
3. Strong-field reduction: collapse ODE, endpoint law, identity, PDE dispersion recovered
4. Bianchi compatibility: effective-level combined conservation for both sectors
5. Master analysis: internally consistent, serialization, closures populated

STATUS: FIRST COVARIANT PASS — auxiliary memory field (scalarized first pass)
NOT derived from a covariant action. Scalar is the minimal closure;
tensorial generalization remains open.

NONCLAIMS:
- Tests verify structural consistency, NOT physical correctness
- "Recovered" means matches current solver structure, NOT first-principles derivation
- Bianchi compatibility is at the effective level, not proven from variational principles
- T^Φ_μν is schematic/effective — tests do not verify a specific stress-energy form
"""

from __future__ import annotations

import math

import pytest

from grut.field_equations import (
    G_SI,
    C_SI,
    M_SUN,
    CandidateFormulation,
    MemoryFieldParams,
    BianchiCheck,
    WeakFieldReduction,
    StrongFieldReduction,
    FieldEquationResult,
    build_candidate_formulations,
    check_weak_field_reduction,
    check_strong_field_reduction,
    check_bianchi_compatibility,
    compute_field_equation_analysis,
    candidate_to_dict,
    bianchi_to_dict,
    field_equation_result_to_dict,
    _memory_update_exact,
)


# ================================================================
# 1. Candidate Formulations
# ================================================================

class TestCandidateFormulations:
    """Tests for candidate covariant formulation construction."""

    def test_three_candidates_built(self) -> None:
        """build_candidate_formulations() returns exactly 3 candidates."""
        candidates = build_candidate_formulations()
        assert len(candidates) == 3

    def test_candidate1_insufficient(self) -> None:
        """Candidate 1 (algebraic tensor) is structurally insufficient."""
        candidates = build_candidate_formulations()
        c1 = candidates[0]
        assert c1.name == "algebraic_tensor"
        assert c1.memory_type == "algebraic"
        assert c1.has_independent_dynamics is False
        assert c1.sufficient is False
        assert c1.preferred is False
        # Cannot recover either sector (no independent dynamics → no relaxation)
        assert c1.weak_field_recovers is False
        assert c1.strong_field_recovers is False

    def test_candidate2_preferred(self) -> None:
        """Candidate 2 (auxiliary scalar) is the preferred formulation."""
        candidates = build_candidate_formulations()
        c2 = candidates[1]
        assert c2.name == "auxiliary_scalar"
        assert c2.memory_type == "scalar_field"
        assert c2.has_independent_dynamics is True
        assert c2.sufficient is True
        assert c2.preferred is True
        assert c2.kernel_type == "exponential"
        assert c2.weak_field_recovers is True
        assert c2.strong_field_recovers is True
        assert c2.bianchi_compatible_effective is True
        # Verify scalarized first pass framing
        assert "scalarized first pass" in c2.label

    def test_candidate3_formal_parent(self) -> None:
        """Candidate 3 (nonlocal kernel) is the formal parent of Candidate 2."""
        candidates = build_candidate_formulations()
        c3 = candidates[2]
        assert c3.name == "nonlocal_kernel"
        assert c3.memory_type == "nonlocal_integral"
        assert c3.has_independent_dynamics is True
        assert c3.sufficient is True
        assert c3.preferred is False  # parent, not preferred for implementation
        assert c3.kernel_type == "general_causal"
        # Relationship to Candidate 2
        assert "formal parent" in c3.relationship_to_others.lower()

    def test_exponential_kernel_equivalence(self) -> None:
        """Candidates 2 and 3 are equivalent for exponential kernel along single observer flow."""
        candidates = build_candidate_formulations()
        c2 = candidates[1]
        c3 = candidates[2]
        # Both sufficient
        assert c2.sufficient and c3.sufficient
        # C2 is the local realization of C3
        assert "local realization" in c2.relationship_to_others.lower()
        assert "exponential kernel" in c2.relationship_to_others.lower()
        # C3 acknowledges the single-observer limitation
        assert any("observer flow" in nc.lower() or "covariant" in nc.lower() for nc in c3.nonclaims)


# ================================================================
# 2. Weak-Field Reduction
# ================================================================

class TestWeakFieldReduction:
    """Tests for cosmological sector recovery at the effective level."""

    def test_friedmann_recovered(self) -> None:
        """Modified Friedmann equation H² = (1−α)H²_base + α·Φ recovered."""
        wf = check_weak_field_reduction(alpha_mem=0.1)
        assert wf.friedmann_recovered is True
        assert wf.H_sq_match_rtol < 1e-12

    def test_memory_ode_recovered(self) -> None:
        """Memory ODE τ_eff dΦ/dt + Φ = H²_base recovered."""
        wf = check_weak_field_reduction(alpha_mem=0.1)
        assert wf.memory_ode_recovered is True

    def test_tau_coupling_recovered(self) -> None:
        """τ_eff(H) = τ₀/(1+(Hτ₀)²) coupling recovered."""
        wf = check_weak_field_reduction(alpha_mem=0.1)
        assert wf.tau_coupling_recovered is True

    def test_lag_structure_verified(self) -> None:
        """Memory state lags behind driver — lag structure verified."""
        wf = check_weak_field_reduction(alpha_mem=0.1)
        # fully_recovered implies all three sub-checks passed
        assert wf.fully_recovered is True
        # Recovery level must be "effective", NOT "derived"
        assert wf.recovery_level == "effective"


# ================================================================
# 3. Strong-Field Reduction
# ================================================================

class TestStrongFieldReduction:
    """Tests for collapse sector recovery at the effective level."""

    def test_force_balance_at_equilibrium(self) -> None:
        """Force balance at R_eq: barrier = gravity → net force = 0."""
        sf = check_strong_field_reduction(
            M_kg=30.0 * M_SUN,
            alpha_vac=1.0 / 3.0,
            beta_Q=2.0,
            epsilon_Q=1.0 / 9.0,
        )
        assert sf.force_balance_recovered is True

    def test_memory_ode_matches_collapse(self) -> None:
        """Memory ODE dM_drive/dt = (a_grav − M_drive)/τ_eff at equilibrium."""
        sf = check_strong_field_reduction(M_kg=30.0 * M_SUN)
        assert sf.memory_ode_recovered is True

    def test_endpoint_law_recovered(self) -> None:
        """Constrained endpoint law R_eq/r_s = ε_Q^(1/β_Q) = 1/3."""
        sf = check_strong_field_reduction(
            M_kg=30.0 * M_SUN,
            epsilon_Q=1.0 / 9.0,
            beta_Q=2.0,
        )
        assert sf.endpoint_recovered is True
        # Verify the numerical value
        ratio = (1.0 / 9.0) ** (1.0 / 2.0)
        assert abs(ratio - 1.0 / 3.0) < 1e-12

    def test_structural_identity_preserved(self) -> None:
        """ω₀ × τ_local = 1.0 preserved in covariant framework."""
        sf = check_strong_field_reduction(M_kg=30.0 * M_SUN)
        assert sf.structural_identity_preserved is True

    def test_pde_dispersion_recovered(self) -> None:
        """PDE dispersion relation ω² = ω₀² + 2αω²_g/(1+iωτ) recovered."""
        sf = check_strong_field_reduction(M_kg=30.0 * M_SUN)
        assert sf.pde_dispersion_recovered is True
        assert sf.fully_recovered is True
        assert sf.recovery_level == "effective"


# ================================================================
# 4. Bianchi Compatibility
# ================================================================

class TestBianchiCompatibility:
    """Tests for effective-level Bianchi compatibility."""

    def test_cosmological_sector_compatible(self) -> None:
        """Cosmological sector: combined conservation satisfied at effective level."""
        bc = check_bianchi_compatibility("cosmological")
        assert bc.combined_conserved is True
        assert bc.status == "compatible_effective"
        # Fundamental statement must reference combined conservation
        assert any("combined" in n.lower() for n in bc.notes)

    def test_collapse_sector_compatible(self) -> None:
        """Collapse sector: combined conservation satisfied at effective level."""
        bc = check_bianchi_compatibility("collapse")
        assert bc.combined_conserved is True
        assert bc.status == "compatible_effective"
        # Individual components NOT separately conserved in collapse sector
        assert "not separately" in bc.individual_conservation_status.lower()

    def test_conservation_modes_correct(self) -> None:
        """Conservation modes correctly labeled for each sector."""
        bc_cosmo = check_bianchi_compatibility("cosmological")
        bc_collapse = check_bianchi_compatibility("collapse")
        # Cosmological: approximate separate conservation in weak-field regime
        assert "approximate_separate" in bc_cosmo.conservation_mode
        # Collapse: no separate conservation at all
        assert "no_separate" in bc_collapse.conservation_mode


# ================================================================
# 5. Master Analysis Result
# ================================================================

class TestFieldEquationResult:
    """Tests for the master field equation analysis."""

    def test_preferred_is_auxiliary_scalar(self) -> None:
        """Preferred formulation is auxiliary_scalar."""
        result = compute_field_equation_analysis()
        assert result.preferred_name == "auxiliary_scalar"
        assert result.preferred is not None
        assert result.preferred.preferred is True

    def test_internally_consistent(self) -> None:
        """Full analysis is internally consistent."""
        result = compute_field_equation_analysis()
        assert result.internally_consistent is True
        assert result.valid is True
        assert result.approx_level == "auxiliary_scalar_field_effective"

    def test_serialization_roundtrip(self) -> None:
        """Serialization produces valid dict with all expected keys."""
        result = compute_field_equation_analysis()
        d = field_equation_result_to_dict(result)
        # Top-level keys
        assert "candidates" in d
        assert "preferred_name" in d
        assert "memory_params" in d
        assert "bianchi_checks" in d
        assert "weak_field" in d
        assert "strong_field" in d
        assert "internally_consistent" in d
        assert "resolved_closures" in d
        assert "remaining_closures" in d
        assert "ansatz_items" in d
        assert "derived_items" in d
        assert "nonclaims" in d
        assert "valid" in d
        # 3 candidates
        assert len(d["candidates"]) == 3
        # Preferred name
        assert d["preferred_name"] == "auxiliary_scalar"
        # Bianchi checks for both sectors
        assert len(d["bianchi_checks"]) == 2
        # Memory params include alpha unification status
        assert "alpha_unification_status" in d["memory_params"]

    def test_closures_populated(self) -> None:
        """Both resolved and remaining closures are populated."""
        result = compute_field_equation_analysis()
        assert len(result.resolved_closures) >= 5
        assert len(result.remaining_closures) >= 7
        # Remaining closures must include T^Phi_mu_nu and junction conditions
        remaining_str = " ".join(result.remaining_closures).lower()
        assert "t^phi" in remaining_str or "stress-energy" in remaining_str or "lagrangian" in remaining_str
        assert "junction" in remaining_str or "israel" in remaining_str

    def test_ansatz_vs_derived_labeled(self) -> None:
        """Ansatz items and derived items are correctly classified."""
        result = compute_field_equation_analysis()
        assert len(result.ansatz_items) >= 4
        assert len(result.derived_items) >= 4
        # T^Phi is ansatz, not derived
        ansatz_str = " ".join(result.ansatz_items).lower()
        assert "t^phi" in ansatz_str or "stress-energy" in ansatz_str or "schematic" in ansatz_str
        # Candidate 1 insufficiency is derived, not assumed
        derived_str = " ".join(result.derived_items).lower()
        assert "candidate 1" in derived_str or "insufficiency" in derived_str

    def test_nonclaims_minimum(self) -> None:
        """At least 10 nonclaims are present."""
        result = compute_field_equation_analysis()
        assert len(result.nonclaims) >= 10

    def test_alpha_unification_flagged_open(self) -> None:
        """α_mem vs α_vac unification is flagged as open research target."""
        result = compute_field_equation_analysis()
        assert "open" in result.memory_params.alpha_unification_status.lower()
        # Nonclaims should mention it
        nc_str = " ".join(result.nonclaims).lower()
        assert "alpha" in nc_str or "α" in nc_str

    def test_candidate_serialization(self) -> None:
        """Individual candidate serialization works correctly."""
        candidates = build_candidate_formulations()
        for c in candidates:
            d = candidate_to_dict(c)
            assert "name" in d
            assert "memory_type" in d
            assert "sufficient" in d
            assert "nonclaims" in d

    def test_bianchi_serialization(self) -> None:
        """Bianchi check serialization works correctly."""
        bc = check_bianchi_compatibility("cosmological")
        d = bianchi_to_dict(bc)
        assert d["sector"] == "cosmological"
        assert d["combined_conserved"] is True
        assert d["status"] == "compatible_effective"


# ================================================================
# 6. Memory Update Function
# ================================================================

class TestMemoryUpdate:
    """Tests for the inline exponential memory update."""

    def test_steady_state(self) -> None:
        """At steady state (M = X), no change."""
        M = 1.0
        X = 1.0
        result = _memory_update_exact(M, X, dt=0.1, tau_eff=1.0)
        assert abs(result - X) < 1e-15

    def test_relaxation_toward_driver(self) -> None:
        """M relaxes toward X on timescale tau_eff."""
        M = 0.0
        X = 1.0
        tau = 1.0
        dt = 0.01 * tau
        result = _memory_update_exact(M, X, dt, tau)
        # Should move toward X
        assert 0 < result < X
        # Should be close to dt/tau * X for small dt
        linear_approx = dt / tau * X
        assert abs(result - linear_approx) < 0.01 * linear_approx

    def test_long_time_convergence(self) -> None:
        """After many tau, M → X."""
        M = 0.0
        X = 1.0
        tau = 1.0
        result = _memory_update_exact(M, X, dt=100.0 * tau, tau_eff=tau)
        assert abs(result - X) < 1e-10

    def test_zero_tau_instant_response(self) -> None:
        """With tau=0 or dt=0, returns X (instant response)."""
        result = _memory_update_exact(0.5, 1.0, dt=0.1, tau_eff=0.0)
        assert result == 1.0
        result2 = _memory_update_exact(0.5, 1.0, dt=0.0, tau_eff=1.0)
        assert result2 == 1.0
