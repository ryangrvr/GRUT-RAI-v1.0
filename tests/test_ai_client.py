"""Tests for the AI client with graceful degradation."""

import os
import pytest


def test_client_unavailable_without_key(monkeypatch):
    """Without ANTHROPIC_API_KEY, client.available should be False."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # Reset singleton
    import ai.client as mod
    mod._instance = None
    client = mod.get_ai_client()
    assert client.available is False
    mod._instance = None


def test_client_chat_returns_none_without_key(monkeypatch):
    """Chat should return None when unavailable."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import ai.client as mod
    mod._instance = None
    client = mod.get_ai_client()
    result = client.chat(
        messages=[{"role": "user", "content": "hello"}],
        system="test",
    )
    assert result is None
    mod._instance = None


def test_client_singleton():
    """get_ai_client should return the same instance."""
    import ai.client as mod
    mod._instance = None
    c1 = mod.get_ai_client()
    c2 = mod.get_ai_client()
    assert c1 is c2
    mod._instance = None
