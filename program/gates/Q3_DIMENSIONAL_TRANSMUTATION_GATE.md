# Q3 — DIMENSIONAL-TRANSMUTATION DESIGN + CONSTRUCTIVE DERIVATION GATE

> **2026-09-07 · Reality-Program investigation. No expensive computation performed.** The
> frozen corpus is treated as the **baseline** for what was historically established, **not
> as a boundary on what may be derived now**. Nothing is retroactively inserted into the
> books: any result here is *a new Reality-Program derivation from declared GRUT structure*.
> Q1, Q2, Q2-SY, Q2-BRIDGE, the register and the corpus are untouched. Phase 1 reconstruction:
> workflow `wf_6a4ec424-651` (five axes). Phase 3 algebra: symbolic only, executed inline,
> no numbers inserted, no parameter chosen.

## 1 · The question

> Can the GRUT constitutive framework support a genuine dimensional-transmutation mechanism
> in which an internal physical scale emerges dynamically from a dimensionless running
> quantity, **without introducing that scale as a new primitive or a fit**?

Not: *did historical GRUT already contain one*. The three-way classification governs —
**A** historical content · **B** new derivation from declared structure · **C** new primitive
(stop and justify separately). **Only B is the constructive outcome.**

## 2 · VERDICT: outcome class **2** — *a viable dimensionless candidate exists in declared
structure, but it does not run*

**This gate's own constructive attempt was made and it FAILED, for a precise and instructive
reason.** A first draft claimed the candidate ran and generated a transmutation-shaped scale;
the hostile refuter destroyed both claims and I verified the destruction independently. The
failure is reported in §5 as the gate's main content, because *why* it fails is the finding:
**renormalization-point independence is exactly the statement that nothing here runs.**

## 3 · Phase 1 — what the record actually supplies

| ingredient | status |
|---|---|
| gravitational coupling κ | **dimensionful** — the classic obstruction to transmutation |
| anomaly coefficients a, c | dimensionless, but the register asserts the **anti-running** property: *"cohomological, one-loop-exact … independent of state/metric/dynamics"* — a **protected constant**, and rung9b's sector split leaves α *"the coefficient of NEITHER"* channel |
| the RG log L = log(μ²/ω²) | **genuine**, with a **frozen** coefficient A = −3/(1280π²) (= the 1/ε residue) |
| Λ_R = μ·exp(c₄/2A) | a real **RG invariant**, machine-gated with a detecting control — **and** *"algebraically the inserted μ. A reparameterization is not emergence"* (ROOT-1 §7, whose title is **"EMERGENT PARAMETER OR FUNCTION — NONE"**) |
| any beta function | **ZERO occurrences repo-wide** (confirmed). The only μ-statement is an *additive, ω-independent* shift c₄ → c₄ + A·log(μ²/μ′²), i.e. dc₄/dlog μ = const — **linear**, where QCD's mechanism needs **nonlinear** β(g) = −b₀g³ |
| μ itself | **mu-RULING-C**: no numerical convention exists; *"a numerical μ WOULD BE A NEW INPUT"* |
| the Ward-surviving two-channel family K_R = c₂P⁽²⁾ + c₀P⁽⁰ˢ⁾ | **declared structure** (`eft_operator_basis`) |
| **the dimensionless channel ratio r := c₀/c₂** | declared; `x_no_pin`: the admissible cone is amplitude-homogeneous and *"realizes every nonnegative c₀/c₂"* — **the action pins no ratio** |

**Named-artifact check, reported plainly:** `C_Final`, `C_Cosmo` and the value `1.154283` do
**not exist anywhere in this repository** (zero files, all types, including the release tree).
Neither does any beta function. If those objects exist, they belong to a lineage outside this
record, and nothing here reconstructs them.

**Trap recorded:** the Tier-4 kernel's local slot `c0 + c2ω² + c4ω⁴` and S_IF's projector
coefficients `c₂P⁽²⁾ + c₀P⁽⁰ˢ⁾` **share letters and are different objects.** Every statement
below about the channel ratio concerns the **projector** ratio.

## 4 · Phase 2 — the candidate that survives screening

Both candidates the record itself nominates die early: **μ/Λ_R** at arrows 1–2 (a dimensionless
*slot*, not a coupling; no β) and **α = a/c** at arrow 2 and worse (its β is not missing but
**structurally zero**, the exact inverse of the QCD mechanism).

**The surviving candidate is r = c₀/c₂**, and it is *not* rejected for absence from the
historical record — it is **declared structure**, and its profile is exactly the one a
transmutation candidate must have: **dimensionless by construction**, **not fixed by the
action** (x_no_pin), and **sitting in a kernel that carries a genuine RG log**.

## 5 · Phase 3 — the constructive attempt, and why it fails

