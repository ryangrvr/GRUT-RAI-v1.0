# Phase III-C WP2 Roadmap: Ringdown / Echo Falsifier Track

**Date**: 2026-03-09
**Status**: FORMULATION COMPLETE — first echo estimates computed
**Predecessor**: WP1 Exterior Matching (Schwarzschild-like, conditional GO)
**Exterior assumption**: All results labeled as computed under Schwarzschild-like exterior

---

## 1. The Physical Problem

### Standard GR Ringdown

When a black hole is perturbed (e.g., by a merger), it rings down through
quasinormal modes (QNMs). These are damped oscillations of the spacetime
metric governed by the Regge-Wheeler (odd parity) and Zerilli (even parity)
effective potentials.

The key features:
- The potential peak is at the light ring: r = (3/2) r_s in Schwarzschild
- The ingoing boundary condition at the horizon is PURELY ABSORBING:
  waves enter the horizon and never return
- The QNM spectrum depends only on M (and J for Kerr)
- The fundamental l=2 mode has: ω_R ≈ 0.3737 / M, τ_damp ≈ 17.8 M
  (in geometric units G=c=1)

### The GRUT Modification

If a Barrier-Dominated Compact Core exists at R_eq = (1/3) r_s:
- The horizon still exists at r = r_s (C = 1)
- Below the horizon, the collapse halts at R_eq (force balance)
- The BDCC has a restoring equilibrium (positive stability eigenvalue)
- Perturbations around R_eq are RESTORED, not absorbed

This means the "purely absorbing" horizon boundary condition is replaced by
a partially or fully reflecting boundary — and that changes the ringdown
signal.

### The Echo Mechanism

1. An ingoing perturbation crosses the potential peak at the light ring
2. It enters the horizon region and propagates inward
3. Instead of falling to the singularity, it encounters the BDCC
   transition zone
4. If the BDCC reflects some fraction, the wave propagates outward
5. It reaches the potential peak, where part leaks out (observable)
   and part reflects back inward
6. This creates a series of delayed pulses — ECHOES — with decreasing
   amplitude and characteristic time delay

The echo time delay is:
```
Δt_echo ≈ 2 × |r*(R_reflect) - r*(R_peak)|
```
where r* is the tortoise coordinate.

---

## 2. Why This Is Non-Trivial Even Under Schwarzschild Exterior

Even with an exactly Schwarzschild exterior (WP1 leading candidate):
- The exterior potential peak is standard GR
- The transmission/reflection at the peak is standard GR
- BUT: the interior boundary condition changes
- Standard GR: purely absorbing (no reflection)
- GRUT: potentially reflecting (BDCC is a stable equilibrium)

Therefore: **echoes are the primary channel where the interior structure
leaks into an exterior observable**, even if the exterior metric is
exactly Schwarzschild.

---

## 3. Interior Boundary Condition at R_eq

### What the Solver Tells Us

At R_eq = (1/3) r_s under the constrained law:

- Φ = 1 (exact force balance)
- Stability eigenvalue: d(a_net)/dR = β_Q × GM/R_eq³ > 0
- With β_Q = 2: d(a_net)/dR = 2GM/(R_eq)³
- This is a RESTORING force — perturbations oscillate around R_eq

A restoring equilibrium behaves as a reflecting boundary for waves.
The effective "hardness" of the reflection depends on the ratio of
the wave frequency to the natural oscillation frequency of the BDCC.

### Natural Oscillation Frequency of the BDCC

From the stability eigenvalue, the natural radial oscillation frequency is:

```
ω_core² ≈ (1/R_eq) × d(a_net)/dR = β_Q × GM / R_eq⁴
```

Under the constrained law (β_Q = 2, R_eq = r_s/3):
```
ω_core² = 2GM / (r_s/3)⁴ = 2GM × 81 / r_s⁴
```

Since r_s = 2GM/c²:
```
ω_core = c/r_s × √(2 × 81 / (r_s/2GM)² × ...)
```

