#!/usr/bin/env python3
"""
Zo Task Registry Module

Core interface for V's task management system.
Tasks are treated as "plans of action" with domain/project hierarchy,
latency tracking, and source linking to conversations/meetings.

Usage:
    import task_registry as tr
    
    # Create a task
    task_id = tr.create_task(
        title="Review client proposal",
        domain="Careerspan",
        project="Client Work",
        priority_bucket="strategic",
        source_type="conversation",
        source_id="con_xyz123"
    )
    
    # Get today's tasks
    today = tr.get_tasks_for_today()
    
    # Complete a task
    tr.complete_task(task_id)
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

# Constants
DB_PATH = Path(__file__).parent / "tasks.db"
STATUS_OPTIONS = ["pending", "in_progress", "blocked", "complete", "abandoned"]
PRIORITY_BUCKETS = ["strategic", "external", "urgent", "normal"]
PROJECT_TYPES = ["ephemeral", "permanent", "recurring"]
SOURCE_TYPES = ["conversation", "meeting", "manual", "email"]


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory for dict access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _log_event(conn: sqlite3.Connection, task_id: int, event_type: str, event_data: Optional[Dict] = None):
    """Log a task event."""
    conn.execute(
        """INSERT INTO task_events (task_id, event_type, event_data, timestamp)
           VALUES (?, ?, ?, ?)""",
        (task_id, event_type, json.dumps(event_data) if event_data else None, datetime.now().isoformat())
    )


def create_task(
    title: str,
    domain: str,
    description: Optional[str] = None,
    project: Optional[str] = None,
    priority_bucket: str = "normal",
    source_type: str = "manual",
    source_id: Optional[str] = None,
    due_at: Optional[str] = None,
    estimated_minutes: Optional[int] = None,
    parent_task_id: Optional[int] = None,
    plan_json: Optional[Dict] = None
) -> int:
    """
    Create a new task.
    
    Args:
        title: Task title
        domain: Domain name (will create if doesn't exist)
        description: Optional description
        project: Optional project name (will create if doesn't exist)
        priority_bucket: One of 'strategic', 'external', 'urgent', 'normal'
        source_type: Where this task came from
        source_id: Source identifier (conversation_id, meeting_id, etc.)
        due_at: ISO format datetime or None
        estimated_minutes: Time estimate in minutes
        parent_task_id: Parent task for subtasks
        plan_json: Plan of action data
    
    Returns:
        Task ID
    """
    conn = get_connection()
    try:
        # Validate inputs
        if priority_bucket not in PRIORITY_BUCKETS:
            raise ValueError(f"priority_bucket must be one of {PRIORITY_BUCKETS}")
        if source_type not in SOURCE_TYPES:
            raise ValueError(f"source_type must be one of {SOURCE_TYPES}")
        
        # Get or create domain
        domain_row = conn.execute("SELECT id FROM domains WHERE name = ?", (domain,)).fetchone()
        if not domain_row:
            cursor = conn.execute(
                "INSERT INTO domains (name, description) VALUES (?, ?)",
                (domain, f"Domain created from task: {title}")
            )
            domain_id = cursor.lastrowid
        else:
            domain_id = domain_row["id"]
        
        # Get or create project if specified
        project_id = None
        if project:
            project_row = conn.execute(
                "SELECT id FROM projects WHERE domain_id = ? AND name = ?",
                (domain_id, project)
            ).fetchone()
            if not project_row:
                cursor = conn.execute(
                    """INSERT INTO projects (domain_id, name, description, project_type)
                       VALUES (?, ?, ?, ?)""",
                    (domain_id, project, f"Project created from task: {title}", "ephemeral")
                )
                project_id = cursor.lastrowid
            else:
                project_id = project_row["id"]
        
        # Insert task
        cursor = conn.execute(
            """INSERT INTO tasks (title, description, domain_id, project_id, status,
               priority_bucket, source_type, source_id, due_at, estimated_minutes,
               parent_task_id, plan_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                title, description, domain_id, project_id, "pending",
                priority_bucket, source_type, source_id, due_at,
                estimated_minutes, parent_task_id,
                json.dumps(plan_json) if plan_json else None
            )
        )
        task_id = cursor.lastrowid
        
        # Log creation event
        _log_event(conn, task_id, "created", {"title": title, "source_type": source_type, "source_id": source_id})
        
        conn.commit()
        return task_id
        
    finally:
        conn.close()


def update_task(task_id: int, **fields) -> bool:
    """
    Update task fields.
    
    Args:
        task_id: Task to update
        **fields: Fields to update (title, description, status, priority_bucket, etc.)
    
    Returns:
        True if updated, False if not found
    """
    if not fields:
        return False
    
    conn = get_connection()
    try:
        # Build update query dynamically
        valid_fields = {k: v for k, v in fields.items() if v is not None}
        if not valid_fields:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in valid_fields.keys()])
        values = list(valid_fields.values()) + [task_id]
        
        cursor = conn.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ?",
            values
        )
        
        if cursor.rowcount > 0:
            # Log update event
            _log_event(conn, task_id, "updated", {"fields": list(valid_fields.keys())})
            conn.commit()
            return True
        return False
        
    finally:
        conn.close()


