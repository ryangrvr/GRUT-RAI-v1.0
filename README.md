# GRUT-RAI v1.0 — Canonical Build (Phases I–III Complete)

Phase I canon is frozen by the GRUT_v12 Closure Protocol (February 2026). All outputs are definition-only and reproducibility-first.

Canonical authority order and conflict policy: docs/reference_hierarchy.md

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


## Cosmology checklist (Phase E+)

- H(z) (Phase-2 kernel)
- fσ8(z) linear growth (kinematic baseline, Geff = G)
- Start redshift support via `run_config.start_z` (defaults to canon PARAM_Z_START)

Growth uses the GR background H(a) and integrates in ln a:

$$
D'' + \left[2 + \frac{d \ln H}{d \ln a}\right] D' - \frac{3}{2}\,\Omega_m(a)\,D = 0
$$

where $\Omega_m(a)=C_\rho\,\rho/H^2$. The output is normalized at the step closest to $z=0$.

Masking rule (emission-only): when emitting fσ8, if $H < 10^{-12}$ or $D \le 0$, the value is masked (`fsigma8 = null`) and `fs8_mask=true`. This does **not** change the physics state; it only affects output emission and robustness reporting.

Comparison window (survey-facing): summaries also include a deterministic compare mask:

- $z \in [0, z_\mathrm{start}]$
- $H > 10 \times H_\mathrm{floor}$
- `fsigma8` not null

Fields: `fs8_min_compare`, `fs8_max_compare`, `fs8_z0_compare`, `compare_point_count`, `compare_definition`.

Viability gate: any export or summary that relies on $H_0$ at $z\approx 0$ marks a run as `VIABLE` only if $H_0$ is finite and positive. Otherwise status is `NOT_VIABLE_AT_Z0` with a failure reason. This is a falsification signal, not a software error.

Domain-of-validity gate: presets can define `valid_z_max` for late-time-only models. If `start_z > valid_z_max`, status is `OUT_OF_DOMAIN_HIGH_Z` and compare metrics are restricted to $z \le \mathrm{valid\_z\_max}$.

## Portal UI (Phase F)

Run the server and open `http://127.0.0.1:8000/ui` for a minimal narrative-first chat UI that calls `/ask` and renders the expandable certificate.

## Example: /grut/run with growth (start_z=2)

```bash
curl -sS -X POST "http://127.0.0.1:8000/grut/run" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "input_state": {"rho": 0.2, "p": -0.2, "H": 1e-10, "M_X": 0.0},
    "run_config": {"dt_years": 100000, "steps": 500, "integrator": "RK4", "start_z": 2.0},
    "assumptions": {"growth_enabled": true}
  }' | python -m json.tool
```

This returns `OBS_HZ_001` and `OBS_FS8_001` when growth is enabled. Future work may add scale-dependent $G_\mathrm{eff}(k,a)$ or memory-drag corrections in the perturbation equation.

Growth uses a matter density source term `rho_m` (not the effective background fluid). You can pass `rho_m0` or `rho_m` in `input_state`. If omitted and the effective EOS is vacuum-like ($w\approx-1$), `rho_m0` defaults to 0, which suppresses growth as expected.

## Evidence Packet: Sensitivity Sweeps

Deterministic sweeps vary a single canon parameter and emit a reproducible evidence packet (CSV/JSONL + hashes).

```bash
python tools/sweep_cosmology.py \
  --param alpha_mem \
  --grid "0.0,0.1,0.333333333,0.5,1.0" \
  --start_z 2.0 \
  --rho0 0.2 \
  --p -0.2 \
  --dt_years 100000 \
  --steps 300 \
  --outdir artifacts/sweeps/alpha_mem_quick
```

Growth sensitivity sweep (explicit matter source):

