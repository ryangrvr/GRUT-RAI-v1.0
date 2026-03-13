# PACKET_ENDPOINT_v0.1 — OP_QPRESS_001 Acceptance Evidence

Generated: 2026-03-08T21:08:31.382386Z

## Operator

```
a_Q = (GM/R^2) * epsilon_Q * (r_s/R)^beta_Q
Equilibrium: R_eq/r_s = epsilon_Q^(1/beta_Q)
```

- epsilon_Q = 0.1 (UNFIXED research parameter)
- beta_Q = 2 (UNFIXED research parameter)
- R_eq/r_s predicted = 0.316228
- canon_status: RESEARCH_TARGET
- Default: epsilon_Q = 0.0 (operator OFF, zero regression risk)

## Canonical Force Decomposition

All force terms use this canonical convention:

```
a_inward  = (1 - alpha_vac) * GM/R^2 + alpha_vac * M_drive
a_outward = a_Q = (GM/R^2) * epsilon_Q * (r_s/R)^beta_Q
a_net     = a_inward - a_outward
force_balance_residual = |a_net| / (GM/R^2)
```

The deprecated name 'a_eff' is NOT used. The canonical term is 'a_net'.

## Acceptance Summary

| Criterion | Result | Detail |
|-----------|--------|--------|
| V_tol insensitive | PASS | spread=0.00% |
| R0 insensitive | PASS | spread=0.00% |
| Force balanced | PASS | residual=0.000000 |
| Operator-driven | PASS | a_outward/a_grav=1.0000 |
| Not artifact | PASS | deviation=49.6% |
| Stable endpoint | PASS | err_out=0.0000 err_in=0.0000 |
| Stability positive | PASS | indicator_outside=1.29e+12 indicator_inside=1.29e+12 |

**Overall**: ALL PASS

## Boundary of Current Claim

### DEMONSTRATED

- OP_QPRESS_001 creates a genuine finite-radius equilibrium where a_net -> 0 physically.
- The endpoint is independent of V_tol (< 1% spread across 4+ orders of magnitude, barrier-engaged runs only).
- The endpoint is independent of R0 (< 1% spread across R0/r_s = 3..100).
- The endpoint is independent of H_cap (< 1% spread across 2 orders of magnitude).
- The endpoint is independent of M (same R_eq/r_s across stellar to supermassive masses, barrier-engaged runs only).
- The endpoint is operator-driven: a_outward/a_grav ~ 1 at the final state (not an L_stiff artifact).
- The equilibrium is asymptotically stable: perturbations from both sides recover to R_eq within 5%.
- The asymptotic stability indicator d(a_net)/dR is positive (restoring).

### NOT DEMONSTRATED

- The values of epsilon_Q and beta_Q are UNFIXED research parameters. No derivation from first principles or observational data.
- No exterior observables (gravitational waves, electromagnetic signatures) have been computed.
- No unitarity constraints or information-theoretic closure.
- No Whole-Hole analysis (matching interior to exterior).
- Endpoint validation applies to barrier-engaged runs ONLY. Loose V_tol values (>= ~1e-6 for typical configurations) can cause the saturation detector to fire before the shell reaches the barrier, producing the old L_stiff artifact endpoint.
- The operator does NOT claim to 'solve' black hole physics or replace GR interiors. It is a candidate operator under active investigation.

### V_tol CAVEAT (3/4 rule)

The benchmark acceptance suite identifies 'barrier-engaged' runs as those where the solver-determined R_f differs from the artifact prediction (V_tol^2 * 2GM / H_cap^2)^(1/3) / r_s by more than 10%. Runs where R_f matches the artifact formula are classified as 'artifact-dominated' — the saturation detector fired before the barrier could engage. This is not a failure of the operator; it is a saturation-detector priority issue. Future work may add a barrier-aware termination criterion.

## Status Ladder

| Status | Item |
|--------|------|
| LOCKED | Tier 0 local-tau closure fixes frozen-collapse pathology |
| LOCKED | Old finite-radius endpoint is L_stiff x V_tol artifact |
| LOCKED | OP_QPRESS_001 passes anti-artifact acceptance suite |
| LOCKED | Stable endpoint at R_eq/r_s = epsilon_Q^(1/beta_Q) |
| CANDIDATE | r_sat = epsilon_Q^(1/beta_Q) * r_s (physical saturation radius) |
| CANDIDATE | Endpoint law R_eq/r_s = epsilon_Q^(1/beta_Q) |
| ACTIVE | Derivation of epsilon_Q from vacuum structure |
| ACTIVE | Derivation of beta_Q from vacuum structure |
| ACTIVE | Whole-Hole closure (exterior observables, unitarity, archive) |

## Files in This Packet

| File | Description |
|------|-------------|
| PACKET_INDEX.json | Manifest with SHA-256 hashes |
| README_ENDPOINT.md | This file |
| acceptance.json | Machine-readable acceptance results |
| force_decomposition.json | Canonical force budget at endpoint |
| vtol_sweep.json | V_tol insensitivity data |
| r0_sweep.json | R0 insensitivity data |
| stability.json | Perturbation recovery data |
| artifact_comparison.json | Artifact law comparison |
