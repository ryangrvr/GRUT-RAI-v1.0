# BOOK IX — TESTS AND PREDICTIONS

> *"WORKING DRAFT — part of the GRUT working corpus; statuses per `books/CORPUS_CHARTER.md`;
> subject to chapter-by-chapter audit; nothing here banks."*

**GRUT Books — Working Edition v1.0** · D. Ryan Grover · 2026-09-07 · release `zenodo-v1.0` · Markdown is the authoritative source; the PDF is generated from it. Drafted from the frozen record by the RAI builder (Claude, Anthropic) under owner direction — this edition is a publishing pass only: formatting, navigation, and metadata; no claim strengthened or weakened for publication.

## Contents

- [1 · The organizing fact: the PREDICTED section is empty](#1--the-organizing-fact-the-predicted-section-is-empty)
- [2 · The experimental philosophy](#2--the-experimental-philosophy)
- [3 · The entry rules: the preregistration discipline](#3--the-entry-rules-the-preregistration-discipline)
- [4 · The prediction-gate methodology, as demonstrated](#4--the-prediction-gate-methodology-as-demonstrated)
- [5 · The Γ_T closure, in full](#5--the-γ_t-closure-in-full)
  - [5.1 The candidate](#51-the-candidate)
  - [5.2 The design-time verdict](#52-the-design-time-verdict)
  - [5.3 The closure computation](#53-the-closure-computation)
- [6 · The signature audit record](#6--the-signature-audit-record)
- [7 · Candidates still standing — none gated](#7--candidates-still-standing--none-gated)
  - [7.1 The USL shape candidate](#71-the-usl-shape-candidate)
  - [7.2 The rung8 bookkeeping candidate](#72-the-rung8-bookkeeping-candidate)
  - [7.3 The interior window — a bound, not a prediction](#73-the-interior-window--a-bound-not-a-prediction)
- [8 · Failed and refused prediction routes — the graveyard, preserved](#8--failed-and-refused-prediction-routes--the-graveyard-preserved)
- [9 · Future gates and the reopening keys](#9--future-gates-and-the-reopening-keys)
- [Sources drawn from](#sources-drawn-from)
- [Gaps in this book](#gaps-in-this-book)

---

---

## 1 · The organizing fact: the PREDICTED section is empty

Every book in this corpus reserves the word *prediction* for gate-earned results, and this
is the book that governs entry. Its organizing fact can therefore be stated in one line, at
the top, where it belongs:

**The PREDICTED section of the GRUT record is empty. Nothing has earned entry.**

> **STATUS: EMPTY (nothing has earned entry; Book IX governs entry)** — canonical claim 21,
> verbatim (source: `books/CORPUS_CHARTER.md`; `GRUT_PROGRAM_FREEZE.md` §3, "PREDICTED —
> EMPTY, with the reason on the record").

This is not an apology and not a placeholder. It is a *result*, and it comes with a derived
reason, established at two levels of the record. At the structural level: the framework's
commitment is a **class** of admissible response kernels, a class has no scale, and the
admissible set is an amplitude-homogeneous cone — the passivity/cone theorems orient
channels and pin no ratio, so "every route from this framework to a number runs outside it"
(`GRUT_PROGRAM_FREEZE.md` §3). At the level of the one candidate carried all the way through
a gate: the Γ_T design table (§5 below) exposed the same fact in ledger form —

*Everything that is fixed lives where nothing is observable; everything observable-sized
runs through unresolved inputs.* In the gate's own words: "every quantity that is fixed
lives in horn (a); every quantity that could make Γ_T observable lives in horn (b) and is
unresolved. The two horns do not mix: no fixed coefficient feeds the observable-sized
number, and no observable-sized number is fixed."

> **STATUS: DERIVED (status-level: read off the gate's fixed-versus-free table and the
> freeze's cone theorems; no physics evaluated in the reading)** — the derived reason the
> PREDICTED set is empty (source: `GRUT_PREDICTION_GATE_GAMMA_T.md` §5;
> `GRUT_PROGRAM_FREEZE.md` §3).

Nor is the emptiness for lack of searching. Two FOREST discriminator hunts returned
FOREST-EMPTY ("no live register node is a working discriminator" — the second hunt
confirming the first by an independent route); the signature audit returned EMPTY across
every candidate observable; and the X_FLOOR campaign, built to ask whether anything *pins*
the interior modulus x, landed NO PIN on its computed route (R1: the anomaly's own
contribution ≥108 decades below every banked bound, the scheme piece free — "that freedom
*is* the no-pin finding") and closed its dynamics route as a classifier (the channel-diagonal
passivity lemma: a convex cone, no ceiling, no pin) (source: `GRUT_PROGRAM_FREEZE.md` §3;
`PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md`; `X_FLOOR_MAP.md`;
`calc/RESULTS_anomaly_c0_map.md`; `calc/RESULTS_x_no_pin.md`).

The rest of this book is the record of how that emptiness was established, policed, and
priced: the philosophy that assigns the votes (§2), the entry rules (§3), the gate
methodology as demonstrated (§4), the Γ_T closure in full (§5), the signature audit (§6),
the candidates still standing without gates (§7), the graveyard of failed routes (§8), and
the future gates and reopening keys (§9).

---

## 2 · The experimental philosophy

**What counts as a prediction.** On this record, a prediction is a gate-earned result: a
quantitative consequence that is nontrivial and not already encoded in the inputs, reached
through a pre-registered design that survives all five discrimination requirements (§4) and
whose computed output then survives the program's own screens. Nothing else may carry the
word. In particular, the mandatory honesty note of the freeze applies throughout: the
framework reproduces standard results *because its executed machinery is standard machinery
on the declared inputs* — recovery-by-identity is compatibility, not correspondence
evidence, and **nothing RECOVERED counts toward PREDICTED**
(source: `GRUT_PROGRAM_FREEZE.md` §3, RECOVERED note; `GRUT_NEXT_STEPS.md`, the prediction
hunt).

**Signatures versus no-go directions.** The record's standing distinction, kept on the face
of both ledgers: a *signature* is a positive distinctive observable; a *falsifiable-direction
no-go* is a statement about what the framework forbids. GRUT currently has the second and
not the first. The no-go ledger is explicit about strength calibration — its legend
(FORBIDDEN / SETTLED-NEGATIVE / EMPIRICALLY EXCLUDED / INVISIBLE-BY-SUPPRESSION / BORROWED)
is load-bearing, and the register currently banks **no genuine FORBIDDEN entry at all**;
reporting that absence, rather than promoting a settled-negative to an impossibility, is
itself part of the discipline (source: `SIGNATURE_AUDIT.md` header; `NO_GO_LEDGER.md`
legend and closing note).

**The standing kill condition.** The framework's cleanest exposure to data is a direction it
shares with an entire class: no purely relaxational kernel crosses w = −1; only an
oscillatory pole pair does. Any observed crossing excludes the whole passive relaxational
family at a stroke, GRUT included — the freeze elevates this to a formal reopening
condition ("Nature votes at w = −1").

> **STATUS: DERIVED (class-level; explicitly not GRUT-specific)** — canonical claim 15,
> verbatim: menu-scope exclusion shared by the entire passive class (source:
> `books/CORPUS_CHARTER.md`; `GRUT_MODEL_FRAMEWORK.md` §5; `GRUT_PROGRAM_FREEZE.md` §5,
> condition 4).

**The posture.** The model framework's §8 states both lists — what would strengthen GRUT
(the zero-mode returning *protected*; a §2-selection derived from an independent principle;
a gate-surviving sector consequence; the SLOT test discharging the clock-slot) and what
would weaken or falsify it (an observed w = −1 crossing; the zero-mode returning *lifted*;
a self-closing description of the time-asymmetry; the USL shape signature excluded in its
distinguishable regime; the RESIDUE test deriving the alignment from unoriented hypotheses)
— and then closes with the sentence this book adopts as its own summary of the experimental
philosophy: **"Nature and mathematics hold every one of these votes. The framework holds
none of them."** (source: `GRUT_MODEL_FRAMEWORK.md` §8, verbatim).

**The stop rule.** Behind the posture sits committed governance: no new generation, model
class, or foundational rung may be created merely because the previous one failed; and if
no discriminator survives the comparative pass and the prediction hunt, the program says so
in the model document and stops — no automatic rescue, no new rung. The reopening keys are
hung where the program cannot reach them by itself (source: `GRUT_PROGRAM_FREEZE.md` §1;
`GRUT_NEXT_STEPS.md`, stop rule).

---

## 3 · The entry rules: the preregistration discipline

The methodology below is enforced, not aspirational, and it exists because the program
caught itself violating it — repeatedly, in one recurring shape.

**Immutability after hashing.** Every pre-registration is immutable once hashed
(`provenance/prereg/MANIFEST.txt` carries the seals); results live in **separate files**
citing the seal in the pinned `sha256 = <64hex>` format; editing any sealed file breaks the
verification check. And the record is explicit about what a green run means: the
*discipline* holds — declarations complete, seals intact, guards firing. "It does not
certify physical truth — a wrong-but-well-provenanced claim passes, and the register says
so about itself" (source: `HOW_TO_VERIFY.md` §§3–4).

**The self-certification pattern.** The reason results must live outside the files that
pre-register them is that the program's audits found multiple defects with a single
structure: *the thing that certifies sitting inside the thing being certified* — a selftest
whose answer lived in its own print statement; a ratchet computed from the very list it
existed to bound; results appended to the pre-registration they were meant to be tested
against. Each was caught only by an outsider constructing a case the author's own controls
had already certified as clean. The remedy adopted program-wide: move the certifying thing
outside — an external hash, a hardcoded literal, a separate file, an adversary who did not
write the answer (source: `STAGE_CLOSE_2026-08-09.md`; `AGENT_COORDINATION.md`, the
"standing self-certification pattern").

**The instrument standard.** The freeze's §7 lists what the method earned as its
transferable asset: pre-registration with hashes before results; **two-sided gates**;
negative controls to the N1–N10 standard; **journal-read, de-pinned instruments** (an
instrument must extract the statuses it adjudicates from the record at runtime, never carry
them pinned in its own text); mirror controls; preserve-the-failure; the stopping rule
itself. The same section records the price of learning this: **the audit apparatus itself
was caught three times** — pass-label gates, story-pinned gates, the uncalibrated sorter —
each generation of instrument caught, stamped, and preserved rather than erased (source:
`GRUT_PROGRAM_FREEZE.md` §§4, 7).

**The pass-label lesson, recurring and caught again.** The pass-label pattern — a gate whose
"pass" is defined so that only the desired answer can pass — recurred in the Γ_T closure
instrument itself and was caught pre-commit by the SPEC-compliance checker: the script
contained a margin *gate* that hard-failed unless the result landed ≥50 orders below the
bound. It was rebuilt as a report-never-gate branch, and the final instrument's gates
"assert well-formedness, arithmetic identities, and extraction success only — no gate
asserts which verdict passes, and magnitude findings are reported, never gated" (source:
`calc/RESULTS_gw_tensor_friction.md`, adversarial verification, defect 1 and closing line).

**The discipline demonstrated on a data gate.** The low-ℓ TT-auto gate on the interior
modulus x is the record's fullest demonstration that the firewall machinery works on
data-facing instruments too: the first frozen version was **voided the same day by the
program's own firewall** (a Bessel-recurrence bug made every headline constant noise — the
"edge" moved by a factor of ~8 on one resolution doubling), then rebuilt, verified against
an independent harness, and legally re-frozen under a written amendment record A1–A7.

> **STATUS: DERIVED (instrument-grade data gate, re-frozen after its first freeze was
> voided by its own firewall; unconditional most-conservative-corner bound x < 0.358; the
> κ-filter is the entire systematic; the A6 Boltzmann-grade differential check is OWED
> before any κ=3 kill-grade use)** — (source: `calc/RESULTS_isw_tt_auto.md`;
> `calc/isw_tt_auto.py`).

**The entry rule this section adds up to.** For a claim to enter the PREDICTED set it must
pass through a design-first gate of the §4 kind, reach DISCRIMINATING on all five
requirements, and then have its computation survive the same screens as everything else —
the SPEC template says it on its face: "Nothing here banks; the output needs the four-lens
screen and the bank gate like anything else" (source: `calc/SPEC_gw_tensor_friction.md`
preamble). No such claim currently exists.

---

## 4 · The prediction-gate methodology, as demonstrated

The record contains exactly one prediction gate executed end-to-end:
`GRUT_PREDICTION_GATE_GAMMA_T.md` (2026-09-06, owner-ordered), run **design-first** — every
verdict-shaped statement preceding computation is derived from the *statuses* of register
inputs, not from values. Its structure is the program's demonstrated protocol for any
future candidate.

**The eleven steps**, as the gate instantiates them:

1–2. Read the record — every source the candidate touches, listed on the gate's face.
3. Name what the candidate connects — which registers of the program the slot joins.
4. Write the governing equation *before any calculation*.
5. Write the baseline — GR, and every standard parameterization the slot is degenerate with.
6. List **every** input entering the calculation, each with its register status.
7. Sort fixed versus free — what is genuinely pinned, what is staked/inserted/chosen.
8. Establish the licensed frequency/IR domain — where the record permits evaluation at all.
9. Test absorbability — can existing parameters (α_M, the free open-EFT slot) mimic it?
10. Pre-register the decision tree, before any evaluation.
11. Render the gate verdict — at design time, from statuses alone, where that is decidable.

**The five-outcome decision tree** (step 10, declared before evaluation): verdicts are
**DISCRIMINATING / DEGENERATE / UNDERDETERMINED / OUT OF VALID DOMAIN / NO EFFECT**,
rendered **per horn and never composed into a single label**, with UNDERDETERMINED and OUT
OF VALID DOMAIN taking precedence over magnitude verdicts for anything they touch. The
rules: **R1 (sector)** — the friction-carrying structure must be *derived* into the channel
from booked nodes; entry by projector choice caps the verdict at UNDERDETERMINED. **R2
(domain)** — any load-bearing kernel feature supported at ω ≲ 3.4H is OUT OF VALID DOMAIN.
**R3 (fixedness)** — any staked amplitude or unverified identification in the chain forces
UNDERDETERMINED. **R4 (absorbability)** — distinguishable from α_M only is class-level, not
DISCRIMINATING; indistinguishable from the free SCDP slot is DEGENERATE. **R5 (magnitude)**
— more than 10 orders below both the slot bound and any named future sensitivity is NO
EFFECT. **DISCRIMINATING requires all five at once.** Beneath the gate, the calc-level SPEC
carries its own four pre-registered outcomes — PASS (parameter-free bridge) /
FAIL-BUT-INFORMATIVE (relocation, priced +1 at entry) / CLOSES-THE-QUESTION (channel empty)
/ REFUSE (the sector question undecidable from the booked family) — and the gate maps them
into the tree explicitly (source: `GRUT_PREDICTION_GATE_GAMMA_T.md` §8;
`calc/SPEC_gw_tensor_friction.md` §5).

**The wording rule** (owner correction, adopted on the gate's face): a candidate under a
gate is **the currently identified candidate** for a nontrivial cross-sector consequence —
never "the only place such a thing could live." Nothing forces the discriminator to live in
the slot being gated; the gate adjudicates that candidate only (source:
`GRUT_PREDICTION_GATE_GAMMA_T.md` preamble).

> **STATUS: DERIVED (methodological record: the protocol exists as executed governance, not
> as a claim about nature)** — the eleven-step design-first gate with a five-outcome
> preregistered decision tree and per-horn routing (source:
> `GRUT_PREDICTION_GATE_GAMMA_T.md`, whole document).

---

## 5 · The Γ_T closure, in full

This is the record's one complete pass from candidate to computed closure, and every part of
it is load-bearing for how this book's organizing fact was earned.

### 5.1 The candidate

Γ_T — a dissipative friction term in the cosmological tensor wave equation — was the
currently identified candidate for a nontrivial cross-sector consequence, because one slot
connects three registers of the program: (1) the **derived Tier-4 TT dissipation kernel**
(gravity sector); (2) the **KMS/FDT lock** (any friction must arrive with its stochastic
companion at the coth(ω/2T_dS) ratio, T_dS = H/2π); (3) **cosmological tensor propagation**,
where the SCDP open EFT (arXiv:2507.03103) has parameterized the same object class and the
only measured statement exists: |Γ_T| ≲ few × H₀ on the shared slot. The pre-registered
question, unchanged from the register: *does the local memory scale connect to the
cosmological friction parameter-free, or does the bridge need a new inserted scale?*
(source: `GRUT_PREDICTION_GATE_GAMMA_T.md` §1; `calc/SPEC_gw_tensor_friction.md` §2).

The record contains two kernel candidates — the gate's two horns, which never mix:

- **Horn (a), the DERIVED kernel** (Tier-4, flat contract scope, ω ≫ H): chromatic,
  Γ_T ∝ ω³, parameter-free, sign fixed by passivity.
- **Horn (b), the BOOKED two-scale ansatz** (`calc/wz_dark_energy.py`, register `rung7_wz`):
  χ(ω) = A/(1 − iωτ_c) + B/(1 − iωτ₂) with τ₂ ~ 1/H₀ — achromatic in the observing band,
  Γ_T → B·H₀/2.

### 5.2 The design-time verdict

The gate's step-6 input table graded all twelve inputs; step 7 sorted them, exposing the
fixed/observable disjunction quoted in §1. Step 8 licensed the domain: the ground-based band
sits at ω/H₀ ~ 10²⁰, fully licensed for horn (a) (the derived refusal boundary ω = 3.3993H
is 20 orders below the band), while horn (b)'s τ₂ pole is an analytic feature at |ω| ~ H₀ —
inside the region ROOT-1 established as **UNASKABLE** on four independent obstructions
(no frequency variable is even defined there). Step 11 then routed what was decidable from
statuses alone:

- **Horn (b) trips R1, R2 and R3 simultaneously** — the sector assignment is CHOSEN, the
  pole sits in the unaskable region, B is staked and B ≡ ε unverified — and even resolved,
  its achromatic form is R4-DEGENERATE with the free SCDP slot. *No route from horn (b) to
  DISCRIMINATING exists on the current record.*
- **Horn (a) passes R1–R3** (derived, licensed, parameter-free) **but is foreseen dead at
  R5**: its scale against the slot bound is set by (ω/ω_Pl)², placing it ≳ 60 orders below
  few × H₀ at design-level foresight. Because horn (a) has no free parameter, a calculation
  can only confirm this routing, never move it. **"A calculation whose verdict cannot
  change is a closure, not a hunt."**
- The one in-principle discriminating structure — the chromatic ω³ term with fixed
  coefficient plus the KMS-locked noise companion — lives entirely in horn (a) and dies
  with it at R5; its relation-level content (dissipative ≠ α_M; noise mandatory) is
  class-level and already fenced against GRUT credit.

> **STATUS: CLOSED (gate outcome, rendered at design time from register statuses alone:
> the design does not survive as a prediction hunt; no number computed in the verdict)** —
> (source: `GRUT_PREDICTION_GATE_GAMMA_T.md` §9).

### 5.3 The closure computation

The gate left one honest move available — a closure computation, explicitly priced as "a
closure, not a prediction" — and the owner authorized it. `calc/gw_tensor_friction.py` was
built to the **unmodified 2026-08-22 SPEC** (the immutable calc-level pre-registration), to
the de-pinned standard: its verdicts are computed at runtime from statuses extracted out of
`provenance/claims.json` and `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md`, never carried in the
script's own text.

**SPEC outcome: REFUSE, with the obstruction stack named.** Q-A — the sector question the
SPEC says dominates everything else — cannot be settled from the booked family: every
booked level books the channel assignment as a projector **choice** (p_tt CHOSEN,
five-angle interrogation unanimous; the operator-basis frame CHOSEN at its enumerated
order); the SPEC's two horns disagree; nothing booked selects between them. The full stack:
(i) p_tt CHOSEN; (ii) frame-level CHOSEN; (iii) τ₂ INSERTED un-sourced (+2 of rung7's +3);
(iv) the pole's region ω ≲ 3.4H UNASKABLE — the derivation that would settle Q-A cannot
currently be posed (source: `calc/RESULTS_gw_tensor_friction.md`).

**The pre-registered question, answered: NO parameter-free connection exists on the
licensed record.** The only parameter-free, licensed entry into the slot is the Tier-4
derived kernel's

    Γ_T(ω) = (3/1280π)·(ω³/M̄_P²)·[1 + (104/9)(H₀/ω)²]    (chromatic ∝ ω³; μ-independent)

giving Γ_T/H₀ = 6.19×10⁻⁶³ at 100 Hz — **62.7 orders below the shared-slot bound
few × H₀** (arXiv:2507.03103), final at these declarations because the horn has no free
parameter. The gate's NO EFFECT routing is thereby **computed, not foreseen**.

> **STATUS: CLOSED (computed NO EFFECT; SPEC outcome REFUSE on the observable route;
> commits 2116251, 41e1af5)** — canonical claim 16, verbatim: the Γ_T parameter-free value
> (6.19e-63·H₀ at 100 Hz) (source: `books/CORPUS_CHARTER.md`;
> `calc/RESULTS_gw_tensor_friction.md`; `calc/gw_tensor_friction.py`;
> `GRUT_PREDICTION_GATE_GAMMA_T.md`).

**The conditional exhibits, labelled and unbanked.** The SPEC's owed composition of horn
(b)'s two live B values was performed and never composed silently: B = 0.4 (staked) gives
Γ_T = 0.20·H₀ and a standard-siren amplitude effect Ξ(z=0.5) − 1 ≈ 3.7×10⁻²; B ≈ 2.4×10⁻⁴
(the conformalon leg) gives 1.2×10⁻⁴·H₀ and 2.2×10⁻⁵ — 3.2 orders apart, with nothing on
the record selecting between them. The match-temptation fence was applied in full: the
staked B = 0.4 landing inside the slot bound carries **evidential weight zero**. The B ≡ ε
identification is carried UNVERIFIED; no computation uses it. The unpinned ω_c moves the
UV/IR crossover across a 19.8-order span (9.8×10⁻⁹ Hz / 22 Hz / 0.64 THz on the three
in-corpus values) and enters no headline (source: `calc/RESULTS_gw_tensor_friction.md`,
conditional exhibits; `calc/SPEC_gw_tensor_friction.md` §§3–4).

**The hostile verification.** Three independent checkers ran pre-commit. Arithmetic: a
from-scratch recomputation reproduced every table value to the printed digits. SPEC
compliance: four minor defects caught and fixed, disclosed per house rule — including the
pass-label margin gate of §3. And a **hostile refutation of the REFUSE**: an exhaustive
search of all 74 register nodes found **no FORCED verdict anywhere** — three nearest
misses, each failing on the register's own face (noise-transversality does not force
tracelessness, "the TT restriction remains CHOSEN"; `response_lorentz_covariance` is
TT-scoped at the vertex and corroborates the domain obstruction; the rung9b a/c
sector-split assigns anomaly counterterms at k⁴, not the τ₂ pole). Obstructions (i)–(iii)
satisfy the REFUSE clause even with (iv) struck (source:
`calc/RESULTS_gw_tensor_friction.md`, adversarial verification).

**Standing consequences.** The signature audit's gate-to-readmit is closed **as a computed
refusal** — the ≤10⁻²¹ figures stay un-readmitted, no number banks. EDIT 1's conditional
marker is NOT finalised (that required a scalar-only Q-A answer; a REFUSE is not one). And
under the freeze's stop rule, with the Γ_T candidate closed by computation, the honest
program statement stands:

> **STATUS: CLOSED (gate outcome + closure computation: "no discriminator identified on the
> current record"; remaining candidates each require their own gate before any
> computation)** — (source: `GRUT_PREDICTION_GATE_GAMMA_T.md` §9;
> `calc/RESULTS_gw_tensor_friction.md`, standing consequences).

---

## 6 · The signature audit record

`SIGNATURE_AUDIT.md` is the standing record of GRUT's empirical reach — every observable
the program could in principle touch, and what an exhaustive audit found. Its headline is
printed on its own face: at interpretation-level, GRUT is signature-null. The audited
candidates, compressed:

| candidate | audit verdict |
|---|---|
| GW dissipation (dephasing, v_g ≠ c) | invisible-by-suppression (~22–62 orders below sensitivity) |
| dark-energy w(z) | signature-null (sourced = ΛCDM; evolving w needs an inserted scale) |
| tabletop decoherence (energy-basis wedge) | invisible-by-suppression (quiet-or-faint) |
| linear cosmology (μ, Σ growth) | signature-removing (no-go export: μ = 1; GRUT forbids its own naive μ = 4/3) |
| founding ζ / info / L₀ screens | no observable |
| linear-cosmology interior ({shear, bulk} family) | constrained-to-a-computed-window (the fourth category) |

> **STATUS: CLOSED (audit outcome: EMPTY — no admissible, dedicated, parameter-free
> signature survives; scoped to GRUT-as-written, and known conditional on the CHOSEN
> projector per the audit's own post-interrogation note)** — (source: `SIGNATURE_AUDIT.md`,
> audit-critic verdict and 2026-08-02 post-interrogation note).

Four items from the audit's verified 2026-08-02 extension are individually load-bearing for
this book.

**The scoped null.** The external four-domain hunt (pre-registered A/B/C bar, adversarially
refereed, numbers overseer-verified) found no candidate above Grade C **in the explored
structure** — the admitted TT-channel / passive-KMS / ΛCDM-at-linear family. This confirms
the EMPTY verdict from outside, and is explicitly *not* the universal claim "GRUT is
empirically silent," which no search can establish.

> **STATUS: CLOSED (audit outcome: scoped null — no candidate above Grade C in the explored
> structure; not a universal silence claim)** — (source: `SIGNATURE_AUDIT.md`, 2026-08-02
> item 1).

**The DESI anti-signature — the live threat.** GRUT's sourced prediction is w = −1 flat;
the passivity no-go forbids a single passive relaxor from crossing w = −1; DESI's preferred
w₀wₐ trajectory crosses the phantom divide at z ≈ 0.35–0.5 — exactly the forbidden shape.
The four attribution fences travel with it, verbatim: (a) the preference is DESI BAO + CMB
+ SNe — DESI BAO alone shows no significant preference, and with a fixed r_d anchor the ~3σ
does not reproduce; (b) the honest headline is 3.1σ (DESI DR2+CMB, arXiv:2503.14738) — the
4.2σ endpoint rides the contested DESY5 compilation; (c) Bayesian model comparison gives
only weak-to-moderate evidence; (d) the direction is Quintom-B, phantom in the past,
quintessence today.

> **STATUS: pending refutation if the signal consolidates** — the audit's verbatim standing
> disposition, with its comparative clause carried: "GRUT is structurally worse-placed to
> survive it than ΛCDM+quintessence" (source: `SIGNATURE_AUDIT.md`, 2026-08-02 item 2).

The geometry deserves one plain sentence, and Book VI's is adopted unchanged: there is no
branch in which this observable delivers a confirming signature — if the crossing
consolidates, the whole passive class is excluded; if it dissolves, GRUT's sourced
cosmology remains indistinguishable from ΛCDM. The audit's word for this shape is
*anti-signature*.

**The α_M category fence and the Ξ₀ rule.** Standard-siren friction α_M (running Planck
mass) comes from a Hermitian action: removable by field redefinition,
graviton-number-conserving, sign-indefinite, achromatic, noiseless. A genuine dissipative
Im Σ_R is none of those; they are slot-degenerate in the mean-field equation only. The
consequences cut both ways: GRUT's object class is not absorbable into α_M — but **a
detected Ξ₀ ≠ 1 could never confirm GRUT**, and the distinction identifies the dissipative
*class*, not GRUT within it.

> **STATUS: DERIVED (audit-level category distinction within standard theory; no GRUT
> credit — the distinction identifies the dissipative class, not GRUT within it)** —
> α_M ≠ Im Σ_R (source: `SIGNATURE_AUDIT.md` item 4).

**The SCDP slot bound — the first measured bound on the object class.** The
Salcedo–Colas–Dufner–Pajer open EFT (JHEP 02(2026)241, arXiv:2507.03103) parameterizes a
genuine dissipative tensor friction with mandatory stochastic source, explicitly distinct
from α_M·H — the first mainstream parameterization of the object class — and current
friction measurements transfer as |Γ_T| ≲ few × H₀: **a no-cancellation bound on the
shared slot, not a decomposed measurement of GRUT's kernel**, and no validation of any GRUT
value (the retarded+noise form is u1-generic).

> **STATUS: ASSUMPTION (EMPIRICAL-INPUT, external, shared-slot; the retarded+noise form
> itself is u1-generic — no validation credit for the form)** — (source:
> `SIGNATURE_AUDIT.md` item 5; arXiv:2507.03103 as the record cites it).

**The one soft spot.** Exactly one observable was never closed by a dedicated calculation:
black-hole quasinormal modes / ringdown damping, where a lossy tidal response could in
principle differ from GR's conservative one. The expectation on record — inheritance of
rung4's structural Planck suppression — is an argument, not a computation, and the EMPTY
verdict carries this one explicit caveat.

> **STATUS: UNRESOLVED (invisible-by-inheritance, not a dedicated calculation — the
> signature audit's single explicit caveat)** — QNM/ringdown (source: `SIGNATURE_AUDIT.md`,
> "The one soft spot").

**The NOT-banked fence**, honored throughout this book: no ≤10⁻²¹ figure is a banked
number — including reworded as "GRUT's effect" (no calculation exists; the figure in the
graviton-mass demotion is arithmetic about a *test's reach*); and no "ET closes ~1.5
orders" claim (one choice inside a 2.5-order forecast spread). The fence's gate-to-readmit
was `calc/gw_tensor_friction.py`; that gate is now closed **as a computed refusal**, so the
fence stands permanently on the current record (source: `SIGNATURE_AUDIT.md`, NOT-banked;
`calc/RESULTS_gw_tensor_friction.md`, standing consequences).

---

## 7 · Candidates still standing — none gated

Two candidates named by the gate's own closing paragraph remain on the record. Neither has
a designed gate. The record is explicit that each "would need its own gate" before any
computation, and this book states plainly that **no such gate design exists for either** —
an absence, mapped, not a task silently assumed done.

### 7.1 The USL shape candidate

GRUT's noise kernel driving the Anastopoulos–Hu (2013) gravitational-decoherence master
equation yields a signature distinguished from Diósi–Penrose/CSL **in shape only**: an
energy-basis rate Γ(ΔE) = |A_nm|²S(ΔE/ħ)/ħ², scaling with the energy gap and ignoring
spatial size — the qualitative opposite of position-basis collapse models — with a
parameter-free predicted *shape* (suppressed rise, peak at ΔE = 1.22 ħω_c, cutoff).

> **STATUS: HYPOTHESIS (proposed phenomenological relation; shape-only; magnitude verdict
> quiet-or-faint)** — canonical claim 12, verbatim (source: `books/CORPUS_CHARTER.md`;
> register node `rung8_falsifier`; `GRUT_MODEL_FRAMEWORK.md` §5).

The magnitude verdict is itself computed, and it is the reason this candidate does not
carry the program: the dominant diagonal coupling (T⁰⁰ ~ energy density) commutes with H_S
and samples S(0) = 0 — a quiet bath, Γ = 0; the wedge-carrying off-diagonal coupling
(T⁰ⁱ/Tⁱʲ ~ v/c) survives but lands 7–47 orders below detectability; observability would
require staking the noise amplitude ~10⁷× above natural, a tuned number at the current
matter-wave bound.

> **STATUS: CLOSED (computed outcome B — quiet-or-faint: diagonal coupling samples
> S(0) = 0, Γ = 0; the off-diagonal wedge is 7–47 orders below detectable; the falsifier
> does not carry the program)** — (source: register node `rung8_falsifier` tier_note and
> differentiator; `calc/q1_energy_basis_magnitude.py`; `calc/energy_basis_decoherence.py`;
> `NO_GO_LEDGER.md` entry 4).

Two live threads could move it, both on the record and both open: the specialist gray-zone
check (any leading-order off-diagonal energy coupling sampling S(ΔE) at O(1)?), and the +2
staked inputs made explicit (the amplitude normalization κ; the cutoff ω_c — what
"689 Hz" really was). The bar it must eventually meet is also on the record: the
parameter-free Diósi–Penrose model was excluded at Gran Sasso — it made a magnitude claim
and died by it. GRUT's shape claim, in its quiet-or-faint state, cannot yet be killed that
way — which by the program's own lights is a deficit, not a safety (source:
`books/BOOK_III_QUANTUM_REALITY.md` §7, consistent with `GRUT_MODEL_FRAMEWORK.md` §5).
**Its eleven-step gate has not been designed; the record is silent on what its decision
tree would be.**

### 7.2 The rung8 bookkeeping candidate

`GRUT_NEXT_STEPS.md` lists, after Γ_T and the USL shape, "the rung8 decoherence bookkeeping
against tabletop bounds" as the third currently identified candidate. The record contains
its inputs (the rung8 node's staked κ and ω_c, the declared cutoff convention, the
matter-wave bound as the binding edge) but no gate design, no SPEC, and no pre-registered
decision tree.

> **STATUS: UNRESOLVED (named candidate; no gate designed; nothing beyond the register
> node's own bookkeeping exists)** — (source: `GRUT_NEXT_STEPS.md`, prediction hunt;
> register node `rung8_falsifier`, ledger_note and cutoff_convention).

### 7.3 The interior window — a bound, not a prediction

The one place where data currently binds a GRUT parameter is the linear-cosmology interior:
the {shear, bulk} family's scalar admixture is bounded by measurement (DESI Σ₀ lensing:
x < ~0.59 central-inputs, loose-upper per the F-MAP fence, hence μ − 1 ≲ 0.20), the
audit's *fourth category* — constrained-to-a-computed-window rather than deleted by fiat.
The null is not softened: **x has no floor, so no detection confirms GRUT and no null
refutes it** — the family allows up to the edge and predicts nothing. The TT-auto gate
(§3) is the standing instrument on this window, awaiting a computed candidate x* that the
record does not contain.

> **STATUS: UNRESOLVED (register tier to-derive, default-BROKEN;
> constrained-to-a-computed-window; x has no floor — no detection confirms, no null
> refutes)** — harmonized with Book VI §VI.2.3 at corpus audit (source: `SIGNATURE_AUDIT.md` table row 6;
> `calc/RESULTS_isw_tt_auto.md`; `X_FLOOR_MAP.md`).

---

## 8 · Failed and refused prediction routes — the graveyard, preserved

The program's rule is preserve-the-failure, and this section is its exhibit hall. Every
entry is part of model history, stated on its face.

- **"689 Hz, parameter-free" — RETIRED.** The once-quoted tabletop frequency was
  re-expressed as what it really was: a staked cutoff scale ω_c plus a parameter-free
  predicted *shape*. The number was never parameter-free (source: register node
  `rung8_falsifier`, tier_note and ledger_note).
- **The BMV entanglement-witness backup — WITHDRAWN.** An energy-basis decoherer may not
  degrade a position-basis witness; it has not been recomputed (source: `rung8_falsifier`
  tier_note).
- **The graviton-mass entry — demoted to vacuous.** The dispersion observable scales as m²,
  so any m ~ H₀-class mass induces a phase 10⁻²¹ of threshold: a test that was never
  capable of running, not a test passed; and any such mass has Compton wavelength beyond
  the Hubble radius — of no observational significance in principle.
  > **STATUS: CLOSED (demoted to vacuous — arithmetically right, evidentially empty; the
  > ≤10⁻²¹ figure is a test-reach number, hard-fenced against banking as a GRUT effect)** —
  > (source: `SIGNATURE_AUDIT.md` item 3 and NOT-banked fence).
- **The μ = 4/3 trace-only endpoint — the framework's own self-exclusion.** The
  modification GRUT's conformal coefficient naively suggests is excluded by the framework's
  own consistency analysis plus data.
  > **STATUS: CLOSED (self-exclusion: separate-universe consistency + low-ℓ ISW)** —
  > canonical claim 14, verbatim (source: `books/CORPUS_CHARTER.md`; `NO_GO_LEDGER.md`
  > entry 2).
- **The registered spectral law s = 3 — rejected by the framework's own calculation.** The
  flat-scope computation returned s = 5 exactly, rejecting the registered value at the
  frozen tolerance; importing s = 3 anywhere is laundering, per the dispatch spec.
  > **STATUS: DERIVED (flat scope; rejects the framework's own registered s = 3)** —
  > canonical claim 6, verbatim (source: `books/CORPUS_CHARTER.md`;
  > `GRUT_PROGRAM_FREEZE.md` §§3–4).
- **Evolving w(z) as a GRUT prediction — never earned.** The sourced statement is w = −1
  flat; any evolving w(z) requires the inserted, un-sourced τ₂ ~ 1/H₀.
  > **STATUS: DERIVED (within the choices x = 0 / pure-TT: the sourced cosmology
  > statement)** for w = −1 flat; **HYPOTHESIS (requires the inserted, un-sourced
  > τ₂ ~ 1/H₀, priced +2)** for evolving w(z) — canonical claim 13, verbatim (source:
  > `books/CORPUS_CHARTER.md`; `NO_GO_LEDGER.md` entry 3).
  Both wₐ-sign over-claims — the "wrong sign vs DESI" reading and its mirror "wₐ ≤ 0 is
  the prediction" — were retracted; the sign is frontier-indeterminate (source:
  `NO_GO_LEDGER.md` entry 3, retraction; `books/BOOK_VI_COSMOLOGY.md` VI.3).
- **The GW dephasing route — real but closed as unobservable.** The dissipative dephasing
  exists (absent in lossless GR) and sits 22–62 orders below threshold across the band;
  the GW170817 speed bound is satisfied with 26–66 orders to spare.
  > **STATUS: CLOSED (computed outcome B — real-but-unobservable; FAILS-DIFFERENTIATION;
  > Planck suppression structural, not tuned)** — (source: register node `rung4_love_kk`;
  > `calc/gw_dissipation_bounds.py`; `NO_GO_LEDGER.md` entry 5). The 2026-08-20 scope fence
  > travels with this: the statement stands *as a dephasing statement*; the amplitude
  > channel of a two-scale kernel is not covered by it — that channel is exactly the Γ_T
  > slot, closed separately in §5.
- **The discriminator hunts themselves — empty, twice, plus X_FLOOR.** FOREST-EMPTY
  (confirmed by an independent route in phase 11); X-floor R1 returned NO PIN with the
  confirmation-bias trap unsprung (x = α² structurally unreachable; "α-power = 0 as an
  output"); the dynamics route closed as a classifier (cone, no ceiling, no pin) (source:
  `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md`; `calc/RESULTS_anomaly_c0_map.md`;
  `calc/RESULTS_x_no_pin.md`; `GRUT_PROGRAM_FREEZE.md` §3).
- **And the Γ_T candidate itself** — the record's one gated candidate, closed by
  computation in §5. The graveyard's newest stone is its best-documented one.

---

## 9 · Future gates and the reopening keys

**The rule going forward.** Any new candidate — USL shape, rung8 bookkeeping, or anything a
future record proposes — requires its own eleven-step gate, designed and pre-registered
before any computation, with verdicts routed per horn through the five-outcome tree.
PREDICTED entry requires DISCRIMINATING on all five requirements plus survival of the
program's standard screens. Absent a survivor, the standing statement remains "no
discriminator identified on the current record," and the freeze's stop rule governs
(source: `GRUT_PREDICTION_GATE_GAMMA_T.md` §9; `GRUT_PROGRAM_FREEZE.md` §1).

**The reopening keys** (any one justifies unfreezing; every vote external):

1. **O2 computed** — the interacting graviton zero-mode: *lifted* and the persistence
   claim falls; *protected* and the one surviving derived structure strengthens materially.
2. **The RESIDUE test decided** — the half-line/KMS alignment derived from unoriented
   hypotheses, or the functorial no-go proved.
3. **The SLOT test decided** — a rigorous single-patch G_N → 0 limit (CLPW §4.3).
4. **Nature votes at w = −1** — any observed crossing excludes the entire relaxational
   class at a stroke.
5. **An independently motivated principle** naming a specific phenomenon the framework
   cannot represent — the only door for any new rung.

> **STATUS: UNRESOLVED (posed, decidable, unrun — held as governance conditions, not as
> results)** — the O2 / RESIDUE / SLOT tests (source: `GRUT_PROGRAM_FREEZE.md` §5).

**The nearest empirical threads**, in the order the record leaves them: the DESI
consolidation watch (§6 — the one place nature is currently moving toward a verdict); a
dedicated QNM/ringdown calculation (converting "signature-null by inheritance" into
"signature-null by calculation," or surprising everyone); the rung8 gray-zone check (an
O(1) off-diagonal energy coupling would lift quiet-or-faint and make the USL shape
testable); and the TT-auto instrument's owed A6 check plus any future computed x*. None of
these is a prediction; each is a place a vote could land.

**What would show the whole approach was wrong** — kept in this book because a test of the
method is a test: a self-closing description of the observed asymmetric phenomena with zero
contentful undischarged inputs would falsify the consolidated "every closure consumed an
input" record outright; a demonstrated second discharge row anywhere would break the
conservation pattern; and if the frozen-predicate calibration ever shows the consolidated
claim deflating paradigm cases, it dies as ill-typed rather than false — the honest worst
end (source: `GRUT_PROGRAM_FREEZE.md` §6).

Sectors this book cannot test because the record contains no account of them at all:

> **STATUS: UNMAPPED** — flavor, strong-CP, neutrino masses, dark matter, baryogenesis —
> canonical claim 22, verbatim (source: `books/CORPUS_CHARTER.md`;
> `GRUT_PROGRAM_FREEZE.md`).

The book closes where it opened. The PREDICTED section is empty, for a derived reason; the
machinery that keeps it honestly empty — gates, seals, fences, and the stop rule — is the
program's demonstrated contribution; and the standing posture is the framework's own
closing sentence, adopted verbatim: **"Nature and mathematics hold every one of these
votes. The framework holds none of them."**

---

## Sources drawn from

- `books/CORPUS_CHARTER.md` (status vocabulary; canonical status table, claims 6, 12–16,
  21–22 used verbatim)
- `GRUT_PREDICTION_GATE_GAMMA_T.md` (the eleven-step gate; decision tree; design verdict)
- `calc/SPEC_gw_tensor_friction.md` (the immutable calc-level pre-registration; four
  outcomes; traps; clock scoping)
- `calc/RESULTS_gw_tensor_friction.md` (the closure: REFUSE; the parameter-free pin; the
  conditional exhibits; the hostile verification; standing consequences)
- `SIGNATURE_AUDIT.md` (full: the table; EMPTY verdict; the 2026-08-02 items 1–5; the QNM
  soft spot; the NOT-banked fence and gate-to-readmit)
- `GRUT_MODEL_FRAMEWORK.md` (§§2–8; §8 for the strengthen/weaken lists and the closing
  posture sentence)
- `GRUT_PROGRAM_FREEZE.md` (§1 stopping rule; §3 ledger incl. PREDICTED-EMPTY reason; §4
  what the audits killed; §5 reopening conditions; §6 approach-falsifiers; §7 the method)
- `GRUT_NEXT_STEPS.md` (prediction hunt; experimental bridge; stop rule)
- `NO_GO_LEDGER.md` (strength legend; entries 2–5; the no-FORBIDDEN calibration)
- `provenance/claims.json` — node `rung8_falsifier` in full (statement, tier_note,
  ledger_note, differentiator, cutoff_convention); register framing (74 nodes, sha256
  beaeb84e8a6f8468, read-only to this corpus)
- `HOW_TO_VERIFY.md` (§3 seals; §4 what green means)
- `provenance/prereg/MANIFEST.txt` (the seal mechanism, as directory evidence)
- `STAGE_CLOSE_2026-08-09.md` and `AGENT_COORDINATION.md` (the self-certification pattern)
- `calc/RESULTS_isw_tt_auto.md` (the TT-auto gate history and amendment record)
- `calc/RESULTS_anomaly_c0_map.md`, `calc/RESULTS_x_no_pin.md`, `X_FLOOR_MAP.md`,
  `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` (the empty hunts)
- Sibling books for cross-book consistency of shared statuses:
  `books/BOOK_III_QUANTUM_REALITY.md` (USL), `books/BOOK_IV_GRAVITY_SPACETIME_RESPONSE.md`
  (GW observables), `books/BOOK_VI_COSMOLOGY.md` (DESI, kernel-class discriminator)
- External literature only as the record cites it: arXiv:2507.03103 (SCDP open EFT / the
  slot bound); arXiv:2503.14738 (DESI DR2+CMB); arXiv:1305.5231 (Anastopoulos–Hu, via
  Book III's citation of the record)

## Gaps in this book

1. **No gate design exists for the USL shape candidate** — the record names it as a
   candidate and this book cannot supply its eleven-step design; doing so would be new
   work, not corpus assembly.
2. **No gate design exists for the rung8 bookkeeping candidate** — same absence.
3. **The record does not expand the acronym USL** — carried here, as in Book III, as the
   register's name for the rung8 shape signature.
4. **No dedicated QNM/ringdown calculation** — the signature audit's one explicit caveat;
   "signature-null by inheritance" remains an argument, not a computation.
5. **The ≤10⁻²¹ tabletop/GW figures remain un-readmitted** — no calculation exists behind
   them; the gate that could have readmitted them closed as a computed refusal.
6. **EDIT 1's conditional marker is unfinalised** — a REFUSE is not the scalar-only Q-A
   answer that finalisation required.
7. **The TT-auto gate's A6 Boltzmann-grade differential check is owed** before any κ=3
   kill-grade use, and no computed candidate x* exists for the gate to adjudicate.
8. **The amplitude channel of the two-scale kernel is uncovered** and the ω_c adjudication
   is owed — three in-corpus values span 39.6 orders; the crossover moves ~10 orders on
   that choice alone (shared with Book IV's gap list). The ~10-order and 19.8-order
   figures are consistent: crossover ∝ √ω_c (SPEC §4), so the full span halves to 19.8
   orders while adjacent pairs move ~10.
9. **The DESI consolidation is external** — the record can fence its attribution but cannot
   decide it; this book reports the audit's standing disposition only.
10. **R5's "named future sensitivity" clause has no named instrument on the record** — the
    one candidate forecast ("ET closes ~1.5 orders") is explicitly NOT banked; any future
    gate needing a sensitivity name must source one first.
11. **The rung8 gray-zone check is pending** — the one operator-algebra question whose
    answer could lift quiet-or-faint is posed in the register and unanswered.
12. **Whole sectors are UNMAPPED** (flavor, strong-CP, neutrino masses, dark matter,
    baryogenesis) — no GRUT account exists, hence no test content; recorded here so their
    absence from this book is read as the record's absence, not an oversight.
