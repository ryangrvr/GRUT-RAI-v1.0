from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional, Tuple

from grut.conversion import find_z0_index


def _is_finite(x: Optional[float]) -> bool:
    return x is not None and math.isfinite(float(x))


def interpolate_linear(x_vals: Iterable[float], y_vals: Iterable[Optional[float]], xq: float) -> Optional[float]:
    xs = list(x_vals)
    ys = list(y_vals)
    if len(xs) != len(ys) or not xs:
        return None
    pairs = sorted(zip(xs, ys), key=lambda t: t[0])
    xs_sorted = [p[0] for p in pairs]
    ys_sorted = [p[1] for p in pairs]
    if xq < xs_sorted[0] or xq > xs_sorted[-1]:
        return None
    for i in range(len(xs_sorted) - 1):
        x0 = xs_sorted[i]
        x1 = xs_sorted[i + 1]
        if x0 <= xq <= x1:
            y0 = ys_sorted[i]
            y1 = ys_sorted[i + 1]
            if not _is_finite(y0) or not _is_finite(y1):
                return None
            if x1 == x0:
                return float(y0)
            t = (xq - x0) / (x1 - x0)
            return float(y0) + t * (float(y1) - float(y0))
    return None


def compute_residuals_vs_lcdm(
    *,
    z_vals: Iterable[float],
    E_grut: Iterable[Optional[float]],
    E_lcdm: Iterable[float],
    start_z: float,
    valid_z_max: Optional[float] = None,
) -> Dict[str, Any]:
    z_list = list(z_vals)
    e_grut_list = list(E_grut)
    e_lcdm_list = list(E_lcdm)
    diffs: List[float] = []
    compare_mask: List[bool] = []
    for z, eg, el in zip(z_list, e_grut_list, e_lcdm_list):
        in_range = 0.0 <= z <= float(start_z)
        if valid_z_max is not None:
            in_range = in_range and (z <= float(valid_z_max))
        ok = in_range and _is_finite(eg)
        compare_mask.append(ok)
        if ok:
            diffs.append(float(eg) - float(el))
    if diffs:
        rms = math.sqrt(sum(d * d for d in diffs) / len(diffs))
        max_abs = max(abs(d) for d in diffs)
    else:
        rms = None
        max_abs = None
    return {
        "compare_count": len(diffs),
        "rms_E_vs_lcdm": rms,
        "max_abs_E_diff": max_abs,
        "compare_mask": compare_mask,
        "start_z": float(start_z),
        "valid_z_max": float(valid_z_max) if valid_z_max is not None else None,
    }


def _select_href(
    z_obs: List[float],
    Hz_obs: List[float],
    sigma_obs: List[float],
    policy: str,
) -> Tuple[Optional[Tuple[int, float, float, float]], Dict[str, Any]]:
    candidates = []
    for idx, (z_i, h_i, s_i) in enumerate(zip(z_obs, Hz_obs, sigma_obs)):
        if not _is_finite(h_i) or not _is_finite(s_i) or float(s_i) <= 0.0:
            continue
        candidates.append((idx, float(z_i), float(h_i), float(s_i)))
    if not candidates:
        return None, {"policy": policy, "status": "no_valid_points"}

    policy = policy.strip().lower()
    if policy == "median_lowz":
        lowz = [c for c in candidates if c[1] <= 0.1]
        if not lowz:
            lowz = candidates
        lowz_sorted = sorted(lowz, key=lambda x: x[2])
        mid = len(lowz_sorted) // 2
        chosen = lowz_sorted[mid]
        meta = {
            "policy": "median_lowz",
            "status": "ok",
            "z_max": 0.1,
            "n_lowz": len(lowz),
        }
        return chosen, meta

    candidates.sort(key=lambda x: x[1])
    return candidates[0], {"policy": "lowest_z", "status": "ok"}


