#!/usr/bin/env python3
"""Phase III-B Audit — Constrained-Law Stress Test, Phi Mapping, Ledger Tracking.

Runs with the constrained endpoint law from Phase III-A:
  epsilon_Q = alpha_vac^2 = 1/9
  beta_Q = 2
  R_eq/r_s = alpha_vac = 1/3

TASK 1: Full anti-artifact acceptance audit (same criteria as Phase II)
TASK 2: Phi = a_outward/a_inward phase-transition mapping vs R/r_s
TASK 3: Information ledger tracking along trajectories
"""

from __future__ import annotations

import math
import sys
import time

import numpy as np

from grut.collapse import (
    G_SI,
    C_SI,
    SEC_PER_YEAR,
    compute_collapse,
    compute_schwarzschild_radius,
)
from grut.information import from_collapse_result, to_dict

# ── Constrained law parameters ──
ALPHA_VAC = 1.0 / 3.0
EPS_Q_CONSTRAINED = ALPHA_VAC ** 2          # = 1/9 ≈ 0.1111
BETA_Q_CONSTRAINED = 2
R_EQ_PREDICTED = ALPHA_VAC                  # = 1/3 ≈ 0.3333

TAU0_CANON = 1.3225e15       # s
GAMMA_DISS = 1e-15           # s^-1
H_CAP_BASE = 1e6 / SEC_PER_YEAR
M_REF = 1e30                 # kg
N_STEPS = 2_000_000


def _run(*, M_kg=M_REF, R0_factor=10.0, epsilon_Q=EPS_Q_CONSTRAINED,
         beta_Q=BETA_Q_CONSTRAINED, n_steps=N_STEPS, V_tol_frac=1e-8,
         H_cap=H_CAP_BASE, V0_mps=0.0, record_every=10, **kw):
    r_s = compute_schwarzschild_radius(M_kg)
    return compute_collapse(
        M_kg=M_kg, R0_m=R0_factor * r_s, tau0_s=TAU0_CANON,
        alpha_vac=ALPHA_VAC, gamma_diss=GAMMA_DISS, H_cap=H_cap,
        n_steps=n_steps, local_tau_mode="tier0",
        epsilon_Q=epsilon_Q, beta_Q=beta_Q, V_tol_frac=V_tol_frac,
        V0_mps=V0_mps, record_every=record_every, **kw,
    )


def _header(title: str):
    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")


# ================================================================
# TASK 1: CONSTRAINED-LAW STRESS TEST
# ================================================================
results = {}


def task1_vtol():
    _header("TASK 1a: V_tol Insensitivity (constrained law)")
    vtols = [1e-6, 1e-8, 1e-10, 1e-12]
    barrier_engaged = []

    print(f"  {'V_tol':>12s}  {'R_f/r_s':>10s}  {'FBR':>10s}  {'artifact':>10s}  {'barrier?':>10s}")
    for vt in vtols:
        r = _run(V_tol_frac=vt)
        R_f = float(r.R_m[-1]) / r.r_s_m
        engaged = r.artifact_R_f > 0 and abs(R_f - r.artifact_R_f) / max(R_f, 1e-30) > 0.10
        if engaged:
            barrier_engaged.append(R_f)
        print(f"  {vt:>12.0e}  {R_f:>10.6f}  {r.force_balance_residual:>10.6f}  "
              f"{r.artifact_R_f:>10.6f}  {'YES' if engaged else 'no':>10s}")

    if len(barrier_engaged) >= 2:
        spread = max(barrier_engaged) / min(barrier_engaged)
        passed = spread < 1.01
        print(f"  Barrier-engaged spread = {spread:.6f} ({len(barrier_engaged)}/{len(vtols)} runs)")
        results["vtol"] = (passed, f"spread={spread:.6f}")
    else:
        passed = False
        results["vtol"] = (False, f"only {len(barrier_engaged)} barrier-engaged")
    print(f"  => {'PASS' if passed else 'FAIL'}")
    return passed


def task1_r0():
    _header("TASK 1b: R0 Insensitivity (constrained law)")
    factors = [3, 5, 10, 30, 100]
    R_vals = []

    print(f"  {'R0/r_s':>10s}  {'R_f/r_s':>10s}  {'FBR':>10s}  {'Phi':>10s}")
    for f in factors:
        r = _run(R0_factor=f)
        R_f = float(r.R_m[-1]) / r.r_s_m
        R_vals.append(R_f)
        print(f"  {f:>10d}  {R_f:>10.6f}  {r.force_balance_residual:>10.6f}  "
              f"{r.barrier_dominance_final:>10.6f}")

    spread = max(R_vals) / min(R_vals) if min(R_vals) > 0 else float("inf")
    passed = spread < 1.01
    results["r0"] = (passed, f"spread={spread:.6f}")
    print(f"  Spread = {spread:.6f}")
    print(f"  => {'PASS' if passed else 'FAIL'}")
    return passed


