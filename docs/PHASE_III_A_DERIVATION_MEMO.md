# Phase III-A Derivation Memo: epsilon_Q and beta_Q

**Status**: CONSTRAINED — not fully derived
**Date**: 2026-03-08
**Operator**: OP_QPRESS_001
**Equation**: a_Q = (GM/R²) × epsilon_Q × (r_s/R)^beta_Q
**Equilibrium**: R_eq/r_s = epsilon_Q^(1/beta_Q)

---

## 1. Problem Statement

Phase II established OP_QPRESS_001 as a phenomenological operator that produces
a genuine, stable, artifact-free finite-radius endpoint. But epsilon_Q and beta_Q
are unfixed free parameters (defaults: 0.1 and 2 for benchmarks). Phase III-A
must determine whether they can be derived or constrained from existing GRUT
structure.

## 2. Available Ingredients

From the frozen Phase I canon and Phase II solver:

| Constant | Value | Role |
|----------|-------|------|
| alpha_vac | 1/3 | Vacuum response parameter |
| screening_S | 108π ≈ 339.29 | 12π / alpha_vac² |
| lambda_lock | 2/√3 ≈ 1.1547 | Refractive index anchor |
| n_g(0) | √(4/3) = 2/√3 | Vacuum refractive index |
| K0_anchor | -1/12 | Curvature anchor |
| tau0 | 41.9 Myr | Memory relaxation timescale |
| chi(ω) | alpha_vac / (1 + (ωτ₀)²) | Vacuum susceptibility (Lorentzian) |
| t_grut | ((2πτ₀)²/alpha_vac × t_DP)^(1/3) | Self-consistent decoherence |
| R_anomaly | ~1.15428 | 3-loop anomaly residue (Tier B) |

## 3. Candidate Derivation Tracks

### Track A: Curvature-Linked Occupancy (PREFERRED)

**Core idea**: The barrier scaling mirrors the Kretschner curvature invariant.

The Kretschner scalar K = 48(GM)²/(c⁴R⁶) can be rewritten:
```
K × R⁴ × c⁴ / (48 G²M²) = (r_s / R)² = C²
```

The compactness-squared C² = (r_s/R)² appears naturally in curvature invariants.
If the quantum pressure barrier is proportional to the curvature load on the
vacuum — i.e., the vacuum resists compression proportionally to the local
curvature — then:
```
a_Q / a_grav ∝ C^beta_Q
```
With curvature ∝ C², the natural scaling is **beta_Q = 2**.

For the coupling strength epsilon_Q, the question is: at what curvature
does the vacuum begin to saturate? In GRUT, the vacuum response is
characterized by alpha_vac = 1/3. The natural threshold is:

**Candidate A1**: epsilon_Q = alpha_vac² = 1/9 ≈ 0.1111
```
R_eq / r_s = (1/9)^(1/2) = 1/3 ≈ 0.3333
Endpoint compactness C_eq = 3
```

**Candidate A2**: epsilon_Q = alpha_vac = 1/3
```
R_eq / r_s = (1/3)^(1/2) = 1/√3 ≈ 0.5774
Endpoint compactness C_eq = √3 ≈ 1.732
```

**Candidate A3**: epsilon_Q = alpha_vac³ = 1/27 ≈ 0.0370
```
R_eq / r_s = (1/27)^(1/2) ≈ 0.1925
Endpoint compactness C_eq ≈ 5.196
```

**Assessment**:
- A1 is closest to the benchmark value (0.1 vs 0.1111), produces a clean
  fraction R_eq/r_s = 1/3, and gives C_eq = 3 (well inside the horizon).
- A2 puts the endpoint barely inside the horizon (C = 1.73).
- A3 puts it very deep (C ≈ 5.2).
- A1 has the strongest dimensional motivation: alpha_vac enters TWICE because
  the barrier involves both the vacuum response (one factor of alpha_vac) and
  the vacuum saturation threshold (another factor of alpha_vac).

**Ranking**: A1 > A2 > A3

**Missing closure for A1**:
1. A micro-derivation showing WHY epsilon_Q = alpha_vac² specifically
   (not just dimensional coincidence)
2. Whether the factor-of-two is alpha_vac entering the response amplitude
   AND the saturation threshold independently
3. Whether this survives in a fully covariant treatment

### Track B: Bandwidth Saturation / Susceptibility Gradient

**Core idea**: The vacuum has finite temporal bandwidth. Near a compact
object, dynamical frequencies exceed the vacuum response bandwidth, creating
a gradient in vacuum stiffness that manifests as a repulsive force.

The vacuum susceptibility is:
```
chi(ω) = alpha_vac / (1 + (ω τ₀)²)
```

The local dynamical frequency near mass M at radius R:
```
ω_local ~ 1/t_dyn = √(2GM/R³) = c/r_s × (r_s/R)^(3/2) / √2
```

The vacuum capacity at radius R:
```
Capacity(R) = chi(ω_local) / chi(0) = 1 / (1 + (τ₀/t_dyn)²)
```

The gradient of capacity creates a pressure:
```
F_bandwidth ∝ -dCapacity/dR ∝ ... → power law in r_s/R
```

**Problem**: With bare τ₀ = 41.9 Myr, the capacity drops to 1/2 at
R_half ≈ (2GM τ₀²)^(1/3) >> r_s (by many orders of magnitude for
astrophysical M). The bandwidth saturation happens FAR outside the
Schwarzschild radius.

