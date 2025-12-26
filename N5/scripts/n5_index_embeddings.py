#!/usr/bin/env python3
"""
N5 Semantic Index Embeddings Script
Re-index critical areas with text-embedding-3-large model.
Handles rate limiting, resumability, and dimension upgrades.
"""

import argparse
import hashlib
import logging
import os
import sys
import time
from pathlib import Path
from typing import List, Optional, Set

import sqlite3
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from N5.cognition.n5_memory_client import N5MemoryClient

LOG = logging.getLogger("n5_index_embeddings")
logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")

# Critical areas to index (priority order)
CRITICAL_PATHS = [
    "/home/workspace/N5/capabilities",
    "/home/workspace/N5/prefs",
    "/home/workspace/N5/docs",
    "/home/workspace/N5/schemas",
    "/home/workspace/Knowledge",
    "/home/workspace/Personal/Knowledge",
    "/home/workspace/Prompts",
    "/home/workspace/N5/scripts",  # Just the MD files
]

# Exclusions
EXCLUDE_PATTERNS = [
    "transcript",
    ".transcript.",
    "__pycache__",
    ".git",
    "node_modules",
    ".EXPUNGED",
    "_DEPRECATED",
    "Archive/",
    "Trash/",
]


def should_skip(path: str) -> bool:
    """Check if path should be skipped based on exclusion patterns."""
    path_lower = path.lower()
    for pattern in EXCLUDE_PATTERNS:
        if pattern.lower() in path_lower:
            return True
    return False


def get_files_to_index(paths: List[str], extensions: Set[str] = {".md"}) -> List[Path]:
    """Collect all files to index from given paths."""
    files = []
    for root_path in paths:
        root = Path(root_path)
        if not root.exists():
            LOG.warning(f"Path does not exist: {root_path}")
            continue
            
        if root.is_file():
            if root.suffix in extensions and not should_skip(str(root)):
                files.append(root)
        else:
            for f in root.rglob("*"):
                if f.is_file() and f.suffix in extensions and not should_skip(str(f)):
                    files.append(f)
    return files


def read_utf8_strict(path: Path) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError as e:
        LOG.warning(f"SKIP (non-UTF8): {path} ({e})")
        return None


def check_needs_reindex(conn: sqlite3.Connection, path: str, expected_dim: int = 3072) -> bool:
    """Check if a file needs re-indexing (wrong dimension or changed content)."""
    cursor = conn.cursor()
    
    # Get resource ID
    resource_id = hashlib.md5(path.encode('utf-8')).hexdigest()
    
    # Check if resource exists
    cursor.execute("SELECT hash FROM resources WHERE id = ?", (resource_id,))
    row = cursor.fetchone()
    
    if not row:
        return True  # Not indexed
    
    # Check current file hash
    try:
        content = read_utf8_strict(Path(path))
        if content is None:
            return False
        current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        if row[0] != current_hash:
            return True  # Content changed
    except Exception:
        return True
    
    # Check embedding dimension
    cursor.execute("""
        SELECT v.embedding FROM vectors v
        JOIN blocks b ON v.block_id = b.id
        WHERE b.resource_id = ?
        LIMIT 1
    """, (resource_id,))
    vec_row = cursor.fetchone()
    
    if not vec_row:
        return True  # No vectors
    
    emb = np.frombuffer(vec_row[0], dtype=np.float32)
    if len(emb) != expected_dim:
        return True  # Wrong dimension
    
    return False


def index_file_safe(client: N5MemoryClient, path: Path, batch_delay: float = 0.15) -> bool:
    """Index a single file with error handling and rate limiting."""
    try:
        content = read_utf8_strict(path)
        if content is None:
            return False

        if not content.strip():
            LOG.debug(f"Skipping empty file: {path}")
            return False

        content_date = client.extract_content_date(str(path))
        client.index_file(str(path), content, content_date)

        time.sleep(batch_delay)  # Rate limiting between files
        return True

    except Exception as e:
        LOG.error(f"Failed to index {path}: {e}")
        if "rate" in str(e).lower() or "429" in str(e):
            LOG.warning("Rate limited - waiting 30 seconds...")
            time.sleep(30)
        return False


def main():
    parser = argparse.ArgumentParser(description="Index critical N5 areas with large embedding model")
    parser.add_argument("--paths", nargs="+", help="Custom paths to index (overrides defaults)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of files to process (0=unlimited)")
    parser.add_argument("--force", action="store_true", help="Force re-index even if already indexed")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be indexed without doing it")
    parser.add_argument("--batch-delay", type=float, default=0.15, help="Delay between files (seconds)")
    args = parser.parse_args()
    
    paths = args.paths if args.paths else CRITICAL_PATHS
    
    LOG.info("=" * 60)
    LOG.info("N5 SEMANTIC INDEX - Large Embedding Model Upgrade")
    LOG.info("=" * 60)
    
    # Initialize client
    client = N5MemoryClient()
    LOG.info(f"Provider: {client.provider}, Model: {client.openai_model}")
    
    if client.provider != "openai":
        LOG.error("OpenAI provider not available. Check API key.")
        sys.exit(1)
    
    # Collect files
    files = get_files_to_index(paths)
    LOG.info(f"Found {len(files)} candidate files")
    
    # Filter to those needing indexing
    conn = client._get_db()
    if args.force:
        to_index = files
    else:
        to_index = [f for f in files if check_needs_reindex(conn, str(f), expected_dim=3072)]
    
    LOG.info(f"Files needing (re)indexing: {len(to_index)}")
    
    if args.limit > 0:
        to_index = to_index[:args.limit]
        LOG.info(f"Limited to {len(to_index)} files")
    
    if args.dry_run:
        LOG.info("DRY RUN - would index:")
        for f in to_index[:20]:
            LOG.info(f"  {f}")
        if len(to_index) > 20:
            LOG.info(f"  ... and {len(to_index) - 20} more")
        return
    
    # Index files
    success = 0
    failed = 0
    
    for i, path in enumerate(to_index):
        LOG.info(f"[{i+1}/{len(to_index)}] Indexing: {path}")
        if index_file_safe(client, path, args.batch_delay):
            success += 1
        else:
            failed += 1
        
        # Progress checkpoint every 50 files
        if (i + 1) % 50 == 0:
            LOG.info(f"Checkpoint: {success} success, {failed} failed, {len(to_index) - i - 1} remaining")
    
    LOG.info("=" * 60)
    LOG.info(f"COMPLETE: {success} indexed, {failed} failed")
    LOG.info("=" * 60)


if __name__ == "__main__":
    main()





