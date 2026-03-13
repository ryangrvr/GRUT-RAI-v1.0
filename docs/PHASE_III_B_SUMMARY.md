# Phase III-B Summary: Constrained-Law Stress Test, Phi Mapping, Ledger Tracking

**Date**: 2026-03-09
**Status**: Phase III-B complete. All 11 acceptance criteria PASS.
**Predecessor**: Phase III-A Kickoff (2026-03-08)

---

## Constrained Endpoint Law Under Test

From the Phase III-A derivation memo (preferred track: curvature-linked occupancy):

```
epsilon_Q  = alpha_vac^2 = 1/9 ≈ 0.1111
beta_Q     = 2          (Kretschner curvature scaling)
R_eq / r_s = alpha_vac  = 1/3 ≈ 0.3333
C_eq       = 3          (endpoint compactness)
```

**Question asked**: Does this constrained law survive first contact with the
same brutal anti-artifact audit that killed the fake endpoint?

**Answer**: YES — all 11 criteria pass.

---

## TASK 1: Constrained-Law Stress Test

### 1a. V_tol Insensitivity

The test that killed the old endpoint. Four V_tol values spanning 6 orders
of magnitude: [1e-6, 1e-8, 1e-10, 1e-12].

**Result**: R_f/r_s = 0.333333 at all V_tol. Spread = 1.000000.
**Verdict**: PASS (< 1.01 threshold)

### 1b. R0 Insensitivity

Five initial radii R0/r_s = [3, 5, 10, 30, 100].

**Result**: R_f/r_s = 0.333333 at all R0. Spread = 1.000000.
**Verdict**: PASS (< 1.01 threshold)

### 1c. Force Balance & Operator Share

At the endpoint:
- Force balance residual = 0.000000 (|a_net|/a_grav, should → 0)
- a_outward/a_grav = 1.000000 (operator does the work, not L_stiff)
- Phi (barrier dominance) = 1.000000
- Memory tracking ratio = 1.000000 (memory saturated)
- Endpoint motion class = sign_definite_infall

**Verdict**: PASS (FBR < 0.01, operator share > 0.5)

### 1d. Perturbation Stability

Two trajectories starting near predicted R_eq:
- Outside (1.1 × R_eq, at rest): converges to R_f/r_s ≈ R_eq
- Inside (0.9 × R_eq, small inward kick): converges to R_f/r_s ≈ R_eq
- Stability indicator: POSITIVE (d(a_net)/dR > 0 = restoring)

**Verdict**: PASS (both convergence errors < 5%)

### 1e. Artifact Rejection

- R_f/r_s (actual) = 0.333333
- R_f/r_s (artifact formula) ≠ 0.333333
- Deviation from artifact = 52.1%

**Verdict**: PASS (> 10% deviation from old artifact law)

### 1f. H_cap Independence

Three H_cap values spanning 2 orders of magnitude:
[H_cap_base, 10×, 100×].

**Result**: R_f/r_s = 0.333333 at all H_cap. Spread = 1.000002.
**Verdict**: PASS (< 1.01 threshold)

### 1g. No Regression (epsilon_Q=0)

epsilon_Q = 0 produces barrier_dominance = 0.0 (operator completely off).

**Verdict**: PASS

### 1h. No Bounce Violation

Endpoint motion class = sign_definite_infall (NOT bounce_violation).

**Verdict**: PASS

### 1i. Analytical Prediction Match

- R_f/r_s (numerical) = 0.333333
- R_eq/r_s (predicted) = 1/3 = 0.333333
- Match error = 0.00%
- Compactness = 3.0000

**Verdict**: PASS (< 1% error)

---

## TASK 2: Phi Phase-Transition Mapping

The barrier dominance ratio Phi = a_outward / a_inward was tracked along
the full collapse trajectory (record_every=1).

### Phi vs R/r_s Progression

| R/r_s | Phi | C | Regime |
|-------|-----|---|--------|
| 100 | ~0 | 0.01 | Quantum Fluid |
| 10 | ~0 | 0.1 | Quantum Fluid |
| 5 | ~0 | 0.2 | Quantum Fluid |
| 1.0 | ~0.01 | 1.0 | Onset |
| 0.5 | ~0.4 | 2.0 | Transition |
| 0.47 | ~0.5 | 2.12 | Crystallization Threshold |
| 0.35 | ~0.9 | 2.86 | Near-Equilibrium |
| 0.3333 | 1.0 | 3.0 | Barrier-Dominated Core |

### Key Findings

1. **Crystallization threshold (Phi = 0.5)** occurs at R/r_s ≈ 0.4715,
   compactness C ≈ 2.12 — this is POST-HORIZON.

2. **Transition width** (Phi = 0.1 to Phi = 0.9): width ≈ 0.703 r_s.
   Classification: SMOOTH transition.

3. **The entire Quantum Fluid → Core transition is post-horizon**.
   At R/r_s = 1 (horizon crossing), Phi is still near zero. The barrier
   only becomes significant deep inside the horizon.

4. **Phi reaches exactly 1.0 at R_eq** — confirming the equilibrium is
   a true force balance, not an asymptotic approach.

### Phase Vocabulary (status after audit)

| Term | Criterion | Audit Result |
|------|-----------|-------------|
| Quantum Fluid | Phi < 0.01 | Observed for R/r_s > ~1 |
| Crystallization Threshold | Phi ~ 0.5 | At R/r_s ≈ 0.47, C ≈ 2.12 |
| Barrier-Dominated Core | Phi > 0.99 | At R/r_s ≈ 1/3, C = 3 |

