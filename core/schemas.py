from __future__ import annotations

from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Literal, Dict, Any

# ----------------------------
# Inputs
# ----------------------------

class HzModelConfig(BaseModel):
    """Baseline H(z) provider configuration. Phase B+: flat LCDM."""
    model: Literal["lcdm_flat"] = "lcdm_flat"
    H0_km_s_Mpc: float = 67.36
    Omega_m: float = 0.315
    Omega_lambda: float = 0.6847

class TauScaling(BaseModel):
    TAU_FACTOR: float = 1.0
    p: float = 1.0

class PhaseBridge(BaseModel):
    x0: float = 0.0
    w: float = 0.6

class StiffCap(BaseModel):
    rho_lock: float = 1.0
    sigma_cap: float = 1.0

class DissipationConfig(BaseModel):
    k: float = 1.0
    phi_mode: Literal["unity", "phase_weighted"] = "unity"

class GrowthConfig(BaseModel):
    enable: bool = True
    gamma: float = 0.55
    sigma8: float = 0.83

class EngineInput(BaseModel):
    z_grid: List[float] = Field(..., min_length=2)
    rho_grid: Optional[List[float]] = None
    v_grid: Optional[List[float]] = None

    eps_t_myr: float = 0.10

    hz_model: HzModelConfig = HzModelConfig()
    tau_scaling: TauScaling = TauScaling()
    phase_bridge: PhaseBridge = PhaseBridge()
    stiff_cap: StiffCap = StiffCap()
    dissipation: DissipationConfig = DissipationConfig()
    growth: GrowthConfig = GrowthConfig()


class GrutRunRequest(BaseModel):
    input_state: Dict[str, float]
    run_config: Optional[Dict[str, Any]] = None
    assumptions: Optional[Dict[str, Any]] = None


class GrutRunResponse(BaseModel):
    outputs: Dict[str, Any]
    certificate: Dict[str, Any]


class GrutCanonResponse(BaseModel):
    canon_hash: str
    schema_version: str
    phase: str
    status: str


class RaiChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    mode: Optional[str] = None
    input_state: Optional[Dict[str, float]] = None
    run_config: Optional[Dict[str, Any]] = None
    assumptions: Optional[Dict[str, Any]] = None


class RaiChatResponse(BaseModel):
    session_id: str
    assistant_message: str
    actions_taken: List[str] = Field(default_factory=list)
    grut_outputs: Optional[Dict[str, Any]] = None
    nis_certificate: Optional[Dict[str, Any]] = None
    monad_state: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    reply: Optional[str] = None


class RaiSessionNewResponse(BaseModel):
    session_id: str


class RaiSessionDebugResponse(BaseModel):
    session_id: str
    state: Dict[str, Any]
    events: List[Dict[str, Any]]

# ----------------------------
# Observer layer (Phase C)
# ----------------------------

ObserverProfile = Literal["monk", "astronomer", "participant"]
SensorMode = Literal["off", "ambient", "snapshot"]

class UIInteractionWindow(BaseModel):
    ui_actions: int = 0
    window_s: float = 30.0
    avg_param_delta: float = 0.0

class UIEntropyConfig(BaseModel):
    k_rate: float = 0.4
    k_mag: float = 0.6
    max_actions_per_s: float = 3.0

class SensorConfig(BaseModel):
    mode: SensorMode = "off"
    ambient_flux: float = 0.02
    snapshot_flux: Optional[float] = None
    snapshot_payload: Optional[Dict[str, Any]] = None
    timestamp_utc: Optional[str] = None
    source: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def coerce_snapshot_legacy(cls, data):
        """Accept common legacy/request shapes.

        Allows:
          - mode="recorded" as alias for "snapshot"
          - sensor: {mode:"snapshot", snapshot:{ambient_flux:0.03}}
        """
        if not isinstance(data, dict):
            return data
        if data.get("mode") == "recorded":
            data = dict(data)
            data["mode"] = "snapshot"
        if "snapshot" in data and "snapshot_payload" not in data:
            snap = data.get("snapshot")
            if isinstance(snap, dict):
                data = dict(data)
                data.setdefault("snapshot_payload", snap)
                if data.get("snapshot_flux") is None:
                    if "flux" in snap:
                        data["snapshot_flux"] = snap.get("flux")
                    elif "ambient_flux" in snap:
                        data["snapshot_flux"] = snap.get("ambient_flux")
        return data

