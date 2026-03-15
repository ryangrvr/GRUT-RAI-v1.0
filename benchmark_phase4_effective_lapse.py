#!/usr/bin/env python3
"""Benchmark: Phase IV — Effective Lapse Derivation.

Verifies the constitutive-derived effective lapse proxy analysis:
  1. Central algebraic result (barrier-to-gravity ratio)
  2. Route A (barrier-gravity ratio lapse proxy)
  3. Route B (effective metric — unresolved)
  4. Route C (Schwarzschild reference — upper bound)
  5. Route comparison
  6. Sensitivity / scenario band
  7. Three-level hierarchy
  8. Self-healing independence
  9. Shift estimates
  10. Coincidence explanation & beta_Q parametric scan
  11. Serialization round-trip
  12. Nonclaims completeness
"""

from __future__ import annotations

import json
import math
import sys

from grut.effective_lapse import (
    compute_effective_lapse_analysis,
    effective_lapse_result_to_dict,
    build_barrier_gravity_ratio,
    build_route_a,
    build_route_b,
    build_route_c,
    scan_beta_Q,
    _barrier_potential_ratio,
    ALPHA_VAC,
    BETA_Q,
    EPSILON_Q,
    C_ENDPOINT,
    Q_CANON,
    OMEGA_0_TAU_CANON,
    LEVEL_EXACT,
    LEVEL_CONSTITUTIVE_DERIVED,
    LEVEL_UNRESOLVED,
    LEVEL_UPPER_BOUND_ONLY,
)

passed = 0
failed = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {label}")
    else:
        failed += 1
        msg = f"  [FAIL] {label}"
        if detail:
            msg += f": {detail}"
        print(msg)


# ======================================================================
# Run master analysis
# ======================================================================

print("Building effective lapse analysis...")
result = compute_effective_lapse_analysis()
print(f"  Valid: {result.valid}")
print()

# ======================================================================
print("=" * 70)
print("SECTION 1: Central Algebraic Result (Barrier-to-Gravity Ratio)")
print("=" * 70)

bgr = result.barrier_gravity_ratio
check("Ratio = 1/3 for canon beta_Q=2",
      abs(bgr.ratio - 1.0 / 3.0) < 1e-15)
check("Ratio formula populated", len(bgr.ratio_formula) > 0)
check("Is exact", bgr.is_exact is True)
check("Independent of epsilon_Q", bgr.depends_on_epsilon_Q is False)
check("Independent of alpha_vac", bgr.depends_on_alpha_vac is False)
check("Independent of mass", bgr.depends_on_mass is False)
check("Endpoint law used", len(bgr.endpoint_law_used) > 10)
check("Derivation steps >= 4", len(bgr.derivation_steps) >= 4)

# Cross-check with different epsilon_Q
bgr2 = build_barrier_gravity_ratio(beta_Q=2.0, epsilon_Q=0.25)
check("Ratio unchanged with epsilon_Q=0.25",
      abs(bgr2.ratio - 1.0 / 3.0) < 1e-15)

# Check beta_Q = 3
bgr3 = build_barrier_gravity_ratio(beta_Q=3.0, epsilon_Q=ALPHA_VAC ** 3)
check("Ratio = 1/4 for beta_Q=3", abs(bgr3.ratio - 0.25) < 1e-15)

# ======================================================================
print()
print("=" * 70)
print("SECTION 2: Route A (Barrier-Gravity Ratio Lapse Proxy)")
print("=" * 70)

ra = result.routes.route_a
check("Psi_proxy = 1/3 canon", abs(ra.psi_proxy - 1.0 / 3.0) < 1e-15)
check("Classification = constitutive_derived",
      ra.classification == LEVEL_CONSTITUTIVE_DERIVED)
check("Route name correct", ra.route_name == "A_barrier_gravity_ratio")
check("Barrier ratio attached", ra.barrier_ratio is not None)
check("Identification basis mentions NOT true metric",
      "not" in ra.identification_basis.lower())
check("Notes populated", len(ra.notes) >= 3)

# ======================================================================
print()
print("=" * 70)
print("SECTION 3: Route B (Effective Metric — Unresolved)")
print("=" * 70)

rb = result.routes.route_b
check("A_schw = -2", abs(rb.A_schw_at_Req - (-2.0)) < 1e-10)
check("delta_A = 1", abs(rb.delta_A - 1.0) < 1e-10)
check("A_eff = -1", abs(rb.A_eff_at_Req - (-1.0)) < 1e-10)
check("A_eff is negative", rb.A_eff_is_negative is True)
check("Redshift formula NOT applicable", rb.redshift_formula_applicable is False)
check("psi_metric is None (unresolved)", rb.psi_metric is None)
check("Classification = unresolved", rb.classification == LEVEL_UNRESOLVED)
check("Obstruction populated", len(rb.obstruction) > 100)

