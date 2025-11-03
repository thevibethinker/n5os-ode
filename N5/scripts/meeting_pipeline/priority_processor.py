#!/usr/bin/env python3
"""
Priority Meeting Processor
Processes manually marked meetings (👉) and meetings with health issues.
Renames to 👍 when complete.
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import subprocess

WORKSPACE = Path("/home/workspace")
MEETINGS_DIR = WORKSPACE / "Personal/Meetings"
INBOX = MEETINGS_DIR / "Inbox"
PIPELINE_DB = WORKSPACE / "N5/data/meeting_pipeline.db"
AI_REQUEST_QUEUE = WORKSPACE / "N5/inbox/ai_requests"
HEALTH_REPORT = WORKSPACE / "N5/data/meeting_health_report.json"

def find_marked_meetings():
    """Find meetings marked with 👉."""
    marked = []
    for meeting_dir in MEETINGS_DIR.glob("*👉*"):
        if meeting_dir.is_dir():
            # Extract clean meeting_id
            meeting_id = meeting_dir.name.replace("👉 ", "").replace("👉", "")
            marked.append({
                "meeting_id": meeting_id,
                "source": "manual_marker",
                "path": meeting_dir,
                "reason": "User marked with 👉"
            })
    return marked

def find_critical_meetings():
    """Find meetings with critical health issues."""
    if not HEALTH_REPORT.exists():
        return []
    
    health = json.loads(HEALTH_REPORT.read_text())
    critical = []
    for issue in health.get("critical", []):
        meeting_id = issue["meeting_id"]
        meeting_dir = MEETINGS_DIR / meeting_id
        if meeting_dir.exists():
            critical.append({
                "meeting_id": meeting_id,
                "source": "health_scanner",
                "path": meeting_dir,
                "reason": f"Critical issues: {len(issue['issues'])}"
            })
    return critical

def queue_meeting_for_reprocessing(meeting):
    """Queue a meeting for AI processing."""
    meeting_id = meeting["meeting_id"]
    meeting_dir = meeting["path"]
    
    # Check for transcript file
    transcript_files = list(meeting_dir.glob("transcript.*"))
    if not transcript_files:
        print(f"  ⚠ No transcript found for {meeting_id}")
        return False
    
    transcript = transcript_files[0]
    
    # Convert to .md if needed
    if transcript.suffix in [".docx", ".txt"]:
        md_path = INBOX / f"{meeting_id}.transcript.md"
        if transcript.suffix == ".docx":
            subprocess.run([
                "pandoc", str(transcript), "-o", str(md_path),
                "--wrap=none"
            ], check=True)
        else:
            md_path.write_text(transcript.read_text())
        transcript = md_path
    
    # Create AI request
    request_id = f"meeting_{meeting_id}_{int(datetime.now().timestamp())}"
    request = {
        "request_id": request_id,
        "request_type": "meeting_reprocess",
        "prompt_name": "Meeting Process",
        "inputs": {
            "transcript_path": str(transcript),
            "meeting_id": meeting_id,
            "meeting_type": "external" if "external" in meeting_id else "internal",
            "original_dir": str(meeting_dir),
            "reason": meeting["reason"]
        },
        "output_requirements": {
            "blocks": ["notes", "commitments", "key_quotes", "deliverables"],
            "output_dir": str(meeting_dir)
        },
        "status": "pending",
        "priority": 1,  # High priority
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    request_file = AI_REQUEST_QUEUE / f"{request_id}.json"
    request_file.write_text(json.dumps(request, indent=2))
    
    # Register in database
    conn = sqlite3.connect(PIPELINE_DB)
    conn.execute("""
        INSERT OR REPLACE INTO meetings (meeting_id, transcript_path, meeting_type, status, detected_at, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (meeting_id, str(transcript), request["inputs"]["meeting_type"], "queued_for_ai", 
          datetime.now(timezone.utc).isoformat(), f"Reprocessing: {meeting['reason']}"))
    conn.commit()
    conn.close()
    
    return True

def main():
    print("Priority Meeting Processor")
    print("=" * 60)
    
    # Find meetings needing attention
    marked = find_marked_meetings()
    critical = find_critical_meetings()
    
    all_priority = marked + critical
    
    # Deduplicate
    seen = set()
    priority_meetings = []
    for m in all_priority:
        if m["meeting_id"] not in seen:
            priority_meetings.append(m)
            seen.add(m["meeting_id"])
    
    print(f"Found {len(priority_meetings)} meeting(s) needing processing:")
    print(f"  - {len(marked)} manually marked with 👉")
    print(f"  - {len(critical)} with critical health issues")
    print()
    
    if not priority_meetings:
        print("✓ No priority meetings to process")
        return 0
    
    # Queue each meeting
    queued = 0
    for meeting in priority_meetings:
        print(f"Processing: {meeting['meeting_id']}")
        print(f"  Reason: {meeting['reason']}")
        try:
            if queue_meeting_for_reprocessing(meeting):
                queued += 1
                print(f"  ✓ Queued for AI processing")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()
    
    print("=" * 60)
    print(f"✓ Queued {queued}/{len(priority_meetings)} meeting(s)")
    print(f"These will be processed by the AI request processor")
    print(f"Folders will be renamed with 👍 when complete")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
