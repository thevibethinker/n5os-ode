#!/usr/bin/env python3
"""
Conversation Orchestrator - Autonomous Worker Conversation Coordination
Spawns, monitors, and coordinates multiple Zo worker conversations.

Centralized telemetry pattern: Workers report TO orchestrator workspace.
"""

import argparse
import json
import logging
import subprocess
import sys
import time
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import telemetry validator
sys.path.insert(0, str(Path(__file__).parent))
from phase_telemetry_validator import TelemetryValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
CONVO_WORKSPACES_ROOT = Path("/home/.z/workspaces")
STATE_DIR = Path("/home/workspace/N5/.state")
ORCHESTRATION_DIR = Path("/home/workspace/N5/builds")


class ConversationOrchestrator:
    """Coordinates multiple worker conversations with validated handoffs."""
    
    def __init__(self, orchestrator_id: str, project_name: str):
        self.orchestrator_id = orchestrator_id
        self.project_name = project_name
        self.project_dir = ORCHESTRATION_DIR / project_name
        self.orchestrator_workspace = CONVO_WORKSPACES_ROOT / orchestrator_id
        self.state_file = self.orchestrator_workspace / "orchestrator_state.json"
        self.workers = []
        self.telemetry_validator = TelemetryValidator()
        
        logger.info(f"Orchestrator: {orchestrator_id}")
        logger.info(f"Project: {project_name}")
        logger.info(f"Orchestrator workspace: {self.orchestrator_workspace}")
        
        # Ensure orchestrator workspace exists
        self.orchestrator_workspace.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize state
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load orchestrator state from file."""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        
        # Initialize new state
        return {
            "orchestrator_id": self.orchestrator_id,
            "project_name": self.project_name,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "initializing",
            "workers": {},
            "phases": {},
            "completed_phases": [],
            "failed_phases": []
        }
    
    def _save_state(self):
        """Save orchestrator state to file."""
        self.state_file.write_text(json.dumps(self.state, indent=2))
    
    def load_worker_briefs(self) -> List[Dict]:
        """Load and parse worker brief files."""
        if not self.project_dir.exists():
            logger.error(f"Project directory not found: {self.project_dir}")
            return []
        
        briefs = []
        for brief_file in sorted(self.project_dir.glob("WORKER_*.md")):
            content = brief_file.read_text()
            
            # Extract worker number from filename
            match = re.search(r'WORKER_(\d+)', brief_file.name)
            worker_num = int(match.group(1)) if match else len(briefs) + 1
            
            # Extract description from first line
            description = "Worker Task"
            lines = content.split('\n')
            if lines and lines[0].startswith('#'):
                title = lines[0].lstrip('#').strip()
                if ':' in title:
                    description = title.split(':', 1)[1].strip()
            
            # Parse dependencies
            deps = []
            for line in content.split('\n'):
                if line.startswith('**Dependencies:**'):
                    dep_text = line.split(':', 1)[1].strip()
                    if dep_text.lower() not in ['none', 'n/a']:
                        deps = [d.strip() for d in dep_text.split(',')]
            
            briefs.append({
                "number": worker_num,
                "description": description,
                "brief_file": str(brief_file),
                "brief_content": content,
                "dependencies": deps,
                "status": "pending",
                "worker_id": None,
                "telemetry_path": str(self.orchestrator_workspace / f"worker_{worker_num}_telemetry.json")
            })
        
        logger.info(f"Loaded {len(briefs)} worker briefs")
        return briefs
    
    def create_worker_assignment(self, worker_info: Dict, worker_convo_id: str):
        """Create assignment file in worker's conversation workspace."""
        worker_workspace = CONVO_WORKSPACES_ROOT / worker_convo_id
        worker_workspace.mkdir(parents=True, exist_ok=True)
        
        # Create ASSIGNMENT.md with full brief
        assignment_file = worker_workspace / "ASSIGNMENT.md"
        content = f"""# Worker Assignment

**Orchestrator:** {self.orchestrator_id}  
**Worker ID:** {worker_convo_id}  
**Project:** {self.project_name}  
**Assigned:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

---

{worker_info['brief_content']}

---

## Orchestrator Instructions

1. Read this entire assignment carefully
2. Initialize your SESSION_STATE.md with this task
3. Execute the work as described
4. Update SESSION_STATE.md with progress (use **Progress:** field)
5. When complete, update status to "complete" in SESSION_STATE.md
6. Create COMPLETION_REPORT.md with deliverables summary

**The orchestrator monitors your SESSION_STATE.md for progress updates.**

---

**Orchestrator Contact:** {self.orchestrator_id}  
**Generated:** {datetime.now(timezone.utc).isoformat()}
"""
        assignment_file.write_text(content)
        logger.info(f"  Created assignment: {assignment_file}")
        
        return str(assignment_file)
    
    def spawn_worker(self, worker_info: Dict) -> Dict:
        """
        Spawn a new Zo worker conversation.
        
        Note: This creates the assignment file, but Zo doesn't have an API
        to programmatically spawn conversations. The orchestrator user must
        manually create conversations and invoke them with the worker ID.
        
        Returns worker state dict with expected conversation ID.
        """
        # Generate worker conversation ID (user will create this)
        worker_id = f"worker_{self.project_name}_{worker_info['number']}"
        expected_convo_id = f"con_EXPECTED_{worker_id}"
        
        # Create assignment file
        assignment_file = self.create_worker_assignment(worker_info, expected_convo_id)
        
        worker_state = {
            "worker_id": worker_id,
            "expected_convo_id": expected_convo_id,
            "number": worker_info["number"],
            "description": worker_info["description"],
            "status": "pending_spawn",
            "assignment_file": assignment_file,
            "brief_file": worker_info["brief_file"],
            "spawned_at": datetime.now(timezone.utc).isoformat(),
            "last_checked": None,
            "progress": 0,
            "completion_report": None
        }
        
        logger.info(f"""
╔══════════════════════════════════════════════════════════════
║ WORKER SPAWN INSTRUCTIONS
╠══════════════════════════════════════════════════════════════
║ Worker: {worker_id}
║ Brief: {worker_info['brief_file']}
║ 
║ TO SPAWN THIS WORKER:
║ 1. Create a new Zo conversation
║ 2. Name it: "{worker_info['description']}"
║ 3. In that conversation, send message:
║    "I am {worker_id} for Build Orchestrator {self.orchestrator_id}.
║     Load and execute: file '{assignment_file}'"
║ 
║ The orchestrator will monitor for completion.
╚══════════════════════════════════════════════════════════════
""")
        
        return worker_state
    
    def generate_worker_instructions(self, worker: Dict) -> str:
        """Generate spawn instructions for a worker."""
        brief_path = worker["brief_file"]
        worker_num = worker["worker_num"]
        telemetry_path = worker["telemetry_path"]
        
        instructions = f"""
=== WORKER {worker_num} SPAWN INSTRUCTIONS ===

1. Create new conversation (spawn worker thread)

2. In that conversation, provide this assignment:

---
I am Worker {worker_num} for Build Orchestrator {self.orchestrator_id}.

MISSION: Execute task from brief: {brief_path}

INSTRUCTIONS:
1. Load and read: file '{brief_path}'
2. Execute all tasks per brief specifications
3. When complete, write telemetry to: {telemetry_path}

TELEMETRY FORMAT:
{{
  "phase_id": "worker_{worker_num}",
  "worker_id": "<your_conversation_id>",
  "timestamp": "<ISO8601>",
  "status": "complete|blocked",
  "outputs": {{
    "files": ["list", "of", "created", "files"],
    "artifacts": ["key", "deliverables"]
  }},
  "quality": {{
    "placeholders": [],
    "stubs": [],
    "incomplete": []
  }},
  "tests": {{
    "status": "passed|failed|skipped",
    "passed": 0,
    "failed": 0
  }},
  "blockers": [],
  "recommendations": ["for", "next", "phase"]
}}

CONTEXT:
- Orchestrator workspace: {self.orchestrator_workspace}
- Report completion by writing telemetry JSON to above path
- Orchestrator will validate before proceeding
---

3. Copy the conversation ID and update state:
   python3 -c "
import json
from pathlib import Path
state = json.loads(Path('{self.state_file}').read_text())
state['workers'][{worker_num - 1}]['worker_id'] = 'con_XXXXXXX'  # Replace with actual ID
state['workers'][{worker_num - 1}]['status'] = 'running'
Path('{self.state_file}').write_text(json.dumps(state, indent=2))
print('✓ Updated state with worker ID')
"
"""
        return instructions
    
    def check_worker_status(self, worker: Dict) -> str:
        """Check worker status via telemetry file in orchestrator workspace."""
        telemetry_path = Path(worker["telemetry_path"])
        
        # Check if telemetry exists (= worker complete)
        if telemetry_path.exists():
            return "complete"
        
        # Check if worker has been spawned
        if worker.get("worker_id"):
            return "running"
        
        return "pending"
    
    def validate_worker_handoff(self, worker: Dict) -> Tuple[str, Dict]:
        """Validate worker completion via telemetry."""
        telemetry_path = Path(worker["telemetry_path"])
        
        if not telemetry_path.exists():
            return "pending", {
                "decision": "pending",
                "message": "Telemetry not yet submitted"
            }
        
        logger.info(f"📊 Validating Worker {worker['worker_num']} telemetry")
        result = self.telemetry_validator.validate_handoff(telemetry_path)
        
        # Log validation decision
        decision = result["decision"]
        worker_num = worker["worker_num"]
        
        if decision == "block":
            logger.error(f"❌ Worker {worker_num} BLOCKED - Critical issues prevent advancement")
        elif decision == "allow":
            logger.warning(f"⚠️  Worker {worker_num} ALLOWED - Has concerns but can proceed")
        else:
            logger.info(f"✅ Worker {worker_num} PASSED - Clean handoff")
        
        # Log issues
        for issue in result.get("issues", []):
            severity = issue.get("severity", "unknown")
            logger.info(f"  [{severity}] {issue.get('type')}: {issue.get('detail')}")
        
        return decision, result
    
    def monitor_workers(self, interval: int = 10) -> Dict:
        """Monitor workers by checking orchestrator workspace for telemetry."""
        logger.info("\n=== MONITORING WORKERS ===")
        logger.info(f"Checking orchestrator workspace: {self.orchestrator_workspace}")
        
        validation_results = {}
        
        while True:
            all_complete = True
            
            for worker in self.workers:
                if worker["status"] == "validated":
                    continue
                
                # Check status via telemetry in orchestrator workspace
                current_status = self.check_worker_status(worker)
                worker_num = worker["worker_num"]
                
                if current_status == "complete" and worker["status"] != "validated":
                    logger.info(f"\n📊 Worker {worker_num} telemetry received")
                    
                    # Validate handoff
                    decision, result = self.validate_worker_handoff(worker)
                    validation_results[f"worker_{worker_num}"] = result
                    
                    if decision == "block":
                        logger.error(f"❌ Worker {worker_num} blocked - cannot proceed")
                        worker["status"] = "blocked"
                        return {
                            "status": "blocked",
                            "worker": worker_num,
                            "validation_results": validation_results
                        }
                    else:
                        worker["status"] = "validated"
                        logger.info(f"✅ Worker {worker_num} validated - can proceed")
                
                if worker["status"] not in ["validated", "blocked"]:
                    all_complete = False
            
            if all_complete:
                logger.info("\n✅ All workers validated!")
                break
            
            # Status summary
            logger.info(f"\nWorker Status:")
            for worker in self.workers:
                status_emoji = {
                    "pending": "⏳",
                    "running": "🔄",
                    "complete": "📊",
                    "validated": "✅",
                    "blocked": "❌"
                }.get(worker["status"], "❓")
                logger.info(f"  Worker {worker['worker_num']}: {status_emoji} {worker['status']}")
            
            logger.info(f"\nNext check in {interval}s...\n")
            time.sleep(interval)
        
        return {
            "status": "complete",
            "validation_results": validation_results
        }
    
    def _parse_session_state(self, content: str) -> Dict:
        """Parse SESSION_STATE.md for key fields."""
        info = {
            "status": "active",
            "progress": 0,
            "current_task": None,
            "raw_content": content
        }
        
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "**Status:**" in line:
                status = line.split("**Status:**")[1].strip()
                info["status"] = status.lower()
            
            elif "**Progress:**" in line:
                progress_text = line.split("**Progress:**")[1].strip()
                # Try to extract percentage
                if "%" in progress_text:
                    try:
                        pct = int(progress_text.split("%")[0].strip().split()[-1])
                        info["progress"] = pct
                    except (ValueError, IndexError):
                        pass
            
            elif line.startswith("### Current Task"):
                # Get next non-empty line
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip() and not lines[j].startswith("#"):
                        info["current_task"] = lines[j].strip()
                        break
        
        return info
    
    def validate_worker_handoff(self, worker_id: str, phase_id: str) -> Dict:
        """
        Validate worker phase completion via telemetry.
        
        Returns validation result with decision (block/allow/pass).
        """
        # Look for telemetry file in worker workspace
        worker_workspace = CONVO_WORKSPACES_ROOT / worker_id
        telemetry_path = worker_workspace / f"{phase_id}_telemetry.json"
        
        if not telemetry_path.exists():
            logger.warning(f"⚠️  No telemetry found for {worker_id}/{phase_id}")
            logger.info(f"   Expected: {telemetry_path}")
            return {
                "decision": "allow",  # Allow if no telemetry (backward compat)
                "severity": "none",
                "issues": [],
                "recommendations": ["Consider generating telemetry for validated handoffs"]
            }
        
        logger.info(f"📊 Validating telemetry: {worker_id}/{phase_id}")
        result = self.telemetry_validator.validate_handoff(telemetry_path)
        
        # Log validation decision
        decision = result["decision"]
        if decision == "block":
            logger.error(f"❌ {worker_id} BLOCKED - Critical issues prevent advancement")
        elif decision == "allow":
            logger.warning(f"⚠️  {worker_id} ALLOW - Issues noted, can advance")
        else:
            logger.info(f"✅ {worker_id} PASS - Clean handoff")
        
        # Log issues
        for issue in result.get("issues", []):
            severity = issue.get("severity", "unknown")
            issue_type = issue.get("type", "unknown")
            if severity == "critical":
                logger.error(f"   CRITICAL: {issue_type}")
            elif severity == "major":
                logger.warning(f"   MAJOR: {issue_type}")
            else:
                logger.info(f"   minor: {issue_type}")
        
        return result
    
    def monitor_workers(self, check_interval: int = 10) -> bool:
        """
        Monitor all active workers until completion or failure.
        
        Returns True if all workers completed successfully.
        """
        logger.info(f"\n{'='*70}")
        logger.info("👀 MONITORING WORKERS")
        logger.info(f"{'='*70}")
        logger.info(f"Check interval: {check_interval}s")
        
        all_complete = False
        iteration = 0
        
        while not all_complete:
            iteration += 1
            time.sleep(check_interval)
            
            logger.info(f"\n🔍 Check #{iteration} - {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
            
            status_summary = []
            active_count = 0
            complete_count = 0
            failed_count = 0
            pending_count = 0
            
            for worker_id, worker_state in self.state["workers"].items():
                status_info = self.check_worker_status(worker_state)
                current_status = status_info.get("status", "unknown")
                
                # Update state
                if current_status != worker_state.get("status"):
                    old_status = worker_state.get("status")
                    worker_state["status"] = current_status
                    logger.info(f"  {worker_id}: {old_status} → {current_status}")
                
                # Count statuses
                if current_status == "complete":
                    complete_count += 1
                    status_summary.append(f"{worker_id}:✅")
                    
                    # Add to completed list
                    if worker_id not in self.state["completed_phases"]:
                        self.state["completed_phases"].append(worker_id)
                        logger.info(f"  ✅ {worker_id} COMPLETED")
                    
                    # Validate handoff
                    validation = self.validate_worker_handoff(worker_id, worker_state["phase_id"])
                    worker_state["validation"] = validation
                    
                    # Check if blocked
                    if validation["decision"] == "block":
                        logger.error(f"\n🚫 {worker_id} blocked by quality gate")
                        logger.error("   Worker must resolve issues before advancement")
                        all_complete = False
                elif current_status in ["active", "running"]:
                    active_count += 1
                    progress = worker_state.get("progress", 0)
                    status_summary.append(f"{worker_id}:🔄{progress}%")
                    
                    # Show current task if available
                    if "session_state" in worker_state:
                        task = worker_state["session_state"].get("current_task")
                        if task:
                            logger.info(f"  🔄 {worker_id}: {task[:60]}")
                
                elif current_status in ["failed", "error"]:
                    failed_count += 1
                    status_summary.append(f"{worker_id}:❌")
                    
                    if worker_id not in self.state["failed_phases"]:
                        self.state["failed_phases"].append(worker_id)
                        logger.error(f"  ❌ {worker_id} FAILED")
                
                else:  # pending_spawn, unknown
                    pending_count += 1
                    status_summary.append(f"{worker_id}:⏳")
            
            # Progress summary
            total = len(self.state["workers"])
            logger.info(f"\n📊 Status: {' | '.join(status_summary)}")
            logger.info(f"   Complete: {complete_count}/{total} | Active: {active_count} | Failed: {failed_count} | Pending: {pending_count}")
            
            # Check if all complete or failed
            if complete_count + failed_count == total:
                all_complete = True
            
            # Save state after each check
            self._save_state()
        
        # Final status
        success = failed_count == 0 and complete_count == len(self.state["workers"])
        return success
    
    def generate_summary_report(self) -> str:
        """Generate final orchestrator summary report."""
        report_lines = [
            "# Build Orchestrator Summary Report",
            "",
            f"**Project:** {self.project_name}",
            f"**Orchestrator:** {self.orchestrator_id}",
            f"**Started:** {self.state['started_at']}",
            f"**Completed:** {datetime.now(timezone.utc).isoformat()}",
            "",
            "---",
            "",
            "## Workers",
            ""
        ]
        
        for worker_id, worker_state in self.state["workers"].items():
            status_icon = {
                "complete": "✅",
                "active": "🔄",
                "failed": "❌",
                "pending_spawn": "⏳"
            }.get(worker_state.get("status"), "❓")
            
            report_lines.append(f"### {status_icon} {worker_id}")
            report_lines.append(f"- **Status:** {worker_state.get('status')}")
            report_lines.append(f"- **Description:** {worker_state.get('description')}")
            
            if worker_state.get("actual_convo_id"):
                report_lines.append(f"- **Conversation:** {worker_state['actual_convo_id']}")
            
            if worker_state.get("completion_report"):
                report_lines.append(f"- **Report:** {worker_state[completion_report]}: cannot open `{worker_state[completion_report]}' (No such file or directory)")
            
            report_lines.append("")
        
        report_lines.extend([
            "---",
            "",
            "## Summary",
            f"- **Total Workers:** {len(self.state['workers'])}",
            f"- **Completed:** {len(self.state['completed_phases'])}",
            f"- **Failed:** {len(self.state['failed_phases'])}",
            "",
        ])
        
        if self.state["failed_phases"]:
            report_lines.append("### ⚠️ Failed Workers")
            for worker_id in self.state["failed_phases"]:
                report_lines.append(f"- {worker_id}")
            report_lines.append("")
        
        report_lines.append(f"**Status:** {'✅ SUCCESS' if not self.state['failed_phases'] else '❌ PARTIAL FAILURE'}")
        
        return "\n".join(report_lines)
    
    def run(self, auto_spawn: bool = False, monitor_interval: int = 10) -> int:
        """
        Run the orchestrator: load briefs, spawn workers, monitor completion.
        
        Args:
            auto_spawn: If True, automatically spawn workers (manual by default)
            monitor_interval: Seconds between worker status checks
        
        Returns:
            0 if all workers complete successfully, 1 otherwise
        """
        logger.info("="*70)
        logger.info("🎯 CONVERSATION ORCHESTRATOR")
        logger.info(f"   Project: {self.project_name}")
        logger.info(f"   Orchestrator: {self.orchestrator_id}")
        logger.info("="*70)
        
        # Update status
        self.state["status"] = "running"
        self._save_state()
        
        # Load worker briefs
        worker_briefs = self.load_worker_briefs()
        if not worker_briefs:
            logger.error("❌ No worker briefs found - cannot proceed")
            return 1
        
        # Spawn workers
        logger.info(f"\n{'='*70}")
        logger.info("🚀 SPAWNING WORKERS")
        logger.info(f"{'='*70}")
        
        for worker_info in worker_briefs:
            worker_state = self.spawn_worker(worker_info)
            self.state["workers"][worker_state["worker_id"]] = worker_state
            self._save_state()
        
        # Wait for user to spawn conversations
        if not auto_spawn:
            logger.info(f"\n{'='*70}")
            logger.info("⏸️  WAITING FOR MANUAL WORKER SPAWN")
            logger.info(f"{'='*70}")
            logger.info("Follow the instructions above to create worker conversations.")
            logger.info("Orchestrator will begin monitoring in 30 seconds...")
            logger.info("(Press Ctrl+C to cancel and spawn workers manually later)")
            time.sleep(30)
        
        # Monitor workers
        success = self.monitor_workers(check_interval=monitor_interval)
        
        # Generate summary
        logger.info(f"\n{'='*70}")
        logger.info("📊 GENERATING SUMMARY REPORT")
        logger.info(f"{'='*70}")
        
        summary = self.generate_summary_report()
        summary_file = self.orchestrator_workspace / "ORCHESTRATOR_SUMMARY.md"
        summary_file.write_text(summary)
        
        logger.info(f"✓ Summary report: {summary_file}")
        
        # Update final status
        self.state["status"] = "complete" if success else "partial"
        self.state["completed_at"] = datetime.now(timezone.utc).isoformat()
        self._save_state()
        
        # Final verdict
        if success:
            logger.info("\n✅ ALL WORKERS COMPLETED SUCCESSFULLY")
            return 0
        else:
            logger.warning(f"\n⚠️ BUILD INCOMPLETE: {len(self.state['failed_phases'])} workers failed")
            return 1


def main():
    parser = argparse.ArgumentParser(
        description="Conversation Orchestrator - Coordinate multiple Zo worker conversations"
    )
    parser.add_argument(
        "project_name", nargs="?", default=None,
        help="Project name (must have worker briefs in N5/builds/<project>/)"
    )
    parser.add_argument(
        "--orchestrator-id",
        default="con_unknown",
        help="Orchestrator conversation ID"
    )
    parser.add_argument(
        "--auto-spawn",
        action="store_true",
        help="Automatically spawn workers (default: manual spawn with instructions)"
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=10,
        help="Seconds between worker status checks (default: 10)"
    )
    parser.add_argument(
        "--list-projects",
        action="store_true",
        help="List available orchestration projects"
    )
    
    args = parser.parse_args()
    
    # List projects if requested
    if args.list_projects:
        if ORCHESTRATION_DIR.exists():
            projects = [d.name for d in ORCHESTRATION_DIR.iterdir() if d.is_dir()]
            if projects:
                logger.info("Available orchestration projects:")
                for proj in projects:
                    logger.info(f"  - {proj}")
            else:
                logger.info("No orchestration projects found")
        else:
            logger.info(f"Orchestration directory not found: {ORCHESTRATION_DIR}")
        return 0
    
    # Run orchestrator
    orchestrator = ConversationOrchestrator(
        orchestrator_id=args.orchestrator_id,
        project_name=args.project_name
    )
    
    return orchestrator.run(
        auto_spawn=args.auto_spawn,
        monitor_interval=args.check_interval
    )


if __name__ == "__main__":
    exit(main())
