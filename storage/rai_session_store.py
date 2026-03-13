"""Event-sourced session store for RAI chat (SQLite)."""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def _stable_json_dumps(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _hash_payload(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(_stable_json_dumps(payload).encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


class RAISessionStore:
    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_path = str(Path(__file__).resolve().parent.parent / "data" / "rai.sqlite")
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._local = threading.local()
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(str(self.db_path))
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_schema(self) -> None:
        conn = self._get_conn()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                ts_utc TEXT NOT NULL,
                type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                payload_hash TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_calls_json TEXT,
                run_ids_json TEXT,
                ts_utc TEXT NOT NULL
            )
            """
        )
        conn.commit()

    def new_session_id(self) -> str:
        return str(uuid.uuid4())

    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT session_id, state_json, updated_utc FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["state_json"])

    def upsert_session_state(self, session_id: str, state: Dict[str, Any]) -> None:
        updated_utc = _utc_now()
        state_json = _stable_json_dumps(state)
        conn = self._get_conn()
        conn.execute(
            """
            INSERT OR REPLACE INTO sessions (session_id, state_json, updated_utc)
            VALUES (?, ?, ?)
            """,
            (session_id, state_json, updated_utc),
        )
        conn.commit()

    def append_event(self, session_id: str, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            "event_id": str(uuid.uuid4()),
            "session_id": session_id,
            "ts_utc": _utc_now(),
            "type": event_type,
            "payload": payload,
            "payload_hash": _hash_payload(payload),
        }
        conn = self._get_conn()
        conn.execute(
            """
            INSERT INTO events (event_id, session_id, ts_utc, type, payload_json, payload_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_id"],
                event["session_id"],
                event["ts_utc"],
                event["type"],
                _stable_json_dumps(event["payload"]),
                event["payload_hash"],
            ),
        )
        conn.commit()
        return event

    # --- Conversation memory (Phase 2) ---

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        run_ids: Optional[List[str]] = None,
    ) -> None:
        conn = self._get_conn()
        conn.execute(
            """
            INSERT INTO conversation_messages
                (session_id, role, content, tool_calls_json, run_ids_json, ts_utc)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                role,
                content,
                json.dumps(tool_calls) if tool_calls else None,
                json.dumps(run_ids) if run_ids else None,
                _utc_now(),
            ),
        )
        conn.commit()

    def get_conversation(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            """
            SELECT role, content, tool_calls_json, run_ids_json, ts_utc
            FROM conversation_messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
        messages = []
        for row in rows:
            msg: Dict[str, Any] = {
                "role": row["role"],
                "content": row["content"],
                "ts_utc": row["ts_utc"],
            }
            if row["tool_calls_json"]:
                msg["tool_calls"] = json.loads(row["tool_calls_json"])
            if row["run_ids_json"]:
                msg["run_ids"] = json.loads(row["run_ids_json"])
            messages.append(msg)
        messages.reverse()
        return messages

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        conn = self._get_conn()
        msg_count = conn.execute(
            "SELECT COUNT(*) as c FROM conversation_messages WHERE session_id = ?",
            (session_id,),
        ).fetchone()["c"]
        return {
            "session_id": session_id,
            "message_count": msg_count,
        }

    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT session_id, updated_utc FROM sessions ORDER BY updated_utc DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [{"session_id": row["session_id"], "updated_utc": row["updated_utc"]} for row in rows]

    def list_events(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            """
            SELECT event_id, session_id, ts_utc, type, payload_json, payload_hash
            FROM events
            WHERE session_id = ?
            ORDER BY ts_utc DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
        events = []
        for row in rows:
            events.append(
                {
                    "event_id": row["event_id"],
                    "session_id": row["session_id"],
                    "ts_utc": row["ts_utc"],
                    "type": row["type"],
                    "payload": json.loads(row["payload_json"]),
                    "payload_hash": row["payload_hash"],
                }
            )
        events.reverse()
        return events
