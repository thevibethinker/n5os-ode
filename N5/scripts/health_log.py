#!/usr/bin/env python3
from N5.lib.paths import WELLNESS_DB, N5_ROOT
"""
Health Log - Log checkpoint completions to Life Counter

Logs supplement checkpoint completions to the wellness.db life_logs table.
Called when V replies "done" to a health checkpoint SMS.

Usage:
    python3 health_log.py --checkpoint wake
    python3 health_log.py --checkpoint post_workout
    python3 health_log.py --checkpoint evening
    python3 health_log.py --checkpoint wake --notes "Took with extra water"
"""

import argparse
import json
import logging
import sqlite3
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WELLNESS_DB = WELLNESS_DB
REGIMEN_PATH = N5_ROOT / "systems" / "health" / "regimen.json"


def load_regimen() -> dict:
    """Load the regimen SSOT."""
    if not REGIMEN_PATH.exists():
        raise FileNotFoundError(f"Regimen not found: {REGIMEN_PATH}")
    with open(REGIMEN_PATH) as f:
        return json.load(f)


def get_category_id(conn: sqlite3.Connection, slug: str) -> int | None:
    """Get category ID from slug."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM life_categories WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    return row[0] if row else None


def log_checkpoint(checkpoint_id: str, notes: str = None) -> dict:
    """Log a checkpoint completion to Life Counter."""
    regimen = load_regimen()
    
    # Find checkpoint
    checkpoint = None
    for cp in regimen["checkpoints"]:
        if cp["id"] == checkpoint_id:
            checkpoint = cp
            break
    
    if not checkpoint:
        raise ValueError(f"Checkpoint not found: {checkpoint_id}")
    
    life_counter_slug = checkpoint.get("life_counter_slug")
    if not life_counter_slug:
        raise ValueError(f"No life_counter_slug defined for checkpoint: {checkpoint_id}")
    
    # Connect to wellness.db
    conn = sqlite3.connect(WELLNESS_DB)
    
    # Get category ID
    category_id = get_category_id(conn, life_counter_slug)
    if not category_id:
        conn.close()
        raise ValueError(f"Life Counter category not found: {life_counter_slug}")
    
    # Insert log entry
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    
    # Build notes with items taken
    items_taken = ", ".join(checkpoint.get("items", []))
    full_notes = f"Items: {items_taken}"
    if notes:
        full_notes += f" | {notes}"
    
    cursor.execute("""
        INSERT INTO life_logs (category_id, timestamp, value, note)
        VALUES (?, ?, ?, ?)
    """, (category_id, timestamp, 1, full_notes))
    
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    
    logger.info(f"Logged checkpoint '{checkpoint_id}' to life_logs (id={log_id})")
    
    return {
        "success": True,
        "log_id": log_id,
        "checkpoint": checkpoint_id,
        "category_slug": life_counter_slug,
        "timestamp": timestamp,
        "notes": full_notes
    }


def is_done_reply(message: str, regimen: dict = None) -> bool:
    """Check if a message is a 'done' reply."""
    if regimen is None:
        regimen = load_regimen()
    
    aliases = regimen.get("done_aliases", ["done", "took it", "taken", "✓", "✅"])
    message_lower = message.strip().lower()
    
    return message_lower in [a.lower() for a in aliases]


def main():
    parser = argparse.ArgumentParser(description="Log health checkpoint completion")
    parser.add_argument("--checkpoint", "-c", type=str, required=True,
                       help="Checkpoint ID (wake, post_workout, evening)")
    parser.add_argument("--notes", "-n", type=str, default=None,
                       help="Optional notes")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--check-reply", type=str, metavar="MESSAGE",
                       help="Check if message is a 'done' reply (doesn't log)")
    args = parser.parse_args()
    
    if args.check_reply:
        regimen = load_regimen()
        is_done = is_done_reply(args.check_reply, regimen)
        if args.json:
            print(json.dumps({"message": args.check_reply, "is_done": is_done}))
        else:
            print(f"'{args.check_reply}' is {'a' if is_done else 'NOT a'} done reply")
        return 0 if is_done else 1
    
    try:
        result = log_checkpoint(args.checkpoint, args.notes)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"✅ Logged {result['checkpoint']} (id={result['log_id']})")
        return 0
    except (ValueError, FileNotFoundError) as e:
        logger.error(str(e))
        if args.json:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())


