"""Tests for grut.nonlocal_metric_variation — Route C perturbative metric variation.

Coverage:
- TestFRWBackground: background construction, analytical forms, ODE consistency
- TestKernelTools: retarded kernel, tau derivative, proper-time kernel, causality
- TestSourcePerturbation: convolution-ODE commutation (Markov property)
- TestTauPerturbation: three-way (conv, ODE, analytical) commutation
- TestLapsePerturbation: coordinate mismatch, proper-time commutation, analytical
- TestLapseMagnitude: cosmological vs collapse estimates
- TestCommutationSummary: overall assessment, nonclaims
- TestUpgradeAssessment: status upgrade conditions
- TestMasterAnalysis: all components, diagnostics, nonclaims
- TestSerialization: round-trip, all fields populated
"""

from __future__ import annotations

import math
import json
import pytest

from grut.nonlocal_metric_variation import (
    FRWPerturbativeBackground,
    SourcePerturbationTest,
    TauPerturbationTest,
    LapsePerturbationTest,
    LapseMagnitudeEstimate,
    CommutationSummary,
    RouteCUpgradeAssessment,
    RouteCMetricVariationResult,
    build_frw_perturbative_background,
    estimate_lapse_magnitude,
    build_commutation_summary,
    build_upgrade_assessment,
    compute_route_c_metric_variation_analysis,
    metric_variation_result_to_dict,
    _retarded_kernel,
    _retarded_kernel_tau_derivative,
    _proper_time_kernel,
    _convolution_with_kernel,
    _integrate_memory_ode,
    _integrate_perturbed_ode_tau,
    _integrate_lapse_corrected_ode,
    _analytical_lapse_correction,
)

# Import test_ functions with underscore aliases to prevent pytest from
# collecting them as module-level tests (they return dataclass results).
from grut.nonlocal_metric_variation import (
    test_source_perturbation_commutation as _test_source_perturbation,
    test_tau_perturbation_commutation as _test_tau_perturbation,
    test_lapse_perturbation_commutation as _test_lapse_perturbation,
)


# ================================================================
# Fixtures
# ================================================================

@pytest.fixture(scope="module")
def bg():
    """Background FRW solution for all perturbation tests."""
    return build_frw_perturbative_background(
        tau_eff=1.0, X_0=1.0, n_steps=2000, n_tau=10.0
    )


@pytest.fixture(scope="module")
def master_result():
    """Full Route C metric variation analysis result."""
    return compute_route_c_metric_variation_analysis(
        tau_eff=1.0, X_0=1.0, n_steps=2000, n_tau=10.0,
        Psi_lapse=0.01, delta_tau_fraction=0.01,
    )


# ================================================================
# TestFRWBackground
# ================================================================

class TestFRWBackground:
    """Tests for the FRW perturbative background construction."""

    def test_background_parameters(self, bg):
        assert bg.tau_eff == 1.0
        assert bg.X_0 == 1.0
        assert bg.n_steps == 2000
        assert bg.n_tau == 10.0

    def test_time_grid(self, bg):
        assert len(bg.times) == 2001
        assert bg.times[0] == 0.0
        assert abs(bg.times[-1] - 10.0) < 1e-10

    def test_dt_correct(self, bg):
        expected_dt = 10.0 / 2000
        assert abs(bg.dt - expected_dt) < 1e-14

    def test_phi_0_initial_condition(self, bg):
        """Phi_0(0) = 0 for constant source starting from rest."""
        assert abs(bg.Phi_0[0]) < 1e-14

    def test_phi_0_asymptotic(self, bg):
        """Phi_0(t >> tau) -> X_0."""
        assert abs(bg.Phi_0[-1] - 1.0) < 1e-4

    def test_dphi_0_dt_initial(self, bg):
        """dPhi_0/dt(0) = X_0/tau_0."""
        assert abs(bg.dPhi_0_dt[0] - 1.0) < 1e-14

    def test_dphi_0_dt_asymptotic(self, bg):
        """dPhi_0/dt(t >> tau) -> 0."""
        assert abs(bg.dPhi_0_dt[-1]) < 1e-4

    def test_phi_0_analytical(self, bg):
        """Phi_0(t) = X_0 * (1 - exp(-t/tau))."""
        for idx in [0, 100, 500, 1000, 2000]:
            t = bg.times[idx]
            expected = 1.0 * (1.0 - math.exp(-t / 1.0))
            assert abs(bg.Phi_0[idx] - expected) < 1e-12, f"Failed at idx={idx}"

    def test_dphi_0_dt_analytical(self, bg):
        """dPhi_0/dt = (X_0/tau) * exp(-t/tau)."""
        for idx in [0, 100, 500, 1000]:
            t = bg.times[idx]
            expected = 1.0 * math.exp(-t / 1.0)
            assert abs(bg.dPhi_0_dt[idx] - expected) < 1e-12

    def test_analytical_forms_populated(self, bg):
        assert "exp" in bg.phi_0_form
        assert "exp" in bg.dphi_0_dt_form

    def test_notes_populated(self, bg):
        assert len(bg.notes) >= 3

    def test_different_tau(self):
        """Background works for different tau values."""
        for tau in [0.5, 2.0, 5.0]:
            bg2 = build_frw_perturbative_background(tau_eff=tau, X_0=2.0)
            assert bg2.tau_eff == tau
            assert bg2.X_0 == 2.0
            assert abs(bg2.Phi_0[-1] - 2.0) < 0.01

    def test_different_X0(self):
        """Background scales linearly with X_0."""
        bg_a = build_frw_perturbative_background(X_0=1.0)
        bg_b = build_frw_perturbative_background(X_0=3.0)
        for idx in [500, 1000, 1500]:
            assert abs(bg_b.Phi_0[idx] - 3.0 * bg_a.Phi_0[idx]) < 1e-10


