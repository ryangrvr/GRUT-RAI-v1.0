#!/usr/bin/env python3
"""Q2 ESTIMATOR-VALIDITY AUDIT (deterministic, NON-EVIDENTIARY, no stochastic ensemble).

QUESTION (owner-posed, the last pre-execution gate): the frozen primary observable O1a is a
log-linear fit to a FINITE-LAG autocorrelation. For a nonlinear process
    C(tau) = sum_i A_i exp(-Lambda_i tau),  NOT  A exp(-Lambda_1 tau).
Lambda_1 dominates only once the faster modes have died. Does the FROZEN estimator, over the
FROZEN lag domain, actually estimate Lambda_1 for the nonlinear phi^4 equation -- or is it
contaminated by higher modes?

METHOD (independent of the SDE and of the OU calibration):
  1. Build the Fokker-Planck operator for dphi/dt = -V'(phi)/(3H) + (H/2pi) eta directly,
     symmetrized to the Schroedinger form -psi'' + W(phi) psi with
     W = (U'/2)^2 - U''/2,  U = beta V,  beta = 8 pi^2/(3 H^4),  Lambda_n = D * lambda_n.
  2. Eigenvalues by Sturm bisection; eigenvectors by inverse iteration (tridiagonal).
  3. Weights A_n = |<phi>_{0n}|^2 give the EXACT multi-exponential C(tau).
  4. Replicate the FROZEN fit exactly on that noise-free C(tau) and compare to Lambda_1.
  5. Report the instantaneous log-slope -dlnC/dtau vs tau to locate any asymptotic regime.
This file NEVER retunes anything and writes no config. Pure stdlib.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def build_W(lam, m2, beta):
    """W(phi) for V = m2 phi^2/2 + lam phi^4/4;  U = beta V."""
    def W(p):
        Up = beta * (m2 * p + lam * p ** 3)
        Upp = beta * (m2 + 3.0 * lam * p * p)
        return 0.25 * Up * Up - 0.5 * Upp
    return W


def sturm_count(d, e2, x):
    """Number of eigenvalues < x for the symmetric tridiagonal (d, off-diag e), e2 = e^2."""
    n = len(d); count = 0; q = d[0] - x
    if q < 0: count += 1
    for i in range(1, n):
        if q == 0.0: q = 1e-300
        q = d[i] - x - e2[i - 1] / q
        if q < 0: count += 1
    return count


def eigenvalues(d, e2, k_max, lo, hi, tol=1e-11):
    """Lowest k_max eigenvalues by bisection on the Sturm count."""
    out = []
    for k in range(k_max):
        a, b = lo, hi
        for _ in range(200):
            mid = 0.5 * (a + b)
            if sturm_count(d, e2, mid) > k: b = mid
            else: a = mid
            if b - a < tol * max(1.0, abs(b)): break
        out.append(0.5 * (a + b))
    return out


def eigenvector(d, e, lamb, n_iter=60):
    """Inverse iteration for the eigenvector of a symmetric tridiagonal at shift lamb."""
    n = len(d)
    shift = lamb * (1.0 + 1e-8) + 1e-13
    v = [1.0 / math.sqrt(n)] * n
    for _ in range(n_iter):
        # Thomas algorithm on (T - shift I) x = v
        cp = [0.0] * n; dp = [0.0] * n
        b0 = d[0] - shift
        if abs(b0) < 1e-300: b0 = 1e-300
        cp[0] = e[0] / b0; dp[0] = v[0] / b0
        for i in range(1, n):
            den = (d[i] - shift) - e[i - 1] * cp[i - 1]
            if abs(den) < 1e-300: den = 1e-300
            cp[i] = (e[i] if i < n - 1 else 0.0) / den
            dp[i] = (v[i] - e[i - 1] * dp[i - 1]) / den
        x = [0.0] * n; x[n - 1] = dp[n - 1]
        for i in range(n - 2, -1, -1):
            x[i] = dp[i] - cp[i] * x[i + 1]
        nrm = math.sqrt(sum(t * t for t in x))
        if nrm == 0 or not math.isfinite(nrm): break
        v = [t / nrm for t in x]
    return v


def spectral_analysis(lam, m2, H, L=8.0, N=1600, n_modes=8):
    beta = 8.0 * math.pi ** 2 / (3.0 * H ** 4)
    D = 0.5 * (H / (2.0 * math.pi)) ** 2
    W = build_W(lam, m2, beta)
    h = 2.0 * L / (N - 1)
    phi = [-L + i * h for i in range(N)]
    d = [2.0 / h ** 2 + W(p) for p in phi]
    e = [-1.0 / h ** 2] * (N - 1)
    e2 = [x * x for x in e]
    lo = min(d) - 4.0 / h ** 2 - 1.0
    hi = max(d) + 4.0 / h ** 2 + 1.0
    evs = eigenvalues(d, e2, n_modes, lo, hi)
    modes = []
    for k, ev in enumerate(evs):
        v = eigenvector(d, e, ev)
        modes.append(v)
    # ground state defines P_eq^(1/2); normalise all with the same measure
    def dot(a, b): return sum(x * y for x, y in zip(a, b)) * h
    psi0 = modes[0]
    n0 = math.sqrt(dot(psi0, psi0)); psi0 = [x / n0 for x in psi0]
    out = {"beta": beta, "D": D, "grid": {"L": L, "N": N, "h": h},
           "lambda_schrodinger": evs,
           "Lambda_FP": [D * (ev - evs[0]) for ev in evs],
           "modes": []}
    # <phi^2>_eq from the ground state, as an independent cross-check
    p2 = sum(psi0[i] ** 2 * phi[i] ** 2 for i in range(N)) * h
    out["phi2_eq_from_ground_state"] = p2
    for k in range(1, n_modes):
        v = modes[k]; nv = math.sqrt(dot(v, v)); v = [x / nv for x in v]
        c = sum(phi[i] * psi0[i] * v[i] for i in range(N)) * h
        out["modes"].append({"n": k, "Lambda": D * (evs[k] - evs[0]), "weight": c * c})
    return out


def frozen_fit(taus, cs, fit_frac, amplitude_cut):
    """EXACT replication of the frozen estimator's fitting rule (q2_stochastic_sy.py)."""
    c0 = cs[0]
    xs, ys = [], []
    for t, c in zip(taus, cs):
        if c / c0 > amplitude_cut and t <= fit_frac * taus[-1]:
            xs.append(t); ys.append(math.log(c / c0))
    if len(xs) < 5: return None, None, 0
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    return -sxy / sxx, (sxy * sxy) / (sxx * syy) if syy > 0 else None, max(xs)