# ======================================================================
print()
print("=" * 70)
print("SECTION 4: Route C (Schwarzschild Reference — Upper Bound)")
print("=" * 70)

rc = result.routes.route_c
check("Psi_Schw = 1.5", abs(rc.psi_schw - 1.5) < 1e-15)
check("Is upper bound", rc.is_upper_bound is True)
check("Classification = upper_bound_only",
      rc.classification == LEVEL_UPPER_BOUND_ONLY)
check("Psi_Schw > Route A proxy",
      rc.psi_schw > result.routes.route_a.psi_proxy)

# ======================================================================
print()
print("=" * 70)
print("SECTION 5: Route Comparison")
print("=" * 70)

cmp = result.routes
check("Preferred route = A", cmp.preferred_route == "A")
check("Preferred psi matches Route A",
      abs(cmp.preferred_psi_proxy - ra.psi_proxy) < 1e-15)
check("Preferred classification = constitutive_derived",
      cmp.preferred_classification == LEVEL_CONSTITUTIVE_DERIVED)
check("Route A < Route C",
      cmp.route_a.psi_proxy < cmp.route_c.psi_schw)
check("Route B not applicable", cmp.route_b.psi_metric is None)
check("Notes populated", len(cmp.notes) >= 3)

# ======================================================================
print()
print("=" * 70)
print("SECTION 6: Sensitivity / Scenario Band")
print("=" * 70)

sb = result.sensitivity_band
check("Central = 1/3", abs(sb.central - 1.0 / 3.0) < 1e-15)
check("Low = 1/6", abs(sb.low - 1.0 / 6.0) < 1e-15)
check("High = 2/3", abs(sb.high - 2.0 / 3.0) < 1e-15)
check("Low < Central < High", sb.low < sb.central < sb.high)
check("Numerically same as prior", sb.numerically_same_as_prior is True)
check("Central elevated from heuristic", sb.central_elevated is True)
check("Prior label = heuristic", sb.prior_central_label == "heuristic")
check("New label = constitutive_derived",
      sb.new_central_label == LEVEL_CONSTITUTIVE_DERIVED)

# ======================================================================
print()
print("=" * 70)
print("SECTION 7: Three-Level Hierarchy")
print("=" * 70)

tls = result.three_levels
check("Level 1 value = 1/3", abs(tls.level_1_value - 1.0 / 3.0) < 1e-15)
check("Level 1 status = exact", tls.level_1_status == LEVEL_EXACT)
check("Level 2 value = 1/3", abs(tls.level_2_value - 1.0 / 3.0) < 1e-15)
check("Level 2 status = constitutive_derived",
      tls.level_2_status == LEVEL_CONSTITUTIVE_DERIVED)
check("Level 3 value = None", tls.level_3_value is None)
check("Level 3 status = unresolved", tls.level_3_status == LEVEL_UNRESOLVED)
check("Level 3 obstruction populated", len(tls.level_3_obstruction) > 100)

# ======================================================================
print()
print("=" * 70)
print("SECTION 8: Self-Healing Independence")
print("=" * 70)

sh = result.self_healing
check("Source vanishes at eq", sh.source_vanishes is True)
check("Source ~ 0", abs(sh.source_at_eq) < 1e-14)
check("Independent of Psi", sh.independent_of_psi is True)
check("Preserved under Route A", sh.preserved_under_route_a is True)
check("Preserved under Route B", sh.preserved_under_route_b is True)
check("Preserved under Route C", sh.preserved_under_route_c is True)
check("Mechanism documented", len(sh.mechanism) > 100)

# ======================================================================
print()
print("=" * 70)
print("SECTION 9: Shift Estimates")
print("=" * 70)

se = result.shift_estimates
check("Psi proxy = 1/3", abs(se.psi_proxy_central - 1.0 / 3.0) < 1e-15)
check("Tau ratio = 3/4", abs(se.tau_ratio_central - 0.75) < 1e-14)
check("Proper-time shift > 0", se.proper_time_shift_pct > 0)
check("Q shift > 0", se.Q_shift_pct > 0)
check("omega_0*tau at eq = 3/4", abs(se.omega_0_tau_at_eq - 0.75) < 1e-14)

# ======================================================================
print()
print("=" * 70)
print("SECTION 10: Coincidence Explanation & beta_Q Scan")
print("=" * 70)

