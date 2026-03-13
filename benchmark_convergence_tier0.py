#!/usr/bin/env python3
"""Tier 0 convergence & endpoint benchmark.

Key question: Do the plunging cases (R0 > 3 r_s) converge to an arrested
endpoint given enough steps, or are they genuinely singular?

Tests:
1. Step-budget convergence: Run M=1e30, R0=5,10,30,100 r_s with
   increasing n_steps (500K, 1M, 2M, 5M) — does R_f/r_s converge?
2. Endpoint table: Compact (mass × R0 × final_class × R_f/r_s × converged?)
3. Post-horizon arrest criterion: Check whether arrested cases are
   genuinely inside the horizon at the end.
"""

import math
import sys
import numpy as np
from grut.collapse import (
    compute_collapse,
    compute_schwarzschild_radius,
    compute_freefall_time,
    SEC_PER_YEAR,
)


TAU0_CANON = 41.92e6 * SEC_PER_YEAR   # 41.92 Myr in seconds
ALPHA = 1.0 / 3.0
H_CAP = 1e6 / SEC_PER_YEAR


def convergence_vs_steps():
    """Does R_f/r_s converge as we increase n_steps?"""
    print("=" * 100)
    print("CONVERGENCE TEST 1: R_f/r_s vs n_steps  (M=1e30, canon tau, tier0)")
    print("    Does collapse endpoint converge, or does the shell keep falling?")
    print("=" * 100)

    M = 1e30
    r_s = compute_schwarzschild_radius(M)
    R0_factors = [3, 5, 10, 30]
    step_budgets = [500_000, 1_000_000, 2_000_000]

    header = f"  {'R0/rs':>6s}  {'n_steps':>10s}  {'class':>22s}  {'frac':>8s}  {'R_f/rs':>10s}  {'rsat/rs':>10s}  {'term':>16s}  {'budget':>6s}  {'t/tff':>10s}  {'teff/tdyn':>10s}"
    print(header)
    print("  " + "-" * (len(header.strip())))

    for factor in R0_factors:
        R0 = factor * r_s
        for ns in step_budgets:
            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=TAU0_CANON,
                alpha_vac=ALPHA, gamma_diss=1e-15,
                H_cap=H_CAP, n_steps=ns,
                local_tau_mode="tier0",
            )

            R_final = float(result.R_m[-1]) if len(result.R_m) > 0 else R0
            rsat_rs = result.r_sat_over_r_s if result.r_sat_over_r_s is not None else "—"

            print(
                f"  {factor:>6d}  {ns:>10d}  {result.collapse_class:>22s}  "
                f"{result.collapse_fraction:>8.4f}  "
                f"{R_final / r_s if r_s > 0 else 0:>10.4f}  "
                f"{rsat_rs if isinstance(rsat_rs, str) else f'{rsat_rs:>10.4f}':>10s}  "
                f"{result.termination_reason:>16s}  "
                f"{result.step_budget_fraction:>6.2f}  "
                f"{result.t_total_over_t_ff:>10.4f}  "
                f"{result.tau_eff_over_t_dyn_final:>10.4f}"
            )
        print()  # blank line between R0 groups

    print()


def convergence_supermassive():
    """Same test for M=1e35 and M=1e40 — do these converge?"""
    print("=" * 100)
    print("CONVERGENCE TEST 2: Supermassive convergence  (M=1e35, 1e40, canon tau, tier0)")
    print("=" * 100)

    masses = [1e35, 1e40]

    header = f"  {'M':>10s}  {'R0/rs':>6s}  {'n_steps':>10s}  {'class':>22s}  {'frac':>8s}  {'R_f/rs':>10s}  {'term':>16s}  {'budget':>6s}  {'t/tff':>10s}"
    print(header)
    print("  " + "-" * (len(header.strip())))

    for M in masses:
        r_s = compute_schwarzschild_radius(M)
        for factor in [3, 10]:
            R0 = factor * r_s
            for ns in [500_000, 2_000_000]:
                result = compute_collapse(
                    M_kg=M, R0_m=R0, tau0_s=TAU0_CANON,
                    alpha_vac=ALPHA, gamma_diss=1e-15,
                    H_cap=H_CAP, n_steps=ns,
                    local_tau_mode="tier0",
                )

                R_final = float(result.R_m[-1]) if len(result.R_m) > 0 else R0

                print(
                    f"  {M:>10.0e}  {factor:>6d}  {ns:>10d}  {result.collapse_class:>22s}  "
                    f"{result.collapse_fraction:>8.6f}  "
                    f"{R_final / r_s if r_s > 0 else 0:>10.6f}  "
                    f"{result.termination_reason:>16s}  "
                    f"{result.step_budget_fraction:>6.2f}  "
                    f"{result.t_total_over_t_ff:>10.4f}"
                )
        print()

    print()


