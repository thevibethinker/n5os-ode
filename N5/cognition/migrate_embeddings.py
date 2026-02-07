#!/usr/bin/env python3
"""
Re-embedding Migration: brain.db (384-dim) → vectors_v2.db (3072-dim)

Uses OpenAI text-embedding-3-large.
Processes in batches of 100 to handle rate limits.
"""

import sqlite3
import os
import sys
import time
import json
from datetime import datetime
from openai import OpenAI

# Config
SOURCE_DB = "/home/workspace/N5/cognition/brain.db"
TARGET_DB = "/home/workspace/N5/cognition/vectors_v2.db"
BATCH_SIZE = 100
MODEL = "text-embedding-3-large"
CHECKPOINT_FILE = "/home/workspace/N5/cognition/migration_checkpoint.json"

def get_embedding(client, texts):
    """Get embeddings for a batch of texts."""
    response = client.embeddings.create(
        model=MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]

def load_checkpoint():
    """Load migration checkpoint if exists."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {"last_block_id": None, "processed": 0, "errors": 0}

def save_checkpoint(checkpoint):
    """Save migration checkpoint."""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f)

def migrate():
    client = OpenAI()
    
    # Connect to databases
    source = sqlite3.connect(SOURCE_DB)
    target = sqlite3.connect(TARGET_DB)
    
    checkpoint = load_checkpoint()
    
    # First, copy resources and blocks (structure only, not vectors)
    if checkpoint["processed"] == 0:
        print("Copying resources and blocks structure...")
        source_cur = source.cursor()
        target_cur = target.cursor()
        
        # Copy resources
        source_cur.execute("SELECT * FROM resources")
        resources = source_cur.fetchall()
        target_cur.executemany(
            "INSERT OR REPLACE INTO resources VALUES (?,?,?,?,?)",
            resources
        )
        print(f"  Copied {len(resources)} resources")
        
        # Copy blocks
        source_cur.execute("SELECT * FROM blocks")
        blocks = source_cur.fetchall()
        target_cur.executemany(
            "INSERT OR REPLACE INTO blocks VALUES (?,?,?,?,?,?,?,?)",
            blocks
        )
        print(f"  Copied {len(blocks)} blocks")
        
        target.commit()
    
    # Get total count
    source_cur = source.cursor()
    source_cur.execute("SELECT COUNT(*) FROM blocks")
    total = source_cur.fetchone()[0]
    
    print(f"\nMigrating {total} blocks to {MODEL}...")
    print(f"Starting from checkpoint: {checkpoint['processed']} already done")
    
    # Process in batches
    offset = checkpoint["processed"]
    batch_num = offset // BATCH_SIZE
    
    while offset < total:
        batch_num += 1
        
        # Get batch of blocks
        source_cur.execute("""
            SELECT id, content FROM blocks 
            ORDER BY id
            LIMIT ? OFFSET ?
        """, (BATCH_SIZE, offset))
        
        rows = source_cur.fetchall()
        if not rows:
            break
        
        block_ids = [r[0] for r in rows]
        contents = [r[1][:8000] for r in rows]  # Truncate to avoid token limits
        
        try:
            # Get embeddings
            embeddings = get_embedding(client, contents)
            
            # Insert into target
            target_cur = target.cursor()
            import numpy as np
            for block_id, emb in zip(block_ids, embeddings):
                emb_blob = np.array(emb, dtype=np.float32).tobytes()
                target_cur.execute(
                    "INSERT OR REPLACE INTO vectors (block_id, embedding) VALUES (?, ?)",
                    (block_id, emb_blob)
                )
            
            target.commit()
            
            offset += len(rows)
            checkpoint["processed"] = offset
            checkpoint["last_block_id"] = block_ids[-1]
            save_checkpoint(checkpoint)
            
            pct = (offset / total) * 100
            print(f"  Batch {batch_num}: {offset}/{total} ({pct:.1f}%)")
            
            # Rate limit: ~3000 RPM for embeddings, be conservative
            time.sleep(0.5)
            
        except Exception as e:
            checkpoint["errors"] += 1
            save_checkpoint(checkpoint)
            print(f"  ERROR in batch {batch_num}: {e}")
            if checkpoint["errors"] > 10:
                print("Too many errors, stopping")
                break
            time.sleep(5)  # Back off on errors
    
    # Final stats
    target_cur = target.cursor()
    target_cur.execute("SELECT COUNT(*) FROM vectors")
    final_count = target_cur.fetchone()[0]
    
    print(f"\n✅ Migration complete!")
    print(f"   Vectors migrated: {final_count}")
    print(f"   Errors: {checkpoint['errors']}")
    
    source.close()
    target.close()
    
    return final_count, checkpoint["errors"]

if __name__ == "__main__":
    migrate()
