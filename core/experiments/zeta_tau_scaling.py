"""Zeta–Tau Scaling Experiment: tests τ₀ alignment with Riemann zeta zeros."""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class BestMatch:
    """Best matching formula result."""
    family: str
    tau_pred_myr: float
    rel_err: float
    n: int
    m: Optional[int] = None
    p: Optional[float] = None
    gamma_n: Optional[float] = None
    gamma_m: Optional[float] = None


@dataclass
class RobustnessResult:
    """Robustness under H0 perturbation."""
    h0_minus_ok: bool
    h0_plus_ok: bool
    rel_err_minus: float
    rel_err_plus: float


@dataclass
class NullModel:
    """Null model (anti-numerology) results."""
    null_trials: int
    p_value: float
    observed_best_err: float
    null_best_err_median: float
    null_best_err_min: float


def _get_zeta_zeros(N: int) -> np.ndarray:
    """Get first N Riemann zeta zeros (imaginary parts on critical line)."""
    try:
        import mpmath as mp
        mp.dps = 50  # 50 decimal places for precision
        gamma = np.array([float(mp.im(mp.zetazero(i))) for i in range(1, N + 1)], dtype=float)
        return gamma
    except ImportError:
        raise ImportError("mpmath required for zeta_tau_scaling; install with: pip install mpmath")


def _hubble_time_gyr(H0_km_s_Mpc: float) -> float:
    """Compute Hubble time in Gyr from H0 in km/s/Mpc."""
    # H0 [km/s/Mpc] -> H0 [s^-1]
    # 1 Mpc = 3.086e22 m
    # H0_SI = H0_kmsMpc / 3.086e22 [s^-1]
    # t_H = 1 / H0_SI [s]
    # Convert to Gyr: 1 Gyr = 3.154e16 s
    H0_SI = H0_km_s_Mpc / 3.086e22
    t_H_s = 1.0 / H0_SI
    t_H_gyr = t_H_s / 3.154e16
    return t_H_gyr


def _myr_to_gyr(tau_myr: float) -> float:
    """Convert Myr to Gyr."""
    return tau_myr / 1000.0


def _gyr_to_myr(tau_gyr: float) -> float:
    """Convert Gyr to Myr."""
    return tau_gyr * 1000.0


