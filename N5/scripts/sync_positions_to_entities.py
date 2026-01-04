#!/usr/bin/env python3
"""
Sync positions.db → entities table in edges.db

Phase 4.5: Position Integration
Registers positions as first-class entities in the context graph.
"""

import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

POSITIONS_DB = Path(__file__).parent.parent / "data" / "positions.db"
EDGES_DB = Path(__file__).parent.parent / "data" / "edges.db"


def get_positions() -> list[dict]:
    """Read all positions from positions.db."""
    conn = sqlite3.connect(POSITIONS_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, domain, title, insight, stability, confidence, created_at
        FROM positions
        ORDER BY domain, stability DESC
    """)
    
    positions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return positions


def sync_to_entities(positions: list[dict], dry_run: bool = False) -> dict:
    """Upsert positions into entities table in edges.db."""
    if dry_run:
        return {
            "action": "dry_run",
            "would_sync": len(positions),
            "positions": [p["id"] for p in positions[:5]] + (["..."] if len(positions) > 5 else [])
        }
    
    conn = sqlite3.connect(EDGES_DB)
    cursor = conn.cursor()
    
    synced = 0
    errors = []
    
    for pos in positions:
        try:
            metadata = json.dumps({
                "domain": pos["domain"],
                "stability": pos["stability"],
                "confidence": pos["confidence"],
                "insight_preview": pos["insight"][:200] if pos["insight"] else ""
            })
            
            cursor.execute("""
                INSERT OR REPLACE INTO entities (entity_type, entity_id, name, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "position",
                pos["id"],
                pos["title"],
                metadata,
                pos["created_at"] or datetime.now().isoformat()
            ))
            synced += 1
        except Exception as e:
            errors.append({"position_id": pos["id"], "error": str(e)})
    
    conn.commit()
    conn.close()
    
    return {
        "action": "synced",
        "synced": synced,
        "errors": errors,
        "timestamp": datetime.now().isoformat()
    }


def sync_single_position(position_id: str) -> bool:
    """Sync a single position to edges.db entities table.
    
    Called by positions.py after add/update operations.
    Returns True if successful.
    """
    pos_conn = sqlite3.connect(POSITIONS_DB)
    pos_conn.row_factory = sqlite3.Row
    
    row = pos_conn.execute("""
        SELECT id, domain, title, insight, stability, confidence, created_at
        FROM positions WHERE id = ?
    """, (position_id,)).fetchone()
    pos_conn.close()
    
    if not row:
        return False
    
    edges_conn = sqlite3.connect(EDGES_DB)
    now = datetime.now(timezone.utc).isoformat()
    
    metadata = json.dumps({
        "domain": row["domain"],
        "stability": row["stability"],
        "confidence": row["confidence"],
        "insight_preview": row["insight"][:200] if row["insight"] else ""
    })
    
    edges_conn.execute("""
        INSERT OR REPLACE INTO entities (entity_type, entity_id, name, metadata, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, ("position", row["id"], row["title"], metadata, row["created_at"] or now))
    
    edges_conn.commit()
    edges_conn.close()
    return True


def delete_position_entity(position_id: str) -> bool:
    """Remove a position from edges.db entities table.
    
    Called by positions.py after delete operations.
    Returns True if a row was deleted.
    """
    edges_conn = sqlite3.connect(EDGES_DB)
    cursor = edges_conn.execute("""
        DELETE FROM entities WHERE entity_type = 'position' AND entity_id = ?
    """, (position_id,))
    deleted = cursor.rowcount > 0
    edges_conn.commit()
    edges_conn.close()
    return deleted


def verify_sync() -> dict:
    """Verify sync integrity between positions.db and entities."""
    positions = get_positions()
    position_ids = {p["id"] for p in positions}
    
    conn = sqlite3.connect(EDGES_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT entity_id FROM entities WHERE entity_type = 'position'")
    entity_ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    missing_in_entities = position_ids - entity_ids
    orphaned_entities = entity_ids - position_ids
    
    return {
        "positions_count": len(position_ids),
        "entities_count": len(entity_ids),
        "in_sync": len(missing_in_entities) == 0 and len(orphaned_entities) == 0,
        "missing_in_entities": list(missing_in_entities)[:10],
        "orphaned_entities": list(orphaned_entities)[:10]
    }


def main():
    parser = argparse.ArgumentParser(description="Sync positions to context graph entities")
    parser.add_argument("--dry-run", action="store_true", help="Show what would sync without writing")
    parser.add_argument("--verify", action="store_true", help="Check sync integrity")
    parser.add_argument("--force", action="store_true", help="Sync even if recently synced")
    args = parser.parse_args()
    
    if args.verify:
        result = verify_sync()
        print(f"Positions in positions.db: {result['positions_count']}")
        print(f"Position entities in edges.db: {result['entities_count']}")
        if result["in_sync"]:
            print("✓ In sync")
        else:
            if result["missing_in_entities"]:
                print(f"✗ Missing in entities: {result['missing_in_entities']}")
            if result["orphaned_entities"]:
                print(f"✗ Orphaned entities: {result['orphaned_entities']}")
        return
    
    positions = get_positions()
    print(f"Found {len(positions)} positions in positions.db")
    
    result = sync_to_entities(positions, dry_run=args.dry_run)
    
    if args.dry_run:
        print(f"[DRY RUN] Would sync {result['would_sync']} positions")
        print(f"Sample: {result['positions']}")
    else:
        print(f"✓ Synced {result['synced']} positions to entities table")
        if result["errors"]:
            print(f"✗ {len(result['errors'])} errors:")
            for err in result["errors"][:5]:
                print(f"  - {err['position_id']}: {err['error']}")


if __name__ == "__main__":
    main()


