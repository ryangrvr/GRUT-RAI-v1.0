# Q2 — STOCHASTIC / KMS DYNAMICS: EXECUTION PREREGISTRATION

> **2026-09-07 · SETUP ONLY — FROZEN BEFORE EXECUTION · nothing has been run.** Reality
> Program investigation Q2 (`program/REALITY_PROGRAM.md`, `program/QUESTION_LEDGER.md`).
> Q1 is untouched (gate committed `20fd3d4`, status GATED, routing REFUSE). No corpus,
> register, closed gate, or published claim status is modified by this document.
> **Every value below is fixed now and may not be changed after any result is inspected.**

## 1 · The question (reconstructed, then frozen)

> **Does the already-declared stochastic Starobinsky–Yokoyama (SY) dynamics, started from a
> bare massless field, generate a finite relaxation rate — and does it reproduce the
> record's own referent value m_eff² = 0.1H² → rate = m_eff²/(3H) — under controls that can
> distinguish generated dynamics from initialization, discretization, noise-normalization,
> ensemble-size, and analysis artifacts?**

**What this question is NOT** (each explicitly disclaimed): not a claim that GRUT predicts a
cosmological state; not a proof of emergence, self-organization, observation, or a ToE; not
a computation of O2; not evidence for or against GRUT until execution, control comparison,
convergence, provenance audit, and owner adjudication have all occurred.

### 1.1 · THE SCOPE FENCE — this is not O2

`GRUT_PROGRAM_FREEZE.md` §5 reopening key #1 is **the interacting GRAVITON zero-mode**. This
instrument evolves a **self-interacting SCALAR** in de Sitter — the SY channel the record
itself cites when it says "any perturbation lifts it" (`RAI_GORILLA_T1.md` §XVI-N;
`books/BOOK_V…` §V.8). **The scalar→graviton gap is UNRESOLVED and is not bridged here.**
Consequently: *no outcome of this run can discharge reopening key #1, and no outcome may be
reported as "O2 computed."* What the run CAN do is establish whether the record's own cited
lifting channel behaves as the record assumes when actually evolved under controls.

## 2 · Record reconstruction (traced to source, not to filenames)

