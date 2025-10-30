#!/usr/bin/env python3
"""
Zo Feedback Sync Orchestrator

This script queries new feedback and outputs JSON instructions for Zo to execute.
Zo will then handle the actual Drive API calls via use_app_google_drive tool.

Usage:
    python3 zo_feedback_orchestrator.py [--dry-run]
    
Output: JSON array of sync instructions for Zo to process
"""

import argparse
import json
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Constants
DB_PATH = Path("/home/workspace/N5/data/zo_feedback.db")
ATTACHMENTS_DIR = Path("/home/workspace/N5/data/zo_feedback_attachments")
DRIVE_FOLDER_ID = "1nNDtW4oXFablYY5hY9iTxEuK60cVwpLl"


def get_new_feedback() -> list[dict]:
    """Query all feedback with status='new' from database."""
    if not DB_PATH.exists():
        logger.warning(f"Database not found: {DB_PATH}")
        return []
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM feedback 
        WHERE status = 'new' 
        ORDER BY timestamp ASC
    """)
    
    feedback_items = []
    for row in cursor.fetchall():
        item = dict(row)
        
        # Get attachments
        cursor.execute("""
            SELECT * FROM feedback_attachments 
            WHERE feedback_id = ?
        """, (item['id'],))
        
        item['attachments'] = [dict(a) for a in cursor.fetchall()]
        feedback_items.append(item)
    
    conn.close()
    return feedback_items


def format_feedback_markdown(item: dict) -> str:
    """Format feedback item as markdown content."""
    doc_content = f"""# {item['title']}

**ID:** `{item['id']}`  
**Type:** {item['type']}  
**Severity:** {item['severity'].upper()}  
**Submitted:** {item['timestamp']}  

---

## Description

{item['description']}

---

## Context

**Conversation ID:** `{item['conversation_id'] or 'N/A'}`  
"""
    
    if item.get('session_tags'):
        try:
            tags = json.loads(item['session_tags'])
            doc_content += f"**Tags:** {', '.join(tags)}  \n"
        except:
            pass
    
    if item.get('files_mentioned'):
        try:
            files = json.loads(item['files_mentioned'])
            doc_content += f"**Files:** {', '.join(files)}  \n"
        except:
            pass
    
    if item.get('tools_used'):
        try:
            tools = json.loads(item['tools_used'])
            doc_content += f"**Tools:** {', '.join(tools)}  \n"
        except:
            pass
    
    if item['attachments']:
        doc_content += "\n---\n\n## Attachments\n\n"
        for attach in item['attachments']:
            doc_content += f"- `{attach['file_path']}` ({attach['file_size']} bytes)\n"
    
    doc_content += f"\n---\n\n*Report generated: {datetime.now(timezone.utc).isoformat()}*\n"
    
    return doc_content


def generate_sync_instructions(dry_run: bool = False) -> list[dict]:
    """Generate sync instructions for Zo to execute."""
    feedback_items = get_new_feedback()
    
    if not feedback_items:
        logger.info("No new feedback to sync")
        return []
    
    logger.info(f"Found {len(feedback_items)} new feedback item(s)")
    
    instructions = []
    
    for item in feedback_items:
        # Create markdown content
        content = format_feedback_markdown(item)
        
        # Build instruction for this feedback item
        instruction = {
            "feedback_id": item['id'],
            "title": item['title'],
            "severity": item['severity'],
            "type": item['type'],
            "content": content,
            "attachments": [],
            "target_folder_id": DRIVE_FOLDER_ID
        }
        
        # Add attachment paths
        for attach in item['attachments']:
            attach_path = ATTACHMENTS_DIR / attach['file_path']
            if attach_path.exists():
                instruction['attachments'].append({
                    "path": str(attach_path.absolute()),
                    "name": attach_path.name,
                    "size": attach['file_size']
                })
            else:
                logger.warning(f"Attachment not found: {attach_path}")
        
        instructions.append(instruction)
    
    return instructions


def mark_as_sent(feedback_ids: list[str]) -> None:
    """Update feedback status to 'sent' in database."""
    if not feedback_ids:
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc).isoformat()
    
    placeholders = ','.join('?' * len(feedback_ids))
    cursor.execute(f"""
        UPDATE feedback 
        SET status = 'sent', sent_at = ? 
        WHERE id IN ({placeholders})
    """, [now] + feedback_ids)
    
    conn.commit()
    conn.close()
    
    logger.info(f"✓ Marked {len(feedback_ids)} items as sent")


def main():
    parser = argparse.ArgumentParser(description="Generate Zo feedback sync instructions")
    parser.add_argument("--dry-run", action="store_true", help="Preview without database changes")
    parser.add_argument("--mark-sent", nargs="+", help="Mark specific feedback IDs as sent")
    args = parser.parse_args()
    
    try:
        if args.mark_sent:
            mark_as_sent(args.mark_sent)
            print(f"\n✓ Marked {len(args.mark_sent)} items as sent")
            return 0
        
        instructions = generate_sync_instructions(dry_run=args.dry_run)
        
        if not instructions:
            print(json.dumps({"status": "no_new_feedback", "count": 0}, indent=2))
            return 0
        
        # Output instructions as JSON for Zo to consume
        output = {
            "status": "ready_to_sync",
            "count": len(instructions),
            "instructions": instructions,
            "dry_run": args.dry_run
        }
        
        print(json.dumps(output, indent=2))
        
        if not args.dry_run:
            logger.info(f"Ready to sync {len(instructions)} items - Zo will handle Drive operations")
        
        return 0
        
    except Exception as e:
        logger.error(f"Orchestration failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
