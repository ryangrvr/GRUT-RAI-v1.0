# Package B — Boundary / Matching Closure

**DATE**: 2026-03-12
**STATUS**: EFFECTIVE-LEVEL JUNCTION CONDITIONS

---

## 1. Junction Conditions with Memory

Israel-Darmois junction conditions at the BDCC boundary (R = R_eq = r_s/3):

### First Junction (Metric Continuity)

The induced metric on the matching surface Σ is continuous. The angular
metric R²_eq dΩ² is continuous by construction. The lapse function g_tt
has a jump (Δg_tt = δ_A from barrier correction) which is absorbed into
the surface stress-energy via the second junction condition.

### Second Junction (Extrinsic Curvature)

    [K_ij] = −8πG (S_ij − ½ S h_ij)

The jump in extrinsic curvature encodes the surface energy density σ and
surface pressure P at the BDCC boundary:
- σ: determined by the barrier equilibrium force balance
- P: determined by tangential stress balance

Both are constitutive (derived from the barrier equilibrium, not from an
action principle). They are order-of-magnitude estimates.

### Memory Field Matching

- Interior: Φ = M_drive at equilibrium = a_grav = GM/R²_eq
- Exterior: Φ = 0 (no memory field in Schwarzschild vacuum)
- Jump: ΔΦ = a_grav (full jump across boundary)
- Resolution: smooth transition through the WP2D transition layer
  (width ~0.703 r_s, grading factor 0.996)

**Inside-horizon subtlety**: R_eq = r_s/3 is inside the Schwarzschild
horizon (compactness C = 3/2). The standard Israel formalism requires
analytic continuation in the trapped region where r is timelike. The
BDCC is a static equilibrium maintained by the barrier, not a trapped
surface in the conventional sense.

---

## 2. Transition-Width in Covariant Framework

The WP2D transition profile Φ(t) = 1 − t^0.426 connects the interior
(full barrier, full memory) to the exterior (Schwarzschild vacuum, no memory).

### Covariant Embedding

- Inner edge: A_eff = A_schw + δ_A (barrier-corrected lapse)
- Outer edge: A_eff → A_schw (pure Schwarzschild)
- Memory field: Φ smoothly transitions from a_grav to 0
- Grading factor: 0.996 (< 1% impedance correction)
- Sharp-boundary approximation: VALIDATED

The transition layer is embedded in the covariant framework by treating
the Φ-profile as a radial function connecting the interior effective
metric to the exterior Schwarzschild metric.

---

## 3. Matching Consistency

| Quantity | Status |
|----------|--------|
| Angular metric | Continuous (by construction) |
| Total enclosed mass | Conserved (dust, no radiation) |
| Birkhoff compatibility | Preserved (memory confined to interior) |
| g_tt (lapse) | Jump absorbed into σ_surface |
| Memory field Φ | Smooth transition via WP2D profile |

### Underdetermined

- Φ derivative at boundary (depends on transition profile dynamics)
- Tangential stress through transition layer
- Higher multipole (l > 0) matching
- Dynamic (time-dependent) junction conditions

---

## 4. Nonclaims

1. Junction conditions at EFFECTIVE LEVEL, not from field equations
2. σ_surface is constitutive, not action-derived
3. Memory field continuity assumed (natural for scalar), not derived
4. Sharp-boundary approximation VALIDATED (< 1% correction)
5. Matching for EQUILIBRIUM state only — dynamic junctions not evaluated
6. Inside-horizon matching requires analytic continuation
7. Higher multipole matching NOT attempted
8. Transition profile is heuristic, not from a dynamical equation for Φ

---

## Files

| File | Role |
|------|------|
| `grut/junctions.py` | Junction conditions, transition layer, matching |
| `tests/test_packages_abc.py` | 11 tests (Package B classes) |