```bash
python tools/sweep_cosmology.py \
  --param alpha_mem \
  --grid "0.0,0.1,0.333333333,0.5,1.0" \
  --start_z 2.0 \
  --rho0 0.2 \
  --p -0.2 \
  --rho_m0 0.05 \
  --dt_years 100000 \
  --steps 300 \
  --outdir artifacts/sweeps/alpha_mem_growth_quick
```

Matter-only baseline sweep (sanity check):

```bash
python tools/sweep_cosmology.py \
  --param alpha_mem \
  --grid "0.0,0.1,0.333333333,0.5,1.0" \
  --start_z 2.0 \
  --rho0 0.2 \
  --p 0.0 \
  --rho_m0 0.2 \
  --dt_years 100000 \
  --steps 300 \
  --outdir artifacts/sweeps/alpha_mem_matter_baseline
```

Preset shortcuts:

```bash
python tools/sweep_cosmology.py --preset vacuum_plus_matter --grid "0.0,0.1,0.333333333,0.5,1.0"
python tools/sweep_cosmology.py --preset matter_only --grid "0.0,0.1,0.333333333,0.5,1.0"
```

Preset definitions:
- `matter_only`: $\rho_0=\rho_{m,0}$, $p_0=0$.
- `vacuum_plus_matter`: explicit decomposition with $\rho_{vac,0}$ and $\rho_{m,0}$, $p_{vac,0}=-\rho_{vac,0}$, $p_{m,0}\approx 0$, so $\rho_{total,0}=\rho_{vac,0}+\rho_{m,0}$ and $p_{total,0}=p_{vac,0}$.
  A minimum threshold $\rho_{total,0} > -C_k K_0/C_\rho$ is computed and logged; defaults use a safety margin but can be overridden via CLI flags (no silent changes).

Artifacts produced:
- sweep_results.jsonl (one line per run)
- sweep_results.csv (same fields)
- manifest.json (sweep spec + run folders)
- run_<i>_<param>_<value>/certificate.json
- run_<i>_<param>_<value>/outputs.json
- run_<i>_<param>_<value>/summary.json

To cite a sweep point, include `canon_hash`, `repro_hash`, and `output_digest` from the per-run summary.

RMS definition (sweep summaries):

$$
\mathrm{RMS}(x) = \sqrt{\frac{1}{N}\sum_{i=1}^{N}(x_i - x^{\mathrm{baseline}}_i)^2}
$$

For $H$, $N$ is the number of aligned steps. For fσ8, $N$ counts only aligned points where **both** baseline and run are unmasked and `fsigma8` is not null. The summary includes `rms_definition` and `rms_n_points`.

## How to reproduce the Phase-2 cosmology evidence packet

Run the following commands in order:

```bash
python tools/sweep_cosmology.py \
  --preset matter_only \
  --grid "0.333333333" \
  --start_z 2.0 \
  --dt_years 100000 \
  --steps 300 \
  --outdir artifacts/sweeps/phase2_matter_only

python tools/calibrate_and_export.py \
  --preset matter_only \
  --alpha_mem 0.333333333 \
  --start_z 2.0 \
  --dt_years 100000 \
  --steps 300 \
  --outdir artifacts/calibration

python tools/quantum_boundary_test.py \
  --preset optomech_micro \
  --tau0_s 41900000 \
  --omega_policy controlled \
  --outdir artifacts/quantum_boundary

python tools/build_evidence_packet.py \
  --calibration_dir artifacts/calibration \
  --sweep_dir artifacts/sweeps/phase2_matter_only \
  --quantum_boundary_dir artifacts/quantum_boundary \
  --outdir artifacts/evidence_packet_phase2_cosmo_v0

python tools/summarize_evidence_packet.py \
  --packet artifacts/evidence_packet_phase2_cosmo_v0/phase2_evidence_packet.json \
  --outdir artifacts/evidence_packet_phase2_cosmo_v0
```

Baseline vs derived:
- Baseline inputs: $H_0$ (anchor choice), $\sigma_{8,0}$ (baseline amplitude)
- Derived outputs: $\tau_0$-linked timing, $E(z)$, anchored $H(z)$, fσ8(z)

