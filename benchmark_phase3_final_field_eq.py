#!/usr/bin/env python3
"""Phase III Final: Covariant GRUT Field Equations Benchmark.

Verifies that the field equation framework:
1. Evaluates three candidate formulations correctly
2. Recovers the cosmological (weak-field) memory ODE at the effective level
3. Recovers the collapse (strong-field) ODE at the effective level
4. Establishes effective-level Bianchi compatibility for both sectors
5. Maintains cross-sector consistency (same relaxation structure)
6. Classifies ansatz vs derived items correctly
7. Documents ≥10 explicit nonclaims
8. Produces a self-consistent status report

STATUS: FIRST COVARIANT PASS — auxiliary memory field (scalarized first pass)
NOT derived from a covariant action or first-principles field equations.

NONCLAIMS:
- Does NOT prove field equations from first principles
- T^Φ_μν is SCHEMATIC/EFFECTIVE throughout
- Scalar is the minimal closure; tensorial generalization remains open
- Bianchi compatibility at the effective level, not proven from action
- Reductions RECOVER current solver structure — do not derive it
- α_mem / α_vac distinction is OPEN, not resolved
- Constrained endpoint law is CONSISTENT with formulation, not derived from it
"""

from __future__ import annotations

import math
import sys

# ── Physical constants ──
G_SI = 6.674e-11
C_SI = 299_792_458.0
M_SUN = 1.989e30

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
# SECTION 1: Candidate Formulation Evaluation
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 1: Candidate Formulation Evaluation")
print("=" * 70)

from grut.field_equations import (
    build_candidate_formulations,
    check_weak_field_reduction,
    check_strong_field_reduction,
    check_bianchi_compatibility,
    compute_field_equation_analysis,
    candidate_to_dict,
    bianchi_to_dict,
    field_equation_result_to_dict,
    _memory_update_exact,
)

candidates = build_candidate_formulations()

check("Three candidates built", len(candidates) == 3)

c1, c2, c3 = candidates

# Candidate 1: Algebraic tensor — INSUFFICIENT
check("C1 is algebraic tensor", c1.name == "algebraic_tensor" and c1.memory_type == "algebraic")
check("C1 has no independent dynamics", c1.has_independent_dynamics is False)
check("C1 is insufficient", c1.sufficient is False and c1.preferred is False)
check("C1 cannot recover weak field", c1.weak_field_recovers is False)
check("C1 cannot recover strong field", c1.strong_field_recovers is False)
check("C1 rejection is status='rejected'", c1.approx_status == "rejected")

# Candidate 2: Auxiliary scalar — PREFERRED
check("C2 is auxiliary scalar", c2.name == "auxiliary_scalar" and c2.memory_type == "scalar_field")
check("C2 has independent dynamics", c2.has_independent_dynamics is True)
check("C2 is sufficient and preferred", c2.sufficient is True and c2.preferred is True)
check("C2 recovers weak field", c2.weak_field_recovers is True)
check("C2 recovers strong field", c2.strong_field_recovers is True)
check("C2 Bianchi compatible", c2.bianchi_compatible_effective is True)
check("C2 uses exponential kernel", c2.kernel_type == "exponential")
check("C2 label includes 'scalarized first pass'", "scalarized first pass" in c2.label)
check("C2 status is effective_ansatz", c2.approx_status == "effective_ansatz")

# Candidate 3: Nonlocal kernel — FORMAL PARENT
check("C3 is nonlocal kernel", c3.name == "nonlocal_kernel" and c3.memory_type == "nonlocal_integral")
check("C3 is sufficient but not preferred", c3.sufficient is True and c3.preferred is False)
check("C3 is formal parent of C2", "formal parent" in c3.relationship_to_others.lower())
check("C3 uses general causal kernel", c3.kernel_type == "general_causal")

# Cross-candidate checks
check("Exactly one candidate is preferred", sum(1 for c in candidates if c.preferred) == 1)
check("Exactly one candidate is rejected", sum(1 for c in candidates if c.approx_status == "rejected") == 1)

# Nonclaims per candidate
for c in candidates:
    check(f"{c.name} has nonclaims", len(c.nonclaims) >= 1)

print(f"\n  Section 1 summary: {passed} passed")


# ============================================================================
# SECTION 2: Weak-Field Sector Recovery
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 2: Weak-Field Sector Recovery")
print("=" * 70)

sec2_start = passed

wf = check_weak_field_reduction(alpha_mem=0.1)

check("Friedmann equation recovered", wf.friedmann_recovered is True)
check("H² match rtol < 1e-12", wf.H_sq_match_rtol < 1e-12, f"rtol = {wf.H_sq_match_rtol:.2e}")
check("Memory ODE recovered", wf.memory_ode_recovered is True)
check("τ_eff coupling recovered", wf.tau_coupling_recovered is True)
check("Fully recovered", wf.fully_recovered is True)
check("Recovery level is 'effective'", wf.recovery_level == "effective")

