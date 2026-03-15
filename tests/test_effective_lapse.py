"""Tests for grut.effective_lapse — Effective Lapse Derivation at GRUT Endpoint.

Targeted tests for the constitutive-derived lapse proxy, three derivation
routes, three-level hierarchy, self-healing independence, and sensitivity band.
"""

from __future__ import annotations

import json
import math

import pytest

from grut.effective_lapse import (
    compute_effective_lapse_analysis,
    effective_lapse_result_to_dict,
    build_barrier_gravity_ratio,
    build_route_a,
    build_route_b,
    build_route_c,
    build_route_comparison,
    build_sensitivity_band,
    build_three_level_summary,
    build_self_healing_check,
    build_shift_estimates,
    scan_beta_Q,
    _barrier_potential_ratio,
    _effective_metric_at_endpoint,
    _psi_from_route_a,
    _psi_from_route_b,
    _psi_from_route_c,
    ALPHA_VAC,
    BETA_Q,
    EPSILON_Q,
    C_ENDPOINT,
    Q_CANON,
    OMEGA_0_TAU_CANON,
    LEVEL_EXACT,
    LEVEL_CONSTITUTIVE_DERIVED,
    LEVEL_ANSATZ_DEPENDENT,
    LEVEL_UPPER_BOUND_ONLY,
    LEVEL_UNRESOLVED,
)


# ================================================================
# Module-scoped fixtures
# ================================================================

@pytest.fixture(scope="module")
def barrier_ratio():
    """Barrier-to-gravity potential ratio at endpoint."""
    return build_barrier_gravity_ratio()


@pytest.fixture(scope="module")
def route_a():
    """Route A: barrier-gravity ratio lapse proxy."""
    return build_route_a()


@pytest.fixture(scope="module")
def route_b():
    """Route B: effective metric at endpoint."""
    return build_route_b()


@pytest.fixture(scope="module")
def route_c():
    """Route C: Schwarzschild reference."""
    return build_route_c()


@pytest.fixture(scope="module")
def routes():
    """Route comparison."""
    return build_route_comparison(build_route_a(), build_route_b(), build_route_c())


@pytest.fixture(scope="module")
def sensitivity_band():
    """Sensitivity band around constitutive-derived proxy."""
    return build_sensitivity_band()


@pytest.fixture(scope="module")
def three_levels():
    """Three-level hierarchy summary."""
    return build_three_level_summary()


@pytest.fixture(scope="module")
def self_healing():
    """Self-healing check."""
    return build_self_healing_check()


@pytest.fixture(scope="module")
def shift_estimates():
    """Shift estimates."""
    return build_shift_estimates()


@pytest.fixture(scope="module")
def master_result():
    """Full effective lapse analysis."""
    return compute_effective_lapse_analysis()


# ================================================================
# TestBarrierGravityRatio
# ================================================================

class TestBarrierGravityRatio:
    """Tests for the central algebraic result: 1/(1+beta_Q)."""

    def test_ratio_one_third_canon(self, barrier_ratio):
        assert abs(barrier_ratio.ratio - 1.0 / 3.0) < 1e-15

    def test_ratio_formula_general_beta_1(self):
        bgr = build_barrier_gravity_ratio(beta_Q=1.0, epsilon_Q=ALPHA_VAC)
        assert abs(bgr.ratio - 0.5) < 1e-15

    def test_ratio_formula_general_beta_3(self):
        bgr = build_barrier_gravity_ratio(beta_Q=3.0, epsilon_Q=ALPHA_VAC ** 3)
        assert abs(bgr.ratio - 0.25) < 1e-15

    def test_ratio_formula_general_beta_4(self):
        bgr = build_barrier_gravity_ratio(beta_Q=4.0, epsilon_Q=ALPHA_VAC ** 4)
        assert abs(bgr.ratio - 0.2) < 1e-15

    def test_independent_of_epsilon_Q(self):
        r1 = build_barrier_gravity_ratio(beta_Q=2.0, epsilon_Q=1.0 / 9.0)
        r2 = build_barrier_gravity_ratio(beta_Q=2.0, epsilon_Q=1.0 / 4.0)
        r3 = build_barrier_gravity_ratio(beta_Q=2.0, epsilon_Q=1.0 / 16.0)
        assert abs(r1.ratio - r2.ratio) < 1e-15
        assert abs(r1.ratio - r3.ratio) < 1e-15

    def test_depends_on_epsilon_Q_false(self, barrier_ratio):
        assert barrier_ratio.depends_on_epsilon_Q is False

    def test_depends_on_alpha_vac_false(self, barrier_ratio):
        assert barrier_ratio.depends_on_alpha_vac is False

    def test_depends_on_mass_false(self, barrier_ratio):
        assert barrier_ratio.depends_on_mass is False

    def test_is_exact(self, barrier_ratio):
        assert barrier_ratio.is_exact is True

    def test_endpoint_law_used(self, barrier_ratio):
        assert len(barrier_ratio.endpoint_law_used) > 10

    def test_derivation_steps_populated(self, barrier_ratio):
        assert len(barrier_ratio.derivation_steps) >= 4

    def test_notes_populated(self, barrier_ratio):
        assert len(barrier_ratio.notes) >= 3

    def test_ratio_positive(self, barrier_ratio):
        assert barrier_ratio.ratio > 0

    def test_ratio_less_than_one(self, barrier_ratio):
        assert barrier_ratio.ratio < 1.0

    def test_ratio_monotonically_decreasing(self):
        beta_values = [1.0, 2.0, 3.0, 4.0, 5.0]
        ratios = [_barrier_potential_ratio(b) for b in beta_values]
        for i in range(len(ratios) - 1):
            assert ratios[i] > ratios[i + 1]


