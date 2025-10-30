#!/usr/bin/env python3
"""
Daily GTM Meeting Aggregation
Scans for unprocessed GTM meetings with B31 files and appends to aggregated_insights_GTM.md
"""
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Paths
MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
REGISTRY_PATH = Path("/home/workspace/Knowledge/market_intelligence/.processed_meetings.json")
GTM_DOC_PATH = Path("/home/workspace/Knowledge/market_intelligence/aggregated_insights_GTM.md")
TRANSCRIPTS_DIR = Path("/home/workspace/N5/inbox/transcripts")

# GTM meeting filters
EXCLUDED_PATTERNS = ["internal", "team", "vendor", "equals", "faze-clan", "second-shift"]
GTM_REQUIRED_PATTERN = "external"

def load_registry():
    """Load processed meetings registry"""
    try:
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load registry: {e}")
        return None

def save_registry(data):
    """Save updated registry"""
    try:
        with open(REGISTRY_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("✓ Registry updated")
    except Exception as e:
        logger.error(f"Failed to save registry: {e}")

def is_gtm_meeting(meeting_dir: Path) -> bool:
    """Check if meeting qualifies as GTM"""
    meeting_id = meeting_dir.name
    
    # Must be external
    if GTM_REQUIRED_PATTERN not in meeting_id.lower():
        return False
    
    # Exclude internal/vendor meetings
    if any(pattern in meeting_id.lower() for pattern in EXCLUDED_PATTERNS):
        return False
    
    # Must have B31 file
    b31_file = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
    if not b31_file.exists():
        return False
    
    return True

def find_unprocessed_meetings():
    """Scan for GTM meetings not yet in registry"""
    registry = load_registry()
    if not registry:
        return []
    
    processed_ids = {m['meeting_id'] for m in registry['GTM']['meetings']}
    
    unprocessed = []
    for meeting_dir in MEETINGS_DIR.iterdir():
        if not meeting_dir.is_dir():
            continue
        
        meeting_id = meeting_dir.name
        if meeting_id in processed_ids:
            continue
        
        if is_gtm_meeting(meeting_dir):
            unprocessed.append(meeting_id)
    
    return sorted(unprocessed, reverse=True)  # LIFO: most recent first

def main():
    """Main execution"""
    try:
        logger.info("Starting daily GTM aggregation scan...")
        
        unprocessed = find_unprocessed_meetings()
        
        if not unprocessed:
            logger.info("✓ No unprocessed GTM meetings found")
            return 0
        
        logger.info(f"Found {len(unprocessed)} unprocessed GTM meetings:")
        for meeting_id in unprocessed[:10]:  # Log first 10
            logger.info(f"  - {meeting_id}")
        
        if len(unprocessed) > 10:
            logger.info(f"  ... and {len(unprocessed) - 10} more")
        
        logger.info("\n✓ Scan complete. Manual processing required for LLM-driven insights extraction.")
        logger.info("Next step: Process meetings via scheduled LLM task")
        
        return 0
        
    except Exception as e:
        logger.error(f"Aggregation failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
