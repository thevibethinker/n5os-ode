#!/usr/bin/env python3
"""
Update productivity dashboard with correct RPI formula.

NEW FORMULA:
- Weekdays: expected = (free_hours × 2.5) + 5, where free_hours = 8 - meeting_hours
- Weekends: expected = 5 (fixed)
- RPI = (actual_emails / expected_emails) × 100
"""

import sqlite3
import subprocess
import json
from datetime import datetime, date
from typing import Dict, Any


class RPICalculator:
    """Deterministic RPI calculator."""
    
    TOTAL_WORK_HOURS = 8.0
    EMAIL_RATE_PER_FREE_HOUR = 2.5
    WEEKDAY_BASE_EXPECTATION = 5.0
    WEEKEND_EXPECTATION = 5.0
    
    @staticmethod
    def is_weekend(date_obj: date) -> bool:
        """Check if date is Saturday (5) or Sunday (6)."""
        return date_obj.weekday() in (5, 6)
    
    @staticmethod
    def calculate_expected_emails(date_obj: date, meeting_hours: float) -> float:
        """Calculate expected emails for a given day."""
        if RPICalculator.is_weekend(date_obj):
            return RPICalculator.WEEKEND_EXPECTATION
        else:
            free_hours = RPICalculator.TOTAL_WORK_HOURS - meeting_hours
            free_hours = max(0, free_hours)
            expected = (free_hours * RPICalculator.EMAIL_RATE_PER_FREE_HOUR) + \
                       RPICalculator.WEEKDAY_BASE_EXPECTATION
            return expected
    
    @staticmethod
    def calculate_rpi(actual_emails: int, expected_emails: float) -> float:
        """Calculate RPI score."""
        if expected_emails == 0:
            return 0.0
        rpi = (actual_emails / expected_emails) * 100.0
        return round(rpi, 1)


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
    cursor.execute("SELECT emails_sent FROM daily_stats WHERE date = date('now')")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


def calculate_rpi(actual_emails: int, meeting_hours: float) -> Dict[str, Any]:
    """Calculate RPI with new formula using deterministic calculator."""
    today = date.today()
    
    # Use deterministic calculator
    expected_emails = RPICalculator.calculate_expected_emails(today, meeting_hours)
    rpi = RPICalculator.calculate_rpi(actual_emails, expected_emails)
    
    # Determine tier (unchanged logic)
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
        "expected_emails": round(expected_emails, 1),
        "meeting_hours": meeting_hours,
        "rpi": rpi,
        "tier": tier
    }


def update_database(stats: Dict[str, Any]):
    """Update the productivity tracker database."""
    db_path = "/home/workspace/productivity_tracker.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    today = date.today().isoformat()
    
    # Update record with new RPI
    cursor.execute("""
        UPDATE daily_stats 
        SET expected_emails = ?, rpi = ?
        WHERE date = ?
    """, (
        stats["expected_emails"],
        stats["rpi"],
        today
    ))
    
    conn.commit()
    conn.close()


def recalculate_all_rpi():
    """Recalculate RPI for all historical records."""
    db_path = "/home/workspace/productivity_tracker.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all records
    cursor.execute("SELECT date, emails_sent, meeting_hours FROM daily_stats")
    records = cursor.fetchall()
    
    print(f"\n🔄 Recalculating RPI for {len(records)} historical records...")
    
    for record in records:
        date_str, emails_sent, meeting_hours = record
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Calculate with new formula
        expected = RPICalculator.calculate_expected_emails(date_obj, meeting_hours or 0)
        rpi = RPICalculator.calculate_rpi(emails_sent or 0, expected)
        
        # Update
        cursor.execute("""
            UPDATE daily_stats 
            SET expected_emails = ?, rpi = ?
            WHERE date = ?
        """, (round(expected, 1), rpi, date_str))
        
        print(f"  {date_str}: {emails_sent} emails, {meeting_hours:.1f} mtg hrs → Expected: {expected:.1f}, RPI: {rpi:.1f}")
    
    conn.commit()
    conn.close()
    print("✅ All historical records updated!\n")


def main():
    """Main execution."""
    import sys
    
    # Check if --recalculate-all flag
    if "--recalculate-all" in sys.argv:
        recalculate_all_rpi()
        return
    
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
