#!/usr/bin/env python3
"""Batch add frontmatter to command files that are missing it."""

import json
from pathlib import Path
from datetime import datetime

# Load audit report
report_path = Path("/home/.z/workspaces/con_tY3K512yUo3sG7Iv/audit_report.json")
report = json.loads(report_path.read_text())

COMMANDS_DIR = Path("/home/workspace/N5/commands")

# Files to fix (exclude ones already handled manually)
files_to_fix = [
    # Priority: Files that are mostly complete but missing frontmatter
    "conversation-end.md",  # Has content, needs frontmatter
    "prompt-import.md",  # Has content, needs frontmatter
]

def generate_frontmatter(filename, existing_date=None):
    """Generate frontmatter for a command file."""
    # Use existing date if available, otherwise use current time
    timestamp = existing_date or datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Generate checksum from filename
    checksum = filename.replace(".md", "").replace("-", "_") + "_v1_0_0"
    
    # Determine category and tags based on filename
    if "knowledge" in filename:
        category = "knowledge"
        tags = ["knowledge", "data"]
    elif "list" in filename:
        category = "lists"
        tags = ["lists", "data"]
    elif "conversation" in filename:
        category = "productivity"
        tags = ["conversation", "workflow"]
    elif "prompt" in filename:
        category = "productivity"
        tags = ["prompts", "ai"]
    elif any(x in filename for x in ["intel", "extractor", "generator"]):
        category = "data-processing"
        tags = ["extraction", "analysis", "ai"]
    else:
        category = "misc"
        tags = ["utility"]
    
    frontmatter = f"""---
date: '{timestamp}'
last-tested: '{timestamp}'
generated_date: '{timestamp}'
checksum: {checksum}
tags: {tags}
category: {category}
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5/commands/{filename}
---
"""
    return frontmatter

def add_frontmatter(filepath):
    """Add frontmatter to a file that's missing it."""
    content = filepath.read_text()
    
    # Skip if already has frontmatter
    if content.startswith("---"):
        print(f"  ⏭️  {filepath.name} - Already has frontmatter, skipping")
        return False
    
    # Get file modification time for date
    mtime = datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Generate and prepend frontmatter
    frontmatter = generate_frontmatter(filepath.name, mtime)
    new_content = frontmatter + content
    
    # Write back
    filepath.write_text(new_content)
    print(f"  ✅ {filepath.name} - Frontmatter added")
    return True

def main():
    print("=" * 80)
    print("BATCH FIX: Adding Frontmatter to Command Files")
    print("=" * 80)
    print()
    
    # Process files from missing_frontmatter list
    fixed = 0
    skipped = 0
    errors = 0
    
    for item in report["missing_frontmatter"]:
        filename = item["file"]
        filepath = COMMANDS_DIR / filename
        
        # Skip files we've already manually fixed
        if filename in ["core-audit.md", "hygiene-preflight.md"]:
            print(f"  ⏭️  {filename} - Already fixed manually")
            skipped += 1
            continue
        
        # Skip files that are empty or have encoding errors
        if filename in report["empty"]:
            print(f"  ⏭️  {filename} - Empty file, needs manual creation")
            skipped += 1
            continue
        
        try:
            if add_frontmatter(filepath):
                fixed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ {filename} - Error: {e}")
            errors += 1
    
    print()
    print("=" * 80)
    print(f"✅ Fixed: {fixed}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")
    print("=" * 80)

if __name__ == "__main__":
    main()
