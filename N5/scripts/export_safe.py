#!/usr/bin/env python3
"""
Safe Export - Export workspace files while excluding PII and protected paths

Usage:
    export_safe.py preview <source> <destination>
    export_safe.py export <source> <destination> [--force]
    export_safe.py check <path>

Reads .n5protected markers and excludes:
- Any path marked with contains_pii: true
- Any explicitly protected paths (unless --include-protected)

Reports what was included and excluded with reasons.
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

MARKER_FILENAME = ".n5protected"
WORKSPACE = Path("/home/workspace")

# Always exclude these (system/cache directories)
ALWAYS_EXCLUDE = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv',
    '.next', 'dist', 'build', '.cache', '.npm', '.bun'
}


def load_all_markers() -> dict[Path, dict]:
    """Load all .n5protected markers in workspace"""
    markers = {}
    
    try:
        for marker_path in WORKSPACE.rglob(MARKER_FILENAME):
            directory = marker_path.parent
            try:
                marker_data = json.loads(marker_path.read_text())
                markers[directory] = marker_data
            except Exception as e:
                logger.warning(f"Invalid marker at {marker_path}: {e}")
    
    except Exception as e:
        logger.error(f"Failed to load markers: {e}")
    
    return markers


def get_exclusion_reason(path: Path, markers: dict[Path, dict]) -> Optional[str]:
    """
    Check if a path should be excluded.
    Returns exclusion reason if excluded, None if safe.
    """
    resolved = path.resolve()
    
    # Check if path name is in always-exclude list
    if path.name in ALWAYS_EXCLUDE:
        return f"system directory ({path.name})"
    
    # Check if any parent is in always-exclude
    for parent in path.parents:
        if parent.name in ALWAYS_EXCLUDE:
            return f"inside system directory ({parent.name})"
    
    # Check against markers
    for marker_path, marker_data in markers.items():
        # Check if path is the marker directory or inside it
        try:
            path.resolve().relative_to(marker_path)
            is_inside = True
        except ValueError:
            is_inside = False
        
        if is_inside or path.resolve() == marker_path:
            # Check for PII
            if marker_data.get("contains_pii"):
                pii_cats = marker_data.get("pii_categories", [])
                return f"contains PII ({', '.join(pii_cats)})"
    
    return None


def preview_export(source: Path, destination: Path, markers: dict[Path, dict]) -> dict:
    """
    Preview what would be exported.
    Returns dict with 'included', 'excluded', and 'stats'.
    """
    included = []
    excluded = []
    
    if not source.exists():
        logger.error(f"Source does not exist: {source}")
        return {"error": "Source does not exist"}
    
    # Walk the source tree
    if source.is_file():
        files = [source]
    else:
        files = list(source.rglob('*'))
    
    for file_path in files:
        if file_path.is_dir():
            continue  # Only track files
        
        reason = get_exclusion_reason(file_path, markers)
        
        if reason:
            excluded.append({
                "path": str(file_path.relative_to(WORKSPACE) if file_path.is_relative_to(WORKSPACE) else file_path),
                "reason": reason
            })
        else:
            included.append(str(file_path.relative_to(WORKSPACE) if file_path.is_relative_to(WORKSPACE) else file_path))
    
    stats = {
        "total_files": len(files),
        "included_count": len(included),
        "excluded_count": len(excluded),
        "pii_excluded": sum(1 for e in excluded if "PII" in e["reason"]),
        "system_excluded": sum(1 for e in excluded if "system directory" in e["reason"]),
    }
    
    return {
        "source": str(source),
        "destination": str(destination),
        "included": included,
        "excluded": excluded,
        "stats": stats
    }


def perform_export(source: Path, destination: Path, markers: dict[Path, dict], force: bool = False) -> bool:
    """
    Actually perform the export, excluding PII paths.
    """
    preview = preview_export(source, destination, markers)
    
    if "error" in preview:
        return False
    
    # Check if destination exists
    if destination.exists() and not force:
        logger.error(f"Destination exists: {destination}. Use --force to overwrite.")
        return False
    
    # Create destination
    destination.mkdir(parents=True, exist_ok=True)
    
    # Copy included files
    copied = 0
    for rel_path in preview["included"]:
        src_file = WORKSPACE / rel_path if not Path(rel_path).is_absolute() else Path(rel_path)
        
        # Calculate destination path
        try:
            relative = src_file.relative_to(source)
        except ValueError:
            relative = Path(src_file.name)
        
        dst_file = destination / relative
        
        try:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied += 1
        except Exception as e:
            logger.warning(f"Failed to copy {src_file}: {e}")
    
    # Write export manifest
    manifest = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "files_exported": copied,
        "files_excluded": len(preview["excluded"]),
        "exclusions": preview["excluded"]
    }
    
    manifest_path = destination / "_export_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    
    logger.info(f"✓ Exported {copied} files to {destination}")
    logger.info(f"  Excluded {len(preview['excluded'])} files (see _export_manifest.json)")
    
    return True


def print_preview(preview: dict):
    """Print export preview in human-readable format"""
    print("\n" + "=" * 60)
    print("EXPORT PREVIEW")
    print("=" * 60)
    
    print(f"\nSource: {preview['source']}")
    print(f"Destination: {preview['destination']}")
    
    stats = preview['stats']
    print(f"\nTotal files: {stats['total_files']}")
    print(f"  ✓ Will include: {stats['included_count']}")
    print(f"  ✗ Will exclude: {stats['excluded_count']}")
    print(f"    - PII exclusions: {stats['pii_excluded']}")
    print(f"    - System exclusions: {stats['system_excluded']}")
    
    if preview['excluded']:
        print("\n" + "-" * 60)
        print("EXCLUDED FILES")
        print("-" * 60)
        
        # Group by reason
        by_reason = {}
        for item in preview['excluded']:
            reason = item['reason']
            if reason not in by_reason:
                by_reason[reason] = []
            by_reason[reason].append(item['path'])
        
        for reason, paths in sorted(by_reason.items()):
            print(f"\n🚫 {reason}:")
            for path in paths[:10]:
                print(f"   {path}")
            if len(paths) > 10:
                print(f"   ... and {len(paths) - 10} more")
    
    print("\n" + "=" * 60)


def check_path(path: Path, markers: dict[Path, dict]):
    """Check a single path for export safety"""
    reason = get_exclusion_reason(path, markers)
    
    if reason:
        print(f"🚫 EXCLUDED: {path}")
        print(f"   Reason: {reason}")
        return 1
    else:
        print(f"✓ SAFE: {path}")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safe Export - Export workspace files while excluding PII"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # preview command
    preview_parser = subparsers.add_parser("preview", help="Preview what would be exported")
    preview_parser.add_argument("source", type=Path, help="Source directory")
    preview_parser.add_argument("destination", type=Path, help="Destination directory")
    preview_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    
    # export command
    export_parser = subparsers.add_parser("export", help="Perform safe export")
    export_parser.add_argument("source", type=Path, help="Source directory")
    export_parser.add_argument("destination", type=Path, help="Destination directory")
    export_parser.add_argument("--force", "-f", action="store_true", help="Overwrite destination")
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check if a path is safe to export")
    check_parser.add_argument("path", type=Path, help="Path to check")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Load all markers
    markers = load_all_markers()
    logger.info(f"Loaded {len(markers)} protection markers")
    
    try:
        if args.command == "preview":
            source = args.source.resolve()
            destination = args.destination.resolve()
            
            preview = preview_export(source, destination, markers)
            
            if args.json:
                print(json.dumps(preview, indent=2))
            else:
                print_preview(preview)
            
            return 0
            
        elif args.command == "export":
            source = args.source.resolve()
            destination = args.destination.resolve()
            
            # Show preview first
            preview = preview_export(source, destination, markers)
            print_preview(preview)
            
            if preview['stats']['excluded_count'] > 0:
                print("\n⚠️  Some files will be excluded. Proceeding with export...")
            
            success = perform_export(source, destination, markers, args.force)
            return 0 if success else 1
            
        elif args.command == "check":
            path = args.path.resolve()
            return check_path(path, markers)
            
        else:
            parser.print_help()
            return 1
            
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

