#!/usr/bin/env python3
"""Phase 4: Inbox Cleanup - Archive dated export folders"""
import json
import logging
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
INBOX = WORKSPACE / "Inbox"
ARCHIVE_BASE = WORKSPACE / ".archive_2025-10-28"
OUTPUT_FILE = Path("/home/.z/workspaces/con_nT5eqPlvQ3TIfCsN/phase4_results.json")

def is_dated_export(name: str) -> bool:
    """Check if directory name matches dated export pattern"""
    # Pattern: 20251027-132254_*
    return len(name) >= 8 and name[:8].isdigit() and name[8:9] in ["-", "_"]

def main(dry_run=False):
    logger.info(f"=== PHASE 4: INBOX CLEANUP {'[DRY RUN]' if dry_run else ''} ===")
    
    results = {
        "phase": "inbox_cleanup",
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "archived_folders": [],
        "kept_folders": [],
        "errors": []
    }
    
    if not INBOX.exists():
        logger.warning("Inbox directory not found")
        results["status"] = "skipped"
        results["success"] = True
        OUTPUT_FILE.write_text(json.dumps(results, indent=2))
        return 0
    
    if not dry_run:
        ARCHIVE_BASE.mkdir(exist_ok=True)
        inbox_archive_dir = ARCHIVE_BASE / "inbox_exports"
        inbox_archive_dir.mkdir(exist_ok=True)
        logger.info(f"Archive location: {inbox_archive_dir}")
    
    # Scan inbox
    items = list(INBOX.iterdir())
    logger.info(f"Found {len(items)} items in Inbox/")
    
    # Identify dated exports
    dated_exports = [item for item in items if item.is_dir() and is_dated_export(item.name)]
    other_items = [item for item in items if item not in dated_exports]
    
    logger.info(f"  Dated exports: {len(dated_exports)}")
    logger.info(f"  Other items: {len(other_items)}")
    
    # Move dated exports to archive
    if not dry_run:
        for item in dated_exports:
            try:
                dest = inbox_archive_dir / item.name
                shutil.move(str(item), str(dest))
                results["archived_folders"].append(item.name)
                logger.info(f"  Archived: {item.name}")
            except Exception as e:
                logger.error(f"Failed to archive {item.name}: {e}")
                results["errors"].append({
                    "folder": item.name,
                    "error": str(e)
                })
        
        # Compress the entire inbox_exports directory
        tar_file = ARCHIVE_BASE / "inbox_exports_20251027.tar.gz"
        logger.info(f"Compressing inbox exports -> {tar_file}")
        subprocess.run(
            ["tar", "czf", str(tar_file), "-C", str(ARCHIVE_BASE), "inbox_exports"],
            check=True, capture_output=True
        )
        
        size_mb = tar_file.stat().st_size / 1024 / 1024
        logger.info(f"  Created: {tar_file.name} ({size_mb:.1f}MB)")
        
        # Remove uncompressed directory
        shutil.rmtree(inbox_archive_dir)
        logger.info(f"  Removed: {inbox_archive_dir}")
        
        results["archive_file"] = str(tar_file)
        results["archive_size_mb"] = round(size_mb, 2)
    else:
        for item in dated_exports:
            logger.info(f"[DRY RUN] Would archive: {item.name}")
            results["archived_folders"].append(item.name)
    
    results["kept_folders"] = [item.name for item in other_items]
    results["status"] = "complete" if len(results["errors"]) == 0 else "complete_with_errors"
    results["success"] = len(results["errors"]) == 0
    
    OUTPUT_FILE.write_text(json.dumps(results, indent=2))
    logger.info(f"✓ Phase 4 complete. Results: {OUTPUT_FILE}")
    logger.info(f"Inbox now has {len(other_items)} items (clean for triage)")
    
    return 0 if results["success"] else 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    
    exit(main(dry_run=not args.execute))
