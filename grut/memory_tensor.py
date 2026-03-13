"""Explicit effective memory stress-energy tensor T^Φ_μν and action status.

Phase III Package A: pushes the memory sector beyond "schematic auxiliary field"
toward the strongest explicit effective closure currently achievable.

STATUS: CONSTITUTIVE / NONLOCAL-EFFECTIVE
The T^Φ_μν derived here is a constitutive effective stress-energy tensor.
It is NOT derived from a covariant action or Lagrangian. It is constructed
to be the unique source term that, when inserted into the Einstein equations
alongside T_μν, reproduces the GRUT sector dynamics.

KEY RESULTS:
- Cosmological sector: ρ_Φ = (3α_mem / 8πG)(Φ − H²_base), p_Φ determined
  by combined conservation
- Collapse sector: effective radial stress from force balance decomposition
- Action candidate identified (nonlocal retarded action) but first-order
  relaxation is inherently dissipative — standard variational principle
  does not apply without auxiliary fields
- Scalar is minimal; tensorial generalisation adds anisotropic stress and
  propagating modes, classified but not implemented

NONCLAIMS:
- T^Φ_μν is constitutive/effective, NOT derived from a Lagrangian
- Combined conservation is imposed, NOT proven from an action
- Pressure p_Φ determined by conservation, NOT by equation of state
- Energy conditions not guaranteed without further constraints
- Scalar field does not propagate in current formulation (no wave equation)
- Tensorial generalisation classified but not derived

See docs/PHASE_III_PACKAGE_A_MEMORY_TENSOR.md for the full derivation memo.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# Physical constants
G_SI = 6.674e-11          # m^3 kg^-1 s^-2
C_SI = 299_792_458.0      # m/s
M_SUN = 1.989e30          # kg


# ================================================================
# Data Structures
# ================================================================

@dataclass
class EffectiveMemoryTensor:
    """Explicit effective T^Φ_μν components for a given sector state.

    In the cosmological (FRW) sector, T^Φ_μν takes perfect-fluid form:
        T^Φ_μν = (ρ_Φ + p_Φ) u_μ u_ν + p_Φ g_μν

    In the collapse (spherical) sector, T^Φ_μν has anisotropic stress:
        T^Φ_μν = diag(−ρ_Φ, p_r_Φ, p_t_Φ, p_t_Φ)
    in the comoving frame.

    STATUS: CONSTITUTIVE — derived from sector equations, not from action.
    """
    sector: str = ""            # "cosmological" or "collapse"

    # Energy density
    rho_phi: float = 0.0        # effective memory energy density

    # Pressure (cosmological: isotropic; collapse: anisotropic)
    p_phi: float = 0.0          # isotropic pressure (cosmo) or radial pressure (collapse)
    p_tangential: float = 0.0   # tangential pressure (collapse only; = p_phi for cosmo)

    # Equation of state
    w_phi: float = 0.0          # effective EOS: w_Φ = p_Φ / ρ_Φ

    # Energy conditions
    weak_energy: bool = False    # ρ_Φ ≥ 0 and ρ_Φ + p_Φ ≥ 0
    null_energy: bool = False    # ρ_Φ + p_Φ ≥ 0
    strong_energy: bool = False  # ρ_Φ + 3p_Φ ≥ 0
    dominant_energy: bool = False  # ρ_Φ ≥ |p_Φ|

    # Derivation level
    derivation: str = "constitutive"   # always "constitutive" in current pass
    notes: List[str] = field(default_factory=list)
    valid: bool = False


@dataclass
class ActionStatus:
    """Assessment of the action / Lagrangian status of the GRUT memory sector.

    CLASSIFICATION:
    - "action_derived": field equations follow from δS/δg = 0, δS/δΦ = 0
    - "action_candidate": a candidate action exists but has not been proven
      to reproduce the dynamics exactly
    - "constitutive_effective": the dynamics are constitutive; no standard
      variational principle applies without auxiliary fields

    Current status: CONSTITUTIVE_EFFECTIVE with action candidate identified.
    """
    classification: str = "constitutive_effective"
    candidate_action: str = ""
    candidate_action_produces_relaxation: bool = False
    dissipation_barrier: str = ""
    galley_formalism_applicable: bool = False
    summary: str = ""
    nonclaims: List[str] = field(default_factory=list)


@dataclass
class TensorialComparison:
    """Structural comparison: scalar memory Φ vs tensorial memory Φ_μν.

    The scalar field is the minimal closure. The tensorial generalisation
    would carry additional degrees of freedom.
    """
    scalar_dof: int = 1         # one relaxation ODE per sector
    tensor_dof: int = 0         # depends on symmetry and constraints
    scalar_sufficient_for: List[str] = field(default_factory=list)
    tensor_required_for: List[str] = field(default_factory=list)
    structural_differences: List[str] = field(default_factory=list)
    recommendation: str = ""
    nonclaims: List[str] = field(default_factory=list)


@dataclass
class PackageAResult:
    """Master result for Package A: Memory Tensor Closure."""
    tensor_cosmo: Optional[EffectiveMemoryTensor] = None
    tensor_collapse: Optional[EffectiveMemoryTensor] = None
    action_status: Optional[ActionStatus] = None
    tensorial_comparison: Optional[TensorialComparison] = None
    conservation_verified: bool = False
    nonclaims: List[str] = field(default_factory=list)
    valid: bool = False


# ================================================================
# Cosmological Sector: Effective T^Φ_μν
# ================================================================

def compute_cosmo_memory_tensor(
    alpha_mem: float = 0.1,
    H_current: float = 0.0,
    H_base_sq: float = 0.0,
    Phi: float = 0.0,
    dPhi_dt: float = 0.0,
) -> EffectiveMemoryTensor:
    """Derive effective T^Φ_μν in the cosmological (FRW) sector.

    From the modified Friedmann equation:
        H² = (1 − α) H²_base + α Φ

    The memory contribution to the effective energy density is:
        ρ_Φ = (3c² / 8πG) · α · (Φ − H²_base)

    At steady state (Φ = H²_base): ρ_Φ = 0 — memory is invisible.
    Out of steady state: ρ_Φ encodes the lag between memory and driver.

    The pressure p_Φ is determined by the combined conservation equation
    ∇_μ(T^μν_matter + T^Φ_μν) = 0, which in FRW gives:
        dρ_Φ/dt + 3H(ρ_Φ + p_Φ) = Q_exchange

    where Q_exchange encodes any exchange with the matter sector.

    Parameters
    ----------
    alpha_mem : float
        Cosmological memory coupling.
    H_current : float
        Current Hubble rate (1/years or code units).
    H_base_sq : float
        Standard Friedmann H² (before memory modification).
    Phi : float
        Current memory state M_X.
    dPhi_dt : float
        Time derivative of memory state (from relaxation ODE).

    Returns
    -------
    EffectiveMemoryTensor
    """
    t = EffectiveMemoryTensor(sector="cosmological")

    # ── Energy density ──
    # ρ_Φ = (3c²/(8πG)) × α × (Φ − H²_base)
    # In code units where H is in 1/years: factor = 3/(8πG) in consistent units
    # We work in dimensionless ratios for structural verification.
    delta = Phi - H_base_sq
    t.rho_phi = alpha_mem * delta  # in units of H² (dimensionless energy density ratio)

    # ── Pressure from conservation ──
    # In FRW: dρ_Φ/dt + 3H(ρ_Φ + p_Φ) = 0 (combined conservation)
    # dρ_Φ/dt = α × dΦ/dt − α × dH²_base/dt
    # The memory ODE gives: dΦ/dt = (H²_base − Φ)/τ_eff = −delta/τ_eff
    # So: dρ_Φ/dt = α × (−delta/τ_eff) − α × dH²_base/dt
    #
    # For quasi-static analysis (slow evolution of H_base):
    # dρ_Φ/dt ≈ −α × delta / τ_eff
    # Then: −α δ/τ + 3H(ρ_Φ + p_Φ) = 0
    # p_Φ = −ρ_Φ + α δ / (3H τ)
    # p_Φ = −ρ_Φ + ρ_Φ / (3H τ)    since ρ_Φ = α δ
    # p_Φ = ρ_Φ (1/(3Hτ) − 1)
    #
    # This gives a time-dependent effective equation of state.
    if abs(H_current) > 1e-30 and abs(delta) > 1e-30:
        # Using the relation dρ_Φ/dt = α × dΦ_dt (rate of change of memory contribution)
        drho_dt = alpha_mem * dPhi_dt
        # From conservation: p_Φ = −ρ_Φ − dρ_Φ/(3H dt)
        t.p_phi = -t.rho_phi - drho_dt / (3.0 * H_current)
        t.p_tangential = t.p_phi  # isotropic in FRW
    else:
        # Steady state or zero H: p_Φ = −ρ_Φ (cosmological-constant-like)
        t.p_phi = -t.rho_phi
        t.p_tangential = t.p_phi

    # ── Equation of state ──
    if abs(t.rho_phi) > 1e-30:
        t.w_phi = t.p_phi / t.rho_phi
    else:
        t.w_phi = -1.0  # degenerate case, cosmological-constant-like

    # ── Energy conditions ──
    rho = t.rho_phi
    p = t.p_phi
    t.weak_energy = (rho >= -1e-30) and (rho + p >= -1e-30)
    t.null_energy = (rho + p >= -1e-30)
    t.strong_energy = (rho + 3.0 * p >= -1e-30)
    t.dominant_energy = (rho >= -1e-30) and (abs(p) <= rho + 1e-30)

    t.derivation = "constitutive"
    t.notes = [
        "ρ_Φ = α(Φ − H²_base): encodes memory lag",
        "At steady state (Φ = H²_base): ρ_Φ = 0 (memory invisible)",
        "p_Φ determined by combined conservation, NOT by equation of state",
        "Energy conditions are STATE-DEPENDENT — can be violated transiently",
        "Perfect fluid form assumed (isotropic); valid for FRW sector",
    ]
    t.valid = True
    return t


# ================================================================
# Collapse Sector: Effective T^Φ_μν
# ================================================================

def compute_collapse_memory_tensor(
    M_kg: float = 30.0 * M_SUN,
    alpha_vac: float = 1.0 / 3.0,
    beta_Q: float = 2.0,
    epsilon_Q: float = 1.0 / 9.0,
    R_current: float = 0.0,
    M_drive: float = 0.0,
    a_grav: float = 0.0,
) -> EffectiveMemoryTensor:
    """Derive effective T^Φ_μν in the collapse (spherical) sector.

    From the force balance:
        a_eff = (1 − α_vac) a_grav + α_vac M_drive − a_Q

    The memory contribution to the effective acceleration is:
        Δa_mem = α_vac (M_drive − a_grav)

    This maps to an effective radial stress in the Einstein equations.
    The memory stress-energy in spherical symmetry is anisotropic:
        T^Φ_μν = diag(−ρ_Φ, p_r_Φ, p_t_Φ, p_t_Φ)

    Parameters
    ----------
    M_kg : float
        Object mass (kg).
    alpha_vac, beta_Q, epsilon_Q : float
        Barrier and coupling parameters.
    R_current : float
        Current shell radius (m). If 0, uses R_eq.
    M_drive : float
        Current memory state (m/s²). If 0, uses equilibrium a_grav.
    a_grav : float
        Current gravitational acceleration (m/s²). If 0, computed from M, R.

    Returns
    -------
    EffectiveMemoryTensor
    """
    t = EffectiveMemoryTensor(sector="collapse")

    if M_kg <= 0:
        return t

    r_s = 2.0 * G_SI * M_kg / (C_SI ** 2)
    R_eq = r_s * epsilon_Q ** (1.0 / beta_Q) if epsilon_Q > 0 and beta_Q > 0 else r_s
    R = R_current if R_current > 0 else R_eq
    GM = G_SI * M_kg

    if R <= 0:
        return t

    # Gravitational acceleration
    a_g = a_grav if a_grav > 0 else GM / (R ** 2)

    # Memory state: at equilibrium M_drive = a_grav
    Md = M_drive if M_drive > 0 else a_g

    # ── Memory force contribution ──
    # The memory modifies effective acceleration by:
    # Δa_mem = α(M_drive − a_grav)
    delta_a = alpha_vac * (Md - a_g)

    # ── Effective energy density ──
    # The radial force Δa corresponds to an effective pressure gradient:
    # dp_r_Φ/dr = −ρ_eff × Δa (in Newtonian limit)
    # For order-of-magnitude at R_eq:
    # ρ_Φ ~ M_kg / (4π/3 × R³) × |Δa/a_grav| (fractional memory contribution)
    V_shell = (4.0 / 3.0) * math.pi * R ** 3
    rho_matter = M_kg / V_shell if V_shell > 0 else 0.0

    # Memory energy density: fraction of matter energy density
    # proportional to the memory lag
    memory_fraction = abs(Md - a_g) / a_g if a_g > 0 else 0.0
    t.rho_phi = alpha_vac * memory_fraction * rho_matter

    # ── Radial pressure (anisotropic) ──
    # The memory contributes a radial stress that modifies the force balance.
    # At equilibrium (Md = a_grav): Δa = 0 → p_r_Φ = 0 (memory is invisible)
    # Out of equilibrium: p_r_Φ encodes the memory lag
    t.p_phi = alpha_vac * (Md - a_g) / a_g * rho_matter if a_g > 0 else 0.0

    # ── Tangential pressure ──
    # From combined conservation in spherical symmetry:
    # dp_r/dr + (2/r)(p_r − p_t) + ... = 0
    # At equilibrium: anisotropic stress vanishes → p_t = p_r
    t.p_tangential = t.p_phi * 0.5  # approximate: tangential stress is subdominant

    # ── Equation of state ──
    if abs(t.rho_phi) > 1e-30:
        t.w_phi = t.p_phi / t.rho_phi
    else:
        t.w_phi = 0.0

    # ── Energy conditions ──
    rho = t.rho_phi
    p_r = t.p_phi
    p_t = t.p_tangential
    t.weak_energy = (rho >= -1e-30) and (rho + p_r >= -1e-30)
    t.null_energy = (rho + p_r >= -1e-30) and (rho + p_t >= -1e-30)
    t.strong_energy = (rho + p_r + 2.0 * p_t >= -1e-30)
    t.dominant_energy = (rho >= -1e-30) and (abs(p_r) <= rho + 1e-30)

    t.derivation = "constitutive"
    t.notes = [
        "Anisotropic: p_r ≠ p_t in general (spherical symmetry)",
        "At equilibrium (M_drive = a_grav): ρ_Φ → 0, p_r → 0 (memory invisible)",
        "Memory stress encodes the lag between M_drive and a_grav",
        "Energy conditions are STATE-DEPENDENT — depend on memory lag",
        "Constitutive derivation: NOT from action or equation of state",
    ]
    t.valid = True
    return t


# ================================================================
# Action / Lagrangian Status
# ================================================================

def assess_action_status() -> ActionStatus:
    """Classify the action / Lagrangian status of the GRUT memory sector.

    The first-order relaxation equation τ dΦ/dt + Φ = X is inherently
    dissipative. A standard variational principle δS = 0 produces
    second-order equations of motion, not first-order relaxation.

    Three routes to an action exist:
    1. Nonlocal retarded action (Candidate 3 kernel formulation)
    2. Galley doubled-variable formalism (for dissipative systems)
    3. Promote Φ to a massive Klein-Gordon field with strong damping

    All three are candidates, none is confirmed to reproduce the exact
    GRUT dynamics.

    Returns
    -------
    ActionStatus
    """
    a = ActionStatus()

    a.classification = "constitutive_effective"

    a.candidate_action = (
        "S = S_EH[g] + S_matter[g, ψ] + S_memory[g, Φ]\n"
        "where S_memory = −∫ d⁴x √(−g) ["
        "½ g^αβ ∇_α Φ ∇_β Φ + V(Φ) + Φ · J[g, T]"
        "]\n"
        "with J[g, T] = X[g, T] / τ_eff (source current)\n"
        "and V(Φ) = Φ²/(2τ²_eff) (mass term from relaxation)"
    )

    a.candidate_action_produces_relaxation = False
    a.dissipation_barrier = (
        "The relaxation equation τ u^α ∇_α Φ + Φ = X is first-order in "
        "proper-time derivatives. A standard Klein-Gordon action produces "
        "□Φ + m²Φ = J (second-order). The first-order form arises in the "
        "OVERDAMPED LIMIT (m²τ >> 1) of the Klein-Gordon equation, or via "
        "the Galley doubled-variable formalism for open systems. Neither "
        "route has been fully verified for the GRUT dynamics."
    )

    a.galley_formalism_applicable = True

    a.summary = (
        "CLASSIFICATION: CONSTITUTIVE / NONLOCAL-EFFECTIVE.\n\n"
        "The GRUT memory sector is best understood as a constitutive "
        "effective theory. The dynamics are specified by the relaxation "
        "equation and the sector-specific force/Friedmann modifications, "
        "not derived from varying an action.\n\n"
        "An action CANDIDATE exists: the nonlocal retarded action of "
        "Candidate 3, whose exponential kernel reproduces the relaxation "
        "ODE along a single observer flow. The Klein-Gordon action with "
        "overdamped limit is a second candidate.\n\n"
        "The fundamental obstacle is that the first-order relaxation "
        "equation is inherently dissipative. Standard variational "
        "principles produce conservative (second-order) equations. "
        "Reproducing first-order relaxation requires either:\n"
        "  (a) the overdamped limit of a second-order theory, or\n"
        "  (b) the Galley doubled-variable formalism, or\n"
        "  (c) accepting the nonlocal kernel as the fundamental object.\n\n"
        "None of these routes has been fully closed in the current pass."
    )

    a.nonclaims = [
        "The theory is NOT action-derived in its current form",
        "Candidate action exists but has NOT been proven to reproduce dynamics",
        "First-order relaxation is inherently dissipative — no standard variational principle",
        "Overdamped Klein-Gordon limit is a CANDIDATE route, not confirmed",
        "Galley doubled formalism is applicable in principle, not implemented",
        "Nonlocal retarded action (Candidate 3) is the formal parent, not proven equivalent globally",
        "Conservation is IMPOSED, not proven from Noether theorem",
    ]

    return a


# ================================================================
# Scalar vs Tensorial Comparison
# ================================================================

def compare_scalar_vs_tensor() -> TensorialComparison:
    """Structural comparison of scalar Φ vs tensorial Φ_μν memory field.

    The scalar memory field is the minimal covariant object carrying the
    existing memory degree of freedom (one relaxation ODE per sector).
    A tensorial generalisation (symmetric rank-2 field) would carry up to
    10 independent components, subject to symmetry and constraint equations.

    Returns
    -------
    TensorialComparison
    """
    tc = TensorialComparison()

    tc.scalar_dof = 1  # one ODE per sector
    tc.tensor_dof = 6  # symmetric rank-2 in 4D, minus 4 from diffeomorphism constraints → 6 propagating DOF (massive) or 2 (massless)

    tc.scalar_sufficient_for = [
        "FRW cosmology (isotropic, homogeneous)",
        "Spherical collapse (radially symmetric)",
        "Current operator stack (single memory ODE per sector)",
        "Structural identity ω₀τ=1 (depends on scalar relaxation only)",
        "PDE dispersion relation (single-mode perturbation theory)",
        "All current Phase III results",
    ]

    tc.tensor_required_for = [
        "Anisotropic memory effects (shear memory, gravitational-wave memory)",
        "Propagating memory degrees of freedom (memory gravitational waves)",
        "Memory contributions to the Weyl tensor (tidal effects beyond Love numbers)",
        "Multi-mode coupling with angular dependence",
        "Kerr (axisymmetric, not spherically symmetric) — partial: scalar may suffice for leading order",
        "Non-perturbative strong-field dynamics (merger phase)",
    ]

    tc.structural_differences = [
        "Scalar: T^Φ_μν is perfect fluid (cosmo) or simple anisotropic (collapse)",
        "Tensor: T^Φ_μν carries independent shear, anisotropic stress, propagating modes",
        "Scalar: relaxation is single ODE per sector",
        "Tensor: relaxation is coupled system of up to 6 equations (massive) or 2 (massless)",
        "Scalar: Bianchi compatibility is simple (single conservation equation)",
        "Tensor: Bianchi compatibility requires separate analysis for each component",
        "Scalar: no gravitational-wave memory content",
        "Tensor: can carry Christodoulou-type gravitational-wave memory",
    ]

    tc.recommendation = (
        "SCALAR IS SUFFICIENT FOR ALL CURRENT PHASE III RESULTS. "
        "Tensorial generalisation is required only for: (i) anisotropic/shear "
        "effects, (ii) propagating memory, (iii) gravitational-wave memory "
        "coupling. These are POST-PHASE-III research targets. The scalar "
        "formulation is the correct minimal closure for the current pass."
    )

    tc.nonclaims = [
        "Scalar is the MINIMAL closure, NOT proven to be the final ontology",
        "Tensorial generalisation is classified but NOT derived",
        "Whether memory is fundamentally scalar or tensorial remains OPEN",
        "The 6-DOF estimate for massive tensor assumes no additional constraints",
        "Scalar sufficiency for Kerr is a conjecture (leading order), not proven",
    ]

    return tc


# ================================================================
# Combined Conservation Check
# ================================================================

def verify_cosmo_conservation(
    alpha_mem: float = 0.1,
    H: float = 1.0,
    H_base_sq: float = 1.0,
    Phi: float = 0.9,
    tau_eff: float = 1.0,
    rho_m: float = 1.0,
    w: float = 0.0,
) -> Dict[str, Any]:
    """Verify combined conservation ∇_μ(T^μν_m + T^Φ_μν) = 0 in FRW.

    In FRW, conservation reduces to:
        d(ρ_m + ρ_Φ)/dt + 3H(ρ_m + p_m + ρ_Φ + p_Φ) = 0

    We verify this is satisfied when ρ_Φ, p_Φ are computed constitutively
    and the memory ODE is satisfied.

    Returns dict with conservation residual and diagnostic info.
    """
    if H <= 0 or tau_eff <= 0:
        return {"residual": 0.0, "verified": True, "notes": "degenerate case"}

    # Memory energy density
    delta = Phi - H_base_sq
    rho_phi = alpha_mem * delta

    # Memory ODE: dPhi/dt = (H_base_sq - Phi)/tau_eff = -delta/tau_eff
    dPhi_dt = -delta / tau_eff

    # Rate of change of ρ_Φ (quasi-static H_base_sq)
    drho_phi_dt = alpha_mem * dPhi_dt

    # Pressure from conservation: p_Φ = −ρ_Φ − dρ_Φ/(3H dt)
    p_phi = -rho_phi - drho_phi_dt / (3.0 * H)

    # Matter continuity: dρ_m/dt = −3H(ρ_m + p_m)
    p_m = w * rho_m
    drho_m_dt = -3.0 * H * (rho_m + p_m)

    # Combined conservation residual:
    # d(ρ_m + ρ_Φ)/dt + 3H(ρ_m + p_m + ρ_Φ + p_Φ) = 0
    drho_total_dt = drho_m_dt + drho_phi_dt
    pressure_total = rho_m + p_m + rho_phi + p_phi
    residual = drho_total_dt + 3.0 * H * pressure_total

    return {
        "residual": residual,
        "residual_rel": abs(residual) / max(abs(drho_m_dt), 1e-30),
        "verified": abs(residual) < 1e-10 * max(abs(drho_m_dt), 1e-30),
        "rho_phi": rho_phi,
        "p_phi": p_phi,
        "w_phi": p_phi / rho_phi if abs(rho_phi) > 1e-30 else -1.0,
        "notes": "Combined conservation verified by construction (p_Φ derived from conservation)",
    }


# ================================================================
# Master Analysis
# ================================================================

def compute_package_a_analysis(
    M_kg: float = 30.0 * M_SUN,
    alpha_mem: float = 0.1,
    alpha_vac: float = 1.0 / 3.0,
    beta_Q: float = 2.0,
    epsilon_Q: float = 1.0 / 9.0,
) -> PackageAResult:
    """Full Package A analysis: memory tensor, action status, tensor comparison.

    Returns
    -------
    PackageAResult
    """
    result = PackageAResult()

    # ── Cosmological tensor (representative state with 10% memory lag) ──
    H_test = 1.0  # representative H in code units
    H_base_sq = H_test ** 2
    Phi_lagged = 0.9 * H_base_sq  # 10% lag
    tau_eff = 0.5  # representative
    dPhi_dt = (H_base_sq - Phi_lagged) / tau_eff

    result.tensor_cosmo = compute_cosmo_memory_tensor(
        alpha_mem=alpha_mem,
        H_current=H_test,
        H_base_sq=H_base_sq,
        Phi=Phi_lagged,
        dPhi_dt=dPhi_dt,
    )

    # ── Collapse tensor (at equilibrium) ──
    result.tensor_collapse = compute_collapse_memory_tensor(
        M_kg=M_kg,
        alpha_vac=alpha_vac,
        beta_Q=beta_Q,
        epsilon_Q=epsilon_Q,
    )

    # ── Action status ──
    result.action_status = assess_action_status()

    # ── Tensorial comparison ──
    result.tensorial_comparison = compare_scalar_vs_tensor()

    # ── Conservation check ──
    cons = verify_cosmo_conservation(
        alpha_mem=alpha_mem,
        H=H_test,
        H_base_sq=H_base_sq,
        Phi=Phi_lagged,
        tau_eff=tau_eff,
    )
    result.conservation_verified = cons["verified"]

    # ── Nonclaims ──
    result.nonclaims = [
        "T^Φ_μν is CONSTITUTIVE/EFFECTIVE — derived from sector equations, NOT from action",
        "Combined conservation is satisfied BY CONSTRUCTION (p_Φ derived from conservation)",
        "Energy conditions are STATE-DEPENDENT — can be violated during transients",
        "Pressure p_Φ is NOT determined by an equation of state — it follows from conservation",
        "The action is CONSTITUTIVE_EFFECTIVE — standard variational principle does not apply directly",
        "Overdamped Klein-Gordon and nonlocal retarded action are CANDIDATES, not confirmed",
        "Scalar memory is SUFFICIENT for all current Phase III results",
        "Tensorial generalisation is CLASSIFIED but NOT derived",
        "At equilibrium in both sectors, ρ_Φ → 0: memory is invisible at fixed points",
        "Memory stress-energy is dynamically active ONLY during transients (lag ≠ 0)",
    ]

    result.valid = (
        result.tensor_cosmo.valid
        and result.tensor_collapse.valid
        and result.conservation_verified
    )

    return result


# ================================================================
# Serialization
# ================================================================

def tensor_to_dict(t: EffectiveMemoryTensor) -> Dict[str, Any]:
    return {
        "sector": t.sector,
        "rho_phi": t.rho_phi,
        "p_phi": t.p_phi,
        "p_tangential": t.p_tangential,
        "w_phi": t.w_phi,
        "weak_energy": t.weak_energy,
        "null_energy": t.null_energy,
        "strong_energy": t.strong_energy,
        "dominant_energy": t.dominant_energy,
        "derivation": t.derivation,
        "notes": t.notes,
        "valid": t.valid,
    }


def package_a_to_dict(r: PackageAResult) -> Dict[str, Any]:
    return {
        "tensor_cosmo": tensor_to_dict(r.tensor_cosmo) if r.tensor_cosmo else None,
        "tensor_collapse": tensor_to_dict(r.tensor_collapse) if r.tensor_collapse else None,
        "action_classification": r.action_status.classification if r.action_status else None,
        "action_summary": r.action_status.summary if r.action_status else None,
        "tensorial_recommendation": r.tensorial_comparison.recommendation if r.tensorial_comparison else None,
        "conservation_verified": r.conservation_verified,
        "nonclaims": r.nonclaims,
        "valid": r.valid,
    }
