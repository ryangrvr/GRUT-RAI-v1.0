# Phase III Closure and State of the Theory

**DATE**: 2026-03-12
**CANON VERSION**: v0.3.6
**STATUS**: PHASE III FROZEN — effective-level covariant framework established;
first-principles closure remains open

---

## What Phase III Achieved

Phase III took the GRUT framework from a phenomenological operator stack
to a structurally closed effective theory across two sectors. The work
proceeded in four stages:

1. **Phase III-A/B** (barrier dominance, endpoint law, transition profile):
   Established the constrained endpoint law ε_Q = α²_vac = 1/9, β_Q = 2,
   yielding R_eq/r_s = 1/3 as the candidate equilibrium. Introduced the
   transition order parameter Φ and validated sharp-boundary approximation
   (grading factor 0.996, < 1% correction).

2. **Phase III-C** (PDE closure, WP3 null result):
   Derived the interior PDE from ODE linearisation around the BDCC
   equilibrium. Identified the structural identity ω₀τ = 1 (exact within
   the PDE closure framework) and the universal quality factor Q = β_Q/α_vac = 6.
   Reclassified the interior from reactive_candidate (Q ≈ 515, proxy —
   superseded) to mixed_viscoelastic (Q ≈ 6–7.5, leading). Confirmed WP3
   static exterior null result under Schwarzschild-like assessment.

3. **Phase III-C covariant pass** (effective metric ansatz):
   Constructed an effective interior metric and verified that the PDE
   structural identity, quality factor, and mixed_viscoelastic classification
   survive metric corrections. Reflection coefficient modified ±21% by
   the effective metric; echo channel surviving at ~1.1%.

4. **Phase III Final** (covariant field equations):
   Evaluated three candidate covariant formulations for the memory sector.
   Selected the auxiliary scalar field as the preferred effective framework.
   Established weak-field and strong-field recovery at the effective level.
   Confirmed Bianchi compatibility at the effective level. Documented 7
   remaining closures and 12 explicit nonclaims.

The result is a structurally self-consistent effective theory that recovers
both the cosmological and collapse solvers from a single covariant relaxation
equation, τ_eff u^α ∇_α Φ + Φ = X[g, T]. This is the best current covariant
formulation. It is not a first-principles derivation.

---

## 1. LOCKED / OPERATIONAL

Items in this category are implemented, tested, and verified within the
current framework. They represent operational code, confirmed structural
identities, or analysis-complete results that do not depend on the open
closures for their validity within their stated scope.

### 1.1 Weak-Field Memory Sector

The cosmological memory sector is implemented in `grut/engine.py` and
governed by the operator stack defined in `grut/operators.py`.

**Memory ODE**:

    τ_eff dM_X/dt + M_X = H²_base

solved via exact exponential update M_new = M·e^(−dt/τ_eff) + X·(1 − e^(−dt/τ_eff)).

**Modified Friedmann equation**:

    H² = (1 − α_mem) H²_base + α_mem · M_X

with α_mem ≈ 0.1 (tunable cosmological weighting).

**τ_eff coupling**:

    τ_eff(H) = τ₀ / (1 + (H τ₀)²)

This makes the memory window contract during rapid expansion and relax
toward τ₀ during slow expansion. The coupling is what makes GRUT a
dynamical theory rather than a constant-parameter extension of ΛCDM.

**Operator stack**: OP_GENESIS → OP_S_PHASE → OP_L_STIFF → OP_DISSIPATION →
OP_TAU_COUPLING → OP_GROWTH_LINEAR. Each operator is individually tested
and the full stack is deterministically reproducible.

**Status**: LOCKED. Operational since Phase 2.

### 1.2 Quantum Bridge Falsifier Program

The exterior falsifier program (WP1–WP3) was designed to identify
observable channels through which the BDCC interior could be tested.

- **WP1** (exterior matching): Schwarzschild-like exterior at leading order,
  conditional on M_drive being matter-local and OP_QPRESS_001 having no
  exterior gravitational self-energy. Birkhoff status: preserved_candidate.
  Confidence: moderate.

- **WP2** (ringdown/echo): Frozen candidate falsifier channel. Echo delay
  ~0.52 ms at 30 M☉, echo amplitude ~1.1% of QNM signal under PDE closure.
  Mixed_viscoelastic interior (Q ≈ 6–7.5). Sharp-boundary approximation
  validated (grading factor 0.996).

