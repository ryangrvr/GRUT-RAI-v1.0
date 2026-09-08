# QUESTION LEDGER — the puzzle table

> **2026-09-07 · The Reality Program's investigation ledger** (`program/REALITY_PROGRAM.md`
> governs). Dispositions grade *investigations*, never claims: **OPEN** (on the table,
> not yet investigated) · **GATED** (design gate underway) · **ON** (gate survived; work
> licensed at the gate's scope) · **OFF** (evaluated and set aside — the evaluation is
> cited on the entry; never merely unfashionable) · **ANSWERED** (ran the pipeline to a
> status update). OFF ≠ not-yet-investigated; ON ≠ true. Entries are updated, never
> deleted.

## Q1 · The USL analogue signal — **GATED** (rank 1; gate built and rendered 2026-09-07; **OFF is proposed but NOT applied — see the decision line below**)

> **Gate question:** Can a physically realizable open system make a GRUT-class response
> large enough to distinguish it from that same apparatus's standard QM/environmental
> model?

What the record already constrains: rung8's κ and ω_c are *staked* inputs and the
standing verdict is shape-only, quiet-or-faint — so the 1.22 ħω_c peak enters the gate as
a hypothesis to be re-derived for the candidate apparatus, not as an accepted number
(suppression figures likewise get re-established from sources, not inherited). The
gate's hardest row is degeneracy: an analogue system tests the analogue Hamiltonian, so
the licensed claim is about the USL response *class*, and the discriminator must be the
spectral shape against the standard environmental master equation for the same device.
The bar on record: parameter-free DP is already excluded at Gran Sasso. Must be built if
ON: an analogue-system modeling layer (BEC / high-Q optomechanics). Forbidden shortcuts:
inheriting the peak; treating "GRUT-like" as "GRUT"; amplitude claims without the
degeneracy row.