class InfoDensityConfig(BaseModel):
    I_base: float = 1.0
    eta: float = 1.0
    eps_min_s: float = 1.0
    I_max: float = 5.0

class FrameConfig(BaseModel):
    F_min: float = 0.5
    F_max: float = 2.0

class ObserverConfig(BaseModel):
    profile: ObserverProfile = "monk"

    v_obs_m_s: float = 0.0
    phi_over_c2: float = 0.0

    ui_window: UIInteractionWindow = UIInteractionWindow()
    ui_cfg: UIEntropyConfig = UIEntropyConfig()

    sensor: SensorConfig = SensorConfig()

    info_cfg: InfoDensityConfig = InfoDensityConfig()
    frame_cfg: FrameConfig = FrameConfig()

    enable_observer_modulation: bool = False

# ----------------------------
# NIS / errors
# ----------------------------

class CFLErrorDiagnostic(BaseModel):
    cfl_value: float
    cfl_max: float
    v_in_m_s: float
    v_limit_m_s: float
    dt_used_s: float
    L_char_m: float
    frame_factor: float
    message: str

class CFLCorrectionLogic(BaseModel):
    required_dt_s: float
    required_eps_t_myr: float
    current_eps_t_myr: float
    slider_min_eps_t_myr: float = 0.0
    slider_target_eps_t_myr: float = 0.0
    recommendations: List[str]

class NISIntegrityFailure(BaseModel):
    status: Literal["NIS_INTEGRITY_FAILURE"] = "NIS_INTEGRITY_FAILURE"
    error_code: Literal["CFL_VIOLATION"] = "CFL_VIOLATION"
    diagnostic: CFLErrorDiagnostic
    correction_logic: CFLCorrectionLogic

class NISReport(BaseModel):
    status: Literal["PASS", "WARN", "FAIL"]

    # Phase I contract fields
    determinism_stamp: Optional[str] = None
    unit_consistency: Optional[bool] = None
    provenance: Optional[Dict[str, Any]] = None
    environment: Optional[Dict[str, Any]] = None
    safe_mode: Optional[bool] = None
    convergence: Optional[Dict[str, Any]] = None

    # Core
    eps_t_myr: float
    fuzz_fraction: float
    cap_engaged_frac: float
    pivot_intensity: float
    I_heat: float

    cfl_value: float
    cfl_max: float

    W_phase: float
    D_eff: float
    handoff_pass: bool
    handoff_required: float = 0.0
    handoff_margin: float = 0.0

    g_min: float
    g_max_obs: float
    kink_metric: float
    z_len: int = 0

    # Observer layer (Phase C)
    observer_profile: ObserverProfile
    eps_user_s: float
    deltaS: float
    I_value: float
    P_lock: float
    tension_score: float
    tension_color: Literal["green", "amber", "red"]
    metabolic_state: Literal["CALM", "STRESS", "PIVOT"]

    ui_entropy: float
    sensor_mode: SensorMode
    sensor_flux: float
    sensor_snapshot_hash: Optional[str] = None
    sensor_reproducible: bool = True

    warnings: List[str] = Field(default_factory=list)

    engine_version: str
    params_hash: str
    hz_model: str

# ----------------------------
# API request / response
# ----------------------------

class CompareRequest(BaseModel):
    enabled: bool = False
    models: Optional[list[str]] = None
    metric: Optional[Literal["l2", "chi2"]] = "l2"


class RunRequest(BaseModel):
    engine: EngineInput
    observer: Optional[ObserverConfig] = None
    compare: Optional[CompareRequest] = None

class RunResponse(BaseModel):
    run_id: str
    output: Dict[str, Any]
    nis: NISReport

class AskRequest(BaseModel):
    prompt: str = ""
    run: Optional[RunRequest] = None

class ExpandableSection(BaseModel):
    label: str
    content_markdown: Optional[str] = None
    engine: Optional[Dict[str, Any]] = None
    observer: Optional[Dict[str, Any]] = None
    nis: Optional[Dict[str, Any]] = None

class AskResponse(BaseModel):
    run_id: str
    engine_version: str
    params_hash: str
    answer: Dict[str, Any]
    expandable: Dict[str, Any]

# =========================
# Anamnesis (Reconstruction Lens)
# =========================


