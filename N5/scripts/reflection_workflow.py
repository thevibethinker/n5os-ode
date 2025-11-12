#!/usr/bin/env python3
"""
Reflection Processing Full Pipeline Orchestrator
Handles: Drive sync → Classification → Block generation

Usage:
  python3 reflection_workflow.py --full-pipeline
"""

import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone
import subprocess
import sys
from typing import Dict, List, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
SCRIPTS_DIR = WORKSPACE / "N5" / "scripts"
RECORDS_DIR = WORKSPACE / "N5" / "records" / "reflections"
STATE_FILE = RECORDS_DIR / ".state.json"
OUTPUTS_DIR = RECORDS_DIR / "outputs"
INCOMING_DIR = RECORDS_DIR / "incoming"
PROCESSED_DIR = RECORDS_DIR / "processed"
ERROR_LOG = WORKSPACE / "N5" / "logs" / "reflection_errors.jsonl"
DRIVE_FOLDER_ID = "16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV"


def ensure_dirs():
    """Ensure all required directories exist"""
    for d in [RECORDS_DIR, OUTPUTS_DIR, INCOMING_DIR, PROCESSED_DIR, ERROR_LOG.parent]:
        d.mkdir(parents=True, exist_ok=True)


def load_state() -> Dict[str, Any]:
    """Load workflow state"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
    
    return {
        "processed_file_ids": [],
        "registry_entries": {},
        "last_run": None,
        "consecutive_failures": 0,
        "cycle": 0
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


def run_subprocess(cmd: List[str], timeout: int = 300) -> Dict:
    """Execute subprocess with error handling"""
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✓ Command completed successfully")
            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": 0
            }
        else:
            logger.error(f"✗ Command failed with exit code {result.returncode}")
            if result.stderr:
                logger.error(f"stderr: {result.stderr[:500]}")
            return {
                "status": "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout}s")
        return {"status": "timeout", "error": "Command execution timeout"}
    except Exception as e:
        logger.error(f"Exception executing command: {e}", exc_info=True)
        return {"status": "exception", "error": str(e)}


def ingest_from_drive() -> Dict:
    """Phase 1: Ingest reflections from Google Drive"""
    logger.info("\n=== PHASE 1: INGESTION FROM DRIVE ===")
    logger.info("⚠️  Note: Ingest requires Zo Drive API. Using existing files in incoming directory.")
    
    # Count files already present
    incoming_files = list(INCOMING_DIR.glob("*.transcript.jsonl"))
    logger.info(f"Found {len(incoming_files)} transcript files already in incoming directory")
    
    return {
        "status": "skipped",
        "reason": "Drive ingest requires Zo Drive API authentication",
        "files_found": len(incoming_files)
    }


def classify_reflections() -> Dict:
    """Phase 2: Classify reflections"""
    logger.info("\n=== PHASE 2: CLASSIFICATION ===")
    
    # Find all transcript files that need classification
    incoming_files = list(INCOMING_DIR.glob("*.transcript.jsonl"))
    logger.info(f"Found {len(incoming_files)} transcripts to classify")
    
    classified_count = 0
    errors = []
    
    for transcript_file in incoming_files:
        classification_file = transcript_file.with_suffix(".classification.json")
        
        # Skip if already classified
        if classification_file.exists():
            logger.info(f"  ✓ {transcript_file.name} (already classified)")
            continue
        
        logger.info(f"  Classifying: {transcript_file.name}")
        result = run_subprocess([
            "python3", str(SCRIPTS_DIR / "reflection_classifier.py"),
            "--input", str(transcript_file),
            "--output", str(classification_file)
        ])
        
        if result["status"] == "success":
            classified_count += 1
        else:
            errors.append((transcript_file.name, result.get("stderr", "")))
            log_error("classify", f"Failed to classify {transcript_file.name}", 
                     {"error": result.get("stderr", "")})
    
    logger.info(f"Classification complete: {classified_count} files newly classified")
    
    return {
        "status": "success" if not errors else "partial",
        "classified_count": classified_count,
        "errors": len(errors),
        "total_files": len(incoming_files)
    }


def generate_blocks() -> Dict:
    """Phase 3: Generate reflection blocks"""
    logger.info("\n=== PHASE 3: BLOCK GENERATION ===")
    
    return run_subprocess([
        "python3", str(SCRIPTS_DIR / "reflection_block_generator.py"),
        "--process-all",
        "--output", str(OUTPUTS_DIR)
    ])


def verify_outputs() -> Dict:
    """Verify generated outputs"""
    logger.info("\n=== VERIFICATION ===")
    
    if not OUTPUTS_DIR.exists():
        logger.warning("Outputs directory doesn't exist")
        return {"blocks_generated": 0, "status": "no_output_dir"}
    
    # Count various output types
    block_files = list(OUTPUTS_DIR.glob("*_blocks.json"))
    classified_files = list(OUTPUTS_DIR.glob("*_classified.json"))
    
    logger.info(f"✓ Found {len(block_files)} block files")
    logger.info(f"✓ Found {len(classified_files)} classified files")
    
    return {
        "blocks_generated": len(block_files),
        "classified_files": len(classified_files),
        "status": "verified",
        "output_dir": str(OUTPUTS_DIR)
    }


def count_incoming_files() -> int:
    """Count files in incoming directory"""
    if not INCOMING_DIR.exists():
        return 0
    return len(list(INCOMING_DIR.glob("*.transcript.jsonl")))


def main(full_pipeline: bool = True) -> int:
    """Main workflow execution
    
    Args:
        full_pipeline: If True, run complete pipeline (ingest → classify → generate)
        
    Returns:
        Exit code (0=success, 1=failure)
    """
    try:
        ensure_dirs()
        
        logger.info("=" * 70)
        logger.info("REFLECTION PROCESSING PIPELINE")
        logger.info("=" * 70)
        logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        logger.info(f"Pipeline: {'FULL' if full_pipeline else 'PARTIAL'}")
        
        state = load_state()
        logger.info(f"State loaded: {len(state.get('processed_file_ids', []))} previously processed")
        
        results = {
            "start_time": datetime.now(timezone.utc).isoformat(),
            "phases": {},
            "final_stats": {}
        }
        
        # Phase 1: Ingest
        logger.info(f"\n[1/3] Ingesting reflections from Drive (folder: {DRIVE_FOLDER_ID})")
        ingest_result = ingest_from_drive()
        results["phases"]["ingest"] = ingest_result
        
        if ingest_result["status"] != "success":
            logger.warning(f"⚠️  Ingestion had issues, continuing...")
            log_error("ingest", ingest_result.get("stderr", "Unknown error"))
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        else:
            state["consecutive_failures"] = 0
        
        incoming_count = count_incoming_files()
        logger.info(f"Files ready for processing: {incoming_count}")
        
        if incoming_count == 0:
            logger.info("No files to process, exiting")
            return 0
        
        # Phase 2: Classify
        logger.info(f"\n[2/3] Classifying {incoming_count} reflections")
        classify_result = classify_reflections()
        results["phases"]["classify"] = classify_result
        
        if classify_result["status"] != "success":
            logger.warning(f"⚠️  Classification had issues")
            log_error("classify", classify_result.get("stderr", "Unknown error"))
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        else:
            state["consecutive_failures"] = 0
        
        # Phase 3: Generate Blocks
        logger.info(f"\n[3/3] Generating reflection blocks")
        generate_result = generate_blocks()
        results["phases"]["generate"] = generate_result
        
        if generate_result["status"] != "success":
            logger.warning(f"⚠️  Block generation had issues")
            log_error("generate", generate_result.get("stderr", "Unknown error"))
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        else:
            state["consecutive_failures"] = 0
        
        # Verify outputs
        verify_result = verify_outputs()
        results["final_stats"] = verify_result
        
        # Update state
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        state["cycle"] = state.get("cycle", 0) + 1
        save_state(state)
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Cycle: {state['cycle']}")
        logger.info(f"Files processed: {incoming_count}")
        logger.info(f"Blocks generated: {verify_result.get('blocks_generated', 0)}")
        logger.info(f"Consecutive failures: {state['consecutive_failures']}")
        
        # Check failure threshold
        if state["consecutive_failures"] >= 3:
            logger.error(f"⚠️  ALERT: Consecutive failures threshold reached ({state['consecutive_failures']})")
            log_error("threshold_exceeded", f"Consecutive failures: {state['consecutive_failures']}")
        
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"FATAL: Workflow error: {e}", exc_info=True)
        log_error("workflow_fatal", str(e))
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reflection processing full pipeline orchestrator"
    )
    parser.add_argument(
        "--full-pipeline",
        action="store_true",
        default=True,
        help="Run complete pipeline (ingest → classify → generate)"
    )
    
    args = parser.parse_args()
    sys.exit(main(full_pipeline=args.full_pipeline))
