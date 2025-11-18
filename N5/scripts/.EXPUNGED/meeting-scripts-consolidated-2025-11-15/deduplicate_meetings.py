#!/usr/bin/env python3
"""
LLM-based semantic meeting deduplication.
Uses Prompts/deduplicate-meetings.md to identify duplicates intelligently.
"""
import argparse
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)

def scan_directory(directory: Path) -> list[str]:
    """Scan directory for meeting transcript files."""
    files = []
    for f in directory.iterdir():
        if f.is_file() and f.suffix == '.md':
            files.append(f.name)
    return sorted(files)

def main(scan_dir: str, output: str = None, dry_run: bool = True):
    """
    Main deduplication flow.
    
    This script prepares the context for LLM analysis.
    The actual deduplication logic should be executed by invoking
    the Prompts/deduplicate-meetings.md prompt with the file list.
    """
    scan_path = Path(scan_dir).resolve()
    
    if not scan_path.exists():
        logging.error(f"Directory not found: {scan_path}")
        return 1
    
    logging.info(f"Scanning: {scan_path}")
    files = scan_directory(scan_path)
    logging.info(f"Found {len(files)} .md files")
    
    # Prepare context for LLM
    context = {
        "directory": str(scan_path),
        "total_files": len(files),
        "files": files,
        "scan_timestamp": datetime.utcnow().isoformat() + "Z",
        "dry_run": dry_run
    }
    
    output_path = Path(output) if output else Path("/tmp/meeting_dedup_context.json")
    output_path.write_text(json.dumps(context, indent=2))
    
    logging.info(f"✓ Context prepared: {output_path}")
    logging.info(f"✓ Ready for LLM analysis")
    logging.info("")
    logging.info("Next step: Load file 'Prompts/deduplicate-meetings.md' and analyze this context.")
    logging.info(f"Context file: {output_path}")
    
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare meeting files for LLM-based semantic deduplication"
    )
    parser.add_argument("--scan", required=True, help="Directory to scan")
    parser.add_argument("--output", help="Output path for context JSON")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Dry-run mode (default: true)")
    
    args = parser.parse_args()
    exit(main(args.scan, args.output, args.dry_run))
