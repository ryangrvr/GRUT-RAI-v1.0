# Q2-BRIDGE DESIGN GATE — is the GRUT/O2 → stochastic reduction derivable now?

> **2026-09-07 · DESIGN / CAPABILITY GATE. NO computation performed.** No simulation, no
> numerical evolution, no sweep, no new primitive, parameter, scale, bath, cutoff or
> assumption. Q1, the Q2 execution record, the Q2-SY adjudication, the original Q2 wording,
> the register and the frozen corpus are all untouched. **Anti-leakage rule observed:** the
> Q2-SY numbers (0.009216 H, the 0.008892 H spectral solve, target-B reproduction, the
> 0.0333 H historical value, the Q2 convergence results) are **not used anywhere below as
> evidence about the bridge**; they belong exclusively to the inherited scalar subquestion.
> Reconstruction: an eight-axis read-only sweep of the record (workflow `wf_7c887942-043`).

## 1 · The question

> Can the interacting GRUT/O2 TT graviton zero-mode be **derived**, from already-declared
> structure, to reduce under controlled coarse-graining to an SY-class stochastic effective
> dynamics with (1) a derived effective potential, (2) a derived noise/dissipation structure,
> (3) the required consistency relation, (4) a **derived** effective coupling rather than a
> selected λ, and (5) a justified link from the resulting spectral gap to the
> lifted-versus-protected question?

**This gate does not attempt the derivation. It asks whether the derivation is presently
available without smuggling assumptions into it.**

## 2 · DISPOSITION: **BRIDGE BLOCKED** (decision-tree outcome C)

Not one blocker but **seven independent ones**, each separately sufficient, and several
**structural rather than merely unfinished** — i.e. the record contains a positive obstruction,
not just an unfilled slot. No outcome A (derivation available) and no outcome B (conditional
derivation) is reachable without new inputs, and this gate's own no-new-input constraint — the standing form of it in the record
(`GRUT_PREDICTION_GATE_GAMMA_T.md`: *"no new theory, no new kernel, no new scale, no rescue
parameter"*; `GRUT_NEXT_STEPS.md`: *"no rescue mechanism, no new rung"*) — forbids supplying
them.

## 3 · The bridge dependency map — twelve arrows, classified

| # | arrow | status **for the graviton sector** |
|---|---|---|
| 1 | GRUT/O2 starting equations | **ASSUMPTION** — the influence-action form is RECOVERED-generic (u1: "confers no GRUT-specific content") |
| 2 | field decomposition / TT projection | **STRUCTURAL_SELECTION** — `p_tt_ansatz` adjudicated **CHOSEN**, not forced |
| 3 | zero-mode identification | **DERIVED at free level only** (exact dS constant zero mode; conformal coupling gaps it at m_eff² = 2H²) |
| 4 | **interacting dynamics** | **DERIVED at ω ≫ H** (`kr_contract_retarded_tier4`, tier `shown`, incl. a resummed denominator on the reference slice) — **NOT_PRESENT at ω → 0**, where the evaluator refuses. *The break is regimic, not total* |
| 5 | environment/bath identification | **ASSUMPTION (declared stance, scale/mode)** — the contract declares *probe = long-wavelength TT perturbation, bath = the vacuum's own massless fast modes*. Declared, **not derived** |
| 6 | coarse-graining operation | **NOT_PRESENT** — the split's *form* is declared but **no window (comoving q_s) is declared**: ROOT-1 §8, *"A load-bearing input is undeclared"* |
| 7 | influence functional / reduced dynamics | **RECOVERED-generic** (universal form; no GRUT content) |
| 8 | retarded / dissipative kernel | **DERIVED at ω ≫ H only** — evaluator **refuses** ω ≪ H |
| 9 | noise kernel for the interacting zero mode | **NOT_PRESENT** |
| 10 | consistency relation (KMS/FDT) | **DERIVED in the graded T = 0 form only** — not the dS-thermal relation an SY reduction needs |
| 11 | stochastic effective equation | **NOT_PRESENT** |
| 12 | Fokker–Planck generator → spectral gap → lifted/protected | **NOT_PRESENT** |

**Arrows 6, 9, 11 and 12 are NOT_PRESENT; arrow 4 is present at ω ≫ H and absent at ω → 0.**
No arrow was filled with textbook knowledge. *Correction applied at audit: an earlier draft
marked arrows 4–6 flatly NOT_PRESENT and said "the chain never resumes," which contradicted
this gate's own §6 and the banked `kr_contract_retarded_tier4`. The break is at the zero
mode's regime, not at the existence of interacting TT dynamics.*

## 4 · The seven blockers

**B1 · There is no equation to reduce (first-order).** The interacting TT graviton zero-mode
equation is written down nowhere in any propagatable form; every occurrence is a noun phrase
naming an undone task. The record says so itself: *"The computation that would decide it (the
interacting graviton zero-mode) is **exactly the one nobody has done**"* (`RAI_GORILLA_T1.md`
§XVI-N); *"O2, the interacting graviton zero-mode (undone…)"* under
`GRUT_PROGRAM_FREEZE.md`'s heading **UNRESOLVED (genuinely open, fenced, unmoved)**.

