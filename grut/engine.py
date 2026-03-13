import math
from typing import Any, Dict, List, Tuple, Optional

from .canon import GRUTCanon
from .certificate import init_certificate, finalize_certificate, add_repro_hash
from .operator_factory import OperatorFactory
from .operators import op_genesis, op_s_phase, op_l_stiff, op_dissipation, op_tau_coupling
from .exceptions import CanonError
from .utils import is_finite


def _rk4_step(f, t, y, dt):
    k1 = f(t, y)
    k2 = f(t + 0.5 * dt, {k: y[k] + 0.5 * dt * k1[k] for k in y})
    k3 = f(t + 0.5 * dt, {k: y[k] + 0.5 * dt * k2[k] for k in y})
    k4 = f(t + dt, {k: y[k] + dt * k3[k] for k in y})
    return {k: y[k] + (dt / 6.0) * (k1[k] + 2 * k2[k] + 2 * k3[k] + k4[k]) for k in y}


class GRUTEngine:
    def __init__(self, canon: GRUTCanon, determinism_mode: str = "STRICT", engine_version: str = "GRUT-RAI-v0.2"):
        self.canon = canon
        self.determinism_mode = determinism_mode
        self.engine_version = engine_version
        self.factory = OperatorFactory()
        self.factory.register("OP_GENESIS")(op_genesis)
        self.factory.register("OP_S_PHASE")(op_s_phase)
        self.factory.register("OP_L_STIFF")(op_l_stiff)
        self.factory.register("OP_DISSIPATION")(op_dissipation)
        self.factory.register("OP_TAU_COUPLING")(op_tau_coupling)
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

        state = {
            "a": float(input_state.get("a", 1.0)),
            "H": float(input_state.get("H", 0.0)),
            "rho": float(input_state.get("rho", 1.0)),
            "p": float(input_state.get("p", 0.0)),
            "M_X": float(input_state.get("M_X", 0.0)),
            "tau_eff": float(input_state.get("tau_eff", self.canon.get_value("tau0"))),
        }

        hz_z: List[float] = []
        hz_H: List[float] = []

        alpha = self.canon.get_value("alpha_mem")
        C_rho = self.canon.get_value("C_rho")
        C_k = self.canon.get_value("C_k")
        K0 = self.canon.get_value("k0")
        w = self.canon.get_value("w")

        def rhs(_t: float, y: Dict[str, float]) -> Dict[str, float]:
            a = y["a"]
            rho = y["rho"]
            p = y.get("p", w * rho)
            tau_eff = y.get("tau_eff", self.canon.get_value("tau0"))
            M_X = y["M_X"]

            H_base2 = (C_rho * rho) + (C_k * K0 / (a * a))
            X = H_base2
            dMdt = (X - M_X) / max(tau_eff, 1e-30)

            H2 = (1.0 - alpha) * H_base2 + alpha * M_X
            H2 = max(H2, 0.0)
            H_new = math.sqrt(H2)

            drhodt = -3.0 * H_new * (rho + p)
            dadt = a * H_new
            dHdt = 0.0

            return {"a": dadt, "H": dHdt, "rho": drhodt, "p": 0.0, "M_X": dMdt, "tau_eff": 0.0}

        context = {
            "dt_years": dt_years,
            "step_index": 0,
            "warnings": cert["run_trace"]["warnings"],
            "determinism_mode": self.determinism_mode,
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

        t = 0.0
        for i in range(steps):
            context["step_index"] = i
            for op in self.canon.operators:
                op_def = self.canon.operator_defs.get(op.stack_key, {})
                if op_def.get("bootstrap_only", False):
                    continue
                fn = self.factory.get(op.stack_key)
                state, _ = fn(self.canon, state, context)
                if op.op_id not in cert["run_trace"]["operators_executed_ids"]:
                    cert["run_trace"]["operators_executed_ids"].append(op.op_id)
                cert["run_trace"]["operator_execution_counts"][op.op_id] += 1

            if integrator.upper() == "RK4":
                state = _rk4_step(rhs, t, state, dt_years)
            else:
                dy = rhs(t, state)
                state = {k: state[k] + dt_years * dy.get(k, 0.0) for k in state}

            a = state["a"]
            rho = state["rho"]
            M_X = state["M_X"]
            H_base2 = (C_rho * rho) + (C_k * K0 / (a * a))
            H2 = (1.0 - alpha) * H_base2 + alpha * M_X
            state["H"] = math.sqrt(max(H2, 0.0))

            z = (1.0 / state["a"]) - 1.0
            hz_z.append(z)
            hz_H.append(state["H"])

            if self.canon.numeric_policy.get("strict_nan_check", True):
                for k, v in state.items():
                    if isinstance(v, (int, float)) and not is_finite(float(v)):
                        raise ValueError(f"Non-finite state detected at step {i}: {k}={v}")

            t += dt_years

        cert["run_trace"]["steps_computed"] = steps

        outputs = {
            "final_state": state,
            "OBS_HZ_001": {
                "z": hz_z,
                "H": hz_H,
            },
        }

        cert = finalize_certificate(cert, outputs, observables_emitted=["OBS_HZ_001"])
        cert = add_repro_hash(cert)
        return outputs, cert