def complete_task(task_id: int, actual_minutes: Optional[int] = None) -> bool:
    """
    Mark a task as complete.
    
    Args:
        task_id: Task to complete
        actual_minutes: Actual time spent (optional)
    
    Returns:
        True if completed, False if not found
    """
    conn = get_connection()
    try:
        # Get task info first for latency tracking
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not task:
            return False
        
        now = datetime.now().isoformat()
        
        # Update task
        update_fields = {
            "status": "complete",
            "completed_at": now
        }
        if actual_minutes is not None:
            update_fields["actual_minutes"] = actual_minutes
        
        cursor = conn.execute(
            """UPDATE tasks SET status = ?, completed_at = ?, actual_minutes = ?
               WHERE id = ?""",
            ("complete", now, actual_minutes, task_id)
        )
        
        if cursor.rowcount > 0:
            # Log completion event
            event_data = {
                "due_at": task["due_at"],
                "completed_at": now
            }
            if actual_minutes:
                event_data["actual_minutes"] = actual_minutes
            
            _log_event(conn, task_id, "completed", event_data)
            conn.commit()
            return True
        return False
        
    finally:
        conn.close()


def get_tasks_for_today(days_ahead: int = 1) -> List[Dict]:
    """
    Get tasks due today or soon (pending, in_progress, blocked).
    
    Args:
        days_ahead: How many days ahead to include (default: 1 = today + tomorrow)
    
    Returns:
        List of task dictionaries
    """
    conn = get_connection()
    try:
        query = """
            SELECT
                t.*,
                d.name AS domain_name,
                p.name AS project_name
            FROM tasks t
            JOIN domains d ON t.domain_id = d.id
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.status IN ('pending', 'in_progress', 'blocked')
              AND t.archived = FALSE
              AND (
                t.due_at IS NULL
                OR date(t.due_at) >= date('now', 'localtime')
                OR date(t.due_at) <= date('now', 'localtime', '+' || ? || ' day')
              )
            ORDER BY
                CASE t.priority_bucket
                    WHEN 'urgent' THEN 1
                    WHEN 'strategic' THEN 2
                    WHEN 'external' THEN 3
                    WHEN 'normal' THEN 4
                    ELSE 5
                END,
                t.due_at ASC,
                t.created_at ASC
        """
        
        rows = conn.execute(query, (days_ahead,)).fetchall()
        return [dict(row) for row in rows]
        
    finally:
        conn.close()