# ================================================================
# TestKernelTools
# ================================================================

class TestKernelTools:
    """Tests for the kernel numerical tools."""

    def test_retarded_kernel_causal(self):
        for s in [-10.0, -1.0, -0.001]:
            assert _retarded_kernel(s, 1.0) == 0.0

    def test_retarded_kernel_peak(self):
        """K(0) = 1/tau."""
        assert abs(_retarded_kernel(0.0, 2.0) - 0.5) < 1e-14

    def test_retarded_kernel_decay(self):
        """K(s) decreases for s > 0."""
        k_prev = _retarded_kernel(0.0, 1.0)
        for s in [0.1, 0.5, 1.0, 2.0, 5.0]:
            k_curr = _retarded_kernel(s, 1.0)
            assert k_curr < k_prev
            k_prev = k_curr

    def test_tau_derivative_causal(self):
        for s in [-1.0, -0.1]:
            assert _retarded_kernel_tau_derivative(s, 1.0) == 0.0

    def test_tau_derivative_sign_change(self):
        """dK/dtau changes sign at s = tau."""
        tau = 1.0
        assert _retarded_kernel_tau_derivative(0.5, tau) < 0  # s < tau
        assert _retarded_kernel_tau_derivative(2.0, tau) > 0  # s > tau

    def test_tau_derivative_zero_at_tau(self):
        """dK/dtau = 0 at s = tau."""
        assert abs(_retarded_kernel_tau_derivative(1.0, 1.0)) < 1e-14

    def test_proper_time_kernel_causal(self):
        for s in [-1.0, -0.01]:
            assert _proper_time_kernel(s, 1.0, 0.01) == 0.0

    def test_proper_time_kernel_reduces_to_standard(self):
        """At Psi=0, proper-time kernel = standard kernel."""
        for s in [0.0, 0.5, 1.0, 3.0]:
            k_std = _retarded_kernel(s, 1.0)
            k_proper = _proper_time_kernel(s, 1.0, 0.0)
            assert abs(k_proper - k_std) < 1e-14

    def test_proper_time_kernel_effective_tau(self):
        """K_proper with Psi is like K with tau_eff = tau/(1+Psi)."""
        Psi = 0.1
        tau = 2.0
        tau_eff = tau / (1.0 + Psi)
        for s in [0.0, 0.5, 1.0, 3.0]:
            k_proper = _proper_time_kernel(s, tau, Psi)
            k_eff = _retarded_kernel(s, tau_eff)
            assert abs(k_proper - k_eff) < 1e-12


# ================================================================
# TestSourcePerturbation
# ================================================================

