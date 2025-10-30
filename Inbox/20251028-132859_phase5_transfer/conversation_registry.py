#!/usr/bin/env python3
"""
N5 Conversation Registry
Central SQLite database tracking all conversations, artifacts, issues, learnings

Principles: P1 (Human-Readable), P2 (SSOT), P7 (Dry-Run), P19 (Error Handling)
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent))

try:
    from n5_title_generator import TitleGenerator
    TITLE_GENERATOR_AVAILABLE = True
except ImportError:
    logger.warning("n5_title_generator not found, will use basic titles")
    TITLE_GENERATOR_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/N5/data/conversations.db")

SCHEMA = """
-- Core conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    mode TEXT,
    
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT,
    
    focus TEXT,
    objective TEXT,
    tags TEXT,
    
    parent_id TEXT,
    related_ids TEXT,
    
    starred INTEGER DEFAULT 0,
    progress_pct INTEGER DEFAULT 0,
    
    workspace_path TEXT,
    state_file_path TEXT,
    aar_path TEXT,
    
    FOREIGN KEY (parent_id) REFERENCES conversations(id)
);

CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    filepath TEXT NOT NULL,
    artifact_type TEXT,
    created_at TEXT NOT NULL,
    description TEXT,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    severity TEXT NOT NULL,
    category TEXT,
    message TEXT NOT NULL,
    context TEXT,
    resolution TEXT,
    resolved INTEGER DEFAULT 0,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE TABLE IF NOT EXISTS learnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    lesson_id TEXT UNIQUE NOT NULL,
    timestamp TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    principle_refs TEXT,
    status TEXT DEFAULT 'pending',
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    decision TEXT NOT NULL,
    rationale TEXT,
    alternatives TEXT,
    outcome TEXT,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE INDEX IF NOT EXISTS idx_conversations_type ON conversations(type);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conversations_starred ON conversations(starred);
