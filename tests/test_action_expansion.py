"""Phase IV Action Principle Expansion — Tests.

Exhaustive testing of all three action-principle routes:
Route A: Overdamped parent theory (Klein-Gordon)
Route B: Doubled-field dissipative formalism (Galley)
Route C: Nonlocal retarded action (kernel convolution)

Each route is tested numerically, not merely classified.
"""

import math
import pytest

M_SUN = 1.989e30


# ============================================================================
# ROUTE A — OVERDAMPED PARENT (KLEIN-GORDON)
# ============================================================================

class TestRouteACosmological:
    """Full KG integration in cosmological sector."""

    def test_kg_cosmo_converges(self) -> None:
        """KG solution must converge toward GRUT solution."""
        from grut.action_expansion import test_route_a_cosmo
        res = test_route_a_cosmo()
        assert res.kg_converges_to_grut

    def test_kg_cosmo_overdamped_approx(self) -> None:
        """Overdamped approximation must also converge."""
        from grut.action_expansion import test_route_a_cosmo
        res = test_route_a_cosmo()
        assert res.overdamped_is_good_approx

    def test_kg_cosmo_rms_error_bounded(self) -> None:
        """KG-GRUT RMS error must be bounded."""
        from grut.action_expansion import test_route_a_cosmo
        res = test_route_a_cosmo()
        assert res.kg_grut_rms_error < 0.5

    def test_kg_cosmo_approaches_driver(self) -> None:
        """Both KG and GRUT solutions must approach the source X."""
        from grut.action_expansion import test_route_a_cosmo
        res = test_route_a_cosmo()
        # Final value should be close to source
        assert abs(res.phi_kg[-1] - res.source) / abs(res.source) < 0.1
        assert abs(res.phi_grut[-1] - res.source) / abs(res.source) < 0.01

    def test_kg_cosmo_has_enough_steps(self) -> None:
        from grut.action_expansion import test_route_a_cosmo
        res = test_route_a_cosmo()
        assert res.n_steps >= 1000
        assert len(res.phi_kg) > 10


class TestRouteACollapse:
    """Full KG integration in collapse sector — critical damping test."""

    def test_kg_collapse_converges(self) -> None:
        """KG must converge to GRUT even at critical damping."""
        from grut.action_expansion import test_route_a_collapse
        res = test_route_a_collapse()
        assert res.kg_converges_to_grut

    def test_kg_collapse_approaches_driver(self) -> None:
        from grut.action_expansion import test_route_a_collapse
        res = test_route_a_collapse()
        assert abs(res.phi_kg[-1] - res.source) / abs(res.source) < 0.1
        assert abs(res.phi_grut[-1] - res.source) / abs(res.source) < 0.01

    def test_collapse_structural_identity(self) -> None:
        """Notes must mention omega_0*tau structural identity."""
        from grut.action_expansion import test_route_a_collapse
        res = test_route_a_collapse()
        combined = " ".join(res.notes).lower()
        assert "structural identity" in combined or "omega_0" in combined

    def test_collapse_critical_damping_noted(self) -> None:
        """Notes must mention critical damping."""
        from grut.action_expansion import test_route_a_collapse
        res = test_route_a_collapse()
        combined = " ".join(res.notes).lower()
        assert "critical" in combined


class TestRouteAEvaluation:
    """Route A overall evaluation."""

    def test_route_a_classification(self) -> None:
        from grut.action_expansion import evaluate_route_a
        route, _, _ = evaluate_route_a()
        assert route.action_status == "quasi_action"
        assert route.is_local is True
        assert route.is_conservative is True

    def test_route_a_recovers_approximately(self) -> None:
        from grut.action_expansion import evaluate_route_a
        route, _, _ = evaluate_route_a()
        assert route.recovers_first_order == "approximate"

    def test_route_a_scalar_status(self) -> None:
        """Under Route A, scalar is EMERGENT (from deeper KG theory)."""
        from grut.action_expansion import evaluate_route_a
        route, _, _ = evaluate_route_a()
        assert route.scalar_status == "emergent"

    def test_route_a_has_obstruction(self) -> None:
        from grut.action_expansion import evaluate_route_a
        route, _, _ = evaluate_route_a()
        assert len(route.unresolved_obstruction) > 50

    def test_route_a_has_nonclaims(self) -> None:
        from grut.action_expansion import evaluate_route_a
        route, _, _ = evaluate_route_a()
        assert len(route.nonclaims) >= 3


