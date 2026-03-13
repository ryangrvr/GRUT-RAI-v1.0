import math
from typing import Dict, Any

from .canon import GRUTCanon
from .quantum import compute_boundary, compute_scan_rows_mass, compute_scan_rows_omega


def _sanitize_state(canon: GRUTCanon, state: Dict[str, float]) -> Dict[str, float]:
    a_min = canon.get_value("a_min")
    w = canon.get_value("w")

    state["a"] = max(float(state["a"]), a_min)
    rho = float(state["rho"])
    if rho < 0:
        raise ValueError("Canonical constraint violated: rho must be >= 0")
    state["rho"] = rho

    if "p" not in state or state["p"] is None:
        state["p"] = w * rho
    else:
        state["p"] = float(state["p"])

    return state


def _H_base2(canon: GRUTCanon, a: float, rho: float) -> float:
    C_rho = canon.get_value("C_rho")
    C_k = canon.get_value("C_k")
    K0 = canon.get_value("k0")
    return (C_rho * rho) + (C_k * K0 / (a * a))


def _tau_eff(canon: GRUTCanon, H: float) -> float:
    tau0 = canon.get_value("tau0")
    return tau0 / (1.0 + (H * tau0) ** 2)


def op_genesis(canon: GRUTCanon, state: Dict[str, float], context: Dict[str, Any]) -> tuple[Dict[str, float], Dict[str, Any]]:
    state = _sanitize_state(canon, state)

    alpha = canon.get_value("alpha_mem")
    genesis_cfg = canon.data.get("genesis", {}).get("memory_init", {})
    mode = genesis_cfg.get("mode", "steady_state")
    explicit_M = genesis_cfg.get("explicit_M_X")

    a = float(state["a"])
    rho = float(state["rho"])
    Hbase2 = _H_base2(canon, a, rho)
    X0 = Hbase2

    if mode == "steady_state":
        M0 = X0
    elif mode == "empty_history":
        M0 = 0.0
    elif mode == "explicit":
        if explicit_M is None:
            raise ValueError("genesis.mode=explicit requires genesis.memory_init.explicit_M_X")
        M0 = float(explicit_M)
    else:
        raise ValueError(f"Unknown genesis mode: {mode}")

    H2 = (1.0 - alpha) * Hbase2 + alpha * M0
    H2 = max(H2, 0.0)
    H0 = math.sqrt(H2)
    tau_eff0 = _tau_eff(canon, H0)

    state["M_X"] = M0
    state["H"] = H0
    state["tau_eff"] = tau_eff0

    op_log = {
        "genesis_mode": mode,
        "driver": "X=H_base^2",
        "H_base2_t0": Hbase2,
        "M_X_t0": M0,
        "H_t0": H0,
        "tau_eff_t0": tau_eff0,
    }
    return state, op_log


def op_s_phase(canon: GRUTCanon, state: Dict[str, float], context: Dict[str, Any]) -> tuple[Dict[str, float], Dict[str, Any]]:
    state = _sanitize_state(canon, state)
    return state, {}


def op_l_stiff(canon: GRUTCanon, state: Dict[str, float], context: Dict[str, Any]) -> tuple[Dict[str, float], Dict[str, Any]]:
    H_cap = canon.get_value("H_cap")
    H = float(state["H"])
    if abs(H) > H_cap:
        state["H"] = H_cap if H > 0 else -H_cap
        context["warnings"].append("L_STIFF_ACTIVATED:H_CAPPED")
    return state, {}


def op_tau_coupling(canon: GRUTCanon, state: Dict[str, float], context: Dict[str, Any]) -> tuple[Dict[str, float], Dict[str, Any]]:
    H = float(state["H"])
    tau_eff = _tau_eff(canon, H)
    state["tau_eff"] = tau_eff
    return state, {}


def op_dissipation(
    canon: GRUTCanon, state: Dict[str, float], context: Dict[str, Any]
) -> tuple[Dict[str, float], Dict[str, Any]]:
    gamma_h = canon.get_value("gamma_H")
    if gamma_h < 0:
        raise ValueError("Canonical constraint violated: gamma_H must be >= 0")
    dt_years = float(context.get("dt_years", 0.0))
    state["H"] = float(state["H"]) * math.exp(-gamma_h * dt_years)
    return state, {}


