#!/usr/bin/env python3
"""
System Upgrades Backup Manager
Handles backup creation, restoration, retention, and cleanup operations.
"""

import json
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages backup operations for system upgrades with configurable retention policies."""
    
    def __init__(self, backup_dir: Path, retention_days: int = 14, max_backups: int = 30):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups
            retention_days: Maximum age of backups to keep (default 14 days)
            max_backups: Maximum number of backups to keep (default 30)
        """
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self, md_path: Path, jsonl_path: Path, operation_type: str = "manual") -> Dict[str, Any]:
        """
        Create a backup of both markdown and JSONL files.
        
        Args:
            md_path: Path to markdown file
            jsonl_path: Path to JSONL file
            operation_type: Type of operation that triggered backup
            
        Returns:
            Backup metadata dictionary
        """
        timestamp = datetime.now()
        backup_id = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Create backup metadata
        metadata = {
            "backup_id": backup_id,
            "timestamp": timestamp.isoformat(),
            "operation_type": operation_type,
            "success": True,
            "files": {}
        }
        
        try:
            # Backup markdown file
            if md_path.exists():
                md_backup_path = self.backup_dir / f"system-upgrades_{backup_id}.md"
                shutil.copy2(md_path, md_backup_path)
                metadata["files"]["markdown"] = {
                    "original": str(md_path),
                    "backup": str(md_backup_path),
                    "size": md_path.stat().st_size
                }
            
            # Backup JSONL file
            if jsonl_path.exists():
                jsonl_backup_path = self.backup_dir / f"system-upgrades_{backup_id}.jsonl"
                shutil.copy2(jsonl_path, jsonl_backup_path)
                metadata["files"]["jsonl"] = {
                    "original": str(jsonl_path),
                    "backup": str(jsonl_backup_path),
                    "size": jsonl_path.stat().st_size
                }
            
            # Write metadata
            metadata_path = self.backup_dir / f"system-upgrades_{backup_id}.metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Backup created successfully: {backup_id}")
            return metadata
            
        except Exception as e:
            metadata["success"] = False
            metadata["error"] = str(e)
            logger.error(f"Backup creation failed: {e}")
            raise
    
    def get_latest_backup(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent backup metadata.
        
        Returns:
            Latest backup metadata or None if no backups exist
        """
        backup_files = list(self.backup_dir.glob("system-upgrades_*.metadata.json"))
        if not backup_files:
            return None
            
        latest_file = max(backup_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file) as f:
            return json.load(f)
    
    def restore_backup(self, backup_id: str = None) -> bool:
        """
        Restore from a backup.
        
        Args:
            backup_id: Specific backup to restore from. If None, uses latest.
            
        Returns:
            True if restoration successful, False otherwise
        """
        try:
            if backup_id is None:
                metadata = self.get_latest_backup()
                if not metadata:
                    logger.error("No backups available for restoration")
                    return False
                backup_id = metadata["backup_id"]
            else:
                metadata_path = self.backup_dir / f"system-upgrades_{backup_id}.metadata.json"
                if not metadata_path.exists():
                    logger.error(f"Backup {backup_id} not found")
                    return False
                with open(metadata_path) as f:
                    metadata = json.load(f)
            
            if not metadata["success"]:
                logger.error(f"Backup {backup_id} was not successful, cannot restore")
                return False
            
            # Restore files
            for file_type, file_info in metadata["files"].items():
                backup_path = Path(file_info["backup"])
                original_path = Path(file_info["original"])
                
                if backup_path.exists():
                    shutil.copy2(backup_path, original_path)
                    logger.info(f"Restored {file_type} from backup {backup_id}")
                else:
                    logger.warning(f"Backup file not found: {backup_path}")
            
            logger.info(f"Successfully restored from backup {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups with their metadata.
        
        Returns:
            List of backup metadata dictionaries
        """
        backups = []
        backup_files = list(self.backup_dir.glob("system-upgrades_*.metadata.json"))
        
        for metadata_file in sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    backups.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to read backup metadata {metadata_file}: {e}")
                
        return backups
    
    def prune_old_backups(self) -> Dict[str, Any]:
        """
        Remove old backups based on retention policy.
        
        Returns:
            Pruning results dictionary
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        backups = self.list_backups()
        
        results = {
            "retained": 0,
            "removed": 0,
            "total_backups": len(backups),
            "removed_ids": []
        }
        
        if not backups:
            return results
        
        # Sort backups by timestamp (newest first)
        sorted_backups = sorted(backups, key=lambda x: x["timestamp"], reverse=True)
        
        for i, backup in enumerate(sorted_backups):
            backup_id = backup["backup_id"]
            backup_time = datetime.fromisoformat(backup["timestamp"])
            
            # Keep the newest N backups regardless of age, or keep if within retention period
            should_keep = (i < self.max_backups) and (backup_time >= cutoff_date)
            
            if should_keep:
                results["retained"] += 1
            else:
                # Remove backup files
                try:
                    for file_info in backup["files"].values():
                        backup_path = Path(file_info["backup"])
                        if backup_path.exists():
                            backup_path.unlink()
                    
                    # Remove metadata file
                    metadata_path = self.backup_dir / f"system-upgrades_{backup_id}.metadata.json"
                    if metadata_path.exists():
                        metadata_path.unlink()
                    
                    results["removed"] += 1
                    results["removed_ids"].append(backup_id)
                    logger.info(f"Removed old backup: {backup_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to remove backup {backup_id}: {e}")
        
        logger.info(f"Pruning complete: {results['removed']} removed, {results['retained']} retained")
        return results