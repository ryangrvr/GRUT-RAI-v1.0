from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional
import json
import hashlib


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))


SensorMode = Literal["off", "ambient", "snapshot"]


@dataclass(frozen=True)
class SensorConfig:
    """Sensor flux configuration.

    This v1 implementation does not fetch external data.
    Instead, you can:
    - set mode='off'
    - set mode='ambient' and provide ambient_flux (deterministic)
    - set mode='snapshot' and provide snapshot_flux and optionally snapshot_payload

    Sensor flux is a dimensionless score in [0,1].
    """

    mode: SensorMode = "off"
    ambient_flux: float = 0.02
    snapshot_flux: Optional[float] = None
    snapshot_payload: Optional[Dict[str, Any]] = None
    timestamp_utc: Optional[str] = None
    source: Optional[str] = None


def sensor_snapshot_hash(payload: Optional[Dict[str, Any]]) -> Optional[str]:
    if payload is None:
        return None
    # Canonical JSON encoding: sort keys, no whitespace
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def compute_sensor_flux(cfg: SensorConfig) -> dict:
    """Compute sensor flux score in [0,1] plus reproducibility metadata."""

    warnings = []
    mode = cfg.mode
    flux: float
    reproducible = True
    snap_hash = sensor_snapshot_hash(cfg.snapshot_payload)

    if mode == "off":
        flux = 0.0
        reproducible = True
    elif mode == "ambient":
        flux = clamp(cfg.ambient_flux, 0.0, 1.0)
        reproducible = True
    elif mode == "snapshot":
        # Accept explicit snapshot_flux, or infer from payload fields.
        inferred = None
        if cfg.snapshot_payload is not None:
            for key in ("flux", "ambient_flux"):
                if key in cfg.snapshot_payload:
                    try:
                        inferred = float(cfg.snapshot_payload.get(key))
                        break
                    except Exception:
                        inferred = None
        if cfg.snapshot_flux is None and inferred is None:
            flux = 0.0
            warnings.append("SENSOR_SNAPSHOT_MISSING_FLUX")
        else:
            flux_val = cfg.snapshot_flux if cfg.snapshot_flux is not None else inferred
            flux = clamp(float(flux_val), 0.0, 1.0)
        # reproducible only if snapshot payload is present or we at least have a stable recorded scalar
        reproducible = True
        if cfg.snapshot_payload is None:
            warnings.append("SENSOR_SNAPSHOT_NO_PAYLOAD: scalar flux only")
    else:
        # Defensive: unknown mode
        flux = 0.0
        reproducible = True
        warnings.append("SENSOR_MODE_UNKNOWN")

    return {
        "sensor_mode": mode,
        "sensor_flux": float(flux),
        "sensor_snapshot_hash": snap_hash,
        "sensor_timestamp_utc": cfg.timestamp_utc,
        "sensor_source": cfg.source,
        "sensor_reproducible": bool(reproducible),
        "sensor_warnings": warnings,
    }
