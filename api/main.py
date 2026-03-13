from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pathlib import Path
import uuid
import hashlib
import numpy as np

from core.constants import GRUTParams
from core.schemas import (
    RunRequest,
    AskRequest,
    AskResponse,
    GrutRunRequest,
    GrutRunResponse,
    GrutCanonResponse,
    ZetaTauScalingRequest,
    ZetaTauScalingResponse,
    CasimirDensitySweepRequest,
    CasimirDensitySweepResponse,
    PTADispersionProbeRequest,
    PTADispersionProbeResponse,
    GlassTransitionSweepRequest,
    GlassTransitionSweepResponse,
)
from core.narrative import build_narrative
from core.engine import run_engine
from core.nis import cfl_gate_or_raise, SovereignCausalError, build_nis_report, compute_cfl, compute_determinism_stamp, MYR_IN_S
from storage.memory_store import InMemoryRunStore
from storage.db import get_store
from core.evidence import make_evidence_packet
from core.experiments.zeta_tau_scaling import run_experiment as run_zeta_tau_scaling
from core.experiments.casimir_density_sweep import run_experiment as run_casimir_density_sweep
from core.experiments.pta_dispersion_probe import run_probe as run_pta_dispersion_probe
from core.experiments.glass_transition import run_experiment as run_glass_transition_sweep
from grut.canon import GRUTCanon
from grut.engine import GRUTEngine
from pydantic import BaseModel
from typing import Optional, List, Literal

from observer.observer_state import ObserverConfigV1
from observer.ui_entropy import UIInteractionWindow, UIEntropyConfig
from observer.sensors import SensorConfig
from observer.info_density import InfoDensityConfig
from observer.observer_state import FrameConfig, compute_observer_state

params = GRUTParams()
store = InMemoryRunStore()
db_store = get_store()

# Seed GRUTipedia canonical topics (if missing)
DEFAULT_TOPICS = [
    {
        "slug": "tau0-memory-window",
        "title": "τ₀ — Memory Window",
        "definition_md": "τ₀ is the model’s memory relaxation window governing how long past sourcing influences present response. Phase I canon uses τ₀ = τ_Λ / S with S = 108π as a consistency check only (H0 remains baseline-defined).",
        "equations_md": "fuzz_fraction = εt/τ₀\n\nτ_eff(z)=τ₀·TAU_FACTOR·(H0/H(z))^p\n\nkernel: K(Δt) = (α/τ₀) exp(-Δt/τ₀) Θ(Δt)",
        "edition": 1,
        "tags": ["core", "numerics"],
    },
    {"slug": "epsilon-fuzz-fraction", "title": "ε — Fuzz Fraction", "definition_md": "εt/τ₀ (fuzz fraction)", "edition": 1, "tags": ["core"]},
    {"slug": "s-phase-boethian-pivot", "title": "S-phase Boethian Pivot", "definition_md": "Boethian pivot concept (short)", "edition": 1, "tags": ["theory"]},
    {"slug": "dissipation-d-and-eobs", "title": "Dissipation D and E_obs", "definition_md": "Dissipation notes", "edition": 1, "tags": ["core"]},
    {"slug": "cfl-causal-gate", "title": "CFL Causal Gate", "definition_md": "CFL gate constraints and usage", "edition": 1, "tags": ["numerics"]},
    {"slug": "nis-and-ris-certificates", "title": "NIS and RIS Certificates", "definition_md": "NIS certificates include determinism_stamp (SHA-256 of inputs + code_version + seed), unit_consistency, fuzz_fraction, provenance, and environment metadata. RIS is used for reconstruction-level audits.", "edition": 1, "tags": ["certificates"]},
    {"slug": "seth-kernel", "title": "Seth Kernel", "definition_md": "Seth Kernel = causal exponential memory kernel used as DRM for Anamnesis Lens.", "edition": 1, "tags": ["anamnesis", "core"]},
    {"slug": "zeta-operator", "title": "Zeta Operator — Riemann Hypothesis & τ₀", "definition_md": "**Important**: This experiment tests scaling hypotheses under pre-registered mappings; it does not prove the Riemann Hypothesis. The observed alignment between τ₀ and zeta zero ordinates is reported via null-model p-values and robustness checks. Any PASS status only means the observed match is statistically unlikely under uniform random hypotheses, not a claim of mathematical truth.", "edition": 1, "tags": ["research", "integrity", "experiments"]},
    {"slug": "evidence-packet-schema", "title": "Evidence Packet Schema", "definition_md": "Evidence packets are canonical, hash-stable bundles with schema `grut-evidence-v1` containing request/response/receipt and a deterministic bundle hash.", "edition": 1, "tags": ["integrity", "publishing"]},
    {"slug": "casimir-density-hypothesis", "title": "Casimir Density Hypothesis", "definition_md": "**Disclaimer**: Numerical correspondence ≠ mechanism. Phase I canon uses α_vac = 1/3 and S = 108π with n_g(0)=√(1+α_vac); H0 is baseline-defined and any inversion is a consistency check only.", "edition": 1, "tags": ["research", "experiments"]},
    {"slug": "alpha-screening-hypothesis", "title": "Alpha Screening Hypothesis", "definition_md": "**Disclaimer**: Numerical correspondence ≠ mechanism. α_vac = 1/3 (vacuum response) is canonical; QED α candidates are non-canonical and only included as optional comparisons.", "edition": 1, "tags": ["research", "experiments"]},
    {"slug": "glass-transition-hypothesis", "title": "Glass Transition Hypothesis", "definition_md": "**Disclaimer**: Numerical correspondence ≠ mechanism. This page tracks evidence packets for the cosmological Deborah sweep (glass-transition hypothesis).", "edition": 1, "tags": ["research", "experiments"]},
]

try:
    db_store.seed_topics(DEFAULT_TOPICS)
except Exception:
    # Non-fatal if seeding fails during certain test harnesses
    pass

app = FastAPI(title="GRUT-RAI Sovereign Engine (Phase F)", version=params.engine_version)


@app.on_event("startup")
def _load_grut_phase2_engine() -> None:
    canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.2.json"
    canon = GRUTCanon(str(canon_path))
    app.state.grut_engine = GRUTEngine(canon, determinism_mode="STRICT")

@app.exception_handler(SovereignCausalError)

def handle_cfl_error(request: Request, exc: SovereignCausalError):
    return JSONResponse(status_code=422, content=exc.payload)

# --- Minimal portal UI (no build step; single static HTML) ---
_UI_FILE = Path(__file__).resolve().parent.parent / "ui" / "index.html"

@app.get("/", include_in_schema=False)
def root():
    # Handy default: open the portal UI
    return {"ok": True, "hint": "Open /ui for the Portal UI, or /docs for Swagger."}

@app.get("/ui", response_class=HTMLResponse, include_in_schema=False)
def ui():
    if not _UI_FILE.exists():
        return HTMLResponse("<h3>UI not found</h3><p>Missing ui/index.html</p>", status_code=500)
    return HTMLResponse(_UI_FILE.read_text(encoding="utf-8"))

@app.get("/health")
def health():
    return {"status": "ok", "engine_version": params.engine_version, "params_hash": params.params_hash()}


@app.post("/grut/run", response_model=GrutRunResponse, tags=["grut"])
def grut_run(req: GrutRunRequest) -> GrutRunResponse:
    engine = app.state.grut_engine
    outputs, cert = engine.run(
        req.input_state,
        run_config=req.run_config or {},
        assumption_toggles=req.assumptions or {},
    )
    return GrutRunResponse(outputs=outputs, certificate=cert)


@app.get("/grut/canon", response_model=GrutCanonResponse, tags=["grut"])
def grut_canon() -> GrutCanonResponse:
    engine = app.state.grut_engine
    meta = engine.canon.data.get("meta", {})
    return GrutCanonResponse(
        canon_hash=engine.canon.canon_hash,
        schema_version=str(meta.get("schema_version", "")),
        phase=str(meta.get("phase", "")),
        status=str(meta.get("status", "")),
    )


def _to_observer_config_v1(obs_in) -> ObserverConfigV1:
    """Convert Pydantic ObserverConfig -> dataclass ObserverConfigV1."""
    if obs_in is None:
        return ObserverConfigV1(profile="monk")

    ui_window = UIInteractionWindow(
        ui_actions=obs_in.ui_window.ui_actions,
        window_s=obs_in.ui_window.window_s,
        avg_param_delta=obs_in.ui_window.avg_param_delta,
    )
    ui_cfg = UIEntropyConfig(
        k_rate=obs_in.ui_cfg.k_rate,
        k_mag=obs_in.ui_cfg.k_mag,
        max_actions_per_s=obs_in.ui_cfg.max_actions_per_s,
    )
    sensor = SensorConfig(
        mode=obs_in.sensor.mode,
        ambient_flux=obs_in.sensor.ambient_flux,
        snapshot_flux=obs_in.sensor.snapshot_flux,
        snapshot_payload=obs_in.sensor.snapshot_payload,
        timestamp_utc=obs_in.sensor.timestamp_utc,
        source=obs_in.sensor.source,
    )
    info_cfg = InfoDensityConfig(
        I_base=obs_in.info_cfg.I_base,
        eta=obs_in.info_cfg.eta,
        eps_min_s=obs_in.info_cfg.eps_min_s,
        I_max=obs_in.info_cfg.I_max,
    )
    frame_cfg = FrameConfig(F_min=obs_in.frame_cfg.F_min, F_max=obs_in.frame_cfg.F_max)

    return ObserverConfigV1(
        profile=obs_in.profile,
        v_obs_m_s=obs_in.v_obs_m_s,
        phi_over_c2=obs_in.phi_over_c2,
        ui_window=ui_window,
        ui_cfg=ui_cfg,
        sensor=sensor,
        info_cfg=info_cfg,
        frame_cfg=frame_cfg,
        enable_observer_modulation=obs_in.enable_observer_modulation,
    )


