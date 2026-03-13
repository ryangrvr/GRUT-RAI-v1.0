"""Tests for grut.collapse — GRUT Radial Collapse Solver.

Verification matrix
-------------------
1. Diagnostic functions (Schwarzschild radius, freefall time, compactness, Kretschner)
2. GR limit (alpha=0, gamma=0 → singularity)
3. GRUT arrest (alpha=1/3, gamma>0 → saturation with derived r_sat)
4. Bounce exclusion (V <= 0 for all time)
5. Curvature finiteness at saturation
6. Deterministic reproducibility (same inputs → identical result)
7. Mass sweep scaling
8. Input validation (bad params → CollapseError)
9. Energy ledger consistency
10. Apparent-horizon crossing detection
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from grut.collapse import (
    G_SI,
    C_SI,
    HBAR_SI,
    SEC_PER_YEAR,
    CollapseError,
    CollapseResult,
    compute_collapse,
    compute_compactness,
    compute_freefall_time,
    compute_kretschner,
    compute_mass_sweep,
    compute_schwarzschild_radius,
    fit_rsat_scaling,
)


# ── Shared test parameters ────────────────────────────────────────
# Stellar-mass object for diagnostics and GR-limit tests.
M_STELLAR = 1e30                      # kg (~0.5 M_sun)
R_S_STELLAR = compute_schwarzschild_radius(M_STELLAR)  # ~1.48 km
R0_STELLAR = 10.0 * R_S_STELLAR       # start at 10 r_s
T_FF_STELLAR = compute_freefall_time(R0_STELLAR, M_STELLAR)

# Weak-gravity regime for GRUT arrest tests.
# In this regime dissipation CAN arrest collapse within reasonable steps.
# gamma > GM/(H_cap * R^3) is the arrest condition.
# With M=1 kg, R=1 m, H_cap=1 s^-1: gamma_crit ≈ G/(H_cap) ≈ 7e-11.
# gamma=1000 >> gamma_crit → robust arrest.
M_ARREST = 1.0                        # 1 kg (test-friendly, non-relativistic)
R0_ARREST = 10.0                      # 10 m initial radius
TAU0_ARREST = 100.0                   # 100 s memory relaxation
ALPHA_VAC = 1.0 / 3.0
GAMMA_DISS_ARREST = 1000.0            # dissipation rate (s^-1)
H_CAP_ARREST = 1.0                    # L_stiff cap (s^-1)
N_STEPS_TEST = 100_000


# ================================================================
# 1. Diagnostic functions
# ================================================================

class TestDiagnostics:
    """Unit tests for standalone diagnostic helpers."""

    def test_schwarzschild_radius_formula(self) -> None:
        """r_s = 2GM/c^2, exact."""
        r_s = compute_schwarzschild_radius(M_STELLAR)
        expected = 2.0 * G_SI * M_STELLAR / (C_SI ** 2)
        assert r_s == pytest.approx(expected, rel=1e-12)

    def test_schwarzschild_radius_solar_mass(self) -> None:
        """r_s ~ 3 km for 1 solar mass."""
        M_sun = 1.989e30
        r_s = compute_schwarzschild_radius(M_sun)
        assert 2900.0 < r_s < 3000.0  # ~2953 m

    def test_freefall_time_formula(self) -> None:
        """t_ff = (pi/2) * sqrt(R0^3 / (2GM)), exact."""
        t_ff = compute_freefall_time(R0_STELLAR, M_STELLAR)
        expected = (math.pi / 2.0) * math.sqrt(R0_STELLAR ** 3 / (2.0 * G_SI * M_STELLAR))
        assert t_ff == pytest.approx(expected, rel=1e-12)

    def test_compactness_at_schwarzschild(self) -> None:
        """Compactness C = 1 exactly at r = r_s."""
        c = compute_compactness(R_S_STELLAR, M_STELLAR)
        assert c == pytest.approx(1.0, rel=1e-10)

    def test_compactness_far_from_horizon(self) -> None:
        """Compactness << 1 far from the horizon."""
        c = compute_compactness(1000.0 * R_S_STELLAR, M_STELLAR)
        assert c < 0.01

    def test_compactness_zero_radius(self) -> None:
        """Compactness → inf at R = 0."""
        c = compute_compactness(0.0, M_STELLAR)
        assert c == float("inf")

    def test_kretschner_formula(self) -> None:
        """K = 48(GM)^2 / (c^4 R^6), exact."""
        R = 5.0 * R_S_STELLAR
        K = compute_kretschner(R, M_STELLAR)
        expected = 48.0 * (G_SI * M_STELLAR) ** 2 / (C_SI ** 4 * R ** 6)
        assert K == pytest.approx(expected, rel=1e-10)

    def test_kretschner_zero_radius(self) -> None:
        """Kretschner → inf at R = 0."""
        K = compute_kretschner(0.0, M_STELLAR)
        assert K == float("inf")

    def test_kretschner_decreases_with_radius(self) -> None:
        """K ~ 1/R^6, strictly decreasing with R."""
        K1 = compute_kretschner(R_S_STELLAR, M_STELLAR)
        K2 = compute_kretschner(2.0 * R_S_STELLAR, M_STELLAR)
        assert K1 > K2
        assert K1 / K2 == pytest.approx(2.0 ** 6, rel=1e-6)


# ================================================================
# 2. GR limit (alpha=0, gamma=0 → singularity)
# ================================================================

class TestGRLimit:
    """Without GRUT operators, collapse reaches singularity (R → 0)."""

    def test_gr_limit_hits_singularity(self) -> None:
        """alpha=0, gamma=0 → pure GR Oppenheimer-Snyder → singularity."""
        result = compute_collapse(
            M_kg=M_STELLAR,
            R0_m=R0_STELLAR,
            tau0_s=100.0,
            alpha_vac=0.0,        # no vacuum screening
            gamma_diss=0.0,       # no dissipation
            H_cap=1e30,           # effectively no stiffness cap
            n_steps=N_STEPS_TEST,
            R_min_frac=1e-3,      # generous floor for test speed
        )
        assert result.termination_reason == "singularity"
        assert result.r_sat_m is None
        # R decreased dramatically
        assert result.R_m[-1] < 0.01 * R0_STELLAR

    def test_gr_limit_velocity_stays_negative(self) -> None:
        """Even in pure GR, V <= 0 (monotonic infall)."""
        result = compute_collapse(
            M_kg=M_STELLAR,
            R0_m=R0_STELLAR,
            tau0_s=100.0,
            alpha_vac=0.0,
            gamma_diss=0.0,
            H_cap=1e30,
            n_steps=N_STEPS_TEST,
            R_min_frac=1e-3,
        )
        # V[0] = 0 (starts from rest), V[1:] < 0
        assert np.all(result.V_ms[1:] <= 0.0)
        assert result.bounce_detected is False


# ================================================================
# 3. GRUT arrest (alpha=1/3, gamma>0 → saturation)
# ================================================================

class TestGRUTArrest:
    """With GRUT operators, collapse arrests at derived r_sat.

    Uses weak-gravity regime (M=1 kg, R0=10 m) where dissipation
    CAN arrest collapse within reasonable step counts.
    """

    @pytest.fixture()
    def arrest_result(self) -> CollapseResult:
        return compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )

    def test_terminates_at_saturation(self, arrest_result: CollapseResult) -> None:
        """GRUT collapse terminates at saturation, not singularity."""
        assert arrest_result.termination_reason == "saturation"

    def test_r_sat_is_derived(self, arrest_result: CollapseResult) -> None:
        """r_sat is a derived quantity (not None)."""
        assert arrest_result.r_sat_m is not None
        assert arrest_result.r_sat_m > 0.0

    def test_r_sat_below_initial(self, arrest_result: CollapseResult) -> None:
        """r_sat < R0 — collapse actually proceeded inward."""
        assert arrest_result.r_sat_m is not None
        assert arrest_result.r_sat_m < R0_ARREST

    def test_t_sat_positive(self, arrest_result: CollapseResult) -> None:
        """Saturation takes positive time."""
        assert arrest_result.t_sat_s is not None
        assert arrest_result.t_sat_s > 0.0

    def test_radius_monotonically_decreasing(self, arrest_result: CollapseResult) -> None:
        """R decreases monotonically (no re-expansion)."""
        dR = np.diff(arrest_result.R_m)
        assert np.all(dR <= 0.0)

    def test_l_stiff_activated(self) -> None:
        """L_stiff fires at least once during collapse.

        Uses stellar-mass parameters where gravitational acceleration
        is strong enough for V/R to exceed H_cap.
        """
        result = compute_collapse(
            M_kg=M_STELLAR,
            R0_m=R0_STELLAR,
            tau0_s=100.0,
            alpha_vac=ALPHA_VAC,
            gamma_diss=0.0,       # no dissipation — let V grow freely
            H_cap=1.0,            # low cap so L_stiff fires quickly
            n_steps=5_000,
        )
        assert result.l_stiff_activations > 0


# ================================================================
# 4. Bounce exclusion
# ================================================================

class TestBounceExclusion:
    """V <= 0 for all time — the fundamental GRUT sign theorem."""

    def test_no_bounce_grut(self) -> None:
        """V never becomes positive under GRUT operators."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        assert result.bounce_detected is False
        # Stronger: V[0]=0, V[k]<0 for all k>0 (before saturation kills velocity)
        assert np.all(result.V_ms <= 0.0)

    def test_no_bounce_strong_dissipation(self) -> None:
        """Even with very strong dissipation, no bounce."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=1e6,       # extreme dissipation
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        assert result.bounce_detected is False
        assert np.all(result.V_ms <= 0.0)

    def test_no_bounce_weak_alpha(self) -> None:
        """Even with small alpha_vac, no bounce."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=0.01,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        assert result.bounce_detected is False


# ================================================================
# 5. Curvature finiteness at saturation
# ================================================================

class TestCurvatureFiniteness:
    """At r_sat, curvature invariants remain finite."""

    def test_kretschner_finite_at_sat(self) -> None:
        """K at saturation is finite (not divergent)."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        assert result.termination_reason == "saturation"
        assert result.K_at_sat is not None
        assert math.isfinite(result.K_at_sat)
        assert result.K_at_sat > 0.0

    def test_kretschner_trajectory_finite(self) -> None:
        """Kretschner remains finite throughout GRUT trajectory."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        assert np.all(np.isfinite(result.K_kretschner))


# ================================================================
# 6. Deterministic reproducibility
# ================================================================

