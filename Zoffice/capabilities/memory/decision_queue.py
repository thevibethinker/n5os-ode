"""
Memory Capability — Decision Queue

Manages the decision lifecycle: create → pending → resolved/expired.
Decisions requiring human input live here until they're resolved or expire.
"""

import json
import uuid
from datetime import datetime, timezone, timedelta

from Zoffice.capabilities.memory.db_helpers import get_db


def create_decision(
    summary: str,
    origin_employee: str | None = None,
    full_context: dict | None = None,
    options: list | None = None,
    recommendation: str | None = None,
    db_path: str | None = None,
) -> str:
    """
    Create a new pending decision.

    Args:
        summary: Brief description of the decision needed.
        origin_employee: Employee slug that raised the decision.
        full_context: JSON-serializable context for the decision.
        options: List of possible options.
        recommendation: The employee's recommended option.

    Returns:
        Decision ID (UUID string).
    """
    conn = get_db(db_path)
    decision_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    context_json = json.dumps(full_context, default=str) if full_context else None
    options_json = json.dumps(options, default=str) if options else None

    conn.execute(
        """
        INSERT INTO decisions (id, created_at, origin_employee, summary,
                               full_context, options, recommendation, status,
                               resolved_at, resolution, resolved_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', NULL, NULL, NULL)
        """,
        [decision_id, now, origin_employee, summary,
         context_json, options_json, recommendation],
    )
    return decision_id


def get_pending_decisions(
    employee: str | None = None,
    db_path: str | None = None,
) -> list[dict]:
    """
    Get all pending decisions, optionally filtered by origin employee.

    Returns:
        List of decision dicts with status='pending'.
    """
    conn = get_db(db_path)
    conditions = ["status = 'pending'"]
    params = []
    if employee:
        conditions.append("origin_employee = ?")
        params.append(employee)

    where = " AND ".join(conditions)
    result = conn.execute(
        f"SELECT * FROM decisions WHERE {where} ORDER BY created_at DESC",
        params,
    )
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def resolve_decision(
    id: str,
    resolution: str,
    resolved_by: str,
    db_path: str | None = None,
) -> bool:
    """
    Resolve a pending decision.

    Args:
        id: Decision ID.
        resolution: What was decided.
        resolved_by: Who resolved it (human, employee slug, etc.).

    Returns:
        True if the decision was found and resolved.
    """
    conn = get_db(db_path)
    # Pre-check: only resolve if currently pending
    rows = conn.execute(
        "SELECT status FROM decisions WHERE id = ?", [id]
    ).fetchall()
    if not rows or rows[0][0] != "pending":
        return False
    now = datetime.now(timezone.utc)
    conn.execute(
        """
        UPDATE decisions
        SET status = 'resolved', resolved_at = ?, resolution = ?, resolved_by = ?
        WHERE id = ? AND status = 'pending'
        """,
        [now, resolution, resolved_by, id],
    )
    return True


def expire_decisions(
    older_than_days: int = 30,
    db_path: str | None = None,
) -> int:
    """
    Expire pending decisions older than the specified number of days.

    Returns:
        Count of decisions expired.
    """
    conn = get_db(db_path)
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    conn.execute(
        """
        UPDATE decisions
        SET status = 'expired', resolved_at = CURRENT_TIMESTAMP
        WHERE status = 'pending' AND created_at < ?
        """,
        [cutoff],
    )
    # Count expired
    rows = conn.execute(
        "SELECT count(*) FROM decisions WHERE status = 'expired' AND resolved_at >= ?",
        [cutoff],
    ).fetchone()
    return rows[0] if rows else 0