**The construction.** Each Ward-surviving channel carries the same RG log with its own frozen
coefficient A_i (its 1/ε residue) plus its own local slot ℓ_i — declared structure, nothing
added. Write r := c₀/c₂ (**renamed from "x" — see the naming trap in §3**):

    c₂(L) = A₂L + ℓ₂ ,  c₀(L) = A₀L + ℓ₀ ,  r = c₀/c₂ ,  L = log(μ²/ω²)

**FAILURE 1 — the candidate does not run. β_r ≡ 0 identically.**
The first draft computed ∂r/∂L **at fixed ℓ_i** and obtained a nonzero result. That is not
the RG transformation. The record's frozen μ-shift law
(`WALL_KR_MU_OWNER_DECISION_PACKAGE.md` §3, machine-gated with a detecting control) is
*"changing the renormalization point μ → μ′ requires c₄ → c₄ + A·log(μ²/μ′²)"* — i.e. per
channel ℓ_i → ℓ_i + A_i·log(μ²/μ′²). Under that law each coefficient is **exactly**
μ-invariant (verified symbolically: c_i(μ′) − c_i(μ) = 0 identically for both channels), so

    dr/dlog μ = 0 , exactly.

**The apparent "running" was the wrong derivative** — with the kernel's exact degree-4 joint
homogeneity in (ω, μ), ∂/∂L at fixed slots is minus the ω-derivative: **kinematics relabelled
as RG flow.** It is also scheme-annihilable: in momentum subtraction (ℓ_i = 0) r ≡ A₀/A₂
identically, with no flow at all.

**FAILURE 2 — the "generated scale" was an identity.** The first draft inverted r(L) for L,
obtained L = (rℓ₂ − ℓ₀)/(A₀ − rA₂), and exponentiated it into a scale. But that bracket **is
L by construction**, so μ*² = ω²·exp(L) = ω²·(μ²/ω²) = **μ²** exactly, giving μ* ≡ μ and
dμ*/dμ = 1 (verified symbolically). **It is not an RG invariant at all** — strictly *weaker*
than the record's existing Λ_R, which at least satisfies dΛ_R/dμ = 0 under a detecting gate.
The draft described this as "RELOCATE, one level up from Λ_R"; it was a circular
re-derivation of the definition.

**FAILURE 3 — r is not a coupling.** The register types c₀, c₂ as **form factors** of
external kinematics — *"K_R = c₂(ω,k²)P⁽²⁾ + c₀(ω,k²)P⁽⁰ˢ⁾"*, with the constraint being *"on
a FUNCTION, never a bare inequality on a number."* They are not coefficients in an action
appearing in a Callan–Symanzik equation, so "beta function" was an equivocation.

**What survives.** r is genuinely dimensionless, genuinely declared, and genuinely unpinned by
the action — and the fixed ratio A₀/A₂ would still be a pure number. But **unpinned ≠
running**, which was exactly the objection flagged before the algebra was run, and it is the
objection that landed.

## 6 · Phase 5 — the strongest objections, applied to my own construction

- **"Unpinned masquerading as running." — THIS OBJECTION LANDED AND KILLED THE CONSTRUCTION.**
  It was flagged in advance as the place I was most likely to fool myself, and it is exactly
  where the failure occurred (§5, Failure 1). Recorded as a standing lesson: *a quantity the
  action does not fix may be genuinely free (an input) rather than determined by flow, and
  distinguishing these requires applying the actual RG transformation, not a partial
  derivative at fixed subtraction constants.*
- **"A μ-slot masquerading as a physical scale."** Conceded and recorded: μ* is exactly that.
- **"Scheme dependence." — LANDED, and further than the draft allowed.** Beyond the slots
  being scheme-dependent: the refuter established that the ratio A₀/A₂ is *not* cleanly
  scheme-independent either, because **P⁽⁰ˢ⁾ is invariant only under the spatial subgroup at
  fixed slicing**, its 4d-covariant completion (the conformal/Riegert–Paneitz sector) is
  **frontier-reserved**, and A₂'s gauge-robustness rides on P⁽²⁾'s helicity protection which
  P⁽⁰ˢ⁾ does not have. The draft's "scheme-independent pure number" claim is withdrawn.
- **"Anomaly coefficient mistaken for a beta function."** Avoided: the anomaly candidate was
  screened out on the record's own anti-running property.
- **"Hidden new primitive." — PARTIALLY LANDED (§7 was wrong).** No primitive enters the
  *construction*; but the first draft's claim that **computing A₀ needs none** conflated two
  levels and is withdrawn — see §7 as corrected.

## 7 · What computing A₀ would actually cost — corrected

The first draft called this *"bounded, primitive-free, the same declared machinery."*
**All three are wrong, and the record says so.**

