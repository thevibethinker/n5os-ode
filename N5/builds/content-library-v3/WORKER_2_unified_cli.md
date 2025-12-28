---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
---

# Worker 2: Unified CLI & API

**Orchestrator:** con_jYGYNfcv76UTmolk  
**Task ID:** W2-CLI-API  
**Estimated Time:** 45 minutes  
**Dependencies:** Worker 1 (schema + migration must be complete)

---

## Mission

Create a unified CLI and Python API for the Content Library v3 that supports ALL item types (links, snippets, articles, decks, social posts) with a single interface.

---

## Context

Currently there are two separate CLIs:
1. `N5/scripts/content_library.py` – for links/snippets
2. `Personal/Knowledge/ContentLibrary/scripts/ingest.py` – for articles/assets

This worker creates ONE CLI that handles everything.

**Design doc:** `file 'N5/builds/content-library-v3/CONTENT_LIBRARY_V3_ARCHITECTURE.md'`

---

## Dependencies

- Worker 1 complete: `content-library-v3.db` exists with migrated data

---

## Deliverables

1. `Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py` – Unified CLI + API
2. `N5/scripts/content_library.py.new` – Thin wrapper pointing to v3 (backwards compat)

---

## Requirements

### CLI Commands

```bash
# Search (unified across all types)
python3 content_library_v3.py search --query "calendly"
python3 content_library_v3.py search --type link --tag category=scheduling
python3 content_library_v3.py search --type article --topic "AI"

# Get by ID
python3 content_library_v3.py get <id>

# Add new item
python3 content_library_v3.py add --type link --id my_link --title "My Link" --url "https://..."
python3 content_library_v3.py add --type snippet --id my_bio --title "Bio" --content "..."
python3 content_library_v3.py add --type article --id my_article --title "Article" --url "https://..." --topic AI

# Ingest (for assets with content storage)
python3 content_library_v3.py ingest --url "https://..." --type article --title "Title" --source created

# Update
python3 content_library_v3.py update <id> --title "New Title" --url "https://new..."

# Deprecate
python3 content_library_v3.py deprecate <id>

# List
python3 content_library_v3.py list --type link --limit 20
python3 content_library_v3.py list --type article

# Export
python3 content_library_v3.py export --type link --format json
python3 content_library_v3.py export --type article --format markdown

# Stats
python3 content_library_v3.py stats

# Lint (check for JS shell issues, broken content)
python3 content_library_v3.py lint
```

### Python API

```python
from content_library_v3 import ContentLibraryV3

lib = ContentLibraryV3()

# Search
items = lib.search(query="calendly")
items = lib.search(item_type="link", tags={"category": "scheduling"})
items = lib.search(item_type="article", topics=["AI"])

# Get
item = lib.get("my_link")

# Add
lib.add(
    id="new_link",
    item_type="link",
    title="New Link",
    url="https://...",
    tags={"category": "product"}
)

# Ingest asset (downloads/stores content)
lib.ingest(
    url="https://...",
    item_type="article",
    title="Article Title",
    source_type="discovered"
)

# Update
lib.update("my_link", url="https://new...")

# Deprecate
lib.deprecate("old_item")

# Mark used
lib.mark_used("my_link")

# Stats
stats = lib.stats()  # Returns dict with counts by type, source, etc.
```

---

## Implementation Guide

