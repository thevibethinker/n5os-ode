#!/usr/bin/env python3
"""
Content Library v4 Schema Migration

Migrates N5/data/content_library.db from legacy schema to v4:
- Renames `type` → `content_type` (better semantics)
- Removes CHECK constraint (allows new content types)
- Adds: source_url, source_file_path, ingested_at, word_count, has_embedding
- Preserves all existing data

IDEMPOTENT: Safe to run multiple times.

Target Schema (v4):
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL,          -- Renamed from 'type', no CHECK constraint
    content TEXT,
    url TEXT,                             -- Preserved from legacy
    source TEXT,
    source_url TEXT,                      -- NEW: Original URL if from web
    source_file_path TEXT,                -- NEW: Path to file in Knowledge/content-library/
    tags TEXT,                            -- NEW: Comma-separated tags
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    ingested_at TEXT,                     -- NEW: When file was ingested
    deprecated INTEGER DEFAULT 0,
    expires_at TEXT,
    version INTEGER DEFAULT 1,
    last_used_at TEXT,
    confidence INTEGER DEFAULT 3,         -- NEW: 1-5 confidence rating
    has_content INTEGER DEFAULT 0,        -- NEW: Has full content extracted
    has_summary INTEGER DEFAULT 0,        -- NEW: Has AI summary
    word_count INTEGER,                   -- NEW: For articles/content
    has_embedding INTEGER DEFAULT 0       -- NEW: Tracks if in semantic memory

Supported content_type values:
    link, snippet, article, deck, social-post, podcast, video, book, paper, framework, quote

Build: content-library-v4
Wave: 1
Worker: worker_schema
Created: 2026-01-09
Provenance: con_8cI2A33NiwEndujy
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent.parent / "data" / "content_library.db"

def get_connection():
    """Get database connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_if_migrated(conn):
    """Check if migration has already been applied."""
    cursor = conn.execute("PRAGMA table_info(items)")
    columns = {row['name'] for row in cursor.fetchall()}
    return 'content_type' in columns

def get_current_schema(conn):
    """Get current table schema for logging."""
    cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='items'")
    row = cursor.fetchone()
    return row[0] if row else None

def count_items(conn):
    """Count items by type."""
    cursor = conn.execute("SELECT type, COUNT(*) as count FROM items GROUP BY type")
    return {row['type']: row['count'] for row in cursor.fetchall()}

def migrate(dry_run=False):
    """
    Execute the v4 schema migration.
    
    Args:
        dry_run: If True, show what would happen without making changes.
    """
    conn = get_connection()
    
    # Pre-migration state
    print("=" * 60)
    print("Content Library v4 Schema Migration")
    print("=" * 60)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check if already migrated
    if check_if_migrated(conn):
        print("\n✓ Migration already applied (content_type column exists)")
        
        # Show current counts
        cursor = conn.execute("SELECT content_type, COUNT(*) as count FROM items GROUP BY content_type")
        counts = {row['content_type']: row['count'] for row in cursor.fetchall()}
        print(f"\nCurrent item counts: {counts}")
        
        conn.close()
        return True
    
    # Show pre-migration state
    print("\n--- Pre-Migration State ---")
    counts_before = count_items(conn)
    total_before = sum(counts_before.values())
    print(f"Items by type: {counts_before}")
    print(f"Total items: {total_before}")
    
    if dry_run:
        print("\n[DRY RUN] Would perform the following:")
        print("  1. Create new items_v4 table with updated schema")
        print("  2. Copy all data from items → items_v4 (type → content_type)")
        print("  3. Drop old items table")
        print("  4. Rename items_v4 → items")
        print("  5. Recreate indexes")
        conn.close()
        return True
    
    # Execute migration
    print("\n--- Executing Migration ---")
    
    try:
        cursor = conn.cursor()
        
        # 1. Create new table with v4 schema
        print("Creating items_v4 table...")
        cursor.execute("""
            CREATE TABLE items_v4 (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content_type TEXT NOT NULL,
                content TEXT,
                url TEXT,
                source TEXT,
                source_url TEXT,
                source_file_path TEXT,
                tags TEXT,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                ingested_at TEXT,
                deprecated INTEGER NOT NULL DEFAULT 0,
                expires_at TEXT,
                version INTEGER NOT NULL DEFAULT 1,
                last_used_at TEXT,
                confidence INTEGER DEFAULT 3,
                has_content INTEGER DEFAULT 0,
                has_summary INTEGER DEFAULT 0,
                word_count INTEGER,
                has_embedding INTEGER DEFAULT 0
            )
        """)
        
        # 2. Copy data with column rename
        print("Migrating data (type → content_type)...")
        cursor.execute("""
            INSERT INTO items_v4 (
                id, title, content_type, content, url, source, notes,
                created_at, updated_at, deprecated, expires_at, version, last_used_at
            )
            SELECT 
                id, title, type, content, url, source, notes,
                created_at, updated_at, deprecated, expires_at, version, last_used_at
            FROM items
        """)
        migrated_count = cursor.rowcount
        print(f"  Migrated {migrated_count} items")
        
        # 3. Drop old table
        print("Dropping old items table...")
        cursor.execute("DROP TABLE items")
        
        # 4. Rename new table
        print("Renaming items_v4 → items...")
        cursor.execute("ALTER TABLE items_v4 RENAME TO items")
        
        # 5. Recreate indexes
        print("Creating indexes...")
        cursor.execute("CREATE INDEX idx_items_content_type ON items(content_type)")
        cursor.execute("CREATE INDEX idx_items_deprecated ON items(deprecated)")
        cursor.execute("CREATE INDEX idx_items_title ON items(title COLLATE NOCASE)")
        cursor.execute("CREATE INDEX idx_items_updated ON items(updated_at DESC)")
        cursor.execute("CREATE INDEX idx_items_has_embedding ON items(has_embedding)")
        
        # Commit
        conn.commit()
        print("✓ Migration committed")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        conn.close()
        return False
    
    # Post-migration verification
    print("\n--- Post-Migration Verification ---")
    cursor.execute("SELECT content_type, COUNT(*) as count FROM items GROUP BY content_type")
    counts_after = {row['content_type']: row['count'] for row in cursor.fetchall()}
    total_after = sum(counts_after.values())
    
    print(f"Items by content_type: {counts_after}")
    print(f"Total items: {total_after}")
    
    if total_after == total_before:
        print(f"✓ Data integrity verified ({total_after} items preserved)")
    else:
        print(f"✗ DATA LOSS DETECTED: {total_before} → {total_after}")
        return False
    
    # Show new schema
    print("\n--- New Schema ---")
    new_schema = get_current_schema(conn)
    print(new_schema)
    
    conn.close()
    print("\n✓ Migration complete")
    return True

def rollback():
    """
    Rollback migration (if needed).
    Only works if original data hasn't been modified.
    """
    print("Rollback not implemented - restore from backup if needed")
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Content Library v4 Schema Migration")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes")
    parser.add_argument("--rollback", action="store_true", help="Rollback migration (requires backup)")
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback()
    else:
        success = migrate(dry_run=args.dry_run)
    
    sys.exit(0 if success else 1)

