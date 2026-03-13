"""GRUT Radial Collapse Solver — Hole Sector Physics.

Spherically symmetric dust collapse with GRUT memory-kernel coupling.
Uses the Oppenheimer-Snyder interior ↔ closed FRW analogy:
the same operator stack (memory, L_stiff, dissipation, tau_coupling)
governs the collapse dynamics.

Key principle: r_sat is DERIVED from the ODE integration, never hardcoded.

State vector: [R, V, M_drive]
  R       = shell radius (m)
  V       = dR/dt (m/s), V <= 0 during collapse
  M_drive = memory state tracking gravitational drive (m/s^2)

Equations:
  dR/dt      = V
  dV/dt      = -a_net
  dM_drive/dt = (GM/R^2 - M_drive) / tau_eff

  Canonical force decomposition:
    a_inward  = (1 - alpha_vac) * GM/R^2 + alpha_vac * M_drive
    a_outward = a_Q  (quantum pressure barrier, OP_QPRESS_001)
    a_net     = a_inward - a_outward

  a_Q     = (GM/R^2) * epsilon_Q * (r_s/R)^beta_Q   [default epsilon_Q=0: off]
  tau_eff = tau_0 / (1 + (|V/R| * tau_0)^2)

  Equilibrium (asymptotic, when M_drive ≈ a_grav):
    R_eq / r_s = epsilon_Q^(1/beta_Q)

Post-step operators:
  L_stiff:     if |V/R| > H_cap then V = -H_cap * R
  Dissipation: V *= exp(-gamma_diss * dt)

Bounce exclusion (two-tier result):

  Tier 1 — Weak gravity (M ≲ 10²⁴ kg at canon params):
    Sign-definite. M_drive > 0 throughout, a_net > 0 throughout.
    V starts at 0, dV/dt < 0 always => V ≤ 0 for all time. No bounce.
    Dissipation and L_stiff preserve sign. STRUCTURAL.

  Tier 2 — Astrophysical masses (M ≳ 10³⁰ kg at canon params):
    Numerical. M_drive can go transiently negative due to rapid a_grav
    evolution outpacing memory tracking. a_net can become negative at
    some timesteps (transient outward acceleration). Despite this, V
    does not cross zero in tested parameter ranges — the inward inertia
    exceeds the transient outward impulse. CONDITIONAL, not sign-theorem.

  The originally claimed sign-definiteness of a_net > 0 does NOT survive
  into the astrophysical regime. The no-bounce result persists numerically
  but the mechanism differs by mass scale.

Collapse classification (collapse_class field):
  stall               — V → 0 with < 5% radius reduction (shell barely moved)
  arrested_prehorizon — V → 0, R significantly reduced, C_max < 1
  arrested_posthorizon— V → 0, C_max ≥ 1 (passed through trapping)
  plunging            — still collapsing at step budget exhaustion
  singular            — R reached R_min (GR-like singularity)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# ── Physical constants (SI) ──────────────────────────────────────
G_SI = 6.674e-11          # m^3 kg^-1 s^-2
C_SI = 299_792_458.0      # m/s
HBAR_SI = 1.054571817e-34  # J·s
SEC_PER_YEAR = 365.25 * 24.0 * 3600.0


class CollapseError(ValueError):
    """Raised for invalid collapse parameters or integration failures."""
    pass


# ── Diagnostics ──────────────────────────────────────────────────

def compute_schwarzschild_radius(M_kg: float) -> float:
    """r_s = 2GM/c^2."""
    return 2.0 * G_SI * M_kg / (C_SI ** 2)


def compute_freefall_time(R0_m: float, M_kg: float) -> float:
    """Free-fall time for marginally bound collapse: t_ff = (pi/2)*sqrt(R0^3/(2GM))."""
    return (math.pi / 2.0) * math.sqrt(R0_m ** 3 / (2.0 * G_SI * M_kg))


def compute_compactness(R: float, M_kg: float) -> float:
    """Compactness C = 2GM/(Rc^2).  C >= 1 means trapped surface."""
    if R <= 0.0:
        return float("inf")
    return 2.0 * G_SI * M_kg / (R * C_SI ** 2)


def compute_kretschner(R: float, M_kg: float) -> float:
    """Kretschner scalar for Schwarzschild geometry: K = 48(GM)^2 / (c^4 R^6)."""
    if R <= 0.0:
        return float("inf")
    return 48.0 * (G_SI * M_kg) ** 2 / (C_SI ** 4 * R ** 6)


# ── Local-tau closure ────────────────────────────────────────────

def _compute_tau0_local(
    tau0_s: float,
    R: float,
    M_kg: float,
    local_tau_mode: str,
) -> float:
    """Compute local memory timescale using the specified closure.

    Parameters
    ----------
    tau0_s : bare cosmological memory time (s)
    R      : current shell radius (m)
    M_kg   : total mass (kg)
    local_tau_mode : closure mode
        "off"   — return bare tau0_s (no correction)
        "tier0" — F = t_dyn / (t_dyn + tau0_s)

    Returns
    -------
    tau0_local : effective local memory timescale (s)
    """
    if local_tau_mode == "off":
        return tau0_s

    R_safe = max(abs(R), 1e-30)

    if local_tau_mode == "tier0":
        # t_dyn = sqrt(R^3 / (2GM)) — local gravitational free-fall time
        t_dyn_local = math.sqrt(R_safe ** 3 / (2.0 * G_SI * M_kg))
        # F = t_dyn / (t_dyn + tau0_s)
        # tau0_local = tau0_s * F = tau0_s * t_dyn / (t_dyn + tau0_s)
        tau0_local = tau0_s * t_dyn_local / (t_dyn_local + tau0_s)
        return max(tau0_local, 1e-30)

    # Fallback: bare tau0
    return tau0_s


# ── Core ODE RHS ─────────────────────────────────────────────────

def _rhs(
    state: np.ndarray,
    M_kg: float,
    tau0_s: float,
    alpha_vac: float,
    local_tau_mode: str = "off",
    epsilon_Q: float = 0.0,
    beta_Q: float = 2.0,
    r_s: float = 0.0,
) -> np.ndarray:
    """Compute time derivatives [dR/dt, dV/dt, dM_drive/dt].

    Parameters
    ----------
    state : [R, V, M_drive]
    M_kg  : total mass (kg)
    tau0_s: memory relaxation time (s)
    alpha_vac: vacuum screening fraction
    local_tau_mode: "off" | "tier0" — local memory closure
    epsilon_Q: quantum pressure coupling (0 = off)
    beta_Q: barrier steepness exponent
    r_s: Schwarzschild radius (m), needed for a_Q

    Returns
    -------
    [dR, dV, dM_drive] time derivatives
    """
    R, V, M_drive = state[0], state[1], state[2]

    # Prevent division by zero
    R_safe = max(abs(R), 1e-30)

    # Gravitational drive
    a_grav = G_SI * M_kg / (R_safe ** 2)

    # Canonical force decomposition:
    #   a_inward  = (1-alpha_vac)*a_grav + alpha_vac*M_drive
    #   a_outward = a_Q (OP_QPRESS_001 barrier)
    #   a_net     = a_inward - a_outward
    # Variable name "a_eff" is retained for backward compat but equals a_net.
    a_eff = (1.0 - alpha_vac) * a_grav + alpha_vac * M_drive  # = a_inward

    # OP_QPRESS_001: Compactness-dependent quantum pressure barrier
    if epsilon_Q > 0.0 and r_s > 0.0:
        a_Q = a_grav * epsilon_Q * (r_s / R_safe) ** beta_Q
        a_eff = a_eff - a_Q  # a_eff = a_inward - a_outward = a_net

    # Derivatives
    dR = V
    dV = -a_eff  # V_dot = -a_net (positive a_net → inward, negative → outward)

    if alpha_vac > 0:
        # Local-tau closure: replace bare tau0 with local version
        tau0_local = _compute_tau0_local(tau0_s, R_safe, M_kg, local_tau_mode)

        # Tau coupling: tau_eff = tau0_local / (1 + (H_coll * tau0_local)^2)
        H_coll = abs(V) / R_safe
        H_tau = H_coll * tau0_local
        tau_eff = tau0_local / (1.0 + H_tau * H_tau)
        tau_eff = max(tau_eff, 1e-30)  # floor
        dM_drive = (a_grav - M_drive) / tau_eff
    else:
        # Pure GR: memory coupling off — M_drive doesn't affect a_eff,
        # so skip its evolution to avoid numerical overflow.
        dM_drive = 0.0

    return np.array([dR, dV, dM_drive])


def _rk4_step(
    state: np.ndarray,
    dt: float,
    M_kg: float,
    tau0_s: float,
    alpha_vac: float,
    local_tau_mode: str = "off",
    epsilon_Q: float = 0.0,
    beta_Q: float = 2.0,
    r_s: float = 0.0,
) -> np.ndarray:
    """Single RK4 step."""
    k1 = _rhs(state, M_kg, tau0_s, alpha_vac, local_tau_mode, epsilon_Q, beta_Q, r_s)
    k2 = _rhs(state + 0.5 * dt * k1, M_kg, tau0_s, alpha_vac, local_tau_mode, epsilon_Q, beta_Q, r_s)
    k3 = _rhs(state + 0.5 * dt * k2, M_kg, tau0_s, alpha_vac, local_tau_mode, epsilon_Q, beta_Q, r_s)
    k4 = _rhs(state + dt * k3, M_kg, tau0_s, alpha_vac, local_tau_mode, epsilon_Q, beta_Q, r_s)
    return state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


# ── Main solver ──────────────────────────────────────────────────

@dataclass
class CollapseResult:
    """Complete collapse trajectory and diagnostics."""

    # Trajectory arrays (length = n_recorded)
    t_s: np.ndarray           # time (s)
    R_m: np.ndarray           # radius (m)
    V_ms: np.ndarray          # velocity (m/s)
    M_drive: np.ndarray       # memory state (m/s^2)
    compactness: np.ndarray   # 2GM/(Rc^2)
    is_trapped: np.ndarray    # boolean: compactness >= 1
    K_kretschner: np.ndarray  # Kretschner scalar
    tau_eff_s: np.ndarray     # effective tau at each step
    a_eff: np.ndarray         # effective acceleration at each step

    # Energy ledger
    E_kinetic: np.ndarray     # (1/2) M V^2
    E_potential: np.ndarray   # -G M^2 / R
    E_dissipated_cumul: np.ndarray  # cumulative dissipation loss

    # Derived quantities
    r_sat_m: Optional[float]       # saturation radius (m), None if not reached
    t_sat_s: Optional[float]       # time to saturation (s)
    r_sat_over_r_s: Optional[float]  # r_sat / r_schwarzschild
    bounce_detected: bool          # True if V ever changes sign (should be False)
    K_at_sat: Optional[float]      # Kretschner at saturation
    compactness_at_sat: Optional[float]  # compactness at saturation
    trapped_at_sat: Optional[bool]  # whether trapped at saturation

    # AH crossings: list of (t, R, direction) where trapped status changes
    ah_crossings: List[Tuple[float, float, str]]

    # Inputs (for audit)
    inputs: Dict[str, Any]

    # Reference quantities
    r_s_m: float               # Schwarzschild radius
    t_ff_s: float              # free-fall time

    # Integration metadata
    n_steps_taken: int
    termination_reason: str    # "saturation", "singularity", "max_steps"
    l_stiff_activations: int
    max_compactness: float

    # ── Refined collapse classification (Phase-G additions) ──
    # These fields add physics-level interpretation on top of the
    # backward-compatible termination_reason string.
    collapse_class: str = "unknown"
    # "stall"                — V → 0 with < 5 % radius reduction
    # "arrested_prehorizon"  — V → 0, significant R reduction, C_max < 1
    # "arrested_posthorizon" — V → 0, C_max ≥ 1 (crossed trapping)
    # "plunging"             — still collapsing at step budget
    # "singular"             — reached R_min (GR singularity)
    # "unknown"              — fallback / uninitialised

    collapse_fraction: float = 0.0
    # (R0 - R_final) / R0   — 0 = no motion, 1 = reached origin

    a_eff_min: float = 0.0
    # minimum a_eff across trajectory (< 0 means outward impulse occurred)

    M_drive_min: float = 0.0
    # minimum M_drive across trajectory (< 0 means memory inverted)

    bounce_exclusion_tier: str = "unknown"
    # "sign_definite" — a_eff > 0 AND M_drive > 0 throughout (Tier 1)
    # "numerical"     — V ≤ 0 throughout but a_eff or M_drive went negative (Tier 2)
    # "violated"      — V changed sign (bounce detected)

    # ── Timescale competition (the key hole-sector control parameter) ──
    tau0_over_t_dyn: float = 0.0
    # τ₀ / t_ff — ratio of memory relaxation time to free-fall time.
    # >> 1: memory too slow, collapse freezes or inverts
    # ~ 1:  memory participates meaningfully
    # << 1: memory tracks instantly, approaches GR limit

    tau_eff_over_t_dyn_final: float = 0.0
    # τ_eff(final) / t_dyn(final) — evolved ratio at end of trajectory.
    # Captures how the competition shifted during collapse.

    # ── Step-budget diagnostics (first-class audit fields) ──
    step_budget_fraction: float = 0.0
    # n_steps_taken / n_steps_requested — 1.0 means budget exhausted.

    step_budget_exhausted: bool = False
    # True iff termination_reason == "max_steps" — explicit flag.

    t_total_over_t_ff: float = 0.0
    # t_total / t_ff — how many free-fall times did the integration cover?
    # If << 1 and step_budget_exhausted, the solver needs more steps.

    # ── Quantum pressure endpoint diagnostics (OP_QPRESS_001) ──
    a_Q: np.ndarray = None  # type: ignore[assignment]
    # Quantum pressure acceleration array (m/s^2), recorded alongside a_eff.
    # None when epsilon_Q = 0 (off).

    ## CANONICAL FORCE DECOMPOSITION (used everywhere):
    #
    #   a_inward  = (1-alpha_vac)*a_grav + alpha_vac*M_drive   [total inward drive]
    #   a_outward = a_Q                                         [barrier, outward]
    #   a_net     = a_inward - a_outward                        [net, drives V_dot = -a_net]
    #
    #   force_balance_residual = |a_net| / a_grav               [dimensionless]
    #
    # This convention is used in _rhs, _record, diagnostics, and all benchmarks.

    force_balance_residual: float = 0.0
    # Dimensionless: |a_net| / a_grav at final state.
    # a_net = a_inward - a_outward. Should → 0 for genuine equilibrium.
    # NOTE: R_eq/r_s = epsilon_Q^(1/beta_Q) is an ASYMPTOTIC prediction
    # valid when M_drive ≈ a_grav (memory saturated). Not an exact guarantee.

    R_eq_predicted: float = 0.0
    # Asymptotic prediction: R_eq/r_s = epsilon_Q^(1/beta_Q)
    # Valid in the converged regime where M_drive has saturated to a_grav.

    asymptotic_stability_indicator: float = 0.0
    # d(a_net)/dR at R_f — POSITIVE means stable (restoring).
    # Derivation: V_dot = -a_net, so V_dot ≈ -(d(a_net)/dR)*δR near R_eq.
    # For restoring: δR>0 → V_dot<0 (inward) requires d(a_net)/dR > 0.

    # ── Operator share at endpoint (force decomposition) ──
    a_grav_final: float = 0.0
    # GM/R_f^2 — raw gravitational acceleration at endpoint (m/s^2)

    a_inward_final: float = 0.0
    # (1-alpha)*a_grav + alpha*M_drive at endpoint (m/s^2) — total inward drive

    a_outward_final: float = 0.0
    # a_Q at endpoint (m/s^2) — OP_QPRESS_001 barrier, outward

    a_net_final: float = 0.0
    # a_inward - a_outward at endpoint (m/s^2) — should → 0

    artifact_R_f: float = 0.0
    # L_stiff artifact prediction: (V_tol^2 * 2GM / H_cap^2)^(1/3) / r_s
    # Computed DIRECTLY from the closed-form law. NOT using V_ff at final R.

    # ── Endpoint motion diagnostics (honest classification) ──
    endpoint_motion_class: str = "unknown"
    # "sign_definite_infall" | "equilibrium_restoring" | "overshoot_damped" | "bounce_violation"

    positive_velocity_episodes: int = 0
    # Number of times V crossed from negative to positive

    max_outward_velocity: float = 0.0
    # Peak positive V (m/s). 0 if V ≤ 0 always.

    overshoot_count: int = 0
    # Number of R oscillations around R_eq (direction changes in R)

    memory_tracking_ratio_final: float = 0.0
    # M_drive / a_grav at final state.
    # The asymptotic prediction R_eq/r_s = epsilon_Q^(1/beta_Q) is only valid
    # when M_drive ≈ a_grav (memory has saturated). If this ratio is not ≈ 1,
    # analytical mismatch does NOT falsify the operator — it means the
    # asymptotic regime was not reached.

    # ── Phase III-A: Order parameter for fluid-to-core transition ──
    barrier_dominance_final: float = 0.0
    # Φ = a_outward / a_inward at the final state.
    # PRIMARY ORDER PARAMETER for the Quantum Fluid → Barrier-Dominated Core transition.
    #   Φ → 0: Quantum Fluid regime (barrier negligible, gravity-dominated)
    #   Φ ≈ 0.5: Crystallization Threshold (barrier substantially resists infall)
    #   Φ → 1: Barrier-Dominated Compact Core (near-equilibrium, force-balanced)
    # Status: CANDIDATE (Phase III-A). Threshold values are research targets.

    compactness_final: float = 0.0
    # C = r_s / R_f at the final state (supporting diagnostic).
    # C < 1: pre-horizon; C ≥ 1: post-horizon (inside apparent horizon).


def compute_collapse(
    *,
    M_kg: float,
    R0_m: float,
    tau0_s: float,
    alpha_vac: float = 1.0 / 3.0,
    gamma_diss: float = 1e-15,
    H_cap: float = 1e6 / SEC_PER_YEAR,
    n_steps: int = 50_000,
    record_every: int = 10,
    V_tol_frac: float = 1e-8,
    R_min_frac: float = 1e-12,
    local_tau_mode: str = "off",
    R_conv_tol: float = 1e-10,
    conv_window: int = 500,
    epsilon_Q: float = 0.0,
    beta_Q: float = 2.0,
    V0_mps: float = 0.0,
) -> CollapseResult:
    """Integrate spherically symmetric collapse with GRUT memory coupling.

    Parameters
    ----------
    M_kg : float
        Total mass of collapsing object (kg).
    R0_m : float
        Initial radius (m).  Must be > Schwarzschild radius.
    tau0_s : float
        Memory relaxation timescale (s).  Canon: 1.3225e15 s.
    alpha_vac : float
        Vacuum screening fraction.  Canon: 1/3.
    gamma_diss : float
        Dissipation rate (s^-1).  Must be >= 0.
        Canon default for cosmology is 0; collapse arrest requires > 0.
    H_cap : float
        L_stiff collapse rate cap (s^-1).
        Canon: 10^6 yr^-1 ≈ 3.17e-2 s^-1.
    n_steps : int
        Maximum integration steps.
    record_every : int
        Record trajectory every N steps (memory management).
    V_tol_frac : float
        Fractional velocity tolerance for saturation detection.
        Saturation when |V| < V_tol_frac * (V_freefall at R_current).
    R_min_frac : float
        Minimum R/R0 before declaring singularity.
    local_tau_mode : str
        Local memory timescale closure.
        "off"   — bare tau0 (backward compatible, default).
        "tier0" — tau0_local = tau0 * t_dyn / (t_dyn + tau0).
    R_conv_tol : float
        Fractional radius change per step threshold for convergence.
        When |dR/R| < R_conv_tol for conv_window consecutive steps,
        declare radius convergence (the shell has effectively stopped).
    conv_window : int
        Number of consecutive steps below R_conv_tol needed to
        trigger radius convergence termination.
    epsilon_Q : float
        OP_QPRESS_001 quantum pressure coupling strength.
        0.0 (default) = operator OFF, no barrier.
        > 0 activates compactness-dependent barrier.
    beta_Q : float
        OP_QPRESS_001 barrier steepness exponent. Default 2.
    V0_mps : float
        Initial radial velocity (m/s). Default 0 = rest start.
        Negative = inward, positive = outward.

    Returns
    -------
    CollapseResult with full trajectory and diagnostics.
    """
    # ── Validate inputs ──
    if M_kg <= 0:
        raise CollapseError("M_kg must be positive")
    if R0_m <= 0:
        raise CollapseError("R0_m must be positive")
    if tau0_s <= 0:
        raise CollapseError("tau0_s must be positive")
    if alpha_vac < 0 or alpha_vac >= 1:
        raise CollapseError("alpha_vac must be in [0, 1)")
    if gamma_diss < 0:
        raise CollapseError("gamma_diss must be >= 0")
    if H_cap <= 0:
        raise CollapseError("H_cap must be positive")

    # ── Reference quantities ──
    r_s = compute_schwarzschild_radius(M_kg)
    t_ff = compute_freefall_time(R0_m, M_kg)
    R_min = R_min_frac * R0_m

    # Adaptive timestep: fraction of the dynamical time
    # Use CFL-like condition: dt = C * min(R/|V|, tau_eff, 1/H_cap)
    CFL = 0.005

    # ── Initial state ──
    a_grav_0 = G_SI * M_kg / (R0_m ** 2)
    state = np.array([R0_m, V0_mps, a_grav_0])  # [R, V, M_drive]

    # ── Storage ──
    max_records = n_steps // record_every + 2
    t_arr = np.zeros(max_records)
    R_arr = np.zeros(max_records)
    V_arr = np.zeros(max_records)
    Md_arr = np.zeros(max_records)
    comp_arr = np.zeros(max_records)
    trap_arr = np.zeros(max_records, dtype=bool)
    K_arr = np.zeros(max_records)
    tau_eff_arr = np.zeros(max_records)
    a_eff_arr = np.zeros(max_records)
    a_Q_arr = np.zeros(max_records)
    Ek_arr = np.zeros(max_records)
    Ep_arr = np.zeros(max_records)
    Ed_arr = np.zeros(max_records)

    t_current = 0.0
    rec_idx = 0
    l_stiff_count = 0
    E_dissipated = 0.0
    termination = "max_steps"
    ah_crossings: List[Tuple[float, float, str]] = []
    prev_trapped = False
    # Radius convergence tracking
    conv_count = 0       # consecutive steps with |dR/R| < R_conv_tol
    R_prev_step = R0_m   # previous step radius for convergence check
    step = -1            # will be set by loop; -1 means no steps taken

    def _record(idx: int, t: float, s: np.ndarray, E_diss: float) -> int:
        if idx >= max_records:
            return idx
        R, V, Md = s[0], s[1], s[2]
        R_safe = max(abs(R), 1e-30)
        c = compute_compactness(R_safe, M_kg)
        t_arr[idx] = t
        R_arr[idx] = R_safe
        V_arr[idx] = V
        Md_arr[idx] = Md
        comp_arr[idx] = c
        trap_arr[idx] = c >= 1.0
        K_arr[idx] = compute_kretschner(R_safe, M_kg)
        H_coll = abs(V) / R_safe
        tau0_loc = _compute_tau0_local(tau0_s, R_safe, M_kg, local_tau_mode)
        tau_eff_arr[idx] = tau0_loc / (1.0 + (H_coll * tau0_loc) ** 2)
        a_g = G_SI * M_kg / (R_safe ** 2)
        # OP_QPRESS_001: include barrier in a_eff and record a_Q
        a_Q_rec = 0.0
        if epsilon_Q > 0.0 and r_s > 0.0:
            a_Q_rec = a_g * epsilon_Q * (r_s / R_safe) ** beta_Q
        a_Q_arr[idx] = a_Q_rec
        a_eff_arr[idx] = (1.0 - alpha_vac) * a_g + alpha_vac * Md - a_Q_rec
        Ek_arr[idx] = 0.5 * M_kg * V * V
        Ep_arr[idx] = -G_SI * M_kg * M_kg / R_safe
        Ed_arr[idx] = E_diss
        return idx + 1

    # Record initial state
    rec_idx = _record(rec_idx, 0.0, state, 0.0)

    # ── Integration loop ──
    for step in range(n_steps):
        R, V, M_drive_val = state[0], state[1], state[2]
        R_safe = max(abs(R), 1e-30)

        # ── Adaptive dt ──
        H_coll = abs(V) / R_safe if abs(V) > 0 else 1e-30
        tau0_loc = _compute_tau0_local(tau0_s, R_safe, M_kg, local_tau_mode)
        tau_eff_local = tau0_loc / (1.0 + (H_coll * tau0_loc) ** 2)
        tau_eff_local = max(tau_eff_local, 1e-30)

        # Acceleration timescale: sqrt(2R/a) — prevents velocity overshoot
        # when V ≈ 0 (first steps) or during rapid deceleration.
        a_grav_local = G_SI * M_kg / (R_safe ** 2)
        a_eff_local = (1.0 - alpha_vac) * a_grav_local + alpha_vac * M_drive_val
        # OP_QPRESS_001: include barrier in CFL acceleration estimate
        if epsilon_Q > 0.0 and r_s > 0.0:
            a_Q_local = a_grav_local * epsilon_Q * (r_s / R_safe) ** beta_Q
            a_eff_local = a_eff_local - a_Q_local
        # Near equilibrium a_eff → 0, so dt_acc → inf. Floor at 0.1*a_grav
        # to prevent timestep blowup while still resolving the restoring force.
        a_for_dt = max(abs(a_eff_local), 0.1 * a_grav_local, 1e-30)
        dt_acc = math.sqrt(2.0 * R_safe / a_for_dt)   # acceleration time

        dt_dyn = R_safe / max(abs(V), 1e-30)   # dynamical time
        # Note: L_stiff is a post-step clipping operator, NOT part of the
        # smooth ODE.  Its timescale (1/H_cap) does not enter the CFL.
        if alpha_vac > 0:
            # Memory coupling is active — constrain step by tau_eff
            # so that M_drive dynamics are resolved.
            dt_tau = tau_eff_local                # memory time
            dt = CFL * min(dt_dyn, dt_tau, dt_acc)
        else:
            # Pure GR (alpha=0): M_drive decouples from a_eff,
            # so tau_eff doesn't constrain the integration.
            dt = CFL * min(dt_dyn, dt_acc)
        dt = max(dt, 1e-30)                       # floor
        dt = min(dt, 1e20)                        # ceiling for stability

        # ── RK4 step ──
        state_new = _rk4_step(state, dt, M_kg, tau0_s, alpha_vac, local_tau_mode,
                              epsilon_Q, beta_Q, r_s)

        # ── Post-step operators ──
        R_new, V_new, Md_new = state_new[0], state_new[1], state_new[2]
        R_new_safe = max(abs(R_new), 1e-30)

        # L_stiff: cap collapse rate
        H_coll_new = abs(V_new) / R_new_safe
        if H_coll_new > H_cap:
            V_new = -H_cap * R_new_safe  # preserve sign (collapse = negative)
            l_stiff_count += 1

        # Dissipation: exponential damping
        if gamma_diss > 0:
            damp = math.exp(-gamma_diss * dt)
            E_before = 0.5 * M_kg * V_new * V_new
            V_new *= damp
            E_after = 0.5 * M_kg * V_new * V_new
            E_dissipated += (E_before - E_after)

        state_new = np.array([R_new_safe, V_new, Md_new])

        # ── AH crossing detection ──
        c_new = compute_compactness(R_new_safe, M_kg)
        now_trapped = c_new >= 1.0
        if now_trapped and not prev_trapped:
            ah_crossings.append((t_current + dt, R_new_safe, "formation"))
        elif not now_trapped and prev_trapped:
            ah_crossings.append((t_current + dt, R_new_safe, "dissolution"))
        prev_trapped = now_trapped

        # ── Advance ──
        state = state_new
        t_current += dt

        # ── Record ──
        if (step + 1) % record_every == 0:
            rec_idx = _record(rec_idx, t_current, state, E_dissipated)

        # ── Termination checks ──
        # Saturation: |V| small relative to local freefall velocity
        V_ff_local = math.sqrt(2.0 * G_SI * M_kg / R_new_safe) if R_new_safe > 0 else 1e30
        if abs(V_new) < V_tol_frac * V_ff_local and step > 100:
            termination = "saturation"
            rec_idx = _record(rec_idx, t_current, state, E_dissipated)
            break

        # Singularity: R too small
        if R_new_safe < R_min:
            termination = "singularity"
            rec_idx = _record(rec_idx, t_current, state, E_dissipated)
            break

        # Radius convergence: shell effectively stopped moving
        dR_frac = abs(R_new_safe - R_prev_step) / max(R_prev_step, 1e-30)
        R_prev_step = R_new_safe
        if dR_frac < R_conv_tol and step > 100:
            conv_count += 1
        else:
            conv_count = 0
        if conv_count >= conv_window:
            termination = "radius_converged"
            rec_idx = _record(rec_idx, t_current, state, E_dissipated)
            break
    else:
        # Loop completed without break — max_steps exhausted.
        # Record the true final state for accurate diagnostics.
        rec_idx = _record(rec_idx, t_current, state, E_dissipated)

    # ── Trim arrays ──
    t_arr = t_arr[:rec_idx]
    R_arr = R_arr[:rec_idx]
    V_arr = V_arr[:rec_idx]
    Md_arr = Md_arr[:rec_idx]
    comp_arr = comp_arr[:rec_idx]
    trap_arr = trap_arr[:rec_idx]
    K_arr = K_arr[:rec_idx]
    tau_eff_arr = tau_eff_arr[:rec_idx]
    a_eff_arr = a_eff_arr[:rec_idx]
    a_Q_arr = a_Q_arr[:rec_idx]
    Ek_arr = Ek_arr[:rec_idx]
    Ep_arr = Ep_arr[:rec_idx]
    Ed_arr = Ed_arr[:rec_idx]

    # ── Derived quantities ──
    r_sat_m: Optional[float] = None
    t_sat_s: Optional[float] = None
    r_sat_over_r_s: Optional[float] = None
    K_at_sat: Optional[float] = None
    comp_at_sat: Optional[float] = None
    trapped_at_sat: Optional[bool] = None

    if termination in ("saturation", "radius_converged") and rec_idx > 0:
        r_sat_m = float(R_arr[-1])
        t_sat_s = float(t_arr[-1])
        r_sat_over_r_s = r_sat_m / r_s if r_s > 0 else None
        K_at_sat = float(K_arr[-1])
        comp_at_sat = float(comp_arr[-1])
        trapped_at_sat = bool(trap_arr[-1])

    # Bounce detection: did V ever change sign?
    # For V0_mps=0 (default): V should be <= 0 always (starts at 0, goes negative).
    # For V0_mps>0 (perturbation test): initial positive V is intentional, not a bounce.
    # With OP_QPRESS_001: positive V near R_eq is expected (restoring force).
    # Keep backward-compatible detection (any V>0 after first entry).
    bounce_detected = bool(np.any(V_arr[1:] > 0))  # skip V[0]

    # ── Refined classification ──
    R_final = float(R_arr[-1]) if rec_idx > 0 else R0_m
    collapse_frac = (R0_m - R_final) / R0_m if R0_m > 0 else 0.0

    a_eff_min_val = float(np.min(a_eff_arr)) if rec_idx > 0 else 0.0
    M_drive_min_val = float(np.min(Md_arr)) if rec_idx > 0 else 0.0

    max_comp = float(np.max(comp_arr)) if rec_idx > 0 else 0.0

    # Bounce-exclusion tier
    if bounce_detected:
        bounce_tier = "violated"
    elif a_eff_min_val >= 0.0 and M_drive_min_val >= 0.0:
        bounce_tier = "sign_definite"     # Tier 1: structural
    else:
        bounce_tier = "numerical"          # Tier 2: holds numerically only

    # Collapse class
    STALL_THRESHOLD = 0.05  # < 5 % radius reduction = stall
    if termination == "singularity":
        collapse_cls = "singular"
    elif termination in ("saturation", "radius_converged"):
        if collapse_frac < STALL_THRESHOLD:
            collapse_cls = "stall"
        elif max_comp >= 1.0:
            collapse_cls = "arrested_posthorizon"
        else:
            collapse_cls = "arrested_prehorizon"
    else:
        # max_steps — still moving
        if abs(V_arr[-1]) > 0 if rec_idx > 0 else False:
            collapse_cls = "plunging"
        else:
            collapse_cls = "stall"

    # ── Timescale competition ──
    tau0_over_tff = tau0_s / t_ff if t_ff > 0 else float("inf")

    # Evolved ratio at end of trajectory
    # Uses the SAME local-tau closure as the ODE, and the gravitational
    # free-fall time t_dyn = sqrt(R^3 / 2GM) for consistency with Tier 0.
    if rec_idx > 0:
        R_f = float(R_arr[-1])
        V_f = float(V_arr[-1])
        R_f_safe = max(abs(R_f), 1e-30)
        H_f = abs(V_f) / R_f_safe
        # Use local tau closure (matches what the ODE actually used)
        tau0_f_local = _compute_tau0_local(tau0_s, R_f_safe, M_kg, local_tau_mode)
        tau_eff_f = tau0_f_local / (1.0 + (H_f * tau0_f_local) ** 2)
        # Gravitational free-fall time (consistent with Tier 0 definition)
        t_dyn_f = math.sqrt(R_f_safe ** 3 / (2.0 * G_SI * M_kg))
        tau_eff_over_tdyn_f = tau_eff_f / t_dyn_f if t_dyn_f > 0 else float("inf")
    else:
        tau_eff_over_tdyn_f = tau0_over_tff

    # ── Step-budget diagnostics ──
    n_taken = step + 1
    budget_frac = n_taken / n_steps if n_steps > 0 else 0.0
    budget_exhausted = termination == "max_steps"
    t_total = float(t_arr[-1]) if rec_idx > 0 else 0.0
    t_total_over_tff = t_total / t_ff if t_ff > 0 else 0.0

    # ── OP_QPRESS_001 endpoint diagnostics ──
    force_balance_res = 0.0
    R_eq_predicted_val = 0.0
    stability_ind = 0.0
    a_grav_f_val = 0.0
    a_inward_f_val = 0.0
    a_Q_f_val = 0.0
    a_net_f_val = 0.0
    artifact_R_f_val = 0.0
    ep_motion = "unknown"
    pos_vel_eps = 0
    max_outward_v = 0.0
    overshoot_ct = 0
    mem_track_ratio = 0.0

    if rec_idx > 0:
        R_f = float(R_arr[-1])
        R_f_safe = max(abs(R_f), 1e-30)
        a_g_f = G_SI * M_kg / (R_f_safe ** 2)
        Md_f = float(Md_arr[-1])
        a_grav_f_val = a_g_f
        a_inward_f_val = (1.0 - alpha_vac) * a_g_f + alpha_vac * Md_f

        # Memory tracking ratio: M_drive / a_grav
        mem_track_ratio = Md_f / a_g_f if a_g_f > 0 else 0.0

        # L_stiff artifact prediction — DIRECT closed-form, no V_ff at final R
        # R_artifact = (V_tol^2 * 2GM / H_cap^2)^(1/3)
        artifact_R_f_val = (
            (V_tol_frac ** 2 * 2.0 * G_SI * M_kg / H_cap ** 2) ** (1.0 / 3.0)
            / r_s if r_s > 0 else 0.0
        )

        # Endpoint motion diagnostics — honest classification
        # Noise floor for velocity sign detection
        V_ff_final = math.sqrt(2.0 * G_SI * M_kg / R_f_safe) if R_f_safe > 0 else 1.0
        V_noise = 1e-10 * V_ff_final

        # Predicted R_eq for hysteresis threshold
        R_eq_m = (
            epsilon_Q ** (1.0 / beta_Q) * r_s
            if epsilon_Q > 0 and r_s > 0
            else R_f_safe
        )

        # Count positive velocity episodes (noise-filtered)
        pos_vel_eps_real = 0
        max_outward_v_real = 0.0
        for i in range(1, rec_idx):
            if float(V_arr[i]) > V_noise:
                max_outward_v_real = max(max_outward_v_real, float(V_arr[i]))
                if float(V_arr[i - 1]) <= V_noise:
                    pos_vel_eps_real += 1

        # Count R direction changes (oscillations) with R-side hysteresis
        overshoot_ct = 0
        R_hyst = 1e-6 * R_eq_m  # hysteresis: ignore sub-ppm R jitter
        for i in range(2, rec_idx):
            dR_prev = float(R_arr[i - 1]) - float(R_arr[i - 2])
            dR_curr = float(R_arr[i]) - float(R_arr[i - 1])
            if (dR_prev * dR_curr < 0
                    and abs(dR_curr) > R_hyst
                    and abs(dR_prev) > R_hyst):
                overshoot_ct += 1

        # bounce_violation: shell escapes — quantitative definition:
        #   (a) sustained positive velocity above noise, AND
        #   (b) shell moved away from R_eq by > 50% (R > 1.5 * R_eq), AND
        #   (c) does not re-converge (final R still > 1.2 * R_eq)
        escaped = (
            max_outward_v_real > V_noise
            and R_f_safe > 1.2 * R_eq_m
            and any(float(R_arr[i]) > 1.5 * R_eq_m for i in range(rec_idx))
        )

        if max_outward_v_real <= V_noise:
            ep_motion = "sign_definite_infall"
        elif escaped:
            ep_motion = "bounce_violation"
        elif pos_vel_eps_real > 0 and overshoot_ct > 2:
            ep_motion = "overshoot_damped"
        elif pos_vel_eps_real > 0:
            ep_motion = "equilibrium_restoring"
        else:
            ep_motion = "sign_definite_infall"  # noise-only flips filtered out

        pos_vel_eps = pos_vel_eps_real
        max_outward_v = max_outward_v_real

    # OP_QPRESS_001 force decomposition and stability at endpoint
    if epsilon_Q > 0.0 and r_s > 0.0 and rec_idx > 0:
        a_Q_f = a_g_f * epsilon_Q * (r_s / R_f_safe) ** beta_Q
        a_Q_f_val = a_Q_f
        a_net_f = a_inward_f_val - a_Q_f
        a_net_f_val = a_net_f
        # Dimensionless force balance: |a_net| / a_grav (canonical convention)
        force_balance_res = abs(a_net_f) / a_g_f if a_g_f > 0 else 0.0

        # Analytical prediction: R_eq/r_s = epsilon_Q^(1/beta_Q)
        R_eq_predicted_val = epsilon_Q ** (1.0 / beta_Q)

        # Stability eigenvalue: d(a_net)/dR at R=R_f
        # a_net = GM/R^2 * [1 - epsilon_Q * (r_s/R)^beta_Q]  (after M_drive saturates)
        # d(a_net)/dR = -2GM/R^3 * [1 - ((2+beta_Q)/2) * epsilon_Q * (r_s/R)^beta_Q]
        # At R=R_eq where epsilon_Q*(r_s/R_eq)^beta_Q = 1:
        #   = -2GM/R^3 * [1 - (2+beta_Q)/2] = -2GM/R^3 * (-beta_Q/2) = beta_Q*GM/R^3 > 0 ✓
        ratio = epsilon_Q * (r_s / R_f_safe) ** beta_Q
        stability_ind = -2.0 * a_g_f / R_f_safe * (1.0 - (2.0 + beta_Q) / 2.0 * ratio)
    elif rec_idx > 0:
        # epsilon_Q=0: no barrier, report net = inward
        a_net_f_val = a_inward_f_val

    # Phase III-A: order parameter and supporting diagnostics
    barrier_dom_val = 0.0
    if a_inward_f_val > 0 and a_Q_f_val > 0:
        barrier_dom_val = a_Q_f_val / a_inward_f_val
    compactness_f_val = r_s / R_f_safe if R_f_safe > 0 else 0.0

    return CollapseResult(
        t_s=t_arr,
        R_m=R_arr,
        V_ms=V_arr,
        M_drive=Md_arr,
        compactness=comp_arr,
        is_trapped=trap_arr,
        K_kretschner=K_arr,
        tau_eff_s=tau_eff_arr,
        a_eff=a_eff_arr,
        E_kinetic=Ek_arr,
        E_potential=Ep_arr,
        E_dissipated_cumul=Ed_arr,
        r_sat_m=r_sat_m,
        t_sat_s=t_sat_s,
        r_sat_over_r_s=r_sat_over_r_s,
        bounce_detected=bounce_detected,
        K_at_sat=K_at_sat,
        compactness_at_sat=comp_at_sat,
        trapped_at_sat=trapped_at_sat,
        ah_crossings=ah_crossings,
        inputs={
            "M_kg": M_kg,
            "R0_m": R0_m,
            "tau0_s": tau0_s,
            "alpha_vac": alpha_vac,
            "gamma_diss": gamma_diss,
            "H_cap": H_cap,
            "n_steps": n_steps,
            "local_tau_mode": local_tau_mode,
            "epsilon_Q": epsilon_Q,
            "beta_Q": beta_Q,
            "V0_mps": V0_mps,
        },
        r_s_m=r_s,
        t_ff_s=t_ff,
        n_steps_taken=n_taken,
        termination_reason=termination,
        l_stiff_activations=l_stiff_count,
        max_compactness=float(np.max(comp_arr)) if rec_idx > 0 else 0.0,
        # Phase-G refined classification
        collapse_class=collapse_cls,
        collapse_fraction=collapse_frac,
        a_eff_min=a_eff_min_val,
        M_drive_min=M_drive_min_val,
        bounce_exclusion_tier=bounce_tier,
        # Timescale competition
        tau0_over_t_dyn=tau0_over_tff,
        tau_eff_over_t_dyn_final=tau_eff_over_tdyn_f,
        # Step-budget diagnostics
        step_budget_fraction=budget_frac,
        step_budget_exhausted=budget_exhausted,
        t_total_over_t_ff=t_total_over_tff,
        # OP_QPRESS_001 diagnostics
        a_Q=a_Q_arr,
        force_balance_residual=force_balance_res,
        R_eq_predicted=R_eq_predicted_val,
        asymptotic_stability_indicator=stability_ind,
        a_grav_final=a_grav_f_val,
        a_inward_final=a_inward_f_val,
        a_outward_final=a_Q_f_val,
        a_net_final=a_net_f_val,
        artifact_R_f=artifact_R_f_val,
        endpoint_motion_class=ep_motion,
        positive_velocity_episodes=pos_vel_eps,
        max_outward_velocity=max_outward_v,
        overshoot_count=overshoot_ct,
        memory_tracking_ratio_final=mem_track_ratio,
        # Phase III-A order parameter
        barrier_dominance_final=barrier_dom_val,
        compactness_final=compactness_f_val,
    )


# ── Mass sweep ───────────────────────────────────────────────────

def compute_mass_sweep(
    *,
    M_min_kg: float,
    M_max_kg: float,
    n_masses: int,
    R0_factor: float = 10.0,
    tau0_s: float,
    alpha_vac: float = 1.0 / 3.0,
    gamma_diss: float = 1e-15,
    H_cap: float = 1e6 / SEC_PER_YEAR,
    n_steps: int = 50_000,
    local_tau_mode: str = "off",
    epsilon_Q: float = 0.0,
    beta_Q: float = 2.0,
) -> List[Dict[str, Any]]:
    """Sweep r_sat over a logarithmic mass range.

    Parameters
    ----------
    M_min_kg, M_max_kg : mass range (kg)
    n_masses : number of mass points
    R0_factor : initial radius as multiple of r_s  (R0 = R0_factor * r_s)
    tau0_s, alpha_vac, gamma_diss, H_cap : physics parameters
    n_steps : max steps per run
    local_tau_mode : "off" | "tier0" — local memory closure

    Returns
    -------
    List of dicts with M_kg, r_s, r_sat, r_sat_over_r_s, t_sat, bounce,
    K_at_sat, termination.
    """
    if n_masses < 2:
        raise CollapseError("n_masses must be >= 2")
    if M_min_kg <= 0 or M_max_kg <= M_min_kg:
        raise CollapseError("Need 0 < M_min < M_max")

    masses = np.logspace(math.log10(M_min_kg), math.log10(M_max_kg), n_masses)
    rows: List[Dict[str, Any]] = []

    for M in masses:
        r_s = compute_schwarzschild_radius(float(M))
        R0 = R0_factor * r_s

        result = compute_collapse(
            M_kg=float(M),
            R0_m=R0,
            tau0_s=tau0_s,
            alpha_vac=alpha_vac,
            gamma_diss=gamma_diss,
            H_cap=H_cap,
            n_steps=n_steps,
            local_tau_mode=local_tau_mode,
            epsilon_Q=epsilon_Q,
            beta_Q=beta_Q,
        )
        rows.append({
            "M_kg": float(M),
            "r_s_m": r_s,
            "R0_m": R0,
            "r_sat_m": result.r_sat_m,
            "r_sat_over_r_s": result.r_sat_over_r_s,
            "t_sat_s": result.t_sat_s,
            "bounce_detected": result.bounce_detected,
            "K_at_sat": result.K_at_sat,
            "compactness_at_sat": result.compactness_at_sat,
            "trapped_at_sat": result.trapped_at_sat,
            "termination": result.termination_reason,
            "l_stiff_activations": result.l_stiff_activations,
            "max_compactness": result.max_compactness,
            "n_steps_taken": result.n_steps_taken,
            # Phase-G refined classification
            "collapse_class": result.collapse_class,
            "collapse_fraction": result.collapse_fraction,
            "a_eff_min": result.a_eff_min,
            "M_drive_min": result.M_drive_min,
            "bounce_exclusion_tier": result.bounce_exclusion_tier,
            # Timescale competition
            "tau0_over_t_dyn": result.tau0_over_t_dyn,
            "tau_eff_over_t_dyn_final": result.tau_eff_over_t_dyn_final,
            # Step-budget diagnostics
            "step_budget_fraction": result.step_budget_fraction,
            "step_budget_exhausted": result.step_budget_exhausted,
            "t_total_over_t_ff": result.t_total_over_t_ff,
            # OP_QPRESS_001 diagnostics
            "force_balance_residual": result.force_balance_residual,
            "R_eq_predicted": result.R_eq_predicted,
            "asymptotic_stability_indicator": result.asymptotic_stability_indicator,
            "endpoint_motion_class": result.endpoint_motion_class,
            "a_grav_final": result.a_grav_final,
            "a_outward_final": result.a_outward_final,
            "a_net_final": result.a_net_final,
            "artifact_R_f": result.artifact_R_f,
            "memory_tracking_ratio_final": result.memory_tracking_ratio_final,
        })

    return rows


def fit_rsat_scaling(
    masses: np.ndarray,
    r_sats: np.ndarray,
) -> Tuple[float, float]:
    """Fit log-log slope of r_sat vs M.

    Returns (slope, intercept).
    """
    if masses.size < 2:
        raise CollapseError("Need >= 2 points for slope fit")
    valid = (masses > 0) & (r_sats > 0) & np.isfinite(masses) & np.isfinite(r_sats)
    if np.sum(valid) < 2:
        raise CollapseError("Need >= 2 valid (positive, finite) points")
    logm = np.log10(masses[valid])
    logr = np.log10(r_sats[valid])
    slope, intercept = np.polyfit(logm, logr, 1)
    return float(slope), float(intercept)
