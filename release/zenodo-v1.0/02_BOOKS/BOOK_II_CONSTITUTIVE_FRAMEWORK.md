# BOOK II — THE MATHEMATICAL / CONSTITUTIVE FRAMEWORK

> *WORKING DRAFT — part of the GRUT working corpus; statuses per `books/CORPUS_CHARTER.md`;
> subject to chapter-by-chapter audit; nothing here banks.*

**GRUT Books — Working Edition v1.0** · D. Ryan Grover · 2026-09-07 · release `zenodo-v1.0` · Markdown is the authoritative source; the PDF is generated from it. Drafted from the frozen record by the RAI builder (Claude, Anthropic) under owner direction — this edition is a publishing pass only: formatting, navigation, and metadata; no claim strengthened or weakened for publication.

## Contents

- [II.0 · What this book is](#ii0--what-this-book-is)
- [II.1 · The influence action](#ii1--the-influence-action)
- [II.2 · The admissible kernel space: the operator basis](#ii2--the-admissible-kernel-space-the-operator-basis)
- [II.3 · The admission gates](#ii3--the-admission-gates)
- [II.4 · The two anti-overclaim theorems](#ii4--the-two-anti-overclaim-theorems)
- [II.5 · Memory: the Mori–Zwanzig leg and the state of the finite-memory bet](#ii5--memory-the-morizwanzig-leg-and-the-state-of-the-finite-memory-bet)
- [II.6 · The derived kernel: the Tier-4 contract object](#ii6--the-derived-kernel-the-tier-4-contract-object)
- [II.7 · The H¹ = 0 theorem and the even-degree ladder class (Theorem II)](#ii7--the-h¹--0-theorem-and-the-even-degree-ladder-class-theorem-ii)
- [II.8 · Kernel selection: derived from declared inputs, constrained but not selected](#ii8--kernel-selection-derived-from-declared-inputs-constrained-but-not-selected)
- [II.9 · State descriptions and effective dynamics downstream](#ii9--state-descriptions-and-effective-dynamics-downstream)
- [II.10 · The absence map](#ii10--the-absence-map)
- [Sources drawn from](#sources-drawn-from)
- [Gaps in this book](#gaps-in-this-book)

---

---

## II.0 · What this book is

This book presents the mathematical machinery of the responsive-vacuum framework as the
record actually supports it: the influence action, the admissible kernel space, the
admission gates (causality, KMS/FDT, passivity, positivity), the memory structures, the
one kernel the program has actually computed at its declared scope, and the structural
theorems that were earned along the way. It is written for a physicist reader who wants
the constitutive mathematics as a coherent object — but the coherence must not be
mistaken for derivational strength, and so two theorems that *cut against* the framework's
own ambitions are treated as load-bearing members of the framework itself: the
form-universality result (u1: the mathematical form is generic and confers no
GRUT-specific content) and the no-pin theorem (x_no_pin: the action carries a family of
kernels, an amplitude-homogeneous cone, and pins no point of it). A constitutive framework
that knows exactly what its mathematics does and does not fix is the only kind this record
can honestly present.

Throughout, standard-physics background (Schwinger–Keldysh contours, Feynman–Vernon
influence functionals, Kramers–Kronig relations, KMS states, Mori–Zwanzig projections) is
summarized for readability and is *always* distinguished from what the GRUT record itself
established. The register `provenance/claims.json` (74 nodes, read-only to this corpus) is
the status authority wherever it speaks.

---

## II.1 · The influence action

The framework's heart is a single Schwinger–Keldysh influence action for the metric
perturbation h on a declared background. Fields are doubled on the closed time path
(h⁺, h⁻); in the Keldysh basis h_r = (h⁺+h⁻)/2, h_a = h⁺−h⁻ the quadratic action reads

    S_IF[h_r, h_a] = ∫ (dω/2π) d³k [ h_a · K_R(ω,k²) · h_r + (i/2) h_a · N(ω,k²) · h_a ]

with K_R the retarded (dissipation) kernel and N the noise kernel. This is the standard
open-system structure: coarse-graining any local, causal open quantum system over its
environment yields precisely this form (Feynman–Vernon 1963; Caldeira–Leggett 1983;
non-equilibrium Keldysh field theory).

> **STATUS: RECOVERED (generic; u1: the form confers no GRUT-specific content)** — the
> canonical status for the influence-functional/Feynman–Vernon form; the SHOWN content is
> the *borrowed* universality of the form only (source: `provenance/claims.json` node
> `u1_form_universality`; `S_IF.md`).

The register books the formalism at an explicit price. Node `rung1_inin_formalism`
(the formalism half, split by owner ruling 2026-08-23 from the ontological bet) carries
**four priced inputs** (+4): the system/bath split, the Gaussian/linear-response
truncation, the background Lorentzian causal structure, and — booked 2026-08-17 after an
adversarial screen — the *4d-covariant availability of the Ward-sourced gauge-orbit zero*
(that K_R annihilates the full 4d gauge orbit on its retarded slot at covariant strength;
the frontier-reserved Bardeen completion is exactly what this input pre-pays).

> **STATUS: ASSUMPTION (AXIOM — the program's declared entry price, four priced inputs)**
> — a stance, booked openly with a `laundering_ok` justification; the formalism does not
> imply the ontology (source: `provenance/claims.json` node `rung1_inin_formalism`,
> ledger_note).

The companion ontological claim — that the gravitational vacuum *is* a responsive medium
with finite memory — is booked separately and is not part of the mathematics at all:

> **STATUS: ASSUMPTION (AXIOM, +1; "a STANCE, explicitly not derived")** — node
> `rung1_ontology_finite_memory`; its strongest form (single-pole memory) is treated in
> §II.5 below, where its supporting history is stated on its face.

The formal action itself is written out in `S_IF.md`, a construction document at ledger
zero: it declares the field content, the S1–S7 symmetry inventory (causality, quadratic
truncation, system/bath split, KMS/FDT + matrix passivity, diffeomorphism invariance with
its banked Ward limitation, background homogeneity/isotropy with inherited parity-evenness,
and pair symmetry/Onsager — the last flagged as inherited, not chosen, and substantive for
the retarded kernel). No symmetry beyond these is declared; in particular linearized Weyl
invariance is *not available* to the framework, because GRUT imports α as the
trace-anomaly ratio and the anomaly is the statement that Weyl invariance is broken
(`p_tt_ansatz.boundary_condition`).

## II.2 · The admissible kernel space: the operator basis

What tensor structures can K_R and N carry? This was made a computation rather than an
assumption (`calc/operator_basis.py`, results in `calc/RESULTS_operator_basis.md`;
register node `eft_operator_basis`). In the spatial-SVT frame at fixed slicing and fixed
k — the same frame in which the pure-TT ansatz and the linear-cosmology work state their
claims — the isotropic, parity-even, pair-symmetric kernel space is **exactly rank 5**:
{P⁽²⁾, P⁽¹⁾, P⁽⁰ˢ⁾, P⁽⁰ʷ⁾, MIX}. Exhaustiveness is *computed, not asserted*: the
instrument builds the little-group representation and finds the pair-symmetric commutant
is exactly 5-dimensional (full commutant 6; the +1 is the single pair-antisymmetric
trace-longitudinal mixer, itself Ward-killed). The linearized-diffeo (Ward) orbit is
annihilated by P⁽²⁾ and P⁽⁰ˢ⁾ and hit by the rest; helicity forbids TT↔scalar mixing. The
Ward-surviving family is therefore **exactly two independent coefficient functions**:

    K_R(ω,k²) = c₂(ω,k²)·P⁽²⁾ + c₀(ω,k²)·P⁽⁰ˢ⁾
    N(ω,k²)   = n₂(ω,k²)·P⁽²⁾ + n₀(ω,k²)·P⁽⁰ˢ⁾

> **STATUS: DERIVED (enumerated frame/order; exhaustiveness computed via the little-group
> commutant, independently reproduced in a separate helicity-frame construction)** — the
> register node `eft_operator_basis` itself remains tier `to-derive` pending its own
> graduation screen; the frame-level result is banked in its boundary_condition (source:
> `calc/RESULTS_operator_basis.md`; `provenance/claims.json`).

Three honesty notes travel with this result and are constitutive of how the framework must
be read:

**(i) The TT restriction is chosen, not forced.** Restricting c₀ = 0 — the pure-TT
projector — is exactly the `p_tt_ansatz` choice: an input, not a consequence. The
five-angle interrogation of 2026-08-02 (full Lorentz-covariant level, Barnes–Rivers
6-dimensional kernel space, core computation replicated in exact rational arithmetic by
three independent verifiers) returned the same verdict from a strictly stronger level of
generality: diffeomorphism invariance gets you to transverse and stops exactly one
condition short of transverse-traceless. The decisive exhibited fact: linearized
Einstein–Hilbert is *itself* (1/2)k²[P⁽²⁾ − 2P⁽⁰ˢ⁾] — GR's own response kernel carries a
scalar component twice its spin-2 one, so no general principle can force a gravitational
response kernel to be TT-only.

> **STATUS: ASSUMPTION (STRUCTURAL-SELECTION — CHOSEN, unanimous five-angle
> interrogation; not forced)** — canonical status for the TT-only projector (source:
> `provenance/claims.json` node `p_tt_ansatz`, boundary_condition).

**(ii) The two-survivor exhaustiveness is scope-corrected.** The 2026-08-14 Ward-scope
correction, from the SCDP primary-literature read the register's own fence had flagged as
owed (arXiv:2507.03103): dissipative and noise operators necessarily break the doubled
diffeomorphism group to its diagonal, so imposing the *advanced-branch* identity is a
symmetry no dissipative completion sustains; under the surviving diagonal identity the
Ward constraint buys transversality on the retarded slot only, and the admissible
open-gravity space is strictly larger. The correction *strengthens* the CHOSEN verdict (a
larger space makes TT-only more of a choice) and surfaced the noise kernel's
transversality as an input — subsequently discharged as a family-conditional theorem on
rung1's fourth priced input (the 2026-08-17 owner ruling: the Ward-sourced zero plus
N-positivity close the admissible (K_R, N) pair on the projector pair;
`calc/noise_transversality_check.py`, recorded in `S_IF.md` §3).

**(iii) The gauge footing is asymmetric.** P⁽²⁾ is invariant under the full linearized 4d
diffeomorphism group (helicity protection); P⁽⁰ˢ⁾ is invariant only under the spatial
subgroup at fixed slicing — its full 4d-covariant status requires the Bardeen completion,
which remains frontier-reserved. Every uniqueness statement in this section carries that
frame/order fence.

## II.3 · The admission gates

A candidate kernel pair (K_R, N) must pass four gates before it is admissible. Each gate
has a declared status; none of them is a GRUT discovery, and the record says so.

**Causality / analyticity.** The coefficient functions c_i(ω) must be analytic in the
upper half ω-plane — the retarded condition. Kramers–Kronig then links the elastic
(storage) part Re χ to the dissipative part Im χ; the record's rung4 recovers the
worldline-EFT tidal-response (Love-number) structure for the vacuum in exactly this
standard linear-response sense.

> **STATUS: RECOVERED (borrowed Kubo/KK linear-response structure on the declared
> inputs)** — register node `rung4_love_kk`, tier shown; its GW-dissipation observable was
> computed and landed real-but-unobservable, ~21–62 orders below LIGO phase sensitivity
> (outcome B, closed) (source: `provenance/claims.json` node `rung4_love_kk`).

Retardation itself — *why* the kernel is retarded rather than advanced — is not derived:

> **STATUS: ASSUMPTION (EMPIRICAL-INPUT + STRUCTURAL — observed time-asymmetry; the
> audits located its origin in a past-boundary condition in every formulation examined)**
> — source: `GRUT_MODEL_FRAMEWORK.md` §2; the surviving unexplained input is one relative
> datum, the half-line/KMS alignment: **ASSUMPTION (one relative datum: the
> half-line/KMS alignment; five dressings audited, every closure consumed it)** (canonical
> status; Book V treats this front in full).

**The KMS/FDT lock.** In equilibrium the noise kernel is locked to the dissipation by the
fluctuation–dissipation theorem, N tied to Im χ by the coth(ħω/2kT) factor, and KMS
detailed balance is enforced as a *hard admission gate*: any candidate (χ, N) pair whose
residual |G_K − coth·(G_R − G_A)| exceeds tolerance fails and is barred from the
foundation (`gate/kms.py`).

> **STATUS: ASSUMPTION (borrowed standard identity, enforced as a hard admission gate;
> rung2)** — canonical status (source: `provenance/claims.json` node `rung2_kms_gate`).

The temperature in that lock carries zero freedom on the declared background:

> **STATUS: DERIVED (within declarations: forced by Hadamard/KMS on the declared
> background)** — T_dS = H/2π, canonical status; the register's only "forced given the
> background" credit (source: `provenance/claims.json` node `rung2_kms_gate`,
> ledger_note).

A corroborating computed record exists at curved order: Gate-E verified the FDT/KMS lock
per H-order — PASS at O(H⁰), O(H¹) (both sides identically zero, each computed) and
O(H²), as a support identity within the declared validity domain ω ≫ H, with the
coth → sgn grading *derived*, not asserted (the dS temperature is non-perturbative in the
H grading). This is a W-0 record: computed and reported, unbanked
(`PHYSICS_LEDGER/GATE_E_H2_FDT_KMS_AUDIT.md`).

**Passivity, per channel.** For any kernel decomposed on mutually orthogonal idempotent
projectors, the matrix-sense passivity condition (ω·Im K positive-semidefinite) is
*exactly equivalent* to the per-channel scalar conditions ω·Im c_i(ω) ≥ 0, each channel
independently, pointwise — with **no cross-channel rescue**: a violating channel's
negative eigenvalue is unmoved by any amplification of a compliant channel. The KMS lock,
carrying a common scalar thermal factor, is channel-diagonal at the same level, so a
dissipation-sign violation survives into the noise rather than being masked.

> **STATUS: DERIVED (frame-free mathematics; PSD factorizes over orthogonal idempotents;
> machine-verified with a pre-registered four-mutant battery)** — register node
> `passivity_channel_diagonal`, tier shown, sealed prereg before the calc existed
> (source: `calc/RESULTS_x_no_pin.md`; `provenance/prereg/PREREG_X_NO_PIN_2026-08-09.txt`).

A guard travels verbatim with this lemma and is quoted here because downstream prose has
historically been tempted to violate it: passivity *"can propagate a channel's vanishing …
but can never source one. Any argument deriving channel annihilation from passivity alone
is a category error and dies."* The passivity floor is not a licence for the pure-TT
ansatz and not evidence against it.

**Positivity of N.** The noise kernel is a positive-semidefinite covariance. The record's
2026-08-17 owner decomposition ruled this *constitutive* of what the framework already
banks: the symmetrized correlator of any genuine state is PSD by construction, given the
declared system/bath split and Gaussian truncation.

> **STATUS: ASSUMPTION (constitutive of the declared Gaussian-bath inputs; not a separate
> dial)** — source: `provenance/claims.json` node `rung1_inin_formalism`, ledger_note
> (owner ruling 2026-08-17).

## II.4 · The two anti-overclaim theorems

Two theorem-grade structural facts about the admissible family are load-bearing precisely
because they bound what the framework may claim of itself.

**u1 — form-universality.** Any local, causal open quantum system coarse-grains to the
S_IF = K_R + (i/2)N form. The framework is therefore a genuine universal IR *language* —
and for exactly that reason the form confers no GRUT-specific content. GRUT adopts a
universal language; it does not own the universality, and u1's truth must never be
leveraged as support for kernel-universality (u2), which is a separate, open question
(§II.8).

> **STATUS: RECOVERED (generic; u1: the form confers no GRUT-specific content)** —
> canonical status (source: `provenance/claims.json` node `u1_form_universality`).

**x_no_pin — the action carries a family, not a point.** Applying the channel-diagonal
passivity lemma to the Ward-surviving two-channel family: every admissible kernel obeys
the per-channel sign floors ω·Im c₂ ≥ 0 and ω·Im c₀ ≥ 0, pointwise — **and nothing
more**. The admissible set is a convex cone, closed under independent nonnegative
rescaling of each channel (verified through amplitude 10⁶) and realizing *every*
nonnegative ratio c₀/c₂. Passivity orients each channel, never bounds an amplitude, never
selects a ratio. Route R3 closes as *classifier, not pinner*.

> **STATUS: DERIVED (enumerated frame/order; register tier `derived-pending`, pending
> exactly its hypothesis's open frontier — the operator basis's 4d-covariant
> completion)** — source: `provenance/claims.json` node `x_no_pin_theorem`;
> `calc/RESULTS_x_no_pin.md`.

Under the written action's declared normalization x := c₀/c₀^(trace-only) (`S_IF.md` §5),
the floor restates as x_diss(ω) ≥ 0 pointwise — a constraint on a *function*, never a
bare inequality on a number. The transfer from the dissipative floor to the
static/quasi-static modulus that observables couple to is *not* automatic: unconditional
transfer is refuted by an exhibited passive counterexample (a negative contact term is
invisible to passivity, causality, and the two-point KMS lock), and conditional transfer
is derived at the class-level criterion χ_∞ ≥ 0 (sufficient, not necessary).

> **STATUS: UNRESOLVED (register tier derived-pending; the conditional-transfer theorem
> is derived — criterion χ_∞ ≥ 0, sufficient not necessary — but the transfer question
> gates on the open sign of χ_∞; unconditional transfer REFUTED by passive
> counterexample)** — harmonized with Book IV §8.1 at corpus audit; register node `kk_static_transfer`,
> tier `derived-pending`; the residual sign of χ_∞ is a contact/renormalization datum in
> rung3's domain (source: `provenance/claims.json` node `kk_static_transfer`;
> `S_IF.md` §7).

The hand-chosen point of the family is then booked exactly as what it is:

> **STATUS: ASSUMPTION (STRUCTURAL-SELECTION; x_no_pin: the action carries a family, pins
> nothing)** — the x = 0 scalar-to-tensor choice, canonical status (source:
> `provenance/claims.json` nodes `p_tt_ansatz`, `x_no_pin_theorem`).

The consequence of the cone structure deserves stating in this book because it is a
*mathematical* fact about the constitutive framework: the framework's commitment is a
class; a class has no scale; the admissible set is an amplitude-homogeneous cone — every
route from this framework to a number runs outside it. That is the derived structural
reason the program's PREDICTED set is empty.

> **STATUS: EMPTY (nothing has earned entry; Book IX governs entry)** — the PREDICTED
> set, canonical status (source: `GRUT_PROGRAM_FREEZE.md` §3).

## II.5 · Memory: the Mori–Zwanzig leg and the state of the finite-memory bet

The Mori–Zwanzig / Nakajima–Zwanzig projection formalism — slow variable, projected fast
bath, memory kernel, generalized Langevin equation — is one of the framework's four
standard-machinery legs, verified against the primary literature (Mori 1965; Zwanzig 2001;
the register's source list). As with u1, the leg is borrowed: the NZ equation is an
identity, its kernel is defined by the projector P, and MZ coarse-graining is many-to-one
— distinct microscopics wash to the same kernel. The framework's *content* claim was
always about the shape of the kernel, and that claim's record is the most heavily audited
in the corpus.

**The conjecture.** The strongest GRUT form: the vacuum's memory kernel is single-pole
(Debye) — finite memory, one relaxation time.

> **STATUS: UNRESOLVED (anchor-class, derived-pending; pole-vs-cut open; the Tier-4
> computation found a CUT, not a pole, at flat scope)** — canonical status for the
> single-pole/finite-memory kernel (source: `provenance/claims.json` node
> `rung3_single_pole`).

**The audited state of the conjecture, stated on its face.** The record on this node is a
model lesson in what ruthless tier-marking looks like, and this book reports it rather
than smoothing it:

- *The phrase "the Mori–Zwanzig kernel" in the node's own statement does not denote a
  unique object.* `calc/mz_inheritance.py` (2026-08-19) showed the two standard candidates
  answer the key inheritance question oppositely: the symmetrized correlation carries the
  KMS factor's full Matsubara pole ladder, while the Kubo–Mori (canonical) correlation
  replaces coth by 2/(βω) and has no ladder at all; the generalized-Langevin friction
  kernel contains no temperature. The node's own finite-T history identifies its kernel as
  the symmetrized one, so the adverse reading applies. Recorded on the node without tier
  or ledger move — the tier is already the honest one.
- *At free level on the static patch, the single rate the conjecture names does not
  exist.* The free graviton bath's memory is a family indexed by multipole: the slowest
  surviving Matsubara rung is (l+1)H (the graviton has no l = 0, 1), and at fixed l the
  surviving rungs are the whole infinite tower n ≥ l+1. An exact sum rule
  (Σ_l (2l+1)A_l = −ω sinh²x, verified to 26+ digits) shows the l-summed local spectral
  density is exactly Ohmic with no rung zeros — the rung structure survives into the
  graviton bath solely because two partial waves are absent. The owner's final
  reconciliation: *the splitting mechanism is genuinely de Sitter* (β = 2π/H places the
  split centrifugal zeros exactly on the ladder); *its survival in the summed bath is
  kinematic.* All recorded 2026-08-19 on the node, no tier move (source:
  `provenance/claims.json` node `rung3_single_pole`, tier_note; `calc/mz_inheritance.py`,
  `calc/finite_T_pole_structure.py`).

**The reversal, part of the model's history and not a footnote.** The finite-memory bet's
sole in-house quantitative support (the tt_worldline decay) was reversed by corrected
analysis — a real bug validated only at its blind point — and the prior ("something surely
forces finite memory") was removed by enumeration: all seven candidate memory mechanisms
deliver either no memory or unbounded, scale-free memory.

> **STATUS: ASSUMPTION, with REVERSED history on its face (the in-house "no memory time"
> computation was reversed; exact dS free-field theory forces infinite scale-free
> memory)** — finite memory time, canonical status (source: `GRUT_PROGRAM_FREEZE.md` §4;
> `RAI_GORILLA_T1.md` XVI-H).

**What exact de Sitter actually forces: the constant tail.** The massless minimally
coupled field on dS₄ — hence each free TT graviton polarization — has an exact constant
zero mode (Δ₋ = 0), and its retarded response keeps an **exactly constant tail H²/4π
filling the interior of the light cone**, verified by a two-sided causality gate sited
away from any degenerate point; conformal coupling gaps it at m_eff² = 2H².

> **STATUS: DERIVED (exact dS; gapped only at conformal coupling)** — canonical status;
> the surviving fixed point of every deletion test (source: `RAI_GORILLA_T1.md` XVI-G;
> `GRUT_PROGRAM_FREEZE.md` §3).

Whether that persistence survives interaction is the open computation the freeze names as
reopening key O2: the interacting graviton zero-mode. The record's own mutation control
shows the zero is unprotected against generic perturbation (an interaction-induced
m_eff² = 0.1H² returns a finite rate ≈ 0.034H through the verified Starobinsky–Yokoyama
channel); *lifted* fells the persistence claim, *protected* strengthens it materially.

> **STATUS: UNRESOLVED (O2 undone; decides the fixed point's referent)** — source:
> `GRUT_PROGRAM_FREEZE.md` §5; `RAI_GORILLA_T1.md` XVI-N.

## II.6 · The derived kernel: the Tier-4 contract object

Against that backdrop of chosen structure and open memory, the program computed one kernel
end-to-end at a declared scope — the contract-level retarded TT kernel, built through the
validated chain vertex (T1) → massless TT bath (T2) → one-loop assembly (T3) → retarded
completion (T4):

    K_R(ω) = Σ_R(ω) = −(3/1280π²) ω⁴ L + H²·(−(13/480π²) ω² L) + [real local slot],
    L = log(μ²/ω²) + iπ,    with H¹ = 0 identically.

Unconditional content: a branch point at ω = 0 with a real-axis cut (the gapless
two-graviton continuum); the frozen absorptive coefficients; retarded analyticity of the
+iπ completion. Conditional content, banked *as* conditional: no additional real-axis zero
of the resummed denominator on the reference slice only; resummed/first-order agreement
iff |λ| ≪ 1. **No pole claim is made.** Validity ω ≫ H with ε_H = (104/9)H²/ω²; ω ≲ H is
refused by the evaluator itself. The local slot is carried symbolically: at H⁰,
c0 = c2 = 0 exact by the Option-β D5 execution with c4 represented by the RG-invariant
Λ_R, retained symbolic — one unresolved renormalization input; the H² locals c0′, c2′ are
unresolved and fork-gated (no IR scale introduced).

> **STATUS: DERIVED (flat contract scope, ω ≫ H)** — the Tier-4 TT kernel with H¹ = 0
> identically, canonical status; register node `kr_contract_retarded_tier4` banked
> 2026-09-01 as a scoped computed record at ledger 0 — *no derivation credit accrues to
> any GRUT rung* (source: `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`;
> `provenance/claims.json` node `kr_contract_retarded_tier4`).

The benchmark consequence of that kernel, computed under pre-registered rules
(`PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`, W-0):

    Im χ(ω) = (3/1280π) ω⁴ + (13/480π) H²ω²  > 0
    J_eff(ω) = (3/1280π) ω⁵ + (13/480π) H²ω³

The flat slice is a pure power law — log-slope of Im χ exactly 4 at every ω — i.e. **s = 5**
in the registered J-convention, firmly convergent (Re χ(0) = 3/(2560π²) exactly, no cutoff
anywhere in the instrument). The registered s = 3 is *rejected by the register's own
tolerance* (slope residual 2.0 ≫ TOL_S = 0.30); the s = 3 shape re-enters only as the
curvature-induced O(H²) component, with an H²-proportional coefficient the registered
family excludes. The mechanism finding adjudicates the register's own rung3 derivation:
s = 3 came from DOS ~ ω² with an assumed coupling weight; the actual TT-TT-TT vertex is
two-derivative, contributing ω⁴ in |V|² on the gapless cut.

> **STATUS: DERIVED (flat scope; rejects the framework's own registered s = 3)** — the
> spectral law s = 5, canonical status (source:
> `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`).

Axis 2 of the benchmark (relaxational vs resonant) is INDETERMINATE with the missing
component precisely named — the D5 local conditions; the registered test is scheme-hostage
(the reference-slice sign crossing sits exactly at ω = μ and moves with μ). The
scheme-robust substatement: for every real local choice there is no resonance-class
feature in-domain — Im χ monotone positive, no pole, no peak. Two boundaries of this whole
section remain the owner's: the D5 renormalization conditions, and the kernel-vs-dressed
object identity (the dressed reading would land Im χ → const, the opposite side of the
pre-registered convergence boundary).

> **STATUS: UNRESOLVED (owner fork, still owed: kernel vs dressed-propagator identity of
> the registered object; axis-2 verdicts must be re-run if the dressed reading is
> ruled)** — source: `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`
> (sensitivity disclosure); `GRUT_PROGRAM_FREEZE.md` §3 UNRESOLVED.

A separate W-0 record (NOISE-A) confines the α = −2 noise-sector behavior to the
equal-time/secular mode-sum class, which no registered observable consumes; the
finite-frequency noise kernel of the registered observable is an exact polynomial
(`PHYSICS_LEDGER/WALL_KR_NOISE_IR_AUDIT.md`, unbanked).

## II.7 · The H¹ = 0 theorem and the even-degree ladder class (Theorem II)

The Tier-4 kernel's most striking structural feature — the identically vanishing O(H)
sector — was made the object of a nine-phase campaign (2026-09, frozen 2026-09-04) that
decomposed, derived, and then honestly bounded it. The final object:

    H¹ = F_state + F_weight + F_ladder + F_R ≡ 0   (pointwise, pre-angular, frozen construction)

Four channels, four distinct cancellation depths, no channel promoted beyond its support:

- **S (state)** — the O(H) state term of the Bunch–Davies pair, killed at identity level:
  the canonical FRW Wronskian a²W = const forces the amplitude direction (a standard
  identity); the declared BD prescription excludes the mixing direction (an input).
  DERIVED (amplitude) + DECLARED INPUT (mixing).
- **W (weight)** — the (−2+2)(u+u′) conformal-weight cancellation per key: the total is
  derived from the T1/T2 chains; the 2-vs-2 split is convention. DERIVED (total) +
  CONVENTION (split).
- **L (ladder)** — Λ_N = 0 per transposition orbit: even momentum degree ⇒ reflection
  bridge ⇒ graded Gram symmetry ⇒ the antisymmetric weight annihilates. DERIVED
  (class-level) — this is the leg that generalizes.
- **R (remainder)** — the u-free vertex-grading remainder: exactly zero in the frozen
  construction, gated across all four cache configurations, mechanism *characterized*
  (frequency-insertion antisymmetry) but **underived**. CLOSED-AS-GATED.

The ladder leg's generalization is the campaign's — and arguably the program's — one
genuinely new structural identity, **Theorem II**: for *any* entry family of even total
momentum degree, any entry count, any symmetric slot pairing, under the fixed-ω reflection
convention, Λ_N ≡ 0 as a polynomial identity. Its ancestry is exactly two standard
mathematical identities; support is gated at complete bases of degrees {0, 2, 4}, with odd
counterexamples at {1, 3} and higher even degrees following by the parity identity (a
derivation, not a gate). The boundary was located precisely: the true premise is the
*evenness* of the momentum degree — a generic cosmological constant cannot break the
ladder; odd degree is the obstruction. Einstein–Hilbert membership implies even-degree
entries (tensor-level gate, 7,560 terms), so EH guarantees the ladder premise everywhere
the construction reaches — but the EH-general statement is explicitly *not* established
(probe-direction coverage, S/W at EH-general level, and the R channel are the named
missing bridge).

> **STATUS: DERIVED (the one genuinely new structural identity; carries no confirmatory
> weight for GRUT)** — the H¹ = 0 four-channel cancellation + even-degree ladder class
> (Theorem II), canonical status (source: `PHYSICS_LEDGER/WALL_KR_H1_PHASE9_CLOSURE.md`;
> `provenance/claims.json` via the frozen phase artifacts).

The closure memorandum's binding interpretation is reproduced here because every book of
this corpus must obey it: **no GRUT-specific premise occurs in the H¹ ancestry** (a
machine-checked leaf audit over a hand-encoded 21-node graph — a search verdict, not a
proof of absence), so GRUT was never under test, and H¹ = 0 must not be cited as evidence
for GRUT in any downstream record. That no-citation rule is PROPOSED, awaiting owner
ratification; until then it binds the record's authors and this corpus's default behavior.
The deflationary consequence is stated without cushioning: the campaign isolated a
computed identity *of the standard construction* at this order and scope.

## II.8 · Kernel selection: derived from declared inputs, constrained but not selected

Does anything in the registered material *select* the Tier-4 kernel out of the admissible
space of §II.2–II.3? The kernel-selection audit (2026-09-03, W-0, 23/23 battery) answered
with a six-way decomposition of the ω⁴ claim: dimensional analysis alone forces nothing
(the registered ω³ comparator was dimensionally admissible); the ω⁴ weight is forced by
the two-derivative vertex — *and the vertex order is input microphysics
(Einstein–Hilbert), not a principle*; the gapless two-graviton cut comes from the declared
massless bath; scale-freeness at H = 0 then forces the exponent; one loop computes the
coefficient. Five admissible-but-different kernel families were exhibited without
computing anything (the Λ_R family; the (c0′, c2′) family; different bath content; a
gapped bath; a different admissible state) — **every alternative is excluded by an input
— vertex, bath, state, scheme — never by a principle.** On the forced hierarchy, the
GRUT kernel sits at "derived from microscopic dynamics *given the declared inputs*" and at
"constrained — not uniquely selected — within the admissible space."

> **STATUS: UNRESOLVED (the selection question is open — novelty class B; no registered
> GRUT-specific principle reduces the admissible kernel space beyond standard
> constraints; W-0 audit record, unbanked)** — source:
> `PHYSICS_LEDGER/WALL_KR_KERNEL_SELECTION.md`.

The one candidate with selective power if proven is u2 — kernel-universality across
microscopic/quantum-gravity completions:

> **STATUS: UNRESOLVED (to-derive, default-BROKEN; likely under-determined out of the
> gate; graduation requires ≥ 2 distinct completions flowing to the same IR-kernel
> class)** — source: `provenance/claims.json` node `u2_kernel_universality`.

## II.9 · State descriptions and effective dynamics downstream

**States.** The framework's state-side declarations are the D1–D5 sheet: the BD-analogue
state (D3), scheme/no-IR-scale (D5), order of limits (D1), gauge (D2/D4) — each a priced
structural selection (`GRUT_PROGRAM_FREEZE.md` §3). The BD declaration is not decorative:
in Theorem II's decomposition it is *the entire reason the S channel's mixing direction
vanishes* — a concrete instance of a state declaration doing constitutive work. For the
equilibrium statements the state is KMS at the background temperature; and at the
algebraic level the record carries the audited caveat that the canonical tensor-product
system/bath split does not exist in the relevant algebra type (III₁) — what survives
translation is a one-sided inclusion, with the crossed-product construction relocating
rather than discharging the state-selection input.

> **STATUS: RECOVERED (borrowed; audited verdict B-INPUT-RELOCATION: the unexplained
> input moves, it is not discharged)** — Type III₁ → II₁ via the CLPW crossed product,
> canonical status; Book VIII treats this front (source: `GRUT_MODEL_FRAMEWORK.md` §2).

**Effective dynamics.** Integrating out the bath yields the reduced master equation; the
unitary core is Schrödinger; the noise kernel supplies decoherence selecting a pointer
basis.

> **STATUS: RECOVERED (standard decoherence machinery on declared inputs)** —
> pointer-basis selection via the noise kernel, canonical status; Book III treats the
> quantum sector, including the Born-measure door GRUT does not open (source:
> `provenance/claims.json` node `rung6_qm_limit`; `GRUT_MODEL_FRAMEWORK.md` §5).

At zero memory the framework collapses to GR:

> **STATUS: RECOVERED (largely by identity; KERNEL-STANDARD, scoped)** — GR at
> zero-memory collapse, canonical status: compatibility, not correspondence evidence
> (source: `GRUT_PROGRAM_FREEZE.md` §3).

One class-level dynamical exclusion survives with real discriminating force, and its
non-ownership is part of its statement: every purely relaxational kernel — Debye,
multi-pole, Cole–Cole — stays on one side of w = −1; only an oscillatory pole pair
crosses. Any observed crossing falsifies the whole passive class at once, GRUT included.

> **STATUS: DERIVED (class-level; explicitly not GRUT-specific)** — the kernel-class
> discriminator, canonical status (source: `PHYSICS_LEDGER/RUNG7_TWO_POLE_COMPARISON.md`;
> `NO_GO_LEDGER.md` entry 3).

Finally, the RRT arm contributed the program's cleanest theorem-grade product, a
structural statement about response itself: intervention response is reducible for *all*
linear dynamics — unitary, dissipative, non-invertible, Lindblad alike — escaped only by
nonlinearity.

> **STATUS: DERIVED (RRT arm: intervention response reducible for all linear dynamics;
> escaped only by nonlinearity)** — canonical status (source: `GRUT_PROGRAM_FREEZE.md`
> §3).

## II.10 · The absence map

Where the constitutive record is silent, this book says so. The following have **no GRUT
account in the record** or are explicitly fenced open:

1. **The bath's microscopic content.** S_IF is defined at the level of its kernels; the
   bath Hilbert space is integrated out and *not specified* — rung3's frontier, priced
   where it lives. The transport self-energy Σ from the bath's internal dynamics (the
   object that would decide pole-vs-cut at the memory level) is frontier-reserved:
   specify and hand out, do not approximate in-house.
2. **The ω ≲ H regime.** UNASKABLE at current declarations, on four obstructions — not
   false; the evaluator refuses it (source: `GRUT_PROGRAM_FREEZE.md` §3;
   `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`).
3. **The D5 local conditions and Λ_R.** One unresolved renormalization input, owner-ruled
   symbolic; the H² locals fork-gated. Until chosen, axis-2 of the benchmark cannot be
   adjudicated and no scheme-invariant Re χ sign statement exists.
4. **Amplitudes and scales.** No amplitude theorem is executed; every verdict in §II.6 is
   invariant under overall positive rescaling; the cone structure of §II.4 is why.
5. **The 4d-covariant / Bardeen / Riegert–Paneitz completion of the operator basis** —
   frontier-reserved; every frame-level uniqueness statement carries this fence. The
   parity-odd sector is outside the enumeration entirely.
6. **An in-house causality ceiling (Israel–Stewart-type).** Not computable in-house — it
   needs a relaxation time, sound speed, and entropy density named nowhere in the corpus;
   reclassified as a rung3-dispatch sub-question. No number was computed.
7. **A GRUT-specific selection principle for the kernel** — none found (§II.8); and no
   GRUT gate principle was found for the H¹ identity (§II.7). Both absences are recorded
   findings, not oversights.

> **STATUS: UNMAPPED / UNRESOLVED (as itemized; each absence carries its source above)**
> — an absence map is valid content; nothing here is bridged by invention.

---

## Sources drawn from

- `books/CORPUS_CHARTER.md` (status vocabulary; canonical status table)
- `GRUT_MODEL_FRAMEWORK.md` (authoritative model presentation)
- `GRUT_PROGRAM_FREEZE.md` (stopping rule; consolidated ledger)
- `provenance/claims.json` (register nodes: `rung1_inin_formalism`,
  `rung1_ontology_finite_memory`, `rung2_kms_gate`, `rung3_single_pole`, `rung4_love_kk`,
  `p_tt_ansatz`, `eft_operator_basis`, `passivity_channel_diagonal`, `x_no_pin_theorem`,
  `kk_static_transfer`, `u1_form_universality`, `u2_kernel_universality`,
  `kr_contract_retarded_tier4`)
- `S_IF.md` (the formal action specification)
- `calc/RESULTS_operator_basis.md`
- `calc/RESULTS_x_no_pin.md`
- `PHYSICS_LEDGER/WALL_KR_KERNEL_SELECTION.md`
- `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`
- `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`
- `PHYSICS_LEDGER/WALL_KR_H1_PHASE9_CLOSURE.md`
- `PHYSICS_LEDGER/GATE_E_H2_FDT_KMS_AUDIT.md`
- `PHYSICS_LEDGER/WALL_KR_NOISE_IR_AUDIT.md`
- `NO_GO_LEDGER.md`
- `RAI_GORILLA_T1.md` (the dS tail / zero-mode complex; the memory-mechanism enumeration)
- `RAI_DIALECTIC_CHAMBER.md` (the tail's three-round stability; W-0 chamber record)
- `GRUT_V1_PLAIN.md` (the four standard-machinery legs)

External literature cited only where the record already cites it: arXiv:2507.03103 (the
SCDP Ward-scope correction); Feynman–Vernon 1963, Caldeira–Leggett 1983, Mori 1965,
Zwanzig 2001, Callen–Welton 1951, Kubo 1966 (via register `sources` keys).

## Gaps in this book

1. **The Mori–Zwanzig leg has no dedicated committed synthesis document**; its state is
   reconstructed here from the rung3 node's tier_note history and the cited calc files
   (`calc/mz_inheritance.py`, `calc/finite_T_pole_structure.py`). A reader wanting the
   full 2026-08-19 sequence must read the node text itself.
2. **The exact dS tail's primary derivation artifact** is cited via `RAI_GORILLA_T1.md`
   and the freeze rather than a single dedicated calc RESULTS file; the underlying
   computations (static-patch response, zero-mode complex) are spread across session
   records this book did not re-verify.
3. **The Wall-A A3-x finite-masters chain** (the dimensional-regularization master
   integrals feeding the Tier-3 loop) is not narrated here; this book picks up the chain
   at the frozen T1–T4 verdicts.
4. **The noise-sector fork** (ω ≲ H, white-floor regime, owner-held) is named but not
   developed — it is outside every declared scope this book covers.
5. **Book cross-references are prospective**: Books III (quantum sector), V (KMS/arrow),
   VI (cosmology), VIII (algebraic/relational) are cited by scope, and were not available
   to check for consistency at the time of writing. (Corpus audit 2026-09-06: the landed
   books were checked against these citations and found consistent.)
6. **The eft_operator_basis graduation screen** (which would move the node past
   `to-derive`) has not run; if it runs, §II.2's status blocks must be re-read against
   its outcome.
7. **The H¹ no-citation rule is PROPOSED, not ratified**; this book obeys it as default
   behavior. If the owner rules otherwise, §II.7's framing sentence changes, though no
   status changes.
