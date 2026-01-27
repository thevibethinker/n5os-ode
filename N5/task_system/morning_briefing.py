#!/usr/bin/env python3
"""
Morning Briefing Module for Zo Task System

Generates daily task briefings for V, with calendar awareness and
capacity management. Handles task adjustments via SMS responses.

Usage:
    from N5.task_system.morning_briefing import (
        get_todays_tasks,
        check_calendar_blocks,
        generate_briefing_text,
        process_adjustment,
        lock_day_plan
    )
    
    briefing = generate_briefing_text()
"""

import sqlite3
import re
from datetime import datetime, time, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "tasks.db"

# Priority buckets and their order (higher = more important)
PRIORITY_ORDER = {
    "strategic": 1,
    "external": 2,
    "urgent": 3,
    "normal": 4
}

# Priority display mapping
PRIORITY_EMOJIS = {
    "strategic": "🔴",
    "external": "🟠",
    "urgent": "🟡",
    "normal": "⚪"
}

# Default capacity settings
DEFAULT_CAPACITY = 6  # tasks
MIN_CAPACITY = 3
MAX_CAPACITY =10


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_todays_tasks(
    days_ahead: int = 1,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get tasks due today or tomorrow, ordered by priority and age.
    
    Args:
        days_ahead: How many days ahead to include (default: 1)
        limit: Maximum number of tasks to return (capacity management)
    
    Returns:
        List of task dictionaries with metadata
    """
    conn = get_connection()
    try:
        query = """
            SELECT
                t.*,
                d.name AS domain_name,
                p.name AS project_name,
                CASE
                    WHEN t.due_at IS NULL THEN 9999
                    WHEN date(t.due_at) < date('now', 'localtime') THEN -1 * 
                        (julianday('now', 'localtime') - julianday(t.due_at))
                    ELSE 0
                END AS days_overdue
            FROM tasks t
            JOIN domains d ON t.domain_id = d.id
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.status IN ('pending', 'in_progress', 'blocked')
              AND t.archived = FALSE
              AND (
                t.due_at IS NULL
                OR date(t.due_at) <= date('now', 'localtime', '+' || ? || ' day')
              )
            ORDER BY
                CASE t.priority_bucket
                    WHEN 'strategic' THEN 1
                    WHEN 'external' THEN 2
                    WHEN 'urgent' THEN 3
                    WHEN 'normal' THEN 4
                    ELSE 5
                END,
                days_overdue DESC,
                t.created_at DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        rows = conn.execute(query, (days_ahead,)).fetchall()
        tasks = [dict(row) for row in rows]
        
        # Add computed fields
        for task in tasks:
            task["priority_emoji"] = PRIORITY_EMOJIS.get(task["priority_bucket"], "⚪")
            if task["due_at"]:
                due_date = datetime.fromisoformat(task["due_at"])
                task["due_formatted"] = due_date.strftime("%-I:%M %p")
                if due_date.date() < date.today():
                    task["is_overdue"] = True
                    days_overdue = (date.today() - due_date.date()).days
                    task["overdue_text"] = f"{days_overdue} days overdue"
                elif due_date.date() == date.today():
                    task["is_overdue"] = False
                    task["overdue_text"] = "due today"
                else:
                    task["is_overdue"] = False
                    task["overdue_text"] = f"due {due_date.strftime('%A')}"
            else:
                task["is_overdue"] = False
                task["overdue_text"] = "no due date"
        
        return tasks
        
    finally:
        conn.close()


def check_calendar_blocks() -> Dict[str, Any]:
    """
    Get today's meeting time blocks from Google Calendar.
    
    Returns:
        Dict with:
        - meeting_count: Number of meetings today
        - total_minutes: Total blocked time in minutes
        - meetings: List of meeting dicts (title, start, end, minutes)
        - available_hours: Available work hours (8 - meeting hours)
    """
    try:
        import os
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        
        # This would use proper OAuth credentials in production
        # For now, return empty structure to allow testing
        
        # Placeholder for calendar integration
        # In production, this would:
        # 1. Load OAuth credentials
        # 2. Call Calendar API for events today
        # 3. Calculate blocked time
        
        return {
            "meeting_count": 0,
            "total_minutes": 0,
            "meetings": [],
            "available_hours": 8.0,
            "note": "Calendar integration pending - OAuth setup required"
        }
        
    except Exception as e:
        # Fail gracefully if calendar not available
        return {
            "meeting_count": 0,
            "total_minutes": 0,
            "meetings": [],
            "available_hours": 8.0,
            "error": str(e)
        }


def calculate_realistic_capacity(
    tasks: List[Dict[str, Any]],
    calendar: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate realistic capacity based on tasks and calendar.
    
    Args:
        tasks: List of tasks for today
        calendar: Calendar info from check_calendar_blocks()
    
    Returns:
        Dict with capacity analysis
    """
    total_meeting_hours = calendar.get("total_minutes", 0) / 60
    available_hours = 8 - total_meeting_hours
    
    # Simple capacity heuristic: ~1 hour per task average
    # Adjust based on available time
    raw_capacity = int(available_hours * 0.8)  # 80% utilization target
    
    # Clamp to reasonable bounds
    capacity = max(MIN_CAPACITY, min(MAX_CAPACITY, raw_capacity))
    
    # Count overdue tasks (they should be prioritized)
    overdue_count = sum(1 for t in tasks if t.get("is_overdue"))
    
    return {
        "recommended_tasks": capacity,
        "available_hours": round(available_hours, 1),
        "meeting_hours": round(total_meeting_hours, 1),
        "overdue_count": overdue_count,
        "total_available": len(tasks)
    }


def generate_briefing_text(
    tasks: Optional[List[Dict[str, Any]]] = None,
    calendar: Optional[Dict[str, Any]] = None,
    capacity: Optional[int] = None
) -> str:
    """
    Generate the morning briefing SMS text.
    
    Args:
        tasks: List of tasks (defaults to get_todays_tasks())
        calendar: Calendar info (defaults to check_calendar_blocks())
        capacity: Override task limit
    
    Returns:
        Formatted briefing text
    """
    if tasks is None:
        tasks = get_todays_tasks()
    
    if calendar is None:
        calendar = check_calendar_blocks()
    
    # Group by priority bucket
    by_bucket: Dict[str, List[Dict]] = {
        "strategic": [],
        "external": [],
        "urgent": [],
        "normal": []
    }
    
    for task in tasks:
        bucket = task.get("priority_bucket", "normal")
        if bucket in by_bucket:
            by_bucket[bucket].append(task)
    
    # Calculate capacity
    cap_analysis = calculate_realistic_capacity(tasks, calendar)
    if capacity is None:
        capacity = cap_analysis["recommended_tasks"]
    
    # Build briefing text
    lines = [
        f"Morning, V. Here's your day ({date.today().strftime('%A, %-m/%d')}):",
        ""
    ]
    
    task_num = 1
    shown_count = 0
    
    # Show tasks by priority order
    for bucket in ["strategic", "external", "urgent", "normal"]:
        bucket_tasks = by_bucket[bucket]
        
        if not bucket_tasks:
            continue
        
        if shown_count > 0:
            lines.append("")
        
        bucket_emoji = PRIORITY_EMOJIS[bucket]
        lines.append(f"{bucket_emoji.upper()} {bucket.upper()}")
        
        for task in bucket_tasks:
            if shown_count >= capacity:
                break
            
            task_title = task["title"]
            overdue_note = ""
            if task.get("is_overdue"):
                overdue_note = f" ({task['overdue_text']})"
            
            lines.append(f"{task_num}. {task_title}{overdue_note}")
            
            task_num += 1
            shown_count += 1
        
        # Stop if we've shown enough
        if shown_count >= capacity:
            break
    
    lines.append("")
    
    # Summary stats
    if shown_count < len(tasks):
        lines.append(f"That's {shown_count} tasks ({len(tasks) - shown_count} more queued).")
    else:
        lines.append(f"That's {shown_count} tasks.")
    
    # Calendar info
    meeting_info = []
    if calendar.get("meeting_count", 0) > 0:
        meeting_count = calendar["meeting_count"]
        meeting_hours = calendar["total_minutes"] / 60
        meeting_info.append(f"{meeting_count} meetings ({meeting_hours:.1f} hrs)")
    
    if meeting_info:
        lines.append(f"You have {', '.join(meeting_info)}.")
    
    # Capacity guidance
    lines.append(f"Realistic capacity: {cap_analysis['available_hours']} hrs → {capacity} tasks.")
    lines.append("")
    
    lines.append("Reply with your plan or adjustments:")
    lines.append("  • 'push #2 to tomorrow'")
    lines.append("  • 'swap #1 and #3'")
    lines.append("  • 'add: review proposal'")
    lines.append("  • 'confirm' to lock the day")
    
    return "\n".join(lines)


def parse_adjustment(
    response: str,
    tasks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Parse V's adjustment response.
    
    Supported commands:
    - "push #N to tomorrow" - Move task to tomorrow
    - "push #N" - Same as above
    - "swap #A and #B" - Swap positions
    - "add: task title" - Add new task
    - "remove #N" - Remove from today's list
    - "confirm" - Lock the plan
    
    Args:
        response: User's SMS response
        tasks: Current task list
    
    Returns:
        Dict with:
        - command: The parsed command type
        - params: Command parameters
        - valid: Whether parsing succeeded
    """
    response = response.strip().lower()
    
    # Confirm command
    if response in ["confirm", "ok", "yes", "good", "looks good", "confirmed"]:
        return {
            "command": "confirm",
            "params": {},
            "valid": True
        }
    
    # Push command: "push #N to tomorrow" or just "push #N"
    push_match = re.match(r"push\s+#?(\d+)(?:\s+to\s+tomorrow)?", response)
    if push_match:
        task_num = int(push_match.group(1))
        if 1 <= task_num <= len(tasks):
            return {
                "command": "push",
                "params": {"task_num": task_num},
                "valid": True
            }
    
    # Swap command: "swap #A and #B"
    swap_match = re.match(r"swap\s+#?(\d+)\s+and\s+#?(\d+)", response)
    if swap_match:
        a = int(swap_match.group(1))
        b = int(swap_match.group(2))
        if 1 <= a <= len(tasks) and 1 <= b <= len(tasks):
            return {
                "command": "swap",
                "params": {"a": a, "b": b},
                "valid": True
            }
    
    # Remove command: "remove #N"
    remove_match = re.match(r"remove\s+#?(\d+)", response)
    if remove_match:
        task_num = int(remove_match.group(1))
        if 1 <= task_num <= len(tasks):
            return {
                "command": "remove",
                "params": {"task_num": task_num},
                "valid": True
            }
    
    # Add command: "add: task title"
    add_match = re.match(r"add:\s*(.+)", response)
    if add_match:
        task_title = add_match.group(1).strip()
        if len(task_title) > 0:
            return {
                "command": "add",
                "params": {"title": task_title},
                "valid": True
            }
    
    # Unknown command
    return {
        "command": "unknown",
        "params": {"raw": response},
        "valid": False
    }


def process_adjustment(
    response: str,
    tasks: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Process V's adjustment and return updated task list with message.
    
    Args:
        response: User's SMS response
        tasks: Current task list
    
    Returns:
        Tuple of (updated_tasks, status_message)
    """
    parsed = parse_adjustment(response, tasks)
    
    if not parsed["valid"]:
        return tasks, f"Couldn't understand that. Try: 'push #2', 'swap #1 and #3', 'add: new task', or 'confirm'"
    
    command = parsed["command"]
    params = parsed["params"]
    
    if command == "confirm":
        # No changes, just confirm
        return tasks, "Day plan locked! Got it."
    
    elif command == "push":
        # Push task to tomorrow (remove from list for today)
        task_num = params["task_num"] - 1  # Convert to 0-index
        task = tasks[task_num]
        # Update due date to tomorrow
        new_due = (date.today() + timedelta(days=1)).isoformat()
        
        # Update in database
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE tasks SET due_at = ? WHERE id = ?",
                (new_due, task["id"])
            )
            conn.commit()
        finally:
            conn.close()
        
        # Remove from list
        updated_tasks = tasks[:task_num] + tasks[task_num+1:]
        return updated_tasks, f"Pushed '{task['title']}' to tomorrow."
    
    elif command == "swap":
        # Swap two tasks
        a = params["a"] - 1
        b = params["b"] - 1
        
        updated_tasks = tasks.copy()
        updated_tasks[a], updated_tasks[b] = updated_tasks[b], updated_tasks[a]
        
        return updated_tasks, f"Swapped tasks #{params['a']} and #{params['b']}."
    
    elif command == "remove":
        # Remove from today (don't delete, just postpone)
        task_num = params["task_num"] - 1
        task = tasks[task_num]
        
        # Clear due date (no longer due today)
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE tasks SET due_at = NULL WHERE id = ?",
                (task["id"],)
            )
            conn.commit()
        finally:
            conn.close()
        
        updated_tasks = tasks[:task_num] + tasks[task_num+1:]
        return updated_tasks, f"Removed '{task['title']}' from today's list (not deleted)."
    
    elif command == "add":
        # Add new task
        new_title = params["title"]
        
        # Import here to avoid circular dependency
        from N5.task_system.task_registry import create_task
        
        task_id = create_task(
            title=new_title,
            domain="Zo",  # Default domain
            project="Daily",
            priority_bucket="urgent",  # Default to urgent for same-day adds
            due_at=datetime.now().isoformat(),
            source_type="manual"
        )
        
        # Get the new task
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT *, d.name AS domain_name FROM tasks t JOIN domains d ON t.domain_id = d.id WHERE t.id = ?",
                (task_id,)
            ).fetchone()
            new_task = dict(row)
            new_task["priority_emoji"] = PRIORITY_EMOJIS.get(new_task["priority_bucket"], "⚪")
            new_task["is_overdue"] = False
            new_task["overdue_text"] = "due today"
        finally:
            conn.close()
        
        # Add to list at the top (strategic priority)
        updated_tasks = [new_task] + tasks
        return updated_tasks, f"Added '{new_title}' to today's list."
    
    return tasks, "Something went wrong."


def lock_day_plan(tasks: List[Dict[str, Any]]) -> bool:
    """
    Lock the day's task plan by creating a baseline snapshot.
    
    This records the committed plan for accountability tracking.
    
    Args:
        tasks: The final task list for the day
    
    Returns:
        True if successful
    """
    conn = get_connection()
    try:
        # Check if day_plans table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='day_plans'"
        ).fetchone()
        
        if not cursor:
            # Create table
            conn.execute("""
                CREATE TABLE day_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_date TEXT UNIQUE NOT NULL,
                    task_ids TEXT NOT NULL,
                    total_tasks INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Record the plan
        task_ids = ",".join(str(t["id"]) for t in tasks)
        today = date.today().isoformat()
        
        conn.execute(
            """INSERT OR REPLACE INTO day_plans 
               (plan_date, task_ids, total_tasks, created_at, locked_at)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
            (today, task_ids, len(tasks))
        )
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error locking day plan: {e}")
        return False
    finally:
        conn.close()


def get_current_day_plan() -> Optional[Dict[str, Any]]:
    """
    Get the current locked day plan for today.
    
    Returns:
        Dict with plan details or None if no plan locked
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM day_plans WHERE plan_date = ?",
            (date.today().isoformat(),)
        ).fetchone()
        
        if row:
            plan = dict(row)
            # Parse task IDs
            task_ids = [int(tid) for tid in plan["task_ids"].split(",")]
            
            # Get task details
            placeholders = ",".join(["?"] * len(task_ids))
            rows = conn.execute(
                f"SELECT * FROM tasks WHERE id IN ({placeholders})",
                task_ids
            ).fetchall()
            
            plan["tasks"] = [dict(r) for r in rows]
            return plan
        
        return None
        
    finally:
        conn.close()


# Test/demo functions
if __name__ == "__main__":
    print("=== Morning Briefing Module ===\n")
    
    # Test getting tasks
    tasks = get_todays_tasks()
    print(f"Found {len(tasks)} tasks for today\n")
    
    # Test calendar
    calendar = check_calendar_blocks()
    print(f"Calendar: {calendar['meeting_count']} meetings, {calendar['available_hours']} hrs available\n")
    
    # Test briefing generation
    briefing = generate_briefing_text(tasks, calendar, capacity=5)
    print("=== Briefing ===")
    print(briefing)
    print("\n=== End ===")
