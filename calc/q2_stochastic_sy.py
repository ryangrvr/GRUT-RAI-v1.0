#!/usr/bin/env python3
"""Q2 INSTRUMENT -- stochastic Starobinsky-Yokoyama dynamics of a light self-interacting
scalar in de Sitter.  SETUP-FROZEN 2026-09-07; EXECUTION REQUIRES OWNER AUTHORIZATION.

SCOPE FENCE, ON THE FILE'S FACE (read before any use of this output).
  This instrument does NOT compute O2 (the interacting GRAVITON zero-mode) and CANNOT
  discharge reopening key #1 of GRUT_PROGRAM_FREEZE.md section 5.  It evolves the SCALAR
  Starobinsky-Yokoyama channel -- the same channel the record already cites for the claim
  that "any perturbation lifts" the exact-dS zero (RAI_GORILLA_T1.md section XVI-N;
  calc/two_scale_desitter.py).  The scalar-to-graviton gap is UNRESOLVED and is declared in
  program/gates/Q2_STOCHASTIC_EXECUTION_PREREG.md section 3.  Any use of this output as if
  it were O2 is laundering.

WHAT IT DOES.  Integrates the overdamped Langevin (stochastic-inflation) equation

    dphi/dt = -V'(phi)/(3H) + (H/2pi) eta(t),   <eta(t)eta(t')> = delta(t-t')
    V(phi)  = 0.5 m^2 phi^2 + (lambda/4) phi^4

over an ensemble, and measures relaxation rates and stationary moments.  The equation, the
noise amplitude H/2pi (Gibbons-Hawking), and the drift 1/(3H) are INHERITED verbatim from
calc/two_scale_desitter.py (committed); nothing here introduces a new physical scale.

VERDICT DISCIPLINE.  This instrument emits MACHINE labels only --
OBSERVED / NOT_OBSERVED / INCONCLUSIVE / INVALID_RUN / CONVERGED / NONCONVERGED.
It NEVER emits PASS/FAIL, "confirmed", "predicted", or any scientific adjudication; that is
reserved for the audit layer and the owner.  Comparison targets are computed here from
analytic formulae by independent quadrature, never fitted to the simulation.

NO HIDDEN DEFAULTS.  Every physically meaningful parameter is required in the config file;
the loader raises on any missing key.  Numerical/computational parameters are declared as
such in the config and echoed into the output manifest.

Units: H = 1 throughout (time in Hubble times, phi in units of H).  Pure stdlib.
"""
import hashlib
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# --- keys that MUST be present; no defaults anywhere in this file -------------------
REQUIRED_PHYSICAL = ["H", "m2_over_H2", "lambda_self", "phi0_over_H", "noise_amplitude_rule"]
REQUIRED_NUMERICAL = ["dt", "t_max", "n_traj", "seed_base", "n_seeds", "burn_in_fraction",
                      "fit_windows", "sample_stride", "ac_traj", "ac_lag_max_t",
                      "ac_fit_frac", "ac_origin_stride", "ac_amplitude_cut",
                      "burn_in_time", "fit_window_coordinate",
                      "autocorrelation_lag_coordinate", "seed_list_explicit",
                      "rng_implementation"]
