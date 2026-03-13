"""Interior wave-equation module — Phase III-C WP2C.

Determines whether the Barrier-Dominated Compact Core (BDCC) behaves
primarily as a REACTIVE medium, a DISSIPATIVE medium, or a MIXED
VISCOELASTIC medium for perturbations at the QNM frequency.

STATUS: CANDIDATE — zeroth-order interior response estimate
EXTERIOR ASSUMPTION: Schwarzschild-like (WP1 conditional)
PREDECESSOR: WP2B impedance reflectivity (sharp-boundary approximation)

VISCOELASTIC FRAMING:
The BDCC is treated as a viscoelastic medium with two response channels:
  1. STORAGE (reactive): elastic energy stored per cycle → reflection
  2. LOSS (dissipative): energy absorbed/thermalized per cycle → absorption

In standard viscoelastic language:
  - Storage modulus G' ~ omega_core^2 (restoring force from stability eigenvalue)
  - Loss modulus G'' ~ omega * gamma_eff (energy dissipation per cycle)
  - Loss tangent tan(delta) = G''/G' = 1/(2Q)

The quality factor Q = omega_core / (2 * gamma_eff) maps directly:
  - Q >> 1: storage-dominated (reactive, high reflection)
  - Q ~ 1:  mixed viscoelastic (frequency-dependent, band-limited echoes)
  - Q << 1: loss-dominated (dissipative, low reflection)

WHAT THIS MODULE COMPUTES:
- Storage and loss moduli from stability eigenvalue and damping rates
- Quality factor Q (reactive vs dissipative diagnostic)
- Loss tangent tan(delta) = 1/(2Q) (viscoelastic characterization)
- Interior response classification: reactive / dissipative / mixed / underdetermined
- Effective damping rate from solver dissipation and memory coupling
- Frequency-dependent interior reflection estimate (beyond sharp-boundary)

WHAT THIS MODULE DOES NOT COMPUTE:
- Covariant wave equation on GRUT-modified interior metric (requires GR
  perturbation theory with memory coupling — missing closure)
- Exact interior effective potential V_int(r) (requires metric coefficients)
- Spin/angular mode coupling (Schwarzschild l=2 only)
- Kerr interior wave structure
- Whether information saturation implies elasticity (tested, not assumed)

APPROXIMATIONS:
- Treats the BDCC as a damped harmonic oscillator with parameters drawn
  from the collapse solver (omega_core, gamma_diss, memory coupling)
- This is a ZEROTH-ORDER MODEL, not a wave-equation solution
- The interior is modeled as a single-mode resonator, not a continuous
  medium with a spatially-varying potential
- All results are ORDER OF MAGNITUDE estimates

NONCLAIMS:
- This does NOT solve the wave equation on the GRUT interior metric.
- The reactive/dissipative/mixed classification is a CANDIDATE assessment
  based on available solver parameters, not a rigorous determination.
- Does NOT assume information saturation implies perfect elasticity.
- Does NOT assume dissipation disappears at the endpoint.
- The quality factor Q is estimated from the solver's dissipation
  operator (phenomenological) and memory-mediated damping (structural).
- A proper determination requires the covariant interior metric and
  its perturbation theory — a missing closure.
- Hidden dissipation mechanisms (nonlinear mode coupling, quantum
  effects, transition-width absorption) are NOT modeled and could
  change the classification.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Physical constants (SI) — must match ringdown.py
G_SI = 6.674e-11          # m^3 kg^-1 s^-2
C_SI = 299_792_458.0      # m/s
M_SUN = 1.989e30          # kg


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class InteriorWaveParams:
    """Input parameters for interior wave analysis.

    All quantities in SI unless otherwise noted.
    """
    # Black hole parameters
    M_kg: float = 0.0           # Total mass (kg)
    R_eq_m: float = 0.0         # Endpoint radius (m)
    r_s_m: float = 0.0          # Schwarzschild radius (m)

    # Stability structure (from collapse solver)
    beta_Q: float = 2.0         # Barrier exponent
    epsilon_Q: float = 1.0/9.0  # Quantum pressure coupling

    # Dissipation (from collapse solver)
    gamma_diss: float = 1e-15   # Dissipation rate (1/s)

    # Memory coupling (from collapse solver)
    alpha_vac: float = 1.0/3.0  # Vacuum susceptibility
    tau0_s: float = 1.3225e15   # Memory relaxation time (s)

    # Frequency of interest (default: QNM frequency)
    omega_probe_rad_s: float = 0.0  # Probing frequency (rad/s)
    # If 0, will be set to QNM frequency internally.


@dataclass
class InteriorWaveResult:
    """Results of interior wave analysis.

    STATUS: CANDIDATE — zeroth-order interior response estimate.
    All results are CONDITIONAL on the WP1 exterior assumption.
    """
    # BDCC oscillation (from stability eigenvalue)
    omega_core_rad_s: float = 0.0   # Natural frequency (rad/s)
    f_core_Hz: float = 0.0          # Natural frequency (Hz)

    # Effective damping
    gamma_eff_rad_s: float = 0.0    # Effective damping rate (rad/s)
    # Combines solver dissipation (gamma_diss) and memory-mediated damping.

    # Quality factor — KEY DIAGNOSTIC
    quality_factor_Q: float = 0.0
    # Q = omega_core / (2 * gamma_eff)
    # Q >> 1: REACTIVE (oscillator stores energy, high reflection)
    # Q ~ 1:  MIXED VISCOELASTIC (frequency-dependent)
    # Q << 1: OVERDAMPED / DISSIPATIVE (absorbs energy, low reflection)

    # Viscoelastic characterization
    loss_tangent: float = 0.0
    # tan(delta) = 1 / (2Q) = gamma_eff / omega_core
    # << 1: storage-dominated (reactive)
    # ~ 1:  mixed viscoelastic
    # >> 1: loss-dominated (dissipative)

    storage_modulus_proxy: float = 0.0
    # G' proxy ~ omega_core^2 (dimensionless, normalized to GM/R_eq^3)
    # Represents the elastic restoring force from the stability eigenvalue.

    loss_modulus_proxy: float = 0.0
    # G'' proxy ~ omega_probe * gamma_eff (dimensionless, same normalization)
    # Represents energy dissipated per cycle at the probing frequency.

    # Frequency ratio
    omega_probe_over_omega_core: float = 0.0
    # omega_QNM / omega_core — determines which regime we're in.
    # >> 1: probe frequency far above natural frequency (typical case)

    # Interior response function
    response_amplitude: float = 0.0
    # |chi(omega_probe)| — amplitude of the oscillator response function.
    # For a damped oscillator: chi = 1 / sqrt((1-x^2)^2 + (x/Q)^2)
    # where x = omega_probe / omega_core.
    # When x >> 1 and Q >> 1: chi ~ 1/x^2 (reactive, off-resonance)
    # When x >> 1 and Q << 1: chi ~ Q/x   (dissipative, overdamped)

    # Interior reflection estimate
    r_interior_amp: float = 0.0
    # Amplitude reflection coefficient estimated from interior response.
    # This goes BEYOND the sharp-boundary impedance model by incorporating
    # the frequency-dependent interior dynamics.

    # Damping timescale vs crossing time
    damping_time_s: float = 0.0     # 1 / gamma_eff (s)
    crossing_time_s: float = 0.0    # R_eq / c_s (s) — light crossing of BDCC
    damping_over_crossing: float = 0.0
    # If >> 1: perturbation survives many crossings → reactive
    # If << 1: perturbation damped before one crossing → dissipative

    # Memory coupling diagnostics
    memory_damping_rate: float = 0.0   # Memory-mediated damping (rad/s)
    solver_damping_rate: float = 0.0   # Direct solver gamma_diss (rad/s)

    # Classification — THE KEY OUTPUT
    response_class: str = "underdetermined"
    # "reactive_candidate"            — Q >> 10, storage-dominated, high reflection
    # "mixed_viscoelastic_candidate"  — 1 < Q < 10, both channels active
    # "dissipative_candidate"         — Q < 1, loss-dominated, low reflection
    # "underdetermined"               — insufficient information to classify

    response_confidence: str = "zeroth_order"
    # "zeroth_order" — based on damped oscillator model with solver params
    # "computed"     — from proper wave equation (future)

    # Impact on echo channel
    echo_impact: str = ""
    # Human-readable assessment of what this means for the echo falsifier.

    # Nonclaims
    nonclaims: List[str] = field(default_factory=list)

    # Missing closures
    required_closures: List[str] = field(default_factory=list)


# ============================================================================
# CORE COMPUTATIONS
# ============================================================================

def schwarzschild_radius(M_kg: float) -> float:
    """Compute Schwarzschild radius r_s = 2GM/c^2."""
    return 2.0 * G_SI * M_kg / (C_SI * C_SI)


def bdcc_oscillation_frequency(
    M_kg: float,
    R_eq_m: float,
    beta_Q: float = 2.0,
) -> float:
    """Natural radial oscillation frequency of the BDCC.

    From the stability eigenvalue: k_eff = beta_Q * GM / R_eq^3
    omega_core^2 ~ k_eff / R_eq = beta_Q * GM / R_eq^4

    Same formula as ringdown.py — duplicated here for module independence.
    """
    if R_eq_m <= 0 or M_kg <= 0:
        return 0.0
    k_eff = beta_Q * G_SI * M_kg / (R_eq_m ** 3)
    omega_sq = k_eff / R_eq_m
    return math.sqrt(omega_sq) if omega_sq > 0 else 0.0


def schwarzschild_qnm_l2(M_kg: float) -> float:
    """Fundamental l=2 QNM real frequency for Schwarzschild (rad/s)."""
    if M_kg <= 0:
        return 0.0
    M_geom = G_SI * M_kg / (C_SI ** 3)
    return 0.3737 / M_geom


def memory_mediated_damping(
    M_kg: float,
    R_eq_m: float,
    alpha_vac: float,
    tau0_s: float,
    omega_core: float,
) -> float:
    """Estimate memory-mediated damping rate at the BDCC.

    The memory kernel acts as a low-pass filter with effective time
    constant tau_eff. At the BDCC equilibrium (V ~ 0), the local
    tau_eff is approximately:

        tau_eff ~ tau0_local

    where tau0_local uses the tier-0 closure:

        tau0_local = tau0 * t_dyn / (t_dyn + tau0)

    The memory coupling contributes damping at a rate proportional to
    alpha_vac / tau_eff_local. This is because the memory state M_drive
    tracks a_grav with time constant tau_eff — perturbations at
    frequencies >> 1/tau_eff are not tracked by memory, creating a
    phase mismatch that acts as effective damping.

    ORDER OF MAGNITUDE: gamma_memory ~ alpha_vac * omega_core^2 * tau_eff_local
    when omega_core * tau_eff >> 1 (which is true for astrophysical BHs).

    Parameters
    ----------
    M_kg : float
        Black hole mass (kg).
    R_eq_m : float
        Endpoint radius (m).
    alpha_vac : float
        Vacuum susceptibility.
    tau0_s : float
        Memory relaxation time (s).
    omega_core : float
        BDCC natural frequency (rad/s).

    Returns
    -------
    float
        Memory-mediated damping rate (rad/s). Always >= 0.
    """
    if M_kg <= 0 or R_eq_m <= 0 or alpha_vac <= 0 or tau0_s <= 0:
        return 0.0

    # Local dynamical time at R_eq
    t_dyn_local = math.sqrt(R_eq_m ** 3 / (2.0 * G_SI * M_kg))

    # Tier-0 local tau
    tau_local = tau0_s * t_dyn_local / (t_dyn_local + tau0_s)
    tau_local = max(tau_local, 1e-30)

    # Memory damping: the memory kernel responds at rate 1/tau_local.
    # At frequencies omega >> 1/tau_local, the memory cannot track the
    # perturbation, and the fraction alpha_vac of the restoring force
    # that comes through memory is effectively "delayed", acting as
    # damping.
    #
    # For a harmonic oscillator with fraction alpha of the spring
    # constant mediated by a low-pass filter with time constant tau:
    #   gamma_memory ~ alpha / (2 * tau) when omega * tau >> 1
    #   gamma_memory ~ alpha * omega^2 * tau / 2 when omega * tau << 1
    #
    # At the BDCC: omega_core * tau_local can be either regime depending
    # on mass. We use the interpolated formula:
    #   gamma_memory = alpha_vac * omega_core / (2 * (1 + (omega_core * tau_local)^2)) * omega_core * tau_local
    # Which simplifies to:
    #   gamma_memory = alpha_vac * omega_core^2 * tau_local / (2 * (1 + (omega_core * tau_local)^2))

    x = omega_core * tau_local
    gamma_mem = alpha_vac * omega_core * omega_core * tau_local / (2.0 * (1.0 + x * x))

    return max(gamma_mem, 0.0)


def effective_damping_rate(
    M_kg: float,
    R_eq_m: float,
    alpha_vac: float,
    tau0_s: float,
    gamma_diss: float,
    omega_core: float,
) -> tuple:
    """Total effective damping rate at the BDCC.

    Combines:
    1. Solver dissipation (gamma_diss) — phenomenological damping
    2. Memory-mediated damping — from the memory kernel's finite response time

    Parameters
    ----------
    (all physical parameters as described above)

    Returns
    -------
    tuple
        (gamma_eff, gamma_mem, gamma_solver) all in rad/s.
    """
    gamma_mem = memory_mediated_damping(
        M_kg, R_eq_m, alpha_vac, tau0_s, omega_core
    )
    gamma_solver = gamma_diss

    # Total effective damping
    gamma_eff = gamma_solver + gamma_mem

    return (gamma_eff, gamma_mem, gamma_solver)


def quality_factor(omega_core: float, gamma_eff: float) -> float:
    """Quality factor Q = omega_core / (2 * gamma_eff).

    Q >> 1: reactive (underdamped), stores and reflects energy
    Q ~ 1:  critically damped (marginal)
    Q << 1: overdamped / dissipative, absorbs energy

    Parameters
    ----------
    omega_core : float
        Natural frequency (rad/s).
    gamma_eff : float
        Effective damping rate (rad/s).

    Returns
    -------
    float
        Quality factor Q. Returns inf if gamma_eff = 0 (undamped).
    """
    if gamma_eff <= 0:
        return float("inf") if omega_core > 0 else 0.0
    return omega_core / (2.0 * gamma_eff)


def oscillator_response(
    omega_probe: float,
    omega_core: float,
    Q: float,
) -> float:
    """Amplitude response of a damped harmonic oscillator.

    |chi(omega)| = 1 / sqrt((1 - x^2)^2 + (x/Q)^2)

    where x = omega_probe / omega_core.

    This is the standard frequency response of a driven damped oscillator.
    It determines how much the BDCC "responds" to an incoming perturbation
    at frequency omega_probe (typically omega_QNM).

    Parameters
    ----------
    omega_probe : float
        Probing frequency (rad/s).
    omega_core : float
        Natural frequency (rad/s).
    Q : float
        Quality factor.

    Returns
    -------
    float
        |chi(omega_probe)| — dimensionless response amplitude.
    """
    if omega_core <= 0:
        return 0.0

    x = omega_probe / omega_core
    if x <= 0:
        return 1.0  # DC response

    denom_sq = (1.0 - x * x) ** 2
    if Q > 0 and math.isfinite(Q):
        denom_sq += (x / Q) ** 2
    # else Q = inf means no damping term

    if denom_sq <= 0:
        return float("inf")  # At resonance with no damping

    return 1.0 / math.sqrt(denom_sq)


def interior_reflection_estimate(
    omega_probe: float,
    omega_core: float,
    R_eq_m: float,
    Q: float,
) -> float:
    """Estimate interior amplitude reflection coefficient.

    Goes beyond the sharp-boundary impedance model by incorporating
    the frequency-dependent interior response.

    Physical picture: The BDCC acts as a resonator. An incoming wave
    at frequency omega_probe drives the resonator. The reflection
    depends on both the impedance mismatch AND the interior response.

    For a reactive resonator (Q >> 1) probed far off resonance
    (omega_probe >> omega_core): the BDCC is effectively rigid at that
    frequency, giving high reflection (consistent with impedance model).

    For a dissipative resonator (Q << 1): incoming energy is absorbed,
    giving low reflection (consistent with Boltzmann model).

    The interpolation uses:
        r_interior_amp = r_impedance * f(Q, x)

    where r_impedance is the sharp-boundary value and f captures the
    Q-dependent correction:
        f(Q, x) = 1 - (1/Q^2) * chi^2  for Q > 1
        f(Q, x) = Q^2 * chi^2          for Q < 1

    This is a ZEROTH-ORDER ESTIMATE. The actual reflection requires
    the full wave equation solution.

    Parameters
    ----------
    omega_probe : float
        Probing frequency (rad/s).
    omega_core : float
        Natural frequency (rad/s).
    R_eq_m : float
        Endpoint radius (m).
    Q : float
        Quality factor.

    Returns
    -------
    float
        Estimated amplitude reflection coefficient in [0, 1].
    """
    if omega_core <= 0 or R_eq_m <= 0:
        return 0.0

    # Base impedance ratio (same as WP2B)
    c_s_bdcc = omega_core * R_eq_m
    eta = c_s_bdcc / C_SI

    # Sharp-boundary reflection (WP2B impedance model)
    if eta <= 0:
        return 0.0
    r_impedance = abs(1.0 - eta) / (1.0 + eta)

    # Q-dependent correction factor
    if not math.isfinite(Q) or Q <= 0:
        # Q = inf (undamped) → pure impedance model
        return max(0.0, min(1.0, r_impedance))

    # For high Q (reactive): correction is small, reflection stays high
    # For low Q (dissipative): reflection is suppressed
    #
    # Physical reasoning: The fraction of incident energy that is
    # reflected depends on how much the resonator absorbs per cycle.
    # Absorption per cycle ~ 1/Q. For Q >> 1, almost no absorption.
    # For Q << 1, strong absorption.
    #
    # We model this as:
    #   r_eff = r_impedance * (1 - absorption_factor)
    #   absorption_factor = min(1, 1/(Q * max(1, x)))
    # where x = omega_probe / omega_core.
    # This ensures:
    #   - Q >> 1: absorption_factor → 0, r_eff → r_impedance
    #   - Q << 1: absorption_factor → 1, r_eff → 0
    #   - x >> 1, Q ~ 1: moderate absorption

    x = omega_probe / omega_core if omega_core > 0 else 0.0
    x_eff = max(1.0, x)

    absorption_factor = 1.0 / (Q * x_eff)
    absorption_factor = min(1.0, absorption_factor)

    r_eff = r_impedance * (1.0 - absorption_factor)
    return max(0.0, min(1.0, r_eff))


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def compute_interior_wave_analysis(
    params: InteriorWaveParams,
) -> InteriorWaveResult:
    """Run interior wave analysis for given parameters.

    This is the main entry point for WP2C. It determines whether
    the BDCC is reactive or dissipative by estimating the quality
    factor Q from available solver parameters.

    Parameters
    ----------
    params : InteriorWaveParams
        Input parameters including mass, endpoint, and dissipation.

    Returns
    -------
    InteriorWaveResult
        Complete interior wave analysis with classification.
    """
    r_s = params.r_s_m
    if r_s <= 0:
        r_s = schwarzschild_radius(params.M_kg)
    R_eq = params.R_eq_m
    if R_eq <= 0 and r_s > 0:
        R_eq = r_s / 3.0  # Default: constrained endpoint

    # ── BDCC natural frequency ──
    omega_core = bdcc_oscillation_frequency(
        params.M_kg, R_eq, params.beta_Q
    )
    f_core = omega_core / (2.0 * math.pi) if omega_core > 0 else 0.0

    # ── Probing frequency ──
    omega_probe = params.omega_probe_rad_s
    if omega_probe <= 0:
        omega_probe = schwarzschild_qnm_l2(params.M_kg)

    # ── Effective damping ──
    gamma_eff, gamma_mem, gamma_solver = effective_damping_rate(
        params.M_kg, R_eq, params.alpha_vac, params.tau0_s,
        params.gamma_diss, omega_core,
    )

    # ── Quality factor ──
    Q = quality_factor(omega_core, gamma_eff)

    # ── Frequency ratio ──
    freq_ratio = omega_probe / omega_core if omega_core > 0 else 0.0

    # ── Interior response ──
    chi = oscillator_response(omega_probe, omega_core, Q)

    # ── Interior reflection estimate ──
    r_int = interior_reflection_estimate(
        omega_probe, omega_core, R_eq, Q,
    )

    # ── Damping vs crossing timescales ──
    damping_t = 1.0 / gamma_eff if gamma_eff > 0 else float("inf")
    c_s_bdcc = omega_core * R_eq if omega_core > 0 and R_eq > 0 else 0.0
    crossing_t = R_eq / c_s_bdcc if c_s_bdcc > 0 else float("inf")
    damp_over_cross = damping_t / crossing_t if crossing_t > 0 and math.isfinite(crossing_t) else float("inf")

    # ── Viscoelastic characterization ──
    # Storage modulus proxy: G' ~ omega_core^2 (elastic restoring force)
    # Loss modulus proxy: G'' ~ omega_probe * gamma_eff (dissipation per cycle)
    # Both normalized to GM/R_eq^3 for dimensionless comparison.
    norm = G_SI * params.M_kg / (R_eq ** 3) if R_eq > 0 and params.M_kg > 0 else 1.0
    storage_mod = (omega_core ** 2) / norm if norm > 0 else 0.0
    loss_mod = (omega_probe * gamma_eff) / norm if norm > 0 else 0.0
    loss_tan = gamma_eff / omega_core if omega_core > 0 else float("inf")
    # Equivalently: loss_tan = 1 / (2Q)

    # ── Classification ──
    # Thresholds for classification (zeroth-order):
    #   Q > 10:    reactive / storage-dominated (high reflection expected)
    #   1 < Q < 10: mixed viscoelastic (both channels active)
    #   Q < 1:     dissipative / loss-dominated (low reflection expected)
    #
    # Equivalently in loss tangent:
    #   tan(delta) < 0.05: reactive
    #   0.05 < tan(delta) < 0.5: mixed
    #   tan(delta) > 0.5: dissipative
    #
    # NOTE: These thresholds are ORDER OF MAGNITUDE conventions.
    # The actual classification requires the interior wave equation.
    Q_REACTIVE_THRESHOLD = 10.0
    Q_MIXED_THRESHOLD = 1.0

    if not math.isfinite(Q):
        response_cls = "reactive"
        echo_impact = (
            "Q = inf (zero effective damping). "
            "BDCC is purely reactive (storage-dominated) under current "
            "solver parameters. Impedance model reflection estimates "
            "(WP2B) apply without correction. Echo channel is PROMISING. "
            "WARNING: zero damping may be an artifact of incomplete "
            "dissipation modeling."
        )
    elif Q > Q_REACTIVE_THRESHOLD:
        response_cls = "reactive"
        echo_impact = (
            f"Q = {Q:.1f} >> 1 (tan(delta) = {loss_tan:.4f}). "
            "BDCC is storage-dominated (reactive). "
            "Loss channel is subdominant. "
            "Impedance model reflection estimates (WP2B) apply with "
            f"small Q-dependent correction ({1.0/(Q * max(1.0, freq_ratio))*100:.2f}% absorption). "
            "Echo channel is PROMISING under this model."
        )
    elif Q > Q_MIXED_THRESHOLD:
        response_cls = "mixed_viscoelastic"
        echo_impact = (
            f"Q = {Q:.2f} (tan(delta) = {loss_tan:.3f}). "
            "BDCC is in the mixed viscoelastic regime. "
            "Both storage and loss channels are active. "
            "Reflection is frequency-dependent: reduced from impedance "
            "model but not negligible. "
            "Echoes may be band-limited or weaker than impedance model predicts. "
            "Echo channel status is UNCERTAIN — requires interior wave equation."
        )
    else:
        response_cls = "dissipative"
        echo_impact = (
            f"Q = {Q:.4f} << 1 (tan(delta) = {loss_tan:.2f}). "
            "BDCC is loss-dominated (dissipative). "
            "Incoming perturbation energy is absorbed. "
            "Boltzmann model applies. "
            "Echo channel is NOT promising as a falsifier."
        )

    # ── Nonclaims ──
    nonclaims = [
        "This does NOT solve the wave equation on the GRUT interior metric.",
        "The reactive/dissipative/mixed classification is a CANDIDATE assessment "
        "based on the damped harmonic oscillator model with solver parameters.",
        "Does NOT assume information saturation implies perfect elasticity. "
        "The storage-vs-loss balance is TESTED from solver parameters.",
        "Does NOT assume dissipation disappears at the endpoint. Memory-mediated "
        "damping is the dominant loss channel and is explicitly computed.",
        "The quality factor Q is estimated from gamma_diss (phenomenological) "
        "and memory-mediated damping (from tau_eff coupling). Both are "
        "ORDER OF MAGNITUDE estimates.",
        "A proper determination requires the covariant interior metric and "
        "perturbation theory — a missing closure.",
        "The interior reflection estimate r_interior_amp goes beyond the "
        "sharp-boundary impedance model but is still a zeroth-order "
        "approximation.",
        "All results are CONDITIONAL on the WP1 exterior assumption "
        "(Schwarzschild-like).",
        "The damped oscillator model treats the BDCC as a single-mode "
        "resonator. The actual interior may have a continuous spectrum.",
        "The classification thresholds (Q > 10 reactive, 1 < Q < 10 mixed, "
        "Q < 1 dissipative) are ORDER OF MAGNITUDE conventions.",
        "Hidden dissipation mechanisms (nonlinear mode coupling, quantum "
        "pair production, transition-width absorption) are NOT modeled "
        "and could change the classification.",
    ]

    # ── Required closures ──
    closures = [
        "Covariant GRUT interior metric (needed for proper wave equation)",
        "Interior effective potential V_int(r) from metric perturbation theory",
        "Frequency-dependent boundary condition at R_eq from first principles",
        "Transition-width corrections (Phase III-B finite-width transition)",
        "Multi-mode interior spectrum (beyond single-mode oscillator)",
        "Kerr generalization for astrophysical black holes",
    ]

    return InteriorWaveResult(
        omega_core_rad_s=omega_core,
        f_core_Hz=f_core,
        gamma_eff_rad_s=gamma_eff,
        quality_factor_Q=Q,
        loss_tangent=loss_tan,
        storage_modulus_proxy=storage_mod,
        loss_modulus_proxy=loss_mod,
        omega_probe_over_omega_core=freq_ratio,
        response_amplitude=chi,
        r_interior_amp=r_int,
        damping_time_s=damping_t,
        crossing_time_s=crossing_t,
        damping_over_crossing=damp_over_cross,
        memory_damping_rate=gamma_mem,
        solver_damping_rate=gamma_solver,
        response_class=response_cls,
        response_confidence="zeroth_order",
        echo_impact=echo_impact,
        nonclaims=nonclaims,
        required_closures=closures,
    )


def interior_wave_result_to_dict(
    result: InteriorWaveResult,
) -> Dict[str, Any]:
    """Serialize an InteriorWaveResult to a dict for evidence packets."""
    return {
        "bdcc_oscillation": {
            "omega_core_rad_s": result.omega_core_rad_s,
            "f_core_Hz": result.f_core_Hz,
        },
        "damping": {
            "gamma_eff_rad_s": result.gamma_eff_rad_s,
            "memory_damping_rate": result.memory_damping_rate,
            "solver_damping_rate": result.solver_damping_rate,
        },
        "quality_factor": {
            "Q": result.quality_factor_Q,
            "loss_tangent": result.loss_tangent,
            "note": "Q >> 10 reactive; 1 < Q < 10 mixed viscoelastic; Q < 1 dissipative",
        },
        "viscoelastic": {
            "storage_modulus_proxy": result.storage_modulus_proxy,
            "loss_modulus_proxy": result.loss_modulus_proxy,
            "loss_tangent": result.loss_tangent,
            "note": "G' (storage) vs G'' (loss); tan(delta) = G''/G' = 1/(2Q)",
        },
        "frequency_response": {
            "omega_probe_over_omega_core": result.omega_probe_over_omega_core,
            "response_amplitude_chi": result.response_amplitude,
        },
        "interior_reflection": {
            "r_interior_amp": result.r_interior_amp,
            "note": "zeroth-order estimate beyond sharp-boundary impedance",
        },
        "timescales": {
            "damping_time_s": result.damping_time_s,
            "crossing_time_s": result.crossing_time_s,
            "damping_over_crossing": result.damping_over_crossing,
        },
        "classification": {
            "response_class": result.response_class,
            "response_confidence": result.response_confidence,
            "echo_impact": result.echo_impact,
        },
        "nonclaims": result.nonclaims,
        "required_closures": result.required_closures,
    }


# ============================================================================
# SCANNING UTILITIES
# ============================================================================

# ============================================================================
# WP2D — GRADED-TRANSITION REFLECTIVITY MODEL
# ============================================================================
#
# Replaces the sharp-boundary impedance approximation with a smooth
# transition profile based on Phase III-B barrier dominance mapping.
#
# Phase III-B measured:
#   - Transition width: ~0.703 r_s (Phi = 0.1 to Phi = 0.9)
#   - Phi(R/r_s) is smooth, monotonic, continuously differentiable
#   - Crystallization threshold Phi = 0.5 at R/r_s ≈ 0.4715 (post-horizon)
#   - Endpoint Phi = 1.0 at R/r_s = 1/3 (force-balanced BDCC)
#
# Physical picture:
#   Instead of a sharp impedance step at R_eq, the wave entering the
#   transition zone encounters a graded impedance profile. Each
#   infinitesimal layer partially reflects and partially transmits.
#   The total reflection is the coherent sum of all partial reflections
#   (WKB-like integral over the graded transition).
#
#   For a wave with wavelength lambda_probe:
#     - If lambda_probe >> transition_width: wave "sees" the transition
#       as sharp → reflectivity ≈ sharp-boundary value
#     - If lambda_probe << transition_width: wave propagates adiabatically
#       through the transition → reflectivity suppressed exponentially
#     - lambda_probe ~ transition_width: intermediate regime
#
#   The characteristic wavelength of the QNM probe is:
#     lambda_probe ~ 2*pi*c / omega_QNM ~ 2*pi * M_geom ~ pi * r_s
#
#   Compared to transition width ~0.703 r_s, so lambda_probe ~ pi * r_s
#   is of the same ORDER as the transition width. This means we are NOT
#   safely in the "sharp" limit — the correction is non-trivial.
#
# NONCLAIMS:
#   - This is a ZEROTH-ORDER graded model, not a full wave-equation solution
#   - The Phi(R) profile is parameterized, not derived from the metric
#   - WKB validity requires smooth variation — may break near R_eq
#   - Phase coherence across the transition is assumed (no stochastic loss)
# ============================================================================


@dataclass
class GradedTransitionParams:
    """Parameters for the graded-transition reflectivity model (WP2D).

    Uses Phase III-B barrier dominance Phi(R/r_s) to model the
    transition zone as a smooth impedance gradient.
    """
    # Black hole parameters
    M_kg: float = 0.0
    R_eq_m: float = 0.0        # Endpoint radius (m)
    r_s_m: float = 0.0         # Schwarzschild radius (m)

    # Barrier structure
    beta_Q: float = 2.0
    epsilon_Q: float = 1.0/9.0
    alpha_vac: float = 1.0/3.0

    # Transition zone from Phase III-B
    transition_width_rs: float = 0.703  # Measured width in units of r_s
    # Phi = 0.1 at R/r_s ≈ R_eq/r_s + transition_width_rs
    # Phi = 0.9 at R/r_s ≈ R_eq/r_s + small offset

    # Probing frequency
    omega_probe_rad_s: float = 0.0  # If 0, set to QNM

    # Interior quality factor from WP2C
    quality_factor_Q: float = 7.5  # PDE canon default (was 515.6 pre-PDE proxy; SUPERSEDED)

    # Number of layers for graded computation
    n_layers: int = 100

    # Multi-mode parameters (WP2D spectrum correction)
    n_modes: int = 3            # Number of interior modes (1 = single-mode WP2C)
    # Mode spacing model:
    #   omega_n = omega_core * sqrt(1 + n*(n+1)*xi)
    #   where xi is a dimensionless mode spacing parameter
    mode_spacing_xi: float = 0.1  # Fractional mode spacing parameter


@dataclass
class GradedTransitionResult:
    """Results of graded-transition reflectivity computation (WP2D).

    STATUS: CANDIDATE — zeroth-order graded transition estimate.
    """
    # Sharp-boundary reference (WP2B)
    r_sharp_amp: float = 0.0       # r_surface_amp from impedance model
    r_sharp_pow: float = 0.0       # Power reflectivity = r_sharp^2

    # WP2C single-mode interior reference
    r_interior_amp: float = 0.0    # From WP2C (single-mode, sharp boundary)

    # Graded-transition result
    r_graded_amp: float = 0.0      # Graded-transition amplitude reflectivity
    r_graded_pow: float = 0.0      # Power reflectivity = r_graded^2

    # Multi-mode corrected result
    r_multimode_amp: float = 0.0   # Multi-mode corrected reflectivity
    r_multimode_pow: float = 0.0   # Power reflectivity

    # Combined (graded + multi-mode) — the WP2D best estimate
    r_wp2d_amp: float = 0.0        # Best WP2D estimate
    r_wp2d_pow: float = 0.0        # Power reflectivity

    # Diagnostics
    grading_factor: float = 0.0    # r_graded / r_sharp (< 1 means suppression)
    multimode_factor: float = 0.0  # r_multimode / r_interior (mode correction)
    combined_factor: float = 0.0   # r_wp2d / r_sharp (total correction)

    # Wavelength vs transition width
    lambda_probe_m: float = 0.0    # Probe wavelength (m)
    transition_width_m: float = 0.0  # Transition zone width (m)
    lambda_over_width: float = 0.0  # Ratio — key diagnostic

    # Multi-mode spectrum
    mode_frequencies_rad_s: List[float] = field(default_factory=list)
    mode_quality_factors: List[float] = field(default_factory=list)
    mode_weights: List[float] = field(default_factory=list)

    # Echo impact
    echo_amplitudes_sharp: List[float] = field(default_factory=list)
    echo_amplitudes_graded: List[float] = field(default_factory=list)
    echo_amplitudes_multimode: List[float] = field(default_factory=list)
    echo_amplitudes_wp2d: List[float] = field(default_factory=list)

    # Classification
    transition_regime: str = ""
    # "quasi_sharp"   — lambda >> width, correction < 10%
    # "intermediate"  — lambda ~ width, correction 10-50%
    # "adiabatic"     — lambda << width, strong suppression > 50%

    echo_channel_status: str = ""
    # "strengthened"       — graded correction helps (shouldn't happen normally)
    # "weakened_modestly"  — correction < 30%, channel still viable
    # "weakened_significantly" — correction 30-80%
    # "collapsed"          — correction > 80%, channel no longer viable

    response_class: str = "underdetermined"
    nonclaims: List[str] = field(default_factory=list)
    required_closures: List[str] = field(default_factory=list)


def barrier_dominance_profile(
    r_over_rs: float,
    R_eq_over_rs: float = 1.0 / 3.0,
    transition_width_rs: float = 0.703,
) -> float:
    """Parameterized barrier dominance Phi(R/r_s).

    Uses a logistic (sigmoid) profile calibrated to Phase III-B measurements:
      - Phi(R_eq/r_s = 1/3) = 1.0 (exact force balance at endpoint)
      - Phi rises from ~0 to ~1 over width ~0.703 r_s
      - Crystallization Phi=0.5 at R/r_s ≈ 0.4715

    The profile is:
        Phi(x) = 1 / (1 + exp(-k * (x_cryst - x)))

    where x = R/r_s, x_cryst = crystallization point, and k controls
    the steepness (calibrated from measured width).

    Parameters
    ----------
    r_over_rs : float
        Radial coordinate R/r_s (dimensionless).
    R_eq_over_rs : float
        Endpoint R_eq/r_s (default 1/3).
    transition_width_rs : float
        Measured transition width in r_s units (default 0.703).

    Returns
    -------
    float
        Barrier dominance Phi in [0, 1].
    """
    # Phase III-B measured key points:
    #   R/r_s = 1.0  (horizon):  Phi ~ 0.01
    #   R/r_s = 0.5:             Phi ~ 0.4
    #   R/r_s = 0.4715 (cryst):  Phi = 0.5
    #   R/r_s = 0.35:            Phi ~ 0.9
    #   R/r_s = 1/3 (endpoint):  Phi = 1.0  (exact force balance)
    #
    # We use a power-law profile anchored to three points:
    #   Phi(R_eq/r_s) = 1.0        (endpoint: force balance)
    #   Phi(x_cryst) = 0.5         (crystallization threshold)
    #   Phi(R_eq/r_s + width) = 0  (outer edge of transition)
    #
    # Profile:
    #   t = (r_over_rs - R_eq_over_rs) / transition_width_rs
    #   Phi(t) = max(0, 1 - t^alpha)  for t in [0, 1]
    #   Phi = 1 for t < 0 (inside R_eq, if ever queried)
    #   Phi = 0 for t > 1 (outside transition)
    #
    # alpha is derived from the crystallization constraint:
    #   t_cryst = (x_cryst - R_eq/r_s) / width
    #   t_cryst^alpha = 0.5
    #   alpha = ln(0.5) / ln(t_cryst)

    x_cryst = 0.4715  # Crystallization point

    if transition_width_rs <= 0:
        # Sharp boundary limit
        return 1.0 if r_over_rs <= R_eq_over_rs + 0.01 else 0.0

    # Normalized coordinate: t = 0 at endpoint, t = 1 at outer edge
    t = (r_over_rs - R_eq_over_rs) / transition_width_rs

    if t <= 0:
        return 1.0  # At or below endpoint
    if t >= 1.0:
        return 0.0  # Beyond transition zone

    # Compute alpha from crystallization constraint
    t_cryst = (x_cryst - R_eq_over_rs) / transition_width_rs
    if t_cryst <= 0 or t_cryst >= 1.0:
        alpha = 1.0  # Fallback: linear profile
    else:
        alpha = math.log(0.5) / math.log(t_cryst)
        alpha = max(0.01, min(10.0, alpha))  # Clamp for safety

    phi = 1.0 - t ** alpha
    return max(0.0, min(1.0, phi))


def local_impedance_ratio(
    r_over_rs: float,
    r_s_m: float,
    M_kg: float,
    beta_Q: float,
    Phi: float,
) -> float:
    """Local impedance ratio at position r in the transition zone.

    In the transition zone, the BDCC properties vary with Phi.
    The local effective sound speed interpolates between the vacuum
    (c_s = c, Phi = 0) and the BDCC interior (c_s = omega_core * R_eq, Phi = 1).

    The local impedance ratio is:
        eta_local(r) = Phi(r) * eta_BDCC + (1 - Phi(r)) * eta_vacuum

    where:
        eta_BDCC = omega_core * R_eq / c  (from WP2B, << 1)
        eta_vacuum = 1.0 (vacuum has Z = c)

    So the transition goes from eta = 1 (vacuum) to eta << 1 (BDCC),
    and the impedance mismatch GROWS as we enter the transition zone.

    Parameters
    ----------
    r_over_rs : float
        Radial coordinate R/r_s.
    r_s_m : float
        Schwarzschild radius (m).
    M_kg : float
        Mass (kg).
    beta_Q : float
        Barrier exponent.
    Phi : float
        Barrier dominance at this location.

    Returns
    -------
    float
        Local impedance ratio eta_local (dimensionless).
    """
    # BDCC impedance at the endpoint
    R_eq_m = r_s_m / 3.0  # Constrained endpoint
    omega_core = bdcc_oscillation_frequency(M_kg, R_eq_m, beta_Q)
    if omega_core <= 0 or R_eq_m <= 0:
        return 1.0
    eta_bdcc = omega_core * R_eq_m / C_SI

    # Linear interpolation in impedance
    # Phi = 0 → vacuum (eta = 1)
    # Phi = 1 → BDCC interior (eta = eta_bdcc << 1)
    eta_local = (1.0 - Phi) * 1.0 + Phi * eta_bdcc
    return max(1e-30, eta_local)


def graded_reflection_coefficient(
    M_kg: float,
    r_s_m: float,
    beta_Q: float,
    omega_probe: float,
    transition_width_rs: float = 0.703,
    n_layers: int = 100,
    Q: float = 515.6,
) -> tuple:
    """Compute graded-transition amplitude reflectivity.

    Models the transition zone as n_layers thin layers, each with a
    local impedance ratio. Computes the overall reflection using a
    transfer-matrix approach (characteristic impedance stacking).

    For a stack of thin layers, the total reflection coefficient is
    approximated by the WKB integral over the impedance gradient:

        |r_graded| ~ |r_sharp| * exp(-pi * delta / lambda)

    where:
        delta = transition width (m)
        lambda = probe wavelength (m) = 2*pi*c / omega_probe

    This exponential suppression is the standard result for reflection
    from a graded impedance profile (e.g., Brekhovskikh 1960).

    Additionally, we compute the coherent layer-by-layer result for
    more accuracy.

    Parameters
    ----------
    M_kg : float
        Mass (kg).
    r_s_m : float
        Schwarzschild radius (m).
    beta_Q : float
        Barrier exponent.
    omega_probe : float
        Probing frequency (rad/s).
    transition_width_rs : float
        Transition width in r_s units.
    n_layers : int
        Number of layers for numerical integration.
    Q : float
        Quality factor from WP2C (for absorption correction).

    Returns
    -------
    tuple
        (r_graded_amp, r_sharp_amp, grading_factor, lambda_over_width)
        where grading_factor = r_graded / r_sharp.
    """
    if M_kg <= 0 or r_s_m <= 0 or omega_probe <= 0:
        return (0.0, 0.0, 0.0, 0.0)

    R_eq_m = r_s_m / 3.0  # Constrained endpoint
    R_eq_over_rs = 1.0 / 3.0

    # Sharp-boundary reference
    omega_core = bdcc_oscillation_frequency(M_kg, R_eq_m, beta_Q)
    if omega_core <= 0:
        return (0.0, 0.0, 0.0, 0.0)
    eta_sharp = omega_core * R_eq_m / C_SI
    r_sharp = abs(1.0 - eta_sharp) / (1.0 + eta_sharp)

    # Probe wavelength
    lambda_probe = 2.0 * math.pi * C_SI / omega_probe
    transition_width_m = transition_width_rs * r_s_m
    lambda_over_width = lambda_probe / transition_width_m if transition_width_m > 0 else float("inf")

    # ── Method 1: WKB exponential suppression ──
    # For a monotonic impedance transition of width delta,
    # the reflection amplitude is suppressed by:
    #   r_graded ~ r_sharp * exp(-pi * delta / lambda)
    #
    # This is exact for a linear impedance gradient and a good
    # approximation for smooth profiles.
    #
    # HOWEVER: This formula applies when the wave NUMBER changes
    # smoothly. In our case, the transition is from vacuum (k = omega/c)
    # to BDCC interior (k = omega/c_s_bdcc). Since c_s_bdcc << c,
    # the wavenumber INCREASES dramatically inside the BDCC.
    #
    # The correct WKB integral is:
    #   r_graded ~ r_sharp * exp(-integral of |dk/dr| * dr / k)
    #            ~ r_sharp * exp(-pi * delta * Delta_k / k_avg)
    #
    # For eta << 1 (our regime), Delta_k/k_avg ~ |1 - 1/eta|.
    # But since eta << 1, the mismatch is huge, and the suppression
    # is actually LESS than the naive formula suggests.
    #
    # We use a careful transfer-matrix approach instead.

    # ── Method 2: Transfer-matrix (layer stacking) ──
    # Divide transition zone into n_layers. Each layer has thickness
    # dl = delta / n_layers and local impedance Z_j.
    # The reflection from layer j to j+1 is:
    #   r_j = (Z_{j+1} - Z_j) / (Z_{j+1} + Z_j)
    # The phase accumulated crossing layer j is:
    #   phi_j = omega_probe * dl / c_local_j
    #
    # For a graded transition, the total reflection is the coherent sum
    # of all partial reflections with appropriate phase factors.
    #
    # In the small-reflection limit (|r_j| << 1 for each layer),
    # this reduces to:
    #   r_total ~ sum_j r_j * exp(2i * sum_{k<j} phi_k)

    # Edge case: zero or very small transition width → sharp boundary
    if transition_width_rs < 1e-10:
        return (r_sharp, r_sharp, 1.0, float("inf"))

    # Build the impedance profile
    # Transition extends from R_eq/r_s = 1/3 outward to ~1/3 + 0.703
    r_inner = R_eq_over_rs      # 1/3
    r_outer = R_eq_over_rs + transition_width_rs  # ~1.036

    layer_etas = []

    for j in range(n_layers + 1):
        frac = j / n_layers
        # j=0 → innermost (R_eq, Phi=1, eta=eta_BDCC)
        # j=N → outermost (outer edge, Phi~0, eta=1)
        r_ov_rs = r_inner + frac * (r_outer - r_inner)
        Phi = barrier_dominance_profile(r_ov_rs, R_eq_over_rs, transition_width_rs)
        eta_loc = local_impedance_ratio(r_ov_rs, r_s_m, M_kg, beta_Q, Phi)
        layer_etas.append(eta_loc)

    dl = (r_outer - r_inner) * r_s_m / n_layers  # physical layer thickness (m)

    # ── Recursive Airy formula (exact for stratified media) ──
    #
    # Starting from the innermost layer and working outward, we use:
    #
    #   r_eff = (r_interface + r_prev * exp(2i*delta)) /
    #           (1 + r_interface * r_prev * exp(2i*delta))
    #
    # This is the exact Fresnel-Airy recursion for a layered medium,
    # properly handling all multiple reflections.
    #
    # At the innermost layer (j=0, BDCC core), there is no further
    # substrate reflection — the graded profile IS the reflector.
    # So r_prev_start = 0.
    #
    # We work outward: j = 0, 1, ..., N-1.
    # At each step, we compute the Fresnel coefficient between layer
    # j (eta_j) and layer j+1 (eta_{j+1}) for a wave traveling INWARD
    # (from j+1 toward j), then update the running r_eff.
    #
    # The wave enters from outside (layer N, eta_N ≈ 1) traveling
    # inward. The total reflection is r_eff after processing all layers.

    # Start at the innermost layer: no reflection from beyond R_eq
    r_eff_real = 0.0
    r_eff_imag = 0.0

    for j in range(n_layers):
        eta_j = layer_etas[j]        # Inner layer
        eta_jp1 = layer_etas[j + 1]  # Outer layer (one step outward)

        # Fresnel reflection at interface j+1 → j (inward-going wave)
        # When a wave in medium j+1 encounters medium j:
        # r = (eta_{j+1} - eta_j) / (eta_{j+1} + eta_j)
        denom = eta_jp1 + eta_j
        if denom > 0:
            r_interface = (eta_jp1 - eta_j) / denom
        else:
            r_interface = 0.0

        # Phase accumulated in layer j (single pass, one-way)
        c_eff = eta_j * C_SI
        if c_eff > 0:
            delta_j = omega_probe * dl / c_eff
        else:
            delta_j = 0.0

        # exp(2i * delta_j) — round-trip phase through layer j
        cos2d = math.cos(2.0 * delta_j)
        sin2d = math.sin(2.0 * delta_j)

        # r_prev * exp(2i*delta) — complex multiplication
        rp_cos = r_eff_real * cos2d - r_eff_imag * sin2d
        rp_sin = r_eff_real * sin2d + r_eff_imag * cos2d

        # Numerator: r_interface + r_prev*exp(2i*delta)
        num_r = r_interface + rp_cos
        num_i = rp_sin

        # Denominator: 1 + r_interface * r_prev*exp(2i*delta)
        den_r = 1.0 + r_interface * rp_cos
        den_i = r_interface * rp_sin

        # Complex division: (num_r + i*num_i) / (den_r + i*den_i)
        den_sq = den_r * den_r + den_i * den_i
        if den_sq > 1e-60:
            r_eff_real = (num_r * den_r + num_i * den_i) / den_sq
            r_eff_imag = (num_i * den_r - num_r * den_i) / den_sq
        else:
            r_eff_real = 0.0
            r_eff_imag = 0.0

    # Total graded reflection amplitude
    r_graded_raw = math.sqrt(r_eff_real ** 2 + r_eff_imag ** 2)

    # Apply Q-dependent absorption correction (same as WP2C)
    # The graded model inherits the Q-dependent absorption from the
    # interior response — if Q is low, energy is absorbed regardless
    # of the impedance profile.
    freq_ratio = omega_probe / omega_core if omega_core > 0 else 0.0
    x_eff = max(1.0, freq_ratio)
    absorption_factor = 1.0 / (Q * x_eff) if Q > 0 and math.isfinite(Q) else 0.0
    absorption_factor = min(1.0, absorption_factor)

    r_graded_amp = r_graded_raw * (1.0 - absorption_factor)
    r_graded_amp = max(0.0, min(1.0, r_graded_amp))

    grading_factor = r_graded_amp / r_sharp if r_sharp > 0 else 0.0

    return (r_graded_amp, r_sharp, grading_factor, lambda_over_width)


# ============================================================================
# WP2D — MULTI-MODE / CONTINUUM CORRECTION
# ============================================================================
#
# Upgrades the single-mode oscillator (WP2C) to a minimal multi-mode model.
#
# Physical motivation:
#   The BDCC is a spatially extended medium, not a point oscillator.
#   It supports multiple resonant modes, analogous to:
#     - drum modes: omega_n = omega_0 * sqrt(1 + n*(n+1)*xi)
#     - spherical cavity modes: roughly equally spaced in frequency
#
#   For reflection, what matters is how the TOTAL BDCC response
#   (summed over all modes) modifies the boundary condition at R_eq.
#
#   If multiple modes contribute, the effective Q at the probing
#   frequency could differ from the single-mode Q — either higher
#   (if the probe frequency is near a higher overtone) or lower
#   (if the density of states increases effective absorption).
#
# Model:
#   omega_n = omega_core * sqrt(1 + n*(n+1)*xi)  for n = 0, 1, 2, ...
#   Q_n = Q_0 / sqrt(1 + n*(n+1)*xi)  (Q decreases for higher overtones)
#   Weight_n = 1 / (1 + n)^2  (fundamental dominates)
#
#   Effective response:
#     chi_eff(omega) = sum_n weight_n * chi_n(omega)
#     where chi_n = 1 / sqrt((1 - x_n^2)^2 + (x_n/Q_n)^2)
#     and x_n = omega / omega_n
#
# NONCLAIMS:
#   - Mode spectrum is PARAMETERIZED, not derived from the metric
#   - Mode spacing xi is an ORDER OF MAGNITUDE estimate
#   - Does not account for continuum modes (only discrete)
#   - Weight distribution is assumed, not computed
# ============================================================================


def multimode_spectrum(
    omega_core: float,
    Q_fundamental: float,
    n_modes: int = 3,
    xi: float = 0.1,
) -> tuple:
    """Generate a multi-mode interior spectrum.

    Parameters
    ----------
    omega_core : float
        Fundamental mode frequency (rad/s).
    Q_fundamental : float
        Quality factor of the fundamental mode.
    n_modes : int
        Number of modes to include.
    xi : float
        Dimensionless mode spacing parameter.

    Returns
    -------
    tuple
        (frequencies, Q_values, weights) — lists of length n_modes.
    """
    if n_modes <= 0 or omega_core <= 0:
        return ([], [], [])

    frequencies = []
    Q_values = []
    weights = []

    for n in range(n_modes):
        # Mode frequency
        spacing_factor = math.sqrt(1.0 + n * (n + 1) * xi)
        omega_n = omega_core * spacing_factor

        # Mode Q — overtones have lower Q (more damped)
        # Physical reasoning: higher overtones have more spatial
        # nodes, leading to more efficient coupling to dissipation.
        Q_n = Q_fundamental / spacing_factor
        Q_n = max(Q_n, 0.01)  # Floor to avoid singularities

        # Mode weight — fundamental dominates
        # For a compact oscillator driven at the boundary,
        # the overlap integral with higher modes scales as 1/(n+1)^2
        weight_n = 1.0 / ((1.0 + n) ** 2)

        frequencies.append(omega_n)
        Q_values.append(Q_n)
        weights.append(weight_n)

    # Normalize weights
    total_w = sum(weights)
    if total_w > 0:
        weights = [w / total_w for w in weights]

    return (frequencies, Q_values, weights)


def multimode_reflection_correction(
    omega_probe: float,
    omega_core: float,
    R_eq_m: float,
    Q_fundamental: float,
    n_modes: int = 3,
    xi: float = 0.1,
) -> tuple:
    """Compute multi-mode corrected reflectivity.

    Compares single-mode (WP2C) vs multi-mode reflection to determine
    how the richer interior spectrum modifies the echo channel.

    Parameters
    ----------
    omega_probe : float
        Probing frequency (rad/s).
    omega_core : float
        Fundamental frequency (rad/s).
    R_eq_m : float
        Endpoint radius (m).
    Q_fundamental : float
        Fundamental mode quality factor.
    n_modes : int
        Number of modes.
    xi : float
        Mode spacing parameter.

    Returns
    -------
    tuple
        (r_multimode_amp, r_singlemode_amp, multimode_factor,
         frequencies, Q_values, weights)
    """
    if omega_core <= 0 or R_eq_m <= 0 or omega_probe <= 0:
        return (0.0, 0.0, 0.0, [], [], [])

    # Single-mode reference (WP2C)
    r_single = interior_reflection_estimate(
        omega_probe, omega_core, R_eq_m, Q_fundamental
    )

    if n_modes <= 1:
        return (r_single, r_single, 1.0, [omega_core], [Q_fundamental], [1.0])

    # Multi-mode spectrum
    freqs, Qs, weights = multimode_spectrum(
        omega_core, Q_fundamental, n_modes, xi
    )

    # Compute weighted reflection from each mode.
    # Each mode contributes to the BDCC response at the boundary.
    # The effective reflection is:
    #
    #   r_eff = r_impedance * (1 - absorption_eff)
    #
    # where absorption_eff is the weighted average absorption over all modes:
    #   absorption_eff = sum_n w_n * absorption_n
    #   absorption_n = min(1, 1/(Q_n * max(1, omega_probe/omega_n)))
    #
    # This captures: if SOME modes have low Q (high absorption),
    # they pull the effective reflectivity down proportionally.

    # Base impedance
    c_s_bdcc = omega_core * R_eq_m
    eta = c_s_bdcc / C_SI
    if eta <= 0:
        return (0.0, 0.0, 0.0, freqs, Qs, weights)
    r_impedance = abs(1.0 - eta) / (1.0 + eta)

    # Weighted absorption
    absorption_eff = 0.0
    for n in range(len(freqs)):
        omega_n = freqs[n]
        Q_n = Qs[n]
        w_n = weights[n]

        x_n = omega_probe / omega_n if omega_n > 0 else 0.0
        x_eff_n = max(1.0, x_n)

        if Q_n > 0 and math.isfinite(Q_n):
            abs_n = 1.0 / (Q_n * x_eff_n)
            abs_n = min(1.0, abs_n)
        else:
            abs_n = 0.0

        absorption_eff += w_n * abs_n

    r_multimode = r_impedance * (1.0 - absorption_eff)
    r_multimode = max(0.0, min(1.0, r_multimode))

    multimode_factor = r_multimode / r_single if r_single > 0 else 0.0

    return (r_multimode, r_single, multimode_factor, freqs, Qs, weights)


# ============================================================================
# WP2D — COMBINED ANALYSIS
# ============================================================================

def compute_graded_transition_analysis(
    params: GradedTransitionParams,
    n_echoes: int = 5,
) -> GradedTransitionResult:
    """Run the full WP2D graded-transition + multi-mode analysis.

    This is the main WP2D entry point. It computes:
    1. Sharp-boundary reflectivity (WP2B reference)
    2. WP2C single-mode interior reflectivity
    3. Graded-transition reflectivity (WP2D Task 1)
    4. Multi-mode corrected reflectivity (WP2D Task 2)
    5. Combined WP2D best estimate
    6. Echo amplitudes under all four models
    7. Channel status determination

    Parameters
    ----------
    params : GradedTransitionParams
        Input parameters.
    n_echoes : int
        Number of echo amplitudes to compute.

    Returns
    -------
    GradedTransitionResult
        Full WP2D analysis with comparisons.
    """
    r_s = params.r_s_m
    if r_s <= 0:
        r_s = schwarzschild_radius(params.M_kg)
    R_eq = params.R_eq_m
    if R_eq <= 0 and r_s > 0:
        R_eq = r_s / 3.0

    omega_core = bdcc_oscillation_frequency(params.M_kg, R_eq, params.beta_Q)

    # Probe frequency
    omega_probe = params.omega_probe_rad_s
    if omega_probe <= 0:
        omega_probe = schwarzschild_qnm_l2(params.M_kg)

    # ── 1. Sharp-boundary reference (WP2B) ──
    eta = omega_core * R_eq / C_SI if omega_core > 0 and R_eq > 0 else 0.0
    r_sharp = abs(1.0 - eta) / (1.0 + eta) if eta > 0 else 0.0

    # ── 2. WP2C single-mode interior ──
    Q = params.quality_factor_Q
    r_interior = interior_reflection_estimate(omega_probe, omega_core, R_eq, Q)

    # ── 3. Graded-transition (WP2D Task 1) ──
    r_graded, _, grading_factor, lambda_over_width = graded_reflection_coefficient(
        params.M_kg, r_s, params.beta_Q, omega_probe,
        transition_width_rs=params.transition_width_rs,
        n_layers=params.n_layers,
        Q=Q,
    )

    # ── 4. Multi-mode correction (WP2D Task 2) ──
    r_multi, r_single_ref, multimode_factor, mode_freqs, mode_Qs, mode_ws = \
        multimode_reflection_correction(
            omega_probe, omega_core, R_eq, Q,
            n_modes=params.n_modes,
            xi=params.mode_spacing_xi,
        )

    # ── 5. Combined WP2D best estimate ──
    # The graded correction and multi-mode correction act on different
    # aspects of the physics:
    #   - Grading: modifies the IMPEDANCE PROFILE (spatial)
    #   - Multi-mode: modifies the INTERIOR RESPONSE (spectral)
    #
    # They combine multiplicatively:
    #   r_wp2d = r_sharp * grading_factor * multimode_factor_on_sharp_base
    #
    # More precisely: start from the graded result (which includes
    # the Q-absorption), then apply the multi-mode correction
    # relative to the single-mode result.
    #
    # r_wp2d = r_graded * (r_multi / r_interior)  if r_interior > 0
    #        = r_graded * multimode_factor

    if r_interior > 0 and multimode_factor > 0:
        r_wp2d = r_graded * multimode_factor
    else:
        r_wp2d = r_graded

    r_wp2d = max(0.0, min(1.0, r_wp2d))
    combined_factor = r_wp2d / r_sharp if r_sharp > 0 else 0.0

    # ── Wavelength and transition width ──
    lambda_probe_m = 2.0 * math.pi * C_SI / omega_probe if omega_probe > 0 else 0.0
    transition_width_m = params.transition_width_rs * r_s

    # ── Echo amplitudes under all four models ──
    # Using standard formula: A_n/A_0 = |T|^2 * (r_surface * r_peak)^n
    # WKB estimates: |T|^2 ~ 0.04 (l=2), r_peak ~ 0.94 (l=2)
    T_sq = 0.04    # Approximate |T|^2 for l=2
    r_peak = 0.94  # Approximate peak reflection

    def _echo_amps(r_surf, n):
        return [T_sq * (r_surf * r_peak) ** k for k in range(1, n + 1)]

    amps_sharp = _echo_amps(r_sharp, n_echoes)
    amps_graded = _echo_amps(r_graded, n_echoes)
    amps_multi = _echo_amps(r_multi, n_echoes)
    amps_wp2d = _echo_amps(r_wp2d, n_echoes)

    # ── Classification ──
    # Transition regime
    if lambda_over_width > 5.0:
        transition_regime = "quasi_sharp"
    elif lambda_over_width > 1.0:
        transition_regime = "intermediate"
    else:
        transition_regime = "adiabatic"

    # Echo channel status
    # Based on the combined correction factor
    suppression_pct = (1.0 - combined_factor) * 100.0 if combined_factor < 1.0 else 0.0

    if combined_factor >= 1.0:
        echo_status = "strengthened"
    elif combined_factor >= 0.70:
        echo_status = "weakened_modestly"
    elif combined_factor >= 0.20:
        echo_status = "weakened_significantly"
    else:
        echo_status = "collapsed"

    # Inherit response class from WP2C
    # (graded transition doesn't change reactive/dissipative classification)
    if Q > 10.0:
        resp_cls = "reactive"
    elif Q > 1.0:
        resp_cls = "mixed_viscoelastic"
    elif Q > 0:
        resp_cls = "dissipative"
    else:
        resp_cls = "underdetermined"

    # ── Nonclaims ──
    nonclaims = [
        "Graded-transition model is ZEROTH-ORDER — uses parameterized Phi(R) profile, "
        "not a solution of the wave equation on the GRUT interior metric.",
        "Transfer-matrix computation assumes Born approximation validity "
        "(small local reflections per layer). May break near the BDCC endpoint.",
        "Phi(R/r_s) sigmoid profile is calibrated to Phase III-B benchmark at M=1e30 kg. "
        "Mass dependence of the transition profile is untested.",
        "Multi-mode spectrum uses parameterized mode spacing (xi), not computed "
        "from the interior metric perturbation theory.",
        "Mode weights are assumed (1/(n+1)^2 overlap integrals), not derived.",
        "Continuum modes are not modeled — only a finite discrete spectrum.",
        "Phase coherence across transition is assumed; decoherence/scattering "
        "within the transition zone is not modeled.",
        "All results remain CONDITIONAL on WP1 exterior assumption (Schwarzschild-like).",
        "Kerr generalization is not attempted.",
        f"Grading factor = {grading_factor:.4f} is an ESTIMATE — actual value "
        "requires the full interior wave equation.",
    ]

    closures = [
        "Full wave equation on GRUT interior metric with graded boundary",
        "Ab initio mode spectrum from metric perturbation theory",
        "Transition zone scattering/decoherence effects",
        "Mass-dependent Phi profile (currently calibrated to one mass only)",
        "Kerr generalization for rotating black holes",
        "Nonlinear mode coupling at large perturbation amplitudes",
    ]

    return GradedTransitionResult(
        r_sharp_amp=r_sharp,
        r_sharp_pow=r_sharp ** 2,
        r_interior_amp=r_interior,
        r_graded_amp=r_graded,
        r_graded_pow=r_graded ** 2,
        r_multimode_amp=r_multi,
        r_multimode_pow=r_multi ** 2,
        r_wp2d_amp=r_wp2d,
        r_wp2d_pow=r_wp2d ** 2,
        grading_factor=grading_factor,
        multimode_factor=multimode_factor,
        combined_factor=combined_factor,
        lambda_probe_m=lambda_probe_m,
        transition_width_m=transition_width_m,
        lambda_over_width=lambda_over_width,
        mode_frequencies_rad_s=mode_freqs,
        mode_quality_factors=mode_Qs,
        mode_weights=mode_ws,
        echo_amplitudes_sharp=amps_sharp,
        echo_amplitudes_graded=amps_graded,
        echo_amplitudes_multimode=amps_multi,
        echo_amplitudes_wp2d=amps_wp2d,
        transition_regime=transition_regime,
        echo_channel_status=echo_status,
        response_class=resp_cls,
        nonclaims=nonclaims,
        required_closures=closures,
    )


def graded_transition_result_to_dict(
    result: GradedTransitionResult,
) -> Dict[str, Any]:
    """Serialize a GradedTransitionResult to a dict."""
    return {
        "reflectivity_comparison": {
            "sharp_boundary_WP2B": {
                "r_amp": result.r_sharp_amp,
                "r_pow": result.r_sharp_pow,
            },
            "interior_singlemode_WP2C": {
                "r_amp": result.r_interior_amp,
            },
            "graded_transition_WP2D": {
                "r_amp": result.r_graded_amp,
                "r_pow": result.r_graded_pow,
                "grading_factor": result.grading_factor,
            },
            "multimode_WP2D": {
                "r_amp": result.r_multimode_amp,
                "r_pow": result.r_multimode_pow,
                "multimode_factor": result.multimode_factor,
            },
            "combined_WP2D_best": {
                "r_amp": result.r_wp2d_amp,
                "r_pow": result.r_wp2d_pow,
                "combined_factor": result.combined_factor,
            },
        },
        "transition_diagnostics": {
            "lambda_probe_m": result.lambda_probe_m,
            "transition_width_m": result.transition_width_m,
            "lambda_over_width": result.lambda_over_width,
            "transition_regime": result.transition_regime,
        },
        "multimode_spectrum": {
            "mode_frequencies_rad_s": result.mode_frequencies_rad_s,
            "mode_quality_factors": result.mode_quality_factors,
            "mode_weights": result.mode_weights,
        },
        "echo_amplitudes": {
            "sharp": result.echo_amplitudes_sharp,
            "graded": result.echo_amplitudes_graded,
            "multimode": result.echo_amplitudes_multimode,
            "wp2d_combined": result.echo_amplitudes_wp2d,
        },
        "classification": {
            "echo_channel_status": result.echo_channel_status,
            "transition_regime": result.transition_regime,
            "response_class": result.response_class,
        },
        "nonclaims": result.nonclaims,
        "required_closures": result.required_closures,
    }


# ============================================================================
# SCANNING UTILITIES
# ============================================================================

def scan_dissipation_range(
    M_kg: float,
    R_eq_over_r_s: float = 1.0 / 3.0,
    beta_Q: float = 2.0,
    gamma_diss_values: Optional[List[float]] = None,
) -> List[Dict[str, Any]]:
    """Scan over dissipation rates to map Q vs gamma_diss.

    Parameters
    ----------
    M_kg : float
        Black hole mass (kg).
    R_eq_over_r_s : float
        Dimensionless endpoint radius (default 1/3).
    beta_Q : float
        Barrier exponent (default 2).
    gamma_diss_values : list of float, optional
        Dissipation rates to scan. Default covers 12 orders of magnitude.

    Returns
    -------
    list of dict
        One dict per gamma_diss value with Q and classification.
    """
    if gamma_diss_values is None:
        gamma_diss_values = [
            0.0, 1e-20, 1e-18, 1e-15, 1e-12,
            1e-9, 1e-6, 1e-3, 1.0,
        ]

    r_s = schwarzschild_radius(M_kg)
    R_eq = R_eq_over_r_s * r_s

    results = []
    for gamma in gamma_diss_values:
        params = InteriorWaveParams(
            M_kg=M_kg, R_eq_m=R_eq, r_s_m=r_s,
            beta_Q=beta_Q, gamma_diss=gamma,
        )
        res = compute_interior_wave_analysis(params)
        results.append({
            "gamma_diss": gamma,
            "Q": res.quality_factor_Q,
            "gamma_eff": res.gamma_eff_rad_s,
            "gamma_memory": res.memory_damping_rate,
            "response_class": res.response_class,
            "r_interior_amp": res.r_interior_amp,
        })

    return results


def scan_mass_interior(
    mass_range_kg: Optional[List[float]] = None,
    R_eq_over_r_s: float = 1.0 / 3.0,
    gamma_diss: float = 1e-15,
) -> List[Dict[str, Any]]:
    """Scan over mass range for interior wave analysis.

    Parameters
    ----------
    mass_range_kg : list of float, optional
        Masses to scan. Default: 10, 30, 100 M_sun + SMBHs.
    R_eq_over_r_s : float
        Dimensionless endpoint radius (default 1/3).
    gamma_diss : float
        Dissipation rate (default 1e-15).

    Returns
    -------
    list of dict
        One dict per mass with Q, classification, and reflection.
    """
    if mass_range_kg is None:
        mass_range_kg = [
            10.0 * M_SUN,
            30.0 * M_SUN,
            100.0 * M_SUN,
            1e4 * M_SUN,
            1e6 * M_SUN,
            1e9 * M_SUN,
        ]

    results = []
    for M in mass_range_kg:
        r_s = schwarzschild_radius(M)
        R_eq = R_eq_over_r_s * r_s

        params = InteriorWaveParams(
            M_kg=M, R_eq_m=R_eq, r_s_m=r_s,
            gamma_diss=gamma_diss,
        )
        res = compute_interior_wave_analysis(params)
        results.append({
            "M_solar": M / M_SUN,
            "omega_core": res.omega_core_rad_s,
            "Q": res.quality_factor_Q,
            "gamma_eff": res.gamma_eff_rad_s,
            "gamma_memory": res.memory_damping_rate,
            "gamma_solver": res.solver_damping_rate,
            "response_class": res.response_class,
            "r_interior_amp": res.r_interior_amp,
            "freq_ratio": res.omega_probe_over_omega_core,
            "damping_over_crossing": res.damping_over_crossing,
        })

    return results
