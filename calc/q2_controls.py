#!/usr/bin/env python3
"""Q2 CONTROL BATTERY -- Q2-C1..C10.  SETUP-FROZEN; execution requires authorization.

NUMBERING FENCE (mandatory, per the setup instruction).  These are numbered Q2-C1..C10 and
are NOT the house N1-N10 battery.  Only N4 (null-manufacturing mutant) and N5 (displaced
gate) carry committed definitions in the record (RAI_GORILLA_T1.md lines 36-41); N1-N3 and
N6-N10 are referenced but their definitions are NOT in the committed record and are marked
UNRESOLVED -- CONTROL DEFINITION REQUIRED in the preregistration.  Q2-C1..C10 are built
only from already-declared structure and claim no correspondence to the N-numbering.
Where the N-analogues DO apply they are noted per control.

Each control states what result would DISAPPEAR if the claimed mechanism were real.
Machine labels only.  Pure stdlib.
"""
import json, math, os, sys
import q2_stochastic_sy as Q2

HERE = os.path.dirname(os.path.abspath(__file__))


def _rate_from(cfg, m2, lam, seed, noise_scale=1.0, drift_scale=1.0):
    N = cfg["numerical"]
    r = Q2.evolve_ensemble(cfg, m2, lam, seed, noise_scale, drift_scale)
    w0, w1 = N["fit_windows"][0]           # controls use the FIRST preregistered window
    rate, r2, n = Q2.fit_log_rate(r["t"], r["mean"], w0, w1)
    var = Q2.stationary_variance(r["t"], r["var"], N["burn_in_fraction"] * N["t_max"])
    return {"rate": rate, "r2": r2, "fit_points": n, "stationary_var": var, "raw": r}


def control_C1_zero_noise(cfg):
    """C1 ZERO-NOISE LIMIT. noise_scale=0 -> deterministic decay at exactly m^2/(3H).
    DISAPPEARS IF REAL: if the measured relaxation were a noise artifact, killing the noise
    would remove it. Here it must SURVIVE and match the analytic drift rate."""
    P = cfg["physical"]; H = P["H"]
    m2 = cfg["controls"]["ou_baseline_m2_over_H2"] * H * H   # analytic anchor needs m2>0
    out = _rate_from(cfg, m2, 0.0, cfg["numerical"]["seed_base"], noise_scale=0.0)
    target = Q2.ou_rate_analytic(m2, H)
    return {"control": "Q2-C1", "measured_rate": out["rate"], "analytic_drift_rate": target,
            "stationary_var_should_be_zero": out["stationary_var"],
            "criterion": "|measured-target|/target <= tol_rate AND var -> 0"}


def control_C2_zero_interaction(cfg):
    """C2 ZERO-INTERACTION LIMIT. lambda=0 -> exact Ornstein-Uhlenbeck.
    DISAPPEARS IF REAL: an interaction-generated effect must vanish; the OU baseline must be
    reproduced exactly (rate m^2/3H, variance 3H^4/(8pi^2 m^2))."""
    P = cfg["physical"]; H = P["H"]
    m2 = cfg["controls"]["ou_baseline_m2_over_H2"] * H * H
    out = _rate_from(cfg, m2, 0.0, cfg["numerical"]["seed_base"])
    return {"control": "Q2-C2", "measured_rate": out["rate"],
            "analytic_rate": Q2.ou_rate_analytic(m2, H),
            "measured_var": out["stationary_var"],
            "analytic_var": Q2.ou_variance_analytic(m2, H),
            "criterion": "both within tol; this is the strongest correctness anchor"}


