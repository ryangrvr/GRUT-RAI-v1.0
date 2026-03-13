"""Final observable closure: Love numbers, Kerr, nonlinear coupling, detectability.

Phase III Package C: closes the remaining major observable channels and
provides a detector-relevance summary.

STATUS: FIRST-PASS ESTIMATES — order-of-magnitude bounds
NOT full perturbation theory calculations. Kerr and nonlinear coupling
are bounded parametric estimates, not complete solutions.

KEY RESULTS:
- Tidal Love numbers: k₂ ~ O(0.01) for reflecting BDCC at R_eq = r_s/3.
  Non-null but suppressed by potential barrier transmission |T|² ≈ 0.04.
  This is a POTENTIAL NON-NULL CHANNEL distinct from echoes.
- Kerr: echo delay reduced by spin (shorter path); QNM frequencies shift;
  structural identity ω₀τ=1 must be re-verified for spinning case.
  Full solution requires Boyer-Lindquist interior — NOT attempted.
- Nonlinear coupling: Q correction ΔQ/Q ~ O((δR/R_eq)²). For small
  perturbations (δR/R_eq << 1), universal Q=6 is robust. Breaks down
  for merger-level perturbations.
- Detectability: echoes marginal for current LIGO (O4); within reach of
  ET/CE (3G detectors). Love numbers potentially constrainable with
  high-SNR events. Kerr effects enter at O(a/M) correction level.

NONCLAIMS:
- All estimates are ORDER OF MAGNITUDE — not precision calculations
- Love number is an upper bound assuming perfect reflection at zero frequency
- Kerr extension is a parametric scaling, not a solution
- Nonlinear estimate assumes weak coupling; breaks down near merger
- Detector thresholds are approximate; depend on noise model and analysis pipeline
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any

G_SI = 6.674e-11
C_SI = 299_792_458.0
M_SUN = 1.989e30


# ================================================================
# Data Structures
# ================================================================

@dataclass
class TidalLoveResult:
    """Tidal Love number estimate for the GRUT BDCC.

    For a GR black hole: k₂ = 0 (exactly).
    For a compact object with reflecting boundary at R_eq: k₂ ≠ 0.

    The Love number is suppressed by the potential barrier transmission
    coefficient |T|²: any tidal perturbation must cross the Schwarzschild
    potential barrier twice (in and out) to produce a non-zero response.
    """
    # Setup
    R_eq_over_r_s: float = 0.0
    compactness: float = 0.0

    # Potential barrier
    transmission_sq: float = 0.0    # |T|² through potential peak
    r_surface: float = 0.0         # reflection coefficient at R_eq

    # Love number estimate
    k2_estimate: float = 0.0       # dimensionless l=2 Love number
    k2_upper_bound: float = 0.0    # upper bound (perfect reflection)
    Lambda_tidal: float = 0.0       # dimensionless tidal deformability

    # Comparison
    k2_GR_BH: float = 0.0          # GR black hole: exactly 0
    k2_neutron_star_range: str = "0.01 – 0.15"

    # Status
    channel_type: str = ""          # "null", "candidate_non_null", "underdetermined"
    notes: List[str] = field(default_factory=list)
    nonclaims: List[str] = field(default_factory=list)
    valid: bool = False


@dataclass
class KerrEstimate:
    """Bounded first-pass estimate of Kerr / spin corrections.

    The Kerr extension modifies:
    - Horizon location: r_+ = M + √(M² − a²)
    - QNM frequencies: ω_QNM(a) (spin-dependent)
    - Echo delay: modified by Kerr geometry
    - ISCO: r_ISCO(a) (spin-dependent)
    - Structural identity: ω₀τ=1 needs re-verification

    This is a PARAMETRIC ESTIMATE, not a full solution.
    """
    # Spin parameter
    a_over_M: float = 0.0           # dimensionless spin

    # Horizon
    r_plus_over_M: float = 0.0     # outer horizon / M
    r_minus_over_M: float = 0.0    # inner horizon / M

    # Echo delay modification
    echo_delay_ratio: float = 0.0   # Δt(a) / Δt(0)

    # QNM modification
    omega_QNM_ratio: float = 0.0    # ω_QNM(a) / ω_QNM(0)

    # ISCO modification
    r_ISCO_over_M: float = 0.0

    # Structural identity
    identity_preserved: str = ""    # "likely", "needs_verification", "expected_broken"

    status: str = ""
    nonclaims: List[str] = field(default_factory=list)
    valid: bool = False


@dataclass
class NonlinearEstimate:
    """First-pass estimate of nonlinear mode coupling.

    The current PDE is linearised. Nonlinear corrections enter at
    quadratic order in the perturbation amplitude δR/R_eq.
    """
    # Perturbation amplitude
    delta_R_over_R_eq: float = 0.0

    # Quadratic correction to Q
    delta_Q_over_Q: float = 0.0
    Q_linear: float = 6.0
    Q_corrected: float = 0.0

    # Energy transfer between modes
    energy_transfer_fraction: float = 0.0

    # Validity range
    linear_regime_valid: bool = False
    breakdown_amplitude: float = 0.0    # δR/R_eq at which nonlinear ~ linear

    status: str = ""
    nonclaims: List[str] = field(default_factory=list)
    valid: bool = False


@dataclass
class DetectabilitySummary:
    """Detector relevance summary for GRUT observable channels."""

    @dataclass
    class ChannelAssessment:
        channel: str = ""
        amplitude: str = ""
        detector_current: str = ""      # LIGO O4/O5
        detector_3G: str = ""           # ET, CE
        detector_space: str = ""        # LISA
        status: str = ""                # "marginal", "detectable", "null", "underdetermined"

    channels: List[ChannelAssessment] = field(default_factory=list)
    falsification_summary: str = ""
    nonclaims: List[str] = field(default_factory=list)


@dataclass
class PackageCResult:
    """Master result for Package C: Final Observable Closure."""
    love_numbers: TidalLoveResult = field(default_factory=TidalLoveResult)
    kerr_estimates: List[KerrEstimate] = field(default_factory=list)
    nonlinear: NonlinearEstimate = field(default_factory=NonlinearEstimate)
    detectability: DetectabilitySummary = field(default_factory=DetectabilitySummary)
    nonclaims: List[str] = field(default_factory=list)
    valid: bool = False


# ================================================================
# Tidal Love Numbers
# ================================================================

def compute_tidal_love_numbers(
    M_kg: float = 30.0 * M_SUN,
    alpha_vac: float = 1.0 / 3.0,
    beta_Q: float = 2.0,
    epsilon_Q: float = 1.0 / 9.0,
    r_pde_amp: float = 0.303,
) -> TidalLoveResult:
    """Estimate l=2 tidal Love number for the GRUT BDCC.

    For a compact object with a reflecting boundary at R_eq = r_s/3
    (inside the would-be horizon), the tidal Love number k₂ is non-zero
    but suppressed by the potential barrier.

    The estimate follows the ECO (exotic compact object) framework:
        k₂ ~ |T|² × r_surface × geometric_factor

    where |T|² is the transmission through the Schwarzschild potential
    barrier at the light ring, and r_surface is the BDCC reflection
    coefficient.

    For ultra-compact objects with R < r_s, the zero-frequency limit
    is subtle (r is timelike inside the horizon), so the Love number
    is understood as the low-frequency tidal response.

    Parameters
    ----------
    M_kg : float
        Object mass (kg).
    r_pde_amp : float
        PDE reflection coefficient at R_eq.

    Returns
    -------
    TidalLoveResult
    """
    tlr = TidalLoveResult()

    if M_kg <= 0:
        return tlr

    r_s = 2.0 * G_SI * M_kg / (C_SI ** 2)
    R_eq = r_s * epsilon_Q ** (1.0 / beta_Q) if epsilon_Q > 0 and beta_Q > 0 else r_s

    tlr.R_eq_over_r_s = R_eq / r_s if r_s > 0 else 0.0
    tlr.compactness = r_s / (2.0 * R_eq) if R_eq > 0 else 0.0

    # ── Potential barrier transmission ──
    # For Schwarzschild, the l=2 potential barrier peak is at r ≈ 3M = 3r_s/2.
    # The transmission coefficient for low-frequency waves:
    # |T|² ≈ exp(−2π ω Δr*/c) for ω → 0, but for the tidal Love number
    # we need the static (ω→0) response.
    #
    # For ECOs at R_eq < r_s, the standard result is:
    # |T|² ~ (echo_amplitude / r_surface)^2 for the roundtrip
    # From the echo analysis: A_echo/A_QNM ≈ 1.1%, and this includes
    # one transmission |T|² and one reflection r_surface.
    # So: |T|² × r_surface ≈ 0.011 → |T|² ≈ 0.011 / r_surface
    echo_fraction = 0.011  # ~1.1% echo amplitude
    tlr.r_surface = r_pde_amp
    tlr.transmission_sq = (echo_fraction / r_pde_amp) ** 2 if r_pde_amp > 0 else 0.0
    # More conservative: |T|² from the single-pass barrier penetration
    # |T|² ≈ echo_fraction / r_surface ≈ 0.037
    T_sq_single = echo_fraction / r_pde_amp if r_pde_amp > 0 else 0.0
    tlr.transmission_sq = T_sq_single  # single-pass transmission

    # ── Love number estimate ──
    # k₂ ~ |T|² × r_surface × C^5 × geometric_correction
    # For the static tidal response, the roundtrip matters:
    # k₂ ~ |T|² × r_surface × O(1)
    # Upper bound: perfect reflection (r_surface = 1)
    tlr.k2_upper_bound = tlr.transmission_sq * 1.0  # upper bound
    # Realistic: with PDE reflection coefficient
    tlr.k2_estimate = tlr.transmission_sq * r_pde_amp

    # ── Tidal deformability ──
    # Λ = (2/3) k₂ / C^5 where C = M/R = r_s/(2R)
    C_param = tlr.compactness
    if C_param > 0:
        tlr.Lambda_tidal = (2.0 / 3.0) * tlr.k2_estimate / (C_param ** 5)
    else:
        tlr.Lambda_tidal = 0.0

    # ── GR comparison ──
    tlr.k2_GR_BH = 0.0

    # ── Channel type ──
    if tlr.k2_estimate > 1e-6:
        tlr.channel_type = "candidate_non_null"
    else:
        tlr.channel_type = "underdetermined"

    tlr.notes = [
        f"k₂ ≈ {tlr.k2_estimate:.4f} (order-of-magnitude estimate)",
        f"k₂ upper bound ≈ {tlr.k2_upper_bound:.4f} (perfect reflection)",
        f"|T|² ≈ {tlr.transmission_sq:.4f} (barrier transmission)",
        f"Λ ≈ {tlr.Lambda_tidal:.4f} (tidal deformability)",
        "GR black hole: k₂ = 0 exactly",
        f"Neutron stars: k₂ ~ {tlr.k2_neutron_star_range}",
    ]

    tlr.nonclaims = [
        "Love number is an ORDER-OF-MAGNITUDE estimate, not perturbation theory",
        "Zero-frequency limit is subtle for R_eq < r_s (r is timelike inside horizon)",
        "k₂ understood as low-frequency tidal response, not strictly static",
        "Upper bound assumes perfect reflection; actual value depends on frequency",
        "Λ_tidal depends on compactness convention and reflection model",
        "Full calculation requires Zerilli equation with GRUT boundary conditions",
    ]

    tlr.valid = True
    return tlr


# ================================================================
# Kerr / Spin Extension
# ================================================================

def estimate_kerr_correction(a_over_M: float = 0.7) -> KerrEstimate:
    """Bounded first-pass estimate of Kerr / spin corrections.

    For a Kerr black hole with dimensionless spin a/M:
    - Outer horizon: r_+ = M(1 + √(1 − (a/M)²))
    - ISCO (prograde): decreases with spin
    - QNM frequencies: increase with spin for prograde modes
    - Echo delay: decreases (shorter cavity between R_eq and potential barrier)

    This is a PARAMETRIC ESTIMATE. Full Kerr interior requires Boyer-Lindquist
    coordinates and is NOT attempted.

    Parameters
    ----------
    a_over_M : float
        Dimensionless spin parameter (0 ≤ a/M < 1).

    Returns
    -------
    KerrEstimate
    """
    ke = KerrEstimate()

    chi = min(abs(a_over_M), 0.999)  # cap below extremal
    ke.a_over_M = chi

    # ── Horizon ──
    # r_± = M(1 ± √(1 − χ²))  [in units of M]
    sqrt_term = math.sqrt(1.0 - chi ** 2)
    ke.r_plus_over_M = 1.0 + sqrt_term   # outer horizon
    ke.r_minus_over_M = 1.0 - sqrt_term   # inner (Cauchy) horizon

    # ── Echo delay ──
    # The echo cavity is between R_eq and the light ring.
    # For Kerr, the light ring (prograde) moves inward:
    # r_LR ≈ 2M(1 + cos(2arccos(−χ)/3)) for prograde
    # Simplified: r_LR/M ≈ 3 for χ=0, → 1 for χ→1
    # Echo delay scales roughly as (r_LR − R_eq) → shorter for higher spin
    r_LR_schw = 3.0  # in units of M, Schwarzschild
    # Approximate prograde light ring for Kerr:
    r_LR_kerr = 2.0 * (1.0 + math.cos(2.0 * math.acos(-chi) / 3.0))
    ke.echo_delay_ratio = r_LR_kerr / r_LR_schw if r_LR_schw > 0 else 1.0

    # ── QNM frequency ──
    # ω_QNM ≈ ω_QNM(0) × (1 + c₁ χ + c₂ χ²)
    # For l=2, m=2 (dominant mode): c₁ ≈ 0.29, c₂ ≈ 0.19
    # (from fit to Kerr QNM tables)
    c1, c2 = 0.29, 0.19
    ke.omega_QNM_ratio = 1.0 + c1 * chi + c2 * chi ** 2

    # ── ISCO ──
    # Prograde ISCO for Kerr (exact formula):
    z1 = 1.0 + (1.0 - chi ** 2) ** (1.0 / 3.0) * (
        (1.0 + chi) ** (1.0 / 3.0) + (1.0 - chi) ** (1.0 / 3.0)
    )
    z2 = math.sqrt(3.0 * chi ** 2 + z1 ** 2)
    ke.r_ISCO_over_M = 3.0 + z2 - math.sqrt((3.0 - z1) * (3.0 + z1 + 2.0 * z2))

    # ── Structural identity ──
    # ω₀τ = 1 was derived for Schwarzschild. For Kerr:
    # ω₀ depends on the effective potential near R_eq, which is spin-modified
    # τ_local depends on the local dynamical timescale, also spin-modified
    # At leading order, both scale the same way → identity likely preserved
    # But this needs explicit verification.
    if chi < 0.3:
        ke.identity_preserved = "likely_preserved_low_spin"
    elif chi < 0.7:
        ke.identity_preserved = "needs_verification"
    else:
        ke.identity_preserved = "needs_verification_high_spin"

    ke.status = "parametric_estimate"
    ke.nonclaims = [
        "This is a PARAMETRIC ESTIMATE, not a full Kerr solution",
        "Boyer-Lindquist interior with memory field NOT attempted",
        "R_eq(a) scaling with spin NOT derived — assumed same R_eq/r_+ ratio",
        "Echo delay ratio is approximate (prograde light ring used)",
        "QNM frequency ratio from empirical fit, not GRUT-specific calculation",
        "ISCO formula is exact GR but does not include GRUT memory corrections",
        "Structural identity ω₀τ=1 NOT verified for spinning case",
        "Superradiance and ergoregion effects NOT considered",
    ]
    ke.valid = True
    return ke


# ================================================================
# Nonlinear Mode Coupling
# ================================================================

def estimate_nonlinear_coupling(
    delta_R_over_R_eq: float = 0.01,
    Q_linear: float = 6.0,
    beta_Q: float = 2.0,
) -> NonlinearEstimate:
    """First-pass estimate of nonlinear mode coupling effects.

    The current PDE is linearised around the BDCC equilibrium. Nonlinear
    corrections enter at quadratic order in the perturbation amplitude.

    The force balance F(R) = a_inward(R) − a_Q(R) has nonlinear terms:
        F(R_eq + δR) = F(R_eq) + F'(R_eq)δR + ½F''(R_eq)δR² + ...

    The linearised eigenfrequency ω₀² = −F'(R_eq)/R_eq gives the linear PDE.
    The quadratic correction modifies Q:
        ΔQ/Q ~ c₂ × (δR/R_eq)²

    where c₂ depends on F''(R_eq) / F'(R_eq).

    Parameters
    ----------
    delta_R_over_R_eq : float
        Fractional perturbation amplitude.
    Q_linear : float
        Linear Q factor.
    beta_Q : float
        Barrier exponent.

    Returns
    -------
    NonlinearEstimate
    """
    ne = NonlinearEstimate()

    eps = delta_R_over_R_eq
    ne.delta_R_over_R_eq = eps
    ne.Q_linear = Q_linear

    # ── Quadratic correction coefficient ──
    # The barrier force a_Q ∝ (r_s/R)^β_Q has nonlinear structure:
    # a_Q(R_eq + δR) = a_Q(R_eq) × (1 − β_Q δR/R_eq + β_Q(β_Q+1)/2 (δR/R_eq)² + ...)
    # The quadratic correction to the effective potential:
    # c₂ ~ β_Q(β_Q + 1) / 2 = 2(3)/2 = 3 for β_Q = 2
    c2 = beta_Q * (beta_Q + 1.0) / 2.0

    # ── Q correction ──
    # ΔQ/Q ~ c₂ × ε² (leading nonlinear correction)
    ne.delta_Q_over_Q = c2 * eps ** 2
    ne.Q_corrected = Q_linear * (1.0 + ne.delta_Q_over_Q)

    # ── Energy transfer ──
    # Quadratic coupling transfers energy from fundamental to first overtone
    # Energy fraction ~ c₂ × ε² × (coupling overlap integral)
    ne.energy_transfer_fraction = c2 * eps ** 2 * 0.5  # O(1) overlap integral

    # ── Validity ──
    # Linear regime valid when c₂ × ε² << 1
    ne.linear_regime_valid = (c2 * eps ** 2) < 0.1
    # Breakdown amplitude: c₂ × ε² ~ 1 → ε ~ 1/√c₂
    ne.breakdown_amplitude = 1.0 / math.sqrt(c2) if c2 > 0 else float("inf")

    ne.status = "bounded_first_pass"
    ne.nonclaims = [
        "Nonlinear estimate is ORDER OF MAGNITUDE from force balance expansion",
        "c₂ coefficient derived from barrier force Taylor expansion",
        "Mode coupling overlap integral approximated as O(1)",
        "Linear Q=6 is ROBUST for small perturbations (ε < 0.1)",
        "Breaks down for merger-level perturbations (ε ~ 1)",
        "Multi-mode coupling (l > 2, overtone interactions) NOT computed",
        "Does NOT include nonlinear memory field effects (τ_eff variation)",
    ]
    ne.valid = True
    return ne


# ================================================================
# Detectability Summary
# ================================================================

def compute_detectability_summary(
    echo_amplitude_pct: float = 1.1,
    k2_estimate: float = 0.01,
    Q_value: float = 6.0,
) -> DetectabilitySummary:
    """Produce a detector-relevance summary for all GRUT observable channels.

    Compares the predicted signal levels against current and future
    gravitational-wave detector sensitivities.

    Parameters
    ----------
    echo_amplitude_pct : float
        Echo amplitude as percentage of QNM signal.
    k2_estimate : float
        Estimated l=2 Love number.
    Q_value : float
        Quality factor.

    Returns
    -------
    DetectabilitySummary
    """
    ds = DetectabilitySummary()
    CA = DetectabilitySummary.ChannelAssessment

    # ── Echo channel ──
    echo_channel = CA(
        channel="Ringdown echoes",
        amplitude=f"~{echo_amplitude_pct:.1f}% of QNM (mixed_viscoelastic, Q≈{Q_value:.0f})",
        detector_current=(
            "MARGINAL — echoes at ~1% require SNR > 50 in ringdown; "
            "current O4 events typically SNR ~ 10–30 in ringdown"
        ),
        detector_3G=(
            "DETECTABLE — ET/CE ringdown SNR > 100 for nearby events; "
            "~1% echoes should be resolvable with matched filtering"
        ),
        detector_space=(
            "DETECTABLE — LISA massive BH mergers (10⁶ M☉) produce "
            "echo delays of hours; high SNR expected"
        ),
        status="marginal_current__detectable_3G",
    )

    # ── Tidal Love numbers ──
    love_channel = CA(
        channel="Tidal Love numbers",
        amplitude=f"k₂ ~ {k2_estimate:.3f} (vs k₂ = 0 for GR BH)",
        detector_current=(
            "CHALLENGING — requires BH-BH events with measurable tidal effects; "
            "current constraints: Λ < O(100) for BH-BH, far above GRUT prediction"
        ),
        detector_3G=(
            "POTENTIALLY CONSTRAINABLE — ET/CE could constrain Λ ~ O(1) for "
            "high-mass-ratio events with SNR > 200"
        ),
        detector_space="NOT DIRECTLY APPLICABLE — LISA band too low for tidal effects in inspiral",
        status="underdetermined_current__potentially_constrainable_3G",
    )

    # ── Static observables (null) ──
    null_channel = CA(
        channel="Shadow / photon sphere / ISCO",
        amplitude="IDENTICALLY NULL (Schwarzschild exterior at leading order)",
        detector_current="NULL — no deviation from GR expected",
        detector_3G="NULL — no deviation from GR expected",
        detector_space="NULL — no deviation from GR expected",
        status="null",
    )

    # ── Spin-dependent effects ──
    spin_channel = CA(
        channel="Spin-dependent echo modifications",
        amplitude="O(a/M) corrections to echo delay and amplitude",
        detector_current=(
            "NOT DISTINGUISHABLE — spin corrections subdominant to "
            "echo detection threshold"
        ),
        detector_3G=(
            "POTENTIALLY MEASURABLE — if echoes detected, spin dependence "
            "would test framework consistency"
        ),
        detector_space="RELEVANT — LISA massive BH remnants have well-measured spin",
        status="underdetermined",
    )

    ds.channels = [echo_channel, love_channel, null_channel, spin_channel]

    ds.falsification_summary = (
        "The GRUT BDCC framework has three falsification pathways:\n\n"
        "1. ECHO NON-DETECTION at 3G sensitivity: If ET/CE observe high-SNR "
        "ringdowns with NO echoes at the ~0.1% level, the mixed_viscoelastic "
        "BDCC at R_eq = r_s/3 with current parameters would be excluded "
        "(but Boltzmann model remains viable).\n\n"
        "2. LOVE NUMBER MEASUREMENT: If BH-BH tidal deformability is measured "
        "at Λ = 0 to high precision, the reflecting BDCC would be constrained "
        "(but frequency-dependent reflection could evade static TLN bounds).\n\n"
        "3. ECHO DETECTION with wrong parameters: If echoes are detected at "
        "amplitudes or delays inconsistent with the predicted ~1.1% and "
        "Δt ~ 0.52 ms × (M/30M☉), the specific GRUT parameter values would "
        "be falsified (not the framework itself)."
    )

    ds.nonclaims = [
        "Detectability estimates are APPROXIMATE — depend on noise model and pipeline",
        "Echo SNR threshold depends on ringdown SNR, NOT on inspiral SNR",
        "Love number constrainability is speculative for BH-BH events",
        "Static null channels (shadow etc.) are NOT falsification targets",
        "Spin corrections are parametric estimates, NOT GRUT-specific calculations",
        "Boltzmann model (r ≈ 0, no echoes) remains viable and NOT excluded",
        "No claim that current or future data WILL detect GRUT signatures",
        "Falsification pathways are conditional on Schwarzschild-like exterior",
    ]

    return ds


# ================================================================
# Master Package C Analysis
# ================================================================

def compute_package_c_analysis(
    M_kg: float = 30.0 * M_SUN,
    alpha_vac: float = 1.0 / 3.0,
    beta_Q: float = 2.0,
    epsilon_Q: float = 1.0 / 9.0,
    r_pde_amp: float = 0.303,
) -> PackageCResult:
    """Full Package C analysis: Love numbers, Kerr, nonlinear, detectability."""
    result = PackageCResult()

    # ── Tidal Love numbers ──
    result.love_numbers = compute_tidal_love_numbers(
        M_kg, alpha_vac, beta_Q, epsilon_Q, r_pde_amp
    )

    # ── Kerr estimates at representative spins ──
    for chi in [0.0, 0.3, 0.7, 0.9]:
        result.kerr_estimates.append(estimate_kerr_correction(chi))

    # ── Nonlinear coupling at representative amplitudes ──
    result.nonlinear = estimate_nonlinear_coupling(
        delta_R_over_R_eq=0.01, Q_linear=6.0, beta_Q=beta_Q
    )

    # ── Detectability ──
    result.detectability = compute_detectability_summary(
        echo_amplitude_pct=1.1,
        k2_estimate=result.love_numbers.k2_estimate,
        Q_value=6.0,
    )

    result.nonclaims = [
        "All estimates are ORDER OF MAGNITUDE — not precision calculations",
        "Love number is suppressed by potential barrier; exact value needs Zerilli equation",
        "Kerr extension is PARAMETRIC, not a full Boyer-Lindquist solution",
        "Nonlinear estimate valid for small perturbations only (δR/R_eq << 1)",
        "Detectability depends on analysis pipeline, not just signal amplitude",
        "Boltzmann model (r ≈ 0) remains viable; no echo detection is also consistent",
        "Static channels (shadow, ISCO) are IDENTICALLY NULL — not falsification targets",
        "Tidal Love numbers are a CANDIDATE non-null channel, not a prediction",
    ]

    result.valid = (
        result.love_numbers.valid
        and all(ke.valid for ke in result.kerr_estimates)
        and result.nonlinear.valid
    )

    return result


# ================================================================
# Serialization
# ================================================================

def love_to_dict(tlr: TidalLoveResult) -> Dict[str, Any]:
    return {
        "k2_estimate": tlr.k2_estimate,
        "k2_upper_bound": tlr.k2_upper_bound,
        "Lambda_tidal": tlr.Lambda_tidal,
        "transmission_sq": tlr.transmission_sq,
        "r_surface": tlr.r_surface,
        "channel_type": tlr.channel_type,
        "notes": tlr.notes,
        "nonclaims": tlr.nonclaims,
        "valid": tlr.valid,
    }


def package_c_to_dict(r: PackageCResult) -> Dict[str, Any]:
    return {
        "love_numbers": love_to_dict(r.love_numbers),
        "kerr_estimates": [
            {"a_over_M": ke.a_over_M, "echo_delay_ratio": ke.echo_delay_ratio,
             "identity_preserved": ke.identity_preserved, "status": ke.status}
            for ke in r.kerr_estimates
        ],
        "nonlinear": {
            "delta_Q_over_Q": r.nonlinear.delta_Q_over_Q,
            "Q_corrected": r.nonlinear.Q_corrected,
            "linear_regime_valid": r.nonlinear.linear_regime_valid,
            "breakdown_amplitude": r.nonlinear.breakdown_amplitude,
        },
        "falsification_summary": r.detectability.falsification_summary,
        "nonclaims": r.nonclaims,
        "valid": r.valid,
    }