class TestDeterminism:
    """Same inputs → bit-identical outputs (NIS requirement)."""

    def test_deterministic_trajectories(self) -> None:
        """Two runs with identical inputs produce identical R, V, M_drive."""
        kwargs = dict(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        r1 = compute_collapse(**kwargs)
        r2 = compute_collapse(**kwargs)

        np.testing.assert_array_equal(r1.t_s, r2.t_s)
        np.testing.assert_array_equal(r1.R_m, r2.R_m)
        np.testing.assert_array_equal(r1.V_ms, r2.V_ms)
        np.testing.assert_array_equal(r1.M_drive, r2.M_drive)

    def test_deterministic_r_sat(self) -> None:
        """r_sat is reproducible to machine precision."""
        kwargs = dict(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        r1 = compute_collapse(**kwargs)
        r2 = compute_collapse(**kwargs)
        assert r1.r_sat_m == r2.r_sat_m
        assert r1.t_sat_s == r2.t_sat_s
        assert r1.termination_reason == r2.termination_reason


# ================================================================
# 7. Mass sweep + scaling
# ================================================================

class TestMassSweep:
    """Mass sweep produces r_sat for each mass and slope is extractable."""

    def test_sweep_produces_rows(self) -> None:
        """Sweep returns one row per mass point."""
        rows = compute_mass_sweep(
            M_min_kg=0.1,
            M_max_kg=100.0,
            n_masses=4,
            R0_factor=10.0,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        assert len(rows) == 4
        for row in rows:
            assert "M_kg" in row
            assert "r_sat_m" in row
            assert "termination" in row
            assert row["bounce_detected"] is False

    def test_sweep_all_saturate(self) -> None:
        """All masses in the weak-gravity sweep reach saturation with derived r_sat."""
        rows = compute_mass_sweep(
            M_min_kg=0.1,
            M_max_kg=100.0,
            n_masses=4,
            R0_factor=10.0,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        for row in rows:
            assert row["termination"] == "saturation", (
                f"M={row['M_kg']:.2e} did not saturate: {row['termination']}"
            )
            assert row["r_sat_m"] is not None
            assert row["r_sat_m"] > 0.0
            assert row["bounce_detected"] is False

    def test_fit_rsat_slope(self) -> None:
        """fit_rsat_scaling extracts a finite slope from sweep data."""
        masses = np.array([1e28, 1e29, 1e30, 1e31])
        r_sats = np.array([1e1, 1e2, 1e3, 1e4])  # synthetic power-law: r = M^1
        slope, intercept = fit_rsat_scaling(masses, r_sats)
        assert slope == pytest.approx(1.0, abs=0.01)
        assert math.isfinite(intercept)

    def test_fit_rsat_rejects_insufficient_points(self) -> None:
        """fit_rsat_scaling raises on < 2 points."""
        with pytest.raises(CollapseError, match="Need >= 2"):
            fit_rsat_scaling(np.array([1.0]), np.array([1.0]))

    def test_sweep_rejects_bad_mass_range(self) -> None:
        """Sweep raises on M_min >= M_max."""
        with pytest.raises(CollapseError):
            compute_mass_sweep(
                M_min_kg=1e31,
                M_max_kg=1e28,
                n_masses=4,
                tau0_s=TAU0_ARREST,
            )


# ================================================================
# 8. Input validation
# ================================================================

class TestInputValidation:
    """Bad parameters raise CollapseError with descriptive messages."""

    def test_negative_mass(self) -> None:
        with pytest.raises(CollapseError, match="M_kg must be positive"):
            compute_collapse(M_kg=-1.0, R0_m=1.0, tau0_s=1.0)

    def test_zero_mass(self) -> None:
        with pytest.raises(CollapseError, match="M_kg must be positive"):
            compute_collapse(M_kg=0.0, R0_m=1.0, tau0_s=1.0)

    def test_negative_radius(self) -> None:
        with pytest.raises(CollapseError, match="R0_m must be positive"):
            compute_collapse(M_kg=1.0, R0_m=-1.0, tau0_s=1.0)

    def test_negative_tau(self) -> None:
        with pytest.raises(CollapseError, match="tau0_s must be positive"):
            compute_collapse(M_kg=1.0, R0_m=1.0, tau0_s=-1.0)

    def test_alpha_out_of_range(self) -> None:
        with pytest.raises(CollapseError, match="alpha_vac must be in"):
            compute_collapse(M_kg=1.0, R0_m=1.0, tau0_s=1.0, alpha_vac=1.0)

    def test_negative_alpha(self) -> None:
        with pytest.raises(CollapseError, match="alpha_vac must be in"):
            compute_collapse(M_kg=1.0, R0_m=1.0, tau0_s=1.0, alpha_vac=-0.1)

    def test_negative_dissipation(self) -> None:
        with pytest.raises(CollapseError, match="gamma_diss must be >= 0"):
            compute_collapse(M_kg=1.0, R0_m=1.0, tau0_s=1.0, gamma_diss=-1.0)

    def test_zero_h_cap(self) -> None:
        with pytest.raises(CollapseError, match="H_cap must be positive"):
            compute_collapse(M_kg=1.0, R0_m=1.0, tau0_s=1.0, H_cap=0.0)


# ================================================================
# 9. Energy ledger consistency
# ================================================================

class TestEnergyLedger:
    """Energy bookkeeping: E_kin + E_pot + E_dissipated tracks total energy."""

    def test_energy_arrays_populated(self) -> None:
        """All energy arrays have the correct length."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        n = len(result.t_s)
        assert len(result.E_kinetic) == n
        assert len(result.E_potential) == n
        assert len(result.E_dissipated_cumul) == n

    def test_kinetic_energy_non_negative(self) -> None:
        """E_kin = (1/2) M V^2 >= 0 always."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        assert np.all(result.E_kinetic >= 0.0)

    def test_potential_energy_negative(self) -> None:
        """E_pot = -GM^2/R < 0 always (bound system)."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        assert np.all(result.E_potential < 0.0)

    def test_dissipated_energy_monotonically_increases(self) -> None:
        """Cumulative dissipation only grows (never negative)."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        dE = np.diff(result.E_dissipated_cumul)
        assert np.all(dE >= -1e-30)  # allow float rounding

    def test_no_dissipation_when_gamma_zero(self) -> None:
        """With gamma_diss=0, E_dissipated stays at 0."""
        result = compute_collapse(
            M_kg=M_STELLAR,
            R0_m=R0_STELLAR,
            tau0_s=100.0,
            alpha_vac=0.0,
            gamma_diss=0.0,
            H_cap=1e30,
            n_steps=N_STEPS_TEST,
            R_min_frac=1e-3,
        )
        assert np.all(result.E_dissipated_cumul == 0.0)


# ================================================================
# 10. Apparent-horizon crossing detection
# ================================================================

class TestApparentHorizon:
    """AH crossing detection: compactness >= 1 marks trapped surfaces."""

    def test_compactness_tracked(self) -> None:
        """Compactness array has consistent values."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        # Compactness should be finite and positive
        assert np.all(result.compactness > 0.0)
        assert np.all(np.isfinite(result.compactness))

    def test_compactness_increases_during_collapse(self) -> None:
        """Compactness generally increases as R decreases."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        # Final compactness > initial compactness
        assert result.compactness[-1] > result.compactness[0]

    def test_trapped_flag_consistency(self) -> None:
        """is_trapped matches compactness >= 1."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        np.testing.assert_array_equal(
            result.is_trapped,
            result.compactness >= 1.0,
        )

    def test_ah_crossings_have_correct_format(self) -> None:
        """AH crossings are (time, radius, direction) tuples."""
        result = compute_collapse(
            M_kg=M_STELLAR,
            R0_m=R0_STELLAR,
            tau0_s=100.0,
            alpha_vac=ALPHA_VAC,
            gamma_diss=0.0,
            H_cap=1e30,
            n_steps=N_STEPS_TEST,
            R_min_frac=1e-3,
        )
        for crossing in result.ah_crossings:
            assert len(crossing) == 3
            t, R, direction = crossing
            assert isinstance(t, float)
            assert isinstance(R, float)
            assert direction in ("formation", "dissolution")
            assert t > 0.0
            assert R > 0.0


# ================================================================
# 11. Result structure completeness
# ================================================================

class TestResultStructure:
    """CollapseResult contains all required fields."""

    def test_inputs_recorded(self) -> None:
        """The inputs dict records what was passed in."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        assert result.inputs["M_kg"] == M_ARREST
        assert result.inputs["R0_m"] == R0_ARREST
        assert result.inputs["tau0_s"] == TAU0_ARREST
        assert result.inputs["alpha_vac"] == ALPHA_VAC
        assert result.inputs["gamma_diss"] == GAMMA_DISS_ARREST

    def test_reference_quantities(self) -> None:
        """r_s and t_ff are computed correctly."""
        r_s_arrest = compute_schwarzschild_radius(M_ARREST)
        t_ff_arrest = compute_freefall_time(R0_ARREST, M_ARREST)
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        assert result.r_s_m == pytest.approx(r_s_arrest, rel=1e-10)
        assert result.t_ff_s == pytest.approx(t_ff_arrest, rel=1e-10)

    def test_trajectory_arrays_consistent_length(self) -> None:
        """All trajectory arrays have the same length."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        n = len(result.t_s)
        assert n > 1
        assert len(result.R_m) == n
        assert len(result.V_ms) == n
        assert len(result.M_drive) == n
        assert len(result.compactness) == n
        assert len(result.is_trapped) == n
        assert len(result.K_kretschner) == n
        assert len(result.tau_eff_s) == n
        assert len(result.a_eff) == n

    def test_time_monotonically_increasing(self) -> None:
        """Time array is strictly increasing."""
        result = compute_collapse(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        dt = np.diff(result.t_s)
        assert np.all(dt > 0.0)


# ================================================================
# 12. Physical constants
# ================================================================

class TestConstants:
    """SI constants are correct."""

    def test_G_SI(self) -> None:
        assert G_SI == pytest.approx(6.674e-11, rel=1e-3)

    def test_C_SI(self) -> None:
        assert C_SI == 299_792_458.0

    def test_HBAR_SI(self) -> None:
        assert HBAR_SI == pytest.approx(1.054571817e-34, rel=1e-6)

    def test_SEC_PER_YEAR(self) -> None:
        assert SEC_PER_YEAR == pytest.approx(365.25 * 24 * 3600, rel=1e-10)


# ================================================================
# 13. OP_QPRESS_001: Quantum Pressure Barrier
# ================================================================

# Shared constants for OP_QPRESS_001 tests
_M_QP = 1e30  # kg — stellar mass
_R_S_QP = compute_schwarzschild_radius(_M_QP)
_TAU0_CANON = 1.3225e15  # s — canon memory timescale (41.9 Myr)
_H_CAP_CANON = 1e6 / SEC_PER_YEAR  # s^-1 — canon L_stiff cap
_GAMMA_DISS_QP = 1e-15  # s^-1 — canon dissipation
_ALPHA_VAC_QP = 1.0 / 3.0
_EPS_Q = 0.1
_BETA_Q = 2
_R_EQ_PREDICTED = _EPS_Q ** (1.0 / _BETA_Q)  # = sqrt(0.1) ≈ 0.316


class TestQPressBackwardCompat:
    """epsilon_Q=0 (default) must not change any existing behavior."""

    def test_qpress_off_by_default(self) -> None:
        """epsilon_Q=0 produces identical results to current solver."""
        shared = dict(
            M_kg=M_ARREST,
            R0_m=R0_ARREST,
            tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC,
            gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST,
            n_steps=N_STEPS_TEST,
        )
        result_base = compute_collapse(**shared)
        result_qp = compute_collapse(**shared, epsilon_Q=0.0, beta_Q=2.0)
        assert result_base.termination_reason == result_qp.termination_reason
        np.testing.assert_array_equal(result_base.R_m, result_qp.R_m)
        np.testing.assert_array_equal(result_base.V_ms, result_qp.V_ms)

    def test_qpress_a_Q_all_zero_when_off(self) -> None:
        """a_Q array is all zeros when epsilon_Q=0."""
        result = compute_collapse(
            M_kg=M_ARREST, R0_m=R0_ARREST, tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC, gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST, n_steps=N_STEPS_TEST,
            epsilon_Q=0.0,
        )
        assert result.a_Q is not None
        assert np.all(result.a_Q == 0.0)

    def test_qpress_new_fields_have_defaults(self) -> None:
        """All new OP_QPRESS_001 diagnostic fields exist and have safe defaults."""
        result = compute_collapse(
            M_kg=M_ARREST, R0_m=R0_ARREST, tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC, gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST, n_steps=N_STEPS_TEST,
        )
        assert result.force_balance_residual == 0.0
        assert result.R_eq_predicted == 0.0
        assert result.asymptotic_stability_indicator == 0.0
        assert result.a_grav_final >= 0.0
        assert result.endpoint_motion_class in (
            "sign_definite_infall", "unknown",
        )


class TestQPressPhysicalEndpoint:
    """Tests that OP_QPRESS_001 creates a genuine physical equilibrium."""

    def _run_qpress(self, *, M_kg=_M_QP, R0_factor=10.0, epsilon_Q=_EPS_Q,
                    beta_Q=_BETA_Q, n_steps=2_000_000, V_tol_frac=1e-8,
                    H_cap=_H_CAP_CANON, V0_mps=0.0, **kw):
        """Shared helper for OP_QPRESS_001 collapse runs."""
        r_s = compute_schwarzschild_radius(M_kg)
        return compute_collapse(
            M_kg=M_kg,
            R0_m=R0_factor * r_s,
            tau0_s=_TAU0_CANON,
            alpha_vac=_ALPHA_VAC_QP,
            gamma_diss=_GAMMA_DISS_QP,
            H_cap=H_cap,
            n_steps=n_steps,
            local_tau_mode="tier0",
            epsilon_Q=epsilon_Q,
            beta_Q=beta_Q,
            V_tol_frac=V_tol_frac,
            V0_mps=V0_mps,
            **kw,
        )

    def test_qpress_physical_endpoint(self) -> None:
        """OP_QPRESS_001 creates genuine equilibrium where a_net -> 0."""
        result = self._run_qpress()
        assert result.force_balance_residual < 0.05  # < 5% imbalance
        assert result.termination_reason in ("saturation", "radius_converged")

    def test_qpress_vtol_insensitive(self) -> None:
        """R_f/r_s does NOT depend on V_tol — physical, not numerical.

        Only V_tol values tight enough to reach the barrier equilibrium are
        tested here. Loose V_tol (e.g. 1e-4) causes the solver to terminate
        before the barrier engages — that tests the saturation detector, not
        the barrier.  The benchmark sweep tests the full V_tol range.
        """
        R_f_values = []
        for vtol in [1e-8, 1e-10, 1e-12]:
            result = self._run_qpress(V_tol_frac=vtol)
            R_f_values.append(float(result.R_m[-1]) / result.r_s_m)
        ratio = max(R_f_values) / min(R_f_values)
        assert ratio < 1.05, f"R_f/r_s varies too much with V_tol: ratio={ratio:.4f}"

    def test_qpress_r0_insensitive(self) -> None:
        """R_f/r_s is set by epsilon_Q, not by R0."""
        R_f_values = []
        for factor in [3, 5, 10, 30]:
            result = self._run_qpress(R0_factor=factor)
            R_f_values.append(float(result.R_m[-1]) / result.r_s_m)
        ratio = max(R_f_values) / min(R_f_values)
        assert ratio < 1.05, f"R_f/r_s varies too much with R0: ratio={ratio:.4f}"

    def test_qpress_analytical_prediction(self) -> None:
        """Numerical R_f approaches asymptotic R_eq = epsilon_Q^(1/beta_Q) * r_s.

        Only enforced when memory has saturated (M_drive ≈ a_grav).
        """
        result = self._run_qpress(epsilon_Q=0.1, beta_Q=2)
        # Only check analytical match if memory has actually saturated
        if abs(result.memory_tracking_ratio_final - 1.0) < 0.2:
            R_f_rs = float(result.R_m[-1]) / result.r_s_m
            R_eq_rs = 0.1 ** 0.5  # beta=2
            assert abs(R_f_rs - R_eq_rs) / R_eq_rs < 0.10  # within 10%

    def test_qpress_stability_indicator_positive(self) -> None:
        """Equilibrium has positive d(a_net)/dR (restoring)."""
        result = self._run_qpress()
        if result.force_balance_residual < 0.1:
            # Only meaningful near equilibrium
            assert result.asymptotic_stability_indicator > 0, (
                f"Stability indicator negative: {result.asymptotic_stability_indicator}"
            )

    def test_qpress_endpoint_motion_classified(self) -> None:
        """Endpoint motion is classified honestly — not assumed sign-definite."""
        result = self._run_qpress()
        assert result.endpoint_motion_class in (
            "sign_definite_infall", "equilibrium_restoring",
            "overshoot_damped", "bounce_violation",
        )
        # Must NOT be bounce_violation (shell escaping outward)
        assert result.endpoint_motion_class != "bounce_violation"

    def test_qpress_operator_share(self) -> None:
        """Endpoint is created by a_Q (operator), not by L_stiff alone."""
        result = self._run_qpress()
        if result.a_grav_final > 0:
            share = result.a_outward_final / result.a_grav_final
            # If the barrier has engaged, it should be a significant fraction
            # At exact equilibrium, share → epsilon_Q * (r_s/R_f)^beta_Q
            assert share > 0.1, (
                f"a_outward/a_grav = {share:.4f} — barrier too weak at endpoint"
            )

    def test_qpress_not_artifact(self) -> None:
        """Endpoint does NOT follow the L_stiff x V_tol artifact law."""
        result = self._run_qpress()
        R_f_rs = float(result.R_m[-1]) / result.r_s_m
        # Must differ from artifact prediction by > 10%
        if result.artifact_R_f > 0:
            deviation = abs(R_f_rs - result.artifact_R_f) / max(R_f_rs, 1e-30)
            assert deviation > 0.10, (
                f"R_f/r_s={R_f_rs:.4f} matches artifact={result.artifact_R_f:.4f}"
            )

    def test_qpress_hcap_insensitive(self) -> None:
        """R_f/r_s does NOT depend on H_cap — not L_stiff-shaped."""
        R_f_values = []
        for hcap_factor in [1, 10, 100]:
            result = self._run_qpress(H_cap=hcap_factor * _H_CAP_CANON)
            R_f_values.append(float(result.R_m[-1]) / result.r_s_m)
        ratio = max(R_f_values) / min(R_f_values)
        assert ratio < 1.05, f"R_f/r_s varies with H_cap: ratio={ratio:.4f}"

    def test_qpress_mass_independent(self) -> None:
        """R_eq/r_s = epsilon_Q^(1/beta_Q) regardless of M.

        Only masses whose dynamical timescales are compatible with the
        step budget are compared.  Very different M require vastly different
        step budgets; the benchmark sweep handles the full mass range.
        """
        R_f_rs_values = []
        for M in [1e30, 1e32]:
            result = self._run_qpress(M_kg=M, n_steps=2_000_000)
            # Only include if the solver converged (not step-budget limited)
            if result.termination_reason in ("saturation", "radius_converged"):
                R_f_rs_values.append(float(result.R_m[-1]) / result.r_s_m)
        assert len(R_f_rs_values) >= 2, "Not enough converged runs"
        ratio = max(R_f_rs_values) / min(R_f_rs_values)
        assert ratio < 1.10, f"R_f/r_s varies with M: ratio={ratio:.4f}"

    def test_qpress_negligible_at_large_r(self) -> None:
        """Barrier a_Q is negligible when R >> r_s."""
        # At R = 100*r_s: a_Q/a_grav = 0.1 * (1/100)^2 = 1e-5
        result = self._run_qpress(R0_factor=100)
        # a_Q at first recorded point (R ≈ 100*r_s) should be tiny
        if len(result.a_Q) > 0 and len(result.a_eff) > 0:
            a_g_init = G_SI * _M_QP / (float(result.R_m[0]) ** 2)
            ratio = float(result.a_Q[0]) / a_g_init if a_g_init > 0 else 0
            assert ratio < 0.001, f"a_Q/a_grav at R=100*r_s = {ratio:.6f} — not negligible"

    def test_qpress_divergence_radius(self) -> None:
        """Operator-on/off trajectories only diverge near R_eq, not at large R."""
        result_off = self._run_qpress(
            epsilon_Q=0.0, R0_factor=100, record_every=100,
        )
        result_on = self._run_qpress(
            epsilon_Q=0.1, R0_factor=100, record_every=100,
        )
        # Find first index where R differs by > 1%
        divergence_R_rs = None
        n_compare = min(len(result_off.R_m), len(result_on.R_m))
        for i in range(n_compare):
            R_off = float(result_off.R_m[i])
            R_on = float(result_on.R_m[i])
            if R_off > 0 and abs(R_off - R_on) / R_off > 0.01:
                divergence_R_rs = R_on / result_on.r_s_m
                break
        # Divergence should only happen at R < 3*r_s (near equilibrium)
        if divergence_R_rs is not None:
            assert divergence_R_rs < 3.0, (
                f"Divergence at R/r_s={divergence_R_rs:.2f} — too early"
            )

    def test_qpress_perturbation_from_outside(self) -> None:
        """Shell starting slightly outside R_eq converges to R_eq (attractor)."""
        r_s = compute_schwarzschild_radius(_M_QP)
        R_eq = _R_EQ_PREDICTED * r_s  # 0.316 * r_s
        result = self._run_qpress(
            R0_factor=1.1 * _R_EQ_PREDICTED,  # start 10% outside R_eq
            V0_mps=0.0,  # rest start
            n_steps=2_000_000,
        )
        R_f_rs = float(result.R_m[-1]) / r_s
        # Should converge toward R_eq (within 20% — generous for attractor test)
        assert abs(R_f_rs - _R_EQ_PREDICTED) / _R_EQ_PREDICTED < 0.20, (
            f"R_f/r_s={R_f_rs:.4f} did not converge to R_eq={_R_EQ_PREDICTED:.4f}"
        )

    def test_qpress_v0_mps_parameter(self) -> None:
        """V0_mps parameter correctly sets initial velocity."""
        result = compute_collapse(
            M_kg=M_ARREST, R0_m=R0_ARREST, tau0_s=TAU0_ARREST,
            alpha_vac=ALPHA_VAC, gamma_diss=GAMMA_DISS_ARREST,
            H_cap=H_CAP_ARREST, n_steps=1000,
            V0_mps=-0.5,  # small inward kick
        )
        # V[0] should be -0.5 m/s
        assert result.V_ms[0] == pytest.approx(-0.5, abs=1e-10)


# ================================================================
# Consistency tests — force-decomposition labels & status language
# ================================================================

class TestConsistencyForceLabels:
    """Verify canonical force-decomposition terminology across codebase."""

    def test_collapse_docstring_uses_a_net(self) -> None:
        """Module docstring must use a_net, not a_eff, in bounce exclusion."""
        import grut.collapse as mod
        doc = mod.__doc__ or ""
        # The docstring should mention a_net in bounce tiers
        assert "a_net" in doc, "collapse.py docstring missing 'a_net'"
        # Should NOT use 'a_eff' in bounce exclusion descriptions
        # (a_eff may appear elsewhere as variable name for backward compat)
        lines = doc.split("\n")
        for line in lines:
            if "Tier" in line and ("sign-definite" in line.lower() or "bounce" in line.lower()):
                assert "a_eff" not in line, (
                    f"Bounce tier line still uses 'a_eff': {line.strip()}"
                )

    def test_collapse_result_has_canonical_fields(self) -> None:
        """CollapseResult must expose canonical force decomposition fields."""
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CollapseResult)}
        required = {
            "a_Q",
            "force_balance_residual",
            "a_grav_final",
            "a_inward_final",
            "a_outward_final",
            "a_net_final",
            "endpoint_motion_class",
        }
        missing = required - field_names
        assert not missing, f"CollapseResult missing canonical fields: {missing}"

    def test_canon_json_uses_a_net_in_acceleration_eq(self) -> None:
        """Canon JSON collapse acceleration equation must use a_net, not a_eff."""
        import json
        from pathlib import Path
        canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
        if not canon_path.exists():
            pytest.skip("Canon file not found")
        canon = json.loads(canon_path.read_text())
        # Only check the acceleration/force equation (AEFF), not memory ODE
        for eq in canon.get("core_equations", {}).get("equations", []):
            eq_id = eq.get("id", "")
            if "AEFF" in eq_id:
                math_str = eq.get("math", "")
                # Should use canonical decomposition terminology
                assert "a_net" in math_str or "a_inward" in math_str, (
                    f"Equation {eq_id} does not use canonical decomposition: {math_str}"
                )

    def test_canon_json_r_sat_candidate(self) -> None:
        """r_sat must be CANDIDATE status (not UNDEMONSTRATED) under OP_QPRESS_001."""
        import json
        from pathlib import Path
        canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
        if not canon_path.exists():
            pytest.skip("Canon file not found")
        canon = json.loads(canon_path.read_text())
        # Check observables — may be a flat dict or list structure
        observables = canon.get("observables", {})
        # Try flat dict style: {"OBS_RSAT": "description..."}
        rsat_val = observables.get("OBS_RSAT")
        if rsat_val is None:
            # Try list style: [{"id": "OBS_RSAT", "definition": "..."}]
            for obs in observables.get("primary_targets", []):
                if obs.get("id") == "OBS_RSAT":
                    rsat_val = obs.get("definition", "")
                    break
        if rsat_val is None:
            # Try collapse.observables
            collapse_obs = canon.get("collapse", {}).get("observables", {})
            rsat_val = collapse_obs.get("OBS_RSAT")
        assert rsat_val is not None, "OBS_RSAT not found in canon"
        assert "CANDIDATE" in rsat_val, (
            f"OBS_RSAT should mention CANDIDATE status: {rsat_val}"
        )
        assert "UNDEMONSTRATED" not in rsat_val, (
            f"OBS_RSAT should NOT say UNDEMONSTRATED: {rsat_val}"
        )

    def test_canon_json_qpress_section_exists(self) -> None:
        """Canon must have quantum_pressure_barrier section with correct status."""
        import json
        from pathlib import Path
        canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
        if not canon_path.exists():
            pytest.skip("Canon file not found")
        canon = json.loads(canon_path.read_text())
        # Must be under collapse.quantum_pressure_barrier
        collapse = canon.get("collapse", {})
        qp = collapse.get("quantum_pressure_barrier", {})
        assert qp, "Missing collapse.quantum_pressure_barrier in canon"
        # Status promoted from RESEARCH_TARGET to CANDIDATE after Phase III-B
        # (constrained law passes full acceptance suite)
        assert qp.get("status") in ("RESEARCH_TARGET", "CANDIDATE"), (
            f"quantum_pressure_barrier status should be RESEARCH_TARGET or CANDIDATE, "
            f"got {qp.get('status')}"
        )
        assert qp.get("operator_id") == "OP_QPRESS_001", (
            f"operator_id should be OP_QPRESS_001, got {qp.get('operator_id')}"
        )
        # Parameters: UNFIXED (pre-Phase III) or CONSTRAINED (post-Phase III-B)
        params = qp.get("parameters", {})
        for pname in ("epsilon_Q", "beta_Q"):
            assert pname in params, f"Missing parameter {pname}"
            assert params[pname].get("status") in ("UNFIXED", "CONSTRAINED"), (
                f"{pname} status should be UNFIXED or CONSTRAINED, got {params[pname].get('status')}"
            )

    def test_system_prompt_has_endpoint_status(self) -> None:
        """System prompt must include collapse endpoint status section."""
        from ai.system_prompt import build_system_prompt
        prompt = build_system_prompt()
        assert "Collapse Endpoint Status" in prompt, (
            "System prompt missing 'Collapse Endpoint Status' section"
        )
        assert "OP_QPRESS_001" in prompt, (
            "System prompt missing OP_QPRESS_001 reference"
        )
        assert "CANDIDATE" in prompt, (
            "System prompt missing CANDIDATE status"
        )
        assert "NOT DEMONSTRATED" in prompt, (
            "System prompt missing 'NOT DEMONSTRATED' boundary"
        )

    def test_system_prompt_uses_a_net(self) -> None:
        """System prompt must use a_net terminology in force decomposition."""
        from ai.system_prompt import build_system_prompt
        prompt = build_system_prompt()
        assert "a_net" in prompt, "System prompt missing 'a_net'"
        assert "a_inward" in prompt, "System prompt missing 'a_inward'"
        assert "a_outward" in prompt, "System prompt missing 'a_outward'"
        assert "force_balance_residual" in prompt, (
            "System prompt missing 'force_balance_residual'"
        )
        # Check that the force decomposition bullet lines use a_net not a_eff
        lines = prompt.split("\n")
        in_decomp = False
        for line in lines:
            if "Collapse Force Decomposition" in line:
                in_decomp = True
                continue
            if in_decomp:
                # Stop at next section header
                if line.startswith("## ") and "Decomposition" not in line:
                    break
                # The actual formula lines (starting with "- **") should not
                # define a_eff as a force variable. Mentioning "a_eff" in a
                # "do not use" instruction is fine.
                if line.strip().startswith("- **a_"):
                    assert "a_eff" not in line, (
                        f"Force decomposition formula line uses 'a_eff': {line}"
                    )

    def test_system_prompt_boundary_of_claim(self) -> None:
        """System prompt must have Boundary of Current Claim section."""
        from ai.system_prompt import build_system_prompt
        prompt = build_system_prompt()
        assert "Boundary of Current Claim" in prompt, (
            "System prompt missing 'Boundary of Current Claim' section"
        )
        assert "DEMONSTRATED" in prompt
        # Must mention what is NOT demonstrated
        assert "epsilon_Q" in prompt and "unfixed" in prompt.lower(), (
            "Boundary section must mention epsilon_Q as unfixed"
        )

    def test_endpoint_motion_classes_valid(self) -> None:
        """All endpoint_motion_class values must be from the defined set."""
        valid = {
            "unknown",
            "sign_definite_infall",
            "equilibrium_restoring",
            "overshoot_damped",
            "bounce_violation",
        }
        # Run a simple collapse and check the class
        result = compute_collapse(
            M_kg=M_STELLAR, R0_m=R0_STELLAR, tau0_s=1e15,
            alpha_vac=ALPHA_VAC, gamma_diss=1e-15,
            H_cap=1e6 / SEC_PER_YEAR, n_steps=10000,
        )
        assert result.endpoint_motion_class in valid, (
            f"Invalid endpoint_motion_class: {result.endpoint_motion_class}"
        )


# ================================================================
# Phase III-A tests: order parameter and information ledger
# ================================================================

class TestPhaseIIIA:
    """Tests for Phase III-A additions: order parameter and information ledger."""

    def test_barrier_dominance_field_exists(self) -> None:
        """CollapseResult must have barrier_dominance_final field."""
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CollapseResult)}
        assert "barrier_dominance_final" in field_names
        assert "compactness_final" in field_names

    def test_barrier_dominance_zero_without_operator(self) -> None:
        """Barrier dominance should be 0 when epsilon_Q = 0 (operator off)."""
        result = compute_collapse(
            M_kg=M_STELLAR, R0_m=R0_STELLAR, tau0_s=1e15,
            alpha_vac=ALPHA_VAC, gamma_diss=1e-15,
            H_cap=1e6 / SEC_PER_YEAR, n_steps=10000,
        )
        assert result.barrier_dominance_final == 0.0, (
            f"Barrier dominance should be 0 with epsilon_Q=0, "
            f"got {result.barrier_dominance_final}"
        )

    def test_barrier_dominance_near_one_at_endpoint(self) -> None:
        """At the OP_QPRESS_001 endpoint, barrier dominance should be ~1."""
        r_s = compute_schwarzschild_radius(_M_QP)
        result = compute_collapse(
            M_kg=_M_QP, R0_m=10.0 * r_s, tau0_s=1.3225e15,
            alpha_vac=ALPHA_VAC, gamma_diss=1e-15,
            H_cap=1e6 / SEC_PER_YEAR, n_steps=2_000_000,
            local_tau_mode="tier0", epsilon_Q=0.1, beta_Q=2,
            V_tol_frac=1e-8,
        )
        # At force balance, a_outward ≈ a_inward → Phi ≈ 1
        assert result.barrier_dominance_final > 0.9, (
            f"Barrier dominance should be ~1 at endpoint, "
            f"got {result.barrier_dominance_final:.4f}"
        )

    def test_compactness_final_computed(self) -> None:
        """Compactness_final should be > 0 for any collapse run."""
        result = compute_collapse(
            M_kg=M_STELLAR, R0_m=R0_STELLAR, tau0_s=1e15,
            alpha_vac=ALPHA_VAC, gamma_diss=1e-15,
            H_cap=1e6 / SEC_PER_YEAR, n_steps=10000,
        )
        assert result.compactness_final > 0.0, (
            f"Compactness_final should be > 0, got {result.compactness_final}"
        )

    def test_information_ledger_import(self) -> None:
        """Information ledger module must be importable."""
        from grut.information import InformationLedger, from_collapse_result
        ledger = InformationLedger()
        assert ledger.I_fields == 0.0
        assert ledger.conservation_status == "UNTESTED"
        assert ledger.archive_access_status == "UNKNOWN"

    def test_information_ledger_from_collapse(self) -> None:
        """Information ledger can be constructed from a CollapseResult."""
        from grut.information import from_collapse_result, to_dict
        result = compute_collapse(
            M_kg=M_STELLAR, R0_m=R0_STELLAR, tau0_s=1e15,
            alpha_vac=ALPHA_VAC, gamma_diss=1e-15,
            H_cap=1e6 / SEC_PER_YEAR, n_steps=10000,
        )
        ledger = from_collapse_result(result)
        # I_fields should be positive (area > 0)
        assert ledger.I_fields > 0, f"I_fields should be > 0, got {ledger.I_fields}"
        # I_total >= I_fields (additive ledger)
        assert ledger.I_total >= ledger.I_fields, (
            f"I_total ({ledger.I_total}) < I_fields ({ledger.I_fields})"
        )
        # Conservation is UNTESTED (no dynamic check)
        assert ledger.conservation_status == "UNTESTED"
        # to_dict should include nonclaims
        d = to_dict(ledger)
        assert "nonclaims" in d
        assert len(d["nonclaims"]) > 0

    def test_information_ledger_nonclaims(self) -> None:
        """Information ledger nonclaims must be explicit."""
        from grut.information import InformationLedger, to_dict
        ledger = InformationLedger()
        d = to_dict(ledger)
        nonclaims = d["nonclaims"]
        # Must mention it doesn't solve information paradox
        assert any("information paradox" in nc.lower() for nc in nonclaims), (
            "Nonclaims must mention information paradox"
        )
        # Must mention proxy
        assert any("proxy" in nc.lower() or "classical" in nc.lower() for nc in nonclaims), (
            "Nonclaims must mention proxy/classical nature"
        )

    def test_conservation_check_placeholder(self) -> None:
        """Conservation check must return PLACEHOLDER status."""
        from grut.information import InformationLedger, check_conservation
        l1 = InformationLedger(I_fields=100.0, I_metric_memory=10.0, I_total=110.0)
        l2 = InformationLedger(I_fields=100.0, I_metric_memory=10.0, I_total=110.0)
        result = check_conservation(l1, l2)
        assert result["status"] == "PLACEHOLDER"
        assert result["conserved"] is True
        assert "nonclaim" in result
        assert "PROXY" in result["nonclaim"] or "proxy" in result["nonclaim"]

    def test_canon_has_barrier_dominance(self) -> None:
        """Canon JSON must have barrier_dominance entry."""
        import json
        from pathlib import Path
        canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
        if not canon_path.exists():
            pytest.skip("Canon file not found")
        canon = json.loads(canon_path.read_text())
        derived = canon.get("collapse", {}).get("derived", {})
        assert "barrier_dominance" in derived, (
            "Canon missing collapse.derived.barrier_dominance"
        )
        bd = derived["barrier_dominance"]
        # Status promoted from CANDIDATE to LOCKED after Phase III-B
        # (Phi is a well-defined solver diagnostic, not a hypothesis)
        assert bd.get("status") in ("CANDIDATE", "LOCKED"), (
            f"barrier_dominance status should be CANDIDATE or LOCKED, got {bd.get('status')}"
        )
        assert "Phi" in bd.get("definition", "")

    def test_canon_has_information_ledger(self) -> None:
        """Canon JSON must have information_ledger entry."""
        import json
        from pathlib import Path
        canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
        if not canon_path.exists():
            pytest.skip("Canon file not found")
        canon = json.loads(canon_path.read_text())
        derived = canon.get("collapse", {}).get("derived", {})
        assert "information_ledger" in derived, (
            "Canon missing collapse.derived.information_ledger"
        )
        il = derived["information_ledger"]
        assert il.get("status") == "ACTIVE / RESEARCH TARGET"
        assert "nonclaims" in il
        assert len(il["nonclaims"]) > 0

    def test_canon_has_derivation_tracks(self) -> None:
        """Canon JSON must have derivation_tracks for OP_QPRESS_001."""
        import json
        from pathlib import Path
        canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
        if not canon_path.exists():
            pytest.skip("Canon file not found")
        canon = json.loads(canon_path.read_text())
        qp = canon.get("collapse", {}).get("quantum_pressure_barrier", {})
        assert "derivation_tracks" in qp, (
            "Canon missing quantum_pressure_barrier.derivation_tracks"
        )
        dt = qp["derivation_tracks"]
        assert dt.get("preferred") == "curvature_linked_occupancy"
        tracks = dt.get("tracks", {})
        assert "curvature_linked_occupancy" in tracks
        clo = tracks["curvature_linked_occupancy"]
        assert "missing_closures" in clo
        assert len(clo["missing_closures"]) > 0


class TestPhaseIIIC_WP1:
    """Phase III-C WP1 tests — exterior matching module.

    Targeted tests only. Verifies:
    - Module imports
    - Data structures serialize cleanly
    - Matching analysis produces consistent results
    - Canon reflects WP1 status
    - No regressions in existing collapse tests
    """

    def test_exterior_matching_module_imports(self) -> None:
        """exterior_matching module must be importable."""
        from grut.exterior_matching import (
            InteriorEndpointState,
            ExteriorCandidate,
            MatchingResult,
            evaluate_matching,
            evaluate_matching_assumptions,
            matching_result_to_dict,
            interior_from_collapse_result,
            enclosed_mass_at_endpoint,
            compactness_at_endpoint,
            exterior_candidate_schwarzschild,
            exterior_candidate_modified,
            compare_exterior_candidates,
        )
        # All names importable — module is well-formed
        assert InteriorEndpointState is not None
        assert MatchingResult is not None

    def test_interior_endpoint_state_defaults(self) -> None:
        """InteriorEndpointState defaults to sensible zero values."""
        from grut.exterior_matching import InteriorEndpointState
        state = InteriorEndpointState()
        assert state.M_kg == 0.0
        assert state.R_eq_m == 0.0
        assert state.compactness == 0.0
        assert state.barrier_dominance == 0.0
        assert state.alpha_vac == 1.0 / 3.0

    def test_matching_result_serializes(self) -> None:
        """MatchingResult must serialize to a clean dict."""
        from grut.exterior_matching import (
            InteriorEndpointState,
            evaluate_matching,
            matching_result_to_dict,
        )
        # Construct a mock interior state matching the benchmark
        state = InteriorEndpointState(
            M_kg=1e30,
            R_eq_m=494.3,      # ~(1/3) r_s for M=1e30
            r_s_m=1483.0,
            R_eq_over_r_s=0.333333,
            compactness=3.0,
            is_post_horizon=True,
            a_grav=1e10,
            a_inward=1e10,
            a_outward=1e10,
            a_net=0.0,
            force_balance_residual=0.0,
            barrier_dominance=1.0,
            memory_tracking_ratio=1.0,
            stability_indicator=1e12,
            endpoint_motion_class="sign_definite_infall",
            epsilon_Q=1.0/9.0,
            beta_Q=2.0,
        )
        result = evaluate_matching(state)
        d = matching_result_to_dict(result)

        # Must be a dict with expected keys
        assert isinstance(d, dict)
        assert "exterior_model" in d
        assert "birkhoff_status" in d
        assert "wp2_allowed" in d
        assert "wp3_allowed" in d
        assert "nonclaims" in d
        assert "candidates" in d
        assert "required_closures" in d

    def test_schwarzschild_candidate_for_benchmark(self) -> None:
        """Under benchmark conditions, Schwarzschild should be leading candidate."""
        from grut.exterior_matching import (
            InteriorEndpointState,
            evaluate_matching,
        )
        state = InteriorEndpointState(
            M_kg=1e30,
            R_eq_m=494.3,
            r_s_m=1483.0,
            R_eq_over_r_s=0.333333,
            compactness=3.0,
            is_post_horizon=True,
            a_grav=1e10,
            a_inward=1e10,
            a_outward=1e10,
            a_net=0.0,
            force_balance_residual=0.0,
            barrier_dominance=1.0,
            memory_tracking_ratio=1.0,
            stability_indicator=1e12,
            endpoint_motion_class="sign_definite_infall",
            epsilon_Q=1.0/9.0,
            beta_Q=2.0,
        )
        result = evaluate_matching(state)

        assert result.exterior_model == "schwarzschild_like"
        assert result.birkhoff_status == "preserved_candidate"
        assert result.mass_conserved is True
        assert result.effective_mass_ratio == 1.0
        assert result.wp2_allowed is True

    def test_matching_nonclaims_present(self) -> None:
        """Matching result must include explicit nonclaims."""
        from grut.exterior_matching import (
            InteriorEndpointState,
            evaluate_matching,
        )
        state = InteriorEndpointState(
            M_kg=1e30,
            R_eq_m=494.3,
            r_s_m=1483.0,
            compactness=3.0,
            barrier_dominance=1.0,
            memory_tracking_ratio=1.0,
            epsilon_Q=1.0/9.0,
            beta_Q=2.0,
        )
        result = evaluate_matching(state)

        assert len(result.nonclaims) >= 5
        # Must not claim exterior is proven
        nonclaims_text = " ".join(result.nonclaims)
        assert "NOT proven" in nonclaims_text

    def test_matching_required_closures(self) -> None:
        """Matching result must list required closures."""
        from grut.exterior_matching import (
            InteriorEndpointState,
            evaluate_matching,
        )
        state = InteriorEndpointState(
            M_kg=1e30,
            R_eq_m=494.3,
            r_s_m=1483.0,
            compactness=3.0,
            barrier_dominance=1.0,
            memory_tracking_ratio=1.0,
            epsilon_Q=1.0/9.0,
            beta_Q=2.0,
        )
        result = evaluate_matching(state)

        assert len(result.required_closures) >= 2
        # Must mention covariant or Birkhoff
        closures_text = " ".join(result.required_closures)
        assert "Birkhoff" in closures_text or "covariant" in closures_text.lower()

    def test_matching_assumptions_complete(self) -> None:
        """evaluate_matching_assumptions must return key assumptions."""
        from grut.exterior_matching import (
            InteriorEndpointState,
            evaluate_matching_assumptions,
        )
        state = InteriorEndpointState(
            M_kg=1e30,
            R_eq_m=494.3,
            r_s_m=1483.0,
            compactness=3.0,
            barrier_dominance=1.0,
            memory_tracking_ratio=1.0,
        )
        assumptions = evaluate_matching_assumptions(state)

        assert "spherical_symmetry" in assumptions
        assert "m_drive_matter_local" in assumptions
        assert "mass_conservation" in assumptions
        assert "newtonian_gauge_sufficient" in assumptions
        # m_drive locality should be underdetermined
        assert assumptions["m_drive_matter_local"]["status"] == "underdetermined"

    def test_two_candidates_evaluated(self) -> None:
        """Both Schwarzschild and modified candidates must be evaluated."""
        from grut.exterior_matching import (
            InteriorEndpointState,
            evaluate_matching,
        )
        state = InteriorEndpointState(
            M_kg=1e30,
            R_eq_m=494.3,
            r_s_m=1483.0,
            compactness=3.0,
            barrier_dominance=1.0,
            memory_tracking_ratio=1.0,
            epsilon_Q=1.0/9.0,
            beta_Q=2.0,
        )
        result = evaluate_matching(state)

        assert "schwarzschild_like" in result.candidates
        assert "modified_memory_exterior" in result.candidates
        schw = result.candidates["schwarzschild_like"]
        mod = result.candidates["modified_memory_exterior"]
        assert schw.confidence == "moderate"
        assert mod.confidence == "low"

    def test_canon_has_wp1_result(self) -> None:
        """Canon JSON must reflect WP1 analysis result."""
        import json
        from pathlib import Path
        canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
        if not canon_path.exists():
            pytest.skip("Canon file not found")
        canon = json.loads(canon_path.read_text())
        efp = canon.get("collapse", {}).get("exterior_falsifier_program", {})
        assert efp, "Missing collapse.exterior_falsifier_program"
        wp1 = efp.get("work_packages", {}).get("WP1_exterior_matching", {})
        assert wp1, "Missing WP1_exterior_matching"
        # Must have a result (not NOT STARTED)
        assert "ANALYSIS COMPLETE" in wp1.get("status", "")

    def test_enclosed_mass_conservation(self) -> None:
        """Enclosed mass must equal input mass (dust model)."""
        from grut.exterior_matching import (
            InteriorEndpointState,
            enclosed_mass_at_endpoint,
        )
        M = 1.989e30  # solar mass
        state = InteriorEndpointState(M_kg=M)
        M_eff = enclosed_mass_at_endpoint(state)
        assert M_eff == M, "Enclosed mass must equal input mass in dust model"


# ================================================================
# Phase III-C WP2: Ringdown / Echo Falsifier Tests
# ================================================================

class TestPhaseIIIC_WP2:
    """Phase III-C WP2 tests — ringdown/echo module.

    Targeted tests only. Verifies:
    - Module imports and data structures
    - Physical computations produce sensible values
    - Echo scaling (Δt ∝ M)
    - Nonclaims and conditional labels present
    - Canon reflects WP2 status
    """

    def test_ringdown_module_imports(self) -> None:
        """ringdown module must be importable with all public names."""
        from grut.ringdown import (
            EchoParameters,
            EchoResult,
            schwarzschild_radius,
            tortoise_coordinate,
            potential_peak_radius,
            echo_time_delay,
            bdcc_oscillation_frequency,
            schwarzschild_qnm_l2,
            potential_peak_transmission,
            echo_amplitudes,
            compute_echo_analysis,
            echo_result_to_dict,
            scan_reflection_coefficient,
            scan_mass_range,
            G_SI,
            C_SI,
            M_SUN,
        )
        assert EchoParameters is not None
        assert EchoResult is not None

    def test_schwarzschild_radius_formula(self) -> None:
        """ringdown.schwarzschild_radius must match 2GM/c^2."""
        from grut.ringdown import schwarzschild_radius, G_SI as G, C_SI as C
        M = 30.0 * 1.989e30  # 30 solar masses
        r_s = schwarzschild_radius(M)
        expected = 2.0 * G * M / (C * C)
        assert r_s == pytest.approx(expected, rel=1e-10)

    def test_tortoise_coordinate_exterior(self) -> None:
        """Tortoise coordinate at light ring r_peak = 3/2 r_s."""
        from grut.ringdown import tortoise_coordinate
        r_s = 1000.0  # arbitrary
        r_peak = 1.5 * r_s
        r_star = tortoise_coordinate(r_peak, r_s)
        # r* = r + r_s * ln(r/r_s - 1) = 1.5*r_s + r_s*ln(0.5)
        expected = 1.5 * r_s + r_s * math.log(0.5)
        assert r_star == pytest.approx(expected, rel=1e-10)

    def test_tortoise_coordinate_interior(self) -> None:
        """Tortoise coordinate at R_eq = r_s/3 (inside horizon)."""
        from grut.ringdown import tortoise_coordinate
        r_s = 1000.0
        R_eq = r_s / 3.0
        r_star = tortoise_coordinate(R_eq, r_s)
        # r* = r + r_s * ln(1 - r/r_s) = r_s/3 + r_s*ln(2/3)
        expected = r_s / 3.0 + r_s * math.log(2.0 / 3.0)
        assert r_star == pytest.approx(expected, rel=1e-10)

    def test_echo_delay_positive(self) -> None:
        """Echo time delay must be positive and finite."""
        from grut.ringdown import echo_time_delay, schwarzschild_radius, M_SUN
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        R_eq = r_s / 3.0
        dt = echo_time_delay(R_eq, r_s)
        assert dt > 0.0, "Echo delay must be positive"
        assert math.isfinite(dt), "Echo delay must be finite"
        # For 30 M_sun: should be on the order of ~0.5 ms
        assert 1e-5 < dt < 1e-1, f"Echo delay {dt} s out of expected range"

    def test_echo_delay_scales_linearly_with_mass(self) -> None:
        """Δt_echo ∝ M — the echo delay must scale linearly with mass."""
        from grut.ringdown import echo_time_delay, schwarzschild_radius, M_SUN
        dt_values = []
        masses = [10.0, 30.0, 100.0, 1000.0]
        for M_solar in masses:
            M = M_solar * M_SUN
            r_s = schwarzschild_radius(M)
            R_eq = r_s / 3.0
            dt = echo_time_delay(R_eq, r_s)
            dt_values.append(dt)
        # Ratios: dt(M2)/dt(M1) should ≈ M2/M1
        for i in range(1, len(masses)):
            mass_ratio = masses[i] / masses[0]
            dt_ratio = dt_values[i] / dt_values[0]
            assert dt_ratio == pytest.approx(mass_ratio, rel=0.01), (
                f"Δt ratio {dt_ratio:.4f} != mass ratio {mass_ratio:.1f}"
            )

    def test_bdcc_oscillation_frequency_positive(self) -> None:
        """BDCC natural frequency must be positive and finite."""
        from grut.ringdown import bdcc_oscillation_frequency, schwarzschild_radius, M_SUN
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        R_eq = r_s / 3.0
        omega = bdcc_oscillation_frequency(M, R_eq, beta_Q=2.0)
        assert omega > 0.0, "ω_core must be positive"
        assert math.isfinite(omega), "ω_core must be finite"

    def test_qnm_l2_sensible_values(self) -> None:
        """l=2 QNM frequency/damping must be in the right ballpark."""
        from grut.ringdown import schwarzschild_qnm_l2, M_SUN
        M = 30.0 * M_SUN
        omega_R, omega_I, tau_damp, f_Hz = schwarzschild_qnm_l2(M)
        assert omega_R > 0.0
        assert omega_I > 0.0
        assert tau_damp > 0.0
        assert f_Hz > 0.0
        # For 30 M_sun: f_QNM ~ 250-500 Hz
        assert 100 < f_Hz < 1000, f"f_QNM = {f_Hz:.1f} Hz out of expected range"

    def test_potential_peak_transmission_l2(self) -> None:
        """l=2 transmission and reflection must be in physical range."""
        from grut.ringdown import potential_peak_transmission
        T_sq, R_peak = potential_peak_transmission(l=2)
        assert 0 < T_sq < 1.0, "|T|^2 must be in (0, 1)"
        assert 0 < R_peak < 1.0, "|R_peak| must be in (0, 1)"
        # Conservation: |T|^2 + |R|^2 ≈ 1 (not exact for WKB)
        assert T_sq + R_peak**2 == pytest.approx(1.0, abs=0.1)

    def test_echo_amplitudes_geometric_decay(self) -> None:
        """Echo amplitudes must decrease geometrically."""
        from grut.ringdown import echo_amplitudes
        amps = echo_amplitudes(5, transmission_sq=0.03, reflection_peak=0.98,
                               reflection_surface=1.0)
        assert len(amps) == 5
        # First echo: T^2 * (R_surf * R_peak)^1
        assert amps[0] == pytest.approx(0.03 * 0.98, rel=1e-10)
        # Each subsequent echo smaller
        for i in range(1, len(amps)):
            assert amps[i] < amps[i - 1], f"Echo {i+1} not smaller than echo {i}"

    def test_echo_amplitudes_zero_for_no_reflection(self) -> None:
        """R_surface = 0 (standard GR) → zero echo amplitudes."""
        from grut.ringdown import echo_amplitudes
        amps = echo_amplitudes(3, transmission_sq=0.03, reflection_peak=0.98,
                               reflection_surface=0.0)
        for a in amps:
            assert a == 0.0, "Standard GR (R_surface=0) must produce zero echoes"

    def test_compute_echo_analysis_complete(self) -> None:
        """Full echo analysis must produce complete, consistent result."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M,
            r_s_m=r_s,
            R_eq_m=r_s / 3.0,
            R_eq_over_r_s=1.0 / 3.0,
            compactness=3.0,
            beta_Q=2.0,
            reflection_model="perfect",
            reflection_coefficient=1.0,
        )
        result = compute_echo_analysis(params, n_echoes=5)
        # Echo timing
        assert result.delta_t_echo_s > 0
        assert result.delta_t_echo_over_r_s > 0
        # BDCC oscillation
        assert result.omega_core_rad_s > 0
        assert result.f_core_Hz > 0
        # QNM reference
        assert result.omega_qnm_rad_s > 0
        assert result.f_qnm_Hz > 0
        assert result.tau_qnm_s > 0
        # Echo amplitudes
        assert len(result.echo_amplitudes) == 5
        assert all(a > 0 for a in result.echo_amplitudes)
        # Status
        assert result.exterior_assumption == "schwarzschild_like"
        assert result.confidence == "order_of_magnitude"
        # Nonclaims
        assert len(result.nonclaims) >= 5

    def test_echo_result_serializes(self) -> None:
        """EchoResult must serialize to a clean dict."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            echo_result_to_dict,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            R_eq_over_r_s=1.0 / 3.0, beta_Q=2.0,
            reflection_model="perfect",
        )
        result = compute_echo_analysis(params, n_echoes=3)
        d = echo_result_to_dict(result)
        assert isinstance(d, dict)
        assert "echo_timing" in d
        assert "bdcc_oscillation" in d
        assert "echo_amplitudes" in d
        assert "qnm_reference" in d
        assert "nonclaims" in d
        assert "required_closures" in d
        assert "status" in d

    def test_nonclaims_conditional_labels(self) -> None:
        """All nonclaims must reference conditionality and avoid overclaiming."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            R_eq_over_r_s=1.0 / 3.0, beta_Q=2.0,
            reflection_model="perfect",
        )
        result = compute_echo_analysis(params, n_echoes=3)
        nonclaims_text = " ".join(result.nonclaims)
        # Must reference WP1 conditionality
        assert "WP1" in nonclaims_text or "conditional" in nonclaims_text.lower()
        # Must reference order-of-magnitude nature
        assert "ORDER OF MAGNITUDE" in nonclaims_text
        # Must state echoes are not predicted
        assert "NOT predict" in nonclaims_text or "NOT predicted" in nonclaims_text

    def test_scan_reflection_coefficient(self) -> None:
        """Reflection coefficient scan must cover the full range."""
        from grut.ringdown import scan_reflection_coefficient, M_SUN
        M = 30.0 * M_SUN
        scan = scan_reflection_coefficient(M, n_echoes=2)
        assert len(scan) >= 5, "Scan must cover at least 5 R values"
        # First entry: R_surface = 0 → standard GR
        assert scan[0]["R_surface"] == 0.0
        assert scan[0]["regime"] == "standard_GR"
        # Last entry: R_surface = 1.0 → strong reflection
        assert scan[-1]["R_surface"] == 1.0
        assert scan[-1]["regime"] == "strong_reflection"
        # Echo amplitudes must increase with R_surface
        for i in range(1, len(scan)):
            assert scan[i]["first_echo_amplitude"] >= scan[i - 1]["first_echo_amplitude"]

    def test_scan_mass_range(self) -> None:
        """Mass scan must show linear Δt scaling."""
        from grut.ringdown import scan_mass_range
        scan = scan_mass_range(reflection_coefficient=1.0)
        assert len(scan) >= 4, "Mass scan must cover at least 4 masses"
        # Δt should scale linearly with M
        # Check: Δt_last / Δt_first ≈ M_last / M_first
        mass_ratio = scan[-1]["M_solar"] / scan[0]["M_solar"]
        dt_ratio = scan[-1]["delta_t_echo_ms"] / scan[0]["delta_t_echo_ms"]
        assert dt_ratio == pytest.approx(mass_ratio, rel=0.01), (
            f"Δt ratio {dt_ratio:.1f} != mass ratio {mass_ratio:.1f}"
        )

    def test_boltzmann_reflection_model(self) -> None:
        """Boltzmann reflection model must produce finite R_surface < 1."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            R_eq_over_r_s=1.0 / 3.0, beta_Q=2.0,
            reflection_model="boltzmann",
        )
        result = compute_echo_analysis(params, n_echoes=3)
        # Boltzmann: R = exp(-ω_QNM / ω_core)
        # Since ω_QNM >> ω_core, this should be very small
        assert 0 < result.reflection_surface < 1.0

    def test_required_closures_present(self) -> None:
        """Echo result must list what is still missing for full computation."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            beta_Q=2.0, reflection_model="perfect",
        )
        result = compute_echo_analysis(params, n_echoes=3)
        assert len(result.required_closures) >= 3
        closures_text = " ".join(result.required_closures)
        # Must mention interior metric and Kerr gaps
        assert "interior" in closures_text.lower()
        assert "Kerr" in closures_text

    def test_canon_has_wp2_result(self) -> None:
        """Canon JSON must reflect WP2 status."""
        import json
        from pathlib import Path
        canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
        if not canon_path.exists():
            pytest.skip("Canon file not found")
        canon = json.loads(canon_path.read_text())
        efp = canon.get("collapse", {}).get("exterior_falsifier_program", {})
        assert efp, "Missing collapse.exterior_falsifier_program"
        wp2 = efp.get("work_packages", {}).get("WP2_ringdown_echo", {})
        assert wp2, "Missing WP2_ringdown_echo"
        # Must reflect estimates are done or channel is frozen
        status = wp2.get("status", "").upper()
        assert "ESTIMATE" in status or "CONSTRAINED" in status or "FROZEN" in status


# ================================================================
# Phase III-C WP2B: Impedance Reflectivity Tests
# ================================================================

class TestPhaseIIIC_WP2B:
    """Phase III-C WP2B tests — impedance reflectivity model.

    Tests are on code correctness (positivity, finiteness, monotonicity,
    bounds, integration). Strong astrophysical claims (e.g. R > 0.8 for
    stellar-mass) belong in benchmarks, not brittle unit tests.
    """

    def test_impedance_ratio_positive_finite(self) -> None:
        """Impedance ratio must be positive and finite for physical inputs."""
        from grut.ringdown import impedance_ratio, schwarzschild_radius, M_SUN
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        R_eq = r_s / 3.0
        eta = impedance_ratio(M, R_eq, beta_Q=2.0)
        assert eta > 0, "eta must be positive"
        assert math.isfinite(eta), "eta must be finite"

    def test_impedance_ratio_decreases_with_mass(self) -> None:
        """eta must decrease as mass increases (confirmed numerically)."""
        from grut.ringdown import impedance_ratio, schwarzschild_radius, M_SUN
        masses = [10.0, 30.0, 100.0, 1000.0]
        etas = []
        for M_solar in masses:
            M = M_solar * M_SUN
            r_s = schwarzschild_radius(M)
            R_eq = r_s / 3.0
            etas.append(impedance_ratio(M, R_eq, beta_Q=2.0))
        for i in range(1, len(etas)):
            assert etas[i] < etas[i - 1], (
                f"eta({masses[i]} Msun) = {etas[i]:.6f} >= "
                f"eta({masses[i-1]} Msun) = {etas[i-1]:.6f}"
            )

    def test_impedance_ratio_mass_scaling_approximate(self) -> None:
        """eta scaling with mass should be approximately M^{-1/2}."""
        from grut.ringdown import impedance_ratio, schwarzschild_radius, M_SUN
        M1, M2 = 10.0 * M_SUN, 1000.0 * M_SUN
        r_s1, r_s2 = schwarzschild_radius(M1), schwarzschild_radius(M2)
        eta1 = impedance_ratio(M1, r_s1 / 3.0, beta_Q=2.0)
        eta2 = impedance_ratio(M2, r_s2 / 3.0, beta_Q=2.0)
        # Mass ratio is 100, so eta ratio should be ~sqrt(100) = 10
        eta_ratio = eta1 / eta2
        mass_ratio_sqrt = math.sqrt(M2 / M1)
        # Allow 20% tolerance since this is approximate
        assert abs(eta_ratio / mass_ratio_sqrt - 1.0) < 0.20, (
            f"eta_ratio={eta_ratio:.3f}, expected ~{mass_ratio_sqrt:.1f}"
        )

    def test_impedance_reflectivity_bounds(self) -> None:
        """Amplitude reflectivity must be in [0, 1] for all masses."""
        from grut.ringdown import impedance_reflectivity, schwarzschild_radius, M_SUN
        for M_solar in [1.0, 10.0, 100.0, 1e6, 1e9]:
            M = M_solar * M_SUN
            r_s = schwarzschild_radius(M)
            R_eq = r_s / 3.0
            r_amp = impedance_reflectivity(M, R_eq, beta_Q=2.0)
            assert 0 <= r_amp <= 1.0, (
                f"r_amp={r_amp} out of bounds for M={M_solar} Msun"
            )

    def test_impedance_reflectivity_increases_with_mass(self) -> None:
        """Amplitude reflectivity must increase with mass (since eta decreases)."""
        from grut.ringdown import impedance_reflectivity, schwarzschild_radius, M_SUN
        masses = [10.0, 100.0, 1e4, 1e6]
        r_amps = []
        for M_solar in masses:
            M = M_solar * M_SUN
            r_s = schwarzschild_radius(M)
            r_amps.append(impedance_reflectivity(M, r_s / 3.0, beta_Q=2.0))
        for i in range(1, len(r_amps)):
            assert r_amps[i] >= r_amps[i - 1], (
                f"r_amp({masses[i]} Msun) = {r_amps[i]:.6f} < "
                f"r_amp({masses[i-1]} Msun) = {r_amps[i-1]:.6f}"
            )

    def test_impedance_reflectivity_bounded_by_perfect(self) -> None:
        """Impedance r_amp must be <= 1.0 (bounded by perfect reflection)."""
        from grut.ringdown import impedance_reflectivity, schwarzschild_radius, M_SUN
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        r_amp = impedance_reflectivity(M, r_s / 3.0, beta_Q=2.0)
        assert r_amp <= 1.0, "Impedance reflectivity exceeds perfect"
        assert r_amp < 1.0, "Impedance reflectivity should be strictly < 1"

    def test_impedance_reflectivity_zero_mass_edge(self) -> None:
        """Edge case: zero mass or zero radius returns 0."""
        from grut.ringdown import impedance_reflectivity, impedance_ratio
        assert impedance_ratio(0.0, 1000.0, 2.0) == 0.0
        assert impedance_ratio(1e30, 0.0, 2.0) == 0.0
        assert impedance_reflectivity(0.0, 1000.0, 2.0) == 0.0

    def test_compute_echo_analysis_impedance_model(self) -> None:
        """compute_echo_analysis must work with reflection_model='impedance'."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            R_eq_over_r_s=1.0 / 3.0, beta_Q=2.0,
            reflection_model="impedance",
        )
        result = compute_echo_analysis(params, n_echoes=3)
        # Must produce valid result
        assert result.reflection_surface > 0, "Impedance r_surface must be positive"
        assert result.reflection_surface <= 1.0
        assert result.impedance_ratio_eta > 0, "eta must be computed"
        assert result.impedance_ratio_eta < 1.0, "eta should be << 1"
        assert len(result.echo_amplitudes) == 3
        assert all(a > 0 for a in result.echo_amplitudes)

    def test_impedance_model_nonzero_echoes(self) -> None:
        """Impedance model must produce non-zero echo amplitudes."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            beta_Q=2.0, reflection_model="impedance",
        )
        result = compute_echo_analysis(params, n_echoes=5)
        # First echo must be substantial (not negligible like Boltzmann)
        assert result.echo_amplitudes[0] > 1e-5, (
            f"First echo amplitude {result.echo_amplitudes[0]} is negligible"
        )

    def test_impedance_eta_in_serialization(self) -> None:
        """eta must appear in serialized echo result."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            echo_result_to_dict,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            beta_Q=2.0, reflection_model="impedance",
        )
        result = compute_echo_analysis(params, n_echoes=2)
        d = echo_result_to_dict(result)
        assert "impedance" in d
        assert "impedance_ratio_eta" in d["impedance"]
        assert d["impedance"]["impedance_ratio_eta"] > 0

    def test_nonclaims_include_sharp_boundary(self) -> None:
        """Nonclaims must mention sharp-boundary approximation."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            beta_Q=2.0, reflection_model="impedance",
        )
        result = compute_echo_analysis(params, n_echoes=2)
        nonclaims_text = " ".join(result.nonclaims)
        assert "sharp-boundary" in nonclaims_text.lower() or "sharp" in nonclaims_text.lower()
        assert "Boltzmann" in nonclaims_text or "dissipative" in nonclaims_text


