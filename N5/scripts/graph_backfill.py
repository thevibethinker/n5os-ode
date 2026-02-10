#!/usr/bin/env python3
"""
N5 Graph Backfill — Extract entities from all indexed documents.

Runs incrementally, tracking progress. Safe to restart.
Uses rate limiting and a SQLite-based progress store to avoid API overload.

Usage:
    python3 graph_backfill.py              # Process next batch (default 50 docs)
    python3 graph_backfill.py --batch 100  # Process 100 docs
    python3 graph_backfill.py --status     # Show status
    python3 graph_backfill.py --reset      # Reset progress (re-extract all)
    python3 graph_backfill.py --sample 100 # Process only top 100 most-mentioned docs
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Set

sys.path.insert(0, '/home/workspace')

from N5.cognition.entity_extractor import extract_entities
from N5.cognition.graph_store import GraphStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
LOG = logging.getLogger("graph_backfill")

BRAIN_DB = Path("/home/workspace/N5/cognition/brain.db")
VECTORS_DB = Path("/home/workspace/N5/cognition/vectors_v2.db")
PROGRESS_FILE = Path("/home/workspace/N5/cognition/backfill_progress.json")
CONTROL_FILE = Path("/home/workspace/N5/config/backfill_control.json")

MIN_DELAY_BETWEEN_EXTRACTIONS = 0.75  # seconds


def iso_now() -> str:
    """Return an ISO timestamp in UTC."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class BackfillProgressStore:
    """SQLite-backed store for block-level backfill progress."""

    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute("""
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
        self.conn.commit()

    def processed_block_ids(self) -> Set[str]:
        cursor = self.conn.execute(
            "SELECT block_id FROM backfill_progress WHERE needs_retry = 0"
        )
        return {row[0] for row in cursor.fetchall()}

    def record_success(self, block_id: str, entity_count: int, relationship_count: int) -> None:
        now = iso_now()
        self.conn.execute(
            """
            INSERT OR REPLACE INTO backfill_progress
            (block_id, processed_at, entity_count, relationship_count, error, needs_retry, last_attempt_at, retry_count)
            VALUES (?, ?, ?, ?, NULL, 0, ?, 0)
            """,
            (block_id, now, entity_count, relationship_count, now)
        )
        self.conn.commit()

    def record_error(self, block_id: str, error_text: str) -> None:
        now = iso_now()
        row = self.conn.execute(
            "SELECT retry_count FROM backfill_progress WHERE block_id = ?",
            (block_id,)
        ).fetchone()
        retry_count = (row[0] if row and row[0] else 0) + 1
        self.conn.execute(
            """
            INSERT OR REPLACE INTO backfill_progress
            (block_id, processed_at, entity_count, relationship_count, error, needs_retry, last_attempt_at, retry_count)
            VALUES (?, ?, 0, 0, ?, 1, ?, ?)
            """,
            (block_id, now, error_text[:1000], now, retry_count)
        )
        self.conn.commit()

    def stats(self) -> Dict[str, int]:
        processed = self.conn.execute(
            "SELECT COUNT(*) FROM backfill_progress WHERE needs_retry = 0"
        ).fetchone()[0]
        errors = self.conn.execute(
            "SELECT COUNT(*) FROM backfill_progress WHERE needs_retry = 1"
        ).fetchone()[0]
        entities = self.conn.execute(
            "SELECT COALESCE(SUM(entity_count), 0) FROM backfill_progress"
        ).fetchone()[0]
        relationships = self.conn.execute(
            "SELECT COALESCE(SUM(relationship_count), 0) FROM backfill_progress"
        ).fetchone()[0]
        return {
            "processed": processed,
            "errors": errors,
            "entities": entities,
            "relationships": relationships,
        }

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()


def load_control_state() -> Dict[str, Optional[str]]:
    if CONTROL_FILE.exists():
        try:
            return json.loads(CONTROL_FILE.read_text())
        except json.JSONDecodeError:
            LOG.warning("Malformed control file, resetting")
    return {"state": "active", "started": iso_now(), "last_run": None}


def save_control_state(state: Dict[str, Optional[str]]) -> None:
    CONTROL_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTROL_FILE.write_text(json.dumps(state))


def mark_last_run() -> None:
    state = load_control_state()
    state["last_run"] = iso_now()
    save_control_state(state)


def load_legacy_totals() -> (int, int):
    if not PROGRESS_FILE.exists():
        return 0, 0
    try:
        data = json.loads(PROGRESS_FILE.read_text())
        return (
            data.get("total_entities_extracted", 0),
            data.get("total_relationships_extracted", 0)
        )
    except json.JSONDecodeError:
        LOG.warning("Legacy progress JSON is malformed")
        return 0, 0


def get_unprocessed_blocks(limit: int = 50, sample_mode: bool = False, processed_ids: Optional[Set[str]] = None) -> list:
    """Get blocks that haven't been processed yet."""
    processed_ids = processed_ids or set()

    conn = sqlite3.connect(str(VECTORS_DB))
    cursor = conn.cursor()

    if sample_mode:
        cursor.execute("""
            SELECT b.id, b.content, r.path
            FROM blocks b
            JOIN resources r ON b.resource_id = r.id
            WHERE b.content IS NOT NULL
            AND LENGTH(b.content) > 100
            AND LENGTH(b.content) < 3000
            ORDER BY r.last_indexed_at DESC
            LIMIT ?
        """, (limit * 2,))
    else:
        cursor.execute("""
            SELECT b.id, b.content, r.path
            FROM blocks b
            JOIN resources r ON b.resource_id = r.id
            WHERE b.content IS NOT NULL
            AND LENGTH(b.content) > 100
            ORDER BY r.last_indexed_at DESC
        """)

    blocks = []
    for row in cursor.fetchall():
        block_id, content, path = row
        if block_id in processed_ids:
            continue
        blocks.append({
            "block_id": block_id,
            "content": content,
            "path": path
        })
        if len(blocks) >= limit:
            break

    conn.close()
    return blocks


def get_status() -> dict:
    progress = BackfillProgressStore(BRAIN_DB)
    stats = progress.stats()
    progress.close()

    conn = sqlite3.connect(str(VECTORS_DB))
    total_blocks = conn.execute(
        "SELECT COUNT(*) FROM blocks WHERE content IS NOT NULL AND LENGTH(content) > 100"
    ).fetchone()[0]
    conn.close()

    control = load_control_state()

    legacy_entities, legacy_relationships = load_legacy_totals()
    entities_value = max(stats["entities"], legacy_entities)
    relationships_value = max(stats["relationships"], legacy_relationships)

    return {
        "total_blocks": total_blocks,
        "processed": stats["processed"],
        "remaining": max(total_blocks - stats["processed"], 0),
        "percent": round(stats["processed"] / total_blocks * 100, 1) if total_blocks > 0 else 0,
        "entities_extracted": entities_value,
        "relationships_extracted": relationships_value,
        "errors": stats["errors"],
        "started_at": control.get("started"),
        "last_run": control.get("last_run"),
    }


def run_backfill(batch_size: int = 50, sample_mode: bool = False) -> dict:
    progress_store = BackfillProgressStore(BRAIN_DB)
    processed = progress_store.processed_block_ids()
    blocks = get_unprocessed_blocks(batch_size, sample_mode, processed)

    if not blocks:
        LOG.info("No unprocessed blocks remaining")
        progress_store.close()
        return {"processed": 0, "entities": 0, "relationships": 0}

    LOG.info(f"Processing {len(blocks)} blocks...")
    graph = GraphStore(str(BRAIN_DB))

    entities_total = 0
    relationships_total = 0
    processed_count = 0

    try:
        for i, block in enumerate(blocks):
            block_id = block["block_id"]
            content = block["content"]
            path = block["path"]

            LOG.info(f"[{i+1}/{len(blocks)}] Processing {path[-60:]}...")

            try:
                entities, relationships = extract_entities(content, use_cache=True)

                for entity in entities:
                    graph.add_entity(
                        entity.name,
                        entity.type,
                        entity.context,
                        source_block_id=block_id
                    )
                for rel in relationships:
                    graph.add_relationship(
                        rel.from_entity,
                        rel.to_entity,
                        rel.relation_type,
                        rel.context,
                        source_block_id=block_id
                    )

                entities_total += len(entities)
                relationships_total += len(relationships)
                processed_count += 1

                progress_store.record_success(block_id, len(entities), len(relationships))

                LOG.info(f"  Extracted {len(entities)} entities, {len(relationships)} relationships")

            except Exception as exc:
                LOG.error(f"  Error processing block {block_id}: {exc}")
                progress_store.record_error(block_id, str(exc))

            if i < len(blocks) - 1:
                time.sleep(MIN_DELAY_BETWEEN_EXTRACTIONS)
    finally:
        graph.close()
        progress_store.close()
        mark_last_run()

    LOG.info(f"Batch complete: {processed_count} blocks, {entities_total} entities, {relationships_total} relationships")
    return {
        "processed": processed_count,
        "entities": entities_total,
        "relationships": relationships_total
    }


def reset_progress() -> None:
    if PROGRESS_FILE.exists():
        LOG.info("Legacy progress JSON file preserved at %s", PROGRESS_FILE)

    conn = sqlite3.connect(str(BRAIN_DB))
    conn.execute("DELETE FROM backfill_progress")
    conn.commit()
    conn.close()
    LOG.info("Progress reset")

    state = {"state": "active", "started": iso_now(), "last_run": None}
    save_control_state(state)


def main() -> int:
    parser = argparse.ArgumentParser(description="N5 Graph Backfill")
    parser.add_argument("--batch", type=int, default=50, help="Batch size")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--reset", action="store_true", help="Reset progress")
    parser.add_argument("--sample", type=int, help="Sample mode: process only N docs")
    args = parser.parse_args()

    if args.status:
        status = get_status()
        print(f"""
N5 Graph Backfill Status
========================
Total blocks:    {status['total_blocks']:,}
Processed:       {status['processed']:,} ({status['percent']}%)
Remaining:       {status['remaining']:,}

Entities:        {status['entities_extracted']:,}
Relationships:   {status['relationships_extracted']:,}
Errors recorded: {status['errors']}

Started:         {status['started_at'] or 'Unknown'}
Last run:        {status['last_run'] or 'Never'}
""")
        return 0

    if args.reset:
        reset_progress()
        return 0

    if args.sample:
        result = run_backfill(batch_size=args.sample, sample_mode=True)
    else:
        result = run_backfill(batch_size=args.batch)

    print(f"\nResult: {result['processed']} blocks → {result['entities']} entities, {result['relationships']} relationships")
    return 0


if __name__ == "__main__":
    sys.exit(main())