def main():
    cfg = json.load(open(os.path.join(HERE, "q2_config.json")))
    P, N = cfg["physical"], cfg["numerical"]
    H = P["H"]; lam = P["lambda_self"]; m2 = P["m2_over_H2"] * H * H
    rep = {"non_evidentiary": True,
           "purpose": "estimator-validity audit; no stochastic ensemble was run",
           "frozen_inputs_echo": {"lambda": lam, "m2_bare": m2, "H": H,
                                  "ac_lag_max_t": N["ac_lag_max_t"],
                                  "ac_fit_frac": N["ac_fit_frac"],
                                  "ac_amplitude_cut": N["ac_amplitude_cut"],
                                  "sample_dt": N["dt"] * N["sample_stride"]}}

    # ---- validation of the solver itself against the EXACT OU spectrum ----------
    ou_m2 = 0.3
    ou = spectral_analysis(0.0, ou_m2, H)
    rep["solver_validation_OU"] = {
        "m2": ou_m2, "exact_Lambda_n": [ou_m2 * n / 3.0 for n in range(1, 4)],
        "computed_Lambda_n": ou["Lambda_FP"][1:4],
        "note": "for V=m2 phi^2/2 the exact FP spectrum is Lambda_n = n m2/(3H)"}

    # ---- the nonlinear operator at the frozen lambda ----------------------------
    sp = spectral_analysis(lam, m2, H)
    L1 = sp["modes"][0]["Lambda"]
    rep["nonlinear_spectrum"] = {
        "Lambda_1": L1, "Lambda_1_over_sqrt_lambda": L1 / math.sqrt(lam),
        "preregistered_target_B_coefficient": 0.0885,
        "phi2_eq_from_ground_state": sp["phi2_eq_from_ground_state"],
        "modes": sp["modes"][:6]}

    # ---- the EXACT multi-exponential C(tau) and the frozen estimator on it -------
    odd = [m for m in sp["modes"] if m["weight"] > 1e-9]
    tot = sum(m["weight"] for m in odd)
    dt_s = N["dt"] * N["sample_stride"]
    n_lag = int(round(N["ac_lag_max_t"] / dt_s))
    taus = [i * dt_s for i in range(n_lag + 1)]
    cs = [sum(m["weight"] * math.exp(-m["Lambda"] * t) for m in odd) for t in taus]
    rate, r2, tfit = frozen_fit(taus, cs, N["ac_fit_frac"], N["ac_amplitude_cut"])
    rep["frozen_estimator_on_exact_C"] = {
        "estimated_rate": rate, "Lambda_1": L1,
        "relative_deviation": (rate - L1) / L1 if rate else None,
        "r2": r2, "tau_fitted_max": tfit,
        "mode_weight_fractions": [{"Lambda": m["Lambda"], "frac": m["weight"] / tot}
                                  for m in odd[:5]]}
    # ---- instantaneous log-slope: is there an asymptotic Lambda_1 regime? --------
    slope = []
    for i in range(1, len(taus)):
        s = -(math.log(cs[i]) - math.log(cs[i - 1])) / dt_s
        if i % 40 == 0 or i in (1, 2, 4, 8, 20):
            slope.append({"tau": taus[i], "local_slope": s, "ratio_to_Lambda_1": s / L1})
    rep["instantaneous_log_slope"] = slope
    # ---- the discrimination question the owner posed ----------------------------
    sep = (math.sqrt(lam) / 3.0) / L1
    rep["discrimination"] = {
        "target_A": math.sqrt(lam) / 3.0, "Lambda_1_computed": L1,
        "separation_factor": sep,
        "estimator_bias_relative": (rate - L1) / L1 if rate else None}
    json.dump(rep, open(os.path.join(HERE, "RESULTS_q2_estimator_validity.json"), "w"), indent=1)
    # console summary
    print("SOLVER VALIDATION (OU, exact Lambda_n = n m2/3H):")
    for ex, co in zip(rep["solver_validation_OU"]["exact_Lambda_n"],
                      rep["solver_validation_OU"]["computed_Lambda_n"]):
        print(f"   exact {ex:.6f}   computed {co:.6f}   rel {100*(co-ex)/ex:+.3f}%")
    print(f"\nNONLINEAR phi^4 at lambda={lam}:")
    print(f"   Lambda_1 = {L1:.6f}  = {L1/math.sqrt(lam):.5f} sqrt(lambda) H "
          f"(preregistered coefficient 0.0885)")
    print(f"   <phi^2>_eq from ground state = {sp['phi2_eq_from_ground_state']:.6f} "
          f"(analytic 1.317645)")
    print("   mode structure of C(tau):")
    for m in rep["frozen_estimator_on_exact_C"]["mode_weight_fractions"]:
        print(f"      Lambda={m['Lambda']:.6f}  weight fraction {m['frac']:.5f}")
    print(f"\nFROZEN ESTIMATOR ON THE EXACT NOISE-FREE C(tau):")
    print(f"   returns {rate:.6f}  vs Lambda_1 {L1:.6f}   bias {100*(rate-L1)/L1:+.2f}%  "
          f"(r2={r2:.6f}, fitted to tau={tfit:.0f})")
    print("\nINSTANTANEOUS LOG-SLOPE (is there an asymptotic Lambda_1 regime?):")
    for s in rep["instantaneous_log_slope"]:
        print(f"   tau={s['tau']:7.2f}   -dlnC/dtau={s['local_slope']:.6f}   "
              f"= {s['ratio_to_Lambda_1']:.4f} x Lambda_1")
    print(f"\nDISCRIMINATION: target A / Lambda_1 = {sep:.2f}x ; estimator bias "
          f"{100*rep['discrimination']['estimator_bias_relative']:+.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
