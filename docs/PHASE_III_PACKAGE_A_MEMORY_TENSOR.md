# Package A — Memory Tensor Closure

**DATE**: 2026-03-12
**STATUS**: CONSTITUTIVE / NONLOCAL-EFFECTIVE

---

## 1. Explicit Effective T^Φ_μν

The memory stress-energy tensor is derived constitutively — it is the
unique source term that, inserted into the Einstein equations alongside
T_μν, reproduces the GRUT sector dynamics.

### Cosmological (FRW) Sector

Perfect-fluid form: T^Φ_μν = (ρ_Φ + p_Φ) u_μ u_ν + p_Φ g_μν

**Energy density**:

    ρ_Φ = (3c²/8πG) · α_mem · (Φ − H²_base)

- At steady state (Φ = H²_base): ρ_Φ = 0 — memory is invisible
- Out of steady state: ρ_Φ encodes the lag between memory and driver
- Lag sign: Φ < H²_base during expansion acceleration → ρ_Φ < 0

**Pressure**: determined by combined conservation ∇_μ(T^μν_m + T^Φ_μν) = 0:

    p_Φ = −ρ_Φ − dρ_Φ/(3H dt)

This gives a time-dependent effective equation of state w_Φ = p_Φ/ρ_Φ.
At steady state: w_Φ → −1 (cosmological-constant-like).

### Collapse (Spherical) Sector

Anisotropic form: T^Φ_μν = diag(−ρ_Φ, p_r, p_t, p_t) in comoving frame.

**Memory force contribution**: Δa_mem = α_vac(M_drive − a_grav)

- At equilibrium (M_drive = a_grav): ρ_Φ → 0, p_r → 0 — memory invisible
- During transients: memory stress encodes the lag between M_drive and a_grav

### Energy Conditions

Energy conditions are STATE-DEPENDENT:
- Weak energy (ρ ≥ 0, ρ + p ≥ 0): can be violated during transients
- Null energy (ρ + p ≥ 0): can be violated when memory lags strongly
- At equilibrium: all conditions trivially satisfied (ρ_Φ = 0)

---

## 2. Action / Lagrangian Status

**Classification**: CONSTITUTIVE_EFFECTIVE

The first-order relaxation equation τ u^α ∇_α Φ + Φ = X is inherently
dissipative. A standard variational principle δS = 0 produces second-order
equations of motion, not first-order relaxation.

**Three routes to an action exist**:
1. **Nonlocal retarded action** (Candidate 3 kernel formulation)
2. **Galley doubled-variable formalism** for open/dissipative systems
3. **Overdamped Klein-Gordon limit**: □Φ + m²Φ = J in the limit m²τ >> 1

All three are candidates; none is confirmed to reproduce the exact GRUT
dynamics. The theory is best described as constitutive/nonlocal-effective.

---

## 3. Scalar vs Tensorial Comparison

| Property | Scalar Φ | Tensor Φ_μν |
|----------|----------|-------------|
| DOF | 1 per sector | 6 (massive) or 2 (massless) |
| Sufficient for FRW | Yes | Yes (overkill) |
| Sufficient for spherical collapse | Yes | Yes (overkill) |
| Required for Kerr | Likely (leading order) | For subleading spin effects |
| Required for GW memory | No | Yes |
| Required for anisotropic memory | No | Yes |
| Current Phase III results | All covered | Not needed |

**Recommendation**: Scalar is sufficient for all current Phase III results.
Tensorial generalisation is a post-Phase-III research target.

---

## 4. Conservation

Combined conservation ∇_μ(T^μν + T^Φ_μν) = 0 is satisfied **by construction**:
p_Φ is derived from the conservation equation, not from an independent
equation of state. This is self-consistent but does not constitute a proof
from Noether's theorem or a variational principle.

---

## 5. Nonclaims

1. T^Φ_μν is CONSTITUTIVE/EFFECTIVE — derived from sector equations, NOT from action
2. Combined conservation satisfied BY CONSTRUCTION (p_Φ from conservation)
3. Energy conditions are STATE-DEPENDENT — can be violated during transients
4. p_Φ is NOT from equation of state — follows from conservation
5. Action status is CONSTITUTIVE_EFFECTIVE — standard variational principle does not apply
6. Overdamped KG and nonlocal action are CANDIDATES, not confirmed routes
7. Scalar memory SUFFICIENT for all current Phase III results
8. Tensorial generalisation CLASSIFIED but NOT derived
9. At equilibrium, ρ_Φ → 0: memory invisible at fixed points
10. Memory stress-energy dynamically active ONLY during transients

---

## Files

| File | Role |
|------|------|
| `grut/memory_tensor.py` | Explicit T^Φ_μν, action status, tensor comparison |
| `tests/test_packages_abc.py` | 18 tests (Package A classes) |
