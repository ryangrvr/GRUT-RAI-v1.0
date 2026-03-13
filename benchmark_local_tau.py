#!/usr/bin/env python3
"""Local-tau Tier 0 closure benchmark.

Tests F(t_dyn) = t_dyn / (t_dyn + tau0) closure against the bare-tau baseline.
Key question: does Tier 0 produce a physical r_sat that doesn't echo R0?

Probes:
1. R0-dependence: R0 = 3, 5, 10, 30, 100 r_s — does r_sat decouple from R0?
2. Mass ladder:  M = 1, 1e10, 1e20, 1e30, 1e35, 1e40 at canon tau
3. Phase diagram slice: Mass × class at canon params with tier0
4. tau/t_dyn diagnostic: verify the ratio is brought to ~1
"""

import math
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


def probe_R0_with_local_tau():
    """Does r_sat decouple from R0 under Tier 0?"""
    print("=" * 90)
    print("PROBE 1: R0-dependence under Tier 0 (local_tau_mode='tier0')")
    print("         Key question: does r_sat/r_s converge across R0?")
    print("=" * 90)

    test_cases = [
        {"label": "Stellar M=1e30 kg, canon tau", "M_kg": 1e30,
         "tau0_s": TAU0_CANON, "gamma_diss": 1e-15, "H_cap": H_CAP, "n_steps": 500_000},
        {"label": "Stellar M=1e30 kg, canon tau, stronger diss", "M_kg": 1e30,
         "tau0_s": TAU0_CANON, "gamma_diss": 1e-5, "H_cap": H_CAP, "n_steps": 500_000},
        {"label": "Supermassive M=1e40 kg, canon tau", "M_kg": 1e40,
         "tau0_s": TAU0_CANON, "gamma_diss": 1e-15, "H_cap": H_CAP, "n_steps": 500_000},
    ]

    R0_factors = [3, 5, 10, 30, 100]

    for case in test_cases:
        M = case["M_kg"]
        r_s = compute_schwarzschild_radius(M)
        t_ff_10rs = compute_freefall_time(10 * r_s, M)

        print(f"\n{'─' * 90}")
        print(f"  {case['label']}")
        print(f"  r_s = {r_s:.4e} m,  t_ff(10rs) = {t_ff_10rs:.4e} s")
        print(f"  tau0 = {case['tau0_s']:.4e} s,  tau0/t_ff = {case['tau0_s']/t_ff_10rs:.4e}")
        print(f"{'─' * 90}")

        header = (f"  {'R0/rs':>6s}  {'class':>14s}  {'frac':>8s}  "
                  f"{'R_f/rs':>10s}  {'rsat/rs':>10s}  "
                  f"{'t0/tdyn':>10s}  {'teff/tdyn':>10s}  "
                  f"{'tier':>10s}  {'budget':>6s}  {'t/tff':>8s}")
        print(header)
        print("  " + "-" * (len(header.strip())))

        for factor in R0_factors:
            R0 = factor * r_s

            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=case["tau0_s"],
                alpha_vac=ALPHA, gamma_diss=case["gamma_diss"],
                H_cap=case["H_cap"], n_steps=case["n_steps"],
                local_tau_mode="tier0",
            )

            R_final = float(result.R_m[-1]) if len(result.R_m) > 0 else R0
            rsat_rs = result.r_sat_over_r_s if result.r_sat_over_r_s is not None else "—"
            budg = f"{result.step_budget_fraction:.2f}"

            print(
                f"  {factor:>6d}  {result.collapse_class:>14s}  "
                f"{result.collapse_fraction:>8.4f}  "
                f"{R_final / r_s if r_s > 0 else 0:>10.4f}  "
                f"{rsat_rs if isinstance(rsat_rs, str) else f'{rsat_rs:>10.4f}':>10s}  "
                f"{result.tau0_over_t_dyn:>10.4e}  "
                f"{result.tau_eff_over_t_dyn_final:>10.4e}  "
                f"{result.bounce_exclusion_tier[:10]:>10s}  "
                f"{budg:>6s}  "
                f"{result.t_total_over_t_ff:>8.4f}"
            )

    print()


