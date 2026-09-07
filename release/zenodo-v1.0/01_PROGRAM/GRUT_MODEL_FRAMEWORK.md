# GRUT — A CONSTITUTIVE-RELATIONAL FRAMEWORK FOR PHYSICAL THEORY

**The authoritative model presentation** · 2026-09-06 · assembled from the committed record
(base 7399765) · governed by `GRUT_PROGRAM_FREEZE.md` (the derivational ladder is frozen;
**the framework itself is live**) and by the eight-status vocabulary defined there.

> Originally developed toward a unified theory, GRUT is presented here at the standard it can
> honestly support: **a constitutive-relational framework** in which physical systems are
> understood through response, relation, and memory. The framework does not claim its
> primitives are derived from an assumption-free substrate. It explicitly distinguishes
> postulates, empirically motivated inputs, structural selections, derivations, recovered
> limits, predictions, unresolved questions, and speculative interpretations. Its scientific
> value is therefore determined by the coherence, consistency, explanatory reach,
> adaptability, and experimentally distinguishable consequences of the resulting framework.

---

## 1 · WHAT GRUT PROPOSES

Physics is ordinarily organized around entities obeying externally specified laws. GRUT
proposes a different primitive language: **physical systems relate through constitutive
response** — what a system does next depends on what has acted on it, through a retarded
kernel carrying its interaction history — and the gravitational vacuum itself is treated as
such a responsive medium rather than as inert stage. Dissipation, noise, decoherence,
relaxation, and gravitational response then become **sector instances of one architecture**
instead of separate formalisms.

None of this is claimed to be derived from nothing. It is a proposed way of writing physics,
to be judged by what the writing earns.

## 2 · EXPLICIT PRIMITIVES — nothing hides in the mathematics

| element | status | why selected | alternatives considered / fate |
|---|---|---|---|
| responsiveness (constitutive relation as primitive) | **AXIOM** | the central ontological bet; a framework must bet something | entity-first ontology = the standard alternative; GRUT's claim is that the response language organizes better |
| relational description (system defined against what it responds to) | **AXIOM** | inseparable from the above | the audits showed the *specific* decomposition is a further choice (below) |
| a system/bath-type decomposition | **AXIOM (form) + STRUCTURAL-SELECTION (instance)** | required to write any influence functional | canonical tensor split is *impossible* in the relevant algebra type (III₁); what survives translation is a one-sided inclusion; the contract's operative partition (external-leg vs internal-line) was historically **undeclared** — now declared here |
| memory / finite relaxation | **AXIOM, downgraded from earlier billing** | the historically central bet | its one in-house support was **reversed** (§7); retained as postulate only, with its strongest form (single pole) carrying no surviving discriminating consequence |
| retardation / causality of K_R | **EMPIRICAL-INPUT + STRUCTURAL** | observed time-asymmetry; upper-half-plane analyticity | the audits located its origin in a past-boundary condition (Past Hypothesis), an input in every formulation examined |
| Past Hypothesis (direction of relaxation) | **AXIOM** | no examined route derives temporal orientation; every closure consumed it | five dressings audited; all one input (the half-line/KMS alignment) |
| Born measure | **AXIOM** | decoherence selects a basis, not a probability | inherited, irreducible in-house; flagged as the never-sorted door |
| bath content (massless relativistic modes) | **STRUCTURAL-SELECTION** | simplest relativistic choice | classified "standard input" by the distinctiveness ledger; proviso ("no second internal scale") undischarged |
| TT projector (pure spin-2 response, x = 0) | **STRUCTURAL-SELECTION** | interrogated 2026-08-02: **CHOSEN, unanimous** — diffeo invariance stops one condition short of forcing it | the {shear, bulk} interior remains the unexplored empirically viable sector |
| c₀ = α DC normalization | **STRUCTURAL-SELECTION** | adopted phenomenological anchor | the conformal anomaly does **not** derive it (rung9b) |
| state (BD-analogue), scheme, order of limits, gauge | **STRUCTURAL-SELECTIONS** | the D1–D5 declaration sheet | each priced; the crossed-product result shows state-selection dissolves at that level (Connes cocycle) |
| measured constants (H₀, M_P, T_dS given background, …) | **EMPIRICAL-INPUTS** | nature's numbers | T = H/2π is *forced given the background* — the register's only credit |

