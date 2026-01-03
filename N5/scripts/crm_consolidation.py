#!/usr/bin/env python3
"""
CRM Consolidation Script

One-time migration to consolidate fragmented CRM data:
1. Merge profiles from legacy directory to canonical location
2. Merge database records from profiles.db into crm.db
3. Rebuild index.jsonl from canonical profiles
4. Generate validation report

Usage:
    python3 crm_consolidation.py --dry-run    # Preview changes
    python3 crm_consolidation.py              # Execute migration
    python3 crm_consolidation.py --validate   # Validate only (no changes)
"""

import argparse
import json
import logging
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Import canonical paths
import sys
sys.path.insert(0, str(Path(__file__).parent))
from crm_paths import (
    CRM_DB, CRM_INDIVIDUALS, CRM_INDEX,
    LEGACY_CRM_DIR, LEGACY_PROFILES_DB, LEGACY_CRM_INDEX,
    ensure_crm_dirs, WORKSPACE
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def parse_frontmatter(content: str) -> Dict:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}

    if not content.startswith("---"):
        return frontmatter

    try:
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return frontmatter

        yaml_content = content[3:end_idx].strip()
        for line in yaml_content.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                frontmatter[key] = value
    except Exception as e:
        logger.warning(f"Failed to parse frontmatter: {e}")

    return frontmatter


def extract_email_from_content(content: str) -> Optional[str]:
    """Try to extract email from profile content."""
    # Check frontmatter
    fm = parse_frontmatter(content)
    if fm.get("email_primary"):
        return fm["email_primary"].lower()
    if fm.get("email"):
        return fm["email"].lower()

    # Check body for email pattern
    email_pattern = r'\*\*Email:\*\*\s*(\S+@\S+\.\S+)'
    match = re.search(email_pattern, content)
    if match:
        return match.group(1).lower()

    return None


def extract_name_from_content(content: str, slug: str) -> str:
    """Extract name from profile content or derive from slug."""
    fm = parse_frontmatter(content)
    if fm.get("name"):
        return fm["name"]

    # Try to find # Name header
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    # Derive from slug
    return slug.replace("-", " ").title()


def extract_organization_from_content(content: str) -> Optional[str]:
    """Extract organization from profile content."""
    fm = parse_frontmatter(content)
    if fm.get("organization"):
        return fm["organization"]

    match = re.search(r'\*\*Organization:\*\*\s*(.+)', content)
    if match:
        return match.group(1).strip()

    return None


def extract_lead_type_from_content(content: str) -> Optional[str]:
    """Extract lead type from profile content."""
    fm = parse_frontmatter(content)
    if fm.get("lead_type"):
        return fm["lead_type"]

    match = re.search(r'\*\*Lead Type:\*\*\s*(\S+)', content)
    if match:
        return match.group(1).strip()

    return None


def map_lead_type_to_category(lead_type: Optional[str]) -> str:
    """Map legacy lead_type to new category enum."""
    if not lead_type:
        return "OTHER"

    mapping = {
        "LD-INV": "INVESTOR",
        "LD-HIR": "CUSTOMER",
        "LD-COM": "COMMUNITY",
        "LD-NET": "NETWORKING",
        "LD-GEN": "OTHER",
        "LD-ADV": "ADVISOR",
        "LD-PAR": "PARTNER",
        "LD-FND": "FOUNDER",
    }

    return mapping.get(lead_type.upper(), "OTHER")