@app.post("/runs")
def runs(req: RunRequest):
    engine_in = req.engine

    # Compute max v from engine grid
    v_grid_max = 0.0
    if engine_in.v_grid is not None and len(engine_in.v_grid) > 0:
        v_grid_max = float(np.max(np.abs(np.asarray(engine_in.v_grid, dtype=float))))

    # Run engine first? No: CFL gate is first, but needs observer eps_user and v_in.
    obs_cfg = _to_observer_config_v1(req.observer)

    # Minimal internal placeholders for observer classification inputs
    # We don't yet know cap/pivot/I_heat until after engine runs. For CFL we only need eps_user and v_in.
    # So we compute a provisional frame factor + eps_user using neutral values.
    # Then run engine, then recompute full observer state.
    #
    # NOTE: eps_user only depends on eps_t and frame inputs (v_obs, phi). So this is safe.
    MYR_IN_S_LOCAL = MYR_IN_S
    eps_t_s = float(engine_in.eps_t_myr) * MYR_IN_S_LOCAL
    from observer.observer_state import compute_frame_factor
    frame = compute_frame_factor(obs_cfg.v_obs_m_s, obs_cfg.phi_over_c2, obs_cfg.frame_cfg)
    eps_user_s = eps_t_s * float(frame["frame_factor"])

    # v_in for CFL combines engine v_grid and observer v_obs
    v_in = max(float(v_grid_max), abs(float(obs_cfg.v_obs_m_s)))

    # CFL hard-stop gate
    cfl_value = compute_cfl(v_in, eps_user_s, params.L_char_m)
    cfl_gate_or_raise(
        v_in_m_s=v_in,
        dt_used_s=eps_user_s,
        params=params,
        current_eps_t_myr=float(engine_in.eps_t_myr),
        frame_factor=float(frame["frame_factor"]),
    )

    # Phase D: optional observer→dissipation modulation. This does NOT affect CFL,
    # gain bounds, or tau_eff; it only scales D(z) by a bounded factor.
    obs_mod = None
    if obs_cfg is not None and bool(obs_cfg.enable_observer_modulation) and obs_cfg.profile != "monk":
        from observer.ui_entropy import compute_ui_entropy
        from observer.sensors import compute_sensor_flux
        from observer.info_density import compute_I_value
        profile_weights = {"monk": (0.0, 0.0), "astronomer": (0.2, 0.8), "participant": (0.9, 0.1)}
        w_ui, w_sensor = profile_weights.get(obs_cfg.profile, (0.0, 0.0))
        ui = compute_ui_entropy(obs_cfg.ui_window, obs_cfg.ui_cfg)
        sensor = compute_sensor_flux(obs_cfg.sensor)
        deltaS = (w_ui * float(ui["ui_entropy"]) + w_sensor * float(sensor["sensor_flux"]))
        I = compute_I_value(deltaS, eps_user_s, obs_cfg.info_cfg)
        # IMPORTANT (Phase D): engine-level dissipation coupling expects an explicit enable flag.
        # This keeps the coupling opt-in and auditable.
        obs_mod = {
            "enabled": True,
            "deltaS": float(deltaS),
            "I_value": float(I["I_value"]),
            "lambda": float(params.info_coupling_lambda),
        }

    # Core engine
    out, internal = run_engine(engine_in, params, obs_mod=obs_mod)

    # Observer layer (now with real engine diagnostics)
    obs_state = compute_observer_state(
        eps_t_myr=float(engine_in.eps_t_myr),
        tau0_seconds=params.tau0_seconds,
        engine_v_grid_max_m_s=float(v_grid_max),
        cap_engaged_frac=float(internal.get("cap_engaged_frac", 0.0)),
        pivot_intensity=float(internal.get("pivot_intensity", 0.0)),
        I_heat=float(internal.get("D_max", 0.0)),
        fuzz_fraction=float(internal.get("fuzz_fraction", 0.0)),
        obs=obs_cfg,
    )

    # Merge observer diagnostics into internal for NIS report
    internal.update({
        "observer_profile": obs_state["observer_profile"],
        "eps_user_s": obs_state["eps_user_s"],
        "deltaS": obs_state["deltaS"],
        "I_value": obs_state["I"]["I_value"],
        "P_lock": obs_state["P_lock"]["P_lock"],
        "tension_score": obs_state["tension"]["tension_score"],
        "tension_color": obs_state["tension"]["tension_color"],
        "metabolic_state": obs_state["metabolic_state"],
        "ui_entropy": obs_state["ui"]["ui_entropy"],
        "sensor_mode": obs_state["sensor"]["sensor_mode"],
        "sensor_flux": obs_state["sensor"]["sensor_flux"],
        "sensor_snapshot_hash": obs_state["sensor"].get("sensor_snapshot_hash"),
        "sensor_reproducible": obs_state["sensor"].get("sensor_reproducible", True),
        "observer_warnings": obs_state["sensor"].get("sensor_warnings", []),
    })

    # Include observer block in outputs for UI expansion
    out["observer"] = obs_state

    request_dict = req.model_dump()
    determinism_stamp = compute_determinism_stamp(request_dict, params.engine_version, seed=0)
    nis = build_nis_report(
        internal,
        params,
        hz_model=internal.get("Hz_model", "unknown"),
        cfl_value=cfl_value,
        determinism_stamp=determinism_stamp,
        unit_consistency=True,
        provenance={
            "contract": "AI narrates; engine calculates; NIS certifies.",
            "inputs": request_dict,
            "seed": 0,
        },
        safe_mode=bool(internal.get("safe_mode", False)),
        convergence={"status": True, "final_residual": None, "iterations": None},
    )

    run_id = str(uuid.uuid4())
    store.put(run_id, {"output": out, "nis": nis})

    # Auto-save to persistent storage so runs created via /runs are available to the UI
    cmp = None
    try:
        response_dict = {"output": out, "nis": nis}

        # Optional comparison
        if getattr(req, "compare", None) and getattr(req.compare, "enabled", False):
            from core.baselines import grut_f_sigma8_baseline
            from core.metrics import l2_score, delta_score
            baseline_info = grut_f_sigma8_baseline(out)
            if baseline_info is not None:
                # metric L2 between arrays (baseline vs baseline = 0)
                try:
                    score_baseline = l2_score(baseline_info["f_sigma8"], baseline_info["f_sigma8"])
                    # grut series vs baseline
                    score_grut = l2_score(baseline_info["grut"], baseline_info["f_sigma8"])
                    delta = delta_score(score_grut, score_baseline)
                    winner = "tie"
                    if delta < -1e-9:
                        winner = "grut"
                    elif delta > 1e-9:
                        winner = "baseline"
                    cmp = {
                        "metric": req.compare.metric or "l2",
                        "baseline": {"name": baseline_info["name"], "f_sigma8": baseline_info["f_sigma8"]},
                        "grut": {"f_sigma8": baseline_info["grut"]},
                        "delta": {"value": delta, "winner": winner},
                    }
                except Exception:
                    cmp = None

            if cmp is not None:
                response_dict["comparison"] = cmp

        db_store.save_run(
            kind="grut_run",
            request=request_dict,
            response=response_dict,
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status=nis.get("status", "—"),
            run_id=run_id,
        )
    except Exception:
        # Persistence must not interfere with core run behavior; swallow errors
        pass

    # Include comparison in API return when present
    ret = {"run_id": run_id, "output": out, "nis": nis}
    if cmp is not None:
        ret["comparison"] = cmp

    return ret

    return {"run_id": run_id, "output": out, "nis": nis}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """Narrative-first interface.

    Returns:
      - answer.text_markdown: human-readable summary
      - expandable.sections: raw engine + observer + NIS certificate
    """
    # Default run if none provided
    run_req = req.run
    if run_req is None:
        run_req = RunRequest(
            engine={
                "z_grid": [0.0, 0.5, 1.0, 2.0],
                "eps_t_myr": 0.10,
                "growth": {"enable": True},
            },
            observer={"profile": "monk"},
        )

    run_resp = runs(run_req)  # may raise SovereignCausalError
    nis = run_resp["nis"]
    out = run_resp["output"]

    narrative = build_narrative(req.prompt, nis, out)

    equations_md = (
        "**tau_eff(z)** = τ0 · TAU_FACTOR · (H0/H(z))^p\n\n"
        "**S_phase(z)** = 1 / (1 + exp((ln(1+z) − x0)/w))\n\n"
        "**g_raw(z)** = 1 + (1/3) · S_phase(z)\n\n"
        "**L_stiff(χ)** = 1 + ((g_max − 1) · χ) / (χ + σ)\n\n"
        "**g_final(z)** = smooth_min(g_raw(z), L_stiff(χ))\n\n"
        "**fuzz_fraction** = εt / τ0\n\n"
        "**D(z)** = k · fuzz_fraction · Φ(z)   and   **E_obs** = 0.75 · (1 − D)\n\n"
        "**ΔS** = w_ui · UI_entropy + w_sensor · Sensor_flux\n"
        "**I(t)** = I_base · (1 + η · ΔS / max(ε_user, ε_min))\n"
        "**P_lock** = I · (1 − exp(−ε_user/τ0))\n"
    )

    sections = [
        {"label": "Prompt", "content_markdown": (req.prompt or "").strip() or "_(empty)_"},
        {"label": "Narrative synthesis (deterministic)", "content_markdown": narrative["text_markdown"]},
        {"label": "Key equations used", "content_markdown": equations_md},
        {"label": "Engine outputs", "engine": {k: v for k, v in out.items() if k != "observer"}},
        {"label": "Observer layer", "observer": out.get("observer")},
        {"label": "NIS certificate", "nis": nis},
    ]

    answer = {
        "text_markdown": narrative["text_markdown"],
        "headline": narrative["headline"],
        "confidence": narrative["confidence"],
        "badge": {
            "nis": nis.get("status"),
            "metabolic_state": nis.get("metabolic_state"),
            "tension_color": nis.get("tension_color"),
        },
        "tension": {"score": nis.get("tension_score"), "color": nis.get("tension_color")},
        "key": narrative["key"],
        "recommendations": narrative["recommendations"],
    }

    return AskResponse(
        run_id=run_resp["run_id"],
        engine_version=params.engine_version,
        params_hash=params.params_hash(),
        answer=answer,
        expandable={"sections": sections},
    )# =========================
# Anamnesis (Reconstruction Lens)
# =========================

from core.reconstruction.simulator import KernelSpec, exponential_kernel, build_drm_matrix, simulate_shadow, make_sparse_events, make_seth_kernel
from core.reconstruction.reconstructor import LCAConfig, lca_reconstruct, ridge_deconvolution
from core.reconstruction.evaluator import emd_1d, emd_with_mass_ratio, build_ris_report, search_tau_grid, search_tau_with_ris
from core.data_adapter import lookback_time_gyr, resample_uniform, myr_to_s, s_to_myr, gyr_to_s, canonical_dataset_hash
import json
from core.synthetic_fsigma8 import generate_synthetic_fsigma8_dataset
from core.schemas import (
    AnamnesisDemoRequest,
    AnamnesisReconstructRequest,
    AnamnesisResponse,
    AnamnesisTauSearchRequest,
    AnamnesisTauSearchResponse,
    AnamnesisTauCandidateScore,
    AnamnesisKernelCfg,
    AnamnesisLcaCfg,
    Fsigma8DatasetRequest,
    Fsigma8TauSearchRequest,
    Fsigma8TauSearchResponse,
    Fsigma8TauCandidateScore,
    Fsigma8ResonanceMapRequest,
    Fsigma8ResonanceMapResponse,
    Fsigma8PointDiagnostic,
)


