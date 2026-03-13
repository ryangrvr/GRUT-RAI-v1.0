import numpy as np
from core.reconstruction.simulator import exponential_kernel, build_drm_matrix, KernelSpec, make_seth_kernel
from fastapi.testclient import TestClient
from api.main import app


def test_drm_convolution_adjoint():
    """Verify forward convolution matrix A and its transpose satisfy the adjoint property: <A x, r> == <x, A^T r>."""
    n = 64
    spec = KernelSpec(tau_s=10.0, dt_s=1.0, length=16)
    k = exponential_kernel(spec)
    A = build_drm_matrix(k, n)

    # Seth alias should produce same kernel
    k_seth = make_seth_kernel(dt_s=spec.dt_s, tau_s=spec.tau_s, n_kernel=spec.length)
    assert np.allclose(k, k_seth, atol=1e-12)

    rng = np.random.default_rng(123)
    x = rng.normal(size=n)
    r = rng.normal(size=n)

    lhs = float(r @ (A @ x))
    rhs = float((A.T @ r) @ x)

    # Use a relative tolerance scaled by magnitudes
    scale = max(1.0, abs(lhs), abs(rhs))
    assert abs(lhs - rhs) <= 1e-10 * scale, f"Adjoint check failed: lhs={lhs}, rhs={rhs}"


def test_demo_recovery_deterministic_and_min_iter():
    """Ensure the demo is deterministic for a fixed seed, recovers spikes (recall>=0.5 within ±2),
    and does not converge in fewer than min_iters (25). Also validate iter_trace keys."""
    client = TestClient(app)
    payload = {
        "n": 256,
        "dt_s": 1.0,
        "tau_s": 30.0,
        "n_kernel": 128,
        "spikes": [{"index": 40, "amplitude": 1.0}, {"index": 150, "amplitude": 0.7}],
        "noise_std": 0.0,
        "lam": 0.01,
        "max_iter": 4000,
        "seed": 42,
    }

    r1 = client.post("/anamnesis/demo", json=payload)
    r2 = client.post("/anamnesis/demo", json=payload)
    assert r1.status_code == 200 and r2.status_code == 200
    j1 = r1.json()
    j2 = r2.json()

    # Deterministic: reconstructed_source and diagnostics should match exactly for same seed
    assert j1["reconstructed_source"] == j2["reconstructed_source"]
    assert j1["diagnostic"] == j2["diagnostic"]

    # New: kernel metadata should be present and indicate Seth Kernel
    assert j1.get("kernel_name") == "seth"
    assert j1.get("kernel_family") == "causal_exponential"

    diag = j1["diagnostic"]
    spike_recovery = diag.get("spike_recovery", {})

    # Recovery within tolerance (±2 bins) recall >= 0.5 for two injected spikes
    assert float(spike_recovery.get("recovery_within_tol_recall", 0.0)) >= 0.5

    # Ensure solver did not finish in fewer than min_iters (25)
    assert int(diag.get("iters", 0)) >= 25

    # iter_trace should have first entries with required keys
    iter_trace = diag.get("iter_trace", [])
    assert len(iter_trace) > 0
    first = iter_trace[0]
    for key in ("obj", "res_norm", "nnz", "max_abs_x"):
        assert key in first, f"Missing {key} in iter_trace entry"
