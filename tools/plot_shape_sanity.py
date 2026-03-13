from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.canon import GRUTCanon
from grut.canon_override import override_canon
from grut.engine import GRUTEngine
from grut.conversion import compute_Ez, find_z0_index


PRESETS = ["matter_only", "vacuum_plus_matter"]


def _vacuum_threshold(canon: GRUTCanon) -> float:
    C_rho = canon.get_value("C_rho")
    C_k = canon.get_value("C_k")
    K0 = canon.get_value("k0")
    return -(C_k * K0) / max(C_rho, 1e-30)


def _preset_init(
    preset: str,
    canon: GRUTCanon,
    *,
    start_z: float,
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
            "assumptions": {"growth_enabled": True},
        }
    if preset == "vacuum_plus_matter":
        threshold = _vacuum_threshold(canon)
        rho_m0_val = 0.05 if rho_m0 is None else float(rho_m0)
        rho0_vac_val = (threshold * 5.0) if rho0_vac is None else float(rho0_vac)
        a_init = 1.0 / (1.0 + float(start_z))
        rho_vac_init = rho0_vac_val
        rho_m_init = rho_m0_val * (a_init ** -3.0)
        rho_total_init = rho_vac_init + rho_m_init
        p_total_init = -rho_vac_init
        C_rho = canon.get_value("C_rho")
        C_k = canon.get_value("C_k")
        K0 = canon.get_value("k0")
        curv_term = (C_k * K0) / (a_init * a_init)
        base_term = C_rho * rho_total_init
        denom = max(C_rho * (a_init ** -3.0), 1e-30)
        rho_m0_min = max(0.0, (-(curv_term) - (C_rho * rho0_vac_val)) / denom)
        return {
            "init_state": {
                "a": 1.0,
                "rho": rho_total_init,
                "p": p_total_init,
                "rho_m": rho_m_init,
                "rho_m0": rho_m0_val,
                "rho0_vac": rho0_vac_val,
                "rho_vac_init": rho_vac_init,
                "rho_m_init": rho_m_init,
                "rho_total_init": rho_total_init,
                "p_total_init": p_total_init,
                "rho_threshold_min": threshold,
                "rho_m0_min": rho_m0_min,
                "curv_term": curv_term,
                "base_term": base_term,
                "rho_at_start": True,
                "H": 1e-10,
                "M_X": 0.0,
            },
            "assumptions": {"growth_enabled": True},
        }
    raise ValueError(f"Unknown preset: {preset}")


