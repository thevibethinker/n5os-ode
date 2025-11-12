#!/usr/bin/env python3
"""
Rename meeting folder to standardized format: YYYY-MM-DD_lead-participant_context_subtype

ATOMIC & REVERSIBLE:
- Creates rename log before any changes
- Checks for collisions
- Validates new name
- Can rollback using log file
"""

import re
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))
from infer_meeting_taxonomy import infer_from_folder

def extract_meeting_date(folder_name: str, b26_content: str = "") -> str:
    """Extract date from folder name, B26, or use today."""
    # Try folder name first
    if match := re.search(r'(20\d{2}-\d{2}-\d{2})', folder_name):
        return match.group(1)
    
    # Try transcript ID in folder name
    if match := re.search(r'transcript-(20\d{2})-(0\d|1[0-2])-(0\d|[12]\d|3[01])', folder_name):
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    
    # Try B26 content
    if b26_content:
        if match := re.search(r'\*\*Date:\*\*\s+(20\d{2})-(0\d|1[0-2])-(0\d|[12]\d|3[01])', b26_content):
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    
    # Fall back to today
    return datetime.now().strftime("%Y-%m-%d")

def extract_lead_participant(b26_content: str, folder_name: str) -> str:
    """Extract lead participant/org from B26 Primary classification."""
    
    # Parse Primary classification
    if match := re.search(r'\*?\*?Primary:\*?\*?\s+(.+?)(?:\n|$)', b26_content):
        primary = match.group(1).strip()
        
        # Extract org/person name from Primary (before parentheses or dash)
        if org_match := re.match(r'([^\(]+)', primary):
            name = org_match.group(1).strip()
            # Clean and slugify
            name = name.lower()
            name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars
            name = re.sub(r'[-\s]+', '-', name)    # Normalize spaces/hyphens
            name = name.strip('-')
            return name[:30]  # Max 30 chars
    
    # Fallback: extract from folder name
    folder_clean = re.sub(r'-transcript-.*', '', folder_name)
    folder_clean = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', folder_clean)
    if folder_clean:
        return folder_clean[:30]
    
    return "unknown"

def extract_context(b26_content: str, meeting_subtype: str) -> str:
    """Extract brief context from B26 or use sensible fallback."""
    
    # Try to extract from Secondary classification
    if match := re.search(r'\*?\*?Secondary:\*?\*?\s+(.+?)(?:\n|$)', b26_content):
        secondary = match.group(1).strip()
        if secondary and secondary.lower() != "n/a":
            # Slugify secondary
            context = secondary.lower()
            context = re.sub(r'[^\w\s-]', '', context)
            context = re.sub(r'[-\s]+', '-', context)
            context = context.strip('-')
            context = context[:20]  # Max 20 chars
            # Don't return if it's same as subtype
            if context != meeting_subtype and context:
                return context
    
    # Try first key theme
    if themes_match := re.search(r'##+ Key Themes\s+.*?1\.\s+\*\*([^*]+)\*\*', b26_content, re.DOTALL):
        theme = themes_match.group(1).strip().lower()
        theme = re.sub(r'[^\w\s-]', '', theme)
        theme = re.sub(r'[-\s]+', '-', theme)
        theme = theme.strip('-')[:20]
        if theme and theme != meeting_subtype:
            return theme
    
    # Fallback to "meeting" (generic but never duplicates subtype)
    return "meeting"

def generate_new_name(folder_path: Path, meeting_type: str, meeting_subtype: str) -> str:
    """Generate standardized folder name."""
    
    b26_file = folder_path / "B26_metadata.md"
    b26_content = b26_file.read_text() if b26_file.exists() else ""
    
    date = extract_meeting_date(folder_path.name, b26_content)
    participant = extract_lead_participant(b26_content, folder_path.name)
    context = extract_context(b26_content, meeting_subtype)
    
    # Format: YYYY-MM-DD_participant_context_subtype
    new_name = f"{date}_{participant}_{context}_{meeting_subtype}"
    
    # Clean any double underscores or hyphens
    new_name = re.sub(r'__+', '_', new_name)
    new_name = re.sub(r'--+', '-', new_name)
    
    return new_name

def check_collision(parent_dir: Path, new_name: str) -> bool:
    """Check if new name already exists."""
    return (parent_dir / new_name).exists()

def rename_folder(folder_path: Path, new_name: str, log_file: Path) -> bool:
    """Perform atomic rename and log it."""
    
    parent = folder_path.parent
    new_path = parent / new_name
    
    if check_collision(parent, new_name):
        print(f"❌ Collision: {new_name} already exists")
        return False
    
    # Log the rename BEFORE doing it
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "old_path": str(folder_path),
        "new_path": str(new_path),
        "old_name": folder_path.name,
        "new_name": new_name
    }
    
    # Append to log
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    # Perform rename
    folder_path.rename(new_path)
    
    return True

def process_folder(folder_path: Path, log_file: Path, dry_run: bool = False) -> dict:
    """Process a single meeting folder."""
    
    # Infer taxonomy
    taxonomy = infer_from_folder(folder_path)
    if not taxonomy:
        return {"success": False, "reason": "no_b26_or_old_format"}
    
    meeting_type, meeting_subtype = taxonomy
    
    # Generate new name
    new_name = generate_new_name(folder_path, meeting_type, meeting_subtype)
    
    # Check if already correct
    if folder_path.name == new_name:
        return {"success": True, "action": "skip", "reason": "already_correct"}
    
    print(f"\n📁 {folder_path.name}")
    print(f"   → {new_name}")
    print(f"   ({meeting_type}/{meeting_subtype})")
    
    if dry_run:
        print("   [DRY RUN - No changes made]")
        return {"success": True, "dry_run": True, "new_name": new_name}
    
    # Check collision
    if check_collision(folder_path.parent, new_name):
        print("   ❌ Collision - folder exists")
        return {"success": False, "reason": "collision", "new_name": new_name}
    
    # Perform rename
    if rename_folder(folder_path, new_name, log_file):
        print("   ✅ Renamed")
        return {"success": True, "action": "renamed", "new_name": new_name}
    else:
        return {"success": False, "reason": "rename_failed"}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Rename meeting folder to standardized format")
    parser.add_argument("folder", type=Path, help="Meeting folder to rename")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--log-file", type=Path, default=Path("/home/workspace/Personal/Meetings/rename_log.jsonl"),
                       help="Path to rename log file")
    
    args = parser.parse_args()
    
    if not args.folder.is_dir():
        print(f"ERROR: {args.folder} is not a directory")
        sys.exit(1)
    
    result = process_folder(args.folder, args.log_file, dry_run=args.dry_run)
    
    if result["success"]:
        print("\n✅ Complete")
    else:
        print(f"\n❌ Failed: {result.get('reason', 'unknown')}")
        sys.exit(1)
