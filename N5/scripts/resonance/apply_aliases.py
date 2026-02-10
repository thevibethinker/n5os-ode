#!/usr/bin/env python3
"""
Apply Idea Aliases: Consolidate duplicate idea slugs in brain.db.

Reads aliases from N5/config/idea_aliases.json and updates brain.db
to use canonical slugs instead of variants.

Usage:
    python3 apply_aliases.py preview   # Show what would change
    python3 apply_aliases.py apply     # Actually apply changes
"""

import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

N5_ROOT = Path("/home/workspace/N5")
ALIASES_FILE = N5_ROOT / "config" / "idea_aliases.json"
EDGES_DB = Path("/home/workspace/N5/cognition/brain.db")


def load_aliases() -> dict:
    """Load alias mappings from config file."""
    with open(ALIASES_FILE) as f:
        data = json.load(f)
    # Filter out metadata keys
    return {k: v for k, v in data.items() if not k.startswith("_")}


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(EDGES_DB)
    conn.row_factory = sqlite3.Row
    return conn


def preview_changes(aliases: dict) -> dict:
    """Preview what changes would be made."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    changes = {
        "edges_to_update": [],
        "entities_to_merge": [],
        "summary": {}
    }
    
    for variant, canonical in aliases.items():
        # Check edges where this variant appears as source
        cursor.execute("""
            SELECT id, source_type, source_id, relation, target_type, target_id
            FROM edges 
            WHERE (source_type = 'idea' AND source_id = ?)
               OR (target_type = 'idea' AND target_id = ?)
        """, (variant, variant))
        
        for row in cursor.fetchall():
            changes["edges_to_update"].append({
                "edge_id": row["id"],
                "old_source": f"{row['source_type']}:{row['source_id']}",
                "old_target": f"{row['target_type']}:{row['target_id']}",
                "variant": variant,
                "canonical": canonical
            })
        
        # Check entities table
        cursor.execute("""
            SELECT id, entity_type, entity_id, name
            FROM entities
            WHERE entity_type = 'idea' AND entity_id = ?
        """, (variant,))
        
        for row in cursor.fetchall():
            changes["entities_to_merge"].append({
                "entity_db_id": row["id"],
                "variant": variant,
                "canonical": canonical,
                "name": row["name"]
            })
    
    changes["summary"] = {
        "total_aliases": len(aliases),
        "edges_affected": len(changes["edges_to_update"]),
        "entities_to_merge": len(changes["entities_to_merge"])
    }
    
    conn.close()
    return changes


def apply_changes(aliases: dict, dry_run: bool = True) -> dict:
    """Apply alias changes to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    result = {
        "edges_updated": 0,
        "entities_merged": 0,
        "dry_run": dry_run
    }
    
    for variant, canonical in aliases.items():
        # Update edges where variant appears as source_id
        cursor.execute("""
            UPDATE edges 
            SET source_id = ?, updated_at = ?
            WHERE source_type = 'idea' AND source_id = ?
        """, (canonical, datetime.now(timezone.utc).isoformat(), variant))
        result["edges_updated"] += cursor.rowcount
        
        # Update edges where variant appears as target_id
        cursor.execute("""
            UPDATE edges 
            SET target_id = ?, updated_at = ?
            WHERE target_type = 'idea' AND target_id = ?
        """, (canonical, datetime.now(timezone.utc).isoformat(), variant))
        result["edges_updated"] += cursor.rowcount
        
        # Check if canonical entity exists
        cursor.execute("""
            SELECT id FROM entities 
            WHERE entity_type = 'idea' AND entity_id = ?
        """, (canonical,))
        canonical_exists = cursor.fetchone()
        
        if canonical_exists:
            # Delete the variant entity (canonical already exists)
            cursor.execute("""
                DELETE FROM entities 
                WHERE entity_type = 'idea' AND entity_id = ?
            """, (variant,))
            result["entities_merged"] += cursor.rowcount
        else:
            # Rename variant to canonical
            cursor.execute("""
                UPDATE entities 
                SET entity_id = ?
                WHERE entity_type = 'idea' AND entity_id = ?
            """, (canonical, variant))
            result["entities_merged"] += cursor.rowcount
    
    if dry_run:
        conn.rollback()
        result["status"] = "preview_only"
    else:
        conn.commit()
        result["status"] = "applied"
        result["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    conn.close()
    return result


def main():
    parser = argparse.ArgumentParser(description="Apply idea aliases to consolidate duplicates")
    parser.add_argument("command", choices=["preview", "apply"], help="preview or apply changes")
    args = parser.parse_args()
    
    aliases = load_aliases()
    print(f"Loaded {len(aliases)} aliases from {ALIASES_FILE}")
    
    if args.command == "preview":
        changes = preview_changes(aliases)
        print(json.dumps(changes, indent=2))
    
    elif args.command == "apply":
        # First show preview
        changes = preview_changes(aliases)
        print(f"Will update {changes['summary']['edges_affected']} edges")
        print(f"Will merge {changes['summary']['entities_to_merge']} entities")
        print()
        
        # Apply for real
        result = apply_changes(aliases, dry_run=False)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()