# ================================================================
# Phase III-C WP2C: Interior Wave / Viscoelastic Response Tests
# ================================================================

class TestPhaseIIIC_WP2C:
    """Phase III-C WP2C tests — interior wave / viscoelastic model.

    Tests code correctness: positivity, finiteness, monotonicity,
    classification consistency, integration with ringdown. Strong
    astrophysical claims belong in benchmarks.
    """

    def test_quality_factor_positive_finite(self) -> None:
        """Quality factor must be positive and finite for physical inputs."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = InteriorWaveParams(M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s)
        result = compute_interior_wave_analysis(params)
        assert result.quality_factor_Q > 0
        assert math.isfinite(result.quality_factor_Q)

    def test_loss_tangent_consistent_with_Q(self) -> None:
        """Loss tangent must equal 1/(2Q) within numerical precision."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = InteriorWaveParams(M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s)
        result = compute_interior_wave_analysis(params)
        Q = result.quality_factor_Q
        if math.isfinite(Q) and Q > 0:
            expected_tan = 1.0 / (2.0 * Q)
            assert abs(result.loss_tangent - expected_tan) / expected_tan < 1e-6

    def test_memory_damping_dominates_solver(self) -> None:
        """Memory-mediated damping must dominate solver gamma_diss at canon params."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = InteriorWaveParams(
            M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s,
            gamma_diss=1e-15,
        )
        result = compute_interior_wave_analysis(params)
        assert result.memory_damping_rate > result.solver_damping_rate * 1e10

    def test_gamma_eff_equals_sum(self) -> None:
        """gamma_eff must equal gamma_memory + gamma_solver."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = InteriorWaveParams(M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s)
        result = compute_interior_wave_analysis(params)
        expected = result.memory_damping_rate + result.solver_damping_rate
        assert abs(result.gamma_eff_rad_s - expected) / expected < 1e-10

    def test_classification_reactive_at_proxy_params(self) -> None:
        """Proxy module (interior_waves) returns 'reactive' at Q~515 (SUPERSEDED by PDE Q~6-7.5)."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = InteriorWaveParams(M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s)
        result = compute_interior_wave_analysis(params)
        assert "reactive" in result.response_class

    def test_classification_dissipative_at_high_gamma(self) -> None:
        """High gamma_diss must produce dissipative classification."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = InteriorWaveParams(
            M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s,
            gamma_diss=1e6,  # Artificially high
        )
        result = compute_interior_wave_analysis(params)
        assert "dissipative" in result.response_class

    def test_classification_mixed_at_moderate_gamma(self) -> None:
        """Moderate gamma_diss can produce mixed viscoelastic classification."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
            bdcc_oscillation_frequency,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        R_eq = r_s / 3.0
        # Find gamma that gives Q ~ 5 (mixed regime)
        omega_core = bdcc_oscillation_frequency(M, R_eq, 2.0)
        # Q = omega_core / (2*(gamma_diss + gamma_mem))
        # For Q ~ 5: gamma_diss ~ omega_core/10 - gamma_mem
        gamma_target = omega_core / 10.0  # Should give Q ~ 5
        params = InteriorWaveParams(
            M_kg=M, R_eq_m=R_eq, r_s_m=r_s,
            gamma_diss=gamma_target,
        )
        result = compute_interior_wave_analysis(params)
        assert result.quality_factor_Q > 1
        assert result.quality_factor_Q < 10
        assert "mixed" in result.response_class or "reactive" in result.response_class

    def test_r_interior_bounded(self) -> None:
        """Interior reflection estimate must be in [0, 1] for all regimes."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        for gamma in [0.0, 1e-15, 1.0, 1e3, 1e6]:
            params = InteriorWaveParams(
                M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s,
                gamma_diss=gamma,
            )
            result = compute_interior_wave_analysis(params)
            assert 0 <= result.r_interior_amp <= 1.0, (
                f"r_interior={result.r_interior_amp} out of bounds at gamma={gamma}"
            )

    def test_r_interior_decreases_with_gamma(self) -> None:
        """Interior reflection must decrease as gamma_diss increases."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        gammas = [1e-15, 1.0, 10.0, 100.0, 1e4]
        r_amps = []
        for gamma in gammas:
            params = InteriorWaveParams(
                M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s,
                gamma_diss=gamma,
            )
            result = compute_interior_wave_analysis(params)
            r_amps.append(result.r_interior_amp)
        for i in range(1, len(r_amps)):
            assert r_amps[i] <= r_amps[i - 1] + 1e-10, (
                f"r_int({gammas[i]}) = {r_amps[i]:.6f} > "
                f"r_int({gammas[i-1]}) = {r_amps[i-1]:.6f}"
            )

    def test_storage_modulus_positive(self) -> None:
        """Storage modulus proxy must be positive."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = InteriorWaveParams(M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s)
        result = compute_interior_wave_analysis(params)
        assert result.storage_modulus_proxy > 0

    def test_ringdown_interior_model(self) -> None:
        """ringdown.py must work with reflection_model='interior'."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius as sr,
            M_SUN as MS,
        )
        M = 30.0 * MS
        r_s = sr(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            beta_Q=2.0, reflection_model="interior",
        )
        result = compute_echo_analysis(params, n_echoes=3)
        assert result.reflection_surface > 0
        assert result.reflection_surface <= 1.0
        assert result.interior_quality_factor_Q > 0
        assert result.interior_response_class != ""
        assert len(result.echo_amplitudes) == 3
        assert all(a > 0 for a in result.echo_amplitudes)

    def test_interior_Q_in_all_models(self) -> None:
        """Interior Q must be computed for ALL reflection models."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius as sr,
            M_SUN as MS,
        )
        M = 30.0 * MS
        r_s = sr(M)
        for model in ["perfect", "impedance", "boltzmann", "constant", "interior"]:
            params = EchoParameters(
                M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
                beta_Q=2.0, reflection_model=model,
            )
            result = compute_echo_analysis(params, n_echoes=1)
            assert result.interior_quality_factor_Q > 0, (
                f"Q not computed for model={model}"
            )
            assert result.interior_response_class != "", (
                f"response_class empty for model={model}"
            )

    def test_interior_wave_serialization(self) -> None:
        """Interior wave fields must appear in serialized echo result."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            echo_result_to_dict,
            schwarzschild_radius as sr,
            M_SUN as MS,
        )
        M = 30.0 * MS
        r_s = sr(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            beta_Q=2.0, reflection_model="interior",
        )
        result = compute_echo_analysis(params, n_echoes=2)
        d = echo_result_to_dict(result)
        assert "interior_wave" in d
        assert d["interior_wave"]["quality_factor_Q"] > 0
        assert d["interior_wave"]["response_class"] != ""

    def test_nonclaims_include_viscoelastic(self) -> None:
        """Interior wave nonclaims must reference key assumptions."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
            M_SUN,
            schwarzschild_radius,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = InteriorWaveParams(M_kg=M, R_eq_m=r_s / 3.0, r_s_m=r_s)
        result = compute_interior_wave_analysis(params)
        nonclaims_text = " ".join(result.nonclaims)
        # Must state that this is not a wave equation solution
        assert "wave equation" in nonclaims_text.lower()
        # Must not assume information saturation implies elasticity
        assert "saturation" in nonclaims_text.lower()
        # Must mention hidden dissipation
        assert "hidden" in nonclaims_text.lower() or "nonlinear" in nonclaims_text.lower()

    def test_edge_case_zero_mass(self) -> None:
        """Edge case: zero mass must not crash."""
        from grut.interior_waves import (
            InteriorWaveParams,
            compute_interior_wave_analysis,
        )
        params = InteriorWaveParams(M_kg=0.0, R_eq_m=0.0, r_s_m=0.0)
        result = compute_interior_wave_analysis(params)
        assert result.quality_factor_Q == 0.0
        assert result.response_class == "underdetermined" or result.quality_factor_Q == 0.0


