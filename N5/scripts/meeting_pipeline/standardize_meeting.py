#!/usr/bin/env python3
"""
Meeting Standardization Module
Integrates into pipeline after B26 generation.

Responsibilities:
1. Add frontmatter to all B*.md files
2. Infer taxonomy from B26_metadata.md
3. Rename folder to standard format
"""

import json
import logging
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
RENAME_LOG = MEETINGS_DIR / "rename_log.jsonl"

logger = logging.getLogger(__name__)


def standardize_meeting(meeting_id: str) -> bool:
    """
    Standardize a meeting folder after intelligence generation.
    
    Args:
        meeting_id: The meeting folder name (current, unstandardized)
    
    Returns:
        True if standardization succeeded, False otherwise
    """
    meeting_folder = MEETINGS_DIR / meeting_id
    
    if not meeting_folder.exists():
        logger.warning(f"Meeting folder not found: {meeting_id}")
        return False
    
    b26_file = meeting_folder / "B26_metadata.md"
    if not b26_file.exists():
        logger.warning(f"No B26_metadata.md found for {meeting_id}")
        return False
    
    try:
        # Step 1: Add frontmatter to all B*.md files
        logger.info(f"Adding frontmatter to {meeting_id}")
        add_frontmatter_result = add_frontmatter(meeting_folder)
        if not add_frontmatter_result:
            logger.warning(f"Frontmatter addition failed/skipped for {meeting_id}")
        
        # Step 2: Infer taxonomy and rename folder
        logger.info(f"Standardizing folder name for {meeting_id}")
        new_name = generate_standard_name(meeting_folder, b26_file)
        
        if not new_name:
            logger.warning(f"Could not generate standard name for {meeting_id}")
            return False
        
        if new_name == meeting_id:
            logger.info(f"Folder already has standard name: {meeting_id}")
            return True
        
        # Step 3: Rename (use shutil.move for cross-filesystem support)
        new_folder = MEETINGS_DIR / new_name
        if new_folder.exists():
            logger.warning(f"Target folder already exists: {new_name}")
            return False
        
        shutil.move(str(meeting_folder), str(new_folder))
        
        # Log the rename
        log_rename(meeting_id, new_name, "pipeline_integration")
        
        logger.info(f"✓ Standardized: {meeting_id} → {new_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error standardizing {meeting_id}: {e}")
        return False


def add_frontmatter(meeting_folder: Path) -> bool:
    """Add frontmatter to all B*.md files that don't have it."""
    b_files = list(meeting_folder.glob("B*.md"))
    if not b_files:
        return False
    
    added_count = 0
    for b_file in b_files:
        content = b_file.read_text()
        
        # Skip if already has frontmatter
        if content.startswith("---"):
            continue
        
        # Extract block ID from filename
        block_id = b_file.stem  # e.g., "B01_detailed_recap" -> "B01"
        if "_" in block_id:
            block_id = block_id.split("_")[0]
        
        # Generate frontmatter
        frontmatter = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
block_id: {block_id}
---

"""
        
        # Prepend frontmatter
        new_content = frontmatter + content
        b_file.write_text(new_content)
        added_count += 1
    
    logger.info(f"  Added frontmatter to {added_count}/{len(b_files)} files")
    return True


def generate_standard_name(meeting_folder: Path, b26_file: Path) -> Optional[str]:
    """Generate standard folder name using Zo CLI."""
    
    b26_content = b26_file.read_text()
    
    # Build prompt
    prompt = f"""Based on this B26 metadata, generate a standardized meeting folder name.

Format: YYYY-MM-DD_lead-participant_context_subtype

Rules:
- Date: ISO format from B26
- Lead participant: Actual company/person name (lowercase, hyphenated), NOT CRM codes
- Context: 2-4 words describing what meeting was about
- Subtype: One of: coaching, partnership, sales, workshop, discovery, ai-consulting, career-advising, standup, technical, planning, cofounder, general

B26 METADATA:
{b26_content}

Output ONLY the folder name, nothing else. No explanations, no markdown, no timestamps.
"""
    
    try:
        # Call Zo CLI
        result = subprocess.run(
            ["zo", prompt],
            capture_output=True,
            text=True,
            timeout=90,
            cwd="/home/workspace"
        )
        
        if result.returncode != 0:
            logger.warning(f"Zo CLI error: {result.stderr}")
            return None
        
        # Parse output - Zo returns JSON with "output" field
        try:
            data = json.loads(result.stdout)
            full_output = data.get("output", "")
        except json.JSONDecodeError:
            full_output = result.stdout
        
        # Extract folder name from output (look for pattern match
        import re
        for line in full_output.split("\n"):
            match = re.match(r"^\d{4}-\d{2}-\d{2}_[a-z0-9-]+_[a-z0-9-]+_[a-z]+$", line.strip())
            if match:
                folder_name = line.strip()
                logger.info(f"  Extracted folder name: {folder_name}")
                return folder_name
        
        logger.warning(f"Could not find valid folder name in Zo output: {full_output[:200]}")
        return None
        
    except Exception as e:
        logger.error(f"Error generating name: {e}")
        return None


def validate_folder_name(name: str) -> bool:
    """Validate that folder name matches expected format."""
    parts = name.split("_")
    if len(parts) != 4:
        return False
    
    date, participant, context, subtype = parts
    
    # Check date format
    if len(date) != 10 or date.count("-") != 2:
        return False
    
    # Check subtype is valid
    valid_subtypes = [
        "coaching", "partnership", "sales", "workshop", "discovery",
        "ai-consulting", "career-advising", "general",
        "standup", "technical", "planning", "cofounder"
    ]
    if subtype not in valid_subtypes:
        return False
    
    return True


def log_rename(old_name: str, new_name: str, method: str):
    """Log rename operation to JSONL file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "old": old_name,
        "new": new_name,
        "method": method
    }
    
    with open(RENAME_LOG, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    # Test mode - standardize a single meeting
    import sys
    if len(sys.argv) < 2:
        print("Usage: python standardize_meeting.py <meeting_id>")
        sys.exit(1)
    
    logging.basicConfig(level=logging.INFO)
    meeting_id = sys.argv[1]
    success = standardize_meeting(meeting_id)
    sys.exit(0 if success else 1)
