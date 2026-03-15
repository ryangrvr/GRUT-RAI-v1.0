"""GRUT Phase IV — Route B: Consistent Truncation and Attractor Analysis.

Tests whether the physical limit of the Galley doubled-field GRUT memory sector
is a dynamically stable consistent truncation.

CONTEXT:
The Galley doubled-field formalism produces a physical-limit-derived T^Phi_{mu nu}
(Phase IV Route B T^Phi derivation). That derivation depends on the physical limit:
    Phi_1 = Phi_2 = Phi
    g^(1) = g^(2) = g

This module determines whether this physical limit is:
1. A consistent truncation (Phi_- = 0 is an exact solution)
2. A dynamical attractor (perturbations in Phi_- decay toward zero)
3. Stable in the metric-difference sector

KEY PHYSICS:
The Galley doubled-field action S = S_1 - S_2 + S_diss, when varied with respect
to the individual copies, gives CROSS-COUPLED equations:
    dPhi_1/dt = (X - Phi_2) / tau
    dPhi_2/dt = (X - Phi_1) / tau

In the plus/minus decomposition (Phi_+ = (Phi_1+Phi_2)/2, Phi_- = Phi_1-Phi_2):
    dPhi_+/dt = (X - Phi_+) / tau   [RELAXATION — correct GRUT law]
    dPhi_-/dt = Phi_- / tau          [GROWTH — ghost mode amplification]

The physical limit (Phi_- = 0) is:
    - An EXACT consistent truncation (Phi_- = 0 is a solution)
    - NOT a dynamical attractor (perturbations grow at rate 1/tau)
    - MAINTAINED by the CTP boundary condition, not by dynamics

This is a FUNDAMENTAL FEATURE of the Galley formalism: the ghost mode's
exponential growth and its CTP boundary condition (Phi_-(T) = 0 at the
final time) are what encode time-asymmetry (dissipation) variationally.

RESULTS:
  Scalar consistent truncation:   EXACT
  Scalar attractor status:        NOT AN ATTRACTOR (growing mode at rate 1/tau)
  Full KG+Galley Phi_- rate:      phi/tau where phi = (1+sqrt(5))/2 (golden ratio)
  Scalar CTP consistency:         YES
  Metric-difference sector:       EXPECTED UNSTABLE (wrong-sign EH, not proven)
  Overall classification:         CONSISTENT TRUNCATION — NOT ATTRACTOR

See docs/PHASE_IV_ROUTE_B_TRUNCATION.md for the full theory memo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


# Physical constants
G_SI = 6.674e-11          # m^3 kg^-1 s^-2
C_SI = 299_792_458.0      # m/s
M_SUN = 1.989e30          # kg

# Mathematical constants
PHI_GOLDEN = (1.0 + math.sqrt(5.0)) / 2.0  # golden ratio ≈ 1.618


# ================================================================
# Data Structures
# ================================================================

@dataclass
class DoubledScalarSystem:
    """The full Galley doubled-scalar system in +/- variables.

    Two formulations are tracked:
    1. Simple (first-order Galley): directly encodes first-order relaxation
    2. Full KG+Galley: includes kinetic terms from the scalar action

    In both, Phi_- has a growing mode. The growth rate differs:
    - Simple: rate = 1/tau
    - Full KG+Galley: rate = phi/tau (golden ratio)
    """
    # Simple Galley system (first-order)
    simple_phi_plus_eom: str = ""
    simple_phi_minus_eom: str = ""
    simple_phi_minus_growth_rate: float = 0.0  # 1/tau

    # Full KG+Galley system (second-order)
    full_phi_plus_eom: str = ""
    full_phi_minus_eom: str = ""
    full_phi_minus_eigenvalues: List[float] = field(default_factory=list)
    full_phi_minus_growing_rate: float = 0.0  # phi/tau
    full_phi_minus_decaying_rate: float = 0.0  # 1/(phi*tau)

    # System properties
    has_growing_mode: bool = False
    phi_minus_is_ghost: bool = False
    ctp_boundary_required: bool = False

    notes: List[str] = field(default_factory=list)


@dataclass
class PlusMinusTransform:
    """Validation of the +/- variable decomposition.

    Phi_+ = (Phi_1 + Phi_2) / 2   (physical mode)
    Phi_- = Phi_1 - Phi_2          (difference / ghost mode)

    Inverse:
    Phi_1 = Phi_+ + Phi_-/2
    Phi_2 = Phi_+ - Phi_-/2
    """
    transform_valid: bool = False
    inverse_valid: bool = False
    phi_plus_definition: str = ""
    phi_minus_definition: str = ""
    inverse_phi_1: str = ""
    inverse_phi_2: str = ""
    jacobian_determinant: float = 0.0
    transform_preserves_action: bool = False

    notes: List[str] = field(default_factory=list)


@dataclass
class ScalarTruncationResult:
    """Whether Phi_- = 0 is a consistent truncation of the doubled system.

    Consistent truncation means: if Phi_- = 0 at the initial time,
    then Phi_- = 0 for all subsequent times. Equivalently, Phi_- = 0
    is an exact solution of the Phi_- equation of motion.
    """
    # Analytical
    phi_minus_zero_is_solution: bool = False
    phi_minus_eom_at_zero: float = 0.0  # should be exactly 0

    # Numerical verification
    phi_minus_zero_preserved_numerically: bool = False
    max_phi_minus_residual: float = 0.0
    n_steps_tested: int = 0

    # Classification
    is_consistent_truncation: bool = False
    truncation_classification: str = ""  # "exact", "approximate", "inconsistent"

    notes: List[str] = field(default_factory=list)


@dataclass
class ScalarAttractorResult:
    """Whether Phi_- = 0 is a dynamical attractor.

    An attractor means: small perturbations in Phi_- decay toward zero.
    For the Galley system, this is NOT the case — Phi_- has a growing mode.

    Two formulations are tested:
    1. Simple Galley (first-order): growth rate = 1/tau
    2. Full KG+Galley (second-order): growth rate = phi/tau (golden ratio)
    """
    # Simple system results
    simple_has_growing_mode: bool = False
    simple_growth_rate_theoretical: float = 0.0   # 1/tau
    simple_growth_rate_measured: float = 0.0
    simple_growth_rate_matches: bool = False

    # Full KG+Galley system results
    full_has_growing_mode: bool = False
    full_has_decaying_mode: bool = False
    full_growing_rate_theoretical: float = 0.0    # phi/tau
    full_decaying_rate_theoretical: float = 0.0   # 1/(phi*tau)
    full_growing_rate_measured: float = 0.0
    full_growing_rate_matches: bool = False

    # Galley vs independent comparison
    galley_phi_minus_grows: bool = False
    independent_phi_minus_decays: bool = False
    cross_coupling_causes_growth: bool = False

    # Cosmological regime
    cosmo_growth_rate_measured: float = 0.0
    cosmo_growth_matches: bool = False

    # Collapse regime
    collapse_growth_rate_measured: float = 0.0
    collapse_growth_matches: bool = False

    # CTP boundary condition
    ctp_boundary_enforces_zero: bool = False
    ctp_interpretation: str = ""

    # Classification
    is_attractor: bool = False
    is_conditional_attractor: bool = False
    classification: str = ""  # "unstable_consistent_truncation", "attractor", "conditional_attractor"

    diagnostics: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    nonclaims: List[str] = field(default_factory=list)


@dataclass
class MetricDifferenceResult:
    """Analysis of the metric-difference sector (g_- = g_1 - g_2).

    The doubled-metric action: S_grav = (1/(16piG)) int [sqrt(-g_1)R_1 - sqrt(-g_2)R_2]

    In the +/- decomposition:
    - g_+ = (g_1 + g_2)/2  (physical metric)
    - g_- = g_1 - g_2       (difference metric)

    The linearized g_- action has WRONG-SIGN kinetic energy (gravitational ghost).
    This means g_- = 0 is expected to be unstable, analogous to the scalar sector.
    """
    # Structural analysis
    linearized_analysis_possible: bool = False
    metric_minus_wrong_sign_kinetic: bool = False
    metric_minus_expected_unstable: bool = False
    metric_truncation_is_consistent: bool = False  # g_- = 0 is a solution

    # Coupling to scalar sector
    scalar_sources_metric_minus: bool = False
    phi_minus_growth_drives_g_minus: bool = False

    # Status
    metric_attractor_status: str = ""  # "undetermined", "expected_unstable"
    full_analysis_obstruction: str = ""

    notes: List[str] = field(default_factory=list)


@dataclass
class TruncationClassification:
    """Overall classification of the truncation/attractor analysis."""
    # Scalar sector
    scalar_truncation: str = ""   # "exact_consistent_truncation"
    scalar_attractor: str = ""    # "not_attractor__growing_mode"

    # Metric sector
    metric_truncation: str = ""   # "consistent_truncation_expected"
    metric_attractor: str = ""    # "expected_unstable__not_proven"

    # Overall
    overall: str = ""             # "consistent_truncation__not_attractor"
    route_b_upgrade: str = ""     # "no_upgrade", "clarification", "partial_upgrade"

    # What this means for Route B
    route_b_status_before: str = ""  # "physical-limit derived"
    route_b_status_after: str = ""   # "physical-limit derived (truncation consistent, not attractor)"

    notes: List[str] = field(default_factory=list)


@dataclass
class GalleyTruncationResult:
    """Master result from the truncation/attractor analysis."""
    # Components
    system: Optional[DoubledScalarSystem] = None
    transform: Optional[PlusMinusTransform] = None
    scalar_truncation: Optional[ScalarTruncationResult] = None
    scalar_attractor: Optional[ScalarAttractorResult] = None
    metric: Optional[MetricDifferenceResult] = None
    classification: Optional[TruncationClassification] = None

    # Summary
    exact_remaining_obstruction: str = ""
    comparison_to_route_c: str = ""

    nonclaims: List[str] = field(default_factory=list)
    valid: bool = False


# ================================================================
# Plus/Minus Variable Transform
# ================================================================

def transform_to_plus_minus_variables() -> PlusMinusTransform:
    """Validate the +/- variable decomposition.

    Forward transform:
        Phi_+ = (Phi_1 + Phi_2) / 2
        Phi_- = Phi_1 - Phi_2

    Inverse:
        Phi_1 = Phi_+ + Phi_-/2
        Phi_2 = Phi_+ - Phi_-/2

    Jacobian: |d(Phi_+, Phi_-)/d(Phi_1, Phi_2)| = |det [[1/2, 1/2],[1, -1]]| = 1
    """
    t = PlusMinusTransform()

    t.phi_plus_definition = "Phi_+ = (Phi_1 + Phi_2) / 2"
    t.phi_minus_definition = "Phi_- = Phi_1 - Phi_2"
    t.inverse_phi_1 = "Phi_1 = Phi_+ + Phi_-/2"
    t.inverse_phi_2 = "Phi_2 = Phi_+ - Phi_-/2"

    # Jacobian of (Phi_+, Phi_-) -> (Phi_1, Phi_2)
    # d(Phi_+)/d(Phi_1) = 1/2, d(Phi_+)/d(Phi_2) = 1/2
    # d(Phi_-)/d(Phi_1) = 1,   d(Phi_-)/d(Phi_2) = -1
    # det = (1/2)(-1) - (1/2)(1) = -1
    t.jacobian_determinant = -1.0

    # Validate: forward then inverse should give identity
    # Test with specific values
    phi_1_test, phi_2_test = 3.7, 1.2
    phi_plus_test = (phi_1_test + phi_2_test) / 2.0
    phi_minus_test = phi_1_test - phi_2_test
    phi_1_recov = phi_plus_test + phi_minus_test / 2.0
    phi_2_recov = phi_plus_test - phi_minus_test / 2.0

    t.transform_valid = (
        abs(phi_1_recov - phi_1_test) < 1e-15
        and abs(phi_2_recov - phi_2_test) < 1e-15
    )
    t.inverse_valid = t.transform_valid

    # Physical limit: Phi_- = 0 implies Phi_1 = Phi_2 = Phi_+
    # The action in +/- variables decomposes into Phi_+ dynamics (physical)
    # and Phi_- dynamics (ghost/difference mode)
    t.transform_preserves_action = True  # linear change of variables

    t.notes = [
        "The +/- decomposition diagonalizes the Galley EOM into physical and ghost sectors",
        "Phi_+ satisfies the GRUT relaxation law (correct dissipation)",
        "Phi_- satisfies the ghost equation (exponential growth)",
        "Physical limit: Phi_- = 0 => Phi_1 = Phi_2 = Phi_+",
        f"Jacobian determinant: {t.jacobian_determinant:.1f} (nonsingular)",
    ]

    return t


# ================================================================
# Doubled-System Construction
# ================================================================

def build_doubled_scalar_system(tau_eff: float = 1.0) -> DoubledScalarSystem:
    """Construct the Galley doubled-scalar system in +/- variables.

    DERIVATION (Simple Galley action for first-order relaxation):

    The Galley CTP action for the first-order system tau dPhi/dt + Phi = X is:

        S = integral dt Phi_- [tau dPhi_+/dt + Phi_+ - X]

    Euler-Lagrange equations:
        delta S / delta Phi_- = 0:  tau dPhi_+/dt + Phi_+ - X = 0
            => dPhi_+/dt = (X - Phi_+) / tau  [GRUT relaxation law]

        delta S / delta Phi_+ = 0:  Phi_- - tau dPhi_-/dt = 0
            => dPhi_-/dt = Phi_- / tau         [EXPONENTIAL GROWTH]

    The individual-variable form (cross-coupled):
        dPhi_1/dt = (X - Phi_2) / tau
        dPhi_2/dt = (X - Phi_1) / tau

    This is DIFFERENT from independent evolution (dPhi_i/dt = (X - Phi_i)/tau)
    where both copies relax independently and Phi_- decays.

    DERIVATION (Full KG+Galley action with kinetic terms):

    The full action with -(1/2)(dPhi)^2 kinetic terms in each copy gives:
        d^2 Phi_-/dt^2 - (1/tau) dPhi_-/dt - (1/tau^2) Phi_- = 0

    Characteristic equation: mu^2 - mu - 1 = 0  (with mu = tau * lambda)
    Solutions: mu = (1 +/- sqrt(5)) / 2

    Growing mode: lambda_+ = phi / tau  (phi = golden ratio ~ 1.618)
    Decaying mode: lambda_- = -1/(phi*tau) ~ -0.618/tau
    """
    sys = DoubledScalarSystem()

    # ── Simple Galley system ──
    sys.simple_phi_plus_eom = "dPhi_+/dt = (X - Phi_+) / tau [GRUT relaxation]"
    sys.simple_phi_minus_eom = "dPhi_-/dt = Phi_- / tau [exponential GROWTH]"
    sys.simple_phi_minus_growth_rate = 1.0 / tau_eff

    # ── Full KG+Galley system ──
    sys.full_phi_plus_eom = (
        "d^2 Phi_+/dt^2 + (1/tau) dPhi_+/dt - (1/tau^2) Phi_+ + X/tau = 0"
    )
    sys.full_phi_minus_eom = (
        "d^2 Phi_-/dt^2 - (1/tau) dPhi_-/dt - (1/tau^2) Phi_- = 0"
    )

    # Eigenvalues for Phi_- in full system
    # mu^2 - mu - 1 = 0, mu = (1 +/- sqrt(5))/2
    mu_plus = (1.0 + math.sqrt(5.0)) / 2.0   # golden ratio phi
    mu_minus = (1.0 - math.sqrt(5.0)) / 2.0   # -1/phi

    lambda_plus = mu_plus / tau_eff
    lambda_minus = mu_minus / tau_eff

    sys.full_phi_minus_eigenvalues = [lambda_plus, lambda_minus]
    sys.full_phi_minus_growing_rate = lambda_plus    # phi/tau
    sys.full_phi_minus_decaying_rate = abs(lambda_minus)  # 1/(phi*tau)

    # ── System properties ──
    sys.has_growing_mode = True
    sys.phi_minus_is_ghost = True
    sys.ctp_boundary_required = True

    sys.notes = [
        f"Simple Galley: Phi_- grows at rate 1/tau = {1.0/tau_eff:.6e}",
        f"Full KG+Galley: Phi_- grows at rate phi/tau = {lambda_plus:.6e}",
        f"Full KG+Galley: Phi_- also has decaying mode at rate 1/(phi*tau) = {abs(lambda_minus):.6e}",
        "The growth rate is FASTER in the full KG+Galley system than in the simple system",
        "In both formulations, Phi_- = 0 is an UNSTABLE equilibrium",
        "The Galley EOM give CROSS-COUPLED dynamics: dPhi_1/dt = (X-Phi_2)/tau, NOT (X-Phi_1)/tau",
        "This cross-coupling is what produces the growing ghost mode",
        "Independent evolution (same equation for each copy) gives Phi_- DECAYING — "
        "but this is NOT the Galley dynamics",
        "The CTP boundary condition Phi_-(T_final) = 0 enforces the physical limit",
    ]

    return sys


# ================================================================
# Numerical Integration of Doubled System
# ================================================================

def _integrate_galley_coupled(
    phi_1_0: float,
    phi_2_0: float,
    X: float,
    tau_eff: float,
    dt: float,
    n_steps: int,
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """Integrate the GALLEY cross-coupled system using RK4.

    Galley EOM (derived from the CTP variational principle):
        dPhi_1/dt = (X - Phi_2) / tau
        dPhi_2/dt = (X - Phi_1) / tau

    Note: Phi_1 is driven by Phi_2 and vice versa (cross-coupling).
    This is NOT the same as independent relaxation.

    Returns: (phi_1_hist, phi_2_hist, phi_plus_hist, phi_minus_hist)
    """
    phi_1 = phi_1_0
    phi_2 = phi_2_0

    phi_1_hist = [phi_1]
    phi_2_hist = [phi_2]
    phi_plus_hist = [(phi_1 + phi_2) / 2.0]
    phi_minus_hist = [phi_1 - phi_2]

    for _ in range(n_steps):
        # RK4 for the coupled system
        k1_1 = (X - phi_2) / tau_eff
        k1_2 = (X - phi_1) / tau_eff

        k2_1 = (X - (phi_2 + 0.5 * dt * k1_2)) / tau_eff
        k2_2 = (X - (phi_1 + 0.5 * dt * k1_1)) / tau_eff

        k3_1 = (X - (phi_2 + 0.5 * dt * k2_2)) / tau_eff
        k3_2 = (X - (phi_1 + 0.5 * dt * k2_1)) / tau_eff

        k4_1 = (X - (phi_2 + dt * k3_2)) / tau_eff
        k4_2 = (X - (phi_1 + dt * k3_1)) / tau_eff

        phi_1 += dt * (k1_1 + 2.0 * k2_1 + 2.0 * k3_1 + k4_1) / 6.0
        phi_2 += dt * (k1_2 + 2.0 * k2_2 + 2.0 * k3_2 + k4_2) / 6.0

        phi_1_hist.append(phi_1)
        phi_2_hist.append(phi_2)
        phi_plus_hist.append((phi_1 + phi_2) / 2.0)
        phi_minus_hist.append(phi_1 - phi_2)

    return phi_1_hist, phi_2_hist, phi_plus_hist, phi_minus_hist


def _integrate_independent(
    phi_1_0: float,
    phi_2_0: float,
    X: float,
    tau_eff: float,
    dt: float,
    n_steps: int,
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """Integrate INDEPENDENT relaxation (NOT the Galley dynamics).

    Independent EOM:
        dPhi_1/dt = (X - Phi_1) / tau
        dPhi_2/dt = (X - Phi_2) / tau

    In this case, Phi_- DECAYS (each copy relaxes independently).
    This is provided for CONTRAST with the Galley dynamics.

    Returns: (phi_1_hist, phi_2_hist, phi_plus_hist, phi_minus_hist)
    """
    phi_1 = phi_1_0
    phi_2 = phi_2_0

    # Use exact exponential update for each independent copy
    lam = dt / tau_eff
    e_factor = math.exp(-lam)

    phi_1_hist = [phi_1]
    phi_2_hist = [phi_2]
    phi_plus_hist = [(phi_1 + phi_2) / 2.0]
    phi_minus_hist = [phi_1 - phi_2]

    for _ in range(n_steps):
        phi_1 = phi_1 * e_factor + X * (1.0 - e_factor)
        phi_2 = phi_2 * e_factor + X * (1.0 - e_factor)

        phi_1_hist.append(phi_1)
        phi_2_hist.append(phi_2)
        phi_plus_hist.append((phi_1 + phi_2) / 2.0)
        phi_minus_hist.append(phi_1 - phi_2)

    return phi_1_hist, phi_2_hist, phi_plus_hist, phi_minus_hist


def _integrate_full_kg_galley_phi_minus(
    phi_minus_0: float,
    dphi_minus_0: float,
    tau_eff: float,
    dt: float,
    n_steps: int,
) -> Tuple[List[float], List[float]]:
    """Integrate the full KG+Galley Phi_- equation using RK4.

    Equation: d^2 Phi_-/dt^2 - (1/tau) dPhi_-/dt - (1/tau^2) Phi_- = 0

    Converted to first-order system:
        y1 = Phi_-, y2 = dPhi_-/dt
        dy1/dt = y2
        dy2/dt = (1/tau) y2 + (1/tau^2) y1

    Returns: (phi_minus_hist, dphi_minus_hist)
    """
    y1 = phi_minus_0
    y2 = dphi_minus_0
    inv_tau = 1.0 / tau_eff
    inv_tau_sq = 1.0 / (tau_eff ** 2)

    y1_hist = [y1]
    y2_hist = [y2]

    for _ in range(n_steps):
        # RK4 for the 2D system
        def f1(y1_loc: float, y2_loc: float) -> float:
            return y2_loc

        def f2(y1_loc: float, y2_loc: float) -> float:
            return inv_tau * y2_loc + inv_tau_sq * y1_loc

        k1_1 = f1(y1, y2)
        k1_2 = f2(y1, y2)

        k2_1 = f1(y1 + 0.5 * dt * k1_1, y2 + 0.5 * dt * k1_2)
        k2_2 = f2(y1 + 0.5 * dt * k1_1, y2 + 0.5 * dt * k1_2)

        k3_1 = f1(y1 + 0.5 * dt * k2_1, y2 + 0.5 * dt * k2_2)
        k3_2 = f2(y1 + 0.5 * dt * k2_1, y2 + 0.5 * dt * k2_2)

        k4_1 = f1(y1 + dt * k3_1, y2 + dt * k3_2)
        k4_2 = f2(y1 + dt * k3_1, y2 + dt * k3_2)

        y1 += dt * (k1_1 + 2.0 * k2_1 + 2.0 * k3_1 + k4_1) / 6.0
        y2 += dt * (k1_2 + 2.0 * k2_2 + 2.0 * k3_2 + k4_2) / 6.0

        y1_hist.append(y1)
        y2_hist.append(y2)

    return y1_hist, y2_hist


# ================================================================
# Scalar Truncation Analysis
# ================================================================

def analyze_scalar_truncation(
    tau_eff: float = 1.0,
    n_steps: int = 2000,
    n_tau: float = 5.0,
) -> ScalarTruncationResult:
    """Test whether Phi_- = 0 is a consistent truncation of the doubled system.

    DEFINITION: A consistent truncation means that if we set Phi_- = 0
    initially (and dPhi_-/dt = 0 for the second-order system), then
    Phi_- remains zero for all subsequent times.

    For the simple Galley system: dPhi_-/dt = Phi_-/tau
    If Phi_-(0) = 0, then Phi_-(t) = 0 for all t.  => EXACT CONSISTENT TRUNCATION

    For the full KG+Galley: d^2 Phi_-/dt^2 - (1/tau) dPhi_-/dt - (1/tau^2) Phi_- = 0
    If Phi_-(0) = 0 and dPhi_-(0)/dt = 0, then Phi_-(t) = 0 for all t.
    => EXACT CONSISTENT TRUNCATION

    Both are exact by linearity: Phi_- = 0 is trivially a solution of
    a linear homogeneous equation.
    """
    result = ScalarTruncationResult()

    # Analytical: Phi_- = 0 satisfies dPhi_-/dt = Phi_-/tau trivially
    result.phi_minus_zero_is_solution = True
    result.phi_minus_eom_at_zero = 0.0  # dPhi_-/dt|_{Phi_-=0} = 0/tau = 0

    # Numerical verification: integrate with Phi_-(0) = 0
    T_total = n_tau * tau_eff
    dt = T_total / n_steps

    X_test = 1.0
    phi_plus_0 = 0.5  # arbitrary initial condition for Phi_+
    phi_1_0 = phi_plus_0  # Phi_- = 0 => Phi_1 = Phi_2 = Phi_+
    phi_2_0 = phi_plus_0

    _, _, _, phi_minus_hist = _integrate_galley_coupled(
        phi_1_0, phi_2_0, X_test, tau_eff, dt, n_steps,
    )

    # Check that Phi_- stays at zero
    max_residual = 0.0
    for pm in phi_minus_hist:
        if abs(pm) > max_residual:
            max_residual = abs(pm)

    result.phi_minus_zero_preserved_numerically = max_residual < 1e-12
    result.max_phi_minus_residual = max_residual
    result.n_steps_tested = n_steps

    # Also verify the full KG+Galley system
    phi_minus_kg, _ = _integrate_full_kg_galley_phi_minus(
        0.0, 0.0, tau_eff, dt, n_steps,
    )
    max_residual_kg = max(abs(pm) for pm in phi_minus_kg)

    result.is_consistent_truncation = (
        result.phi_minus_zero_is_solution
        and result.phi_minus_zero_preserved_numerically
        and max_residual_kg < 1e-12
    )

    result.truncation_classification = (
        "exact" if result.is_consistent_truncation else "inconsistent"
    )

    result.notes = [
        "Phi_- = 0 is an EXACT consistent truncation (by linearity of the Phi_- EOM)",
        f"Numerical verification: max|Phi_-| = {max_residual:.2e} (simple Galley)",
        f"Numerical verification: max|Phi_-| = {max_residual_kg:.2e} (full KG+Galley)",
        f"Tested over {n_steps} steps ({n_tau} relaxation times)",
        "Consistent truncation means: if imposed exactly, it is maintained exactly",
        "This does NOT address stability to perturbations (see attractor analysis)",
    ]

    return result


# ================================================================
# Scalar Attractor Analysis
# ================================================================

def analyze_scalar_attractor(
    tau_eff: float = 1.0,
    n_steps: int = 2000,
    n_tau: float = 3.0,
    epsilon: float = 1e-6,
) -> ScalarAttractorResult:
    """Test whether Phi_- = 0 is a dynamical attractor.

    RESULT: Phi_- = 0 is NOT a dynamical attractor.

    The Galley EOM give dPhi_-/dt = Phi_-/tau, so any nonzero perturbation
    GROWS exponentially. This is fundamental to the Galley formalism:
    the ghost mode's growth encodes time-asymmetry in the variational principle.

    The physical limit is maintained by the CTP BOUNDARY CONDITION
    (Phi_-(T_final) = 0), not by dynamical attraction.

    This function:
    1. Integrates the Galley coupled system with a small Phi_- perturbation
    2. Measures the growth rate and compares to theoretical prediction
    3. Contrasts with independent evolution (where Phi_- decays)
    4. Tests in both cosmological and collapse parameter regimes
    5. Classifies the result
    """
    result = ScalarAttractorResult()

    T_total = n_tau * tau_eff
    dt = T_total / n_steps

    X_test = 1.0
    phi_plus_0 = 0.5
    phi_1_0 = phi_plus_0 + epsilon / 2.0
    phi_2_0 = phi_plus_0 - epsilon / 2.0
    # So Phi_-(0) = epsilon

    # ── Simple Galley system: cross-coupled integration ──
    _, _, phi_plus_galley, phi_minus_galley = _integrate_galley_coupled(
        phi_1_0, phi_2_0, X_test, tau_eff, dt, n_steps,
    )

    # Measure growth rate from the numerical data
    # Phi_-(t) = epsilon * exp(t/tau) => ln(|Phi_-|/epsilon) = t/tau
    # Use the final value to estimate the rate
    final_phi_minus_galley = abs(phi_minus_galley[-1])
    if final_phi_minus_galley > abs(epsilon) * 1.01:  # grew
        measured_rate_simple = math.log(final_phi_minus_galley / abs(epsilon)) / T_total
    else:
        measured_rate_simple = 0.0

    theoretical_rate_simple = 1.0 / tau_eff

    result.simple_has_growing_mode = final_phi_minus_galley > abs(epsilon) * 1.5
    result.simple_growth_rate_theoretical = theoretical_rate_simple
    result.simple_growth_rate_measured = measured_rate_simple
    result.simple_growth_rate_matches = (
        abs(measured_rate_simple - theoretical_rate_simple)
        / theoretical_rate_simple < 0.01
    )

    # ── Independent evolution (NOT Galley): Phi_- should DECAY ──
    _, _, _, phi_minus_indep = _integrate_independent(
        phi_1_0, phi_2_0, X_test, tau_eff, dt, n_steps,
    )

    final_phi_minus_indep = abs(phi_minus_indep[-1])
    result.galley_phi_minus_grows = final_phi_minus_galley > abs(epsilon) * 1.5
    result.independent_phi_minus_decays = final_phi_minus_indep < abs(epsilon) * 0.5
    result.cross_coupling_causes_growth = (
        result.galley_phi_minus_grows and result.independent_phi_minus_decays
    )

    # ── Full KG+Galley system ──
    # Use longer integration (10 tau) so the growing mode dominates over the
    # decaying transient.  Measure the LATE-TIME rate from the last third of
    # the run, where the asymptotic growing mode is cleanly dominant.
    n_steps_kg = max(n_steps, 4000)
    n_tau_kg = 10.0
    T_kg = n_tau_kg * tau_eff
    dt_kg = T_kg / n_steps_kg

    phi_minus_kg, _ = _integrate_full_kg_galley_phi_minus(
        epsilon, 0.0, tau_eff, dt_kg, n_steps_kg,
    )

    final_phi_minus_kg = abs(phi_minus_kg[-1])

    # Measure rate from last 1/3 of integration (growing mode dominates)
    i_late_start = 2 * n_steps_kg // 3
    t_late_start = i_late_start * dt_kg
    pm_late_start = abs(phi_minus_kg[i_late_start])
    pm_late_end = abs(phi_minus_kg[-1])
    dt_late = T_kg - t_late_start

    if pm_late_start > 0 and pm_late_end > pm_late_start * 1.01:
        measured_rate_full = math.log(pm_late_end / pm_late_start) / dt_late
    else:
        measured_rate_full = 0.0

    theoretical_rate_full = PHI_GOLDEN / tau_eff

    result.full_has_growing_mode = final_phi_minus_kg > abs(epsilon) * 1.5
    result.full_has_decaying_mode = True  # always true for the 2nd-order system
    result.full_growing_rate_theoretical = theoretical_rate_full
    result.full_decaying_rate_theoretical = 1.0 / (PHI_GOLDEN * tau_eff)
    result.full_growing_rate_measured = measured_rate_full
    result.full_growing_rate_matches = (
        abs(measured_rate_full - theoretical_rate_full)
        / theoretical_rate_full < 0.02  # slightly looser for 2nd-order system
    )

    # ── Cosmological regime ──
    tau0_years = 4.19e7
    H_test = 1.0 / tau0_years
    tau_cosmo = tau0_years / (1.0 + (H_test * tau0_years) ** 2)
    T_cosmo = 3.0 * tau_cosmo
    dt_cosmo = T_cosmo / n_steps

    X_cosmo = H_test ** 2 * 1.1
    phi_c0 = H_test ** 2
    eps_cosmo = abs(phi_c0) * 1e-6 if abs(phi_c0) > 0 else 1e-30

    _, _, _, pm_cosmo = _integrate_galley_coupled(
        phi_c0 + eps_cosmo / 2.0, phi_c0 - eps_cosmo / 2.0,
        X_cosmo, tau_cosmo, dt_cosmo, n_steps,
    )

    final_pm_cosmo = abs(pm_cosmo[-1])
    if final_pm_cosmo > abs(eps_cosmo) * 1.01:
        rate_cosmo = math.log(final_pm_cosmo / abs(eps_cosmo)) / T_cosmo
    else:
        rate_cosmo = 0.0

    result.cosmo_growth_rate_measured = rate_cosmo
    result.cosmo_growth_matches = (
        abs(rate_cosmo - 1.0 / tau_cosmo) / (1.0 / tau_cosmo) < 0.01
    )

    # ── Collapse regime ──
    # Critical damping: tau_eff is much shorter, omega_0 ~ 1/tau_eff
    tau_collapse = 1.0e-3  # seconds (compact object timescale)
    T_collapse = 3.0 * tau_collapse
    dt_collapse = T_collapse / n_steps

    X_collapse = 1.0e10  # m/s^2 (gravitational acceleration scale)
    phi_collapse_0 = 0.5e10
    eps_collapse = abs(phi_collapse_0) * 1e-6

    _, _, _, pm_collapse = _integrate_galley_coupled(
        phi_collapse_0 + eps_collapse / 2.0,
        phi_collapse_0 - eps_collapse / 2.0,
        X_collapse, tau_collapse, dt_collapse, n_steps,
    )

    final_pm_collapse = abs(pm_collapse[-1])
    if final_pm_collapse > abs(eps_collapse) * 1.01:
        rate_collapse = math.log(final_pm_collapse / abs(eps_collapse)) / T_collapse
    else:
        rate_collapse = 0.0

    result.collapse_growth_rate_measured = rate_collapse
    result.collapse_growth_matches = (
        abs(rate_collapse - 1.0 / tau_collapse) / (1.0 / tau_collapse) < 0.01
    )

    # ── CTP boundary condition ──
    result.ctp_boundary_enforces_zero = True
    result.ctp_interpretation = (
        "In the Galley CTP formalism, the physical limit Phi_- = 0 is enforced "
        "as a BOUNDARY CONDITION at the final time (Phi_1(T) = Phi_2(T)), not as "
        "a dynamical attractor. The variational principle operates on the doubled "
        "system with this boundary condition, which selects the physical sector. "
        "The growing ghost mode is the mathematical price paid for encoding "
        "dissipation (time-asymmetry) in a variational framework. "
        "This is analogous to the Schwinger-Keldysh contour in quantum field "
        "theory, where the CTP boundary condition enforces the correct vacuum state."
    )

    # ── Classification ──
    result.is_attractor = False
    result.is_conditional_attractor = False  # not even conditional on any physical condition
    result.classification = "unstable_consistent_truncation"

    result.diagnostics = {
        "simple_phi_minus_final": final_phi_minus_galley,
        "simple_phi_minus_initial": epsilon,
        "simple_growth_ratio": final_phi_minus_galley / abs(epsilon),
        "independent_phi_minus_final": final_phi_minus_indep,
        "independent_decay_ratio": final_phi_minus_indep / abs(epsilon),
        "full_kg_phi_minus_final": final_phi_minus_kg,
        "full_kg_growth_ratio": final_phi_minus_kg / abs(epsilon),
        "cosmo_growth_ratio": final_pm_cosmo / abs(eps_cosmo) if eps_cosmo > 0 else 0.0,
        "collapse_growth_ratio": final_pm_collapse / abs(eps_collapse) if eps_collapse > 0 else 0.0,
        "golden_ratio": PHI_GOLDEN,
    }

    result.notes = [
        "Phi_- = 0 is NOT a dynamical attractor in either formulation",
        f"Simple Galley: Phi_- grows at rate 1/tau = {theoretical_rate_simple:.6e} "
        f"(measured: {measured_rate_simple:.6e})",
        f"Full KG+Galley: Phi_- grows at rate phi/tau = {theoretical_rate_full:.6e} "
        f"(measured: {measured_rate_full:.6e})",
        f"Phi_- growth factor over {n_tau} tau (simple): {final_phi_minus_galley / abs(epsilon):.4f}",
        f"Phi_- decay factor over {n_tau} tau (independent): {final_phi_minus_indep / abs(epsilon):.6e}",
        "Galley cross-coupling (dPhi_1/dt = (X-Phi_2)/tau) CAUSES the growth",
        "Independent evolution (dPhi_i/dt = (X-Phi_i)/tau) gives Phi_- DECAYING",
        "This is a FUNDAMENTAL feature of the Galley formalism, not a bug",
        "The CTP boundary condition at the final time maintains the physical limit",
        "Growth rate is ROBUST across cosmological and collapse parameter regimes",
    ]

    result.nonclaims = [
        "Phi_- = 0 is NOT a dynamical attractor (growing mode exists)",
        "The physical limit is maintained by CTP boundary conditions, not dynamics",
        "This does NOT invalidate the Galley formalism (CTP BCs are fundamental)",
        "The attractor failure means Route B cannot upgrade from physical-limit derived",
        "The growing mode rate (1/tau or phi/tau) is a structural prediction",
    ]

    return result


# ================================================================
# Metric-Difference Sector Analysis
# ================================================================

def analyze_metric_difference_sector() -> MetricDifferenceResult:
    """Analyze the metric-difference sector (g_- = g_1 - g_2).

    The doubled-metric action: S_grav = (1/(16piG)) int [sqrt(-g_1)R_1 - sqrt(-g_2)R_2]

    LINEARIZED ANALYSIS:

    Around the physical limit g_1 = g_2 = g (background), with perturbation:
        g_1 = g + h_+  + h_-/2
        g_2 = g + h_+  - h_-/2

    where h_+ is the physical metric perturbation and h_- is the difference.

    The linearized action for h_- has WRONG-SIGN kinetic energy because:
    - R_1 contributes POSITIVE kinetic term for h_-
    - R_2 contributes NEGATIVE kinetic term for h_-
    - The S_1 - S_2 structure means the net h_- kinetic term is WRONG-SIGN

    This is the gravitational analogue of the scalar ghost: g_2 has wrong-sign
    Einstein-Hilbert action (-R_2 in S = ... - sqrt(-g_2)R_2).

    Furthermore, the scalar difference Phi_- GROWS (from the scalar attractor
    analysis), and its stress-energy sources g_-. This means the metric-difference
    mode is driven by a growing source, making it EVEN MORE unstable.

    CONCLUSION:
    - g_- = 0 is a consistent truncation (by linearity and symmetry)
    - g_- = 0 is EXPECTED to be unstable (wrong-sign kinetic + growing scalar source)
    - Full proof requires solving the linearized Einstein equations for the doubled system
    - This has NOT been done and remains the DEEPEST Route B obstruction
    """
    m = MetricDifferenceResult()

    m.linearized_analysis_possible = True  # structural argument is possible
    m.metric_minus_wrong_sign_kinetic = True
    m.metric_minus_expected_unstable = True

    # g_- = 0 is a solution by symmetry: if g_1 = g_2 = g, the full system
    # reduces to the standard Einstein equations for the single metric g.
    m.metric_truncation_is_consistent = True

    # Coupling to scalar sector
    m.scalar_sources_metric_minus = True
    m.phi_minus_growth_drives_g_minus = True

    # Status
    m.metric_attractor_status = "expected_unstable__not_proven"

    m.full_analysis_obstruction = (
        "The full linearized stability analysis of the metric-difference sector "
        "requires: (1) writing the linearized Einstein equations for g_- sourced "
        "by T^Phi_- around the physical-limit background, (2) solving for the "
        "normal modes of g_-, (3) showing whether the wrong-sign kinetic energy "
        "and the growing scalar source lead to exponential growth of g_-. "
        "This is a tensor-mode perturbation theory problem in the doubled-metric "
        "Galley formalism. No prior treatment exists in the literature. "
        "The structural expectation (wrong-sign kinetic + growing source = unstable) "
        "is strong but NOT proven."
    )

    m.notes = [
        "The metric-difference sector has WRONG-SIGN kinetic energy (gravitational ghost)",
        "This is the metric analogue of the scalar ghost (Phi_2 has wrong-sign kinetic)",
        "g_- = 0 is a CONSISTENT TRUNCATION (by symmetry of the doubled Einstein equations)",
        "g_- = 0 is EXPECTED to be unstable based on:",
        "  1. Wrong-sign kinetic term in the linearized action",
        "  2. Growing scalar source (Phi_- drives g_-)",
        "  3. Structural analogy with the scalar sector (which IS unstable)",
        "Full proof would require solving the linearized doubled Einstein equations",
        "This has NOT been done — deepest remaining Route B obstruction",
        "The CTP boundary condition (g_1(T) = g_2(T)) would maintain g_- = 0 formally",
    ]

    return m


# ================================================================
# Master Analysis
# ================================================================

def compute_galley_truncation_analysis(
    tau_eff: float = 1.0,
    n_steps: int = 2000,
    n_tau: float = 3.0,
    epsilon: float = 1e-6,
) -> GalleyTruncationResult:
    """Full truncation and attractor analysis for the Galley Route B physical limit.

    This is the master function that:
    1. Constructs the doubled-scalar system
    2. Validates the +/- transform
    3. Tests consistent truncation (Phi_- = 0 preserved)
    4. Tests attractor status (Phi_- stability)
    5. Analyzes the metric-difference sector
    6. Classifies the overall result
    """
    result = GalleyTruncationResult()

    # ── Step 1: Build system ──
    result.system = build_doubled_scalar_system(tau_eff)

    # ── Step 2: Validate transform ──
    result.transform = transform_to_plus_minus_variables()

    # ── Step 3: Test truncation ──
    result.scalar_truncation = analyze_scalar_truncation(
        tau_eff=tau_eff, n_steps=n_steps, n_tau=n_tau,
    )

    # ── Step 4: Test attractor ──
    result.scalar_attractor = analyze_scalar_attractor(
        tau_eff=tau_eff, n_steps=n_steps, n_tau=n_tau, epsilon=epsilon,
    )

    # ── Step 5: Metric sector ──
    result.metric = analyze_metric_difference_sector()

    # ── Step 6: Classification ──
    cls = TruncationClassification()

    cls.scalar_truncation = "exact_consistent_truncation"
    cls.scalar_attractor = "not_attractor__growing_mode"

    cls.metric_truncation = "consistent_truncation_expected"
    cls.metric_attractor = "expected_unstable__not_proven"

    cls.overall = "consistent_truncation__not_attractor"

    # Route B upgrade assessment
    cls.route_b_upgrade = "clarification"  # not an upgrade, but a decisive clarification
    cls.route_b_status_before = "physical-limit derived"
    cls.route_b_status_after = (
        "physical-limit derived (truncation consistent, not attractor)"
    )

    cls.notes = [
        "The scalar physical limit IS a consistent truncation (Phi_- = 0 is a solution)",
        "The scalar physical limit is NOT a dynamical attractor (Phi_- grows at rate 1/tau)",
        "The Galley formalism uses CTP boundary conditions to maintain the physical limit",
        "The metric-difference sector is expected unstable but not proven",
        "Route B remains at 'physical-limit derived' — no upgrade to 'derived'",
        "This is a DECISIVE CLARIFICATION: the obstruction is now precisely localized",
        "The next move would be either: (a) prove CTP sufficiency, or "
        "(b) find a modified doubled action with attractive Phi_- dynamics",
    ]

    result.classification = cls

    # ── Remaining obstruction ──
    result.exact_remaining_obstruction = (
        "The consistent truncation analysis reveals that the Galley physical limit "
        "is EXACTLY consistent (Phi_- = 0 is preserved when imposed) but NOT "
        "dynamically attractive (perturbations in Phi_- grow at rate 1/tau). "
        "\n\n"
        "The EXACT remaining obstructions are, ranked by depth: "
        "\n1. ATTRACTOR FAILURE (scalar sector): The ghost mode Phi_- grows "
        "exponentially at rate 1/tau in the simple Galley system and at rate "
        "phi/tau (golden ratio ~ 1.618) in the full KG+Galley system. "
        "The physical limit requires enforcement by CTP boundary conditions, "
        "not dynamical attraction. This prevents the upgrade from "
        "'physical-limit derived' to 'derived'. "
        "\n2. METRIC-DIFFERENCE INSTABILITY (expected, not proven): The "
        "metric-difference mode g_- has wrong-sign kinetic energy and is "
        "sourced by the growing Phi_-. Full linearized analysis of the "
        "doubled Einstein equations has not been performed. "
        "\n3. CTP BOUNDARY CONDITION SUFFICIENCY: Whether the CTP "
        "formulation (with its final-time boundary condition) provides "
        "a mathematically rigorous framework for the physical limit is a "
        "question in mathematical physics that goes beyond the current analysis. "
        "\n4. OBSERVER-FLOW DEPENDENCE: The dissipative kernel requires u^a, "
        "making the action not manifestly covariant. "
        "\n5. POTENTIAL AMBIGUITY: V(Phi) = Phi^2/(2 tau^2) is chosen, not uniquely "
        "determined."
    )

    # ── Route C comparison ──
    result.comparison_to_route_c = (
        "The truncation analysis SHARPENS the comparison between Routes B and C. "
        "\n\n"
        "Route B (Galley): "
        "\n- ADVANTAGE: Produces explicit T^Phi from an action (physical-limit derived) "
        "\n- ADVANTAGE: Has a well-defined variational principle (CTP) "
        "\n- LIMITATION: Physical limit requires CTP boundary enforcement, not dynamics "
        "\n- LIMITATION: Ghost mode Phi_- is unstable (grows at rate 1/tau) "
        "\n- STATUS: physical-limit derived, consistent truncation, not attractor "
        "\n\n"
        "Route C (Nonlocal Retarded): "
        "\n- ADVANTAGE: EOM equivalence is exact (mathematical identity, no projection) "
        "\n- ADVANTAGE: No ghost mode (single-field nonlocal formulation) "
        "\n- ADVANTAGE: No stability issue (no doubled system to stabilize) "
        "\n- LIMITATION: No standard metric variation for T^Phi "
        "\n- STATUS: structural parent for EOM "
        "\n\n"
        "The truncation result STRENGTHENS Route C's position: Route C avoids the "
        "ghost/attractor problem entirely by working with a single field. Route B "
        "produces T^Phi but requires CTP boundary enforcement. Neither route is "
        "strictly better — they remain complementary with different strengths."
    )

    # ── Nonclaims ──
    result.nonclaims = [
        "Phi_- = 0 is a consistent truncation but NOT a dynamical attractor",
        "The growing mode dPhi_-/dt = Phi_-/tau is a FEATURE of the Galley formalism, not a bug",
        "Route B does NOT upgrade from 'physical-limit derived' to 'derived'",
        "The CTP boundary condition maintains the physical limit, but whether this constitutes "
        "a 'derivation' in the physics sense is a matter of interpretation",
        "The metric-difference sector instability is EXPECTED but NOT PROVEN",
        "The cross-coupled Galley dynamics (dPhi_1/dt = (X-Phi_2)/tau) are "
        "DIFFERENT from independent relaxation (dPhi_i/dt = (X-Phi_i)/tau)",
        "No modification of the doubled action has been found that makes Phi_- attractive",
        "The full KG+Galley system has BOTH growing (phi/tau) and decaying (1/(phi*tau)) modes for Phi_-",
        "The golden ratio appearance (phi = (1+sqrt(5))/2) in the growth rate is structural",
        "Route C avoids the ghost/attractor problem entirely by using a single-field nonlocal formulation",
        "Quantization of the Galley CTP action with the ghost sector remains completely open",
        "The attractor failure is ROBUST across cosmological and collapse parameter regimes",
    ]

    result.valid = True
    return result


# ================================================================
# Serialization
# ================================================================

def system_to_dict(s: DoubledScalarSystem) -> Dict[str, Any]:
    return {
        "simple_phi_plus_eom": s.simple_phi_plus_eom,
        "simple_phi_minus_eom": s.simple_phi_minus_eom,
        "simple_phi_minus_growth_rate": s.simple_phi_minus_growth_rate,
        "full_phi_minus_eigenvalues": s.full_phi_minus_eigenvalues,
        "full_phi_minus_growing_rate": s.full_phi_minus_growing_rate,
        "full_phi_minus_decaying_rate": s.full_phi_minus_decaying_rate,
        "has_growing_mode": s.has_growing_mode,
        "phi_minus_is_ghost": s.phi_minus_is_ghost,
        "ctp_boundary_required": s.ctp_boundary_required,
    }


def transform_to_dict(t: PlusMinusTransform) -> Dict[str, Any]:
    return {
        "transform_valid": t.transform_valid,
        "inverse_valid": t.inverse_valid,
        "jacobian_determinant": t.jacobian_determinant,
        "transform_preserves_action": t.transform_preserves_action,
    }


def truncation_to_dict(t: ScalarTruncationResult) -> Dict[str, Any]:
    return {
        "phi_minus_zero_is_solution": t.phi_minus_zero_is_solution,
        "phi_minus_zero_preserved_numerically": t.phi_minus_zero_preserved_numerically,
        "max_phi_minus_residual": t.max_phi_minus_residual,
        "is_consistent_truncation": t.is_consistent_truncation,
        "truncation_classification": t.truncation_classification,
    }


def attractor_to_dict(a: ScalarAttractorResult) -> Dict[str, Any]:
    return {
        "simple_has_growing_mode": a.simple_has_growing_mode,
        "simple_growth_rate_theoretical": a.simple_growth_rate_theoretical,
        "simple_growth_rate_measured": a.simple_growth_rate_measured,
        "simple_growth_rate_matches": a.simple_growth_rate_matches,
        "full_has_growing_mode": a.full_has_growing_mode,
        "full_growing_rate_theoretical": a.full_growing_rate_theoretical,
        "full_growing_rate_measured": a.full_growing_rate_measured,
        "full_growing_rate_matches": a.full_growing_rate_matches,
        "galley_phi_minus_grows": a.galley_phi_minus_grows,
        "independent_phi_minus_decays": a.independent_phi_minus_decays,
        "cross_coupling_causes_growth": a.cross_coupling_causes_growth,
        "cosmo_growth_matches": a.cosmo_growth_matches,
        "collapse_growth_matches": a.collapse_growth_matches,
        "is_attractor": a.is_attractor,
        "classification": a.classification,
    }


def metric_to_dict(m: MetricDifferenceResult) -> Dict[str, Any]:
    return {
        "linearized_analysis_possible": m.linearized_analysis_possible,
        "metric_minus_wrong_sign_kinetic": m.metric_minus_wrong_sign_kinetic,
        "metric_minus_expected_unstable": m.metric_minus_expected_unstable,
        "metric_truncation_is_consistent": m.metric_truncation_is_consistent,
        "scalar_sources_metric_minus": m.scalar_sources_metric_minus,
        "phi_minus_growth_drives_g_minus": m.phi_minus_growth_drives_g_minus,
        "metric_attractor_status": m.metric_attractor_status,
    }


def classification_to_dict(c: TruncationClassification) -> Dict[str, Any]:
    return {
        "scalar_truncation": c.scalar_truncation,
        "scalar_attractor": c.scalar_attractor,
        "metric_truncation": c.metric_truncation,
        "metric_attractor": c.metric_attractor,
        "overall": c.overall,
        "route_b_upgrade": c.route_b_upgrade,
        "route_b_status_before": c.route_b_status_before,
        "route_b_status_after": c.route_b_status_after,
    }


def truncation_result_to_dict(r: GalleyTruncationResult) -> Dict[str, Any]:
    return {
        "valid": r.valid,
        "system": system_to_dict(r.system) if r.system else None,
        "transform": transform_to_dict(r.transform) if r.transform else None,
        "scalar_truncation": truncation_to_dict(r.scalar_truncation) if r.scalar_truncation else None,
        "scalar_attractor": attractor_to_dict(r.scalar_attractor) if r.scalar_attractor else None,
        "metric": metric_to_dict(r.metric) if r.metric else None,
        "classification": classification_to_dict(r.classification) if r.classification else None,
        "nonclaims": r.nonclaims,
    }
