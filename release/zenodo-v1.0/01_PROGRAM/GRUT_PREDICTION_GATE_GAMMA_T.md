# GRUT PREDICTION GATE — Γ_T (design/analysis; no calculation performed)

> **2026-09-06. Owner-ordered gate, executed design-first per the eleven-step protocol.**
> Constraints in force: no new theory, no new kernel, no new scale, no rescue parameter,
> no RRT. Register untouched (74 nodes, sha256 beaeb84e8a6f8468). This document sits ABOVE
> `calc/SPEC_gw_tensor_friction.md` (2026-08-22), which remains the calc-level
> pre-registration and is not superseded; where this gate reaches a routing the SPEC already
> pre-registered, the SPEC's clause is cited. **Every verdict-shaped statement below that
> precedes a computation is derived from the *statuses* of register inputs, not from values
> — nothing here evaluates the physics.**
>
> **Wording rule (owner correction, adopted):** Γ_T is **the currently identified
> candidate** for a nontrivial cross-sector consequence — not "the only place such a thing
> could live." Nothing forces the discriminator to live here; this gate adjudicates this
> candidate only.

## 0 · Sources read for this gate (steps 1–2)

`GRUT_MODEL_FRAMEWORK.md` §§3–6 (constitutive family; KMS/FDT lock; Tier-4 kernel; the Γ_T
slot); `calc/SPEC_gw_tensor_friction.md` (Q-A–Q-D; four pre-registered outcomes); 
`SIGNATURE_AUDIT.md` items 4–5 + the NOT-banked fence (α_M category distinction; the SCDP
anchor arXiv:2507.03103; the gate-to-readmit); `provenance/claims.json` nodes
`rung2_kms_gate` (KMS lock; T_dS = H/2π forced; the (ε,τ₂)-restriction booked +1),
`rung3_single_pole` (pole-vs-cut OPEN; Σ frontier-reserved), `rung7_wz` (+3; τ₂ = +2 of it;
sourced prediction w = −1 flat), `rung7_w1/w2/w3`; `calc/wz_dark_energy.py:18-25,61`
(ε staked; ω_c hand-set); `RUNG3_KEYSTONE_MAP.md` §7 (bridge test: derive vs relocate), §9;
`calc/gw_dissipation_bounds.py` (the dephasing channel; "real-but-tiny" framing);
`PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md` §3 (obstructions O1–O4; refusal boundary
ω = 3.3993H derived; standing guard), §4 (cut, not pole);
`PHYSICS_LEDGER/WALL_KR_CONTRACT_BENCHMARK_VERDICT.md` (validity terminates at ω ~ H).

## 1 · What Γ_T is supposed to connect (step 3)

One slot, three registers of the program:

1. **The equilibrium TT dissipation kernel** (gravity sector): the derived Tier-4 Im K_R —
   and/or the booked two-scale ansatz χ(ω).
2. **The KMS/FDT lock** (rung2): whatever friction exists must arrive with a stochastic
   companion at the coth(ω/2T_dS) ratio, T_dS = H/2π.
