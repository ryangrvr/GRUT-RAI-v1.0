"""
Interior PDE module — perturbation equation for the BDCC.

Phase III-C: Replaces the proxy oscillator model (WP2C) with a
PDE-informed framework derived from the linearised GRUT collapse
equations around the barrier-dominated equilibrium.

**Core equation (dispersion relation):**

    omega^2 = omega_0^2 + 2*alpha*omega_g^2 / (1 + i*omega*tau_eff)

where:
    omega_0^2 = beta_Q * GM / R_eq^3   (barrier restoring frequency)
    omega_g^2 = GM / R_eq^3            (gravitational frequency scale)
    alpha     = alpha_vac               (vacuum susceptibility)
    tau_eff   = tier-0 memory timescale at R_eq

This dispersion relation is DERIVED from linearising the coupled
(R, V, M_drive) ODE system about the equilibrium R_eq, V=0.

STATUS: FIRST DERIVATION — approximate, zeroth-order.
NOT a covariant wave equation. NOT a full PDE in space-time.
See docs/PHASE_III_C_PDE_MEMO.md for complete derivation.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# Physical constants (duplicated for module independence)
G_SI = 6.674e-11      # m^3 kg^-1 s^-2
C_SI = 299_792_458.0   # m/s


# ================================================================
# Data Structures
# ================================================================

@dataclass
class PDEBackground:
    """Background state at the BDCC equilibrium.

    All quantities evaluated at R = R_eq, V = 0, M_drive = a_grav.
    These are the coefficients of the linearised perturbation equation.
    """
    # Physical parameters
    M_kg: float = 0.0
    R_eq_m: float = 0.0
    r_s_m: float = 0.0

    # Operator parameters
    alpha_vac: float = 1.0 / 3.0
    beta_Q: float = 2.0
    epsilon_Q: float = 1.0 / 9.0
    tau0_s: float = 1.3225e15
    gamma_diss: float = 1e-15

    # Derived frequencies (computed by build_pde_background)
    omega_g: float = 0.0           # sqrt(GM / R_eq^3)
    omega_0: float = 0.0           # sqrt(beta_Q) * omega_g  (bare eigenfrequency)
    omega_g_sq: float = 0.0        # GM / R_eq^3
    omega_0_sq: float = 0.0        # beta_Q * omega_g^2

    # Memory timescale at equilibrium
    t_dyn_local: float = 0.0       # sqrt(R_eq^3 / (2GM))
    tau_local: float = 0.0         # tau0 * t_dyn / (t_dyn + tau0)
    tau_eff: float = 0.0           # = tau_local at V=0

    # Derived dimensionless ratios
    omega_0_tau: float = 0.0       # omega_0 * tau_eff
    compactness: float = 0.0       # 2GM / (R_eq * c^2)

    # Status flags
    valid: bool = False
    missing_closures: List[str] = field(default_factory=list)


@dataclass
class PDEMode:
    """A single mode from the PDE dispersion relation."""
    label: str = ""                 # e.g. "fundamental", "n=1", etc.
    l: int = 0                      # angular quantum number
    omega_real: float = 0.0         # Re(omega) — oscillation frequency (rad/s)
    omega_imag: float = 0.0         # Im(omega) — damping rate (rad/s)
    Q_pde: float = 0.0             # Quality factor from PDE
    period_s: float = 0.0          # 2*pi / omega_real
    damping_time_s: float = 0.0    # 1 / |omega_imag|
    response_class: str = ""        # reactive / mixed / dissipative


@dataclass
class PDEResult:
    """Full result from the interior PDE analysis."""
    # Background
    background: PDEBackground = field(default_factory=PDEBackground)

    # Mode spectrum
    modes: List[PDEMode] = field(default_factory=list)

    # Summary quantities
    Q_pde_fundamental: float = 0.0
    Q_proxy: float = 0.0          # WP2C proxy Q for comparison
    gamma_pde: float = 0.0        # PDE-derived damping rate
    gamma_proxy: float = 0.0      # WP2C proxy damping rate
    omega_eff: float = 0.0        # Effective restoring frequency
    omega_proxy: float = 0.0      # WP2C proxy frequency

    # Response classification
    response_class: str = "undetermined"
    proxy_agreement: str = ""      # "confirmed" / "modified" / "contradicted"

    # Echo channel impact
    r_pde_amp: float = 0.0        # Reflection amplitude from PDE Q
    r_proxy_amp: float = 0.0      # Reflection amplitude from proxy Q
    echo_impact: str = ""          # "strengthened" / "preserved" / "weakened" / "collapsed"

    # Effective potential
    V_eff_at_Req: float = 0.0     # V_eff(R_eq) — minimum of potential well
    potential_depth: float = 0.0   # Depth of potential well

    # Nonclaims and closures
    nonclaims: List[str] = field(default_factory=list)
    missing_closures: List[str] = field(default_factory=list)


# ================================================================
# Background Builder
# ================================================================

def build_pde_background(
    M_kg: float,
    alpha_vac: float = 1.0 / 3.0,
    beta_Q: float = 2.0,
    epsilon_Q: float = 1.0 / 9.0,
    tau0_s: float = 1.3225e15,
    gamma_diss: float = 1e-15,
) -> PDEBackground:
    """Build the PDE background state from physical parameters.

    Computes all derived frequencies, timescales, and dimensionless
    ratios at the equilibrium point R_eq.

    Parameters
    ----------
    M_kg : float
        Black hole mass (kg).
    alpha_vac : float
        Vacuum susceptibility (canon: 1/3).
    beta_Q : float
        Barrier exponent (canon: 2).
    epsilon_Q : float
        Barrier amplitude (canon: 1/9).
    tau0_s : float
        Bare memory timescale (s).
    gamma_diss : float
        Solver dissipation rate (s^-1).

    Returns
    -------
    PDEBackground
        Fully populated background state.
    """
    bg = PDEBackground(
        M_kg=M_kg,
        alpha_vac=alpha_vac,
        beta_Q=beta_Q,
        epsilon_Q=epsilon_Q,
        tau0_s=tau0_s,
        gamma_diss=gamma_diss,
    )

    if M_kg <= 0:
        bg.missing_closures = ["M_kg must be positive"]
        return bg

    # Schwarzschild radius
    r_s = 2.0 * G_SI * M_kg / (C_SI * C_SI)
    bg.r_s_m = r_s

    # Equilibrium radius from constrained endpoint law
    R_eq = r_s * epsilon_Q ** (1.0 / beta_Q)
    bg.R_eq_m = R_eq

    if R_eq <= 0:
        bg.missing_closures = ["R_eq must be positive"]
        return bg

    # Gravitational frequency scale
    omega_g_sq = G_SI * M_kg / (R_eq ** 3)
    omega_g = math.sqrt(omega_g_sq)
    bg.omega_g = omega_g
    bg.omega_g_sq = omega_g_sq

    # Bare eigenfrequency (stability eigenvalue)
    omega_0_sq = beta_Q * omega_g_sq
    omega_0 = math.sqrt(omega_0_sq)
    bg.omega_0 = omega_0
    bg.omega_0_sq = omega_0_sq

    # Local dynamical time at R_eq
    t_dyn = math.sqrt(R_eq ** 3 / (2.0 * G_SI * M_kg))
    bg.t_dyn_local = t_dyn

    # Tier-0 local tau
    tau_local = tau0_s * t_dyn / (t_dyn + tau0_s)
    tau_local = max(tau_local, 1e-30)
    bg.tau_local = tau_local
    bg.tau_eff = tau_local  # At V=0, tau_eff = tau_local

    # Dimensionless ratio
    bg.omega_0_tau = omega_0 * tau_local

    # Compactness
    bg.compactness = 2.0 * G_SI * M_kg / (R_eq * C_SI * C_SI)

    bg.valid = True
    bg.missing_closures = [
        "Covariant interior metric not available — using ODE linearisation",
        "Radial field equation requires inter-shell coupling (sound speed)",
        "Non-radial coupling derived from Schwarzschild separation, not GRUT metric",
        "Perturbations in tau_eff itself neglected (second-order)",
        "Kerr/spin effects not included",
    ]

    return bg


# ================================================================
# Dispersion Relation Solver
# ================================================================

def dispersion_relation(
    omega: complex,
    bg: PDEBackground,
) -> complex:
    """Evaluate the GRUT interior dispersion relation.

    F(omega) = omega^2 - omega_0^2 - 2*alpha*omega_g^2 / (1 + i*omega*tau)

    Roots of F(omega) = 0 are the eigenfrequencies of the BDCC.

    Parameters
    ----------
    omega : complex
        Trial frequency.
    bg : PDEBackground
        Background state.

    Returns
    -------
    complex
        F(omega) — zero at eigenfrequencies.
    """
    tau = bg.tau_eff
    alpha = bg.alpha_vac
    w0sq = bg.omega_0_sq
    wgsq = bg.omega_g_sq

    denom = 1.0 + 1j * omega * tau
    memory_term = 2.0 * alpha * wgsq / denom

    return omega * omega - w0sq - memory_term


def _dispersion_derivative(
    omega: complex,
    bg: PDEBackground,
) -> complex:
    """Derivative dF/d(omega) for Newton iteration."""
    tau = bg.tau_eff
    alpha = bg.alpha_vac
    wgsq = bg.omega_g_sq

    denom = 1.0 + 1j * omega * tau
    # d/domega of [omega^2 - w0sq - 2*alpha*wgsq/(1+i*omega*tau)]
    # = 2*omega + 2*alpha*wgsq * i*tau / (1+i*omega*tau)^2
    return 2.0 * omega + 2.0 * alpha * wgsq * 1j * tau / (denom * denom)


def solve_dispersion(
    bg: PDEBackground,
    l: int = 2,
    n_modes: int = 3,
    max_iter: int = 200,
    tol: float = 1e-12,
) -> List[PDEMode]:
    """Find eigenfrequencies of the GRUT interior dispersion relation.

    Uses Newton's method starting from intelligent initial guesses.

    Parameters
    ----------
    bg : PDEBackground
        Background state.
    l : int
        Angular quantum number (default l=2 for gravitational waves).
    n_modes : int
        Number of modes to search for.
    max_iter : int
        Maximum Newton iterations per mode.
    tol : float
        Convergence tolerance.

    Returns
    -------
    List[PDEMode]
        Found modes, sorted by increasing real frequency.
    """
    if not bg.valid:
        return []

    modes: List[PDEMode] = []

    # Angular frequency contribution for l > 0
    # For a cavity of size R_eq, angular modes contribute:
    # delta_omega^2 ~ l(l+1) * c_s^2 / R_eq^2
    c_s = bg.omega_0 * bg.R_eq_m  # effective sound speed
    angular_correction = l * (l + 1) * c_s * c_s / (bg.R_eq_m * bg.R_eq_m)

    for n in range(n_modes):
        # Initial guess for mode n:
        # Fundamental: omega ~ omega_0 with angular correction
        # Higher: omega ~ omega_0 * sqrt(1 + n^2 * pi^2 * c_s^2 / (omega_0^2 * R_eq^2))
        spatial_factor = 1.0 + n * n * math.pi * math.pi * c_s * c_s / (
            bg.omega_0_sq * bg.R_eq_m * bg.R_eq_m
        ) if bg.omega_0_sq > 0 else 1.0
        omega_guess_real = bg.omega_0 * math.sqrt(spatial_factor)

        if n == 0:
            omega_guess_real = math.sqrt(bg.omega_0_sq + angular_correction) if (
                bg.omega_0_sq + angular_correction > 0) else bg.omega_0

        # Initial damping guess from proxy
        gamma_guess = bg.alpha_vac * bg.omega_g_sq * bg.tau_eff / (
            1.0 + omega_guess_real * omega_guess_real * bg.tau_eff * bg.tau_eff
        )
        gamma_guess = max(gamma_guess, 1e-30)

        omega_guess = complex(omega_guess_real, -gamma_guess)

        # Newton iteration
        omega = omega_guess
        converged = False
        for _ in range(max_iter):
            F = dispersion_relation(omega, bg)

            # Add angular correction to the dispersion relation
            if n == 0 and l > 0:
                F -= angular_correction

            dF = _dispersion_derivative(omega, bg)
            if abs(dF) < 1e-50:
                break

            delta = F / dF
            omega = omega - delta

            if abs(delta) < tol * abs(omega):
                converged = True
                break

        if not converged:
            # Try again with slightly different initial guess
            omega = complex(omega_guess_real * 1.01, -gamma_guess * 0.5)
            for _ in range(max_iter):
                F = dispersion_relation(omega, bg)
                if n == 0 and l > 0:
                    F -= angular_correction
                dF = _dispersion_derivative(omega, bg)
                if abs(dF) < 1e-50:
                    break
                delta = F / dF
                omega = omega - delta
                if abs(delta) < tol * abs(omega):
                    converged = True
                    break

        omega_real = abs(omega.real)
        omega_imag = omega.imag  # negative for damping

        # Compute quality factor
        gamma_mode = abs(omega_imag)
        Q_mode = omega_real / (2.0 * gamma_mode) if gamma_mode > 0 else float("inf")

        # Period and damping time
        period = 2.0 * math.pi / omega_real if omega_real > 0 else float("inf")
        damp_time = 1.0 / gamma_mode if gamma_mode > 0 else float("inf")

        # Classification
        if Q_mode > 10.0:
            resp_class = "reactive"
        elif Q_mode > 1.0:
            resp_class = "mixed_viscoelastic"
        else:
            resp_class = "dissipative"

        label = "fundamental" if n == 0 else f"n={n}"
        if l > 0:
            label = f"l={l} {label}"

        modes.append(PDEMode(
            label=label,
            l=l,
            omega_real=omega_real,
            omega_imag=omega_imag,
            Q_pde=Q_mode,
            period_s=period,
            damping_time_s=damp_time,
            response_class=resp_class,
        ))

    # Sort by real frequency
    modes.sort(key=lambda m: m.omega_real)
    return modes


# ================================================================
# Effective Potential
# ================================================================

def effective_potential(
    r_over_rs: float,
    bg: PDEBackground,
    l: int = 2,
    omega_probe: float = 0.0,
) -> float:
    """Compute the effective potential V_eff(r) for radial perturbations.

    V_eff(r) = omega_eff^2(r) * Phi(r) + l(l+1) * c_s^2(r) / r^2

    where Phi(r) is the barrier dominance profile.

    Parameters
    ----------
    r_over_rs : float
        Radial coordinate r / r_s.
    bg : PDEBackground
        Background state.
    l : int
        Angular quantum number.
    omega_probe : float
        Probing frequency (rad/s). If 0, uses omega_0.

    Returns
    -------
    float
        V_eff in rad^2/s^2.
    """
    if not bg.valid or r_over_rs <= 0:
        return 0.0

    R_eq_over_rs = bg.R_eq_m / bg.r_s_m if bg.r_s_m > 0 else 1.0 / 3.0
    r_m = r_over_rs * bg.r_s_m

    # Barrier dominance profile (power-law from WP2D)
    transition_width = 0.703  # in units of r_s
    t = (r_over_rs - R_eq_over_rs) / transition_width if transition_width > 0 else 0.0

    if t <= 0:
        Phi = 1.0
    elif t >= 1.0:
        Phi = 0.0
    else:
        # Crystallisation constraint: Phi(0.4715) = 0.5
        t_cryst = (0.4715 - R_eq_over_rs) / transition_width
        if t_cryst > 0 and t_cryst < 1:
            alpha_pow = math.log(0.5) / math.log(t_cryst)
        else:
            alpha_pow = 1.0
        Phi = max(0.0, 1.0 - t ** alpha_pow)

    # Local omega_eff^2 — modulated by Phi
    if omega_probe <= 0:
        omega_probe = bg.omega_0

    omega_tau_sq = omega_probe * omega_probe * bg.tau_eff * bg.tau_eff
    omega_eff_sq = bg.omega_0_sq * Phi + (
        2.0 * bg.alpha_vac * bg.omega_g_sq * Phi / (1.0 + omega_tau_sq)
    )

    # Angular barrier
    c_s = bg.omega_0 * bg.R_eq_m  # sound speed
    angular_term = 0.0
    if r_m > 0:
        angular_term = l * (l + 1) * c_s * c_s / (r_m * r_m) * Phi

    return omega_eff_sq + angular_term


# ================================================================
# PDE-Informed Response Analysis
# ================================================================

def _pde_damping_rate(bg: PDEBackground, omega: float) -> float:
    """PDE-derived damping rate at frequency omega.

    gamma_PDE = alpha * omega_g^2 * tau / (1 + omega^2 * tau^2)
    """
    omega_tau_sq = omega * omega * bg.tau_eff * bg.tau_eff
    return bg.alpha_vac * bg.omega_g_sq * bg.tau_eff / (1.0 + omega_tau_sq)


def _pde_effective_frequency(bg: PDEBackground, omega: float) -> float:
    """PDE-derived effective restoring frequency at probe frequency omega.

    omega_eff^2 = omega_0^2 + 2*alpha*omega_g^2 / (1 + omega^2*tau^2)
    """
    omega_tau_sq = omega * omega * bg.tau_eff * bg.tau_eff
    memory_stiffness = 2.0 * bg.alpha_vac * bg.omega_g_sq / (1.0 + omega_tau_sq)
    return math.sqrt(bg.omega_0_sq + memory_stiffness)


def _proxy_damping_rate(bg: PDEBackground) -> float:
    """WP2C proxy damping rate for comparison.

    gamma_proxy = alpha * omega_0^2 * tau / (2 * (1 + (omega_0*tau)^2))

    Note the factor of 2 difference from PDE: the proxy used
    omega_core^2 = beta_Q * omega_g^2 and a different normalisation.
    """
    x = bg.omega_0 * bg.tau_eff
    return bg.alpha_vac * bg.omega_0_sq * bg.tau_eff / (2.0 * (1.0 + x * x))


def _impedance_reflection(omega_core: float, R_eq: float) -> float:
    """Sharp-boundary impedance reflection amplitude.

    eta = omega_core * R_eq / c
    r = |1 - eta| / (1 + eta)
    """
    eta = omega_core * R_eq / C_SI
    if eta < 0:
        return 0.0
    return abs(1.0 - eta) / (1.0 + eta)


def compute_pde_analysis(
    M_kg: float,
    alpha_vac: float = 1.0 / 3.0,
    beta_Q: float = 2.0,
    epsilon_Q: float = 1.0 / 9.0,
    tau0_s: float = 1.3225e15,
    gamma_diss: float = 1e-15,
    l: int = 2,
    n_modes: int = 3,
) -> PDEResult:
    """Full PDE-informed interior analysis.

    This is the main entry point. It:
    1. Builds the background state
    2. Solves the dispersion relation for eigenfrequencies
    3. Computes PDE-derived Q and damping
    4. Compares to WP2C proxy model
    5. Classifies response and echo channel impact

    Parameters
    ----------
    M_kg : float
        Black hole mass (kg).
    alpha_vac, beta_Q, epsilon_Q, tau0_s, gamma_diss : float
        GRUT operator parameters.
    l : int
        Angular quantum number (default l=2).
    n_modes : int
        Number of modes to find.

    Returns
    -------
    PDEResult
        Complete analysis result.
    """
    result = PDEResult()

    # Step 1: Build background
    bg = build_pde_background(M_kg, alpha_vac, beta_Q, epsilon_Q, tau0_s, gamma_diss)
    result.background = bg

    if not bg.valid:
        result.nonclaims = ["Background construction failed — no analysis possible"]
        return result

    # Step 2: Solve dispersion relation
    modes = solve_dispersion(bg, l=l, n_modes=n_modes)
    result.modes = modes

    # Step 3: PDE-derived quantities
    gamma_pde = _pde_damping_rate(bg, bg.omega_0)
    gamma_pde_total = gamma_pde + bg.gamma_diss
    omega_eff = _pde_effective_frequency(bg, bg.omega_0)

    result.gamma_pde = gamma_pde_total
    result.omega_eff = omega_eff

    # PDE quality factor
    Q_pde = omega_eff / (2.0 * gamma_pde_total) if gamma_pde_total > 0 else float("inf")
    result.Q_pde_fundamental = Q_pde

    # Step 4: Proxy comparison
    gamma_proxy = _proxy_damping_rate(bg)
    gamma_proxy_total = gamma_proxy + bg.gamma_diss
    Q_proxy = bg.omega_0 / (2.0 * gamma_proxy_total) if gamma_proxy_total > 0 else float("inf")

    result.gamma_proxy = gamma_proxy_total
    result.Q_proxy = Q_proxy
    result.omega_proxy = bg.omega_0

    # Step 5: Mode spectrum Q
    if modes:
        result.Q_pde_fundamental = modes[0].Q_pde

    # Step 6: Response classification
    if Q_pde > 10.0:
        result.response_class = "reactive"
    elif Q_pde > 1.0:
        result.response_class = "mixed_viscoelastic"
    else:
        result.response_class = "dissipative"

    # Step 7: Proxy agreement assessment
    # Compare the ratio Q_pde / Q_proxy
    if Q_proxy > 0 and math.isfinite(Q_proxy):
        ratio = Q_pde / Q_proxy
        if 0.5 < ratio < 2.0:
            result.proxy_agreement = "confirmed"
        elif 0.1 < ratio < 10.0:
            result.proxy_agreement = "modified"
        else:
            result.proxy_agreement = "contradicted"
    else:
        result.proxy_agreement = "undetermined"

    # Step 8: Reflection amplitudes
    r_pde = _impedance_reflection(omega_eff, bg.R_eq_m)
    r_proxy = _impedance_reflection(bg.omega_0, bg.R_eq_m)
    result.r_pde_amp = r_pde
    result.r_proxy_amp = r_proxy

    # Step 9: Echo channel impact
    if r_pde > 0 and r_proxy > 0:
        ratio = r_pde / r_proxy
        if ratio > 1.01:
            result.echo_impact = "strengthened"
        elif ratio > 0.95:
            result.echo_impact = "preserved"
        elif ratio > 0.5:
            result.echo_impact = "weakened_modestly"
        else:
            result.echo_impact = "collapsed"
    else:
        result.echo_impact = "undetermined"

    # Step 10: Effective potential at R_eq
    V_eff_Req = effective_potential(bg.R_eq_m / bg.r_s_m, bg, l=l, omega_probe=bg.omega_0)
    result.V_eff_at_Req = V_eff_Req
    # Potential depth: difference between barrier peak and well minimum
    V_eff_outer = effective_potential(1.036, bg, l=l, omega_probe=bg.omega_0)
    result.potential_depth = V_eff_Req - V_eff_outer

    # Step 11: Nonclaims
    result.nonclaims = [
        "PDE is derived from ODE linearisation, NOT from a covariant wave equation",
        "Spatial structure added via Regge-Wheeler separation, not from GRUT metric",
        "Memory coupling simplified — single tau_eff at equilibrium, not a field",
        "Angular mode structure uses standard l(l+1)/r^2, not GRUT angular equation",
        "Perturbations in tau_eff are neglected (second-order effect)",
        "Mode spectrum uses cavity model — not derived from boundary value problem",
        "Phi(r) profile is parameterised (Phase III-B), not from dynamical equation",
        "Quality factor is CANDIDATE — hidden dissipation channels not modeled",
        "Kerr/spin effects are NOT included",
        "No result is promoted to final canon",
    ]

    result.missing_closures = [
        "Covariant interior metric tensor (GRUT does not yet have one)",
        "Inter-shell coupling equation (relates adjacent radial shells)",
        "Ab initio angular mode equation on GRUT interior",
        "Nonlinear mode coupling beyond perturbation theory",
        "Dynamical tau_eff perturbation equation",
        "Kerr generalisation for rotating black holes",
    ]

    return result


# ================================================================
# Serialisation
# ================================================================

def pde_background_to_dict(bg: PDEBackground) -> dict:
    """Convert PDEBackground to a dictionary for JSON output."""
    return {
        "M_kg": bg.M_kg,
        "R_eq_m": bg.R_eq_m,
        "r_s_m": bg.r_s_m,
        "alpha_vac": bg.alpha_vac,
        "beta_Q": bg.beta_Q,
        "epsilon_Q": bg.epsilon_Q,
        "tau0_s": bg.tau0_s,
        "gamma_diss": bg.gamma_diss,
        "omega_g": bg.omega_g,
        "omega_0": bg.omega_0,
        "omega_g_sq": bg.omega_g_sq,
        "omega_0_sq": bg.omega_0_sq,
        "t_dyn_local": bg.t_dyn_local,
        "tau_local": bg.tau_local,
        "tau_eff": bg.tau_eff,
        "omega_0_tau": bg.omega_0_tau,
        "compactness": bg.compactness,
        "valid": bg.valid,
        "missing_closures": list(bg.missing_closures),
    }


def pde_mode_to_dict(mode: PDEMode) -> dict:
    """Convert PDEMode to a dictionary."""
    return {
        "label": mode.label,
        "l": mode.l,
        "omega_real": mode.omega_real,
        "omega_imag": mode.omega_imag,
        "Q_pde": mode.Q_pde,
        "period_s": mode.period_s,
        "damping_time_s": mode.damping_time_s,
        "response_class": mode.response_class,
    }


def pde_result_to_dict(result: PDEResult) -> dict:
    """Convert PDEResult to a serialisable dictionary."""
    return {
        "background": pde_background_to_dict(result.background),
        "modes": [pde_mode_to_dict(m) for m in result.modes],
        "summary": {
            "Q_pde_fundamental": result.Q_pde_fundamental,
            "Q_proxy": result.Q_proxy,
            "gamma_pde": result.gamma_pde,
            "gamma_proxy": result.gamma_proxy,
            "omega_eff": result.omega_eff,
            "omega_proxy": result.omega_proxy,
            "response_class": result.response_class,
            "proxy_agreement": result.proxy_agreement,
            "r_pde_amp": result.r_pde_amp,
            "r_proxy_amp": result.r_proxy_amp,
            "echo_impact": result.echo_impact,
            "V_eff_at_Req": result.V_eff_at_Req,
            "potential_depth": result.potential_depth,
        },
        "nonclaims": list(result.nonclaims),
        "missing_closures": list(result.missing_closures),
    }
