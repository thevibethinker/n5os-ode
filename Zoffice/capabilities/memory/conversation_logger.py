"""
Memory Capability — Conversation Logger

Tracks conversations between employees and external parties.
"""

import uuid
from datetime import datetime, timezone

from Zoffice.capabilities.memory.db_helpers import get_db


def log_conversation(
    channel: str,
    employee: str,
    counterparty_id: str | None = None,
    summary: str | None = None,
    duration_seconds: int | None = None,
    satisfaction: float | None = None,
    metadata: dict | None = None,
    db_path: str | None = None,
) -> str:
    """
    Log a new conversation.

    Args:
        channel: Communication channel (email, voice, webhook, zo2zo).
        employee: Employee slug handling the conversation.
        counterparty_id: Contact ID of the external party.
        summary: Brief summary of the conversation.
        duration_seconds: Length of conversation in seconds.
        satisfaction: Satisfaction score (0.0 - 1.0).
        metadata: Additional JSON-serializable details.

    Returns:
        Conversation ID (UUID string).
    """
    import json

    conn = get_db(db_path)
    conv_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    meta_json = json.dumps(metadata, default=str) if metadata else None

    conn.execute(
        """
        INSERT INTO conversations (id, started_at, ended_at, channel, employee,
                                   counterparty_id, summary, duration_seconds,
                                   satisfaction, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [conv_id, now, None, channel, employee,
         counterparty_id, summary, duration_seconds, satisfaction, meta_json],
    )
    return conv_id


def get_conversations(
    counterparty_id: str | None = None,
    employee: str | None = None,
    channel: str | None = None,
    since: datetime | None = None,
    limit: int = 50,
    db_path: str | None = None,
) -> list[dict]:
    """
    Retrieve conversations with optional filters.

    Returns:
        List of conversation dicts, most recent first.
    """
    conn = get_db(db_path)
    conditions = []
    params = []

    if counterparty_id:
        conditions.append("counterparty_id = ?")
        params.append(counterparty_id)
    if employee:
        conditions.append("employee = ?")
        params.append(employee)
    if channel:
        conditions.append("channel = ?")
        params.append(channel)
    if since:
        conditions.append("started_at >= ?")
        params.append(since)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.append(limit)

    result = conn.execute(
        f"SELECT * FROM conversations {where} ORDER BY started_at DESC LIMIT ?",
        params,
    )
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def end_conversation(
    id: str,
    summary: str | None = None,
    satisfaction: float | None = None,
    db_path: str | None = None,
) -> bool:
    """
    Mark a conversation as ended, optionally updating summary and satisfaction.

    Returns:
        True if the conversation was found and updated.
    """
    conn = get_db(db_path)
    now = datetime.now(timezone.utc)
    updates = ["ended_at = ?"]
    params = [now]

    if summary is not None:
        updates.append("summary = ?")
        params.append(summary)
    if satisfaction is not None:
        updates.append("satisfaction = ?")
        params.append(satisfaction)

    params.append(id)
    conn.execute(
        f"UPDATE conversations SET {', '.join(updates)} WHERE id = ?",
        params,
    )
    rows = conn.execute("SELECT id FROM conversations WHERE id = ?", [id]).fetchall()
    return len(rows) > 0
