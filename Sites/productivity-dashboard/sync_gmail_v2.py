#!/usr/bin/env python3
"""
WORKING VERSION: Proper integration with Zo app tools.
This script is designed to be called WITH proper Gmail/Calendar data passed as arguments.
Never generates fake data.
"""
import sys
import json
import sqlite3
import logging
import argparse
from datetime import date
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = '/home/workspace/productivity_tracker.db'

def ensure_schema():
    """Ensure database has correct schema including meeting_hours column."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if meeting_hours exists
    c.execute("PRAGMA table_info(daily_stats)")
    columns = {col[1] for col in c.fetchall()}
    
    if 'meeting_hours' not in columns:
        logging.info("Adding missing meeting_hours column...")
        c.execute("ALTER TABLE daily_stats ADD COLUMN meeting_hours REAL DEFAULT 0")
        conn.commit()
        logging.info("✓ Schema updated")
    
    conn.close()

def calculate_rpi(emails_sent: int, meeting_hours: float, target_date: date = None) -> dict:
    """Calculate RPI using the correct formula."""
    if target_date is None:
        target_date = date.today()
    
    is_weekend = target_date.weekday() in (5, 6)
    
    if is_weekend:
        expected_emails = 5.0
    else:
        free_hours = max(0, 8.0 - meeting_hours)
        expected_emails = (free_hours * 2.5) + 5.0
    
    rpi = round((emails_sent / expected_emails) * 100, 1) if expected_emails > 0 else 0
    
    # Determine tier
    if rpi >= 150:
        tier = "Invincible Form 🔥"
    elif rpi >= 125:
        tier = "Top Performance ⭐"
    elif rpi >= 100:
        tier = "Meeting Expectations ✅"
    elif rpi >= 75:
        tier = "Catch Up Needed ⚠️"
    else:
        tier = "Behind Schedule 🔻"
    
    return {
        "date": target_date.isoformat(),
        "emails_sent": emails_sent,
        "meeting_hours": round(meeting_hours, 2),
        "expected_emails": round(expected_emails, 1),
        "rpi": rpi,
        "tier": tier,
        "is_weekend": is_weekend
    }

def update_database(stats: dict):
    """Update database with calculated stats."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        INSERT OR REPLACE INTO daily_stats 
        (date, emails_sent, expected_emails, rpi, meeting_hours)
        VALUES (?, ?, ?, ?, ?)
    """, (
        stats["date"],
        stats["emails_sent"],
        stats["expected_emails"],
        stats["rpi"],
        stats["meeting_hours"]
    ))
    
    conn.commit()
    conn.close()
    
    logging.info(f"✓ Updated {stats['date']}: {stats['emails_sent']} emails, "
                f"{stats['meeting_hours']}h meetings → RPI {stats['rpi']}% ({stats['tier']})")

def main():
    parser = argparse.ArgumentParser(description='Update productivity dashboard with real data')
    parser.add_argument('--emails', type=int, required=True, help='Number of emails sent')
    parser.add_argument('--meetings', type=float, required=True, help='Hours of meetings')
    parser.add_argument('--date', type=str, help='Date (YYYY-MM-DD), defaults to today')
    
    args = parser.parse_args()
    
    # Ensure schema
    ensure_schema()
    
    # Parse date
    if args.date:
        target_date = date.fromisoformat(args.date)
    else:
        target_date = date.today()
    
    # Calculate and update
    stats = calculate_rpi(args.emails, args.meetings, target_date)
    update_database(stats)
    
    # Output result
    print(json.dumps(stats, indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())