**B2 · The one interacting graviton object that exists is evaluator-refused at the zero mode.**
The Tier-4 retarded TT self-energy carries the declared validity *"ω ≫ H with ε_H =
(104/9)H²/ω²; **ω ≪ H refused by the evaluator**"* — and by ROOT-1 O1 that boundary
(ω = 3.3993H) is a **result of the calculation**, so it "cannot be loosened by declaration."
The zero mode is an ω → 0 object. **The one asset points away from the target regime.**

**B3 · The target regime is record-declared UNASKABLE, not merely uncomputed.** Four
independently sufficient obstructions (ROOT-1 §3). Decisively O2: on the declared patch
*"ρ(ω), J(ω), Im χ(ω) are not defined objects there"* — **so a "spectral gap" for the
interacting zero mode has no frequency variable to be a gap in.** Ingredient (5) of the
bridge question is therefore not merely unproven but currently unposeable.

**B4 · The split is a declared stance with no declared window — not a derivation.**
*(Rewritten at audit; see §10.)* The record **settled** in
`PHYSICS_LEDGER/WALL_KR_U3_SCALE_SPLIT_CORRECTION.md` (2026-09-03) that **GRUT's split is
scale/mode**: *"the probe = a long-wavelength TT metric perturbation, with the bath = the
gravitational vacuum's own massless fast modes"* — *"GRUT splits by wavelength, not by
region."* The same file **withdraws** the type III₁ tensor-factorization argument as
irrelevant here (*"GRUT does not split by region, so the type III₁ obstruction does not apply
to GRUT's actual U3 object"*). **This gate does not use that withdrawn argument.**

What blocks is narrower and true: the split is **declared, not derived**. `rung1_inin_formalism`
books it as priced input #1 — *"STANCE, not derivation"* — with the register's own note that
*"a fixed Lorentzian background admits arbitrarily many system/bath partitions."*
`u3_split_origin` is `to-derive`, `default-BROKEN`, **fenced against pre-answering in either
direction**, and machine-checked **UNDETERMINED** (`RAI_GRUT_RESURRECTION.md`, 2026-09-04);
what is machine-checked structurally is that it is a **graph isolate** (`depends_on == []`),
which is the absence of an edge, **not a proof of underivability** — and this gate claims no
such proof. Decisively for a *reduction*: **no coarse-graining window is declared.** ROOT-1
§8 records exactly this — *"A load-bearing input is undeclared"* — for the Wilsonian partition
at comoving q_s. A reduction needs a window; the record declares a stance without one.

**B5 · No coupling is derived, and no scale is available.** `λ_grav` occurs in exactly two files
other than this gate — `program/gates/Q2_ADJUDICATION.md` and `program/QUESTION_LEDGER.md` —
both naming it as **owed, never as derived**. There is no claims node, no
calc, no ledger artifact for a graviton self-coupling or an effective potential for the TT
zero mode. **Of the six scales a stochastic reduction needs, only H and M_P are on the record
at all, and both are EMPIRICAL_INPUT.** The coarse-graining scale is NOT_PRESENT and would be
a NEW INPUT; μ is a **slot**, not a determination. → **BRIDGE-BLOCKER: COUPLING NOT DERIVED.**
*Record finding, narrowed at audit:* **no calculation derives m_eff² = 0.1H² for the
graviton.** Its only provenance is prose (`GRUT_PROGRAM_FREEZE.md`, `RAI_GORILLA_T1.md`) plus
the **borrowed** SY scaling rule m²_eff ∼ √λ H² with **λ selected** to reproduce it
(`Q2_STOCHASTIC_EXECUTION_PREREG.md` §2, classified STRUCTURAL_SELECTION). *(An earlier draft
said "no calc anywhere in the repository — prose-only"; that is refuted by grep — the value
appears in the Q2 calc files — and is withdrawn.)*

**B6 · No Markov limit exists, and no single rate exists to take one toward.** An SY-class
target is Markovian by definition (δ-correlated, overdamped, single-rate). The record's own
audit: *"Derived: nothing. Approximation: nowhere exhibited"* (`RUNG3_BRIDGE_SCOPE.md`), the
identification being *"an ADDITIONAL INPUT wherever it is used."* Worse than absent: the
computed free-level graviton object **names no single rate** — at fixed multipole the
surviving rungs are an infinite tower, lowest rate (ℓ+1)H, multipole-dependent. Compounding,
§XVI-H records that de Sitter forces **infinite, scale-free memory — the opposite shape** of
the Markovian target.

**B7 · The frame pincer — on the record's own on-point obstructions.** *(Rewritten at audit;
see §10.)* The zero mode lives on the cosmological slicing, where the record states there is
no global KMS and no global timelike Killing vector. The static patch **does** have both — and
the record ran the migration and **scored it a retraction**
(`provenance/prereg/RESULT_FRAME_MIGRATION_2026-08-19.txt`). Two findings there are directly
on point and are **stronger** than the leg this gate previously used:

