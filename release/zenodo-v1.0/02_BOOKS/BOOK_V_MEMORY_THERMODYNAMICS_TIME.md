# BOOK V — MEMORY, THERMODYNAMICS, AND TIME

> **WORKING DRAFT** — part of the GRUT working corpus; statuses per
> `books/CORPUS_CHARTER.md`; subject to chapter-by-chapter audit; nothing here banks.

**GRUT Books — Working Edition v1.0** · D. Ryan Grover · 2026-09-07 · release `zenodo-v1.0` · Markdown is the authoritative source; the PDF is generated from it. Drafted from the frozen record by the RAI builder (Claude, Anthropic) under owner direction — this edition is a publishing pass only: formatting, navigation, and metadata; no claim strengthened or weakened for publication.

## Contents

- [V.0 · What this book is about — and the central honest result, stated first](#v0--what-this-book-is-about--and-the-central-honest-result-stated-first)
- [V.1 · Memory as ontology: the founding bet, split and priced](#v1--memory-as-ontology-the-founding-bet-split-and-priced)
- [V.2 · The KMS/FDT lock: an assumption enforced as an instrument](#v2--the-kmsfdt-lock-an-assumption-enforced-as-an-instrument)
- [V.3 · What the formalism gives for free, and what it never gives: existence versus direction](#v3--what-the-formalism-gives-for-free-and-what-it-never-gives-existence-versus-direction)
- [V.4 · The Past Hypothesis, audited](#v4--the-past-hypothesis-audited)
- [V.5 · Borchers–Wiesbrock at the level the record supports](#v5--borcherswiesbrock-at-the-level-the-record-supports)
- [V.6 · The finite-memory bet: a reversed history, stated on its face](#v6--the-finite-memory-bet-a-reversed-history-stated-on-its-face)
- [V.7 · Where the memory question actually lives — and why the record refuses to answer it there](#v7--where-the-memory-question-actually-lives--and-why-the-record-refuses-to-answer-it-there)
- [V.8 · The surviving sentence, with its grades welded on](#v8--the-surviving-sentence-with-its-grades-welded-on)
- [V.9 · Passivity, the second law, and the w(z) story](#v9--passivity-the-second-law-and-the-wz-story)
- [V.10 · The ledger of temporal structure: derived versus assumed, in one place](#v10--the-ledger-of-temporal-structure-derived-versus-assumed-in-one-place)
- [Sources drawn from](#sources-drawn-from)
- [Gaps in this book](#gaps-in-this-book)

---

---

## V.0 · What this book is about — and the central honest result, stated first

GRUT's founding language is temporal. A constitutive kernel *remembers*: what a system does
next depends on what has acted on it, through a retarded kernel carrying its interaction
history. Every word in that sentence — remembers, next, retarded, history — presupposes
temporal structure, and this book is the accounting of exactly which pieces of that structure
the record derives, which it recovers from standard physics, and which it assumes. The
accounting is not decoration. Two of the program's largest audited findings live in this
book, and both cut against the founding intuitions.

The first is the book's central honest result. After the program's deepest audits — the
Dialectic Chamber (`RAI_DIALECTIC_CHAMBER.md`) and the Final Boss (`RAI_FINAL_BOSS.md`) ran
temporal orientation through every formalism the record confronts — what survives as
unexplained is not "the arrow of time" as a grand mystery but **one relative Z₂ datum: the
alignment of a spectral half-line with the decaying side of a KMS weight** (the
half-line/KMS alignment). Five dressings of temporal orientation were audited — θ (the
retarded step function), the half-sided modular inclusion, the spectral half-line, the KMS
half-plane, the low-entropy boundary state — and every description that successfully closed
on the observed time-asymmetry consumed at least one of them. Nothing confronted produced
the datum; nothing confronted eliminated it; the closures only converted it between
dressings.

> **STATUS: ASSUMPTION (one relative datum: the half-line/KMS alignment; five dressings
> audited, every closure consumed it)** — canonical claim 17; sources: `RAI_FINAL_BOSS.md`
> §3, `RAI_DIALECTIC_CHAMBER.md` §1, `GRUT_PROGRAM_FREEZE.md` §3.

The second is a reversal the record carries on its face: the finite-memory bet — the
program's historically central commitment — had its sole in-house quantitative support
overturned, and the corrected analysis found that exact de Sitter free-field theory forces
the *opposite* shape: **infinite, scale-free memory** (§V.7).

Everything else in this book — the KMS/FDT lock, the existence-versus-direction
decomposition of dissipation, the Past Hypothesis audit, the Borchers–Wiesbrock material,
passivity in the dark-energy story — is the supporting structure around those two findings.

---

## V.1 · Memory as ontology: the founding bet, split and priced

GRUT's rung-1 commitment was historically stated as one thing: *the gravitational vacuum IS
a responsive medium with finite memory*, described by a Schwinger–Keldysh influence action.
The 2026-08-23 Ruling B split it into two register nodes, because the two halves have
entirely different epistemic standing.

**The formalism half** (`rung1_inin_formalism`, tier `shown`, ledger +4) is the doubled-field
influence action S_IF with retarded dissipation kernel K_R and noise kernel N. It is
borrowed, standard open-system machinery (Schwinger 1961; Keldysh 1964; Feynman–Vernon 1963;
Calzetta–Hu), verified against primary literature, and it carries four priced prerequisite
inputs: the system/bath split, the Gaussian/linear-response truncation, the background
Lorentzian causal structure, and the 4d-covariant availability of the Ward-sourced
gauge-orbit zero. The register is explicit that *the formalism does not imply the ontology*.

> **STATUS: ASSUMPTION (AXIOM — the formalism entry's four priced prerequisite inputs,
> +4)** — the doubled-field machinery is admitted as declared input, its price booked at
> entry (source: `provenance/claims.json` node `rung1_inin_formalism`, tier `shown`,
> ledger +4; block added at corpus audit — Books II/III carry the same).

> **STATUS: RECOVERED (generic; u1: the form confers no GRUT-specific content)** — canonical
> claim 1; any local causal open system yields the Feynman–Vernon form (source:
> `provenance/claims.json` node `u1_form_universality`; `GRUT_MODEL_FRAMEWORK.md` §3).

**The ontology half** (`rung1_ontology_finite_memory`, tier `assumed`, ledger +1) is the
proposition that the vacuum physically *possesses* finite memory — in its strongest GRUT
form, a single-pole relaxation structure. The register's own words: "a STANCE, explicitly
not derived." It is priced +1 precisely because founding status does not exempt an input
from epistemic pricing.

> **STATUS: ASSUMPTION, with REVERSED history on its face (the in-house "no memory time"
> computation was reversed; exact dS free-field theory forces infinite scale-free memory)**
> — canonical claim 18; the reversal is detailed in §V.7 (sources: `provenance/claims.json`
> node `rung1_ontology_finite_memory`; `RAI_GORILLA_T1.md` §XVI-H).

Beneath both halves sits a quieter assumption that this book must surface because every
temporal statement in the record uses it: the declared background carries a
**time-translation flow**, so that two-point kernels depend on the time difference alone and
a single-frequency kernel K_R(ω, k) is definable at all. This was booked in 2026-08-18 as an
*omission* — a presupposition used everywhere and priced nowhere — after the register's own
audit showed causal structure alone gives retarded support but not single-ω collapse.
Without the flow, in the node's words, "there is no single-ω kernel and no ω→0 transport
coefficient to conjecture about."

> **STATUS: ASSUMPTION (booked omission, +1; a presupposition of the formalism's basic form,
> with a named discharge route — a background with a timelike Killing vector — not taken)**
> — source: `provenance/claims.json` node `background_time_translation_flow`.

The honest shape of rung 1, then: the mathematics of memory is standard and borrowed; the
*physics* of memory — that the vacuum has any finite memory at all — is a postulate whose
one in-house support was reversed. That is where this book starts, not where it hides.

---

## V.2 · The KMS/FDT lock: an assumption enforced as an instrument

Rung 2 is the program's thermodynamic discipline. In equilibrium, the noise kernel N is
locked to the dissipative kernel by the fluctuation-dissipation theorem with the quantum
coth(ħω/2kT) factor, and admissible kernels must satisfy KMS detailed balance. GRUT does not
derive this; it borrows the standard identity (Callen–Welton 1951; Kubo 1966) and enforces
it as a **hard admission gate**: `gate/kms.py` is a function, not a slogan — any candidate
(χ, N) pair whose residual |G_K − coth·(G_R − G_A)| exceeds tolerance over the frequency
grid FAILS and is barred from the foundation. White-noise, temperature-independent kernels
fail. T ≤ 0 is rejected as undefined.

> **STATUS: ASSUMPTION (borrowed standard identity, enforced as a hard admission gate;
> rung2)** — canonical claim 2; source: `provenance/claims.json` node `rung2_kms_gate`,
> `gate/kms.py`.

Within its declarations the gate forces one number, and the register counts it as its only
credit of this kind: on the declared de Sitter-like background, the Hadamard/KMS condition
forces the temperature uniquely — any other T is singular at the horizon. The horizon forces
the noise level.

> **STATUS: DERIVED (within declarations: forced by Hadamard/KMS on the declared
> background)** — canonical claim 3, T_dS = H/2π; source: `provenance/claims.json` node
> `rung2_kms_gate`; the Unruh/horizon-temperature *relation* itself is a borrowed import
> (node `entropy_area_unruh`, ledger 0 to avoid double-count).

Two disciplinary details in the rung-2 node matter for this book's honesty:

*T is not an independent input.* The 2026-08-02 adjudication (T_SUBSUMED) records that in
equilibrium the KMS temperature carries zero freedom (forced, above), and out of equilibrium
there *is no* KMS temperature by definition — an "effective temperature" is a coordinate on
the departure family, not a third axis.

*But the departure family itself is a priced input.* The same adjudication caught a
completeness assertion hiding in a note: the claim that the departure of N from its
KMS-locked value is parameterized by exactly two dials — amplitude ε and the relaxation mode
τ₂ ~ 1/H₀ — is a restriction of the free non-KMS occupation profile n(ω) to a
two-parameter family. That restriction is a separate, stronger input than Gaussianity
(which fixes correlator order, not the ω-profile), and it was **booked** as rung7_wz's third
input (+1), with a standing fence: any further state-shape dial beyond (ε, τ₂) is another
new input, booked at its point of entry.

> **STATUS: ASSUMPTION (booked input: the restriction of the non-KMS occupation profile to
> the (ε, τ₂) two-dial family; +1 at rung7_wz, 2026-08-02, with fence)** — sources:
> `provenance/claims.json` nodes `rung2_kms_gate` (amendment), `rung7_wz` (ledger note).

The surrounding thermodynamic substrate — Boltzmann/Gibbs/von Neumann entropy, the
fluctuation theorems (FDT and the Jarzynski/Crooks work relations), the second law and
H-theorem with Lindblad CP dynamics — is carried in the register as three explicitly
**borrowed** reference-class nodes. Their shared verdict is uniform and worth quoting:
"GRUT derives nothing here."

> **STATUS: ASSUMPTION (borrowed reference classes; GRUT-standing "borrowed"; zero GRUT
> credit)** — sources: `provenance/claims.json` nodes `entropy_foundations`,
> `fluctuation_theorems`, `second_law_h_theorem`.

---

## V.3 · What the formalism gives for free, and what it never gives: existence versus direction

The record's cleanest statement about the arrow of time is a decomposition, hardened in
`ARROW_OF_TIME.md` and register node `arrow_of_time`, and its precision is the point:
irreversibility splits into two logically separable parts, and they have different statuses.

**Existence and magnitude of dissipation are intrinsic to the formalism.** The in-in/CTP
influence functional of a Gaussian bath yields a retarded, upper-half-plane-analytic
self-energy Σ_R(ω), a positive Källén–Lehmann spectral measure, and a positive-semidefinite
noise kernel — operator-identically, with no assumption about the *system's* initial state.
That dissipation occurs, and its magnitude |Im Σ_R|, are genuine outputs.

> **STATUS: RECOVERED (standard in-in/Feynman–Vernon structure on declared inputs; the
> register grades existence-of-dissipation "intrinsic, shown-grade"; scope: linear response,
> Gaussian bath, Born reduction)** — sources: `ARROW_OF_TIME.md` §2,
> `provenance/claims.json` node `arrow_of_time` (boundary_condition).

**Direction is imported — state-dependent, never dynamics-intrinsic.** Nothing above fixes
the *sign* of relaxation. The direction enters through low-entropy data on the past
boundary, in three interchangeable guises that the analysis reduces to one initial-condition
assumption: (1) the past-endpoint contour convention; (2) — decisive — passivity/KMS β > 0
of the bath state, where by Pusz–Woronowicz (1978) KMS with β > 0 *is* passivity *is* "no
work extractable" *is* the second law as a property of the state, and the sign of β in the
coth factor alone decides damping versus anti-damping (a legal population-inverted β < 0
KMS state reverses the arrow); (3) the factorization ρ_S ⊗ ρ_B — the quantum
Stosszahlansatz, the Nakajima–Zwanzig Qρ(0) = 0 deletion. The runnable demonstration
(`calc/arrow_origin.py`, independent-boson model) exhibits the split exactly: Γ(t) = Γ(−t)
identically (the dynamics pick no direction), full Poincaré recurrence at finite mode number
(reversible; irreversibility lives in the continuum limit), and a decay rate set entirely by
the assumed bath state.

> **STATUS: ASSUMPTION (the direction of relaxation is imported via a passive, low-entropy
> past-boundary state — located, not derived; +1 booked at `arrow_of_time`)** — sources:
> `ARROW_OF_TIME.md` §§2–5, `provenance/claims.json` node `arrow_of_time`.

The scope ceiling travels with this. "Direction tracks sign(β) alone" holds *within the
equilibrium KMS class* — which is exactly GRUT's assumed vacuum. Outside KMS (squeezed,
driven-Floquet, active, non-thermal Gaussian baths) there is no single β; N and Im χ
decouple and the direction is set by the full Liouvillian/stationary state. Either way the
direction is set by the assumed reservoir state, never by the time-symmetric dynamics — but
this "closed ceiling" is a result *within the cases surveyed*, explicitly not a universal
no-go theorem. And the record's own anti-laundering note tightens rather than loosens the
import: even the "intrinsic" positivity of §V.3's first half is established relative to a
passive reference state, so the passive-state assumption co-supplies part of what looks
dynamics-intrinsic. The import is more total, not less.

The one GRUT-specific corollary is structural and, in this book's view, the framework's most
honest self-description: the rung-2 gate — built as a *discipline* mechanism — is exactly
the object where the direction enters (β > 0 in the coth factor). GRUT does not bury the
Past Hypothesis; it makes it the visible, labeled gate every kernel passes through. **The
discipline machinery and the imported assumption are the same gate.**

> **STATUS: DERIVED (scoped: an identification within GRUT's declared structure — the
> KMS/FDT admission gate is the locus where the temporal-orientation input enters; it does
> not derive the input)** — source: `ARROW_OF_TIME.md` §6.

---

## V.4 · The Past Hypothesis, audited

The register carries the Past Hypothesis as a borrowed cosmological boundary condition
(node `past_hypothesis`, tier `assumed`, ledger 0 — the +1 cost already counted inside
`arrow_of_time`): the direction of dissipation traces to the bath's low-entropy past, not to
GRUT's time-symmetric dynamics.

> **STATUS: ASSUMPTION (borrowed premise; a low-entropy initial condition imported, not
> shown; ledger 0 to avoid double-count with `arrow_of_time`)** — source:
> `provenance/claims.json` node `past_hypothesis`.

The Final Boss campaign then adjudicated a double-booking the corpus had been carrying: is
the Past Hypothesis a "boundary condition" or an "irreducible input"? The adjudication:
**two answers to two questions**. "Boundary condition" is correct as to *form*.
"Irreducible" is correct only as to *current epistemic status* — Barbour–Koslowski–Mercati
Janus-point candidates exist in the literature, none established, so irreducibility is
UNRESOLVED, not established necessity. Gradient-explanation (why low entropy) and
orientation-explanation (why this direction) are enforced as distinct problems.

> **STATUS: UNRESOLVED (PH irreducibility — an open question the record poses and does not
> settle; contested external discharge programs exist, unassessed)** — sources:
> `RAI_FINAL_BOSS.md` §4 (answer 4), `RAI_GORILLA_T1.md` §XVI-K.

What the audits did settle is sharper than the folklore version of the problem, and it is
the finding this book opened with. Decomposing the "Direction Residue":

- **Absolute temporal orientation was never an input — it is gauge.** Three explicit
  isomorphisms flip it (a parity unitary on L²(ℝ) for the jointly-flipped CLPW package;
  commutant relabeling; Ad J_M). Both mirror worlds are isomorphic.

  > **STATUS: DERIVED (theorem-level, within the confronted corpus; with the flagged
  > OWN-DERIVATION RISK — the no-internal-T lemma and the parity-flip isomorphism are the
  > campaign's own derivations from standard theory, not literature-verified)** — source:
  > `RAI_FINAL_BOSS.md` §3, §4 (answer 16).

- **What survives is exactly one relative Z₂ datum** — the half-line/KMS alignment — which
  is simultaneously CLPW's q ≥ 0-versus-eq-2.1 alignment and Wiesbrock's half-sided-modular
  sign clause. This fuses three of the five audited dressings into one and shows the two
  modular-theoretic targets consume the *same* input in two notations. Status: canonical
  claim 17, as given in §V.0.

- **The datum is empirically invisible** — stated honestly by the campaign itself: the
  mirror worlds are isomorphic, so the bit is invisible *by the very gauge theorems that
  sharpened it*. No empirical discriminator currently exists.

  > **STATUS: CLOSED (gate outcome — "empirical discriminator: NONE currently available";
  > the audit's own verdict, not an in-principle impossibility claim)** — source:
  > `RAI_FINAL_BOSS.md` §4 (answer 14).

- **One apparent input was genuinely dissolved**: state-selection. The crossed product is
  state-independent up to natural isomorphism (Connes cocycle) — an apparent input proven
  not consumed.

  > **STATUS: DERIVED (state-selection dissolved at the crossed-product level; Connes
  > cocycle)** — source: `RAI_FINAL_BOSS.md` §3.

One fork remains open and is precisely posed: the primary reading bills the surviving input
as the relative temporal datum *alone*; the hostile reading bills it as the *pair*
{a supplied clock-like system gauged into the constraint} + {the relative-orientation
datum}. Whether the clock-slot is a second irreducible input is exactly what the SLOT test
(a rigorous single-patch G_N → 0 limit, CLPW §4.3) would decide; the RESIDUE test — derive
the half-line/KMS alignment from unoriented hypotheses, or prove the functorial no-go —
would decide the residue framing itself. Both are posed, decidable, and unrun.

> **STATUS: UNRESOLVED (the RESIDUE and SLOT tests: posed, decidable, unrun; reopening keys
> 1–3 of the freeze)** — sources: `RAI_FINAL_BOSS.md` §4 (answers 15, 17–19),
> `GRUT_PROGRAM_FREEZE.md` §5.

Finally, the honesty caps that the record itself welds onto this whole section. The
Dialectic Chamber found that the "every closure consumed an input" conservation pattern was
partly *preloaded as doctrine* (`POSTULATE_MAP.md`'s anti-falsification clause), and that
the apparatus *instantiates the arrow it was hunting* — ordered rounds, immutable-past
preregistration, retarded verdicts — so an unquantified part of the observed conservation is
self-generated. The chamber's closing confidence split for the conserved one-sidedness:
genuinely physical ~40% · vocabulary-bound ~25% · investigation-generated ~20% · emergent
~15%. The per-case record is established; its universal generalization is capped.

> **STATUS: audited per-case record with capped generalization ("ESTABLISHED as a per-case
> record… its generalization is capped SUPPORTED and can be removed without contradicting
> established evidence"); the universal form — UNRESOLVED** — source:
> `RAI_DIALECTIC_CHAMBER.md` §2 (X1), §4.

---

## V.5 · Borchers–Wiesbrock at the level the record supports

The modern modular-theoretic material enters the record through two confronted targets, and
the record's use of both is deliberately narrow. Neither is GRUT mathematics; both are
reconstructed from primary sources (Borchers 1992; Wiesbrock 1993 with erratum, completed
Araki–Zsidó 2005; CLPW, arXiv:2206.10780), and both received the same audited
classification: **B-INPUT-RELOCATION** — the unexplained temporal input moves; it is not
discharged.

**The Wiesbrock structure.** From four primitives — a Hilbert space H; a proper inclusion
N ⊂ M; a common cyclic-separating vector Ω; and the *signed* half-sided-modular clause —
the theorem derives: essential self-adjointness and **positivity** of
P = (1/2π)(ln Δ_N − ln Δ_M); the translation group U(a) with U(a)Ω = Ω
(vacuum-invariance an *output*, not an input); the ax+b relations; the subfactor tunnel; and
type III₁ rigidity (no tracial or semifinite algebra admits a proper half-sided-modular
inclusion at all).

The load-bearing fact for this book — verified independently on the paper's own page images
after one audit stage was blocked by a classifier (recorded, not bypassed) — is this:
**positivity of P follows from the inclusion order alone and is orientation-free.** The
naive objection "the past-sided version has negative energy" is FALSE: the canonical P is
positive in *both* orientations, because the form inequality follows from the inclusion
order, and the two orientation classes are exchanged by commutant relabeling and by Ad J_M
(with J_M Ω = Ω — the state never flips; the algebra–flow relation does). **The arrow is
carried solely by the signed half-sided-modular clause.** Positivity buys no direction.

> **STATUS: RECOVERED (borrowed theorem-grade mathematics; audited verdict
> B-INPUT-RELOCATION — positivity from inclusion order alone is orientation-free; the
> orientation is carried entirely by the signed hsm clause, and it is the same input as the
> half-line/KMS alignment in a second notation)** — source: `RAI_FINAL_BOSS.md` §§0, 2, 3.

**The CLPW crossed product.** The type III₁ → II₁ conversion (adjoining an observer clock
with q ≥ 0, gauging into Ĥ = H + q) is established mathematics (Takesaki 1973) and
conditionally discharges the no-trace gap — the one gap genuinely discharged in the
campaign. But the discharge is purchased: delete the clock and the invariant algebra is
ℂ·1; the clock slot is generic, produced by nothing in the dynamics, conceded external by
CLPW themselves; and the modular-identification constraint (eq 2.1) is asserted by
BW/Sewell analogy, not proved in-paper. The register's u3 question — why is there a split at
all — relocates into that postulate.

> **STATUS: RECOVERED (borrowed; audited verdict B-INPUT-RELOCATION: the unexplained input
> moves, it is not discharged)** — canonical claim 23; source: `RAI_FINAL_BOSS.md` §1.

**The one conditional mathematical home for the old "universal refresh" intuition.** The
speculative self-recording/refresh picture from GRUT's early phase found exactly one
theorem-grade instantiation: the Wiesbrock tunnel M ⊃ N ⊃ γ(M) ⊃ γ(N) ⊃ … is "refresh
with persistent records" (monotone nesting = record persistence; the whole tower generated
by one datum; III₁ rigidity certifies non-genericity). But the refresh *direction* is the
supplied hsm sign bit in tunnel dressing; the input-free version is refuted in the
confronted corpus.

> **STATUS: HYPOTHESIS (freeze class SPECULATIVE, barred from load-bearing; one conditional
> mathematical home, direction supplied; the input-free version REFUTED in the confronted
> corpus)** — sources: `RAI_FINAL_BOSS.md` §4 (answers 5–6), `GRUT_PROGRAM_FREEZE.md` §3.

The net of this section, in the record's own summary: two doors opened at theorem level; one
gap discharged conditionally; **one input fused, relocated twice, and named exactly.**

---

## V.6 · The finite-memory bet: a reversed history, stated on its face

The corpus charter requires this history told as history, not as a footnote.

The bet: the vacuum has *finite* memory — in strongest form, single-pole relaxation with a
derived memory time. Its one in-house quantitative support was the tt_worldline decay
computation (⟨h²⟩ appearing to decay, 127 → 0.002). The Gorilla T1 negative-control
campaign found the computation carried a spurious 1/(a₁a₂) factor that collapses the
correlator, and — the standing methodological lesson — the sole prior validation gate sat at
t = 0, the unique point where buggy and corrected versions agree to < 10⁻¹²: *a check
placed at the blind point*. Recomputed in two independent formulations agreeing to 10⁻¹³,
the corrected correlator asymptotes to the constant ln3/(4π²) in a fixed comoving band and
grows under the comoving-IR/physical-UV prescription. The support did not weaken; it
**REVERSED**.

The prior ("something surely forces finite memory") was then removed by enumeration: all
seven candidate memory mechanisms examined deliver either *no* memory or *unbounded,
scale-free* memory. The one genuine finite rate anywhere in the examined record — the KMS
rate τ = β/2π — has β conditional on a supplied static patch, the very selection nothing
derives. The campaign's summary sentence: **what de Sitter forces is infinite, scale-free
memory — the opposite shape of the asserted kernel.** The reformulated chain
(relational structure → inclusion → susceptibility → kernel) independently terminates on an
*occupied* kernel class — scale-invariant open quantum systems (arXiv:2605.22919),
power-law kernels, no characteristic timescale.

> **STATUS: ASSUMPTION, with REVERSED history on its face (the in-house "no memory time"
> computation was reversed; exact dS free-field theory forces infinite scale-free memory)**
> — canonical claim 18; sources: `RAI_GORILLA_T1.md` §§XVI-B, XVI-H, XVI-J.

The downstream single-pole claim (rung 3) inherits this honestly. The register's long node
history — anchor-class rulings, the Class A (analytic, collisional) versus Class B
(free-streaming, Weinberg branch cut) fork, the free-field infinite-shear-viscosity
argument, the near-circularity flag ("GRUT's finite-memory premise essentially IS the
Class-A choice") — converges on: undetermined, and gated on the unpinned system/bath split.

> **STATUS: UNRESOLVED (anchor-class, derived-pending; pole-vs-cut open; the Tier-4
> computation found a CUT, not a pole, at flat scope)** — canonical claim 4; sources:
> `provenance/claims.json` node `rung3_single_pole`, `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md`
> §4.

The Dialectic Chamber drew the consequence at framework level and this corpus does not
soften it: the chamber's recorded verdict on GRUT's central bet is **REFUTED** — "zero rate
came exact where derived, and every finite rate was purchased — the negation of an intrinsic
finite memory." That verdict is a W-0 research finding: the register was not modified by it,
and the framework is henceforth carried (per the freeze) with finite memory as a downgraded
postulate, not a supported structure.

> **STATUS: REVERSED / CLOSED (chamber verdict, W-0, register untouched: the finite-memory
> kernel as a *supported structure* is destroyed; the postulate survives only as a declared,
> priced stance)** — sources: `RAI_DIALECTIC_CHAMBER.md` §3, §5; `GRUT_PROGRAM_FREEZE.md`
> §4; `GRUT_MODEL_FRAMEWORK.md` §2.

---

## V.7 · Where the memory question actually lives — and why the record refuses to answer it there

A subtlety of scope, derived by the ROOT-1 campaign, keeps both sides of the memory question
honest. The flat-scope kernel results (Books II and IV) are T=0-graded vacuum objects valid
at ω ≫ H. The kernel GRUT actually asserts — finite memory, relaxation at ω ~ H₀ — lives
at ω ≲ H. ROOT-1 §3 found that region not merely unresolved but **UNASKABLE at current
declarations**, on four independent obstructions, each separately sufficient:

- **O1 — the boundary is derived, not declared**: ε_H = (104/9)H²/ω² with 104/9 exactly the
  ratio of the two computed absorptive coefficients; the refusal at ω = 3.3993H is a result
  of the calculation and cannot be loosened by declaration.
- **O2 — no frequency variable exists there**: the time-translation flow (§V.1) is priced,
  and its only named discharge (the static patch) is exhibited false for the TT graviton on
  the declared FLRW patch; ρ(ω), J(ω), Im χ(ω) are not defined objects there.
- **O3 — an unregulated IR log at O(H²)**: nine candidate regulators swept, zero licensed.
- **O4 — thermal blindness, derived**: the candidate memory floor is thermal, but dS
  thermality is invisible to the H-grading — exp(−2πω/H) vanishes to all orders, and
  coth(πω/H) − 1 has vanishing limit and vanishing first and second H-derivatives at fixed
  ω > 0. The declared scheme is provably blind to the effect it would be asked to
  adjudicate.

> **STATUS: DERIVED (obstruction set: the ω ≲ H regime is UNASKABLE at current
> declarations — the scheme can return neither a floor nor its absence; with the standing
> guard: any graded-calculation claim of "no memory floor" must be refused as definitional)**
> — source: `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §3.

Two consequences. First, the finite-memory reversal of §V.6 and the O4 obstruction compose
into a strict discipline: the record neither asserts a memory time nor asserts its absence
*at the claimed scale* — the free exact-dS results force scale-free memory in the free
theory, and the interacting, thermal, low-frequency object has never been computed where the
claim lives ("the pole was never looked for where it was claimed"). Second, the temperature
needed for any such computation is not missing — T_dS = H/2π is on the record (§V.2) — what
is missing is a licence to use it, a method non-perturbative in H, and a proved stationary
reduction.

---

## V.8 · The surviving sentence, with its grades welded on

What survived every deletion test in the temporal sector is one physics sentence, and the
program's freeze mandates that it never travel without its grades. In the Gorilla T1
formulation (GRUT-free, AQFT-free, split-free, response-free):

> "On a de Sitter background, the massless minimally coupled wave equation has the constant
> as an exact solution: a disturbance therefore leaves a permanent remnant of fixed size
> (H²/4π) throughout the interior of its light cone, and nothing in the equation sets a
> time for that remnant to fade. Every fading-time and every one-sidedness in time that
> appeared anywhere in this record was supplied to the mathematics — a mass, a temperature,
> a chosen function, a condition placed on the past — never produced by it. **Persistence
> came free; forgetting and direction were always paid for.**"

The grades, as the record states them: the first clause is a controlled derivation with
independent numerical and literature confirmation, *conditional on the background*; the
second is an induction over the cases examined — not a theorem, and its universal form is
exactly what the campaign's one-sided apparatus is least able to check.

> **STATUS (first clause): DERIVED (exact dS; gapped only at conformal coupling)** —
> canonical claim 7, the constant retarded tail H²/4π and the Δ₋ = 0 zero-mode complex
> (sources: `RAI_GORILLA_T1.md` §XVI-G, §XVII; `GRUT_PROGRAM_FREEZE.md` §3).
>
> **STATUS (second clause): audited per-case induction, not a theorem; its universal form —
> UNRESOLVED (the one-sided-apparatus cap applies)** — sources: `RAI_GORILLA_T1.md` §XVII
> (grades), `GRUT_PROGRAM_FREEZE.md` §7.

The referent of the persistence clause is itself conditionally held: the whole adverse
free-field complex flows from one exact zero (Δ₋ = 0), and the record's own mutation
controls show any perturbation lifts it — an interaction-induced m_eff² = 0.1H² returns a
finite rate 0.034H through the verified Starobinsky–Yokoyama channel. The computation that
decides whether persistence survives interaction — O2, the interacting graviton zero-mode —
is undone, and is reopening key 1 of the freeze.

> **STATUS: UNRESOLVED (O2, the interacting graviton zero-mode: undone; decides the fixed
> point's referent — "protected" strengthens the one surviving derived structure, "lifted"
> fells it)** — sources: `RAI_GORILLA_T1.md` §XVI-N, `GRUT_PROGRAM_FREEZE.md` §5.

---

## V.9 · Passivity, the second law, and the w(z) story

The temporal sector's one contact with observational cosmology runs through passivity, and
the record's handling of it is a case study in the discipline this book documents — two
over-claims, one in each direction, both retracted.

The structure (rung7_wz, rung7_w2, rung7_w3): out of equilibrium, FDT no longer locks N to
K_R, and a relaxing χ(ω) yields an effective dark-energy equation of state w(z). What the
second law actually fixes, after the verify-the-verifier corrections of 2026-06-29:

- **The side, per branch**: passivity ζ = lim Im χ/ω ≥ 0 forces Π = −3ζH ≤ 0, so the
  dissipative branch sits at w ≤ −1 and the reactive branch at w ≥ −1; entropy production
  σ = Π²/(ζT) ≥ 0 forbids a within-branch crossing of w = −1. This is the robust
  second-law-supported piece — the **no-crossing support**.
- **Not the slope**: σ is quadratic in Π, blind to dΠ/dt, so the sign of w_a rides on
  sign[d(ζH)/da], which the dissipation inequality never touches. Both passivity-consistent
  readings exist; both prior sign-claims ("w_a > 0, wrong for DESI" and "w_a ≤ 0,
  second-law-fixed") were retracted as over-claims. The sign is genuinely open; two
  non-theorem arguments lean DESI-ward, banked as notes, not tiered claims.

> **STATUS: UNRESOLVED (to-derive, default-BROKEN: the no-crossing no-go is the robust
> second-law-supported piece but is held at to-derive — a no-go cannot outrank its anchor,
> and rung3 is open; the w_a sign is indeterminate in-house, with both over-claims retracted
> on the record)** — sources: `provenance/claims.json` nodes `rung7_w2_wa_sign`,
> `rung7_w3_nocrossing_export`, `rung7_wz`.

The sourced prediction and the priced escape are canonical:

> **STATUS: w = −1 flat — DERIVED (within the choices x = 0 / pure-TT: the sourced cosmology
> statement); evolving w(z) — HYPOTHESIS (requires the inserted, un-sourced τ₂ ~ 1/H₀,
> priced +2)** — canonical claim 13; source: `provenance/claims.json` node `rung7_wz`.

And the class-level discriminator that survives contamination-clean — every purely
relaxational kernel (Debye, multi-pole, Cole–Cole) stays on one side of w = −1; only an
oscillatory pole pair crosses — is menu-scope exclusion shared by the whole passive class.
Any observed crossing falsifies the entire family at once, GRUT included; this is the
standing kill condition, held by nature.

> **STATUS: DERIVED (class-level; explicitly not GRUT-specific)** — canonical claim 15;
> sources: `RAI_GORILLA_T1.md` §XVI-M, `GRUT_MODEL_FRAMEWORK.md` §5.

The thermodynamic reading of this story belongs in this book: GRUT's second-law structure is
entirely the borrowed passivity/KMS structure of its bath state (§§V.2–V.3). Where that
structure binds (the side; the no-crossing support), the record uses it and marks the
conclusions as gated; where it does not bind (the slope), the record says so and refuses the
number. GRUT nowhere derives the second law — node `second_law_h_theorem`, borrowed — and
its dark-energy statements inherit exactly the second law it assumed.

---

## V.10 · The ledger of temporal structure: derived versus assumed, in one place

This book closes with the absence map the charter requires — the temporal sector sorted by
what actually carries each piece.

**Derived, at declared scopes:** T_dS = H/2π given the background (canonical 3); the
existence-versus-direction *decomposition* as a located import (scoped, §V.3); absolute
temporal orientation as gauge (theorem-level, campaign-own, §V.4); state-selection dissolved
at the crossed-product level (§V.4); the exact dS constant tail H²/4π (canonical 7); the
UNASKABLE obstruction set including the O4 thermal-blindness derivation (§V.7); the
side-not-slope second-law structure (gated, §V.9).

**Recovered (borrowed, with the honesty note):** the influence-functional form itself
(canonical 1); FDT/KMS as identities; the Borchers–Wiesbrock and CLPW theorem chains
(canonical 23); the whole entropy/fluctuation-theorem/second-law substrate (three borrowed
nodes, "GRUT derives nothing here").

**Assumed, priced, on the record:** the responsive-medium ontology (+1); the background
time-translation flow (+1); the KMS/FDT lock as admission gate (canonical 2); the
(ε, τ₂) restriction (+1); the passive low-entropy past-boundary state — the Past
Hypothesis, in whichever of its five audited dressings a formulation wears (+1 at
`arrow_of_time`; canonical 17); finite memory itself, with its reversal on its face
(canonical 18).

**Unresolved, posed, unrun:** pole-versus-cut at the claimed scale (canonical 4); PH
irreducibility; the RESIDUE and SLOT tests; O2; the w_a slope; the universal form of
"forgetting and direction were always paid for."

**Predicted: EMPTY** — nothing in this book's sector has earned that word (canonical 21;
Book IX governs entry).

The single sentence this book exists to defend: *GRUT's temporal structure is standard
temporal structure, borrowed openly, with exactly one number forced within declarations
(T_dS = H/2π), one genuinely new class-level structural finding elsewhere in the corpus
(canonical 24, Book IV), and one honestly named unexplained datum at the bottom — the
half-line/KMS alignment — which every confronted closure consumed and none produced.* The
program's contribution here is not an arrow derived; it is an arrow *located*, priced,
audited through five dressings, and pinned to a decidable pair of open tests.

---

## Sources drawn from

- `books/CORPUS_CHARTER.md` (status vocabulary, canonical table)
- `GRUT_MODEL_FRAMEWORK.md` (§§2–7)
- `GRUT_PROGRAM_FREEZE.md` (ledger, stopping rule, reopening conditions, §7 grades)
- `provenance/claims.json` — register nodes: `rung1_ontology_finite_memory`,
  `rung1_inin_formalism`, `rung2_kms_gate`, `rung3_single_pole`,
  `background_time_translation_flow`, `arrow_of_time`, `past_hypothesis`,
  `entropy_foundations`, `fluctuation_theorems`, `second_law_h_theorem`,
  `entropy_area_unruh`, `rung7_wz`, `rung7_w2_wa_sign`, `rung7_w3_nocrossing_export`
- `RAI_FINAL_BOSS.md` (CLPW / Wiesbrock reconstruction; the direction residue; the nineteen
  answers)
- `RAI_DIALECTIC_CHAMBER.md` (the survivor X1; the gorilla; the confidence split; the
  chamber's REFUTED verdict, W-0)
- `RAI_GORILLA_T1.md` (the tt_worldline reversal; the seven-mechanism enumeration; §XVII and
  the graded surviving sentence)
- `ARROW_OF_TIME.md` (the existence/direction decomposition; `calc/arrow_origin.py` as its
  runnable demonstration — cited, not re-run here)
- `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` (§3: the four obstructions incl. O4 thermal
  blindness; §4 pole-vs-cut; the standing guard)
- `gate/kms.py` (the admission gate as executable code)

External literature is cited only as the record cites it: CLPW = arXiv:2206.10780;
scale-invariant open quantum systems = arXiv:2605.22919; Borchers 1992, Wiesbrock 1993 (+
erratum), Araki–Zsidó 2005, Takesaki 1973, Pusz–Woronowicz 1978, Partovi 2008, te Vrugt
2022, Vikman 2005, Surya et al. 2019, Callen–Welton 1951, Kubo 1966, Feynman–Vernon 1963,
Schwinger 1961, Keldysh 1964, Calzetta–Hu, Jarzynski 1997, Crooks 1999, Jacobson 1995,
Albert 2000 — all via the register's `sources` keys and the audit documents' own citations.

## Gaps in this book

1. **The memory kernel at its claimed home (ω ≲ H) has never been computed** — the region
   is UNASKABLE at current declarations (four obstructions, §V.7). Nothing in this book can
   say whether the vacuum has a memory floor there; the record can currently return neither
   a floor nor its absence.
2. **No GRUT content exists for entropy production, the H-theorem, or fluctuation theorems
   beyond borrowed nodes.** All three substrate nodes are marked "GRUT derives nothing
   here." There is no GRUT account of coarse-graining, no in-house entropy functional, no
   Jarzynski/Crooks-level result. UNMAPPED beyond the borrowed reference classes.
3. **The Past Hypothesis's magnitude is untouched.** The record locates the direction input;
   it says nothing about *how* low the past entropy was, the cosmological entropy budget, or
   gradient-explanation in Boltzmann's quantitative sense. The gradient/orientation split is
   enforced; only the orientation half was audited to residue level.
4. **PH irreducibility is UNRESOLVED**: BKM/Janus-point-type discharge programs are named,
   contested, and unassessed by this record.
5. **The RESIDUE test and the SLOT test are unrun.** The book's central result (canonical
   17) is scoped to the confronted corpus; unconfronted routes (thermal time, deeper
   passivity, dS/CFT, cosmological measure programs) could in principle derive the surviving
   datum. The functorial half of the no-go is open; the within-triple half is campaign-own
   and awaits independent verification.
6. **O2 (the interacting graviton zero-mode) is undone**, so the persistence clause of
   §V.8's surviving sentence has a conditionally held referent.
7. **The w_a slope sign is open**; the de Sitter trace-sector effective stress tensor that
   would decide it (and would graduate or fail the no-crossing no-go) has not been computed.
8. **Two campaign-own derivations are not literature-verified** (the no-internal-T lemma;
   the parity-flip isomorphism) — an error there weakens the *elimination* half of the
   direction-residue verdict (the "absolute orientation = gauge" claim), flagged by the
   campaign itself.
9. **One audit stage was blocked by an API classifier** (the dedicated `wiesbrock:attack`
   stage, three refusals, request IDs journaled); its role was covered by two independent
   passes that agree on the three load-bearing claims, but the dedicated hostile pass itself
   does not exist.
10. **The self-generated-arrow contamination is unquantified**: the chamber found the
    apparatus instantiates the arrow it hunts (ordered rounds, immutable-past
    preregistration, retarded verdicts); how much of the observed "every closure consumed an
    orientation" pattern this manufactures is bounded only by the recorded confidence split
    (~40/25/20/15), not by a measurement.
11. **Non-equilibrium GRUT thermodynamics beyond the (ε, τ₂) family is fenced, not
    developed**: any further state-shape dial is a new input by standing rule, and none has
    been proposed, priced, or explored.
