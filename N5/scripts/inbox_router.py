#!/usr/bin/env python3
"""
Inbox Router Script
Routes files based on analysis results from inbox_analyzer.py
"""
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
INBOX_PATH = WORKSPACE_ROOT / "Inbox"
CONFIG_PATH = WORKSPACE_ROOT / "N5/config/routing_config.json"
ANALYSIS_LOG_PATH = WORKSPACE_ROOT / "N5/logs/.inbox_analysis.jsonl"


def load_config() -> dict:
    """Load routing configuration."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_latest_analysis() -> dict:
    """Load most recent analysis for each file."""
    if not ANALYSIS_LOG_PATH.exists():
        return {}
    
    analyses = {}
    with open(ANALYSIS_LOG_PATH) as f:
        for line in f:
            entry = json.loads(line)
            filepath = entry["file_path"]
            # Keep most recent analysis per file
            if filepath not in analyses or entry["timestamp"] > analyses[filepath]["timestamp"]:
                analyses[filepath] = entry
    
    return analyses


def validate_destination(destination: str, config: dict) -> bool:
    """Check if destination is in valid list."""
    return destination in config["valid_destinations"]


def route_file(filepath: Path, destination_rel: str, dry_run: bool = False) -> bool:
    """Move file to destination."""
    try:
        destination = WORKSPACE_ROOT / destination_rel / filepath.name
        
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(filepath), str(destination))
            logger.info(f"✓ Routed: {filepath.name} → {destination_rel}")
        else:
            logger.info(f"[DRY RUN] Would route: {filepath.name} → {destination_rel}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to route {filepath.name}: {e}")
        return False


def update_analysis_log(filepath: str, routed: bool) -> None:
    """Mark file as routed in analysis log."""
    if not ANALYSIS_LOG_PATH.exists():
        return
    
    # Read all entries
    entries = []
    with open(ANALYSIS_LOG_PATH) as f:
        for line in f:
            entry = json.loads(line)
            if entry["file_path"] == filepath:
                entry["routed"] = routed
                entry["routed_timestamp"] = datetime.now().isoformat()
            entries.append(entry)
    
    # Rewrite log
    with open(ANALYSIS_LOG_PATH, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def route_inbox(dry_run: bool = False, auto_only: bool = True) -> dict:
    """Route files based on analysis."""
    config = load_config()
    analyses = load_latest_analysis()
    
    stats = {
        "routed": 0,
        "skipped": 0,
        "errors": 0
    }
    
    for filepath_str, analysis in analyses.items():
        filepath = Path(filepath_str)
        
        # Skip if already routed
        if analysis.get("routed", False):
            continue
        
        # Skip if file no longer exists
        if not filepath.exists():
            logger.warning(f"File no longer exists: {filepath.name}")
            continue
        
        # Check action type
        action = analysis["action"]
        if auto_only and action != "auto_route":
            logger.info(f"○ Skipping {filepath.name}: {action} (not auto_route)")
            stats["skipped"] += 1
            continue
        
        # Validate destination
        destination = analysis["destination"]
        if not validate_destination(destination, config):
            logger.error(f"✗ Invalid destination for {filepath.name}: {destination}")
            stats["errors"] += 1
            continue
        
        # Route file
        success = route_file(filepath, destination, dry_run=dry_run)
        
        if success:
            if not dry_run:
                update_analysis_log(filepath_str, routed=True)
            stats["routed"] += 1
        else:
            stats["errors"] += 1
    
    return stats


def main(dry_run: bool = False, auto_only: bool = True) -> int:
    """Main execution."""
    try:
        logger.info("=" * 60)
        logger.info("INBOX ROUTER - Starting")
        logger.info("=" * 60)
        
        if not CONFIG_PATH.exists():
            logger.error(f"Config not found: {CONFIG_PATH}")
            return 1
        
        stats = route_inbox(dry_run=dry_run, auto_only=auto_only)
        
        logger.info("=" * 60)
        logger.info("INBOX ROUTER - Complete")
        logger.info(f"  Routed: {stats['routed']}")
        logger.info(f"  Skipped: {stats['skipped']}")
        logger.info(f"  Errors: {stats['errors']}")
        logger.info("=" * 60)
        
        return 0 if stats["errors"] == 0 else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Route Inbox files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be routed without routing")
    parser.add_argument("--all", action="store_true", help="Route all files, not just auto_route candidates")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run, auto_only=not args.all))
