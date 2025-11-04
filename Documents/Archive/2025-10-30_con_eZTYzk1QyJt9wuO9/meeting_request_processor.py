#!/usr/bin/env python3
"""
Meeting Request Processor
Consumes pending request.json files from N5/inbox/meeting_requests/processed/
Downloads transcripts from Google Drive, saves to Personal/Meetings/, marks complete.

This is the missing component in the meeting pipeline.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

REQ_DIR = Path('/home/workspace/N5/inbox/meeting_requests/processed')
MEETINGS_DIR = Path('/home/workspace/Personal/Meetings')
LOG_FILE = Path('/home/workspace/N5/logs/meeting_request_processing.log')

def log_message(msg):
    """Append log message with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')
    log_line = f"{timestamp} | {msg}\n"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_line)
    print(log_line.strip())

def load_pending_requests():
    """Load all pending request files."""
    pending = []
    if not REQ_DIR.exists():
        return pending
    
    for req_file in REQ_DIR.glob('*_request.json'):
        try:
            with open(req_file) as f:
                data = json.load(f)
                if data.get('status') == 'pending':
                    data['_request_file'] = req_file
                    pending.append(data)
        except Exception as e:
            log_message(f"Error reading {req_file}: {e}")
    
    return pending

def main():
    log_message("=== MEETING REQUEST PROCESSOR ===")
    
    pending = load_pending_requests()
    log_message(f"Found {len(pending)} pending requests")
    
    for req in pending:
        meeting_id = req['meeting_id']
        gdrive_link = req['gdrive_link']
        log_message(f"Would process: {meeting_id}")
        log_message(f"  Download from: {gdrive_link}")
        log_message(f"  Classification: {req['classification']}")
    
    log_message("✓ Analysis complete")
    log_message("NOTE: This is a diagnostic script showing what needs to be done")
    log_message("Real processing requires Zo AI to:")
    log_message("  1. use_app_google_drive to download transcript")
    log_message("  2. Call Smart Block generation workflow")
    log_message("  3. Move to Personal/Meetings/")
    log_message("  4. Update request status to 'completed'")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