@app.post("/anamnesis/demo", tags=["anamnesis"], response_model=AnamnesisResponse)
def anamnesis_demo(body: AnamnesisDemoRequest) -> AnamnesisResponse:
    try:
        # 1) Build a sparse "past" source
        n = int(body.n)
        x_true = np.zeros(n, dtype=float)
        for sp in body.spikes:
            idx = int(sp.index)
            if 0 <= idx < n:
                x_true[idx] += float(sp.amplitude)

        # 2) Forward smear (DRM). Use nested kernel_cfg but allow simple top-level overrides.
        kcfg = body.kernel_cfg if body.kernel_cfg is not None else AnamnesisKernelCfg()
        if getattr(body, "dt_s", None) is not None:
            kcfg.dt_s = float(body.dt_s)
        if getattr(body, "tau_s", None) is not None:
            kcfg.tau_s = float(body.tau_s)
        if getattr(body, "n_kernel", None) is not None:
            kcfg.n_kernel = int(body.n_kernel)

        dt_s = float(kcfg.dt_s)
        tau_s = float(kcfg.tau_s)
        n_kernel = int(kcfg.n_kernel)

        # Use Seth Kernel (causal exponential) for forward DRM
        k = make_seth_kernel(dt_s=dt_s, tau_s=tau_s, n_kernel=n_kernel)
        A = build_drm_matrix(k, n)
        y = A @ x_true

        # Noise: safe seed handling
        seed = int(getattr(body, "seed", 0) or 0)
        if body.noise_std > 0:
            rng = np.random.default_rng(seed)
            y = y + rng.normal(0.0, float(body.noise_std), size=y.shape)

        # 3) Reconstruct with LCA
        lcfg = body.lca_cfg if body.lca_cfg is not None else AnamnesisLcaCfg()
        if getattr(body, "lam", None) is not None:
            lcfg.lam = float(body.lam)
        if getattr(body, "max_iter", None) is not None:
            lcfg.max_iters = int(body.max_iter)
        if getattr(body, "tol", None) is not None:
            lcfg.tol = float(body.tol)
        if getattr(body, "nonnegative", None) is not None:
            lcfg.nonnegative = bool(body.nonnegative)

        # Ensure the LCA uses the same timebase as the forward kernel (dt_s, tau_s)
        cfg = LCAConfig(
            lam=float(lcfg.lam),
            max_iters=int(lcfg.max_iters),
            dt=float(dt_s),
            tau=float(tau_s),
            tol=float(lcfg.tol),
            nonneg=bool(getattr(lcfg, "nonnegative", False)),
        )

        # Compute a canonical kernel hash so we can assert the reconstructor
        # ran against the same forward operator.
        kernel_hash = hashlib.sha256(np.ascontiguousarray(k).tobytes()).hexdigest()

        res = lca_reconstruct(y, A, cfg, kernel_hash=kernel_hash)

        # Expose kernel metadata (Seth Kernel = causal exponential)
        kernel_name = "seth"
        kernel_family = "causal_exponential"
        x_hat = res.x_hat
        diag = {
            "residual_norm": float(res.residual_norm),
            "converged": bool(res.converged),
            "iters": int(res.iters),
            "objective": float(res.objective),
            **res.diagnostics,
        }
        y_hat = A @ x_hat

        # 4) Evaluate
        emd_norm_source, mass_ratio_source, emd_source_pen = emd_with_mass_ratio(
            np.maximum(x_true, 0.0), np.maximum(x_hat, 0.0), dx=dt_s
        )
        emd_norm_shadow, mass_ratio_shadow, emd_shadow_pen = emd_with_mass_ratio(
            np.maximum(y, 0.0), np.maximum(y_hat, 0.0), dx=dt_s
        )

        # Spike recovery diagnostics (top-K)
        injected_idx = list(map(int, np.where(x_true > 0.0)[0].tolist()))
        injected_count = len(injected_idx)
        if injected_count > 0:
            K = injected_count
            topk_idx = list(np.argsort(np.abs(x_hat))[-K:][::-1].astype(int).tolist())
            recovered = len([i for i in topk_idx if i in injected_idx])

            # Also count recovered within a small index tolerance (±2 bins)
            tol_bins = 2
            recovered_within_tol = 0
            for idx in topk_idx:
                for inj in injected_idx:
                    if abs(int(idx) - int(inj)) <= tol_bins:
                        recovered_within_tol += 1
                        break

            recovery_precision = float(recovered) / float(K) if K > 0 else 0.0
            recovery_recall = float(recovered) / float(injected_count) if injected_count > 0 else 0.0
            recovery_within_tol_recall = float(recovered_within_tol) / float(injected_count) if injected_count > 0 else 0.0
        else:
            K = 0
            topk_idx = []
            recovered = 0
            recovered_within_tol = 0
            recovery_precision = 0.0
            recovery_recall = 0.0
            recovery_within_tol_recall = 0.0

        spike_recovery = {
            "injected_count": injected_count,
            "recovered_topk_count": recovered,
            "recovered_topk_within_tol_count": recovered_within_tol,
            "recovery_precision": recovery_precision,
            "recovery_recall": recovery_recall,
            "recovery_within_tol_recall": recovery_within_tol_recall,
            "topk_idx": topk_idx,
        }

        # Prefer source EMD as primary reconstruction metric; apply mass-ratio penalty
        # DRM mismatch guard: ensure the kernel used by the reconstructor matches the
        # kernel we generated for the forward model.
        used_kernel_hash = diag.get("kernel_hash_used_by_reconstructor")
        drm_mismatch = False
        if used_kernel_hash is None or used_kernel_hash != kernel_hash:
            drm_mismatch = True

        ris = build_ris_report(
            emd=emd_source_pen,
            residual_norm=float(diag.get("residual_norm", 0.0)),
            converged=bool(diag.get("converged", False)),
            iters=int(diag.get("iters", 0)),
            lam=float(cfg.lam),
            emd_warn=float(body.emd_warn),
            emd_fail=float(body.emd_fail),
            mass_ratio=float(mass_ratio_source),
            spike_recovery=spike_recovery,
        )

        # If DRM mismatch detected, force a FAIL and annotate with an error code
        if drm_mismatch:
            ris.status = "FAIL"
            ris.warnings.append("DRM_MISMATCH")
            ris.message = "DRM_MISMATCH"
            drm_error = "DRM_MISMATCH"
        else:
            drm_error = None

        # Rename legacy dt/tau fields (explicit) if present in diagnostics
        legacy_dt = diag.pop("dt", None)
        legacy_tau = diag.pop("tau", None)

        diagnostic_out = {
            "effective_dt_s": float(dt_s),
            "effective_tau_s": float(tau_s),
            "effective_n_kernel": int(n_kernel),
            "kernel_hash": kernel_hash,
            "kernel_hash_used_by_reconstructor": used_kernel_hash,
            "lam_used": float(cfg.lam),
            "max_iter_used": int(cfg.max_iters),
            "tol_used": float(cfg.tol),
            "emd_source": float(emd_norm_source),
            "emd_source_penalized": float(emd_source_pen),
            "emd_shadow": float(emd_norm_shadow),
            "emd_shadow_penalized": float(emd_shadow_pen),
            "residual_norm": float(diag.get("residual_norm", 0.0)),
            "spike_recovery": spike_recovery,
            **diag,
        }

        # If legacy dt/tau were present, keep them under explicit legacy_ names
        if legacy_dt is not None:
            diagnostic_out["legacy_dt_default"] = float(legacy_dt)
        if legacy_tau is not None:
            diagnostic_out["legacy_tau_default"] = float(legacy_tau)
        if drm_error is not None:
            diagnostic_out["error_code"] = drm_error

        response = AnamnesisResponse(
            kernel=list(map(float, k.tolist())),
            observed=list(map(float, y.tolist())),
            reconstructed_source=list(map(float, x_hat.tolist())),
            reconstructed_observed=list(map(float, y_hat.tolist())),
            ris=ris.__dict__,
            diagnostic=diagnostic_out,
            kernel_name=kernel_name,
            kernel_family=kernel_family,
        )

        # Auto-save to persistent storage
        request_dict = body.model_dump()
        response_dict = response.model_dump()
        run_id = db_store.save_run(
            kind="anamnesis_demo",
            request=request_dict,
            response=response_dict,
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status=ris.status,
        )

        # Return response with run_id attached
        result = response_dict.copy()
        result["run_id"] = run_id
        return JSONResponse(content=result)
    except Exception as e:
        ctx = {"n": getattr(body, "n", None), "dt_s": getattr(body, "dt_s", None), "tau_s": getattr(body, "tau_s", None), "n_kernel": getattr(body, "n_kernel", None), "lam": getattr(body, "lam", None)}
        return JSONResponse(status_code=500, content={"error": "ANAMNESIS_INTERNAL_ERROR", "message": str(e), "context": ctx})


@app.post("/anamnesis/demo_fsigma8", tags=["anamnesis"])
def anamnesis_demo_fsigma8(body: Optional[dict] = None):
    """Synthetic fsigma8 harness: generates a memory-positive dataset.

    Designed for instrument calibration only; not physical evidence.
    """
    try:
        payload = body or {}
        planted_tau_myr = float(payload.get("planted_tau_myr", 41.9))
        dt_myr = float(payload.get("dt_myr", 5.0))
        span_myr = float(payload.get("span_myr", 600.0))
        n_kernel = int(payload.get("n_kernel", 128))
        n_points = int(payload.get("n_points", 8))
        seed = int(payload.get("seed", 0))
        noise_std = float(payload.get("noise_std", 0.0))
        include_series = bool(payload.get("include_series", True))

        synth = generate_synthetic_fsigma8_dataset(
            planted_tau_myr=planted_tau_myr,
            dt_myr=dt_myr,
            span_myr=span_myr,
            n_kernel=n_kernel,
            n_points=n_points,
            seed=seed,
            noise_std=noise_std,
        )

        diagnostic = dict(synth.diagnostic)
        diagnostic.update({"dataset_label": synth.dataset.get("dataset_label", "fsigma8_synth_memory_positive"), "seed": seed})

        response = {
            "dataset": synth.dataset,
            "diagnostic": diagnostic,
            "planted_tau_myr": planted_tau_myr,
            "dt_myr": dt_myr,
            "span_myr": span_myr,
            "n_kernel": n_kernel,
            "n_points": n_points,
        }

        if include_series:
            response["x_true"] = synth.x_true
            response["y_time"] = synth.y_time

        # Save run to vault for traceability
        run_id = db_store.save_run(
            kind="fsigma8_demo_synthetic",
            request=payload,
            response=response,
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status="PASS",
        )
        response["run_id"] = run_id

        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "FSIGMA8_DEMO_ERROR", "message": str(e)})


