#!/usr/bin/env python3
"""Phase IV — Route C Follow-Up: Perturbative Nonlocal Metric Variation Benchmark.

Verifies the complete Route C perturbative metric variation analysis:

1. FRW perturbative background
2. Kernel tools and causality
3. Source perturbation commutation (Markov property)
4. Kernel (tau) perturbation commutation (three-way)
5. Lapse perturbation (coordinate mismatch, proper-time commutation)
6. Lapse magnitude estimates
7. Commutation summary
8. Route C upgrade assessment
9. Serialization
10. Master nonclaims

STATUS: PERTURBATIVELY VERIFIED (coordinate time) — Route C UPGRADED.
"""

from __future__ import annotations

import math
import json
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
# SECTION 1: FRW Perturbative Background
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 1: FRW Perturbative Background")
print("=" * 70)

from grut.nonlocal_metric_variation import (
    build_frw_perturbative_background,
    test_source_perturbation_commutation,
    test_tau_perturbation_commutation,
    test_lapse_perturbation_commutation,
    estimate_lapse_magnitude,
    build_commutation_summary,
    build_upgrade_assessment,
    compute_route_c_metric_variation_analysis,
    metric_variation_result_to_dict,
    _retarded_kernel,
    _retarded_kernel_tau_derivative,
    _proper_time_kernel,
    _analytical_lapse_correction,
)

bg = build_frw_perturbative_background(tau_eff=1.0, X_0=1.0, n_steps=2000, n_tau=10.0)

check("Background tau_eff = 1.0", bg.tau_eff == 1.0)
check("Background X_0 = 1.0", bg.X_0 == 1.0)
check("Time grid 2001 points", len(bg.times) == 2001)
check("Phi_0(0) = 0", abs(bg.Phi_0[0]) < 1e-14)
check("Phi_0(t>>tau) -> X_0", abs(bg.Phi_0[-1] - 1.0) < 1e-4)
check("dPhi_0/dt(0) = X_0/tau", abs(bg.dPhi_0_dt[0] - 1.0) < 1e-14)
check("dPhi_0/dt(t>>tau) -> 0", abs(bg.dPhi_0_dt[-1]) < 1e-4)
check("Analytical form populated", "exp" in bg.phi_0_form)
check("Notes >= 3", len(bg.notes) >= 3)

# Different tau values
for tau_test in [0.5, 2.0, 5.0]:
    bg_t = build_frw_perturbative_background(tau_eff=tau_test)
    check(f"Background valid tau={tau_test}", abs(bg_t.Phi_0[-1] - 1.0) < 0.01)


# ============================================================================
# SECTION 2: Kernel Tools
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 2: Kernel Tools and Causality")
print("=" * 70)

# Causality
for s in [-1.0, -0.01, -100.0]:
    check(f"K({s}) = 0 (causal)", _retarded_kernel(s, 1.0) == 0.0)
    check(f"dK/dtau({s}) = 0 (causal)", _retarded_kernel_tau_derivative(s, 1.0) == 0.0)
    check(f"K_proper({s}) = 0 (causal)", _proper_time_kernel(s, 1.0, 0.01) == 0.0)

# Peak
check("K(0) = 1/tau", abs(_retarded_kernel(0.0, 2.0) - 0.5) < 1e-14)

# Tau derivative sign change
check("dK/dtau < 0 for s < tau", _retarded_kernel_tau_derivative(0.5, 1.0) < 0)
check("dK/dtau = 0 at s = tau", abs(_retarded_kernel_tau_derivative(1.0, 1.0)) < 1e-14)
check("dK/dtau > 0 for s > tau", _retarded_kernel_tau_derivative(2.0, 1.0) > 0)

# Proper-time kernel reduces to standard at Psi=0
for s in [0.0, 0.5, 1.0, 3.0]:
    check(f"K_proper(s={s}, Psi=0) = K(s={s})",
          abs(_proper_time_kernel(s, 1.0, 0.0) - _retarded_kernel(s, 1.0)) < 1e-14)


# ============================================================================
# SECTION 3: Source Perturbation Commutation
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 3: Source Perturbation Commutation (Markov Property)")
print("=" * 70)

st = test_source_perturbation_commutation(bg, delta_X_amplitude=0.1)

check("Source commutes", st.commutes)
check("Source max_rel < 0.05", st.max_relative_mismatch < 0.05,
      f"max_rel={st.max_relative_mismatch:.6e}")
check("Source max_abs < 0.01", st.max_absolute_mismatch < 0.01,
      f"max_abs={st.max_absolute_mismatch:.6e}")
check("Source arrays populated", len(st.delta_phi_convolution) == 2001)
check("Source IC: conv[0] = 0", st.delta_phi_convolution[0] == 0.0)
check("Source IC: ode[0] = 0", st.delta_phi_ode[0] == 0.0)
check("Source form populated", "sin" in st.delta_X_form)

# Different amplitudes
for amp in [0.01, 0.1, 0.5]:
    st_a = test_source_perturbation_commutation(bg, delta_X_amplitude=amp)
    check(f"Source commutes amp={amp}", st_a.commutes)


