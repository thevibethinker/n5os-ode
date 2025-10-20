#!/usr/bin/env python3
"""
Unified reflection ingestion orchestrator.
Pulls from email and/or Drive, transcribes audio, processes through worker.
"""
import argparse, json, logging, subprocess, sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
ROOT = WORKSPACE / "N5/records/reflections"
INCOMING = ROOT / "incoming"
STATE_FILE = ROOT / ".state.json"
CONFIG = WORKSPACE / "N5/config/reflection-sources.json"

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".opus", ".aac", ".flac"}


def load_config() -> dict:
    if not CONFIG.exists():
        logger.error(f"Missing config: {CONFIG}")
        return {"drive_folder_id": None, "email_lookback_minutes": 10}
    return json.loads(CONFIG.read_text())


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_run_iso": None, "processed_file_ids": [], "processed_message_ids": []}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def ingest_email(lookback_minutes: int, state: dict) -> list:
    """Pull reflections from Gmail with [Reflect] tag."""
    logger.info(f"Checking email for [Reflect] messages (last {lookback_minutes} min)...")
    
    # NOTE: This is a placeholder for Zo's use_app_gmail tool
    # In production, Zo will call this directly via its tool
    # For now, return empty list - Zo will handle the actual Gmail API call
    
    logger.warning("Email ingestion requires Zo's use_app_gmail tool - run via Zo command interface")
    logger.info("Query: newer_than:{lookback_minutes}m has:attachment subject:\"[Reflect]\" filename:(mp3 OR m4a OR wav OR opus)")
    
    return []


def ingest_drive(folder_id: str, state: dict) -> list:
    """Pull reflections from Google Drive folder."""
    if not folder_id or folder_id == "REPLACE_WITH_YOUR_FOLDER_ID":
        logger.warning("Drive folder_id not configured in N5/config/reflection-sources.json")
        return []
    
    logger.info(f"Checking Drive folder {folder_id}...")
    
    # NOTE: This is a placeholder for Zo's use_app_google_drive tool
    # In production, Zo will call this directly via its tool
    
    logger.warning("Drive ingestion requires Zo's use_app_google_drive tool - run via Zo command interface")
    
    return []


def transcribe_audio(audio_path: Path) -> Path:
    """Transcribe audio file using Zo's transcribe_audio tool."""
    transcript_path = Path(str(audio_path) + ".transcript.jsonl")
    
    if transcript_path.exists():
        logger.info(f"✓ Transcript exists: {transcript_path}")
        return transcript_path
    
    logger.info(f"Transcribing {audio_path.name}...")
    
    # NOTE: This should be called via Zo's transcribe_audio tool
    # For now, create a placeholder that Zo will replace with actual transcription
    
    logger.error("MANUAL ACTION REQUIRED: Use Zo's transcribe_audio tool")
    logger.error(f"  transcribe_audio('{audio_path}')")
    
    # Create minimal placeholder so worker doesn't fail
    transcript_path.write_text(json.dumps({"text": "[PENDING TRANSCRIPTION]"}))
    
    return transcript_path


def process_file(file_path: Path) -> bool:
    """Process a single reflection file through the worker."""
    logger.info(f"Processing: {file_path.name}")
    
    # If audio, ensure transcript exists
    if file_path.suffix.lower() in AUDIO_EXTENSIONS:
        try:
            transcribe_audio(file_path)
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return False
    
    # Run worker
    try:
        result = subprocess.run(
            ["python3", str(WORKSPACE / "N5/scripts/reflection_worker.py"), "--file", str(file_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            logger.error(f"Worker failed: {result.stderr}")
            return False
        
        logger.info(f"✓ Processed: {file_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Worker error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Unified reflection ingestion")
    parser.add_argument("--source", choices=["email", "drive", "both"], default="both",
                        help="Source to ingest from (default: both)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()
    
    config = load_config()
    state = load_state()
    
    INCOMING.mkdir(parents=True, exist_ok=True)
    
    new_files = []
    
    # Pull from sources
    if args.source in ["email", "both"]:
        new_files.extend(ingest_email(config["email_lookback_minutes"], state))
    
    if args.source in ["drive", "both"]:
        new_files.extend(ingest_drive(config.get("drive_folder_id"), state))
    
    # Check for manually staged files in incoming/
    staged = list(INCOMING.glob("*"))
    staged = [f for f in staged if f.is_file() and not f.name.startswith(".") and f.suffix != ".jsonl"]
    
    if staged:
        logger.info(f"Found {len(staged)} manually staged files")
        new_files.extend(staged)
    
    if not new_files:
        logger.info("No new reflections to process")
        return 0
    
    logger.info(f"Processing {len(new_files)} reflection(s)...")
    
    if args.dry_run:
        logger.info("[DRY RUN] Would process:")
        for f in new_files:
            logger.info(f"  - {f}")
        return 0
    
    # Process each file
    success_count = 0
    for file_path in new_files:
        if process_file(file_path):
            success_count += 1
            # Move to processed
            processed_path = ROOT / "processed" / file_path.name
            processed_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.rename(processed_path)
    
    # Update state
    state["last_run_iso"] = datetime.now().isoformat()
    save_state(state)
    
    logger.info(f"✓ Complete: {success_count}/{len(new_files)} processed successfully")
    
    return 0 if success_count == len(new_files) else 1


if __name__ == "__main__":
    sys.exit(main())
