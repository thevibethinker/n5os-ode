#!/usr/bin/env python3
"""
Duplicate Meeting Detection v2
Convention: Second meeting merges into first (chronologically)
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from difflib import SequenceMatcher

WORKSPACE_ROOT = Path("/home/workspace")
PIPELINE_DB = WORKSPACE_ROOT / "N5/data/meeting_pipeline.db"

def extract_meeting_date(meeting_id):
    """Extract date from meeting_id (format: YYYY-MM-DD_...)"""
    try:
        date_str = meeting_id.split('_')[0]
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return None

def check_for_duplicate(meeting_id, transcript_text, time_window_hours=4):
    """
    Check if this meeting is a duplicate
    
    Convention: Earlier meeting wins (is "first")
    
    Returns: (is_duplicate, first_meeting_id, confidence, action)
        action = "skip" (this is second) or "flag" (this is first, other should merge)
    """
    conn = sqlite3.connect(PIPELINE_DB)
    cursor = conn.cursor()
    
    meeting_date = extract_meeting_date(meeting_id)
    if not meeting_date:
        conn.close()
        return (False, None, 0.0, None)
    
    # Search in time window
    window_start = meeting_date - timedelta(hours=time_window_hours)
    window_end = meeting_date + timedelta(hours=time_window_hours)
    
    cursor.execute("""
        SELECT meeting_id, transcript_path, detected_at FROM meetings
        WHERE detected_at BETWEEN ? AND ?
        AND meeting_id != ?
    """, (window_start.isoformat(), window_end.isoformat(), meeting_id))
    
    recent_meetings = cursor.fetchall()
    conn.close()
    
    transcript_start = transcript_text[:500]
    transcript_end = transcript_text[-500:]
    transcript_len = len(transcript_text)
    
    for existing_id, existing_path, existing_detected in recent_meetings:
        try:
            existing_transcript = Path(existing_path).read_text()
            existing_len = len(existing_transcript)
            
            # Length similarity check (within 20%)
            len_ratio = min(transcript_len, existing_len) / max(transcript_len, existing_len)
            if len_ratio < 0.80:
                continue
            
            # Content similarity
            existing_start = existing_transcript[:500]
            existing_end = existing_transcript[-500:]
            
            start_sim = SequenceMatcher(None, transcript_start, existing_start).ratio()
            end_sim = SequenceMatcher(None, transcript_end, existing_end).ratio()
            
            # Duplicate if both highly similar
            if start_sim > 0.85 and end_sim > 0.85:
                confidence = (start_sim + end_sim) / 2
                
                # Determine which is "first" by detected_at timestamp
                existing_detected_dt = datetime.fromisoformat(existing_detected)
                this_detected_dt = datetime.now(timezone.utc)
                
                if existing_detected_dt < this_detected_dt:
                    # Existing is first, this one should skip
                    return (True, existing_id, confidence, "skip")
                else:
                    # This one is first, flag the other for merge
                    return (True, meeting_id, confidence, "flag")
                
        except Exception:
            continue
    
    return (False, None, 0.0, None)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python duplicate_detector_v2.py <meeting_id> <transcript_file>")
        sys.exit(1)
    
    meeting_id = sys.argv[1]
    transcript_file = Path(sys.argv[2])
    
    if not transcript_file.exists():
        print(f"Error: {transcript_file} not found")
        sys.exit(1)
    
    transcript = transcript_file.read_text()
    is_dup, first_id, conf, action = check_for_duplicate(meeting_id, transcript)
    
    if is_dup:
        if action == "skip":
            print(f"⚠️  DUPLICATE: Skip processing {meeting_id}")
            print(f"   First meeting: {first_id} (confidence: {conf:.0%})")
            print(f"   Action: Auto-merge into first after processing")
        else:
            print(f"⚠️  DUPLICATE: {first_id} will be merged into this")
            print(f"   (This meeting came first, other is duplicate)")
    else:
        print(f"✓ No duplicates found for {meeting_id}")
