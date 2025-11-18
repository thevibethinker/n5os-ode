#!/usr/bin/env python3
"""
Remove duplicate entries from meeting registry
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

REGISTRY_PATH = Path("/home/workspace/N5/data/meeting_gdrive_registry.jsonl")
BACKUP_DIR = Path("/home/workspace/N5/data/backups")

def analyze_duplicates():
    """Analyze duplicate Drive IDs in registry."""
    if not REGISTRY_PATH.exists():
        return {}
    
    by_id = defaultdict(list)
    entries = []
    
    with open(REGISTRY_PATH) as f:
        for idx, line in enumerate(f):
            entry = json.loads(line.strip())
            entries.append((idx, entry))
            gdrive_id = entry.get("gdrive_id")
            if gdrive_id:
                by_id[gdrive_id].append((idx, entry))
    
    duplicates = {k: v for k, v in by_id.items() if len(v) > 1}
    return duplicates, entries

def backup_registry():
    """Backup registry before modification."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"meeting_gdrive_registry_{timestamp}.jsonl"
    shutil.copy(REGISTRY_PATH, backup_path)
    return backup_path

def deduplicate_registry(dry_run=False):
    """Remove duplicates, keeping the first occurrence."""
    duplicates, all_entries = analyze_duplicates()
    
    if not duplicates:
        print("✓ No duplicates found")
        return 0
    
    # Identify entries to keep (first occurrence of each ID)
    seen_ids = set()
    keep_indices = set()
    
    for idx, entry in all_entries:
        gdrive_id = entry.get("gdrive_id")
        if gdrive_id not in seen_ids:
            seen_ids.add(gdrive_id)
            keep_indices.add(idx)
    
    removed_count = len(all_entries) - len(keep_indices)
    
    print(f"Found {len(duplicates)} duplicate Drive IDs")
    print(f"Will remove {removed_count} duplicate entries")
    print()
    
    print("Duplicates to remove:")
    for gdrive_id, occurrences in list(duplicates.items())[:5]:
        print(f"  {gdrive_id}: {len(occurrences)} occurrences, keeping first")
    print()
    
    if dry_run:
        print("DRY RUN - no changes made")
        return removed_count
    
    # Backup first
    backup_path = backup_registry()
    print(f"✓ Backup created: {backup_path}")
    print()
    
    # Write deduplicated registry
    with open(REGISTRY_PATH, 'w') as f:
        for idx, entry in all_entries:
            if idx in keep_indices:
                f.write(json.dumps(entry) + "\n")
    
    print(f"✓ Removed {removed_count} duplicate entries")
    return removed_count

def main():
    print("=" * 80)
    print("REGISTRY DEDUPLICATION")
    print("=" * 80)
    print()
    
    # Dry run first
    print("Analyzing registry...")
    removed = deduplicate_registry(dry_run=True)
    print()
    
    if removed == 0:
        return
    
    response = input(f"Remove {removed} duplicate entries? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    print()
    deduplicate_registry(dry_run=False)
    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

