#!/usr/bin/env python3
"""
Meeting Transcript Format Normalizer
Converts Word docs (.docx) with .transcript.md extension to actual markdown.
"""
import logging
import subprocess
from pathlib import Path
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")

def detect_file_type(filepath):
    """Use 'file' command to detect actual file type."""
    result = subprocess.run(
        ["file", "--brief", str(filepath)],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def convert_docx_to_markdown(docx_path):
    """Convert Word doc to markdown using pandoc."""
    md_path = docx_path.with_suffix(".transcript.md.converted")
    
    try:
        subprocess.run(
            ["pandoc", str(docx_path), "-f", "docx", "-t", "markdown", "-o", str(md_path)],
            check=True,
            capture_output=True
        )
        return md_path
    except subprocess.CalledProcessError as e:
        logging.error(f"Conversion failed for {docx_path.name}: {e.stderr.decode()}")
        return None

def normalize_inbox():
    """Scan inbox and convert all misformatted files."""
    files = list(INBOX.glob("*.transcript.md"))
    
    converted = 0
    skipped = 0
    errors = 0
    
    for filepath in files:
        file_type = detect_file_type(filepath)
        
        if "Microsoft Word" in file_type or "Zip archive" in file_type:
            logging.info(f"Converting: {filepath.name}")
            
            converted_path = convert_docx_to_markdown(filepath)
            if converted_path:
                # Replace original with converted
                filepath.unlink()
                converted_path.rename(filepath)
                converted += 1
                logging.info(f"✅ Converted: {filepath.name}")
            else:
                errors += 1
        elif "Unicode text" in file_type or "UTF-8" in file_type:
            skipped += 1
        else:
            logging.warning(f"Unknown format: {filepath.name} ({file_type})")
            errors += 1
    
    logging.info(f"\n=== Summary ===")
    logging.info(f"Converted: {converted}")
    logging.info(f"Already markdown: {skipped}")
    logging.info(f"Errors: {errors}")
    logging.info(f"Total processed: {len(files)}")
    
    return converted > 0

if __name__ == "__main__":
    normalize_inbox()
