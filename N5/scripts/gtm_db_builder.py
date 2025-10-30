#!/usr/bin/env python3
"""
GTM Intelligence Database Builder
Extracts B31 insights into SQLite database for surgical querying
"""
import re
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
DB_PATH = WORKSPACE / "Knowledge/market_intelligence/gtm_intelligence.db"
SCHEMA_PATH = WORKSPACE / "N5/schemas/gtm_intelligence.sql"
MEETINGS_DIR = WORKSPACE / "Personal/Meetings"

def init_database():
    """Initialize database with schema"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Load and execute schema
    schema = SCHEMA_PATH.read_text()
    conn.executescript(schema)
    conn.commit()
    
    logger.info(f"✓ Database initialized: {DB_PATH}")
    return conn

def parse_b31_file(b31_path: Path):
    """
    Parse B31_STAKEHOLDER_RESEARCH.md into structured insights
    Handles multiple format variations
    """
    content = b31_path.read_text()
    
    # Extract meeting metadata
    meeting_id = b31_path.parent.name
    
    date_match = re.search(r'\*\*Meeting Date\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
    if not date_match:
        # Fallback: extract from meeting_id
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', meeting_id)
    meeting_date = date_match.group(1) if date_match else meeting_id[:10]
    
    stakeholder_match = re.search(r'\*\*Stakeholder\*\*:\s*(.+?)(?:\n|$)', content)
    stakeholder_full = stakeholder_match.group(1).strip() if stakeholder_match else "Unknown"
    
    # Parse stakeholder name and role
    if ' - ' in stakeholder_full:
        stakeholder_name, stakeholder_role = stakeholder_full.split(' - ', 1)
    elif '→' in stakeholder_full:
        # Format: "David Speigel → see file..."
        stakeholder_name = stakeholder_full.split('→')[0].strip()
        stakeholder_role = None
    else:
        stakeholder_name = stakeholder_full
        stakeholder_role = None
    
    # Find all insights - try multiple patterns
    insights = []
    
    # Pattern 1: Standard format with signal strength dots in title
    pattern1 = r'## Insight \d+: (.+?) (●+○*)\n\n\*\*Category\*\*: (.+?)\n.*?\*\*What We Learned\*\*:\n(.+?)(?=\n\*\*Why It Matters\*\*:|## Insight|\Z)'
    
    # Pattern 2: Alternative format with signal strength after "Why it matters"
    pattern2 = r'## Insight \d+: (.+?)\n\n\*\*Evidence\*\*:(.+?)\n\n\*\*Why it matters\*\*:(.+?)\n\n\*\*Signal strength:\*\* (●+○+)(?:.+?)?\n\n\*\*Category:\*\* (.+?)(?:\n|$)'
    
    # Try pattern 1
    for match in re.finditer(pattern1, content, re.DOTALL):
        title = match.group(1).strip()
        signal_dots = match.group(2)
        category = match.group(3).strip()
        insight_text = match.group(4).strip()
        signal_strength = signal_dots.count('●')
        
        # Extract "Why It Matters"
        why_match = re.search(
            r'\*\*Why It Matters\*\*:\n(.+?)(?=\n\*\*|## Insight|\Z)',
            content[match.end():],
            re.DOTALL
        )
        why_it_matters = why_match.group(1).strip() if why_match else None
        
        # Extract quote
        quote_match = re.search(
            r'\*\*Quote\*\*:\n>\s*"(.+?)"',
            content[match.end():],
            re.DOTALL
        )
        quote = quote_match.group(1).strip() if quote_match else None
        
        confidence = "MEDIUM"
        
        insights.append({
            'title': title,
            'insight': insight_text,
            'why_it_matters': why_it_matters,
            'category': category,
            'signal_strength': signal_strength,
            'quote': quote,
            'confidence_level': confidence
        })
    
    # Try pattern 2 if pattern 1 found nothing
    if not insights:
        for match in re.finditer(pattern2, content, re.DOTALL):
            title = match.group(1).strip()
            evidence = match.group(2).strip()
            why_it_matters = match.group(3).strip()
            signal_dots = match.group(4).strip()
            category = match.group(5).strip()
            
            signal_strength = signal_dots.count('●')
            
            # Extract quote from evidence
            quote_match = re.search(r'"(.+?)"', evidence, re.DOTALL)
            quote = quote_match.group(1).strip() if quote_match else None
            
            insights.append({
                'title': title,
                'insight': evidence,
                'why_it_matters': why_it_matters,
                'category': category,
                'signal_strength': signal_strength,
                'quote': quote,
                'confidence_level': "MEDIUM"
            })
    
    # Enrich each insight with metadata
    for insight in insights:
        insight['meeting_id'] = meeting_id
        insight['meeting_date'] = meeting_date
        insight['source_b31_path'] = str(b31_path)
        insight['stakeholder_name'] = stakeholder_name
        insight['stakeholder_role'] = stakeholder_role
    
    return insights, stakeholder_name

def infer_stakeholder_type(stakeholder_name: str, stakeholder_role: str) -> str:
    """Infer stakeholder type from name/role"""
    role_lower = (stakeholder_role or "").lower()
    name_lower = stakeholder_name.lower()
    
    if any(x in role_lower for x in ['recruiter', 'recruiting', 'talent']):
        return 'recruiter'
    elif any(x in role_lower for x in ['founder', 'ceo', 'co-founder']):
        return 'founder'
    elif any(x in role_lower for x in ['director', 'vp', 'senior', 'manager']) and          any(x in role_lower for x in ['google', 'microsoft', 'amazon', 'meta', 'apple']):
        return 'big_company'
    elif any(x in role_lower for x in ['consultant', 'advisor', 'coach']):
        return 'consultant'
    elif any(x in role_lower for x in ['university', 'education', 'professor', 'year up']):
        return 'education'
    else:
        return 'other'

def extract_stakeholder_company(stakeholder_role: str) -> str:
    """Extract company name from role if present"""
    if not stakeholder_role:
        return None
    
    # Common patterns: "Role at Company" or "Role, Company"
    patterns = [
        r' at (.+?)(?:\s*\(|$)',
        r', (.+?)(?:\s*\(|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, stakeholder_role)
        if match:
            return match.group(1).strip()
    
    return None

def process_meeting(conn, meeting_dir: Path, force=False):
    """Process a single meeting's B31 file"""
    meeting_id = meeting_dir.name
    b31_path = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
    
    if not b31_path.exists():
        return 0
    
    # Check if already processed
    cursor = conn.execute(
        "SELECT insights_extracted FROM gtm_processing_registry WHERE meeting_id = ?",
        (meeting_id,)
    )
    existing = cursor.fetchone()
    
    if existing and not force:
        logger.info(f"⏭️  {meeting_id} already processed ({existing[0]} insights)")
        return 0
    
    try:
        insights, stakeholder_name = parse_b31_file(b31_path)
        
        if not insights:
            logger.warning(f"⚠️  {meeting_id}: No insights parsed")
            return 0
        
        # Infer stakeholder metadata
        stakeholder_role = insights[0].get('stakeholder_role')
        stakeholder_type = infer_stakeholder_type(stakeholder_name, stakeholder_role or "")
        stakeholder_company = extract_stakeholder_company(stakeholder_role or "")
        
        # Insert insights
        for insight in insights:
            insight['stakeholder_type'] = stakeholder_type
            insight['stakeholder_company'] = stakeholder_company
            
            conn.execute("""
                INSERT OR REPLACE INTO gtm_insights (
                    meeting_id, meeting_date, source_b31_path,
                    stakeholder_name, stakeholder_role, stakeholder_type, stakeholder_company,
                    category, signal_strength, title, insight, why_it_matters, quote, confidence_level
                ) VALUES (
                    :meeting_id, :meeting_date, :source_b31_path,
                    :stakeholder_name, :stakeholder_role, :stakeholder_type, :stakeholder_company,
                    :category, :signal_strength, :title, :insight, :why_it_matters, :quote, :confidence_level
                )
            """, insight)
        
        # Update registry
        conn.execute("""
            INSERT OR REPLACE INTO gtm_processing_registry (meeting_id, b31_path, insights_extracted)
            VALUES (?, ?, ?)
        """, (meeting_id, str(b31_path), len(insights)))
        
        conn.commit()
        logger.info(f"✓ {meeting_id}: {len(insights)} insights extracted")
        return len(insights)
        
    except Exception as e:
        logger.error(f"❌ {meeting_id}: {e}", exc_info=True)
        return 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build GTM Intelligence Database")
    parser.add_argument('--rebuild', action='store_true', help='Force rebuild all meetings')
    parser.add_argument('--meeting-id', help='Process specific meeting only')
    args = parser.parse_args()
    
    logger.info("Starting GTM Intelligence Database Builder...")
    
    # Initialize database
    conn = init_database()
    
    # Find meetings with B31 files
    meetings = []
    for meeting_dir in MEETINGS_DIR.iterdir():
        if meeting_dir.is_dir() and 'external' in meeting_dir.name:
            b31_path = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
            if b31_path.exists():
                if args.meeting_id:
                    if meeting_dir.name == args.meeting_id:
                        meetings.append(meeting_dir)
                else:
                    meetings.append(meeting_dir)
    
    logger.info(f"Found {len(meetings)} meetings with B31 files")
    
    # Process meetings
    total_insights = 0
    for meeting_dir in sorted(meetings):
        insights_count = process_meeting(conn, meeting_dir, force=args.rebuild)
        total_insights += insights_count
    
    conn.close()
    
    logger.info(f"\n✓ Complete: {total_insights} total insights extracted")
    logger.info(f"✓ Database: {DB_PATH}")
    
    return 0

if __name__ == "__main__":
    exit(main())
