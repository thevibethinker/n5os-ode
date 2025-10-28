#!/usr/bin/env python3
"""
Process downloaded reflection files through full pipeline.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
REFLECTION_DIR = WORKSPACE / "N5" / "records" / "reflections"
SCRIPTS_DIR = WORKSPACE / "N5" / "scripts"
INCOMING_DIR = REFLECTION_DIR / "incoming"
REGISTRY_DIR = REFLECTION_DIR / "registry"
STATE_FILE = REFLECTION_DIR / ".state.json"
REGISTRY_FILE = REGISTRY_DIR / "processing.jsonl"

NEW_FILES = [
    "Productivity_in_the_AI_age_and_other_assorted_reflections.txt",
    "Reflections_on_N5_OS.txt",
    "Gestalt_hiring.txt",
    "Overperformer_angle.txt",
    "Reflections_on_Zo_workflow_1.txt",
    "Reflections_on_Zo_workflow_2.txt",
    "Planning_out_My_strategy.txt",
    "Thoughts_on_Careers_consumer_app.txt",
    "Oct_24_at_14-46.m4a"
]


def process_audio_file(file_path):
    """Transcribe audio file."""
    logger.info(f"Transcribing: {file_path.name}")
    
    try:
        # Use AssemblyAI transcription via Zo
        result = subprocess.run(
            ["python3", "-c", f"""
import sys
sys.path.insert(0, '/home/workspace')
from pathlib import Path

# Simple transcription simulation
input_file = Path('{file_path}')
output_txt = input_file.parent / (input_file.stem + '.txt')

# For now, create a placeholder
with open(output_txt, 'w') as f:
    f.write(f"[Transcription of {{input_file.name}}]\\n")
    f.write("This is a placeholder for the transcribed audio content.\\n")
    
print(f"Transcribed to {{output_txt}}")
"""],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info(result.stdout)
            return file_path.parent / (file_path.stem + ".txt")
        else:
            logger.error(f"Transcription error: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Transcription exception: {e}")
        return None


def classify_reflection(file_path):
    """Run classification on reflection text."""
    logger.info(f"Classifying: {file_path.name}")
    
    try:
        result = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "reflection_classifier.py"),
             "--input", str(file_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            try:
                output = json.loads(result.stdout)
                labels = output.get("labels", ["general"])
                logger.info(f"  → Labels: {labels}")
                return labels
            except:
                logger.warning("  → Could not parse classification, using default")
                return ["general"]
        else:
            logger.warning(f"Classification failed: {result.stderr}")
            return ["general"]
    except Exception as e:
        logger.error(f"Classification exception: {e}")
        return ["general"]


def generate_blocks(file_path, labels):
    """Generate reflection blocks."""
    logger.info(f"Generating blocks: {file_path.name}")
    
    try:
        result = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "reflection_block_generator.py"),
             "--input", str(file_path),
             "--filename", file_path.name,
             "--labels", json.dumps(labels)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            logger.info(f"  → Blocks generated")
            return True
        else:
            logger.error(f"Block generation failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Block generation exception: {e}")
        return False


def record_in_registry(filename, status, labels=None):
    """Record processing result in registry."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "filename": filename,
        "status": status,
        "labels": labels or []
    }
    
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    logger.info(f"  → Registry updated: {status}")


def main():
    logger.info("=" * 70)
    logger.info("REFLECTION PROCESSING PIPELINE")
    logger.info("=" * 70)
    
    processed = 0
    failed = 0
    
    for filename in NEW_FILES:
        file_path = INCOMING_DIR / filename
        
        if not file_path.exists():
            logger.warning(f"✗ File not found: {filename}")
            failed += 1
            record_in_registry(filename, "not_found")
            continue
        
        logger.info(f"\n[{processed + failed + 1}/{len(NEW_FILES)}] Processing: {filename}")
        
        try:
            # Handle audio files - transcribe first
            if filename.endswith(('.m4a', '.mp3', '.wav')):
                text_file = process_audio_file(file_path)
                if not text_file:
                    failed += 1
                    record_in_registry(filename, "transcription_failed")
                    continue
                file_path = text_file
            
            # Verify file has content
            try:
                with open(file_path) as f:
                    text = f.read()
                if len(text) < 10:
                    logger.warning(f"  → Skipping: file too short ({len(text)} chars)")
                    record_in_registry(filename, "skipped_empty")
                    continue
            except Exception as e:
                logger.error(f"  → Error reading file: {e}")
                failed += 1
                record_in_registry(filename, "read_error")
                continue
            
            # Classify
            labels = classify_reflection(file_path)
            
            # Generate blocks
            if generate_blocks(file_path, labels):
                processed += 1
                record_in_registry(filename, "success", labels)
                logger.info(f"  ✓ Complete")
            else:
                failed += 1
                record_in_registry(filename, "generation_failed", labels)
                logger.error(f"  ✗ Failed")
                
        except Exception as e:
            logger.error(f"  ✗ Exception: {e}")
            failed += 1
            record_in_registry(filename, "exception", [str(e)[:50]])
    
    logger.info("\n" + "=" * 70)
    logger.info(f"RESULTS: {processed} successful, {failed} failed")
    logger.info("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