# ================================================================
# TestRouteA
# ================================================================

class TestRouteA:
    """Tests for Route A: barrier-gravity ratio lapse proxy."""

    def test_psi_proxy_one_third_canon(self, route_a):
        assert abs(route_a.psi_proxy - 1.0 / 3.0) < 1e-15

    def test_classification_constitutive_derived(self, route_a):
        assert route_a.classification == LEVEL_CONSTITUTIVE_DERIVED

    def test_route_name(self, route_a):
        assert route_a.route_name == "A_barrier_gravity_ratio"

    def test_formula_populated(self, route_a):
        assert len(route_a.formula) > 0

    def test_identification_basis_populated(self, route_a):
        assert len(route_a.identification_basis) > 50

    def test_identification_mentions_not_true_metric(self, route_a):
        assert "NOT" in route_a.identification_basis or "not" in route_a.identification_basis.lower()

    def test_barrier_ratio_attached(self, route_a):
        assert route_a.barrier_ratio is not None
        assert route_a.barrier_ratio.is_exact is True

    def test_psi_positive(self, route_a):
        assert route_a.psi_proxy > 0

    def test_notes_populated(self, route_a):
        assert len(route_a.notes) >= 3


# ================================================================
# TestRouteB
# ================================================================

class TestRouteB:
    """Tests for Route B: effective metric at endpoint."""

    def test_A_schw_minus_2(self, route_b):
        assert abs(route_b.A_schw_at_Req - (-2.0)) < 1e-10

    def test_delta_A_one(self, route_b):
        assert abs(route_b.delta_A - 1.0) < 1e-10

    def test_A_eff_minus_one(self, route_b):
        assert abs(route_b.A_eff_at_Req - (-1.0)) < 1e-10

    def test_A_eff_is_negative(self, route_b):
        assert route_b.A_eff_is_negative is True

    def test_redshift_not_applicable(self, route_b):
        assert route_b.redshift_formula_applicable is False

    def test_psi_metric_is_none(self, route_b):
        assert route_b.psi_metric is None

    def test_classification_unresolved(self, route_b):
        assert route_b.classification == LEVEL_UNRESOLVED

    def test_obstruction_populated(self, route_b):
        assert len(route_b.obstruction) > 100

    def test_obstruction_mentions_sub_horizon(self, route_b):
        assert "sub-horizon" in route_b.obstruction.lower() or "spacelike" in route_b.obstruction.lower()

    def test_route_name(self, route_b):
        assert route_b.route_name == "B_effective_metric"

    def test_notes_populated(self, route_b):
        assert len(route_b.notes) >= 3

    def test_helper_returns_none_for_negative(self):
        psi, applicable = _psi_from_route_b(-1.0)
        assert psi is None
        assert applicable is False

    def test_helper_returns_value_for_positive(self):
        psi, applicable = _psi_from_route_b(0.5)
        assert applicable is True
        assert psi is not None
        assert abs(psi - (1.0 / math.sqrt(0.5) - 1.0)) < 1e-14


# ================================================================
# TestRouteC
# ================================================================