- **WP3** (shadow/accretion): Analysis complete — null at leading order.
  Shadow, photon sphere, ISCO, radiative efficiency, Eddington luminosity,
  and disk spectrum are all identically standard Schwarzschild. The BDCC
  at R_eq = r_s/3 is causally disconnected from all static exterior observables
  at r > r_s.

**Status**: LOCKED as analysis framework. Individual results carry their
own confidence levels (see Section 2 for candidate items).

### 1.3 Artifact Rejection in the Collapse Sector

The collapse solver (`grut/collapse.py`) includes explicit artifact
diagnostics:

- **L_stiff artifact prediction**: R_artifact = (V_tol² · 2GM / H²_cap)^(1/3) / r_s.
  Any arrest at R ≈ R_artifact is classified as an L_stiff artifact, not
  physical saturation.

- **Bounce exclusion**: Two-tier result.
  - *Tier 1* (weak gravity, M ≲ 10²⁴ kg): Sign-definite. M_drive > 0,
    a_net > 0 throughout. V ≤ 0 for all time. Structural.
  - *Tier 2* (astrophysical masses, M ≳ 10³⁰ kg): M_drive can go
    transiently negative. a_net can become negative at some timesteps.
    No-bounce persists numerically but the mechanism differs. Conditional.

- **Collapse classification**: stall, arrested_prehorizon, arrested_posthorizon,
  plunging, singular — each with diagnostic criteria.

**Status**: LOCKED. Artifact rejection operational and tested across mass range.

### 1.4 Primary Transition Order Parameter Φ

The transition profile at the BDCC boundary is modeled by a power-law
order parameter:

    Φ(t) = 1 − t^0.426

calibrated in Phase III-B. The transition-width correction to the sharp-boundary
impedance model is a grading factor of 0.996 (< 1% correction). Multi-mode
corrections are negligible (factor 0.99999). The sharp-boundary model is
confirmed as an excellent approximation.

**Status**: LOCKED as zeroth-order transition model.

### 1.5 Mixed-Viscoelastic Interior (PDE/Covariant Effective Closure)

The interior PDE dispersion relation, derived from linearisation of the
collapse ODE system around the BDCC equilibrium:

    ω² = ω₀² + 2α ω²_g / (1 + iωτ)

yields the structural identity ω₀ · τ_local = 1.0 (exact within the PDE closure,
mass-independent) and the universal quality factor Q = β_Q / α_vac = 6.0.

The covariant pass (effective metric ansatz) confirms that eigenfrequencies
are zeros of the PDE dispersion relation F(ω) = 0, independent of the
effective sound speed c_eff. The covariant wavevector relation is
k² = F_PDE(ω) / c²_eff, so the PDE structural identity survives.

**Key numbers at 30 M☉**:

| Quantity | PDE | Covariant |
|----------|-----|-----------|
| Q | 7.46 | ~6.5 |
| r_amp | 0.303 | 0.367 |
| Echo amplitude | ~1.1% | ~1.1% |
| ω₀ × τ | 1.0 | 1.0 |
| Response class | mixed_viscoelastic | mixed_viscoelastic |

**Status**: LOCKED as best current interior characterisation within the
effective closure framework.

### 1.6 Static Exterior Null Map

Under the Schwarzschild-like exterior assessment (WP1):

| Observable | Result | Mechanism |
|-----------|--------|-----------|
| Shadow (b_crit) | IDENTICALLY NULL | b_crit = 3√3 M, standard Schwarzschild |
| Photon sphere (r_ph) | IDENTICALLY NULL | r_ph = 3M = (3/2) r_s |
| ISCO (r_ISCO) | IDENTICALLY NULL | r_ISCO = 6M = 3 r_s |
| Radiative efficiency | IDENTICALLY NULL | η = 1 − √(8/9) ≈ 5.72% |
| Eddington luminosity | IDENTICALLY NULL | L_Edd depends only on M |
| Disk spectrum | IDENTICALLY NULL | Novikov–Thorne, exterior metric only |

The BDCC at R_eq = r_s/3 (compactness C = 3) is inside the horizon. All
static observables are determined by the exterior metric at r > r_s. Causal
argument: the BDCC has no influence on these at leading order.

