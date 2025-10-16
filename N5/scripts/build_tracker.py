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
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


class BuildTracker:
    def __init__(self, convo_id: Optional[str] = None):
        self.convo_id = convo_id or self._detect_current_convo()
        self.workspace = CONVO_WORKSPACES_ROOT / self.convo_id
        self.build_map_file = self.workspace / "BUILD_MAP.md"
        self.session_file = self._get_session_file()
        
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        SESSION_LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    def _detect_current_convo(self) -> str:
        cwd = Path.cwd()
        if str(cwd).startswith(str(CONVO_WORKSPACES_ROOT)):
            return cwd.name
        return "unknown"
    
    def _get_session_file(self) -> Path:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return SESSION_LOG_DIR / f"session_{date_str}_{self.convo_id}.jsonl"
    
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
        with open(self.session_file) as f:
            for line in f:
                event = json.loads(line.strip())
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
        
        return list(tasks.values())
    
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
    
    def _get_build_conversations(self) -> List[Dict]:
        """Get recent build conversations."""
        try:
            convo_types = self._load_conversation_types()
            recent_convos = []
            
            for convo_dir in sorted(CONVO_WORKSPACES_ROOT.iterdir(), 
                                   key=lambda x: x.stat().st_mtime, 
                                   reverse=True)[:5]:
                if not convo_dir.is_dir():
                    continue
                
                convo_id = convo_dir.name
                is_build = convo_types.get(convo_id, {}).get("type") == "build"
                
                files = list(convo_dir.glob("*"))
                recent_files = [
                    f.name for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
                    if f.is_file()
                ]
                
                recent_convos.append({
                    "id": convo_id,
                    "is_build": is_build,
                    "recent_files": recent_files,
                    "file_count": len(files)
                })
            
            return recent_convos
        except Exception as e:
            logger.error(f"Error getting build conversations: {e}")
            return []
    
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
            marker = "🔨" if convo["is_build"] else "💬"
            current = " **(current)**" if convo["id"] == self.convo_id else ""
            content += f"{marker} `{convo['id']}`{current}\n"
            if convo["recent_files"]:
                content += f"  Recent: {', '.join(f'`{f}`' for f in convo['recent_files'][:3])}\n"
        
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


def main():
    parser = argparse.ArgumentParser(description="Build Companion Tracker")
    parser.add_argument("action", choices=["activate", "refresh", "track", "status", "mark-build-convo", "classify"])
    parser.add_argument("task", nargs="?", help="Task name (for track/status actions)")
    parser.add_argument("--state", choices=["open", "active", "complete", "paused", "abandoned"],
                       help="Task state (for status action)")
    parser.add_argument("--convo-id", help="Conversation ID (defaults to current)")
    
    args = parser.parse_args()
    tracker = BuildTracker(convo_id=args.convo_id)
    
    if args.action == "activate":
        success = tracker.activate()
        return 0 if success else 1
    
    elif args.action == "refresh":
        success = tracker.refresh()
        return 0 if success else 1
    
    elif args.action == "track":
        if not args.task:
            logger.error("Task name required for 'track' action")
            return 1
        success = tracker.track_task(args.task)
        return 0 if success else 1
    
    elif args.action == "status":
        if not args.task or not args.state:
            logger.error("Task name and --state required for 'status' action")
            return 1
        success = tracker.update_task_state(args.task, args.state)
        return 0 if success else 1
    
    elif args.action == "mark-build-convo":
        success = tracker.mark_build_convo(args.convo_id)
        return 0 if success else 1
    
    return 0


if __name__ == "__main__":
    exit(main())
