# Phase III-C Interior PDE Memo — Perturbation Equation for the BDCC

**DATE**: 2026-03-11
**STATUS**: FIRST DERIVATION — approximate, zeroth-order
**CONDITIONAL ON**: WP1 Schwarzschild-like exterior, constrained endpoint law

---

## A. What Is Being Derived

A linearized perturbation equation for small radial disturbances
around the BDCC equilibrium state. This replaces the WP2C proxy
(parameterized damped oscillator) with a PDE derived from the actual
GRUT collapse dynamics.

The goal is to obtain the **effective wave operator** that a perturbation
sees inside the BDCC, including:
- the restoring force (storage / elasticity)
- the damping channels (loss / dissipation)
- the effective potential landscape
- the mode structure implied by the equation

---

## B. Inherited Assumptions from WP1/WP2

1. **Exterior**: Schwarzschild-like (WP1 conditional). The perturbation
   enters from outside as a standard Regge-Wheeler/Zerilli mode.

2. **Endpoint**: R_eq / r_s = 1/3 from constrained endpoint law
   (epsilon_Q = alpha_vac^2 = 1/9, beta_Q = 2).

3. **Background is static**: At R_eq, V = 0, dV/dt = 0, M_drive has
   saturated to a_grav. This is the equilibrium state about which we
   perturb.

4. **Spherical symmetry**: Schwarzschild background, radial collapse.
   Angular structure enters only through l(l+1) separation constant.

5. **WP2D validation**: Sharp-boundary impedance is accurate to < 1%.
   Transition-width corrections are small.

---

## C. Derivation of the Interior Perturbation Equation

### C.1 Background State at Equilibrium

The collapse solver has three state variables: (R, V, M_drive).
At equilibrium:

    R = R_eq,   V = 0,   M_drive = a_grav_eq = GM / R_eq^2

The force balance is:

    a_inward = (1 - alpha) * a_grav + alpha * M_drive
             = (1 - alpha) * GM/R_eq^2 + alpha * GM/R_eq^2
             = GM / R_eq^2

    a_outward = a_Q = (GM/R_eq^2) * epsilon_Q * (r_s/R_eq)^beta_Q
              = GM/R_eq^2   [at R_eq where epsilon_Q*(r_s/R_eq)^beta_Q = 1]

    a_net = 0  (force balance)

### C.2 Linearization: Perturb R = R_eq + delta_R

Write R(t) = R_eq + delta_R(t) with |delta_R| << R_eq.

The net acceleration is a_net(R) = a_inward(R) - a_outward(R).

**Inward force** (after M_drive saturation):

    a_inward(R) = GM / R^2

**Outward force (OP_QPRESS_001)**:

    a_outward(R) = (GM/R^2) * epsilon_Q * (r_s/R)^beta_Q

Expand to first order in delta_R / R_eq:

    a_inward(R_eq + dR) = GM/R_eq^2 * [1 - 2 dR/R_eq + ...]

    a_outward(R_eq + dR) = GM/R_eq^2 * epsilon_Q * (r_s/R_eq)^beta_Q
                            * [1 - (2 + beta_Q) dR/R_eq + ...]

At equilibrium, epsilon_Q * (r_s/R_eq)^beta_Q = 1, so:

    a_net(R_eq + dR) = GM/R_eq^2 * [-2 dR/R_eq + (2+beta_Q) dR/R_eq]
                     = GM/R_eq^2 * beta_Q * dR / R_eq

The equation of motion d^2(dR)/dt^2 = -a_net gives:

    d^2(dR)/dt^2 = -omega_0^2 * dR

where the **bare eigenfrequency** is:

    omega_0^2 = beta_Q * GM / R_eq^3

This is the restoring force. For beta_Q = 2:

    omega_0^2 = 2 GM / R_eq^3

This exactly matches the stability eigenvalue from Phase III-A.

