#!/usr/bin/env python3
"""
Reorganize meetings into weekly folders and clean up structure.
Run with --dry-run first to preview changes.
"""
import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
MEETINGS = Path("/home/workspace/Personal/Meetings")

def get_week_folder_name(date_str: str) -> str:
    """Get week folder name like 'Week-of-2025-12-01' (Monday of that week)."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        monday = date - timedelta(days=date.weekday())
        return f"Week-of-{monday.strftime('%Y-%m-%d')}"
    except:
        return "Unknown-Week"

def extract_readable_name(folder_name: str, manifest_path: Path = None) -> str:
    """Extract a clean, readable meeting name."""
    # Try to get title from manifest first
    if manifest_path and manifest_path.exists():
        try:
            with open(manifest_path) as f:
                data = json.load(f)
                if data.get("meeting_title"):
                    title = data["meeting_title"]
                    # Clean the title
                    title = title.replace("_", " ").strip()
                    if len(title) > 5:
                        return title[:60]
        except:
            pass
    
    # Extract from folder name
    name = folder_name
    
    # Remove date prefix
    if name.startswith("2025-"):
        parts = name.split("_", 1)
        if len(parts) > 1:
            name = parts[1]
    
    # Remove state suffix
    for suffix in ["_[P]", "_[M]", "_[C]"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    
    # Clean up concatenated emails
    # Pattern: word1word2word3_word1_word2 -> just take first unique part
    if "_" in name and "com" in name.lower():
        parts = name.split("_")
        # Take the first meaningful part or first few parts
        if len(parts) > 1:
            # Check if it's the email concat pattern
            first_part = parts[0]
            if len(first_part) > 50 and "com" in first_part.lower():
                # It's likely concatenated emails, try to extract names
                # Split on email domains
                cleaned = []
                current = ""
                for char in first_part:
                    current += char
                    if current.endswith("com") or current.endswith("ai") or current.endswith("org"):
                        # Extract name before @
                        name_part = current.rstrip("comaiorg")
                        if name_part:
                            cleaned.append(name_part.title())
                        current = ""
                if cleaned:
                    name = "_".join(cleaned[:2])  # Take first 2 names max
    
    # Replace underscores with spaces, title case
    name = name.replace("_", " ").strip()
    
    # Clean up common patterns
    name = name.replace("mycareerspancom", "").replace("theapplyai", "")
    name = name.replace("gmailcom", "").replace("  ", " ").strip()
    
    # Title case and limit length
    if name:
        name = " ".join(word.capitalize() for word in name.split())
    
    return name[:60] if name else "Unknown"

def flatten_nested_duplicates(meeting_dir: Path, dry_run: bool = True):
    """Move content from nested duplicate folders up to parent."""
    changes = []
    
    nested_dirs = [d for d in meeting_dir.iterdir() if d.is_dir() and d.name.startswith("2025-")]
    
    for nested in nested_dirs:
        # This is a duplicate nested folder
        for item in nested.iterdir():
            if item.is_file():
                target = meeting_dir / item.name
                if not target.exists():
                    changes.append(f"  MOVE: {item.name} → parent")
                    if not dry_run:
                        shutil.move(str(item), str(target))
        
        # Check if nested has its own nested
        deep_nested = [d for d in nested.iterdir() if d.is_dir() and d.name.startswith("2025-")]
        for dn in deep_nested:
            for item in dn.iterdir():
                if item.is_file():
                    target = meeting_dir / item.name
                    if not target.exists():
                        changes.append(f"  MOVE: {dn.name}/{item.name} → parent")
                        if not dry_run:
                            shutil.move(str(item), str(target))
        
        # Remove empty nested dirs
        if not dry_run:
            try:
                # Clean up nested dirs
                for dn in deep_nested:
                    if not list(dn.iterdir()):
                        dn.rmdir()
                if not list(nested.iterdir()):
                    nested.rmdir()
            except:
                pass
        else:
            changes.append(f"  DELETE: empty nested folder {nested.name}")
    
    return changes

def reorganize(dry_run: bool = True, include_inbox: bool = True, include_processed: bool = True):
    """Main reorganization function."""
    print(f"\n{'='*60}")
    print(f"MEETING REORGANIZATION {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    print(f"{'='*60}\n")
    
    all_meetings = []
    
    # Collect from Inbox
    if include_inbox:
        for item in INBOX.iterdir():
            if item.is_dir() and not item.name.startswith((".", "_")):
                all_meetings.append(("inbox", item))
    
    # Collect already-processed meetings from main folder
    if include_processed:
        for item in MEETINGS.iterdir():
            if item.is_dir() and item.name.startswith("2025-") and "_[P]" in item.name:
                all_meetings.append(("processed", item))
    
    print(f"Found {len(all_meetings)} meetings to process\n")
    
    # Group by week
    by_week = defaultdict(list)
    for source, meeting_dir in all_meetings:
        date_str = meeting_dir.name[:10]
        week = get_week_folder_name(date_str)
        by_week[week].append((source, meeting_dir))
    
    total_changes = []
    
    for week in sorted(by_week.keys()):
        week_dir = MEETINGS / week
        print(f"\n--- {week} ({len(by_week[week])} meetings) ---")
        
        if not dry_run:
            week_dir.mkdir(exist_ok=True)
        else:
            print(f"  CREATE FOLDER: {week}")
        
        for source, meeting_dir in by_week[week]:
            date_str = meeting_dir.name[:10]
            manifest_path = meeting_dir / "manifest.json"
            
            # Get clean name
            clean_name = extract_readable_name(meeting_dir.name, manifest_path)
            
            # New folder name: DATE_CleanName (no [P] suffix)
            new_name = f"{date_str}_{clean_name.replace(' ', '-')}"
            new_path = week_dir / new_name
            
            print(f"\n  {meeting_dir.name}")
            print(f"    → {week}/{new_name}")
            
            # First flatten any nested duplicates
            if source == "inbox":
                nested_changes = flatten_nested_duplicates(meeting_dir, dry_run)
                if nested_changes:
                    print(f"    Nested fixes:")
                    for c in nested_changes:
                        print(f"      {c}")
            
            # Move to weekly folder
            if not dry_run:
                if new_path.exists():
                    # Merge instead
                    for item in meeting_dir.iterdir():
                        target = new_path / item.name
                        if not target.exists():
                            shutil.move(str(item), str(target))
                    try:
                        meeting_dir.rmdir()
                    except:
                        pass
                else:
                    shutil.move(str(meeting_dir), str(new_path))
            
            total_changes.append({
                "from": str(meeting_dir),
                "to": str(new_path),
                "week": week
            })
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(total_changes)} meetings organized into {len(by_week)} weekly folders")
    print(f"{'='*60}")
    
    return total_changes

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reorganize meetings into weekly folders")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Preview changes without executing (default)")
    parser.add_argument("--execute", action="store_true",
                        help="Actually perform the reorganization")
    parser.add_argument("--inbox-only", action="store_true",
                        help="Only process Inbox, not already-processed meetings")
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    include_processed = not args.inbox_only
    
    reorganize(dry_run=dry_run, include_inbox=True, include_processed=include_processed)

