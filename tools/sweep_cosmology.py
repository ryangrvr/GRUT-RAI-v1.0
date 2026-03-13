from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.canon import GRUTCanon
from grut.canon_override import override_canon
from grut.engine import GRUTEngine
from tools.audit_schemas import SweepManifest


def _parse_grid(grid: str) -> List[float]:
    return [float(x.strip()) for x in grid.split(",") if x.strip()]


def _safe_name(value: float) -> str:
    s = str(value)
    return s.replace("-", "m").replace(".", "p")


def _closest_index(z_values: List[float]) -> Optional[int]:
    if not z_values:
        return None
    return min(range(len(z_values)), key=lambda i: abs(z_values[i]))


def _vacuum_threshold(canon: GRUTCanon) -> float:
    C_rho = canon.get_value("C_rho")
    C_k = canon.get_value("C_k")
    K0 = canon.get_value("k0")
    return -(C_k * K0) / max(C_rho, 1e-30)


def _is_finite(x: Optional[float]) -> bool:
    return x is not None and math.isfinite(x)


def _validate_outputs(outputs: Dict[str, Any], steps: int) -> None:
    hz = outputs.get("OBS_HZ_001", {})
    z_vals = list(hz.get("z", []))
    H_vals = list(hz.get("H", []))
    if len(z_vals) != len(H_vals):
        raise ValueError("H(z) array length mismatch")
    if len(z_vals) != steps:
        raise ValueError("H(z) array length does not match steps")
    if any(not _is_finite(v) for v in z_vals):
        raise ValueError("Non-finite z values in H(z) output")
    if any(not _is_finite(v) for v in H_vals):
        raise ValueError("Non-finite H values in H(z) output")

    fs8 = outputs.get("OBS_FS8_001")
    if fs8:
        fs8_vals = list(fs8.get("fsigma8", []))
        fs8_mask = list(fs8.get("fs8_mask", []))
        if len(fs8_vals) != len(z_vals):
            raise ValueError("fsigma8 length does not match H(z)")
        if len(fs8_mask) not in (0, len(z_vals)):
            raise ValueError("fs8_mask length does not match H(z)")
        if not fs8_mask:
            fs8_mask = [False] * len(fs8_vals)
        for v, m in zip(fs8_vals, fs8_mask):
            if m:
                continue
            if v is None or not _is_finite(float(v)):
                raise ValueError("Non-finite fsigma8 value in unmasked output")


