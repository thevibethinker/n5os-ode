#!/usr/bin/env python3
"""
Research Migration Script - One-off migration from legacy locations.

Migrates research artifacts from:
- Knowledge/market and competitor intel/research/
- Knowledge/market and competitor intel/due-diligence/

To the new canonical location: Research/

Usage:
    python3 N5/scripts/migrate_research.py --dry-run
    python3 N5/scripts/migrate_research.py --execute
"""

import argparse
import shutil
from datetime import datetime
from pathlib import Path

LEGACY_LOCATIONS = [
    Path("/home/workspace/Knowledge/market and competitor intel/research"),
    Path("/home/workspace/Knowledge/market and competitor intel/due-diligence"),
]

RESEARCH_ROOT = Path("/home/workspace/Research")

# Category mappings for legacy folders
CATEGORY_MAPPINGS = {
    "research": "market-intel",
    "due-diligence": "market-intel/due-diligence",
}


def scan_legacy_items() -> list[dict]:
    """Scan legacy locations for items to migrate."""
    items = []
    
    for legacy_path in LEGACY_LOCATIONS:
        if not legacy_path.exists():
            continue
        
        category_key = legacy_path.name
        target_category = CATEGORY_MAPPINGS.get(category_key, "general")
        
        for item in legacy_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                items.append({
                    "source": item,
                    "name": item.name,
                    "target_category": target_category,
                    "target_path": RESEARCH_ROOT / target_category / item.name
                })
            elif item.is_file() and item.suffix == '.md':
                items.append({
                    "source": item,
                    "name": item.stem,
                    "target_category": target_category,
                    "target_path": RESEARCH_ROOT / target_category / item.name
                })
    
    return items


def migrate_item(item: dict, dry_run: bool = True) -> dict:
    """Migrate a single item."""
    result = {
        "source": str(item["source"]),
        "target": str(item["target_path"]),
        "status": "pending"
    }
    
    if dry_run:
        result["status"] = "would_migrate"
        return result
    
    try:
        # Ensure target category exists
        item["target_path"].parent.mkdir(parents=True, exist_ok=True)
        
        # Move the item
        if item["source"].is_dir():
            shutil.copytree(item["source"], item["target_path"])
            shutil.rmtree(item["source"])
        else:
            shutil.copy2(item["source"], item["target_path"])
            item["source"].unlink()
        
        result["status"] = "migrated"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result


def create_market_intel_readme():
    """Create README for market-intel category."""
    market_intel_path = RESEARCH_ROOT / "market-intel"
    market_intel_path.mkdir(parents=True, exist_ok=True)
    
    readme_content = """---
created: 2026-01-27
last_edited: 2026-01-27
version: 1.0
provenance: migrate_research.py
---

# Market Intelligence

Competitor analysis, due diligence, company research, and market investigations.

## Subcategories

- `due-diligence/` - Deep dives on specific companies or opportunities
"""
    (market_intel_path / "README.md").write_text(readme_content)


def main():
    parser = argparse.ArgumentParser(description="Migrate research from legacy locations")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without doing it")
    parser.add_argument("--execute", action="store_true", help="Actually perform the migration")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("Please specify --dry-run or --execute")
        return
    
    dry_run = not args.execute
    
    print(f"Research Migration {'(DRY RUN)' if dry_run else ''}")
    print("=" * 50)
    
    items = scan_legacy_items()
    
    if not items:
        print("No items found to migrate.")
        return
    
    print(f"Found {len(items)} items to migrate:\n")
    
    # Create market-intel category if executing
    if not dry_run:
        create_market_intel_readme()
    
    results = []
    for item in items:
        result = migrate_item(item, dry_run=dry_run)
        results.append(result)
        
        status_icon = "→" if dry_run else ("✓" if result["status"] == "migrated" else "✗")
        print(f"{status_icon} {result['source']}")
        print(f"  → {result['target']}")
        if result.get("error"):
            print(f"  Error: {result['error']}")
        print()
    
    # Summary
    migrated = sum(1 for r in results if r["status"] in ["migrated", "would_migrate"])
    errors = sum(1 for r in results if r["status"] == "error")
    
    print("=" * 50)
    if dry_run:
        print(f"Would migrate: {migrated} items")
        print("\nRun with --execute to perform migration.")
    else:
        print(f"Migrated: {migrated} items")
        if errors:
            print(f"Errors: {errors} items")
        
        # Log the migration
        log_path = RESEARCH_ROOT / ".migration_log.txt"
        with open(log_path, "a") as f:
            f.write(f"\n--- Migration {datetime.now().isoformat()} ---\n")
            for r in results:
                f.write(f"{r['status']}: {r['source']} → {r['target']}\n")


if __name__ == "__main__":
    main()
