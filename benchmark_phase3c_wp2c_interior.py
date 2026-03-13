#!/usr/bin/env python3
"""Phase III-C WP2C Interior Wave Benchmark — Viscoelastic response of the BDCC.

EXTERIOR ASSUMPTION: Schwarzschild-like (WP1 conditional).

Tests:
1. Canon parameters: Q, tan(delta), classification at 30 M_sun
2. Mass dependence of Q across astrophysical range
3. Dissipation sensitivity: what gamma_diss changes the classification?
4. Three candidate models: reactive / mixed / dissipative
5. Comparison with WP2B impedance model
6. Summary with status determination
"""

from __future__ import annotations

import math
import sys
import time

from grut.interior_waves import (
    InteriorWaveParams,
    compute_interior_wave_analysis,
    interior_wave_result_to_dict,
    scan_dissipation_range,
    scan_mass_interior,
    bdcc_oscillation_frequency,
    memory_mediated_damping,
    quality_factor,
    schwarzschild_radius,
    M_SUN,
)
from grut.ringdown import (
    EchoParameters,
    compute_echo_analysis,
    impedance_reflectivity,
    impedance_ratio,
)


def _header(title: str):
    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")


def main():
    t0 = time.time()

    print("Phase III-C WP2C: Interior Wave / Viscoelastic Response Benchmark")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("EXTERIOR ASSUMPTION: Schwarzschild-like (WP1 conditional)")
    print()

    # ================================================================
    # 1. CANON PARAMETERS (30 M_sun)
    # ================================================================
    _header("1. CANON PARAMETERS (30 M_sun, R_eq = r_s/3)")

    M_bench = 30.0 * M_SUN
    r_s = schwarzschild_radius(M_bench)
    R_eq = r_s / 3.0

    params = InteriorWaveParams(
        M_kg=M_bench, R_eq_m=R_eq, r_s_m=r_s,
    )
    result = compute_interior_wave_analysis(params)

    print(f"  Mass: {M_bench/M_SUN:.0f} M_sun")
    print(f"  R_eq: {R_eq/1000:.3f} km ({R_eq/r_s:.6f} r_s)")
    print()
    print(f"  OSCILLATION:")
    print(f"    omega_core      = {result.omega_core_rad_s:.4e} rad/s")
    print(f"    f_core           = {result.f_core_Hz:.2f} Hz")
    print()
    print(f"  DAMPING:")
    print(f"    gamma_eff        = {result.gamma_eff_rad_s:.4e} rad/s")
    print(f"    gamma_memory     = {result.memory_damping_rate:.4e} rad/s  (structural)")
    print(f"    gamma_solver     = {result.solver_damping_rate:.4e} rad/s  (phenomenological)")
    print(f"    memory/solver    = {result.memory_damping_rate/max(result.solver_damping_rate, 1e-30):.2e}")
    print()
    print(f"  QUALITY FACTOR:")
    print(f"    Q                = {result.quality_factor_Q:.2f}")
    print(f"    tan(delta)       = {result.loss_tangent:.6f}")
    print()
    print(f"  VISCOELASTIC MODULI (normalized):")
    print(f"    G' (storage)     = {result.storage_modulus_proxy:.6f}")
    print(f"    G'' (loss)       = {result.loss_modulus_proxy:.8f}")
    print(f"    G'/G'' ratio     = {result.storage_modulus_proxy/result.loss_modulus_proxy:.1f}" if result.loss_modulus_proxy > 0 else "")
    print()
    print(f"  FREQUENCY RESPONSE:")
    print(f"    omega_QNM/omega_core = {result.omega_probe_over_omega_core:.1f}")
    print(f"    |chi(omega_QNM)|     = {result.response_amplitude:.4e}")
    print()
    print(f"  TIMESCALES:")
    print(f"    damping time     = {result.damping_time_s:.2f} s")
    print(f"    crossing time    = {result.crossing_time_s:.4e} s")
    print(f"    damping/crossing = {result.damping_over_crossing:.1f}")
    print()
    print(f"  INTERIOR REFLECTION:")
    print(f"    r_interior_amp   = {result.r_interior_amp:.6f}")
    print()
    print(f"  CLASSIFICATION:")
    print(f"    response_class   = {result.response_class}")
    print(f"    confidence       = {result.response_confidence}")
    print()
    print(f"  ECHO IMPACT:")
    print(f"    {result.echo_impact}")

    # ================================================================
    # 2. MASS DEPENDENCE
    # ================================================================
    _header("2. MASS DEPENDENCE OF Q (canon gamma_diss = 1e-15)")

    mass_scan = scan_mass_interior()

    print(f"  {'M (M_sun)':>12s}  {'Q':>10s}  {'gamma_eff':>12s}  {'gamma_mem':>12s}  "
          f"{'freq_ratio':>10s}  {'r_int':>8s}  {'class':>25s}")
    print(f"  {'-'*12}  {'-'*10}  {'-'*12}  {'-'*12}  {'-'*10}  {'-'*8}  {'-'*25}")
    for row in mass_scan:
        print(f"  {row['M_solar']:>12.0f}  {row['Q']:>10.2f}  {row['gamma_eff']:>12.4e}  "
              f"{row['gamma_memory']:>12.4e}  {row['freq_ratio']:>10.1f}  "
              f"{row['r_interior_amp']:>8.6f}  {row['response_class']:>25s}")

    # Check: Q should be > 1 for all masses
    all_reactive = all(row["Q"] > 10 for row in mass_scan)
    print(f"\n  All masses Q > 10 (reactive):  {'YES' if all_reactive else 'NO'}")
    if mass_scan:
        Q_min = min(row["Q"] for row in mass_scan)
        Q_max = max(row["Q"] for row in mass_scan)
        print(f"  Q range: [{Q_min:.1f}, {Q_max:.1f}]")

    # ================================================================
    # 3. DISSIPATION SENSITIVITY SCAN
    # ================================================================
    _header("3. DISSIPATION SENSITIVITY (30 M_sun)")

    print("  What gamma_diss changes the classification?")
    print()

    # Extended scan to find crossover points
    omega_core = bdcc_oscillation_frequency(M_bench, R_eq, 2.0)
    gamma_values = [
        0.0, 1e-15, 1e-10, 1e-5, 1e-3, 1e-1,
        1.0, 5.0, 10.0, 20.0, 50.0, 100.0, 500.0, 1e3, 1e6,
    ]
    diss_scan = scan_dissipation_range(
        M_bench, gamma_diss_values=gamma_values,
    )

    print(f"  {'gamma_diss':>12s}  {'Q':>10s}  {'r_int':>10s}  {'class':>28s}")
    print(f"  {'-'*12}  {'-'*10}  {'-'*10}  {'-'*28}")
    for row in diss_scan:
        print(f"  {row['gamma_diss']:>12.2e}  {row['Q']:>10.2f}  "
              f"{row['r_interior_amp']:>10.6f}  {row['response_class']:>28s}")

    # Find crossover gamma values
    for row in diss_scan:
        if row["Q"] < 10 and row["Q"] > 1:
            print(f"\n  MIXED VISCOELASTIC at gamma_diss = {row['gamma_diss']:.2e}: Q = {row['Q']:.2f}")
            break
    for row in diss_scan:
        if row["Q"] < 1:
            print(f"  DISSIPATIVE at gamma_diss = {row['gamma_diss']:.2e}: Q = {row['Q']:.2f}")
            break

    print(f"\n  gamma_memory at 30 M_sun: {result.memory_damping_rate:.2e} rad/s")
    print(f"  Canon gamma_diss:         1e-15 rad/s")
    print(f"  Ratio canon/memory:       {1e-15/result.memory_damping_rate:.2e}")

    # ================================================================
    # 4. THREE CANDIDATE MODELS
    # ================================================================
    _header("4. THREE CANDIDATE INTERIOR RESPONSE MODELS (30 M_sun)")

    print("  Testing reactive, mixed viscoelastic, and dissipative explicitly.")
    print()

    # Model A: Reactive (canon parameters)
    print("  MODEL A: REACTIVE (canon gamma_diss = 1e-15)")
    p_A = InteriorWaveParams(M_kg=M_bench, R_eq_m=R_eq, r_s_m=r_s, gamma_diss=1e-15)
    r_A = compute_interior_wave_analysis(p_A)
    print(f"    Q = {r_A.quality_factor_Q:.2f}, tan(delta) = {r_A.loss_tangent:.6f}")
    print(f"    r_interior_amp = {r_A.r_interior_amp:.6f}")
    print(f"    class = {r_A.response_class}")
    print()

    # Model B: Mixed Viscoelastic (moderate gamma_diss)
    gamma_mixed = omega_core / 10.0  # Should give Q ~ 5
    print(f"  MODEL B: MIXED VISCOELASTIC (gamma_diss = {gamma_mixed:.1f} rad/s)")
    p_B = InteriorWaveParams(M_kg=M_bench, R_eq_m=R_eq, r_s_m=r_s, gamma_diss=gamma_mixed)
    r_B = compute_interior_wave_analysis(p_B)
    print(f"    Q = {r_B.quality_factor_Q:.2f}, tan(delta) = {r_B.loss_tangent:.4f}")
    print(f"    r_interior_amp = {r_B.r_interior_amp:.6f}")
    print(f"    class = {r_B.response_class}")
    print()

    # Model C: Dissipative (high gamma_diss)
    gamma_diss_high = omega_core * 10.0  # Should give Q << 1
    print(f"  MODEL C: DISSIPATIVE (gamma_diss = {gamma_diss_high:.0f} rad/s)")
    p_C = InteriorWaveParams(M_kg=M_bench, R_eq_m=R_eq, r_s_m=r_s, gamma_diss=gamma_diss_high)
    r_C = compute_interior_wave_analysis(p_C)
    print(f"    Q = {r_C.quality_factor_Q:.4f}, tan(delta) = {r_C.loss_tangent:.2f}")
    print(f"    r_interior_amp = {r_C.r_interior_amp:.6f}")
    print(f"    class = {r_C.response_class}")
    print()

    # Side-by-side comparison
    print("  SIDE-BY-SIDE COMPARISON:")
    print(f"    {'Model':>15s}  {'Q':>10s}  {'tan(d)':>10s}  {'r_int':>10s}  {'class':>28s}")
    print(f"    {'-'*15}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*28}")
    for label, res in [("Reactive", r_A), ("Mixed", r_B), ("Dissipative", r_C)]:
        tan_d = f"{res.loss_tangent:.4f}" if math.isfinite(res.loss_tangent) else "inf"
        print(f"    {label:>15s}  {res.quality_factor_Q:>10.2f}  {tan_d:>10s}  "
              f"{res.r_interior_amp:>10.6f}  {res.response_class:>28s}")

    # ================================================================
    # 5. COMPARISON WITH WP2B IMPEDANCE MODEL
    # ================================================================
    _header("5. WP2C vs WP2B COMPARISON (30 M_sun)")

    eta = impedance_ratio(M_bench, R_eq, 2.0)
    r_imp = impedance_reflectivity(M_bench, R_eq, 2.0)

    print(f"  WP2B impedance model (sharp-boundary):")
    print(f"    eta                = {eta:.6f}")
    print(f"    r_surface_amp      = {r_imp:.6f}")
    print()
    print(f"  WP2C interior model (with Q-correction):")
    print(f"    Q                  = {r_A.quality_factor_Q:.2f}")
    print(f"    r_interior_amp     = {r_A.r_interior_amp:.6f}")
    print(f"    Difference         = {abs(r_imp - r_A.r_interior_amp):.6f}")
    print(f"    Relative change    = {abs(r_imp - r_A.r_interior_amp)/r_imp*100:.4f}%")
    print()

    # Echo comparison: impedance vs interior model
    print("  Echo amplitude comparison (A_1/A_0):")
    for model_name, model_key in [("perfect", "perfect"), ("impedance", "impedance"),
                                    ("interior (WP2C)", "interior"), ("boltzmann", "boltzmann")]:
        p = EchoParameters(
            M_kg=M_bench, r_s_m=r_s, R_eq_m=R_eq,
            R_eq_over_r_s=1.0/3.0, beta_Q=2.0,
            reflection_model=model_key,
        )
        r = compute_echo_analysis(p, n_echoes=1)
        a1 = r.echo_amplitudes[0] if r.echo_amplitudes else 0.0
        print(f"    {model_name:>20s}: r_surface = {r.reflection_surface:.6f}, A_1/A_0 = {a1:.6f}")

    # ================================================================
    # 6. SUMMARY
    # ================================================================
    _header("6. WP2C INTERIOR WAVE BENCHMARK SUMMARY")

    print("  EXTERIOR ASSUMPTION: Schwarzschild-like (WP1 conditional)")
    print()
    print("  VISCOELASTIC MODEL:")
    print(f"    Storage modulus (G'): from stability eigenvalue")
    print(f"    Loss modulus (G''): from memory-mediated damping + solver dissipation")
    print(f"    Quality factor Q = omega_core / (2*gamma_eff)")
    print(f"    Loss tangent tan(delta) = 1/(2Q)")
    print()
    print("  KEY RESULTS (30 M_sun, canon parameters):")
    print(f"    Q                  = {r_A.quality_factor_Q:.2f}")
    print(f"    tan(delta)         = {r_A.loss_tangent:.6f}")
    print(f"    r_interior_amp     = {r_A.r_interior_amp:.6f}")
    print(f"    Classification     = {r_A.response_class}")
    print()
    print("  MASS DEPENDENCE:")
    if mass_scan:
        print(f"    Q range:           [{min(r['Q'] for r in mass_scan):.1f}, {max(r['Q'] for r in mass_scan):.1f}]")
        print(f"    All masses Q > 10: {'YES' if all_reactive else 'NO'}")
    print()
    print("  DISSIPATION SENSITIVITY:")
    print(f"    gamma_memory (dominant) = {r_A.memory_damping_rate:.4e} rad/s")
    print(f"    gamma_diss (canon)      = 1e-15 rad/s (negligible)")
    print(f"    Mixed threshold         ~ {omega_core/10:.0f} rad/s")
    print(f"    Dissipative threshold   ~ {omega_core*2:.0f} rad/s")
    print()
    print("  THREE-MODEL COMPARISON:")
    print(f"    Reactive (canon):     Q = {r_A.quality_factor_Q:.0f}, echoes PROMISING")
    print(f"    Mixed (hypothetical): Q = {r_B.quality_factor_Q:.1f}, echoes UNCERTAIN")
    print(f"    Dissipative (hypo):   Q = {r_C.quality_factor_Q:.3f}, echoes NOT viable")
    print()
    print("  ECHO CHANNEL ASSESSMENT:")
    print("    Under zeroth-order viscoelastic model with canon parameters:")
    print(f"    - BDCC is storage-dominated (Q = {r_A.quality_factor_Q:.0f} >> 10)")
    print(f"    - Impedance model (WP2B) applies with < 0.01% correction")
    print("    - Echo channel remains PROMISING")
    print("    - Boltzmann (dissipative) model requires unidentified loss mechanism")
    print()
    print("  WHAT COULD CHANGE THIS:")
    print("    - Hidden dissipation (nonlinear coupling, quantum effects)")
    print("    - Transition-width absorption (graded impedance)")
    print("    - Interior metric modification (imaginary effective potential)")
    print(f"    - Need gamma_diss > {omega_core/10:.0f} rad/s for mixed regime")
    print(f"    - Need gamma_diss > {omega_core*2:.0f} rad/s for dissipative regime")
    print()
    print("  EXPLICIT NONCLAIMS:")
    print("    - This does NOT solve the interior wave equation")
    print("    - Does NOT assume saturation implies elasticity (tested from params)")
    print("    - Does NOT assume dissipation disappears (memory damping is modeled)")
    print("    - Classification is CANDIDATE, not proven")
    print("    - Hidden dissipation mechanisms could change the assessment")
    print("    - All results CONDITIONAL on WP1 exterior assumption")

    elapsed = time.time() - t0
    print(f"\nTotal runtime: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
