#!/usr/bin/env python3
"""
GTM B31 Processor - Processes unprocessed B31 files into GTM intelligence database
Runs as scheduled task every 10 minutes, processes 1 meeting per run.
"""

import sqlite3
import re
import logging
from pathlib import Path
from datetime import datetime
import sys
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
PATHS_YAML = WORKSPACE / "N5/prefs/paths/knowledge_paths.yaml"


def load_db_path() -> str:
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
        return str(WORKSPACE / db_rel)
    except Exception as exc:
        logger.error("Failed to resolve GTM DB from %s: %s", PATHS_YAML, exc)
        sys.exit(1)


DB_PATH = load_db_path()
MEETINGS_PER_RUN = 1  # Process 1 meeting per 10-minute cycle

def extract_meeting_info(meeting_dir):
    """Extract meeting ID and date from directory name."""
    dir_name = meeting_dir.name
    parts = dir_name.split('_', 1)
    if len(parts) >= 1 and re.match(r'\d{4}-\d{2}-\d{2}', parts[0]):
        return dir_name, parts[0]
    return dir_name, datetime.now().strftime('%Y-%m-%d')

def parse_b31_format_new(content, meeting_id, meeting_date, b31_path):
    """Parse new format: ## Insight N:"""
    insights = []
    blocks = re.split(r'\n## Insight \d+:', content)
    
    for block in blocks[1:]:
        if len(block.strip()) < 50:
            continue
            
        title_match = re.search(r'^(.+?)(?:\n|$)', block)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        
        category_match = re.search(r'\*\*Category\*\*:\s*(.+)', block)
        category = category_match.group(1).strip() if category_match else "Uncategorized"
        
        signal_match = re.search(r'●+', block)
        signal_strength = len(signal_match.group(0)) if signal_match else 1
        
        insight_match = re.search(r'\*\*What We Learned\*\*:\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
        insight = insight_match.group(1).strip() if insight_match else ""
        
        evidence_match = re.search(r'\*\*Evidence\*\*:\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
        evidence = evidence_match.group(1).strip() if evidence_match else ""
        
        why_match = re.search(r'\*\*Business Implications\*\*:\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
        why_it_matters = why_match.group(1).strip() if why_match else ""
        
        stakeholder_match = re.search(r'\*\*Source\*\*:\s*(.+?)(?:\(|$)', block)
        stakeholder_name = stakeholder_match.group(1).strip() if stakeholder_match else "Unknown"
        
        role_match = re.search(r'\*\*Source\*\*:.+?\((.+?)\)', block)
        role = role_match.group(1).strip() if role_match else None
        
        quote_match = re.search(r'"([^"]+)"', evidence)
        quote = quote_match.group(1) if quote_match else None
        
        source_type_match = re.search(r'PRIMARY|SECONDARY|TERTIARY', block)
        source_type = source_type_match.group(0) if source_type_match else "UNKNOWN"
        confidence = "HIGH" if source_type == "PRIMARY" else "MEDIUM" if source_type == "SECONDARY" else "LOW"
        
        insights.append({
            'title': title, 'insight': insight, 'why_it_matters': why_it_matters,
            'quote': quote, 'category': category, 'signal_strength': signal_strength,
            'confidence_level': confidence, 'stakeholder_name': stakeholder_name,
            'stakeholder_role': role, 'stakeholder_type': None, 'stakeholder_company': None,
            'meeting_id': meeting_id, 'meeting_date': meeting_date, 'source_b31_path': str(b31_path)
        })
    
    return insights

def parse_b31_format_old(content, meeting_id, meeting_date, b31_path):
    """Parse old format: **N. Title**"""
    insights = []
    blocks = re.split(r'\n\*\*\d+\.', content)
    
    for block in blocks[1:]:
        if len(block.strip()) < 50:
            continue
            
        title_match = re.search(r'^(.+?)\*\*', block)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        
        category_match = re.search(r'\*\*Category\*\*:\s*(.+)', block)
        category = category_match.group(1).strip() if category_match else "Uncategorized"
        
        signal_match = re.search(r'Signal [Ss]trength.*?(\d+)', block)
        signal_strength = int(signal_match.group(1)) if signal_match else 1
        
        insight_match = re.search(r'\*\*What [Ww]e [Ll]earned\*\*:\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
        insight = insight_match.group(1).strip() if insight_match else ""
        
        evidence_match = re.search(r'\*\*Evidence\*\*:\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
        evidence = evidence_match.group(1).strip() if evidence_match else ""
        
        why_match = re.search(r'\*\*(?:Why [Ii]t [Mm]atters|Business Implications)\*\*:\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
        why_it_matters = why_match.group(1).strip() if why_match else ""
        
        stakeholder_match = re.search(r'\*\*(?:Source|Stakeholder)\*\*:\s*(.+?)(?:\(|$)', block)
        stakeholder_name = stakeholder_match.group(1).strip() if stakeholder_match else "Unknown"
        
        role_match = re.search(r'\(([^)]+)\)', block)
        role = role_match.group(1).strip() if role_match else None
        
        quote_match = re.search(r'"([^"]+)"', evidence)
        quote = quote_match.group(1) if quote_match else None
        
        source_type_match = re.search(r'PRIMARY|SECONDARY', block)
        source_type = source_type_match.group(0) if source_type_match else "UNKNOWN"
        confidence = "HIGH" if source_type == "PRIMARY" else "MEDIUM" if source_type == "SECONDARY" else "LOW"
        
        insights.append({
            'title': title, 'insight': insight, 'why_it_matters': why_it_matters,
            'quote': quote, 'category': category, 'signal_strength': signal_strength,
            'confidence_level': confidence, 'stakeholder_name': stakeholder_name,
            'stakeholder_role': role, 'stakeholder_type': None, 'stakeholder_company': None,
            'meeting_id': meeting_id, 'meeting_date': meeting_date, 'source_b31_path': str(b31_path)
        })
    
    return insights

def parse_b31_format_3(content, meeting_id, meeting_date, b31_path):
    """Parse format 3: ### N. **Title**"""
    insights = []
    blocks = re.split(r'\n### \d+\.', content)
    
    for block in blocks[1:]:
        if len(block.strip()) < 50:
            continue
            
        title_match = re.search(r'^\s*\*\*(.+?)\*\*', block)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        
        signal_match = re.search(r'●+', title)
        signal_strength = len(signal_match.group(0)) if signal_match else 3
        title = re.sub(r'\s*●+\s*', '', title)
        
        insight_match = re.search(r'\*\*\n\n(.+?)(?=\n-|\n\*\*|$)', block, re.DOTALL)
        insight = insight_match.group(1).strip() if insight_match else ""
        
        evidence_bullets = re.findall(r'^-\s*(.+)$', block, re.MULTILINE)
        evidence = " ".join(evidence_bullets) if evidence_bullets else ""
        
        action_match = re.search(r'\*\*Action\*\*:\s*(.+?)(?=\n|$)', block)
        why_it_matters = action_match.group(1).strip() if action_match else ""
        
        quote_match = re.search(r'"([^"]+)"', block)
        quote = quote_match.group(1) if quote_match else None
        
        insights.append({
            'title': title, 'insight': insight, 'why_it_matters': why_it_matters,
            'quote': quote, 'category': 'Uncategorized', 'signal_strength': signal_strength,
            'confidence_level': 'MEDIUM', 'stakeholder_name': 'Unknown',
            'stakeholder_role': None, 'stakeholder_type': None, 'stakeholder_company': None,
            'meeting_id': meeting_id, 'meeting_date': meeting_date, 'source_b31_path': str(b31_path)
        })
    
    return insights

def parse_b31_file(b31_path, meeting_id, meeting_date):
    """Parse B31 file using appropriate format parser."""
    try:
        content = b31_path.read_text()
        
        if '## Insight' in content:
            insights = parse_b31_format_new(content, meeting_id, meeting_date, b31_path)
        elif '### 1. **' in content or '### 2. **' in content:
            insights = parse_b31_format_3(content, meeting_id, meeting_date, b31_path)
        else:
            insights = parse_b31_format_old(content, meeting_id, meeting_date, b31_path)
        
        return insights
    except Exception as e:
        logger.error(f"Error parsing {b31_path}: {e}")
        return []

def process_meeting(meeting_id, b31_path, conn):
    """Process a single meeting's B31 file."""
    meeting_path = Path(b31_path)
    meeting_id_from_path, meeting_date = extract_meeting_info(meeting_path.parent)
    
    logger.info(f"Processing: {meeting_id}")
    
    insights = parse_b31_file(meeting_path, meeting_id, meeting_date)
    
    if not insights:
        logger.info(f"  No insights extracted from {meeting_id}")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE gtm_processing_registry 
            SET insights_extracted = 0,
                extraction_version = '3.0-scheduled',
                processed_at = CURRENT_TIMESTAMP
            WHERE meeting_id = ?
        """, (meeting_id,))
        conn.commit()
        return 0
    
    cursor = conn.cursor()
    inserted = 0
    
    for insight in insights:
        try:
            cursor.execute("""
                INSERT INTO gtm_insights (
                    meeting_id, meeting_date, source_b31_path,
                    stakeholder_name, stakeholder_role, stakeholder_type, stakeholder_company,
                    category, signal_strength,
                    title, insight, why_it_matters, quote,
                    confidence_level, processed_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight['meeting_id'], insight['meeting_date'], insight['source_b31_path'],
                insight['stakeholder_name'], insight['stakeholder_role'], 
                insight['stakeholder_type'], insight['stakeholder_company'],
                insight['category'], insight['signal_strength'],
                insight['title'], insight['insight'], insight['why_it_matters'], 
                insight['quote'], insight['confidence_level'], 
                'gtm_b31_processor.py (scheduled)'
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            pass
    
    cursor.execute("""
        UPDATE gtm_processing_registry 
        SET insights_extracted = ?,
            extraction_version = '3.0-scheduled',
            processed_at = CURRENT_TIMESTAMP
        WHERE meeting_id = ?
    """, (inserted, meeting_id))
    
    conn.commit()
    logger.info(f"  ✓ Extracted {inserted} insights from {meeting_id}")
    return inserted

def main():
    logger.info("=" * 60)
    logger.info("GTM B31 Processor - Scheduled Run")
    logger.info("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT meeting_id, b31_path 
        FROM gtm_processing_registry 
        WHERE processed_at IS NULL
        ORDER BY meeting_id DESC
        LIMIT ?
    """, (MEETINGS_PER_RUN,))
    
    unprocessed = cursor.fetchall()
    
    if not unprocessed:
        logger.info("✓ No unprocessed meetings found - queue is empty!")
        
        cursor.execute("SELECT COUNT(*) FROM gtm_processing_registry WHERE processed_at IS NOT NULL")
        processed_count = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(insights_extracted) FROM gtm_processing_registry")
        total_insights = cursor.fetchone()[0] or 0
        
        logger.info(f"📊 Final Stats: {processed_count} meetings processed, {total_insights} total insights")
        conn.close()
        return 0
    
    cursor.execute("SELECT COUNT(*) FROM gtm_processing_registry WHERE processed_at IS NULL")
    remaining = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM gtm_processing_registry WHERE processed_at IS NOT NULL")
    processed = cursor.fetchone()[0]
    
    logger.info(f"📊 Queue Status: {remaining} unprocessed, {processed} completed")
    logger.info(f"Processing {len(unprocessed)} meeting(s) this cycle...")
    logger.info("")
    
    total_insights = 0
    for meeting_id, b31_path in unprocessed:
        insights_count = process_meeting(meeting_id, b31_path, conn)
        total_insights += insights_count
    
    conn.close()
    
    logger.info("")
    logger.info(f"✓ Cycle complete: Extracted {total_insights} insights from {len(unprocessed)} meeting(s)")
    logger.info(f"📊 Remaining in queue: {remaining - len(unprocessed)}")
    logger.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