MACHINE_LABELS = {"OBSERVED", "NOT_OBSERVED", "INCONCLUSIVE", "INVALID_RUN",
                  "CONVERGED", "NONCONVERGED"}


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def sha256_obj(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def load_config(path):
    cfg = json.load(open(path))
    for k in REQUIRED_PHYSICAL:
        if k not in cfg.get("physical", {}):
            raise SystemExit(f"CONFIG ERROR: missing physical key '{k}' (no defaults exist)")
    for k in REQUIRED_NUMERICAL:
        if k not in cfg.get("numerical", {}):
            raise SystemExit(f"CONFIG ERROR: missing numerical key '{k}' (no defaults exist)")
    if cfg["physical"]["noise_amplitude_rule"] != "gibbons_hawking_H_over_2pi":
        raise SystemExit("CONFIG ERROR: noise rule is frozen to gibbons_hawking_H_over_2pi")
    return cfg


# ============================================================ analytic anchors
# Computed independently of the SDE.  These are the comparison targets; they are NEVER
# fitted, and the simulation is never tuned to them.

def diffusion_D(H):
    """D = (1/2)(H/2pi)^2 -- the Gibbons-Hawking diffusion constant (two_scale_desitter.py)."""
    return 0.5 * (H / (2.0 * math.pi)) ** 2


def ou_rate_analytic(m2, H):
    """Free-field (lambda=0) OU relaxation rate k = m^2/(3H).  At m^2=0.1H^2 -> 0.03333H."""
    return m2 / (3.0 * H)


def ou_variance_analytic(m2, H):
    """Free-field stationary variance D/k = 3H^4/(8 pi^2 m^2)."""
    return diffusion_D(H) / ou_rate_analytic(m2, H)


def sy_equilibrium_moments(m2, lam, H, phi_max=None, n=200001):
    """Stationary moments of the SY equilibrium P_eq ~ exp(-8 pi^2 V(phi)/(3 H^4)),
    by Simpson quadrature.  Independent of the integrator -- this is the anchor the
    stationary simulation is compared against."""
    def V(p):
        return 0.5 * m2 * p * p + 0.25 * lam * p ** 4
    beta = 8.0 * math.pi ** 2 / (3.0 * H ** 4)
    if phi_max is None:
        # extend until the weight is negligible; no tuning -- a pure numerical bound
        phi_max = 1.0
        while beta * V(phi_max) < 80.0:
            phi_max *= 1.5
            if phi_max > 1e6:
                break
    if n % 2 == 0:
        n += 1
    h = 2.0 * phi_max / (n - 1)
    z = m2_acc = m4_acc = 0.0
    for i in range(n):
        p = -phi_max + i * h
        w = 1.0 if i in (0, n - 1) else (4.0 if i % 2 == 1 else 2.0)
        f = math.exp(-beta * V(p))
        z += w * f
        m2_acc += w * f * p * p
        m4_acc += w * f * p ** 4
    return {"phi2": m2_acc / z, "phi4": m4_acc / z, "phi_max_used": phi_max,
            "quadrature_points": n}


# ============================================================ the integrator
def evolve_ensemble(cfg, m2, lam, seed, noise_scale=1.0, drift_scale=1.0,
                    record_mean=True, ac_traj=0, ac_start=None):
    """Euler-Maruyama on the overdamped Langevin equation.
    NOTE (declared): the noise is ADDITIVE, so the Milstein correction vanishes identically
    and Euler-Maruyama is strong order 1.0 here -- this is a property of the equation, not
    an approximation choice.
    noise_scale / drift_scale are CONTROL knobs (C1/C2-style limits), 1.0 in physics runs.
    """
    P = cfg["physical"]; N = cfg["numerical"]
    H = P["H"]; dt = N["dt"]; n_steps = int(round(N["t_max"] / dt))
    n_traj = N["n_traj"]; stride = N["sample_stride"]
    sigma = noise_scale * (H / (2.0 * math.pi)) * math.sqrt(dt)
    inv3H = drift_scale / (3.0 * H)
    rng = random.Random(seed)
    phi = [P["phi0_over_H"] * H] * n_traj
    times, means, vars_ = [], [], []
    ac_rows, ac_times = [], []          # stationary samples for the autocorrelation route
    ac_n = min(ac_traj, n_traj)
    ac_t0 = ac_start if ac_start is not None else N["burn_in_time"]   # declared, not recomputed
    for step in range(n_steps + 1):
        if step % stride == 0:
            s = sum(phi); s2 = sum(p * p for p in phi)
            mean = s / n_traj
            times.append(step * dt)
            means.append(mean)
            vars_.append(s2 / n_traj - mean * mean)
            if ac_n and step * dt >= ac_t0:
                ac_rows.append(phi[:ac_n]); ac_times.append(step * dt)
        if step == n_steps:
            break
        for i in range(n_traj):
            p = phi[i]
            drift = -(m2 * p + lam * p ** 3) * inv3H
            phi[i] = p + drift * dt + sigma * rng.gauss(0.0, 1.0)
    return {"t": times, "mean": means, "var": vars_, "final_phi_sample": phi[:64],
            "ac_rows": ac_rows, "ac_times": ac_times}


# ============================================================ observables
def fit_log_rate(times, values, t_lo, t_hi):
    """Least-squares slope of ln|value| over a PREREGISTERED window -> decay rate.
    Returns (rate, r_squared, n_points) or (None, None, n) if the window is unusable."""
    xs, ys = [], []
    for t, v in zip(times, values):
        if t_lo <= t <= t_hi and v is not None and abs(v) > 1e-12:
            xs.append(t); ys.append(math.log(abs(v)))
    n = len(xs)
    if n < 5:
        return None, None, n
    mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return None, None, n
    slope = sxy / sxx
    syy = sum((y - my) ** 2 for y in ys)
    r2 = (sxy * sxy) / (sxx * syy) if syy > 0 else None
    return -slope, r2, n


def autocorrelation_rate(ac_rows, ac_times, lag_max_t, origin_stride, fit_frac,
                         amplitude_cut):
    """PRIMARY rate estimator O1a: spectral gap from the stationary autocorrelation
    C(tau) = <(phi(t)-<phi>)(phi(t+tau)-<phi>)>_stationary ~ exp(-Lambda_1 tau).

    CONNECTED by construction: the per-origin ensemble mean is subtracted.  If the ensemble
    is not perfectly relaxed, <phi> != 0 and the RAW second moment would carry a
    non-decaying <phi>^2 pedestal biasing the fitted rate downward -- toward the slower of
    the two preregistered targets.  Caught and removed before execution.

    Statistically efficient (uses all origins and all recorded trajectories) and free of the
    ensemble-mean SNR cliff that limits the decay-fit route: C(tau) is a stationary average,
    so its error does NOT grow as the signal decays toward zero."""
    if not ac_rows or len(ac_rows) < 4:
        return {"rate": None, "reason": "insufficient stationary samples"}
    dt_s = ac_times[1] - ac_times[0]
    n_lag = int(round(lag_max_t / dt_s))
    n_t, n_traj = len(ac_rows), len(ac_rows[0])
    if n_lag >= n_t - 2:
        n_lag = max(2, n_t - 3)
    origins = list(range(0, n_t - n_lag, max(1, origin_stride)))
    if len(origins) < 2:
        return {"rate": None, "reason": "insufficient origins"}
    # per-origin ensemble means, for the CONNECTED correlation
    row_mean = [sum(r) / len(r) for r in ac_rows]
    taus, cs = [], []
    for L in range(n_lag + 1):
        acc = cnt = 0
        for o in origins:
            a, b = ac_rows[o], ac_rows[o + L]
            ma, mb = row_mean[o], row_mean[o + L]
            for i in range(n_traj):
                acc += (a[i] - ma) * (b[i] - mb)   # CONNECTED: subtracts the <phi>^2 pedestal
            cnt += n_traj
        taus.append(L * dt_s); cs.append(acc / cnt)
    c0 = cs[0]
    if c0 <= 0:
        return {"rate": None, "reason": "non-positive C(0)"}
    # fit over the first fit_frac of the lag range where C stays comfortably positive
    xs, ys = [], []
    for t, c in zip(taus, cs):
        if c / c0 > amplitude_cut and t <= fit_frac * taus[-1]:
            xs.append(t); ys.append(math.log(c / c0))
    if len(xs) < 5:
        return {"rate": None, "reason": "too few usable lags"}
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx if sxx else None
    r2 = (sxy * sxy) / (sxx * syy) if (sxx and syy) else None
    return {"rate": (-slope if slope is not None else None), "r2": r2, "n_lags": n,
            "C0": c0, "tau_max": taus[-1],
            "tau_fitted_max": max(xs) if xs else None,
            "knobs": {"origin_stride": origin_stride, "fit_frac": fit_frac,
                      "amplitude_cut": amplitude_cut},
            "n_origins": len(origins)}


def stationary_variance(times, vars_, t_burn):
    vals = [v for t, v in zip(times, vars_) if t >= t_burn]
    if not vals:
        return None
    mean = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals)) if len(vals) > 1 else 0.0
    return {"mean": mean, "sd": sd, "n_samples": len(vals)}


