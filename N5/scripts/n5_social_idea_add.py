#!/usr/bin/env python3
"""
Quick-add social media idea to Lists/social-media-ideas.md

Usage:
    n5_social_idea_add.py --title "Title" --body "Details..." [--tags "tag1,tag2"]
    n5_social_idea_add.py --interactive  # Prompt for input
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import logging
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

IDEAS_FILE = Path("/home/workspace/Lists/social-media-ideas.md")


def get_next_id() -> str:
    """Generate next sequential ID for today"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if not IDEAS_FILE.exists():
        return f"I-{today}-001"
    
    content = IDEAS_FILE.read_text()
    
    # Find all IDs for today
    pattern = rf"I-{re.escape(today)}-(\d{{3}})"
    matches = re.findall(pattern, content)
    
    if not matches:
        return f"I-{today}-001"
    
    # Get highest number and increment
    highest = max(int(m) for m in matches)
    next_num = highest + 1
    
    return f"I-{today}-{next_num:03d}"


def add_idea(title: str, body: str, tags: str = "", dry_run: bool = False) -> str:
    """Add idea to inbox section"""
    
    idea_id = get_next_id()
    
    # Format the idea block
    idea_block = f"""
**ID:** {idea_id}  
**Title:** {title}  
**Body:**

{body}

**Tags:** {tags if tags else "(none)"}

---
"""
    
    if dry_run:
        logger.info(f"[DRY RUN] Would add idea:")
        logger.info(f"  ID: {idea_id}")
        logger.info(f"  Title: {title}")
        logger.info(f"  Body length: {len(body)} chars")
        logger.info(f"  Tags: {tags if tags else '(none)'}")
        return idea_id
    
    # Read current content
    if not IDEAS_FILE.exists():
        logger.error(f"Ideas file not found: {IDEAS_FILE}")
        return ""
    
    content = IDEAS_FILE.read_text()
    
    # Find the Inbox section and insert after it
    inbox_marker = "## Inbox"
    
    if inbox_marker not in content:
        logger.error("Could not find '## Inbox' section in ideas file")
        return ""
    
    # Split at inbox marker, find the end of the header comment, insert idea
    parts = content.split(inbox_marker, 1)
    if len(parts) != 2:
        logger.error("Malformed ideas file")
        return ""
    
    before_inbox = parts[0] + inbox_marker
    after_inbox = parts[1]
    
    # Find end of comment block after inbox header
    comment_end = after_inbox.find("-->")
    if comment_end == -1:
        # No comment, insert right after inbox
        insert_point = 0
    else:
        insert_point = comment_end + 3
    
    # Insert the idea
    new_content = (
        before_inbox + 
        after_inbox[:insert_point] + 
        "\n" + idea_block + 
        after_inbox[insert_point:]
    )
    
    # Write back
    IDEAS_FILE.write_text(new_content)
    
    logger.info(f"✓ Added idea: {idea_id}")
    logger.info(f"  Title: {title}")
    logger.info(f"  File: {IDEAS_FILE}")
    
    return idea_id


def interactive_add():
    """Interactive mode for adding ideas"""
    print("\n=== Add Social Media Idea (Interactive) ===\n")
    
    title = input("Title: ").strip()
    if not title:
        print("Error: Title required")
        return 1
    
    print("\nBody (paste/type, then Ctrl-D or Ctrl-Z when done):")
    body_lines = []
    try:
        while True:
            line = input()
            body_lines.append(line)
    except EOFError:
        pass
    
    body = "\n".join(body_lines).strip()
    if not body:
        print("Error: Body required")
        return 1
    
    tags = input("\nTags (comma-separated, optional): ").strip()
    
    # Confirm
    print("\n--- Preview ---")
    print(f"Title: {title}")
    print(f"Body: {body[:100]}..." if len(body) > 100 else f"Body: {body}")
    print(f"Tags: {tags if tags else '(none)'}")
    
    confirm = input("\nAdd this idea? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Cancelled")
        return 0
    
    idea_id = add_idea(title, body, tags)
    if idea_id:
        print(f"\n✓ Added: {idea_id}")
        return 0
    else:
        print("\n✗ Failed to add idea")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Add social media idea to capture list")
    parser.add_argument("--title", help="Idea title")
    parser.add_argument("--body", help="Idea body/details")
    parser.add_argument("--tags", help="Comma-separated tags", default="")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--dry-run", action="store_true", help="Preview without adding")
    
    args = parser.parse_args()
    
    try:
        if args.interactive:
            return interactive_add()
        
        if not args.title or not args.body:
            parser.print_help()
            print("\nError: --title and --body required (or use --interactive)")
            return 1
        
        idea_id = add_idea(args.title, args.body, args.tags, dry_run=args.dry_run)
        
        if idea_id:
            return 0
        else:
            return 1
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
