#!/usr/bin/env python3
"""Fix files missing .docx extension and convert them"""
import subprocess
import logging
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

STAGING = Path("/home/workspace/Personal/Meetings/BULK_IMPORT_20251104/staging")

def main():
    # Find files without .transcript.md extension
    all_files = list(STAGING.iterdir())
    missing_ext = [f for f in all_files if f.is_file() and not f.name.endswith('.transcript.md')]
    
    logger.info(f"Found {len(missing_ext)} files without .transcript.md extension")
    
    for file_path in missing_ext:
        # Check if it's a Word doc
        result = subprocess.run(['file', '-b', str(file_path)], capture_output=True, text=True)
        file_type = result.stdout.strip()
        
        if 'Microsoft Word' in file_type:
            # Add .docx extension
            new_path = file_path.parent / f"{file_path.name}.docx"
            file_path.rename(new_path)
            logger.info(f"✅ Added .docx: {file_path.name}")
            
            # Now convert it
            clean_name = re.sub(r'^\[ZO-PROCESSED\]\s*', '', new_path.stem)
            output_path = new_path.parent / f"{clean_name}.transcript.md"
            
            result = subprocess.run([
                'pandoc', str(new_path), '-f', 'docx', '-t', 'markdown', '-o', str(output_path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                new_path.unlink()  # Delete the .docx
                logger.info(f"✅ Converted: {output_path.name}")
            else:
                logger.error(f"❌ Failed to convert: {new_path.name}")
        else:
            logger.warning(f"⚠️ Unknown file type: {file_path.name} ({file_type})")
    
    # Final count
    md_files = list(STAGING.glob("*.transcript.md"))
    logger.info(f"\n📊 Final count: {len(md_files)} .transcript.md files")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
