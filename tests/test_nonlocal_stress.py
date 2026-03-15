"""Tests for grut.nonlocal_stress — Route C nonlocal stress-functional construction.

Coverage:
- TestNonlocalAction: kernel properties, normalization, causality, Markov
- TestMetricVariation: contributions, classification, local reduction
- TestStressFunctional: decomposition, derivation chain, forms
- TestMarkovProperty: two-history test, Phi match, T^Phi match
- TestCosmoReduction: convolution=ODE, Friedmann, memory ODE, tau coupling
- TestCollapseReduction: force balance, memory ODE, endpoint
- TestBianchiCompatibility: cosmo consistency, collapse consistency
- TestRouteBComparison: same T^Phi, different derivation, advantages
- TestMasterAnalysis: all components present, classification, ontology
- TestSerialization: round-trip, all fields populated
"""

from __future__ import annotations

import math
import pytest

from grut.nonlocal_stress import (
    NonlocalRetardedAction,
    MetricVariationAnalysis,
    StressFunctional,
    MarkovTestResult,
    CosmoReduction,
    CollapseReduction,
    BianchiAnalysis,
    RouteBComparison,
    RouteCClassification,
    RouteCStressResult,
    build_nonlocal_action,
    analyze_metric_variation,
    construct_stress_functional,
    verify_cosmo_reduction,
    verify_collapse_reduction,
    analyze_bianchi_compatibility,
    compare_to_route_b,
    compute_route_c_stress_analysis,
    stress_result_to_dict,
    _retarded_kernel,
    _convolution_integral,
    _integrate_memory_ode,
    _effective_rho_phi,
    C_RHO,
    G_SI,
    M_SUN,
)
from grut.nonlocal_stress import test_markov_property as _test_markov_property


# ================================================================
# TestNonlocalAction
# ================================================================

class TestNonlocalAction:
    """Tests for the nonlocal retarded action construction."""

    def test_kernel_normalized(self):
        action = build_nonlocal_action(tau_eff=1.0)
        assert action.kernel_normalized
        assert abs(action.kernel_norm_value - 1.0) < 0.01

    def test_kernel_normalized_different_tau(self):
        for tau in [0.1, 1.0, 5.0, 100.0]:
            action = build_nonlocal_action(tau_eff=tau)
            assert action.kernel_normalized, f"Failed for tau={tau}"

    def test_kernel_causal(self):
        action = build_nonlocal_action(tau_eff=1.0)
        assert action.is_causal

    def test_kernel_real(self):
        action = build_nonlocal_action(tau_eff=1.0)
        assert action.is_real

    def test_kernel_causal_values(self):
        """K(s) = 0 for s < 0 (causality)."""
        for s in [-1.0, -0.1, -0.001]:
            assert _retarded_kernel(s, 1.0) == 0.0

    def test_kernel_positive(self):
        """K(s) >= 0 for s >= 0."""
        for s in [0.0, 0.1, 1.0, 10.0, 100.0]:
            assert _retarded_kernel(s, 1.0) >= 0.0

    def test_kernel_peak_at_zero(self):
        """K(0) = 1/tau (maximum value)."""
        tau = 2.5
        assert abs(_retarded_kernel(0.0, tau) - 1.0 / tau) < 1e-14

    def test_kernel_decaying(self):
        """K(s) is monotonically decreasing for s > 0."""
        tau = 1.0
        for i in range(10):
            s1 = i * 0.5
            s2 = (i + 1) * 0.5
            assert _retarded_kernel(s1, tau) >= _retarded_kernel(s2, tau)

    def test_markov_property_flag(self):
        action = build_nonlocal_action(tau_eff=1.0)
        assert action.markov_property

    def test_local_auxiliary_equivalent(self):
        action = build_nonlocal_action(tau_eff=1.0)
        assert action.local_auxiliary_equivalent

    def test_exponential_kernel_special_nonempty(self):
        action = build_nonlocal_action(tau_eff=1.0)
        assert len(action.exponential_kernel_special) >= 4

    def test_nonclaims_populated(self):
        action = build_nonlocal_action(tau_eff=1.0)
        assert len(action.nonclaims) >= 4


# ================================================================
# TestMetricVariation
# ================================================================

