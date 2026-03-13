from __future__ import annotations

from typing import Tuple, Dict, Any, Optional
import numpy as np

from .constants import GRUTParams
from .schemas import EngineInput
from .hz_models import hz_lcdm_flat, H0_SI, omega_m_z
from .operators import tau_eff_seconds, S_phase, L_stiff, smooth_min, phi_z

MYR_IN_S = 1_000_000 * 365.25 * 24 * 3600


def _observer_dissipation_multiplier(
    obs_mod: Optional[Dict[str, Any]],
    params: GRUTParams,
) -> Tuple[float, Dict[str, Any]]:
    """Observer→dissipation coupling (Phase D).

    This is intentionally limited:
      - does NOT change CFL gating
      - does NOT change g_raw/g_cap/tau_eff
      - only scales D(z) by a bounded multiplier based on engagement ΔS
    """
    if not obs_mod or not bool(obs_mod.get("enabled", False)):
        return 1.0, {"enabled": False, "lambda": 0.0, "deltaS": 0.0, "multiplier": 1.0}

    deltaS = float(obs_mod.get("deltaS", 0.0))
    lam = float(obs_mod.get("lambda", params.info_coupling_lambda))
    # Linear, bounded coupling: D := D * (1 + λ·ΔS)
    raw = 1.0 + lam * deltaS
    mult = float(np.clip(raw, 0.5, 3.0))
    return mult, {"enabled": True, "lambda": lam, "deltaS": deltaS, "multiplier": mult}


def run_engine(
    engine: EngineInput,
    params: GRUTParams,
    obs_mod: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Run the canonical GRUT operator stack (Phase D).

    Returns:
      out: JSON-serializable engine outputs
      internal: diagnostics for NIS + response shaping
    """

    z = np.asarray(engine.z_grid, dtype=float)
    if z.ndim != 1 or len(z) < 2:
        raise ValueError("z_grid must be a 1D array with at least 2 points")

    # Optional grids
    rho_supplied = engine.rho_grid is not None
    rho = np.asarray(engine.rho_grid, dtype=float) if rho_supplied else np.zeros_like(z)
    v = np.asarray(engine.v_grid, dtype=float) if engine.v_grid is not None else np.zeros_like(z)

    # Grid diagnostics for warnings
    dz = np.diff(z)
    z_len = int(len(z))
    z_min_dz = float(np.min(np.abs(dz))) if len(dz) else 0.0

    # -------- H(z) model --------
    hz_cfg = engine.hz_model
    if hz_cfg.model != "lcdm_flat":
        raise ValueError(f"Unsupported Hz model: {hz_cfg.model}")
    Hz = hz_lcdm_flat(z, hz_cfg.H0_km_s_Mpc, hz_cfg.Omega_m, hz_cfg.Omega_lambda)
    H0 = H0_SI(hz_cfg.H0_km_s_Mpc)

    # -------- tau_eff(z) --------
    tau_eff = tau_eff_seconds(params, z, Hz, H0, engine.tau_scaling.TAU_FACTOR, engine.tau_scaling.p)

    # -------- phase bridge --------
    s = S_phase(z, engine.phase_bridge.x0, engine.phase_bridge.w)

    # -------- raw gain and stiffness cap --------
    g_raw = 1.0 + params.alpha_imp * s

    if rho_supplied:
        chi = rho / max(engine.stiff_cap.rho_lock, 1e-30)
        g_cap = L_stiff(chi, params.g_max, engine.stiff_cap.sigma_cap)
    else:
        # If no density grid is provided, do not engage the stiff-cap.
        chi = np.zeros_like(z)
        g_cap = np.full_like(z, params.g_max)

    g_final = smooth_min(g_raw, g_cap, k=params.smooth_min_k)
    # Smooth-min can undershoot by a tiny amount; clamp to physical bounds.
    g_final = np.clip(g_final, 1.0, params.g_max)

    # -------- dissipation --------
    eps_t_s = float(engine.eps_t_myr) * MYR_IN_S
    fuzz_fraction = eps_t_s / params.tau0_seconds
    Phi = phi_z(z, engine.dissipation.phi_mode, s_phase=s)
    D = engine.dissipation.k * fuzz_fraction * Phi

    # Optional observer coupling (Phase D)
    D_mult, D_mod_meta = _observer_dissipation_multiplier(obs_mod, params)
    D = D * D_mult

    D = np.clip(D, 0.0, 0.999)
    E_obs = params.E_base * (1.0 - D)

    # -------- growth proxy (optional) --------
    f_sigma8_base = None
    f_sigma8_grut = None
    if engine.growth.enable and params.enable_growth_proxy:
        Omz = omega_m_z(z, hz_cfg.Omega_m, hz_cfg.Omega_lambda)
        f = np.clip(Omz, 0.0, 1.0) ** float(engine.growth.gamma)
        f_sigma8_base = float(engine.growth.sigma8) * f
        # Explicit GRUT-modulated proxy: baseline * gain
        f_sigma8_grut = f_sigma8_base * g_final

    # -------- diagnostics for NIS --------
    cap_engaged = (g_raw > g_cap).astype(float)
    cap_engaged_frac = float(np.mean(cap_engaged)) if rho_supplied else 0.0
    pivot_band = ((s > 0.25) & (s < 0.75)).astype(float)
    pivot_intensity = float(np.mean(pivot_band))
    D_max = float(np.max(D))
    D_eff = float(np.mean(D))
    # Potential transfer proxy (positive only)
    W_phase = float(np.mean(np.maximum(g_final - 1.0, 0.0)))
    g_min = float(np.min(g_final))
    g_max_obs = float(np.max(g_final))

    # Smoothness diagnostic: finite-difference second derivative magnitude
    dg = np.gradient(g_final, z)
    d2g = np.gradient(dg, z)
    pivot_mask = (s > 0.25) & (s < 0.75)
    kink_metric = float(np.max(np.abs(d2g[pivot_mask])) if np.any(pivot_mask) else np.max(np.abs(d2g)))

    internal: Dict[str, Any] = {
        "eps_t_myr": float(engine.eps_t_myr),
        "fuzz_fraction": float(fuzz_fraction),
        "cap_engaged_frac": cap_engaged_frac,
        "pivot_intensity": pivot_intensity,
        "D_max": D_max,
        "D_eff": D_eff,
        "W_phase": W_phase,
        "g_min": g_min,
        "g_max_obs": g_max_obs,
        "kink_metric": kink_metric,
        "z_len": z_len,
        "z_min_dz": z_min_dz,
        "H0_SI": float(H0),
        "Hz_model": hz_cfg.model,
        "growth_enabled": bool(engine.growth.enable),
        "observer_modulation": D_mod_meta,
    }

    out: Dict[str, Any] = {
        "z_grid": [float(x) for x in z.tolist()],
        "tau_eff_s": [float(x) for x in tau_eff.tolist()],
        "S_phase": [float(x) for x in s.tolist()],
        "g_raw": [float(x) for x in g_raw.tolist()],
        "g_cap": [float(x) for x in g_cap.tolist()],
        "g_final": [float(x) for x in g_final.tolist()],
        "D": [float(x) for x in D.tolist()],
        "E_obs": [float(x) for x in E_obs.tolist()],
        "observer_modulation": D_mod_meta,
        "anchor": {"K0": params.K0_anchor, "zpe_neutral": True},
    }
    if f_sigma8_base is not None:
        out["f_sigma8_base"] = [float(x) for x in f_sigma8_base.tolist()]
        out["f_sigma8_grut"] = [float(x) for x in f_sigma8_grut.tolist()]

    return out, internal
