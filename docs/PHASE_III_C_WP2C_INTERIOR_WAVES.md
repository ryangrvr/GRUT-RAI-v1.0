# Phase III-C WP2C: Interior Wave-Equation Closure for the BDCC

> **SUPERSEDED** (v1.0): The proxy result in this document (Q ~ 515,
> reactive_candidate) has been superseded by the PDE closure (Q ~ 6–7.5,
> mixed_viscoelastic). See `PHASE_III_C_PDE_MEMO.md` for the leading
> result and `PHASE_III_FINAL_UPLOAD_STATE.md` for the final status.
> This document is retained as historical record of the zeroth-order
> proxy analysis.

**Date**: 2026-03-09
**Status**: SUPERSEDED — was REACTIVE CANDIDATE under zeroth-order viscoelastic model
**Predecessor**: WP2B Impedance Reflectivity (sharp-boundary approximation)
**Exterior assumption**: Schwarzschild-like (WP1 conditional)

---

## 1. The Question

WP2B established two bracketing models for R_surface:
- **Impedance model** (reactive BDCC): r_surface_amp > 0.96 for stellar-mass BHs
- **Boltzmann model** (dissipative BDCC): r_surface_amp ≈ 0

The distinguishing question is:

> **Does the BDCC behave primarily as a reactive medium, a dissipative
> medium, or a mixed viscoelastic medium for perturbations at the QNM
> frequency?**

WP2C addresses this by constructing a zeroth-order interior perturbation
model using the viscoelastic response framework.

**What WP2C does NOT assume:**
- It does NOT assume information saturation implies perfect elasticity
- It does NOT assume dissipation disappears at the endpoint
- It does NOT assume echoes exist or vanish
- It does NOT assume the BDCC is fully reflective or fully absorbing

Instead, it TESTS the competing response structures from solver parameters.

---

## 2. Viscoelastic Framing

The BDCC is treated as a viscoelastic medium with two response channels:

### 2a. Storage (Reactive) Channel

The stability eigenvalue d(a_net)/dR > 0 at R_eq provides a restoring
force. This elastic energy storage is characterized by the **storage
modulus proxy**:

```
G' ~ omega_core^2
```

where omega_core = sqrt(beta_Q * GM / R_eq^4) is the natural oscillation
frequency from the stability eigenvalue.

In GRUT language: G' comes from the fact that the quantum pressure barrier
a_Q and the memory-coupled gravitational drive create a stable equilibrium.
Perturbations around R_eq experience a restoring force proportional to
displacement — this IS the storage modulus.

### 2b. Loss (Dissipative) Channel

Two loss mechanisms are identified:

1. **Solver dissipation** (gamma_diss): phenomenological V-damping
2. **Memory-mediated damping** (gamma_memory): structural, from the
   finite response time of the memory kernel

The **loss modulus proxy** at the probing frequency is:

```
G'' ~ omega_probe * gamma_eff
```

In GRUT language: G'' comes from the fact that a fraction alpha_vac of the
restoring force is mediated through memory (M_drive). The memory kernel
acts as a low-pass filter — perturbations at frequencies above 1/tau_local
are not fully tracked, creating a phase lag that dissipates energy.

### 2c. The Key Diagnostic

The **loss tangent** characterizes the balance:

```
tan(delta) = G'' / G' = gamma_eff / omega_core = 1 / (2Q)
```

where Q = omega_core / (2 * gamma_eff) is the quality factor.

| Regime | Q | tan(delta) | Behavior |
|--------|---|------------|----------|
| Reactive (storage-dominated) | >> 10 | << 0.05 | High reflection |
| Mixed viscoelastic | 1–10 | 0.05–0.5 | Band-limited echoes |
| Dissipative (loss-dominated) | << 1 | >> 0.5 | Low reflection |

---

## 3. Candidate Interior Response Models

### Model A: Reactive (Storage-Dominated)

**Conditions**: Q >> 10, tan(delta) << 0.05
**Physics**: The BDCC stores elastic energy efficiently. Incoming
perturbations at QNM frequencies are reflected because the BDCC cannot
respond fast enough to absorb them (omega_QNM >> omega_core).
**Echo consequence**: r_surface_amp ~ r_impedance (WP2B estimate applies)
**Status**: This is what the zeroth-order model predicts at canon params.

### Model B: Dissipative (Loss-Dominated)

**Conditions**: Q << 1, tan(delta) >> 0.5
**Physics**: The BDCC absorbs incoming perturbation energy thermally.
This requires a physical mechanism that dissipates energy faster than
the elastic restoring force can store it.
**Echo consequence**: r_surface_amp ~ 0 (Boltzmann model applies)
**What would be needed**: gamma_eff >> omega_core. In the current solver,
this requires gamma_diss >> gamma_memory ~ alpha_vac * omega_core / 4.
For 30 M_sun this means gamma_diss >> ~85 rad/s — 17 orders of magnitude
above the canon value (1e-15).