def _summarize_run(outputs: Dict[str, Any], cert: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    hz = outputs.get("OBS_HZ_001", {})
    fs8 = outputs.get("OBS_FS8_001")
    init = cert.get("initial_conditions", {})

    z_vals = list(hz.get("z", []))
    H_vals = list(hz.get("H", []))
    z_start = z_vals[0] if z_vals else None
    z_end = z_vals[-1] if z_vals else None

    hz_idx = _closest_index(z_vals)
    H_z0 = H_vals[hz_idx] if hz_idx is not None and H_vals else None
    H0_code = H_z0
    z0 = z_vals[hz_idx] if hz_idx is not None and z_vals else None
    valid_z_max = cert.get("run_trace", {}).get("valid_z_max")
    out_of_domain_fraction = None
    if z_vals and valid_z_max is not None:
        out_of_domain_fraction = sum(1 for z in z_vals if z > float(valid_z_max)) / len(z_vals)

    viable = (H0_code == H0_code) and (H0_code is not None) and (H0_code > 0.0)
    if not viable:
        status = "NOT_VIABLE_AT_Z0"
        failure_reason = "H0_code_nonpositive_or_nonfinite"
    elif valid_z_max is not None and float(init.get("start_z_used", 0.0)) > float(valid_z_max):
        status = "OUT_OF_DOMAIN_HIGH_Z"
        failure_reason = "start_z_above_valid_z_max"
    else:
        status = "VIABLE"
        failure_reason = None

    H_floor = 1e-12
    H_floor_count = sum(1 for h in H_vals if h < H_floor)

    fs8_min = fs8_max = fs8_z0 = None
    fs8_min_unmasked = fs8_max_unmasked = fs8_z0_unmasked = None
    fs8_min_compare = fs8_max_compare = fs8_z0_compare = None
    compare_point_count = 0
    compare_definition = None
    fs8_masked_count = None
    D0_index = D0 = sigma8_0 = None
    fs8_payload: Dict[str, Any] = {}
    if fs8:
        fs8_vals = list(fs8.get("fsigma8", []))
        fs8_z = list(fs8.get("z", []))
        fs8_mask = list(fs8.get("fs8_mask", []))
        fs8_masked_count = sum(1 for m in fs8_mask if m)
        compare_mask = list(fs8.get("compare_mask", []))
        if not compare_mask and fs8_z:
            compare_definition = (
                "compare mask: z in [0, start_z] AND H > 10*H_floor AND fsigma8 not None"
            )
            compare_mask = []
            for i, (z_val, v, m) in enumerate(zip(fs8_z, fs8_vals, fs8_mask)):
                H_val = H_vals[i] if i < len(H_vals) else 0.0
                in_domain = True
                if valid_z_max is not None and z_val is not None:
                    in_domain = z_val <= float(valid_z_max)
                compare_mask.append(
                    (z_val is not None)
                    and (0.0 <= z_val <= float(init.get("start_z_used", z_val)))
                    and in_domain
                    and (H_val > (10.0 * H_floor))
                    and (v is not None)
                    and (not m)
                )
        else:
            compare_definition = cert.get("run_trace", {}).get("compare_definition")

        fs8_vals_clean = [v for v in fs8_vals if v is not None]
        fs8_min = min(fs8_vals_clean) if fs8_vals_clean else None
        fs8_max = max(fs8_vals_clean) if fs8_vals_clean else None
        fs8_idx = _closest_index(list(fs8.get("z", [])))
        if fs8_idx is not None and fs8_vals:
            fs8_z0 = fs8_vals[fs8_idx]
            D0_index = fs8_idx

        unmasked = [
            (z, v)
            for z, v, m in zip(fs8_z, fs8_vals, fs8_mask)
            if (v is not None) and (not m)
        ]
        if unmasked:
            unmasked_vals = [v for _, v in unmasked]
            fs8_min_unmasked = min(unmasked_vals)
            fs8_max_unmasked = max(unmasked_vals)
            z0_idx = min(range(len(unmasked)), key=lambda i: abs(unmasked[i][0]))
            fs8_z0_unmasked = unmasked[z0_idx][1]

        if status == "VIABLE":
            compare = [
                (z, v)
                for z, v, m in zip(fs8_z, fs8_vals, compare_mask)
                if (v is not None) and m
            ]
            compare_point_count = len(compare)
            if compare:
                compare_vals = [v for _, v in compare]
                fs8_min_compare = min(compare_vals)
                fs8_max_compare = max(compare_vals)
                z0_idx = min(range(len(compare)), key=lambda i: abs(compare[i][0]))
                fs8_z0_compare = compare[z0_idx][1]
        else:
            compare_point_count = 0
            fs8_min_compare = None
            fs8_max_compare = None
            fs8_z0_compare = None

        fs8_payload = {
            "fs8_vals": fs8_vals,
            "fs8_z": fs8_z,
            "fs8_mask": fs8_mask,
        }
        D0 = cert.get("run_trace", {}).get("growth_D0")
        sigma8_0 = cert.get("run_trace", {}).get("growth_sigma8_0")

    final_state = outputs.get("final_state", {})

    summary = {
        "canon_hash": cert.get("engine_signature", {}).get("canon_hash"),
        "repro_hash": cert.get("repro_hash"),
        "output_digest": cert.get("outputs", {}).get("output_digest"),
        "rho_init_used": init.get("rho_init_used"),
        "p_init_used": init.get("p_init_used"),
        "w_effective_init": init.get("w_effective_init"),
        "start_z_used": init.get("start_z_used"),
        "a_init_used": init.get("a_init_used"),
        "genesis_mode": init.get("genesis_mode"),
        "a_end": final_state.get("a"),
        "H_end": final_state.get("H"),
        "rho_end": final_state.get("rho"),
        "rho_m_end": final_state.get("rho_m"),
        "M_X_end": final_state.get("M_X"),
        "H_min": min(H_vals) if H_vals else None,
        "H_max": max(H_vals) if H_vals else None,
        "H_z0": H_z0,
        "H0_code": H0_code,
        "idx0": hz_idx,
        "z0": z0,
        "status": status,
        "failure_reason": failure_reason,
        "valid_z_max": valid_z_max,
        "out_of_domain_fraction": out_of_domain_fraction,
        "H_floor_count": H_floor_count,
        "z_start": z_start,
        "z_end": z_end,
        "fs8_min": fs8_min,
        "fs8_max": fs8_max,
        "fs8_z0": fs8_z0,
        "fs8_masked_count": fs8_masked_count,
        "fs8_min_unmasked": fs8_min_unmasked,
        "fs8_max_unmasked": fs8_max_unmasked,
        "fs8_z0_unmasked": fs8_z0_unmasked,
        "fs8_min_compare": fs8_min_compare,
        "fs8_max_compare": fs8_max_compare,
        "fs8_z0_compare": fs8_z0_compare,
        "compare_point_count": compare_point_count,
        "compare_definition": compare_definition,
        "D0_index": D0_index,
        "D0": D0,
        "sigma8_0": sigma8_0,
        "rho_m0_input": init.get("rho_m0_input"),
        "rho_m_init_used": init.get("rho_m_init_used"),
    }
    payload = {
        "H_vals": H_vals,
        **fs8_payload,
    }
    return summary, payload


def run_sweep(
    *,
    canon_path: str,
    param: str,
    grid: List[float],
    start_z: float,
    rho0: float,
    p: float,
    rho_m0: Optional[float] = None,
    rho0_vac: Optional[float] = None,
    rho_threshold_min: Optional[float] = None,
    rho_total0: Optional[float] = None,
    p_total0: Optional[float] = None,
    valid_z_max: Optional[float] = None,
    rho_m_init: Optional[float] = None,
    dt_years: float,
    steps: int,
    outdir: str,
    rho_is_rho0: bool = True,
) -> Dict[str, Any]:
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    canon = GRUTCanon(canon_path)
    run_folders: List[str] = []
    run_dirs: List[Path] = []
    results: List[Dict[str, Any]] = []
    payloads: List[Dict[str, Any]] = []
    certs: List[Dict[str, Any]] = []

    for idx, value in enumerate(grid):
        overridden = override_canon(canon, {param: value})
        engine = GRUTEngine(overridden, determinism_mode="STRICT")

        init_state = {
            "a": 1.0,
            "rho": rho0,
            "p": p,
            "H": 1e-10,
            "M_X": 0.0,
        }
        if rho0_vac is not None:
            init_state["rho0_vac"] = rho0_vac
        if rho_total0 is not None:
            init_state["rho_total0"] = rho_total0
        if p_total0 is not None:
            init_state["p_total0"] = p_total0
        if rho_threshold_min is not None:
            init_state["rho_threshold_min"] = rho_threshold_min
        if rho_m0 is not None:
            init_state["rho_m0"] = rho_m0
        if rho_m_init is not None:
            init_state["rho_m"] = rho_m_init
            init_state["rho_at_start"] = True
        run_config = {
            "dt_years": dt_years,
            "steps": steps,
            "integrator": "RK4",
            "start_z": start_z,
            "rho_is_rho0": rho_is_rho0,
        }
        if valid_z_max is not None:
            run_config["valid_z_max"] = float(valid_z_max)

        outputs, cert = engine.run(
            init_state,
            run_config=run_config,
            assumption_toggles={"deterministic_run": True, "growth_enabled": True},
        )
        _validate_outputs(outputs, steps)

        summary, payload = _summarize_run(outputs, cert)
        summary.update(
            {
                "param": param,
                "value": value,
                "run_index": idx,
            }
        )
        results.append(summary)
        payloads.append(payload)
        certs.append(cert)

        run_dir = outdir_path / f"run_{idx}_{param}_{_safe_name(value)}"
        run_dir.mkdir(parents=True, exist_ok=True)
        run_folders.append(str(run_dir))
        run_dirs.append(run_dir)

        (run_dir / "certificate.json").write_text(json.dumps(cert, indent=2))
        (run_dir / "outputs.json").write_text(json.dumps(outputs))
        (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    if results and payloads:
        baseline = payloads[0]
        baseline_H = baseline.get("H_vals", [])
        baseline_fs8 = baseline.get("fs8_vals", [])
        baseline_fs8_mask = baseline.get("fs8_mask", [])
        rms_definition = (
            "rms = sqrt(mean((x_i - x_i_baseline)^2)); fs8 uses aligned points where "
            "both baseline and run are unmasked and fsigma8 is not None"
        )
        for idx, (row, payload) in enumerate(zip(results, payloads)):
            H_vals = payload.get("H_vals", [])
            n_h = min(len(baseline_H), len(H_vals))
            if n_h:
                rms_H = math.sqrt(
                    sum((H_vals[i] - baseline_H[i]) ** 2 for i in range(n_h)) / n_h
                )
            else:
                rms_H = None

            fs8_vals = payload.get("fs8_vals", [])
            fs8_mask = payload.get("fs8_mask", [])
            n_fs8 = min(len(baseline_fs8), len(fs8_vals), len(baseline_fs8_mask), len(fs8_mask))
            fs8_diffs = []
            for i in range(n_fs8):
                if baseline_fs8_mask[i] or fs8_mask[i]:
                    continue
                if baseline_fs8[i] is None or fs8_vals[i] is None:
                    continue
                fs8_diffs.append(fs8_vals[i] - baseline_fs8[i])
            rms_fs8 = math.sqrt(sum(d * d for d in fs8_diffs) / len(fs8_diffs)) if fs8_diffs else None

            row["rms_H_vs_baseline"] = rms_H
            row["rms_fs8_vs_baseline"] = rms_fs8
            row["rms_definition"] = rms_definition
            row["rms_n_points"] = {"H": n_h, "fs8": len(fs8_diffs)}

            run_dir = run_dirs[idx]
            (run_dir / "summary.json").write_text(json.dumps(row, indent=2))

            cert = certs[idx]
            cert.setdefault("run_trace", {})
            cert["run_trace"]["rms_definition"] = rms_definition
            cert["run_trace"]["rms_n_points"] = {"H": n_h, "fs8": len(fs8_diffs)}
            (run_dir / "certificate.json").write_text(json.dumps(cert, indent=2))

    jsonl_path = outdir_path / "sweep_results.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, sort_keys=True))
            f.write("\n")

    fieldnames = list(results[0].keys()) if results else []
    csv_path = outdir_path / "sweep_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    manifest = {
        "sweep": {
            "param": param,
            "grid": grid,
            "run_config": {
                "dt_years": dt_years,
                "steps": steps,
                "integrator": "RK4",
                "start_z": start_z,
                "rho_is_rho0": rho_is_rho0,
            },
            "init_state": {
                "a": 1.0,
                "rho": rho0,
                "p": p,
                "H": 1e-10,
                "M_X": 0.0,
                "rho_m0": rho_m0,
                "rho0_vac": rho0_vac,
                "rho_total0": rho_total0,
                "p_total0": p_total0,
                "rho_threshold_min": rho_threshold_min,
                "rho_m_init": rho_m_init,
            },
            "valid_z_max": valid_z_max,
            "canon": canon_path,
        },
        "run_folders": run_folders,
    }
    SweepManifest.model_validate(manifest)
    (outdir_path / "manifest.json").write_text(json.dumps(manifest, indent=2))

    try:
        import matplotlib.pyplot as plt

        if results:
            plt.figure()
            for row in results:
                run_dir = outdir_path / f"run_{row['run_index']}_{param}_{_safe_name(row['value'])}"
                outputs = json.loads((run_dir / "outputs.json").read_text())
                hz = outputs.get("OBS_HZ_001", {})
                plt.plot(hz.get("z", []), hz.get("H", []), label=f"{param}={row['value']}")
            plt.xlabel("z")
            plt.ylabel("H(z)")
            plt.title("H(z) sweep")
            plt.legend(fontsize=8)
            plt.savefig(outdir_path / "plot_Hz_vs_z.png", dpi=160)

            plt.figure()
            for row in results:
                run_dir = outdir_path / f"run_{row['run_index']}_{param}_{_safe_name(row['value'])}"
                outputs = json.loads((run_dir / "outputs.json").read_text())
                fs8 = outputs.get("OBS_FS8_001", {})
                plt.plot(fs8.get("z", []), fs8.get("fsigma8", []), label=f"{param}={row['value']}")
            plt.xlabel("z")
            plt.ylabel("fσ8(z)")
            plt.title("fσ8(z) sweep")
            plt.legend(fontsize=8)
            plt.savefig(outdir_path / "plot_fs8_vs_z.png", dpi=160)
    except Exception:
        pass

    return {"results": results, "manifest": manifest}


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic cosmology sweep runner")
    parser.add_argument("--canon", default="canon/grut_canon_v0.3.json")
    parser.add_argument("--param", default="alpha_mem")
    parser.add_argument("--grid", required=True)
    parser.add_argument("--preset", choices=["vacuum_plus_matter", "matter_only"], default=None)
    parser.add_argument("--start_z", type=float, default=2.0)
    parser.add_argument("--rho0", type=float, default=0.2)
    parser.add_argument("--p", type=float, default=-0.2)
    parser.add_argument("--rho_m0", type=float, default=None)
    parser.add_argument("--rho0_vac", type=float, default=None)
    parser.add_argument("--valid_z_max", type=float, default=None)
    parser.add_argument("--dt_years", type=float, default=1e5)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--outdir", default=None)
    parser.add_argument("--rho_is_rho0", type=str, default="true")
    args = parser.parse_args()

    rho_is_rho0 = str(args.rho_is_rho0).strip().lower() in {"1", "true", "yes", "y"}
    grid = _parse_grid(args.grid)
    rho_threshold_min = None
    rho_total0 = None
    p_total0 = None
    rho_m_init = None
    valid_z_max = args.valid_z_max
    if args.preset == "vacuum_plus_matter":
        canon = GRUTCanon(args.canon)
        rho_threshold_min = _vacuum_threshold(canon)
        rho_m0_val = 0.05 if args.rho_m0 is None else float(args.rho_m0)
        rho0_vac_val = (rho_threshold_min * 5.0) if args.rho0_vac is None else float(args.rho0_vac)
        a_init = 1.0 / (1.0 + float(args.start_z))
        rho_vac_init = rho0_vac_val
        rho_m_init = rho_m0_val * (a_init ** -3.0)
        rho_total_init = rho_vac_init + rho_m_init
        p_total_init = -rho_vac_init
        args.rho0 = rho_total_init
        args.p = p_total_init
        args.rho_m0 = rho_m0_val
        args.rho0_vac = rho0_vac_val
        rho_total0 = rho_total_init
        p_total0 = p_total_init
        if valid_z_max is None:
            valid_z_max = None
        if args.outdir is None:
            args.outdir = "artifacts/sweeps/alpha_mem_growth_quick"
    elif args.preset == "matter_only":
        args.rho0 = 0.2
        args.p = 0.0
        args.rho_m0 = 0.2
        if args.outdir is None:
            args.outdir = "artifacts/sweeps/alpha_mem_matter_baseline"

    if args.outdir is None:
        raise ValueError("--outdir is required when --preset is not provided")
    run_sweep(
        canon_path=args.canon,
        param=args.param,
        grid=grid,
        start_z=args.start_z,
        rho0=args.rho0,
        p=args.p,
        rho_m0=args.rho_m0,
        rho0_vac=args.rho0_vac,
        rho_threshold_min=rho_threshold_min,
        rho_total0=rho_total0,
        p_total0=p_total0,
        valid_z_max=valid_z_max,
        rho_m_init=rho_m_init if args.preset == "vacuum_plus_matter" else None,
        dt_years=args.dt_years,
        steps=args.steps,
        outdir=args.outdir,
        rho_is_rho0=rho_is_rho0,
    )


if __name__ == "__main__":
    main()
