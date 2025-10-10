#!/usr/bin/env python3
"""
Meeting Auto-Processor for N5
Monitors for new meeting transcripts and creates processing requests for Zo.
"""
import os
import json
import re
from pathlib import Path
from datetime import datetime
import time
import sys

WATCH_DIR = Path("/home/workspace/Document Inbox")
PROCESSED_LOG = Path("/home/workspace/N5/logs/processed_meetings.jsonl")
CHECK_INTERVAL = 60  # seconds

def extract_meeting_info(filepath: Path) -> dict:
    """Extract meeting metadata from transcript filename."""
    filename = filepath.stem
    
    # Pattern: "Name x Name-transcript-2025-09-23T21-04-28.138Z"
    match = re.search(r'(.+?)-transcript-(\d{4}-\d{2}-\d{2})', filename)
    
    if match:
        participants = match.group(1)
        date_str = match.group(2)
        
        # Clean up participant names
        participants_clean = participants.replace(' x ', '-').replace(' ', '-').lower()
        participants_clean = re.sub(r'[^a-z0-9-]', '', participants_clean)
        
        meeting_id = f"{participants_clean}-{date_str}"
        
        return {
            "meeting_id": meeting_id,
            "participants": participants,
            "date": date_str,
            "filepath": str(filepath),
            "detected_at": datetime.now().isoformat()
        }
    
    # Fallback for non-standard filenames
    return {
        "meeting_id": f"meeting-{filepath.stem[:30]}",
        "participants": "unknown",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "filepath": str(filepath),
        "detected_at": datetime.now().isoformat()
    }

def is_processed(filepath: Path) -> bool:
    """Check if this transcript has already been processed."""
    if not PROCESSED_LOG.exists():
        return False
    
    filepath_str = str(filepath)
    with open(PROCESSED_LOG, 'r') as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                if record.get("filepath") == filepath_str:
                    return True
    return False

def mark_processed(meeting_info: dict):
    """Mark a transcript as processed."""
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_LOG, 'a') as f:
        f.write(json.dumps(meeting_info) + '\n')

def create_processing_request(meeting_info: dict):
    """Create a processing request file for Zo to pick up."""
    request_dir = Path("/home/workspace/N5/inbox/meeting_requests")
    request_dir.mkdir(parents=True, exist_ok=True)
    
    request_file = request_dir / f"{meeting_info['meeting_id']}_request.json"
    
    request_data = {
        **meeting_info,
        "status": "pending",
        "type": "meeting_intelligence_extraction",
        "created_at": datetime.now().isoformat()
    }
    
    with open(request_file, 'w') as f:
        json.dump(request_data, f, indent=2)
    
    print(f"✅ Created processing request: {request_file.name}")
    return request_file

def scan_for_transcripts():
    """Scan Document Inbox for new meeting transcripts."""
    print(f"🔍 Scanning {WATCH_DIR} for new transcripts...")
    
    transcript_patterns = [
        "*-transcript-*.docx",
        "*-transcript-*.txt",
        "*transcript*.docx",
        "*transcript*.txt"
    ]
    
    found_new = False
    
    for pattern in transcript_patterns:
        for filepath in WATCH_DIR.glob(pattern):
            if not is_processed(filepath):
                print(f"📋 New transcript found: {filepath.name}")
                meeting_info = extract_meeting_info(filepath)
                create_processing_request(meeting_info)
                mark_processed(meeting_info)
                found_new = True
    
    if not found_new:
        print("   No new transcripts found")
    
    return found_new

def watch_mode():
    """Continuously monitor for new transcripts."""
    print("👀 Starting meeting transcript auto-processor...")
    print(f"📂 Watching: {WATCH_DIR}")
    print(f"⏰ Check interval: {CHECK_INTERVAL}s")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            scan_for_transcripts()
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 Stopping auto-processor")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once and exit (for cron/scheduled tasks)
        scan_for_transcripts()
    else:
        # Continuous watch mode
        watch_mode()

if __name__ == "__main__":
    main()