The local-tau closure (τ_local = τ₀ × t_dyn/(t_dyn + τ₀)) already
addresses this by dynamically adapting the timescale. With local-tau:
```
τ_local/t_dyn = τ₀/(t_dyn + τ₀) → 1 as t_dyn → 0
```
So the bandwidth ratio saturates at 1, never diverges.

**Assessment**: This track motivates the EXISTENCE of a barrier (vacuum
stiffness gradient) but does not fix the exact power law or coupling
strength. It is compatible with Track A but does not independently
determine epsilon_Q or beta_Q.

**Missing closures**:
1. Exact mapping from susceptibility gradient to acceleration
2. Why the barrier has a simple power-law form
3. How local-tau interacts with the bandwidth-derived barrier

**Ranking**: Second-best. Useful as motivation, not as derivation.

### Track C: Anomaly Bridge

**Core idea**: The 3-loop anomaly residue R ~ 1.15428 acts as a UV
regulation anchor. If the barrier operator and the quantum decoherence
operator both emerge from the same finite-bandwidth vacuum, their coupling
constants may be related through R.

Possible mappings:
```
epsilon_Q = R^(-n) for some n?
  R^(-2) ≈ 0.750  (too large)
  R^(-6) ≈ 0.422  (too large)
  R^(-20) ≈ 0.053 (plausible range but arbitrary)
```

**Assessment**: No clean dimensional link exists between R_anomaly and
epsilon_Q. The anomaly residue is a UV quantity; the barrier is an IR
phenomenon. While a deep unification might connect them, this is currently
speculative.

**Missing closures**: Everything. No structural derivation path exists.

**Ranking**: Weakest. Defer to Phase III-B or later.

## 4. Preferred Path

**beta_Q = 2**: Constrained by curvature scaling (Track A).
Kretschner invariant provides (r_s/R)² dependence.
Status: CONSTRAINED (dimensionally motivated, not rigorously derived).

**epsilon_Q = alpha_vac²**: Best candidate from Track A.
Produces R_eq/r_s = 1/3 (exact), C_eq = 3, benchmark-compatible.
Status: CANDIDATE (within 11% of current benchmark default 0.1).

**Combined law**:
```
a_Q = (GM/R²) × alpha_vac² × (r_s/R)²
    = GM × alpha_vac² × r_s² / R⁴
    = (4G³M³ / c⁴) × alpha_vac² / R⁴

R_eq / r_s = alpha_vac = 1/3
Endpoint compactness: C_eq = 1/alpha_vac = 3
```

Note: If epsilon_Q = alpha_vac² and beta_Q = 2, then
R_eq/r_s = alpha_vac^(2/2) = alpha_vac. The endpoint radius IS alpha_vac
times the Schwarzschild radius. This is an extraordinarily clean relation.

## 5. Independence of epsilon_Q and beta_Q

Under the curvature-linked occupancy track:
- **beta_Q** is determined by the geometric scaling of the curvature
  invariant (= 2 for Kretschner-linked). This is GEOMETRIC.
- **epsilon_Q** is determined by the vacuum coupling strength (= alpha_vac²
  for the double-response interpretation). This is COUPLING.

They are conceptually independent: beta_Q comes from geometry, epsilon_Q
from vacuum physics. However, the endpoint law R_eq/r_s = alpha_vac links
them into a single prediction that can be falsified.

## 6. Falsifiability

The preferred track makes specific predictions:
1. R_eq/r_s = alpha_vac = 1/3 (not 0.316 as in current benchmarks)
2. C_eq = 3 (endpoint is at compactness 3, inside horizon)
3. Changing alpha_vac would change R_eq proportionally
4. The scaling exponent beta_Q = 2 is exact (not 1.9 or 2.1)

These are testable against future constraints on epsilon_Q and beta_Q.

## 7. Implementation Recommendation

**Do not change the default epsilon_Q/beta_Q values yet.** Instead:
1. Add a `parameter_origin` metadata field to track provenance
2. Add a `derived_mode` option where epsilon_Q = alpha_vac², beta_Q = 2
3. Run the acceptance suite with derived values to check compatibility
4. Keep the current UNFIXED defaults (epsilon_Q=0, beta_Q=2) as the
   backward-compatible zero-regression path

## 8. Status Summary

| Parameter | Current Status | Proposed Status | Derivation Track |
|-----------|---------------|-----------------|------------------|
| beta_Q = 2 | UNFIXED | CONSTRAINED | Curvature scaling |
| epsilon_Q = alpha_vac² | UNFIXED | CANDIDATE | Occupancy threshold |
| R_eq/r_s = alpha_vac | CANDIDATE | CANDIDATE (strengthened) | Combined law |
| C_eq = 3 | not computed | CANDIDATE | Combined law |

## 9. Exact Missing Closures

To promote from CONSTRAINED/CANDIDATE to DERIVED:

1. **Vacuum occupancy micro-derivation**: Show that the gravitational field
   "occupies" vacuum degrees of freedom proportionally to C², and that
   saturation begins at alpha_vac² of capacity. This requires a statistical
   mechanics argument about vacuum mode counting.

2. **Curvature-to-force mapping**: Derive the exact form a_Q ∝ a_grav × C²
   from the gradient of vacuum stiffness, not just dimensional matching.

3. **Covariant extension**: Verify that the Newtonian-gauge power law
   (r_s/R)^beta_Q survives in a fully relativistic treatment (Tolman-
   Oppenheimer-Volkoff or similar).

4. **Connection to quantum decoherence**: Show whether the self-consistent
   decoherence law t_grut ∝ (τ₀²/alpha_vac × t_DP)^(1/3) shares the
   same alpha_vac dependence for the same reason.
