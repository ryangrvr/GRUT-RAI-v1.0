# Q2 EXECUTION PACKAGE — ready-to-run; execution NOT authorized

> **2026-09-07 · SETUP COMPLETE, NOTHING RUN.** Everything methodological is frozen:
> equations, parameters, seeds, thresholds, observables, controls, decision rules, analysis.
> The next prompt authorizes execution and needs to choose nothing.
> Preregistration: `program/gates/Q2_STOCHASTIC_EXECUTION_PREREG.md` (binding).

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

## SHA-256 manifest (frozen at setup, after the design-time repairs of prereg §2.3)

| file | sha256 |
|---|---|
| `calc/q2_run.py` | `686375a3dc7da88b8fc780b49506317c40a7c7b8e93bfc1a5ec5ac0075148733` |
| `calc/q2_stochastic_sy.py` | `36e10c8f0e6d09b14b6a9b20239c2726873a5c9e8b9a7ad08a99a5d64ce9ee88` |
| `calc/q2_controls.py` | `9af6c3b5cbf53de99a54bd47b4a6189d819fafb8a049f2f8e4d0128739afbc55` |
| `calc/q2_audit.py` | `9ebd0b8bd446834cfe945fc29e03600057f80b95b290a3382d303af3cd244142` |
| `calc/q2_config.json` | `5e66be4914aa28c11879d98d85f06f8dfe5985cfc106ae3004aada3ce2134c9b` |
| `program/gates/Q2_STOCHASTIC_EXECUTION_PREREG.md` | `8cc89f061629e95cb9d6fb21681f8e99b04aae780e62e8feb4edcb149edcd7a1` |
