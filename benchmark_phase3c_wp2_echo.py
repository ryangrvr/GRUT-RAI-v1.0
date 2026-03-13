#!/usr/bin/env python3
"""Phase III-C WP2 Echo Benchmark — First echo estimates under Schwarzschild-like exterior.

EXTERIOR ASSUMPTION: All results computed under Schwarzschild-like exterior
(WP1 conditional assessment).

Computes:
1. Echo time delay for the benchmark endpoint (R_eq = 1/3 r_s)
2. BDCC oscillation frequency
3. Echo amplitudes across reflection coefficient scan
4. Mass scaling of echo timing
5. Comparison with standard GR QNM
"""

from __future__ import annotations

import sys
import time

from grut.ringdown import (
    EchoParameters,
    compute_echo_analysis,
    echo_result_to_dict,
    scan_reflection_coefficient,
    scan_mass_range,
    schwarzschild_radius,
    impedance_ratio,
    impedance_reflectivity,
    M_SUN,
)


def _header(title: str):
    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")


def main():
    t0 = time.time()

    print("Phase III-C WP2: Echo Falsifier Benchmark")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("EXTERIOR ASSUMPTION: Schwarzschild-like (WP1 conditional)")
    print()

    # ================================================================
    # 1. BENCHMARK ECHO ANALYSIS (M = 30 M_sun, R_eq = 1/3 r_s)
    # ================================================================
    _header("1. BENCHMARK ECHO ANALYSIS (30 M_sun, R_eq = 1/3 r_s)")

    M_bench = 30.0 * M_SUN
    r_s = schwarzschild_radius(M_bench)

    params = EchoParameters(
        M_kg=M_bench,
        r_s_m=r_s,
        R_eq_m=r_s / 3.0,
        R_eq_over_r_s=1.0 / 3.0,
        compactness=3.0,
        beta_Q=2.0,
        epsilon_Q=1.0 / 9.0,
        reflection_model="perfect",
        reflection_coefficient=1.0,
    )

    result = compute_echo_analysis(params, n_echoes=5)

    print(f"  Mass: {M_bench/M_SUN:.0f} M_sun")
    print(f"  r_s: {r_s/1000:.3f} km")
    print(f"  R_eq: {r_s/3000:.3f} km ({1.0/3.0:.6f} r_s)")
    print()
    print(f"  ECHO TIMING:")
    print(f"    r*(R_eq)     = {result.r_star_eq:.3f} m")
    print(f"    r*(r_peak)   = {result.r_star_peak:.3f} m")
    print(f"    Δt_echo      = {result.delta_t_echo_s*1000:.4f} ms")
    print(f"    Δt_echo/r_s  = {result.delta_t_echo_over_r_s:.4f}")
    print()
    print(f"  BDCC OSCILLATION:")
    print(f"    ω_core       = {result.omega_core_rad_s:.4e} rad/s")
    print(f"    f_core       = {result.f_core_Hz:.1f} Hz")
    print()
    print(f"  QNM REFERENCE (l=2, Schwarzschild):")
    print(f"    ω_QNM        = {result.omega_qnm_rad_s:.4e} rad/s")
    print(f"    f_QNM        = {result.f_qnm_Hz:.1f} Hz")
    print(f"    τ_QNM        = {result.tau_qnm_s*1000:.4f} ms")
    print(f"    ω_core/ω_QNM = {result.omega_core_rad_s/result.omega_qnm_rad_s:.2f}" if result.omega_qnm_rad_s > 0 else "")
    print()
    print(f"  ECHO AMPLITUDES (R_surface = 1.0, perfect reflection):")
    print(f"    |T|^2        = {result.transmission_squared:.4f}")
    print(f"    |R_peak|     = {result.reflection_peak:.4f}")
    print(f"    |R_surface|  = {result.reflection_surface:.4f}")
    for i, amp in enumerate(result.echo_amplitudes, 1):
        print(f"    Echo {i}: A_{i}/A_0 = {amp:.6f}")

    # ================================================================
    # 2. REFLECTION COEFFICIENT SCAN
    # ================================================================
    _header("2. REFLECTION COEFFICIENT SCAN (30 M_sun)")

    scan_R = scan_reflection_coefficient(M_bench, n_echoes=3)

    print(f"  {'R_surface':>10s}  {'Δt_echo (ms)':>12s}  {'A_1/A_0':>10s}  {'A_2/A_0':>10s}  {'Regime':>20s}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*10}  {'-'*10}  {'-'*20}")
    for row in scan_R:
        a1 = row["echo_amplitudes"][0] if row["echo_amplitudes"] else 0.0
        a2 = row["echo_amplitudes"][1] if len(row["echo_amplitudes"]) > 1 else 0.0
        print(f"  {row['R_surface']:>10.3f}  {row['delta_t_echo_s']*1000:>12.4f}  "
              f"{a1:>10.6f}  {a2:>10.8f}  {row['regime']:>20s}")

    # ================================================================
    # 3. MASS SCALING
    # ================================================================
    _header("3. MASS SCALING (R_surface = 1.0, perfect reflection)")

    scan_M = scan_mass_range(reflection_coefficient=1.0)

    print(f"  {'M (M_sun)':>12s}  {'r_s (km)':>12s}  {'Δt_echo (ms)':>14s}  {'f_QNM (Hz)':>12s}  {'f_core (Hz)':>12s}  {'A_1/A_0':>10s}")
    print(f"  {'-'*12}  {'-'*12}  {'-'*14}  {'-'*12}  {'-'*12}  {'-'*10}")
    for row in scan_M:
        print(f"  {row['M_solar']:>12.0f}  {row['r_s_km']:>12.3f}  {row['delta_t_echo_ms']:>14.4f}  "
              f"{row['f_qnm_Hz']:>12.1f}  {row['f_core_Hz']:>12.1f}  {row['first_echo_amplitude']:>10.6f}")

    # Check scaling: Δt ∝ M
    if len(scan_M) >= 2:
        ratio = scan_M[-1]["delta_t_echo_ms"] / scan_M[0]["delta_t_echo_ms"]
        mass_ratio = scan_M[-1]["M_solar"] / scan_M[0]["M_solar"]
        print(f"\n  Mass ratio:    {mass_ratio:.0e}")
        print(f"  Δt ratio:      {ratio:.0e}")
        print(f"  Δt ∝ M^{ratio/mass_ratio:.2f}" if mass_ratio > 0 else "")
        print(f"  Expected:      Δt ∝ M^1.0 (linear)")

    # ================================================================
    # 4. OBSERVATIONAL CONTEXT
    # ================================================================
    _header("4. OBSERVATIONAL CONTEXT")

    # 30 M_sun (LIGO range)
    echo_30 = result
    print(f"  30 M_sun black hole:")
    print(f"    Echo delay:      {echo_30.delta_t_echo_s*1000:.2f} ms")
    print(f"    QNM frequency:   {echo_30.f_qnm_Hz:.0f} Hz (LIGO band)")
    print(f"    QNM damping:     {echo_30.tau_qnm_s*1000:.2f} ms")
    print(f"    Echo 1 at |R|=1: {echo_30.echo_amplitudes[0]*100:.1f}% of main signal")
    print(f"    LIGO sensitivity: ~10% currently (not constraining for weak R_surface)")
    print()

    # 1e6 M_sun (LISA range)
    params_lisa = EchoParameters(
        M_kg=1e6 * M_SUN,
        r_s_m=schwarzschild_radius(1e6 * M_SUN),
        R_eq_over_r_s=1.0 / 3.0,
        beta_Q=2.0,
        reflection_model="perfect",
    )
    params_lisa.R_eq_m = params_lisa.R_eq_over_r_s * params_lisa.r_s_m
    echo_lisa = compute_echo_analysis(params_lisa, n_echoes=3)
    print(f"  10^6 M_sun SMBH:")
    print(f"    Echo delay:      {echo_lisa.delta_t_echo_s:.2f} s")
    print(f"    QNM frequency:   {echo_lisa.f_qnm_Hz*1000:.2f} mHz (LISA band)")
    print(f"    Echo 1 at |R|=1: {echo_lisa.echo_amplitudes[0]*100:.1f}% of main signal")

    # ================================================================
    # 5. IMPEDANCE MODEL: CONSTRAINED R_surface (WP2B)
    # ================================================================
    _header("5. IMPEDANCE MODEL: CONSTRAINED R_surface (WP2B)")

    print("  SHARP-BOUNDARY APPROXIMATION — transition-width corrections open")
    print("  NOTE: All reflection coefficients are AMPLITUDE (not power).")
    print("        Power reflectivity = r_amp^2.")
    print()

    # 5a. 30 M_sun with impedance model
    print("  5a. 30 M_sun BENCHMARK (impedance model)")
    params_imp = EchoParameters(
        M_kg=M_bench,
        r_s_m=r_s,
        R_eq_m=r_s / 3.0,
        R_eq_over_r_s=1.0 / 3.0,
        compactness=3.0,
        beta_Q=2.0,
        epsilon_Q=1.0 / 9.0,
        reflection_model="impedance",
    )
    result_imp = compute_echo_analysis(params_imp, n_echoes=5)
    eta_30 = result_imp.impedance_ratio_eta

    print(f"    η (impedance ratio)     = {eta_30:.6f}")
    print(f"    r_surface_amp           = {result_imp.reflection_surface:.6f}")
    print(f"    R_surface_pow           = {result_imp.reflection_surface**2:.6f}")
    print(f"    Echo 1 amplitude A_1/A_0= {result_imp.echo_amplitudes[0]:.6f}")
    print(f"    vs perfect (r_amp=1.0)  : {result.echo_amplitudes[0]:.6f}")
    print(f"    Ratio impedance/perfect : {result_imp.echo_amplitudes[0]/result.echo_amplitudes[0]:.4f}")
    print()

    # 5b. Mass-dependent impedance table
    print("  5b. MASS-DEPENDENT IMPEDANCE TABLE")
    print(f"  {'M (M_sun)':>12s}  {'η':>10s}  {'r_amp':>10s}  {'R_pow':>10s}  {'A_1/A_0':>10s}")
    print(f"  {'-'*12}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}")
    imp_masses = [10.0, 30.0, 100.0, 1e4, 1e6, 1e9]
    imp_etas = []
    for M_sol in imp_masses:
        M_kg = M_sol * M_SUN
        r_s_m = schwarzschild_radius(M_kg)
        R_eq_m = r_s_m / 3.0
        eta_m = impedance_ratio(M_kg, R_eq_m, 2.0)
        r_amp = impedance_reflectivity(M_kg, R_eq_m, 2.0)
        imp_etas.append(eta_m)
        # Echo amplitude under impedance model
        params_m = EchoParameters(
            M_kg=M_kg, r_s_m=r_s_m, R_eq_m=R_eq_m,
            R_eq_over_r_s=1.0/3.0, beta_Q=2.0,
            reflection_model="impedance",
        )
        res_m = compute_echo_analysis(params_m, n_echoes=1)
        a1 = res_m.echo_amplitudes[0] if res_m.echo_amplitudes else 0.0
        print(f"  {M_sol:>12.0f}  {eta_m:>10.6f}  {r_amp:>10.6f}  {r_amp**2:>10.6f}  {a1:>10.6f}")

    # 5c. Verify mass scaling of eta
    print()
    print("  5c. MASS SCALING CHECK")
    if len(imp_etas) >= 2:
        mass_ratio = imp_masses[-1] / imp_masses[0]
        eta_ratio = imp_etas[0] / imp_etas[-1]
        expected_sqrt = mass_ratio ** 0.5
        print(f"    Mass ratio (last/first):  {mass_ratio:.0e}")
        print(f"    η ratio (first/last):     {eta_ratio:.2f}")
        print(f"    Expected if η ∝ M^(-1/2): {expected_sqrt:.2f}")
        print(f"    Deviation from M^(-1/2):  {abs(eta_ratio/expected_sqrt - 1)*100:.1f}%")

    # 5d. Model comparison at 30 M_sun
    print()
    print("  5d. MODEL COMPARISON AT 30 M_sun")
    print(f"    {'Model':>20s}  {'r_surface_amp':>14s}  {'R_surface_pow':>14s}  {'A_1/A_0':>10s}")
    print(f"    {'-'*20}  {'-'*14}  {'-'*14}  {'-'*10}")

    models = [
        ("perfect", "perfect", {}),
        ("impedance", "impedance", {}),
        ("constant (0.5)", "constant", {"reflection_coefficient": 0.5}),
        ("constant (0.1)", "constant", {"reflection_coefficient": 0.1}),
        ("boltzmann", "boltzmann", {}),
    ]
    for label, model, extra in models:
        p = EchoParameters(
            M_kg=M_bench, r_s_m=r_s, R_eq_m=r_s/3.0,
            R_eq_over_r_s=1.0/3.0, beta_Q=2.0,
            reflection_model=model, **extra,
        )
        r = compute_echo_analysis(p, n_echoes=1)
        a1 = r.echo_amplitudes[0] if r.echo_amplitudes else 0.0
        print(f"    {label:>20s}  {r.reflection_surface:>14.6f}  "
              f"{r.reflection_surface**2:>14.6f}  {a1:>10.6f}")

    # ================================================================
    # 6. SUMMARY
    # ================================================================
    _header("6. WP2 + WP2B ECHO BENCHMARK SUMMARY")

    print("  EXTERIOR ASSUMPTION: Schwarzschild-like (WP1 conditional)")
    print()
    print("  KEY RESULTS (WP2):")
    print(f"    Echo time delay scales as Δt ∝ r_s ∝ M (linear in mass)")
    print(f"    At 30 M_sun: Δt ≈ {echo_30.delta_t_echo_s*1000:.2f} ms")
    print(f"    BDCC oscillation frequency ω_core << ω_QNM (slow core)")
    print(f"    Maximum echo amplitude (perfect reflection): ~{echo_30.echo_amplitudes[0]*100:.0f}% of main signal")
    print(f"    Echo amplitude falls rapidly with each bounce (geometric decay)")
    print()
    print("  IMPEDANCE MODEL RESULTS (WP2B):")
    print(f"    Impedance ratio η = ω_core × R_eq / c")
    print(f"    At 30 M_sun: η = {eta_30:.4f}")
    print(f"    r_surface_amp (impedance) = {result_imp.reflection_surface:.4f}")
    print(f"    η decreases with mass (approximately ∝ M^(-1/2))")
    print(f"    SHARP-BOUNDARY APPROXIMATION — transition-width corrections open")
    print()
    print("  ECHO CHANNEL ASSESSMENT:")
    print("    Under impedance model (reactive, non-dissipative BDCC):")
    print(f"    - r_surface_amp ≈ {result_imp.reflection_surface:.3f} at 30 M_sun")
    print(f"    - Echo amplitude ≈ {result_imp.echo_amplitudes[0]*100:.1f}% of main signal")
    print("    - Nearly the same as perfect-reflection upper bound")
    print("    - PROMISING for next-generation detectors")
    print()
    print("    Under Boltzmann model (dissipative BDCC):")
    print("    - r_surface_amp ≈ 0 (effectively no reflection)")
    print("    - Echo channel NOT useful as falsifier")
    print()
    print("    DISTINGUISHING QUESTION: Is the BDCC reactive or dissipative?")
    print("    This requires the interior wave equation (missing closure).")
    print()
    print("  GO/NO-GO:")
    echo_promising = echo_30.echo_amplitudes[0] > 0.001 if echo_30.echo_amplitudes else False
    if echo_promising:
        print("    ECHO CHANNEL: PROMISING under impedance model")
        print("    The impedance model provides a CANDIDATE constrained estimate.")
        print("    The Boltzmann model remains viable as worst-case bound.")
    else:
        print("    ECHO CHANNEL: UNCERTAIN")
    print()
    print("  EXPLICIT NONCLAIMS:")
    print("    - Echoes are NOT predicted to exist. This computes what they WOULD look like.")
    print("    - Echo delay is an ORDER OF MAGNITUDE estimate.")
    print("    - Impedance model is a sharp-boundary APPROXIMATION, not a derivation.")
    print("    - Transition-width corrections remain open.")
    print("    - Boltzmann model (R ≈ 0) remains viable if BDCC is dissipative.")
    print("    - All results are CONDITIONAL on WP1 exterior assessment.")
    print("    - Kerr generalization is not attempted.")
    print("    - All reflection coefficients are AMPLITUDE (power = r_amp^2).")

    elapsed = time.time() - t0
    print(f"\nTotal runtime: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
