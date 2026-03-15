# Phase IV — Route B: Consistent Truncation and Attractor Analysis

## Status

**PHASE IV — ROUTE B TRUNCATION ANALYSIS**

Classification: **CONSISTENT TRUNCATION — NOT ATTRACTOR**

The physical limit (Phi_- = 0) of the Galley doubled-field system is an exact
consistent truncation: if imposed, it is maintained by the dynamics. However, it
is NOT a dynamical attractor: perturbations in Phi_- grow exponentially at rate
1/tau. The physical limit is maintained by the CTP (closed-time-path) boundary
condition, not by dynamical attraction. This is a fundamental feature of the
Galley formalism, not a deficiency.

---

## A. Why Consistent Truncation Is the Next Decisive Question

Phase IV Route B derived an explicit T^Phi_{mu nu} in the physical limit
(Phi_1 = Phi_2 = Phi, g^(1) = g^(2) = g). That derivation was classified as
"physical-limit derived" because the physical limit was imposed as a constraint,
not shown to be dynamically selected.

The next decisive question: Is the physical limit merely a projection, or is it
dynamically selected? If Phi_- = 0 is an attractor, then solutions starting
near the physical limit would naturally flow toward it, upgrading Route B from
"physical-limit derived" toward "derived."

Three possible outcomes:
1. ATTRACTOR: Phi_- = 0 is dynamically stable => upgrade to "derived"
2. CONSISTENT TRUNCATION: Phi_- = 0 is a solution but not stable => no upgrade
3. INCONSISTENT: Phi_- = 0 is not even a solution => Route B broken

The result is (2): consistent truncation, not attractor.

---

## B. Doubled-Field Variables and Physical-Limit Submanifold

The Galley formalism doubles all degrees of freedom. We define:

    Phi_+ = (Phi_1 + Phi_2) / 2    (physical mode)
    Phi_- = Phi_1 - Phi_2            (difference / ghost mode)

Inverse:

    Phi_1 = Phi_+ + Phi_-/2
    Phi_2 = Phi_+ - Phi_-/2

The physical limit is the submanifold Phi_- = 0 (and analogously g_- = 0 for
the metric sector). On this submanifold, Phi_1 = Phi_2 = Phi_+ and the doubled
system reduces to a single-field theory.

The Jacobian of the transform has determinant -1 (nonsingular), so the
decomposition is well-defined everywhere.

---

## C. Scalar-Sector Truncation Analysis

### C.1. Galley EOM Derivation

The Galley CTP action for the first-order GRUT relaxation law is:

    S = integral dt Phi_- [tau dPhi_+/dt + Phi_+ - X]

Euler-Lagrange equations:

    delta S / delta Phi_- = 0:
        tau dPhi_+/dt + Phi_+ - X = 0
        => dPhi_+/dt = (X - Phi_+) / tau    [GRUT relaxation law]

    delta S / delta Phi_+ = 0:
        Phi_- - tau dPhi_-/dt = 0
        => dPhi_-/dt = Phi_- / tau            [EXPONENTIAL GROWTH]

### C.2. Cross-Coupled Individual Variables

In the original variables (Phi_1, Phi_2), the EOM are CROSS-COUPLED:

    dPhi_1/dt = (X - Phi_2) / tau
    dPhi_2/dt = (X - Phi_1) / tau

This is DIFFERENT from independent evolution (dPhi_i/dt = (X - Phi_i)/tau).
In independent evolution, Phi_- decays. In the Galley cross-coupled system,
Phi_- grows. The cross-coupling is what produces the ghost mode amplification.

### C.3. Consistent Truncation

Phi_- = 0 IS an exact consistent truncation:

- The Phi_- EOM is dPhi_-/dt = Phi_-/tau (linear homogeneous)
- If Phi_-(0) = 0, then Phi_-(t) = 0 for all t
- Verified numerically: max|Phi_-| < 1e-14 over 5 relaxation times

This is exact by construction: a linear homogeneous equation always admits the
trivial solution.

---

## D. Linearized Stability of Phi_-

### D.1. Simple Galley System (First-Order)

The Phi_- equation: dPhi_-/dt = Phi_-/tau

General solution: Phi_-(t) = Phi_-(0) exp(t/tau)

