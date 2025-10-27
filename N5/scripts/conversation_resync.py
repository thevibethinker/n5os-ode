#!/usr/bin/env python3
"""
Conversation Re-Sync Script
Re-scan SESSION_STATE files and update database with correct metadata including parent relationships.

Principles: P1 (Human-Readable), P7 (Dry-Run), P15 (Complete), P19 (Error Handling)

Usage:
    python3 conversation_resync.py --dry-run
    python3 conversation_resync.py --execute
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

sys.path.insert(0, str(Path(__file__).parent))
from conversation_registry import ConversationRegistry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

CONVO_WORKSPACES_ROOT = Path("/home/.z/workspaces")


class ConversationResyncer:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.registry = ConversationRegistry()
        self.stats = {
            "scanned": 0,
            "updated_title": 0,
            "updated_focus": 0,
            "updated_parent": 0,
            "errors": 0
        }
    
    def extract_metadata(self, session_path: Path) -> Dict:
        """Extract all metadata from SESSION_STATE.md"""
        try:
            content = session_path.read_text()
            metadata = {}
            
            # Extract conversation ID
            convo_match = re.search(r"Conversation ID:\*\* (con_[a-zA-Z0-9]+)", content)
            if convo_match:
                metadata["id"] = convo_match.group(1)
            
            # Extract type
            type_match = re.search(r"Primary Type:\*\* (\w+)", content)
            if type_match:
                metadata["type"] = type_match.group(1)
            
            # Extract mode
            mode_match = re.search(r"Mode:\*\* (.+?)(?:\n|$)", content, re.MULTILINE)
            if mode_match:
                mode = mode_match.group(1).strip()
                if mode and mode != "*":
                    metadata["mode"] = mode
            
            # Extract focus
            focus_match = re.search(r"\*\*Focus:\*\* (.+?)$", content, re.MULTILINE)
            if focus_match:
                focus = focus_match.group(1).strip()
                if not focus.startswith("*"):  # Skip placeholder text
                    metadata["focus"] = focus
            
            # Extract objective
            goal_match = re.search(r"\*\*Goal:\*\* (.+?)$", content, re.MULTILINE)
            if goal_match:
                goal = goal_match.group(1).strip()
                if not goal.startswith("*"):  # Skip placeholder text
                    metadata["objective"] = goal
            
            # Extract parent - multiple patterns
            parent_id = None
            
            # Pattern 1: "Parent Conversation: con_XXX"
            parent_match = re.search(r"Parent Conversation:\*\* (con_[a-zA-Z0-9]+)", content)
            if parent_match:
                parent_id = parent_match.group(1)
            
            # Pattern 2: "Orchestrator: con_XXX"
            if not parent_id:
                orch_match = re.search(r"Orchestrator:\*\* (con_[a-zA-Z0-9]+)", content)
                if orch_match:
                    parent_id = orch_match.group(1)
            
            # Pattern 3: Look in Relationships section
            if not parent_id:
                relations_match = re.search(r"(con_[a-zA-Z0-9]+) - (?:Orchestrator|Parent)", content)
                if relations_match:
                    candidate = relations_match.group(1)
                    # Make sure it's not self-reference
                    if candidate != metadata.get("id"):
                        parent_id = candidate
            
            if parent_id:
                metadata["parent_id"] = parent_id
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {session_path}: {e}")
            return {}
    
    def resync_conversation(self, convo_id: str, workspace: Path) -> bool:
        """Re-sync a single conversation's metadata"""
        try:
            session_path = workspace / "SESSION_STATE.md"
            if not session_path.exists():
                return True  # Skip if no SESSION_STATE
            
            # Extract fresh metadata
            metadata = self.extract_metadata(session_path)
            if not metadata:
                return True
            
            # Get current database state
            with self.registry._connect() as conn:
                current = conn.execute(
                    "SELECT title, focus, parent_id FROM conversations WHERE id = ?",
                    (convo_id,)
                ).fetchone()
            
            if not current:
                logger.warning(f"Conversation {convo_id} not in database, skipping")
                return True
            
            current_title, current_focus, current_parent = current
            updates_needed = []
            
            # Check what needs updating
            new_focus = metadata.get("focus", "").strip()
            new_parent = metadata.get("parent_id")
            
            # Generate title from focus if missing
            if not current_title and new_focus:
                updates_needed.append(("title", new_focus[:100]))  # Truncate long titles
            
            # Update focus if different and non-empty
            if new_focus and new_focus != (current_focus or ""):
                updates_needed.append(("focus", new_focus))
            
            # Update parent if different
            if new_parent and new_parent != current_parent:
                updates_needed.append(("parent_id", new_parent))
            
            # Apply updates
            if updates_needed:
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would update {convo_id}:")
                    for field, value in updates_needed:
                        logger.info(f"  {field}: {value[:80] if isinstance(value, str) else value}")
                else:
                    with self.registry._connect() as conn:
                        for field, value in updates_needed:
                            conn.execute(
                                f"UPDATE conversations SET {field} = ?, updated_at = ? WHERE id = ?",
                                (value, datetime.now().isoformat(), convo_id)
                            )
                            if field == "title":
                                self.stats["updated_title"] += 1
                            elif field == "focus":
                                self.stats["updated_focus"] += 1
                            elif field == "parent_id":
                                self.stats["updated_parent"] += 1
                        conn.commit()
                    logger.info(f"✓ Updated {convo_id}: {len(updates_needed)} fields")
            
            return True
            
        except Exception as e:
            logger.error(f"Error resyncing {convo_id}: {e}")
            self.stats["errors"] += 1
            return False
    
    def run(self) -> bool:
        """Run resync on all conversations"""
        try:
            # Get all conversation IDs from database
            with self.registry._connect() as conn:
                convo_ids = [row[0] for row in conn.execute("SELECT id FROM conversations").fetchall()]
            
            logger.info(f"Re-syncing {len(convo_ids)} conversations...")
            
            for convo_id in convo_ids:
                workspace = CONVO_WORKSPACES_ROOT / convo_id
                if not workspace.exists():
                    continue
                
                self.stats["scanned"] += 1
                self.resync_conversation(convo_id, workspace)
            
            # Print summary
            logger.info("=" * 60)
            logger.info("Re-Sync Summary")
            logger.info("=" * 60)
            logger.info(f"Conversations scanned:  {self.stats['scanned']}")
            logger.info(f"Titles updated:         {self.stats['updated_title']}")
            logger.info(f"Focus updated:          {self.stats['updated_focus']}")
            logger.info(f"Parent links updated:   {self.stats['updated_parent']}")
            logger.info(f"Errors:                 {self.stats['errors']}")
            logger.info("=" * 60)
            
            return self.stats["errors"] == 0
            
        except Exception as e:
            logger.error(f"Re-sync failed: {e}", exc_info=True)
            return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-sync conversation metadata from SESSION_STATE files")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview changes without applying")
    parser.add_argument("--execute", action="store_true", help="Actually apply changes")
    args = parser.parse_args()
    
    dry_run = not args.execute
    logger.info("[DRY RUN MODE]" if dry_run else "[EXECUTE MODE]")
    
    try:
        resyncer = ConversationResyncer(dry_run=dry_run)
        success = resyncer.run()
        
        if dry_run and success:
            logger.info("")
            logger.info("To execute changes, run with --execute flag")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Re-sync failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