def mass_ladder_tier0():
    """Mass ladder from 1 kg to 10^40 kg with Tier 0 and canon tau."""
    print("=" * 90)
    print("PROBE 2: Mass ladder with Tier 0 closure (canon tau, R0=10rs)")
    print("=" * 90)

    masses = [1e0, 1e5, 1e10, 1e15, 1e20, 1e25, 1e30, 1e35, 1e40]

    header = (f"  {'M_kg':>10s}  {'class':>14s}  {'frac':>8s}  "
              f"{'R_f/rs':>10s}  {'rsat/rs':>10s}  "
              f"{'t0/tdyn':>10s}  {'teff/tdyn':>10s}  "
              f"{'tier':>10s}  {'budget':>6s}")
    print(header)
    print("  " + "-" * (len(header.strip())))

    for M in masses:
        r_s = compute_schwarzschild_radius(M)
        R0 = 10.0 * r_s
        if R0 < 1e-20:
            R0 = max(R0, 1.0)  # floor for sub-Planck masses

        result = compute_collapse(
            M_kg=M, R0_m=R0, tau0_s=TAU0_CANON,
            alpha_vac=ALPHA, gamma_diss=1e-15,
            H_cap=H_CAP, n_steps=200_000,
            local_tau_mode="tier0",
        )

        R_final = float(result.R_m[-1]) if len(result.R_m) > 0 else R0
        rsat_rs = result.r_sat_over_r_s if result.r_sat_over_r_s is not None else "—"
        budg = f"{result.step_budget_fraction:.2f}"

        print(
            f"  {M:>10.0e}  {result.collapse_class:>14s}  "
            f"{result.collapse_fraction:>8.4f}  "
            f"{R_final / r_s if r_s > 0 else 0:>10.4f}  "
            f"{rsat_rs if isinstance(rsat_rs, str) else f'{rsat_rs:>10.4f}':>10s}  "
            f"{result.tau0_over_t_dyn:>10.4e}  "
            f"{result.tau_eff_over_t_dyn_final:>10.4e}  "
            f"{result.bounce_exclusion_tier[:10]:>10s}  "
            f"{budg:>6s}"
        )

    print()


def compare_off_vs_tier0():
    """Side-by-side comparison: off vs tier0 for stellar mass at canon tau."""
    print("=" * 90)
    print("PROBE 3: Side-by-side off vs tier0 — M=1e30, canon tau, R0=10rs")
    print("=" * 90)

    M = 1e30
    r_s = compute_schwarzschild_radius(M)
    R0 = 10.0 * r_s

    for gamma in [0.0, 1e-15, 1e-10, 1e-5, 1.0]:
        print(f"\n  gamma_diss = {gamma:.0e}")
        for mode in ["off", "tier0"]:
            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=TAU0_CANON,
                alpha_vac=ALPHA, gamma_diss=gamma,
                H_cap=H_CAP, n_steps=200_000,
                local_tau_mode=mode,
            )
            R_final = float(result.R_m[-1]) if len(result.R_m) > 0 else R0
            rsat_rs = result.r_sat_over_r_s if result.r_sat_over_r_s is not None else "—"
            print(
                f"    {mode:>6s}: {result.collapse_class:>14s}  "
                f"frac={result.collapse_fraction:>8.4f}  "
                f"R_f/rs={R_final/r_s:>10.4f}  "
                f"rsat/rs={rsat_rs if isinstance(rsat_rs, str) else f'{rsat_rs:.4f}':>10s}  "
                f"t0/tdyn={result.tau0_over_t_dyn:.4e}  "
                f"tier={result.bounce_exclusion_tier}  "
                f"budget={result.step_budget_fraction:.2f}"
            )

    print()


def phase_diagram_tier0():
    """Phase diagram slice: Mass × gamma with tier0 closure."""
    print("=" * 90)
    print("PROBE 4: Phase diagram with Tier 0 — Mass × gamma (canon tau, alpha=1/3)")
    print("=" * 90)

    masses = [1e0, 1e10, 1e20, 1e25, 1e30, 1e35, 1e40]
    gammas = [0.0, 1e-15, 1e-10, 1e-5, 1.0, 1e3]

    header = f"  {'Mass':>10s} | " + " | ".join(f"γ={g:.0e}" for g in gammas)
    print(header)
    print("  " + "-" * (len(header.strip())))

    for M in masses:
        r_s = compute_schwarzschild_radius(M)
        R0 = 10.0 * r_s
        if R0 < 1e-20:
            R0 = max(R0, 1.0)

        cells = []
        for gamma in gammas:
            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=TAU0_CANON,
                alpha_vac=ALPHA, gamma_diss=gamma,
                H_cap=H_CAP, n_steps=200_000,
                local_tau_mode="tier0",
            )
            tag = result.collapse_class[:6]
            cells.append(f"{tag:>6s}")
        print(f"  {M:>10.0e} | " + " | ".join(cells))

    print()


if __name__ == "__main__":
    probe_R0_with_local_tau()
    mass_ladder_tier0()
    compare_off_vs_tier0()
    phase_diagram_tier0()
    print("\n✓ Local-tau Tier 0 benchmarks complete.")
