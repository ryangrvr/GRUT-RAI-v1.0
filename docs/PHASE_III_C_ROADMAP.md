# Phase III-C Roadmap: Exterior Falsifier Program

**Date**: 2026-03-09
**Status**: KICKOFF — no exterior computations performed yet
**Predecessor**: Phase III-B Summary (all 11 interior criteria PASS)

---

## Context

Phase III-B established a solver-backed candidate interior endpoint:

```
R_eq / r_s = alpha_vac = 1/3
C_eq = 3 (compactness at endpoint)
Phi = 1.0 (exact force balance)
Transition: smooth, post-horizon, width ~0.7 r_s
```

The entire barrier-active transition zone lies inside the horizon. The
question now is: **what does this interior structure predict for exterior
observables?**

No exterior predictions exist yet. This roadmap defines the calculation
program to produce them.

---

## Work Package 1 — Exterior Matching

### Questions

1. What exterior metric or effective matching behavior is implied by a
   barrier-dominated compact core at (1/3) r_s?

2. Under what conditions does the exterior spacetime remain observationally
   indistinguishable from Schwarzschild (or Kerr, eventually)?

3. What is the matching surface? Is it the horizon (R = r_s), the
   crystallization threshold (R ~ 0.47 r_s), or the core surface (R_eq)?

4. Does the GRUT memory coupling produce any exterior metric deviation
   at R > r_s, or is the exterior exactly Schwarzschild by Birkhoff's
   theorem?

### What Needs to Be Computed First

**Minimal viable calculation**: Solve for the metric function at the
matching surface. For a static, spherically symmetric core at R_eq:

- **Interior region** (R < R_eq): The core is at force balance (a_net = 0).
  The effective interior equation of state is determined by the balance
  between gravity+memory and the quantum pressure barrier.

- **Matching surface** (R = R_eq or R = r_s): Junction conditions. For a
  perfect fluid sphere, the Israel junction conditions require continuity
  of the induced metric and the extrinsic curvature across the surface.

- **Exterior region** (R > R_eq): In vacuum, Birkhoff's theorem guarantees
  Schwarzschild for any spherically symmetric matter distribution. The
  exterior IS Schwarzschild to the extent that the matter is entirely
  contained within R_eq. But: does the GRUT memory field extend beyond
  the matter surface?

**Key open question**: Is the GRUT memory state M_drive a property of
matter (contained within the shell) or a property of spacetime (potentially
extending outside)? If the latter, the exterior may not be exactly
Schwarzschild.

### Deliverables

| Item | Description | Module |
|------|-------------|--------|
| Matching analysis | Junction conditions at candidate surfaces | `grut/exterior_matching.py` |
| Birkhoff check | Whether GRUT memory coupling breaks Birkhoff | analysis memo |
| Exterior metric | Schwarzschild + possible deviations | output of matching module |

### Missing Equations

1. Israel junction conditions for the GRUT-modified interior
2. Effective stress-energy tensor at the matching surface
3. Whether M_drive contributes to the exterior Weyl curvature
4. TOV-equivalent hydrostatic balance for the BDCC

---

## Work Package 2 — Ringdown / Echo Falsifier

### Questions

1. Could inward-propagating perturbations interact with the candidate
   core or transition region strongly enough to generate echoes or
   modified ringdown?

2. What is the effective potential for wave propagation in the interior
   spacetime? Is there a potential well or barrier near R_eq that could
   reflect waves?

3. What is the minimal computational experiment to test this?

### Physical Setup

In standard GR, the ringdown of a perturbed black hole is governed by
quasinormal modes (QNMs) — damped oscillations of the Regge-Wheeler or
Zerilli potential. These have specific frequencies and damping times that
depend only on M and J (for Kerr).

If a physical core exists at R_eq = (1/3) r_s:
- Perturbations that would normally propagate inward through the horizon
  may encounter the barrier transition zone (0.34 < R/r_s < 0.47).
- The transition zone could reflect a fraction of the wave back outward.
- The reflected wave would need to traverse the potential peak at the
  light ring (R = 3 r_s / 2 in Schwarzschild), producing a delayed
  secondary signal — an "echo."

