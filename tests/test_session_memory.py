"""Tests for conversation memory in RAISessionStore."""

import pytest
import tempfile
import os

from storage.rai_session_store import RAISessionStore


@pytest.fixture
def store(tmp_path):
    db_path = str(tmp_path / "test_rai.sqlite")
    return RAISessionStore(db_path=db_path)


def test_append_and_get_messages(store):
    """Messages should be stored and retrieved in order."""
    sid = store.new_session_id()
    store.append_message(sid, "user", "hello")
    store.append_message(sid, "assistant", "hi there")
    store.append_message(sid, "user", "run H(z)")

    msgs = store.get_conversation(sid)
    assert len(msgs) == 3
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "hello"
    assert msgs[1]["role"] == "assistant"
    assert msgs[2]["content"] == "run H(z)"


def test_conversation_limit(store):
    """get_conversation with limit should return most recent messages."""
    sid = store.new_session_id()
    for i in range(10):
        store.append_message(sid, "user", f"message {i}")

    msgs = store.get_conversation(sid, limit=3)
    assert len(msgs) == 3
    # Should be the last 3 messages, in chronological order
    assert msgs[0]["content"] == "message 7"
    assert msgs[1]["content"] == "message 8"
    assert msgs[2]["content"] == "message 9"


def test_session_summary(store):
    """get_session_summary should count messages."""
    sid = store.new_session_id()
    store.append_message(sid, "user", "a")
    store.append_message(sid, "assistant", "b")

    summary = store.get_session_summary(sid)
    assert summary["session_id"] == sid
    assert summary["message_count"] == 2


def test_list_sessions(store):
    """list_sessions should return sessions ordered by update time."""
    s1 = store.new_session_id()
    s2 = store.new_session_id()
    store.upsert_session_state(s1, {"mode": "test"})
    store.upsert_session_state(s2, {"mode": "test"})

    sessions = store.list_sessions(limit=10)
    assert len(sessions) >= 2
    assert any(s["session_id"] == s1 for s in sessions)
    assert any(s["session_id"] == s2 for s in sessions)


def test_message_with_tool_calls(store):
    """Messages with tool calls should serialize/deserialize correctly."""
    sid = store.new_session_id()
    tool_calls = [{"tool": "run_cosmology", "input": {"rho0": 0.2}}]
    run_ids = ["run-123", "run-456"]

    store.append_message(sid, "assistant", "I ran the engine", tool_calls=tool_calls, run_ids=run_ids)

    msgs = store.get_conversation(sid)
    assert len(msgs) == 1
    assert msgs[0]["tool_calls"] == tool_calls
    assert msgs[0]["run_ids"] == run_ids


def test_isolated_sessions(store):
    """Messages from one session should not appear in another."""
    s1 = store.new_session_id()
    s2 = store.new_session_id()

    store.append_message(s1, "user", "session 1 message")
    store.append_message(s2, "user", "session 2 message")

    msgs1 = store.get_conversation(s1)
    msgs2 = store.get_conversation(s2)

    assert len(msgs1) == 1
    assert msgs1[0]["content"] == "session 1 message"
    assert len(msgs2) == 1
    assert msgs2[0]["content"] == "session 2 message"