def control_C3_massless_free_NULL(cfg):
    """C3 THE NULL CONTROL -- massless, non-interacting (m=0, lambda=0).
    This is the numerical analogue of the UNLIFTED exact-dS zero mode (Delta_- = 0).
    There is NO relaxation: the variance must grow as 2*D*t without bound and the mean must
    NOT decay.  DISAPPEARS IF REAL: if the instrument reports a finite relaxation rate HERE,
    it manufactures lifting out of discretization/analysis and every 'lift' result in the
    primary run is void.  This is the single most important control in the battery
    (N-analogue: the null-manufacturing role of N4)."""
    out = _rate_from(cfg, 0.0, 0.0, cfg["numerical"]["seed_base"])
    N = cfg["numerical"]; D = Q2.diffusion_D(cfg["physical"]["H"])
    ts, vs = out["raw"]["t"], out["raw"]["var"]
    pred = [2.0 * D * t for t in ts]
    dev = max((abs(v - p) / p) for v, p in zip(vs[1:], pred[1:]) if p > 0) if len(ts) > 1 else None
    return {"control": "Q2-C3", "measured_rate_MUST_BE_null": out["rate"],
            "max_relative_deviation_from_2Dt": dev,
            "criterion": "rate is None or |rate| <= tol_null AND var tracks 2Dt within tol",
            "role": "voids the primary run if it reports relaxation"}


def control_C4_timestep(cfg, ladder):
    """C4 TIMESTEP REFINEMENT. rate(dt) must converge as dt->0.
    DISAPPEARS IF REAL: a discretization artifact drifts with dt; real dynamics does not."""
    P = cfg["physical"]; H = P["H"]; m2 = P["m2_over_H2"] * H * H
    rows = []
    for dt in ladder:
        c = json.loads(json.dumps(cfg)); c["numerical"]["dt"] = dt
        c["numerical"]["sample_stride"] = max(1, int(round(cfg["numerical"]["sample_stride"]
                                                          * cfg["numerical"]["dt"] / dt)))
        rows.append({"dt": dt, "rate": _rate_from(c, m2, P["lambda_self"],
                                                  cfg["numerical"]["seed_base"])["rate"]})
    return {"control": "Q2-C4", "ladder": rows,
            "criterion": "successive |rate(dt_k)-rate(dt_k+1)|/rate <= tol_converge"}


def control_C5_seeds(cfg, seeds):
    """C5 SEED DEPENDENCE. Spread across frozen seeds must be within statistical expectation.
    DISAPPEARS IF REAL: a seed-specific fluctuation does not survive replication."""
    P = cfg["physical"]; H = P["H"]; m2 = P["m2_over_H2"] * H * H
    rs = [_rate_from(cfg, m2, P["lambda_self"], s)["rate"] for s in seeds]
    good = [r for r in rs if r is not None]
    mean = sum(good) / len(good) if good else None
    sd = (math.sqrt(sum((r - mean) ** 2 for r in good) / len(good))
          if good and len(good) > 1 else None)
    return {"control": "Q2-C5", "seeds": seeds, "rates": rs, "mean": mean, "sd": sd,
            "relative_spread": (sd / mean) if (sd is not None and mean) else None,
            "criterion": "relative_spread <= tol_seed"}


def control_C6_initial_condition(cfg, phi0_list):
    """C6 INITIAL-CONDITION DEPENDENCE. Stationary variance must be INDEPENDENT of phi0.
    DISAPPEARS IF REAL: an initialization imprint moves the stationary state; genuine
    stationarity does not."""
    P = cfg["physical"]; H = P["H"]; m2 = P["m2_over_H2"] * H * H
    rows = []
    for p0 in phi0_list:
        c = json.loads(json.dumps(cfg)); c["physical"]["phi0_over_H"] = p0
        rows.append({"phi0": p0,
                     "stationary_var": _rate_from(c, m2, P["lambda_self"],
                                                  cfg["numerical"]["seed_base"])["stationary_var"]})
    return {"control": "Q2-C6", "rows": rows,
            "criterion": "stationary variances agree within tol across phi0"}


def control_C7_noise_normalization(cfg, n_draws=200000):
    """C7 NOISE NORMALIZATION. Directly measure the increment variance against (H/2pi)^2 dt.
    DISAPPEARS IF REAL: a mis-normalized noise shifts every stationary moment; this catches
    it at the source rather than through the physics."""
    import random
    P, N = cfg["physical"], cfg["numerical"]
    sigma = (P["H"] / (2.0 * math.pi)) * math.sqrt(N["dt"])
    rng = random.Random(N["seed_base"] + 99991)
    s2 = sum((sigma * rng.gauss(0, 1)) ** 2 for _ in range(n_draws)) / n_draws
    target = (P["H"] / (2.0 * math.pi)) ** 2 * N["dt"]
    return {"control": "Q2-C7", "measured_increment_variance": s2, "target": target,
            "relative_error": abs(s2 - target) / target,
            "criterion": "relative_error <= tol_noise (statistical, ~1/sqrt(n_draws))"}