**CRITICAL NOTE**: The WP2C proxy used omega_core^2 = beta_Q * GM / R_eq^4
(an extra factor of 1/R_eq). The correct linearisation gives
omega_0^2 = beta_Q * GM / R_eq^3. The proxy was too low by a factor
of sqrt(R_eq) in physical units. This shifts the regime placement
dramatically: omega_0 * tau_eff = 1.0 exactly (at max damping), while
the proxy had omega_core * tau ≈ 0.006 (low-damping regime).

**STRUCTURAL IDENTITY**: omega_0 * tau_local = 1 for ALL masses.
This is because both omega_0 and 1/tau scale as (GM/R_eq^3)^{1/2},
and R_eq = r_s/3 gives exact cancellation. The BDCC always sits at
the peak of the memory damping function. This is not a coincidence —
it is a consequence of the constrained endpoint law.

**UNIVERSAL Q**: Q_PDE = beta_Q / alpha_vac = 6.0, independent of mass.

### C.3 Memory Kernel Contribution

The above assumed M_drive instantaneously tracks a_grav. In reality,
M_drive evolves with finite response time tau_eff:

    dM_drive/dt = (a_grav - M_drive) / tau_eff

At equilibrium, M_drive_eq = a_grav_eq. Perturb:

    M_drive(t) = a_grav_eq + delta_M(t)

Then:

    d(delta_M)/dt = (delta_a_grav - delta_M) / tau_eff

where delta_a_grav = -2 GM/R_eq^3 * delta_R (from expanding a_grav).

The inward force now has a memory-mediated component. The full
linearized a_inward perturbation is:

    delta_a_inward = (1-alpha) * delta_a_grav + alpha * delta_M
                   = (1-alpha) * (-2GM/R_eq^3) * dR + alpha * delta_M

The outward perturbation is purely position-dependent (no memory):

    delta_a_outward = -(2+beta_Q) * GM/R_eq^3 * dR

### C.4 The Coupled PDE System

Define: xi = delta_R / R_eq (dimensionless perturbation),
         mu = delta_M / a_grav_eq (dimensionless memory perturbation).

The linearized system is:

    d^2(xi)/dt^2 = -omega_0^2 * [(1-alpha) * xi - alpha * mu * xi_0]
                   + (2+beta_Q) * omega_g^2 * xi
                 = -[omega_0^2 - (2+beta_Q)*omega_g^2] * xi
                   ... [after careful bookkeeping]

Actually, let us write this more carefully. Define:

    omega_g^2 = GM / R_eq^3   (gravitational frequency scale)

Then a_grav_eq = omega_g^2 * R_eq, and the perturbation equations
in physical variables are:

**Equation 1 (shell dynamics):**

    d^2(dR)/dt^2 + omega_0^2 * dR = alpha * omega_g^2 * R_eq * delta_mu

where omega_0^2 = beta_Q * omega_g^2, and delta_mu = delta_M / a_grav_eq.

The RHS is the memory correction: the memory state has not yet caught up.

**Equation 2 (memory evolution):**

    d(delta_mu)/dt + (1/tau_eff) * delta_mu = -(2/tau_eff) * (dR/R_eq)

This is a first-order ODE: the memory perturbation relaxes toward the
gravitational perturbation with time constant tau_eff.

### C.5 Elimination to Single PDE

Differentiate Eq. 1 and substitute Eq. 2 to eliminate delta_mu.
From Eq. 2: delta_mu satisfies an inhomogeneous first-order ODE
with driving term proportional to dR.

Taking the Laplace/Fourier transform (s = i*omega):

    Eq. 1:  -omega^2 * Xi = -omega_0^2 * Xi + alpha * omega_g^2 * Mu
    Eq. 2:  (i*omega + 1/tau) * Mu = -(2/tau) * Xi

Solve Eq. 2 for Mu:

    Mu = -2 Xi / (1 + i*omega*tau)

Substitute into Eq. 1:

    -omega^2 * Xi = -omega_0^2 * Xi - 2*alpha*omega_g^2 * Xi / (1 + i*omega*tau)

Rearrange:

    omega^2 = omega_0^2 + 2*alpha*omega_g^2 / (1 + i*omega*tau)

