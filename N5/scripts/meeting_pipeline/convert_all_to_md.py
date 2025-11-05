#!/usr/bin/env python3
"""
Convert ALL Word/DOCX files in Inbox to proper markdown
Uses pandoc for conversion
"""
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

INBOX_DIR = Path("/home/workspace/Personal/Meetings/Inbox")
CONVERTED_DIR = INBOX_DIR / "_CONVERTED"

def check_file_type(file_path):
    """Use 'file' command to detect actual file type."""
    result = subprocess.run(['file', '-b', str(file_path)], capture_output=True, text=True)
    return result.stdout.strip()

def convert_docx_to_md(docx_path):
    """Convert .docx to .md using pandoc."""
    # Create new filename: remove .transcript.md, add .md
    stem = docx_path.stem.replace('.transcript', '')
    md_path = docx_path.parent / f"{stem}.transcript.md.converted"
    
    try:
        # Use pandoc to convert
        subprocess.run([
            'pandoc',
            str(docx_path),
            '-f', 'docx',
            '-t', 'markdown',
            '-o', str(md_path),
            '--wrap=none'
        ], check=True, capture_output=True, text=True)
        
        logger.info(f"  ✅ Converted: {docx_path.name}")
        return md_path
    except subprocess.CalledProcessError as e:
        logger.error(f"  ❌ Failed to convert {docx_path.name}: {e.stderr}")
        return None

def main():
    logger.info("Converting Word docs to markdown...")
    CONVERTED_DIR.mkdir(exist_ok=True)
    
    # Find all .transcript.md files
    all_files = list(INBOX_DIR.glob("*.transcript.md"))
    logger.info(f"Found {len(all_files)} .transcript.md files")
    
    converted_count = 0
    for file_path in all_files:
        file_type = check_file_type(file_path)
        
        # Check if it's a Word doc or zip (which is docx)
        if "Microsoft Word" in file_type or "Zip archive" in file_type:
            md_path = convert_docx_to_md(file_path)
            if md_path and md_path.exists():
                # Replace original with converted
                backup_path = CONVERTED_DIR / file_path.name
                file_path.rename(backup_path)
                md_path.rename(file_path)
                converted_count += 1
    
    logger.info(f"\n✅ Converted {converted_count} files to markdown")
    logger.info(f"📁 Originals backed up in {CONVERTED_DIR}")
    
    # Now verify
    remaining_word = 0
    for file_path in INBOX_DIR.glob("*.transcript.md"):
        file_type = check_file_type(file_path)
        if "Microsoft Word" in file_type or "Zip archive" in file_type:
            remaining_word += 1
    
    if remaining_word > 0:
        logger.warning(f"⚠️ {remaining_word} Word docs still remain (conversion may have failed)")
    else:
        logger.info("✅ All files are now proper markdown!")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