class AnamnesisKernelCfg(BaseModel):
    """Kernel configuration for the reconstruction lens.

    This is intentionally generic: it can represent GRUT's memory smear kernel
    or any causal response used for deconvolution.
    """

    kind: Literal["causal_exp"] = "causal_exp"
    tau_s: float = Field(30.0, ge=1e-12, description="Kernel decay time in seconds")
    dt_s: float = Field(1.0, ge=1e-12, description="Sampling interval in seconds")
    n_kernel: int = Field(128, ge=4, le=8192, description="Kernel length (samples)")


class AnamnesisLcaCfg(BaseModel):
    lam: float = Field(0.02, ge=0.0, description="L1 sparsity strength (lambda)")
    max_iters: int = Field(4000, ge=10, le=200000)
    tol: float = Field(1e-6, gt=0.0)
    dt: float = Field(0.05, gt=0.0, description="LCA integration step")
    tau: float = Field(1.0, gt=0.0, description="LCA membrane time constant")
    nonnegative: bool = Field(True, description="Enforce nonnegative source by default")


class AnamnesisReconstructRequest(BaseModel):
    """Reconstruct a sparse source from an observed 1D "shadow" signal."""

    signal: List[float] = Field(..., description="Observed shadow signal y(t)")
    kernel: Optional[List[float]] = Field(None, description="Optional explicit kernel. If omitted, kernel_cfg is used.")
    kernel_cfg: Optional[AnamnesisKernelCfg] = Field(None)
    lca_cfg: Optional[AnamnesisLcaCfg] = Field(None)
    emd_warn: float = Field(0.25, ge=0.0, description="EMD threshold for RIS_WARN")
    emd_fail: float = Field(1.0, ge=0.0, description="EMD threshold for RIS_FAIL")


class AnamnesisSpike(BaseModel):
    index: int = Field(..., ge=0)
    amplitude: float = Field(1.0)


class AnamnesisDemoRequest(BaseModel):
    """Generate a synthetic "past" and run the reconstruction end-to-end.

    Supports both a structured payload (with nested `kernel_cfg` and `lca_cfg`)
    and a simple, human-friendly payload with top-level fields that override
    the nested configs when provided.
    """

    n: int = Field(256, ge=16, le=8192)

    # Structured kernel config (canonical) - optional to allow simple payloads
    kernel_cfg: Optional[AnamnesisKernelCfg] = None

    # Simple top-level kernel defaults (human-friendly)
    dt_s: Optional[float] = Field(1.0, gt=0.0, description="Sampling interval in seconds")
    tau_s: Optional[float] = Field(30.0, gt=0.0, description="Kernel decay time in seconds")
    n_kernel: Optional[int] = Field(128, ge=4, le=8192, description="Kernel length (samples)")

    # Simple top-level LCA defaults (human-friendly)
    lam: Optional[float] = Field(0.02, ge=0.0, description="L1 sparsity strength (lambda)")
    max_iter: Optional[int] = Field(1500, ge=1, description="Max iterations (simple override)")
    tol: Optional[float] = Field(1e-6, gt=0.0, description="Convergence tolerance (simple override)")
    nonnegative: Optional[bool] = Field(True, description="Enforce nonnegative source by default")

    # Misc convenience
    seed: Optional[int] = Field(0, description="RNG seed for demo noise")
    score_space: Optional[Literal["shadow", "source"]] = Field("shadow")

    spikes: List[AnamnesisSpike] = Field(default_factory=lambda: [AnamnesisSpike(index=40, amplitude=1.0), AnamnesisSpike(index=120, amplitude=0.7)])
    noise_std: float = Field(0.0, ge=0.0, description="Gaussian noise std added to observed shadow")

    # Structured LCA config (canonical) - optional to allow simple payloads
    lca_cfg: Optional[AnamnesisLcaCfg] = None

    # More sensible demo thresholds for EMD when using normalized EMD
    emd_warn: float = Field(2.0, ge=0.0)
    emd_fail: float = Field(5.0, ge=0.0)


class RISReport(BaseModel):
    status: Literal["PASS", "WARN", "FAIL"]
    emd: float
    residual_norm: float
    converged: bool
    iters: int
    lam: float
    message: str


class AnamnesisResponse(BaseModel):
    kernel: List[float]
    observed: List[float]
    reconstructed_source: List[float]
    reconstructed_observed: List[float]
    ris: RISReport
    diagnostic: Dict[str, Any] = Field(default_factory=dict)
    kernel_name: Optional[str] = None
    kernel_family: Optional[str] = None


class AnamnesisTauCandidateScore(BaseModel):
    """Score for a single tau candidate."""
    tau_s: float
    emd_shadow: float
    residual_norm: float
    objective: float
    ris_status: str
    converged: bool
    iters: int
    label: Optional[str] = None


