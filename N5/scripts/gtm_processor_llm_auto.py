#!/usr/bin/env python3
"""
GTM Intelligence Processor - LLM-Based Extraction (Fully Automated)
Replaces regex-based parsers with LLM interpretation for robust insight extraction.
"""
import sqlite3
import logging
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
import anthropic
import sys
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
PATHS_YAML = WORKSPACE / "N5/prefs/paths/knowledge_paths.yaml"


def load_db_path() -> Path:
    try:
        with PATHS_YAML.open() as f:
            cfg = yaml.safe_load(f) or {}
        db_rel = (
            cfg.get("personal_knowledge", {})
            .get("market_intelligence", {})
            .get("db")
        )
        if not db_rel:
            raise KeyError("personal_knowledge.market_intelligence.db missing")
        return WORKSPACE / db_rel
    except Exception as exc:
        logger.error("Failed to resolve GTM DB from %s: %s", PATHS_YAML, exc)
        sys.exit(1)


DB_PATH = load_db_path()
MEETINGS_DIR = WORKSPACE / "Personal/Meetings"

EXTRACTION_PROMPT_TEMPLATE = """Extract GTM intelligence insights from this B31 stakeholder research file.

MEETING CONTEXT:
- Meeting ID: {meeting_id}
- Date: {meeting_date}

B31 CONTENT:
{content}

INSTRUCTIONS:
Read the B31 content and extract ALL insights into a structured JSON array.

For EACH insight, extract:
1. **title**: Concise insight title (what is the finding?)
2. **category**: Choose from: GTM & Distribution, Recruiting Pain Points, Hiring Manager Pain Points, Job Seeker Pain Points, Founder Pain Points, Product Strategy, Competitive Landscape, Market Dynamics, Pricing & Business Model, Partnership Strategy
3. **evidence**: Direct quotes with timestamps if available, specific examples
4. **why_it_matters**: Strategic implications for Careerspan (why should we care?)
5. **signal_strength**: Integer 1-5 (1=weak anecdote, 5=validated pattern across multiple sources)
6. **stakeholder_name**: Extract from content or context
7. **stakeholder_role**: Extract from content or context
8. **stakeholder_type**: Categorize as: Founder, Hiring Manager, Recruiter, Job Seeker, Consultant, Investor, Partner, Other
9. **quote**: Key quote that supports the insight

OUTPUT REQUIREMENTS:
- Return ONLY valid JSON array, no markdown formatting, no explanation
- Each insight must be a complete object with all 9 fields
- If a field cannot be determined, use reasonable defaults (e.g., "Unknown" for stakeholder_name)
- Signal strength should reflect confidence based on source credibility and evidence quality

CRITICAL: Output ONLY the JSON array starting with [ and ending with ]. No other text.
"""

def extract_insights_llm(b31_path: Path, meeting_id: str, meeting_date: str) -> list:
    """
    Extract insights using LLM via Anthropic API.
    Returns list of insight dictionaries.
    """
    try:
        content = b31_path.read_text()
        
        # Skip if file is too small (likely empty/stub)
        if len(content) < 200:
            logger.info(f"  Skipping {meeting_id}: File too small ({len(content)} bytes)")
            return []
        
        # Create extraction prompt
        prompt = EXTRACTION_PROMPT_TEMPLATE.format(
            meeting_id=meeting_id,
            meeting_date=meeting_date,
            content=content
        )
        
        # Initialize Anthropic client
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not set in environment")
            return []
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Call Claude
        logger.info(f"  🤖 Calling LLM for extraction...")
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Extract JSON from response
        response_text = response.content[0].text.strip()
        
        # Try to parse JSON
        try:
            insights = json.loads(response_text)
            if not isinstance(insights, list):
                logger.error(f"  ✗ LLM returned non-array: {type(insights)}")
                return []
            
            logger.info(f"  ✓ Extracted {len(insights)} insights")
            return insights
            
        except json.JSONDecodeError as e:
            logger.error(f"  ✗ JSON parse error: {e}")
            logger.error(f"  Response preview: {response_text[:500]}")
            
            # Save failed response for debugging
            debug_dir = Path("/home/.z/workspaces/gtm_extraction_debug")
            debug_dir.mkdir(parents=True, exist_ok=True)
            debug_file = debug_dir / f"{meeting_id}_failed_response.txt"
            debug_file.write_text(f"PROMPT:\n{prompt}\n\nRESPONSE:\n{response_text}")
            logger.info(f"  Debug saved: {debug_file}")
            
            return []
        
    except Exception as e:
        logger.error(f"  Error extracting from {meeting_id}: {e}")
        return []

