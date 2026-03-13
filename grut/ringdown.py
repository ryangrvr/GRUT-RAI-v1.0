"""Ringdown / echo falsifier module — Phase III-C WP2.

Computes echo time delays, amplitudes, and transfer functions for a
Barrier-Dominated Compact Core at R_eq under a Schwarzschild-like exterior.

STATUS: ACTIVE / RESEARCH TARGET
EXTERIOR ASSUMPTION: All results computed under Schwarzschild-like exterior
    (WP1 conditional assessment). If the exterior assessment changes, all
    results must be recomputed.

WHAT THIS MODULE COMPUTES:
- Echo time delay from R_eq and r_s (order of magnitude)
- Natural oscillation frequency of BDCC from stability eigenvalue
- Parameterized echo amplitudes for given reflection coefficient
- Comparison with standard GR (no echoes)

WHAT THIS MODULE DOES NOT COMPUTE:
- Reflection coefficient from first principles (requires interior metric)
- Full QNM spectrum (requires numerical relativity)
- Kerr generalization (non-rotating only)
- Interior effective potential from covariant treatment

NONCLAIMS:
- Echoes are NOT predicted to exist. The module computes what they WOULD
  look like under parameterized assumptions.
- The echo time delay is an ORDER OF MAGNITUDE estimate.
- No specific reflection coefficient is derived from GRUT structure.
- All results are CONDITIONAL on the WP1 exterior assessment.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Physical constants (SI)
G_SI = 6.674e-11          # m^3 kg^-1 s^-2
C_SI = 299_792_458.0      # m/s
M_SUN = 1.989e30          # kg


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class EchoParameters:
    """Input parameters for echo computation.

    All quantities in SI unless otherwise noted.
    """
    # Black hole parameters
    M_kg: float = 0.0           # Total mass (kg)
    r_s_m: float = 0.0          # Schwarzschild radius (m)

    # Interior endpoint (from collapse solver)
    R_eq_m: float = 0.0         # Endpoint radius (m)
    R_eq_over_r_s: float = 0.0  # Dimensionless endpoint radius
    compactness: float = 0.0    # C = r_s / R_eq

    # Stability (from solver)
    stability_eigenvalue: float = 0.0  # d(a_net)/dR at R_eq (1/s^2 per m)
    beta_Q: float = 2.0
    epsilon_Q: float = 0.0

    # Boundary condition model
    reflection_model: str = "constant"
    # "constant"   — r_surface_amp = reflection_coefficient for all ω
    # "boltzmann"  — r_surface_amp = exp(-ω / ω_core)
    # "perfect"    — r_surface_amp = 1.0
    # "impedance"  — r_surface_amp from acoustic impedance mismatch at BDCC
    #                (mass-dependent, sharp-boundary approximation)
    # "interior"   — r_surface_amp from interior wave analysis (WP2C)
    #                incorporates Q-dependent correction to impedance model
    # "graded"     — r_surface_amp from graded-transition model (WP2D)
    #                replaces sharp boundary with smooth Phi(R) profile
    #                and includes multi-mode interior correction

    reflection_coefficient: float = 1.0
    # Used when reflection_model = "constant". Range [0, 1].
    # 0 = standard GR (no echoes). 1 = perfect reflection (upper bound).
    # NOTE: All reflection coefficients in this module are AMPLITUDE
    # coefficients (not power). Power reflectivity = r_amp^2.


@dataclass
class EchoResult:
    """Results of echo computation.

    All results are CONDITIONAL on the Schwarzschild-like exterior
    assumption from WP1. If that assumption changes, these results
    are invalidated.
    """
    # Echo timing
    r_star_eq: float = 0.0          # Tortoise coordinate at R_eq (m)
    r_star_peak: float = 0.0        # Tortoise coordinate at potential peak (m)
    delta_t_echo_s: float = 0.0     # Echo time delay (s)
    delta_t_echo_over_r_s: float = 0.0  # Dimensionless echo delay

    # BDCC oscillation
    omega_core_rad_s: float = 0.0   # Natural frequency of BDCC (rad/s)
    f_core_Hz: float = 0.0          # Natural frequency (Hz)

    # Echo amplitudes (first N echoes)
    n_echoes: int = 0
    echo_amplitudes: List[float] = field(default_factory=list)
    # A_n / A_0 for n = 1, 2, ..., n_echoes

    # Transfer function parameters
    # NOTE: reflection coefficients are AMPLITUDE unless explicitly "_pow"
    transmission_squared: float = 0.0  # |T|^2 (power) through potential peak
    reflection_peak: float = 0.0       # r_peak_amp: amplitude reflection at peak (from inside)
    reflection_surface: float = 0.0    # r_surface_amp: amplitude reflection at BDCC

    # Impedance model (WP2B)
    impedance_ratio_eta: float = 0.0   # η = c_s(BDCC) / c (dimensionless)
    # η << 1: soft boundary relative to background. Both η→0 and η→∞ give
    # high reflection. Only η≈1 (impedance matched) gives low reflection.
    # NOTE: This is a sharp-boundary approximation. The Phase III-B
    # transition has finite width; transition-width corrections remain open.

    # Interior wave model (WP2C)
    interior_quality_factor_Q: float = 0.0  # Q = omega_core / (2*gamma_eff)
    # Q >> 1: reactive (high reflection), Q << 1: dissipative (low reflection)
    interior_response_class: str = ""       # reactive / mixed_viscoelastic / dissipative / underdetermined

    # PDE-informed model (interior PDE closure)
    pde_Q: float = 0.0                     # Q from PDE dispersion relation
    pde_gamma: float = 0.0                 # PDE-derived damping rate (rad/s)
    pde_omega_eff: float = 0.0             # PDE effective restoring frequency (rad/s)
    pde_r_amp: float = 0.0                 # PDE-informed reflection amplitude
    pde_response_class: str = ""           # reactive / mixed_viscoelastic / dissipative
    pde_proxy_agreement: str = ""          # confirmed / modified / contradicted
    pde_echo_impact: str = ""              # strengthened / preserved / weakened / collapsed

    # Covariant ansatz model (final closure)
    cov_Q: float = 0.0                     # Q from covariant analysis
    cov_r_amp: float = 0.0                 # Covariant reflection amplitude
    cov_response_class: str = ""           # Response classification
    cov_echo_pct: float = 0.0             # Covariant echo amplitude (%)
    cov_pde_agreement: str = ""           # confirmed / modified / contradicted
    cov_identity_preserved: bool = False   # omega_0*tau=1 preserved?

    # Graded-transition model (WP2D)
    graded_r_amp: float = 0.0              # Graded-transition reflectivity
    graded_grading_factor: float = 0.0     # r_graded / r_sharp (< 1 means suppression)
    graded_multimode_factor: float = 0.0   # Multi-mode correction factor
    graded_combined_factor: float = 0.0    # Total WP2D correction factor
    graded_lambda_over_width: float = 0.0  # Probe wavelength / transition width
    graded_echo_channel_status: str = ""   # strengthened / weakened_modestly / weakened_significantly / collapsed

    # Standard GR comparison
    omega_qnm_rad_s: float = 0.0    # Fundamental l=2 QNM frequency (rad/s)
    tau_qnm_s: float = 0.0          # QNM damping time (s)
    f_qnm_Hz: float = 0.0           # QNM frequency (Hz)

    # Status
    exterior_assumption: str = "schwarzschild_like"
    confidence: str = "order_of_magnitude"
    # "order_of_magnitude" — echo delay and amplitudes are estimates
    # "parameterized" — parameterized but not derived
    # "computed" — derived from interior metric (future)

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


def tortoise_coordinate(r: float, r_s: float) -> float:
    """Compute Schwarzschild tortoise coordinate r*(r).

    For r > r_s (exterior): r* = r + r_s * ln(r/r_s - 1)
    For r < r_s (interior): r* = r + r_s * ln(1 - r/r_s)

    NOTE: The interior formula uses the standard Schwarzschild metric.
    The GRUT-modified interior may have a different effective metric,
    making this an ORDER OF MAGNITUDE estimate for r < r_s.

    Parameters
    ----------
    r : float
        Radial coordinate (m). Must be > 0.
    r_s : float
        Schwarzschild radius (m). Must be > 0.

    Returns
    -------
    float
        Tortoise coordinate r* (m).
    """
    if r <= 0 or r_s <= 0:
        return 0.0

    ratio = r / r_s
    if ratio > 1.0:
        # Exterior
        return r + r_s * math.log(ratio - 1.0)
    elif ratio < 1.0:
        # Interior (ORDER OF MAGNITUDE — uses standard Schwarzschild)
        return r + r_s * math.log(1.0 - ratio)
    else:
        # At horizon — diverges
        return float("-inf")


def potential_peak_radius(r_s: float) -> float:
    """Light ring radius for Schwarzschild: r_peak = (3/2) r_s."""
    return 1.5 * r_s


def echo_time_delay(R_eq_m: float, r_s_m: float) -> float:
    """Compute the echo round-trip time delay.

    Δt_echo ≈ 2 × |r*(R_eq) - r*(r_peak)|

    This is an ORDER OF MAGNITUDE estimate using the standard Schwarzschild
    tortoise coordinate. The GRUT-modified interior metric may change this.

    Parameters
    ----------
    R_eq_m : float
        Endpoint radius (m).
    r_s_m : float
        Schwarzschild radius (m).

    Returns
    -------
    float
        Echo time delay (seconds). Divide by c to get light-travel time.
    """
    r_peak = potential_peak_radius(r_s_m)
    r_star_eq = tortoise_coordinate(R_eq_m, r_s_m)
    r_star_peak = tortoise_coordinate(r_peak, r_s_m)

    # Round-trip: down to surface, back to peak
    delta_r_star = abs(r_star_eq - r_star_peak)
    return 2.0 * delta_r_star / C_SI


def bdcc_oscillation_frequency(
    M_kg: float,
    R_eq_m: float,
    beta_Q: float = 2.0,
) -> float:
    """Estimate the natural radial oscillation frequency of the BDCC.

    From the stability eigenvalue d(a_net)/dR = β_Q × GM/R_eq³,
    the effective spring constant for radial perturbations is:

        k_eff = d(a_net)/dR = β_Q × GM / R_eq³

    The oscillation frequency (for a unit mass shell) is:

        ω_core² ~ k_eff / R_eq = β_Q × GM / R_eq⁴

    This is an ORDER OF MAGNITUDE estimate. A proper perturbation theory
    calculation on the interior metric is needed for the exact value.

    Parameters
    ----------
    M_kg : float
        Black hole mass (kg).
    R_eq_m : float
        Endpoint radius (m).
    beta_Q : float
        Barrier exponent (default 2).

    Returns
    -------
    float
        Angular frequency ω_core (rad/s).
    """
    if R_eq_m <= 0 or M_kg <= 0:
        return 0.0
    k_eff = beta_Q * G_SI * M_kg / (R_eq_m ** 3)
    # Dimensional estimate: ω² ~ k_eff / R_eq
    omega_sq = k_eff / R_eq_m
    return math.sqrt(omega_sq) if omega_sq > 0 else 0.0


def impedance_ratio(
    M_kg: float,
    R_eq_m: float,
    beta_Q: float = 2.0,
) -> float:
    """Compute the acoustic impedance ratio η at the BDCC surface.

    The BDCC creates an acoustic impedance discontinuity at R_eq.
    The effective sound speed inside the BDCC is estimated as:

        c_s(BDCC) ~ ω_core × R_eq

    where ω_core is the natural radial oscillation frequency from the
    stability eigenvalue. The background propagation speed near the
    horizon is c (speed of light).

    The impedance ratio is:

        η = c_s(BDCC) / c = ω_core × R_eq / c

    This is computed NUMERICALLY from the implemented ω_core formula.
    No closed-form simplification is assumed.

    KEY PROPERTIES:
    - η << 1 for astrophysical BHs (the BDCC is much 'softer' than
      the vacuum background at QNM frequencies)
    - Under the constrained endpoint, η decreases with mass
    - Both η → 0 (soft) and η → ∞ (rigid) give high reflection
    - Only η ≈ 1 (impedance matched) gives low reflection

    SHARP-BOUNDARY APPROXIMATION: This assumes a sharp transition at
    R_eq. The Phase III-B transition has finite width (~0.7 r_s in the
    benchmark). Transition-width corrections remain open and could
    modify the effective impedance.

    Parameters
    ----------
    M_kg : float
        Black hole mass (kg).
    R_eq_m : float
        Endpoint radius (m).
    beta_Q : float
        Barrier exponent (default 2).

    Returns
    -------
    float
        Dimensionless impedance ratio η.
    """
    omega_core = bdcc_oscillation_frequency(M_kg, R_eq_m, beta_Q)
    if omega_core <= 0 or R_eq_m <= 0:
        return 0.0
    c_s_bdcc = omega_core * R_eq_m
    return c_s_bdcc / C_SI


def impedance_reflectivity(
    M_kg: float,
    R_eq_m: float,
    beta_Q: float = 2.0,
) -> float:
    """Compute the amplitude reflection coefficient from impedance mismatch.

    Uses the standard step-impedance formula for the AMPLITUDE
    reflection coefficient:

        r_surface_amp = |1 - η| / (1 + η)

    where η is the impedance ratio from impedance_ratio().

    NOTE: This is an AMPLITUDE coefficient. The power reflectivity is:

        R_surface_pow = r_surface_amp²

    The echo amplitude formula A_n/A_0 uses amplitude coefficients
    throughout, so this is directly compatible.

    PHYSICAL INTERPRETATION:
    - η << 1 (soft BDCC): r_amp → 1 − 2η (near-total reflection
      with phase flip, like a free-end reflection)
    - η >> 1 (rigid BDCC): r_amp → 1 − 2/η (near-total reflection
      without phase flip, like a fixed-end reflection)
    - η = 1 (impedance matched): r_amp = 0 (maximum transmission)

    Since η << 1 for all astrophysical BHs under the constrained
    endpoint, the impedance model yields high amplitude reflectivity.

    NONCLAIMS:
    - This is a PHYSICALLY MOTIVATED ESTIMATE, not a rigorous derivation.
    - The actual r_surface_amp requires the interior wave equation.
    - Sharp-boundary approximation: transition-width corrections open.
    - The Boltzmann model (R ≈ 0) remains viable if the BDCC is
      dissipative rather than reactive.

    Parameters
    ----------
    M_kg : float
        Black hole mass (kg).
    R_eq_m : float
        Endpoint radius (m).
    beta_Q : float
        Barrier exponent (default 2).

    Returns
    -------
    float
        Amplitude reflection coefficient r_surface_amp in [0, 1].
    """
    eta = impedance_ratio(M_kg, R_eq_m, beta_Q)
    if eta <= 0:
        return 0.0
    return abs(1.0 - eta) / (1.0 + eta)


def schwarzschild_qnm_l2(M_kg: float) -> tuple:
    """Fundamental l=2 quasinormal mode for Schwarzschild.

    Using the well-known analytic approximation:
        ω_R ≈ 0.3737 / M  (in geometric units G=c=1)
        ω_I ≈ 0.0890 / M

    Returns (omega_real_rad_s, omega_imag_rad_s, tau_damp_s, f_Hz).

    Parameters
    ----------
    M_kg : float
        Black hole mass (kg).

    Returns
    -------
    tuple
        (omega_real, omega_imag, tau_damp, f_Hz) all in SI units.
    """
    if M_kg <= 0:
        return (0.0, 0.0, 0.0, 0.0)

    # Convert to geometric time: M_geom = GM/c³ (seconds)
    M_geom = G_SI * M_kg / (C_SI ** 3)

    omega_R = 0.3737 / M_geom  # rad/s
    omega_I = 0.0890 / M_geom  # 1/s (damping rate)
    tau_damp = 1.0 / omega_I   # damping time (s)
    f_Hz = omega_R / (2.0 * math.pi)

    return (omega_R, omega_I, tau_damp, f_Hz)


def potential_peak_transmission(l: int = 2) -> tuple:
    """Approximate transmission and reflection at the Schwarzschild potential peak.

    These are ORDER OF MAGNITUDE estimates for the l=2 mode based on
    the WKB approximation of the Regge-Wheeler potential.

    The potential peak acts as a barrier:
    - Waves from outside: most reflected, some transmitted inward
    - Waves from inside: most reflected back inward, some leak out

    Returns (|T|², |R_peak|) where:
    - |T|² is the fraction of energy transmitted through the peak
    - |R_peak| is the amplitude reflection coefficient from inside

    Parameters
    ----------
    l : int
        Angular mode number (default 2).

    Returns
    -------
    tuple
        (transmission_squared, reflection_peak_amplitude)
    """
    # WKB estimates for Schwarzschild l=2 fundamental mode.
    # These are rough but capture the right order of magnitude.
    # |T|² depends on frequency relative to the potential peak.
    # Near the QNM frequency: |T|² ~ 0.01-0.05 for l=2.
    # |R_peak| ~ sqrt(1 - |T|²) ~ 0.97-0.99
    #
    # We use representative values. A proper calculation would
    # integrate through the potential barrier.
    if l == 2:
        T_sq = 0.03   # ~3% transmission
        R_peak = 0.98  # ~98% reflection from inside
    elif l == 3:
        T_sq = 0.01
        R_peak = 0.99
    else:
        # Higher l: more opaque barrier
        T_sq = 0.005
        R_peak = 0.997

    return (T_sq, R_peak)


def echo_amplitudes(
    n_echoes: int,
    transmission_sq: float,
    reflection_peak: float,
    reflection_surface: float,
) -> List[float]:
    """Compute relative amplitudes of the first N echoes.

    The nth echo amplitude relative to the main QNM signal is:

        A_n / A_0 ≈ T² × (R_surface × R_peak)^n

    where:
    - T² is the transmission through the potential peak
    - R_surface is the reflection coefficient at the BDCC
    - R_peak is the reflection coefficient at the peak (from inside)

    Parameters
    ----------
    n_echoes : int
        Number of echoes to compute.
    transmission_sq : float
        |T|² through potential peak.
    reflection_peak : float
        |R_peak| at potential peak from inside.
    reflection_surface : float
        |R_surface| at BDCC. Range [0, 1].

    Returns
    -------
    list of float
        Relative amplitudes A_n / A_0 for n = 1, ..., n_echoes.
    """
    amplitudes = []
    product = reflection_surface * reflection_peak
    for n in range(1, n_echoes + 1):
        A_n = transmission_sq * (product ** n)
        amplitudes.append(A_n)
    return amplitudes


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def compute_echo_analysis(params: EchoParameters, n_echoes: int = 5) -> EchoResult:
    """Run the full echo analysis for given parameters.

    Parameters
    ----------
    params : EchoParameters
        Input parameters including mass, endpoint, and reflection model.
    n_echoes : int
        Number of echo amplitudes to compute (default 5).

    Returns
    -------
    EchoResult
        Complete echo analysis with timing, amplitudes, and nonclaims.
    """
    r_s = params.r_s_m
    if r_s <= 0:
        r_s = schwarzschild_radius(params.M_kg)
    R_eq = params.R_eq_m
    if R_eq <= 0 and params.R_eq_over_r_s > 0:
        R_eq = params.R_eq_over_r_s * r_s

    # ── Tortoise coordinates ──
    r_peak = potential_peak_radius(r_s)
    r_star_eq = tortoise_coordinate(R_eq, r_s)
    r_star_peak = tortoise_coordinate(r_peak, r_s)

    # ── Echo time delay ──
    dt_echo = echo_time_delay(R_eq, r_s)
    dt_echo_over_r_s = dt_echo * C_SI / r_s if r_s > 0 else 0.0

    # ── BDCC oscillation frequency ──
    omega_core = bdcc_oscillation_frequency(params.M_kg, R_eq, params.beta_Q)
    f_core = omega_core / (2.0 * math.pi) if omega_core > 0 else 0.0

    # ── QNM reference ──
    omega_qnm, omega_I, tau_qnm, f_qnm = schwarzschild_qnm_l2(params.M_kg)

    # ── Potential peak transmission/reflection ──
    T_sq, R_peak = potential_peak_transmission(l=2)

    # ── Impedance ratio (computed for all models) ──
    eta = impedance_ratio(params.M_kg, R_eq, params.beta_Q)

    # ── Interior wave analysis (computed for all models, WP2C) ──
    interior_Q = 0.0
    interior_cls = ""
    _iw_r = None
    try:
        from grut.interior_waves import (
            InteriorWaveParams as _IWP,
            compute_interior_wave_analysis as _ciwa,
        )
        _iw_p = _IWP(
            M_kg=params.M_kg, R_eq_m=R_eq, r_s_m=r_s,
            beta_Q=params.beta_Q, epsilon_Q=params.epsilon_Q,
        )
        _iw_r = _ciwa(_iw_p)
        interior_Q = _iw_r.quality_factor_Q
        interior_cls = _iw_r.response_class
    except Exception:
        pass  # interior_waves module not available — leave defaults

    # ── Graded-transition analysis (computed for all models, WP2D) ──
    graded_r = 0.0
    graded_gf = 0.0
    graded_mf = 0.0
    graded_cf = 0.0
    graded_low = 0.0
    graded_status = ""
    _gt_r = None
    try:
        from grut.interior_waves import (
            GradedTransitionParams as _GTP,
            compute_graded_transition_analysis as _cgta,
        )
        _gt_p = _GTP(
            M_kg=params.M_kg, R_eq_m=R_eq, r_s_m=r_s,
            beta_Q=params.beta_Q, epsilon_Q=params.epsilon_Q,
            quality_factor_Q=interior_Q if interior_Q > 0 else 7.5,  # PDE canon fallback (was 515.6 pre-PDE)
        )
        _gt_r = _cgta(_gt_p, n_echoes=n_echoes)
        graded_r = _gt_r.r_wp2d_amp
        graded_gf = _gt_r.grading_factor
        graded_mf = _gt_r.multimode_factor
        graded_cf = _gt_r.combined_factor
        graded_low = _gt_r.lambda_over_width
        graded_status = _gt_r.echo_channel_status
    except Exception:
        pass  # graded model not available — leave defaults

    # ── PDE-informed interior analysis (interior PDE closure) ──
    pde_Q = 0.0
    pde_gamma = 0.0
    pde_omega_eff = 0.0
    pde_r = 0.0
    pde_cls = ""
    pde_agree = ""
    pde_impact = ""
    try:
        from grut.interior_pde import compute_pde_analysis as _cpde
        _pde_eps = params.epsilon_Q if params.epsilon_Q > 0 else 1.0 / 9.0
        _pde_r = _cpde(
            M_kg=params.M_kg,
            alpha_vac=getattr(params, 'alpha_vac', 1.0 / 3.0),
            beta_Q=params.beta_Q,
            epsilon_Q=_pde_eps,
        )
        pde_Q = _pde_r.Q_pde_fundamental
        pde_gamma = _pde_r.gamma_pde
        pde_omega_eff = _pde_r.omega_eff
        pde_r = _pde_r.r_pde_amp
        pde_cls = _pde_r.response_class
        pde_agree = _pde_r.proxy_agreement
        pde_impact = _pde_r.echo_impact
    except Exception:
        pass  # PDE module not available — leave defaults

    # ── Covariant interior analysis (final closure) ──
    cov_Q = 0.0
    cov_r = 0.0
    cov_cls = ""
    cov_echo_pct = 0.0
    cov_agree = ""
    cov_identity = False
    try:
        from grut.interior_covariant import compute_covariant_analysis as _ccov
        _cov_r = _ccov(
            M_kg=params.M_kg,
            alpha_vac=getattr(params, 'alpha_vac', 1.0 / 3.0),
            beta_Q=params.beta_Q,
            epsilon_Q=params.epsilon_Q if params.epsilon_Q > 0 else 1.0 / 9.0,
        )
        if _cov_r.valid:
            cov_Q = _cov_r.Q_cov
            cov_r = _cov_r.r_cov_amp
            cov_cls = _cov_r.response_class
            cov_echo_pct = _cov_r.echo_amp_cov_pct
            cov_agree = _cov_r.pde_agreement
            cov_identity = _cov_r.structural_identity_preserved
    except Exception:
        pass  # covariant module not available — leave defaults

    # ── Surface amplitude reflection coefficient ──
    # NOTE: All reflection coefficients are AMPLITUDE (not power).
    # Power reflectivity = r_amp^2.
    if params.reflection_model == "perfect":
        R_surface = 1.0
    elif params.reflection_model == "boltzmann":
        if omega_core > 0 and omega_qnm > 0:
            R_surface = math.exp(-omega_qnm / omega_core)
        else:
            R_surface = 0.0
    elif params.reflection_model == "impedance":
        R_surface = impedance_reflectivity(params.M_kg, R_eq, params.beta_Q)
    elif params.reflection_model == "interior":
        # WP2C: interior wave model with Q-dependent correction
        R_surface = _iw_r.r_interior_amp if (_iw_r and interior_cls) else impedance_reflectivity(params.M_kg, R_eq, params.beta_Q)
    elif params.reflection_model == "graded":
        # WP2D: graded-transition + multi-mode best estimate
        R_surface = graded_r if graded_r > 0 else impedance_reflectivity(params.M_kg, R_eq, params.beta_Q)
    elif params.reflection_model == "pde":
        # Interior PDE: PDE-informed reflectivity from dispersion relation
        R_surface = pde_r if pde_r > 0 else impedance_reflectivity(params.M_kg, R_eq, params.beta_Q)
    elif params.reflection_model == "covariant":
        # Covariant interior: metric-corrected impedance from effective ansatz
        R_surface = cov_r if cov_r > 0 else (pde_r if pde_r > 0 else impedance_reflectivity(params.M_kg, R_eq, params.beta_Q))
    elif params.reflection_model == "constant":
        R_surface = params.reflection_coefficient
    else:
        R_surface = params.reflection_coefficient

    R_surface = max(0.0, min(1.0, R_surface))

    # ── Echo amplitudes ──
    amps = echo_amplitudes(n_echoes, T_sq, R_peak, R_surface)

    # ── Nonclaims ──
    nonclaims = [
        "All results computed under SCHWARZSCHILD-LIKE exterior assumption (WP1 conditional).",
        "Echo time delay is an ORDER OF MAGNITUDE estimate using standard Schwarzschild tortoise coordinate.",
        "The GRUT-modified interior metric may change the echo delay significantly.",
        "The BDCC oscillation frequency is a dimensional estimate, not a perturbation-theory result.",
        "Kerr generalization is not attempted (non-rotating only).",
        "This does NOT predict echoes exist — it computes what they WOULD look like under assumptions.",
        "Potential peak transmission |T|^2 is a WKB estimate, not an exact calculation.",
        "All reflection coefficients are AMPLITUDE (not power). Power reflectivity = r_amp^2.",
        "The impedance model for r_surface_amp is a sharp-boundary approximation. "
        "The Phase III-B transition has finite width; transition-width corrections remain open.",
        "The Boltzmann model (r_amp ≈ 0) remains viable if the BDCC is dissipative rather than reactive.",
    ]

    # ── Required closures ──
    closures = [
        "Interior effective metric (needed for exact tortoise coordinate inside horizon)",
        "Proper perturbation theory on GRUT interior (for ω_core and R_surface)",
        "Covariant treatment of the BDCC boundary condition",
        "Kerr generalization for astrophysical black holes",
        "Frequency-dependent R_surface — impedance model provides zeroth-order estimate, "
        "proper wave equation on GRUT interior metric still needed",
        "Transition-width corrections to the sharp-boundary impedance model",
    ]

    return EchoResult(
        r_star_eq=r_star_eq,
        r_star_peak=r_star_peak,
        delta_t_echo_s=dt_echo,
        delta_t_echo_over_r_s=dt_echo_over_r_s,
        omega_core_rad_s=omega_core,
        f_core_Hz=f_core,
        n_echoes=n_echoes,
        echo_amplitudes=amps,
        transmission_squared=T_sq,
        reflection_peak=R_peak,
        reflection_surface=R_surface,
        impedance_ratio_eta=eta,
        interior_quality_factor_Q=interior_Q,
        interior_response_class=interior_cls,
        pde_Q=pde_Q,
        pde_gamma=pde_gamma,
        pde_omega_eff=pde_omega_eff,
        pde_r_amp=pde_r,
        pde_response_class=pde_cls,
        pde_proxy_agreement=pde_agree,
        pde_echo_impact=pde_impact,
        cov_Q=cov_Q,
        cov_r_amp=cov_r,
        cov_response_class=cov_cls,
        cov_echo_pct=cov_echo_pct,
        cov_pde_agreement=cov_agree,
        cov_identity_preserved=cov_identity,
        graded_r_amp=graded_r,
        graded_grading_factor=graded_gf,
        graded_multimode_factor=graded_mf,
        graded_combined_factor=graded_cf,
        graded_lambda_over_width=graded_low,
        graded_echo_channel_status=graded_status,
        omega_qnm_rad_s=omega_qnm,
        tau_qnm_s=tau_qnm,
        f_qnm_Hz=f_qnm,
        exterior_assumption="schwarzschild_like",
        confidence="order_of_magnitude",
        nonclaims=nonclaims,
        required_closures=closures,
    )


def echo_result_to_dict(result: EchoResult) -> Dict[str, Any]:
    """Serialize an EchoResult to a dict for evidence packets."""
    return {
        "echo_timing": {
            "r_star_eq_m": result.r_star_eq,
            "r_star_peak_m": result.r_star_peak,
            "delta_t_echo_s": result.delta_t_echo_s,
            "delta_t_echo_over_r_s": result.delta_t_echo_over_r_s,
        },
        "bdcc_oscillation": {
            "omega_core_rad_s": result.omega_core_rad_s,
            "f_core_Hz": result.f_core_Hz,
        },
        "echo_amplitudes": {
            "n_echoes": result.n_echoes,
            "A_n_over_A_0": result.echo_amplitudes,
            "transmission_squared_pow": result.transmission_squared,
            "reflection_peak_amp": result.reflection_peak,
            "reflection_surface_amp": result.reflection_surface,
            "reflection_surface_pow": result.reflection_surface ** 2,
        },
        "impedance": {
            "impedance_ratio_eta": result.impedance_ratio_eta,
            "note": "sharp-boundary approximation; transition-width corrections open",
        },
        "interior_wave": {
            "quality_factor_Q": result.interior_quality_factor_Q,
            "response_class": result.interior_response_class,
            "note": "WP2C zeroth-order damped oscillator model",
        },
        "graded_transition": {
            "r_wp2d_amp": result.graded_r_amp,
            "grading_factor": result.graded_grading_factor,
            "multimode_factor": result.graded_multimode_factor,
            "combined_factor": result.graded_combined_factor,
            "lambda_over_width": result.graded_lambda_over_width,
            "echo_channel_status": result.graded_echo_channel_status,
            "note": "WP2D graded-transition + multi-mode correction",
        },
        "pde_interior": {
            "Q_pde": result.pde_Q,
            "gamma_pde": result.pde_gamma,
            "omega_eff_pde": result.pde_omega_eff,
            "r_pde_amp": result.pde_r_amp,
            "response_class": result.pde_response_class,
            "proxy_agreement": result.pde_proxy_agreement,
            "echo_impact": result.pde_echo_impact,
            "note": "Interior PDE closure — dispersion relation on linearised collapse ODE",
        },
        "covariant_interior": {
            "Q_cov": result.cov_Q,
            "r_cov_amp": result.cov_r_amp,
            "response_class": result.cov_response_class,
            "echo_pct": result.cov_echo_pct,
            "pde_agreement": result.cov_pde_agreement,
            "identity_preserved": result.cov_identity_preserved,
            "note": "Covariant interior closure — effective metric ansatz with memory-dressed impedance",
        },
        "qnm_reference": {
            "omega_qnm_rad_s": result.omega_qnm_rad_s,
            "tau_qnm_s": result.tau_qnm_s,
            "f_qnm_Hz": result.f_qnm_Hz,
        },
        "status": {
            "exterior_assumption": result.exterior_assumption,
            "confidence": result.confidence,
        },
        "nonclaims": result.nonclaims,
        "required_closures": result.required_closures,
    }


# ============================================================================
# COMPARISON / SCANNING UTILITIES
# ============================================================================

def scan_reflection_coefficient(
    M_kg: float,
    R_eq_over_r_s: float = 1.0 / 3.0,
    beta_Q: float = 2.0,
    R_values: Optional[List[float]] = None,
    n_echoes: int = 3,
) -> List[Dict[str, Any]]:
    """Scan over reflection coefficients to map echo amplitude vs R_surface.

    Parameters
    ----------
    M_kg : float
        Black hole mass (kg).
    R_eq_over_r_s : float
        Dimensionless endpoint radius (default 1/3).
    beta_Q : float
        Barrier exponent (default 2).
    R_values : list of float, optional
        Reflection coefficients to scan. Default: [0.0, 0.01, 0.1, 0.5, 1.0].
    n_echoes : int
        Number of echoes per scan point (default 3).

    Returns
    -------
    list of dict
        One dict per R_value with echo parameters.
    """
    if R_values is None:
        R_values = [0.0, 0.01, 0.1, 0.3, 0.5, 0.8, 1.0]

    r_s = schwarzschild_radius(M_kg)

    results = []
    for R_val in R_values:
        params = EchoParameters(
            M_kg=M_kg,
            r_s_m=r_s,
            R_eq_m=R_eq_over_r_s * r_s,
            R_eq_over_r_s=R_eq_over_r_s,
            compactness=1.0 / R_eq_over_r_s if R_eq_over_r_s > 0 else 0.0,
            beta_Q=beta_Q,
            reflection_model="constant",
            reflection_coefficient=R_val,
        )
        echo = compute_echo_analysis(params, n_echoes=n_echoes)

        results.append({
            "R_surface": R_val,
            "delta_t_echo_s": echo.delta_t_echo_s,
            "first_echo_amplitude": echo.echo_amplitudes[0] if echo.echo_amplitudes else 0.0,
            "echo_amplitudes": echo.echo_amplitudes,
            "regime": (
                "standard_GR" if R_val == 0.0
                else "weak_reflection" if R_val < 0.1
                else "moderate_reflection" if R_val < 0.5
                else "strong_reflection"
            ),
        })

    return results


def scan_mass_range(
    mass_range_kg: Optional[List[float]] = None,
    R_eq_over_r_s: float = 1.0 / 3.0,
    reflection_coefficient: float = 1.0,
) -> List[Dict[str, Any]]:
    """Scan over mass range to show echo timing scaling.

    Parameters
    ----------
    mass_range_kg : list of float, optional
        Masses to scan. Default: 10, 30, 100 solar masses + 1e6, 1e9 M_sun.
    R_eq_over_r_s : float
        Dimensionless endpoint radius (default 1/3).
    reflection_coefficient : float
        R_surface for all masses (default 1.0 = perfect).

    Returns
    -------
    list of dict
        One dict per mass with echo timing.
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
        params = EchoParameters(
            M_kg=M,
            r_s_m=r_s,
            R_eq_m=R_eq_over_r_s * r_s,
            R_eq_over_r_s=R_eq_over_r_s,
            beta_Q=2.0,
            reflection_model="constant",
            reflection_coefficient=reflection_coefficient,
        )
        echo = compute_echo_analysis(params, n_echoes=3)

        # Impedance model values at this mass (always computed for reference)
        R_eq_m = R_eq_over_r_s * r_s
        eta = impedance_ratio(M, R_eq_m, 2.0)
        r_imp_amp = impedance_reflectivity(M, R_eq_m, 2.0)

        results.append({
            "M_solar": M / M_SUN,
            "r_s_km": r_s / 1000.0,
            "delta_t_echo_ms": echo.delta_t_echo_s * 1000.0,
            "f_qnm_Hz": echo.f_qnm_Hz,
            "f_core_Hz": echo.f_core_Hz,
            "first_echo_amplitude": echo.echo_amplitudes[0] if echo.echo_amplitudes else 0.0,
            "impedance_eta": eta,
            "impedance_r_surface_amp": r_imp_amp,
            "interior_Q": echo.interior_quality_factor_Q,
            "interior_response_class": echo.interior_response_class,
            "graded_r_amp": echo.graded_r_amp,
            "graded_combined_factor": echo.graded_combined_factor,
            "graded_echo_channel_status": echo.graded_echo_channel_status,
            "pde_Q": echo.pde_Q,
            "pde_r_amp": echo.pde_r_amp,
            "pde_response_class": echo.pde_response_class,
            "cov_Q": echo.cov_Q,
            "cov_r_amp": echo.cov_r_amp,
            "cov_response_class": echo.cov_response_class,
            "cov_echo_pct": echo.cov_echo_pct,
            "cov_pde_agreement": echo.cov_pde_agreement,
        })

    return results
