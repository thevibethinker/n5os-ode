#!/usr/bin/env python3
"""Deduplicate meeting transcripts in Inbox based on content hash."""

import hashlib
from pathlib import Path
from collections import defaultdict

inbox = Path("/home/workspace/Personal/Meetings/Inbox")
files = list(inbox.glob("*.transcript.md"))

print(f"Found {len(files)} transcript files")

# Group by content hash
hash_groups = defaultdict(list)
for f in files:
    content = f.read_bytes()
    h = hashlib.sha256(content).hexdigest()
    hash_groups[h].append(f)

# Find duplicates
duplicates_removed = 0
for h, group in hash_groups.items():
    if len(group) > 1:
        # Sort to pick canonical version (prefer [IMPORTED-TO-ZO] versions, then shortest name)
        group.sort(key=lambda f: (
            0 if "[IMPORTED-TO-ZO]" in f.name else 1,
            len(f.name),
            f.name
        ))
        
        canonical = group[0]
        duplicates = group[1:]
        
        print(f"\nKeeping: {canonical.name}")
        for dup in duplicates:
            print(f"  Removing: {dup.name}")
            dup.unlink()
            duplicates_removed += 1

print(f"\n✅ Removed {duplicates_removed} duplicate files")
print(f"✅ Kept {len(hash_groups)} unique files")
