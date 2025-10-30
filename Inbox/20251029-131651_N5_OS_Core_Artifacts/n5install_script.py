#!/usr/bin/env python3
"""
N5 OS Core Installation Script
Installs N5 cognitive operating system for Zo Computer instances.

Usage:
    python3 n5install_script.py --target /home/workspace
    python3 n5install_script.py --target /home/workspace --dry-run
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

VERSION = "0.1.0"

DIRECTORY_STRUCTURE = {
    "Documents": "Long-form documentation and system specs",
    "Knowledge": "Architectural principles and SSOT content",
    "Knowledge/architectural": "System design principles",
    "Knowledge/architectural/principles": "Individual principle documents",
    "Lists": "Action tracking (inbox, someday, waiting)",
    "Records": "Processing staging area",
    "Records/Company": "Business-related records",
    "Records/Personal": "Personal information processing",
    "Records/Temporary": "Short-term processing (auto-archive 14d)",
    "N5": "Core operating system",
    "N5/commands": "Command definitions (markdown)",
    "N5/config": "System configuration",
    "N5/data": "Databases and persistent state",
    "N5/logs": "System logs and thread exports",
    "N5/prefs": "User preferences",
    "N5/prefs/operations": "Operational protocols",
    "N5/schemas": "JSON schemas for validation",
    "N5/scripts": "Automation scripts",
}

CORE_FILES = {
    "Documents/N5.md": "# N5 System Overview\n\nSee user guide and developer guide for details.\n",
    "Lists/inbox.md": "# Inbox\n\n*New items requiring triage*\n\n",
    "Lists/someday.md": "# Someday\n\n*Deferred but not forgotten*\n\n",
    "Lists/waiting.md": "# Waiting\n\n*Blocked on external dependencies*\n\n",
    "N5/config/commands.jsonl": "",  # Empty, will be populated by command compiler
    "N5/prefs/prefs.md": """# N5 Preferences

## Touch Rate
- target: 15%  # Percent of items requiring manual intervention
- alert_threshold: 25%  # Alert when touch rate exceeds this

## Auto-Archive
- temporary_records_days: 14
- completed_tasks_days: 30
- old_logs_days: 90

## Confidence Thresholds
- auto_triage: 0.85  # Confidence required for automated triage
- auto_categorize: 0.90  # Confidence required for auto-categorization
- auto_respond: 0.95  # Confidence required for automated responses

## SLA Defaults (hours)
- inbox_triage: 24
- records_processing: 168  # 7 days
- waiting_followup: 72  # 3 days

