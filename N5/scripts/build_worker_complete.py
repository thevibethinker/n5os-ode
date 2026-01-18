#!/usr/bin/env python3
"""
Build Worker Completion Notifier v1.0

Called when a worker conversation closes to update the build orchestrator.
This script:
1. Reads the worker's SESSION_STATE to get build context
2. Updates the build's STATUS.md with completion info
3. Updates the build's plan.json (if using build_orchestrator_v2)

Usage:
    python3 build_worker_complete.py --convo-id con_XXX [--status complete|partial|blocked]
    python3 build_worker_complete.py --convo-id con_XXX --summary "Completed signal router"
    
Called automatically by Close Conversation workflow for workers.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE_BASE = Path("/home/.z/workspaces")

try:
    from N5.lib.paths import N5_BUILDS_DIR
    BUILDS_DIR = N5_BUILDS_DIR
except ImportError:
    BUILDS_DIR = Path("/home/workspace/N5/builds")


def get_build_context(convo_id: str) -> dict:
    """Extract build context from worker's SESSION_STATE.md."""
    session_path = WORKSPACE_BASE / convo_id / "SESSION_STATE.md"
    
    if not session_path.exists():
        return {"error": f"SESSION_STATE.md not found for {convo_id}"}
    
    content = session_path.read_text()
    context = {}
    
    # Parse frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        for line in frontmatter_match.group(1).split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                context[key.strip()] = value.strip()
    
    # Check for Build Context section
    bc_match = re.search(r"## Build Context\n\n((?:- \*\*[^*]+\*\*[^\n]+\n)+)", content)
    if bc_match:
        for line in bc_match.group(1).strip().split("\n"):
            match = re.match(r"- \*\*([^:]+):\*\*\s+(.+)", line)
            if match:
                key = match.group(1).lower().replace(" ", "_")
                context[key] = match.group(2)
    
    return context


def update_status_md(build_id: str, worker_num: int, status: str, summary: str = None) -> bool:
    """Update the build's STATUS.md with worker completion info."""
    status_path = BUILDS_DIR / build_id / "STATUS.md"
    
    if not status_path.exists():
        print(f"⚠ STATUS.md not found for build {build_id}", file=sys.stderr)
        return False
    
    content = status_path.read_text()
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    
    # Map status to emoji
    status_emoji = {
        "complete": "🟢 Complete",
        "partial": "🟡 Partial", 
        "blocked": "🔴 Blocked"
    }.get(status.lower(), status)
    
    # Try to update the Worker Status table
    # Look for pattern: | N | ... | ... |
    worker_pattern = rf"\| {worker_num} \|([^|]+)\|([^|]+)\|([^|]+)\|([^|]*)\|"
    
    def replace_row(match):
        current_notes = match.group(4).strip()
        new_notes = summary if summary else current_notes
        return f"| {worker_num} | {status_emoji} | {timestamp} | ✅ | {new_notes} |"
    
    new_content, count = re.subn(worker_pattern, replace_row, content)
    
    if count == 0:
        # Try simpler pattern
        simple_pattern = rf"(\| {worker_num} \|)[^\n]+"
        def simple_replace(match):
            return f"| {worker_num} | {status_emoji} | {timestamp} | ✅ | {summary or ''} |"
        new_content, count = re.subn(simple_pattern, simple_replace, content)
    
    if count > 0:
        # Update last_edited in frontmatter
        new_content = re.sub(
            r"(last_edited:\s*)\S+",
            f"\\g<1>{now.strftime('%Y-%m-%d')}",
            new_content
        )
        status_path.write_text(new_content)
        print(f"✓ Updated STATUS.md: Worker {worker_num} → {status}")
        return True
    else:
        print(f"⚠ Could not find Worker {worker_num} row in STATUS.md", file=sys.stderr)
        return False


