"""Claude API client with graceful degradation."""

from __future__ import annotations

import json
import os
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_anthropic_available = False
try:
    import anthropic
    _anthropic_available = True
except ImportError:
    anthropic = None  # type: ignore[assignment]

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 8192


class GRUTAIClient:
    """Thin wrapper around the Anthropic SDK with graceful degradation.

    If ANTHROPIC_API_KEY is not set or the SDK is missing, all methods
    return None so callers can fall back to the deterministic path.
    """

    def __init__(self) -> None:
        self._client: Optional[Any] = None
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if api_key and _anthropic_available:
            try:
                self._client = anthropic.Anthropic(api_key=api_key)
                logger.info("GRUT-RAI AI client initialized (model=%s)", MODEL)
            except Exception as exc:
                logger.warning("Failed to initialize Anthropic client: %s", exc)
                self._client = None
        else:
            if not _anthropic_available:
                logger.info("anthropic SDK not installed; AI features disabled")
            elif not api_key:
                logger.info("ANTHROPIC_API_KEY not set; AI features disabled")

    @property
    def available(self) -> bool:
        return self._client is not None

    def chat(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Any]:
        """Send a message to Claude with optional tool-use.

        Returns the raw API response or None if unavailable.
        """
        if not self.available:
            return None

        kwargs: Dict[str, Any] = {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "system": system,
            "messages": messages,
        }
        if tools:
            # Round-trip through JSON to ensure all Python types (True/False/None)
            # become JSON-native types, avoiding Pydantic v2 serialization issues.
            kwargs["tools"] = json.loads(json.dumps(tools))

        try:
            return self._client.messages.create(**kwargs)
        except Exception as exc:
            logger.error("Claude API call failed: %s", exc)
            return None


# Module-level singleton (lazy)
_instance: Optional[GRUTAIClient] = None


def get_ai_client() -> GRUTAIClient:
    global _instance
    if _instance is None:
        _instance = GRUTAIClient()
    return _instance
