#!/usr/bin/env python3
"""
Backfill historical conversations into registry

Scans /home/.z/workspaces for conversations and registers them.
Only processes conversations with SESSION_STATE.md files.

Usage:
    backfill_conversations.py --dry-run       # Preview
    backfill_conversations.py --limit 10      # Process 10
    backfill_conversations.py                 # Process all

Principles: P7 (Dry-Run), P19 (Error Handling), P18 (Verify State)
"""

import argparse
import logging
import re
from pathlib import Path
from typing import Dict, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent))
from conversation_registry import ConversationRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACES_ROOT = Path("/home/.z/workspaces")


def parse_session_state(state_file: Path) -> Optional[Dict]:
    """Extract key fields from SESSION_STATE.md"""
    try:
        content = state_file.read_text()
        
        data = {
            "type": "discussion",  # default
            "status": "active",
            "focus": None,
            "objective": None,
            "tags": []
        }
        
        # Extract type
        type_match = re.search(r'\*\*Primary Type:\*\*\s*(\w+)', content)
        if type_match:
            data["type"] = type_match.group(1).lower()
        
        # Extract focus
        focus_match = re.search(r'\*\*Focus:\*\*\s*(.+)', content)
        if focus_match:
            data["focus"] = focus_match.group(1).strip()
        
        # Extract objective/goal
        goal_match = re.search(r'\*\*Goal:\*\*\s*(.+)', content)
        if goal_match:
            data["objective"] = goal_match.group(1).strip()
        
        # Extract status
        status_match = re.search(r'\*\*Status:\*\*\s*(\w+)', content)
        if status_match:
            data["status"] = status_match.group(1).lower()
        
        return data
        
    except Exception as e:
        logger.debug(f"Failed to parse {state_file}: {e}")
        return None


def backfill_conversation(convo_id: str, workspace: Path, registry: ConversationRegistry, dry_run: bool = False) -> bool:
    """Backfill a single conversation"""
    try:
        # Check if already exists
        existing = registry.get(convo_id)
        if existing:
            logger.debug(f"  Skip {convo_id} - already in registry")
            return False
        
        # Look for SESSION_STATE.md
        state_file = workspace / "SESSION_STATE.md"
        if not state_file.exists():
            logger.debug(f"  Skip {convo_id} - no SESSION_STATE.md")
            return False
        
        # Parse state
        state_data = parse_session_state(state_file)
        if not state_data:
            logger.debug(f"  Skip {convo_id} - failed to parse SESSION_STATE.md")
            return False
        
        if dry_run:
            logger.info(f"  [DRY RUN] Would add: {convo_id}")
            logger.info(f"    Type: {state_data['type']}, Focus: {state_data.get('focus', 'N/A')[:50]}")
            return True
        
        # Create in registry
        success = registry.create(
            convo_id,
            type=state_data["type"],
            status=state_data["status"],
            focus=state_data.get("focus"),
            objective=state_data.get("objective"),
            workspace_path=str(workspace),
            state_file_path=str(state_file)
        )
        
        if success:
            # Try to enrich with title
            try:
                registry.enrich_conversation(convo_id, str(workspace))
            except Exception as e:
                logger.debug(f"Title generation failed for {convo_id}: {e}")
            
            logger.info(f"  ✓ Added: {convo_id}")
            return True
        else:
            logger.warning(f"  ✗ Failed to add: {convo_id}")
            return False
            
    except Exception as e:
        logger.error(f"  Error processing {convo_id}: {e}")
        return False


def main(limit: Optional[int] = None, dry_run: bool = False) -> int:
    """Main backfill process"""
    try:
        logger.info(f"Scanning {WORKSPACES_ROOT} for conversations...")
        logger.info(f"Dry run: {dry_run}")
        
        registry = ConversationRegistry()
        
        # Get all conversation directories
        convo_dirs = sorted([d for d in WORKSPACES_ROOT.iterdir() 
                            if d.is_dir() and d.name.startswith("con_")])
        
        total = len(convo_dirs)
        logger.info(f"Found {total} conversation workspaces")
        
        if limit:
            convo_dirs = convo_dirs[:limit]
            logger.info(f"Processing {len(convo_dirs)} (limit={limit})")
        
        # Process each
        added = 0
        skipped = 0
        errors = 0
        
        for i, convo_dir in enumerate(convo_dirs, 1):
            convo_id = convo_dir.name
            
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{len(convo_dirs)} ({added} added, {skipped} skipped, {errors} errors)")
            
            try:
                success = backfill_conversation(convo_id, convo_dir, registry, dry_run=dry_run)
                if success:
                    added += 1
                else:
                    skipped += 1
            except Exception as e:
                logger.error(f"Error processing {convo_id}: {e}")
                errors += 1
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info(f"{'DRY RUN ' if dry_run else ''}Backfill complete")
        logger.info(f"  Total scanned: {len(convo_dirs)}")
        logger.info(f"  Added: {added}")
        logger.info(f"  Skipped: {skipped}")
        logger.info(f"  Errors: {errors}")
        logger.info("="*70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Backfill failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill historical conversations")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    parser.add_argument("--limit", type=int, help="Max conversations to process")
    
    args = parser.parse_args()
    
    exit(main(limit=args.limit, dry_run=args.dry_run))
