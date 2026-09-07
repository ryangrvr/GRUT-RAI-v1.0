# Q1 DESIGN GATE — USL in a tabletop analogue

> **2026-09-07 · Investigation gate under `program/REALITY_PROGRAM.md` · disposition
> vocabulary: OPEN/GATED/ON/OFF/ANSWERED (grades the investigation; claim statuses are
> untouched).** Owner-ordered, design-first: **no computation is performed here**; no
> corpus, register, or closed-gate content is modified; verdict-shaped statements below
> are derived from record *statuses and structure*, each with its source cited, per the
> demonstrated Γ_T-gate method. The eventual instrument, if authorized, must be de-pinned
> (verdict extracted at runtime, never hardcoded). Machine-audit companion:
> `Q1_USL_TABLETOP_GATE.schema.json`.

**The boxed question — two phrasings on the record, reconciled here (audit-caught: an
earlier draft of this gate mis-attributed the second phrasing to the ledger).**
The ledger's original (`program/QUESTION_LEDGER.md` Q1): *"Can a physically realizable
open system make a GRUT-class response large enough to distinguish it from that same
apparatus's standard QM/environmental model?"* The owner's ordering instruction
(2026-09-07): *"Can a physically realizable tabletop analogue isolate a GRUT-specific
USL spectral signature that cannot be absorbed into the apparatus's standard
environmental model?"* The phrasings differ (GRUT-class vs GRUT-specific; large-enough
vs cannot-be-absorbed) and **the routing below is read against BOTH**: under the ledger
phrasing, an engineered GRUT-class response is itself an instance of the apparatus's
standard environmental model (legs 1–2), and amplitude alone is insufficient by the §E
rule — so "large enough" cannot rescue it; under the instruction phrasing the same legs
apply directly. Neither phrasing is silently substituted for the other.

---

## 0 · Record reconstruction (step 1, completed before any design)

Primary artifacts located and read: `calc/RESULTS_energy_basis.md` +
`calc/energy_basis_decoherence.py` (2026-06-25, the shape and the wedge);
`calc/q1_energy_basis_magnitude.py` (the magnitude/ratio instrument — NB: its "Q1" is a
2026-06 label unrelated to this ledger's Q1) + `calc/RESULTS_q1_magnitude.md` (the static
artifact carrying the 7–47-orders verdict); register node `rung8_falsifier`
(tier `to-derive`, +2); `SIGNATURE_AUDIT.md`; `books/BOOK_III_QUANTUM_REALITY.md` §USL;
`books/BOOK_IX_TESTS_PREDICTIONS.md`; `GRUT_PROGRAM_FREEZE.md` (the memory-reversal and
spectral-law entries); `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md` (the s = 5
result). Status inventory of every load-bearing element (primary labels from the ordered
six-way vocabulary: derived / recovered / staked / unresolved / excluded / hypothesized):

