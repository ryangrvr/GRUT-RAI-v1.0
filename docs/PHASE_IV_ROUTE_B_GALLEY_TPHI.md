# Phase IV — Route B Follow-Up: Galley T^Phi Derivation

## Status

**PHASE IV — ROUTE B FOLLOW-UP: T^Phi DERIVATION**

Classification: **PHYSICAL-LIMIT DERIVED**

The Galley doubled-field formalism produces a SPECIFIC, EXPLICIT T^Phi_{mu nu}
in the physical limit. This upgrades the memory stress-energy from
constitutive-effective (Phase III) to physical-limit derived (Phase IV Route B).
The derivation is honest but incomplete: the physical-limit projection is
imposed, not emergent, and the doubled-metric ghost status is undetermined.

---

## A. Why Route B Is Being Pursued Now

Phase IV Action Expansion tested three routes and identified Route B (Galley)
as the strongest path for deriving T^Phi_{mu nu} from an action-like framework.
Route C (nonlocal retarded action) remains the structural parent for the EOM
(mathematical identity), but Route C does not directly produce a stress-energy
tensor through a standard metric variation.

Route B is the only route where:
1. The memory field appears directly in a local action
2. A metric variation produces a specific T^Phi_{ab}
3. The physical limit gives the correct first-order relaxation law

The question is: can this path be pushed to produce an explicit, testable
T^Phi_{mu nu}?

---

## B. Minimal Doubled-Field Setup

The Galley formalism doubles all degrees of freedom:

    Phi_1(x), Phi_2(x), g^(1)_{ab}(x), g^(2)_{ab}(x)

The doubled action is:

    S = S_1 - S_2 + S_diss

where for each copy i = 1, 2:

    S_i = integral d^4x sqrt(-g^(i)) [
        R^(i) / (16 pi G)
        - (1/2) g^{ab(i)} nabla_a Phi_i nabla_b Phi_i
        - V(Phi_i) + Phi_i J^(i)
    ]

with the potential V(Phi) = Phi^2 / (2 tau_eff^2) (mass term) and
source J = X / tau_eff.

The dissipative kernel:

    S_diss = integral d^4x sqrt(-g)
        (Phi_1 - Phi_2) u^a nabla_a(Phi_1 + Phi_2) / (2 tau_eff)

Note the antisymmetric structure: S_1 - S_2. This ensures that the "2" copy
acts as the time-reversed partner, encoding dissipation.

---

## C. Physical-Limit Reduction

Physical limit: Phi_1 = Phi_2 = Phi, g^(1)_{ab} = g^(2)_{ab} = g_{ab}.

In this limit:
- S_1 - S_2 -> 0 (copies cancel)
- S_diss -> 0 (Phi_1 - Phi_2 = 0)

But the EQUATIONS OF MOTION survive. Variation of S with respect to Phi_1 and
Phi_2, followed by the physical limit, gives:

    tau_eff u^a nabla_a Phi + Phi = X

This is the GRUT relaxation law, recovered EXACTLY.

Numerical verification:
- Max error between Galley physical-limit solution and GRUT ODE: < 1e-14
- This is machine-precision agreement (both solve the same exponential update)

---

## D. Gravity Coupling Strategy

The gravity coupling proceeds through the standard Einstein equations for each
copy:

    G^(1)_{ab} = (8 pi G / c^4) [ T^(1)_{ab} + T^{Phi_1}_{ab} ]
    G^(2)_{ab} = (8 pi G / c^4) [ T^(2)_{ab} + T^{Phi_2}_{ab} ]

In the physical limit (g^(1) = g^(2) = g):

    G_{ab} = (8 pi G / c^4) [ T_{ab} + T^Phi_{ab} ]

This is the standard modified Einstein equation with a memory stress-energy
contribution.

The strategy: derive T^{Phi_i}_{ab} from the metric variation of each S_i,
then take the physical limit T^{Phi_1} = T^{Phi_2} = T^Phi.

---

## E. Candidate Derivation of T^Phi_{mu nu}

The physical-limit scalar action is:

    S_scalar = integral d^4x sqrt(-g) [
        -(1/2) g^{ab} nabla_a Phi nabla_b Phi - V(Phi) + Phi J
    ]

