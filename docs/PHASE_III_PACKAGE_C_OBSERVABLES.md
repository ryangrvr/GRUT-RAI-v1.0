# Package C — Final Observable Closure

**DATE**: 2026-03-12
**STATUS**: FIRST-PASS ESTIMATES — order-of-magnitude bounds

---

## 1. Tidal Love Numbers

For a GR black hole: k₂ = 0 exactly.
For a GRUT BDCC with reflecting boundary at R_eq = r_s/3: k₂ ≠ 0.

### Mechanism

A tidal perturbation from infinity crosses the potential barrier at the
light ring (r ~ 3M), enters the horizon region, and encounters the BDCC
at R_eq. The BDCC reflects a fraction (r_surface ≈ 0.30). The reflected
wave crosses the barrier outward (transmission |T|²), modifying the
exterior field and producing a non-zero tidal response.

### Estimate

    k₂ ~ |T|² × r_surface ~ 0.037 × 0.30 ≈ 0.011

- |T|² ≈ 0.037 (barrier transmission, from echo analysis)
- r_surface ≈ 0.30 (PDE reflection coefficient)
- k₂_upper ≈ 0.037 (perfect reflection at zero frequency)

For comparison:
- GR black hole: k₂ = 0
- Neutron star: k₂ ~ 0.01–0.15

The GRUT BDCC Love number is comparable to the low end of neutron star
values — a potential discriminant, but not dramatic.

### Channel Classification

**CANDIDATE NON-NULL** — potential observable distinct from echoes.
Requires full Zerilli equation with GRUT boundary conditions for
precision estimate.

---

## 2. Kerr / Spin Extension (Bounded First Pass)

### What Changes with Spin

| Quantity | Schwarzschild (χ=0) | Kerr (χ=0.7) | Scaling |
|----------|-------------------|-------------|---------|
| Horizon r_+ / M | 2.0 | 1.71 | r_+ = M(1+√(1−χ²)) |
| Light ring r_LR / M | 3.0 | 2.17 | Decreases with spin |
| Echo delay ratio | 1.0 | 0.72 | Shorter cavity |
| QNM ω ratio | 1.0 | 1.29 | Higher frequency |
| ISCO r/M | 6.0 | 3.39 | Moves inward (prograde) |

### Structural Identity

ω₀τ = 1 was derived for Schwarzschild. For Kerr:
- Low spin (χ < 0.3): likely preserved (same scaling arguments apply)
- Moderate spin (0.3 < χ < 0.7): needs explicit verification
- High spin (χ > 0.7): needs verification, potential for spin-dependent corrections

### What Is NOT Attempted

- Boyer-Lindquist interior with memory field
- Kerr QNM spectrum with GRUT corrections
- Superradiance and ergoregion effects
- Spin-dependent R_eq(a)

---

## 3. Nonlinear Mode Coupling

### Leading Estimate

The force balance F(R) has nonlinear structure from the barrier term
a_Q ∝ (r_s/R)^β_Q. Taylor expansion around R_eq:

    F(R_eq + δR) = F'δR + ½F''δR² + ...

The quadratic correction coefficient:

    c₂ = β_Q(β_Q + 1)/2 = 3  (for β_Q = 2)

Correction to Q:

    ΔQ/Q ~ c₂ × (δR/R_eq)² = 3 × ε²

For ε = 0.01 (small perturbation): ΔQ/Q ~ 3 × 10⁻⁴ — **negligible**.
For ε = 0.1 (moderate): ΔQ/Q ~ 3% — **small correction**.
Breakdown at ε ~ 1/√3 ≈ 0.58 (merger-level).

### Conclusion

Universal Q = 6 is **robust** for small and moderate perturbations.
Nonlinear effects become important only at merger-level amplitudes,
which is precisely where the linearised PDE framework breaks down anyway.

---

## 4. Observability / Detector Relevance

### Channel Summary

| Channel | Amplitude | Current (O4/O5) | 3G (ET/CE) | Space (LISA) |
|---------|-----------|-----------------|------------|--------------|
| Echoes | ~1.1% QNM | MARGINAL | DETECTABLE | DETECTABLE |
| Love numbers | k₂ ~ 0.01 | CHALLENGING | CONSTRAINABLE | N/A |
| Shadow/ISCO | NULL | — | — | — |
| Spin corrections | O(a/M) | N/A | MEASURABLE (if echoes found) | RELEVANT |

### Falsification Pathways

1. **Echo non-detection at 3G**: If ET/CE sees high-SNR ringdowns with
   no echoes at ~0.1%, the mixed_viscoelastic BDCC at current parameters
   is excluded (Boltzmann model still viable).

2. **Love number measurement**: If BH-BH tidal deformability is measured
   at Λ = 0 to high precision, the reflecting BDCC is constrained.

3. **Echo with wrong parameters**: Echoes at amplitudes or delays
   inconsistent with predictions would falsify specific parameters.

---

## 5. Nonclaims

1. All estimates are ORDER OF MAGNITUDE — not precision calculations
2. Love number needs full Zerilli equation with GRUT boundary conditions
3. Kerr extension is PARAMETRIC, not a full Boyer-Lindquist solution
4. Nonlinear estimate valid for small perturbations only
5. Detectability depends on analysis pipeline, not just signal amplitude
6. Boltzmann model (r ≈ 0) remains viable
7. Static channels are IDENTICALLY NULL — not falsification targets
8. No claim that current or future data WILL detect GRUT signatures

---

## Files

| File | Role |
|------|------|
| `grut/observables_final.py` | Love numbers, Kerr, nonlinear, detectability |
| `tests/test_packages_abc.py` | 18 tests (Package C classes) |
