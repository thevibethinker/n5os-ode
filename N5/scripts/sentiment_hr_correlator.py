#!/usr/bin/env python3
"""
Sentiment-HR Correlator - Correlates meeting sentiment (from B15 blocks) with HR data.

Architecture:
- LLM-powered extraction (no regex for content parsing)
- SQLite for structured storage after extraction
- Flexible to B15 format changes

provenance: con_wne5ccsJoVnFSW6f
"""

import argparse
import json
import os
import sqlite3
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Paths
WORKOUTS_DB = Path("/home/workspace/Personal/Health/workouts.db")
PERFORMANCE_DB = Path("/home/workspace/N5/data/performance.db")
MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")

def init_db():
    """Initialize the sentiment correlation tables."""
    conn = sqlite3.connect(PERFORMANCE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meeting_sentiment (
            id INTEGER PRIMARY KEY,
            meeting_date TEXT NOT NULL,
            meeting_folder TEXT NOT NULL UNIQUE,
            b15_path TEXT,
            energy_rating REAL,
            sentiment_category TEXT,
            relationship_health REAL,
            raw_extraction TEXT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_hr_correlation (
            id INTEGER PRIMARY KEY,
            meeting_folder TEXT NOT NULL,
            meeting_date TEXT NOT NULL,
            energy_rating REAL,
            hr_before REAL,
            hr_during REAL,
            hr_after REAL,
            hr_delta REAL,
            correlated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_folder) REFERENCES meeting_sentiment(meeting_folder)
        )
    """)
    
    conn.commit()
    conn.close()


def llm_extract_sentiment(b15_content: str) -> dict:
    """
    Use LLM to extract sentiment data from B15 block content.
    Flexible to format changes - LLM handles semantic understanding.
    """
    prompt = f"""Extract the following from this meeting sentiment/energy block. Return ONLY valid JSON, no other text.

Required fields:
- energy_rating: number 1-10 (the overall energy/engagement score)
- sentiment_category: string (e.g., "HIGH POSITIVE", "COLLABORATIVE", "TENSE", etc.)
- relationship_health: number 1-10 (if present, otherwise null)

B15 Content:
{b15_content[:3000]}

Return JSON like: {{"energy_rating": 8, "sentiment_category": "HIGH POSITIVE + COLLABORATIVE", "relationship_health": 8.5}}
"""
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", ""),
                "content-type": "application/json"
            },
            json={
                "input": prompt
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", "")
            # Parse JSON from response
            try:
                # Find JSON in response
                import re
                json_match = re.search(r'\{[^}]+\}', output)
                if json_match:
                    return json.loads(json_match.group())
                return json.loads(output)
            except json.JSONDecodeError:
                print(f"  [Warning] Could not parse LLM response as JSON")
                return {}
        else:
            print(f"  [Warning] LLM extraction failed: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"  [Warning] LLM extraction error: {e}")
        return {}


def extract_date_from_folder(folder_name: str) -> Optional[str]:
    """Extract date from folder name. Uses simple string parsing, not regex."""
    # Folder names typically start with YYYY-MM-DD
    parts = folder_name.split("_")
    if parts and len(parts[0]) == 10:
        date_str = parts[0]
        # Validate it looks like a date
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            pass
    return None


def scan_and_extract_b15_blocks():
    """Scan for B15 blocks and extract sentiment using LLM."""
    init_db()
    conn = sqlite3.connect(PERFORMANCE_DB)
    cursor = conn.cursor()
    
    print("Scanning for B15 blocks and extracting with LLM...")
    
    # Find all B15 files
    b15_files = list(MEETINGS_DIR.rglob("B15*.md"))
    print(f"Found {len(b15_files)} B15 blocks")
    
    extracted = 0
    skipped = 0
    
    for b15_path in b15_files:
        folder_name = b15_path.parent.name
        
        # Check if already extracted
        cursor.execute("SELECT id FROM meeting_sentiment WHERE meeting_folder = ?", (folder_name,))
        if cursor.fetchone():
            skipped += 1
            continue
        
        # Extract date from folder
        meeting_date = extract_date_from_folder(folder_name)
        if not meeting_date:
            print(f"  Skipping {folder_name} - cannot determine date")
            continue
        
        # Read B15 content
        with open(b15_path, 'r') as f:
            content = f.read()
        
        # LLM extraction
        print(f"  Extracting: {folder_name[:50]}...")
        extraction = llm_extract_sentiment(content)
        
        if extraction:
            cursor.execute("""
                INSERT INTO meeting_sentiment 
                (meeting_date, meeting_folder, b15_path, energy_rating, sentiment_category, relationship_health, raw_extraction)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                meeting_date,
                folder_name,
                str(b15_path),
                extraction.get('energy_rating'),
                extraction.get('sentiment_category'),
                extraction.get('relationship_health'),
                json.dumps(extraction)
            ))
            extracted += 1
            print(f"    ✓ Energy: {extraction.get('energy_rating')}/10, Sentiment: {extraction.get('sentiment_category')}")
        else:
            print(f"    ✗ Could not extract sentiment")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Extracted {extracted} new meetings, skipped {skipped} already processed")


