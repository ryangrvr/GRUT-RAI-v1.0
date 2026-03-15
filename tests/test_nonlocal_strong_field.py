"""Tests for grut.nonlocal_strong_field — Route C strong-field lapse correction.

Coverage:
- TestCompactnessPoint: single-point lapse analysis, both channels
- TestCompactnessScan: full sweep, regime boundaries, monotonicity
- TestEndpointAnalysis: self-healing proof, force balance, Schwarzschild lapse
- TestEndpointSensitivity: scenario scan, classifications, Q shifts
- TestProperTimeComparison: tau ratio formula, thresholds
- TestRingdownBoundedEstimate: bounded Q/echo shifts, framing
- TestLoveNumberImpact: underdetermined, no pseudo-k2
- TestForceBalanceImpact: equilibrium preserved, transient bounded
- TestMasterClassification: bounded, Phase III preserved, status-ladder
- TestSerialization: round-trip, all fields populated
"""

from __future__ import annotations

import math
import json
import pytest

from grut.nonlocal_strong_field import (
    # Data structures
    CompactnessPoint,
    CompactnessScan,
    EndpointAnalysis,
    EndpointSensitivity,
    ProperTimeComparison,
    RingdownBoundedEstimate,
    LoveNumberImpact,
    ForceBalanceImpact,
    MasterClassification,
    StrongFieldLapseResult,
    # Builder functions
    build_compactness_scan,
    build_endpoint_analysis,
    build_endpoint_sensitivity,
    build_proper_time_comparison,
    build_ringdown_bounded_estimate,
    build_love_number_impact,
    build_force_balance_impact,
    build_master_classification,
    # Master function
    compute_strong_field_lapse_analysis,
    # Serialization
    strong_field_lapse_result_to_dict,
    # Internal helpers (for direct testing)
    _psi_schwarzschild,
    _psi_effective_proxy,
    _first_order_correction,
    _classify_correction,
    _tau_ratio,
    _barrier_lapse_estimate,
    # Constants
    ALPHA_VAC,
    BETA_Q,
    EPSILON_Q,
    C_ENDPOINT,
    Q_CANON,
    OMEGA_0_TAU_CANON,
    THRESH_NEGLIGIBLE,
    THRESH_BOUNDED_PERTURBATIVE,
    THRESH_BOUNDED_EXTRAPOLATED,
    THRESH_SIGNIFICANT,
)


# ================================================================
# Fixtures
# ================================================================

@pytest.fixture(scope="module")
def scan():
    """Compactness scan for all tests."""
    return build_compactness_scan(C_min=0.05, C_max=3.0, n_points=30)


@pytest.fixture(scope="module")
def endpoint():
    """Endpoint analysis for all tests."""
    return build_endpoint_analysis()


@pytest.fixture(scope="module")
def sensitivity():
    """Endpoint sensitivity scan for all tests."""
    return build_endpoint_sensitivity()


@pytest.fixture(scope="module")
def master_result():
    """Full strong-field lapse analysis."""
    return compute_strong_field_lapse_analysis()


# ================================================================
# TestCompactnessPoint
# ================================================================

