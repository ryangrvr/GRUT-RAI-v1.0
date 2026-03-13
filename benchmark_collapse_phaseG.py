#!/usr/bin/env python3
"""Phase-G collapse benchmarks: R0-dependence probe + collapse phase diagram.

Probe 1 — Initial-condition dependence:
  Does r_sat echo R0?  If r_sat/r_s ~ R0/r_s then the saturation
  radius is a starting-condition artefact, not a physical radius.

Probe 2 — Collapse phase diagram:
  Map (mass × alpha × gamma × tau × R0) parameter space to
  collapse_class outcomes.  Identify which regions give
  stall / arrested_prehorizon / arrested_posthorizon / plunging / singular.

Uses the Phase-G fields: collapse_class, collapse_fraction,
bounce_exclusion_tier, a_eff_min, M_drive_min.
"""

import sys
import math
import numpy as np
from grut.collapse import (
    compute_collapse,
    compute_schwarzschild_radius,
    compute_freefall_time,
    SEC_PER_YEAR,
)


def probe_R0_dependence():
    """Probe whether r_sat tracks R0 (artefact) or stabilises (physical)."""
    print("=" * 78)
    print("PROBE 1: Initial-condition dependence — R0 = 3, 5, 10, 30, 100 r_s")
    print("=" * 78)

    # Use two representative masses: weak-gravity and stellar
    test_cases = [
        {"label": "Weak gravity (M=1 kg)", "M_kg": 1.0,
         "tau0_s": 100.0, "gamma_diss": 1000.0, "H_cap": 1.0, "n_steps": 200_000},
        {"label": "Intermediate (M=1e15 kg)", "M_kg": 1e15,
         "tau0_s": 1e8, "gamma_diss": 1e-5, "H_cap": 1e3, "n_steps": 200_000},
        {"label": "Stellar (M=1e30 kg, canon tau)", "M_kg": 1e30,
         "tau0_s": 41.92e6 * SEC_PER_YEAR, "gamma_diss": 1e-15,
         "H_cap": 1e6 / SEC_PER_YEAR, "n_steps": 200_000},
        {"label": "Stellar (M=1e30 kg, local tau=100s)", "M_kg": 1e30,
         "tau0_s": 100.0, "gamma_diss": 1e-5, "H_cap": 1e3, "n_steps": 200_000},
    ]

    R0_factors = [3, 5, 10, 30, 100]

    for case in test_cases:
        M = case["M_kg"]
        r_s = compute_schwarzschild_radius(M)
        print(f"\n{'─' * 78}")
        print(f"  {case['label']}   r_s = {r_s:.4e} m")
        print(f"  tau0 = {case['tau0_s']:.4e} s, gamma = {case['gamma_diss']:.4e}, H_cap = {case['H_cap']:.4e}")
        print(f"{'─' * 78}")

        header = f"  {'R0/r_s':>8s}  {'class':>22s}  {'frac':>8s}  {'R_f/r_s':>10s}  {'r_sat/r_s':>10s}  {'tier':>14s}  {'a_eff_min':>12s}  {'Md_min':>12s}"
        print(header)
        print("  " + "-" * len(header.strip()))

        for factor in R0_factors:
            R0 = factor * r_s
            if R0 < 1e-30:
                R0 = max(factor * 1e-10, 1.0)  # floor for numerical safety

            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=case["tau0_s"],
                alpha_vac=1.0 / 3.0, gamma_diss=case["gamma_diss"],
                H_cap=case["H_cap"], n_steps=case["n_steps"],
            )

            R_final = float(result.R_m[-1]) if len(result.R_m) > 0 else R0
            r_sat_over_rs = result.r_sat_over_r_s if result.r_sat_over_r_s is not None else "—"

            print(
                f"  {factor:>8d}  {result.collapse_class:>22s}  "
                f"{result.collapse_fraction:>8.4f}  "
                f"{R_final / r_s if r_s > 0 else 0:>10.4f}  "
                f"{r_sat_over_rs if isinstance(r_sat_over_rs, str) else f'{r_sat_over_rs:>10.4f}':>10s}  "
                f"{result.bounce_exclusion_tier:>14s}  "
                f"{result.a_eff_min:>12.4e}  "
                f"{result.M_drive_min:>12.4e}"
            )

    print()


