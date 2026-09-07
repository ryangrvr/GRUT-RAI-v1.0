# Q2 EXECUTION PACKAGE — ready-to-run; execution NOT authorized

> **2026-09-07 · SETUP COMPLETE, NOTHING RUN.** Everything methodological is frozen:
> equations, parameters, seeds, thresholds, observables, controls, decision rules, analysis.
> The next prompt authorizes execution and needs to choose nothing.
> Preregistration: `program/gates/Q2_STOCHASTIC_EXECUTION_PREREG.md` (binding).

## Time-coordinate semantics (read before interpreting any span)

| estimator | coordinate | phase | range | e-folds at A / B |
|---|---|---|---|---|
| **O1a autocorrelation (PRIMARY)** | **LAG** | stationary [300, 600] | available τ ≤ 200; **effective fitted τ ≤ 90 (A) / 160 (B)** | available 6.67 / 1.77; **EFFECTIVE FITTED 3.00 / 1.42** ← the operative figures |
| O1b decay fit (cross-check) | **ABSOLUTE TIME** | transient (before burn-in 300) | [5,40] [5,65] [30,70] | 1.17·2.00·1.33 / 0.31·0.53·0.35 |

`burn_in_time = 300.0` (= 0.5 × t_max). The O1b windows lie before it **by design**:
relaxation-from-initial-condition cannot be measured after the system has relaxed. The two
estimators are never compared span-to-span, and the auditor verifies that the code's
interpretation equals this table.

## Scope fence (read first)

This package evolves the **scalar** Starobinsky–Yokoyama channel. It does **not** compute
O2 (the interacting **graviton** zero-mode) and **cannot discharge reopening key #1** of the
program freeze. The scalar→graviton gap is declared UNRESOLVED (prereg §1.1, U1).

## The exact command to authorize

```bash
cd "/Users/mpg/Desktop/GRUT ResponsiveAI/calc" && python3 q2_run.py --config q2_config.json
```

`q2_run.py` accepts **only** `--config` and refuses any other argument — nothing is tunable
at run time. It runs the instrument, the control battery, and the independent auditor in
order, and exits with the AUDITOR's code (never a verdict about the physics).

Runtime estimate (from a NON-EVIDENTIARY timing probe, ~1.0M trajectory-steps/sec measured
on this machine, pure stdlib): **primary ≈ 20 min** (5 seeds × 240M trajectory-steps:
n_traj = 4000 × t_max = 600), **controls ≈ 36 min**, **audit < 1 s** — **≈ 56 min total**,
single-threaded.

## Files in the package

| file | role | state |
|---|---|---|
| `calc/q2_stochastic_sy.py` | instrument: SY Langevin integrator, autocorrelation + decay-fit observables, dual analytic targets | frozen |
| `calc/q2_controls.py` | control battery Q2-C1…C10 | frozen |
| `calc/q2_run.py` | **the frozen entrypoint** — one command, no choices | frozen |
| `calc/q2_audit.py` | **independent** auditor (imports neither instrument module); carries the non-circularity firewall | frozen |
| `calc/q2_config.json` | all parameters, classified; SHA-256 pinned into outputs | frozen |
| `program/gates/Q2_STOCHASTIC_EXECUTION_PREREG.md` | the preregistration | frozen |

## Files execution WILL create

`calc/RESULTS_q2_stochastic_sy.json` · `calc/RESULTS_q2_controls.json` ·
`calc/RESULTS_q2_audit.json`. Nothing else is written; no committed file is modified.

## Preflight checks already run (cheap, non-evidentiary)

- Python syntax parse of all three modules — OK.
- Config loads; all required physical/numerical/control keys present; no defaults exist — OK.
- Independent pre-execution audit (`q2_audit.py`) — **AUDIT_OK, 0 fail, 0 warn**, including:
  noise rule frozen to Gibbons–Hawking H/2π; primary run starts bare-massless; λ = 0.01
  reproduces the record's m_eff² = 0.1H²; fit window strictly inside the horizon; instrument
  emits no PASS/FAIL label; machine-label set excludes PASS/FAIL.
- Timing probe (200 trajectories × 2 Hubble times) — used ONLY for the runtime estimate,
  **NON-EVIDENTIARY**, and no physics quantity was read from it.