**Undetermined**: Tidal Love numbers (potential non-null), echo–accretion
coupling (second-order at ~1%).

**Status**: LOCKED as null result within scope. Conditional on WP1.

### 1.7 Effective Cross-Sector Recovery Structure

The covariant field equation framework (Candidate 2 — auxiliary scalar field)
recovers both GRUT sectors from a single relaxation equation:

    τ_eff u^α ∇_α Φ + Φ = X[g, T]

with the combined conservation constraint ∇_μ(T^μν + T^Φ_μν) = 0.

| | Cosmological | Collapse |
|---|---|---|
| Φ | M_X | M_drive |
| X (driver) | H²_base | a_grav = GM/R² |
| α (coupling) | α_mem ≈ 0.1 | α_vac = 1/3 |
| τ_eff | τ₀/(1 + (Hτ₀)²) | τ_local/(1 + H²_coll τ²_local) |

Weak-field reduction recovers the modified Friedmann equation and memory ODE.
Strong-field reduction recovers the collapse force balance, endpoint law,
structural identity, and PDE dispersion relation. All reductions are at the
effective level — they recover the current solver structure, they do not
derive it from first principles.

**Status**: LOCKED as effective-level structural result.

---

## 2. CONSTRAINED / CANDIDATE

Items in this category are structurally motivated, internally consistent,
and constrained by the effective framework — but not derived from first
principles. They could shift under a deeper theory or alternative closures.

### 2.1 Constrained Endpoint Law

    ε_Q = α²_vac = 1/9,    β_Q = 2

This yields the equilibrium radius R_eq/r_s = ε_Q^(1/β_Q) = 1/3. The law
is consistent with the covariant framework, with the structural identity
ω₀τ = 1, and with the universal Q = 6. It is not derived from the field
equations or from an action principle. It enters the framework as a
constrained parametric choice motivated by the barrier dominance analysis.

**Status**: CONSTRAINED. Internally consistent, not derived.

### 2.2 Candidate Endpoint R_eq / r_s = 1/3

The equilibrium radius at one-third of the Schwarzschild radius is the
candidate BDCC endpoint under the constrained law. It places the core
inside the horizon (compactness C = 3), below the photon sphere, below
the ISCO, and causally disconnected from all static exterior observables.

The endpoint is a consequence of the parametric choice ε_Q = 1/9, β_Q = 2,
not an independent derivation. If the constrained law changes, the endpoint
changes.

**Status**: CANDIDATE. Conditional on the constrained endpoint law.

### 2.3 Ringdown Echo Channel

The echo channel is the only non-null observable identified within the
current framework. Under the PDE/covariant effective closure:

- Echo time delay: ~0.52 ms at 30 M☉ (order of magnitude)
- Echo amplitude: ~1.1% of main QNM signal
- Reflection coefficient: r_PDE ≈ 0.30, r_cov ≈ 0.37
- Quality factor: Q ≈ 6–7.5 (mixed_viscoelastic, mass-independent)
- Δt_echo / r_s = 1.76 (dimensionless, mass-independent)

The channel is weakened from the superseded proxy estimate (~3.7%, Q ≈ 515,
reactive_candidate) but not collapsed. The Boltzmann model (r_amp ≈ 0)
remains viable if the BDCC is dissipative. No prediction is made that
echoes exist — the module computes what they would look like under
the current assumptions.

**Status**: CANDIDATE FALSIFIER CHANNEL. Frozen, weakened but surviving.

### 2.4 Auxiliary Memory Field (Preferred Effective Covariant Framework)

Candidate 2 — auxiliary memory field (scalarized first pass):

    G_μν = (8πG/c⁴)(T_μν + T^Φ_μν)
    τ_eff u^α ∇_α Φ + Φ = X[g, T]

Selected as preferred on the grounds of:

- **Structural adequacy**: Has independent dynamics (unlike algebraic tensor,
  Candidate 1, which cannot capture retardation).
- **Minimality**: Scalar is the minimal covariant object carrying the existing
  memory degree of freedom. It maps directly onto both sector ODEs.
- **Implementability**: Local realisation of the exponential retarded kernel
  K(s) = (1/τ)exp(−s/τ)Θ(s) along the chosen observer flow u^α. Does not
  require the full nonlocal integral machinery (Candidate 3) for the current
  single-observer, single-mode solver structure.
