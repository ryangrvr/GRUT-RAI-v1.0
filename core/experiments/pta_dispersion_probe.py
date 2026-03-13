"""PTA dispersion probe (Phase I falsification test).

Assumes n_g(ω) maps to GW propagation for the purpose of a forced falsification test.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from typing import Any, Dict, List

C_M_S = 299_792_458.0
MPC_M = 3.085677581e22
MPC_OVER_C_S = MPC_M / C_M_S
H_EVS = 4.135667696e-15


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _determinism_stamp(inputs: Dict[str, Any], code_version: str, seed: int) -> str:
    payload = {"inputs": inputs, "code_version": code_version, "seed": seed}
    return hashlib.sha256(_canonical_json(payload).encode()).hexdigest()


def _ng2(alpha_scr: float, omega: float, tau0_s: float) -> float:
    x = omega * tau0_s
    return 1.0 + alpha_scr / (1.0 + x * x)


def _dn_domega(alpha_scr: float, omega: float, tau0_s: float, ng2: float) -> float:
    x = omega * tau0_s
    denom = (1.0 + x * x) ** 2
    dng2_domega = alpha_scr * (-2.0 * x) * tau0_s / denom
    return 0.5 * dng2_domega / math.sqrt(ng2)


def _n_minus_1(re_chi: float) -> float:
    # Stable for tiny re_chi: n-1 = re_chi / (1 + sqrt(1+re_chi))
    return re_chi / (1.0 + math.sqrt(1.0 + re_chi))


def run_probe(
    tau0_myr: float,
    alpha_scr: float,
    freqs_hz: List[float],
    use_group_velocity: bool,
    f_hf_hz: float,
    apply_to_gw_propagation: bool,
    seed: int,
    code_version: str,
) -> Dict[str, Any]:
    tau0_s = tau0_myr * 1_000_000 * 365.25 * 24 * 3600
    freqs = [float(f) for f in freqs_hz]

    results: List[Dict[str, float]] = []
    comparisons: List[Dict[str, Any]] = []
    v_phase_over_band: List[float] = []
    delta_v_phase_over_band: List[float] = []
    delta_v_group_over_band: List[float] = []
    for f in freqs:
        omega = 2.0 * math.pi * f
        x = omega * tau0_s
        re_chi = alpha_scr / (1.0 + x * x)
        ng2 = 1.0 + re_chi
        n_minus_1 = _n_minus_1(re_chi)
        n = 1.0 + n_minus_1
        eps_vp = n_minus_1
        vp_over_c = 1.0 / (1.0 + eps_vp)
        dn_domega = _dn_domega(alpha_scr, omega, tau0_s, ng2)
        if use_group_velocity:
            eps_g = n_minus_1 + omega * dn_domega
            vg_over_c = 1.0 / (1.0 + eps_g)
            delta_vg = -eps_g / (1.0 + eps_g)
        else:
            vg_over_c = vp_over_c
            delta_vg = -eps_vp / (1.0 + eps_vp)
        delta_vp = -eps_vp / (1.0 + eps_vp)
        v_phase_over_c = vp_over_c
        delta_v_phase = delta_vp
        delay_s_per_mpc = -MPC_OVER_C_S * delta_vg
        delay_sign = "advance" if delay_s_per_mpc < 0 else "delay"

        one_minus_vg = -delta_vg
        mg_equiv_abs_eV = H_EVS * f * math.sqrt(2.0 * abs(one_minus_vg))
        mg_equiv_sign = "tachyonic_like" if one_minus_vg < 0 else "massive_like"
        mg_margin = (8.2e-24 / mg_equiv_abs_eV) if mg_equiv_abs_eV > 0 else 1.0e99
        mg_mapping_mode = "magnitude_proxy_only" if delta_vg > 0 else "like_for_like"

        v_phase_over_band.append(v_phase_over_c)
        delta_v_phase_over_band.append(delta_v_phase)
        delta_v_group_over_band.append(delta_vg)

        results.append(
            {
                "f_hz": f,
                "omega_rad_s": omega,
                "x": x,
                "ReChi": re_chi,
                "ng2": ng2,
                "n": n,
                "n_minus_1": n_minus_1,
                "vp_over_c": vp_over_c,
                "vg_over_c": vg_over_c,
                "v_phase_over_c": v_phase_over_c,
                "vp_minus_1": delta_vp,
                "vg_minus_1": delta_vg,
                "delta_v_phase": delta_v_phase,
                "n_sci": f"{n:.6e}",
                "ng2_sci": f"{ng2:.6e}",
                "vp_over_c_sci": f"{vp_over_c:.6e}",
                "vg_over_c_sci": f"{vg_over_c:.6e}",
                "delta_vp": delta_vp,
                "delta_vg": delta_vg,
                "delay_s_per_Mpc": delay_s_per_mpc,
                "delay_sign": delay_sign,
            }
        )

        comparisons.append(
            {
                "delta_vg": delta_vg,
                "delta_vp": delta_vp,
                "mg_equiv_abs_eV": mg_equiv_abs_eV,
                "mg_equiv_sign": mg_equiv_sign,
                "mg_mapping_mode": mg_mapping_mode,
                "mg_limit_eV": 8.2e-24,
                "mg_margin": mg_margin,
                "mg_exclusion_flag": "EXCLUDED_BY_PTA_MG_PROXY"
                if (mg_equiv_sign == "massive_like" and mg_equiv_abs_eV > 8.2e-24)
                else "NOT_EXCLUDED_BY_PTA_MG_PROXY",
                "hf_sanity_flag": "PASS",
            }
        )

    limits = [
        {
            "name": "NANOGrav 15-year PTA phase-speed lower bound",
            "value": 0.87,
            "units": "v_over_c",
            "bound_type": "lower",
            "citation": "DOI:10.1103/PhysRevD.109.L061101; arXiv:2310.08366",
            "applicability_note": "Phase-speed lower bound from PTA ORF analysis; posterior flattens for v>c, bound uses pragmatic 1/e^2 (~2σ) width on subluminal side.",
        },
        {
            "name": "GW170817 speed bound (~100 Hz)",
            "value": None,
            "value_low": -3.0e-15,
            "value_high": 7.0e-16,
            "units": "(v_g-c)/c",
            "citation": "arXiv:1710.05834",
            "applicability_note": "HF sanity check only (~100 Hz).",
        },
        {
            "name": "NANOGrav 15-year graviton mass bound (95% CL)",
            "value": 8.2e-24,
            "units": "eV",
            "citation": "arXiv:2310.07469",
            "applicability_note": "Magnitude-only proxy via mg_equiv_abs_eV mapping; sign noted.",
        },
        {
            "name": "PTA graviton-mass constraints (context)",
            "value": None,
            "units": "eV",
            "citation": "arXiv:2302.11796",
            "applicability_note": "Reference only; not a direct like-for-like bound in this parametrization.",
        },
    ]

    # HF sanity check at f_hf_hz
    omega_hf = 2.0 * math.pi * float(f_hf_hz)
    x_hf = omega_hf * tau0_s
    re_chi_hf = alpha_scr / (1.0 + x_hf * x_hf)
    ng2_hf = 1.0 + re_chi_hf
    n_hf = 1.0 + _n_minus_1(re_chi_hf)
    dn_domega_hf = _dn_domega(alpha_scr, omega_hf, tau0_s, ng2_hf)
    eps_g_hf = _n_minus_1(re_chi_hf) + omega_hf * dn_domega_hf
    vg_over_c_hf = 1.0 / (1.0 + eps_g_hf)
    delta_vg_hf = -eps_g_hf / (1.0 + eps_g_hf)
    hf_limit = next((limit for limit in limits if "GW170817" in limit.get("name", "")), None)
    hf_low = hf_limit.get("value_low") if hf_limit else -3.0e-15
    hf_high = hf_limit.get("value_high") if hf_limit else 7.0e-16
    hf_sanity_ok = hf_low <= delta_vg_hf <= hf_high

    hf_check = {
        "f_hz": float(f_hf_hz),
        "omega_rad_s": omega_hf,
        "x": x_hf,
        "ReChi": re_chi_hf,
        "ng2": ng2_hf,
        "n": n_hf,
        "delta_vg": delta_vg_hf,
        "pass_flag": "PASS" if hf_sanity_ok else "FAIL",
    }

    for row in comparisons:
        row["hf_sanity_flag"] = "PASS" if hf_sanity_ok else "FAIL"

    min_v_phase_over_c_over_band = min(v_phase_over_band)
    worst_speed_margin_over_band = min_v_phase_over_c_over_band - 0.87
    worst_idx = v_phase_over_band.index(min_v_phase_over_c_over_band)
    worst_freq_hz = freqs[worst_idx]
    max_abs_delta_v_phase_over_c_over_band = max(abs(x) for x in delta_v_phase_over_band)
    max_abs_delta_v_group_over_c_over_band = max(abs(x) for x in delta_v_group_over_band)

    pta_direct_dispersion_bound_present = True
    exclusion_basis = None
    worst_margin_over_band = min(row["mg_margin"] for row in comparisons)
    status = "PASS_NOT_EXCLUDED"
    if not apply_to_gw_propagation:
        status = "NOT_APPLICABLE"
    elif min_v_phase_over_c_over_band < 0.87:
        status = "EXCLUDED_BY_PTA_SPEED"
        exclusion_basis = "PTA_SPEED_GATE"
    elif not hf_sanity_ok:
        status = "FAIL_HF_SANITY"
    elif any(c["mg_exclusion_flag"] == "EXCLUDED_BY_PTA_MG_PROXY" for c in comparisons):
        status = "EXCLUDED_BY_PTA_MG_PROXY"
        exclusion_basis = "MG_PROXY_ONLY"
    else:
        exclusion_basis = "PTA_SPEED_GATE_PRIMARY"

    assumptions = [
        "Assume n_g(ω) applies to GW propagation (forced test).",
        "Use n_g^2(ω) = 1 + α_scr / (1 + (ω τ0)^2).",
        "Group velocity computed as v_g/c = 1 / ( n + ω dn/dω ).",
        "Baseline-defined H0 is not predicted; τΛ is not inferred here.",
        "Mapping to graviton mass is a proxy; sign mismatch (tachyonic_like) is not a strict exclusion.",
    ]
    if not apply_to_gw_propagation:
        assumptions.append("apply_to_gw_propagation=false: return NOT_APPLICABLE; no exclusions applied.")

    conclusion = (
        "This test assumes n_g(ω) applies to GW propagation. If GRUT defines n_g(ω) as a *field-response index only* "
        "(not wave propagation), then the correct output is ‘NOT_APPLICABLE’ and the theory must provide the propagation "
        "law to be testable."
    )
    conclusion += " PTA phase-speed lower bound is applied as the primary gate; MG proxy is secondary and magnitude-only when superluminal."

    determinism_inputs = {
        "tau0_myr": tau0_myr,
        "alpha_scr": alpha_scr,
        "freqs_hz": freqs,
        "use_group_velocity": use_group_velocity,
        "f_hf_hz": float(f_hf_hz),
        "apply_to_gw_propagation": bool(apply_to_gw_propagation),
        "status": status,
        "min_v_phase_over_c_over_band": min_v_phase_over_c_over_band,
        "max_abs_delta_v_phase_over_c_over_band": max_abs_delta_v_phase_over_c_over_band,
        "max_abs_delta_v_group_over_c_over_band": max_abs_delta_v_group_over_c_over_band,
        "worst_speed_margin_over_band": worst_speed_margin_over_band,
        "worst_freq_hz": worst_freq_hz,
        "worst_margin_over_band": worst_margin_over_band,
    }
    stamp = _determinism_stamp(determinism_inputs, code_version, seed)

    return {
        "run_id": stamp[:16],
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
        "min_v_phase_over_c_over_band": min_v_phase_over_c_over_band,
        "max_abs_delta_v_phase_over_c_over_band": max_abs_delta_v_phase_over_c_over_band,
        "max_abs_delta_v_group_over_c_over_band": max_abs_delta_v_group_over_c_over_band,
        "worst_speed_margin_over_band": worst_speed_margin_over_band,
        "worst_freq_hz": worst_freq_hz,
        "assumptions": assumptions,
        "results": results,
        "comparisons": comparisons,
        "hf_check_100Hz": hf_check,
        "cited_limits": limits,
        "conclusion": conclusion,
        "pta_direct_dispersion_bound_present": pta_direct_dispersion_bound_present,
        "exclusion_basis": exclusion_basis,
        "worst_margin_over_band": worst_margin_over_band,
        "determinism_stamp": stamp,
    }
