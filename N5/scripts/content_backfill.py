#!/usr/bin/env python3
"""
Content Library Backfill Script
Scans content directories and creates DB records for files not yet tracked.

Usage:
    python3 N5/scripts/content_backfill.py --dry-run  # Preview
    python3 N5/scripts/content_backfill.py            # Execute

Part of Content Library v4.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from content_ingest import (
    ingest_file,
    detect_content_type,
    get_relative_path,
    DB_PATH,
    WORKSPACE_ROOT,
)

# Paths
CANONICAL_ROOT = WORKSPACE_ROOT / "Knowledge/content-library"
BUILD_DIR = WORKSPACE_ROOT / "N5/builds/content-library-v4"

# Special paths that get extra tags
VRIJEN_PATH = CANONICAL_ROOT / "articles/vrijen"

# File extensions to process
CONTENT_EXTENSIONS = {".md", ".txt", ".pdf", ".html"}


def scan_content_directory(root: Path) -> list[Path]:
    """Scan directory recursively for content files."""
    files = []
    for ext in CONTENT_EXTENSIONS:
        files.extend(root.rglob(f"*{ext}"))
    return sorted(files)


def get_special_tags(filepath: Path) -> list[str]:
    """Get special tags based on file location."""
    tags = []
    
    # V's authored content
    try:
        if VRIJEN_PATH in filepath.parents or filepath.parent == VRIJEN_PATH:
            tags.append("vrijen-authored")
    except (ValueError, TypeError):
        pass
    
    return tags


def run_backfill(dry_run: bool = False) -> dict:
    """
    Run the backfill process.
    
    Returns summary dict.
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "scanned": 0,
        "created": 0,
        "skipped": 0,
        "errors": 0,
        "by_type": {},
        "files": [],
    }
    
    # Scan for content files
    print(f"📁 Scanning {CANONICAL_ROOT}...")
    files = scan_content_directory(CANONICAL_ROOT)
    report["scanned"] = len(files)
    print(f"   Found {len(files)} content files")
    
    if not files:
        print("   No files to process")
        return report
    
    # Process each file
    for filepath in files:
        content_type = detect_content_type(filepath)
        special_tags = get_special_tags(filepath)
        
        result = ingest_file(
            filepath=filepath,
            content_type=content_type,
            dry_run=dry_run,
            move=False,
            tags=special_tags if special_tags else None,
        )
        
        # Track results
        file_record = {
            "file": str(filepath.relative_to(WORKSPACE_ROOT)),
            "status": result["status"],
            "content_type": content_type,
        }
        
        if result["status"] == "created":
            report["created"] += 1
            file_record["record_id"] = result.get("record_id")
            print(f"   ✅ {filepath.name}")
        elif result["status"] == "skipped":
            report["skipped"] += 1
            print(f"   ⏭️  {filepath.name} (exists)")
        elif result["status"] == "dry_run":
            report["created"] += 1  # Would be created
            print(f"   🔍 {filepath.name} (would create)")
        elif result["status"] == "error":
            report["errors"] += 1
            file_record["error"] = result.get("error")
            print(f"   ❌ {filepath.name}: {result.get('error')}")
        
        # Track by type
        report["by_type"][content_type] = report["by_type"].get(content_type, 0) + 1
        report["files"].append(file_record)
    
    return report


def save_report(report: dict, output_path: Path):
    """Save backfill report to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Backfill Content Library database from existing files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dry-run    # Preview what would be created
  %(prog)s              # Execute backfill
        """
    )
    
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would happen without making changes"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=BUILD_DIR / "backfill_report.json",
        help="Output path for report"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Content Library Backfill")
    print("=" * 60)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    
    # Run backfill
    report = run_backfill(dry_run=args.dry_run)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Files scanned: {report['scanned']}")
    print(f"  Records {'would be ' if args.dry_run else ''}created: {report['created']}")
    print(f"  Skipped (exist): {report['skipped']}")
    print(f"  Errors: {report['errors']}")
    
    if report["by_type"]:
        print("\n  By content type:")
        for ct, count in sorted(report["by_type"].items()):
            print(f"    {ct}: {count}")
    
    # Save report
    save_report(report, args.output)
    
    # Exit code
    if report["errors"] > 0:
        exit(1)


if __name__ == "__main__":
    main()

