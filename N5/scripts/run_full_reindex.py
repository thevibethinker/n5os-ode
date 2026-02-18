#!/usr/bin/env python3
"""
Memory-efficient re-indexer for N5 brain.db with text-embedding-3-large.
Processes files one at a time with explicit cleanup.
"""
import gc
import hashlib
import logging
import os
import sys
import time
from pathlib import Path

# Add workspace to path FIRST
sys.path.insert(0, '/home/workspace')
os.chdir('/home/workspace')

LOG_FILE = "/home/workspace/N5/logs/reindex_large_model.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
LOG = logging.getLogger("reindex")

CRITICAL_PATHS = [
    "/home/workspace/N5/capabilities",
    "/home/workspace/N5/prefs",
    "/home/workspace/N5/docs",
    "/home/workspace/N5/schemas",
    "/home/workspace/N5/workflows",
    "/home/workspace/Knowledge",
    "/home/workspace/Personal/Knowledge",
    "/home/workspace/Prompts",
]

EXCLUDE = ["transcript", "__pycache__", ".git", "node_modules", "Archive/", "Trash/", ".EXPUNGED"]

def should_skip(p):
    pl = p.lower()
    return any(x.lower() in pl for x in EXCLUDE)

def collect_files():
    files = []
    for root in CRITICAL_PATHS:
        rp = Path(root)
        if not rp.exists():
            continue
        for f in rp.rglob("*.md"):
            if not should_skip(str(f)):
                files.append(str(f))
    return sorted(set(files))

def main():
    # Import here to control memory
    from N5.cognition.n5_memory_client import N5MemoryClient
    
    LOG.info("=" * 70)
    LOG.info("N5 FULL RE-INDEX WITH text-embedding-3-large")
    LOG.info("=" * 70)
    
    client = N5MemoryClient()
    LOG.info(f"Provider: {client.provider}, Model: {client.openai_model}")
    
    if client.provider != "openai":
        LOG.error("OpenAI not available")
        sys.exit(1)
    
    files = collect_files()
    total = len(files)
    LOG.info(f"Total files: {total}")
    
    success, failed, skipped = 0, 0, 0
    
    for i, fpath in enumerate(files):
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                skipped += 1
                continue
            
            content_date = client.extract_content_date(fpath)
            client.index_file(fpath, content, content_date)
            success += 1
            
            # Force cleanup every file
            del content
            gc.collect()
            
            if (i + 1) % 20 == 0:
                LOG.info(f"[{i+1}/{total}] S:{success} F:{failed} S:{skipped}")
            
            time.sleep(0.15)  # Rate limit
            
        except Exception as e:
            LOG.error(f"Failed {fpath}: {e}")
            failed += 1
            if "rate" in str(e).lower():
                time.sleep(30)
            else:
                time.sleep(1)
            gc.collect()
    
    LOG.info("=" * 70)
    LOG.info(f"DONE: {success} indexed, {failed} failed, {skipped} skipped")
    LOG.info("=" * 70)
    
    with open("/home/workspace/N5/logs/reindex_complete.marker", "w") as f:
        f.write(f"Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"S:{success} F:{failed} K:{skipped}\n")

if __name__ == "__main__":
    main()

