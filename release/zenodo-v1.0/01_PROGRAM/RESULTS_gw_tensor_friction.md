# RESULTS — `calc/gw_tensor_friction.py` (the closure computation)

> **2026-09-06.** Built to `calc/SPEC_gw_tensor_friction.md` (2026-08-22, unmodified) under
> `GRUT_PREDICTION_GATE_GAMMA_T.md` (commit 2116251), which found the design does not
> survive as a prediction hunt and priced this file as a **closure, not a prediction**.
> Owner authorization 2026-09-06 is recorded in this file's landing commit message
> (the gate doc had reserved the closure as "available but NOT run — owner's call"). Verdicts below are **computed by the script from statuses
> extracted out of `provenance/claims.json` and `PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md`
> at runtime** (the de-pinned standard); nothing banks; the register is read-only to this
> work and untouched (74 nodes, sha256 beaeb84e8a6f8468).

## SPEC §5 OUTCOME: **REFUSE** — with the obstruction named

**(Q-A), which the SPEC says dominates everything else, cannot be settled from the booked
family.** Extracted adjudications: `p_tt_ansatz` = **CHOSEN** (tier assumed; five-angle
interrogation, unanimous); `eft_operator_basis` = **CHOSEN** at the enumerated frame/order
(tier to-derive). Every booked level books the channel assignment as a projector **choice**;
the SPEC's two horns disagree; nothing booked selects between them. The REFUSE clause of
SPEC §5 applies verbatim. The named obstruction stack: (i) p_tt CHOSEN, (ii) frame-level
CHOSEN, (iii) τ₂ INSERTED un-sourced (`rung7_wz`, +2 of +3) — so horn (b) is
FAIL-BUT-INFORMATIVE-shaped before Q-A is even reached, and (iv) the pole's region
ω ≲ 3.4H is **UNASKABLE** (ROOT-1 §3, O1–O4) — the derivation that would settle Q-A
cannot currently be posed.

## The pre-registered register question, answered

*"Does the local memory scale connect parameter-free, or does the bridge need a new
inserted scale?"* — **NO parameter-free connection exists on the licensed record.** The
only parameter-free entry into the Γ_T slot is the Tier-4 derived kernel's

    Γ_T(ω) = (3/1280π)·(ω³/M̄_P²)·[1 + (104/9)(H₀/ω)²]      (chromatic ∝ ω³;
    Im L = π ⇒ μ-independent — no scheme slot enters the friction)

| f | Γ_T (s⁻¹) | Γ_T/H₀ |
|---|---|---|
| 10 Hz | 1.352e-83 | 6.19e-66 |
| 100 Hz | 1.352e-80 | 6.19e-63 |
| 1024 Hz | 1.452e-77 | 6.65e-60 |

**62.7 orders below the shared-slot bound few×H₀ at 100 Hz** (arXiv:2507.03103), with the
H² correction term ~1e-40 (below double precision) and 8π-class convention slop (~1.4
orders) irrelevant against the margin. This is the NO EFFECT routing of the gate's
decision tree, now **computed, not foreseen** — and since horn (a) has no free parameter,
it is final at these declarations. Every observable-sized route runs through
inserted/staked/choice-dependent inputs.

## Conditional exhibits (labelled; NOT banked; no headline)

Horn (b) achromatic limit Γ_T → B·H₀/2, siren-amplitude channel (SPEC Q-D; dephasing NOT
re-derived), Ξ(z)=d_L^GW/d_L^EM, H₀·t_lookback(0.5)=0.3597, flat ΛCDM Ωm=0.31:

| B (status) | Γ_T | Ξ(z=0.5) − 1 |
|---|---|---|
| 0.4 (staked) | 0.20·H₀ | 3.7e-2 |
| ~2.4e-4 (conformalon leg) | 1.2e-4·H₀ | 2.2e-5 |

