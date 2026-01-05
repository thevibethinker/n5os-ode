#!/usr/bin/env python3
"""
Reflection Processing Orchestrator
Coordinates end-to-end reflection processing pipeline (Workers 1-5)

Flow:
1. Ingest (Worker 1) - Pull from Drive + transcribe
2. Classify (Worker 2) - Multi-label classification
3. Generate (Worker 4) - Create blocks from transcript
4. Suggest (Worker 5) - Pattern detection (optional/periodic)
5. Synthesize (Worker 5) - B90/B91 generation (optional/weekly)
6. Registry Update - Track all processed reflections

Usage:
    python3 reflection_orchestrator.py \
        --folder-id 16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV \
        --run-suggester \
        --run-synthesizer \
        [--dry-run]
"""

import subprocess
import logging
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Configure logging
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


def run_worker(script: str, args: list, dry_run: bool = False) -> Dict:
    """Execute worker script with error handling
    
    Args:
        script: Script filename (e.g., "reflection_ingest_v2.py")
        args: List of command-line arguments
        dry_run: If True, add --dry-run flag
        
    Returns:
        Dict with status, stdout, stderr
    """
    script_path = SCRIPTS_DIR / script
    cmd = ["python3", str(script_path)] + args
    
    if dry_run and "--dry-run" not in args:
        cmd.append("--dry-run")
    
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logger.info(f"✓ {script} completed successfully")
            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        else:
            logger.error(f"✗ {script} failed with exit code {result.returncode}")
            logger.error(f"stderr: {result.stderr}")
            return {
                "status": "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
            
    except Exception as e:
        logger.error(f"Exception running {script}: {e}", exc_info=True)
        return {
            "status": "exception",
            "error": str(e)
        }


def ingest_reflections(folder_id: str, dry_run: bool = False) -> Dict:
    """Worker 1: Ingest from Drive + transcribe"""
    logger.info("=== Phase 1: Ingestion ===")
    
    return run_worker(
        "reflection_ingest_v2.py",
        ["--folder-id", folder_id],
        dry_run=dry_run
    )


def classify_reflections(dry_run: bool = False) -> Dict:
    """Worker 2: Classify new transcripts"""
    logger.info("=== Phase 2: Classification ===")
    
    return run_worker(
        "reflection_classifier.py",
        ["--input-dir", str(INCOMING_DIR)],
        dry_run=dry_run
    )


def generate_blocks(dry_run: bool = False) -> Dict:
    """Worker 4: Generate block content"""
    logger.info("=== Phase 3: Block Generation ===")
    
    return run_worker(
        "reflection_block_generator.py",
        ["--input-dir", str(INCOMING_DIR)],
        dry_run=dry_run
    )


def suggest_blocks(dry_run: bool = False) -> Dict:
    """Worker 5: Pattern detection"""
    logger.info("=== Phase 4: Block Suggestion (Pattern Detection) ===")
    
    return run_worker(
        "reflection_block_suggester.py",
        [],
        dry_run=dry_run
    )


def synthesize_compound(dry_run: bool = False) -> Dict:
    """Worker 5: B90/B91 synthesis"""
    logger.info("=== Phase 5: Compound Synthesis (B90/B91) ===")
    
    return run_worker(
        "reflection_synthesizer_v2.py",
        [],
        dry_run=dry_run
    )


def get_transcripts_to_process() -> List[Path]:
    """Get list of transcript files that need processing"""
    if not INCOMING_DIR.exists():
        return []
    
    return sorted(INCOMING_DIR.glob("*.transcript.jsonl"))


def load_registry() -> Dict[str, Dict]:
    """Load existing registry as dict keyed by reflection ID"""
    registry = {}
    
    if not REGISTRY_FILE.exists():
        return registry
    
    try:
        with open(REGISTRY_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if 'id' in entry:
                        registry[entry['id']] = entry
    except Exception as e:
        logger.error(f"Error loading registry: {e}")
    
    return registry


def update_registry(processed_files: List[Path], phase: str, dry_run: bool = False) -> bool:
    """Update reflection registry with processed files
    
    Args:
        processed_files: List of transcript file paths
        phase: Processing phase (e.g., "ingested", "classified", "generated")
        dry_run: If True, don't write to registry
        
    Returns:
        True if successful
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would update registry for {len(processed_files)} files (phase={phase})")
        return True
    
    if not processed_files:
        logger.info("No files to add to registry")
        return True
    
    try:
        # Ensure registry directory exists
        REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load existing registry
        registry = load_registry()
        
        # Process each file
        for transcript_path in processed_files:
            # Extract reflection ID from filename
            # Format: YYYY-MM-DD_topic.m4a.transcript.jsonl
            stem = transcript_path.stem.replace(".transcript", "")
            
            # Check if already in registry
            if stem in registry:
                # Update existing entry
                registry[stem]["last_updated"] = datetime.now(timezone.utc).isoformat()
                registry[stem]["phases"] = registry[stem].get("phases", [])
                if phase not in registry[stem]["phases"]:
                    registry[stem]["phases"].append(phase)
                logger.info(f"Updated registry entry: {stem} (phase={phase})")
            else:
                # Create new entry
                entry = {
                    "id": stem,
                    "source_file": transcript_path.name,
                    "transcript_path": str(transcript_path.relative_to(WORKSPACE)),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "phases": [phase],
                    "status": "processing"
                }
                registry[stem] = entry
                logger.info(f"Created registry entry: {stem}")
        
        # Write registry back to file
        with open(REGISTRY_FILE, 'w') as f:
            for entry in registry.values():
                f.write(json.dumps(entry) + "\n")
        
        logger.info(f"✓ Registry updated: {REGISTRY_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating registry: {e}", exc_info=True)
        return False


def verify_registry() -> bool:
    """Verify registry file is valid JSONL"""
    if not REGISTRY_FILE.exists():
        logger.warning("Registry file doesn't exist yet")
        return True
    
    try:
        with open(REGISTRY_FILE, 'r') as f:
            for i, line in enumerate(f, 1):
                if line.strip():
                    json.loads(line)
        logger.info(f"✓ Registry verified: {REGISTRY_FILE}")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Registry validation failed at line {i}: {e}")
        return False


def count_blocks_generated(output_dir: Path) -> int:
    """Count number of block files generated"""
    if not output_dir.exists():
        return 0
    return len(list(output_dir.glob("B*.md")))


def main(
    folder_id: str,
    run_suggester: bool = False,
    run_synthesizer: bool = False,
    dry_run: bool = False
) -> int:
    """Main orchestration flow
    
    Args:
        folder_id: Google Drive folder ID to poll
        run_suggester: If True, run pattern detection
        run_synthesizer: If True, run compound synthesis
        dry_run: If True, don't make any changes
        
    Returns:
        Exit code (0=success, 1=failure)
    """
    try:
        logger.info("=" * 60)
        logger.info("REFLECTION PROCESSING ORCHESTRATOR")
        logger.info("=" * 60)
        
        if dry_run:
            logger.info("[DRY RUN MODE] No changes will be made")
        
        # Phase 1: Ingest from Drive
        ingest_result = ingest_reflections(folder_id, dry_run)
        if ingest_result["status"] != "success":
            logger.error("Ingestion failed, aborting pipeline")
            return 1
        
        # Get list of transcripts to process
        transcripts = get_transcripts_to_process()
        if not transcripts:
            logger.info("No transcripts to process")
            return 0
        
        logger.info(f"Found {len(transcripts)} transcript(s) to process")
        
        # Update registry: ingested phase
        update_registry(transcripts, "ingested", dry_run)
        
        # Phase 2: Classify
        classify_result = classify_reflections(dry_run)
        if classify_result["status"] != "success":
            logger.warning("Classification failed, continuing anyway")
        else:
            update_registry(transcripts, "classified", dry_run)
        
        # Phase 3: Generate blocks
        generate_result = generate_blocks(dry_run)
        if generate_result["status"] != "success":
            logger.warning("Block generation failed, continuing anyway")
        else:
            update_registry(transcripts, "generated", dry_run)
        
        # Phase 4: Suggest (optional/periodic)
        if run_suggester:
            suggest_result = suggest_blocks(dry_run)
            if suggest_result["status"] != "success":
                logger.warning("Block suggestion failed, continuing anyway")
        else:
            logger.info("Skipping block suggestion (use --run-suggester to enable)")
        
        # Phase 5: Synthesize (optional/weekly)
        if run_synthesizer:
            synthesize_result = synthesize_compound(dry_run)
            if synthesize_result["status"] != "success":
                logger.warning("Compound synthesis failed, continuing anyway")
        else:
            logger.info("Skipping compound synthesis (use --run-synthesizer to enable)")
        
        # Final verification
        if not dry_run:
            if not verify_registry():
                logger.error("Registry verification failed")
                return 1
        
        # Summary
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info(f"Processed: {len(transcripts)} reflection(s)")
        logger.info(f"Registry: {REGISTRY_FILE}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Orchestrator error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reflection processing orchestrator (Workers 1-5)"
    )
    parser.add_argument(
        "--folder-id",
        required=True,
        help="Google Drive folder ID to poll"
    )
    parser.add_argument(
        "--run-suggester",
        action="store_true",
        help="Run pattern detection (Worker 5: suggester)"
    )
    parser.add_argument(
        "--run-synthesizer",
        action="store_true",
        help="Run compound synthesis (Worker 5: synthesizer)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode (no changes)"
    )
    
    args = parser.parse_args()
    
    exit_code = main(
        folder_id=args.folder_id,
        run_suggester=args.run_suggester,
        run_synthesizer=args.run_synthesizer,
        dry_run=args.dry_run
    )
    
    exit(exit_code)