## Session Defaults
- default_conversation_type: "discussion"
- auto_detect_type: true
- load_system_files: true
""",
}

SCHEMA_FILES = {
    "N5/schemas/index.schema.json": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://n5.local/schemas/index.schema.json",
        "title": "N5 Index Entry",
        "type": "object",
        "required": ["path", "kind", "updated_at"],
        "properties": {
            "path": {"type": "string"},
            "kind": {"type": "string", "enum": ["doc", "sheet", "code", "media", "service", "note"]},
            "tags": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
            "summary": {"type": "string", "maxLength": 220},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    }
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Install N5 OS Core on Zo Computer instance"
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Target installation directory (e.g., /home/workspace)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be installed without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing installation (DESTRUCTIVE)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"N5 Installer v{VERSION}"
    )
    return parser.parse_args()


def validate_target(target: Path, force: bool = False) -> bool:
    """Validate target directory is suitable for installation."""
    if not target.exists():
        logger.error(f"Target directory does not exist: {target}")
        return False
    
    if not target.is_dir():
        logger.error(f"Target is not a directory: {target}")
        return False
    
    # Check for existing N5 installation
    n5_dir = target / "N5"
    if n5_dir.exists() and not force:
        logger.error(
            f"N5 installation already exists at {n5_dir}. "
            "Use --force to overwrite (DESTRUCTIVE)"
        )
        return False
    
    # Check write permissions
    if not (target /".write_test").parent.exists():
        logger.error(f"Cannot write to target directory: {target}")
        return False
    
    return True


def create_directories(target: Path, dry_run: bool = False) -> Dict[str, bool]:
    """Create directory structure."""
    results = {}
    
    for rel_path, description in DIRECTORY_STRUCTURE.items():
        full_path = target / rel_path
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create: {full_path}")
            results[rel_path] = True
            continue
        
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Created: {full_path}")
            results[rel_path] = True
        except Exception as e:
            logger.error(f"✗ Failed to create {full_path}: {e}")
            results[rel_path] = False
    
    return results


def create_files(target: Path, dry_run: bool = False) -> Dict[str, bool]:
    """Create core files."""
    results = {}
    
    for rel_path, content in CORE_FILES.items():
        full_path = target / rel_path
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create file: {full_path}")
            results[rel_path] = True
            continue
        
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            logger.info(f"✓ Created file: {full_path}")
            results[rel_path] = True
        except Exception as e:
            logger.error(f"✗ Failed to create {full_path}: {e}")
            results[rel_path] = False
    
    return results


def create_schemas(target: Path, dry_run: bool = False) -> Dict[str, bool]:
    """Create JSON schemas."""
    results = {}
    
    for rel_path, schema in SCHEMA_FILES.items():
        full_path = target / rel_path
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create schema: {full_path}")
            results[rel_path] = True
            continue
        
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(json.dumps(schema, indent=2))
            logger.info(f"✓ Created schema: {full_path}")
            results[rel_path] = True
        except Exception as e:
            logger.error(f"✗ Failed to create {full_path}: {e}")
            results[rel_path] = False
    
    return results


def initialize_database(target: Path, dry_run: bool = False) -> bool:
    """Initialize SQLite database for session state."""
    db_path = target / "N5/data/conversations.db"
    
    if dry_run:
        logger.info(f"[DRY RUN] Would initialize database: {db_path}")
        return True
    
    try:
        import sqlite3
        
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                convo_id TEXT PRIMARY KEY,
                type TEXT,
                mode TEXT,
                focus TEXT,
                objective TEXT,
                tags TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                convo_id TEXT,
                file_path TEXT,
                added_at TEXT,
                FOREIGN KEY (convo_id) REFERENCES conversations(convo_id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Initialized database: {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        return False


def verify_installation(target: Path) -> bool:
    """Verify installation completed successfully."""
    required_paths = [
        "N5",
        "N5/config",
        "N5/data",
        "N5/scripts",
        "N5/schemas",
        "Knowledge",
        "Lists",
        "Records",
        "N5/data/conversations.db"
    ]
    
    for rel_path in required_paths:
        full_path = target / rel_path
        if not full_path.exists():
            logger.error(f"✗ Missing required path: {full_path}")
            return False
    
    logger.info("✓ Installation verification passed")
    return True


def main() -> int:
    args = parse_args()
    
    logger.info(f"N5 OS Core Installer v{VERSION}")
    logger.info(f"Target: {args.target}")
    
    if args.dry_run:
        logger.info("*** DRY RUN MODE - No changes will be made ***")
    
    # Validate
    if not validate_target(args.target, force=args.force):
        return 1
    
    # Create directories
    logger.info("Creating directory structure...")
    dir_results = create_directories(args.target, dry_run=args.dry_run)
    if not all(dir_results.values()):
        logger.error("Directory creation failed")
        return 1
    
    # Create files
    logger.info("Creating core files...")
    file_results = create_files(args.target, dry_run=args.dry_run)
    if not all(file_results.values()):
        logger.error("File creation failed")
        return 1
    
    # Create schemas
    logger.info("Creating schemas...")
    schema_results = create_schemas(args.target, dry_run=args.dry_run)
    if not all(schema_results.values()):
        logger.error("Schema creation failed")
        return 1
    
    # Initialize database
    logger.info("Initializing database...")
    if not initialize_database(args.target, dry_run=args.dry_run):
        logger.error("Database initialization failed")
        return 1
    
    if args.dry_run:
        logger.info("*** DRY RUN COMPLETE - No changes were made ***")
        return 0
    
    # Verify
    logger.info("Verifying installation...")
    if not verify_installation(args.target):
        return 1
    
    logger.info("")
    logger.info("="*60)
    logger.info("✓ N5 OS Core installation complete!")
    logger.info("="*60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Review and customize N5/prefs/prefs.md")
    logger.info("2. Read user guide: user_guide_template.md")
    logger.info("3. Start a conversation with Zo - N5 will auto-initialize")
    logger.info("")
    logger.info(f"Installation directory: {args.target}")
    logger.info("")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
