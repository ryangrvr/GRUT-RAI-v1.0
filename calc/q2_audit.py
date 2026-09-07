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
        efolds[f"win[{w0},{w1}]"] = {"A": targetA * (w1 - w0), "B": targetB * (w1 - w0)}
    lagmax = cfg["numerical"]["ac_lag_max_t"]
    efolds["autocorr_lags"] = {"A": targetA * lagmax, "B": targetB * lagmax}
    labels["efolds_spanned"] = efolds
    check(efolds["autocorr_lags"]["A"] >= 1.0 and efolds["autocorr_lags"]["B"] >= 1.0, FAIL,
          "FIREWALL: the PRIMARY (autocorrelation) range spans >= 1 e-fold at BOTH targets "
          f"(A {efolds['autocorr_lags']['A']:.1f}, B {efolds['autocorr_lags']['B']:.2f})",
          findings)
    check(max(v["A"] for k, v in efolds.items() if k.startswith("win")) >= 1.0, FAIL,
          "FIREWALL: at least one cross-check window spans >= 1 e-fold at the faster target",
          findings)
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
        seeds_cfg = sorted(cfg["numerical"]["seed_base"] + i
                           for i in range(cfg["numerical"]["n_seeds"]))
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