# ============================================================================
# ROUTE B — DOUBLED-FIELD DISSIPATIVE (GALLEY)
# ============================================================================

class TestRouteBGalley:
    """Galley doubled-field formal verification."""

    def test_physical_limit_recovers_ode(self) -> None:
        """Physical-limit Galley must EXACTLY recover the GRUT ODE."""
        from grut.action_expansion import evaluate_route_b
        _, galley = evaluate_route_b()
        assert galley.physical_limit_recovers_ode

    def test_energy_balance(self) -> None:
        """Dissipation integral must match analytic prediction."""
        from grut.action_expansion import evaluate_route_b
        _, galley = evaluate_route_b()
        assert galley.energy_balance_consistent

    def test_dissipation_rate(self) -> None:
        """Dissipation rate ratio must be close to 1.0."""
        from grut.action_expansion import evaluate_route_b
        _, galley = evaluate_route_b()
        assert 0.99 < galley.dissipation_rate_matches < 1.01

    def test_is_serious_candidate(self) -> None:
        from grut.action_expansion import evaluate_route_b
        _, galley = evaluate_route_b()
        assert galley.is_serious_candidate
        assert not galley.is_formal_shell

    def test_gravity_coupling_not_tested(self) -> None:
        """Gravity coupling must be flagged as NOT tested."""
        from grut.action_expansion import evaluate_route_b
        _, galley = evaluate_route_b()
        assert not galley.gravity_coupling_tested


class TestRouteBEvaluation:
    """Route B overall evaluation."""

    def test_route_b_exact_recovery(self) -> None:
        from grut.action_expansion import evaluate_route_b
        route, _ = evaluate_route_b()
        assert route.recovers_first_order == "exact"
        assert route.recovery_quality > 0.99

    def test_route_b_is_dissipative(self) -> None:
        from grut.action_expansion import evaluate_route_b
        route, _ = evaluate_route_b()
        assert route.is_dissipative is True
        assert route.is_conservative is False

    def test_route_b_critical_damping_compatible(self) -> None:
        from grut.action_expansion import evaluate_route_b
        route, _ = evaluate_route_b()
        assert route.critical_damping_compatible

    def test_route_b_scalar_fundamental(self) -> None:
        """Under Route B, scalar is FUNDAMENTAL (in action)."""
        from grut.action_expansion import evaluate_route_b
        route, _ = evaluate_route_b()
        assert route.scalar_status == "fundamental"

    def test_route_b_obstruction_is_gravity(self) -> None:
        """The remaining obstruction must be gravity coupling."""
        from grut.action_expansion import evaluate_route_b
        route, _ = evaluate_route_b()
        assert "gravity" in route.unresolved_obstruction.lower()


# ============================================================================
# ROUTE C — NONLOCAL RETARDED ACTION
# ============================================================================

class TestRouteCKernel:
    """Nonlocal retarded kernel numerical verification."""

    def test_kernel_is_causal(self) -> None:
        from grut.action_expansion import test_route_c_kernel
        res = test_route_c_kernel(tau_eff=1.0)
        assert res.kernel_is_causal

    def test_kernel_is_normalized(self) -> None:
        from grut.action_expansion import test_route_c_kernel
        res = test_route_c_kernel(tau_eff=1.0)
        assert res.kernel_is_normalized
        assert 0.99 < res.kernel_norm < 1.01

    def test_convolution_equals_ode(self) -> None:
        """The convolution integral must match the ODE solution."""
        from grut.action_expansion import test_route_c_kernel
        res = test_route_c_kernel(tau_eff=1.0)
        assert res.equivalence_verified
        assert res.convolution_ode_max_error < 0.05

    def test_multi_timescale(self) -> None:
        """Multi-timescale source must also match."""
        from grut.action_expansion import test_route_c_kernel
        res = test_route_c_kernel(tau_eff=1.0)
        assert res.multi_timescale_verified
        assert res.multi_timescale_max_error < 0.1

    def test_action_properties(self) -> None:
        from grut.action_expansion import test_route_c_kernel
        res = test_route_c_kernel(tau_eff=1.0)
        assert res.action_is_real
        assert res.action_is_bounded


