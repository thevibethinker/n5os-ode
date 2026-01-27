#!/usr/bin/env python3
"""
Pre-Task Staging Module for Zo Task System

This module provides functionality for capturing potential tasks from various sources
(meetings, conversations, emails) into a staging area before promotion to the official
task registry. This prevents task bloat and ensures conscious commitment.

Usage:
    from N5.task_system.staging import capture_staged_task, generate_review_markdown

    # Capture a task from a meeting
    staged_id = capture_staged_task(
        title="Follow up with Sarah",
        source_type="meeting",
        source_id="meeting_123",
        context="Discussed partnership opportunities",
        suggestions={
            "domain": "Careerspan",
            "project": "Partnerships",
            "priority": "strategic"
        }
    )
"""

import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from pathlib import Path

# Database path
DB_PATH = Path("/home/workspace/N5/task_system/tasks.db")
REVIEW_DIR = Path("/home/workspace/N5/review/tasks")


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def capture_staged_task(
    title: str,
    source_type: str,
    source_id: str,
    context: Optional[str] = None,
    description: Optional[str] = None,
    suggestions: Optional[Dict[str, Any]] = None
) -> int:
    """
    Capture a potential task into the staging area.

    Args:
        title: Task title
        source_type: Type of source (meeting, conversation, email, manual)
        source_id: ID of the source (meeting_id, conversation_id, etc.)
        context: Relevant quote or context from source
        description: Full description of the potential task
        suggestions: Dict with AI guesses for domain, project, priority

    Returns:
        staged_id: ID of the newly created staged task
    """
    suggestions = suggestions or {}

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO staged_tasks (
                title, description, source_type, source_id, source_context,
                suggested_domain, suggested_project, suggested_priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            description or "",
            source_type,
            source_id,
            context or "",
            suggestions.get("domain", ""),
            suggestions.get("project", ""),
            suggestions.get("priority", "normal")
        ))
        conn.commit()
        return cursor.lastrowid


def get_pending_staged_tasks() -> List[Dict[str, Any]]:
    """
    Get all pending staged tasks awaiting review.

    Returns:
        List of staged task dictionaries
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM staged_tasks
            WHERE status = 'pending_review'
            ORDER BY captured_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_staged_task_by_id(staged_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific staged task by ID.

    Args:
        staged_id: ID of the staged task

    Returns:
        Task dict or None if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM staged_tasks WHERE id = ?", (staged_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def generate_review_markdown(for_date: Optional[date] = None) -> str:
    """
    Generate a markdown review file for pending staged tasks.

    Args:
        for_date: Date for review (defaults to today)

    Returns:
        Markdown string with formatted review
    """
    if for_date is None:
        for_date = date.today()

    tasks = get_pending_staged_tasks()

    # Group by source type
    by_source: Dict[str, List[Dict]] = {
        "meeting": [],
        "conversation": [],
        "email": [],
        "manual": [],
        "other": []
    }

    for task in tasks:
        source = task["source_type"].lower()
        if source not in by_source:
            source = "other"
        by_source[source].append(task)

    # Build markdown
    lines = [
        f"# Staged Tasks for Review - {for_date.strftime('%Y-%m-%d')}",
        "",
        f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total pending tasks: {len(tasks)}",
        ""
    ]

    source_headers = {
        "meeting": "## From Meetings",
        "conversation": "## From Conversations",
        "email": "## From Emails",
        "manual": "## Manually Captured",
        "other": "## From Other Sources"
    }

    for source_type, task_list in by_source.items():
        if not task_list:
            continue

        lines.append(source_headers[source_type])
        lines.append("")

        for task in task_list:
            lines.append(f"- [ ] {task['title']} ({task['source_type']}: {task['source_id']})")
            if task['description']:
                lines.append(f"  - Description: {task['description']}")
            if task['source_context']:
                lines.append(f"  - Context: \"{task['source_context']}\"")

            # Show suggestions
            suggestions = []
            if task['suggested_domain']:
                suggestions.append(f"Domain: {task['suggested_domain']}")
            if task['suggested_project']:
                suggestions.append(f"Project: {task['suggested_project']}")
            if task['suggested_priority']:
                suggestions.append(f"Priority: {task['suggested_priority']}")

            if suggestions:
                lines.append(f"  - Suggested: {' | '.join(suggestions)}")

            lines.append(f"  - Staged ID: `{task['id']}`")
            lines.append("")

    return "\n".join(lines)


def write_review_file(for_date: Optional[date] = None) -> Path:
    """
    Write the review markdown to a file in the review directory.

    Args:
        for_date: Date for review (defaults to today)

    Returns:
        Path to the created review file
    """
    if for_date is None:
        for_date = date.today()

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"staged-tasks-review-{for_date.strftime('%Y-%m-%d')}.md"
    filepath = REVIEW_DIR / filename

    markdown = generate_review_markdown(for_date)

    with open(filepath, "w") as f:
        f.write(markdown)

    return filepath


def promote_staged_task(
    staged_id: int,
    domain: str,
    project: Optional[str],
    priority_bucket: str,
    due_at: Optional[str] = None,
    description: Optional[str] = None,
    plan_json: Optional[str] = None
) -> int:
    """
    Promote a staged task to the official task registry.

    This creates a real task in the tasks table and links the staged task to it.

    Args:
        staged_id: ID of the staged task to promote
        domain: Domain name for the new task (string, e.g., "Careerspan")
        project: Project name for the new task (string, optional)
        priority_bucket: Priority bucket (strategic, external, urgent, normal)
        due_at: Due date (ISO format string, optional)
        description: Override description (optional)
        plan_json: Plan JSON string (optional)

    Returns:
        task_id: ID of the newly created task
    """
    staged = get_staged_task_by_id(staged_id)
    if not staged:
        raise ValueError(f"Staged task {staged_id} not found")

    # Import here to avoid circular dependency
    from N5.task_system.task_registry import create_task

    task_id = create_task(
        title=staged["title"],
        domain=domain,
        project=project,
        description=description or staged["description"],
        priority_bucket=priority_bucket,
        source_type=staged["source_type"],
        source_id=staged["source_id"],
        due_at=due_at,
        plan_json=json.loads(plan_json) if plan_json else None
    )

    # Update staged task
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE staged_tasks
            SET status = 'promoted',
                promoted_task_id = ?,
                promoted_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (task_id, staged_id))
        conn.commit()

    return task_id


def dismiss_staged_task(staged_id: int, reason: str) -> None:
    """
    Dismiss a staged task (not a real task, but keep for audit trail).

    Args:
        staged_id: ID of the staged task to dismiss
        reason: Reason for dismissal
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE staged_tasks
            SET status = 'dismissed',
                dismissed_reason = ?,
                dismissed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (reason, staged_id))
        conn.commit()


