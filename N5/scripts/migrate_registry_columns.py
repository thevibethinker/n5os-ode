#!/usr/bin/env python3
"""
Migration: Reorder conversations table columns (title after id)

Principles: P5 (Anti-Overwrite), P7 (Dry-Run), P19 (Error Handling), P18 (Verify State)

Usage:
    migrate_registry_columns.py --dry-run    # Preview changes
    migrate_registry_columns.py              # Execute migration
"""

import sqlite3
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime, UTC
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/N5/data/conversations.db")
BACKUP_DIR = Path("/home/workspace/N5/data/backups")

NEW_SCHEMA = """
-- Core conversations table with proper column order
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    title TEXT,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    mode TEXT,
    
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT,
    
    focus TEXT,
    objective TEXT,
    tags TEXT,
    
    parent_id TEXT,
    related_ids TEXT,
    
    starred INTEGER DEFAULT 0,
    progress_pct INTEGER DEFAULT 0,
    
    workspace_path TEXT,
    state_file_path TEXT,
    aar_path TEXT,
    
    FOREIGN KEY (parent_id) REFERENCES conversations(id)
);
"""


def backup_database(dry_run: bool = False) -> Path:
    """Create timestamped backup of database"""
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"conversations_{timestamp}.db"
    
    if dry_run:
        logger.info(f"[DRY RUN] Would backup to: {backup_path}")
        return backup_path
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DB_PATH, backup_path)
    
    # Verify backup
    if not backup_path.exists():
        raise RuntimeError(f"Backup failed: {backup_path} not created")
    
    backup_size = backup_path.stat().st_size
    original_size = DB_PATH.stat().st_size
    
    if backup_size != original_size:
        raise RuntimeError(f"Backup size mismatch: {backup_size} != {original_size}")
    
    logger.info(f"✓ Backup created: {backup_path} ({backup_size} bytes)")
    return backup_path


def extract_data(conn: sqlite3.Connection) -> dict:
    """Extract all data from existing tables"""
    data = {}
    
    # Conversations
    conversations = conn.execute("SELECT * FROM conversations").fetchall()
    data["conversations"] = [dict(row) for row in conversations]
    logger.info(f"  Extracted {len(data['conversations'])} conversations")
    
    # Artifacts
    artifacts = conn.execute("SELECT * FROM artifacts").fetchall()
    data["artifacts"] = [dict(row) for row in artifacts]
    logger.info(f"  Extracted {len(data['artifacts'])} artifacts")
    
    # Issues
    issues = conn.execute("SELECT * FROM issues").fetchall()
    data["issues"] = [dict(row) for row in issues]
    logger.info(f"  Extracted {len(data['issues'])} issues")
    
    # Learnings
    learnings = conn.execute("SELECT * FROM learnings").fetchall()
    data["learnings"] = [dict(row) for row in learnings]
    logger.info(f"  Extracted {len(data['learnings'])} learnings")
    
    # Decisions
    decisions = conn.execute("SELECT * FROM decisions").fetchall()
    data["decisions"] = [dict(row) for row in decisions]
    logger.info(f"  Extracted {len(data['decisions'])} decisions")
    
    return data


