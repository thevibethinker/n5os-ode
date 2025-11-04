#!/usr/bin/env python3
"""
GTM Intelligence Direct Extraction
No regex, no API calls - just presents content to Zo for interpretation during execution.
"""
import sqlite3
import argparse
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
DB_PATH = WORKSPACE / "Knowledge/market_intelligence/gtm_intelligence.db"
MEETINGS_DIR = WORKSPACE / "Personal/Meetings"


def extract_meeting_info(meeting_dir: Path):
    """Extract meeting ID and date from directory name."""
    dir_name = meeting_dir.name
    # Remove emoji prefixes
    clean_name = ''.join(c for c in dir_name if c.isascii() or c.isspace()).strip()
    parts = clean_name.split('_', 1)
    
    if len(parts) >= 1 and '-' in parts[0]:
        return dir_name, parts[0]
    return dir_name, datetime.now().strftime('%Y-%m-%d')


def find_b31_file(meeting_dir: Path):
    """Find B31 file in meeting directory."""
    b31_files = list(meeting_dir.glob("B31_*.md"))
    if not b31_files:
        return None
    # Prefer specific names
    priorities = ["B31_strategic_intel.md", "B31_STAKEHOLDER_RESEARCH.md", "B31_stakeholder_research.md"]
    for priority in priorities:
        for b31_file in b31_files:
            if b31_file.name == priority:
                return b31_file
    return b31_files[0]


def read_b31_content(b31_path: Path):
    """Read B31 file content."""
    try:
        content = b31_path.read_text()
        # Basic checks
        if len(content) < 100:
            return None, "too_short"
        if "## Stakeholder Research" in content and len(content) < 200:
            return None, "empty_stub"
        return content, "ok"
    except Exception as e:
        logger.error(f"Error reading {b31_path}: {e}")
        return None, "read_error"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--meeting-id", help="Specific meeting ID to process")
    parser.add_argument("--batch", type=int, help="Process N unprocessed meetings")
    parser.add_argument("--list", action="store_true", help="List processable meetings")
    args = parser.parse_args()

    # Find all meetings
    meetings = sorted([d for d in MEETINGS_DIR.iterdir() if d.is_dir()])
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Filter to unprocessed or failed extractions
    cursor.execute("SELECT meeting_id FROM gtm_processing_registry WHERE insights_extracted = 0")
    failed_ids = {row[0] for row in cursor.fetchall()}
    
    processable = []
    for meeting_dir in meetings:
        meeting_id, meeting_date = extract_meeting_info(meeting_dir)
        b31_file = find_b31_file(meeting_dir)
        
        if not b31_file:
            continue
            
        content, status = read_b31_content(b31_file)
        if status != "ok":
            continue
            
        # Check if needs processing
        cursor.execute("""
            SELECT insights_extracted FROM gtm_processing_registry 
            WHERE meeting_id = ?
        """, (meeting_id,))
        result = cursor.fetchone()
        
        if result is None or result[0] == 0 or meeting_id in failed_ids:
            processable.append((meeting_dir, meeting_id, meeting_date, b31_file))
    
    if args.list:
        logger.info(f"\nProcessable meetings: {len(processable)}\n")
        for _, meeting_id, meeting_date, b31_file in processable[:20]:
            logger.info(f"  {meeting_id} ({meeting_date}) - {b31_file.name}")
        if len(processable) > 20:
            logger.info(f"  ... and {len(processable)-20} more")
        conn.close()
        return 0
    
    if args.meeting_id:
        # Find specific meeting
        found = None
        for item in processable:
            if args.meeting_id in item[1]:
                found = item
                break
        
        if not found:
            logger.error(f"Meeting {args.meeting_id} not found or not processable")
            conn.close()
            return 1
        
        meeting_dir, meeting_id, meeting_date, b31_file = found
        content, _ = read_b31_content(b31_file)
        
        # Present to Zo for interpretation
        logger.info(f"\n{'='*80}")
        logger.info(f"MEETING: {meeting_id}")
        logger.info(f"DATE: {meeting_date}")
        logger.info(f"FILE: {b31_file}")
        logger.info(f"{'='*80}\n")
        logger.info(f"CONTENT:\n{content}\n")
        logger.info(f"{'='*80}")
        logger.info("\nZo: Please interpret this B31 content and extract GTM insights.")
        logger.info("Return JSON array with fields: title, category, signal_strength,")
        logger.info("insight, why_it_matters, quote, stakeholder_name, stakeholder_company, stakeholder_type")
        logger.info(f"{'='*80}\n")
    
    elif args.batch:
        logger.info(f"Batch mode: {args.batch} meetings")
        for i, (meeting_dir, meeting_id, meeting_date, b31_file) in enumerate(processable[:args.batch]):
            logger.info(f"\n[{i+1}/{args.batch}] {meeting_id}")
            content, _ = read_b31_content(b31_file)
            logger.info(f"File: {b31_file}")
            logger.info(f"Content length: {len(content)} chars")
            logger.info("Ready for interpretation")
    
    else:
        logger.info(f"Total processable: {len(processable)}")
        logger.info("\nUsage:")
        logger.info("  --list              List processable meetings")
        logger.info("  --meeting-id ID     Process specific meeting")
        logger.info("  --batch N           Process N meetings")
    
    conn.close()
    return 0


if __name__ == "__main__":
    exit(main())
