"""Tests for grut.galley_truncation — Consistent truncation and attractor analysis.

Tests the Phase IV Route B truncation/attractor analysis:
- Plus/minus variable transform
- Scalar consistent truncation (Phi_- = 0 preserved)
- Scalar attractor status (Phi_- growth dynamics)
- Full KG+Galley system eigenvalue structure
- Galley vs independent evolution contrast
- Cosmological and collapse regime robustness
- Metric-difference sector structural analysis
- Master analysis and classification
- Serialization
"""

import math
import unittest

from grut.galley_truncation import (
    PHI_GOLDEN,
    build_doubled_scalar_system,
    transform_to_plus_minus_variables,
    analyze_scalar_truncation,
    analyze_scalar_attractor,
    analyze_metric_difference_sector,
    compute_galley_truncation_analysis,
    system_to_dict,
    transform_to_dict,
    truncation_to_dict,
    attractor_to_dict,
    metric_to_dict,
    classification_to_dict,
    truncation_result_to_dict,
    _integrate_galley_coupled,
    _integrate_independent,
    _integrate_full_kg_galley_phi_minus,
)


# ================================================================
# Plus/Minus Transform Tests
# ================================================================

class TestPlusMinusTransform(unittest.TestCase):
    """Tests for the +/- variable decomposition."""

    def setUp(self):
        self.t = transform_to_plus_minus_variables()

    def test_transform_valid(self):
        self.assertTrue(self.t.transform_valid)

    def test_inverse_valid(self):
        self.assertTrue(self.t.inverse_valid)

    def test_jacobian_nonzero(self):
        self.assertNotEqual(self.t.jacobian_determinant, 0.0)

    def test_jacobian_value(self):
        """Jacobian should be -1."""
        self.assertAlmostEqual(self.t.jacobian_determinant, -1.0, places=10)

    def test_transform_preserves_action(self):
        self.assertTrue(self.t.transform_preserves_action)

    def test_definitions_nonempty(self):
        self.assertGreater(len(self.t.phi_plus_definition), 5)
        self.assertGreater(len(self.t.phi_minus_definition), 5)

    def test_roundtrip_consistency(self):
        """Forward then inverse transform gives identity."""
        phi_1, phi_2 = 7.3, -2.1
        phi_plus = (phi_1 + phi_2) / 2.0
        phi_minus = phi_1 - phi_2
        phi_1_recov = phi_plus + phi_minus / 2.0
        phi_2_recov = phi_plus - phi_minus / 2.0
        self.assertAlmostEqual(phi_1_recov, phi_1, places=14)
        self.assertAlmostEqual(phi_2_recov, phi_2, places=14)


# ================================================================
# Doubled System Tests
# ================================================================

class TestDoubledScalarSystem(unittest.TestCase):
    """Tests for the doubled-scalar system construction."""

    def setUp(self):
        self.tau = 1.0
        self.sys = build_doubled_scalar_system(tau_eff=self.tau)

    def test_has_growing_mode(self):
        self.assertTrue(self.sys.has_growing_mode)

    def test_phi_minus_is_ghost(self):
        self.assertTrue(self.sys.phi_minus_is_ghost)

    def test_ctp_boundary_required(self):
        self.assertTrue(self.sys.ctp_boundary_required)

    def test_simple_growth_rate(self):
        """Simple Galley: growth rate = 1/tau."""
        self.assertAlmostEqual(
            self.sys.simple_phi_minus_growth_rate, 1.0 / self.tau, places=10,
        )

    def test_full_growing_rate(self):
        """Full KG+Galley: growing rate = phi/tau."""
        expected = PHI_GOLDEN / self.tau
        self.assertAlmostEqual(
            self.sys.full_phi_minus_growing_rate, expected, places=10,
        )

    def test_full_decaying_rate(self):
        """Full KG+Galley: decaying rate = 1/(phi*tau)."""
        expected = 1.0 / (PHI_GOLDEN * self.tau)
        self.assertAlmostEqual(
            self.sys.full_phi_minus_decaying_rate, expected, places=10,
        )

    def test_full_eigenvalue_product(self):
        """Product of eigenvalues = -1/tau^2 (from characteristic equation)."""
        eigenvalues = self.sys.full_phi_minus_eigenvalues
        product = eigenvalues[0] * eigenvalues[1]
        self.assertAlmostEqual(product, -1.0 / self.tau ** 2, places=10)

    def test_full_eigenvalue_sum(self):
        """Sum of eigenvalues = 1/tau (from characteristic equation)."""
        eigenvalues = self.sys.full_phi_minus_eigenvalues
        total = eigenvalues[0] + eigenvalues[1]
        self.assertAlmostEqual(total, 1.0 / self.tau, places=10)

    def test_eom_nonempty(self):
        self.assertGreater(len(self.sys.simple_phi_plus_eom), 10)
        self.assertGreater(len(self.sys.simple_phi_minus_eom), 10)
        self.assertGreater(len(self.sys.full_phi_minus_eom), 10)


