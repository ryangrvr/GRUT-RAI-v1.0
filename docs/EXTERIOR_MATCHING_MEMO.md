# WP1 Exterior Matching Memo

**Date**: 2026-03-09
**Phase**: III-C WP1 (Gateway)
**Status**: ANALYSIS COMPLETE — exterior status: UNDERDETERMINED pending
covariant treatment, with Schwarzschild-like as the leading candidate.

---

## A. Problem Statement

### What Is Being Matched

The GRUT radial collapse solver produces a candidate interior endpoint:
a Barrier-Dominated Compact Core (BDCC) at R_eq = (1/3) r_s, compactness
C_eq = 3, with force balance Φ = 1 (a_outward = a_inward, a_net = 0).

The question is: **what exterior geometry follows from this interior
structure?**

Specifically:
1. Is the exterior spacetime Schwarzschild (standard GR black hole)?
2. Is it a modified spacetime (GRUT-specific deviations)?
3. Is the question underdetermined by the current Newtonian-gauge solver?

### Why This Is the Gateway

Every exterior falsifier — ringdown echoes, shadow deviations, accretion
signatures — depends on the exterior metric. If the exterior is exactly
Schwarzschild, then:
- Shadow: identical to GR (no deviation)
- Accretion: identical to GR at large distances
- Ringdown: standard QNMs from the light ring, BUT interior echoes
  remain possible if the BDCC reflects perturbations

If the exterior is modified, all three channels open.

**Until this question is answered, WP2 and WP3 cannot produce reliable
predictions.**

---

## B. Known Interior Inputs

### Solver-Backed Results (Phase III-B)

| Quantity | Value | Status |
|----------|-------|--------|
| R_eq / r_s | 1/3 = 0.333333 | CANDIDATE (constrained law) |
| C_eq = r_s / R_eq | 3 | CANDIDATE |
| Φ at endpoint | 1.0 (exact force balance) | LOCKED diagnostic |
| Force balance residual | 0.0 | benchmark result |
| Stability | positive restoring (d(a_net)/dR > 0) | benchmark result |
| Endpoint motion | sign_definite_infall | benchmark result |
| Transition width | ~0.7 r_s (smooth) | benchmark result |
| Crystallization (Φ=0.5) | R/r_s ≈ 0.47, C ≈ 2.12 | benchmark, post-horizon |

### Solver Structure

The current solver is a Newtonian-gauge shell model:
- State vector: [R, V, M_drive]
- R = shell radius, V = dR/dt, M_drive = memory state
- Equations of motion:
  - dR/dt = V
  - dV/dt = -a_net = -(a_inward - a_outward)
  - dM_drive/dt = (GM/R² - M_drive) / τ_eff

The solver does NOT compute a metric tensor. It does not have an
exterior region. It integrates a single shell with no vacuum zone.

### What the Solver Cannot Tell Us

1. The metric at R > R_eq (no exterior computation exists)
2. Whether the memory field M_drive has any exterior extension
3. Whether the effective pressure from OP_QPRESS_001 has gravitational
   self-energy that modifies the exterior metric
4. What boundary conditions hold at R_eq for perturbation propagation

---

## C. Exterior Candidates

### Candidate 1: Schwarzschild-Like Exterior

**Hypothesis**: The exterior is exactly Schwarzschild for R > r_s.

**Physical basis**: In GR, Birkhoff's theorem guarantees that any
spherically symmetric vacuum region has the Schwarzschild metric. The
argument requires:
1. Spherical symmetry (present in current solver)
2. Vacuum exterior (the shell contains all matter)
3. The gravitational theory admits Birkhoff's theorem

For the GRUT collapse:
- The total gravitating mass M is fixed (no mass-energy is radiated
  in the dust model)
- The entire matter distribution is contained within R_eq < r_s
- Any observer at R >> r_s sees only the total enclosed mass

**Strength**: This is the default expectation from GR + spherical
symmetry + vacuum exterior. It requires the least new physics.