def endpoint_table():
    """First Tier 0 endpoint table: mass × R0 × outcome."""
    print("=" * 100)
    print("ENDPOINT TABLE: Tier 0 results  (canon tau, alpha=1/3, gamma=1e-15)")
    print("    n_steps = 2M for adequate budget")
    print("=" * 100)

    masses = [1e25, 1e28, 1e30, 1e32, 1e35, 1e38, 1e40]
    R0_factors = [3, 5, 10, 30]
    n_steps = 2_000_000

    header = (f"  {'M_kg':>10s}  {'R0/rs':>6s}  {'class':>22s}  {'frac':>8s}  "
              f"{'R_f/rs':>10s}  {'C_max':>8s}  {'term':>16s}  "
              f"{'tier':>14s}  {'budget':>6s}  {'t/tff':>10s}  {'conv?':>5s}")
    print(header)
    print("  " + "-" * (len(header.strip())))

    for M in masses:
        r_s = compute_schwarzschild_radius(M)
        for factor in R0_factors:
            R0 = factor * r_s
            if R0 < 1e-20:
                R0 = max(R0, 1.0)

            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=TAU0_CANON,
                alpha_vac=ALPHA, gamma_diss=1e-15,
                H_cap=H_CAP, n_steps=n_steps,
                local_tau_mode="tier0",
            )

            R_final = float(result.R_m[-1]) if len(result.R_m) > 0 else R0
            converged = result.termination_reason in ("saturation", "singularity", "radius_converged")

            print(
                f"  {M:>10.0e}  {factor:>6d}  {result.collapse_class:>22s}  "
                f"{result.collapse_fraction:>8.4f}  "
                f"{R_final / r_s if r_s > 0 else 0:>10.4f}  "
                f"{result.max_compactness:>8.4f}  "
                f"{result.termination_reason:>16s}  "
                f"{result.bounce_exclusion_tier:>14s}  "
                f"{result.step_budget_fraction:>6.2f}  "
                f"{result.t_total_over_t_ff:>10.4f}  "
                f"{'YES' if converged else 'no':>5s}"
            )
        print()  # blank between mass groups

    print()


def posthorizon_detail():
    """Detailed look at the best post-horizon arrest candidate."""
    print("=" * 100)
    print("POST-HORIZON DETAIL: M=1e30, R0=3rs, tier0, n_steps=5M")
    print("    Is the arrest real? What does the trajectory look like near the end?")
    print("=" * 100)

    M = 1e30
    r_s = compute_schwarzschild_radius(M)
    R0 = 3.0 * r_s

    result = compute_collapse(
        M_kg=M, R0_m=R0, tau0_s=TAU0_CANON,
        alpha_vac=ALPHA, gamma_diss=1e-15,
        H_cap=H_CAP, n_steps=5_000_000,
        record_every=1,  # record every step for endpoint analysis
        local_tau_mode="tier0",
    )

    R_final = float(result.R_m[-1])
    V_final = float(result.V_ms[-1])

    print(f"\n  Termination: {result.termination_reason}")
    print(f"  Class:       {result.collapse_class}")
    print(f"  Steps taken: {result.n_steps_taken:,d}")
    print(f"  Budget:      {result.step_budget_fraction:.4f}")
    print(f"  R_f/r_s:     {R_final/r_s:.6f}")
    print(f"  V_f:         {V_final:.6e} m/s")
    print(f"  C_max:       {result.max_compactness:.6f}")
    print(f"  Bounce tier: {result.bounce_exclusion_tier}")
    print(f"  t_total/t_ff:{result.t_total_over_t_ff:.4f}")
    print(f"  tau_eff/t_dyn:{result.tau_eff_over_t_dyn_final:.6f}")

    # Last 20 trajectory points
    n_show = min(20, len(result.R_m))
    print(f"\n  Last {n_show} trajectory points:")
    print(f"  {'t(s)':>14s}  {'R/r_s':>12s}  {'V(m/s)':>14s}  {'C':>10s}  {'a_eff':>12s}  {'M_drive':>12s}")
    print("  " + "-" * 80)
    for i in range(-n_show, 0):
        t = float(result.t_s[i])
        R = float(result.R_m[i])
        V = float(result.V_ms[i])
        C = float(result.compactness[i])
        ae = float(result.a_eff[i])
        md = float(result.M_drive[i])
        print(
            f"  {t:>14.6e}  {R/r_s:>12.6f}  {V:>14.6e}  "
            f"{C:>10.4f}  {ae:>12.4e}  {md:>12.4e}"
        )

    # AH crossings
    if result.ah_crossings:
        print(f"\n  Apparent Horizon crossings: {len(result.ah_crossings)}")
        for t, R, direction in result.ah_crossings[:5]:
            print(f"    t={t:.4e} s, R/r_s={R/r_s:.4f}, {direction}")
    else:
        print("\n  No Apparent Horizon crossings recorded.")

    print()


if __name__ == "__main__":
    # Run the fast convergence test first
    convergence_vs_steps()

    # Then the supermassive convergence
    convergence_supermassive()

    # Endpoint table
    endpoint_table()

    # Detailed post-horizon analysis
    posthorizon_detail()

    print("\n✓ Tier 0 convergence & endpoint benchmarks complete.")
