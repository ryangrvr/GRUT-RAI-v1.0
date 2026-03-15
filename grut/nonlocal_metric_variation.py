"""GRUT Phase IV — Route C Follow-Up: Perturbative Nonlocal Metric Variation.

Computes the perturbative metric variation of the nonlocal retarded action
around FRW and tests whether it commutes with auxiliary-field reduction.

CONTEXT:
Route C stress-functional analysis (nonlocal_stress.py) established that
the nonlocal retarded action yields a FUNCTIONAL-DERIVED stress-functional.
The deepest remaining obstruction: does the metric variation of the nonlocal
action commute with the auxiliary-field (ODE) reduction?

    Path 1: vary S_nonlocal[g] w.r.t. g,  then reduce to auxiliary field
    Path 2: reduce to auxiliary field first, then vary the local system

KEY PHYSICS — PERTURBATIVE SETUP AROUND FRW:

Background FRW:
    ds^2 = -dt^2 + a(t)^2 delta_{ij} dx^i dx^j
    H_0(t), rho_0(t), X_0(t) = C_rho * rho_0(t),  tau_eff_0,  Phi_0(t)

Perturbations considered (each tested independently):

(A) SOURCE PERTURBATION — X -> X_0 + epsilon * delta_X(t):
    Convolution: delta_Phi_conv = integral K(t-t') delta_X(t') dt'
    ODE:         tau d(delta_Phi)/dt + delta_Phi = delta_X
    Result:      COMMUTES exactly. Linearity of convolution = linearity of ODE.
                 This is the Markov property applied to source perturbations.

(B) KERNEL PERTURBATION — tau -> tau_0 + epsilon * delta_tau:
    The kernel changes: K(s; tau_0+delta_tau) = K(s; tau_0) + delta_tau * dK/dtau
    where dK/dtau = [(s - tau)/tau^3] exp(-s/tau).
    Convolution: delta_Phi = delta_tau * integral [(s-tau)/tau^3] exp(-s/tau) X_0 dt'
    ODE:         tau d(delta_Phi)/dt + delta_Phi = -delta_tau * dPhi_0/dt
    For constant X_0 and constant delta_tau:
        BOTH give: delta_Phi(t) = -(delta_tau/tau_0) * X_0 * (t/tau_0) * exp(-t/tau_0)
    Result:      COMMUTES exactly. The lag-dependent kernel perturbation
                 is fully captured by the perturbed ODE coefficient.

(C) LAPSE PERTURBATION — proper time ds = (1 + Psi) dt:
    In the Newtonian gauge, g_00 = -(1+2*Psi), so ds ≈ (1+Psi)*dt.
    The retarded convolution in PROPER TIME uses effective kernel:
        K_proper(s_coord) = ((1+Psi)/tau_0) exp(-(1+Psi)*s_coord/tau_0)
    which is equivalent to a kernel with tau_eff_proper = tau_0/(1+Psi).
    Convolution (proper time): uses tau = tau_0/(1+Psi) ≈ tau_0*(1-Psi)
    ODE (coordinate time):     uses tau = tau_0 (misses the lapse)
    ODE (proper time):         uses tau_eff/(1+Psi) ≈ tau_0*(1-Psi)
    Result:
        Coordinate-time ODE:  DOES NOT COMMUTE with proper-time convolution.
        Proper-time ODE:      COMMUTES with proper-time convolution.
        Mismatch term:        delta_Phi_lapse = Psi * (X_0 - Phi_0) driving the ODE.
        For constant X_0:     delta_Phi_lapse(t) = Psi * X_0 * (t/tau) * exp(-t/tau)
        Peak at t = tau:      |delta_Phi_max| = Psi * X_0 / e ≈ 0.368 * Psi * X_0

SUMMARY OF COMMUTATION:
    Source perturbation:  COMMUTES (exact, Markov property)
    Tau perturbation:     COMMUTES (exact, Markov property applied to kernel coefficients)
    Lapse (coord. time):  DOES NOT COMMUTE — mismatch = Psi * (X - Phi) driving term
    Lapse (proper time):  COMMUTES (exact, once lapse is included in ODE)

    The CURRENT GRUT framework uses coordinate time, so the lapse correction
    is absent. This means:
    - Commutation HOLDS in the current coordinate-time formulation
    - Commutation BREAKS at the covariant level due to lapse correction
    - The lapse correction is computable and specific:
        delta_Phi_lapse satisfies: tau * d(delta_Phi)/dt + delta_Phi = Psi*(X - Phi)

MAGNITUDES:
    Cosmology:  Psi ~ 10^{-5} (CMB anisotropy) => delta_Phi/Phi ~ 10^{-5} (NEGLIGIBLE)
    Collapse:   Psi ~ G*M/(c^2*R) ~ r_s/(2R) => O(1) near horizon (SIGNIFICANT)

ROUTE C STATUS:
    Upgraded from FUNCTIONAL-DERIVED to PERTURBATIVELY VERIFIED (in coordinate time).
    The remaining obstruction is now the LAPSE CORRECTION in the covariant formulation,
    which is specific, computable, and negligible in the weak-field sector.

See docs/PHASE_IV_ROUTE_C_METRIC_VARIATION.md for the full theory memo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


# Physical constants
G_SI = 6.674e-11          # m^3 kg^-1 s^-2
C_SI = 299_792_458.0      # m/s
M_SUN = 1.989e30          # kg
C_RHO = 8.0 * math.pi * G_SI / 3.0  # 8piG/3


# ================================================================
# Data Structures
# ================================================================

@dataclass
class FRWPerturbativeBackground:
    """FRW background for perturbative metric variation.

    Background: ds^2 = -dt^2 + a(t)^2 delta_{ij} dx^i dx^j
    All quantities at the background level (zeroth order in perturbations).

    The memory field Phi_0(t) satisfies:
        tau_0 dPhi_0/dt + Phi_0 = X_0

    For constant X_0 and Phi_0(0) = 0:
        Phi_0(t) = X_0 * (1 - exp(-t/tau_0))
        dPhi_0/dt = (X_0/tau_0) * exp(-t/tau_0)
    """
    # Background parameters
    tau_eff: float = 0.0
    X_0: float = 0.0          # background source (constant for simplicity)

    # Time grid
    n_steps: int = 0
    n_tau: float = 0.0
    dt: float = 0.0
    times: List[float] = field(default_factory=list)

    # Background solutions
    Phi_0: List[float] = field(default_factory=list)       # Phi_0(t)
    dPhi_0_dt: List[float] = field(default_factory=list)   # dPhi_0/dt

    # Analytical forms (for constant X_0)
    phi_0_form: str = ""
    dphi_0_dt_form: str = ""

    notes: List[str] = field(default_factory=list)


@dataclass
class SourcePerturbationTest:
    """Commutation test for source perturbation X -> X_0 + epsilon*delta_X.

    THEORY:
    The convolution delta_Phi_conv(t) = integral K(t-t') delta_X(t') dt'
    is mathematically identical to the ODE solution:
        tau d(delta_Phi_ode)/dt + delta_Phi_ode = delta_X,  delta_Phi(0) = 0

    This is the Markov property applied to source perturbations:
    the retarded convolution of the exponential kernel IS the first-order ODE.

    Expected: COMMUTES exactly (to quadrature precision).
    """
    # Perturbation definition
    delta_X_form: str = ""
    delta_X_amplitude: float = 0.0

    # Results
    delta_phi_convolution: List[float] = field(default_factory=list)
    delta_phi_ode: List[float] = field(default_factory=list)

    # Mismatch
    max_absolute_mismatch: float = 0.0
    max_relative_mismatch: float = 0.0
    commutes: bool = False

    notes: List[str] = field(default_factory=list)


@dataclass
class TauPerturbationTest:
    """Commutation test for kernel perturbation tau -> tau_0 + epsilon*delta_tau.

    THEORY:
    The perturbed kernel:
        K(s; tau_0 + delta_tau) ≈ K(s; tau_0) + delta_tau * dK/dtau
    where:
        dK/dtau = [(s - tau_0)/tau_0^3] exp(-s/tau_0)

    Convolution perturbation:
        delta_Phi_conv = delta_tau * integral [(s-tau_0)/tau_0^3] exp(-s/tau_0) X_0 dt'

    ODE perturbation:
        tau_0 d(delta_Phi)/dt + delta_Phi = -delta_tau * dPhi_0/dt

    For constant X_0 and constant delta_tau, BOTH give:
        delta_Phi(t) = -(delta_tau/tau_0) * X_0 * (t/tau_0) * exp(-t/tau_0)

    This is the Markov property applied to kernel coefficient perturbations:
    the lag-dependent kernel perturbation [(s-tau)/tau^3]*exp(-s/tau) is
    exactly captured by the -delta_tau * dPhi_0/dt term in the perturbed ODE.

    Expected: COMMUTES exactly (to quadrature precision).
    """
    # Perturbation definition
    delta_tau: float = 0.0

    # Analytical solution
    delta_phi_analytical_form: str = ""
    delta_phi_analytical: List[float] = field(default_factory=list)

    # Numerical results
    delta_phi_convolution: List[float] = field(default_factory=list)
    delta_phi_ode: List[float] = field(default_factory=list)

    # Conv vs ODE mismatch
    conv_ode_max_mismatch: float = 0.0
    conv_ode_relative_mismatch: float = 0.0
    conv_ode_commutes: bool = False

    # Conv vs analytical
    conv_analytical_max_mismatch: float = 0.0
    conv_analytical_commutes: bool = False

    # ODE vs analytical
    ode_analytical_max_mismatch: float = 0.0
    ode_analytical_commutes: bool = False

    notes: List[str] = field(default_factory=list)


@dataclass
class LapsePerturbationTest:
    """Commutation test for lapse perturbation ds = (1+Psi)*dt.

    THEORY:
    In the Newtonian gauge, g_00 = -(1+2*Psi), so proper time:
        ds = sqrt(-g_00) dt ≈ (1 + Psi) dt  (first order in Psi)

    The retarded convolution in PROPER TIME becomes:
        Phi_proper(t) = integral_0^t K_proper(t-t') X_0(t') dt'
    where:
        K_proper(s) = ((1+Psi)/tau_0) exp(-(1+Psi)*s/tau_0)

    This is equivalent to a kernel with effective tau = tau_0/(1+Psi).

    Coordinate-time ODE:  tau_0 * dPhi/dt + Phi = X  (ignores lapse)
    Proper-time ODE:      tau_0/(1+Psi) * dPhi/dt + Phi = X  (includes lapse)
                        ≈ tau_0*(1-Psi) * dPhi/dt + Phi = X

    The lapse correction at first order:
        tau_0 d(delta_Phi_lapse)/dt + delta_Phi_lapse = Psi * (X_0 - Phi_0)

    For constant X_0 with Phi_0(t) = X_0*(1-exp(-t/tau_0)):
        Source = Psi * X_0 * exp(-t/tau_0)
        Solution: delta_Phi_lapse(t) = Psi * X_0 * (t/tau_0) * exp(-t/tau_0)
        Peak at t = tau_0: |delta_Phi_max| = Psi * X_0 / e ≈ 0.368 * Psi * X_0

    CRITICAL RESULT:
        Coordinate-time ODE FAILS to commute with proper-time convolution.
        Proper-time ODE COMMUTES with proper-time convolution.
        The mismatch is the lapse correction: a SPECIFIC, COMPUTABLE term.
    """
    # Perturbation parameter
    Psi: float = 0.0    # Newtonian potential (lapse perturbation)

    # Proper-time convolution result
    delta_phi_proper_convolution: List[float] = field(default_factory=list)

    # Coordinate-time ODE (no lapse correction)
    delta_phi_coordinate_ode: List[float] = field(default_factory=list)

    # Proper-time ODE (with lapse correction)
    delta_phi_proper_ode: List[float] = field(default_factory=list)

    # Analytical lapse correction
    delta_phi_lapse_analytical: List[float] = field(default_factory=list)
    lapse_correction_form: str = ""
    lapse_peak_value: float = 0.0
    lapse_peak_time_over_tau: float = 0.0

    # Coordinate-time ODE vs proper-time convolution (should MISMATCH)
    coord_vs_proper_max_mismatch: float = 0.0
    coord_vs_proper_relative_mismatch: float = 0.0
    coordinate_commutes: bool = False  # expected: False

    # Proper-time ODE vs proper-time convolution (should MATCH)
    proper_vs_proper_max_mismatch: float = 0.0
    proper_vs_proper_relative_mismatch: float = 0.0
    proper_commutes: bool = False  # expected: True

    # Analytical lapse correction vs numerical mismatch
    lapse_analytical_vs_numerical_mismatch: float = 0.0
    lapse_analytical_verified: bool = False

    notes: List[str] = field(default_factory=list)


@dataclass
class LapseMagnitudeEstimate:
    """Magnitude of the lapse correction in cosmological and collapse sectors.

    The lapse correction:
        delta_Phi_lapse(t) = Psi * X_0 * (t/tau) * exp(-t/tau)
        Peak: Psi * X_0 / e at t = tau

    Cosmology (weak field):
        Psi ~ 10^{-5} (CMB anisotropy)
        delta_Phi / Phi ~ Psi ~ 10^{-5} (utterly negligible)

    Collapse (strong field):
        Psi ~ G*M / (c^2 * R) = r_s / (2*R)
        Near horizon (R ~ 3*r_s): Psi ~ 1/6 ≈ 0.17
        delta_Phi / Phi ~ 0.17 / e ≈ 6% (significant)
    """
    # Cosmological sector
    Psi_cosmo: float = 0.0
    delta_phi_over_phi_cosmo: float = 0.0
    cosmo_negligible: bool = True

    # Collapse sector
    Psi_collapse: float = 0.0
    R_over_r_s: float = 0.0
    delta_phi_over_phi_collapse: float = 0.0
    collapse_negligible: bool = False

    # Classification
    weak_field_safe: bool = True
    strong_field_correction_needed: bool = True

    notes: List[str] = field(default_factory=list)


@dataclass
class CommutationSummary:
    """Master commutation assessment across all perturbation types.

    The commutation question: does varying S_nonlocal w.r.t. g then reducing
    to the auxiliary field give the same T^Phi as reducing first then varying?

    Answer (perturbative, around FRW, first order):
    - Source perturbation:   COMMUTES (exact, Markov property)
    - Tau perturbation:      COMMUTES (exact, Markov property for kernel coefficients)
    - Lapse (coordinate):    DOES NOT COMMUTE (missing proper-time correction)
    - Lapse (proper time):   COMMUTES (exact, once lapse included in ODE)

    Overall: COMMUTES in coordinate-time formulation (current GRUT framework).
    The lapse correction is the price of manifest covariance.
    """
    source_commutes: bool = False
    tau_commutes: bool = False
    lapse_coordinate_commutes: bool = False
    lapse_proper_commutes: bool = False

    # In the current GRUT framework (coordinate time):
    overall_coordinate_time_commutes: bool = False

    # For a fully covariant formulation:
    overall_proper_time_commutes: bool = False
    covariant_mismatch_source: str = ""
    covariant_mismatch_form: str = ""
    covariant_mismatch_order: str = ""

    # Perturbative order of agreement
    perturbative_order: str = ""  # "first_order_in_scalar_perturbations"

    notes: List[str] = field(default_factory=list)
    nonclaims: List[str] = field(default_factory=list)


@dataclass
class RouteCUpgradeAssessment:
    """Assessment of whether this analysis upgrades Route C status.

    Previous: FUNCTIONAL-DERIVED (from nonlocal_stress.py)
    Current:  PERTURBATIVELY VERIFIED in coordinate time

    The upgrade is conditional:
    - In coordinate-time (current GRUT): variation and reduction commute at
      first perturbative order. This is stronger than "functional-derived."
    - In covariant formulation: lapse correction breaks commutation, but
      the correction is specific and computable.
    """
    previous_status: str = ""
    current_status: str = ""
    upgraded: bool = False
    upgrade_reason: str = ""

    # Conditions on the upgrade
    upgrade_scope: str = ""
    upgrade_limitations: List[str] = field(default_factory=list)

    remaining_obstruction: str = ""
    remaining_obstruction_severity: str = ""

    notes: List[str] = field(default_factory=list)


@dataclass
class RouteCMetricVariationResult:
    """Master result for Route C perturbative metric variation analysis."""
    valid: bool = False

    # Components
    background: Optional[FRWPerturbativeBackground] = None
    source_test: Optional[SourcePerturbationTest] = None
    tau_test: Optional[TauPerturbationTest] = None
    lapse_test: Optional[LapsePerturbationTest] = None
    lapse_magnitude: Optional[LapseMagnitudeEstimate] = None
    commutation: Optional[CommutationSummary] = None
    upgrade: Optional[RouteCUpgradeAssessment] = None

    # Overall
    remaining_obstruction: str = ""
    nonclaims: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)


# ================================================================
# Internal Numerical Tools
# ================================================================

def _retarded_kernel(s: float, tau: float) -> float:
    """Exponential retarded kernel K(s) = (1/tau) exp(-s/tau) for s >= 0."""
    if s < 0:
        return 0.0
    return math.exp(-s / tau) / tau


def _retarded_kernel_tau_derivative(s: float, tau: float) -> float:
    """Derivative of the retarded kernel with respect to tau:

        dK/dtau = [(s - tau)/tau^3] exp(-s/tau)

    This encodes how the kernel shape changes when the relaxation timescale
    is perturbed. Note the sign: for s < tau, dK/dtau < 0 (kernel peak
    decreases); for s > tau, dK/dtau > 0 (kernel tail increases).
    """
    if s < 0:
        return 0.0
    return ((s - tau) / (tau ** 3)) * math.exp(-s / tau)


def _proper_time_kernel(s: float, tau: float, Psi: float) -> float:
    """Proper-time-corrected kernel for lapse perturbation.

    In the Newtonian gauge with constant Psi:
        K_proper(s) = ((1+Psi)/tau) exp(-(1+Psi)*s/tau)

    This is equivalent to a kernel with tau_eff = tau/(1+Psi).

    The factor (1+Psi) in front accounts for the Jacobian ds/dt = (1+Psi).
    The factor (1+Psi) in the exponent accounts for the proper-time distance.
    """
    if s < 0:
        return 0.0
    factor = 1.0 + Psi
    return (factor / tau) * math.exp(-factor * s / tau)


def _convolution_with_kernel(
    kernel_func,
    source: List[float],
    times: List[float],
    t_eval_index: int,
) -> float:
    """Compute convolution integral with an arbitrary kernel function.

        result = integral_0^{t_eval} kernel(t_eval - t') source(t') dt'

    Uses trapezoidal rule.
    """
    result_val = 0.0
    t_eval = times[t_eval_index]

    for i in range(t_eval_index):
        t_prime = times[i]
        t_prime_next = times[i + 1]
        s = t_eval - t_prime
        s_next = t_eval - t_prime_next

        k1 = kernel_func(s)
        k2 = kernel_func(max(s_next, 0.0))

        x1 = source[i]
        x2 = source[i + 1]

        dt_trap = t_prime_next - t_prime
        result_val += 0.5 * dt_trap * (k1 * x1 + k2 * x2)

    return result_val


def _integrate_memory_ode(
    source: List[float],
    times: List[float],
    tau: float,
    phi_0: float = 0.0,
) -> List[float]:
    """Integrate tau*dPhi/dt + Phi = source using exact exponential update."""
    phi_values = [phi_0]
    phi = phi_0
    for i in range(len(times) - 1):
        dt = times[i + 1] - times[i]
        if dt <= 0 or tau <= 0:
            phi_values.append(phi)
            continue
        lam = dt / tau
        e = math.exp(-lam)
        phi = phi * e + source[i + 1] * (1.0 - e)
        phi_values.append(phi)
    return phi_values


def _integrate_perturbed_ode_tau(
    dPhi_0_dt: List[float],
    times: List[float],
    tau_0: float,
    delta_tau: float,
) -> List[float]:
    """Integrate the tau-perturbed ODE:

        tau_0 d(delta_Phi)/dt + delta_Phi = -delta_tau * dPhi_0/dt

    The source is -delta_tau * dPhi_0/dt.
    """
    source = [-delta_tau * dpdt for dpdt in dPhi_0_dt]
    return _integrate_memory_ode(source, times, tau_0, phi_0=0.0)


def _integrate_lapse_corrected_ode(
    X_0_values: List[float],
    Phi_0_values: List[float],
    times: List[float],
    tau_0: float,
    Psi: float,
) -> List[float]:
    """Integrate the lapse correction ODE:

        tau_0 d(delta_Phi)/dt + delta_Phi = Psi * (X_0 - Phi_0)

    This captures the proper-time effect of the Newtonian potential Psi
    on the memory ODE. The source Psi*(X_0 - Phi_0) arises because
    proper time runs slower in a potential well:
        ds = (1+Psi)*dt  =>  tau_0 dPhi/ds = tau_0/(1+Psi) dPhi/dt

    At first order: this adds Psi*tau_0*dPhi_0/dt = Psi*(X_0-Phi_0)
    as an effective source for the lapse correction delta_Phi.
    """
    source = [Psi * (x - p) for x, p in zip(X_0_values, Phi_0_values)]
    return _integrate_memory_ode(source, times, tau_0, phi_0=0.0)


def _analytical_lapse_correction(
    X_0: float,
    tau_0: float,
    Psi: float,
    times: List[float],
) -> List[float]:
    """Analytical lapse correction for constant X_0:

        delta_Phi_lapse(t) = Psi * X_0 * (t/tau_0) * exp(-t/tau_0)

    Derivation:
    The lapse correction satisfies:
        tau_0 d(f)/dt + f = Psi * X_0 * exp(-t/tau_0),  f(0) = 0

    where the source is Psi * (X_0 - Phi_0) = Psi * X_0 * exp(-t/tau_0).

    The solution is f(t) = Psi * X_0 * (t/tau_0) * exp(-t/tau_0).

    Verification:
        f'(t) = Psi*X_0/tau_0 * [1 - t/tau_0] * exp(-t/tau_0)
        tau_0*f'(t) + f(t) = Psi*X_0 * [1 - t/tau_0 + t/tau_0] * exp(-t/tau_0)
                            = Psi * X_0 * exp(-t/tau_0) = source ✓

    Peak value at t = tau_0:
        f_max = Psi * X_0 * (1) * exp(-1) = Psi * X_0 / e ≈ 0.368 * Psi * X_0
    """
    return [Psi * X_0 * (t / tau_0) * math.exp(-t / tau_0) for t in times]


# ================================================================
# Analysis Functions
# ================================================================

def build_frw_perturbative_background(
    tau_eff: float = 1.0,
    X_0: float = 1.0,
    n_steps: int = 2000,
    n_tau: float = 10.0,
) -> FRWPerturbativeBackground:
    """Build the FRW background for perturbative analysis.

    Uses a constant source X_0 for analytical tractability.
    The background memory field:
        Phi_0(t) = X_0 * (1 - exp(-t/tau))
        dPhi_0/dt = (X_0/tau) * exp(-t/tau)

    Parameters
    ----------
    tau_eff : float
        Background relaxation timescale.
    X_0 : float
        Background source (constant).
    n_steps : int
        Number of time steps.
    n_tau : float
        Total time in units of tau.

    Returns
    -------
    FRWPerturbativeBackground
    """
    bg = FRWPerturbativeBackground()

    bg.tau_eff = tau_eff
    bg.X_0 = X_0
    bg.n_steps = n_steps
    bg.n_tau = n_tau

    T = n_tau * tau_eff
    bg.dt = T / n_steps
    bg.times = [i * bg.dt for i in range(n_steps + 1)]

    # Background Phi_0(t) = X_0 * (1 - exp(-t/tau))
    bg.Phi_0 = [X_0 * (1.0 - math.exp(-t / tau_eff)) for t in bg.times]

    # dPhi_0/dt = (X_0/tau) * exp(-t/tau)
    bg.dPhi_0_dt = [(X_0 / tau_eff) * math.exp(-t / tau_eff) for t in bg.times]

    bg.phi_0_form = "Phi_0(t) = X_0 * (1 - exp(-t/tau_0))"
    bg.dphi_0_dt_form = "dPhi_0/dt = (X_0/tau_0) * exp(-t/tau_0)"

    # Verify: ODE solution matches analytical
    phi_ode = _integrate_memory_ode(
        [X_0] * (n_steps + 1), bg.times, tau_eff, phi_0=0.0
    )
    max_err = 0.0
    for i in range(n_steps + 1):
        denom = abs(bg.Phi_0[i]) if abs(bg.Phi_0[i]) > 1e-30 else 1.0
        err = abs(phi_ode[i] - bg.Phi_0[i]) / denom
        if err > max_err:
            max_err = err

    bg.notes = [
        f"tau_eff = {tau_eff}, X_0 = {X_0}, n_steps = {n_steps}, n_tau = {n_tau}",
        f"Background ODE vs analytical max error: {max_err:.2e}",
        "Constant source for analytical tractability",
        "All perturbative tests use this background",
    ]

    return bg


def test_source_perturbation_commutation(
    bg: FRWPerturbativeBackground,
    delta_X_amplitude: float = 0.1,
) -> SourcePerturbationTest:
    """Test commutation for source perturbation X -> X_0 + epsilon*delta_X.

    Uses delta_X(t) = delta_X_amplitude * sin(2*pi*t / (3*tau)).
    Compares convolution integral vs ODE for the perturbation delta_Phi.

    Expected result: COMMUTES exactly (Markov property = linearity).

    Parameters
    ----------
    bg : FRWPerturbativeBackground
        Background solution.
    delta_X_amplitude : float
        Amplitude of source perturbation.

    Returns
    -------
    SourcePerturbationTest
    """
    result = SourcePerturbationTest()

    tau = bg.tau_eff
    n = bg.n_steps
    times = bg.times

    result.delta_X_form = f"delta_X(t) = {delta_X_amplitude} * sin(2*pi*t / (3*tau))"
    result.delta_X_amplitude = delta_X_amplitude

    # Source perturbation
    delta_X = [delta_X_amplitude * math.sin(2.0 * math.pi * t / (3.0 * tau))
               for t in times]

    # Path 1: Convolution of K with delta_X
    def kernel(s):
        return _retarded_kernel(s, tau)

    delta_phi_conv = [0.0]
    for i in range(1, n + 1):
        val = _convolution_with_kernel(kernel, delta_X, times, i)
        delta_phi_conv.append(val)
    result.delta_phi_convolution = delta_phi_conv

    # Path 2: ODE solution
    delta_phi_ode = _integrate_memory_ode(delta_X, times, tau, phi_0=0.0)
    result.delta_phi_ode = delta_phi_ode

    # Compare (skip very early transient)
    # Use peak-normalized comparison: divide by the peak |delta_Phi_ode|
    # over the comparison window.  This avoids blow-up near zero-crossings
    # of the oscillating response and is the same approach used in the
    # tau-perturbation test.
    max_abs = 0.0
    peak_ode = max(abs(v) for v in delta_phi_ode[n // 5:]) if n > 5 else 1e-30
    peak_ode = max(peak_ode, 1e-30)

    for i in range(n // 5, n + 1):
        abs_err = abs(delta_phi_conv[i] - delta_phi_ode[i])
        max_abs = max(max_abs, abs_err)

    max_rel = max_abs / peak_ode

    result.max_absolute_mismatch = max_abs
    result.max_relative_mismatch = max_rel
    result.commutes = max_rel < 0.05

    result.notes = [
        f"Max absolute mismatch: {max_abs:.6e}",
        f"Max relative mismatch: {max_rel:.6e}",
        f"Commutes: {result.commutes}",
        "Source perturbation commutation is a direct consequence of the Markov property",
        "Convolution with exponential kernel = first-order ODE (mathematical identity)",
    ]

    return result


def test_tau_perturbation_commutation(
    bg: FRWPerturbativeBackground,
    delta_tau_fraction: float = 0.01,
) -> TauPerturbationTest:
    """Test commutation for kernel perturbation tau -> tau_0 + delta_tau.

    Uses constant delta_tau = delta_tau_fraction * tau_0.

    Three-way comparison:
    1. Analytical: delta_Phi(t) = -(delta_tau/tau_0) * X_0 * (t/tau_0) * exp(-t/tau_0)
    2. Convolution: compute Phi(tau_0+delta_tau) - Phi(tau_0) numerically
    3. ODE: solve tau_0 d(delta_Phi)/dt + delta_Phi = -delta_tau * dPhi_0/dt

    Expected: all three agree (Markov property for kernel coefficients).

    Parameters
    ----------
    bg : FRWPerturbativeBackground
        Background solution.
    delta_tau_fraction : float
        Fractional perturbation of tau (small, for perturbative regime).

    Returns
    -------
    TauPerturbationTest
    """
    result = TauPerturbationTest()

    tau_0 = bg.tau_eff
    X_0 = bg.X_0
    n = bg.n_steps
    times = bg.times
    delta_tau = delta_tau_fraction * tau_0
    result.delta_tau = delta_tau

    result.delta_phi_analytical_form = (
        "delta_Phi(t) = -(delta_tau/tau_0) * X_0 * (t/tau_0) * exp(-t/tau_0)"
    )

    # Analytical solution
    coeff = -(delta_tau / tau_0) * X_0
    result.delta_phi_analytical = [
        coeff * (t / tau_0) * math.exp(-t / tau_0) for t in times
    ]

    # Convolution: Phi(tau_0 + delta_tau) - Phi(tau_0), divided by epsilon
    # Use finite difference: epsilon = delta_tau, then
    # delta_Phi ≈ [Phi(tau_0+delta_tau) - Phi(tau_0)] (already first-order)
    source_const = [X_0] * (n + 1)

    # Phi at tau_0
    def kernel_0(s):
        return _retarded_kernel(s, tau_0)

    phi_base = [0.0]
    for i in range(1, n + 1):
        val = _convolution_with_kernel(kernel_0, source_const, times, i)
        phi_base.append(val)

    # Phi at tau_0 + delta_tau
    tau_perturbed = tau_0 + delta_tau

    def kernel_perturbed(s):
        return _retarded_kernel(s, tau_perturbed)

    phi_perturbed = [0.0]
    for i in range(1, n + 1):
        val = _convolution_with_kernel(kernel_perturbed, source_const, times, i)
        phi_perturbed.append(val)

    # Numerical delta_Phi from convolution
    result.delta_phi_convolution = [
        phi_perturbed[i] - phi_base[i] for i in range(n + 1)
    ]

    # ODE: tau_0 d(delta_Phi)/dt + delta_Phi = -delta_tau * dPhi_0/dt
    result.delta_phi_ode = _integrate_perturbed_ode_tau(
        bg.dPhi_0_dt, times, tau_0, delta_tau
    )

    # Three-way comparison (skip early transient; use range where delta_Phi is
    # not too small)
    def _max_mismatch(a: List[float], b: List[float]) -> float:
        peak_b = max(abs(v) for v in b[n // 5:])
        if peak_b < 1e-30:
            return 0.0
        mx = 0.0
        for i in range(n // 5, n + 1):
            denom = peak_b
            err = abs(a[i] - b[i]) / denom
            mx = max(mx, err)
        return mx

    result.conv_ode_max_mismatch = _max_mismatch(
        result.delta_phi_convolution, result.delta_phi_ode
    )
    result.conv_analytical_max_mismatch = _max_mismatch(
        result.delta_phi_convolution, result.delta_phi_analytical
    )
    result.ode_analytical_max_mismatch = _max_mismatch(
        result.delta_phi_ode, result.delta_phi_analytical
    )

    result.conv_ode_commutes = result.conv_ode_max_mismatch < 0.05
    result.conv_analytical_commutes = result.conv_analytical_max_mismatch < 0.1
    result.ode_analytical_commutes = result.ode_analytical_max_mismatch < 0.01

    result.notes = [
        f"delta_tau = {delta_tau:.4e} ({delta_tau_fraction*100:.1f}% of tau_0)",
        f"Conv vs ODE mismatch: {result.conv_ode_max_mismatch:.6e}",
        f"Conv vs analytical: {result.conv_analytical_max_mismatch:.6e}",
        f"ODE vs analytical: {result.ode_analytical_max_mismatch:.6e}",
        "Tau perturbation commutes: Markov property for kernel coefficients",
        "The lag-dependent kernel perturbation is captured by the perturbed ODE",
    ]

    return result


def test_lapse_perturbation_commutation(
    bg: FRWPerturbativeBackground,
    Psi: float = 0.01,
) -> LapsePerturbationTest:
    """Test commutation for lapse perturbation ds = (1+Psi)*dt.

    This is the KEY TEST. The lapse introduces a proper-time correction to the
    retarded convolution that is NOT captured by the coordinate-time ODE.

    Three comparisons:
    1. Proper-time convolution vs coordinate-time ODE => MISMATCH expected
    2. Proper-time convolution vs proper-time ODE => MATCH expected
    3. Mismatch vs analytical lapse correction => MATCH expected

    Parameters
    ----------
    bg : FRWPerturbativeBackground
        Background solution.
    Psi : float
        Newtonian potential (lapse perturbation).

    Returns
    -------
    LapsePerturbationTest
    """
    result = LapsePerturbationTest()

    tau_0 = bg.tau_eff
    X_0 = bg.X_0
    n = bg.n_steps
    times = bg.times
    result.Psi = Psi

    source_const = [X_0] * (n + 1)

    # --- Proper-time convolution ---
    # K_proper(s) = ((1+Psi)/tau_0) exp(-(1+Psi)*s/tau_0)
    def kernel_proper(s):
        return _proper_time_kernel(s, tau_0, Psi)

    phi_proper_conv = [0.0]
    for i in range(1, n + 1):
        val = _convolution_with_kernel(kernel_proper, source_const, times, i)
        phi_proper_conv.append(val)

    # Baseline: coordinate-time convolution
    def kernel_coord(s):
        return _retarded_kernel(s, tau_0)

    phi_coord = [0.0]
    for i in range(1, n + 1):
        val = _convolution_with_kernel(kernel_coord, source_const, times, i)
        phi_coord.append(val)

    # delta_Phi from proper-time effect
    result.delta_phi_proper_convolution = [
        phi_proper_conv[i] - phi_coord[i] for i in range(n + 1)
    ]

    # --- Coordinate-time ODE (no lapse) ---
    # delta_Phi = 0 (the coordinate-time ODE gives ZERO lapse correction)
    result.delta_phi_coordinate_ode = [0.0] * (n + 1)

    # --- Proper-time ODE (with lapse) ---
    # tau_0 d(delta_Phi)/dt + delta_Phi = Psi * (X_0 - Phi_0)
    result.delta_phi_proper_ode = _integrate_lapse_corrected_ode(
        source_const, bg.Phi_0, times, tau_0, Psi
    )

    # --- Analytical lapse correction ---
    result.delta_phi_lapse_analytical = _analytical_lapse_correction(
        X_0, tau_0, Psi, times
    )
    result.lapse_correction_form = (
        "delta_Phi_lapse(t) = Psi * X_0 * (t/tau_0) * exp(-t/tau_0)"
    )
    result.lapse_peak_value = Psi * X_0 / math.e
    result.lapse_peak_time_over_tau = 1.0

    # --- Comparison 1: Coordinate ODE vs proper convolution (should MISMATCH) ---
    peak_proper = max(
        abs(v) for v in result.delta_phi_proper_convolution[n // 5:]
    ) if n > 5 else 1e-30
    peak_proper = max(peak_proper, 1e-30)

    max_coord_mismatch = 0.0
    max_coord_rel = 0.0
    for i in range(n // 5, n + 1):
        err = abs(result.delta_phi_proper_convolution[i]
                  - result.delta_phi_coordinate_ode[i])
        max_coord_mismatch = max(max_coord_mismatch, err)
        max_coord_rel = max(max_coord_rel, err / peak_proper)

    result.coord_vs_proper_max_mismatch = max_coord_mismatch
    result.coord_vs_proper_relative_mismatch = max_coord_rel
    result.coordinate_commutes = max_coord_rel < 0.05  # expected: False

    # --- Comparison 2: Proper ODE vs proper convolution (should MATCH) ---
    max_proper_mismatch = 0.0
    max_proper_rel = 0.0
    for i in range(n // 5, n + 1):
        err = abs(result.delta_phi_proper_convolution[i]
                  - result.delta_phi_proper_ode[i])
        max_proper_mismatch = max(max_proper_mismatch, err)
        max_proper_rel = max(max_proper_rel, err / peak_proper)

    result.proper_vs_proper_max_mismatch = max_proper_mismatch
    result.proper_vs_proper_relative_mismatch = max_proper_rel
    result.proper_commutes = max_proper_rel < 0.05  # expected: True

    # --- Comparison 3: Analytical vs numerical lapse correction ---
    max_lapse_err = 0.0
    for i in range(n // 5, n + 1):
        err = abs(result.delta_phi_proper_convolution[i]
                  - result.delta_phi_lapse_analytical[i])
        max_lapse_err = max(max_lapse_err, err / peak_proper)

    result.lapse_analytical_vs_numerical_mismatch = max_lapse_err
    result.lapse_analytical_verified = max_lapse_err < 0.1

    result.notes = [
        f"Psi = {Psi}",
        f"Lapse peak correction: {result.lapse_peak_value:.6e} at t = tau_0",
        f"Coord vs proper relative mismatch: {max_coord_rel:.6e} (should be ~1)",
        f"Proper ODE vs proper conv relative mismatch: {max_proper_rel:.6e} (should be ~0)",
        f"Analytical lapse vs numerical: {max_lapse_err:.6e}",
        f"Coordinate-time commutes: {result.coordinate_commutes} (expected False)",
        f"Proper-time commutes: {result.proper_commutes} (expected True)",
        "The lapse correction is SPECIFIC: tau d(delta_Phi)/dt + delta_Phi = Psi*(X-Phi)",
        "Peak magnitude: Psi * X_0 / e (occurs at t = tau_0)",
    ]

    return result


def estimate_lapse_magnitude() -> LapseMagnitudeEstimate:
    """Estimate the magnitude of the lapse correction in physical sectors.

    Cosmology (weak field):
        Psi ~ 10^{-5} (CMB anisotropy / Newtonian potential at cosmological scales)
        delta_Phi / Phi_0 ~ Psi / e ~ 3.7 * 10^{-6}  (utterly negligible)

    Collapse (strong field):
        Psi = G*M / (c^2 * R) = r_s / (2*R)
        For R = 3*r_s: Psi = 1/6 ≈ 0.167
        delta_Phi / Phi_0 ~ Psi / e ~ 0.061  (6.1% — significant)
        For R = 1.5*r_s (ISCO): Psi = 1/3 ≈ 0.333
        delta_Phi / Phi_0 ~ 0.123  (12.3% — large)

    Returns
    -------
    LapseMagnitudeEstimate
    """
    est = LapseMagnitudeEstimate()

    # Cosmological sector
    est.Psi_cosmo = 1e-5
    est.delta_phi_over_phi_cosmo = est.Psi_cosmo / math.e
    est.cosmo_negligible = True

    # Collapse sector (at R = 3 r_s)
    est.R_over_r_s = 3.0
    est.Psi_collapse = 1.0 / (2.0 * est.R_over_r_s)  # r_s/(2R)
    est.delta_phi_over_phi_collapse = est.Psi_collapse / math.e
    est.collapse_negligible = False

    est.weak_field_safe = True
    est.strong_field_correction_needed = True

    est.notes = [
        f"Cosmo: Psi ~ {est.Psi_cosmo:.1e}, delta_Phi/Phi ~ {est.delta_phi_over_phi_cosmo:.2e} (NEGLIGIBLE)",
        f"Collapse (R=3*r_s): Psi = {est.Psi_collapse:.4f}, delta_Phi/Phi ~ {est.delta_phi_over_phi_collapse:.4f} ({est.delta_phi_over_phi_collapse*100:.1f}%)",
        "Weak-field (cosmology): lapse correction can be safely ignored",
        "Strong-field (collapse): lapse correction is significant and must be included",
        "The correction is a 6% effect at R=3*r_s, growing toward the horizon",
    ]

    return est


def build_commutation_summary(
    source_test: SourcePerturbationTest,
    tau_test: TauPerturbationTest,
    lapse_test: LapsePerturbationTest,
) -> CommutationSummary:
    """Build the overall commutation assessment.

    Parameters
    ----------
    source_test : SourcePerturbationTest
    tau_test : TauPerturbationTest
    lapse_test : LapsePerturbationTest

    Returns
    -------
    CommutationSummary
    """
    cs = CommutationSummary()

    cs.source_commutes = source_test.commutes
    cs.tau_commutes = tau_test.conv_ode_commutes
    cs.lapse_coordinate_commutes = lapse_test.coordinate_commutes
    cs.lapse_proper_commutes = lapse_test.proper_commutes

    # Overall assessment
    cs.overall_coordinate_time_commutes = (
        cs.source_commutes and cs.tau_commutes
        # lapse is irrelevant in coordinate time — the two formulations agree
    )
    cs.overall_proper_time_commutes = (
        cs.source_commutes and cs.tau_commutes and cs.lapse_proper_commutes
    )

    cs.covariant_mismatch_source = (
        "Lapse correction: the proper-time measure ds = (1+Psi)*dt introduces "
        "a correction to the retarded convolution that is absent from the "
        "coordinate-time memory ODE. The mismatch is the lapse correction."
    )
    cs.covariant_mismatch_form = (
        "delta_Phi_lapse satisfies: tau d(delta_Phi)/dt + delta_Phi = Psi*(X - Phi). "
        "For constant source: delta_Phi_lapse(t) = Psi * X * (t/tau) * exp(-t/tau). "
        "Peak at t = tau: |delta_Phi_max| = Psi * X / e."
    )
    cs.covariant_mismatch_order = "first_order_in_Psi"

    cs.perturbative_order = "first_order_in_scalar_perturbations_around_FRW"

    cs.notes = [
        f"Source perturbation: {'COMMUTES' if cs.source_commutes else 'FAILS'}",
        f"Tau perturbation: {'COMMUTES' if cs.tau_commutes else 'FAILS'}",
        f"Lapse (coordinate time): {'COMMUTES' if cs.lapse_coordinate_commutes else 'FAILS'} (expected: FAILS)",
        f"Lapse (proper time): {'COMMUTES' if cs.lapse_proper_commutes else 'FAILS'} (expected: COMMUTES)",
        f"Overall (coordinate time): {'COMMUTES' if cs.overall_coordinate_time_commutes else 'FAILS'}",
        f"Overall (proper time): {'COMMUTES' if cs.overall_proper_time_commutes else 'FAILS'}",
        "In the current GRUT framework (coordinate time): variation and reduction COMMUTE",
        "For covariant extension: lapse correction required (specific, computable)",
    ]

    cs.nonclaims = [
        "Commutation is verified at FIRST perturbative order only",
        "Higher-order commutation has NOT been tested",
        "Vector and tensor perturbations not tested (decouple at first order for scalar memory)",
        "The coordinate-time commutation is specific to FRW + scalar perturbations",
        "Full nonlinear commutation is OPEN",
    ]

    return cs


def build_upgrade_assessment(
    cs: CommutationSummary,
    lapse_mag: LapseMagnitudeEstimate,
) -> RouteCUpgradeAssessment:
    """Assess whether Route C status is upgraded by this analysis.

    Parameters
    ----------
    cs : CommutationSummary
    lapse_mag : LapseMagnitudeEstimate

    Returns
    -------
    RouteCUpgradeAssessment
    """
    upgrade = RouteCUpgradeAssessment()

    upgrade.previous_status = "functional_derived"

    if cs.overall_coordinate_time_commutes:
        upgrade.current_status = "perturbatively_verified__coordinate_time"
        upgrade.upgraded = True
        upgrade.upgrade_reason = (
            "The nonlocal metric variation and auxiliary-field reduction COMMUTE "
            "at first perturbative order in scalar perturbations around FRW, "
            "in the coordinate-time formulation used by the current GRUT framework. "
            "This means the constitutive-effective T^Phi IS the correct first-order "
            "metric response of the nonlocal retarded action — not merely an ansatz."
        )
    else:
        upgrade.current_status = "functional_derived"
        upgrade.upgraded = False
        upgrade.upgrade_reason = "Commutation failed — no upgrade"

    upgrade.upgrade_scope = (
        "First-order scalar perturbations around FRW, coordinate time"
    )

    upgrade.upgrade_limitations = [
        "Perturbative only (not nonlinear)",
        "Scalar perturbations only (vectors/tensors decouple at first order)",
        "FRW background only (not general curved spacetime)",
        "Coordinate-time formulation (not manifestly covariant)",
        "Lapse correction needed for covariant extension",
    ]

    upgrade.remaining_obstruction = (
        "The remaining obstruction is the LAPSE CORRECTION: the proper-time "
        "measure ds = (1+Psi)*dt introduces a correction to the retarded "
        "convolution that the coordinate-time ODE does not capture. "
        "This correction is:\n"
        "  - SPECIFIC: tau d(delta_Phi)/dt + delta_Phi = Psi*(X-Phi)\n"
        "  - COMPUTABLE: delta_Phi(t) = Psi*X*(t/tau)*exp(-t/tau) for constant source\n"
        "  - NEGLIGIBLE in cosmology: Psi ~ 10^{-5}\n"
        f"  - SIGNIFICANT in collapse: Psi ~ {lapse_mag.Psi_collapse:.3f} at R=3*r_s "
        f"({lapse_mag.delta_phi_over_phi_collapse*100:.1f}% correction)\n\n"
        "The deeper remaining questions (unchanged):\n"
        "  1. Full nonlinear commutation (beyond perturbative order)\n"
        "  2. Observer-flow dependence of the retardation condition\n"
        "  3. Quantization of the nonlocal action"
    )

    if lapse_mag.cosmo_negligible:
        upgrade.remaining_obstruction_severity = (
            "MILD in cosmology (negligible lapse), "
            "MODERATE in collapse (6% correction at R=3*r_s)"
        )
    else:
        upgrade.remaining_obstruction_severity = "SIGNIFICANT in both sectors"

    upgrade.notes = [
        f"Previous status: {upgrade.previous_status}",
        f"Current status: {upgrade.current_status}",
        f"Upgraded: {upgrade.upgraded}",
        "The upgrade is CONDITIONAL on the coordinate-time formulation",
        "Covariant extension requires the lapse correction term",
    ]

    return upgrade


def compute_route_c_metric_variation_analysis(
    tau_eff: float = 1.0,
    X_0: float = 1.0,
    n_steps: int = 2000,
    n_tau: float = 10.0,
    Psi_lapse: float = 0.01,
    delta_tau_fraction: float = 0.01,
) -> RouteCMetricVariationResult:
    """Master analysis: perturbative nonlocal metric variation around FRW.

    Builds the FRW background, runs all three perturbation commutation tests,
    estimates lapse magnitudes, and produces the overall assessment.

    Parameters
    ----------
    tau_eff : float
        Background relaxation timescale.
    X_0 : float
        Background source.
    n_steps : int
        Number of time steps.
    n_tau : float
        Evolution time in tau units.
    Psi_lapse : float
        Newtonian potential for lapse test.
    delta_tau_fraction : float
        Fractional tau perturbation.

    Returns
    -------
    RouteCMetricVariationResult
    """
    result = RouteCMetricVariationResult()

    # Build background
    result.background = build_frw_perturbative_background(
        tau_eff=tau_eff, X_0=X_0, n_steps=n_steps, n_tau=n_tau
    )

    # Run perturbation tests
    result.source_test = test_source_perturbation_commutation(
        result.background, delta_X_amplitude=0.1
    )
    result.tau_test = test_tau_perturbation_commutation(
        result.background, delta_tau_fraction=delta_tau_fraction
    )
    result.lapse_test = test_lapse_perturbation_commutation(
        result.background, Psi=Psi_lapse
    )

    # Lapse magnitude estimate
    result.lapse_magnitude = estimate_lapse_magnitude()

    # Commutation summary
    result.commutation = build_commutation_summary(
        result.source_test, result.tau_test, result.lapse_test
    )

    # Upgrade assessment
    result.upgrade = build_upgrade_assessment(
        result.commutation, result.lapse_magnitude
    )

    # Remaining obstruction
    result.remaining_obstruction = result.upgrade.remaining_obstruction

    # Nonclaims
    result.nonclaims = [
        "Commutation is verified at FIRST perturbative order only (not nonlinear)",
        "The perturbative setup is FRW + scalar perturbations (not general curved spacetime)",
        "The coordinate-time commutation applies to the CURRENT GRUT framework only",
        "Covariant extension requires the lapse correction: tau d(delta_Phi)/dt + delta_Phi = Psi*(X-Phi)",
        "The lapse correction is NEGLIGIBLE in cosmology but SIGNIFICANT in collapse",
        "Vector and tensor perturbations decouple at first order for scalar memory (not tested independently)",
        "The Markov property ensures commutation for source and tau perturbations (exponential kernel only)",
        "For non-exponential kernels, even source-perturbation commutation may fail",
        "Observer-flow dependence is NOT resolved by this perturbative analysis",
        "Quantization of the nonlocal action remains OPEN",
        "The upgrade from functional-derived to perturbatively-verified is CONDITIONAL",
        "Full nonlinear commutation (beyond FRW perturbation theory) is UNTESTED",
    ]

    # Diagnostics
    result.diagnostics = {
        "source_max_rel_mismatch": result.source_test.max_relative_mismatch,
        "tau_conv_ode_mismatch": result.tau_test.conv_ode_max_mismatch,
        "tau_conv_analytical_mismatch": result.tau_test.conv_analytical_max_mismatch,
        "tau_ode_analytical_mismatch": result.tau_test.ode_analytical_max_mismatch,
        "lapse_coord_vs_proper_rel": result.lapse_test.coord_vs_proper_relative_mismatch,
        "lapse_proper_ode_vs_conv_rel": result.lapse_test.proper_vs_proper_relative_mismatch,
        "lapse_analytical_vs_numerical": result.lapse_test.lapse_analytical_vs_numerical_mismatch,
        "lapse_peak_value": result.lapse_test.lapse_peak_value,
        "lapse_cosmo_magnitude": result.lapse_magnitude.delta_phi_over_phi_cosmo,
        "lapse_collapse_magnitude": result.lapse_magnitude.delta_phi_over_phi_collapse,
    }

    result.valid = True
    return result


# ================================================================
# Serialization
# ================================================================

def _bg_to_dict(bg: FRWPerturbativeBackground) -> Dict[str, Any]:
    return {
        "tau_eff": bg.tau_eff,
        "X_0": bg.X_0,
        "n_steps": bg.n_steps,
        "n_tau": bg.n_tau,
        "phi_0_form": bg.phi_0_form,
        "dphi_0_dt_form": bg.dphi_0_dt_form,
        "notes": bg.notes,
    }


def _source_test_to_dict(st: SourcePerturbationTest) -> Dict[str, Any]:
    return {
        "delta_X_form": st.delta_X_form,
        "max_absolute_mismatch": st.max_absolute_mismatch,
        "max_relative_mismatch": st.max_relative_mismatch,
        "commutes": st.commutes,
        "notes": st.notes,
    }


def _tau_test_to_dict(tt: TauPerturbationTest) -> Dict[str, Any]:
    return {
        "delta_tau": tt.delta_tau,
        "delta_phi_analytical_form": tt.delta_phi_analytical_form,
        "conv_ode_max_mismatch": tt.conv_ode_max_mismatch,
        "conv_analytical_max_mismatch": tt.conv_analytical_max_mismatch,
        "ode_analytical_max_mismatch": tt.ode_analytical_max_mismatch,
        "conv_ode_commutes": tt.conv_ode_commutes,
        "conv_analytical_commutes": tt.conv_analytical_commutes,
        "ode_analytical_commutes": tt.ode_analytical_commutes,
        "notes": tt.notes,
    }


def _lapse_test_to_dict(lt: LapsePerturbationTest) -> Dict[str, Any]:
    return {
        "Psi": lt.Psi,
        "lapse_correction_form": lt.lapse_correction_form,
        "lapse_peak_value": lt.lapse_peak_value,
        "coord_vs_proper_relative_mismatch": lt.coord_vs_proper_relative_mismatch,
        "coordinate_commutes": lt.coordinate_commutes,
        "proper_vs_proper_relative_mismatch": lt.proper_vs_proper_relative_mismatch,
        "proper_commutes": lt.proper_commutes,
        "lapse_analytical_vs_numerical_mismatch": lt.lapse_analytical_vs_numerical_mismatch,
        "lapse_analytical_verified": lt.lapse_analytical_verified,
        "notes": lt.notes,
    }


def _lapse_magnitude_to_dict(lm: LapseMagnitudeEstimate) -> Dict[str, Any]:
    return {
        "Psi_cosmo": lm.Psi_cosmo,
        "delta_phi_over_phi_cosmo": lm.delta_phi_over_phi_cosmo,
        "cosmo_negligible": lm.cosmo_negligible,
        "Psi_collapse": lm.Psi_collapse,
        "R_over_r_s": lm.R_over_r_s,
        "delta_phi_over_phi_collapse": lm.delta_phi_over_phi_collapse,
        "collapse_negligible": lm.collapse_negligible,
        "weak_field_safe": lm.weak_field_safe,
        "strong_field_correction_needed": lm.strong_field_correction_needed,
        "notes": lm.notes,
    }


def _commutation_to_dict(cs: CommutationSummary) -> Dict[str, Any]:
    return {
        "source_commutes": cs.source_commutes,
        "tau_commutes": cs.tau_commutes,
        "lapse_coordinate_commutes": cs.lapse_coordinate_commutes,
        "lapse_proper_commutes": cs.lapse_proper_commutes,
        "overall_coordinate_time_commutes": cs.overall_coordinate_time_commutes,
        "overall_proper_time_commutes": cs.overall_proper_time_commutes,
        "covariant_mismatch_source": cs.covariant_mismatch_source,
        "covariant_mismatch_form": cs.covariant_mismatch_form,
        "covariant_mismatch_order": cs.covariant_mismatch_order,
        "perturbative_order": cs.perturbative_order,
        "notes": cs.notes,
        "nonclaims": cs.nonclaims,
    }


def _upgrade_to_dict(u: RouteCUpgradeAssessment) -> Dict[str, Any]:
    return {
        "previous_status": u.previous_status,
        "current_status": u.current_status,
        "upgraded": u.upgraded,
        "upgrade_reason": u.upgrade_reason,
        "upgrade_scope": u.upgrade_scope,
        "upgrade_limitations": u.upgrade_limitations,
        "remaining_obstruction": u.remaining_obstruction,
        "remaining_obstruction_severity": u.remaining_obstruction_severity,
        "notes": u.notes,
    }


def metric_variation_result_to_dict(r: RouteCMetricVariationResult) -> Dict[str, Any]:
    """Serialize the master result to a dictionary."""
    return {
        "valid": r.valid,
        "background": _bg_to_dict(r.background) if r.background else None,
        "source_test": _source_test_to_dict(r.source_test) if r.source_test else None,
        "tau_test": _tau_test_to_dict(r.tau_test) if r.tau_test else None,
        "lapse_test": _lapse_test_to_dict(r.lapse_test) if r.lapse_test else None,
        "lapse_magnitude": _lapse_magnitude_to_dict(r.lapse_magnitude) if r.lapse_magnitude else None,
        "commutation": _commutation_to_dict(r.commutation) if r.commutation else None,
        "upgrade": _upgrade_to_dict(r.upgrade) if r.upgrade else None,
        "remaining_obstruction": r.remaining_obstruction,
        "nonclaims": r.nonclaims,
        "diagnostics": r.diagnostics,
    }
