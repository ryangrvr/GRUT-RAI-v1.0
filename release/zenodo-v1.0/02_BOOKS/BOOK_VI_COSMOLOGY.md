# BOOK VI — COSMOLOGY

> *WORKING DRAFT — part of the GRUT working corpus; statuses per `books/CORPUS_CHARTER.md`;
> subject to chapter-by-chapter audit; nothing here banks.*

**GRUT Books — Working Edition v1.0** · D. Ryan Grover · 2026-09-07 · release `zenodo-v1.0` · Markdown is the authoritative source; the PDF is generated from it. Drafted from the frozen record by the RAI builder (Claude, Anthropic) under owner direction — this edition is a publishing pass only: formatting, navigation, and metadata; no claim strengthened or weakened for publication.

## Contents

- [VI.0 · Why this sector is treated ruthlessly](#vi0--why-this-sector-is-treated-ruthlessly)
- [VI.1 · Background cosmology](#vi1--background-cosmology)
  - [VI.1.1 The background is an input, not a product](#vi11-the-background-is-an-input-not-a-product)
  - [VI.1.2 The sourced background equation of state: w = −1, flat](#vi12-the-sourced-background-equation-of-state-w--1-flat)
- [VI.2 · Linear perturbations and structure formation](#vi2--linear-perturbations-and-structure-formation)
  - [VI.2.1 Linear cosmology = ΛCDM at the chosen point](#vi21-linear-cosmology--λcdm-at-the-chosen-point)
  - [VI.2.2 The μ = 4/3 self-exclusion — the sector's genuine earned no-go](#vi22-the-μ--43-self-exclusion--the-sectors-genuine-earned-no-go)
  - [VI.2.3 The interior window — bounded by a measurement, not deleted by fiat](#vi23-the-interior-window--bounded-by-a-measurement-not-deleted-by-fiat)
- [VI.3 · Dark energy: the sourced prediction, and the hypothesis that must not be](#vi3--dark-energy-the-sourced-prediction-and-the-hypothesis-that-must-not-be)
  - [VI.3.1 The sourced statement](#vi31-the-sourced-statement)
  - [VI.3.2 Evolving w(z): a hypothesis with a price tag](#vi32-evolving-wz-a-hypothesis-with-a-price-tag)
  - [VI.3.3 The wₐ-sign history: two retractions, told on their face](#vi33-the-wₐ-sign-history-two-retractions-told-on-their-face)
  - [VI.3.4 The no-crossing no-go: robust, and correctly held below its ceiling](#vi34-the-no-crossing-no-go-robust-and-correctly-held-below-its-ceiling)
- [VI.4 · The kernel-class discriminator — what the sector actually exports](#vi4--the-kernel-class-discriminator--what-the-sector-actually-exports)
- [VI.5 · The DESI anti-signature — the live threat](#vi5--the-desi-anti-signature--the-live-threat)
- [VI.6 · Derived structural results in the cosmological sector](#vi6--derived-structural-results-in-the-cosmological-sector)
  - [VI.6.1 The spectral law s = 5](#vi61-the-spectral-law-s--5)
  - [VI.6.2 The exact de Sitter constant tail](#vi62-the-exact-de-sitter-constant-tail)
  - [VI.6.3 What the constant tail did to the finite-memory bet](#vi63-what-the-constant-tail-did-to-the-finite-memory-bet)
  - [VI.6.4 The Γ_T closure — the one cosmological number, computed to refuse](#vi64-the-γ_t-closure--the-one-cosmological-number-computed-to-refuse)
- [VI.7 · The ΛCDM comparison, stated whole](#vi7--the-λcdm-comparison-stated-whole)
- [VI.8 · Absence map — where the record is silent](#vi8--absence-map--where-the-record-is-silent)
- [Sources drawn from](#sources-drawn-from)
- [Gaps in this book](#gaps-in-this-book)

---

---

## VI.0 · Why this sector is treated ruthlessly

Cosmology is where the responsive-vacuum program made its most attractive-sounding claims,
and it is the sector where the program's own audit apparatus did the most damage to them. In
the committed record this sector contains: two retracted sign claims (one in each direction),
a headline exclusion significance retired as impossible in its own channel (~32σ → ~2.0σ),
a "wrong equation of state" verdict on the mechanism proposed to rescue an evolving dark
energy, and a standing fence that names the import of an unsourced second timescale for what
it is — laundering. The corpus charter therefore requires that this book be built the way the
register itself came to be built: the sourced statement first, the inserted structure priced,
the retractions on their face, and the ΛCDM comparison stated as what it is — compatibility
at a chosen point, not correspondence evidence.

The one-sentence summary, which everything below unpacks: **GRUT's sourced cosmology is
ΛCDM.** The framework's only fully-sourced dark-energy statement is w = −1 flat; its linear
cosmology reproduces ΛCDM at the chosen projector point; every evolving-dark-energy shape
requires an inserted, unsourced input; and the sector's genuine products are two directional
no-gos (the μ = 4/3 self-exclusion and the kernel-class no-crossing discriminator), a pair of
derived structural results about the vacuum kernel (the s = 5 spectral law and the exact dS
constant tail), and one live external threat (the DESI phantom-divide crossing) that runs
*against* the framework. The PREDICTED set is empty here as everywhere.

> **STATUS: EMPTY (nothing has earned entry; Book IX governs entry)** — canonical claim 21,
> restated for this sector: no cosmological claim in this book carries the label PREDICTED
> (source: `books/CORPUS_CHARTER.md`, `GRUT_PROGRAM_FREEZE.md`).

---

## VI.1 · Background cosmology

### VI.1.1 The background is an input, not a product

GRUT does not derive the background universe. The de Sitter-like late-time background on
which every cosmological computation in the record runs is a declared input.

> **STATUS: ASSUMPTION (EMPIRICAL-INPUT — "the dS-like background where used", per the
> freeze ledger's EMPIRICAL-INPUTS row)** — (source: `GRUT_PROGRAM_FREEZE.md` §3).

Nor does the framework determine the cosmological constant. The register carries this as a
marked-open field, deliberately distinguished from both "borrowed input" and "GRUT fill":

> **STATUS: UNRESOLVED (register: tier `to-derive`, sub_status "open field; GRUT does not
> determine Lambda — marked-open, not claimed")** — the value of Λ is undetermined by the
> responsive-vacuum framing; the cosmological-constant problem is inherited, posed, and not
> filled (source: `provenance/claims.json` node `lambda_undetermined`).

What the background *does* yield, given the declaration, is its temperature:

**T_dS = H/2π.**

> **STATUS: DERIVED (within declarations: forced by Hadamard/KMS on the declared
> background)** — canonical claim 3; Gibbons–Hawking, borrowed with zero freedom; the
> register's only background-sector credit (source: `books/CORPUS_CHARTER.md`;
> `GRUT_PROGRAM_FREEZE.md` §3).

### VI.1.2 The sourced background equation of state: w = −1, flat

The framework's admitted gravitational response is pure spin-2 transverse-traceless
(the `p_tt_ansatz` projector, with the scalar-to-tensor admixture set at x = 0). The spin-0 /
trace sector is the one that carries a bulk (volume) response; the TT projector annihilates
it. Consequently ζ_bulk = 0, the dissipative pressure correction Π = −3ζH vanishes, and
(w+1) = Π/ρ = 0 — at *background* order, not merely at linear order. The vacuum sits exactly
at the de Sitter equilibrium w = −1 and stays there.

> **STATUS: DERIVED (within the choices x = 0 / pure-TT: the sourced cosmology statement)**
> — canonical claim 13, first half; the derivation chain is `p_tt_ansatz` → ζ_bulk = 0 →
> (w+1) = 0 at background order (source: `calc/wz_sign.py`, `calc/RESULTS_wz_sign.md` §(iii);
> `provenance/claims.json` node `rung7_w2_wa_sign`).

The two choices this statement rests on are themselves registered inputs, and their statuses
travel with the claim:

> **STATUS: ASSUMPTION (STRUCTURAL-SELECTION — CHOSEN, unanimous five-angle interrogation;
> not forced)** — canonical claim 8, the TT-only projector: diffeomorphism invariance stops
> one condition short of forcing tracelessness; the 2026-08-02 interrogation returned CHOSEN
> (source: `provenance/claims.json` node `p_tt_ansatz`; `BRIEF_p_tt_interrogation.md`).

> **STATUS: ASSUMPTION (STRUCTURAL-SELECTION; x_no_pin: the action carries a family, pins
> nothing)** — canonical claim 9, the x = 0 scalar-to-tensor choice: the admissible set is an
> amplitude-homogeneous cone; excluding the x = 1 endpoint (§VI.2.2) does not select the
> x = 0 point (source: `provenance/claims.json` nodes `x_no_pin_theorem`, `mu_linear`).

So the honest reading of "GRUT's background cosmology is ΛCDM" is: *given* an empirically
input background, a chosen projector, and a chosen point in an unpinned family, the framework
reproduces the cosmological constant it was handed. It also inherits, undischarged, the
cosmological-constant problem (`calc/RESULTS_wz.md` §A states this directly: the UV-cutoff
single-pole vacuum "reproduces Λ, inherits the cosmological-constant problem").

---

## VI.2 · Linear perturbations and structure formation

### VI.2.1 Linear cosmology = ΛCDM at the chosen point

At the chosen point x = 0 (pure-TT), the linear-cosmology bookkeeping — modified-Poisson
μ(a,k), lensing Σ(a,k), gravitational slip η = Ψ/Φ — collapses to the ΛCDM values exactly:
**μ = Σ = η = 1.** Growth of structure, lensing, and the ISW effect are then standard; GRUT
adds nothing and subtracts nothing at linear order.

> **STATUS: DERIVED (conditional leg — GIVEN the CHOSEN c₀ = 0 / x = 0; register tier
> `derived-pending`, sub_status `no_go_export`; empirically SELECTED by exclusion, not
> derived-clean)** — the register is explicit that "μ = 1 likely IS right, but NOT because
> 'TT annihilates scalars'"; it survives because the alternative endpoint is excluded
> (§VI.2.2), which is a no-go export, not a positive derivation (source:
> `provenance/claims.json` node `mu_linear`; `calc/mu_linear.py`, bookkeeping only).

Two pieces of register history are part of this claim's honest presentation. First, the
graduation route "derive the scalar-sector vanishing from the action without inserting P^TT"
was run in 2026-08-02 and **answered against** (the projector is CHOSEN); the only surviving
graduation route relocates the assumption to the rung3 trace correlator at the price of a new
+1 — relocation, not discharge. Second, the register carries, at the owner's order, a
verbatim dissent against its own tier: the argument that "a conditional on a demonstrably
arbitrary choice is assumed-conditional, not derived-pending," recorded precisely because
*linear cosmology = ΛCDM is the register's most-quoted headline* and a stale tier at this
node would do more downstream laundering work than anywhere else. An armed tier trigger
stands: if rung3 resolves against the trace-correlator route, the node moves
`derived-pending` → `assumed` without re-litigation (source: `provenance/claims.json` node
`mu_linear`, `boundary_condition`).

### VI.2.2 The μ = 4/3 self-exclusion — the sector's genuine earned no-go

The modification GRUT's own conformal coefficient would naively suggest is the trace-only
endpoint μ = 1 + α = 4/3. The framework *excludes its own naive suggestion*:

> **STATUS: CLOSED (self-exclusion: separate-universe consistency + low-ℓ ISW)** — canonical
> claim 14, verbatim (source: `books/CORPUS_CHARTER.md`; `provenance/claims.json` node
> `mu_linear`; `calc/isw_exclusion.py`, `calc/RESULTS_isw_exclusion.md`).

This is the sector's one genuinely earned deflationary result, and its computed anatomy
matters because its history is a model case of the program's discipline working on itself:

- **The structural leg (separate-universe consistency).** A super-horizon adiabatic mode is a
  shifted FRW background whose comoving-gauge growing mode (δ ∝ a in EdS) is fixed by the
  Friedmann equation; super-horizon μ = 4/3 forces δ ∝ a^1.186 — internally inconsistent,
  dataset-independent. EdS-quantified 2026-08-03: p(4/3) − p_SU = +0.186 ≠ 0. Scored
  **usable-but-conditional** — the owed residue (adiabaticity + the presupposed dilatation
  bridge, which the L0 screen scored "relocated, not derived") is named, not hidden
  (source: `calc/RESULTS_isw_exclusion.md`, Part 3 / PART E).
- **The empirical legs.** ISW–galaxy cross-correlation: **computed ~2.0σ** (1.97 central,
  Σ-corrected; kill-condition band ~0.6–4.8). DESI Σ₀ lensing: ~3.5σ, independent; joint
  ~4σ-class. The low-ℓ TT auto-power channel is a **prospect, not a leg** (estimate-grade,
  order-10²σ-class at x = 1, filter/normalization-sensitive; its rigorous calc is owed).
- **The retired number.** The previously banked ~32σ ISW exclusion is **retired**: for a
  signal-suppressing model the cross-channel exclusion is structurally capped at ~9–12σ, so
  a 32-class number was never possible in that channel; and the banked mechanism was
  backwards (μ > 1 *strengthens* growth and suppresses potential decay — the model suppresses
  the positive ΛCDM-like signal to ~0.57× the template; the exclusion operates because the
  data detect the positive signal). The correction and the same-wave firewall's Σ-factor
  repair (B1) are both on the record (source: `calc/RESULTS_isw_exclusion.md`).

> **STATUS: REVERSED (the banked ~32σ and its mechanism direction; retired 2026-08-03 by
> `calc/isw_exclusion.py`; the exclusion itself SURVIVES multi-leg at re-graded strength)**
> — part of model history, stated on its face (source: `calc/RESULTS_isw_exclusion.md`;
> `provenance/claims.json` node `mu_linear`, `overturning_computation`).

The signature-audit classification of the surviving result is exact: this is
**signature-removing**, not predictive. "GRUT *forbids* the μ = 4/3 modification its own
coefficient naively suggests; linear cosmology = ΛCDM." It removes a would-be signature and
predicts no new one (source: `SIGNATURE_AUDIT.md`, audit table row 4; `NO_GO_LEDGER.md`
entry 2).

### VI.2.3 The interior window — bounded by a measurement, not deleted by fiat

Because the projector is CHOSEN rather than forced, the continuous {shear, bulk} family
*between* the endpoints (x = 0, TT-only, μ = 1; x = 1, trace-only, μ = 4/3, excluded) is
empirically live. The 2026-08 interior wave replaced "closed by fiat" with a computed window:
the DESI Σ₀ lensing bound binds at **x < ~0.59** (central-inputs, loose-upper per the named
F-MAP fence), i.e. **μ − 1 ≲ 0.20**, Σ − 1 ≲ 0.10; the owed TT-auto calculation would likely
re-tighten this substantially.

> **STATUS: UNRESOLVED (register tier `to-derive`, default-BROKEN;
> "constrained-to-a-computed-window" — the signature audit's fourth category; x has NO FLOOR,
> so no detection confirms GRUT and no null refutes it: the family allows up to the edge and
> predicts nothing)** — (source: `provenance/claims.json` node `zeta_interior_family`;
> `SIGNATURE_AUDIT.md` audit table row 6 and "fourth category" note;
> `calc/RESULTS_isw_exclusion.md`, binding-inversion row).

The honesty point the audit insists on: the window does **not** soften the signature-null
verdict. Structure formation in GRUT is ΛCDM structure formation at the chosen point, with a
data-bounded, floorless allowance for departure that carries no predictive content.

---

## VI.3 · Dark energy: the sourced prediction, and the hypothesis that must not be
promoted

### VI.3.1 The sourced statement

Repeating VI.1.2 in dark-energy language, because this is the sector's backbone: the sourced
prediction of GRUT-as-written is **w = −1, flat, at all redshifts**. This is
signature-null — it is ΛCDM (source: `SIGNATURE_AUDIT.md`, audit table row 2:
"signature-null (sourced = ΛCDM)").

### VI.3.2 Evolving w(z): a hypothesis with a price tag

A finite-memory vacuum has a frequency-dependent χ(ω); out of equilibrium, its effective
w(z) can in principle leave −1. The record explored this as a differentiator and found the
structure, priced straight (`calc/wz_dark_energy.py`, `calc/RESULTS_wz.md`):

- w(z) deviates from −1 only if the vacuum has response power at ω ~ H(z). The confirmed
  UV-cutoff memory scale gives H₀τ_c ~ 10⁻⁴⁰: **w = −1 flat to ~80 decimals.** No evolution.
- Observable evolution therefore **requires a second, cosmologically slow scale τ₂ ~ 1/H₀**
  — exactly the "second internal bath scale" the single-pole spine forbids, coexisting with
  it only via a ~40-order scale separation (a two-scale vacuum, an explicitly named
  structural commitment).
- The de Sitter horizon forces the noise temperature and the *existence* of relaxation, but
  **not the timescale**: both examined horns *insert* τ₂ ~ 1/H (a free field needs a tuned
  m ~ H — the η-problem; a self-interacting mode relocates the insertion into a structural
  bundle). The candidate economical rescue — the rung-9 conformalon doing double duty as the
  IR mode — is **DEAD, frozen as a disposition**, on three grounds with prefactors carried:
  its pinned stress is w = +1/3 (radiation-like — the wrong equation of state for a
  dark-energy deviation), the w-deviation lands ~8× below DESI's amplitude at N = 60, and no
  Starobinsky–Yokoyama dynamical mass exists for the Δ₄ Paneitz compensator (source:
  `provenance/claims.json` node `rung7_wz`, `boundary_condition`; `calc/RESULTS_conformalon.md`,
  cited there).

> **STATUS: HYPOTHESIS (requires the inserted, un-sourced τ₂ ~ 1/H₀, priced +2)** —
> canonical claim 13, second half, verbatim; the register's ledger for `rung7_wz` is +3
> total, of which the τ₂ commitment constitutes +2 and the single-departure-shape closure the
> remaining +1 (source: `books/CORPUS_CHARTER.md`; `provenance/claims.json` node `rung7_wz`,
> `ledger_note`).

The laundering fence is the operational form of this status. The forward-model harness
carries the invariant **evolving ⇒ needs_unsourced_input**: across the responsive-medium
kernel family, the only clean data-consistent vacuum is w = −1 ΛCDM, and *every*
DESI-like evolving signal the machine can produce is flagged and refused on inserted-input
grounds — independent of the sign of the evolution (the harness's own DESI-sign
representative "matches DESI's sign within precision and is still refused"). Importing τ₂
silently, or re-billing an evolving w(z) as a GRUT prediction, is the specific act the fence
exists to catch (source: `SIGNATURE_AUDIT.md`, audit-critic verdict; `calc/RESULTS_wz_sign.md`,
harness-showcase note).

### VI.3.3 The wₐ-sign history: two retractions, told on their face

The record's most instructive cosmological episode is not a result but a double retraction.

1. **The first over-claim (away from DESI).** The 2026-06-25 toy computed wₐ > 0 for the
   simplest passive relaxor and the record briefly carried "wₐ > 0 — the WRONG sign for
   DESI." Retracted 2026-06-29 as un-earned: it was only one of two passivity-consistent
   branches, and the toy's slope was a ζ = const/Eckart modeling artifact.
2. **The mirror over-claim (toward DESI).** The overseer's own sharpening — "wₐ ≤ 0 is
   second-law-fixed" — was then run through an independent workflow *by its own author* and
   retracted the same day (the verify-the-verifier principle operating on the verifier).

What survived both retractions is a precise partition: **the second law fixes the SIDE, not
the SLOPE.** Passivity (ζ ≥ 0) puts the dissipative branch at w ≤ −1 and the reactive branch
at w ≥ −1, and the entropy production σ = Π²/(ζT) ≥ 0 forbids a within-branch crossing of −1
— that is the robust content. But σ is quadratic in Π and blind to dΠ/dt, so the wₐ slope
rides on sign[d(ζH)/da], which the dissipation inequality never touches: ζ = const gives
wₐ < 0, ζ ~ 1/H² gives wₐ > 0, both fully passive.

> **STATUS: UNRESOLVED (the wₐ sign is genuinely indeterminate; both directional claims —
> "wₐ > 0 wrong sign" and "wₐ ≤ 0 second-law-fixed" — RETRACTED 2026-06-29; two non-theorem
> arguments lean wₐ < 0, banked as notes, not tiered claims)** — with the additional
> side-tension recorded: the dissipative branch's w ≤ −1 floor sits on the *wrong side* of
> DESI's present-day w₀ > −1, so the natural-reading lean lost, on the side axis, even its
> direction (source: `provenance/claims.json` node `rung7_w2_wa_sign`;
> `calc/RESULTS_wz_sign.md`, "Overseer rulings" section; `calc/wz_sign.py`).

### VI.3.4 The no-crossing no-go: robust, and correctly held below its ceiling

The robustly supported derived-candidate in the w(z) story is the **no-crossing** statement:
a single passive channel's deviation (w+1) is one-signed and shrinks toward the de Sitter
attractor, so w approaches −1 from one side and never crosses the phantom divide. A crossing
requires the equilibrium itself off −1 (a real quintessence/phantom degree of freedom) or a
sign-changing kernel (≥2 modes / oscillatory poles) — exactly the inserted structure the
laundering fence prices.

The register nevertheless **holds this at `to-derive`**, by explicit overseer ruling, for two
reasons that this corpus must not smooth over: (1) the no-go is *generic* — it is Vikman 2005
(arXiv:astro-ph/0407107; a single non-ghost degree of freedom cannot dynamically cross
w = −1), and GRUT's specific content is only "the single-pole spine lands in that class";
(2) it is *conditional on rung3, which is open* — the one-signed-Π argument needs a single
real pole, and if the vacuum bath is collisionless free-streaming (a branch cut), the
argument fails and the no-crossing needs re-derivation. **A no-go cannot outrank its
anchor.**

> **STATUS: UNRESOLVED (held at `to-derive`, overseer-ruled 2026-06-29: generic-flavored —
> Vikman 2005 cited at any shipped strength — and conditional on the open rung3 anchor; the
> would-be export `rung7_w3` is contingent and default-BROKEN)** — (source:
> `provenance/claims.json` nodes `rung7_w2_wa_sign`, `rung7_w3_nocrossing_export`;
> `calc/RESULTS_wz_sign.md`).

And the anchor itself, for the reader tracking the dependency:

> **STATUS: UNRESOLVED (anchor-class, derived-pending; pole-vs-cut open; the Tier-4
> computation found a CUT, not a pole, at flat scope)** — canonical claim 4, verbatim; rung3
> is the named bottleneck for the entire w(z) story (source: `books/CORPUS_CHARTER.md`;
> `provenance/claims.json` node `rung3_single_pole`).

---

## VI.4 · The kernel-class discriminator — what the sector actually exports

The 2026-08-23 discriminator computation (`PHYSICS_LEDGER/rung7_discriminator.py`,
`PHYSICS_LEDGER/RUNG7_TWO_POLE_COMPARISON.md`) answered the question "what property of the
kernel actually controls the crossing?" with a frozen pre-scan criterion and planted
controls, and the answer sharpened the whole export:

- Single-pole Debye: no crossing. Two real poles: no crossing. Three real poles: no
  crossing. One-channel non-Debye Cole–Cole (a branch-cut kernel): no crossing.
- A damped **oscillatory pole pair**: TRUE CROSSING.

**The operative variable is the existence of a second dynamical mode with independent phase
(oscillation) — not pole count, and not single-pole structure.** Every purely relaxational
kernel stays on one side of w = −1; single-pole is *decorative* for this observable (the
registered derivation never invokes χ's spectral form).

> **STATUS: DERIVED (class-level; explicitly not GRUT-specific)** — canonical claim 15,
> verbatim: no purely relaxational kernel crosses w = −1; only an oscillatory pole pair does.
> Menu-scope exclusion shared by the entire passive class (source:
> `books/CORPUS_CHARTER.md`; `PHYSICS_LEDGER/RUNG7_TWO_POLE_COMPARISON.md`,
> `PHYSICS_LEDGER/rung7_discriminator.py`; consistency-reproduction of Vikman 2005, not a
> discovery).

The consequence cuts both ways, and the freeze document elevates the adverse direction to a
standing reopening condition: **any observed w = −1 crossing excludes the entire passive
relaxational family at once — GRUT included — at a stroke.** This is the sector's real
falsifiable content: a direction, shared with a whole class, not a signature owned by GRUT
(source: `GRUT_PROGRAM_FREEZE.md` §5, reopening condition 4; `SIGNATURE_AUDIT.md`).

---

## VI.5 · The DESI anti-signature — the live threat

The 2026-08-02 external hunt (pre-registered A/B/C bar, adversarially refereed, load-bearing
numbers overseer-verified against primary literature) produced two cosmology-relevant items,
recorded in `SIGNATURE_AUDIT.md` and restated here at their audited strength.

**Item 1 — the scoped null.** No candidate differentiator above Grade C exists *in the
explored structure* (the admitted TT-channel / passive-KMS / ΛCDM-at-linear family, across
the four searched domains). This confirms the audit's EMPTY verdict from outside — and it is
explicitly *not* the universal claim "GRUT is empirically silent," which no search can
establish (source: `SIGNATURE_AUDIT.md`, 2026-08-02 item 1).

**Item 2 — the DESI anti-signature, with four attribution fences.** GRUT's sourced
prediction is w = −1 flat; the passivity no-go forbids a single passive relaxor from crossing
w = −1. DESI's preferred w₀wₐ trajectory **crosses the phantom divide at z ≈ 0.35–0.5** —
exactly the forbidden shape. The fences, verbatim from the audit (overseer-verified):

> **(a)** the preference is DESI **BAO + CMB + SNe** — DESI BAO alone shows no significant
> preference, and with a fixed r_d anchor the ~3σ does not reproduce; **(b)** the honest
> headline is **3.1σ (DESI DR2+CMB, arXiv:2503.14738)** — the 4.2σ endpoint rides the
> contested DESY5 compilation (live Efstathiou-vs-DES systematics dispute; one reanalysis
> drops it to 0.5–1.5σ); **(c)** Bayesian model comparison on the same data gives only
> weak-to-moderate evidence; **(d)** the direction is Quintom-B — *phantom in the past,
> quintessence today* (secondary summaries routinely state it backwards).

> **STATUS: pending refutation if the signal consolidates** — the audit's verbatim standing
> disposition, with its comparative clause carried: "GRUT is structurally worse-placed to
> survive it than ΛCDM+quintessence" (source: `SIGNATURE_AUDIT.md`, 2026-08-02 item 2).

The logical geometry deserves one plain paragraph. The framework's cleanest class-level
derived result (VI.4) and its most probable near-term empirical test point at the same
observable from opposite sides. If the DESI-preferred crossing consolidates, the whole
passive relaxational family — GRUT's admitted structure among it — is excluded without any
GRUT-specific measurement ever being needed. If it dissolves, ΛCDM stands and GRUT's sourced
cosmology remains indistinguishable from it. There is no branch in which the sector delivers
a confirming signature; the audit's phrase for this shape is *anti-signature*.

---

## VI.6 · Derived structural results in the cosmological sector

Three results in this sector carry the word DERIVED at frozen scope, and one canonical
reversal frames them. None yields a number an experiment can chase — that, too, is on the
record (the admissible set is an amplitude-homogeneous cone; "every route from this
framework to a number runs outside it," `GRUT_PROGRAM_FREEZE.md` §3) — but they are the
sector's genuine mathematical content.

### VI.6.1 The spectral law s = 5

The flat-scope one-loop TT kernel of the gravitational vacuum, at contract scope
(ω ≫ H), is

    Σ_R(ω>0) = −(3/1280π²) ω⁴ [log(μ²/ω²) + iπ] + H²(−(13/480π²)) ω² [log(μ²/ω²) + iπ] + local slot,

giving Im χ ~ ω⁴ as an exact power law on the flat slice — **s = 5 in the registered
J-convention** (J ~ ω⁵), convergent, with Re χ(0) = 3/(2560π²) exactly. The physics headline
is deflationary in the program's characteristic way: the framework's **own registered s = 3
is rejected** by the frozen tolerance — the two-derivative TT-TT-TT vertex contributes ω⁴ in
|V|² on the gapless cut, which the original rung3 density-of-states argument never counted.
The registered ω³ power re-enters only as the curvature-induced O(H²) component, with an
H²-proportional coefficient the registered family excludes ("H_dependence: NONE declared").
Same side of the decision axis (convergent), structurally different analytic form at leading
flat order.

> **STATUS: DERIVED (flat scope; rejects the framework's own registered s = 3)** — canonical
> claim 6, verbatim; importing s = 3 anywhere downstream is laundering, per the dispatch spec
> (source: `books/CORPUS_CHARTER.md`; `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`,
> `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md`; `AGENT_COORDINATION.md`, 2026-09-01
> entries).

### VI.6.2 The exact de Sitter constant tail

On exact dS₄, the massless minimally coupled field — hence each free TT graviton
polarization — has an exact constant zero mode (Δ₋ = 0), and the retarded response carries an
**exactly constant tail H²/4π filling the interior of the light cone**, verified by a
two-sided causality gate sited away from any degenerate point; conformal coupling gaps it at
m_eff² = 2H². This "Δ₋ = 0 zero-mode complex" is the structure that survived every deletion
test in the resurrection campaign — the record's one surviving fixed point.

> **STATUS: DERIVED (exact dS; gapped only at conformal coupling)** — canonical claim 7,
> verbatim (source: `books/CORPUS_CHARTER.md`; `RAI_GORILLA_T1.md` §XVI-G;
> `GRUT_PROGRAM_FREEZE.md` §3).

### VI.6.3 What the constant tail did to the finite-memory bet

The two derived results above are not neutral decorations; the second one *reversed the
sector's founding intuition*. The finite-memory / single-pole kernel was the program's
central asserted object, and the constant tail is its negation in the regime cosmology
lives in: what exact dS free-field theory forces is **infinite, scale-free memory** — the
opposite shape of the asserted kernel. The one in-house quantitative support for finite
memory fell to a bug validated only at its blind point; the prior ("something surely forces
finite memory") was removed by enumeration of all seven candidate memory mechanisms.

> **STATUS: ASSUMPTION, with REVERSED history on its face (the in-house "no memory time"
> computation was reversed; exact dS free-field theory forces infinite scale-free memory)**
> — canonical claim 18, verbatim; retained as postulate only (source:
> `books/CORPUS_CHARTER.md`; `RAI_GORILLA_T1.md` §XVI-H; `GRUT_MODEL_FRAMEWORK.md` §7).

### VI.6.4 The Γ_T closure — the one cosmological number, computed to refuse

The only parameter-free number this sector ever produced is the closure of the
gravitational-wave friction route. The Tier-4 derived kernel's induced cosmological tensor
friction is Γ_T(ω) = (3/1280π)(ω³/M̄_P²)[1 + (104/9)(H₀/ω)²] — chromatic, μ-independent —
evaluating to **Γ_T/H₀ = 6.19×10⁻⁶³ at 100 Hz: 62.7 orders below the shared-slot bound**
few×H₀. The pre-registered question ("does the local memory scale connect to the
cosmological friction parameter-free?") is answered: no parameter-free connection exists on
the licensed record, and the SPEC's own gate returns REFUSE on the observable route.

> **STATUS: CLOSED (computed NO EFFECT; SPEC outcome REFUSE on the observable route; commits
> 2116251, 41e1af5)** — canonical claim 16, verbatim (source: `books/CORPUS_CHARTER.md`;
> `calc/RESULTS_gw_tensor_friction.md`, `calc/gw_tensor_friction.py`,
> `GRUT_PREDICTION_GATE_GAMMA_T.md`).

---

## VI.7 · The ΛCDM comparison, stated whole

Assembling the sector: at background order the sourced statement is w = −1 flat (VI.1.2); at
linear order μ = Σ = η = 1 at the chosen point (VI.2.1); the one naive departure the
framework's own coefficient suggests is self-excluded (VI.2.2); the admissible interior
departure is data-bounded with no floor (VI.2.3); every evolving-dark-energy shape is priced
as an inserted input (VI.3.2); and the class-level no-crossing direction is shared with all
passive media (VI.4). The comparison with ΛCDM is therefore not "GRUT reproduces ΛCDM" in
the correspondence-limit sense that phrase usually carries. It is: *GRUT-as-written, at its
chosen point, is observationally ΛCDM*, and the choices that put it there are registered
assumptions. Per the freeze's mandatory honesty note, recovery of standard results by
standard machinery on declared inputs is **compatibility, not correspondence evidence**, and
nothing in this sector counts toward PREDICTED.

What the sector genuinely contributes, at its earned strengths:

| product | kind | status label carried |
|---|---|---|
| w = −1 flat | sourced statement | DERIVED (within the choices x = 0 / pure-TT) |
| μ = 4/3 endpoint exclusion | self-exclusion (no-go export) | CLOSED |
| no purely relaxational kernel crosses w = −1 | class-level theorem-grade result | DERIVED (class-level; not GRUT-specific) |
| s = 5 spectral law; dS constant tail H²/4π | structural results about the vacuum kernel | DERIVED (at their frozen scopes) |
| evolving w(z) | hypothesis, priced | HYPOTHESIS (+2, τ₂ un-sourced) |
| DESI crossing | external anti-signature | pending refutation if the signal consolidates |
| Γ_T at ω ~ 100 Hz | closure | CLOSED (computed NO EFFECT) |

---

## VI.8 · Absence map — where the record is silent

The corpus charter treats an absence map as valid content. The following standard-cosmology
topics have **no GRUT account in the frozen record**. Listing them here is a statement about
the record, not a promise; under the stopping rule, none may be filled by invention.

> **STATUS: UNMAPPED** — for every item below (the label is canonical claim 22's for its
> listed sectors; extended here descriptively to sector-adjacent silences, each verified
> silent against the register and the ledgers).

- **Dark matter and baryogenesis** — canonical claim 22, verbatim: "Flavor, strong-CP,
  neutrino masses, dark matter, baryogenesis — **UNMAPPED**." The register's 74 nodes contain
  no GRUT account of the dark-matter sector or the baryon asymmetry.
- **Inflation and the early universe.** No GRUT inflationary mechanism, spectrum, or
  initial-condition account exists in the record. (E-fold counts appear only inside the
  conformalon closure arithmetic, VI.3.2; the Past Hypothesis input is a time-orientation
  datum, not an early-universe model.)
- **BBN, recombination, reionization, CMB physics beyond the low-ℓ ISW/TT channels used in
  the μ = 4/3 exclusion.** Nothing in the record.
- **Nonlinear structure formation** (halo formation, N-body regime, baryonic feedback).
  The record's structure-formation content is entirely linear-order bookkeeping.
- **The observational tensions** (H₀, S8). No GRUT position exists; no node addresses them.
- **The ω ≲ H regime** — not merely unmapped but **UNASKABLE at current declarations, on
  four obstructions** (not false — unposable); this is where the noise-sector fork and the
  white-floor regime live, outside the contract truncation (source:
  `GRUT_PROGRAM_FREEZE.md` §3 UNRESOLVED row; `AGENT_COORDINATION.md` 2026-09-01).
- **Black-hole ringdown/QNM** — the signature audit's one flagged soft spot:
  expected invisible by inheritance of the rung4 Planck suppression, but this is an
  inheritance argument, **not a dedicated computation**; the calc does not exist (source:
  `SIGNATURE_AUDIT.md`, "the one soft spot").

---

## Sources drawn from

- `books/CORPUS_CHARTER.md` (canonical status table; formatting)
- `GRUT_MODEL_FRAMEWORK.md` (authoritative presentation; §5 cosmology, §7 failures)
- `GRUT_PROGRAM_FREEZE.md` (ledger; stopping rule; reopening conditions)
- `provenance/claims.json` — nodes `rung7_wz`, `rung7_w1_wz_map`, `rung7_w2_wa_sign`,
  `rung7_w3_nocrossing_export`, `mu_linear`, `rung3_single_pole`, `zeta_interior_family`,
  `lambda_undetermined`, `vc_w_equals_minus_one`, `p_tt_ansatz` (via node texts)
- `SIGNATURE_AUDIT.md` (items 1–2 of the 2026-08-02 hunt; audit table; fourth category;
  QNM soft spot)
- `NO_GO_LEDGER.md` (entries 2 and 3; strength legend)
- `calc/wz_dark_energy.py` + `calc/RESULTS_wz.md`
- `calc/wz_sign.py` + `calc/RESULTS_wz_sign.md`
- `calc/mu_linear.py` (bookkeeping, via register node)
- `calc/isw_exclusion.py` + `calc/RESULTS_isw_exclusion.md`
- `calc/RESULTS_gw_tensor_friction.md` (+ `calc/gw_tensor_friction.py`,
  `GRUT_PREDICTION_GATE_GAMMA_T.md`)
- `PHYSICS_LEDGER/RUNG7_TWO_POLE_COMPARISON.md` (+ `PHYSICS_LEDGER/rung7_discriminator.py`)
- `PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md`,
  `PHYSICS_LEDGER/WALL_KR_CONTRACT_RETARDED_VERDICT.md` (via `AGENT_COORDINATION.md`
  2026-09-01 consolidated entries)
- `RAI_GORILLA_T1.md` (§XVI-G, §XVI-H: the constant tail; the memory reversal)
- External literature, as already cited by the record: Vikman 2005
  (arXiv:astro-ph/0407107); Gubitosi–Piazza–Vernizzi (arXiv:1210.0201); DESI DR2+CMB
  (arXiv:2503.14738); DESI MG (arXiv:2411.12026); Li–Barrow (arXiv:0902.3163);
  Salcedo–Colas–Dufner–Pajer (arXiv:2507.03103); Calzetta–Hu (book); Kubo 1966.

## Gaps in this book

1. **The register's authority-vocabulary annotation applies throughout.** Words like
   "overseer," "specialist," "referee," and "external" in the sources quoted here denote
   in-house passes — separate AI sessions run by the program's one human author; no outside
   human has been contacted (sealed audit `PREREG_AUTHORITY_TERMS_2026-08-12.txt`, quoted in
   `rung7_wz` and `rung3_single_pole`). This book inherits that vocabulary when quoting; the
   reader must not read it as independent review.
2. **The owed calculations are owed, not done**: the low-ℓ TT-auto exclusion calc (the gate
   for interior viability above x ~ 0.06); the separate-universe residue (adiabaticity + the
   dilatation bridge); the de Sitter trace-sector effective stress tensor that would decide
   the wₐ slope; the rung3 transport self-energy that anchors the no-crossing; the dedicated
   QNM/ringdown calc.
3. **This book does not re-derive the s = 5 kernel or the dS tail**; it restates the frozen
   verdicts and their scopes from the Wall-A/K_R ledger artifacts. The full contract chain
   (declarations D1–D5, the scheme fork, the T4 adjudication queue) belongs to Books II/IV.
4. **The DESI empirical situation is quoted as of the record's 2026-08-02 verification**;
   nothing newer is imported, per the charter's no-new-external-claims rule.
5. **No account of the {shear, bulk} interior's dynamics** (μ(c₀), slip, stability) exists
   in the record beyond the window arithmetic; the register holds it at `to-derive`,
   default-BROKEN, and this book adds nothing to it.
6. **Background cosmology beyond the dS-like patch** (matter era dynamics, radiation era,
   transitions) has no GRUT-specific account; the record's w(z) toys run on an input
   ΛCDM background H(a), and this book flags rather than fills that dependence.