class TestSourcePerturbation:
    """Tests for source perturbation commutation (Markov property)."""

    def test_source_commutes(self, bg):
        st = _test_source_perturbation(bg, delta_X_amplitude=0.1)
        assert st.commutes, f"Source should commute: max_rel={st.max_relative_mismatch}"

    def test_source_max_rel_small(self, bg):
        st = _test_source_perturbation(bg, delta_X_amplitude=0.1)
        assert st.max_relative_mismatch < 0.05

    def test_source_max_abs_small(self, bg):
        st = _test_source_perturbation(bg, delta_X_amplitude=0.1)
        assert st.max_absolute_mismatch < 0.01

    def test_source_form_populated(self, bg):
        st = _test_source_perturbation(bg, delta_X_amplitude=0.1)
        assert "sin" in st.delta_X_form

    def test_source_amplitude_recorded(self, bg):
        st = _test_source_perturbation(bg, delta_X_amplitude=0.2)
        assert st.delta_X_amplitude == 0.2

    def test_source_arrays_populated(self, bg):
        st = _test_source_perturbation(bg, delta_X_amplitude=0.1)
        assert len(st.delta_phi_convolution) == 2001
        assert len(st.delta_phi_ode) == 2001

    def test_source_initial_condition(self, bg):
        st = _test_source_perturbation(bg, delta_X_amplitude=0.1)
        assert st.delta_phi_convolution[0] == 0.0
        assert st.delta_phi_ode[0] == 0.0

    def test_source_notes_populated(self, bg):
        st = _test_source_perturbation(bg, delta_X_amplitude=0.1)
        assert len(st.notes) >= 4

    def test_source_different_amplitude(self, bg):
        """Commutation holds for different source amplitudes."""
        for amp in [0.01, 0.1, 0.5]:
            st = _test_source_perturbation(bg, delta_X_amplitude=amp)
            assert st.commutes, f"Failed for amplitude={amp}"


# ================================================================
# TestTauPerturbation
# ================================================================

class TestTauPerturbation:
    """Tests for kernel (tau) perturbation commutation."""

    def test_tau_conv_ode_commutes(self, bg):
        tt = _test_tau_perturbation(bg, delta_tau_fraction=0.01)
        assert tt.conv_ode_commutes

    def test_tau_ode_analytical_commutes(self, bg):
        tt = _test_tau_perturbation(bg, delta_tau_fraction=0.01)
        assert tt.ode_analytical_commutes

    def test_tau_conv_analytical_commutes(self, bg):
        tt = _test_tau_perturbation(bg, delta_tau_fraction=0.01)
        assert tt.conv_analytical_commutes

    def test_tau_delta_recorded(self, bg):
        tt = _test_tau_perturbation(bg, delta_tau_fraction=0.05)
        assert abs(tt.delta_tau - 0.05) < 1e-14

    def test_tau_analytical_form_populated(self, bg):
        tt = _test_tau_perturbation(bg, delta_tau_fraction=0.01)
        assert "delta_tau" in tt.delta_phi_analytical_form
        assert "exp" in tt.delta_phi_analytical_form

    def test_tau_analytical_initial_zero(self, bg):
        tt = _test_tau_perturbation(bg, delta_tau_fraction=0.01)
        assert tt.delta_phi_analytical[0] == 0.0

    def test_tau_analytical_peak_at_tau(self, bg):
        """Analytical delta_Phi peaks near t = tau_0."""
        tt = _test_tau_perturbation(bg, delta_tau_fraction=0.01)
        peak_idx = max(range(len(tt.delta_phi_analytical)),
                       key=lambda i: abs(tt.delta_phi_analytical[i]))
        t_peak = bg.times[peak_idx]
        assert abs(t_peak - 1.0) < 0.1, f"Peak at t={t_peak}, expected ~1.0"

    def test_tau_arrays_populated(self, bg):
        tt = _test_tau_perturbation(bg, delta_tau_fraction=0.01)
        assert len(tt.delta_phi_convolution) == 2001
        assert len(tt.delta_phi_ode) == 2001
        assert len(tt.delta_phi_analytical) == 2001

    def test_tau_different_fractions(self, bg):
        """Commutation holds for different tau perturbation sizes."""
        for frac in [0.001, 0.01, 0.05]:
            tt = _test_tau_perturbation(bg, delta_tau_fraction=frac)
            assert tt.conv_ode_commutes, f"Failed for frac={frac}"

    def test_tau_notes_populated(self, bg):
        tt = _test_tau_perturbation(bg, delta_tau_fraction=0.01)
        assert len(tt.notes) >= 4


# ================================================================
# TestLapsePerturbation
# ================================================================