# ================================================================
# Scalar Truncation Tests
# ================================================================

class TestScalarTruncation(unittest.TestCase):
    """Tests that Phi_- = 0 is a consistent truncation."""

    def setUp(self):
        self.trunc = analyze_scalar_truncation(tau_eff=1.0, n_steps=1000)

    def test_phi_minus_zero_is_solution(self):
        """Phi_- = 0 should be an exact solution of the Phi_- EOM."""
        self.assertTrue(self.trunc.phi_minus_zero_is_solution)

    def test_eom_at_zero(self):
        """dPhi_-/dt evaluated at Phi_- = 0 should be exactly 0."""
        self.assertAlmostEqual(self.trunc.phi_minus_eom_at_zero, 0.0, places=15)

    def test_phi_minus_preserved_numerically(self):
        """Phi_- should stay at zero when started at zero (numerically)."""
        self.assertTrue(self.trunc.phi_minus_zero_preserved_numerically)

    def test_max_residual_small(self):
        """Maximum Phi_- residual should be at machine precision."""
        self.assertLess(self.trunc.max_phi_minus_residual, 1e-12)

    def test_is_consistent_truncation(self):
        """Overall classification should be 'exact consistent truncation'."""
        self.assertTrue(self.trunc.is_consistent_truncation)

    def test_classification_is_exact(self):
        self.assertEqual(self.trunc.truncation_classification, "exact")


# ================================================================
# Scalar Attractor Tests
# ================================================================

class TestScalarAttractor(unittest.TestCase):
    """Tests that Phi_- = 0 is NOT a dynamical attractor."""

    def setUp(self):
        self.att = analyze_scalar_attractor(
            tau_eff=1.0, n_steps=2000, n_tau=3.0, epsilon=1e-6,
        )

    def test_simple_has_growing_mode(self):
        """Simple Galley system should have a growing Phi_- mode."""
        self.assertTrue(self.att.simple_has_growing_mode)

    def test_simple_growth_rate_matches(self):
        """Measured growth rate should match theoretical 1/tau."""
        self.assertTrue(self.att.simple_growth_rate_matches)

    def test_simple_growth_rate_value(self):
        """Theoretical growth rate should be 1/tau = 1.0."""
        self.assertAlmostEqual(self.att.simple_growth_rate_theoretical, 1.0, places=10)

    def test_full_has_growing_mode(self):
        """Full KG+Galley system should also have a growing Phi_- mode."""
        self.assertTrue(self.att.full_has_growing_mode)

    def test_full_growing_rate_matches(self):
        """Measured growth rate in full system should match phi/tau."""
        self.assertTrue(self.att.full_growing_rate_matches)

    def test_full_growing_rate_value(self):
        """Theoretical growing rate should be phi/tau."""
        self.assertAlmostEqual(
            self.att.full_growing_rate_theoretical, PHI_GOLDEN, places=10,
        )

    def test_is_not_attractor(self):
        """Phi_- = 0 must NOT be classified as an attractor."""
        self.assertFalse(self.att.is_attractor)

    def test_classification(self):
        self.assertEqual(self.att.classification, "unstable_consistent_truncation")

    def test_ctp_boundary_enforces_zero(self):
        """CTP boundary condition should be identified as the enforcement mechanism."""
        self.assertTrue(self.att.ctp_boundary_enforces_zero)


