#!/usr/bin/env python3
"""
Content Library Media Extension - Schema Migration Script
Part of Content Library Media Extension build (Worker 1)
"""

import sqlite3
import logging
from pathlib import Path
import json

# Configuration
DB_PATH = "/home/workspace/N5/data/content_library.db"
DIRECTORIES = [
    "/home/workspace/Knowledge/content-library/audio",
    "/home/workspace/Knowledge/content-library/video",
    "/home/workspace/Knowledge/content-library/images",
    "/home/workspace/Knowledge/content-library/transcripts",
]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def migrate_schema():
    """Add media-specific columns to the items table."""
    columns_to_add = [
        ("file_path", "TEXT"),
        ("mime_type", "TEXT"),
        ("duration_seconds", "INTEGER"),
        ("dimensions", "TEXT"),
        ("transcript_path", "TEXT"),
        ("media_metadata", "TEXT")
    ]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(items)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                logger.info(f"Adding column '{col_name}' ({col_type}) to 'items' table.")
                cursor.execute(f"ALTER TABLE items ADD COLUMN {col_name} {col_type}")
            else:
                logger.info(f"Column '{col_name}' already exists in 'items' table.")
        
        conn.commit()
        logger.info("Schema migration successful.")
    except Exception as e:
        logger.error(f"Schema migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def setup_directories():
    """Create the necessary directory structure for media files."""
    for dir_path in DIRECTORIES:
        p = Path(dir_path)
        if not p.exists():
            logger.info(f"Creating directory: {dir_path}")
            p.mkdir(parents=True, exist_ok=True)
        else:
            logger.info(f"Directory already exists: {dir_path}")

def define_taxonomy():
    """
    In the current system, tags are in a separate table (item_id, tag_key, tag_value).
    We define the canonical constants here for future workers to use.
    """
    taxonomy = {
        "types": ["audio", "video", "image", "podcast", "webinar", "presentation-recording"],
        "sources": ["meeting-recording", "loom", "youtube", "podcast-feed", "voice-memo"],
        "status": ["needs-transcription", "transcribed", "reviewed"]
    }
    
    logger.info("Canonical Taxonomy defined (for use in ingestion):")
    logger.info(json.dumps(taxonomy, indent=2))
    
    # We could pre-seed global tags here if needed, but usually tags are per-item.
    # However, let's ensure we can at least interact with the tags table.
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM tags")
        count = cursor.fetchone()[0]
        logger.info(f"Tags table verified. Current tag count: {count}")
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("Starting Content Library Media migration...")
    setup_directories()
    migrate_schema()
    define_taxonomy()
    logger.info("Migration complete.")

