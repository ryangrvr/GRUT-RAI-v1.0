# Phase III-C WP3: Static Exterior Null-Result Confirmation

**DATE**: 2026-03-11
**STATUS**: ANALYSIS COMPLETE — null at leading order (conditional on Schwarzschild-like exterior)
**CONDITIONAL ON**: WP1 assessment: Schwarzschild-like exterior (preserved_candidate)

---

## A. Mission Statement

Formally verify that static exterior observables — shadow, photon sphere,
and accretion — show zero or negligible deviation from standard GR to
leading order under the WP1 Schwarzschild-like exterior assumption.

This is NOT a speculative pass. It is a bounded confirmation that the
BDCC interior at R_eq = r_s/3 does not leak into static exterior observables
under the current best exterior model.

---

## B. WP1 Exterior Assumption (Inherited)

The WP1 analysis established:

- **Exterior model**: Schwarzschild-like (leading candidate)
- **Birkhoff status**: preserved_candidate (conditional)
- **Confidence**: moderate — consistent with solver, not proven
- **Conditions**: M_drive is matter-local, OP_QPRESS_001 has no exterior self-energy
- **Missing closure**: Covariant treatment required for proof

Under this assumption, the exterior metric is:

    ds² = -(1 - r_s/r) dt² + (1 - r_s/r)⁻¹ dr² + r² dΩ²

for all r > R_eq = r_s/3. Since R_eq < r_s (the BDCC is inside the
horizon), the exterior metric is Schwarzschild at all r ≥ r_s.

---

## C. Observable-by-Observable Analysis

### C.1 Shadow

**Definition**: The shadow is the dark silhouette of a black hole as seen
by a distant observer. Its angular radius is determined by the impact
parameter of the unstable photon orbit (photon sphere).

**Schwarzschild result**:

    b_crit = 3√3 M_geom = (3√3/2) r_s

    θ_shadow = b_crit / D   (for distant observer at distance D)

**GRUT-BDCC modification**: NONE at leading order.

**Reasoning**: The shadow boundary is set by null geodesics at the photon
sphere (r = 3M = 3/2 r_s). The BDCC sits at R_eq = r_s/3, which is deep
inside the horizon (compactness C = 3). Photons defining the shadow
boundary never reach R_eq. They orbit at r = 3/2 r_s and either escape
to infinity or fall inward. The interior structure at R_eq has no causal
influence on the photon sphere dynamics.

**Result**: IDENTICALLY NULL under Schwarzschild exterior.

**Caveat**: If the exterior is NOT Schwarzschild (e.g., GRUT memory
modifies the vacuum metric), the shadow could deviate. This requires
the covariant treatment that WP1 identified as a missing closure.

### C.2 Photon Sphere

**Definition**: The radius at which circular null geodesics exist.

**Schwarzschild result**:

    r_ph = 3M = (3/2) r_s

**GRUT-BDCC modification**: NONE at leading order.

**Reasoning**: The photon sphere location is determined by the condition
d²V_eff/dr² = 0 for the effective potential V_eff(r) = (1 - r_s/r)(L²/r²).
Under Schwarzschild exterior, this gives r_ph = 3M exactly. The BDCC at
r_s/3 is inside the horizon and does not enter the exterior potential.

Photon sphere properties (circular orbit frequency, Lyapunov exponent):

    ω_ph = c/(3√3 M_geom) = c/((3√3/2) r_s)
    λ_Lyap = ω_ph / √2

These are IDENTICALLY STANDARD under Schwarzschild exterior.

**Result**: IDENTICALLY NULL under Schwarzschild exterior.

### C.3 Accretion

**Definition**: Observable accretion properties: innermost stable circular
orbit (ISCO), radiative efficiency, Eddington luminosity profile.

**Schwarzschild results**:

    r_ISCO = 6M = 3 r_s
    η = 1 - √(8/9) ≈ 5.72%   (radiative efficiency)
    L_Edd = 4π G M m_p c / σ_T   (Eddington luminosity)

**GRUT-BDCC modification at leading order**: NONE.

**Reasoning**:

1. **ISCO**: Determined by the exterior metric at r = 6M = 3r_s. The
   BDCC at r_s/3 is inside the horizon. ISCO is IDENTICALLY STANDARD.

2. **Radiative efficiency**: Depends on the specific energy at ISCO,
   which is a function of the exterior metric at r_ISCO. Under
   Schwarzschild: η = 1 - E_ISCO/mc² = 1 - √(8/9). This is
   IDENTICALLY STANDARD.

3. **Eddington luminosity**: Depends only on the total mass M (which is
   conserved in the GRUT solver). IDENTICALLY STANDARD.

4. **Disk spectrum**: The thin-disk spectrum (Novikov-Thorne) depends on
   the metric from r_ISCO outward. Under Schwarzschild exterior, this is
   IDENTICALLY STANDARD.

**Possible second-order effects**:

