#!/usr/bin/env python3
import json
import subprocess
import sys

API_KEY = "kEpNfMKK4HcLmx7XqPWrt6WZCjuKtVRu"
BASE_URL = "http://localhost:8384"

# Comprehensive list of folders to sync
FOLDERS = [
    {
        "id": "personal-meetings",
        "label": "Personal Meetings",
        "path": "/home/workspace/Personal/Meetings",
        "description": "Meeting records, transcripts, and intelligence"
    },
    {
        "id": "knowledge",
        "label": "Knowledge Base",
        "path": "/home/workspace/Knowledge",
        "description": "Architectural docs, market intelligence, infrastructure guides"
    },
    {
        "id": "records-company",
        "label": "Company Records",
        "path": "/home/workspace/Records/Company",
        "description": "Company documents, proposals, emails, technology notes"
    },
    {
        "id": "lists",
        "label": "Lists & Tracking",
        "path": "/home/workspace/Lists",
        "description": "Action items, services, task tracking"
    },
    {
        "id": "documents",
        "label": "Documents",
        "path": "/home/workspace/Documents",
        "description": "Key documents including N5.md"
    },
    {
        "id": "careerspan-meetings",
        "label": "Careerspan Meetings",
        "path": "/home/workspace/Careerspan/Meetings",
        "description": "Careerspan-specific meeting records"
    },
    {
        "id": "records-reflections",
        "label": "Reflections",
        "path": "/home/workspace/Records/Reflections",
        "description": "Personal reflections and insights"
    },
    {
        "id": "articles",
        "label": "Articles",
        "path": "/home/workspace/Articles",
        "description": "Saved articles and research"
    }
]

def get_config():
    result = subprocess.run(
        ["curl", "-s", "-H", f"X-API-Key: {API_KEY}", f"{BASE_URL}/rest/system/config"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def put_config(config):
    config_json = json.dumps(config)
    result = subprocess.run(
        ["curl", "-s", "-X", "PUT", "-H", f"X-API-Key: {API_KEY}",
         "-H", "Content-Type: application/json",
         "-d", config_json,
         f"{BASE_URL}/rest/system/config"],
        capture_output=True, text=True
    )
    return result

def folder_exists(config, folder_id):
    return any(f["id"] == folder_id for f in config.get("folders", []))

def add_folders():
    config = get_config()
    device_id = config["devices"][0]["deviceID"]
    
    added = []
    skipped = []
    
    for folder in FOLDERS:
        if folder_exists(config, folder["id"]):
            skipped.append(folder["label"])
            continue
        
        new_folder = {
            "id": folder["id"],
            "label": folder["label"],
            "filesystemType": "basic",
            "path": folder["path"],
            "type": "sendreceive",
            "devices": [{"deviceID": device_id, "introducedBy": "", "encryptionPassword": ""}],
            "rescanIntervalS": 3600,
            "fsWatcherEnabled": True,
            "fsWatcherDelayS": 10,
            "ignorePerms": False,
            "autoNormalize": True,
            "minDiskFree": {"value": 1, "unit": "%"},
            "versioning": {
                "type": "simple",
                "params": {"keep": "5"},
                "cleanupIntervalS": 3600
            },
            "paused": False,
            "markerName": ".stfolder"
        }
        
        config["folders"].append(new_folder)
        added.append(folder["label"])
    
    if added:
        put_config(config)
        print(f"✓ Added {len(added)} folders:")
        for label in added:
            print(f"  - {label}")
    
    if skipped:
        print(f"\n⊘ Skipped {len(skipped)} existing folders:")
        for label in skipped:
            print(f"  - {label}")
    
    return len(added)

if __name__ == "__main__":
    try:
        count = add_folders()
        sys.exit(0 if count >= 0 else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
