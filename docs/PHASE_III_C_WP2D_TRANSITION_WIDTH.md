# Phase III-C WP2D — Transition-Width and Spectrum Correction

> **SUPERSEDED** (v1.0): The proxy results in this document (Q ~ 515,
> reactive_candidate, ~3.7% echo) have been superseded by the PDE
> closure (Q ~ 6–7.5, mixed_viscoelastic, ~1.1% echo). See
> `PHASE_III_C_PDE_MEMO.md` for the leading result. The transition-width
> methodology (grading factor, multi-mode correction) remains valid and
> has been folded into the covariant framework (Package B). This
> document is retained as historical record.

**STATUS**: SUPERSEDED — was CANDIDATE graded-transition + multi-mode estimate
**EXTERIOR ASSUMPTION**: Schwarzschild-like (WP1 conditional)
**PREDECESSORS**: WP2B (impedance), WP2C (interior wave), Phase III-B (Phi mapping)

---

## 1. Question

Does the proxy reactive result from WP2C survive when:
1. The sharp-boundary impedance model is replaced by a graded transition?
2. The single-mode interior oscillator is replaced by a multi-mode spectrum?

---

## 2. Motivation

WP2B and WP2C both used simplifying assumptions:
- **WP2B**: sharp impedance step at R_eq (no transition zone)
- **WP2C**: single-mode damped oscillator (no overtones or continuum)

Phase III-B measured a **smooth transition** with width ~0.703 r_s from the
Quantum Fluid regime (Phi ~ 0) to the Barrier-Dominated Compact Core (Phi = 1).
The probe wavelength lambda_QNM ~ pi * r_s is comparable to this width —
the question is whether we are safely in the sharp-boundary limit.

---

## 3. Graded-Transition Model (Task 1)

### 3.1 Barrier Dominance Profile

The order parameter Phi(R/r_s) is parameterized by a power-law profile
calibrated to three Phase III-B anchor points:

    t = (R/r_s - R_eq/r_s) / transition_width_rs
    Phi(t) = 1 - t^alpha   for t in [0, 1]

where:
- t = 0 at R_eq/r_s = 1/3 (endpoint, Phi = 1.0)
- t = 1 at R_eq/r_s + width ≈ 1.036 (outer edge, Phi = 0)
- alpha = ln(0.5)/ln(t_cryst) ≈ 0.426 (from crystallization constraint)
- Phi(0.4715) = 0.5 (crystallization threshold, exact)

### 3.2 Local Impedance

In the transition zone, the local impedance ratio interpolates:

    eta_local(r) = (1 - Phi(r)) * 1.0 + Phi(r) * eta_BDCC

At Phi = 0 (vacuum): eta = 1 (impedance matched to incoming wave)
At Phi = 1 (BDCC): eta = eta_BDCC << 1 (large mismatch, high reflection)

### 3.3 Recursive Airy (Transfer Matrix) Computation

The transition zone is divided into N layers (default 100). The total
reflection is computed using the exact recursive Fresnel-Airy formula:

    r_eff = (r_interface + r_prev * exp(2i*delta)) /
            (1 + r_interface * r_prev * exp(2i*delta))

This properly handles all multiple reflections and is exact for stratified
media (no Born approximation). Convergence: 0.014% between N=100 and N=500.

### 3.4 Key Result

**The probe wavelength (lambda ~ pi * r_s) is ~12x the transition width
(0.703 r_s).** This places us firmly in the quasi-sharp regime where the
wave sees the transition as nearly sharp.

The grading factor = **0.996** (0.4% reduction from sharp boundary).
**The sharp-boundary impedance model is an EXCELLENT approximation.**

---

## 4. Multi-Mode Correction (Task 2)

### 4.1 Mode Spectrum

The BDCC supports multiple resonant modes:

    omega_n = omega_core * sqrt(1 + n*(n+1)*xi)

with xi = 0.1 (ORDER OF MAGNITUDE parameterized spacing).

For 30 M_sun (n_modes = 3):
- Mode 0: omega = 102.3 rad/s, Q = 515.6, weight = 0.735
- Mode 1: omega = 112.0 rad/s, Q = 470.7, weight = 0.184
- Mode 2: omega = 129.4 rad/s, Q = 407.6, weight = 0.082

### 4.2 Multi-Mode Reflection

**Result**: multimode_factor = **0.99999** (negligible correction).

