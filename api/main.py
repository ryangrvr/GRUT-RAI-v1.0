from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pathlib import Path
import uuid
import hashlib
from datetime import datetime
import numpy as np

from core.constants import GRUTParams
from core.schemas import (
    RunRequest,
    AskRequest,
    AskResponse,
    GrutRunRequest,
    GrutRunResponse,
    GrutCanonResponse,
    RaiChatRequest,
    RaiChatResponse,
    RaiSessionNewResponse,
    RaiSessionDebugResponse,
    ZetaTauScalingRequest,
    ZetaTauScalingResponse,
    CasimirDensitySweepRequest,
    CasimirDensitySweepResponse,
    PTADispersionProbeRequest,
    PTADispersionProbeResponse,
    GlassTransitionSweepRequest,
    GlassTransitionSweepResponse,
    RaiAskRequest,
    RaiAskResponse,
    RaiAskResponseBody,
    RaiStatusResponse,
    ChartData,
    CertificateSummary,
    SuggestionItem,
    GenerateSweepRequest,
)
from core.narrative import build_narrative
from core.engine import run_engine
from core.nis import cfl_gate_or_raise, SovereignCausalError, build_nis_report, compute_cfl, compute_determinism_stamp, MYR_IN_S
from storage.memory_store import InMemoryRunStore
from storage.db import get_store
from storage.rai_session_store import RAISessionStore
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
from grut.lensing import run_lensing
from observer.observer_state import FrameConfig, compute_observer_state

# AI orchestrator (Phase H)
from ai.orchestrator import respond as ai_respond, AIResponse as _AIResponse
from ai.client import get_ai_client

params = GRUTParams()
store = InMemoryRunStore()
db_store = get_store()

