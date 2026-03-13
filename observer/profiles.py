from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Dict

ObserverProfile = Literal["monk", "astronomer", "participant"]


@dataclass(frozen=True)
class ProfileWeights:
    """Weights for the hybrid action/entropy flux ΔS."""

    w_ui: float
    w_sensor: float


# Canonical v1 profile presets
PROFILE_WEIGHTS: Dict[ObserverProfile, ProfileWeights] = {
    "monk": ProfileWeights(w_ui=0.0, w_sensor=0.0),
    "astronomer": ProfileWeights(w_ui=0.2, w_sensor=0.8),
    "participant": ProfileWeights(w_ui=0.9, w_sensor=0.1),
}