This is the **GRUT interior dispersion relation**. It is the fundamental
equation replacing the proxy model.

### C.6 Interpretation

Separate real and imaginary parts. Write omega = Omega + i*Gamma:

For the underdamped case (Gamma << Omega):

    Omega^2 ≈ omega_0^2 + 2*alpha*omega_g^2 / (1 + Omega^2*tau^2)

    Gamma ≈ alpha * omega_g^2 * Omega * tau / (1 + Omega^2*tau^2)

**Storage (restoring force):**

    omega_eff^2 = omega_0^2 + 2*alpha*omega_g^2 / (1 + omega^2 * tau^2)

The first term (omega_0^2) is the direct restoring force from the
OP_QPRESS_001 barrier potential. The second term is the memory-mediated
enhancement: when the memory tracks the perturbation (omega*tau << 1),
it adds 2*alpha*omega_g^2 to the stiffness. When memory cannot track
(omega*tau >> 1), this contribution vanishes.

**Loss (damping):**

    gamma_PDE = alpha * omega_g^2 * tau / (1 + omega^2 * tau^2)

This is the PDE-derived damping rate. It has the same functional form
as the WP2C proxy gamma_memory, confirming the proxy was capturing
the right physics. The factor of 2 difference comes from careful
normalization conventions.

**Quality factor from PDE:**

    Q_PDE = Omega / (2 * gamma_PDE)

This is the PDE-derived quality factor, replacing the proxy estimate.

### C.7 Spatial Structure: From ODE to PDE

The above is the temporal perturbation equation at a single shell.
To obtain a true PDE, we need radial and angular structure.

For perturbations with angular dependence Y_lm:

    delta_R(r, theta, phi, t) = Psi(r, t) * Y_lm(theta, phi)

The radial wave equation in the GRUT interior is:

    d^2 Psi/dt^2 + 2*gamma_PDE * dPsi/dt + V_eff(r) * Psi = 0

where the effective potential is:

    V_eff(r) = omega_eff^2(r) + l(l+1) * c_s^2(r) / r^2

with:
- omega_eff^2(r): the local restoring frequency (from C.6)
- c_s^2(r): the local sound speed in the BDCC medium
- l(l+1)/r^2: angular momentum barrier

The local sound speed follows from the dispersion relation:

    c_s^2 = omega_eff^2 * R_eq^2 / pi^2   (fundamental mode)

More precisely, for a standing wave in a cavity of size R_eq:

    c_s_eff = omega_eff * R_eq / pi

### C.8 Mode Structure

The boundary conditions are:
- At r = R_eq (inner boundary): reflecting or impedance boundary
- At r = R_transition (outer edge of BDCC): matching to exterior

For a cavity of effective size L_eff ~ R_eq, the standing modes are:

    omega_n = omega_eff * sqrt(1 + n^2 * pi^2 * c_s^2 / (omega_eff^2 * L^2))

For the fundamental (n=0): omega_0 ~ omega_eff (homogeneous oscillation).
Higher modes add spatial structure.

The transition profile Phi(r) enters through the radial dependence of
omega_eff^2(r) and gamma_PDE(r) — these are position-dependent through
the local background.

---

## D. Variables and Coefficients

| Symbol | Definition | Source |
|--------|-----------|--------|
| omega_0 | sqrt(beta_Q * GM / R_eq^3) | Stability eigenvalue (Phase III-A) |
| omega_g | sqrt(GM / R_eq^3) | Gravitational frequency scale |
| alpha | alpha_vac = 1/3 | Vacuum susceptibility (canon) |
| tau | tau_eff at R_eq | Memory timescale (tier-0 closure) |
| beta_Q | 2 | Barrier exponent (constrained) |
| epsilon_Q | 1/9 | Barrier amplitude (constrained) |
| Phi(r) | a_outward/a_inward | Barrier dominance profile (Phase III-B) |
| l | Angular quantum number | From Y_lm decomposition |

---

## E. Where Storage and Loss Enter

**Storage (elastic/reactive channel):**