class AnamnesisTauSearchRequest(BaseModel):
    """
    Search tau candidates for the reconstruction lens.
    y_obs is the observed 'shadow' time series.
    """
    y_obs: List[float] = Field(..., description="Observed shadow signal y(t)")
    dt_s: float = Field(..., gt=0.0, description="Time step in seconds")
    tau_candidates_s: List[float] = Field(..., min_length=1, description="Tau candidates (seconds)")
    n_kernel: int = Field(128, ge=8, description="Kernel length (samples)")

    # Reconstruction knobs (defaults kept conservative)
    lam: float = Field(0.02, ge=0.0, description="L1 sparsity strength")
    max_iter: int = Field(1500, ge=10, description="Max iterations for solver")
    tol: float = Field(1e-6, gt=0.0, description="Convergence tolerance")
    nonnegative: bool = Field(True, description="Enforce nonnegative source")

    # RIS thresholds for tau search
    emd_warn: float = Field(2.0, ge=0.0, description="EMD threshold for WARN")
    emd_fail: float = Field(5.0, ge=0.0, description="EMD threshold for FAIL")
    residual_warn: float = Field(0.10, ge=0.0, description="Residual threshold for WARN")
    residual_fail: float = Field(0.25, ge=0.0, description="Residual threshold for FAIL")


class AnamnesisTauSearchResponse(BaseModel):
    """Result of tau search."""
    best_tau_s: Optional[float]
    best_index: Optional[int]
    best: Optional[Dict[str, Any]]
    scores: List[AnamnesisTauCandidateScore]
    ris_summary: Dict[str, Any]
    comparison: Optional[Dict[str, Any]] = None
    kernel_name: Optional[str] = None
    kernel_family: Optional[str] = None


# ----------------------------
# F(sig8) adapter & tau search (real data)
# ----------------------------

class Fsigma8DatasetRequest(BaseModel):
    z: List[float]
    fsigma8: List[float]
    sigma: Optional[List[float]] = None
    dataset_label: Optional[str] = None
    cosmo: Optional[HzModelConfig] = None


class Fsigma8TauSearchRequest(BaseModel):
    data: Fsigma8DatasetRequest
    dt_myr: float = Field(5.0, gt=0.0, description="Resample spacing in Myr")
    tau_candidates_myr: List[float] = Field(..., min_length=1)
    n_kernel: int = Field(128, ge=8)

    # Reconstruction priors: 'smooth' uses ridge deconvolution (Fourier), 'sparse' uses LCA
    prior: Literal["smooth", "sparse"] = Field("smooth")
    lam: float = Field(0.02, ge=0.0, description="L1 sparsity strength (used for sparse prior)")
    lam_smooth: float = Field(1e-3, ge=0.0, description="Ridge strength for smooth prior (lam2)")

    # Optional preprocessing
    demean: bool = Field(True, description="Subtract mean from resampled signal before reconstruction")
    standardize: bool = Field(False, description="Divide by std (after demeaning) before reconstruction")

    max_iter: int = Field(1500, ge=1)
    tol: float = Field(1e-6, gt=0.0)
    nonnegative: bool = Field(True)

    debug_trace: bool = Field(False, description="Return first 10 entries of iter_trace for diagnostics when available")

    # RIS thresholds
    emd_warn: float = Field(2.0, ge=0.0)
    emd_fail: float = Field(5.0, ge=0.0)
    residual_warn: float = Field(1.0, ge=0.0)
    residual_fail: float = Field(2.0, ge=0.0)


class Fsigma8TauCandidateScore(BaseModel):
    tau_myr: float
    emd: float
    residual_norm: float
    objective: float
    ris_status: str
    converged: bool
    iters: int
    label: Optional[str] = None

    # Per-candidate diagnostics (optional)
    max_abs_x: Optional[float] = None
    nnz_x: Optional[int] = None
    objective_first: Optional[float] = None
    objective_last: Optional[float] = None
    residual_first: Optional[float] = None
    residual_last: Optional[float] = None
    iter_trace: Optional[List[Dict[str, float]]] = None
    emd_mass_warning: Optional[bool] = None

    # Optional original-scale reconstructed observed signal (for plotting/audit)
    y_hat_original: Optional[List[float]] = None


