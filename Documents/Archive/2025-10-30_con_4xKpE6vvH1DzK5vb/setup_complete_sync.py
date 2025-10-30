#!/usr/bin/env python3
import json
import subprocess
import sys
import time

API_KEY = "kEpNfMKK4HcLmx7XqPWrt6WZCjuKtVRu"
BASE_URL = "http://localhost:8384"
ZO_DEVICE_ID = "3CFWBF3-P4AVQKP-HTZQUPO-PI2POMG-LDJMSFI-XKFIMPY-BPP4PZZ-3472NAY"
DESKTOP_DEVICE_ID = "W7OPWZL-RWJER6R-FM5EYDI-SVE5HGK-PD7LV6B-WTKVG2G-6OLRH4R-5QIRAQI"
DESKTOP_NAME = "Vrijens-MacBook-Pro"

FOLDERS = [
    {"id": "personal-meetings", "label": "Personal Meetings", "path": "/home/workspace/Personal/Meetings"},
    {"id": "knowledge", "label": "Knowledge Base", "path": "/home/workspace/Knowledge"},
    {"id": "company-records", "label": "Company Records", "path": "/home/workspace/Records/Company"},
    {"id": "lists", "label": "Lists & Tracking", "path": "/home/workspace/Lists"},
    {"id": "documents", "label": "Documents", "path": "/home/workspace/Documents"},
    {"id": "careerspan-meetings", "label": "Careerspan Meetings", "path": "/home/workspace/Careerspan/Meetings"},
    {"id": "reflections", "label": "Reflections", "path": "/home/workspace/Records/Reflections"},
    {"id": "articles", "label": "Articles", "path": "/home/workspace/Articles"},
]

def get_config():
    result = subprocess.run(
        ["curl", "-s", "-H", f"X-API-Key: {API_KEY}", f"{BASE_URL}/rest/system/config"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def set_config(config):
    config_json = json.dumps(config)
    result = subprocess.run(
        ["curl", "-s", "-X", "PUT", "-H", f"X-API-Key: {API_KEY}",
         "-H", "Content-Type: application/json",
         "-d", config_json,
         f"{BASE_URL}/rest/system/config"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"curl failed: {result.stderr}")
        return False
    return True

def setup_complete_sync():
    config = get_config()
    
    # 1. Add desktop device if it doesn't exist
    desktop_exists = False
    for device in config.get("devices", []):
        if device["deviceID"] == DESKTOP_DEVICE_ID:
            desktop_exists = True
            print(f"✓ Desktop device already added: {DESKTOP_NAME}")
            break
    
    if not desktop_exists:
        new_device = {
            "deviceID": DESKTOP_DEVICE_ID,
            "name": DESKTOP_NAME,
            "addresses": ["dynamic"],
            "compression": "metadata",
            "certName": "",
            "introducer": False,
            "skipIntroductionRemovals": False,
            "introducedBy": "",
            "paused": False,
            "allowedNetworks": [],
            "autoAcceptFolders": False,
            "maxSendKbps": 0,
            "maxRecvKbps": 0,
            "ignoredFolders": [],
            "maxRequestKiB": 0,
            "untrusted": False,
            "remoteGUIPort": 0
        }
        config["devices"].append(new_device)
        print(f"✓ Added desktop device: {DESKTOP_NAME}")
    
    # 2. Add/update folders
    existing_folder_ids = {f["id"] for f in config.get("folders", [])}
    added_folders = []
    
    for folder_def in FOLDERS:
        if folder_def["id"] in existing_folder_ids:
            # Update existing folder to include both devices
            for folder in config["folders"]:
                if folder["id"] == folder_def["id"]:
                    device_ids = {d["deviceID"] for d in folder.get("devices", [])}
                    if DESKTOP_DEVICE_ID not in device_ids:
                        folder["devices"].append({
                            "deviceID": DESKTOP_DEVICE_ID,
                            "introducedBy": "",
                            "encryptionPassword": ""
                        })
                        added_folders.append(folder_def["label"])
            continue
        
        # Create new folder
        new_folder = {
            "id": folder_def["id"],
            "label": folder_def["label"],
            "filesystemType": "basic",
            "path": folder_def["path"],
            "type": "sendreceive",
            "devices": [
                {
                    "deviceID": ZO_DEVICE_ID,
                    "introducedBy": "",
                    "encryptionPassword": ""
                },
                {
                    "deviceID": DESKTOP_DEVICE_ID,
                    "introducedBy": "",
                    "encryptionPassword": ""
                }
            ],
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
        added_folders.append(folder_def["label"])
    
    # 3. Save configuration
    if set_config(config):
        print(f"\n✓ Configuration saved successfully!")
        print(f"✓ Added/shared {len(added_folders)} folders with desktop:\n")
        for label in added_folders:
            print(f"  - {label}")
        
        print(f"\n📱 On your desktop, you should now see notifications to accept these {len(added_folders)} folders!")
        return True
    else:
        print("✗ Failed to save configuration")
        return False

if __name__ == "__main__":
    try:
        success = setup_complete_sync()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
