#!/usr/bin/env python3
"""
Zo-compatible Reflection Workflow Orchestrator
Handles Drive sync, classification, and block generation with Zo Drive API integration.

This script is designed to be run by Zo with Drive API access enabled.
"""

import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone
import subprocess
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
SCRIPTS_DIR = WORKSPACE / "N5/scripts"
RECORDS_DIR = WORKSPACE / "N5/records/reflections"
STATE_FILE = RECORDS_DIR / ".state.json"
OUTPUTS_DIR = RECORDS_DIR / "outputs"
INCOMING_DIR = RECORDS_DIR / "incoming"
ERROR_LOG = WORKSPACE / "N5/logs/reflection_errors.jsonl"


def load_state() -> Dict[str, Any]:
    """Load workflow state"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "processed_file_ids": [],
        "registry_entries": {},
        "last_run": None,
        "consecutive_failures": 0
    }


def save_state(state: Dict[str, Any]) -> bool:
    """Save workflow state"""
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
        return True
    except Exception as e:
        logger.error(f"Failed to save state: {e}")
        return False


def log_error(component: str, error: str, context: Dict = None) -> bool:
    """Log error to error log"""
    try:
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": component,
            "error": error,
            "context": context or {}
        }
        with open(ERROR_LOG, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        return True
    except Exception as e:
        logger.error(f"Failed to log error: {e}")
        return False


def run_subprocess(cmd: List[str], dry_run: bool = False) -> Dict:
    """Execute subprocess with error handling"""
    logger.info(f"Running: {' '.join(cmd)}")
    
    if dry_run:
        logger.info("[DRY RUN] Would execute command")
        return {"status": "success", "stdout": "", "stderr": ""}
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info(f"✓ Command completed successfully")
            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        else:
            logger.error(f"✗ Command failed with exit code {result.returncode}")
            if result.stderr:
                logger.error(f"stderr: {result.stderr}")
            return {
                "status": "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
    except subprocess.TimeoutExpired:
        logger.error("Command timed out after 5 minutes")
        return {"status": "timeout", "error": "Command execution timeout"}
    except Exception as e:
        logger.error(f"Exception executing command: {e}", exc_info=True)
        return {"status": "exception", "error": str(e)}


def classify_reflections(dry_run: bool = False) -> Dict:
    """Phase 2: Classify new transcripts"""
    logger.info("=== Phase 2: Classification ===")
    
    return run_subprocess(
        ["python3", str(SCRIPTS_DIR / "reflection_classifier.py"),
         "--input-dir", str(INCOMING_DIR)],
        dry_run=dry_run
    )


def generate_blocks(dry_run: bool = False) -> Dict:
    """Phase 3: Generate block content"""
    logger.info("=== Phase 3: Block Generation ===")
    
    return run_subprocess(
        ["python3", str(SCRIPTS_DIR / "reflection_block_generator.py"),
         "--input-dir", str(INCOMING_DIR)],
        dry_run=dry_run
    )


def verify_outputs() -> Dict:
    """Verify generated blocks"""
    if not OUTPUTS_DIR.exists():
        logger.warning("Outputs directory doesn't exist")
        return {"blocks_generated": 0, "status": "no_output_dir"}
    
    block_files = list(OUTPUTS_DIR.glob("*_blocks.json"))
    logger.info(f"✓ Found {len(block_files)} block files in {OUTPUTS_DIR}")
    
    return {
        "blocks_generated": len(block_files),
        "status": "verified",
        "output_dir": str(OUTPUTS_DIR)
    }


def main(folder_id: str, dry_run: bool = False, full_pipeline: bool = True) -> int:
    """Main workflow execution
    
    Args:
        folder_id: Google Drive folder ID
        dry_run: If True, don't make changes
        full_pipeline: If True, run complete pipeline
        
    Returns:
        Exit code (0=success, 1=failure)
    """
    try:
        logger.info("=" * 60)
        logger.info("REFLECTION WORKFLOW (Zo-Compatible)")
        logger.info("=" * 60)
        
        if dry_run:
            logger.info("[DRY RUN MODE] No changes will be made")
        
        # Load current state
        state = load_state()
        logger.info(f"✓ Loaded state: {len(state.get('processed_file_ids', []))} files processed")
        
        # Phase 1: Ingestion is handled by Zo Drive API in scheduled task context
        # Files should already be synced to INCOMING_DIR
        incoming_files = list(INCOMING_DIR.glob("*.transcript.jsonl")) if INCOMING_DIR.exists() else []
        logger.info(f"Found {len(incoming_files)} transcript files to process")
        
        if not incoming_files:
            logger.info("No new files to process")
            return 0
        
        # Phase 2: Classification
        classify_result = classify_reflections(dry_run)
        if classify_result["status"] != "success":
            logger.warning(f"Classification phase issue: {classify_result.get('stderr', '')}")
            log_error("classification", str(classify_result))
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        else:
            state["consecutive_failures"] = 0
        
        # Phase 3: Block Generation
        generate_result = generate_blocks(dry_run)
        if generate_result["status"] != "success":
            logger.warning(f"Generation phase issue: {generate_result.get('stderr', '')}")
            log_error("block_generation", str(generate_result))
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        else:
            state["consecutive_failures"] = 0
        
        # Verify outputs
        verify_result = verify_outputs()
        logger.info(f"✓ Output verification: {verify_result['blocks_generated']} blocks generated")
        
        # Update state
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        state["consecutive_failures"] = state.get("consecutive_failures", 0)
        save_state(state)
        
        # Check failure threshold
        if state["consecutive_failures"] >= 3:
            logger.error(f"⚠️ Consecutive failures threshold reached ({state['consecutive_failures']})")
            log_error("threshold_exceeded", f"Consecutive failures: {state['consecutive_failures']}")
        
        logger.info("=" * 60)
        logger.info("WORKFLOW COMPLETE")
        logger.info(f"Files processed: {len(incoming_files)}")
        logger.info(f"Blocks generated: {verify_result['blocks_generated']}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Workflow error: {e}", exc_info=True)
        log_error("workflow_fatal", str(e))
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zo-compatible reflection workflow")
    parser.add_argument("--folder-id", default="16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV",
                        help="Google Drive folder ID")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--full-pipeline", action="store_true", default=True,
                        help="Run complete pipeline")
    
    args = parser.parse_args()
    exit(main(args.folder_id, args.dry_run, args.full_pipeline))
