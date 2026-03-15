# Phase IV Package 2: Tensorial Memory-Field Program

## Status

**PHASE IV — FIRST TENSORIAL ASSESSMENT**

Classification: **SCALAR CLOSURE SUFFICIENT; TENSORIAL EXTENSION PATH IDENTIFIED**

The scalar memory field Phi is sufficient for all Phase III results (FRW
cosmology, spherical collapse, PDE dispersion, structural identity). Five
candidate tensor structures have been evaluated. The minimal tensorial
extension is a **scalar plus trace-free anisotropic stress correction**
(Phi plus sigma_{ab}), which captures shear memory without introducing
propagating tensor DOF. The full rank-2 symmetric tensor is the maximal
candidate but requires substantially more constraint equations.

---

## A. Closure Target

Determine the most honest tensorial extension beyond the scalar memory
closure. The target is NOT to build a complete tensorial field theory, but
to:

1. Classify what tensor structure is NEEDED for each missing physics sector
2. Determine whether the scalar is a symmetry-reduced limit of a deeper
   tensor
3. Identify which Phase III results survive unchanged under extension
4. Map what new physics becomes possible only with tensorial memory

---

## B. Candidate 1 — Scalar-Only Closure (Current Framework)

### Structure

One degree of freedom per sector:
- Phi = M_X (cosmological memory state, H^2 units)
- Phi = M_drive (collapse memory state, m/s^2 units)

Relaxation equation: tau u^a nabla_a Phi + Phi = X[g, T]

T^Phi_{ab} takes perfect-fluid form (FRW) or simple anisotropic form
(spherical collapse), determined constitutively by combined conservation.

### What It Captures

- FRW cosmology: isotropic memory modification of Friedmann equation
- Spherical collapse: radial memory lag in force balance
- PDE dispersion: single-mode perturbation theory (l=2 fundamental)
- Structural identity: omega_0 * tau = 1
- Mixed-viscoelastic classification: Q ~ 6-7.5
- Echo channel: ~1.1% of QNM amplitude

### What It Cannot Capture

- Anisotropic memory (shear, vorticity components)
- Propagating memory degrees of freedom
- Gravitational-wave memory effects (Christodoulou memory)
- Multi-mode angular coupling beyond single-l separation
- Full Kerr (axisymmetric, requires at least m-dependence)
- Nonperturbative merger dynamics

### Assessment

- **Status**: SUFFICIENT for all Phase III results
- **DOF**: 1 (one ODE per sector)
- **Symmetry**: consistent with isotropic (FRW) and radial (collapse)
  symmetries
- **Limitation**: cannot accommodate physics that breaks these symmetries

---

## C. Candidate 2 — Scalar + Anisotropic Stress Correction

### Structure

Extend Phi to carry an anisotropic stress correction:
- Phi (scalar, 1 DOF): isotropic memory, as before
- sigma_{ab} (trace-free symmetric, 5 DOF in 3+1 split): anisotropic
  memory stress

The total memory stress-energy becomes:
  T^Phi_{ab} = T^scalar_{ab}(Phi) + sigma_{ab}

where sigma_{ab} satisfies:
  tau u^c nabla_c sigma_{ab} + sigma_{ab} = S_{ab}[g, T]

with S_{ab} the trace-free part of the matter stress or curvature
anisotropy.

### What It Adds

- Shear memory: sigma_{ab} carries the trace-free anisotropic memory
- Partial angular coupling: sigma_{ab} has l=2 content by structure
- Cosmological perturbation theory: scalar and tensor perturbations
  now have distinct memory timescales

### Scalar Limit

In FRW (isotropic): sigma_{ab} = 0 identically.
In spherical collapse (radial symmetry): sigma_{ab} has one independent
component (the radial-tangential stress difference).

The scalar-only closure IS the isotropic/spherical limit of this candidate.

### Assessment

- **Status**: MINIMAL TENSORIAL EXTENSION
- **DOF**: 1 + 5 = 6 (in 3+1 split)
- **Symmetry reduction**: recovers Candidate 1 in isotropic/spherical limits
- **Computational cost**: moderate (5 additional coupled ODEs in 3+1)
- **Advantage**: captures shear memory without full rank-2 tensor field theory
- **Disadvantage**: sigma_{ab} is still constitutive; no action derivation

---

## D. Candidate 3 — Vector / Flow-Structured Extension

### Structure

Introduce a vector memory field v_a alongside the scalar:
- Phi (scalar, 1 DOF): isotropic memory
- v_a (vector, 3 DOF in 3+1 split): flow-structured memory

The vector field tracks the memory of the velocity/acceleration field:
  tau u^b nabla_b v_a + v_a = W_a[g, T, u]

where W_a is a vector source (e.g., nabla_a Phi or u^b nabla_b u_a).

### What It Adds

- Velocity memory: v_a carries the memory of flow acceleration
- Vorticity effects: if v_a has a curl component, vorticity memory
  is captured
