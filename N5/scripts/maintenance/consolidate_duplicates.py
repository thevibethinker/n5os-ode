#!/usr/bin/env python3
"""
Duplicate Folder Consolidation System

Scans Inbox for timestamped duplicate folders, keeps latest version,
archives old copies, and moves to canonical locations.
"""

import argparse
import json
import logging
import re
import shutil
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configuration
WORKSPACE_ROOT = Path("/home/workspace")
INBOX_PATH = WORKSPACE_ROOT / "Inbox"
CONFIG_PATH = WORKSPACE_ROOT / "N5/config/canonical_locations.json"
ARCHIVE_BASE = WORKSPACE_ROOT / "N5/data/consolidation_archives"
LOG_PATH = WORKSPACE_ROOT / "N5/logs/consolidation.log"

TIMESTAMP_PATTERN = re.compile(r'^(\d{8}-\d{6})_(.+)$')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config() -> Dict:
    """Load canonical locations configuration."""
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        logger.info(f"✓ Loaded config from {CONFIG_PATH}")
        return config
    except FileNotFoundError:
        logger.error(f"❌ Config not found: {CONFIG_PATH}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in config: {e}")
        raise


def detect_duplicates() -> Dict[str, List[Tuple[str, Path]]]:
    """Scan Inbox and group timestamped items by basename."""
    if not INBOX_PATH.exists():
        logger.warning(f"⚠️  Inbox not found: {INBOX_PATH}")
        return {}
    
    groups = defaultdict(list)
    
    for item in INBOX_PATH.iterdir():
        match = TIMESTAMP_PATTERN.match(item.name)
        if match:
            timestamp, basename = match.groups()
            groups[basename].append((timestamp, item))
    
    duplicates = {
        basename: sorted(items, key=lambda x: x[0], reverse=True)
        for basename, items in groups.items()
        if len(items) >= 2
    }
    
    logger.info(f"✓ Found {len(duplicates)} duplicate groups")
    for basename, items in duplicates.items():
        logger.info(f"  - {basename}: {len(items)} copies")
    
    return duplicates


def get_file_stats(path: Path) -> Dict:
    """Get file/directory statistics."""
    if path.is_file():
        return {
            "type": "file",
            "size_bytes": path.stat().st_size,
            "file_count": 1
        }
    elif path.is_dir():
        files = list(path.rglob("*"))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        return {
            "type": "directory",
            "size_bytes": total_size,
            "file_count": len([f for f in files if f.is_file()])
        }
    return {"type": "unknown", "size_bytes": 0, "file_count": 0}


