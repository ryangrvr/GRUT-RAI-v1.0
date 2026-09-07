# RAI CAPABILITIES — an evidence-based assessment

> **2026-09-07 · W-0 (computed-and-reported, not banked).** Input to the Reality Program
> decision: what the RAI infrastructure has *demonstrated*, what rulebook it has developed,
> and what it demonstrably cannot do or has never done. Compiled from a three-sweep
> read-only inventory of this repository (workflow `wf_1d380ccc-056`: 29 instrument items,
> 25 method assets, 20 limitations; evidence paths verified by the sweep agents). The
> frozen record is preserved separately (`FROZEN 9:6` duplicate; tags `zenodo-v1.0`,
> `v5.0-program-record`); nothing here amends it.

## 1 · The central finding

RAI's demonstrated core competence is **adversarial verification and adjudication under
pre-registered discipline** — not physics generation. Its single most portable asset is
already domain-decoupled: `provenance/auditor.py` audits *any* claim set for tiering,
sourcing, falsifiability, and anti-laundering, by design independent of GRUT content.
The infrastructure is closer to a general research-auditing engine than to a
GRUT-specific tool. That is exactly the right shape for the program the owner described:
*"the machine that helps us prevent ourselves from fooling ourselves while we find out."*

## 2 · Demonstrated capability classes (with representative evidence)

1. **Adversarial multi-agent campaigns** — blind primary + hostile leg launched in
   parallel (blindness structural), commit gated on cross-lineage convergence
   (`RAI_STRUCTURAL_THEORY_SEARCH.md`: 36-agent primary vs 4-agent blind hostile;
   `RAI_GRUT_RESURRECTION.md`: primary == hostile before recording).
2. **De-pinned executable gate instruments** — verdicts flow journal → record; gates
   assert well-formedness and record/source consistency via dynamic needles, never which
   verdict passes (the five `rai_*.py` batteries; the standard exists because the
   pass-label defect recurred 11+ recorded times).
3. **Spec-first computation** — outcomes enumerated and sealed before any result exists,
   REFUSE a first-class terminal state, the verdict computed at runtime from live state
   (`calc/SPEC_gw_tensor_friction.md` → `gw_tensor_friction.py` → RESULTS: end-to-end
   demonstrated).
4. **Design gates** — a pre-computation review that decides whether a proposed calculation
   can even discriminate, from input *statuses* alone, before the calculation is paid for
   (`GRUT_PREDICTION_GATE_GAMMA_T.md`, the 11-step protocol + five-outcome tree).
5. **Register machine-audit and change control** — the portable auditor engine +
   `validate.py`; `bankgate.py`/`resident.py` three-state change control on register
   mutations; mutation batteries required before any number banks
   (`provenance/mutation_registry.py`: "no number banks without one"); machine-emitted
   status documents and prose-to-register pins as anti-drift.
6. **Negative-result auditing** — the N1–N10 standard built on the asymmetry that a null
   is the generic output of a broken instrument; plants that must detect; displaced-gate
   mutation tests that separated a shipped bug from the correct physics
   (`RAI_GORILLA_T1.md`: 22.05 vs 2.98 at t=1).
7. **Independent verification** — second-author blind re-derivation with calibration
   gates; retraction by recomputation with the defective artifact preserved unpatched;
   read-only cross-workstream audits that touch neither repository
   (`CROSS_WORKSTREAM_RRT0_RAI_AUDIT.md`).
8. **Campaign architecture at scale** — the WALL_KR contract machine (66 instruments,
   ~130 verdict artifacts, 110 preserved run logs; tier ladder, frozen inputs by hash,
   sealed comparators); adversarially-gated *target selection* that withdrew its own
   choices (the FOREST phases); escalation instruments that package process deviations
   for owner adjudication rather than self-exonerating.
9. **Corpus and publication production under vocabulary control** — ten independently
   drafted books held to zero cross-book status drift by a canonical status table;
   publishing passes provably substance-free (pure-insertion diffs); versioned release
   manifests with per-file integrity.

## 3 · The portable rulebook (method assets, domain-independent)

Governance forms: tier-every-claim + anti-laundering as code; adversarial pre-screen with
the directional-optimism rule (scrutiny scales with how much we want the result);
outcomes-first stopping rules with externally-decidable reopening keys; W-0 two-stage
endorsement; preserve-the-failure; the CLAIM/LOG coordination protocol ("give the check,
not the conclusion"). Instrument standards: the SPEC form; the de-pinned standard; the
declared-conventions block; N1–N10. Verification patterns: plants that must detect;
mutation batteries with the executed-at-least-once ledger; check-the-reference (every
oracle carries provenance); declared-red as a third CI state; derived-artifact sync
(counts emitted, never typed); committed-manifest enumeration. Vocabulary devices: the
controlled status vocabulary + canonical table; the NOT-banked fence with a named
gate-to-readmit; attribution fences + the match-temptation rule.

## 4 · Limitations, three kinds, stated plainly

**Demonstrated failure modes** (each with its codified answer): the pass-label pattern
(11+ occurrences → the de-pinned standard); self-certification (→ hash-freeze the
certifier outside the certified); the asymmetric error budget — negatives went unverified
for months (→ N1–N10); a wrong-signed flagship negative whose bug survived every gate
(→ displaced-gate mutation testing); an uncalibrated sorter producing frame-entailed
nulls (→ calibrate on paradigm positives first); external-classifier dependency (the
wiesbrock:attack stage, 3 refusals, never bypassed → record-then-substitute coverage);
long-run cost fragility (→ checkpoint/cache discipline); the breadcrumb pattern — the
apparatus partly manufactured its own trail of missing ingredients (→ the stopping rule).

**In-principle limits:** the frontier-reserved sectors the record itself fences
(bath-microphysics/transport Σ; the dS trace/conformal sector; rung3's pole-vs-cut —
in-house approximation of these is an automatic fail); the ω ≲ 3.4H regime UNASKABLE at
current declarations; and the one-sided-apparatus clause — this method can verify claims
against a corpus, never establish universal negatives.

**Undeveloped capabilities** (the honest gap list): **no stochastic/Monte-Carlo
simulation instrument class exists**; **no laboratory or observational-data interface**
(all empirical contact is literature citation); **no external-referee integration**
(campaign-own derivations await anyone independent); decisive tests posed but never run.

## 5 · Fit against the four candidate directions

| direction | served by existing capability | must be BUILT |
|---|---|---|
| Q1 USL/tabletop | design gate (class 4), SPEC form, negative controls | an analogue-system modeling layer + eventually a data interface |
| Q2 stochastic KMS dynamics | spec-first + mutation batteries + plants transfer directly to numerics | **the stochastic instrument class itself** (discretization, convergence, ensemble controls) |
| Q3 dimensional transmutation | design gate; the bridge test (derive vs relocate); register pricing | nothing new until the gate's inventory question is answered |
| Q4 EFT hierarchy | theorem-campaign machinery (H1-style); the closure discipline | a power-counting formalization; no rewrite of standing verdicts |

## 6 · Verdict

**A coherent program is supportable.** The demonstrated shape: RAI audits, the new
program generates, and the bridge between them — the design gate that decides whether a
question can even discriminate before it is paid for — is the one piece already proven
end to end. The two capability gaps that gate the ranked directions (a stochastic
instrument class; an analogue/data modeling layer) are buildable *inside* the existing
discipline: every rule in §3 applies to a simulation exactly as to a markdown gate.
