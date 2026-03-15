# Phase IV — Effective Lapse Derivation from Covariant Field Equations

## A. Mission and Context

### A.1 Prior State

The strong-field lapse correction analysis (Route C Strong-Field Follow-Up) established:

- The lapse-sector correction is **bounded** across the compactness range C in [0.05, 3.0].
- The correction **self-heals** at the equilibrium endpoint: the source term Psi * (X - Phi) vanishes when M_drive = a_grav.
- The Phase III endpoint law R_eq / r_s = 1/3 is **unaffected**.
- The Phase III status ladder is **preserved**.

The single remaining epistemic uncertainty: the **effective lapse at the endpoint** was heuristic. The function `_barrier_lapse_estimate()` in `nonlocal_strong_field.py` returned `alpha_vac = 1/3` with no derivation chain. The sensitivity band [alpha_vac/2, alpha_vac, 2*alpha_vac] = [1/6, 1/3, 2/3] was labeled as a scenario scan.

### A.2 Mission

Derive the effective lapse at the GRUT equilibrium endpoint from the covariant field-equation framework as far as honestly possible. Determine whether the prior heuristic can be replaced by a derived value or tighter bounded interval.

### A.3 Result Summary

The central lapse proxy is **strengthened from heuristic to constitutive-derived**. The true interior metric lapse **remains unresolved** pending a deeper interior covariant solution.

---

## B. Central Result — Barrier-to-Gravity Potential Ratio

### B.1 The Algebraic Identity

At the GRUT equilibrium endpoint (R_eq, where force balance holds), the barrier-to-gravity potential ratio is:

    Phi_barrier / Phi_grav = 1 / (1 + beta_Q)

**Derivation:**

1. Barrier potential at R_eq (from integrating the barrier force):

       Phi_barrier = GM * epsilon_Q * r_s^beta_Q / ((1 + beta_Q) * R_eq^(1 + beta_Q))

2. Gravitational potential at R_eq:

       Phi_grav = GM / R_eq

3. Ratio:

       Phi_barrier / Phi_grav = epsilon_Q * r_s^beta_Q / ((1 + beta_Q) * R_eq^beta_Q)
                               = epsilon_Q / ((1 + beta_Q) * (R_eq/r_s)^beta_Q)

4. By the endpoint law (from force balance a_Q = a_grav):

       (R_eq / r_s)^beta_Q = epsilon_Q

5. Therefore:

       Phi_barrier / Phi_grav = epsilon_Q / ((1 + beta_Q) * epsilon_Q) = 1 / (1 + beta_Q)

### B.2 Properties

- **EXACT**: algebraic identity, proven from the barrier integral and endpoint law.
- **Independent of epsilon_Q**: cancels between numerator and denominator.
- **Independent of alpha_vac**: does not enter the barrier integral.
- **Independent of mass**: cancels in the ratio.
- **Depends only on beta_Q**: the barrier steepness exponent.

For canon beta_Q = 2: ratio = 1/3.

### B.3 Classification

This is a **Level 1** result: an exact algebraic identity at the endpoint within the constitutive framework.

---

## C. Three Derivation Routes

### C.1 Route A — Barrier-Gravity Ratio as Lapse Proxy

The exact barrier-to-gravity ratio (Level 1) is identified as the effective lapse SCALE:

    Psi_proxy = 1 / (1 + beta_Q)

**Basis:** The barrier potential energy at the endpoint sets the gravitational energy scale for the lapse correction. The barrier-to-gravity ratio is the natural dimensionless parameter for the effective lapse at the constitutive level.

**Classification:** constitutive_derived (Level 2). This is a lapse PROXY / effective lapse scale, NOT the true metric lapse.

For canon beta_Q = 2: Psi_proxy = 1/3.

### C.2 Route B — Effective Metric at Endpoint

The constitutive ansatz from `interior_covariant.py` gives:

    A_schw = 1 - C_endpoint = 1 - 3 = -2
    delta_A = 2 * Phi_barrier / c^2 = C_endpoint / (1 + beta_Q) = 1
    A_eff = A_schw + delta_A = -2 + 1 = -1

Since **A_eff < 0**, the coordinate t is spacelike at the endpoint. The standard redshift formula Psi = 1/sqrt(A_eff) - 1 does NOT apply when A_eff < 0.

**Classification:** unresolved. The metric route does not yield a lapse value.

**Significance:** A_eff = -1 < 0 reveals that the constitutive ansatz is INCOMPLETE for the interior metric. The barrier potential (delta_A = 1) does not fully compensate the Schwarzschild deficit (A_schw = -2) to make A_eff positive. The true interior metric requires additional contributions that are not captured by the constitutive-level post-Newtonian mapping delta_A = 2*Phi_barrier/c^2.