class TestLapsePerturbation:
    """Tests for lapse perturbation commutation (the KEY test)."""

    def test_lapse_coordinate_does_not_commute(self, bg):
        """Coordinate-time ODE FAILS to commute with proper-time convolution."""
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        assert not lt.coordinate_commutes

    def test_lapse_proper_commutes(self, bg):
        """Proper-time ODE COMMUTES with proper-time convolution."""
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        assert lt.proper_commutes

    def test_lapse_analytical_verified(self, bg):
        """Analytical lapse correction matches numerical."""
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        assert lt.lapse_analytical_verified

    def test_lapse_coord_mismatch_large(self, bg):
        """Coordinate mismatch should be ~1.0 (100% relative)."""
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        assert lt.coord_vs_proper_relative_mismatch > 0.5

    def test_lapse_proper_mismatch_small(self, bg):
        """Proper-time mismatch should be < 5%."""
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        assert lt.proper_vs_proper_relative_mismatch < 0.05

    def test_lapse_peak_value(self, bg):
        """Peak lapse correction = Psi * X_0 / e."""
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        expected = 0.01 * 1.0 / math.e
        assert abs(lt.lapse_peak_value - expected) < 1e-14

    def test_lapse_peak_time(self, bg):
        """Peak occurs at t = tau_0."""
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        assert lt.lapse_peak_time_over_tau == 1.0

    def test_lapse_correction_form(self, bg):
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        assert "Psi" in lt.lapse_correction_form
        assert "exp" in lt.lapse_correction_form

    def test_lapse_psi_recorded(self, bg):
        lt = _test_lapse_perturbation(bg, Psi=0.05)
        assert lt.Psi == 0.05

    def test_lapse_coordinate_ode_is_zero(self, bg):
        """Coordinate-time ODE gives zero lapse correction (by construction)."""
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        assert all(v == 0.0 for v in lt.delta_phi_coordinate_ode)

    def test_lapse_arrays_populated(self, bg):
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        assert len(lt.delta_phi_proper_convolution) == 2001
        assert len(lt.delta_phi_proper_ode) == 2001
        assert len(lt.delta_phi_lapse_analytical) == 2001

    def test_lapse_different_psi_perturbative(self, bg):
        """Proper-time commutation holds for Psi in the perturbative regime."""
        for psi in [0.001, 0.01, 0.05]:
            lt = _test_lapse_perturbation(bg, Psi=psi)
            assert lt.proper_commutes, f"Failed for Psi={psi}"
            assert not lt.coordinate_commutes, f"Coord should not commute for Psi={psi}"

    def test_lapse_large_psi_breaks_perturbative(self, bg):
        """At Psi=0.1, O(Psi^2) corrections break first-order commutation."""
        lt = _test_lapse_perturbation(bg, Psi=0.1)
        # Coordinate-time still fails (physical)
        assert not lt.coordinate_commutes
        # Proper-time mismatch grows as O(Psi^2) — may exceed 5% threshold
        assert lt.proper_vs_proper_relative_mismatch > 0.05

    def test_lapse_notes_populated(self, bg):
        lt = _test_lapse_perturbation(bg, Psi=0.01)
        assert len(lt.notes) >= 7

    def test_analytical_lapse_solution_check(self):
        """Verify delta_Phi_lapse(t) = Psi*X*(t/tau)*exp(-t/tau) by substitution."""
        Psi, X_0, tau = 0.1, 2.0, 1.5
        times = [i * 0.01 for i in range(1001)]
        analytical = _analytical_lapse_correction(X_0, tau, Psi, times)
        # Verify ODE: tau*f' + f = Psi*X*exp(-t/tau)
        for i in range(10, 990):
            t = times[i]
            f = analytical[i]
            # Finite-difference derivative
            fp = (analytical[i + 1] - analytical[i - 1]) / (2 * 0.01)
            lhs = tau * fp + f
            rhs = Psi * X_0 * math.exp(-t / tau)
            assert abs(lhs - rhs) < 0.01 * abs(rhs) + 1e-10


# ================================================================
# TestLapseMagnitude
# ================================================================

