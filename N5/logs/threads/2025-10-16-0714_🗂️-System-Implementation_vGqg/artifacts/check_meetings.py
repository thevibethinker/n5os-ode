#!/usr/bin/env python3
from pathlib import Path

meetings_dir = Path("/home/workspace/N5/records/meetings")

with_b31 = []
without_b31 = []
empty = []

for meeting_dir in sorted(meetings_dir.glob("2025-*_external-*"), reverse=True):
    b_files = list(meeting_dir.glob("B*.md"))
    b31 = meeting_dir / "B31_STAKEHOLDER_RESEARCH.md"
    
    if not b_files:
        empty.append(meeting_dir.name)
    elif b31.exists():
        with_b31.append(meeting_dir.name)
    else:
        without_b31.append(meeting_dir.name)

print(f"=== MEETING STATUS ===\n")
print(f"With B31: {len(with_b31)}")
print(f"Without B31 (but has other B files): {len(without_b31)}")
print(f"Empty (no B files): {len(empty)}\n")

if empty:
    print(f"=== EMPTY MEETINGS (need full processing) ===")
    for i, name in enumerate(empty[:15], 1):
        print(f"{i:2}. {name}")
    print()

if without_b31:
    print(f"=== HAS B FILES BUT NO B31 ===")
    for i, name in enumerate(without_b31[:10], 1):
        print(f"{i:2}. {name}")
