"""Tests for Phase III Final Completion Packages A, B, C.

Package A: Memory Tensor Closure (grut/memory_tensor.py)
Package B: Boundary/Matching Closure (grut/junctions.py)
Package C: Final Observable Closure (grut/observables_final.py)

STATUS: EFFECTIVE-LEVEL TESTS
Verify structural consistency and constitutive correctness of the
final Phase III closure modules. Do NOT test first-principles
derivation (which does not exist).
"""

from __future__ import annotations

import math
import pytest

from grut.memory_tensor import (
    compute_cosmo_memory_tensor,
    compute_collapse_memory_tensor,
    assess_action_status,
    compare_scalar_vs_tensor,
    verify_cosmo_conservation,
    compute_package_a_analysis,
    package_a_to_dict,
    M_SUN,
)

from grut.junctions import (
    compute_junction_conditions,
    compute_transition_layer,
    compute_matching_consistency,
    compute_package_b_analysis,
    package_b_to_dict,
)

from grut.observables_final import (
    compute_tidal_love_numbers,
    estimate_kerr_correction,
    estimate_nonlinear_coupling,
    compute_detectability_summary,
    compute_package_c_analysis,
    package_c_to_dict,
)


# ================================================================
# Package A: Memory Tensor
# ================================================================

class TestCosmoMemoryTensor:
    """Tests for cosmological effective T^Φ_μν."""

    def test_steady_state_invisible(self) -> None:
        """At steady state (Φ = H²_base), ρ_Φ = 0."""
        t = compute_cosmo_memory_tensor(
            alpha_mem=0.1,
            H_current=1.0,
            H_base_sq=1.0,
            Phi=1.0,  # steady state
            dPhi_dt=0.0,
        )
        assert t.valid
        assert abs(t.rho_phi) < 1e-14

    def test_lagged_state_nonzero(self) -> None:
        """Out of steady state: ρ_Φ ≠ 0, encodes lag."""
        t = compute_cosmo_memory_tensor(
            alpha_mem=0.1,
            H_current=1.0,
            H_base_sq=1.0,
            Phi=0.9,  # 10% lag
            dPhi_dt=0.2,
        )
        assert t.valid
        assert t.rho_phi != 0.0
        # Lag (Phi < H_base_sq) → negative ρ_Φ (memory trails driver)
        assert t.rho_phi < 0.0

    def test_derivation_constitutive(self) -> None:
        """Derivation is constitutive, not action-derived."""
        t = compute_cosmo_memory_tensor()
        assert t.derivation == "constitutive"

    def test_sector_label(self) -> None:
        """Sector is cosmological."""
        t = compute_cosmo_memory_tensor(H_current=1.0, H_base_sq=1.0, Phi=0.9)
        assert t.sector == "cosmological"


class TestCollapseMemoryTensor:
    """Tests for collapse effective T^Φ_μν."""

    def test_equilibrium_negligible(self) -> None:
        """At equilibrium (M_drive = a_grav), ρ_Φ → 0."""
        M = 30.0 * M_SUN
        t = compute_collapse_memory_tensor(M_kg=M)
        assert t.valid
        # At equilibrium, memory_fraction = 0 → ρ_Φ = 0
        assert abs(t.rho_phi) < 1e-10

    def test_anisotropic_structure(self) -> None:
        """Collapse sector has anisotropic stress."""
        t = compute_collapse_memory_tensor(M_kg=30.0 * M_SUN)
        assert t.sector == "collapse"
        assert t.derivation == "constitutive"


class TestActionStatus:
    """Tests for action / Lagrangian classification."""

    def test_classification_constitutive(self) -> None:
        """Current status is constitutive_effective."""
        a = assess_action_status()
        assert a.classification == "constitutive_effective"

    def test_dissipation_barrier_documented(self) -> None:
        """Dissipation barrier is documented."""
        a = assess_action_status()
        assert "first-order" in a.dissipation_barrier.lower()
        assert "overdamped" in a.dissipation_barrier.lower()

    def test_galley_applicable(self) -> None:
        """Galley doubled formalism is applicable."""
        a = assess_action_status()
        assert a.galley_formalism_applicable is True

    def test_nonclaims_present(self) -> None:
        """Action status has ≥ 5 nonclaims."""
        a = assess_action_status()
        assert len(a.nonclaims) >= 5