3. **Cosmological tensor propagation** (rung7's clock and background): the friction slot in
   the TT wave equation, where the SCDP open EFT (arXiv:2507.03103) has parameterized the
   same object class and where the only measured statement exists:
   |Γ_T| ≲ few × H₀ **on the shared slot**.

The pre-registered question (unchanged from the register): *does the local memory scale
connect to the cosmological friction parameter-free, or does the bridge need a new inserted
scale?*

## 2 · The GRUT equation, written before any calculation (step 4)

Single FRW cosmic clock (SPEC §4 / keystone C5 — inherited, mandatory), per TT
polarization, sub-horizon ω ≫ H, frequency domain:

    M_P² [ ḧ + (3H + Γ_T(ω)) ḣ + (k²/a²) h ] = ξ(t)
    ⟨ξξ⟩(ω) = N(ω) = coth(ω/2T_dS) · |Im K_R(ω)|        (mandatory companion, rung2)

GRUT's constitutive entry, with the two kernel candidates the record actually contains:

**Horn (a) — the DERIVED kernel** (Tier-4, flat contract scope, ω ≫ H):

    |Im K_R(ω)| = (3/1280π) ω⁴ · [ 1 + (104/9) H²/ω² ]
    Γ_T⁽ᵃ⁾(ω)  ~  |Im K_R|/(M_P² ω)  =  (3/1280π) (ω³/M_P²) [ 1 + (104/9) H²/ω² ]

  — **chromatic** (∝ ω³), parameter-free given the μ-slot, sign fixed by passivity.
  (Exact normalization — factor placement of M_P², factors of 2 — is pinned against the
  SCDP definitions at calculation time; the parametrics above are convention-independent.)

**Horn (b) — the BOOKED two-scale ansatz** (`wz_dark_energy.py`, register rung7):

    χ(ω) = A/(1 − iωτ_c) + B/(1 − iωτ₂),   τ₂ ~ 1/H₀
    Γ_T⁽ᵇ⁾(ω) = (ω/2)·Im χ(ω)  →  B·H₀/2   (achromatic for ωτ₂ ≫ 1; SPEC §1)

## 3 · The GR/EFT baseline (step 5)

- **GR:** Γ_T = 0, ξ = 0; friction is 3H only.
- **Modified gravity (α_M / running Planck mass):** friction (3 + α_M)H·ḣ, from a
  **Hermitian action** — removable by field redefinition, graviton-number-conserving,
  sign-indefinite, achromatic, **noiseless** (SIGNATURE_AUDIT item 4, verbatim category
  fence). Slot-degenerate with Γ_T in the mean-field equation only.
- **SCDP open EFT:** Γ_T a free parameter, ξ mandatory, effective-Markovian (achromatic);
  the measured |Γ_T| ≲ few × H₀ is a **no-cancellation bound on the shared slot, not a
  decomposed measurement of GRUT's kernel**.

## 4 · Every GRUT input entering the calculation, with status (step 6)

| # | input | status | source |
|---|-------|--------|--------|
| 1 | influence-functional form | GENERIC (u1) — **no credit for the form** | Feynman–Vernon |
| 2 | Ward-surviving projector pair | DERIVED at declared scope | S_IF contract |
| 3 | sector assignment: `p_tt_ansatz` vs `operator_basis` family | **CHOSEN** (its own boundary_condition) — the Q-A fork | register |
| 4 | Tier-4 kernel coefficients 3/1280π², 13/480π² | DERIVED (flat scope, ω ≫ H; μ-slot open) | K_R contract |
| 5 | KMS lock + T_dS = H/2π | borrowed standard + declared equilibrium | rung2 |
| 6 | τ₂ ~ 1/H₀ | **INSERTED, un-sourced** (+2 of rung7's +3) | rung7_wz |
| 7 | B | **STAKED illustrative**; two live values 3.2 orders apart (0.4 vs ~2.4e-4) | SPEC Q-B |
| 8 | B ≡ ε identification | **UNVERIFIED** | SPEC Q-C |
| 9 | ω_c | **UNPINNED** across 39.6 orders; crossover moves ~10 orders | SPEC §4 |
| 10 | single FRW clock | declared (C5 obligation) | keystone map |
| 11 | flat-ΛCDM background E(z) | standard empirical input | — |
| 12 | slot bound few × H₀ | EMPIRICAL-INPUT, external, shared-slot | arXiv:2507.03103 |

## 5 · Fixed versus free (step 7)

**Genuinely fixed:** the Tier-4 coefficients and their exact ratio 104/9; T_dS = H/2π
(given the equilibrium declaration); the noise-to-friction KMS ratio; the chromaticity
class of each horn (ω³ vs achromatic); the achromatic limit *form* B·H₀/2 **given** a τ₂
pole.

**Free or unresolved:** the sector assignment (input 3 — a choice, not a derivation); B
(staked); B ≡ ε (unverified); τ₂ (inserted); ω_c (unpinned); the μ-slot locals.

**The structural fact this table exposes:** every quantity that is fixed lives in horn (a);
every quantity that could make Γ_T observable lives in horn (b) and is unresolved. The two
horns do not mix: no fixed coefficient feeds the observable-sized number, and no
observable-sized number is fixed.

## 6 · Licensed frequency/IR domain (step 8)

- **The wave:** ground-based band ω/H₀ ~ 10²⁰ — evaluation frequency deep in ω ≫ H.
  In-domain for horn (a) everywhere relevant.
- **Horn (a)'s kernel support:** entirely at ω ≫ H. Fully licensed; refusal boundary
  ω = 3.3993H (ROOT-1 O1, derived not declared) is 20 orders below the band.
- **Horn (b)'s kernel support:** the τ₂ pole is an analytic feature at |ω| ~ H₀ — inside
  the region ROOT-1 §3 established as **UNASKABLE** on four independent obstructions
  (O2: no frequency variable is defined there — ρ(ω), Im χ(ω) are not objects; O1/O3/O4).
  The high-frequency tail B·H₀/2 is the tail **of that pole**: its existence and residue
  are statements about the unaskable region. Per the owner's standing warning, no Γ_T
  evaluation may treat ω ~ H₀ as validated; the SPEC's six-decimal check of the achromatic
  limit is arithmetic ON the ansatz, not a license FOR it.

## 7 · Absorbability into existing parameters (step 9)

- **vs α_M:** NOT absorbable, by the register's own category fence — chromaticity,
  mandatory noise, passivity-fixed sign, non-removability. But the same fence cuts both
  ways: **a detected Ξ₀ ≠ 1 could never confirm GRUT** (SIGNATURE_AUDIT item 4), and the
  distinction identifies the *dissipative class*, not GRUT within it.
- **vs SCDP:** horn (b)'s achromatic B·H₀/2 has **exactly the SCDP-Markovian form** — that
  is why the bound transfers. Degenerate by construction; only a *derived* B would
  distinguish, and B is staked. Horn (a)'s chromatic ω³ term is in-principle not absorbable
  into a Markovian Γ_T — the one in-principle GRUT-vs-everything structure on the table —
  but it is the parameter-free horn (see §8).
- **The KMS noise ratio:** pinned at T_dS given equilibrium — but that is class-level
  equilibrium physics (rung2 is borrowed Callen–Welton; u1 fence: no form credit). It
  discriminates open-vs-Hermitian gravity, not GRUT-vs-SCDP.

## 8 · Pre-registered decision tree (step 10) — declared before any evaluation

**Verdicts:** DISCRIMINATING / DEGENERATE / UNDERDETERMINED / OUT OF VALID DOMAIN /
NO EFFECT. **Rules:** verdicts are rendered PER HORN and never composed into a single
label; UNDERDETERMINED and OUT OF VALID DOMAIN take precedence over magnitude verdicts for
any contribution they touch; the SPEC's outcomes map as PASS → gate continues toward
DISCRIMINATING, FAIL-BUT-INFORMATIVE → UNDERDETERMINED (relocation priced +1 at entry,
keystone §7), CLOSES-THE-QUESTION → NO EFFECT (TT channel empty), REFUSE → the sector
question is undecidable from the booked family.

- **R1 (sector):** the friction-carrying structure must be *derived* into the TT channel
  from booked nodes. If it enters by projector choice, no verdict above UNDERDETERMINED.
- **R2 (domain):** any contribution whose load-bearing kernel feature has support at
  ω ≲ 3.4H → OUT OF VALID DOMAIN for that contribution.
- **R3 (fixedness):** any staked/illustrative amplitude or unverified identification in the
  chain → UNDERDETERMINED.
- **R4 (absorbability):** a number distinguishable from α_M only → class-level, not
  DISCRIMINATING (Ξ₀ fence); indistinguishable in form from the free SCDP slot →
  DEGENERATE.
- **R5 (magnitude):** |Γ_T| more than 10 orders below both the slot bound and any named
  future sensitivity → NO EFFECT.
- **DISCRIMINATING requires ALL of:** derived sector assignment (R1), fully licensed domain
  (R2), fully fixed coefficients (R3), a structure neither α_M nor free-SCDP can mimic
  (R4), magnitude within named reach (R5).

## 9 · GATE VERDICT (step 11) — rendered at design time, from statuses alone

**The design does not survive as a prediction hunt. The calculation is not performed.**

Routing that is decidable *now*, from register statuses, with no physics evaluated:

- **Horn (b) trips R1, R2 and R3 simultaneously:** the sector assignment is CHOSEN (input
  3), so the SPEC's own REFUSE clause is live ("if the sector question cannot be settled
  from the booked family"); the τ₂ pole sits in the unaskable region (R2); B is staked and
  B ≡ ε unverified (R3). Even were all three resolved, its achromatic form is
  R4-DEGENERATE with the free SCDP slot. **No route from horn (b) to DISCRIMINATING
  exists on the current record.**
- **Horn (a) passes R1–R3** (derived, licensed, parameter-free) **but is foreseen dead at
  R5:** its scale relative to the slot bound is set by (ω/ω_Pl)² — of order 10⁻⁸¹ at
  ground-based frequencies against an ω/H₀ ~ 10²⁰ enhancement — a design-level
  order-of-magnitude foresight (not a computed number; the exact figure would be the
  calculation's to state) placing it ≳ 60 orders below few × H₀. Because horn (a) has **no
  free parameter**, a calculation can only confirm this routing, never move it. A
  calculation whose verdict cannot change is a closure, not a hunt.
- **The one in-principle discriminating structure** — the chromatic ω³ term with fixed
  coefficient plus the KMS-locked noise companion — lives entirely in horn (a) and dies
  with it at R5. The relation-level content (dissipative ≠ α_M; noise mandatory) is
  class-level and already fenced against GRUT credit.

**Consequence under the stop rule:** Γ_T was the currently identified candidate; this gate
finds the candidate fails at design time. That statement is the deliverable. The remaining
candidates on the record (the USL shape signature; rung8 decoherence bookkeeping) would
each need their own gate; absent one that survives, the honest program statement is **"no
discriminator identified on the current record"** — and the freeze's stop rule governs.

**What remains available but is NOT run under this gate (owner's call):** a *closure
computation* — build `calc/gw_tensor_friction.py` to its SPEC, formally registering the
Q-A REFUSE with the obstruction named (p_tt CHOSEN + ROOT-1 O1–O4) and pinning horn (a)'s
exact parameter-free Γ_T(ω) as GRUT's only licensed entry into the slot. That would close
the `SIGNATURE_AUDIT` gate-to-readmit and EDIT 1's conditional marker as a **computed
refusal** rather than a standing IOU. It is cheap and honest; it is also a closure, not a
prediction, which is why step 11's conditional does not trigger it.

## 10 · Pre-calculation protocol table (frozen; binds any future closure computation)

| row | horn (a) — derived kernel | horn (b) — booked two-scale |
|---|---|---|
| observable | standard-siren amplitude (GW vs EM luminosity distance); NOT dephasing (SPEC Q-D: achromatic friction is phase-degenerate, matched-filter blind by construction) | same |
| predicted quantity | Γ_T(ω) = (3/1280π)(ω³/M_P²)[1 + (104/9)H²/ω²], chromatic | Γ_T = B·H₀/2, achromatic |
| GRUT inputs | Tier-4 coefficients (DERIVED) + equilibrium + projector choice | τ₂ (INSERTED), B (STAKED), B≡ε (UNVERIFIED), sector (CHOSEN), ω_c (UNPINNED) |
| baseline | GR 0; α_M Hermitian slot; SCDP free (Γ_T, ξ) | same |
| what separates | chromaticity + KMS noise companion — class-level only | nothing in form; only the value of B |
| what a null means | nothing (foreseen tens of orders below reach) | nothing (B free to be small) |
| what a positive means | cannot be this term (magnitude); confirms the open-EFT class at most, never GRUT (Ξ₀ fence) | at most consistency with a staked value; CHARTER §4 match-temptation fence applies in full |
| licensed domain | ω ≫ 3.4H — fully licensed | pole at ω ~ H₀ — UNASKABLE (ROOT-1 O1–O4) |

*Inherited obligations for any future run:* SPEC §4 clock scoping and ω_c three-value
sensitivity; SPEC §6 traps 1–4; SPEC §7 must-not-touch list; both B values reported,
labelled, never composed silently; no headline number carrying an unpinned constant.

— *Gate executed by Claude (builder), 2026-09-06. Register, SPEC, and all frozen artifacts
untouched. No number was computed in the making of this verdict.*
