#!/usr/bin/env python3
"""CRM Index Builder - Builds and maintains SQLite indexes for O(1) CRM lookups.

Creates and populates the email_index and name_variants tables used by
CRMLookupService for fast participant resolution.

Part of N5 System Optimization - Workstream 1.

Usage:
    python crm_index_builder.py rebuild    # Full rebuild from profiles
    python crm_index_builder.py update     # Incremental update
    python crm_index_builder.py stats      # Show index statistics
"""

import argparse
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Import canonical paths
import sys
sys.path.insert(0, str(Path(__file__).parent))
from crm_paths import CRM_DB, CRM_INDEX, CRM_INDIVIDUALS


class CRMIndexBuilder:
    """Builds and maintains CRM lookup indexes."""

    SCHEMA = """
    -- Email index for O(1) email lookups
    CREATE TABLE IF NOT EXISTS email_index (
        email TEXT PRIMARY KEY COLLATE NOCASE,
        slug TEXT NOT NULL,
        display_name TEXT,
        company TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    -- Name variants for normalized name matching
    CREATE TABLE IF NOT EXISTS name_variants (
        normalized_name TEXT NOT NULL COLLATE NOCASE,
        slug TEXT NOT NULL,
        display_name TEXT,
        variant_type TEXT,  -- 'full', 'first_last', 'last_first', 'first_only'
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (normalized_name, slug)
    );

    -- Index for fast name lookups
    CREATE INDEX IF NOT EXISTS idx_name_variants_name
    ON name_variants(normalized_name COLLATE NOCASE);

    -- Index for slug lookups (useful for updates)
    CREATE INDEX IF NOT EXISTS idx_email_index_slug
    ON email_index(slug);

    CREATE INDEX IF NOT EXISTS idx_name_variants_slug
    ON name_variants(slug);
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the builder.

        Args:
            db_path: Path to SQLite database. Defaults to canonical CRM_DB.
        """
        self.db_path = db_path or CRM_DB
        self.index_path = CRM_INDEX
        self.profiles_dir = CRM_INDIVIDUALS
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._conn is None:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def ensure_schema(self) -> None:
        """Ensure lookup tables exist."""
        self.conn.executescript(self.SCHEMA)
        self.conn.commit()

    def rebuild_full(self) -> Dict[str, int]:
        """Full rebuild of index from index.jsonl and profile files.

        Returns:
            Dict with counts of records processed and indexed.
        """
        print(f"Starting full rebuild from {self.index_path}")
        start_time = datetime.now()

        # Ensure schema
        self.ensure_schema()

        # Clear existing data
        self.conn.execute("DELETE FROM email_index")
        self.conn.execute("DELETE FROM name_variants")
        self.conn.commit()

        stats = {
            'profiles_processed': 0,
            'emails_indexed': 0,
            'name_variants_indexed': 0,
            'skipped_no_email': 0,
            'errors': 0
        }

        # Load from index.jsonl
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                        self._index_record(record, stats)
                        stats['profiles_processed'] += 1
                    except json.JSONDecodeError as e:
                        print(f"  Warning: Invalid JSON line: {e}")
                        stats['errors'] += 1
                    except Exception as e:
                        print(f"  Warning: Error processing record: {e}")
                        stats['errors'] += 1

        self.conn.commit()

        elapsed = (datetime.now() - start_time).total_seconds()
        stats['elapsed_seconds'] = elapsed

        print(f"Rebuild complete in {elapsed:.2f}s")
        print(f"  Profiles processed: {stats['profiles_processed']}")
        print(f"  Emails indexed: {stats['emails_indexed']}")
        print(f"  Name variants indexed: {stats['name_variants_indexed']}")

        return stats

    def _index_record(self, record: Dict, stats: Dict) -> None:
        """Index a single record from index.jsonl.

        Args:
            record: Dict with person_id, name, email, organization, path
            stats: Stats dict to update
        """
        slug = record.get('person_id', '')
        name = record.get('name', '')
        email = record.get('email')
        company = record.get('organization')

        if not slug:
            return

        # Index email if present
        if email and email.strip():
            email_normalized = email.lower().strip()
            try:
                self.conn.execute(
                    """INSERT OR REPLACE INTO email_index
                       (email, slug, display_name, company, updated_at)
                       VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                    (email_normalized, slug, name, company)
                )
                stats['emails_indexed'] += 1
            except sqlite3.IntegrityError:
                pass  # Duplicate email, skip
        else:
            stats['skipped_no_email'] += 1

        # Generate and index name variants
        variants = self._generate_name_variants(name, slug)
        for normalized, display, variant_type in variants:
            try:
                self.conn.execute(
                    """INSERT OR REPLACE INTO name_variants
                       (normalized_name, slug, display_name, variant_type)
                       VALUES (?, ?, ?, ?)""",
                    (normalized, slug, display, variant_type)
                )
                stats['name_variants_indexed'] += 1
            except sqlite3.IntegrityError:
                pass  # Duplicate variant, skip

    def _generate_name_variants(
        self,
        display_name: str,
        slug: str
    ) -> List[Tuple[str, str, str]]:
        """Generate all searchable name variants.

        Returns:
            List of (normalized_name, display_name, variant_type) tuples
        """
        variants = []

        if not display_name:
            # Use slug as fallback
            normalized = self._normalize_name(slug.replace('-', ' '))
            if normalized:
                variants.append((normalized, slug, 'slug'))
            return variants

        # Full normalized name
        normalized = self._normalize_name(display_name)
        if normalized:
            variants.append((normalized, display_name, 'full'))

        # Split into parts
        parts = normalized.split() if normalized else []

        if len(parts) >= 2:
            # First + Last (e.g., "victor hu")
            first_last = f"{parts[0]} {parts[-1]}"
            if first_last != normalized:
                variants.append((first_last, display_name, 'first_last'))

            # Last + First (e.g., "hu victor")
            last_first = f"{parts[-1]} {parts[0]}"
            variants.append((last_first, display_name, 'last_first'))

            # First name only (lower confidence)
            if len(parts[0]) >= 3:  # Skip very short first names
                variants.append((parts[0], display_name, 'first_only'))

        elif len(parts) == 1 and len(parts[0]) >= 3:
            # Single name (treat as first_only)
            variants.append((parts[0], display_name, 'first_only'))

        return variants

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize name for matching."""
        if not name:
            return ""

        # Lowercase and strip
        name = name.lower().strip()

        # Remove common suffixes
        name = re.sub(r'\s+(jr|sr|ii|iii|iv|phd|md|esq)\.?$', '', name, flags=re.IGNORECASE)

        # Remove punctuation except hyphens
        name = re.sub(r'[^\w\s-]', '', name)

        # Collapse whitespace
        name = re.sub(r'\s+', ' ', name)

        return name.strip()

    def update_incremental(self, changed_slugs: Optional[Set[str]] = None) -> Dict[str, int]:
        """Update index for specific profiles.

        Args:
            changed_slugs: Set of slugs to update. If None, detects changes.

        Returns:
            Dict with counts of records updated.
        """
        self.ensure_schema()

        stats = {
            'profiles_checked': 0,
            'profiles_updated': 0,
            'emails_added': 0,
            'name_variants_added': 0
        }

        # If no specific slugs, do full rebuild
        if changed_slugs is None:
            return self.rebuild_full()

        # Load current index
        if not self.index_path.exists():
            print("Index file not found, doing full rebuild")
            return self.rebuild_full()

        index_records = {}
        with open(self.index_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    slug = record.get('person_id')
                    if slug:
                        index_records[slug] = record
                except json.JSONDecodeError:
                    pass

        # Update specified slugs
        for slug in changed_slugs:
            stats['profiles_checked'] += 1

            if slug in index_records:
                # Remove old entries
                self.conn.execute("DELETE FROM email_index WHERE slug = ?", (slug,))
                self.conn.execute("DELETE FROM name_variants WHERE slug = ?", (slug,))

                # Re-index
                sub_stats = {'emails_indexed': 0, 'name_variants_indexed': 0, 'skipped_no_email': 0}
                self._index_record(index_records[slug], sub_stats)

                stats['profiles_updated'] += 1
                stats['emails_added'] += sub_stats['emails_indexed']
                stats['name_variants_added'] += sub_stats['name_variants_indexed']

        self.conn.commit()
        return stats

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the lookup index."""
        self.ensure_schema()

        email_count = self.conn.execute(
            "SELECT COUNT(*) FROM email_index"
        ).fetchone()[0]

        name_count = self.conn.execute(
            "SELECT COUNT(*) FROM name_variants"
        ).fetchone()[0]

        slug_count = self.conn.execute(
            "SELECT COUNT(DISTINCT slug) FROM name_variants"
        ).fetchone()[0]

        variant_types = self.conn.execute(
            """SELECT variant_type, COUNT(*) as count
               FROM name_variants
               GROUP BY variant_type"""
        ).fetchall()

        return {
            'emails_indexed': email_count,
            'name_variants_indexed': name_count,
            'unique_profiles': slug_count,
            'variant_breakdown': {row['variant_type']: row['count'] for row in variant_types}
        }

    def verify_integrity(self) -> Dict[str, List[str]]:
        """Verify index integrity against source data.

        Returns:
            Dict with lists of issues found.
        """
        issues = {
            'missing_in_index': [],
            'orphaned_in_index': [],
            'email_mismatches': []
        }

        # Load source index
        source_slugs = set()
        source_emails = {}

        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        slug = record.get('person_id')
                        if slug:
                            source_slugs.add(slug)
                            email = record.get('email')
                            if email:
                                source_emails[slug] = email.lower()
                    except json.JSONDecodeError:
                        pass

        # Check indexed slugs
        indexed_slugs = set()
        for row in self.conn.execute("SELECT DISTINCT slug FROM name_variants"):
            indexed_slugs.add(row['slug'])

        # Find missing
        for slug in source_slugs - indexed_slugs:
            issues['missing_in_index'].append(slug)

        # Find orphaned
        for slug in indexed_slugs - source_slugs:
            issues['orphaned_in_index'].append(slug)

        # Verify emails
        for row in self.conn.execute("SELECT email, slug FROM email_index"):
            slug = row['slug']
            indexed_email = row['email']
            source_email = source_emails.get(slug)
            if source_email and indexed_email != source_email:
                issues['email_mismatches'].append(f"{slug}: {indexed_email} != {source_email}")

        return issues

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CRM Index Builder - Build and maintain lookup indexes"
    )
    parser.add_argument(
        'command',
        choices=['rebuild', 'update', 'stats', 'verify'],
        help="Command to execute"
    )
    parser.add_argument(
        '--db',
        type=Path,
        help="Path to database (defaults to canonical CRM_DB)"
    )
    args = parser.parse_args()

    builder = CRMIndexBuilder(db_path=args.db)

    try:
        if args.command == 'rebuild':
            stats = builder.rebuild_full()
            print(f"\nFinal stats: {json.dumps(stats, indent=2)}")

        elif args.command == 'update':
            stats = builder.update_incremental()
            print(f"\nUpdate stats: {json.dumps(stats, indent=2)}")

        elif args.command == 'stats':
            stats = builder.get_stats()
            print("CRM Lookup Index Statistics:")
            print(f"  Emails indexed: {stats['emails_indexed']}")
            print(f"  Name variants indexed: {stats['name_variants_indexed']}")
            print(f"  Unique profiles: {stats['unique_profiles']}")
            print(f"  Variant breakdown:")
            for vtype, count in stats.get('variant_breakdown', {}).items():
                print(f"    {vtype}: {count}")

        elif args.command == 'verify':
            issues = builder.verify_integrity()
            if any(issues.values()):
                print("Integrity issues found:")
                for issue_type, items in issues.items():
                    if items:
                        print(f"  {issue_type}: {len(items)}")
                        for item in items[:5]:
                            print(f"    - {item}")
                        if len(items) > 5:
                            print(f"    ... and {len(items) - 5} more")
            else:
                print("Index integrity verified - no issues found")

    finally:
        builder.close()


if __name__ == "__main__":
    main()