class TestCompactnessPoint:
    """Single-point lapse analysis, both channels."""

    def test_psi_schwarzschild_formula(self):
        """Psi_Schw = C / 2."""
        for C in [0.1, 0.5, 1.0, 2.0, 3.0]:
            assert abs(_psi_schwarzschild(C) - C / 2.0) < 1e-15

    def test_psi_effective_leq_psi_schw(self):
        """Psi_eff <= Psi_Schw for all C (barrier reduces effective lapse)."""
        for C in [0.1, 0.5, 1.0, 2.0, 3.0]:
            assert _psi_effective_proxy(C) <= _psi_schwarzschild(C) + 1e-15

    def test_psi_effective_agrees_weak_field(self):
        """Psi_eff ~ Psi_Schw for C << 1."""
        C = 0.01
        ratio = _psi_effective_proxy(C) / _psi_schwarzschild(C)
        assert abs(ratio - 1.0) < 0.02  # within 2% at C = 0.01

    def test_psi_effective_bounded_at_endpoint(self):
        """Psi_eff at C = 3 is bounded and less than Psi_Schw = 3/2."""
        psi_eff = _psi_effective_proxy(C_ENDPOINT)
        assert psi_eff < _psi_schwarzschild(C_ENDPOINT)
        assert psi_eff > 0
        assert psi_eff < 1.0  # well below Psi_Schw = 1.5

    def test_first_order_correction(self):
        """delta_Phi / Phi = Psi / e."""
        for Psi in [0.01, 0.1, 0.5, 1.0]:
            assert abs(_first_order_correction(Psi) - Psi / math.e) < 1e-15

    def test_classification_negligible(self):
        assert _classify_correction(0.005) == "negligible"

    def test_classification_bounded_perturbative(self):
        assert _classify_correction(0.03) == "bounded_perturbative"

    def test_classification_bounded_extrapolated(self):
        assert _classify_correction(0.07) == "bounded_extrapolated"

    def test_classification_significant(self):
        assert _classify_correction(0.15) == "significant"

    def test_classification_breakdown(self):
        assert _classify_correction(0.25) == "perturbative_breakdown"

    def test_tau_ratio_formula(self):
        """tau_proper / tau_coord = 1 / (1 + Psi)."""
        for Psi in [0.01, 0.1, 0.5]:
            assert abs(_tau_ratio(Psi) - 1.0 / (1.0 + Psi)) < 1e-15

    def test_scan_point_both_channels(self, scan):
        """Every scan point has both Psi_Schw and Psi_eff populated."""
        for pt in scan.points:
            assert pt.Psi_Schw > 0
            assert pt.Psi_eff > 0
            assert pt.correction_Schw > 0
            assert pt.correction_eff > 0
            assert pt.classification_Schw != ""
            assert pt.classification_eff != ""


# ================================================================
# TestCompactnessScan
# ================================================================

class TestCompactnessScan:
    """Full compactness sweep."""

    def test_scan_length(self, scan):
        assert scan.n_points == 30
        assert len(scan.points) == 30
        assert len(scan.C_values) == 30

    def test_C_range(self, scan):
        assert abs(scan.C_min - 0.05) < 1e-10
        assert abs(scan.C_max - 3.0) < 1e-10
        assert scan.C_values[0] >= scan.C_min - 1e-10
        assert scan.C_values[-1] <= scan.C_max + 1e-10

    def test_monotonic_C(self, scan):
        for i in range(1, len(scan.C_values)):
            assert scan.C_values[i] > scan.C_values[i - 1]

    def test_monotonic_correction_Schw(self, scan):
        """Schwarzschild correction increases monotonically with C."""
        for i in range(1, len(scan.points)):
            assert scan.points[i].correction_Schw > scan.points[i - 1].correction_Schw

    def test_monotonic_correction_eff(self, scan):
        """Effective correction increases monotonically with C."""
        for i in range(1, len(scan.points)):
            assert scan.points[i].correction_eff > scan.points[i - 1].correction_eff

    def test_regime_boundaries_positive(self, scan):
        assert scan.C_at_negligible_boundary > 0
        assert scan.C_at_perturbative_boundary > scan.C_at_negligible_boundary
        assert scan.C_at_extrapolated_boundary > scan.C_at_perturbative_boundary
        assert scan.C_at_significant_boundary > scan.C_at_extrapolated_boundary

    def test_regime_counts_sum(self, scan):
        total = (scan.n_negligible + scan.n_bounded_perturbative
                 + scan.n_bounded_extrapolated + scan.n_significant
                 + scan.n_breakdown)
        assert total == scan.n_points

    def test_has_negligible_points(self, scan):
        """Low C points should be negligible."""
        assert scan.n_negligible >= 1

    def test_has_breakdown_points(self, scan):
        """High C points should be breakdown (Psi_Schw > 0.54)."""
        assert scan.n_breakdown >= 1

    def test_endpoint_in_range(self, scan):
        """C = 3 should be within or near the scan range."""
        assert scan.C_max >= C_ENDPOINT - 0.01

    def test_notes_populated(self, scan):
        assert len(scan.notes) >= 3

    def test_boundaries_are_model_dependent(self, scan):
        """Boundaries are computed from Schwarzschild reference."""
        # C_at_negligible_boundary ~ 2e * 0.01 ~ 0.054
        expected = 2.0 * math.e * THRESH_NEGLIGIBLE
        assert abs(scan.C_at_negligible_boundary - expected) < 1e-10

    def test_weak_field_point_negligible(self, scan):
        """First point (C ~ 0.05) should have negligible Schwarzschild classification."""
        assert scan.points[0].classification_Schw == "negligible"

    def test_strong_field_point_not_negligible(self, scan):
        """Last point (C ~ 3.0) should NOT be negligible."""
        assert scan.points[-1].classification_Schw != "negligible"