@app.post("/anamnesis/reconstruct", tags=["anamnesis"], response_model=AnamnesisResponse)
def anamnesis_reconstruct(body: AnamnesisReconstructRequest) -> AnamnesisResponse:
    y = np.asarray(body.signal, dtype=float).reshape(-1)
    n = y.size

    # Kernel: explicit or generated
    if body.kernel is not None and len(body.kernel) > 0:
        k = np.asarray(body.kernel, dtype=float).reshape(-1)
        dt_s = float(body.kernel_cfg.dt_s) if body.kernel_cfg is not None else float(getattr(body, "dt_s", 1.0))
    else:
        dt_s = float(body.kernel_cfg.dt_s)
        tau_s = float(body.kernel_cfg.tau_s)
        n_kernel = int(body.kernel_cfg.n_kernel)
        # For tau search use Seth Kernel alias
        k = make_seth_kernel(dt_s=dt_s, tau_s=tau_s, n_kernel=n_kernel)

    A = build_drm_matrix(k, n)

    cfg = LCAConfig(
        lam=float(body.lca_cfg.lam),
        max_iters=int(body.lca_cfg.max_iters),
        dt=float(body.lca_cfg.dt),
        tau=float(body.lca_cfg.tau),
        tol=float(body.lca_cfg.tol),
        nonneg=False,
    )

    res = lca_reconstruct(y, A, cfg)
    x_hat = res.x_hat
    diag = {
        "residual_norm": float(res.residual_norm),
        "converged": bool(res.converged),
        "iters": int(res.iters),
        "objective": float(res.objective),
        **res.diagnostics,
    }
    y_hat = A @ x_hat

    # Evaluate against the observed shadow (fit quality)
    emd_shadow = emd_1d(np.maximum(y, 0.0), np.maximum(y_hat, 0.0), dx=dt_s)
    ris = build_ris_report(
        emd=emd_shadow,
        residual_norm=float(diag.get("residual_norm", 0.0)),
        converged=bool(diag.get("converged", False)),
        iters=int(diag.get("iters", 0)),
        lam=float(cfg.lam),
        emd_warn=float(body.emd_warn),
        emd_fail=float(body.emd_fail),
    )

    return AnamnesisResponse(
        kernel=list(map(float, k.tolist())),
        observed=list(map(float, y.tolist())),
        reconstructed_source=list(map(float, x_hat.tolist())),
        reconstructed_observed=list(map(float, y_hat.tolist())),
        ris=ris.__dict__,
        diagnostic={
            "emd_shadow": float(emd_shadow),
            "residual_norm": float(diag.get("residual_norm", 0.0)),
            **diag,
        },
    )


@app.post("/anamnesis/search_tau", tags=["anamnesis"], response_model=AnamnesisTauSearchResponse)
def anamnesis_search_tau(body: AnamnesisTauSearchRequest) -> AnamnesisTauSearchResponse:
    """Search over tau candidates with RIS gating."""
    try:
        y = np.asarray(body.y_obs, dtype=float).reshape(-1)
        n = y.size
        dt_s = float(body.dt_s)

        candidates = [float(t) for t in body.tau_candidates_s]
        if len(candidates) == 0:
            raise HTTPException(status_code=422, detail="tau_candidates_s must not be empty")

        cfg = LCAConfig(
            lam=float(body.lam),
            max_iters=int(body.max_iter),
            tol=float(body.tol),
            nonneg=bool(body.nonnegative),
        )

        def forward_fn(tau_s: float):
            k = exponential_kernel(KernelSpec(tau_s=float(tau_s), dt_s=dt_s, length=int(body.n_kernel)))
            A = build_drm_matrix(k, n)
            return A, {"kernel": k}

        def reconstruct_fn(A, meta=None):
            # Return LCAResult for compatibility with enhanced evaluator
            return lca_reconstruct(y, A, cfg)

        # Run search with RIS gating
        best_idx, scores, ris_summary = search_tau_with_ris(
            y,
            candidates,
            forward_fn=forward_fn,
            reconstruct_fn=reconstruct_fn,
            dx=dt_s,
            emd_warn=float(body.emd_warn),
            emd_fail=float(body.emd_fail),
            residual_warn=float(body.residual_warn),
            residual_fail=float(body.residual_fail),
        )

        # Always include a tau0 baseline (no-memory) candidate
        try:
            from core.baselines import anamnesis_tau0_baseline
            from core.reconstruction.evaluator import emd_1d

            baseline_info = anamnesis_tau0_baseline(y, reconstruct_fn, dx=dt_s)
            # Build baseline score matching others
            emd_shadow = emd_1d(y, baseline_info["y_hat"], dx=dt_s)
            residual_norm = float(baseline_info["residual_norm"])
            objective = emd_shadow + 0.25 * residual_norm
            # RIS logic same as search
            if not baseline_info["converged"]:
                ris_status = "FAIL"
            elif emd_shadow >= float(body.emd_fail) or residual_norm >= float(body.residual_fail):
                ris_status = "FAIL"
            elif emd_shadow >= float(body.emd_warn) or residual_norm >= float(body.residual_warn):
                ris_status = "WARN"
            else:
                ris_status = "PASS"

            baseline_score = {
                "tau_s": 0.0,
                "emd_shadow": float(emd_shadow),
                "residual_norm": float(residual_norm),
                "objective": float(objective),
                "ris_status": ris_status,
                "converged": bool(baseline_info["converged"]),
                "iters": int(baseline_info["iters"]),
                "label": "tau0_baseline",
            }
            scores.append(baseline_score)
        except Exception:
            # Baseline computation must not break search
            pass

        score_objs = [
            AnamnesisTauCandidateScore(**score)
            for score in scores
        ]

        # Recompute best among admissible including baseline if present
        admissible = [i for i, s in enumerate(scores) if s.get("ris_status") in ("PASS", "WARN")]
        best = None
        if admissible:
            best_idx = min(admissible, key=lambda i: scores[i]["objective"])
            best = {
                "tau_s": float(scores[best_idx]["tau_s"]),
                "emd_shadow": float(scores[best_idx]["emd_shadow"]),
                "residual_norm": float(scores[best_idx]["residual_norm"]),
                "ris_status": scores[best_idx]["ris_status"],
            }

        response = AnamnesisTauSearchResponse(
            best_tau_s=ris_summary.get("best_tau_s"),
            best_index=best_idx,
            best=best,
            scores=score_objs,
            ris_summary=ris_summary,
            kernel_name="seth",
            kernel_family="causal_exponential",
        )

        # Add comparison block if baseline present
        try:
            baseline_entry = next((s for s in scores if s.get("label") == "tau0_baseline"), None)
            if baseline_entry is not None and best is not None:
                baseline_obj = float(baseline_entry.get("objective", float("inf")))
                best_obj = float(scores[best_idx]["objective"])
                delta = best_obj - baseline_obj
                winner = "tie"
                if delta < -1e-9:
                    winner = "best"
                elif delta > 1e-9:
                    winner = "baseline"
                response.comparison = {
                    "baseline": {"name": "tau0_baseline", "objective": baseline_obj},
                    "best": {"tau_s": best["tau_s"], "objective": best_obj},
                    "delta": {"value": delta, "winner": winner},
                }
        except Exception:
            pass

        # Auto-save to persistent storage
        request_dict = body.model_dump()
        response_dict = response.model_dump()
        run_id = db_store.save_run(
            kind="anamnesis_search_tau",
            request=request_dict,
            response=response_dict,
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status=ris_summary.get("status", "FAIL"),
        )

        # Return response with run_id attached
        result = response_dict.copy()
        result["run_id"] = run_id
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "TAU_SEARCH_ERROR", "message": str(e)})


