# Hole-Sector Radial Collapse Solver — Implementation Plan

## Physics Summary

The GRUT hole-sector is blocked by one missing mathematical sector: **radial collapse with memory coupling**. The Tier A substrate (finite-bandwidth kernel, causal pole, sign-definite dissipation, L_stiff) provides the machinery. This plan builds the solver that turns structural claims into derived engine outputs.

### Key Insight: Oppenheimer-Snyder ↔ Closed FRW
A uniform dust sphere's interior is exactly a closed FRW universe. GRUT already integrates modified FRW. The collapse solver extends this to the radial case using the **same** operator stack.

### Equations (3-variable ODE)

State: `[R, V, M_drive]`
- `R` = shell radius (m)
- `V = dR/dt` (m/s), V ≤ 0 during collapse
- `M_drive` = memory state tracking gravitational drive (m/s²)

```
dR/dt = V
dV/dt = -a_eff
dM_drive/dt = (GM/R² - M_drive) / tau_eff
```

Where:
- `a_eff = (1 - alpha_vac) * GM/R² + alpha_vac * M_drive`
- `tau_eff = tau_0 / (1 + (|V/R| * tau_0)²)`

Post-step operators (same stack as cosmological engine):
- **L_stiff**: if `|V/R| > H_cap` then `V = -H_cap * R`
- **Dissipation**: `V *= exp(-gamma_diss * dt)`

### Why This Works

1. **GR limit** (α=0, γ=0, no L_stiff): reduces to `d²R/dt² = -GM/R²`, standard free-fall → singularity
2. **L_stiff arrest**: caps collapse rate → R decays as `exp(-H_cap*t)`, never reaches zero
3. **Dissipation arrest**: damps V exponentially → R → `R_sat > 0` (finite arrest)
4. **Memory enhancement**: lag in M_drive reduces effective drive → arrest happens sooner
5. **r_sat is DERIVED**: falls out of ODE integration, NOT hardcoded

### Bounce Exclusion (Tier A Proof)

`dV/dt = -a_eff` where `a_eff = (1-α)*GM/R² + α*M_drive > 0` always (both terms positive).
Therefore `dV/dt < 0` always. V starts at 0, becomes negative, can never become positive.
Dissipation preserves sign. L_stiff preserves sign.
**V ≤ 0 for all time. No bounce. QED.**

### Timescale Separation

- `t_ff ~ ms` (stellar collapse) vs `tau_0 ~ 42 Myr`
- During fast collapse: `tau_eff → tiny`, memory tracks drive instantly → GR-like
- After L_stiff activates: `tau_eff` grows → memory lag becomes significant
- Full arrest happens on timescale `~ 1/gamma_diss`

---

## Implementation

### New Files

#### 1. `grut/collapse.py` (~300 lines)
Core radial collapse solver. Pattern follows `grut/quantum.py` (stateless functions, audit dicts).

Functions:
- `compute_collapse(M_kg, R0_m, tau0_s, alpha_vac, gamma_diss, H_cap, n_steps)` — Main ODE integrator with RK4, returns full trajectory + diagnostics
- `compute_trappedness(R, M_kg)` — Compactness `2GM/(Rc²)`, `is_trapped` boolean
- `compute_kretschner(R, M_kg)` — Kretschner scalar `48(GM)²/(c⁴R⁶)`
- `detect_saturation(trajectory, tol)` — Find R_sat from trajectory where |V| → 0
- `check_bounce(V_array)` — Verify V never changes sign (sign-definiteness test)
- `compute_energy_ledger(trajectory)` — Track E_kinetic, E_potential, E_dissipated
- `compute_mass_sweep(M_min, M_max, n_masses, ...)` — Scan r_sat vs M

#### 2. `tests/test_collapse.py` (~120 lines)
Test suite verifying:
- **GR limit**: α=0, γ=0, no cap → singularity (R reaches R_min)
- **GRUT arrest**: α=1/3, γ>0, with cap → R_sat > 0
- **r_sat derivation**: r_sat falls out as function of (M, tau_0, alpha, gamma, H_cap)
- **Bounce exclusion**: V never changes sign in any configuration
- **Curvature finiteness**: Kretschner remains finite at R_sat
- **Determinism**: identical inputs → identical trajectory
- **Mass scaling**: r_sat scales consistently across mass sweep

#### 3. Canon updates: `canon/grut_canon_v0.3.json`
Add to operator_stack:
```json
"OP_RADIAL_COLLAPSE_001": {
  "role": "Spherically symmetric collapse with memory-kernel coupling",
  "status": "IMPLEMENTED"
}
```
Add to core_equations:
```json
{
  "id": "EQ_COLLAPSE_001",
  "name": "GRUT radial collapse (Newtonian + memory)",
  "math": "d2R/dt2 = -[(1-alpha_vac)*GM/R^2 + alpha_vac*M_drive]"
}
```

#### 4. API endpoint: `api/main.py`
- `POST /experiments/radial_collapse` — Run collapse with parameters, return trajectory summary + NIS certificate
- New GRUTipedia topic: `radial-collapse-solver`

#### 5. Tool wiring: `ai/tools.py` + `ai/tool_executor.py`
- New tool: `run_radial_collapse` for AI orchestration

---

## Diagnostics at Each Step

| Quantity | Definition | Purpose |
|----------|-----------|---------|
| `compactness` | `2GM/(Rc²)` | Apparent horizon indicator |
| `is_trapped` | `compactness ≥ 1` | Trapped surface test |
| `K_kretschner` | `48(GM)²/(c⁴R⁶)` | Curvature invariant |
| `E_kinetic` | `½MV²` | Energy ledger |
| `E_potential` | `-GM²/R` | Energy ledger |
| `E_dissipated` | `∫γMV²dt` | Dissipation tracking |

---

## What This Resolves

| Audit Question | Before | After |
|----------------|--------|-------|
| Q1: Horizon stability | UNDERDETERMINED | DERIVABLE — trajectory shows whether trapped surface forms and persists |
| Q2: Collapse endpoint | UNDERDETERMINED | DERIVABLE — r_sat falls out of ODE integration |
| Q3: Bounce rejection | UNDERDETERMINED | TIER A PROOF — sign-definiteness of a_eff > 0 |
| Q4a: Archive existence | UNDERDETERMINED | PARTIALLY — energy ledger tracks where energy goes |
| Q4b: External inaccessibility | UNDERDETERMINED | PARTIALLY — trapped surface analysis shows trapping |
| Q4c: Global unitarity | UNDERDETERMINED | STILL TIER B — needs full phase-space definition |

---

## Dependency Order
1. `grut/collapse.py` (zero dependencies beyond numpy + existing constants)
2. `tests/test_collapse.py` (depends on collapse.py)
3. Canon JSON updates (parallel with tests)
4. API endpoint + tool wiring (depends on solver being tested)
5. GRUTipedia topic (last)

## Rules (from user directive)
- **Derive r_sat** — do not hardcode it
- **Compute trappedness** — do not assume a horizon
- **Test sign-definiteness** — do not assert bounce rejection without proof
- **Track energy explicitly** — do not infer unitarity from memory alone
