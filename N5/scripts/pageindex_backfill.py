#!/usr/bin/env python3
"""
PageIndex Backfill — Index existing documents with PageIndex.

Processes:
1. Content Library items (articles, papers, social-posts, frameworks)
2. Personal/Knowledge tier documents

Usage:
    # Dry run
    python3 N5/scripts/pageindex_backfill.py --dry-run
    
    # Content Library only
    python3 N5/scripts/pageindex_backfill.py --source content-library
    
    # Knowledge tier only
    python3 N5/scripts/pageindex_backfill.py --source knowledge
    
    # Full backfill
    python3 N5/scripts/pageindex_backfill.py --source all
    
    # Single file
    python3 N5/scripts/pageindex_backfill.py --file /path/to/doc.pdf
"""

import argparse
import hashlib
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Add workspace to path
sys.path.insert(0, "/home/workspace")

from N5.cognition.pageindex.pageindex_store import PageIndexStore

LOG = logging.getLogger("pageindex_backfill")

# Paths
WORKSPACE = Path("/home/workspace")
CONTENT_LIBRARY_DB = WORKSPACE / "N5/data/content_library.db"
CONTENT_LIBRARY_DIR = WORKSPACE / "Knowledge/content-library"
KNOWLEDGE_DIR = WORKSPACE / "Personal/Knowledge"
PROGRESS_FILE = WORKSPACE / "N5/cognition/pageindex/backfill_progress.json"

# Content types eligible for PageIndex
ELIGIBLE_CONTENT_TYPES = ["article", "paper", "deck", "framework", "social-post"]

# File extensions to process
ELIGIBLE_EXTENSIONS = [".md", ".markdown", ".pdf"]


def get_content_library_items() -> List[Dict]:
    """Get eligible items from content library directory.
    
    Scans the content-library directories directly since DB doesn't track file paths.
    """
    if not CONTENT_LIBRARY_DIR.exists():
        LOG.warning(f"Content library dir not found: {CONTENT_LIBRARY_DIR}")
        return []
    
    # Map directories to content types
    dir_type_map = {
        "articles": "article",
        "social-posts": "social-post",
        "papers": "paper",
        "decks": "deck",
        "frameworks": "framework",
        "inspiration": "inspiration"
    }
    
    items = []
    for dirname, content_type in dir_type_map.items():
        dir_path = CONTENT_LIBRARY_DIR / dirname
        if not dir_path.exists():
            continue
        
        for ext in ELIGIBLE_EXTENSIONS:
            for filepath in dir_path.rglob(f"*{ext}"):
                # Skip hidden files
                if filepath.name.startswith("."):
                    continue
                
                # Generate stable ID from path
                resource_id = hashlib.md5(str(filepath).encode()).hexdigest()
                
                items.append({
                    "id": resource_id,
                    "title": filepath.stem,
                    "content_type": content_type,
                    "file_path": str(filepath),
                    "source": "content-library"
                })
    
    return items


def get_knowledge_tier_docs() -> List[Dict]:
    """Get documents from Personal/Knowledge directory."""
    if not KNOWLEDGE_DIR.exists():
        LOG.warning(f"Knowledge directory not found: {KNOWLEDGE_DIR}")
        return []
    
    items = []
    for ext in ELIGIBLE_EXTENSIONS:
        for filepath in KNOWLEDGE_DIR.rglob(f"*{ext}"):
            # Skip certain directories
            rel_path = filepath.relative_to(KNOWLEDGE_DIR)
            if any(part.startswith(".") or part in ["Archive", "archive", "deprecated"] 
                   for part in rel_path.parts):
                continue
            
            # Generate stable ID from path
            resource_id = hashlib.md5(str(filepath).encode()).hexdigest()
            
            items.append({
                "id": resource_id,
                "title": filepath.stem,
                "content_type": "knowledge-doc",
                "file_path": str(filepath),
                "source": "knowledge-tier"
            })
    
    return items


