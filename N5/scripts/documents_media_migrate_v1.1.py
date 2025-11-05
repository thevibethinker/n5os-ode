#!/usr/bin/env python3
"""
Schema Migration v1.0 → v1.1: Add curation_score columns
Fixes critical bug identified in debugger report.
"""

import argparse
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")

DB_PATH = Path("/home/workspace/N5/data/documents_media.db")


def check_column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    """Check if column exists in table."""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def main(dry_run: bool = False) -> int:
    try:
        if not DB_PATH.exists():
            logging.error(f"Database not found: {DB_PATH}")
            return 1
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check current schema
        docs_has_curation = check_column_exists(cursor, "documents", "curation_score")
        media_has_curation = check_column_exists(cursor, "media", "curation_score")
        
        logging.info(f"Current schema check:")
        logging.info(f"  documents.curation_score: {'EXISTS' if docs_has_curation else 'MISSING'}")
        logging.info(f"  media.curation_score: {'EXISTS' if media_has_curation else 'MISSING'}")
        
        if docs_has_curation and media_has_curation:
            logging.info("✓ Schema already up to date")
            return 0
        
        if dry_run:
            logging.info("[DRY-RUN] Would add curation_score columns")
            if not docs_has_curation:
                logging.info("[DRY-RUN]   ALTER TABLE documents ADD COLUMN curation_score REAL DEFAULT 0.0")
            if not media_has_curation:
                logging.info("[DRY-RUN]   ALTER TABLE media ADD COLUMN curation_score REAL DEFAULT 0.0")
            return 0
        
        # Apply migration
        if not docs_has_curation:
            logging.info("Adding curation_score to documents table...")
            cursor.execute("ALTER TABLE documents ADD COLUMN curation_score REAL DEFAULT 0.0")
            logging.info("✓ documents.curation_score added")
        
        if not media_has_curation:
            logging.info("Adding curation_score to media table...")
            cursor.execute("ALTER TABLE media ADD COLUMN curation_score REAL DEFAULT 0.0")
            logging.info("✓ media.curation_score added")
        
        conn.commit()
        
        # Verify
        docs_has_curation = check_column_exists(cursor, "documents", "curation_score")
        media_has_curation = check_column_exists(cursor, "media", "curation_score")
        
        if docs_has_curation and media_has_curation:
            logging.info("✓ Migration successful - schema v1.1")
            return 0
        else:
            logging.error("❌ Migration verification failed")
            return 1
        
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        return 1
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate documents_media.db schema to v1.1"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