def build_phase_diagram():
    """Map collapse outcomes over parameter space."""
    print("=" * 78)
    print("PROBE 2: Collapse phase diagram")
    print("=" * 78)

    # Fixed baseline params
    R0_factor = 10.0
    n_steps = 100_000

    # ── Axis 1: Mass ladder ──
    masses = [1e0, 1e5, 1e10, 1e15, 1e20, 1e25, 1e30, 1e35, 1e40]

    # ── Axis 2: alpha_vac ──
    alphas = [0.0, 0.01, 0.1, 1.0/3.0, 0.5, 0.9]

    # ── Axis 3: gamma_diss ──
    gammas = [0.0, 1e-15, 1e-10, 1e-5, 1.0, 1e3]

    # ── Axis 4: tau0 ──
    taus = [1.0, 100.0, 1e6, 1e10, 41.92e6 * SEC_PER_YEAR]  # 1s to canon
    tau_labels = ["1s", "100s", "1e6s", "1e10s", "canon"]

    # Slice 1: Mass × alpha (gamma=1e-5, tau=100, H_cap=1e3)
    print("\n── Slice 1: Mass × alpha_vac  (gamma=1e-5, tau=100s, H_cap=1e3) ──")
    header = f"  {'Mass':>10s} | " + " | ".join(f"α={a:.3f}" for a in alphas)
    print(header)
    print("  " + "-" * len(header.strip()))

    for M in masses:
        r_s = compute_schwarzschild_radius(M)
        R0 = R0_factor * r_s
        if R0 < 1e-30:
            R0 = max(R0_factor * 1e-10, 1.0)

        cells = []
        for alpha in alphas:
            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=100.0,
                alpha_vac=alpha, gamma_diss=1e-5,
                H_cap=1e3, n_steps=n_steps,
            )
            tag = result.collapse_class[:6]
            frac = result.collapse_fraction
            cells.append(f"{tag:>6s}")
        print(f"  {M:>10.0e} | " + " | ".join(cells))

    # Slice 2: Mass × gamma (alpha=1/3, tau=100, H_cap=1e3)
    print("\n── Slice 2: Mass × gamma_diss  (alpha=1/3, tau=100s, H_cap=1e3) ──")
    header = f"  {'Mass':>10s} | " + " | ".join(f"γ={g:.0e}" for g in gammas)
    print(header)
    print("  " + "-" * len(header.strip()))

    for M in masses:
        r_s = compute_schwarzschild_radius(M)
        R0 = R0_factor * r_s
        if R0 < 1e-30:
            R0 = max(R0_factor * 1e-10, 1.0)

        cells = []
        for gamma in gammas:
            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=100.0,
                alpha_vac=1.0/3.0, gamma_diss=gamma,
                H_cap=1e3, n_steps=n_steps,
            )
            tag = result.collapse_class[:6]
            cells.append(f"{tag:>6s}")
        print(f"  {M:>10.0e} | " + " | ".join(cells))

    # Slice 3: Mass × tau (alpha=1/3, gamma=1e-5, H_cap=1e3)
    print("\n── Slice 3: Mass × tau0  (alpha=1/3, gamma=1e-5, H_cap=1e3) ──")
    header = f"  {'Mass':>10s} | " + " | ".join(f"τ={lbl:>6s}" for lbl in tau_labels)
    print(header)
    print("  " + "-" * len(header.strip()))

    for M in masses:
        r_s = compute_schwarzschild_radius(M)
        R0 = R0_factor * r_s
        if R0 < 1e-30:
            R0 = max(R0_factor * 1e-10, 1.0)

        cells = []
        for tau in taus:
            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=tau,
                alpha_vac=1.0/3.0, gamma_diss=1e-5,
                H_cap=1e3, n_steps=n_steps,
            )
            tag = result.collapse_class[:6]
            cells.append(f"{tag:>6s}")
        print(f"  {M:>10.0e} | " + " | ".join(cells))

    # Slice 4: Detailed view — Mass × R0/r_s (alpha=1/3, gamma=1e-5, tau=100, H_cap=1e3)
    print("\n── Slice 4: Mass × R0/r_s  (alpha=1/3, gamma=1e-5, tau=100s, H_cap=1e3) ──")
    R0_factors_diag = [3, 5, 10, 30, 100]
    header = f"  {'Mass':>10s} | " + " | ".join(f"R0={f}rs" for f in R0_factors_diag)
    print(header)
    print("  " + "-" * len(header.strip()))

    for M in masses:
        r_s = compute_schwarzschild_radius(M)
        cells = []
        for factor in R0_factors_diag:
            R0 = factor * r_s
            if R0 < 1e-30:
                R0 = max(factor * 1e-10, 1.0)

            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=100.0,
                alpha_vac=1.0/3.0, gamma_diss=1e-5,
                H_cap=1e3, n_steps=n_steps,
            )
            tag = result.collapse_class[:6]
            cells.append(f"{tag:>6s}")
        print(f"  {M:>10.0e} | " + " | ".join(cells))

    # Slice 5: Bounce-exclusion tier map (same axes as Slice 1)
    print("\n── Slice 5: Bounce-exclusion tier map  (mass × alpha, gamma=1e-5, tau=100s) ──")
    header = f"  {'Mass':>10s} | " + " | ".join(f"α={a:.3f}" for a in alphas)
    print(header)
    print("  " + "-" * len(header.strip()))

    for M in masses:
        r_s = compute_schwarzschild_radius(M)
        R0 = R0_factor * r_s
        if R0 < 1e-30:
            R0 = max(R0_factor * 1e-10, 1.0)

        cells = []
        for alpha in alphas:
            result = compute_collapse(
                M_kg=M, R0_m=R0, tau0_s=100.0,
                alpha_vac=alpha, gamma_diss=1e-5,
                H_cap=1e3, n_steps=n_steps,
            )
            tier = result.bounce_exclusion_tier[:5]  # sign_ / numer / viola
            cells.append(f"{tier:>6s}")
        print(f"  {M:>10.0e} | " + " | ".join(cells))

    print()


if __name__ == "__main__":
    probe_R0_dependence()
    build_phase_diagram()
    print("\n✓ Phase-G benchmarks complete.")
