#!/usr/bin/env python3
"""
Build Companion Tracker
Monitors parallel work streams across conversations during build sessions.

Usage:
    python3 build_tracker.py activate
    python3 build_tracker.py refresh
    python3 build_tracker.py track "Task name"
    python3 build_tracker.py status "Task name" --state [open|active|complete|paused|abandoned]
    python3 build_tracker.py mark-build-convo
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

STATE_DIR = Path("/home/workspace/N5/.state")
ACTIVE_TRACKER_FILE = STATE_DIR / "build_tracker_active.json"
CONVO_TYPES_FILE = STATE_DIR / "conversation_types.json"
SESSION_LOG_DIR = Path("/home/workspace/N5/logs/build-sessions")
WORKSPACE_ROOT = Path("/home/workspace")
CONVO_WORKSPACES_ROOT = Path("/home/.z/workspaces")

# Import session state manager
sys.path.insert(0, str(Path(__file__).parent))
try:
    from session_state_manager import SessionStateManager
except ImportError:
    SessionStateManager = None


class BuildTracker:
    def __init__(self, convo_id: Optional[str] = None, filter_type: str = "all"):
        self.convo_id = convo_id or self._detect_current_convo()
        self.filter_type = filter_type
        self.workspace = Path("/home/workspace")
        self.session_log_dir = self.workspace / "N5/logs/build-sessions"
        self.archive_dir = self.session_log_dir / "archive"
        self.session_file = self._get_session_file()
        self.build_map_file = self._get_build_map_path()
        
        # Ensure directories exist
        self.session_log_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def _detect_current_convo(self) -> str:
        cwd = Path.cwd()
        if str(cwd).startswith(str(CONVO_WORKSPACES_ROOT)):
            return cwd.name
        return "unknown"
    
    def _get_session_file(self) -> Path:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return SESSION_LOG_DIR / f"session_{date_str}_{self.convo_id}.jsonl"
    
    def _get_build_map_path(self) -> Path:
        """Get path to BUILD_MAP.md in conversation workspace."""
        convo_ws = CONVO_WORKSPACES_ROOT / self.convo_id
        return convo_ws / "BUILD_MAP.md"
    
    def _log_event(self, event: str, data: Dict = None):
        """Append event to session log."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "data": data or {}
        }
        with open(self.session_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def activate(self) -> bool:
        """Activate this conversation as the build tracker."""
        state = {
            "active_conversation_id": self.convo_id,
            "activated_at": datetime.now(timezone.utc).isoformat()
        }
        ACTIVE_TRACKER_FILE.write_text(json.dumps(state, indent=2))
        self._log_event("tracker_activated")
        self._create_build_map()
        logger.info(f"✓ Activated build tracker in conversation: {self.convo_id}")
        logger.info(f"✓ Created BUILD_MAP: {self.build_map_file}")
        return True
    
    def _create_build_map(self):
        """Initialize BUILD_MAP.md template."""
        template = f"""# Build Session Map

**Created:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Session:** {self.convo_id}

---

## Active Tasks

*No tasks yet. Use `track <task-name>` to add one.*

## Git Status

Initializing...

## Build Conversations

Initializing...

---

**Commands:**
- `track <task>` - Add new task
- `working on <task>` - Mark task as active
- `done with <task>` - Mark task complete
- `refresh tracker` - Update this map
"""
        self.build_map_file.write_text(template)
    
    def track_task(self, task_name: str) -> bool:
        """Add new task to tracker."""
        self._log_event("task_added", {"task": task_name, "state": "open"})
        logger.info(f"✓ Tracking task: {task_name}")
        return True
    
    def update_task_state(self, task_name: str, state: str) -> bool:
        """Update task state."""
        valid_states = ["open", "active", "complete", "paused", "abandoned"]
        if state not in valid_states:
            logger.error(f"Invalid state: {state}. Must be one of {valid_states}")
            return False
        
        self._log_event("task_state_changed", {"task": task_name, "state": state})
        logger.info(f"✓ Task '{task_name}' → {state}")
        return True
    
    def refresh(self) -> bool:
        """Refresh build map with current state."""
        try:
            tasks = self._load_tasks()
            git_status = self._get_git_status()
            build_convos = self._get_build_conversations()
            
            self._update_build_map(tasks, git_status, build_convos)
            logger.info(f"✓ Refreshed BUILD_MAP: {self.build_map_file}")
            return True
        except Exception as e:
            logger.error(f"Error refreshing tracker: {e}", exc_info=True)
            return False
    
    def _load_tasks(self) -> List[Dict]:
        """Load tasks from session log."""
        if not self.session_file.exists():
            return []
        
        tasks = {}
        session_closed = False
        
        with open(self.session_file) as f:
            for line in f:
                event = json.loads(line.strip())
                
                # Check if session is closed
                if event["event"] == "session_closed":
                    session_closed = True
                    continue
                
                if event["event"] == "task_added":
                    task_name = event["data"]["task"]
                    tasks[task_name] = {
                        "name": task_name,
                        "state": "open",
                        "added_at": event["timestamp"]
                    }
                elif event["event"] == "task_state_changed":
                    task_name = event["data"]["task"]
                    if task_name in tasks:
                        tasks[task_name]["state"] = event["data"]["state"]
                        tasks[task_name]["updated_at"] = event["timestamp"]
        
        # Filter completed tasks if session is closed
        task_list = list(tasks.values())
        if session_closed:
            task_list = [t for t in task_list if t["state"] != "complete"]
        
        return task_list
    
    def _get_git_status(self) -> Dict:
        """Get git status from workspace."""
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=WORKSPACE_ROOT,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return {"error": "Not a git repository or git error"}
            
            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            modified = [l[3:] for l in lines if l.startswith(" M")]
            staged = [l[3:] for l in lines if l.startswith("M ")]
            untracked = [l[3:] for l in lines if l.startswith("??")]
            
            return {
                "modified": modified[:10],
                "staged": staged[:10],
                "untracked": untracked[:10],
                "total": len(lines)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _scan_conversations(self, hours: int = 2) -> List[Dict]:
        """Scan conversation workspaces for recent activity."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        convos = []
        
        for convo_dir in sorted(CONVO_WORKSPACES_ROOT.iterdir(), 
                               key=lambda p: p.stat().st_mtime, reverse=True)[:10]:
            if not convo_dir.is_dir():
                continue
            
            mtime = datetime.fromtimestamp(convo_dir.stat().st_mtime, timezone.utc)
            if mtime < cutoff:
                continue
            
            files = sorted(convo_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not files:
                continue
            
            convo_id = convo_dir.name
            recent_files = [f.name for f in files[:3]]
            
            # Try to read SESSION_STATE.md if it exists
            session_info = None
            if SessionStateManager:
                manager = SessionStateManager(convo_id)
                session_info = manager.read()
            
            convos.append({
                "id": convo_id,
                "mtime": mtime,
                "files": recent_files,
                "session_state": session_info
            })
        
        return convos[:5]
    
    def _get_build_conversations(self) -> List[Dict]:
        """Get recent build conversations."""
        all_convos = self._scan_conversations()
        
        # Apply filter
        if self.filter_type == "all":
            return all_convos
        
        filtered = []
        for convo in all_convos:
            if convo.get("session_state"):
                convo_type = convo["session_state"].get("type", "")
                if convo_type == self.filter_type:
                    filtered.append(convo)
        
        return filtered
    
    def _load_conversation_types(self) -> Dict:
        """Load conversation type classifications."""
        if not CONVO_TYPES_FILE.exists():
            return {}
        return json.loads(CONVO_TYPES_FILE.read_text())
    
    def _update_build_map(self, tasks: List[Dict], git_status: Dict, build_convos: List[Dict]):
        """Update BUILD_MAP.md with current state."""
        content = f"""# Build Session Map

**Updated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Session:** {self.convo_id}

---

## Active Tasks

"""
        
        active_tasks = [t for t in tasks if t["state"] in ["open", "active"]]
        if active_tasks:
            for task in active_tasks:
                icon = "🔵" if task["state"] == "active" else "⚪"
                content += f"{icon} **{task['name']}** ({task['state']})\n"
        else:
            content += "*No active tasks*\n"
        
        completed_tasks = [t for t in tasks if t["state"] == "complete"]
        if completed_tasks:
            content += "\n### Completed\n"
            for task in completed_tasks:
                content += f"✅ {task['name']}\n"
        
        content += "\n## Git Status\n\n"
        if "error" in git_status:
            content += f"*{git_status['error']}*\n"
        else:
            content += f"**Total changes:** {git_status.get('total', 0)}\n\n"
            if git_status.get("modified"):
                content += "**Modified:**\n"
                for f in git_status["modified"]:
                    content += f"- `{f}`\n"
            if git_status.get("staged"):
                content += "\n**Staged:**\n"
                for f in git_status["staged"]:
                    content += f"- `{f}`\n"
        
        content += "\n## Build Conversations\n\n"
        for convo in build_convos:
            current = " **(current)**" if convo["id"] == self.convo_id else ""
            
            # Add session state info if available
            state_info = ""
            if convo.get("session_state"):
                ss = convo["session_state"]
                convo_type = ss.get("type", "unknown")
                mode = ss.get("mode", "")
                focus = ss.get("focus", "").strip("*").strip()
                if convo_type != "unknown":
                    state_info = f" [{convo_type}:{mode}]" if mode else f" [{convo_type}]"
                if focus and focus != "What is this conversation specifically about?":
                    state_info += f" - {focus}"
            
            content += f"💬 `{convo['id']}`{current}{state_info}\n"
            if convo.get("files"):
                content += f"  Recent: {', '.join(f'`{f}`' for f in convo['files'][:3])}\n"
        
        content += """
---

**Commands:**
- `track <task>` - Add new task
- `working on <task>` - Mark task as active
- `done with <task>` - Mark task complete
- `refresh tracker` - Update this map
"""
        
        self.build_map_file.write_text(content)
    
    def mark_build_convo(self, convo_id: Optional[str] = None) -> bool:
        """Manually mark conversation as build type."""
        target = convo_id or self.convo_id
        convo_types = self._load_conversation_types()
        convo_types[target] = {"type": "build", "marked_at": datetime.now(timezone.utc).isoformat()}
        CONVO_TYPES_FILE.write_text(json.dumps(convo_types, indent=2))
        logger.info(f"✓ Marked {target} as build conversation")
        return True

    def is_session_closed(self) -> bool:
        """Check if this session has been closed."""
        if not self.session_file.exists():
            return False
        
        with open(self.session_file) as f:
            for line in f:
                event = json.loads(line.strip())
                if event.get("event") == "session_closed":
                    return True
        return False
    
    def close_session(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Close this build session and mark tasks as archived.
        
        Returns summary with counts of tasks by state.
        """
        if not self.session_file.exists():
            return {"error": "No session file found", "closed": False}
        
        # Check if already closed
        if self.is_session_closed():
            return {"error": "Session already closed", "closed": True}
        
        # Load current tasks
        tasks = self._load_tasks()
        
        # Count by state
        summary = {
            "total": len(tasks),
            "complete": len([t for t in tasks if t["state"] == "complete"]),
            "active": len([t for t in tasks if t["state"] == "active"]),
            "open": len([t for t in tasks if t["state"] == "open"]),
            "paused": len([t for t in tasks if t["state"] == "paused"]),
            "abandoned": len([t for t in tasks if t["state"] == "abandoned"]),
            "closed": True
        }
        
        if dry_run:
            print(f"[DRY RUN] Would close session {self.convo_id}")
            print(f"  Total tasks: {summary['total']}")
            print(f"  Complete: {summary['complete']}")
            print(f"  Active/Open: {summary['active'] + summary['open']}")
            return summary
        
        # Log session closed event
        self._log_event("session_closed", {
            "summary": summary,
            "tasks": [t["name"] for t in tasks]
        })
        
        return summary
    
    def generate_archive(self, dry_run: bool = False) -> Optional[Path]:
        """
        Generate archive file with completed tasks.
        
        Returns path to archive file or None if no completed tasks.
        """
        if not self.session_file.exists():
            return None
        
        tasks = self._load_tasks()
        completed_tasks = [t for t in tasks if t["state"] == "complete"]
        
        if not completed_tasks:
            if not dry_run:
                print("No completed tasks to archive")
            return None
        
        archive_file = self.archive_dir / f"{self.convo_id}_completed.jsonl"
        
        if dry_run:
            print(f"[DRY RUN] Would create archive: {archive_file}")
            print(f"  Tasks to archive: {len(completed_tasks)}")
            for task in completed_tasks:
                print(f"    - {task['name']}")
            return archive_file
        
        # Write archive
        with open(archive_file, 'w') as f:
            # Header
            archive_header = {
                "type": "session_archive",
                "convo_id": self.convo_id,
                "archived_at": datetime.now().isoformat(),
                "task_count": len(completed_tasks)
            }
            f.write(json.dumps(archive_header) + '\n')
            
            # Tasks
            for task in completed_tasks:
                archive_entry = {
                    "type": "task_completed",
                    "task": task["name"],
                    "added_at": task.get("added_at"),
                    "completed_at": task.get("updated_at"),
                    "state": task["state"]
                }
                f.write(json.dumps(archive_entry) + '\n')
        
        print(f"✓ Archived {len(completed_tasks)} completed tasks to {archive_file.name}")
        return archive_file


def main():
    parser = argparse.ArgumentParser(description="Build session tracker")
    parser.add_argument("command", choices=["activate", "track", "status", "refresh", "mark", "close", "archive"])
    parser.add_argument("task", nargs="?", help="Task name")
    parser.add_argument("--state", choices=["open", "active", "complete", "paused", "abandoned"])
    parser.add_argument("--convo-id", help="Specific conversation ID")
    parser.add_argument("--filter", choices=["all", "build", "active"], default="all")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    
    args = parser.parse_args()
    
    tracker = BuildTracker(convo_id=args.convo_id, filter_type=args.filter)
    
    if args.command == "activate":
        success = tracker.activate()
        sys.exit(0 if success else 1)
    
    elif args.command == "track":
        if not args.task:
            print("Error: task name required")
            sys.exit(1)
        success = tracker.track_task(args.task)
        sys.exit(0 if success else 1)
    
    elif args.command == "status":
        if not args.task or not args.state:
            print("Error: task name and --state required")
            sys.exit(1)
        success = tracker.update_task_state(args.task, args.state)
        sys.exit(0 if success else 1)
    
    elif args.command == "refresh":
        success = tracker.refresh()
        sys.exit(0 if success else 1)
    
    elif args.command == "mark":
        success = tracker.mark_build_convo(args.convo_id)
        sys.exit(0 if success else 1)
    
    elif args.command == "close":
        summary = tracker.close_session(dry_run=args.dry_run)
        if summary.get("error"):
            print(f"Error: {summary['error']}")
            sys.exit(1)
        print(f"✓ Session closed: {summary['total']} total tasks, {summary['complete']} completed")
        sys.exit(0)
    
    elif args.command == "archive":
        archive_file = tracker.generate_archive(dry_run=args.dry_run)
        if archive_file:
            print(f"✓ Archive created: {archive_file}")
            sys.exit(0)
        else:
            print("No tasks to archive")
            sys.exit(0)


if __name__ == "__main__":
    exit(main())