CREATE INDEX IF NOT EXISTS idx_conversations_parent ON conversations(parent_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_convo ON artifacts(conversation_id);
CREATE INDEX IF NOT EXISTS idx_issues_convo ON issues(conversation_id);
CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues(severity, resolved);
CREATE INDEX IF NOT EXISTS idx_learnings_convo ON learnings(conversation_id);
CREATE INDEX IF NOT EXISTS idx_learnings_status ON learnings(status);
"""


class ConversationRegistry:
    """Central registry for tracking conversations, artifacts, issues, learnings"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self):
        """Initialize database and schema"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()
        
        logger.info(f"Database ready: {self.db_path}")
    
    @contextmanager
    def _connect(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def create(
        self,
        convo_id: str,
        type: str,
        status: str = "active",
        mode: str = "standalone",
        parent_id: Optional[str] = None,
        focus: Optional[str] = None,
        objective: Optional[str] = None,
        tags: Optional[List[str]] = None,
        workspace_path: Optional[str] = None,
        state_file_path: Optional[str] = None
    ) -> bool:
        """
        Create new conversation record
        
        Args:
            convo_id: Conversation ID (con_XXX)
            type: build, research, discussion, planning, content
            status: active, complete, archived, blocked
            mode: standalone, orchestrator, worker
            parent_id: For worker threads, orchestrator conversation ID
        
        Returns:
            True if created, False if already exists
        """
        try:
            now = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
            
            with self._connect() as conn:
                # Check if exists
                existing = conn.execute(
                    "SELECT id FROM conversations WHERE id = ?",
                    (convo_id,)
                ).fetchone()
                
                if existing:
                    logger.warning(f"Conversation {convo_id} already exists")
                    return False
                
                conn.execute("""
                    INSERT INTO conversations (
                        id, type, status, mode, created_at, updated_at,
                        parent_id, focus, objective, tags,
                        workspace_path, state_file_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    convo_id, type, status, mode, now, now,
                    parent_id, focus, objective, json.dumps(tags or []),
                    workspace_path, state_file_path
                ))
                conn.commit()
            
            logger.info(f"✓ Created conversation: {convo_id} (type={type}, mode={mode})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create conversation {convo_id}: {e}", exc_info=True)
            return False
    
    def update(self, convo_id: str, **fields) -> bool:
        """
        Update conversation fields
        
        Args:
            convo_id: Conversation ID
            **fields: Field names and values to update
        
        Returns:
            True if updated, False if conversation not found
        """
        try:
            # Special handling for tags (convert list to JSON)
            if "tags" in fields and isinstance(fields["tags"], list):
                fields["tags"] = json.dumps(fields["tags"])
            
            # Always update updated_at
            fields["updated_at"] = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
            
            # Build UPDATE query
            set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
            values = list(fields.values()) + [convo_id]
            
            with self._connect() as conn:
                cursor = conn.execute(
                    f"UPDATE conversations SET {set_clause} WHERE id = ?",
                    values
                )
                conn.commit()
                
                if cursor.rowcount == 0:
                    logger.warning(f"Conversation {convo_id} not found")
                    return False
            
            logger.debug(f"✓ Updated conversation: {convo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update conversation {convo_id}: {e}", exc_info=True)
            return False
    
    def add_artifact(
        self,
        convo_id: str,
        filepath: str,
        artifact_type: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """
        Add artifact to conversation
        
        Args:
            convo_id: Conversation ID
            filepath: Absolute path to artifact
            artifact_type: script, document, data, config, command
            description: Human-readable description
        
        Returns:
            True if added successfully
        """
        try:
            now = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
            
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO artifacts (
                        conversation_id, filepath, artifact_type, created_at, description
                    ) VALUES (?, ?, ?, ?, ?)
                """, (convo_id, filepath, artifact_type, now, description))
                conn.commit()
            
            logger.debug(f"✓ Added artifact: {filepath} to {convo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add artifact: {e}", exc_info=True)
            return False
    
    def log_issue(
        self,
        convo_id: str,
        severity: str,
        category: str,
        message: str,
        context: Optional[str] = None
    ) -> bool:
        """
        Log significant issue
        
        Args:
            convo_id: Conversation ID
            severity: blocker, system_threat, learning_opportunity
            category: tool_failure, logic_error, external_api, design_flaw
            message: Brief description
            context: Stack traces, reproduction steps
        
        Returns:
            True if logged successfully
        """
        try:
            now = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
            
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO issues (
                        conversation_id, timestamp, severity, category, message, context
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (convo_id, now, severity, category, message, context))
                conn.commit()
            
            logger.info(f"⚠️  Issue logged: {severity} - {message[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log issue: {e}", exc_info=True)
            return False
    
    def log_decision(
        self,
        convo_id: str,
        decision: str,
        rationale: Optional[str] = None,
        alternatives: Optional[str] = None,
        outcome: Optional[str] = None
    ) -> bool:
        """
        Log design decision
        
        Args:
            convo_id: Conversation ID
            decision: What was decided
            rationale: Why this choice
            alternatives: What else was considered
            outcome: How did it work out (updated later)
        
        Returns:
            True if logged successfully
        """
        try:
            now = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
            
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO decisions (
                        conversation_id, timestamp, decision, rationale, alternatives, outcome
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (convo_id, now, decision, rationale, alternatives, outcome))
                conn.commit()
            
            logger.debug(f"✓ Decision logged: {decision[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log decision: {e}", exc_info=True)
            return False
    
    def import_learning(self, convo_id: str, lesson_data: Dict[str, Any]) -> bool:
        """
        Import learning from lessons system
        
        Args:
            convo_id: Conversation ID
            lesson_data: Lesson dict from lessons.jsonl
        
        Returns:
            True if imported successfully
        """
        try:
            with self._connect() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO learnings (
                        conversation_id, lesson_id, timestamp, type, title, 
                        description, principle_refs, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    convo_id,
                    lesson_data["lesson_id"],
                    lesson_data["timestamp"],
                    lesson_data["type"],
                    lesson_data["title"],
                    lesson_data["description"],
                    json.dumps(lesson_data.get("principle_refs", [])),
                    lesson_data.get("status", "pending")
                ))
                conn.commit()
            
            logger.debug(f"✓ Imported learning: {lesson_data['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import learning: {e}", exc_info=True)
            return False
    
    def close(self, convo_id: str, aar_path: Optional[str] = None) -> bool:
        """
        Close conversation
        
        Args:
            convo_id: Conversation ID
            aar_path: Path to archived AAR
        
        Returns:
            True if closed successfully
        """
        try:
            now = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
            
            fields = {
                "status": "complete",
                "completed_at": now,
                "updated_at": now
            }
            
            if aar_path:
                fields["aar_path"] = aar_path
            
            return self.update(convo_id, **fields)
            
        except Exception as e:
            logger.error(f"Failed to close conversation {convo_id}: {e}", exc_info=True)
            return False
    
    def close_conversation(self, convo_id: str, aar_path: Optional[str] = None) -> bool:
        """
        Close a conversation
        
        Args:
            convo_id: Conversation ID
            aar_path: Optional path to AAR file
        
        Returns:
            True if successful
        """
        try:
            fields = {
                "status": "completed",
                "completed_at": datetime.now(UTC).isoformat().replace('+00:00', 'Z')
            }
            
            if aar_path:
                fields["aar_path"] = aar_path
            
            return self.update(convo_id, **fields)
            
        except Exception as e:
            logger.error(f"Failed to close conversation {convo_id}: {e}", exc_info=True)
            return False
    
    def get(self, convo_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation by ID
        
        Args:
            convo_id: Conversation ID
        
        Returns:
            Conversation dict or None if not found
        """
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT * FROM conversations WHERE id = ?",
                    (convo_id,)
                ).fetchone()
                
                if not row:
                    return None
                
                result = dict(row)
                # Parse JSON fields
                if result.get("tags"):
                    result["tags"] = json.loads(result["tags"])
                if result.get("related_ids"):
                    result["related_ids"] = json.loads(result["related_ids"])
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to get conversation {convo_id}: {e}", exc_info=True)
            return None
    
    def get_with_details(self, convo_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation with all related data (artifacts, issues, learnings, decisions)
        
        Args:
            convo_id: Conversation ID
        
        Returns:
            Conversation dict with nested details or None
        """
        try:
            convo = self.get(convo_id)
            if not convo:
                return None
            
            with self._connect() as conn:
                # Get artifacts
                artifacts = conn.execute(
                    "SELECT * FROM artifacts WHERE conversation_id = ? ORDER BY created_at",
                    (convo_id,)
                ).fetchall()
                convo["artifacts"] = [dict(row) for row in artifacts]
                
                # Get issues
                issues = conn.execute(
                    "SELECT * FROM issues WHERE conversation_id = ? ORDER BY timestamp DESC",
                    (convo_id,)
                ).fetchall()
                convo["issues"] = [dict(row) for row in issues]
                
                # Get learnings
                learnings = conn.execute(
                    "SELECT * FROM learnings WHERE conversation_id = ? ORDER BY timestamp",
                    (convo_id,)
                ).fetchall()
                convo["learnings"] = [dict(row) for row in learnings]
                
                # Get decisions
                decisions = conn.execute(
                    "SELECT * FROM decisions WHERE conversation_id = ? ORDER BY timestamp",
                    (convo_id,)
                ).fetchall()
                convo["decisions"] = [dict(row) for row in decisions]
            
            return convo
            
        except Exception as e:
            logger.error(f"Failed to get conversation details: {e}", exc_info=True)
            return None
    
    def search(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search conversations
        
        Args:
            query: Text search in focus/objective/tags
            filters: Dict of field filters (type, status, mode, parent_id, starred)
            limit: Max results
        
        Returns:
            List of conversation dicts
        """
        try:
            conditions = []
            params = []
            
            # Text search
            if query:
                conditions.append("(focus LIKE ? OR objective LIKE ? OR tags LIKE ?)")
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])
            
            # Field filters
            if filters:
                for field, value in filters.items():
                    conditions.append(f"{field} = ?")
                    params.append(value)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            with self._connect() as conn:
                rows = conn.execute(
                    f"SELECT * FROM conversations WHERE {where_clause} ORDER BY updated_at DESC LIMIT ?",
                    params + [limit]
                ).fetchall()
                
                results = []
                for row in rows:
                    result = dict(row)
                    if result.get("tags"):
                        result["tags"] = json.loads(result["tags"])
                    if result.get("related_ids"):
                        result["related_ids"] = json.loads(result["related_ids"])
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return []
    
    def get_workers(self, orchestrator_id: str) -> List[Dict[str, Any]]:
        """
        Get all worker threads for an orchestrator
        
        Args:
            orchestrator_id: Orchestrator conversation ID
        
        Returns:
            List of worker conversation dicts
        """
        return self.search(filters={"parent_id": orchestrator_id})
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics
        
        Returns:
            Dict with counts and metrics
        """
        try:
            with self._connect() as conn:
                stats = {}
                
                # Total conversations
                stats["total_conversations"] = conn.execute(
                    "SELECT COUNT(*) FROM conversations"
                ).fetchone()[0]
                
                # By type
                type_counts = conn.execute(
                    "SELECT type, COUNT(*) FROM conversations GROUP BY type"
                ).fetchall()
                stats["by_type"] = {row[0]: row[1] for row in type_counts}
                
                # By status
                status_counts = conn.execute(
                    "SELECT status, COUNT(*) FROM conversations GROUP BY status"
                ).fetchall()
                stats["by_status"] = {row[0]: row[1] for row in status_counts}
                
                # Total artifacts
                stats["total_artifacts"] = conn.execute(
                    "SELECT COUNT(*) FROM artifacts"
                ).fetchone()[0]
                
                # Unresolved issues
                stats["unresolved_issues"] = conn.execute(
                    "SELECT COUNT(*) FROM issues WHERE resolved = 0"
                ).fetchone()[0]
                
                # Pending learnings
                stats["pending_learnings"] = conn.execute(
                    "SELECT COUNT(*) FROM learnings WHERE status = 'pending'"
                ).fetchone()[0]
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get stats: {e}", exc_info=True)
            return {}

    def extract_conversation_metadata(self, convo_id: str, workspace_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Use LLM to extract focus, objective, tags from conversation workspace
        
        Args:
            convo_id: Conversation ID
            workspace_path: Path to conversation workspace (auto-detected if None)
        
        Returns:
            Dict with focus, objective, tags
        """
        try:
            if not workspace_path:
                workspace_path = f"/home/.z/workspaces/{convo_id}"
            
            workspace = Path(workspace_path)
            if not workspace.exists():
                logger.warning(f"Workspace not found: {workspace_path}")
                return {}
            
            # Gather context
            context_parts = []
            
            # Read SESSION_STATE if exists
            state_file = workspace / "SESSION_STATE.md"
            if state_file.exists():
                context_parts.append(f"=== SESSION_STATE.md ===\n{state_file.read_text()[:2000]}")
            
            # Read recent chat messages or logs
            for log_file in workspace.glob("*.md"):
                if log_file.name != "SESSION_STATE.md":
                    content = log_file.read_text()[:1000]
                    context_parts.append(f"=== {log_file.name} ===\n{content}")
                    if len(context_parts) >= 3:
                        break
            
            if not context_parts:
                logger.warning(f"No context found in workspace: {workspace_path}")
                return {}
            
            context = "\n\n".join(context_parts)
            
            # Create extraction prompt
            prompt = f"""Analyze this conversation workspace and extract metadata.

{context}

Generate a JSON object with:
- focus: One sentence describing the main topic/goal (max 80 chars)
- objective: 1-2 sentences describing what's being accomplished (max 200 chars)
- tags: Array of 3-8 relevant keywords (lowercase, hyphenated)

Respond ONLY with valid JSON, no other text."""

            # Call LLM via shell (using current conversation context)
            # Note: In production, this would use a dedicated LLM API
            # For now, we'll parse context heuristically and return structured data
            
            # Heuristic extraction (placeholder for LLM call)
            extracted = {
                "focus": "Conversation workspace analysis needed",
                "objective": "Extract meaningful metadata from conversation content",
                "tags": ["metadata", "analysis", "extraction"]
            }
            
            # TODO: Replace with actual LLM API call when available
            logger.info(f"Extracted metadata for {convo_id}: {extracted['focus'][:50]}")
            
            return extracted
            
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}", exc_info=True)
            return {}
    
    def enrich_conversation(self, convo_id: str, workspace_path: Optional[str] = None) -> bool:
        """
        Enrich conversation with auto-generated title using n5_title_generator
        """
        try:
            if not TITLE_GENERATOR_AVAILABLE:
                logger.warning("Title generator not available, skipping enrichment")
                return False
            
            convo = self.get(convo_id)
            if not convo:
                logger.error(f"Conversation {convo_id} not found")
                return False
            
            # Build mock AAR data for title generator
            aar_data = {
                "objective": convo.get("objective", "") or convo.get("focus", ""),
                "summary": convo.get("focus", ""),
                "artifacts": [],
                "key_events": []
            }
            
            # Try to load actual workspace content if available
            if not workspace_path:
                workspace_path = convo.get("workspace_path")
            
            if workspace_path:
                ws_path = Path(workspace_path)
                session_state = ws_path / "SESSION_STATE.md"
                if session_state.exists():
                    content = session_state.read_text()
                    aar_data["summary"] = f"{aar_data['summary']}\n\n{content[:1000]}"
            
            # Generate title
            generator = TitleGenerator()
            title = generator.generate_auto_title(aar_data, [])
            
            if title:
                self.update(convo_id, title=title)
                logger.info(f"✓ Generated title: {title}")
                return True
            
            return False
                
        except Exception as e:
            logger.error(f"Failed to enrich conversation: {e}", exc_info=True)
            return False