check("Prior heuristic confirmed", result.prior_heuristic_confirmed is True)
check("Prior heuristic elevated", result.prior_heuristic_elevated is True)
check("Coincidence explained", result.coincidence_explained is True)
check("Coincidence description populated",
      len(result.coincidence_description) > 50)

# beta_Q scan
scan = scan_beta_Q()
check("Scan returns >= 5 entries", len(scan) >= 5)
canon_entry = [r for r in scan if abs(r["beta_Q"] - 2.0) < 1e-10][0]
check("beta_Q=2 gives psi=1/3",
      abs(canon_entry["psi_proxy"] - 1.0 / 3.0) < 1e-15)
check("beta_Q=2 coincides with alpha_vac",
      canon_entry["coincides_with_alpha_vac"] is True)
non_canon = [r for r in scan if not r["coincides_with_alpha_vac"]]
check("Non-canon beta_Q do NOT coincide", len(non_canon) >= 4)

# ======================================================================
print()
print("=" * 70)
print("SECTION 11: Serialization")
print("=" * 70)

d = effective_lapse_result_to_dict(result)
check("Serialized to dict", isinstance(d, dict))
check("Serialized valid", d["valid"] is True)
check("Has barrier_gravity_ratio", "barrier_gravity_ratio" in d)
check("Has three_levels", "three_levels" in d)
check("Has routes", "routes" in d)
check("Has sensitivity_band", "sensitivity_band" in d)
check("Has self_healing", "self_healing" in d)
check("Route B psi_metric is None in serialized",
      d["routes"]["route_b"]["psi_metric"] is None)

# JSON round-trip
s = json.dumps(d)
d2 = json.loads(s)
check("JSON round-trip valid", d2["valid"] is True)
check("JSON round-trip ratio",
      abs(d2["barrier_gravity_ratio"]["ratio"] - 1.0 / 3.0) < 1e-15)

# ======================================================================
print()
print("=" * 70)
print("SECTION 12: Nonclaims")
print("=" * 70)

check("Nonclaims >= 15", len(result.nonclaims) >= 15)
ncs_text = " ".join(result.nonclaims).lower()
check("Mentions constitutive", "constitutive" in ncs_text)
check("Mentions coincidence", "coincidence" in ncs_text)
check("Mentions beta_q or beta", "beta" in ncs_text)
check("Mentions sub-horizon", "sub-horizon" in ncs_text)
check("Mentions self-healing", "self-healing" in ncs_text)
check("Mentions unresolved", "unresolved" in ncs_text)

print(f"\n  Nonclaims ({len(result.nonclaims)}):")
for i, nc in enumerate(result.nonclaims, 1):
    print(f"    {i}. {nc}")

# ======================================================================
print()
print("=" * 70)
print("STATUS REPORT")
print("=" * 70)

print(f"""
  Effective Lapse Derivation:
    Barrier-to-gravity ratio:     1/(1+beta_Q) = {bgr.ratio:.6f}  [EXACT, Level 1]
    Central lapse proxy:          {ra.psi_proxy:.6f}  [CONSTITUTIVE-DERIVED, Level 2]
    True interior metric lapse:   UNRESOLVED  [Level 3]
    Sensitivity band:             [{sb.low:.4f}, {sb.central:.4f}, {sb.high:.4f}]
    Prior heuristic band:         [0.1667, 0.3333, 0.6667]
    Prior band confirmed:         {'YES' if sb.numerically_same_as_prior else 'NO'}
    Central elevated from:        heuristic -> constitutive_derived
    Route A (barrier ratio):      Psi_proxy = {ra.psi_proxy:.6f} ({ra.classification})
    Route B (effective metric):   A_eff = {rb.A_eff_at_Req:.1f} -> {'UNRESOLVED' if rb.psi_metric is None else rb.psi_metric}
    Route C (Schwarzschild):      Psi_Schw = {rc.psi_schw:.1f} (upper bound)
    Self-healing:                 PRESERVED (Psi-independent)
    Proper-time shift:            {se.proper_time_shift_pct:.1f}%
    Q shift (bounded):            +{se.Q_shift_pct:.1f}%
    omega_0*tau at eq:            {se.omega_0_tau_at_eq:.4f}
    Coincidence alpha_vac = 1/(1+beta_Q): EXPLAINED (canon beta_Q=2 only)
    Nonclaims:                    {len(result.nonclaims)}
""")

# ======================================================================
print("=" * 70)
print(f"BENCHMARK RESULT: {passed} passed, {failed} failed")
print("=" * 70)

if failed == 0:
    print("\n  All checks PASSED — Effective Lapse Derivation Benchmark CLEAN")
else:
    print(f"\n  WARNING: {failed} check(s) FAILED")
    sys.exit(1)
