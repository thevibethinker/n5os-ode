#!/usr/bin/env python3
"""
Batch convert meeting transcripts from .docx to .transcript.md
Strips [ZO-PROCESSED] prefixes and validates output
"""
import logging
import subprocess
from pathlib import Path
import sys
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

STAGING = Path("/home/workspace/Personal/Meetings/BULK_IMPORT_20251104/staging")
LOG_FILE = STAGING.parent / "conversion_log.txt"

def convert_file(docx_path: Path) -> bool:
    """Convert single .docx to .transcript.md"""
    try:
        # Strip [ZO-PROCESSED] prefix from filename
        original_name = docx_path.stem
        clean_name = re.sub(r'^\[ZO-PROCESSED\]\s*', '', original_name)
        
        # Ensure it ends with .transcript
        if not clean_name.endswith('-transcript'):
            # Extract date and add transcript suffix if needed
            if 'transcript' not in clean_name.lower():
                clean_name = f"{clean_name}-transcript"
        
        # Output path
        output_path = docx_path.parent / f"{clean_name}.transcript.md"
        
        # Convert using pandoc
        result = subprocess.run([
            'pandoc',
            str(docx_path),
            '-f', 'docx',
            '-t', 'markdown',
            '-o', str(output_path)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            logger.error(f"❌ Pandoc failed for {docx_path.name}: {result.stderr}")
            return False
        
        # Validate output exists and has content
        if not output_path.exists():
            logger.error(f"❌ Output file not created: {output_path}")
            return False
        
        if output_path.stat().st_size < 100:
            logger.warning(f"⚠️ Suspiciously small output: {output_path} ({output_path.stat().st_size} bytes)")
        
        # Delete original .docx
        docx_path.unlink()
        
        logger.info(f"✅ Converted: {docx_path.name} → {output_path.name}")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Timeout converting {docx_path.name}")
        return False
    except Exception as e:
        logger.error(f"❌ Error converting {docx_path.name}: {e}")
        return False

def main():
    logger.info("Starting batch conversion...")
    
    # Find all .docx files
    docx_files = list(STAGING.glob("*.docx")) + list(STAGING.glob("*.txt"))
    logger.info(f"Found {len(docx_files)} files to process")
    
    if not docx_files:
        logger.error("No .docx or .txt files found!")
        return 1
    
    # Convert all files
    success = 0
    failed = 0
    
    for docx_file in docx_files:
        if docx_file.suffix == '.txt':
            # Text files - just rename
            clean_name = re.sub(r'^\[ZO-PROCESSED\]\s*', '', docx_file.stem)
            output_path = docx_file.parent / f"{clean_name}.transcript.md"
            docx_file.rename(output_path)
            logger.info(f"✅ Renamed text file: {docx_file.name} → {output_path.name}")
            success += 1
        else:
            if convert_file(docx_file):
                success += 1
            else:
                failed += 1
    
    # Summary
    logger.info("=" * 60)
    logger.info(f"✅ Successfully converted: {success}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📊 Total: {len(docx_files)}")
    
    # Verify all are .transcript.md now
    md_files = list(STAGING.glob("*.transcript.md"))
    logger.info(f"📝 Final count of .transcript.md files: {len(md_files)}")
    
    if failed > 0:
        logger.warning(f"⚠️ {failed} files failed conversion - check logs")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
