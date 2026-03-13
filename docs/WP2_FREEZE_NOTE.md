# WP2 Freeze Note — Ringdown/Echo Candidate Falsifier Channel

**DATE**: 2026-03-10 (initial freeze), **REVISED**: 2026-03-11 (PDE closure + covariant closure + field equation framework)
**STATUS**: FROZEN — PDE-informed, covariant-confirmed constrained estimate (candidate falsifier channel, weakened but surviving)
**CONDITIONAL ON**: WP1 Schwarzschild-like exterior assumption

---

## 1. What Was Tested

WP2 was stress-tested through four proxy levels (WP2A-D), then the interior PDE closure was derived (Phase III-C):

| Level | What | Result |
|-------|------|--------|
| WP2A | Parameterized echo model (free R_surface) | Echo delay ~0.52 ms (30 M_sun), amplitude up to ~3% of QNM |
| WP2B | Impedance-based reflection (sharp boundary) | eta << 1, r_amp ~ 0.98 (30 M_sun, **SUPERSEDED by PDE**) |
| WP2C | Interior wave analysis (viscoelastic proxy) | Q = 515.6, reactive_candidate (**SUPERSEDED — eigenfrequency error**) |
| WP2D | Transition-width + multi-mode corrections | Grading factor 0.996, multi-mode negligible, sharp boundary VALIDATED |
| PDE | Interior PDE from ODE linearisation | Q = 6-7.5, mixed_viscoelastic, r_PDE ≈ 0.30 (**LEADING**) |
| Covariant | Effective metric ansatz closure | CONFIRMS PDE: ω₀τ=1, Q~6.5, r_cov ≈ 0.37 (±21% of PDE) |
| Field Eqs | Covariant field equation framework | Auxiliary scalar (preferred); algebraic tensor (insufficient); nonlocal (parent) |

---

## 2. What Changed: PDE Closure (Phase III-C)

The PDE closure identified an eigenfrequency error in the WP2C proxy:

- **Proxy**: omega_core² = beta_Q × GM / R_eq⁴ (extra 1/R_eq factor — **WRONG**)
- **PDE**: omega_0² = beta_Q × GM / R_eq³ (**CORRECT** — from linearisation of force balance)
- **Error factor**: sqrt(R_eq) ~ 172 at 30 M_sun

This shifts omega × tau from 0.006 (low-damping regime) to 1.0 (peak-damping regime), changing:
- Q from ~515 (reactive) → ~6-7.5 (mixed viscoelastic)
- r_amp from ~0.98 → ~0.30
- Echo amplitude from ~3.7% → ~1.1%

The echo channel is **weakened but NOT collapsed**.

---

## 3. Structural Identity: ω₀ × τ_local = 1

The PDE derivation reveals that ω₀ × τ_local = 1.0 exactly, for all masses.

**What this means**: The oscillation timescale and local memory-relaxation timescale are locked together. The BDCC always sits at the peak of the memory damping function.

**Scope**: This is an exact identity within the current PDE closure framework (Tier-0 local tau, constrained endpoint law, linearised ODE).

**What this does NOT mean**:
- Not a universal law independent of the closure used
- Not final canon beyond its current framework
- Not proof of bandwidth saturation in an absolute sense
- Not guaranteed to survive under alternative tau closures

**Consequence**: Universal Q = beta_Q / alpha_vac = 6.0, mass-independent. This naturally favors a mixed viscoelastic regime.

---

## 4. Status Classification (Revised)

### LOCKED
- Phi-profile as zeroth-order graded transition model
- Transition-width corrections small in the benchmark regime (< 1%)
- Multi-mode corrections negligible under canon dissipation
- WP2 mature enough to freeze as candidate falsifier channel
- PDE structural identity ω₀ × τ = 1 (exact within current closure)
- Universal Q_PDE = beta_Q / alpha_vac = 6.0

### LEADING CLASSIFICATION (PDE-informed)
- **mixed_viscoelastic** — best current candidate classification
- Q ≈ 6-7.5 (mass-independent)
- r_PDE ≈ 0.30 (30 M_sun)
- Echo amplitude ≈ 1.1% of QNM signal
- Schwarzschild-like exterior assumption (WP1 conditional)

### SUPERSEDED PROXY RESULT (historical)
- reactive_candidate (Q ≈ 515) — eigenfrequency error identified
- r_proxy ≈ 0.98 — based on incorrect omega_core
- Echo amplitude ≈ 3.7% — overestimate
- Useful historical step, NOT the current leading estimate