def _finalize_stats(residuals: List[float], abs_vals: List[float]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    if not residuals:
        return None, None, None
    chi2 = sum(r * r for r in residuals)
    rms_sigma = math.sqrt(sum(r * r for r in residuals) / len(residuals))
    rms_abs = math.sqrt(sum(d * d for d in abs_vals) / len(abs_vals)) if abs_vals else None
    return chi2, rms_sigma, rms_abs


def compute_residuals_vs_data(
    *,
    z_obs: Iterable[float],
    Hz_obs: Iterable[float],
    sigma_obs: Iterable[float],
    tracer: Optional[Iterable[str]] = None,
    z_model: Iterable[float],
    E_grut: Iterable[Optional[float]],
    H0_phys: float,
    Eobs_anchor_policy: str,
    start_z: float,
    valid_z_max: Optional[float] = None,
) -> Dict[str, Any]:
    z_obs_list = list(z_obs)
    hz_obs_list = list(Hz_obs)
    sig_list = list(sigma_obs)
    tracer_list = list(tracer) if tracer is not None else ["unknown"] * len(z_obs_list)

    href, href_meta = _select_href(z_obs_list, hz_obs_list, sig_list, Eobs_anchor_policy)
    if href is not None:
        href_meta = {
            **href_meta,
            "idx": href[0],
            "z_ref": href[1],
            "Hz_ref": href[2],
            "sigma_ref": href[3],
        }

    residuals: List[Dict[str, Any]] = []
    residual_vals: List[float] = []
    abs_vals: List[float] = []
    residuals_E: List[Dict[str, Any]] = []
    residual_vals_E: List[float] = []
    abs_vals_E: List[float] = []

    by_tracer: Dict[str, Dict[str, List[float]]] = {}
    by_tracer_E: Dict[str, Dict[str, List[float]]] = {}

    exclusions_H = {"outside_z_window": 0, "out_of_domain": 0, "missing_sigma": 0, "interp_failed": 0}
    exclusions_E = {"outside_z_window": 0, "out_of_domain": 0, "missing_sigma": 0, "interp_failed": 0, "missing_href": 0}

    for z_i, h_i, s_i, tracer_i in zip(z_obs_list, hz_obs_list, sig_list, tracer_list):
        if z_i < 0.0 or z_i > float(start_z):
            exclusions_H["outside_z_window"] += 1
            exclusions_E["outside_z_window"] += 1
            continue
        if valid_z_max is not None and z_i > float(valid_z_max):
            exclusions_H["out_of_domain"] += 1
            exclusions_E["out_of_domain"] += 1
            continue
        if not _is_finite(s_i) or float(s_i) <= 0.0:
            exclusions_H["missing_sigma"] += 1
            exclusions_E["missing_sigma"] += 1
            continue
        e_interp = interpolate_linear(z_model, E_grut, z_i)
        if e_interp is None or not _is_finite(e_interp):
            exclusions_H["interp_failed"] += 1
            exclusions_E["interp_failed"] += 1
            continue

        h_model = float(e_interp) * float(H0_phys)
        denom = float(s_i) if float(s_i) != 0.0 else 1e-30
        resid = (h_model - float(h_i)) / denom
        residual_vals.append(resid)
        abs_vals.append(h_model - float(h_i))
        residuals.append(
            {
                "z": float(z_i),
                "Hz_model": h_model,
                "Hz_obs": float(h_i),
                "sigma": float(s_i),
                "residual_sigma": resid,
                "tracer": tracer_i,
            }
        )
        tracer_key = tracer_i or "unknown"
        by_tracer.setdefault(tracer_key, {"residuals": [], "abs": []})
        by_tracer[tracer_key]["residuals"].append(resid)
        by_tracer[tracer_key]["abs"].append(h_model - float(h_i))

        if href is None:
            exclusions_E["missing_href"] += 1
            continue
        _, _, h_ref, s_ref = href
        if h_ref == 0.0:
            exclusions_E["missing_href"] += 1
            continue
        e_obs = float(h_i) / float(h_ref)
        if not _is_finite(e_obs):
            exclusions_E["missing_href"] += 1
            continue
        sigma_E = abs(e_obs) * math.sqrt(
            (float(s_i) / max(abs(float(h_i)), 1e-30)) ** 2 + (float(s_ref) / max(abs(float(h_ref)), 1e-30)) ** 2
        )
        if not _is_finite(sigma_E) or sigma_E == 0.0:
            exclusions_E["missing_sigma"] += 1
            continue
        resid_E = (float(e_interp) - e_obs) / sigma_E
        residual_vals_E.append(resid_E)
        abs_vals_E.append(float(e_interp) - e_obs)
        residuals_E.append(
            {
                "z": float(z_i),
                "E_model": float(e_interp),
                "E_obs": e_obs,
                "sigma_E": sigma_E,
                "residual_sigma": resid_E,
                "tracer": tracer_i,
            }
        )
        by_tracer_E.setdefault(tracer_key, {"residuals": [], "abs": []})
        by_tracer_E[tracer_key]["residuals"].append(resid_E)
        by_tracer_E[tracer_key]["abs"].append(float(e_interp) - e_obs)

    chi2, rms_sigma, rms_km_s_Mpc = _finalize_stats(residual_vals, abs_vals)
    chi2_E, rms_sigma_E, rms_E = _finalize_stats(residual_vals_E, abs_vals_E)

    def _tracer_block(stats: Dict[str, Dict[str, List[float]]]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for key, vals in stats.items():
            chi2_t, rms_sigma_t, rms_abs_t = _finalize_stats(vals["residuals"], vals["abs"])
            out[key] = {
                "n_points": len(vals["residuals"]),
                "chi2": chi2_t,
                "rms_sigma": rms_sigma_t,
                "rms_abs": rms_abs_t,
            }
        return out

    top_k = 5
    worst_H = sorted(residuals, key=lambda r: abs(float(r.get("residual_sigma", 0.0))), reverse=True)[:top_k]
    worst_E = sorted(residuals_E, key=lambda r: abs(float(r.get("residual_sigma", 0.0))), reverse=True)[:top_k]

    return {
        "compare_count": len(residual_vals),
        "chi2": chi2,
        "rms_sigma": rms_sigma,
        "rms_km_s_Mpc": rms_km_s_Mpc,
        "residuals": residuals,
        "compare_report": {
            "n_points_total": len(z_obs_list),
            "n_points_used": len(residual_vals),
            "exclusions": exclusions_H,
        },
        "by_tracer": _tracer_block(by_tracer),
        "E_obs_policy": href_meta,
        "compare_count_E": len(residual_vals_E),
        "chi2_E": chi2_E,
        "rms_sigma_E": rms_sigma_E,
        "rms_E": rms_E,
        "residuals_E": residuals_E,
        "compare_report_E": {
            "n_points_total": len(z_obs_list),
            "n_points_used": len(residual_vals_E),
            "exclusions": exclusions_E,
        },
        "by_tracer_E": _tracer_block(by_tracer_E),
        "top_k_worst_points_H": worst_H,
        "top_k_worst_points_E": worst_E,
        "start_z": float(start_z),
        "valid_z_max": float(valid_z_max) if valid_z_max is not None else None,
    }


def build_growth_sidecar(outputs: Dict[str, Any]) -> Dict[str, Any]:
    fs8 = outputs.get("OBS_FS8_001") if outputs else None
    if not fs8:
        return {
            "fs8_present": False,
            "fs8_z0": None,
            "compare_point_count": 0,
            "rms_fs8_vs_lcdm_stub": None,
        }
    z_vals = list(fs8.get("z", []))
    fs8_vals = list(fs8.get("fsigma8", []))
    compare_mask = list(fs8.get("compare_mask", []))
    if not compare_mask:
        compare_mask = [False] * len(z_vals)
    idx0 = find_z0_index(z_vals)
    fs8_z0 = None
    if idx0 is not None and idx0 < len(fs8_vals):
        fs8_z0 = fs8_vals[idx0]
    compare_count = sum(1 for m in compare_mask if m)
    return {
        "fs8_present": True,
        "fs8_z0": fs8_z0,
        "compare_point_count": compare_count,
        "rms_fs8_vs_lcdm_stub": None,
    }


def build_point_residuals(
    *,
    z_obs: Iterable[float],
    Hz_obs: Iterable[float],
    sigma_obs: Iterable[float],
    tracer: Iterable[str],
    z_model: Iterable[float],
    E_grut: Iterable[Optional[float]],
    anchors: Dict[str, float],
    Eobs_anchor_policy: str,
    start_z: float,
    valid_z_max: Optional[float] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    z_obs_list = list(z_obs)
    hz_obs_list = list(Hz_obs)
    sig_list = list(sigma_obs)
    tracer_list = list(tracer)

    href, href_meta = _select_href(z_obs_list, hz_obs_list, sig_list, Eobs_anchor_policy)
    if href is not None:
        href_meta = {
            **href_meta,
            "idx": href[0],
            "z_ref": href[1],
            "Hz_ref": href[2],
            "sigma_ref": href[3],
        }

    rows: List[Dict[str, Any]] = []
    for z_i, h_i, s_i, tracer_i in zip(z_obs_list, hz_obs_list, sig_list, tracer_list):
        row: Dict[str, Any] = {
            "z": float(z_i),
            "tracer": tracer_i,
            "Hz_obs": float(h_i),
            "sigma_Hz": float(s_i),
            "E_obs": None,
            "sigma_E": None,
            "E_model": None,
            "resid_sigma_E": None,
            "exclude_reason_H": "",
            "exclude_reason_E": "",
        }

        if z_i < 0.0 or z_i > float(start_z):
            row["exclude_reason_H"] = "outside_z_window"
            row["exclude_reason_E"] = "outside_z_window"
            rows.append(row)
            continue
        if valid_z_max is not None and z_i > float(valid_z_max):
            row["exclude_reason_H"] = "out_of_domain"
            row["exclude_reason_E"] = "out_of_domain"
            rows.append(row)
            continue
        if not _is_finite(s_i) or float(s_i) <= 0.0:
            row["exclude_reason_H"] = "missing_sigma"
            row["exclude_reason_E"] = "missing_sigma"
            rows.append(row)
            continue

        e_interp = interpolate_linear(z_model, E_grut, z_i)
        if e_interp is None or not _is_finite(e_interp):
            row["exclude_reason_H"] = "interp_failed"
            row["exclude_reason_E"] = "interp_failed"
            rows.append(row)
            continue

        row["E_model"] = float(e_interp)
        for anchor_name, H0_phys in anchors.items():
            h_model = float(e_interp) * float(H0_phys)
            resid = (h_model - float(h_i)) / max(float(s_i), 1e-30)
            row[f"Hz_model_{anchor_name}"] = h_model
            row[f"resid_sigma_H_{anchor_name}"] = resid

        if href is None or href[2] == 0.0:
            row["exclude_reason_E"] = "missing_href"
            rows.append(row)
            continue
        _, _, h_ref, s_ref = href
        e_obs = float(h_i) / float(h_ref)
        if not _is_finite(e_obs):
            row["exclude_reason_E"] = "missing_href"
            rows.append(row)
            continue
        sigma_E = abs(e_obs) * math.sqrt(
            (float(s_i) / max(abs(float(h_i)), 1e-30)) ** 2 + (float(s_ref) / max(abs(float(h_ref)), 1e-30)) ** 2
        )
        if not _is_finite(sigma_E) or sigma_E == 0.0:
            row["exclude_reason_E"] = "missing_sigma"
            rows.append(row)
            continue
        row["E_obs"] = e_obs
        row["sigma_E"] = sigma_E
        row["resid_sigma_E"] = (float(e_interp) - e_obs) / sigma_E
        rows.append(row)

    return rows, href_meta
