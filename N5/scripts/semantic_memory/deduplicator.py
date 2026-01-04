#!/usr/bin/env python3
"""Semantic Memory Deduplicator - Ensures unique positions in brain.db.

Identifies and removes duplicate entries in the semantic memory database,
using content similarity and resource path analysis.

Part of N5 System Optimization - Workstream 4.

Usage:
    python deduplicator.py report       # Show duplicate analysis
    python deduplicator.py deduplicate  # Remove duplicates (keep_latest)
    python deduplicator.py add-indexes  # Add performance indexes
"""

import argparse
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Paths
WORKSPACE = Path("/home/workspace")
BRAIN_DB = WORKSPACE / "N5/cognition/brain.db"
BACKUP_DIR = WORKSPACE / "N5/cognition/backups"


@dataclass
class DuplicateReport:
    """Report on a set of duplicate entries."""
    content_hash: str
    resource_paths: List[str]
    block_ids: List[str]
    occurrences: int
    content_preview: str
    timestamps: List[str]


@dataclass
class DeduplicationStats:
    """Statistics from a deduplication run."""
    duplicates_found: int
    entries_removed: int
    entries_kept: int
    strategy: str
    elapsed_seconds: float


class SemanticDeduplicator:
    """Manages deduplication of semantic memory entries.

    The brain.db schema:
    - resources: id, path, hash, last_indexed_at, content_date
    - blocks: id, resource_id, block_type, content, start_line, end_line, token_count, content_date
    - vectors: block_id, embedding
    - tags: resource_id, tag

    Deduplication strategies:
    - Content hash: Find blocks with identical content
    - Resource path: Find resources with duplicate paths
    - Semantic similarity: Find blocks with similar embeddings (requires numpy)
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the deduplicator.

        Args:
            db_path: Path to brain.db. Defaults to canonical location.
        """
        self.db_path = db_path or BRAIN_DB
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def find_content_duplicates(self, block_type: Optional[str] = None) -> List[DuplicateReport]:
        """Find blocks with identical content.

        Args:
            block_type: Optional filter by block type (e.g., 'position', 'text')

        Returns:
            List of DuplicateReport for each set of duplicates.
        """
        type_filter = f"WHERE b.block_type = '{block_type}'" if block_type else ""

        query = f"""
            WITH content_hashes AS (
                SELECT
                    b.id as block_id,
                    b.content,
                    r.path as resource_path,
                    b.content_date,
                    LENGTH(b.content) as content_length
                FROM blocks b
                JOIN resources r ON b.resource_id = r.id
                {type_filter}
            ),
            duplicate_contents AS (
                SELECT content, COUNT(*) as cnt
                FROM content_hashes
                GROUP BY content
                HAVING cnt > 1
            )
            SELECT
                ch.block_id,
                ch.content,
                ch.resource_path,
                ch.content_date
            FROM content_hashes ch
            JOIN duplicate_contents dc ON ch.content = dc.content
            ORDER BY ch.content, ch.content_date DESC
        """

        rows = self.conn.execute(query).fetchall()

        # Group by content
        content_groups: Dict[str, List[dict]] = {}
        for row in rows:
            content = row['content']
            if content not in content_groups:
                content_groups[content] = []
            content_groups[content].append({
                'block_id': row['block_id'],
                'resource_path': row['resource_path'],
                'content_date': row['content_date']
            })

        # Create reports
        reports = []
        for content, entries in content_groups.items():
            content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
            reports.append(DuplicateReport(
                content_hash=content_hash,
                resource_paths=[e['resource_path'] for e in entries],
                block_ids=[e['block_id'] for e in entries],
                occurrences=len(entries),
                content_preview=content[:100] + "..." if len(content) > 100 else content,
                timestamps=[e['content_date'] or '' for e in entries]
            ))

        return reports

    def find_path_duplicates(self) -> List[DuplicateReport]:
        """Find resources with duplicate paths (should not happen but check)."""
        query = """
            SELECT path, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
            FROM resources
            GROUP BY path
            HAVING cnt > 1
        """

        rows = self.conn.execute(query).fetchall()
        reports = []

        for row in rows:
            reports.append(DuplicateReport(
                content_hash=hashlib.md5(row['path'].encode()).hexdigest()[:12],
                resource_paths=[row['path']],
                block_ids=row['ids'].split(','),
                occurrences=row['cnt'],
                content_preview=f"Duplicate path: {row['path']}",
                timestamps=[]
            ))

        return reports

    def deduplicate(
        self,
        strategy: str = 'keep_latest',
        block_type: Optional[str] = None,
        dry_run: bool = False
    ) -> DeduplicationStats:
        """Remove duplicate entries.

        Args:
            strategy: 'keep_latest' or 'keep_earliest'
            block_type: Optional filter by block type
            dry_run: If True, report but don't delete

        Returns:
            DeduplicationStats with results.
        """
        start_time = datetime.now()
        duplicates = self.find_content_duplicates(block_type)

        entries_removed = 0
        entries_kept = 0

        for dup in duplicates:
            # Sort by timestamp
            indexed_entries = list(zip(dup.block_ids, dup.timestamps))

            # Sort by timestamp (None values sorted to end)
            indexed_entries.sort(
                key=lambda x: x[1] if x[1] else '0000-00-00',
                reverse=(strategy == 'keep_latest')
            )

            # Keep first, remove rest
            keep_id = indexed_entries[0][0]
            remove_ids = [e[0] for e in indexed_entries[1:]]

            entries_kept += 1
            entries_removed += len(remove_ids)

            if not dry_run and remove_ids:
                # Delete blocks (cascades to vectors due to foreign key)
                placeholders = ','.join('?' * len(remove_ids))
                self.conn.execute(
                    f"DELETE FROM blocks WHERE id IN ({placeholders})",
                    remove_ids
                )

        if not dry_run:
            self.conn.commit()

        elapsed = (datetime.now() - start_time).total_seconds()

        return DeduplicationStats(
            duplicates_found=len(duplicates),
            entries_removed=entries_removed,
            entries_kept=entries_kept,
            strategy=strategy,
            elapsed_seconds=elapsed
        )

    def add_performance_indexes(self) -> List[str]:
        """Add indexes to improve query performance.

        Returns:
            List of indexes created.
        """
        indexes = [
            # Index for path-based partitioning
            ("idx_resources_path_prefix", """
                CREATE INDEX IF NOT EXISTS idx_resources_path_prefix
                ON resources(path)
            """),
            # Index for time-based queries
            ("idx_blocks_content_date", """
                CREATE INDEX IF NOT EXISTS idx_blocks_content_date
                ON blocks(content_date)
            """),
            # Index for block type filtering
            ("idx_blocks_type", """
                CREATE INDEX IF NOT EXISTS idx_blocks_type
                ON blocks(block_type)
            """),
            # Index for resource lookups
            ("idx_blocks_resource", """
                CREATE INDEX IF NOT EXISTS idx_blocks_resource
                ON blocks(resource_id)
            """),
        ]

        created = []
        for name, sql in indexes:
            try:
                self.conn.execute(sql)
                created.append(name)
            except sqlite3.OperationalError as e:
                if "already exists" not in str(e):
                    raise

        self.conn.commit()
        return created

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        stats = {}

        stats['total_resources'] = self.conn.execute(
            "SELECT COUNT(*) FROM resources"
        ).fetchone()[0]

        stats['total_blocks'] = self.conn.execute(
            "SELECT COUNT(*) FROM blocks"
        ).fetchone()[0]

        stats['position_blocks'] = self.conn.execute(
            "SELECT COUNT(*) FROM blocks WHERE block_type = 'position'"
        ).fetchone()[0]

        stats['text_blocks'] = self.conn.execute(
            "SELECT COUNT(*) FROM blocks WHERE block_type = 'text'"
        ).fetchone()[0]

        stats['total_vectors'] = self.conn.execute(
            "SELECT COUNT(*) FROM vectors"
        ).fetchone()[0]

        # Check for content duplicates
        content_dups = self.conn.execute("""
            SELECT COUNT(*) FROM (
                SELECT content FROM blocks GROUP BY content HAVING COUNT(*) > 1
            )
        """).fetchone()[0]
        stats['content_duplicate_sets'] = content_dups

        return stats

    def backup_database(self) -> Path:
        """Create a backup of the database before modifications.

        Returns:
            Path to backup file.
        """
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"brain_{timestamp}.db"

        # Use SQLite backup API
        backup_conn = sqlite3.connect(backup_path)
        self.conn.backup(backup_conn)
        backup_conn.close()

        return backup_path

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Semantic Memory Deduplicator"
    )
    parser.add_argument(
        'command',
        choices=['report', 'deduplicate', 'add-indexes', 'stats', 'backup'],
        help="Command to execute"
    )
    parser.add_argument(
        '--block-type',
        choices=['position', 'text'],
        help="Filter by block type"
    )
    parser.add_argument(
        '--strategy',
        choices=['keep_latest', 'keep_earliest'],
        default='keep_latest',
        help="Deduplication strategy"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Report without making changes"
    )
    parser.add_argument(
        '--db',
        type=Path,
        help="Path to database"
    )
    args = parser.parse_args()

    dedup = SemanticDeduplicator(db_path=args.db)

    try:
        if args.command == 'report':
            print("Analyzing duplicates...")
            duplicates = dedup.find_content_duplicates(args.block_type)

            if not duplicates:
                print("No duplicates found!")
                return

            print(f"\nFound {len(duplicates)} sets of duplicates:\n")
            for i, dup in enumerate(duplicates[:20], 1):
                print(f"{i}. Hash: {dup.content_hash}")
                print(f"   Occurrences: {dup.occurrences}")
                print(f"   Preview: {dup.content_preview}")
                print(f"   Paths: {', '.join(dup.resource_paths[:3])}")
                if len(dup.resource_paths) > 3:
                    print(f"   ... and {len(dup.resource_paths) - 3} more")
                print()

            if len(duplicates) > 20:
                print(f"... and {len(duplicates) - 20} more duplicate sets")

        elif args.command == 'deduplicate':
            if not args.dry_run:
                print("Creating backup...")
                backup_path = dedup.backup_database()
                print(f"Backup created: {backup_path}")

            print(f"\nDeduplicating (strategy: {args.strategy})...")
            stats = dedup.deduplicate(
                strategy=args.strategy,
                block_type=args.block_type,
                dry_run=args.dry_run
            )

            print(f"\nResults {'(DRY RUN)' if args.dry_run else ''}:")
            print(f"  Duplicate sets found: {stats.duplicates_found}")
            print(f"  Entries removed: {stats.entries_removed}")
            print(f"  Entries kept: {stats.entries_kept}")
            print(f"  Elapsed: {stats.elapsed_seconds:.2f}s")

        elif args.command == 'add-indexes':
            print("Adding performance indexes...")
            created = dedup.add_performance_indexes()
            print(f"Created {len(created)} indexes:")
            for idx in created:
                print(f"  - {idx}")

        elif args.command == 'stats':
            stats = dedup.get_stats()
            print("Database Statistics:")
            print(f"  Total resources: {stats['total_resources']}")
            print(f"  Total blocks: {stats['total_blocks']}")
            print(f"    Position blocks: {stats['position_blocks']}")
            print(f"    Text blocks: {stats['text_blocks']}")
            print(f"  Total vectors: {stats['total_vectors']}")
            print(f"  Content duplicate sets: {stats['content_duplicate_sets']}")

        elif args.command == 'backup':
            print("Creating backup...")
            backup_path = dedup.backup_database()
            print(f"Backup created: {backup_path}")

    finally:
        dedup.close()


if __name__ == "__main__":
    main()
