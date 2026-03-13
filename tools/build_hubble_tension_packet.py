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
from grut.canon_override import override_canon
from grut.engine import GRUTEngine
from grut.conversion import compute_Ez, find_z0_index
from grut.hubble_tension_metrics import (
    build_growth_sidecar,
    build_point_residuals,
    compute_residuals_vs_data,
    compute_residuals_vs_lcdm,
)
from grut.lcdm_reference import Ez_lcdm_series
from grut.cluster_packet import file_sha256
from grut.utils import stable_sha256

ANCHORS = [
    {"name": "Planck_67p4", "H0": 67.4},
    {"name": "SH0ES_73p0", "H0": 73.0},
]

LCDM_DEFAULTS = {
    "Omega_m": 0.315,
    "Omega_L": 0.685,
    "Omega_k": 0.0,
    "Omega_r": 0.0,
}


def _write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


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
            "valid_z_max": None,
        }
    if preset == "vacuum_plus_matter":
        threshold = _vacuum_threshold(canon)
        rho_m0_val = 0.05
        rho0_vac_val = threshold * 5.0
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
            "valid_z_max": 1.0,
        }
    raise ValueError(f"Unknown preset: {preset}")


def _evaluate_run_status(
    *,
    start_z: float,
    idx0: int,
    H0_code: float,
    valid_z_max: Optional[float],
    z0: Optional[float],
) -> Dict[str, Any]:
    viable = (H0_code == H0_code) and (H0_code is not None) and (H0_code > 0.0)
    if not viable:
        status = "NOT_VIABLE_AT_Z0"
        failure_reason = "H0_code_nonpositive_or_nonfinite"
    elif valid_z_max is not None and start_z > float(valid_z_max):
        status = "OUT_OF_DOMAIN_HIGH_Z"
        failure_reason = "start_z_above_valid_z_max"
    else:
        status = "VIABLE"
        failure_reason = None
    return {
        "status": status,
        "H0_code": H0_code,
        "idx0": idx0,
        "z0": z0,
        "failure_reason": failure_reason,
        "valid_z_max": valid_z_max,
    }


def _load_hz_dataset(path: Path) -> Dict[str, List[Any]]:
    rows = list(csv.DictReader(path.read_text().splitlines()))
    return {
        "z": [float(r["z"]) for r in rows],
        "Hz": [float(r["Hz_km_s_Mpc"]) for r in rows],
        "sigma": [float(r["sigma_Hz"]) for r in rows],
        "tracer": [r.get("tracer") for r in rows],
        "reference": [r.get("reference") for r in rows],
    }


def _apply_dataset_policy(dataset: Dict[str, List[Any]], policy: str) -> Dict[str, List[Any]]:
    policy = policy.strip().lower()
    if policy in {"min", "all"}:
        return dataset
    if policy not in {"cc_only", "bao_only"}:
        raise ValueError(f"Unknown dataset_policy: {policy}")
    keep = "CC" if policy == "cc_only" else "BAO"
    indices = [i for i, t in enumerate(dataset["tracer"]) if str(t).strip().upper() == keep]
    return {key: [vals[i] for i in indices] for key, vals in dataset.items()}


