#!/usr/bin/env python3
"""
GTM Intelligence Database - LLM-Based Backfill
Extracts insights from B31 files using LLM for flexible parsing
"""
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
import json
import yaml
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
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

def extract_insights_from_b31(b31_path: Path, meeting_id: str, meeting_date: str) -> str:
    """
    Returns a prompt for LLM to extract structured insights from B31.
    LLM will output JSON array of insights.
    """
    content = b31_path.read_text()
    
    prompt = f"""Extract GTM intelligence insights from this B31 file into structured JSON.

MEETING CONTEXT:
- Meeting ID: {meeting_id}
- Date: {meeting_date}
- Source: {b31_path}

B31 CONTENT:
{content}

OUTPUT REQUIREMENTS:
Return a JSON array of insights. Each insight object must have:
{{
  "title": "Insight title (concise)",
  "category": "Category name",
  "evidence": "Direct quotes and specific examples",
  "why_it_matters": "Strategic implications for Careerspan",
  "signal_strength": 1-5 (integer),
  "confidence_level": "HIGH/MEDIUM/LOW",
  "confidence_reasoning": "Brief explanation",
  "stakeholder_name": "Extract from B31 header/context",
  "stakeholder_role": "Extract from B31 header/context"
}}

CATEGORY OPTIONS:
- GTM & Distribution
- Recruiting Agency Pain Points
- Hiring Manager Pain Points
- Job Seeker Pain Points
- Founder Pain Points
- Consultant Pain Points
- Product Strategy & Features
- Competitive Landscape
- Market Dynamics
- Pricing & Business Model
- Fundraising & Investor Relations

CRITICAL: Output ONLY valid JSON array, no markdown, no explanation.
"""
    return prompt

def process_meeting_with_llm(conn: sqlite3.Connection, meeting_dir: Path) -> int:
    """Process one meeting using LLM extraction"""
    meeting_id = meeting_dir.name
    b31_path = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
    
    if not b31_path.exists():
        return 0
    
    # Check if already processed
    cursor = conn.cursor()
    cursor.execute(
        "SELECT insights_extracted FROM gtm_processing_registry WHERE meeting_id = ?",
        (meeting_id,)
    )
    existing = cursor.fetchone()
    if existing and existing[0] > 0:
        logger.info(f"⏭️  {meeting_id}: Already processed ({existing[0]} insights)")
        return 0
    
    # Extract meeting date from folder name
    meeting_date = meeting_id[:10]  # First 10 chars: YYYY-MM-DD
    
    # Get LLM extraction prompt
    prompt = extract_insights_from_b31(b31_path, meeting_id, meeting_date)
    
    # Save prompt to temp file for manual processing
    prompt_file = WORKSPACE / f".z/workspaces/gtm_backfill/{meeting_id}_extraction_prompt.txt"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(prompt)
    
    logger.info(f"📝 {meeting_id}: Extraction prompt ready")
    logger.info(f"   → {prompt_file}")
    
    return 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description="GTM backfill using LLM extraction")
    parser.add_argument("--meeting-id", help="Process specific meeting")
    parser.add_argument("--batch", action="store_true", help="Generate all extraction prompts")
    args = parser.parse_args()
    
    conn = sqlite3.connect(DB_PATH)
    
    # Find all meetings with B31 files
    meetings = []
    for meeting_dir in sorted(MEETINGS_DIR.iterdir()):
        if meeting_dir.is_dir() and "external" in meeting_dir.name:
            b31 = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
            if b31.exists():
                if args.meeting_id:
                    if meeting_dir.name == args.meeting_id:
                        meetings.append(meeting_dir)
                else:
                    meetings.append(meeting_dir)
    
    logger.info(f"Found {len(meetings)} meetings with B31 files")
    
    if args.batch:
        logger.info("Generating extraction prompts for batch processing...")
        for meeting_dir in meetings:
            process_meeting_with_llm(conn, meeting_dir)
        
        logger.info(f"\n✓ Generated {len(meetings)} extraction prompts")
        logger.info(f"✓ Location: {WORKSPACE}/.z/workspaces/gtm_backfill/")
        logger.info("\nNEXT STEP: Process each prompt with LLM, save JSON responses, then run import")
    else:
        logger.info("Use --batch to generate all extraction prompts")
    
    conn.close()
    return 0

if __name__ == "__main__":
    exit(main())