# ============================================================ main
def main(argv):
    cfg_path = argv[1] if len(argv) > 1 else os.path.join(HERE, "q2_config.json")
    cfg = load_config(cfg_path)
    P, N = cfg["physical"], cfg["numerical"]
    H = P["H"]; m2 = P["m2_over_H2"] * H * H; lam = P["lambda_self"]

    manifest = {
        "instrument": "calc/q2_stochastic_sy.py",
        "instrument_sha256": sha256_file(os.path.abspath(__file__)),
        "config_path": os.path.relpath(cfg_path, os.path.dirname(HERE)),
        "config_sha256": sha256_file(cfg_path),
        "config_echo": cfg,
        "python": sys.version.split()[0],
        "rng_implementation": cfg["numerical"]["rng_implementation"],
        "rng_module_state_class": type(random.Random()).__module__ + "." +
                                  type(random.Random()).__name__,
        "seeds_explicit": cfg["numerical"]["seed_list_explicit"],
        "fit_window_coordinate": cfg["numerical"]["fit_window_coordinate"],
        "autocorrelation_lag_coordinate": cfg["numerical"]["autocorrelation_lag_coordinate"],
        "burn_in_time": cfg["numerical"]["burn_in_time"],
        "scope_fence": ("scalar SY channel; NOT the interacting graviton zero-mode; "
                        "cannot discharge reopening key #1"),
        "verdict_discipline": "machine labels only; no scientific PASS/FAIL emitted",
    }

    anchors = {
        "diffusion_D": diffusion_D(H),
        "ou_rate_analytic_at_m2": ou_rate_analytic(m2, H) if m2 > 0 else None,
        "ou_variance_analytic_at_m2": ou_variance_analytic(m2, H) if m2 > 0 else None,
        "sy_equilibrium": sy_equilibrium_moments(m2, lam, H),
        "sy_dynamical_mass_rule": "m_eff^2 ~ sqrt(lambda) H^2 (record: RESULTS_conformalon.md)",
        "m_eff2_from_lambda": math.sqrt(lam) * H * H if lam > 0 else 0.0,
        "rate_from_m_eff2": ou_rate_analytic(math.sqrt(lam) * H * H, H) if lam > 0 else None,
        # TWO preregistered comparison targets -- both declared BEFORE execution so that
        # neither can be selected after the fact (the "check what your check is compared
        # against" rule).  They differ by ~3.8x; see prereg section 2.2 / U4.
        "target_A_naive_meff_over_3H": math.sqrt(lam) * H / 3.0,
        "target_A_provenance": "record rule m_eff^2 ~ sqrt(lambda) H^2 fed into the free-field "
                               "OU rate m^2/(3H); the reopening-key referent (0.0333H at lambda=0.01)",
        "target_B_sy_fp_eigenvalue": 0.0885 * math.sqrt(lam) * H,
        "target_B_provenance": "Starobinsky-Yokoyama Fokker-Planck first eigenvalue for "
                               "lambda phi^4/4, Lambda_1 = 0.0885 sqrt(lambda) H (literature "
                               "coefficient; the O(1) constant the record does NOT supply -- U4)",
    }

    t0 = time.time()
    runs, results = {}, {}
    seeds = list(N["seed_list_explicit"])          # the explicit integers, not a formula
    if seeds != [N["seed_base"] + i for i in range(N["n_seeds"])]:
        raise SystemExit("CONFIG ERROR: seed_list_explicit disagrees with seed_base/n_seeds")

    # ---- PRIMARY: the interacting physics run, replicated across frozen seeds ----
    primary = []
    for s in seeds:
        r = evolve_ensemble(cfg, m2, lam, s, ac_traj=N["ac_traj"])
        # O1a PRIMARY: autocorrelation (no SNR cliff)
        ac = autocorrelation_rate(r["ac_rows"], r["ac_times"], N["ac_lag_max_t"],
                                  N["ac_origin_stride"], N["ac_fit_frac"],
                                  N["ac_amplitude_cut"])
        # O1b CROSS-CHECK: ensemble-mean decay fit over EVERY preregistered window
        windows = []
        for (w0, w1) in N["fit_windows"]:
            rate, r2, npts = fit_log_rate(r["t"], r["mean"], w0, w1)
            windows.append({"window": [w0, w1], "rate": rate, "r2": r2, "points": npts})
        var = stationary_variance(r["t"], r["var"], N["burn_in_fraction"] * N["t_max"])
        primary.append({"seed": s, "autocorrelation_rate": ac, "decay_fits": windows,
                        "stationary_var": var,
                        "D1_final_phi_sample": r["final_phi_sample"]})
    runs["primary"] = primary

    rates = [p["autocorrelation_rate"]["rate"] for p in primary
             if p["autocorrelation_rate"].get("rate") is not None]
    if rates:
        mr = sum(rates) / len(rates)
        sdr = math.sqrt(sum((x - mr) ** 2 for x in rates) / len(rates)) if len(rates) > 1 else 0.0
        results["primary_rate"] = {"mean": mr, "sd": sdr, "n_seeds": len(rates),
                                   "seed_spread_relative": (sdr / mr) if mr else None}
    else:
        results["primary_rate"] = {"label": "INVALID_RUN", "reason": "no usable rate fits"}

    manifest["wall_seconds"] = time.time() - t0
    out = {"manifest": manifest, "analytic_anchors": anchors, "runs": runs,
           "results": results,
           "labels_available": sorted(MACHINE_LABELS),
           "note": ("Adjudication is NOT performed here. Controls are run by "
                    "--controls; convergence ladders by --converge.")}
    outpath = os.path.join(HERE, "RESULTS_q2_stochastic_sy.json")
    json.dump(out, open(outpath, "w"), indent=1)
    # human-readable report (repo convention: every calc ships a RESULTS_*.md)
    md = [f"# RESULTS — Q2 stochastic SY run", "",
          "> Machine labels only. NO scientific adjudication is performed here; see",
          "> `program/gates/Q2_STOCHASTIC_EXECUTION_PREREG.md` §18 for the frozen decision",
          "> tree. This instrument evolves the SCALAR SY channel and is NOT O2.", "",
          f"- instrument sha256: `{manifest['instrument_sha256']}`",
          f"- config sha256: `{manifest['config_sha256']}`",
          f"- python {manifest['python']} · RNG {manifest['rng_implementation']}",
          f"- seeds: {manifest['seeds_explicit']}",
          f"- wall seconds: {manifest['wall_seconds']:.1f}", "",
          "## Preregistered comparison targets (emitted before measurement)", "",
          f"- target A (record composition m_eff^2/3H): {anchors['target_A_naive_meff_over_3H']:.6f} H",
          f"- target B (SY Fokker-Planck eigenvalue): {anchors['target_B_sy_fp_eigenvalue']:.6f} H", "",
          "## Primary estimator O1a (stationary connected autocorrelation, LAG coordinate)", "",
          "| seed | rate | r2 | n_lags |", "|---|---|---|---|"]
    for p_ in primary:
        a_ = p_["autocorrelation_rate"]
        md.append(f"| {p_['seed']} | {a_.get('rate')} | {a_.get('r2')} | {a_.get('n_lags')} |")
    md += ["", "## Cross-check O1b (ensemble-mean decay, ABSOLUTE TIME, transient phase)", "",
           "| seed | window | rate | r2 |", "|---|---|---|---|"]
    for p_ in primary:
        for w in p_["decay_fits"]:
            md.append(f"| {p_['seed']} | {w['window']} | {w['rate']} | {w['r2']} |")
    md += ["", f"## Aggregate", "", f"```json", json.dumps(results, indent=1), "```"]
    open(os.path.join(HERE, "RESULTS_q2_stochastic_sy.md"), "w").write("\n".join(md) + "\n")
    print(f"[q2] wrote {outpath} and RESULTS_q2_stochastic_sy.md ({manifest['wall_seconds']:.1f}s)")
    print("[q2] machine labels only; scientific adjudication belongs to the audit layer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