# Seed GRUTipedia canonical topics (if missing)
DEFAULT_TOPICS = [
    # ── Core Constants & Parameters ──
    {
        "slug": "tau0-memory-window",
        "title": "\u03c4\u2080 \u2014 Memory Window",
        "definition_md": (
            "\u03c4\u2080 is the canonical memory relaxation timescale (41.9 Myr). It governs how "
            "long past sourcing influences the present cosmological response. The universe "
            "'remembers' its expansion history over this window via an exponential retarded kernel.\n\n"
            "Phase I canon derives \u03c4\u2080 = \u03c4_\u039b / S with S = 108\u03c0 as a consistency check "
            "(H\u2080 remains baseline-defined). The effective timescale \u03c4_eff adapts with redshift "
            "through the coupling operator OP_TAU_COUPLING."
        ),
        "equations_md": (
            "fuzz_fraction = eps_t / tau_0\n\n"
            "tau_eff(z) = tau_0 * TAU_FACTOR * (H0/H(z))^p\n\n"
            "kernel: K(dt) = (1/tau_eff) exp(-dt/tau_eff) Theta(dt)\n\n"
            "susceptibility: chi(omega) = alpha_vac / (1 - i * omega * tau_0)"
        ),
        "edition": 1,
        "tags": ["core", "numerics"],
    },
    {
        "slug": "epsilon-fuzz-fraction",
        "title": "\u03b5 \u2014 Fuzz Fraction",
        "definition_md": (
            "The fuzz fraction \u03b5t/\u03c4\u2080 measures how close the current integration "
            "time is to the memory relaxation window. When \u03b5t/\u03c4\u2080 \u226a 1 the system is "
            "'cold' (memory dominates); when \u03b5t/\u03c4\u2080 \u2248 1 the system approaches the "
            "memory horizon.\n\n"
            "This dimensionless ratio appears in NIS certificates as a diagnostic for "
            "numerical trustworthiness. High fuzz fractions signal that the integrator "
            "is operating near the edge of the causal window and results should be "
            "interpreted with care."
        ),
        "edition": 1,
        "tags": ["core", "numerics"],
    },
    {
        "slug": "alpha-mem",
        "title": "\u03b1_mem \u2014 Memory Coupling Weight",
        "definition_md": (
            "\u03b1_mem controls the weight of the memory-smoothed correction to the Hubble "
            "parameter. The modified Friedmann equation is:\n\n"
            "H\u00b2 = (1 - \u03b1_mem) \u00b7 H_base\u00b2 + \u03b1_mem \u00b7 M_X\n\n"
            "Setting \u03b1_mem = 0 recovers standard cosmology (no memory). Setting \u03b1_mem = 1 "
            "is full memory correction. Canon default: 0.1 (TUNABLE, bounds [0, 1]).\n\n"
            "This is the primary parameter that distinguishes GRUT from \u039bCDM. It can be "
            "swept to produce sensitivity analyses and is included in NIS certificates for "
            "reproducibility."
        ),
        "equations_md": "H^2 = (1 - alpha_mem) * H_base^2 + alpha_mem * M_X",
        "edition": 1,
        "tags": ["core", "numerics"],
    },
    {
        "slug": "lambda-lock",
        "title": "\u039b_lock \u2014 Geometric Anchor",
        "definition_md": (
            "\u039b_lock = 2/\u221a3 \u2248 1.1547 is the geometric anchor derived from the GRUT "
            "refractive index n_g(0) = 2/\u221a3. It is a fundamental dimensionless scaling "
            "ratio that appears in the relationship between the memory kernel and the "
            "cosmological expansion.\n\n"
            "Canon status: LOCKED (Phase I frozen constant)."
        ),
        "edition": 1,
        "tags": ["core"],
    },
    {
        "slug": "screening-s-108pi",
        "title": "S = 108\u03c0 \u2014 Vacuum Screening Factor",
        "definition_md": (
            "S = 108\u03c0 \u2248 339.29 is the vacuum screening factor relating the cosmological "
            "timescale \u03c4_\u039b = H\u2080\u207b\u00b9 to the memory timescale \u03c4\u2080:\n\n"
            "\u03c4\u2080 = \u03c4_\u039b / S\n\n"
            "Derived from \u03b1_vac = 1/3: S = 12\u03c0 / \u03b1_vac\u00b2 = 12\u03c0 / (1/9) = 108\u03c0.\n\n"
            "This connects the microscopic vacuum response fraction to the macroscopic "
            "memory timescale without introducing free parameters."
        ),
        "equations_md": "S = 12*pi / alpha_vac^2 = 108*pi\n\ntau_0 = tau_Lambda / S = H0^(-1) / (108*pi)",
        "edition": 1,
        "tags": ["core"],
    },
    # ── Operators & Engine ──
    {
        "slug": "s-phase-state-preparation",
        "title": "S-phase \u2014 State Preparation Operator",
        "definition_md": (
            "OP_S_PHASE is the first per-step operator in the GRUT execution stack. "
            "It enforces physical constraints on the state vector before integration:\n\n"
            "- Scale factor floor: a := max(a, a_min) where a_min = 10\u207b\u00b9\u00b2\n"
            "- Density non-negativity: require \u03c1 \u2265 0\n"
            "- Equation of state: p := w \u00b7 \u03c1 (baseline EOS unless overridden)\n\n"
            "This operator prevents numerical pathologies from propagating into the "
            "integration and is mandatory for all runs."
        ),
        "edition": 1,
        "tags": ["operators", "numerics"],
    },
    {
        "slug": "dissipation-operator",
        "title": "Dissipation D(z) \u2014 Damping Operator",
        "definition_md": (
            "OP_DISSIPATION applies positive-definite damping to the Hubble parameter "
            "each integration step:\n\n"
            "H := H \u00b7 exp(-\u03b3_H \u00b7 \u0394t)\n\n"
            "The damping rate \u03b3_H \u2265 0 is TUNABLE (canon default: 0.0). With observer "
            "modulation enabled, the dissipation scales as:\n\n"
            "D *= (1 + \u03bb \u00b7 \u0394S), clamped to [0.5, 3.0]\n\n"
            "where \u0394S is the observer entropy contribution. The dissipation is bounded "
            "at 0.999 (it cannot fully erase the Hubble rate). This ensures "
            "thermodynamic consistency: the universe dissipates energy but never "
            "reaches absolute zero expansion."
        ),
        "equations_md": "H := H * exp(-gamma_H * dt)\n\nD_modulated = D * (1 + lambda * deltaS), clamped [0.5, 3.0]",
        "edition": 1,
        "tags": ["core", "operators"],
    },
    {
        "slug": "l-stiff-guardrail",
        "title": "L-Stiff \u2014 Anti-Singularity Stiffening",
        "definition_md": (
            "OP_L_STIFF is the anti-singularity guardrail. If |H| exceeds the numerical "
            "cap H_cap (10\u2076 yr\u207b\u00b9), the operator clamps it:\n\n"
            "If |H| > H_cap: H := sign(H) \u00b7 H_cap\n\n"
            "This prevents numerical divergence near cosmological singularities while "
            "preserving the sign of H. Any activation is logged as L_STIFF_ACTIVATED "
            "and flagged in the NIS certificate."
        ),
        "edition": 1,
        "tags": ["operators", "numerics"],
    },
    {
        "slug": "tau-coupling-operator",
        "title": "\u03c4_eff(H) \u2014 Cosmological Coupling",
        "definition_md": (
            "OP_TAU_COUPLING computes the effective memory timescale as a function of "
            "the instantaneous Hubble rate:\n\n"
            "\u03c4_eff(H) = \u03c4\u2080 / (1 + (H\u03c4\u2080)\u00b2)\n\n"
            "This makes the memory window contract during rapid expansion (high H) "
            "and relax toward \u03c4\u2080 during slow expansion. The coupling is what makes "
            "GRUT a dynamical theory rather than a constant-parameter extension of \u039bCDM."
        ),
        "equations_md": "tau_eff(H) = tau_0 / (1 + (H * tau_0)^2)",
        "edition": 1,
        "tags": ["core", "operators"],
    },
    {
        "slug": "memory-kernel",
        "title": "Memory Kernel \u2014 Causal Retarded Kernel",
        "definition_md": (
            "The GRUT memory kernel is an exponential retarded kernel:\n\n"
            "K(s) = (1/\u03c4_eff) exp(-s/\u03c4_eff) \u0398(s)\n\n"
            "where \u0398(s) is the Heaviside step function enforcing strict causality "
            "(only past states contribute). The integral is normalized to 1.\n\n"
            "The equivalent ODE form (computationally efficient):\n\n"
            "\u03c4_eff \u00b7 dM_X/dt + M_X = X(t), where X = H_base\u00b2\n\n"
            "M_X is the memory state variable that tracks the smoothed history of the "
            "cosmological driver. This causal kernel is the mathematical core of GRUT."
        ),
        "equations_md": (
            "K(s) = (1/tau_eff) * exp(-s/tau_eff) * Theta(s)\n\n"
            "integral_0^inf K(s) ds = 1\n\n"
            "ODE: tau_eff * dM_X/dt + M_X = X(t)"
        ),
        "edition": 1,
        "tags": ["core"],
    },
    {
        "slug": "genesis-operator",
        "title": "Genesis \u2014 Cold Start Operator",
        "definition_md": (
            "OP_GENESIS is the boundary condition solver that initializes the memory "
            "state M_X at the start of integration. It runs once (bootstrap_only = true).\n\n"
            "Steps:\n"
            "1. Sanitize inputs (a \u2265 a_min, \u03c1 \u2265 0, p = w\u03c1 unless provided)\n"
            "2. Compute H_base\u00b2 from the unmodified closure equation\n"
            "3. Set M_X(t\u2080) using the genesis memory_init mode (default: steady_state)\n"
            "4. Recompute H(t\u2080) using the GRUT closure with M_X(t\u2080)\n"
            "5. Compute \u03c4_eff(H(t\u2080))\n\n"
            "The steady-state initialization assumes the universe has been in its current "
            "state long enough for memory to equilibrate: M_X = H_base\u00b2."
        ),
        "edition": 1,
        "tags": ["operators", "numerics"],
    },
    # ── Observables ──
    {
        "slug": "fsigma8-growth",
        "title": "f\u03c38(z) \u2014 Linear Growth Observable",
        "definition_md": (
            "f\u03c38(z) is the key structure-growth observable that combines the growth "
            "rate f with the amplitude \u03c38:\n\n"
            "f\u03c38(z) = f(z) \u00b7 \u03c38(z)\n\n"
            "where f = dln D/dln a (growth rate) and \u03c38(z) = \u03c38,0 \u00b7 D(z)/D(0).\n\n"
            "The growth factor D(z) satisfies the second-order ODE:\n\n"
            "D'' + [2 + dln H/dln a] D' - (3/2) \u03a9_m(a) D = 0\n\n"
            "In GRUT, H(z) is modified by the memory kernel, which alters the growth "
            "history relative to \u039bCDM. The canon default normalization is \u03c38,0 = 0.811."
        ),
        "equations_md": (
            "D'' + [2 + dln H/dln a] D' - (3/2) Omega_m(a) D = 0\n\n"
            "f = D'/D = dln D / dln a\n\n"
            "fsigma8(z) = f(z) * sigma8_0 * D(z)/D(0)"
        ),
        "edition": 1,
        "tags": ["observables", "core"],
    },
    {
        "slug": "hubble-tension",
        "title": "Hubble Tension \u2014 H(z) Evidence",
        "definition_md": (
            "The Hubble tension refers to the discrepancy between local (distance ladder) "
            "and early-universe (CMB) measurements of H\u2080. GRUT addresses this by modifying "
            "the late-time expansion history through the memory kernel.\n\n"
            "The hubble_tension_packet tool runs GRUT and \u039bCDM side-by-side against "
            "compiled H(z) observations (cosmic chronometer, BAO, and combined datasets). "
            "It produces residuals, E(z) = H(z)/H\u2080 comparisons, and NIS-certified evidence "
            "packets with per-file SHA-256 hashes.\n\n"
            "The evidence packets support multiple dataset policies (cc_only, bao_only, all) "
            "and E_obs anchoring strategies (lowest_z, median_lowz)."
        ),
        "equations_md": (
            "E_LCDM(z) = sqrt( Omega_m*(1+z)^3 + Omega_k*(1+z)^2 + Omega_Lambda + Omega_r*(1+z)^4 )\n\n"
            "E(z) = H(z) / H0"
        ),
        "edition": 1,
        "tags": ["observables", "evidence"],
    },
    # ── Integrity & Certificates ──
    {
        "slug": "cfl-causal-gate",
        "title": "CFL Causal Gate",
        "definition_md": (
            "The CFL (Courant-Friedrichs-Lewy) causal gate is a hard NIS integrity "
            "check that enforces causal consistency in the integrator. It verifies that "
            "the numerical timestep does not exceed the causal horizon:\n\n"
            "\u0394t \u2264 CFL_factor / |H_max|\n\n"
            "If violated, the run is flagged with NIS status FAIL and results are "
            "rejected. This prevents superluminal information propagation in the "
            "numerical solution and is non-negotiable."
        ),
        "edition": 1,
        "tags": ["numerics", "integrity"],
    },
    {
        "slug": "nis-certificates",
        "title": "NIS \u2014 Numerical Integrity Standard",
        "definition_md": (
            "NIS (Numerical Integrity Standard) provides deterministic reproducibility "
            "certificates for every engine run. Each certificate contains:\n\n"
            "- **determinism_stamp**: SHA-256 of (inputs + code_version + seed)\n"
            "- **canon_hash**: Hash of the frozen canon parameters used\n"
            "- **input_hash**: Hash of the specific input configuration\n"
            "- **output_digest**: SHA-256 of all output arrays\n"
            "- **repro_hash**: Combined hash for full reproducibility verification\n\n"
            "**Status levels**:\n"
            "- **PASS**: All hard gates cleared (CFL, bounds, handoff)\n"
            "- **WARN**: Completed but guardrails flagged sensitivity\n"
            "- **FAIL**: Integrity gate blocked the run\n\n"
            "NIS ensures that any GRUT result can be independently reproduced by "
            "anyone with the same canon parameters and input configuration."
        ),
        "edition": 1,
        "tags": ["integrity", "certificates"],
    },
    {
        "slug": "evidence-packet-schema",
        "title": "Evidence Packet Schema",
        "definition_md": (
            "Evidence packets are canonical, hash-stable bundles with schema "
            "`grut-evidence-v1`. Each packet contains:\n\n"
            "- **PACKET_INDEX.json**: Manifest with file hashes, output_digest, input_hash\n"
            "- **NIS certificate**: Determinism stamp and integrity status\n"
            "- **Data files**: Input observations, output arrays, run configurations\n"
            "- **canon_hash**: Ensures the packet was produced under frozen Phase I parameters\n\n"
            "Packets are designed for Zenodo archival and public replication. The "
            "RELEASE_INDEX.json aggregates all packets with a combined SHA-256 digest."
        ),
        "edition": 1,
        "tags": ["integrity", "publishing"],
    },
    {
        "slug": "sovereign-firewall",
        "title": "Sovereign Firewall",
        "definition_md": (
            "The Sovereign Firewall is the architectural principle that physics numbers "
            "ALWAYS come from the deterministic engine, never from the LLM. Claude "
            "narrates and interprets; the engine computes.\n\n"
            "This means:\n"
            "- All H(z), f\u03c38(z), \u03c4_eff values come from tool calls\n"
            "- Certificate hashes are engine-generated, never AI-generated\n"
            "- If a number is not available from a tool result, the AI must run the engine\n"
            "- The AI cannot 'estimate' or 'approximate' physics values\n\n"
            "This firewall is what makes GRUT-RAI trustworthy for scientific publication."
        ),
        "edition": 1,
        "tags": ["integrity", "architecture"],
    },
    # ── Observer Layer ──
    {
        "slug": "observer-profiles",
        "title": "Observer Profiles",
        "definition_md": (
            "GRUT models three observer engagement profiles that modulate dissipation "
            "through entropy contributions:\n\n"
            "- **Monk**: Zero engagement (baseline). No UI/sensor contribution to \u0394S.\n"
            "- **Astronomer**: Sensor-dominant (w_ui=0.2, w_sensor=0.8). Represents "
            "passive measurement.\n"
            "- **Participant**: UI-dominant (w_ui=0.9, w_sensor=0.1). Represents "
            "active experimental intervention.\n\n"
            "The entropy contribution is:\n"
            "\u0394S = w_ui \u00b7 UI_entropy + w_sensor \u00b7 Sensor_flux\n\n"
            "When observer modulation is enabled, \u0394S scales the dissipation operator."
        ),
        "equations_md": "deltaS = w_ui * UI_entropy + w_sensor * Sensor_flux",
        "edition": 1,
        "tags": ["observer", "theory"],
    },
    {
        "slug": "metabolic-states",
        "title": "Metabolic States \u2014 CALM / STRESS / PIVOT",
        "definition_md": (
            "The engine classifies each integration step into one of three metabolic states:\n\n"
            "- **CALM**: Far from handoff, numerically quiet (fuzz \u2264 0.01, heat \u2264 0.1, "
            "cap \u2264 0.1). Routine integration.\n"
            "- **STRESS**: Elevated observer/tension channels. The system is under "
            "numerical or physical pressure but still stable.\n"
            "- **PIVOT**: Sigmoid bridge active. Small input changes produce larger-than-"
            "usual output shifts. This is the transition regime where the memory kernel "
            "is maximally sensitive.\n\n"
            "Metabolic state is reported in NIS certificates and can be used to identify "
            "physically interesting redshift ranges."
        ),
        "edition": 1,
        "tags": ["numerics", "observer"],
    },
    # ── Anamnesis & Seth ──
    {
        "slug": "seth-kernel",
        "title": "Seth Kernel",
        "definition_md": (
            "The Seth Kernel is the causal exponential memory kernel used as the "
            "Digital Rights Management (DRM) primitive for the Anamnesis Lens. It is "
            "mathematically identical to the GRUT memory kernel K(s) but applied in "
            "the context of temporal reconstruction and memory-based inference.\n\n"
            "Named after the Egyptian god of chaos/transformation, the Seth Kernel "
            "represents the system's ability to reconstruct past states from present "
            "observations through causal, time-reversible memory operations."
        ),
        "edition": 1,
        "tags": ["anamnesis", "core"],
    },
    # ── Research Experiments ──
    {
        "slug": "zeta-operator",
        "title": "Zeta Operator \u2014 Riemann Hypothesis & \u03c4\u2080",
        "definition_md": (
            "**Important**: This experiment tests scaling hypotheses under pre-registered "
            "mappings; it does not prove the Riemann Hypothesis.\n\n"
            "The zeta operator maps Riemann zeta zero ordinates onto GRUT timescale "
            "parameters and tests whether the observed alignment between \u03c4\u2080 and zeta "
            "zero structure is statistically significant. Results are reported via "
            "null-model p-values and robustness checks.\n\n"
            "Any PASS status only means the observed match is statistically unlikely "
            "under uniform random hypotheses, not a claim of mathematical truth."
        ),
        "edition": 1,
        "tags": ["research", "integrity", "experiments"],
    },
    {
        "slug": "casimir-density-hypothesis",
        "title": "Casimir Density Hypothesis",
        "definition_md": (
            "**Disclaimer**: Numerical correspondence \u2260 mechanism.\n\n"
            "This experiment investigates whether the GRUT vacuum screening factor "
            "S = 108\u03c0 and the vacuum response fraction \u03b1_vac = 1/3 produce energy "
            "density values that correspond to Casimir-scale predictions.\n\n"
            "Phase I canon uses \u03b1_vac = 1/3 with n_g(0) = \u221a(1 + \u03b1_vac). "
            "H\u2080 is baseline-defined and any inversion is a consistency check only. "
            "The Casimir density sweep tool runs parameterized scans over plate "
            "separation and returns NIS-certified energy density comparisons."
        ),
        "edition": 1,
        "tags": ["research", "experiments"],
    },
    {
        "slug": "alpha-screening-hypothesis",
        "title": "Alpha Screening Hypothesis",
        "definition_md": (
            "**Disclaimer**: Numerical correspondence \u2260 mechanism.\n\n"
            "\u03b1_vac = 1/3 is the canonical vacuum response fraction in GRUT. This "
            "experiment explores whether there is a non-trivial relationship between "
            "\u03b1_vac and the QED fine-structure constant \u03b1 \u2248 1/137.\n\n"
            "\u03b1_vac is canonical and frozen; QED \u03b1 candidates are non-canonical and "
            "included only as optional comparisons. Any correspondence is reported "
            "as a numerical observation, not a physical mechanism."
        ),
        "edition": 1,
        "tags": ["research", "experiments"],
    },
    {
        "slug": "glass-transition-hypothesis",
        "title": "Glass Transition Hypothesis",
        "definition_md": (
            "**Disclaimer**: Numerical correspondence \u2260 mechanism.\n\n"
            "The glass-transition hypothesis explores whether the cosmological memory "
            "kernel exhibits a Deborah-number transition analogous to glass-forming "
            "liquids. The Deborah number De = \u03c4_relax / \u03c4_obs compares the relaxation "
            "time to the observation time.\n\n"
            "When De >> 1, the system appears 'solid' (memory-dominated). When De << 1, "
            "it flows freely (memoryless). The cosmological Deborah sweep tool scans "
            "this transition and produces NIS-certified evidence packets."
        ),
        "edition": 1,
        "tags": ["research", "experiments"],
    },
    {
        "slug": "quantum-decoherence-boundary",
        "title": "Quantum Decoherence Boundary",
        "definition_md": (
            "The quantum decoherence boundary evaluator tests GRUT's predictions for "
            "mass-dependent decoherence rates. The key observable is the slope of "
            "log(\u0393) vs log(m):\n\n"
            "- **GRUT self-consistent slope**: -2/3 (predicted by vacuum screening)\n"
            "- **Di\u00f3si-Penrose controlled slope**: -2 (gravitational decoherence baseline)\n\n"
            "The quantum evidence packet tool computes both slopes across mass and "
            "frequency scans, producing NIS-certified results. The \u03b1_vac = 1/3 "
            "screening fraction is what generates the -2/3 departure from the DP baseline."
        ),
        "equations_md": (
            "t_dec = [ (hbar * ell * tau_0^2) / (alpha_vac * G) ]^(1/3) * m^(-2/3)\n\n"
            "t_DP = (hbar * ell) / (G * m^2)\n\n"
            "Self-consistent slope: -2/3\n"
            "Controlled (DP) slope: -2\n\n"
            "alpha_vac = 1/3, S = 108*pi"
        ),
        "edition": 1,
        "tags": ["evidence", "experiments"],
    },
    # ── Lensing & Cluster Physics ──
    {
        "slug": "hff-cluster-lensing",
        "title": "HFF Cluster Lensing \u2014 A2744",
        "definition_md": (
            "The Hubble Frontier Fields (HFF) program provides deep gravitational "
            "lensing observations of massive galaxy clusters. GRUT-RAI processes "
            "convergence (\u03ba) and shear (\u03b3\u2081, \u03b3\u2082) maps from three independent mass "
            "reconstruction models for cluster Abell 2744:\n\n"
            "- **CATS** (Clusters As TelescopeS)\n"
            "- **GLAFIC** (Gravitational Lensing Analysis via Flexible Inference Code)\n"
            "- **Sharon** (Sharon & Johnson reconstruction)\n\n"
            "Each model produces independent \u03ba/\u03b3 maps from the same observational data, "
            "yielding distinct provenance hashes. The cluster profile packet tool "
            "computes radial profiles and optionally compares against GRUT model "
            "response predictions."
        ),
        "edition": 1,
        "tags": ["evidence", "lensing"],
    },
    {
        "slug": "rotation-curves",
        "title": "Rotation Curves \u2014 Galaxy-Scale Evidence",
        "definition_md": (
            "The rotation curve tool tests GRUT's memory-modified dynamics at galaxy "
            "scales. Input data provides observed rotation velocities v_obs(r) along "
            "with baryonic components (v_gas, v_star, optionally v_bulge).\n\n"
            "GRUT applies the memory response model to predict the total rotation "
            "curve without invoking a dark matter halo. The response_model parameter "
            "controls the modification: 'identity' (no modification), "
            "'radial_gate_v0', or 'memory_scale_boost_v0'.\n\n"
            "Results include \u03c7\u00b2 residuals and NIS-certified output digests. The "
            "rotation_batch tool runs multiple galaxies for statistical comparisons."
        ),
        "edition": 1,
        "tags": ["evidence", "experiments"],
    },
    # ── Architecture ──
    {
        "slug": "release-bundle",
        "title": "Release Bundle \u2014 Zenodo Archive",
        "definition_md": (
            "A release bundle is a deterministic archive of evidence packets prepared "
            "for public upload to Zenodo. Each bundle contains:\n\n"
            "- **packets/**: Normalized, human-readable packet directories\n"
            "- **docs/**: ToE PDF and appendices\n"
            "- **RELEASE_INDEX.json**: Manifest with per-file hashes and a combined "
            "SHA-256 digest\n\n"
            "The combined digest is computed from sorted output_digests + doc hashes, "
            "excluding timestamps. This makes the bundle deterministic: building "
            "twice from the same source yields identical digests.\n\n"
            "The verify_release_bundle tool can recompute and validate all hashes."
        ),
        "edition": 1,
        "tags": ["publishing", "integrity"],
    },
    {
        "slug": "forensic-mode",
        "title": "Forensic Mode",
        "definition_md": (
            "Forensic mode is a response option for the /rai/chat endpoint that strips "
            "all narrative and returns pure structured JSON. Use it by sending "
            "`mode: \"forensic\"` in the request body.\n\n"
            "In forensic mode, the AI returns only:\n"
            "- Packet paths and certificate fields\n"
            "- File hashes and output digests\n"
            "- Numeric metrics\n\n"
            "No commentary, interpretation, or suggestions. This mode exists for "
            "public replication disputes where precision and traceability are the "
            "only priorities."
        ),
        "edition": 1,
        "tags": ["architecture", "integrity"],
    },
    {
        "slug": "radial-collapse",
        "title": "Radial Collapse Solver",
        "definition_md": (
            "Spherically symmetric dust collapse with GRUT memory-kernel coupling.\n\n"
            "Uses the Oppenheimer-Snyder interior analogy: a uniform dust sphere's "
            "interior is a closed FRW universe, so the same operator stack "
            "(memory, L_stiff, dissipation, tau_coupling) governs the collapse.\n\n"
            "**State vector**: [R, V, M_drive]\n"
            "- R = shell radius (m)\n"
            "- V = dR/dt (m/s), V <= 0 during collapse\n"
            "- M_drive = memory state tracking gravitational drive (m/s^2)\n\n"
            "**Equations (canonical force decomposition)**:\n"
            "- dR/dt = V\n"
            "- dV/dt = -a_net\n"
            "- a_inward = (1-alpha)*GM/R^2 + alpha*M_drive\n"
            "- a_outward = a_Q  (OP_QPRESS_001 barrier, default 0 = off)\n"
            "- a_net = a_inward - a_outward\n"
            "- a_Q = (GM/R^2) * epsilon_Q * (r_s/R)^beta_Q\n"
            "- dM_drive/dt = (GM/R^2 - M_drive) / tau_eff\n"
            "- tau_eff = tau_0 / (1 + (|V/R| * tau_0)^2)\n\n"
            "**Post-step operators**:\n"
            "- L_stiff: if |V/R| > H_cap then V = -H_cap * R\n"
            "- Dissipation: V *= exp(-gamma_diss * dt)\n\n"
            "**Endpoint status (OP_QPRESS_001)**:\n"
            "- LOCKED: Tier 0 local-tau closure fixes frozen-collapse pathology\n"
            "- LOCKED: the old finite-radius endpoint was an L_stiff x V_tol artifact\n"
            "- LOCKED: OP_QPRESS_001 passes the anti-artifact acceptance suite\n"
            "- CANDIDATE: r_sat = epsilon_Q^(1/beta_Q) * r_s under OP_QPRESS_001\n"
            "- ACTIVE: derivation of epsilon_Q and beta_Q remains a research target\n\n"
            "**Key control parameter**: tau0/t_dyn (timescale competition ratio). "
            "When >> 1, memory is too slow and collapse freezes. "
            "When ~ 1, memory participates meaningfully. "
            "When << 1, approaches GR limit.\n\n"
            "**Bounce exclusion (two-tier)**:\n"
            "- Tier 1 (M <= ~10^24 kg): Sign-definite. a_net > 0, M_drive > 0 throughout. STRUCTURAL.\n"
            "- Tier 2 (M >= ~10^30 kg): V <= 0 throughout but a_net can go transiently negative. CONDITIONAL.\n\n"
            "**Collapse classification**: stall | arrested_prehorizon | arrested_posthorizon | plunging | singular"
        ),
        "equations_md": (
            "**Canonical force decomposition**:\n"
            "  a_inward  = (1-alpha_vac)*G*M/R^2 + alpha_vac*M_drive\n"
            "  a_outward = a_Q = (G*M/R^2)*epsilon_Q*(r_s/R)^beta_Q  [OP_QPRESS_001]\n"
            "  a_net     = a_inward - a_outward\n"
            "  force_balance_residual = |a_net| / (G*M/R^2)\n\n"
            "dM_drive/dt = (G*M/R^2 - M_drive) / tau_eff\n\n"
            "tau_eff = tau_0 / (1 + (|V/R| * tau_0)^2)\n\n"
            "Equilibrium (OP_QPRESS_001): R_eq/r_s = epsilon_Q^(1/beta_Q)\n\n"
            "Compactness: C = 2*G*M / (R * c^2),  C >= 1 means trapped surface\n\n"
            "Kretschner: K = 48*(G*M)^2 / (c^4 * R^6)\n\n"
            "Timescale competition: tau0/t_dyn = tau0 / ((pi/2)*sqrt(R0^3/(2GM)))\n\n"
            "Bounce exclusion: Tier 1 (weak gravity) sign-definite a_net > 0, "
            "Tier 2 (astrophysical) numerical V <= 0 only"
        ),
        "edition": 3,
        "tags": ["hole-sector", "collapse", "operators", "timescale-competition",
                 "quantum-pressure", "force-decomposition"],
    },
    {
        "slug": "local-tau-hypothesis",
        "title": "Local-Tau Hypothesis",
        "definition_md": (
            "**Research target** — not yet derived.\n\n"
            "Phase G showed that cosmological tau_0 (41.92 Myr) is too large for direct "
            "reuse in stellar collapse dynamics. The relevant quantity is the ratio "
            "tau/t_dyn, not tau alone.\n\n"
            "**Hypothesis**: The local effective memory timescale in the hole sector is:\n\n"
            "  tau_eff_local = tau_0 * F(rho, C, K, t_dyn)\n\n"
            "where F is a dimensionless function of local conditions that brings "
            "tau/t_dyn into the regime where memory coupling produces meaningful physics.\n\n"
            "**What is known**:\n"
            "- When tau/t_dyn >> 1, memory cannot track gravity and collapse freezes or inverts\n"
            "- When tau/t_dyn ~ 1, memory participates and the sign theorem holds structurally\n"
            "- When tau/t_dyn << 1, memory tracks instantly and GR is recovered\n\n"
            "**What is NOT known**:\n"
            "- The functional form of F\n"
            "- Whether F is universal or sector-dependent\n"
            "- Whether the local-tau closure produces a genuine saturation radius\n\n"
            "**Core insight**: The collapse sector is governed by a timescale-competition law, "
            "not by a universal fixed-memory constant applied blindly across regimes."
        ),
        "equations_md": (
            "tau_eff_local = tau_0 * F(rho, C, K, t_dyn)\n\n"
            "Control parameter: tau0/t_dyn = tau0 / ((pi/2)*sqrt(R0^3/(2GM)))\n\n"
            "Regime map:\n"
            "  tau0/t_dyn >> 1  =>  memory frozen, collapse suppressed\n"
            "  tau0/t_dyn ~ 1   =>  memory participates, sign theorem structural\n"
            "  tau0/t_dyn << 1  =>  GR recovered"
        ),
        "edition": 1,
        "tags": ["hole-sector", "collapse", "research-target", "timescale-competition"],
    },
    {
        "slug": "op-qpress-001",
        "title": "OP_QPRESS_001 — Quantum Pressure Barrier",
        "definition_md": (
            "Compactness-dependent quantum pressure barrier operator for the "
            "radial collapse solver.\n\n"
            "**Equation**:\n"
            "  a_Q = (GM/R^2) * epsilon_Q * (r_s/R)^beta_Q\n\n"
            "Produces an asymptotic equilibrium at R_eq/r_s = epsilon_Q^(1/beta_Q) "
            "where a_inward = a_outward and force_balance_residual -> 0.\n\n"
            "**Parameters**:\n"
            "- epsilon_Q: barrier amplitude (default 0.0 = off; constrained value 1/9)\n"
            "- beta_Q: compactness exponent (default 2; constrained by Kretschner scaling)\n"
            "- When epsilon_Q = 0 the operator is OFF (backward compatible)\n\n"
            "**Preferred constrained law** (Phase III-B):\n"
            "  epsilon_Q = alpha_vac^2 = 1/9\n"
            "  beta_Q = 2\n"
            "  R_eq / r_s = alpha_vac = 1/3\n"
            "  C_eq = 3\n"
            "  Status: CONSTRAINED (not fully first-principles derived)\n"
            "  Passes all 11 anti-artifact acceptance criteria\n\n"
            "**Status ladder**:\n"
            "- LOCKED: Tier 0 local-tau closure fixes frozen-collapse pathology\n"
            "- LOCKED: Old finite-radius endpoint was an L_stiff x V_tol artifact\n"
            "- LOCKED: OP_QPRESS_001 passes anti-artifact acceptance suite\n"
            "- LOCKED: Barrier dominance Phi = a_outward/a_inward as order parameter\n"
            "- CONSTRAINED: epsilon_Q = alpha_vac^2, beta_Q = 2 "
            "(preferred constrained law, not fully derived)\n"
            "- CANDIDATE: r_sat = (1/3) r_s as physical saturation radius\n"
            "- ACTIVE / RESEARCH TARGET: micro-derivation of alpha_vac^2 coupling\n"
            "- ACTIVE / RESEARCH TARGET: exterior observables, unitarity, archive\n\n"
            "**Boundary of current claim**:\n"
            "DEMONSTRATED: Genuine finite-radius equilibrium where a_net -> 0 "
            "physically, independent of V_tol, R0, H_cap, and M. Operator-driven "
            "(a_outward/a_grav = 1), stable under perturbation. Preferred "
            "constrained law produces R_f/r_s = 1/3 exactly in benchmark.\n"
            "NOT DEMONSTRATED: micro-derivation of alpha_vac^2 coupling. "
            "No exterior observables, unitarity constraints, or archive proof. "
            "Does NOT claim to solve the black hole information paradox or "
            "establish final ontology."
        ),
        "equations_md": (
            "a_Q = (GM/R^2) * epsilon_Q * (r_s/R)^beta_Q\n\n"
            "General equilibrium: R_eq/r_s = epsilon_Q^(1/beta_Q)\n\n"
            "Constrained law: epsilon_Q = alpha_vac^2 = 1/9, beta_Q = 2\n"
            "  => R_eq / r_s = alpha_vac = 1/3\n"
            "  => C_eq = 1/alpha_vac = 3\n\n"
            "Stability: d(a_net)/dR > 0 at R_eq  (derived: beta*GM/R^3 > 0)\n\n"
            "Canonical force decomposition:\n"
            "  a_inward  = (1-alpha)*GM/R^2 + alpha*M_drive\n"
            "  a_outward = a_Q\n"
            "  a_net     = a_inward - a_outward\n"
            "  force_balance_residual = |a_net| / (GM/R^2)\n\n"
            "Phi = a_outward / a_inward  (order parameter)\n\n"
            "Endpoint motion classes:\n"
            "  sign_definite_infall | equilibrium_restoring |\n"
            "  overshoot_damped | bounce_violation"
        ),
        "edition": 2,
        "tags": [
            "hole-sector", "collapse", "operators",
            "quantum-pressure", "phase-iii",
        ],
    },
    {
        "slug": "collapse-endpoint-artifact",
        "title": "Collapse Endpoint Artifact & V_tol Caveat",
        "definition_md": (
            "The old finite-radius collapse endpoint was a numerical artifact, "
            "not physical equilibrium.\n\n"
            "**Artifact law**: R_f = (V_tol^2 * 2GM / H_cap^2)^(1/3)\n\n"
            "This position is set by the velocity-tolerance saturation detector "
            "(L_stiff guardrail) and has no physical content — it moves with "
            "V_tol and H_cap.\n\n"
            "**How OP_QPRESS_001 differs**:\n"
            "- The barrier endpoint R_eq/r_s = epsilon_Q^(1/beta_Q) is independent "
            "of V_tol, R0, and H_cap (< 1% spread in acceptance tests)\n"
            "- At the barrier endpoint, force_balance_residual -> 0 (genuine equilibrium)\n"
            "- The endpoint is operator-driven (a_outward/a_grav ~ 1)\n"
            "- Perturbations recover to R_eq (asymptotically stable)\n\n"
            "**V_tol caveat (barrier-engaged regime)**:\n"
            "Endpoint validation applies to barrier-engaged runs ONLY. Loose V_tol "
            "values (>= ~1e-6 for typical configurations) can cause the saturation "
            "detector to fire before the shell reaches the quantum pressure barrier, "
            "producing the old artifact endpoint.\n\n"
            "A run is classified as 'barrier-engaged' when R_f differs from the "
            "artifact prediction by more than 10%. Runs where R_f matches the artifact "
            "formula are 'artifact-dominated' — the saturation detector fires first. "
            "This is a saturation-detector priority issue, not a failure of the operator.\n\n"
            "**H_cap independence**: The barrier endpoint is independent of H_cap "
            "(< 1% spread across 2 orders of magnitude), unlike the artifact which "
            "scales as H_cap^(-2/3)."
        ),
        "equations_md": (
            "Artifact endpoint law:\n"
            "  R_f_artifact / r_s = (V_tol^2 * 2GM / H_cap^2)^(1/3) / r_s\n\n"
            "Barrier endpoint law:\n"
            "  R_eq / r_s = epsilon_Q^(1/beta_Q)   [independent of V_tol, H_cap]\n\n"
            "Barrier-engaged classification:\n"
            "  |R_f - R_f_artifact| / R_f > 0.10  =>  barrier-engaged\n"
            "  |R_f - R_f_artifact| / R_f < 0.10  =>  artifact-dominated"
        ),
        "edition": 1,
        "tags": ["hole-sector", "collapse", "artifact", "vtol-caveat"],
    },
    {
        "slug": "packet-endpoint-v0-1",
        "title": "PACKET_ENDPOINT_v0.1",
        "definition_md": (
            "Evidence packet for OP_QPRESS_001 endpoint acceptance.\n\n"
            "Built by tools/build_endpoint_packet.py following the "
            "grut-evidence-v1 schema.\n\n"
            "**Contents**:\n"
            "- PACKET_INDEX.json: Manifest with SHA-256 hashes\n"
            "- README_ENDPOINT.md: Human-readable summary with boundary of claim\n"
            "- acceptance.json: Machine-readable acceptance results (7 criteria)\n"
            "- force_decomposition.json: Canonical force budget at endpoint\n"
            "- vtol_sweep.json: V_tol insensitivity data\n"
            "- r0_sweep.json: R0 insensitivity data\n"
            "- stability.json: Perturbation recovery data\n"
            "- artifact_comparison.json: Artifact law comparison\n\n"
            "**Acceptance criteria** (all must PASS):\n"
            "1. V_tol insensitive: R_f spread < 1% across 4+ orders of V_tol "
            "(barrier-engaged runs)\n"
            "2. R0 insensitive: R_f spread < 1% across R0/r_s = 3..100\n"
            "3. Force balanced: force_balance_residual < 0.01\n"
            "4. Operator-driven: a_outward/a_grav > 0.5\n"
            "5. Not artifact: R_f deviates > 10% from artifact law\n"
            "6. Stable endpoint: perturbations converge to R_eq within 5%\n"
            "7. Stability positive: asymptotic stability indicator > 0\n\n"
            "**Status**: LOCKED (acceptance suite passes)."
        ),
        "equations_md": "",
        "edition": 1,
        "tags": ["hole-sector", "collapse", "evidence-packet", "acceptance"],
    },
    # ── Phase III: Whole Hole Thermodynamics ──
    {
        "slug": "barrier-dominance-phi",
        "title": "Phi — Barrier Dominance Order Parameter",
        "definition_md": (
            "Phi = a_outward / a_inward is the primary order parameter governing "
            "the transition from Quantum Fluid (collapsing matter with negligible "
            "barrier resistance) to Barrier-Dominated Compact Core (force-balanced "
            "endpoint).\n\n"
            "**Definition** (canonical force decomposition):\n"
            "  a_inward  = (1-alpha_vac)*GM/R^2 + alpha_vac*M_drive\n"
            "  a_outward = a_Q = (GM/R^2)*epsilon_Q*(r_s/R)^beta_Q\n"
            "  Phi = a_outward / a_inward\n\n"
            "**Physical meaning**:\n"
            "- Phi -> 0: the quantum pressure barrier is negligible. The shell "
            "is in free collapse governed by gravity and memory (Quantum Fluid regime).\n"
            "- Phi ~ 0.5: the barrier provides roughly half the resistance needed "
            "to halt collapse (Crystallization Threshold candidate).\n"
            "- Phi -> 1: the barrier balances inward forces. The shell approaches "
            "equilibrium (Barrier-Dominated Compact Core).\n"
            "- Phi = 1: exact force balance, a_net = 0.\n\n"
            "**Solver-backed benchmark behavior** (M=1e30, constrained law):\n"
            "The transition from Phi ~ 0 to Phi = 1 is smooth, with width "
            "~0.7 r_s. The candidate crystallization threshold (Phi = 0.5) "
            "falls at R/r_s ~ 0.47, compactness C ~ 2.12, which is post-horizon.\n\n"
            "**Status**: LOCKED in current solver language. Phi is a well-defined "
            "diagnostic computed from the canonical force decomposition."
        ),
        "equations_md": (
            "Phi = a_outward / a_inward\n\n"
            "a_inward  = (1-alpha_vac)*GM/R^2 + alpha_vac*M_drive\n"
            "a_outward = (GM/R^2)*epsilon_Q*(r_s/R)^beta_Q\n\n"
            "Regimes:\n"
            "  Phi < 0.01  =>  Quantum Fluid\n"
            "  Phi ~ 0.5   =>  Crystallization Threshold (candidate)\n"
            "  Phi > 0.99  =>  Barrier-Dominated Compact Core\n"
            "  Phi = 1     =>  exact equilibrium"
        ),
        "edition": 1,
        "tags": ["hole-sector", "phase-iii", "order-parameter", "thermodynamics"],
    },
    {
        "slug": "quantum-fluid",
        "title": "Quantum Fluid Regime",
        "definition_md": (
            "The Quantum Fluid regime is the portion of a collapse trajectory where "
            "the barrier dominance Phi = a_outward / a_inward is near zero. In this "
            "regime, the quantum pressure barrier (OP_QPRESS_001) is negligible and "
            "the dynamics are governed by gravity, memory coupling, and dissipation.\n\n"
            "**Criterion**: Phi < 0.01\n\n"
            "In the current benchmark (constrained law, M=1e30), the shell remains "
            "in the Quantum Fluid regime for most of its trajectory — from the "
            "initial radius down to R ~ r_s (horizon crossing). The barrier only "
            "becomes significant well inside the horizon.\n\n"
            "**Status**: LOCKED as solver-backed conceptual term in the benchmark regime."
        ),
        "equations_md": "Criterion: Phi = a_outward / a_inward < 0.01",
        "edition": 1,
        "tags": ["hole-sector", "phase-iii", "phase-vocabulary"],
    },
    {
        "slug": "crystallization-threshold",
        "title": "Crystallization Threshold (Candidate)",
        "definition_md": (
            "The Crystallization Threshold is the candidate name for the radius at "
            "which the barrier dominance Phi = a_outward / a_inward passes through "
            "~0.5, meaning the quantum pressure barrier provides roughly half the "
            "force needed to halt collapse.\n\n"
            "**Current benchmark result** (constrained law, M=1e30):\n"
            "  R/r_s ~ 0.47 at Phi = 0.5\n"
            "  Compactness C ~ 2.12\n"
            "  This is POST-HORIZON (C > 1)\n\n"
            "The term 'crystallization' is a candidate conceptual label, not a "
            "claim about solid-state physics or phase transitions in the conventional "
            "sense. It refers to the transition from free-falling fluid to "
            "force-balanced structure.\n\n"
            "**Status**: CANDIDATE — observed in the benchmark regime. Whether the "
            "threshold location is universal across masses and parameters has not "
            "been tested."
        ),
        "equations_md": (
            "Phi(R_cryst) = 0.5\n\n"
            "Under constrained law (benchmark):\n"
            "  R_cryst / r_s ~ 0.47\n"
            "  C_cryst ~ 2.12 (post-horizon)"
        ),
        "edition": 1,
        "tags": ["hole-sector", "phase-iii", "phase-vocabulary", "candidate"],
    },
    {
        "slug": "barrier-dominated-compact-core",
        "title": "Barrier-Dominated Compact Core (BDCC)",
        "definition_md": (
            "A Barrier-Dominated Compact Core is the endpoint state of collapse "
            "under OP_QPRESS_001, where the barrier dominance Phi -> 1 and "
            "the force_balance_residual -> 0.\n\n"
            "**Criterion**: Phi > 0.99 (barrier supplies > 99% of the "
            "counterforce to gravity+memory).\n\n"
            "Under the preferred constrained law (epsilon_Q = 1/9, beta_Q = 2), "
            "the BDCC forms at:\n"
            "  R_eq / r_s = alpha_vac = 1/3\n"
            "  Compactness C_eq = 3 (well inside the horizon)\n"
            "  Phi = 1.0 (exact force balance)\n\n"
            "**Key property**: The equilibrium is asymptotically stable — "
            "perturbations on both sides of R_eq are restored. The stability "
            "eigenvalue d(a_net)/dR is positive at R_eq.\n\n"
            "**Status**: CANDIDATE — realized in the solver under the constrained "
            "law. Whether this structure persists in a covariant treatment, and "
            "what its exterior observable signatures would be, are open research "
            "targets."
        ),
        "equations_md": (
            "Criterion: Phi = a_outward / a_inward > 0.99\n\n"
            "Under constrained law:\n"
            "  R_eq / r_s = alpha_vac = 1/3\n"
            "  C_eq = 1/alpha_vac = 3\n"
            "  force_balance_residual = 0\n"
            "  stability = d(a_net)/dR = beta*GM/R^3 > 0"
        ),
        "edition": 1,
        "tags": ["hole-sector", "phase-iii", "phase-vocabulary", "candidate"],
    },
    {
        "slug": "whole-hole",
        "title": "Whole Hole (Research Target)",
        "definition_md": (
            "The Whole Hole is the proposed name for the complete physical "
            "object that replaces the classical black hole singularity in GRUT: "
            "a Barrier-Dominated Compact Core located inside the horizon.\n\n"
            "**Working definition**: Barrier-Dominated Compact Core (Phi > 0.99) "
            "+ post-horizon (compactness C > 1).\n\n"
            "Under the preferred constrained law, the candidate Whole Hole has:\n"
            "  Core radius: R_eq = (1/3) r_s\n"
            "  Core compactness: C_eq = 3\n"
            "  Interior structure: smooth Phi(R) transition from Quantum Fluid to Core\n"
            "  Crystallization threshold: at R/r_s ~ 0.47, post-horizon\n\n"
            "**What is NOT established**:\n"
            "- Whether the exterior metric matches standard Schwarzschild/Kerr to "
            "sufficient precision that exterior observers cannot distinguish it\n"
            "- Whether the structure produces detectable echoes, modified ringdown, "
            "or shadow deviations\n"
            "- Whether the information ledger recovers unitarity\n"
            "- Whether the Newtonian-gauge structure survives covariant extension\n\n"
            "**Status**: ACTIVE / RESEARCH TARGET. The interior endpoint candidate "
            "exists in the solver but exterior consequences have not been computed. "
            "Phase III-C defines the exterior falsifier program."
        ),
        "equations_md": (
            "Working definition:\n"
            "  Whole Hole = BDCC + post-horizon\n"
            "  Criterion: Phi > 0.99 AND C > 1\n\n"
            "Under constrained law:\n"
            "  R_eq = alpha_vac * r_s = (1/3) r_s\n"
            "  C_eq = 3\n"
            "  Phi_eq = 1.0"
        ),
        "edition": 1,
        "tags": ["hole-sector", "phase-iii", "research-target", "ontology"],
    },
    {
        "slug": "r-sat-constrained",
        "title": "r_sat — Saturation Radius (Constrained Law)",
        "definition_md": (
            "The saturation radius r_sat is the physical radius at which the "
            "collapsing shell reaches force balance (a_net -> 0) under "
            "OP_QPRESS_001.\n\n"
            "**General law**: r_sat = epsilon_Q^(1/beta_Q) * r_s\n\n"
            "**Preferred constrained law** (Phase III-B):\n"
            "  r_sat = alpha_vac * r_s = (1/3) r_s\n"
            "  This follows from epsilon_Q = alpha_vac^2 = 1/9, beta_Q = 2.\n\n"
            "**Significance**: The same constant alpha_vac = 1/3 appears in "
            "three independent roles in GRUT:\n"
            "1. Weak-field vacuum susceptibility: chi(0) = alpha_vac\n"
            "2. Quantum bridge decoherence: via screening factor S = 12pi/alpha_vac^2\n"
            "3. Candidate endpoint radius: R_eq/r_s = alpha_vac\n\n"
            "Whether this triple appearance has a common structural origin "
            "remains open. The micro-derivation connecting vacuum response to "
            "endpoint radius has not been established.\n\n"
            "**Status**: CANDIDATE. Passes all anti-artifact acceptance criteria. "
            "Independent of V_tol, R0, H_cap, and M in the benchmark regime."
        ),
        "equations_md": (
            "r_sat = epsilon_Q^(1/beta_Q) * r_s  (general)\n\n"
            "Under constrained law:\n"
            "  r_sat = alpha_vac * r_s = (1/3) * r_s\n"
            "  r_sat / r_s = (1/9)^(1/2) = 1/3\n\n"
            "alpha_vac roles:\n"
            "  Susceptibility: chi(0) = alpha_vac = 1/3\n"
            "  Screening: S = 12*pi / alpha_vac^2 = 108*pi\n"
            "  Endpoint: R_eq / r_s = alpha_vac = 1/3"
        ),
        "edition": 1,
        "tags": ["hole-sector", "phase-iii", "candidate", "constrained-law"],
    },
    {
        "slug": "information-ledger",
        "title": "Information Ledger (Skeleton)",
        "definition_md": (
            "Proxy-based information bookkeeping for collapse endpoint states.\n\n"
            "**Variables**:\n"
            "- I_fields: Bekenstein-Hawking-like area proxy, pi*R^2/l_P^2 "
            "(CLASSICAL, not quantum information)\n"
            "- I_metric_memory: placeholder scaling, I_fields * mem_ratio * Phi "
            "(NOT derived from first principles)\n"
            "- I_total: I_fields + I_metric_memory (additivity HYPOTHESIZED)\n"
            "- archive_access_status: OPEN / FROZEN / UNKNOWN (compactness-based)\n"
            "- conservation_status: UNTESTED\n\n"
            "**What is observed**: Late-time stabilization of I_total near the "
            "barrier-dominated endpoint. The proxy ledger shows structured "
            "saturation behavior.\n\n"
            "**What is NOT proven**:\n"
            "- Information conservation is UNTESTED\n"
            "- No dynamic step-by-step conservation check exists\n"
            "- Proxy definitions are not quantum information measures\n"
            "- The additivity I_total = I_fields + I_metric_memory is hypothesized\n"
            "- This does NOT solve the black hole information paradox\n"
            "- This does NOT prove unitarity\n\n"
            "**Status**: ACTIVE / RESEARCH TARGET."
        ),
        "equations_md": (
            "I_fields = pi * R^2 / l_P^2  (classical area proxy)\n\n"
            "I_metric_memory = I_fields * mem_ratio * Phi  (placeholder)\n\n"
            "I_total = I_fields + I_metric_memory  (hypothesized additive)\n\n"
            "archive_access:\n"
            "  C < 1  =>  OPEN (pre-horizon)\n"
            "  C >= 1 =>  FROZEN (post-horizon)\n\n"
            "conservation_status: UNTESTED"
        ),
        "edition": 1,
        "tags": ["hole-sector", "phase-iii", "research-target", "information"],
    },
    # ── Phase III-C: Exterior Matching ──
    {
        "slug": "exterior-matching",
        "title": "Exterior Matching — WP1 Gateway Analysis",
        "definition_md": (
            "Phase III-C WP1: the gateway question for all exterior falsifiers.\n\n"
            "**Question**: Does a Barrier-Dominated Compact Core at R_eq = (1/3) r_s "
            "produce any exterior deviation from standard Schwarzschild behavior?\n\n"
            "**Current best assessment**: Schwarzschild-like exterior is the "
            "LEADING CANDIDATE, at moderate confidence.\n\n"
            "**Basis**:\n"
            "- Total enclosed mass M is fixed (dust model, no radiation)\n"
            "- M_drive is shell-local in the current solver\n"
            "- At R >> r_s, a_Q/a_grav -> 0 (barrier negligible far from shell)\n"
            "- Oppenheimer-Snyder analogy starts from Schwarzschild exterior\n\n"
            "**Conditional on**:\n"
            "- M_drive being a matter-sector variable (not a spacetime field)\n"
            "- OP_QPRESS_001 not having exterior gravitational self-energy\n\n"
            "**NOT proven**: This assessment is NOT a rigorous proof. A covariant "
            "treatment of the GRUT field equations is required to determine "
            "whether Birkhoff's theorem holds in the modified theory.\n\n"
            "**Implication for WP2 (ringdown/echo)**: CONDITIONAL GO. Interior "
            "echoes can be computed using Schwarzschild exterior as background. "
            "Echo predictions depend on interior boundary condition at R_eq.\n\n"
            "**Implication for WP3 (shadow)**: CONDITIONAL GO, expected null "
            "result. Under Schwarzschild exterior, shadow is identical to GR.\n\n"
            "**Module**: grut/exterior_matching.py\n\n"
            "**Status**: ANALYSIS COMPLETE — Schwarzschild-like, conditional."
        ),
        "equations_md": (
            "Effective exterior metric (parameterized):\n"
            "  ds^2 = -f(r) dt^2 + f(r)^(-1) dr^2 + r^2 dOmega^2\n"
            "  f(r) = 1 - r_s/r + delta_f(r)\n\n"
            "Leading candidate: delta_f = 0 (Schwarzschild)\n\n"
            "Birkhoff status: preserved_candidate (conditional)\n\n"
            "Effective enclosed mass: M_eff = M_input (dust, no radiation)\n"
            "  M_eff / M_input = 1.0"
        ),
        "edition": 1,
        "tags": ["hole-sector", "phase-iii-c", "exterior", "gateway"],
    },
    {
        "slug": "birkhoff-status",
        "title": "Birkhoff Status in GRUT",
        "definition_md": (
            "Birkhoff's theorem guarantees that any spherically symmetric vacuum "
            "region has the Schwarzschild metric in GR. The question is whether "
            "GRUT preserves this property.\n\n"
            "**Current status**: UNDERDETERMINED\n\n"
            "**Arguments for preservation**:\n"
            "- The GRUT memory M_drive is shell-local in the solver (no spatial "
            "propagation equation exists)\n"
            "- Total enclosed mass is conserved (dust model)\n"
            "- The quantum pressure barrier a_Q is negligible at R >> r_s\n\n"
            "**Arguments against**:\n"
            "- If M_drive is a spacetime field (not matter-local), the exterior "
            "is not vacuum in the GRUT theory\n"
            "- If GRUT modifies the gravitational field equations, the vacuum "
            "equations change and may not have Birkhoff's property\n"
            "- The Newtonian-gauge solver cannot rigorously address this\n\n"
            "**Required closure**: Covariant GRUT field equations and a proof "
            "that the vacuum sector admits only Schwarzschild.\n\n"
            "**Status**: UNDERDETERMINED — leading assessment is preservation, "
            "but proof is missing."
        ),
        "equations_md": "",
        "edition": 1,
        "tags": ["hole-sector", "phase-iii-c", "exterior", "birkhoff"],
    },
    # ── Phase III-C WP2: Ringdown / Echo Falsifier ──
    {
        "slug": "ringdown-echo-channel",
        "title": "Ringdown / Echo Falsifier Channel",
        "definition_md": (
            "**STATUS**: FROZEN CANDIDATE FALSIFIER CHANNEL — PDE-informed constrained estimate "
            "(mixed_viscoelastic, Q ~ 6-7.5, echo ~ 1.1%; "
            "conditional on WP1 Schwarzschild-like exterior)\n\n"
            "The echo channel is the primary route by which a Barrier-Dominated Compact "
            "Core (BDCC) interior can leak into an exterior observable, even under an "
            "exactly Schwarzschild exterior metric.\n\n"
            "**Mechanism**: After a perturbation (e.g., merger ringdown), ingoing waves "
            "cross the potential peak at the light ring (r = 3/2 r_s), enter the "
            "horizon region, and encounter the BDCC at R_eq. If the BDCC reflects some "
            "fraction, waves propagate outward, partially leak through the potential "
            "peak (observable), and partially bounce back — creating a series of "
            "delayed, decaying pulses: ECHOES.\n\n"
            "**LEADING PDE-INFORMED RESULT (30 M_sun, R_eq = r_s/3)**:\n"
            "- Echo time delay: ~0.52 ms (ORDER OF MAGNITUDE estimate)\n"
            "- Δt_echo / r_s = 1.76 (dimensionless, mass-independent)\n"
            "- Interior response: MIXED VISCOELASTIC (Q ≈ 7.5, mass-independent)\n"
            "- Reflection coefficient: r_PDE ≈ 0.30 (amplitude)\n"
            "- Echo amplitude: ~1.1% of main QNM signal\n"
            "- Structural identity: ω₀ × τ_local = 1.0 (exact within PDE closure)\n\n"
            "**SUPERSEDED PROXY RESULT (WP2C, historical)**:\n"
            "The pre-PDE proxy gave Q ≈ 515 (reactive_candidate), r ≈ 0.98, echo ≈ 3.7%. "
            "This was based on an eigenfrequency error (extra 1/R_eq factor in omega_core). "
            "The PDE-corrected eigenfrequency is omega_0^2 = beta_Q * GM / R_eq^3. "
            "The proxy is a useful historical step but NOT the current leading estimate.\n\n"
            "**Structural Identity (PDE closure)**:\n"
            "ω₀ × τ_local = 1.0 — this is an exact identity within the current PDE closure "
            "framework. It implies that oscillation and local memory-relaxation timescales are "
            "locked together. This naturally favors a mixed viscoelastic regime (Q ~ 6) rather "
            "than a purely reactive or purely dissipative one. This identity is NOT claimed as "
            "a universal law independent of the closure used.\n\n"
            "**Transition-Width Correction (WP2D, VALIDATED)**:\n"
            "The Phase III-B transition (width ~0.703 r_s) is modeled with a graded "
            "impedance profile. Grading factor = 0.996 (< 1% correction). "
            "The sharp-boundary model is CONFIRMED as an excellent approximation.\n\n"
            "**COVARIANT CLOSURE (2026-03-11)**:\n"
            "First covariant pass (effective metric ansatz) CONFIRMS PDE structural results:\n"
            "- ω₀ × τ = 1.0: PRESERVED in covariant framework\n"
            "- Q ≈ 6.5: PRESERVED (mixed_viscoelastic confirmed)\n"
            "- Reflection: modified ±21% (r_cov ≈ 0.37 vs r_PDE ≈ 0.30)\n"
            "- Echo: ~1.1% PRESERVED (channel not collapsed)\n"
            "- Key finding: F_PDE(ω) = 0 dispersion relation SURVIVES — eigenfrequencies "
            "are zeros of F, independent of c_eff\n"
            "- Status: effective metric ansatz (NOT derived from field equations)\n"
            "- 5 closures resolved, 7 remaining\n\n"
            "**FIELD EQUATIONS (Phase III Final, 2026-03-11)**:\n"
            "Three candidate covariant formulations evaluated:\n"
            "- Candidate 1 (algebraic memory tensor): INSUFFICIENT — no independent dynamics\n"
            "- Candidate 2 (auxiliary scalar field): PREFERRED — scalarized first pass, minimal closure\n"
            "- Candidate 3 (nonlocal retarded kernel): FORMAL PARENT of Candidate 2\n"
            "Preferred: G_μν = (8πG/c⁴)(T_μν + T^Φ_μν) with τ_eff u^α∇_αΦ + Φ = X[g,T]\n"
            "T^Φ_μν is SCHEMATIC/EFFECTIVE. Scalar is minimal closure; tensorial open.\n"
            "Bianchi: combined conservation at effective level. α_mem/α_vac unification OPEN.\n"
            "7 remaining closures (T^Φ form, τ_eff curvature dependence, propagation, "
            "junction, Kerr, Love numbers, nonlinear coupling).\n\n"
            "**FREEZE NOTE (revised 2026-03-11)**: WP2 is FROZEN as candidate falsifier channel. "
            "The PDE closure reclassifies the interior from reactive_candidate (Q ~ 515, SUPERSEDED) "
            "to mixed_viscoelastic (Q ~ 6-7.5, LEADING). The covariant closure confirms structural "
            "results. The echo channel is weakened from ~3.7% to ~1.1% but not collapsed.\n\n"
            "**NONCLAIMS**:\n"
            "- Echoes are NOT predicted to exist. The module computes what they WOULD "
            "look like under assumptions.\n"
            "- Echo time delay is an ORDER OF MAGNITUDE estimate.\n"
            "- PDE closure is approximate (ODE linearisation); covariant closure confirms but is itself an effective ansatz.\n"
            "- Boltzmann model (r_amp ~ 0) remains viable if hidden dissipation exists.\n"
            "- Structural identity ω₀×τ=1 is exact only within current closure framework.\n"
            "- Pre-PDE proxy result (Q~515, r~0.98, echo~3.7%) is SUPERSEDED.\n"
            "- All results are CONDITIONAL on the WP1 exterior assessment.\n"
            "- Kerr generalization is not attempted.\n"
            "- mixed_viscoelastic is the best current candidate, not the final answer.\n"
            "- Field equations are a FIRST COVARIANT PASS — T^Φ_μν is schematic/effective.\n"
            "- Scalar memory field is the minimal closure; tensorial generalization remains open.\n"
            "- α_mem / α_vac unification is an OPEN QUESTION."
        ),
        "equations_md": (
            "Echo time delay (ORDER OF MAGNITUDE):\n"
            "  Δt_echo ≈ 2 × |r*(R_eq) - r*(r_peak)| / c\n\n"
            "PDE DISPERSION RELATION (LEADING — Phase III-C):\n"
            "  ω² = ω₀² + 2α ωg² / (1 + iωτ)\n"
            "  ω₀² = β_Q × GM / R_eq³  (CORRECT — from linearisation)\n"
            "  ωg² = GM / R_eq³  (gravitational reference frequency)\n\n"
            "STRUCTURAL IDENTITY:\n"
            "  ω₀ × τ_local = 1.0  (exact, mass-independent within PDE closure)\n"
            "  Q_PDE = β_Q / α_vac = 6.0  (universal quality factor)\n\n"
            "PDE damping:\n"
            "  γ_PDE = α ωg² τ / (1 + ω²τ²)\n\n"
            "Echo amplitudes (AMPLITUDE coefficients throughout):\n"
            "  A_n / A_0 ≈ |T|² × (r_surface_amp × r_peak_amp)^n\n\n"
            "SUPERSEDED proxy oscillation frequency:\n"
            "  omega_core² ~ β_Q × GM / R_eq⁴  (WRONG — extra 1/R_eq)\n\n"
            "QNM reference (l=2, Schwarzschild):\n"
            "  omega_R ≈ 0.3737 / M_geom,  tau_damp ≈ 1 / (0.0890 / M_geom)\n\n"
            "COVARIANT CLOSURE (effective metric ansatz):\n"
            "  k² = F_PDE(ω) / c_eff²  (same dispersion relation, modified wavevector)\n"
            "  c_eff² = c² |A_eff|² / (1 + α_eff)  (sub-luminal, c_eff/c ≈ 0.87)\n"
            "  η_cov = ω₀ R_eq / c_eff;  r_cov = |1-η|/(1+η)  (metric-corrected impedance)\n\n"
            "Transition-width correction (WP2D, VALIDATED):\n"
            "  Phi(t) = 1 - t^0.426 (power-law profile, Phase III-B calibrated)\n"
            "  Grading factor ≈ 0.996 (< 1% correction to sharp boundary)\n\n"
            "FIELD EQUATIONS (Phase III Final — scalarized first pass):\n"
            "  G_μν = (8πG/c⁴)(T_μν + T^Φ_μν)  [T^Φ schematic/effective]\n"
            "  τ_eff u^α ∇_α Φ + Φ = X[g, T]  (covariant memory relaxation)\n"
            "  ∇_μ(T^μν + T^Φ_μν) = 0  (combined conservation, fundamental)\n"
            "  Cosmo: Φ → M_X, X → H²_base, α → α_mem = 0.1\n"
            "  Collapse: Φ → M_drive, X → a_grav, α → α_vac = 1/3"
        ),
        "edition": 8,
        "tags": ["hole-sector", "phase-iii-c", "phase-iii-final", "ringdown", "echo", "falsifier", "frozen-candidate", "pde-revised", "mixed-viscoelastic", "covariant-confirmed", "field-equations"],
    },
]

