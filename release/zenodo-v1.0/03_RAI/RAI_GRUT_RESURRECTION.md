# RAI-GRUT RESURRECTION — THE U3/U4 REOPENING

**Date:** 2026-09-04 · **Base:** eb65a34 · **Instrument:** `rai_grut_resurrection.py` · **Battery 22/22**
**Blind reconstruction:** `wf_151ebf60-954` · **Primary:** `wf_74de2095-08f` · **Hostile:** `wf_df16c2a3-e18`

> ## STATUS: **`D — NOT RESURRECTED`** — primary and hostile agree.
> **u3_split_origin = UNDETERMINED · u4_constitutive_origin = ARTIFACTUAL (contested — see §3)**
> **Kernel origin = F (NO WELL-DEFINED REFERENT) for the *asserted* kernel · Genuinely derived: NOTHING.**

**Machine-readable status: `D-NOT-RESURRECTED`** (primary `wf_74de2095-08f` == hostile
`wf_df16c2a3-e18`; the agreement precondition for commit is met).

**Register sha256 identical pre/post (`beaeb84e8a6f8468…`, 74 nodes). Both fences unmoved. No prior
result modified. ROOT-0 still preserved uncommitted. A–F unselected. W-0.**

> ## ⚠ THE MOST IMPORTANT FINDING IS NOT THE STATUS
> **This campaign has an ASYMMETRIC ERROR BUDGET, and it produced a systematically negative record
> with nobody being biased.** Positive claims in this corpus face source verification, deletion
> tests, teeth-controls, wording gates and mutation testing. **Negative claims face none of it.**
> Machine-checked here: mutation-testing artifacts exist but cover **one subject**; exactly **1 of
> 74** register nodes carries a credit. Errors that produce negatives survive; errors that produce
> positives are caught. **That is worse than bias, because it is invisible to every self-check this
> programme actually ran** — and it was found only by the first agent ever *mandated to attack a
> negative*.

---

## 1 · RETRACTION — the flagship negative was wrong, and wrong-signed **[RECOMPUTED]**

`calc/RESULTS_tt_worldline.md` **Finding 1 is RETRACTED.** It reported ⟨h²⟩ decaying 127 → 0.002.

**Cause:** `calc/tt_worldline_spectrum.py:60` — `pref = 1.0/(2.0*k**3*a1*a2)` — carries a spurious
1/(a₁a₂). The Bunch–Davies **strain** mode is u_k = (H/√(2k³))(1+ikη)e^{−ikη}, with **no explicit
scale factor** (the canonical variable carries a factor of *a*, not its inverse). The docstring at
line 21 declares the same wrong mode function, so the code is faithful to a wrong specification.

**Independently recomputed by this instrument** (band [20,60], H=1, a=eᵗ, t = 0…4):

| prescription | t=0 | t=1 | t=2 | t=3 | t=4 |
|---|---|---|---|---|---|
| buggy 1/(a₁a₂), comoving band | 40.556 | 0.746 | 0.014 | 0.0003 | 0.000 |
| **corrected**, comoving band | 40.556 | 5.513 | 0.770 | 0.128 | 0.041 |
| **corrected**, comoving-IR / physical-UV | 40.556 | 44.962 | 45.580 | 45.686 | **45.722** |

**The trend is sign-flipped.** Under the standard prescription in which the known minimally-coupled
IR secular growth lives, ⟨h²⟩ **grows**. It does not decay to zero.

**And the gate was sited where it could not see.** The sole validation call is
`g_two((20.0, 60.0), 0.0, 0.0)` — at t=0, where a=1 and buggy and corrected agree **to machine
precision** (verified: |Δ| < 10⁻¹²). *A check placed at the unique point of blindness is the
signature of a gate written to pass.* It survived from 2026-08 until an agent was told to attack it.

**Finding 2's channel contrast is PRESCRIPTION-DEPENDENT and must never be quoted bare:** fixed
comoving band — strain 134.2% vs conformal control 130.5%, **no contrast**; co-dilated
(dS-invariant) band — both stationary to 12 digits, **no contrast**; comoving-IR/physical-UV —
strain 44.2% vs conformal 0.9%, **contrast real**, and the mechanism is standard Vilenkin–Ford /
Linde / Starobinsky IR secular growth, belonging to nobody in particular. **Findings 3–4**
(τ_eff = 0.40/0.33/2.40; W* < 0.25 e-folds) are quantities of one unnamed prescription and must be
re-priced or withdrawn.

