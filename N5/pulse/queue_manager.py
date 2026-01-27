#!/usr/bin/env python3
"""Task queue manager for Pulse v2."""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
import uuid
import re

QUEUE_PATH = Path(__file__).parent / "task_queue.json"

def ensure_queue():
    """Ensure queue file exists."""
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not QUEUE_PATH.exists():
        QUEUE_PATH.write_text(json.dumps({"version": "1.0", "tasks": []}, indent=2))

def load_queue() -> dict:
    ensure_queue()
    return json.loads(QUEUE_PATH.read_text())

def save_queue(data: dict):
    QUEUE_PATH.write_text(json.dumps(data, indent=2))

def generate_slug(title: str) -> str:
    """Generate URL-safe slug from title."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug[:50].strip('-')
    return slug or f"task-{uuid.uuid4().hex[:8]}"

def add_task(title: str, task_type: str, channel: str, message: str, priority: int = 5) -> dict:
    """Add a new task to the queue."""
    queue = load_queue()
    
    task_id = f"task-{uuid.uuid4().hex[:12]}"
    slug = generate_slug(title)
    
    # Ensure unique slug
    existing_slugs = {t["slug"] for t in queue["tasks"]}
    if slug in existing_slugs:
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"
    
    task = {
        "id": task_id,
        "slug": slug,
        "title": title,
        "type": task_type,
        "status": "queued",
        "priority": priority,
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
        "intake_channel": channel,
        "intake_message": message,
        "interview_id": None,
        "build_slug": None
    }
    
    queue["tasks"].append(task)
    save_queue(queue)
    
    print(json.dumps({"success": True, "task": task}))
    return task

def list_tasks(status: str = None, task_type: str = None) -> list:
    """List tasks with optional filters."""
    queue = load_queue()
    tasks = queue["tasks"]
    
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if task_type:
        tasks = [t for t in tasks if t["type"] == task_type]
    
    # Sort by priority (lower = higher priority), then by created_at
    tasks.sort(key=lambda t: (t["priority"], t["created_at"]))
    
    print(json.dumps({"tasks": tasks, "count": len(tasks)}))
    return tasks

def prioritize(task_id: str) -> dict:
    """Move task to front of queue (priority = 0)."""
    queue = load_queue()
    
    for task in queue["tasks"]:
        if task["id"] == task_id or task["slug"] == task_id:
            task["priority"] = 0
            task["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
            save_queue(queue)
            print(json.dumps({"success": True, "task": task}))
            return task
    
    print(json.dumps({"success": False, "error": "Task not found"}))
    return None

def advance(task_id: str, new_status: str) -> dict:
    """Advance task to new status."""
    valid_statuses = ["queued", "interviewing", "seeded", "planning", "plan_review", "building", "tidying", "complete", "failed"]
    
    if new_status not in valid_statuses:
        print(json.dumps({"success": False, "error": f"Invalid status. Must be one of: {valid_statuses}"}))
        return None
    
    queue = load_queue()
    
    for task in queue["tasks"]:
        if task["id"] == task_id or task["slug"] == task_id:
            task["status"] = new_status
            task["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
            save_queue(queue)
            print(json.dumps({"success": True, "task": task}))
            return task
    
    print(json.dumps({"success": False, "error": "Task not found"}))
    return None

def get_next() -> dict:
    """Get next queued task ready for interview."""
    queue = load_queue()
    tasks = [t for t in queue["tasks"] if t["status"] == "queued"]
    tasks.sort(key=lambda t: (t["priority"], t["created_at"]))
    
    if tasks:
        print(json.dumps({"success": True, "task": tasks[0]}))
        return tasks[0]
    
    print(json.dumps({"success": True, "task": None, "message": "No queued tasks"}))
    return None

def get_task(task_id: str) -> dict:
    """Get a specific task by ID or slug."""
    queue = load_queue()
    
    for task in queue["tasks"]:
        if task["id"] == task_id or task["slug"] == task_id:
            print(json.dumps({"success": True, "task": task}))
            return task
    
    print(json.dumps({"success": False, "error": "Task not found"}))
    return None

def link_interview(task_id: str, interview_id: str) -> dict:
    """Link an interview session to a task."""
    queue = load_queue()
    
    for task in queue["tasks"]:
        if task["id"] == task_id or task["slug"] == task_id:
            task["interview_id"] = interview_id
            task["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
            save_queue(queue)
            print(json.dumps({"success": True, "task": task}))
            return task
    
    print(json.dumps({"success": False, "error": "Task not found"}))
    return None

def link_build(task_id: str, build_slug: str) -> dict:
    """Link a build to a task."""
    queue = load_queue()
    
    for task in queue["tasks"]:
        if task["id"] == task_id or task["slug"] == task_id:
            task["build_slug"] = build_slug
            task["updated_at"] = datetime.now(timezone.utc).isoformat() + "Z"
            save_queue(queue)
            print(json.dumps({"success": True, "task": task}))
            return task
    
    print(json.dumps({"success": False, "error": "Task not found"}))
    return None

def remove_task(task_id: str) -> dict:
    """Remove a task from the queue."""
    queue = load_queue()
    
    for i, task in enumerate(queue["tasks"]):
        if task["id"] == task_id or task["slug"] == task_id:
            removed = queue["tasks"].pop(i)
            save_queue(queue)
            print(json.dumps({"success": True, "removed": removed}))
            return removed
    
    print(json.dumps({"success": False, "error": "Task not found"}))
    return None

def main():
    parser = argparse.ArgumentParser(description="Pulse v2 Task Queue Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("--type", default="hybrid", choices=["code_build", "research", "content", "analysis", "hybrid"])
    add_parser.add_argument("--channel", default="chat", choices=["sms", "email", "chat"])
    add_parser.add_argument("--message", default="", help="Original intake message")
    add_parser.add_argument("--priority", type=int, default=5, help="Priority (0=highest)")
    
    # list
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--type", help="Filter by type")
    
    # prioritize
    prio_parser = subparsers.add_parser("prioritize", help="Move task to front")
    prio_parser.add_argument("task_id", help="Task ID or slug")
    
    # advance
    adv_parser = subparsers.add_parser("advance", help="Change task status")
    adv_parser.add_argument("task_id", help="Task ID or slug")
    adv_parser.add_argument("status", help="New status")
    
    # next
    subparsers.add_parser("next", help="Get next queued task")
    
    # get
    get_parser = subparsers.add_parser("get", help="Get specific task")
    get_parser.add_argument("task_id", help="Task ID or slug")
    
    # link-interview
    link_int_parser = subparsers.add_parser("link-interview", help="Link interview to task")
    link_int_parser.add_argument("task_id", help="Task ID or slug")
    link_int_parser.add_argument("interview_id", help="Interview session ID")
    
    # link-build
    link_build_parser = subparsers.add_parser("link-build", help="Link build to task")
    link_build_parser.add_argument("task_id", help="Task ID or slug")
    link_build_parser.add_argument("build_slug", help="Build slug")
    
    # remove
    remove_parser = subparsers.add_parser("remove", help="Remove task from queue")
    remove_parser.add_argument("task_id", help="Task ID or slug")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_task(args.title, args.type, args.channel, args.message, args.priority)
    elif args.command == "list":
        list_tasks(args.status, getattr(args, 'type', None))
    elif args.command == "prioritize":
        prioritize(args.task_id)
    elif args.command == "advance":
        advance(args.task_id, args.status)
    elif args.command == "next":
        get_next()
    elif args.command == "get":
        get_task(args.task_id)
    elif args.command == "link-interview":
        link_interview(args.task_id, args.interview_id)
    elif args.command == "link-build":
        link_build(args.task_id, args.build_slug)
    elif args.command == "remove":
        remove_task(args.task_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
