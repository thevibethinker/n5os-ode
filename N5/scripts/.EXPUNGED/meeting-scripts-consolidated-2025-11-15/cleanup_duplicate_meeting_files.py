#!/usr/bin/env python3
"""Clean up duplicate lowercase intelligence files, keep B## and UPPERCASE"""

from pathlib import Path
import shutil

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")

duplicate_patterns = [
    "action_items.md",
    "key_insights.md", 
    "metadata.md",
    "relationship_intel.md",
    "strategic_analysis.md",
    "talking_points.md"
]

def main():
    cleaned = []
    
    for meeting_dir in MEETINGS_DIR.iterdir():
        if not meeting_dir.is_dir() or meeting_dir.name.startswith('.') or meeting_dir.name in ['Inbox', '_ARCHIVE_2024']:
            continue
        
        for pattern in duplicate_patterns:
            lowercase_file = meeting_dir / pattern
            if lowercase_file.exists():
                # Check if UPPERCASE or B## equivalent exists
                uppercase = meeting_dir / pattern.upper()
                b_format = meeting_dir / f"B{pattern.split('_')[0][0:2]}_{pattern.split('.')[0].upper()}.md" if '_' in pattern else None
                
                if uppercase.exists() or (b_format and b_format.exists()):
                    lowercase_file.unlink()
                    cleaned.append(str(lowercase_file))
    
    print(f"✓ Cleaned {len(cleaned)} duplicate lowercase files")
    for f in cleaned[:10]:
        print(f"  - {f}")
    if len(cleaned) > 10:
        print(f"  ... and {len(cleaned) - 10} more")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

