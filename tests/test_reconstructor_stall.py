"""Test that the LCA reconstructor does not prematurely converge when dynamics are stalled."""

import numpy as np
from core.reconstruction.reconstructor import LCAConfig, lca_reconstruct
from core.reconstruction.simulator import exponential_kernel, build_drm_matrix, KernelSpec


def test_lca_min_iters_enforced():
    """Ensure LCA runs at least min_iters iterations, even if gradients are small."""
    n = 64
    spec = KernelSpec(tau_s=10.0, dt_s=1.0, length=16)
    k = exponential_kernel(spec)
    A = build_drm_matrix(k, n)

    # Create a "hard" problem: large energy but very sparse
    # The solver may converge early if not forced to min_iters
    rng = np.random.default_rng(99)
    x_true = np.zeros(n)
    x_true[10] = 5.0
    x_true[50] = 3.0
    y = A @ x_true

    cfg = LCAConfig(
        lam=0.1,
        max_iters=2000,
        dt=0.05,
        tau=1.0,
        tol=1e-6,
        min_iters=50,  # enforced minimum
        tol_res=1e-6,
        nonneg=False,
    )

    res = lca_reconstruct(y, A, cfg)

    # Verify min_iters was enforced
    assert res.iters >= cfg.min_iters, f"Expected iters >= {cfg.min_iters}, got {res.iters}"

    # Ensure iter_trace shows actual movement (nnz > 0 or max_abs_x > 0)
    iter_trace = res.diagnostics.get("iter_trace", [])
    assert len(iter_trace) > 0
    assert any(entry.get("nnz", 0) > 0 for entry in iter_trace), "iter_trace shows no nonzero coefficients"


def test_lca_stalled_x_does_not_converge():
    """If x remains near zero for all iterations and residual is not improving, ensure iter_trace shows stall."""
    n = 64
    spec = KernelSpec(tau_s=10.0, dt_s=1.0, length=16)
    k = exponential_kernel(spec)
    A = build_drm_matrix(k, n)

    # Very small signal + high lambda = x stays near zero
    y = np.zeros(n)
    y[20] = 0.001  # tiny signal

    cfg = LCAConfig(
        lam=1.0,  # very high lambda forces shrinkage
        max_iters=500,
        dt=0.05,
        tau=1.0,
        tol=1e-6,
        min_iters=25,
        tol_res=1e-6,
        nonneg=False,
    )

    res = lca_reconstruct(y, A, cfg)

    # Check iter_trace: if nnz==0 throughout, the solution is empty (stalled)
    iter_trace = res.diagnostics.get("iter_trace", [])
    nnz_counts = [entry.get("nnz", 0) for entry in iter_trace]

    # Either the solver ran at least min_iters, or if it converged early,
    # at least some iterations show nonzero coefficients.
    if all(c == 0 for c in nnz_counts):
        # Empty solution throughout initial iterations: verify we did run at least min_iters
        assert res.iters >= cfg.min_iters, \
            f"Empty reconstruction should run at least min_iters ({cfg.min_iters}), got {res.iters}"

