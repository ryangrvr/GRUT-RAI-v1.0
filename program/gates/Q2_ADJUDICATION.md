# Q2 ADJUDICATION — against the frozen §18 decision tree

> **2026-09-07 · ADJUDICATION ONLY.** No simulation was run for this document. The Q2
> execution record (`78452bd`, run at freeze point `eba9991`) and its raw outputs are not
> modified. Q1, the register, the frozen corpus and every historical record are untouched.
> **Three token families appear below and are kept distinct:** *claim status* (DERIVED /
> RECOVERED / ASSUMPTION / HYPOTHESIS / UNRESOLVED / CLOSED / UNMAPPED / REVERSED, defined in
> `books/CORPUS_CHARTER.md`); *investigation disposition* (OPEN / GATED / ON / OFF /
> ANSWERED, defined in `program/QUESTION_LEDGER.md`); and *parameter/provenance class*
> (INHERITED / STRUCTURAL_SELECTION / EMPIRICAL_INPUT …, defined in prereg §5). No new
> vocabulary is introduced. **This document was revised after an adversarial leakage check
> found two blocking defects in its first draft; both are disclosed in §10.**

## 0 · THE PREREGISTERED MEANING OF THIS OUTCOME — quoted first, before any grading

Prereg §19–22, frozen before execution, verbatim:

> **An advance:** a converged, control-surviving result that lands in B-(b3) — behavior not
> already supplied by the SY literature rule — or a clean, well-controlled A or J … **Null /
> inconclusive:** A with clean controls (informative), or **E/D/H (uninformative about
> physics; informative about what the question needs)**. … **What would merely motivate
> another investigation:** any of C, D, E, F, G, **H** — each names its own next step and
> **none licenses a claim**.

The run landed **B-(b1) + b2 + H**. **The preregistration therefore classifies this outcome,
in advance, as NOT an advance** — b3 was required for that — **and as uninformative about
physics, licensing no claim.** Everything below is written under that pre-commitment. The
word "success" is not used of this outcome: the emitted audit mechanically screened the
output for that very token, and the first draft of this document reintroduced it.

## 1 · Preregistered branches reached

| branch | reached? | evidence |
|---|---|---|
| A clean null | no | rate 0.009216 H ≫ tol_null |
| **B reproducible nontrivial dynamics** | **YES** | finite rate; seed spread 5.80% (emitted `CONVERGED`); controls below |
| — sub-classification | **b1 AND b2** | §2 |
| C numerical artifact | **excluded for the primary route by C10 only** | C10 ensemble ladder on `ac_rate`, last step 4.13%, inside tol_converge 0.25. **C4 (timestep) records only the demoted O1b route** — see §1.1 |
| D parameter-sensitive | **partially excluded** | φ₀ limb excluded by C6 (1.3176 / 1.3163 / 1.3146). **λ limb NOT tested by any control** — see §1.1 |
| E nonconvergent | no | ladders inside tol_converge (computed here from the emitted ladders) |
| F control reproduces the phenomenon | no | C3 null: primary-ac 0.000248 ≤ tol_null 0.002 — primary NOT voided |
| G phenomenon disappears under a preserving control | no | C1 0.0333389 vs analytic 0.0333333; C2 +1.7%; C8 planted exact gap 0.100000 → 0.101655 (1.65%) |
| **H unresolved input dominates** | **YES** | §2 |
| I-a target A reproduced | no | deviation 0.724 → emitted `NOT_OBSERVED` |
| **I-b target B reproduced** | **YES** | deviation 0.041 → emitted `OBSERVED` |
| J neither target | no | — |

*`CONVERGED` / `OBSERVED` / `NOT_OBSERVED` above are quoted only where the instrument
actually emitted them. The instrument emitted `CONVERGED` exactly once — for seed stability.
The ladder comparisons are the adjudicator's arithmetic against tol_converge, not emitted
labels.*

### 1.1 · Two residual coverage gaps, recorded rather than glossed

**(i) Branch C is excluded for the primary estimator by C10 alone.** `q2_controls.py`
`control_C4_timestep` records `_rate_from(...)["rate"]` — the **demoted O1b** route — so the
primary estimator's timestep-independence was never measured. The prereg §2.4(a) repair list
was "C3, C5, C8 and C10"; C4 was not in it, and the auditor's coverage check names the same
four. **The primary route's dt-independence is therefore an untested residual.**