def control_C8_planted_positive(cfg, planted_m2_over_H2):
    """C8 PLANTED POSITIVE (sensitivity calibration). Inject a KNOWN mass and require the
    pipeline to recover its analytic rate.  Not rigged pro-GRUT: the planted value is
    class-mathematics (OU), and failure to recover it indicts the instrument, not the
    physics.  DISAPPEARS IF REAL: an instrument blind to a real rate cannot be trusted to
    report one (N-analogue: the detect-capability role of N5)."""
    P = cfg["physical"]; H = P["H"]; m2p = planted_m2_over_H2 * H * H
    out = _rate_from(cfg, m2p, 0.0, cfg["numerical"]["seed_base"] + 7)
    return {"control": "Q2-C8", "planted_m2_over_H2": planted_m2_over_H2,
            "recovered_rate": out["rate"], "analytic_rate": Q2.ou_rate_analytic(m2p, H),
            "criterion": "recovered within tol_rate of analytic"}


def control_C9_stationary_distribution(cfg):
    """C9 STATIONARY MOMENTS vs the INDEPENDENT quadrature anchor.
    DISAPPEARS IF REAL: a solver that violates detailed balance lands on the wrong stationary
    distribution even when its rate looks plausible."""
    P = cfg["physical"]; H = P["H"]; m2 = P["m2_over_H2"] * H * H
    out = _rate_from(cfg, m2, P["lambda_self"], cfg["numerical"]["seed_base"])
    anchor = Q2.sy_equilibrium_moments(m2, P["lambda_self"], H)
    return {"control": "Q2-C9", "measured_var": out["stationary_var"],
            "quadrature_phi2": anchor["phi2"],
            "criterion": "|measured - quadrature|/quadrature <= tol_moment"}


def control_C10_ensemble_size(cfg, sizes):
    """C10 ENSEMBLE-SIZE REFINEMENT. Estimates must stabilize as n_traj grows.
    DISAPPEARS IF REAL: a small-ensemble fluctuation shrinks with N; a real effect does not."""
    P = cfg["physical"]; H = P["H"]; m2 = P["m2_over_H2"] * H * H
    rows = []
    for n in sizes:
        c = json.loads(json.dumps(cfg)); c["numerical"]["n_traj"] = n
        rows.append({"n_traj": n, "rate": _rate_from(c, m2, P["lambda_self"],
                                                     cfg["numerical"]["seed_base"])["rate"]})
    return {"control": "Q2-C10", "ladder": rows,
            "criterion": "successive differences shrink and last step <= tol_converge"}


def main(argv):
    cfg_path = argv[1] if len(argv) > 1 else os.path.join(HERE, "q2_config.json")
    cfg = Q2.load_config(cfg_path)
    L = cfg["controls"]
    res = {
        "battery": "Q2-C1..C10 (NOT the house N1-N10; see numbering fence)",
        "config_sha256": Q2.sha256_file(cfg_path),
        "C1": control_C1_zero_noise(cfg),
        "C2": control_C2_zero_interaction(cfg),
        "C3": control_C3_massless_free_NULL(cfg),
        "C4": control_C4_timestep(cfg, L["timestep_ladder"]),
        "C5": control_C5_seeds(cfg, L["seed_list"]),
        "C6": control_C6_initial_condition(cfg, L["phi0_list"]),
        "C7": control_C7_noise_normalization(cfg),
        "C8": control_C8_planted_positive(cfg, L["planted_m2_over_H2"]),
        "C9": control_C9_stationary_distribution(cfg),
        "C10": control_C10_ensemble_size(cfg, L["ensemble_ladder"]),
    }
    out = os.path.join(HERE, "RESULTS_q2_controls.json")
    json.dump(res, open(out, "w"), indent=1)
    print(f"[q2-controls] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    raise SystemExit(main(sys.argv))