class TestRouteC:
    """Tests for Route C: Schwarzschild reference."""

    def test_psi_schw_1_5(self, route_c):
        assert abs(route_c.psi_schw - 1.5) < 1e-15

    def test_is_upper_bound(self, route_c):
        assert route_c.is_upper_bound is True

    def test_classification_upper_bound_only(self, route_c):
        assert route_c.classification == LEVEL_UPPER_BOUND_ONLY

    def test_greater_than_route_a(self, route_a, route_c):
        assert route_c.psi_schw > route_a.psi_proxy

    def test_route_name(self, route_c):
        assert route_c.route_name == "C_schwarzschild_reference"

    def test_notes_populated(self, route_c):
        assert len(route_c.notes) >= 3


# ================================================================
# TestRouteComparison
# ================================================================

class TestRouteComparison:
    """Tests for the comparison of all three routes."""

    def test_preferred_is_route_a(self, routes):
        assert routes.preferred_route == "A"

    def test_preferred_psi_matches_route_a(self, routes):
        assert abs(routes.preferred_psi_proxy - routes.route_a.psi_proxy) < 1e-15

    def test_preferred_classification_constitutive(self, routes):
        assert routes.preferred_classification == LEVEL_CONSTITUTIVE_DERIVED

    def test_all_routes_present(self, routes):
        assert routes.route_a is not None
        assert routes.route_b is not None
        assert routes.route_c is not None

    def test_route_a_less_than_route_c(self, routes):
        assert routes.route_a.psi_proxy < routes.route_c.psi_schw

    def test_route_b_not_applicable(self, routes):
        assert routes.route_b.redshift_formula_applicable is False

    def test_route_b_psi_is_none(self, routes):
        assert routes.route_b.psi_metric is None

    def test_notes_populated(self, routes):
        assert len(routes.notes) >= 3


# ================================================================
# TestSensitivityBand
# ================================================================

class TestSensitivityBand:
    """Tests for the sensitivity / scenario band around the proxy."""

    def test_central_one_third(self, sensitivity_band):
        assert abs(sensitivity_band.central - 1.0 / 3.0) < 1e-15

    def test_low_one_sixth(self, sensitivity_band):
        assert abs(sensitivity_band.low - 1.0 / 6.0) < 1e-15

    def test_high_two_thirds(self, sensitivity_band):
        assert abs(sensitivity_band.high - 2.0 / 3.0) < 1e-15

    def test_ordering(self, sensitivity_band):
        assert sensitivity_band.low < sensitivity_band.central < sensitivity_band.high

    def test_band_factor_2(self, sensitivity_band):
        assert sensitivity_band.band_factor == 2.0

    def test_low_equals_central_over_factor(self, sensitivity_band):
        assert abs(sensitivity_band.low - sensitivity_band.central / 2.0) < 1e-15

    def test_high_equals_central_times_factor(self, sensitivity_band):
        assert abs(sensitivity_band.high - sensitivity_band.central * 2.0) < 1e-15

    def test_numerically_same_as_prior(self, sensitivity_band):
        assert sensitivity_band.numerically_same_as_prior is True

    def test_central_elevated(self, sensitivity_band):
        assert sensitivity_band.central_elevated is True

    def test_prior_label_heuristic(self, sensitivity_band):
        assert sensitivity_band.prior_central_label == "heuristic"

    def test_new_label_constitutive(self, sensitivity_band):
        assert sensitivity_band.new_central_label == LEVEL_CONSTITUTIVE_DERIVED

    def test_band_source_populated(self, sensitivity_band):
        assert len(sensitivity_band.band_source) > 50

    def test_notes_populated(self, sensitivity_band):
        assert len(sensitivity_band.notes) >= 3


# ================================================================
# TestThreeLevelSummary
# ================================================================

class TestThreeLevelSummary:
    """Tests for the three-level hierarchy."""

    def test_level_1_value(self, three_levels):
        assert abs(three_levels.level_1_value - 1.0 / 3.0) < 1e-15

    def test_level_1_status_exact(self, three_levels):
        assert three_levels.level_1_status == LEVEL_EXACT

    def test_level_2_value(self, three_levels):
        assert abs(three_levels.level_2_value - 1.0 / 3.0) < 1e-15

    def test_level_2_status_constitutive(self, three_levels):
        assert three_levels.level_2_status == LEVEL_CONSTITUTIVE_DERIVED

    def test_level_3_value_none(self, three_levels):
        assert three_levels.level_3_value is None

    def test_level_3_status_unresolved(self, three_levels):
        assert three_levels.level_3_status == LEVEL_UNRESOLVED

    def test_level_3_obstruction_populated(self, three_levels):
        assert len(three_levels.level_3_obstruction) > 100

    def test_level_3_mentions_covariant(self, three_levels):
        assert "covariant" in three_levels.level_3_obstruction.lower()

    def test_notes_populated(self, three_levels):
        assert len(three_levels.notes) >= 2


