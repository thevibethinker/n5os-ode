#!/usr/bin/env python3
"""
Reflection Ingestion v2 - Drive Integration & Transcription

Pulls files from Google Drive folder, transcribes audio, stages text files.
Drive-only (no email), with state tracking and dry-run support.

Usage:
    python3 reflection_ingest_v2.py [--dry-run] [--folder-id FOLDER_ID]
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

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
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".opus", ".ogg", ".flac"}
TEXT_EXTENSIONS = {".txt", ".md"}
DOC_MIME_TYPES = {
    "application/vnd.google-apps.document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword"
}


def load_state() -> Dict:
    """Load state file or return default state."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
                logger.info(f"✓ Loaded state: {len(state.get('processed_file_ids', []))} files processed")
                return state
        except Exception as e:
            logger.error(f"Failed to load state file: {e}")
            return create_default_state()
    else:
        logger.info("No state file found, creating new state")
        return create_default_state()


def create_default_state() -> Dict:
    """Create default state structure."""
    return {
        "last_run_iso": None,
        "processed_file_ids": [],
        "last_sync_token": None
    }


def save_state(state: Dict, dry_run: bool = False) -> bool:
    """Save state file with updated information."""
    if dry_run:
        logger.info(f"[DRY RUN] Would save state: {len(state['processed_file_ids'])} files")
        return True
    
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        logger.info(f"✓ Saved state: {len(state['processed_file_ids'])} files processed")
        return True
    except Exception as e:
        logger.error(f"Failed to save state: {e}")
        return False


def list_drive_files(folder_id: str, dry_run: bool = False) -> List[Dict]:
    """
    List files from Google Drive folder.
    
    NOTE: This function requires Zo's use_app_google_drive tool.
    For automation, this script should be called by Zo with Drive API access.
    """
    logger.error("MANUAL ACTION REQUIRED: This script must be run by Zo")
    logger.error("  Use: use_app_google_drive tool to list files")
    logger.error(f"  Folder ID: {folder_id}")
    
    # Placeholder for manual execution
    # In actual execution, Zo will call use_app_google_drive and pass results
    return []


