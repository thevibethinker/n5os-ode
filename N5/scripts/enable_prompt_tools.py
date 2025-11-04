#!/usr/bin/env python3
"""
Enable tool invocation for all prompts by adding tool: true to frontmatter.

This makes prompts discoverable and invocable via @ mentions in Zo.
"""

import re
import argparse
import logging
from pathlib import Path
from typing import Tuple, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")
logger = logging.getLogger(__name__)

PROMPTS_DIR = Path("/home/workspace/Prompts")

def has_tool_field(content: str) -> bool:
    """Check if frontmatter already has tool field."""
    # Match YAML frontmatter
    frontmatter_pattern = r'^---\n(.*?)\n---'
    match = re.search(frontmatter_pattern, content, re.DOTALL)
    if not match:
        return False
    
    frontmatter = match.group(1)
    return bool(re.search(r'^tool:\s*', frontmatter, re.MULTILINE))

def add_tool_field(content: str) -> Tuple[str, bool]:
    """
    Add tool: true to frontmatter if missing.
    
    Returns:
        (modified_content, was_modified)
    """
    # Match YAML frontmatter
    frontmatter_pattern = r'^(---\n)(.*?)(\n---)'
    match = re.search(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        logger.warning("No frontmatter found")
        return content, False
    
    start_delimiter = match.group(1)
    frontmatter = match.group(2)
    end_delimiter = match.group(3)
    
    # Check if tool field already exists
    if re.search(r'^tool:\s*', frontmatter, re.MULTILINE):
        return content, False  # Already has tool field
    
    # Add tool: true after description or at start
    if 'description:' in frontmatter:
        # Add after description
        modified_frontmatter = re.sub(
            r"(description:.*?)(\n)",
            r"\1\2tool: true\n",
            frontmatter,
            count=1
        )
    else:
        # Add at beginning
        modified_frontmatter = f"tool: true\n{frontmatter}"
    
    # Reconstruct content
    modified_content = content.replace(
        f"{start_delimiter}{frontmatter}{end_delimiter}",
        f"{start_delimiter}{modified_frontmatter}{end_delimiter}"
    )
    
    return modified_content, True

def process_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Process single prompt file.
    
    Returns:
        True if modified (or would be modified in dry-run)
    """
    try:
        content = file_path.read_text()
        
        if has_tool_field(content):
            logger.debug(f"⊘ {file_path.name} - Already has tool field")
            return False
        
        modified_content, was_modified = add_tool_field(content)
        
        if not was_modified:
            logger.debug(f"⊘ {file_path.name} - No changes needed")
            return False
        
        if dry_run:
            logger.info(f"[DRY-RUN] ✓ {file_path.name} - Would add tool: true")
            return True
        else:
            file_path.write_text(modified_content)
            logger.info(f"✓ {file_path.name} - Added tool: true")
            return True
            
    except Exception as e:
        logger.error(f"✗ {file_path.name} - Error: {e}")
        return False

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enable tool invocation for prompts"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Process single file (for testing)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.file:
            # Single file mode
            if not args.file.exists():
                logger.error(f"File not found: {args.file}")
                return 1
            
            modified = process_file(args.file, dry_run=args.dry_run)
            return 0 if modified else 1
        
        # Batch mode - process all prompts
        prompt_files = list(PROMPTS_DIR.rglob("*.md"))
        
        if not prompt_files:
            logger.error(f"No .md files found in {PROMPTS_DIR}")
            return 1
        
        logger.info(f"Found {len(prompt_files)} prompt files")
        
        modified_count = 0
        skipped_count = 0
        
        for file_path in sorted(prompt_files):
            if process_file(file_path, dry_run=args.dry_run):
                modified_count += 1
            else:
                skipped_count += 1
        
        logger.info(f"\nSummary:")
        logger.info(f"  Modified: {modified_count}")
        logger.info(f"  Skipped: {skipped_count}")
        logger.info(f"  Total: {len(prompt_files)}")
        
        if args.dry_run:
            logger.info(f"\n⚠️  DRY RUN - No files were modified")
            logger.info(f"Run without --dry-run to apply changes")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