**GATE RECORD (2026-09-07):** `program/gates/Q1_USL_TABLETOP_GATE.md` built design-first
(no computation). Design-time routing: **REFUSE — analogue-mapping obstruction** (the
engineered signal sits inside the baseline's freedom by construction; nothing
GRUT-specific transfers; the real-coupling version is governed by the record's own
quiet-or-faint 7–47-order verdict — which the reconstruction CONFIRMED as the record's
own figure, correcting this ledger's earlier doubt above). **Owner decision owed and NOT
YET TAKEN:** accept (which would move Q1 → OFF, evaluation = the gate) or contest.
**Until that acceptance actually occurs, Q1's disposition is GATED, not OFF** — under this
ledger's semantics OFF means *evaluated and set aside with the evaluation cited*, and no
acceptance has been recorded, so applying it now would be the disposition drifting by
inertia rather than by ruling. Claim statuses untouched.

## Q2 · Stochastic KMS-bath dynamics — **GATED** *(gloss: NOT ANSWERED)* (rank 2; package executed 2026-09-07 — see the ruling below)

> **Gate question:** Do the legitimately specified GRUT constitutive equations, evolved
> numerically as a stochastic realization, exhibit structure (fixed points, spectra,
> response) not visible analytically — under a numerical instrument that itself passes
> the house discipline?

What the record already provides: the O2 interacting graviton zero-mode is **reopening
key #1 of the freeze** (lift rate 0.034H at m_eff² = 0.1H² already on record) — this
question walks through a door the freeze left open. Numerics are a method, not a bypass:
an underived equation does not become fundamental by discretization, and the
frontier-reserved fences (transport Σ, the dS trace sector) bind the simulation exactly
as they bind analysis. Must be built if ON: the stochastic instrument class itself —
discretization + convergence controls, mutation batteries, plants, ensemble negative
controls; "the computer found a fixed point" is treated as a pass-label until de-pinned.

**EXECUTION PACKAGE FROZEN (2026-09-07, nothing run):**
`program/gates/Q2_STOCHASTIC_EXECUTION_PREREG.md` + `calc/q2_run.py` (single entrypoint,
refuses any argument but `--config`). Scope fence on the instrument's face: this evolves the
**scalar** SY channel, **not** the interacting graviton zero-mode, and cannot discharge
reopening key #1. Design-time findings recorded before any execution: the record's "≈0.034H"
traces to m_eff²/(3H) = **0.0333H** (and a separate, unrelated 0.034 exists in the record —
the worldline S(ω=0.1); the two are now separated); **two** rate targets are preregistered
because the record's composition (0.0333H) and the SY Fokker–Planck eigenvalue of the very
equation (0.00885H) differ by 3.8× — with a formal model-status adjudication and a rule that
neither may be chosen post hoc; an SNR defect, a stationarity defect, and an unconnected-
correlation bias were each found and repaired before running. Owner authorization pending.

**OWNER RULING 2026-09-07, after execution and adjudication (`0b33ebe`).** The boxed
question above is **preserved verbatim and is NOT re-worded.** Re-wording it after seeing the
result would be post-hoc question substitution. The executed model was the **inherited scalar
Starobinsky–Yokoyama channel**, graded in the adjudication §6 as INHERITED /
STRUCTURAL_SELECTION / ASSUMPTION with *"derived from the GRUT construction? **NO**"*.
**Therefore the execution did NOT answer this question, and the scalar-SY run — however
cleanly it executed — may not be used to discharge it.** Disposition token: **GATED**; the owner's ruling records the clarifying gloss *"not
answered"*, which is **not** a sixth disposition token — the declared set remains OPEN /
GATED / ON / OFF / ANSWERED. GATED here — not because the
computation failed (it ran cleanly and passed every control) but because it answered a
different, narrower question, recorded separately as Q2-SY below. Q2 is **not** "failed":
the original question remains unanswered, the child question is answered, and the run was
technically valid — three distinct facts.

## Q2-SY · The inherited scalar SY computational question — **ANSWERED** (post-execution child of Q2)

> **Provenance: spawned from Q2 on 2026-09-07 AFTER execution**, by owner ruling, to hold the
> question the run actually answered without altering Q2's registered wording.

> **Registered question — the PRE-EXECUTION frozen wording** (prereg §1, byte-stable across
> every commit from freeze to run; used here so that no post-execution formulation stands in
> for the question actually asked, and because it covers **both** limbs, including the one
> that came out NO):
>
> *"Does the already-declared stochastic Starobinsky–Yokoyama (SY) dynamics, started from a
> bare massless field, **generate a finite relaxation rate** — and does it **reproduce the
> record's own referent value** m_eff² = 0.1H² → rate = m_eff²/(3H) — under controls that can
> distinguish generated dynamics from initialization, discretization, noise-normalization,
> ensemble-size, and analysis artifacts?"*
>
> **Answered on both limbs, with the first limb stated at its exact strength:**
>
> **Limb 1 — qualified.** *The inherited scalar SY dynamics produced the finite decay rate
> expected for that equation, and the simulation recovered the independently established
> nonlinear gap* (0.009216 H against Λ₁ = 0.008892 H). **This is not an emergent prediction
> of a previously unconstrained rate:** the equation, λ, and the spectral structure were all
> supplied in advance, and branch **H remains operative** — Λ₁ ∝ √λ with λ **selected**.
> The prereg's verb "generate" is therefore read in its weak sense (the dynamics exhibited a
> finite rate) and **must not be read as "GRUT generated a scale."** *The run demonstrates
> dynamics, not parameter prediction.*
>
> **Limb 2 — NO.** The record's referent value was **not** reproduced (target A
> NOT OBSERVED).
>
> *(The owner's ruling phrased this entry as "does the inherited scalar SY channel … reproduce
> its independently established nonlinear spectral dynamics without introducing new
> structure?" — retained as the entry's summary label. The frozen wording above is the
> registered question; the label is aimed at the affirmative limb only.)*

**ANSWERED — and preregistered as NOT an advance.** Preregistered branches reached:
**B-(b1), b2, H, I-b, not I-a.** Prereg §19–22 classifies **H** as *"uninformative about
physics"* and required **B-(b3)** for an advance; b3 was not reached. **No registered
scientific advance occurred under the Q2 preregistered decision rule.** That does not erase
the findings below; it means they do not satisfy the criterion set beforehand for advancing
the GRUT question.

