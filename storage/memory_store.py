from __future__ import annotations

from typing import Dict, Any, Optional
import time

class InMemoryRunStore:
    def __init__(self, max_items: int = 2000):
        self.max_items = max_items
        self._store: Dict[str, Any] = {}
        self._order: list[str] = []

    def put(self, run_id: str, payload: Dict[str, Any]) -> None:
        if run_id in self._store:
            self._store[run_id] = payload
            return
        self._store[run_id] = {"ts": time.time(), **payload}
        self._order.append(run_id)
        if len(self._order) > self.max_items:
            old = self._order.pop(0)
            self._store.pop(old, None)

    def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(run_id)
