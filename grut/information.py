"""Information ledger skeleton for GRUT collapse sector.

Phase III-A: Explicit information-architecture layer WITHOUT overclaiming
unitarity. This is a SKELETON, not a solved paradox.

STATUS: ACTIVE / RESEARCH TARGET

NONCLAIMS (explicit):
- This module does NOT prove information conservation.
- This module does NOT solve the black hole information paradox.
- This module does NOT derive unitarity from GRUT structure.
- The conservation placeholder returns UNTESTED unless the engine
  actually computes and verifies the conservation relation.
- All information quantities are PROXY DEFINITIONS, not fundamental
  measures of quantum information content.

DEFINITIONS:
- I_fields: Information content of the matter/field sector.
  Proxy: Bekenstein-Hawking-like area entropy S_BH = A / (4 l_P^2)
  where A = 4 pi R^2 is the shell area. This is a CLASSICAL proxy.
- I_metric_memory: Information content of the metric/memory sector.
  Proxy: log2 of the number of distinguishable memory states,
  estimated from memory tracking ratio and compactness.
- I_total: I_fields + I_metric_memory (proposed additive ledger).
- archive_access_status: Whether the information is in principle
  accessible to exterior observers.
- conservation_domain: Whether conservation is claimed locally
  or globally.

WHAT WOULD BE NEEDED TO PROMOTE THIS:
1. A micro-derivation of I_fields from quantum gravity (not classical area law)
2. A proper counting of metric memory degrees of freedom
3. A dynamical conservation law that the engine can compute step-by-step
4. A proof that I_total is preserved through horizon crossing
5. An exterior-accessibility analysis (can information escape?)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Physical constants
G_SI = 6.674e-11          # m^3 kg^-1 s^-2
C_SI = 299_792_458.0      # m/s
HBAR_SI = 1.054571817e-34  # J s
K_B = 1.380649e-23        # J/K (Boltzmann)

# Planck length
L_PLANCK = math.sqrt(HBAR_SI * G_SI / C_SI**3)  # ~1.616e-35 m


@dataclass
class InformationLedger:
    """Information bookkeeping for a collapse endpoint state.

    All quantities are PROXY DEFINITIONS. Status: ACTIVE / RESEARCH TARGET.
    """

    # ── Field-sector information (proxy) ──
    I_fields: float = 0.0
    # Bekenstein-Hawking-like area entropy: S = 4 pi R^2 / (4 l_P^2)
    # = pi R^2 / l_P^2. Units: dimensionless (in Planck units).
    # This is a CLASSICAL proxy using the shell area at the current radius.
    # It is NOT a claim about quantum information content.

    # ── Metric/memory-sector information (proxy) ──
    I_metric_memory: float = 0.0
    # Proxy for information stored in the metric memory state.
    # Estimated from the memory tracking ratio and compactness.
    # When M_drive tracks a_grav perfectly (ratio = 1), the metric memory
    # has "saturated" — it encodes the full gravitational field state.

    # ── Total information (proposed additive ledger) ──
    I_total: float = 0.0
    # I_fields + I_metric_memory. The HYPOTHESIS is that I_total is
    # conserved through collapse. This is NOT PROVEN.

    # ── Archive accessibility ──
    archive_access_status: str = "UNKNOWN"
    # Possible values:
    #   "OPEN"    — information is exterior-accessible (pre-horizon)
    #   "FROZEN"  — information is trapped behind horizon
    #   "UNKNOWN" — accessibility not determined
    # Status: PLACEHOLDER. Requires exterior matching to determine.

    # ── Conservation domain ──
    conservation_domain: str = "UNDEFINED"
    # Possible values:
    #   "LOCAL"     — conservation holds within the collapse shell only
    #   "GLOBAL"    — conservation holds including exterior
    #   "UNDEFINED" — conservation domain not yet specified
    # Status: PLACEHOLDER. Requires information flow analysis.

    # ── Conservation check result ──
    conservation_status: str = "UNTESTED"
    # Possible values:
    #   "UNTESTED"    — conservation relation has not been checked
    #   "PLACEHOLDER" — conservation formula exists but engine doesn't verify it
    #   "VERIFIED"    — engine has computed and verified conservation (step-by-step)
    #   "VIOLATED"    — engine found conservation violation
    # Status: UNTESTED. No dynamic conservation check is implemented yet.

    # ── Source metadata ──
    source: str = "collapse_endpoint"
    # Where this ledger was constructed from:
    #   "collapse_endpoint" — from a CollapseResult at final state
    #   "trajectory_step"   — from a single timestep (future)

    # ── Diagnostic fields ──
    R_m: float = 0.0            # shell radius (m)
    compactness: float = 0.0    # r_s / R (dimensionless)
    is_post_horizon: bool = False  # compactness > 1
    memory_tracking_ratio: float = 0.0  # M_drive / a_grav
    barrier_dominance: float = 0.0      # Phi = a_outward / a_inward


def from_collapse_result(result: Any) -> InformationLedger:
    """Construct an InformationLedger from a CollapseResult at the endpoint.

    This uses PROXY definitions for all information quantities.
    It does NOT claim to compute actual quantum information content.

    Parameters
    ----------
    result : CollapseResult
        A completed collapse simulation result.

    Returns
    -------
    InformationLedger
        Ledger with proxy values filled in.
    """
    # Shell radius at endpoint
    R_f = float(result.R_m[-1]) if len(result.R_m) > 0 else 0.0
    r_s = result.r_s_m

    # Compactness
    C = r_s / R_f if R_f > 0 else 0.0
    is_post_horizon = C >= 1.0

    # I_fields: Bekenstein-Hawking-like area entropy (proxy)
    # S_BH = A / (4 l_P^2) = 4 pi R^2 / (4 l_P^2) = pi R^2 / l_P^2
    if R_f > 0:
        I_fields = math.pi * R_f**2 / L_PLANCK**2
    else:
        I_fields = 0.0

    # I_metric_memory: proxy from memory state
    # When memory_tracking_ratio = 1, the memory has fully encoded the
    # gravitational field. We use:
    #   I_metric_memory = I_fields * memory_tracking_ratio * (barrier_dominance)
    # This is a PLACEHOLDER scaling — it says the memory sector carries
    # information proportional to how much it has saturated and how much
    # the barrier is engaged.
    mem_ratio = result.memory_tracking_ratio_final
    barrier_dom = result.barrier_dominance_final

    I_metric_memory = I_fields * mem_ratio * barrier_dom

    I_total = I_fields + I_metric_memory

    # Archive access: simple compactness-based placeholder
    if not is_post_horizon:
        archive_status = "OPEN"
    else:
        archive_status = "FROZEN"
    # NOTE: "FROZEN" does not mean information is lost — it means it is
    # behind the apparent horizon. Whether it is recoverable depends on
    # the Whole Hole structure, which is an ACTIVE RESEARCH TARGET.

    return InformationLedger(
        I_fields=I_fields,
        I_metric_memory=I_metric_memory,
        I_total=I_total,
        archive_access_status=archive_status,
        conservation_domain="UNDEFINED",
        conservation_status="UNTESTED",
        source="collapse_endpoint",
        R_m=R_f,
        compactness=C,
        is_post_horizon=is_post_horizon,
        memory_tracking_ratio=mem_ratio,
        barrier_dominance=barrier_dom,
    )


def check_conservation(
    ledger_initial: InformationLedger,
    ledger_final: InformationLedger,
    rtol: float = 0.01,
) -> Dict[str, Any]:
    """Placeholder conservation check between two ledger states.

    STATUS: PLACEHOLDER. This computes the ratio I_total_final / I_total_initial
    but does NOT claim the conservation law is proven. The proxy definitions
    are too crude for this to be a real test.

    Parameters
    ----------
    ledger_initial : InformationLedger
        Ledger at the initial state.
    ledger_final : InformationLedger
        Ledger at the final state.
    rtol : float
        Relative tolerance for "conservation" (default 1%).

    Returns
    -------
    dict
        Conservation check result with fields:
        - ratio: I_total_final / I_total_initial
        - conserved: bool (within rtol)
        - status: "PLACEHOLDER" (always, until dynamic check is implemented)
        - nonclaim: explicit statement that this is not a proof
    """
    if ledger_initial.I_total <= 0:
        return {
            "ratio": float("nan"),
            "conserved": False,
            "status": "PLACEHOLDER",
            "nonclaim": (
                "Cannot check conservation: initial I_total <= 0. "
                "This is a proxy limitation, not a physics result."
            ),
        }

    ratio = ledger_final.I_total / ledger_initial.I_total
    conserved = abs(ratio - 1.0) < rtol

    return {
        "ratio": ratio,
        "conserved": conserved,
        "status": "PLACEHOLDER",
        "nonclaim": (
            "This conservation check uses PROXY definitions for I_fields "
            "and I_metric_memory. It is NOT a proof of information "
            "conservation. The proxy I_fields = pi R^2 / l_P^2 is a "
            "classical area law, not a quantum information measure. "
            "The proxy I_metric_memory scales with memory saturation "
            "and barrier dominance. Both proxies need micro-derivation "
            "to become operational."
        ),
    }


def to_dict(ledger: InformationLedger) -> Dict[str, Any]:
    """Serialize an InformationLedger to a dict for packet output."""
    return {
        "I_fields": ledger.I_fields,
        "I_metric_memory": ledger.I_metric_memory,
        "I_total": ledger.I_total,
        "archive_access_status": ledger.archive_access_status,
        "conservation_domain": ledger.conservation_domain,
        "conservation_status": ledger.conservation_status,
        "source": ledger.source,
        "R_m": ledger.R_m,
        "compactness": ledger.compactness,
        "is_post_horizon": ledger.is_post_horizon,
        "memory_tracking_ratio": ledger.memory_tracking_ratio,
        "barrier_dominance": ledger.barrier_dominance,
        "nonclaims": [
            "I_fields uses classical Bekenstein-Hawking area proxy, not quantum information",
            "I_metric_memory is a placeholder scaling, not a derived measure",
            "I_total additivity is HYPOTHESIZED, not proven",
            "Conservation is UNTESTED — no dynamic step-by-step check exists",
            "Archive accessibility is based on compactness threshold only",
            "This module does NOT solve the black hole information paradox",
        ],
    }
