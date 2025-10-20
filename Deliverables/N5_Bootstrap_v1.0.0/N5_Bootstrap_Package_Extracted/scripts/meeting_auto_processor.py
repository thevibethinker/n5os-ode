#!/usr/bin/env python3
"""
Meeting Auto-Processor for N5
Monitors for new meeting transcripts and creates processing requests for Zo.
Includes stakeholder classification (internal vs external).
"""
import os
import json
import re
from pathlib import Path
from datetime import datetime
import time
import sys

# Import stakeholder classifier
sys.path.insert(0, str(Path(__file__).parent))
from utils.stakeholder_classifier import classify_meeting, get_participant_details, extract_emails_from_text

WATCH_DIR = Path("/home/workspace/Document Inbox")
PROCESSED_LOG = Path("/home/workspace/N5/logs/processed_meetings.jsonl")
CHECK_INTERVAL = 60  # seconds

def extract_meeting_info(filepath: Path) -> dict:
    """Extract meeting metadata from transcript filename and content."""
    filename = filepath.stem
    
    # Pattern: "Name x Name-transcript-2025-09-23T21-04-28.138Z"
    match = re.search(r'(.+?)-transcript-(\d{4}-\d{2}-\d{2})', filename)
    
    # Read transcript content to extract emails
    try:
        transcript_text = filepath.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f"⚠️  Warning: Could not read transcript content: {e}")
        transcript_text = ""
    
    if match:
        participants = match.group(1)
        date_str = match.group(2)
        
        # Clean up participant names
        participants_clean = participants.replace(' x ', '-').replace(' ', '-').lower()
        participants_clean = re.sub(r'[^a-z0-9-]', '', participants_clean)
        
        # Classify meeting based on participants and transcript
        classification_details = get_participant_details(participants, transcript_text)
        meeting_type = classification_details['meeting_type']
        
        # Create meeting ID with classification suffix
        if meeting_type == 'internal':
            meeting_id = f"{date_str}_internal"
        else:
            # For external meetings, use first external participant name
            if classification_details['external_emails']:
                first_external = classification_details['external_emails'][0]
                external_name = first_external.split('@')[0].replace('.', '-')
                meeting_id = f"{date_str}_{external_name}"
            else:
                meeting_id = f"{date_str}_{participants_clean}"
        
        return {
            "meeting_id": meeting_id,
            "participants": participants,
            "date": date_str,
            "filepath": str(filepath),
            "detected_at": datetime.now().isoformat(),
            "stakeholder_classification": meeting_type,
            "participant_details": classification_details
        }
    
    # Fallback for non-standard filenames
    # Try to classify anyway using transcript content
    classification_details = get_participant_details("", transcript_text)
    meeting_type = classification_details['meeting_type']
    
    return {
        "meeting_id": f"meeting-{filepath.stem[:30]}",
        "participants": "unknown",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "filepath": str(filepath),
        "detected_at": datetime.now().isoformat(),
        "stakeholder_classification": meeting_type,
        "participant_details": classification_details
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
    
    classification_icon = "🏢" if meeting_info.get('stakeholder_classification') == 'internal' else "🌐"
    print(f"✅ Created processing request: {request_file.name} {classification_icon} {meeting_info.get('stakeholder_classification', 'unknown').upper()}")
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
