from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.canon import GRUTCanon
from grut.engine import GRUTEngine
from grut.conversion import build_policy, compute_Ez, convert_H, find_z0_index
from grut.canon_override import override_canon
from tools.audit_schemas import CalibrationManifest


ANCHORS = [
    {"name": "Planck_67p4", "H0": 67.4},
    {"name": "SH0ES_73p0", "H0": 73.0},
]


def _write_csv_with_header(path: Path, header_lines: List[str], fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        for line in header_lines:
            f.write(f"# {line}\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _vacuum_threshold(canon: GRUTCanon) -> float:
    C_rho = canon.get_value("C_rho")
    C_k = canon.get_value("C_k")
    K0 = canon.get_value("k0")
    return -(C_k * K0) / max(C_rho, 1e-30)


def _is_finite(x: Optional[float]) -> bool:
    return x is not None and math.isfinite(x)


def _validate_cosmology_arrays(
    *,
    z_vals: List[float],
    H_vals: List[float],
    steps: int,
    fs8: Optional[Dict[str, Any]],
) -> None:
    if len(z_vals) != len(H_vals):
        raise ValueError("H(z) array length mismatch")
    if len(z_vals) != steps:
        raise ValueError("H(z) array length does not match steps")
    if any(not _is_finite(v) for v in z_vals):
        raise ValueError("Non-finite z values in H(z) output")
    if any(not _is_finite(v) for v in H_vals):
        raise ValueError("Non-finite H values in H(z) output")
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


def _preset_init(
    preset: str,
    canon: GRUTCanon,
    alpha_mem: float,
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
            "canon_overrides": {"alpha_mem": alpha_mem},
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
            "canon_overrides": {"alpha_mem": alpha_mem},
        }
    raise ValueError(f"Unknown preset: {preset}")


def calibrate_and_export(
    *,
    canon_path: str,
    preset: str,
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

    canon = GRUTCanon(canon_path)
    overrides = _preset_init(
        preset,
        canon,
        alpha_mem,
        start_z=start_z,
        rho0_vac=vacuum_rho0_vac,
        rho_m0=vacuum_rho_m0,
    )
    if overrides.get("canon_overrides"):
        canon = override_canon(canon, overrides["canon_overrides"])

    engine = GRUTEngine(canon, determinism_mode="STRICT")
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
        overrides["init_state"],
        run_config=run_config,
        assumption_toggles=overrides.get("assumptions", {}),
    )

    hz = outputs.get("OBS_HZ_001", {})
    z_vals = list(hz.get("z", []))
    H_code = list(hz.get("H", []))
    _validate_cosmology_arrays(z_vals=z_vals, H_vals=H_code, steps=steps, fs8=outputs.get("OBS_FS8_001"))
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
    if status != "VIABLE":
        status_payload = {
            "status": status,
            "H0_code": H0_code,
            "idx0": idx0,
            "z0": z0,
            "failure_reason": failure_reason,
        }
        (outdir_path / "calibration_status.json").write_text(json.dumps(status_payload, indent=2))
        manifest = {
            "preset": preset,
            "alpha_mem": alpha_mem,
            "start_z": start_z,
            "dt_years": dt_years,
            "steps": steps,
            "canon_hash": cert.get("engine_signature", {}).get("canon_hash"),
            "repro_hash": cert.get("repro_hash"),
            "output_digest": cert.get("outputs", {}).get("output_digest"),
            "H0_code": H0_code,
            "idx0": idx0,
            "z0": z0,
            "status": status,
            "failure_reason": failure_reason,
            "anchors": [],
            "sigma8_0": canon.get_value("PARAM_SIGMA8_0") if "PARAM_SIGMA8_0" in canon.constants_by_id else 0.0,
            "compare_definition": cert.get("run_trace", {}).get("compare_definition"),
            "valid_z_max": valid_z_max,
        }
        CalibrationManifest.model_validate(manifest)
        (outdir_path / "calibration_manifest.json").write_text(json.dumps(manifest, indent=2))
        return manifest

    E_z = compute_Ez(H_code, idx0)
    if len(E_z) != len(H_code):
        raise ValueError("E_z length mismatch")
    if not math.isclose(E_z[idx0], 1.0, rel_tol=1e-10, abs_tol=0.0):
        raise ValueError("E_z at z0 index is not 1")
    if H0_code > 0 and any(not _is_finite(float(v)) for v in E_z):
        raise ValueError("Non-finite E_z values with positive H0_code")

    header_base = [
        f"canon_hash: {cert.get('engine_signature', {}).get('canon_hash')}",
        f"repro_hash: {cert.get('repro_hash')}",
        f"output_digest: {cert.get('outputs', {}).get('output_digest')}",
        f"preset: {preset}",
        f"alpha_mem: {alpha_mem}",
        f"idx0: {idx0}",
        f"H0_code: {H0_code}",
    ]

    ez_rows = [{"z": z, "H_code": h, "E_z": e} for z, h, e in zip(z_vals, H_code, E_z)]
    _write_csv_with_header(
        outdir_path / "Hz_dimensionless_Ez.csv",
        header_base,
        ["z", "H_code", "E_z"],
        ez_rows,
    )

    anchor_policies = []
    for anchor in ANCHORS:
        policy = build_policy(anchor["H0"], H0_code, {"anchor": anchor["name"]})
        if policy["scale_H"] <= 0 or not _is_finite(float(policy["scale_H"])):
            raise ValueError("Non-positive or non-finite scale_H")
        expected_scale = anchor["H0"] / H0_code
        if not math.isclose(policy["scale_H"], expected_scale, rel_tol=1e-10, abs_tol=0.0):
            raise ValueError("scale_H does not match H0/H0_code")
        anchor_policies.append(
            {
                "name": anchor["name"],
                "H0_km_s_Mpc": anchor["H0"],
                "scale_H": policy["scale_H"],
            }
        )
        H_phys = convert_H(H_code, policy["scale_H"])
        header_lines = header_base + [
            f"anchor_name: {anchor['name']}",
            f"H0_km_s_Mpc: {anchor['H0']}",
            f"scale_H: {policy['scale_H']}",
        ]
        rows = [{"z": z, "H_km_s_Mpc": h} for z, h in zip(z_vals, H_phys)]
        _write_csv_with_header(
            outdir_path / f"Hz_km_s_Mpc_{anchor['name']}.csv",
            header_lines,
            ["z", "H_km_s_Mpc"],
            rows,
        )

    fs8 = outputs.get("OBS_FS8_001")
    sigma8_0 = canon.get_value("PARAM_SIGMA8_0") if "PARAM_SIGMA8_0" in canon.constants_by_id else 0.0
    compare_definition = cert.get("run_trace", {}).get("compare_definition")
    fs8_header = header_base + [
        f"sigma8_0: {sigma8_0}",
        "sigma8_0_note: baseline parameter, not fitted",
    ]
    if compare_definition:
        fs8_header.append(f"compare_definition: {compare_definition}")

    fs8_rows: List[Dict[str, Any]] = []
    if fs8:
        fs8_z = list(fs8.get("z", []))
        fs8_vals = list(fs8.get("fsigma8", []))
        compare_mask = list(fs8.get("compare_mask", []))
        if not compare_mask:
            compare_mask = [False] * len(fs8_vals)
        for z_val, fs8_val, cm in zip(fs8_z, fs8_vals, compare_mask):
            in_domain = True
            if valid_z_max is not None and z_val is not None:
                in_domain = z_val <= float(valid_z_max)
            fs8_rows.append(
                {
                    "z": z_val,
                    "fsigma8_compare": fs8_val if (cm and in_domain) else None,
                    "compare_mask_flag": bool(cm and in_domain),
                }
            )

    _write_csv_with_header(
        outdir_path / "fs8_compare_window.csv",
        fs8_header,
        ["z", "fsigma8_compare", "compare_mask_flag"],
        fs8_rows,
    )

    manifest = {
        "preset": preset,
        "alpha_mem": alpha_mem,
        "start_z": start_z,
        "dt_years": dt_years,
        "steps": steps,
        "canon_hash": cert.get("engine_signature", {}).get("canon_hash"),
        "repro_hash": cert.get("repro_hash"),
        "output_digest": cert.get("outputs", {}).get("output_digest"),
        "H0_code": H0_code,
        "idx0": idx0,
        "z0": z0,
        "status": status,
        "failure_reason": failure_reason,
        "anchors": anchor_policies,
        "sigma8_0": sigma8_0,
        "compare_definition": compare_definition,
        "valid_z_max": valid_z_max,
    }
    CalibrationManifest.model_validate(manifest)
    (outdir_path / "calibration_manifest.json").write_text(json.dumps(manifest, indent=2))

    evidence_dir = Path("artifacts/evidence_packet_phase2_cosmo_v0")
    if evidence_dir.exists():
        calib_target = evidence_dir / "calibration"
        calib_target.mkdir(parents=True, exist_ok=True)
        for item in outdir_path.iterdir():
            if item.is_file():
                shutil.copy2(item, calib_target / item.name)

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate and export H(z) conversions")
    parser.add_argument("--canon", default="canon/grut_canon_v0.3.json")
    parser.add_argument("--preset", default="matter_only", choices=["matter_only", "vacuum_plus_matter"])
    parser.add_argument("--alpha_mem", type=float, default=0.333333333)
    parser.add_argument("--start_z", type=float, default=2.0)
    parser.add_argument("--dt_years", type=float, default=1e5)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--outdir", default="artifacts/calibration")
    parser.add_argument("--vacuum_rho0_vac", type=float, default=None)
    parser.add_argument("--vacuum_rho_m0", type=float, default=None)
    parser.add_argument("--vacuum_valid_z_max", type=float, default=None)
    args = parser.parse_args()

    calibrate_and_export(
        canon_path=args.canon,
        preset=args.preset,
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
