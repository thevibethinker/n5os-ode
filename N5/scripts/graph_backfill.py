#!/usr/bin/env python3
"""
N5 Graph Backfill — Extract entities from all indexed documents.

Runs incrementally, tracking progress. Safe to restart.
Uses rate limiting to avoid API overload.

Usage:
    python3 graph_backfill.py              # Process next batch (default 50 docs)
    python3 graph_backfill.py --batch 100  # Process 100 docs
    python3 graph_backfill.py --status     # Show progress
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
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/workspace')

from N5.cognition.entity_extractor import extract_entities
from N5.cognition.graph_store import GraphStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
LOG = logging.getLogger("graph_backfill")

BRAIN_DB = "/home/workspace/N5/cognition/brain.db"
VECTORS_DB = "/home/workspace/N5/cognition/vectors_v2.db"
PROGRESS_FILE = "/home/workspace/N5/cognition/backfill_progress.json"

# Rate limiting
MIN_DELAY_BETWEEN_EXTRACTIONS = 0.75  # seconds


def load_progress() -> dict:
    """Load backfill progress."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        "processed_block_ids": [],
        "total_entities_extracted": 0,
        "total_relationships_extracted": 0,
        "started_at": None,
        "last_run_at": None,
        "errors": []
    }


def save_progress(progress: dict):
    """Save backfill progress."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, default=str)


def get_unprocessed_blocks(limit: int = 50, sample_mode: bool = False) -> list:
    """Get blocks that haven't been processed yet."""
    progress = load_progress()
    processed = set(progress.get("processed_block_ids", []))
    
    conn = sqlite3.connect(VECTORS_DB)
    cursor = conn.cursor()
    
    if sample_mode:
        # Get blocks from most-accessed resources (by path frequency in searches)
        # For now, prioritize shorter content (more likely to be high-signal)
        cursor.execute("""
            SELECT b.id, b.content, r.path
            FROM blocks b
            JOIN resources r ON b.resource_id = r.id
            WHERE b.content IS NOT NULL
            AND LENGTH(b.content) > 100
            AND LENGTH(b.content) < 3000
            ORDER BY r.last_indexed_at DESC
            LIMIT ?
        """, (limit * 2,))  # Get more, filter processed in Python
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
        if block_id not in processed:
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
    """Get backfill status."""
    progress = load_progress()
    
    conn = sqlite3.connect(VECTORS_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM blocks WHERE content IS NOT NULL AND LENGTH(content) > 100")
    total_blocks = cursor.fetchone()[0]
    conn.close()
    
    processed = len(progress.get("processed_block_ids", []))
    
    return {
        "total_blocks": total_blocks,
        "processed": processed,
        "remaining": total_blocks - processed,
        "percent": round(processed / total_blocks * 100, 1) if total_blocks > 0 else 0,
        "entities_extracted": progress.get("total_entities_extracted", 0),
        "relationships_extracted": progress.get("total_relationships_extracted", 0),
        "errors": len(progress.get("errors", [])),
        "started_at": progress.get("started_at"),
        "last_run_at": progress.get("last_run_at")
    }


def run_backfill(batch_size: int = 50, sample_mode: bool = False) -> dict:
    """Run one batch of backfill."""
    progress = load_progress()
    
    if not progress.get("started_at"):
        progress["started_at"] = datetime.now().isoformat()
    
    blocks = get_unprocessed_blocks(batch_size, sample_mode)
    
    if not blocks:
        LOG.info("No unprocessed blocks remaining")
        return {"processed": 0, "entities": 0, "relationships": 0}
    
    LOG.info(f"Processing {len(blocks)} blocks...")
    
    graph = GraphStore(BRAIN_DB)
    
    entities_total = 0
    relationships_total = 0
    processed = 0
    
    for i, block in enumerate(blocks):
        block_id = block["block_id"]
        content = block["content"]
        path = block["path"]
        
        LOG.info(f"[{i+1}/{len(blocks)}] Processing {path[-50:]}...")
        
        try:
            entities, relationships = extract_entities(content, use_cache=True)
            
            # Store entities
            for entity in entities:
                graph.add_entity(
                    entity.name,
                    entity.type,
                    entity.context,
                    source_block_id=block_id
                )
            
            # Store relationships
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
            
            progress["processed_block_ids"].append(block_id)
            progress["total_entities_extracted"] = progress.get("total_entities_extracted", 0) + len(entities)
            progress["total_relationships_extracted"] = progress.get("total_relationships_extracted", 0) + len(relationships)
            
            processed += 1
            
            LOG.info(f"  Extracted {len(entities)} entities, {len(relationships)} relationships")
            
        except Exception as e:
            LOG.error(f"  Error: {e}")
            progress["errors"].append({
                "block_id": block_id,
                "path": path,
                "error": str(e),
                "time": datetime.now().isoformat()
            })
            # Still mark as processed to avoid infinite retry
            progress["processed_block_ids"].append(block_id)
        
        # Rate limiting
        if i < len(blocks) - 1:
            time.sleep(MIN_DELAY_BETWEEN_EXTRACTIONS)
        
        # Save progress periodically
        if (i + 1) % 10 == 0:
            progress["last_run_at"] = datetime.now().isoformat()
            save_progress(progress)
    
    graph.close()
    
    progress["last_run_at"] = datetime.now().isoformat()
    save_progress(progress)
    
    LOG.info(f"Batch complete: {processed} blocks, {entities_total} entities, {relationships_total} relationships")
    
    return {
        "processed": processed,
        "entities": entities_total,
        "relationships": relationships_total
    }


def reset_progress():
    """Reset backfill progress."""
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        LOG.info("Progress reset")
    else:
        LOG.info("No progress file to reset")


def main():
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
Errors:          {status['errors']}

Started:         {status['started_at'] or 'Never'}
Last run:        {status['last_run_at'] or 'Never'}
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