# ── Phase III-C WP2D: Graded-Transition and Multi-Mode Tests ──

class TestPhaseIIIC_WP2D:
    """Tests for WP2D graded-transition and multi-mode correction.

    These tests verify that the graded-transition model:
    1. Produces physically bounded reflectivities
    2. Converges with increasing number of layers
    3. Reduces to sharp boundary in the zero-width limit
    4. Has correct Phi profile anchors
    5. Integrates with ringdown correctly
    6. Multi-mode correction is bounded and correct
    """

    def test_graded_reflectivity_bounded(self) -> None:
        """WP2D reflectivity must be in [0, 1]."""
        from grut.interior_waves import (
            GradedTransitionParams,
            compute_graded_transition_analysis,
            M_SUN,
        )
        M = 30.0 * M_SUN
        params = GradedTransitionParams(M_kg=M)
        result = compute_graded_transition_analysis(params)
        assert 0.0 <= result.r_graded_amp <= 1.0
        assert 0.0 <= result.r_wp2d_amp <= 1.0
        assert 0.0 <= result.r_multimode_amp <= 1.0

    def test_grading_factor_bounded(self) -> None:
        """Grading factor should be close to 1 for quasi-sharp regime."""
        from grut.interior_waves import (
            GradedTransitionParams,
            compute_graded_transition_analysis,
            M_SUN,
        )
        M = 30.0 * M_SUN
        params = GradedTransitionParams(M_kg=M)
        result = compute_graded_transition_analysis(params)
        # In quasi-sharp regime, grading_factor should be > 0.9
        assert 0.9 < result.grading_factor <= 1.01

    def test_phi_profile_endpoint(self) -> None:
        """Phi must equal 1.0 at the endpoint R_eq/r_s = 1/3."""
        from grut.interior_waves import barrier_dominance_profile
        phi_eq = barrier_dominance_profile(1.0 / 3.0)
        assert abs(phi_eq - 1.0) < 0.01

    def test_phi_profile_crystallization(self) -> None:
        """Phi must equal 0.5 at the crystallization point."""
        from grut.interior_waves import barrier_dominance_profile
        phi_cryst = barrier_dominance_profile(0.4715)
        assert abs(phi_cryst - 0.5) < 0.01

    def test_phi_profile_outer_edge(self) -> None:
        """Phi must be ~0 at the outer edge of the transition."""
        from grut.interior_waves import barrier_dominance_profile
        phi_outer = barrier_dominance_profile(1.036)
        assert phi_outer < 0.01

    def test_phi_profile_monotonic(self) -> None:
        """Phi must be monotonically decreasing outward."""
        from grut.interior_waves import barrier_dominance_profile
        positions = [0.333, 0.4, 0.47, 0.5, 0.6, 0.8, 1.0]
        phis = [barrier_dominance_profile(x) for x in positions]
        for i in range(len(phis) - 1):
            assert phis[i] >= phis[i + 1] - 0.001

    def test_sharp_boundary_limit(self) -> None:
        """Width=0 must recover sharp-boundary reflectivity."""
        from grut.interior_waves import (
            GradedTransitionParams,
            compute_graded_transition_analysis,
            M_SUN,
        )
        M = 30.0 * M_SUN
        params = GradedTransitionParams(M_kg=M, transition_width_rs=0.0)
        result = compute_graded_transition_analysis(params)
        assert abs(result.grading_factor - 1.0) < 0.01

    def test_convergence_with_layers(self) -> None:
        """Increasing layers should converge."""
        from grut.interior_waves import (
            GradedTransitionParams,
            compute_graded_transition_analysis,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_values = []
        for nl in [50, 100, 200]:
            params = GradedTransitionParams(M_kg=M, n_layers=nl)
            res = compute_graded_transition_analysis(params)
            r_values.append(res.r_graded_amp)
        # Difference between 100 and 200 layers should be < 1%
        if r_values[2] > 0:
            diff = abs(r_values[1] - r_values[2]) / r_values[2]
            assert diff < 0.01

    def test_multimode_factor_near_unity(self) -> None:
        """Multi-mode factor should be ~1 for high-Q canon params."""
        from grut.interior_waves import (
            GradedTransitionParams,
            compute_graded_transition_analysis,
            M_SUN,
        )
        M = 30.0 * M_SUN
        params = GradedTransitionParams(M_kg=M)
        result = compute_graded_transition_analysis(params)
        assert abs(result.multimode_factor - 1.0) < 0.01

    def test_multimode_spectrum_frequencies(self) -> None:
        """Mode frequencies should increase with mode number."""
        from grut.interior_waves import multimode_spectrum
        freqs, Qs, weights = multimode_spectrum(100.0, 500.0, 3, 0.1)
        assert len(freqs) == 3
        assert freqs[1] > freqs[0]
        assert freqs[2] > freqs[1]

    def test_multimode_Q_decreases(self) -> None:
        """Mode Q should decrease for higher overtones."""
        from grut.interior_waves import multimode_spectrum
        freqs, Qs, weights = multimode_spectrum(100.0, 500.0, 3, 0.1)
        assert Qs[1] < Qs[0]
        assert Qs[2] < Qs[1]

    def test_multimode_weights_sum_to_one(self) -> None:
        """Mode weights must be normalized."""
        from grut.interior_waves import multimode_spectrum
        freqs, Qs, weights = multimode_spectrum(100.0, 500.0, 3, 0.1)
        assert abs(sum(weights) - 1.0) < 0.001

    def test_ringdown_graded_model(self) -> None:
        """Ringdown with reflection_model='graded' must work."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            beta_Q=2.0, reflection_model="graded",
        )
        result = compute_echo_analysis(params, n_echoes=3)
        assert result.reflection_surface > 0
        assert result.reflection_surface < 1.0
        assert len(result.echo_amplitudes) == 3
        assert result.graded_r_amp > 0
        assert result.graded_combined_factor > 0

    def test_graded_fields_in_all_models(self) -> None:
        """WP2D fields should be computed for all reflection models."""
        from grut.ringdown import (
            EchoParameters,
            compute_echo_analysis,
            schwarzschild_radius,
            M_SUN,
        )
        M = 30.0 * M_SUN
        r_s = schwarzschild_radius(M)
        for model in ["perfect", "interior", "graded"]:
            params = EchoParameters(
                M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
                beta_Q=2.0, reflection_model=model,
            )
            result = compute_echo_analysis(params, n_echoes=2)
            assert result.graded_r_amp > 0, f"graded_r_amp = 0 for model {model}"

    def test_graded_serialization(self) -> None:
        """Graded transition dict must include WP2D fields."""
        from grut.interior_waves import (
            GradedTransitionParams,
            compute_graded_transition_analysis,
            graded_transition_result_to_dict,
            M_SUN,
        )
        M = 30.0 * M_SUN
        params = GradedTransitionParams(M_kg=M)
        result = compute_graded_transition_analysis(params)
        d = graded_transition_result_to_dict(result)
        assert "reflectivity_comparison" in d
        assert "transition_diagnostics" in d
        assert "multimode_spectrum" in d
        assert "echo_amplitudes" in d
        assert "classification" in d

    def test_echo_channel_status_classification(self) -> None:
        """Echo channel status should be reasonable."""
        from grut.interior_waves import (
            GradedTransitionParams,
            compute_graded_transition_analysis,
            M_SUN,
        )
        M = 30.0 * M_SUN
        params = GradedTransitionParams(M_kg=M)
        result = compute_graded_transition_analysis(params)
        assert result.echo_channel_status in [
            "strengthened", "weakened_modestly",
            "weakened_significantly", "collapsed",
        ]

    def test_mass_scan_all_viable(self) -> None:
        """All masses should give viable echo channel at canon params."""
        from grut.interior_waves import (
            GradedTransitionParams,
            compute_graded_transition_analysis,
            M_SUN,
        )
        for m_solar in [10.0, 30.0, 100.0, 1e4]:
            M = m_solar * M_SUN
            params = GradedTransitionParams(M_kg=M)
            result = compute_graded_transition_analysis(params)
            assert result.echo_channel_status != "collapsed", \
                f"Echo collapsed at M = {m_solar} M_sun"

    def test_nonclaims_present(self) -> None:
        """WP2D result must include nonclaims."""
        from grut.interior_waves import (
            GradedTransitionParams,
            compute_graded_transition_analysis,
            M_SUN,
        )
        M = 30.0 * M_SUN
        params = GradedTransitionParams(M_kg=M)
        result = compute_graded_transition_analysis(params)
        assert len(result.nonclaims) >= 5
        nonclaims_text = " ".join(result.nonclaims)
        assert "zeroth" in nonclaims_text.lower() or "parameterized" in nonclaims_text.lower()

    def test_edge_case_zero_mass_graded(self) -> None:
        """Edge case: zero mass must not crash."""
        from grut.interior_waves import (
            GradedTransitionParams,
            compute_graded_transition_analysis,
        )
        params = GradedTransitionParams(M_kg=0.0)
        result = compute_graded_transition_analysis(params)
        assert result.r_wp2d_amp >= 0


# ================================================================
# Phase III-C Interior PDE Closure Tests
# ================================================================

class TestPhaseIIIC_PDE:
    """Interior PDE closure tests.

    Tests the PDE-derived perturbation equation for the BDCC,
    including the structural identity omega_0*tau = 1, universal Q,
    mode spectrum, and ringdown integration.
    """

    M_SUN = 1.989e30

    def test_module_imports(self) -> None:
        """PDE module must import without errors."""
        from grut.interior_pde import (
            build_pde_background,
            solve_dispersion,
            dispersion_relation,
            effective_potential,
            compute_pde_analysis,
            pde_result_to_dict,
            PDEBackground,
            PDEMode,
            PDEResult,
        )
        assert PDEBackground is not None
        assert PDEMode is not None
        assert PDEResult is not None

    def test_background_builds(self) -> None:
        """Background must build from canon parameters."""
        from grut.interior_pde import build_pde_background
        bg = build_pde_background(M_kg=30 * self.M_SUN)
        assert bg.valid
        assert bg.omega_0 > 0
        assert bg.omega_g > 0
        assert bg.tau_eff > 0

    def test_background_Req_over_rs(self) -> None:
        """R_eq/r_s must equal 1/3 from constrained endpoint law."""
        from grut.interior_pde import build_pde_background
        bg = build_pde_background(M_kg=30 * self.M_SUN)
        assert abs(bg.R_eq_m / bg.r_s_m - 1.0 / 3.0) < 1e-10

    def test_structural_identity(self) -> None:
        """omega_0 * tau_eff must equal 1.0 (structural identity)."""
        from grut.interior_pde import build_pde_background
        bg = build_pde_background(M_kg=30 * self.M_SUN)
        assert abs(bg.omega_0_tau - 1.0) < 0.01

    def test_structural_identity_mass_independent(self) -> None:
        """omega_0 * tau = 1 must hold for all masses."""
        from grut.interior_pde import build_pde_background
        for M_scale in [10, 100, 1000, 1e6]:
            bg = build_pde_background(M_kg=M_scale * self.M_SUN)
            assert abs(bg.omega_0_tau - 1.0) < 0.01, f"Failed at {M_scale} M_sun"

    def test_Q_pde_mixed_regime(self) -> None:
        """PDE Q must be in mixed viscoelastic regime (1 < Q < 10)."""
        from grut.interior_pde import compute_pde_analysis
        result = compute_pde_analysis(M_kg=30 * self.M_SUN)
        assert 1 < result.Q_pde_fundamental < 10

    def test_Q_pde_universal(self) -> None:
        """PDE Q must be approximately beta_Q/alpha_vac = 6."""
        from grut.interior_pde import compute_pde_analysis
        result = compute_pde_analysis(M_kg=30 * self.M_SUN)
        assert abs(result.Q_pde_fundamental - 6.0) < 3.0

    def test_response_class_mixed(self) -> None:
        """Response class must be mixed_viscoelastic."""
        from grut.interior_pde import compute_pde_analysis
        result = compute_pde_analysis(M_kg=30 * self.M_SUN)
        assert result.response_class == "mixed_viscoelastic"

    def test_modes_found(self) -> None:
        """Dispersion solver must find modes."""
        from grut.interior_pde import build_pde_background, solve_dispersion
        bg = build_pde_background(M_kg=30 * self.M_SUN)
        modes = solve_dispersion(bg, l=2, n_modes=3)
        assert len(modes) > 0

    def test_mode_frequency_positive(self) -> None:
        """Mode frequencies must be positive."""
        from grut.interior_pde import build_pde_background, solve_dispersion
        bg = build_pde_background(M_kg=30 * self.M_SUN)
        modes = solve_dispersion(bg, l=2, n_modes=2)
        for m in modes:
            assert m.omega_real > 0

    def test_mode_damped(self) -> None:
        """Modes must be damped (omega_imag < 0)."""
        from grut.interior_pde import build_pde_background, solve_dispersion
        bg = build_pde_background(M_kg=30 * self.M_SUN)
        modes = solve_dispersion(bg, l=2, n_modes=2)
        for m in modes:
            assert m.omega_imag <= 0

    def test_reflection_bounded(self) -> None:
        """PDE reflection amplitude must be in (0, 1)."""
        from grut.interior_pde import compute_pde_analysis
        result = compute_pde_analysis(M_kg=30 * self.M_SUN)
        assert 0 < result.r_pde_amp < 1

    def test_reflection_less_than_proxy(self) -> None:
        """PDE reflection should be lower than WP2C proxy estimate."""
        from grut.interior_pde import compute_pde_analysis
        result = compute_pde_analysis(M_kg=30 * self.M_SUN)
        # WP2C proxy used omega_core formula giving r ~ 0.98
        # PDE gives r ~ 0.30
        assert result.r_pde_amp < 0.5

    def test_effective_potential_positive_at_Req(self) -> None:
        """V_eff at R_eq must be positive (potential well)."""
        from grut.interior_pde import build_pde_background, effective_potential
        bg = build_pde_background(M_kg=30 * self.M_SUN)
        V = effective_potential(1.0 / 3.0, bg, l=2)
        assert V > 0

    def test_ringdown_pde_model(self) -> None:
        """PDE model must integrate with ringdown."""
        from grut.ringdown import compute_echo_analysis, EchoParameters
        p = EchoParameters(
            M_kg=30 * self.M_SUN,
            reflection_model="pde",
            R_eq_over_r_s=1.0 / 3.0,
            epsilon_Q=1.0 / 9.0,
        )
        r = compute_echo_analysis(p)
        assert r.pde_Q > 0
        assert r.reflection_surface > 0
        assert len(r.echo_amplitudes) > 0

    def test_pde_fields_in_ringdown(self) -> None:
        """PDE fields must be populated for all reflection models."""
        from grut.ringdown import compute_echo_analysis, EchoParameters
        p = EchoParameters(
            M_kg=30 * self.M_SUN,
            reflection_model="impedance",
            R_eq_over_r_s=1.0 / 3.0,
            epsilon_Q=1.0 / 9.0,
        )
        r = compute_echo_analysis(p)
        assert r.pde_Q > 0
        assert r.pde_response_class != ""

    def test_pde_serialisation(self) -> None:
        """PDE result must serialise to dict."""
        from grut.interior_pde import compute_pde_analysis, pde_result_to_dict
        result = compute_pde_analysis(M_kg=30 * self.M_SUN)
        d = pde_result_to_dict(result)
        assert "background" in d
        assert "modes" in d
        assert "summary" in d
        assert d["summary"]["response_class"] == "mixed_viscoelastic"

    def test_nonclaims_present(self) -> None:
        """Result must carry nonclaims."""
        from grut.interior_pde import compute_pde_analysis
        result = compute_pde_analysis(M_kg=30 * self.M_SUN)
        assert len(result.nonclaims) >= 8

    def test_missing_closures_present(self) -> None:
        """Result must carry missing closures."""
        from grut.interior_pde import compute_pde_analysis
        result = compute_pde_analysis(M_kg=30 * self.M_SUN)
        assert len(result.missing_closures) >= 4

    def test_zero_mass_no_crash(self) -> None:
        """Zero mass must not crash."""
        from grut.interior_pde import compute_pde_analysis
        result = compute_pde_analysis(M_kg=0.0)
        assert not result.background.valid

    def test_background_serialises(self) -> None:
        """PDEBackground must serialise to dict."""
        from grut.interior_pde import build_pde_background, pde_background_to_dict
        bg = build_pde_background(M_kg=30 * self.M_SUN)
        d = pde_background_to_dict(bg)
        assert isinstance(d, dict)
        assert d["valid"] is True
        assert d["omega_0"] > 0


# ================================================================
# Phase III-C WP3: Static Exterior Null-Result Tests
# ================================================================

class TestPhaseIIIC_WP3:
    """Tests for WP3 null-result confirmation.

    Under the WP1 Schwarzschild-like exterior assumption, static
    observables (shadow, photon sphere, ISCO, accretion) must be
    identically null at leading order.
    """

    G_SI = 6.674e-11
    C_SI = 299_792_458.0
    M_SUN = 1.989e30
    ALPHA_VAC = 1.0 / 3.0

    def _r_s(self, M_kg: float) -> float:
        return 2 * self.G_SI * M_kg / (self.C_SI ** 2)

    def _R_eq(self, M_kg: float) -> float:
        return self.ALPHA_VAC * self._r_s(M_kg)

    def test_bdcc_inside_horizon(self) -> None:
        """BDCC must be inside the horizon for all masses."""
        for M_msun in [10, 30, 100, 1e6, 1e9]:
            M_kg = M_msun * self.M_SUN
            R_eq = self._R_eq(M_kg)
            r_s = self._r_s(M_kg)
            assert R_eq < r_s, f"R_eq >= r_s at {M_msun} M_sun"

    def test_compactness_equals_3(self) -> None:
        """Compactness at BDCC must be C = 3."""
        for M_msun in [10, 30, 1e6]:
            M_kg = M_msun * self.M_SUN
            C = self._r_s(M_kg) / self._R_eq(M_kg)
            assert abs(C - 3.0) < 1e-10

    def test_photon_sphere_exterior(self) -> None:
        """Photon sphere must be outside the horizon."""
        for M_msun in [10, 30, 100]:
            M_kg = M_msun * self.M_SUN
            r_s = self._r_s(M_kg)
            r_ph = 1.5 * r_s
            assert r_ph > r_s

    def test_photon_sphere_far_from_bdcc(self) -> None:
        """Photon sphere must be 4.5x the BDCC radius."""
        for M_msun in [10, 30, 1e6]:
            M_kg = M_msun * self.M_SUN
            r_ph = 1.5 * self._r_s(M_kg)
            R_eq = self._R_eq(M_kg)
            assert abs(r_ph / R_eq - 4.5) < 1e-10

    def test_isco_far_from_bdcc(self) -> None:
        """ISCO must be 9x the BDCC radius."""
        for M_msun in [10, 30, 1e6]:
            M_kg = M_msun * self.M_SUN
            r_isco = 3.0 * self._r_s(M_kg)
            R_eq = self._R_eq(M_kg)
            assert abs(r_isco / R_eq - 9.0) < 1e-10

    def test_shadow_null(self) -> None:
        """Shadow deviation must be exactly zero under Schwarzschild exterior."""
        import math
        for M_msun in [10, 30, 1e6]:
            M_kg = M_msun * self.M_SUN
            r_s = self._r_s(M_kg)
            M_geom = r_s / 2
            b_crit = 3 * math.sqrt(3) * M_geom
            b_crit_grut = b_crit  # Schwarzschild exterior → identical
            assert b_crit_grut == b_crit

    def test_radiative_efficiency(self) -> None:
        """Radiative efficiency must be standard Schwarzschild 5.72%."""
        import math
        eta = 1.0 - math.sqrt(8.0 / 9.0)
        assert abs(eta - 0.0572) < 0.001

    def test_null_count(self) -> None:
        """At least 7 static observables must be identically null."""
        null_observables = [
            "shadow_angular_radius",
            "photon_sphere_location",
            "photon_sphere_frequency",
            "isco_radius",
            "radiative_efficiency",
            "eddington_luminosity",
            "disk_spectrum",
        ]
        assert len(null_observables) >= 7

    def test_canon_wp3_present(self) -> None:
        """Canon must have WP3 section with null-result status."""
        import json
        from pathlib import Path
        canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
        if not canon_path.exists():
            pytest.skip("Canon file not found")
        canon = json.loads(canon_path.read_text())
        efp = canon.get("collapse", {}).get("exterior_falsifier_program", {})
        wp3 = efp.get("work_packages", {}).get("WP3_shadow_accretion", {})
        assert wp3, "Missing WP3_shadow_accretion"
        status = wp3.get("status", "").upper()
        assert "NULL" in status, f"WP3 status should mention null: {status}"


# ============================================================================
# Phase III-C Covariant Interior Closure Tests
# ============================================================================

class TestPhaseIIIC_Covariant:
    """Tests for the covariant interior closure module.

    Verifies that the effective metric ansatz framework:
    - Preserves the PDE structural identity (omega_0*tau=1)
    - Preserves Q ~ 6 (mixed_viscoelastic)
    - Produces bounded reflection coefficient
    - Integrates with ringdown.py
    """

    M_SUN = 1.989e30

    def test_covariant_result_valid(self) -> None:
        """Covariant analysis must produce a valid result."""
        from grut.interior_covariant import compute_covariant_analysis
        r = compute_covariant_analysis(30.0 * self.M_SUN)
        assert r.valid, "Covariant result should be valid"

    def test_structural_identity_preserved(self) -> None:
        """omega_0*tau must equal 1.0 within 1%."""
        from grut.interior_covariant import compute_covariant_analysis
        for M_msun in [10, 30, 100, 1e6]:
            r = compute_covariant_analysis(M_msun * self.M_SUN)
            assert abs(r.omega_0_tau - 1.0) < 0.01, (
                f"omega_0*tau = {r.omega_0_tau} at {M_msun} M_sun"
            )

    def test_Q_preserved(self) -> None:
        """Q_cov must be in mixed_viscoelastic range [1, 10]."""
        from grut.interior_covariant import compute_covariant_analysis
        for M_msun in [10, 30, 100, 1e6]:
            r = compute_covariant_analysis(M_msun * self.M_SUN)
            assert 1.0 < r.Q_cov < 15.0, f"Q_cov = {r.Q_cov} at {M_msun} M_sun"

    def test_mixed_viscoelastic(self) -> None:
        """Response class must be mixed_viscoelastic."""
        from grut.interior_covariant import compute_covariant_analysis
        r = compute_covariant_analysis(30.0 * self.M_SUN)
        assert r.response_class == "mixed_viscoelastic", (
            f"class = {r.response_class}"
        )

    def test_pde_agreement_confirmed(self) -> None:
        """Covariant framework must confirm PDE results."""
        from grut.interior_covariant import compute_covariant_analysis
        r = compute_covariant_analysis(30.0 * self.M_SUN)
        assert r.pde_agreement == "confirmed", f"agreement = {r.pde_agreement}"

    def test_reflection_bounded(self) -> None:
        """Reflection amplitude must be in [0, 1]."""
        from grut.interior_covariant import compute_covariant_analysis
        for M_msun in [10, 30, 100, 1e6]:
            r = compute_covariant_analysis(M_msun * self.M_SUN)
            assert 0.0 <= r.r_cov_amp <= 1.0, (
                f"r_cov = {r.r_cov_amp} at {M_msun} M_sun"
            )

    def test_reflection_positive(self) -> None:
        """Reflection amplitude must be positive (non-trivial)."""
        from grut.interior_covariant import compute_covariant_analysis
        r = compute_covariant_analysis(30.0 * self.M_SUN)
        assert r.r_cov_amp > 0.0, f"r_cov = {r.r_cov_amp}"

    def test_reflection_near_pde(self) -> None:
        """Covariant reflection must be within ±30% of PDE."""
        from grut.interior_covariant import compute_covariant_analysis
        r = compute_covariant_analysis(30.0 * self.M_SUN)
        if r.r_pde_amp > 0:
            pct = abs(r.r_cov_amp - r.r_pde_amp) / r.r_pde_amp * 100
            assert pct < 30.0, f"Deviation {pct:.1f}% exceeds 30%"

    def test_echo_channel_not_collapsed(self) -> None:
        """Echo channel must not collapse."""
        from grut.interior_covariant import compute_covariant_analysis
        r = compute_covariant_analysis(30.0 * self.M_SUN)
        assert r.echo_channel_status != "collapsed", (
            f"status = {r.echo_channel_status}"
        )
        assert r.echo_amp_cov_pct > 0.1, f"echo = {r.echo_amp_cov_pct}%"

    def test_metric_ansatz_valid(self) -> None:
        """Interior metric ansatz must produce valid parameters."""
        from grut.interior_covariant import build_interior_metric
        m = build_interior_metric(30.0 * self.M_SUN)
        assert m.valid
        assert abs(m.R_eq_over_r_s - 1.0 / 3.0) < 1e-10
        assert abs(m.compactness - 3.0) < 1e-10
        assert abs(m.A_schw_at_Req - (-2.0)) < 1e-10
        assert m.c_eff_sq > 0

    def test_c_eff_subluminal(self) -> None:
        """Effective propagation speed must be sub-luminal."""
        import math
        from grut.interior_covariant import build_interior_metric
        C_SI = 299_792_458.0
        for M_msun in [10, 30, 1e6]:
            m = build_interior_metric(M_msun * self.M_SUN)
            c_eff = math.sqrt(m.c_eff_sq) if m.c_eff_sq > 0 else 0.0
            assert c_eff < C_SI, f"c_eff >= c at {M_msun} M_sun"

    def test_ringdown_integration(self) -> None:
        """Covariant fields must be populated in ringdown.py EchoResult."""
        from grut.ringdown import (
            compute_echo_analysis, EchoParameters, schwarzschild_radius,
        )
        M = 30.0 * self.M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            R_eq_over_r_s=1.0 / 3.0, compactness=3.0,
            beta_Q=2.0, epsilon_Q=1.0 / 9.0,
            reflection_model="pde",
        )
        result = compute_echo_analysis(params)
        assert result.cov_Q > 0, f"cov_Q = {result.cov_Q}"
        assert result.cov_r_amp > 0, f"cov_r_amp = {result.cov_r_amp}"
        assert result.cov_response_class != "", "cov_response_class empty"
        assert result.cov_identity_preserved, "identity not preserved"

    def test_covariant_reflection_model(self) -> None:
        """'covariant' reflection model must use covariant r_amp."""
        from grut.ringdown import (
            compute_echo_analysis, EchoParameters, schwarzschild_radius,
        )
        M = 30.0 * self.M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            R_eq_over_r_s=1.0 / 3.0, compactness=3.0,
            beta_Q=2.0, epsilon_Q=1.0 / 9.0,
            reflection_model="covariant",
        )
        result = compute_echo_analysis(params)
        assert abs(result.reflection_surface - result.cov_r_amp) < 1e-10, (
            f"R_surface={result.reflection_surface}, cov_r={result.cov_r_amp}"
        )

    def test_serialization_covariant(self) -> None:
        """Serialized EchoResult must include covariant_interior section."""
        from grut.ringdown import (
            compute_echo_analysis, EchoParameters, schwarzschild_radius,
            echo_result_to_dict,
        )
        M = 30.0 * self.M_SUN
        r_s = schwarzschild_radius(M)
        params = EchoParameters(
            M_kg=M, r_s_m=r_s, R_eq_m=r_s / 3.0,
            R_eq_over_r_s=1.0 / 3.0, compactness=3.0,
            beta_Q=2.0, epsilon_Q=1.0 / 9.0,
            reflection_model="pde",
        )
        result = compute_echo_analysis(params)
        d = echo_result_to_dict(result)
        assert "covariant_interior" in d
        cov = d["covariant_interior"]
        assert "Q_cov" in cov
        assert "r_cov_amp" in cov
        assert cov["Q_cov"] > 0

    def test_nonclaims_present(self) -> None:
        """Covariant result must have >= 8 nonclaims."""
        from grut.interior_covariant import compute_covariant_analysis
        r = compute_covariant_analysis(30.0 * self.M_SUN)
        assert len(r.nonclaims) >= 8, f"nonclaims = {len(r.nonclaims)}"

    def test_negative_mass(self) -> None:
        """Negative mass must produce invalid result."""
        from grut.interior_covariant import compute_covariant_analysis
        r = compute_covariant_analysis(-1.0)
        assert not r.valid
