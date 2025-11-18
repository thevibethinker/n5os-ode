#!/usr/bin/env python3
"""
CLI script to process pending Fireflies webhooks

Usage:
    python3 process_queue.py --api-key <key>
    python3 process_queue.py --api-key <key> --max 5
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fireflies_webhook.transcript_processor import TranscriptProcessor
from fireflies_webhook.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Process pending Fireflies webhooks")
    parser.add_argument("--api-key", help="Fireflies API key (or set FIREFLIES_API_KEY env var)")
    parser.add_argument("--max", type=int, default=10, help="Max webhooks to process (default: 10)")
    parser.add_argument("--db", help="Database path (default: from Config)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or Config.FIREFLIES_API_KEY
    if not api_key:
        logger.error("API key required: use --api-key or set FIREFLIES_API_KEY env var")
        sys.exit(1)
    
    # Get database path
    db_path = Path(args.db) if args.db else Config.DATABASE_PATH
    
    logger.info(f"Starting webhook processor (max: {args.max}, db: {db_path})")
    
    # Process queue
    processor = TranscriptProcessor(api_key=api_key, db_path=db_path)
    
    try:
        count = processor.process_pending_webhooks(max_process=args.max)
        logger.info(f"✓ Processed {count} webhooks successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"✗ Processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