### Model C: Mixed Viscoelastic

**Conditions**: 1 < Q < 10, 0.05 < tan(delta) < 0.5
**Physics**: Both storage and loss channels are active. The BDCC
partially reflects and partially absorbs, with the balance depending
on the probing frequency. At QNM frequencies (omega >> omega_core),
the response is still predominantly elastic, but with measurable loss.
**Echo consequence**: Echoes present but weaker than impedance model.
Band-limited: lower-frequency perturbations are more absorbed than
higher-frequency ones. Richer falsifier structure than simple yes/no.
**What would be needed**: gamma_eff within a factor of ~10 of omega_core.
This is the case if omega_core * tau_local ~ 1 and alpha_vac is order 1.

---

## 4. What Current Solver Quantities Proxy

| Physical quantity | GRUT solver proxy | Value (30 M_sun) |
|-------------------|-------------------|------------------|
| Storage modulus G' | omega_core^2 / (GM/R_eq^3) | beta_Q = 2 |
| Loss modulus G'' | omega_probe * gamma_eff / (GM/R_eq^3) | computed |
| Natural frequency | omega_core | ~102 rad/s |
| Effective damping | gamma_eff = gamma_diss + gamma_memory | ~0.099 rad/s |
| Memory damping | gamma_memory | ~0.099 rad/s |
| Solver damping | gamma_diss | 1e-15 rad/s |
| Quality factor | Q = omega_core / (2*gamma_eff) | ~516 |
| Loss tangent | tan(delta) = 1/(2Q) | ~0.001 |
| Frequency ratio | omega_QNM / omega_core | ~25 |

---

## 5. Sources of Damping

### 5a. Solver Dissipation (gamma_diss)

The collapse solver applies phenomenological damping: V *= exp(-gamma_diss * dt).
At the canon value gamma_diss = 1e-15 s^{-1}, this is negligible.

### 5b. Memory-Mediated Damping (gamma_memory)

This is the STRUCTURAL damping channel. The memory kernel responds at
rate 1/tau_local. At the BDCC:

```
tau_local = tau0 * t_dyn / (t_dyn + tau0) ≈ t_dyn  [since t_dyn << tau0]
```

The memory coupling contributes damping:

```
gamma_memory = alpha_vac * omega_core^2 * tau_local / (2 * (1 + (omega_core * tau_local)^2))
```

The behavior depends on omega_core * tau_local:
- omega_core * tau_local >> 1: gamma_memory → alpha_vac / (2*tau_local),
  Q → omega_core * tau_local / alpha_vac >> 1
- omega_core * tau_local << 1: gamma_memory → alpha_vac * omega_core^2 * tau_local / 2,
  Q → 1 / (alpha_vac * omega_core * tau_local) >> 1
- omega_core * tau_local ~ 1: gamma_memory ~ alpha_vac * omega_core / 4,
  Q → 2/alpha_vac ~ 6

**Key observation**: Q > 1 in ALL regimes of omega_core * tau_local.
The minimum Q occurs when omega_core * tau_local = 1, giving
Q_min ≈ 2/alpha_vac ≈ 6. This is above the mixed/reactive boundary
(Q > 1) but below the strong-reactive threshold (Q > 10).

### 5c. Potential Hidden Dissipation

The current model does NOT capture:
- Nonlinear mode coupling (perturbation energy cascading to smaller scales)
- Quantum pair production at the BDCC surface
- Transition-width absorption (graded impedance)
- Interior metric modification (imaginary part of effective potential)

Any of these could increase gamma_eff and lower Q, potentially changing
the classification from reactive to mixed or dissipative.

---

## 6. Numerical Results

### 6a. Canon Parameters (30 M_sun)

| Quantity | Value |
|----------|-------|
| omega_core | 102 rad/s |
| gamma_eff | 0.099 rad/s |
| gamma_memory | 0.099 rad/s |
| gamma_diss | 1e-15 rad/s |
| Q | 516 |
| tan(delta) | 0.00097 |
| G'/G'' ratio | ~1031 |
| r_interior_amp | 0.980 |
| r_impedance (WP2B) | 0.980 |
| Q-correction to r | < 0.01% |
| Classification | reactive_candidate |

### 6b. Mass Dependence

Q is mass-dependent through omega_core and tau_local. The benchmark
confirms Q >> 10 (reactive) for all tested masses (10 to 10^9 M_sun).

### 6c. Sensitivity Analysis

What gamma_diss would change the classification?
- Mixed (Q ~ 5): gamma_diss ~ gamma_memory ~ 10 rad/s (30 M_sun)
- Dissipative (Q ~ 0.5): gamma_diss ~ 100 rad/s (30 M_sun)
- Canon value: 1e-15 rad/s (17 orders below crossover)