class TestMetricVariation:
    """Tests for the metric variation analysis."""

    def test_formal_variation_exists(self):
        mv = analyze_metric_variation()
        assert mv.formal_variation_exists

    def test_variation_is_nonlocal(self):
        mv = analyze_metric_variation()
        assert mv.variation_is_nonlocal
        assert not mv.variation_is_local

    def test_five_contributions(self):
        mv = analyze_metric_variation()
        assert mv.n_explicit_contributions == 5

    def test_not_computed_explicitly(self):
        mv = analyze_metric_variation()
        assert not mv.computed_explicitly
        assert len(mv.obstruction_to_explicit) > 100

    def test_exponential_local_reduction(self):
        mv = analyze_metric_variation()
        assert mv.exponential_local_reduction
        assert len(mv.local_tphi_form) > 20

    def test_classification(self):
        mv = analyze_metric_variation()
        assert mv.classification == "nonlocal_stress_functional"

    def test_nonclaims(self):
        mv = analyze_metric_variation()
        assert len(mv.nonclaims) >= 3


# ================================================================
# TestStressFunctional
# ================================================================

class TestStressFunctional:
    """Tests for the stress-functional construction."""

    def test_not_local_tensor(self):
        sf = construct_stress_functional()
        assert not sf.is_local_tensor

    def test_local_for_exponential(self):
        sf = construct_stress_functional()
        assert sf.is_local_for_exponential_kernel

    def test_decomposition_valid(self):
        sf = construct_stress_functional()
        assert sf.decomposition_valid

    def test_instantaneous_form_nonempty(self):
        sf = construct_stress_functional()
        assert len(sf.instantaneous_form) > 10

    def test_history_form_nonempty(self):
        sf = construct_stress_functional()
        assert len(sf.history_form) > 10

    def test_on_shell_local_form(self):
        sf = construct_stress_functional()
        assert "Markov" in sf.on_shell_local_form or "exponential" in sf.on_shell_local_form

    def test_classification_functional_derived(self):
        sf = construct_stress_functional()
        assert sf.classification == "functional_derived"

    def test_derivation_chain(self):
        sf = construct_stress_functional()
        assert len(sf.derivation_chain) >= 5

    def test_cosmo_forms(self):
        sf = construct_stress_functional()
        assert len(sf.cosmo_rho_phi_form) > 10
        assert len(sf.cosmo_p_phi_form) > 10

    def test_collapse_form(self):
        sf = construct_stress_functional()
        assert len(sf.collapse_force_form) > 10

    def test_nonclaims(self):
        sf = construct_stress_functional()
        assert len(sf.nonclaims) >= 5


# ================================================================
# TestMarkovProperty
# ================================================================

class TestMarkovProperty:
    """Tests for the Markov property of the exponential kernel."""

    def test_markov_holds(self):
        mt = _test_markov_property(tau_eff=1.0)
        assert mt.markov_holds

    def test_phi_match(self):
        mt = _test_markov_property(tau_eff=1.0)
        assert mt.phi_match_rtol < 1e-6

    def test_tphi_match(self):
        mt = _test_markov_property(tau_eff=1.0)
        assert mt.tphi_match_rtol < 1e-6

    def test_different_histories_same_phi(self):
        """Two different source histories arrive at same Phi."""
        mt = _test_markov_property(tau_eff=1.0)
        assert abs(mt.phi_A_final - mt.phi_B_final) / abs(mt.phi_A_final) < 1e-6

    def test_different_histories_same_tphi(self):
        """Same Phi => same rho_Phi regardless of history."""
        mt = _test_markov_property(tau_eff=1.0)
        assert abs(mt.tphi_A_rho - mt.tphi_B_rho) / max(abs(mt.tphi_A_rho), 1e-30) < 1e-6

    def test_non_exponential_would_fail(self):
        mt = _test_markov_property(tau_eff=1.0)
        assert mt.non_exponential_would_fail

    def test_different_tau(self):
        for tau in [0.5, 2.0, 10.0]:
            mt = _test_markov_property(tau_eff=tau)
            assert mt.markov_holds, f"Markov failed for tau={tau}"

    def test_notes_populated(self):
        mt = _test_markov_property(tau_eff=1.0)
        assert len(mt.notes) >= 3


