"""Demo: Anamnesis (Numerical Reconstruction Lens) "first light".

Runs a toy 1D sparse-source reconstruction:
- create a sparse "past" (two spikes)
- smear it with a causal exponential kernel (forward model)
- reconstruct with LCA
- score with 1D EMD

Usage:
  python scripts/demo_anamnesis.py
"""

from __future__ import annotations

import json

import numpy as np

from core.reconstruction.simulator import KernelSpec, build_causal_exp_kernel, build_drm_matrix
from core.reconstruction.reconstructor import LCAConfig, lca_solve
from core.reconstruction.evaluator import build_ris_report, emd_1d


def main() -> None:
    n = 256
    dt_s = 1.0
    tau_s = 30.0

    # True sparse "past" source
    x_true = np.zeros(n)
    x_true[40] = 1.0
    x_true[120] = 0.7

    k = build_causal_exp_kernel(KernelSpec(tau_s=tau_s, dt_s=dt_s, n_kernel=128))
    A = build_drm_matrix(k, n=n)

    y = A @ x_true

    cfg = LCAConfig(lam=0.05, max_iters=4000, tol=1e-6, dt=0.05)
    x_hat, diag = lca_solve(A, y, cfg)

    y_hat = A @ x_hat
    emd = emd_1d(y, y_hat, dx=dt_s)

    ris = build_ris_report(
        emd=emd,
        residual_norm=float(diag["residual_norm"]),
        converged=bool(diag["converged"]),
        iters=int(diag["iters"]),
        lam=float(diag["lam"]),
    )

    out = {
        "config": {"n": n, "dt_s": dt_s, "tau_s": tau_s, "lam": cfg.lam},
        "ris": ris.__dict__,
        "diagnostic": diag,
        "peaks_true": [int(np.argmax(x_true)), int(np.argmax(np.where(np.arange(n) != np.argmax(x_true), x_true, 0)))],
        "peaks_hat": [int(np.argmax(x_hat))],
    }

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
