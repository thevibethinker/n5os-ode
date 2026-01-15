#!/usr/bin/env python3
"""
Media Batch Ingest Script for Content Library
Recursively finds and ingests media files from a directory.

Part of Content Library Media Extension build (Worker 2)

Usage:
    python3 media_batch_ingest.py <directory> [--move] [--dry-run] [--exclude PATTERN]
"""

import argparse
import json
import logging
import re
from pathlib import Path

# Import from media_ingest
from media_ingest import (
    AUDIO_EXTENSIONS,
    VIDEO_EXTENSIONS,
    IMAGE_EXTENSIONS,
    ingest_media,
    check_already_ingested,
    compute_file_hash
)

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ALL_MEDIA_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS | IMAGE_EXTENSIONS


def find_media_files(
    directory: Path,
    exclude_patterns: list[str] | None = None
) -> list[Path]:
    """Recursively find all media files in a directory."""
    media_files = []
    exclude_patterns = exclude_patterns or []
    
    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue
        
        # Check extension
        if file_path.suffix.lower() not in ALL_MEDIA_EXTENSIONS:
            continue
        
        # Check exclude patterns
        skip = False
        for pattern in exclude_patterns:
            if re.search(pattern, str(file_path)):
                skip = True
                break
        
        if not skip:
            media_files.append(file_path)
    
    return sorted(media_files)


def batch_ingest(
    directory: Path,
    move: bool = False,
    dry_run: bool = False,
    exclude_patterns: list[str] | None = None
) -> dict:
    """
    Batch ingest all media files from a directory.
    
    Returns summary dict.
    """
    directory = directory.resolve()
    
    if not directory.exists():
        return {"status": "error", "message": f"Directory not found: {directory}"}
    
    if not directory.is_dir():
        return {"status": "error", "message": f"Not a directory: {directory}"}
    
    logger.info(f"Scanning directory: {directory}")
    media_files = find_media_files(directory, exclude_patterns)
    logger.info(f"Found {len(media_files)} media files")
    
    results = {
        "total": len(media_files),
        "ingested": 0,
        "skipped": 0,
        "errors": 0,
        "details": []
    }
    
    for i, file_path in enumerate(media_files, 1):
        logger.info(f"[{i}/{len(media_files)}] Processing: {file_path.name}")
        
        result = ingest_media(
            file_path=file_path,
            move=move,
            dry_run=dry_run
        )
        
        results["details"].append({
            "file": str(file_path),
            "result": result
        })
        
        if result["status"] == "success" or result["status"] == "dry-run":
            results["ingested"] += 1
        elif result["status"] == "skipped":
            results["skipped"] += 1
        else:
            results["errors"] += 1
    
    logger.info("=" * 50)
    logger.info(f"Batch complete: {results['ingested']} ingested, {results['skipped']} skipped, {results['errors']} errors")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Batch ingest media files into the Content Library"
    )
    parser.add_argument("directory", type=Path, help="Directory to scan")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument(
        "--exclude", 
        action="append",
        dest="exclude_patterns",
        help="Regex pattern to exclude (can be used multiple times)"
    )
    
    args = parser.parse_args()
    
    result = batch_ingest(
        directory=args.directory,
        move=args.move,
        dry_run=args.dry_run,
        exclude_patterns=args.exclude_patterns
    )
    
    # Print summary (without full details for cleaner output)
    summary = {k: v for k, v in result.items() if k != "details"}
    print(json.dumps(summary, indent=2))
    
    if result.get("status") == "error":
        exit(1)
    elif result.get("errors", 0) > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()

