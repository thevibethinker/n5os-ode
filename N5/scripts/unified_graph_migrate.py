#!/usr/bin/env python3
"""Migration helper for the unified knowledge graph backfill."""

import argparse
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Optional

SRC_PROGRESS_FILE = Path("/home/workspace/N5/cognition/backfill_progress.json")
BRAIN_DB_PATH = Path("/home/workspace/N5/cognition/brain.db")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
LOG = logging.getLogger("unified_graph_migrate")


def iso_now() -> str:
    """Return a UTC timestamp string."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_progress_table(conn: sqlite3.Connection) -> None:
    """Ensure the backfill_progress table schema contains the required columns."""
    cursor = conn.execute("PRAGMA table_info('backfill_progress')")
    columns = {row[1] for row in cursor.fetchall()}
    if not columns:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS backfill_progress (
                block_id TEXT PRIMARY KEY,
                processed_at TEXT DEFAULT (datetime('now')),
                entity_count INTEGER DEFAULT 0,
                relationship_count INTEGER DEFAULT 0,
                error TEXT,
                needs_retry INTEGER DEFAULT 0,
                last_attempt_at TEXT,
                retry_count INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        columns = {
            "block_id",
            "processed_at",
            "entity_count",
            "relationship_count",
            "error",
            "needs_retry",
            "last_attempt_at",
            "retry_count",
        }
    extras: Dict[str, str] = {
        "needs_retry": "INTEGER DEFAULT 0",
        "last_attempt_at": "TEXT",
        "retry_count": "INTEGER DEFAULT 0",
    }
    for name, definition in extras.items():
        if name not in columns:
            LOG.info(f"Adding missing column {name} to backfill_progress")
            conn.execute(f"ALTER TABLE backfill_progress ADD COLUMN {name} {definition}")
    conn.commit()


def load_json_progress() -> Dict:
    """Read the legacy progress JSON file."""
    if not SRC_PROGRESS_FILE.exists():
        LOG.error("Progress file missing: %s", SRC_PROGRESS_FILE)
        return {}
    try:
        return json.loads(SRC_PROGRESS_FILE.read_text())
    except json.JSONDecodeError as exc:
        LOG.error("Failed to read progress JSON: %s", exc)
        return {}


def migrate_progress(conn: sqlite3.Connection, data: Dict, *, dry_run: bool, force: bool) -> None:
    """Import JSON progress into the SQLite table."""
    processed_ids: Iterable[str] = data.get("processed_block_ids", [])
    error_entries = data.get("errors", [])
    errors_by_block = {entry.get("block_id"): entry for entry in error_entries if entry.get("block_id")}

    existing = {row[0] for row in conn.execute("SELECT block_id FROM backfill_progress").fetchall()}
    inserted_success = 0
    inserted_errors = 0

    def _insert_row(block_id: str, entities: int, relationships: int, error: Optional[str], needs_retry: int, retry_count: int) -> None:
        now = iso_now()
        params = (
            block_id,
            now,
            entities,
            relationships,
            error,
            needs_retry,
            now,
            retry_count,
        )
        sql = """INSERT OR REPLACE INTO backfill_progress
            (block_id, processed_at, entity_count, relationship_count, error, needs_retry, last_attempt_at, retry_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        if dry_run:
            LOG.info("DRY-RUN: Would insert row %s (retry=%d, error=%s)", block_id, retry_count, bool(error))
        else:
            conn.execute(sql, params)

    LOG.info("Migrating %d processed block IDs", len(list(processed_ids)))
    for block_id in processed_ids:
        if not block_id:
            continue
        if block_id in errors_by_block:
            continue
        if block_id in existing and not force:
            continue
        _insert_row(block_id, entities=0, relationships=0, error=None, needs_retry=0, retry_count=0)
        inserted_success += 1

    LOG.info("Marking %d errored block IDs for retry", len(errors_by_block))
    for block_id, error_data in errors_by_block.items():
        if not block_id:
            continue
        existing_retry = 0
        row = conn.execute("SELECT retry_count FROM backfill_progress WHERE block_id = ?", (block_id,)).fetchone()
        if row and isinstance(row[0], int):
            existing_retry = row[0]
        _insert_row(
            block_id,
            entities=0,
            relationships=0,
            error=error_data.get("error"),
            needs_retry=1,
            retry_count=existing_retry + 1,
        )
        inserted_errors += 1

    if dry_run:
        LOG.info("Dry-run mode, skipping commit. Success inserts: %d, errors: %d", inserted_success, inserted_errors)
    else:
        conn.commit()
        LOG.info("Committed %d successes and %d errors to backfill_progress", inserted_success, inserted_errors)
        total_rows = conn.execute("SELECT COUNT(*) FROM backfill_progress").fetchone()[0]
        LOG.info("backfill_progress now contains %d rows", total_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare the unified graph database.")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without modifying the DB")
    parser.add_argument("--force", action="store_true", help="Re-import even if rows already exist")
    args = parser.parse_args()

    progress_data = load_json_progress()
    if not progress_data:
        LOG.error("No progress data found, aborting")
        return 1

    conn = sqlite3.connect(BRAIN_DB_PATH)
    try:
        ensure_progress_table(conn)
        migrate_progress(conn, progress_data, dry_run=args.dry_run, force=args.force)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
