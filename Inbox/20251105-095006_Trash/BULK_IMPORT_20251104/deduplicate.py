#!/usr/bin/env python3
"""
Deduplicate meeting transcripts using multiple heuristics:
1. Exact filename matches
2. Same title + timestamp variants (e.g., "14-48-06-960Z" vs "14-48-06.960Z")
3. Same title + timestamps within 5 minutes
4. MD5 hash matches (identical content)
"""
import hashlib
import re
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

STAGING = Path("/home/workspace/Personal/Meetings/BULK_IMPORT_20251104/staging")
DUPLICATES_DIR = STAGING.parent / "duplicates"

def parse_filename(filename: str):
    """Extract title and timestamp from filename"""
    # Pattern: "Title-transcript-2025-10-23T14-48-06.960Z.transcript.md"
    match = re.match(r'(.+?)-transcript-([\d\-]+T[\d\-:.]+Z?)\.transcript\.md$', filename)
    if match:
        title = match.group(1).strip()
        timestamp_str = match.group(2)
        
        # Normalize timestamp (handle both '-' and '.' in milliseconds)
        timestamp_str = re.sub(r'[-.](\d{3})Z', r'.\1Z', timestamp_str)
        
        try:
            # Parse timestamp
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H-%M-%S.%fZ')
        except ValueError:
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H-%M-%SZ')
            except ValueError:
                timestamp = None
        
        return title, timestamp, timestamp_str
    return None, None, None

def get_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of file content"""
    return hashlib.md5(file_path.read_bytes()).hexdigest()

def main():
    DUPLICATES_DIR.mkdir(exist_ok=True)
    
    files = list(STAGING.glob("*.transcript.md"))
    logger.info(f"Analyzing {len(files)} files for duplicates...\n")
    
    # Group by title
    by_title = defaultdict(list)
    for file_path in files:
        title, timestamp, timestamp_str = parse_filename(file_path.name)
        if title:
            by_title[title].append({
                'path': file_path,
                'title': title,
                'timestamp': timestamp,
                'timestamp_str': timestamp_str
            })
    
    duplicates_found = []
    kept_files = set(files)
    files_to_remove = set()  # Track files to remove
    
    # Check each title group for duplicates
    for title, file_group in by_title.items():
        if len(file_group) <= 1:
            continue
        
        # Sort by timestamp
        file_group.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min)
        
        # Check for duplicates within this title group
        for i, file1 in enumerate(file_group):
            for file2 in file_group[i+1:]:
                is_duplicate = False
                reason = ""
                
                # Check 1: Exact same timestamp (different formatting)
                if file1['timestamp_str'] == file2['timestamp_str']:
                    is_duplicate = True
                    reason = "Exact timestamp match"
                
                # Check 2: Timestamps within 5 minutes
                elif file1['timestamp'] and file2['timestamp']:
                    time_diff = abs((file2['timestamp'] - file1['timestamp']).total_seconds())
                    if time_diff < 300:  # 5 minutes
                        is_duplicate = True
                        reason = f"Timestamps {int(time_diff)}s apart"
                
                # Check 3: Same content (MD5 hash)
                if not is_duplicate:
                    if get_file_hash(file1['path']) == get_file_hash(file2['path']):
                        is_duplicate = True
                        reason = "Identical content (MD5)"
                
                if is_duplicate:
                    # Keep the older file (earlier timestamp)
                    keep = file1 if (not file2['timestamp'] or (file1['timestamp'] and file1['timestamp'] < file2['timestamp'])) else file2
                    remove = file2 if keep == file1 else file1
                    
                    # Only record if not already marked for removal
                    if remove['path'] not in files_to_remove:
                        duplicates_found.append({
                            'keep': keep['path'],
                            'remove': remove['path'],
                            'reason': reason
                        })
                        files_to_remove.add(remove['path'])
                        
                        if remove['path'] in kept_files:
                            kept_files.discard(remove['path'])
    
    # Report findings
    if duplicates_found:
        logger.info(f"🔍 Found {len(duplicates_found)} duplicate pairs:\n")
        
        for dup in duplicates_found:
            logger.info(f"  Duplicate: {dup['remove'].name}")
            logger.info(f"  Reason: {dup['reason']}")
            logger.info(f"  Keeping: {dup['keep'].name}")
            logger.info("")
            
            # Move duplicate to duplicates folder (check if still exists)
            if dup['remove'].exists():
                dup['remove'].rename(DUPLICATES_DIR / dup['remove'].name)
        
        logger.info(f"\n✅ Moved {len(duplicates_found)} duplicates to: {DUPLICATES_DIR}")
        logger.info(f"📊 Remaining unique files: {len(kept_files)}")
    else:
        logger.info("✅ No duplicates found!")
        logger.info(f"📊 All {len(files)} files are unique")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
