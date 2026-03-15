"""Tests for grut.galley_memory — Galley Route B T^Phi derivation.

Tests the Galley doubled-field formalism follow-up:
- Action candidate construction
- Physical-limit reduction
- T^Phi derivation
- Conservation checks
- Ghost / pathology analysis
- Master analysis
- Serialization
"""

import math
import unittest

from grut.galley_memory import (
    build_galley_candidate_action,
    reduce_to_physical_limit,
    derive_candidate_tphi,
    check_effective_conservation,
    analyze_ghost_risk,
    compute_galley_route_b_analysis,
    action_to_dict,
    reduction_to_dict,
    tphi_to_dict,
    ghost_to_dict,
    conservation_to_dict,
    galley_result_to_dict,
)


# ================================================================
# Action Candidate Tests
# ================================================================

class TestActionCandidate(unittest.TestCase):
    """Tests for the Galley action candidate construction."""

    def setUp(self):
        self.action = build_galley_candidate_action()

    def test_name(self):
        self.assertEqual(self.action.name, "galley_minimal_scalar")

    def test_physical_limit_recovers_grut(self):
        self.assertTrue(self.action.physical_limit_recovers_grut)

    def test_minimally_coupled(self):
        self.assertTrue(self.action.is_minimally_coupled)

    def test_has_kinetic_term(self):
        self.assertTrue(self.action.has_kinetic_term)

    def test_kinetic_sign_standard(self):
        self.assertEqual(self.action.kinetic_sign, "standard")

    def test_tphi_status(self):
        self.assertEqual(self.action.tphi_status, "physical-limit derived")

    def test_has_nonclaims(self):
        self.assertGreaterEqual(len(self.action.nonclaims), 3)

    def test_scalar_action_form_nonempty(self):
        self.assertGreater(len(self.action.scalar_action_form), 20)

    def test_dissipative_kernel_form_nonempty(self):
        self.assertGreater(len(self.action.dissipative_kernel_form), 20)


# ================================================================
# Physical-Limit Reduction Tests
# ================================================================

class TestPhysicalLimitReduction(unittest.TestCase):
    """Tests for the physical-limit reduction of the doubled system."""

    def setUp(self):
        self.reduction = reduce_to_physical_limit()

    def test_eom_recovered(self):
        self.assertTrue(self.reduction.eom_recovered)

    def test_eom_max_error_small(self):
        self.assertLess(self.reduction.eom_max_error, 1e-12)

    def test_tphi_form_obtained(self):
        self.assertTrue(self.reduction.tphi_form_obtained)

    def test_tphi_is_type_I(self):
        self.assertTrue(self.reduction.tphi_is_type_I)

    def test_tphi_components_explicit(self):
        self.assertTrue(self.reduction.tphi_components_explicit)

    def test_cosmo_reduction_consistent(self):
        self.assertTrue(self.reduction.cosmo_reduction_consistent)

    def test_collapse_reduction_consistent(self):
        self.assertTrue(self.reduction.collapse_reduction_consistent)

    def test_reduction_status_exact(self):
        self.assertEqual(self.reduction.reduction_status, "exact")

    def test_notes_nonempty(self):
        self.assertGreater(len(self.reduction.notes), 3)


# ================================================================
# T^Phi Derivation Tests
# ================================================================

class TestCandidateTphi(unittest.TestCase):
    """Tests for the derived T^Phi_{mu nu}."""

    def setUp(self):
        self.tphi = derive_candidate_tphi()

    def test_derivation_status(self):
        self.assertEqual(self.tphi.derivation_status, "physical-limit derived")

    def test_derived_from_galley(self):
        self.assertEqual(self.tphi.derived_from, "galley_action")

    def test_derivation_chain_complete(self):
        self.assertGreaterEqual(len(self.tphi.derivation_chain), 5)

    def test_matches_constitutive_cosmo(self):
        self.assertTrue(self.tphi.matches_constitutive_cosmo)

    def test_matches_constitutive_collapse(self):
        self.assertTrue(self.tphi.matches_constitutive_collapse)

    def test_upgrades_constitutive(self):
        self.assertTrue(self.tphi.upgrades_constitutive)

    def test_energy_density_form_nonempty(self):
        self.assertGreater(len(self.tphi.energy_density_form), 20)

    def test_pressure_form_nonempty(self):
        self.assertGreater(len(self.tphi.pressure_form), 20)

    def test_cosmo_forms_populated(self):
        self.assertGreater(len(self.tphi.cosmo_rho_phi), 10)
        self.assertGreater(len(self.tphi.cosmo_p_phi), 10)
        self.assertGreater(len(self.tphi.cosmo_effective_w), 10)

    def test_steady_state_rho_negative(self):
        """At steady state (Phi = X), rho_Phi should be negative."""
        rho = self.tphi.diagnostics.get("cosmo_steady_state_rho_phi", 0)
        self.assertLess(rho, 0, "Memory energy density should be negative at steady state")

    def test_steady_state_w_minus_one(self):
        """At steady state (Phi = X), w_Phi should be -1."""
        w = self.tphi.diagnostics.get("cosmo_steady_state_w", 0)
        self.assertAlmostEqual(w, -1.0, places=5)

    def test_nonclaims_minimum(self):
        self.assertGreaterEqual(len(self.tphi.nonclaims), 5)


# ================================================================
# Conservation Tests
# ================================================================