def insert_insights(conn: sqlite3.Connection, insights: list, meeting_id: str, meeting_date: str, b31_path: str):
    """Insert extracted insights into database."""
    cursor = conn.cursor()
    inserted = 0
    
    for insight in insights:
        try:
            cursor.execute("""
                INSERT INTO gtm_insights (
                    meeting_id, meeting_date, stakeholder_name, stakeholder_company,
                    stakeholder_type, stakeholder_role, category, signal_strength,
                    title, insight, why_it_matters, quote, source_block, b31_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meeting_id,
                meeting_date,
                insight.get('stakeholder_name', 'Unknown'),
                insight.get('stakeholder_company', ''),
                insight.get('stakeholder_type', 'Other'),
                insight.get('stakeholder_role', ''),
                insight.get('category', 'Uncategorized'),
                insight.get('signal_strength', 1),
                insight.get('title', ''),
                insight.get('evidence', ''),
                insight.get('why_it_matters', ''),
                insight.get('quote', ''),
                insight.get('category', ''),  # source_block
                b31_path
            ))
            inserted += 1
        except Exception as e:
            logger.error(f"  Error inserting insight: {e}")
            continue
    
    conn.commit()
    return inserted

def process_meeting(conn: sqlite3.Connection, meeting_dir: Path) -> int:
    """Process one meeting directory."""
    meeting_id = meeting_dir.name
    
    # Find B31 file (try multiple patterns)
    b31_candidates = [
        meeting_dir / "B31_STAKEHOLDER_RESEARCH.md",
        meeting_dir / "B31_stakeholder_research.md",
        meeting_dir / "B31_strategic_intel.md",
    ]
    
    b31_path = None
    for candidate in b31_candidates:
        if candidate.exists():
            b31_path = candidate
            break
    
    if not b31_path:
        return 0
    
    # Extract date from meeting_id
    meeting_date = meeting_id[:10] if meeting_id[:10].count('-') == 2 else datetime.now().strftime('%Y-%m-%d')
    
    # Check if already processed
    cursor = conn.cursor()
    cursor.execute(
        "SELECT insights_extracted FROM gtm_processing_registry WHERE meeting_id = ?",
        (meeting_id,)
    )
    row = cursor.fetchone()
    if row and row[0] > 0:
        logger.info(f"⏭️  {meeting_id}: Already processed ({row[0]} insights)")
        return 0
    
    logger.info(f"🔄 Processing: {meeting_id}")
    
    # Extract insights using LLM
    insights = extract_insights_llm(b31_path, meeting_id, meeting_date)
    
    if not insights:
        logger.info(f"  ⚠️  No insights extracted")
        # Update registry
        cursor.execute("""
            INSERT OR REPLACE INTO gtm_processing_registry 
            (meeting_id, b31_path, processed_at, insights_extracted, extraction_version)
            VALUES (?, ?, CURRENT_TIMESTAMP, 0, '4.0-llm-auto')
        """, (meeting_id, str(b31_path)))
        conn.commit()
        return 0
    
    # Insert insights
    inserted = insert_insights(conn, insights, meeting_id, meeting_date, str(b31_path))
    
    # Update registry
    cursor.execute("""
        INSERT OR REPLACE INTO gtm_processing_registry 
        (meeting_id, b31_path, processed_at, insights_extracted, extraction_version)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?, '4.0-llm-auto')
    """, (meeting_id, str(b31_path), inserted))
    conn.commit()
    
    logger.info(f"  ✓ Inserted {inserted} insights")
    return inserted

def main():
    import argparse
    parser = argparse.ArgumentParser(description="GTM processor with LLM extraction")
    parser.add_argument("--meeting-id", help="Process specific meeting")
    parser.add_argument("--batch", type=int, help="Process N unprocessed meetings")
    parser.add_argument("--all", action="store_true", help="Process all unprocessed meetings")
    args = parser.parse_args()
    
    conn = sqlite3.connect(DB_PATH)
    
    # Find meetings to process
    meetings = []
    for meeting_dir in sorted(MEETINGS_DIR.iterdir()):
        if not meeting_dir.is_dir():
            continue
        
        if args.meeting_id:
            if meeting_dir.name == args.meeting_id:
                meetings.append(meeting_dir)
        else:
            meetings.append(meeting_dir)
    
    if args.meeting_id:
        logger.info(f"Processing specific meeting: {args.meeting_id}")
        if meetings:
            process_meeting(conn, meetings[0])
    elif args.batch:
        logger.info(f"Processing up to {args.batch} meetings")
        count = 0
        for meeting_dir in meetings:
            if count >= args.batch:
                break
            result = process_meeting(conn, meeting_dir)
            if result > 0:
                count += 1
    elif args.all:
        logger.info(f"Processing all {len(meetings)} meetings")
        for meeting_dir in meetings:
            process_meeting(conn, meeting_dir)
    else:
        logger.info("Usage: --meeting-id <ID> | --batch <N> | --all")
    
    conn.close()

if __name__ == "__main__":
    main()

