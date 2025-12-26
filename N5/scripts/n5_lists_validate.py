#!/usr/bin/env python3
"""
Lists Validation Script - Orphan Detection for Hybrid Storage

Validates list JSONL files to detect orphaned markdown files referenced
in the `links` field. Ensures SSOT integrity for hybrid storage.

Usage:
    python3 N5/scripts/n5_lists_validate.py [list_slug]
    python3 N5/scripts/n5_lists_validate.py --all
    python3 N5/scripts/n5/scripts/n5_lists_validate.py --fix
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Constants
WORKSPACE_ROOT = Path("/home/workspace")
LISTS_DIR = WORKSPACE_ROOT / "Lists"
INDEX_FILE = LISTS_DIR / "index.jsonl"

def read_jsonl(filepath: Path) -> list[dict]:
    """Read and return all records from a JSONL file."""
    if not filepath.exists():
        return []
    items = []
    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"⚠️  Warning: Invalid JSON in {filepath}: {e}")
    return items

def validate_list_links(list_slug: str, verbose: bool = True) -> dict:
    """
    Validate all links in a list's JSONL entries.
    Returns dict with 'orphans' (missing files) and 'valid' (found files).
    """
    jsonl_file = LISTS_DIR / f"{list_slug}.jsonl"
    registry = read_jsonl(INDEX_FILE)
    
    # Verify list exists in registry
    list_metadata = next((r for r in registry if r.get("slug") == list_slug), None)
    if not list_metadata:
        print(f"❌ List '{list_slug}' not found in registry")
        return {"orphans": [], "valid": [], "total": 0}
    
    items = read_jsonl(jsonl_file)
    results = {"orphans": [], "valid": [], "total": len(items)}
    
    for item in items:
        item_id = item.get("id", "unknown")
        title = item.get("title", "untitled")
        links = item.get("links", [])
        
        for link in links:
            if link.get("type") == "file":
                raw_path = link.get("value", "")
                # Resolve relative to workspace root if not absolute
                file_path = Path(raw_path)
                if not file_path.is_absolute():
                    file_path = WORKSPACE_ROOT / raw_path
                
                if not file_path.exists():
                    results["orphans"].append({
                        "item_id": item_id,
                        "title": title,
                        "missing_file": str(file_path)
                    })
                else:
                    results["valid"].append({
                        "item_id": item_id,
                        "title": title,
                        "file": str(file_path)
                    })
    
    if verbose:
        if results["orphans"]:
            print(f"\n❌ Orphaned files found in '{list_slug}':")
            for orphan in results["orphans"]:
                print(f"   • '{orphan['title']}' ({orphan['item_id']})")
                print(f"     Missing: {orphan['missing_file']}")
        else:
            print(f"✅ All links valid in '{list_slug}' ({results['total']} items)")
    
    return results

def validate_all_lists() -> dict:
    """Validate all lists that exist in the registry."""
    registry = read_jsonl(INDEX_FILE)
    all_results = {}
    
    print("🔍 Validating all lists...\n")
    for list_metadata in registry:
        slug = list_metadata.get("slug")
        if slug:
            print(f"\n📋 Checking: {slug}")
            all_results[slug] = validate_list_links(slug, verbose=False)
    
    # Summary
    total_orphans = sum(len(r["orphans"]) for r in all_results.values())
    total_valid = sum(len(r["valid"]) for r in all_results.values())
    
    print(f"\n{'='*50}")
    print(f"SUMMARY: {total_orphans} orphans, {total_valid} valid links")
    print(f"{'='*50}")
    
    if total_orphans > 0:
        print("\n🔴 Lists with orphaned files:")
        for slug, results in all_results.items():
            if results["orphans"]:
                print(f"   • {slug}: {len(results['orphans'])} orphan(s)")
    
    return all_results

def main():
    parser = argparse.ArgumentParser(
        description="Validate list JSONL files for orphaned markdown references"
    )
    parser.add_argument(
        "list_slug",
        nargs="?",
        help="List slug to validate (omit with --all)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all lists in registry"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Remove orphaned links from JSONL entries (EXPERIMENTAL)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without actually fixing"
    )
    
    args = parser.parse_args()
    
    if args.all:
        results = validate_all_lists()
    elif args.list_slug:
        results = validate_list_links(args.list_slug)
    else:
        print("❌ Error: Specify a list_slug or use --all")
        sys.exit(1)
    
    if args.fix and any("orphans" in r for r in [results] if isinstance(results, dict)):
        print("\n⚠️  Fix mode is experimental. Backing up...")
        # Fix logic would go here - for now, just report
        print("Fix mode not implemented yet. Manual cleanup required.")

if __name__ == "__main__":
    main()


