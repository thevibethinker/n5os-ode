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
PROGRESS_FILE = "/home/workspace/N5/cognition/backfill_progress.json"

# Rate limit: 500 RPM = 8.3/sec, target 7/sec to be safe
RATE_LIMIT_SEMAPHORE = Semaphore(7)  # Max concurrent
REQUESTS_PER_SECOND = 7.0
last_request_time = [0.0]  # Mutable for closure

import sys
sys.path.insert(0, "/home/workspace")
from N5.cognition.entity_extractor import extract_entities
from N5.cognition.graph_store import GraphStore


def load_progress() -> dict:
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {
        "processed_block_ids": [],
        "total_entities_extracted": 0,
        "total_relationships_extracted": 0,
        "errors": [],
        "started_at": None,
        "last_run_at": None
    }


def save_progress(progress: dict):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)


def get_unprocessed_blocks(limit: int = 500) -> list:
    progress = load_progress()
    processed = set(progress.get("processed_block_ids", []))
    
    conn = sqlite3.connect(VECTORS_DB)
    cursor = conn.cursor()
    
    cursor.execute("CREATE TEMP TABLE IF NOT EXISTS processed_ids (id TEXT PRIMARY KEY)")
    cursor.execute("DELETE FROM processed_ids")
    
    for i in range(0, len(processed), 500):
        batch = list(processed)[i:i+500]
        cursor.executemany("INSERT OR IGNORE INTO processed_ids VALUES (?)", [(x,) for x in batch])
    
    cursor.execute("""
        SELECT b.id, b.content, r.path
        FROM blocks b
        JOIN resources r ON b.resource_id = r.id
        LEFT JOIN processed_ids p ON b.id = p.id
        WHERE b.content IS NOT NULL
        AND LENGTH(b.content) > 100
        AND p.id IS NULL
        ORDER BY LENGTH(b.content)
        LIMIT ?
    """, (limit,))
    
    blocks = [{"block_id": row[0], "content": row[1], "path": row[2]} for row in cursor.fetchall()]
    conn.close()
    
    return blocks


def process_single_block(block: dict) -> dict:
    """Process a single block with rate limiting."""
    # Rate limit
    with RATE_LIMIT_SEMAPHORE:
        # Ensure minimum spacing between requests
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


async def run_parallel_backfill(batch_size: int = 400, max_workers: int = 15) -> dict:
    """Run parallel backfill with rate limiting."""
    progress = load_progress()
    
    if not progress.get("started_at"):
        progress["started_at"] = datetime.now().isoformat()
    
    blocks = get_unprocessed_blocks(batch_size)
    
    if not blocks:
        LOG.info("No unprocessed blocks remaining!")
        return {"processed": 0, "entities": 0, "relationships": 0}
    
    LOG.info(f"Processing {len(blocks)} blocks with {max_workers} workers (rate limited to ~7 req/sec)...")
    
    start_time = time.time()
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = await asyncio.gather(*[
            loop.run_in_executor(executor, process_single_block, block)
            for block in blocks
        ])
    
    extract_time = time.time() - start_time
    LOG.info(f"Extraction complete in {extract_time:.1f}s ({len(blocks)/extract_time:.1f} blocks/sec)")
    
    graph = GraphStore(BRAIN_DB)
    
    entities_total = 0
    relationships_total = 0
    errors = 0
    
    for result in results:
        if result["error"]:
            errors += 1
            progress["errors"].append({
                "block_id": result["block_id"],
                "path": result["path"],
                "error": result["error"],
                "time": datetime.now().isoformat()
            })
            progress["processed_block_ids"].append(result["block_id"])
            continue
        
        block_id = result["block_id"]
        
        for entity in result["entities"]:
            graph.add_entity(
                entity.name,
                entity.type,
                entity.context,
                source_block_id=block_id
            )
        
        for rel in result["relationships"]:
            graph.add_relationship(
                rel.from_entity,
                rel.to_entity,
                rel.relation_type,
                rel.context,
                source_block_id=block_id
            )
        
        entities_total += len(result["entities"])
        relationships_total += len(result["relationships"])
        progress["processed_block_ids"].append(block_id)
    
    graph.close()
    
    progress["total_entities_extracted"] = progress.get("total_entities_extracted", 0) + entities_total
    progress["total_relationships_extracted"] = progress.get("total_relationships_extracted", 0) + relationships_total
    progress["last_run_at"] = datetime.now().isoformat()
    save_progress(progress)
    
    total_time = time.time() - start_time
    LOG.info(f"Batch: {len(blocks)} blocks, {entities_total} ents, {relationships_total} rels, {errors} errors ({len(blocks)/total_time:.1f} b/s)")
    
    return {
        "processed": len(blocks),
        "entities": entities_total,
        "relationships": relationships_total,
        "errors": errors
    }


def get_status() -> dict:
    progress = load_progress()
    
    conn = sqlite3.connect(VECTORS_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM blocks WHERE content IS NOT NULL AND LENGTH(content) > 100")
    total = cursor.fetchone()[0]
    conn.close()
    
    processed = len(progress.get("processed_block_ids", []))
    
    return {
        "total": total,
        "processed": processed,
        "remaining": total - processed,
        "pct": round(processed / total * 100, 1) if total > 0 else 0,
        "entities_extracted": progress.get("total_entities_extracted", 0),
        "relationships_extracted": progress.get("total_relationships_extracted", 0),
        "errors": len(progress.get("errors", [])),
        "started_at": progress.get("started_at"),
        "last_run_at": progress.get("last_run_at")
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
""")
        return
    
    for i in range(args.loops):
        if args.loops > 1 and i % 10 == 0:
            LOG.info(f"=== Loop {i+1}/{args.loops} ===")
        
        result = await run_parallel_backfill(args.batch, args.workers)
        
        if result["processed"] == 0:
            LOG.info("Backfill complete!")
            break
        
        if i < args.loops - 1:
            await asyncio.sleep(1)
    
    s = get_status()
    LOG.info(f"Final: {s['processed']:,}/{s['total']:,} ({s['pct']}%)")


if __name__ == "__main__":
    asyncio.run(main())
