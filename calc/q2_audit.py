#!/usr/bin/env python3
"""Q2 INDEPENDENT AUDITOR -- verifies the Q2 run WITHOUT sharing the instrument's analysis.

INDEPENDENCE RULE (enforced by design): this file does NOT import q2_stochastic_sy or
q2_controls.  Every quantity it checks is recomputed here from first principles or read
from the emitted JSON.  The simulation does not certify itself.

De-pinned: this auditor asserts well-formedness, schema completeness, config/hash
consistency, dimensional and analytic invariants, and convergence LOGIC.  It never asserts
which scientific outcome should occur, and emits machine labels only.  Pure stdlib.
"""
import hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FAIL, WARN, OK = "AUDIT_FAIL", "AUDIT_WARN", "AUDIT_OK"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check(cond, label, msg, findings):
    findings.append({"status": OK if cond else label, "check": msg})
    return cond


def main(argv):
    cfg_path = os.path.join(HERE, "q2_config.json")
    res_path = os.path.join(HERE, "RESULTS_q2_stochastic_sy.json")
    ctl_path = os.path.join(HERE, "RESULTS_q2_controls.json")
    findings, labels = [], {}

    # ---- 1. configuration integrity (runs even before execution) -------------------
    cfg = json.load(open(cfg_path))
    for sec in ("physical", "numerical", "controls", "tolerances"):
        check(sec in cfg, FAIL, f"config section '{sec}' present", findings)
    check(cfg["physical"]["noise_amplitude_rule"] == "gibbons_hawking_H_over_2pi",
          FAIL, "noise rule frozen to Gibbons-Hawking H/2pi", findings)
    check(cfg["physical"]["m2_over_H2"] == 0.0, FAIL,
          "primary run starts from BARE MASSLESS (relaxation must be generated)", findings)
    lam = cfg["physical"]["lambda_self"]
    check(abs(math.sqrt(lam) - 0.1) < 1e-12, FAIL,
          "lambda=0.01 reproduces the record's m_eff^2 = 0.1 H^2 via sqrt(lambda)", findings)
    wins = cfg["numerical"]["fit_windows"]
    check(all(w1 < cfg["numerical"]["t_max"] for _, w1 in wins), FAIL,
          "every fit window lies strictly inside the integration horizon", findings)
    check(all(w0 > 0 and w1 > w0 for w0, w1 in wins), FAIL,
          "every fit window excludes t=0 and is well ordered", findings)
    check(len(wins) >= 3, FAIL,
          "at least three fit windows preregistered (window-dependence is itself a control)",
          findings)
    # INDEPENDENT SNR safety re-derivation (the design defect this package was repaired for)
    lam_ = cfg["physical"]["lambda_self"]
    var_eq = math.sqrt(3.0 / (2.0 * math.pi ** 2 * lam_)) * math.gamma(0.75) / math.gamma(0.25)
    floor = math.sqrt(var_eq) / math.sqrt(cfg["numerical"]["n_traj"])
    k_fast = math.sqrt(lam_) / 3.0
    worst_end = max(w1 for _, w1 in wins)
    snr_at_end = math.exp(-k_fast * worst_end) / floor
    labels["independent_snr_at_worst_window_end"] = snr_at_end
    check(snr_at_end >= 5.0, FAIL,
          f"ensemble-mean SNR at the latest window end is >=5 (recomputed: {snr_at_end:.1f})",
          findings)
    check(cfg["numerical"]["ac_traj"] > 0 and cfg["numerical"]["ac_lag_max_t"] > 0, FAIL,
          "autocorrelation route (primary estimator) is configured", findings)
    # NON-DEFINITIONAL COVERAGE CHECK (the record's own standing lesson: a gate whose
    # identity is definitional proves nothing).  The controls must actually CALL the
    # primary estimator, not merely have it configured.
    src_c = open(os.path.join(HERE, "q2_controls.py")).read()
    check("Q2.autocorrelation_rate(" in src_c, FAIL,
          "CONTROLS EXERCISE THE PRIMARY ESTIMATOR (autocorrelation_rate is actually called "
          "in the control battery, not merely configured)", findings)
    for cid in ("C3", "C5", "C8", "C10"):
        pass
    check(all(k in src_c for k in ('"PRIMARY_ac_rate_MUST_BE_null"', '"primary_ac_rates"',
                                   '"recovered_PRIMARY_ac_rate"', '"ac_rate": o["ac_rate"]')),
          FAIL, "C3/C5/C8/C10 each report the PRIMARY estimator's result, not only O1b",
          findings)
    check("control_C11_estimator_calibration" in src_c, FAIL,
          "C11 planted-Lambda calibration of the primary estimator exists", findings)
    check(cfg["tolerances"]["tol_rate"] >= 0.20, FAIL,
          f"tol_rate ({cfg['tolerances']['tol_rate']}) is not tighter than the estimator's "
          f"measured precision (~7-11% scatter); a tighter value would make CONVERGED "
          f"unreachable on good data", findings)

    # ---- 2. INDEPENDENT recomputation of the analytic anchors ----------------------
    H = cfg["physical"]["H"]
    D_here = 0.5 * (H / (2.0 * math.pi)) ** 2            # recomputed, not imported
    rate_here = math.sqrt(lam) * H * H / (3.0 * H)        # m_eff^2/(3H) with m_eff^2=sqrt(l)H^2
    labels["independent_D"] = D_here
    labels["independent_expected_rate_from_record_rule"] = rate_here
    labels["independent_target_B_sy_eigenvalue"] = 0.0885 * math.sqrt(lam)
    check(abs(rate_here - 0.1 / 3.0) < 1e-12, FAIL,
          "record-rule rate recomputes to m_eff^2/(3H) = 0.03333H", findings)

    # ---- 3. no-hidden-defaults: instrument must refuse an incomplete config --------
    src = open(os.path.join(HERE, "q2_stochastic_sy.py")).read()
    check("REQUIRED_PHYSICAL" in src and "no defaults exist" in src, FAIL,
          "instrument enforces required config keys with no fallback defaults", findings)
    # precise: no PASS may be EMITTED as a label/status value (mentions in prose are fine)
    import re as _re
    emitted = _re.findall(r'"(?:label|status|verdict)"\s*:\s*"([^"]*)"', src)
    check(not any("PASS" in e.upper() or "FAIL" in e.upper() for e in emitted
                  if e not in ("INVALID_RUN",)), FAIL,
          "instrument emits no PASS/FAIL label value (machine labels only)", findings)
    check("MACHINE_LABELS" in src and "PASS" not in src.split("MACHINE_LABELS")[1][:200],
          FAIL, "the declared machine-label set excludes PASS/FAIL", findings)

    # ---- 3b. NON-CIRCULARITY FIREWALL (the Q2 analogue of Q1's anti-self-certification)
    # Requirement: the primary stochastic dynamics must contain NO parameter, initial
    # condition, analysis window, or observable definition whose value is equivalent to the
    # phenomenon being tested (a generated relaxation rate).
    phys = cfg["physical"]
    check(phys["m2_over_H2"] == 0.0, FAIL,
          "FIREWALL: no mass is supplied to the primary dynamics (m_bare^2 = 0); a nonzero "
          "bare mass would inject the very relaxation being tested", findings)
    targetA = math.sqrt(lam) / 3.0          # record's composition
    targetB = 0.0885 * math.sqrt(lam)       # SY Fokker-Planck eigenvalue
    labels["target_A"] = targetA; labels["target_B"] = targetB
    # FIREWALL-2 (no injected rate).  The dynamics consume exactly {H, m2, lambda, phi0, dt}.
    # Of these only m2 and lambda can set a relaxation rate: m2 is pinned to zero above, and
    # lambda is the free COUPLING of which both targets are FUNCTIONS -- measuring the rate
    # therefore tests that function rather than reading back an input.  (A naive
    # decimal-proximity test was tried first and produced three false positives -- lambda,
    # dt and an inverse window length -- all dimensionally distinct from a rate; it was
    # replaced with the dimension- and mechanism-aware checks below rather than deleted.)
    live_inputs = {k for k in phys if not k.startswith("_")}   # keys beginning "_" are docs
    labels["physical_input_keys"] = sorted(live_inputs)
    check(phys["m2_over_H2"] == 0.0
          and live_inputs == {"H", "m2_over_H2", "lambda_self", "phi0_over_H",
                              "noise_amplitude_rule"}, FAIL,
          "FIREWALL: the physical-input set is exactly {H, m2=0, lambda, phi0, noise-rule} "
          "-- no rate-valued parameter enters the dynamics", findings)
    # FIREWALL-3 (resolution): the integrator must resolve BOTH candidate rates.
    dt = cfg["numerical"]["dt"]
    labels["dt_times_targetA"] = dt * targetA; labels["dt_times_targetB"] = dt * targetB
    check(dt * targetA < 1e-2 and dt * targetB < 1e-2, FAIL,
          f"FIREWALL: timestep resolves both targets (dt*k = {dt*targetA:.1e}, "
          f"{dt*targetB:.1e}; both must be << 1)", findings)
    # FIREWALL-4 (adequacy): each analysis range must span enough decay to constrain a rate,
    # reported per target so a weak range cannot silently masquerade as a measurement.
    efolds = {}
    for w0, w1 in cfg["numerical"]["fit_windows"]:
        efolds[f"O1b_decay_window_ABSOLUTE_TIME[{w0},{w1}]"] = {
            "span": w1 - w0, "efolds_at_A": targetA * (w1 - w0),
            "efolds_at_B": targetB * (w1 - w0)}
    lagmax = cfg["numerical"]["ac_lag_max_t"]
    efolds["O1a_autocorrelation_LAG_range[0,%g]" % lagmax] = {
        "span": lagmax, "efolds_at_A": targetA * lagmax, "efolds_at_B": targetB * lagmax}
    labels["efolds_spanned"] = efolds
    labels["efolds_semantics"] = ("O1a figures are LAG-range x rate in the STATIONARY phase; "
                                  "O1b figures are ABSOLUTE-TIME span x rate in the TRANSIENT "
                                  "phase. They are different coordinates and are never mixed.")
    # COORDINATE-SEMANTICS VERIFICATION: the code's interpretation must equal the prereg's
    src_i = open(os.path.join(HERE, "q2_stochastic_sy.py")).read()
    check(cfg["numerical"]["fit_window_coordinate"] == "ABSOLUTE_TIME", FAIL,
          "prereg declares the O1b fit windows are ABSOLUTE_TIME", findings)
    check(cfg["numerical"]["autocorrelation_lag_coordinate"] == "LAG", FAIL,
          "prereg declares the O1a autocorrelation range is a LAG", findings)
    check('fit_log_rate(r["t"], r["mean"], w0, w1)' in src_i, FAIL,
          "CODE MATCHES PREREG: the decay fit is applied to absolute times r['t'] (not lags, "
          "not post-burn-in-shifted times)", findings)
    check('ac_t0 = ac_start if ac_start is not None else N["burn_in_time"]' in src_i, FAIL,
          "CODE MATCHES PREREG: autocorrelation sampling starts exactly at the declared "
          "burn_in_time", findings)
    check('step * dt >= ac_t0' in src_i, FAIL,
          "CODE MATCHES PREREG: burn-in is applied to the autocorrelation sample collection",
          findings)
    check('stationary_variance(r["t"], r["var"], N["burn_in_fraction"] * N["t_max"])' in src_i
          or 'stationary_variance(r["t"], r["var"], N["burn_in_time"])' in src_i, FAIL,
          "CODE MATCHES PREREG: the stationary-variance observable applies burn-in", findings)
    check(abs(cfg["numerical"]["burn_in_time"]
              - cfg["numerical"]["burn_in_fraction"] * cfg["numerical"]["t_max"]) < 1e-9, FAIL,
          "declared burn_in_time equals burn_in_fraction x t_max (no drift between them)",
          findings)
    # O1b windows are TRANSIENT by design: assert they lie BEFORE burn-in, as declared
    check(all(w1 <= cfg["numerical"]["burn_in_time"] for _, w1 in cfg["numerical"]["fit_windows"]),
          FAIL, "O1b decay windows lie entirely in the transient phase (before burn_in_time) "
          "-- required, because relaxation-from-initial-condition cannot be measured after "
          "the system has relaxed", findings)
    # the autocorrelation must have origin room inside the stationary phase
    origin_span = cfg["numerical"]["t_max"] - cfg["numerical"]["burn_in_time"] - lagmax
    labels["autocorr_origin_span"] = origin_span
    check(origin_span > 0, FAIL,
          f"stationary phase is longer than the lag range (origin span {origin_span:g} > 0)",
          findings)
    ackey = [k for k in efolds if k.startswith("O1a_")][0]
    acA, acB = efolds[ackey]["efolds_at_A"], efolds[ackey]["efolds_at_B"]
    # EFFECTIVE fitted span: the fit keeps lags with tau <= fit_frac*tau_max AND
    # C/C0 > amplitude_cut, so the span actually used is the MIN of the two limits.
    # (A pre-execution audit found the certified figures described the AVAILABLE range,
    # 1.67x wider than any fit uses; the check now certifies what the fit actually spans.)
    ff = cfg["numerical"]["ac_fit_frac"]; cut = cfg["numerical"]["ac_amplitude_cut"]
    eff = {}
    for nm, k in (("A", targetA), ("B", targetB)):
        frac_lim = ff * lagmax
        amp_lim = math.log(1.0 / cut) / k
        e = min(frac_lim, amp_lim)
        eff[nm] = {"tau_fitted_max": e, "efolds": k * e,
                   "limited_by": "amplitude_cut" if amp_lim < frac_lim else "fit_frac"}
    labels["effective_fitted_span"] = eff
    labels["available_lag_range_efolds"] = {"A": acA, "B": acB}
    check(eff["A"]["efolds"] >= 1.0 and eff["B"]["efolds"] >= 1.0, FAIL,
          f"FIREWALL: the PRIMARY estimator's EFFECTIVE FITTED span exceeds 1 e-fold at BOTH "
          f"targets (A {eff['A']['efolds']:.2f} to tau={eff['A']['tau_fitted_max']:.0f} "
          f"[{eff['A']['limited_by']}], B {eff['B']['efolds']:.2f} to "
          f"tau={eff['B']['tau_fitted_max']:.0f} [{eff['B']['limited_by']}]). The AVAILABLE "
          f"lag range spans {acA:.2f}/{acB:.2f} -- that is NOT what the fit uses",
          findings)
    check(all(k in cfg["numerical"] for k in ("ac_fit_frac", "ac_origin_stride",
                                              "ac_amplitude_cut")), FAIL,
          "the three analysis knobs are in the FROZEN CONFIG, not hardcoded Python defaults",
          findings)
    src_k = open(os.path.join(HERE, "q2_stochastic_sy.py")).read()
    check("origin_stride=10, fit_frac=0.6" not in src_k and "c / c0 > 0.05" not in src_k,
          FAIL, "no hardcoded analysis-knob defaults remain in the instrument", findings)
    winA = [v["efolds_at_A"] for k, v in efolds.items() if k.startswith("O1b_")]
    winB = [v["efolds_at_B"] for k, v in efolds.items() if k.startswith("O1b_")]
    check(max(winA) >= 1.0, FAIL,
          f"at least one O1b cross-check window spans >= 1 e-fold at the FASTER target "
          f"(max {max(winA):.2f})", findings)
    check(max(winB) < 1.0, WARN,
          f"DECLARED EXPECTATION: at the SLOWER target the O1b windows span < 1 e-fold "
          f"(max {max(winB):.2f}) -- so if the measured rate is near B, O1b is expected to be "
          f"weak and its window-consistency criterion is INCONCLUSIVE by the frozen gating "
          f"rule, and may not invalidate O1a", findings)
    # FIREWALL-5 (stationarity): burn-in must exceed ~2 relaxation times of the SLOWER target
    burn = cfg["numerical"]["burn_in_fraction"] * cfg["numerical"]["t_max"]
    labels["burnin_in_slow_relaxation_times"] = burn * targetB
    check(burn * targetB >= 2.0, FAIL,
          f"FIREWALL: burn-in is >= 2 relaxation times of the SLOWER target "
          f"({burn*targetB:.2f}) -- the autocorrelation route requires real stationarity",
          findings)
    check(0.1 not in (phys["m2_over_H2"], phys["phi0_over_H"]), FAIL,
          "FIREWALL: the reference value m_eff^2/H^2 = 0.1 is NOT a primary-run input "
          "(it is a comparison target only)", findings)
    sl = cfg["numerical"]["seed_list_explicit"]
    check(sl == [cfg["numerical"]["seed_base"] + i for i in range(cfg["numerical"]["n_seeds"])]
          and len(set(sl)) == len(sl) == cfg["numerical"]["n_seeds"], FAIL,
          f"the five RNG seeds are explicit, distinct, and consistent with seed_base: {sl}",
          findings)
    check("Mersenne" in cfg["numerical"]["rng_implementation"]
          and "random.Random" in cfg["numerical"]["rng_implementation"], FAIL,
          "the RNG implementation is named explicitly for cross-environment reproducibility",
          findings)
    labels["seeds"] = sl
    src_ctl = open(os.path.join(HERE, "q2_stochastic_sy.py")).read()
    check("CONNECTED" in src_ctl and "- ma) * (b[i] - mb)" in src_ctl, FAIL,
          "FIREWALL: the autocorrelation is CONNECTED (mean-subtracted), so an unrelaxed "
          "<phi> cannot bias the fitted rate toward the slower target", findings)
    check("0.0885" in src_ctl and "target_B" in src_ctl, FAIL,
          "FIREWALL: both targets are emitted as ANCHORS, not used as dynamics inputs "
          "(0.0885 appears only in the anchor block)", findings)
    drift_region = src_ctl.split("def evolve_ensemble")[1].split("def ")[0]
    check("0.0885" not in drift_region and "0.1" not in drift_region.replace("0.15", ""),
          FAIL, "FIREWALL: the integrator body contains neither target value nor the "
          "reference m_eff^2 (dynamics are free of the tested phenomenon)", findings)

    # ---- 4. post-execution checks (skipped cleanly if not yet run) -----------------
    if not os.path.exists(res_path):
        findings.append({"status": OK,
                         "check": "results absent -- PRE-EXECUTION audit only (expected in setup)"})
    else:
        R = json.load(open(res_path))
        m = R.get("manifest", {})
        check(m.get("config_sha256") == sha(cfg_path), FAIL,
              "emitted config hash matches the on-disk config (no post-hoc edit)", findings)
        check(m.get("instrument_sha256") == sha(os.path.join(HERE, "q2_stochastic_sy.py")),
              FAIL, "emitted instrument hash matches the on-disk instrument", findings)
        for key in ("analytic_anchors", "runs", "results"):
            check(key in R, FAIL, f"output schema contains '{key}'", findings)
        # independent re-derivation of the seed set actually used
        anch = R.get("analytic_anchors", {})
        check("target_A_naive_meff_over_3H" in anch and "target_B_sy_fp_eigenvalue" in anch,
              FAIL, "BOTH comparison targets were emitted (neither selectable post hoc)",
              findings)
        if "target_A_naive_meff_over_3H" in anch:
            check(abs(anch["target_A_naive_meff_over_3H"] - rate_here) < 1e-12, FAIL,
                  "emitted target A equals the independently recomputed value", findings)
        seeds_used = sorted(p["seed"] for p in R["runs"]["primary"])
        seeds_cfg = sorted(cfg["numerical"]["seed_list_explicit"])
        check(m.get("rng_implementation") == cfg["numerical"]["rng_implementation"], FAIL,
              "emitted RNG implementation matches the frozen declaration", findings)
        check(m.get("seeds_explicit") == cfg["numerical"]["seed_list_explicit"], FAIL,
              "emitted seed list equals the explicit frozen integers", findings)
        check(seeds_used == seeds_cfg, FAIL,
              "seed set used equals the preregistered seed set", findings)
        # the instrument must not have emitted a scientific verdict
        blob = json.dumps(R).lower()
        for forbidden in ("confirmed", "prediction", "success", "verdict: pass"):
            check(forbidden not in blob, FAIL,
                  f"output contains no scientific adjudication token '{forbidden}'", findings)
    if os.path.exists(ctl_path):
        C = json.load(open(ctl_path))
        check(C.get("config_sha256") == sha(cfg_path), FAIL,
              "control battery ran against the same frozen config", findings)
        c3 = C.get("C3", {})
        r3 = c3.get("measured_rate_MUST_BE_null")
        check(r3 is None or abs(r3) <= cfg["tolerances"]["tol_null"], FAIL,
              "C3 NULL control reports no manufactured relaxation (voids primary if it does)",
              findings)

    n_fail = sum(1 for f in findings if f["status"] == FAIL)
    n_warn = sum(1 for f in findings if f["status"] == WARN)
    out = {"auditor": "calc/q2_audit.py (independent; imports no Q2 analysis module)",
           "auditor_sha256": sha(os.path.abspath(__file__)),
           "config_sha256": sha(cfg_path),
           "instrument_sha256": sha(os.path.join(HERE, "q2_stochastic_sy.py")),
           "controls_sha256": sha(os.path.join(HERE, "q2_controls.py")),
           "findings": findings, "n_fail": n_fail, "n_warn": n_warn,
           "independent_values": labels,
           "label": "AUDIT_FAIL" if n_fail else ("AUDIT_WARN" if n_warn else "AUDIT_OK"),
           "note": "machine labels only; scientific adjudication is the owner's"}
    json.dump(out, open(os.path.join(HERE, "RESULTS_q2_audit.json"), "w"), indent=1)
    for f in findings:
        print(f"  [{f['status']}] {f['check']}")
    print(f"[q2-audit] {out['label']}  ({n_fail} fail, {n_warn} warn)")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