# ================================================================
# TestEndpointAnalysis
# ================================================================

class TestEndpointAnalysis:
    """Self-healing proof at the GRUT equilibrium endpoint."""

    def test_C_endpoint_is_3(self, endpoint):
        assert abs(endpoint.C_endpoint - 3.0) < 1e-10

    def test_R_eq_over_r_s_is_third(self, endpoint):
        assert abs(endpoint.R_eq_over_r_s - 1.0 / 3.0) < 1e-10

    def test_source_vanishes(self, endpoint):
        """Source term X - Phi = 0 at equilibrium (exact)."""
        assert endpoint.source_vanishes
        assert abs(endpoint.source_term_at_eq) < 1e-14

    def test_self_healing_verified(self, endpoint):
        assert endpoint.self_healing_verified

    def test_self_healing_mechanism_populated(self, endpoint):
        assert len(endpoint.self_healing_mechanism) > 100
        assert "M_drive" in endpoint.self_healing_mechanism
        assert "a_grav" in endpoint.self_healing_mechanism

    def test_force_balance_preserved(self, endpoint):
        assert endpoint.force_balance_preserved

    def test_endpoint_law_unaffected(self, endpoint):
        assert endpoint.endpoint_law_unaffected

    def test_endpoint_law_independent_of_Psi(self, endpoint):
        """Self-healing holds for ANY Psi value."""
        assert endpoint.endpoint_law_independence_of_Psi

    def test_A_Schwarzschild_at_Req(self, endpoint):
        """A_Schw = 1 - r_s/R_eq = 1 - 3 = -2."""
        assert abs(endpoint.A_Schw_at_Req - (-2.0)) < 1e-10

    def test_lapse_below_horizon(self, endpoint):
        """Schwarzschild lapse at R_eq is below horizon."""
        assert endpoint.lapse_below_horizon

    def test_Psi_Schw_at_endpoint(self, endpoint):
        """Psi_Schw = C/2 = 3/2 = 1.5."""
        assert abs(endpoint.Psi_Schw_at_endpoint - 1.5) < 1e-10

    def test_Psi_eff_positive(self, endpoint):
        assert endpoint.Psi_eff_nominal > 0

    def test_Psi_eff_bounded(self, endpoint):
        """Effective Psi at endpoint is less than Schwarzschild value."""
        assert endpoint.Psi_eff_nominal < endpoint.Psi_Schw_at_endpoint

    def test_Psi_eff_proxy_type(self, endpoint):
        """Proxy type is explicitly labeled as heuristic."""
        assert "heuristic" in endpoint.Psi_eff_proxy_type

    def test_transient_peaks_during_approach(self, endpoint):
        assert endpoint.transient_correction_peaks_during_approach

    def test_transient_bound_positive(self, endpoint):
        assert endpoint.transient_correction_bound_eff > 0

    def test_notes_populated(self, endpoint):
        assert len(endpoint.notes) >= 5

    def test_nonclaims_populated(self, endpoint):
        assert len(endpoint.nonclaims) >= 5


# ================================================================
# TestEndpointSensitivity
# ================================================================

class TestEndpointSensitivity:
    """Scenario scan around endpoint effective lapse."""

    def test_three_scenarios(self, sensitivity):
        assert sensitivity.Psi_eff_low > 0
        assert sensitivity.Psi_eff_nominal > sensitivity.Psi_eff_low
        assert sensitivity.Psi_eff_high > sensitivity.Psi_eff_nominal

    def test_low_is_half_nominal(self, sensitivity):
        assert abs(sensitivity.Psi_eff_low - sensitivity.Psi_eff_nominal / 2.0) < 1e-15

    def test_high_is_double_nominal(self, sensitivity):
        assert abs(sensitivity.Psi_eff_high - 2.0 * sensitivity.Psi_eff_nominal) < 1e-15

    def test_corrections_ordered(self, sensitivity):
        assert sensitivity.correction_low < sensitivity.correction_nominal
        assert sensitivity.correction_nominal < sensitivity.correction_high

    def test_corrections_are_psi_over_e(self, sensitivity):
        assert abs(sensitivity.correction_nominal - sensitivity.Psi_eff_nominal / math.e) < 1e-15

    def test_classifications_populated(self, sensitivity):
        assert sensitivity.classification_low != ""
        assert sensitivity.classification_nominal != ""
        assert sensitivity.classification_high != ""

    def test_Q_shifts_ordered(self, sensitivity):
        assert sensitivity.Q_shift_low_pct < sensitivity.Q_shift_nominal_pct
        assert sensitivity.Q_shift_nominal_pct < sensitivity.Q_shift_high_pct

    def test_omega_0_tau_ordered(self, sensitivity):
        """Higher Psi -> lower omega_0_tau."""
        assert sensitivity.omega_0_tau_low > sensitivity.omega_0_tau_nominal
        assert sensitivity.omega_0_tau_nominal > sensitivity.omega_0_tau_high

    def test_omega_0_tau_nominal_formula(self, sensitivity):
        expected = 1.0 / (1.0 + sensitivity.Psi_eff_nominal)
        assert abs(sensitivity.omega_0_tau_nominal - expected) < 1e-15

    def test_notes_mention_scenario_scan(self, sensitivity):
        assert any("SCENARIO" in n.upper() or "scenario" in n.lower()
                    for n in sensitivity.notes)