def _write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_shape_sanity(
    *,
    canon_path: str,
    alpha_mem: float,
    start_z: float,
    dt_years: float,
    steps: int,
    outdir: str,
    vacuum_rho0_vac: Optional[float] = None,
    vacuum_rho_m0: Optional[float] = None,
    vacuum_valid_z_max: Optional[float] = None,
) -> Dict[str, Any]:
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)

    canon_base = GRUTCanon(canon_path)
    results: Dict[str, Any] = {
        "presets": [],
        "run_config": {
            "start_z": start_z,
            "dt_years": dt_years,
            "steps": steps,
            "integrator": "RK4",
        },
        "alpha_mem": alpha_mem,
        "presets_meta": {},
        "presets_status": {},
        "compare_definition": None,
    }

    series_E: Dict[str, Tuple[List[float], List[float]]] = {}
    series_fs8: Dict[str, Tuple[List[float], List[float]]] = {}

    for preset in PRESETS:
        canon = override_canon(canon_base, {"alpha_mem": alpha_mem})
        engine = GRUTEngine(canon, determinism_mode="STRICT")
        preset_cfg = _preset_init(
            preset,
            canon,
            start_z=start_z,
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
        H_code = list(hz.get("H", []))
        idx0 = find_z0_index(z_vals)
        if idx0 is None:
            raise ValueError("No z values to compute H0")
        H0_code = H_code[idx0]
        z0 = z_vals[idx0] if idx0 < len(z_vals) else None
        viable = (H0_code == H0_code) and (H0_code is not None) and (H0_code > 0.0)
        valid_z_max = run_config.get("valid_z_max")
        if not viable:
            status = "NOT_VIABLE_AT_Z0"
            failure_reason = "H0_code_nonpositive_or_nonfinite"
        elif valid_z_max is not None and start_z > float(valid_z_max):
            status = "OUT_OF_DOMAIN_HIGH_Z"
            failure_reason = "start_z_above_valid_z_max"
        else:
            status = "VIABLE"
            failure_reason = None
        if viable:
            E_z = compute_Ez(H_code, idx0)
            ez_rows = [{"z": z, "H_code": h, "E_z": e} for z, h, e in zip(z_vals, H_code, E_z)]
            _write_csv(outdir_path / f"{preset}_Ez.csv", ["z", "H_code", "E_z"], ez_rows)

        fs8 = outputs.get("OBS_FS8_001") or {}
        fs8_z = list(fs8.get("z", []))
        fs8_vals = list(fs8.get("fsigma8", []))
        compare_mask = list(fs8.get("compare_mask", []))
        if not compare_mask:
            compare_mask = [False] * len(fs8_vals)
        fs8_rows = []
        compare_count = 0
        fs8_plot_z: List[float] = []
        fs8_plot_vals: List[float] = []
        if viable:
            for z, v, cm in zip(fs8_z, fs8_vals, compare_mask):
                in_domain = True
                if valid_z_max is not None:
                    in_domain = z <= float(valid_z_max)
                fs8_rows.append({"z": z, "fsigma8_compare": v if (cm and in_domain) else None})
                if cm and in_domain and v is not None:
                    fs8_plot_z.append(z)
                    fs8_plot_vals.append(v)
                    compare_count += 1

            _write_csv(outdir_path / f"{preset}_fs8_compare.csv", ["z", "fsigma8_compare"], fs8_rows)

        meta = {
            "canon_hash": cert.get("engine_signature", {}).get("canon_hash"),
            "repro_hash": cert.get("repro_hash"),
            "output_digest": cert.get("outputs", {}).get("output_digest"),
            "H0_code": H0_code,
            "idx0": idx0,
            "z0": z0,
            "status": status,
            "failure_reason": failure_reason,
            "compare_point_count": compare_count,
            "valid_z_max": valid_z_max,
        }
        (outdir_path / f"{preset}_meta.json").write_text(json.dumps(meta, indent=2))

        results["presets"].append(preset)
        results["presets_meta"][preset] = meta
        results["presets_status"][preset] = status
        if results["compare_definition"] is None:
            results["compare_definition"] = cert.get("run_trace", {}).get("compare_definition")

        if viable:
            series_E[preset] = (z_vals, [float(e) for e in E_z])
        series_fs8[preset] = (fs8_plot_z, fs8_plot_vals)

    try:
        import matplotlib.pyplot as plt

        plt.figure()
        for preset, (z_vals, E_vals) in series_E.items():
            plt.plot(z_vals, E_vals, label=preset)
        plt.xlabel("z")
        plt.ylabel("E(z) = H/H0")
        plt.title("Anchor-free E(z)")
        plt.legend(fontsize=8)
        plt.savefig(outdir_path / "Ez_overlay.png", dpi=160)
        plt.close()

        plt.figure()
        for preset, (z_vals, fs8_vals) in series_fs8.items():
            if z_vals and fs8_vals:
                plt.plot(z_vals, fs8_vals, label=preset)
        plt.xlabel("z")
        plt.ylabel("fσ8 (compare window)")
        plt.title("Compare-window fσ8")
        plt.legend(fontsize=8)
        plt.savefig(outdir_path / "fs8_compare_overlay.png", dpi=160)
        plt.close()
    except Exception:
        pass

    (outdir_path / "shape_sanity_manifest.json").write_text(json.dumps(results, indent=2))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Shape sanity plots for E(z) and fσ8")
    parser.add_argument("--canon", default="canon/grut_canon_v0.3.json")
    parser.add_argument("--alpha_mem", type=float, default=0.333333333)
    parser.add_argument("--start_z", type=float, default=2.0)
    parser.add_argument("--dt_years", type=float, default=1e5)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--outdir", default="artifacts/shape_sanity")
    parser.add_argument("--vacuum_rho0_vac", type=float, default=None)
    parser.add_argument("--vacuum_rho_m0", type=float, default=None)
    parser.add_argument("--vacuum_valid_z_max", type=float, default=None)
    args = parser.parse_args()

    run_shape_sanity(
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
