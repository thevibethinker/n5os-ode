"""Action conversation tagging.

This module tracks which conversations correspond to which tasks.

Storage: SQLite db at N5/task_system/action_conversations.db
Table: action_conversations

Note: The wider task system (tasks registry, close hooks) may evolve.
This module is intentionally small and dependency-free so that other
workflows (Pulse, thread-close, meeting ingestion) can rely on it.
"""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

_DB_PATH = Path("/home/workspace/N5/task_system/action_conversations.db")


def _connect() -> sqlite3.Connection:
    if not _DB_PATH.exists():
        raise FileNotFoundError(f"action conversations db not found at {_DB_PATH}")
    con = sqlite3.connect(str(_DB_PATH))
    con.row_factory = sqlite3.Row
    return con


def _ensure_schema() -> None:
    con = _connect()
    try:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS action_conversations (
                conversation_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                tagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tag_method TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            );
            """
        )
        con.commit()
    finally:
        con.close()


def _stable_inferred_task_id(description: str) -> str:
    h = hashlib.sha1(description.strip().encode("utf-8")).hexdigest()[:12]
    return f"inferred:{h}"


def tag_conversation(
    conversation_id: str,
    task_id: Optional[str] = None,
    method: Optional[str] = None,
    tag_method: Optional[str] = None,
    inferred_task_description: Optional[str] = None,
    **_: Any,
) -> str:
    """Tag a conversation to a task.

    Supports two calling styles:

    1) Explicit (used by integration tests)
        tag_conversation(conversation_id="con_X", task_id="123", method="explicit")

    2) Inferred (used by newer orchestration rules)
        tag_conversation(conversation_id="con_X", tag_method="inferred",
                         inferred_task_description="...")

    Returns a human-readable status string.
    """

    _ensure_schema()

    final_method = (method or tag_method or "explicit").strip()

    final_task_id = task_id
    if final_task_id is None:
        if not inferred_task_description:
            raise ValueError("task_id is required unless inferred_task_description is provided")
        final_task_id = _stable_inferred_task_id(inferred_task_description)

    con = _connect()
    try:
        con.execute(
            """
            INSERT INTO action_conversations (conversation_id, task_id, tag_method, status)
            VALUES (?, ?, ?, 'active')
            ON CONFLICT(conversation_id) DO UPDATE SET
                task_id=excluded.task_id,
                tag_method=excluded.tag_method,
                status='active',
                tagged_at=CURRENT_TIMESTAMP;
            """,
            (conversation_id, str(final_task_id), final_method),
        )
        con.commit()
    finally:
        con.close()

    return f"success: tagged {conversation_id} → {final_task_id} ({final_method})"


def get_task_for_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    _ensure_schema()
    con = _connect()
    try:
        row = con.execute(
            "SELECT * FROM action_conversations WHERE conversation_id = ?",
            (conversation_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        con.close()


def get_active_action_conversations() -> List[Dict[str, Any]]:
    _ensure_schema()
    con = _connect()
    try:
        rows = con.execute(
            "SELECT * FROM action_conversations WHERE status = 'active' ORDER BY tagged_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()


def close_action_conversation(conversation_id: str, status: str = "closed") -> str:
    """Mark an action conversation as no longer active."""

    _ensure_schema()
    con = _connect()
    try:
        cur = con.execute(
            "UPDATE action_conversations SET status = ? WHERE conversation_id = ?",
            (status, conversation_id),
        )
        con.commit()
        if cur.rowcount == 0:
            return f"not_found: {conversation_id}"
        return f"success: {conversation_id} marked {status}"
    finally:
        con.close()


def check_completion(conversation_id: str) -> Dict[str, Any]:
    """Lightweight completion check.

    Current implementation only reports whether the conversation is still tagged as active.
    It does NOT infer semantic completion of the underlying task.
    """

    rec = get_task_for_conversation(conversation_id)
    if not rec:
        return {
            "conversation_id": conversation_id,
            "found": False,
            "status": "unknown",
            "note": "No tag found in action_conversations.db",
        }

    return {
        "conversation_id": conversation_id,
        "found": True,
        "task_id": rec.get("task_id"),
        "tag_method": rec.get("tag_method"),
        "status": rec.get("status"),
        "note": "This reports tag status, not semantic task completion.",
    }
