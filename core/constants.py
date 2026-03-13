from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
import math
from typing import Any, Dict


@dataclass(frozen=True)
class GRUTParams:
    """Single source of truth for hardened constants and default knobs.

    Internal units:
      - time: seconds
      - speed: m/s
    """

    engine_version: str = "grut-rai-v1.0"

    # Geometric invariants
    # Canonical refractive index: n_g(0) = sqrt(1 + alpha_vac) = 2/sqrt(3)
    lambda_lock: float = 2.0 / (3.0 ** 0.5)          # 2/sqrt(3) ≈ 1.1547
    beta_lock: float = (3.0 ** 0.5) / 2.0            # 1/lambda_lock ≈ 0.8660
    K0_anchor: float = -1.0 / 12.0                   # curvature anchor

    # Vacuum screening (Phase I canon)
    alpha_vac: float = 1.0 / 3.0                     # GRUT vacuum response parameter (not QED alpha)
    screening_S: float = (12.0 * math.pi) / ((1.0 / 3.0) ** 2)  # 108π ≈ 339.29
    n_g0_sq: float = 1.0 + (1.0 / 3.0)               # n_g^2(0) = 1 + alpha_vac
    n_g0: float = math.sqrt(1.0 + (1.0 / 3.0))        # n_g(0) = sqrt(1 + alpha_vac)

    # Reduced Planck constant (J·s)
    hbar_J_s: float = 1.054571817e-34

    # Core gains / ceilings
    alpha_imp: float = 1.0 / 3.0                     # headroom to reach 4/3
    g_max: float = 4.0 / 3.0                         # saturation ceiling

    # Elasticity / dissipation
    E_base: float = 0.75                             # theoretical stiffness
    dissipation_k: float = 1.0
    phi_mode: str = "unity"                          # supported: unity, phase_weighted
    handoff_kappa: float = 0.02                      # budget scale for phase handoff

    # Optional observer→dissipation coupling (Phase D)
    # Only applies if ObserverConfig.enable_observer_modulation=True.
    info_coupling_lambda: float = 1.0

    # Memory window
    tau0_seconds: float = 41.9 * 1_000_000 * 365.25 * 24 * 3600  # 41.9 Myr

    # Phase bridge defaults (Boethian Pivot)
    phase_x0: float = 0.0
    phase_w: float = 0.6

    # Stiffness cap defaults
    rho_lock: float = 1.0
    sigma_cap: float = 1.0
    smooth_min_k: float = 24.0

    # Smoothness warnings (only applied on sufficiently dense z-grids)
    min_z_for_smoothness: int = 10
    kink_thresh: float = 0.20

    # Growth proxy defaults (optional)
    enable_growth_proxy: bool = True
    growth_gamma: float = 0.55
    sigma8: float = 0.83

    # Tau_eff scaling defaults
    TAU_FACTOR: float = 1.0
    tau_p: float = 1.0

    # CFL / causal integrity
    c_vacuum: float = 299_792_458.0
    CFL_max: float = 1.0
    L_char_m: float = 1.0e21                         # characteristic length scale proxy

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def params_hash(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
