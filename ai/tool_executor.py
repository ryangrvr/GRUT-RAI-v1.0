"""Execute tool calls by invoking the deterministic GRUT engine.

The sovereign firewall: all physics numbers come from the engine,
never from the LLM. This module bridges Claude's tool calls to
existing internal functions.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def execute_tool(
    tool_name: str,
    tool_input: Dict[str, Any],
    *,
    grut_engine: Any = None,
    db_store: Any = None,
) -> Dict[str, Any]:
    """Dispatch a tool call to the appropriate internal function.

    Returns a dict with the tool result, always including provenance info.
    """
    try:
        if tool_name == "run_cosmology":
            return _run_cosmology(tool_input, grut_engine)
        elif tool_name == "run_experiment":
            return _run_experiment(tool_input)
        elif tool_name == "run_anamnesis":
            return _run_anamnesis(tool_input)
        elif tool_name == "lookup_grutipedia":
            return _lookup_grutipedia(tool_input, db_store)
        elif tool_name == "get_canon_value":
            return _get_canon_value(tool_input, grut_engine)
        elif tool_name == "search_past_runs":
            return _search_past_runs(tool_input, db_store)
        elif tool_name == "suggest_next_experiment":
            return _suggest_next(tool_input, db_store)
        elif tool_name == "build_hubble_tension_packet":
            return _build_hubble_tension_packet(tool_input, grut_engine)
        elif tool_name == "run_lensing":
            return _run_lensing(tool_input)
        elif tool_name == "run_anamnesis_fsigma8":
            return _run_anamnesis_fsigma8(tool_input)
        elif tool_name == "search_tau":
            return _search_tau(tool_input)
        elif tool_name == "fsigma8_resonance_map":
            return _fsigma8_resonance_map(tool_input)
        elif tool_name == "get_library":
            return _get_library(tool_input, db_store)
        elif tool_name == "get_run_details":
            return _get_run_details(tool_input, db_store)
        elif tool_name == "export_evidence_packet":
            return _export_evidence_packet(tool_input, db_store)
        elif tool_name == "anamnesis_reconstruct":
            return _anamnesis_reconstruct(tool_input)
        elif tool_name == "search_tau_fsigma8":
            return _search_tau_fsigma8(tool_input)
        elif tool_name == "publish_run":
            return _publish_run(tool_input, db_store)
        elif tool_name == "get_published":
            return _get_published(tool_input, db_store)
        elif tool_name == "list_grutipedia":
            return _list_grutipedia(tool_input, db_store)
        elif tool_name == "link_run_to_topic":
            return _link_run_to_topic(tool_input, db_store)
        elif tool_name == "get_full_canon":
            return _get_full_canon(tool_input, grut_engine)
        elif tool_name == "generate_sweep":
            return _generate_sweep(tool_input, grut_engine)
        elif tool_name == "build_quantum_evidence_packet":
            return _build_quantum_evidence_packet(tool_input)
        elif tool_name == "run_rotation_packet":
            return _run_rotation_packet(tool_input)
        elif tool_name == "run_cluster_profile_packet":
            return _run_cluster_profile_packet(tool_input)
        elif tool_name == "run_audit":
            return _run_audit(tool_input)
        elif tool_name == "list_evidence_packets":
            return _list_evidence_packets(tool_input)
        elif tool_name == "build_release_bundle":
            return _build_release_bundle(tool_input)
        elif tool_name == "verify_release_bundle":
            return _verify_release_bundle(tool_input)
        elif tool_name == "run_radial_collapse":
            return _run_radial_collapse(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except Exception as exc:
        logger.error("Tool execution error (%s): %s", tool_name, exc)
        return {"error": str(exc), "tool": tool_name}


def _run_cosmology(params: Dict[str, Any], engine: Any) -> Dict[str, Any]:
    """Run the Phase-2 engine and return results with certificate."""
    if engine is None:
        return {"error": "GRUT engine not initialized"}

    input_state = {
        "a": 1.0,
        "H": float(params.get("H0", 1e-10)),
        "rho": float(params.get("rho0", 0.2)),
        "p": float(params.get("p0", -0.2)),
        "M_X": 0.0,
    }
    rho_m0 = params.get("rho_m0")
    if rho_m0 is not None:
        input_state["rho_m"] = float(rho_m0)

    run_config = {
        "dt_years": float(params.get("dt_years", 100000)),
        "steps": int(params.get("steps", 300)),
        "integrator": "RK4",
    }
    start_z = params.get("start_z")
    if start_z is not None:
        run_config["start_z"] = float(start_z)

    assumptions = {}
    if params.get("enable_growth", True):
        assumptions["growth_enabled"] = True

    alpha_mem = params.get("alpha_mem")
    run_engine = engine
    if alpha_mem is not None:
        from grut.canon_override import override_canon
        from grut.engine import GRUTEngine
        new_canon = override_canon(engine.canon, {"PARAM_ALPHA_MEM": float(alpha_mem)})
        run_engine = GRUTEngine(new_canon, determinism_mode="STRICT")

    outputs, cert = run_engine.run(
        input_state,
        run_config=run_config,
        assumption_toggles=assumptions,
    )

    # Extract chart-friendly data
    hz_data = outputs.get("OBS_HZ_001", {})
    fs8_data = outputs.get("OBS_FS8_001", {})

    final = outputs.get("final_state", {})

    # Summarize for the AI (don't send full arrays, just key info)
    hz_points = hz_data.get("data", [])
    fs8_points = fs8_data.get("data", [])

    hz_summary = {}
    if hz_points:
        z_vals = [p.get("z", p.get("a", 0)) for p in hz_points]
        h_vals = [p.get("H", 0) for p in hz_points]
        hz_summary = {
            "n_points": len(hz_points),
            "z_range": [min(z_vals), max(z_vals)] if z_vals else [],
            "H_range": [min(h_vals), max(h_vals)] if h_vals else [],
        }

    fs8_summary = {}
    if fs8_points:
        z_vals = [p.get("z", 0) for p in fs8_points]
        fs8_vals = [p.get("fsigma8") for p in fs8_points if p.get("fsigma8") is not None]
        fs8_summary = {
            "n_points": len(fs8_points),
            "z_range": [min(z_vals), max(z_vals)] if z_vals else [],
            "fsigma8_range": [min(fs8_vals), max(fs8_vals)] if fs8_vals else [],
        }

    cert_summary = {
        "canon_hash": cert.get("engine_signature", {}).get("canon_hash", ""),
        "repro_hash": cert.get("repro_hash", ""),
        "steps_computed": cert.get("run_trace", {}).get("steps_computed"),
        "integrator": cert.get("run_trace", {}).get("integrator"),
        "observables_emitted": cert.get("outputs", {}).get("observables_emitted", []),
    }

    viability = outputs.get("viability", {})

    return {
        "status": "completed",
        "hz_summary": hz_summary,
        "fs8_summary": fs8_summary,
        "final_state": {
            "a": final.get("a"),
            "H": final.get("H"),
            "rho": final.get("rho"),
        },
        "viability": viability,
        "certificate": cert_summary,
        "charts": {
            "hz": {
                "z": [p.get("z", 1.0 / p.get("a", 1.0) - 1.0 if p.get("a", 0) > 0 else 0) for p in hz_points],
                "H": [p.get("H", 0) for p in hz_points],
            } if hz_points else None,
            "fs8": {
                "z": [p.get("z", 0) for p in fs8_points],
                "fsigma8": [p.get("fsigma8") for p in fs8_points],
            } if fs8_points else None,
        },
    }


def _run_experiment(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run a pre-registered experiment."""
    name = params.get("experiment_name", "")
    exp_params = params.get("params", {})

    if name == "zeta_tau_scaling":
        from core.experiments.zeta_tau_scaling import run_experiment as _run_zeta
        defaults = {
            "tau0_myr": 41.9,
            "H0_km_s_Mpc": 67.4,
            "zeros_n": 50,
            "eps_hit": 0.01,
            "null_trials": 2000,
            "h0_perturb_frac": 0.02,
            "seed": 7,
            "Omega_m": 0.315,
        }
        defaults.update(exp_params)
        result = _run_zeta(**defaults)
        return {"experiment": name, "result": _safe_serialize(result)}

    elif name == "casimir_density_sweep":
        from core.experiments.casimir_density_sweep import run_experiment as _run_casimir
        defaults = {
            "tau0_myr": 41.9,
            "H0_km_s_Mpc": 67.36,
            "Omega_lambda": 0.6847,
            "seed": 7,
        }
        defaults.update(exp_params)
        result = _run_casimir(**defaults)
        return {"experiment": name, "result": _safe_serialize(result)}

    elif name == "pta_dispersion_probe":
        from core.experiments.pta_dispersion_probe import run_probe as _run_pta
        from core.constants import GRUTParams as _GRUTParams
        defaults = {
            "tau0_myr": 41.92,
            "alpha_scr": 1 / 3,
            "freqs_hz": [1e-9, 1e-8, 1e-7],
            "use_group_velocity": True,
            "f_hf_hz": 100.0,
            "apply_to_gw_propagation": False,
            "seed": 7,
            "code_version": _GRUTParams().engine_version,
        }
        defaults.update(exp_params)
        result = _run_pta(**defaults)
        return {"experiment": name, "result": _safe_serialize(result)}

    elif name == "glass_transition_sweep":
        from core.experiments.glass_transition import run_experiment as _run_glass
        defaults = {}
        defaults.update(exp_params)
        result = _run_glass(**defaults)
        return {"experiment": name, "result": _safe_serialize(result)}

    else:
        return {"error": f"Unknown experiment: {name}"}