**Weakness**: GRUT modifies the gravitational dynamics through memory
coupling. If this constitutes a modification to the gravitational sector
(not just the matter sector), Birkhoff may not apply in the modified
theory.

### Candidate 2: Modified Memory Exterior

**Hypothesis**: The GRUT memory coupling creates a residual exterior
modification — a "memory halo" or effective scalar field extending
beyond the matter distribution.

**Physical basis**: In the GRUT framework, the memory kernel couples
the gravitational field to its own history:

  τ_eff dM_drive/dt + M_drive = GM/R²

If we interpret M_drive as a degree of freedom of the gravitational
theory (not just a property of matter), it could in principle extend
outside the shell. In this interpretation:
- The exterior has a non-trivial M_drive field
- This field carries energy-momentum
- Birkhoff does not apply (the exterior is not vacuum in the modified
  theory)

**Strength**: Would produce potentially observable exterior deviations.

**Weakness**: The current solver treats M_drive as a shell-local variable.
There is no spatial propagation equation for M_drive. The solver does not
extend M_drive outside the matter distribution. To make this concrete,
one would need:
- A covariant field equation for the memory sector
- A stress-energy tensor for the memory field
- An exterior solution of the modified field equations

None of these exist in the current framework.

### Candidate 3: Underdetermined

**Hypothesis**: The current Newtonian-gauge solver is structurally
insufficient to determine the exterior metric. The answer requires a
covariant formulation that has not been constructed.

**Physical basis**: The solver integrates shell dynamics using Newtonian
gravity with GRUT corrections. It does not construct a spacetime metric.
The mapping from Newtonian-gauge dynamics to a full relativistic spacetime
is ambiguous:

- In GR, the Oppenheimer-Snyder solution gives an exact interior-exterior
  matching (closed FRW interior, Schwarzschild exterior). But the GRUT
  modification changes the interior dynamics, so the matching conditions
  may also change.

- The quantum pressure barrier a_Q is defined as a force-law correction.
  Its interpretation as a stress-energy contribution (which modifies the
  metric) versus a fundamental force modification (which changes the field
  equations) is not determined by the Newtonian-gauge solver.

**Strength**: Honest. Does not overclaim.

**Weakness**: Does not allow progress to WP2/WP3 until resolved.

---

## D. Matching Conditions

### What Must Be Matched

For any interior-exterior matching, we need continuity conditions at a
matching surface Σ. In GR, the Israel junction conditions require:

1. **Induced metric continuity**: The 3-metric on Σ must agree when
   approached from either side.

2. **Extrinsic curvature**: Either continuous (no surface layer) or
   discontinuous by an amount proportional to the surface stress-energy.

### Matching Surface Candidates

| Surface | Location | Physical meaning |
|---------|----------|-----------------|
| Horizon | R = r_s (C = 1) | Standard matching point in GR |
| BDCC surface | R = R_eq = (1/3) r_s | Core boundary |
| Transition zone | 0.34 < R/r_s < 0.47 | Φ transition region |

In the Oppenheimer-Snyder analogy, the matching surface is the shell
itself (which is the matter boundary). In the GRUT solver, the shell is
the only matter surface — so the natural matching point is R = R_eq at
the endpoint.

### What Is Continuous

Regardless of the exterior model:
- **Mass function**: The total enclosed mass M is continuous across any
  spherical surface. The shell contains mass M at R_eq, and any exterior
  observer measures mass M.
- **Angular part of metric**: By spherical symmetry, the angular metric
  g_θθ = R² is continuous.

### What May Jump

- **Extrinsic curvature**: If the core has non-zero surface pressure
  (from the quantum pressure barrier), the extrinsic curvature is
  discontinuous. This is a standard thin-shell result in GR.
- **Radial metric component**: If the memory field contributes to the
  effective stress-energy, the radial metric derivative may be modified.

### What Is Currently Undefined

