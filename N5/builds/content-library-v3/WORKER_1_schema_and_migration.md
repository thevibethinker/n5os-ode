---
created: 2025-12-02
last_edited: 2025-12-02
version: 1
---
# Worker 1: Schema Creation & Data Migration

**Orchestrator:** con_jYGYNfcv76UTmolk  
**Task ID:** W1-SCHEMA-MIGRATION  
**Estimated Time:** 45 minutes  
**Dependencies:** None (can start immediately)

---

## Mission

Create the unified Content Library v3 SQLite database with the merged schema and migrate all data from both existing databases.

---

## Context

Two separate "Content Library" systems currently exist:
1. **N5 Links DB** (`N5/data/content_library.db`) – 67 items (links, snippets)
2. **Personal CL DB** (`Personal/Knowledge/ContentLibrary/content-library.db`) – 16 items (articles, posts)

This worker creates a unified database that holds ALL content types.

**Design doc:** `file 'N5/builds/content-library-v3/CONTENT_LIBRARY_V3_ARCHITECTURE.md'`

---

## Dependencies

None – this is the foundational worker.

---

## Deliverables

1. `Personal/Knowledge/ContentLibrary/content-library-v3.db` – New unified database
2. `Personal/Knowledge/ContentLibrary/scripts/migrate_to_v3.py` – Migration script
3. `Personal/schemas/content-library-v3.schema.json` – JSON schema for validation
4. Migration report showing item counts

---

## Requirements

### Schema (from architecture doc)

```sql
CREATE TABLE items (
    id TEXT PRIMARY KEY,
    item_type TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    content TEXT,
    content_path TEXT,
    summary TEXT,
    summary_path TEXT,
    word_count INTEGER,
    source_type TEXT NOT NULL DEFAULT 'manual',
    platform TEXT,
    author TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    deprecated INTEGER NOT NULL DEFAULT 0,
    expires_at TEXT,
    last_used_at TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    confidence INTEGER DEFAULT 3,
    has_content INTEGER DEFAULT 0,
    has_summary INTEGER DEFAULT 0,
    notes TEXT,
    source TEXT
);

CREATE TABLE tags (
    item_id TEXT NOT NULL,
    tag_key TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    PRIMARY KEY (item_id, tag_key, tag_value),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE item_topics (
    item_id TEXT NOT NULL,
    topic_id INTEGER NOT NULL,
    PRIMARY KEY (item_id, topic_id),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE blocks (
    id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL,
    block_code TEXT,
    block_type TEXT,
    content TEXT NOT NULL,
    context TEXT,
    speaker TEXT,
    file_path TEXT,
    line_start INTEGER,
    line_end INTEGER,
    extracted_at TEXT,
    confidence INTEGER DEFAULT 3,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

CREATE TABLE block_topics (
    block_id TEXT NOT NULL,
    topic_id INTEGER NOT NULL,
    PRIMARY KEY (block_id, topic_id),
    FOREIGN KEY (block_id) REFERENCES blocks(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE knowledge_refs (
    block_id TEXT PRIMARY KEY,
    knowledge_type TEXT,
    knowledge_id TEXT,
    source_type TEXT,
    source_id TEXT,
    promoted_at TEXT,
    notes TEXT,
    FOREIGN KEY (block_id) REFERENCES blocks(id)
);

CREATE TABLE relationships (
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (from_id, to_id, rel_type),
    FOREIGN KEY (from_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (to_id) REFERENCES items(id) ON DELETE CASCADE
);

CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_items_type ON items(item_type);
CREATE INDEX idx_items_source_type ON items(source_type);
CREATE INDEX idx_items_deprecated ON items(deprecated);
CREATE INDEX idx_items_title ON items(title COLLATE NOCASE);
CREATE INDEX idx_items_updated ON items(updated_at DESC);
CREATE INDEX idx_tags_key_value ON tags(tag_key, tag_value);
CREATE INDEX idx_blocks_item ON blocks(item_id);
```

### Migration Logic

