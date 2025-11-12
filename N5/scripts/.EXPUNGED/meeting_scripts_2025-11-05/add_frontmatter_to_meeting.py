#!/usr/bin/env python3
"""
Add standardized frontmatter to meeting intelligence files.
Runs on all B*.md files in a meeting folder.
"""

import re
from pathlib import Path
from datetime import datetime
import sys

# Import taxonomy inference
sys.path.insert(0, str(Path(__file__).parent))
from infer_meeting_taxonomy import infer_from_folder

PROCESSING_VERSION = "2.0"

def extract_meeting_date(folder_name: str) -> str:
    """Extract date from folder name or use today."""
    # Try to parse YYYY-MM-DD from folder name
    if match := re.search(r'20\d{2}-\d{2}-\d{2}', folder_name):
        return match.group(0)
    
    # Try to parse from transcript ID
    if match := re.search(r'transcript-(\d{4})-(\d{2})-(\d{2})', folder_name):
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    
    # Fall back to today
    return datetime.now().strftime("%Y-%m-%d")

def has_frontmatter(content: str) -> bool:
    """Check if file already has YAML frontmatter."""
    return content.startswith("---\n")

def generate_frontmatter(meeting_type: str, meeting_subtype: str, meeting_date: str) -> str:
    """Generate standardized frontmatter block."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    return f"""---
processing_version: {PROCESSING_VERSION}
meeting_date: {meeting_date}
meeting_type: {meeting_type}
meeting_subtype: {meeting_subtype}
created: {today}
last_edited: {today}
---

"""

def add_frontmatter_to_file(file_path: Path, meeting_type: str, meeting_subtype: str, meeting_date: str) -> bool:
    """Add frontmatter to a single file if missing."""
    content = file_path.read_text()
    
    if has_frontmatter(content):
        print(f"  ⏭️  {file_path.name} - Already has frontmatter, skipping")
        return False
    
    frontmatter = generate_frontmatter(meeting_type, meeting_subtype, meeting_date)
    new_content = frontmatter + content
    
    file_path.write_text(new_content)
    print(f"  ✅ {file_path.name} - Added frontmatter")
    return True

def process_meeting_folder(folder_path: Path, dry_run: bool = False) -> dict:
    """Add frontmatter to all B*.md files in meeting folder."""
    
    # Infer taxonomy from B26
    taxonomy = infer_from_folder(folder_path)
    if not taxonomy:
        print(f"❌ {folder_path.name}: No B26_metadata.md found or old format")
        return {"success": False, "reason": "no_b26"}
    
    meeting_type, meeting_subtype = taxonomy
    meeting_date = extract_meeting_date(folder_path.name)
    
    print(f"\n📁 {folder_path.name}")
    print(f"   Type: {meeting_type}/{meeting_subtype}, Date: {meeting_date}")
    
    if dry_run:
        print("   [DRY RUN MODE - No changes made]")
        return {"success": True, "dry_run": True}
    
    # Find all B*.md files
    b_files = sorted(folder_path.glob("B*.md"))
    
    if not b_files:
        print("   ⚠️  No B*.md files found")
        return {"success": True, "files_processed": 0}
    
    files_updated = 0
    for file_path in b_files:
        if add_frontmatter_to_file(file_path, meeting_type, meeting_subtype, meeting_date):
            files_updated += 1
    
    return {
        "success": True,
        "files_processed": len(b_files),
        "files_updated": files_updated
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add frontmatter to meeting intelligence files")
    parser.add_argument("folder", type=Path, help="Meeting folder path")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    if not args.folder.is_dir():
        print(f"ERROR: {args.folder} is not a directory")
        sys.exit(1)
    
    result = process_meeting_folder(args.folder, dry_run=args.dry_run)
    
    if result["success"]:
        print("\n✅ Complete")
    else:
        print(f"\n❌ Failed: {result.get('reason', 'unknown')}")
        sys.exit(1)
