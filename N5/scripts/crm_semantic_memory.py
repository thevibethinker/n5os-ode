#!/usr/bin/env python3
"""CRM semantic-memory synchronization helpers."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:
    from db_paths import INTERACTIONS_TABLE, PEOPLE_TABLE, get_db_connection
except ModuleNotFoundError:
    from N5.scripts.db_paths import INTERACTIONS_TABLE, PEOPLE_TABLE, get_db_connection

try:
    from N5.cognition.n5_memory_client import N5MemoryClient
    _HAS_MEMORY_CLIENT = True
except Exception:
    _HAS_MEMORY_CLIENT = False


LOG = logging.getLogger(__name__)
_SEMANTIC_PATH_TEMPLATE = "/home/workspace/Personal/Knowledge/CRM/_semantic/person-{person_id}.md"


def _load_person_snapshot(person_id: int, interaction_limit: int = 25) -> Optional[Dict[str, Any]]:
    conn = get_db_connection(readonly=True)
    try:
        person = conn.execute(
            f"""
            SELECT id, full_name, email, linkedin_url, company, title, category, status,
                   markdown_path, last_contact_date, updated_at
            FROM {PEOPLE_TABLE}
            WHERE id = ?
            """,
            (person_id,),
        ).fetchone()
        if not person:
            return None

        interactions = conn.execute(
            f"""
            SELECT type, direction, summary, source_ref, occurred_at
            FROM {INTERACTIONS_TABLE}
            WHERE person_id = ?
            ORDER BY occurred_at DESC
            LIMIT ?
            """,
            (person_id, interaction_limit),
        ).fetchall()

        return {
            "person": dict(person),
            "interactions": [dict(row) for row in interactions],
        }
    finally:
        conn.close()


def _build_person_memory_block(snapshot: Dict[str, Any], trigger: str, metadata: Optional[Dict[str, Any]]) -> str:
    person = snapshot["person"]
    interactions = snapshot["interactions"]
    now = datetime.now(timezone.utc).astimezone().isoformat()
    lines = [
        f"CRM Person Snapshot",
        f"Generated At: {now}",
        f"Trigger: {trigger}",
        f"Person ID: {person.get('id')}",
        f"Name: {person.get('full_name') or ''}",
        f"Email: {person.get('email') or ''}",
        f"LinkedIn: {person.get('linkedin_url') or ''}",
        f"Company: {person.get('company') or ''}",
        f"Title: {person.get('title') or ''}",
        f"Category: {person.get('category') or ''}",
        f"Status: {person.get('status') or ''}",
        f"Profile Path: {person.get('markdown_path') or ''}",
        f"Last Contact Date: {person.get('last_contact_date') or ''}",
        "",
        "Recent Interactions:",
    ]

    if not interactions:
        lines.append("- none")
    else:
        for item in interactions:
            lines.append(
                "- "
                + " | ".join(
                    [
                        str(item.get("occurred_at") or ""),
                        str(item.get("type") or ""),
                        str(item.get("direction") or ""),
                        str(item.get("summary") or ""),
                        str(item.get("source_ref") or ""),
                    ]
                )
            )

    if metadata:
        lines.extend(["", "Trigger Metadata:", json.dumps(metadata, ensure_ascii=True, sort_keys=True)])

    return "\n".join(lines).strip() + "\n"


def record_person_interaction(
    person_id: int,
    interaction_type: str,
    summary: str,
    source_ref: str,
    occurred_at: Optional[str] = None,
    direction: Optional[str] = None,
) -> int:
    occurred = occurred_at or datetime.now(timezone.utc).isoformat()
    conn = get_db_connection()
    try:
        existing = conn.execute(
            f"""
            SELECT id FROM {INTERACTIONS_TABLE}
            WHERE person_id = ? AND type = ? AND source_ref = ? AND occurred_at = ?
            LIMIT 1
            """,
            (person_id, interaction_type, source_ref, occurred),
        ).fetchone()
        if existing:
            return int(existing["id"])

        cur = conn.execute(
            f"""
            INSERT INTO {INTERACTIONS_TABLE}
            (person_id, type, direction, summary, source_ref, occurred_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (person_id, interaction_type, direction, summary, source_ref, occurred),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def sync_person_to_semantic_memory(
    person_id: int,
    trigger: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    if not _HAS_MEMORY_CLIENT:
        LOG.warning("N5MemoryClient unavailable; skipping CRM semantic sync for person_id=%s", person_id)
        return False

    snapshot = _load_person_snapshot(person_id)
    if not snapshot:
        LOG.warning("Person %s not found; skipping CRM semantic sync", person_id)
        return False

    content = _build_person_memory_block(snapshot, trigger=trigger, metadata=metadata)
    semantic_path = _SEMANTIC_PATH_TEMPLATE.format(person_id=person_id)

    try:
        client = N5MemoryClient()
        client.index_file(
            semantic_path,
            content,
            content_date=datetime.now(timezone.utc).date().isoformat(),
        )
        return True
    except Exception as exc:
        LOG.warning("CRM semantic sync failed for person %s: %s", person_id, exc)
        return False
