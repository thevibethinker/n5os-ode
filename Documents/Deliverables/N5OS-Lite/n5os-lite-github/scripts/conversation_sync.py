#!/usr/bin/env python3
"""
Conversation DB Sync - Sync SESSION_STATE.md to conversations.db

Synchronizes conversation state from SESSION_STATE.md files into the 
conversations.db for querying, analytics, and intelligence extraction.

Usage:
  python3 conversation_sync.py sync --convo-id con_XXX
  python3 conversation_sync.py sync-all
  python3 conversation_sync.py query --type build --status active
"""

import argparse
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
import re


class ConversationSync:
    """Sync SESSION_STATE.md to conversations.db."""
    
    WORKSPACE_BASE = Path("/home/.z/workspaces")
    DB_PATH = Path("/home/workspace/N5/data/conversations.db")
    
    def __init__(self):
        self.conn = None
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Ensure conversations.db exists with proper schema."""
        self.conn = sqlite3.connect(str(self.DB_PATH))
        self.conn.row_factory = sqlite3.Row
        
        # Schema already exists based on inspection, but verify
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'"
        )
        if not cursor.fetchone():
            print("⚠️  conversations table doesn't exist, creating...", file=sys.stderr)
            self._create_schema()
    
    def _create_schema(self):
        """Create conversations table schema if it doesn't exist."""
        self.conn.execute("""
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
            )
        """)
        
        # Create indexes
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_type ON conversations(type)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_starred ON conversations(starred)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_parent ON conversations(parent_id)")
        
        self.conn.commit()
    
    def parse_session_state(self, convo_id: str) -> Optional[Dict]:
        """Parse SESSION_STATE.md for a conversation."""
        session_state_path = self.WORKSPACE_BASE / convo_id / "SESSION_STATE.md"
        
        if not session_state_path.exists():
            return None
        
        content = session_state_path.read_text()
        
        # Extract YAML frontmatter
        frontmatter = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                for line in yaml_content.strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        frontmatter[key.strip()] = value.strip()
        
        # Extract markdown sections
        data = {
            "id": convo_id,
            "type": frontmatter.get("type", "discussion"),
            "status": frontmatter.get("status", "active"),
            "mode": frontmatter.get("mode"),
            "created_at": frontmatter.get("created"),
            "updated_at": frontmatter.get("last_updated"),
            "workspace_path": str(self.WORKSPACE_BASE / convo_id),
            "state_file_path": str(session_state_path),
        }
        
        # Extract focus, objective, progress from markdown content
        if "**Focus:**" in content:
            match = re.search(r'\*\*Focus:\*\*\s*(.+?)(?:\n|$)', content)
            if match:
                data["focus"] = match.group(1).strip()
        
        if "**Objective:**" in content:
            match = re.search(r'\*\*Objective:\*\*\s*(.+?)(?:\n|$)', content)
            if match:
                data["objective"] = match.group(1).strip()
        
        if "**Overall:**" in content:
            match = re.search(r'\*\*Overall:\*\*\s*(\d+)%', content)
            if match:
                data["progress_pct"] = int(match.group(1))
        
        # Extract tags
        tags = []
        for line in content.split("\n"):
            if line.startswith("#") and not line.startswith("# ") and not line.startswith("##"):
                tags.extend([tag.strip() for tag in line.split() if tag.startswith("#")])
        if tags:
            data["tags"] = json.dumps(tags)
        
        # Generate title from focus or objective
        data["title"] = data.get("focus") or data.get("objective") or f"Conversation {convo_id}"
        
        return data
    
    def sync_conversation(self, convo_id: str) -> bool:
        """Sync a single conversation to the database."""
        data = self.parse_session_state(convo_id)
        
        if not data:
            print(f"✗ No SESSION_STATE.md found for {convo_id}", file=sys.stderr)
            return False
        
        # Check if conversation exists
        cursor = self.conn.execute("SELECT id FROM conversations WHERE id = ?", (convo_id,))
        exists = cursor.fetchone() is not None
        
        if exists:
            # Update existing
            self.conn.execute("""
                UPDATE conversations
                SET title = ?, type = ?, status = ?, mode = ?,
                    updated_at = ?, focus = ?, objective = ?, tags = ?,
                    progress_pct = ?, workspace_path = ?, state_file_path = ?
                WHERE id = ?
            """, (
                data.get("title"),
                data.get("type"),
                data.get("status"),
                data.get("mode"),
                data.get("updated_at"),
                data.get("focus"),
                data.get("objective"),
                data.get("tags"),
                data.get("progress_pct", 0),
                data.get("workspace_path"),
                data.get("state_file_path"),
                convo_id
            ))
            action = "Updated"
        else:
            # Insert new
            self.conn.execute("""
                INSERT INTO conversations 
                (id, title, type, status, mode, created_at, updated_at,
                 focus, objective, tags, progress_pct, workspace_path, state_file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("id"),
                data.get("title"),
                data.get("type"),
                data.get("status"),
                data.get("mode"),
                data.get("created_at"),
                data.get("updated_at"),
                data.get("focus"),
                data.get("objective"),
                data.get("tags"),
                data.get("progress_pct", 0),
                data.get("workspace_path"),
                data.get("state_file_path")
            ))
            action = "Inserted"
        
        self.conn.commit()
        print(f"✓ {action} {convo_id} → conversations.db")
        return True
    
    def sync_all(self) -> int:
        """Sync all conversations with SESSION_STATE.md files."""
        count = 0
        
        if not self.WORKSPACE_BASE.exists():
            print(f"✗ Workspace base not found: {self.WORKSPACE_BASE}", file=sys.stderr)
            return 0
        
        for workspace in self.WORKSPACE_BASE.iterdir():
            if workspace.is_dir() and workspace.name.startswith("con_"):
                convo_id = workspace.name
                session_state = workspace / "SESSION_STATE.md"
                
                if session_state.exists():
                    if self.sync_conversation(convo_id):
                        count += 1
        
        print(f"\n✓ Synced {count} conversations to database")
        return count
    
    def query(self, type: str = None, status: str = None, starred: bool = None) -> List[Dict]:
        """Query conversations from database."""
        query = "SELECT * FROM conversations WHERE 1=1"
        params = []
        
        if type:
            query += " AND type = ?"
            params.append(type)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if starred is not None:
            query += " AND starred = ?"
            params.append(1 if starred else 0)
        
        query += " ORDER BY updated_at DESC"
        
        cursor = self.conn.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        return results
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(description="Sync SESSION_STATE.md to conversations.db")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Sync single conversation
    sync_parser = subparsers.add_parser("sync", help="Sync single conversation")
    sync_parser.add_argument("--convo-id", required=True, help="Conversation ID")
    
    # Sync all conversations
    subparsers.add_parser("sync-all", help="Sync all conversations")
    
    # Query conversations
    query_parser = subparsers.add_parser("query", help="Query conversations")
    query_parser.add_argument("--type", help="Filter by type")
    query_parser.add_argument("--status", help="Filter by status")
    query_parser.add_argument("--starred", action="store_true", help="Only starred")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    syncer = ConversationSync()
    
    try:
        if args.command == "sync":
            success = syncer.sync_conversation(args.convo_id)
            sys.exit(0 if success else 1)
        
        elif args.command == "sync-all":
            count = syncer.sync_all()
            sys.exit(0 if count > 0 else 1)
        
        elif args.command == "query":
            results = syncer.query(
                type=args.type,
                status=args.status,
                starred=args.starred if args.starred else None
            )
            
            if results:
                print(f"\nFound {len(results)} conversations:\n")
                for conv in results:
                    print(f"• {conv['id']}: {conv['title']}")
                    print(f"  Type: {conv['type']} | Status: {conv['status']} | Progress: {conv['progress_pct']}%")
                    if conv['focus']:
                        print(f"  Focus: {conv['focus']}")
                    print()
            else:
                print("No conversations found matching criteria")
            
            sys.exit(0)
    
    finally:
        syncer.close()


if __name__ == "__main__":
    main()

