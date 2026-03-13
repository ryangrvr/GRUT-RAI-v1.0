from typing import Any, Dict, Tuple, Optional

from .canon import GRUTCanon
from .engine import GRUTEngine

_CANON = None
_ENGINE = None


def get_engine(canon_path: str = "canon/grut_canon_v0.2.json") -> GRUTEngine:
    global _CANON, _ENGINE
    if _ENGINE is None:
        _CANON = GRUTCanon(canon_path)
        _ENGINE = GRUTEngine(_CANON, determinism_mode="STRICT")
    return _ENGINE


def run_grut(
    input_state: Dict[str, float],
    run_config: Optional[Dict[str, Any]] = None,
    assumptions: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    eng = get_engine()
    return eng.run(input_state, run_config=run_config or {}, assumption_toggles=assumptions or {})