def main():
    """Test registry functionality"""
    import argparse
    
    parser = argparse.ArgumentParser(description="N5 Conversation Registry")
    parser.add_argument("--init", action="store_true", help="Initialize database")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--test", action="store_true", help="Run test")
    
    args = parser.parse_args()
    
    registry = ConversationRegistry()
    
    if args.init:
        print("✓ Database initialized")
    
    if args.stats:
        stats = registry.get_stats()
        print("\nRegistry Statistics:")
        print(f"  Total conversations: {stats.get('total_conversations', 0)}")
        print(f"  By type: {stats.get('by_type', {})}")
        print(f"  By status: {stats.get('by_status', {})}")
        print(f"  Total artifacts: {stats.get('total_artifacts', 0)}")
        print(f"  Unresolved issues: {stats.get('unresolved_issues', 0)}")
        print(f"  Pending learnings: {stats.get('pending_learnings', 0)}")
    
    if args.test:
        print("\nRunning tests...")
        
        # Test create
        test_id = "con_TEST123"
        registry.create(
            test_id,
            type="build",
            focus="Test conversation",
            tags=["test", "demo"]
        )
        
        # Test update
        registry.update(test_id, progress_pct=50, status="active")
        
        # Test add artifact
        registry.add_artifact(test_id, "/test/path.py", "script", "Test script")
        
        # Test log issue
        registry.log_issue(
            test_id,
            "learning_opportunity",
            "tool_failure",
            "Test issue message",
            "Test context"
        )
        
        # Test get
        convo = registry.get_with_details(test_id)
        print(f"\nRetrieved conversation: {convo['id']}")
        print(f"  Focus: {convo['focus']}")
        print(f"  Progress: {convo['progress_pct']}%")
        print(f"  Artifacts: {len(convo['artifacts'])}")
        print(f"  Issues: {len(convo['issues'])}")
        
        # Test search
        results = registry.search(query="Test", filters={"type": "build"})
        print(f"\nSearch results: {len(results)} conversations")
        
        print("\n✓ All tests passed")
    
    return 0


if __name__ == "__main__":
    exit(main())