# ================================================================
# TestProperTimeComparison
# ================================================================

class TestProperTimeComparison:
    """Proper-time vs coordinate-time tau comparison."""

    def test_tau_ratio_at_weak_field(self, master_result):
        pt = master_result.proper_time
        # First point (lowest C) should have ratio near 1
        assert pt.tau_ratio_Schw[0] > 0.95

    def test_tau_ratio_at_strong_field(self, master_result):
        pt = master_result.proper_time
        # Last point (highest C, C=3) should have ratio much less than 1
        assert pt.tau_ratio_Schw[-1] < 0.5

    def test_tau_ratio_formula_Schw(self, master_result):
        pt = master_result.proper_time
        for i, C in enumerate(pt.C_values):
            expected = 1.0 / (1.0 + C / 2.0)
            assert abs(pt.tau_ratio_Schw[i] - expected) < 1e-12

    def test_tau_ratio_formula_eff(self, master_result):
        pt = master_result.proper_time
        for i, C in enumerate(pt.C_values):
            psi_eff = _psi_effective_proxy(C)
            expected = 1.0 / (1.0 + psi_eff)
            assert abs(pt.tau_ratio_eff[i] - expected) < 1e-12

    def test_thresholds_positive(self, master_result):
        pt = master_result.proper_time
        assert pt.C_at_1pct_shift_Schw > 0
        assert pt.C_at_5pct_shift_Schw > pt.C_at_1pct_shift_Schw
        assert pt.C_at_10pct_shift_Schw > pt.C_at_5pct_shift_Schw

    def test_1pct_threshold_reasonable(self, master_result):
        """C for 1% tau shift should be ~ 0.02."""
        pt = master_result.proper_time
        assert 0.01 < pt.C_at_1pct_shift_Schw < 0.05

    def test_notes_populated(self, master_result):
        assert len(master_result.proper_time.notes) >= 3


# ================================================================
# TestRingdownBoundedEstimate
# ================================================================

class TestRingdownBoundedEstimate:
    """Bounded ringdown/echo estimates."""

    def test_framing_is_bounded_estimate(self, master_result):
        assert master_result.ringdown.framing == "bounded_estimate"

    def test_Q_canon(self, master_result):
        assert abs(master_result.ringdown.Q_canon - Q_CANON) < 1e-10

    def test_omega_0_tau_canon(self, master_result):
        assert abs(master_result.ringdown.omega_0_tau_canon - OMEGA_0_TAU_CANON) < 1e-10

    def test_Q_shift_positive(self, master_result):
        """Lapse increases effective Q (bounded estimate)."""
        assert master_result.ringdown.Q_shift_bounded_pct > 0

    def test_Q_shift_bounded(self, master_result):
        """Q shift should be moderate, not enormous."""
        assert master_result.ringdown.Q_shift_bounded_pct < 100.0

    def test_omega_0_tau_shift_negative(self, master_result):
        """Lapse decreases omega_0*tau (bounded estimate)."""
        assert master_result.ringdown.omega_0_tau_shift_bounded < 0

    def test_omega_0_tau_at_eq_less_than_1(self, master_result):
        assert master_result.ringdown.omega_0_tau_at_eq_bounded < 1.0

    def test_echo_correction_bounded(self, master_result):
        """Echo correction should be a small fraction of canon echo."""
        assert master_result.ringdown.echo_correction_bounded_pct > 0
        assert master_result.ringdown.echo_correction_bounded_pct < 5.0

    def test_sensitivity_range(self, master_result):
        rb = master_result.ringdown
        assert rb.Q_shift_low_pct < rb.Q_shift_bounded_pct
        assert rb.Q_shift_high_pct > rb.Q_shift_bounded_pct

    def test_echo_channel_status_populated(self, master_result):
        assert master_result.ringdown.echo_channel_status != ""

    def test_nonclaims_mention_bounded(self, master_result):
        assert any("bounded" in nc.lower() or "BOUNDED" in nc
                    for nc in master_result.ringdown.nonclaims)

    def test_nonclaims_count(self, master_result):
        assert len(master_result.ringdown.nonclaims) >= 3