1. **A TT decomposition is not available in that frame.** The static slice is an *open
   hemisphere of S³ — a manifold **with boundary*** — so the York split loses its
   L²-orthogonality; the file records `tt_decomposition_available = "no"`. **The one frame
   where KMS genuinely holds is a frame in which the TT object the bridge is about cannot be
   defined in the usual sense.**
2. **There is nothing to relax there anyway.** *"The free static-patch response for the
   graviton family has **NO decaying quasinormal mode at all**. The cavity is **TOTALLY
   REFLECTING** at every real frequency."* And the earlier gapped-tower reading was
   **self-retracted** (the boundary check never tested outgoingness).

Plus X1: [K, P_i] = +H P_i, so boost frequency and comoving wavenumber **admit no common
eigenbasis**. *(An earlier draft also cited the FDT/KMS scale-blindness as a positive
obstruction. `NO_GO_LEDGER.md` states that mechanism and, in its own boldface, forbids exactly
that use — "**a supporting mechanism (not a fourth obstruction — do not over-count the
negative)** … FDT does not itself obstruct; it simply fails to rescue." **That leg is
withdrawn.**)*

**Posedness note (independent of all seven):** the free TT worldline kernel was computed and
found **non-stationary** (>130% shape variation across epochs), so there is presently no
stationary reduced object for the graviton whose spectrum could be taken.

## 5 · Capability assessment (owner's item 12)

| required step | classification |
|---|---|
| cubic graviton vertex | **AVAILABLE** — but only in a domain that structurally excludes the zero mode |
| graviton coarse-graining / reduction | **REQUIRES FRONTIER TOOLING + NEW PRIMITIVE** |
| interacting-graviton noise + dissipation kernels | **REQUIRES FRONTIER TOOLING** |
| derived λ_grav | **REQUIRES NEW INPUT** |
| spectral gap of a written-down generator | **AVAILABLE IN-HOUSE** — *demonstrated in the Q2-SY arc (its pre-execution Fokker–Planck solve). Disclosed: this is the gate's one use of Q2-SY material, it is a capability fact rather than evidence about the bridge, and it cuts toward **less** blocked* |

**Three of five steps land inside the three sectors `RAI_CAPABILITIES.md` fences as
in-principle limits** (transport Σ; the dS trace/conformal sector; rung3 pole-vs-cut), where
in-house approximation is an **automatic fail** under `CHARTER.md` §3. **This is not a
judgement the gate may make differently — it is pre-committed.** And the program's designated
escape hatch — specify and hand out to a specialist — **has never once been exercised**: no
outside human has ever been contacted, and the standing dispatch is unsent and held as
possibly ill-posed.

## 6 · The genuine asset, reported honestly

The record **does** contain a machine-frozen **cubic EH TT-TT-TT graviton vertex on dS**
(26,032 terms, `WALL_KR_TIER1_VERTEX_ARTIFACT.json`, sha256 `0152c777…`) and a one-loop
retarded TT self-energy built from it. That is real interacting-graviton content and the gate
does not deflate it. It is nevertheless certified only for ω ≫ H and refused at ω ≪ H, so it
is an asset **pointing away from** the zero mode, not a starting point for this bridge.

## 7 · The minimum admissible bridge (derived from the reconstruction, not assumed)

Given B1–B7, the smallest theorem-shaped target that could actually discharge the question is
**not** a stochastic reduction. It is upstream of one:

> **Exhibit the interacting TT graviton zero-mode dynamics as a defined object at ω → 0 on a
> declared background — i.e. supply arrow 4 — together with the licence, the method
> non-perturbative in H, and the proved stationary reduction that ROOT-1 names as the three
> categorically distinct missing pieces.**

Only after that does "reduce it to an SY-class equation" become a well-posed request. Any
attempt to write the stochastic equation first would be supplying arrows 5–11 by assumption.

## 8 · Falsifiers of this gate's verdict

The BLOCKED verdict is overturned by any one of: an interacting TT zero-mode equation exhibited
in the record (falsifies B1); a licensed extension of the Tier-4 evaluator below ε_H = 1
(B2/B3); a derivation of the system/bath split from GRUT primitives, or a demonstration that
the one-sided inclusion suffices for the reduction (B4); a derived dimensionless graviton
self-coupling (B5); a derived or controlled Markov limit with a single rate for the graviton
(B6); or a licensed frame in which KMS holds for the cosmological slicing (B7). **Each is
externally decidable and none requires trusting this gate.**

