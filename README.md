# GRUT-RAI Sovereign Engine (Phase E)

Phase I canon is frozen by the GRUT_v12 Closure Protocol (February 2026). All outputs are definition-only and reproducibility-first.

Phase E hardens the Phase C stack with better defaults + guardrails and an **optional** observer→dissipation coupling.

## What Phase E Adds
- Observer profiles: **Monk / Astronomer / Participant**
- Hybrid engagement flux: **ΔS = w1*UI_entropy + w2*Sensor_flux**
- Information density: **I(t)** (bounded, auditable)
- Determination strength: **P_lock**
- Metric tension meter + metabolic state labels
- Sensor snapshot hashing (for reproducibility) and explicit warnings
- Optional observer→dissipation modulation (enabled per-request)

Phase E also adds:
- **Observer modulation toggle** (optional): when enabled, ΔS scales dissipation D(z) by a bounded factor.
- Better defaults when `rho_grid` is omitted (no accidental "cap to 1" behavior).
- Smoother NIS warnings (only evaluate pivot smoothness on sufficiently dense z-grids).

### Important Principle
By default, observer-layer metrics do **not** change cosmology outputs. They are reported in the NIS certificate and the expandable observer panel.

If you set `observer.enable_observer_modulation=true` (and you're not in Monk mode), Phase E will scale **D(z)** by a bounded factor derived from ΔS.
If you set `enable_observer_modulation=true`, the engine still keeps the **same gain + tau_eff** outputs; only the **dissipation operator** D(z) is scaled.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Then open:
- http://127.0.0.1:8000/docs

## Example /runs payload (Participant)

```json
{
  "engine": {
    "z_grid": [0.0, 0.5, 1.0, 2.0],
    "eps_t_myr": 0.10
  },
  "observer": {
    "profile": "participant",
    "v_obs_m_s": 200000,
    "ui_window": {"ui_actions": 12, "window_s": 20, "avg_param_delta": 0.4},
    "sensor": {"mode": "ambient", "ambient_flux": 0.03},
    "info_cfg": {"eta": 1.0}
  }
}
```

## Notes
- `numpy` is specified as `>=1.26.4,<3.0` for broad compatibility.
- Sensor modes are v1 stubs: `off`, `ambient`, `snapshot` (no external fetches yet).
- For convenience, the API also accepts legacy forms like `mode: "recorded"` and a `sensor.snapshot` object.

## /ask (Portal)

`/ask` returns a narrative-first answer plus an expandable bundle containing engine outputs and the NIS certificate.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/ask"   -H "accept: application/json"   -H "Content-Type: application/json"   -d '{
    "prompt": "why is the answer 42?",
    "run": {
      "engine": { "z_grid": [0.0, 0.5, 1.0, 2.0], "eps_t_myr": 0.10 },
      "observer": {
        "profile": "participant",
        "v_obs_m_s": 200000,
        "ui_window": { "ui_actions": 60, "window_s": 10, "avg_param_delta": 0.9 },
        "sensor": { "mode": "recorded", "snapshot": { "ambient_flux": 0.03 } },
        "info_cfg": { "eta": 1.0 },
        "enable_observer_modulation": true
      }
    }
  }'
```

The response always includes:
- `answer.text_markdown` (narrative-first)
- `expandable.sections[]` with **Engine outputs**, **Observer layer**, and **NIS certificate**


## Portal UI (Phase F)

Run the server and open `http://127.0.0.1:8000/ui` for a minimal narrative-first chat UI that calls `/ask` and renders the expandable certificate.

## E2E UI tests (Playwright) — dev-only

E2E UI tests are optional and intentionally kept as a development-only dependency to keep runtime installs lightweight.

To run them locally:

```bash
# activate your virtualenv
. .venv/bin/activate
# install runtime deps
pip install -r requirements.txt
# install dev-only deps
pip install -r requirements-dev.txt
# install Playwright browsers
python -m playwright install --with-deps
# run unit tests
pytest -q
# run E2E tests
pytest -q tests/e2e
```

CI: The GitHub Actions `e2e` workflow installs `requirements-dev.txt` and runs the E2E suite in a headless environment (Playwright browsers are installed in the workflow).
## Anamnesis (Reconstruction Lens)

Phase G introduces an **inverse-problem pipeline** inspired by a rotating scatter-mask workflow:

- **simulator.py** (Forward model / DRM): smears a sparse source with a causal kernel
- **reconstructor.py** (Inverse / LCA): sparse reconstruction via Locally Competitive Algorithm
- **evaluator.py** (Judge / EMD): Earth Mover's Distance + basic fit metrics + RIS report

### Endpoints

#### POST `/anamnesis/demo`
Generates a toy "past" (sparse spikes), smears it, reconstructs it, and returns arrays + a `RIS` report.

#### POST `/anamnesis/reconstruct`
Accepts an observed 1D signal + a kernel specification and returns a reconstructed source plus a `RIS` report.

#### POST `/anamnesis/search_tau`
Simple grid search over candidate `tau_s` values (demo-oriented) and reports the best `tau_s` by EMD.

### Demo script

```bash
python scripts/demo_anamnesis.py
```

This prints a compact "first light" summary and can be the seed for a future UI view.

## Experiments

### Zeta–Tau Scaling

Pre-registered experiment testing whether τ₀ ≈ 41.9 Myr aligns with Riemann zeta zero ordinates under dimensionally-honest cosmological mappings.

**Run the experiment:**

```bash
curl -sS -X POST "http://127.0.0.1:8000/experiments/zeta_tau_scaling" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "tau0_myr": 41.9,
    "H0_km_s_Mpc": 67.4,
    "zeros_n": 30,
    "eps_hit": 0.01,
    "null_trials": 500,
    "h0_perturb_frac": 0.02,
    "seed": 7,
    "Omega_m": 0.315
  }' | python -m json.tool
```