def bulk_promote(
    staged_ids: List[int],
    defaults: Dict[str, Any]
) -> List[int]:
    """
    Promote multiple staged tasks with default values.

    Args:
        staged_ids: List of staged task IDs to promote
        defaults: Dict with default values:
            - domain: required (string, e.g., "Careerspan")
            - project: optional (string, e.g., "Partnerships")
            - priority_bucket: default "normal"
            - due_at: optional

    Returns:
        List of created task IDs
    """
    task_ids = []

    for staged_id in staged_ids:
        try:
            task_id = promote_staged_task(
                staged_id=staged_id,
                domain=defaults.get("domain"),
                project=defaults.get("project"),
                priority_bucket=defaults.get("priority_bucket", "normal"),
                due_at=defaults.get("due_at")
            )
            task_ids.append(task_id)
        except Exception as e:
            print(f"Failed to promote staged task {staged_id}: {e}")

    return task_ids


def bulk_dismiss(staged_ids: List[int], reason: str) -> int:
    """
    Dismiss multiple staged tasks with the same reason.

    Args:
        staged_ids: List of staged task IDs to dismiss
        reason: Reason for dismissal

    Returns:
        Number of tasks dismissed
    """
    count = 0
    for staged_id in staged_ids:
        try:
            dismiss_staged_task(staged_id, reason)
            count += 1
        except Exception as e:
            print(f"Failed to dismiss staged task {staged_id}: {e}")

    return count


def get_staged_tasks_by_source(source_type: str, source_id: str) -> List[Dict[str, Any]]:
    """
    Get all staged tasks from a specific source.

    Useful for checking if a meeting/conversation already has staged tasks.

    Args:
        source_type: Type of source (meeting, conversation, email, manual)
        source_id: ID of the source

    Returns:
        List of staged task dictionaries
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM staged_tasks
            WHERE source_type = ? AND source_id = ?
            ORDER BY captured_at DESC
        """, (source_type, source_id))
        return [dict(row) for row in cursor.fetchall()]


def cleanup_old_staged_tasks(days_old: int = 30) -> int:
    """
    Clean up old dismissed or promoted staged tasks.

    Args:
        days_old: Delete tasks older than this many days

    Returns:
        Number of tasks deleted
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM staged_tasks
            WHERE status IN ('dismissed', 'promoted')
            AND (
                (dismissed_at < datetime('now', '-' || ? || ' days'))
                OR (promoted_at < datetime('now', '-' || ? || ' days'))
            )
        """, (days_old, days_old))
        conn.commit()
        return cursor.rowcount


if __name__ == "__main__":
    # Test/demo mode
    print("Staging module loaded successfully")
    print(f"Database: {DB_PATH}")
    print(f"Review directory: {REVIEW_DIR}")