try:
    db_store.seed_topics(DEFAULT_TOPICS)
    # Remove stale slugs that have been renamed/replaced
    _canonical_slugs = {t["slug"] for t in DEFAULT_TOPICS}
    _stale = [
        "nis-and-ris-certificates",   # replaced by nis-certificates
        "dissipation-d-and-eobs",     # replaced by dissipation-operator
        "s-phase-boethian-pivot",     # replaced by s-phase-state-preparation
    ]
    for _s in _stale:
        if _s not in _canonical_slugs:
            try:
                db_store._get_conn().execute("DELETE FROM topics WHERE slug = ?", (_s,))
            except Exception:
                pass
    db_store._get_conn().commit()
except Exception:
    # Non-fatal if seeding fails during certain test harnesses
    pass

app = FastAPI(title="GRUT-RAI v1.0 — Canonical Build (Phases I–III Complete)", version=params.engine_version)


@app.on_event("startup")
def _load_grut_phase2_engine() -> None:
    # Load .env for ANTHROPIC_API_KEY if present
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)
    except ImportError:
        pass
    # Reset AI client singleton so it picks up the newly-loaded env var
    import ai.client as _ai_mod
    _ai_mod._instance = None

    canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
    canon = GRUTCanon(str(canon_path))
    app.state.grut_engine = GRUTEngine(canon, determinism_mode="STRICT")
    app.state.rai_store = RAISessionStore()


