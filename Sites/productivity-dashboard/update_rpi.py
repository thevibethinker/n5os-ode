#!/usr/bin/env python3
"""
Update productivity dashboard with correct RPI formula.

RPI = (actual_emails / expected_emails) × 100
Where: expected_emails = (meeting_hours × 3) + 5
"""

import sqlite3
import subprocess
import json
from datetime import datetime, date
from typing import Dict, Any


def get_meeting_hours_today() -> float:
    """Fetch today's meeting hours from calendar."""
    try:
        # Use Google Calendar API to get today's meetings
        today = date.today().isoformat()
        cmd = [
            'python3', '-c',
            f'''
import subprocess
import json
from datetime import datetime

result = subprocess.run(
    ["zo", "apps", "google_calendar", "list-events", 
     "--calendarId", "primary",
     "--timeMin", "{today}T00:00:00Z",
     "--timeMax", "{today}T23:59:59Z"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
total_hours = 0
for event in data.get("items", []):
    if "start" in event and "end" in event:
        start = event["start"].get("dateTime")
        end = event["end"].get("dateTime")
        if start and end:
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
            duration = (end_dt - start_dt).total_seconds() / 3600
            total_hours += duration
print(total_hours)
'''
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip() or 0)
    except Exception as e:
        print(f"Warning: Could not fetch meeting hours: {e}")
        return 0.0


def get_sent_emails_today() -> int:
    """Fetch count of sent emails today from database."""
    conn = sqlite3.connect("/home/workspace/productivity_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email_count FROM daily_stats WHERE date = date('now')")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


def calculate_rpi(actual_emails: int, meeting_hours: float) -> Dict[str, Any]:
    """Calculate RPI with correct formula.
    
    RPI = (actual_emails / expected_emails) × 100
    Where: expected_emails = (meeting_hours × 3) + base_expectation
           base_expectation = 10 for weekdays, 5 for weekends
    """
    from datetime import date
    
    # Determine base expectation based on day of week
    today = date.today()
    is_weekday = today.weekday() < 5  # Monday=0, Sunday=6
    base_expectation = 10 if is_weekday else 5
    
    expected_emails = int((meeting_hours * 3) + base_expectation)
    rpi = (actual_emails / expected_emails * 100) if expected_emails > 0 else 0
    
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
        "actual_emails": actual_emails,
        "expected_emails": expected_emails,
        "meeting_hours": meeting_hours,
        "rpi": round(rpi, 1),
        "tier": tier
    }


def update_database(stats: Dict[str, Any]):
    """Update the productivity tracker database."""
    db_path = "/home/workspace/productivity_tracker.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    today = date.today().isoformat()
    
    # Check if columns exist, add if needed
    cursor.execute("PRAGMA table_info(daily_stats)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "meeting_hours" not in columns:
        cursor.execute("ALTER TABLE daily_stats ADD COLUMN meeting_hours REAL DEFAULT 0")
    if "expected_emails" not in columns:
        cursor.execute("ALTER TABLE daily_stats ADD COLUMN expected_emails INTEGER DEFAULT 5")
    
    # Update record
    cursor.execute("""
        INSERT OR REPLACE INTO daily_stats 
        (date, email_count, total_words, rpi, meeting_hours, expected_emails)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        today,
        stats["actual_emails"],
        0,  # words not tracked in this system
        stats["rpi"],
        stats["meeting_hours"],
        stats["expected_emails"]
    ))
    
    conn.commit()
    conn.close()


def main():
    """Main execution."""
    print("🔄 Updating productivity dashboard with correct RPI formula...")
    
    # Get data
    print("📧 Fetching sent emails from database...")
    actual_emails = get_sent_emails_today()
    
    print("📅 Fetching meeting hours...")
    meeting_hours = get_meeting_hours_today()
    
    # Calculate RPI
    print("🧮 Calculating RPI...")
    stats = calculate_rpi(actual_emails, meeting_hours)
    
    # Update database
    print("💾 Updating database...")
    update_database(stats)
    
    # Display results
    print("\n" + "="*50)
    print("📊 PRODUCTIVITY DASHBOARD UPDATE")
    print("="*50)
    print(f"Date:            {date.today().isoformat()}")
    print(f"Meeting Hours:   {stats['meeting_hours']:.1f}")
    print(f"Expected Emails: {stats['expected_emails']}")
    print(f"Actual Emails:   {stats['actual_emails']}")
    print(f"RPI:             {stats['rpi']:.1f}%")
    print(f"Status:          {stats['tier']}")
    print("="*50)
    print("\n✅ Dashboard updated successfully!")


if __name__ == "__main__":
    main()
