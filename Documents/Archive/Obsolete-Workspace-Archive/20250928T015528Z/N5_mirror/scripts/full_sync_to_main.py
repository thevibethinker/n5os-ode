#!/usr/bin/env python3
"""
Full Sync from N5_mirror to N5
Recursively synchronize all files and directories from N5_mirror to N5 with backups
"""

import shutil
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
log_dir = Path("/home/workspace/N5/knowledge/logs/Sync")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"full_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

source_root = Path("/home/workspace/N5_mirror")
target_root = Path("/home/workspace/N5")


def backup_file(target_path: Path) -> bool:
    if not target_path.exists():
        return True
    try:
        backup_suffix = f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = target_path.with_suffix(target_path.suffix + backup_suffix)
        shutil.copy2(target_path, backup_path)
        logger.info(f"Backed up {target_path} to {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Backup failed for {target_path}: {e}")
        return False


def sync_dir(source_dir: Path, target_dir: Path):
    logger.info(f"Syncing directory {source_dir} to {target_dir}")
    if not target_dir.exists():
        target_dir.mkdir(parents=True)
        logger.info(f"Created directory {target_dir}")

    for item in source_dir.iterdir():
        source_path = source_dir / item.name
        target_path = target_dir / item.name

        if item.is_dir():
            sync_dir(source_path, target_path)
        else:
            if target_path.exists():
                if not backup_file(target_path):
                    logger.error(f"Skipping {target_path} - backup failed")
                    continue
            try:
                shutil.copy2(source_path, target_path)
                logger.info(f"Copied {source_path} to {target_path}")
            except Exception as e:
                logger.error(f"Failed to copy {source_path} to {target_path}: {e}")


if __name__ == '__main__':
    logger.info("Starting full sync from N5_mirror to N5")
    sync_dir(source_root, target_root)
    logger.info("Full sync completed")