`ROOT1_KERNEL_ORIGIN.md` §1 gives the provenance of the loop that produced A₂ as **six
separate declared inputs**, including *"declared two-derivative EH **TT-TT-TT** cubic vertex
[INPUT microphysics]"*, *"declared massless **TT** graviton bath [INPUT]"*, and *"chosen TT
projector [INPUT, `p_tt_ansatz`, +1]"*. And `K_R_OWNER_CHARTER.md` §6 is headed **"K_R is
TT-scoped by definition."** A P⁽⁰ˢ⁾ external structure **cannot be projected out of a
self-energy whose external legs are both TT** — there is no scalar external component to
project onto. Obtaining A₀ would require: **(i)** a cubic vertex with a non-TT external leg
(the scalar analogue of an object itself carried as `[INPUT microphysics]`); **(ii)** a
probe/bath assignment in the scalar sector (the validated bath is the *TT* bath);
**(iii)** an owner ruling lifting §6's TT-by-definition scope — a ruling, not a computation.

**And there is no evaluation point.** The executed kernel sits at k_ext = 0, while the
{P⁽²⁾, P⁽⁰ˢ⁾} decomposition exists only at k ≠ 0 (*"k̂ is the only available direction"*).
At k = 0 there is no k̂ and hence **no channel decomposition at all**.

**The level-confusion, named:** the scalar channel is declared *structure* (true, via
`eft_operator_basis`); its loop coefficient is **not** thereby computable input-free. Those
are different levels, and conflating them is what produced the draft's error.

## 7b · What the draft missed in the other direction

The Phase-1 inventory was **incomplete**. The frozen retarded kernel carries **two** log
coefficients, −3/(1280π²) at ω⁴ and −13/(480π²) at H²ω², both frozen, both three-route
validated, both **slot-invariant** — and **their exact ratio 104/9 is already computed** and
already used in the record (it is the ε_H coefficient behind ROOT-1's derived refusal
boundary). The draft's "everything is conditional on A₀, which has never been computed" was
therefore overstated: a second log-carrying structure with an exactly known ratio already
exists. **It does not rescue transmutation** — 104/9 is a derived pure *number*, not a
generated *scale*, and the same μ-invariance argument (§5, Failure 1) applies to it — but it
belongs in the inventory and its omission was a defect.

## 8 · Result classification (all classes were available; the draft picked the wrong one)

**Class 2 — a candidate exists but there is no genuine running.** Not class 1 (a viable
dimensionless candidate *does* exist in declared structure), not class 3 (the draft's claim;
withdrawn — nothing runs, so there is no flow to fail to generate a scale from), not class 5,
not class 6. **Class 4 is not excluded** as the draft asserted: any route through A₀ would
require the explicitly priced new inputs of §7, so a conditional mechanism resting on them
remains formally available and would have to be justified separately.

## 9 · Disposition

**Q3: OPEN → GATED** (design gate built and rendered; the owner applies the ledger change).
**No computation is authorized**, and none is proposed: the §7 route is priced, not
recommended.

The gate's purpose was to determine whether a genuinely generative route exists that the
program is entitled to pursue. **The answer, from a constructive attempt that was actually
made rather than an audit of the old record: not by this route.** The one candidate with the
right profile — dimensionless, declared, unpinned by the action — **does not run**, because
renormalization-point independence is precisely the statement that its coefficients do not
depend on μ. That is a structural reason, obtained without inserting anything, and it is more
informative than the historical-absence finding the audit-only framing would have produced.

## 10 · Disclosed defects in this gate's first draft

Both audits failed the draft. **Audit A** verified every quote, both absence claims, the
name-collision analysis, and re-derived all four algebraic results exactly in sympy (zero
residual) — then found §7's "no new primitive" claim refuted by ROOT-1's own six-input
provenance chain. **Audit B (hostile anti-transmutation refuter)** destroyed the construction
itself, and I verified its two decisive claims independently:

1. **β_r ≡ 0.** The draft differentiated at fixed subtraction constants; the record's frozen
   μ-shift law makes each channel coefficient exactly μ-invariant. *The claimed running was
   kinematics relabelled as RG flow.*
2. **μ* ≡ μ.** The draft's "generated scale" was a circular re-derivation of the definition —
   the inverted bracket **is** L, so μ*² = ω²·(μ²/ω²) = μ². Not an invariant at all, and
   strictly weaker than the record's existing Λ_R.
3. **r is a form factor, not a coupling** — the register types c₀, c₂ as functions of external
   kinematics, so "beta function" equivocated.
4. **§7 was wrong on three counts** (no primitive-free path; not the same machinery; no
   evaluation point at k_ext = 0), and the class-4 exclusion built on it is withdrawn.
5. **The inventory was incomplete** — the second frozen log coefficient and the already-known
   exact ratio 104/9 were absent from the draft entirely (§7b).
6. **Naming collision** — the register's declared x := c₀/c₀^trace-only carries banked numbers
   (a DESI-window bound, x = 1 excluded, μ(x) = 1 + xα); this gate's ratio is a **different
   object** and inherits none of them. Renamed **r** throughout to prevent a reader importing
   those bounds.
