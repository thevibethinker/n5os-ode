#!/usr/bin/env python3
"""Email intake handler for Pulse v2 tasks and interview responses."""

import json
import argparse
import subprocess
import re
from pathlib import Path

def run_cmd(cmd: list) -> dict:
    """Run a command and return JSON output."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return {"error": result.stderr or result.stdout}

def extract_task_from_subject(subject: str) -> str | None:
    """Check if subject indicates a new task."""
    task_patterns = [
        r'^task:\s*(.+)$',
        r'^new task:\s*(.+)$',
        r'^pulse task:\s*(.+)$',
    ]
    
    for pattern in task_patterns:
        match = re.match(pattern, subject.lower())
        if match:
            return match.group(1).strip()
    
    return None

def handle_email(subject: str, body: str) -> dict:
    """
    Handle incoming email.
    
    Conventions:
    - Subject "Task: <description>" → Create new task
    - Subject with #task-<slug> → Route body to that interview
    - Otherwise → Route based on open interviews
    """
    # Check for explicit task creation
    task_description = extract_task_from_subject(subject)
    if task_description:
        # Classify using body for more context
        full_description = f"{task_description}. {body[:200]}" if body else task_description
        classification = run_cmd(["python3", "N5/pulse/classifier.py", full_description])
        task_type = classification.get("type", "hybrid")
        
        # Add to queue
        result = run_cmd([
            "python3", "N5/pulse/queue_manager.py", "add",
            task_description,
            "--type", task_type,
            "--channel", "email",
            "--message", body[:500] if body else task_description
        ])
        
        if result.get("success"):
            task = result["task"]
            return {
                "action": "task_created",
                "task": task,
                "response": f"Task created: {task['title']} ({task['type']})"
            }
        else:
            return {"action": "error", "response": f"Failed: {result.get('error')}"}
    
    # Check for explicit tag in subject or body
    combined = f"{subject} {body}"
    route_result = run_cmd(["python3", "N5/pulse/fragment_router.py", combined, "--channel", "email"])
    
    if route_result["action"] == "route_to_interview":
        task_id = route_result["task_id"]
        # Use cleaned content from router (tag already stripped)
        content = route_result["content"]
        run_cmd([
            "python3", "N5/pulse/interview_manager.py", "add",
            task_id,
            "--channel", "email",
            "--content", content
        ])
        return {
            "action": "fragment_added",
            "task_id": task_id,
            "response": f"Added to interview: {task_id}"
        }
    
    elif route_result["action"] == "clarify":
        return {
            "action": "clarify",
            "open_interviews": route_result["open_interviews"],
            "response": "Multiple open interviews. Use #task-<slug> in subject to specify."
        }
    
    elif route_result["action"] == "new_task":
        return {
            "action": "suggestion",
            "response": "No open interviews. Use subject 'Task: <description>' to create one."
        }
    
    return {"action": "unknown"}

def main():
    parser = argparse.ArgumentParser(description="Email Intake Handler")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", default="", help="Email body")
    
    args = parser.parse_args()
    result = handle_email(args.subject, args.body)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