class TestTensorialComparison:
    """Tests for scalar vs tensorial memory comparison."""

    def test_scalar_dof(self) -> None:
        """Scalar has 1 DOF."""
        tc = compare_scalar_vs_tensor()
        assert tc.scalar_dof == 1

    def test_scalar_sufficient_for_current(self) -> None:
        """Scalar sufficient for all current Phase III results."""
        tc = compare_scalar_vs_tensor()
        assert len(tc.scalar_sufficient_for) >= 5
        assert any("phase iii" in s.lower() for s in tc.scalar_sufficient_for)

    def test_tensor_required_items(self) -> None:
        """Tensorial required for anisotropic / propagating effects."""
        tc = compare_scalar_vs_tensor()
        assert len(tc.tensor_required_for) >= 3

    def test_recommendation_scalar(self) -> None:
        """Recommendation is scalar sufficient for current pass."""
        tc = compare_scalar_vs_tensor()
        assert "sufficient" in tc.recommendation.lower()


class TestCosmoConservation:
    """Tests for combined conservation verification."""

    def test_conservation_verified(self) -> None:
        """Combined conservation satisfied by construction."""
        result = verify_cosmo_conservation(
            alpha_mem=0.1, H=1.0, H_base_sq=1.0,
            Phi=0.9, tau_eff=0.5, rho_m=1.0, w=0.0,
        )
        assert result["verified"] is True
        assert abs(result["residual"]) < 1e-10


class TestPackageAMaster:
    """Tests for the master Package A analysis."""

    def test_package_a_valid(self) -> None:
        result = compute_package_a_analysis()
        assert result.valid is True
        assert result.conservation_verified is True

    def test_package_a_nonclaims(self) -> None:
        result = compute_package_a_analysis()
        assert len(result.nonclaims) >= 8

    def test_package_a_serialization(self) -> None:
        result = compute_package_a_analysis()
        d = package_a_to_dict(result)
        assert d["valid"] is True
        assert d["action_classification"] == "constitutive_effective"


# ================================================================
# Package B: Boundary / Matching
# ================================================================

class TestJunctionConditions:
    """Tests for Israel-Darmois junction conditions."""

    def test_first_junction(self) -> None:
        """First junction (metric continuity) satisfied."""
        j = compute_junction_conditions(M_kg=30.0 * M_SUN)
        assert j.first_junction_satisfied is True
        assert j.metric_continuous is True

    def test_second_junction_evaluated(self) -> None:
        """Second junction (extrinsic curvature) evaluated."""
        j = compute_junction_conditions(M_kg=30.0 * M_SUN)
        assert j.second_junction_evaluated is True
        assert j.sigma_surface > 0  # positive surface energy

    def test_memory_field_jump(self) -> None:
        """Memory field jumps from a_grav to 0 at boundary."""
        j = compute_junction_conditions(M_kg=30.0 * M_SUN)
        assert j.Phi_interior > 0
        assert j.Phi_exterior == 0.0
        assert j.Phi_jump > 0

    def test_sharp_boundary_valid(self) -> None:
        """Sharp-boundary approximation validated."""
        j = compute_junction_conditions(M_kg=30.0 * M_SUN)
        assert j.sharp_boundary_valid is True
        assert abs(j.grading_factor - 0.996) < 0.01

    def test_compactness_correct(self) -> None:
        """Compactness = 3/2 for R_eq = r_s/3."""
        j = compute_junction_conditions(M_kg=30.0 * M_SUN)
        assert abs(j.compactness - 1.5) < 0.01


class TestTransitionLayer:
    """Tests for transition layer embedding."""

    def test_quasi_sharp(self) -> None:
        """Transition layer is in quasi-sharp regime (λ >> width)."""
        tr = compute_transition_layer(M_kg=30.0 * M_SUN)
        assert tr.valid
        assert tr.quasi_sharp is True

    def test_grading_factor(self) -> None:
        """Grading factor ~0.996 (< 1% correction)."""
        tr = compute_transition_layer(M_kg=30.0 * M_SUN)
        assert abs(tr.grading_factor - 0.996) < 0.01
        assert tr.impedance_correction_pct < 1.0


class TestMatchingConsistency:
    """Tests for full matching consistency."""

    def test_overall_consistent(self) -> None:
        """Full matching is consistent at effective level."""
        mc = compute_matching_consistency(M_kg=30.0 * M_SUN)
        assert mc.overall_consistent is True
        assert mc.status == "consistent_effective"

    def test_mass_conserved(self) -> None:
        mc = compute_matching_consistency(M_kg=30.0 * M_SUN)
        assert mc.mass_conserved is True

    def test_underdetermined_present(self) -> None:
        mc = compute_matching_consistency(M_kg=30.0 * M_SUN)
        assert len(mc.underdetermined_quantities) >= 3


class TestPackageBMaster:
    """Tests for master Package B analysis."""

    def test_package_b_valid(self) -> None:
        result = compute_package_b_analysis()
        assert result.valid is True

    def test_package_b_serialization(self) -> None:
        result = compute_package_b_analysis()
        d = package_b_to_dict(result)
        assert d["valid"] is True
        assert d["matching_consistent"] is True


