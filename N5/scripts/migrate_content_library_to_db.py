#!/usr/bin/env python3
"""
Migrate Content Library from JSON to SQLite
Consolidates data from:
- N5/prefs/communication/content-library.json
- N5/prefs/communication/essential-links.json (deprecated)

Output: N5/data/content_library.db
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/home/workspace/N5/data/content_library.db")
JSON_PATH = Path("/home/workspace/N5/prefs/communication/content-library.json")
ESSENTIAL_PATH = Path("/home/workspace/N5/prefs/communication/essential-links.json")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    migrated_count = 0
    
    # Load JSON file
    if JSON_PATH.exists():
        print(f"Loading {JSON_PATH}...")
        data = json.loads(JSON_PATH.read_text())
        
        for item in data.get("items", []):
            item_id = item["id"]
            item_type = item["type"]
            title = item["title"]
            content = item.get("content")
            url = item.get("url")
            tags = item.get("tags", {})
            metadata = item.get("metadata", {})
            
            # Insert item
            cursor.execute("""
                INSERT OR REPLACE INTO items 
                (id, type, title, content, url, created_at, updated_at, deprecated, expires_at, version, last_used_at, notes, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id,
                item_type,
                title,
                content,
                url,
                metadata.get("created", datetime.now().isoformat()),
                metadata.get("updated", datetime.now().isoformat()),
                1 if metadata.get("deprecated") else 0,
                metadata.get("expires_at"),
                metadata.get("version", 1),
                metadata.get("last_used"),
                metadata.get("notes"),
                "json_migration"
            ))
            
            # Insert tags
            for tag_key, tag_values in tags.items():
                if isinstance(tag_values, list):
                    for tag_value in tag_values:
                        cursor.execute("""
                            INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value)
                            VALUES (?, ?, ?)
                        """, (item_id, tag_key, tag_value))
                else:
                    cursor.execute("""
                        INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value)
                        VALUES (?, ?, ?)
                    """, (item_id, tag_key, str(tag_values)))
            
            migrated_count += 1
        
        print(f"✓ Migrated {migrated_count} items from content-library.json")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Migration complete: {migrated_count} total items")
    print(f"Database: {DB_PATH}")
    
    return migrated_count


if __name__ == "__main__":
    try:
        count = migrate()
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