**The SPEC's owed composition:** the two live B values differ by 3.2 orders and nothing on
the record selects between them — the induced effect spans "percent-level at z~0.5" to
"invisible" across one staked constant. **Match-temptation fence applied (SPEC trap 4):**
B=0.4 landing inside the slot bound is a staked amplitude near a *shared*-slot bound —
evidential weight zero. **(Q-C):** the B ≡ ε identification is carried
UNVERIFIED and no computation uses it; B = 0.4 is quoted per the SPEC's own Q-B booking of
the staked value (the transfer is the SPEC's, not a fresh identification here).

**ω_c sensitivity (SPEC §4):** crossover ω_× = √(B·H₀·ω_c/A), A=1 declared: 9.8e-9 Hz /
22.0 Hz / 0.64 THz across the three in-corpus ω_c (19.8-order span) — an unpinned constant;
enters no headline. *Cross-check against the SPEC's own quoted pair (trap 2):* the Planck
value reproduces the prior pass's **0.64 THz exactly**; the hand-set value gives 22 Hz where
a prior pass reported 10 Hz (same order; an O(2) input convention in that pass, not ours to
reconstruct) — the ~10-order sensitivity conclusion is identical either way.

## Standing consequences

- `SIGNATURE_AUDIT.md`'s **gate-to-readmit is closed as a computed refusal** — the ≤1e-21
  figures stay un-readmitted; no number banks.
- **EDIT 1's conditional marker is NOT finalised** (that required a scalar-only Q-A answer;
  this REFUSE is not one).
- `claims.json`, the TT quarantine, the Class-A suspension, and the 22–62-order dephasing
  statements: untouched (SPEC §7 honored).
- Under the program freeze's stop rule, with the Γ_T candidate now closed by computation:
  **no discriminator identified on the current record.** Remaining candidates (USL shape,
  rung8 bookkeeping) each require their own gate before any computation.

## Adversarial verification (pre-commit, 2026-09-06, three independent checkers)

- **Arithmetic (PASS):** from-scratch independent recomputation (own constants, own
  integrator) reproduced every table value to the printed digits — Γ_T at all three
  frequencies, the 62.7-order margin, H₀·t_lb(0.5) = 0.3597, both Ξ values, all three
  crossovers, the 19.8-order span, and the exact 104/9 identity.
- **SPEC compliance (PASS, four minors fixed pre-commit):** the caught-and-fixed defects,
  disclosed per house rule: (1) a margin *gate* that hard-failed unless the result landed
  ≥50 orders below the bound — **the pass-label pattern in miniature, caught pre-commit**;
  now a report-never-gate branch; (2) the REFUSE obstruction stack was a static narrative —
  now assembled from the runtime-extracted flags; (3) the counterfactual settled-sector
  branch emitted a label outside the SPEC outcome space — now fails forward loudly ("new
  run required", no outcome emitted); (4) the Tier-4 coefficients are now
  extraction-checked verbatim against `kr_contract_retarded_tier4` at runtime. Trap-1/-3
  dispositions added to the script's face.
- **Hostile refutation of the REFUSE (SURVIVES):** exhaustive search of all 74 nodes found
  **no FORCED verdict anywhere in the register**. Three nearest misses, each failing on the
  register's own face: the noise-transversality derivation (transversality does not force
  tracelessness — "P^(0s) remains admissible, the TT restriction remains CHOSEN");
  `response_lorentz_covariance` (TT-scoped at the vertex, "c0 = 0 remains separately
  unlicensed", validity ω ≫ H — it *corroborates* obstruction (iv)); the rung9b a/c
  anomaly sector-split (assigns anomaly counterterms at k⁴, not the τ₂ pole). Obstructions
  (i)–(iii) satisfy the REFUSE clause even with (iv) struck.

— *Executed by Claude (builder), 2026-09-06; script exit 0, all gates passed (gates assert
well-formedness, arithmetic identities, and extraction success only — no gate asserts which
verdict passes, and magnitude findings are reported, never gated).*