def restore_data(conn: sqlite3.Connection, data: dict):
    """Restore data to new table structure"""
    
    # Restore conversations
    for row in data["conversations"]:
        conn.execute("""
            INSERT INTO conversations (
                id, title, type, status, mode,
                created_at, updated_at, completed_at,
                focus, objective, tags,
                parent_id, related_ids,
                starred, progress_pct,
                workspace_path, state_file_path, aar_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("id"),
            row.get("title"),
            row.get("type"),
            row.get("status"),
            row.get("mode"),
            row.get("created_at"),
            row.get("updated_at"),
            row.get("completed_at"),
            row.get("focus"),
            row.get("objective"),
            row.get("tags"),
            row.get("parent_id"),
            row.get("related_ids"),
            row.get("starred", 0),
            row.get("progress_pct", 0),
            row.get("workspace_path"),
            row.get("state_file_path"),
            row.get("aar_path")
        ))
    logger.info(f"  Restored {len(data['conversations'])} conversations")
    
    # Restore artifacts
    for row in data["artifacts"]:
        conn.execute("""
            INSERT INTO artifacts (id, conversation_id, filepath, artifact_type, created_at, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row.get("id"),
            row.get("conversation_id"),
            row.get("filepath"),
            row.get("artifact_type"),
            row.get("created_at"),
            row.get("description")
        ))
    logger.info(f"  Restored {len(data['artifacts'])} artifacts")
    
    # Restore issues
    for row in data["issues"]:
        conn.execute("""
            INSERT INTO issues (
                id, conversation_id, timestamp, severity, category, 
                message, context, resolution, resolved
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("id"),
            row.get("conversation_id"),
            row.get("timestamp"),
            row.get("severity"),
            row.get("category"),
            row.get("message"),
            row.get("context"),
            row.get("resolution"),
            row.get("resolved", 0)
        ))
    logger.info(f"  Restored {len(data['issues'])} issues")
    
    # Restore learnings
    for row in data["learnings"]:
        conn.execute("""
            INSERT INTO learnings (
                id, conversation_id, lesson_id, timestamp, type,
                title, description, principle_refs, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("id"),
            row.get("conversation_id"),
            row.get("lesson_id"),
            row.get("timestamp"),
            row.get("type"),
            row.get("title"),
            row.get("description"),
            row.get("principle_refs"),
            row.get("status", "pending")
        ))
    logger.info(f"  Restored {len(data['learnings'])} learnings")
    
    # Restore decisions
    for row in data["decisions"]:
        conn.execute("""
            INSERT INTO decisions (
                id, conversation_id, timestamp, decision,
                rationale, alternatives, outcome
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("id"),
            row.get("conversation_id"),
            row.get("timestamp"),
            row.get("decision"),
            row.get("rationale"),
            row.get("alternatives"),
            row.get("outcome")
        ))
    logger.info(f"  Restored {len(data['decisions'])} decisions")


def verify_migration(original_data: dict, new_conn: sqlite3.Connection) -> bool:
    """Verify migration completed successfully"""
    logger.info("\nVerifying migration...")
    
    new_conn.row_factory = sqlite3.Row  # Enable column name access
    
    # Check conversation counts
    new_count = new_conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
    if new_count != len(original_data["conversations"]):
        logger.error(f"❌ Conversation count mismatch: {new_count} != {len(original_data['conversations'])}")
        return False
    logger.info(f"✓ Conversation count matches: {new_count}")
    
    # Check column order
    cursor = new_conn.execute("PRAGMA table_info(conversations)")
    columns = [row[1] for row in cursor.fetchall()]
    expected_order = ["id", "title", "type", "status", "mode"]
    if columns[:5] != expected_order:
        logger.error(f"❌ Column order incorrect: {columns[:5]} != {expected_order}")
        return False
    logger.info(f"✓ Column order correct: {columns[:5]}")
    
    # Verify data integrity (spot check)
    for orig_row in original_data["conversations"][:5]:
        new_row = new_conn.execute(
            "SELECT id, type, status, focus FROM conversations WHERE id = ?",
            (orig_row["id"],)
        ).fetchone()
        
        if not new_row:
            logger.error(f"❌ Missing conversation: {orig_row['id']}")
            return False
        
        if new_row["type"] != orig_row["type"]:
            logger.error(f"❌ Data mismatch for {orig_row['id']}")
            return False
    
    logger.info(f"✓ Data integrity verified (spot checked {min(5, len(original_data['conversations']))} rows)")
    
    return True


def migrate(dry_run: bool = False) -> int:
    """Execute migration"""
    try:
        if not DB_PATH.exists():
            logger.error(f"Database not found: {DB_PATH}")
            return 1
        
        logger.info(f"Starting migration: {DB_PATH}")
        logger.info(f"Dry run: {dry_run}")
        
        # Step 1: Backup
        logger.info("\n[Step 1/5] Creating backup...")
        backup_path = backup_database(dry_run)
        
        if dry_run:
            logger.info("\n[DRY RUN] Migration steps:")
            logger.info("  1. Backup database ✓")
            logger.info("  2. Extract all data from tables")
            logger.info("  3. Drop old tables")
            logger.info("  4. Create new tables with correct column order")
            logger.info("  5. Restore all data")
            logger.info("  6. Verify data integrity")
            logger.info("\nRun without --dry-run to execute")
            return 0
        
        # Step 2: Extract data
        logger.info("\n[Step 2/5] Extracting data...")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        original_data = extract_data(conn)
        conn.close()
        
        # Step 3: Drop tables and recreate
        logger.info("\n[Step 3/5] Recreating tables...")
        conn = sqlite3.connect(DB_PATH)
        
        # Drop tables
        conn.execute("DROP TABLE IF EXISTS decisions")
        conn.execute("DROP TABLE IF EXISTS learnings")
        conn.execute("DROP TABLE IF EXISTS issues")
        conn.execute("DROP TABLE IF EXISTS artifacts")
        conn.execute("DROP TABLE IF EXISTS conversations")
        logger.info("  Dropped old tables")
        
        # Import full schema from conversation_registry
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from conversation_registry import SCHEMA
        
        conn.executescript(SCHEMA)
        conn.commit()
        logger.info("  Created new tables")
        
        # Step 4: Restore data
        logger.info("\n[Step 4/5] Restoring data...")
        restore_data(conn, original_data)
        conn.commit()
        
        # Step 5: Verify
        logger.info("\n[Step 5/5] Verification...")
        if not verify_migration(original_data, conn):
            conn.close()
            logger.error("\n❌ Migration verification failed!")
            logger.error(f"Restore backup: cp {backup_path} {DB_PATH}")
            return 1
        
        conn.close()
        
        logger.info("\n" + "="*80)
        logger.info("✅ Migration completed successfully!")
        logger.info(f"   Backup saved: {backup_path}")
        logger.info(f"   Migrated: {len(original_data['conversations'])} conversations")
        logger.info("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}", exc_info=True)
        logger.error(f"\nRestore backup if needed: cp {backup_path} {DB_PATH}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Migrate conversation registry schema")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    
    args = parser.parse_args()
    
    return migrate(dry_run=args.dry_run)


if __name__ == "__main__":
    exit(main())
