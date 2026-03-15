# GRUT Phase IV: Fundamental Closure of Phase III — Master Plan

## Phase Purpose

Phase III established the effective covariant framework for GRUT:
constitutive-effective T^Phi_{mu nu}, auxiliary scalar memory field (scalarized
first pass), PDE closure with Q ~ 6-7.5, structural identity omega_0 * tau = 1,
effective junction conditions, and 25 explicit nonclaims.

Phase IV pushes the memory sector beyond constitutive-effective closure toward
a deeper foundational form. This is NOT a speculative expansion phase. It is the
foundational derivation phase that follows Phase I-III.

**Immediate priority:**
1. Action principle
2. Tensorial memory field

**Explicitly excluded:**
- Consciousness / observer architecture
- Particle-sector hypotheses
- Broader force unification
- Detector pipelines

---

## Package Dependency Order

### Package 1 — Action Principle Program (FIRST)

**Why first:** The action principle determines whether the scalar memory field
is fundamental, emergent, or purely effective. This classification constrains
what tensor structures are physically meaningful. If the scalar sector has a
genuine variational obstruction (dissipation barrier), this shapes the entire
tensorial extension strategy. Without knowing the action-level status, tensorial
extension risks building on an ungrounded foundation.

### Package 2 — Tensorial Memory-Field Program (SECOND)

**Why second:** The tensor structure of the memory field determines anisotropy,
spin coupling, shear memory, and richer perturbation physics. But the correct
tensor extension depends on whether the scalar is fundamental (extend the scalar
Lagrangian) or constitutive-effective (extend the constitutive relations). Package 1
must deliver this classification before Package 2 can proceed optimally.

---

## Success Criteria

### Package 1 — Action Principle

The package succeeds if:

1. **Landscape classified:** At least 4 action/quasi-action candidate families
   evaluated (local scalar, doubled-field dissipative, nonlocal retarded,
   auxiliary-field realization).

2. **Obstruction localized:** If a standard variational principle fails,
   the obstruction is sharply identified (e.g., "the exponential kernel is
   dissipative, violating time-reversal symmetry required for Hamilton's
   principle").

3. **Best formulation identified:** One candidate designated as preferred
   with explicit status: fully action-derived, quasi-action, nonlocal-effective
   parent, or constitutive-effective with obstruction.

4. **Reduction verified:** Preferred candidate recovers both weak-field
   (cosmological) and strong-field (collapse) sectors at the effective level.

5. **No overclaiming:** If the best result is "constitutive-effective with
   sharply defined obstruction," this is stated without apology.

### Package 2 — Tensorial Memory Field

The package succeeds if:

1. **Candidate tensor structures evaluated:** At least 4 candidates
   (scalar-only, scalar+anisotropic stress, vector/flow-structured,
   rank-2 symmetric tensor).

2. **Scalar closure status determined:** Whether the scalar is a
   symmetry-reduced limit of a deeper structure, or a minimal standalone
   closure.

3. **Phase III survival assessed:** Which Phase III results survive
   unchanged vs. which are modified under tensorial extension.

4. **New sectors identified:** What becomes possible only with tensorial
   memory (anisotropic memory, propagating modes, GW memory effects).

5. **Minimal extension identified:** The smallest honest tensorial
   extension that captures the missing physics.

---

## What Counts as "Substantially Advanced"

Phase IV substantially advances the theory if:

- The action-principle landscape is honestly classified with obstructions
  sharply localized
- The tensorial memory-field landscape is honestly classified with the
  scalar-to-tensor upgrade path identified
- Uncertainty about the memory sector's foundational status is reduced
- Remaining obstructions are fewer and more precisely defined than at
  Phase III close
- No speculative sector creep has been introduced

This does NOT require:
- A complete action derivation
- A full tensorial field theory
- Resolution of alpha_mem / alpha_vac unification
- Full Kerr or Love number calculations

---

## Frontier Memo Policy

Brief frontier memos may be created if needed, clearly marked as
exploratory and not part of the resolved core:

- Consciousness / observer architecture
- Particle-sector hypotheses
- Broader sector / force unification

These are NOT part of the opening packages and receive no code
implementation, no tests, and no benchmarks.

---

## Fixed Inputs from Phase III

### LOCKED / OPERATIONAL
1. Weak-field memory sector structure
2. Modified Friedmann / memory ODE logic at effective level
3. Collapse artifact rejection (old L_stiff x V_tol endpoint)
4. Transition order parameter Phi
5. Mixed-viscoelastic interior (PDE closure, covariant confirmation)
6. Static exterior null map (Schwarzschild-like, WP1 conditional)
7. Effective cross-sector recovery structure
8. Constitutive-effective T^Phi_{mu nu} (Package A)
9. Effective junction conditions (Package B)

### CONSTRAINED / CANDIDATE
1. Endpoint law: epsilon_Q = alpha_vac^2, beta_Q = 2
2. Candidate endpoint: R_eq / r_s = 1/3
3. Echo channel: ~1.1% of QNM amplitude (PDE-informed)
4. Preferred field equations: auxiliary memory scalar field
5. Love numbers: k_2 ~ 0.01 (candidate non-null)
6. Kerr extension: bounded first-pass parametric estimates
7. Nonlinear coupling: bounded first-pass (Q robust for small perturbations)

### FUNDAMENTALLY OPEN (Phase IV targets)
1. First-principles T^Phi_{mu nu} (action-derived)
2. Action / Lagrangian-level derivation
3. Tensorial memory-sector generalization
4. Curvature dependence of tau_eff from first principles
5. alpha_mem / alpha_vac unification
6. Full junction theory from field equations
7. Full Kerr solution
8. Precise Love-number calculation
9. Nonlinear strong-amplitude dynamics

### alpha_mem / alpha_vac Rule
alpha_mem (cosmological, 0.1) and alpha_vac (collapse, 1/3) remain
**distinct symbols**. Do NOT unify. Do NOT declare fundamentally distinct.
Possible unification remains an OPEN research target.

---

## Deliverables

### Package 1
- `docs/PHASE_IV_PACKAGE_1_ACTION_PRINCIPLE.md` — theory memo
- `grut/action_principle.py` — action candidate evaluation module
- `tests/test_action_principle.py` — targeted tests
- Benchmark diagnostic (inline or separate)

### Package 2
- `docs/PHASE_IV_PACKAGE_2_TENSORIAL_MEMORY.md` — theory memo
- `grut/tensorial_memory.py` — tensorial extension module
- `tests/test_tensorial_memory.py` — targeted tests
- Benchmark diagnostic (inline or separate)

### Final Output
8-point status report covering both packages.