class TestLapseMagnitude:
    """Tests for lapse magnitude estimates."""

    def test_cosmo_negligible(self):
        lm = estimate_lapse_magnitude()
        assert lm.cosmo_negligible

    def test_collapse_not_negligible(self):
        lm = estimate_lapse_magnitude()
        assert not lm.collapse_negligible

    def test_cosmo_psi(self):
        lm = estimate_lapse_magnitude()
        assert lm.Psi_cosmo == 1e-5

    def test_collapse_psi(self):
        lm = estimate_lapse_magnitude()
        assert abs(lm.Psi_collapse - 1.0 / 6.0) < 1e-10

    def test_collapse_r_over_rs(self):
        lm = estimate_lapse_magnitude()
        assert lm.R_over_r_s == 3.0

    def test_cosmo_correction_tiny(self):
        lm = estimate_lapse_magnitude()
        assert lm.delta_phi_over_phi_cosmo < 1e-4

    def test_collapse_correction_percent(self):
        lm = estimate_lapse_magnitude()
        assert 0.05 < lm.delta_phi_over_phi_collapse < 0.07  # ~6.1%

    def test_weak_field_safe(self):
        lm = estimate_lapse_magnitude()
        assert lm.weak_field_safe

    def test_strong_field_correction_needed(self):
        lm = estimate_lapse_magnitude()
        assert lm.strong_field_correction_needed

    def test_notes_populated(self):
        lm = estimate_lapse_magnitude()
        assert len(lm.notes) >= 4


# ================================================================
# TestCommutationSummary
# ================================================================

class TestCommutationSummary:
    """Tests for the overall commutation summary."""

    def test_source_commutes_flag(self, master_result):
        assert master_result.commutation.source_commutes

    def test_tau_commutes_flag(self, master_result):
        assert master_result.commutation.tau_commutes

    def test_lapse_coordinate_does_not_commute(self, master_result):
        assert not master_result.commutation.lapse_coordinate_commutes

    def test_lapse_proper_commutes(self, master_result):
        assert master_result.commutation.lapse_proper_commutes

    def test_overall_coordinate_commutes(self, master_result):
        """In coordinate time, source + tau suffice. Overall: commutes."""
        assert master_result.commutation.overall_coordinate_time_commutes

    def test_overall_proper_commutes(self, master_result):
        """In proper time, all three channels commute."""
        assert master_result.commutation.overall_proper_time_commutes

    def test_covariant_mismatch_source_populated(self, master_result):
        assert len(master_result.commutation.covariant_mismatch_source) > 50

    def test_covariant_mismatch_form_populated(self, master_result):
        assert "delta_Phi" in master_result.commutation.covariant_mismatch_form

    def test_covariant_mismatch_order(self, master_result):
        assert "Psi" in master_result.commutation.covariant_mismatch_order

    def test_perturbative_order_populated(self, master_result):
        assert "first_order" in master_result.commutation.perturbative_order

    def test_nonclaims_populated(self, master_result):
        assert len(master_result.commutation.nonclaims) >= 4

    def test_notes_populated(self, master_result):
        assert len(master_result.commutation.notes) >= 6


# ================================================================
# TestUpgradeAssessment
# ================================================================

class TestUpgradeAssessment:
    """Tests for the Route C upgrade assessment."""

    def test_upgraded(self, master_result):
        assert master_result.upgrade.upgraded

    def test_previous_status(self, master_result):
        assert master_result.upgrade.previous_status == "functional_derived"

    def test_current_status(self, master_result):
        assert master_result.upgrade.current_status == "perturbatively_verified__coordinate_time"

    def test_upgrade_reason_populated(self, master_result):
        assert len(master_result.upgrade.upgrade_reason) > 100

    def test_upgrade_scope_populated(self, master_result):
        assert "FRW" in master_result.upgrade.upgrade_scope

    def test_upgrade_limitations_count(self, master_result):
        assert len(master_result.upgrade.upgrade_limitations) >= 5

    def test_remaining_obstruction_populated(self, master_result):
        assert len(master_result.upgrade.remaining_obstruction) > 200

    def test_remaining_obstruction_mentions_lapse(self, master_result):
        assert "lapse" in master_result.upgrade.remaining_obstruction.lower()

    def test_remaining_obstruction_severity(self, master_result):
        assert "MILD" in master_result.upgrade.remaining_obstruction_severity

    def test_notes_populated(self, master_result):
        assert len(master_result.upgrade.notes) >= 4


# ================================================================
# TestMasterAnalysis
# ================================================================

