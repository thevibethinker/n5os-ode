import os
import json
import datetime
import shutil
from pathlib import Path
import re

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
QUARANTINE = INBOX / "_quarantine"
ARCHIVE_ROOT = Path("/home/workspace/Personal/Meetings")

def get_current_iso():
    return datetime.datetime.now().isoformat()

def get_meeting_date(folder_name):
    match = re.search(r"(\d{4}-\d{2}-\d{2})", folder_name)
    if match:
        return match.group(1)
    return datetime.date.today().isoformat()

def is_duplicate(folder_name):
    base_name = folder_name.lower()
    for week_folder in ARCHIVE_ROOT.glob("Week-of-*"):
        for existing in week_folder.iterdir():
            if existing.is_dir():
                existing_base = existing.name.lower()
                existing_base = existing_base.replace("_[m]", "").replace("_[p]", "").replace("_[c]", "")
                if base_name == existing_base:
                    return week_folder.name
    return None

def merge_folders(src, dst):
    print(f"  Merging {src.name} into {dst.name}")
    for item in src.iterdir():
        target = dst / item.name
        if target.exists():
            print(f"    Skipping existing {item.name}")
            continue
        shutil.move(str(item), str(target))
    
    # Try to clean up empty dirs
    try:
        shutil.rmtree(src)
        print(f"  Cleaned up {src.name}")
    except Exception as e:
        print(f"  Warning: Could not fully clean up {src.name}: {e}")

def process_folder(folder_path):
    folder_name = folder_path.name
    print(f"Processing: {folder_name}")

    jsonl_path = folder_path / "transcript.jsonl"
    md_path = folder_path / "transcript.md"
    txt_path = folder_path / "transcript.txt"

    if not jsonl_path.exists():
        if md_path.exists():
            content = md_path.read_text()
            with open(jsonl_path, "w") as f:
                json.dump({"text": content}, f)
            print(f"  Converted transcript.md to transcript.jsonl")
        elif txt_path.exists():
            content = txt_path.read_text()
            with open(jsonl_path, "w") as f:
                json.dump({"text": content}, f)
            print(f"  Converted transcript.txt to transcript.jsonl")
        else:
            print(f"  Warning: No transcript found. Moving to quarantine.")
            if not QUARANTINE.exists(): QUARANTINE.mkdir()
            shutil.move(str(folder_path), str(QUARANTINE / folder_name))
            return

    week_folder = is_duplicate(folder_name)
    if week_folder:
        print(f"  Duplicate found in {week_folder}. Moving to quarantine.")
        if not QUARANTINE.exists(): QUARANTINE.mkdir()
        shutil.move(str(folder_path), str(QUARANTINE / f"{folder_name}_duplicate_already_archived"))
        return

    manifest = {
        "manifest_version": "1.0",
        "generated_at": get_current_iso(),
        "meeting_folder": folder_name,
        "meeting_date": get_meeting_date(folder_name),
        "status": "manifest_generated",
        "blocks_generated": {
            "stakeholder_intelligence": False,
            "brief": False,
            "transcript_processed": True
        },
        "last_updated_by": "MG-1_Agent"
    }
    with open(folder_path / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Generated manifest.json")

    target_name = f"{folder_name}_[M]"
    target_path = INBOX / target_name
    
    if target_path.exists():
        merge_folders(folder_path, target_path)
    else:
        shutil.move(str(folder_path), str(target_path))
        print(f"  Transitioned to [M] state: {target_name}")

def main():
    if not INBOX.exists():
        print(f"Inbox {INBOX} not found.")
        return
        
    folders = [f for f in INBOX.iterdir() if f.is_dir() 
               and not f.name.endswith("_[M]") 
               and not f.name.endswith("_[P]") 
               and f.name != "_quarantine"]
    
    if not folders:
        print("No unprocessed folders found.")
        return

    for folder in folders:
        process_folder(folder)

if __name__ == "__main__":
    main()
