#!/usr/bin/env python3
"""
PROPER Dashboard Sync - Uses actual Gmail API data via stored results
This script can be called by a Zo agent that has Gmail access
"""
import sqlite3
import sys
import json
from datetime import datetime, date
from pathlib import Path

DB_PATH = '/home/workspace/productivity_tracker.db'

def parse_gmail_date(date_str):
    """Parse Gmail API ISO date to date object"""
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return dt.date()

def count_emails_by_date(gmail_data_file):
    """Count emails by date from Gmail API JSON output"""
    with open(gmail_data_file, 'r') as f:
        data = json.load(f)
    
    emails = data.get('ret', [])
    counts = {}
    
    for email in emails:
        email_date = parse_gmail_date(email['date'])
        date_str = email_date.isoformat()
        counts[date_str] = counts.get(date_str, 0) + 1
    
    return counts

def calculate_rpi(emails_sent, date_obj):
    """Calculate RPI based on emails sent and day of week"""
    is_weekend = date_obj.weekday() in (5, 6)  # Sat=5, Sun=6
    
    if is_weekend:
        expected_emails = 5.0
    else:
        # Weekday: assume 8 hours available, 0 meeting hours for now
        # TODO: Integrate calendar data for meeting_hours
        free_hours = 8.0
        expected_emails = (free_hours * 2.5) + 5.0
    
    rpi = round((emails_sent / expected_emails) * 100, 1) if expected_emails > 0 else 0
    return expected_emails, rpi

def update_database(date_str, emails_sent):
    """Update database with real counts"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    expected_emails, rpi = calculate_rpi(emails_sent, date_obj)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Ensure table exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            emails_sent INTEGER NOT NULL DEFAULT 0,
            expected_emails INTEGER NOT NULL DEFAULT 0,
            rpi REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        INSERT OR REPLACE INTO daily_stats (date, emails_sent, expected_emails, rpi)
        VALUES (?, ?, ?, ?)
    ''', (date_str, emails_sent, int(expected_emails), rpi))
    
    conn.commit()
    conn.close()
    
    print(f"✓ {date_str}: {emails_sent} emails, RPI {rpi}%")

def main(attawar_file, careerspan_file):
    """Sync dashboard with real Gmail data"""
    print("=" * 60)
    print("DASHBOARD SYNC - REAL DATA ONLY")
    print("=" * 60)
    
    # Count emails from both accounts
    print("\nCounting emails from attawar.v@gmail.com...")
    attawar_counts = count_emails_by_date(attawar_file)
    
    print("Counting emails from vrijen@mycareerspan.com...")
    careerspan_counts = count_emails_by_date(careerspan_file)
    
    # Combine counts
    all_dates = sorted(set(list(attawar_counts.keys()) + list(careerspan_counts.keys())))
    
    print(f"\nUpdating database for {len(all_dates)} dates...")
    for date_str in all_dates:
        total = attawar_counts.get(date_str, 0) + careerspan_counts.get(date_str, 0)
        update_database(date_str, total)
    
    print("\n" + "=" * 60)
    print("✓ SYNC COMPLETE - ALL DATA IS REAL")
    print("=" * 60)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 sync_dashboard_PROPER.py <attawar_json> <careerspan_json>")
        print("\nJSON files should contain Gmail API output with 'ret' array of emails")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2])
