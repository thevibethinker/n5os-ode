#!/usr/bin/env python3
"""
Reprocess Marked Meetings
Finds meetings marked with 👉 emoji and queues them for processing.
Marks with 👍 when complete.
"""
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
MEETINGS_DIR = WORKSPACE / "Personal/Meetings"
INBOX = MEETINGS_DIR / "Inbox"
AI_REQUESTS = WORKSPACE / "N5/inbox/ai_requests"
PIPELINE_DB = WORKSPACE / "N5/data/meeting_pipeline.db"

def scan_for_marked_meetings():
    """Find all meetings with 👉 emoji in folder name."""
    marked = []
    for dir_path in MEETINGS_DIR.iterdir():
        if dir_path.is_dir() and "👉" in dir_path.name:
            marked.append(dir_path)
    return marked

def extract_meeting_id(folder_name):
    """Extract meeting_id by removing emoji prefixes."""
    return folder_name.replace("👉", "").replace(" ", "").strip()

def convert_transcript_to_md(meeting_dir):
    """Convert .docx or .txt transcript to .md format."""
    docx_file = meeting_dir / "transcript.docx"
    txt_file = meeting_dir / "transcript.txt"
    md_file = INBOX / f"{meeting_dir.name.replace('👉', '').strip()}.transcript.md"
    
    if docx_file.exists():
        # Convert docx to md using pandoc
        cmd = f"pandoc '{docx_file}' -f docx -t markdown -o '{md_file}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"  ✓ Converted: {docx_file.name} → {md_file.name}")
            return md_file
        else:
            logger.error(f"  ✗ Conversion failed: {result.stderr}")
            return None
    elif txt_file.exists():
        # Copy txt to md
        md_file.write_text(txt_file.read_text())
        logger.info(f"  ✓ Copied: {txt_file.name} → {md_file.name}")
        return md_file
    else:
        logger.warning(f"  ⚠ No transcript file found in {meeting_dir.name}")
        return None

def create_ai_request(meeting_id, transcript_path):
    """Create AI processing request."""
    AI_REQUESTS.mkdir(parents=True, exist_ok=True)
    request_id = f"meeting_{meeting_id}_{int(datetime.now().timestamp())}"
    
    request = {
        "request_id": request_id,
        "request_type": "meeting_process",
        "prompt_name": "Meeting Process",
        "inputs": {
            "transcript_path": str(transcript_path),
            "meeting_id": meeting_id,
            "meeting_type": "external" if "external" in meeting_id else "internal"
        },
        "output_requirements": {
            "blocks": ["notes", "follow_up", "key_quotes", "deliverables"],
            "output_dir": str(MEETINGS_DIR / meeting_id)
        },
        "status": "pending",
        "priority": 5,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    request_file = AI_REQUESTS / f"{request_id}.json"
    request_file.write_text(json.dumps(request, indent=2))
    logger.info(f"  ✓ AI request created: {request_id}")
    return request_id

def register_in_db(meeting_id, transcript_path):
    """Register meeting in pipeline database."""
    conn = sqlite3.connect(PIPELINE_DB)
    conn.execute("""
        INSERT OR REPLACE INTO meetings (meeting_id, transcript_path, meeting_type, status, detected_at)
        VALUES (?, ?, ?, ?, ?)
    """, (meeting_id, str(transcript_path), "UNKNOWN", "queued_for_ai", datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

def mark_complete(meeting_dir):
    """Rename folder to add 👍 emoji."""
    new_name = meeting_dir.name.replace("👉", "👍")
    new_path = meeting_dir.parent / new_name
    meeting_dir.rename(new_path)
    logger.info(f"  ✓ Marked complete: {new_name}")

def main():
    logger.info("Reprocess Marked Meetings")
    logger.info("="*60)
    
    marked = scan_for_marked_meetings()
    logger.info(f"Found {len(marked)} meeting(s) marked with 👉")
    
    if not marked:
        logger.info("No meetings to reprocess")
        return 0
    
    for meeting_dir in marked:
        meeting_id = extract_meeting_id(meeting_dir.name)
        logger.info(f"\nProcessing: {meeting_id}")
        
        # Step 1: Convert transcript
        md_file = convert_transcript_to_md(meeting_dir)
        if not md_file:
            logger.error(f"  ✗ Skipping {meeting_id} - no transcript")
            continue
        
        # Step 2: Register in DB
        register_in_db(meeting_id, md_file)
        logger.info(f"  ✓ Registered in database")
        
        # Step 3: Create AI request
        create_ai_request(meeting_id, md_file)
        
        logger.info(f"  ⏳ Queued for AI processing")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✓ Queued {len(marked)} meeting(s) for reprocessing")
    logger.info("These will be processed by the scheduled AI task")
    logger.info("Folders will be renamed with 👍 when complete")
    
    return 0

if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
