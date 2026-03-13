"""SQLite persistence layer for GRUT-RAI Portal runs and published evidence."""

import sqlite3
import json
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import threading


class RunStore:
    """Thread-safe SQLite store for runs and published evidence."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Use absolute path to storage directory
            db_path = str(Path(__file__).parent / "grut_rai.db")
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._local = threading.local()
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        """Get thread-local DB connection."""
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(str(self.db_path))
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_schema(self):
        """Initialize database schema."""
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                created_at TEXT NOT NULL,
                engine_version TEXT,
                params_hash TEXT,
                request_json TEXT,
                response_json TEXT,
                nis_or_ris_status TEXT,
                hash_bundle TEXT,
                evidence_packet_json TEXT,
                is_published INTEGER DEFAULT 0,
                publish_slug TEXT,
                published_revision INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS published (
                slug TEXT NOT NULL,
                run_id TEXT NOT NULL,
                revision INTEGER NOT NULL,
                published_at TEXT NOT NULL,
                published_json TEXT,
                published_hash TEXT,
                PRIMARY KEY (slug, revision),
                FOREIGN KEY(run_id) REFERENCES runs(id)
            )
        """)

        # Migration: If the table existed with a PRIMARY KEY on slug only (legacy),
        # migrate rows into the composite primary key table to allow multiple revisions.
        try:
            # Inspect pragma to see pk columns
            rows = conn.execute("PRAGMA table_info(published)").fetchall()
            pk_columns = [r[1] for r in rows if r[5] > 0]  # r[1]=name, r[5]=pk
            if len(pk_columns) == 1 and pk_columns[0] == 'slug':
                # Legacy schema detected. Rename and recreate with new PK.
                conn.execute("ALTER TABLE published RENAME TO published_legacy")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS published (
                        slug TEXT NOT NULL,
                        run_id TEXT NOT NULL,
                        revision INTEGER NOT NULL,
                        published_at TEXT NOT NULL,
                        published_json TEXT,
                        published_hash TEXT,
                        PRIMARY KEY (slug, revision),
                        FOREIGN KEY(run_id) REFERENCES runs(id)
                    )
                """)
                # Copy legacy rows (set revision to 1 if NULL)
                conn.execute("INSERT OR IGNORE INTO published (slug, run_id, revision, published_at, published_json, published_hash) SELECT slug, run_id, IFNULL(revision,1), published_at, published_json, published_hash FROM published_legacy")
                conn.execute("DROP TABLE published_legacy")
                conn.commit()
        except Exception:
            # Best effort migration; continue if anything fails
            pass
        # Topics for GRUTipedia
        conn.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                slug TEXT PRIMARY KEY,
                title TEXT,
                definition_md TEXT,
                equations_md TEXT,
                edition INTEGER,
                created_at TEXT,
                updated_at TEXT,
                tags_json TEXT
            )
        """)

        # Links from topics to runs (or published slugs)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS topic_links (
                topic_slug TEXT NOT NULL,
                run_id TEXT NOT NULL,
                added_at TEXT NOT NULL,
                note_md TEXT,
                PRIMARY KEY (topic_slug, run_id),
                FOREIGN KEY(topic_slug) REFERENCES topics(slug),
                FOREIGN KEY(run_id) REFERENCES runs(id)
            )
        """)
        conn.commit()

    def save_run(
        self,
        kind: str,
        request: Dict[str, Any],
        response: Dict[str, Any],
        engine_version: str,
        params_hash: str,
        status: str,
        run_id: Optional[str] = None,
    ) -> str:
        """Save a run to the database.

        Returns the run_id.
        """
        if run_id is None:
            run_id = str(uuid.uuid4())

        created_at = datetime.utcnow().isoformat()
        request_json = json.dumps(request, sort_keys=True)
        response_json = json.dumps(response, sort_keys=True)
        bundle_data = f"{request_json}|{response_json}|{engine_version}".encode()
        hash_bundle = hashlib.sha256(bundle_data).hexdigest()

        conn = self._get_conn()
        conn.execute("""
            INSERT OR REPLACE INTO runs
            (id, kind, created_at, engine_version, params_hash, request_json, response_json, nis_or_ris_status, hash_bundle)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (run_id, kind, created_at, engine_version, params_hash, request_json, response_json, status, hash_bundle))
        conn.commit()

        return run_id

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a run by ID."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM runs WHERE id = ?", (run_id,)
        ).fetchone()

        if row is None:
            return None

        return {
            "id": row["id"],
            "kind": row["kind"],
            "created_at": row["created_at"],
            "engine_version": row["engine_version"],
            "params_hash": row["params_hash"],
            "request": json.loads(row["request_json"]),
            "response": json.loads(row["response_json"]),
            "status": row["nis_or_ris_status"],
            "hash_bundle": row["hash_bundle"],
            "evidence_packet_json": row["evidence_packet_json"],
            "is_published": bool(row["is_published"]),
            "publish_slug": row["publish_slug"],
            "published_revision": row["published_revision"],
        }

    def list_runs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List recent runs."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT id, kind, created_at, engine_version, params_hash, nis_or_ris_status, is_published, publish_slug, published_revision FROM runs ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()

        return [
            {
                "id": row["id"],
                "kind": row["kind"],
                "created_at": row["created_at"],
                "engine_version": row["engine_version"],
                "params_hash": row["params_hash"],
                "status": row["nis_or_ris_status"],
                "is_published": bool(row["is_published"]),
                "publish_slug": row["publish_slug"],
                "published_revision": row["published_revision"],
            }
            for row in rows
        ]

    def _slugify(self, s: str) -> str:
        s = s.lower()
        # keep letters, numbers and hyphens
        import re
        s = re.sub(r"[^a-z0-9]+", "-", s)
        s = re.sub(r"-+", "-", s).strip("-")
        return s

    def _make_slug(self, run_row: Dict[str, Any]) -> str:
        base = f"{run_row.get('kind','run')}-{(run_row.get('params_hash') or '')[:8]}-{(run_row.get('hash_bundle') or '')[:8]}"
        slug = self._slugify(base)
        conn = self._get_conn()
        # Ensure uniqueness by suffixing -2, -3 ...
        candidate = slug
        suffix = 1
        while conn.execute("SELECT 1 FROM published WHERE slug = ?", (candidate,)).fetchone():
            suffix += 1
            candidate = f"{slug}-{suffix}"
        return candidate

    def create_or_update_publish(self, run_id: str) -> Dict[str, Any]:
        """Create a published immutable snapshot for a run.

        Returns dict with slug, revision, published_hash, published_at and urls.
        """
        conn = self._get_conn()

        run = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        if run is None:
            raise ValueError(f"Run {run_id} not found")

        # Load run fields
        run_row = {
            "id": run["id"],
            "kind": run["kind"],
            "params_hash": run["params_hash"],
            "hash_bundle": run["hash_bundle"],
            "engine_version": run["engine_version"],
            "request_json": run["request_json"],
            "response_json": run["response_json"],
            "evidence_packet_json": run["evidence_packet_json"],
            "publish_slug": run["publish_slug"],
        }

        # If we have a cached packet, reuse it for deterministic publishes
        if run_row.get("evidence_packet_json"):
            packet = json.loads(run_row["evidence_packet_json"])
        else:
            # Build packet now
            from core.evidence import make_evidence_packet
            request = json.loads(run_row["request_json"]) if run_row.get("request_json") else {}
            response = json.loads(run_row["response_json"]) if run_row.get("response_json") else {}
            receipt = response.get("nis") or response.get("ris") or {}
            packet = make_evidence_packet(
                kind=run_row.get("kind"),
                request=request,
                response=response,
                engine_version=run_row.get("engine_version"),
                params_hash=run_row.get("params_hash"),
                receipt=receipt,
            )
            # Cache the canonical packet JSON on the run for determinism on republish
            from core.evidence import make_canonical_json
            cached_packet_json = make_canonical_json(packet)
            conn.execute("UPDATE runs SET evidence_packet_json = ? WHERE id = ?", (cached_packet_json, run_id))

        # Determine slug and revision
        if run_row.get("publish_slug"):
            slug = run_row.get("publish_slug")
            existing = conn.execute("SELECT MAX(revision) FROM published WHERE slug = ?", (slug,)).fetchone()
            revision = (existing[0] or 0) + 1
        else:
            slug = self._make_slug(run_row)
            revision = 1

        published_at = datetime.utcnow().isoformat()
        # Use canonical JSON for published snapshot hashing and storage
        from core.evidence import make_canonical_json
        published_json = make_canonical_json(packet)
        published_hash = hashlib.sha256(published_json.encode()).hexdigest()

        # Insert published row for this revision
        conn.execute(
            "INSERT INTO published (slug, run_id, revision, published_at, published_json, published_hash) VALUES (?, ?, ?, ?, ?, ?)",
            (slug, run_id, revision, published_at, published_json, published_hash),
        )

        # Update run metadata to mark published (do not mutate request/response payloads)
        conn.execute(
            "UPDATE runs SET is_published = 1, publish_slug = ?, published_revision = ? WHERE id = ?",
            (slug, revision, run_id),
        )

        conn.commit()

        return {
            "slug": slug,
            "revision": revision,
            "published_hash": published_hash,
            "published_at": published_at,
            "url_latest": f"/p/{slug}",
            "url_revision": f"/p/{slug}/{revision}",
        }

    def get_published_latest(self, slug: str) -> Optional[Dict[str, Any]]:
        return self.get_published(slug, revision=None)

    def get_published_revision(self, slug: str, revision: int) -> Optional[Dict[str, Any]]:
        return self.get_published(slug, revision=revision)

    def get_published(self, slug: str, revision: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get a published snapshot (latest revision if not specified)."""
        conn = self._get_conn()

        if revision is None:
            row = conn.execute(
                "SELECT * FROM published WHERE slug = ? ORDER BY revision DESC LIMIT 1",
                (slug,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM published WHERE slug = ? AND revision = ?",
                (slug, revision),
            ).fetchone()

        if row is None:
            return None

        return {
            "slug": row["slug"],
            "run_id": row["run_id"],
            "revision": row["revision"],
            "published_at": row["published_at"],
            "published_json": json.loads(row["published_json"]),
            "published_hash": row["published_hash"],
        }

    def list_published(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List published snapshots (latest revision of each slug)."""
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT slug, run_id, MAX(revision) as revision, published_at, published_hash
            FROM published
            GROUP BY slug
            ORDER BY published_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()

        return [
            {
                "slug": row["slug"],
                "run_id": row["run_id"],
                "revision": row["revision"],
                "published_at": row["published_at"],
                "published_hash": row["published_hash"],
            }
            for row in rows
        ]

    # -----------------
    # GRUTipedia helpers
    # -----------------
    def seed_topics(self, topics: List[Dict[str, Any]]) -> None:
        """Seed canonical topics if missing."""
        conn = self._get_conn()
        for t in topics:
            slug = t.get("slug")
            title = t.get("title")
            definition_md = t.get("definition_md")
            equations_md = t.get("equations_md")
            edition = int(t.get("edition", 1))
            created_at = t.get("created_at") or datetime.utcnow().isoformat()
            tags_json = json.dumps(t.get("tags", []), sort_keys=True)

            conn.execute("""
                INSERT OR IGNORE INTO topics (slug, title, definition_md, equations_md, edition, created_at, updated_at, tags_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (slug, title, definition_md, equations_md, edition, created_at, None, tags_json))
        conn.commit()

    def list_topics(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT slug, title, edition, tags_json FROM topics ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()

        return [
            {
                "slug": row["slug"],
                "title": row["title"],
                "edition": row["edition"],
                "tags": json.loads(row["tags_json"] or "[]"),
            }
            for row in rows
        ]

    def get_topic(self, slug: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM topics WHERE slug = ?", (slug,)).fetchone()
        if row is None:
            return None

        topic = {
            "slug": row["slug"],
            "title": row["title"],
            "definition_md": row["definition_md"],
            "equations_md": row["equations_md"],
            "edition": row["edition"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "tags": json.loads(row["tags_json"] or "[]"),
        }

        # Gather linked runs
        rows = conn.execute(
            """
            SELECT tl.run_id, tl.added_at, tl.note_md, r.nis_or_ris_status as status, r.engine_version, r.params_hash, r.hash_bundle, r.created_at, r.is_published, r.publish_slug, r.published_revision
            FROM topic_links tl
            LEFT JOIN runs r ON r.id = tl.run_id
            WHERE tl.topic_slug = ?
            ORDER BY tl.added_at DESC
            """,
            (slug,),
        ).fetchall()

        links = []
        for r in rows:
            links.append(
                {
                    "run_id": r["run_id"],
                    "added_at": r["added_at"],
                    "note_md": r["note_md"],
                    "status": r["status"],
                    "engine_version": r["engine_version"],
                    "params_hash": r["params_hash"],
                    "bundle_hash": r["hash_bundle"],
                    "created_at": r["created_at"],
                    "export_url": f"/runs/{r['run_id']}/export",
                    "is_published": bool(r["is_published"]),
                    "publish_slug": r["publish_slug"],
                    "published_revision": r["published_revision"],
                }
            )

        topic["links"] = links
        return topic

    def add_link(self, topic_slug: str, run_id: str, note_md: Optional[str] = None) -> None:
        conn = self._get_conn()

        # Validate topic exists
        t = conn.execute("SELECT slug FROM topics WHERE slug = ?", (topic_slug,)).fetchone()
        if t is None:
            raise ValueError(f"Topic {topic_slug} not found")

        # Validate run exists
        r = conn.execute("SELECT id FROM runs WHERE id = ?", (run_id,)).fetchone()
        if r is None:
            raise ValueError(f"Run {run_id} not found")

        added_at = datetime.utcnow().isoformat()
        conn.execute(
            "INSERT OR REPLACE INTO topic_links (topic_slug, run_id, added_at, note_md) VALUES (?, ?, ?, ?)",
            (topic_slug, run_id, added_at, note_md),
        )
        conn.commit()


# Global store instance
_store = None


def get_store() -> RunStore:
    """Get or create the global run store."""
    global _store
    if _store is None:
        _store = RunStore()
    return _store
