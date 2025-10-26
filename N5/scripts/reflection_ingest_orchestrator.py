#!/usr/bin/env python3
"""
Reflection Ingestion Orchestrator - Zo Integration Layer

This script bridges between reflection_ingest_v2.py and Zo's Drive API.
It handles the actual Drive API calls that the base script can't do directly.

Usage by Zo:
    python3 reflection_ingest_orchestrator.py [--dry-run]
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Constants
DRIVE_FOLDER_ID = "16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV"
INCOMING_DIR = Path("/home/workspace/N5/records/reflections/incoming")
STATE_FILE = Path("/home/workspace/N5/records/reflections/.state.json")
TEMP_DIR = Path("/home/.z/workspaces/con_FXkbqnkVx2vtjQwx/drive_cache")

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".opus", ".ogg", ".flac"}
TEXT_EXTENSIONS = {".txt", ".md"}


def load_state() -> Dict:
    """Load state file or return default state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "last_run_iso": None,
        "processed_file_ids": [],
        "last_sync_token": None
    }


def save_state(state: Dict) -> bool:
    """Save state file."""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save state: {e}")
        return False


def sanitize_filename(name: str, created_date: str = None) -> str:
    """Sanitize filename for filesystem storage."""
    sanitized = name.replace("/", "-").replace("\\", "-").replace(" ", "-")
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in "-_.")
    
    if created_date:
        try:
            date_obj = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
            date_prefix = date_obj.strftime("%Y-%m-%d")
            return f"{date_prefix}_{sanitized}"
        except:
            pass
    
    return sanitized


def should_convert_to_markdown(mime_type: str, file_name: str) -> bool:
    """Determine if file should be converted to markdown."""
    doc_types = {
        "application/vnd.google-apps.document",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    }
    return mime_type in doc_types


def process_file(file_info: Dict, state: Dict, dry_run: bool = False) -> bool:
    """
    Process a single file: download, transcribe if audio, save metadata.
    
    NOTE: This function is called BY ZO and has access to use_app_google_drive.
    This is a placeholder - Zo will inject the actual Drive API calls.
    """
    file_id = file_info["id"]
    file_name = file_info["name"]
    mime_type = file_info.get("mimeType", "")
    
    # Determine output filename
    file_ext = Path(file_name).suffix.lower()
    is_audio = file_ext in AUDIO_EXTENSIONS
    convert_to_md = should_convert_to_markdown(mime_type, file_name)
    
    sanitized_name = sanitize_filename(file_name, file_info.get("createdTime"))
    if convert_to_md and not sanitized_name.endswith(".md"):
        sanitized_name = sanitized_name.rsplit(".", 1)[0] + ".md"
    
    output_path = INCOMING_DIR / sanitized_name
    metadata_path = INCOMING_DIR / (sanitized_name.rsplit(".", 1)[0] + ".json")
    
    if dry_run:
        logger.info(f"[DRY RUN] Would process: {file_name} → {output_path.name}")
        return True
    
    # PLACEHOLDER: Zo will call use_app_google_drive here
    logger.info(f"Downloading: {file_name} ({mime_type})")
    logger.info(f"  File ID: {file_id}")
    logger.info(f"  Output: {output_path}")
    logger.info(f"  Convert to MD: {convert_to_md}")
    
    # Create metadata
    metadata = {
        "drive_file_id": file_id,
        "original_name": file_name,
        "downloaded_at_iso": datetime.utcnow().isoformat() + "Z",
        "file_type": "audio" if is_audio else "text",
        "mime_type": mime_type,
        "size_bytes": file_info.get("size", 0),
        "has_transcript": False,  # Will be updated after transcription
        "drive_modified_time": file_info.get("modifiedTime"),
        "drive_created_time": file_info.get("createdTime")
    }
    
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"✓ Metadata saved: {metadata_path.name}")
    
    # PLACEHOLDER: Transcription will be handled by Zo
    if is_audio:
        logger.info(f"  Audio file - requires transcription: {output_path}")
    
    return True


def main(dry_run: bool = False) -> int:
    """Main orchestration flow."""
    try:
        logger.info("=" * 60)
        logger.info("Reflection Ingestion Orchestrator")
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'PRODUCTION'}")
        logger.info("=" * 60)
        
        # Ensure directories exist
        INCOMING_DIR.mkdir(parents=True, exist_ok=True)
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load state
        state = load_state()
        processed_ids = set(state.get("processed_file_ids", []))
        
        logger.info(f"Loaded state: {len(processed_ids)} files already processed")
        logger.info(f"Target folder: {DRIVE_FOLDER_ID}")
        
        # PLACEHOLDER: Zo will list files here using use_app_google_drive
        logger.info("\n⚠️  REQUIRES ZO EXECUTION ⚠️")
        logger.info("Zo must call use_app_google_drive to:")
        logger.info("  1. List files in folder")
        logger.info("  2. Download each file")
        logger.info("  3. Transcribe audio files")
        logger.info("\nThis is a template for Zo to follow.")
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Orchestrate reflection ingestion with Zo's Drive API"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))