def _get_rai_store() -> RAISessionStore:
    store = getattr(app.state, "rai_store", None)
    if store is None:
        store = RAISessionStore()
        app.state.rai_store = store
    return store


def _get_grut_engine() -> GRUTEngine:
    engine = getattr(app.state, "grut_engine", None)
    if engine is None:
        canon_path = Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json"
        canon = GRUTCanon(str(canon_path))
        engine = GRUTEngine(canon, determinism_mode="STRICT")
        app.state.grut_engine = engine
    return engine

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


INTENT_KEYWORDS = ["run", "simulate", "hz", "h(z)", "fs8", "pta", "probe", "canon", "certificate"]


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _default_monad_state(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "mode": "CANONICAL",
        "last_user_message": "",
        "last_assistant_message": "",
        "last_actions": [],
        "last_certificate_meta": {"canon_hash": "", "repro_hash": ""},
        "counters": {"messages": 0, "runs": 0},
        "flags": {"transient_warning_seen": False},
    }


def _determine_intent(message: str) -> tuple[str, dict]:
    msg = (message or "").strip()
    msg_lower = msg.lower()
    reasons: dict = {"matches": [], "starts_with_run": False}
    if msg_lower.startswith("/run"):
        reasons["starts_with_run"] = True
    matches = [kw for kw in INTENT_KEYWORDS if kw in msg_lower]
    reasons["matches"] = matches
    intent = "GRUT_RUN" if reasons["starts_with_run"] or matches else "CHAT_ONLY"
    return intent, reasons


