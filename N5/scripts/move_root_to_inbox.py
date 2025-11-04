#!/usr/bin/env python3
"""
Root Cleanup Script v2.0 - Enhanced Protection
Scans workspace root and moves unprotected items to Inbox/

Changes in v2.0:
- Integrated .n5protected marker check
- Service-awareness (checks registered user services)
- Better logging of protection reasons
"""
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import fnmatch
import shutil
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
CONFIG_PATH = WORKSPACE_ROOT / "N5/config/root_cleanup_config.json"
LOG_PATH = WORKSPACE_ROOT / "N5/logs/.cleanup_log.jsonl"
MARKER_FILENAME = ".n5protected"


def load_config() -> dict:
    """Load cleanup configuration."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


def check_n5protected_marker(item: Path) -> tuple[bool, str]:
    """
    Check if item or any parent has .n5protected marker.
    Returns (is_protected, reason)
    """
    # Check item itself if directory
    if item.is_dir():
        marker = item / MARKER_FILENAME
        if marker.exists():
            try:
                data = json.loads(marker.read_text())
                reason = data.get("reason", "unknown")
                return True, f".n5protected marker: {reason}"
            except:
                return True, ".n5protected marker (malformed)"
    
    # Check parent directories
    for parent in item.parents:
        if parent == WORKSPACE_ROOT:
            break
        marker = parent / MARKER_FILENAME
        if marker.exists():
            return True, f"parent protected: {parent.name}"
    
    return False, ""


def get_registered_services() -> list:
    """Get list of registered user services from Zo."""
    try:
        # Call Zo service API to list services
        result = subprocess.run(
            ["python3", "-c", 
             "from tools import list_user_services; import json; print(json.dumps(list_user_services()))"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except:
        # Fallback: services likely exist but we can't query
        logger.warning("Could not query user services - assuming none")
        return []


def is_referenced_by_service(item: Path, services: list) -> tuple[bool, str]:
    """
    Check if any registered service uses this directory.
    Returns (is_referenced, service_label)
    """
    item_str = str(item.resolve())
    
    for service in services:
        workdir = service.get('workdir')
        if not workdir:
            continue
        
        workdir_path = Path(workdir).resolve()
        
        # Check if service workdir is under this item
        try:
            if workdir_path.is_relative_to(item_str):
                return True, service.get('label', 'unknown service')
        except:
            pass
    
    return False, ""


def is_protected(item: Path, config: dict, services: list) -> tuple[bool, str]:
    """
    Check if item should be protected from cleanup.
    Returns (is_protected, reason)
    """
    item_name = item.name
    
    # Priority 1: Check .n5protected marker
    protected, reason = check_n5protected_marker(item)
    if protected:
        return True, reason
    
    # Priority 2: Check if referenced by registered service
    referenced, service_label = is_referenced_by_service(item, services)
    if referenced:
        return True, f"used by service: {service_label}"
    
    # Priority 3: Check protected directories config
    if item_name in config["protected_directories"]:
        return True, "in protected_directories config"
    
    # Priority 4: Check ignore patterns
    for pattern in config["ignore_patterns"]:
        if fnmatch.fnmatch(item_name, pattern):
            return True, f"matches pattern: {pattern}"
    
    return False, "not protected"


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
    services = get_registered_services()
    
    logger.info(f"Loaded {len(services)} registered services")
    
    stats = {
        "scanned": 0,
        "moved": 0,
        "protected": {},
        "errors": 0
    }
    
    logger.info(f"Scanning {WORKSPACE_ROOT}")
    
    for item in WORKSPACE_ROOT.iterdir():
        stats["scanned"] += 1
        
        protected, reason = is_protected(item, config, services)
        
        if protected:
            logger.info(f"○ Protected: {item.name} ({reason})")
            # Track protection reasons
            stats["protected"][item.name] = reason
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
        logger.info("ROOT CLEANUP v2.0 - Starting")
        logger.info("=" * 60)
        
        if not CONFIG_PATH.exists():
            logger.error(f"Config not found: {CONFIG_PATH}")
            return 1
        
        stats = scan_root(dry_run=dry_run)
        
        logger.info("=" * 60)
        logger.info("ROOT CLEANUP v2.0 - Complete")
        logger.info(f"  Scanned: {stats['scanned']}")
        logger.info(f"  Moved: {stats['moved']}")
        logger.info(f"  Protected: {len(stats['protected'])}")
        if stats['protected']:
            for name, reason in list(stats['protected'].items())[:5]:
                logger.info(f"    - {name}: {reason}")
            if len(stats['protected']) > 5:
                logger.info(f"    ... and {len(stats['protected']) - 5} more")
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
