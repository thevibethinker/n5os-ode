#!/usr/bin/env python3
"""
Conversation Backfill Script
Scan all conversation workspaces and register missing conversations in database.

Principles: P1 (Human-Readable), P7 (Dry-Run), P15 (Complete), P19 (Error Handling)

Usage:
    python3 conversation_backfill.py --dry-run
    python3 conversation_backfill.py --execute
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from conversation_registry import ConversationRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONVERSATION_WORKSPACES = Path("/home/.z/workspaces")


class ConversationBackfiller:
    """Backfill conversations.db from existing workspace directories."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.registry = ConversationRegistry()
        self.stats = {
            "total_workspaces": 0,
            "already_registered": 0,
            "registered": 0,
            "with_parent": 0,
            "errors": 0,
            "skipped": 0
        }
    
    def parse_session_state(self, path: Path) -> Optional[Dict]:
        """Extract metadata from SESSION_STATE.md."""
        try:
            if not path.exists():
                return None
            
            content = path.read_text()
            
            # Extract fields
            metadata = {
                "type": "discussion",  # default
                "status": "active",
                "mode": "",
                "focus": None,
                "objective": None,
                "parent_id": None,
                "created_at": None
            }
            
            # Type
            type_match = re.search(r'\*\*Primary Type:\*\*\s*(\w+)', content)
            if type_match:
                metadata["type"] = type_match.group(1).strip()
            
            # Status
            status_match = re.search(r'\*\*Status:\*\*\s*(\w+)', content)
            if status_match:
                metadata["status"] = status_match.group(1).strip()
            
            # Mode
            mode_match = re.search(r'\*\*Mode:\*\*\s*([^\n]+)', content)
            if mode_match:
                mode = mode_match.group(1).strip()
                if mode and not mode.startswith('*'):
                    metadata["mode"] = mode
            
            # Focus
            focus_match = re.search(r'\*\*Focus:\*\*\s*([^\n]+)', content)
            if focus_match:
                focus = focus_match.group(1).strip().strip('*')
                if focus and not focus.startswith('What is'):
                    metadata["focus"] = focus
            
            # Objective (Goal)
            obj_match = re.search(r'\*\*Goal:\*\*\s*([^\n]+)', content)
            if obj_match:
                objective = obj_match.group(1).strip().strip('*')
                if objective and not objective.startswith('What are'):
                    metadata["objective"] = objective
            
            # Parent
            parent_match = re.search(r'\*\*Parent Conversation:\*\*\s*([^\s\n]+)', content)
            if parent_match:
                parent_id = parent_match.group(1).strip()
                # Clean up
                parent_id = parent_id.split('(')[0].strip()  # Remove (Orchestrator) suffix
                if parent_id.startswith('con_'):
                    metadata["parent_id"] = parent_id
            
            # Created timestamp
            started_match = re.search(r'\*\*Started:\*\*\s*([^\n]+)', content)
            if started_match:
                timestamp_str = started_match.group(1).strip()
                try:
                    # Parse various formats
                    if 'ET' in timestamp_str or 'EST' in timestamp_str:
                        # 2025-10-26 22:26 ET
                        dt = datetime.strptime(timestamp_str.split(' ET')[0].split(' EST')[0].strip(), '%Y-%m-%d %H:%M')
                        metadata["created_at"] = dt.isoformat() + 'Z'
                except Exception as e:
                    logger.debug(f"Could not parse timestamp: {timestamp_str}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to parse {path}: {e}")
            return None
    
    def extract_convo_id(self, workspace_path: Path) -> Optional[str]:
        """Extract conversation ID from workspace path."""
        convo_id = workspace_path.name
        if convo_id.startswith('con_') or convo_id == 'WORKER_TEST':
            return convo_id
        return None
    
    def process_workspace(self, workspace_path: Path) -> bool:
        """Process a single workspace directory."""
        try:
            convo_id = self.extract_convo_id(workspace_path)
            if not convo_id:
                logger.debug(f"Skipping non-conversation workspace: {workspace_path.name}")
                self.stats["skipped"] += 1
                return False
            
            self.stats["total_workspaces"] += 1
            
            # Check if already registered
            with self.registry._connect() as conn:
                existing = conn.execute(
                    "SELECT id, parent_id FROM conversations WHERE id = ?",
                    (convo_id,)
                ).fetchone()
            
            session_state_path = workspace_path / "SESSION_STATE.md"
            metadata = self.parse_session_state(session_state_path)
            
            if existing:
                # Update if has parent but DB doesn't
                if metadata and metadata["parent_id"] and not existing["parent_id"]:
                    if not self.dry_run:
                        self.registry.update(convo_id, parent_id=metadata["parent_id"], mode="worker")
                        logger.info(f"✓ Updated {convo_id} with parent {metadata['parent_id']}")
                    else:
                        logger.info(f"[DRY RUN] Would update {convo_id} with parent {metadata['parent_id']}")
                    self.stats["with_parent"] += 1
                else:
                    logger.debug(f"Already registered: {convo_id}")
                    self.stats["already_registered"] += 1
                return True
            
            # Register new conversation
            if not metadata:
                logger.warning(f"No SESSION_STATE.md for {convo_id}, using defaults")
                metadata = {
                    "type": "discussion",
                    "status": "active",
                    "mode": "",
                    "focus": None,
                    "objective": None,
                    "parent_id": None,
                    "created_at": None
                }
            
            if not self.dry_run:
                self.registry.create(
                    convo_id=convo_id,
                    type=metadata["type"],
                    status=metadata["status"],
                    mode=metadata.get("mode", ""),
                    parent_id=metadata.get("parent_id"),
                    focus=metadata.get("focus"),
                    objective=metadata.get("objective"),
                    workspace_path=str(workspace_path),
                    state_file_path=str(session_state_path) if session_state_path.exists() else None
                )
                logger.info(f"✓ Registered {convo_id} (type={metadata['type']}, parent={metadata.get('parent_id', 'None')})")
            else:
                logger.info(f"[DRY RUN] Would register {convo_id} (type={metadata['type']}, parent={metadata.get('parent_id', 'None')})")
            
            self.stats["registered"] += 1
            if metadata.get("parent_id"):
                self.stats["with_parent"] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {workspace_path}: {e}", exc_info=True)
            self.stats["errors"] += 1
            return False
    
    def scan_all(self) -> bool:
        """Scan all conversation workspaces."""
        try:
            if not CONVERSATION_WORKSPACES.exists():
                logger.error(f"Workspaces directory not found: {CONVERSATION_WORKSPACES}")
                return False
            
            logger.info(f"Scanning {CONVERSATION_WORKSPACES}")
            
            for workspace in sorted(CONVERSATION_WORKSPACES.iterdir()):
                if not workspace.is_dir():
                    continue
                self.process_workspace(workspace)
            
            return True
            
        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            return False
    
    def print_summary(self):
        """Print statistics summary."""
        logger.info("=" * 60)
        logger.info("Backfill Summary")
        logger.info("=" * 60)
        logger.info(f"Total workspaces scanned:  {self.stats['total_workspaces']}")
        logger.info(f"Already registered:        {self.stats['already_registered']}")
        logger.info(f"Newly registered:          {self.stats['registered']}")
        logger.info(f"  With parent linkage:     {self.stats['with_parent']}")
        logger.info(f"Skipped (non-conversations): {self.stats['skipped']}")
        logger.info(f"Errors:                    {self.stats['errors']}")
        logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Backfill conversations.db from workspaces")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview without making changes (default)")
    parser.add_argument("--execute", action="store_true", help="Actually execute the backfill")
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    logger.info("[DRY RUN MODE]" if dry_run else "[EXECUTE MODE]")
    
    try:
        backfiller = ConversationBackfiller(dry_run=dry_run)
        success = backfiller.scan_all()
        backfiller.print_summary()
        
        if dry_run and success:
            logger.info("")
            logger.info("To execute changes, run with --execute flag")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Backfill failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