def task1_force_balance():
    _header("TASK 1c: Force Balance & Operator Share (constrained law)")
    r = _run()
    R_f = float(r.R_m[-1]) / r.r_s_m
    share = r.a_outward_final / r.a_grav_final if r.a_grav_final > 0 else 0.0

    print(f"  R_f/r_s           = {R_f:.6f}")
    print(f"  R_eq predicted    = {R_EQ_PREDICTED:.6f}")
    print(f"  Match error       = {abs(R_f - R_EQ_PREDICTED)/R_EQ_PREDICTED*100:.2f}%")
    print(f"  FBR               = {r.force_balance_residual:.8f}")
    print(f"  a_outward/a_grav  = {share:.6f}")
    print(f"  Phi (barrier dom) = {r.barrier_dominance_final:.6f}")
    print(f"  mem track ratio   = {r.memory_tracking_ratio_final:.6f}")
    print(f"  endpoint motion   = {r.endpoint_motion_class}")
    print(f"  stability ind     = {r.asymptotic_stability_indicator:.4e}")

    fb_pass = r.force_balance_residual < 0.01
    share_pass = share > 0.5
    results["force_balance"] = (fb_pass, f"FBR={r.force_balance_residual:.6f}")
    results["operator_share"] = (share_pass, f"share={share:.4f}")
    print(f"  Force balance => {'PASS' if fb_pass else 'FAIL'}")
    print(f"  Operator share => {'PASS' if share_pass else 'FAIL'}")
    return fb_pass and share_pass


def task1_stability():
    _header("TASK 1d: Perturbation Stability (constrained law)")
    r_s = compute_schwarzschild_radius(M_REF)
    R_eq_m = R_EQ_PREDICTED * r_s

    # Start 10% outside R_eq, at rest
    r_out = _run(R0_factor=1.1 * R_EQ_PREDICTED, V0_mps=0.0)
    R_f_out = float(r_out.R_m[-1]) / r_s
    err_out = abs(R_f_out - R_EQ_PREDICTED) / R_EQ_PREDICTED

    # Start 10% inside R_eq, small inward kick
    V_ff = math.sqrt(2.0 * G_SI * M_REF / (0.9 * R_eq_m))
    r_in = _run(R0_factor=0.9 * R_EQ_PREDICTED, V0_mps=-0.01 * V_ff)
    R_f_in = float(r_in.R_m[-1]) / r_s
    err_in = abs(R_f_in - R_EQ_PREDICTED) / R_EQ_PREDICTED

    print(f"  Outside: R_f/r_s = {R_f_out:.6f}, error = {err_out:.4f}")
    print(f"  Inside:  R_f/r_s = {R_f_in:.6f}, error = {err_in:.4f}")
    print(f"  Outside stability = {r_out.asymptotic_stability_indicator:.4e}")
    print(f"  Inside stability  = {r_in.asymptotic_stability_indicator:.4e}")

    converge = err_out < 0.05 and err_in < 0.05
    stable = r_out.asymptotic_stability_indicator > 0 and r_in.asymptotic_stability_indicator > 0
    results["stability_converge"] = (converge, f"err_out={err_out:.4f}, err_in={err_in:.4f}")
    results["stability_positive"] = (stable, f"ind_out={r_out.asymptotic_stability_indicator:.2e}")
    print(f"  Convergence => {'PASS' if converge else 'FAIL'}")
    print(f"  Stability   => {'PASS' if stable else 'FAIL'}")
    return converge and stable


def task1_artifact():
    _header("TASK 1e: Artifact Rejection (constrained law)")
    r = _run()
    R_f = float(r.R_m[-1]) / r.r_s_m
    dev = abs(R_f - r.artifact_R_f) / R_f if R_f > 0 else 0.0

    print(f"  R_f/r_s     = {R_f:.6f}")
    print(f"  Artifact    = {r.artifact_R_f:.6f}")
    print(f"  Deviation   = {dev*100:.1f}%")

    passed = dev > 0.10
    results["artifact"] = (passed, f"dev={dev*100:.1f}%")
    print(f"  => {'PASS' if passed else 'FAIL'}")
    return passed