### What Needs to Be Computed

**Minimal calculation**: Scalar wave scattering on the interior background.

1. **Effective potential**: Compute V_eff(r) for a scalar field on the
   modified interior spacetime. Does the BDCC create a reflecting surface
   or a smooth absorption?

2. **Reflection coefficient**: What fraction of an ingoing wave at the
   horizon is reflected back by the core/transition region?

3. **Echo time delay**: If reflection occurs, what is the round-trip time
   between the potential peak (light ring) and the reflecting surface?

```
t_echo ~ 2 * integral from R_reflect to R_peak of dr / f(r)
```

where f(r) is the metric function.

4. **Ringdown modification**: How do the first few QNM frequencies shift
   compared to Schwarzschild?

### What Would Count as a Discriminating Signal

- **Modified QNM frequencies**: If the first few modes shift by > 1%
  relative to Schwarzschild for the same M, this is potentially observable
  by LIGO/Virgo/KAGRA.

- **Echo amplitude**: If the reflection coefficient is > 10^{-3}, post-
  merger echoes could be detectable in stacked gravitational wave data.

- **Echo timing**: A clean prediction for t_echo(M) would be a falsifiable
  target.

### Deliverables

| Item | Description | Module |
|------|-------------|--------|
| Effective potential | V_eff(r) for scalar field on interior background | `grut/ringdown.py` |
| Reflection solver | Ingoing/outgoing wave decomposition at core | `grut/ringdown.py` |
| Echo timing | t_echo(M) prediction (if reflection exists) | output |
| QNM shift estimate | Delta-omega / omega for fundamental mode | output |
| PACKET_RINGDOWN_v0.1 | Evidence packet with falsifiable predictions | `tools/build_ringdown_packet.py` |

### Missing Equations

1. Scalar wave equation on the GRUT interior background
2. Effective potential V_eff(r*) in tortoise coordinate
3. Boundary condition at R_eq (reflecting, absorbing, or partially reflecting?)
4. Transfer matrix through the transition zone

---

## Work Package 3 — Shadow / Near-Horizon Imaging / Accretion

### Questions

1. Could a core at (1/3) r_s affect the observable shadow, photon region,
   or accretion behavior?

2. What is the photon sphere location in the modified spacetime?

3. Are there observable consequences for EHT-type observations?

### Physical Setup

The black hole shadow is determined by the unstable circular photon orbit
(photon sphere) at R = 3GM/c^2 = (3/2) r_s in Schwarzschild. The shadow
radius depends on the photon sphere location and the metric there.

If the core at R_eq = (1/3) r_s modifies the spacetime only at R < r_s:
- The photon sphere at (3/2) r_s is OUTSIDE the horizon
- If the exterior is exactly Schwarzschild (by Birkhoff), the shadow
  is EXACTLY Schwarzschild — no observable difference
- Any deviation requires the interior structure to modify the exterior
  metric

If the GRUT memory coupling produces a small exterior deviation:
- The photon sphere shifts by a calculable amount
- The shadow radius shifts proportionally
- EHT measurements constrain the shadow to ~10% currently

### What Should Be Computed First

1. **Null geodesics**: Trace photon paths on the (possibly modified)
   exterior metric. Does the shadow change?

2. **Photon sphere**: Is the photon sphere location exactly (3/2) r_s
   or is it shifted?

3. **Near-horizon emission**: If accreting matter falls toward the core
   rather than a singularity, does the emission profile change near the
   inner edge of the accretion flow?

### What Can Be Deferred

- Full ray-tracing with accretion disk models (requires emission model)
- Kerr generalization (requires rotating interior solution)
- Polarization effects (requires vector wave treatment)
- Concrete EHT comparison (requires observational pipeline)

### Deliverables

| Item | Description | Module |
|------|-------------|--------|
| Null geodesic solver | Photon paths on exterior+interior metric | `grut/shadow.py` |
| Shadow computation | Shadow radius and shape prediction | `grut/shadow.py` |
| Photon sphere check | Location relative to Schwarzschild | output |
| PACKET_SHADOW_v0.1 | Evidence packet (when ready) | `tools/build_shadow_packet.py` |

### Missing Equations