def create_archive(basename: str, older_copies: List[Tuple[str, Path]], dry_run: bool = False) -> Optional[Path]:
    """Create zip archive of older duplicate copies."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archive_dir = ARCHIVE_BASE / today
    archive_path = archive_dir / f"{basename}_duplicates_{today}.zip"
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would create archive: {archive_path}")
        logger.info(f"[DRY-RUN] Would include {len(older_copies)} items")
        return None
    
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        "consolidation_date": datetime.now(timezone.utc).isoformat(),
        "basename": basename,
        "archived_versions": []
    }
    
    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for timestamp, path in older_copies:
                stats = get_file_stats(path)
                
                manifest["archived_versions"].append({
                    "timestamp": timestamp,
                    "full_path": str(path),
                    **stats
                })
                
                if path.is_file():
                    zf.write(path, arcname=path.name)
                elif path.is_dir():
                    for file_path in path.rglob("*"):
                        if file_path.is_file():
                            arcname = str(file_path.relative_to(path.parent))
                            zf.write(file_path, arcname=arcname)
            
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        
        logger.info(f"✓ Created archive: {archive_path} ({len(older_copies)} items)")
        return archive_path
        
    except Exception as e:
        logger.error(f"❌ Archive creation failed for {basename}: {e}", exc_info=True)
        return None


def consolidate_group(basename: str, copies: List[Tuple[str, Path]], config: Dict, dry_run: bool = False) -> Dict:
    """Consolidate a duplicate group: keep latest, archive old, move to canonical."""
    summary = {
        "basename": basename,
        "total_copies": len(copies),
        "kept_version": None,
        "archived_count": 0,
        "moved_to_canonical": False,
        "canonical_destination": None,
        "errors": []
    }
    
    if len(copies) < 2:
        summary["errors"].append("Not a duplicate (< 2 copies)")
        return summary
    
    latest_timestamp, latest_path = copies[0]
    older_copies = copies[1:]
    
    summary["kept_version"] = {"timestamp": latest_timestamp, "path": str(latest_path)}
    logger.info(f"Processing {basename}: keeping {latest_timestamp}")
    
    if older_copies:
        archive_path = create_archive(basename, older_copies, dry_run)
        summary["archived_count"] = len(older_copies)
        
        if not dry_run and archive_path:
            for _, old_path in older_copies:
                try:
                    if old_path.is_dir():
                        shutil.rmtree(old_path)
                    else:
                        old_path.unlink()
                    logger.info(f"✓ Deleted: {old_path.name}")
                except Exception as e:
                    error_msg = f"Failed to delete {old_path.name}: {e}"
                    summary["errors"].append(error_msg)
                    logger.error(f"❌ {error_msg}")
    
    mappings = config.get("mappings", {})
    special_handling = config.get("special_handling", {})
    
    if basename in special_handling:
        action = special_handling[basename]
        if action == "DELETE":
            if dry_run:
                logger.info(f"[DRY-RUN] Would delete {basename} (special handling)")
            else:
                try:
                    if latest_path.is_dir():
                        shutil.rmtree(latest_path)
                    else:
                        latest_path.unlink()
                    logger.info(f"✓ Deleted {basename} per special handling")
                    summary["moved_to_canonical"] = "DELETED"
                except Exception as e:
                    error_msg = f"Failed to delete {basename}: {e}"
                    summary["errors"].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            return summary
    
    if basename in mappings:
        canonical_rel = mappings[basename]
        canonical_dest = WORKSPACE_ROOT / canonical_rel
        summary["canonical_destination"] = str(canonical_dest)
        
        if canonical_dest.exists():
            warning_msg = f"Collision: {canonical_dest} already exists, skipping move"
            summary["errors"].append(warning_msg)
            logger.warning(f"⚠️  {warning_msg}")
        else:
            if dry_run:
                logger.info(f"[DRY-RUN] Would move {latest_path.name} → {canonical_dest}")
            else:
                try:
                    canonical_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(latest_path), str(canonical_dest))
                    logger.info(f"✓ Moved to canonical: {canonical_dest}")
                    summary["moved_to_canonical"] = True
                except Exception as e:
                    error_msg = f"Failed to move to canonical: {e}"
                    summary["errors"].append(error_msg)
                    logger.error(f"❌ {error_msg}")
    else:
        logger.info(f"ℹ️  No canonical mapping for {basename}, leaving in Inbox")
        summary["canonical_destination"] = "SKIP (no mapping)"
    
    return summary


def generate_summary_report(results: List[Dict], dry_run: bool = False) -> Dict:
    """Generate consolidated summary report."""
    total_groups = len(results)
    total_archived = sum(r["archived_count"] for r in results)
    successful_moves = sum(1 for r in results if r["moved_to_canonical"] is True)
    errors = [e for r in results for e in r.get("errors", [])]
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "total_duplicate_groups": total_groups,
        "total_items_archived": total_archived,
        "successful_canonical_moves": successful_moves,
        "total_errors": len(errors),
        "errors": errors,
        "details": results
    }


def save_summary(summary: Dict) -> Path:
    """Save summary to logs directory."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    summary_path = WORKSPACE_ROOT / f"N5/logs/consolidation_summary_{today}.json"
    
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"✓ Summary saved: {summary_path}")
    return summary_path


def main(dry_run: bool = False) -> int:
    """Main execution function."""
    try:
        logger.info("=" * 60)
        logger.info(f"Duplicate Consolidation System v1.0")
        logger.info(f"Mode: {'DRY-RUN (preview only)' if dry_run else 'LIVE EXECUTION'}")
        logger.info("=" * 60)
        
        config = load_config()
        duplicates = detect_duplicates()
        
        if not duplicates:
            logger.info("✓ No duplicates found")
            return 0
        
        results = []
        for basename, copies in duplicates.items():
            result = consolidate_group(basename, copies, config, dry_run)
            results.append(result)
        
        summary = generate_summary_report(results, dry_run)
        
        logger.info("=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Duplicate groups processed: {summary['total_duplicate_groups']}")
        logger.info(f"Items archived: {summary['total_items_archived']}")
        logger.info(f"Canonical moves: {summary['successful_canonical_moves']}")
        logger.info(f"Errors: {summary['total_errors']}")
        
        if not dry_run:
            save_summary(summary)
        
        if summary['total_errors'] > 0:
            logger.warning(f"⚠️  Completed with {summary['total_errors']} errors")
            return 1
        
        logger.info(f"✓ Consolidation complete")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate duplicate folders in Inbox")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without making changes")
    
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