def build_hubble_tension_packet(
    *,
    outdir: str,
    canon_path: str,
    alpha_mem: Optional[float],
    start_z: float,
    steps: int,
    dt_years: float,
    integrator: str,
    include_vacuum_plus_matter: bool,
    dataset_policy: str,
    eobs_anchor_policy: str,
    compare_window_policy: str,
    preset: str,
    recommendation_mode: str,
    make_plots: bool,
) -> Dict[str, Any]:
    outdir_path = Path(outdir)
    runs_dir = outdir_path / "runs"
    data_dir = outdir_path / "data"
    outputs_dir = outdir_path / "outputs"
    plots_dir = outputs_dir / "plots"

    runs_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    if make_plots:
        plots_dir.mkdir(parents=True, exist_ok=True)

    canon = GRUTCanon(canon_path)
    canon_hash = canon.canon_hash
    if alpha_mem is not None:
        canon = override_canon(canon, {"alpha_mem": float(alpha_mem)})

    recommendation_mode = recommendation_mode.strip().lower()
    if recommendation_mode not in {"configured_only", "late_time_grid"}:
        raise ValueError("Unknown recommendation_mode")

    if recommendation_mode == "late_time_grid":
        presets = ["matter_only", "vacuum_plus_matter"]
        if not include_vacuum_plus_matter:
            presets = ["matter_only"]
        window_policies = ["full", "z_le_1_0"]
    else:
        if preset == "both":
            presets = ["matter_only", "vacuum_plus_matter"]
        else:
            presets = [preset]
        if (not include_vacuum_plus_matter) and "vacuum_plus_matter" in presets:
            presets.remove("vacuum_plus_matter")
        compare_window_policy = compare_window_policy.strip().lower()
        if compare_window_policy not in {"full", "z_le_1_0", "z_le_1_5"}:
            raise ValueError("Unknown compare_window_policy")
        window_policies = [compare_window_policy]
        if compare_window_policy == "full":
            window_policies = ["full"]

    window_map = {
        "full": float(start_z),
        "z_le_1_0": min(float(start_z), 1.0),
        "z_le_1_5": min(float(start_z), 1.5),
    }

    run_config = {
        "start_z": float(start_z),
        "steps": int(steps),
        "dt_years": float(dt_years),
        "integrator": str(integrator),
        "rho_is_rho0": True,
    }

    engine = GRUTEngine(canon, determinism_mode="STRICT")

    preset_results: Dict[str, Any] = {}
    ez_rows: List[Dict[str, Any]] = []
    ez_lcdm_rows: List[Dict[str, Any]] = []
    hz_anchor_rows: List[Dict[str, Any]] = []
    residuals_vs_lcdm: Dict[str, Any] = {"presets": {}}
    residuals_vs_data: Dict[str, Any] = {"presets": {}}
    point_rows_all: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []
    summary_json: Dict[str, Any] = {"rows": []}
    recommendation_candidates: List[Dict[str, Any]] = []
    anchors_map = {anchor["name"]: float(anchor["H0"]) for anchor in ANCHORS}

    hz_source = ROOT / "data" / "hz_observations_min.csv"
    sources_path = ROOT / "data" / "sources.json"
    hz_dataset = _apply_dataset_policy(_load_hz_dataset(hz_source), dataset_policy)
    tracer_counts: Dict[str, int] = {}
    for tracer in hz_dataset.get("tracer", []):
        key = str(tracer)
        tracer_counts[key] = tracer_counts.get(key, 0) + 1

    for preset in presets:
        preset_cfg = _preset_init(preset, canon, start_z=float(start_z))
        run_cfg = dict(run_config)
        if preset_cfg.get("valid_z_max") is not None:
            run_cfg["valid_z_max"] = float(preset_cfg["valid_z_max"])

        outputs, cert = engine.run(
            preset_cfg["init_state"],
            run_config=run_cfg,
            assumption_toggles=preset_cfg.get("assumptions", {}),
        )
        hz = outputs.get("OBS_HZ_001", {})
        z_vals = list(hz.get("z", []))
        H_code = list(hz.get("H", []))
        idx0 = find_z0_index(z_vals)
        if idx0 is None:
            raise ValueError("No z values to compute H0")
        H0_code = H_code[idx0]
        z0 = z_vals[idx0] if idx0 < len(z_vals) else None
        valid_z_max = run_cfg.get("valid_z_max")
        status = _evaluate_run_status(
            start_z=float(start_z),
            idx0=idx0,
            H0_code=float(H0_code),
            valid_z_max=valid_z_max,
            z0=z0,
        )

        E_grut: List[Optional[float]]
        if H0_code is None or H0_code <= 0.0:
            E_grut = [None for _ in H_code]
        else:
            E_grut = [float(v) for v in compute_Ez(H_code, idx0)]

        E_lcdm = Ez_lcdm_series(
            z_vals,
            LCDM_DEFAULTS["Omega_m"],
            LCDM_DEFAULTS["Omega_L"],
            Omega_r=LCDM_DEFAULTS["Omega_r"],
            Omega_k=LCDM_DEFAULTS["Omega_k"],
        )

        residuals_vs_lcdm["presets"][preset] = compute_residuals_vs_lcdm(
            z_vals=z_vals,
            E_grut=E_grut,
            E_lcdm=E_lcdm,
            start_z=float(start_z),
            valid_z_max=valid_z_max,
        )

        windows_block: Dict[str, Any] = {}
        for window_policy in window_policies:
            window_start = window_map[window_policy]
            anchors_block: Dict[str, Any] = {}
            for anchor in ANCHORS:
                anchors_block[anchor["name"]] = compute_residuals_vs_data(
                    z_obs=hz_dataset["z"],
                    Hz_obs=hz_dataset["Hz"],
                    sigma_obs=hz_dataset["sigma"],
                    tracer=hz_dataset["tracer"],
                    z_model=z_vals,
                    E_grut=E_grut,
                    H0_phys=float(anchor["H0"]),
                    Eobs_anchor_policy=eobs_anchor_policy,
                    start_z=window_start,
                    valid_z_max=valid_z_max,
                )
            windows_block[window_policy] = {
                "anchors": anchors_block,
                "compare_window_policy": window_policy,
                "compare_window_max_z": window_start,
                "dataset_policy": dataset_policy,
                "tracer_counts": tracer_counts,
                "n_points_total": len(hz_dataset.get("z", [])),
            }

            point_rows, _ = build_point_residuals(
                z_obs=hz_dataset["z"],
                Hz_obs=hz_dataset["Hz"],
                sigma_obs=hz_dataset["sigma"],
                tracer=hz_dataset["tracer"],
                z_model=z_vals,
                E_grut=E_grut,
                anchors=anchors_map,
                Eobs_anchor_policy=eobs_anchor_policy,
                start_z=window_start,
                valid_z_max=valid_z_max,
            )
            for row in point_rows:
                row["preset"] = preset
                row["compare_window_policy"] = window_policy
                point_rows_all.append(row)

            planck = anchors_block.get("Planck_67p4", {})
            shoes = anchors_block.get("SH0ES_73p0", {})
            by_tracer_E = planck.get("by_tracer_E", {})
            cc_block = by_tracer_E.get("CC", {})
            bao_block = by_tracer_E.get("BAO", {})
            worst_E = planck.get("top_k_worst_points_E", [])
            worst = worst_E[0] if worst_E else {}
            compare_report_E = planck.get("compare_report_E", {})
            n_points_used = compare_report_E.get("n_points_used")
            n_total = compare_report_E.get("n_points_total")
            n_excluded = None
            if isinstance(n_total, int) and isinstance(n_points_used, int):
                n_excluded = n_total - n_points_used
            summary_row = {
                "preset": preset,
                "compare_window_policy": window_policy,
                "status": status.get("status"),
                "n_points_used": n_points_used,
                "n_excluded": n_excluded,
                "chi2_total_planck": planck.get("chi2"),
                "chi2_total_shoes": shoes.get("chi2"),
                "chi2_E_total": planck.get("chi2_E"),
                "chi2_E_cc": cc_block.get("chi2"),
                "chi2_E_bao": bao_block.get("chi2"),
                "worst_point_z": worst.get("z"),
                "worst_point_tracer": worst.get("tracer"),
                "worst_point_resid_sigma_E": worst.get("residual_sigma"),
            }
            summary_rows.append(summary_row)
            summary_json["rows"].append(
                {
                    **summary_row,
                    "exclusions": compare_report_E.get("exclusions"),
                }
            )
            recommendation_candidates.append(summary_row)

        residuals_vs_data["presets"][preset] = {
            "status": status,
            "windows": windows_block,
            "growth_sidecar": build_growth_sidecar(outputs),
            "dataset_policy": dataset_policy,
            "tracer_counts": tracer_counts,
            "n_points_total": len(hz_dataset.get("z", [])),
        }

        for z, h, e in zip(z_vals, H_code, E_grut):
            in_domain = True
            if valid_z_max is not None and z > float(valid_z_max):
                in_domain = False
            ez_rows.append(
                {
                    "preset": preset,
                    "z": z,
                    "H_code": h,
                    "E_grut": e,
                    "in_domain": in_domain,
                    "status": status["status"],
                }
            )
        for z, e in zip(z_vals, E_lcdm):
            ez_lcdm_rows.append({"preset": preset, "z": z, "E_lcdm": e})

        for anchor in ANCHORS:
            H0_phys = float(anchor["H0"])
            H_phys_vals = [float(e) * H0_phys if e is not None else None for e in E_grut]
            for z, h, hp in zip(z_vals, H_code, H_phys_vals):
                row = {
                    "preset": preset,
                    "anchor": anchor["name"],
                    "z": z,
                    "H_code": h,
                    "H_phys": hp,
                }
                hz_anchor_rows.append(row)

        preset_results[preset] = {
            "init_state": preset_cfg["init_state"],
            "assumption_toggles": preset_cfg.get("assumptions", {}),
            "run_config": run_cfg,
            "status": status,
            "cert": {
                "canon_hash": cert.get("engine_signature", {}).get("canon_hash"),
                "repro_hash": cert.get("repro_hash"),
                "output_digest": cert.get("outputs", {}).get("output_digest"),
            },
        }

    lcdm_reference = {"params": dict(LCDM_DEFAULTS)}
    (runs_dir / "lcdm_reference.json").write_text(json.dumps(lcdm_reference, indent=2, sort_keys=True))

    grut_run_payload = {
        "run_config": run_config,
        "presets": preset_results,
    }
    (runs_dir / "grut_run.json").write_text(json.dumps(grut_run_payload, indent=2, sort_keys=True))

    shutil.copyfile(hz_source, data_dir / "hz_observations.csv")
    shutil.copyfile(sources_path, data_dir / "sources.json")

    _write_csv(
        outputs_dir / "Ez_grut.csv",
        ["preset", "z", "H_code", "E_grut", "in_domain", "status"],
        ez_rows,
    )
    _write_csv(outputs_dir / "Ez_lcdm.csv", ["preset", "z", "E_lcdm"], ez_lcdm_rows)
    _write_csv(
        outputs_dir / "Hz_grut_anchors.csv",
        ["preset", "anchor", "z", "H_code", "H_phys"],
        hz_anchor_rows,
    )

    point_fields = list(point_rows_all[0].keys()) if point_rows_all else [
        "preset",
        "compare_window_policy",
        "z",
        "tracer",
        "Hz_obs",
        "sigma_Hz",
        "E_obs",
        "sigma_E",
        "E_model",
        "resid_sigma_E",
        "exclude_reason_H",
        "exclude_reason_E",
        "Hz_model_Planck_67p4",
        "resid_sigma_H_Planck_67p4",
        "Hz_model_SH0ES_73p0",
        "resid_sigma_H_SH0ES_73p0",
    ]
    _write_csv(outputs_dir / "point_residuals.csv", point_fields, point_rows_all)

    summary_fields = [
        "preset",
        "compare_window_policy",
        "status",
        "n_points_used",
        "n_excluded",
        "chi2_total_planck",
        "chi2_total_shoes",
        "chi2_E_total",
        "chi2_E_cc",
        "chi2_E_bao",
        "worst_point_z",
        "worst_point_tracer",
        "worst_point_resid_sigma_E",
    ]
    _write_csv(outputs_dir / "preset_window_summary.csv", summary_fields, summary_rows)
    (outputs_dir / "preset_window_summary.json").write_text(
        json.dumps(summary_json, indent=2, sort_keys=True)
    )

    candidate_rows = recommendation_candidates
    if recommendation_mode == "late_time_grid":
        grid_candidates: List[Dict[str, Any]] = []
        combos = [
            {"preset": "matter_only", "compare_window_policy": "full"},
            {"preset": "matter_only", "compare_window_policy": "z_le_1_0"},
            {"preset": "vacuum_plus_matter", "compare_window_policy": "z_le_1_0"},
            {"preset": "vacuum_plus_matter", "compare_window_policy": "full"},
        ]
        for combo in combos:
            for row in summary_rows:
                if row.get("preset") != combo["preset"]:
                    continue
                if row.get("compare_window_policy") != combo["compare_window_policy"]:
                    continue
                if row.get("compare_window_policy") == "full" and row.get("status") not in {"VIABLE", None}:
                    continue
                grid_candidates.append(row)
        candidate_rows = grid_candidates

    candidates = []
    for row in candidate_rows:
        chi2_E = row.get("chi2_E_total")
        chi2_planck = row.get("chi2_total_planck")
        if chi2_E is None:
            continue
        candidates.append(
            {
                **row,
                "chi2_E_total": float(chi2_E),
                "chi2_total_planck": float(chi2_planck) if chi2_planck is not None else float("inf"),
            }
        )
    candidates_sorted = sorted(
        candidates,
        key=lambda r: (r["chi2_E_total"], r["chi2_total_planck"], r.get("preset"), r.get("compare_window_policy")),
    )
    recommendation = None
    if candidates_sorted:
        best = candidates_sorted[0]
        recommendation = {
            "recommended_preset": best.get("preset"),
            "recommended_compare_window_policy": best.get("compare_window_policy"),
            "chi2_E_total": best.get("chi2_E_total"),
            "chi2_total_planck": best.get("chi2_total_planck"),
            "chi2_total_shoes": best.get("chi2_total_shoes"),
            "n_points_used": best.get("n_points_used"),
            "n_excluded": best.get("n_excluded"),
            "rationale": "Selected lowest chi2_E_total; tie-breaker lowest chi2_total_planck.",
            "caution": "Tier A non-fitted recommendation; domain-limited.",
            "candidates": candidates_sorted,
        }
    else:
        recommendation = {
            "recommended_preset": None,
            "recommended_compare_window_policy": None,
            "chi2_E_total": None,
            "chi2_total_planck": None,
            "chi2_total_shoes": None,
            "n_points_used": None,
            "n_excluded": None,
            "rationale": "No valid candidates with chi2_E_total.",
            "caution": "Tier A non-fitted recommendation; domain-limited.",
            "candidates": candidates_sorted,
        }
    (outputs_dir / "late_time_recommendation.json").write_text(
        json.dumps(recommendation, indent=2, sort_keys=True)
    )

    (outputs_dir / "residuals_vs_lcdm.json").write_text(
        json.dumps(residuals_vs_lcdm, indent=2, sort_keys=True)
    )
    (outputs_dir / "residuals_vs_data.json").write_text(
        json.dumps(residuals_vs_data, indent=2, sort_keys=True)
    )

    readme = (
        "# Hubble Tension Evidence Packet v0.2.4\n\n"
        "This Tier A packet compares GRUT cosmology outputs to a fixed ΛCDM reference and to an offline H(z) compilation.\n\n"
        "## Presets\n"
        "- matter_only\n"
        "- vacuum_plus_matter (domain-of-validity gating if valid_z_max is set)\n\n"
        "## Anchor Policy\n"
        "E(z) = H(z)/H(0) is the anchor-free shape observable.\n"
        "Anchored H(z) uses explicit anchors with no fitting:\n"
        "- Planck_67p4: H0 = 67.4 km/s/Mpc\n"
        "- SH0ES_73p0: H0 = 73.0 km/s/Mpc\n\n"
        "H(z) scaling policy: Hz_phys(z) = Hz_code(z) * (H0_phys / H0_code).\n\n"
        "## Shape-Only Residuals\n"
        "E(z) residuals are computed using a dataset anchor policy (lowest_z or median_lowz).\n"
        "These provide an anchor-free shape comparison with tracer-split reporting.\n\n"
        "## Dataset Policy\n"
        "Dataset curation is explicit via --dataset_policy: min, cc_only, bao_only, all.\n\n"
        "## Compare Window Policy\n"
        "Compare windows are explicit via --compare_window_policy: full, z_le_1_0, z_le_1_5.\n\n"
        "## Current Best Late-Time Branch\n"
        "See outputs/late_time_recommendation.json for the current multi-candidate recommendation derived from chi2_E_total.\n\n"
        "## ΛCDM Reference (No Fitting)\n"
        "Reference parameters are fixed and logged: Ωm=0.315, ΩΛ=0.685, Ωk=0, Ωr=0.\n\n"
        "## Claims / Non-Claims\n"
        "This packet emits residual metrics only. It does not fit or tune model parameters.\n"
        "Network access is not used in tests or audit; data are bundled offline.\n\n"
        "## Reproduction\n"
        "python tools/build_hubble_tension_packet.py --outdir artifacts/evidence_hubble_tension_v0_2_4\n"
    )
    (outdir_path / "README_DATA.md").write_text(readme)

    base_files = {
        "README_DATA.md": outdir_path / "README_DATA.md",
        "runs/grut_run.json": runs_dir / "grut_run.json",
        "runs/lcdm_reference.json": runs_dir / "lcdm_reference.json",
        "data/hz_observations.csv": data_dir / "hz_observations.csv",
        "data/sources.json": data_dir / "sources.json",
        "outputs/Ez_grut.csv": outputs_dir / "Ez_grut.csv",
        "outputs/Ez_lcdm.csv": outputs_dir / "Ez_lcdm.csv",
        "outputs/Hz_grut_anchors.csv": outputs_dir / "Hz_grut_anchors.csv",
        "outputs/point_residuals.csv": outputs_dir / "point_residuals.csv",
        "outputs/preset_window_summary.csv": outputs_dir / "preset_window_summary.csv",
        "outputs/preset_window_summary.json": outputs_dir / "preset_window_summary.json",
        "outputs/late_time_recommendation.json": outputs_dir / "late_time_recommendation.json",
        "outputs/residuals_vs_lcdm.json": outputs_dir / "residuals_vs_lcdm.json",
        "outputs/residuals_vs_data.json": outputs_dir / "residuals_vs_data.json",
    }

    input_hash = stable_sha256(
        {
            "run_config": run_config,
            "canon_hash": canon_hash,
            "lcdm_reference": LCDM_DEFAULTS,
            "anchors": ANCHORS,
            "data_hashes": {
                "hz_observations_min.csv": file_sha256(str(hz_source)),
                "sources.json": file_sha256(str(sources_path)),
            },
            "dataset_policy": dataset_policy,
            "eobs_anchor_policy": eobs_anchor_policy,
            "compare_window_policy": compare_window_policy,
            "preset": preset,
        }
    )

    base_hashes = {name: file_sha256(str(path)) for name, path in base_files.items() if path.exists()}
    output_digest = stable_sha256({"output_hashes": base_hashes, "input_hash": input_hash, "canon_hash": canon_hash})

    certificate = {
        "tool_version": "hubble_tension_packet_v0.2.4",
        "determinism_mode": "STRICT",
        "canon_hash": canon_hash,
        "input_hash": input_hash,
        "output_digest": output_digest,
        "output_hashes": dict(base_hashes),
        "timestamp": None,
    }
    cert_path = outdir_path / "nis_hubble_certificate.json"
    cert_path.write_text(json.dumps(certificate, indent=2, sort_keys=True))

    output_files = dict(base_files)
    output_files["nis_hubble_certificate.json"] = cert_path

    packet_index = {
        "packet": "evidence_hubble_tension_v0_2_4",
        "input_hash": input_hash,
        "canon_hash": canon_hash,
        "output_digest": output_digest,
        "files": {},
    }
    index_path = outdir_path / "PACKET_INDEX.json"
    index_path.write_text(json.dumps(packet_index, indent=2, sort_keys=True))
    output_files["PACKET_INDEX.json"] = index_path

    output_hashes = {name: file_sha256(str(path)) for name, path in output_files.items() if path.exists()}
    certificate["output_hashes"] = output_hashes
    cert_path.write_text(json.dumps(certificate, indent=2, sort_keys=True))

    packet_index["files"] = output_hashes
    index_path.write_text(json.dumps(packet_index, indent=2, sort_keys=True))

    return {
        "outdir": str(outdir_path),
        "input_hash": input_hash,
        "output_digest": output_digest,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Hubble Tension Evidence Packet v0.2.4")
    parser.add_argument("--outdir", default="artifacts/evidence_hubble_tension_v0_2_4")
    parser.add_argument("--canon_path", default="canon/grut_canon_v0.3.json")
    parser.add_argument("--alpha_mem", type=float, default=None)
    parser.add_argument("--start_z", type=float, default=2.0)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--dt_years", type=float, default=100000.0)
    parser.add_argument("--integrator", default="RK4")
    parser.add_argument("--include_vacuum_plus_matter", default="true")
    parser.add_argument("--dataset_policy", default="all", choices=["min", "cc_only", "bao_only", "all"])
    parser.add_argument("--Eobs_anchor_policy", default="lowest_z", choices=["lowest_z", "median_lowz"])
    parser.add_argument("--compare_window_policy", default="full", choices=["full", "z_le_1_0", "z_le_1_5"])
    parser.add_argument("--preset", default="both", choices=["matter_only", "vacuum_plus_matter", "both"])
    parser.add_argument("--recommendation_mode", default="late_time_grid", choices=["configured_only", "late_time_grid"])
    parser.add_argument("--make_plots", action="store_true", default=False)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    include_vacuum_plus_matter = str(args.include_vacuum_plus_matter).strip().lower() in {"true", "1", "yes"}
    build_hubble_tension_packet(
        outdir=args.outdir,
        canon_path=args.canon_path,
        alpha_mem=args.alpha_mem,
        start_z=args.start_z,
        steps=args.steps,
        dt_years=args.dt_years,
        integrator=args.integrator,
        include_vacuum_plus_matter=include_vacuum_plus_matter,
        dataset_policy=args.dataset_policy,
        eobs_anchor_policy=args.Eobs_anchor_policy,
        compare_window_policy=args.compare_window_policy,
        preset=args.preset,
        recommendation_mode=args.recommendation_mode,
        make_plots=args.make_plots,
    )


if __name__ == "__main__":
    main()
