# GRUT-RAI v1.0 Release Notes

## Release Identity

**GRUT-RAI v1.0 — Canonical Build (Phases I–III Complete)**

Date: 2026-03-12

---

## What v1.0 Is

The first serious GRUT-RAI release synchronized to the completed Phase I–III
canon.  Every AI-facing reference, default parameter, classification string,
and status label is aligned to the final Phase III state.

What v1.0 is NOT:
- Not a final first-principles closure of all GRUT
- Not the final ontology of the memory sector
- Not the end of theory development

---

## What Changed from Pre-v1.0 Builds

### Version Identity
- Engine version: `grut-rai-v1.0` (was `grut-rai-2026.1-phaseE-portal`)
- Default engine version in GRUTEngine: `GRUT-RAI-v1.0` (was `GRUT-RAI-v0.2`)
- Package docstring: `GRUT-RAI v1.0` (was `GRUT Phase 2 bootstrap package (DRAFT)`)
- Canon meta: phase `3`, status `v1.0` (was phase `2`, status `DRAFT`)
- FastAPI title updated to v1.0 identity
- README title updated to v1.0 identity

### Classification Strings (Breaking Change)
All `_candidate` suffixes removed from interior classification returns:
- `reactive_candidate` → `reactive` (Q > 10)
- `mixed_viscoelastic_candidate` → `mixed_viscoelastic` (1 < Q ≤ 10)
- `dissipative_candidate` → `dissipative` (Q ≤ 1)

Affected modules: `interior_waves.py`, `interior_pde.py`, `interior_covariant.py`

**Rationale**: The `_candidate` suffix was a relic of the pre-PDE era when the
classification was a zeroth-order proxy estimate. With the PDE closure and
covariant confirmation, the classification thresholds (Q > 10, Q > 1) are
well-established conventions. The `_candidate` suffix added confusion without
adding epistemic value.

### Default Q Fallback
- `GradedTransitionParams.quality_factor_Q`: `7.5` (was `515.6`)
- `ringdown.py` graded-transition Q fallback: `7.5` (was `515.6`)

**Rationale**: The old default (515.6) came from the pre-PDE proxy. The PDE
closure yields Q ~ 6–7.5 at canon parameters. Any code path falling back to
the default Q should use the PDE-informed value.

### System Prompt
- Added Phase III Final State section with 10 key status items
- Updated engine version fallback to `grut-rai-v1.0`
- Updated canon line to reference Phases I–III
- Added leading results: mixed_viscoelastic, ~1.1% echo, omega_0*tau=1,
  constitutive T^Phi, junction conditions, Love numbers, Kerr, action status

### Superseded-Result Banners
- `docs/PHASE_III_C_WP2C_INTERIOR_WAVES.md`: Added SUPERSEDED banner
- `docs/PHASE_III_C_WP2D_TRANSITION_WIDTH.md`: Added SUPERSEDED banner

### Benchmark Fix
- `benchmark_phase3c_wp2d_transition.py`: Updated docstring and classification
  assertion to accept both `reactive` and `mixed_viscoelastic` (reflects the
  Q value passed in, which is now 7.5 by default)

### Test Updates
- `test_classification_reactive_at_canon` renamed to
  `test_classification_reactive_at_proxy_params` with updated docstring
  marking it as testing the superseded proxy
- New test file: `tests/test_v1_release_alignment.py` (30 tests) verifying
  all v1.0 alignment criteria

---

## What Is Now Synchronized to Phases I–III

### LOCKED / OPERATIONAL
1. Weak-field memory sector structure
2. Modified Friedmann / memory ODE logic at effective level
3. Collapse artifact rejection (old L_stiff x V_tol endpoint)
4. Transition order parameter Phi
5. Mixed-viscoelastic interior (PDE closure, covariant confirmation)
6. Static exterior null map (Schwarzschild-like, WP1 conditional)
7. Effective cross-sector recovery structure
8. Constitutive-effective T^Phi_{mu nu} (Package A)
9. Effective junction conditions (Package B)

### CONSTRAINED / CANDIDATE
1. Endpoint law: epsilon_Q = alpha_vac^2, beta_Q = 2
2. Candidate endpoint: R_eq / r_s = 1/3
3. Echo channel: ~1.1% of QNM amplitude (PDE-informed)
4. Preferred field equations: auxiliary memory scalar field
5. Love numbers: k_2 ~ 0.01 (candidate non-null)
6. Kerr extension: bounded first-pass parametric estimates
7. Nonlinear coupling: bounded first-pass (Q robust for small perturbations)

### FUNDAMENTALLY OPEN
1. First-principles T^Phi_{mu nu} (action-derived)
2. Tensorial memory-sector generalization
3. Curvature dependence of tau_eff
4. alpha_mem / alpha_vac unification
5. Full junction theory from field equations
6. Full Kerr solution
7. Precise Love-number calculation

### POST-PHASE-III EXTENSIONS (future work only)
- Consciousness / observer architecture
- Particle-sector hypotheses
- Broader sector / force unification

---

## What Remains Open

The primary open target for future work is an **action-level derivation** of
the GRUT field equations. The current framework is constitutive/effective —
self-consistent and testable, but not derived from a covariant action. Three
candidate action routes have been identified (overdamped Klein-Gordon, Galley
doubled formalism, nonlocal retarded action); none has been completed.

The tensorial generalization of the memory sector (6 DOF massive symmetric
tensor vs. current 1 DOF scalar) is needed for anisotropic memory,
propagating modes, and gravitational-wave memory effects. The scalar closure
is sufficient for all Phase III results (FRW cosmology + spherical collapse).

---

## What Future Versions Will Likely Target

- **v1.1**: Canon schema v0.4 (if needed for action-level content)
- **v2.0**: Action-derived field equations (if achieved)
- **v2.x**: Tensorial memory sector, full Kerr solution, precision Love numbers
- **v3.0**: Post-Phase-III extensions (consciousness, particles, unification)

---

## Repository Statistics at v1.0

- Total test files: 30+
- Phase III modules: 10 (collapse, interior_waves, interior_pde, interior_covariant,
  field_equations, ringdown, exterior_matching, memory_tensor, junctions, observables_final)
- Phase III documents: 12
- Explicit nonclaims: 25
- Canon notes: 8 (v0.3 through v1.0)