class Fsigma8TauSearchResponse(BaseModel):
    best_tau_myr: Optional[float]
    best_index: Optional[int]
    best: Optional[Dict[str, Any]]
    best_nonbaseline_tau_myr: Optional[float] = None
    scores: List[Fsigma8TauCandidateScore]
    ris_summary: Dict[str, Any]
    comparison: Optional[Dict[str, Any]] = None
    adapter_diagnostic: Optional[Dict[str, Any]] = None


# ----------------------------
# F(sig8) resonance diagnostics
# ----------------------------

class Fsigma8ResonanceMapRequest(BaseModel):
    data: Fsigma8DatasetRequest
    dt_myr: float = Field(5.0, gt=0.0)
    tau_candidates_myr: List[float] = Field(..., min_length=1)
    n_kernel: int = Field(128, ge=8)

    prior: Literal["smooth", "sparse"] = Field("smooth")
    lam: float = Field(0.02, ge=0.0)
    lam_smooth: float = Field(1e-3, ge=0.0)
    max_iter: int = Field(1500, ge=1)
    tol: float = Field(1e-6, gt=0.0)
    nonnegative: bool = Field(True)
    demean: bool = Field(True)
    standardize: bool = Field(False)
    emd_warn: float = Field(2.0, ge=0.0)
    emd_fail: float = Field(5.0, ge=0.0)
    residual_warn: float = Field(1.0, ge=0.0)
    residual_fail: float = Field(2.0, ge=0.0)

    leave_one_out: bool = Field(True, description="Run leave-one-out tau search for each point")
    local_windows: bool = Field(False, description="Reserved for future local window diagnostics")


class Fsigma8PointDiagnostic(BaseModel):
    z: float
    t_lookback_gyr: float
    y_obs: float
    sigma: Optional[float] = None
    y_hat: Optional[float] = None
    residual: Optional[float] = None
    chi2_contrib: Optional[float] = None
    delta_tau_leave_one_out: Optional[float] = None
    winner_leave_one_out: Optional[str] = None


class Fsigma8ResonanceMapResponse(BaseModel):
    best_tau_myr: Optional[float]
    best_nonbaseline_tau_myr: Optional[float] = None
    winner: Optional[str] = None
    per_point: List[Fsigma8PointDiagnostic]
    robustness: Dict[str, Any]
    adapter_diagnostic: Optional[Dict[str, Any]] = None
    dataset_hash: Optional[str] = None
    run_id: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    links: Optional[List[str]] = None


# ----------------------------
# Zeta-Tau Scaling Experiment
# ----------------------------

class ZetaTauScalingRequest(BaseModel):
    """Pre-registered zeta-tau scaling experiment parameters."""
    tau0_myr: float = Field(41.9, description="Target memory timescale in Myr")
    H0_km_s_Mpc: float = Field(67.4, description="Hubble parameter in km/s/Mpc")
    Omega_m: float = Field(0.315, description="Matter density (for provenance)")
    zeros_n: int = Field(50, ge=10, le=500, description="Number of zeta zeros to retrieve")
    eps_hit: float = Field(0.01, ge=0.001, le=0.5, description="Hit threshold (relative error)")
    null_trials: int = Field(2000, ge=100, le=10000, description="Number of null trials")
    h0_perturb_frac: float = Field(0.02, ge=0.01, le=0.1, description="H0 perturbation fraction")
    seed: int = Field(7, description="Random seed for deterministic null trials")


class ZetaTauScalingBestMatch(BaseModel):
    """Best matching formula."""
    family: str
    n: int
    m: Optional[int] = None
    p: Optional[float] = None
    gamma_n: Optional[float] = None
    gamma_m: Optional[float] = None
    tau_pred_myr: float
    rel_err: float


class ZetaTauScalingRobustness(BaseModel):
    """Robustness under H0 perturbation."""
    h0_minus_ok: bool
    h0_plus_ok: bool
    rel_err_minus: float
    rel_err_plus: float


class ZetaTauScalingNullModel(BaseModel):
    """Null model (anti-numerology) results."""
    null_trials: int
    p_value: float
    observed_best_err: float
    null_best_err_median: float
    null_best_err_min: float


class ZetaTauScalingTestedCounts(BaseModel):
    """Hypothesis testing counts."""
    N_zeros: int
    K_hypotheses: int


class ZetaTauScalingConstants(BaseModel):
    """Constants and parameters used."""
    tau0_myr: float
    H0_km_s_Mpc: float
    tH_gyr: float
    Omega_m: float
    eps_hit: float
    null_trials: int
    h0_perturb_frac: float
    seed: int