class TestConservationCosmo(unittest.TestCase):
    """Tests for cosmological sector conservation."""

    def setUp(self):
        self.cc = check_effective_conservation(sector="cosmological")

    def test_combined_conserved(self):
        self.assertTrue(self.cc.combined_conserved)

    def test_numerical_verified(self):
        self.assertTrue(self.cc.numerical_verified)

    def test_derivation_status(self):
        self.assertEqual(self.cc.derivation_status, "physical-limit derived")

    def test_conservation_mode_combined(self):
        self.assertIn("combined", self.cc.combined_conservation_mode)

    def test_mechanism_mentions_bianchi(self):
        self.assertIn("Bianchi", self.cc.conservation_mechanism)


class TestConservationCollapse(unittest.TestCase):
    """Tests for collapse sector conservation."""

    def setUp(self):
        self.cc = check_effective_conservation(sector="collapse")

    def test_combined_conserved(self):
        self.assertTrue(self.cc.combined_conserved)

    def test_derivation_status(self):
        self.assertEqual(self.cc.derivation_status, "physical-limit derived")

    def test_conservation_mode_force_balance(self):
        self.assertIn("force_balance", self.cc.combined_conservation_mode)


# ================================================================
# Ghost Analysis Tests
# ================================================================

class TestGhostAnalysis(unittest.TestCase):
    """Tests for ghost / pathology analysis."""

    def setUp(self):
        self.ghost = analyze_ghost_risk()

    def test_scalar_ghost_free_physical_limit(self):
        self.assertTrue(self.ghost.scalar_ghost_free_physical_limit)

    def test_scalar_mass_squared_positive(self):
        self.assertTrue(self.ghost.scalar_mass_squared_positive)

    def test_scalar_hamiltonian_bounded(self):
        self.assertTrue(self.ghost.scalar_hamiltonian_bounded_below)

    def test_doubled_has_wrong_sign_mode(self):
        """The doubled system MUST have a wrong-sign mode (Phi_2)."""
        self.assertTrue(self.ghost.doubled_has_wrong_sign_mode)

    def test_physical_limit_projects_out_ghost(self):
        self.assertTrue(self.ghost.physical_limit_projects_out_ghost)

    def test_physical_limit_ghost_free(self):
        self.assertTrue(self.ghost.physical_limit_ghost_free)

    def test_metric_ghost_undetermined(self):
        self.assertEqual(self.ghost.metric_doubling_ghost_risk, "undetermined")

    def test_full_theory_undetermined(self):
        self.assertEqual(self.ghost.full_theory_ghost_status, "undetermined")

    def test_notes_mention_design(self):
        """Ghost is by design in Galley formalism."""
        notes_combined = " ".join(self.ghost.notes).lower()
        self.assertIn("by design", notes_combined)


# ================================================================
# Master Analysis Tests
# ================================================================

class TestMasterAnalysis(unittest.TestCase):
    """Tests for the full Route B master analysis."""

    def setUp(self):
        self.result = compute_galley_route_b_analysis()

    def test_valid(self):
        self.assertTrue(self.result.valid)

    def test_all_components_present(self):
        self.assertIsNotNone(self.result.action)
        self.assertIsNotNone(self.result.reduction)
        self.assertIsNotNone(self.result.tphi)
        self.assertIsNotNone(self.result.conservation_cosmo)
        self.assertIsNotNone(self.result.conservation_collapse)
        self.assertIsNotNone(self.result.ghost)

    def test_tphi_derivation_status(self):
        self.assertEqual(self.result.tphi_derivation_status, "physical-limit derived")

    def test_route_b_standing_upgraded(self):
        self.assertEqual(self.result.route_b_standing, "upgraded")

    def test_comparison_to_route_c_nonempty(self):
        self.assertGreater(len(self.result.comparison_to_route_c), 100)

    def test_exact_remaining_obstruction_nonempty(self):
        self.assertGreater(len(self.result.exact_remaining_obstruction), 100)

    def test_nonclaims_minimum(self):
        self.assertGreaterEqual(len(self.result.nonclaims), 10)

    def test_obstruction_mentions_physical_limit(self):
        self.assertIn("physical-limit", self.result.exact_remaining_obstruction.lower())

    def test_obstruction_mentions_ghost(self):
        self.assertIn("ghost", self.result.exact_remaining_obstruction.lower())

    def test_route_c_comparison_balanced(self):
        """Should mention both advantages for B and C."""
        comp = self.result.comparison_to_route_c.lower()
        self.assertIn("advantage", comp)
        self.assertIn("route b", comp)
        self.assertIn("route c", comp)


# ================================================================
# Serialization Tests
# ================================================================

class TestSerialization(unittest.TestCase):
    """Tests for serialization helpers."""

    def setUp(self):
        self.result = compute_galley_route_b_analysis()

    def test_action_to_dict(self):
        d = action_to_dict(self.result.action)
        self.assertEqual(d["name"], "galley_minimal_scalar")
        self.assertTrue(d["physical_limit_recovers_grut"])

    def test_reduction_to_dict(self):
        d = reduction_to_dict(self.result.reduction)
        self.assertTrue(d["eom_recovered"])
        self.assertEqual(d["reduction_status"], "exact")

    def test_tphi_to_dict(self):
        d = tphi_to_dict(self.result.tphi)
        self.assertEqual(d["derivation_status"], "physical-limit derived")
        self.assertTrue(d["upgrades_constitutive"])

    def test_ghost_to_dict(self):
        d = ghost_to_dict(self.result.ghost)
        self.assertTrue(d["physical_limit_ghost_free"])
        self.assertEqual(d["full_theory_ghost_status"], "undetermined")

    def test_full_result_to_dict(self):
        d = galley_result_to_dict(self.result)
        self.assertTrue(d["valid"])
        self.assertEqual(d["tphi_derivation_status"], "physical-limit derived")
        self.assertEqual(d["route_b_standing"], "upgraded")
        self.assertGreaterEqual(len(d["nonclaims"]), 10)


if __name__ == "__main__":
    unittest.main()
