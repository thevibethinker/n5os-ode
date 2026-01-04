#!/usr/bin/env python3
"""CRM Lookup Service - O(1) lookups for participant resolution.

Replaces the O(n) linear scan in meeting_crm_linker.py with SQLite-backed
indexed lookups for email and normalized name matching.

Part of N5 System Optimization - Workstream 1.
"""

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

# Import canonical paths
import sys
sys.path.insert(0, str(Path(__file__).parent))
from crm_paths import CRM_DB, CRM_INDIVIDUALS


@dataclass
class CRMLookupResult:
    """Result of a CRM lookup operation."""
    slug: str
    display_name: str
    company: Optional[str]
    email: Optional[str]
    match_type: str  # 'email_exact', 'name_exact', 'name_fuzzy'
    confidence: float  # 0.0-1.0


class CRMLookupService:
    """Fast CRM lookups using SQLite indexes.

    Provides O(1) lookups by email and O(1) lookups by normalized name,
    replacing the previous O(n) linear scan through all index entries.

    Usage:
        service = CRMLookupService()
        result = service.lookup_participant("Victor Hu", "victor@lumoscapitalgroup.com")
        if result:
            print(f"Found: {result.slug} (confidence: {result.confidence})")
    """

    # Schema for lookup tables (added to existing crm.db)
    SCHEMA = """
    -- Email index for O(1) email lookups
    CREATE TABLE IF NOT EXISTS email_index (
        email TEXT PRIMARY KEY COLLATE NOCASE,
        slug TEXT NOT NULL,
        display_name TEXT,
        company TEXT
    );

    -- Name variants for normalized name matching
    CREATE TABLE IF NOT EXISTS name_variants (
        normalized_name TEXT NOT NULL COLLATE NOCASE,
        slug TEXT NOT NULL,
        display_name TEXT,
        variant_type TEXT,  -- 'full', 'first_last', 'last_first', 'first_only'
        PRIMARY KEY (normalized_name, slug)
    );

    -- Index for fast name lookups
    CREATE INDEX IF NOT EXISTS idx_name_variants_name
    ON name_variants(normalized_name COLLATE NOCASE);
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the lookup service.

        Args:
            db_path: Path to SQLite database. Defaults to canonical CRM_DB.
        """
        self.db_path = db_path or CRM_DB
        self._conn: Optional[sqlite3.Connection] = None
        self._tables_verified = False

    @property
    def conn(self) -> sqlite3.Connection:
        """Get database connection, creating tables if needed."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row

            # Verify lookup tables exist
            if not self._tables_verified:
                self._ensure_tables()
                self._tables_verified = True

        return self._conn

    def _ensure_tables(self) -> None:
        """Ensure lookup tables exist in database."""
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='email_index'"
        )
        if cursor.fetchone() is None:
            self.conn.executescript(self.SCHEMA)
            self.conn.commit()

    def lookup_by_email(self, email: str) -> Optional[CRMLookupResult]:
        """O(1) email lookup. Highest confidence match.

        Args:
            email: Email address to look up (case-insensitive).

        Returns:
            CRMLookupResult if found, None otherwise.
        """
        if not email:
            return None

        email_normalized = email.lower().strip()

        row = self.conn.execute(
            """SELECT slug, display_name, company, email
               FROM email_index
               WHERE email = ?""",
            (email_normalized,)
        ).fetchone()

        if row:
            return CRMLookupResult(
                slug=row['slug'],
                display_name=row['display_name'] or row['slug'],
                company=row['company'],
                email=row['email'],
                match_type='email_exact',
                confidence=1.0
            )
        return None

    def lookup_by_name(self, name: str) -> Optional[CRMLookupResult]:
        """Name-based lookup with normalized matching.

        Args:
            name: Person name to look up.

        Returns:
            CRMLookupResult if found, None otherwise.
        """
        if not name:
            return None

        normalized = self._normalize_name(name)
        if not normalized:
            return None

        # Try exact normalized match first
        row = self.conn.execute(
            """SELECT nv.slug, nv.display_name, nv.variant_type, e.company, e.email
               FROM name_variants nv
               LEFT JOIN email_index e ON nv.slug = e.slug
               WHERE nv.normalized_name = ?
               ORDER BY
                   CASE nv.variant_type
                       WHEN 'full' THEN 1
                       WHEN 'first_last' THEN 2
                       WHEN 'last_first' THEN 3
                       ELSE 4
                   END
               LIMIT 1""",
            (normalized,)
        ).fetchone()

        if row:
            # Confidence based on match type
            confidence_map = {
                'full': 0.95,
                'first_last': 0.90,
                'last_first': 0.85,
                'first_only': 0.70
            }
            confidence = confidence_map.get(row['variant_type'], 0.80)

            return CRMLookupResult(
                slug=row['slug'],
                display_name=row['display_name'] or row['slug'],
                company=row['company'],
                email=row['email'],
                match_type='name_exact',
                confidence=confidence
            )
        return None

    def lookup_participant(
        self,
        name: str,
        email: Optional[str] = None
    ) -> Optional[CRMLookupResult]:
        """Combined lookup: try email first (highest confidence), then name.

        Args:
            name: Person name.
            email: Optional email address (preferred if available).

        Returns:
            CRMLookupResult if found, None otherwise.
        """
        # Email lookup has highest confidence
        if email:
            result = self.lookup_by_email(email)
            if result:
                return result

        # Fall back to name lookup
        return self.lookup_by_name(name)

    def batch_lookup(
        self,
        participants: List[Dict[str, str]]
    ) -> Dict[str, CRMLookupResult]:
        """Batch lookup for multiple participants.

        Args:
            participants: List of dicts with 'name' and optional 'email' keys.

        Returns:
            Dict mapping participant names to lookup results.
        """
        results = {}
        for p in participants:
            name = p.get('name', '')
            email = p.get('email')
            result = self.lookup_participant(name, email)
            if result:
                results[name] = result
        return results

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the lookup index.

        Returns:
            Dict with counts of emails and name variants indexed.
        """
        email_count = self.conn.execute(
            "SELECT COUNT(*) FROM email_index"
        ).fetchone()[0]

        name_count = self.conn.execute(
            "SELECT COUNT(*) FROM name_variants"
        ).fetchone()[0]

        slug_count = self.conn.execute(
            "SELECT COUNT(DISTINCT slug) FROM name_variants"
        ).fetchone()[0]

        return {
            'emails_indexed': email_count,
            'name_variants_indexed': name_count,
            'unique_profiles': slug_count
        }

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize name for matching.

        Lowercase, remove punctuation except hyphens, collapse whitespace.
        """
        if not name:
            return ""

        # Lowercase and strip
        name = name.lower().strip()

        # Remove common suffixes/prefixes
        name = re.sub(r'\s+(jr|sr|ii|iii|iv|phd|md|esq)\.?$', '', name, flags=re.IGNORECASE)

        # Remove punctuation except hyphens (preserve hyphenated names)
        name = re.sub(r'[^\w\s-]', '', name)

        # Collapse whitespace
        name = re.sub(r'\s+', ' ', name)

        return name.strip()


def main():
    """CLI for testing lookups."""
    import argparse

    parser = argparse.ArgumentParser(description="CRM Lookup Service")
    parser.add_argument('--email', help="Look up by email")
    parser.add_argument('--name', help="Look up by name")
    parser.add_argument('--stats', action='store_true', help="Show index stats")
    args = parser.parse_args()

    service = CRMLookupService()

    if args.stats:
        stats = service.get_stats()
        print(f"CRM Lookup Index Stats:")
        print(f"  Emails indexed: {stats['emails_indexed']}")
        print(f"  Name variants: {stats['name_variants_indexed']}")
        print(f"  Unique profiles: {stats['unique_profiles']}")
        return

    if args.email:
        result = service.lookup_by_email(args.email)
        if result:
            print(f"Found: {result.slug}")
            print(f"  Display name: {result.display_name}")
            print(f"  Company: {result.company}")
            print(f"  Confidence: {result.confidence}")
        else:
            print(f"No match found for email: {args.email}")
        return

    if args.name:
        result = service.lookup_by_name(args.name)
        if result:
            print(f"Found: {result.slug}")
            print(f"  Display name: {result.display_name}")
            print(f"  Company: {result.company}")
            print(f"  Match type: {result.match_type}")
            print(f"  Confidence: {result.confidence}")
        else:
            print(f"No match found for name: {args.name}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