- Kerr application: v_a can carry m-dependent (azimuthal) memory in
  axisymmetric spacetimes

### Assessment

- **Status**: PLAUSIBLE INTERMEDIATE EXTENSION
- **DOF**: 1 + 3 = 4 (in 3+1 split)
- **Use case**: axisymmetric problems (Kerr), flows with vorticity
- **Scalar limit**: v_a = 0 in isotropic/irrotational flows
- **Disadvantage**: incomplete for full anisotropy — lacks symmetric
  trace-free tensor content
- **Relationship to Candidate 2**: v_a is the vector part of a general
  decomposition; sigma_{ab} is the tensor part. Both together cover
  more than either alone.

---

## E. Candidate 4 — Rank-2 Symmetric Tensor Memory Field

### Structure

Full generalization: Phi_{ab} is a symmetric rank-2 tensor field.

In 4D, a symmetric rank-2 tensor has 10 independent components.
Subject to:
- Trace constraint: g^{ab} Phi_{ab} = Phi_scalar (links to scalar DOF)
- Diffeomorphism constraints: nabla^a Phi_{ab} = J_b (4 constraints)

This leaves:
- Massive: 10 - 1 (trace) = 9, then - 4 (diffeo) = 5 propagating DOF
  plus 1 scalar trace = 6 total
- Massless: 10 - 4 (gauge) - 4 (constraints) = 2 propagating DOF
  (analogous to GW polarizations) plus 1 scalar

The relaxation equation generalizes to:
  tau u^c nabla_c Phi_{ab} + Phi_{ab} = X_{ab}[g, T]

### What It Adds

- All of Candidates 2 and 3 as special cases
- Propagating memory modes (memory gravitational waves)
- Full Christodoulou-type gravitational-wave memory
- Complete tidal (Weyl tensor) memory coupling
- Nonperturbative strong-field dynamics

### Decomposition in 3+1 Split

Phi_{ab} decomposes as:
- Phi (scalar trace): 1 DOF (= current memory)
- v_a (vector): 3 DOF (flow memory, Candidate 3)
- sigma_{ab} (trace-free tensor): 5 DOF (shear memory, part of Candidate 2)

Total: 9 spatial + 1 trace = 10, minus constraints.

### Assessment

- **Status**: MAXIMAL EXTENSION (underdetermined at current pass)
- **DOF**: up to 6 propagating (massive) or 2 (massless) + scalar
- **Advantage**: complete — captures all possible memory physics
- **Disadvantage**: requires full constraint theory, Cauchy problem analysis,
  stability analysis, ghost/tachyon checks, and more constraint equations
  than current framework provides
- **Computational cost**: HIGH — coupled PDE system in 3+1 decomposition
- **Recommendation**: study only after Candidate 2 is exhausted

---

## F. Candidate 5 — Constitutive Anisotropic Stress (No New Field)

### Structure

Instead of promoting memory to a tensor FIELD, keep the scalar Phi but
allow the constitutive T^Phi_{ab} to carry anisotropic stress
phenomenologically:

  T^Phi_{ab} = T^iso_{ab}(Phi) + Delta T^aniso_{ab}(Phi, curvature)

where Delta T^aniso is determined by curvature invariants (Weyl tensor,
shear scalar) and the scalar memory state. No new dynamical DOF.

### What It Adds

- Anisotropic stress without extra DOF
- Curvature-dependent memory effects
- Still one ODE per sector (scalar relaxation unchanged)
- Applicable to Kerr at leading order

### Assessment

- **Status**: EFFECTIVE ANISOTROPIC LIMIT
- **DOF**: 1 (same as Candidate 1)
- **Advantage**: minimal modification to existing framework
- **Disadvantage**: purely phenomenological; does not capture propagating
  modes or shear memory dynamics
- **Relationship**: this is the CONSTITUTIVE LIMIT of Candidate 2 —
  sigma_{ab} determined algebraically rather than dynamically

---

## G. Tensor Classification Summary

| Candidate | DOF | Captures | Scalar limit? | Status |
|-----------|:---:|----------|:---:|--------|
| 1: Scalar only | 1 | FRW, collapse, PDE | IS scalar | sufficient for Phase III |
| 2: Scalar + aniso stress | 6 | Shear memory, angular coupling | Yes | minimal extension |
| 3: Scalar + vector | 4 | Flow memory, vorticity, Kerr | Yes | plausible intermediate |
| 4: Rank-2 tensor | 6-10 | Everything | Yes | maximal (underdetermined) |
| 5: Constitutive aniso | 1 | Aniso stress, no new DOF | IS scalar + phenomen. | effective limit |

---

## H. Which Phase III Results Survive?

### Unchanged Under All Extensions

1. Modified Friedmann equation: H^2 = (1 - alpha) H^2_base + alpha Phi
   (the scalar trace is always present)
