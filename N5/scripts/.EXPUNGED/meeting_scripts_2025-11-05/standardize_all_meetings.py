#!/usr/bin/env python3
"""
Bulk standardization of all meetings:
1. Add frontmatter to B*.md files
2. Rename folders to standard format

ATOMIC: Processes in two phases, logs all changes
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from add_frontmatter_to_meeting import process_meeting_folder as add_frontmatter
from rename_meeting_folder import process_folder as rename_folder

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
RENAME_LOG = MEETINGS_DIR / "rename_log.jsonl"

def get_meeting_folders() -> list[Path]:
    """Get all meeting folders (exclude special directories)."""
    exclude = {"Inbox", ".stfolder", ".stversions"}
    
    folders = []
    for item in MEETINGS_DIR.iterdir():
        if item.is_dir() and item.name not in exclude and not item.name.startswith('.'):
            folders.append(item)
    
    return sorted(folders)

def run_standardization(dry_run: bool = True, frontmatter: bool = True, rename: bool = True):
    """Run full standardization process."""
    
    folders = get_meeting_folders()
    
    print(f"📊 Found {len(folders)} meeting folders")
    print(f"{'🔍 DRY RUN MODE' if dry_run else '⚡ LIVE MODE'}\n")
    
    stats = {
        "total": len(folders),
        "frontmatter_added": 0,
        "renamed": 0,
        "skipped_old_format": 0,
        "skipped_already_correct": 0,
        "errors": 0
    }
    
    for folder in folders:
        try:
            # Phase 1: Add frontmatter
            if frontmatter:
                fm_result = add_frontmatter(folder, dry_run=dry_run)
                if fm_result["success"] and fm_result.get("files_updated", 0) > 0:
                    stats["frontmatter_added"] += 1
            
            # Phase 2: Rename folder
            if rename:
                rename_result = rename_folder(folder, RENAME_LOG, dry_run=dry_run)
                
                if not rename_result["success"]:
                    if rename_result.get("reason") == "no_b26_or_old_format":
                        stats["skipped_old_format"] += 1
                    else:
                        stats["errors"] += 1
                elif rename_result.get("action") == "renamed":
                    stats["renamed"] += 1
                elif rename_result.get("action") == "skip":
                    stats["skipped_already_correct"] += 1
                    
        except Exception as e:
            print(f"❌ Error processing {folder.name}: {e}")
            stats["errors"] += 1
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total folders:            {stats['total']}")
    print(f"Frontmatter added:        {stats['frontmatter_added']}")
    print(f"Renamed:                  {stats['renamed']}")
    print(f"Already correct:          {stats['skipped_already_correct']}")
    print(f"Skipped (old format):     {stats['skipped_old_format']}")
    print(f"Errors:                   {stats['errors']}")
    
    if dry_run:
        print("\n🔍 This was a DRY RUN - no changes made")
        print("Run with --execute to apply changes")
    else:
        print(f"\n✅ Changes logged to: {RENAME_LOG}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Standardize all meeting folders")
    parser.add_argument("--execute", action="store_true", help="Execute changes (default is dry-run)")
    parser.add_argument("--frontmatter-only", action="store_true", help="Only add frontmatter, skip rename")
    parser.add_argument("--rename-only", action="store_true", help="Only rename, skip frontmatter")
    
    args = parser.parse_args()
    
    frontmatter = not args.rename_only
    rename = not args.frontmatter_only
    
    run_standardization(
        dry_run=not args.execute,
        frontmatter=frontmatter,
        rename=rename
    )