def run_experiment(
    tau0_myr: float,
    H0_km_s_Mpc: float,
    zeros_n: int = 50,
    eps_hit: float = 0.01,
    null_trials: int = 2000,
    h0_perturb_frac: float = 0.02,
    seed: int = 7,
    Omega_m: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Run Zeta–Tau Scaling experiment.

    Returns dict with:
      status: str ("PASS", "WARN", or "FAIL")
      best_match: dict with family, tau_pred_myr, rel_err, etc.
      robustness: dict with H0±perturbation results
      null_model: dict with p_value and null trial stats
      tested_counts: dict with N_zeros, K_hypotheses
      constants: dict with tau0_myr, H0_km_s_Mpc, tH_gyr, etc.
    """
    np.random.seed(seed)

    # 1. Get zeta zeros
    gamma = _get_zeta_zeros(zeros_n)

    # 2. Hubble time
    t_H_gyr = _hubble_time_gyr(H0_km_s_Mpc)
    t_H_myr = _gyr_to_myr(t_H_gyr)

    tau0_gyr = _myr_to_gyr(tau0_myr)

    # 3. Test each mapping family
    candidates: List[BestMatch] = []
    K_hypotheses = 0

    # Family 1: tau_pred = t_H / gamma_n
    for n, gamma_n in enumerate(gamma, start=1):
        tau_pred_gyr = t_H_gyr / gamma_n
        tau_pred_myr = _gyr_to_myr(tau_pred_gyr)
        rel_err = abs(tau0_myr - tau_pred_myr) / tau0_myr
        candidates.append(
            BestMatch(
                family="t_H / gamma_n",
                tau_pred_myr=tau_pred_myr,
                rel_err=rel_err,
                n=n,
                gamma_n=gamma_n,
            )
        )
        K_hypotheses += 1

    # Family 2: tau_pred = t_H / gamma_n^p for p in {1,2,3}
    for p in [1.0, 2.0, 3.0]:
        for n, gamma_n in enumerate(gamma, start=1):
            tau_pred_gyr = t_H_gyr / (gamma_n ** p)
            tau_pred_myr = _gyr_to_myr(tau_pred_gyr)
            rel_err = abs(tau0_myr - tau_pred_myr) / tau0_myr
            candidates.append(
                BestMatch(
                    family=f"t_H / gamma_n^{p}",
                    tau_pred_myr=tau_pred_myr,
                    rel_err=rel_err,
                    n=n,
                    p=p,
                    gamma_n=gamma_n,
                )
            )
            K_hypotheses += 1

    # Family 3: tau_pred = t_H * (2*pi / gamma_n)
    for n, gamma_n in enumerate(gamma, start=1):
        tau_pred_gyr = t_H_gyr * (2.0 * np.pi / gamma_n)
        tau_pred_myr = _gyr_to_myr(tau_pred_gyr)
        rel_err = abs(tau0_myr - tau_pred_myr) / tau0_myr
        candidates.append(
            BestMatch(
                family="t_H * 2π / gamma_n",
                tau_pred_myr=tau_pred_myr,
                rel_err=rel_err,
                n=n,
                gamma_n=gamma_n,
            )
        )
        K_hypotheses += 1

    # Family 4: tau_pred = t_H * (gamma_n / gamma_m) for small m in {1..10}
    M_max = min(10, len(gamma))
    for n, gamma_n in enumerate(gamma, start=1):
        for m in range(1, M_max + 1):
            if m <= len(gamma):
                gamma_m = gamma[m - 1]
                tau_pred_gyr = t_H_gyr * (gamma_n / gamma_m)
                tau_pred_myr = _gyr_to_myr(tau_pred_gyr)
                rel_err = abs(tau0_myr - tau_pred_myr) / tau0_myr
                candidates.append(
                    BestMatch(
                        family="t_H * gamma_n / gamma_m",
                        tau_pred_myr=tau_pred_myr,
                        rel_err=rel_err,
                        n=n,
                        m=m,
                        gamma_n=gamma_n,
                        gamma_m=gamma_m,
                    )
                )
                K_hypotheses += 1

    # Find best match overall
    best = min(candidates, key=lambda x: x.rel_err)
    observed_best_err = best.rel_err

    # 4. Robustness: H0 perturbation
    h0_minus = H0_km_s_Mpc * (1.0 - h0_perturb_frac)
    h0_plus = H0_km_s_Mpc * (1.0 + h0_perturb_frac)

    def best_err_for_H0(H0_test):
        t_H_test_gyr = _hubble_time_gyr(H0_test)
        t_H_test_myr = _gyr_to_myr(t_H_test_gyr)
        min_err = float("inf")
        for cand in candidates:
            if cand.family == best.family:
                if cand.family == "t_H / gamma_n":
                    tau_pred = t_H_test_myr / cand.gamma_n
                    err = abs(tau0_myr - tau_pred) / tau0_myr
                    min_err = min(min_err, err)
                elif cand.family.startswith("t_H / gamma_n^"):
                    p = cand.p
                    tau_pred = t_H_test_myr / (cand.gamma_n ** p)
                    err = abs(tau0_myr - tau_pred) / tau0_myr
                    min_err = min(min_err, err)
                elif cand.family == "t_H * 2π / gamma_n":
                    tau_pred = t_H_test_myr * (2.0 * np.pi / cand.gamma_n)
                    err = abs(tau0_myr - tau_pred) / tau0_myr
                    min_err = min(min_err, err)
                elif cand.family == "t_H * gamma_n / gamma_m":
                    tau_pred = t_H_test_myr * (cand.gamma_n / cand.gamma_m)
                    err = abs(tau0_myr - tau_pred) / tau0_myr
                    min_err = min(min_err, err)
        return min_err

    rel_err_minus = best_err_for_H0(h0_minus)
    rel_err_plus = best_err_for_H0(h0_plus)
    h0_minus_ok = rel_err_minus <= eps_hit
    h0_plus_ok = rel_err_plus <= eps_hit

    robustness = RobustnessResult(
        h0_minus_ok=h0_minus_ok,
        h0_plus_ok=h0_plus_ok,
        rel_err_minus=rel_err_minus,
        rel_err_plus=rel_err_plus,
    )

    # 5. Null model
    null_best_errs: List[float] = []
    gamma_min, gamma_max = float(np.min(gamma)), float(np.max(gamma))

    for trial in range(null_trials):
        gamma_fake = np.random.uniform(gamma_min, gamma_max, len(gamma))
        null_cands: List[float] = []

        # Test the best family's formula with fake gamma
        if best.family == "t_H / gamma_n":
            for g in gamma_fake:
                tau_pred = t_H_myr / g
                err = abs(tau0_myr - tau_pred) / tau0_myr
                null_cands.append(err)
        elif best.family.startswith("t_H / gamma_n^"):
            p = best.p
            for g in gamma_fake:
                tau_pred = t_H_myr / (g ** p)
                err = abs(tau0_myr - tau_pred) / tau0_myr
                null_cands.append(err)
        elif best.family == "t_H * 2π / gamma_n":
            for g in gamma_fake:
                tau_pred = t_H_myr * (2.0 * np.pi / g)
                err = abs(tau0_myr - tau_pred) / tau0_myr
                null_cands.append(err)
        elif best.family == "t_H * gamma_n / gamma_m":
            for n_idx in range(len(gamma_fake)):
                for m_idx in range(min(M_max, len(gamma_fake))):
                    tau_pred = t_H_myr * (gamma_fake[n_idx] / gamma_fake[m_idx])
                    err = abs(tau0_myr - tau_pred) / tau0_myr
                    null_cands.append(err)

        if null_cands:
            null_best_errs.append(min(null_cands))

    null_best_errs_arr = np.array(null_best_errs)
    p_value = float(np.mean(null_best_errs_arr <= observed_best_err))

    null_model = NullModel(
        null_trials=null_trials,
        p_value=p_value,
        observed_best_err=observed_best_err,
        null_best_err_median=float(np.median(null_best_errs_arr)),
        null_best_err_min=float(np.min(null_best_errs_arr)),
    )

    # 6. Status determination
    if observed_best_err <= eps_hit and p_value <= 0.05 and (h0_minus_ok or h0_plus_ok):
        status = "PASS"
    elif observed_best_err <= eps_hit and (p_value > 0.05 or (not h0_minus_ok and not h0_plus_ok)):
        status = "WARN"
    else:
        status = "FAIL"

    # 7. Build result
    return {
        "status": status,
        "best_match": {
            "family": best.family,
            "n": best.n,
            "m": best.m,
            "p": best.p,
            "gamma_n": best.gamma_n,
            "gamma_m": best.gamma_m,
            "tau_pred_myr": float(best.tau_pred_myr),
            "rel_err": float(best.rel_err),
        },
        "robustness": {
            "h0_minus_ok": bool(robustness.h0_minus_ok),
            "h0_plus_ok": bool(robustness.h0_plus_ok),
            "rel_err_minus": float(robustness.rel_err_minus),
            "rel_err_plus": float(robustness.rel_err_plus),
        },
        "null_model": {
            "null_trials": int(null_model.null_trials),
            "p_value": float(null_model.p_value),
            "observed_best_err": float(null_model.observed_best_err),
            "null_best_err_median": float(null_model.null_best_err_median),
            "null_best_err_min": float(null_model.null_best_err_min),
        },
        "tested_counts": {
            "N_zeros": zeros_n,
            "K_hypotheses": K_hypotheses,
        },
        "constants": {
            "tau0_myr": float(tau0_myr),
            "H0_km_s_Mpc": float(H0_km_s_Mpc),
            "tH_gyr": float(t_H_gyr),
            "Omega_m": float(Omega_m or 0.315),
            "eps_hit": float(eps_hit),
            "null_trials": int(null_trials),
            "h0_perturb_frac": float(h0_perturb_frac),
            "seed": int(seed),
        },
    }