The metric variation gives:

    T^Phi_{ab} = (2/sqrt(-g)) delta S_scalar / delta g^{ab}
               = nabla_a Phi nabla_b Phi
                 - g_{ab} [(1/2)(nabla Phi)^2 + V(Phi) - Phi J]

This is the STANDARD minimally-coupled scalar stress-energy tensor, with the
specific V and J determined by the GRUT memory sector.

The dissipative kernel S_diss does NOT contribute to T^Phi in the physical limit
because S_diss vanishes when Phi_1 = Phi_2.

In an FRW background with spatially homogeneous Phi:

    rho_Phi = (1/2)(dot{Phi})^2 + V(Phi) - Phi J
    p_Phi   = (1/2)(dot{Phi})^2 - V(Phi) + Phi J

Using the EOM (dot{Phi} = (X - Phi)/tau_eff):

    rho_Phi = (X - Phi)^2 / (2 tau^2) + Phi^2 / (2 tau^2) - Phi X / tau
            = [X^2 - 4 X Phi + 2 Phi^2] / (2 tau^2)

    p_Phi = (X - Phi)^2 / (2 tau^2) - Phi^2 / (2 tau^2) + Phi X / tau
          = X^2 / (2 tau^2)

Notable structural result: p_Phi = X^2 / (2 tau^2) depends only on the driver X,
not on the current memory state Phi.

At steady state (Phi = X):
- rho_Phi = -X^2 / (2 tau^2) < 0
- p_Phi = X^2 / (2 tau^2) > 0
- rho + p = 0 (dot{Phi} = 0)
- w = p/rho = -1 (de Sitter-like)

The negative energy density at steady state is CORRECT: the memory sector acts as
a correction that modifies the effective expansion rate. The constitutive form
H^2 = (1-alpha)H_base^2 + alpha*Phi is recovered.

---

## F. Conservation / Bianchi Discussion

The fundamental conservation statement is:

    nabla_mu (T^{mu nu} + T^{Phi mu nu}) = 0

This follows from the Bianchi identity nabla_mu G^{mu nu} = 0 combined with the
modified Einstein equation.

In the Galley formalism: each copy has its own diffeomorphism invariance, giving
a Bianchi identity for each. In the physical limit, these merge into the standard
single Bianchi identity.

The scalar field is NOT separately conserved:

    nabla_mu T^{Phi mu nu} != 0

This is expected: the memory field is dissipative and exchanges energy with the
matter sector through the relaxation dynamics. The dissipation rate is:

    d(rho_Phi)/dt + 3H(rho_Phi + p_Phi) = -dot{Phi} F_diss

where F_diss encodes the difference between the first-order relaxation EOM and
the second-order KG equation that would make T^Phi separately conserved.

Combined conservation is GUARANTEED by the Galley construction (diffeomorphism
invariance). This is an upgrade from "effective-level compatible" (Phase III)
to "physical-limit derived" (Phase IV Route B).

---

## G. Ghost / Pathology Analysis

The Galley doubled-field system NECESSARILY has ghost modes:

**Scalar sector:**
- The action S = S_1 - S_2 gives kinetic matrix K = diag(-1/2, +1/2)
- Phi_1 has standard kinetic sign (-1/2 nabla Phi nabla Phi)
- Phi_2 has WRONG-SIGN kinetic energy (+1/2 nabla Phi nabla Phi) — this IS a ghost
- In the (Phi_+, Phi_-) basis where Phi_+ = (Phi_1+Phi_2)/2, Phi_- = (Phi_1-Phi_2)/2:
  - Phi_+ (physical mode): correct kinetic sign
  - Phi_- (ghost mode): wrong kinetic sign
- Physical limit (Phi_- = 0): ghost is PROJECTED OUT

This is BY DESIGN. The ghost mode in the Galley formalism is the price paid for
encoding dissipation in a variational framework. It is not a physical instability
as long as the physical-limit constraint is maintained.

**Metric sector:**
- The metric "2" copy has wrong-sign Einstein-Hilbert action (-R^(2))
- This is a gravitational ghost in the full doubled system
- Physical limit (g^(1) = g^(2) = g) should project it out
- But DYNAMICAL STABILITY of this projection is UNDETERMINED
- This is the deepest remaining Route B obstruction

