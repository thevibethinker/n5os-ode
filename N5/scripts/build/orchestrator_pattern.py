#!/usr/bin/env python3
"""Build Orchestrator v2 - Parallel Worker Execution"""
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE_DIR = Path("/home/.z/workspaces/con_nT5eqPlvQ3TIfCsN")
STATE_FILE = WORKSPACE_DIR / "orchestrator_state.json"
WORKER_DIR = WORKSPACE_DIR / "workers"

PHASES = [
    {
        "id": "phase1_survey",
        "name": "Survey & Protect",
        "script": "phase1_survey.py",
        "parallel": False,
        "required": True,
        "depends_on": []
    },
    {
        "id": "phase2_n5_rationalization",
        "name": "N5 Rationalization",
        "script": "phase2_n5_rationalization.py",
        "parallel": False,  # Must run solo due to filesystem writes
        "required": True,
        "depends_on": ["phase1_survey"]
    },
    {
        "id": "phase3_backup_consolidation",
        "name": "Backup Consolidation",
        "script": "phase3_backup_consolidation.py",
        "parallel": True,
        "required": True,
        "depends_on": ["phase1_survey"]
    },
    {
        "id": "phase4_inbox_cleanup",
        "name": "Inbox Cleanup",
        "script": "phase4_inbox_cleanup.py",
        "parallel": True,
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

def spawn_worker(phase_id: str, script_name: str, dry_run: bool) -> Dict:
    """Spawn a worker process for a phase"""
    script_path = WORKSPACE_DIR / script_name
    
    # Create worker log files
    WORKER_DIR.mkdir(exist_ok=True)
    log_file = WORKER_DIR / f"{phase_id}.log"
    pid_file = WORKER_DIR / f"{phase_id}.pid"
    
    # Prepare command
    cmd = ["python3", str(script_path)]
    if dry_run:
        cmd.append("--dry-run")
    else:
        cmd.append("--execute")
    
    logger.info(f"🚀 Spawning worker: {phase_id}")
    logger.info(f"   Command: {' '.join(cmd)}")
    logger.info(f"   Log: {log_file}")
    
    try:
        # Spawn background process
        process = subprocess.Popen(
            cmd,
            stdout=open(log_file, 'w'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
        # Save PID
        pid_file.write_text(str(process.pid))
        
        logger.info(f"✓ Worker spawned: PID {process.pid}")
        
        return {
            "pid": process.pid,
            "log_file": str(log_file),
            "started_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to spawn worker: {e}")
        return {"error": str(e)}

def check_worker_status(phase_id: str, worker_info: Dict) -> str:
    """Check if worker is still running"""
    pid_file = WORKER_DIR / f"{phase_id}.pid"
    results_file = WORKSPACE_DIR / f"{phase_id}_results.json"
    
    # Check if results file exists
    if results_file.exists():
        return "complete"
    
    # Check if process is still running
    if "pid" in worker_info:
        pid = worker_info["pid"]
        try:
            # Check if process exists
            subprocess.run(["ps", "-p", str(pid)], capture_output=True, check=True)
            return "running"
        except subprocess.CalledProcessError:
            # Process ended but no results file = failed
            return "failed"
    
    return "unknown"

def get_worker_logs(phase_id: str, last_n_lines: int = 10) -> List[str]:
    """Get last N lines from worker log"""
    log_file = WORKER_DIR / f"{phase_id}.log"
    if not log_file.exists():
        return []
    
    try:
        result = subprocess.run(
            ["tail", "-n", str(last_n_lines), str(log_file)],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split("\n")
    except Exception:
        return []

def run_sequential_phase(phase_id: str, script_name: str, dry_run: bool) -> Dict:
    """Run a phase sequentially (blocking)"""
    script_path = WORKSPACE_DIR / script_name
    
    cmd = ["python3", str(script_path)]
    if dry_run:
        cmd.append("--dry-run")
    else:
        cmd.append("--execute")
    
    logger.info(f"⚙️  Running sequential: {phase_id}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Show output
        if result.stdout:
            for line in result.stdout.split("\n"):
                if line.strip():
                    logger.info(f"  {line}")
        
        success = result.returncode == 0
        
        # Load results
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

def main(dry_run=False):
    """Run orchestrator with parallel workers"""
    logger.info("="*70)
    logger.info("🎯 BUILD ORCHESTRATOR V2: PARALLEL WORKER EXECUTION")
    logger.info(f"   Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    logger.info(f"   Orchestrator: con_nT5eqPlvQ3TIfCsN")
    logger.info("="*70)
    
    # Load state
    state = load_state()
    if not state:
        logger.error("Orchestrator state not initialized")
        return 1
    
    state["status"] = "running"
    state["execution_mode"] = "parallel_workers"
    state["worker_dir"] = str(WORKER_DIR)
    save_state(state)
    
    # PHASE 1: Sequential (required baseline)
    logger.info("\n" + "="*70)
    logger.info("📋 PHASE 1: SURVEY & PROTECT (Sequential)")
    logger.info("="*70)
    
    phase1 = PHASES[0]
    state["phases"][phase1["id"]]["status"] = "running"
    state["phases"][phase1["id"]]["started"] = datetime.now().isoformat()
    save_state(state)
    
    result = run_sequential_phase(phase1["id"], phase1["script"], dry_run)
    
    if not result["success"]:
        logger.error("❌ Phase 1 FAILED - Cannot proceed")
        state["phases"][phase1["id"]]["status"] = "failed"
        state["status"] = "failed"
        save_state(state)
        return 1
    
    state["phases"][phase1["id"]]["status"] = "complete"
    state["phases"][phase1["id"]]["completed"] = datetime.now().isoformat()
    state["phases"][phase1["id"]]["results"] = result.get("results")
    save_state(state)
    
    logger.info("✅ Phase 1 COMPLETE")
    
    # PHASES 2, 3, 4: Parallel workers
    logger.info("\n" + "="*70)
    logger.info("🚀 SPAWNING PARALLEL WORKERS (Phases 2, 3, 4)")
    logger.info("="*70)
    
    workers = {}
    parallel_phases = PHASES[1:]  # Phases 2, 3, 4
    
    for phase in parallel_phases:
        phase_id = phase["id"]
        logger.info(f"\n🔧 {phase['name']}")
        
        worker_info = spawn_worker(phase_id, phase["script"], dry_run)
        
        if "error" in worker_info:
            logger.error(f"❌ Failed to spawn worker: {worker_info['error']}")
            state["phases"][phase_id]["status"] = "failed"
            state["phases"][phase_id]["error"] = worker_info["error"]
        else:
            workers[phase_id] = worker_info
            state["phases"][phase_id]["status"] = "running"
            state["phases"][phase_id]["started"] = datetime.now().isoformat()
            state["phases"][phase_id]["worker"] = worker_info
        
        save_state(state)
    
    # Monitor workers
    logger.info("\n" + "="*70)
    logger.info("👀 MONITORING WORKERS")
    logger.info("="*70)
    
    all_complete = False
    check_interval = 2  # seconds
    last_log_update = {}
    
    while not all_complete:
        time.sleep(check_interval)
        
        status_line = []
        all_done = True
        
        for phase_id, worker_info in workers.items():
            status = check_worker_status(phase_id, worker_info)
            
            if status == "complete":
                if state["phases"][phase_id]["status"] != "complete":
                    # Just completed
                    state["phases"][phase_id]["status"] = "complete"
                    state["phases"][phase_id]["completed"] = datetime.now().isoformat()
                    
                    # Load results
                    results_file = WORKSPACE_DIR / f"{phase_id}_results.json"
                    if results_file.exists():
                        state["phases"][phase_id]["results"] = json.loads(results_file.read_text())
                    
                    save_state(state)
                    logger.info(f"✅ {phase_id}: COMPLETE")
                
                status_line.append(f"{phase_id}:✅")
            
            elif status == "running":
                all_done = False
                status_line.append(f"{phase_id}:🔄")
                
                # Show recent logs (every 10 checks)
                if phase_id not in last_log_update:
                    last_log_update[phase_id] = 0
                
                last_log_update[phase_id] += 1
                if last_log_update[phase_id] >= 5:
                    last_log_update[phase_id] = 0
                    recent_logs = get_worker_logs(phase_id, 2)
                    if recent_logs:
                        logger.info(f"  {phase_id}: {recent_logs[-1][:80]}")
            
            elif status == "failed":
                if state["phases"][phase_id]["status"] != "failed":
                    state["phases"][phase_id]["status"] = "failed"
                    save_state(state)
                    logger.error(f"❌ {phase_id}: FAILED")
                
                status_line.append(f"{phase_id}:❌")
            
            else:
                all_done = False
                status_line.append(f"{phase_id}:❓")
        
        # Progress indicator
        logger.info(f"📊 Status: {' | '.join(status_line)}")
        
        all_complete = all_done
    
    # Final summary
    logger.info("\n" + "="*70)
    logger.info("📊 ORCHESTRATOR SUMMARY")
    logger.info("="*70)
    
    for phase_id, phase_state in state["phases"].items():
        status_icon = {
            "complete": "✅",
            "running": "🔄",
            "failed": "❌",
            "pending": "⏳"
        }.get(phase_state["status"], "❓")
        logger.info(f"{status_icon} {phase_id}: {phase_state['status']}")
    
    # Check if all required phases completed
    all_success = all(
        state["phases"][p["id"]]["status"] == "complete"
        for p in PHASES if p.get("required")
    )
    
    if all_success:
        state["status"] = "complete"
        state["completed_at"] = datetime.now().isoformat()
        logger.info("\n✅ ALL PHASES COMPLETE")
    else:
        state["status"] = "partial"
        logger.warning("\n⚠️  Some phases failed or incomplete")
    
    save_state(state)
    
    return 0 if all_success else 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    
    exit(main(dry_run=not args.execute))