def task1_hcap():
    _header("TASK 1f: H_cap Independence (constrained law)")
    hcaps = [H_CAP_BASE, 10.0 * H_CAP_BASE, 100.0 * H_CAP_BASE]
    R_vals = []

    for hc in hcaps:
        r = _run(H_cap=hc)
        R_f = float(r.R_m[-1]) / r.r_s_m
        R_vals.append(R_f)
        print(f"  H_cap = {hc:.4e}  R_f/r_s = {R_f:.6f}")

    spread = max(R_vals) / min(R_vals) if min(R_vals) > 0 else float("inf")
    passed = spread < 1.01
    results["hcap"] = (passed, f"spread={spread:.6f}")
    print(f"  Spread = {spread:.6f}")
    print(f"  => {'PASS' if passed else 'FAIL'}")
    return passed


def task1_no_regression():
    _header("TASK 1g: No Regression (epsilon_Q=0 backward compat)")
    r = _run(epsilon_Q=0.0)
    print(f"  epsilon_Q=0: R_f/r_s = {float(r.R_m[-1])/r.r_s_m:.6f}")
    print(f"  termination = {r.termination_reason}")
    print(f"  barrier_dom = {r.barrier_dominance_final:.6f}")
    passed = r.barrier_dominance_final == 0.0
    results["no_regression"] = (passed, f"barrier_dom={r.barrier_dominance_final}")
    print(f"  => {'PASS' if passed else 'FAIL'}")
    return passed


def task1_no_bounce():
    _header("TASK 1h: No Bounce Violation (constrained law)")
    r = _run()
    ep = r.endpoint_motion_class
    passed = ep != "bounce_violation"
    results["no_bounce"] = (passed, f"motion={ep}")
    print(f"  Endpoint motion class = {ep}")
    print(f"  => {'PASS' if passed else 'FAIL'}")
    return passed


def task1_analytical_match():
    _header("TASK 1i: Analytical Prediction Match (constrained law)")
    r = _run()
    R_f = float(r.R_m[-1]) / r.r_s_m
    err = abs(R_f - R_EQ_PREDICTED) / R_EQ_PREDICTED

    print(f"  R_f/r_s        = {R_f:.6f}")
    print(f"  Predicted      = {R_EQ_PREDICTED:.6f} (alpha_vac = 1/3)")
    print(f"  Error          = {err*100:.2f}%")
    print(f"  Compactness    = {r.compactness_final:.4f}")

    passed = err < 0.01
    results["analytical"] = (passed, f"err={err*100:.2f}%")
    print(f"  => {'PASS' if passed else 'FAIL'}")
    return passed