def load_progress() -> Dict:
    """Load backfill progress from file."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {
        "processed_ids": [],
        "failed_ids": [],
        "started_at": None,
        "last_updated": None,
        "stats": {
            "content_library": {"total": 0, "processed": 0, "failed": 0},
            "knowledge_tier": {"total": 0, "processed": 0, "failed": 0}
        }
    }


def save_progress(progress: Dict):
    """Save backfill progress to file."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    progress["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def backfill_item(store: PageIndexStore, item: Dict, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Backfill a single item.
    
    Returns:
        (success: bool, message: str)
    """
    file_path = item["file_path"]
    resource_id = item["id"]
    
    # Check if already indexed
    if store.has_tree(resource_id):
        return True, "already indexed"
    
    if dry_run:
        return True, "would index"
    
    # Index the document
    LOG.info(f"Indexing: {item['title']} ({item['content_type']})")
    
    tree = store.index_document(file_path, model="gpt-4o")
    if not tree:
        return False, "indexing failed"
    
    # Store the tree
    if store.store_tree(resource_id, tree):
        return True, f"indexed {tree.get('structure', []).__len__()} nodes"
    else:
        return False, "storage failed"


def run_backfill(
    source: str = "all",
    dry_run: bool = False,
    limit: Optional[int] = None,
    single_file: Optional[str] = None
):
    """
    Run the backfill process.
    
    Args:
        source: "content-library", "knowledge", or "all"
        dry_run: If True, don't actually index
        limit: Max items to process (for testing)
        single_file: Process only this file
    """
    store = PageIndexStore()
    progress = load_progress()
    
    if not progress["started_at"]:
        progress["started_at"] = datetime.now().isoformat()
    
    # Collect items to process
    items = []
    
    if single_file:
        # Single file mode
        filepath = Path(single_file)
        if not filepath.exists():
            LOG.error(f"File not found: {single_file}")
            return
        
        resource_id = hashlib.md5(single_file.encode()).hexdigest()
        items = [{
            "id": resource_id,
            "title": filepath.stem,
            "content_type": "manual",
            "file_path": single_file,
            "source": "manual"
        }]
    else:
        if source in ["content-library", "all"]:
            cl_items = get_content_library_items()
            items.extend(cl_items)
            progress["stats"]["content_library"]["total"] = len(cl_items)
            LOG.info(f"Content Library: {len(cl_items)} items")
        
        if source in ["knowledge", "all"]:
            k_items = get_knowledge_tier_docs()
            items.extend(k_items)
            progress["stats"]["knowledge_tier"]["total"] = len(k_items)
            LOG.info(f"Knowledge Tier: {len(k_items)} items")
    
    # Filter already processed
    items = [i for i in items if i["id"] not in progress["processed_ids"]]
    
    if limit:
        items = items[:limit]
    
    LOG.info(f"Processing {len(items)} items (dry_run={dry_run})")
    
    # Process items
    for i, item in enumerate(items):
        try:
            success, message = backfill_item(store, item, dry_run)
            
            if success:
                if not dry_run:
                    progress["processed_ids"].append(item["id"])
                    if item["source"] == "content-library":
                        progress["stats"]["content_library"]["processed"] += 1
                    elif item["source"] == "knowledge-tier":
                        progress["stats"]["knowledge_tier"]["processed"] += 1
                
                LOG.info(f"[{i+1}/{len(items)}] ✓ {item['title']}: {message}")
            else:
                if not dry_run:
                    progress["failed_ids"].append(item["id"])
                    if item["source"] == "content-library":
                        progress["stats"]["content_library"]["failed"] += 1
                    elif item["source"] == "knowledge-tier":
                        progress["stats"]["knowledge_tier"]["failed"] += 1
                
                LOG.warning(f"[{i+1}/{len(items)}] ✗ {item['title']}: {message}")
            
            # Save progress periodically
            if not dry_run and (i + 1) % 10 == 0:
                save_progress(progress)
            
            # Rate limit to avoid API throttling
            if not dry_run and i < len(items) - 1:
                time.sleep(1)
                
        except Exception as e:
            LOG.error(f"Error processing {item['title']}: {e}")
            if not dry_run:
                progress["failed_ids"].append(item["id"])
    
    # Final save
    if not dry_run:
        save_progress(progress)
    
    # Summary
    stats = store.get_stats()
    LOG.info(f"\n=== Backfill Complete ===")
    LOG.info(f"Total trees: {stats['tree_count']}")
    LOG.info(f"Total nodes: {stats['node_count']}")
    LOG.info(f"Content Library: {progress['stats']['content_library']}")
    LOG.info(f"Knowledge Tier: {progress['stats']['knowledge_tier']}")
    
    store.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PageIndex Backfill")
    parser.add_argument("--source", choices=["content-library", "knowledge", "all"], 
                        default="all", help="Source to backfill")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually index")
    parser.add_argument("--limit", type=int, help="Max items to process")
    parser.add_argument("--file", help="Process single file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    
    run_backfill(
        source=args.source,
        dry_run=args.dry_run,
        limit=args.limit,
        single_file=args.file
    )
