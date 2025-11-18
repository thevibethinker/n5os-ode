#!/usr/bin/env python3
"""
Content Library Manager - Database Edition
Manages links and snippets for emails, documents, and communications
Database: N5/data/content_library.db
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path("/home/workspace/N5/data/content_library.db")


def get_connection():
    """Get database connection"""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    return sqlite3.connect(DB_PATH)


def search(query: str, item_type: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict]:
    """
    Search content library by keyword, type, or tags
    
    Args:
        query: Search term (searches title, content, url)
        item_type: Filter by type ('link' or 'snippet')
        tags: Filter by tag values
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = """
        SELECT DISTINCT i.* 
        FROM items i
        LEFT JOIN tags t ON i.id = t.item_id
        WHERE i.deprecated = 0
    """
    params = []
    
    if query:
        sql += " AND (i.title LIKE ? OR i.content LIKE ? OR i.url LIKE ? OR i.id LIKE ?)"
        search_term = f"%{query}%"
        params.extend([search_term, search_term, search_term, search_term])
    
    if item_type:
        sql += " AND i.type = ?"
        params.append(item_type)
    
    if tags:
        placeholders = ",".join(["?" for _ in tags])
        sql += f" AND t.tag_value IN ({placeholders})"
        params.extend(tags)
    
    sql += " ORDER BY i.last_used_at DESC, i.title ASC"
    
    cursor.execute(sql, params)
    results = []
    
    for row in cursor.fetchall():
        item = dict(row)
        
        # Get tags for this item
        cursor.execute("SELECT tag_key, tag_value FROM tags WHERE item_id = ?", (item['id'],))
        item['tags'] = {}
        for tag_row in cursor.fetchall():
            key, value = tag_row
            if key not in item['tags']:
                item['tags'][key] = []
            item['tags'][key].append(value)
        
        results.append(item)
    
    conn.close()
    return results


def get_by_id(item_id: str) -> Optional[Dict]:
    """Get item by ID"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    item = dict(row)
    
    # Get tags
    cursor.execute("SELECT tag_key, tag_value FROM tags WHERE item_id = ?", (item_id,))
    item['tags'] = {}
    for tag_row in cursor.fetchall():
        key, value = tag_row
        if key not in item['tags']:
            item['tags'][key] = []
        item['tags'][key].append(value)
    
    conn.close()
    return item


def get_links_for_context(context: str, categories: Optional[List[str]] = None) -> List[Dict]:
    """
    Smart link retrieval based on context/commitments
    
    Args:
        context: Text describing what was promised (e.g., "trial link", "calendar", "demo")
        categories: Optional category filters
    
    Returns:
        List of matching link items
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build search query
    keywords = context.lower().split()
    
    sql = """
        SELECT DISTINCT i.* 
        FROM items i
        LEFT JOIN tags t ON i.id = t.item_id
        WHERE i.deprecated = 0 AND i.type = 'link'
    """
    params = []
    
    # Match keywords in title, content, tags
    if keywords:
        conditions = []
        for keyword in keywords:
            conditions.append("(i.title LIKE ? OR i.content LIKE ? OR t.tag_value LIKE ?)")
            search_term = f"%{keyword}%"
            params.extend([search_term, search_term, search_term])
        
        sql += " AND (" + " OR ".join(conditions) + ")"
    
    if categories:
        placeholders = ",".join(["?" for _ in categories])
        sql += f" AND t.tag_key = 'category' AND t.tag_value IN ({placeholders})"
        params.extend(categories)
    
    sql += " ORDER BY i.last_used_at DESC, i.title ASC LIMIT 10"
    
    cursor.execute(sql, params)
    results = []
    
    for row in cursor.fetchall():
        item = dict(row)
        cursor.execute("SELECT tag_key, tag_value FROM tags WHERE item_id = ?", (item['id'],))
        item['tags'] = {}
        for tag_row in cursor.fetchall():
            key, value = tag_row
            if key not in item['tags']:
                item['tags'][key] = []
            item['tags'][key].append(value)
        results.append(item)
    
    conn.close()
    return results


def mark_used(item_id: str):
    """Mark item as used (updates last_used_at timestamp)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE items SET last_used_at = ? WHERE id = ?",
        (datetime.now().isoformat(), item_id)
    )
    conn.commit()
    conn.close()


def list_all(item_type: Optional[str] = None, category: Optional[str] = None):
    """List all items"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = "SELECT * FROM items WHERE deprecated = 0"
    params = []
    
    if item_type:
        sql += " AND type = ?"
        params.append(item_type)
    
    if category:
        sql += """ AND id IN (
            SELECT item_id FROM tags 
            WHERE tag_key = 'category' AND tag_value = ?
        )"""
        params.append(category)
    
    sql += " ORDER BY type, title"
    
    cursor.execute(sql, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def main():
    parser = argparse.ArgumentParser(description="Content Library Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search library")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--type", choices=["link", "snippet"], help="Filter by type")
    search_parser.add_argument("--tags", nargs="+", help="Filter by tags")
    
    # Get by ID
    get_parser = subparsers.add_parser("get", help="Get item by ID")
    get_parser.add_argument("id", help="Item ID")
    
    # Get for context
    context_parser = subparsers.add_parser("context", help="Get links for context/promise")
    context_parser.add_argument("text", help="Context description")
    context_parser.add_argument("--categories", nargs="+", help="Category filters")
    
    # List
    list_parser = subparsers.add_parser("list", help="List all items")
    list_parser.add_argument("--type", choices=["link", "snippet"], help="Filter by type")
    list_parser.add_argument("--category", help="Filter by category")
    
    # Mark used
    used_parser = subparsers.add_parser("mark-used", help="Mark item as used")
    used_parser.add_argument("id", help="Item ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "search":
            results = search(args.query, args.type, args.tags)
            print(json.dumps(results, indent=2))
        
        elif args.command == "get":
            result = get_by_id(args.id)
            if result:
                print(json.dumps(result, indent=2))
            else:
                print(f"Item not found: {args.id}", file=sys.stderr)
                sys.exit(1)
        
        elif args.command == "context":
            results = get_links_for_context(args.text, args.categories)
            print(json.dumps(results, indent=2))
        
        elif args.command == "list":
            results = list_all(args.type, args.category)
            print(json.dumps(results, indent=2))
        
        elif args.command == "mark-used":
            mark_used(args.id)
            print(f"✓ Marked {args.id} as used")
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