In geometric units (G = c = 1, r_s = 2M):
```
ω_core² = 2M / (2M/3)⁴ = 2M × 81 / (16 M⁴) = 162 / (16 M³)
ω_core = √(162/16) / M^{3/2} ≈ 3.18 / M^{3/2}
```

**Note**: This dimensional analysis gives the correct scaling but the
numerical prefactor requires a proper perturbation theory calculation
on the interior metric. The above is an ORDER OF MAGNITUDE ESTIMATE.

### Candidate Boundary Conditions

| Model | Description | Reflection coefficient |
|-------|-------------|----------------------|
| Perfectly reflecting | R(ω) = 1 for all ω | Upper bound on echo amplitude |
| Perfectly absorbing | R(ω) = 0 for all ω | Standard GR (no echoes) |
| Boltzmann reflectivity | R(ω) = exp(-|ω|/T_eff) | Thermal-like damping |
| Impedance mismatch | R(ω) from ω_core matching | Physics-motivated |

The solver-backed input is the stability eigenvalue, which supports
the impedance-mismatch model. The other models are parameterized
alternatives for comparison.

---

## 4. Echo Time Delay Estimate

### Tortoise Coordinate

In Schwarzschild coordinates, the tortoise coordinate is:
```
r* = r + r_s × ln|r/r_s - 1|
```

At the potential peak (r_peak = 3/2 r_s):
```
r*_peak = (3/2) r_s + r_s × ln(1/2) = r_s × (3/2 - ln 2) ≈ 0.807 r_s
```

### The Interior Problem

The reflecting surface is at R_eq = (1/3) r_s, which is INSIDE the
horizon. In Schwarzschild coordinates inside the horizon:
- r becomes timelike, t becomes spacelike
- The tortoise coordinate maps to r* = r + r_s × ln(1 - r/r_s) for r < r_s

At R_eq = r_s/3:
```
r*_eq = r_s/3 + r_s × ln(1 - 1/3) = r_s × (1/3 + ln(2/3))
     = r_s × (0.333 - 0.405) = -0.072 r_s
```