| element | what the record says | status |
|---|---|---|
| Γ(ΔE) = (1/ħ²)\|A_nm\|² S(ΔE/ħ) | Born–Markov reduction of the in-in action; rate samples the noise spectrum at the Bohr frequency | RECOVERED (standard open-system machinery) |
| the shape g(ΔE): x³ rise, **peak at ΔE = 1.22 ħω_c**, FWHM [0.69, 1.85] ħω_c, cutoff | "parameter-free up to one normalization" — but explicitly **contingent on kill-shot #1's S(ω)** (short, cutoff-set memory; `calc/RESULTS_energy_basis.md` header) | HYPOTHESIZED, premise-degraded: the finite-memory support was later REVERSED — exact dS forces infinite scale-free memory (`GRUT_PROGRAM_FREEZE.md:111`; `books/BOOK_I_FOUNDATIONS.md` P4) — and the registered s = 3 spectral class was REJECTED at flat contract scope by the s = 5 computation (`PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`, 2026-09-01 — **W-0 computed-and-reported, NOT banked; the register still carries s = 3**) — the peak location is *class-conditional* either way |
| the **ΔE-vs-Δx wedge** (Γ ~ S(ΔE/ħ), no Δx dependence; DP/CSL the exact opposite) | "independent of #1, the real differentiator" | DERIVED (class-level structure of the AH family; magnitude-limited — see next rows) |
| the coupling-operator structure | dominant T⁰⁰ ≈ H_S is DIAGONAL → [A,H_S] = 0 → samples S(0) = 0 → **quiet (dies)**; the wedge needs the off-diagonal T⁰ⁱ/Tⁱʲ, suppressed (v/c)² | DERIVED (computed 2026-06-25); one gray-zone check pending on record (any O(1) off-diagonal energy coupling?) — quantified under F8 below |
| magnitude | **Γ/Γ_det ~ 10⁻⁷…10⁻⁴⁷** (outcome B, lives-but-faint); observability needs the staked amplitude ~10⁷⁺ above natural — "a tuned number at the current matter-wave edge" | DERIVED (computed ratio under staked inputs) — the banked quiet-or-faint verdict. **The externally quoted "7–47 orders" is CONFIRMED as the record's own figure** — carried statically by `calc/RESULTS_q1_magnitude.md:43` and the rung8 statement; *reconciled footnote:* the instrument's own prose understates its bright end ("10⁻²⁹..10⁻⁴⁷", its q=2 column only) and misprints the staking factor ("10²⁰⁺" where its own inversion prints ~8.0e6 ≈ 10⁷) — defects in the calc's prose, not in the banked figures |
| κ (amplitude), ω_c (cutoff/peak scale) | staked inputs, +2; "689 Hz parameter-free" RETIRED; ω_c's physical value is an open specialist item | STAKED (register: ASSUMPTION, +2) |
| the response-class *form* | Feynman–Vernon / influence-functional form is universal over any local causal open system | RECOVERED-generic; **u1 fence: no GRUT credit for the form** |
| "specialist" sign-offs | in-house AI passes; **no outside human has ever been contacted** (authority-vocabulary annotation 2026-08-12) | UNRESOLVED (external validation owed; disclosed) |
| BMV entanglement backup | WITHDRAWN (energy-basis decoherer may not degrade a position-basis witness) | EXCLUDED (withdrawn on the record) |
| Pikovski time-dilation decoherence | real, standard, but POSITION-basis — same axis as DP/CSL, not the wedge | RECOVERED (standard physics; the confounder to fence) |

## A · Target observable

**Γ(ΔE)** — the decoherence rate of a superposition of two energy eigenstates split by
ΔE, at fixed spatial separation; units s⁻¹ against energy (or Bohr frequency ΔE/ħ).
Measured as interferometric visibility decay versus an *engineered, scannable* ΔE
(clock-state / motional-state superpositions in the candidate platforms: high-Q
optomechanics, trapped ions, BEC motional or internal states). The paired control
observable is Γ(Δx) at fixed ΔE — the wedge's other axis. This is the observable the
existing USL formalism actually licenses; no stronger observable is invented here.

## B · The GRUT hypothesis, at its weakest defensible strength

Separated per the owner's instruction:

1. **The mathematical response class** (RECOVERED-generic): a super-Ohmic, cutoff-limited
   bath under KMS produces Γ(ΔE) ∝ S(ΔE/ħ) with suppressed small-gap response and a
   class-conditional peak. *This is standard open-system physics; u1 assigns it no GRUT
   content.*
2. **The analogue mapping** (NEW ASSUMPTION, unlicensed by any record artifact): that an
   engineered tabletop bath "stands in for" the gravitational vacuum's bath.
3. **Parameter values** (STAKED): κ, ω_c — and in any analogue these become *engineered
   apparatus properties*, severing them from the vacuum values entirely.
4. **Genuinely GRUT-derived content in the USL sector**: after the above subtractions,
   the record contains **none** that a tabletop analogue could access — GRUT's claim is
   that *the gravitational vacuum* instantiates the class with its specific coupling
   structure (diagonal-dead, off-diagonal (v/c)²-faint) and its specific staked scales.

The weakest defensible testable hypothesis is therefore: *"an engineered open system
realizing the USL response class exhibits the class's Γ(ΔE) shape and wedge."* The gate
notes at design time that this is a prediction of **standard theory**, not of GRUT.

## C · Standard baseline (same apparatus, full strength)

For any candidate platform the baseline model MUST include, at realistic parameters:
thermal Brownian/phonon baths (Ohmic and structured), photon/laser recoil and measurement
back-action, background-gas collisions, trap/clamping and technical noise, charge/flux
noise where relevant, ordinary non-Markovian structured-environment effects — and the
**engineered bath itself**, modeled by standard open-system theory with its measured
spectral density J_env(ω). Pikovski-type time-dilation dephasing is included on the
position axis. *No artificially weakened baseline: the baseline owns every knob the
apparatus physically has, including a fully flexible J_env(ω).*

## D · The analogue mapping — the hardest row

