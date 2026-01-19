#!/usr/bin/env python3
"""
Content Library v5 Schema Migration
====================================
Adds: subtype, summary, managed_fields, external_id columns
Creates: id_redirects table for migration support

Run: python3 N5/scripts/migrations/content_library_v5_schema.py

Idempotent - safe to run multiple times.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("/home/workspace/N5/data/content_library.db")


def run_migration():
    """Execute v5 schema migration."""
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    changes = []
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(items)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    
    # Add new columns (idempotent)
    new_columns = [
        ("subtype", "TEXT"),
        ("summary", "TEXT"),
        ("managed_fields", "TEXT"),
        ("external_id", "TEXT"),
    ]
    
    for col_name, col_type in new_columns:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE items ADD COLUMN {col_name} {col_type}")
            changes.append(f"Added column: {col_name}")
            print(f"✓ Added column: {col_name}")
        else:
            print(f"· Column already exists: {col_name}")
    
    # Add indexes (idempotent via IF NOT EXISTS)
    indexes = [
        ("idx_items_subtype", "CREATE INDEX IF NOT EXISTS idx_items_subtype ON items(subtype)"),
        ("idx_items_type_subtype", "CREATE INDEX IF NOT EXISTS idx_items_type_subtype ON items(content_type, subtype)"),
        ("idx_items_external_id", "CREATE INDEX IF NOT EXISTS idx_items_external_id ON items(external_id)"),
    ]
    
    for idx_name, idx_sql in indexes:
        cursor.execute(idx_sql)
        changes.append(f"Created index: {idx_name}")
        print(f"✓ Index: {idx_name}")
    
    # Create id_redirects table for migration support
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS id_redirects (
            old_id TEXT PRIMARY KEY,
            new_id TEXT NOT NULL,
            migrated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    
    # Check if table was just created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='id_redirects'")
    if cursor.fetchone():
        changes.append("Created table: id_redirects")
        print("✓ Table: id_redirects")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Migration complete. {len(changes)} changes applied.")
    return True


if __name__ == "__main__":
    run_migration()