Tier A vs Tier B:
- Tier A (operational, falsifiable): Phase-2 cosmology runs + conversions, Quantum Boundary Test, controlled-ω oracle, self-consistent closure, slope falsifier
- Tier B (derivation-only): 3-loop residue / r_sat numeric values and higher-loop corrections

Explicit: $\sigma_{8,0}$ is baseline-tagged; $\tau_0$ is derived from the baseline chain.

## Quantum Boundary Test (Tier A)

Standalone, falsifiable decoherence bound test with NIS-style hashing. The primary mode uses a controlled experimental $\omega_{exp}$; the self-consistent mode is a mock closure for comparison only.

Definition of $\omega_{exp}$ (choose the most appropriate experimental control):
- trap frequency
- pulse repetition frequency
- interferometer sequence frequency

Controlled policy (primary):

```bash
python tools/quantum_boundary_test.py \
  --m_kg 1.0 \
  --l_m 1.0 \
  --tau0_s 41900000 \
  --omega_policy controlled \
  --omega_exp 1000.0 \
  --outdir artifacts/quantum_boundary
```

Self-consistent mock (secondary):

```bash
python tools/quantum_boundary_test.py \
  --m_kg 1.0 \
  --l_m 1.0 \
  --tau0_s 41900000 \
  --omega_policy self_consistent \
  --outdir artifacts/quantum_boundary_mock
```

Artifacts written per run:
- quantum_boundary_packet.json
- quantum_boundary_packet.sha256
- quantum_boundary_table.csv

## Quantum Evidence Packet v0.1

Reproducible, Zenodo-ready packet for the $m^{-2/3}$ bridge with explicit slope falsifier and controlled-vs-self-consistent policy split. Tier A only.

```bash
python tools/build_quantum_evidence_packet.py \
  --outdir artifacts/evidence_quantum_v0_1
```

Outputs:
- README_DATA.md
- PACKET_INDEX.json
- benchmarks/benchmark_controlled.json
- benchmarks/benchmark_self_consistent.json
- scans/scan_omega_controlled.csv
- scans/scan_mass_controlled.csv
- scans/scan_mass_self_consistent.csv
- summary.csv (slopes + benchmarks)
- nis_quantum_certificate.json
- file_hashes.json

## Hubble Tension Evidence Packet v0.2.4

Tier A evidence packet comparing GRUT $E(z)$ shape outputs to a fixed ΛCDM reference and to an offline H(z) compilation. Anchor policies are explicit (Planck-like vs SH0ES-like); no fitting or tuning is performed. Includes tracer-split residuals, shape-only $E(z)$ residuals, and dataset curation policies.

```bash
python tools/build_hubble_tension_packet.py \
  --outdir artifacts/evidence_hubble_tension_v0_2_4
```

Notes:
- ΛCDM reference parameters are fixed (Ωm=0.315, ΩΛ=0.685, Ωk=0, Ωr=0).
- GRUT parameters are not fit or tuned in this packet.
- Outputs are residuals only; no Tier B claims.

## Rotation Curve Packet v0.1

Deterministic baryons → baseline → GRUT response → residual metrics pipeline. No hidden fitting or optimization; all policy choices are logged.

Single galaxy:

```bash
python tools/run_rotation_packet.py \
  --data_path path/to/galaxy.csv \
  --response_model radial_gate_v0 \
  --alpha_mem 0.333333333 \
  --r0_policy median_radius \
  --outdir artifacts/rotation_packet_v0_1
```

Batch:

```bash
python tools/run_rotation_batch.py \
  --datadir path/to/galaxies \
  --glob "*.csv" \
  --response_model radial_gate_v0 \
  --alpha_mem 0.333333333 \
  --r0_policy median_radius \
  --outdir artifacts/rotation_batch_v0_1
```

