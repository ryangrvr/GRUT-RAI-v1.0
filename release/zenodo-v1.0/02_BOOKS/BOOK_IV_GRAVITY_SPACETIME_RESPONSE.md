# BOOK IV — GRAVITY / SPACETIME RESPONSE

> *"WORKING DRAFT — part of the GRUT working corpus; statuses per `books/CORPUS_CHARTER.md`;
> subject to chapter-by-chapter audit; nothing here banks."*

**GRUT Books — Working Edition v1.0** · D. Ryan Grover · 2026-09-07 · release `zenodo-v1.0` · Markdown is the authoritative source; the PDF is generated from it. Drafted from the frozen record by the RAI builder (Claude, Anthropic) under owner direction — this edition is a publishing pass only: formatting, navigation, and metadata; no claim strengthened or weakened for publication.

## Contents

- [1 · The gravitational-response picture](#1--the-gravitational-response-picture)
- [2 · The Tier-4 contract: the computed kernel](#2--the-tier-4-contract-the-computed-kernel)
  - [Validity boundary — derived, not declared](#validity-boundary--derived-not-declared)
  - [Ward status](#ward-status)
- [3 · Analytic structure: a cut, not the asserted pole](#3--analytic-structure-a-cut-not-the-asserted-pole)
- [4 · The infrared: ω ≲ 3.4H is UNASKABLE, on four obstructions](#4--the-infrared-ω--34h-is-unaskable-on-four-obstructions)
- [5 · The object-identity fork: kernel vs dressed response — OWNER FORK](#5--the-object-identity-fork-kernel-vs-dressed-response--owner-fork)
- [6 · Where the kernel comes from: the KERNEL-STANDARD verdict](#6--where-the-kernel-comes-from-the-kernel-standard-verdict)
- [7 · Known recoveries and limits](#7--known-recoveries-and-limits)
  - [7.1 GR at zero-memory collapse](#71-gr-at-zero-memory-collapse)
  - [7.2 Lorentz covariance of the response — priced, then discharged](#72-lorentz-covariance-of-the-response--priced-then-discharged)
  - [7.3 Solar-system safety via cutoff suppression](#73-solar-system-safety-via-cutoff-suppression)
- [8 · Gravitational-wave physics](#8--gravitational-wave-physics)
  - [8.1 The Love-number / Kramers–Kronig leg (rung4)](#81-the-love-number--kramerskronig-leg-rung4)
  - [8.2 GW dissipation: real, and 22–62 orders too small](#82-gw-dissipation-real-and-2262-orders-too-small)
  - [8.3 The graviton-mass entry — demoted to vacuous](#83-the-graviton-mass-entry--demoted-to-vacuous)
  - [8.4 The category distinction: α_M is not Im Σ_R](#84-the-category-distinction-α_m-is-not-im-σ_r)
  - [8.5 The Γ_T closure — summary](#85-the-γ_t-closure--summary)
  - [8.6 The one soft spot: black-hole ringdown / QNM](#86-the-one-soft-spot-black-hole-ringdown--qnm)
- [9 · What this sector does not contain — the absence map](#9--what-this-sector-does-not-contain--the-absence-map)
- [10 · The sector in one paragraph](#10--the-sector-in-one-paragraph)
- [Sources drawn from](#sources-drawn-from)
- [Gaps in this book](#gaps-in-this-book)

---

---

## 1 · The gravitational-response picture

GRUT's proposal for gravity is constitutive rather than geometric-first: the gravitational
vacuum is treated as a responsive medium, and what the metric perturbation does next depends
on what has acted on it, through a retarded kernel carrying interaction history. The entire
gravitational sector of the program is organized around one object — the retarded
transverse-traceless (TT) response kernel K_R of the vacuum itself — written inside a single
Schwinger–Keldysh influence action for the metric perturbation h (doubled fields, Keldysh
basis h_r, h_a):

    S_IF[h_r, h_a] = ∫ (dω/2π) d³k [ h_a · K_R(ω,k²) · h_r + (i/2) h_a · N(ω,k²) · h_a ]

with K_R = c₂ P⁽²⁾ + c₀ P⁽⁰ˢ⁾ decomposed on the Ward-surviving projector pair, subject to
upper-half-plane analyticity, per-channel passivity, and the KMS/FDT lock tying the noise
kernel N to Im χ in equilibrium (`GRUT_MODEL_FRAMEWORK.md` §3).

Two honesty facts frame everything below, before any gravitational result is stated. First,
the influence-functional form itself is generic:

> **STATUS: RECOVERED (generic; u1: the form confers no GRUT-specific content)** — any local
> causal open system yields the Feynman–Vernon form; no GRUT credit accrues for the form
> (source: `GRUT_MODEL_FRAMEWORK.md` §3; canonical table item 1).

Second, the restriction of the vacuum's response to the pure spin-2 (TT) channel is a choice,
not a theorem:

> **STATUS: ASSUMPTION (STRUCTURAL-SELECTION — CHOSEN, unanimous five-angle interrogation;
> not forced)** — diffeomorphism invariance stops one condition short of forcing the TT
> projector; the {shear, bulk} interior remains the unexplored empirically viable sector
> (source: register node `p_tt_ansatz`; canonical table item 8).

And the equilibrium lock that disciplines the whole family:

> **STATUS: ASSUMPTION (borrowed standard identity, enforced as a hard admission gate;
> rung2)** — KMS/FDT ties N to Im χ by the coth factor; borrowed, not derived (source:
> `GRUT_MODEL_FRAMEWORK.md` §3; canonical table item 2).

The constitutive interpretation, stated at the level the record supports: GRUT does not
claim to have derived a new gravitational dynamics. It claims that gravitational response,
dissipation, and noise can be *written* as sector instances of one open-system architecture,
and it then asks — through the campaigns recorded below — what that writing earns. The
answer of the completed root-level audit is severe and is presented first-class in §6: the
kernel that this architecture actually produces is produced by standard QFT/EFT acting on
inputs GRUT declares rather than derives.

---

## 2 · The Tier-4 contract: the computed kernel

The backbone of the gravitational sector is the Tier-4 contract result (2026-09-01): the
response formulation, run as an ordinary one-loop Schwinger–Keldysh computation on the
declared inputs (two-derivative Einstein–Hilbert TT-TT-TT cubic vertex; massless graviton
bath; BD-analogue state; Option-β dimensional continuation with no IR scale; k→0-first
order of limits; the chosen TT projector), reproduces the standard one-loop retarded TT
self-energy. At contract scope:

    K_R(ω) = Σ_R(ω)                             [(1/2 κ²)-weighted probe units]

    Σ_R(ω > 0) = −(3/1280π²) ω⁴ L + H²(−(13/480π²) ω² L) + [real local slot],
    L = log(μ²/ω²) + iπ,   H¹ sector ≡ 0

with the real local polynomial (c₀, c₂, c₄, c₀′, c₂′) carried symbolically — the D5/scheme
slot, never chosen — and the absorptive content exact: Im Σ_R^{H⁰} = −(3/1280π)ω⁴,
Im Σ_R^{H²} = −(13/480π)H²ω².

> **STATUS: DERIVED (register tier SHOWN; declared scope: ω ≫ H, k→0-first, reference-slice
> conditionals preserved verbatim)** — the contract-level retarded TT kernel exists and is
> well-defined in its declared domain; banked at ledger delta 0 as a scoped computed record,
> explicitly *not* a strength claim, with no derivation credit accruing to any GRUT rung
> (source: register node `kr_contract_retarded_tier4`;
> `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`).

The structural theorem inside it:

> **STATUS: DERIVED (flat contract scope, ω ≫ H)** — Tier-4 TT kernel, H¹ = 0 identically
> (source: canonical table item 5; `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`).

and its generalization,

> **STATUS: DERIVED (the one genuinely new structural identity; carries no confirmatory
> weight for GRUT)** — the H¹ = 0 four-channel cancellation and the even-degree ladder class
> (Theorem II) follow from exactly two standard identities; the true premise is evenness of
> momentum degree (source: canonical table item 24; memory-consolidated H¹ closure package —
> the full derivation chain is Book II/X material).

The benchmark consequence run against the register's own expectations (2026-09-01) produced
the sector's most important self-correction:

> **STATUS: DERIVED (flat scope; rejects the framework's own registered s = 3)** — spectral
> law s = 5: J_eff(ω) = (3/1280π)ω⁵ + (13/480π)H²ω³; the flat vacuum is a pure ω⁴ power law
> in Im χ, firmly convergent with Re χ(0) = 3/(2560π²) exactly; the registered s = 3 power
> re-enters only as the curvature-induced O(H²) component with an H²-proportional
> coefficient the registered family excludes (source: canonical table item 6;
> `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`).

The benchmark's second axis (relaxational vs resonant) returned INDETERMINATE with the
missing component precisely named — the D5 local/renormalization conditions; the registered
test is scheme-hostage (the reference-slice sign crossing sits exactly at ω = μ and moves
with μ). The scheme-robust substatement: for every real local choice there is no
resonance-class feature in-domain — Im χ monotone positive, no pole, no peak.

> **STATUS: UNRESOLVED (axis 2 INDETERMINATE; missing component = D5 local conditions;
> row 4 of the registered cell as registered)** — no scheme-invariant relaxational/resonant
> adjudication exists on the current declarations (source:
> `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`).

One further exact-de Sitter derived object belongs to this sector's inventory:

> **STATUS: DERIVED (exact dS; gapped only at conformal coupling)** — the exact dS constant
> retarded tail H²/4π, with the conformal gap at m_eff² = 2H² (source: canonical table
> item 7; `GRUT_PROGRAM_FREEZE.md` §3).

### Validity boundary — derived, not declared

The kernel's validity domain is ω ≫ H, and its termination is itself a *result* of the
calculation, not a stipulation. The expansion-control parameter is ε_H = (104/9)H²/ω², and
the coefficient is exact arithmetic on the two computed absorptive coefficients:
(13/480)/(3/1280) = 104/9. So ε_H ≥ 1 literally states "the second term of the H-expansion
equals or exceeds the first," and the evaluator's refusal at ω = √(104/9)·H = 3.3993H is a
consequence of the computed kernel — it cannot be loosened by declaration.

> **STATUS: DERIVED (the refusal boundary ω = 3.3993H is a result of the calculation: the
> 104/9 is the ratio of the two computed absorptive coefficients)** — ROOT-1 obstruction O1
> (source: `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §3;
> `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`).

The instrument enforces the boundary in hardware: ε_H ≤ 0.1 controlled, 0.1–1 returned only
with an explicit BOUNDARY flag, ε_H ≥ 1 refused (DomainRejected) — and the refusal is itself
a gated control.

### Ward status

The frozen T3 record's nonzero gauge-image contraction is carried through Tier 4 unchanged:
the graviton-loop analogue of the Class-B structure persists, and K_R is TT-scoped by the
frozen charter, so the residual is *excluded by construction* — not resolved, not repaired,
and K_R was not altered to change it.

> **STATUS: UNRESOLVED (Ward Class-B residual excluded by TT scope, not repaired)** —
> (source: `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`, T4-9).

---

## 3 · Analytic structure: a cut, not the asserted pole

GRUT's historically central gravitational bet was a finite-memory, single-pole vacuum
kernel. What the Tier-4 computation actually found at ω = 0 is a branch point with a
real-axis cut — the gapless two-graviton continuum — present in both Dyson forms
(first-order and resummed), one-loop in origin, unconditional within the contract.

> **STATUS: DERIVED (contract scope; unconditional within the declared inputs)** — branch
> point at ω = 0 with a real-axis cut, the gapless two-graviton continuum; the cut is
> mandatory but input-forced (the ordinary massless two-particle threshold, from the
> declared massless bath) (source: `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`
> T4-8; `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §4).

No pole claim is made anywhere in the contract record. No residue is computed anywhere in
the repository (grep-verified, zero hits); no width; no pole shown gauge-invariant. The
absence-of-additional-zeros statement for the resummed denominator is triply conditional and
frozen as such (reference slice c = 0, κ = 0.1 units, μ = 1); pole-from-cut candidates
require (κω)²|log| ~ 1, outside the EFT domain. Two naive inferences are refused in both
directions by the record's own numbers: "cut ⇒ no pole" is false (matter-scope first-sheet
poles coexist with a cut), and "TT projection precludes a pole" is false (the matter pole
hunt ran in the TT sector); the matter-scope fence is respected and nothing is imported
across it.

The status of the asserted kernel itself, verbatim from the canonical table:

> **STATUS: UNRESOLVED (anchor-class, derived-pending; pole-vs-cut open; the Tier-4
> computation found a CUT, not a pole, at flat scope)** — single-pole/finite-memory kernel
> (rung3) (source: canonical table item 4; register node `rung3_single_pole`).

The decisive scope fact, which must travel with any quotation of "no pole": GRUT's claimed
relaxation pole sits at ω ~ H₀ — *inside the region the evaluator refuses*. "No pole" is a
statement about ω ≫ H; the pole was never looked for where it was claimed
(`PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §4).

---

## 4 · The infrared: ω ≲ 3.4H is UNASKABLE, on four obstructions

The region below the refusal boundary is not merely unresolved at current declarations —
ROOT-1 §3 established that the question itself cannot currently be posed there. Four
independent obstructions, each separately sufficient, presented faithfully:

- **O1 — the boundary is DERIVED, not declared.** ε_H = (104/9)H²/ω² with 104/9 exactly the
  ratio of the two computed absorptive coefficients (§2 above). The refusal at ω = 3.3993H
  is a result of the calculation and cannot be loosened by declaration.

- **O2 — there is no frequency variable there.** The background time-translation flow is a
  priced assumption (register node `background_time_translation_flow`, tier assumed, +1);
  without the flow "there is no single-ω kernel and no ω→0 transport coefficient to
  conjecture about." Its only named discharge route (the static patch) is exhibited false
  for the TT graviton, with shapes differing up to 134% across epochs. ρ(ω), J(ω), Im χ(ω)
  are not defined objects at ω ≲ H; any low-frequency spectral claim — convergent *or*
  floored — presupposes exactly what is missing.

- **O3 — an unregulated IR log at O(H²)**, coefficient −8ω²/15 per H² at d = 3; nine
  candidate regulators were swept, zero licensed, none adopted.

- **O4 — the declared scheme is provably blind to the effect it would adjudicate.** The
  candidate IR floor is thermal, but de Sitter thermality is invisible to the H-grading:
  exp(−2πω/H) vanishes to all orders in H, and the blindness was *derived* (coth(πω/H) − 1
  has vanishing limit and vanishing first and second H-derivatives at fixed ω > 0), not
  asserted.

> **STATUS: UNRESOLVED (UNASKABLE at current declarations — four independent obstructions,
> each separately sufficient; not false)** — the ω ≲ 3.4H regime (source:
> `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §3; `GRUT_PROGRAM_FREEZE.md` §3 UNRESOLVED list).

Two standing guards travel with this verdict. First, the record refuses in advance any
future "we computed it and there is no floor" produced from a graded calculation — the
scheme can return neither a floor nor its absence, so such a gate would be definitional in
the adverse direction. Second, the "new scale required" framing is refused: GRUT already
has the number (rung2 records that Hadamard/KMS forces T_dS = H/2π uniquely, given the
background). What is missing is a *licence* to use it, a *method* non-perturbative in H,
and a *proved stationary reduction* — without which the low-frequency question has no
referent.

> **STATUS: DERIVED (within declarations: forced by Hadamard/KMS on the declared
> background)** — T_dS = H/2π (source: canonical table item 3; register node
> `rung2_kms_gate`).

---

## 5 · The object-identity fork: kernel vs dressed response — OWNER FORK

Every classification-bearing verdict in the gravitational sector was read on χ = −K_R — the
*undressed* 1PI kernel. But the pre-registration's pipeline and the Class-C manifest both
name the *dressed* object G_R = 1/(G₀⁻¹ − Σ), and the two readings land on opposite sides
of the pre-registered convergence boundary: the dressed reading gives
lim Im G_R = −3κ⁴/(320π) on the reference slice — Ohmic and log-divergent, the side that
trips rung1's own falsifier. The benchmark verdict carries the sensitivity disclosure
explicitly: the kernel-level reading is load-bearing, and if the owner rules the registered
object is the dressed response, the axis verdicts must be re-run on it. The divergence
between the readings is contingent on c₀ = 0, which the D5 execution has since made exact —
so the fork may already be decided in the adverse direction by a result the record has not
caught up with. No document carries the fork forward in either direction (zero "dressed"
mentions across all four 2026-09-03 audits).

> **STATUS: UNRESOLVED (owner fork, still owed; the dressed reading lands on the opposite
> side of the pre-registered convergence boundary)** — kernel-vs-dressed object identity;
> this book does not resolve it and neither reading is adopted here (source:
> `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §11;
> `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md` "Limitations";
> `GRUT_PROGRAM_FREEZE.md` §3).

---

## 6 · Where the kernel comes from: the KERNEL-STANDARD verdict

The root-level question — *does anything internal to GRUT, as opposed to a declared input
or standard EFT/QFT machinery, select the GRUT response kernel?* — was adjudicated by the
ROOT-1 campaign (2026-09-04; primary plus independent adversarial leg, 42/42 battery,
agreeing verdicts). The answer is NO: *why this kernel — because standard QFT/EFT produces
it*, acting on inputs GRUT declares rather than derives. Not one link of the chain (vertex,
bath, state, scheme, order of limits, projector) is a GRUT principle. All nine variation
axes produced a countermodel; nine rescue principles classified as five category-2
(standard QFT/EFT) and four category-5 (ad hoc), zero category-4 (genuinely new GRUT
principle) — and the gate was two-sided, so a single category-4 would have flipped it.

> **STATUS: CLOSED (gate outcome: KERNEL-STANDARD — primary and adversarial leg agree;
> nothing internal to GRUT selects the kernel)** — with the mandatory scope warning adopted
> from the adversarial leg: KERNEL-STANDARD means *the ω ≫ H stand-in is accounted for by
> standard physics*; the kernel GRUT actually asserts (finite memory, single pole, s = 3)
> lives at ω ≲ H and was never computed there — on the claimed object nothing determines
> the kernel, not GRUT and not standard EFT (source:
> `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §§1–2, scope box, §13).

Two structural barriers, GRUT's own, explain why nothing internal ever could select it: the
framework asserts a class, and a class has no scale; and the admissible set is an
amplitude-homogeneous cone that orients channels and pins no ratio — "every route from this
framework to a number runs outside it" (`docs/WHERE_IT_STOPS.md`, as quoted in ROOT-1 §6).

The strongest successful countermodel deserves its own line, because it names an undeclared
input: a Wilsonian system/bath partition at a comoving scale q_s, holding every declared
input fixed, multiplies the H⁰ absorptive part by θ(ω − 2q_s) — turning the unconditional
gapless branch point into a gapped threshold. It is admissible because the contract's
declaration sheet (D1–D5) never declares the system/bath mode partition at all.

> **STATUS: UNRESOLVED (a load-bearing input — the system/bath mode partition — is
> undeclared in D1–D5; the gaplessness of the cut is contingent on it)** — (source:
> `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §8, §12).

---

## 7 · Known recoveries and limits

### 7.1 GR at zero-memory collapse

> **STATUS: RECOVERED (largely by identity; KERNEL-STANDARD, scoped)** — GR at zero-memory
> collapse (source: canonical table item 19; `GRUT_PROGRAM_FREEZE.md` §3 RECOVERED).

The register's own record of the mechanism is blunt (node `rung5_gr_limit`, tier assumed,
ledger +2): τ_c → 0 collapses χ to its conservative local form, and the Einstein equations
are then recovered via the Clausius/Rindler-horizon route — which is Jacobson's argument,
not GRUT's. The in-in formalism does no work in that step. The recovery imports two
declared items (entropy ~ area, which sets G; Unruh temperature, which sets ħ) and is
priced +2 *because* it is a recovery: the specialist verdict on record is that the
diffeomorphism Ward identity enforces only ∇_μT^{μν} = 0 and does not determine the action
— EH, R², f(R), Lovelock, and nonlocal curvature actions all satisfy the same Ward
identities — so GR is *borrowed, not hosted*. Λ remains undetermined by the framework.

> **STATUS: ASSUMPTION (register tier assumed; +2 imports: entropy~area and Unruh T; a
> recovery that must not be sold as a derivation)** — the zero-memory GR limit's mechanism
> (source: register node `rung5_gr_limit`, tier_note and ledger_note).

Recovery-by-identity is compatibility, not correspondence evidence
(`GRUT_PROGRAM_FREEZE.md` §3). Nothing in this subsection counts toward PREDICTED.

### 7.2 Lorentz covariance of the response — priced, then discharged

The claim that the vacuum response kernel belongs to the Lorentz-covariant subspace was
owner-ruled a priced assumption (+1) on 2026-08-24, with a measured basis: the FRW
gauge-allowed bilinear response space is 11-dimensional, the Lorentz-covariant
flat-compatible subspace is 3-dimensional, and the 8 removed structures were explicitly
computed. It was then discharged by its own clause on 2026-08-30: the microscopic Σ_R^TT
calculation demonstrated the response lies in the 3-dimensional subspace *without imposing
it as an input* (Q1^TT = INSIDE: the nonlocal TT block equals a(ω,k,H,m)·P₂^TT exactly at
H⁰/H¹/H²; predicates hash-frozen before the TT numbers existed; Q5^TT = INSIDE: flat limit
matches placement), and the +1 was retired.

> **STATUS: DERIVED (discharged 2026-08-30: the priced response property demonstrated
> unimposed, +1 retired; scope ω ≫ H; c₀ = 0 remains separately unlicensed)** — Lorentz
> covariance of the vacuum response kernel (source: register node
> `response_lorentz_covariance`, sub_status and ledger_note;
> `PHYSICS_LEDGER/OWNER_ADJUDICATION_WALL_A_CLOSURE.md` as cited there).

This is the sector's cleanest example of the program's discipline working as designed: an
assumption priced on entry, given a falsifier, and retired only when a computation met the
node's own discharge condition.

### 7.3 Solar-system safety via cutoff suppression

The vacuum's dissipative response is Planck-cutoff suppressed, and the effect *grows* with
frequency — so solar-system tests (orbital μHz–mHz) are even more suppressed than the
LIGO band, where the effect is already 22–62 orders below detectability (§8.2). There is no
regime where the GW effect is large while solar-system physics is safe; both are suppressed
by the same structure, GW less so.

> **STATUS: DERIVED (scaling/consistency argument within the rung4 computation: the same
> structural Planck suppression that makes the GW effect invisible underwrites solar-system
> safety; no dedicated solar-system bound computation exists in the record)** — (source:
> `calc/RESULTS_gw.md` "Consistency"; `calc/gw_dissipation_bounds.py` header; register node
> `rung4_love_kk` tier_note).

---

## 8 · Gravitational-wave physics

### 8.1 The Love-number / Kramers–Kronig leg (rung4)

The elastic side of the vacuum's response — Re χ, the storage modulus — is the vacuum
analogue of a Love-number (tidal) response, Kramers–Kronig-linked to the dissipative Im χ;
the structure recovers the worldline-EFT tidal-response organization for the vacuum.

> **STATUS: RECOVERED (register tier SHOWN; borrowed KK/worldline-EFT tidal-response structure on the
> declared inputs)** — Re[χ] = elastic/storage (Love-number) response, KK-linked to
> dissipative Im[χ] (source: register node `rung4_love_kk`, statement and tier).

The static-transfer question — whether the per-channel *dissipative* sign floor
(ω·Im c₀ ≥ 0) transfers to the static/quasi-static modulus that observable couplings
actually see — was posed into the register as its own node and answered in 2026-08-09 at
the two unflattering outcomes jointly: the decomposition identity
χ(0) = χ_∞ + (2/π)∫₀^∞ dω Im χ/ω shows passivity pushes the static modulus up *from* the
instantaneous part χ_∞ and never below it, so the whole transfer question is the sign of
χ_∞ — a reactive contact/UV datum that passivity, causality, and the KMS lock are all
structurally blind to. A banked counterexample (a retarded-analytic, pointwise-passive,
KMS-consistent kernel with χ(0) = −0.6 < 0) refutes unconditional transfer permanently;
χ_∞ ≥ 0 is the tightest sufficient premise, and whether GRUT's vacuum kernel satisfies it
is bath/UV structure — rung3's domain, priced there.

> **STATUS: UNRESOLVED (register tier derived-pending; answered at outcomes (ii)+(iii):
> unconditional sign transfer REFUTED permanently; the conditional floor gates on the sign
> of χ_∞, a contact/renormalization datum)** — the dissipative-to-static sign transfer
> (source: register node `kk_static_transfer`, sub_status and boundary_condition;
> `calc/kk_static_transfer.py`).

### 8.2 GW dissipation: real, and 22–62 orders too small

A finite dissipative Im χ is something a lossless GR vacuum does not have: it would give a
propagating GW frequency-dependent attenuation, dephasing, and v_g(ω) ≠ c. The rung4
computation (2026-06-25, `calc/gw_dissipation_bounds.py`) asked the honest question — not
"extract a bound" but "is the effect within many orders of sensitivity?" — with the
coupling set to 1, most generous for detectability. Outcome (B): real-but-unobservable.

- Predicted accumulated dephasing over 40 Mpc at 100 Hz: 4.4×10⁻²³ rad (q = 1 thermal
  reading) to 1.5×10⁻⁶³ rad (q = 2), against a ~0.1 rad detectability threshold — 22 to 62
  orders below, across the whole 10–1024 Hz band.
- GW170817 speed bound |c_gw − c|/c < 10⁻¹⁵: satisfied with 26–66 orders to spare — not
  binding.
- The live window for |χ| is [8×10⁻²⁰, 2×10⁻¹⁵]; GRUT sits 21–62 orders below it, and
  reaching it would require dropping the vacuum cutoff to MeV–meV scales — grossly excluded
  by particle-physics and equivalence-principle tests. You cannot tune into detectability
  without breaking everything else; the smallness is structural.

> **STATUS: CLOSED (computed outcome B — real-but-unobservable; FAILS-DIFFERENTIATION;
> ledger 0)** — GW dissipation from Im χ: real (absent in lossless GR) but ~22–62 orders
> below LIGO-class sensitivity; Planck suppression structural, not tuned (source: register
> node `rung4_love_kk` tier_note; `calc/RESULTS_gw.md`; `calc/gw_dissipation_bounds.py`;
> `SIGNATURE_AUDIT.md` table row 1).

A scope fence added 2026-08-20 travels with the dephasing statements and is reproduced
faithfully: the |Re χ| ~ |Im χ| step behind the "same order" amplitude-loss line holds only
on the power-law branch and is false once a second (IR) pole is present — a Lorentzian pole
does not switch off above its own frequency; for the two-scale kernel the register books,
the UV/IR crossover lands at the geometric mean and moves ~10 orders on an unpinned
constant ω_c (three in-corpus values spanning 39.6 orders). The Δφ dephasing numbers are
computed from Re χ on the power-law branch and are unaffected — the filed "22–62 orders
below" *stands as a dephasing statement* — but the amplitude channel of a second IR pole is
not covered by anything computed in that file, and the IR pole's achromatic friction
contribution is exactly the Γ_T slot of §8.5.

> **STATUS: UNRESOLVED (the amplitude channel of a two-scale kernel is not covered by the
> rung4 computation; the crossover rides an unpinned ω_c across ~10 orders)** — (source:
> `calc/gw_dissipation_bounds.py` header, REGIME CHECK block, corrected 2026-08-20).

### 8.3 The graviton-mass entry — demoted to vacuous

The audit's graviton-mass line (a dS-horn m ~ H₀ against the LVK dispersion bound) was
demoted in the 2026-08-02 verification: the dispersion observable scales as m², so the
induced phase of any m ~ H₀-class mass is 10⁻²¹ of threshold — *a test that was never
capable of running, not a test passed*. Against the best current bound (CMB dipole,
5×10⁻³² eV) the margin is ~1.5 orders, not 10; and any m ~ H₀-class mass has Compton
wavelength beyond the Hubble radius — of no observational significance in principle
(Trivedi–Loeb). The 10⁻²¹ figure is demotion arithmetic about a test's reach and is fenced
against ever being re-derived into "GRUT's effect size" — no such calculation exists.

> **STATUS: CLOSED (demoted to vacuous — arithmetically right, evidentially empty; the
> ≤10⁻²¹ figure is a test-reach number, hard-fenced against banking as a GRUT effect)** —
> (source: `SIGNATURE_AUDIT.md` item 3 and the NOT-banked fence).

### 8.4 The category distinction: α_M is not Im Σ_R

Standard-siren friction α_M (running Planck mass) comes from a Hermitian action: removable
by field redefinition, graviton-number-conserving, sign-indefinite, achromatic, noiseless.
A genuine dissipative Im Σ_R is none of those. The two are slot-degenerate in the
mean-field tensor equation only. Consequences carried on the record: a detected Ξ₀ ≠ 1
could never *confirm* GRUT, and would bear on GRUT only after a
conservative-vs-dissipative decomposition the current parameterization does not perform.

> **STATUS: DERIVED (audit-level category distinction within standard theory; no GRUT
> credit — the distinction identifies the dissipative class, not GRUT within it)** —
> α_M ≠ Im Σ_R (source: `SIGNATURE_AUDIT.md` item 4; register node `rung3_single_pole`
> category fence).

The one measured statement in this sector is external: the Salcedo–Colas–Dufner–Pajer open
EFT (JHEP 02(2026)241, arXiv:2507.03103) parameterizes a genuine dissipative tensor
friction Γ_T with a mandatory stochastic source, explicitly distinct from α_M·H — the
first mainstream parameterization of the object *class* — and via slot-degeneracy current
friction measurements transfer as |Γ_T| ≲ few × H₀ on the *shared* slot: a no-cancellation
bound on the slot, not a decomposed measurement of GRUT's kernel.

> **STATUS: ASSUMPTION (EMPIRICAL-INPUT, external, shared-slot; the retarded+noise form
> itself is u1-generic — no validation credit for the form)** — the SCDP Γ_T slot bound
> (source: `SIGNATURE_AUDIT.md` item 5; arXiv:2507.03103 as the record cites it).

### 8.5 The Γ_T closure — summary

Γ_T was the currently identified candidate for a nontrivial cross-sector consequence — the
one slot connecting the derived Tier-4 dissipation kernel, the KMS lock, and cosmological
tensor propagation. The owner-ordered design gate (2026-09-06) found at design time, from
register statuses alone, that the design does not survive as a prediction hunt; the
subsequent closure computation (`calc/gw_tensor_friction.py`, same date) executed the SPEC
and returned REFUSE on the observable route with the obstruction stack named (p_tt CHOSEN;
frame-level CHOSEN; τ₂ inserted un-sourced; the ω ≲ 3.4H region UNASKABLE), and computed
the only parameter-free entry — the Tier-4 derived chromatic friction
Γ_T(ω) = (3/1280π)(ω³/M̄_P²)[1 + (104/9)(H₀/ω)²], μ-independent since Im L = π:

    Γ_T/H₀ = 6.19×10⁻⁶³ at 100 Hz — 62.7 orders below the shared-slot bound few×H₀,

final at these declarations because the horn has no free parameter. Every observable-sized
route runs through inserted, staked, or choice-dependent inputs.

> **STATUS: CLOSED (computed NO EFFECT; SPEC outcome REFUSE on the observable route;
> commits 2116251, 41e1af5)** — Γ_T parameter-free value (6.19e-63·H₀ at 100 Hz) (source:
> canonical table item 16; `GRUT_PREDICTION_GATE_GAMMA_T.md`;
> `calc/RESULTS_gw_tensor_friction.md`). Cross-reference: Book IX carries the full gate
> story — the eleven-step protocol, the decision tree, and the standing consequence that
> no discriminator is identified on the current record.

### 8.6 The one soft spot: black-hole ringdown / QNM

Exactly one GW observable was not closed by a dedicated calculation: black-hole
quasinormal modes / ringdown damping, where a lossy tidal response could in principle
differ from GR's conservative one. The expectation on record is that any shift inherits
rung4's structural Planck suppression — but this is an inheritance argument, not a
computation, and the signature audit's EMPTY verdict carries this one explicit caveat.

> **STATUS: UNRESOLVED (invisible-by-inheritance, not a dedicated calculation — the
> signature audit's single explicit caveat)** — QNM/ringdown (source: `SIGNATURE_AUDIT.md`
> "The one soft spot").

---

## 9 · What this sector does not contain — the absence map

Stated explicitly, because the record is silent and silence is content:

- **Strong-field gravity.** No GRUT account of black-hole interiors, horizons as response
  structures, gravitational collapse, or binary dynamics/GW generation exists in the
  record. The only strong-field-adjacent item is the QNM inheritance caveat (§8.6).
  **STATUS: UNMAPPED** (no register node; no calc).
- **Nonlinear gravitational response.** The contract is one-loop, linear-response, TT-only,
  at the k_ext = 0 evaluation point of the D1 limit; Σ's O(k²) is not computed (T3 scope,
  disclosed). **STATUS: UNMAPPED beyond the declared scope** (source:
  `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md` "Scope limitations").
- **The interacting graviton zero-mode (O2).** Undone; it decides the referent of the
  persistence fixed point and is reopening condition 1 of the program freeze.
  **STATUS: UNRESOLVED (posed, decidable, unrun)** (source: `GRUT_PROGRAM_FREEZE.md` §5).
- **The {shear, bulk} interior.** The scalar-sector response foreclosed by the chosen TT
  projector is empirically viable and windowed by data, not deleted by derivation — it is
  Book VI/IX territory but its existence conditions every "TT-only" statement in this book
  (source: `SIGNATURE_AUDIT.md` post-interrogation note; register node
  `zeta_interior_family`).
- **The noise-sector fork (α = −2) and D5's frozen renormalization conditions.** Both
  owner-held, both untouched by the Tier-4 record by construction; the D5 locals are the
  named missing component of the benchmark's axis 2 (source:
  `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md` HARD STOP;
  `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`).

---

## 10 · The sector in one paragraph

The gravitational sector is the program's most fully executed front and its most
disciplined self-audit. What it established: the response formulation reproduces the
standard one-loop retarded TT self-energy on the declared inputs (SHOWN, declared scope),
with a genuinely new structural identity inside it (H¹ = 0 and its even-degree ladder
class, DERIVED — carrying no confirmatory weight for GRUT), a derived spectral law s = 5
that rejects the framework's own registered s = 3, and a derived validity boundary at
ω = 3.3993H below which the record's own instruments refuse to answer. What it found
against the founding bet: a cut, not the asserted pole — with the claimed pole never looked
for where it was claimed, because at current declarations it *cannot* be looked for there.
What it recovered: GR at zero-memory collapse, largely by identity, with its imports
priced. What it predicts observationally: nothing — GW dissipation is real and 22–62
orders too small; the graviton-mass test was never capable of running; the one
parameter-free number ever computed (Γ_T) landed 62.7 orders below the only bound on its
slot and closed its own gate. The kernel at the center of it all is, by the record's own
two-sided adjudication, standard physics on declared inputs — and the question the sector
hands to the rest of the corpus is not "why this kernel" (answered: standard QFT/EFT) but
the one ROOT-1 names as deepest: *what is the bath, and by what partition is it separated
from the system?*

---

## Sources drawn from

- `books/CORPUS_CHARTER.md`
- `GRUT_MODEL_FRAMEWORK.md`
- `GRUT_PROGRAM_FREEZE.md`
- `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md`
- `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`
- `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`
- `provenance/claims.json` — nodes `kr_contract_retarded_tier4`, `rung4_love_kk`,
  `rung5_gr_limit`, `rung3_single_pole`, `kk_static_transfer`,
  `response_lorentz_covariance`, `p_tt_ansatz` (via charter table and audits),
  `rung2_kms_gate` (via charter table)
- `calc/gw_dissipation_bounds.py` (header + REGIME CHECK block)
- `calc/RESULTS_gw.md`
- `calc/RESULTS_gw_tensor_friction.md`
- `GRUT_PREDICTION_GATE_GAMMA_T.md`
- `SIGNATURE_AUDIT.md` (table; items 3–5; NOT-banked fence; QNM soft spot)
- `docs/WHERE_IT_STOPS.md` (as quoted in ROOT-1 §6)
- External literature only as the record cites it: arXiv:2507.03103 (SCDP open EFT);
  arXiv:2103.08547, arXiv:2107.13905, arXiv:1307.1422, arXiv:2602.07908 (dS graviton
  self-energy line, via `rung3_single_pole`).

## Gaps in this book

1. **The ω ≲ 3.4H regime has no content here because the record has none** — presented as
   UNASKABLE on four obstructions; any future account requires a licence, a method
   non-perturbative in H, and a proved stationary reduction (ROOT-1 §3).
2. **The kernel-vs-dressed fork is presented, not resolved** — every quantitative statement
   in §§2–3 and §8 is on the undressed reading and would need re-running if the owner rules
   for the dressed object.
3. **No strong-field content**: black holes, collapse, binary dynamics, GW generation —
   UNMAPPED in the record; only the QNM inheritance caveat exists.
4. **No dedicated QNM/ringdown calculation** — the audit's one explicit caveat stands.
5. **No dedicated solar-system bound computation** — safety is a scaling/consistency
   argument riding the same structural suppression as the GW smallness.
6. **The GW amplitude channel of a two-scale kernel is uncovered** — the 2026-08-20 fence;
   the crossover rides an unpinned ω_c across ~10 orders (three in-corpus values span 39.6
   orders; the adjudication is owed). The ~10-order figure and Book IX's 19.8-order span
   are consistent, not competing: the crossover scales as √ω_c
   (`calc/SPEC_gw_tensor_friction.md` §4), so the full three-value span halves to 19.8
   orders of crossover while an adjacent-pair choice moves it ~10.
7. **D5's frozen renormalization conditions and the noise-sector (α = −2) fork** — both
   owner-held; axis 2 of the benchmark is INDETERMINATE until D5 lands.
8. **Σ's O(k²) is not computed** (k_ext = 0 evaluation point; T3 scope), and the Ward
   Class-B residual is excluded by TT scope, not repaired.
9. **The system/bath mode partition is undeclared in D1–D5** — a load-bearing input named
   by ROOT-1's strongest countermodel; the gaplessness of the cut is contingent on it.
10. **O2 (interacting graviton zero-mode), the RESIDUE and SLOT tests** — posed, decidable,
    unrun; held as the freeze's reopening keys, not as this book's content.
11. **The Γ_T gate story is summarized, not reproduced** — the full eleven-step protocol,
    decision tree, and conditional exhibits live in Book IX's scope.