For Q >> 1 across all modes, each mode contributes negligible absorption.
The correction only becomes significant if Q drops to O(1), requiring
dissipation 10+ orders of magnitude above canon.

---

## 5. Numerical Results (30 M_sun, canon parameters)

| Model | r_amp | A_1/A_0 | Factor vs sharp |
|-------|-------|---------|-----------------|
| Sharp boundary (WP2B) | 0.9800 | 0.0369 | 1.000 |
| Single-mode interior (WP2C) | 0.9800 | 0.0368 | 1.000 |
| Graded transition | 0.9759 | 0.0367 | 0.996 |
| Multi-mode corrected | 0.9800 | 0.0368 | 1.000 |
| **WP2D combined** | **0.9759** | **0.0367** | **0.996** |

### Key Diagnostics

| Quantity | Value |
|----------|-------|
| lambda_probe / transition_width | 11.96 |
| Transition regime | **quasi_sharp** |
| Grading factor | 0.996 |
| Multi-mode factor | 1.000 |
| Combined factor | 0.996 |
| Echo channel status | **weakened_modestly** |
| Convergence (100 vs 500 layers) | 0.014% |

### Mass Dependence

| M/M_sun | r_sharp | r_graded | grading_factor |
|---------|---------|----------|----------------|
| 10 | 0.966 | 0.959 | 0.993 |
| 30 | 0.980 | 0.976 | 0.996 |
| 100 | 0.989 | 0.987 | 0.998 |
| 10^4 | 0.999 | 0.999 | 1.000 |
| 10^9 | 1.000 | 1.000 | 1.000 |

The correction decreases with mass: heavier BHs have even more quasi-sharp
transitions (larger r_s, same fractional transition width).

---

## 6. Echo Channel Status Determination

The graded transition reduces echo amplitude by **< 1%** compared to the
sharp-boundary estimate. This means:

- The **sharp-boundary impedance model is VALIDATED** as an excellent
  approximation for the echo channel
- The WP2C reactive_candidate classification is **UNCHANGED**
- The echo channel remains at ~3.7% of QNM amplitude (effectively
  unchanged from WP2B)
- The dominant remaining uncertainty is NOT the transition width — it is
  the Q classification (reactive vs dissipative) and the missing interior PDE

> **CONCLUSION**: The echo channel SURVIVES the transition-width stress test.
> The sharp-boundary impedance model is confirmed as a good approximation.
> The WP2 falsifier channel is mature enough to freeze as a CANDIDATE.

---

## 7. Missing Closures

1. Full wave equation on GRUT interior metric with graded boundary
2. Ab initio mode spectrum from metric perturbation theory
3. Transition zone scattering/decoherence effects
4. Mass-dependent Phi profile (currently calibrated to one mass benchmark)
5. Kerr generalization for rotating black holes
6. Nonlinear mode coupling at large perturbation amplitudes

---

## 8. Nonclaims

1. Graded-transition model is ZEROTH-ORDER — uses parameterized Phi(R)
   profile, not a wave-equation solution.
2. Recursive Airy computation assumes stratified medium — horizontal
   homogeneity in each layer.
3. Phi profile calibrated to Phase III-B benchmark at M = 1e30 kg;
   mass dependence of profile is untested.
4. Multi-mode spectrum is parameterized, not from perturbation theory.
5. Mode weights are assumed, not derived from overlap integrals.
6. Continuum modes are not modeled.
7. Phase coherence across transition is assumed.
8. All results CONDITIONAL on WP1 exterior assumption.
9. Kerr generalization not attempted.
10. No result is promoted to final canon.

---

## 9. Freeze Recommendation

WP2 (ringdown/echo falsifier channel) has been stress-tested through
four levels:
- **WP2A**: parameterized echo model (free reflection coefficient)
- **WP2B**: impedance-based reflection (sharp boundary)
- **WP2C**: interior wave analysis (reactive vs dissipative classification)
- **WP2D**: transition-width and multi-mode corrections

**Recommendation**: WP2 is **MATURE ENOUGH TO FREEZE** as a candidate
falsifier channel:
- The sharp-boundary model is confirmed (< 1% correction from grading)
- The reactive_candidate classification is stable across all corrections
- The multi-mode spectrum is negligible (Q >> 1 for all modes)
- The echo amplitude estimate remains ~3.7% of QNM (unchanged from WP2B)
- The next meaningful improvement requires the actual interior PDE

**Status for canon**: PREFERRED CONSTRAINED ESTIMATE (CANDIDATE)