**Per governance, `calc/RESULTS_tt_worldline.md` is NOT edited.** The defect is recorded here as
provenance. The failure is preserved.

## 2 · WHAT HAPPENED TO u3 — the demotion was wrong on its own terms **[WALKED]**

The 2026-09-03 demotion (`fd6d6fd`) called u3 a graph isolate "load-bearing on nothing." **The
premise is literally true and the conclusion does not follow.** Both verified by walking the register:

- `u3_split_origin.depends_on == []`, and no node names it. **Isolate: confirmed.**
- `rung1_inin_formalism.ledger_note` prices *"the system/bath split"* as **prerequisite #1** inside
  its `ledger_delta: +4` — and **28 of 74 nodes** transitively depend on `rung1_inin_formalism`.

**The split has no dependents *as a node* only because it was booked as priced prose inside another
node's ledger_note.** Graph isolation was a bookkeeping artifact, not a fact about the physics. The
programme mistook "no edges drawn" for "load-bearing on nothing."

**And the demotion's engine was withdrawn six minutes later** (`WALL_KR_U3_EFT_BASELINE.md:38`,
*"'Placement is immaterial' was too strong, and I withdraw it"*) and never propagated. **Recorded as
provenance, not repaired.**

**u3 status: UNDETERMINED.** No derivation was exhibited in either direction. The fence stands.
*Poverty of primitives, machine-checked:* rung1's transitive ancestor set is a **single node**,
`{background_time_translation_flow}`. A one-parameter automorphism group does not select a
subalgebra; the one it canonically selects is its fixed-point algebra, which is not GRUT's system
(the probe is time-*dependent*). **No derivation of the split from GRUT primitives is available.**

## 3 · WHAT HAPPENED TO u4 — dissolution CLAIMED, then KILLED

The primary claimed an exhibited dissolution: Nakajima–Zwanzig/Mori returns drift + memory kernel +
noise exactly, for **any idempotent projector**, consuming none of weak coupling, Gaussianity,
near-equilibrium or timescale separation — so the constitutive form is what the leading term of any
causal differentiable functional of a projected variable *is*, meeting u4's registered dissolution
clause and exceeding it.

**The hostile killed it on four independent counts, and the kill stands:**

1. **"ANY idempotent projector" is false at source.** The formalism needs an **orthogonal**
   projection. The orthogonal-dynamics existence premise is real and named: Givon–Hald–Kupferman
   (*Israel J. Math.* **145**, 221, 2005) prove classical solutions only for **finite-dimensional-range**
   P. GRUT's is infinite-rank. Widder & Schilling (arXiv:2604.20453): *"A completely rigorous
   derivation is only possible for simple special cases. To this day, general derivations should be
   considered heuristic."* **A premise the pass did not know it had.**
2. **Hidden state choice, already documented in three repository files the pass never cited.**
   `ARROW_OF_TIME.md:30` / `calc/RESULTS_arrow.md:23` / `docs/WHERE_IT_STOPS.md:161`: the NZ
   inhomogeneous term must be retained for exactness; calling it **"noise"** requires an ensemble
   over initial conditions, stationarity, and the second FDT — *exactly the conditions the pass
   claimed to consume nothing of, reintroduced under a new name.*
3. **The pass's own back-door finding is fatal to its own claim and it did not wire it up.** Writing
   the kernel as ⟨F(τ)F(0)⟩ requires P orthogonal w.r.t. a **state-induced Kubo–Mori inner product**
   — so producing GRUT's registered object needs the state. Already found in-house a fortnight
   earlier: `calc/mz_inheritance.py` — *"rung3's phrase 'the Mori-Zwanzig kernel' does not currently
   denote a unique object, and the two objects it could denote answer this question OPPOSITELY."*
4. **The dissolution is `u1_form_universality` restated.** Already tier `shown`, already priced at
   zero: *"U1 being TRUE is GENERIC and confers NO GRUT-specific content."* Substituting
   Mori–Zwanzig for Feynman–Vernon is **vocabulary substitution**. u4's own tier_note refuses the
   move in advance.

> **THE MANDATED ANSWER (Section XI): RELOCATED, NOT DERIVED.** u4's content did not move one level
> down. It moved **four ways sideways** into things already open — which projector (u3), why the
> kernel decays (rung3), the state supplying the inner product (unpriced anywhere), and the
> 𝒬ρ(0)=0 deletion the repository itself books as the arrow's origin. **u4 was not dissolved; it was
> reduced to u3 + rung3.**