```python
#!/usr/bin/env python3
"""
content_library_v3.py - Unified Content Library CLI & API
Supports: links, snippets, articles, decks, social-posts, podcasts, etc.

Database: /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db
"""
import argparse
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")

DB_PATH = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db")
CONTENT_DIR = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content")

class ContentLibraryV3:
    """Unified Content Library API"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self):
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
    
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def search(
        self,
        query: Optional[str] = None,
        item_type: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        topics: Optional[List[str]] = None,
        include_deprecated: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """Search items by query, type, tags, or topics"""
        conn = self._connect()
        
        sql = "SELECT DISTINCT i.* FROM items i"
        joins = []
        conditions = []
        params = []
        
        # Join tags if filtering by tag
        if tags:
            for i, (key, value) in enumerate(tags.items()):
                alias = f"t{i}"
                joins.append(f"JOIN tags {alias} ON i.id = {alias}.item_id")
                conditions.append(f"{alias}.tag_key = ? AND {alias}.tag_value = ?")
                params.extend([key, value])
        
        # Join topics if filtering by topic
        if topics:
            joins.append("JOIN item_topics it ON i.id = it.item_id")
            joins.append("JOIN topics tp ON it.topic_id = tp.id")
            placeholders = ",".join("?" * len(topics))
            conditions.append(f"tp.name IN ({placeholders})")
            params.extend(topics)
        
        # Text search
        if query:
            conditions.append("(i.title LIKE ? OR i.content LIKE ? OR i.url LIKE ?)")
            like_query = f"%{query}%"
            params.extend([like_query, like_query, like_query])
        
        # Type filter
        if item_type:
            conditions.append("i.item_type = ?")
            params.append(item_type)
        
        # Deprecated filter
        if not include_deprecated:
            conditions.append("i.deprecated = 0")
        
        # Build query
        if joins:
            sql += " " + " ".join(joins)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += f" ORDER BY i.updated_at DESC LIMIT {limit}"
        
        cursor = conn.execute(sql, params)
        results = []
        for row in cursor:
            item = dict(row)
            # Add tags
            item['tags'] = self._get_tags(conn, item['id'])
            # Add topics
            item['topics'] = self._get_topics(conn, item['id'])
            results.append(item)
        
        conn.close()
        return results
    
    def _get_tags(self, conn, item_id: str) -> Dict[str, List[str]]:
        cursor = conn.execute(
            "SELECT tag_key, tag_value FROM tags WHERE item_id = ?",
            (item_id,)
        )
        tags = {}
        for row in cursor:
            tags.setdefault(row['tag_key'], []).append(row['tag_value'])
        return tags
    
    def _get_topics(self, conn, item_id: str) -> List[str]:
        cursor = conn.execute("""
            SELECT t.name FROM topics t
            JOIN item_topics it ON t.id = it.topic_id
            WHERE it.item_id = ?
        """, (item_id,))
        return [row['name'] for row in cursor]
    
    def get(self, item_id: str) -> Optional[Dict]:
        """Get single item by ID"""
        conn = self._connect()
        cursor = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        item = dict(row)
        item['tags'] = self._get_tags(conn, item_id)
        item['topics'] = self._get_topics(conn, item_id)
        conn.close()
        return item
    
    def add(
        self,
        id: str,
        item_type: str,
        title: str,
        url: Optional[str] = None,
        content: Optional[str] = None,
        content_path: Optional[str] = None,
        source_type: str = "manual",
        platform: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        topics: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """Add new item"""
        conn = self._connect()
        now = datetime.now().isoformat()
        
        conn.execute("""
            INSERT INTO items (id, item_type, title, url, content, content_path,
                               source_type, platform, author, created_at, updated_at,
                               notes, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new')
        """, (id, item_type, title, url, content, content_path, source_type,
              platform, author, now, now, notes))
        
        # Add tags
        if tags:
            for key, value in tags.items():
                conn.execute(
                    "INSERT INTO tags (item_id, tag_key, tag_value) VALUES (?, ?, ?)",
                    (id, key, value)
                )
        
        # Add topics
        if topics:
            for topic_name in topics:
                conn.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic_name,))
                topic_id = conn.execute(
                    "SELECT id FROM topics WHERE name = ?", (topic_name,)
                ).fetchone()[0]
                conn.execute(
                    "INSERT INTO item_topics (item_id, topic_id) VALUES (?, ?)",
                    (id, topic_id)
                )
        
        conn.commit()
        conn.close()
        
        logging.info(f"Added item: {id}")
        return self.get(id)
    
    def update(self, item_id: str, **fields) -> Optional[Dict]:
        """Update item fields"""
        conn = self._connect()
        
        # Check exists
        if not conn.execute("SELECT 1 FROM items WHERE id = ?", (item_id,)).fetchone():
            conn.close()
            return None
        
        # Build update
        allowed = ['title', 'url', 'content', 'content_path', 'summary', 'summary_path',
                   'platform', 'author', 'notes', 'deprecated', 'expires_at']
        updates = []
        params = []
        for key, value in fields.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(item_id)
            
            conn.execute(f"UPDATE items SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
        
        conn.close()
        logging.info(f"Updated item: {item_id}")
        return self.get(item_id)
    
    def deprecate(self, item_id: str) -> bool:
        """Mark item as deprecated"""
        return self.update(item_id, deprecated=1) is not None
    
    def mark_used(self, item_id: str) -> bool:
        """Update last_used_at timestamp"""
        conn = self._connect()
        conn.execute(
            "UPDATE items SET last_used_at = ? WHERE id = ?",
            (datetime.now().isoformat(), item_id)
        )
        conn.commit()
        conn.close()
        return True
    
    def stats(self) -> Dict:
        """Get library statistics"""
        conn = self._connect()
        
        stats = {
            'total': conn.execute("SELECT COUNT(*) FROM items").fetchone()[0],
            'by_type': {},
            'by_source': {},
            'topics': conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0],
            'tags': conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0],
            'deprecated': conn.execute("SELECT COUNT(*) FROM items WHERE deprecated=1").fetchone()[0]
        }
        
        for row in conn.execute("SELECT item_type, COUNT(*) as c FROM items GROUP BY item_type"):
            stats['by_type'][row['item_type']] = row['c']
        
        for row in conn.execute("SELECT source, COUNT(*) as c FROM items GROUP BY source"):
            stats['by_source'][row['source']] = row['c']
        
        conn.close()
        return stats
    
    def lint(self) -> List[Dict]:
        """Check for quality issues"""
        issues = []
        conn = self._connect()
        
        # Check for JS shell content
        js_shell_markers = ["JavaScript is not available", "enable JavaScript"]
        for marker in js_shell_markers:
            cursor = conn.execute(
                "SELECT id, title FROM items WHERE content LIKE ?",
                (f"%{marker}%",)
            )
            for row in cursor:
                issues.append({
                    'id': row['id'],
                    'title': row['title'],
                    'issue': 'JS shell content detected'
                })
        
        # Check content files exist
        cursor = conn.execute("SELECT id, title, content_path FROM items WHERE content_path IS NOT NULL")
        for row in cursor:
            if row['content_path'] and not Path(row['content_path']).exists():
                issues.append({
                    'id': row['id'],
                    'title': row['title'],
                    'issue': f"Content file missing: {row['content_path']}"
                })
        
        conn.close()
        return issues


def main():
    parser = argparse.ArgumentParser(description="Content Library v3 CLI")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Search
    search_p = subparsers.add_parser('search', help='Search items')
    search_p.add_argument('--query', '-q', help='Text search')
    search_p.add_argument('--type', '-t', help='Item type filter')
    search_p.add_argument('--tag', action='append', help='Tag filter (key=value)')
    search_p.add_argument('--topic', action='append', help='Topic filter')
    search_p.add_argument('--include-deprecated', action='store_true')
    search_p.add_argument('--limit', type=int, default=50)
    
    # Get
    get_p = subparsers.add_parser('get', help='Get item by ID')
    get_p.add_argument('id', help='Item ID')
    
    # Add
    add_p = subparsers.add_parser('add', help='Add new item')
    add_p.add_argument('--id', required=True)
    add_p.add_argument('--type', required=True, dest='item_type')
    add_p.add_argument('--title', required=True)
    add_p.add_argument('--url')
    add_p.add_argument('--content')
    add_p.add_argument('--tag', action='append', help='Tag (key=value)')
    add_p.add_argument('--topic', action='append')
    add_p.add_argument('--notes')
    
    # Update
    update_p = subparsers.add_parser('update', help='Update item')
    update_p.add_argument('id')
    update_p.add_argument('--title')
    update_p.add_argument('--url')
    update_p.add_argument('--content')
    update_p.add_argument('--notes')
    
    # Deprecate
    dep_p = subparsers.add_parser('deprecate', help='Deprecate item')
    dep_p.add_argument('id')
    
    # List
    list_p = subparsers.add_parser('list', help='List items')
    list_p.add_argument('--type', '-t')
    list_p.add_argument('--limit', type=int, default=20)
    
    # Stats
    subparsers.add_parser('stats', help='Show statistics')
    
    # Lint
    subparsers.add_parser('lint', help='Check for quality issues')
    
    args = parser.parse_args()
    lib = ContentLibraryV3()
    
    if args.command == 'search':
        tags = {}
        if args.tag:
            for t in args.tag:
                k, v = t.split('=', 1)
                tags[k] = v
        
        results = lib.search(
            query=args.query,
            item_type=args.type,
            tags=tags or None,
            topics=args.topic,
            include_deprecated=args.include_deprecated,
            limit=args.limit
        )
        print(json.dumps(results, indent=2, default=str))
    
    elif args.command == 'get':
        item = lib.get(args.id)
        if item:
            print(json.dumps(item, indent=2, default=str))
        else:
            print(json.dumps({"error": "Not found"}))
    
    elif args.command == 'add':
        tags = {}
        if args.tag:
            for t in args.tag:
                k, v = t.split('=', 1)
                tags[k] = v
        
        item = lib.add(
            id=args.id,
            item_type=args.item_type,
            title=args.title,
            url=args.url,
            content=args.content,
            tags=tags or None,
            topics=args.topic,
            notes=args.notes
        )
        print(json.dumps(item, indent=2, default=str))
    
    elif args.command == 'update':
        updates = {}
        if args.title: updates['title'] = args.title
        if args.url: updates['url'] = args.url
        if args.content: updates['content'] = args.content
        if args.notes: updates['notes'] = args.notes
        
        item = lib.update(args.id, **updates)
        if item:
            print(json.dumps(item, indent=2, default=str))
        else:
            print(json.dumps({"error": "Not found"}))
    
    elif args.command == 'deprecate':
        success = lib.deprecate(args.id)
        print(json.dumps({"success": success, "id": args.id}))
    
    elif args.command == 'list':
        results = lib.search(item_type=args.type, limit=args.limit)
        for item in results:
            print(f"[{item['item_type']}] {item['id']}: {item['title']}")
    
    elif args.command == 'stats':
        stats = lib.stats()
        print(json.dumps(stats, indent=2))
    
    elif args.command == 'lint':
        issues = lib.lint()
        if issues:
            print(f"Found {len(issues)} issue(s):")
            for issue in issues:
                print(f"  - {issue['id']}: {issue['issue']}")
        else:
            print("No issues found.")


if __name__ == "__main__":
    main()
```

---

## Testing

```bash
# Search for calendly links
python3 content_library_v3.py search --query "calendly"

# Search by type
python3 content_library_v3.py search --type article

# Get specific item
python3 content_library_v3.py get trial_code_general

# Add new item
python3 content_library_v3.py add --id test_item --type link --title "Test" --url "https://test.com"

# Stats
python3 content_library_v3.py stats

# Lint
python3 content_library_v3.py lint

# List all links
python3 content_library_v3.py list --type link --limit 10
```

---

## Report Back

When complete, report:
1. ✅ CLI created at path
2. ✅ All commands working
3. ✅ API importable
4. ✅ Backwards compat wrapper created
5. ✅ Test results

---

**Orchestrator Contact:** con_jYGYNfcv76UTmolk  
**Created:** 2025-12-02 22:00 ET

