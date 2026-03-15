# Phase IV Route C — Strong-Field Lapse Correction

## A. Mission and Context

### A.1 What Was Established

Route C Parts 1 + 2 established that the nonlocal retarded action's stress-functional and auxiliary-field reduction **commute** at first perturbative order around FRW for three independent scalar perturbation channels:

- **Source perturbation (δX):** Commutes exactly (Markov property).
- **Kernel perturbation (δτ):** Commutes exactly (Markov property for kernel coefficients).
- **Lapse perturbation (Ψ):** Does NOT commute in coordinate time; DOES commute in proper time.

The lapse correction ODE was identified:

    τ · d(δΦ)/dt + δΦ = Ψ · (X − Φ)

with analytical solution (constant source):

    δΦ(t) = Ψ · X · (t/τ) · exp(−t/τ)

peaking at Ψ·X/e at t = τ.  Route C was upgraded to `perturbatively_verified__coordinate_time`.

### A.2 The Deepest Remaining Obstruction

The lapse correction was quantified at a single compactness (R = 3r_s, Ψ = 1/6 → 6.1% correction). The key remaining question: **how does this correction scale with compactness C = r_s/R across the full strong-field regime, and does it affect any Phase III canon quantity?**

### A.3 Mission

Advance Route C into the strong-field collapse regime by:
1. Scanning the lapse correction across compactness C ∈ [0.05, 3.0]
2. Proving the self-healing property at the GRUT equilibrium endpoint
3. Bounding the impact on ringdown, echo, Love numbers, and boundaries
4. Classifying each regime and determining the status-ladder impact

---

## B. Two Lapse Channels

### B.1 Schwarzschild Lapse Proxy (Channel A)

    Ψ_Schw(C) = C / 2 = r_s / (2R)

This is the Newtonian gravitational potential in the Schwarzschild exterior. It serves as a **reference scaling** for the lapse correction magnitude.

- Valid as a background estimate for C ≲ 1 (exterior region).
- At the endpoint (C = 3): Ψ_Schw = 3/2, giving A_Schw = 1 − 3 = −2 (below the Schwarzschild horizon). This value is **not physically applicable** at the GRUT endpoint.

### B.2 Effective GRUT Lapse Proxy (Channel B)

    Ψ_eff(C) = heuristic interpolation

The GRUT quantum-pressure barrier modifies the effective metric near and below the would-be horizon. The effective lapse at the endpoint is NOT the Schwarzschild value. Instead:

- At low C (C ≪ 1): Ψ_eff ≈ Ψ_Schw (they agree in weak field).
- At the endpoint (C = 3): Ψ_eff is bounded, estimated heuristically as Ψ_eff ∼ α_vac = 1/3, motivated by the barrier strength scaling as O(α_vac) of the gravitational potential.

**CRITICAL:** Ψ_eff is a **heuristic interpolation / effective proxy**, NOT a derived GRUT lapse law. It is treated with a **scenario scan** (not a confidence interval):

| Scenario | Ψ_eff | δΦ/Φ | Classification |
|----------|-------|-------|---------------|
| Low      | α_vac/2 = 1/6 | 6.1% | bounded_extrapolated |
| Nominal  | α_vac = 1/3   | 12.3% | significant |
| High     | 2·α_vac = 2/3 | 24.5% | perturbative_breakdown |

These two channels must never be conflated.

---

## C. Compactness Scan

### C.1 First-Order Correction Scaling

For either lapse channel:

    δΦ/Φ = Ψ / e ≈ 0.368 · Ψ

This is the peak fractional correction at t = τ.

### C.2 Classification Thresholds

Thresholds are defined on **correction magnitude** δΦ/Φ, NOT on compactness:

| Classification | δΦ/Φ range | Meaning |
|---------------|-----------|---------|
| negligible | < 1% | No impact on canon quantities |
| bounded_perturbative | 1–5% | First-order perturbative, corrections trackable |
| bounded_extrapolated | 5–10% | Beyond strict perturbative validity, scaling plausible |
| significant | 10–20% | Must be carried forward |
| perturbative_breakdown | > 20% | First-order analysis unreliable |

Approximate C values at these thresholds (Schwarzschild reference, **model-dependent**):

| Threshold | δΦ/Φ | C_Schw | R/r_s |
|-----------|-------|--------|-------|
| Negligible boundary | 1% | 0.054 | 18.4 |
| Perturbative boundary | 5% | 0.272 | 3.7 |
| Extrapolated boundary | 10% | 0.544 | 1.8 |
| Significant boundary | 20% | 1.087 | 0.92 |

### C.3 Scan Results (30 points, C ∈ [0.05, 3.0])

- 1 point negligible
- 11 points bounded_perturbative
- 5 points bounded_extrapolated
- 5 points significant
- 8 points perturbative_breakdown

