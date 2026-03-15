# Phase IV Package 1: Action Principle Program

## Status

**PHASE IV — FIRST FOUNDATIONAL PASS**

Classification: **CONSTITUTIVE-EFFECTIVE WITH SHARPLY DEFINED OBSTRUCTION**

The GRUT memory sector cannot be directly embedded in a standard (conservative)
variational principle. The obstruction is structural: the first-order relaxation
equation is inherently dissipative, producing entropy and breaking time-reversal
symmetry. Four candidate routes to an action have been evaluated. The strongest
current formulation is an **auxiliary-field realization of the nonlocal retarded
kernel**, which reproduces the memory ODE in the overdamped/adiabatic limit
but does NOT fully derive the GRUT dynamics from a single stationary-action
principle.

---

## A. Closure Target

Find the strongest honest formulation of the GRUT memory sector at the
action / quasi-action / constitutive-fundamental level, such that:

1. Bianchi identity is satisfied (conservation guaranteed by diffeomorphism
   invariance of the action, not imposed)
2. Both weak-field (cosmological) and strong-field (collapse) sectors are
   recovered
3. The structural identity omega_0 * tau = 1 is preserved
4. The classification of the result is sharp: action-derived, quasi-action,
   or constitutive-effective with obstruction

---

## B. Candidate 1 — Local Scalar Action (Klein-Gordon type)

### Formulation

S_memory = integral d^4x sqrt(-g) [ -(1/2) g^{ab} nabla_a Phi nabla_b Phi
           - V(Phi) + Phi J[g, T] ]

where:
- V(Phi) = Phi^2 / (2 tau_eff^2) is a mass term
- J[g, T] = X[g,T] / tau_eff is a source current
- X = H^2_base (cosmological) or a_grav (collapse)

### Equation of Motion

Variation delta S / delta Phi = 0 gives:

  box Phi + m^2 Phi = J

where box = g^{ab} nabla_a nabla_b is the covariant d'Alembertian and
m^2 = 1/tau_eff^2.

This is a SECOND-ORDER wave equation. The GRUT memory ODE is FIRST-ORDER:

  tau_eff u^a nabla_a Phi + Phi = X

### Overdamped Limit

The Klein-Gordon equation can be written as:

  tau_eff^2 box Phi + Phi = tau_eff^2 J

In the overdamped limit (spatial gradients and second time derivatives
negligible compared to the mass term), this reduces to:

  Phi approx tau_eff^2 J = X

At first order beyond the algebraic limit, the cosmological reduction gives:

  tau_eff dPhi/dt + Phi approx X + O(tau_eff^2 d^2Phi/dt^2)

This RECOVERS the GRUT memory ODE as the leading-order overdamped
approximation, with corrections at O(tau_eff^2 ddot{Phi}).

### Assessment

- **Status**: QUASI-ACTION CANDIDATE
- **Recovers memory ODE**: Yes, in overdamped limit only
- **Bianchi compatible**: Yes — derived from diffeomorphism-invariant action
- **Obstruction**: The full Klein-Gordon dynamics include propagating wave
  modes absent from the GRUT effective framework. The memory ODE is an
  APPROXIMATION of the Klein-Gordon dynamics, not an exact consequence.
- **Wave modes**: The Klein-Gordon field propagates at c/sqrt(1 + omega^2 tau^2).
  These modes are NOT part of the current GRUT framework.
- **Falsifiable prediction**: If the local scalar action is correct, the memory
  field should exhibit propagating modes at frequencies omega >> 1/tau_eff.
  No observational constraint on this currently exists.

---

## C. Candidate 2 — Doubled-Field Dissipative Formalism (Galley type)

### Formulation

Following Galley (2013), the dissipative system is described by doubling
the degrees of freedom: introduce Phi_1 (physical) and Phi_2 (auxiliary),
with the combined action:

  S_Galley = integral d^4x sqrt(-g) [ L(Phi_1) - L(Phi_2)
             + K_diss(Phi_1, Phi_2, dPhi_1/dt, dPhi_2/dt) ]

where K_diss is a dissipation kernel that breaks time-reversal symmetry
in a controlled way. The physical limit is Phi_1 = Phi_2 = Phi.

For the GRUT relaxation equation, the dissipation kernel must enforce:

  tau_eff u^a nabla_a Phi + Phi = X