---

## 7. Classification

Based on the zeroth-order viscoelastic model with canon parameters:

**CLASSIFICATION: reactive_candidate**

Justification:
- Q ≈ 516 >> 10 at 30 M_sun (deeply in the reactive regime)
- tan(delta) ≈ 0.001 << 0.05 (storage-dominated)
- Memory-mediated damping is the dominant loss channel (structural)
- Solver dissipation is negligible (17+ orders below memory damping)
- Q > 10 for ALL astrophysical masses tested (10 to 10^9 M_sun)
- No physical mechanism identified for gamma_eff >> gamma_memory

**What this means for the echo channel**:
- The impedance model reflection estimates (WP2B) apply with negligible
  Q-dependent correction (< 0.01% for canon parameters)
- The echo channel remains PROMISING under this model
- The Boltzmann model would require Q << 1, which needs a physical
  mechanism for gamma_eff >> 100 rad/s — not present in current solver

**What could change this**:
- A hidden dissipation mechanism providing gamma_diss >> 10 rad/s
  would push the BDCC into the mixed viscoelastic regime
- gamma_diss >> 100 rad/s would make it dissipative
- Neither is present in the current solver, but cannot be ruled out

---

## 8. Missing Closures

The following closures are needed for a rigorous determination:

1. **Covariant GRUT interior metric**: Needed for the proper wave equation
   on the modified background. The Newtonian-gauge ODE model does not
   capture relativistic wave propagation effects.

2. **Interior effective potential**: V_int(r) from metric perturbation theory
   determines whether the interior has an absorptive (imaginary) component.

3. **Transition-width corrections**: The Phase III-B transition has finite
   width (~0.7 r_s). A graded impedance profile could change the effective
   Q at high frequencies.

4. **Nonlinear mode coupling**: Whether perturbation energy cascades to
   dissipative scales within the BDCC is unknown.

5. **Multi-mode interior spectrum**: The single-mode oscillator model
   may miss features of the actual continuous interior response.

6. **Quantum dissipation channels**: Whether Hawking-like processes at
   or near the BDCC provide additional loss channels.

---

## 9. Explicit Nonclaims

1. This does NOT solve the wave equation on the GRUT interior metric.
   The model is a ZEROTH-ORDER viscoelastic approximation.

2. Does NOT assume information saturation implies perfect elasticity.
   The storage-vs-loss balance is tested from solver parameters.

3. Does NOT assume dissipation disappears at the endpoint. Memory-mediated
   damping is the dominant loss channel and is explicitly computed.

4. The reactive classification is a CANDIDATE assessment, not a proven result.
   Hidden dissipation mechanisms could change the classification.

5. The classification thresholds (Q > 10 reactive, 1 < Q < 10 mixed,
   Q < 1 dissipative) are ORDER OF MAGNITUDE conventions.

6. The interior reflection estimate r_interior_amp is a zeroth-order
   approximation that goes beyond sharp-boundary but is not a
   wave-equation solution.

7. All results are CONDITIONAL on the WP1 exterior assumption
   (Schwarzschild-like, moderate confidence).

8. The single-mode oscillator model may miss features of the actual
   continuous interior spectrum.

9. Neither echoes nor their absence is predicted. The module tests
   which model (reactive/dissipative/mixed) is CONSISTENT with
   current solver structure.

---

## 10. Summary

WP2C constructs the first interior perturbation model for the BDCC
using the viscoelastic response framework:

- **Storage modulus** (G'): from stability eigenvalue (restoring force)
- **Loss modulus** (G''): from memory-mediated damping (dominant) + solver dissipation
- **Key diagnostic**: Q = omega_core / (2*gamma_eff), tan(delta) = 1/(2Q)

**Result at canon parameters**: Q ≈ 516, tan(delta) ≈ 0.001

| Model | Q regime | r_surface_amp | Echo viability |
|-------|----------|---------------|----------------|
| Reactive (canon) | 516 | 0.980 | PROMISING |
| Mixed (hypothetical) | 1–10 | reduced | UNCERTAIN |
| Dissipative (hypothetical) | << 1 | ~0 | NOT viable |

The zeroth-order model favors the **reactive candidate** because:
- Memory-mediated damping is the only structural loss channel
- It gives Q >> 10 for all astrophysical masses
- Pushing Q below 10 requires an unidentified dissipation mechanism

The next missing closure is the covariant interior wave equation,
which would determine whether hidden dissipation channels (nonlinear
coupling, quantum effects, transition-width absorption) modify Q.

**Status**: REACTIVE CANDIDATE — zeroth-order viscoelastic model.
The covariant interior wave equation remains the key open closure.
