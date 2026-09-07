# SPEC — `calc/gw_tensor_friction.py`

> **Written by Claude (checker) for Ox (builder), 2026-08-22.** Owed since 2026-08-02
> (`SIGNATURE_AUDIT.md:68`); item 3 of `RUNG3_KEYSTONE_MAP.md` §9. It is the only queued item
> that produces a NUMBER rather than a map.
>
> **Pass/fail is pre-registered below, before any result exists.** Nothing here banks; the
> output needs the four-lens screen and the bank gate like anything else.

## 1. The object

GRUT's **induced cosmological tensor friction Γ_T at ω ~ H₀**, computed from the admitted
kernel, in the same parameterisation as the open-EFT-of-gravity slot bound the register
already quotes (`SIGNATURE_AUDIT.md:62`, |Γ_T| ≲ few × H₀, from arXiv:2507.03103).

The two-scale kernel the register itself books:

    chi(w) = A/(1 - i w tau_c) + B/(1 - i w tau_2),   tau_2 ~ 1/H0,   tau_c = 1/w_c

The friction the IR pole induces is **achromatic**: w*Im chi_IR/2 -> B*H0/2 as w*tau_2 >> 1,
constant in w (verified to six decimals across 10-1024 Hz during the 2026-08-20 pass).

## 2. The pre-registered question (unchanged from the register)

> **Does the local memory scale connect parameter-free, or does the bridge need a new
> inserted scale?**

## 3. What this must settle, in order

**(Q-A) The sector question — this dominates everything else.** Does the tau_2 pole appear in
the **P^TT** channel at all, or only in the scalar **P^(0s)** channel that `p_tt_ansatz`
excludes? Gravitational waves propagate through the TT coefficient. If the IR pole is
scalar-only, the whole friction result is zero in this channel and the question closes.

Note the horns, because neither is free:
- under `p_tt_ansatz` (TT-only, K^R = alpha*chi*P^TT) there is no scalar channel for the pole
  to hide in -- but there is then also no channel for rung7's w(z), a homogeneous background
  equation of state, so B is unpinned;
- under the `operator_basis` two-survivor family (K = c2*P^TT + c0*P0s) the scalar channel
  exists and the escape is open.
**Neither horn supports a quoted number. Settle which family you are in FIRST and say so.**

**(Q-B) The value of B.** B is a **staked illustrative** amplitude; its own source file
disclaims the form (`wz_dark_energy.py:18-25`, "eps is a staked amplitude ... the exact form
needs the full Calzetta-Hu in-in stress tensor"). Two values are live and they differ by
~3.2 orders:
- B = 0.4 (the staked value) -> Gamma_T = 0.2*H0, INSIDE the few-x-H0 slot bound by ~5x;
- B ~ 2.4e-4 (implied by the conformalon epoch-free rate leg, w_a = -1/(8 pi^2 Q^4)) ->
  Gamma_T ~ 1.2e-4 * H0, invisible.
**Report BOTH, labelled, and do not pick one silently.** The 2026-08-20 pass produced these
40 lines apart and never composed them; that composition is part of this deliverable.

**(Q-C) B == eps?** B is the residue of the IR pole in the **TT bath kernel** nu(t); eps is
the amplitude of a **background equation-of-state** response. Identifying them is a separate
unverified assumption and was flagged as such. Either justify it or carry both symbols.

**(Q-D) Which channel is the bound even about?** The friction is achromatic, therefore
**degenerate with the coalescence phase**, so the matched-filter dephasing test in
`gw_dissipation_bounds.py` is blind to it BY CONSTRUCTION. The channel that is not blind is
**standard-siren amplitude**. Compute in that channel; do not re-derive a dephasing number.

## 4. Clock scoping (mandatory — this is a keystone-map D5/C5 obligation)

Work in the **single FRW cosmic clock** throughout, and say so on the file's face. Row C5 of
`RUNG3_KEYSTONE_MAP.md` §1.3 records that the mu_linear / ISW / GW family is already
internally consistent in that one clock; this file inherits that and must not import a
static-Killing or e-fold quantity without the D1-D6 conversion written out.

**w_c is NOT PINNED and it matters here.** Three in-corpus values span 39.6 orders:
2*pi*689 rad/s (21.30), the hand-set 1e40*H0 (40.00, `wz_dark_energy.py:61`), and the Planck
frequency (60.93). The UV/IR crossover goes as sqrt(w_c), so the choice moves it ~10 orders --
two independent passes computed that crossover and got 10 Hz vs 0.64 THz **from this alone**.
**Declare which w_c you use, report the answer's sensitivity to all three, and do not let an
unpinned constant enter a headline.**

## 5. Pass / fail, declared now

**PASS (parameter-free bridge)** if Gamma_T follows from the admitted kernel with **no new
inserted scale**, in one declared clock, with the sector question (Q-A) answered from the
booked family rather than chosen -- and the answer is stable across the three w_c values to
within the "few" in "few x H0".

**FAIL-BUT-INFORMATIVE (relocated, not discharged)** if a parameter-free number requires a new
commitment. Then **price it as a NEW +1 at its point of entry**, per `RUNG3_KEYSTONE_MAP.md`
§7's bridge test. A relocation reported as a discharge is the laundering shape.

**CLOSES THE QUESTION** if (Q-A) returns scalar-only: the TT friction is zero in this channel,
`rung4_love_kk`'s conditional marker resolves to "dephasing number stands, amplitude channel
empty," and EDIT 1 in `handover/REGISTER_EDITS_DRAFT_2026-08-20.md` can be finalised.

**REFUSE** if the sector question cannot be settled from the booked family. An early "my
machinery cannot in principle produce this, and here is which obstruction applies" is a
first-class result that terminates the question cleanly (the dispatch brief's standing guard).

## 6. Traps, each already sprung once in this program

1. **Do not transplant a functional form across backgrounds without checking its own
   identity.** The Schwarzschild Zerilli potential fails the Chandrasekhar identity on SdS
   (residual 72 H^2 M^2 f/(...) at O(M^2 H^2)) while looking correct. Whatever closed form you
   borrow, verify it satisfies its own defining relation ON THE BACKGROUND YOU USE.
2. **Check what your check is compared AGAINST.** Five defects in this layer have now been
   check-side, not physics-side; the most recent was a reference value 4x too large that a
   fix had been tuned to match. State where every target number comes from.
3. **A magnitude test cannot separate solutions that share magnitude.** Compare complex values,
   or phases, or both.
4. **The match temptation** (CHARTER §4): a computed Gamma_T landing near the slot bound is to
   be scrutinised hardest, never celebrated. The bound is a bound on a SHARED slot, not a
   decomposed measurement of GRUT's kernel.

## 7. What this file must not do

Not touch `claims.json`. Not resolve the TT quarantine or the Class-A suspension. Not amend
the 22-62 orders in the seven downstream documents -- that number is correct AS A DEPHASING
STATEMENT and only the amplitude channel is at issue. Not enter the Class-C frontier: this is
the admitted linear-response kernel, not the assembled interacting Sigma.
