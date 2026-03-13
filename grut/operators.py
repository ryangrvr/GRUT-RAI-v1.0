import math
from typing import Dict, Any

from .canon import GRUTCanon


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