def download_drive_file(file_id: str, file_name: str, mime_type: str, 
                        output_path: Path, dry_run: bool = False) -> bool:
    """
    Download file from Google Drive.
    
    NOTE: This function requires Zo's use_app_google_drive tool.
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would download: {file_name} → {output_path}")
        return True
    
    logger.error("MANUAL ACTION REQUIRED: Use Zo's use_app_google_drive tool")
    logger.error(f"  File ID: {file_id}")
    logger.error(f"  Output: {output_path}")
    return False


def sanitize_filename(name: str, created_date: str = None) -> str:
    """
    Sanitize filename for filesystem storage.
    Format: YYYY-MM-DD_filename (if date available) or filename
    """
    # Remove/replace invalid characters
    sanitized = name.replace("/", "-").replace("\\", "-").replace(" ", "-")
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in "-_.")
    
    # Prepend date if available
    if created_date:
        try:
            date_obj = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
            date_prefix = date_obj.strftime("%Y-%m-%d")
            return f"{date_prefix}_{sanitized}"
        except:
            pass
    
    return sanitized


def create_metadata(file_info: Dict, output_path: Path, has_transcript: bool = False) -> Dict:
    """Create metadata JSON for downloaded file."""
    return {
        "drive_file_id": file_info.get("id"),
        "original_name": file_info.get("name"),
        "downloaded_at_iso": datetime.utcnow().isoformat() + "Z",
        "file_type": "audio" if has_transcript else "text",
        "mime_type": file_info.get("mimeType"),
        "size_bytes": file_info.get("size", 0),
        "has_transcript": has_transcript,
        "drive_modified_time": file_info.get("modifiedTime")
    }


def save_metadata(metadata: Dict, metadata_path: Path, dry_run: bool = False) -> bool:
    """Save metadata JSON file."""
    if dry_run:
        logger.info(f"[DRY RUN] Would save metadata: {metadata_path}")
        return True
    
    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✓ Saved metadata: {metadata_path.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to save metadata: {e}")
        return False


def transcribe_audio(audio_path: Path, dry_run: bool = False) -> bool:
    """
    Transcribe audio file using Zo's built-in transcribe_audio tool.
    
    NOTE: This function requires Zo's transcribe_audio tool.
    The transcript will be saved as: {audio_path}.transcript.jsonl
    """
    transcript_path = Path(str(audio_path) + ".transcript.jsonl")
    
    if transcript_path.exists():
        logger.info(f"✓ Transcript exists: {transcript_path.name}")
        return True
    
    if dry_run:
        logger.info(f"[DRY RUN] Would transcribe: {audio_path.name}")
        return True
    
    logger.error("MANUAL ACTION REQUIRED: Use Zo's transcribe_audio tool")
    logger.error(f"  Audio file: {audio_path}")
    logger.error(f"  Expected output: {transcript_path}")
    
    return False


def verify_download(file_path: Path, expected_size: int = None) -> bool:
    """Verify downloaded file exists and is valid."""
    if not file_path.exists():
        logger.error(f"File does not exist: {file_path}")
        return False
    
    actual_size = file_path.stat().st_size
    if actual_size == 0:
        logger.error(f"File is empty: {file_path}")
        return False
    
    if expected_size and abs(actual_size - expected_size) > 1024:  # Allow 1KB variance
        logger.warning(f"Size mismatch: expected {expected_size}, got {actual_size}")
    
    return True


def process_files(files: List[Dict], state: Dict, dry_run: bool = False) -> int:
    """
    Process new files from Drive: download, transcribe, save metadata.
    
    Returns number of successfully processed files.
    """
    processed_ids = set(state.get("processed_file_ids", []))
    new_files = [f for f in files if f["id"] not in processed_ids]
    
    logger.info(f"Found {len(files)} total files, {len(new_files)} new")
    
    if len(new_files) == 0:
        logger.info("No new files to process")
        return 0
    
    success_count = 0
    
    for file_info in new_files:
        file_id = file_info["id"]
        file_name = file_info["name"]
        mime_type = file_info.get("mimeType", "")
        
        logger.info(f"Processing: {file_name} ({mime_type})")
        
        # Determine file type and extension
        file_ext = Path(file_name).suffix.lower()
        is_audio = file_ext in AUDIO_EXTENSIONS
        is_gdoc = mime_type in DOC_MIME_TYPES
        
        # Sanitize filename
        sanitized_name = sanitize_filename(file_name, file_info.get("createdTime"))
        
        # Handle Google Docs → markdown conversion
        if is_gdoc and not sanitized_name.endswith(".md"):
            sanitized_name = sanitized_name.rsplit(".", 1)[0] + ".md"
        
        output_path = INCOMING_DIR / sanitized_name
        metadata_path = INCOMING_DIR / (sanitized_name.rsplit(".", 1)[0] + ".json")
        
        # Download file
        if not download_drive_file(file_id, file_name, mime_type, output_path, dry_run):
            logger.error(f"Failed to download: {file_name}")
            continue
        
        # Verify download (skip in dry-run)
        if not dry_run and not verify_download(output_path, int(file_info.get("size", 0))):
            logger.error(f"Verification failed: {file_name}")
            continue
        
        # Transcribe audio files
        if is_audio:
            if not transcribe_audio(output_path, dry_run):
                logger.error(f"Transcription failed: {file_name}")
                # Continue anyway - file is downloaded
        
        # Create and save metadata
        metadata = create_metadata(file_info, output_path, has_transcript=is_audio)
        if not save_metadata(metadata, metadata_path, dry_run):
            logger.warning(f"Metadata save failed: {file_name}")
        
        # Mark as processed
        if not dry_run:
            processed_ids.add(file_id)
        
        success_count += 1
        logger.info(f"✓ Processed ({success_count}/{len(new_files)}): {file_name}")
    
    # Update state
    state["processed_file_ids"] = list(processed_ids)
    state["last_run_iso"] = datetime.utcnow().isoformat() + "Z"
    
    return success_count


def main(dry_run: bool = False, folder_id: str = None) -> int:
    """Main execution flow."""
    try:
        logger.info("=" * 60)
        logger.info("Reflection Ingestion v2 - Drive Integration")
        logger.info(f"Dry-run mode: {dry_run}")
        logger.info("=" * 60)
        
        # Ensure directories exist
        INCOMING_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load state
        state = load_state()
        
        # Use provided folder ID or default
        target_folder = folder_id or DRIVE_FOLDER_ID
        logger.info(f"Target folder: {target_folder}")
        
        # List files from Drive (requires Zo's tool)
        logger.info("Listing files from Drive...")
        files = list_drive_files(target_folder, dry_run)
        
        if not files:
            logger.error("No files retrieved - requires Zo execution")
            logger.info("This script must be run by Zo with Drive API access")
            return 1
        
        # Process files
        processed_count = process_files(files, state, dry_run)
        
        # Save state
        if not save_state(state, dry_run):
            logger.error("Failed to save state")
            return 1
        
        logger.info("=" * 60)
        logger.info(f"✓ Complete: {processed_count} files processed")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest reflection files from Google Drive"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files without downloading"
    )
    parser.add_argument(
        "--folder-id",
        type=str,
        help=f"Drive folder ID (default: {DRIVE_FOLDER_ID})"
    )
    
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run, folder_id=args.folder_id))
