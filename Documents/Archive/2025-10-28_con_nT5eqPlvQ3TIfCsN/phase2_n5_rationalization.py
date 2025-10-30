#!/usr/bin/env python3
"""Phase 2: N5 Directory Rationalization - Core migration"""
import shutil
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
N5 = WORKSPACE / "N5"
ARCHIVE_BASE = WORKSPACE / ".archive_2025-10-28"
OUTPUT_FILE = Path("/home/.z/workspaces/con_nT5eqPlvQ3TIfCsN/phase2_results.json")

KEEP_DIRS = [
    "commands", "config", "data", "prefs", "schemas", "scripts",
    "logs", "templates", "workflows", "backups", "services", "lib"
]

ARCHIVE_DIRS = [
    "Documentation", "Documents", "docs", "digests", "exemplars",
    "exports", "inbox", "instructions", "intelligence", "knowledge",
    "lessons", "lists", "maintenance", "modules", "orchestration",
    "records", "registries", "registry", "runtime", "sessions",
    "specs", "strategy-evolution", "style_guides", "telemetry",
    "test", "tests", "timeline"
]

def compress_and_archive_dir(src: Path, archive_base: Path, results: dict):
    """Compress directory to .tar.gz and remove original"""
    rel_name = src.name
    tar_file = archive_base / f"N5_{rel_name}.tar.gz"
    
    try:
        # Create compressed archive
        logger.info(f"Compressing: {src} -> {tar_file}")
        subprocess.run(
            ["tar", "czf", str(tar_file), "-C", str(src.parent), src.name],
            check=True, capture_output=True
        )
        
        # Verify archive was created
        if not tar_file.exists():
            raise FileNotFoundError(f"Archive not created: {tar_file}")
        
        size_mb = tar_file.stat().st_size / 1024 / 1024
        logger.info(f"  Created: {tar_file.name} ({size_mb:.2f}MB)")
        
        # Remove original directory
        shutil.rmtree(src)
        logger.info(f"  Removed: {src}")
        
        results["archived"][rel_name] = {
            "archive_file": str(tar_file),
            "size_mb": round(size_mb, 2),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to archive {src}: {e}")
        results["errors"].append({
            "directory": rel_name,
            "error": str(e)
        })

def create_symlinks(results: dict):
    """Create compatibility symlinks"""
    symlinks = [
        (N5 / "records", WORKSPACE / "Records"),
        (N5 / "lists", WORKSPACE / "Lists"),
    ]
    
    for link_path, target_path in symlinks:
        if link_path.exists():
            if link_path.is_symlink():
                logger.info(f"Symlink exists: {link_path} -> {target_path}")
                continue
            else:
                logger.warning(f"Path exists but is not symlink: {link_path}")
                results["warnings"].append(f"Could not create symlink {link_path}: path exists")
                continue
        
        try:
            link_path.symlink_to(target_path)
            logger.info(f"✓ Created symlink: {link_path} -> {target_path}")
            results["symlinks_created"].append({
                "link": str(link_path),
                "target": str(target_path)
            })
        except Exception as e:
            logger.error(f"Failed to create symlink {link_path}: {e}")
            results["errors"].append({
                "symlink": str(link_path),
                "error": str(e)
            })

def main(dry_run=False):
    logger.info(f"=== PHASE 2: N5 RATIONALIZATION {'[DRY RUN]' if dry_run else ''} ===")
    
    results = {
        "phase": "n5_rationalization",
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "archived": {},
        "symlinks_created": [],
        "warnings": [],
        "errors": []
    }
    
    # Create archive base directory
    if not dry_run:
        ARCHIVE_BASE.mkdir(exist_ok=True)
        logger.info(f"Archive location: {ARCHIVE_BASE}")
    
    # Scan N5 directory
    n5_subdirs = [d for d in N5.iterdir() if d.is_dir() and not d.name.startswith(".")]
    logger.info(f"Found {len(n5_subdirs)} subdirectories in N5/")
    
    # Archive unwanted directories
    archived_count = 0
    for subdir in n5_subdirs:
        dir_name = subdir.name
        
        if dir_name in KEEP_DIRS:
            logger.info(f"KEEP: {dir_name}")
            continue
        
        if dir_name in ARCHIVE_DIRS:
            logger.info(f"ARCHIVE: {dir_name}")
            if not dry_run:
                compress_and_archive_dir(subdir, ARCHIVE_BASE, results)
            archived_count += 1
        else:
            logger.warning(f"UNKNOWN: {dir_name} (not in keep or archive list)")
            results["warnings"].append(f"Unknown directory: {dir_name}")
    
    logger.info(f"Archived {archived_count} directories")
    
    # Create symlinks
    if not dry_run:
        create_symlinks(results)
    
    # Verify keep directories still exist
    missing = []
    for dirname in KEEP_DIRS:
        path = N5 / dirname
        if not path.exists():
            missing.append(dirname)
            logger.warning(f"⚠️  Missing after migration: {dirname}")
    
    results["verification"] = {
        "missing_keep_dirs": missing,
        "all_keep_dirs_present": len(missing) == 0
    }
    
    # Overall status
    results["status"] = "complete" if len(results["errors"]) == 0 else "complete_with_errors"
    results["success"] = len(results["errors"]) == 0 and len(missing) == 0
    
    # Write results
    OUTPUT_FILE.write_text(json.dumps(results, indent=2))
    logger.info(f"✓ Phase 2 complete. Results: {OUTPUT_FILE}")
    
    return 0 if results["success"] else 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    
    exit(main(dry_run=not args.execute))