# ================================================================
# TestConvolutionODEEquivalence
# ================================================================

class TestConvolutionODEEquivalence:
    """Tests for the mathematical equivalence of convolution and ODE."""

    def test_step_source_equivalence(self):
        """Constant source: convolution matches ODE."""
        tau = 1.0
        T = 10.0 * tau
        n = 2000
        dt = T / n
        times = [i * dt for i in range(n + 1)]
        source = [1.0] * (n + 1)

        phi_ode = _integrate_memory_ode(source, times, tau, phi_0=0.0)
        phi_conv = []
        for i, t in enumerate(times):
            if i == 0:
                phi_conv.append(0.0)
            else:
                val = _convolution_integral(source, times[:i + 1], tau, t)
                phi_conv.append(val)

        # Compare (skip initial points)
        for i in range(n // 5, n + 1):
            if abs(phi_ode[i]) > 1e-10:
                rtol = abs(phi_conv[i] - phi_ode[i]) / abs(phi_ode[i])
                assert rtol < 0.05, f"Step source: rtol={rtol} at i={i}"

    def test_oscillating_source_equivalence(self):
        """Oscillating source: convolution matches ODE."""
        tau = 1.0
        T = 10.0 * tau
        n = 3000
        dt = T / n
        times = [i * dt for i in range(n + 1)]
        source = [1.0 + 0.5 * math.sin(2 * math.pi * t / (3 * tau)) for t in times]

        phi_ode = _integrate_memory_ode(source, times, tau, phi_0=source[0])
        phi_conv = []
        for i, t in enumerate(times):
            if i == 0:
                phi_conv.append(0.0)
            else:
                val = _convolution_integral(source, times[:i + 1], tau, t)
                phi_conv.append(val)

        # Compare after initial transient
        for i in range(n // 3, n + 1):
            denom = abs(phi_ode[i]) if abs(phi_ode[i]) > 1e-10 else 1.0
            rtol = abs(phi_conv[i] - phi_ode[i]) / denom
            assert rtol < 0.1, f"Oscillating source: rtol={rtol} at i={i}"

    def test_ode_exact_for_constant_source(self):
        """ODE solution for constant X: Phi(t) = X*(1 - exp(-t/tau))."""
        tau = 2.0
        X = 3.0
        T = 15.0
        n = 1000
        dt = T / n
        times = [i * dt for i in range(n + 1)]
        source = [X] * (n + 1)

        phi_ode = _integrate_memory_ode(source, times, tau, phi_0=0.0)

        for i in range(n + 1):
            t = times[i]
            exact = X * (1.0 - math.exp(-t / tau))
            assert abs(phi_ode[i] - exact) < 0.01 * X, f"t={t}: ode={phi_ode[i]}, exact={exact}"


# ================================================================
# TestCosmoReduction
# ================================================================

class TestCosmoReduction:
    """Tests for cosmological sector recovery."""

    def test_convolution_ode_equivalence(self):
        cr = verify_cosmo_reduction(alpha_mem=0.1, tau_eff=1.0)
        assert cr.convolution_ode_equivalence
        assert cr.convolution_ode_max_error < 0.05

    def test_friedmann_recovered(self):
        cr = verify_cosmo_reduction(alpha_mem=0.1, tau_eff=1.0)
        assert cr.friedmann_recovered

    def test_memory_ode_recovered(self):
        cr = verify_cosmo_reduction(alpha_mem=0.1, tau_eff=1.0)
        assert cr.memory_ode_recovered

    def test_tau_coupling_recovered(self):
        cr = verify_cosmo_reduction(alpha_mem=0.1, tau_eff=1.0)
        assert cr.tau_coupling_recovered

    def test_different_alpha(self):
        for alpha in [0.01, 0.1, 0.3]:
            cr = verify_cosmo_reduction(alpha_mem=alpha, tau_eff=1.0)
            assert cr.friedmann_recovered, f"Failed for alpha={alpha}"


# ================================================================
# TestCollapseReduction
# ================================================================

class TestCollapseReduction:
    """Tests for collapse sector recovery."""

    def test_force_balance(self):
        cr = verify_collapse_reduction()
        assert cr.force_balance_recovered
        assert cr.equilibrium_residual < 1e-12

    def test_memory_ode(self):
        cr = verify_collapse_reduction()
        assert cr.memory_ode_recovered
        assert cr.memory_ode_residual < 1e-12

    def test_endpoint(self):
        cr = verify_collapse_reduction()
        assert cr.endpoint_recovered

    def test_different_mass(self):
        for M in [10.0 * M_SUN, 30.0 * M_SUN, 100.0 * M_SUN]:
            cr = verify_collapse_reduction(M_kg=M)
            assert cr.force_balance_recovered, f"Failed for M={M/M_SUN} Msun"


# ================================================================
# TestBianchiCompatibility
# ================================================================

class TestBianchiCompatibility:
    """Tests for Bianchi compatibility analysis."""

    def test_cosmo_verified(self):
        ba = analyze_bianchi_compatibility(alpha_mem=0.1, tau_eff=1.0)
        assert ba.cosmo_sector_verified

    def test_collapse_verified(self):
        ba = analyze_bianchi_compatibility(alpha_mem=0.1, tau_eff=1.0)
        assert ba.collapse_sector_verified

    def test_combined_conservation_expected(self):
        ba = analyze_bianchi_compatibility()
        assert ba.combined_conservation_expected

    def test_full_proof_not_available(self):
        ba = analyze_bianchi_compatibility()
        assert not ba.full_proof_available
        assert len(ba.obstruction_to_full_proof) > 100

    def test_classification(self):
        ba = analyze_bianchi_compatibility()
        assert ba.classification == "effective_level_verified"

    def test_nonclaims(self):
        ba = analyze_bianchi_compatibility()
        assert len(ba.nonclaims) >= 3


# ================================================================
# TestRouteBComparison
# ================================================================

class TestRouteBComparison:
    """Tests for Route B vs Route C comparison."""

    def test_same_tphi(self):
        comp = compare_to_route_b()
        assert comp.tphi_expression_same

    def test_different_derivation(self):
        comp = compare_to_route_b()
        assert comp.derivation_chain_different

    def test_complementary(self):
        comp = compare_to_route_b()
        assert comp.complementary

    def test_route_b_advantages_nonempty(self):
        comp = compare_to_route_b()
        assert len(comp.route_b_advantages) >= 3

    def test_route_c_advantages_nonempty(self):
        comp = compare_to_route_b()
        assert len(comp.route_c_advantages) >= 5

    def test_route_c_no_ghost(self):
        comp = compare_to_route_b()
        assert "ghost" in comp.route_c_ghost_status.lower()
        assert "no ghost" in comp.route_c_ghost_status.lower()

    def test_route_b_has_ghost(self):
        comp = compare_to_route_b()
        assert "growing" in comp.route_b_ghost_status.lower()

    def test_overall_assessment(self):
        comp = compare_to_route_b()
        assert "complementary" in comp.overall_assessment.lower()


# ================================================================
# TestMasterAnalysis
# ================================================================

class TestMasterAnalysis:
    """Tests for the master Route C stress-functional analysis."""

    @pytest.fixture(scope="class")
    def result(self):
        return compute_route_c_stress_analysis()

    def test_valid(self, result):
        assert result.valid

    def test_all_components_present(self, result):
        assert result.action is not None
        assert result.metric_variation is not None
        assert result.stress_functional is not None
        assert result.markov_test is not None
        assert result.cosmo_reduction is not None
        assert result.collapse_reduction is not None
        assert result.bianchi is not None
        assert result.route_b_comparison is not None
        assert result.classification is not None

    def test_classification_overall(self, result):
        assert result.classification.overall == "functional_derived"

    def test_classification_action(self, result):
        assert result.classification.nonlocal_action == "formal_parent"

    def test_classification_metric_variation(self, result):
        assert result.classification.metric_variation == "nonlocal_stress_functional"

    def test_classification_stress_functional(self, result):
        assert result.classification.stress_functional == "functional_derived"

    def test_classification_cosmo(self, result):
        assert result.classification.cosmo_reduction == "recovered"

    def test_classification_collapse(self, result):
        assert result.classification.collapse_reduction == "recovered"

    def test_classification_bianchi(self, result):
        assert result.classification.bianchi == "effective_level_verified"

    def test_classification_complementary(self, result):
        assert "complementary" in result.classification.route_c_vs_b

    def test_phi_ontology(self, result):
        assert result.phi_ontology == "effective_local_representation"
        assert len(result.phi_ontology_explanation) > 200

    def test_remaining_obstruction(self, result):
        assert len(result.remaining_obstruction) > 300
        assert "nonlocal" in result.remaining_obstruction.lower()
        assert "observer" in result.remaining_obstruction.lower()

    def test_nonclaims_count(self, result):
        assert len(result.nonclaims) >= 10

    def test_nonclaims_content(self, result):
        nc_text = " ".join(result.nonclaims).lower()
        assert "functional-derived" in nc_text or "functional" in nc_text
        assert "nonlocal" in nc_text
        assert "markov" in nc_text
        assert "observer" in nc_text or "covariance" in nc_text

    def test_diagnostics_populated(self, result):
        assert "kernel_norm" in result.diagnostics
        assert "markov_phi_match_rtol" in result.diagnostics
        assert "cosmo_conv_ode_max_error" in result.diagnostics

    def test_markov_test_passed(self, result):
        assert result.markov_test.markov_holds

    def test_cosmo_passed(self, result):
        assert result.cosmo_reduction.convolution_ode_equivalence

    def test_collapse_passed(self, result):
        assert result.collapse_reduction.force_balance_recovered

    def test_bianchi_passed(self, result):
        assert result.bianchi.cosmo_sector_verified


# ================================================================
# TestSerialization
# ================================================================

class TestSerialization:
    """Tests for dictionary serialization."""

    @pytest.fixture(scope="class")
    def result(self):
        return compute_route_c_stress_analysis()

    def test_serializes(self, result):
        d = stress_result_to_dict(result)
        assert isinstance(d, dict)

    def test_valid_field(self, result):
        d = stress_result_to_dict(result)
        assert d["valid"] is True

    def test_has_action(self, result):
        d = stress_result_to_dict(result)
        assert d["action"] is not None
        assert d["action"]["kernel_normalized"] is True

    def test_has_metric_variation(self, result):
        d = stress_result_to_dict(result)
        assert d["metric_variation"] is not None
        assert d["metric_variation"]["classification"] == "nonlocal_stress_functional"

    def test_has_stress_functional(self, result):
        d = stress_result_to_dict(result)
        assert d["stress_functional"] is not None
        assert d["stress_functional"]["classification"] == "functional_derived"

    def test_has_nonclaims(self, result):
        d = stress_result_to_dict(result)
        assert len(d["nonclaims"]) >= 10

    def test_has_diagnostics(self, result):
        d = stress_result_to_dict(result)
        assert "kernel_norm" in d["diagnostics"]

    def test_has_classification(self, result):
        d = stress_result_to_dict(result)
        assert d["classification"]["overall"] == "functional_derived"

    def test_phi_ontology(self, result):
        d = stress_result_to_dict(result)
        assert d["phi_ontology"] == "effective_local_representation"


# ================================================================
# TestEffectiveRhoPhi
# ================================================================

class TestEffectiveRhoPhi:
    """Tests for the effective memory energy density helper."""

    def test_zero_when_equilibrium(self):
        """rho_Phi = 0 when Phi = H^2_base."""
        rho = _effective_rho_phi(phi=1.0, H_base_sq=1.0, alpha=0.1)
        assert abs(rho) < 1e-30

    def test_positive_when_phi_greater(self):
        """rho_Phi > 0 when Phi > H^2_base."""
        rho = _effective_rho_phi(phi=1.5, H_base_sq=1.0, alpha=0.1)
        assert rho > 0

    def test_negative_when_phi_less(self):
        """rho_Phi < 0 when Phi < H^2_base (lagging memory)."""
        rho = _effective_rho_phi(phi=0.5, H_base_sq=1.0, alpha=0.1)
        assert rho < 0

    def test_scales_with_alpha(self):
        """rho_Phi scales linearly with alpha."""
        rho_01 = _effective_rho_phi(phi=2.0, H_base_sq=1.0, alpha=0.1)
        rho_02 = _effective_rho_phi(phi=2.0, H_base_sq=1.0, alpha=0.2)
        assert abs(rho_02 / rho_01 - 2.0) < 1e-10
