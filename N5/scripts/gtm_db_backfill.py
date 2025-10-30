#!/usr/bin/env python3
"""
One-off backfill: Extract insights from existing B31 files (forgiving parser)
"""
import re
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
DB_PATH = WORKSPACE / "Knowledge/market_intelligence/gtm_intelligence.db"
MEETINGS_DIR = WORKSPACE / "Personal/Meetings"

def extract_insights_flexible(content: str):
    """Flexible parser - split by ## Insight headers"""
    # Split by insight headers
    parts = re.split(r'(## Insight \d+:[^\n]+)', content)
    
    insights = []
    for i in range(1, len(parts), 2):
        if i+1 >= len(parts):
            break
            
        header = parts[i]
        body = parts[i+1]
        
        # Extract title from header
        title_match = re.search(r'## Insight \d+:\s*(.+)', header)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        
        # Extract fields from body (case-insensitive, flexible)
        category = "Uncategorized"
        cat_match = re.search(r'\*\*Category:\*\*\s*(.+?)(?:\n|$)', body, re.IGNORECASE)
        if cat_match:
            category = cat_match.group(1).strip()
        
        signal_strength = 3  # default
        sig_match = re.search(r'\*\*Signal strength:\*\*\s*(●+)', body, re.IGNORECASE)
        if sig_match:
            signal_strength = sig_match.group(1).count('●')
        
        # Build insight text (everything up to "Source Credibility" or next section)
        insight_text = body
        if "**Source Credibility:**" in insight_text:
            insight_text = insight_text.split("**Source Credibility:**")[0]
        
        insight_text = insight_text.strip()
        
        if title and len(insight_text) > 50:  # Has meaningful content
            insights.append({
                'title': title,
                'category': category,
                'signal_strength': signal_strength,
                'insight': insight_text[:2000],  # Limit length
                'quote': "",
                'why_it_matters': ""
            })
    
    return insights

def process_meeting(conn, meeting_dir: Path):
    """Process one meeting"""
    meeting_id = meeting_dir.name
    b31_path = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
    
    if not b31_path.exists():
        return 0
    
    # Check if already processed
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM gtm_insights WHERE meeting_id = ?", (meeting_id,))
    if cursor.fetchone()[0] > 0:
        logger.info(f"⏭️  {meeting_id}: Already in database")
        return 0
    
    # Extract meeting date
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', meeting_id)
    meeting_date = date_match.group(1) if date_match else "2025-01-01"
    
    # Extract insights
    try:
        content = b31_path.read_text()
        insights = extract_insights_flexible(content)
    except Exception as e:
        logger.warning(f"⚠️  {meeting_id}: Extraction failed - {e}")
        return 0
    
    if not insights:
        logger.warning(f"⚠️  {meeting_id}: No insights parsed")
        return 0
    
    # Infer stakeholder from meeting_id
    stakeholder_name = "Unknown"
    if "_external-" in meeting_id:
        parts = meeting_id.split("_external-")[1].split("_")[0]
        stakeholder_name = parts.replace("-", " ").title()
    
    # Insert insights
    for insight in insights:
        try:
            cursor.execute("""
                INSERT INTO gtm_insights 
                (meeting_id, meeting_date, source_b31_path, stakeholder_name, 
                 stakeholder_role, stakeholder_type, category, signal_strength, 
                 title, insight, quote, why_it_matters)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meeting_id,
                meeting_date,
                str(b31_path),
                stakeholder_name,
                "",
                "external",
                insight['category'],
                insight['signal_strength'],
                insight['title'],
                insight['insight'],
                insight['quote'],
                insight['why_it_matters']
            ))
        except Exception as e:
            logger.warning(f"Failed to insert insight: {e}")
            continue
    
    conn.commit()
    logger.info(f"✓ {meeting_id}: {len(insights)} insights extracted")
    return len(insights)

def main():
    conn = sqlite3.connect(DB_PATH)
    
    # Find all meetings with B31 files
    meetings = []
    for meeting_dir in MEETINGS_DIR.iterdir():
        if meeting_dir.is_dir() and "external" in meeting_dir.name:
            b31 = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
            if b31.exists():
                meetings.append(meeting_dir)
    
    logger.info(f"Found {len(meetings)} external meetings with B31 files")
    
    # Process all
    total = 0
    for meeting_dir in sorted(meetings):
        count = process_meeting(conn, meeting_dir)
        total += count
    
    conn.close()
    
    logger.info(f"\n✓ Backfill complete: {total} total insights extracted")
    logger.info(f"✓ Database: {DB_PATH}")
    
    return 0

if __name__ == "__main__":
    exit(main())
