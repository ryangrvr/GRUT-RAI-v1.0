# BOOK III — QUANTUM REALITY IN GRUT

> **WORKING DRAFT — part of the GRUT working corpus; statuses per `books/CORPUS_CHARTER.md`;
> subject to chapter-by-chapter audit; nothing here banks.**

**GRUT Books — Working Edition v1.0** · D. Ryan Grover · 2026-09-07 · release `zenodo-v1.0` · Markdown is the authoritative source; the PDF is generated from it. Drafted from the frozen record by the RAI builder (Claude, Anthropic) under owner direction — this edition is a publishing pass only: formatting, navigation, and metadata; no claim strengthened or weakened for publication.

## Contents

- [1 · Scope, and the reading rule this book lives or dies by](#1--scope-and-the-reading-rule-this-book-lives-or-dies-by)
- [2 · The backbone: one action, one reduction](#2--the-backbone-one-action-one-reduction)
- [3 · The unitary core: Schrödinger recovered](#3--the-unitary-core-schrödinger-recovered)
- [4 · Decoherence: the noise kernel and the pointer basis](#4--decoherence-the-noise-kernel-and-the-pointer-basis)
- [5 · The Born measure: the never-sorted door](#5--the-born-measure-the-never-sorted-door)
- [6 · Measurement and interpretation: the absence map](#6--measurement-and-interpretation-the-absence-map)
- [7 · Gravitational decoherence: the rung8 hypothesis](#7--gravitational-decoherence-the-rung8-hypothesis)
- [8 · The linear-universe response no-go (the RRT arm)](#8--the-linear-universe-response-no-go-the-rrt-arm)
- [9 · What would move this book](#9--what-would-move-this-book)
- [Sources drawn from](#sources-drawn-from)
- [Gaps in this book](#gaps-in-this-book)

---

---

## 1 · Scope, and the reading rule this book lives or dies by

This book presents what the GRUT record says about quantum mechanics: how the framework
recovers standard quantum theory, what its open-system machinery does for state evolution
and decoherence, where the Born probability structure comes from, what its one proposed
quantum-gravitational observable is, and what its cleanest theorem-grade result forbids.

Four different kinds of statement live in these pages, and the entire value of the book is
that the reader can never mistake one for another:

- **Recoveries** — standard quantum physics reproduced on GRUT's declared inputs, largely
  *by identity*: the executed machinery is standard machinery. Recovery establishes
  compatibility, not correspondence evidence, and it earns nothing toward prediction.
- **Assumptions** — declared inputs, priced on the register's ledger. The most important
  one in this book, the Born measure, is the framework's openly flagged never-sorted door.
- **Hypotheses** — proposed relations, not derived, not validated. Exactly one lives here:
  the rung8 gravitational-decoherence shape signature.
- **One derivation** — the linear-universe response no-go from the RRT arm, which is a
  theorem about *all* linear dynamics and therefore, precisely because of its generality,
  carries no confirmatory weight for GRUT. It closes a door rather than opening one.

The owner's standing directive governs throughout: no invented derivations, no promotion of
hypotheses to predictions, no reopened gates. Where the record is silent — and on several
questions a physicist would ask first, it is silent — this book says so explicitly. The
PREDICTED set is empty across the corpus, and nothing in this book is an exception.

> **STATUS: EMPTY (nothing has earned entry; Book IX governs entry)** — canonical claim 21;
> the PREDICTED set contains no quantum-sector entry (source: `GRUT_PROGRAM_FREEZE.md` §3,
> `books/CORPUS_CHARTER.md`).

---

## 2 · The backbone: one action, one reduction

GRUT's quantum story starts where the whole framework starts: a single Schwinger–Keldysh
influence action for the system degrees of freedom against a declared bath,

    S_IF[h_r, h_a] = ∫ (dω/2π) d³k [ h_a · K_R(ω,k²) · h_r + (i/2) h_a · N(ω,k²) · h_a ]

with K_R the retarded dissipation kernel and N the noise kernel (`S_IF.md`,
`provenance/claims.json#rung1_inin_formalism`). Everything quantum-mechanical in this book
descends from one move: **integrating out the declared bath yields the reduced dynamics of
the system's density matrix** — the reduced master equation, in the Feynman–Vernon /
Calzetta–Hu sense the register cites (`feynman_vernon1963`, `calzetta_hu_book` in
`provenance/sources.json`).

Two honesty notes attach to the backbone before any physics is read off it.

First, the form itself proves nothing. The influence-functional form is universal: any
local, causal open quantum system coarse-grains to S_IF = K_R + (i/2)N. GRUT adopts a
universal IR language; it does not own the universality.

> **STATUS: RECOVERED (generic; u1: the form confers no GRUT-specific content)** —
> canonical claim 1 (source: `provenance/claims.json#u1_form_universality`,
> `GRUT_MODEL_FRAMEWORK.md` §3).

Second, writing S_IF at all costs declared inputs. The register prices four on the
formalism node alone: the system/bath split, the Gaussian/linear-response truncation, the
background Lorentzian causal structure, and the 4d-covariant availability of the
Ward-sourced gauge-orbit zero (booked 2026-08-17, discharge condition named).

> **STATUS: ASSUMPTION (four declared inputs, +4 on the rung1 formalism node; the
> system/bath split is an AXIOM-form input whose specific partition is a
> structural selection)** — source: `provenance/claims.json#rung1_inin_formalism`
> ledger_note; `GRUT_MODEL_FRAMEWORK.md` §2.

In equilibrium the noise kernel is not free: N is locked to Im χ by the
fluctuation–dissipation theorem with the coth(ħω/2kT) factor, and KMS detailed balance is
enforced on every admissible kernel as a hard admission gate (`gate/kms.py`). This is the
one place the ledger *removes* an input (−1): N ceases to be independent.

> **STATUS: ASSUMPTION (borrowed standard identity, enforced as a hard admission gate;
> rung2)** — canonical claim 2 (source: `provenance/claims.json#rung2_kms_gate`;
> `callen_welton1951`, `kubo1966` per `provenance/sources.json`).

*Standard-physics background, distinguished from GRUT's record:* the reduction from a
closed system-plus-bath to a closed dissipative master equation is the Nakajima–Zwanzig /
Born–Markov construction, and it consumes inputs of its own — most notably the factorized
initial system–bath state (the quantum Stosszahlansatz: the closed dissipative master
equation is literally the Qρ(0)=0 deletion of initial correlations) and the continuum limit
of bath modes. The GRUT record does not hide this; its own arrow-of-time analysis
(`calc/RESULTS_arrow.md`, `docs/WHERE_IT_STOPS.src.md` §I.2) identifies the factorization
as one of the three interchangeable guises of the imported past-boundary condition. The
direction of relaxation in the reduced dynamics is Book V's subject; what matters here is
that the master equation's irreversibility is *supplied by declared inputs*, not generated
by the formalism, and the record says so on its face.

What the record does **not** contain is a GRUT-specific master equation for a concrete
laboratory system, derived in-house with novel structure. The reduction is cited machinery
on declared inputs. The one executed in-house master-equation computation in the quantum
sector is the rung8 energy-basis decoherence-rate calculation of §7 — and it is a
magnitude audit of a hypothesis, not a new dynamical law.

---

## 3 · The unitary core: Schrödinger recovered

Switch the noise off and the reduced dynamics closes on the system: the influence-functional
reduction reproduces the Schrödinger equation as the unitary core of the QM limit. This is
rung6's first clause — "integrating out the bath yields the reduced-density-matrix master
equation; unitary core = Schrödinger" — and it is a recovery in the strict, deflationary
sense this corpus uses everywhere: the machinery that produces it is standard open-system
machinery, and the result establishes that GRUT *contains* quantum mechanics, not that it
*explains* it.

> **STATUS: RECOVERED (noise-free limit of the influence-functional reduction; the register
> carries the composite rung6 node at tier `assumed` with +2 declared imports — a
> recovery-with-imports, same shape as the GR limit)** — source:
> `provenance/claims.json#rung6_qm_limit`; frozen summary `GRUT_MODEL_FRAMEWORK.md` §5.

The two imports are the content of the "assumed" tier, and the register declares them by
name (rung6 ledger_note, +2):

1. **The quantization / single-valuedness condition.** The record books this as declared
   import (i) and nowhere elaborates or derives it; it is a line-item on the ledger, not a
   worked document. This book records the absence as an absence.

   > **STATUS: ASSUMPTION (declared import (i) on rung6; carried on the ledger, not
   > elaborated anywhere in the record)** — source: `provenance/claims.json#rung6_qm_limit`
   > ledger_note.

2. **The Born probability-measure postulate** — §5 of this book, where it gets the full
   treatment it is owed.

A discipline note the record keeps on its own face: the rung6 ledger was once undercounted
as +1 — one of the two imports was being carried silently — and the kill-shot audit that
caught it is recorded in the node itself. The corrected +2 stands, with a written stance
justification under the register's `laundering_ok` waiver: the waiver says the ledger, not
the tier, carries the inputs.

The node's own overturning computation states what would break the recovery: show that the
influence-functional reduction does *not* reproduce Schrödinger in the noise-free limit —
or show that decoherence alone yields the Born measure (it does not; the improper-mixture
objection, §5).

---

## 4 · Decoherence: the noise kernel and the pointer basis

With the noise on, the second half of rung6 engages: **the noise kernel N supplies
decoherence, and decoherence selects a pointer basis.** Superpositions of states that the
bath distinguishes lose their mutual coherence at a rate set by N; the surviving basis is
the one the system–bath coupling picks out. In GRUT's telling this is a sector instance of
the one architecture — the same N that the KMS gate locks to Im χ in equilibrium is the
object doing the einselecting.

> **STATUS: RECOVERED (standard decoherence machinery on declared inputs)** — canonical
> claim 11 (source: `provenance/claims.json#rung6_qm_limit`; `NO_GO_LEDGER.md` entry 7;
> `GRUT_MODEL_FRAMEWORK.md` §5).

Two grading remarks, both from the register:

- **The decoherence *rate* is the genuinely differentiating output.** The rung6 node's
  differentiator field is explicit: "Decoherence RATE is differentiating; Born rule
  FAILS-DIFFERENTIATION (inherited postulate)." A bath with GRUT's declared kernels
  produces specific rates, and rates are in principle measurable — which is exactly why the
  program's one proposed quantum observable (§7) is a decoherence-rate structure and not
  anything deeper.
- **Basis selection is not outcome selection.** This is the load-bearing boundary of the
  whole chapter, and the record draws it in one sentence (`NO_GO_LEDGER.md` entry 7): the
  reduction reproduces the Schrödinger core plus environment-induced decoherence that
  selects a pointer *basis* — but a preferred basis is **not** outcome selection. That
  boundary is §5.

The record contains no in-house pointer-basis computation for a concrete system — no
worked model exhibiting einselection dynamics from GRUT's specific kernels, beyond the
energy-basis rate analysis of §7. The pointer-basis claim is cited standard machinery
(Feynman–Vernon; Calzetta–Hu) applied to declared inputs, and this book grades it exactly
so: RECOVERED, not DERIVED.

---

## 5 · The Born measure: the never-sorted door

Here is the chapter the corpus is contractually obliged to write honestly, because the
temptation to blur it is the oldest failure mode in the decoherence literature.

Decoherence, run to completion, delivers a reduced density matrix diagonal in the pointer
basis. What it does **not** deliver is the probability that any particular diagonal entry
is *the outcome*. GRUT does not produce the Born measure. It inherits it.

> **STATUS: ASSUMPTION (inherited axiom; the improper-mixture objection stands)** —
> canonical claim 10 (source: `provenance/claims.json#born_rule`,
> `provenance/claims.json#rung6_qm_limit`, `NO_GO_LEDGER.md` entry 7,
> `POSTULATE_MAP.md` Bin 1 item 3).

The improper-mixture objection, as the record states it and as standard-physics background
fills it in: a reduced density matrix that is diagonal in some basis is an *improper*
mixture — it arises from tracing out entanglement, not from classical ignorance over
outcomes that have already happened. Reading its diagonal entries as probabilities of
single outcomes presupposes exactly the probability interpretation one was trying to
derive. Decoherence plus a pointer basis is *necessary but not sufficient*; the |ψ|²
weighting must come from elsewhere (`NO_GO_LEDGER.md` entry 7, "spec for a completion").

The register's bookkeeping around this is unusually careful and worth reproducing, because
it is the difference between hiding an assumption and displaying one:

- The Born rule is a **first-class register node** (`born_rule`, tier `assumed`,
  grut_standing `borrowed`), promoted 2026-07-06 precisely so the borrow would be *visible
  and edged*: rung6_qm_limit formally `depends_on` born_rule. An import you can see in the
  dependency graph cannot be laundered.
- The node carries **ledger_delta 0** — not because it is free, but because its +1 cost is
  already counted inside rung6's declared +2; carrying it twice would double-count, and the
  register's blind-sum auditor cannot catch double counts, so the humans did.
- Its overturning computation is stated: a derivation of the Born rule *from* S_IF without
  assuming it would promote borrowed → derived. "None exists; GRUT imports it."
- `POSTULATE_MAP.md` sorts it into **Bin 1 — irreducible primitives**: not an open layer
  with a path to derivation, but bedrock, alongside the responsive-medium ontology and the
  Past Hypothesis. "Anything claiming to derive one of them is laundering."
- The program freeze flags it with a distinct shade of honesty: the Born measure "never
  once entered any campaign's sort" (`GRUT_PROGRAM_FREEZE.md` §3) — every other primitive
  was attacked, audited, or triangulated at least once; this one was declared and then left
  standing. It is the framework's never-sorted door, and the freeze says so.

One meta-note completes the picture. The freeze's own falsification section
(`GRUT_PROGRAM_FREEZE.md` §6) lists "a demonstrated second discharge row anywhere
(einselection, Born-measure sort, CLPW outcome A)" as something that would *break* the
consolidated record's conservation pattern — the finding that every closure consumed an
input. A successful derivation of the Born measure from decoherence would therefore not
merely upgrade one node; it would overturn the program's central consolidated claim. The
record has priced its own refutation.

---

## 6 · Measurement and interpretation: the absence map

What does GRUT say about the measurement problem? The honest answer, and the record's own
answer, is: **it inherits it, unsolved.** "GRUT recovers quantum mechanics as a limit, not
a derivation: the rate is earned, the Born rule is borrowed. The measurement problem is
inherited, not solved" (`NO_GO_LEDGER.md` entry 7, calibration).

The absence map, itemized — each line an explicit statement that the record is silent,
which the charter counts as valid content:

- **No interpretation is adjudicated.** The record contains no node, computation, or ruling
  selecting Everett, collapse, pilot-wave, relational, or any other interpretation of the
  quantum state. The words do not appear as claims anywhere in the register.

  > **STATUS: UNMAPPED (the record contains no GRUT account of interpretation selection)**
  > — source: absence verified against `provenance/claims.json` (74 nodes) and the
  > repository's consolidation documents.

- **No collapse mechanism is proposed.** GRUT's noise kernel decoheres; it does not
  collapse. The framework's one contact with the collapse-model literature is
  *adversarial*: the rung8 signature is defined by its *distinction* from Diósi–Penrose
  and CSL (§7), not by membership in that family.
- **No Bell-inequality, contextuality, or entanglement-structure account exists.** No node
  covers nonlocal correlations, CHSH structure, or entanglement thermodynamics.

  > **STATUS: UNMAPPED** — source: absence verified by repository-wide search; nearest
  > contact is the Gisin-signalling caution attached to nonlinear extensions in
  > `rrt0/RRT1_REDUCIBILITY_CORRECTION.md` §5 (branch `rrt0-phase2`), which is a fence,
  > not an account.

- **The double-slit founding hypothesis is deferred as analogy-only.** The founding-era
  hope that GRUT yields a unique double-slit observable (H3) was screened 2026-06-27: the
  original two-state mapping had no operator, coupling, or observable behind it — standard
  complementarity accounts for everything invoked — and the one steelman
  (Casimir-modified interferometry) is killed by GRUT's *own* rung8 result: the vacuum
  coupling decoheres in the energy basis (the wrong basis for a double-slit), samples
  S(0) = 0, and the surviving wedge is 7–47 orders below detectability. H3 becomes a GRUT
  claim only if a unique observable distinct from standard QM is exhibited; none has been.

  > **STATUS: UNRESOLVED (deferred; analogy-only absent a unique observable; register
  > tier `to-derive`, disposition deferred)** — source:
  > `provenance/claims.json#founding_h3_doubleslit_anchor`.

  A vocabulary annotation attached to that node binds this whole corpus: the "specialist,"
  "referee," and "overseer" passes recorded across the register are in-house AI sessions
  run by the program's own human author from clean contexts; no outside human has ever
  been contacted by this program. The register carries the annotation rather than renaming
  the history — the drift is itself the finding.

What GRUT *positively* offers the measurement discussion is exactly one thing: a unified
home for the decoherence half. The same N, the same KMS lock, and the same passivity
structure that govern dissipation and gravitational response also govern which basis
survives monitoring — one architecture across sectors, with the outcome problem left
standing exactly where standard decoherence theory leaves it.

---

## 7 · Gravitational decoherence: the rung8 hypothesis

This is the book's one hypothesis, and it must be read with its label welded on. The record
calls it the USL shape signature (the register's name for the rung8 gravitational-
decoherence signature; the record does not expand the acronym).

**The proposal.** Take GRUT's noise kernel N and let it drive the Anastopoulos–Hu (2013)
gravitational-decoherence master equation (arXiv:1305.5231, the record's cited source).
The result is a decoherence signature distinguished from Diósi–Penrose and CSL **in shape
only**: AH-type decoherence acts in the **energy basis**, whereas DP/CSL localize in
**position**. Born–Markov reduction of the influence action gives, for coherence between
energy eigenstates split by ΔE (`calc/RESULTS_energy_basis.md`):

    Γ(ΔE) = (1/ħ²) |A_nm|² S(ΔE/ħ)

— the rate samples the vacuum noise spectrum at the Bohr frequency of the energy gap, with
a predicted parameter-free *shape* g(ΔE): suppressed rise, peak at ΔE = 1.22 ħω_c, FWHM
ΔE ∈ [0.69, 1.85] ħω_c, then cutoff. The experimental wedge is orthogonal by construction:
vary ΔE at fixed Δx and GRUT-AH responds while DP/CSL stay flat; vary Δx at fixed ΔE and
DP/CSL respond while GRUT-AH stays flat.

> **STATUS: HYPOTHESIS (proposed phenomenological relation; shape-only; magnitude verdict
> quiet-or-faint)** — canonical claim 12 (source: `provenance/claims.json#rung8_falsifier`,
> tier `to-derive`; `calc/RESULTS_energy_basis.md`; `GRUT_MODEL_FRAMEWORK.md` §5).

**What is staked, not predicted.** The register declares +2 inputs on the node: (i) the
overall amplitude/coupling normalization κ, which must survive the
MICROSCOPE/LISA-Pathfinder/Donadi bounds, and (ii) the cutoff scale ω_c that places the
energy-gap peak — which is what the retired "689 Hz, parameter-free" claim really was.
The shape and the energy-vs-position wedge are proposed as consequences; the amplitude and
the peak location are staked.

> **STATUS: ASSUMPTION (two staked inputs, +2: amplitude κ and cutoff ω_c; the '689 Hz
> parameter-free' billing is RETIRED on the record)** — source:
> `provenance/claims.json#rung8_falsifier` ledger_note; `calc/RESULTS_energy_basis.md`.

**The magnitude verdict — quiet-or-faint.** The Q1 computation
(`calc/q1_energy_basis_magnitude.py`, 2026-06-25) asked the decisive operator-algebra
question: does the effective gravitational coupling A carry nonzero Bohr-frequency
components, [A, H_S] ≠ 0? The answer, computed ratio-first: the *dominant* coupling is the
diagonal T⁰⁰ ~ energy density, which commutes with H_S and therefore samples S(0) = 0 —
the responsive vacuum is a **quiet** bath for static energy superpositions (Γ = 0). The
wedge-carrying off-diagonal couplings T⁰ⁱ/Tⁱʲ (~v/c) survive but land **7–47 orders of
magnitude below current sensitivity**; observability would require staking the noise
amplitude ~10⁷ or more above its natural value — a tuned number at the current
matter-wave bound. The robust Pikovski time-dilation decoherence does work, but it is
position-basis — the same axis as DP/CSL, not the wedge. The falsifier does not carry the
program.

> **STATUS: CLOSED (computed magnitude verdict quiet-or-faint — the no-go ledger's
> INVISIBLE-BY-SUPPRESSION strength; the node itself stays register-tier `to-derive` with
> a named gray-zone check pending: any leading-order off-diagonal energy coupling sampling
> S(ΔE) at O(1)?)** — source: `provenance/claims.json#rung8_falsifier` tier_note and
> differentiator; `NO_GO_LEDGER.md` entry 4; instruments
> `calc/q1_energy_basis_magnitude.py`, `calc/energy_basis_decoherence.py`.

**Scope fences the record itself carries, reproduced here because they travel with the
claim:**

- *Cutoff convention (Ruling A, 2026-08-23):* the calculation uses the staked tabletop
  cutoff ω_c = 2π·689 rad/s; there is no universal ω_c — every calculation must name its
  cutoff; spectral claims are scoped to ω ≪ ω_c, and the vicinity ω ~ ω_c is outside the
  declared validity domain.
- *The spectral shape rides on an open anchor.* The finite-T shape check
  (`calc/finite_T_exponent.py`: S(ω) analytic at ω = 0, no second slow pole within the
  analytic class) is confirmed, conditional on the analytic class holding and no second
  bath scale — but the pole-vs-cut anchor itself is open. The qualitative
  energy-vs-position wedge never depended on it; the quantitative shape does.

  > **STATUS: UNRESOLVED (anchor-class, derived-pending; pole-vs-cut open; the Tier-4
  > computation found a CUT, not a pole, at flat scope)** — canonical claim 4 (source:
  > `provenance/claims.json#rung3_single_pole`).

- *The BMV entanglement-witness backup is WITHDRAWN* — an energy-basis decoherer may not
  degrade a position-basis witness; recompute or drop. It has not been recomputed.

**The standard the shape-claim must eventually meet.** The record's own structural-theory
adjudication (`RAI_STRUCTURAL_THEORY_SEARCH.md` §6) identifies the one historical instance
of a foundations-level structural claim killed by an experiment: the **parameter-free
Diósi–Penrose model, excluded at Gran Sasso** — the template, not the outlier
(`GRUT_MODEL_FRAMEWORK.md` §5 carries the same context line). That is the bar. DP in its
parameter-free form made a magnitude claim and died by it; GRUT's rung8, in its current
quiet-or-faint state, makes a shape claim whose magnitude sits 7–47 orders below reach and
whose amplitude is staked, not derived. Until the gray-zone check or a new mechanism lifts
the magnitude into a distinguishable regime, the USL signature is a hypothesis that cannot
yet be killed the way DP was killed — which, by the program's own lights, is a *deficit*,
not a safety. The framework's weakening conditions (`GRUT_MODEL_FRAMEWORK.md` §8)
explicitly include "the USL shape-signature excluded in the regime where it is
distinguishable" — the record wants this claim exposed to fire, and it currently is not.

---

## 8 · The linear-universe response no-go (the RRT arm)

The strongest quantum-sector result in the record is a negative one, and it was found by
the program's own adversarial arm running against itself. It lives on the sibling branch
`rrt0-phase2` (working tree `/Users/mpg/Desktop/testing`), and its provenance discipline
is part of its content.

**What RRT-0 was.** A pre-registered, frozen-before-simulation hostile test
(`rrt0/RRT0_SPEC.md`): a d = 4 closed unitary toy universe (GUE Hamiltonian, density
matrices, integer update steps), a pre-registered internal intervention family
E_α(ρ) = U^τ((1−λ)ρ + λσ_α)U^(−τ), an influence statistic Φ, and frozen decision gates —
run under a claim firewall (`rrt0/RRT0_CLAIM_BOUNDARIES.md`) that marks every output
UNBANKED / PRE-REGISTERED / EXPLORATORY, **NOT GRUT evidence**, with a CI test that fails
any output document claiming more.

**What it found.** The intervention influence statistic is *fully reducible*: for the
registered class, Δρ(t,τ) = U^τ(E[ρ₀(t)] − ρ₀(t))U^(−τ) exactly, residual identically zero
(`rrt0/MODEL_CLASS_VERDICT.md` — derived in preflight, registered before any battery run).
Raw Φ is a propagation/response diagnostic, not a diagnostic of irreducible emergence.

**What the correction made of it.** The RRT-1 design audit initially claimed the no-go
rested on invertibility and that a general CPTP channel escapes it. Both claims were
caught false by the owner and corrected on the record
(`rrt0/RRT1_REDUCIBILITY_CORRECTION.md`). The generalized identity is one line from
linearity alone: for ANY linear map 𝒯 on operators, any intervention E, any step count n,

    Δ_n := 𝒯ⁿ(E[ρ]) − 𝒯ⁿ(ρ) = 𝒯ⁿ((E−I)[ρ]).

The exact load-bearing assumptions: 𝒯 linear; E linear or affine; readout linear
(Tr[B·]). **Not required:** invertibility, unitarity, trace preservation, complete
positivity, a semigroup property, a fixed point. Numerical confirmation at machine zero
(residuals ≤ 9.5×10⁻¹⁷) on genuinely non-invertible channels — depolarizing, non-unital
amplitude damping, full rank-collapsing reset — and on Lindblad evolution e^{t𝓛} for
arbitrary generators.

> **STATUS: DERIVED (RRT arm: intervention response reducible for all linear dynamics;
> escaped only by nonlinearity)** — canonical claim 20 (source:
> `rrt0/RRT1_REDUCIBILITY_CORRECTION.md` and `rrt0/MODEL_CLASS_VERDICT.md`, branch
> `rrt0-phase2`; consolidated in `GRUT_PROGRAM_FREEZE.md` §3 DERIVED list).

**The P1–P4 separation** — the correction's lasting conceptual contribution, because the
design audit had conflated the first two:

| proposition | statement | holds iff |
|---|---|---|
| **P1** response reducibility | Δ = 𝒯ⁿ((E−I)ρ) | 𝒯, E, readout linear — invertibility plays NO role |
| **P2** state recoverability | ρ₀ recoverable from ρ_t | 𝒯 invertible — this is where invertibility lives |
| **P3** asymptotic-structure reducibility | attractors/pointer/DFS reduce to Fix(𝒯) and the peripheral algebra | a function of 𝒯's spectral data |
| **P4** operator-algebra reducibility | emergent preferred algebra = a function of the generator's algebra | governed by Fix/Comm{L_a} |

RRT-0 tests P1, and P1 is escaped **only by abandoning linearity** — of the dynamics, the
intervention, or the readout. Nonlinear quantum dynamics is non-standard and carries its
own no-gos (Gisin signalling), so the escape hatch is named, fenced, and expensive
(Fork B); the recommended successor question (Fork A) keeps linearity and asks the P3/P4
question instead, itself predicted to yield another no-go class.

> **STATUS: DERIVED (analytic correction audit: the four-proposition separation and the
> corrected minimum escape condition — loss of linearity, not invertibility)** — source:
> `rrt0/RRT1_REDUCIBILITY_CORRECTION.md` §§1–4.

**What this means for quantum reality in GRUT.** Three things, in descending order of
comfort:

1. **Every "emergence" reading of intervention response within linear quantum mechanics is
   closed.** Any claim that a linear open quantum system — unitary, dissipative, CPTP,
   Lindblad, GRUT's reduced dynamics included — exhibits intervention-response structure
   beyond what its supplied 𝒯, E, and readout encode, is false by identity. The program's
   own P1 emergence framing is listed among the killed in `GRUT_PROGRAM_FREEZE.md` §4.
2. **This is deflationary for GRUT, and the record insists on that reading.** The no-go is
   broader than designed — a property of the entire linear dynamical universe — so it
   confers no distinction on GRUT. What it forbids, it forbids for everyone; what it
   leaves, it leaves for everyone. The claim-boundary firewall (NOT GRUT evidence) and the
   freeze's consolidation coexist without tension: the theorem is banked as *mathematics
   the program produced*, not as *support for the program's physics*.
3. **What cannot be concluded** is fenced in the correction itself: not that open systems
   lack interesting structure (P3 attractors, pointer states, and decoherence-free
   subspaces all exist — they are functions of the supplied 𝒯); not that nonlinearity
   *would* yield irreducible organization (unknown; only that it is the sole P1 escape);
   nothing about the half-line/KMS residue; no transfer of RRT-0's passes to any new class.

The RRT-0 arc's procedural record is also part of this book's evidence about *how* the
program treats quantum claims: five consecutive self-refusals on the record — semantic
PASS, reducibility PASS, mirror PASS (bit-exact), sector UNRESOLVED, CPR reference ABSENT
(6/6 seeds) — followed by the broadening of the no-go (`GRUT_PROGRAM_FREEZE.md` §7;
reports under `rrt0/reports/`). Even the final reducibility-gate rerun carries its own
correction on its face: a 2026-09-06 audit found the prior gate's independent propagator
route mathematically invalid (a Hermitian-only eigensolver applied to a non-Hermitian
unitary), superseded it with two valid routes, preserved the failed artifact with zero
evidentiary status, and re-passed at max residual 2.7×10⁻¹⁴ over 15,120 cases
(`rrt0/reports/REDUCIBILITY_GATE.json`, SUPERSEDED_AUDIT block). The instrument corrects
itself in public. That habit, not any quantum mechanism, is what the record offers as its
contribution to quantum foundations.

---

## 9 · What would move this book

Every claim above names its own overturning condition; collected, they are the book's
forward edge — none is scheduled, and none may be presumed:

- **A derivation of the Born measure from S_IF without assuming it** promotes the borrowed
  node to derived — and simultaneously breaks the freeze's consolidated
  "every-closure-consumed-an-input" record (§5, §6 above). Highest stakes, no known route.
- **Failure of the Schrödinger recovery in the noise-free limit** would break rung6's
  recovery clause (the node's own overturning computation). No indication exists.
- **The rung8 gray-zone check**: a leading-order off-diagonal energy coupling sampling
  S(ΔE) at O(1) would lift quiet-or-faint and make the USL shape signature testable — at
  which point it faces the Gran Sasso standard. Conversely, exclusion of the shape in a
  regime where it is distinguishable is a named weakener of the whole framework
  (`GRUT_MODEL_FRAMEWORK.md` §8).
- **A Fork-B construction** — declared, firewalled nonlinearity in dynamics, intervention,
  or readout — is the only route by which intervention response can become irreducible.
  The stopping rule governs: no new generation merely because the previous one failed; an
  independently motivated principle naming a phenomenon the linear framework cannot
  represent must open the door (`GRUT_PROGRAM_FREEZE.md` §§1, 5).
- **A unique double-slit observable computable from GRUT** would revive H3 from deferral.
  None has been exhibited.

---

## Sources drawn from

- `books/CORPUS_CHARTER.md` (status vocabulary; canonical claims 1, 2, 4, 10, 11, 12, 20, 21)
- `GRUT_MODEL_FRAMEWORK.md` (§§2–5, 7–8 — the frozen QM/USL summary this book stays consistent with)
- `GRUT_PROGRAM_FREEZE.md` (§§1–7 — ledger, stopping rule, RRT-0 arc consolidation)
- `provenance/claims.json` — nodes `rung6_qm_limit`, `rung8_falsifier`, `born_rule`,
  `rung1_inin_formalism`, `rung2_kms_gate`, `rung3_single_pole`, `rung5_gr_limit`,
  `u1_form_universality`, `founding_h3_doubleslit_anchor`, `emergence_chain`
- `provenance/sources.json` (external citations: `feynman_vernon1963`, `calzetta_hu_book`,
  `calzetta_hu_ctp1988`, `schwinger1961`, `keldysh1964`, `callen_welton1951`, `kubo1966`,
  `born1926`, `anastopoulos_hu2013` [arXiv:1305.5231], `bassi_rmp2013`)
- `NO_GO_LEDGER.md` (entries 4 and 7)
- `POSTULATE_MAP.md` (Bin 1 item 3; modular decomposition M4/M6)
- `S_IF.md` (the action, kernel structure, structural conditions)
- `calc/RESULTS_energy_basis.md`; `calc/RESULTS_arrow.md` (master-equation input context)
- `docs/WHERE_IT_STOPS.src.md` (§I.2, Nakajima–Zwanzig factorization input)
- `RAI_STRUCTURAL_THEORY_SEARCH.md` (§6 — the Gran Sasso DP-exclusion template)
- `GRUT_NEXT_STEPS.md` (USL shape-signature forward items)
- Branch `rrt0-phase2` (working tree `/Users/mpg/Desktop/testing`):
  `rrt0/RRT1_REDUCIBILITY_CORRECTION.md`, `rrt0/RRT0_SPEC.md`,
  `rrt0/RRT0_CLAIM_BOUNDARIES.md`, `rrt0/MODEL_CLASS_VERDICT.md`,
  `rrt0/reports/REDUCIBILITY_GATE.json`, `rrt0/reports/MIRROR_CONTROL.json`,
  `rrt0/reports/SECTOR_SELECTION_FIREWALL.json`, `rrt0/reports/CPR_FEASIBILITY.json`

## Gaps in this book

1. **No interpretation of quantum mechanics is adjudicated anywhere in the record** —
   Everett, collapse, pilot-wave, relational: no node, no ruling. This book reports the
   silence; it does not fill it.
2. **The quantization/single-valuedness condition (rung6 import (i)) is a ledger line-item
   only.** No document in the record elaborates what is imported or why it takes that
   form. An audit of that import is owed and unscheduled.
3. **No in-house pointer-basis computation for a concrete system exists** — einselection is
   cited machinery; no worked model exhibits basis selection from GRUT's specific kernels.
4. **Bell-inequality structure, contextuality, and entanglement thermodynamics are
   UNMAPPED** — no GRUT account exists at all.
5. **The rung8 gray-zone check is pending** (off-diagonal energy coupling at O(1)); until
   it is run, quiet-or-faint is the standing verdict and the USL signature is untestable.
6. **The BMV witness under an energy-basis decoherer was withdrawn and never recomputed.**
7. **The rung8 spectral shape is conditional on the open rung3 anchor** (pole-vs-cut,
   analytic class, no-second-scale proviso); a cut-class resolution would force the shape
   claim to be redone.
8. **Fork B (nonlinearity) is named but wholly unexplored** — the only P1 escape has no
   construction, no model, and a standing Gisin-signalling caution.
9. **The relation between GRUT's reduced dynamics and specific laboratory master equations**
   (beyond the AH-driven rung8 lead) is not worked anywhere: no GRUT-specific Lindblad
   coefficients for any real system are on the record.
10. **This book leans on the frozen summaries for cross-sector claims** (arrow/Past
    Hypothesis → Book V; algebraic/CLPW structure → Book VIII; test governance → Book IX);
    where those books sharpen statuses, this book's cross-references inherit the audit.