class ZetaTauScalingResponse(BaseModel):
    """Full zeta-tau scaling experiment result."""
    status: Literal["PASS", "WARN", "FAIL"]
    best_match: ZetaTauScalingBestMatch
    robustness: ZetaTauScalingRobustness
    null_model: ZetaTauScalingNullModel
    tested_counts: ZetaTauScalingTestedCounts
    constants: ZetaTauScalingConstants
    run_id: str
    message: str = ""
    tested_families: List[str] = Field(default_factory=list)


# =========================
# Zeta–Tau Scaling Experiment
# =========================


class ZetaTauScalingRequest(BaseModel):
    """Request for Zeta–Tau Scaling experiment."""
    tau0_myr: float = Field(41.9, gt=0.0, description="Memory time candidate (Myr)")
    H0_km_s_Mpc: float = Field(67.4, gt=0.0, description="Hubble constant (km/s/Mpc)")
    Omega_m: float = Field(0.315, ge=0.0, le=1.0, description="Matter density (stored for provenance)")
    zeros_n: int = Field(50, ge=10, le=500, description="Number of Riemann zeta zeros to test")
    eps_hit: float = Field(0.01, gt=0.0, description="Relative error threshold (e.g., 1%)")
    null_trials: int = Field(2000, ge=100, le=100000, description="Null model trials")
    h0_perturb_frac: float = Field(0.02, gt=0.0, description="H0 perturbation fraction (e.g., 2%)")
    seed: int = Field(7, ge=0, description="RNG seed for determinism")


class ZetaTauScalingResponse(BaseModel):
    """Response from Zeta–Tau Scaling experiment."""
    status: Literal["PASS", "WARN", "FAIL"]

    best_match: Dict[str, Any]  # family, tau_pred_myr, rel_err, n, m?, p?, gamma_n, gamma_m?

    robustness: Dict[str, Any]  # h0_minus_ok, h0_plus_ok, rel_err_minus, rel_err_plus

    null_model: Dict[str, Any]  # null_trials, p_value, observed_best_err, null_best_err_median, null_best_err_min

    tested_counts: Dict[str, Any]  # N_zeros, K_hypotheses

    constants: Dict[str, Any]  # tau0_myr, H0_km_s_Mpc, tH_gyr, Omega_m, eps_hit, null_trials, h0_perturb_frac, seed

    run_id: Optional[str] = None


# ----------------------------
# Casimir Density Sweep (Phase I canon)
# ----------------------------


class CasimirDensitySweepRequest(BaseModel):
    """Request for Casimir Density Sweep (Phase I canon)."""
    tau0_myr: float = Field(41.9, gt=0.0, description="Local interaction time τ0 in Myr")
    H0_km_s_Mpc: float = Field(67.36, gt=0.0, description="Baseline-defined H0 (km/s/Mpc)")
    Omega_lambda: float = Field(0.6847, ge=0.0, le=1.0, description="Baseline-defined ΩΛ")

    h0_min: float = Field(67.0, gt=0.0, description="H0 sweep min")
    h0_max: float = Field(74.0, gt=0.0, description="H0 sweep max")
    h0_step: float = Field(0.1, gt=0.0, description="H0 sweep step")

    omegaL_min: float = Field(0.675, ge=0.0, le=1.0, description="ΩΛ sweep min")
    omegaL_max: float = Field(0.695, ge=0.0, le=1.0, description="ΩΛ sweep max")
    omegaL_step: float = Field(0.002, gt=0.0, description="ΩΛ sweep step")

    alpha_vac: Optional[float] = Field(None, gt=0.0, description="Vacuum response parameter α_vac (canonical)")
    alpha_scr: Optional[float] = Field(None, gt=0.0, description="Alias for α_vac")
    seed: int = Field(7, ge=0, description="Determinism seed")


class CasimirSweepComputed(BaseModel):
    rho_crit: float
    rho_lambda: float
    rho_req: float
    R_obs: float
    tau_lambda_s: float
    tau_lambda_gyr: float
    tau0_s: float
    tau0_myr: float
    S_thy: float
    rel_err_S: float
    rel_err_R: Optional[float] = None
    rel_err_R_note: Optional[str] = None


class CasimirSweepArgmin(BaseModel):
    H0_km_s_Mpc: float
    Omega_lambda: float
    rel_err_S: float
    tauLambda_gyr: float
    tau0_myr: float


