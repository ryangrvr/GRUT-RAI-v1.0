# ROOT-1 RECONCILIATION — KERNEL ORIGIN, SELECTION, AND DESTRUCTION

**Date:** 2026-09-04 · **Instrument:** `root1_kernel_origin.py` · **Battery: 42/42.**
**Base:** 8449984 (Phase 12 closed). **Primary:** `wf_e1d7a5df-b9e` (31 agents).
**Adversarial leg (PART XIII):** `wf_8cf50411-4b2` (5 agents).
**VERDICT: `KERNEL-STANDARD` — primary and leg AGREE.**
Read-only. Register sha256 identical pre/post (`beaeb84e8a6f8468…`, 74 nodes). No A–F
selection. No observable selected. No new microscopic parameter. Nothing banked. W-0.

> ## THE ANSWER TO THE CENTRAL ROOT QUESTION
>
> **Does anything internal to GRUT, as opposed to a declared input or standard EFT/QFT
> machinery, select the GRUT response kernel?**
>
> **NO.** *Why this kernel: **because standard QFT/EFT produces it**, acting on inputs
> GRUT declares rather than derives.*

## 1 · THE OBJECT UNDER EXAMINATION, AND THE SCOPE THAT MUST TRAVEL WITH THE VERDICT

```
declared two-derivative EH TT-TT-TT cubic vertex     [INPUT microphysics]
 + declared massless graviton bath (gapless cut, DOS ~ ω²)   [INPUT]
 + declared BD-analogue Option-3a state               [INPUT, D3]
 + declared Option-β dim-continuation, no IR scale     [INPUT, D5]
 + declared k→0-first / ω→0-last order of limits       [INPUT, D1]
 + chosen TT projector       [INPUT, p_tt_ansatz, tier=assumed, ledger_delta +1]
    ──[ ordinary one-loop Schwinger–Keldysh / Feynman–Vernon ]──►   K_candidate
```

Not one link is a GRUT principle. The ω⁴ decomposes as 2 (radial measure at d=3) + 2
(excess momentum weight of two two-derivative vertices); the "+1" giving s_J = 5 is the
registered friction **definition** Im χ = J/ω. Coefficients are set by bath field content;
Λ_R is the inserted renormalization point; the cut is the ordinary massless two-particle
threshold.

> **⚠ SCOPE — ADOPTED FROM THE ADVERSARIAL LEG, WHICH RAISED IT AGAINST ITS OWN VERDICT.**
> `CHARTER.md` §4 lists among **named failure modes to recognize and refuse**:
> *"**Wrong object** — the T=0 vacuum exponent is not the memory; memory is the finite-T
> transport object."* K_candidate **is** a T=0-graded vacuum exponent, and this campaign
> **derived** that the declared scheme is blind to the de Sitter temperature (§3, O4).
> The kernel GRUT actually asserts — finite memory, single pole, s = 3 — lives at ω ≲ H
> and **was never computed there**. Therefore: `KERNEL-STANDARD` means **the stand-in is
> accounted for by standard physics**. It does **NOT** mean GRUT's claimed kernel has been
> accounted for, and it must never be quoted as such. On the claimed object nothing
> determines the kernel — not GRUT, not standard EFT.

## 2 · DERIVATION STATUS

**Derived given the declared inputs; forced by no principle.** The exponent is forced by
*(two-derivative vertex + gapless cut + scale-freeness)* **jointly** — and all three legs
trace to declarations: the vertex order is *"INPUT microphysics (Einstein-Hilbert), not a
principle"*; the gaplessness is the declared massless bath; scale-freeness is downstream of
the owner's *"IR: dimensional continuation ONLY; NO explicit IR scale."*

**Machine facts (computed, not quoted):** tier `derived` holds **0 of 74** register entries
(histogram: shown 12, assumed 17, derived-pending 4, to-derive 20, measured 3, postulate 14,
heuristic 2, open 2). `u2_kernel_universality` — the one registered route with selective
power — is `to-derive` **and `depends_on` rung3**, so the selective route lies *downstream*
and is unreachable by going deeper. `u3_split_origin` and `u4_constitutive_origin` are graph
isolates (`depends_on == []`, named by no node).