This requires:
  K_diss ~ (Phi_1 - Phi_2) * (tau_eff u^a nabla_a (Phi_1 + Phi_2)/2)

### Assessment

- **Status**: FORMAL FRAMEWORK — applicable in principle
- **Recovers memory ODE**: Yes, by construction (the formalism is designed
  for first-order dissipative equations)
- **Bianchi compatible**: Yes — the doubled action is diffeomorphism-invariant
  if both copies transform covariantly
- **Obstruction**: The physical interpretation of the auxiliary field Phi_2
  is unclear in the gravitational context. The Galley formalism was developed
  for classical dissipative mechanics, not covariant field theory coupled
  to gravity. The "physical limit" Phi_1 = Phi_2 = Phi must be taken
  after variation, which complicates the coupling to Einstein equations.
- **Status of Bianchi**: The doubled action does have a Bianchi identity
  for the full doubled system. The physical-limit Bianchi identity is
  inherited but the projection is nontrivial for the gravitational coupling.
- **Unique advantage**: This is the ONLY formalism that directly produces
  first-order dissipative equations from an action principle.
- **Unique disadvantage**: No prior application to gravity-coupled scalar
  field with retarded memory. The formalism is proven for point-particle
  dissipation (radiation reaction, friction), not for field-theoretic
  cosmology.

---

## D. Candidate 3 — Nonlocal Retarded Action

### Formulation

S_nonlocal = S_EH[g] + S_matter[g, psi]
           + integral d^4x d^4x' sqrt(-g(x)) sqrt(-g(x'))
             G_ret(x, x') S_{ab}(x') g^{ab}(x)