---

## TASK 3: Information Ledger Trajectory Tracking

The proxy-based information ledger was tracked along the collapse trajectory
using sample points from R/r_s = 10 down to R/r_s = 1/3.

### Endpoint Ledger

| Quantity | Value | Status |
|----------|-------|--------|
| I_fields | ~2.95e+75 | Classical BH area proxy |
| I_metric_memory | ~2.95e+75 | Placeholder scaling |
| I_total | ~5.90e+75 | Hypothesized additive |
| archive_access | FROZEN | Post-horizon (C = 3) |
| conservation_status | UNTESTED | No dynamic check |

### Late-Time Behavior

- I_total ratio (last 3 samples): 1.000063
- I_total stabilizes near endpoint: YES
- At endpoint: I_fields ≈ I_metric_memory (both ≈ 2.95e+75)

### What This Shows

The ledger exhibits structured saturation near the barrier-dominated
endpoint. I_total does not diverge, collapse, or oscillate wildly near
Phi → 1. This is interesting behavior that warrants further investigation.

### What This Does NOT Show

- Conservation of information is NOT proven
- The proxy definitions are NOT quantum information measures
- The additivity I_total = I_fields + I_metric_memory is HYPOTHESIZED
- The check_conservation() function returns PLACEHOLDER always
- This does NOT solve the black hole information paradox

---

## Acceptance Summary (11 Criteria)

| # | Criterion | Result | Detail |
|---|-----------|--------|--------|
| 1 | V_tol insensitive | PASS | spread = 1.000000 |
| 2 | R0 insensitive | PASS | spread = 1.000000 |
| 3 | Force balanced | PASS | FBR = 0.000000 |
| 4 | Operator-driven | PASS | share = 1.0000 |
| 5 | Not artifact | PASS | deviation = 52.1% |
| 6 | H_cap independent | PASS | spread = 1.000002 |
| 7 | No regression | PASS | barrier_dom = 0.0 when off |
| 8 | No bounce violation | PASS | sign_definite_infall |
| 9 | Analytical match | PASS | error = 0.00% |
| 10 | Stability converge | PASS | both perturbations converge |
| 11 | Stability positive | PASS | d(a_net)/dR > 0 |

**OVERALL**: ALL 11 CRITERIA PASS

---

## Status Recommendation

**Preferred constrained law / candidate-canon**

The constrained law epsilon_Q = alpha_vac^2, beta_Q = 2 survives the full
anti-artifact acceptance suite. It produces R_f/r_s = alpha_vac = 1/3
exactly, with zero force-balance residual, perfect V_tol/R0/H_cap
independence, and a stable attractor equilibrium.

This is a **preferred constrained law** — stronger than an unfixed
parameter but NOT a fully derived Tier A result.

---

## Explicit Nonclaims

1. **epsilon_Q and beta_Q are CONSTRAINED, not fully DERIVED**.
   The curvature-linked occupancy track is the strongest candidate but
   requires a micro-derivation (statistical mechanics of vacuum mode
   occupancy under gravitational loading).

2. **The information ledger is PROXY-based, not operational**.
   The proxy I_fields = pi R^2 / l_P^2 is a classical area law. The proxy
   I_metric_memory is a placeholder scaling. No conservation law has been
   computed or verified step-by-step.

3. **"Whole Hole" remains an ACTIVE RESEARCH TARGET**.
   The term is defined as Barrier-Dominated Compact Core + post-horizon
   (C > 1), but this is a candidate definition, not a proven geometric
   object class.

4. **Exterior observables are NOT started**.
   Ringdown, shadow, and accretion packets are deferred to Phase III-C.

5. **All derivation is in Newtonian gauge**.
   A fully relativistic treatment (TOV or equivalent) has not been attempted.

---

## Exact Missing Closures for Promotion

To promote from CONSTRAINED to DERIVED:

1. **Micro-derivation**: Why epsilon_Q = alpha_vac^2 specifically?
   (Not just dimensional coincidence — need vacuum mode counting argument)

2. **Curvature-to-force mapping**: Derive a_Q ∝ a_grav × C^2 from
   vacuum stiffness gradient, not just dimensional matching.

3. **Covariant extension**: Verify Newtonian-gauge power law (r_s/R)^2
   survives in Tolman-Oppenheimer-Volkoff or equivalent.

4. **Decoherence connection**: Does t_grut share the same alpha_vac
   dependence for the same structural reason?

---

## Files Modified/Created in Phase III-B

| File | Change |
|------|--------|
| docs/PHASE_III_B_SUMMARY.md | **NEW** — This summary |
| benchmark_phase3b_audit.py | **NEW** — Full audit script (3 tasks, 11 criteria) |

No source code files were modified in Phase III-B. The audit exercises
existing code (grut/collapse.py, grut/information.py) with the constrained
parameter values.

---

## Next Steps

### Immediate (within Phase III)
1. **Canon update**: Promote epsilon_Q = alpha_vac^2 from UNFIXED to
   CONSTRAINED in grut_canon_v0.3.json (pending user approval)
2. **Benchmark registration**: Add constrained-law audit to CI/CD suite
3. **Phi atlas**: Generate publication-quality Phi(R/r_s) figure

### Phase III-C (exterior observables, deferred)
1. Exterior matching at the phase boundary
2. Ringdown / quasinormal mode analysis
3. Shadow computation
4. Accretion near-horizon emission

### Longer-term
1. Micro-derivation of alpha_vac^2 coupling
2. Covariant extension to TOV
3. Dynamic information conservation check (step-by-step ledger tracking)