## 3 · IR RESULT — ω ≲ H IS NOT MERELY UNRESOLVED, IT IS **UNASKABLE**

Four independent obstructions, each separately sufficient:

- **O1 · the boundary is DERIVED, not declared.** ε_H = (104/9)H²/ω², and
  **(13/480)/(3/1280) = 104/9 exactly** — the coefficient *is* the ratio of the two computed
  absorptive coefficients. So ε_H ≥ 1 literally states "the second term of the H-expansion
  equals or exceeds the first," and the refusal at ω = √(104/9)·H = **3.3993H** is a *result
  of the calculation*. It cannot be loosened by declaration.
- **O2 · there is no frequency variable there.** `background_time_translation_flow` is
  tier `assumed`, +1, and its own text: *without the flow "there is no single-ω kernel and no
  ω→0 transport coefficient to conjecture about."* Its only named discharge is the static
  patch while the declared patch is flat FLRW — and it is **exhibited false** for the TT
  graviton (shapes differing up to 134% across epochs). **ρ(ω), J(ω), Im χ(ω) are not
  defined objects there.** Any low-frequency spectral claim — convergent **or** floored —
  presupposes exactly what is missing.
- **O3 · an unregulated IR log at O(H²)**, coefficient −8ω²/15 per H² at d=3; nine candidate
  regulators swept, **zero licensed, none adopted**.
- **O4 · the declared scheme is provably blind to the effect it is asked to adjudicate.**
  The candidate floor is thermal, but dS thermality is invisible to the H-grading:
  exp(−2πω/H) vanishes to all orders, and the blindness was **derived** (coth(πω/H) − 1 has
  vanishing limit and vanishing first and second H-derivatives at fixed ω > 0), not asserted.

> **STANDING GUARD ADOPTED HERE (the 7th-occurrence lesson, pointed at a *favourable* null).**
> Any future *"we computed it and there is no floor"* produced from a graded calculation
> **must be refused on this ground** — it would be a gate whose outcome is definitional, in
> the adverse direction. The scheme can return neither a floor nor its absence.

**The "new scale required" framing is wrong and is refused in advance.** GRUT already *has*
the number: `rung2_kms_gate` records that Hadamard/KMS forces T = T_dS = H/2π uniquely
("the horizon FORCES the noise level"). What is missing is a **licence** to use it, a
**method** non-perturbative in H, and — categorically different from both — a **proved
stationary reduction**, without which the question has no referent.

## 4 · POLE VS CUT

**No pole/memory feature survives that ordinary EFT fails to predict, and GRUT forces none.**

- **Cut: mandatory but input-forced** — the ordinary massless two-particle threshold; gapped
  alternatives are excluded by the declared massless bath (a Class-B standard input).
- **Pole: none certified anywhere.** No **residue** is computed anywhere in the repository
  (grep-verified, zero hits); no **width**. No pole has been shown gauge-invariant.
- **Both naive inferences FAIL, and the repository refutes them with its own numbers.**
  "Cut ⇒ no pole" is false (matter-scope first-sheet poles coexist with the cut); "TT
  projection precludes a pole" is false (the matter pole hunt ran in the TT sector). The
  matter-scope fence is respected: nothing is imported from it.
- **The decisive scope fact:** GRUT's claimed relaxation pole sits at ω ~ H₀ — *inside the
  region the evaluator refuses.* **"No pole" is a statement about ω ≫ H; the pole was never
  looked for where it was claimed.**

## 5 · ORDINARY-EFT HEAD-TO-HEAD

Ordinary open-system EFT produces all of it: the influence-functional form (the register's
own `u1`: *"standard open-system physics, NOT a GRUT result"*), the dissipative tensor sector
(a **named, published mainstream** open-EFT graviton-friction parameterization, not a
GRUT-private construct), and the pole machinery (standard Dyson resummation). The register's
own ledger already files *"single-pole relaxation (contradicted at contract scope)"* on the
must-not-market list. **Nothing survives the head-to-head that ordinary EFT cannot explain.**

## 6 · SURVIVING GRUT-SPECIFIC CANDIDATES — **NONE**

