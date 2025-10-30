#!/usr/bin/env python3
"""Phase 3: Backup Consolidation - Compress and archive scattered backups"""
import json
import logging
import shutil
import subprocess
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
ARCHIVE_DIR = WORKSPACE / ".archive_2025-10-28"
RESULTS_FILE = Path("/home/.z/workspaces/con_nT5eqPlvQ3TIfCsN/phase3_results.json")

# Backup directories to consolidate
BACKUP_DIRS = [
    WORKSPACE / ".migration_backups",
    WORKSPACE / ".n5-ats-backups",
    WORKSPACE / ".n5_backups",
]

N5_BACKUPS_DIR = WORKSPACE / "N5" / "backups"
RETENTION_DAYS = 30

def get_dir_size_mb(path: Path) -> float:
    """Calculate directory size in MB"""
    if not path.exists():
        return 0.0
    total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    return total / (1024 * 1024)

def verify_tarball(tar_path: Path) -> bool:
    """Verify tarball integrity by listing contents"""
    try:
        result = subprocess.run(
            ["tar", "tzf", str(tar_path)],
            check=True,
            capture_output=True,
            timeout=60
        )
        logger.info(f"✓ Verified integrity: {tar_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Integrity check failed for {tar_path.name}: {e}")
        return False
    except subprocess.TimeoutExpired:
        logger.error(f"✗ Integrity check timeout for {tar_path.name}")
        return False

def compress_directory(src_dir: Path, archive_dir: Path, dry_run: bool = False) -> dict:
    """Compress a directory to tar.gz with verification"""
    if not src_dir.exists():
        logger.warning(f"Directory not found, skipping: {src_dir}")
        return {"status": "skipped", "reason": "not_found"}
    
    size_mb = get_dir_size_mb(src_dir)
    tar_name = f"{src_dir.name}_backups_{datetime.now().strftime('%Y%m%d')}.tar.gz"
    tar_path = archive_dir / tar_name
    
    if dry_run:
        logger.info(f"[DRY RUN] Would compress: {src_dir.relative_to(WORKSPACE)} ({size_mb:.1f}MB)")
        return {
            "status": "dry_run",
            "source": str(src_dir),
            "size_mb": size_mb,
            "target": str(tar_path)
        }
    
    try:
        # Create archive
        logger.info(f"Compressing {src_dir.relative_to(WORKSPACE)} ({size_mb:.1f}MB)...")
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(src_dir, arcname=src_dir.name)
        
        # Verify integrity
        if not verify_tarball(tar_path):
            raise Exception("Tarball integrity verification failed")
        
        compressed_size = tar_path.stat().st_size / (1024 * 1024)
        logger.info(f"✓ Compressed: {tar_name} ({compressed_size:.1f}MB)")
        
        # Remove original only after verification
        shutil.rmtree(src_dir)
        logger.info(f"✓ Removed original: {src_dir.relative_to(WORKSPACE)}")
        
        return {
            "status": "success",
            "source": str(src_dir),
            "archive": str(tar_path),
            "original_size_mb": size_mb,
            "compressed_size_mb": compressed_size,
            "compression_ratio": f"{(compressed_size/size_mb*100):.1f}%" if size_mb > 0 else "N/A"
        }
        
    except Exception as e:
        logger.error(f"Failed to compress {src_dir}: {e}")
        # If tar was created but verification failed, remove it
        if tar_path.exists():
            tar_path.unlink()
            logger.info(f"Removed failed archive: {tar_path.name}")
        return {
            "status": "error",
            "source": str(src_dir),
            "error": str(e)
        }