class CasimirNISCertificate(BaseModel):
    status: Literal["PASS", "EXPLORATORY", "FAIL"]
    determinism_stamp: str
    unit_consistency: bool
    fuzz_fraction: float
    provenance: Dict[str, Any]
    environment: Optional[Dict[str, Any]] = None
    safe_mode: Optional[bool] = None
    convergence: Optional[Dict[str, Any]] = None
    data_provenance: Optional[Dict[str, Any]] = None


class CasimirSweepMetadata(BaseModel):
    baseline_note: str
    velocity_potential_note: str
    alpha_vac: float
    n_g0_sq: float
    n_g0: float
    stability: Dict[str, Any]


class CasimirDensitySweepResponse(BaseModel):
    status: Literal["PASS", "EXPLORATORY", "FAIL"]
    computed: CasimirSweepComputed
    two_loop_argmin: CasimirSweepArgmin
    rel_err_S_vs_H0: List[Dict[str, float]]
    nis: CasimirNISCertificate
    metadata: CasimirSweepMetadata
    run_id: Optional[str] = None


# ----------------------------
# PTA Dispersion Probe (Phase I falsification test)
# ----------------------------


class PTADispersionProbeRequest(BaseModel):
    tau0_myr: float = Field(41.92, gt=0.0, description="Local interaction time τ0 in Myr")
    alpha_scr: float = Field(1.0 / 3.0, gt=0.0, description="GRUT screening parameter α_scr (not QED α)")
    freqs_hz: List[float] = Field(default_factory=lambda: [1e-9, 1e-8, 1e-7], description="Frequencies in Hz")
    use_group_velocity: bool = Field(True, description="Compute v_g using dispersive relation")
    f_hf_hz: float = Field(100.0, gt=0.0, description="HF sanity check frequency in Hz")
    apply_to_gw_propagation: bool = Field(False, description="Force n_g(ω) to apply to GW propagation")
    seed: int = Field(7, ge=0, description="Determinism seed")

    @model_validator(mode="before")
    def _alias_alpha_scr(cls, values):
        if isinstance(values, dict) and "alpha_vac" in values:
            if "alpha_scr" in values and values["alpha_scr"] is not None:
                if abs(float(values["alpha_scr"]) - float(values["alpha_vac"])) > 1e-12:
                    raise ValueError("alpha_scr and alpha_vac differ; provide only one or matching values")
            values["alpha_scr"] = values.get("alpha_scr", values["alpha_vac"])
        return values

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True


class PTADispersionProbeResult(BaseModel):
    f_hz: float
    omega_rad_s: float
    x: float
    ReChi: float
    ng2: float
    n: float
    n_minus_1: float
    vp_over_c: float
    vg_over_c: float
    v_phase_over_c: float
    vp_minus_1: float
    vg_minus_1: float
    delta_v_phase: float
    n_sci: Optional[str] = None
    ng2_sci: Optional[str] = None
    vp_over_c_sci: Optional[str] = None
    vg_over_c_sci: Optional[str] = None
    delta_vp: float
    delta_vg: float
    delay_s_per_Mpc: float
    delay_sign: Literal["advance", "delay"]


class PTADispersionProbeComparison(BaseModel):
    delta_vg: float
    delta_vp: float
    mg_equiv_abs_eV: float
    mg_equiv_sign: Literal["tachyonic_like", "massive_like"]
    mg_mapping_mode: Literal["like_for_like", "magnitude_proxy_only"]
    mg_limit_eV: float
    mg_margin: float
    mg_exclusion_flag: Literal["EXCLUDED_BY_PTA_MG_PROXY", "NOT_EXCLUDED_BY_PTA_MG_PROXY"]
    hf_sanity_flag: Literal["PASS", "FAIL"]


class PTADispersionHFCheck(BaseModel):
    f_hz: float
    omega_rad_s: float
    x: float
    ReChi: float
    ng2: float
    n: float
    delta_vg: float
    pass_flag: Literal["PASS", "FAIL"]


class PTADispersionLimit(BaseModel):
    name: str
    value: Optional[float]
    value_low: Optional[float] = None
    value_high: Optional[float] = None
    units: str
    bound_type: Optional[str] = None
    citation: str
    applicability_note: str


