from __future__ import annotations

import math


def compute_P_lock(I_value: float, eps_user_s: float, tau0_s: float) -> dict:
    """Compute v1 determination strength.

    We assume I(t) is constant over the window [t-eps_user, t].
    Kernel K(Δt) is the normalized exponential with time constant tau0.

    Integral_0^eps K dt = 1 - exp(-eps/tau0)
    P_lock = I_value * (1 - exp(-eps/tau0))
    """

    eps = max(float(eps_user_s), 0.0)
    tau0 = max(float(tau0_s), 1e-12)
    kernel_mass = 1.0 - math.exp(-eps / tau0)
    P = float(I_value) * kernel_mass
    return {
        "kernel_mass": float(kernel_mass),
        "P_lock": float(P),
        "eps_user_s": float(eps),
        "tau0_s": float(tau0),
    }
