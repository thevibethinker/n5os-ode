#!/usr/bin/env python3
"""
Migration script for SYSTEM_LEARNINGS.json to v2 schema.
Adds default values for new v2 fields to existing learnings.
Creates a backup before migration.
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

SYSTEM_LEARNINGS = Path("/home/workspace/N5/learnings/SYSTEM_LEARNINGS.json")
BACKUP_DIR = Path("/home/workspace/N5/learnings/backups")

def migrate_learnings():
    """Migrate existing learnings to v2 schema"""
    
    # Create backup directory if it doesn't exist
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create backup
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"SYSTEM_LEARNINGS_v1_{timestamp}.json"
    
    if SYSTEM_LEARNINGS.exists():
        shutil.copy2(SYSTEM_LEARNINGS, backup_path)
        print(f"Backup created: {backup_path}")
    
    # Load existing data
    with open(SYSTEM_LEARNINGS) as f:
        data = json.load(f)
    
    # Update meta version
    if "meta" in data:
        data["meta"]["version"] = "2.0"
        data["meta"]["migrated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Migrate each learning
    learnings = data.get("learnings", [])
    migrated_count = 0
    
    for learning in learnings:
        # Skip if already has v2 fields
        if "confidence" in learning:
            continue
        
        # Add v2 fields with defaults
        learning["confidence"] = 0.7
        learning["validated_count"] = 0
        learning["last_validated"] = None
        learning["decay_days"] = 30
        learning["expires_at"] = None
        learning["status"] = "active"
        learning["disputed_by"] = None
        learning["dispute_reason"] = None
        
        migrated_count += 1
    
    # Save migrated data
    with open(SYSTEM_LEARNINGS, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Migrated {migrated_count} learnings to v2 schema")
    print(f"Total learnings: {len(learnings)}")
    
    return migrated_count

if __name__ == "__main__":
    migrate_learnings()
