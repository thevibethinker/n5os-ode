#!/usr/bin/env python3
"""
Luma Email Helper
Updates event status and sends SMS when an approval email is detected.

Usage:
    python3 N5/scripts/luma_email_helper.py --approve-by-title "Tech Mixer NYC"
"""

import argparse
import logging
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

N5_ROOT = Path("/home/workspace/N5")
DB_PATH = N5_ROOT / "data" / "luma_events.db"

def confirm_event(title_query: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Fuzzy match title
    cursor.execute("SELECT id, title, registration_status FROM events WHERE title LIKE ? AND registration_status != 'confirmed'", (f"%{title_query}%",))
    rows = cursor.fetchall()
    
    if not rows:
        logger.warning(f"No pending event found matching '{title_query}'")
        conn.close()
        return
    
    if len(rows) > 1:
        logger.warning(f"Multiple events match '{title_query}'. Updating the most recent.")
        # Logic to pick best match could be added
        event = rows[0] # Pick first for now
    else:
        event = rows[0]
        
    event_id = event['id']
    event_title = event['title']
    
    logger.info(f"Confirming event: {event_title} ({event_id})")
    
    # Update DB
    cursor.execute("UPDATE events SET registration_status = 'confirmed', registered_at = ? WHERE id = ?", (datetime.now().isoformat(), event_id))
    conn.commit()
    conn.close()
    
    # Send SMS
    try:
        sys.path.append(str(N5_ROOT / "scripts"))
        from send_sms_notification import send_sms_via_zo
        message = f"🎉 You're in! Confirmed for {event_title}."
        send_sms_via_zo(message)
        logger.info("Sent confirmation SMS.")
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--approve-by-title", required=True, help="Partial title of the event")
    args = parser.parse_args()
    
    confirm_event(args.approve_by_title)

