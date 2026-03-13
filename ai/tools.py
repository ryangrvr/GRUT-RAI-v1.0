"""Tool definitions for Claude tool-use in GRUT-RAI."""

from __future__ import annotations

from typing import Any, Dict, List


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Return the tool schemas that Claude can call."""
    return [
        {
            "name": "run_cosmology",
            "description": (
                "Run the GRUT Phase-2 cosmology engine. Returns H(z) and optionally "
                "fsigma8(z) arrays with a full NIS certificate. All physics numbers come "
                "from the deterministic engine -- never invent them."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "rho0": {
                        "type": "number",
                        "description": "Initial energy density (code units). Default 0.2.",
                        "default": 0.2,
                    },
                    "p0": {
                        "type": "number",
                        "description": "Initial pressure (code units). Default -0.2 for vacuum-like.",
                        "default": -0.2,
                    },
                    "H0": {
                        "type": "number",
                        "description": "Initial Hubble parameter (1/years). Default 1e-10.",
                        "default": 1e-10,
                    },
                    "rho_m0": {
                        "type": "number",
                        "description": "Initial matter density for growth calculation. 0 suppresses growth.",
                        "default": 0.0,
                    },
                    "alpha_mem": {
                        "type": "number",
                        "description": "Memory coupling weight [0,1]. 0 = no memory, 1 = full memory.",
                        "default": 0.1,
                    },
                    "start_z": {
                        "type": "number",
                        "description": "Starting redshift. Default 2.0.",
                        "default": 2.0,
                    },
                    "dt_years": {
                        "type": "number",
                        "description": "Time step in years. Default 100000.",
                        "default": 100000,
                    },
                    "steps": {
                        "type": "integer",
                        "description": "Number of integration steps. Default 300.",
                        "default": 300,
                    },
                    "enable_growth": {
                        "type": "boolean",
                        "description": "Whether to compute fsigma8 linear growth. Default true.",
                        "default": True,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "run_experiment",
            "description": (
                "Run a pre-registered GRUT experiment. Available experiments: "
                "zeta_tau_scaling (tests tau0 alignment with Riemann zeta zeros), "
                "casimir_density_sweep (vacuum screening consistency), "
                "pta_dispersion_probe (PTA dispersion falsification), "
                "glass_transition_sweep (cosmological Deborah number)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "experiment_name": {
                        "type": "string",
                        "enum": [
                            "zeta_tau_scaling",
                            "casimir_density_sweep",
                            "pta_dispersion_probe",
                            "glass_transition_sweep",
                        ],
                        "description": "Which experiment to run.",
                    },
                    "params": {
                        "type": "object",
                        "description": "Experiment-specific parameters. If omitted, uses canon defaults.",
                    },
                },
                "required": ["experiment_name"],
            },
        },
        {
            "name": "run_anamnesis",
            "description": (
                "Run an Anamnesis (memory reconstruction) demo. Generates a sparse "
                "past signal, smears it with a causal kernel, reconstructs it, "
                "and returns the RIS (Reconstruction Integrity System) report."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "tau_s": {
                        "type": "number",
                        "description": "Kernel decay time in seconds. Default uses tau0.",
                    },
                    "n_events": {
                        "type": "integer",
                        "description": "Number of sparse source events. Default 5.",
                        "default": 5,
                    },
                    "n_bins": {
                        "type": "integer",
                        "description": "Number of time bins. Default 128.",
                        "default": 128,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "lookup_grutipedia",
            "description": (
                "Look up a GRUTipedia topic by slug. Returns the topic definition, "
                "body text, and linked runs. Available topics include: tau0, epsilon, "
                "s-phase-bridge, dissipation-operator, cfl-gate, nis-certificate, "
                "seth-kernel, zeta-operator, evidence-packets, casimir-density, "
                "alpha-screening, glass-transition."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Topic slug (e.g. 'tau0', 'nis-certificate', 'seth-kernel').",
                    },
                },
                "required": ["slug"],
            },
        },
        {
            "name": "get_canon_value",
            "description": (
                "Look up a specific canon constant by ID or alias. Returns the value, "
                "units, bounds, and description."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": (
                            "Constant ID (e.g. 'CONST_TAU_0', 'PARAM_ALPHA_MEM') "
                            "or alias (e.g. 'tau0', 'alpha_mem', 'w')."
                        ),
                    },
                },
                "required": ["name"],
            },
        },
        {
            "name": "search_past_runs",
            "description": (
                "Search past engine runs stored in the vault. Returns summaries "
                "of matching runs including status, key metrics, and run IDs."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of runs to return. Default 5.",
                        "default": 5,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "suggest_next_experiment",
            "description": (
                "Based on a run ID, get deterministic suggestions for what to try next. "
                "Returns topic links and reasons."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "The run ID to generate suggestions for.",
                    },
                },
                "required": ["run_id"],
            },
        },
        # ── Hubble Tension Evidence Packet ──
        {
            "name": "build_hubble_tension_packet",
            "description": (
                "Build a complete Hubble Tension Evidence Packet. Runs GRUT cosmology "
                "across presets (matter_only, vacuum_plus_matter, or both), computes "
                "residuals vs ΛCDM and observational data, anchors H(z) to Planck and "
                "SH0ES, and produces a late-time recommendation with chi-squared metrics. "
                "Returns NIS-certified results with tension scores."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "preset": {
                        "type": "string",
                        "enum": ["matter_only", "vacuum_plus_matter", "both"],
                        "description": "Initial condition preset. 'both' runs both presets.",
                        "default": "both",
                    },
                    "alpha_mem": {
                        "type": "number",
                        "description": "Memory coupling override. If omitted uses canon default.",
                    },
                    "dataset_policy": {
                        "type": "string",
                        "enum": ["min", "cc_only", "bao_only", "all"],
                        "description": "Which H(z) data to include. 'all' = full compilation.",
                        "default": "all",
                    },
                    "compare_window_policy": {
                        "type": "string",
                        "enum": ["full", "z_le_1_0", "z_le_1_5"],
                        "description": "Redshift window for comparison. 'full' = all z.",
                        "default": "full",
                    },
                    "start_z": {
                        "type": "number",
                        "description": "Starting redshift. Default 2.0.",
                        "default": 2.0,
                    },
                    "steps": {
                        "type": "integer",
                        "description": "Integration steps. Default 300.",
                        "default": 300,
                    },
                    "dt_years": {
                        "type": "number",
                        "description": "Time step in years. Default 100000.",
                        "default": 100000,
                    },
                    "eobs_anchor_policy": {
                        "type": "string",
                        "enum": ["lowest_z", "median_lowz"],
                        "description": (
                            "How to anchor E(z) observations. 'lowest_z' anchors at "
                            "the single lowest-redshift data point; 'median_lowz' uses "
                            "the median of data below z<0.1. Default 'lowest_z'."
                        ),
                        "default": "lowest_z",
                    },
                    "recommendation_mode": {
                        "type": "string",
                        "enum": ["configured_only", "late_time_grid"],
                        "description": (
                            "How to generate the late-time recommendation. "
                            "'configured_only' uses current alpha_mem only; "
                            "'late_time_grid' sweeps a grid of alpha_mem values. "
                            "Default 'late_time_grid'."
                        ),
                        "default": "late_time_grid",
                    },
                    "include_vacuum_plus_matter": {
                        "type": "boolean",
                        "description": (
                            "Whether to include the vacuum_plus_matter preset in "
                            "addition to matter_only. Only relevant when preset='both'. "
                            "Default true."
                        ),
                        "default": True,
                    },
                },
                "required": [],
            },
        },
        # ── Lensing ──
        {
            "name": "run_lensing",
            "description": (
                "Run a gravitational lensing packet. Computes convergence (kappa), "
                "shear (gamma), deflection fields, and peak statistics for a chosen "
                "density or potential preset."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Grid resolution. Default 256.",
                        "default": 256,
                    },
                    "preset": {
                        "type": "string",
                        "enum": ["single_halo", "bullet_toy"],
                        "description": "Density profile preset.",
                        "default": "single_halo",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["sigma_to_kappa", "phi_to_psi"],
                        "description": "Operation mode. Default sigma_to_kappa.",
                        "default": "sigma_to_kappa",
                    },
                    "fov_arcmin": {
                        "type": "number",
                        "description": "Field of view in arcminutes. Default 20.",
                        "default": 20.0,
                    },
                },
                "required": [],
            },
        },
        # ── Advanced Anamnesis ──
        {
            "name": "run_anamnesis_fsigma8",
            "description": (
                "Generate a synthetic memory-positive fsigma8 dataset for instrument "
                "calibration. Creates a planted tau signal in fsigma8 data that can be "
                "tested with tau search."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "planted_tau_myr": {
                        "type": "number",
                        "description": "Planted tau in Megayears. Default 41.9 (tau0).",
                        "default": 41.9,
                    },
                    "dt_myr": {
                        "type": "number",
                        "description": "Time step in Megayears. Default 5.0.",
                        "default": 5.0,
                    },
                    "n_points": {
                        "type": "integer",
                        "description": "Number of data points. Default 8.",
                        "default": 8,
                    },
                    "seed": {
                        "type": "integer",
                        "description": "Random seed. Default 0.",
                        "default": 0,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "search_tau",
            "description": (
                "Search over tau candidates to find the best memory timescale from "
                "observed data. Uses RIS (Reconstruction Integrity System) gating. "
                "Returns scores for each candidate with EMD, residual norms, and status."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "y_obs": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Observed shadow signal y(t) as array of floats.",
                    },
                    "dt_s": {
                        "type": "number",
                        "description": "Time step in seconds.",
                    },
                    "tau_candidates_s": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Array of tau candidate values in seconds.",
                    },
                    "n_kernel": {
                        "type": "integer",
                        "description": "Kernel length in samples. Default 128.",
                        "default": 128,
                    },
                },
                "required": ["y_obs", "dt_s", "tau_candidates_s"],
            },
        },
        {
            "name": "fsigma8_resonance_map",
            "description": (
                "Run a full fsigma8 resonance map diagnostic. Searches over tau "
                "candidates on redshift/fsigma8 data with leave-one-out influence "
                "analysis. Returns per-point diagnostics, best tau, winner "
                "(grut vs baseline), and robustness metrics."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "z": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Array of redshift values.",
                    },
                    "fsigma8": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Array of f(sigma8) values.",
                    },
                    "sigma": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional uncertainties.",
                    },
                    "tau_candidates_myr": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Tau candidates in Megayears.",
                    },
                    "leave_one_out": {
                        "type": "boolean",
                        "description": "Run leave-one-out diagnostics. Default true.",
                        "default": True,
                    },
                },
                "required": ["z", "fsigma8", "tau_candidates_myr"],
            },
        },
        # ── Library & Evidence ──
        {
            "name": "get_library",
            "description": (
                "Browse saved runs in the library. Returns run summaries with IDs, "
                "kinds, status, and timestamps. Use this to find past runs."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max runs to return. Default 20.",
                        "default": 20,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "get_run_details",
            "description": (
                "Get full details for a specific run by ID, including request "
                "parameters, response data, and NIS/RIS certificate."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "The run ID to retrieve.",
                    },
                },
                "required": ["run_id"],
            },
        },
        {
            "name": "export_evidence_packet",
            "description": (
                "Export a run as a complete evidence packet with full provenance, "
                "NIS certificate, and reproducibility data."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "The run ID to export.",
                    },
                },
                "required": ["run_id"],
            },
        },
        # ── Anamnesis Reconstruct ──
        {
            "name": "anamnesis_reconstruct",
            "description": (
                "Reconstruct a sparse source from an observed 1D 'shadow' signal "
                "using kernel deconvolution (LCA solver). Returns the reconstructed "
                "source, RIS quality report, and diagnostics."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "signal": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Observed shadow signal y(t) as array of floats.",
                    },
                    "kernel_tau_s": {
                        "type": "number",
                        "description": "Kernel decay time in seconds. Default 30.",
                        "default": 30.0,
                    },
                    "kernel_dt_s": {
                        "type": "number",
                        "description": "Sampling interval in seconds. Default 1.",
                        "default": 1.0,
                    },
                    "n_kernel": {
                        "type": "integer",
                        "description": "Kernel length in samples. Default 128.",
                        "default": 128,
                    },
                    "lam": {
                        "type": "number",
                        "description": "L1 sparsity strength. Default 0.02.",
                        "default": 0.02,
                    },
                    "nonnegative": {
                        "type": "boolean",
                        "description": "Enforce nonnegative source. Default true.",
                        "default": True,
                    },
                },
                "required": ["signal"],
            },
        },
        # ── fsigma8 Tau Search ──
        {
            "name": "search_tau_fsigma8",
            "description": (
                "Search for the best memory timescale from f(sigma8) observational data. "
                "Accepts redshift/fsigma8 arrays, converts to lookback time, resamples "
                "uniformly, and performs tau search with RIS gating. Returns scored "
                "candidates with best tau in Megayears."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "z": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Redshift values.",
                    },
                    "fsigma8": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "f(sigma8) values.",
                    },
                    "sigma": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional uncertainties.",
                    },
                    "tau_candidates_myr": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Tau candidates in Megayears.",
                    },
                    "prior": {
                        "type": "string",
                        "enum": ["smooth", "sparse"],
                        "description": "Reconstruction prior. Default smooth.",
                        "default": "smooth",
                    },
                    "dt_myr": {
                        "type": "number",
                        "description": "Resample spacing in Megayears. Default 5.",
                        "default": 5.0,
                    },
                },
                "required": ["z", "fsigma8", "tau_candidates_myr"],
            },
        },
        # ── Publish & Public Access ──
        {
            "name": "publish_run",
            "description": (
                "Publish a run as an immutable versioned snapshot for sharing. "
                "Returns a slug, revision number, and public URL."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "The run ID to publish.",
                    },
                },
                "required": ["run_id"],
            },
        },
        {
            "name": "get_published",
            "description": (
                "Retrieve a published run snapshot by its slug. Returns the "
                "sanitized evidence packet with metadata, request, response, "
                "and bundle hash."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Published run slug.",
                    },
                    "revision": {
                        "type": "integer",
                        "description": "Specific revision number. If omitted, returns latest.",
                    },
                },
                "required": ["slug"],
            },
        },
        # ── GRUTipedia Management ──
        {
            "name": "list_grutipedia",
            "description": (
                "List all available GRUTipedia topics with titles, slugs, and categories."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max topics. Default 50.",
                        "default": 50,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "link_run_to_topic",
            "description": (
                "Link a run to a GRUTipedia topic with an optional markdown note "
                "explaining the connection."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "GRUTipedia topic slug.",
                    },
                    "run_id": {
                        "type": "string",
                        "description": "Run ID to link.",
                    },
                    "note_md": {
                        "type": "string",
                        "description": "Optional markdown note about the link.",
                    },
                },
                "required": ["slug", "run_id"],
            },
        },
        # ── Full Canon ──
        {
            "name": "get_full_canon",
            "description": (
                "Get the complete GRUT canonical configuration including all "
                "constants, operators, equations, frozen parameters, and the "
                "canon hash. More comprehensive than get_canon_value."
            ),
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        # ── Parameter Sweep ──
        {
            "name": "generate_sweep",
            "description": (
                "Run a parameter sweep over alpha_mem values. Runs the engine "
                "at each grid point and returns H(z) and fsigma8 point counts, "
                "viability, and certificates for each. Good for systematic "
                "exploration of memory coupling effects."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "preset": {
                        "type": "string",
                        "description": "Scenario preset. Default matter_only.",
                        "default": "matter_only",
                    },
                    "grid": {
                        "type": "string",
                        "description": "Comma-separated alpha_mem values. Default '0.0,0.1,0.333,0.5,1.0'.",
                        "default": "0.0,0.1,0.333333333,0.5,1.0",
                    },
                    "start_z": {
                        "type": "number",
                        "description": "Starting redshift. Default 2.0.",
                        "default": 2.0,
                    },
                    "steps": {
                        "type": "integer",
                        "description": "Integration steps. Default 300.",
                        "default": 300,
                    },
                    "dt_years": {
                        "type": "number",
                        "description": "Time step in years. Default 100000.",
                        "default": 100000,
                    },
                },
                "required": [],
            },
        },
        # ── Quantum Evidence Packet ──
        {
            "name": "build_quantum_evidence_packet",
            "description": (
                "Build a Quantum Evidence Packet. Computes decoherence timescales "
                "under GRUT's self-consistent vacuum response and compares against "
                "Diosi-Penrose (DP) baseline. Returns slope_self_consistent (should "
                "be -2/3), slope_controlled (should match DP at -2), benchmark "
                "enhancements, mass/omega scans, and a full NIS certificate."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "alpha_vac": {
                        "type": "number",
                        "description": "Vacuum screening fraction. Default 1/3.",
                        "default": 0.3333333333333333,
                    },
                    "l_m": {
                        "type": "number",
                        "description": "Characteristic length scale in meters. Default 1e-6.",
                        "default": 1e-6,
                    },
                    "omega_benchmark": {
                        "type": "number",
                        "description": "Benchmark angular frequency in rad/s. Default 1000.",
                        "default": 1000.0,
                    },
                    "omega_scan_points": {
                        "type": "integer",
                        "description": "Number of omega scan grid points. Default 50.",
                        "default": 50,
                    },
                    "mass_scan_points": {
                        "type": "integer",
                        "description": "Number of mass scan grid points. Default 40.",
                        "default": 40,
                    },
                },
                "required": [],
            },
        },
        # ── Rotation Curve Packet ──
        {
            "name": "run_rotation_packet",
            "description": (
                "Run a Rotation Curve Packet on galaxy rotation data. Computes "
                "baseline (Newtonian baryonic) and GRUT-modified rotation curves. "
                "No fitting is performed -- the response model applies a deterministic "
                "transformation. Returns RMS residuals, chi-like metrics, and an NIS "
                "certificate. Available response models: identity (no modification), "
                "radial_gate_v0, memory_scale_boost_v0."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "data_path": {
                        "type": "string",
                        "description": (
                            "Path to galaxy rotation data CSV. Must have columns: "
                            "r_kpc, v_obs, v_err, v_gas, v_star (optionally v_bulge). "
                            "Example: 'artifacts/audit/rotation_packet/galaxy.csv'."
                        ),
                    },
                    "response_model": {
                        "type": "string",
                        "enum": ["identity", "radial_gate_v0", "memory_scale_boost_v0"],
                        "description": "Response model to apply. Default 'identity'.",
                        "default": "identity",
                    },
                    "alpha_mem": {
                        "type": "number",
                        "description": "Memory coupling. If omitted, uses canon default.",
                    },
                    "r0_policy": {
                        "type": "string",
                        "enum": ["median_radius", "fixed_kpc"],
                        "description": "How to set r0 scale radius. Default 'median_radius'.",
                        "default": "median_radius",
                    },
                    "r0_kpc": {
                        "type": "number",
                        "description": "Fixed r0 in kpc. Only used when r0_policy='fixed_kpc'.",
                    },
                    "ups_star": {
                        "type": "number",
                        "description": "Stellar mass-to-light ratio. Default 1.0.",
                        "default": 1.0,
                    },
                    "ups_bulge": {
                        "type": "number",
                        "description": "Bulge mass-to-light ratio. Default 1.0.",
                        "default": 1.0,
                    },
                },
                "required": ["data_path"],
            },
        },
        # ── Cluster Profile Packet ──
        {
            "name": "run_cluster_profile_packet",
            "description": (
                "Run a Cluster Lensing Profile Packet. Computes radial convergence "
                "(kappa) and tangential shear (gamma_t) profiles from lensing maps, "
                "optionally comparing observed profiles against a GRUT model response. "
                "Returns profile arrays, falsification metrics (kappa_rms_diff, "
                "gamma_rms_diff), and an NIS certificate."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "kappa_path": {
                        "type": "string",
                        "description": "Path to kappa (convergence) .npy file.",
                    },
                    "gamma1_path": {
                        "type": "string",
                        "description": "Path to gamma1 (shear component 1) .npy file.",
                    },
                    "gamma2_path": {
                        "type": "string",
                        "description": "Path to gamma2 (shear component 2) .npy file.",
                    },
                    "center_mode": {
                        "type": "string",
                        "enum": ["peak", "com_positive"],
                        "description": "How to center the profile. Default 'com_positive'.",
                        "default": "com_positive",
                    },
                    "profile_bins": {
                        "type": "integer",
                        "description": "Number of radial bins. Default 20.",
                        "default": 20,
                    },
                    "compare_to_model": {
                        "type": "boolean",
                        "description": "Whether to compare against GRUT model response. Default false.",
                        "default": False,
                    },
                    "model_response": {
                        "type": "string",
                        "enum": ["identity", "grut_gate_kspace_v0"],
                        "description": "Model response function. Default 'grut_gate_kspace_v0'.",
                        "default": "grut_gate_kspace_v0",
                    },
                    "fov_arcmin": {
                        "type": "number",
                        "description": "Field of view in arcminutes. Default 20.",
                        "default": 20.0,
                    },
                },
                "required": ["kappa_path"],
            },
        },
        # ── Audit & Evidence Index ──
        {
            "name": "run_audit",
            "description": (
                "Run the full GRUT-RAI audit suite (audit_all.py). Executes all "
                "deterministic reproducibility checks: dual cosmology runs with "
                "hash comparison, Hubble tension packets across dataset policies, "
                "quantum evidence packet with slope verification, rotation curve "
                "packet, cluster profile and prediction packets. Returns PASS/FAIL "
                "with canon_hash and repro_hash."
            ),
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "list_evidence_packets",
            "description": (
                "Scan the artifacts directory for ALL evidence packets and build a "
                "structured Evidence Index. Discovers packets under evidence_*, "
                "*_packet_*, *_batch_*, audit/*, sweeps, cluster_*, and other "
                "standard GRUT-RAI artifact directories. For each packet, reads "
                "PACKET_INDEX.json and/or NIS certificates to extract: "
                "packet_version (folder label), tool_version (from certificate), "
                "input_hash, output_digest, canon_hash, repro_hash, "
                "provenance_hash, certificate_relpath, status, and file_list. "
                "Supports limit/offset pagination for large indices."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "include_audit": {
                        "type": "boolean",
                        "description": "Also scan artifacts/audit/ subdirectories. Default true.",
                        "default": True,
                    },
                    "limit": {
                        "type": "integer",
                        "description": (
                            "Maximum number of packets to return. "
                            "Default 0 (no limit, return all)."
                        ),
                        "default": 0,
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Skip the first N packets (for pagination). Default 0.",
                        "default": 0,
                    },
                },
                "required": [],
            },
        },
        # ── Release Bundle Builder ──
        {
            "name": "build_release_bundle",
            "description": (
                "Build a deterministic Zenodo release bundle. Selects evidence "
                "packets by family, copies them into a release_bundle/ directory, "
                "includes the ToE PDF + appendices, writes RELEASE_INDEX.json with "
                "per-file hashes and a combined digest. The bundle is ready for "
                "upload as a reproducibility archive."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "outdir": {
                        "type": "string",
                        "description": (
                            "Output directory name under artifacts/. "
                            "Example: 'release_bundle_v0_1'. Must not already exist."
                        ),
                        "default": "release_bundle_v0_1",
                    },
                    "include_all": {
                        "type": "boolean",
                        "description": (
                            "If true, include all discoverable packet families. "
                            "If false, only evidence_* directories. Default true."
                        ),
                        "default": True,
                    },
                    "include_audit": {
                        "type": "boolean",
                        "description": "Include audit/ packets. Default true.",
                        "default": True,
                    },
                    "include_docs": {
                        "type": "boolean",
                        "description": "Include ToE PDF and appendices. Default true.",
                        "default": True,
                    },
                },
                "required": [],
            },
        },
        # ── Release Bundle Verifier ──
        {
            "name": "verify_release_bundle",
            "description": (
                "Verify integrity of a release bundle. Reads RELEASE_INDEX.json, "
                "recomputes SHA-256 for a random sample of files, and recomputes "
                "the combined digest. Returns mismatches (if any) and whether the "
                "combined digest matches the expected value. Use this to confirm "
                "a bundle has not been corrupted before upload."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "bundle_dir": {
                        "type": "string",
                        "description": (
                            "Path to the release bundle directory (relative to "
                            "project root). Example: 'artifacts/release_bundle_v0_1'."
                        ),
                        "default": "artifacts/release_bundle_v0_1",
                    },
                    "sample_size": {
                        "type": "integer",
                        "description": (
                            "Number of files to randomly sample for hash "
                            "verification. Default 10."
                        ),
                        "default": 10,
                    },
                    "expected_digest": {
                        "type": "string",
                        "description": (
                            "Expected combined_digest to verify against. If not "
                            "provided, only recomputation is performed."
                        ),
                        "default": "",
                    },
                },
                "required": [],
            },
        },
        # ── Radial Collapse ──
        {
            "name": "run_radial_collapse",
            "description": (
                "Run a radial collapse experiment with GRUT memory coupling. "
                "Integrates spherically symmetric dust collapse using the same "
                "operator stack (memory, L_stiff, dissipation, tau_coupling) "
                "that governs FLRW expansion. r_sat is DERIVED from the ODE, "
                "never hardcoded. Supports single-trajectory mode and mass-sweep "
                "mode. Returns termination reason (saturation/singularity/max_steps), "
                "r_sat, compactness, Kretschner scalar, bounce detection, and "
                "apparent-horizon crossings."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "M_kg": {
                        "type": "number",
                        "description": "Total mass of collapsing object in kg. Default 1e30 (~0.5 M_sun).",
                        "default": 1e30,
                    },
                    "R0_m": {
                        "type": "number",
                        "description": "Initial radius in meters. If omitted, uses R0_factor * r_s.",
                    },
                    "R0_factor": {
                        "type": "number",
                        "description": "Initial radius as multiple of Schwarzschild radius. Default 10.",
                        "default": 10.0,
                    },
                    "tau0_s": {
                        "type": "number",
                        "description": "Memory relaxation timescale in seconds. Canon: 1.3225e15 s.",
                        "default": 1.3225e15,
                    },
                    "alpha_vac": {
                        "type": "number",
                        "description": "Vacuum screening fraction. Canon: 1/3.",
                        "default": 0.3333333333333333,
                    },
                    "gamma_diss": {
                        "type": "number",
                        "description": "Dissipation rate in s^-1. Default 1e-15.",
                        "default": 1e-15,
                    },
                    "H_cap": {
                        "type": "number",
                        "description": "L_stiff collapse rate cap in s^-1. Canon: 10^6 yr^-1.",
                        "default": 3.168808781402895e-02,
                    },
                    "n_steps": {
                        "type": "integer",
                        "description": "Maximum integration steps. Default 50000.",
                        "default": 50000,
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["single", "mass_sweep"],
                        "description": "single: one trajectory. mass_sweep: sweep r_sat over mass range.",
                        "default": "single",
                    },
                    "M_min_kg": {
                        "type": "number",
                        "description": "Minimum mass for sweep (kg). Required for mass_sweep mode.",
                    },
                    "M_max_kg": {
                        "type": "number",
                        "description": "Maximum mass for sweep (kg). Required for mass_sweep mode.",
                    },
                    "n_masses": {
                        "type": "integer",
                        "description": "Number of mass points in sweep. Default 10.",
                        "default": 10,
                    },
                },
                "required": [],
            },
        },
    ]
