#!/usr/bin/env python3
"""
Initialize Documents & Media Intelligence System database.
Creates documents_media.db with schema per architectural specification.
"""

import argparse
import logging
import sqlite3
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")

DB_PATH = Path("/home/workspace/N5/data/documents_media.db")


def create_schema(conn: sqlite3.Connection) -> None:
    """Create all tables and indices for documents & media tracking."""
    cursor = conn.cursor()
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filepath TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            size_bytes INTEGER,
            created_date TEXT,
            modified_date TEXT,
            ingestion_date TEXT NOT NULL,
            source_origin TEXT,
            source_metadata TEXT,
            processing_status TEXT DEFAULT 'pending',
            last_processed TEXT,
            checksum TEXT,
            tags TEXT,
            UNIQUE(filepath)
        )
    """)
    
    # Documents indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_file_type ON documents(file_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_processing_status ON documents(processing_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_created_date ON documents(created_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_tags ON documents(tags)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_checksum ON documents(checksum)")
    
    # Media table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id TEXT PRIMARY KEY,
            filepath TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            media_type TEXT NOT NULL,
            format TEXT,
            duration_seconds INTEGER,
            size_bytes INTEGER,
            created_date TEXT,
            modified_date TEXT,
            ingestion_date TEXT NOT NULL,
            source_origin TEXT,
            source_metadata TEXT,
            transcript_path TEXT,
            transcript_status TEXT DEFAULT 'pending',
            processing_status TEXT DEFAULT 'pending',
            last_processed TEXT,
            checksum TEXT,
            tags TEXT,
            UNIQUE(filepath)
        )
    """)
    
    # Media indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_type ON media(media_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_transcript_status ON media(transcript_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_processing_status ON media(processing_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_checksum ON media(checksum)")
    
    # Intelligence extracts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_extracts (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            source_type TEXT NOT NULL,
            extract_type TEXT NOT NULL,
            content TEXT NOT NULL,
            knowledge_path TEXT,
            extracted_date TEXT NOT NULL,
            confidence_score REAL,
            metadata TEXT
        )
    """)
    
    # Intelligence indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intel_source_id ON intelligence_extracts(source_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intel_extract_type ON intelligence_extracts(extract_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intel_knowledge_path ON intelligence_extracts(knowledge_path)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_intel_source_type ON intelligence_extracts(source_type)")
    
    conn.commit()
    logging.info("✓ Schema created successfully")


def verify_schema(conn: sqlite3.Connection) -> bool:
    """Verify all tables and indices exist."""
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    required_tables = {'documents', 'media', 'intelligence_extracts'}
    
    if not required_tables.issubset(tables):
        missing = required_tables - tables
        logging.error(f"Missing tables: {missing}")
        return False
    
    # Check indices
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indices = {row[0] for row in cursor.fetchall()}
    
    required_indices = {
        'idx_doc_file_type', 'idx_doc_processing_status', 'idx_doc_created_date',
        'idx_doc_tags', 'idx_doc_checksum',
        'idx_media_type', 'idx_media_transcript_status', 'idx_media_processing_status',
        'idx_media_checksum',
        'idx_intel_source_id', 'idx_intel_extract_type', 'idx_intel_knowledge_path',
        'idx_intel_source_type'
    }
    
    if not required_indices.issubset(indices):
        missing = required_indices - indices
        logging.error(f"Missing indices: {missing}")
        return False
    
    logging.info("✓ Schema verification passed")
    return True


def main(dry_run: bool = False) -> int:
    """Initialize database with schema."""
    try:
        # Ensure data directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if database already exists
        db_exists = DB_PATH.exists()
        
        if dry_run:
            logging.info(f"[DRY-RUN] Would initialize database at: {DB_PATH}")
            logging.info(f"[DRY-RUN] Database exists: {db_exists}")
            if db_exists:
                # Connect to verify schema
                conn = sqlite3.connect(DB_PATH)
                verify_schema(conn)
                conn.close()
            return 0
        
        # Connect to database (creates if doesn't exist)
        conn = sqlite3.connect(DB_PATH)
        logging.info(f"Connected to database: {DB_PATH}")
        
        # Create schema
        create_schema(conn)
        
        # Verify schema
        if not verify_schema(conn):
            logging.error("Schema verification failed")
            return 1
        
        # Get database size
        size_bytes = DB_PATH.stat().st_size
        logging.info(f"Database size: {size_bytes:,} bytes")
        
        conn.close()
        logging.info(f"✓ Documents & Media database initialized: {DB_PATH}")
        return 0
        
    except Exception as e:
        logging.error(f"Error initializing database: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialize Documents & Media Intelligence System database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