## 3 · THE CONSTITUTIVE MATHEMATICS

The framework's heart is a single Schwinger–Keldysh influence action for the metric
perturbation h (doubled fields, Keldysh basis h_r, h_a):

    S_IF[h_r, h_a] = ∫ (dω/2π) d³k [ h_a · K_R(ω,k²) · h_r + (i/2) h_a · N(ω,k²) · h_a ]

with both kernels decomposed on the Ward-surviving projector pair,

    K_R = c₂(ω,k²) P⁽²⁾ + c₀(ω,k²) P⁽⁰ˢ⁾   (retarded / dissipation)
    N   = n₂(ω,k²) P⁽²⁾ + n₀(ω,k²) P⁽⁰ˢ⁾   (noise)

subject to: upper-half-plane analyticity (causality); the **KMS/FDT lock** in equilibrium —
N tied to Im χ by the coth(ħω/2kT) factor, enforced as a hard admission gate; **passivity**
per channel, no cross-channel rescue; positivity of N. Two theorem-grade structural facts
about this family, both cutting against over-claiming: **the action carries a family, not a
point** — x (the scalar-to-tensor ratio) is not fixed by the action (x_no_pin: the
admissible set is an amplitude-homogeneous cone, orienting channels and pinning nothing) —
and the **form itself is universal** (Feynman–Vernon; u1): any local causal open system
yields it, so the form confers no GRUT-specific content. GRUT's content lives entirely in
the *choices* of §2 and whatever consequences they earn.

## 4 · WHAT FOLLOWS MATHEMATICALLY (the earned arrows)

**DERIVED** (from the declared inputs, exhibited and checked): the flat-scope one-loop TT
kernel K_R = −(3/1280π²)ω⁴L + H²(−13/480π²)ω²L + local slot, L = log(μ²/ω²) + iπ, with
**H¹ = 0 identically** — the four-channel cancellation theorem and its even-degree ladder
class (Theorem II, a genuinely new structural identity from two standard identities); the
spectral law **s = 5** at flat contract scope, *rejecting the framework's own registered
s = 3*; the exact dS constant retarded tail H²/4π, gapped only at conformal coupling; the
passivity/cone theorems; and — from the RRT arm — the **linear-universe response no-go**
(intervention response reducible for *all* linear dynamics; escaped only by nonlinearity).

**RECOVERED** (with the honesty note): GR at zero-memory collapse; standard open-system
structure throughout — noting that recovery here is largely *by identity* (the executed
machinery is standard machinery on the declared inputs; KERNEL-STANDARD, scoped), which
establishes compatibility, not correspondence evidence.

**PREDICTED**: **empty** — see §7.

## 5 · SECTOR-BY-SECTOR PHYSICS (from the register, statuses attached)

**Quantum mechanics** (rung6, ASSUMED +2). Integrating out the bath yields the reduced
master equation; the unitary core is Schrödinger; the noise kernel supplies decoherence
selecting a pointer **basis**. What GRUT does *not* produce: the outcome **probability** —
the Born measure is an inherited axiom (the improper-mixture objection), stated openly.

**Decoherence / USL** (rung8, TO-DERIVE +2). GRUT's N driving the Anastopoulos–Hu (2013)
gravitational-decoherence master equation yields a signature distinguished from
Diósi–Penrose/CSL **in shape only**; the banked magnitude verdict is **quiet-or-faint**.
Status discipline: this is a *proposed phenomenological relation*, not a derived prediction,
and not an experimentally validated effect. (Context: the parameter-free DP model is already
experimentally excluded at Gran Sasso — the standard the shape-claim must eventually meet.)

**Gravity** (Tier-4 contract, SHOWN at declared scope). The response formulation reproduces
the standard one-loop retarded TT self-energy on the declared inputs; validity ω ≫ H;
branch point at ω = 0 (gapless two-graviton continuum) — a **cut, not the asserted pole**.
The registered object's identity (kernel vs dressed propagator) remains an **owner fork**:
the dressed reading lands on the opposite side of the pre-registered convergence boundary.

