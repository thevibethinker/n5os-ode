#!/usr/bin/env python3
"""
N5 File Backup System - Automatic timestamped backups with rotation
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import json


class FileBackupSystem:
    """Manages automatic backups with rotation for protected files"""
    
    BACKUP_DIR = Path("/home/workspace/.n5_backups")
    MAX_BACKUPS_PER_FILE = 5
    
    PROTECTED_FILES = [
        "/home/workspace/Documents/N5.md",
        "/home/workspace/N5/prefs/prefs.md",
        "/home/workspace/Recipes/recipes.jsonl",
        "/home/workspace/N5/timeline/system-timeline.jsonl",
        "/home/workspace/Knowledge/stable/careerspan-timeline.md",
    ]
    
    def __init__(self):
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_manifest()
    
    def _ensure_manifest(self):
        """Ensure backup manifest file exists"""
        manifest_path = self.BACKUP_DIR / "manifest.json"
        if not manifest_path.exists():
            manifest_path.write_text(json.dumps({"backups": {}}, indent=2))
    
    def _get_manifest(self) -> dict:
        """Load backup manifest"""
        manifest_path = self.BACKUP_DIR / "manifest.json"
        try:
            return json.loads(manifest_path.read_text())
        except:
            return {"backups": {}}
    
    def _save_manifest(self, manifest: dict):
        """Save backup manifest"""
        manifest_path = self.BACKUP_DIR / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
    
    def create_backup(self, file_path: str, operation: str = "write") -> Optional[Path]:
        """
        Create a timestamped backup of a file before modification
        
        Args:
            file_path: Absolute path to file to backup
            operation: Description of operation (for logging)
            
        Returns:
            Path to backup file, or None if file doesn't exist
        """
        source = Path(file_path)
        
        if not source.exists():
            print(f"⚠️  Source file does not exist: {file_path}")
            return None
        
        if not source.is_file():
            print(f"⚠️  Source is not a file: {file_path}")
            return None
        
        # Create backup filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        relative_path = str(source).replace("/home/workspace/", "").replace("/", "_")
        backup_name = f"{relative_path}.{timestamp}.backup"
        backup_path = self.BACKUP_DIR / backup_name
        
        # Copy file
        try:
            shutil.copy2(source, backup_path)
            size = backup_path.stat().st_size
            
            # Update manifest
            manifest = self._get_manifest()
            if str(source) not in manifest["backups"]:
                manifest["backups"][str(source)] = []
            
            manifest["backups"][str(source)].append({
                "backup_path": str(backup_path),
                "timestamp": datetime.utcnow().isoformat(),
                "operation": operation,
                "size_bytes": size
            })
            
            self._save_manifest(manifest)
            
            print(f"✅ Backup created: {backup_path.name} ({size} bytes)")
            
            # Rotate old backups
            self._rotate_backups(str(source))
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def _rotate_backups(self, file_path: str):
        """Keep only the most recent N backups per file"""
        manifest = self._get_manifest()
        
        if file_path not in manifest["backups"]:
            return
        
        backups = manifest["backups"][file_path]
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda b: b["timestamp"], reverse=True)
        
        # Keep only MAX_BACKUPS_PER_FILE most recent
        if len(backups) > self.MAX_BACKUPS_PER_FILE:
            to_delete = backups[self.MAX_BACKUPS_PER_FILE:]
            backups = backups[:self.MAX_BACKUPS_PER_FILE]
            
            # Delete old backup files
            for backup in to_delete:
                backup_path = Path(backup["backup_path"])
                if backup_path.exists():
                    backup_path.unlink()
                    print(f"🗑️  Rotated old backup: {backup_path.name}")
            
            # Update manifest
            manifest["backups"][file_path] = backups
            self._save_manifest(manifest)
    
    def list_backups(self, file_path: Optional[str] = None) -> dict:
        """List all backups, optionally filtered by file path"""
        manifest = self._get_manifest()
        
        if file_path:
            return {file_path: manifest["backups"].get(file_path, [])}
        
        return manifest["backups"]
    
    def restore_backup(self, backup_path: str, target_path: str) -> bool:
        """
        Restore a backup file to target location
        
        Args:
            backup_path: Path to backup file
            target_path: Where to restore it
            
        Returns:
            True if successful, False otherwise
        """
        backup = Path(backup_path)
        target = Path(target_path)
        
        if not backup.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        try:
            # Create backup of current file before restoring
            if target.exists():
                print(f"ℹ️  Creating backup of current file before restore...")
                self.create_backup(str(target), operation="pre-restore")
            
            # Restore
            shutil.copy2(backup, target)
            print(f"✅ Restored {backup.name} to {target}")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def check_before_write(self, file_path: str, show_preview: bool = True) -> bool:
        """
        Pre-flight check before writing to protected file
        
        Args:
            file_path: Path to file that will be written
            show_preview: Show content preview
            
        Returns:
            True if safe to proceed, False if should abort
        """
        source = Path(file_path)
        
        if not source.exists():
            print(f"✅ New file - safe to create: {file_path}")
            return True
        
        if source.stat().st_size == 0:
            print(f"⚠️  File is empty - safe to overwrite: {file_path}")
            return True
        
        # File has content - requires backup and confirmation
        size = source.stat().st_size
        lines = len(source.read_text().splitlines())
        
        print(f"\n{'='*70}")
        print(f"⚠️  PROTECTED FILE WRITE DETECTED")
        print(f"{'='*70}")
        print(f"File: {file_path}")
        print(f"Size: {size} bytes ({lines} lines)")
        
        if show_preview:
            content = source.read_text()
            preview_lines = content.splitlines()[:10]
            print(f"\nCurrent content preview (first 10 lines):")
            print("-" * 70)
            for i, line in enumerate(preview_lines, 1):
                print(f"{i:3d} | {line[:60]}{'...' if len(line) > 60 else ''}")
            if lines > 10:
                print(f"     ... and {lines - 10} more lines")
            print("-" * 70)
        
        # Create backup automatically
        print(f"\n🔒 Creating automatic backup before modification...")
        backup_path = self.create_backup(file_path, operation="pre-write")
        
        if backup_path:
            print(f"✅ Backup secured: {backup_path.name}")
            print(f"📝 To restore: python3 {__file__} restore {backup_path} {file_path}")
            return True
        else:
            print(f"❌ Backup failed - ABORTING write operation for safety")
            return False


def main():
    """CLI interface for file backup system"""
    import sys
    
    backup_system = FileBackupSystem()
    
    if len(sys.argv) < 2:
        print("N5 File Backup System")
        print("=" * 50)
        print("\nUsage:")
        print(f"  {sys.argv[0]} backup <file_path> [operation]")
        print(f"  {sys.argv[0]} list [file_path]")
        print(f"  {sys.argv[0]} restore <backup_path> <target_path>")
        print(f"  {sys.argv[0]} check <file_path>")
        print("\nExamples:")
        print(f"  {sys.argv[0]} backup /home/workspace/Documents/N5.md 'manual edit'")
        print(f"  {sys.argv[0]} list")
        print(f"  {sys.argv[0]} list /home/workspace/Documents/N5.md")
        print(f"  {sys.argv[0]} check /home/workspace/Documents/N5.md")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        if len(sys.argv) < 3:
            print("Error: File path required")
            sys.exit(1)
        file_path = sys.argv[2]
        operation = sys.argv[3] if len(sys.argv) > 3 else "manual"
        result = backup_system.create_backup(file_path, operation)
        sys.exit(0 if result else 1)
    
    elif command == "list":
        file_path = sys.argv[2] if len(sys.argv) > 2 else None
        backups = backup_system.list_backups(file_path)
        
        print("\n📦 Backup Inventory")
        print("=" * 70)
        
        for path, backup_list in backups.items():
            print(f"\n{path}")
            print(f"  Backups: {len(backup_list)}")
            for backup in backup_list:
                timestamp = backup["timestamp"][:19].replace("T", " ")
                size = backup["size_bytes"]
                operation = backup.get("operation", "unknown")
                print(f"    • {timestamp} | {size:,} bytes | {operation}")
                print(f"      {backup['backup_path']}")
        
        sys.exit(0)
    
    elif command == "restore":
        if len(sys.argv) < 4:
            print("Error: Both backup_path and target_path required")
            sys.exit(1)
        backup_path = sys.argv[2]
        target_path = sys.argv[3]
        result = backup_system.restore_backup(backup_path, target_path)
        sys.exit(0 if result else 1)
    
    elif command == "check":
        if len(sys.argv) < 3:
            print("Error: File path required")
            sys.exit(1)
        file_path = sys.argv[2]
        result = backup_system.check_before_write(file_path, show_preview=True)
        sys.exit(0 if result else 1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
