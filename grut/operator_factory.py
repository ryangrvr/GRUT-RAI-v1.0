from typing import Any, Callable, Dict, Tuple

from .exceptions import CanonError

OperatorFn = Callable[[Any, Dict[str, float], Dict[str, Any]], Tuple[Dict[str, float], Dict[str, Any]]]


class OperatorFactory:
    def __init__(self) -> None:
        self._registry: Dict[str, OperatorFn] = {}

    def register(self, stack_key: str) -> Callable[[OperatorFn], OperatorFn]:
        def deco(fn: OperatorFn) -> OperatorFn:
            if stack_key in self._registry:
                raise CanonError(f"Duplicate operator registration: {stack_key}")
            self._registry[stack_key] = fn
            return fn

        return deco

    def validate_against_canon(self, canon) -> None:
        missing = [k for k in canon.stack_order if k not in self._registry]
        if missing:
            raise CanonError(f"Missing Implementation(s): {missing}")

    def get(self, stack_key: str) -> OperatorFn:
        if stack_key not in self._registry:
            raise CanonError(f"Missing Implementation: {stack_key}")
        return self._registry[stack_key]
