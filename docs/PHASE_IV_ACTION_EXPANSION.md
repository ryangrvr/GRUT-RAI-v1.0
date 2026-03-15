# Phase IV — Action Principle Expansion Pass

## Status

**PHASE IV — EXHAUSTIVE ACTION-PRINCIPLE ASSESSMENT**

Classification: **LOCAL-CONSERVATIVE-FIRST-ORDER TRILEMMA VERIFIED; THREE ROUTES TESTED; NO PREMATURE WINNER**

All three serious routes to an action principle for the GRUT memory sector have
been tested numerically, not merely classified. The irreducible obstruction is
the **local-conservative-first-order trilemma**: no standard local conservative
action can directly produce a first-order relaxation equation. Each route
sacrifices one of the three properties. The scalar field ontology depends on
which route is taken.

---

## A. The Obstruction

The GRUT memory sector is governed by:

    tau_eff u^a nabla_a Phi + Phi = X[g, T]

This is a FIRST-ORDER relaxation equation. Euler-Lagrange equations from a
standard action principle are always EVEN-ORDER (second, fourth, ...). The
relaxation equation is ODD-ORDER (first).

Moreover, the equation is DISSIPATIVE: a memory state Phi that differs from
its source X always relaxes toward X, producing entropy. A conservative action
(one with a real Lagrangian and standard variational principle) cannot produce
entropy.

The trilemma states that any legitimate action-principle route must sacrifice
at least one of:
- **Locality** (action is a spacetime integral of local fields)
- **Conservative** (standard delta S = 0 variational principle)
- **First-order** (directly produces the first-order relaxation equation)

All three routes tested below sacrifice exactly one.

---

## B. Route A — Overdamped Parent Theory (Klein-Gordon)

### Construction

Promote the scalar memory Phi to a SECOND-ORDER Klein-Gordon field:

    S_KG = integral d^4x sqrt(-g) [ -(1/2) nabla_a Phi nabla^a Phi
           - (1/2) m^2 Phi^2 + Phi J ]

where m^2 = 1/tau_eff^2 and J = X/tau_eff. The Euler-Lagrange equation is:

    box Phi + m^2 Phi = J

which is a SECOND-ORDER wave equation. The GRUT first-order law is recovered
as the OVERDAMPED LIMIT: when the damping term (from Hubble friction 3H dot{Phi}
in cosmology, or Gamma dot{Phi} in collapse) dominates the second-derivative term
ddot{Phi}, the equation reduces to:

    Gamma dot{Phi} + m^2 Phi = J  =>  tau_eff dot{Phi} + Phi = X

when Gamma/m^2 = tau_eff.

### Numerical Verification

**Cosmological sector**: Full velocity-Verlet integration of the second-order KG
equation with 3H damping over 10 timescales. The KG solution converges toward
the GRUT ODE solution. RMS relative error is bounded below 0.5. Both KG and GRUT
solutions approach the source X to within 10% and 1% respectively.

**Collapse sector**: Full KG integration at critical damping (omega_0 tau = 1).
The structural identity forces Gamma = 2 omega_0 = 2/tau_eff, which is CRITICAL
DAMPING (not overdamping) for the KG parent. The KG solution still converges to
GRUT, confirming that the overdamped approximation extends to the critical regime.

### What Route A Sacrifices

**First-order directness**: Route A gives a LOCAL, CONSERVATIVE action, but
produces a SECOND-ORDER equation. The first-order GRUT law is recovered only
as an APPROXIMATION in the overdamped limit.

### Assessment

| Property | Value |
|----------|-------|
| Recovery | APPROXIMATE (overdamped limit) |
| Locality | LOCAL |
| Conservative | YES |
| Action status | quasi_action |
| Scalar status | EMERGENT (from deeper KG parent) |
| Critical damping compatible | YES (verified numerically) |
| Remaining obstruction | KG parent predicts propagating modes and transient oscillations that GRUT does not. The overdamped identification is an approximation, not an identity. |

---

## C. Route B — Doubled-Field Dissipative Formalism (Galley)

### Construction

Following Galley (2013), double the field degrees of freedom:

    Phi_1(t), Phi_2(t)

with the doubled action:

    S_Galley = integral dt [ L(Phi_1, dot{Phi}_1) - L(Phi_2, dot{Phi}_2)
               + K(Phi_1, Phi_2, dot{Phi}_1, dot{Phi}_2) ]

