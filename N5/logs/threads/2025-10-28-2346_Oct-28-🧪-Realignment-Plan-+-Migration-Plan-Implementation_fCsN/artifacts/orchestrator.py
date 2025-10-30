#!/usr/bin/env python3
"""Build Orchestrator for N5 Platonic Realignment"""
import json
import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE_DIR = Path("/home/.z/workspaces/con_nT5eqPlvQ3TIfCsN")
STATE_FILE = WORKSPACE_DIR / "orchestrator_state.json"

PHASES = [
    {
        "id": "phase1_survey",
        "name": "Survey & Protect",
        "script": "phase1_survey.py",
        "parallel_safe": True,
        "required": True
    },
    {
        "id": "phase2_n5_rationalization",
        "name": "N5 Rationalization",
        "script": "phase2_n5_rationalization.py",
        "parallel_safe": False,
        "required": True,
        "depends_on": ["phase1_survey"]
    },
    {
        "id": "phase3_backup_consolidation",
        "name": "Backup Consolidation",
        "script": "phase3_backup_consolidation.py",
        "parallel_safe": True,
        "required": True,
        "depends_on": ["phase1_survey"]
    },
    {
        "id": "phase4_inbox_cleanup",
        "name": "Inbox Cleanup",
        "script": "phase4_inbox_cleanup.py",
        "parallel_safe": True,
        "required": True,
        "depends_on": ["phase1_survey"]
    },
]

def load_state():
    """Load orchestrator state"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return None

def save_state(state):
    """Save orchestrator state"""
    STATE_FILE.write_text(json.dumps(state, indent=2))

def run_phase(phase_id, script_name, dry_run=False):
    """Execute a phase script"""
    script_path = WORKSPACE_DIR / script_name
    
    if not script_path.exists():
        logger.error(f"Script not found: {script_path}")
        return {"success": False, "error": "Script not found"}
    
    # Make executable
    script_path.chmod(0o755)
    
    # Run script
    cmd = ["python3", str(script_path)]
    if dry_run:
        cmd.append("--dry-run")
    else:
        cmd.append("--execute")
    
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Log output
        if result.stdout:
            for line in result.stdout.split("\n"):
                if line.strip():
                    logger.info(f"  {line}")
        
        if result.stderr:
            for line in result.stderr.split("\n"):
                if line.strip():
                    logger.warning(f"  {line}")
        
        success = result.returncode == 0
        
        # Load phase results
        results_file = WORKSPACE_DIR / f"{phase_id}_results.json"
        phase_results = None
        if results_file.exists():
            phase_results = json.loads(results_file.read_text())
        
        return {
            "success": success,
            "returncode": result.returncode,
            "results": phase_results
        }
        
    except Exception as e:
        logger.error(f"Phase execution failed: {e}")
        return {"success": False, "error": str(e)}

def check_dependencies(phase, state):
    """Check if phase dependencies are satisfied"""
    if "depends_on" not in phase:
        return True
    
    for dep_id in phase["depends_on"]:
        dep_status = state["phases"][dep_id]["status"]
        if dep_status != "complete":
            return False
    
    return True

def main(dry_run=False, start_from=None):
    """Run orchestrator"""
    logger.info(f"=== BUILD ORCHESTRATOR: N5 PLATONIC REALIGNMENT {'[DRY RUN]' if dry_run else ''} ===")
    logger.info(f"Orchestrator thread: con_nT5eqPlvQ3TIfCsN")
    
    # Load or initialize state
    state = load_state()
    if not state:
        logger.error("Orchestrator state not initialized")
        return 1
    
    state["status"] = "running"
    state["dry_run"] = dry_run
    save_state(state)
    
    # Execute phases
    for phase in PHASES:
        phase_id = phase["id"]
        
        # Skip if starting from a later phase
        if start_from and phase_id != start_from and state["phases"][phase_id]["status"] != "pending":
            continue
        
        # Check dependencies
        if not check_dependencies(phase, state):
            logger.info(f"⏳ {phase['name']}: Waiting for dependencies")
            continue
        
        logger.info(f"\n{'='*60}")
        logger.info(f"PHASE: {phase['name']}")
        logger.info(f"{'='*60}\n")
        
        # Update state
        state["phases"][phase_id]["status"] = "running"
        state["phases"][phase_id]["started"] = datetime.now().isoformat()
        save_state(state)
        
        # Run phase
        result = run_phase(phase_id, phase["script"], dry_run=dry_run)
        
        # Update state with results
        if result["success"]:
            state["phases"][phase_id]["status"] = "complete"
            state["phases"][phase_id]["completed"] = datetime.now().isoformat()
            state["phases"][phase_id]["results"] = result.get("results")
            logger.info(f"✅ {phase['name']}: COMPLETE")
        else:
            state["phases"][phase_id]["status"] = "failed"
            state["phases"][phase_id]["error"] = result.get("error", "Unknown error")
            state["errors"].append({
                "phase": phase_id,
                "error": result.get("error"),
                "timestamp": datetime.now().isoformat()
            })
            logger.error(f"❌ {phase['name']}: FAILED")
            
            if phase.get("required"):
                logger.error("Required phase failed. Aborting.")
                state["status"] = "failed"
                save_state(state)
                return 1
        
        save_state(state)
    
    # Final status
    all_complete = all(
        p["status"] == "complete" 
        for p in state["phases"].values()
    )
    
    if all_complete:
        state["status"] = "complete"
        state["completed_at"] = datetime.now().isoformat()
        logger.info("\n✅ ALL PHASES COMPLETE")
    else:
        state["status"] = "partial"
        logger.warning("\n⚠️  Some phases incomplete")
    
    save_state(state)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("ORCHESTRATOR SUMMARY")
    logger.info("="*60)
    for phase_id, phase_state in state["phases"].items():
        status_icon = {
            "complete": "✅",
            "running": "🔄",
            "failed": "❌",
            "pending": "⏳"
        }.get(phase_state["status"], "❓")
        logger.info(f"{status_icon} {phase_id}: {phase_state['status']}")
    
    return 0 if all_complete else 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--start-from", help="Resume from specific phase")
    args = parser.parse_args()
    
    exit(main(dry_run=not args.execute, start_from=args.start_from))