All nine variation axes (bath spectrum, state, coarse-graining, field content, interaction,
symmetry, renormalization, probe, response-object) produced a countermodel. Nine rescue
principles were classified: **five category-2 (standard QFT/EFT), four category-5 (ad hoc),
ZERO category-4 (genuinely new GRUT principle).** A single category-4 would have flipped the
verdict; the gate is two-sided.

The leg confirmed all four category-5 rescues independently, two on **stronger** grounds than
the primary gave, and the register refutes the three natural rescue routes itself:

| route | the register's own words |
|---|---|
| passivity | `passivity_channel_diagonal` (tier `shown`): the admissible set is a **convex cone**, closed under per-channel rescaling — it *"ORIENTS each channel and can never bound an amplitude or select a ratio."* |
| FDT/KMS | `rung9b_bridge` / NO_GO_LEDGER: *"FDT fixes shape/temperature but LEAVES the overall scale c₀ free (FDT does not rescue the bridge)."* |
| the premise | `CHARTER.md` §2: *"the favorable lean is near-circular — GRUT's finite-memory/local-influence-functional axiom **is** the analytic class, so the lean is the premise restated."* |

**The structural explanation, in GRUT's own voice** (`docs/WHERE_IT_STOPS.md`): *"a class has
no scale, and the framework asserts the class"*, and the cone barrier blocks ratios — *"two
distinct barriers, one for scales and one for ratios, and together they are why every route
from this framework to a number runs outside it. **The action carries a family.**"*

**The program already ran this test, pre-registered, and lost it.** `X_FLOOR_MAP.md` posed
"does any derived structure FORCE x" with an overseer decision criterion fixed in advance;
all four routes returned no pin (R1 *"RETURNS NO PIN"*; u5/R3 *"classifier, not pinner"*;
rung3 frontier-blocked), terminal state **"D3 — NOTHING PINS (modal)"**. That gate was *not*
definitional — R1 could have returned a scheme-immune pin, and the passivity run's first
tolerance actually **faked a ceiling in the flattering direction before its own selftest
caught it.** It is the most honestly instrumented evidence in the repository, and unanimous.

**The one selection principle ever attempted** is on an archived branch
(`origin/v2:theory/GRUT_SELECTION_PRINCIPLE.md`, June 2026) and was **killed in-house**, in
its own text, before this campaign existed.

## 7 · EMERGENT PARAMETER OR FUNCTION — **NONE**

Λ_R, the object's one free quantity, is algebraically the inserted μ. A reparameterization is
not emergence. *(Numerical defect self-caught by the leg and recorded: exp(κ/2) =
0.7948345635404438444…; the handed-down 0.794700 is wrong in the fourth figure.)*

## 8 · STRONGEST SUCCESSFUL COUNTERMODEL

**A Wilsonian system/bath partition at a comoving scale q_s**, holding every declared input
fixed. It multiplies the H⁰ absorptive part by **θ(ω − 2q_s)** — turning the banked
*unconditional* gapless branch point into a **gapped threshold** and destroying "c0 = c2 = 0,
EXACT, structural."

It is admissible because — verified here, and **stated by no prior document** — the contract
declaration sheet fixes D1 (probe kinematics), D2 (gauge), D3 (state + IR), D4 (dual gauge)
and D5 (renormalization), and **never declares the system/bath mode partition**: zero
occurrences of "partition" or "system/bath" across the entire D-sheet and owner ruling. **A
load-bearing input is undeclared.**

## 9 · STRONGEST SUCCESSFUL RESCUE ARGUMENT — **none succeeded**

The strongest *attempted* rescue is **Constitutive Response-Object Primacy** (exactly one
distinguished response object, the 1PI kernel K_R = Σ_R, not the Dyson-dressed propagator).
It fails as a free selector because the register has **already pre-adjudicated the route
twice**: `eft_operator_basis` — *"the SYMMETRY route to FORCED is definitively closed; only a
DYNAMICAL (bath-microphysics) route survives — a trace-correlator vanishing that would cost a
new +1 at rung3, **RELOCATING the assumption rather than discharging it**"*; and
`NO_GO_LEDGER.md` entry 2 to the same effect. **Any primacy principle is priced as a new
input by standing ruling.**

## 10 · GOVERNANCE DEBT (recorded, not resolved — no precedence rule invented)