| field | source artifact | exact content | record status | inherit? | must be fixed by this prereg? | new structure if used? |
|---|---|---|---|---|---|---|
| Langevin equation dφ/dt = −V′(φ)/(3H) + (H/2π)η | `calc/two_scale_desitter.py:16` (committed) | overdamped stochastic-inflation equation | RECOVERED (standard SY/stochastic inflation, borrowed) | YES, verbatim | no | no |
| noise amplitude H/2π (Gibbons–Hawking) | same, docstring + `D = H²/(8π²)` | diffusion D = ½(H/2π)² | RECOVERED (horizon-forced; the record's "not a patch" clause) | YES | no | no |
| OU moment closure, rate k = m²/(3H) | same, `rk4_moments`, `k = m*m/(3.0*H)` | free-field relaxation rate | DERIVED (exact for V = ½m²φ²) | YES | no | no |
| stationary variance 3H⁴/(8π²m²) | same, `var_eq_pred` | free-field equilibrium | DERIVED | YES | no | no |
| SY dynamical mass m²_eff ∼ √λ H² | `calc/RESULTS_conformalon.md:26` (cites SY 1994; Beneke–Moch; Rajaraman; Serreau) | interacting IR mass generation | RECOVERED (literature; "workflow-verifying" in `two_scale_desitter.py:87`) | YES as the *rule* | **YES — λ must be fixed** | no |
| **λ = 0.01 ⇒ m_eff² = 0.1H²** | derived here from the two rows above | √0.01 = 0.1 | STRUCTURAL_SELECTION (chosen to hit the record's own referent) | — | **YES, fixed now** | no (a value of an existing parameter) |
| the "lift rate ≈ 0.034H at m_eff² = 0.1H²" | `GRUT_PROGRAM_FREEZE.md:126`; `RAI_GORILLA_T1.md:185`; Books II/V/X | the reopening-key referent | **see §2.1 — arithmetic discrepancy found** | as a *comparison target only* | **YES** | no |
| exact-dS zero Δ₋ = 0 | `GRUT_PROGRAM_FREEZE.md`, `RAI_GORILLA_T1.md` §XVI-N | the unlifted zero mode; "the whole adverse complex flows from one exact zero" | DERIVED (free-level, exact dS) | as the **null-control referent** (Q2-C3) | no | no |
| SY equilibrium P_eq ∝ exp(−8π²V/(3H⁴)) | standard SY; recomputed here by quadrature | stationary distribution | RECOVERED | YES | no | no |
| KMS/FDT condition | `provenance/claims.json` `rung2_kms_gate` | N locked to Im χ by coth; T_dS = H/2π forced | ASSUMPTION (borrowed, hard admission gate) | **NOT directly applicable** — see §4 | no | would be, if imposed as an extra constraint |
| N1–N10 negative-control standard | `RAI_GORILLA_T1.md:32–41` | **only N4 and N5 are defined in the committed record** | N4/N5 DERIVED; **N1–N3, N6–N10: UNRESOLVED — CONTROL DEFINITION REQUIRED** | N4/N5 roles only | yes — see §10 | inventing definitions would be |
| numerical parameters (dt, t_max, n_traj, seeds, windows) | none in the record | — | **DESIGN DECISION** | no | **YES, all frozen in §5–§9** | no (computational only) |

### 2.1 · The 0.034H figure — reconstruction finding, reported straight

Tracing the reopening-key referent to source: the SY overdamped rate is k = m²/(3H), so at
m_eff² = 0.1H² the value is **0.1/3 = 0.03333H**, which rounds to 0.033H, not 0.034H. The
record quotes "≈ 0.034H" in five committed places. Two possibilities are visible and **this
prereg does not adjudicate between them**: (i) loose rounding of 0.0333; (ii) a transcription
collision with an *unrelated* 0.034 in the record — `AGENT_COORDINATION.md:107` reports the
worldline reduction's S(ω = 0.1) = 0.03393 → 0.034116, a different quantity in a different
calculation. **Frozen consequence:** the comparison target for this run is the *analytic
formula* m_eff²/(3H) = **0.03333H**, computed inside the instrument, not the quoted 0.034H.
Decision-tree branches I/J are evaluated against the formula. The discrepancy is recorded
for the owner as a possible documentation defect in the record; **no committed file is
edited by this setup pass.**

### 2.2 · TWO comparison targets, both preregistered (design-time finding)

A pre-execution analysis of this package found that the record's referent rate and the
*correct* rate for this equation need not coincide, and that only preregistering both
prevents a post-hoc choice of target:

- **Target A = m_eff²/(3H) = 0.03333H** — the record's own construction: its scaling rule
  m²_eff ∼ √λ H² fed into the free-field OU rate. This is the reopening-key referent.
- **Target B = Λ₁ = 0.0885 √λ H = 0.00885H** — the Starobinsky–Yokoyama Fokker–Planck first
  eigenvalue for λφ⁴/4, i.e. the actual spectral gap of the very equation being integrated.
  The 0.0885 coefficient is exactly the O(1) constant the record does **not** supply (U4).

**They differ by 3.8×.** Both are emitted by the instrument before any measurement, and the
decision tree branches on both (§18, I-a / I-b / J). Neither may be selected after seeing
the result. *This is the "check what your check is compared against" rule applied to the
target itself.*

**FORMAL MODEL-STATUS ADJUDICATION (required before execution).** The three possibilities
were examined and the answer is determinate:

- *Are they two different approximations to the same already-defined dynamics?* — **Partly:
  yes as to the dynamics, no as to their standing.** There is exactly ONE dynamics here (the
  SY Langevin equation with V = λφ⁴/4). Both numbers are estimates of the SAME observable of
  it: the relaxation rate = the Fokker–Planck spectral gap.
- *Is B a correction/eigenvalue result that replaces the OU estimate?* — **Yes, as a
  prediction OF THAT EQUATION.** Target A is a two-step composition: the record's scaling
  rule m²_eff ∼ √λH², inserted into the *free-field* OU formula m²/(3H). Step two is exact
  only for a quadratic potential; for λφ⁴ it is a Gaussian/effective-mass approximation.
  Target B is the exact spectral gap of the equation actually being integrated. **As physics
  for this equation, B supersedes A.**
- *Are they genuinely different models or observables?* — **No.** Same model, same
  observable, different levels of approximation.

**Preregistered adjudication rule, fixed now:** the measured rate is compared to both. A
measurement consistent with B and not A is a **documentation finding about the record** —
its own rule, composed with a free-field formula, overstates the rate of its own cited
channel by ≈3.8× — and is **not** a result about GRUT or about gravity. A measurement
consistent with A and not B would instead indict either the literature coefficient 0.0885 or
this implementation, and is adjudicated against control **C2** (the exact λ = 0 OU limit),
which is the correctness anchor. A measurement consistent with neither is branch J.
**Because B supersedes A as physics, "the run reproduced 0.0333H" may never be reported as a
vindication of the record's number without this paragraph attached.**

**GUARD — "B supersedes A for this equation" is NOT "B is the expected GRUT answer."** The
licensed hierarchy is: *the equation* → *its spectral gap B*. Target **A is retained only as
a record-consistency diagnostic.** Neither is a GRUT prediction: the equation is the SY
scalar channel (§1.1), not gravity, and λ is unresolved (U2). Reproducing B would mean the
implementation agrees with the registered spectral-gap calculation of the equation it
integrates — an instrument-and-literature agreement, nothing more. **This run must not
become a hunt for 0.00885.** Preregistered outcome meanings:

| outcome | what it means (and does not) |
|---|---|
| B reproduced | the nonlinear instrument is consistent with its registered spectral-gap result. NOT evidence for GRUT, NOT a prediction, NOT O2 |
| A reproduced, B not | an implementation-vs-literature discrepancy to adjudicate against control C2 (the exact λ = 0 OU limit); until adjudicated, no physics reading |
| neither | a discrepancy requiring investigation; report both gaps and the measured value |
| neither, with numerical pathology | INVALID_RUN / NONCONVERGED — no physics reading at all |
| either value reproduced *in a control* that should not exhibit it | **not** evidence for the intended mechanism; it indicts the instrument (C3 in particular voids the primary) |

### 2.3 · Signal-to-noise defect found and repaired BEFORE execution

The original configuration (n_traj = 4000, single fit window [5, 120]) was defective: the
ensemble-mean noise floor σ_φ/√N = 0.0182 equals the signal e^{−0.0333·120} = 0.0183
**exactly at the window end**, so the tail of the only fit window was pure statistical noise
and ln|mean| of noise biases the slope. Repairs, all made at design time with no result in
existence: (i) **primary estimator changed** to the stationary **autocorrelation** route
C(τ) ∼ e^{−Λ₁τ}, which has no SNR cliff because it is a stationary average; (ii) the
ensemble-mean decay fit is demoted to a cross-check and run over **three** preregistered
windows [5,40], [5,65], [30,70] — window-dependence is itself a control, since a genuine
exponential gives one rate across all three and a power law does not; (iii) n_traj raised
(iv) the integration horizon was extended t_max 300 → 600 so that the burn-in (50% = 300
Hubble times) exceeds **2.66 relaxation times of the SLOWER candidate** — the autocorrelation
route requires genuine stationarity for both candidates, not only the faster one; (v) a
**connected (mean-subtracted)** autocorrelation replaced the raw second moment, because an
incompletely relaxed ensemble has ⟨φ⟩ ≠ 0 and the raw moment then carries a non-decaying
⟨φ⟩² pedestal that biases the fitted rate **downward, toward the slower target** — a bias
that would have manufactured agreement with B.

**Ex ante justification, stated explicitly (§2.3 is a design record, not a result record):**
the windows were selected from exactly three inputs, all available before any execution —
(1) the analytic ensemble-mean noise floor σ_φ/√N, with σ_φ from the SY closed-form
stationary variance; (2) the two already-identified candidate rates of §2.2; (3) the
**predetermined detectability criterion SNR ≥ 5 at every window end**, evaluated against the
faster candidate as the binding case. *No stochastic result existed when these were fixed,
no preliminary run informed them, and none may reopen them.* The independent auditor
**re-derives** the noise floor, the SNR, the e-folds spanned by every analysis range at both
targets, the timestep resolution dt·k, and the burn-in in slow-relaxation-times, and fails
the run if any falls below its frozen threshold.

### 2.4 · Estimator calibration and the tolerances (pre-execution audit findings)

A pre-execution audit found **two blocking defects that no amount of prose could have
caught**, both now repaired:

**(a) The PRIMARY estimator had zero control coverage.** Every control routed through the
*demoted* cross-check (O1b); `autocorrelation_rate` was called only in the primary run, and
the auditor's only check on it was definitional (`ac_traj > 0`). That is precisely the
program's own standing lesson — *a gate whose identity is definitional proves nothing* — and
it was not hypothetical: the auditor demonstrated an earlier configuration in which the
estimator was **inoperable** (one usable origin ⇒ every seed returns `None` ⇒ INVALID_RUN)
while the definitional check still reported AUDIT_OK. Roughly an hour of compute would have
produced a void primary with nothing catching it. **Repair:** C3, C5, C8 and C10 now report
the primary estimator's result alongside O1b; C8 plants a known exact spectral gap (OU, where
Λ = m²/3H exactly) and requires the *primary route* to recover it inside the real SDE
pipeline; a new **C11** feeds the primary estimator synthetic AR(1) data with an exactly
known Λ in production geometry; and the auditor now verifies non-definitionally that the
controls actually **call** the estimator.

**(b) The frozen tolerances were tighter than the estimator's intrinsic precision.**
Calibration (now C11, run at setup): bias −2.6% / +0.1%, **scatter 9.8% / 4.4%** at targets
A / B. Raising `ac_traj` 400 → 1600 moved scatter only 10.1% → 7.1%, because the error is
dominated by **origin correlation** (~40 highly-correlated origins across a 100-Hubble-time
span), not by trajectory count — so it is not affordably reducible. The old `tol_rate = 5%`
and `tol_seed = 15%` were arbitrary design decisions **below** that floor: CONVERGED would
have been unreachable and branches I-a/I-b reachable only by luck, **on perfectly good data**.

**Tolerances are therefore set FROM the measurement: `tol_rate = tol_seed = 0.25`** (≈3×
the measured scatter), with the calibration recorded here and **re-measured at run time by
C11**, which voids the precision claim if it drifts.

**This is not a weakened test — it is a corrected precision claim.** The discrimination this
run exists to perform is **target A vs target B, which are 3.8× (280%) apart — roughly 30
standard deviations of the measured scatter.** What the instrument cannot do is certify a 5%
match to either target, and claiming it could was the defect. Branches I-a/I-b are therefore
decided as *"which target is consistent, and is the other excluded"*, never as a 5%
agreement.

## 3 · Unresolved inputs (exposed, not invented)

U1. **The scalar→graviton gap** (§1.1) — structural, unbridged, blocks any O2 claim.
U2. **λ's physical value in GRUT** — the record supplies the *rule* m²_eff ∼ √λ H² and an
O(1)-coupling hypothesis (`two_scale_desitter.py` verdict: "the horizon supplies the noise
and the tracking; it does not supply the mode or its coupling"), but no derived λ. λ = 0.01
is a STRUCTURAL_SELECTION to hit the record's referent, **not** a derived value.
U3. **The existence of a light scalar IR vacuum mode** — a declared input in the record, not
derived (same verdict block).
U4. **The O(1) proportionality constant in m²_eff ∼ √λ H²** — the record gives the scaling,
not the coefficient; the run therefore tests the *scaling relation*, and an O(1) mismatch is
NOT a falsification of the rule (branch H).
U5. **N1–N3, N6–N10 control definitions** — UNRESOLVED — CONTROL DEFINITION REQUIRED.

## 4 · KMS/FDT status in this run (declared, to prevent a silent import)

The overdamped SY Langevin equation carries its own fluctuation–dissipation balance:
diffusion D = ½(H/2π)² against drift 1/(3H), whose stationary distribution is the SY
equilibrium. **This is the equation's internal balance, not the register's rung2 KMS gate**
(which governs the graviton noise/retarded kernel pair). Imposing rung2's coth condition on
this scalar system would be **new structure** and is therefore NOT done. Q2-C9 checks the
internal balance only, against an independent quadrature anchor.

## 5 · Parameter ledger (the anti-pinning instrument)

| # | parameter | value | class | fittable? |
|---|---|---|---|---|
| 1 | H | 1.0 (units) | INHERITED (convention) | no |
| 2 | noise rule | H/2π | INHERITED PHYSICAL | no — frozen by config validator |
| 3 | drift 1/(3H) | — | INHERITED PHYSICAL | no |
| 4 | **m²_bare** | **0.0** | INHERITED (the unlifted zero mode) — *the primary dynamics receive NO mass* | no |
| 4b | *m²_eff = 0.1H²* | *reference only* | **NOT AN INPUT** — an existing reference result / comparison target (§2.2). Injecting it into the primary run would turn the phenomenon under test into an input; the auditor's firewall fails the run if it appears among the physical inputs | n/a |
| 5 | λ | **0.01** | STRUCTURAL_SELECTION (§2, U2) | **no — frozen; a post-hoc change voids the run** |
| 6 | φ₀ | 1.0 | COMPUTATIONAL (initial condition; Q2-C6 proves it does not matter) | no |
| 7 | dt, t_max, n_traj, stride | 0.01, **600**, 4000, 25 | COMPUTATIONAL (horizon extended at design time per §2.3) | no |
| 8 | seeds | 20260907 + 0…4 | COMPUTATIONAL (fixed list) | no |
| 9 | fit windows (3) + autocorrelation lag range | [5,40] [5,65] [30,70]; τ ≤ 200 | **DESIGN DECISION, preregistered** | **no** |
| 9b | ac_fit_frac / ac_origin_stride / ac_amplitude_cut | 0.8 / 10 / 0.05 | **DESIGN DECISION, preregistered** — lifted out of hardcoded defaults; they set the EFFECTIVE fitted span | **no** |
| 10 | tolerances | §8 | **DESIGN DECISION, preregistered** | **no — may not be relaxed after results** |
| 11 | measured rate, stationary moments | — | **DERIVED FROM THE RUN** (outputs, never inputs) | n/a |

**Anti-pinning enforcement:** configuration lives in `calc/q2_config.json`, is SHA-256
hashed, and the hash is embedded in every output; `calc/q2_audit.py` (independent) fails the
run if the emitted hash and the on-disk config disagree. The instrument raises on any
missing physical key — there are no fallback defaults to silently supply a value. Seeds are
a fixed list. No branch in the analysis selects on the result.

## 6–7 · Numerical architecture and discretization

Overdamped Langevin, **Euler–Maruyama**. Declared property (not an approximation choice):
the noise is **additive**, so the Milstein correction vanishes identically and EM is strong
order 1.0 for this equation. Ensemble of independent trajectories; moments accumulated on a
stride. No lattice, no box, no UV/IR cutoff, no solver tolerance — the single-mode
(coarse-grained IR) formulation has none, which removes the finite-box and cutoff artifact
classes by construction rather than by control. **No new physical scale is introduced by any
numerical parameter.**

## 8 · Convergence criteria (frozen thresholds)

Timestep ladder dt ∈ {0.04, 0.02, 0.01, 0.005}; ensemble ladder n ∈ {500, 1000, 2000, 4000};
5 independent seeds; burn-in = 50% of t_max discarded before any stationary estimate;
fit windows as above, in Hubble times. Tolerances (**DESIGN DECISIONS**, no defensible record
value exists): rate 5%, null 0.002 absolute, convergence 5% between successive ladder steps,
seed spread 15%, noise normalization 2%, stationary moment 10%. **CONVERGED** requires the
last ladder step of both dt and n within tolerance, seed spread within tolerance, AND the
three decay-fit windows mutually consistent within tol_window_consistency;
anything else is **NONCONVERGED**.

## 9 · Seed policy and RNG

Fixed list of five explicit integers — **[20260907, 20260908, 20260909, 20260910,
20260911]** — preregistered here and stored as `seed_list_explicit` in the config (the
instrument uses the explicit list, not the `seed_base + i` formula, and raises if the two
disagree). **RNG implementation, recorded for cross-environment reproducibility:** Python
stdlib `random.Random` (Mersenne Twister MT19937), `.gauss(0, 1)`; one instance per ensemble
run; draws consumed in trajectory-index order within each timestep. The emitted manifest
carries the RNG name, the resolved class, the Python version, and the explicit seeds; the
auditor fails the run if any differs from this declaration. No seed may be added, dropped, or reordered after execution; a rerun with
different seeds is a NEW run requiring its own record.

## 10 · Controls — Q2-C1…C10 (numbering fence)

**These are NOT the house N1–N10.** Only N4 (null-manufacturing mutant) and N5 (displaced
gate) have committed definitions (`RAI_GORILLA_T1.md:36–41`); N1–N3 and N6–N10 are referenced
without definitions in the committed record and are marked **UNRESOLVED — CONTROL DEFINITION
REQUIRED**. The battery below is built only from already-declared structure.

| id | control | what disappears if the mechanism is real |
|---|---|---|
| C1 | zero-noise limit | if relaxation were a noise artifact it would vanish; here it must survive and equal the drift rate |
| C2 | zero-interaction (λ=0) OU limit | the exact analytic baseline must be reproduced (strongest correctness anchor) |
| **C3** | **massless free NULL (m=0, λ=0)** | **the unlifted-zero-mode analogue: variance must grow as 2Dt with NO relaxation. If a rate appears here, the instrument manufactures lifting and the primary run is VOID** (N4-analogue role) |
| C4 | timestep refinement | a discretization artifact drifts with dt |
| C5 | seed dependence | a seed-specific fluctuation does not replicate |
| C6 | initial-condition dependence | an initialization imprint moves the stationary state |
| C7 | noise normalization | a mis-normalized noise shifts every moment (checked at source) |
| C8 | planted positive (known m²) | an instrument blind to a real rate cannot report one (N5-analogue detect role) |
| C9 | stationary moments vs independent quadrature | a detailed-balance violation lands on the wrong stationary law |
| C10 | ensemble-size refinement | a small-ensemble fluctuation shrinks with N |
| **C11** | **planted-Λ calibration of the PRIMARY estimator** (synthetic AR(1), exact known Λ, production geometry) | **an estimator that cannot recover a known Λ cannot report an unknown one; its measured scatter is what the tolerances are set against** |

## 11–12 · Observables (defined before execution)

**Primary O1a — relaxation rate from the stationary autocorrelation**
C(τ) = ⟨φ(t)φ(t+τ)⟩: least-squares slope of ln[C(τ)/C(0)] over lags τ ≤ 200 (400 stationary
trajectories, origins strided); units H; expected null behavior: no decay for the C3 null;
artifact controls C3/C4/C5/C10; interpretation **EXPLORATORY** pending audit.
**Cross-check O1b — ensemble-mean decay fit** over the three preregistered windows
[5,40], [5,65], [30,70]. **Coordinate: ABSOLUTE SIMULATION TIME, in the TRANSIENT phase
(before burn_in_time = 300).** This is deliberate and not an inconsistency with the burn-in:
O1b measures relaxation *from the initial condition*, which by definition can only be
observed before the system has relaxed. O1a, by contrast, is a **LAG** coordinate computed
in the **stationary** phase [300, 600]. *The two estimators use different coordinates in
different regimes and their spans are never compared to one another.*

**GATING RULE (frozen ex ante).** Window-consistency within tol_window_consistency (20%)
gates CONVERGED **only when the measured rate is fast enough for the windows to span ≥ 1
e-fold**. At target A the windows span 1.17 / 2.00 / 1.33 e-folds — adequate. At target B
they span 0.31 / 0.53 / 0.35 — inadequate, so **if the measured rate is near B, O1b is
reported INCONCLUSIVE for that route and may not invalidate the O1a primary.** Without this
rule a legitimate slow-rate result would be failed for a purely statistical reason.

**E-FOLD FIGURES, disambiguated — and the distinction that matters.** Three different spans
exist and were previously conflated (a pre-execution audit caught this; the certified figure
described a range 1.67× wider than any fit uses):

| span | A | B | meaning |
|---|---|---|---|
| O1b decay windows (ABSOLUTE TIME) | 1.17 / 2.00 / 1.33 | 0.31 / 0.53 / 0.35 | cross-check only |
| O1a **available** lag range (τ ≤ 200) | 6.67 | 1.77 | what is *collected* |
| O1a **EFFECTIVE FITTED** span | **3.00** (to τ=90, amplitude-limited) | **1.42** (to τ=160, frac-limited) | **what the fit actually uses — the operative number** |

The fit keeps lags with τ ≤ `ac_fit_frac`·τ_max **and** C/C₀ > `ac_amplitude_cut`, so the
effective span is min(fit_frac·τ_max, ln(1/cut)/k). **The auditor certifies the EFFECTIVE
span**, not the available range, and fails the run if it drops below 1 e-fold at either
target. `ac_fit_frac` was raised 0.6 → 0.8 at design time so the slower target clears the
threshold with margin (1.42 rather than 1.06, which sat barely above the very threshold it
was tested against).

**The three analysis knobs are now IN THE FROZEN CONFIG** (`ac_fit_frac`,
`ac_origin_stride`, `ac_amplitude_cut`). They were hardcoded Python defaults, absent from
the config and never inspected — despite §5 classifying every analysis range as a
preregistered design decision. The instrument now takes them as required arguments with no
defaults, and the auditor fails if any hardcoded default reappears.
**Primary O2 — stationary variance** ⟨φ²⟩ over t > 150; units H²; compared to the
independent SY quadrature anchor; artifact controls C6/C7/C9.
**Secondary S1** — fit quality r² of the rate fit (a poor fit is itself informative:
non-exponential relaxation). **Diagnostic D1** — φ sample at t_max for distributional
inspection. **No observable is added after execution.**

## 13–14 · Stopping and invalid-run rules

Execution stops at t_max for every configured run; there is no result-dependent early stop.
A run is **INVALID_RUN** if: the emitted config hash ≠ on-disk config; any required key is
missing; C3 reports relaxation beyond tol_null; C7 exceeds tol_noise; the fit window contains
< 5 usable points; or any non-finite value is produced.

## 15–16 · Output schema and provenance

`calc/RESULTS_q2_stochastic_sy.json` — manifest (instrument SHA-256, config SHA-256, full
config echo, Python version, scope fence, wall time), analytic_anchors, runs.primary (per
seed: rate, r², fit points, stationary variance), results, labels_available.
`calc/RESULTS_q2_stochastic_sy.md` — human-readable report generated from the JSON.
`calc/RESULTS_q2_controls.json` — C1…C11 with per-control criteria; carries its own sha256,
the instrument's, and the config's.
`calc/RESULTS_q2_audit.json` — independent audit findings and label.

## 16b · The non-circularity firewall (the Q2 analogue of Q1's anti-self-certification)

**Requirement, verified mechanically by `calc/q2_audit.py` before and after execution:** *the
primary stochastic dynamics contain no parameter, initial condition, analysis window, or
observable definition whose value is equivalent to the phenomenon being tested.* Implemented
as: m²_bare = 0 (no injected mass); the live physical-input set is exactly {H, m²=0, λ, φ₀,
noise-rule} with no rate-valued member; both targets appear only in the anchor block and
never in the integrator body; the reference m²_eff = 0.1H² is not an input; the
autocorrelation is connected; plus quantitative adequacy checks (dt·k ≪ 1 at both targets;
≥ 1 e-fold spanned by the primary range at both targets; burn-in ≥ 2 slow relaxation times).
*Disclosure:* a first implementation used a naive decimal-proximity test and produced three
false positives (λ, dt, an inverse window length — all dimensionally distinct from a rate);
it was replaced with the dimension- and mechanism-aware checks above rather than deleted or
weakened.

## 17 · Analysis firewall

`calc/q2_audit.py` **does not import** `q2_stochastic_sy` or `q2_controls`; it recomputes the
diffusion constant, the record-rule rate, and the seed set independently, and verifies hashes,
schema, seed-set identity, and the absence of any emitted PASS/FAIL token. The simulation
cannot certify itself.

## 18 · Decision tree (frozen; no branch is "GRUT success")

A **clean null** — no relaxation generated (rate ≈ 0 within tol_null) with C1–C10 clean.
B **reproducible nontrivial dynamics** — a finite rate, converged, seed-stable, surviving
every control. *Still not evidence for GRUT*: must then be classified as (b1) already
supplied by the declared equations (the SY rule is literature — the default reading), (b2)
dependent on the unresolved inputs U2–U4, or (b3) genuinely new within the model.
C **numerical artifact** — effect moves with dt or n (C4/C10 fail).
D **parameter-sensitive** — outcome moves qualitatively under φ₀ (C6) or λ perturbation.
E **nonconvergent** — ladders do not settle within tolerance.
F **control reproduces the phenomenon** — C3 shows relaxation ⇒ primary VOID.
G **phenomenon disappears under a control that should preserve it** (C1/C2/C8 fail) ⇒
instrument defect, not physics.
H **unresolved input dominates** — the outcome is set by λ or the O(1) coefficient (U2/U4).
I-a **Target A reproduced** — measured rate within tol_rate of m_eff²/(3H) = 0.03333H (the
record's referent construction).
I-b **Target B reproduced** — measured rate within tol_rate of Λ₁ = 0.00885H (the SY
Fokker–Planck eigenvalue of the integrated equation). *I-b with not-I-a would mean the
equation behaves as the SY literature says while the record's naive composition of its own
rule overstates the rate by ~3.8× — a documentation finding about the record, not a physics
result about GRUT.*
J **neither target reproduced** — report the measured value and both gaps.
*All branches are evaluated against the FORMULAE (§2.1, §2.2), never against the quoted
0.034H, and both targets are emitted before measurement.*

## 19–22 · What each outcome would and would not mean

**An advance:** a converged, control-surviving result that lands in B-(b3) — behavior not
already supplied by the SY literature rule — or a clean, well-controlled A or J, either of
which contradicts an assumption the record currently leans on. **Null / inconclusive:** A
with clean controls (informative), or E/D/H (uninformative about physics; informative about
what the question needs). **What would falsify a specific computational hypothesis:** branch
J falsifies "the SY channel reproduces the record's referent rate at λ = 0.01 under these
declared dynamics" — a *computational* hypothesis about the declared model, **not** a
statement about GRUT or about gravity. **What would merely motivate another investigation:**
any of C, D, E, F, G, H — each names its own next step and none licenses a claim.

**Nothing in any branch modifies a claim status, the register, the corpus, Q1, or a closed
gate. Adjudication is the owner's.**
