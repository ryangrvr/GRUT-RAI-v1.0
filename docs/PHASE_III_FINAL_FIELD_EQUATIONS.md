# Phase III Final: Covariant GRUT Field Equations

**DATE**: 2026-03-11
**STATUS**: FIRST COVARIANT PASS — auxiliary memory field (scalarized first pass)
**CONDITIONAL ON**: Current GRUT operator stack, constrained endpoint law
**NOT**: First-principles derivation from a covariant action

---

## A. Closure Target

The GRUT framework currently operates through two phenomenological ODE systems:

**Cosmological sector** (`grut/engine.py`):
```
τ_eff dM_X/dt + M_X = H²_base
H² = (1 − α_mem) H²_base + α_mem M_X
τ_eff(H) = τ₀ / (1 + (H τ₀)²)
```

**Collapse sector** (`grut/collapse.py`):
```
dM_drive/dt = (a_grav − M_drive) / τ_eff
a_eff = (1 − α_vac) a_grav + α_vac M_drive
τ_eff = τ_local / (1 + H²_coll τ²_local)
```

These are first-order relaxation equations, not covariant field equations.
Neither system follows from a gravitational field equation. Both enter the
solver as effective operator insertions.

**The closure target**: determine the most honest covariant field-equation
framework consistent with:
- The weak-field lag / retarded-memory behavior
- The strong-field saturation / endpoint behavior (ε_Q = α²_vac, β_Q = 2, R_eq/r_s = 1/3)
- Combined conservation of matter + memory (Bianchi compatibility at the effective level)
- The structural identity ω₀ τ = 1 and universal Q = 6

**This memo does NOT claim**: a first-principles derivation of the GRUT
field equations from a covariant action. It evaluates three candidate
formulations for structural adequacy and selects the one that is most
internally consistent and implementable as a bounded first pass.

---

## B. Candidate 1 — Algebraic Memory Tensor

**Formulation**:

    G_μν = (8πG/c⁴) (T_μν + T^mem_μν)

where T^mem_μν is algebraically determined from the metric and matter
content, with no independent dynamical equation.

**Assessment**: INSUFFICIENT.

**Why**: GRUT's memory has its own first-order relaxation dynamics with a
characteristic timescale τ_eff. An algebraically determined tensor responds
instantaneously — it tracks the metric with zero delay. This is structurally
equivalent to a modified gravity theory (e.g., f(R) or Brans-Dicke with no
kinetic term) and cannot reproduce:
- The retardation/lag behavior that defines GRUT's cosmological memory
- The relaxation toward gravitational acceleration in the collapse sector
- The frequency-dependent susceptibility χ(ω) = 2αω²_g / (1 + iωτ)

An algebraic memory tensor has no ω-dependence, no τ_eff, and no damping
channel. It collapses the GRUT memory structure to an instantaneous
effective equation of state modification. This is not what GRUT is.

**Verdict**: Candidate 1 is structurally insufficient. Rejected.

---

## C. Candidate 2 — Auxiliary Memory Field (Scalarized First Pass)

**Formulation**:

    G_μν = (8πG/c⁴) (T_μν + T^Φ_μν)

together with a covariant relaxation equation for the memory field Φ:

    τ_eff u^α ∇_α Φ + Φ = X[g, T]

where:
- Φ is a scalar memory field (first pass; tensorial generalization remains open)
- u^α is the matter 4-velocity (or normal observer field)
- X[g, T] is the "driver" functional — the quantity that Φ tracks with delay
- τ_eff is the effective relaxation timescale (depends on local dynamics)
- T^Φ_μν is the effective stress-energy associated with the memory field

**Status of T^Φ_μν**: SCHEMATIC / EFFECTIVE. The current pass supports an
ansatz-level effective form, NOT a fully specified stress-energy tensor
derived from a covariant action. T^Φ_μν is the placeholder for whatever
contribution the memory field makes to the gravitational source terms.
Its explicit form (ρ_Φ, p_Φ, anisotropic stress) remains an open closure.

**Mapping to existing sectors**:

| | Cosmological | Collapse |
|---|---|---|
| Φ | M_X | M_drive |
| X (driver) | H²_base | a_grav = GM/R² |
| α (coupling) | α_mem (tunable, ~0.1) | α_vac (fixed, 1/3) |
| τ_eff | τ₀/(1+(Hτ₀)²) | τ_local/(1+H²_coll τ²_local) |
| Memory ODE | τ_eff dM_X/dt + M_X = H²_base | dM_drive/dt = (a_grav−M_drive)/τ_eff |

