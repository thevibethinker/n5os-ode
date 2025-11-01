#!/usr/bin/env python3
"""Meeting Pipeline Database Setup"""
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/N5/data/meeting_pipeline.db")

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meetings (
        meeting_id TEXT PRIMARY KEY,
        transcript_path TEXT NOT NULL,
        meeting_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'detected',
        quality_score REAL,
        detected_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        duration_seconds INTEGER,
        notes TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blocks (
        block_id TEXT PRIMARY KEY,
        meeting_id TEXT NOT NULL,
        block_type TEXT NOT NULL,
        content TEXT,
        file_path TEXT,
        size_bytes INTEGER,
        status TEXT NOT NULL DEFAULT 'pending',
        quality_score REAL,
        validation_issues TEXT,
        generated_at TEXT,
        duration_seconds INTEGER,
        model TEXT,
        FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        meeting_id TEXT NOT NULL,
        block_id TEXT,
        issue_type TEXT NOT NULL,
        issue_detail TEXT,
        detected_at TEXT NOT NULL,
        resolved INTEGER DEFAULT 0,
        resolved_at TEXT,
        FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id),
        FOREIGN KEY (block_id) REFERENCES blocks(block_id)
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_blocks_meeting ON blocks(meeting_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_blocks_status ON blocks(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_meeting ON feedback(meeting_id)")
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Database created: {DB_PATH}")

def verify_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    expected = ['meetings', 'blocks', 'feedback']
    for table in expected:
        if table in tables:
            logger.info(f"✅ Table exists: {table}")
        else:
            logger.error(f"❌ Table missing: {table}")
            return False
    return True

def insert_test_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("""
    INSERT OR REPLACE INTO meetings 
    (meeting_id, transcript_path, meeting_type, status, detected_at)
    VALUES (?, ?, ?, ?, ?)
    """, ("2025-10-31_test-meeting", "/tmp/test.md", "NETWORKING", "detected", now))
    
    for block_type in ["B01", "B02", "B08"]:
        block_id = f"2025-10-31_test-meeting_{block_type}"
        cursor.execute("""
        INSERT OR REPLACE INTO blocks
        (block_id, meeting_id, block_type, status, generated_at)
        VALUES (?, ?, ?, ?, ?)
        """, (block_id, "2025-10-31_test-meeting", block_type, "pending", now))
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM meetings")
    meeting_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM blocks")
    block_count = cursor.fetchone()[0]
    conn.close()
    
    logger.info(f"✅ Test data: {meeting_count} meetings, {block_count} blocks")
    return True

if __name__ == "__main__":
    logger.info("Creating Meeting Pipeline database...")
    create_database()
    
    if not verify_schema():
        exit(1)
    if not insert_test_data():
        exit(1)
    
    logger.info("✅ BUILD_WORKER_1: Database setup complete")
