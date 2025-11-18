#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def log(msg, level="✓"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {level} {msg}")

def find_next_ready_meeting():
    """Find next [P] meeting ready for archival."""
    inbox_path = Path("/home/workspace/Personal/Meetings/Inbox")
    # Use os.listdir and filter since glob has issues with brackets
    all_items = sorted(inbox_path.iterdir())
    ready_meetings = [p for p in all_items if p.is_dir() and p.name.endswith("_[P]")]
    if not ready_meetings:
        log("No [P] meetings ready for archival", "✓")
        return None
    return ready_meetings[0]

def validate_manifest(meeting_path):
    """Check manifest.json exists and all blocks are in acceptable completion states."""
    manifest_path = meeting_path / "manifest.json"
    
    if not manifest_path.exists():
        log(f"ERROR: manifest.json missing in {meeting_path.name}", "✗")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        log(f"ERROR: manifest.json unparseable in {meeting_path.name}: {e}", "✗")
        return False
    
    # Acceptable completion states for processed meetings
    acceptable_states = {
        "completed", "generated", "complete", 
        "not_applicable", "not_started", "drafts_ready"
    }
    
    blocks = manifest.get("blocks", [])
    for block in blocks:
        status = block.get("status", "")
        # Handle both string and boolean status values
        if isinstance(status, str):
            status_lower = status.lower()
            if status_lower not in acceptable_states:
                log(f"ERROR: Meeting {meeting_path.name} has problematic block (status: {status})", "✗")
                return False
    
    return True

def clean_nested_duplicates(meeting_path):
    """Remove nested duplicate folders matching 2025-* pattern."""
    nested = list(meeting_path.glob("2025-*"))
    for nested_path in nested:
        if nested_path.is_dir():
            subprocess.run(["rm", "-rf", str(nested_path)], check=True)
            log(f"Cleaned nested duplicate: {nested_path.name}", "✓")

def register_in_database(meeting_path):
    """Register meeting in database using add_to_database.py script."""
    script_path = Path("/home/workspace/N5/scripts/meeting_pipeline/add_to_database.py")
    
    # Look for transcript in priority order
    transcript_path = None
    candidates = [
        meeting_path / "transcript.md",
        meeting_path / "transcript.jsonl",
    ]
    for candidate in candidates:
        if candidate.exists():
            transcript_path = candidate
            break
    
    # Fall back to first block file if no transcript found
    if transcript_path is None:
        blocks = sorted([f for f in meeting_path.glob("B*.md") if f.is_file()])
        if blocks:
            transcript_path = blocks[0]
        else:
            log(f"ERROR: No transcript or block files found in {meeting_path.name}", "✗")
            return False
    
    # Extract meeting_id from folder name (remove _[P] suffix)
    meeting_id = meeting_path.name[:-4] if meeting_path.name.endswith("_[P]") else meeting_path.name
    
    # Try to detect meeting type from manifest
    manifest_path = meeting_path / "manifest.json"
    meeting_type = "EXTERNAL"
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                classification = manifest.get("classification", "external").upper()
                meeting_type = "INTERNAL" if classification == "INTERNAL" else "EXTERNAL"
        except:
            pass
    
    result = subprocess.run(
        ["python3", str(script_path), meeting_id, 
         "--transcript", str(transcript_path),
         "--type", meeting_type,
         "--status", "complete"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        log(f"ERROR: Database registration failed for {meeting_path.name} (exit code: {result.returncode})", "✗")
        if result.stderr:
            print(f"  stderr: {result.stderr}")
        return False
    
    log(f"Registered in database: {meeting_path.name}", "✓")
    return True

def calculate_archive_path(meeting_folder_name):
    """Extract date from folder name and calculate archive quarter."""
    try:
        date_str = meeting_folder_name.split("_")[0]
        year, month, day = date_str.split("-")
        month_int = int(month)
        
        if 1 <= month_int <= 3:
            quarter = "Q1"
        elif 4 <= month_int <= 6:
            quarter = "Q2"
        elif 7 <= month_int <= 9:
            quarter = "Q3"
        else:
            quarter = "Q4"
        
        archive_dir = Path(f"/home/workspace/Personal/Meetings/Archive/{year}-{quarter}")
        return archive_dir
    except (ValueError, IndexError):
        log(f"ERROR: Could not parse date from folder name: {meeting_folder_name}", "✗")
        return None

def clean_folder_name(folder_name):
    """Remove _[P] suffix from folder name."""
    if folder_name.endswith("_[P]"):
        return folder_name[:-4]
    return folder_name

def archive_meeting(meeting_path):
    """Move meeting to archive with cleaned name, handling collisions."""
    meeting_name = meeting_path.name
    cleaned_name = clean_folder_name(meeting_name)
    
    archive_dir = calculate_archive_path(meeting_name)
    if archive_dir is None:
        return False
    
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / cleaned_name
    
    # If destination already exists, merge contents
    if archive_path.exists():
        log(f"Destination exists, merging contents: {cleaned_name}", "→")
        try:
            # Copy all files from meeting_path to archive_path, overwriting
            result = subprocess.run(
                ["cp", "-r", "--force", str(meeting_path) + "/*", str(archive_path) + "/"],
                shell=True,
                capture_output=True,
                text=True
            )
            # Clean up the source folder
            subprocess.run(["rm", "-rf", str(meeting_path)], check=True)
            log(f"Merged: {meeting_name} → Archive/{archive_dir.name}/{cleaned_name}", "✅")
            return True
        except subprocess.CalledProcessError as e:
            log(f"ERROR: Merge operation failed for {meeting_name}: {e}", "✗")
            return False
    else:
        # Normal move operation
        try:
            subprocess.run(["mv", str(meeting_path), str(archive_path)], check=True)
            log(f"Archived: {meeting_name} → Archive/{archive_dir.name}/{cleaned_name}", "✅")
            return True
        except subprocess.CalledProcessError as e:
            log(f"ERROR: Move operation failed for {meeting_name}: {e}", "✗")
            return False

def main():
    meeting_path = find_next_ready_meeting()
    if meeting_path is None:
        return 0
    
    log(f"Processing: {meeting_path.name}", "→")
    
    if not validate_manifest(meeting_path):
        return 0
    
    try:
        clean_nested_duplicates(meeting_path)
    except Exception as e:
        log(f"ERROR: Failed to clean nested duplicates: {e}", "✗")
        return 1
    
    if not register_in_database(meeting_path):
        return 0
    
    if not archive_meeting(meeting_path):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())