**u4 status: ARTIFACTUAL as claimed by the primary — CONTESTED by the hostile.** Recorded as a
disagreement, not reconciled. **The fence is unmoved; nothing is banked in either direction.**

## 4 · THE LAYER INVERSION nobody checked **[QUOTE-VERIFIED]**

`GRUT_ToE.md:216`: **"Modular theory = KMS = rung2."** rung2 is the FDT/KMS gate applied to an
**already-split** system. So answering u3 — a *below-rung1* question — with modular inclusions
grounds a foundational question in a rung2 object. **That is circular, and the circularity is
registered in this repository's own synthesis line.** Three hostile lenses argued about Takesaki;
none checked whether the answer they were debating was already booked downstream of the thing it was
supposed to ground.

**The criterion the Gorilla self-attack supplied:** *a vocabulary has reached its boundary exactly
when its primitives contain the explanandum.* Modular theory's primitives are (M, φ). **u3 asks
where M comes from. A theory whose primitive is M cannot select M.** Takesaki's theorem is not a
source of splits — it is a **filter on splits already on the table**, and filters do not generate
their own inputs.

## 5 · THE BLIND RECONSTRUCTION (Section VII, locked before comparison)

Three independent angles, none knowing GRUT exists, converged:

- **Decomposition into PARTS is not forced and is REFUTED** in the relevant regimes — type III₁
  admits no tensor factorization; a Gauss law leaves a **center**, not a factor; the split-state set
  is **empty** in perturbative massless gravity; a k-local tensor structure exists only for a
  **measure-zero** set of Hamiltonians. *"My architecture contains no parts, and its not containing
  parts is derived."*
- **What IS forced is a one-sided INCLUSION**, by a one-line argument: relative entropy is invariant
  under automorphisms, so nonzero monotone entropy differences require a proper inclusion N ⊂ M plus
  a reference. *Parts are "a luxury of the type I special case."*
- **Coarse-graining is generically unavailable** — Takesaki: a normal state-preserving conditional
  expectation exists **iff** the subalgebra is modular-invariant, which causal/regional subalgebras
  generically are not.
- **Susceptibility is derived** — the first variation of relative entropy under deformation of the
  cut is the modular energy (Faulkner–Leigh–Parrikar–Wang 2016).
- **And its own honest deflation:** *"THE CONVERGENCE IS REAL BUT NOT NEW… essentially algebraic QFT
  plus modular theory. I did not invent it and I will not present it as invention."*

## 6 · SECTION XIV — THE FOURTEEN ANSWERS

| # | question | answer |
|---|---|---|
| 1 | u3_split_origin? | **UNDETERMINED.** Demotion premise true, conclusion false: load-bearing on 28 nodes via rung1's priced prose. Fence stands. |
| 2 | u4_constitutive_origin? | **ARTIFACTUAL (primary) / CONTESTED (hostile).** Dissolution claimed then killed; reduced to u3 + rung3. Fence stands. |
| 3 | Is system/bath fundamental? | **Not established either way.** What the blind reconstruction forces is a one-sided *inclusion*, not a two-sided split. |
| 4 | Is response fundamental? | **No.** The response *form* is split-free; the response *interpretation* imports an exterior — observer/world, not system/bath. |
| 5 | The kernel? | **F — no well-defined referent** for the *asserted* kernel (ω ≲ H, where it is UNASKABLE on four obstructions). The computed stand-in is E (generic). |
| 6 | What survives of GRUT? | The machinery, none of it GRUT's. One forced item, not GRUT's: T = T_dS = H/2π with zero freedom. |
| 7 | What does not? | Finite memory; the single pole; a memory time; any GRUT-specific selection. |
| 8 | Genuinely derived? | **NOTHING.** |
| 9 | Remains input? | Everything GRUT-specific: the partition, the probe, the order of limits, the state, the scheme, the gauge, the bath content, the vertex order, the stationarity of the flow, the ontological stance. |
| 10 | Strongest hostile objection? | The u4 dissolution is `u1` restated by vocabulary substitution — and the flagship negative rests on a normalization error whose gate was sited where it could not fire. |
| 11 | Strongest surviving result? | The forced de Sitter temperature (Gibbons–Hawking, 1977, borrowed) — and, negatively, that no clock is forced with it. |
| 12 | What would discriminate? | **T1:** run the register's own deletion test inside a formalism whose primitives contain neither an algebra nor a state (causal sets, CDT). *Computationally accessible, and nobody has run it as a test.* |
| 13 | What did the Gorilla Audit discover? | A structure repeatedly inserted rather than derived across seven programmes — **and, here, the asymmetric error budget in the auditor itself.** |
| 14 | What did it mistake for the Gorilla? | The *split* as a two-sided partition. What is forced is a one-sided inclusion; and modular theory, offered as the answer, is booked downstream of the question. |

