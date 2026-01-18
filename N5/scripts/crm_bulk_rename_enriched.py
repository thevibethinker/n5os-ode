#!/usr/bin/env python3
"""
CRM Bulk Rename: Fix *-NotYetEnriched files that have already been enriched.

This is a one-time cleanup script to rename profiles that were enriched
but never had their filenames updated to canonical slugs.

Usage:
    python3 N5/scripts/crm_bulk_rename_enriched.py --dry-run  # Preview changes
    python3 N5/scripts/crm_bulk_rename_enriched.py            # Execute renames
"""

import argparse
import re
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, '/home/workspace')
from N5.scripts.crm_paths import CRM_INDIVIDUALS


def generate_canonical_slug(full_name: str) -> str:
    """Generate a canonical slug from a full name."""
    if not full_name:
        return ""
    slug = full_name.lower().strip()
    slug = re.sub(r"['\"]", "", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


def extract_full_name_from_profile(path: Path) -> str | None:
    """Extract full_name from Aviato enrichment in Intelligence Log."""
    content = path.read_text(encoding="utf-8", errors="ignore")
    
    # Try to find full_name in Intelligence Log (Aviato enrichment format)
    match = re.search(r"^- full_name: (.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    # Try to find it in frontmatter or header
    match = re.search(r"^# (.+)$", content, re.MULTILINE)
    if match:
        name = match.group(1).strip()
        # Validate it looks like a name (has at least 2 parts)
        if len(name.split()) >= 2:
            return name
    
    return None


def is_enriched(path: Path) -> bool:
    """Check if the profile has been enriched (has Aviato data)."""
    content = path.read_text(encoding="utf-8", errors="ignore")
    
    # Check for Aviato enrichment markers
    return (
        "aviato_enrichment" in content.lower() or
        "**Aviato Professional Intelligence:**" in content or
        "- full_name:" in content
    )


def find_notyetenriched_profiles() -> list[Path]:
    """Find all *-NotYetEnriched.md profiles."""
    profiles = []
    for path in CRM_INDIVIDUALS.glob("*-NotYetEnriched.md"):
        profiles.append(path)
    for path in CRM_INDIVIDUALS.glob("*-notyetenriched.md"):
        profiles.append(path)
    return sorted(set(profiles))


def rename_profile(old_path: Path, new_slug: str, dry_run: bool = True) -> tuple[bool, str]:
    """
    Rename a profile file to its canonical slug.
    
    Returns:
        (success, message)
    """
    new_path = CRM_INDIVIDUALS / f"{new_slug}.md"
    
    if new_path.exists():
        return False, f"Target exists: {new_slug}.md"
    
    if dry_run:
        return True, f"Would rename: {old_path.name} → {new_slug}.md"
    
    try:
        # Rename file
        old_path.rename(new_path)
        
        # Update person_id in frontmatter
        content = new_path.read_text(encoding="utf-8", errors="ignore")
        old_slug = old_path.stem
        if f"person_id: {old_slug}" in content:
            content = content.replace(f"person_id: {old_slug}", f"person_id: {new_slug}")
            new_path.write_text(content, encoding="utf-8")
        
        return True, f"Renamed: {old_path.name} → {new_slug}.md"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Bulk rename *-NotYetEnriched profiles to canonical slugs"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview changes without making them"
    )
    parser.add_argument(
        "--enriched-only",
        action="store_true",
        default=True,
        help="Only rename profiles that have been enriched (default)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Rename all *-NotYetEnriched profiles (even if not enriched)"
    )
    
    args = parser.parse_args()
    
    profiles = find_notyetenriched_profiles()
    
    print(f"🔍 Found {len(profiles)} *-NotYetEnriched profiles")
    print()
    
    if not profiles:
        print("✓ No profiles to rename")
        return
    
    results = {
        "renamed": [],
        "skipped_not_enriched": [],
        "skipped_target_exists": [],
        "skipped_no_name": [],
        "errors": []
    }
    
    for path in profiles:
        # Check if enriched
        enriched = is_enriched(path)
        
        if not args.all and not enriched:
            results["skipped_not_enriched"].append(path.name)
            continue
        
        # Extract name for slug
        full_name = extract_full_name_from_profile(path)
        
        if not full_name:
            # Fall back: strip suffix
            new_slug = path.stem.replace("-NotYetEnriched", "").replace("-notyetenriched", "")
            new_slug = new_slug.strip("-").lower()
        else:
            new_slug = generate_canonical_slug(full_name)
        
        if not new_slug:
            results["skipped_no_name"].append(path.name)
            continue
        
        success, message = rename_profile(path, new_slug, dry_run=args.dry_run)
        
        if success:
            results["renamed"].append(message)
        elif "Target exists" in message:
            results["skipped_target_exists"].append(f"{path.name} ({message})")
        else:
            results["errors"].append(f"{path.name}: {message}")
    
    # Print results
    if results["renamed"]:
        print(f"{'Would rename' if args.dry_run else '✓ Renamed'}: {len(results['renamed'])}")
        for msg in results["renamed"]:
            print(f"  {msg}")
        print()
    
    if results["skipped_not_enriched"]:
        print(f"⏭ Skipped (not enriched): {len(results['skipped_not_enriched'])}")
        for name in results["skipped_not_enriched"][:5]:
            print(f"  {name}")
        if len(results["skipped_not_enriched"]) > 5:
            print(f"  ... and {len(results['skipped_not_enriched']) - 5} more")
        print()
    
    if results["skipped_target_exists"]:
        print(f"⚠ Skipped (target exists): {len(results['skipped_target_exists'])}")
        for item in results["skipped_target_exists"]:
            print(f"  {item}")
        print()
    
    if results["skipped_no_name"]:
        print(f"⚠ Skipped (no name found): {len(results['skipped_no_name'])}")
        for name in results["skipped_no_name"]:
            print(f"  {name}")
        print()
    
    if results["errors"]:
        print(f"✗ Errors: {len(results['errors'])}")
        for error in results["errors"]:
            print(f"  {error}")
        print()
    
    # Summary
    print("─" * 50)
    print(f"Summary: {len(results['renamed'])} renamed, "
          f"{len(results['skipped_not_enriched'])} not enriched, "
          f"{len(results['skipped_target_exists'])} target exists, "
          f"{len(results['errors'])} errors")
    
    if args.dry_run and results["renamed"]:
        print("\n💡 Run without --dry-run to execute renames")


if __name__ == "__main__":
    main()
