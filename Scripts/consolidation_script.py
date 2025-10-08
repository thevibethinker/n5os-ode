#!/usr/bin/env python3
"""
Consolidation Script: Merge N5 subdirectories into main workspace directories.
Moves files from N5 subdirs to main subdirs, with deduplication to avoid duplicates.
Removes empty N5 subdirs after consolidation.
"""

import os
import shutil
from pathlib import Path
import hashlib

class ConsolidationHandler:
    def __init__(self, log_file: str):
        self.log_file = log_file

    def log_action(self, action: str, file_path: Path, target: str = ""):
        with open(self.log_file, 'a') as f:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} - {action}: {file_path} -> {target}\n")

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of the file content."""
        hash_sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def is_duplicate(self, source_path: Path, target_dir: Path) -> bool:
        """Check if source file is a duplicate of any file in target_dir."""
        source_hash = self.compute_hash(source_path)
        for existing_file in target_dir.iterdir():
            if existing_file.is_file():
                try:
                    if self.compute_hash(existing_file) == source_hash:
                        return True
                except:
                    pass
        return False

    def consolidate_subdir(self, n5_subdir: Path, main_subdir: Path):
        """Move files from N5 subdir to main subdir with deduplication."""
        if not n5_subdir.exists():
            return
        os.makedirs(main_subdir, exist_ok=True)
        for file_path in n5_subdir.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                if self.is_duplicate(file_path, main_subdir):
                    os.remove(file_path)
                    self.log_action("Deleted duplicate during consolidation", file_path)
                else:
                    target = main_subdir / file_path.name
                    counter = 1
                    while target.exists():
                        stem = file_path.stem
                        suffix = file_path.suffix
                        target = main_subdir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    shutil.move(str(file_path), target)
                    self.log_action("Consolidated to main", file_path, str(target))

def main():
    log_file = '/home/workspace/file_hygiene_log.txt'
    handler = ConsolidationHandler(log_file)

    # Define subdirs to consolidate
    subdirs = ['Scripts', 'Backups', 'Data', 'Documents', 'Logs', 'Misc', 'Images']

    base_n5 = Path('/home/workspace/N5')
    base_main = Path('/home/workspace')

    for sub in subdirs:
        n5_sub = base_n5 / sub
        main_sub = base_main / sub
        handler.consolidate_subdir(n5_sub, main_sub)
        # Remove empty N5 subdir
        if n5_sub.exists() and not any(n5_sub.iterdir()):
            n5_sub.rmdir()
            handler.log_action("Removed empty N5 subdir", n5_sub)

    print("Consolidation complete.")

if __name__ == "__main__":
    main()