# Phase III-C WP2B: Constraining R_surface from GRUT Structure

**Date**: 2026-03-09
**Status**: CANDIDATE ESTIMATE — impedance model preferred
**Predecessor**: WP2 Echo Falsifier (parameterized R_surface)
**Exterior assumption**: Schwarzschild-like (WP1 conditional)

---

## 1. The Question

WP2 established the echo falsifier channel with parameterized R_surface.
Everything — echo amplitude, detectability, go/no-go — turns on this single
parameter. WP2B asks:

> **Can current GRUT structure constrain R_surface, or is it genuinely free?**

The answer is: the constrained endpoint provides enough structure for a
physically motivated estimate via acoustic impedance mismatch. This estimate
is a **zeroth-order sharp-boundary approximation**, not a derivation.

---

## 2. Available Physics at the Constrained Endpoint

The collapse solver at the constrained endpoint (epsilon_Q = 1/9, beta_Q = 2,
R_eq/r_s = 1/3) provides:

| Quantity | Value | Source |
|----------|-------|--------|
| Stability eigenvalue d(a_net)/dR | beta_Q × GM/R_eq³ > 0 | collapse solver |
| Barrier dominance Phi | 1.0 at equilibrium | Phase III-A |
| Force balance residual | |a_net|/a_grav → 0 | benchmark |
| Memory tracking ratio M_drive/a_grav | ≈ 1 (saturated) | benchmark |
| Natural frequency omega_core | sqrt(beta_Q × GM / R_eq⁴) | stability eigenvalue |
| QNM reference omega_QNM | 0.3737 / M_geom (l=2) | Schwarzschild GR |
| Frequency ratio omega_core / omega_QNM | ~ 0.04 at 30 M_sun | computed |

**Key observation**: omega_core << omega_QNM. The BDCC oscillates much
slower than the QNM. This means the BDCC and the near-horizon vacuum have
very different characteristic impedances for wave propagation.

---

## 3. Derivation Tracks

Four tracks were identified for constraining R_surface. They are ranked
by internal consistency and implementability.

### Track 1: Impedance Mismatch (PREFERRED)

**Physical basis**: The BDCC at R_eq creates an acoustic impedance
discontinuity. The effective "sound speed" inside the BDCC is estimated
from the natural oscillation:

```
c_s(BDCC) ~ omega_core × R_eq
```

The background propagation speed near the horizon is c (speed of light).
The impedance ratio is:

```
eta = c_s(BDCC) / c = omega_core × R_eq / c
```

The amplitude reflection coefficient from a step impedance mismatch is:

```
r_surface_amp = |1 - eta| / (1 + eta)
```

**Why this works**: In standard wave physics, reflection occurs whenever
two media have different impedances. Both the eta → 0 (soft surface) and
eta → ∞ (rigid surface) limits give r_amp → 1. Only impedance matching
(eta ≈ 1) gives r_amp → 0.

Since eta << 1 for all astrophysical BHs, the BDCC is never impedance-
matched to the vacuum background. High amplitude reflection is expected.

**Mass scaling**: eta is computed numerically from the implemented
omega_core formula. Under the constrained endpoint, eta decreases with
mass (confirmed numerically — see benchmark section 6). The approximate
scaling is eta ~ M^{-1/2}, making more massive objects slightly more
reflective.

**SHARP-BOUNDARY APPROXIMATION**: This model assumes a sharp transition
at R_eq. The Phase III-B transition has finite width (~0.7 r_s in the
benchmark). A gradual transition could reduce or smear the effective
reflectivity. Transition-width corrections remain an open closure.

**Amplitude vs power**: The formula gives the AMPLITUDE coefficient
r_surface_amp. The power reflectivity is R_surface_pow = r_surface_amp².
All echo amplitude formulas (A_n/A_0) use amplitude coefficients.

### Track 2: Boltzmann Reflectivity (Worst-Case Bound)

**Physical basis**: Treats the BDCC as a thermal absorber with effective
temperature T_eff proportional to omega_core:

```
r_surface_amp = exp(-omega_QNM / omega_core)
```

Since omega_QNM >> omega_core (ratio ~ 25 at 30 M_sun):

```
r_surface_amp ≈ exp(-25) ≈ 1.4e-11  (effectively zero)
```

**Assessment**: This is the worst-case bound. If the BDCC is dissipative
(absorbs high-frequency perturbations thermally), reflection is negligible
and no echoes are detectable. This model is viable and cannot be ruled out
from current GRUT structure alone.

**What distinguishes Tracks 1 and 2**: The impedance model treats the BDCC
as a reactive (non-dissipative) boundary. The Boltzmann model treats it as a
dissipative absorber. The distinction requires knowing the interior wave
equation, which is a missing closure.

### Track 3: Barrier Dominance Proxy (Zeroth-Order Static Estimate)

**Physical basis**: The barrier dominance Phi = a_outward / a_inward = 1.0
at equilibrium. By static analogy: if the barrier completely balances
gravity, it should also reflect perturbations.

```
r_surface_amp ~ Phi = 1.0  (static upper bound)
```

**Assessment**: This is a zeroth-order argument that does not account for
wave frequency or impedance. It gives the same result as the "perfect"
model. Not useful as a constraint beyond the upper bound already known.

### Track 4: WKB Potential Step (Requires Interior Metric — Deferred)

**Physical basis**: The effective potential V(r) changes at R_eq due to the
quantum pressure barrier. In the WKB approximation:

