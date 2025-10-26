#!/usr/bin/env python3
"""
Commands Chronological Setup

Creates dated symlinks for all command files to enable chronological sorting
while maintaining backward compatibility with existing semantic names.

Usage:
    python3 commands_chronological_setup.py [--dry-run] [--migrate]
    
Modes:
    --dry-run: Preview what would happen
    --migrate: Actually rename files (permanent)
    (default): Create symlinks (safe, reversible)
"""

import argparse
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


class CommandsChronologicalMigrator:
    """Migrates command files to chronological naming."""
    
    def __init__(self, commands_dir: Path):
        self.commands_dir = commands_dir
        self.stats = {
            'total': 0,
            'processed': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def get_file_creation_date(self, filepath: Path) -> str:
        """Extract creation date from file metadata."""
        try:
            # Get file modification time (best proxy for creation)
            mtime = filepath.stat().st_mtime
            dt = datetime.fromtimestamp(mtime)
            return dt.strftime('%Y-%m-%d')
        except Exception as e:
            logger.warning(f"Could not get date for {filepath.name}: {e}")
            # Fallback to today
            return datetime.now().strftime('%Y-%m-%d')
    
    def is_dated_format(self, filename: str) -> bool:
        """Check if filename already has YYYY-MM-DD prefix."""
        import re
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}_', filename))
    
    def generate_dated_name(self, filepath: Path) -> str:
        """Generate YYYY-MM-DD_original-name.md format."""
        date = self.get_file_creation_date(filepath)
        return f"{date}_{filepath.name}"
    
    def create_symlink(self, original: Path, dry_run: bool = False) -> bool:
        """Create dated symlink pointing to original file."""
        if self.is_dated_format(original.name):
            logger.info(f"⏭️  Already dated: {original.name}")
            self.stats['skipped'] += 1
            return True
        
        dated_name = self.generate_dated_name(original)
        symlink_path = self.commands_dir / dated_name
        
        if symlink_path.exists():
            logger.warning(f"⚠️  Link exists: {dated_name}")
            self.stats['skipped'] += 1
            return True
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create: {dated_name} -> {original.name}")
            self.stats['processed'] += 1
            return True
        
        try:
            # Create relative symlink
            os.symlink(original.name, symlink_path)
            logger.info(f"✓ Created link: {dated_name}")
            self.stats['processed'] += 1
            return True
        except Exception as e:
            logger.error(f"✗ Failed to link {original.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def migrate_file(self, original: Path, dry_run: bool = False) -> bool:
        """Rename file to dated format (permanent)."""
        if self.is_dated_format(original.name):
            logger.info(f"⏭️  Already dated: {original.name}")
            self.stats['skipped'] += 1
            return True
        
        dated_name = self.generate_dated_name(original)
        new_path = self.commands_dir / dated_name
        
        if new_path.exists():
            logger.warning(f"⚠️  Target exists: {dated_name}")
            self.stats['skipped'] += 1
            return True
        
        if dry_run:
            logger.info(f"[DRY RUN] Would rename: {original.name} -> {dated_name}")
            self.stats['processed'] += 1
            return True
        
        try:
            shutil.move(str(original), str(new_path))
            logger.info(f"✓ Renamed: {original.name} -> {dated_name}")
            self.stats['processed'] += 1
            return True
        except Exception as e:
            logger.error(f"✗ Failed to rename {original.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def process_all(self, mode: str = 'symlink', dry_run: bool = False):
        """Process all .md files in commands directory."""
        files = sorted(self.commands_dir.glob('*.md'))
        self.stats['total'] = len(files)
        
        logger.info(f"Found {len(files)} command files")
        logger.info(f"Mode: {mode} | Dry run: {dry_run}")
        logger.info("=" * 60)
        
        for filepath in files:
            if mode == 'migrate':
                self.migrate_file(filepath, dry_run=dry_run)
            else:
                self.create_symlink(filepath, dry_run=dry_run)
        
        logger.info("=" * 60)
        logger.info(f"✓ Processed: {self.stats['processed']}")
        logger.info(f"⏭️  Skipped: {self.stats['skipped']}")
        logger.info(f"✗ Errors: {self.stats['errors']}")
        logger.info(f"📊 Total: {self.stats['total']}")
    
    def cleanup_symlinks(self, dry_run: bool = False):
        """Remove all dated symlinks (cleanup operation)."""
        symlinks = [f for f in self.commands_dir.iterdir() 
                   if f.is_symlink() and self.is_dated_format(f.name)]
        
        logger.info(f"Found {len(symlinks)} dated symlinks to remove")
        
        for symlink in symlinks:
            if dry_run:
                logger.info(f"[DRY RUN] Would remove: {symlink.name}")
            else:
                try:
                    symlink.unlink()
                    logger.info(f"✓ Removed: {symlink.name}")
                except Exception as e:
                    logger.error(f"✗ Failed to remove {symlink.name}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Setup chronological naming for N5 commands'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without making them'
    )
    parser.add_argument(
        '--migrate',
        action='store_true',
        help='Permanently rename files (default: create symlinks)'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Remove all dated symlinks'
    )
    parser.add_argument(
        '--commands-dir',
        type=Path,
        default=Path('/home/workspace/N5/commands'),
        help='Commands directory path'
    )
    
    args = parser.parse_args()
    
    if not args.commands_dir.exists():
        logger.error(f"Commands directory not found: {args.commands_dir}")
        return 1
    
    migrator = CommandsChronologicalMigrator(args.commands_dir)
    
    if args.cleanup:
        migrator.cleanup_symlinks(dry_run=args.dry_run)
    else:
        mode = 'migrate' if args.migrate else 'symlink'
        migrator.process_all(mode=mode, dry_run=args.dry_run)
    
    return 0 if migrator.stats['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