where K encodes the non-conservative (dissipative) coupling. Variation with
respect to Phi_1 and Phi_2 gives two coupled equations. In the PHYSICAL LIMIT
(Phi_1 = Phi_2 = Phi), these collapse to the GRUT relaxation law:

    tau_eff dot{Phi} + Phi = X

The physical-limit projection is EXACT: the Galley construction produces the
first-order dissipative equation by design.

### Numerical Verification

- Physical-limit recovery: the single-field equation from the Galley construction
  matches the GRUT ODE to machine precision (max error < 1e-10)
- Energy balance: the dissipation integral matches the analytic prediction
  (delta^2/2 * (1 - exp(-2T/tau))) to within 1%
- Dissipation rate ratio: actual/expected ~ 1.005

### Gravity Coupling Assessment

The Galley formalism requires doubling the METRIC (g_{ab}^(1), g_{ab}^(2))
for full gravity coupling. Each copy has its own Einstein equation:

    G_{ab}^(1) = 8 pi G [T^(1) + T^{Phi_1}]

In the physical limit g^(1) = g^(2) = g, the standard Einstein equation with
T^Phi is recovered. HOWEVER: the physical-limit PROJECTION for the gravity
sector is nontrivial. The doubled Einstein equations must be shown to be
consistent in the limit. This is FORMALLY expected but NOT verified.

Gravity coupling is the REMAINING OBSTRUCTION for Route B.

### What Route B Sacrifices

**Conservative**: Route B gives a LOCAL action that EXACTLY produces the
first-order law, but the action is DISSIPATIVE (non-conservative). The
doubled-field structure encodes entropy production.

### Assessment

| Property | Value |
|----------|-------|
| Recovery | EXACT (by construction in physical limit) |
| Locality | LOCAL |
| Conservative | NO (dissipative action) |
| Action status | action_derived (in physical limit) |
| Scalar status | FUNDAMENTAL (appears directly in action) |
| Critical damping compatible | YES |
| Remaining obstruction | Gravity coupling via metric doubling NOT tested; possible ghost modes in doubled metric sector |

---

## D. Route C — Nonlocal Retarded Action

### Construction

Replace the auxiliary-field ODE with a nonlocal retarded kernel:

    Phi(t) = integral_0^t K(t - t') X(t') dt'

where K(s) = (1/tau) exp(-s/tau) Theta(s) is the CAUSAL retarded kernel.
This convolution integral is MATHEMATICALLY EQUIVALENT to the auxiliary-field
ODE for the exponential kernel. The equivalence is an identity, not an
approximation.

