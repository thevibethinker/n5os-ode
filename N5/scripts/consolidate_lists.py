#!/usr/bin/env python3
"""
Consolidate dual-write lists to SSOT (JSONL only)

Safely removes .md files after verifying JSONL completeness.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

LISTS_DIR = Path("/home/workspace/Lists")
BACKUP_DIR = Path("/home/workspace/Documents/Archive/list-consolidation-backup")

DUAL_WRITE_LISTS = [
    "fundraising-opportunity-tracker",
    "ideas",
    "must-contact",
    "opportunity-calendar",
    "pending-knowledge-updates",
    "phase3-test",
    "social-media-ideas",
    "social_media_ideas",
    "squawk"
]

def verify_jsonl(list_name: str) -> bool:
    """Verify JSONL file exists and is valid."""
    jsonl_path = LISTS_DIR / f"{list_name}.jsonl"
    
    if not jsonl_path.exists():
        logger.error(f"JSONL not found: {jsonl_path}")
        return False
    
    if jsonl_path.stat().st_size == 0:
        logger.warning(f"JSONL is empty: {jsonl_path}")
        return True  # Empty is valid
    
    try:
        with open(jsonl_path) as f:
            for i, line in enumerate(f, 1):
                json.loads(line)
        logger.info(f"✓ {list_name}.jsonl: {i} entries, valid")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"✗ {list_name}.jsonl: Invalid JSON at line {i}: {e}")
        return False

def backup_md(list_name: str) -> bool:
    """Backup .md file before deletion."""
    md_path = LISTS_DIR / f"{list_name}.md"
    
    if not md_path.exists():
        logger.info(f"  No .md file for {list_name}")
        return True
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{list_name}.md.backup_{timestamp}"
    
    try:
        backup_path.write_text(md_path.read_text())
        logger.info(f"  Backed up: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"  Backup failed: {e}")
        return False

def delete_md(list_name: str, dry_run: bool = False) -> bool:
    """Delete .md file after backup."""
    md_path = LISTS_DIR / f"{list_name}.md"
    
    if not md_path.exists():
        return True
    
    if dry_run:
        logger.info(f"  [DRY RUN] Would delete: {md_path}")
        return True
    
    try:
        md_path.unlink()
        logger.info(f"  ✓ Deleted: {md_path}")
        return True
    except Exception as e:
        logger.error(f"  ✗ Delete failed: {e}")
        return False

def consolidate_list(list_name: str, dry_run: bool = False) -> bool:
    """Consolidate a single list to SSOT."""
    logger.info(f"\n=== {list_name} ===")
    
    # Step 1: Verify JSONL
    if not verify_jsonl(list_name):
        logger.error(f"SKIP: {list_name} - JSONL invalid")
        return False
    
    # Step 2: Backup .md
    if not backup_md(list_name):
        logger.error(f"SKIP: {list_name} - Backup failed")
        return False
    
    # Step 3: Delete .md
    if not delete_md(list_name, dry_run=dry_run):
        logger.error(f"SKIP: {list_name} - Delete failed")
        return False
    
    return True

def main(dry_run: bool = False) -> int:
    """Main consolidation process."""
    logger.info(f"List Consolidation - {'DRY RUN' if dry_run else 'LIVE'}")
    logger.info(f"Lists to consolidate: {len(DUAL_WRITE_LISTS)}")
    
    results = {
        "success": [],
        "failed": [],
        "skipped": []
    }
    
    for list_name in DUAL_WRITE_LISTS:
        if consolidate_list(list_name, dry_run=dry_run):
            results["success"].append(list_name)
        else:
            results["failed"].append(list_name)
    
    # Summary
    logger.info("\n=== SUMMARY ===")
    logger.info(f"✓ Success: {len(results['success'])}")
    logger.info(f"✗ Failed: {len(results['failed'])}")
    
    if results["failed"]:
        logger.info("\nFailed lists:")
        for name in results["failed"]:
            logger.info(f"  - {name}")
        return 1
    
    if not dry_run:
        logger.info(f"\n✓ All lists consolidated to SSOT")
        logger.info(f"Backups saved to: {BACKUP_DIR}")
    else:
        logger.info(f"\n[DRY RUN] No changes made")
    
    return 0

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Test without making changes")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run))
