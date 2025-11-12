#!/usr/bin/env python3
"""
Reflection Pipeline Runner (Zo-integrated version)
Handles full pipeline: ingest → classify → generate → synthesize
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
SCRIPTS_DIR = WORKSPACE / "N5/scripts"
RECORDS_DIR = WORKSPACE / "N5/records/reflections"
REGISTRY_DIR = RECORDS_DIR / "registry"
REGISTRY_FILE = REGISTRY_DIR / "reflections.jsonl"
INCOMING_DIR = RECORDS_DIR / "incoming"
OUTPUTS_DIR = RECORDS_DIR / "outputs"
ERROR_LOG = WORKSPACE / "N5/logs/reflection_errors.jsonl"

def log_error(context: str, error: str, details: Dict = None):
    """Log error to error log file."""
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    error_record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "context": context,
        "error": error,
        "details": details or {}
    }
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(json.dumps(error_record) + "\n")
    except Exception as e:
        logger.error(f"Failed to log error: {e}")

def run_worker(script: str, args: list, step_name: str) -> bool:
    """Execute worker script with error handling."""
    script_path = SCRIPTS_DIR / script
    if not script_path.exists():
        error_msg = f"Script not found: {script_path}"
        logger.error(f"✗ {step_name} failed: {error_msg}")
        log_error(step_name, error_msg, {"script": str(script_path)})
        return False
    
    cmd = ["python3", str(script_path)] + args
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.stdout:
            logger.info(result.stdout)
        
        if result.returncode != 0:
            error_msg = result.stderr or f"Exit code {result.returncode}"
            logger.error(f"✗ {step_name} failed: {error_msg}")
            log_error(step_name, error_msg, {
                "exit_code": result.returncode,
                "stdout": result.stdout[-500:] if result.stdout else "",
                "stderr": result.stderr[-500:] if result.stderr else ""
            })
            return False
        
        logger.info(f"✓ {step_name} completed")
        return True
        
    except subprocess.TimeoutExpired:
        error_msg = f"Timeout (>300s)"
        logger.error(f"✗ {step_name} failed: {error_msg}")
        log_error(step_name, error_msg)
        return False
    except Exception as e:
        error_msg = str(e)
        logger.error(f"✗ {step_name} failed: {error_msg}")
        log_error(step_name, error_msg)
        return False

def main():
    """Execute full reflection pipeline."""
    try:
        logger.info("=" * 70)
        logger.info("REFLECTION PIPELINE (Zo-integrated)")
        logger.info("=" * 70)
        
        # Ensure directories exist
        for dir_path in [INCOMING_DIR, OUTPUTS_DIR, REGISTRY_DIR, ERROR_LOG.parent]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        steps_passed = 0
        total_steps = 2  # Classify, Generate (Ingest is manual)
        
        # Step 1: Classification (process all pending transcripts)
        logger.info("\n=== Phase 1: Classification ===")
        if run_worker(
            "reflection_classifier.py",
            ["--input", str(INCOMING_DIR)],
            "Classification"
        ):
            steps_passed += 1
        else:
            logger.warning("⚠ Classification had issues - continuing")
        
        # Step 2: Block Generation
        logger.info("\n=== Phase 2: Block Generation ===")
        if run_worker(
            "reflection_block_generator.py",
            ["--process-all", "--output", str(OUTPUTS_DIR)],
            "Block Generation"
        ):
            steps_passed += 1
        else:
            logger.warning("⚠ Block Generation had issues")
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info(f"Pipeline Complete: {steps_passed}/{total_steps} phases succeeded")
        logger.info(f"Output directory: {OUTPUTS_DIR}")
        if ERROR_LOG.exists():
            error_count = sum(1 for line in open(ERROR_LOG) if line.strip())
            logger.info(f"Errors logged: {error_count}")
        logger.info("=" * 70)
        
        return 0 if steps_passed >= 1 else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        log_error("main", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())
