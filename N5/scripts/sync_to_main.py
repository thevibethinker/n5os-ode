#!/usr/bin/env python3
"""
N5 Mirror to Main Synchronization Tool
Synchronizes tested functionality from N5_mirror to main N5 system
"""

import os
import shutil
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Setup logging
log_dir = Path("/home/workspace/Knowledge/logs/Sync")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class N5SyncManager:
    def __init__(self, dry_run: bool = False, backup: bool = True):
        self.n5_main = Path("/home/workspace/N5")
        self.n5_mirror = Path("/home/workspace/N5_mirror")
        self.dry_run = dry_run
        self.backup = backup
        self.sync_manifest = []

        # Define priority sync items - these are the automation tools we need
        self.priority_scripts = [
            "blurb_ticket_generator.py",
            "consolidated_workflow.py",
            "front_matter_manager.py",
            "file_protector.py",
            "direct_ingestion_mechanism.py",
            "gdrive_transcript_workflow.py",
            "consolidated_transcript_workflow.py"
        ]

        # Config files that need syncing
        self.config_files = [
            "commands.jsonl",
            "prefs.md",
            "POLICY.md"
        ]

        # Output directories that should exist in main
        self.output_dirs = [
            "output/content_maps",
            "output/emails",
            "output/tickets"
        ]

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for change detection"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return ""

    def backup_file(self, target_path: Path) -> bool:
        """Create backup of existing file before sync"""
        if not target_path.exists():
            return True

        backup_path = target_path.with_suffix(f"{target_path.suffix}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        try:
            if not self.dry_run:
                shutil.copy2(target_path, backup_path)
            logger.info(f"Backed up {target_path} to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup {target_path}: {e}")
            return False

    def sync_script(self, script_name: str) -> bool:
        """Sync a single script file with safety checks"""
        source = self.n5_mirror / "scripts" / script_name
        target = self.n5_main / "scripts" / script_name

        if not source.exists():
            logger.warning(f"Source script {script_name} not found in mirror")
            return False

        if target.exists():
            source_hash = self.calculate_file_hash(source)
            target_hash = self.calculate_file_hash(target)

            if source_hash == target_hash:
                logger.info(f"Script {script_name} is already synchronized")
                return True

            logger.info(f"Script {script_name} differs, syncing...")
        else:
            logger.info(f"New script {script_name} found in mirror, syncing...")

        # Backup existing file
        if self.backup and target.exists():
            if not self.backup_file(target):
                return False

        # Perform sync
        try:
            if not self.dry_run:
                shutil.copy2(source, target)

            logger.info(f"\u2713 Synced {script_name}")
            self.sync_manifest.append({
                "action": "script_sync",
                "file": script_name,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            })
            return True
        except Exception as e:
            logger.error(f"Failed to sync {script_name}: {e}")
            self.sync_manifest.append({
                "action": "script_sync",
                "file": script_name,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
            return False

    def sync_priority_scripts(self) -> Dict[str, bool]:
        """Sync all priority automation scripts"""
        results = {}
        logger.info("Syncing priority automation scripts...")

        for script in self.priority_scripts:
            results[script] = self.sync_script(script)

        return results

    def setup_output_structure(self) -> bool:
        """Ensure output directories exist in main N5"""
        logger.info("Setting up output directory structure...")
        success = True

        for dir_path in self.output_dirs:
            target_dir = self.n5_main / dir_path
            try:
                if not self.dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"\u2713 Created directory {dir_path}")
                self.sync_manifest.append({
                    "action": "directory_create",
                    "path": dir_path,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                })
            except Exception as e:
                logger.error(f"Failed to create directory {dir_path}: {e}")
                success = False
                self.sync_manifest.append({
                    "action": "directory_create",
                    "path": dir_path,
                    "timestamp": datetime.now().isoformat(),
                    "status": "failed",
                    "error": str(e)
                })

        return success

    def generate_sync_report(self) -> Dict:
        """Generate comprehensive sync report"""
        report = {
            "sync_id": f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "backup_enabled": self.backup,
            "manifest": self.sync_manifest,
            "summary": {
                "total_operations": len(self.sync_manifest),
                "successful_operations": len([op for op in self.sync_manifest if op["status"] == "success"]),
                "failed_operations": len([op for op in self.sync_manifest if op["status"] == "failed"])
            }
        }

        return report

    def save_sync_report(self, report: Dict) -> bool:
        """Save sync report to knowledge system"""
        report_file = self.n5_main / "knowledge" / "sync_reports" / f"sync_report_{report['sync_id']}.json"

        try:
            if not self.dry_run:
                report_file.parent.mkdir(exist_ok=True)
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2)

            logger.info(f"\u2713 Sync report saved to {report_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save sync report: {e}")
            return False

    def run_full_sync(self) -> Dict:
        """Execute complete synchronization process"""
        logger.info("Starting N5 Mirror to Main synchronization...")
        logger.info(f"Dry run: {self.dry_run}")
        logger.info(f"Backup enabled: {self.backup}")

        # Setup output structure first
        self.setup_output_structure()

        # Sync priority scripts
        script_results = self.sync_priority_scripts()

        # Generate final report
        report = self.generate_sync_report()

        # Save report
        self.save_sync_report(report)

        # Log completion summary
        logger.info(f"Sync complete: {report['summary']['successful_operations']} succeeded, {report['summary']['failed_operations']} failed")
        return report


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Synchronize N5_mirror content to N5')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without file changes')
    parser.add_argument('--no-backup', action='store_false', dest='backup', help='Disable backup before overwriting files')
    args = parser.parse_args()

    sync_manager = N5SyncManager(dry_run=args.dry_run, backup=args.backup)
    summary = sync_manager.run_full_sync()
    
    if summary['summary']['failed_operations'] > 0:
        exit(1)
    else:
        exit(0)
