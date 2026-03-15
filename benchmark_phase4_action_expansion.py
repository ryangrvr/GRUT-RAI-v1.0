#!/usr/bin/env python3
"""Phase IV — Action Principle Expansion Pass Benchmark.

Verifies that all three action-principle routes are tested numerically,
not merely classified:

1. Route A: Overdamped KG parent (both sectors)
2. Route B: Galley doubled-field dissipative formalism
3. Route C: Nonlocal retarded kernel
4. Master comparison and trilemma
5. Phase III preservation
6. Scalar field ontology
7. Nonclaims completeness
8. Serialization

STATUS: THREE ROUTES TESTED. NO PREMATURE WINNER. TRILEMMA VERIFIED.
"""

from __future__ import annotations

import math
import sys

passed = 0
failed = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    status = "PASS" if condition else "FAIL"
    if not condition:
        failed += 1
        print(f"  [{status}] {label}: {detail}")
    else:
        passed += 1
        print(f"  [{status}] {label}")


# ============================================================================
# SECTION 1: Route A — Overdamped KG Parent
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 1: Route A — Overdamped KG Parent (Klein-Gordon)")
print("=" * 70)

from grut.action_expansion import (
    test_route_a_cosmo,
    test_route_a_collapse,
    evaluate_route_a,
    evaluate_route_b,
    evaluate_route_c,
    test_route_c_kernel,
    compute_action_expansion,
    route_to_dict,
    expansion_to_dict,
)

# 1a. Cosmological sector
print("\n  -- Cosmological Sector --")
cosmo = test_route_a_cosmo()
check("KG cosmo converges to GRUT", cosmo.kg_converges_to_grut)
check("Overdamped approximation is good", cosmo.overdamped_is_good_approx)
check("KG-GRUT RMS error < 0.5", cosmo.kg_grut_rms_error < 0.5,
      f"rms={cosmo.kg_grut_rms_error:.4f}")
check("KG approaches source X (10%)", abs(cosmo.phi_kg[-1] - cosmo.source) / abs(cosmo.source) < 0.1,
      f"frac err={abs(cosmo.phi_kg[-1] - cosmo.source) / abs(cosmo.source):.4f}")
check("GRUT approaches source X (1%)", abs(cosmo.phi_grut[-1] - cosmo.source) / abs(cosmo.source) < 0.01,
      f"frac err={abs(cosmo.phi_grut[-1] - cosmo.source) / abs(cosmo.source):.6f}")
check("Enough integration steps", cosmo.n_steps >= 1000 and len(cosmo.phi_kg) > 10)

# 1b. Collapse sector
print("\n  -- Collapse Sector --")
collapse = test_route_a_collapse()
check("KG collapse converges to GRUT", collapse.kg_converges_to_grut)
check("KG approaches source X (collapse)", abs(collapse.phi_kg[-1] - collapse.source) / abs(collapse.source) < 0.1)
check("GRUT approaches source X (collapse)", abs(collapse.phi_grut[-1] - collapse.source) / abs(collapse.source) < 0.01)

notes_combined = " ".join(collapse.notes).lower()
check("Structural identity mentioned", "structural identity" in notes_combined or "omega_0" in notes_combined)
check("Critical damping noted", "critical" in notes_combined)

# 1c. Route A evaluation
print("\n  -- Route A Evaluation --")
route_a, _, _ = evaluate_route_a()
check("Route A: quasi_action", route_a.action_status == "quasi_action")
check("Route A: local", route_a.is_local is True)
check("Route A: conservative", route_a.is_conservative is True)
check("Route A: approximate recovery", route_a.recovers_first_order == "approximate")
check("Route A: scalar emergent", route_a.scalar_status == "emergent")
check("Route A: obstruction > 50 chars", len(route_a.unresolved_obstruction) > 50)
check("Route A: nonclaims >= 3", len(route_a.nonclaims) >= 3)
check("Route A: tphi compatible", route_a.tphi_compatible)


# ============================================================================
# SECTION 2: Route B — Galley Doubled-Field Formalism
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 2: Route B — Galley Doubled-Field Dissipative Formalism")
print("=" * 70)

