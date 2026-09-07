# BOOK X — GRUT AS A RESEARCH PROGRAM

> **WORKING DRAFT** — part of the GRUT working corpus; statuses per `books/CORPUS_CHARTER.md`;
> subject to chapter-by-chapter audit; nothing here banks.

**GRUT Books — Working Edition v1.0** · D. Ryan Grover · 2026-09-07 · release `zenodo-v1.0` · Markdown is the authoritative source; the PDF is generated from it. Drafted from the frozen record by the RAI builder (Claude, Anthropic) under owner direction — this edition is a publishing pass only: formatting, navigation, and metadata; no claim strengthened or weakened for publication.

## Contents

- [1 · What kind of object GRUT now is](#1--what-kind-of-object-grut-now-is)
- [2 · The stopping rule — the program's constitution](#2--the-stopping-rule--the-programs-constitution)
- [3 · What has actually been established](#3--what-has-actually-been-established)
  - [3.1 The DERIVED short list — "everything that actually earned the word"](#31-the-derived-short-list--everything-that-actually-earned-the-word)
  - [3.2 What is recovered — with the mandatory honesty note](#32-what-is-recovered--with-the-mandatory-honesty-note)
  - [3.3 What remains conjectural](#33-what-remains-conjectural)
  - [3.4 What is closed by computation — gate outcomes](#34-what-is-closed-by-computation--gate-outcomes)
- [4 · The working position, in layers](#4--the-working-position-in-layers)
- [5 · The register as methodology](#5--the-register-as-methodology)
- [6 · The failure history, presented as scientific content](#6--the-failure-history-presented-as-scientific-content)
  - [6.1 The reversed computations](#61-the-reversed-computations)
  - [6.2 The pass-label pattern, and the standard that answered it](#62-the-pass-label-pattern-and-the-standard-that-answered-it)
  - [6.3 The self-certification pattern](#63-the-self-certification-pattern)
  - [6.4 The asymmetric error budget](#64-the-asymmetric-error-budget)
  - [6.5 What the audits destroyed, and what survived](#65-what-the-audits-destroyed-and-what-survived)
- [7 · Comparison with GR, the Standard Model, and EFT — at the level the record supports](#7--comparison-with-gr-the-standard-model-and-eft--at-the-level-the-record-supports)
- [8 · Known failure boundaries](#8--known-failure-boundaries)
- [9 · Open problems and the roadmap — the reopening keys](#9--open-problems-and-the-roadmap--the-reopening-keys)
- [10 · What a future researcher would need to do to move any single status one notch](#10--what-a-future-researcher-would-need-to-do-to-move-any-single-status-one-notch)
- [11 · Closing statement](#11--closing-statement)
- [Sources drawn from](#sources-drawn-from)
- [Gaps in this book](#gaps-in-this-book)

---

*Book X of X. This is the closing book: what the program has actually established, what
remains conjectural, how it compares with GR/SM/EFT at the level the record supports, where
its known failure boundaries lie, and what a future researcher would have to do to move any
single status one notch. Its backbone is `GRUT_PROGRAM_FREEZE.md` — the owner-decided freeze,
its stopping rule, and its reopening conditions — read against the register
(`provenance/claims.json`, 74 nodes, sha256 `beaeb84e8a6f8468…`, read-only to this corpus).
Every substantive claim carries its status inline; the shared claims of the canonical status
table appear with their statuses verbatim. Where the record is silent, this book says so.*

---

## 1 · What kind of object GRUT now is

GRUT is carried, by owner decision recorded on 2026-09-06, as **a proposed constitutive
framework with declared primitives** — judged at the Newtonian standard, not the
derive-everything standard: *given these primitives, do the relationships among them produce
correct physics, and eventually a distinguishing prediction?* Primitives are not a defect;
**undeclared or re-billed primitives are** (`GRUT_PROGRAM_FREEZE.md` §2).

> **STATUS: ASSUMPTION (AXIOM)** — the reclassification is a governance decision about the
> standard of success, recorded as changing "the standard of success going forward," and
> explicitly *not* changing the current evidence (source: `GRUT_PROGRAM_FREEZE.md` §2).

The derivational ladder is **frozen**. The freeze document is explicit that this is "a
freeze, not a burial": the program stops climbing because the owner decided it stops — "the
only way this class of ladder ever ends" — and the conditions for reopening are written
down, "with the vote assigned to mathematics and nature rather than to the program"
(`GRUT_PROGRAM_FREEZE.md`, preamble).

Two facts frame everything else in this book. First, the register's `derived` tier holds
**0 of 74** nodes — a machine-computed fact, not a rhetorical one (histogram: shown 12,
assumed 17, derived-pending 4, to-derive 20, measured 3, postulate 14, heuristic 2, open 2;
`PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §2). What the freeze's DERIVED list contains was
earned at declared scopes by the campaign record, not by register graduation. Second, the
PREDICTED set is empty:

**The PREDICTED set.**
> **STATUS: EMPTY (nothing has earned entry; Book IX governs entry)** — canonical table
> item 21; and the emptiness has a *derived structural reason*, not a lack of searching:
> "the framework's commitment is a class, a class has no scale, and the admissible set is an
> amplitude-homogeneous cone — every route from this framework to a number runs outside it"
> (sources: `GRUT_PROGRAM_FREEZE.md` §3 PREDICTED; `docs/WHERE_IT_STOPS.md`;
> `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §6).

A research program with zero register-derived nodes and zero predictions might sound like a
program with nothing to report. The record says otherwise, in a specific way: what it has to
report is a short list of scoped derivations, a complete priced inventory of its own
assumptions, a computed refusal on its one live observable candidate, a documented failure
history with the instruments that caught it, and a set of decidable reopening tests it
cannot run on itself. That is what this book presents.

---

## 2 · The stopping rule — the program's constitution

The stopping rule is committed governance, in the owner's words, and this corpus reproduces
it verbatim because everything in the roadmap (§9) is downstream of it:

> **No new RRT generation, model class, or foundational rung will be created merely because
> the previous one failed.** A new generation is permitted only if an **independently
> motivated** physical or mathematical principle identifies a **specific phenomenon that the
> existing framework cannot represent** — never "we need X because not-X failed."
> (`GRUT_PROGRAM_FREEZE.md` §1)

Its binding corollaries, from the same section: reverse-engineering the ontology from the
desired result is barred; a supplied structure may never be re-reported as a derived one;
and the breadcrumb pattern — failure → missing ingredient → new model → new missing
ingredient — is recognized in the record as **partly self-generated**. Three campaigns
independently found the apparatus manufacturing portions of its own trail: the asymmetric
error budget (`RAI_GRUT_RESURRECTION.md`, banner), the frame-entailed null
(`RAI_DIALECTIC_CHAMBER.md` §0), and the apparatus instantiating the arrow it hunted
(`RAI_DIALECTIC_CHAMBER.md` §4). The breadcrumb trail is therefore not, by itself, evidence
of a deeper rung.

> **STATUS: ASSUMPTION (governance rule, owner-decided)** — the stopping rule is not a
> physics result; it is the program's constitution, adopted after the record showed the
> ladder partly feeding itself (source: `GRUT_PROGRAM_FREEZE.md` §1).

---

## 3 · What has actually been established

### 3.1 The DERIVED short list — "everything that actually earned the word"

The freeze's own heading. Six items, each with its scope welded on.

**(1) The H¹ = 0 four-channel cancellation theorem and Theorem II (the even-degree ladder
class).**
> **STATUS: DERIVED (the one genuinely new structural identity; carries no confirmatory
> weight for GRUT)** — canonical table item 24. Theorem II derives the Λ-identity from
> exactly two standard identities; the H¹-closure synthesis found no GRUT gate principle and
> states the deflationary consequence itself: H¹ = 0 confers nothing on GRUT (sources:
> `GRUT_PROGRAM_FREEZE.md` §3 DERIVED; `PHYSICS_LEDGER/WALL_KR_H1_PHASE8_RESULT.md`,
> `WALL_KR_H1_PHASE9_CLOSURE.md`).

**(2) The flat-scope one-loop TT kernel, with H¹ = 0 identically.**
> **STATUS: DERIVED (flat contract scope, ω ≫ H)** — canonical table item 5
> (sources: `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`;
> `GRUT_MODEL_FRAMEWORK.md` §4).

**(3) The spectral law s = 5.**
> **STATUS: DERIVED (flat scope; rejects the framework's own registered s = 3)** — canonical
> table item 6. This is a self-exclusion the program computed against its own registered
> claim; importing s = 3 anywhere afterward is filed as laundering
> (sources: `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`;
> `CLASS_C_DISPATCH_SPEC.md`).

**(4) The exact de Sitter constant retarded tail H²/4π.**
> **STATUS: DERIVED (exact dS; gapped only at conformal coupling)** — canonical table
> item 7; the surviving fixed point of every deletion test the audits ran
> (sources: `GRUT_PROGRAM_FREEZE.md` §3; `RAI_GORILLA_T1.md` XVI-G).

**(5) The passivity/cone theorems.**
> **STATUS: DERIVED (channel-diagonal orientation; no amplitude ceiling, no ratio pin)** —
> the structural reason no number ever came out of the framework: the admissible set is a
> convex, amplitude-homogeneous cone that orients channels and pins nothing
> (sources: `GRUT_PROGRAM_FREEZE.md` §3; `provenance/claims.json`
> `passivity_channel_diagonal`, tier `shown`).

**(6) The linear-universe response no-go.**
> **STATUS: DERIVED (RRT arm: intervention response reducible for all linear dynamics;
> escaped only by nonlinearity)** — canonical table item 20; "broader than designed; the
> program's cleanest theorem-grade product" (source: `GRUT_PROGRAM_FREEZE.md` §3).

And one borrowed but forced identification:

**(7) T = T_dS = H/2π.**
> **STATUS: DERIVED (within declarations: forced by Hadamard/KMS on the declared
> background)** — canonical table item 3; Gibbons–Hawking, "borrowed, zero freedom" — the
> register's only credit, and the resurrection campaign's own answer to "strongest surviving
> result" (sources: `GRUT_PROGRAM_FREEZE.md` §3; `RAI_GRUT_RESURRECTION.md` §6 answer 11).

Note what the list is *not*: none of these is a GRUT-specific selection. Items (1)–(3) are
consequences of standard identities and declared inputs at declared scopes; (4) is a
free-field de Sitter fact; (5) cuts against the program's own ability to predict; (6) is a
theorem about all linear dynamics; (7) is a fifty-year-old result "that belongs to nobody in
particular" (`RAI_GRUT_RESURRECTION.md` §7).

### 3.2 What is recovered — with the mandatory honesty note

**GR at zero-memory collapse.**
> **STATUS: RECOVERED (largely by identity; KERNEL-STANDARD, scoped)** — canonical table
> item 19. The framework reproduces standard QFT/EFT results **because its executed
> machinery IS standard machinery on the declared inputs**. Recovery-by-identity is
> compatibility, not correspondence evidence; nothing recovered counts toward PREDICTED
> (sources: `GRUT_PROGRAM_FREEZE.md` §3 RECOVERED; `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md`).

**The influence-functional / Feynman–Vernon form itself.**
> **STATUS: RECOVERED (generic; u1: the form confers no GRUT-specific content)** — canonical
> table item 1 (source: `provenance/claims.json` `u1_form_universality`).

**The type III₁ → II₁ crossed-product structure.**
> **STATUS: RECOVERED (borrowed; audited verdict B-INPUT-RELOCATION: the unexplained input
> moves, it is not discharged)** — canonical table item 23 (source: `RAI_FINAL_BOSS.md` §1).

### 3.3 What remains conjectural

**The single-pole / finite-memory kernel (rung3), the program's historically central object.**
> **STATUS: UNRESOLVED (anchor-class, derived-pending; pole-vs-cut open; the Tier-4
> computation found a CUT, not a pole, at flat scope)** — canonical table item 4. And the
> decisive scope fact travels with it: the claimed relaxation pole sits at ω ~ H₀, *inside
> the region the evaluator refuses* — "the pole was never looked for where it was claimed"
> (sources: `books/CORPUS_CHARTER.md`; `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §4).

**Finite memory time as such.**
> **STATUS: ASSUMPTION, with REVERSED history on its face (the in-house "no memory time"
> computation was reversed; exact dS free-field theory forces infinite scale-free memory)**
> — canonical table item 18 (sources: `RAI_GRUT_RESURRECTION.md` §1;
> `RAI_GORILLA_T1.md` XVI-H).

**The USL shape signature.**
> **STATUS: HYPOTHESIS (proposed phenomenological relation; shape-only; magnitude verdict
> quiet-or-faint)** — canonical table item 12 (source: `GRUT_MODEL_FRAMEWORK.md` §5).

**Evolving dark energy w(z).**
> **STATUS: HYPOTHESIS (requires the inserted, un-sourced τ₂ ~ 1/H₀, priced +2)** — the
> second half of canonical table item 13; the first half — w = −1 flat — is
> **DERIVED (within the choices x = 0 / pure-TT: the sourced cosmology statement)**
> (source: `books/CORPUS_CHARTER.md` item 13).

**The responsive-vacuum picture itself, self-recording/universal-refresh, black-hole
saturation, and "1Space".**
> **STATUS: HYPOTHESIS (SPECULATIVE tier: permitted to exist, barred from load-bearing)** —
> the freeze's own classification; 1Space is further marked **UNDEFINED** — all seven
> candidate definitions failed non-circularity (sources: `GRUT_PROGRAM_FREEZE.md` §3
> SPECULATIVE; `RAI_FINAL_BOSS.md` §4 answer 8).

### 3.4 What is closed by computation — gate outcomes

**The Γ_T parameter-free tensor-friction value (6.19e-63·H₀ at 100 Hz).**
> **STATUS: CLOSED (computed NO EFFECT; SPEC outcome REFUSE on the observable route; commits
> 2116251, 41e1af5)** — canonical table item 16. This was the one live door with a shared
> parameter and no GRUT entry; the gate ran design-first under the eleven-step protocol and
> the computation closed it. Under the freeze's stop rule the consequence is stated on the
> record: "no discriminator identified on the current record"
> (sources: `GRUT_PREDICTION_GATE_GAMMA_T.md`; `calc/RESULTS_gw_tensor_friction.md`).

**The μ = 4/3 trace-only endpoint.**
> **STATUS: CLOSED (self-exclusion: separate-universe consistency + low-ℓ ISW)** — canonical
> table item 14 (source: `GRUT_MODEL_FRAMEWORK.md` §5).

**The kernel-class discriminator at w = −1.**
> **STATUS: DERIVED (class-level; explicitly not GRUT-specific)** — canonical table item 15.
> No purely relaxational kernel crosses w = −1; only an oscillatory pole pair does. This is
> menu-scope exclusion shared by the whole passive class — which is exactly why it functions
> as a standing *kill condition* rather than a GRUT signature (sources:
> `PHYSICS_LEDGER/RUNG7_TWO_POLE_COMPARISON.md`; `GRUT_PROGRAM_FREEZE.md` §5.4).

---

## 4 · The working position, in layers

The corpus organizes the program's standing as a layered position — each layer honest about
what it hands the next. (The layering is this corpus's presentation device; the content of
every layer is the frozen record's.)

**Layer 1 — the framework.** One Schwinger–Keldysh influence action for the metric
perturbation, kernels on the Ward-surviving projector pair, causality, the KMS/FDT lock,
passivity, positivity (`GRUT_MODEL_FRAMEWORK.md` §3). The form is universal (canonical
item 1, RECOVERED-generic above); GRUT's content lives entirely in the declared choices.

**Layer 2 — the declared assumptions.** The primitives table (`GRUT_MODEL_FRAMEWORK.md` §2):
axioms (the responsive-medium stance; the system/bath decomposition in its surviving
one-sided-inclusion form; the Past Hypothesis; the Born measure), empirical inputs (the
observed time-asymmetry, the dS-like background, measured constants), and structural
selections (state, scheme, order of limits, gauge, the TT projector, Lorentz covariance of
the kernel, the background time-translation flow), each priced. Three of these carry their
canonical statuses here because they are load-bearing for everything downstream:

> **STATUS: ASSUMPTION (borrowed standard identity, enforced as a hard admission gate;
> rung2)** — the KMS/FDT lock in equilibrium; canonical table item 2.

> **STATUS: ASSUMPTION (STRUCTURAL-SELECTION — CHOSEN, unanimous five-angle interrogation;
> not forced)** — the TT-only projector (p_tt_ansatz); canonical table item 8.

> **STATUS: ASSUMPTION (one relative datum: the half-line/KMS alignment; five dressings
> audited, every closure consumed it)** — temporal orientation / the Past Hypothesis;
> canonical table item 17.

> **STATUS: ASSUMPTION (inherited axiom; the improper-mixture objection stands)** — the Born
> measure; canonical table item 10 — flagged by the audits as "the never-sorted door": it
> never once entered any campaign's sort (`RAI_DIALECTIC_CHAMBER.md` §4).

**Layer 3 — derived and recovered structures.** §3.1 and §3.2 above: the short list, each at
its declared scope, plus the recoveries with the by-identity caveat.

**Layer 4 — prediction gates, and their outcomes.** The program's rule is that nothing
enters PREDICTED except through a pre-registered gate (Book IX governs entry). The gates
that have actually run returned refusals and closures, not entries: Γ_T (CLOSED, computed
NO EFFECT), μ = 4/3 (CLOSED, self-exclusion), the two FOREST discriminator hunts, the
signature audit, and X_FLOOR (all empty; `GRUT_PROGRAM_FREEZE.md` §3 PREDICTED). The layer
above this one — earned predictions — is therefore empty, and the record's position is that
an explicit non-result, delivered by a gate that could have gone the other way, is a
first-class output of the layer. The freeze banks exactly that.

---

## 5 · The register as methodology

The methodological claim the program can defend is not "we derived the vacuum" but "we wrote
five sectors of physics in one vocabulary **with every assumption priced**." The register —
74 nodes under one dependency discipline — is the demonstration (`GRUT_MODEL_FRAMEWORK.md`
§6).

The mechanics, for a reader who wants to audit it: each node carries a tier, a statement,
`depends_on` edges, and — non-uniformly — per-claim keys (`sub_status`,
`boundary_condition`, `tier_note`) where qualifying answers often live; reading only the
tier is a documented failure mode ("field blindness," `PHYSICS_LEDGER/ROOT0_FOUNDATION_AUDIT.md`
stamp item 5). Declared inputs carry a `ledger_delta` — an explicit epistemic price (e.g.
the in-in formalism bundle at +4, the TT projector at +1) — and the net figures are, by
house rule, never typed by hand into prose: they ride generated artifacts
(`provenance/emit_public_numbers.py` → `PUBLIC_NUMBERS.md`) so that a stale count is
detectable on its face rather than silently authoritative (`RUNG3_KEYSTONE_MAP.md`,
preamble; `PUBLIC_NUMBERS.md` header).

> **STATUS: DERIVED (about the record, not about nature)** — that the register's `derived`
> tier holds 0 of 74 nodes, and that the pricing discipline is machine-enforced, are
> computed facts about the repository (source: `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §2).

Two limits of the methodology, on its own record. First, the pricing discipline does not
verify physics: the gate "verifies discipline, not truth — a physically wrong but
well-provenanced claim passes" (`GRUT_V1_PLAIN.md`). Second, the discipline itself missed
things for months — the register lacked foliation/clock vocabulary, which is how a
two-clocks comparison passed two pre-registrations (`RUNG3_KEYSTONE_MAP.md` §6.2), and a
load-bearing input (the system/bath mode partition) went entirely undeclared through the
D1–D5 declaration sheet until ROOT-1's countermodel exposed it
(`PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §8).

---

## 6 · The failure history, presented as scientific content

This section is not an apology. The program's transferable asset — by the blind
adjudicator's verdict, quoted in the freeze — is "the method, not the physics," and the
method *is* this failure history plus the instruments that caught it
(`GRUT_PROGRAM_FREEZE.md` §7).

### 6.1 The reversed computations

**The tt_worldline decay — the flagship negative — was wrong and wrong-signed.** The
reported ⟨h²⟩ decay 127 → 0.002 rested on a spurious 1/(a₁a₂) in the mode-function
prefactor; independently recomputed in two formulations agreeing to 10⁻¹³, the corrected
correlator asymptotes to a constant in a fixed comoving band and **grows** under
comoving-IR/physical-UV. The sole validation gate sat at t = 0 — the unique point where
buggy and corrected code agree to machine precision. "A check placed at the unique point of
blindness is the signature of a gate written to pass"
(`RAI_GRUT_RESURRECTION.md` §1; `RAI_GORILLA_T1.md` XVI-B).

> **STATUS: REVERSED** — an in-house result overturned by corrected analysis; part of model
> history, stated on its face. The defective file is deliberately *not* patched (provenance
> preserved); its 16-file fan-out is flagged for re-adjudication.

The consequence is canonical item 18 above: what exact dS free-field theory forces is
**infinite, scale-free memory — the opposite shape of the original bet**
(`RAI_GORILLA_T1.md` XVI-H).

### 6.2 The pass-label pattern, and the standard that answered it

The record's most instructive recurring instrument defect: a gate whose passing criterion is
a label, a string, or an identity — so that the verdict is definitional rather than earned.
The record counts its occurrences explicitly up through the seventh (the sixth: an
"exhaustion gate" passed on junk because R := C1 − 2u·C0 made the check an identity,
`PHYSICS_LEDGER/WALL_KR_H1_PHASE9_CLOSURE.md`; the seventh, twice-stamped: a non-falsifiable
`gate(True)` headline in `PHYSICS_LEDGER/FOREST_PHASE10_RESULT.md`, and ROOT-0's
string-presence verdict criteria, `PHYSICS_LEDGER/ROOT0_FOUNDATION_AUDIT.md` stamp item 4).
Beyond the counted seven, the later campaign records add at least four more instances that
carry no ordinal: the Gorilla T1's own first-draft battery, caught re-committing the defect
"one block below the docstring confessing it" (`RAI_GORILLA_T1.md` §0); the pinned verdict
literals in the two committed predecessor instruments, recorded as standing defects
(`root1_kernel_origin.py:120-123`, `rai_grut_resurrection.py:127`); a pass-label
configuration in `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md`; and the Γ_T gate's margin
check, "the pass-label pattern in miniature, caught pre-commit"
(`calc/RESULTS_gw_tensor_friction.md`). Counting the stamped ordinals and these recorded
instances, the pattern's tally on the record stands at **eleven or more**.

> **STATUS: DERIVED (about the record)** — each instance is committed with its catch; the
> aggregate count above is this book's enumeration of those committed instances, not a
> figure any single artifact types.

The answer, now standing: the **journal-read, de-pinned instrument standard**. Verdicts flow
journal → record; gates assert only (i) well-formedness and (ii) that the record states
whatever the journal says — a different scientific outcome changes the record, not the
battery result; no gate asserts which verdict passes; magnitude findings are reported, never
gated (`RAI_GORILLA_T1.md` §0; `calc/RESULTS_gw_tensor_friction.md`, closing note). Beside
it, the **N1–N10 negative-control standard** — built after the discovery that "for a
negative, error moves the answer *toward* the claim — a null is the generic output of a
broken instrument — so guards aimed at the claim go quiet" (`RAI_GORILLA_T1.md` XVI-A).

### 6.3 The self-certification pattern

Four defects, one shape: **the thing that certifies sitting inside the thing being
certified**. Grades traveling inside the documents they grade (sixth occurrence of that
sub-pattern, both chamber lineages, `RAI_DIALECTIC_CHAMBER.md` §5); ROOT-0's battery, 18 of
45 gates checking that the document contains headings the document wrote
(`PHYSICS_LEDGER/ROOT0_FOUNDATION_AUDIT.md`); the vocabulary audit counting its own
annotation blocks as new occurrences (`docs/WHERE_IT_STOPS.md`, "The commentary that counted
itself"). The standing repair: pre-registrations immutable after hashing, results in a
separate citing file (`provenance/` screen records; house prereg rule).

### 6.4 The asymmetric error budget

The single most consequential meta-finding: positive claims in this corpus faced source
verification, deletion tests, teeth-controls, wording gates, and mutation testing —
**negative claims faced none of it** — so the apparatus produced "a systematically negative
record with nobody being biased," invisible to every self-check the program actually ran,
and found only by the first agent ever mandated to attack a negative
(`RAI_GRUT_RESURRECTION.md`, banner). Every negative verdict quoted anywhere in this corpus
carries the corresponding cap.

### 6.5 What the audits destroyed, and what survived

Destroyed, preserved rather than erased (`GRUT_PROGRAM_FREEZE.md` §4;
`RAI_DIALECTIC_CHAMBER.md` §5): the finite-memory/single-pole kernel as a *supported*
structure; the u4 "dissolution" (relocation, not derivation); s = 3; G-STRONG; both
discriminator hunts and the signature audit (empty); the PAS address ledgers and the
Direction Residue as a certified new type (decomposed — absolute orientation is gauge, one
relative datum survives); the CPR-alignment route for RRT-0 (reference ABSENT, 6/6 seeds);
the P1 emergence framing for all linear dynamics; the deflationary headline as a finding;
every universal quantifier; and, at the meta-level, three generations of the program's own
instruments — pass-label gates, story-pinned gates, the uncalibrated sorter — "each caught,
stamped, and preserved."

Survived, at full strength (`GRUT_PROGRAM_FREEZE.md` §7): **the method** —
pre-registration with hashes before results, two-sided gates, N1–N10 negative controls,
journal-read de-pinned instruments, mirror controls, preserve-the-failure, and the stopping
rule itself. RRT-0 is its finished demonstration: an apparatus that said **no** to its own
program five consecutive times, cleanly and on the record. And one sentence of physics with
its grades welded on: *on a de Sitter background, persistence came free; forgetting and
direction were always paid for* — the first clause a controlled derivation conditional on
the background; the second an induction over the examined record, whose universal form is
exactly what a one-sided apparatus is least able to check.

> **STATUS: DERIVED (first clause, conditional on the background) / HYPOTHESIS-grade
> induction (second clause, per the record's own grading)** — the grades are part of the
> sentence and may not be detached (source: `GRUT_PROGRAM_FREEZE.md` §7;
> `RAI_GORILLA_T1.md` XVII).

---

## 7 · Comparison with GR, the Standard Model, and EFT — at the level the record supports

**Head-to-head with ordinary open-system EFT, the program's own verdict.** Ordinary EFT
produces everything GRUT's executed machinery produced: the influence-functional form (u1),
the dissipative tensor sector (a named, published mainstream open-EFT graviton-friction
parameterization, not a GRUT-private construct), and the pole machinery (standard Dyson
resummation). "Nothing survives the head-to-head that ordinary EFT cannot explain"
(`PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §5). The kernel-origin verdict is the sharp form:

> **STATUS: CLOSED (gate outcome, KERNEL-STANDARD)** — why this kernel: because standard
> QFT/EFT produces it, acting on inputs GRUT declares rather than derives; with the
> mandatory scope caveat that this concerns the computed stand-in (a T = 0-graded vacuum
> exponent at ω ≫ H), *not* GRUT's claimed kernel at ω ≲ H, on which "nothing determines
> the kernel — not GRUT, not standard EFT"
> (source: `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §§1, 13).

**Against the field, from the structural-theory audit.** In the fourteen-candidate
adversarial adjudication (`RAI_STRUCTURAL_THEORY_SEARCH.md` §3), GR + SM as EFT survives
wounded as the best current structural account — SUPPORTED, not established as fundamental,
with prediction-grade confirmations no structural competitor has — while **GRUT as
currently constructed FAILS**, with the attacking agent's scoping mandatory and quoted:
"FAILS means *fails to constitute a distinctive physical theory*, NOT *the
responsive-vacuum hypothesis is FALSE*"; the underlying question stays unresolved and
computationally inaccessible. The hostile adjudicator in the same campaign overruled its own
three routes for treating KERNEL-STANDARD as a settled null: GRUT is "unevaluated at its own
claim point, not nulled there" (`RAI_STRUCTURAL_THEORY_SEARCH.md` §4).

**What GRUT organizes differently — the defensible comparative claim.** Not "GRUT proves
more," but: **a single organizing language for phenomena normally carried in separate
formalisms** — one influence-functional architecture, one KMS/FDT lock, one passivity
structure, one kernel bookkeeping spanning decoherence, dissipation and noise, gravitational
response, cosmological response, and gravitational-wave friction; the register itself is the
demonstration that the sectors *can* be written in one vocabulary with every assumption
priced (`GRUT_MODEL_FRAMEWORK.md` §6). And the reorganization made one framework-level fact
visible that the standard organization obscures — the persistence/forgetting asymmetry of
§6.5, with its grades. Whether this is *merely* a reformulation or eventually earns more is
precisely what the reopening keys decide. The record's standing template for sector-level
honesty is the KERNEL-STANDARD caveat, and `GRUT_NEXT_STEPS.md` orders the comparison
sector by sector with the instruction: "where the honest answer is 'vocabulary only,' write
that."

**Where the record is silent.** No GRUT account exists for the matter sector's structure:

> **STATUS: UNMAPPED** — flavor, strong-CP, neutrino masses, dark matter, baryogenesis;
> canonical table item 22 (source: `GRUT_PROGRAM_FREEZE.md`; `books/CORPUS_CHARTER.md`).

---

## 8 · Known failure boundaries

Where the framework's own record locates the edges of its validity:

1. **ω ≲ H is UNASKABLE, not merely unresolved** — four independent obstructions, each
   separately sufficient: the refusal boundary ω = 3.3993H is *derived* (the exact 104/9
   coefficient ratio); there is no frequency variable there without the priced
   time-translation flow; an unregulated IR log at O(H²) with nine candidate regulators
   swept and zero licensed; and the declared scheme is provably blind to dS thermality. A
   standing guard pre-refuses any future *favourable* null from the same graded calculation
   (`PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §3).
2. **The class/cone barriers** — a class has no scale; the admissible cone pins no ratio;
   every route from the framework to a number runs outside it (`docs/WHERE_IT_STOPS.md`;
   `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §6). This is why PREDICTED is empty for a
   *derived* reason, and it bounds all future prediction hunts from the start.
3. **The kernel-vs-dressed-object fork, still owed** — every classification-bearing verdict
   was read on the undressed χ = −K_R; the dressed reading lands on the opposite side of
   the pre-registered convergence boundary and trips rung1's own falsifier; no document
   carries the fork forward, and it "may already be decided in the adverse direction by a
   result the record has not caught up with"
   (`PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §11; `GRUT_PROGRAM_FREEZE.md` §3 UNRESOLVED).
4. **The undeclared partition** — the strongest successful countermodel (a Wilsonian
   system/bath partition at a comoving scale) gaps the branch point and destroys the one
   "exact, structural" result, and is admissible precisely because the D1–D5 declaration
   sheet never declared the mode partition (`PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §8).
   The framework document now declares the operative partition openly as a historically
   undeclared input (`GRUT_MODEL_FRAMEWORK.md` §2).
5. **The clock boundary** — comparisons of rates across patches are legitimate only where
   the derived clock map D1–D6 licenses them; the assembled TT response has never been
   reduced to a one-time kernel in any named clock, and that reduction is a precondition for
   pole-vs-cut even having meaning (`RUNG3_KEYSTONE_MAP.md` §§1, 3).
6. **The contested survivor** — the "no clock is forced" reading of the de Sitter state is
   contested exactly where GRUT needs it (Allen's theorem on the minimally-coupled sector),
   and the retraction of the tt_worldline support removed the computational evidence the
   primary had attached to it (`RAI_GRUT_RESURRECTION.md` §7).

---

## 9 · Open problems and the roadmap — the reopening keys

The freeze hangs five keys "where the program cannot reach them by itself"
(`GRUT_PROGRAM_FREEZE.md` §5). They are the honest roadmap; each is decidable, none is owned
by the program, and any one justifies unfreezing under the stopping rule.

**Key 1 — O2, the interacting graviton zero-mode.** The entire adverse kernel complex flows
from one exact zero (Δ₋ = 0), which sits on a measure-zero point: the campaign's own
mutation controls show any perturbation lifts it, and an interaction-induced
m_eff² = 0.1H² already returns a finite rate ≈ 0.034H through the verified
Starobinsky–Yokoyama channel. **Lifted** → the fixed point's referent falls and with it the
persistence claim; **protected** → the one surviving derived structure strengthens
materially. "The computation that would decide it is exactly the one nobody has done"
(`RAI_GORILLA_T1.md` XVI-N; `GRUT_PROGRAM_FREEZE.md` §5.1).

> **STATUS: UNRESOLVED (posed, undone; decides the fixed point's referent)** — source:
> `GRUT_PROGRAM_FREEZE.md` §3 UNRESOLVED.

**Key 2 — the RESIDUE test.** Derive the half-line/KMS alignment from unoriented hypotheses
(kills the residue framing and turns the framework's deepest axiom into someone else's
theorem), or prove the functorial no-go — the within-triple half (the no-internal-T lemma)
is proved but campaign-own, awaiting independent verification; the functorial half is
precisely posable in the GLW98 Cor 1.9 category (`RAI_FINAL_BOSS.md` §4 item 15;
`GRUT_PROGRAM_FREEZE.md` §5.2).

**Key 3 — the SLOT test.** A rigorous single-patch G_N → 0 limit (CLPW §4.3, arXiv:2206.10780)
— settles whether the clock-slot is a second irreducible input, the exact fork on which the
Final Boss's two blind sentences disagreed (`RAI_FINAL_BOSS.md` §4 items 13, 17–19).

**Key 4 — nature votes at w = −1.** Any observed crossing excludes the entire relaxational
class, GRUT included, at a stroke — the standing kill condition (canonical item 15 above;
`GRUT_PROGRAM_FREEZE.md` §5.4).

**Key 5 — an independently motivated principle** naming a specific phenomenon the framework
cannot represent — the only door through which any new rung may enter (`GRUT_PROGRAM_FREEZE.md`
§5.5).

Beside the keys, the fenced open problems that do not by themselves reopen anything: u3 (the
selection question, sharpened to three typings, with CPR's uniqueness half standing as
unconfronted counterevidence), u4 (form artifactual, content relocated), the ω ≲ H regime,
the kernel-vs-dressed fork (§8.3 — an owner decision, cheap and owed), the half-line/KMS
relative datum itself, and the Born measure's first entry into any frozen sort
(`GRUT_PROGRAM_FREEZE.md` §3 UNRESOLVED; `RAI_DIALECTIC_CHAMBER.md` §6).

The *practical* near-term program, distinct from the keys (`GRUT_NEXT_STEPS.md`):
consolidation of the presentation; re-verification of only what is central *and* touched by
known defects (the tt_worldline successor at a named prescription; the two campaign-own
derivations); the sector-by-sector comparative pass; the prediction hunt for one
quantitative consequence not encoded in the inputs — with the Γ_T candidate now closed by
computation, the remaining named candidates (USL shape; rung8 bookkeeping) each require
their own gate before any computation; and the stop rule: if no discriminator survives, "say
so, in the model document, and stop."

**And the falsification of the whole approach**, kept where it can be seen
(`GRUT_PROGRAM_FREEZE.md` §6): a self-closing description — any formalism fitting the
observed asymmetric phenomena with zero contentful undischarged inputs — falsifies the
consolidated "every closure consumed an input" record outright; a demonstrated second
discharge row anywhere breaks the conservation pattern; and if the frozen-predicate
calibration shows the consolidated claim deflates paradigm cases the way the chamber's
sorter did, the claim dies **ill-typed rather than false** — "the honest worst end."

---

## 10 · What a future researcher would need to do to move any single status one notch

The eight-status vocabulary is a ratchet with defined pawls. Concretely, per transition:

- **ASSUMPTION (STRUCTURAL-SELECTION) → DERIVED.** Exhibit an independently motivated
  principle that forces the selection — and pass the bridge test: does the new input
  *derive* the result or *relocate* the assumption? The record's standing rule prices any
  relocation as a new +1 at its point of entry; "any primacy principle is priced as a new
  input by standing ruling" (`RUNG3_KEYSTONE_MAP.md` §7;
  `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §9). For the TT projector specifically, the
  symmetry route is closed; only a dynamical bath-microphysics route survives, and it is
  ruled not-in-house (`CHARTER.md` §3, quoted in ROOT-1 §12).
- **UNRESOLVED (rung3) → resolved either way.** Perform the keystone computation: name one
  clock (D1–D6), prove or refute the stationary reduction of the *assembled* gauge-invariant
  TT response, then compute pole/cut/neither for the resummed G_R^TT — through walls A
  (graviton-probe assembly; the scalar result of arXiv:2602.07908 cannot be borrowed), B
  (the RG half of the arXiv:2409.12003 resummation deferral), and C (retarded, not in-out,
  objects). All three outcomes are first-class; predetermining the wanted one is forbidden
  (`RUNG3_KEYSTONE_MAP.md` §§3, 5).
- **RECOVERED → correspondence evidence.** Show any recovered result *fails* for some
  admissible variation of the declared inputs — i.e., turn identity into discrimination.
  Nothing on the record currently does this, which is precisely the honesty note's content.
- **HYPOTHESIS (USL shape) → a gated candidate.** Make the magnitude regime precise, then
  pre-register the gate before computing, meeting the standard the record itself names: the
  parameter-free Diósi–Penrose exclusion at Gran Sasso — "the template, not the outlier"
  (`GRUT_MODEL_FRAMEWORK.md` §5; `RAI_STRUCTURAL_THEORY_SEARCH.md` §6).
- **EMPTY (PREDICTED) → one entry.** Find a quantitative, nontrivial consequence not encoded
  in the inputs — the structural barriers say it must be a *relation between sectors*
  enforced by the common architecture, not a scale or a ratio; the cross-sector KMS lock is
  one candidate locus, not a forced one (`GRUT_NEXT_STEPS.md`, with the owner's 2026-09-06
  correction carried). Entry runs only through a pre-registered gate under Book IX's
  governance.
- **CLOSED → reopened.** Only by the specific instrument named in the closure (e.g. the
  Γ_T gate-to-readmit is itself closed as a computed refusal;
  `calc/RESULTS_gw_tensor_friction.md`), never by prose.
- **Any negative → trusted.** Rebuild it under the de-pinned, journal-read, N1–N10 standard;
  three standing negatives are marked MUST-BE-REOPENED on exactly this ground
  (`RAI_GORILLA_T1.md` XVI-A).
- **UNMAPPED → anything.** Write the sector's first GRUT account, priced at entry. The
  record contains no shortcut; an absence map is the current content.

A researcher who wants a single entry point: run **O2**. It is computationally accessible,
its channel is verified, both outcomes are decisive, and it holds the vote over the one
structure that survived every deletion test.

---

## 11 · Closing statement

What this program established, it established at declared scopes, and most of it cuts
against its own founding bet: the derived kernel rejects the registered spectral law; the
derived cone explains why no prediction ever came out; the derived no-go closes the
emergence framing the program began with; the corrected computation forces the opposite
memory shape from the one asserted. The record holds because the apparatus that produced it
was eventually made strong enough to catch itself, repeatedly, in public — and the freeze
converts that apparatus into the program's actual contribution: "That instrument — RAI — is
the program's existing contribution, independent of whether the responsive vacuum ever earns
a prediction" (`GRUT_PROGRAM_FREEZE.md` §7).

The ladder stops because the owner decided it stops. What was earned is banked as method;
what was killed stays killed; and the reopening keys hang where the program cannot reach
them by itself — with the vote assigned to mathematics and nature.

---

## Sources drawn from

- `GRUT_PROGRAM_FREEZE.md` (primary backbone: stopping rule, ledger, reopening keys)
- `GRUT_MODEL_FRAMEWORK.md` (§§1–8; especially §§6–8 for comparison and change-my-mind)
- `books/CORPUS_CHARTER.md` (status vocabulary; canonical status table, used verbatim)
- `RUNG3_KEYSTONE_MAP.md` (clock map D1–D6; walls A–C; the bridge test; deliverables)
- `GRUT_NEXT_STEPS.md` (the practical program and its stop rule)
- `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` (KERNEL-STANDARD verdict; UNASKABLE obstructions;
  cone/class barriers; the undeclared partition; the kernel-vs-dressed fork)
- `PHYSICS_LEDGER/ROOT0_FOUNDATION_AUDIT.md` (retired failed instrument; pass-label 7th
  occurrence; self-certifying battery)
- `RAI_GRUT_RESURRECTION.md` (tt_worldline retraction; asymmetric error budget; u3/u4)
- `RAI_GORILLA_T1.md` (de-pinned standard; N1–N10; XVI-G/H survivors; XVI-N; XVII)
- `RAI_DIALECTIC_CHAMBER.md` (frame-entailed null; destroyed/live lists; the Born-measure
  door; the CLPW next test)
- `RAI_FINAL_BOSS.md` (CLPW and Wiesbrock relocations; the residue; RESIDUE/SLOT tests)
- `RAI_STRUCTURAL_THEORY_SEARCH.md` (fourteen-candidate adjudication; EFT comparison;
  the foundational gap)
- `GRUT_PREDICTION_GATE_GAMMA_T.md` and `calc/RESULTS_gw_tensor_friction.md` (the Γ_T gate
  and its computed closure; the caught-pre-commit pass-label miniature)
- `PHYSICS_LEDGER/FOREST_PHASE10_RESULT.md`, `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md`,
  `PHYSICS_LEDGER/WALL_KR_H1_PHASE9_CLOSURE.md` (pass-label ordinal instances)
- `PUBLIC_NUMBERS.md` (generated register counts; the no-hand-typed-nets rule)
- `provenance/claims.json` (register; read-only; consulted for tier facts cited above)
- `GRUT_V1_PLAIN.md` ("discipline, not truth"); `docs/WHERE_IT_STOPS.md` (class/cone
  quotations; instrument-defect case studies)
- `books/BOOK_I_FOUNDATIONS.md` (cross-book consistency check only)

## Gaps in this book

1. **Book IX did not exist at the time of writing.** The canonical table assigns PREDICTED
   entry governance to Book IX; this book cites that governance by table item, not by a
   Book IX text it could not read. Reconciliation performed at corpus audit (2026-09-06):
   Book IX's actual entry rules, gate methodology, and Γ_T closure were checked against
   this book's citations and found consistent.
2. **The pass-label tally ("eleven or more") is this book's enumeration.** The record stamps
   ordinals only through the seventh occurrence; the four later instances cited are
   committed but uncounted at source. No single artifact types the aggregate, and if the
   audit disagrees with this enumeration the ordinal-stamped seven plus the Γ_T miniature
   stand independently.
3. **`PUBLIC_NUMBERS.md` is stale relative to the register** (generated 2026-08-12; counts
   73 claims and a +17 GRUT-scope net, while the frozen register holds 74 nodes). Per the
   house rule this book types no net figure; the discrepancy is visible on the generated
   file's face and is flagged here rather than resolved.
4. **The RRT-0 arc is cited from the freeze's summary only.** The sibling record lives on
   the `rrt0-phase2` branch (74e945f → 510c105), which this book did not check out; the
   five-consecutive-no characterization is quoted from `GRUT_PROGRAM_FREEZE.md` §7.
5. **The "four-layer working position" (§4) is a presentation device of this corpus**, not a
   phrase of the frozen record; every statement inside the layers is sourced, but the
   layering itself should not be cited as record vocabulary.
6. **Sector-by-sector GRUT ↔ standard comparisons are ordered but mostly unwritten**
   (`GRUT_NEXT_STEPS.md` COMPARATIVE PHYSICS); §7 here presents only what the executed
   record supports (the ROOT-1 head-to-head, the structural-search adjudication, and the
   framework's §6 organizing claim). The per-sector "what does GRUT change?" answers do not
   yet exist and are not simulated here.
7. **Two campaign-own derivations remain without independent verification** (the
   no-internal-T lemma; the CLPW parity-flip isomorphism); statements in §9 that lean on
   the Final Boss's elimination half inherit that flagged exposure.
8. **The confidence split quoted nowhere here** — the chamber's ~40/25/20/15 split on the
   conserved one-sidedness — was omitted as a judgment-call figure of one instrument; a
   future audit may prefer it included.
9. **Word-count scope**: this book compresses the failure history to its counted patterns
   and flagship cases; the full case-study inventory (e.g. the counting pair, the
   commentary-that-counted-itself) lives in `docs/WHERE_IT_STOPS.md` and is cited, not
   reproduced.
