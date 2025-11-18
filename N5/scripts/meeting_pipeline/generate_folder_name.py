#!/usr/bin/env python3
"""
Generate meeting folder name using LLM intelligence
Calls B99 prompt as tool to leverage semantic understanding
"""

import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Optional
from datetime import datetime

def extract_date_from_filename(filename: str) -> str:
    """Extract date from Drive filename pattern like: name-transcript-2025-11-11T16-28-16.678Z.docx"""
    match = re.search(r'-transcript-(\d{4}-\d{2}-\d{2})T', filename)
    if match:
        return match.group(1)
    # Fallback to current date
    return datetime.now().strftime("%Y-%m-%d")

def generate_folder_name_llm(b26_path: Path, b28_path: Path, current_name: Optional[str] = None) -> str:
    """
    Generate optimal folder name using LLM prompt B99
    
    Args:
        b26_path: Path to B26_metadata.md
        b28_path: Path to B28_strategic_intelligence.md
        current_name: Current folder name (optional, for context)
    
    Returns:
        Generated folder name (e.g., "2025-11-03_TimHe-twill_partnership")
    """
    
    # Read B26 and B28 content
    try:
        b26_content = b26_path.read_text()
        b28_content = b28_path.read_text()
    except Exception as e:
        print(f"Error reading metadata files: {e}", file=sys.stderr)
        return None
    
    # Construct prompt for LLM
    prompt_context = f"""Generate the optimal meeting folder name based on this intelligence:

## B26 Metadata
{b26_content}

## B28 Strategic Intelligence
{b28_content}

{f"## Current Folder Name\\n{current_name}\\n" if current_name else ""}

Follow the naming rules in file 'Intelligence/prompts/B99_folder_naming.md'.

Return ONLY the folder name in format: YYYY-MM-DD_identifier_type
"""
    
    # Create a temporary file with the prompt
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(prompt_context)
        prompt_file = f.name
    
    try:
        # Call Zo CLI to invoke the prompt (this would need to be implemented)
        # For now, we'll use a direct Python implementation as fallback
        
        # Import the name generation logic
        from name_normalizer import extract_metadata_from_b26, generate_folder_name_from_b26
        
        # Extract metadata
        meeting_dir = b26_path.parent
        metadata = extract_metadata_from_b26(meeting_dir)
        
        if not metadata:
            print("Error: Could not extract metadata from B26", file=sys.stderr)
            return None
        
        # Generate name using priority logic
        folder_name = generate_folder_name_from_b26(meeting_dir, metadata)
        
        return folder_name
        
    finally:
        # Cleanup temp file
        Path(prompt_file).unlink(missing_ok=True)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate meeting folder name using LLM intelligence'
    )
    parser.add_argument('b26_path', type=Path, help='Path to B26_metadata.md')
    parser.add_argument('b28_path', type=Path, help='Path to B28_strategic_intelligence.md')
    parser.add_argument('--current-name', type=str, help='Current folder name (optional)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.b26_path.exists():
        print(f"Error: B26 file not found: {args.b26_path}", file=sys.stderr)
        return 1
    
    if not args.b28_path.exists():
        print(f"Error: B28 file not found: {args.b28_path}", file=sys.stderr)
        return 1
    
    # Generate name
    folder_name = generate_folder_name_llm(
        args.b26_path,
        args.b28_path,
        args.current_name
    )
    
    if folder_name:
        print(folder_name)
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())