# ================================================================
# TASK 2: PHI PHASE-TRANSITION MAPPING
# ================================================================
def task2_phi_mapping():
    _header("TASK 2: Phi = a_outward/a_inward vs R/r_s")
    r = _run(record_every=1, n_steps=N_STEPS)
    r_s = r.r_s_m

    R_arr = r.R_m
    a_Q_arr = r.a_Q
    a_eff_arr = r.a_eff  # this is a_net
    Md_arr = r.M_drive

    n = len(R_arr)
    R_rs = np.array([R_arr[i] / r_s for i in range(n)])

    # Compute Phi at each recorded step
    Phi_arr = np.zeros(n)
    C_arr = np.zeros(n)
    for i in range(n):
        R_i = float(R_arr[i])
        if R_i <= 0:
            continue
        a_grav_i = G_SI * M_REF / (R_i * R_i)
        a_inward_i = (1.0 - ALPHA_VAC) * a_grav_i + ALPHA_VAC * float(Md_arr[i])
        a_outward_i = float(a_Q_arr[i]) if a_Q_arr is not None else 0.0
        if a_inward_i > 0 and a_outward_i > 0:
            Phi_arr[i] = a_outward_i / a_inward_i
        C_arr[i] = r_s / R_i

    # Report Phi at key R/r_s checkpoints
    print(f"\n  {'R/r_s':>10s}  {'Phi':>10s}  {'C':>10s}  {'Regime':>30s}")
    print(f"  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*30}")

    checkpoints = [100.0, 50.0, 10.0, 5.0, 3.0, 2.0, 1.5, 1.0, 0.8, 0.5, 0.4, 0.35, 0.34, 0.3333]
    for cp in checkpoints:
        # Find closest index
        diffs = np.abs(R_rs - cp)
        idx = np.argmin(diffs)
        if diffs[idx] > 0.5 * cp:
            continue
        phi_val = Phi_arr[idx]
        c_val = C_arr[idx]
        if phi_val < 0.01:
            regime = "Quantum Fluid"
        elif phi_val < 0.10:
            regime = "Onset"
        elif phi_val < 0.50:
            regime = "Transition"
        elif phi_val < 0.90:
            regime = "Crystallization"
        elif phi_val < 0.99:
            regime = "Near-Equilibrium"
        else:
            regime = "Barrier-Dominated Core"
        print(f"  {R_rs[idx]:>10.4f}  {phi_val:>10.6f}  {c_val:>10.4f}  {regime:>30s}")

    # Identify Phi = 0.5 crossing
    phi_half_R = None
    for i in range(1, n):
        if Phi_arr[i-1] < 0.5 <= Phi_arr[i]:
            phi_half_R = R_rs[i]
            break
    if phi_half_R is not None:
        print(f"\n  Crystallization threshold (Phi=0.5) at R/r_s ≈ {phi_half_R:.4f}")
        print(f"  Compactness at threshold: C ≈ {r_s/(phi_half_R*r_s):.4f}" if phi_half_R > 0 else "")
    else:
        print(f"\n  Phi=0.5 crossing not found in trajectory")

    # Transition characterization
    phi_01_idx = None
    phi_09_idx = None
    for i in range(n):
        if Phi_arr[i] >= 0.1 and phi_01_idx is None:
            phi_01_idx = i
        if Phi_arr[i] >= 0.9 and phi_09_idx is None:
            phi_09_idx = i
            break

    if phi_01_idx is not None and phi_09_idx is not None:
        R_01 = R_rs[phi_01_idx]
        R_09 = R_rs[phi_09_idx]
        width = R_01 - R_09
        print(f"  Transition width: Phi=0.1 at R/r_s={R_01:.4f}, Phi=0.9 at R/r_s={R_09:.4f}")
        print(f"  Width in r_s: {width:.4f}")
        if width < 0.1:
            print(f"  Transition: SHARP")
        elif width < 0.5:
            print(f"  Transition: MODERATE")
        else:
            print(f"  Transition: SMOOTH")

    # Is transition post-horizon?
    if phi_half_R is not None:
        C_half = 1.0 / phi_half_R if phi_half_R > 0 else 0.0
        if C_half > 1.0:
            print(f"  Crystallization is POST-HORIZON (C={C_half:.2f} > 1)")
        else:
            print(f"  Crystallization is PRE-HORIZON (C={C_half:.2f} < 1)")

    return R_rs, Phi_arr, C_arr


# ================================================================
# TASK 3: INFORMATION LEDGER TRAJECTORY TRACKING
# ================================================================
def task3_ledger_tracking():
    _header("TASK 3: Information Ledger Along Trajectory")
    r = _run(record_every=100, n_steps=N_STEPS)
    r_s = r.r_s_m
    n = len(r.R_m)

    # Compute ledger at endpoint
    ledger_final = from_collapse_result(r)
    d = to_dict(ledger_final)

    print(f"  Endpoint ledger:")
    print(f"    I_fields          = {ledger_final.I_fields:.6e}")
    print(f"    I_metric_memory   = {ledger_final.I_metric_memory:.6e}")
    print(f"    I_total           = {ledger_final.I_total:.6e}")
    print(f"    archive_access    = {ledger_final.archive_access_status}")
    print(f"    conservation      = {ledger_final.conservation_status}")
    print(f"    compactness       = {ledger_final.compactness:.4f}")
    print(f"    barrier_dominance = {ledger_final.barrier_dominance:.6f}")

    # Track I_fields and Phi along trajectory at sample points
    import math as _math
    L_P2 = (1.054571817e-34 * 6.674e-11 / 299792458.0**3)  # l_P^2

    sample_indices = np.linspace(0, n-1, min(20, n), dtype=int)
    print(f"\n  {'step':>8s}  {'R/r_s':>10s}  {'C':>8s}  {'I_fields':>12s}  {'Phi':>10s}  {'I_metric':>12s}  {'I_total':>12s}")
    print(f"  {'-'*8}  {'-'*10}  {'-'*8}  {'-'*12}  {'-'*10}  {'-'*12}  {'-'*12}")

    I_fields_arr = []
    I_total_arr = []
    R_rs_arr = []

    for idx in sample_indices:
        R_i = float(r.R_m[idx])
        if R_i <= 0:
            continue
        C_i = r_s / R_i
        I_f = _math.pi * R_i**2 / L_P2

        # Compute local Phi
        a_grav_i = G_SI * M_REF / (R_i * R_i)
        Md_i = float(r.M_drive[idx])
        a_inward_i = (1.0 - ALPHA_VAC) * a_grav_i + ALPHA_VAC * Md_i
        a_Q_i = float(r.a_Q[idx]) if r.a_Q is not None else 0.0
        phi_i = a_Q_i / a_inward_i if a_inward_i > 0 and a_Q_i > 0 else 0.0

        # Memory tracking
        mem_ratio_i = Md_i / a_grav_i if a_grav_i > 0 else 0.0
        I_m = I_f * max(mem_ratio_i, 0.0) * max(phi_i, 0.0)
        I_t = I_f + I_m

        I_fields_arr.append(I_f)
        I_total_arr.append(I_t)
        R_rs_arr.append(R_i / r_s)

        print(f"  {idx:>8d}  {R_i/r_s:>10.4f}  {C_i:>8.4f}  {I_f:>12.4e}  {phi_i:>10.6f}  {I_m:>12.4e}  {I_t:>12.4e}")

    # Saturation behavior near endpoint
    if len(I_total_arr) >= 3:
        I_late = I_total_arr[-3:]
        I_ratio = max(I_late) / min(I_late) if min(I_late) > 0 else float("inf")
        print(f"\n  I_total late-time stability (last 3 samples): ratio = {I_ratio:.6f}")
        if I_ratio < 1.01:
            print(f"  => Structured saturation: I_total stabilizes near endpoint")
        else:
            print(f"  => I_total still evolving near endpoint")

    print(f"\n  NONCLAIM: This ledger tracking uses PROXY definitions.")
    print(f"  It does NOT prove information conservation.")
    print(f"  It shows whether the ledger exhibits structured behavior near Phi->1.")

    return ledger_final


