import math
from typing import Any, Dict, List, Tuple, Optional

from .canon import GRUTCanon
from .certificate import init_certificate, finalize_certificate, add_repro_hash
from .operator_factory import OperatorFactory
from .operators import (
    op_genesis,
    op_s_phase,
    op_l_stiff,
    op_dissipation,
    op_tau_coupling,
    op_growth_linear,
    op_quantum_decohere,
)
from .exceptions import CanonError
from .utils import is_finite
from .schema_validate import validate_json_schema


def _rk4_step(f, t, y, dt):
    k1 = f(t, y)
    k2 = f(t + 0.5 * dt, {k: y[k] + 0.5 * dt * k1[k] for k in y})
    k3 = f(t + 0.5 * dt, {k: y[k] + 0.5 * dt * k2[k] for k in y})
    k4 = f(t + dt, {k: y[k] + dt * k3[k] for k in y})
    return {k: y[k] + (dt / 6.0) * (k1[k] + 2 * k2[k] + 2 * k3[k] + k4[k]) for k in y}


def _memory_exact_update(M: float, X: float, dt: float, tau_eff: float, eps: float = 1e-30) -> Tuple[float, float]:
    if not is_finite(tau_eff) or tau_eff <= 0.0:
        raise ValueError("Canonical constraint violated: tau_eff must be finite and > 0")
    denom = max(tau_eff, eps)
    lam = dt / denom
    e = math.exp(-lam)
    one_minus_e = -math.expm1(-lam)
    M_new = (M * e) + (X * one_minus_e)
    return M_new, lam


