#!/usr/bin/env python3
"""
Log Rotation - Priority 4
Rotate and compress meeting monitor logs to prevent excessive disk usage.
"""

import sys
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import pytz


class LogRotator:
    """Handle log rotation for meeting monitor."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.et_tz = pytz.timezone('America/New_York')
        self.log_dir = self.base_dir / 'logs'
        self.archive_dir = self.log_dir / 'archived'
        
        # Configuration
        self.retention_days = 30
        self.compress_after_days = 7
    
    def ensure_archive_dir(self):
        """Create archive directory if it doesn't exist."""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def rotate_log_file(self, log_file):
        """Rotate a single log file."""
        if not log_file.exists() or log_file.stat().st_size == 0:
            return None
        
        # Generate archive filename with date
        timestamp = datetime.now(self.et_tz).strftime('%Y-%m-%d')
        archive_name = f"{log_file.stem}-{timestamp}{log_file.suffix}"
        archive_path = self.archive_dir / archive_name
        
        # If archive already exists, append to it
        if archive_path.exists():
            with open(archive_path, 'a', encoding='utf-8') as dest:
                dest.write('\n')
                with open(log_file, 'r', encoding='utf-8') as src:
                    dest.write(src.read())
        else:
            # Move log to archive
            shutil.copy2(log_file, archive_path)
        
        # Clear original log file
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Log rotated at {datetime.now(self.et_tz).isoformat()}\n")
        
        return archive_path
    
    def compress_old_logs(self):
        """Compress logs older than compress_after_days."""
        cutoff = datetime.now(self.et_tz) - timedelta(days=self.compress_after_days)
        compressed = []
        
        for log_file in self.archive_dir.glob('*.log'):
            # Skip already compressed files
            if log_file.suffix == '.gz':
                continue
            
            # Check file age
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            mtime = self.et_tz.localize(mtime) if mtime.tzinfo is None else mtime
            
            if mtime < cutoff:
                # Compress file
                gz_path = log_file.with_suffix(log_file.suffix + '.gz')
                
                with open(log_file, 'rb') as f_in:
                    with gzip.open(gz_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove original
                log_file.unlink()
                compressed.append(gz_path.name)
        
        return compressed
    
    def delete_old_logs(self):
        """Delete logs older than retention_days."""
        cutoff = datetime.now(self.et_tz) - timedelta(days=self.retention_days)
        deleted = []
        
        for log_file in self.archive_dir.glob('*'):
            if log_file.is_file():
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                mtime = self.et_tz.localize(mtime) if mtime.tzinfo is None else mtime
                
                if mtime < cutoff:
                    log_file.unlink()
                    deleted.append(log_file.name)
        
        return deleted
    
    def get_log_stats(self):
        """Get statistics about log files."""
        stats = {
            'active_logs': [],
            'archived_logs': 0,
            'compressed_logs': 0,
            'total_size_mb': 0
        }
        
        # Active logs
        for log_file in self.log_dir.glob('*.log'):
            if log_file.parent == self.log_dir:  # Not in archive
                size = log_file.stat().st_size / (1024 * 1024)
                stats['active_logs'].append({
                    'name': log_file.name,
                    'size_mb': round(size, 2)
                })
                stats['total_size_mb'] += size
        
        # Archived logs
        if self.archive_dir.exists():
            for log_file in self.archive_dir.glob('*'):
                size = log_file.stat().st_size / (1024 * 1024)
                stats['total_size_mb'] += size
                
                if log_file.suffix == '.gz':
                    stats['compressed_logs'] += 1
                else:
                    stats['archived_logs'] += 1
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        
        return stats
    
    def run_rotation(self):
        """Execute full log rotation process."""
        print("=" * 60)
        print("Log Rotation - Meeting Monitor")
        print("=" * 60)
        
        timestamp = datetime.now(self.et_tz).strftime('%Y-%m-%d %I:%M %p ET')
        print(f"Started: {timestamp}\n")
        
        # Ensure archive directory exists
        self.ensure_archive_dir()
        print("✓ Archive directory ready\n")
        
        # Get stats before rotation
        print("Before Rotation:")
        print("-" * 60)
        stats_before = self.get_log_stats()
        print(f"  Active logs: {len(stats_before['active_logs'])}")
        print(f"  Archived logs: {stats_before['archived_logs']}")
        print(f"  Compressed logs: {stats_before['compressed_logs']}")
        print(f"  Total size: {stats_before['total_size_mb']} MB\n")
        
        # Rotate main log file
        print("Rotating Logs:")
        print("-" * 60)
        
        log_files = [
            self.log_dir / 'meeting_monitor.log',
            self.log_dir / 'health_check.log'
        ]
        
        rotated = []
        for log_file in log_files:
            if log_file.exists():
                archive_path = self.rotate_log_file(log_file)
                if archive_path:
                    rotated.append(log_file.name)
                    print(f"  ✓ Rotated: {log_file.name}")
        
        if not rotated:
            print("  No logs to rotate")
        
        print()
        
        # Compress old logs
        print("Compressing Old Logs:")
        print("-" * 60)
        compressed = self.compress_old_logs()
        
        if compressed:
            for filename in compressed:
                print(f"  ✓ Compressed: {filename}")
        else:
            print("  No logs to compress")
        
        print()
        
        # Delete very old logs
        print("Deleting Old Logs:")
        print("-" * 60)
        deleted = self.delete_old_logs()
        
        if deleted:
            for filename in deleted:
                print(f"  ✓ Deleted: {filename}")
        else:
            print("  No logs to delete")
        
        print()
        
        # Get stats after rotation
        print("After Rotation:")
        print("-" * 60)
        stats_after = self.get_log_stats()
        print(f"  Active logs: {len(stats_after['active_logs'])}")
        print(f"  Archived logs: {stats_after['archived_logs']}")
        print(f"  Compressed logs: {stats_after['compressed_logs']}")
        print(f"  Total size: {stats_after['total_size_mb']} MB")
        
        saved = stats_before['total_size_mb'] - stats_after['total_size_mb']
        if saved > 0:
            print(f"  Space saved: {saved:.2f} MB")
        
        print()
        print("=" * 60)
        print("Log Rotation Complete")
        print("=" * 60)
        print()
        
        return {
            'rotated': len(rotated),
            'compressed': len(compressed),
            'deleted': len(deleted),
            'space_saved_mb': saved
        }


def main():
    """Run log rotation."""
    rotator = LogRotator()
    results = rotator.run_rotation()
    
    # Return success
    sys.exit(0)


if __name__ == '__main__':
    main()