def get_task_by_source(source_type: str, source_id: str) -> Optional[Dict]:
    """
    Find a task by its source reference.
    
    Args:
        source_type: Type of source (conversation, meeting, email, manual)
        source_id: Source identifier
    
    Returns:
        Task dict or None if not found
    """
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT t.*, d.name AS domain_name, p.name AS project_name
               FROM tasks t
               JOIN domains d ON t.domain_id = d.id
               LEFT JOIN projects p ON t.project_id = p.id
               WHERE t.source_type = ? AND t.source_id = ?""",
            (source_type, source_id)
        ).fetchone()
        
        return dict(row) if row else None
        
    finally:
        conn.close()


def calculate_latency_stats(
    days_back: int = 30,
    domain: Optional[str] = None,
    project: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate latency statistics for completed tasks.
    
    Args:
        days_back: How many days back to analyze
        domain: Filter by domain (optional)
        project: Filter by project (optional)
    
    Returns:
        Dictionary with stats:
        - avg_hours_overdue: Average hours past due date
        - avg_hours_to_complete: Average hours from creation to completion
        - total_tasks: Number of tasks analyzed
        - overdue_count: Tasks completed past due date
        - on_time_count: Tasks completed on or before due date
    """
    conn = get_connection()
    try:
        # Build query with filters
        where_clauses = ["t.status = 'complete'", "t.completed_at IS NOT NULL"]
        params = []
        
        if days_back:
            where_clauses.append("t.completed_at >= datetime('now', ? || ' days')")
            params.append(f"-{days_back}")
        
        if domain:
            where_clauses.append("d.name = ?")
            params.append(domain)
        
        if project:
            where_clauses.append("p.name = ?")
            params.append(project)
        
        where_sql = " AND ".join(where_clauses)
        
        query = f"""
            SELECT
                t.due_at,
                t.completed_at,
                t.created_at,
                julianday(t.completed_at) - julianday(t.due_at) AS days_overdue,
                julianday(t.completed_at) - julianday(t.created_at) AS days_to_complete
            FROM tasks t
            JOIN domains d ON t.domain_id = d.id
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE {where_sql}
        """
        
        rows = conn.execute(query, params).fetchall()
        
        if not rows:
            return {
                "avg_hours_overdue": None,
                "avg_hours_to_complete": None,
                "total_tasks": 0,
                "overdue_count": 0,
                "on_time_count": 0
            }
        
        hours_overdue = [r["days_overdue"] * 24 if r["due_at"] and r["days_overdue"] > 0 else 0 for r in rows]
        hours_to_complete = [r["days_to_complete"] * 24 for r in rows if r["days_to_complete"]]
        overdue_count = sum(1 for h in hours_overdue if h > 0)
        
        return {
            "avg_hours_overdue": sum(hours_overdue) / len(hours_overdue) if hours_overdue else 0,
            "avg_hours_to_complete": sum(hours_to_complete) / len(hours_to_complete) if hours_to_complete else None,
            "total_tasks": len(rows),
            "overdue_count": overdue_count,
            "on_time_count": len(rows) - overdue_count,
            "days_analyzed": days_back
        }
        
    finally:
        conn.close()


def get_task_by_id(task_id: int) -> Optional[Dict]:
    """Get a single task by ID with full details."""
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT t.*, d.name AS domain_name, p.name AS project_name
               FROM tasks t
               JOIN domains d ON t.domain_id = d.id
               LEFT JOIN projects p ON t.project_id = p.id
               WHERE t.id = ?""",
            (task_id,)
        ).fetchone()
        
        return dict(row) if row else None
        
    finally:
        conn.close()


def get_task_history(task_id: int) -> List[Dict]:
    """Get event history for a task."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM task_events WHERE task_id = ? ORDER BY timestamp ASC",
            (task_id,)
        ).fetchall()
        
        return [dict(row) for row in rows]
        
    finally:
        conn.close()


def list_domains() -> List[Dict]:
    """List all domains."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM domains WHERE archived = FALSE ORDER BY name").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def list_projects(domain: Optional[str] = None) -> List[Dict]:
    """List projects, optionally filtered by domain."""
    conn = get_connection()
    try:
        if domain:
            rows = conn.execute(
                """SELECT p.*, d.name AS domain_name
                   FROM projects p
                   JOIN domains d ON p.domain_id = d.id
                   WHERE d.name = ? AND p.archived = FALSE
                   ORDER BY p.name""",
                (domain,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT p.*, d.name AS domain_name
                   FROM projects p
                   JOIN domains d ON p.domain_id = d.id
                   WHERE p.archived = FALSE
                   ORDER BY d.name, p.name"""
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    def test_basic_operations():
        """Run basic tests."""
        print("Testing task registry...")
        
        # Create domains and tasks
        task1_id = create_task(
            title="Test task 1",
            domain="Personal",
            project="Health",
            priority_bucket="normal",
            source_type="manual",
            description="First test task"
        )
        print(f"✓ Created task {task1_id}")
        
        task2_id = create_task(
            title="Urgent task",
            domain="Zo",
            project="System Maintenance",
            priority_bucket="urgent",
            source_type="conversation",
            source_id="con_test123",
            due_at=(datetime.now() + timedelta(hours=2)).isoformat()
        )
        print(f"✓ Created urgent task {task2_id}")
        
        task3_id = create_task(
            title="Strategic task",
            domain="Careerspan",
            priority_bucket="strategic",
            source_type="manual",
            estimated_minutes=30
        )
        print(f"✓ Created strategic task {task3_id}")
        
        # Test retrieval
        tasks = get_tasks_for_today()
        print(f"✓ Found {len(tasks)} tasks for today")
        
        # Test source lookup
        source_task = get_task_by_source("conversation", "con_test123")
        print(f"✓ Found task by source: {source_task['title']}")
        
        # Test completion
        complete_task(task1_id, actual_minutes=15)
        print(f"✓ Completed task {task1_id}")
        
        # Test latency
        stats = calculate_latency_stats(days_back=365)
        print(f"✓ Latency stats: {stats}")
        
        print("\nAll tests passed! ✓")
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_basic_operations()
