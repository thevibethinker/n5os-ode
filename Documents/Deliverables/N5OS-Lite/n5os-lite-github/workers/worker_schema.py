#!/usr/bin/env python3
"""
Worker: worker_schema
Task: Create SQLite database schema for Content Library
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("/home/workspace/Personal/Content-Library/content-library.db")

# Ensure directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def create_schema():
    """Create database schema for Content Library INDEX"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Main content index (raw materials)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            title TEXT,
            file_path TEXT,
            url TEXT,
            date_created TEXT,
            date_ingested TEXT,
            confidence INTEGER DEFAULT 3,
            word_count INTEGER,
            has_content INTEGER DEFAULT 0,
            has_summary INTEGER DEFAULT 0,
            summary_path TEXT,
            topics TEXT,  -- JSON array
            tags TEXT,     -- JSON array
            notes TEXT
        )
    """)
    
    # Blocks (extracted pieces - B01, B02, B31, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            id TEXT PRIMARY KEY,
            content_id TEXT NOT NULL,
            block_code TEXT,  -- B01, B02, B31, etc.
            block_type TEXT,   -- quote, insight, action, resource, etc.
            content TEXT NOT NULL,
            context TEXT,
            speaker TEXT,
            file_path TEXT,  -- Path to block file
            line_start INTEGER,
            line_end INTEGER,
            extracted_at TEXT,
            confidence INTEGER DEFAULT 3,
            topics TEXT,  -- JSON array
            tags TEXT,     -- JSON array
            FOREIGN KEY (content_id) REFERENCES content(id)
        )
    """)
    
    # Topics (normalized)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Many-to-many: content ↔ topics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_topics (
            content_id TEXT NOT NULL,
            topic_id INTEGER NOT NULL,
            PRIMARY KEY (content_id, topic_id),
            FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE,
            FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
        )
    """)
    
    # Many-to-many: blocks ↔ topics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS block_topics (
            block_id TEXT NOT NULL,
            topic_id INTEGER NOT NULL,
            PRIMARY KEY (block_id, topic_id),
            FOREIGN KEY (block_id) REFERENCES blocks(id) ON DELETE CASCADE,
            FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
        )
    """)
    
    # Knowledge references (when promoted to knowledge base)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_refs (
            block_id TEXT PRIMARY KEY,
            knowledge_type TEXT,  -- principle, concept, fact, framework
            knowledge_id TEXT,     -- ID in knowledge system
            source_type TEXT,      -- block or content
            source_id TEXT,        -- block_id or content_id
            promoted_at TEXT,
            notes TEXT,
            FOREIGN KEY (block_id) REFERENCES blocks(id)
        )
    """)
    
    # Schema version tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert current version
    cursor.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (1)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created: {DB_PATH}")
    print("✅ Tables: content, blocks, topics, content_topics, block_topics, knowledge_refs, schema_version")
    return DB_PATH

if __name__ == "__main__":
    db_path = create_schema()
    print(f"\nOutput: {db_path}")