### ACTIVE / RESEARCH TARGET
- Covariant interior wave equation (beyond ODE linearisation)
- Ab initio mode spectrum from metric perturbation theory
- Independent verification of ω₀ × τ = 1 via covariant treatment
- Mass-dependence of the Phi profile
- Kerr generalization for rotating black holes
- Nonlinear mode coupling at large perturbation amplitudes
- Detector inference pipeline

---

## 5. What This Freeze Does NOT Claim

1. Echoes are NOT predicted to exist. The module computes what they WOULD look like under assumptions.
2. Echo time delay is an ORDER OF MAGNITUDE estimate.
3. PDE closure is approximate — linearised, non-covariant, single-shell tau_eff.
4. Boltzmann model (r_amp ~ 0) remains viable if the BDCC is dissipative.
5. Pre-PDE proxy result (Q ~ 515, r ~ 0.98, echo ~ 3.7%) is SUPERSEDED — do not cite as current.
6. Structural identity ω₀ × τ = 1 is exact only within the current closure framework.
7. mixed_viscoelastic is the best current candidate, NOT the final answer.
8. All results are CONDITIONAL on the WP1 exterior assessment.
9. Kerr generalization is not attempted.
10. No result is promoted to final canon.

---

## 6. Key Numbers (30 M_sun, canon parameters)

### Leading PDE-Informed Estimate
| Quantity | Value |
|----------|-------|
| Echo time delay | ~0.52 ms |
| r_PDE_amp | 0.303 |
| A_1/A_0 (echo fraction) | ~1.1% |
| Quality factor Q_PDE | 7.46 |
| gamma_PDE | 1,465 rad/s |
| omega_eff | 18,987 rad/s |
| ω₀ × τ | 1.0 (exact) |
| Response class | mixed_viscoelastic |

### Superseded Proxy Result (historical)
| Quantity | Value | Status |
|----------|-------|--------|
| r_surface_amp (proxy) | 0.980 | SUPERSEDED |
| A_1/A_0 (proxy echo) | ~3.7% | SUPERSEDED |
| Quality factor Q (proxy) | 515.6 | SUPERSEDED |
| Loss tangent (proxy) | 0.001 | SUPERSEDED |
| Grading factor (WP2D) | 0.996 | VALID (unchanged) |
| lambda / transition_width | 11.96 | VALID (unchanged) |

---

## 7. Files

| File | Role |
|------|------|
| `grut/interior_covariant.py` | **NEW** — Covariant interior module (effective metric ansatz, metric-corrected impedance) |
| `grut/interior_pde.py` | Interior PDE module (dispersion relation, mode solver, response classifier) |
| `grut/ringdown.py` | Echo channel: parameterized + impedance + graded + PDE + covariant models |
| `grut/interior_waves.py` | Interior wave analysis (WP2C proxy — SUPERSEDED, retained as baseline) |
| `grut/exterior_matching.py` | WP1 exterior matching (Schwarzschild-like conditional) |
| `docs/PHASE_III_C_PDE_MEMO.md` | PDE derivation memo (Phase III-C) |
| `docs/PHASE_III_C_COVARIANT_CLOSURE.md` | Covariant closure derivation memo |
| `tests/test_collapse.py` | Tests (WP2A-D + PDE + WP3 + 16 covariant tests) |
| `benchmark_phase3c_pde.py` | PDE benchmark (37/37 CLEAN) |
| `benchmark_phase3c_covariant.py` | **NEW** — Covariant closure benchmark (93/93 CLEAN) |
| `benchmark_phase3c_wp2_echo.py` | WP2A-C benchmark |
| `benchmark_phase3c_wp2d_transition.py` | WP2D benchmark |
| `docs/PHASE_III_C_WP2B_REFLECTIVITY.md` | WP2B derivation |
| `docs/PHASE_III_C_WP2C_INTERIOR_WAVE.md` | WP2C derivation |
| `docs/PHASE_III_C_WP2D_TRANSITION_WIDTH.md` | WP2D derivation |
| `grut/field_equations.py` | **NEW** — Covariant field equation module (3 candidates, reductions, Bianchi) |
| `docs/PHASE_III_FINAL_FIELD_EQUATIONS.md` | **NEW** — Field equation theory memo (Sections A-I) |
| `tests/test_field_equations.py` | **NEW** — Field equation tests (~22 tests) |
| `benchmark_phase3_final_field_eq.py` | **NEW** — Field equation benchmark |
| `canon/grut_canon_v0.3.json` | Canon: v0.3.6 with field equation section |
| `api/main.py` | GRUTipedia: edition 8, field-equations tag |

---

## 8. Repository Health

Full repository test suite: **354 passed, 3 skipped, 0 failed.**

All Phase III tests green, including 21 new PDE tests.