- **M_drive at the matching surface**: The solver computes M_drive for
  the shell but does not define what happens to M_drive outside.
- **Stress-energy of OP_QPRESS_001**: The quantum pressure barrier is
  defined as a force-law correction. Its stress-energy tensor T_μν has
  not been constructed.
- **Whether the matching is timelike or null**: At the endpoint (C = 3),
  the matching surface is deep inside the horizon. A timelike shell at
  this location must be matched across a surface where radial and time
  coordinates have already exchanged roles (in Schwarzschild coordinates).

---

## E. The Birkhoff Question

### What Must Be True for Schwarzschild Exterior to Survive

Birkhoff's theorem requires:
1. **The gravitational theory has Birkhoff's property**: The vacuum field
   equations admit only the Schwarzschild solution for spherically
   symmetric spacetimes. This is true in GR but may not hold in modified
   gravity theories.
2. **The exterior is vacuum**: No matter, energy, or additional fields
   in the region R > r_s (or R > R_eq).
3. **Spherical symmetry**: The configuration is exactly spherically
   symmetric. (Present by construction in the current solver.)

### What Could Break Birkhoff in GRUT

1. **Memory as an exterior field**: If M_drive extends outside the
   matter distribution, the exterior is not vacuum in the GRUT theory.
   This would break assumption (2).

2. **Modified field equations**: If the GRUT memory kernel modifies the
   gravitational field equations themselves (not just the matter dynamics),
   the vacuum field equations change and may not have Birkhoff's property.
   This would break assumption (1).

3. **Effective stress-energy of OP_QPRESS_001**: If the quantum pressure
   barrier has gravitational self-energy, it contributes to the effective
   stress-energy outside the shell. This would break assumption (2).

### Can the Current Solver Decide This?

**Partially.** The current solver constrains the problem as follows:

- **M_drive is shell-local in the solver**: The code computes M_drive
  only at the shell radius. There is no spatial propagation equation.
  This is consistent with M_drive being a matter-sector variable (not
  an exterior field), but the absence of a spatial equation does not
  prove it is matter-local — the Newtonian gauge simply does not address
  the question.

- **Total mass is conserved**: The solver uses fixed mass M throughout.
  No mass-energy is radiated, absorbed, or deposited in the exterior
  region. This strongly supports an exterior that appears Schwarzschild
  to distant observers.

- **OP_QPRESS_001 is a force-law correction**: The quantum pressure
  barrier is added as a_Q = (GM/R²) × ε_Q × (r_s/R)^β_Q. This has
  the form of a modified gravitational force, not an additional matter
  source. Whether this maps to a stress-energy correction or a
  fundamental force modification is not determined by the Newtonian-gauge
  formulation.

### Best Current Assessment

**Birkhoff status: PRESERVED_CANDIDATE (conditional)**

The leading assessment is that the exterior is Schwarzschild-like, for
these reasons:

1. Total enclosed mass is fixed and spherically distributed.
2. M_drive is shell-local in the solver — no known mechanism propagates
   it to the exterior.
3. The Oppenheimer-Snyder analogy starts from a Schwarzschild exterior
   and the GRUT modification only changes the interior shell dynamics.
4. At R >> r_s, a_Q / a_grav = ε_Q × (r_s/R)^β_Q → 0, so the quantum
   pressure barrier is negligible far from the shell. Any exterior
   modification would be exponentially suppressed at large radius.

**Conditional on**: M_drive being a matter-sector variable (not a
spacetime field), and OP_QPRESS_001 not having exterior gravitational
self-energy.

**This assessment is NOT a proof.** A covariant formulation is required
to make it rigorous.

---

## F. Exact Missing Closures

### Required to Complete WP1

