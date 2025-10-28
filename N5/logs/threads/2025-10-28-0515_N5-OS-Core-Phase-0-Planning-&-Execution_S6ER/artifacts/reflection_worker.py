#!/usr/bin/env python3
"""
Reflection Processing Worker - integrates with Zo's Google Drive API
Downloads files from Drive and processes through the reflection pipeline.
"""

import json
import logging
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import tempfile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
REFLECTION_DIR = WORKSPACE / "N5" / "records" / "reflections"
SCRIPTS_DIR = WORKSPACE / "N5" / "scripts"
INCOMING_DIR = REFLECTION_DIR / "incoming"
OUTPUTS_DIR = REFLECTION_DIR / "outputs"
REGISTRY_DIR = REFLECTION_DIR / "registry"
STATE_FILE = REFLECTION_DIR / ".state.json"


def load_state():
    """Load processing state."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"processed": [], "failed": []}


def save_state(state):
    """Save processing state."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


def download_file(file_id, filename, mime_type):
    """Download a file using the provided Drive file list."""
    logger.info(f"Downloading: {filename} (ID: {file_id})")
    
    # Use a temporary location for downloads
    temp_dir = Path(tempfile.gettempdir())
    dest_path = temp_dir / filename
    
    # Create destination file with proper extension for audio
    if mime_type == "audio/mpeg":
        dest_path = temp_dir / filename.replace(".m4a", "").replace(".mp3", "") + ".m4a"
    
    # For this iteration, we'll download the file programmatically
    # using the file list from the API
    # This is a placeholder - actual download will be handled via use_app_google_drive
    
    return str(dest_path)


def process_file(file_path, filename):
    """Process a single file through the pipeline."""
    logger.info(f"Processing: {filename}")
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    
    try:
        # Determine file type
        if filename.endswith(('.m4a', '.mp3', '.wav')):
            return process_audio_file(file_path, filename)
        else:
            return process_text_file(file_path, filename)
    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")
        return None


def process_audio_file(file_path, filename):
    """Process audio file: transcribe, classify, generate blocks."""
    logger.info(f"Processing audio: {filename}")
    
    # Copy to incoming
    incoming_file = INCOMING_DIR / filename
    import shutil
    shutil.copy(file_path, incoming_file)
    logger.info(f"Copied to incoming: {incoming_file}")
    
    # Run transcription
    stem = incoming_file.stem
    transcript_path = incoming_file.parent / f"{stem}.txt"
    
    # Use Zo's transcribe capability
    logger.info(f"Transcribing: {incoming_file}")
    try:
        result = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "transcribe_audio.py"), str(incoming_file)],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            logger.error(f"Transcription failed: {result.stderr}")
            return None
        
        # Read transcript
        if transcript_path.exists():
            with open(transcript_path) as f:
                text = f.read()
            logger.info(f"Transcription complete: {len(text)} chars")
            return text
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None


def process_text_file(file_path, filename):
    """Process text file: read, classify, generate blocks."""
    logger.info(f"Processing text: {filename}")
    
    try:
        with open(file_path) as f:
            text = f.read()
        
        incoming_file = INCOMING_DIR / filename
        with open(incoming_file, 'w') as f:
            f.write(text)
        
        logger.info(f"Copied to incoming: {incoming_file}")
        return text
    except Exception as e:
        logger.error(f"Error reading text file: {e}")
        return None


def classify_and_generate(filename, text):
    """Classify reflection and generate blocks."""
    if not text or len(text) < 10:
        logger.warning(f"Skipping {filename}: text too short")
        return None
    
    logger.info(f"Classifying and generating blocks for: {filename}")
    
    # Create a temp file with the content for classification
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text)
        temp_path = f.name
    
    try:
        # Run classifier
        classify_result = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "reflection_classifier.py"), 
             "--input", temp_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if classify_result.returncode != 0:
            logger.warning(f"Classification failed for {filename}, using defaults")
            labels = ["general"]
        else:
            # Parse classification output
            try:
                output_data = json.loads(classify_result.stdout)
                labels = output_data.get("labels", ["general"])
            except:
                labels = ["general"]
        
        logger.info(f"Labels: {labels}")
        
        # Run block generator
        gen_result = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "reflection_block_generator.py"),
             "--input", temp_path,
             "--filename", filename,
             "--labels", json.dumps(labels)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if gen_result.returncode != 0:
            logger.error(f"Block generation failed for {filename}")
            logger.error(gen_result.stderr)
            return None
        
        logger.info(f"Successfully processed: {filename}")
        return {"filename": filename, "labels": labels, "status": "success"}
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def update_registry(filename, status, labels=None):
    """Update registry with processing result."""
    registry_file = REGISTRY_DIR / "registry.jsonl"
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "filename": filename,
        "status": status,
        "labels": labels or []
    }
    
    with open(registry_file, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    logger.info(f"Registry updated: {filename} -> {status}")


def main():
    """Main orchestration function."""
    logger.info("=" * 60)
    logger.info("REFLECTION PROCESSING WORKER (Drive Integration)")
    logger.info("=" * 60)
    
    state = load_state()
    processed_count = 0
    failed_count = 0
    
    # File list from Drive (would be passed from orchestrator)
    # For now, list files in incoming directory
    incoming_files = list(INCOMING_DIR.glob("*"))
    
    if not incoming_files:
        logger.info("No files in incoming directory")
        return 0
    
    for file_path in incoming_files:
        if file_path.name.startswith('.'):
            continue
        
        filename = file_path.name
        
        if filename in state["processed"]:
            logger.info(f"Skipping already processed: {filename}")
            continue
        
        try:
            # Process file
            text = process_file(file_path, filename)
            
            if not text:
                state["failed"].append(filename)
                update_registry(filename, "failed")
                failed_count += 1
                continue
            
            # Classify and generate
            result = classify_and_generate(filename, text)
            
            if result:
                state["processed"].append(filename)
                update_registry(filename, "success", result.get("labels"))
                processed_count += 1
            else:
                state["failed"].append(filename)
                update_registry(filename, "failed")
                failed_count += 1
                
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            state["failed"].append(filename)
            update_registry(filename, "error")
            failed_count += 1
    
    save_state(state)
    
    logger.info("=" * 60)
    logger.info(f"Processing complete: {processed_count} successful, {failed_count} failed")
    logger.info("=" * 60)
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
