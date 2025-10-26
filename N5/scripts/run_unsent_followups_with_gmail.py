#!/usr/bin/env python3
"""
Production runner for unsent followups digest with Gmail API integration.
This is how the scheduled task will execute the digest with real Gmail checking.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add N5 scripts to path
sys.path.insert(0, '/home/workspace/N5/scripts')

from n5_unsent_followups_digest import UnsentFollowupsDigest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


def main(use_app_gmail_fn):
    """
    Run the digest with Gmail integration.
    
    Args:
        use_app_gmail_fn: The actual use_app_gmail function from Zo tools
    
    Returns:
        tuple: (digest_content, output_path)
    """
    logger.info("=== N5 Unsent Follow-Ups Digest with Gmail Integration ===")
    
    # Create digest generator with Gmail API
    digest_gen = UnsentFollowupsDigest(
        dry_run=False,
        debug=False,
        use_app_gmail_fn=use_app_gmail_fn
    )
    
    # Scan meetings
    meetings = digest_gen.scan_meetings_with_followups()
    
    if not meetings:
        logger.info("✓ No meetings with follow-ups found")
        return None, None
    
    # Check Gmail for sent emails
    unsent = digest_gen.check_gmail_sent(meetings)
    
    # Generate and save digest
    digest_content = digest_gen.generate_digest(unsent)
    
    if digest_content:
        output_path = digest_gen.save_digest(digest_content)
        logger.info(f"✓ Complete: {len(unsent)} unsent follow-ups")
        return digest_content, output_path
    else:
        logger.info("✓ All follow-ups have been sent")
        return None, None


if __name__ == "__main__":
    # This script is designed to be imported and called with use_app_gmail
    # For standalone testing, it will run without Gmail integration
    logger.warning("Running without Gmail integration (use from scheduled task for full functionality)")
    main(use_app_gmail_fn=None)