| # | Closure | Why Needed | Status |
|---|---------|------------|--------|
| 1 | Covariant interpretation of M_drive | Is it matter-local or a spacetime field? | UNDEFINED |
| 2 | Stress-energy tensor for OP_QPRESS_001 | Is a_Q a force modification or a matter source? | UNDEFINED |
| 3 | Israel junction conditions at R_eq | Match interior equilibrium to exterior metric | NOT COMPUTED |
| 4 | Birkhoff proof or counterexample in GRUT | Does GRUT preserve or violate Birkhoff? | NOT PROVEN |
| 5 | Effective enclosed mass at matching surface | Does quantum pressure contribute gravitating mass? | NOT COMPUTED |

### Required Before WP2 (Ringdown/Echo)

| # | Closure | Why Needed |
|---|---------|------------|
| 6 | Interior effective potential V_eff(r) | Determines whether perturbations reflect off core |
| 7 | Boundary condition at R_eq for wave propagation | Reflecting, absorbing, or partially reflecting? |
| 8 | Tortoise coordinate through the transition zone | Maps physical radius to wave-equation coordinate |

### Required Before WP3 (Shadow)

| # | Closure | Why Needed |
|---|---------|------------|
| 9 | Exterior metric at photon sphere (R = 3/2 r_s) | Shadow depends on this |
| 10 | Whether null geodesics are modified | Only if exterior ≠ Schwarzschild |

---

## G. Recommendation

### Best Next Formalism

**Recommended: Effective metric approach with Schwarzschild-like exterior
as the zeroth-order solution, parameterized by possible deviations.**

This is the most productive path because:

1. It does not require solving the full covariant GRUT field equations
   (which are not formulated).
2. It acknowledges the leading Birkhoff-preserving candidate.
3. It parameterizes possible deviations so that WP2 (ringdown) can
   compute echo amplitudes as a function of deviation strength.
4. It can be upgraded to a full covariant treatment later without
   invalidating the parameterized results.

### Concrete Implementation Plan

**Step 1**: Define an effective exterior metric:

```
ds² = -f(r) dt² + f(r)⁻¹ dr² + r² dΩ²
f(r) = 1 - r_s/r + δf(r)
```

where δf(r) parameterizes GRUT deviations. Under the Schwarzschild-like
candidate, δf = 0. Under a modified candidate, δf is a calculable
function of the memory coupling.

**Step 2**: At the matching surface R_eq, enforce:
- f(R_eq) consistent with the interior force balance
- f'(R_eq) determined by the junction conditions

**Step 3**: Compute the effective enclosed mass from the interior
force balance. At R_eq with a_net = 0:
- M_eff(R_eq) = R_eq c² / (2G) × [some function of force balance]
- Compare M_eff to the input mass M

**Step 4**: Determine whether M_eff = M (Schwarzschild) or
M_eff ≠ M (modified exterior).

### What This Approach Cannot Do

- It cannot derive δf from first principles (no covariant GRUT equations)
- It cannot prove Birkhoff (only parameterize deviations)
- It cannot determine the interior wave-propagation potential without
  additional assumptions about the interior metric

### Status After Implementation

The module should be able to say:
- "Under the Schwarzschild-like candidate: exterior = Schwarzschild,
  δf = 0, Birkhoff preserved."
- "Under the modified candidate: exterior = Schwarzschild + δf(r),
  where δf is parameterized but not derived."
- "The current solver constrains the exterior to be approximately
  Schwarzschild at large R (a_Q/a_grav → 0), but cannot determine
  δf near the horizon without a covariant treatment."

---

## Summary

| Question | Answer | Confidence |
|----------|--------|------------|
| Is exterior Schwarzschild? | Leading candidate, yes | MODERATE — conditional on M_drive being matter-local |
| Does GRUT break Birkhoff? | Not in the current solver | LOW — solver does not address this directly |
| Can we proceed to WP2? | CONDITIONAL GO — with Schwarzschild exterior as zeroth order and parameterized deviations | |
| Can we proceed to WP3? | CONDITIONAL GO — but shadow is trivially Schwarzschild if exterior is unmodified | |
| What is the minimum closure? | Covariant interpretation of M_drive | HIGH PRIORITY |