**(ii) Branch D's λ limb was never controlled.** §18 D reads "moves qualitatively under φ₀
(C6) **or λ perturbation**." No λ-perturbation control exists in C1–C11. The φ₀ limb is
cleanly excluded; the λ limb is not excluded by any control — and §2 asserts the outcome
*does* move with λ, which is why H is reached. The λ limb is absorbed into H, not refuted.

## 2 · Why b1, b2, and H

**b1 — "already supplied by the declared equations."** The pre-execution Fokker–Planck solve
of the *same* equation predicted Λ₁ = 0.008892 and predicted the frozen estimator would
return 0.008951; the run returned 0.009216 (+3.6% and +3.0%, inside the 7–11% scatter C11
measured beforehand). **No structure appeared that was not already visible analytically.**
b3 is therefore not reached.

**b2 — "dependent on the unresolved inputs."** Also reached, on a different axis: b1 grades
*structure* (nothing new appeared), b2 grades *value* (the number is set by an unresolved
input). The first draft claimed b1 alone while asserting b2's content in prose.

**H — "unresolved input dominates."** Both targets scale as √λ, and λ = 0.01 is a
**STRUCTURAL_SELECTION** made to hit the record's m_eff² = 0.1 H² referent. **H rests on U2
(λ's physical value) alone** — not on U4. *Disambiguation:* prereg §3 defines U4 as the O(1)
constant in the mass rule m²_eff ∼ √λ H², and that constant is **not an input to the
dynamics** (m²_bare = 0; the firewall confirms the live input set is {H, m²=0, λ, φ₀,
noise-rule}), so it cannot set the measured value. Prereg §2.2 uses "the O(1) coefficient"
for a *different* constant — the 0.0885 eigenvalue coefficient. The first draft conflated
them; **§3's definition is canonical here, and the label collision originates in the
preregistration itself** — recorded for the owner, not edited.

## 3 · The four-way firewall

**A · Numerical validation of the implemented dynamics — ESTABLISHED, and it is a recovery.**
Planted exact gap 0.100000 → 0.101655 (1.65%); zero-noise limit reproducing the analytic
drift to 1.7×10⁻⁴ with variance → 10⁻²⁷; λ = 0 OU limit +1.7%; stationary variance 1.3163
vs quadrature 1.3176 (**−0.10%**); noise normalization 0.14%; null control clean.
**Claim status: RECOVERED** — each is a *known answer reproduced*, which is the charter's
RECOVERED, not its DERIVED. *(Corrected during adjudication; the first draft graded this
DERIVED, using "derived" to mean merely "numerically established." The spectral calculation
is the derivation; the Monte-Carlo run recovers it.)* **The one genuinely DERIVED item in
the Q2 arc is separate:** the estimator-validity theorem — mode decomposition (Λ₁ at
98.444%), the asymptotic Λ₁ regime inside the frozen domain, and the +0.66% finite-lag bias
— exhibited and checked from the declared operator. **DERIVED (declared scope: this
operator, this λ, this lag domain); a theorem about the instrument, not about nature.**

**B · Agreement with the independently solved spectral gap — ESTABLISHED.** 0.009216 vs
Λ₁ = 0.008892 (+3.6%), inside the pre-registered scatter; the solve itself validated against
the exact OU spectrum to 0.01% with ⟨φ²⟩_eq = 1.317651 vs analytic 1.317645.
**Claim status: RECOVERED** — two independent computations of one written-down model agree.

**B′ · The O1b cross-check, reported (omitted from the first draft).** Per-seed window-0
rates 0.006964 / 0.006606 / 0.006643 / 0.006554 / 0.006539; overall mean across all three
windows ≈ 0.00741; window-to-window spread 20.1%. At the measured rate these windows span
0.32–0.55 e-folds, so **the frozen gating rule fires: O1b is `INCONCLUSIVE` and may not
invalidate O1a** — the exemption written in advance for exactly this case. O1b did **not**
independently confirm the primary; it was pre-committed to being uninformative here.

**C · The target-A-versus-B finding — ESTABLISHED, TIGHTLY SCOPED.** *For the scalar
nonlinear equation actually analyzed, the record's composition — its m²_eff ∼ √λ H² rule
with the O(1) coefficient taken as unity, fed into the free-field OU formula m²/(3H) —
yields a decay estimate ≈3.75× larger than that equation's exact spectral gap.*
**Where the error lives, localized from emitted numbers:** the free-field mass reproducing
this model's own equilibrium variance is m²_eff = 3/(8π²⟨φ²⟩) = **0.0288 H²**, and feeding
*that* into the same OU formula gives 0.00961 — only **+8.1%** above Λ₁. **The OU rate
formula is not the main error;** the discrepancy is concentrated in taking m²_eff = 1·√λ H²
= 0.100 H², which is **3.47×** the variance-matched mass. **Anti-overreach fence:** this is
**NOT** "GRUT's mass-generation rule is wrong," and must never be restated so. The scaling
relation m²_eff ∝ √λ H² **was not tested**; one *composition* of it was. **Claim status:
DERIVED (about this composition, at λ = 0.01, for this channel); the mass rule itself
UNTESTED; transfer to the graviton case UNRESOLVED.**

**D · Inference about GRUT / O2 — NONE.** The bridge was declared unresolved before
execution (§1.1, U1) and was not crossed by running the equation. Simulating an equation
cannot derive it. **UNRESOLVED, unchanged.**

## 4 · The §2.2 guard, applied literally

"Target B reproduced" means the implementation agrees with the registered spectral-gap
calculation of the equation it integrates — **instrument-and-literature agreement**. It does
**not** mean GRUT predicts 0.0089 H, that O2 is computed or supported, that the persistence
claim is settled either way, or that reopening key #1 is discharged. **Reopening key #1 of
`GRUT_PROGRAM_FREEZE.md` §5 is NOT discharged: it names the interacting *graviton*
zero-mode; this run evolved a *scalar*.**

## 5 · Classification of "I-b without I-a"

*Ruling applied (§9): the computational question answered here is registered separately as
**Q2-SY**; the original **Q2** remains GATED / NOT ANSWERED with its wording intact.*

**Completed at the computational level, and preregistered as NOT an advance** (§0). It is
not a partial answer to the GRUT question, because that question was fenced out of Q2's
scope before execution (§1.1, U1):

- **Q2-A (computational):** can the implemented nonlinear scalar SY dynamics be recovered
  numerically under a disciplined instrument, and does it match independent theory?
  → **completed affirmatively, with controls, and classified null/uninformative-about-physics
  by §19–22.**
- **Q2-B (the bridge):** is that dynamics generated by GRUT rather than supplied through the
  reopening construction? → **untouched; unresolved.**

## 6 · Provenance of the simulated dynamics (**parameter/provenance class**, not claim status)

| element | provenance class |
|---|---|
| Langevin equation and 1/(3H) drift | **INHERITED** (verbatim from `calc/two_scale_desitter.py`) |
| Gibbons–Hawking noise H/2π | **RECOVERED-generic** (corpus term; horizon-forced) |
| m²_eff ∼ √λ H² (SY dynamical mass) | **RECOVERED** (literature) |
| λ = 0.01 | **STRUCTURAL_SELECTION** (chosen to hit the record's referent; U2) |
| a light self-coupled scalar IR vacuum mode | **ASSUMPTION** (U3 — *"the horizon supplies the noise and the tracking; it does not supply the mode or its coupling"*) |
| scalar ↔ graviton-zero-mode correspondence | **UNRESOLVED** (U1) |
| **derived from the GRUT construction?** | **NO** |

## 7 · What would convert this into evidence about O2

A **derivation**, then a computation downstream of it: (1) a stochastic reduction for the
interacting TT graviton zero-mode on de Sitter, with effective potential and noise *computed*
rather than posited; (2) a **derived** λ_grav — since everything scales as √λ, a selected λ
makes the value uninformative (branch H); (3) a demonstration that "lifted vs protected" is
decided by that equation's spectral gap. **Standing obstruction:** (1) and (2) live in the
record's **frontier-reserved** sectors, where in-house resolution is an automatic fail under
`CHARTER.md` §3. **No in-house computation is proposed.**

## 8 · Is there a next computation following from a registered unresolved question?

**Identified, not executed, not recommended:** only U2 (λ's physical value) and U1 (the
bridge) are Q2-adjacent, and both are derivational or frontier-reserved, not numerical.
**No new simulation is proposed.** *(The two coverage gaps in §1.1 are recorded as
limitations of this run, not as a licence for a re-run.)*

## 9 · Statuses

**Claim statuses** (register untouched; nothing banks):
- Instrument fidelity (planted gap, analytic limits, quadrature) → **RECOVERED**.
- Estimator-validity theorem → **DERIVED** (declared scope).
- Simulation/spectral agreement on the written-down equation → **RECOVERED**.
- "At λ = 0.01, the unit-coefficient mass rule composed with the free-field OU formula
  overstates this scalar model's gap by ≈3.75×, localized to the mass normalization (3.47×)
  rather than the rate formula (8.1%)" → **DERIVED**, scoped. **Mass rule itself: UNTESTED.**
- GRUT / O2 / reopening key #1 → **UNRESOLVED, unchanged.**

**Investigation disposition — OWNER RULING 2026-09-07, applied.**

The ledger's boxed Q2 question reads, verbatim:

> *"Do the **legitimately specified GRUT constitutive equations**, evolved numerically as a
> stochastic realization, exhibit structure (fixed points, spectra, response) not visible
> analytically — under a numerical instrument that itself passes the house discipline?"*

**That question, as written, was not answered.** Its subject — GRUT constitutive equations —
was never available; §1.1 substituted the scalar SY channel **before execution**, and §6
grades those dynamics INHERITED / STRUCTURAL_SELECTION / ASSUMPTION with "derived from the
GRUT construction? **NO**."

**The owner ruled against re-wording it.** Re-wording a registered question after seeing the
result is post-hoc question substitution, and the run cannot retrospectively be made an answer
to the original question by editing the question. Accordingly, applied to the ledger:

- **Q2 — original GRUT question: wording PRESERVED VERBATIM; disposition token **GATED**
  (with the ruling's clarifying gloss *"not answered"*; the declared five-token set is
  unchanged).** The scalar-SY execution — however cleanly it ran — **may not be used to discharge it.** Q2 is
  **not "failed"**: the original question is unanswered, the child question is answered, and
  the run was technically valid — three distinct facts.
- **Q2-SY — new post-execution child entry (provenance recorded as spawned from Q2 after
  execution): ANSWERED.** It holds the question the run actually answered.
- **Q2-BRIDGE — new entry: OPEN**, inheriting no disposition from either, with §7 as its gate
  question.

**No registered scientific advance occurred under the Q2 preregistered decision rule** (§0:
b3 was required; H is preregistered as uninformative about physics). The findings in §3
stand as findings; they do not meet the criterion set beforehand for advancing the GRUT
question. **Q2 does not become ON, and I-b licenses no further GRUT-directed computation.**
*(The first draft of this document proposed re-wording the ledger question; that proposal is
withdrawn — the owner ruled the other way, and correctly.)*

## 10 · Disclosed defects in this document's first draft

Found by an adversarial leakage check and repaired here, per the program's disclosure rule:
**(blocking 1)** the first draft never cited §19–22, called the outcome a "successful
completion," and reintroduced the token "success" that the emitted audit had mechanically
screened out — framing as an achievement what the preregistration had already classified as
*not an advance* and *uninformative about physics*; **(blocking 2)** it silently requoted the
ledger's boxed question, dropping "GRUT constitutive equations," which would have let a
"Q2 ANSWERED" mark read as a claim about GRUT. **(minors)** branch D's λ limb asserted as
control-excluded when no λ control exists; branch C asserted from C4, which covers only the
demoted route; b2 omitted; U4 used in two incompatible senses; a sign error (C9 is −0.10%,
not +0.1%); the emitted-label token `CONVERGED` attached to the adjudicator's own arithmetic;
the §6 column headed "status" while carrying provenance classes; and the O1b route omitted
entirely.
