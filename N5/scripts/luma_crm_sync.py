#!/usr/bin/env python3
"""
Luma CRM Sync
Syncs event organizers to the CRM enrichment queue.

Usage:
    python3 N5/scripts/luma_crm_sync.py
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
import uuid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "data" / "luma_events.db"
QUEUE_PATH = Path("/home/workspace/Lists/individuals_queue.jsonl")

def sync_organizers():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get unprocessed organizers
    cursor.execute("SELECT * FROM organizers WHERE enriched_at IS NULL")
    rows = cursor.fetchall()
    
    if not rows:
        logger.info("No new organizers to sync.")
        conn.close()
        return

    logger.info(f"Syncing {len(rows)} organizers to CRM queue...")
    
    new_entries = []
    processed_ids = []
    
    for row in rows:
        organizer_name = row['name']
        organizer_url = row['luma_profile_url']
        
        # Create queue entry
        entry = {
            "individual_id": f"luma_{uuid.uuid4().hex[:8]}",
            "name": organizer_name,
            "email": "", # Unknown initially
            "linkedin_url": "", # Will be found by enrichment
            "source": "discovered_via_luma_event",
            "source_url": organizer_url,
            "priority": "medium",
            "date_added": datetime.now().strftime("%Y-%m-%d"),
            "status": "queued",
            "notes": f"Organizer of Luma event (ID: {row['event_id']})"
        }
        new_entries.append(entry)
        processed_ids.append(row['id'])

    # Append to queue
    try:
        with open(QUEUE_PATH, "a") as f:
            for entry in new_entries:
                f.write(json.dumps(entry) + "\n")
        
        # Mark as processed in DB
        now = datetime.now().isoformat()
        cursor.executemany("UPDATE organizers SET enriched_at = ? WHERE id = ?", 
                          [(now, pid) for pid in processed_ids])
        conn.commit()
        logger.info(f"✓ Successfully queued {len(new_entries)} organizers.")
        
    except Exception as e:
        logger.error(f"Error writing to queue: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    sync_organizers()