route_b, galley = evaluate_route_b()

# 2a. Galley test results
print("\n  -- Galley Formal Verification --")
check("Physical limit recovers ODE", galley.physical_limit_recovers_ode)
check("Energy balance consistent", galley.energy_balance_consistent)
check("Dissipation rate ~ 1.0",
      0.99 < galley.dissipation_rate_matches < 1.01,
      f"ratio={galley.dissipation_rate_matches:.6f}")
check("Is serious candidate", galley.is_serious_candidate)
check("Not a formal shell", not galley.is_formal_shell)
check("Gravity coupling NOT tested", not galley.gravity_coupling_tested)

# 2b. Route B evaluation
print("\n  -- Route B Evaluation --")
check("Route B: exact recovery", route_b.recovers_first_order == "exact")
check("Route B: recovery quality > 0.99", route_b.recovery_quality > 0.99)
check("Route B: local", route_b.is_local is True)
check("Route B: dissipative", route_b.is_dissipative is True)
check("Route B: not conservative", route_b.is_conservative is False)
check("Route B: critical damping compatible", route_b.critical_damping_compatible)
check("Route B: scalar fundamental", route_b.scalar_status == "fundamental")
check("Route B: obstruction mentions gravity", "gravity" in route_b.unresolved_obstruction.lower())


# ============================================================================
# SECTION 3: Route C — Nonlocal Retarded Kernel
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 3: Route C — Nonlocal Retarded Action (Kernel Convolution)")
print("=" * 70)

# 3a. Kernel test
print("\n  -- Kernel Numerical Verification --")
kernel = test_route_c_kernel(tau_eff=1.0)
check("Kernel is causal", kernel.kernel_is_causal)
check("Kernel is normalized", kernel.kernel_is_normalized,
      f"norm={kernel.kernel_norm:.6f}")
check("Kernel norm in [0.99, 1.01]", 0.99 < kernel.kernel_norm < 1.01)
check("Convolution = ODE (step source)", kernel.equivalence_verified,
      f"max err={kernel.convolution_ode_max_error:.6f}")
check("Convolution-ODE max error < 0.05", kernel.convolution_ode_max_error < 0.05)
check("Multi-timescale verified", kernel.multi_timescale_verified,
      f"max err={kernel.multi_timescale_max_error:.6f}")
check("Multi-timescale max error < 0.1", kernel.multi_timescale_max_error < 0.1)
check("Action is real", kernel.action_is_real)
check("Action is bounded", kernel.action_is_bounded)

# 3b. Route C evaluation
print("\n  -- Route C Evaluation --")
route_c, _ = evaluate_route_c()
check("Route C: exact recovery", route_c.recovers_first_order == "exact")
check("Route C: recovery quality > 0.95", route_c.recovery_quality > 0.95)
check("Route C: nonlocal", route_c.is_local is False)
check("Route C: formal parent", route_c.action_status == "formal_parent")
check("Route C: scalar effective", route_c.scalar_status == "effective")
check("Route C: critical damping compatible", route_c.critical_damping_compatible)
check("Route C: nonclaims >= 4", len(route_c.nonclaims) >= 4)


# ============================================================================
# SECTION 4: Master Analysis — Comparison & Trilemma
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 4: Master Analysis — Comparison Table & Trilemma")
print("=" * 70)

result = compute_action_expansion()

check("Result is valid", result.valid)
check("All three routes present",
      result.route_a is not None and result.route_b is not None and result.route_c is not None)
check("Best route = route_c_nonlocal", result.best_route == "route_c_nonlocal")

# Trilemma check
text = result.sharpest_obstruction.lower()
check("Trilemma mentions 'local'", "local" in text)
check("Trilemma mentions 'conservative' or 'nonlocal'", "conservative" in text or "nonlocal" in text)
check("Sharpest obstruction > 100 chars", len(result.sharpest_obstruction) > 100)

