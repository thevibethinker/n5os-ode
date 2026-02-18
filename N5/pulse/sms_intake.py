#!/usr/bin/env python3
"""SMS intake handler for Pulse v2 tasks and interview responses."""

import json
import argparse
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime

PULSE_DIR = Path(__file__).parent
TAG_PATTERN = re.compile(r'^#task-(\S+)\s*(.*)', re.IGNORECASE | re.DOTALL)


def run_cmd(cmd: list) -> dict:
    """Run a command and return JSON output."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return {"error": result.stderr or result.stdout}


def parse_message(message: str) -> dict:
    """Parse SMS message for commands and tags."""
    message = message.strip()
    
    # Priority 1: Check for explicit task tag
    tag_match = TAG_PATTERN.match(message)
    if tag_match:
        task_slug = tag_match.group(1)
        content = tag_match.group(2).strip()
        return {
            "type": "interview_response",
            "task_slug": task_slug,
            "content": content,
            "tagged": True
        }
    
    # Priority 2: Existing command parsing
    lower = message.lower()
    
    if lower.startswith("n5 task "):
        description = message[8:].strip()
        return {"type": "new_task", "description": description}
    
    if lower == "n5 tasks":
        return {"type": "list_tasks"}
    
    if lower.startswith("n5 prioritize "):
        slug = message[14:].strip()
        return {"type": "prioritize", "slug": slug}
    
    if lower == "teach":
        return {"type": "teach"}
    
    if lower.startswith("absorbed:"):
        term = message[9:].strip()
        return {"type": "absorbed", "term": term}
    
    # Priority 3: Check if it could be an interview response (untagged)
    # Route through fragment_router
    return {
        "type": "potential_interview_response",
        "content": message,
        "tagged": False
    }


def route_to_interview(task_slug: str, content: str, channel: str) -> dict:
    """Route content to specific interview."""
    result = subprocess.run([
        "python3", str(Path(__file__).parent / "interview_manager.py"),
        "add", task_slug, "--channel", channel, "--content", content
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return {"success": True, "routed_to": task_slug, "message": f"Added to interview for {task_slug}"}
    return {"success": False, "error": result.stderr or result.stdout}


def handle_new_task(description: str) -> dict:
    """Handle new task creation."""
    # Classify
    classification = run_cmd(["python3", "N5/pulse/classifier.py", description])
    task_type = classification.get("type", "hybrid")

    # Add to queue
    result = run_cmd([
        "python3", "N5/pulse/queue_manager.py", "add",
        description,
        "--type", task_type,
        "--channel", "sms",
        "--message", f"n5 task {description}"
    ])

    if result.get("success"):
        task = result["task"]
        return {
            "action": "task_created",
            "response": f"✓ Task queued: '{task['title']}' ({task['type']}). Slug: {task['slug']}",
            "task": task
        }
    else:
        return {"action": "error", "response": f"Failed to create task: {result.get('error')}"}


def handle_message(message: str) -> dict:
    """Handle incoming SMS message."""
    parsed = parse_message(message)
    msg_type = parsed["type"]
    
    if msg_type == "interview_response":
        # Explicit tag - route directly
        result = route_to_interview(
            task_slug=parsed["task_slug"],
            content=parsed["content"],
            channel="sms"
        )
        if result["success"]:
            return {
                "action": "fragment_added",
                "response": result["message"],
                "task_id": parsed["task_slug"]
            }
        else:
            return {"action": "error", "response": f"Failed to route: {result.get('error')}"}
    
    elif msg_type == "potential_interview_response":
        # No tag - use fragment router to determine target
        result = subprocess.run([
            "python3", str(Path(__file__).parent / "fragment_router.py"),
            parsed["content"], "--channel", "sms"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            routing = json.loads(result.stdout)
            
            if routing.get("action") == "route_to_interview":
                # Route to the specified interview
                route_result = route_to_interview(
                    task_slug=routing["task_id"],
                    content=routing["content"],
                    channel="sms"
                )
                if route_result.get("success"):
                    return {
                        "action": "fragment_added",
                        "response": f"✓ Added to interview for {routing['task_id']}",
                        "task_id": routing['task_id']
                    }
                else:
                    return {"action": "error", "response": route_result.get("error", "Failed to add fragment")}
            
            elif routing.get("action") == "new_task":
                # No open interviews - treat as new task
                return {
                    "action": "ambiguous",
                    "response": "No open interviews. Reply 'n5 task <description>' to create a task, or use #task-<slug> to target a specific interview."
                }
            
            elif routing.get("action") == "clarify":
                # Multiple open interviews - ask for clarification
                interviews = routing.get("open_interviews", [])
                tags = [f"#task-{i}" for i in interviews]
                return {
                    "action": "clarify",
                    "response": f"Multiple tasks open. Reply with tag: {', '.join(tags)}"
                }
            
            else:
                return {"action": "error", "response": "Could not route message"}
        
        else:
            return {"action": "error", "response": f"Fragment routing failed: {result.stderr}"}
    
    elif msg_type == "new_task":
        return handle_new_task(parsed["description"])
    
    elif msg_type == "list_tasks":
        # List tasks
        result = run_cmd(["python3", "N5/pulse/queue_manager.py", "list", "--status", "queued"])
        tasks = result.get("tasks", [])

        if not tasks:
            return {"action": "list", "response": "No queued tasks."}

        lines = ["📋 Queued tasks:"]
        for t in tasks[:5]:  # Show max 5
            lines.append(f"• {t['title']} ({t['type']}) [{t['slug']}]")

        if len(tasks) > 5:
            lines.append(f"...and {len(tasks) - 5} more")

        return {"action": "list", "response": "\n".join(lines)}
    
    elif msg_type == "prioritize":
        slug = parsed["slug"]
        result = run_cmd(["python3", "N5/pulse/queue_manager.py", "prioritize", slug])

        if result.get("success"):
            return {"action": "prioritized", "response": f"✓ Moved '{slug}' to front of queue."}
        else:
            return {"action": "error", "response": f"Task not found: {slug}"}
    
    elif msg_type == "teach":
        try:
            bank_path = Path("/home/workspace/N5/config/understanding_bank.json")
            if not bank_path.exists():
                return {"action": "teaching", "response": "Understanding bank not initialized yet."}
            bank = json.loads(bank_path.read_text())
            unmastered = [c for c in bank.get("concepts", []) if c.get("level") not in ("solid", "deep")]
            if not unmastered:
                return {"action": "teaching", "response": "🎓 All concepts mastered! No pending items."}
            lines = ["📚 Concepts to review:"]
            for c in unmastered[:5]:
                lines.append(f"• {c['term']} ({c.get('level', 'new')}): {c.get('definition', '')[:80]}")
            if len(unmastered) > 5:
                lines.append(f"...and {len(unmastered) - 5} more")
            lines.append("\nReply 'absorbed: <term>' when mastered.")
            return {"action": "teaching", "response": "\n".join(lines)}
        except Exception as e:
            return {"action": "error", "response": f"Teaching review temporarily unavailable: {str(e)}"}
    
    elif msg_type == "absorbed":
        term = parsed["term"]
        try:
            bank_path = Path("/home/workspace/N5/config/understanding_bank.json")
            if not bank_path.exists():
                return {"action": "error", "response": "Understanding bank not initialized yet."}
            bank = json.loads(bank_path.read_text())
            found = False
            for concept in bank.get("concepts", []):
                if concept["term"].lower() == term.lower():
                    concept["level"] = "solid"
                    concept["last_engaged"] = datetime.now().isoformat()
                    found = True
                    break
            if found:
                bank_path.write_text(json.dumps(bank, indent=2))
                return {
                    "action": "absorbed",
                    "response": f"✓ Marked '{term}' as absorbed",
                    "term": term
                }
            else:
                return {
                    "action": "error",
                    "response": f"Term not found in understanding bank: '{term}'"
                }
        except Exception as e:
            return {"action": "error", "response": f"Failed to mark absorbed: {str(e)}"}
    
    else:
        return {"action": "unknown", "response": "Couldn't process message."}


def handle_sms(message: str) -> dict:
    """
    Handle incoming SMS message.

    Commands:
    - "#task-<slug> <content>" → Route to specific interview
    - "n5 task <description>" → Create new task
    - "n5 tasks" → List pending tasks
    - "n5 prioritize <slug>" → Bump task priority
    - "teach" → Review teaching moments
    - "absorbed: <term>" → Mark term as absorbed
    - Anything else → Route as interview response
    """
    return handle_message(message)


def main():
    parser = argparse.ArgumentParser(description="SMS Intake Handler")
    parser.add_argument("message", help="SMS message content")

    args = parser.parse_args()
    result = handle_sms(args.message)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
