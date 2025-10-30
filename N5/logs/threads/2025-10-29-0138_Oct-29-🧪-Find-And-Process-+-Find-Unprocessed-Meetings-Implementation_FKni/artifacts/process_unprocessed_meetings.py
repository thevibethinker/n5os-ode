#!/usr/bin/env python3
"""
Process unprocessed meetings with Smart Blocks.
Extracts action items and emails them for approval.
Limit: Max 2 meetings per run.
"""
import os
import subprocess
from pathlib import Path
from datetime import datetime

MEETINGS_DIR = Path("/home/workspace/Inbox/20251028-132902_Meetings")
ACTIONS_DIR = Path("/home/workspace/N5/inbox/meeting_actions")
SCRIPT_PATH = Path("/home/workspace/N5/scripts/extract_meeting_actions.py")
LOG_FILE = Path("/home/workspace/N5/logs/action_extractions.log")

def log_message(msg):
    """Log to file and stdout."""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {msg}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def get_extracted_meetings():
    """Get set of already extracted meetings."""
    extracted = set()
    for f in os.listdir(ACTIONS_DIR):
        if f.endswith(".json") and not f.endswith("_email_request.json"):
            if "Meetings_" in f:
                meeting_name = f.split("Meetings_", 1)[1].replace(".json", "")
                meeting_name = meeting_name.rsplit("_", 1)[0] if meeting_name[-1].isdigit() else meeting_name
                extracted.add(meeting_name)
    return extracted

def find_unprocessed():
    """Find meetings with Smart Blocks but not extracted."""
    extracted = get_extracted_meetings()
    unprocessed = []
    
    for dir_name in sorted(os.listdir(MEETINGS_DIR)):
        meeting_dir = MEETINGS_DIR / dir_name
        
        if not meeting_dir.is_dir() or dir_name.startswith("."):
            continue
        
        has_blocks = (meeting_dir / "B01_DETAILED_RECAP.md").exists() or \
                     (meeting_dir / "B25_DELIVERABLE_CONTENT_MAP.md").exists()
        
        if has_blocks and dir_name not in extracted:
            unprocessed.append(meeting_dir)
    
    return unprocessed

def process_meeting(meeting_dir):
    """Extract actions from a meeting."""
    meeting_name = meeting_dir.name
    log_message(f"Processing: {meeting_name}")
    
    try:
        cmd = [
            "python3",
            str(SCRIPT_PATH),
            "--meeting-dir",
            str(meeting_dir)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            log_message(f"✓ Successfully processed: {meeting_name}")
            if result.stdout:
                log_message(f"  Output: {result.stdout[:200]}")
            return True
        else:
            log_message(f"✗ Failed to process {meeting_name}")
            if result.stderr:
                log_message(f"  Error: {result.stderr[:300]}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message(f"✗ Timeout processing {meeting_name}")
        return False
    except Exception as e:
        log_message(f"✗ Exception processing {meeting_name}: {str(e)}")
        return False

def main():
    log_message("=== Starting scheduled action extraction run ===")
    
    unprocessed = find_unprocessed()
    log_message(f"Found {len(unprocessed)} unprocessed meetings")
    
    if not unprocessed:
        log_message("No unprocessed meetings found.")
        return
    
    # Process max 2 meetings
    to_process = unprocessed[:2]
    successful = 0
    
    for i, meeting_dir in enumerate(to_process, 1):
        log_message(f"\n[{i}/{len(to_process)}] Processing meeting...")
        if process_meeting(meeting_dir):
            successful += 1
    
    log_message(f"\n=== Run complete: {successful}/{len(to_process)} meetings processed ===")
    log_message(f"Remaining unprocessed: {len(unprocessed) - successful}")

if __name__ == "__main__":
    main()