def get_hr_for_timerange(cursor, start_time: str, end_time: str) -> Optional[float]:
    """Get average HR for a time range."""
    cursor.execute("""
        SELECT AVG(bpm) as avg_hr
        FROM intraday_heart_rate
        WHERE datetime_local >= ? AND datetime_local < ?
    """, (start_time, end_time))
    row = cursor.fetchone()
    return row[0] if row and row[0] else None


def correlate_sentiment_with_hr():
    """Correlate extracted sentiment with HR data."""
    init_db()
    
    perf_conn = sqlite3.connect(PERFORMANCE_DB)
    perf_conn.row_factory = sqlite3.Row
    perf_cursor = perf_conn.cursor()
    
    hr_conn = sqlite3.connect(WORKOUTS_DB)
    hr_conn.row_factory = sqlite3.Row
    hr_cursor = hr_conn.cursor()
    
    # Get HR data date range
    hr_cursor.execute("SELECT MIN(datetime_local), MAX(datetime_local) FROM intraday_heart_rate")
    hr_range = hr_cursor.fetchone()
    if not hr_range or not hr_range[0]:
        print("No HR data available")
        return
    
    hr_start = hr_range[0][:10]
    hr_end = hr_range[1][:10]
    print(f"HR data available: {hr_start} to {hr_end}")
    
    # Get meetings with sentiment that fall within HR date range
    perf_cursor.execute("""
        SELECT meeting_date, meeting_folder, energy_rating, sentiment_category
        FROM meeting_sentiment
        WHERE meeting_date >= ? AND meeting_date <= ?
          AND energy_rating IS NOT NULL
    """, (hr_start, hr_end))
    
    meetings = perf_cursor.fetchall()
    print(f"Found {len(meetings)} meetings with sentiment in HR date range")
    
    correlated = 0
    
    for meeting in meetings:
        meeting_date = meeting['meeting_date']
        folder = meeting['meeting_folder']
        energy = meeting['energy_rating']
        
        # Check if already correlated
        perf_cursor.execute(
            "SELECT id FROM sentiment_hr_correlation WHERE meeting_folder = ?", 
            (folder,)
        )
        if perf_cursor.fetchone():
            continue
        
        # Assume meeting around 9-10am if we don't have exact time
        # (Could be enhanced to parse from calendar or manifest)
        meeting_start = f"{meeting_date}T09:00:00"
        meeting_end = f"{meeting_date}T10:00:00"
        before_start = f"{meeting_date}T08:00:00"
        after_end = f"{meeting_date}T11:00:00"
        
        hr_before = get_hr_for_timerange(hr_cursor, before_start, meeting_start)
        hr_during = get_hr_for_timerange(hr_cursor, meeting_start, meeting_end)
        hr_after = get_hr_for_timerange(hr_cursor, meeting_end, after_end)
        
        if hr_during:
            hr_delta = hr_during - hr_before if hr_before else None
            
            perf_cursor.execute("""
                INSERT INTO sentiment_hr_correlation
                (meeting_folder, meeting_date, energy_rating, hr_before, hr_during, hr_after, hr_delta)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (folder, meeting_date, energy, hr_before, hr_during, hr_after, hr_delta))
            
            correlated += 1
            print(f"  ✓ {meeting_date}: Energy {energy}/10, HR {hr_during:.0f} bpm (Δ{hr_delta:+.1f})" if hr_delta else f"  ✓ {meeting_date}: Energy {energy}/10, HR {hr_during:.0f} bpm")
    
    perf_conn.commit()
    perf_conn.close()
    hr_conn.close()
    
    print(f"\n✓ Correlated {correlated} meetings with HR data")


def generate_insights():
    """Generate insights from sentiment-HR correlations."""
    conn = sqlite3.connect(PERFORMANCE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n" + "=" * 50)
    print("   SENTIMENT-HR CORRELATION INSIGHTS")
    print("=" * 50)
    
    # Overall stats
    cursor.execute("""
        SELECT 
            COUNT(*) as count,
            AVG(energy_rating) as avg_energy,
            AVG(hr_during) as avg_hr,
            AVG(hr_delta) as avg_delta
        FROM sentiment_hr_correlation
        WHERE hr_during IS NOT NULL
    """)
    row = cursor.fetchone()
    
    if not row or row['count'] == 0:
        print("\nNo correlation data yet. Run 'extract' then 'correlate' first.")
        return
    
    print(f"\nTotal Meetings Analyzed: {row['count']}")
    print(f"Average Energy Rating:   {row['avg_energy']:.1f}/10")
    print(f"Average Meeting HR:      {row['avg_hr']:.0f} bpm")
    if row['avg_delta']:
        print(f"Average HR Delta:        {row['avg_delta']:+.1f} bpm")
    
    # By energy rating group
    print("\n--- Sentiment vs. Physiology Patterns ---\n")
    cursor.execute("""
        SELECT 
            CASE 
                WHEN energy_rating >= 7 THEN 'High (7-10)'
                WHEN energy_rating >= 4 THEN 'Medium (4-6)'
                ELSE 'Low (1-3)'
            END as rating_group,
            AVG(hr_during) as avg_hr,
            AVG(hr_delta) as avg_delta,
            COUNT(*) as count
        FROM sentiment_hr_correlation
        WHERE hr_during IS NOT NULL
        GROUP BY rating_group
        ORDER BY avg_hr DESC
    """)
    
    print(f"{'Rating Group':<20} {'Avg HR':>10} {'Avg Δ':>12} {'Count':>8}")
    print("-" * 55)
    
    for row in cursor.fetchall():
        delta_str = f"{row['avg_delta']:+.1f}" if row['avg_delta'] else "N/A"
        print(f"{row['rating_group']:<20} {row['avg_hr']:.0f} bpm    {delta_str:>10}    {row['count']:>5}")
    
    # Key insight
    cursor.execute("""
        SELECT 
            AVG(CASE WHEN energy_rating >= 7 THEN hr_during END) as high_energy_hr,
            AVG(CASE WHEN energy_rating < 7 THEN hr_during END) as low_energy_hr
        FROM sentiment_hr_correlation
        WHERE hr_during IS NOT NULL
    """)
    row = cursor.fetchone()
    
    print("\n--- Key Insight ---")
    if row['high_energy_hr'] and row['low_energy_hr']:
        diff = row['high_energy_hr'] - row['low_energy_hr']
        if diff > 0:
            print(f"High-energy meetings correlate with {diff:.1f} bpm HIGHER heart rate.")
            print("→ Positive meetings are energizing, not calming.")
        else:
            print(f"Low-energy meetings correlate with {abs(diff):.1f} bpm HIGHER heart rate.")
            print("→ Difficult meetings may be causing stress response.")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Sentiment-HR Correlator (LLM-powered)")
    parser.add_argument('command', choices=['extract', 'correlate', 'insights', 'full'],
                        help='extract=LLM parse B15 blocks, correlate=match with HR, insights=analysis, full=all steps')
    
    args = parser.parse_args()
    
    if args.command == 'extract':
        scan_and_extract_b15_blocks()
    elif args.command == 'correlate':
        correlate_sentiment_with_hr()
    elif args.command == 'insights':
        generate_insights()
    elif args.command == 'full':
        scan_and_extract_b15_blocks()
        correlate_sentiment_with_hr()
        generate_insights()


if __name__ == "__main__":
    main()