**Why scalar (first pass)**: The existing memory state in both sectors is a
single scalar quantity (M_X or M_drive). A scalar field is the minimal
covariant object that can carry this degree of freedom with first-order
relaxation dynamics. A tensorial memory field would be needed for anisotropic
or propagating memory effects, but the current solver structure does not
constrain that generalization. Scalar is the honest minimal closure.

**Note on α_mem vs α_vac**: These are treated as distinct symbols in the
current framework. α_vac = 1/3 has stronger canonical status (constrained
endpoint law). α_mem = 0.1 is a tunable cosmological weighting. Whether
they are manifestations of a single scale-dependent coupling α_eff(curvature)
remains an ACTIVE RESEARCH TARGET. This memo does not unify them.

**Verdict**: Candidate 2 is the preferred formulation for the current pass.

---

## D. Candidate 3 — Nonlocal Retarded Kernel

**Formulation**:

The field equations involve a causal integral kernel:

    G_μν(x) + ∫ K(x, x′) S_μν(x′) √(−g′) d⁴x′ = (8πG/c⁴) T_μν(x)

where K(x, x′) is a retarded kernel with support only on the past
light cone (or within the past worldline for the comoving formulation),
and S_μν is a geometric source term.

For the exponential kernel K(s) = (1/τ_eff) exp(−s/τ_eff) Θ(s) along
a chosen observer flow u^α, the integral equation is equivalent to the
auxiliary scalar field + first-order ODE of Candidate 2. This equivalence
is the standard Markovian embedding: introducing Φ(t) = ∫₀^t K(t−s) X(s) ds
and differentiating once yields τ_eff dΦ/dt + Φ = X(t).

**Scope of equivalence**: The auxiliary-field relaxation of Candidate 2 is
the LOCAL REALIZATION of the exponential retarded kernel ALONG THE CHOSEN
OBSERVER FLOW u^α. This equivalence is exact for the single-observer,
single-mode structure of the current solver. It does NOT claim global
equivalence in all covariant settings — multi-observer, multi-mode, or
non-exponential kernel generalizations would require the full nonlocal
treatment.

**Verdict**: Candidate 3 is the formal parent of Candidate 2. It becomes
the required formulation only if the kernel is generalized beyond
exponential, or if the multi-observer structure becomes relevant.
For the current pass: Candidate 2 suffices.

---

## E. Conservation Structure

**Fundamental statement**: Combined conservation of the matter + memory sector.

    ∇_μ (T^μν + T^Φ_μν) = 0

This is required by the contracted Bianchi identity ∇_μ G^μν = 0 and the
Einstein equation G_μν = (8πG/c⁴)(T_μν + T^Φ_μν). It is NOT separately
imposed; it is a consequence of the geometric identity.

**Status**: COMPATIBLE AT THE EFFECTIVE LEVEL. The current pass establishes
that the candidate formulation is structurally compatible with combined
conservation. This is NOT a fully derived conservation structure from a
covariant action. A candidate may be structurally compatible without being
proven from variational principles.

**Sector-by-sector analysis**:

**Cosmological sector**: In the current solver (`engine.py`), matter evolves
via the standard continuity equation dρ/dt = −3H(1+w)ρ with the memory-
corrected Hubble rate. The memory modifies H but does not directly source
or sink matter. This is CONSISTENT WITH (but does not prove) separate
conservation ∇_μ T^μν_matter = 0 in this regime. If matter is separately
conserved, then ∇_μ T^Φ_μν = 0 must also hold. This is an approximation
valid in the weak-field / slow-memory regime, NOT a general result.

**Collapse sector**: The force balance a_eff = (1−α)a_grav + αM_drive − a_Q
implies energy exchange between the gravitational field, memory state, and
barrier sector. The individual components are NOT separately conserved.
Only the combined system satisfies the conservation constraint. This is
consistent with the fundamental statement ∇_μ(T^μν + T^Φ_μν) = 0 where
the barrier contribution is absorbed into T^Φ_μν or into an additional
T^Q_μν term.

---

## F. Weak-Field Reduction

Under the weak-field (FLRW) limit with spatially homogeneous Φ:

1. The relaxation equation τ_eff u^α∇_αΦ + Φ = X reduces to
   τ_eff dΦ/dt + Φ = H²_base (exact match to engine.py memory ODE)