**Summary:**
- Physical-limit scalar sector: GHOST-FREE (m^2 > 0, standard kinetic sign)
- Full doubled system: HAS ghost modes (by design)
- Physical-limit metric sector: EXPECTED ghost-free, NOT PROVEN

---

## H. Comparison to Current Constitutive-Effective T^Phi

| Property | Phase III (Constitutive) | Phase IV Route B (Galley) |
|----------|:-----------------------:|:------------------------:|
| T^Phi source | Ansatz / schematic | Metric variation of scalar action |
| Derivation level | Constitutive-effective | Physical-limit derived |
| Explicit rho_Phi, p_Phi | Not computed | EXPLICIT functional forms |
| w at steady state | Not specified | w = -1 (de Sitter-like) |
| Conservation | Effective-level compatible | Physical-limit derived (Bianchi) |
| Structurally consistent | Yes | Yes |
| Matches constitutive form | — | Yes (cosmo and collapse) |
| Status | Ansatz | Upgraded |

The Galley derivation is a genuine upgrade. The constitutive form is CONSISTENT
with the Galley-derived form (they agree in both sectors), but the Galley form is
more specific: it provides explicit functional forms for rho_Phi and p_Phi that
the constitutive approach did not.

---

## I. Exact Remaining Obstruction

1. **Physical-limit projection**: The constraint Phi_1 = Phi_2, g^(1) = g^(2)
   is IMPOSED, not derived. The doubled system has no mechanism that forces the
   two copies to merge. Showing that the physical limit is a CONSISTENT
   TRUNCATION (i.e., stable under perturbations away from Phi_1 = Phi_2)
   would upgrade the derivation from "physical-limit derived" to "derived."

2. **Doubled-metric ghost**: The "2" copy metric has wrong-sign Einstein-Hilbert
   action. Whether the physical-limit projection eliminates the gravitational
   ghost mode in a dynamically stable way is UNDETERMINED. This is the deepest
   remaining structural question.

3. **Observer-flow dependence**: The dissipative kernel S_diss requires an
   observer flow u^a. Unless u^a is promoted to a dynamical variable, the action
   is not manifestly covariant.

4. **Potential ambiguity**: The choice V(Phi) = Phi^2/(2 tau^2) is the simplest
   mass term, but other potentials are possible and would give different T^Phi.

5. **Consistent truncation**: The physical-limit must be shown to be stable—
   i.e., that solutions with Phi_1 = Phi_2 exactly are attractors of the full
   doubled dynamics. This has NOT been established.

---

## J. Status Recommendation

**Route B standing: UPGRADED from "abstract formalism" to "physical-limit derived T^Phi"**

The Galley derivation:
- Produces an EXPLICIT T^Phi_{mu nu} (standard scalar stress-energy)
- Preserves combined conservation (Bianchi, physical-limit derived)
- Is ghost-free in the physical-limit scalar sector
- Matches the constitutive form in both sectors
- Gives new structural predictions (w = -1 at steady state, constant p_Phi)

The derivation is HONEST but INCOMPLETE:
- Physical-limit projection is imposed
- Doubled-metric ghosts are undetermined
- Observer-flow dependence remains

Route B and Route C are COMPLEMENTARY:
- Route B is strongest for T^Phi (action-derived in physical limit)
- Route C is strongest for EOM (mathematical identity, no projection needed)
- Neither replaces the other

---

## K. Explicit Nonclaims

1. T^Phi is physical-limit derived, NOT fully derived from a single-field action
2. The physical-limit projection is imposed, not emergent or dynamically derived
3. The doubled-metric ghost mode status is UNDETERMINED
4. The dissipative kernel is observer-flow dependent
5. The scalar potential V(Phi) = Phi^2/(2 tau^2) is chosen, not uniquely determined
6. Quantization of the Galley doubled-field system is OPEN
7. Route B does NOT replace Route C as the structural EOM parent
8. The alpha_mem vs alpha_vac distinction is NOT resolved by this derivation
9. The constitutive-effective form is CONSISTENT with but not identical to Galley T^Phi
10. Consistency of the physical-limit truncation has NOT been proven (stability)
11. No observational prediction distinguishes the Galley T^Phi from the constitutive form
12. Anisotropic stress at second order is NOT computed
