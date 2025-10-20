#!/usr/bin/env python3
"""
Read B31 files from the 7 meetings and extract insights for manual review
"""
from pathlib import Path

meetings = [
    "2025-10-15_external-sam-partnership-sync",
    "2025-10-15_external-sam-partnership-sync_211410",
    "2025-10-14_external-nira-team",
    "2025-10-14_external-michael-maher",
    "2025-10-09_external-alex-wisdom-partners-coaching",
    "2025-09-29_external-remotely-good-careerspan",
    "2025-09-24_external-alex-wisdom-partners-coaching",
]

base_dir = Path("/home/workspace/N5/records/meetings")

for meeting_id in meetings:
    b31 = base_dir / meeting_id / "B31_STAKEHOLDER_RESEARCH.md"
    if b31.exists():
        print(f"\n{'='*80}")
        print(f"MEETING: {meeting_id}")
        print(f"{'='*80}\n")
        content = b31.read_text()
        print(content[:2000])  # First 2000 chars to see structure
        print("\n... (truncated)")