# ================================================================
# SUMMARY
# ================================================================
def print_summary():
    _header("PHASE III-B AUDIT SUMMARY")
    print(f"  Constrained law: epsilon_Q = alpha_vac^2 = {EPS_Q_CONSTRAINED:.6f}")
    print(f"  beta_Q = {BETA_Q_CONSTRAINED}")
    print(f"  R_eq predicted = {R_EQ_PREDICTED:.6f}")
    print()

    expected = [
        ("vtol", "V_tol insensitive"),
        ("r0", "R0 insensitive"),
        ("force_balance", "Force balanced"),
        ("operator_share", "Operator-driven"),
        ("artifact", "Not artifact"),
        ("hcap", "H_cap independent"),
        ("no_regression", "No regression"),
        ("no_bounce", "No bounce violation"),
        ("analytical", "Analytical match"),
        ("stability_converge", "Stability converge"),
        ("stability_positive", "Stability positive"),
    ]

    all_pass = True
    for key, label in expected:
        if key in results:
            passed, detail = results[key]
            status = "PASS" if passed else "FAIL"
            if not passed:
                all_pass = False
            print(f"  {label:<24s}  {status:>4s}  ({detail})")
        else:
            print(f"  {label:<24s}  SKIP")
            all_pass = False

    print()
    if all_pass:
        print(f"  OVERALL: ALL CRITERIA PASS")
        print(f"  The constrained law epsilon_Q=alpha_vac^2, beta_Q=2 survives")
        print(f"  the full anti-artifact acceptance suite.")
        print(f"  STATUS RECOMMENDATION: preferred constrained law / candidate-canon")
    else:
        print(f"  OVERALL: SOME CRITERIA FAILED")
        print(f"  The constrained law requires further work.")
        print(f"  STATUS RECOMMENDATION: still research target")

    print(f"\n  EXPLICIT NONCLAIMS:")
    print(f"  - epsilon_Q and beta_Q are CONSTRAINED, not fully DERIVED")
    print(f"  - Missing: micro-derivation of alpha_vac^2 coupling")
    print(f"  - Missing: curvature-to-force mapping")
    print(f"  - Missing: covariant extension")
    print(f"  - Archive/unitarity remains OPEN")
    print(f"  - Information ledger is PROXY-based, not operational")

    return all_pass


# ================================================================
# MAIN
# ================================================================
if __name__ == "__main__":
    t0 = time.time()
    print(f"Phase III-B Audit")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Constrained law: epsilon_Q = {EPS_Q_CONSTRAINED:.6f}, beta_Q = {BETA_Q_CONSTRAINED}")
    print(f"R_eq/r_s predicted = {R_EQ_PREDICTED:.6f}")

    # TASK 1: Stress test
    task1_vtol()
    task1_r0()
    task1_force_balance()
    task1_stability()
    task1_artifact()
    task1_hcap()
    task1_no_regression()
    task1_no_bounce()
    task1_analytical_match()

    # TASK 2: Phi mapping
    task2_phi_mapping()

    # TASK 3: Ledger tracking
    task3_ledger_tracking()

    # Summary
    overall = print_summary()

    elapsed = time.time() - t0
    print(f"\nTotal runtime: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    sys.exit(0 if overall else 1)
