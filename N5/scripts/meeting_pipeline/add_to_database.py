#!/usr/bin/env python3
"""
Add meeting to pipeline database
Simple utility to register meetings in the tracking system
"""
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("/home/workspace/N5/data/meeting_pipeline.db")

def add_meeting(meeting_id: str, transcript_path: str, meeting_type: str = "EXTERNAL", 
                status: str = "complete", notes: str = None):
    """
    Add or update a meeting in the database.
    
    Args:
        meeting_id: Unique meeting identifier (folder name)
        transcript_path: Path to transcript or first block file
        meeting_type: Type of meeting (EXTERNAL, INTERNAL, etc.)
        status: Meeting status (detected, queued_for_ai, processing, complete, failed)
        notes: Optional notes about the meeting
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Check if meeting already exists
    cursor.execute("SELECT meeting_id, status FROM meetings WHERE meeting_id = ?", (meeting_id,))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing meeting
        cursor.execute("""
            UPDATE meetings 
            SET status = ?, 
                completed_at = ?,
                notes = COALESCE(?, notes)
            WHERE meeting_id = ?
        """, (status, now if status == "complete" else None, notes, meeting_id))
        print(f"✅ Updated: {meeting_id} → {status}")
    else:
        # Insert new meeting
        cursor.execute("""
            INSERT INTO meetings 
            (meeting_id, transcript_path, meeting_type, status, detected_at, completed_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (meeting_id, transcript_path, meeting_type, status, now, 
              now if status == "complete" else None, notes))
        print(f"✅ Added: {meeting_id} → {status}")
    
    conn.commit()
    conn.close()
    return True

def main():
    parser = argparse.ArgumentParser(description="Add meeting to pipeline database")
    parser.add_argument("meeting_id", help="Meeting folder name")
    parser.add_argument("--transcript", "-t", required=True, help="Path to transcript/first block")
    parser.add_argument("--type", default="EXTERNAL", help="Meeting type")
    parser.add_argument("--status", default="complete", help="Meeting status")
    parser.add_argument("--notes", help="Optional notes")
    
    args = parser.parse_args()
    
    add_meeting(
        meeting_id=args.meeting_id,
        transcript_path=args.transcript,
        meeting_type=args.type,
        status=args.status,
        notes=args.notes
    )

if __name__ == "__main__":
    main()

