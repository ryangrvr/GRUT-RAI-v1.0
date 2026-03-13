from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np


_FIELD_ALIASES = {
    "r_kpc": {"r_kpc", "r", "radius", "radius_kpc", "r_kpc_median"},
    "v_obs": {"v_obs", "v", "vrot", "v_rot", "v_circ", "v_obs_kms"},
    "v_err": {"v_err", "v_sigma", "v_unc", "v_err_kms", "sigma_v"},
    "v_gas": {"v_gas", "vgas", "v_gas_kms"},
    "v_star": {"v_star", "vstars", "v_star_kms"},
    "v_bulge": {"v_bulge", "vbulge", "v_bulge_kms"},
}


def _normalize_fields(raw: Dict[str, Any]) -> Tuple[Dict[str, np.ndarray], Dict[str, str]]:
    field_map: Dict[str, str] = {}
    normalized: Dict[str, np.ndarray] = {}

    for target, aliases in _FIELD_ALIASES.items():
        match = None
        for key in raw.keys():
            if key in aliases:
                match = key
                break
        if match is not None:
            field_map[target] = match
            normalized[target] = np.array(raw[match], dtype=float)

    missing = [k for k in ("r_kpc", "v_obs") if k not in normalized]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    return normalized, field_map


def load_rotation_data(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    raw: Dict[str, Any]

    if p.suffix == ".npy":
        data = np.load(p, allow_pickle=True)
        if isinstance(data, np.lib.npyio.NpzFile):
            raw = {k: np.array(data[k], dtype=float) for k in data.files}
        elif isinstance(data.item(0), dict):  # type: ignore[arg-type]
            d = data.item()
            raw = {k: np.array(v, dtype=float) for k, v in d.items()}
        else:
            arr = np.array(data, dtype=float)
            if arr.ndim != 2 or arr.shape[1] < 2:
                raise ValueError("npy must be 2D with >=2 columns")
            keys = ["r_kpc", "v_obs", "v_err", "v_gas", "v_star", "v_bulge"]
            raw = {k: arr[:, i] for i, k in enumerate(keys[: arr.shape[1]])}
    elif p.suffix == ".json":
        payload = json.loads(p.read_text())
        if isinstance(payload, dict):
            raw = payload
        elif isinstance(payload, list):
            raw = {}
            for row in payload:
                if not isinstance(row, dict):
                    continue
                for key, value in row.items():
                    raw.setdefault(key, []).append(value)
        else:
            raise ValueError("json must be dict or list")
    elif p.suffix == ".csv":
        arr = np.genfromtxt(p, delimiter=",", names=True, dtype=None, encoding="utf-8")
        raw = {name: np.array(arr[name], dtype=float) for name in arr.dtype.names}
    else:
        raise ValueError("Unsupported data format; use csv/json/npy")

    normalized, field_map = _normalize_fields(raw)
    normalized["field_map"] = field_map
    return normalized


def compute_v_bar(
    v_gas: np.ndarray,
    v_star: np.ndarray,
    v_bulge: Optional[np.ndarray] = None,
    ups_star: float = 1.0,
    ups_bulge: float = 1.0,
) -> np.ndarray:
    v_star_scaled = float(ups_star) * v_star
    terms = v_gas**2 + v_star_scaled**2
    if v_bulge is not None:
        terms += (float(ups_bulge) * v_bulge) ** 2
    return np.sqrt(terms)


def compute_v_grut(
    v_bar: np.ndarray,
    r_kpc: np.ndarray,
    response_model: str = "identity",
    alpha_mem: float = 0.333333333,
    r0_policy: str = "median_radius",
    r0_kpc: Optional[float] = None,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    response_model = response_model.lower().strip()
    r0_policy = r0_policy.lower().strip()
    meta: Dict[str, Any] = {
        "response_model": response_model,
        "alpha_mem": float(alpha_mem),
        "r0_policy": r0_policy,
        "r0_kpc": float(r0_kpc) if r0_kpc is not None else None,
    }

    if response_model == "identity":
        return v_bar, meta

    if response_model == "radial_gate_v0":
        if r0_policy == "median_radius":
            r0 = float(np.median(r_kpc))
        elif r0_policy == "fixed_kpc":
            if r0_kpc is None:
                raise ValueError("r0_kpc is required when r0_policy=fixed_kpc")
            r0 = float(r0_kpc)
        else:
            raise ValueError(f"Unknown r0_policy: {r0_policy}")
        gate = 1.0 + float(alpha_mem) / (1.0 + (r_kpc / r0) ** 2)
        v_eff2 = (v_bar**2) * gate
        meta["r0_kpc"] = r0
        return np.sqrt(v_eff2), meta

    if response_model == "memory_scale_boost_v0":
        if r0_policy == "median_radius":
            r0 = float(np.median(r_kpc))
        elif r0_policy == "fixed_kpc":
            if r0_kpc is None:
                raise ValueError("r0_kpc is required when r0_policy=fixed_kpc")
            r0 = float(r0_kpc)
        else:
            raise ValueError(f"Unknown r0_policy: {r0_policy}")
        v_bar_max2 = float(np.max(v_bar) ** 2)
        v_eff2 = (v_bar**2) + (float(alpha_mem) * v_bar_max2) / (1.0 + (r_kpc / r0) ** 2)
        meta["r0_kpc"] = r0
        return np.sqrt(v_eff2), meta

    raise ValueError(f"Unknown response_model: {response_model}")


def residual_metrics(
    v_obs: np.ndarray,
    v_model: np.ndarray,
    v_err: Optional[np.ndarray] = None,
    r_kpc: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    residuals = v_obs - v_model
    rms = float(np.sqrt(np.mean(residuals**2)))
    mean_abs = float(np.mean(np.abs(residuals)))
    mean_abs_frac = float(np.mean(np.abs(residuals) / np.clip(np.abs(v_obs), 1e-9, None)))
    chi_like = None
    if v_err is not None and np.all(np.isfinite(v_err)):
        chi_like = float(np.mean((residuals / np.clip(v_err, 1e-9, None)) ** 2))

    inner_rms = float("nan")
    outer_rms = float("nan")
    if r_kpc is not None:
        r_med = float(np.median(r_kpc))
        inner_mask = r_kpc <= r_med
        outer_mask = r_kpc > r_med
        if np.any(inner_mask):
            inner_rms = float(np.sqrt(np.mean(residuals[inner_mask] ** 2)))
        if np.any(outer_mask):
            outer_rms = float(np.sqrt(np.mean(residuals[outer_mask] ** 2)))

    return {
        "rms_residual": rms,
        "mean_abs_residual": mean_abs,
        "mean_abs_frac_residual": mean_abs_frac,
        "chi_like": chi_like,
        "inner_disk_rms": inner_rms,
        "outer_disk_rms": outer_rms,
    }


def fit_log_slope(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    if x.size < 2:
        raise ValueError("Need at least two points for slope fit")
    if np.any(x <= 0) or np.any(y <= 0):
        raise ValueError("log fit requires positive x and y")
    logx = np.log10(x)
    logy = np.log10(y)
    slope, intercept = np.polyfit(logx, logy, 1)
    return float(slope), float(intercept)
