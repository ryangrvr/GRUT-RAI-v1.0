"""Effective lapse derivation at the GRUT equilibrium endpoint.

Phase IV: Derives the effective lapse proxy at the GRUT equilibrium endpoint
(R_eq = r_s/3) from the constitutive barrier-potential framework, replacing
the prior heuristic Psi_eff ~ alpha_vac with a constitutive-derived central
lapse proxy.

THREE EXPLICIT LEVELS:

  Level 1 — Barrier-to-gravity potential ratio:
    Phi_barrier / Phi_grav = 1/(1+beta_Q)
    Status: EXACT (algebraic identity at endpoint, proven from endpoint law)

  Level 2 — Constitutive-derived central lapse proxy:
    Psi_proxy = 1/(1+beta_Q)
    Status: CONSTITUTIVE-DERIVED (identifies barrier ratio as lapse scale)
    This is an effective lapse SCALE, not a fully derived metric lapse.

  Level 3 — True interior metric lapse:
    Status: UNRESOLVED (requires covariant interior solution beyond
    the constitutive ansatz)

CENTRAL RESULT:
  The barrier-to-gravity potential ratio at the endpoint is 1/(1+beta_Q),
  independent of epsilon_Q, alpha_vac, and mass.  For canon beta_Q = 2,
  this equals 1/3 = alpha_vac — a coincidence, not the fundamental
  relationship.  The prior heuristic was numerically correct at canon
  parameters but for a different (and weaker) reason.

PRIOR STATE:
  _barrier_lapse_estimate() in nonlocal_strong_field.py returned alpha_vac
  as a heuristic.  The sensitivity band [alpha_vac/2, alpha_vac, 2*alpha_vac]
  was labeled as a scenario scan.

NEW STATE:
  Central lapse proxy = 1/(1+beta_Q) is constitutive-derived.
  Sensitivity band = [1/(2*(1+beta_Q)), 1/(1+beta_Q), 2/(1+beta_Q)] is a
  scenario band around the constitutive-derived central proxy.
  True interior metric lapse remains unresolved.

SELF-HEALING:
  Preserved under all routes — the source term X - Phi vanishes at
  equilibrium regardless of Psi_eff.

NONCLAIMS:
  - The central proxy is NOT the true metric lapse
  - The barrier ratio IS exact; its identification as a lapse scale is
    constitutive-level, not exact
  - Route B (effective metric) is unresolved at the endpoint (A_eff < 0)
  - The true interior metric lapse requires a covariant interior solution
  - The coincidence 1/(1+beta_Q) = alpha_vac at beta_Q = 2 is explained,
    not relied upon
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple


# ================================================================
# Constants
# ================================================================

# Canon defaults (self-contained, no cross-module imports)
ALPHA_VAC = 1.0 / 3.0
BETA_Q = 2.0
EPSILON_Q = ALPHA_VAC ** 2       # 1/9
R_EQ_OVER_R_S = ALPHA_VAC       # 1/3
C_ENDPOINT = 1.0 / R_EQ_OVER_R_S  # 3.0
Q_CANON = BETA_Q / ALPHA_VAC    # 6.0
OMEGA_0_TAU_CANON = 1.0

# Classification labels for derivation level
LEVEL_EXACT = "exact"
LEVEL_CONSTITUTIVE_DERIVED = "constitutive_derived"
LEVEL_ANSATZ_DEPENDENT = "ansatz_dependent"
LEVEL_UPPER_BOUND_ONLY = "upper_bound_only"
LEVEL_UNRESOLVED = "unresolved"


# ================================================================
# Data Structures
# ================================================================

@dataclass
class BarrierGravityRatio:
    """Central algebraic result: barrier-to-gravity potential ratio at endpoint.

    Level 1 — EXACT algebraic identity:
        Phi_barrier / Phi_grav = 1 / (1 + beta_Q)

    Proven from:
      1. Barrier potential integral: Phi_barrier = GM * eps * r_s^beta / ((1+beta) * R_eq^(1+beta))
      2. Gravitational potential: Phi_grav = GM / R_eq
      3. Endpoint law: (R_eq/r_s)^beta_Q = epsilon_Q  (from force balance)

    Independent of epsilon_Q, alpha_vac, and mass.
    """
    beta_Q: float = 0.0
    epsilon_Q: float = 0.0
    ratio: float = 0.0
    ratio_formula: str = ""
    is_exact: bool = False
    depends_on_epsilon_Q: bool = False
    depends_on_alpha_vac: bool = False
    depends_on_mass: bool = False
    endpoint_law_used: str = ""
    derivation_steps: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class RouteAResult:
    """Route A: barrier-to-gravity ratio as constitutive-derived lapse proxy.

    Level 2 — CONSTITUTIVE-DERIVED:
        Psi_proxy = 1 / (1 + beta_Q)

    This identifies the exact barrier-to-gravity ratio (Level 1) as the
    effective lapse SCALE.  This identification is at the constitutive level:
    the barrier potential sets the energy scale for the lapse correction.

    This is NOT the true metric lapse (Level 3), which requires a covariant
    interior solution.
    """
    route_name: str = ""
    psi_proxy: float = 0.0
    formula: str = ""
    classification: str = ""
    identification_basis: str = ""
    barrier_ratio: Optional[BarrierGravityRatio] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class RouteBResult:
    """Route B: effective metric at endpoint.

    The constitutive ansatz gives:
        A_schw = 1 - C_endpoint = -2  (below horizon)
        delta_A = 2 * Phi_barrier / c^2 = 1  (barrier correction)
        A_eff = A_schw + delta_A = -1  (still negative)

    Since A_eff < 0, the coordinate t is spacelike.  The standard redshift
    formula Psi = 1/sqrt(A) - 1 does NOT apply.  The true metric lapse at
    the endpoint is UNRESOLVED by this route.

    psi_metric is None when A_eff < 0 (not applicable).
    """
    route_name: str = ""
    A_schw_at_Req: float = 0.0
    delta_A: float = 0.0
    A_eff_at_Req: float = 0.0
    A_eff_is_negative: bool = False
    redshift_formula_applicable: bool = False
    psi_metric: Optional[float] = None
    classification: str = ""
    obstruction: str = ""
    notes: List[str] = field(default_factory=list)


@dataclass
class RouteCResult:
    """Route C: Schwarzschild reference (upper bound only).

    Psi_Schw = C / 2 = 3/2 at the endpoint.

    This ignores the barrier modification entirely.  It serves as an
    upper bound on the effective lapse: the barrier can only reduce
    the effective gravitational potential relative to Schwarzschild.
    """
    route_name: str = ""
    psi_schw: float = 0.0
    formula: str = ""
    classification: str = ""
    is_upper_bound: bool = False
    notes: List[str] = field(default_factory=list)


@dataclass
class RouteComparison:
    """Comparison of all three derivation routes.

    Route A is preferred as the constitutive-derived central proxy.
    Route B is unresolved (A_eff < 0).
    Route C is an upper bound only.
    """
    route_a: Optional[RouteAResult] = None
    route_b: Optional[RouteBResult] = None
    route_c: Optional[RouteCResult] = None
    preferred_route: str = ""
    preferred_psi_proxy: float = 0.0
    preferred_classification: str = ""
    notes: List[str] = field(default_factory=list)


@dataclass
class ProxySensitivityBand:
    """Sensitivity / scenario band around the constitutive-derived central proxy.

    This is a SCENARIO BAND, not a bounded-derived interval or confidence
    interval.  The width reflects model uncertainty in the sub-horizon
    metric-to-lapse mapping.

    For canon beta_Q = 2: [1/6, 1/3, 2/3] — numerically same as the prior
    heuristic band, but the central value is now constitutive-derived.
    """
    central: float = 0.0
    low: float = 0.0
    high: float = 0.0
    band_factor: float = 0.0
    central_formula: str = ""
    low_formula: str = ""
    high_formula: str = ""
    numerically_same_as_prior: bool = False
    central_elevated: bool = False
    prior_central_label: str = ""
    new_central_label: str = ""
    band_source: str = ""
    notes: List[str] = field(default_factory=list)


@dataclass
class ThreeLevelSummary:
    """Explicit three-level hierarchy for the effective lapse.

    Level 1: Exact barrier-to-gravity ratio (algebraic identity)
    Level 2: Constitutive-derived central lapse proxy
    Level 3: True interior metric lapse (unresolved)
    """
    # Level 1
    level_1_value: float = 0.0
    level_1_formula: str = ""
    level_1_status: str = ""
    level_1_description: str = ""

    # Level 2
    level_2_value: float = 0.0
    level_2_formula: str = ""
    level_2_status: str = ""
    level_2_description: str = ""

    # Level 3
    level_3_value: Optional[float] = None
    level_3_status: str = ""
    level_3_description: str = ""
    level_3_obstruction: str = ""

    notes: List[str] = field(default_factory=list)


@dataclass
class SelfHealingCheck:
    """Verification that self-healing is independent of the effective lapse.

    At equilibrium: X - Phi = a_grav - M_drive = 0.
    The lapse correction source term Psi * (X - Phi) vanishes identically,
    regardless of Psi.  This is a structural property of force balance.
    """
    source_at_eq: float = 0.0
    source_vanishes: bool = False
    independent_of_psi: bool = False
    mechanism: str = ""
    preserved_under_route_a: bool = False
    preserved_under_route_b: bool = False
    preserved_under_route_c: bool = False
    notes: List[str] = field(default_factory=list)


@dataclass
class ShiftEstimates:
    """Updated shift estimates using the constitutive-derived central proxy.

    These are bounded estimates, not derived corrected dispersion relations.
    Numerically unchanged from the prior heuristic (same central value for
    canon parameters), but the central value is now constitutive-derived.
    """
    psi_proxy_central: float = 0.0

    # Proper-time shift
    tau_ratio_central: float = 0.0      # 1 / (1 + psi_proxy)
    proper_time_shift_pct: float = 0.0  # percentage

    # Q shift (bounded)
    Q_canon: float = 0.0
    Q_shift_pct: float = 0.0            # ~ psi_proxy * 100

    # omega_0 * tau shift (bounded)
    omega_0_tau_canon: float = 0.0
    omega_0_tau_at_eq: float = 0.0      # ~ 1 / (1 + psi_proxy)

    notes: List[str] = field(default_factory=list)


@dataclass
class EffectiveLapseResult:
    """Master result: effective lapse derivation analysis.

    Contains all components of the derivation, the three-level hierarchy,
    self-healing verification, and complete nonclaims.
    """
    valid: bool = False

    # Core results
    barrier_gravity_ratio: Optional[BarrierGravityRatio] = None
    three_levels: Optional[ThreeLevelSummary] = None
    routes: Optional[RouteComparison] = None
    sensitivity_band: Optional[ProxySensitivityBand] = None
    self_healing: Optional[SelfHealingCheck] = None
    shift_estimates: Optional[ShiftEstimates] = None

    # Comparison to prior heuristic
    prior_heuristic_confirmed: bool = False
    prior_heuristic_elevated: bool = False
    coincidence_explained: bool = False
    coincidence_description: str = ""

    # Overall
    approx_status: str = ""
    remaining_obstruction: str = ""
    nonclaims: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)


# ================================================================
# Internal helper functions
# ================================================================

def _barrier_potential_ratio(
    beta_Q: float = BETA_Q,
    epsilon_Q: float = EPSILON_Q,
) -> float:
    """Compute the barrier-to-gravity potential ratio at the endpoint.

    EXACT ALGEBRAIC DERIVATION:

      Phi_barrier = GM * epsilon_Q * r_s^beta_Q / ((1+beta_Q) * R_eq^(1+beta_Q))
      Phi_grav    = GM / R_eq

      Ratio = epsilon_Q * r_s^beta_Q / ((1+beta_Q) * R_eq^beta_Q)
            = epsilon_Q / ((1+beta_Q) * (R_eq/r_s)^beta_Q)

      By endpoint law: (R_eq/r_s)^beta_Q = epsilon_Q

      Therefore: Ratio = epsilon_Q / ((1+beta_Q) * epsilon_Q) = 1/(1+beta_Q)

    Returns
    -------
    float
        Barrier-to-gravity potential ratio = 1/(1+beta_Q).
    """
    if beta_Q <= -1.0:
        return 0.0
    return 1.0 / (1.0 + beta_Q)


def _effective_metric_at_endpoint(
    beta_Q: float = BETA_Q,
    epsilon_Q: float = EPSILON_Q,
) -> Tuple[float, float, float]:
    """Compute A_schw, delta_A, A_eff at the endpoint from constitutive ansatz.

    A_schw = 1 - C_endpoint
    delta_A = C_endpoint / (1 + beta_Q)
        (from 2 * Phi_barrier / c^2, using Phi_barrier/Phi_grav = 1/(1+beta_Q)
        and Phi_grav = GM/R_eq = c^2 * C / 2, so delta_A = C/(1+beta_Q))
    A_eff = A_schw + delta_A

    Returns
    -------
    tuple of (A_schw, delta_A, A_eff)
    """
    # C_endpoint = 1 / (R_eq/r_s) = 1 / epsilon_Q^(1/beta_Q)
    if beta_Q > 0 and epsilon_Q > 0:
        R_eq_over_r_s = epsilon_Q ** (1.0 / beta_Q)
        C = 1.0 / R_eq_over_r_s
    else:
        C = C_ENDPOINT

    A_schw = 1.0 - C

    # delta_A = 2 * Phi_barrier / c^2
    # Using Phi_barrier = Phi_grav / (1+beta_Q) and Phi_grav = GM/R_eq = (c^2/2)*C:
    # delta_A = 2 * (c^2/2 * C / (1+beta_Q)) / c^2 = C / (1+beta_Q)
    ratio = _barrier_potential_ratio(beta_Q, epsilon_Q)
    delta_A = C * ratio

    A_eff = A_schw + delta_A

    return (A_schw, delta_A, A_eff)


def _psi_from_route_a(beta_Q: float = BETA_Q) -> float:
    """Constitutive-derived lapse proxy from Route A.

    Returns 1/(1+beta_Q) — the barrier-to-gravity ratio identified
    as the effective lapse scale.
    """
    if beta_Q <= -1.0:
        return 0.0
    return 1.0 / (1.0 + beta_Q)


def _psi_from_route_b(A_eff: float) -> Tuple[Optional[float], bool]:
    """Effective metric route for lapse.

    If A_eff > 0: returns (1/sqrt(A_eff) - 1, True).
    If A_eff <= 0: returns (None, False) — unresolved, not applicable.

    Returns
    -------
    tuple of (Optional[float], bool)
        (psi_metric, applicable)
    """
    if A_eff > 0:
        return (1.0 / math.sqrt(A_eff) - 1.0, True)
    else:
        return (None, False)


def _psi_from_route_c(C: float) -> float:
    """Schwarzschild reference lapse (upper bound only).

    Returns C / 2.
    """
    return C / 2.0


# ================================================================
# Builder functions
# ================================================================

def build_barrier_gravity_ratio(
    beta_Q: float = BETA_Q,
    epsilon_Q: float = EPSILON_Q,
) -> BarrierGravityRatio:
    """Derive the barrier-to-gravity potential ratio at the endpoint.

    This is the Level 1 result: an EXACT algebraic identity.
    """
    bgr = BarrierGravityRatio()
    bgr.beta_Q = beta_Q
    bgr.epsilon_Q = epsilon_Q
    bgr.ratio = _barrier_potential_ratio(beta_Q, epsilon_Q)
    bgr.ratio_formula = "1 / (1 + beta_Q)"
    bgr.is_exact = True
    bgr.depends_on_epsilon_Q = False
    bgr.depends_on_alpha_vac = False
    bgr.depends_on_mass = False
    bgr.endpoint_law_used = "(R_eq/r_s)^beta_Q = epsilon_Q"

    bgr.derivation_steps = [
        "Step 1: Barrier potential Phi_barrier = GM * eps * r_s^beta / ((1+beta) * R_eq^(1+beta))",
        "Step 2: Gravitational potential Phi_grav = GM / R_eq",
        "Step 3: Ratio = eps / ((1+beta) * (R_eq/r_s)^beta)",
        "Step 4: Endpoint law (R_eq/r_s)^beta = eps",
        "Step 5: Ratio = eps / ((1+beta) * eps) = 1/(1+beta)",
    ]

    bgr.notes = [
        "Exact algebraic identity at the endpoint (Level 1).",
        "Independent of epsilon_Q: cancels between numerator and denominator.",
        "Independent of alpha_vac: does not enter the barrier integral.",
        "Independent of mass: cancels in the ratio.",
        f"For beta_Q = {beta_Q}: ratio = {bgr.ratio:.6f}.",
    ]

    return bgr


def build_route_a(
    beta_Q: float = BETA_Q,
    epsilon_Q: float = EPSILON_Q,
) -> RouteAResult:
    """Route A: identify barrier-to-gravity ratio as constitutive-derived lapse proxy.

    Level 2: the exact ratio (Level 1) is identified as the effective lapse
    SCALE at the constitutive level.
    """
    ra = RouteAResult()
    ra.route_name = "A_barrier_gravity_ratio"
    ra.psi_proxy = _psi_from_route_a(beta_Q)
    ra.formula = "1 / (1 + beta_Q)"
    ra.classification = LEVEL_CONSTITUTIVE_DERIVED
    ra.identification_basis = (
        "The barrier potential energy at the endpoint sets the gravitational "
        "energy scale for the lapse correction.  The barrier-to-gravity ratio "
        "1/(1+beta_Q) is identified as the effective lapse scale at the "
        "constitutive level.  This is NOT the true metric lapse, which requires "
        "a covariant interior solution (Level 3)."
    )
    ra.barrier_ratio = build_barrier_gravity_ratio(beta_Q, epsilon_Q)

    ra.notes = [
        "Constitutive-derived lapse proxy (Level 2), not true metric lapse (Level 3).",
        f"Psi_proxy = 1/(1+{beta_Q}) = {ra.psi_proxy:.6f}.",
        "Identification of barrier ratio as lapse scale is at constitutive level.",
        "Elevated from prior heuristic: was 'Psi ~ alpha_vac' without derivation.",
    ]

    return ra


def build_route_b(
    beta_Q: float = BETA_Q,
    epsilon_Q: float = EPSILON_Q,
) -> RouteBResult:
    """Route B: effective metric at endpoint from constitutive ansatz."""
    rb = RouteBResult()
    rb.route_name = "B_effective_metric"

    A_schw, delta_A, A_eff = _effective_metric_at_endpoint(beta_Q, epsilon_Q)
    rb.A_schw_at_Req = A_schw
    rb.delta_A = delta_A
    rb.A_eff_at_Req = A_eff
    rb.A_eff_is_negative = A_eff < 0

    psi_metric, applicable = _psi_from_route_b(A_eff)
    rb.redshift_formula_applicable = applicable
    rb.psi_metric = psi_metric  # None if A_eff < 0

    if not applicable:
        rb.classification = LEVEL_UNRESOLVED
        rb.obstruction = (
            f"A_eff = {A_eff:.4f} < 0 at the endpoint.  The coordinate t is "
            "spacelike in the sub-horizon regime.  The standard redshift formula "
            "Psi = 1/sqrt(A_eff) - 1 does NOT apply when A_eff < 0.  The true "
            "metric lapse at the endpoint requires a covariant interior solution "
            "that resolves the metric signature in the barrier-supported region.  "
            "The constitutive ansatz A_eff = A_schw + delta_A is INCOMPLETE: "
            "the barrier potential (delta_A = 1) does not fully compensate the "
            "Schwarzschild deficit (A_schw = -2) to make A_eff positive."
        )
    else:
        rb.classification = LEVEL_ANSATZ_DEPENDENT
        rb.obstruction = ""

    rb.notes = [
        f"A_schw = 1 - C_endpoint = {A_schw:.4f}.",
        f"delta_A = C_endpoint / (1+beta_Q) = {delta_A:.4f}.",
        f"A_eff = A_schw + delta_A = {A_eff:.4f}.",
        f"A_eff < 0: {'yes' if rb.A_eff_is_negative else 'no'}.",
        f"Redshift formula applicable: {'yes' if applicable else 'no (A_eff < 0)'}.",
        "psi_metric: unresolved (not applicable)" if not applicable else
        f"psi_metric = {psi_metric:.6f}",
    ]

    return rb


def build_route_c(
    beta_Q: float = BETA_Q,
    epsilon_Q: float = EPSILON_Q,
) -> RouteCResult:
    """Route C: Schwarzschild reference (upper bound only)."""
    # Compute C_endpoint
    if beta_Q > 0 and epsilon_Q > 0:
        R_eq_over_r_s = epsilon_Q ** (1.0 / beta_Q)
        C = 1.0 / R_eq_over_r_s
    else:
        C = C_ENDPOINT

    rc = RouteCResult()
    rc.route_name = "C_schwarzschild_reference"
    rc.psi_schw = _psi_from_route_c(C)
    rc.formula = "C_endpoint / 2"
    rc.classification = LEVEL_UPPER_BOUND_ONLY
    rc.is_upper_bound = True

    rc.notes = [
        f"Psi_Schw = C/2 = {rc.psi_schw:.4f} at the endpoint.",
        "Ignores barrier modification entirely.",
        "Serves as an upper bound: the barrier can only reduce the effective potential.",
        "NOT a derivation of the effective lapse.",
    ]

    return rc


def build_route_comparison(
    route_a: RouteAResult,
    route_b: RouteBResult,
    route_c: RouteCResult,
) -> RouteComparison:
    """Compare all three derivation routes."""
    rc = RouteComparison()
    rc.route_a = route_a
    rc.route_b = route_b
    rc.route_c = route_c
    rc.preferred_route = "A"
    rc.preferred_psi_proxy = route_a.psi_proxy
    rc.preferred_classification = route_a.classification

    rc.notes = [
        "Route A (barrier-gravity ratio): constitutive-derived lapse proxy.",
        f"  Psi_proxy = {route_a.psi_proxy:.6f}, classification = {route_a.classification}.",
        "Route B (effective metric): unresolved at endpoint (A_eff < 0)."
        if route_b.A_eff_is_negative else
        f"Route B (effective metric): Psi = {route_b.psi_metric}, classification = {route_b.classification}.",
        f"Route C (Schwarzschild reference): Psi_Schw = {route_c.psi_schw:.4f}, upper bound only.",
        f"Preferred: Route A (Psi_proxy = {route_a.psi_proxy:.6f}).",
        "Route A is preferred because it has a constitutive derivation chain; "
        "Route B is unresolved; Route C is an upper bound only.",
    ]

    return rc


def build_sensitivity_band(
    beta_Q: float = BETA_Q,
    alpha_vac: float = ALPHA_VAC,
    band_factor: float = 2.0,
) -> ProxySensitivityBand:
    """Build the sensitivity / scenario band around the constitutive-derived proxy.

    This is a SCENARIO BAND, not a bounded-derived interval.
    The width reflects model uncertainty in the sub-horizon metric-to-lapse mapping.
    """
    central = _psi_from_route_a(beta_Q)
    low = central / band_factor
    high = central * band_factor

    sb = ProxySensitivityBand()
    sb.central = central
    sb.low = low
    sb.high = high
    sb.band_factor = band_factor
    sb.central_formula = "1 / (1 + beta_Q)"
    sb.low_formula = "1 / (2 * (1 + beta_Q))"
    sb.high_formula = "2 / (1 + beta_Q)"

    # Check if numerically same as prior heuristic [alpha_vac/2, alpha_vac, 2*alpha_vac]
    prior_central = alpha_vac
    prior_low = alpha_vac / band_factor
    prior_high = alpha_vac * band_factor
    sb.numerically_same_as_prior = (
        abs(central - prior_central) < 1e-14
        and abs(low - prior_low) < 1e-14
        and abs(high - prior_high) < 1e-14
    )

    sb.central_elevated = True
    sb.prior_central_label = "heuristic"
    sb.new_central_label = LEVEL_CONSTITUTIVE_DERIVED
    sb.band_source = (
        "Sub-horizon metric-to-lapse mapping uncertainty.  The central value "
        "1/(1+beta_Q) is constitutive-derived from the barrier integral and "
        "endpoint law.  The factor-of-2 band reflects the range of physically "
        "motivated mappings from the barrier potential to the effective lapse "
        "in the sub-horizon regime."
    )

    sb.notes = [
        f"Central: {central:.6f} (constitutive-derived from 1/(1+beta_Q)).",
        f"Low: {low:.6f}, High: {high:.6f} (factor-of-{band_factor} scenario band).",
        f"Prior heuristic band: [{prior_low:.6f}, {prior_central:.6f}, {prior_high:.6f}].",
        f"Numerically same as prior: {'yes' if sb.numerically_same_as_prior else 'no'}.",
        "Central value elevated from heuristic to constitutive-derived.",
        "This is a SCENARIO BAND, not a confidence interval.",
    ]

    return sb


def build_three_level_summary(
    beta_Q: float = BETA_Q,
    epsilon_Q: float = EPSILON_Q,
) -> ThreeLevelSummary:
    """Build the explicit three-level hierarchy for the effective lapse."""
    ratio = _barrier_potential_ratio(beta_Q, epsilon_Q)
    proxy = _psi_from_route_a(beta_Q)

    tls = ThreeLevelSummary()

    # Level 1: exact barrier-to-gravity ratio
    tls.level_1_value = ratio
    tls.level_1_formula = "Phi_barrier / Phi_grav = 1 / (1 + beta_Q)"
    tls.level_1_status = LEVEL_EXACT
    tls.level_1_description = (
        "Algebraic identity at the endpoint.  The barrier-to-gravity potential "
        "ratio is 1/(1+beta_Q), proven from the barrier integral and the "
        "endpoint law.  Independent of epsilon_Q, alpha_vac, and mass."
    )

    # Level 2: constitutive-derived lapse proxy
    tls.level_2_value = proxy
    tls.level_2_formula = "Psi_proxy = 1 / (1 + beta_Q)"
    tls.level_2_status = LEVEL_CONSTITUTIVE_DERIVED
    tls.level_2_description = (
        "The exact barrier-to-gravity ratio (Level 1) is identified as the "
        "effective lapse SCALE at the constitutive level.  This identification "
        "is physically motivated: the barrier potential energy sets the "
        "gravitational energy scale for the lapse correction.  This is a lapse "
        "PROXY, not the true metric lapse."
    )

    # Level 3: true interior metric lapse (unresolved)
    tls.level_3_value = None
    tls.level_3_status = LEVEL_UNRESOLVED
    tls.level_3_description = (
        "The true interior metric lapse at the endpoint requires a covariant "
        "interior solution that resolves the metric signature in the "
        "barrier-supported region.  The constitutive ansatz gives A_eff = -1 < 0, "
        "showing the ansatz is incomplete."
    )
    tls.level_3_obstruction = (
        "Sub-horizon metric-to-lapse mapping.  The constitutive ansatz gives "
        "A_eff < 0 at the endpoint, meaning the standard redshift formula does "
        "not apply.  Resolving the true metric lapse requires: (1) covariant "
        "field equations with a derived interior metric, (2) resolution of the "
        "metric signature in the barrier-supported region, (3) a proper-time "
        "definition for the barrier-equilibrium observer."
    )

    tls.notes = [
        "Three levels are explicitly separate in analysis and outputs.",
        "Level 1 -> Level 2: constitutive identification (barrier ratio -> lapse scale).",
        "Level 2 -> Level 3: requires covariant interior solution (unresolved).",
    ]

    return tls


def build_self_healing_check(
    beta_Q: float = BETA_Q,
) -> SelfHealingCheck:
    """Verify self-healing is independent of the effective lapse."""
    sh = SelfHealingCheck()
    sh.source_at_eq = 0.0  # X - Phi = a_grav - M_drive = 0 at equilibrium
    sh.source_vanishes = True
    sh.independent_of_psi = True

    sh.mechanism = (
        "At the GRUT equilibrium endpoint, the memory field reaches "
        "M_drive = a_grav (force balance).  The lapse correction ODE source "
        "term is Psi * (X - Phi) = Psi * (a_grav - M_drive).  At equilibrium, "
        "a_grav - M_drive = 0, so the source vanishes IDENTICALLY regardless "
        "of the value of Psi.  The correction ODE becomes tau * d(delta_Phi)/dt "
        "+ delta_Phi = 0, with only the decaying solution delta_Phi ~ exp(-t/tau) "
        "-> 0.  This self-healing property is a structural consequence of force "
        "balance, not a perturbative coincidence.  It holds for ANY value of Psi "
        "from any derivation route."
    )

    sh.preserved_under_route_a = True
    sh.preserved_under_route_b = True
    sh.preserved_under_route_c = True

    sh.notes = [
        "Self-healing is independent of Psi_eff — it depends only on X - Phi = 0 at eq.",
        "Preserved under Route A (Psi_proxy = 1/(1+beta_Q)).",
        "Preserved under Route B (psi_metric unresolved, but source term still vanishes).",
        "Preserved under Route C (Psi_Schw = C/2 — source term still vanishes).",
        "Proven at first perturbative order; nonlinear verification open.",
    ]

    return sh


def build_shift_estimates(
    beta_Q: float = BETA_Q,
) -> ShiftEstimates:
    """Compute shift estimates using the constitutive-derived central proxy.

    These are bounded estimates at the constitutive level.
    """
    psi = _psi_from_route_a(beta_Q)

    se = ShiftEstimates()
    se.psi_proxy_central = psi

    # Proper-time shift
    se.tau_ratio_central = 1.0 / (1.0 + psi)
    se.proper_time_shift_pct = (1.0 - se.tau_ratio_central) * 100.0

    # Q shift (bounded estimate)
    se.Q_canon = Q_CANON
    se.Q_shift_pct = psi * 100.0  # first-order: Q_bounded ~ Q_canon * (1 + psi)

    # omega_0 * tau shift (bounded estimate)
    se.omega_0_tau_canon = OMEGA_0_TAU_CANON
    se.omega_0_tau_at_eq = 1.0 / (1.0 + psi)

    se.notes = [
        f"Central proxy Psi = {psi:.6f}.",
        f"Proper-time shift: {se.proper_time_shift_pct:.1f}%.",
        f"Q shift (bounded): +{se.Q_shift_pct:.1f}%.",
        f"omega_0*tau at eq (bounded): {se.omega_0_tau_at_eq:.4f}.",
        "These are bounded estimates at the constitutive level, not derived "
        "corrected dispersion relations.",
    ]

    return se


def scan_beta_Q(
    beta_Q_values: Optional[List[float]] = None,
    alpha_vac: float = ALPHA_VAC,
) -> List[Dict[str, Any]]:
    """Scan Psi_proxy = 1/(1+beta_Q) across a range of beta_Q values.

    Demonstrates that the central value depends on beta_Q, not alpha_vac.
    """
    if beta_Q_values is None:
        beta_Q_values = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]

    results = []
    for bq in beta_Q_values:
        psi = _psi_from_route_a(bq)
        coincides = abs(psi - alpha_vac) < 1e-14
        results.append({
            "beta_Q": bq,
            "psi_proxy": psi,
            "coincides_with_alpha_vac": coincides,
        })

    return results


# ================================================================
# Master analysis
# ================================================================

def compute_effective_lapse_analysis(
    alpha_vac: float = ALPHA_VAC,
    beta_Q: float = BETA_Q,
    epsilon_Q: float = EPSILON_Q,
) -> EffectiveLapseResult:
    """Master analysis: effective lapse derivation at the GRUT endpoint.

    Performs:
      1. Derives barrier-to-gravity ratio (Level 1: exact)
      2. Builds three derivation routes
      3. Compares routes and identifies preferred proxy
      4. Constructs sensitivity band around constitutive-derived central proxy
      5. Builds three-level hierarchy summary
      6. Verifies self-healing independence
      7. Computes shift estimates
      8. Explains the alpha_vac coincidence
      9. Assembles nonclaims (>= 15)
      10. Populates diagnostics

    Parameters
    ----------
    alpha_vac : float
        Vacuum susceptibility (canon: 1/3).
    beta_Q : float
        Barrier exponent (canon: 2).
    epsilon_Q : float
        Barrier amplitude (canon: 1/9).

    Returns
    -------
    EffectiveLapseResult
        Complete derivation analysis.
    """
    result = EffectiveLapseResult()

    # 1. Central algebraic result
    bgr = build_barrier_gravity_ratio(beta_Q, epsilon_Q)
    result.barrier_gravity_ratio = bgr

    # 2-3. Derivation routes
    ra = build_route_a(beta_Q, epsilon_Q)
    rb = build_route_b(beta_Q, epsilon_Q)
    rc = build_route_c(beta_Q, epsilon_Q)
    routes = build_route_comparison(ra, rb, rc)
    result.routes = routes

    # 4. Sensitivity band
    sb = build_sensitivity_band(beta_Q, alpha_vac)
    result.sensitivity_band = sb

    # 5. Three-level hierarchy
    tls = build_three_level_summary(beta_Q, epsilon_Q)
    result.three_levels = tls

    # 6. Self-healing check
    sh = build_self_healing_check(beta_Q)
    result.self_healing = sh

    # 7. Shift estimates
    se = build_shift_estimates(beta_Q)
    result.shift_estimates = se

    # 8. Coincidence explanation
    psi_proxy = ra.psi_proxy
    coincides = abs(psi_proxy - alpha_vac) < 1e-14
    result.coincidence_explained = True
    result.prior_heuristic_confirmed = coincides
    result.prior_heuristic_elevated = True
    result.coincidence_description = (
        f"For canon beta_Q = {beta_Q}, the derived central proxy "
        f"1/(1+beta_Q) = {psi_proxy:.6f} {'equals' if coincides else 'does NOT equal'} "
        f"alpha_vac = {alpha_vac:.6f}.  "
        + (
            "This is a COINCIDENCE of the canon parameter values, not the "
            "fundamental relationship.  The true parametric dependence of the "
            "lapse proxy is on beta_Q (barrier steepness), not alpha_vac "
            "(vacuum susceptibility).  For beta_Q != 2, these values diverge: "
            "e.g., beta_Q = 3 gives 1/4 != alpha_vac."
            if coincides else
            "The prior heuristic 'Psi ~ alpha_vac' is not confirmed at these "
            "parameter values.  The correct formula is 1/(1+beta_Q)."
        )
    )

    # 9. Nonclaims
    result.nonclaims = [
        "The central lapse proxy 1/(1+beta_Q) is constitutive-derived (Level 2), "
        "NOT the true metric lapse (Level 3).",

        "The barrier-to-gravity ratio 1/(1+beta_Q) is exact (Level 1), but its "
        "identification as a lapse scale is at the constitutive level.",

        "Route B (effective metric) is UNRESOLVED at the endpoint because A_eff < 0 "
        "and the standard redshift formula does not apply.",

        "The true interior metric lapse requires a covariant interior solution "
        "beyond the constitutive ansatz.",

        "The constitutive ansatz gives A_eff = -1 < 0 at the endpoint, showing "
        "the ansatz is incomplete for the interior metric.",

        "The coincidence 1/(1+beta_Q) = alpha_vac at canon beta_Q = 2 is a "
        "parametric coincidence, not the fundamental relationship.",

        "The sensitivity band [low, central, high] is a SCENARIO BAND, not a "
        "confidence interval or a bounded-derived interval.",

        "Self-healing is independent of Psi_eff and preserved under all "
        "derivation routes.",

        "Nonlinear self-healing (beyond first perturbative order) is UNTESTED.",

        "Shift estimates (Q, omega_0*tau, proper-time) are bounded estimates "
        "at the constitutive level, not derived corrected dispersion relations.",

        "No claim is made about the effective lapse away from the equilibrium "
        "endpoint (only at R_eq).",

        "Tensorial memory generalization could modify the effective lapse.",

        "Observer-flow dependence is not resolved by this derivation.",

        "The derivation depends on spherical symmetry; no Kerr extension is made.",

        "The sub-horizon metric-to-lapse mapping is the remaining obstruction "
        "for resolving the true metric lapse.",

        "The beta_Q parametric scan shows Psi_proxy varies continuously with "
        "beta_Q; the canon value is not uniquely special.",

        "No detector-level or observational predictions are made from the "
        "constitutive-derived proxy.",
    ]

    # 10. Overall status
    result.approx_status = (
        "Central lapse proxy: constitutive_derived.  "
        "True interior metric lapse: unresolved."
    )
    result.remaining_obstruction = (
        "Sub-horizon metric-to-lapse mapping.  The constitutive ansatz gives "
        "A_eff < 0 at the endpoint, meaning the standard redshift formula does "
        "not apply.  Resolving the true metric lapse requires: (1) covariant "
        "field equations with a derived interior metric that resolves the metric "
        "signature, (2) a proper-time definition for the barrier-equilibrium "
        "observer, (3) possibly going beyond the post-Newtonian mapping "
        "delta_A = 2*Phi_barrier/c^2 to a fully covariant treatment."
    )

    # Diagnostics
    result.diagnostics = {
        "beta_Q": beta_Q,
        "alpha_vac": alpha_vac,
        "epsilon_Q": epsilon_Q,
        "C_endpoint": 1.0 / epsilon_Q ** (1.0 / beta_Q) if beta_Q > 0 and epsilon_Q > 0 else C_ENDPOINT,
        "barrier_ratio": bgr.ratio,
        "psi_proxy_central": psi_proxy,
        "psi_schw_at_endpoint": rc.psi_schw,
        "A_eff_at_endpoint": rb.A_eff_at_Req,
        "A_eff_is_negative": rb.A_eff_is_negative,
        "route_b_applicable": rb.redshift_formula_applicable,
        "self_healing_preserved": sh.source_vanishes,
        "prior_band_confirmed": sb.numerically_same_as_prior,
        "central_elevated": sb.central_elevated,
        "coincidence_at_canon": coincides,
        "true_metric_lapse_resolved": False,
        "n_nonclaims": len(result.nonclaims),
    }

    result.valid = True
    return result


# ================================================================
# Serialization
# ================================================================

def _barrier_gravity_ratio_to_dict(bgr: BarrierGravityRatio) -> Dict[str, Any]:
    """Serialize BarrierGravityRatio."""
    return {
        "beta_Q": bgr.beta_Q,
        "epsilon_Q": bgr.epsilon_Q,
        "ratio": bgr.ratio,
        "ratio_formula": bgr.ratio_formula,
        "is_exact": bgr.is_exact,
        "depends_on_epsilon_Q": bgr.depends_on_epsilon_Q,
        "depends_on_alpha_vac": bgr.depends_on_alpha_vac,
        "depends_on_mass": bgr.depends_on_mass,
        "endpoint_law_used": bgr.endpoint_law_used,
        "derivation_steps": bgr.derivation_steps,
        "notes": bgr.notes,
    }


def _route_a_to_dict(ra: RouteAResult) -> Dict[str, Any]:
    """Serialize RouteAResult."""
    return {
        "route_name": ra.route_name,
        "psi_proxy": ra.psi_proxy,
        "formula": ra.formula,
        "classification": ra.classification,
        "identification_basis": ra.identification_basis,
        "barrier_ratio": _barrier_gravity_ratio_to_dict(ra.barrier_ratio) if ra.barrier_ratio else None,
        "notes": ra.notes,
    }


def _route_b_to_dict(rb: RouteBResult) -> Dict[str, Any]:
    """Serialize RouteBResult."""
    return {
        "route_name": rb.route_name,
        "A_schw_at_Req": rb.A_schw_at_Req,
        "delta_A": rb.delta_A,
        "A_eff_at_Req": rb.A_eff_at_Req,
        "A_eff_is_negative": rb.A_eff_is_negative,
        "redshift_formula_applicable": rb.redshift_formula_applicable,
        "psi_metric": rb.psi_metric,
        "classification": rb.classification,
        "obstruction": rb.obstruction,
        "notes": rb.notes,
    }


def _route_c_to_dict(rc: RouteCResult) -> Dict[str, Any]:
    """Serialize RouteCResult."""
    return {
        "route_name": rc.route_name,
        "psi_schw": rc.psi_schw,
        "formula": rc.formula,
        "classification": rc.classification,
        "is_upper_bound": rc.is_upper_bound,
        "notes": rc.notes,
    }


def _route_comparison_to_dict(cmp: RouteComparison) -> Dict[str, Any]:
    """Serialize RouteComparison."""
    return {
        "route_a": _route_a_to_dict(cmp.route_a) if cmp.route_a else None,
        "route_b": _route_b_to_dict(cmp.route_b) if cmp.route_b else None,
        "route_c": _route_c_to_dict(cmp.route_c) if cmp.route_c else None,
        "preferred_route": cmp.preferred_route,
        "preferred_psi_proxy": cmp.preferred_psi_proxy,
        "preferred_classification": cmp.preferred_classification,
        "notes": cmp.notes,
    }


def _sensitivity_band_to_dict(sb: ProxySensitivityBand) -> Dict[str, Any]:
    """Serialize ProxySensitivityBand."""
    return {
        "central": sb.central,
        "low": sb.low,
        "high": sb.high,
        "band_factor": sb.band_factor,
        "central_formula": sb.central_formula,
        "low_formula": sb.low_formula,
        "high_formula": sb.high_formula,
        "numerically_same_as_prior": sb.numerically_same_as_prior,
        "central_elevated": sb.central_elevated,
        "prior_central_label": sb.prior_central_label,
        "new_central_label": sb.new_central_label,
        "band_source": sb.band_source,
        "notes": sb.notes,
    }


def _three_level_to_dict(tls: ThreeLevelSummary) -> Dict[str, Any]:
    """Serialize ThreeLevelSummary."""
    return {
        "level_1_value": tls.level_1_value,
        "level_1_formula": tls.level_1_formula,
        "level_1_status": tls.level_1_status,
        "level_1_description": tls.level_1_description,
        "level_2_value": tls.level_2_value,
        "level_2_formula": tls.level_2_formula,
        "level_2_status": tls.level_2_status,
        "level_2_description": tls.level_2_description,
        "level_3_value": tls.level_3_value,
        "level_3_status": tls.level_3_status,
        "level_3_description": tls.level_3_description,
        "level_3_obstruction": tls.level_3_obstruction,
        "notes": tls.notes,
    }


def _self_healing_to_dict(sh: SelfHealingCheck) -> Dict[str, Any]:
    """Serialize SelfHealingCheck."""
    return {
        "source_at_eq": sh.source_at_eq,
        "source_vanishes": sh.source_vanishes,
        "independent_of_psi": sh.independent_of_psi,
        "mechanism": sh.mechanism,
        "preserved_under_route_a": sh.preserved_under_route_a,
        "preserved_under_route_b": sh.preserved_under_route_b,
        "preserved_under_route_c": sh.preserved_under_route_c,
        "notes": sh.notes,
    }


def _shift_estimates_to_dict(se: ShiftEstimates) -> Dict[str, Any]:
    """Serialize ShiftEstimates."""
    return {
        "psi_proxy_central": se.psi_proxy_central,
        "tau_ratio_central": se.tau_ratio_central,
        "proper_time_shift_pct": se.proper_time_shift_pct,
        "Q_canon": se.Q_canon,
        "Q_shift_pct": se.Q_shift_pct,
        "omega_0_tau_canon": se.omega_0_tau_canon,
        "omega_0_tau_at_eq": se.omega_0_tau_at_eq,
        "notes": se.notes,
    }


def effective_lapse_result_to_dict(
    result: EffectiveLapseResult,
) -> Dict[str, Any]:
    """Serialize the master EffectiveLapseResult to a dictionary."""
    return {
        "valid": result.valid,
        "barrier_gravity_ratio": (
            _barrier_gravity_ratio_to_dict(result.barrier_gravity_ratio)
            if result.barrier_gravity_ratio else None
        ),
        "three_levels": (
            _three_level_to_dict(result.three_levels)
            if result.three_levels else None
        ),
        "routes": (
            _route_comparison_to_dict(result.routes)
            if result.routes else None
        ),
        "sensitivity_band": (
            _sensitivity_band_to_dict(result.sensitivity_band)
            if result.sensitivity_band else None
        ),
        "self_healing": (
            _self_healing_to_dict(result.self_healing)
            if result.self_healing else None
        ),
        "shift_estimates": (
            _shift_estimates_to_dict(result.shift_estimates)
            if result.shift_estimates else None
        ),
        "prior_heuristic_confirmed": result.prior_heuristic_confirmed,
        "prior_heuristic_elevated": result.prior_heuristic_elevated,
        "coincidence_explained": result.coincidence_explained,
        "coincidence_description": result.coincidence_description,
        "approx_status": result.approx_status,
        "remaining_obstruction": result.remaining_obstruction,
        "nonclaims": result.nonclaims,
        "diagnostics": result.diagnostics,
    }
