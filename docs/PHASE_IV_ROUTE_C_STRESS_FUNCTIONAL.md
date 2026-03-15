# Phase IV — Route C: Nonlocal Retarded Stress-Functional Construction

## Status

**PHASE IV — ROUTE C STRESS-FUNCTIONAL ANALYSIS**

Classification: **FUNCTIONAL-DERIVED**

The nonlocal retarded action defines a causal, normalized kernel from which
the GRUT memory field Phi is constructed as a retarded convolution. The metric
variation of this nonlocal functional yields a nonlocal stress-functional
(not a standard local tensor). For the exponential kernel, the Markov property
allows reduction to a local T^Phi via the auxiliary field. The result is
INTERMEDIATE between constitutive-effective and action-derived.

---

## A. Mission and Context

Phase IV Action Expansion established three live action routes:
- Route A (KG parent): approximate, overdamped limit
- Route B (Galley): physical-limit derived T^Phi, but growing ghost mode
- Route C (nonlocal retarded): exact EOM recovery, mathematical identity

Route B follow-up produced a physical-limit-derived T^Phi and showed that the
physical limit is a consistent truncation but NOT an attractor (growing ghost
mode at rate phi/tau, golden ratio). Route B remains at "physical-limit derived."

The mission: advance Route C to determine whether the nonlocal retarded parent
can produce a meaningful stress-energy analogue.

---

## B. The Nonlocal Retarded Action

### B.1. Kernel Definition

The retarded kernel for the GRUT memory sector:

    K(s) = (1/tau_eff) exp(-s/tau_eff) Theta(s)

Properties:
- **Causal**: K(s) = 0 for s < 0 (no future contributions)
- **Normalized**: integral_0^infty K(s) ds = 1
- **Real**: K(s) >= 0 for all s >= 0
- **Peak at s = 0**: K(0) = 1/tau_eff
- **Monotonically decaying**: K'(s) < 0 for s > 0

### B.2. Memory Field as Retarded Convolution

The memory field is defined as a FUNCTIONAL of the metric history:

    Phi(t) = integral_{-infty}^{t} K(t - t') X[g](t') dt'

where X[g] is the local source:
- Cosmological sector: X = H^2_base = (8piG/3)*rho
- Collapse sector: X = a_grav = G*M/R^2

### B.3. Markov Property (Exponential Kernel Only)

The exponential kernel has a unique property: the retarded convolution is
equivalent to the first-order ODE:

    tau_eff dPhi/dt + Phi = X

This is the **Markov property**: the current value of Phi captures the full
past history. No other causal kernel has this property with a first-order ODE.

Consequence: two different source histories X_A(t), X_B(t) that arrive at the
same Phi(T) produce the same effective T^Phi at time T. This is verified
numerically (Markov test in nonlocal_stress.py).

### B.4. Exponential Kernel Is Special

Among all causal retarded kernels:
- Exponential: gives first-order ODE (Markov, simplest local representation)
- Power-law K(s) ~ s^{-alpha}: gives fractional-order differential equation
- Stretched exponential: gives higher-order or integral equation
- Multi-exponential: gives system of coupled first-order ODEs

The exponential kernel is the UNIQUE kernel that gives a single first-order
auxiliary-field ODE. This is why Phi exists as a simple scalar field.

---

## C. Metric Variation of the Nonlocal Action

### C.1. The Formal Functional Derivative

The metric variation delta S_nonlocal / delta g^{mu nu} formally exists.
It has contributions from five sources of implicit g-dependence:

1. **Volume element**: delta(sqrt(-g))/delta(g^{ab})
2. **Source X[g]**: the source depends on curvature (Friedmann equation)
3. **Kernel tau_eff[g]**: the timescale depends on H (tau coupling)
4. **Proper time measure**: ds along the observer flow depends on g
5. **Observer flow u^a[g]**: normalization g_{ab} u^a u^b = -1

### C.2. The Result Is Nonlocal

