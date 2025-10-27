#!/usr/bin/env python3
"""
Root Cleanup Script
Scans workspace root and moves unprotected items to Inbox/
"""
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import fnmatch
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
CONFIG_PATH = WORKSPACE_ROOT / "N5/config/root_cleanup_config.json"
LOG_PATH = WORKSPACE_ROOT / "N5/logs/.cleanup_log.jsonl"


def load_config() -> dict:
    """Load cleanup configuration."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


def is_protected(item: Path, config: dict) -> bool:
    """Check if item is in protected directory or matches ignore pattern."""
    item_name = item.name
    
    # Check protected directories
    if item_name in config["protected_directories"]:
        return True
    
    # Check ignore patterns
    for pattern in config["ignore_patterns"]:
        if fnmatch.fnmatch(item_name, pattern):
            return True
    
    return False


def get_inbox_destination(item: Path, config: dict) -> Path:
    """Generate timestamped destination path in Inbox."""
    inbox = Path(config["inbox_path"])
    
    if config["move_with_timestamp"]:
        timestamp = datetime.now().strftime(config["timestamp_format"])
        new_name = f"{timestamp}_{item.name}"
        return inbox / new_name
    
    return inbox / item.name


def log_operation(operation: dict) -> None:
    """Append operation to cleanup log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(operation) + "\n")


def move_to_inbox(item: Path, destination: Path, dry_run: bool = False) -> dict:
    """Move item to Inbox with logging."""
    try:
        size_bytes = item.stat().st_size if item.is_file() else None
        item_type = "file" if item.is_file() else "directory"
        
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Use shutil.move to handle cross-device moves
            shutil.move(str(item), str(destination))
            logger.info(f"✓ Moved: {item.name} → {destination}")
        else:
            logger.info(f"[DRY RUN] Would move: {item.name} → {destination}")
        
        operation = {
            "timestamp": datetime.now().isoformat(),
            "operation": "move_to_inbox",
            "source": str(item),
            "destination": str(destination),
            "status": "success" if not dry_run else "dry_run",
            "item_type": item_type,
            "size_bytes": size_bytes
        }
        
        if not dry_run:
            log_operation(operation)
        
        return operation
        
    except Exception as e:
        logger.error(f"✗ Failed to move {item.name}: {e}")
        operation = {
            "timestamp": datetime.now().isoformat(),
            "operation": "move_to_inbox",
            "source": str(item),
            "destination": str(destination),
            "status": "error",
            "error": str(e)
        }
        if not dry_run:
            log_operation(operation)
        return operation


def scan_root(dry_run: bool = False) -> dict:
    """Scan workspace root and process items."""
    config = load_config()
    
    stats = {
        "scanned": 0,
        "moved": 0,
        "skipped_protected": 0,
        "skipped_pattern": 0,
        "errors": 0
    }
    
    logger.info(f"Scanning {WORKSPACE_ROOT}")
    
    for item in WORKSPACE_ROOT.iterdir():
        stats["scanned"] += 1
        
        if is_protected(item, config):
            logger.info(f"○ Protected: {item.name}")
            stats["skipped_protected"] += 1
            continue
        
        destination = get_inbox_destination(item, config)
        result = move_to_inbox(item, destination, dry_run=dry_run)
        
        if result["status"] == "success" or result["status"] == "dry_run":
            stats["moved"] += 1
        elif result["status"] == "error":
            stats["errors"] += 1
    
    return stats


def main(dry_run: bool = False) -> int:
    """Main execution."""
    try:
        logger.info("=" * 60)
        logger.info("ROOT CLEANUP - Starting")
        logger.info("=" * 60)
        
        if not CONFIG_PATH.exists():
            logger.error(f"Config not found: {CONFIG_PATH}")
            return 1
        
        stats = scan_root(dry_run=dry_run)
        
        logger.info("=" * 60)
        logger.info("ROOT CLEANUP - Complete")
        logger.info(f"  Scanned: {stats['scanned']}")
        logger.info(f"  Moved: {stats['moved']}")
        logger.info(f"  Protected: {stats['skipped_protected']}")
        logger.info(f"  Errors: {stats['errors']}")
        logger.info("=" * 60)
        
        return 0 if stats["errors"] == 0 else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up workspace root")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without moving")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run))
