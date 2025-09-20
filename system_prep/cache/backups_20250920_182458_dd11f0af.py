#!/usr/bin/env python3
"""
N5 System Upgrades Backup Manager

Handles backup creation, retention policies, pruning, and recovery operations
for system upgrade data with comprehensive metadata tracking.
"""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
ROOT = Path(__file__).resolve().parents[1]
UPGRADES_MD = ROOT / "lists" / "system-upgrades.md"
UPGRADES_JSONL = ROOT / "lists" / "system-upgrades.jsonl"
BACKUP_DIR = ROOT / "backups" / "system-upgrades"
METADATA_FILE = BACKUP_DIR / "backup_metadata.json"

# Default retention policy
DEFAULT_MAX_BACKUPS = 30
DEFAULT_MAX_AGE_DAYS = 14

@dataclass
class BackupMetadata:
    """Metadata for a backup operation."""
    timestamp: str
    operation_type: str  # 'add', 'edit', 'manual', 'rollback'
    backup_md_path: str
    backup_jsonl_path: str
    original_md_size: int
    original_jsonl_size: int
    success: bool
    error_message: Optional[str] = None
    items_count: Optional[int] = None
    validation_passed: Optional[bool] = None

class BackupManager:
    """Manages system upgrade backups with retention policies and metadata tracking."""

    def __init__(self, backup_dir: Path = BACKUP_DIR):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = METADATA_FILE
        self._ensure_metadata_file()

    def _ensure_metadata_file(self) -> None:
        """Ensure metadata file exists."""
        if not self.metadata_file.exists():
            self._save_metadata([])

    def _load_metadata(self) -> List[Dict]:
        """Load backup metadata from JSON file."""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Metadata file corrupted or missing, starting fresh")
            return []

    def _save_metadata(self, metadata: List[Dict]) -> None:
        """Save backup metadata to JSON file."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def create_backup(self, operation_type: str = "manual") -> Tuple[Path, Path, BackupMetadata]:
        """
        Create a timestamped backup of both system upgrade files.

        Args:
            operation_type: Type of operation triggering the backup

        Returns:
            Tuple of (backup_md_path, backup_jsonl_path, metadata)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_md = self.backup_dir / f"system-upgrades_{timestamp}.md"
        backup_jsonl = self.backup_dir / f"system-upgrades_{timestamp}.jsonl"

        md_size = UPGRADES_MD.stat().st_size if UPGRADES_MD.exists() else 0
        jsonl_size = UPGRADES_JSONL.stat().st_size if UPGRADES_JSONL.exists() else 0

        items_count = 0
        if UPGRADES_JSONL.exists():
            try:
                with open(UPGRADES_JSONL, 'r', encoding='utf-8') as f:
                    items_count = sum(1 for line in f if line.strip())
            except Exception as e:
                logger.warning(f"Could not count items in JSONL: {e}")

        success = True
        error_message = None

        try:
            if UPGRADES_MD.exists():
                shutil.copy2(UPGRADES_MD, backup_md)
                logger.info(f"Created backup: {backup_md}")
            if UPGRADES_JSONL.exists():
                shutil.copy2(UPGRADES_JSONL, backup_jsonl)
                logger.info(f"Created backup: {backup_jsonl}")

            metadata = BackupMetadata(
                timestamp=timestamp,
                operation_type=operation_type,
                backup_md_path=str(backup_md.relative_to(self.backup_dir)),
                backup_jsonl_path=str(backup_jsonl.relative_to(self.backup_dir)),
                original_md_size=md_size,
                original_jsonl_size=jsonl_size,
                success=True,
                items_count=items_count
            )

            all_metadata = self._load_metadata()
            all_metadata.append(asdict(metadata))
            self._save_metadata(all_metadata)
            logger.info(f"Backup created successfully with timestamp {timestamp}")
            return backup_md, backup_jsonl, metadata

        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Backup creation failed: {e}")

            metadata = BackupMetadata(
                timestamp=timestamp,
                operation_type=operation_type,
                backup_md_path=str(backup_md.relative_to(self.backup_dir)),
                backup_jsonl_path=str(backup_jsonl.relative_to(self.backup_dir)),
                original_md_size=md_size,
                original_jsonl_size=jsonl_size,
                success=False,
                error_message=error_message,
                items_count=items_count
            )

            all_metadata = self._load_metadata()
            all_metadata.append(asdict(metadata))
            self._save_metadata(all_metadata)
            raise RuntimeError(f"Backup creation failed: {error_message}")

    def list_backups(self, include_failed: bool = False) -> List[Dict]:
        metadata = self._load_metadata()
        if not include_failed:
            metadata = [m for m in metadata if m.get('success', False)]
        metadata.sort(key=lambda x: x['timestamp'], reverse=True)
        return metadata

    def get_latest_backup(self, include_failed: bool = False) -> Optional[Dict]:
        backups = self.list_backups(include_failed=include_failed)
        return backups[0] if backups else None

    def restore_from_backup(self, timestamp: str = None) -> bool:
        if timestamp is None:
            latest = self.get_latest_backup()
            if not latest:
                raise ValueError("No backups available")
            timestamp = latest['timestamp']

        backup_md = self.backup_dir / f"system-upgrades_{timestamp}.md"
        backup_jsonl = self.backup_dir / f"system-upgrades_{timestamp}.jsonl"

        if not backup_md.exists() or not backup_jsonl.exists():
            raise ValueError(f"Backup files not found for timestamp {timestamp}")

        logger.info(f"Restoring from backup {timestamp}...")

        try:
            safety_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_safety")
            safety_md = UPGRADES_MD.parent / f"system-upgrades_{safety_timestamp}.md"
            safety_jsonl = UPGRADES_JSONL.parent / f"system-upgrades_{safety_timestamp}.jsonl"
            if UPGRADES_MD.exists():
                shutil.copy2(UPGRADES_MD, safety_md)
                logger.info(f"Created safety backup: {safety_md}")
            if UPGRADES_JSONL.exists():
                shutil.copy2(UPGRADES_JSONL, safety_jsonl)
                logger.info(f"Created safety backup: {safety_jsonl}")

            shutil.copy2(backup_md, UPGRADES_MD)
            shutil.copy2(backup_jsonl, UPGRADES_JSONL)

            logger.info(f"Restore complete from backup {timestamp}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    def prune_backups(self, max_backups: int = DEFAULT_MAX_BACKUPS, max_age_days: int = DEFAULT_MAX_AGE_DAYS):
        metadata = self._load_metadata()
        backups_to_keep = []
        backups_to_delete = []

        now = datetime.now()

        # Filter successful backups
        valid_backups = [m for m in metadata if m.get('success', False)]

        # Sort by timestamp descending
        valid_backups.sort(key=lambda x: x['timestamp'], reverse=True)

        # Determine backups to keep
        for i, backup in enumerate(valid_backups):
            backup_time = datetime.strptime(backup['timestamp'], "%Y%m%d_%H%M%S")
            age_days = (now - backup_time).days
            if i < max_backups and age_days <= max_age_days:
                backups_to_keep.append(backup)
            else:
                backups_to_delete.append(backup)

        # Delete old backups
        for backup in backups_to_delete:
            try:
                md_path = self.backup_dir / backup['backup_md_path']
                jsonl_path = self.backup_dir / backup['backup_jsonl_path']
                if md_path.exists():
                    md_path.unlink()
                    logger.info(f"Deleted old backup: {md_path}")
                if jsonl_path.exists():
                    jsonl_path.unlink()
                    logger.info(f"Deleted old backup: {jsonl_path}")
            except Exception as e:
                logger.warning(f"Failed to delete backup files: {e}")

        # Update metadata to keep only valid backups
        new_metadata = [b for b in metadata if b in backups_to_keep]
        self._save_metadata(new_metadata)