def op_growth_linear(canon: GRUTCanon, state: Dict[str, float], context: Dict[str, Any]) -> tuple[Dict[str, float], Dict[str, Any]]:
    if context.get("growth_enabled") is False:
        return state, {"skipped": True}

    eps = 1e-30
    D_floor = 1e-30
    a = float(state.get("a", 1.0))
    H = float(state.get("H", 0.0))
    rho_m = float(state.get("rho_m", 0.0))
    H_floor = 1e-12
    cert = context.get("cert")

    lna = math.log(max(a, eps))
    prev_lna = float(context.get("growth_prev_lna", lna))
    dlna = lna - prev_lna

    if "D" not in state or "Dp" not in state:
        if rho_m <= eps:
            state["D"] = D_floor
            state["Dp"] = 0.0
        else:
            state["D"] = a
            state["Dp"] = a * max(H, 0.0)
        if isinstance(cert, dict):
            cert.setdefault("initial_conditions", {})
            cert["initial_conditions"]["growth_init"] = {
                "mode": "growing_mode",
                "a_init": a,
                "D_init": state["D"],
                "Dp_init": state["Dp"],
            }

    D = float(state.get("D", a))
    Dp = float(state.get("Dp", 0.0))

    H2 = H * H
    if not math.isfinite(H2) or H2 <= 1e-20:
        Omega_m = 0.0
    else:
        Omega_m = (canon.get_value("C_rho") * rho_m) / H2

    if abs(dlna) <= 0.0:
        context["growth_prev_lna"] = lna
        return state, {"Omega_m": Omega_m, "f": None, "D": D, "Dp": Dp, "dlnH_dlna": None}

    if H < H_floor or not math.isfinite(H):
        if isinstance(cert, dict):
            cert.setdefault("run_trace", {})
            cert["run_trace"]["growth_held_low_H_steps"] = cert["run_trace"].get("growth_held_low_H_steps", 0) + 1
        context.get("warnings", []).append("GROWTH_HELD_LOW_H")
        state["D"] = max(D_floor, D)
        state["Dp"] = Dp
        context["growth_prev_lna"] = lna
        return state, {"Omega_m": Omega_m, "f": 0.0, "D": state["D"], "Dp": state["Dp"], "dlnH_dlna": None}

    if rho_m <= eps:
        state["D"] = max(D_floor, D)
        state["Dp"] = 0.0
        return state, {"Omega_m": Omega_m, "f": 0.0, "D": state["D"], "Dp": 0.0, "dlnH_dlna": None}

    four_pi_G = 1.5 * canon.get_value("C_rho")
    dt_eff = abs(dlna) / max(H, H_floor)

    def _derivs(Dv: float, Dpv: float, Hv: float, rho_mv: float) -> tuple[float, float]:
        dD = Dpv
        dDp = (four_pi_G * rho_mv * Dv) - (2.0 * Hv * Dpv)
        return dD, dDp

    dD1, dDp1 = _derivs(D, Dp, H, rho_m)
    D_mid = D + 0.5 * dt_eff * dD1
    Dp_mid = Dp + 0.5 * dt_eff * dDp1
    dD2, dDp2 = _derivs(D_mid, Dp_mid, H, rho_m)

    D_new = D + dt_eff * dD2
    Dp_new = Dp + dt_eff * dDp2

    if not math.isfinite(D_new):
        D_new = D
    if not math.isfinite(Dp_new):
        Dp_new = Dp

    if D_new <= 0.0:
        D_new = max(D_floor, D)
        Dp_new = 0.0

    state["D"] = D_new
    state["Dp"] = Dp_new
    context["growth_prev_lna"] = lna

    f = Dp_new / max(H * D_new, eps)
    return state, {"Omega_m": Omega_m, "f": f, "D": D_new, "Dp": Dp_new, "dlnH_dlna": None}


def op_quantum_decohere(
    canon: GRUTCanon, state: Dict[str, float], context: Dict[str, Any]
) -> tuple[Dict[str, float], Dict[str, Any]]:
    m_kg = float(context.get("m_kg", 0.0))
    l_m = float(context.get("l_m", 0.0))
    tau0_s = context.get("tau0_s")
    omega_policy = str(context.get("omega_policy", "controlled"))
    omega_exp = context.get("omega_exp")
    alpha_vac = float(context.get("alpha_vac", 1.0 / 3.0))

    if tau0_s is None:
        tau0_s = canon.get_value("CONST_TAU_0") * 365.25 * 24.0 * 3600.0
    else:
        tau0_s = float(tau0_s)

    inputs, outputs = compute_boundary(
        m_kg=m_kg,
        l_m=l_m,
        tau0_s=tau0_s,
        omega_policy=omega_policy,
        omega_exp=omega_exp,
        alpha_vac=alpha_vac,
    )

    log: Dict[str, Any] = {
        "inputs": inputs,
        "outputs": outputs,
    }

    scan_mode = context.get("scan_mode")
    if scan_mode == "omega":
        rows = compute_scan_rows_omega(
            m_kg=inputs["m_kg"],
            l_m=inputs["l_m"],
            tau0_s=inputs["tau0_s"],
            alpha_vac=inputs["alpha_vac"],
            omega_min=float(context.get("scan_omega_min", 0.0)),
            omega_max=float(context.get("scan_omega_max", 0.0)),
            scan_points=int(context.get("scan_points", 0)),
        )
        log["scan_omega"] = rows
    elif scan_mode == "mass":
        rows = compute_scan_rows_mass(
            m_min=float(context.get("scan_mass_min", 0.0)),
            m_max=float(context.get("scan_mass_max", 0.0)),
            scan_points=int(context.get("scan_points", 0)),
            l_m=inputs["l_m"],
            tau0_s=inputs["tau0_s"],
            alpha_vac=inputs["alpha_vac"],
            omega_policy=inputs["omega_policy"],
            omega_exp=inputs["omega_exp"],
        )
        log["scan_mass"] = rows

    return state, log