**What correspondence would make the tabletop an analogue?** Only this: the engineered
bath's J(ω) is *chosen* to match the USL class (super-Ohmic, sharp cutoff), and the
engineered coupling operator is *chosen* with [A, H_S] ≠ 0. Both choices are made by the
experimenter, not forced by any GRUT structure.

**What the analogue does NOT reproduce:** the vacuum's bath (the analogue bath is the
apparatus's); gravity's coupling-operator structure (the record's computed result — the
dominant gravitational channel is diagonal and *quiet* — would be deliberately engineered
AWAY to make the signal visible); the staked scales κ and ω_c (replaced by engineered
values); and any Planck-suppression physics. **Everything GRUT-specific fails to
transfer.**

**The steelman, addressed (wording corrected at compliance audit):** analogue gravity
(Unruh/Hawking in BECs) earns its standing by stress-testing a *contested derivation*
(trans-Planckian robustness) through a system sharing the kinematic structure. The record
here DOES contest a step — the short-memory/Markovian reduction for the gravitational
vacuum is exactly rung3's open fork (derived-pending; the finite-memory reversal; Book
III's consumed-inputs caveat on Born–Markov). But the contested step is **bath-class
SELECTION** (pole vs cut, collisional vs free-streaming), and that is precisely what an
engineered analogue cannot probe: the analogue's bath class is *chosen by the
experimenter*, so realizing any class demonstrates nothing about which class the vacuum
selects. Convention-level forks the analogue could touch (e.g. symmetrized vs Kubo–Mori
inheritance) are standard-theory questions — resolving one is F5, not a GRUT signature.

## E · Degeneracy test (the gate's R4)