# Numerical verification: exact exponential update
M0 = 1.0
X_new = 1.1
tau = 1.0
dt = 0.01
M_updated = _memory_update_exact(M0, X_new, dt, tau)
check("Memory moves toward driver", M0 < M_updated < X_new, f"M_updated = {M_updated:.6f}")
check("Exponential update bounded", 0 < M_updated)

# Long-time convergence
M_long = _memory_update_exact(0.0, 1.0, 1000.0, 1.0)
check("Long-time convergence to driver", abs(M_long - 1.0) < 1e-10, f"M_long = {M_long}")

# Test at different alpha_mem values
for alpha_test in [0.05, 0.1, 0.2, 0.3]:
    wf_test = check_weak_field_reduction(alpha_mem=alpha_test)
    check(f"Weak field recovered at α_mem={alpha_test}", wf_test.fully_recovered is True)

print(f"\n  Section 2 summary: {passed - sec2_start} passed")


# ============================================================================
# SECTION 3: Strong-Field Sector Recovery
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 3: Strong-Field Sector Recovery")
print("=" * 70)

sec3_start = passed

sf = check_strong_field_reduction(
    M_kg=30.0 * M_SUN,
    alpha_vac=1.0 / 3.0,
    beta_Q=2.0,
    epsilon_Q=1.0 / 9.0,
)

check("Force balance at equilibrium", sf.force_balance_recovered is True)
check("Memory ODE at equilibrium", sf.memory_ode_recovered is True)
check("Endpoint law recovered", sf.endpoint_recovered is True)
check("Structural identity ω₀τ=1", sf.structural_identity_preserved is True)
check("PDE dispersion recovered", sf.pde_dispersion_recovered is True)
check("Fully recovered", sf.fully_recovered is True)
check("Recovery level is 'effective'", sf.recovery_level == "effective")

# Verify endpoint law numerically
eps_Q = 1.0 / 9.0
beta_Q = 2.0
R_eq_over_r_s = eps_Q ** (1.0 / beta_Q)
check("R_eq/r_s = 1/3", abs(R_eq_over_r_s - 1.0 / 3.0) < 1e-12, f"ratio = {R_eq_over_r_s:.15f}")

# Mass scaling: identity should be mass-independent
for M_test in [10.0 * M_SUN, 100.0 * M_SUN, 1e6 * M_SUN, 1e9 * M_SUN]:
    sf_test = check_strong_field_reduction(M_kg=M_test)
    check(f"ω₀τ=1 at M={M_test/M_SUN:.0e} M_sun", sf_test.structural_identity_preserved is True)

print(f"\n  Section 3 summary: {passed - sec3_start} passed")


# ============================================================================
# SECTION 4: Conservation Structure (Bianchi)
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 4: Conservation Structure (Bianchi)")
print("=" * 70)

sec4_start = passed

bc_cosmo = check_bianchi_compatibility("cosmological")
bc_collapse = check_bianchi_compatibility("collapse")

# Combined conservation is fundamental in both sectors
check("Cosmo: combined conservation", bc_cosmo.combined_conserved is True)
check("Cosmo: compatible at effective level", bc_cosmo.status == "compatible_effective")
check("Collapse: combined conservation", bc_collapse.combined_conserved is True)
check("Collapse: compatible at effective level", bc_collapse.status == "compatible_effective")

# Conservation modes
check("Cosmo: approximate separate in weak field",
      "approximate_separate" in bc_cosmo.conservation_mode)
check("Collapse: no separate conservation",
      "no_separate" in bc_collapse.conservation_mode)

# Notes must reference fundamental combined conservation
check("Cosmo notes reference combined",
      any("combined" in n.lower() for n in bc_cosmo.notes))
check("Collapse notes reference combined",
      any("combined" in n.lower() for n in bc_collapse.notes))

# Collapse sector: individual components NOT separately conserved
check("Collapse: individual not separately conserved",
      "not separately" in bc_collapse.individual_conservation_status.lower())

# Unknown sector returns unchecked
bc_unknown = check_bianchi_compatibility("unknown_sector")
check("Unknown sector: status unchecked", bc_unknown.status == "unchecked")

print(f"\n  Section 4 summary: {passed - sec4_start} passed")


# ============================================================================
# SECTION 5: Cross-Sector Consistency
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 5: Cross-Sector Consistency")
print("=" * 70)

sec5_start = passed

result = compute_field_equation_analysis()

# Same relaxation structure in both sectors
check("Memory params: cosmo phi = M_X", result.memory_params.cosmo_phi == "M_X")
check("Memory params: collapse phi = M_drive", result.memory_params.collapse_phi == "M_drive")

# α values correctly set
check("α_mem = 0.1", abs(result.memory_params.cosmo_alpha - 0.1) < 1e-12)
check("α_vac = 1/3", abs(result.memory_params.collapse_alpha - 1.0 / 3.0) < 1e-12)

# α unification flagged as OPEN
check("α unification: OPEN",
      "open" in result.memory_params.alpha_unification_status.lower())

