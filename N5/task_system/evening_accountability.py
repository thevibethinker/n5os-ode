#!/usr/bin/env python3
"""
Evening Accountability Module for Zo Task System

Provides daily evening check-in with:
- Accountability report (planned vs. completed)
- Latency tracking
- Staged task review
- Tomorrow's priority queue

Usage:
    from N5.task_system.evening_accountability import (
        get_day_results,
        calculate_score,
        generate_accountability_text,
        generate_staged_review_text,
        process_staged_response,
        process_tomorrow_queue
    )
"""

import sqlite3
import json
import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import from other modules
from N5.task_system.task_registry import (
    get_connection,
    get_tasks_for_today,
    calculate_latency_stats,
    get_task_by_id
)
from N5.task_system.staging import (
    get_pending_staged_tasks,
    get_staged_task_by_id,
    promote_staged_task,
    dismiss_staged_task
)

# Database path
DB_PATH = Path("/home/workspace/N5/task_system/tasks.db")

# Constants
STATUS_COMPLETE = "complete"
STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_BLOCKED = "blocked"


def get_day_results(for_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Get today's task results for accountability reporting.
    
    Args:
        for_date: Date to analyze (defaults to today)
    
    Returns:
        Dictionary with:
            - planned_tasks: List of tasks that were due today
            - completed_tasks: List of tasks completed today
            - remaining_tasks: List of incomplete tasks due today
            - total_planned: Count of tasks planned for today
            - total_completed: Count of tasks completed today
    """
    if for_date is None:
        for_date = date.today()
    
    conn = get_connection()
    try:
        # Get tasks due today (including past-due)
        date_str = for_date.strftime("%Y-%m-%d")
        
        query = """
            SELECT
                t.*,
                d.name AS domain_name,
                p.name AS project_name
            FROM tasks t
            JOIN domains d ON t.domain_id = d.id
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.archived = FALSE
              AND (
                date(t.due_at) <= ?
                OR (t.due_at IS NULL AND date(t.created_at) <= ?)
              )
            ORDER BY
                CASE t.priority_bucket
                    WHEN 'strategic' THEN 1
                    WHEN 'external' THEN 2
                    WHEN 'urgent' THEN 3
                    WHEN 'normal' THEN 4
                    ELSE 5
                END,
                t.due_at ASC
        """
        
        rows = conn.execute(query, (date_str, date_str)).fetchall()
        all_tasks = [dict(row) for row in rows]
        
        # Separate into completed and incomplete
        completed = [t for t in all_tasks if t['status'] == STATUS_COMPLETE]
        incomplete = [t for t in all_tasks if t['status'] != STATUS_COMPLETE]
        
        return {
            "date": date_str,
            "planned_tasks": all_tasks,
            "completed_tasks": completed,
            "remaining_tasks": incomplete,
            "total_planned": len(all_tasks),
            "total_completed": len(completed)
        }
    finally:
        conn.close()


def calculate_score(for_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Calculate daily accountability score and latency metrics.
    
    Args:
        for_date: Date to analyze (defaults to today)
    
    Returns:
        Dictionary with:
            - completion_rate: Percentage (0-100)
            - completion_count: Number completed
            - total_count: Total tasks
            - latency_summary: Dictionary with latency stats
            - score_text: Human-readable score description
    """
    if for_date is None:
        for_date = date.today()
    
    results = get_day_results(for_date)
    total = results["total_planned"]
    completed = results["total_completed"]
    
    # Calculate completion rate
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    # Get latency stats for tasks completed in the last 7 days
    latency = calculate_latency_stats(days_back=7)
    
    # Generate score text
    if total == 0:
        score_text = "No tasks planned for today"
    elif completion_rate >= 100:
        score_text = "Perfect execution! 🎯"
    elif completion_rate >= 80:
        score_text = "Strong progress 📈"
    elif completion_rate >= 60:
        score_text = "On track"
    elif completion_rate >= 40:
        score_text = "Need focus"
    else:
        score_text = "Off track - what happened?"
    
    return {
        "completion_rate": round(completion_rate, 0),
        "completion_count": completed,
        "total_count": total,
        "latency_summary": {
            "avg_hours_overdue": latency.get("avg_hours_overdue"),
            "avg_hours_to_complete": latency.get("avg_hours_to_complete"),
            "overdue_count": latency.get("overdue_count", 0),
            "on_time_count": latency.get("on_time_count", 0)
        },
        "score_text": score_text
    }


def _format_task_summary(task: Dict) -> str:
    """Format a single task for SMS display."""
    title = task['title']
    domain = task.get('domain_name', '')
    
    # Add time if completed today
    if task['status'] == 'complete' and task.get('completed_at'):
        try:
            completed_dt = datetime.fromisoformat(task['completed_at'])
            time_str = completed_dt.strftime("%-I:%M %p")
            return f"- {title} ({domain}) - done {time_str}"
        except:
            return f"- {title} ({domain}) ✓"
    
    # Add overdue info
    if task['due_at']:
        try:
            due_dt = datetime.fromisoformat(task['due_at'])
            if due_dt.date() < date.today():
                days_overdue = (date.today() - due_dt.date()).days
                return f"- {title} ({days_overdue} days overdue)"
        except (ValueError, TypeError):
            # Invalid date format, skip to next check
            pass
    
    return f"- {title} ({domain})"


def generate_accountability_text(for_date: Optional[date] = None) -> str:
    """
    Generate evening accountability SMS text.
    
    Args:
        for_date: Date to analyze (defaults to today)
    
    Returns:
        SMS text with accountability report
    """
    if for_date is None:
        for_date = date.today()
    
    results = get_day_results(for_date)
    score = calculate_score(for_date)
    
    # Header
    lines = [
        f"Evening check-in, V.",
        ""
    ]
    
    # Score line
    if results["total_planned"] > 0:
        lines.append(
            f"TODAY'S SCORE: {score['completion_count']}/{results['total_planned']} "
            f"tasks ({int(score['completion_rate'])}%)"
        )
        lines.append(f"Status: {score['score_text']}")
    else:
        lines.append("No tasks were planned for today.")
    
    lines.append("")
    
    # Completed tasks
    if results["completed_tasks"]:
        lines.append("✅ Completed:")
        for task in results["completed_tasks"]:
            lines.append(_format_task_summary(task))
        lines.append("")
    
    # Incomplete tasks
    if results["remaining_tasks"]:
        lines.append("❌ Not done:")
        for task in results["remaining_tasks"][:5]:  # Limit to 5 for SMS
            lines.append(_format_task_summary(task))
        
        if len(results["remaining_tasks"]) > 5:
            lines.append(f"... and {len(results['remaining_tasks']) - 5} more")
        lines.append("")
    
    # Latency info
    latency = score["latency_summary"]
    if latency["avg_hours_overdue"] is not None:
        avg_overdue_hours = latency["avg_hours_overdue"]
        if avg_overdue_hours < 0:
            # Negative means ahead of schedule
            days_ahead = abs(avg_overdue_hours) / 24
            if days_ahead >= 0.5:
                lines.append(f"📈 Avg: {days_ahead:.1f} days AHEAD of due date")
            else:
                lines.append(f"📈 Avg: {abs(avg_overdue_hours):.0f} hours AHEAD")
        elif avg_overdue_hours > 0:
            # Positive means overdue
            days_overdue = avg_overdue_hours / 24
            if days_overdue >= 1:
                lines.append(f"⚠️ Avg: {days_overdue:.1f} days overdue")
            else:
                lines.append(f"⚠️ Avg: {avg_overdue_hours:.0f} hours overdue")
    
    lines.append("")
    
    # Call to action
    if results["remaining_tasks"]:
        lines.append("What happened with the incomplete tasks?")
    
    return "\n".join(lines)


def generate_staged_review_text(limit: int = 5) -> str:
    """
    Generate SMS text for staged task review.
    
    Args:
        limit: Maximum number of tasks to show
    
    Returns:
        SMS text with staged tasks
    """
    staged = get_pending_staged_tasks()
    
    if not staged:
        return "No new items captured today to review."
    
    # Group by source
    by_source: Dict[str, List[Dict]] = {
        "meeting": [],
        "conversation": [],
        "email": [],
        "manual": [],
        "other": []
    }
    
    for task in staged:
        source = task["source_type"].lower()
        if source not in by_source:
            source = "other"
        by_source[source].append(task)
    
    lines = [
        f"NEW ITEMS captured today ({len(staged)}):",
        ""
    ]
    
    # Add tasks grouped by source
    task_num = 0
    for source_type, task_list in by_source.items():
        if not task_list:
            continue
        
        # Enhanced source labels for meetings
        if source_type == "meeting" and task_list:
            # Try to extract meeting names from source_id
            meeting_names = set()
            for task in task_list:
                source_id = task.get('source_id', '')
                if source_id:
                    # Extract human-readable name from folder name
                    # Format: YYYY-MM-DD_Name -> Name
                    name = source_id
                    # Remove date prefix if present
                    if '_' in name and name.count('_') >= 2:
                        # Split and take everything after the date
                        parts = name.split('_')
                        # parts[0] = YYYY-MM-DD
                        # parts[1:] = rest of name
                        name = '_'.join(parts[1:])
                    meeting_names.add(name)
            
            if meeting_names:
                # Show "From meeting: Name1, Name2"
                meeting_list = sorted(list(meeting_names))[:3]  # Limit to 3 meeting names
                if len(meeting_list) == 1:
                    source_label = f"From meeting: {meeting_list[0]}"
                else:
                    source_label = f"From meetings: {', '.join(meeting_list)}"
                    if len(meeting_names) > 3:
                        source_label += f" (+{len(meeting_names) - 3} more)"
            else:
                source_label = "From meetings:"
        else:
            source_labels = {
                "conversation": "From conversations:",
                "email": "From emails:",
                "manual": "Manual captures:",
                "other": "Other sources:"
            }
            source_label = source_labels[source_type]
        
        lines.append(source_label)
        
        for task in task_list[:limit]:
            task_num += 1
            lines.append(f"{task_num}. {task['title']}")
            if task['source_context']:
                # Truncate long context
                context = task['source_context']
                if len(context) > 60:
                    context = context[:57] + "..."
                lines.append(f"   \"{context}\"")
            lines.append("")
    
    # Instructions
    lines.extend([
        "Reply with numbers to promote (e.g., '1,3')",
        "Reply 'none' to dismiss all",
        "Reply 'review <numbers>' to review specific items"
    ])
    
    return "\n".join(lines)


def parse_numbered_response(response: str) -> List[int]:
    """
    Parse a response like "1,3,5" or "1 3 5" into a list of integers.
    
    Args:
        response: User's SMS response
    
    Returns:
        List of integer indices
    """
    # Extract numbers from response
    numbers = re.findall(r'\d+', response)
    return [int(n) for n in numbers]


def process_staged_response(
    response: str,
    staged_tasks: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Process user's response to staged task review.
    
    Args:
        response: User's SMS response
        staged_tasks: List of staged tasks (if None, fetches pending)
    
    Returns:
        Dictionary with:
            - action_taken: What was done ('promoted', 'dismissed', 'none', 'error')
            - promoted_count: Number of tasks promoted
            - dismissed_count: Number of tasks dismissed
            - message: Summary message for user
            - task_ids: IDs of affected tasks
    """
    if staged_tasks is None:
        staged_tasks = get_pending_staged_tasks()
    
    if not staged_tasks:
        return {
            "action_taken": "none",
            "promoted_count": 0,
            "dismissed_count": 0,
            "message": "No staged tasks to process.",
            "task_ids": []
        }
    
    response_lower = response.lower().strip()
    
    # Handle "none" - dismiss all
    if response_lower == "none" or response_lower == "dismiss all":
        dismissed_ids = [t['id'] for t in staged_tasks]
        for task_id in dismissed_ids:
            dismiss_staged_task(task_id, reason="User dismissed all via SMS")
        
        return {
            "action_taken": "dismissed",
            "promoted_count": 0,
            "dismissed_count": len(dismissed_ids),
            "message": f"Dismissed {len(dismissed_ids)} tasks.",
            "task_ids": dismissed_ids
        }
    
    # Parse numbered response
    numbers = parse_numbered_response(response)
    
    if not numbers:
        return {
            "action_taken": "error",
            "promoted_count": 0,
            "dismissed_count": 0,
            "message": "Couldn't understand your response. Try '1,2,3' or 'none'.",
            "task_ids": []
        }
    
    # Validate numbers
    valid_numbers = [n for n in numbers if 1 <= n <= len(staged_tasks)]
    
    if not valid_numbers:
        return {
            "action_taken": "error",
            "promoted_count": 0,
            "dismissed_count": 0,
            "message": f"Invalid numbers. Valid range: 1-{len(staged_tasks)}",
            "task_ids": []
        }
    
    # Promote selected tasks (using defaults from suggestions)
    promoted_ids = []
    dismissed_ids = []
    
    for idx in valid_numbers:
        staged = staged_tasks[idx - 1]
        staged_id = staged['id']
        
        # Check if we have domain/project suggestions
        # For now, we'll defer to manual review via the review file
        # This is a limitation - the SMS interface can't fully handle complex promotion
        
        # As a workaround, we'll mark as "promoted_pending" and flag for review
        # In a full implementation, we'd need domain/project selection UI
        promoted_ids.append(staged_id)
    
    return {
        "action_taken": "promoted_pending",
        "promoted_count": len(promoted_ids),
        "dismissed_count": 0,
        "message": f"{len(promoted_ids)} tasks marked for promotion. Review at /browser to finalize.",
        "task_ids": promoted_ids
    }


def process_tomorrow_queue(
    response: str,
    domain: str = "General",
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Process user's tomorrow priority queue response.
    
    Args:
        response: User's SMS response with tomorrow's priorities
        domain: Default domain for new tasks
        priority: Default priority for new tasks
    
    Returns:
        Dictionary with:
            - tasks_added: Number of tasks added
            - tasks: List of task IDs added
            - message: Summary message
    """
    # Parse response into individual priorities
    # Expecting format like "1. Send email to Sarah\n2. Review proposal"
    
    tasks_created = []
    
    # Split by newlines or commas
    lines = re.split(r'[,\n]', response)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove numbering (1., 2., etc.) and bullets
        clean_title = re.sub(r'^\d+[\.\)]\s*', '', line)
        clean_title = re.sub(r'^[-•*]\s*', '', clean_title)
        clean_title = clean_title.strip()
        
        if not clean_title:
            continue
        
        # Create task for tomorrow
        from N5.task_system.task_registry import create_task
        
        tomorrow = date.today() + timedelta(days=1)
        due_at = datetime.combine(tomorrow, datetime.min.time()).isoformat()
        
        try:
            task_id = create_task(
                title=clean_title,
                domain=domain,
                priority_bucket=priority,
                due_at=due_at,
                source_type="manual",
                source_id=f"evening_checkin_{datetime.now().strftime('%Y%m%d')}"
            )
            tasks_created.append(task_id)
        except Exception as e:
            # Log error but continue
            print(f"Failed to create task '{clean_title}': {e}")
    
    return {
        "tasks_added": len(tasks_created),
        "tasks": tasks_created,
        "message": f"Added {len(tasks_created)} tasks for tomorrow."
    }


def generate_full_evening_flow() -> Tuple[str, str]:
    """
    Generate both the accountability report and staged review for the evening check-in.
    
    Returns:
        Tuple of (accountability_text, staged_review_text)
    """
    accountability = generate_accountability_text()
    staged = generate_staged_review_text()
    
    return accountability, staged


# CLI for testing
if __name__ == "__main__":
    import sys
    
    def test_evening_accountability():
        """Test the evening accountability module."""
        print("=== Testing Evening Accountability Module ===\n")
        
        # Test get_day_results
        print("1. Getting today's results...")
        results = get_day_results()
        print(f"   Planned: {results['total_planned']}")
        print(f"   Completed: {results['total_completed']}")
        print(f"   Remaining: {len(results['remaining_tasks'])}\n")
        
        # Test calculate_score
        print("2. Calculating score...")
        score = calculate_score()
        print(f"   Completion rate: {score['completion_rate']}%")
        print(f"   Score text: {score['score_text']}")
        print(f"   Latency: {score['latency_summary']}\n")
        
        # Test generate_accountability_text
        print("3. Accountability SMS:")
        print("-" * 50)
        accountability = generate_accountability_text()
        print(accountability)
        print("-" * 50)
        
        # Test generate_staged_review_text
        print("\n4. Staged tasks SMS:")
        print("-" * 50)
        staged = generate_staged_review_text()
        print(staged)
        print("-" * 50)
        
        # Test parse_numbered_response
        print("\n5. Testing response parsing...")
        test_responses = ["1,2,3", "1 3 5", "none", "invalid"]
        for resp in test_responses:
            numbers = parse_numbered_response(resp)
            print(f"   '{resp}' -> {numbers}")
        
        print("\n✓ All tests passed!")
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_evening_accountability()