**Cosmology** (rung7 TO-DERIVE +3; mu_linear NO-GO EXPORT) — *treated ruthlessly, per the
model's own history.* Linear cosmology reproduces ΛCDM **at the chosen point x = 0**; the
trace-only endpoint μ = 4/3 that GRUT's conformal coefficient would naively suggest is
**excluded** (separate-universe consistency + low-ℓ ISW) — a genuine self-exclusion the
framework earned. An evolving dark-energy w(z) is reachable **only via an inserted,
un-sourced second scale** (τ₂ ~ 1/H₀ — "laundering" if imported silently); and the
finite-memory/de Sitter story suffered a **structural reversal**: the in-house computation
supporting "no memory time" was reversed by a corrected analysis, and what exact dS
free-field theory forces is **infinite scale-free memory** — the opposite shape of the
original bet. Both facts are part of the model's history, not footnotes.

**Kernel-class discriminator** (committed, contamination-clean): every purely relaxational
kernel — Debye, multi-pole, Cole–Cole — stays on one side of w = −1; **only an oscillatory
pole pair crosses**. This is menu-scope exclusion shared by the entire passive class —
explicitly *not* GRUT-specific — but it means any observed crossing falsifies the whole
family at once, GRUT included.

## 6 · WHAT GRUT EXPLAINS DIFFERENTLY

Not "GRUT proves everything," but: **a single organizing language for phenomena normally
carried in separate formalisms.** One influence-functional architecture, one KMS/FDT lock,
one passivity structure, one kernel bookkeeping spans: decoherence (rung6/8), dissipation
and noise (rung1/2), gravitational response (Tier 4), cosmological response (rung7/mu_linear),
and gravitational-wave friction (the Γ_T slot). The register itself — 74 nodes under one
dependency discipline — is the demonstration that the sectors *can* be written in one
vocabulary with every assumption priced. And the language made one framework-level fact
visible that the standard organization obscures, stated with its grades:
**persistence came free; forgetting and direction were always paid for** — on a de Sitter
background the derivation is controlled; universally it is an induction the record's
one-sided apparatus is least able to check. Whether this reorganization is *merely* a
reformulation or eventually earns more is exactly what §8 decides.

## 7 · WHERE GRUT CURRENTLY FAILS OR STOPS — prominent, not buried

- **It does not derive its own primitives.** Established across ROOT-1, the structural
  search, the resurrection, and the Final Boss: every discharge attempt ended in relocation;
  the surviving unexplained input is one relative datum (the half-line/KMS alignment).
- **No novel experimentally confirmed prediction exists.** PREDICTED is empty for a
  *derived* reason: the framework asserts a class, a class has no scale, and the admissible
  cone pins no ratio — every route to a number runs outside the framework.
- **The strongest historical claim was reversed.** The finite-memory kernel's sole in-house
  quantitative support fell to a bug validated only at its blind point; corrected, the
  computed object tends to a constant or grows; single-pole has no surviving observable
  consequence distinguishing it from the passive class ("decorative for w = −1 crossing").
- **Several apparent structural results were supplied structure**, identified as such:
  the u4 "dissolution" (relocation), G-STRONG, the sector-selection and CPR routes
  (unresolved / reference absent), the P1 emergence framing (closed for all linear dynamics).
- **The audit apparatus itself was caught three times** (asymmetric error budget;
  story-pinned gates; the frame-entailed null) — the record's negatives carry the
  corresponding caps.

## 8 · WHAT WOULD CHANGE OUR MIND

**GRUT is strengthened by:** the interacting graviton zero-mode computation returning
*protected* (the persistence fixed point survives interaction); a derivation of any §2
selection from an independently motivated principle; a sector consequence that is
quantitative, nontrivial, and not encoded in the inputs (§NEXT_STEPS, the prediction hunt);
the SLOT test resolving the clock-slot as *not* a second irreducible input.

**GRUT is weakened or falsified by:** an observed w = −1 crossing (kills the relaxational
class outright); the zero-mode computation returning *lifted* (the one surviving derived
structure falls); a self-closing description of the observed time-asymmetry with zero
undischarged inputs (breaks the consolidated record); the USL shape-signature excluded in
the regime where it is distinguishable; or the RESIDUE test deriving the alignment from
unoriented hypotheses (the framework's deepest axiom becomes someone else's theorem).

Nature and mathematics hold every one of these votes. The framework holds none of them.

---
*Register untouched (74 nodes, sha256 `beaeb84e8a6f8468…`). This document consolidates and
presents; statuses herein restate the committed record in the eight-status vocabulary and
bank nothing new.*
