#!/usr/bin/env python3
"""
Weekly Workspace Cleanup - Temporary File Management

Runs weekly on Mondays at 03:00 ET.
Model: Claude Sonnet 4.5
"""

import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
log_dir = Path("/home/workspace/N5/logs/maintenance/weekly")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"workspace_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Retention policies
CONVERSATION_RETENTION_DAYS = 14
TEMP_FILE_RETENTION_DAYS = 14
EXPORT_RETENTION_DAYS = 30
LOG_RETENTION_DAYS = 30


def clean_old_conversations():
    """Delete conversation workspaces older than retention period."""
    logger.info("=== Cleaning Old Conversation Workspaces ===")
    
    workspaces_dir = Path("/home/.z/workspaces")
    cutoff_time = datetime.now() - timedelta(days=CONVERSATION_RETENTION_DAYS)
    
    deleted_count = 0
    space_freed = 0
    
    if not workspaces_dir.exists():
        logger.warning("Conversation workspaces directory not found")
        return deleted_count, space_freed
    
    for workspace in workspaces_dir.iterdir():
        if workspace.is_dir() and workspace.name.startswith("con_"):
            mtime = datetime.fromtimestamp(workspace.stat().st_mtime)
            
            if mtime < cutoff_time:
                try:
                    # Calculate size before deletion
                    size = sum(f.stat().st_size for f in workspace.rglob('*') if f.is_file())
                    
                    shutil.rmtree(workspace)
                    deleted_count += 1
                    space_freed += size
                    
                    logger.info(f"Deleted: {workspace.name} (age: {(datetime.now() - mtime).days} days, size: {size // 1024} KB)")
                except Exception as e:
                    logger.error(f"Failed to delete {workspace.name}: {e}")
    
    logger.info(f"✓ Deleted {deleted_count} conversation workspace(s), freed {space_freed // 1024 // 1024} MB")
    return deleted_count, space_freed


def clean_temp_files():
    """Clean temporary files older than retention period."""
    logger.info("=== Cleaning Temporary Files ===")
    
    runtime_dir = Path("/home/workspace/N5/runtime")
    cutoff_time = datetime.now() - timedelta(days=TEMP_FILE_RETENTION_DAYS)
    
    deleted_count = 0
    space_freed = 0
    
    if not runtime_dir.exists():
        logger.info("No runtime directory found (nothing to clean)")
        return deleted_count, space_freed
    
    for temp_file in runtime_dir.rglob('*'):
        if temp_file.is_file():
            mtime = datetime.fromtimestamp(temp_file.stat().st_mtime)
            
            if mtime < cutoff_time:
                try:
                    size = temp_file.stat().st_size
                    temp_file.unlink()
                    deleted_count += 1
                    space_freed += size
                    
                    logger.info(f"Deleted: {temp_file.relative_to(runtime_dir)}")
                except Exception as e:
                    logger.error(f"Failed to delete {temp_file}: {e}")
    
    logger.info(f"✓ Deleted {deleted_count} temp file(s), freed {space_freed // 1024} KB")
    return deleted_count, space_freed


def clean_exports():
    """Clean export files older than retention period."""
    logger.info("=== Cleaning Old Exports ===")
    
    exports_dir = Path("/home/workspace/N5/exports")
    cutoff_time = datetime.now() - timedelta(days=EXPORT_RETENTION_DAYS)
    
    deleted_count = 0
    space_freed = 0
    
    if not exports_dir.exists():
        logger.info("No exports directory found (nothing to clean)")
        return deleted_count, space_freed
    
    for export_file in exports_dir.rglob('*'):
        if export_file.is_file():
            mtime = datetime.fromtimestamp(export_file.stat().st_mtime)
            
            if mtime < cutoff_time:
                try:
                    size = export_file.stat().st_size
                    export_file.unlink()
                    deleted_count += 1
                    space_freed += size
                    
                    logger.info(f"Deleted: {export_file.relative_to(exports_dir)}")
                except Exception as e:
                    logger.error(f"Failed to delete {export_file}: {e}")
    
    logger.info(f"✓ Deleted {deleted_count} export(s), freed {space_freed // 1024 // 1024} MB")
    return deleted_count, space_freed


def clean_old_logs():
    """Clean maintenance logs older than retention period."""
    logger.info("=== Cleaning Old Maintenance Logs ===")
    
    logs_base = Path("/home/workspace/N5/logs/maintenance")
    cutoff_time = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
    
    deleted_count = 0
    space_freed = 0
    
    for log_file in logs_base.rglob('*.log'):
        if log_file.is_file():
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if mtime < cutoff_time:
                try:
                    size = log_file.stat().st_size
                    log_file.unlink()
                    deleted_count += 1
                    space_freed += size
                    
                    logger.info(f"Deleted: {log_file.relative_to(logs_base)}")
                except Exception as e:
                    logger.error(f"Failed to delete {log_file}: {e}")
    
    logger.info(f"✓ Deleted {deleted_count} old log(s), freed {space_freed // 1024} KB")
    return deleted_count, space_freed


def generate_summary(results):
    """Generate cleanup summary."""
    logger.info("=== Weekly Cleanup Summary ===")
    
    total_deleted = sum(r[0] for r in results.values())
    total_freed = sum(r[1] for r in results.values())
    
    logger.info(f"Total files/dirs deleted: {total_deleted}")
    logger.info(f"Total space freed: {total_freed // 1024 // 1024} MB")
    
    for category, (count, size) in results.items():
        logger.info(f"  - {category}: {count} items, {size // 1024 // 1024} MB")
    
    logger.info("✅ Weekly cleanup completed successfully")


def main():
    """Run weekly cleanup tasks."""
    logger.info("=== Weekly Workspace Cleanup Started ===")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Coverage: Previous 7 days")
    logger.info(f"Retention Policies:")
    logger.info(f"  - Conversations: {CONVERSATION_RETENTION_DAYS} days")
    logger.info(f"  - Temp files: {TEMP_FILE_RETENTION_DAYS} days")
    logger.info(f"  - Exports: {EXPORT_RETENTION_DAYS} days")
    logger.info(f"  - Logs: {LOG_RETENTION_DAYS} days")
    
    results = {
        "Conversations": clean_old_conversations(),
        "Temp Files": clean_temp_files(),
        "Exports": clean_exports(),
        "Old Logs": clean_old_logs(),
    }
    
    generate_summary(results)
    
    logger.info(f"=== Weekly Workspace Cleanup Completed ===")
    logger.info(f"Log saved to: {log_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())