### C.3 Route C — Schwarzschild Reference

    Psi_Schw = C_endpoint / 2 = 3/2

This ignores the barrier entirely. It serves as an **upper bound only**: the barrier can only reduce the effective gravitational potential relative to Schwarzschild.

**Classification:** upper_bound_only.

### C.4 Comparison

| Route | Psi_eff | Classification | Basis |
|-------|---------|---------------|-------|
| A: Barrier-gravity ratio | 1/(1+beta_Q) = 1/3 | constitutive_derived | Barrier integral + endpoint law |
| B: Effective metric | None (unresolved) | unresolved | A_eff < 0, redshift formula inapplicable |
| C: Schwarzschild | C/2 = 3/2 | upper_bound_only | Ignores barrier |

Route A is preferred.

---

## D. The Effective Metric Ansatz at the Endpoint

### D.1 Computation

From the constitutive framework (`interior_covariant.py`, `build_interior_metric`):

    Phi_barrier(R_eq) = GM * epsilon_Q * r_s^beta_Q / ((1+beta_Q) * R_eq^(1+beta_Q))

For canon parameters (epsilon_Q = 1/9, beta_Q = 2, R_eq = r_s/3):

    Phi_barrier = GM / r_s = c^2 / 2

    delta_A = 2 * Phi_barrier / c^2 = 1

    A_eff = (1 - 3) + 1 = -1

### D.2 Interpretation

A_eff = -1 < 0 means the time coordinate t is spacelike at the endpoint. In the Schwarzschild interior (r < r_s), this is expected — the roles of t and r are exchanged. However, the GRUT equilibrium requires a quasi-static configuration, which in turn requires a timelike direction for the collapsed object to be stationary in.

This reveals a gap in the constitutive framework: the post-Newtonian mapping delta_A = 2*Phi_barrier/c^2 does not fully resolve the interior metric structure. A proper GRUT interior solution would need to provide a positive-definite effective lapse at R_eq.

### D.3 What This Does NOT Mean

- It does NOT invalidate the equilibrium (force balance is a dynamical condition, not a metric condition).
- It does NOT invalidate the endpoint law (derived from force balance, not from the metric).
- It does NOT invalidate self-healing (depends on X - Phi = 0, not on the metric).

---

## E. Why the Prior Heuristic Was Numerically Correct

For canon parameters beta_Q = 2 and alpha_vac = 1/3:

    1/(1 + beta_Q) = 1/(1 + 2) = 1/3 = alpha_vac

This is a **coincidence** of the canon parameter values. The barrier-to-gravity ratio depends on beta_Q (barrier steepness), while alpha_vac is the vacuum susceptibility. They happen to be equal when beta_Q = 2 and alpha_vac = 1/3 because 1/(1+2) = 1/3.

For other parameter values, they diverge:

| beta_Q | 1/(1+beta_Q) | alpha_vac | Coincide? |
|--------|-------------|-----------|-----------|
| 1.0 | 0.500 | 0.333 | No |
| 1.5 | 0.400 | 0.333 | No |
| 2.0 | 0.333 | 0.333 | Yes |
| 2.5 | 0.286 | 0.333 | No |
| 3.0 | 0.250 | 0.333 | No |
| 4.0 | 0.200 | 0.333 | No |

The prior heuristic "Psi_eff ~ alpha_vac" was numerically correct but for a different and weaker reason than the constitutive derivation reveals. The true parametric dependence is on beta_Q, not alpha_vac.

---

## F. Sensitivity / Scenario Band

### F.1 The Band

    Central: 1/(1+beta_Q) = 1/3  [constitutive-derived]
    Low:     1/(2*(1+beta_Q)) = 1/6
    High:    2/(1+beta_Q) = 2/3

This is a **SCENARIO BAND**, not a confidence interval or a bounded-derived interval. The factor-of-2 width reflects the model uncertainty in the sub-horizon metric-to-lapse mapping.

### F.2 Comparison to Prior Band

The prior heuristic band was [alpha_vac/2, alpha_vac, 2*alpha_vac] = [1/6, 1/3, 2/3].

For canon parameters, the new band is **numerically identical** to the prior band. The difference is in status:

| Aspect | Prior | New |
|--------|-------|-----|
| Central value | heuristic | constitutive_derived |
| Band type | scenario scan | scenario band around derived proxy |
| Parametric dependence | alpha_vac | beta_Q |

The band width is NOT reduced. The source of remaining uncertainty — the sub-horizon metric-to-lapse mapping — cannot be resolved without a covariant interior solution.

---

## G. Self-Healing Independence

Self-healing depends on the lapse correction source term:

    Source = Psi * (X - Phi) = Psi * (a_grav - M_drive)

At equilibrium, M_drive = a_grav (force balance), so the source vanishes **identically, regardless of Psi**. The correction ODE becomes:

    tau * d(delta_Phi)/dt + delta_Phi = 0

