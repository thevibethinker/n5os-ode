#!/usr/bin/env python3
"""
Batch rename meeting folders using B99 LLM naming
Dry-run first, then execute renames
"""

import sys
from pathlib import Path
import logging
import json
from typing import List, Dict, Optional

def find_processed_meetings(meetings_dir: Path) -> List[Path]:
    """Find all processed meeting folders with B26/B28 files"""
    meetings = []
    
    for folder in meetings_dir.iterdir():
        if not folder.is_dir():
            continue
        
        # Check if it's a meeting folder (has date prefix)
        if not folder.name[0].isdigit():
            continue
        
        # Check for B26 and B28
        b26 = folder / "B26_metadata.md"
        b28 = folder / "B28_strategic_intelligence.md"
        
        if b26.exists() and b28.exists():
            meetings.append(folder)
    
    return sorted(meetings)

def get_new_name_from_b99(folder: Path) -> Optional[str]:
    """
    Returns the new name that B99 would generate
    NOTE: This is a placeholder - actual implementation will invoke B99 prompt
    """
    # For now, return None to indicate "would call B99 here"
    # The actual scheduled task will invoke the B99 prompt directly
    return None

def generate_rename_plan(meetings_dir: Path) -> List[Dict]:
    """Generate list of renames to perform"""
    meetings = find_processed_meetings(meetings_dir)
    plan = []
    
    logging.info(f"Found {len(meetings)} processed meetings")
    
    for folder in meetings:
        # Skip if already well-named (no "unknown" in name)
        if "unknown" not in folder.name.lower() and "_" in folder.name:
            # Check if name looks reasonable
            parts = folder.name.split("_")
            if len(parts) >= 2 and parts[0].count("-") == 2:  # Has date
                logging.debug(f"Skipping well-named: {folder.name}")
                continue
        
        new_name = get_new_name_from_b99(folder)
        
        if new_name and new_name != folder.name:
            plan.append({
                "old_path": str(folder),
                "old_name": folder.name,
                "new_name": new_name,
                "new_path": str(folder.parent / new_name)
            })
    
    return plan

def execute_rename_plan(plan: List[Dict], dry_run: bool = True):
    """Execute the rename plan"""
    if not plan:
        logging.info("No renames needed")
        return
    
    logging.info(f"{'DRY RUN - ' if dry_run else ''}Renaming {len(plan)} folders")
    
    for item in plan:
        old_path = Path(item["old_path"])
        new_path = Path(item["new_path"])
        
        if dry_run:
            print(f"  Would rename: {item['old_name']} → {item['new_name']}")
        else:
            try:
                old_path.rename(new_path)
                print(f"  ✓ Renamed: {item['old_name']} → {item['new_name']}")
            except Exception as e:
                print(f"  ✗ Failed: {item['old_name']}: {e}")

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    meetings_dir = Path("/home/workspace/Personal/Meetings")
    
    # Check dry-run flag
    dry_run = "--execute" not in sys.argv
    
    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No changes will be made")
        print("Run with --execute to perform actual renames")
        print("=" * 70)
        print()
    
    # Generate plan
    plan = generate_rename_plan(meetings_dir)
    
    # Execute
    execute_rename_plan(plan, dry_run=dry_run)
    
    print()
    print("=" * 70)
    if dry_run:
        print(f"Found {len(plan)} meetings that would be renamed")
        print("NOTE: Actual B99 LLM naming will be used by scheduled task")
    else:
        print(f"Successfully renamed {len(plan)} meetings")
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