The full metric variation is a NONLOCAL stress-functional:

    T^Phi_{mu nu}(x) = T^Phi_{mu nu}[g_{ab}(x'); x' in past of x]

This is NOT a local tensor: it depends on the history of the metric along
the observer's past worldline, not just on the current metric state at x.

### C.3. Local Reduction for Exponential Kernel

For the exponential kernel, the Markov property gives a crucial simplification:

    T^Phi_{mu nu}(x) = F(Phi(x), X(x), nabla Phi(x), g_{mu nu}(x))

The history dependence is fully captured by the current Phi. The resulting
local T^Phi has the form of a standard minimally-coupled scalar stress-energy:

    T^Phi_{ab} = nabla_a Phi nabla_b Phi
                - g_{ab}[(1/2)(nabla Phi)^2 + V(Phi) - Phi X/tau_eff]

This is the SAME expression as Route B physical-limit T^Phi.

### C.4. Obstruction to Explicit Computation

The full metric variation has NOT been computed in closed form because:
- The functional chain rule through the retarded integral is nonstandard
- The integrand and integration domain both depend on g
- The kernel depends on the metric through tau_eff[g]
- No standard variational formula applies directly

The variation IS formally well-defined as a distribution, but computing
it explicitly requires tools from nonlocal variational calculus.

---

## D. The Stress-Functional

### D.1. Decomposition

The stress-functional decomposes into:

    T^Phi_{ab}(x) = T^Phi_instantaneous(Phi(x), X(x), g(x))
                   + T^Phi_history(integral over past metric)

### D.2. On-Shell Reduction

For the exponential kernel, when Phi satisfies the memory ODE:

    T^Phi_history = 0  (absorbed into current Phi by Markov property)
    T^Phi = T^Phi_instantaneous(Phi, X, nabla Phi, g)

This is the KEY result: the nonlocal stress-functional reduces to a LOCAL
expression when evaluated on-shell with the exponential kernel.

### D.3. Classification

The stress-functional is classified as **FUNCTIONAL-DERIVED**:
- Better than constitutive-effective: has a formal parent action
- Weaker than action-derived: the parent action is nonlocal
- The local reduction depends on the exponential kernel choice
- For other kernels, T^Phi would remain genuinely nonlocal

---

## E. Sector Reductions

### E.1. Cosmological Sector

The nonlocal retarded kernel, evaluated along the cosmological observer flow,
produces:
- Modified Friedmann: H^2 = (1-alpha_mem)*H^2_base + alpha_mem*Phi
- Memory ODE: tau_eff dPhi/dt + Phi = H^2_base
- Tau coupling: tau_eff = tau0/(1 + (H*tau0)^2)

All three are recovered. The convolution integral matches the ODE solution
to quadrature precision (verified numerically).

### E.2. Collapse Sector

The same kernel structure recovers:
- Force balance: a_eff = (1-alpha_vac)*a_grav + alpha_vac*M_drive
- Memory ODE: tau_eff dM_drive/dt + M_drive = a_grav
- Equilibrium endpoint: M_drive = a_grav at equilibrium

Both sectors use the SAME retarded kernel, differing only in the source X
and the coupling constant (alpha_mem vs alpha_vac).

---

## F. Bianchi Compatibility

### F.1. Effective-Level Verification

The modified Friedmann equation + memory ODE form a CLOSED system.
The time derivative of H^2 follows from the chain rule:

    dH^2/dt = (1-alpha)*dH^2_base/dt + alpha*dPhi/dt

This is automatically consistent with the evolution equations for rho and Phi.
The effective combined conservation nabla_mu(T^{mu nu} + T^{Phi mu nu}) = 0
is a CONSEQUENCE of this closure.

### F.2. Collapse Sector

At equilibrium: M_drive = a_grav, so a_eff = a_grav (exact). The force balance
is self-consistent by construction.

### F.3. Full Proof Status

A full proof of Bianchi compatibility from variational principles is NOT
available. This would require:
1. Computing the nonlocal metric variation explicitly
2. Showing diffeomorphism invariance of the nonlocal action
3. Handling boundary terms from the retardation constraint

The observer-flow dependence may break diffeomorphism invariance, since the
retardation condition (past along u^a) depends on the choice of observer.

---

## G. Route B vs Route C Comparison

| Property | Route B (Galley) | Route C (Nonlocal) |
|----------|:----------------:|:-----------------:|
| T^Phi expression | Standard scalar form | Same expression |
| Derivation status | Physical-limit derived | Functional-derived |
| Ghost mode | Growing at phi/tau | **NONE** |
| Stability | Not attractor (CTP needed) | **Not applicable** |
| Action type | Local doubled-field | Nonlocal retarded |
| Covariance | Observer-flow in S_diss | Observer-flow in K |
| EOM recovery | Physical-limit projection | **Exact (math identity)** |
| Bianchi | Physical-limit Bianchi | **Effective-level** |

### G.1. Route C Advantages
- No ghost mode, no doubled-field pathology
- No CTP boundary condition needed
- No stability/attractor problem
- Exact EOM recovery (mathematical identity)
- Natural parent of the current framework

### G.2. Route C Disadvantages
- Nonlocal action (not standard QFT)
- Metric variation is a nonlocal stress-functional
- Observer-flow dependent (not manifestly covariant)
- Full metric variation not computed in closed form

### G.3. Assessment

Route B and Route C are COMPLEMENTARY, not competing. Route B pays the price
in ghost/stability pathology; Route C pays the price in nonlocality. Neither
route alone resolves the fundamental obstruction: there is no simultaneously
local, conservative, and first-order action for the memory sector.

---

## H. Phi Ontology Under Route C

Under Route C, Phi is NOT a fundamental field. It is the **effective local
representation** of a nonlocal retarded process:

- The FUNDAMENTAL object is the kernel K(s) = (1/tau)exp(-s/tau)Theta(s)
- Phi exists because the exponential kernel admits a Markovian local representation
- For other kernels (power-law, stretched exponential), no simple Phi exists
- The scalar field is CONTINGENT on the kernel choice, not ontologically primary

This shifts the ontology: the question is not "what field equation does Phi
satisfy?" but "what retarded kernel describes the memory process?"

---

## I. Remaining Obstructions

Ranked by depth:

1. **Nonlocal metric variation** (DEEPEST): The full functional derivative
   delta S_nonlocal / delta g^{ab} has not been computed in closed form.
   The result is a nonlocal stress-functional. For the exponential kernel,
   the auxiliary-field reduction gives a local T^Phi, but this reduction has
   not been proven to commute with the metric variation.

2. **Observer-flow dependence**: The retardation condition (past along u^a)
   requires a choice of observer flow, breaking manifest covariance. Promoting
   u^a to a dynamical variable would introduce new degrees of freedom.

3. **Bianchi compatibility**: Verified at the effective level (closed system
   self-consistency) but not proven from diffeomorphism invariance.

4. **Kernel uniqueness**: The exponential kernel is chosen (gives simplest
   ODE), not derived. Other causal kernels are equally valid mathematically.

5. **Quantization**: The nonlocal retarded action has unknown quantization
   properties. Standard QFT methods do not apply directly.

---

## J. Classification Levels

| Level | Definition | Status |
|-------|-----------|--------|
| Nonlocal action | Formal parent with causal kernel | **YES** |
| Metric variation | Standard local tensor variation | **NO** (nonlocal functional) |
| Stress-functional | Nonlocal metric-response functional | **YES** |
| Markov reduction | Local T^Phi for exponential kernel | **YES** |
| Bianchi compatibility | Effective-level conservation | **YES** (not proven from action) |
| Cosmo reduction | Modified Friedmann + memory ODE | **YES** |
| Collapse reduction | Force balance + memory ODE | **YES** |
| Overall | Functional-derived | **YES** |

---

## K. Explicit Nonclaims

1. Route C produces a FUNCTIONAL-DERIVED stress-functional, NOT a fully derived local T^Phi
2. The nonlocal metric variation has NOT been computed in closed form
3. The stress-functional is nonlocal in g in general (local only for exponential kernel via auxiliary field)
4. Observer-flow dependence (u^a) breaks manifest covariance
5. The Markov property is SPECIFIC to the exponential kernel — not a general feature
6. Bianchi compatibility is effective-level verified, NOT proven from an action principle
7. Route C does NOT resolve the local-conservative-first-order trilemma
8. The scalar field Phi is an effective local representation, NOT a fundamental field
9. Quantization of the nonlocal action is an OPEN problem
10. Route C and Route B are COMPLEMENTARY — neither alone is sufficient
11. The kernel K(s) = (1/tau)exp(-s/tau) is CHOSEN, not derived from deeper principles
12. The auxiliary-field reduction may not commute with the metric variation