class CRMConsolidator:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.stats = {
            "profiles_migrated": 0,
            "profiles_skipped": 0,
            "profiles_conflict": 0,
            "db_records_added": 0,
            "db_records_updated": 0,
            "db_records_skipped": 0,
            "index_entries": 0,
            "errors": [],
        }

    def backup_databases(self):
        """Create backups before migration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if CRM_DB.exists():
            backup_path = CRM_DB.parent / f"crm_backup_{timestamp}.db"
            if not self.dry_run:
                shutil.copy(CRM_DB, backup_path)
            logger.info(f"{'[DRY RUN] Would backup' if self.dry_run else 'Backed up'} {CRM_DB} -> {backup_path}")

        if LEGACY_PROFILES_DB.exists():
            backup_path = LEGACY_PROFILES_DB.parent / f"profiles_backup_{timestamp}.db"
            if not self.dry_run:
                shutil.copy(LEGACY_PROFILES_DB, backup_path)
            logger.info(f"{'[DRY RUN] Would backup' if self.dry_run else 'Backed up'} {LEGACY_PROFILES_DB} -> {backup_path}")

    def migrate_profiles(self) -> Dict[str, Path]:
        """Migrate unique profiles from legacy to canonical directory.

        Returns dict mapping slug -> canonical path for all profiles.
        """
        logger.info("\n=== Phase 1: Profile Migration ===")

        canonical_profiles: Dict[str, Path] = {}

        # First, index all canonical profiles
        if CRM_INDIVIDUALS.exists():
            for md_file in CRM_INDIVIDUALS.glob("*.md"):
                if md_file.name.startswith("_"):
                    continue
                slug = md_file.stem
                canonical_profiles[slug] = md_file

        logger.info(f"Found {len(canonical_profiles)} profiles in canonical location")

        # Check legacy profiles
        if not LEGACY_CRM_DIR.exists():
            logger.info("Legacy directory does not exist, skipping profile migration")
            return canonical_profiles

        legacy_profiles = list(LEGACY_CRM_DIR.glob("*.md"))
        legacy_profiles = [p for p in legacy_profiles if not p.name.startswith("_")]
        logger.info(f"Found {len(legacy_profiles)} profiles in legacy location")

        # Migrate unique profiles
        for legacy_path in legacy_profiles:
            slug = legacy_path.stem

            if slug in canonical_profiles:
                # Check if they differ
                legacy_content = legacy_path.read_text(encoding="utf-8", errors="replace")
                canonical_content = canonical_profiles[slug].read_text(encoding="utf-8", errors="replace")

                if legacy_content.strip() != canonical_content.strip():
                    self.stats["profiles_conflict"] += 1
                    logger.warning(f"Conflict: {slug} differs between locations (keeping canonical)")
                else:
                    self.stats["profiles_skipped"] += 1
                continue

            # Migrate this profile
            dest_path = CRM_INDIVIDUALS / f"{slug}.md"

            if not self.dry_run:
                ensure_crm_dirs()
                shutil.copy(legacy_path, dest_path)

            canonical_profiles[slug] = dest_path
            self.stats["profiles_migrated"] += 1
            logger.info(f"{'[DRY RUN] Would migrate' if self.dry_run else 'Migrated'}: {slug}")

        logger.info(f"Migration complete: {self.stats['profiles_migrated']} migrated, "
                   f"{self.stats['profiles_skipped']} skipped, "
                   f"{self.stats['profiles_conflict']} conflicts")

        return canonical_profiles

    def merge_databases(self, canonical_profiles: Dict[str, Path]):
        """Merge records from profiles.db into crm.db."""
        logger.info("\n=== Phase 2: Database Merge ===")

        if not LEGACY_PROFILES_DB.exists():
            logger.info("Legacy profiles.db does not exist, skipping DB merge")
            return

        if not CRM_DB.exists():
            logger.error(f"Canonical DB not found: {CRM_DB}")
            return

        # Read legacy profiles.db
        legacy_conn = sqlite3.connect(LEGACY_PROFILES_DB)
        legacy_cursor = legacy_conn.cursor()

        try:
            legacy_cursor.execute("SELECT email, name, organization, profile_path FROM profiles")
            legacy_records = legacy_cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Failed to read legacy DB: {e}")
            legacy_conn.close()
            return

        logger.info(f"Found {len(legacy_records)} records in legacy profiles.db")

        # Connect to canonical DB
        if self.dry_run:
            crm_conn = sqlite3.connect(":memory:")
            # Copy schema
            real_conn = sqlite3.connect(CRM_DB)
            real_conn.backup(crm_conn)
            real_conn.close()
        else:
            crm_conn = sqlite3.connect(CRM_DB)

        crm_cursor = crm_conn.cursor()

        # Get existing emails in crm.db
        crm_cursor.execute("SELECT email FROM individuals WHERE email IS NOT NULL AND email != ''")
        existing_emails = {row[0].lower() for row in crm_cursor.fetchall() if row[0]}

        logger.info(f"Found {len(existing_emails)} existing emails in crm.db")

        # Process legacy records
        for email, name, org, profile_path in legacy_records:
            if not email:
                self.stats["db_records_skipped"] += 1
                continue

            email_lower = email.lower()

            if email_lower in existing_emails:
                self.stats["db_records_skipped"] += 1
                continue

            # Determine canonical markdown path
            # Legacy path: "Knowledge/crm/individuals/slug.md"
            # Canonical path: "Personal/Knowledge/CRM/individuals/slug.md"
            if profile_path:
                slug = Path(profile_path).stem
                canonical_md_path = f"Personal/Knowledge/CRM/individuals/{slug}.md"
            else:
                # Generate slug from name
                slug = name.lower().replace(" ", "-") if name else email.split("@")[0]
                canonical_md_path = f"Personal/Knowledge/CRM/individuals/{slug}.md"

            # Check if markdown exists
            full_md_path = WORKSPACE / canonical_md_path
            if not full_md_path.exists() and not self.dry_run:
                logger.warning(f"Markdown not found for {email}: {canonical_md_path}")

            # Insert into crm.db
            try:
                crm_cursor.execute("""
                    INSERT INTO individuals (full_name, email, company, markdown_path, status, priority)
                    VALUES (?, ?, ?, ?, 'active', 'medium')
                """, (name, email_lower, org, canonical_md_path))

                self.stats["db_records_added"] += 1
                existing_emails.add(email_lower)

                if not self.dry_run:
                    logger.debug(f"Added: {email_lower}")
                else:
                    logger.info(f"[DRY RUN] Would add: {email_lower}")

            except sqlite3.IntegrityError as e:
                logger.warning(f"Failed to add {email}: {e}")
                self.stats["errors"].append(f"DB insert failed: {email}")

        if not self.dry_run:
            crm_conn.commit()

        crm_conn.close()
        legacy_conn.close()

        logger.info(f"DB merge complete: {self.stats['db_records_added']} added, "
                   f"{self.stats['db_records_skipped']} skipped")

    def update_missing_emails(self, canonical_profiles: Dict[str, Path]):
        """Update crm.db records that have NULL email by extracting from markdown."""
        logger.info("\n=== Phase 2b: Populate Missing Emails ===")

        if not CRM_DB.exists():
            return

        conn = sqlite3.connect(CRM_DB) if not self.dry_run else sqlite3.connect(":memory:")
        if self.dry_run:
            real_conn = sqlite3.connect(CRM_DB)
            real_conn.backup(conn)
            real_conn.close()

        cursor = conn.cursor()

        # Find records with NULL email
        cursor.execute("""
            SELECT id, full_name, markdown_path
            FROM individuals
            WHERE email IS NULL OR email = ''
        """)
        null_email_records = cursor.fetchall()

        logger.info(f"Found {len(null_email_records)} records with NULL email")

        updated = 0
        for record_id, name, md_path in null_email_records:
            if not md_path:
                continue

            # Try canonical path first
            full_path = WORKSPACE / md_path
            if not full_path.exists():
                # Try without Personal/ prefix
                alt_path = WORKSPACE / "Personal" / md_path
                if alt_path.exists():
                    full_path = alt_path
                else:
                    continue

            try:
                content = full_path.read_text(encoding="utf-8", errors="replace")
                email = extract_email_from_content(content)

                if email:
                    cursor.execute(
                        "UPDATE individuals SET email = ? WHERE id = ?",
                        (email, record_id)
                    )
                    updated += 1
                    self.stats["db_records_updated"] += 1
                    logger.info(f"{'[DRY RUN] Would update' if self.dry_run else 'Updated'} "
                               f"{name}: email={email}")
            except Exception as e:
                logger.warning(f"Failed to extract email from {md_path}: {e}")

        if not self.dry_run:
            conn.commit()
        conn.close()

        logger.info(f"Email population complete: {updated} updated")

    def rebuild_index(self, canonical_profiles: Dict[str, Path]):
        """Rebuild index.jsonl from canonical profiles."""
        logger.info("\n=== Phase 3: Rebuild Index ===")

        entries = []

        for slug, md_path in sorted(canonical_profiles.items()):
            try:
                content = md_path.read_text(encoding="utf-8", errors="replace")

                email = extract_email_from_content(content)
                name = extract_name_from_content(content, slug)
                org = extract_organization_from_content(content)
                lead_type = extract_lead_type_from_content(content)

                entry = {
                    "person_id": slug,
                    "name": name,
                    "email": email,
                    "organization": org,
                    "lead_type": lead_type,
                    "path": f"Personal/Knowledge/CRM/individuals/{slug}.md",
                }
                entries.append(entry)
                self.stats["index_entries"] += 1

            except Exception as e:
                logger.warning(f"Failed to process {slug}: {e}")
                self.stats["errors"].append(f"Index entry failed: {slug}")

        # Write index
        if not self.dry_run:
            ensure_crm_dirs()
            with open(CRM_INDEX, "w", encoding="utf-8") as f:
                for entry in entries:
                    f.write(json.dumps(entry) + "\n")

        logger.info(f"{'[DRY RUN] Would write' if self.dry_run else 'Wrote'} "
                   f"{len(entries)} entries to index.jsonl")

    def validate(self) -> bool:
        """Validate data consistency."""
        logger.info("\n=== Validation Report ===")

        issues = []

        # Count markdown files
        if CRM_INDIVIDUALS.exists():
            md_files = list(CRM_INDIVIDUALS.glob("*.md"))
            md_files = [f for f in md_files if not f.name.startswith("_")]
            md_count = len(md_files)
        else:
            md_count = 0
            issues.append("Canonical profile directory does not exist")

        # Count DB records
        if CRM_DB.exists():
            conn = sqlite3.connect(CRM_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM individuals")
            db_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM individuals WHERE email IS NULL OR email = ''")
            null_email_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM individuals WHERE markdown_path IS NOT NULL")
            with_path_count = cursor.fetchone()[0]

            conn.close()
        else:
            db_count = 0
            null_email_count = 0
            with_path_count = 0
            issues.append("Canonical database does not exist")

        # Count index entries
        if CRM_INDEX.exists():
            with open(CRM_INDEX) as f:
                index_count = sum(1 for line in f if line.strip())
        else:
            index_count = 0

        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Markdown profiles:     {md_count}")
        print(f"Database records:      {db_count}")
        print(f"  - with email:        {db_count - null_email_count}")
        print(f"  - NULL email:        {null_email_count}")
        print(f"  - with markdown_path: {with_path_count}")
        print(f"Index entries:         {index_count}")
        print()

        if md_count != index_count:
            issues.append(f"Mismatch: {md_count} profiles vs {index_count} index entries")

        if null_email_count > 0:
            issues.append(f"{null_email_count} DB records have NULL email")

        if issues:
            print("ISSUES:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("All checks passed!")
            return True

    def run(self):
        """Execute full consolidation."""
        logger.info("=" * 60)
        logger.info(f"CRM Consolidation {'(DRY RUN)' if self.dry_run else ''}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 60)

        # Backup
        self.backup_databases()

        # Phase 1: Migrate profiles
        canonical_profiles = self.migrate_profiles()

        # Phase 2: Merge databases
        self.merge_databases(canonical_profiles)
        self.update_missing_emails(canonical_profiles)

        # Phase 3: Rebuild index
        self.rebuild_index(canonical_profiles)

        # Validation
        self.validate()

        # Summary
        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Profiles migrated:    {self.stats['profiles_migrated']}")
        print(f"Profiles skipped:     {self.stats['profiles_skipped']}")
        print(f"Profiles conflicting: {self.stats['profiles_conflict']}")
        print(f"DB records added:     {self.stats['db_records_added']}")
        print(f"DB records updated:   {self.stats['db_records_updated']}")
        print(f"Index entries:        {self.stats['index_entries']}")

        if self.stats["errors"]:
            print(f"\nErrors ({len(self.stats['errors'])}):")
            for err in self.stats["errors"][:10]:
                print(f"  - {err}")

        if self.dry_run:
            print("\n[DRY RUN] No changes were made. Run without --dry-run to apply.")


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate fragmented CRM data into canonical locations"
    )
    parser.add_argument("--dry-run", "-n", action="store_true",
                       help="Preview changes without applying them")
    parser.add_argument("--validate", "-v", action="store_true",
                       help="Validate data consistency only")

    args = parser.parse_args()

    consolidator = CRMConsolidator(dry_run=args.dry_run)

    if args.validate:
        consolidator.validate()
    else:
        consolidator.run()


if __name__ == "__main__":
    main()
