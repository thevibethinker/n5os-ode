#!/usr/bin/env python3
"""
Integration Test Suite for Intelligence Block System
Tests end-to-end generation and database logging for Batch 1 blocks.
"""

import sys
import sqlite3
import json
import argparse
import logging
from pathlib import Path

# Add scripts directory to path
INTELLIGENCE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(INTELLIGENCE_DIR / "scripts"))

from block_generator_engine import BlockGeneratorEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")

BLOCKS_DB = INTELLIGENCE_DIR / "blocks.db"
TEST_SAMPLES_DIR = INTELLIGENCE_DIR / "test_samples"

# Batch 1 blocks (priority blocks for testing)
BATCH_1_BLOCKS = [
    'B01',  # DETAILED_RECAP
    'B02',  # COMMITMENTS_CONTEXTUAL
    'B08',  # STAKEHOLDER_INTELLIGENCE
    'B13',  # PLAN_OF_ACTION
    'B26',  # MEETING_METADATA_SUMMARY
    'B31',  # STAKEHOLDER_RESEARCH
    'B40',  # INTERNAL_DECISIONS
    'B50',  # PERSONAL_REFLECTION
]

def get_sample_for_block(block_id):
    """Get a test sample input for the block."""
    conn = sqlite3.connect(BLOCKS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT sample_id, input_snapshot
        FROM quality_samples
        WHERE block_id = ?
        LIMIT 1
    """, (block_id,))
    
    sample = cursor.fetchone()
    conn.close()
    
    if not sample:
        return None
    
    return {
        'sample_id': sample['sample_id'],
        'input_data': json.loads(sample['input_snapshot'])
    }

def test_block_generation(block_id, dry_run=False):
    """Test generation of a single block."""
    logging.info(f"\n{'='*60}")
    logging.info(f"Testing {block_id}")
    logging.info(f"{'='*60}")
    
    # Get sample
    sample = get_sample_for_block(block_id)
    if not sample:
        logging.warning(f"⚠ No sample available for {block_id} - SKIP")
        return {'status': 'skipped', 'reason': 'no_sample'}
    
    if dry_run:
        logging.info(f"✓ Dry-run: Would test {block_id} with sample {sample['sample_id']}")
        return {'status': 'dry_run', 'block_id': block_id}
    
    try:
        # Get transcript path from sample data
        input_data = sample['input_data']
        transcript_path = input_data.get('transcript_path')
        meeting_id = input_data.get('meeting_id', 'test_meeting')
        
        if not transcript_path or not Path(transcript_path).exists():
            logging.warning(f"⚠ Transcript file not found: {transcript_path}")
            return {'status': 'skipped', 'reason': 'transcript_not_found'}
        
        # Initialize engine and generate block
        logging.info(f"Generating {block_id}...")
        engine = BlockGeneratorEngine()
        result = engine.generate_block(
            block_id=block_id,
            transcript_path=transcript_path,
            meeting_id=meeting_id,
            dry_run=False
        )
        
        if not result.get('success'):
            logging.error(f"✗ Generation failed for {block_id}: {result.get('error')}")
            return {'status': 'failed', 'reason': result.get('error', 'unknown')}
        
        output = result.get('output', '')
        
        # Verify output
        if len(output) < 50:
            logging.warning(f"⚠ Output suspiciously short ({len(output)} chars)")
            return {'status': 'warning', 'reason': 'short_output', 'length': len(output)}
        
        logging.info(f"✓ Generated {len(output)} characters")
        
        # Verify database logging
        conn = sqlite3.connect(BLOCKS_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM generation_history
            WHERE block_id = ?
            ORDER BY generated_at DESC
            LIMIT 1
        """, (block_id,))
        
        log_count = cursor.fetchone()[0]
        conn.close()
        
        if log_count > 0:
            logging.info(f"✓ Database logging verified")
        else:
            logging.warning(f"⚠ No database log entry found")
        
        return {
            'status': 'success',
            'block_id': block_id,
            'output_length': len(output),
            'sample_id': sample['sample_id'],
            'logged': log_count > 0
        }
        
    except Exception as e:
        logging.error(f"✗ Exception during {block_id}: {e}", exc_info=True)
        return {'status': 'error', 'reason': str(e)}

def run_integration_tests(block_ids=None, dry_run=False):
    """Run integration tests for specified blocks."""
    if block_ids is None:
        block_ids = BATCH_1_BLOCKS
    
    logging.info(f"\n{'='*60}")
    logging.info(f"INTEGRATION TEST SUITE")
    logging.info(f"{'='*60}")
    logging.info(f"Testing {len(block_ids)} blocks")
    if dry_run:
        logging.info("DRY RUN MODE - No actual generation")
    logging.info(f"{'='*60}\n")
    
    results = []
    for block_id in block_ids:
        result = test_block_generation(block_id, dry_run=dry_run)
        results.append(result)
    
    # Summary
    logging.info(f"\n{'='*60}")
    logging.info("TEST SUMMARY")
    logging.info(f"{'='*60}")
    
    success = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'failed')
    errors = sum(1 for r in results if r['status'] == 'error')
    warnings = sum(1 for r in results if r['status'] == 'warning')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    dry_runs = sum(1 for r in results if r['status'] == 'dry_run')
    
    logging.info(f"Total tests:  {len(results)}")
    logging.info(f"Success:      {success} ✓")
    if failed > 0:
        logging.info(f"Failed:       {failed} ✗")
    if errors > 0:
        logging.info(f"Errors:       {errors} ✗")
    if warnings > 0:
        logging.info(f"Warnings:     {warnings} ⚠")
    if skipped > 0:
        logging.info(f"Skipped:      {skipped} (no samples)")
    if dry_runs > 0:
        logging.info(f"Dry runs:     {dry_runs}")
    
    logging.info(f"{'='*60}\n")
    
    # Detailed failures
    if failed > 0 or errors > 0:
        logging.info("FAILURES:")
        for r in results:
            if r['status'] in ['failed', 'error']:
                logging.info(f"  - {r.get('block_id', 'unknown')}: {r.get('reason', 'unknown')}")
    
    return {
        'total': len(results),
        'success': success,
        'failed': failed,
        'errors': errors,
        'warnings': warnings,
        'skipped': skipped,
        'results': results
    }

def main():
    parser = argparse.ArgumentParser(
        description="Run integration tests for Intelligence blocks"
    )
    parser.add_argument(
        "--block-id",
        help="Test specific block ID (default: all Batch 1 blocks)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all active blocks (not just Batch 1)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate test setup without running generation"
    )
    
    args = parser.parse_args()
    
    try:
        # Determine which blocks to test
        if args.block_id:
            block_ids = [args.block_id.upper()]
        elif args.all:
            # Get all active blocks
            conn = sqlite3.connect(BLOCKS_DB)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT block_id FROM blocks
                WHERE status = 'active' AND block_id != 'B99'
                ORDER BY block_id
            """)
            block_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
        else:
            block_ids = BATCH_1_BLOCKS
        
        # Run tests
        summary = run_integration_tests(block_ids, dry_run=args.dry_run)
        
        # Exit code based on results
        if summary['failed'] > 0 or summary['errors'] > 0:
            return 1
        return 0
        
    except Exception as e:
        logging.error(f"Test suite error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