**IMPORTANT CAVEAT**: The tortoise coordinate in the standard
Schwarzschild interior assumes the standard interior metric. The GRUT
modification changes the interior (that's the whole point). The actual
wave travel time depends on the effective interior metric, which is a
WP1 missing closure.

### Estimate Under Schwarzschild Interior Metric

If we use the standard Schwarzschild tortoise coordinate as an
ORDER OF MAGNITUDE estimate:

```
Δt_echo ≈ 2 × |r*_eq - r*_peak|
        = 2 × |(-0.072) - 0.807| r_s
        = 2 × 0.879 r_s
        ≈ 1.76 r_s
```

In physical units: Δt_echo ≈ 1.76 × r_s / c

For a 10 M_☉ black hole (r_s ≈ 30 km):
```
Δt_echo ≈ 1.76 × 30 km / c ≈ 0.18 ms
```

For a 10⁶ M_☉ SMBH (r_s ≈ 3 × 10⁶ km):
```
Δt_echo ≈ 1.76 × 3e6 km / c ≈ 17.6 s
```

**CAVEAT**: This is an order-of-magnitude estimate using the standard
Schwarzschild tortoise coordinate. The actual travel time through the
GRUT-modified interior may differ significantly. The estimate is useful
for scaling (Δt ∝ M) but the numerical coefficient is uncertain.

---

## 5. Echo Amplitude Estimate

### Transfer Function

The standard echo transfer function (following Cardoso et al.) is:

```
h_echo(t) ≈ Σ_{n=1}^{∞} A_n × h_QNM(t - n × Δt_echo)
```

where:
- h_QNM is the standard QNM waveform
- A_n ≈ T² × (R_surface × R_peak)^n is the amplitude of the nth echo
- T is the transmission coefficient through the potential peak
- R_surface is the reflection coefficient at the BDCC
- R_peak is the reflection coefficient at the potential peak (from inside)

### Amplitude Scaling

For the Schwarzschild potential peak, the l=2 mode has:
- |T|² ≈ a few percent (most energy reflected back)
- |R_peak| ≈ 0.9+ (the potential peak is a good reflector from inside)

The first echo amplitude relative to the main QNM signal is:
```
A_1 / A_0 ≈ |T|² × |R_surface|
```

If |T|² ~ 0.03 and |R_surface| = 1 (perfect reflection):
```
A_1 / A_0 ~ 0.03  (3% of main signal)
```

If |R_surface| ~ 0.1 (weak reflection):
```
A_1 / A_0 ~ 0.003  (0.3% of main signal)
```

These are VERY rough estimates. The actual values depend on:
- The l-mode and spin of the perturbation
- The exact effective potential
- The frequency dependence of R_surface
- Phase effects (constructive/destructive interference)

---

## 6. What Would Count as a Discriminating Signal

### Positive Detection (echoes exist)

A positive echo detection would require:
1. A delayed post-ringdown signal at t ≈ n × Δt_echo
2. The time delay matches the GRUT prediction: Δt ∝ M
3. The amplitude is consistent with the computed R_surface

Current observational constraints:
- LIGO/Virgo have searched for echoes in binary BH mergers
- No confirmed detection, but current sensitivity limits are ~10% of
  the main signal amplitude
- Future detectors (LISA, Einstein Telescope) could reach ~0.1%

### Null Result (no echoes)

A null result at sufficient sensitivity would constrain:
- |R_surface| < observable threshold / |T|²
- For current LIGO: |R_surface| < ~3 (not constraining)
- For future detectors: |R_surface| < ~0.03 (constraining)

### What GRUT Predicts

GRUT does NOT yet predict a specific R_surface. It predicts:
- A STABLE equilibrium at R_eq (restoring, not absorbing)
- A natural oscillation frequency ω_core at R_eq
- These are CONSISTENT with a reflecting boundary but do not
  DETERMINE the reflection coefficient

The reflection coefficient requires:
- The effective interior metric (WP1 missing closure)
- A proper wave equation on that metric
- Matching at R_eq

---

## 7. Implementation Plan

### Module: grut/ringdown.py

**What it computes**:
1. Echo time delay from R_eq and r_s (order of magnitude)
2. Natural oscillation frequency of BDCC from stability eigenvalue
3. Parameterized echo transfer function for given R_surface
4. Amplitude of first N echoes
5. Comparison with standard GR (R_surface = 0)

**What it does NOT compute**:
1. R_surface from first principles (requires interior metric)
2. Full QNM spectrum (requires numerical relativity)
3. Kerr generalization (non-rotating only)

### Boundary Condition Models

Three parameterized models implemented:
1. **Perfectly reflecting**: R = 1 (upper bound)
2. **Boltzmann**: R = exp(-ω/T_eff) with T_eff from ω_core
3. **Constant**: R = R_0 (free parameter, for scanning)

---

## 8. Explicit Nonclaims

1. **Echo predictions are CONDITIONAL** on the Schwarzschild-like
   exterior from WP1 (which is itself conditional).
2. **No specific reflection coefficient is derived.** R_surface is
   parameterized, not computed from first principles.
3. **The echo time delay is an ORDER OF MAGNITUDE estimate** using the
   standard Schwarzschild tortoise coordinate. The GRUT-modified interior
   metric could change this significantly.
4. **No claim of echo detection or non-detection is made.** The module
   computes what echoes WOULD look like under various assumptions.
5. **Kerr generalization is not attempted.** Real astrophysical black
   holes rotate. Spin effects on echoes are significant.
6. **The interior effective potential is not derived.** It is
   parameterized from the stability eigenvalue.
7. **This is a FALSIFIER PROGRAM, not a prediction.** The goal is to
   identify what would need to be true for echoes to exist, not to
   claim they do exist.