class PTADispersionProbeResponse(BaseModel):
    run_id: str
    timestamp: str
    status: Literal[
        "PASS_NOT_EXCLUDED",
        "FAIL_HF_SANITY",
        "EXCLUDED_BY_PTA_SPEED",
        "EXCLUDED_BY_PTA_MG_PROXY",
        "NOT_APPLICABLE",
    ]
    min_v_phase_over_c_over_band: float
    max_abs_delta_v_phase_over_c_over_band: float
    max_abs_delta_v_group_over_c_over_band: float
    worst_speed_margin_over_band: float
    worst_freq_hz: float
    assumptions: List[str]
    results: List[PTADispersionProbeResult]
    comparisons: List[PTADispersionProbeComparison]
    hf_check_100Hz: PTADispersionHFCheck
    cited_limits: List[PTADispersionLimit]
    conclusion: str
    pta_direct_dispersion_bound_present: bool
    exclusion_basis: Optional[str]
    worst_margin_over_band: float


# ----------------------------
# Glass Transition (Cosmological Deborah Sweep)
# ----------------------------


class GlassTransitionSweepRequest(BaseModel):
    tau0_myr: float = Field(41.9, gt=0.0, description="Memory relaxation time (Myr)")
    H0_km_s_Mpc: float = Field(67.36, gt=0.0, description="H0 (km/s/Mpc)")
    Omega_m: float = Field(0.315, ge=0.0, le=1.0, description="Matter density")
    Omega_lambda: float = Field(0.6847, ge=0.0, le=1.0, description="Dark energy density")
    Omega_r: float = Field(9.24e-5, ge=0.0, description="Radiation density")
    T_cmb_K: float = Field(2.725, gt=0.0, description="CMB temperature (K)")

    z_min: float = Field(0.0, ge=0.0, description="Minimum redshift for scan")
    z_max: float = Field(1.0e4, gt=0.0, description="Maximum redshift for scan")
    n_samples: int = Field(500, ge=10, le=20000, description="Scan grid size (log-spaced)")

    include_scan_data: bool = Field(False, description="Include sampled scan points")
    scan_max_points: int = Field(200, ge=10, le=20000, description="Max scan points to return if include_scan_data")

    pass_z_min: float = Field(10.0, gt=0.0, description="PASS band min")
    pass_z_max: float = Field(100.0, gt=0.0, description="PASS band max")
    warn_z_max: float = Field(1100.0, gt=0.0, description="WARN upper bound (e.g., CMB scale)")


class GlassTransitionPoint(BaseModel):
    z: float
    age_myr: float
    T_K: float
    De: float


class GlassTransitionCrossing(BaseModel):
    z_crit: float
    age_myr: float
    T_K: float
    De: float


class GlassTransitionCertificate(BaseModel):
    name: str
    status: Literal["PASS", "WARN", "FAIL"]
    message: str
    assumptions: Dict[str, Any]


class GlassTransitionSweepResponse(BaseModel):
    status: Literal["PASS", "WARN", "FAIL"]
    crossing: GlassTransitionCrossing
    scan_points: Optional[List[GlassTransitionPoint]] = None
    constants: Dict[str, Any]
    certificate: GlassTransitionCertificate
    run_id: Optional[str] = None


# ===== RAI Ask (Phase H — Responsive AI) =====

class RaiAskRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    observer_profile: Optional[str] = "participant"

class ChartData(BaseModel):
    type: str  # "hz" or "fs8"
    data: Dict[str, Any]

class CertificateSummary(BaseModel):
    canon_hash: Optional[str] = None
    repro_hash: Optional[str] = None
    steps_computed: Optional[int] = None
    integrator: Optional[str] = None
    observables_emitted: Optional[List[str]] = None

class SuggestionItem(BaseModel):
    action: Optional[str] = None
    label: Optional[str] = None
    reason: Optional[str] = None
    description: Optional[str] = None
    confidence: Optional[str] = None

class RaiAskResponseBody(BaseModel):
    text_markdown: str
    charts: List[ChartData] = []
    run_ids: List[str] = []
    nis_status: Optional[str] = None
    suggestions: List[SuggestionItem] = []
    certificate_summary: Optional[CertificateSummary] = None
    fallback_used: bool = False

class RaiAskResponse(BaseModel):
    session_id: str
    response: RaiAskResponseBody
    expandable: Optional[Dict[str, Any]] = None

class RaiStatusResponse(BaseModel):
    ai_available: bool
    model: Optional[str] = None
    engine_version: str
    canon_hash: str

class GenerateSweepRequest(BaseModel):
    preset: str = "matter_only"
    grid: str = "0.0,0.1,0.333333333,0.5,1.0"
    start_z: float = 2.0
    dt_years: float = 100000
    steps: int = 300

