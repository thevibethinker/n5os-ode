#!/usr/bin/env python3
"""CRM Lookup Service - O(1) lookups for participant resolution.

Fast email and normalized name matching using SQLite-backed indexed lookups.
Uses unified n5_core.db database with 'people' table.

Updated 2026-01-19: Migrated from crm.db to n5_core.db/people table.

Part of N5 System Optimization.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

# Add workspace to path
sys.path.insert(0, '/home/workspace')

# Import unified database paths
from N5.scripts.db_paths import get_db_connection, N5_CORE_DB, PEOPLE_TABLE


@dataclass
class CRMLookupResult:
    """Result of a CRM lookup operation."""
    person_id: int
    display_name: str
    company: Optional[str]
    email: Optional[str]
    markdown_path: Optional[str]
    match_type: str  # 'email_exact', 'name_exact_unique'
    confidence: float  # 0.0-1.0


class CRMLookupService:
    """Fast CRM lookups using SQLite indexes on people table.

    Provides O(1) lookups by email and efficient lookups by normalized name,
    using the unified n5_core.db database.

    Usage:
        service = CRMLookupService()
        result = service.lookup_participant("Victor Hu", "victor@example.com")
        if result:
            print(f"Found: {result.person_id} (confidence: {result.confidence})")
    """

    def __init__(self):
        """Initialize the lookup service."""
        self._conn = None

    @property
    def conn(self):
        """Get database connection."""
        if self._conn is None:
            self._conn = get_db_connection(readonly=True)
        return self._conn

    def lookup_by_email(self, email: str) -> Optional[CRMLookupResult]:
        """Look up a person by exact email match.

        Args:
            email: Email address to look up.

        Returns:
            CRMLookupResult if found, None otherwise.
        """
        if not email:
            return None

        email = email.lower().strip()

        row = self.conn.execute(
            f"""SELECT id, full_name, company, email, markdown_path
               FROM {PEOPLE_TABLE}
               WHERE email = ? COLLATE NOCASE""",
            (email,)
        ).fetchone()

        if row:
            return CRMLookupResult(
                person_id=row['id'],
                display_name=row['full_name'],
                company=row['company'],
                email=row['email'],
                markdown_path=row['markdown_path'],
                match_type='email_exact',
                confidence=1.0
            )
        return None

    def lookup_by_name(self, name: str) -> Optional[CRMLookupResult]:
        """Look up a person by name.

        Exact-only matching; ambiguous names return None.

        Args:
            name: Name to look up.

        Returns:
            CRMLookupResult if found, None otherwise.
        """
        if not name:
            return None

        normalized = self._normalize_name(name)
        if not normalized:
            return None

        rows = self.conn.execute(
            f"""SELECT id, full_name, company, email, markdown_path
               FROM {PEOPLE_TABLE}
               WHERE full_name = ? COLLATE NOCASE""",
            (name,)
        ).fetchall()

        if len(rows) == 1:
            row = rows[0]
            return CRMLookupResult(
                person_id=row['id'],
                display_name=row['full_name'],
                company=row['company'],
                email=row['email'],
                markdown_path=row['markdown_path'],
                match_type='name_exact_unique',
                confidence=0.97
            )
        return None

    def lookup_participant(
        self,
        name: str,
        email: Optional[str] = None
    ) -> Optional[CRMLookupResult]:
        """Look up a meeting participant by name and/or email.

        Prioritizes email match (highest confidence), then falls back to name.

        Args:
            name: Participant name.
            email: Optional email for higher-confidence matching.

        Returns:
            CRMLookupResult if found, None otherwise.
        """
        # Try email first (highest confidence)
        if email:
            result = self.lookup_by_email(email)
            if result:
                return result

        # Fall back to name
        if name:
            return self.lookup_by_name(name)

        return None

    def batch_lookup(
        self,
        participants: List[Dict[str, str]]
    ) -> Dict[str, Optional[CRMLookupResult]]:
        """Look up multiple participants.

        Args:
            participants: List of dicts with 'name' and optional 'email'.

        Returns:
            Dict mapping participant name to lookup result.
        """
        results = {}
        for p in participants:
            name = p.get('name', '')
            email = p.get('email')
            results[name] = self.lookup_participant(name, email)
        return results

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the CRM.

        Returns:
            Dict with counts.
        """
        people_count = self.conn.execute(
            f"SELECT COUNT(*) FROM {PEOPLE_TABLE}"
        ).fetchone()[0]

        with_email = self.conn.execute(
            f"SELECT COUNT(*) FROM {PEOPLE_TABLE} WHERE email IS NOT NULL"
        ).fetchone()[0]

        with_company = self.conn.execute(
            f"SELECT COUNT(*) FROM {PEOPLE_TABLE} WHERE company IS NOT NULL"
        ).fetchone()[0]

        return {
            'total_people': people_count,
            'with_email': with_email,
            'with_company': with_company
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
    parser.add_argument('--stats', action='store_true', help="Show stats")
    args = parser.parse_args()

    service = CRMLookupService()

    try:
        if args.stats:
            stats = service.get_stats()
            print("CRM Lookup Stats:")
            print(f"  Total people: {stats['total_people']}")
            print(f"  With email: {stats['with_email']}")
            print(f"  With company: {stats['with_company']}")
            return

        if args.email:
            result = service.lookup_by_email(args.email)
            if result:
                print(f"Found: {result.display_name} (ID: {result.person_id})")
                print(f"  Email: {result.email}")
                print(f"  Company: {result.company}")
                print(f"  Confidence: {result.confidence}")
            else:
                print(f"No match found for email: {args.email}")
            return

        if args.name:
            result = service.lookup_by_name(args.name)
            if result:
                print(f"Found: {result.display_name} (ID: {result.person_id})")
                print(f"  Email: {result.email}")
                print(f"  Company: {result.company}")
                print(f"  Match type: {result.match_type}")
                print(f"  Confidence: {result.confidence}")
            else:
                print(f"No match found for name: {args.name}")
            return

        parser.print_help()

    finally:
        service.close()


if __name__ == "__main__":
    main()
