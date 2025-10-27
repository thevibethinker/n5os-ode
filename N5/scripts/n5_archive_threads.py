#!/usr/bin/env python3
"""
N5 Thread Archive Cleanup
Archives old thread exports into monthly compressed archives

Workflow:
1. Scan N5/logs/threads for threads older than N days
2. Group threads by month
3. Create tar.gz archives: YYYY-MM_threads_archive.tar.gz
4. Generate manifest files tracking archive contents
5. Remove original directories after successful archival

Design: Flow Over Pools (P2), Maintenance Over Organization
"""

import os
import sys
import json
import shutil
import tarfile
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
THREADS_DIR = WORKSPACE / "N5/logs/threads"
ARCHIVE_DIR = WORKSPACE / "N5/logs/thread_archives"


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Archive old thread exports to compressed monthly archives"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Archive threads older than N days (default: 30)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be archived without executing"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Archive even if fewer than 5 threads in a month"
    )
    parser.add_argument(
        "--extract",
        metavar="THREAD_ID",
        help="Extract a specific thread from archives"
    )
    parser.add_argument(
        "--list",
        metavar="ARCHIVE",
        help="List contents of a specific archive"
    )
    
    return parser.parse_args()


def get_thread_age(thread_dir: Path) -> int:
    """
    Get age of thread in days based on directory name
    
    Args:
        thread_dir: Path to thread directory
        
    Returns:
        Age in days, or None if cannot parse
    """
    # Extract date from directory name: YYYY-MM-DD-HHMM_...
    try:
        date_part = thread_dir.name.split('_')[0]
        # Handle both YYYY-MM-DD-HHMM and YYYY-MM-DD formats
        if len(date_part) >= 10:
            thread_date = datetime.strptime(date_part[:10], "%Y-%m-%d")
            age = (datetime.now() - thread_date).days
            return age
    except Exception as e:
        logger.debug(f"Could not parse date from {thread_dir.name}: {e}")
        return None


def scan_threads(min_age_days: int) -> dict:
    """
    Scan threads directory for old threads
    
    Args:
        min_age_days: Minimum age in days to consider for archival
        
    Returns:
        Dict mapping YYYY-MM to list of thread paths
    """
    if not THREADS_DIR.exists():
        logger.error(f"Threads directory not found: {THREADS_DIR}")
        return {}
    
    threads_by_month = defaultdict(list)
    
    for thread_dir in sorted(THREADS_DIR.iterdir()):
        if not thread_dir.is_dir():
            continue
        
        # Skip already-archived markers
        if thread_dir.name.endswith("_archived"):
            continue
        
        # Get thread age
        age = get_thread_age(thread_dir)
        if age is None:
            logger.warning(f"Skipping thread with unparseable date: {thread_dir.name}")
            continue
        
        # Check if old enough
        if age < min_age_days:
            logger.debug(f"Thread too recent ({age} days): {thread_dir.name}")
            continue
        
        # Extract YYYY-MM from directory name
        try:
            date_part = thread_dir.name.split('_')[0]
            year_month = date_part[:7]  # YYYY-MM
            threads_by_month[year_month].append(thread_dir)
        except Exception as e:
            logger.warning(f"Could not extract month from {thread_dir.name}: {e}")
    
    return threads_by_month


def create_archive(year_month: str, threads: list, dry_run: bool = False) -> Path:
    """
    Create compressed archive for a month's threads
    
    Args:
        year_month: YYYY-MM string
        threads: List of thread directory paths
        dry_run: If True, don't actually create archive
        
    Returns:
        Path to created archive, or None if dry-run
    """
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    archive_name = f"{year_month}_threads_archive.tar.gz"
    archive_path = ARCHIVE_DIR / archive_name
    manifest_path = ARCHIVE_DIR / f"{year_month}_manifest.json"
    
    if archive_path.exists():
        logger.warning(f"Archive already exists: {archive_name}")
        return archive_path
    
    logger.info(f"Creating archive: {archive_name} ({len(threads)} threads)")
    
    if dry_run:
        logger.info(f"[DRY RUN] Would create {archive_path}")
        return None
    
    # Create manifest
    manifest = {
        "created": datetime.now().isoformat(),
        "year_month": year_month,
        "thread_count": len(threads),
        "threads": []
    }
    
    # Create tar.gz archive
    with tarfile.open(archive_path, "w:gz") as tar:
        for thread in threads:
            # Add to archive with relative path
            arcname = thread.name
            tar.add(thread, arcname=arcname)
            
            # Add to manifest
            manifest["threads"].append({
                "directory": thread.name,
                "age_days": get_thread_age(thread),
                "size_bytes": sum(
                    f.stat().st_size
                    for f in thread.rglob("*") if f.is_file()
                )
            })
            
            logger.info(f"  Added: {thread.name}")
    
    # Write manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"✓ Created: {archive_path.name}")
    logger.info(f"  Size: {archive_path.stat().st_size / 1024 / 1024:.1f} MB")
    logger.info(f"  Manifest: {manifest_path.name}")
    
    return archive_path


def remove_archived_threads(threads: list, dry_run: bool = False) -> int:
    """
    Remove thread directories after successful archival
    
    Args:
        threads: List of thread directory paths
        dry_run: If True, don't actually remove
        
    Returns:
        Number of threads removed
    """
    removed = 0
    
    for thread in threads:
        if dry_run:
            logger.info(f"[DRY RUN] Would remove: {thread.name}")
            removed += 1
        else:
            try:
                shutil.rmtree(thread)
                logger.info(f"  Removed: {thread.name}")
                removed += 1
            except Exception as e:
                logger.error(f"Failed to remove {thread.name}: {e}")
    
    return removed


