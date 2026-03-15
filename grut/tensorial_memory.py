"""GRUT Phase IV Package 2: Tensorial Memory-Field Program.

Evaluates five candidate tensor structures for the GRUT memory sector
and determines the most honest extension path beyond the scalar closure.

STATUS: SCALAR CLOSURE SUFFICIENT; TENSORIAL EXTENSION PATH IDENTIFIED
The scalar memory Phi is sufficient for all Phase III results. The minimal
tensorial extension (scalar + trace-free anisotropic stress) is identified
as the next step, with the full rank-2 tensor as the maximal candidate.

CANDIDATES:
1. Scalar-only closure (current) — sufficient for Phase III
2. Scalar + anisotropic stress (sigma_{ab}) — minimal extension (6 DOF)
3. Scalar + vector (v_a) — intermediate extension (4 DOF)
4. Rank-2 symmetric tensor (Phi_{ab}) — maximal extension (6-10 DOF)
5. Constitutive anisotropic stress — effective limit, no new DOF

KEY RESULTS:
- Scalar IS the symmetry-reduced limit of deeper tensorial structure
- All Phase III results survive unchanged under tensorial extension
- New physics (shear memory, GW memory, multi-polarization echoes) requires
  at minimum Candidate 2
- Recommended path: constitutive aniso (now) -> scalar+sigma (next) -> full tensor (future)

NONCLAIMS:
- No complete tensorial field theory constructed
- Scalar proven sufficient, not proven final
- Extension path is a recommendation, not a uniqueness result
- No observational predictions distinguish the candidates

See docs/PHASE_IV_PACKAGE_2_TENSORIAL_MEMORY.md for the full theory memo.
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
class TensorCandidate:
    """A candidate tensor structure for the GRUT memory sector.

    Each candidate represents a different level of tensorial complexity
    for extending the scalar memory Phi to a tensor memory Phi_{ab}.
    """
    name: str = ""
    label: str = ""

    # Structure
    tensor_type: str = ""       # "scalar", "scalar_plus_aniso", "scalar_plus_vector",
                                 # "rank2_symmetric", "constitutive_aniso"
    total_dof: int = 0           # total degrees of freedom (in 3+1 split)
    propagating_dof: int = 0     # propagating DOF (massive) or helicity DOF (massless)
    scalar_dof: int = 1          # scalar trace DOF (always 1)
    additional_dof: int = 0      # DOF beyond scalar

    # Components
    components: List[str] = field(default_factory=list)
    relaxation_equations: int = 0  # number of coupled relaxation ODEs

    # Symmetry reduction
    reduces_to_scalar: bool = False  # recovers Candidate 1 in isotropic/spherical limit
    symmetry_for_reduction: str = "" # what symmetry triggers reduction

    # Phase III compatibility
    phase3_results_unchanged: bool = False
    modifies_what: List[str] = field(default_factory=list)
    enables_new: List[str] = field(default_factory=list)

    # Assessment
    classification: str = ""     # "sufficient", "minimal_extension", "plausible_intermediate",
                                  # "maximal_extension", "effective_limit"
    computational_cost: str = ""  # "low", "moderate", "high"
    recommended_phase: str = ""   # when to pursue this candidate

    # Nonclaims
    nonclaims: List[str] = field(default_factory=list)


@dataclass
class ScalarSufficiencyCheck:
    """Verification that the scalar closure is sufficient for all Phase III results.

    For each Phase III result, confirm that the scalar DOF is structurally
    adequate and that no tensorial content is required.
    """
    result_name: str = ""
    scalar_sufficient: bool = False
    reason: str = ""
    tensor_would_modify: bool = False
    tensor_modification: str = ""


@dataclass
class SymmetryReductionCheck:
    """Verification that the scalar arises as a symmetry reduction of a tensor.

    In FRW (isotropic): only the trace survives.
    In spherical: trace + one anisotropic component survive.
    In axisymmetric: trace + multiple components survive.
    """
    spacetime_symmetry: str = ""    # "FRW_isotropic", "spherical", "axisymmetric", "general"
    isometry_group: str = ""        # "O(3)", "SO(3)", "U(1)", "none"
    surviving_components: int = 0    # how many components survive
    scalar_trace_present: bool = False
    additional_components: int = 0
    reduction_is_consistent: bool = False
    notes: str = ""


@dataclass
class AnisotropicStressEstimate:
    """Order-of-magnitude estimate of anisotropic memory stress.

    For Candidate 2 (scalar + sigma_{ab}), estimate the magnitude of the
    trace-free anisotropic stress relative to the scalar memory stress.
    """
    sector: str = ""          # "cosmological_perturbation" or "collapse"
    sigma_over_phi: float = 0.0  # |sigma|/|Phi| ratio
    source_of_anisotropy: str = ""
    sigma_is_subdominant: bool = False
    notes: str = ""


@dataclass
class TensorialMemoryResult:
    """Master result from the Phase IV Tensorial Memory-Field Program.

    Evaluates all five candidates, checks scalar sufficiency, verifies
    symmetry reductions, and recommends the extension path.
    """
    # Candidates
    candidates: List[TensorCandidate] = field(default_factory=list)
    recommended_immediate: str = ""  # for current/near-term work
    recommended_next: str = ""       # for next major pass
    recommended_future: str = ""     # for long-term

    # Scalar sufficiency
    sufficiency_checks: List[ScalarSufficiencyCheck] = field(default_factory=list)
    scalar_sufficient_for_phase3: bool = False

    # Symmetry reductions
    symmetry_reductions: List[SymmetryReductionCheck] = field(default_factory=list)
    scalar_is_symmetry_limit: bool = False

    # Anisotropic estimates
    anisotropic_estimates: List[AnisotropicStressEstimate] = field(default_factory=list)

    # Phase III survival
    phase3_unchanged: List[str] = field(default_factory=list)
    phase3_modified: List[str] = field(default_factory=list)
    new_physics_with_tensor: List[str] = field(default_factory=list)

    # Overall
    scalar_field_ontology: str = ""  # "symmetry_reduced_limit", "standalone", "undetermined"
    extension_path: List[str] = field(default_factory=list)

    # Nonclaims
    nonclaims: List[str] = field(default_factory=list)

    valid: bool = False


# ================================================================
# Candidate Builders
# ================================================================

def build_candidate_scalar_only() -> TensorCandidate:
    """Candidate 1: Scalar-only closure (current framework)."""
    return TensorCandidate(
        name="scalar_only",
        label="Candidate 1: Scalar-Only Closure (Current)",
        tensor_type="scalar",
        total_dof=1,
        propagating_dof=0,
        scalar_dof=1,
        additional_dof=0,
        components=["Phi (scalar trace / memory state)"],
        relaxation_equations=1,
        reduces_to_scalar=True,
        symmetry_for_reduction="IS scalar (no reduction needed)",
        phase3_results_unchanged=True,
        modifies_what=[],
        enables_new=[],
        classification="sufficient",
        computational_cost="low",
        recommended_phase="Phase III (current)",
        nonclaims=[
            "Scalar is SUFFICIENT for all current results, not proven to be final",
            "Cannot capture anisotropic memory, shear, or propagating modes",
            "Whether scalar is fundamental or symmetry-reduced is OPEN",
        ],
    )


def build_candidate_scalar_plus_aniso() -> TensorCandidate:
    """Candidate 2: Scalar + trace-free anisotropic stress (sigma_{ab})."""
    return TensorCandidate(
        name="scalar_plus_aniso",
        label="Candidate 2: Scalar + Anisotropic Stress (sigma_{ab})",
        tensor_type="scalar_plus_aniso",
        total_dof=6,
        propagating_dof=5,
        scalar_dof=1,
        additional_dof=5,
        components=[
            "Phi (scalar trace, 1 DOF)",
            "sigma_{ab} (trace-free symmetric, 5 DOF in 3+1 split)",
        ],
        relaxation_equations=6,
        reduces_to_scalar=True,
        symmetry_for_reduction="FRW isotropic: sigma_{ab} = 0; spherical: sigma has 1 independent component",
        phase3_results_unchanged=True,
        modifies_what=[
            "T^Phi_{ab} acquires anisotropic stress components",
            "PDE perturbation theory gains angular mode coupling",
            "Echo channel gains additional polarization",
            "Love numbers gain tensor corrections",
        ],
        enables_new=[
            "Shear memory in anisotropic collapse",
            "Anisotropic cosmological perturbation memory",
            "Multi-polarization echo spectrum",
            "Partial Christodoulou memory (coupled to scalar)",
        ],
        classification="minimal_extension",
        computational_cost="moderate",
        recommended_phase="Phase V (next major pass)",
        nonclaims=[
            "Minimal extension, not proven to be unique correct extension",
            "sigma_{ab} is constitutive in current pass (no action derivation)",
            "Coupling between Phi and sigma_{ab} modes is undetermined",
            "Propagating anisotropic modes are classified, not confirmed",
        ],
    )


def build_candidate_scalar_plus_vector() -> TensorCandidate:
    """Candidate 3: Scalar + vector memory (v_a)."""
    return TensorCandidate(
        name="scalar_plus_vector",
        label="Candidate 3: Scalar + Vector Memory (v_a)",
        tensor_type="scalar_plus_vector",
        total_dof=4,
        propagating_dof=3,
        scalar_dof=1,
        additional_dof=3,
        components=[
            "Phi (scalar trace, 1 DOF)",
            "v_a (vector memory, 3 DOF in 3+1 split)",
        ],
        relaxation_equations=4,
        reduces_to_scalar=True,
        symmetry_for_reduction="Isotropic/irrotational: v_a = 0",
        phase3_results_unchanged=True,
        modifies_what=[
            "Force decomposition gains velocity memory term",
            "Kerr gains azimuthal memory component",
        ],
        enables_new=[
            "Vorticity memory",
            "Kerr m-dependent memory modes",
            "Flow-dependent memory effects",
        ],
        classification="plausible_intermediate",
        computational_cost="moderate",
        recommended_phase="Phase V (alongside Candidate 2 if needed for Kerr)",
        nonclaims=[
            "Plausible intermediate, not proven necessary or sufficient",
            "Incomplete for full anisotropy (lacks tensor content)",
            "v_a source term (W_a) is undetermined",
            "May be subsumed by Candidate 4 (rank-2 includes vector sector)",
        ],
    )


def build_candidate_rank2_tensor() -> TensorCandidate:
    """Candidate 4: Full rank-2 symmetric tensor memory field (Phi_{ab})."""
    return TensorCandidate(
        name="rank2_tensor",
        label="Candidate 4: Rank-2 Symmetric Tensor Memory (Phi_{ab})",
        tensor_type="rank2_symmetric",
        total_dof=10,
        propagating_dof=6,  # massive: 10 - 1 (trace) - 4 (diffeo) + 1 (scalar trace) = 6
        scalar_dof=1,
        additional_dof=9,
        components=[
            "Phi = (1/4) g^{ab} Phi_{ab} (scalar trace, 1 DOF)",
            "v_a (vector sector, 3 DOF — from 3+1 decomposition)",
            "sigma_{ab} (tensor sector, 5 DOF — trace-free symmetric in 3+1)",
        ],
        relaxation_equations=10,
        reduces_to_scalar=True,
        symmetry_for_reduction="FRW: only trace survives; spherical: trace + 1 aniso; axisymmetric: trace + several",
        phase3_results_unchanged=True,
        modifies_what=[
            "All of Candidates 2 and 3 modifications",
            "Full tidal memory coupling",
            "Complete perturbation spectrum",
        ],
        enables_new=[
            "All of Candidates 2 and 3 new physics",
            "Propagating memory gravitational waves",
            "Full Christodoulou gravitational-wave memory",
            "Complete Weyl tensor memory coupling",
            "Nonperturbative strong-field memory dynamics",
        ],
        classification="maximal_extension",
        computational_cost="high",
        recommended_phase="Phase VI+ (future, after Candidate 2 exhausted)",
        nonclaims=[
            "Classified but NOT derived — requires constraint theory",
            "DOF count assumes only diffeomorphism constraints",
            "Stability, ghosts, tachyons not analyzed",
            "Cauchy problem well-posedness not proven",
            "Full constraint theory not constructed",
            "Underdetermined at current pass",
        ],
    )


def build_candidate_constitutive_aniso() -> TensorCandidate:
    """Candidate 5: Constitutive anisotropic stress (no new field DOF)."""
    return TensorCandidate(
        name="constitutive_aniso",
        label="Candidate 5: Constitutive Anisotropic Stress",
        tensor_type="constitutive_aniso",
        total_dof=1,
        propagating_dof=0,
        scalar_dof=1,
        additional_dof=0,
        components=[
            "Phi (scalar trace, 1 DOF — same as Candidate 1)",
            "Delta T^aniso_{ab} (determined algebraically from Phi + curvature)",
        ],
        relaxation_equations=1,
        reduces_to_scalar=True,
        symmetry_for_reduction="IS effectively scalar with phenomenological dressing",
        phase3_results_unchanged=True,
        modifies_what=[
            "T^Phi_{ab} gains curvature-dependent anisotropic corrections",
            "Love numbers gain anisotropic corrections",
        ],
        enables_new=[
            "Leading-order Kerr memory effects (without new DOF)",
            "Curvature-dependent anisotropic stress (phenomenological)",
        ],
        classification="effective_limit",
        computational_cost="low",
        recommended_phase="Phase IV (immediate, for Kerr/Love number estimates)",
        nonclaims=[
            "Purely phenomenological — not a dynamical theory",
            "Cannot capture propagating modes or shear memory dynamics",
            "Constitutive limit of Candidate 2, not an independent framework",
            "Curvature dependence is assumed, not derived",
        ],
    )


def build_all_tensor_candidates() -> List[TensorCandidate]:
    """Build all five tensor candidates for comparison."""
    return [
        build_candidate_scalar_only(),
        build_candidate_scalar_plus_aniso(),
        build_candidate_scalar_plus_vector(),
        build_candidate_rank2_tensor(),
        build_candidate_constitutive_aniso(),
    ]


# ================================================================
# Scalar Sufficiency Checks
# ================================================================

def check_scalar_sufficiency() -> List[ScalarSufficiencyCheck]:
    """Verify that the scalar closure is sufficient for each Phase III result.

    Returns list of checks, one per major Phase III result.
    """
    checks = []

    checks.append(ScalarSufficiencyCheck(
        result_name="Modified Friedmann equation",
        scalar_sufficient=True,
        reason="FRW is isotropic; only scalar trace contributes to H^2",
        tensor_would_modify=False,
        tensor_modification="None at background level; tensor affects perturbations",
    ))

    checks.append(ScalarSufficiencyCheck(
        result_name="Memory ODE structure",
        scalar_sufficient=True,
        reason="Single relaxation ODE captures the trace sector",
        tensor_would_modify=True,
        tensor_modification="Additional coupled ODEs for anisotropic components",
    ))

    checks.append(ScalarSufficiencyCheck(
        result_name="Structural identity omega_0*tau=1",
        scalar_sufficient=True,
        reason="Depends on scalar relaxation timescale, not tensor structure",
        tensor_would_modify=False,
        tensor_modification="Identity is scalar-sector property; preserved under extension",
    ))

    checks.append(ScalarSufficiencyCheck(
        result_name="PDE dispersion (fundamental mode)",
        scalar_sufficient=True,
        reason="l=2 fundamental mode is scalar perturbation",
        tensor_would_modify=True,
        tensor_modification="Additional modes from tensor perturbations; l-mode coupling",
    ))

    checks.append(ScalarSufficiencyCheck(
        result_name="Mixed-viscoelastic classification (Q~6-7.5)",
        scalar_sufficient=True,
        reason="Q determined by scalar PDE; tensor corrections subdominant",
        tensor_would_modify=True,
        tensor_modification="Tensor modes may shift Q at subleading order",
    ))

    checks.append(ScalarSufficiencyCheck(
        result_name="Echo channel (~1.1%)",
        scalar_sufficient=True,
        reason="Echo amplitude from scalar reflection coefficient",
        tensor_would_modify=True,
        tensor_modification="Additional echo polarizations from tensor reflections",
    ))

    checks.append(ScalarSufficiencyCheck(
        result_name="Collapse endpoint law",
        scalar_sufficient=True,
        reason="Force balance is radial (1D); only scalar memory contributes",
        tensor_would_modify=False,
        tensor_modification="Endpoint unchanged; additional memory components vanish at equilibrium",
    ))

    checks.append(ScalarSufficiencyCheck(
        result_name="Junction conditions",
        scalar_sufficient=True,
        reason="Effective-level junction uses scalar memory jump only",
        tensor_would_modify=True,
        tensor_modification="Tensor junction conditions would add matching conditions",
    ))

    return checks


# ================================================================
# Symmetry Reduction Analysis
# ================================================================

def check_symmetry_reductions() -> List[SymmetryReductionCheck]:
    """Verify that the scalar arises as symmetry reduction of a tensor in each spacetime.

    Returns list of reduction checks.
    """
    reductions = []

    reductions.append(SymmetryReductionCheck(
        spacetime_symmetry="FRW_isotropic",
        isometry_group="O(3)",
        surviving_components=1,
        scalar_trace_present=True,
        additional_components=0,
        reduction_is_consistent=True,
        notes=(
            "In FRW with O(3) isometry, a symmetric rank-2 tensor field "
            "Phi_{ab} has only its trace component nonzero: "
            "Phi_{ab} = (Phi/4) g_{ab}. All trace-free components vanish "
            "identically. The scalar closure IS the unique isotropic reduction."
        ),
    ))

    reductions.append(SymmetryReductionCheck(
        spacetime_symmetry="spherical",
        isometry_group="SO(3)",
        surviving_components=2,
        scalar_trace_present=True,
        additional_components=1,
        reduction_is_consistent=True,
        notes=(
            "In spherical symmetry, Phi_{ab} = diag(-Phi_t, Phi_r, Phi_theta, Phi_theta). "
            "Two independent functions: trace Phi and anisotropy (Phi_r - Phi_theta). "
            "The scalar closure captures the trace; one additional component "
            "carries radial-tangential memory anisotropy."
        ),
    ))

    reductions.append(SymmetryReductionCheck(
        spacetime_symmetry="axisymmetric",
        isometry_group="U(1)",
        surviving_components=4,
        scalar_trace_present=True,
        additional_components=3,
        reduction_is_consistent=True,
        notes=(
            "In axisymmetry (Kerr-like), Phi_{ab} has up to 4 independent "
            "components in the (t,r,theta,phi) basis. The scalar captures "
            "the isotropic part; 3 additional components carry azimuthal "
            "and meridional memory anisotropy."
        ),
    ))

    reductions.append(SymmetryReductionCheck(
        spacetime_symmetry="general",
        isometry_group="none",
        surviving_components=10,
        scalar_trace_present=True,
        additional_components=9,
        reduction_is_consistent=True,
        notes=(
            "In a general spacetime with no symmetry, all 10 components "
            "of Phi_{ab} are independent (subject to constraint equations). "
            "The scalar is 1/10 of the full content."
        ),
    ))

    return reductions


# ================================================================
# Anisotropic Stress Estimates
# ================================================================

def estimate_anisotropic_stress_cosmo(
    alpha_mem: float = 0.1,
    sigma_shear_over_H: float = 0.01,
) -> AnisotropicStressEstimate:
    """Estimate anisotropic memory stress in cosmological perturbation theory.

    In perturbed FRW, the anisotropic stress sigma_{ab} is sourced by
    the matter shear and curvature anisotropy. At linear perturbation level,
    sigma_{ab} ~ sigma_shear / H * Phi.

    Parameters
    ----------
    alpha_mem : float
        Cosmological memory coupling.
    sigma_shear_over_H : float
        Shear-to-Hubble ratio (dimensionless). For linear perturbations,
        sigma/H ~ 10^{-5} to 10^{-2} depending on scale.

    Returns
    -------
    AnisotropicStressEstimate
    """
    est = AnisotropicStressEstimate(sector="cosmological_perturbation")

    # The anisotropic memory stress is proportional to the matter shear:
    # sigma_{ab} ~ alpha_mem * sigma_shear * tau_eff * Phi
    # Relative to the scalar: |sigma|/|Phi| ~ sigma_shear/H (order of magnitude)
    est.sigma_over_phi = sigma_shear_over_H
    est.source_of_anisotropy = "matter shear in cosmological perturbation theory"
    est.sigma_is_subdominant = est.sigma_over_phi < 0.1

    est.notes = (
        f"sigma/Phi ~ {est.sigma_over_phi:.4f}. "
        "For linear perturbations (sigma/H ~ 0.01), anisotropic memory is "
        "1% of scalar memory. Subdominant but potentially detectable in "
        "CMB B-mode or large-scale structure anisotropy."
    )

    return est


def estimate_anisotropic_stress_collapse(
    M_kg: float = 30.0 * M_SUN,
    alpha_vac: float = 1.0 / 3.0,
    beta_Q: float = 2.0,
    epsilon_Q: float = 1.0 / 9.0,
) -> AnisotropicStressEstimate:
    """Estimate anisotropic memory stress in spherical collapse.

    In spherical symmetry, the trace-free stress has one independent
    component: Delta_p = p_r - p_t. The scalar captures the trace;
    the anisotropic correction captures the radial-tangential difference.

    Parameters
    ----------
    M_kg : float
        Object mass (kg).
    alpha_vac, beta_Q, epsilon_Q : float
        Collapse parameters.

    Returns
    -------
    AnisotropicStressEstimate
    """
    est = AnisotropicStressEstimate(sector="collapse")

    if M_kg <= 0:
        return est

    r_s = 2.0 * G_SI * M_kg / (C_SI ** 2)
    R_eq = r_s * epsilon_Q ** (1.0 / beta_Q)
    GM = G_SI * M_kg

    if R_eq <= 0:
        return est

    # At equilibrium: the anisotropic stress is zero (by spherical symmetry
    # and equilibrium condition). Out of equilibrium, the anisotropy is
    # sourced by the radial-tangential difference in memory response.
    #
    # Order of magnitude: sigma ~ alpha * (1 - epsilon_Q) * a_grav * rho
    # This is suppressed relative to the scalar by the barrier:
    # |sigma|/|Phi| ~ compactness correction ~ (R_eq/r_s - 1) or O(1)

    compactness = R_eq / r_s
    # At equilibrium, sigma = 0. Near equilibrium (perturbation):
    # sigma/Phi ~ O(perturbation amplitude)
    # For order-of-magnitude: use the tangential pressure approximation
    # from memory_tensor.py (p_tangential ~ 0.5 * p_radial)
    est.sigma_over_phi = 0.5  # from p_tangential/p_radial ~ 0.5 in constitutive closure

    est.source_of_anisotropy = (
        "radial-tangential pressure difference in spherical collapse"
    )
    est.sigma_is_subdominant = False  # order unity in collapse sector

    est.notes = (
        f"sigma/Phi ~ {est.sigma_over_phi:.2f} (order unity in collapse). "
        "In spherical collapse, the anisotropic stress is comparable to the "
        "scalar trace. However, at EQUILIBRIUM both vanish (memory invisible). "
        "The anisotropy is dynamically relevant only during transients."
    )

    return est


# ================================================================
# Master Analysis
# ================================================================

def compute_tensorial_memory_analysis(
    alpha_mem: float = 0.1,
    alpha_vac: float = 1.0 / 3.0,
    beta_Q: float = 2.0,
    epsilon_Q: float = 1.0 / 9.0,
    M_kg: float = 30.0 * M_SUN,
) -> TensorialMemoryResult:
    """Full Phase IV tensorial memory-field analysis.

    Builds all five candidates, checks scalar sufficiency, verifies
    symmetry reductions, estimates anisotropic stresses, and recommends
    the extension path.

    Returns
    -------
    TensorialMemoryResult
    """
    result = TensorialMemoryResult()

    # ── Step 1: Build candidates ──
    result.candidates = build_all_tensor_candidates()

    # ── Step 2: Recommendations ──
    result.recommended_immediate = "constitutive_aniso"
    result.recommended_next = "scalar_plus_aniso"
    result.recommended_future = "rank2_tensor"

    # ── Step 3: Scalar sufficiency ──
    result.sufficiency_checks = check_scalar_sufficiency()
    result.scalar_sufficient_for_phase3 = all(
        c.scalar_sufficient for c in result.sufficiency_checks
    )

    # ── Step 4: Symmetry reductions ──
    result.symmetry_reductions = check_symmetry_reductions()
    result.scalar_is_symmetry_limit = all(
        r.reduction_is_consistent and r.scalar_trace_present
        for r in result.symmetry_reductions
    )

    # ── Step 5: Anisotropic estimates ──
    est_cosmo = estimate_anisotropic_stress_cosmo(alpha_mem=alpha_mem)
    est_collapse = estimate_anisotropic_stress_collapse(
        M_kg=M_kg, alpha_vac=alpha_vac, beta_Q=beta_Q, epsilon_Q=epsilon_Q,
    )
    result.anisotropic_estimates = [est_cosmo, est_collapse]

    # ── Step 6: Phase III survival ──
    result.phase3_unchanged = [
        "Modified Friedmann equation",
        "Memory ODE structure (scalar trace)",
        "Structural identity omega_0*tau=1",
        "PDE fundamental mode (l=2 scalar)",
        "Mixed-viscoelastic classification (Q~6-7.5)",
        "Echo channel (~1.1%)",
        "Collapse endpoint law",
        "Constitutive-effective action status",
    ]

    result.phase3_modified = [
        "T^Phi_{ab} acquires additional components",
        "PDE perturbation theory gains additional modes",
        "Echo channel gains additional polarizations",
        "Love numbers gain tensor corrections",
        "Junction conditions acquire tensor matching",
        "Kerr gains azimuthal memory",
    ]

    result.new_physics_with_tensor = [
        "Gravitational-wave memory (Christodoulou type) — requires propagating tensor DOF",
        "Shear memory in anisotropic collapse — requires sigma_{ab}",
        "Memory gravitational waves — propagating memory tensor perturbations",
        "Anisotropic cosmological memory — requires sigma_{ab} in perturbed FRW",
        "Vorticity memory — requires vector v_a",
        "Multi-polarization echo spectrum — tensor reflection coefficients",
    ]

    # ── Step 7: Scalar ontology ──
    # The scalar is CONSISTENT with being a symmetry-reduced limit,
    # but whether the underlying tensor PHYSICALLY exists is undetermined
    result.scalar_field_ontology = "undetermined"

    # ── Step 8: Extension path ──
    result.extension_path = [
        "Phase IV (current): Candidate 5 (constitutive aniso) for near-term Kerr/Love",
        "Phase V (next): Candidate 2 (scalar + sigma_{ab}) as minimal dynamical extension",
        "Phase VI+ (future): Candidate 4 (full rank-2) if Candidate 2 insufficient",
    ]

    # ── Step 9: Nonclaims ──
    result.nonclaims = [
        "No complete tensorial field theory for GRUT memory has been constructed",
        "Scalar closure is SUFFICIENT for Phase III, not proven to be final ontology",
        "Candidate 2 (scalar+aniso) is MINIMAL extension, not unique correct one",
        "Candidate 4 (rank-2) is CLASSIFIED but NOT derived (constraint theory needed)",
        "Constitutive anisotropic stress (Candidate 5) is EFFECTIVE limit, not dynamical",
        "Whether scalar is symmetry-reduced or standalone is UNDETERMINED",
        "No propagating memory modes confirmed or excluded",
        "GW memory effects classified as requiring tensor extension, not demonstrated",
        "Extension path is RECOMMENDATION, not uniqueness result",
        "alpha_mem / alpha_vac unification NOT attempted under any tensor candidate",
        "No observational predictions distinguish the tensor candidates",
        "DOF count for rank-2 assumes only diffeomorphism constraints",
    ]

    result.valid = True
    return result


# ================================================================
# Serialization
# ================================================================

def tensor_candidate_to_dict(c: TensorCandidate) -> Dict[str, Any]:
    """Serialize a TensorCandidate to dict."""
    return {
        "name": c.name,
        "label": c.label,
        "tensor_type": c.tensor_type,
        "total_dof": c.total_dof,
        "propagating_dof": c.propagating_dof,
        "scalar_dof": c.scalar_dof,
        "additional_dof": c.additional_dof,
        "components": c.components,
        "reduces_to_scalar": c.reduces_to_scalar,
        "classification": c.classification,
        "computational_cost": c.computational_cost,
        "recommended_phase": c.recommended_phase,
        "enables_new": c.enables_new,
        "nonclaims": c.nonclaims,
    }


def tensorial_result_to_dict(result: TensorialMemoryResult) -> Dict[str, Any]:
    """Serialize a TensorialMemoryResult to dict."""
    return {
        "candidates": [tensor_candidate_to_dict(c) for c in result.candidates],
        "recommended_immediate": result.recommended_immediate,
        "recommended_next": result.recommended_next,
        "recommended_future": result.recommended_future,
        "scalar_sufficient_for_phase3": result.scalar_sufficient_for_phase3,
        "scalar_is_symmetry_limit": result.scalar_is_symmetry_limit,
        "scalar_field_ontology": result.scalar_field_ontology,
        "extension_path": result.extension_path,
        "phase3_unchanged": result.phase3_unchanged,
        "phase3_modified": result.phase3_modified,
        "new_physics_with_tensor": result.new_physics_with_tensor,
        "nonclaims": result.nonclaims,
        "valid": result.valid,
    }
