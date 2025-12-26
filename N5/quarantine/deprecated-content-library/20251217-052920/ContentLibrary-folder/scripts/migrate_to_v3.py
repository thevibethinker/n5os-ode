#!/usr/bin/env python3
"""
migrate_to_v3.py - Migrate both content libraries to unified v3

Migrates data from:
1. N5 Links DB (N5/data/content_library.db) - 67 items
2. Personal CL DB (Personal/Knowledge/ContentLibrary/content-library.db) - 16 items

Into unified Content Library v3 (Personal/Knowledge/ContentLibrary/content-library-v3.db)
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
-- Main content table (superset of both schemas)
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

CREATE INDEX idx_items_type ON items(item_type);
CREATE INDEX idx_items_source_type ON items(source_type);
CREATE INDEX idx_items_deprecated ON items(deprecated);
CREATE INDEX idx_items_title ON items(title COLLATE NOCASE);
CREATE INDEX idx_items_updated ON items(updated_at DESC);
CREATE INDEX idx_tags_key_value ON tags(tag_key, tag_value);
CREATE INDEX idx_blocks_item ON blocks(item_id);
"""


def create_v3_database():
    """Create fresh v3 database with schema"""
    if V3_DB.exists():
        backup = V3_DB.with_suffix('.db.backup')
        if backup.exists():
            backup.unlink()
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
        return 0, 0
    
    n5_conn = sqlite3.connect(N5_DB)
    n5_conn.row_factory = sqlite3.Row
    
    cursor = n5_conn.execute("SELECT * FROM items")
    count = 0
    collisions = 0
    
    for row in cursor:
        item_id = row['id']
        existing = v3_conn.execute("SELECT id FROM items WHERE id = ?", (item_id,)).fetchone()
        if existing:
            item_id = f"n5_{item_id}"
            logging.info(f"ID collision, renamed to {item_id}")
            collisions += 1
        
        item_type = row['type']  # link or snippet
        url = row['url'] if item_type == 'link' else None
        content = row['content'] if item_type == 'snippet' else None
        
        v3_conn.execute("""
            INSERT INTO items (id, item_type, title, url, content, source_type, 
                               created_at, updated_at, deprecated, expires_at,
                               last_used_at, version, notes, source)
            VALUES (?, ?, ?, ?, ?, 'manual', ?, ?, ?, ?, ?, ?, ?, 'n5_links')
        """, (
            item_id,
            item_type,
            row['title'],
            url,
            content,
            row['created_at'],
            row['updated_at'],
            row['deprecated'],
            row['expires_at'],
            row['last_used_at'],
            row['version'],
            row['notes']
        ))
        
        tag_cursor = n5_conn.execute("SELECT tag_key, tag_value FROM tags WHERE item_id = ?", (row['id'],))
        for tag in tag_cursor:
            v3_conn.execute("""
                INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value)
                VALUES (?, ?, ?)
            """, (item_id, tag['tag_key'], tag['tag_value']))
        
        count += 1
    
    v3_conn.commit()
    n5_conn.close()
    logging.info(f"Migrated {count} items from N5 DB (collisions: {collisions})")
    return count, collisions