What the run did establish (execution record `78452bd`, adjudication `0b33ebe`):
the nonlinear stochastic simulation recovered the independently solved spectral scale
(0.009216 H vs Λ₁ = 0.008892 H, +3.6%, inside the pre-measured scatter); planted and analytic
controls performed (planted exact gap 0.100000 → 0.101655; zero-noise and OU limits; C3 null
clean; stationary variance −0.10% vs quadrature); convergence passed; **target A NOT
OBSERVED**, **target B OBSERVED** — and, carried inline per prereg §2.2's own outcome
table so the fence travels with the finding: *B reproduced means the implementation agrees
with the registered spectral-gap calculation of the equation it integrates — **NOT evidence
for GRUT, NOT a prediction, NOT O2***; O1b INCONCLUSIVE under its preregistered exemption; the
selected λ remains a **non-predictive input** (branch H); and **no new structure appeared
beyond what was already analytically present**. Instrument fidelity → **RECOVERED**; the
estimator-validity theorem → **DERIVED** at its declared mathematical scope. **Localized
finding:** within the scalar SY model the A-vs-B discrepancy is predominantly in the O(1)
mass-normalization (0.100 H² vs the variance-matched 0.0288 H², 3.47×), **not** in the OU
relaxation formula (8.1% when fed a consistent mass); **the scaling law m²_eff ∝ √λ H² was
itself NOT tested and remains UNRESOLVED.** **Residual coverage limitations, retained and not
backfilled** (the experiment is over and the preregistration is frozen): C4's timestep ladder
does not exercise the O1a primary estimator, so the primary's convergence rests on C10; and
branch D's λ limb is independently controlled by nothing, being absorbed into H rather than
falsified.

## Q2-BRIDGE · GRUT/O2 → SY stochastic reduction — OPEN

> **Provenance: spawned 2026-09-07 from the Q2 adjudication §7.** Inherits **no** disposition
> from Q2 or Q2-SY.

> **Gate question:** Can the interacting TT graviton zero-mode be *derived* to reduce to an
> SY-class stochastic dynamics, with the effective potential, the noise kernel, and the
> coupling **derived rather than selected**?

Required for any number of the Q2-SY kind to bear on O2: (1) a stochastic reduction for the
interacting TT graviton zero-mode on de Sitter with potential and noise computed, not posited;
(2) a **derived λ_grav** — since the measured rate scales as √λ, a selected λ makes the value
uninformative (branch H); (3) a demonstration that "lifted vs protected" is decided by that
equation's spectral gap. **Standing obstruction:** (1) and (2) live in the record's
frontier-reserved sectors, where in-house resolution is an automatic fail under `CHARTER.md`
§3. **No computation is authorized. Reopening key #1 remains NOT discharged.**

## Q3 · Dimensional transmutation — OPEN (rank 3)

> **Gate question:** Can GRUT's own renormalization/response structure generate a
> dimensional scale from dimensionless microscopic data — or does every candidate
> mechanism relocate a scale into the bath, kernel, cutoff, initial condition, or
> renormalization condition?

The gate's first step is an inventory question with a checkable answer: **where in the
declared structure does a dimensionless running coupling live?** QCD's transmutation
rides a marginal dimensionless coupling; gravity's EH coupling is dimensionful — the
classic obstruction. The record's two candidates: the anomaly coefficients (dimensionless
by construction) and the genuine RG log already in the derived kernel
(L = log(μ²/ω²), μ-slot open). Whether that log structure *runs* in a scale-generating
way or μ remains a slot is precise and answerable. Tripwires already on record: the
keystone bridge test (derive vs relocate — relocation is priced +1 at entry, reported as
discharge it is laundering) and the ROOT-1 fences at ω ≲ 3.4H. Note: if transmutation
worked it would have to reroute the specific structural split the Γ_T gate found
(everything fixed lives where nothing is observable) — that routing belongs in this
gate's decision tree.

## Q4 · An EFT hierarchy for the suppressed sector — OPEN (rank 4)

> **Gate question:** Does GRUT admit a controlled derivative/power-counting expansion in
> which heavily suppressed terms have a principled high-scale interpretation — as a NEW
> theorem-shaped result?

Standing verdicts are inputs, not casualties: the Γ_T closure remains exactly "the
licensed candidate provides no experimentally relevant discriminator under the tested
conditions." The observation that motivates the question: the closure's chromatic term is
already implicitly an EFT statement — (ω/ω_Pl)² suppression is higher-dimension-operator
power counting. Formalizing "GRUT admits a controlled hierarchy" would be a genuinely new
structural claim (H1-campaign-style machinery applies). Forbidden shortcut: relabeling
the graveyard as a success; nothing here reopens closed gates.

## Question families — backlog (unranked, unformalized; listed so they are not lost)

What is fundamental vs emergent vs merely effective · why the constants and scales that
exist · the structure of quantum behavior · the structure of gravity · the arrow of time
(the one surviving relative datum) · cosmic history · the matter/geometry/information/
thermodynamics/observation relations · whether apparently independent laws share one
constitutive principle · which mathematical structures are necessary vs accidental · and
the standing meta-question: **what questions haven't we thought to ask?** Each enters as
its own OPEN entry with a boxed gate question before any work.
