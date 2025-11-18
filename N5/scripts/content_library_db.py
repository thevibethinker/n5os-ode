#!/usr/bin/env python3
"""
Content Library (Database Version)
- SQLite-backed SSOT for links and reusable text snippets
- CLI + importable API

Database: /home/workspace/N5/data/content_library.db

Usage examples:
  # Search for links/snippets
  python3 N5/scripts/content_library_db.py search --query "calendly" --tag purpose=scheduling
  
  # Get specific item
  python3 N5/scripts/content_library_db.py get --id trial_code_general
  
  # Add new link
  python3 N5/scripts/content_library_db.py add --type link --title "New Link" --url "https://example.com" --tag category=test
  
  # Add new snippet
  python3 N5/scripts/content_library_db.py add --type snippet --title "Email Signature" --content "Best regards, V"
  
  # List all items
  python3 N5/scripts/content_library_db.py list --limit 10
  
  # Deprecate an item
  python3 N5/scripts/content_library_db.py deprecate --id old_link
"""

import argparse
import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("content_library_db")

DB_PATH = Path("/home/workspace/N5/data/content_library.db")


class ContentLibraryDB:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        
    def close(self):
        self.conn.close()
    
    def _now_iso(self) -> str:
        return datetime.now().isoformat()
    
    def add_item(
        self,
        item_id: str,
        item_type: str,
        title: str,
        content: Optional[str] = None,
        url: Optional[str] = None,
        tags: Optional[Dict[str, List[str]]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add or update an item in the database."""
        cursor = self.conn.cursor()
        
        # For links, content should equal url
        if item_type == "link" and url:
            content = url
        
        cursor.execute("""
            INSERT OR REPLACE INTO items 
            (id, type, title, content, url, created_at, updated_at, version, notes, source)
            VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'), 1, ?, 'manual')
        """, (item_id, item_type, title, content, url, notes))
        
        # Add tags
        if tags:
            for tag_key, tag_values in tags.items():
                if isinstance(tag_values, list):
                    for tag_value in tag_values:
                        cursor.execute("""
                            INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value)
                            VALUES (?, ?, ?)
                        """, (item_id, tag_key, tag_value))
        
        self.conn.commit()
        return self.get_item(item_id)
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific item by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        item = dict(row)
        
        # Get tags
        cursor.execute("SELECT tag_key, tag_value FROM tags WHERE item_id = ?", (item_id,))
        tags_rows = cursor.fetchall()
        tags = {}
        for tag_row in tags_rows:
            key = tag_row["tag_key"]
            value = tag_row["tag_value"]
            if key not in tags:
                tags[key] = []
            tags[key].append(value)
        
        item["tags"] = tags
        return item
    
    def search_items(
        self,
        query: Optional[str] = None,
        tag_filters: Optional[Dict[str, List[str]]] = None,
        item_type: Optional[str] = None,
        include_deprecated: bool = False,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for items with optional filters."""
        cursor = self.conn.cursor()
        
        sql = "SELECT DISTINCT items.* FROM items"
        params = []
        where_clauses = []
        
        # Join with tags if needed
        if tag_filters:
            for tag_key, tag_values in tag_filters.items():
                sql += f"""
                    INNER JOIN tags t_{tag_key} ON items.id = t_{tag_key}.item_id 
                    AND t_{tag_key}.tag_key = ? 
                    AND t_{tag_key}.tag_value IN ({','.join('?' * len(tag_values))})
                """
                params.append(tag_key)
                params.extend(tag_values)
        
        # Text search
        if query:
            where_clauses.append("(title LIKE ? OR content LIKE ? OR url LIKE ?)")
            search_term = f"%{query}%"
            params.extend([search_term, search_term, search_term])
        
        # Type filter
        if item_type:
            where_clauses.append("type = ?")
            params.append(item_type)
        
        # Deprecated filter
        if not include_deprecated:
            where_clauses.append("deprecated = 0")
        
        # Expiration filter
        where_clauses.append("(expires_at IS NULL OR datetime(expires_at) > datetime('now'))")
        
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        
        sql += " ORDER BY updated_at DESC"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            item = dict(row)
            
            # Get tags for this item
            cursor.execute("SELECT tag_key, tag_value FROM tags WHERE item_id = ?", (item["id"],))
            tags_rows = cursor.fetchall()
            tags = {}
            for tag_row in tags_rows:
                key = tag_row["tag_key"]
                value = tag_row["tag_value"]
                if key not in tags:
                    tags[key] = []
                tags[key].append(value)
            
            item["tags"] = tags
            results.append(item)
        
        return results
    
    def deprecate_item(self, item_id: str, expires_at: Optional[str] = None) -> bool:
        """Mark an item as deprecated."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE items 
            SET deprecated = 1, expires_at = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (expires_at, item_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def list_items(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List all items with pagination."""
        return self.search_items(limit=limit, include_deprecated=False)


def parse_tag_args(tag_list: Optional[List[str]]) -> Dict[str, List[str]]:
    """Parse tag arguments in format key=value."""
    tags = {}
    if not tag_list:
        return tags
    
    for tag_str in tag_list:
        if "=" in tag_str:
            key, value = tag_str.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key not in tags:
                tags[key] = []
            tags[key].append(value)
    
    return tags


def main():
    parser = argparse.ArgumentParser(description="Content Library (Database Version)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # search command
    p_search = subparsers.add_parser("search", help="Search for items")
    p_search.add_argument("--query", type=str, help="Text search query")
    p_search.add_argument("--tag", action="append", help="Tag filter (key=value)")
    p_search.add_argument("--type", choices=["link", "snippet"], help="Item type filter")
    p_search.add_argument("--limit", type=int, default=50, help="Max results")
    p_search.add_argument("--include-deprecated", action="store_true", help="Include deprecated items")
    
    # get command
    p_get = subparsers.add_parser("get", help="Get specific item by ID")
    p_get.add_argument("--id", required=True, help="Item ID")
    
    # add command
    p_add = subparsers.add_parser("add", help="Add new item")
    p_add.add_argument("--id", required=True, help="Item ID")
    p_add.add_argument("--type", required=True, choices=["link", "snippet"], help="Item type")
    p_add.add_argument("--title", required=True, help="Item title")
    p_add.add_argument("--content", help="Content (for snippets)")
    p_add.add_argument("--url", help="URL (for links)")
    p_add.add_argument("--tag", action="append", help="Tag (key=value)")
    p_add.add_argument("--notes", help="Optional notes")
    
    # list command
    p_list = subparsers.add_parser("list", help="List all items")
    p_list.add_argument("--limit", type=int, default=50, help="Max results")
    
    # deprecate command
    p_deprecate = subparsers.add_parser("deprecate", help="Deprecate an item")
    p_deprecate.add_argument("--id", required=True, help="Item ID")
    p_deprecate.add_argument("--expires-at", help="Expiration date (ISO format)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    db = ContentLibraryDB()
    
    try:
        if args.command == "search":
            tag_filters = parse_tag_args(args.tag) if args.tag else None
            results = db.search_items(
                query=args.query,
                tag_filters=tag_filters,
                item_type=args.type,
                include_deprecated=args.include_deprecated,
                limit=args.limit
            )
            print(json.dumps({"count": len(results), "items": results}, indent=2))
            return 0
        
        elif args.command == "get":
            item = db.get_item(args.id)
            if item:
                print(json.dumps(item, indent=2))
                return 0
            else:
                print(json.dumps({"error": "Item not found", "id": args.id}))
                return 1
        
        elif args.command == "add":
            tags = parse_tag_args(args.tag) if args.tag else None
            item = db.add_item(
                item_id=args.id,
                item_type=args.type,
                title=args.title,
                content=args.content,
                url=args.url,
                tags=tags,
                notes=args.notes
            )
            print(json.dumps(item, indent=2))
            logger.info(f"✓ Added {args.type}: {args.title}")
            return 0
        
        elif args.command == "list":
            results = db.list_items(limit=args.limit)
            print(json.dumps({"count": len(results), "items": results}, indent=2))
            return 0
        
        elif args.command == "deprecate":
            success = db.deprecate_item(args.id, args.expires_at)
            if success:
                logger.info(f"✓ Deprecated: {args.id}")
                print(json.dumps({"success": True, "id": args.id}))
                return 0
            else:
                print(json.dumps({"error": "Item not found", "id": args.id}))
                return 1
    
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

