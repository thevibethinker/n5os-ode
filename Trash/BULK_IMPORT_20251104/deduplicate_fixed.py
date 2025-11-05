#!/usr/bin/env python3
"""
Deduplicate meeting transcripts - keep oldest in each duplicate group
"""
import hashlib
import re
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

STAGING = Path("/home/workspace/Personal/Meetings/BULK_IMPORT_20251104/staging")
DUPLICATES_DIR = STAGING.parent / "duplicates"

def parse_filename(filename: str):
    """Extract title and timestamp from filename"""
    match = re.match(r'(.+?)-transcript-([\d\-]+T[\d\-:.]+Z?)\.transcript\.md$', filename)
    if match:
        title = match.group(1).strip()
        timestamp_str = match.group(2)
        timestamp_str = re.sub(r'[-.](\d{3})Z', r'.\1Z', timestamp_str)
        
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H-%M-%S.%fZ')
        except ValueError:
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H-%M-%SZ')
            except ValueError:
                timestamp = None
        
        return title, timestamp, timestamp_str
    return None, None, None

def get_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash"""
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
                'hash': get_file_hash(file_path)
            })
    
    total_removed = 0
    
    # For each title group, find duplicate clusters
    for title, file_group in by_title.items():
        if len(file_group) <= 1:
            continue
        
        # Sort by timestamp (oldest first)
        file_group.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min)
        
        # Group files that are duplicates (within 5 min OR same hash)
        duplicate_groups = []
        processed = set()
        
        for i, file1 in enumerate(file_group):
            if file1['path'] in processed:
                continue
            
            group = [file1]
            processed.add(file1['path'])
            
            # Find all files that are duplicates of file1
            for file2 in file_group[i+1:]:
                if file2['path'] in processed:
                    continue
                
                # Check if duplicate
                is_dup = False
                
                # Same hash
                if file1['hash'] == file2['hash']:
                    is_dup = True
                # Within 5 minutes
                elif file1['timestamp'] and file2['timestamp']:
                    time_diff = abs((file2['timestamp'] - file1['timestamp']).total_seconds())
                    if time_diff < 300:
                        is_dup = True
                
                if is_dup:
                    group.append(file2)
                    processed.add(file2['path'])
            
            if len(group) > 1:
                duplicate_groups.append(group)
        
        # For each duplicate group, keep the first (oldest), remove others
        for group in duplicate_groups:
            keep = group[0]
            to_remove = group[1:]
            
            logger.info(f"📦 Duplicate group for: {title}")
            logger.info(f"   Keeping: {keep['path'].name}")
            for dup in to_remove:
                logger.info(f"   Removing: {dup['path'].name}")
                dup['path'].rename(DUPLICATES_DIR / dup['path'].name)
                total_removed += 1
            logger.info("")
    
    remaining = len(list(STAGING.glob("*.transcript.md")))
    
    if total_removed > 0:
        logger.info(f"✅ Moved {total_removed} duplicates to: {DUPLICATES_DIR}")
        logger.info(f"📊 Remaining unique files: {remaining}")
    else:
        logger.info("✅ No duplicates found!")
        logger.info(f"📊 All {len(files)} files are unique")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