The correction increases monotonically with C. In the weak-field regime (C < 0.054), the correction is negligible. In the moderate regime (C ∼ 0.3), it reaches ∼5%. Near the horizon (C ∼ 1), it reaches ∼18%.

---

## D. Endpoint Self-Healing

### D.1 The Self-Healing Property

This is the **central result** of the strong-field analysis.

At the GRUT equilibrium endpoint (R_eq = r_s/3, C = 3), the collapse ODE reaches force balance:

    M_drive → a_grav

This means the lapse correction source term:

    Ψ · (X − Φ) = Ψ · (a_grav − M_drive) → 0

**vanishes identically** at equilibrium. The lapse correction ODE becomes:

    τ · d(δΦ)/dt + δΦ = 0

with only the decaying solution δΦ ∼ exp(−t/τ) → 0.

### D.2 Consequences

1. **The endpoint law R_eq/r_s = 1/3 is UNAFFECTED** — independent of Ψ.
2. **Force balance is PRESERVED identically** — the correction is zero at equilibrium.
3. **The correction is maximal during the transient approach**, not at the final state.
4. **Self-healing holds for ANY value of Ψ** — it is a structural property of the force-balance condition, not a perturbative coincidence.

### D.3 Derivation Level

Self-healing is **exact** as a source-term identity at equilibrium (M_drive = a_grav is the equilibrium condition). It is proven at first perturbative order. Nonlinear verification (beyond first order in Ψ) is OPEN.

---

## E. Schwarzschild Lapse at the Endpoint

At R_eq = r_s/3:

    A_Schw = 1 − r_s/R_eq = 1 − 3 = −2

This is below the Schwarzschild horizon. In standard GR, no static equilibrium exists at this radius.

In the GRUT framework, the quantum-pressure barrier supports equilibrium. The effective metric is NOT Schwarzschild — the barrier potential adds a positive correction to the lapse. The EXACT effective lapse at the endpoint depends on the full GRUT metric solution, which requires:

- Covariant field equations (Candidate 2 or beyond)
- Interior metric derived from those equations (not the current effective ansatz)

The heuristic estimate Ψ_eff ∼ α_vac = 1/3 is bounded by the barrier strength scaling and is treated as a **scenario scan** in Section B.2.

---

## F. Proper-Time vs Coordinate-Time

The memory ODE in coordinate time uses τ_coord = τ. In proper time:

    τ_proper = τ / (1 + Ψ)

The fractional shift:

    Δτ/τ = −Ψ / (1 + Ψ) ≈ −Ψ   (for Ψ ≪ 1)

Key thresholds (Schwarzschild reference, model-dependent C values):

| τ shift | C_Schw |
|---------|--------|
| 1% | 0.020 |
| 5% | 0.105 |
| 10% | 0.222 |

At the endpoint (Schwarzschild: Ψ = 1.5), the τ shift would be 60%. With the effective proxy (Ψ_eff = 1/3), the shift is 25%. This is substantial but does NOT affect the equilibrium (self-healing).

---

## G. Ringdown/Echo Impact (Bounded Estimate)

**FRAMING: All quantities in this section are FIRST-ORDER BOUNDED ESTIMATES, not derived corrected dispersion relations.**

Around the equilibrium, perturbations in the memory field experience a lapse-modified τ:

    τ_eff_proper ≈ τ / (1 + Ψ_eq)

This gives bounded estimates for:

**Q factor:**
    Q_bounded ∼ Q_canon · (1 + Ψ_eq)

| Scenario | Ψ_eq | Q_shift |
|----------|------|---------|
| Low | 1/6 | +17% |
| Nominal | 1/3 | +33% |
| High | 2/3 | +67% |

**Structural identity:**
    ω₀·τ_bounded ∼ 1 / (1 + Ψ_eq)

| Scenario | ω₀·τ |
|----------|-------|
| Low | 0.857 |
| Nominal | 0.750 |
| High | 0.600 |

**Echo channel:** The echo amplitude correction is O(Ψ_eq) × canon echo amplitude (∼1.1%). At the nominal scenario, this is ∼0.37% correction on top of 1.1%, giving an echo channel status of **preserved**.

The exact modification requires solving the full lapse-corrected PDE, which is beyond the scope of this perturbative analysis.

---

## H. Love Number Impact (Bound Only)

**STATUS: UNDERDETERMINED.**

Tidal Love numbers are NOT YET COMPUTED in the GRUT codebase. The lapse correction affects the effective rigidity of the interior via the τ shift, giving a rigidity shift scale of O(Ψ_eff).

No Love number value (k₂ or otherwise) is returned. Only:
- Impact classification: bounded_underdetermined
- Rigidity shift scale: O(1/3)
- Requirements for actual computation (5 prerequisites listed)

---

## I. Force Balance and Boundary Impact

**At equilibrium:** Force balance is PRESERVED identically by self-healing (Section D).

