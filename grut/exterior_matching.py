"""Exterior matching module for GRUT collapse sector — Phase III-C WP1.

Gateway question: Does a Barrier-Dominated Compact Core at R_eq = (1/3) r_s
produce any exterior deviation from standard Schwarzschild black-hole behavior,
or is the entire difference hidden behind the horizon?

STATUS: ACTIVE / RESEARCH TARGET
CURRENT ASSESSMENT: Schwarzschild-like exterior is the LEADING CANDIDATE,
    conditional on M_drive being matter-local and OP_QPRESS_001 not having
    exterior gravitational self-energy. This assessment is NOT a proof.

WHAT THIS MODULE DOES:
- Formalizes the interior endpoint state for matching
- Evaluates whether the Schwarzschild exterior candidate is consistent
  with the interior force balance
- Computes the effective enclosed mass at the matching surface
- Identifies required closures for a rigorous determination
- Provides a structured decision on whether WP2/WP3 can proceed

WHAT THIS MODULE DOES NOT DO:
- Derive the exterior metric from covariant GRUT field equations (not formulated)
- Prove or disprove Birkhoff's theorem for GRUT
- Compute ringdown, echoes, shadow, or accretion (deferred to WP2/WP3)
- Determine the interior effective potential for wave propagation

NONCLAIMS:
- The exterior is NOT proven to be Schwarzschild.
- The exterior is NOT proven to be modified.
- The current status is UNDERDETERMINED pending covariant treatment,
  with Schwarzschild-like as the leading candidate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Physical constants (SI)
G_SI = 6.674e-11          # m^3 kg^-1 s^-2
C_SI = 299_792_458.0      # m/s


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class InteriorEndpointState:
    """Interior endpoint state extracted from a CollapseResult.

    These are the solver-backed quantities available for matching.
    """
    # Mass and geometry
    M_kg: float = 0.0                # Total mass (kg)
    R_eq_m: float = 0.0              # Endpoint radius (m)
    r_s_m: float = 0.0               # Schwarzschild radius (m)
    R_eq_over_r_s: float = 0.0       # Dimensionless endpoint radius
    compactness: float = 0.0         # C = r_s / R_eq
    is_post_horizon: bool = False    # C > 1

    # Force balance at endpoint
    a_grav: float = 0.0              # GM/R_eq^2 (m/s^2)
    a_inward: float = 0.0           # (1-alpha)*a_grav + alpha*M_drive (m/s^2)
    a_outward: float = 0.0          # a_Q at endpoint (m/s^2)
    a_net: float = 0.0              # a_inward - a_outward (m/s^2)
    force_balance_residual: float = 0.0  # |a_net| / a_grav

    # Order parameter
    barrier_dominance: float = 0.0   # Phi = a_outward / a_inward
    memory_tracking_ratio: float = 0.0  # M_drive / a_grav

    # Stability
    stability_indicator: float = 0.0  # d(a_net)/dR; positive = restoring
    endpoint_motion_class: str = "unknown"

    # Operator parameters (constrained law)
    epsilon_Q: float = 0.0
    beta_Q: float = 0.0
    alpha_vac: float = 1.0 / 3.0


@dataclass
class ExteriorCandidate:
    """A candidate model for the exterior spacetime.

    STATUS: Each candidate has its own status. The module does not commit
    to any single candidate without sufficient evidence.
    """
    model_name: str = "undefined"
    # "schwarzschild_like" — standard GR vacuum exterior
    # "modified_memory_exterior" — GRUT memory extends outside shell
    # "underdetermined" — current solver cannot decide

    description: str = ""

    # Metric deviation parameter
    # For Schwarzschild: f(r) = 1 - r_s/r + delta_f(r)
    # delta_f = 0 for Schwarzschild, nonzero for modified exterior
    delta_f_at_horizon: float = 0.0       # delta_f evaluated at r = r_s
    delta_f_at_photon_sphere: float = 0.0  # delta_f at r = (3/2) r_s

    # Physical properties
    effective_mass_ratio: float = 1.0  # M_eff / M_input (1.0 = mass conserved)
    birkhoff_compatible: Optional[bool] = None  # True/False/None(unknown)

    # Assessment
    confidence: str = "underdetermined"
    # "high" — strong solver-backed evidence
    # "moderate" — consistent with solver but not proven
    # "low" — speculative, requires covariant treatment
    # "underdetermined" — current solver cannot decide

    required_closures: List[str] = field(default_factory=list)


@dataclass
class MatchingResult:
    """Structured result of the exterior-matching analysis.

    This object is the primary output of WP1. It encodes the current best
    assessment of the exterior spacetime and whether WP2/WP3 can proceed.
    """
    # Interior state (input)
    interior: Optional[InteriorEndpointState] = None

    # Exterior candidates evaluated
    candidates: Dict[str, ExteriorCandidate] = field(default_factory=dict)

    # Best current assessment
    exterior_model: str = "underdetermined"
    # "schwarzschild_like" / "modified_memory_exterior" / "underdetermined"

    birkhoff_status: str = "underdetermined"
    # "preserved_candidate" — leading assessment: Birkhoff holds
    # "modified_candidate" — leading assessment: Birkhoff broken
    # "underdetermined" — current solver cannot decide

    # Matching diagnostics
    effective_mass_ratio: float = 1.0  # M_eff / M_input
    mass_conserved: bool = True  # whether effective mass matches input

    # Decision: can we proceed to WP2 and WP3?
    wp2_allowed: bool = False  # ringdown / echo work
    wp3_allowed: bool = False  # shadow / accretion work
    wp2_basis: str = ""  # on what basis WP2 is allowed/blocked
    wp3_basis: str = ""  # on what basis WP3 is allowed/blocked

    # Required closures for full determination
    required_closures: List[str] = field(default_factory=list)

    # Explicit nonclaims
    nonclaims: List[str] = field(default_factory=list)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def interior_from_collapse_result(result: Any) -> InteriorEndpointState:
    """Extract the interior endpoint state from a CollapseResult.

    Parameters
    ----------
    result : CollapseResult
        A completed collapse simulation result.

    Returns
    -------
    InteriorEndpointState
        Endpoint state suitable for matching analysis.
    """
    R_f = float(result.R_m[-1]) if len(result.R_m) > 0 else 0.0
    r_s = result.r_s_m
    M_kg = result.inputs.get("M_kg", 0.0)

    a_grav = G_SI * M_kg / (R_f * R_f) if R_f > 0 else 0.0

    return InteriorEndpointState(
        M_kg=M_kg,
        R_eq_m=R_f,
        r_s_m=r_s,
        R_eq_over_r_s=R_f / r_s if r_s > 0 else 0.0,
        compactness=r_s / R_f if R_f > 0 else 0.0,
        is_post_horizon=(r_s / R_f >= 1.0) if R_f > 0 else False,
        a_grav=a_grav,
        a_inward=result.a_inward_final,
        a_outward=result.a_outward_final,
        a_net=result.a_net_final,
        force_balance_residual=result.force_balance_residual,
        barrier_dominance=result.barrier_dominance_final,
        memory_tracking_ratio=result.memory_tracking_ratio_final,
        stability_indicator=result.asymptotic_stability_indicator,
        endpoint_motion_class=result.endpoint_motion_class,
        epsilon_Q=result.inputs.get("epsilon_Q", 0.0),
        beta_Q=result.inputs.get("beta_Q", 2.0),
        alpha_vac=result.inputs.get("alpha_vac", 1.0 / 3.0),
    )


def enclosed_mass_at_endpoint(state: InteriorEndpointState) -> float:
    """Compute the effective gravitational mass at the endpoint surface.

    In Newtonian gravity, this is just M. In GR, it is the Misner-Sharp
    mass. In the current GRUT solver, the input mass M is used throughout
    (no mass-energy radiation in the dust model).

    Returns
    -------
    float
        Effective enclosed mass (kg). Currently equal to M_kg.

    Notes
    -----
    If OP_QPRESS_001 has gravitational self-energy, the effective enclosed
    mass could differ from M_kg. This is a missing closure (not computed).
    """
    # In the current solver, mass is conserved (dust model, no radiation).
    # The quantum pressure barrier is a force-law correction, not a
    # mass-energy source. Under this interpretation, M_eff = M_input.
    return state.M_kg


def compactness_at_endpoint(state: InteriorEndpointState) -> float:
    """Return the compactness C = r_s / R_eq at the endpoint.

    Equivalent to 2GM/(Rc²) in geometric units.
    """
    return state.compactness


def exterior_candidate_schwarzschild(
    state: InteriorEndpointState,
) -> ExteriorCandidate:
    """Evaluate the Schwarzschild-like exterior candidate.

    This is the default GR expectation: Birkhoff's theorem gives an exact
    Schwarzschild exterior for any spherically symmetric vacuum region.

    Arguments for this candidate:
    1. Total enclosed mass M is fixed (dust, no radiation).
    2. M_drive is shell-local in the solver (no exterior propagation).
    3. At R >> r_s, a_Q / a_grav → 0 (barrier negligible far away).
    4. Oppenheimer-Snyder analogy starts from Schwarzschild exterior.

    Arguments against:
    1. If M_drive is a spacetime field (not matter-local), exterior ≠ vacuum.
    2. If GRUT modifies field equations, Birkhoff may not hold.
    3. Newtonian-gauge solver cannot rigorously address this.
    """
    M_eff = enclosed_mass_at_endpoint(state)
    mass_ratio = M_eff / state.M_kg if state.M_kg > 0 else 1.0

    closures = []
    if state.memory_tracking_ratio > 0:
        closures.append(
            "Covariant interpretation of M_drive: is it matter-local or a spacetime field?"
        )
    if state.epsilon_Q > 0:
        closures.append(
            "Stress-energy tensor for OP_QPRESS_001: does a_Q contribute gravitating mass?"
        )
    closures.append(
        "Birkhoff proof in GRUT: does the GRUT memory kernel preserve Birkhoff's property?"
    )

    return ExteriorCandidate(
        model_name="schwarzschild_like",
        description=(
            "Standard Schwarzschild vacuum exterior. The collapsing shell "
            "contains all mass-energy; the exterior is vacuum. Birkhoff's "
            "theorem guarantees the Schwarzschild metric for any spherically "
            "symmetric vacuum region in GR. Under the interpretation that "
            "GRUT memory is matter-local (not a spacetime field), this "
            "candidate survives."
        ),
        delta_f_at_horizon=0.0,
        delta_f_at_photon_sphere=0.0,
        effective_mass_ratio=mass_ratio,
        birkhoff_compatible=True,
        confidence="moderate",
        required_closures=closures,
    )


def exterior_candidate_modified(
    state: InteriorEndpointState,
) -> ExteriorCandidate:
    """Evaluate the modified-memory exterior candidate.

    This candidate assumes that the GRUT memory coupling creates a
    residual exterior modification. It is speculative: the current solver
    does not model exterior memory propagation.
    """
    closures = [
        "Covariant field equation for M_drive (spatial propagation)",
        "Stress-energy tensor for the memory field",
        "Exterior solution of modified field equations",
        "Birkhoff violation mechanism in GRUT",
    ]

    return ExteriorCandidate(
        model_name="modified_memory_exterior",
        description=(
            "Hypothetical modified exterior where the GRUT memory field "
            "extends beyond the matter distribution. This would break "
            "Birkhoff's theorem and produce a non-Schwarzschild exterior. "
            "No mechanism for this is formulated in the current solver. "
            "This candidate exists for completeness but has no solver-backed "
            "support."
        ),
        # Cannot compute delta_f without covariant treatment
        delta_f_at_horizon=float("nan"),
        delta_f_at_photon_sphere=float("nan"),
        effective_mass_ratio=float("nan"),  # unknown under this model
        birkhoff_compatible=False,
        confidence="low",
        required_closures=closures,
    )


def evaluate_matching(
    state: InteriorEndpointState,
) -> MatchingResult:
    """Run the full exterior-matching analysis.

    This is the primary WP1 function. It evaluates all exterior candidates
    and produces a structured decision on the exterior model.

    Parameters
    ----------
    state : InteriorEndpointState
        Interior endpoint state from a completed collapse.

    Returns
    -------
    MatchingResult
        Complete matching analysis with decision on WP2/WP3 readiness.
    """
    # Evaluate candidates
    schw = exterior_candidate_schwarzschild(state)
    modified = exterior_candidate_modified(state)

    candidates = {
        "schwarzschild_like": schw,
        "modified_memory_exterior": modified,
    }

    # ── Determine best current assessment ──
    #
    # The Schwarzschild candidate has moderate confidence (consistent with
    # the solver but not proven). The modified candidate has low confidence
    # (speculative, no solver support).
    #
    # Decision logic:
    # 1. If mass is conserved AND barrier is matter-local in solver
    #    → Schwarzschild-like is the leading candidate
    # 2. If mass is NOT conserved → modified candidate gains weight
    # 3. Either way, covariant treatment is required for certainty

    M_eff = enclosed_mass_at_endpoint(state)
    mass_ratio = M_eff / state.M_kg if state.M_kg > 0 else 1.0
    mass_conserved = abs(mass_ratio - 1.0) < 0.01

    if mass_conserved and state.barrier_dominance > 0.9:
        # Strong force balance at endpoint, mass conserved
        # → Schwarzschild-like is the leading candidate
        exterior_model = "schwarzschild_like"
        birkhoff_status = "preserved_candidate"
        confidence_note = (
            "Leading candidate based on: mass conservation, matter-local "
            "M_drive in solver, negligible a_Q at large R, Oppenheimer-Snyder "
            "analogy. Conditional on covariant confirmation."
        )
    elif not mass_conserved:
        # Mass not conserved — unexpected, may indicate modified exterior
        exterior_model = "underdetermined"
        birkhoff_status = "underdetermined"
        confidence_note = (
            "Effective mass deviates from input mass. This is unexpected "
            "under the current dust model and may indicate a missing "
            "energy contribution. Further analysis needed."
        )
    else:
        # Barrier not yet dominant — endpoint not fully converged
        exterior_model = "underdetermined"
        birkhoff_status = "underdetermined"
        confidence_note = (
            "Barrier dominance < 0.9 at endpoint — the shell has not reached "
            "full force balance. Exterior matching requires converged endpoint."
        )

    # ── WP2/WP3 decision ──
    #
    # WP2 (ringdown/echo): Can proceed with Schwarzschild exterior as
    # zeroth-order background. Interior echoes are possible regardless of
    # exterior model — they depend on the interior boundary condition at R_eq.
    #
    # WP3 (shadow): If exterior = Schwarzschild, shadow is trivially identical
    # to GR. WP3 becomes interesting only if exterior deviations exist.

    if exterior_model == "schwarzschild_like":
        wp2_allowed = True
        wp2_basis = (
            "Schwarzschild-like exterior as zeroth-order background. "
            "Interior echo computation depends on boundary condition at "
            "R_eq, which requires the interior effective potential. "
            "WP2 can proceed with parameterized interior reflection."
        )
        wp3_allowed = True
        wp3_basis = (
            "Under Schwarzschild-like exterior: shadow is identical to GR. "
            "WP3 can proceed but the result is expected to be null "
            "(no shadow deviation). Only non-trivial if exterior deviations "
            "are later discovered."
        )
    else:
        wp2_allowed = False
        wp2_basis = (
            "Exterior model underdetermined. Ringdown computation requires "
            "a background metric. Resolve exterior matching first."
        )
        wp3_allowed = False
        wp3_basis = (
            "Exterior model underdetermined. Shadow computation requires "
            "the exterior metric at the photon sphere. Resolve exterior "
            "matching first."
        )

    # ── Required closures ──
    all_closures = list(set(
        schw.required_closures + modified.required_closures
    ))
    all_closures.sort()

    # ── Nonclaims ──
    nonclaims = [
        "The exterior is NOT proven to be Schwarzschild.",
        "The exterior is NOT proven to be modified.",
        "Birkhoff's theorem has NOT been proven or disproven for GRUT.",
        (
            "The Schwarzschild-like assessment is CONDITIONAL on M_drive "
            "being matter-local and OP_QPRESS_001 not having exterior "
            "gravitational self-energy."
        ),
        "A covariant treatment is REQUIRED for a rigorous determination.",
        "No exterior observable predictions have been computed.",
        (
            "This analysis does NOT predict ringdown, echoes, shadow, or "
            "accretion. Those are deferred to WP2 and WP3."
        ),
    ]

    return MatchingResult(
        interior=state,
        candidates=candidates,
        exterior_model=exterior_model,
        birkhoff_status=birkhoff_status,
        effective_mass_ratio=mass_ratio,
        mass_conserved=mass_conserved,
        wp2_allowed=wp2_allowed,
        wp3_allowed=wp3_allowed,
        wp2_basis=wp2_basis,
        wp3_basis=wp3_basis,
        required_closures=all_closures,
        nonclaims=nonclaims,
    )


def evaluate_matching_assumptions(
    state: InteriorEndpointState,
) -> Dict[str, Any]:
    """Evaluate the key assumptions underlying the matching analysis.

    Returns a structured dict of assumptions, each with a status
    (supported / unsupported / underdetermined) and basis.
    """
    assumptions = {}

    # A1: Spherical symmetry
    assumptions["spherical_symmetry"] = {
        "status": "supported",
        "basis": "By construction in the current solver (radial collapse, single shell).",
        "note": "Real astrophysical collapse includes rotation and asymmetries.",
    }

    # A2: Dust matter model (no radiation)
    assumptions["dust_no_radiation"] = {
        "status": "supported",
        "basis": "Current solver is pressureless dust. No mass-energy radiated.",
        "note": "Real collapse emits radiation. This is a model limitation.",
    }

    # A3: M_drive is matter-local
    assumptions["m_drive_matter_local"] = {
        "status": "underdetermined",
        "basis": (
            "The solver computes M_drive only at the shell radius. "
            "There is no spatial propagation equation. This is consistent "
            "with matter-locality but does not prove it."
        ),
        "note": (
            "If M_drive is a spacetime field (gravitational memory), it "
            "could extend outside the shell. A covariant field equation "
            "for M_drive is needed to resolve this."
        ),
        "impact_on_exterior": "If matter-local: Schwarzschild exterior. If spacetime field: possible modification.",
    }

    # A4: OP_QPRESS_001 has no exterior gravitational self-energy
    assumptions["qpress_no_self_energy"] = {
        "status": "underdetermined",
        "basis": (
            "a_Q is defined as a force-law correction in the solver: "
            "a_Q = (GM/R^2) * epsilon_Q * (r_s/R)^beta_Q. "
            "It is not added to the stress-energy tensor."
        ),
        "note": (
            "If interpreted as a vacuum response, the quantum pressure "
            "barrier may carry stress-energy. This requires a covariant "
            "stress-energy tensor for the barrier, which has not been "
            "constructed."
        ),
        "impact_on_exterior": "If no self-energy: mass conserved, Schwarzschild exterior. If self-energy: effective mass modified.",
    }

    # A5: Total mass conservation
    M_eff = enclosed_mass_at_endpoint(state)
    mass_ratio = M_eff / state.M_kg if state.M_kg > 0 else 1.0
    assumptions["mass_conservation"] = {
        "status": "supported",
        "basis": f"M_eff / M_input = {mass_ratio:.6f} (dust model, no radiation).",
        "note": "Mass is exactly conserved in the current solver by construction.",
    }

    # A6: Newtonian gauge captures essential physics
    assumptions["newtonian_gauge_sufficient"] = {
        "status": "underdetermined",
        "basis": (
            "The solver uses Newtonian gravity with GRUT corrections. "
            "At C_eq = 3 (deep inside the horizon), relativistic effects "
            "are strong. The Newtonian approximation may not faithfully "
            "represent the junction conditions."
        ),
        "note": (
            "A relativistic treatment (TOV or covariant field equations) "
            "is needed to verify that the Newtonian-gauge endpoint "
            "survives in the full theory."
        ),
    }

    return assumptions


def compare_exterior_candidates(
    result: MatchingResult,
) -> Dict[str, Any]:
    """Compare the evaluated exterior candidates side by side.

    Returns a comparison dict suitable for inclusion in evidence packets.
    """
    comparison = {}
    for name, cand in result.candidates.items():
        comparison[name] = {
            "confidence": cand.confidence,
            "birkhoff_compatible": cand.birkhoff_compatible,
            "delta_f_at_horizon": cand.delta_f_at_horizon,
            "effective_mass_ratio": cand.effective_mass_ratio,
            "n_required_closures": len(cand.required_closures),
            "required_closures": cand.required_closures,
        }
    comparison["best_current"] = result.exterior_model
    comparison["birkhoff_status"] = result.birkhoff_status
    return comparison


# ============================================================================
# SERIALIZATION
# ============================================================================

def matching_result_to_dict(result: MatchingResult) -> Dict[str, Any]:
    """Serialize a MatchingResult to a dict for evidence packets / JSON output."""
    interior_dict = {}
    if result.interior is not None:
        interior_dict = {
            "M_kg": result.interior.M_kg,
            "R_eq_m": result.interior.R_eq_m,
            "r_s_m": result.interior.r_s_m,
            "R_eq_over_r_s": result.interior.R_eq_over_r_s,
            "compactness": result.interior.compactness,
            "is_post_horizon": result.interior.is_post_horizon,
            "force_balance_residual": result.interior.force_balance_residual,
            "barrier_dominance": result.interior.barrier_dominance,
            "memory_tracking_ratio": result.interior.memory_tracking_ratio,
            "epsilon_Q": result.interior.epsilon_Q,
            "beta_Q": result.interior.beta_Q,
            "alpha_vac": result.interior.alpha_vac,
        }

    candidates_dict = {}
    for name, cand in result.candidates.items():
        candidates_dict[name] = {
            "model_name": cand.model_name,
            "description": cand.description,
            "confidence": cand.confidence,
            "birkhoff_compatible": cand.birkhoff_compatible,
            "delta_f_at_horizon": cand.delta_f_at_horizon,
            "delta_f_at_photon_sphere": cand.delta_f_at_photon_sphere,
            "effective_mass_ratio": cand.effective_mass_ratio,
            "required_closures": cand.required_closures,
        }

    return {
        "interior_endpoint": interior_dict,
        "candidates": candidates_dict,
        "exterior_model": result.exterior_model,
        "birkhoff_status": result.birkhoff_status,
        "effective_mass_ratio": result.effective_mass_ratio,
        "mass_conserved": result.mass_conserved,
        "wp2_allowed": result.wp2_allowed,
        "wp2_basis": result.wp2_basis,
        "wp3_allowed": result.wp3_allowed,
        "wp3_basis": result.wp3_basis,
        "required_closures": result.required_closures,
        "nonclaims": result.nonclaims,
    }