## 7 · SECTION XV — IS THERE A STRUCTURE NATURE APPEARS TO REQUIRE?

> **Yes — one, and it is smaller, older and less flattering than the theory built on it.**
>
> A universe expanding at a steady rate does not leave empty space free to be anything. Demand only
> that the quantum fields look the same at short distances everywhere, and that nothing blows up at
> the edge of what any drifting observer can see, and **exactly one state of the fields is left**.
> Nobody chooses it; the geometry and the demand for regularity choose it. And that state is warm,
> carrying a fixed level of fluctuation set by the expansion rate alone, with no adjustable number
> anywhere. **A real case of a structure nature appears to require — and a fifty-year-old result
> that belongs to nobody in particular.**
>
> **What it does not contain is a clock.** The geometry fixes how loud the fluctuations are, and
> that correlations come apart. **It does not fix how fast.**

**CONTESTED, and the contest is recorded rather than resolved:** the hostile finds that Allen's
theorem — that the minimally-coupled sector admits no de Sitter-invariant vacuum, stated in the
literature to cover gravitons — bears on exactly this claim for GRUT's own degree of freedom, and
that `RESULTS_tt_worldline.md` says so in-house. **The one surviving positive claim is contested
precisely where GRUT needs it.** And the retraction in §1 removes the computational support the
primary had attached to "no clock": the *conclusion* may stand, but **its evidence does not.**

## 8 · GOVERNANCE DEBT (recorded, unresolved)

1. **Two incompatible accounts of what GRUT's split IS**, five minutes apart on 2026-09-03 and never
   reconciled: a scale/mode split for which "Wilsonian decoupling supplies most of the answer"
   (`fd6d6fd`), and a cutoff-free external-leg/internal-line partition explicitly ruled **"NOT B
   (Wilsonian momentum-shell)"** with "no cutoff parameter whose placement could be varied"
   (`9b9036b`). **If these pose *different questions* rather than describe one twice, status F
   becomes correct and D is an artifact of treating a contradiction as a typo.**
2. `GENERIC_KERNEL_SUBSTITUTION.md` still says the single-pole discriminator "has not been computed."
   **It has** — `RUNG7_TWO_POLE_COMPARISON.md`, committed alongside it in `e069fd8`. Verdict: every
   purely relaxational kernel (Debye, two poles, three poles, Cole–Cole) stays on one side of w = −1;
   only an oscillatory pair crosses. **"Single-pole is decorative for w = −1 crossing."**
3. `calc/gw_tensor_friction.py` — **verified absent.** The one live empirical door has a shared
   parameter, a null result, and no GRUT entry.
4. **No negative-control discipline exists anywhere in the corpus.** See the banner.
5. One quotation used by the primary (*"a genuinely closed universe has no external sources"*) is
   **not in the corpus** — grep returns zero matches. Re-marked as the pass's own premise.

## 9 · FIVE PRIMITIVES PROPOSED AND REJECTED (Section IX's brutal rule)

Each had "because GRUT needs it" as its only warrant. **X1 — a second internal bath scale:** rejected
and *self-defeating* — `rung3`'s own statement conditions single-pole on *"PROVIDED the vacuum bath
carries no second internal dynamical scale,"* so the insertion that rescues rung7 breaks rung3.
**X2 — response-object primacy:** pre-adjudicated twice as *"RELOCATING the assumption rather than
discharging it."* **X3 — identify the cosmological flow with a modular flow:** pre-registered as
failing by this repository before the fact.

## GOVERNANCE EXIT

Register sha256 pre == post; **no prior result modified**; `calc/RESULTS_tt_worldline.md` deliberately
**not** repaired; ROOT-0 preserved uncommitted; both fences unmoved and nothing banked in either
direction; HEAD == origin/v4 by ref identity; A–F unselected; no new microscopic parameter; no
observable selected; no prediction created.

## W-0 STATUS — resurrection attempted, failed rigorously, and the failure is preserved.