**During transient approach:** The lapse correction modifies the effective memory field by O(Ψ/e), giving a bounded transient correction to the effective force. At the nominal effective lapse (Ψ_eff = 1/3), this is ∼12.3% of a_grav during the transient peak. The endpoint is determined by the equilibrium condition X = Φ, not by transient values.

**Junction conditions (Israel formalism):** The surface energy σ and memory field boundary conditions receive O(Ψ) corrections. These are at "effective level" — the Israel formalism is applied to effective stress-energy, not derived from GRUT field equations.

---

## J. Master Classification and Status-Ladder Impact

### J.1 Classification: BOUNDED

The strong-field lapse correction is classified as **BOUNDED**:

- The correction is O(Ψ/e) during the transient approach.
- The correction VANISHES at equilibrium via self-healing.
- Canon values at the endpoint (R_eq/r_s = 1/3, ω₀τ = 1, Q = 6) are UNAFFECTED.
- Phase III status ladder is PRESERVED.

### J.2 Per-Regime Breakdown

| Regime | Classification | Basis |
|--------|---------------|-------|
| Cosmology | negligible | Ψ ∼ 10⁻⁵ |
| Weak collapse (C < 0.054) | negligible | δΦ/Φ < 1% |
| Moderate collapse | bounded_perturbative | 1–5% |
| Strong collapse | bounded_extrapolated | 5–10% |
| Near-horizon | significant | 10–20% |
| Endpoint | **self_healing** | correction → 0 |

### J.3 Status-Ladder Impact

**Does the lapse correction modify the Phase III status ladder, or only the quantitative confidence bounds?**

**Answer:** Phase III status ladder is **PRESERVED**. The correction clarifies the strong-field applicability window of the coordinate-time framework without modifying the ladder itself:

- Endpoint law: UNAFFECTED (self-healing)
- Force balance: PRESERVED
- Structural identity: PRESERVED at equilibrium
- Response class: PRESERVED (mixed_viscoelastic)
- Echo channel: PRESERVED (bounded correction)

The quantitative confidence bounds are **refined**: the coordinate-time framework is valid up to O(Ψ) corrections in the memory timescale, with Ψ negligible in cosmology and bounded at the endpoint.

---

## K. Classification Table

| Quantity | Status | Mechanism |
|----------|--------|-----------|
| Endpoint law R_eq/r_s = 1/3 | UNAFFECTED | Self-healing: source term → 0 at equilibrium |
| Force balance | PRESERVED | Self-healing: δΦ → 0 at equilibrium |
| ω₀τ = 1 | PRESERVED at eq | Self-healing; O(Ψ) shift around eq (bounded) |
| Q = 6 | PRESERVED at eq | Self-healing; O(Ψ) shift around eq (bounded) |
| Echo amplitude (1.1%) | PRESERVED | O(Ψ) correction ≪ canon amplitude |
| Love numbers | UNDERDETERMINED | Not computed; rigidity shift O(Ψ) |
| Junction conditions | BOUNDED | O(Ψ) correction at effective level |
| Transient correction | BOUNDED | O(Ψ/e) during approach, decays at eq |
| Phase III status ladder | PRESERVED | All canon values unaffected at eq |

---

## L. Explicit Nonclaims

1. The effective GRUT lapse proxy (Ψ_eff) is a **heuristic interpolation**, NOT a derived GRUT lapse law.
2. The Schwarzschild lapse proxy (Ψ_Schw = C/2) is an exterior reference scaling, not valid at the GRUT endpoint.
3. The two lapse channels are tracked separately; they must not be conflated.
4. Self-healing at equilibrium is exact (source term identity) but proven only at **first perturbative order**.
5. Nonlinear self-healing (beyond first order in Ψ) is **UNTESTED**.
6. Classification thresholds (1%, 5%, 10%, 20%) are on correction magnitude δΦ/Φ, not on compactness.
7. C values at regime boundaries are **model-dependent** mappings from the Schwarzschild reference, not universal thresholds.
8. Q and ω₀τ shifts are **first-order bounded estimates**, not derived corrected dispersion relations.
9. The full ringdown modification requires solving the lapse-corrected PDE (beyond current scope).
10. No Love number value is returned; only an impact bound and classification.
11. Love number computation requires covariant field equations, interior solution, tidal framework, junction conditions, and mode separation.
12. Phase III status ladder is preserved; the correction clarifies strong-field applicability bounds, not modifies the ladder.
13. The endpoint sensitivity band is a **SCENARIO SCAN**, not an inferred confidence interval.
14. The analysis is limited to scalar memory field perturbations; tensorial memory generalization is open.
15. Observer-flow dependence is NOT resolved by this analysis.
16. Quantization of the nonlocal action remains OPEN.
17. The coordinate-time framework acquires O(Ψ) corrections to the memory timescale in strong field; these should be tracked in future calculations.