class TestRouteCEvaluation:
    """Route C overall evaluation."""

    def test_route_c_exact_recovery(self) -> None:
        from grut.action_expansion import evaluate_route_c
        route, _ = evaluate_route_c()
        assert route.recovers_first_order == "exact"
        assert route.recovery_quality > 0.95

    def test_route_c_is_nonlocal(self) -> None:
        from grut.action_expansion import evaluate_route_c
        route, _ = evaluate_route_c()
        assert route.is_local is False

    def test_route_c_is_formal_parent(self) -> None:
        from grut.action_expansion import evaluate_route_c
        route, _ = evaluate_route_c()
        assert route.action_status == "formal_parent"

    def test_route_c_scalar_effective(self) -> None:
        """Under Route C, scalar is EFFECTIVE (local rep of nonlocal kernel)."""
        from grut.action_expansion import evaluate_route_c
        route, _ = evaluate_route_c()
        assert route.scalar_status == "effective"

    def test_route_c_critical_damping_compatible(self) -> None:
        from grut.action_expansion import evaluate_route_c
        route, _ = evaluate_route_c()
        assert route.critical_damping_compatible

    def test_route_c_has_nonclaims(self) -> None:
        from grut.action_expansion import evaluate_route_c
        route, _ = evaluate_route_c()
        assert len(route.nonclaims) >= 4


# ============================================================================
# MASTER ANALYSIS
# ============================================================================

class TestMasterExpansion:
    """The full expansion must produce valid, complete results."""

    def test_result_is_valid(self) -> None:
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        assert result.valid

    def test_all_three_routes_present(self) -> None:
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        assert result.route_a is not None
        assert result.route_b is not None
        assert result.route_c is not None

    def test_best_route_identified(self) -> None:
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        assert result.best_route == "route_c_nonlocal"

    def test_sharpest_obstruction_nonempty(self) -> None:
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        assert len(result.sharpest_obstruction) > 100

    def test_trilemma_in_obstruction(self) -> None:
        """The local-conservative-first-order trilemma must be stated."""
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        text = result.sharpest_obstruction.lower()
        assert "local" in text
        assert "conservative" in text or "nonlocal" in text

    def test_scalar_status_route_dependent(self) -> None:
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        assert result.scalar_field_status == "route_dependent"

    def test_nonclaims_minimum(self) -> None:
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        assert len(result.nonclaims) >= 7

    def test_all_routes_preserve_phase3(self) -> None:
        """All three routes must be compatible with Phase III results."""
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        assert result.route_a.tphi_compatible
        assert result.route_b.tphi_compatible
        assert result.route_c.tphi_compatible

    def test_route_comparison_recovery(self) -> None:
        """Route A = approximate, Route B = exact, Route C = exact."""
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        assert result.route_a.recovers_first_order == "approximate"
        assert result.route_b.recovers_first_order == "exact"
        assert result.route_c.recovers_first_order == "exact"

    def test_route_comparison_locality(self) -> None:
        """Route A = local, Route B = local, Route C = nonlocal."""
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        assert result.route_a.is_local is True
        assert result.route_b.is_local is True
        assert result.route_c.is_local is False

    def test_route_comparison_scalar_status(self) -> None:
        """Each route gives different scalar status."""
        from grut.action_expansion import compute_action_expansion
        result = compute_action_expansion()
        assert result.route_a.scalar_status == "emergent"
        assert result.route_b.scalar_status == "fundamental"
        assert result.route_c.scalar_status == "effective"


# ============================================================================
# SERIALIZATION
# ============================================================================

class TestExpansionSerialization:
    def test_route_to_dict(self) -> None:
        from grut.action_expansion import evaluate_route_a, route_to_dict
        route, _, _ = evaluate_route_a()
        d = route_to_dict(route)
        assert d["name"] == "route_a_overdamped"
        assert isinstance(d["diagnostics"], dict)

    def test_full_expansion_to_dict(self) -> None:
        from grut.action_expansion import compute_action_expansion, expansion_to_dict
        result = compute_action_expansion()
        d = expansion_to_dict(result)
        assert d["valid"] is True
        assert d["best_route"] == "route_c_nonlocal"
        assert d["route_a"] is not None
        assert d["route_b"] is not None
        assert d["route_c"] is not None
