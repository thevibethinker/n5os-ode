#!/usr/bin/env python3
"""
Productivity Dashboard Update Script - Clean Implementation
Updates dashboard database with real email/meeting data.

NO API CALLS. NO FALLBACKS. NO FAKE DATA.
Accepts real data from Zo agent as arguments.
"""
import sys
import argparse
import sqlite3
import logging
from datetime import datetime, date
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database configuration
DEFAULT_DB_PATH = "/home/workspace/productivity_tracker.db"

class RPICalculator:
    """Calculate RPI using correct formula."""
    
    @staticmethod
    def calculate_expected_emails(meeting_hours: float, is_weekend: bool) -> float:
        """
        Calculate expected emails based on meeting hours and day type.
        
        Formula:
        - Weekday: (free_hours × 2.5) + 5, where free_hours = 8 - meeting_hours
        - Weekend: (free_hours × 1.5) + 2, where free_hours = 6 - meeting_hours
        """
        if is_weekend:
            base_hours = 6.0
            multiplier = 1.5
            baseline = 2.0
        else:
            base_hours = 8.0
            multiplier = 2.5
            baseline = 5.0
        
        free_hours = max(0, base_hours - meeting_hours)
        expected = (free_hours * multiplier) + baseline
        return expected
    
    @staticmethod
    def calculate_rpi(emails_sent: int, expected_emails: float) -> float:
        """
        Calculate RPI percentage.
        
        Formula: (actual_emails / expected_emails) × 100
        """
        if expected_emails == 0:
            return 0.0
        return (emails_sent / expected_emails) * 100
    
    @staticmethod
    def get_tier(rpi: float) -> str:
        """Determine performance tier based on RPI."""
        if rpi >= 100:
            return "Crushing It! 🔥"
        elif rpi >= 85:
            return "Winning ⚡"
        elif rpi >= 75:
            return "Catch Up Needed ⚠️"
        else:
            return "Behind Schedule 🔻"


def update_database(
    target_date: date,
    emails_sent: int,
    meeting_hours: float,
    db_path: str = DEFAULT_DB_PATH
) -> dict:
    """
    Update database with real productivity data.
    
    Args:
        target_date: Date for this data
        emails_sent: Actual number of emails sent
        meeting_hours: Actual hours spent in meetings
        db_path: Path to database file
    
    Returns:
        Dict with calculated metrics
    """
    # Determine if weekend
    is_weekend = target_date.weekday() >= 5  # 5=Saturday, 6=Sunday
    
    # Calculate metrics
    expected_emails = RPICalculator.calculate_expected_emails(meeting_hours, is_weekend)
    rpi = RPICalculator.calculate_rpi(emails_sent, expected_emails)
    tier = RPICalculator.get_tier(rpi)
    
    # Update database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            emails_sent INTEGER NOT NULL,
            expected_emails REAL NOT NULL,
            rpi REAL NOT NULL,
            meeting_hours REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Upsert data
    cursor.execute("""
        INSERT INTO daily_stats (date, emails_sent, expected_emails, rpi, meeting_hours)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            emails_sent = excluded.emails_sent,
            expected_emails = excluded.expected_emails,
            rpi = excluded.rpi,
            meeting_hours = excluded.meeting_hours
    """, (
        target_date.isoformat(),
        emails_sent,
        round(expected_emails, 1),
        round(rpi, 1),
        round(meeting_hours, 2)
    ))
    
    conn.commit()
    conn.close()
    
    logging.info(f"✓ Updated {target_date.isoformat()}: {emails_sent} emails, {meeting_hours:.2f}h meetings, {rpi:.1f}% RPI")
    
    return {
        "date": target_date.isoformat(),
        "emails_sent": emails_sent,
        "meeting_hours": round(meeting_hours, 2),
        "expected_emails": round(expected_emails, 1),
        "rpi": round(rpi, 1),
        "tier": tier,
        "is_weekend": is_weekend
    }


def main():
    parser = argparse.ArgumentParser(
        description="Update productivity dashboard with real data"
    )
    parser.add_argument(
        "--emails",
        type=int,
        required=True,
        help="Number of emails sent"
    )
    parser.add_argument(
        "--meetings",
        type=float,
        required=True,
        help="Hours spent in meetings"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date in YYYY-MM-DD format (default: today)"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=DEFAULT_DB_PATH,
        help=f"Database path (default: {DEFAULT_DB_PATH})"
    )
    
    args = parser.parse_args()
    
    # Parse date
    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        target_date = date.today()
    
    # Validate inputs
    if args.emails < 0:
        logging.error("❌ ERROR: emails_sent cannot be negative")
        return 1
    
    if args.meetings < 0 or args.meetings > 24:
        logging.error("❌ ERROR: meeting_hours must be between 0 and 24")
        return 1
    
    # Update database
    try:
        stats = update_database(target_date, args.emails, args.meetings, args.db)
        
        # Print summary
        print("\n" + "="*50)
        print("📊 PRODUCTIVITY DASHBOARD UPDATE")
        print("="*50)
        print(f"Date:            {stats['date']}")
        print(f"Day Type:        {'Weekend' if stats['is_weekend'] else 'Weekday'}")
        print(f"Emails Sent:     {stats['emails_sent']}")
        print(f"Meeting Hours:   {stats['meeting_hours']:.2f}")
        print(f"Expected Emails: {stats['expected_emails']:.1f}")
        print(f"RPI:             {stats['rpi']:.1f}%")
        print(f"Status:          {stats['tier']}")
        print("="*50)
        print("\n✅ Dashboard updated successfully!")
        
        return 0
    
    except Exception as e:
        logging.error(f"❌ ERROR: Failed to update database: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