Outputs per galaxy:
- curves.csv
- metrics.json
- nis_rotation_certificate.json

Batch outputs:
- summary.csv
- batch_manifest.json

## Lensing/Cluster Packet v0.1

Deterministic weak-lensing mapmaking from a surface density map $\Sigma(x,y)$. Produces $\kappa$, $\gamma_1$, $\gamma_2$ and centroid offsets for toy presets. This is a **pipeline plumbing** checkpoint; it makes no DM/modified-gravity claims.

Example run (bullet-style toy):

```bash
python tools/run_lensing_packet.py \
  --n 256 \
  --fov_arcmin 20 \
  --sigma_crit 1.0 \
  --preset bullet_toy \
  --delta_arcmin 2.0 \
  --outdir artifacts/lensing_packet_v0_1
```

Outputs:
- kappa.npy, gamma1.npy, gamma2.npy
- summary.json (peaks, offsets, basic stats)
- nis_lensing_certificate.json (hashes + determinism)

## Lensing v0.2 (Φ_eff→ψ→α, κ, γ)

Pipeline primitive that derives deflection and shear from an effective potential field. The thin-lens prefactor is carried explicitly as `A_psi` and must not be fit per cluster in Tier A.

Example run (potential-to-lensing):

```bash
python tools/run_lensing_packet.py \
  --mode phi_to_psi \
  --phi_preset bullet_phi_toy \
  --A_psi 1.0 \
  --phi_mass_amp 1e-6 \
  --phi_gas_amp 7e-7 \
  --pad_factor 2 \
  --n 256 \
  --fov_arcmin 20 \
  --delta_arcmin 2.0 \
  --outdir artifacts/lensing_packet_v0_2
```

Notes:
- `A_psi` encapsulates the line-of-sight integral and distance prefactor; it is reported in the certificate.
- `bullet_phi_toy` is a pipeline validation field, not a physical mass model.
- `pad_factor` applies zero-padding before FFT derivatives to reduce periodic edge artifacts (cropped back to the original grid).

## Cluster Packet v0.3

Operational centroid robustness for real maps. Ingests kappa and gas proxy maps, sweeps smoothing/threshold choices, and reports an offset distribution.

Example run with .npy inputs:

```bash
python tools/run_cluster_packet.py \
  --kappa_path path/to/kappa.npy \
  --gas_path path/to/gas.npy \
  --smoothing_grid "0,1,2,3" \
  --threshold_grid "0.05,0.1,0.2" \
  --peak_mode com_positive_kappa \
  --gas_centroid_mode peak \
  --pixel_scale_arcsec 1.0 \
  --outdir artifacts/cluster_packet_v0_3
```

Outputs:
- centroids_summary.json (robust offset stats)
- offsets.csv (offset per smoothing/threshold)
- nis_cluster_certificate.json (hashes + config)

## Cluster Gas Offset Packet v0.1

Deterministic lensing-vs-gas offset packet. Produces observed offsets across a robustness grid and optional prediction comparison via $\delta_{pred} = v_{coll}\,\tau_0$ when velocity is supplied. This is a falsifier packet, not a blanket proof of collisionless-dark-matter mimicry.

Example (observed offsets only):

```bash
python tools/run_cluster_offset_packet.py \
  --kappa_path path/to/kappa.npy \
  --gas_path path/to/gas_registered.npy \
  --pixel_scale_arcsec 1.0 \
  --smoothing_grid "0,1,2" \
  --threshold_grid "0.05,0.1" \
  --outdir artifacts/cluster_offset_packet_v0_1
```

Example (with prediction):

```bash
python tools/run_cluster_offset_packet.py \
  --kappa_path path/to/kappa.npy \
  --gas_path path/to/gas_registered.npy \
  --pixel_scale_arcsec 1.0 \
  --v_coll_kms 3000 \
  --tau0_s 1.3225e15 \
  --kpc_per_arcsec 5.3 \
  --outdir artifacts/cluster_offset_packet_v0_1
```