# ================================================================
# TestSelfHealingCheck
# ================================================================

class TestSelfHealingCheck:
    """Tests for self-healing independence."""

    def test_source_vanishes(self, self_healing):
        assert self_healing.source_vanishes is True

    def test_source_at_eq_zero(self, self_healing):
        assert abs(self_healing.source_at_eq) < 1e-14

    def test_independent_of_psi(self, self_healing):
        assert self_healing.independent_of_psi is True

    def test_preserved_under_route_a(self, self_healing):
        assert self_healing.preserved_under_route_a is True

    def test_preserved_under_route_b(self, self_healing):
        assert self_healing.preserved_under_route_b is True

    def test_preserved_under_route_c(self, self_healing):
        assert self_healing.preserved_under_route_c is True

    def test_mechanism_populated(self, self_healing):
        assert len(self_healing.mechanism) > 100

    def test_notes_populated(self, self_healing):
        assert len(self_healing.notes) >= 3


# ================================================================
# TestShiftEstimates
# ================================================================

class TestShiftEstimates:
    """Tests for shift estimates using the constitutive-derived proxy."""

    def test_psi_proxy_central(self, shift_estimates):
        assert abs(shift_estimates.psi_proxy_central - 1.0 / 3.0) < 1e-15

    def test_tau_ratio(self, shift_estimates):
        expected = 1.0 / (1.0 + 1.0 / 3.0)  # 3/4
        assert abs(shift_estimates.tau_ratio_central - expected) < 1e-14

    def test_proper_time_shift(self, shift_estimates):
        assert shift_estimates.proper_time_shift_pct > 0
        assert shift_estimates.proper_time_shift_pct < 100

    def test_Q_shift(self, shift_estimates):
        assert shift_estimates.Q_shift_pct > 0
        assert shift_estimates.Q_shift_pct < 100

    def test_omega_0_tau_at_eq(self, shift_estimates):
        expected = 1.0 / (1.0 + 1.0 / 3.0)  # 3/4
        assert abs(shift_estimates.omega_0_tau_at_eq - expected) < 1e-14

    def test_notes_populated(self, shift_estimates):
        assert len(shift_estimates.notes) >= 3


# ================================================================
# TestParametricScan
# ================================================================

class TestParametricScan:
    """Tests for the beta_Q parametric scan."""

    def test_returns_list(self):
        results = scan_beta_Q()
        assert isinstance(results, list)
        assert len(results) >= 5

    def test_canon_beta_Q_2(self):
        results = scan_beta_Q()
        entry = [r for r in results if abs(r["beta_Q"] - 2.0) < 1e-10][0]
        assert abs(entry["psi_proxy"] - 1.0 / 3.0) < 1e-15
        assert entry["coincides_with_alpha_vac"] is True

    def test_beta_Q_3(self):
        results = scan_beta_Q()
        entry = [r for r in results if abs(r["beta_Q"] - 3.0) < 1e-10][0]
        assert abs(entry["psi_proxy"] - 0.25) < 1e-15
        assert entry["coincides_with_alpha_vac"] is False

    def test_coincidence_only_at_canon(self):
        results = scan_beta_Q()
        coinciding = [r for r in results if r["coincides_with_alpha_vac"]]
        assert len(coinciding) == 1
        assert abs(coinciding[0]["beta_Q"] - 2.0) < 1e-10

    def test_monotonically_decreasing(self):
        results = scan_beta_Q()
        psis = [r["psi_proxy"] for r in results]
        for i in range(len(psis) - 1):
            assert psis[i] > psis[i + 1]


# ================================================================
# TestMasterResult
# ================================================================