**From N5 DB:**
- `type` → `item_type` (link, snippet)
- `content` → `url` (for links) or `content` (for snippets)
- `source` field = 'n5_links'
- Preserve all tags

**From Personal CL DB:**
- Map `source_type` (article, social-post, etc.) → `item_type`
- `source` field = 'personal_cl'
- Preserve topics (create in topics table, link via item_topics)
- Preserve blocks if any exist

**ID Collision Handling:**
- If same ID exists in both, prefix with source: `n5_<id>` or `pcl_<id>`

---

## Implementation Guide

```python
#!/usr/bin/env python3
"""
migrate_to_v3.py - Migrate both content libraries to unified v3
"""
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")

N5_DB = Path("/home/workspace/N5/data/content_library.db")
PERSONAL_DB = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library.db")
V3_DB = Path("/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db")

SCHEMA_SQL = """
-- [paste full schema here]
"""

def create_v3_database():
    """Create fresh v3 database with schema"""
    if V3_DB.exists():
        backup = V3_DB.with_suffix('.db.backup')
        V3_DB.rename(backup)
        logging.info(f"Backed up existing v3 db to {backup}")
    
    conn = sqlite3.connect(V3_DB)
    conn.executescript(SCHEMA_SQL)
    conn.execute("INSERT INTO schema_version (version) VALUES (3)")
    conn.commit()
    logging.info(f"Created v3 database at {V3_DB}")
    return conn

def migrate_n5_items(v3_conn):
    """Migrate items from N5 content_library.db"""
    if not N5_DB.exists():
        logging.warning(f"N5 DB not found at {N5_DB}")
        return 0
    
    n5_conn = sqlite3.connect(N5_DB)
    n5_conn.row_factory = sqlite3.Row
    
    cursor = n5_conn.execute("SELECT * FROM items")
    count = 0
    
    for row in cursor:
        item_id = row['id']
        # Check for collision
        existing = v3_conn.execute("SELECT id FROM items WHERE id = ?", (item_id,)).fetchone()
        if existing:
            item_id = f"n5_{item_id}"
            logging.info(f"ID collision, renamed to {item_id}")
        
        # Map fields
        item_type = row['type']  # link or snippet
        url = row['url'] if item_type == 'link' else None
        content = row['content'] if item_type == 'snippet' else row.get('content')
        
        v3_conn.execute("""
            INSERT INTO items (id, item_type, title, url, content, source_type, 
                               created_at, updated_at, deprecated, notes, source)
            VALUES (?, ?, ?, ?, ?, 'manual', ?, ?, ?, ?, 'n5_links')
        """, (
            item_id,
            item_type,
            row['title'],
            url,
            content,
            row['created_at'],
            row['updated_at'],
            row.get('deprecated', 0),
            row.get('notes')
        ))
        
        # Migrate tags
        tag_cursor = n5_conn.execute("SELECT tag_key, tag_value FROM tags WHERE item_id = ?", (row['id'],))
        for tag in tag_cursor:
            v3_conn.execute("""
                INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value)
                VALUES (?, ?, ?)
            """, (item_id, tag['tag_key'], tag['tag_value']))
        
        count += 1
    
    v3_conn.commit()
    n5_conn.close()
    logging.info(f"Migrated {count} items from N5 DB")
    return count

def migrate_personal_items(v3_conn):
    """Migrate items from Personal content-library.db"""
    if not PERSONAL_DB.exists():
        logging.warning(f"Personal DB not found at {PERSONAL_DB}")
        return 0
    
    pcl_conn = sqlite3.connect(PERSONAL_DB)
    pcl_conn.row_factory = sqlite3.Row
    
    cursor = pcl_conn.execute("SELECT * FROM content")
    count = 0
    
    for row in cursor:
        item_id = row['id']
        # Check for collision
        existing = v3_conn.execute("SELECT id FROM items WHERE id = ?", (item_id,)).fetchone()
        if existing:
            item_id = f"pcl_{item_id}"
            logging.info(f"ID collision, renamed to {item_id}")
        
        v3_conn.execute("""
            INSERT INTO items (id, item_type, title, url, content_path, summary_path,
                               source_type, platform, author, created_at, updated_at,
                               confidence, has_content, has_summary, notes, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'personal_cl')
        """, (
            item_id,
            row['source_type'],  # article, social-post, etc.
            row['title'],
            row.get('url'),
            row.get('content_path'),
            row.get('summary_path'),
            row.get('provenance', 'discovered'),
            row.get('platform'),
            row.get('author'),
            row.get('created_at', datetime.now().isoformat()),
            row.get('updated_at', datetime.now().isoformat()),
            row.get('confidence', 3),
            1 if row.get('content_path') else 0,
            1 if row.get('summary_path') else 0,
            row.get('notes')
        ))
        
        # Migrate topics
        topic_cursor = pcl_conn.execute("""
            SELECT t.name FROM topics t
            JOIN content_topics ct ON t.id = ct.topic_id
            WHERE ct.content_id = ?
        """, (row['id'],))
        
        for topic_row in topic_cursor:
            topic_name = topic_row['name']
            # Get or create topic in v3
            v3_conn.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic_name,))
            topic_id = v3_conn.execute("SELECT id FROM topics WHERE name = ?", (topic_name,)).fetchone()[0]
            v3_conn.execute("INSERT OR IGNORE INTO item_topics (item_id, topic_id) VALUES (?, ?)", (item_id, topic_id))
        
        count += 1
    
    # Migrate blocks if they exist
    try:
        block_cursor = pcl_conn.execute("SELECT * FROM blocks")
        for block in block_cursor:
            v3_conn.execute("""
                INSERT INTO blocks (id, item_id, block_code, block_type, content, 
                                    context, file_path, extracted_at, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                block['id'],
                block['content_id'],  # maps to item_id
                block.get('block_code'),
                block.get('block_type'),
                block['content'],
                block.get('context'),
                block.get('file_path'),
                block.get('extracted_at'),
                block.get('confidence', 3)
            ))
    except sqlite3.OperationalError:
        logging.info("No blocks table in Personal DB")
    
    v3_conn.commit()
    pcl_conn.close()
    logging.info(f"Migrated {count} items from Personal DB")
    return count

def main():
    logging.info("Starting Content Library v3 migration")
    
    v3_conn = create_v3_database()
    
    n5_count = migrate_n5_items(v3_conn)
    pcl_count = migrate_personal_items(v3_conn)
    
    # Verify
    total = v3_conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    topics = v3_conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
    tags = v3_conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
    
    v3_conn.close()
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)
    print(f"N5 items migrated:       {n5_count}")
    print(f"Personal items migrated: {pcl_count}")
    print(f"Total items in v3:       {total}")
    print(f"Topics created:          {topics}")
    print(f"Tags migrated:           {tags}")
    print(f"Database:                {V3_DB}")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

---

## Testing

After running migration:

```bash
# Check item count
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db "SELECT COUNT(*) FROM items;"
# Expected: 83 (67 + 16)

# Check by source
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db "SELECT source, COUNT(*) FROM items GROUP BY source;"
# Expected: n5_links: 67, personal_cl: 16

# Check types
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db "SELECT item_type, COUNT(*) FROM items GROUP BY item_type;"

# Check topics migrated
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db "SELECT COUNT(*) FROM topics;"

# Check tags migrated
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db "SELECT COUNT(*) FROM tags;"

# Verify no ID collisions without prefix
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db "SELECT id FROM items WHERE id LIKE 'n5_%' OR id LIKE 'pcl_%';"
```

---

## Report Back

When complete, report:
1. ✅ Database created at path
2. ✅ Migration script created
3. ✅ Item counts (expected vs actual)
4. ✅ Any ID collisions found
5. ✅ Any errors encountered
6. ✅ Verification queries passed

---

**Orchestrator Contact:** con_jYGYNfcv76UTmolk  
**Created:** 2025-12-02 21:58 ET