# Both sectors use the same equation structure: τ_eff dΦ/dt + Φ = X
check("Cosmo tau formula present", "tau_0" in result.memory_params.cosmo_tau_formula)
check("Collapse tau formula present", "tau_local" in result.memory_params.collapse_tau_formula)

# Both Bianchi checks present
check("Two Bianchi checks", len(result.bianchi_checks) == 2)
sectors = {bc.sector for bc in result.bianchi_checks}
check("Both sectors checked", sectors == {"cosmological", "collapse"})

print(f"\n  Section 5 summary: {passed - sec5_start} passed")


# ============================================================================
# SECTION 6: Ansatz vs Derived Classification
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 6: Ansatz vs Derived Classification")
print("=" * 70)

sec6_start = passed

check("Ansatz items ≥ 4", len(result.ansatz_items) >= 4)
check("Derived items ≥ 4", len(result.derived_items) >= 4)

# T^Phi is ansatz
ansatz_str = " ".join(result.ansatz_items).lower()
check("T^Φ_μν is listed as ansatz",
      "t^phi" in ansatz_str or "stress-energy" in ansatz_str or "schematic" in ansatz_str)

# Scalar nature is ansatz
check("Scalar nature is ansatz",
      "scalar" in ansatz_str or "minimal" in ansatz_str)

# Candidate 1 insufficiency is derived
derived_str = " ".join(result.derived_items).lower()
check("C1 insufficiency is derived",
      "candidate 1" in derived_str or "insufficiency" in derived_str)

# Bianchi is derived
check("Combined conservation is derived",
      "bianchi" in derived_str or "conservation" in derived_str)

# Print classification table
print("\n  ANSATZ items (assumed, not derived):")
for item in result.ansatz_items:
    print(f"    → {item}")
print("\n  DERIVED items (established by analysis):")
for item in result.derived_items:
    print(f"    → {item}")

print(f"\n  Section 6 summary: {passed - sec6_start} passed")


# ============================================================================
# SECTION 7: Nonclaims
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 7: Nonclaims")
print("=" * 70)

sec7_start = passed

check("≥ 10 nonclaims", len(result.nonclaims) >= 10, f"found {len(result.nonclaims)}")

# Critical nonclaims must be present
nc_str = " ".join(result.nonclaims).lower()

check("Nonclaim: not first-principles derivation",
      "first principles" in nc_str or "first-principles" in nc_str)
check("Nonclaim: T^Φ is schematic/effective",
      "schematic" in nc_str or "effective" in nc_str)
check("Nonclaim: scalar is minimal closure",
      "minimal" in nc_str or "scalar" in nc_str)
check("Nonclaim: Bianchi at effective level",
      "bianchi" in nc_str or "effective level" in nc_str)
check("Nonclaim: reductions recover, not derive",
      "recover" in nc_str)
check("Nonclaim: Kerr not attempted",
      "kerr" in nc_str)
check("Nonclaim: no observational predictions",
      "observational" in nc_str or "detector" in nc_str or "prediction" in nc_str)

# Print all nonclaims
print("\n  All nonclaims:")
for i, nc in enumerate(result.nonclaims, 1):
    print(f"    {i:2d}. {nc}")

print(f"\n  Section 7 summary: {passed - sec7_start} passed")


# ============================================================================
# SECTION 8: Status Report
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 8: Status Report")
print("=" * 70)

sec8_start = passed

check("Result is valid", result.valid is True)
check("Internally consistent", result.internally_consistent is True)
check("Preferred formulation identified", result.preferred_name == "auxiliary_scalar")
check("Weak field fully recovered", result.weak_field.fully_recovered is True)
check("Strong field fully recovered", result.strong_field.fully_recovered is True)
check("Resolved closures ≥ 5", len(result.resolved_closures) >= 5)
check("Remaining closures = 7", len(result.remaining_closures) == 7)
check("Approx level correct", result.approx_level == "auxiliary_scalar_field_effective")

# Serialization full roundtrip
d = field_equation_result_to_dict(result)
check("Serialization produces valid dict", isinstance(d, dict))
check("Serialized candidates count", len(d["candidates"]) == 3)
check("Serialized preferred name", d["preferred_name"] == "auxiliary_scalar")
check("Serialized internally_consistent", d["internally_consistent"] is True)
check("Serialized valid", d["valid"] is True)

print(f"\n  Section 8 summary: {passed - sec8_start} passed")


# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print(f"BENCHMARK RESULT: {passed} passed, {failed} failed")
print("=" * 70)

if failed > 0:
    print("\nFAILED — see above for details")
    sys.exit(1)
else:
    print("\nCLEAN — all checks passed")
    print("\nPhase III Final Field Equations: STRUCTURALLY ADEQUATE")
    print("  Preferred: Candidate 2 — Auxiliary Memory Field (scalarized first pass)")
    print("  Weak-field: RECOVERED at effective level")
    print("  Strong-field: RECOVERED at effective level")
    print("  Conservation: COMPATIBLE at effective level")
    print("  Remaining closures: 7")
    print(f"  Nonclaims: {len(result.nonclaims)}")
    sys.exit(0)