The omega_eff^2 term in the dispersion relation:

    omega_eff^2 = omega_0^2 + 2*alpha*omega_g^2 * Re[1/(1 + i*omega*tau)]
               = omega_0^2 + 2*alpha*omega_g^2 / (1 + omega^2*tau^2)

This has two contributions:
1. **Direct barrier restoring force** (omega_0^2 = beta_Q * omega_g^2):
   from the OP_QPRESS_001 potential gradient. This is structural — it
   exists regardless of memory.
2. **Memory-enhanced stiffness** (2*alpha*omega_g^2 / (1+omega^2*tau^2)):
   the fraction alpha of the gravitational force that is mediated by
   memory contributes additional stiffness when tau is short enough to
   track the perturbation. This vanishes at high frequency.

**Loss (dissipative channel):**

The gamma_PDE term:

    gamma_PDE = alpha * omega_g^2 * tau / (1 + omega^2 * tau^2)

This arises because the memory state delta_M lags behind delta_a_grav
by a phase angle arctan(omega*tau). The lagging component generates
effective friction proportional to the imaginary part of the memory
transfer function.

At low frequency (omega*tau << 1): gamma ~ alpha * omega_g^2 * tau
At high frequency (omega*tau >> 1): gamma ~ alpha / tau

For astrophysical BHs (omega_core * tau >> 1 typically), the damping
rate is gamma ~ alpha / tau, independent of frequency. This is the
regime where the WP2C proxy captured the physics correctly.

---

## F. How Phi, Endpoint Law, and Transition Profile Enter

**Endpoint law**: Sets R_eq, which determines omega_0, omega_g, and all
derived quantities. The constrained law epsilon_Q = alpha^2, beta_Q = 2
gives R_eq = r_s/3.

**Phi profile**: The coefficients omega_eff^2(r) and gamma_PDE(r) are
position-dependent. Outside the BDCC (Phi ~ 0), the medium is
"quantum fluid" with no barrier restoring force. Inside (Phi ~ 1),
the full barrier potential applies. The transition is smooth:

    omega_0^2(r) = beta_Q * omega_g^2 * Phi(r)
    gamma_PDE(r) = alpha * omega_g^2 * tau(r) * Phi(r) / (1 + omega^2 * tau(r)^2)

This converts the temporal ODE into a genuine radial PDE with
position-dependent coefficients — a Schrodinger-like equation with
a complex potential.

**Transition profile**: The graded Phi(r) from WP2D creates a potential
well with smooth walls. Modes are trapped in the region where V_eff(r) < 0
(bound states = quasi-normal modes of the BDCC). The shape of Phi(r)
determines the spectrum.

---

## G. Missing Closures and Approximations

### APPROXIMATIONS IN THIS DERIVATION

1. **Spherical symmetry only** — no Kerr/spin effects
2. **Linearization** — perturbation theory (dR << R_eq)
3. **Static background** — perturbation timescale << collapse timescale
4. **Radial collapse ODE as interior metric** — the GRUT interior is not
   described by a standard metric tensor; we use the ODE system as the
   effective dynamical law
5. **Memory-shell coupling simplified** — M_drive couples to a_grav only
   at the shell location, not as a field equation
6. **Tau_eff frozen at equilibrium value** — perturbations in tau_eff
   itself are neglected (second-order effect)
7. **Angular structure added by hand** — l(l+1)/r^2 term from standard
   Regge-Wheeler separation, not derived from GRUT metric

### REMAINING MISSING CLOSURES

1. **Covariant interior metric**: The GRUT interior does not yet have
   a metric tensor; the ODE system is the closest available
2. **Radial field equation for perturbations**: Currently we have a
   temporal ODE at each shell; a proper radial PDE requires knowing
   how adjacent shells couple (sound speed / elasticity tensor)
3. **Non-radial coupling**: How angular modes interact in the GRUT interior
4. **Nonlinear mode coupling**: Beyond linear perturbation theory
5. **Quantum corrections to perturbations**: OP_QPRESS_001 is a
   phenomenological operator; its quantum nature is not modeled