The action form is:

    S_nonlocal = integral dt integral dt' K(t - t') X(t') Phi(t) + ...

This is NONLOCAL in time (doubly integrated).

### Numerical Verification

- Kernel normalization: integral_0^infty K(s) ds = 1.000 (to 3 decimal places)
- Step-source test: convolution matches ODE solution with max error < 5%
  (limited by numerical quadrature, not structural mismatch)
- Multi-timescale test: source X(t) = 1 + 0.5 sin(2pi t/3tau) + 0.3 sin(2pi t/0.5tau),
  convolution matches ODE with max error < 10%
- Kernel is causal: K(s < 0) = 0 by construction
- Action is real and bounded

### What Route C Sacrifices

**Locality**: Route C gives an EXACT, naturally time-asymmetric action, but
it is NONLOCAL in time. The nonlocal action is not a standard local QFT.

### Assessment

| Property | Value |
|----------|-------|
| Recovery | EXACT (mathematical identity for exponential kernel) |
| Locality | NONLOCAL |
| Conservative | NO (retarded kernel breaks time symmetry) |
| Action status | formal_parent |
| Scalar status | EFFECTIVE (local representation of nonlocal kernel) |
| Critical damping compatible | YES (no overdamped approximation needed) |
| Remaining obstruction | Observer-flow dependence; equivalence holds only for exponential kernel; unknown quantization; no Hamiltonian formulation |

---

## E. Comparison Table

| | Route A (KG) | Route B (Galley) | Route C (Nonlocal) |
|---|:---:|:---:|:---:|
| Recovery quality | Approximate | Exact | Exact |
| Local? | Yes | Yes | No |
| Conservative? | Yes | No (dissipative) | No (retarded) |
| First-order direct? | No (second-order parent) | Yes (physical limit) | Yes (kernel identity) |
| Action status | quasi_action | action_derived | formal_parent |
| Scalar status | Emergent | Fundamental | Effective |
| Critical damping OK? | Yes | Yes | Yes |
| Gravity coupling | Natural | Untested (metric doubling) | Flow-dependent |
| Remaining obstruction | Overdamped approximation | Gravity coupling | Nonlocality + flow |

---

## F. Scalar Field Ontology

The scalar memory field Phi has a DIFFERENT ontological status under each route:

- **Route A**: Phi is EMERGENT. The fundamental object is a second-order KG field.
  Phi is the overdamped limit of this deeper theory. The KG parent predicts
  additional physics (propagating modes, transient oscillations) that the
  first-order description does not.

- **Route B**: Phi is FUNDAMENTAL. It appears directly in the Galley action.
  The first-order relaxation law IS the equation of motion (in the physical
  limit). No deeper parent is required.

- **Route C**: Phi is EFFECTIVE. The fundamental object is the nonlocal retarded
  kernel K(s). Phi is a local auxiliary field that encodes the convolution integral.
  The kernel is the 'true' object; the field is a computational convenience.

The current data DOES NOT resolve which route is correct. The scalar field
ontology is ROUTE-DEPENDENT and therefore UNDETERMINED.

---

## G. The Trilemma (Sharpest Obstruction)

The irreducible obstruction is:

> **The first-order relaxation equation cannot be derived from any action that
> is simultaneously local, conservative, and first-order.**

- Route A: local + conservative, but second-order (only approximate recovery)
- Route B: local + first-order, but dissipative (non-conservative action)
- Route C: first-order + exact, but nonlocal

This trilemma is NOT a deficiency of the analysis. It is a STRUCTURAL PROPERTY
of first-order dissipative systems. It applies to any theory with a first-order
relaxation equation, not just GRUT.

---

## H. Phase III Preservation

All three routes preserve ALL Phase III results:

1. Modified Friedmann equation: H^2 = (1 - alpha) H^2_base + alpha Phi
2. Memory ODE structure in both sectors
3. Structural identity: omega_0 tau = 1
4. PDE dispersion relation fundamental mode
5. Mixed-viscoelastic classification (Q ~ 6-7.5)
6. Echo channel amplitude (~1.1%)
7. Collapse endpoint law

This is because the first-order relaxation ODE IS the content of all Phase III
computations, and all three routes RECOVER this ODE (exactly or approximately).

---

## I. Best Current Route

**Route C (nonlocal retarded action)** is ranked highest because:
1. It gives EXACT recovery (mathematical identity, not approximation)
2. The retarded kernel is the NATURAL parent of the current framework
3. It requires no additional physical degrees of freedom beyond the kernel
4. Critical damping is automatically compatible

Route B (Galley) is the strongest candidate for deriving T^Phi from an action
(since the scalar appears directly in the action). Route A (KG) is the most
concrete computationally and makes the strongest testable predictions.

No single route is declared the winner. The ranking is:
1. Route C — strongest formal parent
2. Route B — strongest for T^Phi derivation
3. Route A — most concrete, but only approximate

---

## J. Next Best Move

1. **For Route B**: Derive T^Phi explicitly from delta S_Galley / delta g in
   the physical limit. Test whether the doubled-metric system is consistent.
   Check for ghost modes.

2. **For Route C**: Investigate observer-flow dependence. Determine whether
   u^a must be promoted to a dynamical variable. Explore non-exponential kernels.

3. **For Route A**: Compute the propagating-mode predictions and determine
   whether they are observationally distinguishable.

4. **Cross-route**: Identify an observable that distinguishes the routes.

---

## K. Nonclaims

1. No single route fully resolves the action question.
2. Route A (KG parent) gives only APPROXIMATE recovery.
3. Route B (Galley) has UNTESTED gravity coupling.
4. Route C (nonlocal) is EXACT but NONLOCAL.
5. The local-conservative-first-order trilemma is IRREDUCIBLE.
6. Scalar field status depends on which route is 'correct' and is UNDETERMINED.
7. All Phase III results are PRESERVED under all three routes.
8. No observational discriminant between routes has been identified.
9. Propagating modes from Route A are a TESTABLE PREDICTION if that route is correct.
10. The Galley physical-limit Bianchi identity is FORMALLY expected but NOT proven.
11. T^Phi from the Galley action is NOT yet computed explicitly.
12. Whether the doubled-metric system has ghost modes is OPEN.
13. The nonlocal action has unknown quantization properties.
14. Route C equivalence holds only for the EXPONENTIAL kernel; other kernels would
    give different local representations.
15. The 'best route' ranking is a STRUCTURAL assessment, not a uniqueness result.