# ================================================================
# Galley vs Independent Evolution Tests
# ================================================================

class TestGalleyVsIndependent(unittest.TestCase):
    """Tests contrasting Galley cross-coupled vs independent evolution."""

    def setUp(self):
        self.att = analyze_scalar_attractor(
            tau_eff=1.0, n_steps=2000, n_tau=3.0, epsilon=1e-6,
        )

    def test_galley_phi_minus_grows(self):
        """Under Galley dynamics, Phi_- should grow."""
        self.assertTrue(self.att.galley_phi_minus_grows)

    def test_independent_phi_minus_decays(self):
        """Under independent dynamics, Phi_- should decay."""
        self.assertTrue(self.att.independent_phi_minus_decays)

    def test_cross_coupling_causes_growth(self):
        """The Galley cross-coupling is what causes the growth."""
        self.assertTrue(self.att.cross_coupling_causes_growth)

    def test_growth_is_substantial(self):
        """After 3 tau, Galley Phi_- should have grown by factor exp(3) ~ 20."""
        ratio = self.att.diagnostics["simple_growth_ratio"]
        # exp(3) ≈ 20.09
        self.assertGreater(ratio, 15.0)

    def test_decay_is_substantial(self):
        """After 3 tau, independent Phi_- should have decayed by factor exp(-3) ~ 0.05."""
        ratio = self.att.diagnostics["independent_decay_ratio"]
        self.assertLess(ratio, 0.1)

    def test_direct_integration_galley(self):
        """Direct integration of the Galley coupled system should show growth."""
        tau = 1.0
        eps = 1e-6
        phi0 = 0.5
        dt = 0.001
        n = 3000  # 3 tau with dt=0.001

        _, _, _, phi_minus = _integrate_galley_coupled(
            phi0 + eps / 2, phi0 - eps / 2, 1.0, tau, dt, n,
        )

        # Should have grown substantially
        self.assertGreater(abs(phi_minus[-1]), abs(eps) * 10.0)

    def test_direct_integration_independent(self):
        """Direct integration of independent system should show decay."""
        tau = 1.0
        eps = 1e-6
        phi0 = 0.5
        dt = 0.001
        n = 3000  # 3 tau with dt=0.001

        _, _, _, phi_minus = _integrate_independent(
            phi0 + eps / 2, phi0 - eps / 2, 1.0, tau, dt, n,
        )

        # Should have decayed substantially
        self.assertLess(abs(phi_minus[-1]), abs(eps) * 0.1)


# ================================================================
# Full KG+Galley System Tests
# ================================================================