where:
- G_ret(x, x') = (1/tau_eff) exp(-sigma(x,x')/tau_eff) Theta(t - t')
  is the retarded Green's function of the relaxation operator
- sigma(x, x') is the proper-time separation along the observer flow
- S_{ab} is the memory source tensor (X[g,T] projected onto the metric)

### Variation

delta S_nonlocal / delta g^{ab}(x) produces the nonlocal Einstein equations:

  G_{ab}(x) = (8piG/c^4) [ T_{ab}(x) + integral G_ret(x,x') S_{ab}(x') d^4x' ]

The memory contribution is the retarded convolution integral:

  T^Phi_{ab}(x) = integral_0^infty K(s) X_{ab}(t - s) ds

where K(s) = (1/tau) exp(-s/tau) Theta(s).

### Equivalence to Auxiliary Field

For the exponential kernel K(s) = (1/tau) exp(-s/tau), the convolution
integral is EXACTLY equivalent to the solution of the auxiliary-field
relaxation equation:

  tau dPhi/dt + Phi = X   =>   Phi(t) = integral_0^infty K(s) X(t-s) ds

This equivalence holds:
- Along a single observer flow (worldline or FRW comoving family)
- For the exponential kernel specifically
- At the level of the ODE solution
- It does NOT guarantee equivalence in all covariant settings (different
  slicings, multiple intersecting observers, caustic formation)

### Assessment

- **Status**: FORMAL PARENT
- **Recovers memory ODE**: Exactly, for exponential kernel along observer flow
- **Bianchi compatible**: The nonlocal action is diffeomorphism-invariant if
  the kernel transforms as a bi-scalar
- **Obstruction**: The variation of the nonlocal action is well-defined
  formally but requires careful regularization at coincidence points
  (x = x'). The observer-flow dependence of the kernel means the theory
  is observer-dependent unless the flow field is dynamical.
- **Foundational role**: This is the PARENT formulation from which the
  auxiliary-field realization (Candidate 4) is derived as the local
  equivalent for exponential kernels.

---

## E. Candidate 4 — Auxiliary-Field Realization of Nonlocal Kernel

### Formulation

Introduce Phi as an auxiliary field that localizes the nonlocal retarded
kernel. The system is:

  G_{ab} = (8piG/c^4) (T_{ab} + T^Phi_{ab})
  tau_eff u^a nabla_a Phi + Phi = X[g, T]

where T^Phi_{ab} is the constitutive stress-energy tensor determined by
combined conservation (as derived in Package A of Phase III).

This is NOT a standard action principle. Instead, it is an
INITIAL-VALUE FORMULATION with:
- Einstein equations for the metric (second-order)
- Relaxation equation for the memory field (first-order)
- Conservation as a consistency condition

### Relationship to Other Candidates

- Equivalent to Candidate 3 for exponential kernel along observer flow
- Recoverable from Candidate 1 in the overdamped limit
- Potentially derivable from Candidate 2 in the physical limit
- The constitutive T^Phi_{ab} plays the role that a Lagrangian-derived
  stress-energy would play in a fully action-derived theory

### Assessment

- **Status**: PREFERRED EFFECTIVE FRAMEWORK (extends Phase III Candidate 2)
- **Recovers memory ODE**: By construction (the relaxation equation IS
  the memory ODE)
- **Bianchi compatible**: At the effective level — combined conservation
  is imposed, not proven from an action
- **Obstruction**: T^Phi_{ab} is not derived from delta S / delta g^{ab}.
  It is constitutively determined. This means conservation is a constraint,
  not a consequence. The auxiliary field Phi has no kinetic term in the
  action (it is determined by a first-order equation, not a second-order
  wave equation). This is the FUNDAMENTAL OBSTRUCTION.
- **Why preferred**: It is the most computationally tractable formulation
  that preserves all Phase III results while being structurally compatible
  with all other candidates. It sits at the center of the candidate space.

---

## F. Obstruction Analysis

### The Fundamental Obstruction

The GRUT memory sector is governed by a first-order relaxation equation:

  tau u^a nabla_a Phi + Phi = X

Standard variational principles produce SECOND-ORDER equations of motion:

  delta S / delta Phi = 0   =>   box Phi + m^2 Phi = J   (Klein-Gordon)

The mismatch is structural:
- First-order relaxation: dissipative, entropy-producing, time-irreversible
- Second-order wave equation: conservative, entropy-preserving, time-reversible

### Sharpened Obstruction Statement

The first-order relaxation equation tau dPhi/dt + Phi = X CANNOT be the
Euler-Lagrange equation of any local, real-valued, time-independent Lagrangian
L(Phi, dPhi/dt, ...). This is because:

1. Euler-Lagrange equations are always of even order in time derivatives
   (they arise from integration by parts of the action)
2. The relaxation equation is of ODD order (first order in proper-time
   derivative)
3. No field redefinition Phi -> f(Phi) can convert a first-order equation
   to a second-order one

This obstruction is THEOREM-LEVEL: it is not a technical difficulty
but a structural impossibility within the standard variational framework.

### Bypass Routes

Three bypass routes exist, each with tradeoffs:

1. **Overdamped limit** (Candidate 1): The relaxation equation IS the
   overdamped limit of a Klein-Gordon field. This introduces propagating
   modes not present in the current framework.

2. **Doubled-field** (Candidate 2): The Galley formalism DOES produce
   first-order dissipative equations from a variational principle, but
   requires doubling the degrees of freedom and taking a physical limit.

3. **Accept nonlocality** (Candidate 3): The retarded kernel action is
   nonlocal in time. Standard field theory assumes local actions. Nonlocal
   actions are well-defined mathematically but physically controversial
   (acausality, unitarity, quantization).

### Classification of Each Route

| Route | Recovers ODE? | Bianchi? | Extra DOF? | Status |
|-------|:---:|:---:|:---:|--------|
| Klein-Gordon (overdamped) | Approx | Proven | Propagating modes | quasi-action |
| Galley doubled | Exact | Projected | Auxiliary copy | formal framework |
| Nonlocal retarded | Exact | Formal | None | formal parent |
| Auxiliary-field | By construction | Imposed | None | preferred effective |

---

## G. Weak-Field Reduction

### Recovery from Candidate 1 (Overdamped Klein-Gordon)

In FRW cosmology, the Klein-Gordon equation for Phi coupled to the
Friedmann equation reduces to:

  ddot{Phi} + 3H dot{Phi} + m^2 Phi = m^2 X

In the overdamped limit (3H >> m, or equivalently H tau >> 1):

  3H dot{Phi} + m^2 Phi approx m^2 X
  dot{Phi} + (m^2 / 3H) Phi approx (m^2 / 3H) X

With m^2 = 1/tau_eff^2 and tau_eff = tau_0 / (1 + H^2 tau_0^2):

  dot{Phi} + Phi/tau_KG approx X/tau_KG

where tau_KG = 3H tau_eff^2. This matches the GRUT memory ODE with a
modified effective timescale. The match is exact when tau_KG = tau_eff,
i.e., when 3H tau_eff = 1, which is satisfied to order unity in the
H tau_0 ~ 1 transition regime.

### Recovery from Candidate 4 (Auxiliary-Field)

By construction: the auxiliary-field formulation IS the GRUT memory ODE.
Recovery is exact with no approximation needed.

---

## H. Strong-Field Reduction

### Recovery from Candidate 1 (Overdamped Klein-Gordon)

In the collapse sector, the Klein-Gordon equation in the effective interior
metric reduces to:

  ddot{Phi} + Gamma dot{Phi} + omega_0^2 Phi = omega_0^2 X

where Gamma is the effective damping rate from the metric coefficients.
In the overdamped limit (Gamma >> omega_0):

  dot{Phi} + (omega_0^2 / Gamma) Phi approx (omega_0^2 / Gamma) X

This recovers the collapse memory ODE with tau_eff = Gamma / omega_0^2.
The structural identity omega_0 * tau = 1 is preserved when Gamma = omega_0
(critical damping), which is the condition omega_0 * tau_eff = 1.

### PDE Dispersion

The Klein-Gordon dispersion relation in the effective interior is:

  omega^2 = k^2 c_eff^2 + omega_0^2 + 2 alpha omega_g^2 / (1 + i omega tau)

This EXACTLY matches the GRUT PDE dispersion relation (interior_pde.py),
confirming structural consistency.

---

## I. Preferred Formulation

**Candidate 4: Auxiliary-field realization** is the PREFERRED formulation.

Reasons:
1. Recovers both sectors exactly (by construction)
2. Compatible with all four action candidates as different parent theories
3. Most computationally tractable
4. Preserves all Phase III results without modification
5. Leaves the action question open (does not prematurely commit to a parent)

The auxiliary-field formulation is the intersection of all candidate spaces:
every candidate, when reduced to the appropriate limit, recovers the
auxiliary-field initial-value system.

---

## J. Remaining Closures

1. **Kinetic term for Phi**: Does the memory field have a kinetic term
   (1/2)(nabla Phi)^2? If yes, propagating modes exist. If no, the field
   is purely auxiliary.

2. **Overdamped vs exact**: Is the first-order relaxation exact or an
   overdamped approximation of a deeper second-order theory?

3. **Doubled-field gravity coupling**: Can the Galley formalism be
   extended to gravity-coupled fields with consistent Bianchi identity?

4. **Kernel universality**: Is the exponential kernel K(s) = e^{-s/tau}/tau
   the unique natural kernel, or are other causal kernels possible?

5. **tau_eff curvature dependence**: First-principles derivation of
   tau_eff(R_abcd) — which curvature invariant controls it?

6. **T^Phi_{ab} from action**: Derive T^Phi_{ab} = -(2/sqrt{-g})
   delta S_memory / delta g^{ab} from a confirmed action.

7. **alpha coupling unification**: Determine whether alpha_mem and alpha_vac
   arise from the same coupling in the action.

---

## K. Nonclaims

1. This analysis does NOT produce a confirmed action for the GRUT memory sector.
2. The fundamental obstruction (first-order ODE vs second-order Euler-Lagrange)
   is structural and CANNOT be resolved within the standard variational framework.
3. The Klein-Gordon overdamped limit is an APPROXIMATION, not an exact derivation.
4. The Galley doubled-field formalism is APPLICABLE IN PRINCIPLE but has NOT been
   implemented for gravity-coupled scalar fields.
5. The nonlocal retarded action is a FORMAL PARENT, not a computationally
   tractable action principle.
6. T^Phi_{ab} remains CONSTITUTIVE — not derived from an action.
7. No quantization or quantum consistency checks have been performed.
8. The auxiliary-field formulation is PREFERRED by structural criteria,
   not by a uniqueness theorem.
9. Propagating memory-field modes (from Klein-Gordon kinetic term) are
   classified but NOT confirmed or excluded.
10. The exponential kernel is ASSUMED, not derived from first principles.
11. alpha_mem / alpha_vac unification is NOT attempted.
12. No new observational predictions emerge from this classification.