2. The modified Friedmann equation H² = (1−α_mem)H²_base + α_mem Φ
   recovers at the effective level (matches engine.py line 211)

3. The τ-coupling τ_eff(H) = τ₀/(1 + (Hτ₀)²) recovers at the effective
   level (matches operators.py lines 33-35)

4. The linear growth equation uses the memory-corrected H as input,
   consistent with the current solver structure

**Caution**: This is a recovery check, not a derivation. The field equation
formulation is constructed to be consistent with the existing solver. It
does not prove that the solver follows from first principles.

---

## G. Strong-Field Reduction

Under the strong-field (spherically symmetric collapse) limit:

1. The memory relaxation τ_eff dΦ/dt + Φ = a_grav reduces to the collapse
   ODE dM_drive/dt = (a_grav − M_drive)/τ_eff (matches collapse.py line 209)

2. The force balance a_eff = (1−α_vac)a_grav + α_vac M_drive recovers
   at the effective level (matches collapse.py force decomposition)

3. The constrained endpoint law ε_Q = α²_vac = 1/9, β_Q = 2, R_eq/r_s = 1/3
   is consistent with the equilibrium condition of the coupled system

4. The PDE dispersion relation ω² = ω₀² + 2αω²_g/(1+iωτ) arises from
   linearizing the memory relaxation around equilibrium, consistent with
   the current interior PDE closure

5. The structural identity ω₀τ = 1 is preserved because it depends on
   the dispersion relation zeros, not on the covariant formulation details

**Caution**: Same as weak-field — this is a consistency check with the
current solver structure, not a first-principles derivation.

---

## H. Preferred Formulation and Remaining Closures

**Preferred**: Candidate 2 — auxiliary memory field (scalarized first pass).

**Rationale**:
- Minimal covariant object carrying the existing memory degree of freedom
- Maps directly onto both sector ODEs without modification
- Structurally compatible with combined Bianchi conservation
- Local realization of the exponential retarded kernel along observer flow
- Implementable and testable within the current codebase

**What Candidate 2 resolves**:
1. A covariant field equation framework that accommodates both sectors
2. The structural form of the memory relaxation in covariant language
3. That Candidate 1 (algebraic tensor) is structurally insufficient
4. That Candidate 3 (nonlocal kernel) reduces to Candidate 2 for exponential kernels along a single observer flow
5. Effective-level Bianchi compatibility

**Remaining closures** (7):
1. Explicit form of T^Φ_μν — the memory stress-energy is schematic/effective, not specified from a Lagrangian
2. Curvature dependence of τ_eff — whether τ_eff depends on Ricci scalar, Kretschner, or other invariants
3. Propagation equation for Φ beyond local relaxation — whether the memory field propagates (wave equation?) or only relaxes
4. Israel junction conditions with memory field — matching at transition boundary
5. Kerr extension — spin effects
6. Tidal Love numbers — static perturbation with memory
7. Nonlinear mode coupling — beyond linear perturbation theory

**Structural open questions** (not closures, but deeper):
- Whether α_mem and α_vac are the same coupling in different regimes
- Whether the memory field is fundamentally scalar or tensorial
- Whether the exponential kernel is the unique natural choice or a simplification
- Whether the field equations follow from a covariant action principle

---

## I. Nonclaims

1. This memo does NOT derive the GRUT field equations from first principles or a covariant action
2. T^Φ_μν is SCHEMATIC / EFFECTIVE — not a fully specified stress-energy tensor
3. The scalar field is the MINIMAL implementable closure, not the final memory ontology — tensorial generalization remains open
4. The α_mem / α_vac distinction is an OPEN QUESTION, not resolved
5. Bianchi compatibility is established at the EFFECTIVE LEVEL, not from a fully derived conservation structure
6. The nonlocal equivalence (Candidate 2 ↔ 3) holds ALONG THE CHOSEN OBSERVER FLOW for exponential kernels — not claimed globally
7. Weak-field and strong-field reductions RECOVER the current solver structure — they do NOT prove the solver follows from the field equations
8. Candidate 1 is rejected as structurally insufficient, but this conclusion applies to ALGEBRAIC memory tensors — a dynamical tensor field remains possible
9. The constrained endpoint law (ε_Q = α²_vac, β_Q = 2) is CONSISTENT with the formulation but NOT derived from it
10. Kerr, tidal Love numbers, and junction conditions are NOT attempted
11. No detector-level or observational predictions are made
12. This is a bounded assessment, not a final theory
