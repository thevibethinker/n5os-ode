import os
import json
import shutil
from datetime import datetime

INBOX_DIR = "/home/workspace/Personal/Meetings/Inbox"
QUARANTINE_DIR = os.path.join(INBOX_DIR, "_quarantine")
MEETINGS_ROOT = "/home/workspace/Personal/Meetings"

def get_iso_timestamp():
    return datetime.now().isoformat()

def process_meetings():
    if not os.path.exists(INBOX_DIR):
        print(f"Inbox directory {INBOX_DIR} not found.")
        return

    # Scan for unprocessed folders
    folders = [f for f in os.listdir(INBOX_DIR) 
               if os.path.isdir(os.path.join(INBOX_DIR, f)) 
               and not f.endswith("_[M]") 
               and not f.endswith("_[P]") 
               and f != "_quarantine"]

    if not folders:
        print("No unprocessed meeting folders found in Inbox.")
        return

    for folder_name in folders:
        folder_path = os.path.join(INBOX_DIR, folder_name)
        print(f"Processing: {folder_name}")

        # 1. Validation & Conversion
        transcript_jsonl = os.path.join(folder_path, "transcript.jsonl")
        if not os.path.exists(transcript_jsonl):
            found_transcript = False
            for ext in ["md", "txt"]:
                trans_path = os.path.join(folder_path, f"transcript.{ext}")
                if os.path.exists(trans_path):
                    print(f"  Converting transcript.{ext} to transcript.jsonl")
                    with open(trans_path, 'r') as f:
                        content = f.read()
                    with open(transcript_jsonl, 'w') as f:
                        json.dump({"text": content}, f)
                    found_transcript = True
                    break
            
            if not found_transcript:
                print(f"  Warning: No transcript found in {folder_name}. Moving to quarantine.")
                os.makedirs(QUARANTINE_DIR, exist_ok=True)
                shutil.move(folder_path, os.path.join(QUARANTINE_DIR, folder_name))
                continue

        # 2. Global Duplicate Check
        is_duplicate = False
        target_normalized = folder_name.lower().replace("gmailcom", "").strip("_ ")
        
        # Check all Week-of folders
        for item in os.listdir(MEETINGS_ROOT):
            if item.startswith("Week-of-"):
                week_path = os.path.join(MEETINGS_ROOT, item)
                if os.path.isdir(week_path):
                    for existing in os.listdir(week_path):
                        existing_normalized = existing.lower().replace("_[m]", "").replace("_[p]", "").replace("gmailcom", "").strip("_ ")
                        if target_normalized == existing_normalized:
                            print(f"  Meeting already exists in {item}. Moving to quarantine.")
                            os.makedirs(QUARANTINE_DIR, exist_ok=True)
                            shutil.move(folder_path, os.path.join(QUARANTINE_DIR, f"{folder_name}_duplicate_already_archived"))
                            is_duplicate = True
                            break
            if is_duplicate: break
        
        if is_duplicate: continue

        # 3. Generate Manifest
        manifest_path = os.path.join(folder_path, "manifest.json")
        meeting_date = folder_name.split("_")[0] if "_" in folder_name else datetime.now().strftime("%Y-%m-%d")
        
        manifest_data = {
            "manifest_version": "1.0",
            "generated_at": get_iso_timestamp(),
            "meeting_folder": folder_name,
            "meeting_date": meeting_date,
            "status": "manifest_generated",
            "blocks_generated": {
                "stakeholder_intelligence": False,
                "brief": False,
                "transcript_processed": True
            },
            "last_updated_by": "MG-1_Prompt"
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        print(f"  Generated manifest.json")

        # 4. Transition to [M] State
        new_folder_name = f"{folder_name}_[M]"
        new_folder_path = os.path.join(INBOX_DIR, new_folder_name)
        
        if os.path.exists(new_folder_path):
            print(f"  Warning: {new_folder_name} already exists. Skipping move.")
        else:
            shutil.move(folder_path, new_folder_path)
            print(f"  Renamed to {new_folder_name}")

if __name__ == "__main__":
    process_meetings()
