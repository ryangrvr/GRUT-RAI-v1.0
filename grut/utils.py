import json
import hashlib
import math
from typing import Any


def stable_sha256(obj: Any) -> str:
    """Stable hash for JSON-like objects."""
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def is_finite(x: float) -> bool:
    return math.isfinite(x)