def clean_n5_backups(backups_dir: Path, retention_days: int, archive_dir: Path, dry_run: bool = False) -> dict:
    """Clean N5/backups/ directory: archive old files, keep recent"""
    if not backups_dir.exists():
        return {"status": "skipped", "reason": "directory_not_found"}
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    old_files = []
    recent_files = []
    
    for item in backups_dir.rglob('*'):
        if item.is_file():
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff_date:
                old_files.append(item)
            else:
                recent_files.append(item)
    
    if not old_files:
        logger.info(f"N5/backups/: All {len(recent_files)} files are recent (< {retention_days} days)")
        return {
            "status": "no_action_needed",
            "recent_files": len(recent_files),
            "old_files": 0
        }
    
    total_old_size = sum(f.stat().st_size for f in old_files) / (1024 * 1024)
    
    if dry_run:
        logger.info(f"[DRY RUN] Would archive {len(old_files)} old files ({total_old_size:.1f}MB) from N5/backups/")
        logger.info(f"[DRY RUN] Would keep {len(recent_files)} recent files")
        return {
            "status": "dry_run",
            "old_files": len(old_files),
            "old_size_mb": total_old_size,
            "recent_files": len(recent_files)
        }
    
    try:
        # Create archive of old files
        tar_name = f"N5_backups_old_{datetime.now().strftime('%Y%m%d')}.tar.gz"
        tar_path = archive_dir / tar_name
        
        logger.info(f"Archiving {len(old_files)} old files from N5/backups/ ({total_old_size:.1f}MB)...")
        with tarfile.open(tar_path, "w:gz") as tar:
            for old_file in old_files:
                arcname = old_file.relative_to(backups_dir)
                tar.add(old_file, arcname=arcname)
        
        # Verify integrity
        if not verify_tarball(tar_path):
            raise Exception("N5 backups archive integrity verification failed")
        
        # Remove old files only after verification
        for old_file in old_files:
            old_file.unlink()
        
        # Clean up empty directories
        for dirpath in sorted(backups_dir.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                dirpath.rmdir()
        
        compressed_size = tar_path.stat().st_size / (1024 * 1024)
        logger.info(f"✓ Archived old files: {tar_name} ({compressed_size:.1f}MB)")
        logger.info(f"✓ Kept {len(recent_files)} recent files in N5/backups/")
        
        return {
            "status": "success",
            "old_files_archived": len(old_files),
            "archive": str(tar_path),
            "original_size_mb": total_old_size,
            "compressed_size_mb": compressed_size,
            "recent_files_kept": len(recent_files)
        }
        
    except Exception as e:
        logger.error(f"Failed to clean N5/backups/: {e}")
        if tar_path.exists():
            tar_path.unlink()
        return {
            "status": "error",
            "error": str(e)
        }

def main(dry_run: bool = False) -> int:
    """Main consolidation workflow"""
    logger.info(f"=== PHASE 3: BACKUP CONSOLIDATION {'[DRY RUN]' if dry_run else '[EXECUTE]'} ===")
    
    results = {
        "phase": "backup_consolidation",
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "consolidated": {},
        "n5_backups_cleanup": {},
        "errors": [],
        "status": "in_progress",
        "success": False
    }
    
    # Ensure archive directory exists
    if not dry_run:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Consolidate backup directories
    all_success = True
    for backup_dir in BACKUP_DIRS:
        result = compress_directory(backup_dir, ARCHIVE_DIR, dry_run)
        results["consolidated"][backup_dir.name] = result
        
        if result["status"] == "error":
            all_success = False
            results["errors"].append({
                "directory": str(backup_dir),
                "error": result.get("error")
            })
            # Fail fast on compression errors
            logger.error(f"Aborting due to compression failure: {backup_dir.name}")
            results["status"] = "failed"
            RESULTS_FILE.write_text(json.dumps(results, indent=2))
            return 1
    
    # Clean N5/backups/ directory
    logger.info(f"Cleaning N5/backups/ (keeping files < {RETENTION_DAYS} days old)")
    n5_cleanup = clean_n5_backups(N5_BACKUPS_DIR, RETENTION_DAYS, ARCHIVE_DIR, dry_run)
    results["n5_backups_cleanup"] = n5_cleanup
    
    if n5_cleanup["status"] == "error":
        all_success = False
        results["errors"].append({
            "directory": "N5/backups",
            "error": n5_cleanup.get("error")
        })
    
    # Final status
    results["success"] = all_success
    results["status"] = "complete" if all_success else "partial"
    
    # Write results
    RESULTS_FILE.write_text(json.dumps(results, indent=2))
    logger.info(f"✓ Phase 3 {'complete' if all_success else 'completed with errors'}. Results: {RESULTS_FILE}")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 3: Backup Consolidation")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without executing")
    parser.add_argument("--execute", action="store_true", help="Execute consolidation")
    args = parser.parse_args()
    
    # Default to dry-run unless --execute is specified
    dry_run = not args.execute
    
    exit(main(dry_run=dry_run))