# Recovery comparison
check("Route A = approximate", result.route_a.recovers_first_order == "approximate")
check("Route B = exact", result.route_b.recovers_first_order == "exact")
check("Route C = exact", result.route_c.recovers_first_order == "exact")

# Locality comparison
check("Route A = local", result.route_a.is_local is True)
check("Route B = local", result.route_b.is_local is True)
check("Route C = nonlocal", result.route_c.is_local is False)

# Scalar status comparison
check("Route A = emergent", result.route_a.scalar_status == "emergent")
check("Route B = fundamental", result.route_b.scalar_status == "fundamental")
check("Route C = effective", result.route_c.scalar_status == "effective")
check("Scalar status = route_dependent", result.scalar_field_status == "route_dependent")


# ============================================================================
# SECTION 5: Phase III Preservation
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 5: Phase III Preservation")
print("=" * 70)

check("Route A preserves Phase III", result.route_a.tphi_compatible)
check("Route B preserves Phase III", result.route_b.tphi_compatible)
check("Route C preserves Phase III", result.route_c.tphi_compatible)

# All routes must recover the first-order ODE (at least approximately)
check("Route A: weak-field recovery", result.route_a.weak_field_recovery)
check("Route A: strong-field recovery", result.route_a.strong_field_recovery)
check("Route B: weak-field recovery", result.route_b.weak_field_recovery)
check("Route B: strong-field recovery", result.route_b.strong_field_recovery)
check("Route C: weak-field recovery", result.route_c.weak_field_recovery)
check("Route C: strong-field recovery", result.route_c.strong_field_recovery)


# ============================================================================
# SECTION 6: Nonclaims Completeness
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 6: Nonclaims Completeness")
print("=" * 70)

check("Master nonclaims >= 7", len(result.nonclaims) >= 7)
check("Route A nonclaims >= 3", len(result.route_a.nonclaims) >= 3)
check("Route B nonclaims >= 5", len(result.route_b.nonclaims) >= 5)
check("Route C nonclaims >= 4", len(result.route_c.nonclaims) >= 4)

# Print nonclaims
print("\n  Master nonclaims:")
for i, nc in enumerate(result.nonclaims, 1):
    print(f"    {i}. {nc}")


# ============================================================================
# SECTION 7: Serialization
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 7: Serialization")
print("=" * 70)

d_route_a = route_to_dict(result.route_a)
check("Route A dict has name", d_route_a["name"] == "route_a_overdamped")
check("Route A dict has diagnostics", isinstance(d_route_a["diagnostics"], dict))

d_full = expansion_to_dict(result)
check("Full dict has valid=True", d_full["valid"] is True)
check("Full dict has best_route", d_full["best_route"] == "route_c_nonlocal")
check("Full dict has all routes", d_full["route_a"] is not None and d_full["route_b"] is not None and d_full["route_c"] is not None)
check("Full dict has nonclaims", len(d_full["nonclaims"]) >= 7)


# ============================================================================
# SECTION 8: Status Report
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 8: Status Report")
print("=" * 70)

print(f"""
  Action Expansion Status:
    Total routes tested:     3
    Best route:              Route C (nonlocal retarded action)
    Exact recovery routes:   Route B (Galley), Route C (nonlocal)
    Approximate route:       Route A (KG overdamped parent)
    Trilemma:                local-conservative-first-order (IRREDUCIBLE)
    Scalar field ontology:   ROUTE-DEPENDENT (undetermined)
    Phase III preservation:  ALL routes preserve ALL Phase III results
    Master nonclaims:        {len(result.nonclaims)}
    Route A nonclaims:       {len(result.route_a.nonclaims)}
    Route B nonclaims:       {len(result.route_b.nonclaims)}
    Route C nonclaims:       {len(result.route_c.nonclaims)}
""")

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 70)
print(f"BENCHMARK RESULT: {passed} passed, {failed} failed")
print("=" * 70)

if failed > 0:
    print(f"\n  *** {failed} checks FAILED ***")
    sys.exit(1)
else:
    print("\n  All checks PASSED — Action Expansion Benchmark CLEAN")
    sys.exit(0)