@app.post("/anamnesis/search_tau_fsigma8", tags=["anamnesis"], response_model=Fsigma8TauSearchResponse)
def anamnesis_search_tau_fsigma8(body: Fsigma8TauSearchRequest) -> Fsigma8TauSearchResponse:
    """Adapter endpoint: accept z and f_sigma8 dataset, map z->t, resample, and call existing tau search.

    This is instrument-only: it avoids heavy dependencies and uses trapezoid + linear resample.
    """
    try:
        data = body.data
        z = np.asarray(data.z, dtype=float).reshape(-1)
        fs8 = np.asarray(data.fsigma8, dtype=float).reshape(-1)
        sigma = np.asarray(data.sigma, dtype=float).reshape(-1) if data.sigma is not None else None
        if z.size != fs8.size:
            raise HTTPException(status_code=422, detail="z and fsigma8 arrays must have same length")

        cosmo = data.cosmo or {}
        H0 = float(getattr(cosmo, 'H0_km_s_Mpc', getattr(cosmo, 'H0_km_s_Mpc', 67.4))) if hasattr(cosmo, 'H0_km_s_Mpc') or isinstance(cosmo, dict) else float(67.4)
        Om = float(getattr(cosmo, 'Omega_m', getattr(cosmo, 'Omega_m', 0.315))) if hasattr(cosmo, 'Omega_m') or isinstance(cosmo, dict) else float(0.315)
        Ol = 1.0 - Om

        # Compute lookback times (Gyr) and diagnostic
        t_gyr, diag = lookback_time_gyr(z, H0_km_s_Mpc=H0, Omega_m=Om, Omega_lambda=Ol)

        # Ensure monotonicity
        if not np.all(np.diff(np.sort(t_gyr)) >= 0):
            raise HTTPException(status_code=422, detail="Computed lookback times are not monotonic")

        # Resample to uniform dt (convert dt_myr -> Gyr)
        dt_gyr = float(body.dt_myr) / 1000.0
        t_uniform, fs8_uniform = resample_uniform(t_gyr, fs8, dt_gyr)

        # Convert to seconds for solver
        dt_s = myr_to_s(float(body.dt_myr))

        # Prepare observed signal (original scale)
        y_orig = np.asarray(fs8_uniform, dtype=float).reshape(-1)
        n = y_orig.size

        # Optional preprocessing: demean and/or standardize before reconstruction
        preprocess_mean = 0.0
        preprocess_std = 1.0
        y = y_orig.copy()
        if bool(body.demean):
            preprocess_mean = float(np.mean(y))
            y = y - preprocess_mean
        if bool(body.standardize):
            preprocess_std = float(np.std(y))
            if preprocess_std <= 0.0:
                preprocess_std = 1.0
            y = y / preprocess_std

        # Build candidate taus in seconds (from Myr)
        candidates_myr = [float(t) for t in body.tau_candidates_myr]
        candidates_s = [myr_to_s(t) for t in candidates_myr]

        # Use stable integrator parameters for LCA (dt small) — dt_s is large for Myr-scaled data
        cfg = LCAConfig(
            lam=float(body.lam),
            max_iters=int(body.max_iter),
            tol=float(body.tol),
            nonneg=bool(body.nonnegative),
            dt=0.2,
            tau=1.0,
        )

        prior = str(body.prior or "smooth")

        def forward_fn(tau_s: float):
            k = exponential_kernel(KernelSpec(tau_s=float(tau_s), dt_s=float(dt_s), length=int(body.n_kernel)))
            A = build_drm_matrix(k, n)
            return A, {"kernel": k}

        def reconstruct_fn(A, meta=None):
            # Support two priors: 'sparse' uses LCA; 'smooth' uses ridge deconvolution in FFT domain
            if prior == "sparse":
                return lca_reconstruct(y, A, cfg)

            # smooth prior: expect kernel in meta
            k = None
            if meta and isinstance(meta, dict):
                k = meta.get("kernel")
            if k is None:
                # Try to infer kernel from A by summing first column if possible (best-effort)
                try:
                    k = np.asarray(A[:, 0].flatten(), dtype=float)
                except Exception:
                    k = np.zeros(int(body.n_kernel), dtype=float)
            # Perform ridge deconvolution
            res = ridge_deconvolution(y, np.asarray(k, dtype=float), lam2=float(body.lam_smooth), nonneg=bool(body.nonnegative), kernel_hash=None)
            return res

        # Calibrate RIS thresholds per-prior: smooth prior gets a stricter WARN gate
        # to surface near-miss fits; sparse prior gets a looser FAIL gate to avoid
        # over-penalizing residuals on spike-like series.
        emd_warn = float(body.emd_warn)
        emd_fail = float(body.emd_fail)
        residual_warn = float(body.residual_warn)
        residual_fail = float(body.residual_fail)
        if prior == "smooth":
            residual_warn = min(residual_warn, 0.5)
            residual_fail = max(residual_fail, 2.0)
        elif prior == "sparse":
            residual_warn = max(residual_warn, 1.5)
            residual_fail = max(residual_fail, 3.0)

        # Run search with ris gating
        best_idx, scores, ris_summary = search_tau_with_ris(
            y,
            candidates_s,
            forward_fn=forward_fn,
            reconstruct_fn=reconstruct_fn,
            dx=dt_s,
            emd_warn=emd_warn,
            emd_fail=emd_fail,
            residual_warn=residual_warn,
            residual_fail=residual_fail,
            debug_trace=bool(body.debug_trace),
        )

        # Attach labels: convert s->Myr for returned scores and keep audit tau_s
        scores_out = []
        for s in scores:
            s_out = dict(s)
            # Ensure we keep tau_s in seconds for audit
            tau_s_val = float(s_out.get('tau_s', 0.0))
            s_out['tau_s'] = tau_s_val
            # Convert seconds -> Myr using precise conversion
            from core.data_adapter import s_to_myr
            s_out['tau_myr'] = float(s_to_myr(tau_s_val))
            # rename emd_shadow -> emd for schema compatibility
            if 'emd_shadow' in s_out:
                s_out['emd'] = float(s_out.pop('emd_shadow'))

            # Ensure per-candidate diagnostics exist (may be missing for baseline)
            s_out.setdefault('max_abs_x', None)
            s_out.setdefault('nnz_x', None)
            s_out.setdefault('objective_first', None)
            s_out.setdefault('objective_last', None)
            s_out.setdefault('residual_first', None)
            s_out.setdefault('residual_last', None)
            s_out.setdefault('emd_mass_warning', False)

            # Keep iter_trace only when debug_trace requested
            if not bool(body.debug_trace) and 'iter_trace' in s_out:
                s_out.pop('iter_trace', None)

            # Convert y_hat (solver-space) back to original observed units and store as y_hat_original
            if 'y_hat' in s_out:
                try:
                    yhat_arr = np.asarray(s_out.pop('y_hat'), dtype=float).reshape(-1)
                    yhat_orig = (yhat_arr * preprocess_std) + preprocess_mean
                    s_out['y_hat_original'] = list(map(float, yhat_orig.tolist()))
                except Exception:
                    s_out['y_hat_original'] = None

            scores_out.append(s_out)

        # Baseline tau0
        try:
            from core.baselines import anamnesis_tau0_baseline
            baseline_info = anamnesis_tau0_baseline(y, reconstruct_fn, dx=dt_s)
            emd_shadow = emd_1d(y, baseline_info["y_hat"], dx=dt_s)
            residual_norm = float(baseline_info["residual_norm"])
            objective = emd_shadow + 0.25 * residual_norm
            if not baseline_info["converged"]:
                ris_status = "FAIL"
            elif emd_shadow >= emd_fail or residual_norm >= residual_fail:
                ris_status = "FAIL"
            elif emd_shadow >= emd_warn or residual_norm >= residual_warn:
                ris_status = "WARN"
            else:
                ris_status = "PASS"

            baseline_score = {
                "tau_myr": 0.0,
                "tau_s": 0.0,
                "emd": float(emd_shadow),
                "residual_norm": float(residual_norm),
                "objective": float(objective),
                "ris_status": ris_status,
                "converged": bool(baseline_info["converged"]),
                "iters": int(baseline_info["iters"]),
                "label": "tau0_baseline",
                # Diagnostics - best-effort from baseline info
                "max_abs_x": None,
                "nnz_x": None,
                "objective_first": float(objective),
                "objective_last": float(objective),
                "residual_first": float(residual_norm),
                "residual_last": float(residual_norm),
                "emd_mass_warning": False,
            }
            # Attach baseline y_hat_original; prefer exact observed (preprocessed -> original)
            baseline_score['y_hat_original'] = list(map(float, y_orig.tolist()))
            scores_out.append(baseline_score)
        except Exception:
            pass

        # Sanitize numeric fields (replace NaN/inf with large finite values) throughout each score
        def _sanitize_num(x, default=1e6):
            try:
                v = float(x)
                if not np.isfinite(v):
                    return float(default)
                return v
            except Exception:
                return float(default)

        def _sanitize_obj(obj):
            if isinstance(obj, dict):
                out = {}
                for k, v in obj.items():
                    if isinstance(v, (int, float, bool)):
                        if isinstance(v, bool):
                            out[k] = bool(v)
                        else:
                            out[k] = _sanitize_num(v)
                    elif isinstance(v, dict) or isinstance(v, list):
                        out[k] = _sanitize_obj(v)
                    else:
                        out[k] = v
                return out
            elif isinstance(obj, list):
                return [_sanitize_obj(v) for v in obj]
            else:
                return obj

        clean_scores = [_sanitize_obj(s) for s in scores_out]

        # Ensure conservative typing for a few core fields
        for s in clean_scores:
            s['emd'] = _sanitize_num(s.get('emd', 1e6))
            s['residual_norm'] = _sanitize_num(s.get('residual_norm', 1e6))
            s['objective'] = _sanitize_num(s.get('objective', s.get('emd', 1e6)))
            s['converged'] = bool(s.get('converged', False))
            s['iters'] = int(s.get('iters', 0) or 0)

        score_objs = [Fsigma8TauCandidateScore(**s) for s in clean_scores]
        scores_out = clean_scores

        # Recompute best among admissible (in Myr units)
        admissible = [i for i, s in enumerate(scores_out) if s.get("ris_status") in ("PASS", "WARN")]
        best = None
        best_index = None
        if admissible:
            best_index = min(admissible, key=lambda i: scores_out[i]["objective"])
            b = scores_out[best_index]
            best = {"tau_myr": float(b["tau_myr"]), "objective": float(b["objective"]), "emd": float(b.get("emd", 0.0))}

        adapter_diag = {
            "t_lookback_gyr_min": float(np.min(t_gyr)),
            "t_lookback_gyr_max": float(np.max(t_gyr)),
            "dt_used_gyr": float(dt_gyr),
            "dt_used_myr": float(body.dt_myr),
            "n_resampled": int(n),
            "dt_used_s": float(gyr_to_s(float(dt_gyr))),
            "tau_candidates_myr_min": float(np.min(candidates_myr)) if len(candidates_myr)>0 else None,
            "tau_candidates_myr_max": float(np.max(candidates_myr)) if len(candidates_myr)>0 else None,
            "tau_candidates_s_min": float(np.min(candidates_s)) if len(candidates_s)>0 else None,
            "tau_candidates_s_max": float(np.max(candidates_s)) if len(candidates_s)>0 else None,
            "cosmo_params": {"H0_km_s_Mpc": float(H0), "Omega_m": float(Om)},
            "dataset_hash": canonical_dataset_hash(z.tolist(), fs8.tolist(), (sigma.tolist() if sigma is not None else None), {"H0_km_s_Mpc": float(H0), "Omega_m": float(Om)}),
            "preprocess_mean": float(preprocess_mean),
            "preprocess_std": float(preprocess_std),
        }

        # Re-evaluate admissible including baseline and determine best/nonbaseline with baseline-preferring tie-break
        admissible = [i for i, s in enumerate(scores_out) if s.get("ris_status") in ("PASS", "WARN")]
        obj_tol = 1e-12
        best_index_final = None
        best_final = None
        if admissible:
            min_obj = min(scores_out[i]["objective"] for i in admissible)
            tied = [i for i in admissible if abs(scores_out[i]["objective"] - min_obj) <= obj_tol]
            baseline_tied = next((i for i in tied if scores_out[i].get("label") == "tau0_baseline" or scores_out[i].get("tau_myr") == 0.0), None)
            if baseline_tied is not None:
                best_index_final = baseline_tied
            else:
                # fall back to first tied (stable) or smallest tau_myr if desired
                best_index_final = min(tied, key=lambda i: scores_out[i].get("tau_myr", 0.0))
            b = scores_out[best_index_final]
            best_final = {"tau_myr": float(b["tau_myr"]), "objective": float(b["objective"]), "emd": float(b.get("emd", 0.0))}

        # Best nonbaseline candidate among admissible (exclude tau0_baseline), same tie rule but without baseline preference
        nonbaseline_admissible = [i for i in admissible if scores_out[i].get("label") != "tau0_baseline" and scores_out[i].get("tau_myr") != 0.0]
        best_nonbaseline_tau_myr = None
        if nonbaseline_admissible:
            min_obj_nb = min(scores_out[i]["objective"] for i in nonbaseline_admissible)
            tied_nb = [i for i in nonbaseline_admissible if abs(scores_out[i]["objective"] - min_obj_nb) <= obj_tol]
            nb_idx = min(tied_nb, key=lambda i: scores_out[i].get("tau_myr", 0.0))
            best_nonbaseline_tau_myr = float(scores_out[nb_idx]["tau_myr"])

        # Update ris_summary to reflect best among admissible including baseline
        if best_index_final is not None:
            ris_summary["best_tau_s"] = float(scores_out[best_index_final].get("tau_s", 0.0))
            ris_summary["status"] = scores_out[best_index_final].get("ris_status", ris_summary.get("status", "FAIL"))
            ris_summary["message"] = f"Best admissible candidate at index {best_index_final}"
        else:
            ris_summary["best_tau_s"] = None
            ris_summary["status"] = "FAIL"
            ris_summary["message"] = "No admissible candidate including baseline"

        response = Fsigma8TauSearchResponse(
            best_tau_myr=(scores_out[best_index_final]["tau_myr"] if best_index_final is not None else None),
            best_index=best_index_final,
            best=best_final,
            best_nonbaseline_tau_myr=best_nonbaseline_tau_myr,
            scores=score_objs,
            ris_summary=ris_summary,
            comparison=None,
            adapter_diagnostic=adapter_diag,
        )

        # Add comparison block if baseline present
        try:
            baseline_entry = next((s for s in scores_out if s.get("label") == "tau0_baseline"), None)
            if baseline_entry is not None and response.best is not None:
                baseline_obj = float(baseline_entry.get("objective", float("inf")))
                best_obj = float(scores_out[response.best_index]["objective"]) if response.best_index is not None else float(response.best.get("objective", float("inf")))
                delta = best_obj - baseline_obj
                winner = "tie"
                if delta < -1e-9:
                    winner = "best"
                elif delta > 1e-9:
                    winner = "baseline"
                response.comparison = {
                    "baseline": {"name": "tau0_baseline", "objective": baseline_obj},
                    "best": {"tau_myr": response.best_tau_myr, "objective": best_obj},
                    "delta": {"value": delta, "winner": winner},
                }
        except Exception:
            pass

        # Save run
        req_dict = body.model_dump()
        resp_dict = response.model_dump()
        run_id = db_store.save_run(
            kind="fsigma8_tau_search",
            request=req_dict,
            response=resp_dict,
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status=ris_summary.get("status", "FAIL"),
        )

        result = resp_dict.copy()
        result["run_id"] = run_id
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "FSIGMA8_TAU_SEARCH_ERROR", "message": str(e)})