# ================================================================
# TestLoveNumberImpact
# ================================================================

class TestLoveNumberImpact:
    """Love number bound — no pseudo-k2."""

    def test_not_computed(self, master_result):
        assert master_result.love.love_number_computed is False

    def test_no_value_available(self, master_result):
        assert master_result.love.love_number_value_available is False

    def test_rigidity_shift_positive(self, master_result):
        assert master_result.love.rigidity_shift_scale > 0

    def test_impact_classification_populated(self, master_result):
        assert master_result.love.impact_classification != ""

    def test_requirements_populated(self, master_result):
        assert len(master_result.love.requirements) >= 3

    def test_requirements_mention_covariant(self, master_result):
        reqs = " ".join(master_result.love.requirements)
        assert "covariant" in reqs.lower() or "Covariant" in reqs

    def test_nonclaims_no_k2(self, master_result):
        """Nonclaims should explicitly state no k2 is returned."""
        ncs = " ".join(master_result.love.nonclaims)
        assert "k_2" in ncs or "Love number value" in ncs

    def test_nonclaims_count(self, master_result):
        assert len(master_result.love.nonclaims) >= 3


# ================================================================
# TestForceBalanceImpact
# ================================================================

class TestForceBalanceImpact:
    """Force balance and boundary impact."""

    def test_force_balance_preserved(self, master_result):
        assert master_result.force_balance.force_balance_at_eq_preserved

    def test_delta_force_zero(self, master_result):
        assert abs(master_result.force_balance.delta_force_at_eq) < 1e-14

    def test_transient_correction_positive(self, master_result):
        assert master_result.force_balance.max_transient_correction_over_a_grav > 0

    def test_transient_correction_bounded(self, master_result):
        """Transient correction should be less than 50%."""
        assert master_result.force_balance.max_transient_correction_over_a_grav < 0.5

    def test_junction_bounded(self, master_result):
        assert master_result.force_balance.junction_correction_bounded

    def test_junction_scaling_mentions_Psi(self, master_result):
        assert "Psi" in master_result.force_balance.junction_correction_scaling

    def test_junction_approx_level(self, master_result):
        assert "effective" in master_result.force_balance.junction_approx_level

    def test_nonclaims_populated(self, master_result):
        assert len(master_result.force_balance.nonclaims) >= 3


# ================================================================
# TestMasterClassification
# ================================================================

class TestMasterClassification:
    """Master classification and status-ladder impact."""

    def test_classification_bounded(self, master_result):
        assert master_result.master.classification == "bounded"

    def test_not_canon_changing(self, master_result):
        assert master_result.master.classification != "canon_changing"

    def test_endpoint_unaffected(self, master_result):
        assert master_result.master.endpoint_unaffected

    def test_structural_identity_unaffected(self, master_result):
        assert master_result.master.structural_identity_unaffected

    def test_force_balance_preserved(self, master_result):
        assert master_result.master.force_balance_preserved

    def test_self_healing_verified(self, master_result):
        assert master_result.master.self_healing_verified

    def test_phase_iii_preserved(self, master_result):
        assert master_result.master.phase_iii_preserved

    def test_status_ladder_impact_populated(self, master_result):
        sli = master_result.master.status_ladder_impact
        assert len(sli) > 100
        assert "PRESERVED" in sli or "preserved" in sli.lower()

    def test_status_ladder_not_modified(self, master_result):
        assert master_result.diagnostics["status_ladder_modified"] is False

    def test_regime_cosmology_negligible(self, master_result):
        assert master_result.master.regime_cosmology == "negligible"

    def test_regime_endpoint_self_healing(self, master_result):
        assert "self_healing" in master_result.master.regime_endpoint

    def test_regime_near_horizon_not_negligible(self, master_result):
        assert master_result.master.regime_near_horizon != "negligible"

    def test_notes_populated(self, master_result):
        assert len(master_result.master.notes) >= 3

    def test_nonclaims_populated(self, master_result):
        assert len(master_result.master.nonclaims) >= 3

    def test_nonclaims_mention_model_dependent(self, master_result):
        ncs = " ".join(master_result.master.nonclaims)
        assert "model-dependent" in ncs.lower() or "model dependent" in ncs.lower()


