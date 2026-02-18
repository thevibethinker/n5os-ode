#!/usr/bin/env python3
"""
Promotion CLI for Relationship Intelligence OS

Command-line interface for running promotion processing on meetings.
Can be used standalone or as part of meeting pipeline integration.

Usage:
    # Process specific meetings
    python3 promotion_cli.py process meeting1 meeting2 --dry-run
    
    # Process all ready meetings in inbox
    python3 promotion_cli.py process-inbox --batch-size 10
    
    # Check promotion status
    python3 promotion_cli.py status meeting1
    
    # Test promotion gate on sample data
    python3 promotion_cli.py test-gate --sample-data samples.json
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Add build artifacts to path
BUILD_DIR = Path(__file__).parent
sys.path.insert(0, str(BUILD_DIR))

from post_tick_hook import PostTickHook, execute_post_tick_hook
from promotion_gate_engine import PromotionGateEngine, ScoringInput

logger = logging.getLogger(__name__)

class PromotionCLI:
    """Command-line interface for promotion processing."""
    
    def __init__(self):
        self.hook = PostTickHook()
        self.engine = PromotionGateEngine()
    
    def cmd_process(self, args) -> int:
        """Process specific meetings through promotion pipeline."""
        
        meetings = [Path(m) for m in args.meetings]
        
        # Validate meeting folders exist
        invalid_meetings = [m for m in meetings if not m.exists() or not m.is_dir()]
        if invalid_meetings:
            print(f"Error: Invalid meeting folders: {[str(m) for m in invalid_meetings]}")
            return 1
        
        try:
            result = execute_post_tick_hook([str(m) for m in meetings], args.dry_run)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                self._print_process_results(result, args.dry_run)
            
            return 0 if result.get('errors', 0) == 0 else 1
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            print(f"Error: {e}")
            return 1
    
    def cmd_process_inbox(self, args) -> int:
        """Process all ready meetings in inbox."""
        
        inbox = Path("/home/workspace/Personal/Meetings/Inbox")
        if not inbox.exists():
            print("Error: Meetings inbox not found")
            return 1
        
        # Find meetings ready for promotion
        ready_meetings = []
        
        for item in inbox.iterdir():
            if not item.is_dir() or item.name.startswith('.'):
                continue
                
            manifest_path = item / "manifest.json"
            if not manifest_path.exists():
                continue
            
            try:
                manifest = json.loads(manifest_path.read_text())
                
                # Check if processed and not yet promoted
                if (manifest.get('status') == 'processed' and 
                    not manifest.get('promotion', {}).get('promotion_completed_at')):
                    ready_meetings.append(item)
                    
            except (json.JSONDecodeError, IOError):
                continue
        
        if not ready_meetings:
            print("No meetings ready for promotion in inbox")
            return 0
        
        # Limit to batch size
        batch_size = getattr(args, 'batch_size', 10)
        batch = ready_meetings[:batch_size]
        
        print(f"Processing {len(batch)}/{len(ready_meetings)} meetings ready for promotion")
        
        try:
            result = execute_post_tick_hook([str(m) for m in batch], args.dry_run)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                self._print_process_results(result, args.dry_run)
            
            return 0 if result.get('errors', 0) == 0 else 1
            
        except Exception as e:
            logger.error(f"Inbox processing failed: {e}")
            print(f"Error: {e}")
            return 1
    
    def cmd_status(self, args) -> int:
        """Check promotion status for meetings."""
        
        for meeting_path_str in args.meetings:
            meeting_path = Path(meeting_path_str)
            
            if not meeting_path.exists() or not meeting_path.is_dir():
                print(f"❌ {meeting_path.name}: Not found or not a directory")
                continue
            
            manifest_path = meeting_path / "manifest.json"
            if not manifest_path.exists():
                print(f"❌ {meeting_path.name}: No manifest.json")
                continue
            
            try:
                manifest = json.loads(manifest_path.read_text())
                self._print_meeting_status(meeting_path.name, manifest, args.verbose)
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"❌ {meeting_path.name}: Cannot read manifest ({e})")
        
        return 0
    
    def cmd_test_gate(self, args) -> int:
        """Test promotion gate with sample data."""
        
        if args.sample_data:
            sample_path = Path(args.sample_data)
            if not sample_path.exists():
                print(f"Error: Sample data file not found: {args.sample_data}")
                return 1
            
            try:
                with open(sample_path) as f:
                    sample_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading sample data: {e}")
                return 1
        else:
            # Generate default sample data
            sample_data = self._generate_sample_data()
        
        # Test each sample
        for i, sample in enumerate(sample_data.get('samples', [])):
            print(f"\n--- Sample {i+1}: {sample.get('name', 'Unnamed')} ---")
            
            try:
                # Create scoring input
                scoring_input = ScoringInput(**sample['input'])
                
                # Process through engine
                result = self.engine.process_candidate(scoring_input, dry_run=True)
                
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    self._print_gate_result(result)
                
            except Exception as e:
                print(f"Error processing sample: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
        
        return 0
    
    def cmd_cleanup(self, args) -> int:
        """Clean up old promotion state and logs."""
        
        from post_tick_hook import HOOK_STATE_DB
        import sqlite3
        from datetime import timedelta
        
        cutoff_days = getattr(args, 'older_than_days', 30)
        cutoff = datetime.now(timezone.utc) - timedelta(days=cutoff_days)
        
        try:
            with sqlite3.connect(HOOK_STATE_DB) as conn:
                # Clean up old completed runs
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM promotion_runs 
                    WHERE status = 'completed' 
                      AND datetime(completed_at) < ?
                """, (cutoff.isoformat(),))
                
                old_runs_count = cursor.fetchone()[0]
                
                if args.dry_run:
                    print(f"Would clean up {old_runs_count} old promotion runs (older than {cutoff_days} days)")
                else:
                    # Delete old runs and associated writes
                    conn.execute("""
                        DELETE FROM promotion_writes 
                        WHERE idempotency_key IN (
                            SELECT idempotency_key FROM promotion_runs
                            WHERE status = 'completed' 
                              AND datetime(completed_at) < ?
                        )
                    """, (cutoff.isoformat(),))
                    
                    conn.execute("""
                        DELETE FROM promotion_runs
                        WHERE status = 'completed' 
                          AND datetime(completed_at) < ?
                    """, (cutoff.isoformat(),))
                    
                    print(f"Cleaned up {old_runs_count} old promotion runs")
            
            return 0
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            print(f"Error: {e}")
            return 1
    
    def _print_process_results(self, results: Dict[str, Any], dry_run: bool):
        """Print processing results in human-readable format."""
        
        mode = "[DRY RUN] " if dry_run else ""
        processed = results.get('processed', 0)
        promoted = results.get('promoted', 0)
        errors = results.get('errors', 0)
        
        print(f"\n{mode}Promotion Processing Complete")
        print(f"{'=' * 40}")
        print(f"Meetings processed: {processed}")
        print(f"Meetings promoted:  {promoted}")
        print(f"Errors:            {errors}")
        
        if results.get('meetings'):
            print("\nMeeting Details:")
            for meeting in results['meetings']:
                meeting_id = meeting.get('meeting_id', 'unknown')
                status = meeting.get('status', 'unknown')
                events = meeting.get('promoted_events', 0)
                
                if status == 'completed':
                    print(f"  ✅ {meeting_id}: {events} events promoted")
                elif status == 'already_processed':
                    print(f"  ⏭️  {meeting_id}: already processed recently")
                elif status == 'not_ready':
                    print(f"  ⏳ {meeting_id}: not ready for promotion")
                elif status == 'error':
                    error = meeting.get('error', 'unknown error')
                    print(f"  ❌ {meeting_id}: {error}")
                elif status == 'dry_run_completed':
                    print(f"  🧪 {meeting_id}: would promote {events} events")
                else:
                    print(f"  ℹ️  {meeting_id}: {status}")
    
    def _print_meeting_status(self, meeting_id: str, manifest: Dict[str, Any], verbose: bool):
        """Print status of a single meeting."""
        
        status = manifest.get('status', 'unknown')
        promotion = manifest.get('promotion', {})
        
        print(f"\n--- {meeting_id} ---")
        print(f"Status: {status}")
        
        if promotion:
            completed_at = promotion.get('promotion_completed_at')
            promoted_events = promotion.get('promoted_events', 0)
            
            if completed_at:
                print(f"✅ Promotion completed: {completed_at}")
                print(f"   Events promoted: {promoted_events}")
                
                if verbose and promotion.get('idempotency_key'):
                    print(f"   Idempotency key: {promotion['idempotency_key']}")
            else:
                print("⏳ Promotion not completed")
        else:
            if status == 'processed':
                print("⏳ Ready for promotion")
            else:
                print(f"⏳ Not ready for promotion (status: {status})")
        
        if verbose:
            participants = manifest.get('participants', [])
            meeting_type = manifest.get('meeting_type', 'unknown')
            date = manifest.get('date', 'unknown')
            
            print(f"   Type: {meeting_type}")
            print(f"   Date: {date}")
            print(f"   Participants: {[p.get('name', 'unknown') for p in participants]}")
    
    def _print_gate_result(self, result: Dict[str, Any]):
        """Print promotion gate result."""
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        score = result.get('score', 0)
        tier = result.get('tier', 'unknown')
        confidence = result.get('confidence', 0)
        
        print(f"Score: {score:.1f}")
        print(f"Tier:  {tier}")
        print(f"Confidence: {confidence:.2f}")
        
        # Print routing decision
        routing = result.get('routing', {})
        routed_to = [k for k, v in routing.items() if v]
        if routed_to:
            print(f"Routed to: {', '.join(routed_to)}")
        
        # Print hard override if applied
        hard_override = result.get('hard_override', {})
        if hard_override.get('applied'):
            reason = hard_override.get('reason', 'unknown')
            print(f"🚨 Hard override: {reason}")
        
        # Print score breakdown in audit mode
        if result.get('audit_report'):
            audit = result['audit_report']
            scoring = audit.get('scoring_details', {})
            breakdown = scoring.get('score_breakdown', {})
            
            print("\nScore Breakdown:")
            for dimension, details in breakdown.items():
                score = details.get('score', 0)
                max_score = details.get('max_possible', 0)
                print(f"  {dimension.replace('_', ' ').title()}: {score:.1f}/{max_score}")
    
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample test data."""
        
        return {
            "samples": [
                {
                    "name": "High-value deliverable commitment",
                    "input": {
                        "candidate_type": "deliverable_record",
                        "candidate_data": {
                            "id": "sample_deliv_001",
                            "deliverable": "Complete strategic partnership proposal by Friday",
                            "status": "committed",
                            "commitment_details": {
                                "deliverable": "Strategic partnership proposal",
                                "owner": "V",
                                "due_date": "2026-02-21"
                            },
                            "confidence": 0.9,
                            "evidence": {
                                "quotes": ["I'll have the partnership proposal ready by Friday"]
                            }
                        },
                        "source_meeting_id": "sample_meeting_001",
                        "conversation_id": "test_conversation"
                    }
                },
                {
                    "name": "Low-confidence relationship delta",
                    "input": {
                        "candidate_type": "relationship_delta",
                        "candidate_data": {
                            "id": "sample_rel_001",
                            "person": "John Smith",
                            "delta_type": "trust_change",
                            "description": "Seemed more receptive to our ideas",
                            "confidence": 0.4,
                            "evidence": {
                                "quotes": ["John seemed more open to the proposal"]
                            }
                        },
                        "source_meeting_id": "sample_meeting_001",
                        "conversation_id": "test_conversation"
                    }
                }
            ]
        }


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(description='Promotion Processing CLI')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='JSON output format')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process specific meetings')
    process_parser.add_argument('meetings', nargs='+', help='Meeting folder paths')
    process_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    # Process inbox command
    inbox_parser = subparsers.add_parser('process-inbox', help='Process all ready meetings in inbox')
    inbox_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    inbox_parser.add_argument('--batch-size', type=int, default=10, help='Maximum meetings to process')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check promotion status')
    status_parser.add_argument('meetings', nargs='+', help='Meeting folder paths')
    
    # Test gate command
    test_parser = subparsers.add_parser('test-gate', help='Test promotion gate')
    test_parser.add_argument('--sample-data', type=str, help='Path to sample data JSON file')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old promotion state')
    cleanup_parser.add_argument('--older-than-days', type=int, default=30, help='Clean up older than N days')
    cleanup_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Set up logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    cli = PromotionCLI()
    
    try:
        if args.command == 'process':
            return cli.cmd_process(args)
        elif args.command == 'process-inbox':
            return cli.cmd_process_inbox(args)
        elif args.command == 'status':
            return cli.cmd_status(args)
        elif args.command == 'test-gate':
            return cli.cmd_test_gate(args)
        elif args.command == 'cleanup':
            return cli.cmd_cleanup(args)
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Command failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())