@app.post("/anamnesis/fsigma8_resonance_map", tags=["anamnesis"], response_model=Fsigma8ResonanceMapResponse)
def anamnesis_fsigma8_resonance_map(body: Fsigma8ResonanceMapRequest) -> Fsigma8ResonanceMapResponse:
    """Diagnostic-only resonance map for fsigma8 tau search.

    Runs standard tau search, then computes per-point influence (leave-one-out) without
    altering the underlying solver or selection logic.
    """
    try:
        # Run primary tau search using the existing endpoint logic
        base_req = Fsigma8TauSearchRequest(
            data=body.data,
            dt_myr=body.dt_myr,
            tau_candidates_myr=body.tau_candidates_myr,
            n_kernel=body.n_kernel,
            prior=body.prior,
            lam=body.lam,
            lam_smooth=body.lam_smooth,
            max_iter=body.max_iter,
            tol=body.tol,
            nonnegative=body.nonnegative,
            demean=body.demean,
            standardize=body.standardize,
            emd_warn=body.emd_warn,
            emd_fail=body.emd_fail,
            residual_warn=body.residual_warn,
            residual_fail=body.residual_fail,
            debug_trace=False,
        )

        base_resp = anamnesis_search_tau_fsigma8(base_req)
        base_data = json.loads(base_resp.body)

        # Recompute resampled grid (aligned with search) for per-point diagnostics
        z = np.asarray(body.data.z, dtype=float).reshape(-1)
        fs8 = np.asarray(body.data.fsigma8, dtype=float).reshape(-1)
        sigma_in = np.asarray(body.data.sigma, dtype=float).reshape(-1) if body.data.sigma is not None else None

        cosmo = body.data.cosmo or {}
        H0 = float(getattr(cosmo, 'H0_km_s_Mpc', getattr(cosmo, 'H0_km_s_Mpc', 67.4))) if hasattr(cosmo, 'H0_km_s_Mpc') or isinstance(cosmo, dict) else float(67.4)
        Om = float(getattr(cosmo, 'Omega_m', getattr(cosmo, 'Omega_m', 0.315))) if hasattr(cosmo, 'Omega_m') or isinstance(cosmo, dict) else float(0.315)
        Ol = 1.0 - Om

        t_gyr, _diag = lookback_time_gyr(z, H0_km_s_Mpc=H0, Omega_m=Om, Omega_lambda=Ol)
        dt_gyr = float(body.dt_myr) / 1000.0
        t_uniform, fs8_uniform = resample_uniform(t_gyr, fs8, dt_gyr)
        z_sorted_idx = np.argsort(t_gyr)
        z_sorted = z[z_sorted_idx]
        z_resampled = np.interp(t_uniform, t_gyr[z_sorted_idx], z_sorted)

        if sigma_in is not None and sigma_in.size == z.size:
            # Resample sigma with linear interp; enforce floor to avoid blow-up
            sigma_uniform = np.interp(t_uniform, t_gyr[z_sorted_idx], sigma_in[z_sorted_idx])
            sigma_uniform = np.maximum(sigma_uniform, 1e-6)
        else:
            sigma_uniform = np.ones_like(fs8_uniform)

        # Best candidate diagnostics
        best_index = base_data.get("best_index")
        scores = base_data.get("scores", [])
        best_tau_myr = base_data.get("best_tau_myr")
        best_nonbaseline_tau_myr = base_data.get("best_nonbaseline_tau_myr")
        best_y_hat = None
        if best_index is not None and 0 <= best_index < len(scores):
            best_y_hat = scores[best_index].get("y_hat_original")
        if best_y_hat is None and scores:
            # fall back to first non-baseline with y_hat
            for s in scores:
                if s.get("y_hat_original") is not None:
                    best_y_hat = s.get("y_hat_original")
                    break

        per_point: list[Dict[str, Any]] = []
        n_points = z.size
        # Leave-one-out tau and winner records
        loo_tau: list[Optional[float]] = [None] * n_points
        loo_winner: list[Optional[str]] = [None] * n_points

        base_comp = base_data.get("comparison") or {}
        delta_block = base_comp.get("delta") or {}
        base_winner_raw = delta_block.get("winner")
        if base_winner_raw == "baseline":
            base_winner = "baseline"
        elif base_winner_raw == "tie":
            base_winner = "tie"
        else:
            base_winner = "grut"

        # Optionally run leave-one-out searches
        if bool(body.leave_one_out) and n_points > 2:
            for i in range(n_points):
                mask = np.ones_like(z, dtype=bool)
                mask[i] = False
                z_loo_arr = z[mask]
                fs8_loo_arr = fs8[mask]
                sigma_loo_arr = sigma_in[mask] if sigma_in is not None and sigma_in.size == z.size else None

                dataset_loo = Fsigma8DatasetRequest(
                    z=list(map(float, z_loo_arr.tolist())),
                    fsigma8=list(map(float, fs8_loo_arr.tolist())),
                    sigma=(list(map(float, sigma_loo_arr.tolist())) if sigma_loo_arr is not None else None),
                    dataset_label=body.data.dataset_label,
                    cosmo=body.data.cosmo,
                )
                req_loo = Fsigma8TauSearchRequest(
                    data=dataset_loo,
                    dt_myr=body.dt_myr,
                    tau_candidates_myr=body.tau_candidates_myr,
                    n_kernel=body.n_kernel,
                    prior=body.prior,
                    lam=body.lam,
                    lam_smooth=body.lam_smooth,
                    max_iter=body.max_iter,
                    tol=body.tol,
                    nonnegative=body.nonnegative,
                    demean=body.demean,
                    standardize=body.standardize,
                    emd_warn=body.emd_warn,
                    emd_fail=body.emd_fail,
                    residual_warn=body.residual_warn,
                    residual_fail=body.residual_fail,
                    debug_trace=False,
                )

                try:
                    resp_loo = anamnesis_search_tau_fsigma8(req_loo)
                    data_loo = json.loads(resp_loo.body)
                    tau_loo = data_loo.get("best_tau_myr")
                    loo_tau[i] = tau_loo
                    comp_loo = data_loo.get("comparison") or {}
                    winner_raw = (comp_loo.get("delta") or {}).get("winner")
                    if winner_raw == "baseline":
                        winner_loo_val = "baseline"
                    elif winner_raw == "tie":
                        winner_loo_val = "tie"
                    else:
                        winner_loo_val = "grut" if float(tau_loo or 0.0) != 0.0 else "baseline"
                    loo_winner[i] = winner_loo_val
                except Exception:
                    loo_tau[i] = None
                    loo_winner[i] = None

        # Build per-point diagnostics
        for idx in range(n_points):
            y_obs = float(fs8[idx])
            sigma_val = float(sigma_in[idx]) if sigma_in is not None and sigma_in.size == z.size else None
            t_val = float(t_gyr[idx])
            y_hat_val = None
            if best_y_hat is not None:
                y_hat_val = float(np.interp(t_val, t_uniform, best_y_hat))
            residual_val = y_obs - y_hat_val if y_hat_val is not None else None
            if sigma_val is not None and sigma_val > 0 and residual_val is not None:
                chi2 = float((residual_val / sigma_val) ** 2)
            elif residual_val is not None:
                chi2 = float(residual_val ** 2)
            else:
                chi2 = None

            delta_tau = None
            winner_loo = None
            if body.leave_one_out and idx < len(loo_tau):
                tau_i = loo_tau[idx]
                if tau_i is not None and best_tau_myr is not None:
                    delta_tau = float(tau_i) - float(best_tau_myr)
                winner_loo = loo_winner[idx]

            pd = Fsigma8PointDiagnostic(
                z=float(z[idx]),
                t_lookback_gyr=t_val,
                y_obs=y_obs,
                sigma=sigma_val,
                y_hat=y_hat_val,
                residual=residual_val,
                chi2_contrib=chi2,
                delta_tau_leave_one_out=delta_tau,
                winner_leave_one_out=winner_loo,
            )
            per_point.append(pd)

        # Robustness summary
        delta_vals = [abs(delta) for delta in [p.delta_tau_leave_one_out for p in per_point] if delta is not None]
        max_delta = float(max(delta_vals)) if delta_vals else 0.0
        median_delta = float(np.median(delta_vals)) if delta_vals else 0.0
        flips = 0
        if body.leave_one_out:
            for w in loo_winner:
                if w is not None and base_winner is not None and w != base_winner:
                    flips += 1

        robustness = {
            "max_delta_tau": max_delta,
            "median_delta_tau": median_delta,
            "flips_count": int(flips),
            "base_winner": base_winner,
        }

        evidence = {
            "planted": None,
            "best_tau_myr": best_tau_myr,
            "best_nonbaseline_tau_myr": best_nonbaseline_tau_myr,
            "top_influential_indices": sorted(
                range(len(per_point)),
                key=lambda i: abs(per_point[i].delta_tau_leave_one_out or 0.0),
                reverse=True,
            )[:3],
        }

        links = [
            "grut://topics/tau0-memory-window",
            "grut://topics/nis-and-ris-certificates",
        ]

        adapter_diag = base_data.get("adapter_diagnostic", {})
        dataset_hash = adapter_diag.get("dataset_hash")

        response = Fsigma8ResonanceMapResponse(
            best_tau_myr=best_tau_myr,
            best_nonbaseline_tau_myr=best_nonbaseline_tau_myr,
            winner=base_winner,
            per_point=per_point,
            robustness=robustness,
            adapter_diagnostic=adapter_diag,
            dataset_hash=dataset_hash,
            evidence=evidence,
            links=links,
        )

        # Save run
        run_id = db_store.save_run(
            kind="fsigma8_resonance_map",
            request=body.model_dump(),
            response=response.model_dump(),
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status="PASS",
        )
        response.run_id = run_id
        return response
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "FSIGMA8_RESONANCE_ERROR", "message": str(e)})


