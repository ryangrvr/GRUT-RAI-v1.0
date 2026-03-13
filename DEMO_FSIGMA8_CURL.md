# Enhanced demo_fsigma8 Endpoint - Curl Examples

The `/anamnesis/demo_fsigma8` endpoint now supports flexible synthetic fsigma8 dataset generation for "First Light" calibration.

## Endpoint Overview

**URL:** `POST /anamnesis/demo_fsigma8`  
**Purpose:** Generate a deterministic memory-positive fsigma8 dataset with configurable parameters for instrument validation.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `planted_tau_myr` | float | 41.9 | Memory decay time to inject (Myr) |
| `dt_myr` | float | 5.0 | Internal resampling time step (Myr) |
| `span_myr` | float | 600.0 | Total time span over which to generate data (Myr) |
| `n_kernel` | int | 128 | Seth kernel length (samples) |
| `n_points` | int | 8 | Number of observed data points to sample |
| `seed` | int | 0 | RNG seed for reproducibility |
| `noise_std` | float | 0.0 | Gaussian noise amplitude (optional) |
| `include_series` | bool | true | Include high-resolution x_true and y_time series |

## Response

The endpoint returns a JSON object containing:

- **dataset**: Dictionary with keys `z` (redshifts), `fsigma8` (values), `sigma` (uncertainties), `dataset_label`
- **diagnostic**: Metadata including synthetic flag, planted tau, parameters, and ranges
- **planted_tau_myr**: The injected memory time (for validation)
- **dt_myr**: The resampling step used
- **span_myr**: The time span used
- **n_kernel**: Kernel size used
- **n_points**: Number of sampled points
- **x_true**: High-resolution source signal (if include_series=true)
- **y_time**: High-resolution smeared/convolved signal (if include_series=true)
- **run_id**: Unique identifier for this run (saved to vault)

## Example Curl Commands

### Basic Usage (Defaults)
```bash
curl -X POST http://localhost:8000/anamnesis/demo_fsigma8 \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Custom Parameters
```bash
curl -X POST http://localhost:8000/anamnesis/demo_fsigma8 \
  -H "Content-Type: application/json" \
  -d '{
    "planted_tau_myr": 41.9,
    "dt_myr": 5.0,
    "span_myr": 600.0,
    "n_kernel": 256,
    "n_points": 8,
    "noise_std": 0.0,
    "seed": 7
  }'
```

### High-Resolution Generation (More Points)
```bash
curl -X POST http://localhost:8000/anamnesis/demo_fsigma8 \
  -H "Content-Type: application/json" \
  -d '{
    "planted_tau_myr": 50.0,
    "dt_myr": 2.0,
    "span_myr": 800.0,
    "n_kernel": 512,
    "n_points": 20,
    "seed": 42
  }'
```

### With Noise
```bash
curl -X POST http://localhost:8000/anamnesis/demo_fsigma8 \
  -H "Content-Type: application/json" \
  -d '{
    "planted_tau_myr": 41.9,
    "dt_myr": 5.0,
    "span_myr": 600.0,
    "n_kernel": 256,
    "n_points": 8,
    "noise_std": 0.01,
    "seed": 7
  }'
```

### Without Series Data (Minimal Response)
```bash
curl -X POST http://localhost:8000/anamnesis/demo_fsigma8 \
  -H "Content-Type: application/json" \
  -d '{
    "planted_tau_myr": 41.9,
    "include_series": false
  }'
```

## Data Flow

1. **Generator** (`core/synthetic_fsigma8.py`):
   - Computes high-resolution grid: `n_resampled = ceil(span_myr / dt_myr)`
   - Plants three spikes (alternating signs) at fixed fractions of the time domain
   - Applies Seth kernel convolution with planted memory time
   - Optionally adds Gaussian noise
   - Normalizes to plausible fsigma8 range [0.41, 0.52]
   - Samples `n_points` observations by uniform redshift spacing

2. **Endpoint** (`api/main.py`):
   - Accepts flexible parameters
   - Calls generator
   - Returns dataset, diagnostics, and run metadata
   - Saves run to vault for traceability with kind `fsigma8_demo_synthetic`

3. **Validation**:
   - Search for planted τ in fsigma8 solver (`/anamnesis/search_tau_fsigma8`)
   - Verify recovery near planted value
   - Confirm baseline loses on memory-positive data

## Example Python Usage

```python
import requests
import json

url = "http://localhost:8000/anamnesis/demo_fsigma8"
payload = {
    "planted_tau_myr": 41.9,
    "dt_myr": 5.0,
    "span_myr": 600.0,
    "n_kernel": 256,
    "n_points": 8,
    "seed": 7
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Run ID: {data['run_id']}")
print(f"Dataset points: {len(data['dataset']['z'])}")
print(f"Planted tau: {data['planted_tau_myr']} Myr")
print(f"fsigma8 range: [{min(data['dataset']['fsigma8'])}, {max(data['dataset']['fsigma8'])}]")
```

## Integration with tau Search

After generating synthetic data, validate the memory signal by searching for τ:

```bash
# Extract dataset from demo_fsigma8 response, then search:
curl -X POST http://localhost:8000/anamnesis/search_tau_fsigma8 \
  -H "Content-Type: application/json" \
  -d '{
    "data": <dataset-from-demo>,
    "dt_myr": 5.0,
    "tau_candidates_myr": [10, 20, 30, 35, 40, 41.9, 45, 50, 60, 80],
    "n_kernel": 256,
    "prior": "smooth",
    "lam_smooth": 0.001,
    "nonnegative": true
  }'
```

**Note on Memory Recovery:** With small sample sizes (n_points ≤ 8), the search may not precisely recover the planted τ; instead, it identifies the best-fit τ within the candidate grid. Use larger `n_points` and denser tau grids for tighter recovery. The synthetic generator is primarily useful for verifying that the solver responds to memory-like signals, not for achieving perfect τ reconstruction.

## Notes

- The dataset is **synthetic** and designed for instrument calibration only, not physical evidence.
- Seeds ensure reproducibility; different seeds produce different jitter in spike amplitudes.
- The `span_myr` and `dt_myr` combination determines resolution: small `dt_myr` or large `span_myr` increases computation time.
- Runs are automatically saved to the vault with `kind="fsigma8_demo_synthetic"` for audit trail.
- Memory signal recovery is best achieved with 15+ data points and a fine tau candidate grid (e.g., 1-2 Myr spacing).