class TestFullKGGalley(unittest.TestCase):
    """Tests for the second-order KG+Galley system."""

    def test_eigenvalue_golden_ratio(self):
        """Growing eigenvalue should involve the golden ratio."""
        tau = 1.0
        sys = build_doubled_scalar_system(tau_eff=tau)
        growing = sys.full_phi_minus_growing_rate
        self.assertAlmostEqual(growing, PHI_GOLDEN / tau, places=10)

    def test_phi_golden_ratio_value(self):
        """Golden ratio should be (1+sqrt(5))/2."""
        expected = (1.0 + math.sqrt(5.0)) / 2.0
        self.assertAlmostEqual(PHI_GOLDEN, expected, places=14)

    def test_characteristic_equation(self):
        """Eigenvalues should satisfy mu^2 - mu - 1 = 0."""
        mu_plus = PHI_GOLDEN
        mu_minus = (1.0 - math.sqrt(5.0)) / 2.0
        self.assertAlmostEqual(mu_plus ** 2 - mu_plus - 1.0, 0.0, places=12)
        self.assertAlmostEqual(mu_minus ** 2 - mu_minus - 1.0, 0.0, places=12)

    def test_kg_phi_minus_growth(self):
        """KG+Galley Phi_- should grow when started with nonzero initial data."""
        tau = 1.0
        eps = 1e-6
        dt = 0.001
        n = 2000

        phi_minus, _ = _integrate_full_kg_galley_phi_minus(eps, 0.0, tau, dt, n)

        # Should grow (the growing mode dominates at late times)
        self.assertGreater(abs(phi_minus[-1]), abs(eps) * 5.0)

    def test_kg_phi_minus_truncation(self):
        """KG+Galley Phi_- = 0 should be preserved when started at zero."""
        tau = 1.0
        dt = 0.001
        n = 2000

        phi_minus, _ = _integrate_full_kg_galley_phi_minus(0.0, 0.0, tau, dt, n)

        max_val = max(abs(pm) for pm in phi_minus)
        self.assertLess(max_val, 1e-14)


# ================================================================
# Regime Robustness Tests
# ================================================================

class TestRegimeRobustness(unittest.TestCase):
    """Tests that growth/truncation results are robust across parameter regimes."""

    def setUp(self):
        self.att = analyze_scalar_attractor(
            tau_eff=1.0, n_steps=2000, n_tau=3.0, epsilon=1e-6,
        )

    def test_cosmo_growth_matches(self):
        """Cosmological regime should show growth matching 1/tau_cosmo."""
        self.assertTrue(self.att.cosmo_growth_matches)

    def test_collapse_growth_matches(self):
        """Collapse regime should show growth matching 1/tau_collapse."""
        self.assertTrue(self.att.collapse_growth_matches)

    def test_different_tau_values(self):
        """Growth rate should scale as 1/tau for different tau values."""
        for tau in [0.1, 1.0, 10.0]:
            sys = build_doubled_scalar_system(tau_eff=tau)
            expected = 1.0 / tau
            self.assertAlmostEqual(
                sys.simple_phi_minus_growth_rate, expected, places=10,
            )


# ================================================================
# Metric Sector Tests
# ================================================================

class TestMetricDifferenceSector(unittest.TestCase):
    """Tests for the metric-difference sector analysis."""

    def setUp(self):
        self.metric = analyze_metric_difference_sector()

    def test_linearized_analysis_possible(self):
        self.assertTrue(self.metric.linearized_analysis_possible)

    def test_wrong_sign_kinetic(self):
        """Metric-difference sector should have wrong-sign kinetic energy."""
        self.assertTrue(self.metric.metric_minus_wrong_sign_kinetic)

    def test_expected_unstable(self):
        self.assertTrue(self.metric.metric_minus_expected_unstable)

    def test_truncation_consistent(self):
        """g_- = 0 should be a consistent truncation (by symmetry)."""
        self.assertTrue(self.metric.metric_truncation_is_consistent)

    def test_scalar_sources_metric(self):
        """Growing Phi_- should source metric difference."""
        self.assertTrue(self.metric.scalar_sources_metric_minus)

    def test_attractor_status(self):
        self.assertEqual(self.metric.metric_attractor_status, "expected_unstable__not_proven")

    def test_obstruction_nonempty(self):
        self.assertGreater(len(self.metric.full_analysis_obstruction), 100)


# ================================================================
# Master Analysis Tests
# ================================================================