# =========================
# Zeta–Tau Scaling Experiment
# =========================

@app.post("/experiments/zeta_tau_scaling", tags=["experiments"], response_model=ZetaTauScalingResponse)
def zeta_tau_scaling(req: ZetaTauScalingRequest) -> ZetaTauScalingResponse:
    """Pre-registered zeta-tau scaling experiment.
    
    Tests whether τ₀ ≈ 41.9 Myr aligns with Riemann zeta zero ordinates
    under dimensionally-honest mappings using cosmological time scales.
    
    Outputs:
    - Certificate with status (PASS/WARN/FAIL)
    - Evidence packet (publishable)
    - Null-model p-value (anti-numerology gate)
    """
    try:
        result = run_zeta_tau_scaling(
            tau0_myr=float(req.tau0_myr),
            H0_km_s_Mpc=float(req.H0_km_s_Mpc),
            zeros_n=int(req.zeros_n),
            eps_hit=float(req.eps_hit),
            null_trials=int(req.null_trials),
            h0_perturb_frac=float(req.h0_perturb_frac),
            seed=int(req.seed),
            Omega_m=float(req.Omega_m),
        )

        # Convert internal dict to response model
        response = ZetaTauScalingResponse(
            status=result["status"],
            best_match=result["best_match"],
            robustness=result["robustness"],
            null_model=result["null_model"],
            tested_counts=result["tested_counts"],
            constants=result["constants"],
            run_id=result.get("run_id", str(uuid.uuid4())),
            message=result.get("message", ""),
            tested_families=result.get("tested_families", []),
        )

        # Save to vault
        request_dict = req.model_dump()
        response_dict = response.model_dump()
        
        run_id = db_store.save_run(
            kind="zeta_tau_scaling",
            request=request_dict,
            response=response_dict,
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status=response.status,
            run_id=response.run_id,
        )
        
        # Update run_id in response (use DB assigned ID)
        response.run_id = run_id

        return response

    except ImportError as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "ZETA_IMPORT_ERROR",
                "message": str(e),
                "hint": "Install mpmath: pip install mpmath",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "ZETA_TAU_SCALING_ERROR", "message": str(e)},
        )


# =========================
# Casimir Density / Alpha Screening Experiment
# =========================

@app.post("/experiments/casimir_density_sweep", tags=["experiments"], response_model=CasimirDensitySweepResponse)
def casimir_density_sweep(req: CasimirDensitySweepRequest) -> CasimirDensitySweepResponse:
    """Instrument-grade Casimir density / alpha screening sweep.

    Reports numerical correspondence and robustness only; no mechanistic claims.
    """
    try:
        alpha_vac = req.alpha_vac
        alpha_scr = req.alpha_scr
        if alpha_vac is not None and alpha_scr is not None:
            if abs(float(alpha_vac) - float(alpha_scr)) > 1e-12:
                raise HTTPException(status_code=400, detail="alpha_vac and alpha_scr differ; provide only one or matching values")
        if alpha_vac is None:
            alpha_vac = float(alpha_scr) if alpha_scr is not None else 1.0 / 3.0

        result = run_casimir_density_sweep(
            tau0_myr=float(req.tau0_myr),
            H0_km_s_Mpc=float(req.H0_km_s_Mpc),
            Omega_lambda=float(req.Omega_lambda),
            h0_min=float(req.h0_min),
            h0_max=float(req.h0_max),
            h0_step=float(req.h0_step),
            omegaL_min=float(req.omegaL_min),
            omegaL_max=float(req.omegaL_max),
            omegaL_step=float(req.omegaL_step),
            alpha_vac=float(alpha_vac),
            seed=int(req.seed),
        )

        response = CasimirDensitySweepResponse(
            status=result["status"],
            computed=result["computed"],
            two_loop_argmin=result["two_loop_argmin"],
            rel_err_S_vs_H0=result["rel_err_S_vs_H0"],
            nis=result["nis"],
            metadata=result["metadata"],
            run_id=str(uuid.uuid4()),
        )

        request_dict = req.model_dump()
        response_dict = response.model_dump()

        run_id = db_store.save_run(
            kind="casimir_density_sweep",
            request=request_dict,
            response=response_dict,
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status=response.status,
            run_id=response.run_id,
        )

        response.run_id = run_id

        # Auto-link GRUTipedia topics on PASS/WARN
        if response.status in ("PASS", "WARN"):
            note = (
                "Numerical correspondence ≠ mechanism. This run reports only numerical matching and robustness."
            )
            for slug in ("casimir-density-hypothesis", "alpha-screening-hypothesis", "tau0-memory-window"):
                try:
                    db_store.add_link(slug, run_id, note)
                except Exception:
                    pass

        return response

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "CASIMIR_DENSITY_SWEEP_ERROR", "message": str(e)},
        )


# =========================
# Glass Transition (Cosmological Deborah Sweep)
# =========================

@app.post("/experiments/glass_transition_sweep", tags=["experiments"], response_model=GlassTransitionSweepResponse)
def glass_transition_sweep(req: GlassTransitionSweepRequest) -> GlassTransitionSweepResponse:
    """Cosmological Deborah sweep (glass transition hypothesis)."""
    try:
        result = run_glass_transition_sweep(
            tau0_myr=float(req.tau0_myr),
            H0_km_s_Mpc=float(req.H0_km_s_Mpc),
            Omega_m=float(req.Omega_m),
            Omega_lambda=float(req.Omega_lambda),
            Omega_r=float(req.Omega_r),
            T_cmb_K=float(req.T_cmb_K),
            z_min=float(req.z_min),
            z_max=float(req.z_max),
            n_samples=int(req.n_samples),
            include_scan_data=bool(req.include_scan_data),
            scan_max_points=int(req.scan_max_points),
            pass_z_min=float(req.pass_z_min),
            pass_z_max=float(req.pass_z_max),
            warn_z_max=float(req.warn_z_max),
        )

        response = GlassTransitionSweepResponse(
            status=result["status"],
            crossing=result["crossing"],
            scan_points=result["scan_points"],
            constants=result["constants"],
            certificate=result["certificate"],
            run_id=str(uuid.uuid4()),
        )

        request_dict = req.model_dump()
        response_dict = response.model_dump()

        run_id = db_store.save_run(
            kind="glass_transition_sweep",
            request=request_dict,
            response=response_dict,
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status=response.status,
            run_id=response.run_id,
        )

        response.run_id = run_id

        note = (
            "Numerical correspondence ≠ mechanism. This run reports only Deborah number crossing." 
            f" Status={response.status}."
        )
        for slug in ("glass-transition-hypothesis", "tau0-memory-window", "evidence-packet-schema"):
            try:
                db_store.add_link(slug, run_id, note)
            except Exception:
                pass

        return response

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "GLASS_TRANSITION_SWEEP_ERROR", "message": str(e)},
        )


# =========================
# PTA Dispersion Probe
# =========================

