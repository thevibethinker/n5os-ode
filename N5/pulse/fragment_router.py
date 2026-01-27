#!/usr/bin/env python3
"""Route incoming messages to the correct interview or create new task."""

import json
import argparse
import subprocess
import re
from pathlib import Path

INTERVIEWS_DIR = Path("N5/pulse/interviews")

def route_fragment(message: str, channel: str = "sms") -> dict:
    """
    Route incoming message to correct interview.
    
    Returns:
        {routed: True, task_slug: "...", ...} on success
        {routed: False, prompt: "..."} if clarification needed
        {routed: False, treat_as_new: True} if no interviews open
    """
    
    # Priority 1: Explicit tag (should be handled by sms_intake, but check anyway)
    if message.strip().startswith("#task-"):
        parts = message.strip().split(maxsplit=1)
        slug = parts[0].replace("#task-", "")
        content = parts[1] if len(parts) > 1 else ""
        result = add_fragment(slug, content, channel)
        return {"routed": True, "task_slug": slug, **result}
    
    # Priority 2: Single open interview - route there
    open_interviews = get_open_interviews()
    
    if len(open_interviews) == 0:
        return {"routed": False, "treat_as_new": True, "reason": "no_open_interviews"}
    
    if len(open_interviews) == 1:
        slug = open_interviews[0]
        result = add_fragment(slug, message, channel)
        return {"routed": True, "task_slug": slug, "auto_routed": True, **result}
    
    # Priority 3: Multiple open - ask for tag
    tags = [f"#task-{i}" for i in open_interviews]
    return {
        "routed": False,
        "reason": "multiple_open_interviews",
        "open_count": len(open_interviews),
        "prompt": f"Multiple tasks open. Reply with tag: {', '.join(tags)}"
    }

def get_open_interviews() -> list:
    """Get list of open (non-seeded) interview slugs."""
    result = subprocess.run([
        "python3", str(Path(__file__).parent / "interview_manager.py"),
        "list-all"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        # Filter for interviews with status "open"
        return [i["task_id"] for i in data.get("interviews", []) if i.get("status") == "open"]
    return []

def add_fragment(task_id: str, content: str, channel: str) -> dict:
    """Add fragment to interview."""
    result = subprocess.run([
        "python3", str(Path(__file__).parent / "interview_manager.py"),
        "add", task_id, "--channel", channel, "--content", content
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return {"success": True, "message": f"Fragment added to {task_id}"}
    return {"success": False, "error": result.stderr}

def extract_explicit_tag(message: str) -> str | None:
    """Check for explicit #task-<slug> tag."""
    match = re.search(r'#task-([a-z0-9-]+)', message.lower())
    return match.group(1) if match else None

def route(message: str, channel: str) -> dict:
    """
    Determine where this message should go.
    
    Returns:
    - {"action": "route_to_interview", "task_id": "...", "content": "..."}
    - {"action": "new_task", "content": "..."}
    - {"action": "clarify", "open_interviews": [...]}
    """
    # Check for explicit tag
    explicit_tag = extract_explicit_tag(message)
    if explicit_tag:
        # Remove the tag from content
        content = re.sub(r'#task-[a-z0-9-]+\s*', '', message).strip()
        return {
            "action": "route_to_interview",
            "task_id": explicit_tag,
            "content": content,
            "reason": "explicit_tag"
        }
    
    # Get open interviews
    open_interviews = get_open_interviews()
    
    if len(open_interviews) == 0:
        # No open interviews → treat as new task
        return {
            "action": "new_task",
            "content": message,
            "reason": "no_open_interviews"
        }
    elif len(open_interviews) == 1:
        # Exactly one open interview → route there
        return {
            "action": "route_to_interview",
            "task_id": open_interviews[0],
            "content": message,
            "reason": "single_open_interview"
        }
    else:
        # Multiple open interviews → ask for clarification
        return {
            "action": "clarify",
            "open_interviews": open_interviews,
            "content": message,
            "reason": "multiple_open_interviews"
        }

def main():
    parser = argparse.ArgumentParser(description="Fragment Router")
    parser.add_argument("message", help="Message to route")
    parser.add_argument("--channel", default="chat", choices=["sms", "email", "chat"])
    
    args = parser.parse_args()
    result = route(args.message, args.channel)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()