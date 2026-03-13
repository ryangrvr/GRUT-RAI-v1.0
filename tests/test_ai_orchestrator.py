"""Tests for the AI orchestrator with fallback behavior."""

import pytest
from pathlib import Path


@pytest.fixture
def grut_engine():
    from grut.canon import GRUTCanon
    from grut.engine import GRUTEngine
    canon_path = str(Path(__file__).resolve().parent.parent / "canon" / "grut_canon_v0.3.json")
    canon = GRUTCanon(canon_path)
    return GRUTEngine(canon, determinism_mode="STRICT")


def test_fallback_theory_tau0(monkeypatch):
    """Fallback should explain tau0 without AI."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import ai.client as mod
    mod._instance = None

    from ai.orchestrator import respond
    result = respond("What is tau0?")

    assert result.fallback_used is True
    assert "41.9" in result.text_markdown or "tau0" in result.text_markdown.lower()
    mod._instance = None


def test_fallback_theory_alpha_mem(monkeypatch):
    """Fallback should explain alpha_mem."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import ai.client as mod
    mod._instance = None

    from ai.orchestrator import respond
    result = respond("explain alpha_mem")

    assert result.fallback_used is True
    assert "alpha_mem" in result.text_markdown.lower()
    mod._instance = None


def test_fallback_run_request(monkeypatch, grut_engine):
    """Fallback should detect run intent and execute engine."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import ai.client as mod
    mod._instance = None

    from ai.orchestrator import respond
    result = respond("run H(z)", grut_engine=grut_engine)

    assert result.fallback_used is True
    assert "completed" in result.text_markdown.lower() or "Phase-2" in result.text_markdown
    # Should produce charts
    assert len(result.charts) > 0 or result.certificate_summary is not None
    mod._instance = None


def test_fallback_generic_message(monkeypatch):
    """Fallback should handle generic messages gracefully."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import ai.client as mod
    mod._instance = None

    from ai.orchestrator import respond
    result = respond("hello there")

    assert result.fallback_used is True
    assert "deterministic" in result.text_markdown.lower() or "ANTHROPIC_API_KEY" in result.text_markdown
    mod._instance = None


def test_fallback_nis_question(monkeypatch):
    """Fallback should explain NIS as Numerical Integrity Standard."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import ai.client as mod
    mod._instance = None

    from ai.orchestrator import respond
    result = respond("What is the NIS certificate?")

    assert result.fallback_used is True
    assert "nis" in result.text_markdown.lower()
    assert "Numerical Integrity Standard" in result.text_markdown
    assert "Neutral Integrity System" not in result.text_markdown
    mod._instance = None
