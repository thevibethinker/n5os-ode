#!/usr/bin/env python3
"""
Detect placeholder meetings daily and alert if found.

Purpose: Scan all meetings for Smart Blocks <100 bytes (placeholders),
         log to squawk_log, and alert if >3 new ones found.

Usage: python3 detect_placeholder_meetings.py
"""

import json
from pathlib import Path
from datetime import datetime, timezone

# Paths
MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
SQUAWK_LOG = Path("/home/workspace/N5/logs/squawk_log.jsonl")
REQUESTS_DIR = Path("/home/workspace/N5/inbox/meeting_requests/processed")

PLACEHOLDER_THRESHOLD = 100  # Files smaller than this are placeholders


def load_known_placeholders():
    """Load already-logged placeholder meetings from squawk log."""
    known = set()
    if SQUAWK_LOG.exists():
        for line in SQUAWK_LOG.read_text().splitlines():
            if line.strip():
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "placeholder_meeting":
                        known.add(entry.get("meeting_id"))
                except:
                    continue
    return known


def scan_for_placeholders():
    """Scan all meetings for placeholder Smart Blocks."""
    placeholders = []
    
    for meeting_dir in sorted(MEETINGS_DIR.iterdir()):
        if not meeting_dir.is_dir():
            continue
        
        meeting_id = meeting_dir.name
        
        # Check Smart Block files
        b_files = list(meeting_dir.glob("B*.md"))
        if not b_files:
            continue
        
        # Find smallest file
        smallest_size = min(f.stat().st_size for f in b_files)
        
        if smallest_size < PLACEHOLDER_THRESHOLD:
            # Extract gdrive_id from metadata if exists
            metadata_file = meeting_dir / "_metadata.json"
            gdrive_id = None
            if metadata_file.exists():
                try:
                    meta = json.loads(metadata_file.read_text())
                    gdrive_id = meta.get("gdrive_id")
                except:
                    pass
            
            placeholders.append({
                "meeting_id": meeting_id,
                "smallest_file_size": smallest_size,
                "file_count": len(b_files),
                "gdrive_id": gdrive_id
            })
    
    return placeholders


def log_to_squawk(meeting_id, details):
    """Log placeholder to squawk log."""
    SQUAWK_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": "placeholder_meeting",
        "severity": "high",
        "component": "meeting_consumer",
        "meeting_id": meeting_id,
        "desc": f"Meeting has placeholder Smart Blocks (smallest: {details['smallest_file_size']}B)",
        "workaround": "Meeting flagged for reprocessing",
        "root_cause": "suspected"
    }
    
    with SQUAWK_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def ensure_reprocess_request(placeholder):
    """Ensure request file exists for reprocessing."""
    meeting_id = placeholder["meeting_id"]
    request_file = REQUESTS_DIR / f"{meeting_id}_request.json"
    
    if request_file.exists():
        return True
    
    # Try to create from metadata
    gdrive_id = placeholder.get("gdrive_id")
    if not gdrive_id:
        return False
    
    meeting_dir = MEETINGS_DIR / meeting_id
    metadata_file = meeting_dir / "_metadata.json"
    
    if not metadata_file.exists():
        return False
    
    try:
        metadata = json.loads(metadata_file.read_text())
        request_data = {
            "meeting_id": meeting_id,
            "gdrive_id": gdrive_id,
            "gdrive_link": metadata.get("gdrive_link", f"https://drive.google.com/file/d/{gdrive_id}/view"),
            "original_filename": metadata.get("original_filename", "")
        }
        
        REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
        request_file.write_text(json.dumps(request_data, indent=2) + "\n")
        return True
    except:
        return False


def main():
    print("=" * 60)
    print("Placeholder Meeting Detection")
    print("=" * 60)
    
    # Load known placeholders
    known_placeholders = load_known_placeholders()
    print(f"\n📋 Known placeholders: {len(known_placeholders)}")
    
    # Scan for current placeholders
    print(f"\n🔍 Scanning meetings...")
    current_placeholders = scan_for_placeholders()
    print(f"   Found {len(current_placeholders)} meetings with placeholder content")
    
    # Identify new ones
    new_placeholders = [
        p for p in current_placeholders
        if p["meeting_id"] not in known_placeholders
    ]
    
    if not new_placeholders:
        print(f"\n✅ No new placeholders detected")
        return 0
    
    print(f"\n🚨 Found {len(new_placeholders)} NEW placeholders:")
    
    for placeholder in new_placeholders:
        meeting_id = placeholder["meeting_id"]
        size = placeholder["smallest_file_size"]
        print(f"   - {meeting_id} (smallest: {size}B)")
        
        # Log to squawk
        log_to_squawk(meeting_id, placeholder)
        
        # Ensure reprocess request exists
        if ensure_reprocess_request(placeholder):
            print(f"     ✓ Request file ready for reprocessing")
        else:
            print(f"     ⚠️  Could not create request file (missing gdrive_id)")
    
    # Alert if threshold exceeded
    if len(new_placeholders) > 3:
        print(f"\n⚠️  ALERT: {len(new_placeholders)} new placeholders exceeds threshold (3)")
        print(f"   This may indicate a systemic issue with the consumer task")
        print(f"   Review squawk log: {SQUAWK_LOG}")
    
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"   Total placeholders: {len(current_placeholders)}")
    print(f"   New this run: {len(new_placeholders)}")
    print(f"   Logged to squawk: {len(new_placeholders)}")
    print(f"={'=' * 60}")
    
    return 0


if __name__ == "__main__":
    exit(main())
