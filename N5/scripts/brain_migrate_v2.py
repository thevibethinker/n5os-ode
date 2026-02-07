#!/usr/bin/env python3
"""
N5 Brain Migration v2: Temporal Tracking + Graph Schema

Adds:
- Temporal columns to blocks and resources tables
- Graph tables (entities, relationships)

Safe to run multiple times (idempotent).
"""

import argparse
import sqlite3
import shutil
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger(__name__)

BRAIN_DB = Path("/home/workspace/N5/cognition/brain.db")
VECTORS_DB = Path("/home/workspace/N5/cognition/vectors_v2.db")
BACKUP_DIR = Path("/home/workspace/N5/cognition/backups")

# Temporal schema additions
TEMPORAL_MIGRATIONS = [
    # blocks table
    ("blocks", "indexed_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
    ("blocks", "valid_from", "TIMESTAMP"),
    ("blocks", "valid_until", "TIMESTAMP"),
    ("blocks", "supersedes_block_id", "TEXT"),
    # resources table
    ("resources", "first_indexed_at", "TIMESTAMP"),
    ("resources", "version", "INTEGER DEFAULT 1"),
]

# Graph schema (brain.db only)
GRAPH_SCHEMA = """
-- Entity storage
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    canonical_name TEXT,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mention_count INTEGER DEFAULT 1,
    source_block_id TEXT,
    metadata JSON,
    FOREIGN KEY (source_block_id) REFERENCES blocks(id)
);

-- Relationship storage
CREATE TABLE IF NOT EXISTS relationships (
    id TEXT PRIMARY KEY,
    from_entity_id TEXT NOT NULL,
    to_entity_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    context TEXT,
    source_block_id TEXT,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_entity_id) REFERENCES entities(id),
    FOREIGN KEY (to_entity_id) REFERENCES entities(id),
    FOREIGN KEY (source_block_id) REFERENCES blocks(id)
);

-- Indexes for graph queries
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(canonical_name);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relation_type);
"""


def backup_database(db_path: Path, dry_run: bool = False) -> Path:
    """Create timestamped backup of database."""
    if not db_path.exists():
        LOG.warning(f"Database not found: {db_path}")
        return None
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{db_path.stem}_{timestamp}.db"
    
    if dry_run:
        LOG.info(f"[DRY RUN] Would backup {db_path} → {backup_path}")
        return backup_path
    
    shutil.copy2(db_path, backup_path)
    LOG.info(f"Backup created: {backup_path}")
    return backup_path


def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """Check if a column exists in a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    """Check if a table exists."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None


def migrate_temporal(conn: sqlite3.Connection, db_name: str, dry_run: bool = False) -> dict:
    """Add temporal columns to blocks and resources tables."""
    results = {"added": [], "skipped": [], "errors": []}
    
    for table, column, col_type in TEMPORAL_MIGRATIONS:
        if not table_exists(conn, table):
            LOG.warning(f"[{db_name}] Table '{table}' does not exist, skipping")
            results["skipped"].append(f"{table}.{column} (table missing)")
            continue
            
        if column_exists(conn, table, column):
            LOG.info(f"[{db_name}] Column '{table}.{column}' already exists")
            results["skipped"].append(f"{table}.{column} (exists)")
            continue
        
        sql = f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"
        
        if dry_run:
            LOG.info(f"[DRY RUN] [{db_name}] Would execute: {sql}")
            results["added"].append(f"{table}.{column}")
        else:
            try:
                conn.execute(sql)
                LOG.info(f"[{db_name}] Added column: {table}.{column}")
                results["added"].append(f"{table}.{column}")
            except Exception as e:
                LOG.error(f"[{db_name}] Failed to add {table}.{column}: {e}")
                results["errors"].append(f"{table}.{column}: {e}")
    
    if not dry_run:
        conn.commit()
    
    return results


def migrate_graph(conn: sqlite3.Connection, dry_run: bool = False) -> dict:
    """Create graph tables (entities, relationships) in brain.db."""
    results = {"created": [], "skipped": [], "errors": []}
    
    # Check if tables exist
    if table_exists(conn, "entities"):
        LOG.info("[brain.db] Table 'entities' already exists")
        results["skipped"].append("entities")
    else:
        if dry_run:
            LOG.info("[DRY RUN] Would create table: entities")
        results["created"].append("entities")
    
    if table_exists(conn, "relationships"):
        LOG.info("[brain.db] Table 'relationships' already exists")
        results["skipped"].append("relationships")
    else:
        if dry_run:
            LOG.info("[DRY RUN] Would create table: relationships")
        results["created"].append("relationships")
    
    if not dry_run and results["created"]:
        try:
            conn.executescript(GRAPH_SCHEMA)
            conn.commit()
            LOG.info("[brain.db] Graph schema created successfully")
        except Exception as e:
            LOG.error(f"[brain.db] Failed to create graph schema: {e}")
            results["errors"].append(str(e))
    
    return results


def backfill_temporal_defaults(conn: sqlite3.Connection, db_name: str, dry_run: bool = False):
    """Backfill temporal fields for existing records."""
    cursor = conn.cursor()
    
    # Backfill resources.first_indexed_at from last_indexed_at where null
    if column_exists(conn, "resources", "first_indexed_at"):
        cursor.execute("SELECT COUNT(*) FROM resources WHERE first_indexed_at IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            if dry_run:
                LOG.info(f"[DRY RUN] [{db_name}] Would backfill {null_count} resources.first_indexed_at values")
            else:
                cursor.execute("""
                    UPDATE resources 
                    SET first_indexed_at = last_indexed_at 
                    WHERE first_indexed_at IS NULL
                """)
                conn.commit()
                LOG.info(f"[{db_name}] Backfilled {null_count} resources.first_indexed_at values")
    
    # Backfill blocks.indexed_at where null
    if column_exists(conn, "blocks", "indexed_at"):
        cursor.execute("SELECT COUNT(*) FROM blocks WHERE indexed_at IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            if dry_run:
                LOG.info(f"[DRY RUN] [{db_name}] Would backfill {null_count} blocks.indexed_at values")
            else:
                cursor.execute("""
                    UPDATE blocks 
                    SET indexed_at = CURRENT_TIMESTAMP 
                    WHERE indexed_at IS NULL
                """)
                conn.commit()
                LOG.info(f"[{db_name}] Backfilled {null_count} blocks.indexed_at values")


def main():
    parser = argparse.ArgumentParser(description="N5 Brain Migration v2")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    parser.add_argument("--skip-backup", action="store_true", help="Skip backup (not recommended)")
    parser.add_argument("--temporal-only", action="store_true", help="Only migrate temporal schema")
    parser.add_argument("--graph-only", action="store_true", help="Only migrate graph schema")
    args = parser.parse_args()
    
    LOG.info("=" * 60)
    LOG.info("N5 Brain Migration v2")
    LOG.info("=" * 60)
    
    if args.dry_run:
        LOG.info("DRY RUN MODE — no changes will be made")
    
    # Backup
    if not args.skip_backup:
        backup_database(BRAIN_DB, args.dry_run)
        backup_database(VECTORS_DB, args.dry_run)
    
    all_results = {}
    
    # Migrate brain.db
    if BRAIN_DB.exists():
        LOG.info(f"\nMigrating: {BRAIN_DB}")
        conn = sqlite3.connect(str(BRAIN_DB))
        
        if not args.graph_only:
            all_results["brain_temporal"] = migrate_temporal(conn, "brain.db", args.dry_run)
            backfill_temporal_defaults(conn, "brain.db", args.dry_run)
        
        if not args.temporal_only:
            all_results["brain_graph"] = migrate_graph(conn, args.dry_run)
        
        conn.close()
    else:
        LOG.warning(f"brain.db not found at {BRAIN_DB}")
    
    # Migrate vectors_v2.db (temporal only, no graph)
    if VECTORS_DB.exists() and not args.graph_only:
        LOG.info(f"\nMigrating: {VECTORS_DB}")
        conn = sqlite3.connect(str(VECTORS_DB))
        
        if not args.graph_only:
            all_results["vectors_temporal"] = migrate_temporal(conn, "vectors_v2.db", args.dry_run)
            backfill_temporal_defaults(conn, "vectors_v2.db", args.dry_run)
        
        conn.close()
    
    # Summary
    LOG.info("\n" + "=" * 60)
    LOG.info("MIGRATION SUMMARY")
    LOG.info("=" * 60)
    
    for key, results in all_results.items():
        LOG.info(f"\n{key}:")
        if results.get("added"):
            LOG.info(f"  Added: {', '.join(results['added'])}")
        if results.get("created"):
            LOG.info(f"  Created: {', '.join(results['created'])}")
        if results.get("skipped"):
            LOG.info(f"  Skipped: {', '.join(results['skipped'])}")
        if results.get("errors"):
            LOG.error(f"  ERRORS: {', '.join(results['errors'])}")
    
    # Check for any errors
    has_errors = any(r.get("errors") for r in all_results.values())
    if has_errors:
        LOG.error("\n⚠️  Migration completed with errors")
        return 1
    
    LOG.info("\n✅ Migration completed successfully")
    return 0


if __name__ == "__main__":
    exit(main())