def update_plan_json(build_id: str, worker_num: int, status: str, convo_id: str = None) -> bool:
    """Update the build's plan.json (for build_orchestrator_v2 compatibility)."""
    plan_path = BUILDS_DIR / build_id / "plan.json"
    
    if not plan_path.exists():
        # Not all builds use plan.json
        return True
    
    try:
        plan = json.loads(plan_path.read_text())
    except json.JSONDecodeError:
        print(f"⚠ Invalid plan.json for build {build_id}", file=sys.stderr)
        return False
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Find and update the worker
    for worker in plan.get("workers", []):
        # Match by worker number (id might be "worker_1" or just "1")
        worker_id = str(worker.get("id", ""))
        if worker_id == str(worker_num) or worker_id == f"worker_{worker_num}":
            worker["status"] = "completed" if status == "complete" else status
            worker["completed_at"] = now
            if convo_id:
                worker["spawned_conversation"] = convo_id
            
            plan_path.write_text(json.dumps(plan, indent=2))
            print(f"✓ Updated plan.json: Worker {worker_num} → {status}")
            return True
    
    print(f"⚠ Worker {worker_num} not found in plan.json", file=sys.stderr)
    return False


def add_activity_log(build_id: str, worker_num: int, status: str, summary: str = None) -> bool:
    """Append to the Activity Log section in STATUS.md."""
    status_path = BUILDS_DIR / build_id / "STATUS.md"
    
    if not status_path.exists():
        return False
    
    content = status_path.read_text()
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    
    log_entry = f"| {timestamp} | Worker {worker_num} {status}"
    if summary:
        log_entry += f": {summary}"
    log_entry += " |"
    
    # Find Activity Log section and append
    if "## Activity Log" in content:
        # Find the last row of the table
        activity_section = content.split("## Activity Log")[1]
        table_end = activity_section.find("\n\n")
        if table_end == -1:
            table_end = len(activity_section)
        
        # Insert before end of table
        insert_pos = content.find("## Activity Log") + len("## Activity Log") + activity_section[:table_end].rfind("\n")
        new_content = content[:insert_pos] + "\n" + log_entry + content[insert_pos:]
        status_path.write_text(new_content)
        return True
    
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Notify build orchestrator of worker completion"
    )
    parser.add_argument("--convo-id", required=True, help="Worker conversation ID")
    parser.add_argument("--status", default="complete", 
                       choices=["complete", "partial", "blocked"],
                       help="Worker completion status")
    parser.add_argument("--summary", help="Brief summary of work done")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    
    args = parser.parse_args()
    
    # Get build context
    context = get_build_context(args.convo_id)
    
    if "error" in context:
        print(f"✗ {context['error']}", file=sys.stderr)
        return 1
    
    build_id = context.get("build_id") or context.get("build")
    worker_num = context.get("worker_num") or context.get("worker")
    
    if not build_id:
        print("✗ No build_id found in SESSION_STATE - not a worker conversation", file=sys.stderr)
        return 1
    
    if not worker_num:
        print("✗ No worker_num found in SESSION_STATE", file=sys.stderr)
        return 1
    
    try:
        worker_num = int(worker_num)
    except ValueError:
        print(f"✗ Invalid worker_num: {worker_num}", file=sys.stderr)
        return 1
    
    print(f"Build: {build_id}")
    print(f"Worker: {worker_num}")
    print(f"Status: {args.status}")
    if args.summary:
        print(f"Summary: {args.summary}")
    print()
    
    if args.dry_run:
        print("[DRY RUN] Would update:")
        print(f"  - {BUILDS_DIR / build_id / 'STATUS.md'}")
        print(f"  - {BUILDS_DIR / build_id / 'plan.json'} (if exists)")
        return 0
    
    # Update build artifacts
    success = True
    
    if not update_status_md(build_id, worker_num, args.status, args.summary):
        success = False
    
    update_plan_json(build_id, worker_num, args.status, args.convo_id)
    add_activity_log(build_id, worker_num, args.status, args.summary)
    
    if success:
        print(f"\n✓ Build {build_id} notified of Worker {worker_num} completion")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