- End-to-end path smoke test (100 trajectories × 8 Hubble times) exercising the
  autocorrelation estimator, the multi-window decay fit, and the stationary-variance
  routine — **NON-EVIDENTIARY**: 8 Hubble times is far short of stationarity and no value
  produced by it is a Q2 result or was used to infer one.
- Independent SNR re-derivation inside `q2_audit.py`: latest fit-window end sits at
  SNR 5.3 (others 6.3, 14.5) against the required floor of 5.
- **Estimator calibration (C11) run at setup**: planted Λ recovered with bias −2.6% / +0.1%
  and scatter 9.8% / 4.4% at targets A / B — inside the (measured, not guessed) tolerances.
- **Primary-estimator control coverage verified non-definitionally**: the auditor checks the
  controls actually *call* `autocorrelation_rate`, after an audit found every control had
  been routing through the demoted cross-check only.
- **Estimator-validity audit (`calc/q2_estimator_validity.py`, deterministic, NON-EVIDENTIARY)**:
  an independent Fokker–Planck spectral solve — validated against the exact OU spectrum to
  0.01% — gives Λ₁ = 0.008892 (= 0.08892√λ H, agreeing with the preregistered 0.0885 to
  0.5%) and ⟨φ²⟩_eq = 1.317651 vs analytic 1.317645. C(τ) is 98.44% single-exponential; the
  frozen fit rule applied to the exact noise-free C(τ) returns 0.008951, a **+0.66%**
  finite-lag bias — 15× below the statistical scatter and 566× below the A-vs-B separation.
  **O1a is therefore a valid Λ₁ estimator for the nonlinear operator, not merely for OU.**
- **Non-circularity firewall — all checks AUDIT_OK**: no mass injected (m²_bare = 0); live
  physical-input set exactly {H, m²=0, λ, φ₀, noise-rule}; timestep resolves both targets
  (dt·k = 3.3e-4, 8.9e-5); primary range spans ≥1 e-fold at both targets (6.7, 1.77);
  burn-in = 2.66 slow relaxation times; m²_eff = 0.1H² is a target, never an input;
  autocorrelation is connected; neither target value appears in the integrator body.
- Entrypoint argument refusal verified (`--tune-something` → refused).

## What the run may and may not produce

Machine labels only: `OBSERVED / NOT_OBSERVED / INCONCLUSIVE / INVALID_RUN / CONVERGED /
NONCONVERGED`. The instrument emits no scientific PASS/FAIL, no "confirmed", no "prediction".
Adjudication against the frozen decision tree (prereg §18) is the audit layer's and the
owner's, after execution.

## Repository state at freeze

Branch `master` → `origin/v4`. Q1 untouched (`20fd3d4`, GATED, REFUSE). Register untouched
(74 nodes, sha256 prefix `beaeb84e8a6f8468`). See the commit for this package for the exact
hash manifest.

## SHA-256 manifest — FREEZE POINT

**The freeze point is the git commit recorded below, not this table alone.** Any parameter
change after that commit is a NEW preregistration, not an edit.

| file | sha256 |
|---|---|
| `calc/q2_run.py` | `8cf91b8743eaad56d346988dac40a6fa1679aaada8451dd6a4b347480d4b329b` |
| `calc/q2_stochastic_sy.py` | `3cda78997eaa5314f043594e6ce554e2734812f392fdd8882a326a3c1b6ad2b9` |
| `calc/q2_controls.py` | `edbce973040f6306c5e4ae36881abb68868199df5d5e170930fc57ffb1db1169` |
| `calc/q2_audit.py` | `800f418f63af54e92de3eadd3336946d68b18099a3a15509fd73832b1e040cd8` |
| `calc/q2_estimator_validity.py` | `a7d042bdb9be13e8e55184ff598a895c0ed9e3c1c7d01f3f7b361774f11ed6da` |
| `calc/q2_config.json` | `4aac62a44ac0ad65afe574d6e05eee5c5f3484e17e641aa680d08e5ae91ff4dc` |
| `program/gates/Q2_STOCHASTIC_EXECUTION_PREREG.md` | `47e71a1189b9faad7ddc2fb7678e580cc4e8853dbd03f7af669a458d21374b15` |