Growth rate: 1/tau

This is a PURELY GROWING mode. Any nonzero perturbation is amplified
exponentially. Phi_- = 0 is an UNSTABLE fixed point.

### D.2. Full KG+Galley System (Second-Order)

With kinetic terms (-(1/2)(dPhi)^2) in each copy, the Phi_- equation becomes:

    d^2 Phi_-/dt^2 - (1/tau) dPhi_-/dt - (1/tau^2) Phi_- = 0

Characteristic equation (with mu = tau * lambda):

    mu^2 - mu - 1 = 0

Solutions: mu = (1 +/- sqrt(5)) / 2

Growing mode:   lambda_+ = phi/tau   where phi = (1+sqrt(5))/2 ~ 1.618 (golden ratio)
Decaying mode:  lambda_- = -1/(phi*tau) ~ -0.618/tau

Properties:
- lambda_+ * lambda_- = -1/tau^2  (from Vieta's formula)
- lambda_+ + lambda_- = 1/tau     (from Vieta's formula)
- The growing rate is FASTER than in the simple system (phi/tau > 1/tau)
- The golden ratio appearance is structural (fibonacci relation in the characteristic equation)

### D.3. Numerical Verification

Both growth rates are verified numerically:
- Simple: measured rate matches 1/tau to < 1% over 3 relaxation times
- Full KG+Galley: measured late-time rate matches phi/tau to < 2%
- Results are ROBUST across cosmological and collapse parameter regimes

### D.4. Galley vs Independent Evolution

The contrast is decisive:
- Galley (cross-coupled): Phi_- grows by factor exp(3) ~ 20 in 3 tau
- Independent (same equation): Phi_- decays by factor exp(-3) ~ 0.05 in 3 tau

The Galley cross-coupling (dPhi_1/dt = (X - Phi_2)/tau) is what produces the
ghost mode growth. This is not present in independent evolution where each copy
relaxes toward X on its own.

---

## E. Gravity-Coupled / Metric-Difference Discussion

### E.1. Metric Decomposition

The doubled-metric sector decomposes analogously:

    g_+ = (g_1 + g_2) / 2    (physical metric)
    g_- = g_1 - g_2            (difference metric)

The gravitational action: S_grav = (1/(16piG)) int [sqrt(-g_1)R_1 - sqrt(-g_2)R_2]

### E.2. Wrong-Sign Kinetic Energy

The metric-difference sector has WRONG-SIGN kinetic energy:
- g_2 appears with wrong-sign Einstein-Hilbert action (-R_2)
- Linearized around the physical limit: g_- has a "gravitational ghost"
- This is structurally analogous to the scalar ghost (Phi_2 wrong-sign kinetic)

### E.3. Scalar-Metric Coupling

The growing scalar difference Phi_- sources the metric difference through:

    G_{ab}^(1) = (8piG/c^4)[T_{ab}^(1) + T^Phi_1_{ab}]
    G_{ab}^(2) = (8piG/c^4)[T_{ab}^(2) + T^Phi_2_{ab}]

Since T^Phi_1 != T^Phi_2 when Phi_- != 0, the growing Phi_- drives g_- growth.

### E.4. Metric-Sector Status

- g_- = 0 IS a consistent truncation (by symmetry of doubled Einstein equations)
- g_- = 0 is EXPECTED to be unstable (wrong-sign kinetic + growing scalar source)
- Full linearized analysis of the doubled Einstein equations has NOT been done
- This remains the DEEPEST Route B obstruction

---

## F. Attractor Criteria

### F.1. What Would Count as an Attractor

For Phi_- = 0 to be an attractor, ALL eigenvalues of the linearized Phi_- dynamics
would need to have negative real parts (i.e., all perturbation modes decay).

Result: The growing eigenvalue (1/tau or phi/tau) has POSITIVE real part.
Therefore Phi_- = 0 is NOT an attractor.

### F.2. CTP Boundary Condition Alternative

The Galley formalism does NOT rely on attractiveness. It uses the CTP boundary
condition: Phi_1(T_final) = Phi_2(T_final), i.e., Phi_-(T_final) = 0 at the
FINAL time. This is a boundary-value formulation, not an initial-value one.

The variational principle operates on the doubled system with this boundary
condition, which selects the physical sector. The growing ghost mode is the
mathematical price paid for encoding dissipation in a variational framework.

---

## G. Classification Levels

| Level | Definition | Status |
|-------|-----------|--------|
| Exact consistent truncation | Phi_- = 0 is preserved if imposed | **YES** |
| Linearized attractor | Small Phi_- perturbations decay | **NO** (growing mode) |
| Conditional attractor | Attractor under some physical condition | **NO** |
| CTP-consistent | Physical limit maintained by CTP BCs | **YES** |
| Unresolved | Cannot determine | No (resolved definitively) |

The scalar-sector question is DEFINITIVELY RESOLVED:
- Exact consistent truncation: YES
- Dynamical attractor: NO
- CTP-consistent: YES

---

## H. Implications for Route B Standing

### H.1. No Upgrade

Route B does NOT upgrade from "physical-limit derived" to "derived." The
physical limit requires enforcement (CTP boundary condition), not dynamics.

### H.2. Decisive Clarification

The analysis IS a decisive clarification of the Route B obstruction. Before this
analysis, the nature of the physical-limit constraint was unclear:
- Was it consistent? (Now known: YES)
- Was it attractive? (Now known: NO)
- What enforces it? (Now known: CTP boundary condition)

### H.3. Revised Route B Status

Before: "physical-limit derived"
After: "physical-limit derived (truncation consistent, not attractor)"

This is more precise but not more powerful. The derivation status remains the same.

---

## I. Comparison to Route C

The truncation analysis SHARPENS the Route B vs Route C comparison:

| Property | Route B (Galley) | Route C (Nonlocal Retarded) |
|----------|:----------------:|:--------------------------:|
| T^Phi derivation | Action-derived (physical-limit) | No standard metric variation |
| EOM derivation | Physical-limit projection needed | Exact (mathematical identity) |
| Ghost problem | Growing Phi_- mode | None (single field) |
| Stability | Unstable (not attractor) | Not applicable |
| Enforcement | CTP boundary condition | No enforcement needed |
| Conservation | Physical-limit derived (Bianchi) | Structural (retarded kernel) |

The truncation result STRENGTHENS Route C's relative position: Route C avoids
the ghost/attractor problem entirely by working with a single field. Route B
produces T^Phi but requires CTP boundary enforcement. Neither is strictly
better — they remain complementary with different strengths.

---

## J. Exact Remaining Obstruction

Ranked by depth:

1. **Attractor failure** (RESOLVED — scalar sector): The ghost mode grows at
   rate 1/tau. The physical limit requires CTP boundary enforcement. This is
   now precisely understood but NOT resolvable within the standard Galley framework.

2. **Metric-difference instability** (EXPECTED, NOT PROVEN): The metric-difference
   mode g_- has wrong-sign kinetic energy and is sourced by growing Phi_-. Full
   linearized analysis not performed.

3. **CTP sufficiency question**: Whether the CTP boundary formulation provides
   a mathematically rigorous physical derivation (as opposed to just a computational
   device) is a question in mathematical physics.

4. **Observer-flow dependence**: S_diss requires u^a (not manifestly covariant).

5. **Potential ambiguity**: V(Phi) = Phi^2/(2 tau^2) is chosen, not unique.

---

## K. Explicit Nonclaims

1. Phi_- = 0 is a consistent truncation but NOT a dynamical attractor
2. The growing mode dPhi_-/dt = Phi_-/tau is a FEATURE of the Galley formalism
3. Route B does NOT upgrade from "physical-limit derived" to "derived"
4. The CTP boundary condition maintains the physical limit, but its physical
   interpretation as a "derivation" is a matter of definition
5. The metric-difference sector instability is EXPECTED but NOT PROVEN
6. The Galley cross-coupling (dPhi_1/dt = (X-Phi_2)/tau) is fundamentally
   different from independent relaxation
7. No modification of the doubled action has been found that makes Phi_- attractive
8. The golden ratio growth rate (phi/tau in the full system) is structural
9. Route C avoids the ghost/attractor problem entirely
10. Quantization of the Galley CTP action with the ghost sector remains open
11. The attractor failure is ROBUST across cosmological and collapse parameter regimes
12. This analysis CLARIFIES but does not RESOLVE the Route B obstruction
