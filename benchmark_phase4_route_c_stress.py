#!/usr/bin/env python3
"""Phase IV — Route C: Nonlocal Retarded Stress-Functional Benchmark.

Verifies the complete Route C stress-functional analysis:

1. Nonlocal retarded action properties
2. Metric variation classification
3. Stress-functional construction
4. Markov property of exponential kernel
5. Cosmological sector recovery
6. Collapse sector recovery
7. Bianchi compatibility
8. Route B comparison
9. Master classification
10. Phi ontology
11. Nonclaims completeness

STATUS: FUNCTIONAL-DERIVED — NONLOCAL STRESS-FUNCTIONAL. ROUTE C: ADVANCED.
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
# SECTION 1: Nonlocal Retarded Action
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 1: Nonlocal Retarded Action")
print("=" * 70)

from grut.nonlocal_stress import (
    build_nonlocal_action,
    analyze_metric_variation,
    construct_stress_functional,
    test_markov_property,
    verify_cosmo_reduction,
    verify_collapse_reduction,
    analyze_bianchi_compatibility,
    compare_to_route_b,
    compute_route_c_stress_analysis,
    stress_result_to_dict,
    _retarded_kernel,
    M_SUN,
)

action = build_nonlocal_action(tau_eff=1.0)

check("Kernel normalized", action.kernel_normalized)
check("Kernel norm ~ 1.0", abs(action.kernel_norm_value - 1.0) < 0.01,
      f"norm={action.kernel_norm_value:.6f}")
check("Kernel is causal", action.is_causal)
check("Kernel is real", action.is_real)
check("Markov property", action.markov_property)
check("Local auxiliary equivalent", action.local_auxiliary_equivalent)
check("Exponential kernel special >= 4", len(action.exponential_kernel_special) >= 4)
check("Nonclaims >= 4", len(action.nonclaims) >= 4)

# Verify kernel across different tau values
for tau_test in [0.1, 1.0, 10.0]:
    a = build_nonlocal_action(tau_eff=tau_test)
    check(f"Kernel normalized tau={tau_test}", a.kernel_normalized)

# Kernel causality: K(s<0) = 0
for s_test in [-1.0, -0.01, -100.0]:
    check(f"K({s_test}) = 0", _retarded_kernel(s_test, 1.0) == 0.0)

# Kernel peak: K(0) = 1/tau
check("K(0) = 1/tau", abs(_retarded_kernel(0.0, 2.0) - 0.5) < 1e-14)


# ============================================================================
# SECTION 2: Metric Variation Classification
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 2: Metric Variation Classification")
print("=" * 70)

mv = analyze_metric_variation()

check("Formal variation exists", mv.formal_variation_exists)
check("Variation is nonlocal", mv.variation_is_nonlocal)
check("Variation NOT local", not mv.variation_is_local)
check("5 explicit contributions", mv.n_explicit_contributions == 5)
check("NOT computed explicitly", not mv.computed_explicitly)
check("Obstruction > 200 chars", len(mv.obstruction_to_explicit) > 200)
check("Exponential local reduction exists", mv.exponential_local_reduction)
check("Local T^Phi form nonempty", len(mv.local_tphi_form) > 20)
check("Classification = nonlocal_stress_functional",
      mv.classification == "nonlocal_stress_functional")


# ============================================================================
# SECTION 3: Stress-Functional Construction
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 3: Stress-Functional Construction")
print("=" * 70)

sf = construct_stress_functional()

check("NOT local tensor (general)", not sf.is_local_tensor)
check("IS local for exponential kernel", sf.is_local_for_exponential_kernel)
check("Decomposition valid", sf.decomposition_valid)
check("Instantaneous form nonempty", len(sf.instantaneous_form) > 10)
check("History form nonempty", len(sf.history_form) > 10)
check("On-shell local form mentions Markov/exponential",
      "Markov" in sf.on_shell_local_form or "exponential" in sf.on_shell_local_form)
check("Classification = functional_derived", sf.classification == "functional_derived")
check("Derivation chain >= 5 steps", len(sf.derivation_chain) >= 5)
check("Cosmo rho_Phi form", len(sf.cosmo_rho_phi_form) > 10)
check("Cosmo p_Phi form", len(sf.cosmo_p_phi_form) > 10)
check("Collapse force form", len(sf.collapse_force_form) > 10)
check("Nonclaims >= 5", len(sf.nonclaims) >= 5)


# ============================================================================
# SECTION 4: Markov Property
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 4: Markov Property of Exponential Kernel")
print("=" * 70)

mt = test_markov_property(tau_eff=1.0, n_steps=2000, n_tau=10.0)

check("Markov holds", mt.markov_holds)
check("Phi match < 1e-6", mt.phi_match_rtol < 1e-6,
      f"rtol={mt.phi_match_rtol:.2e}")
check("T^Phi match < 1e-6", mt.tphi_match_rtol < 1e-6,
      f"rtol={mt.tphi_match_rtol:.2e}")
check("Phi_A ~ Phi_B",
      abs(mt.phi_A_final - mt.phi_B_final) / abs(mt.phi_A_final) < 1e-6)
check("rho_A ~ rho_B",
      abs(mt.tphi_A_rho - mt.tphi_B_rho) / max(abs(mt.tphi_A_rho), 1e-30) < 1e-6)
check("Non-exponential would fail", mt.non_exponential_would_fail)

# Test Markov across different tau
for tau_test in [0.5, 2.0, 10.0]:
    mt_t = test_markov_property(tau_eff=tau_test)
    check(f"Markov holds tau={tau_test}", mt_t.markov_holds)


# ============================================================================
# SECTION 5: Cosmological Sector Recovery
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 5: Cosmological Sector Recovery")
print("=" * 70)

cr = verify_cosmo_reduction(alpha_mem=0.1, tau_eff=1.0, n_steps=2000, n_tau=10.0)

check("Convolution-ODE equivalence", cr.convolution_ode_equivalence,
      f"max_error={cr.convolution_ode_max_error:.6f}")
check("Friedmann recovered", cr.friedmann_recovered)
check("Memory ODE recovered", cr.memory_ode_recovered,
      f"max_residual={cr.memory_residual_max:.2e}")
check("Tau coupling recovered", cr.tau_coupling_recovered)

# Different alpha values
for alpha_test in [0.01, 0.1, 0.3]:
    cr_a = verify_cosmo_reduction(alpha_mem=alpha_test, tau_eff=1.0)
    check(f"Cosmo recovered alpha={alpha_test}", cr_a.friedmann_recovered)


# ============================================================================
# SECTION 6: Collapse Sector Recovery
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 6: Collapse Sector Recovery")
print("=" * 70)

clr = verify_collapse_reduction()

check("Force balance recovered", clr.force_balance_recovered,
      f"residual={clr.equilibrium_residual:.2e}")
check("Memory ODE recovered", clr.memory_ode_recovered,
      f"residual={clr.memory_ode_residual:.2e}")
check("Endpoint recovered", clr.endpoint_recovered)

# Different masses
for M_test in [10.0 * M_SUN, 30.0 * M_SUN, 100.0 * M_SUN]:
    clr_m = verify_collapse_reduction(M_kg=M_test)
    check(f"Collapse recovered M={M_test/M_SUN:.0f} Msun", clr_m.force_balance_recovered)


# ============================================================================
# SECTION 7: Bianchi Compatibility
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 7: Bianchi Compatibility")
print("=" * 70)

ba = analyze_bianchi_compatibility(alpha_mem=0.1, tau_eff=1.0)

check("Cosmo sector verified", ba.cosmo_sector_verified,
      f"residual={ba.cosmo_consistency_residual:.6f}")
check("Collapse sector verified", ba.collapse_sector_verified)
check("Combined conservation expected", ba.combined_conservation_expected)
check("Full proof NOT available", not ba.full_proof_available)
check("Obstruction > 200 chars", len(ba.obstruction_to_full_proof) > 200)
check("Classification = effective_level_verified",
      ba.classification == "effective_level_verified")
check("Nonclaims >= 3", len(ba.nonclaims) >= 3)


# ============================================================================
# SECTION 8: Route B Comparison
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 8: Route B Comparison")
print("=" * 70)

comp = compare_to_route_b()

check("Same T^Phi expression", comp.tphi_expression_same)
check("Different derivation chain", comp.derivation_chain_different)
check("Complementary", comp.complementary)
check("Route B advantages >= 3", len(comp.route_b_advantages) >= 3)
check("Route C advantages >= 5", len(comp.route_c_advantages) >= 5)
check("Route B disadvantages >= 4", len(comp.route_b_disadvantages) >= 4)
check("Route C disadvantages >= 4", len(comp.route_c_disadvantages) >= 4)
check("Route C no ghost", "no ghost" in comp.route_c_ghost_status.lower())
check("Route B has growing mode", "growing" in comp.route_b_ghost_status.lower())
check("Route C no truncation needed",
      "not applicable" in comp.route_c_truncation_status.lower())
check("Overall complementary", "complementary" in comp.overall_assessment.lower())


# ============================================================================
# SECTION 9: Master Classification
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 9: Master Classification")
print("=" * 70)

result = compute_route_c_stress_analysis(
    alpha_mem=0.1, tau_eff=1.0, n_steps=2000, n_tau=10.0
)

check("Result valid", result.valid)
check("All components present",
      all([result.action, result.metric_variation, result.stress_functional,
           result.markov_test, result.cosmo_reduction, result.collapse_reduction,
           result.bianchi, result.route_b_comparison, result.classification]))

cls = result.classification
check("Action: formal_parent", cls.nonlocal_action == "formal_parent")
check("Metric variation: nonlocal_stress_functional",
      cls.metric_variation == "nonlocal_stress_functional")
check("Stress functional: functional_derived",
      cls.stress_functional == "functional_derived")
check("Cosmo: recovered", cls.cosmo_reduction == "recovered")
check("Collapse: recovered", cls.collapse_reduction == "recovered")
check("Bianchi: effective_level_verified", cls.bianchi == "effective_level_verified")
check("Overall: functional_derived", cls.overall == "functional_derived")
check("Route C vs B: complementary", "complementary" in cls.route_c_vs_b)
check("Phi ontology: effective_local_representation",
      cls.phi_ontology == "effective_local_representation")


# ============================================================================
# SECTION 10: Phi Ontology
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 10: Phi Ontology")
print("=" * 70)

check("Ontology = effective_local_representation",
      result.phi_ontology == "effective_local_representation")
check("Ontology explanation > 200 chars", len(result.phi_ontology_explanation) > 200)

ont_lower = result.phi_ontology_explanation.lower()
check("Mentions 'not a fundamental field'",
      "not" in ont_lower and "fundamental" in ont_lower)
check("Mentions retarded kernel",
      "retarded" in ont_lower or "kernel" in ont_lower)
check("Mentions Markov/Markovian",
      "markov" in ont_lower)
check("Mentions contingent on kernel",
      "contingent" in ont_lower or "kernel choice" in ont_lower)

check("Remaining obstruction > 300 chars", len(result.remaining_obstruction) > 300)
obs_lower = result.remaining_obstruction.lower()
check("Obstruction mentions nonlocal", "nonlocal" in obs_lower)
check("Obstruction mentions observer", "observer" in obs_lower)
check("Obstruction mentions Bianchi", "bianchi" in obs_lower)
check("Obstruction mentions quantization", "quantiz" in obs_lower)


# ============================================================================
# SECTION 11: Nonclaims and Serialization
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 11: Nonclaims and Serialization")
print("=" * 70)

check("Nonclaims >= 10", len(result.nonclaims) >= 10)

print("\n  Master nonclaims:")
for i, nc in enumerate(result.nonclaims, 1):
    print(f"    {i}. {nc}")

# Serialization
d = stress_result_to_dict(result)
check("Serialized valid=True", d["valid"] is True)
check("Serialized has action", d["action"] is not None)
check("Serialized has metric_variation", d["metric_variation"] is not None)
check("Serialized has stress_functional", d["stress_functional"] is not None)
check("Serialized has markov_test", d["markov_test"] is not None)
check("Serialized has cosmo", d["cosmo_reduction"] is not None)
check("Serialized has collapse", d["collapse_reduction"] is not None)
check("Serialized has bianchi", d["bianchi"] is not None)
check("Serialized has classification", d["classification"] is not None)
check("Serialized nonclaims >= 10", len(d["nonclaims"]) >= 10)
check("Serialized phi_ontology", d["phi_ontology"] == "effective_local_representation")


# ============================================================================
# STATUS REPORT
# ============================================================================

print("\n" + "=" * 70)
print("STATUS REPORT")
print("=" * 70)

print(f"""
  Route C Stress-Functional Analysis:
    Nonlocal action:        FORMAL PARENT (causal, normalized, Markov)
    Metric variation:       NONLOCAL STRESS-FUNCTIONAL (not local tensor of g)
    Exponential kernel:     MARKOV PROPERTY — local auxiliary equivalent
    Stress-functional:      FUNCTIONAL-DERIVED (intermediate: constitutive < this < action-derived)
    Cosmological reduction: RECOVERED (convolution = ODE, Friedmann, memory ODE)
    Collapse reduction:     RECOVERED (force balance, memory ODE, endpoint)
    Bianchi compatibility:  EFFECTIVE-LEVEL VERIFIED (not proven from action)
    Route C vs Route B:     COMPLEMENTARY (C avoids ghost; B has standard action)
    Phi ontology:           EFFECTIVE LOCAL REPRESENTATION (kernel is fundamental)
    Overall:                FUNCTIONAL-DERIVED — Route C ADVANCED
    Master nonclaims:       {len(result.nonclaims)}
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
    print("\n  All checks PASSED — Route C Stress-Functional Benchmark CLEAN")
    sys.exit(0)
