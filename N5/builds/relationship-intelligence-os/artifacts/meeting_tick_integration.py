#!/usr/bin/env python3
"""
Meeting Tick Integration for Relationship Intelligence OS

Patches the meeting ingestion tick command to add post-tick promotion processing.
Provides clean integration without modifying core meeting ingestion files.

Usage:
    # Patch the meeting CLI to include promotion hook
    from meeting_tick_integration import patch_meeting_cli
    patch_meeting_cli()
    
    # Or use as standalone wrapper
    python3 meeting_tick_integration.py tick --auto-process
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone

# Add meeting ingestion to path
MEETING_SKILL_PATH = Path("/home/workspace/Skills/meeting-ingestion/scripts")
sys.path.insert(0, str(MEETING_SKILL_PATH))

# Add build artifacts to path  
BUILD_DIR = Path(__file__).parent
sys.path.insert(0, str(BUILD_DIR))

from post_tick_hook import execute_post_tick_hook

logger = logging.getLogger(__name__)

class MeetingTickWrapper:
    """Wrapper that adds promotion processing to meeting tick pipeline."""
    
    def __init__(self):
        self.original_tick = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for integration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def enhanced_tick(self, args):
        """Enhanced tick command with post-tick promotion processing."""
        
        # Import the original tick function
        try:
            from meeting_cli import cmd_tick
            self.original_tick = cmd_tick
        except ImportError as e:
            logger.error(f"Failed to import meeting_cli: {e}")
            return 1
        
        # Execute original tick
        logger.info("=== Executing original meeting tick ===")
        original_result = self.original_tick(args)
        
        # If original tick failed, don't run promotion
        if original_result != 0:
            logger.warning(f"Original tick failed with code {original_result}, skipping promotion")
            return original_result
        
        # Only run promotion if auto-process was enabled
        if not getattr(args, 'auto_process', False):
            logger.info("Skipping promotion (auto-process not enabled)")
            return original_result
        
        # Execute post-tick promotion hook
        logger.info("=== Executing post-tick promotion processing ===")
        try:
            processed_meetings = self._find_processed_meetings()
            
            if not processed_meetings:
                logger.info("No processed meetings found for promotion")
                return original_result
            
            promotion_result = execute_post_tick_hook(
                [str(m) for m in processed_meetings], 
                dry_run=getattr(args, 'dry_run', False)
            )
            
            self._log_promotion_results(promotion_result)
            
            return original_result
            
        except Exception as e:
            logger.error(f"Post-tick promotion failed: {e}")
            # Don't fail the overall tick - promotion is enhancement
            logger.info("Continuing despite promotion failure")
            return original_result
    
    def _find_processed_meetings(self) -> List[Path]:
        """Find meetings that were just processed and are ready for promotion."""
        
        inbox = Path("/home/workspace/Personal/Meetings/Inbox")
        processed_meetings = []
        
        if not inbox.exists():
            return processed_meetings
        
        # Look for meetings in 'processed' state that don't have promotion completed
        for item in inbox.iterdir():
            if not item.is_dir() or item.name.startswith('.'):
                continue
                
            manifest_path = item / "manifest.json"
            if not manifest_path.exists():
                continue
            
            try:
                manifest = json.loads(manifest_path.read_text())
                
                # Check if meeting is processed but not yet promoted
                if (manifest.get('status') == 'processed' and 
                    not manifest.get('promotion', {}).get('promotion_completed_at')):
                    processed_meetings.append(item)
                    
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not read manifest for {item.name}: {e}")
                continue
        
        # Sort by processing time (most recent first)
        processed_meetings.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return processed_meetings
    
    def _log_promotion_results(self, results: Dict[str, Any]):
        """Log promotion processing results."""
        
        processed = results.get('processed', 0)
        promoted = results.get('promoted', 0) 
        errors = results.get('errors', 0)
        
        logger.info(f"Promotion complete: {processed} meetings processed, {promoted} promoted, {errors} errors")
        
        # Log details for each meeting
        for meeting_result in results.get('meetings', []):
            meeting_id = meeting_result.get('meeting_id', 'unknown')
            status = meeting_result.get('status', 'unknown')
            promoted_events = meeting_result.get('promoted_events', 0)
            
            if status == 'completed':
                logger.info(f"  ✅ {meeting_id}: {promoted_events} events promoted")
            elif status == 'already_processed':
                logger.info(f"  ⏭️  {meeting_id}: already processed recently")
            elif status == 'not_ready':
                logger.info(f"  ⏳ {meeting_id}: not ready for promotion")
            elif status == 'error':
                error = meeting_result.get('error', 'unknown error')
                logger.error(f"  ❌ {meeting_id}: {error}")
            else:
                logger.info(f"  ℹ️  {meeting_id}: {status}")


def patch_meeting_cli():
    """Patch the meeting CLI to include promotion processing."""
    
    try:
        # Import meeting CLI module
        import meeting_cli
        
        # Create wrapper
        wrapper = MeetingTickWrapper()
        
        # Replace the cmd_tick function
        original_tick = meeting_cli.cmd_tick
        meeting_cli.cmd_tick = wrapper.enhanced_tick
        
        logger.info("Successfully patched meeting CLI with promotion processing")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to patch meeting CLI: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error patching meeting CLI: {e}")
        return False


def main():
    """Standalone CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Meeting Tick with Promotion Processing')
    parser.add_argument('command', choices=['tick'], help='Command to execute')
    parser.add_argument('--auto-process', action='store_true', 
                       help='Enable auto-processing (required for promotion)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--batch-size', type=int, default=5, help='Batch size')
    parser.add_argument('--target', type=str, help='Target specific meeting')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    # Set up verbose logging if requested
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    if args.command == 'tick':
        wrapper = MeetingTickWrapper()
        return wrapper.enhanced_tick(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())