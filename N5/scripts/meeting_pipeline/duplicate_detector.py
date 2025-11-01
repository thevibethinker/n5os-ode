#!/usr/bin/env python3
"""
Duplicate Meeting Detection
Fuzzy matching to prevent duplicate processing
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
    Check if this meeting might be a duplicate
    
    Returns: (is_duplicate, suspected_original_id, confidence)
    """
    conn = sqlite3.connect(PIPELINE_DB)
    cursor = conn.cursor()
    
    # Get recent meetings (within time window)
    meeting_date = extract_meeting_date(meeting_id)
    if not meeting_date:
        conn.close()
        return (False, None, 0.0)
    
    window_start = meeting_date - timedelta(hours=time_window_hours)
    window_end = meeting_date + timedelta(hours=time_window_hours)
    
    cursor.execute("""
        SELECT meeting_id, transcript_path FROM meetings
        WHERE detected_at BETWEEN ? AND ?
        AND meeting_id != ?
    """, (window_start.isoformat(), window_end.isoformat(), meeting_id))
    
    recent_meetings = cursor.fetchall()
    conn.close()
    
    # Check each recent meeting for similarity
    transcript_start = transcript_text[:500]
    transcript_end = transcript_text[-500:]
    transcript_len = len(transcript_text)
    
    for existing_id, existing_path in recent_meetings:
        try:
            existing_transcript = Path(existing_path).read_text()
            existing_len = len(existing_transcript)
            
            # Check 1: Length similarity (within 20%)
            len_ratio = min(transcript_len, existing_len) / max(transcript_len, existing_len)
            if len_ratio < 0.80:
                continue
            
            # Check 2: Start similarity
            existing_start = existing_transcript[:500]
            start_similarity = SequenceMatcher(None, transcript_start, existing_start).ratio()
            
            # Check 3: End similarity
            existing_end = existing_transcript[-500:]
            end_similarity = SequenceMatcher(None, transcript_end, existing_end).ratio()
            
            # Duplicate if both start and end are very similar
            if start_similarity > 0.85 and end_similarity > 0.85:
                confidence = (start_similarity + end_similarity) / 2
                return (True, existing_id, confidence)
                
        except Exception as e:
            continue
    
    return (False, None, 0.0)

if __name__ == "__main__":
    # Test
    test_id = "2025-11-01_test-meeting"
    test_transcript = "This is a test transcript for duplicate detection"
    
    is_dup, orig_id, conf = check_for_duplicate(test_id, test_transcript)
    if is_dup:
        print(f"⚠️  Duplicate detected: {orig_id} (confidence: {conf:.2%})")
    else:
        print("✓ No duplicates found")