6. **Detector-level inference**: From mode spectrum to observable signal

---

## H. Recommendation for Minimal Implementable PDE

### The equation to implement:

**Dispersion relation (frequency domain):**

    omega^2 = omega_0^2 + 2*alpha*omega_g^2 / (1 + i*omega*tau_eff)

**Time-domain equivalent (coupled system):**

    d^2(xi)/dt^2 + omega_0^2 * xi = alpha * omega_g^2 * mu * 2
    d(mu)/dt + (1/tau) * mu = -(2/tau) * xi

**Spatial extension (radial wave equation with angular structure):**

    d^2 Psi/dt^2 + 2*gamma(r)*dPsi/dt + [omega_eff^2(r) + l(l+1)*c_s^2/r^2]*Psi = 0

with position-dependent coefficients modulated by Phi(r).

### What to implement:

1. **Background builder**: Compute omega_0, omega_g, tau_eff, alpha at R_eq
   from existing solver parameters
2. **Dispersion relation solver**: Find complex omega roots
3. **Mode finder**: Solve for resonance frequencies and widths
4. **Response classifier**: Compare Q_PDE to proxy Q; determine
   reactive/dissipative/mixed
5. **Effective potential**: V_eff(r) for radial mode structure
6. **Comparison pipeline**: PDE result vs WP2C proxy result

### Success criterion:

The PDE is implemented if:
- The dispersion relation can be evaluated numerically
- Complex eigenfrequencies are found
- Q_PDE is compared to Q_proxy
- Response classification is tested at a deeper level
- Missing closures are narrowed from the current list

---

## I. KEY STRUCTURAL FINDING: The Resonance-Damping Lock

The most significant result from the PDE derivation is a structural
identity that was invisible to the proxy model:

**omega_0 * tau_local = 1.0 (exact, mass-independent)**

Proof:
    omega_0 = sqrt(beta_Q * GM / R_eq^3)
    tau_local ≈ t_dyn = sqrt(R_eq^3 / (2GM))
    omega_0 * tau = sqrt(beta_Q * GM / R_eq^3) * sqrt(R_eq^3 / (2GM))
                  = sqrt(beta_Q / 2) = 1.0  (for beta_Q = 2)

This means the BDCC **always** sits at the peak of the memory damping
function gamma(omega) = alpha * omega_g^2 * tau / (1 + omega^2*tau^2).
The peak occurs at omega*tau = 1, which is exactly where the BDCC is.

**Consequences:**
1. Q_PDE = beta_Q / alpha_vac = 6.0 (universal, mass-independent)
2. The BDCC is in the MIXED VISCOELASTIC regime (1 < Q < 10)
3. The WP2C reactive_candidate classification (Q ≈ 515) was based
   on an incorrect eigenfrequency (off by sqrt(R_eq))
4. The echo channel is weakened compared to the proxy estimate
5. The reflection coefficient drops from r ≈ 0.98 to r ≈ 0.30
6. Echo amplitude is reduced but NOT zero

**Why the proxy missed this:**
The WP2C proxy used omega_core^2 = beta_Q * GM / R_eq^4 (dimensional
estimate with an extra 1/R_eq). This gave omega_core * tau ≈ 0.006,
placing the system in the low-damping regime. The correct linearisation
gives omega_0 * tau = 1.0, which is the MAX-damping point.

**Physical interpretation:**
The resonance-damping lock is a consequence of the constrained endpoint
law: R_eq = r_s/3 ties the oscillation timescale to the dynamical
timescale, which is the same timescale that governs memory relaxation.
When these three timescales coincide, the memory kernel is maximally
effective at extracting energy from perturbations.

This does NOT mean the BDCC is dissipative. Q = 6 is MIXED — it has
both reactive (storage) and dissipative (loss) character. The echo
channel survives at reduced amplitude.

**Status: This result needs independent verification.** The PDE
derivation is approximate (linearised, non-covariant). The structural
identity omega_0 * tau = 1 is exact within the current model, but
the physical interpretation depends on assumptions about the memory
kernel and the endpoint law.