def _run_anamnesis(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run the Anamnesis reconstruction demo."""
    from core.reconstruction.simulator import (
        make_sparse_events,
        exponential_kernel,
        KernelSpec,
        simulate_shadow,
    )
    from core.reconstruction.reconstructor import LCAConfig, lca_reconstruct
    from core.reconstruction.evaluator import emd_1d, build_ris_report

    import numpy as np

    n_bins = int(params.get("n_bins", 128))
    n_events = int(params.get("n_events", 5))
    tau0_s = 41.9e6 * 365.25 * 24 * 3600
    tau_s = float(params.get("tau_s", tau0_s))

    source = make_sparse_events(n_bins, n_events, seed=42)
    kernel = exponential_kernel(n_bins, tau_s / n_bins)
    shadow = simulate_shadow(source, kernel)

    cfg = LCAConfig(threshold=0.1, max_iter=500, dt=0.01)
    recon = lca_reconstruct(shadow, kernel, cfg)

    emd = emd_1d(source, recon)
    ris = build_ris_report(source, recon, shadow, kernel, emd)

    return {
        "n_bins": n_bins,
        "n_events": n_events,
        "tau_s": tau_s,
        "emd": emd,
        "ris_summary": {
            "recovery_score": ris.get("recovery_score"),
            "spike_recall": ris.get("spike_recall"),
            "status": ris.get("status"),
        },
    }


def _lookup_grutipedia(params: Dict[str, Any], db_store: Any) -> Dict[str, Any]:
    """Look up a GRUTipedia topic."""
    slug = params.get("slug", "")
    if not db_store:
        return {"error": "Database store not available"}

    topic = db_store.get_topic(slug)
    if topic is None:
        # Try with hyphens replaced
        topic = db_store.get_topic(slug.replace("_", "-"))
    if topic is None:
        return {"error": f"Topic '{slug}' not found", "available_hint": "Try: tau0, epsilon, s-phase-bridge, dissipation-operator, cfl-gate, nis-certificate, seth-kernel, zeta-operator"}

    # Build combined body from definition + equations
    body = topic.get("definition_md", "") or topic.get("body", "")
    if topic.get("equations_md"):
        body += "\n\n### Equations\n\n" + topic["equations_md"]

    return {
        "slug": topic.get("slug", slug),
        "title": topic.get("title", ""),
        "definition_md": body,
        "tags": topic.get("tags", []),
        "edition": topic.get("edition", 1),
    }


def _get_canon_value(params: Dict[str, Any], engine: Any) -> Dict[str, Any]:
    """Look up a canon constant."""
    name = params.get("name", "")
    if engine is None:
        return {"error": "GRUT engine not initialized"}

    try:
        val = engine.canon.get_value(name)
        const_id = engine.canon.resolve_id(name)
        entry = engine.canon.constants_by_id.get(const_id, {})
        return {
            "id": const_id,
            "symbol": entry.get("symbol", name),
            "value": val,
            "units": entry.get("units", ""),
            "description": entry.get("description", ""),
            "bounds": entry.get("bounds"),
            "status": entry.get("status", ""),
        }
    except Exception as exc:
        return {"error": f"Constant '{name}' not found: {exc}"}


def _search_past_runs(params: Dict[str, Any], db_store: Any) -> Dict[str, Any]:
    """Search past runs in the vault."""
    if not db_store:
        return {"error": "Database store not available"}

    limit = int(params.get("limit", 5))
    try:
        runs = db_store.list_runs(limit=limit)
        summaries = []
        for r in runs:
            summaries.append({
                "run_id": r.get("run_id", ""),
                "kind": r.get("kind", ""),
                "status": r.get("status", ""),
                "created_utc": r.get("created_utc", ""),
            })
        return {"runs": summaries, "count": len(summaries)}
    except Exception as exc:
        return {"error": f"Failed to search runs: {exc}"}


def _suggest_next(params: Dict[str, Any], db_store: Any) -> Dict[str, Any]:
    """Generate suggestions for a specific run."""
    run_id = params.get("run_id", "")
    if not db_store:
        return {"error": "Database store not available"}

    run = db_store.get_run(run_id)
    if run is None:
        return {"error": f"Run {run_id} not found"}

    # Import the existing suggestion logic
    from ai.suggestions import collect_suggestions
    suggestions = collect_suggestions(run)
    return {"run_id": run_id, "suggestions": suggestions}


def _safe_serialize(obj: Any) -> Any:
    """Make an object JSON-safe for returning to Claude."""
    if obj is None:
        return None
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        return str(obj)


# ── Hubble Tension Evidence Packet ──

def _build_hubble_tension_packet(params: Dict[str, Any], engine: Any) -> Dict[str, Any]:
    """Build a complete Hubble Tension Evidence Packet."""
    import tempfile
    from pathlib import Path

    from tools.build_hubble_tension_packet import build_hubble_tension_packet

    canon_path = str(Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json")

    # Resolve parameters — accept from caller, fall back to sensible defaults
    preset = params.get("preset", "both")
    eobs_anchor_policy = params.get("eobs_anchor_policy", "lowest_z")
    recommendation_mode = params.get("recommendation_mode", "late_time_grid")
    include_vpm = params.get("include_vacuum_plus_matter", preset != "matter_only")

    with tempfile.TemporaryDirectory(prefix="grut_tension_") as tmpdir:
        result = build_hubble_tension_packet(
            outdir=tmpdir,
            canon_path=canon_path,
            alpha_mem=params.get("alpha_mem"),
            start_z=float(params.get("start_z", 2.0)),
            steps=int(params.get("steps", 300)),
            dt_years=float(params.get("dt_years", 100000)),
            integrator="RK4",
            include_vacuum_plus_matter=include_vpm,
            dataset_policy=params.get("dataset_policy", "all"),
            eobs_anchor_policy=eobs_anchor_policy,
            compare_window_policy=params.get("compare_window_policy", "full"),
            preset=preset,
            recommendation_mode=recommendation_mode,
            make_plots=False,
        )

        # Read back the key output files
        outpath = Path(tmpdir)
        summary = {}
        recommendation = {}
        residuals_lcdm = {}
        residuals_data = {}
        nis_cert = {}

        summary_path = outpath / "outputs" / "preset_window_summary.json"
        if summary_path.exists():
            summary = json.loads(summary_path.read_text())

        rec_path = outpath / "outputs" / "late_time_recommendation.json"
        if rec_path.exists():
            recommendation = json.loads(rec_path.read_text())

        res_lcdm_path = outpath / "outputs" / "residuals_vs_lcdm.json"
        if res_lcdm_path.exists():
            residuals_lcdm = json.loads(res_lcdm_path.read_text())

        res_data_path = outpath / "outputs" / "residuals_vs_data.json"
        if res_data_path.exists():
            residuals_data = json.loads(res_data_path.read_text())

        nis_path = outpath / "nis_hubble_certificate.json"
        if nis_path.exists():
            nis_cert = json.loads(nis_path.read_text())

    return {
        "status": "completed",
        "preset": preset,
        "dataset_policy": params.get("dataset_policy", "all"),
        "eobs_anchor_policy": eobs_anchor_policy,
        "recommendation_mode": recommendation_mode,
        "include_vacuum_plus_matter": include_vpm,
        "compare_window": params.get("compare_window_policy", "full"),
        "preset_window_summary": _safe_serialize(summary),
        "late_time_recommendation": _safe_serialize(recommendation),
        "residuals_vs_lcdm": _safe_serialize(residuals_lcdm),
        "residuals_vs_data": _safe_serialize(residuals_data),
        "nis_certificate": _safe_serialize(nis_cert),
        "input_hash": result.get("input_hash", ""),
        "output_digest": result.get("output_digest", ""),
    }


# ── Lensing ──

def _run_lensing(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run a gravitational lensing packet."""
    from grut.lensing import run_lensing as _lensing_run

    n = int(params.get("n", 256))
    fov = float(params.get("fov_arcmin", 20.0))

    result = _lensing_run(
        n=n,
        fov_arcmin=fov,
        delta_arcmin=fov / n,
        mode=params.get("mode", "sigma_to_kappa"),
        preset=params.get("preset", "single_halo"),
    )

    summary = result.get("summary", result)
    certificate = result.get("certificate", {})

    return {
        "status": "completed",
        "mode": params.get("mode", "sigma_to_kappa"),
        "preset": params.get("preset", "single_halo"),
        "summary": _safe_serialize(summary),
        "certificate": _safe_serialize(certificate),
    }


# ── Advanced Anamnesis ──

def _run_anamnesis_fsigma8(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate synthetic memory-positive fsigma8 dataset."""
    # Call the endpoint's internal logic directly
    from api.main import anamnesis_demo_fsigma8

    body = {
        "planted_tau_myr": float(params.get("planted_tau_myr", 41.9)),
        "dt_myr": float(params.get("dt_myr", 5.0)),
        "n_points": int(params.get("n_points", 8)),
        "seed": int(params.get("seed", 0)),
        "include_series": False,  # Keep response compact for AI
    }

    response = anamnesis_demo_fsigma8(body)
    resp_dict = response.dict() if hasattr(response, "dict") else (
        response.model_dump() if hasattr(response, "model_dump") else response
    )

    return {
        "status": "completed",
        "planted_tau_myr": body["planted_tau_myr"],
        "result": _safe_serialize(resp_dict),
    }


def _search_tau(params: Dict[str, Any]) -> Dict[str, Any]:
    """Search over tau candidates with RIS gating."""
    from core.reconstruction.simulator import exponential_kernel
    from core.reconstruction.reconstructor import LCAConfig, lca_reconstruct
    from core.reconstruction.evaluator import emd_1d, build_ris_report
    import numpy as np

    y_obs = np.array(params["y_obs"], dtype=float)
    dt_s = float(params["dt_s"])
    tau_candidates = params["tau_candidates_s"]
    n_kernel = int(params.get("n_kernel", 128))

    scores = []
    best_idx = None
    best_obj = float("inf")

    for i, tau_s in enumerate(tau_candidates):
        kernel = exponential_kernel(n_kernel, tau_s / dt_s)
        cfg = LCAConfig(threshold=0.1, max_iter=1500, dt=0.01)
        recon = lca_reconstruct(y_obs, kernel, cfg)
        emd = emd_1d(np.zeros_like(y_obs), recon)  # source unknown
        residual = float(np.linalg.norm(y_obs - np.convolve(recon, kernel, mode="same")))
        objective = emd + residual

        ris_status = "PASS"
        if emd > float(params.get("emd_warn", 2.0)):
            ris_status = "WARN"
        if emd > float(params.get("emd_fail", 5.0)):
            ris_status = "FAIL"

        scores.append({
            "tau_s": tau_s,
            "emd": emd,
            "residual_norm": residual,
            "objective": objective,
            "ris_status": ris_status,
        })

        if objective < best_obj:
            best_obj = objective
            best_idx = i

    return {
        "status": "completed",
        "best_tau_s": tau_candidates[best_idx] if best_idx is not None else None,
        "best_index": best_idx,
        "scores": scores,
    }


def _fsigma8_resonance_map(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run fsigma8 resonance map via the API endpoint's internal logic."""
    # Build the request payload and call the endpoint logic directly
    from core.schemas import Fsigma8ResonanceMapRequest, Fsigma8DatasetRequest

    data = Fsigma8DatasetRequest(
        z=params["z"],
        fsigma8=params["fsigma8"],
        sigma=params.get("sigma"),
    )

    req = Fsigma8ResonanceMapRequest(
        data=data,
        tau_candidates_myr=params["tau_candidates_myr"],
        leave_one_out=params.get("leave_one_out", True),
    )

    # Import the endpoint's internal function
    from api.main import anamnesis_fsigma8_resonance_map
    response = anamnesis_fsigma8_resonance_map(req)

    # Serialize the response
    resp_dict = response.dict() if hasattr(response, "dict") else response.model_dump()
    return _safe_serialize(resp_dict)


# ── Library & Evidence ──

def _get_library(params: Dict[str, Any], db_store: Any) -> Dict[str, Any]:
    """Browse saved runs in the library."""
    if not db_store:
        return {"error": "Database store not available"}

    limit = int(params.get("limit", 20))
    try:
        runs = db_store.list_runs(limit=limit)
        return {
            "runs": [
                {
                    "run_id": r.get("run_id", ""),
                    "kind": r.get("kind", ""),
                    "status": r.get("status", ""),
                    "created_utc": r.get("created_utc", ""),
                }
                for r in runs
            ],
            "count": len(runs),
        }
    except Exception as exc:
        return {"error": f"Failed to list runs: {exc}"}


def _get_run_details(params: Dict[str, Any], db_store: Any) -> Dict[str, Any]:
    """Get full details for a run."""
    if not db_store:
        return {"error": "Database store not available"}

    run_id = params.get("run_id", "")
    run = db_store.get_run(run_id)
    if run is None:
        return {"error": f"Run {run_id} not found"}

    return _safe_serialize(run)


def _export_evidence_packet(params: Dict[str, Any], db_store: Any) -> Dict[str, Any]:
    """Export a run as a complete evidence packet."""
    if not db_store:
        return {"error": "Database store not available"}

    run_id = params.get("run_id", "")
    run = db_store.get_run(run_id)
    if run is None:
        return {"error": f"Run {run_id} not found"}

    from core.evidence import make_evidence_packet
    packet = make_evidence_packet(run)
    return _safe_serialize(packet)


# ── Anamnesis Reconstruct ──

def _anamnesis_reconstruct(params: Dict[str, Any]) -> Dict[str, Any]:
    """Reconstruct sparse source from shadow signal."""
    from core.reconstruction.simulator import exponential_kernel
    from core.reconstruction.reconstructor import LCAConfig, lca_reconstruct
    from core.reconstruction.evaluator import emd_1d, build_ris_report
    import numpy as np

    signal = np.array(params["signal"], dtype=float)
    tau_s = float(params.get("kernel_tau_s", 30.0))
    dt_s = float(params.get("kernel_dt_s", 1.0))
    n_kernel = int(params.get("n_kernel", 128))
    lam = float(params.get("lam", 0.02))
    nonneg = params.get("nonnegative", True)

    kernel = exponential_kernel(n_kernel, tau_s / dt_s)
    cfg = LCAConfig(threshold=lam, max_iter=4000, dt=0.05, nonnegative=nonneg)
    recon = lca_reconstruct(signal, kernel, cfg)

    # Compute quality metrics
    recon_obs = np.convolve(recon, kernel, mode="same")
    residual_norm = float(np.linalg.norm(signal - recon_obs))
    emd = emd_1d(np.zeros_like(signal), recon)
    ris = build_ris_report(np.zeros_like(signal), recon, signal, kernel, emd)

    return {
        "status": "completed",
        "n_samples": len(signal),
        "n_kernel": n_kernel,
        "tau_s": tau_s,
        "residual_norm": residual_norm,
        "emd": emd,
        "ris_summary": {
            "status": ris.get("status"),
            "recovery_score": ris.get("recovery_score"),
            "spike_recall": ris.get("spike_recall"),
        },
        "reconstructed_source_nnz": int(np.count_nonzero(recon > 0.01 * np.max(recon))) if np.max(recon) > 0 else 0,
    }


# ── fsigma8 Tau Search ──

def _search_tau_fsigma8(params: Dict[str, Any]) -> Dict[str, Any]:
    """Search tau from fsigma8 observational data."""
    from core.schemas import Fsigma8TauSearchRequest, Fsigma8DatasetRequest

    data = Fsigma8DatasetRequest(
        z=params["z"],
        fsigma8=params["fsigma8"],
        sigma=params.get("sigma"),
    )

    req = Fsigma8TauSearchRequest(
        data=data,
        tau_candidates_myr=params["tau_candidates_myr"],
        dt_myr=float(params.get("dt_myr", 5.0)),
        prior=params.get("prior", "smooth"),
    )

    from api.main import anamnesis_search_tau_fsigma8
    response = anamnesis_search_tau_fsigma8(req)

    resp_dict = response.dict() if hasattr(response, "dict") else response.model_dump()
    return _safe_serialize(resp_dict)


# ── Publish & Public Access ──

def _publish_run(params: Dict[str, Any], db_store: Any) -> Dict[str, Any]:
    """Publish a run as an immutable snapshot."""
    if not db_store:
        return {"error": "Database store not available"}

    run_id = params.get("run_id", "")
    run = db_store.get_run(run_id)
    if run is None:
        return {"error": f"Run {run_id} not found"}

    try:
        result = db_store.publish_run(run_id)
        return _safe_serialize(result)
    except Exception as exc:
        return {"error": f"Failed to publish: {exc}"}


def _get_published(params: Dict[str, Any], db_store: Any) -> Dict[str, Any]:
    """Retrieve a published snapshot by slug."""
    if not db_store:
        return {"error": "Database store not available"}

    slug = params.get("slug", "")
    revision = params.get("revision")

    try:
        if revision is not None:
            result = db_store.get_published(slug, int(revision))
        else:
            result = db_store.get_published_latest(slug)
        if result is None:
            return {"error": f"Published slug '{slug}' not found"}
        return _safe_serialize(result)
    except Exception as exc:
        return {"error": f"Failed to get published: {exc}"}


# ── GRUTipedia Management ──

def _list_grutipedia(params: Dict[str, Any], db_store: Any) -> Dict[str, Any]:
    """List all GRUTipedia topics."""
    if not db_store:
        return {"error": "Database store not available"}

    limit = int(params.get("limit", 50))
    try:
        topics = db_store.list_topics(limit=limit)
        return {
            "topics": [
                {
                    "slug": t.get("slug", ""),
                    "title": t.get("title", ""),
                    "tags": t.get("tags", []),
                }
                for t in topics
            ],
            "count": len(topics),
        }
    except Exception as exc:
        return {"error": f"Failed to list topics: {exc}"}


# ── Full Canon ──

def _get_full_canon(params: Dict[str, Any], engine: Any) -> Dict[str, Any]:
    """Get the complete GRUT canon configuration."""
    if engine is None:
        return {"error": "GRUT engine not initialized"}

    canon = engine.canon
    try:
        # Build a comprehensive canon summary
        constants = {}
        for cid, entry in canon.constants_by_id.items():
            constants[cid] = {
                "value": entry.get("value"),
                "units": entry.get("units", ""),
                "symbol": entry.get("symbol", ""),
                "description": entry.get("description", ""),
                "status": entry.get("status", ""),
                "bounds": entry.get("bounds"),
            }

        return {
            "canon_hash": canon.hash(),
            "n_constants": len(constants),
            "constants": constants,
            "operators": _safe_serialize(getattr(canon, "operators", [])),
            "equations": _safe_serialize(getattr(canon, "equations", [])),
        }
    except Exception as exc:
        return {"error": f"Failed to read canon: {exc}"}


# ── Parameter Sweep ──

def _generate_sweep(params: Dict[str, Any], engine: Any) -> Dict[str, Any]:
    """Run alpha_mem parameter sweep."""
    if engine is None:
        return {"error": "GRUT engine not initialized"}

    from grut.canon_override import override_canon
    from grut.engine import GRUTEngine

    grid_str = params.get("grid", "0.0,0.1,0.333333333,0.5,1.0")
    grid = [float(v.strip()) for v in grid_str.split(",")]
    start_z = float(params.get("start_z", 2.0))
    dt_years = float(params.get("dt_years", 100000))
    steps = int(params.get("steps", 300))

    results = []
    for i, alpha_mem in enumerate(grid):
        try:
            new_canon = override_canon(engine.canon, {"PARAM_ALPHA_MEM": alpha_mem})
            sweep_engine = GRUTEngine(new_canon, determinism_mode="STRICT")

            input_state = {"a": 1.0, "H": 1e-10, "rho": 0.3, "p": 0.0, "M_X": 0.0, "rho_m": 0.3}
            run_config = {"dt_years": dt_years, "steps": steps, "integrator": "RK4", "start_z": start_z}
            assumptions = {"growth_enabled": True}

            outputs, cert = sweep_engine.run(input_state, run_config=run_config, assumption_toggles=assumptions)

            hz_data = outputs.get("OBS_HZ_001", {}).get("data", [])
            fs8_data = outputs.get("OBS_FS8_001", {}).get("data", [])

            results.append({
                "index": i,
                "alpha_mem": alpha_mem,
                "status": "completed",
                "canon_hash": cert.get("engine_signature", {}).get("canon_hash", ""),
                "repro_hash": cert.get("repro_hash", ""),
                "hz_points": len(hz_data),
                "fs8_points": len(fs8_data),
                "viability": _safe_serialize(outputs.get("viability", {})),
            })
        except Exception as exc:
            results.append({
                "index": i,
                "alpha_mem": alpha_mem,
                "status": "error",
                "error": str(exc),
            })

    completed = sum(1 for r in results if r["status"] == "completed")
    return {
        "preset": params.get("preset", "matter_only"),
        "grid": grid,
        "results": results,
        "completed": completed,
        "total": len(grid),
    }


# ── Quantum Evidence Packet ──

def _build_quantum_evidence_packet(params: Dict[str, Any]) -> Dict[str, Any]:
    """Build a Quantum Evidence Packet with decoherence slope analysis."""
    import csv
    import io
    import tempfile
    from pathlib import Path

    from tools.build_quantum_evidence_packet import build_quantum_evidence_packet

    canon_path = str(Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json")

    config = {
        "canon_path": canon_path,
        "alpha_vac": float(params.get("alpha_vac", 1.0 / 3.0)),
        "l_m": float(params.get("l_m", 1e-6)),
        "omega_benchmark": float(params.get("omega_benchmark", 1000.0)),
        "omega_scan_points": int(params.get("omega_scan_points", 50)),
        "mass_scan_points": int(params.get("mass_scan_points", 40)),
        "determinism_mode": "STRICT",
    }

    with tempfile.TemporaryDirectory(prefix="quantum_") as tmpdir:
        result = build_quantum_evidence_packet(config, tmpdir)

        # Read the summary CSV for slope data
        summary_path = Path(tmpdir) / "summary.csv"
        slopes = {}
        if summary_path.exists():
            with summary_path.open() as f:
                reader = csv.DictReader(f)
                for row in reader:
                    slopes = {
                        "slope_self_consistent": float(row.get("slope_self_consistent", 0)),
                        "slope_controlled": float(row.get("slope_controlled", 0)),
                        "slope_dp_reference": float(row.get("slope_dp_reference", 0)),
                        "intercept_self_consistent": float(row.get("intercept_self_consistent", 0)),
                        "intercept_controlled": float(row.get("intercept_controlled", 0)),
                    }
                    break  # only one row

        cert = result.get("certificate", {})

    return {
        "status": "completed",
        "slopes": slopes,
        "certificate": {
            "tool_version": cert.get("tool_version", ""),
            "canon_hash": cert.get("canon_hash", ""),
            "input_hash": cert.get("input_hash", ""),
            "output_digest": cert.get("output_digest", ""),
        },
        "config": {
            "alpha_vac": config["alpha_vac"],
            "l_m": config["l_m"],
            "omega_benchmark": config["omega_benchmark"],
        },
    }


# ── Rotation Curve Packet ──

def _run_rotation_packet(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run a rotation curve packet on galaxy data."""
    import tempfile
    from pathlib import Path

    from tools.run_rotation_packet import run_rotation_packet

    data_path = params.get("data_path", "")
    if not data_path:
        return {"error": "data_path is required"}

    # Resolve relative paths from project root
    project_root = Path(__file__).resolve().parent.parent
    resolved = Path(data_path)
    if not resolved.is_absolute():
        resolved = project_root / data_path
    if not resolved.exists():
        return {"error": f"Data file not found: {data_path}"}

    config = {
        "data_path": str(resolved),
        "response_model": params.get("response_model", "identity"),
        "ups_star": float(params.get("ups_star", 1.0)),
        "ups_bulge": float(params.get("ups_bulge", 1.0)),
        "r0_policy": params.get("r0_policy", "median_radius"),
    }
    if params.get("alpha_mem") is not None:
        config["alpha_mem"] = float(params["alpha_mem"])
    if params.get("r0_kpc") is not None:
        config["r0_kpc"] = float(params["r0_kpc"])

    with tempfile.TemporaryDirectory(prefix="rotation_") as tmpdir:
        result = run_rotation_packet(config, tmpdir)

    metrics = result.get("metrics", {})
    cert = result.get("certificate", {})

    return {
        "status": "completed",
        "response_model": metrics.get("response_model"),
        "alpha_mem": metrics.get("alpha_mem"),
        "r0_policy": metrics.get("r0_policy"),
        "r0_value_used": metrics.get("r0_value_used"),
        "baseline_rms": metrics.get("baseline", {}).get("rms_residual"),
        "grut_rms": metrics.get("grut", {}).get("rms_residual"),
        "baseline_chi_like": metrics.get("baseline", {}).get("chi_like"),
        "grut_chi_like": metrics.get("grut", {}).get("chi_like"),
        "data_stats": metrics.get("data_stats"),
        "certificate": {
            "tool_version": cert.get("tool_version", ""),
            "input_hash": cert.get("input_hash", ""),
            "output_digest": cert.get("output_digest", ""),
        },
    }


# ── Cluster Profile Packet ──

def _run_cluster_profile_packet(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run a cluster lensing profile packet."""
    import tempfile
    from pathlib import Path

    from tools.run_cluster_profile_packet import run_cluster_profile_packet

    kappa_path = params.get("kappa_path", "")
    if not kappa_path:
        return {"error": "kappa_path is required"}

    project_root = Path(__file__).resolve().parent.parent

    def _resolve(p: str) -> str:
        pp = Path(p)
        if not pp.is_absolute():
            pp = project_root / p
        return str(pp)

    config = {
        "kappa_path": _resolve(kappa_path),
        "center_mode": params.get("center_mode", "com_positive"),
        "profile_bins": int(params.get("profile_bins", 20)),
        "compare_to_model": params.get("compare_to_model", False),
        "model_response": params.get("model_response", "grut_gate_kspace_v0"),
        "fov_arcmin": float(params.get("fov_arcmin", 20.0)),
    }
    if params.get("gamma1_path"):
        config["gamma1_path"] = _resolve(params["gamma1_path"])
    if params.get("gamma2_path"):
        config["gamma2_path"] = _resolve(params["gamma2_path"])

    with tempfile.TemporaryDirectory(prefix="profile_") as tmpdir:
        result = run_cluster_profile_packet(config, tmpdir)

    metrics = result.get("metrics", {})
    cert = result.get("certificate", {})

    # Build a compact summary of profile metrics
    profile_summary = {}
    if metrics:
        for key in ("kappa", "gamma_t"):
            if key in metrics:
                profile_summary[key] = metrics[key]

    return {
        "status": "completed",
        "center_mode": config["center_mode"],
        "profile_bins": config["profile_bins"],
        "compare_to_model": config["compare_to_model"],
        "model_response": config["model_response"],
        "profile_metrics": profile_summary,
        "certificate": {
            "tool_version": cert.get("tool_version", ""),
            "input_hash": cert.get("input_hash", ""),
            "output_digest": cert.get("output_digest", ""),
        },
    }


# ── Audit ──

def _run_audit(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run the full audit suite (audit_all.py)."""
    import subprocess
    import os
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent
    audit_script = project_root / "tools" / "audit_all.py"

    if not audit_script.exists():
        return {"error": "audit_all.py not found"}

    # Find python
    python = str(project_root / ".venv" / "bin" / "python3")
    import shutil
    if not Path(python).exists():
        python = shutil.which("python3") or "python3"

    env = dict(os.environ)
    env["PYTHONPATH"] = f"{project_root / '.venv' / 'lib' / 'python3.9' / 'site-packages'}:{project_root}"

    try:
        result = subprocess.run(
            [python, str(audit_script)],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=120,
            env=env,
        )

        output = result.stdout.strip()

        # Parse the output for key info
        passed = "AUDIT PASS" in output
        canon_hash = ""
        repro_hash = ""
        for line in output.split("\n"):
            if line.startswith("canon_hash:"):
                canon_hash = line.split(":", 1)[1].strip()
            elif line.startswith("repro_hash:"):
                repro_hash = line.split(":", 1)[1].strip()

        return {
            "status": "PASS" if passed else "FAIL",
            "canon_hash": canon_hash,
            "repro_hash": repro_hash,
            "output": output,
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Audit timed out after 120 seconds"}
    except Exception as exc:
        return {"error": f"Audit failed: {exc}"}


# ── Evidence Index ──

# Deterministic discovery patterns for artifact directories.
# Order matters: more specific patterns first to avoid double-counting.
_EVIDENCE_DIR_PATTERNS = [
    "evidence_*",
    "_audit_*",
    "*_packet_*",
    "*_batch_*",
    "cluster_prediction_*",
    "cluster_sample",
    "quantum_boundary*",
    "lensing_packet_*",
    "calibration",
    "sweeps",
]


def _infer_packet_version(folder_name: str) -> str:
    """Infer a packet_version label from the folder name.

    Examples:
        evidence_cluster_v0_6A  -> v0.6A
        lensing_packet_v0_2     -> v0.2
        quantum_boundary        -> (empty -- no version in name)
    """
    import re
    m = re.search(r"v(\d+[._]\d+[A-Za-z0-9_]*)", folder_name)
    if m:
        raw = m.group(1).replace("_", ".")
        return f"v{raw}"
    return ""


def _find_nis_certificates(packet_dir) -> list:
    """Find all NIS certificate JSON files under a packet directory (max depth 4)."""
    from pathlib import Path
    certs = []
    for nis_path in sorted(packet_dir.rglob("nis_*certificate*.json")):
        # Enforce max depth from packet_dir
        try:
            rel = nis_path.relative_to(packet_dir)
            if len(rel.parts) > 4:
                continue
            nis_data = json.loads(nis_path.read_text())
            certs.append({
                "relpath": str(rel),
                "data": nis_data,
            })
        except Exception:
            continue
    return certs


def _build_packet_entry(idx_path, project_root) -> Dict[str, Any]:
    """Build a single packet entry from a PACKET_INDEX.json path."""
    idx_data = json.loads(idx_path.read_text())
    packet_dir = idx_path.parent
    rel_path = str(packet_dir.relative_to(project_root))

    # ── Certificate discovery ──
    # Try embedded certificate keys first, then external NIS files.
    cert_info: Dict[str, Any] = {}
    cert_relpath = ""

    # Check for embedded certificate in PACKET_INDEX.json
    for cert_key in ("profile_packet_certificate", "gas_offset_packet",
                     "certificate", "nis_certificate"):
        candidate = idx_data.get(cert_key, {})
        if isinstance(candidate, dict):
            # gas_offset_packet nests under .certificate
            if "certificate" in candidate and isinstance(candidate["certificate"], dict):
                candidate = candidate["certificate"]
            if candidate.get("tool_version") or candidate.get("input_hash"):
                cert_info = candidate
                break

    # Find external NIS certificate files
    nis_certs = _find_nis_certificates(packet_dir)
    if not cert_info and nis_certs:
        cert_info = nis_certs[0]["data"]
        cert_relpath = nis_certs[0]["relpath"]
    elif nis_certs:
        # Merge: fill in any fields the embedded cert is missing
        nis_data = nis_certs[0]["data"]
        for fill_key in ("tool_version", "input_hash", "output_digest",
                         "canon_hash", "repro_hash", "status"):
            if not cert_info.get(fill_key) and nis_data.get(fill_key):
                cert_info[fill_key] = nis_data[fill_key]
        if not cert_relpath:
            cert_relpath = nis_certs[0]["relpath"]

    # ── File list ──
    file_list: list = []
    pf = idx_data.get("packet_files", {})
    for section in ("raw", "processed", "outputs", "outputs_gas"):
        file_list.extend(pf.get(section, []))

    # Alternative: "files" key is a dict of filename→hash
    if not file_list and isinstance(idx_data.get("files"), dict):
        file_list = sorted(idx_data["files"].keys())

    # Alternative: "output_files" key is a list
    if not file_list and isinstance(idx_data.get("output_files"), list):
        file_list = idx_data["output_files"]

    # Fallback: list actual files on disk
    if not file_list:
        for f in sorted(packet_dir.rglob("*")):
            if f.is_file() and f.name != "PACKET_INDEX.json":
                file_list.append(str(f.relative_to(packet_dir)))

    # ── Infer packet_version from folder name or parent path ──
    packet_label = idx_data.get("packet", "")
    packet_version = _infer_packet_version(packet_label) if packet_label else ""
    if not packet_version:
        # Walk the path segments looking for a version string
        for segment in reversed(rel_path.split("/")):
            packet_version = _infer_packet_version(segment)
            if packet_version:
                break

    # ── Provenance hash ──
    provenance_hash = idx_data.get("provenance_hash", "")
    if not provenance_hash:
        oh = idx_data.get("output_hashes", {})
        # Some packets store a PROVENANCE.json hash
        provenance_hash = oh.get("PROVENANCE.json", oh.get("raw/PROVENANCE.json", ""))

    # ── Assemble entry ──
    return {
        "path": rel_path,
        "packet_name": packet_label or rel_path.rsplit("/", 1)[-1],
        "packet_version": packet_version,
        "tool_version": cert_info.get("tool_version", idx_data.get("tool_version", "")),
        "input_hash": cert_info.get("input_hash", idx_data.get("input_hash", "")),
        "output_digest": (
            cert_info.get("output_digest", "")
            or idx_data.get("output_digest", "")
        ),
        "canon_hash": idx_data.get("canon_hash", cert_info.get("canon_hash", "")) or "",
        "repro_hash": idx_data.get("repro_hash", cert_info.get("repro_hash", "")) or "",
        "provenance_hash": provenance_hash,
        "certificate_relpath": cert_relpath,
        "all_certificates": [c["relpath"] for c in nis_certs],
        "status": idx_data.get("status", cert_info.get("status", "")),
        "file_count": len(file_list),
        "file_list": file_list,
    }


def _build_cert_only_entry(nis_path, project_root) -> Dict[str, Any]:
    """Build a packet entry from a standalone NIS certificate (no PACKET_INDEX)."""
    nis_data = json.loads(nis_path.read_text())
    packet_dir = nis_path.parent
    rel_path = str(packet_dir.relative_to(project_root))
    cert_relpath = nis_path.name

    # List files in the same directory
    file_list = []
    for f in sorted(packet_dir.rglob("*")):
        if f.is_file():
            file_list.append(str(f.relative_to(packet_dir)))

    packet_version = _infer_packet_version(rel_path.split("/")[-1])

    return {
        "path": rel_path,
        "packet_name": rel_path.rsplit("/", 1)[-1],
        "packet_version": packet_version,
        "tool_version": nis_data.get("tool_version", ""),
        "input_hash": nis_data.get("input_hash", ""),
        "output_digest": nis_data.get("output_digest", ""),
        "canon_hash": nis_data.get("canon_hash", "") or "",
        "repro_hash": nis_data.get("repro_hash", "") or "",
        "provenance_hash": "",
        "certificate_relpath": cert_relpath,
        "all_certificates": [cert_relpath],
        "status": nis_data.get("status", ""),
        "file_count": len(file_list),
        "file_list": file_list,
    }


def _list_evidence_packets(params: Dict[str, Any]) -> Dict[str, Any]:
    """Scan artifacts for evidence packets and build an Evidence Index.

    Discovery strategy (deterministic, explicit):
      1. Scan artifacts/ for dirs matching each pattern in _EVIDENCE_DIR_PATTERNS.
      2. Scan artifacts/audit/ subdirectories (if include_audit=True).
      3. Within each dir, find PACKET_INDEX.json files (max depth 6).
      4. For dirs with NIS certs but no PACKET_INDEX, create cert-only entries.
      5. Deduplicate by path, sort by path, apply limit/offset pagination.
    """
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent
    artifacts_dir = project_root / "artifacts"

    if not artifacts_dir.exists():
        return {"error": "artifacts/ directory not found"}

    include_audit = params.get("include_audit", True)
    limit = int(params.get("limit", 0))     # 0 = no limit
    offset = int(params.get("offset", 0))   # skip first N

    # ── Collect scan roots ──
    scan_dirs_set: set = set()
    for pattern in _EVIDENCE_DIR_PATTERNS:
        for d in artifacts_dir.glob(pattern):
            if d.is_dir():
                scan_dirs_set.add(d)

    if include_audit:
        audit_dir = artifacts_dir / "audit"
        if audit_dir.exists():
            for d in audit_dir.iterdir():
                if d.is_dir():
                    scan_dirs_set.add(d)

    scan_dirs = sorted(scan_dirs_set)

    # ── Discover packets ──
    seen_paths: set = set()
    packets: list = []

    for scan_dir in scan_dirs:
        # Find PACKET_INDEX.json files (max depth 6)
        idx_found = False
        for idx_path in sorted(scan_dir.rglob("PACKET_INDEX.json")):
            try:
                rel = idx_path.relative_to(artifacts_dir)
                if len(rel.parts) > 7:
                    continue
            except ValueError:
                continue

            pdir = str(idx_path.parent.relative_to(project_root))
            if pdir in seen_paths:
                continue
            seen_paths.add(pdir)
            idx_found = True

            try:
                entry = _build_packet_entry(idx_path, project_root)
                packets.append(entry)
            except Exception as exc:
                packets.append({
                    "path": pdir,
                    "error": str(exc),
                })

        # If no PACKET_INDEX found, look for standalone NIS certs
        if not idx_found:
            for nis_path in sorted(scan_dir.rglob("nis_*certificate*.json")):
                try:
                    rel = nis_path.relative_to(artifacts_dir)
                    if len(rel.parts) > 7:
                        continue
                except ValueError:
                    continue

                pdir = str(nis_path.parent.relative_to(project_root))
                if pdir in seen_paths:
                    continue
                seen_paths.add(pdir)

                try:
                    entry = _build_cert_only_entry(nis_path, project_root)
                    packets.append(entry)
                except Exception as exc:
                    packets.append({
                        "path": pdir,
                        "error": str(exc),
                    })

    # ── Sort and paginate ──
    packets.sort(key=lambda p: p.get("path", ""))
    total = len(packets)

    if offset > 0:
        packets = packets[offset:]
    if limit > 0:
        packets = packets[:limit]

    return {
        "evidence_index": packets,
        "total_packets": total,
        "returned": len(packets),
        "offset": offset,
        "limit": limit if limit > 0 else "all",
        "scanned_directories": [str(d.relative_to(project_root)) for d in scan_dirs],
    }


# ── Release Bundle Builder ──

def _build_release_bundle(params: Dict[str, Any]) -> Dict[str, Any]:
    """Build a Zenodo release bundle from selected evidence packets."""
    import subprocess
    import os
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent
    script = project_root / "tools" / "build_release_bundle.py"

    if not script.exists():
        return {"error": "build_release_bundle.py not found"}

    outdir_name = params.get("outdir", "release_bundle_v0_1")
    outdir = project_root / "artifacts" / outdir_name

    if outdir.exists():
        return {"error": f"Output directory already exists: artifacts/{outdir_name}"}

    # Build command args
    cmd_args = ["--outdir", str(outdir)]

    if params.get("include_all", True):
        cmd_args.append("--all")

    if not params.get("include_audit", True):
        cmd_args.append("--no-audit")

    if not params.get("include_docs", True):
        cmd_args.append("--no-docs")

    python = str(project_root / ".venv" / "bin" / "python3")
    import shutil as _shutil
    if not Path(python).exists():
        python = _shutil.which("python3") or "python3"

    env = dict(os.environ)
    env["PYTHONPATH"] = (
        f"{project_root / '.venv' / 'lib' / 'python3.9' / 'site-packages'}:{project_root}"
    )

    try:
        result = subprocess.run(
            [python, str(script)] + cmd_args,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=300,
            env=env,
        )

        if result.returncode != 0:
            return {
                "error": f"Bundle build failed (exit {result.returncode})",
                "stderr": result.stderr.strip()[-500:],
                "stdout": result.stdout.strip()[-500:],
            }

        # Read the RELEASE_INDEX.json
        index_path = outdir / "RELEASE_INDEX.json"
        if index_path.exists():
            release_index = json.loads(index_path.read_text())
            return {
                "status": "completed",
                "outdir": f"artifacts/{outdir_name}",
                "release_version": release_index.get("release_version", ""),
                "combined_digest": release_index.get("combined_digest", ""),
                "packet_count": release_index.get("packet_count", 0),
                "doc_count": release_index.get("doc_count", 0),
                "created_utc": release_index.get("created_utc", ""),
            }
        else:
            return {
                "status": "completed",
                "outdir": f"artifacts/{outdir_name}",
                "output": result.stdout.strip()[-1000:],
            }

    except subprocess.TimeoutExpired:
        return {"error": "Bundle build timed out after 300 seconds"}
    except Exception as exc:
        return {"error": f"Bundle build failed: {exc}"}


def _verify_release_bundle(params: Dict[str, Any]) -> Dict[str, Any]:
    """Verify integrity of a release bundle by recomputing file hashes and
    the combined digest."""
    import hashlib
    import random
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent
    bundle_rel = params.get("bundle_dir", "artifacts/release_bundle_v0_1")
    bundle_dir = project_root / bundle_rel
    sample_size = params.get("sample_size", 10)
    expected_digest = params.get("expected_digest", "")

    index_path = bundle_dir / "RELEASE_INDEX.json"
    if not index_path.exists():
        return {"error": f"RELEASE_INDEX.json not found in {bundle_rel}"}

    try:
        release_index = json.loads(index_path.read_text())
    except Exception as exc:
        return {"error": f"Failed to read RELEASE_INDEX.json: {exc}"}

    # ── Collect all (file_path, expected_hash) pairs from the index ──
    all_files: list = []
    for pkt in release_index.get("packets", []):
        bundle_path = pkt.get("bundle_path", "")
        for fname, fhash in pkt.get("file_hashes", {}).items():
            abs_path = bundle_dir / bundle_path / fname
            all_files.append((str(abs_path), fhash, f"{bundle_path}/{fname}"))

    # Also include docs
    for doc_name, doc_hash in release_index.get("docs", {}).items():
        abs_path = bundle_dir / "docs" / doc_name
        all_files.append((str(abs_path), doc_hash, f"docs/{doc_name}"))

    if not all_files:
        return {"error": "No files found in RELEASE_INDEX.json"}

    # ── Sample files for hash verification ──
    actual_sample = min(sample_size, len(all_files))
    random.seed(42)  # deterministic sample for reproducibility
    sampled = random.sample(all_files, actual_sample)

    sampled_results: list = []
    mismatches: list = []

    for abs_path, expected_hash, rel_label in sampled:
        p = Path(abs_path)
        if not p.exists():
            entry = {
                "file": rel_label,
                "expected": expected_hash,
                "actual": "FILE_NOT_FOUND",
                "match": False,
            }
            sampled_results.append(entry)
            mismatches.append(entry)
            continue

        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        actual_hash = h.hexdigest()

        entry = {
            "file": rel_label,
            "expected": expected_hash,
            "actual": actual_hash,
            "match": actual_hash == expected_hash,
        }
        sampled_results.append(entry)
        if not entry["match"]:
            mismatches.append(entry)

    # ── Recompute combined digest ──
    digest_parts = []
    for pkt in sorted(
        release_index.get("packets", []),
        key=lambda e: e.get("source_path", e.get("path", "")),
    ):
        od = pkt.get("output_digest", "")
        if od:
            digest_parts.append(od)
    for doc_name in sorted(release_index.get("docs", {}).keys()):
        digest_parts.append(release_index["docs"][doc_name])

    recomputed_digest = hashlib.sha256(
        "|".join(digest_parts).encode("utf-8")
    ).hexdigest()

    stored_digest = release_index.get("combined_digest", "")

    result: Dict[str, Any] = {
        "bundle_dir": bundle_rel,
        "total_files_in_index": len(all_files),
        "sampled_files": sampled_results,
        "mismatches": mismatches,
        "mismatch_count": len(mismatches),
        "stored_combined_digest": stored_digest,
        "recomputed_combined_digest": recomputed_digest,
        "combined_digest_self_consistent": recomputed_digest == stored_digest,
    }

    if expected_digest:
        result["expected_combined_digest"] = expected_digest
        result["combined_digest_match"] = recomputed_digest == expected_digest

    return result


# ── Radial Collapse ──

def _run_radial_collapse(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run the radial collapse solver (single or mass sweep).

    Calls grut.collapse deterministic ODE integrator — sovereign firewall
    guarantees all physics numbers come from the engine.
    """
    from grut.collapse import (
        compute_collapse,
        compute_mass_sweep,
        compute_schwarzschild_radius,
        compute_freefall_time,
        compute_compactness,
    )

    mode = params.get("mode", "single")

    if mode == "mass_sweep":
        return _run_collapse_sweep(params)

    # ── Single collapse run ──
    M_kg = float(params.get("M_kg", 1e30))
    R0_factor = float(params.get("R0_factor", 10.0))
    R0_m = params.get("R0_m")

    # Compute R0 from factor * r_s if not given explicitly
    r_s = compute_schwarzschild_radius(M_kg)
    if R0_m is not None:
        R0 = float(R0_m)
    else:
        R0 = R0_factor * r_s

    tau0_s = float(params.get("tau0_s", 1.3224e15))
    alpha_vac = float(params.get("alpha_vac", 1.0 / 3.0))
    gamma_diss = float(params.get("gamma_diss", 0.0))
    H_cap = float(params.get("H_cap", 1e10))
    n_steps = int(params.get("n_steps", 100_000))
    local_tau_mode = str(params.get("local_tau_mode", "off"))

    result = compute_collapse(
        M_kg=M_kg,
        R0_m=R0,
        tau0_s=tau0_s,
        alpha_vac=alpha_vac,
        gamma_diss=gamma_diss,
        H_cap=H_cap,
        n_steps=n_steps,
        local_tau_mode=local_tau_mode,
    )

    # Build summary (don't ship entire trajectory arrays to LLM)
    import numpy as _np

    R_final = float(result.R_m[-1]) if len(result.R_m) > 0 else R0
    V_final = float(result.V_ms[-1]) if len(result.V_ms) > 0 else 0.0
    t_ff = compute_freefall_time(R0, M_kg)
    C_initial = compute_compactness(R0, M_kg)
    C_final = compute_compactness(R_final, M_kg)
    K_max = float(_np.max(result.K_kretschner)) if len(result.K_kretschner) > 0 else 0.0
    K_finite = bool(_np.all(_np.isfinite(result.K_kretschner)))

    # Energy ledger: initial and final totals
    E_initial = float(result.E_kinetic[0] + result.E_potential[0]) if len(result.E_kinetic) > 0 else 0.0
    E_final = float(
        result.E_kinetic[-1] + result.E_potential[-1] + result.E_dissipated_cumul[-1]
    ) if len(result.E_kinetic) > 0 else 0.0

    summary: Dict[str, Any] = {
        "status": "completed",
        "mode": "single",
        "params": {
            "M_kg": M_kg,
            "R0_m": R0,
            "R0_over_rs": R0 / r_s if r_s > 0 else None,
            "tau0_s": tau0_s,
            "alpha_vac": alpha_vac,
            "gamma_diss": gamma_diss,
            "H_cap": H_cap,
            "n_steps": n_steps,
        },
        "diagnostics": {
            "r_schwarzschild_m": r_s,
            "t_freefall_s": t_ff,
            "compactness_initial": C_initial,
            "compactness_final": C_final,
        },
        "outcome": {
            "R_final_m": R_final,
            "V_final_m_per_s": V_final,
            "R_final_over_rs": R_final / r_s if r_s > 0 else None,
            "saturated": result.termination_reason == "saturation",
            "termination": result.termination_reason,
            "steps_used": result.n_steps_taken,
            "t_total_s": float(result.t_s[-1]) if len(result.t_s) > 0 else 0.0,
            "l_stiff_activations": result.l_stiff_activations,
        },
        "bounce_exclusion": {
            "all_V_nonpositive": not result.bounce_detected,
            "min_V_m_per_s": float(_np.min(result.V_ms)) if len(result.V_ms) > 0 else 0.0,
            "tier": result.bounce_exclusion_tier,
        },
        "classification": {
            "collapse_class": result.collapse_class,
            "collapse_fraction": result.collapse_fraction,
            "a_eff_min": result.a_eff_min,
            "M_drive_min": result.M_drive_min,
        },
        "qpress_001": {
            "force_balance_residual": result.force_balance_residual,
            "R_eq_predicted": result.R_eq_predicted,
            "asymptotic_stability_indicator": result.asymptotic_stability_indicator,
            "a_grav_final": result.a_grav_final,
            "a_inward_final": result.a_inward_final,
            "a_outward_final": result.a_outward_final,
            "a_net_final": result.a_net_final,
            "artifact_R_f": result.artifact_R_f,
            "endpoint_motion_class": result.endpoint_motion_class,
            "positive_velocity_episodes": result.positive_velocity_episodes,
            "max_outward_velocity": result.max_outward_velocity,
            "overshoot_count": result.overshoot_count,
            "memory_tracking_ratio_final": result.memory_tracking_ratio_final,
        },
        "trappedness": {
            "max_compactness": result.max_compactness,
            "trapped_at_sat": result.trapped_at_sat,
            "compactness_at_sat": result.compactness_at_sat,
            "ah_crossings": len(result.ah_crossings),
        },
        "curvature": {
            "max_kretschner": K_max,
            "is_finite": K_finite,
            "K_at_sat": result.K_at_sat,
        },
        "timescale_competition": {
            "tau0_over_t_dyn": result.tau0_over_t_dyn,
            "tau_eff_over_t_dyn_final": result.tau_eff_over_t_dyn_final,
        },
        "step_budget": {
            "fraction_used": result.step_budget_fraction,
            "exhausted": result.step_budget_exhausted,
            "t_total_over_t_ff": result.t_total_over_t_ff,
        },
        "energy": {
            "E_initial": E_initial,
            "E_final": E_final,
        },
        "certificate": {
            "determinism": "ODE_RK4_STRICT",
            "solver": "grut.collapse.compute_collapse",
        },
    }

    return summary


def _run_collapse_sweep(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run a mass sweep through the collapse solver."""
    from grut.collapse import compute_mass_sweep, fit_rsat_scaling

    M_min_kg = float(params.get("M_min_kg", 1e20))
    M_max_kg = float(params.get("M_max_kg", 1e35))
    n_masses = int(params.get("n_masses", 8))
    R0_factor = float(params.get("R0_factor", 10.0))
    tau0_s = float(params.get("tau0_s", 1.3224e15))
    alpha_vac = float(params.get("alpha_vac", 1.0 / 3.0))
    gamma_diss = float(params.get("gamma_diss", 0.0))
    H_cap = float(params.get("H_cap", 1e10))
    n_steps = int(params.get("n_steps", 100_000))
    local_tau_mode = str(params.get("local_tau_mode", "off"))

    rows = compute_mass_sweep(
        M_min_kg=M_min_kg,
        M_max_kg=M_max_kg,
        n_masses=n_masses,
        R0_factor=R0_factor,
        tau0_s=tau0_s,
        alpha_vac=alpha_vac,
        gamma_diss=gamma_diss,
        H_cap=H_cap,
        n_steps=n_steps,
        local_tau_mode=local_tau_mode,
    )

    # compute_mass_sweep returns List[Dict], not CollapseResult objects.
    # Each dict has: M_kg, r_s_m, R0_m, r_sat_m, r_sat_over_r_s, t_sat_s,
    #   bounce_detected, K_at_sat, compactness_at_sat, trapped_at_sat,
    #   termination, l_stiff_activations, max_compactness, n_steps_taken
    import numpy as _np

    mass_results = []
    for row in rows:
        mass_results.append({
            "M_kg": row["M_kg"],
            "r_s_m": row["r_s_m"],
            "r_sat_m": row["r_sat_m"],
            "r_sat_over_r_s": row["r_sat_over_r_s"],
            "saturated": row["termination"] == "saturation",
            "termination": row["termination"],
            "bounce_excluded": not row["bounce_detected"],
            "K_at_sat": row["K_at_sat"],
            "compactness_at_sat": row["compactness_at_sat"],
            "trapped_at_sat": row["trapped_at_sat"],
            "max_compactness": row["max_compactness"],
            "steps_used": row["n_steps_taken"],
            "l_stiff_activations": row["l_stiff_activations"],
            # Phase-G refined classification
            "collapse_class": row.get("collapse_class", "unknown"),
            "collapse_fraction": row.get("collapse_fraction", 0.0),
            "a_eff_min": row.get("a_eff_min", 0.0),
            "M_drive_min": row.get("M_drive_min", 0.0),
            "bounce_exclusion_tier": row.get("bounce_exclusion_tier", "unknown"),
            # Timescale competition
            "tau0_over_t_dyn": row.get("tau0_over_t_dyn", 0.0),
            "tau_eff_over_t_dyn_final": row.get("tau_eff_over_t_dyn_final", 0.0),
            # Step-budget diagnostics
            "step_budget_fraction": row.get("step_budget_fraction", 0.0),
            "step_budget_exhausted": row.get("step_budget_exhausted", False),
            "t_total_over_t_ff": row.get("t_total_over_t_ff", 0.0),
            # OP_QPRESS_001 diagnostics
            "force_balance_residual": row.get("force_balance_residual", 0.0),
            "R_eq_predicted": row.get("R_eq_predicted", 0.0),
            "asymptotic_stability_indicator": row.get("asymptotic_stability_indicator", 0.0),
            "endpoint_motion_class": row.get("endpoint_motion_class", "unknown"),
            "a_grav_final": row.get("a_grav_final", 0.0),
            "a_outward_final": row.get("a_outward_final", 0.0),
            "a_net_final": row.get("a_net_final", 0.0),
            "artifact_R_f": row.get("artifact_R_f", 0.0),
            "memory_tracking_ratio_final": row.get("memory_tracking_ratio_final", 0.0),
        })

    # Try to fit r_sat scaling law
    scaling: Dict[str, Any] = {}
    saturated = [r for r in rows if r["termination"] == "saturation" and r["r_sat_m"] is not None]
    if len(saturated) >= 2:
        try:
            masses_arr = _np.array([r["M_kg"] for r in saturated])
            rsats_arr = _np.array([r["r_sat_m"] for r in saturated])
            slope, intercept = fit_rsat_scaling(masses_arr, rsats_arr)
            # Compute R² manually
            logm = _np.log10(masses_arr)
            logr = _np.log10(rsats_arr)
            pred = slope * logm + intercept
            ss_res = _np.sum((logr - pred) ** 2)
            ss_tot = _np.sum((logr - _np.mean(logr)) ** 2)
            r_sq = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
            scaling = {
                "log_slope": slope,
                "log_intercept": intercept,
                "r_squared": r_sq,
                "interpretation": (
                    f"r_sat ~ M^{slope:.3f} (log-log fit, R²={r_sq:.4f})"
                ),
            }
        except Exception:
            scaling = {"error": "Fit failed — insufficient saturated points"}

    return {
        "status": "completed",
        "mode": "mass_sweep",
        "params": {
            "M_min_kg": M_min_kg,
            "M_max_kg": M_max_kg,
            "n_masses": n_masses,
            "R0_factor": R0_factor,
            "tau0_s": tau0_s,
            "alpha_vac": alpha_vac,
            "gamma_diss": gamma_diss,
            "H_cap": H_cap,
        },
        "mass_results": mass_results,
        "summary": {
            "total": len(rows),
            "saturated_count": len(saturated),
            "all_bounce_excluded": all(not r["bounce_detected"] for r in rows),
            "all_K_finite": all(
                r["K_at_sat"] is not None and _np.isfinite(r["K_at_sat"])
                for r in rows if r["termination"] == "saturation"
            ),
        },
        "scaling": scaling,
        "certificate": {
            "determinism": "ODE_RK4_STRICT",
            "solver": "grut.collapse.compute_mass_sweep",
        },
    }