Notes:
- No hidden fitting or optimization.
- Physical conversion requires explicit `kpc_per_arcsec`.
- NaN fractions are logged; NaNs are zero-filled deterministically.

## Particle Bridge Spec v0.1

Tier B specification document defining the particle-sector bridge. It is **not** an operational Tier A packet and does not add Tier A observables. See docs/particle_bridge_spec_v0_1.md.

## Cluster Prediction v0.4A (scaffold)

Prediction-side bridge from baryons to lensing maps. This is a **deterministic integration stub**; the kernel/response are placeholders that make the mapping explicit and swappable.

Flow:
1. $\Sigma_b \rightarrow \Phi_b$ via explicit FFT kernel (`k1` or `k2`)
2. $\Phi_b \rightarrow \Phi_{eff}$ via response model (`identity`, `scaled`, `band_gate`)
3. $\Phi_{eff} \rightarrow \psi \rightarrow \alpha/\kappa/\gamma$ (v0.2)
4. Centroid robustness sweep on predicted $\kappa$ (v0.3)

Example run:

```bash
python tools/run_cluster_prediction.py \
  --sigma_baryon_path path/to/sigma_baryon.npy \
  --gas_path path/to/gas.npy \
  --kernel k1 \
  --response_model identity \
  --alpha_mem 0.333333333 \
  --A_psi 1.0 \
  --fov_arcmin 20 \
  --smoothing_grid "0,1,2" \
  --threshold_grid "0.0,0.1" \
  --peak_mode com_positive_kappa \
  --gas_centroid_mode com_positive \
  --pixel_scale_arcsec 1.0 \
  --outdir artifacts/cluster_prediction_v0_4A
```

Outputs:
- phi_b.npy, phi_eff.npy, psi.npy
- alpha_x.npy, alpha_y.npy, kappa.npy, gamma1.npy, gamma2.npy
- centroids_summary.json + offsets.csv
- nis_prediction_certificate.json

Notes:
- This scaffold is **deterministic plumbing**, not a final GRUT lensing claim.
- The kernel and response model are logged in the summary and certificate for NIS traceability.

## Cluster Prediction v0.4B (shape response)

First non-placeholder GRUT response as a k-space transfer function that changes shape without introducing a global multiplier fit per cluster.

Response model: `grut_gate_kspace_v0`

$$
\Phi_{\mathrm{eff}}(k)=\Phi_b(k)\,T(k),\quad
T(k)=1+\frac{\alpha_{\mathrm{mem}}}{1+(k/k_0)^2}
$$

Policies for $k_0$ (deterministic, logged):
- `k0_policy="r_smooth"`: $k_0=1/r_{\mathrm{smooth}}$ with $r_{\mathrm{smooth}}=\sigma_{\mathrm{smooth}}\times$ pixel scale.
- `k0_policy="fov"`: $k_0=2\pi/L$ where $L$ is the map FOV in radians.

Example run with baseline comparison:

```bash
python tools/run_cluster_prediction.py \
  --sigma_baryon_path path/to/sigma_baryon.npy \
  --gas_path path/to/gas.npy \
  --kernel k2 \
  --response_model grut_gate_kspace_v0 \
  --k0_policy fov \
  --alpha_mem 0.333333333 \
  --compare_to_baseline \
  --outdir artifacts/cluster_prediction_v0_4B
```

Comparison outputs (shape metrics):
- centroid_shift_arcsec
- rms_kappa_diff
- corr_kappa (Pearson)

## Cluster Profile Falsifier Packet v0.5

Profile-level comparison for $\kappa(r)$ and $\gamma_t(r)$, designed to test shape changes even when centroids are unchanged.

Example run (observed kappa + model comparison):