# ================================================================
# Package C: Final Observables
# ================================================================

class TestTidalLoveNumbers:
    """Tests for tidal Love number estimates."""

    def test_love_number_nonzero(self) -> None:
        """k₂ > 0 for reflecting BDCC (unlike GR BH where k₂ = 0)."""
        tlr = compute_tidal_love_numbers(M_kg=30.0 * M_SUN)
        assert tlr.valid
        assert tlr.k2_estimate > 0.0
        assert tlr.k2_GR_BH == 0.0

    def test_love_number_small(self) -> None:
        """k₂ is small (suppressed by barrier transmission)."""
        tlr = compute_tidal_love_numbers(M_kg=30.0 * M_SUN)
        assert tlr.k2_estimate < 0.1

    def test_candidate_non_null(self) -> None:
        """Love numbers are a candidate non-null channel."""
        tlr = compute_tidal_love_numbers(M_kg=30.0 * M_SUN)
        assert tlr.channel_type == "candidate_non_null"


class TestKerrEstimate:
    """Tests for Kerr / spin corrections."""

    def test_zero_spin_identity(self) -> None:
        """At χ=0 (Schwarzschild), all ratios = 1."""
        ke = estimate_kerr_correction(a_over_M=0.0)
        assert ke.valid
        assert abs(ke.echo_delay_ratio - 1.0) < 0.01
        assert abs(ke.omega_QNM_ratio - 1.0) < 0.01
        assert abs(ke.r_plus_over_M - 2.0) < 0.01

    def test_spin_reduces_echo_delay(self) -> None:
        """Spin reduces echo delay (shorter cavity)."""
        ke = estimate_kerr_correction(a_over_M=0.7)
        assert ke.echo_delay_ratio < 1.0

    def test_spin_increases_qnm_freq(self) -> None:
        """Spin increases QNM frequency."""
        ke = estimate_kerr_correction(a_over_M=0.7)
        assert ke.omega_QNM_ratio > 1.0

    def test_high_spin_needs_verification(self) -> None:
        """High spin: structural identity needs verification."""
        ke = estimate_kerr_correction(a_over_M=0.9)
        assert "needs_verification" in ke.identity_preserved


class TestNonlinearCoupling:
    """Tests for nonlinear mode coupling estimates."""

    def test_small_perturbation_linear(self) -> None:
        """Small perturbations: linear regime valid, ΔQ/Q << 1."""
        ne = estimate_nonlinear_coupling(delta_R_over_R_eq=0.01)
        assert ne.valid
        assert ne.linear_regime_valid is True
        assert ne.delta_Q_over_Q < 0.01

    def test_q_robust(self) -> None:
        """Universal Q=6 robust for small perturbations."""
        ne = estimate_nonlinear_coupling(delta_R_over_R_eq=0.01, Q_linear=6.0)
        assert abs(ne.Q_corrected - 6.0) < 0.1

    def test_breakdown_amplitude(self) -> None:
        """Breakdown amplitude is O(1)."""
        ne = estimate_nonlinear_coupling()
        assert ne.breakdown_amplitude > 0.1
        assert ne.breakdown_amplitude < 10.0


class TestDetectability:
    """Tests for detectability summary."""

    def test_four_channels(self) -> None:
        """Four observable channels assessed."""
        ds = compute_detectability_summary()
        assert len(ds.channels) == 4

    def test_echo_marginal_current(self) -> None:
        """Echo is marginal for current detectors."""
        ds = compute_detectability_summary()
        echo = ds.channels[0]
        assert "marginal" in echo.detector_current.lower()

    def test_null_channel_present(self) -> None:
        """Static null channels properly classified."""
        ds = compute_detectability_summary()
        null = [c for c in ds.channels if c.status == "null"]
        assert len(null) >= 1

    def test_falsification_summary_present(self) -> None:
        """Falsification pathways documented."""
        ds = compute_detectability_summary()
        assert len(ds.falsification_summary) > 100


class TestPackageCMaster:
    """Tests for master Package C analysis."""

    def test_package_c_valid(self) -> None:
        result = compute_package_c_analysis()
        assert result.valid is True

    def test_package_c_kerr_multi_spin(self) -> None:
        """Kerr estimated at multiple spin values."""
        result = compute_package_c_analysis()
        assert len(result.kerr_estimates) >= 3

    def test_package_c_serialization(self) -> None:
        result = compute_package_c_analysis()
        d = package_c_to_dict(result)
        assert d["valid"] is True
        assert "love_numbers" in d
        assert "kerr_estimates" in d