- **Bianchi compatibility**: Combined conservation ∇_μ(T^μν + T^Φ_μν) = 0
  at the effective level.

T^Φ_μν is schematic and effective throughout — it is the placeholder for
whatever contribution the memory field makes to the gravitational source
terms. Its explicit form (ρ_Φ, p_Φ, anisotropic stress) has not been
derived from a Lagrangian.

**Status**: PREFERRED EFFECTIVE FRAMEWORK. Not a first-principles result.

---

## 3. FUNDAMENTALLY OPEN

Items in this category are necessary for a complete first-principles theory
but are not addressed by the current effective closure. They are not
missing due to oversight — they are explicitly flagged as the boundary
of the current analysis.

### 3.1 Explicit Memory Stress-Energy Tensor T^Φ_μν

T^Φ_μν appears in the field equation G_μν = (8πG/c⁴)(T_μν + T^Φ_μν) but
is schematic. Its components (energy density ρ_Φ, pressure p_Φ, anisotropic
stress) have not been specified. Deriving T^Φ_μν from a covariant action
is the single most important open closure.

### 3.2 Action-Level / Lagrangian Derivation

The field equation framework is constructed to be consistent with the
existing solver, not derived from a variational principle. A Lagrangian
for the coupled gravity + matter + memory system would:
- Fix T^Φ_μν uniquely
- Prove (not assume) Bianchi compatibility
- Determine whether the memory field propagates or only relaxes
- Constrain the τ_eff(curvature) dependence

### 3.3 Tensorial Memory-Sector Generalisation

The scalar memory field is the minimal closure. A tensorial memory field
(rank-2 or higher) would be required for:
- Anisotropic memory effects
- Propagating memory (gravitational-wave–memory coupling)
- Memory contributions to the Weyl tensor
- Situations where the single-scalar approximation breaks down

Whether the memory is fundamentally scalar or tensorial is an open
ontological question.

### 3.4 Junction Conditions

Israel junction conditions with the memory field at the BDCC transition
boundary have not been derived. The current treatment uses an effective
impedance matching (sharp boundary or graded Φ profile) that does not
follow from the covariant field equations. Proper junction conditions
would determine:
- Whether the memory field is continuous or discontinuous at R_eq
- The matching of T^Φ_μν across the boundary
- Corrections to the reflection coefficient beyond the impedance ansatz

### 3.5 Kerr Extension

All results are for non-rotating (Schwarzschild) black holes. The Kerr
extension requires:
- Modification of the BDCC equilibrium for angular momentum
- Spin-dependent corrections to the structural identity
- Kerr quasi-normal mode spectrum as the reference signal
- Boyer–Lindquist or Kerr–Schild coordinates for the interior

### 3.6 Tidal Love Numbers

Tidal Love numbers for standard GR black holes are exactly zero
(TLN = 0). A reflecting boundary at R_eq could break this, making TLN
a potential non-null observable — distinct from the echo channel. This
has not been computed.

### 3.7 Nonlinear Mode Coupling

The current analysis is linearised (single-mode perturbation theory around
the BDCC equilibrium). Nonlinear coupling between modes could:
- Transfer energy between overtones
- Modify the echo decay envelope
- Break the universal-Q prediction at large perturbation amplitudes

---

## What Remains for Final First-Principles Closure

The distance between the current effective framework and a complete
first-principles theory can be summarised as follows:

| Gap | What it would resolve | Difficulty |
|-----|----------------------|------------|
| Covariant action for memory sector | T^Φ_μν, Bianchi proof, propagation | High |
| τ_eff(curvature) derivation | Which curvature invariant controls τ | Medium |
| α_mem / α_vac unification | Whether one coupling underlies both sectors | Medium |
| Tensorial vs scalar memory | Final memory ontology | High |
| Junction conditions at R_eq | Reflection from field equations | Medium |
| Kerr | Rotating black holes | High |
| Love numbers | Second non-null observable | Medium |
| Nonlinear coupling | Beyond linear perturbation theory | Medium |

The α_mem (cosmological, ≈ 0.1) and α_vac (collapse, 1/3) couplings are
treated as distinct symbols. Whether they are manifestations of a single
scale-dependent coupling α_eff(curvature, scale) remains an active research
target. The current framework does not unify them and does not declare
them fundamentally distinct.