@app.post("/rai/session/new", response_model=RaiSessionNewResponse, tags=["rai"])
def rai_new_session() -> RaiSessionNewResponse:
    store: RAISessionStore = _get_rai_store()
    session_id = store.new_session_id()
    state = _default_monad_state(session_id)
    store.upsert_session_state(session_id, state)
    store.append_event(session_id, "SESSION_CREATED", {"session_id": session_id, "ts_utc": _utc_now()})
    return RaiSessionNewResponse(session_id=session_id)


@app.get("/rai/session/{session_id}", response_model=RaiSessionDebugResponse, tags=["rai"])
def rai_get_session(session_id: str) -> RaiSessionDebugResponse:
    store: RAISessionStore = _get_rai_store()
    state = store.get_session_state(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")
    events = store.list_events(session_id, limit=50)
    return RaiSessionDebugResponse(session_id=session_id, state=state, events=events)


@app.post("/rai/chat", response_model=RaiChatResponse, tags=["rai"])
def rai_chat(req: RaiChatRequest) -> RaiChatResponse:
    rai_store: RAISessionStore = _get_rai_store()
    session_id = req.session_id or rai_store.new_session_id()
    state = rai_store.get_session_state(session_id)
    if state is None:
        state = _default_monad_state(session_id)
        rai_store.upsert_session_state(session_id, state)
        rai_store.append_event(session_id, "SESSION_CREATED", {"session_id": session_id, "ts_utc": _utc_now()})

    user_message = (req.message or "").strip()
    rai_store.append_event(
        session_id,
        "USER_MESSAGE",
        {"message": user_message, "mode": req.mode or state.get("mode"), "ts_utc": _utc_now()},
    )

    engine = _get_grut_engine()
    actions_taken = []
    grut_outputs = None
    nis_certificate = None
    assistant_message = ""

    # ── Use the AI orchestrator (tool-use loop) when Claude is available ──
    ai_client = get_ai_client()
    if ai_client.available:
        # Build conversation history from session events
        conversation_history = []
        events = rai_store.list_events(session_id, limit=40)
        for ev in events:
            if ev.get("event_type") == "USER_MESSAGE":
                conversation_history.append({"role": "user", "content": ev.get("data", {}).get("message", "")})
            elif ev.get("event_type") == "ASSISTANT_MESSAGE":
                conversation_history.append({"role": "assistant", "content": ev.get("data", {}).get("message", "")})

        # Resolve response mode: "forensic" enables JSON-only output
        response_mode = (req.mode or "standard").lower()
        if response_mode not in ("standard", "forensic"):
            response_mode = "standard"

        ai_result = ai_respond(
            user_message,
            conversation_history=conversation_history,
            grut_engine=engine,
            db_store=db_store,
            engine_version="grut-rai-v1.0",
            params_hash=engine.canon.canon_hash,
            response_mode=response_mode,
        )

        assistant_message = ai_result.text_markdown
        actions_taken = ["AI_TOOL_USE"]

        # Extract any certificate/output info from tool results
        for tr in ai_result.tool_results:
            result_data = tr.get("result", {})
            if "certificate" in result_data or "nis_certificate" in result_data:
                nis_certificate = result_data.get("nis_certificate") or result_data.get("certificate")
            if result_data.get("status") == "completed":
                grut_outputs = result_data

        if ai_result.certificate_summary:
            if nis_certificate is None:
                nis_certificate = ai_result.certificate_summary

        if ai_result.fallback_used:
            actions_taken = ["AI_FALLBACK"]

        rai_store.append_event(
            session_id,
            "AI_ORCHESTRATOR_RESPONSE",
            {
                "tools_called": [tr.get("tool") for tr in ai_result.tool_results],
                "fallback_used": ai_result.fallback_used,
                "nis_status": ai_result.nis_status,
                "ts_utc": _utc_now(),
            },
        )
    else:
        # ── Fallback: deterministic intent matching ──
        intent, reasons = _determine_intent(user_message)
        rai_store.append_event(
            session_id,
            "INTENT_DECISION",
            {"intent": intent, "reasons": reasons, "ts_utc": _utc_now()},
        )

        if intent == "CHAT_ONLY":
            assistant_message = (
                f"Received: \"{user_message}\". "
                "If you want a canon run, say 'run H(z)' and I will execute the Phase-2 engine."
            )
            actions_taken = ["CHAT_ONLY"]
        else:
            input_state = {
                "a": 1.0,
                "H": 1e-10,
                "rho": 1.0,
                "p": 0.0,
                "M_X": 0.0,
            }
            if req.input_state:
                input_state.update({k: float(v) for k, v in req.input_state.items()})

            numeric_policy = engine.canon.numeric_policy
            default_dt = float(numeric_policy.get("dt_years_default", 1e5))
            default_steps = int(min(200, numeric_policy.get("max_steps_default", 2000)))
            default_integrator = str(numeric_policy.get("integrator", "RK4"))
            run_config = {
                "dt_years": default_dt,
                "steps": default_steps,
                "integrator": default_integrator,
            }
            if req.run_config:
                run_config.update(req.run_config)
            assumptions = req.assumptions or {}

            rai_store.append_event(
                session_id,
                "GRUT_RUN_REQUESTED",
                {
                    "input_state": input_state,
                    "run_config": run_config,
                    "assumptions": assumptions,
                    "ts_utc": _utc_now(),
                },
            )

            outputs, cert = engine.run(input_state, run_config=run_config, assumption_toggles=assumptions)
            grut_outputs = outputs
            nis_certificate = cert

            canon_hash = cert.get("engine_signature", {}).get("canon_hash", "")
            repro_hash = cert.get("repro_hash", "")
            output_digest = cert.get("outputs", {}).get("output_digest")
            diagnostics = {
                "steps": cert.get("run_trace", {}).get("steps_computed"),
                "dt_years": cert.get("run_trace", {}).get("dt_years"),
                "integrator": cert.get("run_trace", {}).get("integrator"),
                "observables": cert.get("outputs", {}).get("observables_emitted"),
            }

            rai_store.append_event(
                session_id,
                "GRUT_RUN_COMPLETED",
                {
                    "canon_hash": canon_hash,
                    "repro_hash": repro_hash,
                    "output_digest": output_digest,
                    "diagnostics": diagnostics,
                    "ts_utc": _utc_now(),
                },
            )

            assistant_message = (
                "Phase-2 run completed with deterministic settings. "
                f"Integrator {diagnostics['integrator']} executed {diagnostics['steps']} steps at dt_years={diagnostics['dt_years']}. "
                f"Canon hash: {canon_hash}. Repro hash: {repro_hash}. "
                "Open the Show Logic panel for the full certificate."
            )
            actions_taken = ["GRUT_RUN"]

    rai_store.append_event(
        session_id,
        "ASSISTANT_MESSAGE",
        {"message": assistant_message[:500], "ts_utc": _utc_now()},
    )

    state.setdefault("counters", {"messages": 0, "runs": 0})
    state.setdefault("flags", {"transient_warning_seen": False})
    state.setdefault("last_certificate_meta", {"canon_hash": "", "repro_hash": ""})
    state["mode"] = req.mode or state.get("mode") or "CANONICAL"
    state["last_user_message"] = user_message
    state["last_assistant_message"] = assistant_message[:500]
    state["last_actions"] = actions_taken
    state["counters"]["messages"] = int(state.get("counters", {}).get("messages", 0)) + 1
    if nis_certificate:
        state["counters"]["runs"] = int(state.get("counters", {}).get("runs", 0)) + 1
        state["last_certificate_meta"] = {
            "canon_hash": (nis_certificate or {}).get("engine_signature", {}).get("canon_hash",
                          (nis_certificate or {}).get("canon_hash", "")),
            "repro_hash": (nis_certificate or {}).get("repro_hash", ""),
        }

    rai_store.upsert_session_state(session_id, state)

    return RaiChatResponse(
        session_id=session_id,
        assistant_message=assistant_message,
        actions_taken=actions_taken,
        grut_outputs=grut_outputs,
        nis_certificate=nis_certificate,
        monad_state=state,
        message=assistant_message,
        reply=assistant_message,
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
# Radial Collapse
# =========================

from pydantic import BaseModel as _BaseModel
from typing import Optional as _Optional, List as _List


class RadialCollapseRequest(_BaseModel):
    """Request for radial collapse experiment."""
    M_kg: float = 1e30
    R0_m: _Optional[float] = None
    R0_factor: float = 10.0
    tau0_s: float = 1.3225e15
    alpha_vac: float = 0.3333333333333333
    gamma_diss: float = 1e-15
    H_cap: float = 3.168808781402895e-02
    n_steps: int = 50000
    record_every: int = 10
    V_tol_frac: float = 1e-8
    R_min_frac: float = 1e-12
    mode: str = "single"
    M_min_kg: _Optional[float] = None
    M_max_kg: _Optional[float] = None
    n_masses: int = 10


@app.post("/experiments/radial_collapse", tags=["experiments"])
def radial_collapse(req: RadialCollapseRequest):
    """Radial collapse experiment with GRUT memory coupling.

    mode='single': Integrate one collapse trajectory.
    mode='mass_sweep': Sweep r_sat over a logarithmic mass range.
    """
    from grut.collapse import (
        compute_collapse,
        compute_mass_sweep,
        compute_schwarzschild_radius,
        fit_rsat_scaling,
        SEC_PER_YEAR,
    )

    try:
        if req.mode == "mass_sweep":
            if req.M_min_kg is None or req.M_max_kg is None:
                return JSONResponse(
                    status_code=400,
                    content={"error": "MISSING_PARAMS", "message": "mass_sweep requires M_min_kg and M_max_kg"},
                )
            rows = compute_mass_sweep(
                M_min_kg=req.M_min_kg,
                M_max_kg=req.M_max_kg,
                n_masses=req.n_masses,
                R0_factor=req.R0_factor,
                tau0_s=req.tau0_s,
                alpha_vac=req.alpha_vac,
                gamma_diss=req.gamma_diss,
                H_cap=req.H_cap,
                n_steps=req.n_steps,
            )
            # Extract slope if enough saturation points
            sat_rows = [r for r in rows if r.get("r_sat_m") is not None]
            slope = None
            if len(sat_rows) >= 2:
                import numpy as _np
                masses = _np.array([r["M_kg"] for r in sat_rows])
                r_sats = _np.array([r["r_sat_m"] for r in sat_rows])
                try:
                    slope, _ = fit_rsat_scaling(masses, r_sats)
                except Exception:
                    slope = None

            response = {
                "mode": "mass_sweep",
                "n_masses": len(rows),
                "n_saturated": len(sat_rows),
                "r_sat_slope": slope,
                "rows": rows,
                "inputs": req.model_dump(),
            }

            db_store.save_run(
                kind="radial_collapse_sweep",
                request=req.model_dump(),
                response=response,
                engine_version=params.engine_version,
                params_hash=params.params_hash(),
                status="COMPLETED",
                run_id=str(uuid.uuid4()),
            )
            return response

        else:
            # Single collapse
            R0 = req.R0_m
            if R0 is None:
                r_s = compute_schwarzschild_radius(req.M_kg)
                R0 = req.R0_factor * r_s

            result = compute_collapse(
                M_kg=req.M_kg,
                R0_m=R0,
                tau0_s=req.tau0_s,
                alpha_vac=req.alpha_vac,
                gamma_diss=req.gamma_diss,
                H_cap=req.H_cap,
                n_steps=req.n_steps,
                record_every=req.record_every,
                V_tol_frac=req.V_tol_frac,
                R_min_frac=req.R_min_frac,
            )

            response = {
                "mode": "single",
                "termination_reason": result.termination_reason,
                "r_sat_m": result.r_sat_m,
                "t_sat_s": result.t_sat_s,
                "r_sat_over_r_s": result.r_sat_over_r_s,
                "bounce_detected": result.bounce_detected,
                "K_at_sat": result.K_at_sat,
                "compactness_at_sat": result.compactness_at_sat,
                "trapped_at_sat": result.trapped_at_sat,
                "r_s_m": result.r_s_m,
                "t_ff_s": result.t_ff_s,
                "n_steps_taken": result.n_steps_taken,
                "l_stiff_activations": result.l_stiff_activations,
                "max_compactness": result.max_compactness,
                "n_ah_crossings": len(result.ah_crossings),
                "ah_crossings": [
                    {"t_s": t, "R_m": r, "direction": d}
                    for t, r, d in result.ah_crossings
                ],
                "trajectory_points": len(result.t_s),
                "inputs": result.inputs,
            }

            db_store.save_run(
                kind="radial_collapse",
                request=req.model_dump(),
                response=response,
                engine_version=params.engine_version,
                params_hash=params.params_hash(),
                status="COMPLETED",
                run_id=str(uuid.uuid4()),
            )
            return response

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "RADIAL_COLLAPSE_ERROR", "message": str(e)},
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


class LensingRunRequest(BaseModel):
    n: int = 256
    fov_arcmin: float = 20.0
    sigma_crit: float = 1.0
    mode: Literal["sigma_to_kappa", "phi_to_psi"] = "sigma_to_kappa"
    preset: Literal["single_halo", "bullet_toy"] = "single_halo"
    phi_preset: Literal["point_mass", "bullet_phi_toy", "from_npy"] = "bullet_phi_toy"
    phi_npy_path: Optional[str] = None
    A_psi: float = 1.0
    phi_mass_amp: float = 1e-6
    phi_gas_amp: float = 7e-7
    pad_factor: int = 1
    peak_mode: Literal["max_kappa", "smoothed_max_kappa", "com_positive_kappa"] = "max_kappa"
    smoothing_sigma_px: float = 0.0
    delta_arcmin: float = 2.0
    include_arrays: bool = False
    include_maps: bool = False


@app.post("/lensing/run", tags=["lensing"])
def run_lensing_packet(req: LensingRunRequest):
    config = {
        "n": int(req.n),
        "fov_arcmin": float(req.fov_arcmin),
        "sigma_crit": float(req.sigma_crit),
        "mode": req.mode,
        "preset": req.preset,
        "phi_preset": req.phi_preset,
        "phi_npy_path": req.phi_npy_path,
        "A_psi": float(req.A_psi),
        "phi_mass_amp": float(req.phi_mass_amp),
        "phi_gas_amp": float(req.phi_gas_amp),
        "pad_factor": int(req.pad_factor),
        "peak_mode": req.peak_mode,
        "smoothing_sigma_px": float(req.smoothing_sigma_px),
        "delta_arcmin": float(req.delta_arcmin),
    }
    result = run_lensing(config)
    response = {
        "summary": result.summary,
        "certificate": result.certificate,
    }
    include_arrays = bool(req.include_arrays or req.include_maps)
    if include_arrays:
        response["kappa"] = result.kappa.tolist()
        response["gamma1"] = result.gamma1.tolist()
        response["gamma2"] = result.gamma2.tolist()
        if result.psi is not None:
            response["psi"] = result.psi.tolist()
        if result.alpha_x is not None:
            response["alpha_x"] = result.alpha_x.tolist()
        if result.alpha_y is not None:
            response["alpha_y"] = result.alpha_y.tolist()
    return response


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


# =========================
# Responsive AI (Phase H)
# =========================

@app.get("/rai/status", response_model=RaiStatusResponse, tags=["rai"])
def rai_status() -> RaiStatusResponse:
    """Check whether the AI layer is available."""
    client = get_ai_client()
    engine = _get_grut_engine()
    return RaiStatusResponse(
        ai_available=client.available,
        model="claude-sonnet-4-20250514" if client.available else None,
        engine_version=params.engine_version,
        canon_hash=engine.canon.canon_hash,
    )


@app.post("/rai/ask", response_model=RaiAskResponse, tags=["rai"])
def rai_ask(req: RaiAskRequest) -> RaiAskResponse:
    """Unified Responsive AI chat endpoint.

    Accepts natural language, routes through the AI orchestrator (Claude
    with tool-use) or falls back to deterministic keyword matching.
    Physics numbers always come from the deterministic engine.
    """
    rai_store: RAISessionStore = _get_rai_store()

    # Session management
    session_id = req.session_id
    if not session_id:
        session_id = rai_store.new_session_id()
        state = _default_monad_state(session_id)
        rai_store.upsert_session_state(session_id, state)

    # Store user message
    rai_store.append_message(session_id, "user", req.message)

    # Get conversation history for context
    conversation = rai_store.get_conversation(session_id, limit=20)

    # Run AI orchestrator
    engine = _get_grut_engine()
    ai_result = ai_respond(
        req.message,
        conversation_history=conversation,
        grut_engine=engine,
        db_store=db_store,
        engine_version=params.engine_version,
        params_hash=params.params_hash(),
    )

    # Store assistant response
    rai_store.append_message(
        session_id,
        "assistant",
        ai_result.text_markdown,
        run_ids=ai_result.run_ids if ai_result.run_ids else None,
    )

    # Build response
    charts = [
        ChartData(type=c["type"], data=c["data"])
        for c in ai_result.charts
        if c.get("data")
    ]

    suggestions = [
        SuggestionItem(
            action=s.get("action"),
            label=s.get("label"),
            reason=s.get("reason"),
            description=s.get("description"),
            confidence=s.get("confidence"),
        )
        for s in ai_result.suggestions
    ]

    cert_summary = None
    if ai_result.certificate_summary:
        cert_summary = CertificateSummary(
            canon_hash=ai_result.certificate_summary.get("canon_hash"),
            repro_hash=ai_result.certificate_summary.get("repro_hash"),
            steps_computed=ai_result.certificate_summary.get("steps_computed"),
            integrator=ai_result.certificate_summary.get("integrator"),
            observables_emitted=ai_result.certificate_summary.get("observables_emitted"),
        )

    response_body = RaiAskResponseBody(
        text_markdown=ai_result.text_markdown,
        charts=charts,
        run_ids=ai_result.run_ids,
        nis_status=ai_result.nis_status,
        suggestions=suggestions,
        certificate_summary=cert_summary,
        fallback_used=ai_result.fallback_used,
    )

    return RaiAskResponse(
        session_id=session_id,
        response=response_body,
    )


@app.get("/rai/sessions", tags=["rai"])
def rai_list_sessions(limit: int = 20):
    """List recent RAI sessions."""
    rai_store: RAISessionStore = _get_rai_store()
    return {"sessions": rai_store.list_sessions(limit=limit)}


@app.get("/rai/session/{session_id}/history", tags=["rai"])
def rai_session_history(session_id: str, limit: int = 50):
    """Get full conversation history for a session."""
    rai_store: RAISessionStore = _get_rai_store()
    messages = rai_store.get_conversation(session_id, limit=limit)
    summary = rai_store.get_session_summary(session_id)
    return {"session_id": session_id, "messages": messages, "summary": summary}


@app.get("/runs/{run_id}/chart_data", tags=["library"])
def run_chart_data(run_id: str):
    """Extract chart-friendly arrays from a stored run."""
    run = db_store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    resp = run.get("response", {})
    hz_data = None
    fs8_data = None

    # Try to extract from OBS fields
    obs_hz = resp.get("OBS_HZ_001", {})
    obs_fs8 = resp.get("OBS_FS8_001", {})

    if obs_hz and "data" in obs_hz:
        points = obs_hz["data"]
        hz_data = {
            "z": [p.get("z", 0) for p in points],
            "H": [p.get("H", 0) for p in points],
        }

    if obs_fs8 and "data" in obs_fs8:
        points = obs_fs8["data"]
        fs8_data = {
            "z": [p.get("z", 0) for p in points],
            "fsigma8": [p.get("fsigma8") for p in points],
        }

    return {"run_id": run_id, "hz": hz_data, "fs8": fs8_data}


# =========================
# Generate (Phase H)
# =========================

@app.post("/generate/sweep", tags=["generate"])
def generate_sweep(req: GenerateSweepRequest):
    """Run a parameter sweep and return results.

    Wraps the existing sweep_cosmology tool for API access.
    """
    engine = _get_grut_engine()
    grid_values = [float(v.strip()) for v in req.grid.split(",") if v.strip()]

    results = []
    for i, alpha_mem_val in enumerate(grid_values):
        try:
            input_state = {"a": 1.0, "H": 1e-10, "rho": 0.2, "p": -0.2, "M_X": 0.0}
            if req.preset == "matter_only":
                input_state["p"] = 0.0
                input_state["rho_m"] = input_state["rho"]

            run_config = {
                "dt_years": req.dt_years,
                "steps": req.steps,
                "integrator": "RK4",
                "start_z": req.start_z,
            }
            assumptions = {"growth_enabled": True}

            # Use canon override for alpha_mem (engine.run doesn't accept overrides)
            from grut.canon_override import override_canon
            sweep_canon = override_canon(engine.canon, {"PARAM_ALPHA_MEM": alpha_mem_val})
            sweep_engine = GRUTEngine(sweep_canon, determinism_mode="STRICT")

            outputs, cert = sweep_engine.run(
                input_state,
                run_config=run_config,
                assumption_toggles=assumptions,
            )

            hz_data = outputs.get("OBS_HZ_001", {})
            fs8_data = outputs.get("OBS_FS8_001", {})

            results.append({
                "index": i,
                "alpha_mem": alpha_mem_val,
                "status": "completed",
                "canon_hash": cert.get("engine_signature", {}).get("canon_hash", ""),
                "repro_hash": cert.get("repro_hash", ""),
                "hz_points": len(hz_data.get("data", [])),
                "fs8_points": len(fs8_data.get("data", [])),
                "viability": outputs.get("viability", {}),
            })
        except Exception as exc:
            results.append({
                "index": i,
                "alpha_mem": alpha_mem_val,
                "status": "error",
                "error": str(exc),
            })

    return {
        "preset": req.preset,
        "grid": grid_values,
        "start_z": req.start_z,
        "dt_years": req.dt_years,
        "steps": req.steps,
        "results": results,
        "completed": sum(1 for r in results if r["status"] == "completed"),
        "total": len(results),
    }

