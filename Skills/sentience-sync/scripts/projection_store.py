#!/usr/bin/env python3
"""
SQLite projection store for Sentience CRM enrichment.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_DB_PATH = DATA_DIR / "projections.db"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _json_dump(value: Any) -> str:
    return json.dumps(value if value is not None else [], sort_keys=True)


def _json_load(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    return json.loads(value)


class ProjectionStore:
    def __init__(self, path: str | Path = DEFAULT_DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.create_tables()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def create_tables(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                  id TEXT PRIMARY KEY,
                  event_ids TEXT NOT NULL,
                  timestamp TEXT NOT NULL,
                  interaction_type TEXT NOT NULL,
                  summary TEXT NOT NULL,
                  person_ids TEXT,
                  company_ids TEXT,
                  confidence TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  projection_key TEXT UNIQUE NOT NULL
                );

                CREATE TABLE IF NOT EXISTS contact_context (
                  person_id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  last_interaction_at TEXT,
                  interaction_count INTEGER DEFAULT 0,
                  context_notes TEXT,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS company_context (
                  company_id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  last_seen_at TEXT,
                  mention_count INTEGER DEFAULT 0,
                  context_notes TEXT,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS review_queue (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  candidate_type TEXT NOT NULL,
                  candidate_data TEXT NOT NULL,
                  reason TEXT NOT NULL,
                  suggested_action TEXT,
                  source_event_ids TEXT NOT NULL,
                  status TEXT DEFAULT 'pending',
                  created_at TEXT NOT NULL,
                  resolved_at TEXT
                );

                CREATE TABLE IF NOT EXISTS projection_ledger (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  candidate_id TEXT NOT NULL,
                  destination TEXT NOT NULL,
                  record_id TEXT,
                  write_type TEXT NOT NULL,
                  confidence TEXT NOT NULL,
                  source_event_ids TEXT NOT NULL,
                  rollback_data TEXT,
                  outcome TEXT NOT NULL DEFAULT 'applied',
                  message TEXT,
                  created_at TEXT NOT NULL
                );
                """
            )

    def table_exists(self, table_name: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
                (table_name,),
            ).fetchone()
        return row is not None

    def insert_interaction(self, record: dict[str, Any]) -> dict[str, Any]:
        payload = self._normalize_interaction(record)
        result: dict[str, Any]
        with self._connect() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO interactions (
                      id, event_ids, timestamp, interaction_type, summary,
                      person_ids, company_ids, confidence, created_at, projection_key
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload["id"],
                        payload["event_ids"],
                        payload["timestamp"],
                        payload["interaction_type"],
                        payload["summary"],
                        payload["person_ids"],
                        payload["company_ids"],
                        payload["confidence"],
                        payload["created_at"],
                        payload["projection_key"],
                    ),
                )
                outcome = "applied"
                message = "interaction inserted"
                record_id = payload["id"]
                result = {"status": "inserted", "record_id": record_id, "projection_key": payload["projection_key"]}
            except sqlite3.IntegrityError:
                existing = conn.execute(
                    "SELECT id FROM interactions WHERE projection_key = ?",
                    (payload["projection_key"],),
                ).fetchone()
                outcome = "blocked"
                message = "interaction replay blocked by projection_key"
                record_id = existing["id"] if existing else None
                result = {"status": "blocked", "record_id": record_id, "projection_key": payload["projection_key"]}

            self._insert_ledger_row(
                conn,
                {
                    "candidate_id": payload["candidate_id"],
                    "destination": "interactions",
                    "record_id": record_id,
                    "write_type": "insert",
                    "confidence": payload["confidence"],
                    "source_event_ids": payload["event_ids"],
                    "rollback_data": payload["rollback_data"],
                    "outcome": outcome,
                    "message": message,
                    "created_at": payload["created_at"],
                },
            )
        return result

    def interaction_exists(self, projection_key: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM interactions WHERE projection_key = ?",
                (projection_key,),
            ).fetchone()
        return row is not None

    def get_interaction(self, interaction_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM interactions WHERE id = ?",
                (interaction_id,),
            ).fetchone()
        return self._deserialize_interaction_row(row) if row else None

    def list_interactions(
        self,
        *,
        interaction_type: str | None = None,
        confidence: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM interactions"
        clauses = []
        params: list[Any] = []
        if interaction_type:
            clauses.append("interaction_type = ?")
            params.append(interaction_type)
        if confidence:
            clauses.append("confidence = ?")
            params.append(confidence)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY timestamp DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._deserialize_interaction_row(row) for row in rows]

    def upsert_contact_context(self, record: dict[str, Any]) -> dict[str, Any]:
        payload = self._normalize_contact_context(record)
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT 1 FROM contact_context WHERE person_id = ?",
                (payload["person_id"],),
            ).fetchone()
            conn.execute(
                """
                INSERT INTO contact_context (
                  person_id, name, last_interaction_at, interaction_count,
                  context_notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(person_id) DO UPDATE SET
                  name = excluded.name,
                  last_interaction_at = excluded.last_interaction_at,
                  interaction_count = excluded.interaction_count,
                  context_notes = excluded.context_notes,
                  updated_at = excluded.updated_at
                """,
                (
                    payload["person_id"],
                    payload["name"],
                    payload["last_interaction_at"],
                    payload["interaction_count"],
                    payload["context_notes"],
                    payload["created_at"],
                    payload["updated_at"],
                ),
            )
        return {"status": "updated" if existing else "inserted", "person_id": payload["person_id"]}

    def contact_context_exists(self, person_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM contact_context WHERE person_id = ?",
                (person_id,),
            ).fetchone()
        return row is not None

    def get_contact_context(self, person_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM contact_context WHERE person_id = ?",
                (person_id,),
            ).fetchone()
        return self._deserialize_contact_context_row(row) if row else None

    def list_contact_context(self, limit: int | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM contact_context ORDER BY updated_at DESC"
        params: list[Any] = []
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._deserialize_contact_context_row(row) for row in rows]

    def upsert_company_context(self, record: dict[str, Any]) -> dict[str, Any]:
        payload = self._normalize_company_context(record)
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT 1 FROM company_context WHERE company_id = ?",
                (payload["company_id"],),
            ).fetchone()
            conn.execute(
                """
                INSERT INTO company_context (
                  company_id, name, last_seen_at, mention_count,
                  context_notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id) DO UPDATE SET
                  name = excluded.name,
                  last_seen_at = excluded.last_seen_at,
                  mention_count = excluded.mention_count,
                  context_notes = excluded.context_notes,
                  updated_at = excluded.updated_at
                """,
                (
                    payload["company_id"],
                    payload["name"],
                    payload["last_seen_at"],
                    payload["mention_count"],
                    payload["context_notes"],
                    payload["created_at"],
                    payload["updated_at"],
                ),
            )
        return {"status": "updated" if existing else "inserted", "company_id": payload["company_id"]}

    def company_context_exists(self, company_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM company_context WHERE company_id = ?",
                (company_id,),
            ).fetchone()
        return row is not None

    def get_company_context(self, company_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM company_context WHERE company_id = ?",
                (company_id,),
            ).fetchone()
        return self._deserialize_company_context_row(row) if row else None

    def list_company_context(self, limit: int | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM company_context ORDER BY updated_at DESC"
        params: list[Any] = []
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._deserialize_company_context_row(row) for row in rows]

    def enqueue_review_item(self, record: dict[str, Any]) -> dict[str, Any]:
        payload = self._normalize_review_item(record)
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO review_queue (
                  candidate_type, candidate_data, reason, suggested_action,
                  source_event_ids, status, created_at, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["candidate_type"],
                    payload["candidate_data"],
                    payload["reason"],
                    payload["suggested_action"],
                    payload["source_event_ids"],
                    payload["status"],
                    payload["created_at"],
                    payload["resolved_at"],
                ),
            )
            review_id = int(cursor.lastrowid)
        return {"status": "inserted", "id": review_id}

    def review_item_exists(self, review_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM review_queue WHERE id = ?",
                (review_id,),
            ).fetchone()
        return row is not None

    def get_review_item(self, review_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM review_queue WHERE id = ?",
                (review_id,),
            ).fetchone()
        return self._deserialize_review_row(row) if row else None

    def list_review_queue(self, *, status: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM review_queue"
        params: list[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._deserialize_review_row(row) for row in rows]

    def record_ledger_entry(self, record: dict[str, Any]) -> int:
        payload = self._normalize_ledger_entry(record)
        with self._connect() as conn:
            cursor = self._insert_ledger_row(conn, payload)
            entry_id = int(cursor.lastrowid)
        return entry_id

    def ledger_entry_exists(self, entry_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM projection_ledger WHERE id = ?",
                (entry_id,),
            ).fetchone()
        return row is not None

    def list_ledger_entries(
        self,
        *,
        candidate_id: str | None = None,
        destination: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM projection_ledger"
        clauses = []
        params: list[Any] = []
        if candidate_id:
            clauses.append("candidate_id = ?")
            params.append(candidate_id)
        if destination:
            clauses.append("destination = ?")
            params.append(destination)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY id ASC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._deserialize_ledger_row(row) for row in rows]

    def _insert_ledger_row(self, conn: sqlite3.Connection, record: dict[str, Any]) -> sqlite3.Cursor:
        payload = self._normalize_ledger_entry(record)
        return conn.execute(
            """
            INSERT INTO projection_ledger (
              candidate_id, destination, record_id, write_type, confidence,
              source_event_ids, rollback_data, outcome, message, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["candidate_id"],
                payload["destination"],
                payload["record_id"],
                payload["write_type"],
                payload["confidence"],
                payload["source_event_ids"],
                payload["rollback_data"],
                payload["outcome"],
                payload["message"],
                payload["created_at"],
            ),
        )

    def _normalize_interaction(self, record: dict[str, Any]) -> dict[str, Any]:
        now = utc_now_iso()
        return {
            "id": str(record["id"]),
            "candidate_id": str(record.get("candidate_id") or record["id"]),
            "event_ids": _json_dump(record.get("event_ids") or []),
            "timestamp": str(record["timestamp"]),
            "interaction_type": str(record["interaction_type"]),
            "summary": str(record["summary"]),
            "person_ids": _json_dump(record.get("person_ids") or []),
            "company_ids": _json_dump(record.get("company_ids") or []),
            "confidence": str(record.get("confidence") or "uncertain"),
            "created_at": str(record.get("created_at") or now),
            "projection_key": str(record["projection_key"]),
            "rollback_data": _json_dump(record.get("rollback_data") or {}),
        }

    def _normalize_contact_context(self, record: dict[str, Any]) -> dict[str, Any]:
        now = utc_now_iso()
        return {
            "person_id": str(record["person_id"]),
            "name": str(record["name"]),
            "last_interaction_at": record.get("last_interaction_at"),
            "interaction_count": int(record.get("interaction_count", 0)),
            "context_notes": _json_dump(record.get("context_notes") or []),
            "created_at": str(record.get("created_at") or now),
            "updated_at": str(record.get("updated_at") or now),
        }

    def _normalize_company_context(self, record: dict[str, Any]) -> dict[str, Any]:
        now = utc_now_iso()
        return {
            "company_id": str(record["company_id"]),
            "name": str(record["name"]),
            "last_seen_at": record.get("last_seen_at"),
            "mention_count": int(record.get("mention_count", 0)),
            "context_notes": _json_dump(record.get("context_notes") or []),
            "created_at": str(record.get("created_at") or now),
            "updated_at": str(record.get("updated_at") or now),
        }

    def _normalize_review_item(self, record: dict[str, Any]) -> dict[str, Any]:
        now = utc_now_iso()
        return {
            "candidate_type": str(record["candidate_type"]),
            "candidate_data": _json_dump(record["candidate_data"]),
            "reason": str(record["reason"]),
            "suggested_action": record.get("suggested_action"),
            "source_event_ids": _json_dump(record.get("source_event_ids") or []),
            "status": str(record.get("status") or "pending"),
            "created_at": str(record.get("created_at") or now),
            "resolved_at": record.get("resolved_at"),
        }

    def _normalize_ledger_entry(self, record: dict[str, Any]) -> dict[str, Any]:
        return {
            "candidate_id": str(record["candidate_id"]),
            "destination": str(record["destination"]),
            "record_id": None if record.get("record_id") is None else str(record.get("record_id")),
            "write_type": str(record.get("write_type") or "insert"),
            "confidence": str(record.get("confidence") or "uncertain"),
            "source_event_ids": _json_dump(record.get("source_event_ids") or []),
            "rollback_data": _json_dump(record.get("rollback_data") or {}),
            "outcome": str(record.get("outcome") or "applied"),
            "message": record.get("message"),
            "created_at": str(record.get("created_at") or utc_now_iso()),
        }

    def _deserialize_interaction_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "event_ids": _json_load(row["event_ids"], []),
            "timestamp": row["timestamp"],
            "interaction_type": row["interaction_type"],
            "summary": row["summary"],
            "person_ids": _json_load(row["person_ids"], []),
            "company_ids": _json_load(row["company_ids"], []),
            "confidence": row["confidence"],
            "created_at": row["created_at"],
            "projection_key": row["projection_key"],
        }

    def _deserialize_contact_context_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "person_id": row["person_id"],
            "name": row["name"],
            "last_interaction_at": row["last_interaction_at"],
            "interaction_count": row["interaction_count"],
            "context_notes": _json_load(row["context_notes"], []),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _deserialize_company_context_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "company_id": row["company_id"],
            "name": row["name"],
            "last_seen_at": row["last_seen_at"],
            "mention_count": row["mention_count"],
            "context_notes": _json_load(row["context_notes"], []),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _deserialize_review_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "candidate_type": row["candidate_type"],
            "candidate_data": _json_load(row["candidate_data"], {}),
            "reason": row["reason"],
            "suggested_action": row["suggested_action"],
            "source_event_ids": _json_load(row["source_event_ids"], []),
            "status": row["status"],
            "created_at": row["created_at"],
            "resolved_at": row["resolved_at"],
        }

    def _deserialize_ledger_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "candidate_id": row["candidate_id"],
            "destination": row["destination"],
            "record_id": row["record_id"],
            "write_type": row["write_type"],
            "confidence": row["confidence"],
            "source_event_ids": _json_load(row["source_event_ids"], []),
            "rollback_data": _json_load(row["rollback_data"], {}),
            "outcome": row["outcome"],
            "message": row["message"],
            "created_at": row["created_at"],
        }
