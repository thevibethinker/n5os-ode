#!/usr/bin/env python3
"""
Luma Feedback Checker
Identifies past events that were approved/registered and likely attended.

Usage:
    python3 N5/scripts/luma_feedback_check.py
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "data" / "luma_events.db"
FEEDBACK_PATH = N5_ROOT / "data" / "luma_feedback.jsonl"

def get_feedback_candidates():
    if not DB_PATH.exists():
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Logic:
    # 1. Event start time has passed (e.g. yesterday)
    # 2. Status is 'approved' OR 'registered' OR has gcal_event_id
    # 3. Not already in feedback log (we need to check this)
    
    now = datetime.now().isoformat()
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    
    query = """
        SELECT * FROM events
        WHERE event_datetime < ?
        AND (status = 'approved' OR registration_status = 'registered' OR gcal_event_id IS NOT NULL)
        ORDER BY event_datetime DESC
        LIMIT 5
    """
    
    cursor.execute(query, (now,))
    candidates = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Filter out already reviewed
    reviewed_ids = set()
    if FEEDBACK_PATH.exists():
        with open(FEEDBACK_PATH, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    reviewed_ids.add(entry.get("event_id"))
                except:
                    pass
    
    final_list = [c for c in candidates if c["id"] not in reviewed_ids]
    return final_list

if __name__ == "__main__":
    events = get_feedback_candidates()
    if events:
        print(json.dumps(events, indent=2, default=str))
    else:
        print("[]")

