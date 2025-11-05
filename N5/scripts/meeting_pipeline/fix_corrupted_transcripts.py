#!/usr/bin/env python3
"""
Fix Corrupted Transcript Files
Detects corrupted .transcript.md files (actually Word docs or corrupted zips),
deletes them, and prepares for proper re-download.
"""
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

INBOX_DIR = Path("/home/workspace/Personal/Meetings/Inbox")

def check_file_type(file_path):
    """Use 'file' command to detect actual file type."""
    result = subprocess.run(['file', '-b', str(file_path)], capture_output=True, text=True)
    file_type = result.stdout.strip()
    return file_type

def main():
    logger.info("Scanning for corrupted transcript files...")
    
    transcript_files = list(INBOX_DIR.glob("*.transcript.md"))
    logger.info(f"Found {len(transcript_files)} .transcript.md files")
    
    corrupted = []
    word_docs = []
    zip_files = []
    text_files = []
    
    for file_path in transcript_files:
        file_type = check_file_type(file_path)
        
        if "Microsoft Word" in file_type:
            word_docs.append(file_path)
        elif "Zip archive" in file_type or "corrupted" in file_type.lower():
            zip_files.append(file_path)
        elif "UTF-8" in file_type or "ASCII text" in file_type:
            text_files.append(file_path)
        else:
            corrupted.append((file_path, file_type))
    
    logger.info(f"\nFile Type Analysis:")
    logger.info(f"  - Word docs (need conversion): {len(word_docs)}")
    logger.info(f"  - Zip/Corrupted files (need re-download): {len(zip_files)}")
    logger.info(f"  - Valid text files: {len(text_files)}")
    logger.info(f"  - Unknown type: {len(corrupted)}")
    
    # Create quarantine directory
    quarantine_dir = INBOX_DIR / "_CORRUPTED_QUARANTINE"
    quarantine_dir.mkdir(exist_ok=True)
    
    # Move corrupted files
    moved_count = 0
    for file_path in zip_files + [c[0] for c in corrupted]:
        dest = quarantine_dir / file_path.name
        file_path.rename(dest)
        moved_count += 1
        logger.info(f"  Moved to quarantine: {file_path.name}")
    
    logger.info(f"\n✅ Moved {moved_count} corrupted files to quarantine")
    logger.info(f"📋 {len(word_docs)} Word docs remain (need conversion)")
    logger.info(f"✅ {len(text_files)} valid text files")
    
    # Report what needs to be done
    if word_docs:
        logger.info(f"\n⚠️ Next step: Convert {len(word_docs)} Word docs to markdown")
        logger.info("Run: python3 /home/workspace/N5/scripts/meeting_pipeline/convert_word_to_md.py")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
