#!/usr/bin/env python3
"""
Sync Event Decisions to DB - Bidirectional sync between site decisions and DB.

Reads event_decisions.json (site decisions) and updates luma_events.db status.
Decision mapping:
  - 'yes' → status='approved'
  - 'no' → status='rejected' 
  - 'maybe' → status='maybe'

Usage:
    python3 sync_decisions_to_db.py              # Sync all decisions
    python3 sync_decisions_to_db.py --dry-run    # Show what would change
    python3 sync_decisions_to_db.py --json       # Output JSON for API

Created: 2026-01-04
Provenance: con_a706XArBDk98jyVA (events-pipeline-consolidation Phase 2)
"""

import argparse
import json
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

# Paths
DB_PATH = Path("/home/workspace/N5/data/luma_events.db")
DECISIONS_FILE = Path("/home/workspace/N5/data/event_decisions.json")

# Decision → DB status mapping
DECISION_MAP = {
    "yes": "approved",
    "no": "rejected",
    "maybe": "maybe"
}


def load_decisions() -> dict:
    """Load decisions from JSON file."""
    if not DECISIONS_FILE.exists():
        log.warning(f"Decisions file not found: {DECISIONS_FILE}")
        return {}
    
    try:
        with open(DECISIONS_FILE) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log.error(f"Invalid JSON in decisions file: {e}")
        return {}


def get_db_statuses(conn: sqlite3.Connection, event_ids: list) -> dict:
    """Get current DB statuses for given event IDs."""
    if not event_ids:
        return {}
    
    placeholders = ",".join("?" * len(event_ids))
    cursor = conn.execute(
        f"SELECT id, status FROM events WHERE id IN ({placeholders})",
        event_ids
    )
    return {row[0]: row[1] for row in cursor.fetchall()}


def sync_decisions(dry_run: bool = False) -> dict:
    """
    Sync decisions from JSON to DB.
    
    Returns:
        dict with sync results
    """
    result = {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decisions_loaded": 0,
        "already_synced": 0,
        "updated": 0,
        "not_in_db": 0,
        "changes": [],
        "errors": []
    }
    
    decisions = load_decisions()
    result["decisions_loaded"] = len(decisions)
    
    if not decisions:
        log.info("No decisions to sync")
        return result
    
    try:
        conn = sqlite3.connect(DB_PATH)
        event_ids = list(decisions.keys())
        current_statuses = get_db_statuses(conn, event_ids)
        
        updates = []
        for event_id, decision_data in decisions.items():
            decision = decision_data.get("decision")
            decided_at = decision_data.get("decidedAt")
            
            if event_id not in current_statuses:
                result["not_in_db"] += 1
                log.debug(f"Event {event_id} not in DB, skipping")
                continue
            
            current_status = current_statuses[event_id]
            new_status = DECISION_MAP.get(decision)
            
            if not new_status:
                log.warning(f"Unknown decision '{decision}' for {event_id}")
                continue
            
            if current_status == new_status:
                result["already_synced"] += 1
                continue
            
            updates.append({
                "event_id": event_id,
                "old_status": current_status,
                "new_status": new_status,
                "decided_at": decided_at
            })
            result["changes"].append({
                "id": event_id,
                "from": current_status,
                "to": new_status
            })
        
        if updates and not dry_run:
            for update in updates:
                conn.execute(
                    """UPDATE events 
                       SET status = ?, 
                           updated_at = ?
                       WHERE id = ?""",
                    (update["new_status"], 
                     datetime.now(timezone.utc).isoformat(),
                     update["event_id"])
                )
            conn.commit()
            result["updated"] = len(updates)
            log.info(f"Updated {len(updates)} events in DB")
        elif updates and dry_run:
            result["updated"] = len(updates)
            log.info(f"[DRY RUN] Would update {len(updates)} events")
        else:
            log.info("No updates needed - all decisions already synced")
        
        conn.close()
        
    except Exception as e:
        result["success"] = False
        result["errors"].append(str(e))
        log.error(f"Sync failed: {e}")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Sync event decisions from JSON to database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 sync_decisions_to_db.py
    python3 sync_decisions_to_db.py --dry-run
    python3 sync_decisions_to_db.py --json
        """
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without updating DB")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    result = sync_decisions(dry_run=args.dry_run)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Sync Results:")
        print(f"  Decisions loaded: {result['decisions_loaded']}")
        print(f"  Already synced:   {result['already_synced']}")
        print(f"  Updated:          {result['updated']}")
        print(f"  Not in DB:        {result['not_in_db']}")
        
        if result["changes"]:
            print(f"\nChanges:")
            for change in result["changes"][:10]:
                print(f"  {change['id']}: {change['from']} → {change['to']}")
            if len(result["changes"]) > 10:
                print(f"  ... and {len(result['changes']) - 10} more")
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()


