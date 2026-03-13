from typing import Any, Dict, Tuple, Optional

from grut.run import run_grut


def run_canonical_phase2(
    input_state: Dict[str, float],
    run_config: Optional[Dict[str, Any]] = None,
    assumptions: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    return run_grut(input_state, run_config=run_config or {}, assumptions=assumptions or {})
