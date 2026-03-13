# Phase III-A Kickoff Summary

**Date**: 2026-03-08
**Status**: Phase III-A kickoff complete. Three tasks delivered.

---

## TASK 1 RESULT: Derive or Constrain epsilon_Q and beta_Q

**Status**: CONSTRAINED (not fully derived)

### Preferred Derivation Track: Curvature-Linked Occupancy

**beta_Q = 2**: Constrained by Kretschner curvature scaling.
The invariant K = 48(GM)^2/(c^4 R^6) gives a natural (r_s/R)^2 = C^2
dependence. The barrier strength tracks curvature load on the vacuum.

**epsilon_Q = alpha_vac^2 = 1/9**: Best candidate coupling constant.
Produces R_eq/r_s = alpha_vac = 1/3 (exact clean fraction).
Endpoint compactness C_eq = 1/alpha_vac = 3 (well inside horizon).
Within 11% of current benchmark default (0.1 vs 0.1111).

**Combined law**:
```
a_Q = (GM/R^2) * alpha_vac^2 * (r_s/R)^2
R_eq / r_s = alpha_vac = 1/3
C_eq = 3
```

### Derivation Track Ranking

| Rank | Track | beta_Q | epsilon_Q | Status |
|------|-------|--------|-----------|--------|
| 1 | Curvature-linked occupancy | 2 (from K) | alpha_vac^2 = 1/9 | CONSTRAINED |
| 2 | Bandwidth saturation | motivates power law | does not fix | MOTIVATIONAL |
| 3 | Anomaly bridge | no link | no link | SPECULATIVE |

### Exact Missing Closures

1. Micro-derivation: WHY does epsilon_Q = alpha_vac^2? Need statistical
   mechanics of vacuum mode occupancy under gravitational loading.
2. Curvature-to-force mapping: derive a_Q proportional to a_grav * C^2
   from vacuum stiffness gradient, not just dimensional matching.
3. Covariant extension: verify Newtonian-gauge power law survives in TOV.
4. Decoherence connection: does t_grut share the same alpha_vac
   dependence for the same structural reason?

**Full memo**: docs/PHASE_III_A_DERIVATION_MEMO.md

---

## TASK 2 RESULT: Order Parameter for Fluid-to-Core Transition

### Primary Order Parameter: Barrier Dominance Ratio

**Definition**:
```
Phi = a_outward / a_inward
```

- Phi -> 0: Quantum Fluid regime (barrier negligible)
- Phi ~ 0.5: Crystallization Threshold (barrier substantially resists infall)
- Phi -> 1: Barrier-Dominated Compact Core (force-balanced)
- Phi = 1: Exact equilibrium

**Supporting diagnostics**:
- Compactness C = r_s / R (geometric measure, distinguishes pre/post-horizon)
- Memory tracking ratio eta = M_drive / a_grav (how fully memory has saturated)

### Phase Vocabulary Status

| Term | Criterion | Status |
|------|-----------|--------|
| Quantum Fluid | Phi < 0.01 | CANDIDATE conceptual term |
| Crystallization Threshold | Phi ~ 0.5 | ACTIVE / RESEARCH TARGET |
| Phase Boundary | Phi -> 1 minus epsilon | ACTIVE / RESEARCH TARGET |
| Barrier-Dominated Compact Core | Phi > 0.99 | CANDIDATE |
| Whole Hole | BDCC + post-horizon (C > 1) | ACTIVE / RESEARCH TARGET |

**Implementation**: Added `barrier_dominance_final` and `compactness_final`
fields to CollapseResult. Computed at endpoint from a_outward / a_inward.

---

## TASK 3 RESULT: Information Ledger Skeleton

### Ledger Objects Created

| Variable | Proxy Definition | Status |
|----------|-----------------|--------|
| I_fields | pi R^2 / l_P^2 (BH area law proxy) | CLASSICAL PROXY |
| I_metric_memory | I_fields * mem_ratio * barrier_dom | PLACEHOLDER scaling |
| I_total | I_fields + I_metric_memory | HYPOTHESIZED additive |
| archive_access_status | OPEN/FROZEN/UNKNOWN (compactness-based) | PLACEHOLDER |
| conservation_domain | UNDEFINED | NOT YET SPECIFIED |
| conservation_status | UNTESTED | NO dynamic check |

### What Is Computed Now

- I_fields is computed from shell area at endpoint (classical BH entropy proxy)
- I_metric_memory scales with memory saturation and barrier engagement
- I_total is the sum (additivity is hypothesized, not proven)
- archive_access_status is determined by compactness (C >= 1 = FROZEN)

### What Is Still Placeholder

- Conservation check returns PLACEHOLDER status always
- I_metric_memory proxy is not derived from first principles
- conservation_domain is UNDEFINED
- No step-by-step dynamic conservation tracking exists

### Whether Any Conservation Statement Is Tested

**No.** The check_conservation() function compares two ledger states
and reports whether I_total changed, but it returns status="PLACEHOLDER"
because the proxy definitions are too crude for a real test.

**Module**: grut/information.py

---

## FILES CHANGED

| File | Change |
|------|--------|
| docs/PHASE_III_A_DERIVATION_MEMO.md | **NEW** — Ranked derivation tracks |
| docs/PHASE_III_A_KICKOFF.md | **NEW** — This summary |
| grut/information.py | **NEW** — Information ledger skeleton |
| grut/collapse.py | Added barrier_dominance_final, compactness_final |
| canon/grut_canon_v0.3.json | Added derivation_tracks, barrier_dominance, information_ledger |
| tests/test_collapse.py | Added 12 Phase III-A tests |

---

## EXPLICIT NONCLAIMS

The following remain OPEN after this kickoff:

1. **First-principles derivation of endpoint operator**: epsilon_Q and
   beta_Q are CONSTRAINED, not DERIVED. The curvature-linked occupancy
   track is the strongest candidate but requires micro-derivation.

2. **Final Whole Hole ontology**: "Whole Hole" is an ACTIVE RESEARCH
   TARGET. It is defined as Barrier-Dominated Compact Core + post-horizon,
   but this is a CANDIDATE definition, not a proven geometric object class.

3. **Archive/unitarity proof**: The information ledger is a SKELETON with
   PROXY definitions. No conservation law has been computed or verified.
   archive_access_status is a placeholder based on compactness alone.

4. **Exterior observables**: NOT started in this kickoff (by design).
   Ringdown, shadow, and accretion packets are deferred to Phase III-C.

5. **Covariant extension**: All derivation is in Newtonian gauge.
   A fully relativistic treatment (TOV or equivalent) has not been attempted.

6. **The preferred endpoint law R_eq/r_s = alpha_vac = 1/3** is a
   CANDIDATE. It has not been tested against the current benchmark
   suite (which uses epsilon_Q = 0.1, giving R_eq/r_s = sqrt(0.1) = 0.316).
   The difference is ~5% but requires explicit verification.

---

## NEXT STEPS

### Phase III-A completion (remaining)
1. Run the acceptance suite with derived values (epsilon_Q = 1/9, beta_Q = 2)
2. Compare derived R_eq/r_s = 1/3 against benchmark R_eq/r_s = 0.316
3. If compatible, propose promoting epsilon_Q = alpha_vac^2 to CONSTRAINED

### Phase III-B (information)
1. Build a step-by-step dynamic information tracker
2. Define I_metric_memory from first principles (not proxy)
3. Test conservation through horizon crossing

### Phase III-C (exterior observables)
1. Exterior matching at the phase boundary
2. Ringdown / quasinormal mode analysis
3. Shadow computation
4. Accretion near-horizon emission
