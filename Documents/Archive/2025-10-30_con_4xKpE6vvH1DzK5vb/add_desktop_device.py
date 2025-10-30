#!/usr/bin/env python3
import json
import subprocess
import sys

API_KEY = "kEpNfMKK4HcLmx7XqPWrt6WZCjuKtVRu"
BASE_URL = "http://localhost:8384"

# Desktop device info from screenshot
DESKTOP_DEVICE_ID = "W7OPWZL-RWJER6R-FM5EYDI-SVE5HGK-PD7LV6B-WTKVG2G-6OLRH4R-5QIRAQI"
DESKTOP_NAME = "Vrijens-MacBook-Pro"

# Folder IDs to share
FOLDER_IDS = [
    "personal-meetings",
    "knowledge",
    "company-records",
    "lists",
    "documents",
    "careerspan-meetings",
    "reflections",
    "articles"
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
    return result.returncode == 0

def add_device_and_share():
    config = get_config()
    
    # Check if device already exists
    existing_device = None
    for device in config.get("devices", []):
        if device["deviceID"] == DESKTOP_DEVICE_ID:
            existing_device = device
            break
    
    # Add device if it doesn't exist
    if not existing_device:
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
        print(f"✓ Added device: {DESKTOP_NAME}")
    else:
        print(f"✓ Device already exists: {DESKTOP_NAME}")
    
    # Share all folders with the desktop
    shared_count = 0
    for folder in config.get("folders", []):
        if folder["id"] in FOLDER_IDS:
            # Check if desktop is already in the devices list
            device_exists = False
            for device in folder.get("devices", []):
                if device["deviceID"] == DESKTOP_DEVICE_ID:
                    device_exists = True
                    break
            
            if not device_exists:
                folder["devices"].append({
                    "deviceID": DESKTOP_DEVICE_ID,
                    "introducedBy": "",
                    "encryptionPassword": ""
                })
                shared_count += 1
    
    # Save config
    if set_config(config):
        print(f"✓ Shared {shared_count} folders with your desktop")
        print("\nFolders shared:")
        for folder in config.get("folders", []):
            if folder["id"] in FOLDER_IDS:
                print(f"  - {folder['label']}")
        return True
    else:
        print("✗ Failed to update config")
        return False

if __name__ == "__main__":
    try:
        success = add_device_and_share()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