If echoes exist (WP2: ~1.1% amplitude), they could in principle
modulate the inner accretion flow through perturbation-accretion coupling.
This is a SECOND-ORDER EFFECT at the 1% level, not detectable with
current instruments, and requires full MHD simulation to evaluate.

**Result**: NULL at leading order. UNDERDETERMINED at second order
(echo-accretion coupling), but expected negligible.

### C.4 Summary Table

| Observable | GRUT-BDCC Deviation | Status | Basis |
|------------|---------------------|--------|-------|
| Shadow angular radius | 0 | IDENTICALLY NULL | Photon sphere is exterior to horizon; BDCC is interior |
| Photon sphere location | 0 | IDENTICALLY NULL | r_ph = 3M from exterior metric only |
| Photon sphere frequency | 0 | IDENTICALLY NULL | Follows from exterior potential |
| ISCO radius | 0 | IDENTICALLY NULL | r_ISCO = 6M from exterior metric only |
| Radiative efficiency | 0 | IDENTICALLY NULL | η = 1 - √(8/9) from metric at ISCO |
| Eddington luminosity | 0 | IDENTICALLY NULL | L_Edd ∝ M only (mass conserved) |
| Disk spectrum | 0 | IDENTICALLY NULL | Novikov-Thorne depends on exterior metric |
| Echo-accretion coupling | ~1% | UNDERDETERMINED | Second-order; requires full MHD simulation |

---

## D. What Is Identically Unchanged

Under the Schwarzschild-like exterior assumption:

1. **Shadow**: Identical to GR. b_crit = 3√3 M.
2. **Photon sphere**: Identical to GR. r_ph = 3M, ω_ph = c/(3√3 M).
3. **ISCO**: Identical to GR. r_ISCO = 6M.
4. **Radiative efficiency**: Identical to GR. η = 5.72%.
5. **Eddington luminosity**: Identical to GR. L_Edd ∝ M.
6. **Disk spectrum**: Identical to GR (Novikov-Thorne).

All of these are functions of the EXTERIOR metric only. The BDCC at
R_eq = r_s/3 is hidden behind the horizon and has no causal influence
on any of these observables at leading order.

## E. What Is Conditionally Unchanged

1. **Quasi-normal modes (QNMs)**: The QNM ringdown frequencies depend on
   the exterior potential at the photon sphere. Under Schwarzschild exterior,
   the leading QNM frequencies are IDENTICAL to GR. However, late-time
   modifications (echoes) can appear — these are the WP2 echo channel.

2. **Tidal Love numbers**: For a Schwarzschild black hole, tidal Love
   numbers are exactly zero. If the BDCC interior creates a reflecting
   boundary at R_eq, the Love numbers could become nonzero. This is a
   potential observable NOT yet computed. **Status: UNDERDETERMINED.**

## F. What Remains Underdetermined

1. **Echo-accretion coupling**: If echoes modulate the inner accretion
   flow, second-order effects on the disk luminosity curve could exist.
   Expected negligible at ~1% echo amplitude.

2. **Tidal Love numbers**: Could differ from zero due to the BDCC
   boundary. Not computed; requires interior matching of tidal perturbations.

3. **Non-Schwarzschild exterior corrections**: If WP1 is revised (e.g.,
   GRUT memory creates exterior modifications), ALL of the above null
   results would need re-evaluation.

4. **Kerr generalization**: All analysis here is for non-rotating
   (Schwarzschild) black holes. Kerr effects (spin) are deferred.

---

## G. Nonclaims

1. This analysis does NOT prove the BDCC is undetectable. The echo
   channel (WP2) provides a non-null observable.
2. This analysis does NOT prove the exterior is exactly Schwarzschild.
   The WP1 assessment is CONDITIONAL.
3. Null results are CONDITIONAL on the Schwarzschild-like exterior.
   If the exterior is modified, all conclusions change.
4. Tidal Love numbers are NOT computed — they remain an open observable.
5. Echo-accretion coupling is NOT computed — second-order effects are
   not evaluated.
6. Kerr is NOT attempted.
7. No EHT, LIGO, or detector-level predictions are made.

---

## H. Conclusion

Under the WP1 Schwarzschild-like exterior assumption, ALL static exterior
observables (shadow, photon sphere, ISCO, accretion efficiency) are
IDENTICALLY NULL at leading order. The BDCC at R_eq = r_s/3 is hidden
behind the horizon and does not causally affect photon-sphere or accretion
dynamics.

The ONLY non-null observable channel identified so far is the ringdown
echo channel (WP2): a ~1.1% amplitude echo signal at delta_t ~ 0.52 ms
(30 M_sun). This is a DYNAMICAL observable, not a STATIC one.

Tidal Love numbers remain UNDERDETERMINED as a potential additional
non-null channel.

**WP3 STATUS**: ANALYSIS COMPLETE — null at leading order.
**WP1 REVISION REQUIRED**: No. The WP3 result is consistent with the
WP1 Schwarzschild-like assessment. No new calculation forces a revision.
