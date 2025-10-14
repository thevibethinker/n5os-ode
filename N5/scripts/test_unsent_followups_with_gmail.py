#!/usr/bin/env python3
"""
Test wrapper for unsent followups digest with Gmail API integration.
This simulates how the scheduled task will inject the Gmail API function.
"""

import sys
import logging
from pathlib import Path

# Add N5 scripts to path
sys.path.insert(0, '/home/workspace/N5/scripts')

from n5_unsent_followups_digest import UnsentFollowupsDigest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


def mock_gmail_api(tool_name: str, configured_props: dict):
    """
    Mock Gmail API for testing.
    In production, this will be the actual use_app_gmail function.
    """
    logger.info(f"[MOCK] Gmail API call: {tool_name}")
    logger.info(f"[MOCK] Query: {configured_props.get('q', 'N/A')}")
    
    # Return empty result (no matches found)
    return {
        'messages': []
    }


def main():
    """Test the digest with Gmail integration."""
    logger.info("=== Testing Unsent Follow-Ups Digest with Gmail Integration ===")
    
    # Create digest generator with Gmail API mock
    digest_gen = UnsentFollowupsDigest(
        dry_run=True,
        debug=True,
        use_app_gmail_fn=mock_gmail_api
    )
    
    # Scan meetings
    meetings = digest_gen.scan_meetings_with_followups()
    
    if not meetings:
        logger.info("✓ No meetings with follow-ups found")
        return 0
    
    # Check Gmail
    unsent = digest_gen.check_gmail_sent(meetings)
    
    # Generate digest
    digest_content = digest_gen.generate_digest(unsent)
    
    if digest_content:
        logger.info("\n=== DIGEST PREVIEW ===\n")
        print(digest_content)
        logger.info(f"✓ Found {len(unsent)} unsent follow-ups")
    else:
        logger.info("✓ All follow-ups have been sent")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
