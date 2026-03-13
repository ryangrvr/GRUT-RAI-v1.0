from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.canon import GRUTCanon
from grut.canon_override import override_canon
from grut.engine import GRUTEngine
from grut.conversion import find_z0_index


def _vacuum_threshold(canon: GRUTCanon) -> float:
    C_rho = canon.get_value("C_rho")
    C_k = canon.get_value("C_k")
    K0 = canon.get_value("k0")
    return -(C_k * K0) / max(C_rho, 1e-30)


def _preset_init(
    preset: str,
    canon: GRUTCanon,
    *,
    rho0_vac: Optional[float] = None,
    rho_m0: Optional[float] = None,
) -> Dict[str, Any]:
    if preset == "matter_only":
        return {
            "init_state": {
                "a": 1.0,
                "rho": 0.2,
                "p": 0.0,
                "rho_m0": 0.2,
                "H": 1e-10,
                "M_X": 0.0,
            },
            "assumptions": {"growth_enabled": True, "diagnostics": True},
        }
    if preset == "vacuum_plus_matter":
        threshold = _vacuum_threshold(canon)
        rho_m0_val = 0.05 if rho_m0 is None else float(rho_m0)
        rho0_vac_val = (threshold * 5.0) if rho0_vac is None else float(rho0_vac)
        rho_total0 = rho0_vac_val + rho_m0_val
        p_total0 = -rho0_vac_val
        return {
            "init_state": {
                "a": 1.0,
                "rho": rho_total0,
                "p": p_total0,
                "rho_m0": rho_m0_val,
                "rho0_vac": rho0_vac_val,
                "rho_total0": rho_total0,
                "p_total0": p_total0,
                "rho_threshold_min": threshold,
                "H": 1e-10,
                "M_X": 0.0,
            },
            "assumptions": {"growth_enabled": True, "diagnostics": True},
        }
    raise ValueError(f"Unknown preset: {preset}")


def diagnose_preset_viability(
    *,
    canon_path: str,
    alpha_mem: float,
    start_z: float,
    dt_years: float,
    steps: int,
    outdir: str,
    vacuum_rho0_vac: Optional[float] = None,
    vacuum_rho_m0: Optional[float] = None,
    vacuum_valid_z_max: Optional[float] = 1.0,
) -> Dict[str, Any]:
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    canon_base = GRUTCanon(canon_path)
    report: Dict[str, Any] = {
        "alpha_mem": alpha_mem,
        "run_config": {
            "start_z": start_z,
            "dt_years": dt_years,
            "steps": steps,
            "integrator": "RK4",
        },
        "presets": {},
    }

    for preset in ["matter_only", "vacuum_plus_matter"]:
        canon = override_canon(canon_base, {"alpha_mem": alpha_mem})
        engine = GRUTEngine(canon, determinism_mode="STRICT")
        preset_cfg = _preset_init(
            preset,
            canon,
            rho0_vac=vacuum_rho0_vac,
            rho_m0=vacuum_rho_m0,
        )
        run_config = {
            "dt_years": dt_years,
            "steps": steps,
            "integrator": "RK4",
            "start_z": start_z,
            "rho_is_rho0": True,
        }
        if preset == "vacuum_plus_matter" and vacuum_valid_z_max is not None:
            run_config["valid_z_max"] = float(vacuum_valid_z_max)

        outputs, cert = engine.run(
            preset_cfg["init_state"],
            run_config=run_config,
            assumption_toggles=preset_cfg["assumptions"],
        )

        hz = outputs.get("OBS_HZ_001", {})
        z_vals = list(hz.get("z", []))
        H_vals = list(hz.get("H", []))
        idx0 = find_z0_index(z_vals)
        H0_code = H_vals[idx0] if idx0 is not None and H_vals else None
        z0 = z_vals[idx0] if idx0 is not None and z_vals else None

        diagnostics = outputs.get("diagnostics", {})
        H_base2 = diagnostics.get("H_base2", [])
        M_X = diagnostics.get("M_X", [])
        H2_raw = diagnostics.get("H2_raw", [])
        H2_neg_count = diagnostics.get("H2_negative_count")
        H2_neg_first_idx = diagnostics.get("H2_negative_first_index")
        H2_neg_first_z = diagnostics.get("H2_negative_first_z")
        H2_neg_above_valid = diagnostics.get("H2_negative_count_above_valid_z_max")
        hbase_z0 = H_base2[idx0] if idx0 is not None and idx0 < len(H_base2) else None
        mx_z0 = M_X[idx0] if idx0 is not None and idx0 < len(M_X) else None
        h2_z0 = H2_raw[idx0] if idx0 is not None and idx0 < len(H2_raw) else None

        report["presets"][preset] = {
            "canon_hash": cert.get("engine_signature", {}).get("canon_hash"),
            "repro_hash": cert.get("repro_hash"),
            "output_digest": cert.get("outputs", {}).get("output_digest"),
            "initial_conditions": cert.get("initial_conditions", {}),
            "H0_code": H0_code,
            "idx0": idx0,
            "z0": z0,
            "H_base2_z0": hbase_z0,
            "M_X_z0": mx_z0,
            "H2_raw_z0": h2_z0,
            "H_floor_count": cert.get("run_trace", {}).get("H_floor_count"),
            "H2_negative_count": H2_neg_count,
            "H2_negative_first_index": H2_neg_first_idx,
            "H2_negative_first_z": H2_neg_first_z,
            "H2_negative_count_above_valid_z_max": H2_neg_above_valid,
            "warnings": cert.get("run_trace", {}).get("warnings", []),
        }

    report_path = outdir_path / "preset_viability_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose preset viability")
    parser.add_argument("--canon", default="canon/grut_canon_v0.3.json")
    parser.add_argument("--alpha_mem", type=float, default=0.333333333)
    parser.add_argument("--start_z", type=float, default=2.0)
    parser.add_argument("--dt_years", type=float, default=1e5)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--outdir", default="artifacts/diagnostics")
    parser.add_argument("--vacuum_rho0_vac", type=float, default=None)
    parser.add_argument("--vacuum_rho_m0", type=float, default=None)
    parser.add_argument("--vacuum_valid_z_max", type=float, default=1.0)
    args = parser.parse_args()

    diagnose_preset_viability(
        canon_path=args.canon,
        alpha_mem=args.alpha_mem,
        start_z=args.start_z,
        dt_years=args.dt_years,
        steps=args.steps,
        outdir=args.outdir,
        vacuum_rho0_vac=args.vacuum_rho0_vac,
        vacuum_rho_m0=args.vacuum_rho_m0,
        vacuum_valid_z_max=args.vacuum_valid_z_max,
    )


if __name__ == "__main__":
    main()