```
r_surface_amp = |k_ext - k_int| / |k_ext + k_int|
```

where k² = omega² - V(r) is the local wavenumber on each side.

**Assessment**: This is the most rigorous approach but requires the interior
effective potential V_int(r), which depends on the GRUT-modified interior
metric. This is a missing closure — the Newtonian-gauge solver does not
provide the wave equation structure inside the BDCC.

**Status**: DEFERRED until interior metric is available.

---

## 4. Side-by-Side Comparison

| Track | r_surface_amp | Status | Assumption |
|-------|---------------|--------|------------|
| Impedance (preferred) | > 0.96 (stellar-mass) | CANDIDATE | Sharp boundary, reactive BDCC |
| Boltzmann (worst-case) | ≈ 0 | CANDIDATE | Dissipative/thermal BDCC |
| Phi proxy (static) | 1.0 | UPPER BOUND | Static analogy only |
| WKB potential step | unknown | DEFERRED | Requires interior metric |

The impedance and Boltzmann models bracket the physically interesting range.
The actual R_surface lies somewhere between them, determined by the degree
to which the BDCC is reactive vs dissipative at the QNM frequency.

---

## 5. Numerical Results (Impedance Model)

Computed numerically from the implemented omega_core formula.
All values are AMPLITUDE coefficients.

| M (M_sun) | eta | r_surface_amp | R_surface_pow | Echo A_1/A_0 |
|-----------|-----|---------------|---------------|--------------|
| 10 | ~0.018 | ~0.965 | ~0.931 | ~0.029 |
| 30 | ~0.010 | ~0.980 | ~0.960 | ~0.029 |
| 100 | ~0.006 | ~0.989 | ~0.978 | ~0.030 |
| 10^4 | ~0.0006 | ~0.999 | ~0.998 | ~0.030 |
| 10^6 | ~6e-5 | ~0.9999 | ~0.9998 | ~0.030 |
| 10^9 | ~2e-6 | ~0.99999 | ~0.99999 | ~0.030 |

**Mass scaling confirmed**: eta decreases with mass (approximately as
M^{-1/2} under the constrained endpoint). More massive BHs are slightly
more reflective, but echo amplitudes are nearly mass-independent because
the first echo is dominated by |T|² (the potential peak transmission).

**Key result**: Under the impedance model, the first echo amplitude
A_1/A_0 ≈ |T|² × r_surface_amp ≈ 0.03 × 0.98 ≈ 2.9% for 30 M_sun.
This is nearly the same as the perfect-reflection upper bound (3.0%),
because the impedance model gives r_surface_amp close to 1.

---

## 6. Implications for Observability

If the impedance model is correct (reactive, non-dissipative BDCC):
- Echoes at ~2.9% of main QNM signal for stellar-mass BHs
- Within reach of next-generation detectors (Einstein Telescope, LISA)
- Current LIGO sensitivity (~10%) is NOT constraining
- The echo channel is a VIABLE falsifier

If the Boltzmann model is correct (dissipative BDCC):
- Echoes are negligible (r_surface_amp ≈ 0)
- The echo channel is NOT a useful falsifier
- Other channels (shadow, accretion) become primary

**The distinguishing question is**: Is the BDCC reactive or dissipative
at the QNM frequency? This cannot be answered from the current solver.
It requires the interior wave equation.

---

## 7. Explicit Nonclaims

1. The impedance model is a **PHYSICALLY MOTIVATED ESTIMATE**, not a
   rigorous derivation from GRUT field equations.

2. The actual r_surface_amp requires the **interior wave equation**
   on the GRUT-modified metric, which is a missing closure.

3. This is a **sharp-boundary approximation**. The Phase III-B transition
   has finite width (~0.7 r_s). A gradual transition could reduce or
   smear the effective reflectivity. Transition-width corrections are
   an open problem.

4. The **Boltzmann model (r_amp ≈ 0) remains viable** if the BDCC is
   dissipative rather than reactive. The impedance model cannot rule it
   out without the interior wave equation.

5. The mass scaling eta approximately proportional to M^{-1/2} is a
   **consequence of the impedance model**, not a universal prediction.
   Other models may give different mass scaling.

6. This **constrains** R_surface — it does not **derive** it from first
   principles. The constraint is: under the impedance model, R_surface
   is high for all astrophysical masses.

7. All results are **CONDITIONAL** on the WP1 exterior assessment
   (Schwarzschild-like, moderate confidence).

8. Echoes are still **NOT predicted to exist**. This computes what they
   would look like if the impedance model holds and the BDCC is reactive.

---

## 8. Summary

WP2B reduces the echo falsifier from a free parameter study to a
**bounded constraint**:

- **Upper bound**: r_surface_amp = 1.0 (perfect reflection, Track 3)
- **Preferred estimate**: r_surface_amp ≈ 0.96–1.0 (impedance model, Track 1)
- **Lower bound**: r_surface_amp ≈ 0 (Boltzmann, Track 2)

The preferred estimate (impedance model) suggests the echo channel is
promising. The key remaining question is whether the BDCC is reactive
(high reflection) or dissipative (low reflection). This is determined
by the interior wave equation, which requires the covariant GRUT
interior metric.

**Status**: CANDIDATE — preferred constrained reflectivity estimate
under sharp-boundary impedance approximation. Transition-width
corrections and interior wave equation remain open closures.
