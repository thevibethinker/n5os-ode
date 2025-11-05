#!/usr/bin/env python3
"""
Test Huey pipeline with sample files
"""
import sys
from pathlib import Path

# Add services to path
sys.path.insert(0, '/home/workspace/N5/services')

from huey_queue.tasks import deduplicate_raw_files, convert_to_markdown, stage_validated_file

# Test with a small batch
STAGING = Path("/home/workspace/N5/data/staging/meetings")

def main():
    print("Testing Huey pipeline...")
    
    # Check staging
    docx_files = list(STAGING.glob("*.docx"))
    print(f"Found {len(docx_files)} .docx files in staging")
    
    if not docx_files:
        print("No files to process. Add .docx files to staging first.")
        return
    
    # Test deduplication
    print("\n1. Testing deduplication...")
    result = deduplicate_raw_files(str(STAGING))
    print(f"   Result: {result}")
    
    # Test conversion (first 3 files)
    unique_files = list(STAGING.glob("*.docx"))[:3]
    print(f"\n2. Testing conversion on {len(unique_files)} files...")
    
    for docx_file in unique_files:
        try:
            md_path = convert_to_markdown(str(docx_file))
            print(f"   ✅ Converted: {Path(md_path).name}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Test staging
    md_files = list(STAGING.glob("*.transcript.md"))[:3]
    print(f"\n3. Testing staging on {len(md_files)} files...")
    
    for md_file in md_files:
        try:
            dest = stage_validated_file(str(md_file))
            print(f"   ✅ Staged: {Path(dest).name}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print("\n✅ Test complete")

if __name__ == "__main__":
    main()