def extract_thread(thread_id: str) -> bool:
    """
    Extract a specific thread from archives
    
    Args:
        thread_id: Thread ID or partial directory name
        
    Returns:
        True if extracted successfully
    """
    if not ARCHIVE_DIR.exists():
        logger.error(f"Archive directory not found: {ARCHIVE_DIR}")
        return False
    
    # Search all archives for matching thread
    for archive in sorted(ARCHIVE_DIR.glob("*_threads_archive.tar.gz")):
        # Read manifest
        manifest_path = archive.with_name(archive.stem.replace("_threads_archive", "_manifest.json"))
        
        if not manifest_path.exists():
            logger.warning(f"Manifest not found for {archive.name}, scanning archive...")
            # Fallback: list archive contents
            with tarfile.open(archive, "r:gz") as tar:
                members = tar.getnames()
                matching = [m for m in members if thread_id in m]
        else:
            with open(manifest_path) as f:
                manifest = json.load(f)
            matching = [
                t["directory"] for t in manifest["threads"]
                if thread_id in t["directory"]
            ]
        
        if not matching:
            continue
        
        # Found matching thread(s)
        logger.info(f"Found in archive: {archive.name}")
        
        for thread_name in matching:
            # Extract to original location
            extract_path = THREADS_DIR / thread_name
            
            if extract_path.exists():
                logger.warning(f"Thread already exists: {thread_name}")
                continue
            
            logger.info(f"Extracting: {thread_name}")
            
            with tarfile.open(archive, "r:gz") as tar:
                # Extract specific member
                members = [m for m in tar.getmembers() if m.name.startswith(thread_name)]
                tar.extractall(THREADS_DIR, members=members)
            
            logger.info(f"✓ Extracted to: {extract_path}")
            return True
    
    logger.error(f"Thread not found in any archive: {thread_id}")
    return False


def list_archive(archive_name: str):
    """
    List contents of a specific archive
    
    Args:
        archive_name: Name of archive file (with or without extension)
    """
    if not archive_name.endswith(".tar.gz"):
        archive_name = f"{archive_name}_threads_archive.tar.gz"
    
    archive_path = ARCHIVE_DIR / archive_name
    
    if not archive_path.exists():
        logger.error(f"Archive not found: {archive_path}")
        return
    
    # Try to load manifest first
    manifest_path = archive_path.with_name(
        archive_path.stem.replace("_threads_archive", "_manifest.json")
    )
    
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        print(f"\nArchive: {archive_name}")
        print(f"Created: {manifest['created']}")
        print(f"Threads: {manifest['thread_count']}")
        print("\nContents:")
        
        for thread in sorted(manifest['threads'], key=lambda x: x['directory']):
            age = thread.get('age_days', '?')
            size = thread.get('size_bytes', 0) / 1024
            print(f"  • {thread['directory']:<60} ({age} days old, {size:.1f} KB)")
    else:
        # Fallback: read archive directly
        print(f"\nArchive: {archive_name}")
        print("(No manifest found, listing archive contents)\n")
        
        with tarfile.open(archive_path, "r:gz") as tar:
            for member in tar.getmembers():
                if member.isdir():
                    print(f"  • {member.name}")


def main():
    """Main execution"""
    args = parse_args()
    
    # Handle extract mode
    if args.extract:
        success = extract_thread(args.extract)
        return 0 if success else 1
    
    # Handle list mode
    if args.list:
        list_archive(args.list)
        return 0
    
    # Archive mode
    logger.info(f"Scanning for threads older than {args.days} days...")
    
    threads_by_month = scan_threads(args.days)
    
    if not threads_by_month:
        logger.info("No threads found for archival")
        return 0
    
    # Report what will be archived
    total_threads = sum(len(threads) for threads in threads_by_month.values())
    logger.info(f"Found {total_threads} threads across {len(threads_by_month)} months")
    
    for year_month in sorted(threads_by_month.keys()):
        threads = threads_by_month[year_month]
        logger.info(f"  {year_month}: {len(threads)} threads")
    
    if args.dry_run:
        logger.info("\n[DRY RUN] No changes will be made")
    
    # Create archives
    archived_count = 0
    removed_count = 0
    
    for year_month in sorted(threads_by_month.keys()):
        threads = threads_by_month[year_month]
        
        # Skip if too few threads (unless forced)
        if len(threads) < 5 and not args.force:
            logger.info(f"Skipping {year_month}: only {len(threads)} threads (use --force to archive anyway)")
            continue
        
        # Create archive
        archive_path = create_archive(year_month, threads, dry_run=args.dry_run)
        
        if archive_path or args.dry_run:
            archived_count += len(threads)
            
            # Remove original threads (only if not dry-run and archive succeeded)
            if not args.dry_run and archive_path:
                removed = remove_archived_threads(threads, dry_run=False)
                removed_count += removed
    
    # Summary
    print("\n" + "="*70)
    print("ARCHIVAL SUMMARY")
    print("="*70)
    print(f"Threads archived: {archived_count}")
    print(f"Threads removed: {removed_count}")
    print(f"Archives created: {len(threads_by_month)}")
    
    if ARCHIVE_DIR.exists():
        archive_size = sum(
            f.stat().st_size 
            for f in ARCHIVE_DIR.glob("*.tar.gz")
        ) / 1024 / 1024
        print(f"Total archive size: {archive_size:.1f} MB")
    
    print("\nTo extract a thread:")
    print(f"  python3 {Path(__file__).name} --extract <thread_id>")
    print("\nTo list archive contents:")
    print(f"  python3 {Path(__file__).name} --list YYYY-MM")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