class GRUTEngine:
    def __init__(self, canon: GRUTCanon, determinism_mode: str = "STRICT", engine_version: str = "GRUT-RAI-v1.0"):
        self.canon = canon
        self.determinism_mode = determinism_mode
        self.engine_version = engine_version
        self.factory = OperatorFactory()
        self.factory.register("OP_GENESIS")(op_genesis)
        self.factory.register("OP_S_PHASE")(op_s_phase)
        self.factory.register("OP_L_STIFF")(op_l_stiff)
        self.factory.register("OP_DISSIPATION")(op_dissipation)
        self.factory.register("OP_TAU_COUPLING")(op_tau_coupling)
        self.factory.register("OP_GROWTH_LINEAR")(op_growth_linear)
        self.factory.register("OP_QUANTUM_DECOHERE")(op_quantum_decohere)
        self.factory.validate_against_canon(self.canon)

    def run(
        self,
        input_state: Dict[str, float],
        run_config: Optional[Dict[str, Any]] = None,
        assumption_toggles: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        run_config = run_config or {}
        assumption_toggles = assumption_toggles or {}

        dt_years = float(run_config.get("dt_years", self.canon.numeric_policy.get("dt_years_default", 1e5)))
        steps = int(run_config.get("steps", self.canon.numeric_policy.get("max_steps_default", 2000)))
        integrator = str(run_config.get("integrator", self.canon.numeric_policy.get("integrator", "RK4")))

        start_z = run_config.get("start_z")
        if start_z is None:
            try:
                start_z = self.canon.get_value("PARAM_Z_START")
            except CanonError:
                start_z = 0.0
        start_z = float(start_z)

        original_has_a = "a" in input_state
        input_state = dict(input_state)
        rho_at_start = bool(input_state.get("rho_at_start", False))
        rho_is_rho0 = bool(run_config.get("rho_is_rho0", True))
        rho0_input = input_state.get("rho")
        p0_input = input_state.get("p")
        rho_m0_input = input_state.get("rho_m0")
        rho_m_input = input_state.get("rho_m")
        w_eff = self.canon.get_value("w")
        w_eff_infer = None
        rho_init_inferred = None
        p_init_used = None
        rho_m_init_used = None

        if p0_input is not None and rho0_input is not None and float(rho0_input) != 0.0:
            w_eff = float(p0_input) / float(rho0_input)

        if rho_m0_input is None:
            if abs(float(w_eff)) < 1e-3 and rho0_input is not None:
                rho_m0_input = float(rho0_input)
            else:
                rho_m0_input = 0.0

        start_z_mode = start_z > 0.0 and (not original_has_a or float(input_state.get("a", 1.0)) == 1.0)
        if start_z_mode:
            a_init = 1.0 / (1.0 + start_z)
            input_state["a"] = a_init
            if rho_is_rho0 and not rho_at_start:
                if p0_input is not None and rho0_input is not None and float(rho0_input) != 0.0:
                    w_eff_infer = float(p0_input) / float(rho0_input)
                else:
                    w_eff_infer = self.canon.get_value("w")
                rho0_val = float(rho0_input) if rho0_input is not None else 1.0
                rho_init_inferred = rho0_val * (a_init ** (-3.0 * (1.0 + w_eff_infer)))
                input_state["rho"] = rho_init_inferred
                p_init_used = float(w_eff_infer) * float(rho_init_inferred)
                input_state["p"] = p_init_used
                w_eff = w_eff_infer
            else:
                if rho0_input is not None:
                    input_state["rho"] = float(rho0_input)
                if p0_input is not None:
                    input_state["p"] = float(p0_input)
                if input_state.get("rho") is not None and float(input_state.get("rho", 0.0)) != 0.0:
                    if input_state.get("p") is not None:
                        w_eff = float(input_state.get("p")) / float(input_state.get("rho"))
                    else:
                        w_eff = self.canon.get_value("w")
                        input_state["p"] = float(w_eff) * float(input_state.get("rho"))
                p_init_used = input_state.get("p")

            if rho_is_rho0 and rho_m_input is None:
                rho_m0_val = float(rho_m0_input) if rho_m0_input is not None else 0.0
                rho_m_init_used = rho_m0_val * (a_init ** -3.0)
                input_state["rho_m"] = rho_m_init_used
            elif rho_m_input is not None:
                rho_m_init_used = float(rho_m_input)
                input_state["rho_m"] = rho_m_init_used
            else:
                rho_m_init_used = float(rho_m0_input) if rho_m0_input is not None else 0.0
                input_state["rho_m"] = rho_m_init_used
        else:
            if rho_m_input is not None:
                rho_m_init_used = float(rho_m_input)
            else:
                rho_m_init_used = float(rho_m0_input) if rho_m0_input is not None else 0.0

        cfg = {"dt_years": dt_years, "steps": steps, "integrator": integrator}

        cert = init_certificate(
            engine_version=self.engine_version,
            canon_hash=self.canon.canon_hash,
            determinism_mode=self.determinism_mode,
            input_state=input_state,
            run_config=cfg,
            assumption_toggles=assumption_toggles,
            operator_stack_keys=[op.stack_key for op in self.canon.operators],
        )
        cert["run_trace"]["operator_execution_counts"] = {
            op.op_id: 0 for op in self.canon.operators
        }
        has_growth_op = any(op.stack_key == "OP_GROWTH_LINEAR" for op in self.canon.operators)
        growth_enabled = bool(assumption_toggles.get("growth_enabled", True)) and has_growth_op
        cert["run_trace"]["growth_enabled"] = growth_enabled
        if growth_enabled:
            cert["run_trace"]["growth_method"] = "TIME_DOMAIN"
            cert["run_trace"]["growth_held_low_H_steps"] = 0
        valid_z_max = run_config.get("valid_z_max")
        if valid_z_max is not None:
            cert["run_trace"]["valid_z_max"] = float(valid_z_max)

        diagnostics_enabled = bool(assumption_toggles.get("diagnostics", False))

        state = {
            "a": float(input_state.get("a", 1.0)),
            "H": float(input_state.get("H", 0.0)),
            "rho": float(input_state.get("rho", 1.0)),
            "p": float(input_state.get("p", 0.0)),
            "rho_m": float(input_state.get("rho_m", rho_m_init_used or 0.0)),
            "M_X": float(input_state.get("M_X", 0.0)),
            "tau_eff": float(input_state.get("tau_eff", self.canon.get_value("tau0"))),
        }

        hz_z: List[float] = []
        hz_H: List[float] = []
        growth_z: List[float] = []
        growth_D: List[float] = []
        growth_Dp: List[float] = []
        diag: Dict[str, List[float]] = {}
        diag_H2_negative_count = 0
        diag_H2_negative_first_index = None
        diag_H2_negative_first_z = None
        diag_H2_negative_above_valid_z_max = 0
        if diagnostics_enabled:
            diag = {
                "a": [],
                "rho": [],
                "H_base2": [],
                "M_X": [],
                "H2_raw": [],
            }

        alpha = self.canon.get_value("alpha_mem")
        C_rho = self.canon.get_value("C_rho")
        C_k = self.canon.get_value("C_k")
        K0 = self.canon.get_value("k0")
        w = self.canon.get_value("w")

        def rhs(_t: float, y: Dict[str, float], M_const: float) -> Dict[str, float]:
            a = y["a"]
            rho = y["rho"]
            rho_m = y.get("rho_m", 0.0)
            p = float(context.get("w_eff", w)) * rho

            H_base2 = (C_rho * rho) + (C_k * K0 / (a * a))
            H2 = (1.0 - alpha) * H_base2 + alpha * M_const
            H2 = max(H2, 0.0)
            H_new = math.sqrt(H2)

            drhodt = -3.0 * H_new * (rho + p)
            drho_m_dt = -3.0 * H_new * rho_m
            dadt = a * H_new

            return {"a": dadt, "rho": drhodt, "rho_m": drho_m_dt}

        context = {
            "dt_years": dt_years,
            "step_index": 0,
            "warnings": cert["run_trace"]["warnings"],
            "determinism_mode": self.determinism_mode,
            "cert": cert,
            "growth_enabled": growth_enabled,
            "w_eff": w_eff,
            "diagnostics_enabled": diagnostics_enabled,
        }

        genesis_def = self.canon.operator_defs.get("OP_GENESIS", {})
        if not genesis_def:
            raise CanonError("Canon missing mandatory OP_GENESIS definition")

        genesis_fn = self.factory.get("OP_GENESIS")
        state, genesis_log = genesis_fn(self.canon, state, context)
        cert["run_trace"]["operators_executed_ids"].append(genesis_def.get("id", "OP_GENESIS"))
        cert["run_trace"]["operator_execution_counts"][genesis_def.get("id", "OP_GENESIS")] = 1
        cert["initial_conditions"] = {
            "t0_years": 0.0,
            "genesis_mode": genesis_log.get("genesis_mode"),
            "driver": genesis_log.get("driver"),
            "H_base2_t0": genesis_log.get("H_base2_t0"),
            "M_X_t0": genesis_log.get("M_X_t0"),
            "H_t0": genesis_log.get("H_t0"),
            "tau_eff_t0": genesis_log.get("tau_eff_t0"),
            "transient_warning": genesis_log.get("genesis_mode") == "empty_history",
        }
        rho_used = float(state.get("rho", 0.0))
        p_used = float(state.get("p", 0.0))
        w_eff_used = None
        if rho_used != 0.0:
            w_eff_used = p_used / rho_used
        cert["initial_conditions"]["a_init_used"] = float(state.get("a", 0.0))
        cert["initial_conditions"]["rho_init_used"] = rho_used
        cert["initial_conditions"]["p_init_used"] = p_used
        cert["initial_conditions"]["w_effective_init"] = w_eff_used
        cert["initial_conditions"]["start_z_used"] = float(start_z)
        cert["initial_conditions"]["start_z"] = float(start_z)
        if "a" in input_state:
            cert["initial_conditions"]["a_init"] = float(input_state.get("a"))
        if "rho" in input_state:
            cert["initial_conditions"]["rho_init"] = float(input_state.get("rho"))
        if "rho_m" in input_state:
            cert["initial_conditions"]["rho_m_init"] = float(input_state.get("rho_m"))
        if "rho0_vac" in input_state:
            cert["initial_conditions"]["rho0_vac"] = float(input_state.get("rho0_vac"))
        if "rho_vac_init" in input_state:
            cert["initial_conditions"]["rho_vac_init"] = float(input_state.get("rho_vac_init"))
        if "rho_m_init" in input_state:
            cert["initial_conditions"]["rho_m_init"] = float(input_state.get("rho_m_init"))
        if "rho_total_init" in input_state:
            cert["initial_conditions"]["rho_total_init"] = float(input_state.get("rho_total_init"))
        if "p_total_init" in input_state:
            cert["initial_conditions"]["p_total_init"] = float(input_state.get("p_total_init"))
        if "rho_m0_min" in input_state:
            cert["initial_conditions"]["rho_m0_min"] = float(input_state.get("rho_m0_min"))
        if "curv_term" in input_state:
            cert["initial_conditions"]["curv_term"] = float(input_state.get("curv_term"))
        if "base_term" in input_state:
            cert["initial_conditions"]["base_term"] = float(input_state.get("base_term"))
        if "rho_total0" in input_state:
            cert["initial_conditions"]["rho_total0"] = float(input_state.get("rho_total0"))
        if "p_total0" in input_state:
            cert["initial_conditions"]["p_total0"] = float(input_state.get("p_total0"))
        if "rho_threshold_min" in input_state:
            cert["initial_conditions"]["rho_threshold_min"] = float(input_state.get("rho_threshold_min"))
        cert["initial_conditions"]["rho_is_rho0"] = bool(rho_is_rho0)
        if rho0_input is not None:
            cert["initial_conditions"]["rho0_input"] = float(rho0_input)
        if rho_m0_input is not None:
            cert["initial_conditions"]["rho_m0_input"] = float(rho_m0_input)
        if rho_m_init_used is not None:
            cert["initial_conditions"]["rho_m_init_used"] = float(rho_m_init_used)
        if p0_input is not None:
            cert["initial_conditions"]["p0_input"] = float(p0_input)
        if w_eff_infer is not None:
            cert["initial_conditions"]["w_eff_used_for_inference"] = float(w_eff_infer)
        if rho_init_inferred is not None:
            cert["initial_conditions"]["rho_init_inferred"] = float(rho_init_inferred)
        if p_init_used is not None:
            cert["initial_conditions"]["p_init_used"] = float(p_init_used)
        if "rho_at_start" in input_state:
            cert["initial_conditions"]["rho_at_start"] = bool(input_state.get("rho_at_start"))
        if start_z_mode:
            dlna_target = -math.log(max(float(input_state.get("a", 1.0)), 1e-30)) / max(steps, 1)
            context["dlna_target"] = dlna_target
            cert["initial_conditions"]["dlna_target"] = float(dlna_target)

        context["growth_prev_lna"] = math.log(max(state["a"], 1e-30))
        context["growth_prev_lnH"] = math.log(max(abs(state["H"]), 1e-30))

        t = 0.0
        max_dt_over_tau_eff = 0.0
        for i in range(steps):
            context["step_index"] = i
            growth_op = None
            for op in self.canon.operators:
                op_def = self.canon.operator_defs.get(op.stack_key, {})
                if op_def.get("bootstrap_only", False):
                    continue
                if op.stack_key == "OP_GROWTH_LINEAR":
                    growth_op = op
                    continue
                fn = self.factory.get(op.stack_key)
                state, _ = fn(self.canon, state, context)
                if op.op_id not in cert["run_trace"]["operators_executed_ids"]:
                    cert["run_trace"]["operators_executed_ids"].append(op.op_id)
                cert["run_trace"]["operator_execution_counts"][op.op_id] += 1

            a = state["a"]
            rho = state["rho"]
            M_X = state["M_X"]

            H_base2 = (C_rho * rho) + (C_k * K0 / (a * a))
            X = H_base2

            H2 = (1.0 - alpha) * H_base2 + alpha * M_X
            H_now = math.sqrt(max(H2, 0.0))
            tau0 = self.canon.get_value("tau0")
            tau_eff_now = tau0 / (1.0 + (H_now * tau0) ** 2)

            M_X, lam = _memory_exact_update(M_X, X, 0.5 * dt_years, tau_eff_now)
            max_dt_over_tau_eff = max(max_dt_over_tau_eff, dt_years / max(tau_eff_now, 1e-30))
            state["M_X"] = M_X

            H2 = (1.0 - alpha) * H_base2 + alpha * M_X
            state["H"] = math.sqrt(max(H2, 0.0))

            rho_m_next = state.get("rho_m", 0.0)
            if start_z_mode:
                dlna = float(context.get("dlna_target", 0.0))
                a_next = state["a"] * math.exp(dlna)
                w_eff_step = float(context.get("w_eff", w))
                rho_next = state["rho"] * math.exp(-3.0 * (1.0 + w_eff_step) * dlna)
                rho_m_next = state.get("rho_m", 0.0) * math.exp(-3.0 * dlna)
            else:
                y = {"a": state["a"], "rho": state["rho"], "rho_m": state.get("rho_m", 0.0)}
                if integrator.upper() == "RK4":
                    y = _rk4_step(lambda tt, yy: rhs(tt, yy, M_X), t, y, dt_years)
                else:
                    dy = rhs(t, y, M_X)
                    y = {k: y[k] + dt_years * dy.get(k, 0.0) for k in y}
                a_next = y["a"]
                rho_next = y["rho"]
                rho_m_next = y.get("rho_m", 0.0)

            a_min = self.canon.get_value("a_min")
            a_cap = 1e300
            if not is_finite(float(a_next)) or a_next > a_cap:
                context["warnings"].append("A_CLAMPED_MAX")
                a_next = a_cap
            if a_next < a_min:
                context["warnings"].append("A_CLAMPED_MIN")
                a_next = a_min
            state["a"] = a_next
            if rho_next < 0.0:
                context["warnings"].append("RHO_CLAMPED_NONNEGATIVE")
                rho_next = 0.0
            state["rho"] = rho_next
            state["p"] = float(context.get("w_eff", w)) * state["rho"]
            if rho_m_next < 0.0:
                rho_m_next = 0.0
            state["rho_m"] = rho_m_next

            a_end = state["a"]
            rho_end = state["rho"]
            H_base2_end = (C_rho * rho_end) + (C_k * K0 / (a_end * a_end))
            X_end = H_base2_end

            H2_end = (1.0 - alpha) * H_base2_end + alpha * M_X
            H_end = math.sqrt(max(H2_end, 0.0))
            tau_eff_end = tau0 / (1.0 + (H_end * tau0) ** 2)

            M_X, _ = _memory_exact_update(M_X, X_end, 0.5 * dt_years, tau_eff_end)
            state["M_X"] = M_X

            H2_end = (1.0 - alpha) * H_base2_end + alpha * M_X
            state["H"] = math.sqrt(max(H2_end, 0.0))
            if diagnostics_enabled:
                diag["a"].append(state["a"])
                diag["rho"].append(state["rho"])
                diag["H_base2"].append(H_base2_end)
                diag["M_X"].append(M_X)
                diag["H2_raw"].append(H2_end)
                z = (1.0 / state["a"]) - 1.0
                if H2_end < 0.0:
                    diag_H2_negative_count += 1
                    if diag_H2_negative_first_index is None:
                        diag_H2_negative_first_index = i
                        diag_H2_negative_first_z = z
                if valid_z_max is not None and H2_end < 0.0 and z > float(valid_z_max):
                    diag_H2_negative_above_valid_z_max += 1

            z = (1.0 / state["a"]) - 1.0
            hz_z.append(z)
            hz_H.append(state["H"])

            if growth_op is not None and growth_enabled:
                fn = self.factory.get(growth_op.stack_key)
                state, _ = fn(self.canon, state, context)
                if growth_op.op_id not in cert["run_trace"]["operators_executed_ids"]:
                    cert["run_trace"]["operators_executed_ids"].append(growth_op.op_id)
                cert["run_trace"]["operator_execution_counts"][growth_op.op_id] += 1
                growth_z.append(z)
                growth_D.append(float(state.get("D", 0.0)))
                growth_Dp.append(float(state.get("Dp", 0.0)))

            if self.canon.numeric_policy.get("strict_nan_check", True):
                for k, v in state.items():
                    if isinstance(v, (int, float)) and not is_finite(float(v)):
                        raise ValueError(f"Non-finite state detected at step {i}: {k}={v}")

            t += dt_years

        cert["run_trace"]["steps_computed"] = steps
        cert["run_trace"]["memory_update_scheme"] = "EXACT_EXPONENTIAL_STRANG"
        cert["run_trace"]["max_dt_over_tau_eff"] = max_dt_over_tau_eff

        H_floor = 1e-12
        H_floor_count = sum(1 for h in hz_H if h < H_floor)

        outputs = {
            "final_state": state,
            "OBS_HZ_001": {
                "z": hz_z,
                "H": hz_H,
            },
        }
        if diagnostics_enabled:
            outputs["diagnostics"] = {
                **diag,
                "H2_negative_count": diag_H2_negative_count,
                "H2_negative_first_index": diag_H2_negative_first_index,
                "H2_negative_first_z": diag_H2_negative_first_z,
                "H2_negative_count_above_valid_z_max": diag_H2_negative_above_valid_z_max,
            }

        cert["run_trace"]["fsigma8_masking_enabled"] = False
        cert["run_trace"]["H_floor"] = H_floor
        cert["run_trace"]["H_floor_count"] = H_floor_count
        cert["run_trace"]["fs8_masked_count"] = 0

        observables_emitted = ["OBS_HZ_001"]
        if growth_enabled and growth_D:
            sigma8_0 = self.canon.get_value("PARAM_SIGMA8_0") if "PARAM_SIGMA8_0" in self.canon.constants_by_id else 0.0
            D0 = None
            if growth_z:
                idx = min(range(len(growth_z)), key=lambda j: abs(growth_z[j]))
                D0 = growth_D[idx]
            if D0 is None or D0 == 0.0:
                D0 = 1e-30
            D_over_D0 = [d / D0 for d in growth_D]
            sigma8 = [sigma8_0 * d for d in D_over_D0]
            growth_method = cert.get("run_trace", {}).get("growth_method")
            if growth_method == "TIME_DOMAIN":
                f = [
                    (dp / max(d * h, 1e-30)) if h > 0.0 else 0.0
                    for d, dp, h in zip(growth_D, growth_Dp, hz_H)
                ]
            else:
                f = [dp / max(d, 1e-30) for d, dp in zip(growth_D, growth_Dp)]
            compare_H_multiplier = 10.0
            compare_definition = (
                "compare mask: z in [0, start_z] AND H > 10*H_floor AND fsigma8 not None"
            )
            fs8_mask = []
            fsigma8 = []
            compare_mask = []
            for i, (fi, si) in enumerate(zip(f, sigma8)):
                H_val = hz_H[i] if i < len(hz_H) else 0.0
                D_val = growth_D[i] if i < len(growth_D) else 0.0
                masked = (H_val < H_floor) or (D_val <= 0.0)
                fs8_mask.append(masked)
                fs8_val = None if masked else fi * si
                fsigma8.append(fs8_val)
                z_val = growth_z[i] if i < len(growth_z) else None
                in_range = (z_val is not None) and (0.0 <= z_val <= float(start_z))
                compare_ok = (
                    in_range
                    and (H_val > (compare_H_multiplier * H_floor))
                    and (fs8_val is not None)
                )
                compare_mask.append(compare_ok)
            outputs["OBS_FS8_001"] = {
                "z": growth_z,
                "fsigma8": fsigma8,
                "f": f,
                "sigma8": sigma8,
                "D_over_D0": D_over_D0,
                "fs8_mask": fs8_mask,
                "compare_mask": compare_mask,
            }
            observables_emitted.append("OBS_FS8_001")
            cert["run_trace"]["growth_sigma8_0"] = sigma8_0
            cert["run_trace"]["growth_D0"] = D0
            cert["run_trace"]["fsigma8_masking_enabled"] = True
            cert["run_trace"]["fs8_mask_rule"] = "H < 1e-12 or D <= 0"
            cert["run_trace"]["fs8_mask_H_floor"] = H_floor
            cert["run_trace"]["fs8_masked_count"] = sum(1 for m in fs8_mask if m)
            cert["run_trace"]["compare_definition"] = compare_definition
            cert["run_trace"]["compare_H_floor_multiplier"] = compare_H_multiplier

        cert = finalize_certificate(cert, outputs, observables_emitted=observables_emitted)
        cert = add_repro_hash(cert)

        # Machine validation: ensure emitted certificate matches the checked-in schema.
        if self.canon.schema_version == "v0.3":
            cert_schema = self.canon.schema_dir / "nis_certificate_schema_v0.3.json"
        else:
            cert_schema = self.canon.schema_dir / "nis_certificate_schema_v0.2.json"
        validate_json_schema(cert, cert_schema)
        return outputs, cert
