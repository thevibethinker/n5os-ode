#!/usr/bin/env python3
"""
TMP Execution Manager
Organizes and manages files in /home/workspace/N5/tmp_execution.
- Groups executions into folders based on AAR references or timestamps.
- Pairs executable files (plans) with their AARs and related artifacts.
- Handles multiple files per execution with subfolders.
- Cleans up old/invalid files.
- Future-proof: Configurable, extensible for new file types, logging, dry-run.

Usage:
    python3 tmp_execution_manager.py [--dry-run] [--cleanup] [--retention-days 7]
"""

import argparse
import json
import logging
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set

# Config
TMP_DIR = Path('/home/workspace/N5/tmp_execution')
SCRIPTS_DIR = TMP_DIR / 'scripts'
LOGS_DIR = TMP_DIR / 'logs'
ARCHIVE_DIR = TMP_DIR / 'archive'
EXECUTION_PATTERN = re.compile(r'(\d{8}_\d{6})')  # YYYYMMDD_HHMMSS
RETENTION_DAYS = 7

class ExecutionManager:
    def __init__(self, dry_run: bool = False, retention_days: int = RETENTION_DAYS):
        self.dry_run = dry_run
        self.retention_days = retention_days
        self.executions: Dict[str, Dict[str, List[Path]]] = {}
        self.ensure_dirs()

    def ensure_dirs(self):
        """Ensure required directories exist."""
        for d in [SCRIPTS_DIR, LOGS_DIR, ARCHIVE_DIR]:
            d.mkdir(parents=True, exist_ok=True)
        # Set up logging after dirs exist
        self.setup_logging()

    def setup_logging(self):
        """Set up logging."""
        LOG_FILE = LOGS_DIR / 'execution_manager.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def scan_files(self):
        """Scan TMP_DIR for files and categorize by execution."""
        for file_path in TMP_DIR.rglob('*'):
            if file_path.is_file() and file_path.parent == TMP_DIR:
                exec_id = self.extract_execution_id(file_path)
                if exec_id:
                    file_type = self.categorize_file(file_path)
                    if exec_id not in self.executions:
                        self.executions[exec_id] = {'plans': [], 'aars': [], 'resolved': [], 'logs': [], 'others': []}
                    self.executions[exec_id][file_type].append(file_path)

    def extract_execution_id(self, file_path: Path) -> str:
        """Extract execution ID from filename or content."""
        # From filename (e.g., plan_20250920_073731.md -> 20250920_073731)
        match = EXECUTION_PATTERN.search(file_path.name)
        if match:
            return match.group(1)
        
        # From AAR content (e.g., Original Plan Reference)
        if file_path.suffix == '.md' and 'AAR' in file_path.name:
            try:
                content = file_path.read_text()
                ref_match = re.search(r'Original Plan Reference.*plan_(\d{8}_\d{6})', content)
                if ref_match:
                    return ref_match.group(1)
            except:
                pass
        
        # Fallback: Use file timestamp
        stat = file_path.stat()
        return datetime.fromtimestamp(stat.st_mtime).strftime('%Y%m%d_%H%M%S')

    def categorize_file(self, file_path: Path) -> str:
        """Categorize file type."""
        name = file_path.name.lower()
        if 'plan' in name or 'phase' in name:
            return 'plans'
        elif 'aar' in name or 'after' in name:
            return 'aars'
        elif 'resolved_command' in name or name.endswith('.json'):
            return 'resolved'
        elif 'log' in name or name.endswith('.txt'):
            return 'logs'
        else:
            return 'others'

    def extract_human_name(self, plan_path: Path) -> str:
        """Extract human-readable name from plan content."""
        try:
            content = plan_path.read_text()
            # Look for title in # header or "Intended Outcome"
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            else:
                # Fallback to Intended Outcome
                for line in lines:
                    if 'Intended Outcome' in line:
                        title = line.split(':', 1)[1].strip() if ':' in line else 'execution'
                        break
                else:
                    title = 'execution'
            # Sanitize: lowercase, underscores, remove special chars
            title = re.sub(r'[^\w\s-]', '', title).lower().replace(' ', '_').replace('-', '_')
            return title
        except:
            return 'execution'

    def organize_executions(self):
        """Create folders and move files for each execution."""
        for exec_id, files in self.executions.items():
            # Find a plan file to extract name
            plan_files = files.get('plans', []) + files.get('others', [])
            human_name = 'execution'
            if plan_files:
                human_name = self.extract_human_name(plan_files[0])
            
            exec_folder = TMP_DIR / f'exec_{human_name}_{exec_id}'
            if not exec_folder.exists():
                if not self.dry_run:
                    exec_folder.mkdir()
                self.logger.info(f"Created execution folder: {exec_folder}")
            
            # Create subfolders if multiple files
            for category, file_list in files.items():
                if len(file_list) > 1:
                    subfolder = exec_folder / category
                    if not self.dry_run:
                        subfolder.mkdir(exist_ok=True)
                    for file_path in file_list:
                        dest = subfolder / file_path.name
                        self.move_file(file_path, dest)
                elif file_list:
                    file_path = file_list[0]
                    dest = exec_folder / file_path.name
                    self.move_file(file_path, dest)

    def move_file(self, src: Path, dest: Path):
        """Move file, logging if dry-run."""
        if self.dry_run:
            self.logger.info(f"DRY-RUN: Would move {src} to {dest}")
        else:
            shutil.move(str(src), str(dest))
            self.logger.info(f"Moved {src} to {dest}")

    def cleanup(self):
        """Archive or delete old files."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        for file_path in TMP_DIR.rglob('*'):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff.timestamp():
                if 'invalid' in file_path.name.lower() or 'failed' in file_path.name.lower():
                    if not self.dry_run:
                        file_path.unlink()
                    self.logger.info(f"Deleted old file: {file_path}")
                else:
                    archive_path = ARCHIVE_DIR / file_path.name
                    if not self.dry_run:
                        shutil.move(str(file_path), str(archive_path))
                    self.logger.info(f"Archived old file: {file_path} to {archive_path}")

    def run(self):
        """Main execution."""
        self.logger.info("Starting TMP Execution Manager")
        self.scan_files()
        self.organize_executions()
        if self.dry_run:
            self.logger.info("Dry-run completed. Run without --dry-run to apply changes.")
        self.cleanup()
        self.logger.info("TMP Execution Manager completed")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage TMP Execution Folder')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--cleanup', action='store_true', help='Perform cleanup (default true)')
    parser.add_argument('--retention-days', type=int, default=RETENTION_DAYS, help='Days to retain files')
    args = parser.parse_args()
    
    manager = ExecutionManager(dry_run=args.dry_run, retention_days=args.retention_days)
    manager.run()