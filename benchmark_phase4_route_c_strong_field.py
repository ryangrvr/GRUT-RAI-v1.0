#!/usr/bin/env python3
"""Benchmark: Phase IV Route C — Strong-Field Lapse Correction.

Verifies the strong-field lapse correction analysis:
  1. Compactness scan with both lapse channels
  2. Endpoint self-healing proof
  3. Endpoint sensitivity (scenario scan)
  4. Proper-time vs coordinate-time comparison
  5. Ringdown bounded estimate
  6. Love number impact (bound only)
  7. Force balance impact
  8. Master classification and status-ladder impact
  9. Serialization round-trip
  10. Nonclaims completeness
"""

from __future__ import annotations

import json
import math
import sys

from grut.nonlocal_strong_field import (
    compute_strong_field_lapse_analysis,
    strong_field_lapse_result_to_dict,
    build_compactness_scan,
    build_endpoint_analysis,
    build_endpoint_sensitivity,
    _psi_schwarzschild,
    _psi_effective_proxy,
    _first_order_correction,
    _classify_correction,
    _tau_ratio,
    ALPHA_VAC,
    BETA_Q,
    EPSILON_Q,
    C_ENDPOINT,
    Q_CANON,
    OMEGA_0_TAU_CANON,
    ECHO_AMP_CANON_PCT,
    THRESH_NEGLIGIBLE,
    THRESH_BOUNDED_PERTURBATIVE,
    THRESH_BOUNDED_EXTRAPOLATED,
    THRESH_SIGNIFICANT,
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

print("Building Route C strong-field lapse analysis...")
result = compute_strong_field_lapse_analysis()
print(f"  Valid: {result.valid}")
print()

# ======================================================================
print("=" * 70)
print("SECTION 1: Compactness Scan")
print("=" * 70)

scan = result.scan
check("Scan valid", scan is not None)
check("Scan 30 points", scan.n_points == 30)
check("C_min = 0.05", abs(scan.C_min - 0.05) < 1e-10)
check("C_max = 3.0", abs(scan.C_max - 3.0) < 1e-10)
check("C values monotonic", all(
    scan.C_values[i] < scan.C_values[i + 1]
    for i in range(len(scan.C_values) - 1)
))
check("Both lapse channels populated", all(
    pt.Psi_Schw > 0 and pt.Psi_eff > 0 for pt in scan.points
))
check("Psi_eff <= Psi_Schw everywhere", all(
    pt.Psi_eff <= pt.Psi_Schw + 1e-15 for pt in scan.points
))
check("Correction Schw monotonic", all(
    scan.points[i].correction_Schw < scan.points[i + 1].correction_Schw
    for i in range(len(scan.points) - 1)
))
check("Regime boundaries ordered",
      scan.C_at_negligible_boundary < scan.C_at_perturbative_boundary
      < scan.C_at_extrapolated_boundary < scan.C_at_significant_boundary)
check("Regime counts sum to n_points",
      (scan.n_negligible + scan.n_bounded_perturbative
       + scan.n_bounded_extrapolated + scan.n_significant
       + scan.n_breakdown) == scan.n_points)
check("Has negligible points", scan.n_negligible >= 1)
check("Has breakdown points", scan.n_breakdown >= 1)
check("Weak-field point negligible",
      scan.points[0].classification_Schw == "negligible")
check("Strong-field point not negligible",
      scan.points[-1].classification_Schw != "negligible")

# Print regime table
print("\n  Regime table (Schwarzschild reference):")
print(f"    Negligible:           {scan.n_negligible} points"
      f" (C < {scan.C_at_negligible_boundary:.3f})")
print(f"    Bounded perturbative: {scan.n_bounded_perturbative} points")
print(f"    Bounded extrapolated: {scan.n_bounded_extrapolated} points")
print(f"    Significant:          {scan.n_significant} points")
print(f"    Breakdown:            {scan.n_breakdown} points"
      f" (C > {scan.C_at_significant_boundary:.3f})")

# ======================================================================
print()
print("=" * 70)
print("SECTION 2: Endpoint Self-Healing")
print("=" * 70)

ep = result.endpoint
check("C_endpoint = 3.0", abs(ep.C_endpoint - 3.0) < 1e-10)
check("R_eq/r_s = 1/3", abs(ep.R_eq_over_r_s - 1.0 / 3.0) < 1e-10)
check("Source vanishes at equilibrium", ep.source_vanishes)
check("Source term ~ 0", abs(ep.source_term_at_eq) < 1e-14)
check("Self-healing verified", ep.self_healing_verified)
check("Self-healing mechanism documented", len(ep.self_healing_mechanism) > 100)
check("Force balance preserved", ep.force_balance_preserved)
check("Endpoint law unaffected", ep.endpoint_law_unaffected)
check("Endpoint law independent of Psi", ep.endpoint_law_independence_of_Psi)
check("A_Schw = -2 at R_eq", abs(ep.A_Schw_at_Req - (-2.0)) < 1e-10)
check("Lapse below horizon", ep.lapse_below_horizon)
check("Psi_Schw = 1.5 at endpoint", abs(ep.Psi_Schw_at_endpoint - 1.5) < 1e-10)
check("Psi_eff < Psi_Schw at endpoint", ep.Psi_eff_nominal < ep.Psi_Schw_at_endpoint)
check("Psi_eff proxy type = heuristic", "heuristic" in ep.Psi_eff_proxy_type)
check("Transient peaks during approach", ep.transient_correction_peaks_during_approach)

# ======================================================================
print()
print("=" * 70)
print("SECTION 3: Endpoint Sensitivity (Scenario Scan)")
print("=" * 70)

es = result.sensitivity
check("Three scenarios present",
      es.Psi_eff_low > 0 and es.Psi_eff_nominal > 0 and es.Psi_eff_high > 0)
check("Low < Nominal < High",
      es.Psi_eff_low < es.Psi_eff_nominal < es.Psi_eff_high)
check("Low = alpha_vac/2", abs(es.Psi_eff_low - ALPHA_VAC / 2.0) < 1e-15)
check("Nominal = alpha_vac", abs(es.Psi_eff_nominal - ALPHA_VAC) < 1e-15)
check("High = 2*alpha_vac", abs(es.Psi_eff_high - 2.0 * ALPHA_VAC) < 1e-15)
check("Corrections ordered",
      es.correction_low < es.correction_nominal < es.correction_high)
check("Classifications populated",
      es.classification_low != "" and es.classification_nominal != ""
      and es.classification_high != "")
check("Q shifts ordered",
      es.Q_shift_low_pct < es.Q_shift_nominal_pct < es.Q_shift_high_pct)

print(f"\n  Sensitivity band:")
print(f"    Low:     Psi={es.Psi_eff_low:.4f}, corr={es.correction_low:.4f},"
      f" class={es.classification_low}, Q_shift={es.Q_shift_low_pct:.1f}%")
print(f"    Nominal: Psi={es.Psi_eff_nominal:.4f}, corr={es.correction_nominal:.4f},"
      f" class={es.classification_nominal}, Q_shift={es.Q_shift_nominal_pct:.1f}%")
print(f"    High:    Psi={es.Psi_eff_high:.4f}, corr={es.correction_high:.4f},"
      f" class={es.classification_high}, Q_shift={es.Q_shift_high_pct:.1f}%")

# ======================================================================
print()
print("=" * 70)
print("SECTION 4: Proper-Time vs Coordinate-Time")
print("=" * 70)

pt = result.proper_time
check("Proper-time comparison populated", len(pt.C_values) == 30)
check("Weak-field tau ratio ~ 1.0", pt.tau_ratio_Schw[0] > 0.95)
check("Strong-field tau ratio < 0.5", pt.tau_ratio_Schw[-1] < 0.5)
check("Tau ratio formula correct", all(
    abs(pt.tau_ratio_Schw[i] - 1.0 / (1.0 + pt.C_values[i] / 2.0)) < 1e-12
    for i in range(len(pt.C_values))
))
check("1% threshold computed", pt.C_at_1pct_shift_Schw > 0)
check("5% threshold > 1%", pt.C_at_5pct_shift_Schw > pt.C_at_1pct_shift_Schw)
check("10% threshold > 5%", pt.C_at_10pct_shift_Schw > pt.C_at_5pct_shift_Schw)
check("1% threshold reasonable (C ~ 0.02)",
      0.01 < pt.C_at_1pct_shift_Schw < 0.05)

# ======================================================================
print()
print("=" * 70)
print("SECTION 5: Ringdown Bounded Estimate")
print("=" * 70)

rb = result.ringdown
check("Framing = bounded_estimate", rb.framing == "bounded_estimate")
check("Q_canon = 6.0", abs(rb.Q_canon - Q_CANON) < 1e-10)
check("omega_0_tau_canon = 1.0", abs(rb.omega_0_tau_canon - OMEGA_0_TAU_CANON) < 1e-10)
check("Q shift > 0 (bounded)", rb.Q_shift_bounded_pct > 0)
check("Q shift < 100% (bounded)", rb.Q_shift_bounded_pct < 100.0)
check("omega_0_tau shift < 0 (bounded)", rb.omega_0_tau_shift_bounded < 0)
check("omega_0_tau at eq < 1 (bounded)", rb.omega_0_tau_at_eq_bounded < 1.0)
check("Echo correction bounded", 0 < rb.echo_correction_bounded_pct < 5.0)
check("Sensitivity: Q_low < Q_nom < Q_high",
      rb.Q_shift_low_pct < rb.Q_shift_bounded_pct < rb.Q_shift_high_pct)
check("Echo channel status populated", rb.echo_channel_status != "")

# ======================================================================
print()
print("=" * 70)
print("SECTION 6: Love Number Impact (Bound Only)")
print("=" * 70)

li = result.love
check("Love NOT computed", li.love_number_computed is False)
check("No value available", li.love_number_value_available is False)
check("Rigidity shift > 0", li.rigidity_shift_scale > 0)
check("Impact classification populated", li.impact_classification != "")
check("Requirements >= 3", len(li.requirements) >= 3)

# ======================================================================
print()
print("=" * 70)
print("SECTION 7: Force Balance Impact")
print("=" * 70)

fb = result.force_balance
check("Force balance preserved at eq", fb.force_balance_at_eq_preserved)
check("Delta force ~ 0", abs(fb.delta_force_at_eq) < 1e-14)
check("Transient correction > 0", fb.max_transient_correction_over_a_grav > 0)
check("Transient correction < 50%", fb.max_transient_correction_over_a_grav < 0.5)
check("Junction bounded", fb.junction_correction_bounded)
check("Junction scaling mentions Psi", "Psi" in fb.junction_correction_scaling)
check("Junction approx = effective level", "effective" in fb.junction_approx_level)
check("Nonclaims >= 3", len(fb.nonclaims) >= 3)

# ======================================================================
print()
print("=" * 70)
print("SECTION 8: Master Classification & Status-Ladder")
print("=" * 70)

mc = result.master
check("Classification = bounded", mc.classification == "bounded")
check("NOT canon_changing", mc.classification != "canon_changing")
check("Endpoint unaffected", mc.endpoint_unaffected)
check("Structural identity unaffected", mc.structural_identity_unaffected)
check("Force balance preserved", mc.force_balance_preserved)
check("Self-healing verified", mc.self_healing_verified)
check("Phase III preserved", mc.phase_iii_preserved)
check("Status ladder impact documented", len(mc.status_ladder_impact) > 100)
check("Status ladder preserved",
      "preserved" in mc.status_ladder_impact.lower()
      or "PRESERVED" in mc.status_ladder_impact)
check("Status ladder NOT modified", result.diagnostics["status_ladder_modified"] is False)
check("Cosmology regime = negligible", mc.regime_cosmology == "negligible")
check("Endpoint regime = self_healing", "self_healing" in mc.regime_endpoint)

# ======================================================================
print()
print("=" * 70)
print("SECTION 9: Serialization")
print("=" * 70)

d = strong_field_lapse_result_to_dict(result)
check("Serialized to dict", isinstance(d, dict))
check("Serialized valid", d["valid"] is True)
check("Serialized has scan", "scan" in d)
check("Serialized has endpoint", "endpoint" in d)
check("Serialized endpoint self-healing", d["endpoint"]["self_healing_verified"] is True)
check("Serialized has sensitivity", "sensitivity" in d)
check("Serialized has ringdown", "ringdown" in d)
check("Serialized ringdown framing", d["ringdown"]["framing"] == "bounded_estimate")
check("Serialized has love", "love" in d)
check("Serialized love NOT computed", d["love"]["love_number_computed"] is False)
check("Serialized has master", "master" in d)
check("Serialized master = bounded", d["master"]["classification"] == "bounded")

# JSON round-trip
s = json.dumps(d)
d2 = json.loads(s)
check("JSON round-trip valid", d2["valid"] is True)
check("JSON round-trip classification", d2["master"]["classification"] == "bounded")

# ======================================================================
print()
print("=" * 70)
print("SECTION 10: Nonclaims")
print("=" * 70)

check("Master nonclaims >= 15", len(result.nonclaims) >= 15)

ncs_text = " ".join(result.nonclaims).lower()
check("Mentions heuristic", "heuristic" in ncs_text)
check("Mentions bounded", "bounded" in ncs_text)
check("Mentions self-healing", "self-healing" in ncs_text or "self_healing" in ncs_text)
check("Mentions Love", "love" in ncs_text)
check("Mentions observer", "observer" in ncs_text)
check("Mentions quantization", "quantization" in ncs_text)

print(f"\n  Master nonclaims ({len(result.nonclaims)}):")
for i, nc in enumerate(result.nonclaims, 1):
    print(f"    {i}. {nc}")

# ======================================================================
print()
print("=" * 70)
print("STATUS REPORT")
print("=" * 70)

print(f"""
  Route C Strong-Field Lapse Correction:
    Compactness scan:         {scan.n_points} points, C in [{scan.C_min}, {scan.C_max}]
    Lapse channels:           Schwarzschild proxy + Effective GRUT proxy (heuristic)
    Source perturbation:      COMMUTES (from Part 1, exact)
    Kernel perturbation:      COMMUTES (from Part 1, exact)
    Lapse perturbation:       BOUNDED (strong-field scan)
    Endpoint self-healing:    VERIFIED (source term vanishes at equilibrium)
    Endpoint law (R/r_s=1/3): UNAFFECTED (independent of Psi)
    Force balance:            PRESERVED (self-healing)
    Structural identity:      PRESERVED (omega_0*tau=1 at equilibrium)
    Schwarzschild A at R_eq:  {ep.A_Schw_at_Req:.1f} (below horizon)
    Effective Psi at endpoint:{ep.Psi_eff_nominal:.4f} (heuristic, scenario band)
    Ringdown Q shift:         ~{rb.Q_shift_bounded_pct:.1f}% (bounded estimate, range {rb.Q_shift_low_pct:.1f}-{rb.Q_shift_high_pct:.1f}%)
    Echo channel:             {rb.echo_channel_status}
    Love numbers:             NOT COMPUTED (bound only: O({li.rigidity_shift_scale:.4f}))
    Master classification:    {mc.classification.upper()}
    Phase III status ladder:  PRESERVED
    Nonclaims:                {len(result.nonclaims)}
""")

# ======================================================================
print("=" * 70)
print(f"BENCHMARK RESULT: {passed} passed, {failed} failed")
print("=" * 70)

if failed == 0:
    print("\n  All checks PASSED — Route C Strong-Field Benchmark CLEAN")
else:
    print(f"\n  WARNING: {failed} check(s) FAILED")
    sys.exit(1)
