#!/usr/bin/env python3
"""
Generate Manifest for Meeting Folder

Creates manifest.json in a meeting folder based on its contents.
This marks the folder as ready for the [M] → [P] transition.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import re

def extract_date_from_folder_name(folder_name: str) -> str:
    """Extract date from folder name (YYYY-MM-DD format)."""
    match = re.match(r'(\d{4}-\d{2}-\d{2})', folder_name)
    if match:
        return match.group(1)
    return ""

def extract_title_from_folder_name(folder_name: str) -> str:
    """Extract title from folder name (part after date)."""
    # Remove date prefix
    name = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', folder_name)
    # Replace underscores with spaces, remove any state markers
    name = name.replace('_', ' ').strip()
    return name

def count_files_by_type(folder: Path) -> dict:
    """Count files by type in the meeting folder."""
    counts = {
        "md_files": 0,
        "txt_files": 0,
        "transcript_files": 0,
        "audio_files": 0,
        "video_files": 0,
        "total_files": 0
    }
    
    if not folder.exists():
        return counts
    
    for file in folder.iterdir():
        if file.is_file():
            counts["total_files"] += 1
            if file.suffix == '.md':
                counts["md_files"] += 1
            elif file.suffix == '.txt':
                counts["txt_files"] += 1
            elif file.suffix == '.jsonl' and 'transcript' in file.name:
                counts["transcript_files"] += 1
            elif file.suffix in ['.mp3', '.wav', '.m4a', '.ogg']:
                counts["audio_files"] += 1
            elif file.suffix in ['.mp4', '.mov', '.avi', '.mkv']:
                counts["video_files"] += 1
    
    return counts

def generate_manifest(meeting_folder: str) -> bool:
    """Generate manifest.json for a meeting folder."""
    folder = Path(meeting_folder)
    
    if not folder.exists():
        print(f"❌ Folder not found: {meeting_folder}")
        return False
    
    if not folder.is_dir():
        print(f"❌ Not a directory: {meeting_folder}")
        return False
    
    manifest_path = folder / "manifest.json"
    
    # Extract metadata from folder name and contents
    folder_name = folder.name
    meeting_date = extract_date_from_folder_name(folder_name)
    meeting_title = extract_title_from_folder_name(folder_name)
    file_counts = count_files_by_type(folder)
    
    # Check for README
    readme_exists = (folder / "README.md").exists()
    
    # Build manifest
    manifest = {
        "manifest_version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "meeting_folder": folder.name,
        "meeting_date": meeting_date,
        "meeting_title": meeting_title,
        "status": "manifest_generated",
        "file_counts": file_counts,
        "has_readme": readme_exists,
        "blocks_generated": {
            "stakeholder_intelligence": file_counts["md_files"] > 1,
            "brief": readme_exists or file_counts["md_files"] > 0,
            "transcript_processed": file_counts["transcript_files"] > 0
        }
    }
    
    # Write manifest
    try:
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"✓ Manifest generated: {manifest_path}")
        return True
    except Exception as e:
        print(f"❌ Error writing manifest: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate manifest.json for meeting folder")
    parser.add_argument("--meeting-dir", required=True, help="Path to meeting folder")
    args = parser.parse_args()
    
    success = generate_manifest(args.meeting_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
