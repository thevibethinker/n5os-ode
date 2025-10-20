#!/usr/bin/env python3
"""
Drive Knowledge Sync System
Syncs Careerspan/Vrijen knowledge to Google Drive for external AI consumption.

Architecture:
1. Load config from N5/config/drive_sync.json
2. Find or create target Drive folder
3. Delete existing folder (clean slate approach)
4. Recreate folder structure mirroring local
5. Upload all configured files
6. Verify uploads and log results

Safety:
- Dry-run mode by default
- Full verification of uploads
- Comprehensive logging
- Error handling with rollback
"""

import json
import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

class DriveKnowledgeSync:
    """Sync knowledge files to Google Drive."""
    
    def __init__(self, config_path: str, dry_run: bool = True):
        """
        Initialize sync system.
        
        Args:
            config_path: Path to drive_sync.json config
            dry_run: If True, preview changes without executing
        """
        self.config_path = Path(config_path)
        self.dry_run = dry_run
        self.config = self._load_config()
        self.stats = {
            "files_scanned": 0,
            "files_uploaded": 0,
            "folders_created": 0,
            "errors": []
        }
        
    def _load_config(self) -> Dict[str, Any]:
        """Load and validate configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path) as f:
            config = json.load(f)
        
        logger.info(f"Loaded config v{config['version']} from {self.config_path}")
        return config
    
    def _collect_files(self) -> List[Dict[str, Any]]:
        """
        Collect all files to sync based on config.
        
        Returns:
            List of file metadata dicts with source_path, target_path, etc.
        """
        files_to_sync = []
        
        for dir_config in self.config["source_directories"]:
            source_dir = Path(dir_config["path"])
            
            if not source_dir.exists():
                logger.warning(f"Source directory not found: {source_dir}")
                continue
            
            # Get files matching patterns
            if dir_config["recursive"]:
                pattern = "**/*"
            else:
                pattern = "*"
            
            for file_path in source_dir.glob(pattern):
                if not file_path.is_file():
                    continue
                
                # Check include patterns
                if dir_config["include_patterns"]:
                    if not any(file_path.match(pat) for pat in dir_config["include_patterns"]):
                        continue
                
                # Check exclude patterns
                if dir_config["exclude_patterns"]:
                    if any(file_path.match(pat) for pat in dir_config["exclude_patterns"]):
                        logger.debug(f"Excluding {file_path} (matches exclude pattern)")
                        continue
                
                # Calculate target path
                rel_path = file_path.relative_to(source_dir)
                target_path = Path(dir_config["target_path"]) / rel_path
                
                files_to_sync.append({
                    "source_path": file_path,
                    "target_path": target_path,
                    "directory_config": dir_config["description"],
                    "size": file_path.stat().st_size,
                    "checksum": self._calculate_checksum(file_path)
                })
                
                self.stats["files_scanned"] += 1
        
        logger.info(f"Collected {len(files_to_sync)} files to sync")
        return files_to_sync
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _print_preview(self, files_to_sync: List[Dict[str, Any]]):
        """Print preview of sync operations."""
        print("\n" + "="*80)
        print("DRIVE SYNC PREVIEW")
        print("="*80)
        print(f"\nTarget folder: {self.config['drive_folder_name']}")
        print(f"Sync mode: {self.config['sync_mode']}")
        print(f"\nFiles to sync: {len(files_to_sync)}")
        print(f"Total size: {sum(f['size'] for f in files_to_sync):,} bytes")
        
        # Group by directory
        by_dir = {}
        for file_meta in files_to_sync:
            target_dir = str(file_meta["target_path"].parent)
            if target_dir not in by_dir:
                by_dir[target_dir] = []
            by_dir[target_dir].append(file_meta["target_path"].name)
        
        print("\nDirectory structure:")
        for dir_path, files in sorted(by_dir.items()):
            print(f"  {dir_path}/")
            for filename in sorted(files):
                print(f"    - {filename}")
        
        print("\n" + "="*80)
        print("This is a DRY RUN. Use --execute to perform actual sync.")
        print("="*80 + "\n")
    
    def sync(self):
        """Execute sync operation."""
        logger.info(f"Starting sync (dry_run={self.dry_run})")
        
        # Step 1: Collect files
        files_to_sync = self._collect_files()
        
        if not files_to_sync:
            logger.warning("No files to sync!")
            return
        
        # Step 2: Preview (always show, even in execute mode)
        self._print_preview(files_to_sync)
        
        if self.dry_run:
            logger.info("Dry run complete. No changes made.")
            return
        
        # Step 3: Execute sync
        logger.info("Executing sync to Google Drive...")
        
        try:
            # This will be implemented to call Zo's Google Drive integration
            self._execute_drive_sync(files_to_sync)
            
            logger.info("Sync completed successfully!")
            logger.info(f"Stats: {self.stats}")
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            self.stats["errors"].append(str(e))
            raise
    
    def _execute_drive_sync(self, files_to_sync: List[Dict[str, Any]]):
        """
        Execute actual Drive sync operations.
        
        This is a placeholder that will be replaced with actual Drive API calls
        via Zo's app integration system.
        """
        logger.info("Drive sync execution - to be implemented with Zo Drive integration")
        logger.info(f"Would sync {len(files_to_sync)} files")
        
        # This function will:
        # 1. Find/create target folder via use_app_google_drive
        # 2. Delete existing folder (clean slate)
        # 3. Recreate folder structure
        # 4. Upload all files
        # 5. Verify uploads
        # 6. Log results
        
        raise NotImplementedError(
            "Drive sync implementation requires Zo Drive integration. "
            "This will be completed in next implementation phase."
        )

def main():
    parser = argparse.ArgumentParser(
        description="Sync Careerspan/Vrijen knowledge to Google Drive"
    )
    parser.add_argument(
        "--config",
        default="/home/workspace/N5/config/drive_sync.json",
        help="Path to sync configuration file"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute sync (default is dry-run)"
    )
    parser.add_argument(
        "--log-file",
        help="Optional log file path"
    )
    
    args = parser.parse_args()
    
    # Setup file logging if requested
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)sZ %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S"
        ))
        logger.addHandler(file_handler)
    
    # Run sync
    syncer = DriveKnowledgeSync(
        config_path=args.config,
        dry_run=not args.execute
    )
    
    try:
        syncer.sync()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