```bash
python tools/run_cluster_profile_packet.py \
  --kappa_path path/to/kappa.npy \
  --sigma_baryon_path path/to/sigma_baryon.npy \
  --compare_to_model \
  --model_response grut_gate_kspace_v0 \
  --k0_policy r_smooth \
  --profile_bins 20 \
  --pixel_scale_arcsec 1.0 \
  --fov_arcmin 20 \
  --outdir artifacts/cluster_profile_v0_5
```

Outputs:
- profiles.csv (radial profiles and ratios)
- profile_metrics.json (rms/max profile differences)
- nis_profile_certificate.json (hashes + determinism)

## v0.6A Real Cluster Evidence Packet (HFF lens models)

Deterministic ingestion of public Hubble Frontier Fields lens-model FITS maps (\$\kappa,\gamma\$), conversion to numpy, and v0.5 profile-falsifier outputs in a Zenodo-ready packet structure. **No fitting**.

Fetch (network):

```bash
python tools/fetch_hff_lensmodel.py --cluster A2744 --model CATS
```

Build packet (offline if raw already present):

```bash
python tools/build_cluster_evidence_packet.py --cluster A2744 --model CATS
```

Packet outputs:
- raw/ (downloaded FITS + PROVENANCE.json)
- processed/ (kappa.npy, gamma1.npy, gamma2.npy, WCS.json)
- outputs/profile_packet/ (v0.5 profile packet)
- PACKET_INDEX.json + README_DATA.md

## v0.6B Gas proxy ingestion + WCS alignment

Registers a user-provided X-ray gas proxy FITS onto the lensing \$\kappa\$ grid (WCS reprojection), then runs the centroid robustness sweep and emits gas-vs-lensing offsets.

Register gas to kappa:

```bash
python tools/register_gas_to_kappa.py \
  --kappa_fits_path path/to/kappa.fits \
  --gas_fits_path path/to/gas.fits \
  --outdir artifacts/gas_registered/A2744
```

Build packet with gas:

```bash
python tools/build_cluster_evidence_packet.py \
  --cluster A2744 \
  --model CATS \
  --gas_fits_path path/to/gas.fits
```

Outputs include:
- outputs/gas_offset_packet/offsets.csv
- outputs/gas_offset_packet/centroids_summary.json
- outputs/gas_offset_packet/nis_cluster_certificate.json
- outputs/gas_offset_packet/registration_report.json

## Rotation Curve Packet v0.1

Deterministic baryonic rotation-curve packet: compute baseline baryonic curve, apply GRUT response, and emit residual metrics.

Example run:

```bash
python tools/run_rotation_packet.py \
  --data_path path/to/galaxy.csv \
  --response_model radial_gate_v0 \
  --alpha_mem 0.333333333 \
  --outdir artifacts/rotation_packet_v0_1
```

Batch run:

```bash
python tools/run_rotation_batch.py \
  --data_dir path/to/rotation_data \
  --response_model memory_scale_boost_v0 \
  --alpha_mem 0.333333333
```

Outputs per galaxy:
- curves.csv
- metrics.json
- nis_rotation_certificate.json

Preset scenarios (placeholders, override as needed):
- `optomech_micro`: $m=10^{-9}$ kg, $\ell=10^{-6}$ m, $\omega=10^5$ s$^{-1}$
- `optomech_nano`: $m=10^{-15}$ kg, $\ell=10^{-7}$ m, $\omega=10^6$ s$^{-1}$
- `atom_interfer`: $m=10^{-25}$ kg, $\ell=10^{-6}$ m, $\omega=10^3$ s$^{-1}$

Example scan (boundary curve):

```bash
python tools/quantum_boundary_test.py \
  --preset optomech_micro \
  --tau0_s 41900000 \
  --omega_policy controlled \
  --scan_omega_min 1e2 \
  --scan_omega_max 1e6 \
  --scan_points 25 \
  --outdir artifacts/quantum_boundary_scan
```

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
# run E2E tests (opt-in)
RUN_E2E=1 pytest -q tests/e2e
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