1. Null geodesic equation on the GRUT spacetime
2. Impact parameter — deflection angle relation
3. Inner boundary condition for geodesics hitting the core
4. Shadow edge condition

---

## Recommended Execution Order

```
WP1 (Exterior Matching)     — FIRST
  │
  ├── Critical dependency: WP2 and WP3 need the exterior metric.
  │   If exterior = exact Schwarzschild, then WP3 (shadow) is trivially
  │   answered (no deviation). WP2 (ringdown) depends on interior
  │   boundary condition which comes from the matching analysis.
  │
  ▼
WP2 (Ringdown / Echo)       — SECOND
  │
  ├── Depends on WP1 for the interior metric and boundary condition.
  │   The reflection coefficient at R_eq determines whether echoes exist.
  │   This is the highest-impact falsifier: LIGO can constrain it.
  │
  ▼
WP3 (Shadow / Accretion)    — THIRD
  │
  └── If WP1 shows exterior = Schwarzschild, WP3 is trivially answered
      (no shadow deviation). Only non-trivial if WP1 finds exterior
      deviations or if interior emission matters for accretion.
```

**Rationale**: WP1 is the gateway. It determines whether there ARE
exterior deviations. If the exterior is exactly Schwarzschild, then
WP3 produces null results and WP2 is the only channel for falsification
(through interior echoes). If WP1 finds deviations, all three WPs become
active.

---

## Files / Modules / Packets to Build Next

| Priority | File | Purpose | Dependencies |
|----------|------|---------|-------------|
| 1 | `grut/exterior_matching.py` | Junction conditions, Birkhoff analysis | collapse.py |
| 2 | `docs/EXTERIOR_MATCHING_MEMO.md` | Derivation of matching conditions | WP1 results |
| 3 | `grut/ringdown.py` | Effective potential, reflection solver | exterior_matching.py |
| 4 | `grut/shadow.py` | Null geodesic solver, shadow computation | exterior_matching.py |
| 5 | `tools/build_ringdown_packet.py` | PACKET_RINGDOWN_v0.1 builder | ringdown.py |
| 6 | `tools/build_shadow_packet.py` | PACKET_SHADOW_v0.1 builder | shadow.py |
| 7 | `benchmark_phase3c_exterior.py` | Phase III-C acceptance audit | all WP modules |

---

## Explicit Nonclaims

1. **No exterior observable predictions exist yet.** This roadmap defines
   the program to compute them, but no calculation has been performed.

2. **No ringdown, echo, shadow, or accretion computation has been done.**
   The deliverables listed above are targets, not results.

3. **The interior endpoint candidate does not by itself predict exterior
   behavior.** Explicit matching is required. The default assumption is
   that Birkhoff's theorem makes the exterior Schwarzschild, but this must
   be verified for the GRUT memory coupling.

4. **No claim is made about observational distinguishability.** Whether
   the Whole Hole candidate can be distinguished from a classical black
   hole by current or near-future instruments is an open question that
   WP2 and WP3 are designed to answer.

5. **The Newtonian-gauge interior endpoint has not been verified in a
   covariant treatment.** The matching analysis (WP1) will partially
   address this, but a full TOV treatment remains needed.

6. **Kerr generalization is not attempted.** All work is in the
   non-rotating (Schwarzschild) limit. Rotation adds angular momentum
   and frame-dragging, which require separate treatment.

7. **The information paradox is NOT solved.** The information ledger
   skeleton exists but conservation is untested. Exterior accessibility
   of information (archive status) depends on WP1 results.

---

## Success Criteria for Phase III-C

Phase III-C will be considered complete when:

1. WP1 delivers a clear answer: does the exterior differ from Schwarzschild,
   and if so, by how much?

2. WP2 delivers: either a clean echo/ringdown prediction (with amplitude
   and timing), or a proof that echoes are suppressed below observable
   thresholds.

3. WP3 delivers: either a shadow deviation prediction, or confirmation
   that the shadow is indistinguishable from Schwarzschild.

4. All results are packaged in evidence packets with explicit nonclaims,
   NIS certificates, and status-gated language.

5. No result overclaims. "No observable deviation" is a valid and
   informative result.
