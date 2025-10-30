#!/usr/bin/env python3
"""
Zo Feedback Reporting Tool

Captures user feedback with optional attachments and stores in SQLite database.
Usage:
    python3 zo_report.py --type bug --severity high --title "..." --description "..." [--attach /path/to/image.png]
"""

import argparse
import asyncio
import hashlib
import json
import logging
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Constants
DB_PATH = Path("/home/workspace/N5/data/zo_feedback.db")
ATTACHMENTS_DIR = Path("/home/workspace/N5/data/zo_feedback_attachments")
SESSION_STATE_PATH = Path("SESSION_STATE.md")

# Ensure directories exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)


def init_database() -> None:
    """Initialize SQLite database with schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            conversation_id TEXT,
            session_tags TEXT,
            files_mentioned TEXT,
            tools_used TEXT,
            status TEXT DEFAULT 'new',
            sent_at TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feedback_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (feedback_id) REFERENCES feedback(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON feedback(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON feedback(timestamp)")
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized: {DB_PATH}")


def generate_feedback_id() -> str:
    """Generate unique feedback ID: zofb_<timestamp>_<hash>"""
    now = datetime.now(timezone.utc)
    timestamp_str = now.strftime("%Y%m%d%H%M%S")
    hash_input = f"{now.isoformat()}{id(object())}"
    hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:6]
    return f"zofb_{timestamp_str}_{hash_suffix}"


def get_conversation_context() -> tuple[Optional[str], Optional[list], Optional[list], Optional[list]]:
    """Extract context from SESSION_STATE.md if available."""
    conversation_id = None
    tags = None
    files = None
    tools = None
    
    # Try to find conversation workspace
    workspaces = Path("/home/.z/workspaces").glob("con_*")
    for workspace in workspaces:
        session_file = workspace / "SESSION_STATE.md"
        if session_file.exists():
            conversation_id = workspace.name
            # Simple parse for tags (could be enhanced)
            content = session_file.read_text()
            if "Tags:" in content:
                tags_line = [l for l in content.split("\n") if l.strip().startswith("Tags:")][0]
                tags = [t.strip() for t in tags_line.replace("Tags:", "").split(",")]
            break
    
    return conversation_id, tags, files, tools


def store_feedback(
    feedback_type: str,
    severity: str,
    title: str,
    description: str,
    attachments: list[Path]
) -> str:
    """Store feedback in database with optional attachments."""
    init_database()
    
    feedback_id = generate_feedback_id()
    now = datetime.now(timezone.utc).isoformat()
    
    # Get conversation context
    conv_id, tags, files, tools = get_conversation_context()
    
    # Insert feedback record
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO feedback (
            id, timestamp, type, severity, title, description,
            conversation_id, session_tags, files_mentioned, tools_used,
            status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?)
    """, (
        feedback_id,
        now,
        feedback_type,
        severity,
        title,
        description,
        conv_id,
        json.dumps(tags) if tags else None,
        json.dumps(files) if files else None,
        json.dumps(tools) if tools else None,
        now
    ))
    
    # Handle attachments
    if attachments:
        attachment_dir = ATTACHMENTS_DIR / feedback_id
        attachment_dir.mkdir(parents=True, exist_ok=True)
        
        for attach_path in attachments:
            if not attach_path.exists():
                logger.warning(f"Attachment not found: {attach_path}")
                continue
            
            # Copy to attachments directory
            dest_path = attachment_dir / attach_path.name
            shutil.copy2(attach_path, dest_path)
            
            # Store attachment record
            relative_path = dest_path.relative_to(ATTACHMENTS_DIR)
            cursor.execute("""
                INSERT INTO feedback_attachments (
                    feedback_id, file_path, file_type, file_size, uploaded_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                feedback_id,
                str(relative_path),
                attach_path.suffix.lower(),
                attach_path.stat().st_size,
                now
            ))
            
            logger.info(f"Attached: {attach_path.name} ({attach_path.stat().st_size} bytes)")
    
    conn.commit()
    conn.close()
    
    logger.info(f"✓ Stored feedback: {feedback_id}")
    logger.info(f"  Type: {feedback_type} | Severity: {severity}")
    logger.info(f"  Title: {title}")
    if conv_id:
        logger.info(f"  Context: {conv_id}")
    
    return feedback_id


def main():
    parser = argparse.ArgumentParser(
        description="Submit feedback to Zo team",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple bug report
  %(prog)s --type bug --severity high --title "API timeout" --description "Request timed out after 30s"
  
  # With screenshot
  %(prog)s --type bug --severity medium --title "UI glitch" --description "..." --attach /path/to/screenshot.png
  
  # Improvement suggestion
  %(prog)s --type improvement --severity low --title "Feature request" --description "Would love X feature"
  
  # List pending feedback
  %(prog)s --list-new
        """
    )
    
    parser.add_argument(
        "--list-new",
        action="store_true",
        help="List pending feedback items (status='new')"
    )
    
    parser.add_argument(
        "--type",
        choices=["bug", "improvement", "question", "glitch"],
        help="Type of feedback"
    )
    
    parser.add_argument(
        "--severity",
        choices=["low", "medium", "high"],
        help="Severity level"
    )
    
    parser.add_argument(
        "--title",
        help="Brief one-line title"
    )
    
    parser.add_argument(
        "--description",
        help="Detailed description"
    )
    
    parser.add_argument(
        "--attach",
        action="append",
        type=Path,
        help="Path to attachment (can be used multiple times)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.list_new:
            # Query and display pending feedback
            if not DB_PATH.exists():
                print("No feedback database found")
                return 0
            
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM feedback WHERE status='new' ORDER BY timestamp DESC")
            items = cursor.fetchall()
            conn.close()
            
            if not items:
                print("No pending feedback")
                return 0
            
            print(f"\nPending Feedback ({len(items)} items):\n")
            for item in items:
                print(f"  [{item['severity'].upper()}] {item['title']}")
                print(f"    ID: {item['id']}")
                print(f"    Type: {item['type']} | Created: {item['timestamp']}")
                print()
            
            return 0
        
        # Validate required fields for submit
        if not all([args.type, args.severity, args.title, args.description]):
            parser.error("--type, --severity, --title, and --description are required (or use --list-new)")
        
        feedback_id = store_feedback(
            feedback_type=args.type,
            severity=args.severity,
            title=args.title,
            description=args.description,
            attachments=args.attach or []
        )
        
        print(f"\n✓ Feedback submitted: {feedback_id}")
        print(f"  Will be sent in next daily sync (08:00 ET)")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
