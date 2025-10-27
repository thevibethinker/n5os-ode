#!/usr/bin/env python3
"""
N5 Conversation Supervisor
Groups, summarizes, and proposes batch operations for related conversations.

Principles: P1 (Human-Readable), P2 (SSOT), P7 (Dry-Run), P15 (Complete), P19 (Error Handling)

Usage:
    # List related conversations by type/focus/window
    python3 convo_supervisor.py list-related --type build --window-days 7
    
    # List conversations by parent/child relationships
    python3 convo_supervisor.py list-related --parent con_XXX
    
    # Generate unified summary for a group
    python3 convo_supervisor.py summarize --ids con_XXX,con_YYY,con_ZZZ
    
    # Propose batch title improvements
    python3 convo_supervisor.py propose-rename --type build --window-days 7 --dry-run
    
    # Propose archive moves for completed conversations
    python3 convo_supervisor.py propose-archive --status complete --older-than-days 30 --dry-run
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sqlite3
from collections import defaultdict
import difflib

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from conversation_registry import ConversationRegistry
except ImportError:
    print("ERROR: conversation_registry.py not found", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

CONVO_WORKSPACES_ROOT = Path("/home/.z/workspaces")
USER_WORKSPACE = Path("/home/workspace")


class ConversationSupervisor:
    """Supervisor for grouping, analyzing, and batch-operating on conversations"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.registry = ConversationRegistry()
    
    def list_related(
        self,
        convo_type: Optional[str] = None,
        window_days: int = 7,
        parent_id: Optional[str] = None,
        focus_similarity: bool = False,
        min_similarity: float = 0.6
    ) -> List[Dict]:
        """
        Find related conversations by various criteria.
        
        Args:
            convo_type: Filter by conversation type (build, research, etc.)
            window_days: Time window for grouping (days)
            parent_id: Find children of this parent conversation
            focus_similarity: Group by similar focus text
            min_similarity: Minimum similarity score for focus matching (0.0-1.0)
        
        Returns:
            List of conversation records
        """
        try:
            cutoff_date = (datetime.now(UTC) - timedelta(days=window_days)).isoformat()
            
            with self.registry._connect() as conn:
                # Base query
                if parent_id:
                    query = """
                        SELECT * FROM conversations
                        WHERE parent_id = ?
                        ORDER BY created_at DESC
                    """
                    params = (parent_id,)
                else:
                    query = """
                        SELECT * FROM conversations
                        WHERE created_at >= ?
                    """
                    params = (cutoff_date,)
                    
                    if convo_type:
                        query += " AND type = ?"
                        params = params + (convo_type,)
                    
                    query += " ORDER BY created_at DESC"
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                conversations = [dict(row) for row in rows]
                
                # If focus similarity requested, group by similar focus
                if focus_similarity and conversations:
                    conversations = self._group_by_focus_similarity(
                        conversations, 
                        min_similarity
                    )
                
                return conversations
                
        except Exception as e:
            logger.error(f"Error listing related conversations: {e}", exc_info=True)
            return []
    
    def _group_by_focus_similarity(
        self, 
        conversations: List[Dict], 
        min_similarity: float
    ) -> List[Dict]:
        """Group conversations by focus text similarity"""
        # Add similarity scores
        for i, conv in enumerate(conversations):
            conv['similar_to'] = []
            focus1 = conv.get('focus', '') or ''
            
            for j, other in enumerate(conversations):
                if i == j:
                    continue
                
                focus2 = other.get('focus', '') or ''
                if not focus1 or not focus2:
                    continue
                
                similarity = difflib.SequenceMatcher(None, focus1, focus2).ratio()
                if similarity >= min_similarity:
                    conv['similar_to'].append({
                        'id': other['id'],
                        'similarity': round(similarity, 2),
                        'focus': focus2
                    })
        
        return conversations
    
    def summarize(
        self, 
        conversation_ids: List[str],
        include_artifacts: bool = True
    ) -> Dict:
        """
        Generate unified summary for a group of conversations.
        
        Args:
            conversation_ids: List of conversation IDs to summarize
            include_artifacts: Include artifacts listing in summary
        
        Returns:
            Unified summary dictionary
        """
        try:
            summaries = []
            all_artifacts = []
            all_tags = set()
            types = set()
            statuses = defaultdict(int)
            
            with self.registry._connect() as conn:
                for conv_id in conversation_ids:
                    # Get conversation details
                    cursor = conn.execute(
                        "SELECT * FROM conversations WHERE id = ?", 
                        (conv_id,)
                    )
                    row = cursor.fetchone()
                    
                    if not row:
                        logger.warning(f"Conversation not found: {conv_id}")
                        continue
                    
                    conv = dict(row)
                    types.add(conv['type'])
                    statuses[conv['status']] += 1
                    
                    # Parse tags
                    tags = conv.get('tags', '') or ''
                    if tags:
                        all_tags.update(t.strip() for t in tags.split(','))
                    
                    # Get session state summary
                    state_file = CONVO_WORKSPACES_ROOT / conv_id / "SESSION_STATE.md"
                    focus = conv.get('focus', 'N/A')
                    objective = conv.get('objective', 'N/A')
                    
                    summaries.append({
                        'id': conv_id,
                        'title': conv.get('title', 'Untitled'),
                        'type': conv['type'],
                        'status': conv['status'],
                        'focus': focus,
                        'objective': objective,
                        'created_at': conv['created_at'],
                        'progress': conv.get('progress_pct', 0)
                    })
                    
                    # Get artifacts if requested
                    if include_artifacts:
                        cursor = conn.execute(
                            "SELECT * FROM artifacts WHERE conversation_id = ?",
                            (conv_id,)
                        )
                        artifacts = [dict(row) for row in cursor.fetchall()]
                        all_artifacts.extend(artifacts)
            
            # Build unified summary
            unified = {
                'conversation_count': len(conversation_ids),
                'types': list(types),
                'status_breakdown': dict(statuses),
                'common_tags': sorted(all_tags),
                'conversations': summaries,
                'artifact_count': len(all_artifacts),
                'generated_at': datetime.now(UTC).isoformat()
            }
            
            if include_artifacts:
                unified['artifacts'] = all_artifacts
            
            return unified
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            return {}
    
    def propose_rename(
        self,
        convo_type: Optional[str] = None,
        window_days: int = 7,
        strategy: str = "focus_based"
    ) -> List[Dict]:
        """
        Propose batch title improvements for conversations.
        
        Args:
            convo_type: Filter by conversation type
            window_days: Time window for selection
            strategy: Naming strategy (focus_based, pattern_based)
        
        Returns:
            List of rename proposals
        """
        try:
            conversations = self.list_related(
                convo_type=convo_type,
                window_days=window_days
            )
            
            proposals = []
            
            for conv in conversations:
                current_title = conv.get('title', '')
                focus = conv.get('focus', '')
                conv_type = conv.get('type', 'discussion')
                created = conv.get('created_at', '')
                
                # Skip if already has good title
                if current_title and len(current_title) > 10 and not current_title.startswith('Untitled'):
                    continue
                
                # Generate proposed title based on strategy
                if strategy == "focus_based" and focus:
                    # Use focus text as title base
                    proposed = self._generate_title_from_focus(focus, conv_type, created)
                elif strategy == "pattern_based":
                    # Use type + date pattern
                    date_str = created[:10] if created else 'unknown'
                    proposed = f"{date_str} {conv_type.title()} Session"
                else:
                    proposed = f"{conv_type.title()}: {focus[:50] if focus else 'Session'}"
                
                if proposed and proposed != current_title:
                    proposals.append({
                        'id': conv['id'],
                        'current_title': current_title or '(none)',
                        'proposed_title': proposed,
                        'confidence': 'high' if focus else 'low',
                        'reason': f"Generated from {strategy} strategy"
                    })
            
            return proposals
            
        except Exception as e:
            logger.error(f"Error proposing renames: {e}", exc_info=True)
            return []
    
    def _generate_title_from_focus(
        self, 
        focus: str, 
        conv_type: str, 
        created_at: str
    ) -> str:
        """Generate human-readable title from focus text"""
        # Clean and truncate focus
        focus_clean = focus.strip().replace('\n', ' ')
        if len(focus_clean) > 60:
            focus_clean = focus_clean[:57] + "..."
        
        # Add date prefix
        date_str = created_at[:10] if created_at else ''
        
        # Format based on type
        type_emoji = {
            'build': '🔨',
            'research': '🔍',
            'discussion': '💬',
            'planning': '📋'
        }.get(conv_type, '')
        
        return f"{date_str} {type_emoji} {focus_clean}"
    
    def propose_archive(
        self,
        status: str = "complete",
        older_than_days: int = 30,
        exclude_starred: bool = True
    ) -> List[Dict]:
        """
        Propose archive moves for completed/old conversations.
        
        Args:
            status: Filter by conversation status
            older_than_days: Age threshold in days
            exclude_starred: Skip starred conversations
        
        Returns:
            List of archive proposals
        """
        try:
            cutoff_date = (datetime.now(UTC) - timedelta(days=older_than_days)).isoformat()
            
            with self.registry._connect() as conn:
                query = """
                    SELECT * FROM conversations
                    WHERE status = ?
                    AND (completed_at < ? OR (completed_at IS NULL AND updated_at < ?))
                """
                params = [status, cutoff_date, cutoff_date]
                
                if exclude_starred:
                    query += " AND starred = 0"
                
                query += " ORDER BY updated_at ASC"
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                proposals = []
                for row in rows:
                    conv = dict(row)
                    current_path = conv.get('workspace_path', '')
                    
                    # Propose archive location based on type and date
                    date_str = (conv.get('completed_at') or conv.get('updated_at', ''))[:10]
                    proposed_path = USER_WORKSPACE / "Documents" / "Archive" / f"{date_str}-{conv['type']}-{conv['id']}"
                    
                    proposals.append({
                        'id': conv['id'],
                        'title': conv.get('title', 'Untitled'),
                        'current_path': current_path,
                        'proposed_path': str(proposed_path),
                        'age_days': (datetime.now(UTC) - datetime.fromisoformat(conv['updated_at'].replace('Z', '+00:00'))).days,
                        'reason': f"Status={status}, age>{older_than_days}d"
                    })
                
                return proposals
                
        except Exception as e:
            logger.error(f"Error proposing archives: {e}", exc_info=True)
            return []
    
    def execute_rename(self, proposals: List[Dict]) -> int:
        """
        Execute batch rename operations.
        
        Args:
            proposals: List of rename proposals from propose_rename()
        
        Returns:
            Number of successful renames
        """
        if self.dry_run:
            logger.info("[DRY RUN] Would rename conversations:")
            for prop in proposals:
                logger.info(f"  {prop['id']}: '{prop['current_title']}' → '{prop['proposed_title']}'")
            return 0
        
        success_count = 0
        
        try:
            with self.registry._connect() as conn:
                for prop in proposals:
                    try:
                        conn.execute(
                            "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                            (prop['proposed_title'], datetime.now(UTC).isoformat(), prop['id'])
                        )
                        conn.commit()
                        logger.info(f"✓ Renamed {prop['id']}: {prop['proposed_title']}")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Failed to rename {prop['id']}: {e}")
                        continue
            
            return success_count
            
        except Exception as e:
            logger.error(f"Error executing renames: {e}", exc_info=True)
            return success_count

    def tree_view(self, root_id: Optional[str] = None, include_artifacts: bool = False) -> int:
        """Display parent-child relationships in tree structure."""
        try:
            with self.registry._connect() as conn:
                if root_id:
                    # Show tree starting from specific root
                    roots = [(root_id,)]
                else:
                    # Show all root conversations (no parent)
                    roots = conn.execute(
                        "SELECT id FROM conversations WHERE parent_id IS NULL AND type != 'discussion' ORDER BY created_at DESC LIMIT 20"
                    ).fetchall()
                
                def print_tree(conv_id: str, prefix: str = "", is_last: bool = True):
                    """Recursively print tree."""
                    # Get conversation info
                    conv = conn.execute(
                        "SELECT id, title, type, status, focus FROM conversations WHERE id = ?",
                        (conv_id,)
                    ).fetchone()
                    
                    if not conv:
                        return
                    
                    # Format output
                    connector = "└── " if is_last else "├── "
                    title = conv[1] or "(untitled)"
                    conv_type = conv[2]
                    status = conv[3]
                    focus = conv[4] or ""
                    
                    info = f"{title[:60]} [{conv_type}, {status}]"
                    if focus and len(focus) < 50:
                        info += f" - {focus[:50]}"
                    
                    logger.info(f"{prefix}{connector}{conv_id}: {info}")
                    
                    # Get children
                    children = conn.execute(
                        "SELECT id FROM conversations WHERE parent_id = ? ORDER BY created_at",
                        (conv_id,)
                    ).fetchall()
                    
                    # Print children
                    for i, (child_id,) in enumerate(children):
                        is_last_child = (i == len(children) - 1)
                        child_prefix = prefix + ("    " if is_last else "│   ")
                        print_tree(child_id, child_prefix, is_last_child)
                
                logger.info("=" * 80)
                logger.info("Conversation Tree View")
                logger.info("=" * 80)
                
                if not roots:
                    logger.info("No root conversations found")
                    return 0
                
                for i, (root_id,) in enumerate(roots):
                    print_tree(root_id, "", i == len(roots) - 1)
                    if i < len(roots) - 1:
                        logger.info("")
                
                return 0
                
        except Exception as e:
            logger.error(f"Tree view failed: {e}", exc_info=True)
            return 1


