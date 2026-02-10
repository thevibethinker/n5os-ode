#!/usr/bin/env python3
"""
N5 Graph Backfill FAST — Parallel entity extraction with rate limiting.
"""

import asyncio
import sqlite3
import json
import os
import time
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from threading import Semaphore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
LOG = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

BRAIN_DB = "/home/workspace/N5/cognition/brain.db"
VECTORS_DB = "/home/workspace/N5/cognition/vectors_v2.db"
CONTROL_FILE = "/home/workspace/N5/config/backfill_control.json"

RATE_LIMIT_SEMAPHORE = Semaphore(7)
REQUESTS_PER_SECOND = 7.0
last_request_time = [0.0]

import sys
sys.path.insert(0, "/home/workspace")
from N5.cognition.entity_extractor import extract_entities
from N5.cognition.graph_store import GraphStore


def ensure_backfill_table(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS backfill_progress (
            block_id TEXT PRIMARY KEY,
            processed_at TEXT DEFAULT (datetime('now')),
            entity_count INTEGER DEFAULT 0,
            relationship_count INTEGER DEFAULT 0,
            error TEXT
        )
    """)


def load_control() -> dict:
    if os.path.exists(CONTROL_FILE):
        with open(CONTROL_FILE) as f:
            return json.load(f)
    return {"state": "active", "started": None, "last_run_at": None, "last_error": None, "error_count": 0}


def save_control(control: dict):
    control["last_run_at"] = datetime.now().isoformat()
    with open(CONTROL_FILE, 'w') as f:
        json.dump(control, f)


def get_processed_ids(conn: sqlite3.Connection) -> set:
    ensure_backfill_table(conn)
    cursor = conn.execute("SELECT block_id FROM backfill_progress")
    return {row[0] for row in cursor.fetchall()}


def record_progress(conn: sqlite3.Connection, block_id: str, entities: int, relationships: int, error: str | None):
    conn.execute(
        "INSERT OR REPLACE INTO backfill_progress (block_id, processed_at, entity_count, relationship_count, error) VALUES (?, datetime('now'), ?, ?, ?)",
        (block_id, entities, relationships, error)
    )
    conn.commit()


def get_unprocessed_blocks(limit: int = 500) -> list:
    conn = sqlite3.connect(VECTORS_DB)
    processed_conn = sqlite3.connect(BRAIN_DB)
    processed = get_processed_ids(processed_conn)
    ensure_backfill_table(processed_conn)

    cursor = conn.cursor()
    if processed:
        placeholders = ",".join("?" for _ in processed)
        cursor.execute(f"""
            SELECT b.id, b.content, r.path
            FROM blocks b
            JOIN resources r ON b.resource_id = r.id
            WHERE b.content IS NOT NULL
            AND LENGTH(b.content) > 100
            AND b.id NOT IN ({placeholders})
            ORDER BY LENGTH(b.content)
            LIMIT ?
        """, tuple(processed) + (limit,))
    else:
        cursor.execute("""
            SELECT b.id, b.content, r.path
            FROM blocks b
            JOIN resources r ON b.resource_id = r.id
            WHERE b.content IS NOT NULL
            AND LENGTH(b.content) > 100
            ORDER BY LENGTH(b.content)
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    processed_conn.close()
    conn.close()

    blocks = [{"block_id": row[0], "content": row[1], "path": row[2]} for row in rows]
    return blocks


def process_single_block(block: dict) -> dict:
    with RATE_LIMIT_SEMAPHORE:
        now = time.time()
        min_interval = 1.0 / REQUESTS_PER_SECOND
        elapsed = now - last_request_time[0]
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        last_request_time[0] = time.time()
        try:
            entities, relationships = extract_entities(block["content"], use_cache=True)
            return {
                "block_id": block["block_id"],
                "path": block["path"],
                "entities": entities,
                "relationships": relationships,
                "error": None
            }
        except Exception as e:
            return {
                "block_id": block["block_id"],
                "path": block["path"],
                "entities": [],
                "relationships": [],
                "error": str(e)
            }


def apply_backoff(failures: int):
    if failures >= 20:
        time.sleep(300)
    elif failures >= 10:
        time.sleep(120)
    elif failures >= 5:
        time.sleep(30)
    elif failures >= 3:
        time.sleep(5)


async def run_parallel_backfill(batch_size: int = 400, max_workers: int = 15) -> dict:
    control = load_control()
    if control.get("state") == "paused":
        LOG.warning("Backfill paused due to previous errors")
        return {"processed": 0, "entities": 0, "relationships": 0, "paused": True}

    if not control.get("started"):
        control["started"] = datetime.now().isoformat()

    blocks = get_unprocessed_blocks(batch_size)
    if not blocks:
        LOG.info("No unprocessed blocks remaining!")
        control["state"] = "complete"
        save_control(control)
        return {"processed": 0, "entities": 0, "relationships": 0}

    LOG.info(f"Processing {len(blocks)} blocks with {max_workers} workers (rate limited to ~7 req/sec)...")
    start_time = time.time()
    failure_streak = 0
    processed = 0
    entities_total = 0
    relationships_total = 0
    errors = 0

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = await asyncio.gather(*[
            loop.run_in_executor(executor, process_single_block, block)
            for block in blocks
        ])

    graph = GraphStore(BRAIN_DB)
    db_conn = sqlite3.connect(BRAIN_DB)
    ensure_backfill_table(db_conn)

    for result in results:
        processed += 1
        if result["error"] or not (result["entities"] or result["relationships"]):
            errors += 1
            failure_streak += 1
            control["last_error"] = result["error"] or "empty response"
            control["error_count"] = control.get("error_count", 0) + 1
            control["state"] = "active"
            apply_backoff(failure_streak)
            if failure_streak >= 20:
                control["state"] = "paused"
                LOG.error("Failure streak exceeded 20, pausing backfill")
                save_control(control)
                break
            continue
        failure_streak = 0
        for entity in result["entities"]:
            graph.add_entity(
                entity.name,
                entity.type,
                entity.context,
                source_block_id=result["block_id"]
            )
        for rel in result["relationships"]:
            graph.add_relationship(
                rel.from_entity,
                rel.to_entity,
                rel.relation_type,
                rel.context,
                source_block_id=result["block_id"]
            )
        entities_total += len(result["entities"])
        relationships_total += len(result["relationships"])
        record_progress(db_conn, result["block_id"], len(result["entities"]), len(result["relationships"]), None)

    graph.close()
    db_conn.close()

    control["processed_block_id"] = processed
    control["total_entities_extracted"] = control.get("total_entities_extracted", 0) + entities_total
    control["total_relationships_extracted"] = control.get("total_relationships_extracted", 0) + relationships_total
    if control.get("state") != "paused":
        control["state"] = "active"
    save_control(control)

    total_time = time.time() - start_time
    LOG.info(f"Batch: {processed} blocks, {entities_total} ents, {relationships_total} rels, {errors} errors")
    return {
        "processed": processed,
        "entities": entities_total,
        "relationships": relationships_total,
        "errors": errors,
        "paused": control.get("state") == "paused"
    }


def get_status() -> dict:
    conn_block = sqlite3.connect(VECTORS_DB)
    cursor = conn_block.cursor()
    cursor.execute("SELECT COUNT(*) FROM blocks WHERE content IS NOT NULL AND LENGTH(content) > 100")
    total = cursor.fetchone()[0]
    conn_block.close()

    conn = sqlite3.connect(BRAIN_DB)
    ensure_backfill_table(conn)
    processed = conn.execute("SELECT COUNT(*) FROM backfill_progress").fetchone()[0]
    conn.close()

    control = load_control()
    return {
        "total": total,
        "processed": processed,
        "remaining": total - processed,
        "pct": round(processed / total * 100, 1) if total > 0 else 0,
        "entities_extracted": control.get("total_entities_extracted", 0),
        "relationships_extracted": control.get("total_relationships_extracted", 0),
        "errors": control.get("error_count", 0),
        "state": control.get("state"),
        "started_at": control.get("started"),
        "last_run_at": control.get("last_run_at")
    }


async def main():
    parser = argparse.ArgumentParser(description="N5 Graph Backfill FAST")
    parser.add_argument("--batch", type=int, default=400, help="Batch size")
    parser.add_argument("--workers", type=int, default=15, help="Parallel workers")
    parser.add_argument("--loops", type=int, default=1, help="Number of batches")
    parser.add_argument("--status", action="store_true", help="Show status")
    args = parser.parse_args()

    if args.status:
        s = get_status()
        print(f"""
N5 Graph Backfill Status
========================
Total blocks:    {s['total']:,}
Processed:       {s['processed']:,} ({s['pct']}%)
Remaining:       {s['remaining']:,}

Entities:        {s['entities_extracted']:,}
Relationships:   {s['relationships_extracted']:,}
Errors:          {s['errors']}
State:           {s['state']}
""")
        return

    for i in range(args.loops):
        if args.loops > 1 and i % 10 == 0:
            LOG.info(f"=== Loop {i+1}/{args.loops} ===")

        result = await run_parallel_backfill(args.batch, args.workers)
        if result.get("paused"):
            LOG.info("Backfill paused. Exiting loops.")
            break
        if result["processed"] == 0:
            LOG.info("Backfill complete!")
            break
        if i < args.loops - 1:
            await asyncio.sleep(1)

    s = get_status()
    LOG.info(f"Final: {s['processed']:,}/{s['total']:,} ({s['pct']}%) state={s['state']}")


if __name__ == "__main__":
    asyncio.run(main())