---

## Repository Status

| Metric | Value |
|--------|-------|
| Canon version | v0.3.6 |
| GRUTipedia edition | 8 |
| Tests: test_field_equations.py | 30 passed |
| Tests: test_collapse.py (Phase III targeted) | 46 passed |
| Benchmark: field equations | 96/96 CLEAN |
| Benchmark: covariant closure | 93/93 CLEAN |
| Full test suite | Green (zero regressions) |

### Key files

| File | Role |
|------|------|
| `grut/engine.py` | Cosmological memory sector |
| `grut/operators.py` | Operator stack definitions |
| `grut/collapse.py` | Radial collapse solver with barrier and memory |
| `grut/interior_pde.py` | Interior PDE (dispersion, structural identity, Q) |
| `grut/interior_covariant.py` | Covariant interior (effective metric ansatz) |
| `grut/field_equations.py` | Covariant field equation framework (3 candidates) |
| `grut/ringdown.py` | Echo channel (parameterised + impedance + PDE + covariant) |
| `grut/exterior_matching.py` | WP1 exterior matching |
| `grut/interior_waves.py` | WP2C proxy (superseded, retained as baseline) |
| `docs/PHASE_III_FINAL_FIELD_EQUATIONS.md` | Field equation theory memo |
| `docs/PHASE_III_C_COVARIANT_CLOSURE.md` | Covariant closure memo |
| `docs/PHASE_III_C_WP3_NULL_RESULT.md` | WP3 null-result analysis |
| `canon/grut_canon_v0.3.json` | Canon (v0.3.6) |

---

## Nonclaims

The following statements are explicit boundaries on what Phase III does
and does not establish. They are drawn from the covariant closure pass,
the field equation analysis, and the sector-specific work packages.

1. Phase III does NOT derive the GRUT field equations from first principles
   or a covariant action.

2. T^Φ_μν is SCHEMATIC / EFFECTIVE — not a fully specified stress-energy
   tensor derived from a Lagrangian.

3. The scalar memory field is the MINIMAL implementable closure, not the
   final memory ontology. Tensorial generalisation remains open.

4. α_mem / α_vac distinction is an OPEN QUESTION. They are treated as
   distinct symbols; unification is an active research target.

5. Bianchi compatibility is established at the EFFECTIVE LEVEL — not
   proven from variational principles or a derived conservation law.

6. The nonlocal equivalence between Candidates 2 and 3 holds along the
   chosen observer flow for exponential kernels. It is NOT claimed
   globally in all covariant settings.

7. Weak-field and strong-field reductions RECOVER the current solver
   structure at the effective level. They do NOT derive the solver from
   the field equations.

8. Candidate 1 rejection applies to ALGEBRAIC memory tensors — a
   dynamical tensor field remains a possible formulation.

9. The constrained endpoint law (ε_Q = α²_vac, β_Q = 2, R_eq/r_s = 1/3)
   is CONSISTENT with the field equation framework but NOT derived from it.

10. The structural identity ω₀ × τ = 1 is exact within the current PDE
    closure framework. It is NOT claimed as a universal law independent
    of the closure used.

11. Kerr, tidal Love numbers, and Israel junction conditions are NOT
    attempted.

12. No detector-level or observational predictions are made. The echo
    channel computes what echoes WOULD look like under current assumptions.

13. The covariant interior metric ansatz is NOT derived from the GRUT
    field equations. It is an effective ansatz constructed to be consistent
    with the solver.

14. The PDE closure is approximate — derived from ODE linearisation, not
    a covariant wave equation on the GRUT metric.

15. The pre-PDE proxy result (Q ≈ 515, reactive_candidate, echo ≈ 3.7%)
    is SUPERSEDED. It is retained as a historical baseline, not a current
    estimate.

16. mixed_viscoelastic is the best current candidate classification, NOT
    the final answer. Alternative closures may shift Q.

17. The Boltzmann model (r_amp ≈ 0) remains viable if the BDCC is
    dissipative. The current framework does not exclude it.

18. All WP3 null results are CONDITIONAL on the WP1 Schwarzschild-like
    exterior assessment. If the exterior is modified, all null results
    require re-evaluation.

19. No result in this document is promoted to final canon in a
    first-principles sense. The framework is effective, bounded, and
    honest about its own limitations.