1. **CHARTER vs register vs read-only audits.** `CHARTER.md:3` makes every artifact
   subordinate to it, and `CHARTER.md` never mentions `PHYSICS_LEDGER`. The 2026-09-03 audit
   run is unbanked, un-indexed, and absent from `AGENT_COORDINATION.md`. Precedence is
   **unresolved**; this record does not choose.
2. **Two disagreeing dependency orderings.** Machine (`depends_on`) vs published prose
   (STATE.md:47, POSTULATE_MAP.md:89, GRUT_II_Agenda.md:59). Neither ROOT-0 nor its leg used
   both. Unresolved.
3. **The register still carries the unamended s = 3** while `CLASS_C_DISPATCH_SPEC.md:73`
   reads *"No J(ω) ∼ ω³ — falsified at class A; importing it anywhere is laundering."*
4. **A stale parametric deferral no document connects** — `WALL_KR_CONTRACT_RETARDED_VERDICT.md`
   still records c0 = 0 as *"DEFERRED, recorded parametrically"*, while D5 has since made
   c0 = 0 **exact and structural**.
5. **ROOT-0 retired**, preserved uncommitted, stamped as a failed instrument.

## 11 · OWNER DECISION OWED — cheap, and it currently decides a pre-registered test

**IS THE REGISTERED OBJECT THE KERNEL OR THE DRESSED RESPONSE?** Every classification-bearing
verdict was read on χ = −K_R (**undressed**). The **dressed** object gives
**lim Im G_R = −3κ⁴/(320π)** — Ohmic and log-divergent, **the opposite side of the
pre-registered convergence boundary, and the side that trips rung1's own falsifier.** The
pre-registration's pipeline and the Class-C manifest both name the **dressed** object; the
executed chain used the undressed one. Verified here: **zero "dressed" mentions across all
four 2026-09-03 audits** — no document carries the fork forward in either direction. And the
divergence between the readings is contingent on c0 = 0, which D5 has since made exact — so
**the fork may already be decided in the adverse direction by a result the record has not
caught up with.**

## 12 · THE SINGLE DEEPEST UNRESOLVED QUESTION

**WHAT IS THE BATH?** — what the vacuum is made of, and by what partition it is separated
from the system. This is **GRUT's own nomination**, not this campaign's: `CHARTER.md` §3 —
*"the deepest open item: **what bath Hilbert space was integrated out to make the influence
functional** … It decides single-pole, the rheology … **It is NOT an in-house calculation** …
**Banking a resolution of this in-house is an automatic fail.**"*

Every one of the nine broken axes descends from it: bath content (A, D) **is** this question;
the state (B) is the bath's quantum state; the coarse-graining (C) is the partition that
defines it; the vertex (E) reduces to it, since what runs in the loop is what is in the bath.
`rung3`'s own `boundary_condition` closes the loop: *"Which GRUT's bath instantiates is
decided by the UNPINNED system/bath split."*

**What would actually move it, named and not supplied:** a theorem that the IR kernel is the
same across two or more distinct microscopic/QG completions (`u2` — blocked C+F), or a
forced-conditions/forced-kernel theorem. Both unexecuted. Absent either, *"why this kernel"*
has no GRUT answer.

## 13 · FINAL

**VERDICT: `KERNEL-STANDARD`** — primary and adversarial leg agree, independently.
**WHY THIS KERNEL: because standard QFT/EFT produces it**, acting on inputs GRUT declares
rather than derives — and GRUT's own two structural barriers (a class has no scale; the
admissible set is an amplitude-homogeneous cone) explain why nothing internal ever could.

**No observable selected. No Γ_T, no QNM, no GW, no cosmology, no preregistration.**
The kernel did not survive the root-level attack, so the right to build on it was not earned.

## GOVERNANCE EXIT

Register sha256 pre == post (`beaeb84e8a6f8468…`, 74 nodes); no tracked file modified by this
campaign; HEAD == origin/v4 verified by **ref identity**, not branch name; A–F **UNSELECTED**;
no new microscopic parameter; no fitted parameter; no reverse engineering; ROOT-0 preserved as
an uncommitted failed instrument.

## W-0 STATUS — kernel origin adjudicated and reported; nothing banked.