# ============================================================================
# SECTION 4: Tau Perturbation Commutation
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 4: Kernel (Tau) Perturbation Commutation")
print("=" * 70)

tt = test_tau_perturbation_commutation(bg, delta_tau_fraction=0.01)

check("Tau conv-ODE commutes", tt.conv_ode_commutes)
check("Tau conv-analytical commutes", tt.conv_analytical_commutes)
check("Tau ODE-analytical commutes", tt.ode_analytical_commutes)
check("Tau conv-ODE mismatch < 0.05", tt.conv_ode_max_mismatch < 0.05,
      f"mismatch={tt.conv_ode_max_mismatch:.6e}")
check("Tau ODE-analytical < 0.01", tt.ode_analytical_max_mismatch < 0.01,
      f"mismatch={tt.ode_analytical_max_mismatch:.6e}")
check("Tau analytical form populated", "exp" in tt.delta_phi_analytical_form)
check("Tau delta recorded", abs(tt.delta_tau - 0.01) < 1e-14)

# Different fractions
for frac in [0.001, 0.01, 0.05]:
    tt_f = test_tau_perturbation_commutation(bg, delta_tau_fraction=frac)
    check(f"Tau commutes frac={frac}", tt_f.conv_ode_commutes)


# ============================================================================
# SECTION 5: Lapse Perturbation
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 5: Lapse Perturbation (KEY TEST)")
print("=" * 70)

lt = test_lapse_perturbation_commutation(bg, Psi=0.01)

check("Coord does NOT commute", not lt.coordinate_commutes)
check("Proper DOES commute", lt.proper_commutes)
check("Analytical verified", lt.lapse_analytical_verified)
check("Coord mismatch > 0.5", lt.coord_vs_proper_relative_mismatch > 0.5,
      f"mismatch={lt.coord_vs_proper_relative_mismatch:.4f}")
check("Proper mismatch < 0.05", lt.proper_vs_proper_relative_mismatch < 0.05,
      f"mismatch={lt.proper_vs_proper_relative_mismatch:.6e}")
check("Peak value = Psi*X/e",
      abs(lt.lapse_peak_value - 0.01 / math.e) < 1e-14)
check("Peak time = tau", lt.lapse_peak_time_over_tau == 1.0)
check("Correction form populated", "Psi" in lt.lapse_correction_form)
check("Coord ODE is zero", all(v == 0.0 for v in lt.delta_phi_coordinate_ode))

# Different Psi values (perturbative regime: Psi << 1)
for psi in [0.001, 0.01, 0.05]:
    lt_p = test_lapse_perturbation_commutation(bg, Psi=psi)
    check(f"Proper commutes Psi={psi}", lt_p.proper_commutes)
    check(f"Coord fails Psi={psi}", not lt_p.coordinate_commutes)

# Psi=0.1 is at the edge: O(Psi^2) corrections break first-order commutation
lt_large = test_lapse_perturbation_commutation(bg, Psi=0.1)
check("Psi=0.1: coord still fails", not lt_large.coordinate_commutes)
check("Psi=0.1: O(Psi^2) breaks first-order",
      lt_large.proper_vs_proper_relative_mismatch > 0.05)


# ============================================================================
# SECTION 6: Lapse Magnitude Estimates
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 6: Lapse Magnitude Estimates")
print("=" * 70)

lm = estimate_lapse_magnitude()

check("Cosmo negligible", lm.cosmo_negligible)
check("Collapse NOT negligible", not lm.collapse_negligible)
check("Cosmo Psi = 1e-5", lm.Psi_cosmo == 1e-5)
check("Collapse Psi ~ 1/6", abs(lm.Psi_collapse - 1.0 / 6.0) < 1e-10)
check("Cosmo dPhi/Phi < 1e-4", lm.delta_phi_over_phi_cosmo < 1e-4)
check("Collapse dPhi/Phi ~ 6%",
      0.05 < lm.delta_phi_over_phi_collapse < 0.07,
      f"value={lm.delta_phi_over_phi_collapse:.4f}")
check("Weak field safe", lm.weak_field_safe)
check("Strong field correction needed", lm.strong_field_correction_needed)
check("Notes >= 4", len(lm.notes) >= 4)


# ============================================================================
# SECTION 7: Commutation Summary
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 7: Commutation Summary")
print("=" * 70)

result = compute_route_c_metric_variation_analysis(
    tau_eff=1.0, X_0=1.0, n_steps=2000, n_tau=10.0
)
cs = result.commutation

check("Source commutes", cs.source_commutes)
check("Tau commutes", cs.tau_commutes)
check("Lapse coordinate FAILS", not cs.lapse_coordinate_commutes)
check("Lapse proper commutes", cs.lapse_proper_commutes)
check("Overall coord-time commutes", cs.overall_coordinate_time_commutes)
check("Overall proper-time commutes", cs.overall_proper_time_commutes)
check("Covariant mismatch source populated",
      len(cs.covariant_mismatch_source) > 50)
check("Covariant mismatch form populated",
      "delta_Phi" in cs.covariant_mismatch_form)
check("Mismatch order = first_order_in_Psi",
      cs.covariant_mismatch_order == "first_order_in_Psi")
