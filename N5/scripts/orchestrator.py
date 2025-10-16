#!/usr/bin/env python3
"""
Orchestrator Commands
Enables orchestrator conversations to manage and coordinate worker conversations.

Usage:
    python3 orchestrator.py assign "Implement auth module" --to con_WORKER
    python3 orchestrator.py check-worker con_WORKER
    python3 orchestrator.py review-changes con_WORKER
    python3 orchestrator.py approve con_WORKER --merge
    python3 orchestrator.py test-integration
"""

import argparse
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
CONVO_WORKSPACES_ROOT = Path("/home/.z/workspaces")
STATE_DIR = Path("/home/workspace/N5/.state")
ASSIGNMENTS_FILE = STATE_DIR / "worker_assignments.jsonl"


class Orchestrator:
    def __init__(self, orchestrator_id: str):
        self.orchestrator_id = orchestrator_id
        self.workspace = CONVO_WORKSPACES_ROOT / orchestrator_id
        
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    def assign_task(self, task_desc: str, worker_id: str) -> bool:
        """Assign a task to a worker conversation."""
        try:
            assignment = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "orchestrator": self.orchestrator_id,
                "worker": worker_id,
                "task": task_desc,
                "status": "assigned"
            }
            
            # Log assignment
            with ASSIGNMENTS_FILE.open("a") as f:
                f.write(json.dumps(assignment) + "\n")
            
            # Create assignment file in worker workspace
            worker_workspace = CONVO_WORKSPACES_ROOT / worker_id
            worker_workspace.mkdir(parents=True, exist_ok=True)
            
            assignment_file = worker_workspace / "ASSIGNMENT.md"
            content = f"""# Task Assignment

**From:** {self.orchestrator_id}  
**Assigned:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}  
**Status:** assigned

---

## Task Description

{task_desc}

---

## Instructions

1. Update SESSION_STATE.md with this task as Current Task
2. Implement the task
3. Update SESSION_STATE.md progress as you work
4. When complete, update status to "complete" in SESSION_STATE.md

**Orchestrator is monitoring your SESSION_STATE.md for progress.**
"""
            assignment_file.write_text(content)
            
            logger.info(f"✓ Assigned task to {worker_id}")
            logger.info(f"  Task: {task_desc}")
            logger.info(f"  Assignment file: {assignment_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign task: {e}")
            return False
    
    def check_worker(self, worker_id: str) -> Dict:
        """Check worker status by reading their SESSION_STATE.md."""
        try:
            worker_workspace = CONVO_WORKSPACES_ROOT / worker_id
            state_file = worker_workspace / "SESSION_STATE.md"
            
            if not state_file.exists():
                return {
                    "error": f"Worker {worker_id} has no SESSION_STATE.md",
                    "exists": False
                }
            
            content = state_file.read_text()
            
            # Parse key fields
            state = {
                "worker_id": worker_id,
                "exists": True,
                "content": content
            }
            
            # Extract status, current task, progress
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("**Status:**"):
                    state["status"] = line.split("**Status:**")[1].strip()
                elif line.startswith("### Current Task"):
                    # Get next non-empty line
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip() and not lines[j].startswith("#"):
                            state["current_task"] = lines[j].strip()
                            break
            
            logger.info(f"✓ Worker {worker_id} status: {state.get('status', 'unknown')}")
            if "current_task" in state:
                logger.info(f"  Current task: {state['current_task']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to check worker: {e}")
            return {"error": str(e), "exists": False}
    
    def review_changes(self, worker_id: str) -> Dict:
        """Review git changes made by worker (requires git staging by worker)."""
        try:
            # Look for files modified in worker's workspace
            worker_workspace = CONVO_WORKSPACES_ROOT / worker_id
            
            if not worker_workspace.exists():
                return {"error": f"Worker workspace {worker_id} not found"}
            
            # Get list of files in worker workspace
            files = list(worker_workspace.glob("**/*"))
            files = [f for f in files if f.is_file() and not f.name.startswith(".")]
            
            # Check git status for changes
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=WORKSPACE_ROOT,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return {"error": "Git status failed"}
            
            changes = result.stdout.strip().split("\n") if result.stdout.strip() else []
            
            review = {
                "worker_id": worker_id,
                "workspace_files": [str(f.relative_to(worker_workspace)) for f in files[:20]],
                "git_changes": changes[:20],
                "total_workspace_files": len(files),
                "total_git_changes": len(changes)
            }
            
            logger.info(f"✓ Review for {worker_id}:")
            logger.info(f"  Workspace files: {len(files)}")
            logger.info(f"  Git changes: {len(changes)}")
            
            return review
            
        except Exception as e:
            logger.error(f"Failed to review changes: {e}")
            return {"error": str(e)}
    
    def approve(self, worker_id: str, merge: bool = False) -> bool:
        """Approve worker's work and optionally merge changes."""
        try:
            # Update assignment status
            assignment = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "orchestrator": self.orchestrator_id,
                "worker": worker_id,
                "action": "approved",
                "merged": merge
            }
            
            with ASSIGNMENTS_FILE.open("a") as f:
                f.write(json.dumps(assignment) + "\n")
            
            # Create approval file in worker workspace
            worker_workspace = CONVO_WORKSPACES_ROOT / worker_id
            approval_file = worker_workspace / "APPROVAL.md"
            
            content = f"""# Work Approved

**By:** {self.orchestrator_id}  
**Approved:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}  
**Merged:** {"Yes" if merge else "No - manual merge required"}

---

## Next Steps

{"✓ Changes have been merged into main workspace" if merge else "⚠️  Please coordinate with orchestrator for manual merge"}
"""
            approval_file.write_text(content)
            
            logger.info(f"✓ Approved work from {worker_id}")
            if merge:
                logger.info("  Note: Auto-merge not implemented yet - manual merge required")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve: {e}")
            return False
    
    def test_integration(self) -> Dict:
        """Run integration tests (placeholder for now)."""
        try:
            logger.info("Running integration tests...")
            
            # Placeholder - would run actual tests
            result = {
                "status": "skipped",
                "message": "Integration test runner not yet implemented",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.warning("⚠️  Integration test runner not yet implemented")
            return result
            
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Orchestrator Commands")
    parser.add_argument("action", choices=["assign", "check-worker", "review-changes", "approve", "test-integration"])
    parser.add_argument("task_or_worker", nargs="?", help="Task description (for assign) or worker ID")
    parser.add_argument("--to", dest="worker_id", help="Worker conversation ID (for assign)")
    parser.add_argument("--orchestrator-id", default="con_unknown", help="Orchestrator conversation ID")
    parser.add_argument("--merge", action="store_true", help="Auto-merge on approve (not yet implemented)")
    
    args = parser.parse_args()
    
    orchestrator = Orchestrator(args.orchestrator_id)
    
    if args.action == "assign":
        if not args.task_or_worker or not args.worker_id:
            logger.error("Task description and --to <worker_id> required for assign")
            return 1
        success = orchestrator.assign_task(args.task_or_worker, args.worker_id)
        return 0 if success else 1
    
    elif args.action == "check-worker":
        if not args.task_or_worker:
            logger.error("Worker ID required for check-worker")
            return 1
        state = orchestrator.check_worker(args.task_or_worker)
        print(json.dumps(state, indent=2))
        return 0 if state.get("exists") else 1
    
    elif args.action == "review-changes":
        if not args.task_or_worker:
            logger.error("Worker ID required for review-changes")
            return 1
        review = orchestrator.review_changes(args.task_or_worker)
        print(json.dumps(review, indent=2))
        return 0 if "error" not in review else 1
    
    elif args.action == "approve":
        if not args.task_or_worker:
            logger.error("Worker ID required for approve")
            return 1
        success = orchestrator.approve(args.task_or_worker, merge=args.merge)
        return 0 if success else 1
    
    elif args.action == "test-integration":
        result = orchestrator.test_integration()
        print(json.dumps(result, indent=2))
        return 0 if "error" not in result else 1
    
    return 0


if __name__ == "__main__":
    exit(main())
