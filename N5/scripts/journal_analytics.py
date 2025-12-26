#!/usr/bin/env python3
import sqlite3
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
import sys

DB_PATH = Path("/home/workspace/N5/data/journal.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def analyze_mood_trends(days=30):
    conn = get_db()
    cursor = conn.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    cursor.execute("""
        SELECT date(created_at) as date, mood, count(*) as count
        FROM journal_entries 
        WHERE created_at >= ? AND mood IS NOT NULL
        GROUP BY date, mood
        ORDER BY date
    """, (cutoff.isoformat(),))
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n## Mood Trends (Last {days} days)")
    if not rows:
        print("No mood data found.")
        return

    # ASCII Chart or list
    for row in rows:
        print(f"{row['date']}: {row['mood']} ({row['count']})")

def analyze_tags(days=30):
    conn = get_db()
    cursor = conn.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    cursor.execute("""
        SELECT tags
        FROM journal_entries 
        WHERE created_at >= ? AND tags IS NOT NULL
    """, (cutoff.isoformat(),))
    
    rows = cursor.fetchall()
    conn.close()
    
    tag_counts = Counter()
    for row in rows:
        if row['tags']:
            # Handle comma-separated tags
            tags = [t.strip() for t in row['tags'].split(',') if t.strip()]
            tag_counts.update(tags)
            
    print(f"\n## Top Tags (Last {days} days)")
    if not tag_counts:
        print("No tags found.")
        return
        
    for tag, count in tag_counts.most_common(10):
        print(f"- {tag}: {count}")

def analyze_temptations(days=30):
    conn = get_db()
    cursor = conn.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    cursor.execute("""
        SELECT count(*) as total,
               COALESCE(sum(case when created_at >= datetime('now', '-7 days') then 1 else 0 end), 0) as last_week
        FROM journal_entries 
        WHERE entry_type = 'temptation' AND created_at >= ?
    """, (cutoff.isoformat(),))
    
    stats = cursor.fetchone()
    conn.close()
    
    print(f"\n## Temptation Tracking")
    print(f"Total entries (last {days}d): {stats['total']}")
    print(f"Last 7 days: {stats['last_week']}")

def main():
    parser = argparse.ArgumentParser(description="Journal Analytics")
    parser.add_argument('--days', type=int, default=30, help='Analysis period in days')
    args = parser.parse_args()
    
    print(f"# Journal Analytics Report - {datetime.now().strftime('%Y-%m-%d')}")
    analyze_mood_trends(args.days)
    analyze_tags(args.days)
    analyze_temptations(args.days)

if __name__ == "__main__":
    main()