## 9 · Decision tree — written here explicitly, and the routing

*This tree is **this gate's own design-time routing**, written into the document as the Q1
gate does. It is not quoted from a prior frozen artifact.* Its three outcomes and the
primitive clause follow the ordering instruction that opened this gate.

- **A · DERIVATION AVAILABLE** — every essential arrow is supported by existing declared
  structure and current capabilities → design a mathematical derivation workflow; **no
  computation yet.**
- **B · CONDITIONAL DERIVATION** — a bridge exists only after explicitly named assumptions →
  enumerate them, test them against the charter, **do not execute without separate
  authorization**, and **do not call the result GRUT-derived**.
- **C · BRIDGE BLOCKED** — one or more essential arrows require frontier-reserved mathematics,
  an underived split, a new primitive, or an unresolved physical input → record the blocker,
  **manufacture no substitute**, and name what would remove it.
- **NEW PRIMITIVE REQUIRED** — stop and classify as a primitive-generation question; **do not
  introduce it under Q2-BRIDGE.**

**Route taken: C — BRIDGE BLOCKED.** Blockers B1–B7 above; no substitute is manufactured;
§7–§8 state what would remove them. **No primitive is introduced here.**

**Q2-BRIDGE disposition: OPEN → GATED** (design gate built and rendered), matching the Q1
precedent under this ledger's semantics, where OPEN means *on the table, not yet
investigated*. It is **not ON** (nothing licensed it) and **not OFF** (OFF means evaluated
and set aside, and §8's falsifiers are live external routes). *This gate does not edit the
ledger; the disposition change is for the owner to apply.* **No computation is authorized.
Reopening key #1 remains NOT discharged.**

**A BLOCKED result is a first-class outcome of this program**, obtained for the cost of a
record reconstruction rather than a derivation attempt that could not have succeeded.

## 10 · Disclosed defects in this gate's first draft

Both audits failed the first draft; the **verdict C survived** the hostile refuter, which
could build no route to B on any of six probed axes and confirmed the gate clean on smuggling
(no hidden split, state, Markov limit, coupling, scale or renormalization condition; no use of
the 0.034H/0.0333H historical values; the influence-functional form correctly refused as GRUT
content; §7's minimum target genuinely derived from ROOT-1 §3). **But the draft blocked on
wrong or forbidden grounds where correct and stronger ones sat in the record**, and those are
repaired above:

1. **B4 resurrected a withdrawn argument.** It made "canonical tensor split impossible in
   type III₁" load-bearing, four days after `WALL_KR_U3_SCALE_SPLIT_CORRECTION.md` (2026-09-03)
   withdrew its relevance, and asserted the *opposite* of that file's settled finding by
   calling the partition "diagrammatic, not a scale split." **GRUT's split is scale/mode.**
   B4 now blocks on the split being *declared rather than derived*, with no declared window.
2. **B4 pre-answered a fenced question.** It called `u3_split_origin` "machine-checked as
   underivable" — a token that appears nowhere in the record. The machine-checked fact is that
   u3 is a **graph isolate** (absence of an edge, not a proof), the instrument recorded
   **UNDETERMINED**, and the node is **fenced against pre-answering in either direction**.
   Corrected, and no underivability is claimed.
3. **B7 over-counted a negative in the exact way the record forbids.** It used the FDT/KMS
   scale-blindness as a positive obstruction; `NO_GO_LEDGER.md` states that mechanism and, in
   its own boldface, calls it *"a supporting mechanism (not a fourth obstruction — do not
   over-count the negative)."* Leg withdrawn; B7 now rests on the frame-migration retraction's
   on-point findings (no TT decomposition on a slice with boundary; no decaying quasinormal
   mode at all), which are stronger.
4. **A phantom decision tree.** The draft quoted "the frozen tree" for text that came from the
   ordering instruction, not from any repo artifact — the self-certification shape. The tree is
   now written into this document explicitly as its own routing.
5. **An overreaching "record finding."** "m_eff² = 0.1H² has no calc anywhere — prose-only" is
   refuted by grep; narrowed to the true and still-sufficient claim that **no calculation
   derives it for the graviton**.
6. **Minors:** the arrow map flatly marked arrows 4–6 NOT_PRESENT, contradicting this gate's
   own §6 and the banked `kr_contract_retarded_tier4` (interacting TT dynamics *is* written
   down at ω ≫ H); the λ_grav file count omitted this gate's own occurrences; the disposition
   said OPEN where the ledger's semantics give GATED; "the No-Rescue Rule" was cited as a
   registered proper noun when no rule of that name exists; and the capability table's
   "spectral gap — available in-house" was an undisclosed use of Q2-SY material, now disclosed.
