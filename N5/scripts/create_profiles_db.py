#!/usr/bin/env python3
"""
Create Profiles Database
Initializes profiles.db with schema for stakeholder profile tracking.
Idempotent - safe to run multiple times.
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/N5/data/profiles.db")


def create_schema(conn: sqlite3.Connection) -> None:
    """Create all tables and indexes."""
    
    cursor = conn.cursor()
    
    # Table: profiles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT,
            organization TEXT,
            profile_path TEXT NOT NULL,
            meeting_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_enriched_at TEXT,
            enrichment_count INTEGER DEFAULT 0,
            notes TEXT
        )
    """)
    
    # Table: profile_enrichments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile_enrichments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            enrichment_type TEXT NOT NULL,
            enriched_at TEXT NOT NULL,
            data_source TEXT,
            blocks_added TEXT,
            success BOOLEAN NOT NULL,
            error_message TEXT,
            FOREIGN KEY (profile_id) REFERENCES profiles(id)
        )
    """)
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_meeting_date ON profiles(meeting_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_enrichments_profile ON profile_enrichments(profile_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_enrichments_type ON profile_enrichments(enrichment_type)")
    
    conn.commit()
    logger.info("✓ Schema created/verified")


def verify_schema(conn: sqlite3.Connection) -> bool:
    """Verify all tables exist."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('profiles', 'profile_enrichments')")
    tables = {row[0] for row in cursor.fetchall()}
    
    if len(tables) != 2:
        logger.error(f"✗ Missing tables. Found: {tables}")
        return False
    
    logger.info("✓ Schema verification passed")
    return True


def main() -> int:
    """Main execution."""
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initializing database: {DB_PATH}")
        
        conn = sqlite3.connect(DB_PATH)
        try:
            create_schema(conn)
            if not verify_schema(conn):
                return 1
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM profiles")
            profile_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM profile_enrichments")
            enrichment_count = cursor.fetchone()[0]
            
            logger.info(f"✓ Database ready: {profile_count} profiles, {enrichment_count} enrichments")
            return 0
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