with only the decaying solution delta_Phi ~ exp(-t/tau) -> 0.

Self-healing is **preserved under all three routes**:
- Route A (Psi_proxy = 1/3): source = (1/3) * 0 = 0
- Route B (unresolved): source = Psi * 0 = 0 for any Psi
- Route C (Psi_Schw = 3/2): source = (3/2) * 0 = 0

This is a **structural property of force balance**, not a perturbative coincidence.

---

## H. Impact on Prior Strong-Field Results

### H.1 Classification: BOUNDED (preserved)

The strong-field classification established in the prior analysis is unchanged. The correction is O(Psi/e) during the transient and vanishes at equilibrium.

### H.2 Sensitivity Band: CONFIRMED

The prior band [1/6, 1/3, 2/3] is numerically confirmed with elevated central-value status.

### H.3 Shift Estimates (Constitutive Level)

Using the constitutive-derived central proxy Psi_proxy = 1/3:

| Quantity | Value | Status |
|----------|-------|--------|
| Proper-time shift | 25% | constitutive-level bounded estimate |
| Q shift | +33% | constitutive-level bounded estimate |
| omega_0*tau at eq | 0.75 | constitutive-level bounded estimate |

These are numerically unchanged from the prior analysis (same central value for canon). They are bounded estimates, not derived corrected dispersion relations.

### H.4 Status Ladder: PRESERVED

No Phase III status-ladder rung is modified.

---

## I. Three Explicit Levels

| Level | Quantity | Status | Description |
|-------|----------|--------|-------------|
| 1 | Barrier-to-gravity ratio | **exact** | Algebraic identity 1/(1+beta_Q) at endpoint |
| 2 | Central lapse proxy | **constitutive_derived** | Barrier ratio identified as lapse scale |
| 3 | True interior metric lapse | **unresolved** | Requires covariant interior solution |

The Level 1 → Level 2 step is the constitutive identification: the barrier potential energy scale determines the effective lapse scale. This is physically motivated and within the constitutive framework.

The Level 2 → Level 3 step requires going beyond the constitutive ansatz to a covariant interior metric solution. This is the remaining obstruction.

---

## J. Remaining Obstruction

### J.1 The Sub-Horizon Metric-to-Lapse Mapping

The constitutive ansatz gives A_eff = -1 < 0 at the endpoint. This means:

1. The standard redshift formula does not apply (t is spacelike).
2. The true effective metric at the barrier-supported equilibrium is not resolved.
3. The mapping from the barrier potential to the metric lapse is model-dependent in the sub-horizon regime.

### J.2 Requirements for Resolution

Resolving the true metric lapse (Level 3) requires:

1. **Covariant field equations** with a derived interior metric that resolves the metric signature at R_eq.
2. **A proper-time definition** for the barrier-equilibrium observer in the sub-horizon regime.
3. **Possibly going beyond the post-Newtonian mapping** delta_A = 2*Phi_barrier/c^2 to a fully covariant treatment.
4. **T^Phi derived from a Lagrangian** (currently schematic/effective).

### J.3 What Is NOT Required

- The endpoint law does not need revision (protected by self-healing).
- Force balance does not need revision.
- The Phase III status ladder does not need revision.

---

## K. Explicit Nonclaims

1. The central lapse proxy 1/(1+beta_Q) is constitutive-derived (Level 2), NOT the true metric lapse (Level 3).
2. The barrier-to-gravity ratio 1/(1+beta_Q) is exact (Level 1), but its identification as a lapse scale is at the constitutive level.
3. Route B (effective metric) is UNRESOLVED at the endpoint because A_eff < 0.
4. The true interior metric lapse requires a covariant interior solution beyond the constitutive ansatz.
5. The constitutive ansatz gives A_eff = -1 < 0, showing the ansatz is incomplete for the interior metric.
6. The coincidence 1/(1+beta_Q) = alpha_vac at canon beta_Q = 2 is a parametric coincidence, not the fundamental relationship.
7. The sensitivity band is a SCENARIO BAND, not a confidence interval.
8. Self-healing is independent of Psi_eff and preserved under all routes.
9. Nonlinear self-healing beyond first perturbative order is UNTESTED.
10. Shift estimates are bounded estimates at the constitutive level, not derived corrected dispersion relations.
11. No claim is made about the effective lapse away from the equilibrium endpoint.
12. Tensorial memory generalization could modify the effective lapse.
13. Observer-flow dependence is not resolved.
14. The derivation depends on spherical symmetry; no Kerr extension is made.
15. The sub-horizon metric-to-lapse mapping is the remaining obstruction.
16. The beta_Q parametric scan shows Psi_proxy varies continuously with beta_Q.
17. No detector-level or observational predictions are made from the proxy.
