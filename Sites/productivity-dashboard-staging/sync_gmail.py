#!/usr/bin/env python3
"""
Sync Gmail sent emails to productivity tracker database using native Zo APIs.
"""
import os
import sys
import json
import sqlite3
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

DB_PATH = '/home/workspace/productivity_tracker.db'
ZO_API_KEY = os.getenv('ZO_CLIENT_IDENTITY_TOKEN')

def call_zo_api(endpoint: str, method='GET', data=None):
    """Call Zo internal API."""
    import requests
    headers = {}
    if ZO_API_KEY:
        headers['Authorization'] = f'Bearer {ZO_API_KEY}'
    
    url = f'http://localhost:8765{endpoint}'
    if method == 'POST':
        resp = requests.post(url, json=data, headers=headers)
    else:
        resp = requests.get(url, headers=headers)
    
    resp.raise_for_status()
    return resp.json()

def fetch_gmail_sent_today():
    """Fetch sent emails from Gmail for today."""
    try:
        today = datetime.now().date()
        query = f'in:sent after:{today.isoformat()}'
        
        result = call_zo_api('/api/tools/gmail/find-email', 'POST', {
            'q': query,
            'maxResults': 500,
            'withTextPayload': False
        })
        
        return result.get('ret', [])
    
    except Exception as e:
        logging.error(f"Error fetching Gmail: {e}")
        return []

def fetch_calendar_events_today():
    """Fetch calendar events for today."""
    try:
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        result = call_zo_api('/api/tools/google-calendar/list-events', 'POST', {
            'calendarId': 'primary',
            'singleEvents': True,
            'timeMin': f'{today.isoformat()}T00:00:00-05:00',
            'timeMax': f'{tomorrow.isoformat()}T00:00:00-05:00',
            'maxResults': 2500,
            'orderBy': 'startTime'
        })
        
        events = result.get('ret', [])
        total_minutes = 0
        
        for event in events:
            start = event.get('start', {}).get('dateTime')
            end = event.get('end', {}).get('dateTime')
            if start and end:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                duration = (end_dt - start_dt).total_seconds() / 60
                total_minutes += duration
        
        return round(total_minutes / 60, 2)
    
    except Exception as e:
        logging.error(f"Error fetching calendar: {e}")
        return 0.0

def update_database(emails_sent, meeting_hours):
    """Update the database with today's stats."""
    today = datetime.now().date().isoformat()
    
    expected_emails = round((meeting_hours * 3) + 10)
    rpi = round((emails_sent / expected_emails) * 100, 1) if expected_emails > 0 else 0
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("PRAGMA table_info(daily_stats)")
    cols = {row[1] for row in c.fetchall()}
    if 'expected_emails' not in cols:
        c.execute("ALTER TABLE daily_stats ADD COLUMN expected_emails REAL DEFAULT 0")
    if 'rpi' not in cols:
        c.execute("ALTER TABLE daily_stats ADD COLUMN rpi REAL DEFAULT 0")
    
    c.execute("""
        INSERT OR REPLACE INTO daily_stats (date, emails_sent, expected_emails, rpi)
        VALUES (?, ?, ?, ?)
    """, (today, emails_sent, expected_emails, rpi))
    
    conn.commit()
    conn.close()
    
    logging.info(f"Updated {today}: emails={emails_sent}, expected={expected_emails}, rpi={rpi}")
    return {"date": today, "emails_sent": emails_sent, "expected_emails": expected_emails, "rpi": rpi}

def main():
    """Main sync workflow."""
    logging.info("Starting Gmail sync...")
    
    # Install requests if needed
    try:
        import requests
    except ImportError:
        logging.info("Installing requests...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'requests'], check=True)
        import requests
    
    emails = fetch_gmail_sent_today()
    emails_sent = len(emails)
    logging.info(f"Fetched {emails_sent} sent emails for today")
    
    meeting_hours = fetch_calendar_events_today()
    logging.info(f"Calculated {meeting_hours} meeting hours for today")
    
    stats = update_database(emails_sent, meeting_hours)
    
    print(json.dumps(stats, indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())