class TestMasterResult:
    """Tests for the complete effective lapse analysis."""

    def test_valid(self, master_result):
        assert master_result.valid is True

    def test_barrier_ratio_present(self, master_result):
        assert master_result.barrier_gravity_ratio is not None

    def test_three_levels_present(self, master_result):
        assert master_result.three_levels is not None

    def test_routes_present(self, master_result):
        assert master_result.routes is not None

    def test_sensitivity_band_present(self, master_result):
        assert master_result.sensitivity_band is not None

    def test_self_healing_present(self, master_result):
        assert master_result.self_healing is not None

    def test_shift_estimates_present(self, master_result):
        assert master_result.shift_estimates is not None

    def test_prior_heuristic_confirmed(self, master_result):
        assert master_result.prior_heuristic_confirmed is True

    def test_prior_heuristic_elevated(self, master_result):
        assert master_result.prior_heuristic_elevated is True

    def test_coincidence_explained(self, master_result):
        assert master_result.coincidence_explained is True

    def test_coincidence_description_populated(self, master_result):
        assert len(master_result.coincidence_description) > 50

    def test_approx_status_mentions_constitutive(self, master_result):
        assert "constitutive" in master_result.approx_status.lower()

    def test_approx_status_mentions_unresolved(self, master_result):
        assert "unresolved" in master_result.approx_status.lower()

    def test_remaining_obstruction_populated(self, master_result):
        assert len(master_result.remaining_obstruction) > 100

    def test_remaining_obstruction_mentions_sub_horizon(self, master_result):
        assert "sub-horizon" in master_result.remaining_obstruction.lower()

    def test_nonclaims_ge_15(self, master_result):
        assert len(master_result.nonclaims) >= 15

    def test_nonclaims_mention_constitutive(self, master_result):
        text = " ".join(master_result.nonclaims).lower()
        assert "constitutive" in text

    def test_nonclaims_mention_coincidence(self, master_result):
        text = " ".join(master_result.nonclaims).lower()
        assert "coincidence" in text

    def test_nonclaims_mention_beta_q(self, master_result):
        text = " ".join(master_result.nonclaims).lower()
        assert "beta_q" in text or "beta" in text

    def test_nonclaims_mention_sub_horizon(self, master_result):
        text = " ".join(master_result.nonclaims).lower()
        assert "sub-horizon" in text or "sub_horizon" in text

    def test_nonclaims_mention_self_healing(self, master_result):
        text = " ".join(master_result.nonclaims).lower()
        assert "self-healing" in text or "self_healing" in text

    def test_diagnostics_populated(self, master_result):
        d = master_result.diagnostics
        assert len(d) >= 10
        assert "barrier_ratio" in d
        assert "psi_proxy_central" in d
        assert "true_metric_lapse_resolved" in d
        assert d["true_metric_lapse_resolved"] is False

    def test_diagnostics_barrier_ratio_one_third(self, master_result):
        assert abs(master_result.diagnostics["barrier_ratio"] - 1.0 / 3.0) < 1e-15

    def test_level_1_exact(self, master_result):
        assert master_result.three_levels.level_1_status == LEVEL_EXACT

    def test_level_2_constitutive(self, master_result):
        assert master_result.three_levels.level_2_status == LEVEL_CONSTITUTIVE_DERIVED

    def test_level_3_unresolved(self, master_result):
        assert master_result.three_levels.level_3_status == LEVEL_UNRESOLVED


# ================================================================
# TestSerialization
# ================================================================

class TestSerialization:
    """Tests for serialization round-trip."""

    def test_serializes_to_dict(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        assert isinstance(d, dict)

    def test_serialized_valid(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        assert d["valid"] is True

    def test_serialized_has_barrier_ratio(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        assert "barrier_gravity_ratio" in d
        assert d["barrier_gravity_ratio"]["is_exact"] is True

    def test_serialized_has_three_levels(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        assert "three_levels" in d
        assert d["three_levels"]["level_1_status"] == LEVEL_EXACT
        assert d["three_levels"]["level_3_status"] == LEVEL_UNRESOLVED

    def test_serialized_has_routes(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        assert "routes" in d
        assert d["routes"]["preferred_route"] == "A"

    def test_serialized_route_b_psi_none(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        assert d["routes"]["route_b"]["psi_metric"] is None

    def test_serialized_has_sensitivity_band(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        assert "sensitivity_band" in d
        assert abs(d["sensitivity_band"]["central"] - 1.0 / 3.0) < 1e-15

    def test_serialized_has_self_healing(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        assert "self_healing" in d
        assert d["self_healing"]["source_vanishes"] is True

    def test_serialized_nonclaims(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        assert len(d["nonclaims"]) >= 15

    def test_json_roundtrip(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        s = json.dumps(d)
        d2 = json.loads(s)
        assert d2["valid"] is True
        assert abs(d2["barrier_gravity_ratio"]["ratio"] - 1.0 / 3.0) < 1e-15
        assert d2["routes"]["preferred_route"] == "A"
        assert d2["three_levels"]["level_3_status"] == LEVEL_UNRESOLVED

    def test_serialized_diagnostics(self, master_result):
        d = effective_lapse_result_to_dict(master_result)
        assert "diagnostics" in d
        assert d["diagnostics"]["true_metric_lapse_resolved"] is False