check("Perturbative order populated", "first_order" in cs.perturbative_order)
check("Nonclaims >= 4", len(cs.nonclaims) >= 4)


# ============================================================================
# SECTION 8: Route C Upgrade Assessment
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 8: Route C Upgrade Assessment")
print("=" * 70)

up = result.upgrade

check("Upgraded = True", up.upgraded)
check("Previous = functional_derived", up.previous_status == "functional_derived")
check("Current = perturbatively_verified__coordinate_time",
      up.current_status == "perturbatively_verified__coordinate_time")
check("Upgrade reason > 100 chars", len(up.upgrade_reason) > 100)
check("Upgrade scope mentions FRW", "FRW" in up.upgrade_scope)
check("Limitations >= 5", len(up.upgrade_limitations) >= 5)
check("Remaining obstruction > 200 chars", len(up.remaining_obstruction) > 200)
check("Obstruction mentions lapse", "lapse" in up.remaining_obstruction.lower())
check("Severity mentions MILD", "MILD" in up.remaining_obstruction_severity)


# ============================================================================
# SECTION 9: Serialization
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 9: Serialization")
print("=" * 70)

d = metric_variation_result_to_dict(result)

check("Serialized valid=True", d["valid"] is True)
check("Serialized has background", d["background"] is not None)
check("Serialized has source_test", d["source_test"] is not None)
check("Serialized source commutes", d["source_test"]["commutes"] is True)
check("Serialized has tau_test", d["tau_test"] is not None)
check("Serialized tau commutes", d["tau_test"]["conv_ode_commutes"] is True)
check("Serialized has lapse_test", d["lapse_test"] is not None)
check("Serialized lapse coord fails", d["lapse_test"]["coordinate_commutes"] is False)
check("Serialized lapse proper passes", d["lapse_test"]["proper_commutes"] is True)
check("Serialized has lapse_magnitude", d["lapse_magnitude"] is not None)
check("Serialized has commutation", d["commutation"] is not None)
check("Serialized overall coord commutes",
      d["commutation"]["overall_coordinate_time_commutes"] is True)
check("Serialized has upgrade", d["upgrade"] is not None)
check("Serialized upgrade=True", d["upgrade"]["upgraded"] is True)
check("Serialized nonclaims >= 12", len(d["nonclaims"]) >= 12)
check("Serialized diagnostics present", len(d["diagnostics"]) >= 8)

# JSON round-trip
json_str = json.dumps(d, default=str)
d2 = json.loads(json_str)
check("JSON round-trip valid", d2["valid"] is True)
check("JSON round-trip upgrade", d2["upgrade"]["upgraded"] is True)


# ============================================================================
# SECTION 10: Master Nonclaims
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 10: Master Nonclaims")
print("=" * 70)

check("Nonclaims >= 12", len(result.nonclaims) >= 12)

print("\n  Master nonclaims:")
for i, nc in enumerate(result.nonclaims, 1):
    print(f"    {i}. {nc}")

nc_lower = " ".join(result.nonclaims).lower()
check("Mentions perturbative", "perturbative" in nc_lower or "first" in nc_lower)
check("Mentions nonlinear", "nonlinear" in nc_lower)
check("Mentions observer", "observer" in nc_lower)
check("Mentions quantization", "quantiz" in nc_lower)
check("Mentions lapse", "lapse" in nc_lower)
check("Mentions exponential kernel", "exponential" in nc_lower)


# ============================================================================
# STATUS REPORT
# ============================================================================

print("\n" + "=" * 70)
print("STATUS REPORT")
print("=" * 70)

print(f"""
  Route C Perturbative Metric Variation:
    FRW background:         VALID (constant source, analytical benchmark)
    Source perturbation:     COMMUTES (Markov property, max_rel={result.source_test.max_relative_mismatch:.2e})
    Kernel perturbation:    COMMUTES (three-way, conv-ode mismatch={result.tau_test.conv_ode_max_mismatch:.2e})
    Lapse (coord time):     DOES NOT COMMUTE (expected, rel_mismatch={result.lapse_test.coord_vs_proper_relative_mismatch:.2f})
    Lapse (proper time):    COMMUTES (rel_mismatch={result.lapse_test.proper_vs_proper_relative_mismatch:.2e})
    Lapse analytical:       VERIFIED (mismatch={result.lapse_test.lapse_analytical_vs_numerical_mismatch:.2e})
    Cosmo lapse magnitude:  NEGLIGIBLE (Psi ~ 1e-5, dPhi/Phi ~ {result.lapse_magnitude.delta_phi_over_phi_cosmo:.1e})
    Collapse lapse mag:     SIGNIFICANT (Psi ~ 1/6, dPhi/Phi ~ {result.lapse_magnitude.delta_phi_over_phi_collapse*100:.1f}%)
    Overall (coord time):   COMMUTES
    Overall (proper time):  COMMUTES
    Route C status:         UPGRADED: functional_derived -> perturbatively_verified__coordinate_time
    Nonclaims:              {len(result.nonclaims)}
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
    print("\n  All checks PASSED — Route C Metric Variation Benchmark CLEAN")
    sys.exit(0)
