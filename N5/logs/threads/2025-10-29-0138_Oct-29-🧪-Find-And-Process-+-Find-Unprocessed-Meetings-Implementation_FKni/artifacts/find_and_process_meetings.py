#!/usr/bin/env python3
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

MEETINGS_DIR = "/home/workspace/Inbox/20251028-132902_Meetings"
ACTIONS_DIR = "/home/workspace/N5/inbox/meeting_actions"
SCRIPT_PATH = "/home/workspace/N5/scripts/extract_meeting_actions.py"
LOG_FILE = "/home/workspace/N5/logs/action_extractions.log"

def log_message(msg):
    """Log to file and stdout."""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {msg}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def has_smart_blocks(meeting_dir):
    """Check if meeting has Smart Blocks (B01 or B25 files)."""
    return (
        (meeting_dir / "B01_Detailed-Recap.md").exists() or
        (meeting_dir / "B25_Deliverable-Content-Map.md").exists()
    )

def get_existing_extractions():
    """Get list of already extracted meetings."""
    extracted = set()
    if not os.path.exists(ACTIONS_DIR):
        return extracted
    
    for filename in os.listdir(ACTIONS_DIR):
        if filename.endswith(".json") and not filename.endswith("_email_request.json"):
            extracted.add(filename)
    return extracted

def get_meeting_identifier(meeting_dir_name):
    """Extract unique identifier from meeting directory name."""
    # Format: YYYY-MM-DD_name
    return meeting_dir_name

def find_new_meetings():
    """Find meetings with Smart Blocks but no action extraction."""
    log_message(f"Scanning {MEETINGS_DIR} for new meetings...")
    
    new_meetings = []
    existing = get_existing_extractions()
    
    if not os.path.exists(MEETINGS_DIR):
        log_message(f"ERROR: Meetings directory not found: {MEETINGS_DIR}")
        return new_meetings
    
    for dir_name in sorted(os.listdir(MEETINGS_DIR)):
        meeting_dir = Path(MEETINGS_DIR) / dir_name
        
        if not meeting_dir.is_dir() or dir_name.startswith("."):
            continue
        
        # Check if has Smart Blocks
        if not has_smart_blocks(meeting_dir):
            continue
        
        # Check if already extracted
        # Look for matching extraction files
        found_extraction = False
        for existing_file in existing:
            if dir_name in existing_file or meeting_dir_name_matches(existing_file, dir_name):
                found_extraction = True
                break
        
        if not found_extraction:
            new_meetings.append(meeting_dir)
            log_message(f"Found new meeting: {dir_name}")
    
    return new_meetings

def meeting_dir_name_matches(extraction_filename, meeting_dir_name):
    """Check if extraction filename matches meeting directory."""
    # extraction format: 20251028-132902_Meetings_[meeting_name].json
    if "Meetings_" in extraction_filename:
        extracted_name = extraction_filename.split("Meetings_", 1)[1].replace(".json", "")
        # Remove trailing codes like _175632 or _email_request
        extracted_name = extracted_name.rsplit("_", 1)[0] if "_" in extracted_name else extracted_name
        return extracted_name == meeting_dir_name
    return False

def process_meeting(meeting_dir, max_retries=2):
    """Run extraction script for a meeting."""
    meeting_name = meeting_dir.name
    log_message(f"Processing: {meeting_name}")
    
    try:
        cmd = [
            "python3",
            SCRIPT_PATH,
            "--meeting-dir",
            str(meeting_dir)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log_message(f"✓ Successfully processed: {meeting_name}")
            return True
        else:
            log_message(f"✗ Failed to process {meeting_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message(f"✗ Timeout processing {meeting_name}")
        return False
    except Exception as e:
        log_message(f"✗ Error processing {meeting_name}: {str(e)}")
        return False

def main():
    log_message("=== Starting meeting action extraction ===")
    
    # Find new meetings
    new_meetings = find_new_meetings()
    log_message(f"Found {len(new_meetings)} new meetings to process")
    
    if not new_meetings:
        log_message("No new meetings to process. Exiting.")
        return
    
    # Process max 2 meetings
    to_process = new_meetings[:2]
    successful = 0
    
    for i, meeting_dir in enumerate(to_process, 1):
        log_message(f"\n[{i}/{len(to_process)}] Processing meeting...")
        if process_meeting(meeting_dir):
            successful += 1
    
    log_message(f"\n=== Summary: {successful}/{len(to_process)} meetings processed successfully ===")

if __name__ == "__main__":
    main()
