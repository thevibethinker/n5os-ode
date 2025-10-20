#!/usr/bin/env python3
"""
N5 Lists Reorder Migration: Reorders all list items to reverse chronological order (newest first).
This one-time migration ensures existing lists conform to the new ordering standard.
"""

import json, sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

def read_jsonl(p: Path) -> List[Dict[str, Any]]:
    """Read JSONL file and return list of items."""
    items = []
    if not p.exists():
        return items
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            ln = line.strip()
            if not ln:
                continue
            try:
                items.append(json.loads(ln))
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {i} of {p}: {e}", file=sys.stderr)
    return items

def write_jsonl(p: Path, items: List[Dict[str, Any]]):
    """Write items to JSONL file with atomic replacement."""
    p.parent.mkdir(parents=True, exist_ok=True)
    temp_file = p.with_suffix('.tmp')
    try:
        with temp_file.open("w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, separators=(',', ':')) + '\n')
        temp_file.replace(p)  # Atomic move
    except Exception as e:
        if temp_file.exists():
            temp_file.unlink()
        raise SystemExit(f"Failed to write {p}: {e}")

def get_sort_key(item: Dict[str, Any]) -> str:
    """Get sort key from item, using created_at and falling back to other timestamp fields."""
    # First try created_at
    if "created_at" in item:
        return item["created_at"]
    
    # If no created_at, try updated_at as approximation
    if "updated_at" in item:
        return item["updated_at"]
    
    # If neither exists, we should probably warn and fall back to current time
    print(f"Warning: Item {item.get('id', 'unknown')} has no timestamp fields", file=sys.stderr)
    return datetime.now(timezone.utc).isoformat()

def reorder_list(jsonl_path: Path) -> bool:
    """Reorder a single list file in reverse chronological order."""
    try:
        items = read_jsonl(jsonl_path)
        if not items:
            return False
        
        print(f"Processing {jsonl_path.name}: {len(items)} items")
        
        # Sort by created_at in reverse order (newest first)
        sorted_items = sorted(items, key=get_sort_key, reverse=True)
        
        # Check if order actually changed
        if items == sorted_items:
            print(f"  ✓ Already in reverse chronological order")
            return False
        
        # Write reordered items
        backup_path = jsonl_path.with_suffix('.jsonl.backup')
        jsonl_path.rename(backup_path)  # Create backup
        
        write_jsonl(jsonl_path, sorted_items)
        
        print(f"  ✓ Reordered successfully (oldest item: {sorted_items[-1].get('created_at', 'unknown')})")
        print(f"  ✓ Backup created: {backup_path.name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {jsonl_path.name}: {e}", file=sys.stderr)
        return False

def main():
    print("N5 Lists Reorder Migration - Reverse Chronological Order")
    print("=" * 60)
    
    ROOT = Path(__file__).resolve().parents[1]
    LISTS_DIR = ROOT / "lists"
    INDEX_FILE = LISTS_DIR / "index.jsonl"
    
    if not LISTS_DIR.exists():
        print(f"Error: Lists directory not found: {LISTS_DIR}")
        return 1
    
    if not INDEX_FILE.exists():
        print(f"Error: Index file not found: {INDEX_FILE}")
        return 1
    
    # Read registry to get active lists
    registry_items = []
    with INDEX_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    registry_items.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON in registry: {e}", file=sys.stderr)
    
    migrated_lists = []
    skipped_lists = []
    errors = []
    
    print(f"Found {len(registry_items)} lists in registry")
    
    for registry_item in registry_items:
        slug = registry_item.get('slug')
        if not slug:
            continue
            
        jsonl_path = LISTS_DIR / f"{slug}.jsonl"
        if not jsonl_path.exists():
            print(f"Warning: List file not found for '{slug}': {jsonl_path}")
            continue
        
        try:
            migrated = reorder_list(jsonl_path)
            if migrated:
                migrated_lists.append(slug)
            else:
                skipped_lists.append(slug)
        except Exception as e:
            errors.append((slug, str(e)))
            print(f"  ✗ Failed to process '{slug}': {e}", file=sys.stderr)
    
    print("\nMigration Summary:")
    print("=" * 30)
    print(f"✓ Successfully migrated: {len(migrated_lists)} lists")
    print(f"✓ Already ordered correctly: {len(skipped_lists)} lists")
    for slug in migrated_lists:
        print(f"  - {slug} (reordered)")
    
    if errors:
        print(f"\n✗ Errors encountered: {len(errors)} lists")
        for slug, error in errors:
            print(f"  - {slug}: {error}")
        return 1
    
    print(f"\n✓ Migration completed successfully!")
    print("  All lists now in reverse chronological order (newest items first)")
    print(f"  Backups created for all modified files with .jsonl.backup extension")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())