class TestMasterAnalysis(unittest.TestCase):
    """Tests for the full truncation/attractor master analysis."""

    def setUp(self):
        self.result = compute_galley_truncation_analysis(
            tau_eff=1.0, n_steps=2000, n_tau=3.0, epsilon=1e-6,
        )

    def test_valid(self):
        self.assertTrue(self.result.valid)

    def test_all_components_present(self):
        self.assertIsNotNone(self.result.system)
        self.assertIsNotNone(self.result.transform)
        self.assertIsNotNone(self.result.scalar_truncation)
        self.assertIsNotNone(self.result.scalar_attractor)
        self.assertIsNotNone(self.result.metric)
        self.assertIsNotNone(self.result.classification)

    def test_scalar_truncation_exact(self):
        self.assertEqual(
            self.result.classification.scalar_truncation,
            "exact_consistent_truncation",
        )

    def test_scalar_not_attractor(self):
        self.assertEqual(
            self.result.classification.scalar_attractor,
            "not_attractor__growing_mode",
        )

    def test_metric_expected_unstable(self):
        self.assertEqual(
            self.result.classification.metric_attractor,
            "expected_unstable__not_proven",
        )

    def test_overall_classification(self):
        self.assertEqual(
            self.result.classification.overall,
            "consistent_truncation__not_attractor",
        )

    def test_route_b_upgrade_is_clarification(self):
        self.assertEqual(self.result.classification.route_b_upgrade, "clarification")

    def test_route_b_status_still_physical_limit_derived(self):
        self.assertIn(
            "physical-limit derived",
            self.result.classification.route_b_status_after,
        )

    def test_obstruction_nonempty(self):
        self.assertGreater(len(self.result.exact_remaining_obstruction), 200)

    def test_obstruction_mentions_attractor(self):
        self.assertIn("attractor", self.result.exact_remaining_obstruction.lower())

    def test_obstruction_mentions_ctp(self):
        self.assertIn("ctp", self.result.exact_remaining_obstruction.lower())

    def test_comparison_nonempty(self):
        self.assertGreater(len(self.result.comparison_to_route_c), 200)

    def test_comparison_mentions_route_c_advantage(self):
        comp = self.result.comparison_to_route_c.lower()
        self.assertIn("route c", comp)
        self.assertIn("advantage", comp)

    def test_nonclaims_minimum(self):
        self.assertGreaterEqual(len(self.result.nonclaims), 10)


# ================================================================
# Serialization Tests
# ================================================================

class TestSerialization(unittest.TestCase):
    """Tests for serialization helpers."""

    def setUp(self):
        self.result = compute_galley_truncation_analysis(
            tau_eff=1.0, n_steps=1000, n_tau=2.0, epsilon=1e-6,
        )

    def test_system_to_dict(self):
        d = system_to_dict(self.result.system)
        self.assertTrue(d["has_growing_mode"])
        self.assertTrue(d["phi_minus_is_ghost"])

    def test_transform_to_dict(self):
        d = transform_to_dict(self.result.transform)
        self.assertTrue(d["transform_valid"])

    def test_truncation_to_dict(self):
        d = truncation_to_dict(self.result.scalar_truncation)
        self.assertTrue(d["is_consistent_truncation"])
        self.assertEqual(d["truncation_classification"], "exact")

    def test_attractor_to_dict(self):
        d = attractor_to_dict(self.result.scalar_attractor)
        self.assertFalse(d["is_attractor"])
        self.assertTrue(d["cross_coupling_causes_growth"])

    def test_metric_to_dict(self):
        d = metric_to_dict(self.result.metric)
        self.assertTrue(d["metric_minus_wrong_sign_kinetic"])

    def test_classification_to_dict(self):
        d = classification_to_dict(self.result.classification)
        self.assertEqual(d["overall"], "consistent_truncation__not_attractor")

    def test_full_result_to_dict(self):
        d = truncation_result_to_dict(self.result)
        self.assertTrue(d["valid"])
        self.assertIsNotNone(d["system"])
        self.assertIsNotNone(d["scalar_truncation"])
        self.assertIsNotNone(d["scalar_attractor"])
        self.assertGreaterEqual(len(d["nonclaims"]), 10)


if __name__ == "__main__":
    unittest.main()