def main():
    parser = argparse.ArgumentParser(description="N5 Conversation Supervisor")
    parser.add_argument(
        "action",
        choices=["list-related", "summarize", "propose-rename", "propose-archive", "execute-rename", "tree"],
        help="Action to perform"
    )
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Preview operations without executing (default: true)")
    parser.add_argument("--execute", action="store_true",
                        help="Actually execute operations (overrides dry-run)")
    
    # Filters
    parser.add_argument("--type", help="Conversation type filter")
    parser.add_argument("--status", default="complete", help="Status filter")
    parser.add_argument("--window-days", type=int, default=7,
                        help="Time window in days")
    parser.add_argument("--older-than-days", type=int, default=30,
                        help="Age threshold in days")
    parser.add_argument("--parent", help="Parent conversation ID")
    
    # Options
    parser.add_argument("--ids", help="Comma-separated conversation IDs")
    parser.add_argument("--focus-similarity", action="store_true",
                        help="Group by focus similarity")
    parser.add_argument("--min-similarity", type=float, default=0.6,
                        help="Minimum similarity score (0.0-1.0)")
    parser.add_argument("--strategy", default="focus_based",
                        choices=["focus_based", "pattern_based"],
                        help="Title generation strategy")
    parser.add_argument("--include-artifacts", action="store_true",
                        help="Include artifacts in summary")
    parser.add_argument("--exclude-starred", action="store_true", default=True,
                        help="Exclude starred conversations from archive")
    parser.add_argument("--output", help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    # Determine dry-run mode
    dry_run = args.dry_run and not args.execute
    
    supervisor = ConversationSupervisor(dry_run=dry_run)
    
    try:
        if args.action == "list-related":
            results = supervisor.list_related(
                convo_type=args.type,
                window_days=args.window_days,
                parent_id=args.parent,
                focus_similarity=args.focus_similarity,
                min_similarity=args.min_similarity
            )
            
            logger.info(f"Found {len(results)} related conversations")
            for conv in results:
                logger.info(f"  {conv['id']}: {conv.get('title', 'Untitled')} ({conv['type']}, {conv['status']})")
                if args.focus_similarity and conv.get('similar_to'):
                    for sim in conv['similar_to']:
                        logger.info(f"    └─ {sim['similarity']:.0%} similar to {sim['id']}")
        
        elif args.action == "summarize":
            if not args.ids:
                logger.error("--ids required for summarize action")
                return 1
            
            conv_ids = [id.strip() for id in args.ids.split(',')]
            summary = supervisor.summarize(
                conversation_ids=conv_ids,
                include_artifacts=args.include_artifacts
            )
            
            logger.info(f"Unified Summary:")
            logger.info(f"  Conversations: {summary['conversation_count']}")
            logger.info(f"  Types: {', '.join(summary['types'])}")
            logger.info(f"  Status: {summary['status_breakdown']}")
            logger.info(f"  Artifacts: {summary['artifact_count']}")
            if summary.get('common_tags'):
                logger.info(f"  Tags: {', '.join(summary['common_tags'][:5])}")
            
            results = summary
        
        elif args.action == "propose-rename":
            proposals = supervisor.propose_rename(
                convo_type=args.type,
                window_days=args.window_days,
                strategy=args.strategy
            )
            
            logger.info(f"Rename Proposals: {len(proposals)}")
            for prop in proposals:
                logger.info(f"  {prop['id']} [{prop['confidence']}]:")
                logger.info(f"    Current: {prop['current_title']}")
                logger.info(f"    Proposed: {prop['proposed_title']}")
            
            results = proposals
        
        elif args.action == "propose-archive":
            proposals = supervisor.propose_archive(
                status=args.status,
                older_than_days=args.older_than_days,
                exclude_starred=args.exclude_starred
            )
            
            logger.info(f"Archive Proposals: {len(proposals)}")
            for prop in proposals:
                logger.info(f"  {prop['id']} ({prop['age_days']}d old):")
                logger.info(f"    {prop['title']}")
                logger.info(f"    → {prop['proposed_path']}")
            
            results = proposals
        
        elif args.action == "execute-rename":
            # First get proposals
            proposals = supervisor.propose_rename(
                convo_type=args.type,
                window_days=args.window_days,
                strategy=args.strategy
            )
            
            # Execute them
            count = supervisor.execute_rename(proposals)
            logger.info(f"✓ Renamed {count} conversations")
            results = {"renamed_count": count, "proposals": proposals}
        
        elif args.action == "tree":
            return supervisor.tree_view(
                root_id=args.parent,
                include_artifacts=args.include_artifacts
            )
        
        # Save output if requested
        if args.output and results:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"✓ Results saved to {output_path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