# ================================================================
# TestMasterResult
# ================================================================

class TestMasterResult:
    """Full strong-field lapse analysis result."""

    def test_valid(self, master_result):
        assert master_result.valid

    def test_all_components_present(self, master_result):
        assert master_result.scan is not None
        assert master_result.endpoint is not None
        assert master_result.sensitivity is not None
        assert master_result.proper_time is not None
        assert master_result.ringdown is not None
        assert master_result.love is not None
        assert master_result.force_balance is not None
        assert master_result.master is not None

    def test_nonclaims_count(self, master_result):
        assert len(master_result.nonclaims) >= 15

    def test_nonclaims_mention_heuristic(self, master_result):
        ncs = " ".join(master_result.nonclaims)
        assert "heuristic" in ncs.lower()

    def test_nonclaims_mention_bounded(self, master_result):
        ncs = " ".join(master_result.nonclaims)
        assert "bounded" in ncs.lower()

    def test_nonclaims_mention_self_healing(self, master_result):
        ncs = " ".join(master_result.nonclaims)
        assert "self-healing" in ncs.lower() or "self_healing" in ncs.lower()

    def test_nonclaims_mention_love(self, master_result):
        ncs = " ".join(master_result.nonclaims)
        assert "love" in ncs.lower() or "Love" in ncs

    def test_nonclaims_mention_observer(self, master_result):
        ncs = " ".join(master_result.nonclaims)
        assert "observer" in ncs.lower()

    def test_nonclaims_mention_quantization(self, master_result):
        ncs = " ".join(master_result.nonclaims)
        assert "quantization" in ncs.lower() or "Quantization" in ncs

    def test_approx_status_populated(self, master_result):
        assert len(master_result.approx_status) > 50

    def test_remaining_obstruction_populated(self, master_result):
        assert len(master_result.remaining_obstruction) > 100

    def test_diagnostics_populated(self, master_result):
        d = master_result.diagnostics
        assert len(d) >= 10
        assert "self_healing" in d
        assert d["self_healing"] is True
        assert "master_classification" in d
        assert d["master_classification"] == "bounded"
        assert "phase_iii_preserved" in d
        assert d["phase_iii_preserved"] is True

    def test_diagnostics_scan_counts(self, master_result):
        d = master_result.diagnostics
        total = (d["n_negligible"] + d["n_bounded_perturbative"]
                 + d["n_bounded_extrapolated"] + d["n_significant"]
                 + d["n_breakdown"])
        assert total == d["n_scan_points"]

    def test_diagnostics_psi_band(self, master_result):
        band = master_result.diagnostics["Psi_eff_band"]
        assert len(band) == 3
        assert band[0] < band[1] < band[2]


# ================================================================
# TestSerialization
# ================================================================

class TestSerialization:
    """Round-trip serialization."""

    def test_serializes_to_dict(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert isinstance(d, dict)

    def test_serialized_valid(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert d["valid"] is True

    def test_serialized_has_scan(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert "scan" in d
        assert d["scan"]["n_points"] == 30

    def test_serialized_has_endpoint(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert "endpoint" in d
        assert d["endpoint"]["self_healing_verified"] is True

    def test_serialized_has_sensitivity(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert "sensitivity" in d
        assert d["sensitivity"]["Psi_eff_nominal"] > 0

    def test_serialized_has_ringdown(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert "ringdown" in d
        assert d["ringdown"]["framing"] == "bounded_estimate"

    def test_serialized_has_love(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert "love" in d
        assert d["love"]["love_number_computed"] is False

    def test_serialized_has_master(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert "master" in d
        assert d["master"]["classification"] == "bounded"

    def test_serialized_nonclaims(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert len(d["nonclaims"]) >= 15

    def test_serialized_diagnostics(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert "diagnostics" in d
        assert d["diagnostics"]["master_classification"] == "bounded"

    def test_json_roundtrip(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        s = json.dumps(d)
        d2 = json.loads(s)
        assert d2["valid"] is True
        assert d2["master"]["classification"] == "bounded"
        assert d2["endpoint"]["self_healing_verified"] is True

    def test_serialized_status_ladder(self, master_result):
        d = strong_field_lapse_result_to_dict(master_result)
        assert len(d["master"]["status_ladder_impact"]) > 50