The response includes:
- `status`: `PASS`, `WARN`, or `FAIL` (gates: rel_err ≤ eps_hit, p_value ≤ 0.05, H0 robustness)
- `best_match`: matching formula, indices, predicted τ, relative error
- `robustness`: results under H0 ± perturbation
- `null_model`: p-value from 500 null trials (anti-numerology)
- `tested_counts`: number of zeta zeros and hypotheses tested
- `run_id`: persisted to vault

**Publish the result:**

```bash
RUN_ID="<copy-run_id-from-response>"
curl -sS -X POST "http://127.0.0.1:8000/runs/$RUN_ID/publish" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" | python -m json.tool
```

This generates a unique slug; you can then view it:

```bash
SLUG="<copy-slug-from-publish-response>"
curl -sS "http://127.0.0.1:8000/p/$SLUG" | python -m json.tool
```

**Important note**: The zeta-tau scaling experiment tests scaling hypotheses under pre-registered mappings. A `PASS` status means the observed alignment is statistically unlikely under uniform random hypotheses, **not** a claim of mathematical proof for the Riemann Hypothesis. See GRUTipedia topic: `zeta-operator` for integrity notes.

### Casimir Density Sweep

Instrument-grade sweep reporting screening consistency under Phase I canon.
Definitions only: $\alpha_{vac}=1/3$ with screening $S=108\pi$ and refractive index $n_g(0)=\sqrt{1+\alpha_{vac}}=2/\sqrt{3}$.
H0 is baseline-defined ($\tau_\Lambda=H_0^{-1}$); any inversion using $\tau_0=\tau_\Lambda/S$ is an internal consistency check only.

**Run the experiment:**

```bash
curl -sS -X POST "http://127.0.0.1:8000/experiments/casimir_density_sweep" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "tau0_myr": 41.9,
    "H0_km_s_Mpc": 67.36,
    "Omega_lambda": 0.6847,
    "h0_min": 67.0,
    "h0_max": 74.0,
    "h0_step": 0.1,
    "omegaL_min": 0.675,
    "omegaL_max": 0.695,
    "omegaL_step": 0.002,
    "alpha_vac": 0.3333333333333333,
    "seed": 7
  }' | python -m json.tool
```

The response includes:
- `computed`: rho_crit, rho_Lambda, rho_req, R_obs, tau_lambda_s, tau_lambda_gyr, S_thy, rel_err_S
- `rel_err_S_vs_H0`: min rel_err_S after marginalizing $\Omega_\Lambda$
- `two_loop_argmin`: argmin (H0, ΩΛ, rel_err_S, τΛ_gyr, τ0_myr)
- `metadata`: baseline note + velocity-vs-potential note + $n_g(0)$ definition
- `nis`: determinism stamp, unit consistency, fuzz_fraction, provenance
- `run_id`: persisted to vault

### PTA Dispersion Probe (Falsification Test)

Black-box, definition-only probe for PTA-band dispersion under the forced assumption that $n_g(\omega)$ maps to GW propagation.

**PTA phase-speed gate (like-for-like):** Applies the NANOGrav 15-year PTA lower bound on GW phase speed ($v_{\rm phase}/c \ge 0.87$) as the primary gate over the PTA band.

**MG proxy (secondary):** Also reports the magnitude-mapped graviton-mass proxy as a secondary diagnostic. When predictions are superluminal, the MG mapping is labeled *magnitude_proxy_only* and never treated as a like-for-like exclusion.

If GRUT defines $n_g(\omega)$ as a field-response index only, set `apply_to_gw_propagation=false` and the status will be `NOT_APPLICABLE`.

**Run the experiment:**

```bash
curl -sS -X POST "http://127.0.0.1:8000/experiments/pta_dispersion_probe" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "tau0_myr": 41.92,
    "alpha_scr": 0.3333333333333333,
    "freqs_hz": [1e-9, 1e-8, 1e-7],
    "use_group_velocity": true,
    "apply_to_gw_propagation": true,
    "seed": 7
  }'
```

The response includes:
- `results`: per-frequency $n_g^2(\omega)$, $n(\omega)$, $v_p/c$, $v_g/c$, and delay per Mpc
- `comparisons`: per-frequency delta_v and graviton-mass proxy comparison
- `hf_check_100Hz`: HF sanity check at 100 Hz
- `cited_limits`: published constraints used as hard gates
- `status`: PASS_NOT_EXCLUDED / EXCLUDED_BY_PTA_SPEED / FAIL_HF_SANITY / EXCLUDED_BY_PTA_MG_PROXY / NOT_APPLICABLE
- `pta_direct_dispersion_bound_present`: whether a like-for-like PTA dispersion bound was applied
- `exclusion_basis`: disclosure for primary/secondary gate (e.g., PTA_SPEED_GATE_PRIMARY or MG_PROXY_ONLY)
- `worst_margin_over_band`: min( mg_limit_eV / mg_equiv_abs_eV ) across requested frequencies
- `min_v_phase_over_c_over_band`, `worst_speed_margin_over_band`, `worst_freq_hz`: PTA phase-speed gate diagnostics
- `conclusion`: forced-interpretation disclaimer

**Publish the result:**

```bash
RUN_ID="<copy-run_id-from-response>"
curl -sS -X POST "http://127.0.0.1:8000/runs/$RUN_ID/publish" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" | python -m json.tool
```

**Integrity note**: PASS indicates a stable numerical correspondence under declared model assumptions; it does **not** establish mechanism.

**NIS fields**: determinism_stamp (SHA-256 of inputs + code_version + seed), unit_consistency, fuzz_fraction, provenance, and environment metadata.

