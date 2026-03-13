# Phase III-C WP1 Decision Framework

**Date**: 2026-03-09
**Status**: WP1 analysis complete. Decision rendered.

---

## Gateway Question

Does a Barrier-Dominated Compact Core at R_eq = (1/3) r_s produce any
exterior deviation from standard black-hole behavior?

## Answer

**Current best assessment**: The exterior is SCHWARZSCHILD-LIKE (leading
candidate), conditional on two underdetermined assumptions:

1. M_drive is matter-local (not a spacetime field)
2. OP_QPRESS_001 has no exterior gravitational self-energy

This is a **moderate-confidence** assessment. It is consistent with the
solver but not proven by it. A covariant treatment is required for a
rigorous determination.

---

## Decision: WP2 (Ringdown / Echo)

### GO — CONDITIONAL

**Basis**: Under the Schwarzschild-like exterior candidate:

- The exterior metric is known (standard Schwarzschild).
- The light ring and QNM spectrum are standard GR.
- BUT: the interior BDCC may reflect perturbations, producing echoes.
- Echo computation depends on the interior effective potential and
  boundary condition at R_eq, which can be modeled under reasonable
  assumptions about the interior metric.

**What WP2 can compute now**:
- Effective potential in the interior, parameterized by the force balance
- Reflection coefficient at R_eq as a function of interior boundary model
- Echo time delay t_echo = 2 × integral from R_reflect to R_peak
- Zeroth-order QNM spectrum (identical to GR under Schwarzschild exterior)

**What WP2 cannot compute without further WP1 work**:
- First-order QNM shifts (require delta_f, which is not determined)
- Exterior metric modifications (require covariant treatment)

**Condition**: WP2 results must be labeled as "computed under
Schwarzschild-like exterior" with the explicit caveat that the exterior
has not been proven to be Schwarzschild.

---

## Decision: WP3 (Shadow / Accretion)

### GO — EXPECTED NULL RESULT

**Basis**: Under the Schwarzschild-like exterior candidate:

- The photon sphere is at R = (3/2) r_s (standard GR value).
- The shadow radius is determined by the photon sphere (standard GR).
- No deviation from Schwarzschild shadow is expected.
- **The shadow question is trivially answered: no deviation.**

**What makes WP3 non-trivial**:
- If WP1 is later revised to find exterior deviations (delta_f ≠ 0),
  the shadow computation becomes interesting.
- Near-horizon emission from accreting matter near R_eq could differ
  from GR if any matter accumulates near the BDCC surface.

**Recommendation**: WP3 can proceed as a quick check to confirm the null
result, but it is low priority compared to WP2 (which can produce
non-trivial echo predictions even with Schwarzschild exterior).

---

## Decision Matrix

| Condition | WP2 Status | WP3 Status |
|-----------|------------|------------|
| Exterior = Schwarzschild (leading candidate) | GO — interior echoes possible | GO — expected null |
| Exterior = weakly modified (delta_f small) | GO — echoes + small QNM shifts | GO — small shadow deviation |
| Exterior = strongly modified (delta_f large) | GO — full ringdown change | GO — measurable shadow shift |
| Exterior = underdetermined | STOP — need exterior metric | STOP — need exterior metric |

**Current status**: Row 1 (Schwarzschild-like, conditional).

---

## When Must We Stop and Derive More?

### WP2 must stop if:
- The interior effective potential depends critically on assumptions
  about the GRUT metric structure that are not determined by the
  Newtonian-gauge solver.
- The boundary condition at R_eq is completely ambiguous (purely
  reflecting vs. purely absorbing produces qualitatively different
  results, and we cannot choose between them).

### WP3 must stop if:
- Evidence emerges that the exterior is modified, but delta_f is
  not parameterized well enough to compute null geodesics.

### The entire Phase III-C must stop if:
- A contradiction is found between the Newtonian-gauge endpoint and
  what a covariant treatment would give (e.g., the endpoint does not
  survive in TOV).

---

## Execution Order

```
WP1 (this document) → DONE (Schwarzschild-like, conditional GO)
    │
    ├─→ WP2 (Ringdown / Echo) — HIGH PRIORITY
    │   Start with: interior effective potential, echo timing
    │   Label all results: "under Schwarzschild-like exterior"
    │
    └─→ WP3 (Shadow) — LOW PRIORITY
        Confirm null result under Schwarzschild exterior.
        Defer detailed computation until exterior status clarified.
```

---

## Explicit Nonclaims for WP1 Decision

1. The exterior is NOT proven to be Schwarzschild.
2. The conditional GO for WP2 does NOT mean the echo predictions are
   final — they are parameterized under an assumed background.
3. The null result for WP3 does NOT mean GRUT predicts zero shadow
   deviation — it means the current leading exterior candidate gives
   zero deviation. If the exterior assessment changes, WP3 results change.
4. The covariant treatment remains a high-priority missing closure.
5. This decision framework may be revised if new information changes
   the exterior assessment.
