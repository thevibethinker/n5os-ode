#!/usr/bin/env python3
"""
GTM Intelligence Rebuilder - Direct Interpretation
Processes B31 files by presenting content to Zo for interpretation.
No regex, no parsing - just human-readable prompts for AI interpretation.
"""
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
import sys
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = "/home/workspace/Knowledge/market_intelligence/gtm_intelligence.db"
MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")

def get_unprocessed_meetings(conn, limit=None):
    """Get meetings that haven't been processed or failed extraction."""
    cursor = conn.cursor()
    
    # Find all B31 files
    all_b31_files = list(MEETINGS_DIR.glob("*/B31_*.md"))
    
    # Get processing registry
    cursor.execute("SELECT meeting_id, insights_extracted FROM gtm_processing_registry")
    registry = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Find candidates: not in registry OR extracted 0 insights
    candidates = []
    for b31_path in all_b31_files:
        meeting_id = b31_path.parent.name
        
        # Skip if file is too small (empty/stub)
        if b31_path.stat().st_size < 200:
            continue
        
        insights_count = registry.get(meeting_id, None)
        if insights_count is None or insights_count == 0:
            candidates.append((meeting_id, str(b31_path)))
    
    if limit:
        candidates = candidates[:limit]
    
    return candidates

def prepare_for_interpretation(b31_path, meeting_id):
    """Read B31 file and prepare interpretation prompt."""
    content = Path(b31_path).read_text()
    
    # Extract meeting date from directory name
    parts = meeting_id.split('_', 1)
    meeting_date = parts[0] if len(parts) > 0 else datetime.now().strftime('%Y-%m-%d')
    
    prompt = f"""
I need you to extract GTM intelligence insights from this B31 stakeholder research file.

Meeting ID: {meeting_id}
Meeting Date: {meeting_date}
File: {b31_path}

===== B31 CONTENT =====
{content}
===== END CONTENT =====

Please extract ALL insights from this content and return them as a JSON array with this structure:
[
  {{
    "title": "Brief insight title",
    "category": "One of: GTM & Distribution, Product Strategy, Founder Pain Points, Market Dynamics, etc",
    "signal_strength": 1-5 (1=weak signal, 5=strong validated pattern),
    "insight": "Full description of what this insight means",
    "why_it_matters": "Why this is important for Careerspan's strategy",
    "quote": "Direct quote from the meeting that supports this",
    "stakeholder_name": "Name of person",
    "stakeholder_company": "Their company",
    "stakeholder_type": "One of: Founder, Job Seeker, Recruiter, Platform, Advisor, Investor, Other"
  }}
]

Extract insights regardless of format (structured headers, narrative, bullet points, etc).
Focus on insights that reveal market dynamics, customer pain points, GTM strategies, or competitive intelligence.

Return ONLY the JSON array, no other text.
"""
    
    return prompt, meeting_date

def save_insights_batch(conn, meeting_id, meeting_date, b31_path, insights_json):
    """Save extracted insights to database."""
    try:
        insights = json.loads(insights_json)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON for {meeting_id}: {e}")
        return 0
    
    if not isinstance(insights, list):
        logger.error(f"Expected list of insights for {meeting_id}, got {type(insights)}")
        return 0
    
    cursor = conn.cursor()
    inserted = 0
    
    for insight in insights:
        try:
            cursor.execute("""
                INSERT INTO gtm_insights (
                    meeting_id, meeting_date, b31_source,
                    stakeholder_name, stakeholder_company, stakeholder_type,
                    category, signal_strength, title, insight, why_it_matters, quote
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meeting_id,
                meeting_date,
                b31_path,
                insight.get('stakeholder_name', 'Unknown'),
                insight.get('stakeholder_company', ''),
                insight.get('stakeholder_type', 'Other'),
                insight.get('category', 'Uncategorized'),
                insight.get('signal_strength', 1),
                insight.get('title', 'Untitled'),
                insight.get('insight', ''),
                insight.get('why_it_matters', ''),
                insight.get('quote', '')
            ))
            inserted += 1
        except Exception as e:
            logger.error(f"Failed to insert insight for {meeting_id}: {e}")
    
    # Update registry
    cursor.execute("""
        INSERT OR REPLACE INTO gtm_processing_registry 
        (meeting_id, b31_path, processed_at, insights_extracted, extraction_version)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?, 'v4.0-llm-direct')
    """, (meeting_id, b31_path, inserted))
    
    conn.commit()
    logger.info(f"Saved {inserted} insights from {meeting_id}")
    return inserted

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Rebuild GTM intelligence with direct interpretation")
    parser.add_argument('--batch', type=int, default=1, help='Number of meetings to process')
    parser.add_argument('--meeting-id', help='Process specific meeting ID')
    parser.add_argument('--dry-run', action='store_true', help='Show prompts without processing')
    args = parser.parse_args()
    
    conn = sqlite3.connect(DB_PATH)
    
    if args.meeting_id:
        b31_files = list(MEETINGS_DIR.glob(f"{args.meeting_id}/B31_*.md"))
        if not b31_files:
            logger.error(f"No B31 file found for {args.meeting_id}")
            return
        b31_path = str(b31_files[0])
        prompt, meeting_date = prepare_for_interpretation(b31_path, args.meeting_id)
        
        print("\n" + "="*80)
        print("INTERPRETATION PROMPT")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")
        
        if not args.dry_run:
            print("Paste the JSON response from Zo below, then press Ctrl+D:")
            insights_json = sys.stdin.read()
            if insights_json.strip():
                save_insights_batch(conn, args.meeting_id, meeting_date, b31_path, insights_json)
    else:
        candidates = get_unprocessed_meetings(conn, limit=args.batch)
        logger.info(f"Found {len(candidates)} meetings to process")
        
        for meeting_id, b31_path in candidates:
            prompt, meeting_date = prepare_for_interpretation(b31_path, meeting_id)
            
            print("\n" + "="*80)
            print(f"MEETING: {meeting_id}")
            print("="*80)
            print(prompt)
            print("="*80 + "\n")
            
            if not args.dry_run:
                print("Paste JSON response (Ctrl+D when done):")
                insights_json = sys.stdin.read()
                if insights_json.strip():
                    save_insights_batch(conn, meeting_id, meeting_date, b31_path, insights_json)
                print("\n")
    
    conn.close()

if __name__ == "__main__":
    main()