def migrate_personal_items(v3_conn):
    """Migrate items from Personal content-library.db"""
    if not PERSONAL_DB.exists():
        logging.warning(f"Personal DB not found at {PERSONAL_DB}")
        return 0, 0, 0, 0
    
    pcl_conn = sqlite3.connect(PERSONAL_DB)
    pcl_conn.row_factory = sqlite3.Row
    
    cursor = pcl_conn.execute("SELECT * FROM content")
    count = 0
    collisions = 0
    topics_count = 0
    blocks_count = 0
    
    for row in cursor:
        item_id = row['id']
        existing = v3_conn.execute("SELECT id FROM items WHERE id = ?", (item_id,)).fetchone()
        if existing:
            item_id = f"pcl_{item_id}"
            logging.info(f"ID collision, renamed to {item_id}")
            collisions += 1
        
        v3_conn.execute("""
            INSERT INTO items (id, item_type, title, url, content_path, summary_path,
                               source_type, word_count, created_at, updated_at,
                               confidence, has_content, has_summary, notes, source)
            VALUES (?, ?, ?, ?, ?, ?, 'discovered', ?, ?, ?, ?, ?, ?, ?, 'personal_cl')
        """, (
            item_id,
            row['source_type'],  # meeting, article, etc.
            row['title'],
            row['url'],
            row['file_path'],  # content_path in v3
            row['summary_path'],
            row['word_count'],
            row['date_created'] or datetime.now().isoformat(),
            row['date_ingested'] or datetime.now().isoformat(),
            row['confidence'] or 3,
            row['has_content'] or 0,
            row['has_summary'] or 0,
            row['notes']
        ))
        
        topic_cursor = pcl_conn.execute("""
            SELECT t.name FROM topics t
            JOIN content_topics ct ON t.id = ct.topic_id
            WHERE ct.content_id = ?
        """, (row['id'],))
        
        for topic_row in topic_cursor:
            topic_name = topic_row['name']
            v3_conn.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic_name,))
            topic_id = v3_conn.execute("SELECT id FROM topics WHERE name = ?", (topic_name,)).fetchone()[0]
            v3_conn.execute("INSERT OR IGNORE INTO item_topics (item_id, topic_id) VALUES (?, ?)", (item_id, topic_id))
            topics_count += 1
        
        count += 1
    
    block_cursor = pcl_conn.execute("SELECT * FROM blocks")
    for block in block_cursor:
        original_content_id = block['content_id']
        existing = v3_conn.execute("SELECT id FROM items WHERE id = ?", (original_content_id,)).fetchone()
        if not existing:
            mapped_id = f"pcl_{original_content_id}"
            existing = v3_conn.execute("SELECT id FROM items WHERE id = ?", (mapped_id,)).fetchone()
            if existing:
                original_content_id = mapped_id
            else:
                logging.warning(f"Block {block['id']} references non-existent content_id {original_content_id}")
                continue
        
        v3_conn.execute("""
            INSERT INTO blocks (id, item_id, block_code, block_type, content, 
                                context, speaker, file_path, line_start, line_end,
                                extracted_at, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            block['id'],
            original_content_id,
            block['block_code'],
            block['block_type'],
            block['content'],
            block['context'],
            block['speaker'],
            block['file_path'],
            block['line_start'],
            block['line_end'],
            block['extracted_at'],
            block['confidence'] or 3
        ))
        
        block_topic_cursor = pcl_conn.execute("""
            SELECT t.name FROM topics t
            JOIN block_topics bt ON t.id = bt.topic_id
            WHERE bt.block_id = ?
        """, (block['id'],))
        
        for topic_row in block_topic_cursor:
            topic_name = topic_row['name']
            v3_conn.execute("INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic_name,))
            topic_id = v3_conn.execute("SELECT id FROM topics WHERE name = ?", (topic_name,)).fetchone()[0]
            v3_conn.execute("INSERT OR IGNORE INTO block_topics (block_id, topic_id) VALUES (?, ?)", (block['id'], topic_id))
        
        blocks_count += 1
    
    kr_cursor = pcl_conn.execute("SELECT * FROM knowledge_refs")
    for kr in kr_cursor:
        v3_conn.execute("""
            INSERT OR IGNORE INTO knowledge_refs (block_id, knowledge_type, knowledge_id,
                                                   source_type, source_id, promoted_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            kr['block_id'],
            kr['knowledge_type'],
            kr['knowledge_id'],
            kr['source_type'],
            kr['source_id'],
            kr['promoted_at'],
            kr['notes']
        ))
    
    v3_conn.commit()
    pcl_conn.close()
    logging.info(f"Migrated {count} items from Personal DB (collisions: {collisions}, blocks: {blocks_count})")
    return count, collisions, topics_count, blocks_count


def main():
    logging.info("Starting Content Library v3 migration")
    logging.info(f"N5 DB: {N5_DB} (exists: {N5_DB.exists()})")
    logging.info(f"Personal DB: {PERSONAL_DB} (exists: {PERSONAL_DB.exists()})")
    logging.info(f"V3 DB target: {V3_DB}")
    
    v3_conn = create_v3_database()
    
    n5_count, n5_collisions = migrate_n5_items(v3_conn)
    pcl_count, pcl_collisions, topics_migrated, blocks_migrated = migrate_personal_items(v3_conn)
    
    total = v3_conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    topics = v3_conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
    tags = v3_conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
    blocks = v3_conn.execute("SELECT COUNT(*) FROM blocks").fetchone()[0]
    
    type_breakdown = v3_conn.execute("SELECT item_type, COUNT(*) FROM items GROUP BY item_type").fetchall()
    source_breakdown = v3_conn.execute("SELECT source, COUNT(*) FROM items GROUP BY source").fetchall()
    
    v3_conn.close()
    
    print("\n" + "=" * 70)
    print("CONTENT LIBRARY V3 MIGRATION COMPLETE")
    print("=" * 70)
    print(f"\n📊 ITEM MIGRATION:")
    print(f"   N5 items migrated:       {n5_count}")
    print(f"   Personal items migrated: {pcl_count}")
    print(f"   Total items in v3:       {total}")
    print(f"   Expected total:          83 (67 + 16)")
    print(f"\n🏷️  METADATA MIGRATION:")
    print(f"   Tags migrated:           {tags}")
    print(f"   Topics created:          {topics}")
    print(f"   Blocks migrated:         {blocks}")
    print(f"\n⚠️  ID COLLISIONS:")
    print(f"   N5 collisions:           {n5_collisions}")
    print(f"   Personal collisions:     {pcl_collisions}")
    print(f"\n📁 TYPE BREAKDOWN:")
    for item_type, cnt in type_breakdown:
        print(f"   {item_type}: {cnt}")
    print(f"\n📍 SOURCE BREAKDOWN:")
    for src, cnt in source_breakdown:
        print(f"   {src}: {cnt}")
    print(f"\n📂 DATABASE LOCATION:")
    print(f"   {V3_DB}")
    print("=" * 70)
    
    return {
        'n5_count': n5_count,
        'pcl_count': pcl_count,
        'total': total,
        'tags': tags,
        'topics': topics,
        'blocks': blocks,
        'n5_collisions': n5_collisions,
        'pcl_collisions': pcl_collisions,
        'type_breakdown': dict(type_breakdown),
        'source_breakdown': dict(source_breakdown)
    }


if __name__ == "__main__":
    main()

