#!/usr/bin/env python3
"""
Normalize transcript files to proper markdown format.

Handles:
- .docx files misnamed as .md (converts to markdown)
- Zip archives misnamed as .md (extracts and converts)
- Already-correct markdown files (passes through)

Usage:
    python3 normalize_transcript.py <file_path>
    python3 normalize_transcript.py --batch /path/to/inbox/
"""

import argparse
import logging
import magic
import subprocess
import sys
import tempfile
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
INBOX = WORKSPACE / "Personal/Meetings/Inbox"


def detect_actual_format(file_path: Path) -> str:
    """Detect actual file format using magic bytes."""
    try:
        mime = magic.from_file(str(file_path), mime=True)
        logger.info(f"Detected MIME type: {mime} for {file_path.name}")
        return mime
    except Exception as e:
        logger.error(f"Failed to detect format for {file_path}: {e}")
        return "unknown"


def convert_docx_to_markdown(docx_path: Path, output_path: Path) -> bool:
    """Convert .docx to markdown using pandoc."""
    try:
        logger.info(f"Converting {docx_path.name} to markdown...")
        result = subprocess.run(
            ["pandoc", str(docx_path), "-f", "docx", "-t", "markdown", "-o", str(output_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Converted to {output_path}")
            return True
        else:
            logger.error(f"Pandoc error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout converting {docx_path}")
        return False
    except Exception as e:
        logger.error(f"Failed to convert {docx_path}: {e}")
        return False


def normalize_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Normalize a single transcript file.
    
    Returns True if file is valid markdown after processing.
    """
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False
    
    # Detect actual format
    mime_type = detect_actual_format(file_path)
    
    # Already valid markdown
    if mime_type in ["text/plain", "text/markdown", "text/x-markdown"]:
        logger.info(f"✓ Already valid markdown: {file_path.name}")
        return True
    
    # Word document (misnamed as .md)
    if "word" in mime_type or "officedocument" in mime_type:
        logger.warning(f"⚠️ Word doc misnamed as .md: {file_path.name}")
        
        if dry_run:
            logger.info("[DRY RUN] Would convert to markdown")
            return False
        
        # Create temp output path
        temp_md = file_path.with_suffix(".md.converted")
        
        if convert_docx_to_markdown(file_path, temp_md):
            # Backup original
            backup = file_path.with_suffix(".md.backup-docx")
            file_path.rename(backup)
            logger.info(f"Backed up to {backup.name}")
            
            # Replace with converted version
            temp_md.rename(file_path)
            logger.info(f"✅ Replaced with converted markdown")
            return True
        else:
            return False
    
    # Zip archive (likely a .docx)
    if mime_type == "application/zip":
        logger.warning(f"⚠️ Zip archive misnamed as .md: {file_path.name}")
        
        if dry_run:
            logger.info("[DRY RUN] Would treat as .docx and convert")
            return False
        
        # Rename to .docx, then convert
        temp_docx = file_path.with_suffix(".docx.temp")
        file_path.rename(temp_docx)
        
        temp_md = file_path.with_suffix(".md.converted")
        
        if convert_docx_to_markdown(temp_docx, temp_md):
            # Backup original
            backup = file_path.with_suffix(".md.backup-zip")
            temp_docx.rename(backup)
            logger.info(f"Backed up to {backup.name}")
            
            # Replace with converted version
            temp_md.rename(file_path)
            logger.info(f"✅ Replaced with converted markdown")
            return True
        else:
            # Restore original name
            temp_docx.rename(file_path)
            return False
    
    logger.error(f"❌ Unknown format ({mime_type}): {file_path.name}")
    return False


def batch_normalize(inbox_dir: Path, dry_run: bool = False):
    """Normalize all .transcript.md files in inbox."""
    transcript_files = list(inbox_dir.glob("*.transcript.md"))
    
    logger.info(f"Found {len(transcript_files)} transcript files")
    
    stats = {
        "total": len(transcript_files),
        "valid": 0,
        "converted": 0,
        "failed": 0
    }
    
    for file_path in transcript_files:
        try:
            # Check if already valid
            mime = detect_actual_format(file_path)
            
            if mime in ["text/plain", "text/markdown", "text/x-markdown"]:
                stats["valid"] += 1
            else:
                # Needs conversion
                if normalize_file(file_path, dry_run):
                    stats["converted"] += 1
                else:
                    stats["failed"] += 1
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            stats["failed"] += 1
    
    logger.info("=" * 60)
    logger.info("BATCH NORMALIZATION COMPLETE")
    logger.info(f"Total files: {stats['total']}")
    logger.info(f"Already valid: {stats['valid']}")
    logger.info(f"Converted: {stats['converted']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Normalize transcript files to markdown")
    parser.add_argument("path", nargs="?", help="File or directory path")
    parser.add_argument("--batch", action="store_true", help="Process all files in inbox")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    if args.batch:
        batch_normalize(INBOX, args.dry_run)
    elif args.path:
        file_path = Path(args.path)
        success = normalize_file(file_path, args.dry_run)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