@app.post("/experiments/pta_dispersion_probe", tags=["experiments"], response_model=PTADispersionProbeResponse)
def pta_dispersion_probe(req: PTADispersionProbeRequest) -> PTADispersionProbeResponse:
    """Black-box falsification probe for PTA-band dispersion."""
    try:
        result = run_pta_dispersion_probe(
            tau0_myr=float(req.tau0_myr),
            alpha_scr=float(req.alpha_scr),
            freqs_hz=[float(f) for f in req.freqs_hz],
            use_group_velocity=bool(req.use_group_velocity),
            f_hf_hz=float(req.f_hf_hz),
            apply_to_gw_propagation=bool(req.apply_to_gw_propagation),
            seed=int(req.seed),
            code_version=params.engine_version,
        )

        response = PTADispersionProbeResponse(
            run_id=result["run_id"],
            timestamp=result["timestamp"],
            status=result["status"],
            min_v_phase_over_c_over_band=result["min_v_phase_over_c_over_band"],
            max_abs_delta_v_phase_over_c_over_band=result["max_abs_delta_v_phase_over_c_over_band"],
            max_abs_delta_v_group_over_c_over_band=result["max_abs_delta_v_group_over_c_over_band"],
            worst_speed_margin_over_band=result["worst_speed_margin_over_band"],
            worst_freq_hz=result["worst_freq_hz"],
            assumptions=result["assumptions"],
            results=result["results"],
            comparisons=result["comparisons"],
            hf_check_100Hz=result["hf_check_100Hz"],
            cited_limits=result["cited_limits"],
            conclusion=result["conclusion"],
            pta_direct_dispersion_bound_present=result["pta_direct_dispersion_bound_present"],
            exclusion_basis=result["exclusion_basis"],
            worst_margin_over_band=result["worst_margin_over_band"],
        )

        request_dict = req.model_dump()
        response_dict = response.model_dump()

        db_store.save_run(
            kind="pta_dispersion_probe",
            request=request_dict,
            response=response_dict,
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status=response.status,
            run_id=response.run_id,
        )

        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "PTA_DISPERSION_PROBE_ERROR", "message": str(e)},
        )


# =========================
# Persistence & Publishing
# =========================

@app.get("/library", tags=["library"])
def get_library(limit: int = 50, offset: int = 0):
    """List recent saved runs."""
    runs = db_store.list_runs(limit=limit, offset=offset)
    return {"runs": runs, "total": len(runs), "limit": limit, "offset": offset}


@app.get("/runs/{run_id}", tags=["library"])
def get_run_details(run_id: str):
    """Retrieve full stored run."""
    run = db_store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/runs/{run_id}/export", tags=["library"])
def export_run(run_id: str):
    """Export run as evidence packet (downloadable JSON)."""
    run = db_store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    packet = make_evidence_packet(
        kind=run["kind"],
        request=run["request"],
        response=run["response"],
        engine_version=run["engine_version"],
        params_hash=run["params_hash"],
        receipt=run["response"].get("nis") or run["response"].get("ris"),
    )

    return JSONResponse(
        content=packet,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=run-{run_id}.json"},
    )


@app.post("/runs/{run_id}/publish", tags=["library"])
def publish_run(run_id: str):
    """Publish run as an immutable snapshot."""
    try:
        publish_info = db_store.create_or_update_publish(run_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "PUBLISH_ERROR", "message": str(e)})

    return {
        "slug": publish_info["slug"],
        "revision": publish_info["revision"],
        "published_hash": publish_info["published_hash"],
        "published_at": publish_info["published_at"],
        "public_url": publish_info["url_latest"],
    }


def _sanitize_published_packet(packet: dict) -> dict:
    # Public view: only expose minimal fields to avoid leaking internal metadata
    return {
        "schema": packet.get("schema", "grut-evidence-v1"),
        "metadata": packet.get("metadata", {}),
        "request": packet.get("request", {}),
        "response": packet.get("response", {}),
        "receipt": packet.get("receipt", {}),
        "bundle_hash": packet.get("bundle_hash") or (packet.get("header") or {}).get("bundle_hash"),
    }


@app.get("/p/{slug}", tags=["library"], response_class=JSONResponse)
def get_published_latest(slug: str):
    """Get latest published snapshot (public view). Returns sanitized packet."""
    published = db_store.get_published_latest(slug)
    if published is None:
        raise HTTPException(status_code=404, detail="Published snapshot not found")

    packet = published["published_json"]
    return _sanitize_published_packet(packet)


@app.get("/p/{slug}/info", tags=["library"], response_class=JSONResponse)
def get_published_info(slug: str):
    """Get metadata + full evidence packet for latest revision (admin-friendly)."""
    published = db_store.get_published_latest(slug)
    if published is None:
        raise HTTPException(status_code=404, detail="Published snapshot not found")
    return {
        "slug": published["slug"],
        "revision": published["revision"],
        "published_hash": published["published_hash"],
        "published_at": published["published_at"],
        "evidence_packet": published["published_json"],
    }


@app.get("/p/{slug}/{revision}/info", tags=["library"], response_class=JSONResponse)
def get_published_revision_info(slug: str, revision: int):
    published = db_store.get_published_revision(slug, revision=revision)
    if published is None:
        raise HTTPException(status_code=404, detail="Published snapshot not found")
    return {
        "slug": published["slug"],
        "revision": published["revision"],
        "published_hash": published["published_hash"],
        "published_at": published["published_at"],
        "evidence_packet": published["published_json"],
    }


@app.get("/p/{slug}/{revision}", tags=["library"], response_class=JSONResponse)
def get_published_revision(slug: str, revision: int):
    """Get specific published revision."""
    published = db_store.get_published_revision(slug, revision=revision)
    if published is None:
        raise HTTPException(status_code=404, detail="Published snapshot not found")

    packet = published["published_json"]
    return _sanitize_published_packet(packet)


# -----------------
# GRUTipedia
# -----------------


class TopicLinkRequest(BaseModel):
    run_id: str
    note_md: Optional[str] = None


class Suggestion(BaseModel):
    type: Literal["topic_link", "info"]
    to_topic: Optional[str] = None
    reason: str
    confidence: Literal["low", "medium", "high"]


class SuggestResponse(BaseModel):
    suggestions: List[Suggestion]


@app.get("/grutipedia", tags=["grutipedia"])
def get_grutipedia(limit: int = 50, offset: int = 0):
    """List available GRUTipedia topics."""
    topics = db_store.list_topics(limit=limit, offset=offset)
    return {"topics": topics, "total": len(topics), "limit": limit, "offset": offset}


@app.get("/grutipedia/{slug}", tags=["grutipedia"])
def get_grutipedia_topic(slug: str):
    t = db_store.get_topic(slug)
    if t is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return t


@app.post("/grutipedia/{slug}/link", tags=["grutipedia"] )
def link_run_to_topic(slug: str, body: TopicLinkRequest):
    # Validate run exists
    run = db_store.get_run(body.run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        db_store.add_link(slug, body.run_id, body.note_md)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"ok": True, "topic": slug, "run_id": body.run_id}


def _collect_suggestions(run: dict) -> List[Suggestion]:
    resp = run.get("response", {}) if isinstance(run, dict) else {}
    kind = (run.get("kind") or "").lower()
    status = (run.get("status") or "").upper()
    err = resp.get("error") or resp.get("error_code") or resp.get("ris_summary", {}).get("error_code")
    error_code = (str(err) if err is not None else "").upper()

    dataset_hash = resp.get("dataset_hash") or (resp.get("adapter_diagnostic") or {}).get("dataset_hash")
    publish_slug = run.get("publish_slug") or resp.get("publish_slug")
    best_tau_myr = resp.get("best_tau_myr") or resp.get("best_nonbaseline_tau_myr")
    winner = resp.get("winner") or (resp.get("ris_summary") or {}).get("winner")

    suggestions: List[Suggestion] = []
    seen: set[str] = set()

    def add(topic: str, reason: str, conf: str = "high"):
        if topic in seen:
            return
        seen.add(topic)
        suggestions.append(Suggestion(type="topic_link", to_topic=topic, reason=reason, confidence=conf))

    # Rules
    if kind.startswith("fsigma8_"):
        add("tau0-memory-window", f"kind={kind}; baseline comparison relevant")
        add("seth-kernel", f"kind={kind}; memory kernel used")
        add("ris-certificate", f"kind={kind}; review RIS/NIS receipt")

    if status == "FAIL" and "CFL" in error_code:
        add("cfl-gate", "status=FAIL with CFL error; resolve gate", conf="medium")

    if publish_slug:
        add("publishing-slugs", f"published as {publish_slug}", conf="medium")

    if dataset_hash:
        add("real-data-adapter-z-to-t", f"dataset_hash={dataset_hash}", conf="medium")

    if kind == "casimir_density_sweep":
        add("tau0-memory-window", f"kind={kind}; τ₀ grounding context", conf="high")
        add("alpha-screening-hypothesis", f"kind={kind}; α-screening candidate", conf="high")
        add("casimir-density-hypothesis", f"kind={kind}; Casimir density sweep", conf="high")
        add("evidence-packet-schema", f"kind={kind}; evidence packet provenance", conf="medium")

    if kind == "glass_transition_sweep":
        add("glass-transition-hypothesis", f"kind={kind}; Deborah sweep", conf="high")
        add("tau0-memory-window", f"kind={kind}; τ₀ grounding context", conf="medium")
        add("evidence-packet-schema", f"kind={kind}; evidence packet provenance", conf="medium")

    # Cap to 3 for MVP
    return suggestions[:3]


@app.get("/suggest/{run_id}", tags=["navigator"], response_model=SuggestResponse)
def suggest(run_id: str):
    """Return deterministic Navigator suggestions for a run."""
    run = db_store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return SuggestResponse(suggestions=_collect_suggestions(run))


# =========================
# Experiments
# =========================


@app.post("/experiments/zeta_tau_scaling", tags=["experiments"], response_model=ZetaTauScalingResponse)
def zeta_tau_scaling(req: ZetaTauScalingRequest):
    """Run Zeta–Tau Scaling experiment: test τ₀ alignment with Riemann zeta zeros."""
    try:
        result = run_zeta_tau_scaling(
            tau0_myr=req.tau0_myr,
            H0_km_s_Mpc=req.H0_km_s_Mpc,
            zeros_n=req.zeros_n,
            eps_hit=req.eps_hit,
            null_trials=req.null_trials,
            h0_perturb_frac=req.h0_perturb_frac,
            seed=req.seed,
            Omega_m=req.Omega_m,
        )

        # Save run to vault
        run_id = db_store.save_run(
            kind="zeta_tau_scaling",
            request=req.model_dump(),
            response=result,
            engine_version=params.engine_version,
            params_hash=params.params_hash(),
            status=result["status"],
        )

        result["run_id"] = run_id

        # Auto-link to zeta-operator topic if status is not FAIL
        if result["status"] in ["PASS", "WARN"]:
            try:
                db_store.add_link(
                    "zeta-operator",
                    run_id,
                    f"τ₀={req.tau0_myr} Myr; p-value={result['null_model']['p_value']:.4f}",
                )
            except Exception:
                pass  # Non-fatal if linking fails

        return ZetaTauScalingResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "ZETA_TAU_SCALING_ERROR", "message": str(e)},
        )

