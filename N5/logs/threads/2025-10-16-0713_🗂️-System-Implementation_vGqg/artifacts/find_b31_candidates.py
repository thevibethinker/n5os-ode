#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

meetings_dir = Path("/home/workspace/N5/records/meetings")
results = []

for meeting_dir in sorted(meetings_dir.glob("2025-*_external-*"), reverse=True):
    b08 = meeting_dir / "B08_STAKEHOLDER_INTELLIGENCE.md"
    b31 = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
    
    if b08.exists() and not b31.exists():
        # Get modification time
        mtime = datetime.fromtimestamp(b08.stat().st_mtime)
        results.append((mtime, meeting_dir.name))

print(f"Found {len(results)} meetings with B08 but no B31:\n")
for i, (mtime, name) in enumerate(results[:15], 1):
    print(f"{i:2}. {name} (B08 updated: {mtime.strftime('%Y-%m-%d %H:%M')})")
