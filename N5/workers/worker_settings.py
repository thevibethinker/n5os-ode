#!/usr/bin/env python3
"""
Worker: worker_settings
Task: Create system settings configuration
"""

import json
from pathlib import Path

SETTINGS_PATH = Path("/home/workspace/Personal/Content-Library/settings.json")

def create_settings():
    """Create system settings configuration"""
    
    # Ensure directory exists
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    settings = {
        "project": "Content Library v1.0",
        "created_at": "2025-11-11T19:20:00Z",
        "id_format": "{type}_{YYYYMMDD}_{random_4}",
        
        # File paths (existing folder structure)
        "file_paths": {
            "meetings": "~/Personal/Meetings/",
            "articles": "~/Articles/",
            "articles_web": "~/Articles/web/",
            "notes": "~/Personal/Notes/",
            "media": "~/media/",
            "downloads_content": "~/downloads/Content/"
        },
        
        # Entry types
        "entry_types": [
            "raw_material",
            "block",
            "article",
            "article_web",
            "email",
            "note",
            "media"
        ],
        
        # Block codes (from existing B-block system)
        "block_codes": [
            "B01", "B02", "B08", "B21", "B25", "B26", "B31"
        ],
        
        # Ingestion rules
        "ingestion_rules": {
            "local_files": "store_pointer_only",
            "remote_content": "download_then_pointer",
            "default_confidence": 3,
            "require_topics": False,
            "require_tags": False
        },
        
        # Promotion rules
        "promotion_rules": {
            "minimum_confidence": 3,
            "confirmation_required": True,
            "append_only": True
        },
        
        # Download locations for remote content
        "download_mapping": {
            "article": "~/Articles/web/",
            "article_web": "~/Articles/web/",
            "media": "~/media/",
            "default": "~/downloads/Content/"
        }
    }
    
    # Write settings file
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)
    
    print(f"✅ Settings created: {SETTINGS_PATH}")
    return SETTINGS_PATH

if __name__ == "__main__":
    settings_file = create_settings()
    print(f"\nOutput: {settings_file}")

