#!/usr/bin/env python3
"""
Post-processing hook for newly completed meetings.
Runs standardization after B26/B28 generation.

Can be called from ANY processing path.
"""

import logging
import sys
from pathlib import Path

# Import standardization
sys.path.insert(0, str(Path(__file__).parent))
from standardize_meeting import standardize_meeting

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


def post_process_meeting(meeting_id: str) -> bool:
    """
    Run post-processing on a completed meeting.
    
    Currently just runs standardization, but can be extended.
    
    Args:
        meeting_id: Meeting folder name
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Post-processing: {meeting_id}")
    
    # Run standardization
    try:
        success = standardize_meeting(meeting_id)
        if success:
            logger.info(f"✓ Post-processing complete: {meeting_id}")
        else:
            logger.warning(f"⚠ Standardization skipped/failed: {meeting_id}")
        return success
    except Exception as e:
        logger.error(f"❌ Post-processing error for {meeting_id}: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_process_meeting.py <meeting_id>")
        sys.exit(1)
    
    meeting_id = sys.argv[1]
    success = post_process_meeting(meeting_id)
    sys.exit(0 if success else 1)
