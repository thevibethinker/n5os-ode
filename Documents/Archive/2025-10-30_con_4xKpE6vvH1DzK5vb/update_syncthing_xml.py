#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import sys

CONFIG_FILE = "/home/workspace/.config/syncthing/config.xml"
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

def create_folder_element(folder_def):
    folder = ET.Element("folder", {
        "id": folder_def["id"],
        "label": folder_def["label"],
        "path": folder_def["path"],
        "type": "sendreceive",
        "rescanIntervalS": "3600",
        "fsWatcherEnabled": "true",
        "fsWatcherDelayS": "10",
        "ignorePerms": "false",
        "autoNormalize": "true"
    })
    
    # Add filesystemType
    fs_type = ET.SubElement(folder, "filesystemType")
    fs_type.text = "basic"
    
    # Add devices
    for dev_id in [ZO_DEVICE_ID, DESKTOP_DEVICE_ID]:
        device = ET.SubElement(folder, "device", {"id": dev_id, "introducedBy": ""})
        enc_pass = ET.SubElement(device, "encryptionPassword")
        enc_pass.text = ""
    
    # Add minDiskFree
    min_disk = ET.SubElement(folder, "minDiskFree", {"unit": "%"})
    min_disk.text = "1"
    
    # Add versioning
    versioning = ET.SubElement(folder, "versioning", {"type": "simple"})
    param = ET.SubElement(versioning, "param", {"key": "keep", "val": "5"})
    cleanup = ET.SubElement(versioning, "cleanupIntervalS")
    cleanup.text = "3600"
    
    # Add paused
    paused = ET.SubElement(folder, "paused")
    paused.text = "false"
    
    # Add markerName
    marker = ET.SubElement(folder, "markerName")
    marker.text = ".stfolder"
    
    return folder

def update_config():
    try:
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()
        
        # Remove old meetings-sync folder
        for folder in root.findall("folder"):
            if folder.get("id") == "meetings-sync":
                root.remove(folder)
                print("✓ Removed old meetings-sync folder")
        
        # Add new folders
        existing_ids = {f.get("id") for f in root.findall("folder")}
        added = []
        
        for folder_def in FOLDERS:
            if folder_def["id"] not in existing_ids:
                folder_elem = create_folder_element(folder_def)
                # Insert before first device element
                device_idx = None
                for i, elem in enumerate(root):
                    if elem.tag == "device":
                        device_idx = i
                        break
                if device_idx is not None:
                    root.insert(device_idx, folder_elem)
                else:
                    root.append(folder_elem)
                added.append(folder_def["label"])
        
        # Check if desktop device exists
        desktop_exists = False
        for device in root.findall("device"):
            if device.get("id") == DESKTOP_DEVICE_ID:
                desktop_exists = True
                break
        
        # Add desktop device if it doesn't exist
        if not desktop_exists:
            device = ET.Element("device", {
                "id": DESKTOP_DEVICE_ID,
                "name": DESKTOP_NAME,
                "compression": "metadata",
                "introducer": "false",
                "skipIntroductionRemovals": "false",
                "introducedBy": ""
            })
            address = ET.SubElement(device, "address")
            address.text = "dynamic"
            paused = ET.SubElement(device, "paused")
            paused.text = "false"
            auto_accept = ET.SubElement(device, "autoAcceptFolders")
            auto_accept.text = "false"
            
            root.append(device)
            print(f"✓ Added desktop device: {DESKTOP_NAME}")
        else:
            print(f"✓ Desktop device already exists")
        
        # Save the config
        tree.write(CONFIG_FILE, encoding="UTF-8", xml_declaration=True)
        
        print(f"\n✓ Added {len(added)} folders:")
        for label in added:
            print(f"  - {label}")
        
        print(f"\nSyncthing will auto-restart and share these folders with your desktop!")
        return True
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_config()
    sys.exit(0 if success else 1)
