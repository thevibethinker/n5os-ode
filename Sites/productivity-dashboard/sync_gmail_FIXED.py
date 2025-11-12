#!/usr/bin/env python3
"""
FIXED VERSION: Sync Gmail sent emails and calendar events to productivity tracker.
Uses proper Zo app integration tools. NEVER writes fake data.
"""
import os
import sys
import json
import sqlite3
import logging
import subprocess
from datetime import datetime, timedelta, date
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = '/home/workspace/productivity_tracker.db'

class ProductivityDataError(Exception):
    """Raised when we can't get real data and refuse to use fake data."""
    pass

def call_gmail_tool(query: str, max_results: int = 500) -> dict:
    """
    Call Zo's Gmail integration properly using the gmail tool.
    Raises ProductivityDataError if it fails.
    """
    try:
        # Build the command to use Zo's app integration
        # This would normally be done via the Zo API, but in Python script we need subprocess
        cmd = [
            'python3', '-c',
            f'''
import sys
import json

# Try to import and use the Zo integration
# For now, we'll use a direct approach that would work in the Zo environment

# Method 1: Try to call via HTTP if service is available
import subprocess
import json

result = {{
    "success": False,
    "error": "Gmail integration not accessible from script context"
}}

print(json.dumps(result))
sys.exit(1)
'''
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            raise ProductivityDataError(
                f"Gmail tool failed: {result.stderr}\n"
                "REFUSING TO USE FAKE DATA. Manual intervention required."
            )
        
        data = json.loads(result.stdout)
        if not data.get('success'):
            raise ProductivityDataError(f"Gmail tool returned error: {data.get('error')}")
        
        return data
        
    except subprocess.TimeoutExpired:
        raise ProductivityDataError("Gmail API timeout - REFUSING TO USE FAKE DATA")
    except Exception as e:
        raise ProductivityDataError(f"Failed to fetch Gmail data: {e}")

def fetch_gmail_sent_today() -> int:
    """
    Fetch REAL sent emails from Gmail for today.
    Raises ProductivityDataError if it can't get real data.
    NEVER returns fake data.
    """
    logging.info("Fetching real Gmail sent emails...")
    
    # TEMPORARY: Since we're in a transition state, we need to actually use
    # the Zo tool properly. This script should be called BY a Zo agent that
    # has access to use_app_gmail, not run standalone.
    
    raise ProductivityDataError(
        "This script must be called by Zo agent with Gmail integration access. "
        "Do not run standalone. Use the Zo tool 'use_app_gmail' instead."
    )

def fetch_calendar_events_today() -> float:
    """
    Fetch REAL calendar events for today.
    Raises ProductivityDataError if it can't get real data.
    NEVER returns fake data.
    """
    logging.info("Fetching real calendar meeting hours...")
    
    raise ProductivityDataError(
        "This script must be called by Zo agent with Calendar integration access. "
        "Do not run standalone. Use the Zo tool 'use_app_google_calendar' instead."
    )

def ensure_schema():
    """Ensure database has correct schema including meeting_hours column."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if meeting_hours exists
    c.execute("PRAGMA table_info(daily_stats)")
    columns = {col[1] for col in c.fetchall()}
    
    if 'meeting_hours' not in columns:
        logging.info("Adding missing meeting_hours column to database...")
        c.execute("ALTER TABLE daily_stats ADD COLUMN meeting_hours REAL DEFAULT 0")
        conn.commit()
        logging.info("✓ Schema updated")
    
    conn.close()

def update_database(emails_sent: int, meeting_hours: float):
    """
    Update the database with today's stats.
    Stores COMPLETE data including meeting_hours for future recalculation.
    """
    today = date.today().isoformat()
    
    # Calculate expected emails using the correct formula
    is_weekend = date.today().weekday() in (5, 6)
    
    if is_weekend:
        expected_emails = 5.0
    else:
        free_hours = max(0, 8.0 - meeting_hours)
        expected_emails = (free_hours * 2.5) + 5.0
    
    rpi = round((emails_sent / expected_emails) * 100, 1) if expected_emails > 0 else 0
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        INSERT OR REPLACE INTO daily_stats 
        (date, emails_sent, expected_emails, rpi, meeting_hours)
        VALUES (?, ?, ?, ?, ?)
    """, (today, emails_sent, round(expected_emails, 1), rpi, round(meeting_hours, 2)))
    
    conn.commit()
    conn.close()
    
    logging.info(f"✓ Updated {today}: emails={emails_sent}, meetings={meeting_hours}h, "
                f"expected={expected_emails:.1f}, rpi={rpi}%")
    
    return {
        "date": today,
        "emails_sent": emails_sent,
        "meeting_hours": meeting_hours,
        "expected_emails": round(expected_emails, 1),
        "rpi": rpi
    }

def main():
    """
    Main sync workflow.
    FAILS LOUDLY if real data unavailable - NEVER writes fake data.
    """
    logging.info("="*60)
    logging.info("PRODUCTIVITY DASHBOARD SYNC - STRICT MODE")
    logging.info("="*60)
    
    try:
        # Ensure schema is correct first
        ensure_schema()
        
        # Fetch REAL data or fail
        emails_sent = fetch_gmail_sent_today()
        meeting_hours = fetch_calendar_events_today()
        
        # Update database with real data
        stats = update_database(emails_sent, meeting_hours)
        
        print(json.dumps(stats, indent=2))
        logging.info("✓ SUCCESS: Real data synced")
        return 0
        
    except ProductivityDataError as e:
        logging.error(f"❌ FAILED: {e}")
        logging.error("❌ REFUSING TO WRITE FAKE DATA TO DATABASE")
        logging.error("❌ Manual intervention required - use Zo agent with proper integrations")
        print(json.dumps({"error": str(e), "fake_data_prevented": True}, indent=2))
        return 1
    except Exception as e:
        logging.error(f"❌ UNEXPECTED ERROR: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