2. Memory ODE structure: tau dPhi/dt + Phi = X (scalar trace always relaxes)
3. Structural identity: omega_0 * tau = 1 (depends on scalar relaxation
   timescale, not tensor structure)
4. PDE dispersion relation fundamental mode: omega^2 = omega_0^2 +
   2 alpha omega_g^2 / (1 + i omega tau) (scalar perturbation)
5. Mixed-viscoelastic classification at canon: Q ~ 6-7.5 (from scalar PDE)
6. Echo channel: ~1.1% (dominated by scalar reflection coefficient)
7. Collapse endpoint law: R_eq = epsilon_Q^{1/beta_Q} r_s (scalar force balance)
8. Constitutive-effective action status (tensor extension does not resolve
   the variational obstruction from Package 1)

### Modified Under Tensorial Extension

1. T^Phi_{ab} acquires additional components (anisotropic stress, off-diagonal)
2. PDE perturbation theory gains additional modes (l-coupling, tensor modes)
3. Echo channel gains additional polarization channels (tensor reflection)
4. Love numbers gain tensor corrections (anisotropic tidal response)
5. Kerr gains azimuthal memory (m-dependent modes from tensor or vector)
6. Junction conditions acquire tensor matching conditions

### New Physics Only With Tensorial Memory

1. Gravitational-wave memory (Christodoulou type) — requires propagating tensor DOF
2. Shear memory in anisotropic collapse — requires sigma_{ab}
3. Memory gravitational waves — propagating memory tensor perturbations
4. Anisotropic cosmological memory — requires sigma_{ab} in perturbed FRW
5. Vorticity memory — requires vector v_a
6. Multi-polarization echo spectrum — tensor reflection coefficients

---

## I. Recommended Extension Path

### Immediate (Phase IV)

**Candidate 5 (constitutive anisotropic stress)** for near-term Kerr and
Love number calculations. This requires NO new dynamical DOF and can be
implemented as a modification to the existing T^Phi_{ab} computation.

### Next Pass (Phase V)

**Candidate 2 (scalar + anisotropic stress tensor)** as the minimal
dynamical extension. This adds 5 coupled ODEs for sigma_{ab} and captures
shear memory. Required for:
- Anisotropic cosmological perturbation theory
- Kerr beyond leading order
- Gravitational-wave memory effects

### Future (Phase VI+)

**Candidate 4 (full rank-2 tensor)** only if Candidate 2 proves insufficient
or if propagating memory modes are observationally motivated. This requires
substantial foundational work (constraint theory, stability, ghosts).

---

## J. Scalar as Symmetry-Reduced Limit

The scalar memory Phi IS the symmetry-reduced limit of a deeper tensorial
structure in the following precise sense:

1. In FRW (O(3) isometry): Phi = (1/3) g^{ab} Phi_{ab} is the only surviving
   component of any symmetric rank-2 tensor memory field. The trace-free
   part vanishes identically.

2. In spherical collapse (SO(3) symmetry): Phi_{ab} has at most 2 independent
   components (radial and tangential). The scalar Phi captures the trace;
   one additional component captures the radial-tangential anisotropy.

3. In Kerr (axial symmetry): Phi_{ab} has up to 4 independent components.
   The scalar captures the isotropic part; additional components carry
   m-dependent azimuthal memory.

This means the scalar closure is NOT an arbitrary simplification — it is
the UNIQUE minimal structure compatible with the symmetries of all current
Phase III computations.

However: whether the scalar arises as a symmetry reduction of a PHYSICAL
tensorial field, or whether it is a standalone degree of freedom that
happens to sit in the trace sector, is an OPEN QUESTION that Package 1
(action principle) did not resolve.

---

## K. Nonclaims

1. No complete tensorial field theory for the GRUT memory sector has been
   constructed.
2. The scalar closure is SUFFICIENT for all Phase III results, not proven
   to be the final memory ontology.
3. Candidate 2 (scalar + anisotropic stress) is the minimal extension, not
   proven to be the unique correct extension.
4. Candidate 4 (full rank-2) is classified but NOT derived — requires
   constraint theory, stability analysis, and ghost checks.
5. The constitutive anisotropic stress (Candidate 5) is an effective limit,
   not a dynamical theory.
6. Whether the scalar is a symmetry-reduced limit of a physical tensor
   field is an OPEN QUESTION.
7. No propagating memory modes have been confirmed or excluded.
8. Gravitational-wave memory effects are classified as requiring tensorial
   extension, not demonstrated.
9. The extension path (constitutive -> scalar+sigma -> full tensor) is a
   RECOMMENDATION based on structural criteria, not a uniqueness result.
10. alpha_mem / alpha_vac unification is NOT attempted under any tensor
    candidate.
11. No observational predictions distinguish the tensor candidates.
12. The 6-DOF count for massive rank-2 assumes no additional constraints
    beyond diffeomorphism invariance.