class TestMasterAnalysis:
    """Tests for the master analysis result."""

    def test_valid(self, master_result):
        assert master_result.valid

    def test_all_components_present(self, master_result):
        assert master_result.background is not None
        assert master_result.source_test is not None
        assert master_result.tau_test is not None
        assert master_result.lapse_test is not None
        assert master_result.lapse_magnitude is not None
        assert master_result.commutation is not None
        assert master_result.upgrade is not None

    def test_source_test_passed(self, master_result):
        assert master_result.source_test.commutes

    def test_tau_test_passed(self, master_result):
        assert master_result.tau_test.conv_ode_commutes

    def test_lapse_test_coord_failed(self, master_result):
        assert not master_result.lapse_test.coordinate_commutes

    def test_lapse_test_proper_passed(self, master_result):
        assert master_result.lapse_test.proper_commutes

    def test_nonclaims_count(self, master_result):
        assert len(master_result.nonclaims) >= 12

    def test_nonclaims_mention_perturbative(self, master_result):
        combined = " ".join(master_result.nonclaims).lower()
        assert "perturbative" in combined or "first" in combined

    def test_nonclaims_mention_nonlinear(self, master_result):
        combined = " ".join(master_result.nonclaims).lower()
        assert "nonlinear" in combined

    def test_nonclaims_mention_observer(self, master_result):
        combined = " ".join(master_result.nonclaims).lower()
        assert "observer" in combined

    def test_nonclaims_mention_quantization(self, master_result):
        combined = " ".join(master_result.nonclaims).lower()
        assert "quantiz" in combined

    def test_remaining_obstruction_populated(self, master_result):
        assert len(master_result.remaining_obstruction) > 200

    def test_diagnostics_populated(self, master_result):
        d = master_result.diagnostics
        assert "source_max_rel_mismatch" in d
        assert "tau_conv_ode_mismatch" in d
        assert "lapse_coord_vs_proper_rel" in d
        assert "lapse_proper_ode_vs_conv_rel" in d
        assert "lapse_peak_value" in d

    def test_diagnostics_source_small(self, master_result):
        assert master_result.diagnostics["source_max_rel_mismatch"] < 0.05

    def test_diagnostics_tau_small(self, master_result):
        assert master_result.diagnostics["tau_conv_ode_mismatch"] < 0.05

    def test_diagnostics_lapse_coord_large(self, master_result):
        assert master_result.diagnostics["lapse_coord_vs_proper_rel"] > 0.5

    def test_diagnostics_lapse_proper_small(self, master_result):
        assert master_result.diagnostics["lapse_proper_ode_vs_conv_rel"] < 0.05


# ================================================================
# TestSerialization
# ================================================================

class TestSerialization:
    """Tests for serialization round-trip."""

    def test_serializes_to_dict(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert isinstance(d, dict)

    def test_serialized_valid(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert d["valid"] is True

    def test_serialized_has_background(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert d["background"] is not None
        assert d["background"]["tau_eff"] == 1.0

    def test_serialized_has_source_test(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert d["source_test"] is not None
        assert d["source_test"]["commutes"] is True

    def test_serialized_has_tau_test(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert d["tau_test"] is not None
        assert d["tau_test"]["conv_ode_commutes"] is True

    def test_serialized_has_lapse_test(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert d["lapse_test"] is not None
        assert d["lapse_test"]["coordinate_commutes"] is False
        assert d["lapse_test"]["proper_commutes"] is True

    def test_serialized_has_lapse_magnitude(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert d["lapse_magnitude"] is not None
        assert d["lapse_magnitude"]["cosmo_negligible"] is True

    def test_serialized_has_commutation(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert d["commutation"] is not None
        assert d["commutation"]["overall_coordinate_time_commutes"] is True

    def test_serialized_has_upgrade(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert d["upgrade"] is not None
        assert d["upgrade"]["upgraded"] is True

    def test_serialized_nonclaims(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert len(d["nonclaims"]) >= 12

    def test_serialized_diagnostics(self, master_result):
        d = metric_variation_result_to_dict(master_result)
        assert "source_max_rel_mismatch" in d["diagnostics"]

    def test_json_roundtrip(self, master_result):
        """Full JSON serialization and deserialization."""
        d = metric_variation_result_to_dict(master_result)
        json_str = json.dumps(d, default=str)
        d2 = json.loads(json_str)
        assert d2["valid"] is True
        assert d2["upgrade"]["upgraded"] is True
        assert len(d2["nonclaims"]) >= 12