The mathematical criterion, per the owner's specification: the gate FAILS if
GRUT-signature ⊆ ordinary-environmental-model freedom. Test form: fit the full baseline
of §C, with free J_env(ω), to the candidate "GRUT" signal; if the fit succeeds at
comparable parameter count, the signature is absorbed. **Design-time evaluation: for a
tabletop analogue this inclusion holds BY CONSTRUCTION** — the analogue realizes the
"GRUT signal" *as* an ordinary environmental model (an engineered J(ω) is exactly the
baseline's freedom). A shape, scaling law, or multi-parameter relation escapes only if
GRUT locks it and generic environments cannot mimic it; the reconstruction found no such
lock: the KMS noise-to-dissipation ratio is generic equilibrium physics (rung2, borrowed);
the peak-to-cutoff ratio 1.22 is a property of the (engineered) class and moves with the
spectral index s, which the record itself leaves unresolved between the rejected s = 3
and the computed s = 5. Amplitude is explicitly insufficient (owner rule), and is in any
case engineered here.

## F · Parameter audit — every quantity, no hidden knobs

| quantity | value/source | GRUT-derived? | external input? | free/staked? | fittable? |
|---|---|---|---|---|---|
| κ (noise amplitude) | staked; observability needs ~10⁷⁺ above natural (record) | no | — | STAKED (+2 with ω_c) | in analogue: engineered → free |
| ω_c (cutoff) | staked; physical value open; sets the peak | no | — | STAKED | engineered → free |
| spectral index s | registered 3 (REJECTED flat-scope) vs computed 5 | contested | — | UNRESOLVED | engineered → free |
| \|A_nm\| (coupling matrix elements) | gravitational: diagonal dead, off-diag (v/c)² (computed) | partially (structure computed) | — | fixed for gravity; engineered in analogue | engineered → free |
| bath temperature T | vacuum: T_dS = H/2π (derived-within-declarations); analogue: measured | vacuum yes / analogue no | analogue: measured | — | measured |
| analogue mapping coefficients | none exist in the record | no | NEW | NEW UNLICENSED INPUT | free |
| Γ_det (sensitivity) | apparatus property; matter-wave edge is the binding bound (record) | no | EMPIRICAL | — | measured |

**Consequence:** every quantity that would carry GRUT content is either staked, dead,
unresolved, or replaced by an engineered stand-in. The proposed discriminator has no
fixed GRUT quantity left to pin it. (This is the same structural split the Γ_T gate
found, now in the decoherence sector.)

## G · Controls (designed now; run only if computation is ever authorized)

1. **Null/control model** — baseline-only synthetic data; analysis must return "no
   USL-class feature." 2. **Full environmental model** — §C at realistic parameters.
3. **Parameter perturbation** — κ, ω_c, s varied; the claimed signature must move as the
class predicts (this control *demonstrates* the signature is class-math, an intended
honesty exhibit). 4. **Spectral-shape control** — an Ohmic engineered bath must NOT show
the peak. 5. **Apparatus-scaling control** — the wedge test: Γ vs ΔE at fixed Δx, Γ vs
Δx at fixed ΔE. 6. **Mapping-deformation control** — deform the engineered J(ω) away from
the USL class; the "signal" must follow the engineering, exposing its provenance.
7. **Planted positive** — synthetic USL-class signal injected into baseline noise;
analysis must recover it (calibrates sensitivity; *not* designed to favor GRUT — the
plant is class-math, which is the point). 8. **Analysis-artifact control** — scrambled /
time-shuffled data reconstruction. Instrument discipline: mutation battery + plants that
must detect, per house rule; the verdict extracted, never hardcoded. *Relation to the
N1–N10 battery:* the eight controls above are gate-specific; the N1–N10 negative-claim
standard applies **in addition** to any null result at instrument time, and the explicit
mapping between the two is drawn when the instrument is built.

## H · Falsifiers — conditions that kill Q1 as posed

F1. The analogue mapping cannot be justified as carrying GRUT content (D). ·
F2. The signature is degenerate with environmental-model freedom (E). ·
F3. The signal vanishes at realistic apparatus parameters. ·
F4. Required inputs are staked/unresolved rather than derived (F). ·
F5. Standard physics predicts the identical feature for the same engineered system. ·
F6. The observable cannot be measured at adequate precision (Γ_det). ·
F7. The result depends on an arbitrary analysis choice. ·
F8. The record's own quiet-or-faint verdict (7–47 orders, dominant channel dead) applies
to any *non-engineered* (real-coupling) version of the experiment.

## Decision tree (pre-registered routes)

- **PROCEED TO COMPUTATION** — only if: a concrete platform is physically specified; a
  licensed GRUT quantity survives into the analogue; the full §C baseline is specified;
  the §E discriminator is nondegenerate; every §F input is known or licensed.
- **REFUSE — [named obstruction]** — if any falsifier F1–F8 is established at design
  time, or the §E inclusion holds. No weaker experiment is manufactured to force
  computability.

## Design-time routing (computed from the record; each leg cited)

**The gate routes to REFUSE — analogue-mapping obstruction (F1 ∧ F2 ∧ F5, with F4).**
The derivation, from statuses and structure alone:

1. The response-class *form* is universal (u1 fence — register's own text): an engineered
   realization of a universal form carries no form-level GRUT information. → F5. (u1
   fences the form only; the kernel-level half of "no GRUT information" is carried by
   leg 3/F4 — u2_kernel_universality is to-derive/default-BROKEN with nothing banked.)
2. The analogue's "GRUT signal" is an engineered environmental model, hence inside the
   baseline's freedom **by construction**. → F2 (the §E inclusion holds identically).
3. Everything GRUT-specific — vacuum bath, gravitational coupling structure (diagonal
   channel dead by the record's own computation), staked scales — fails to transfer
   through the mapping (§D). → F1, F4.
4. The non-engineered version (real gravitational coupling) is governed by the record's
   banked verdict: quiet-or-faint, 7–47 orders below sensitivity, dominant channel
   exactly zero. The pending gray-zone check cannot flip this leg within the record's own
   classes: an O(1) off-diagonal coupling removes at most the (v/c)² ~ 10⁻⁶ factor —
   in the surviving super-Ohmic class that moves ~10⁻²⁹ to ~10⁻²³ (still >20 orders
   faint), and the flat class that reaches the bright end is excluded by the record's
   binding matter-wave bound. → F8.

Per the program charter, **this is a successful gate result, not a failure**: it was
obtained for the cost of a design review, and it sharpens where the USL question actually
lives. What the reconstruction shows would genuinely advance it (recorded for the owner,
not self-authorized): (i) the register's own named next-decisive items — the pending
gray-zone operator check (any O(1) off-diagonal energy coupling?) and the physical value
of ω_c; (ii) the wedge protocol retains value as *apparatus development* for a real
(non-analogue) test, honestly priced against the 7–47-order verdict; (iii) an engineered
demonstration remains available as *instrument validation*, so long as it is never
presented as evidence about GRUT.

**Investigation disposition consequence (claims untouched):** Q1-as-posed → owner
decision: accept the routing (Q1 → OFF, evaluation = this gate) or contest it. The
rung8_falsifier claim statuses are unchanged in every case.
