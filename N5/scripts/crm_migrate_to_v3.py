#!/usr/bin/env python3
"""
CRM V3 Migration Script
Consolidates 3 existing CRM systems into unified CRM V3 database.

Sources:
1. Knowledge/crm/crm.db (57 profiles)
2. N5/stakeholders/*.md (11 profiles)
3. N5/data/profiles.db (44 records)

Usage:
    python3 crm_migrate_to_v3.py --dry-run     # Preview only
    python3 crm_migrate_to_v3.py --execute     # Perform migration
    python3 crm_migrate_to_v3.py --validate    # Validate results
    python3 crm_migrate_to_v3.py --rollback    # Delete migrated data
"""

import argparse
import logging
import sqlite3
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils.crm_deduplicator import CRMDeduplicator, ProfileEntity
from utils.yaml_profile_generator import YAMLProfileGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class CRMv3Migrator:
    """Migrates data from 3 CRM sources to unified V3 system."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.workspace = Path("/home/workspace")
        
        self.source1_db = self.workspace / "Knowledge/crm/crm.db"
        self.source2_dir = self.workspace / "N5/stakeholders"
        self.source3_db = self.workspace / "N5/data/profiles.db"
        
        self.target_db = self.workspace / "N5/data/crm_v3.db"
        self.target_profiles_dir = self.workspace / "N5/crm_v3/profiles"
        
        self.deduplicator = CRMDeduplicator()
        self.stats = {
            "source1_count": 0,
            "source2_count": 0,
            "source3_count": 0,
            "total_records": 0,
            "unique_profiles": 0,
            "duplicates_found": 0,
            "conflicts_resolved": 0,
            "profiles_created": 0,
            "db_records_inserted": 0,
        }
    
    def read_source1_crm_db(self):
        """Read Knowledge/crm/crm.db individuals table."""
        logger.info(f"Reading source 1: {self.source1_db}")
        
        if not self.source1_db.exists():
            logger.error(f"Source 1 not found: {self.source1_db}")
            return
        
        conn = sqlite3.connect(self.source1_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM individuals")
        rows = cursor.fetchall()
        
        skipped_no_email = 0
        for row in rows:
            email = row["email"] if row["email"] else None
            if not email:
                skipped_no_email += 1
                continue
                
            record = {
                "email": email,
                "name": row["full_name"],
                "category": row["category"],
                "organization": row["company"],
                "linkedin_url": row["linkedin_url"],
                "notes": None,
                "last_contact_date": row["last_contact_date"],
            }
            self.deduplicator.add_record("crm.db", record)
            self.stats["source1_count"] += 1
        
        conn.close()
        logger.info(f"✓ Loaded {self.stats['source1_count']} records from source 1 (skipped {skipped_no_email} without email)")
    
    def read_source2_stakeholders(self):
        """Read N5/stakeholders/*.md markdown files."""
        logger.info(f"Reading source 2: {self.source2_dir}")
        
        if not self.source2_dir.exists():
            logger.error(f"Source 2 not found: {self.source2_dir}")
            return
        
        md_files = list(self.source2_dir.glob("*.md"))
        skipped_no_email = 0
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                
                email = None
                name = None
                category = "ADVISOR"
                
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        body = parts[2].strip()
                        
                        name = body.split("\n")[0].strip("# ").strip() if body else None
                        
                        import re
                        email_match = re.search(r'\*\*Email:\*\*\s+([^\s\n]+@[^\s\n]+)', body)
                        if email_match:
                            email = email_match.group(1)
                        
                        record = {
                            "email": email,
                            "name": name,
                            "category": category,
                            "organization": None,
                            "linkedin_url": None,
                            "notes": body[:500] if body else None,
                            "last_contact_date": frontmatter.get("last_edited"),
                        }
                        
                        if email:
                            self.deduplicator.add_record("stakeholders", record)
                            self.stats["source2_count"] += 1
                        else:
                            skipped_no_email += 1
            except Exception as e:
                logger.warning(f"Failed to parse {md_file.name}: {e}")
        
        logger.info(f"✓ Loaded {self.stats['source2_count']} records from source 2 (skipped {skipped_no_email} without email)")
    
    def read_source3_profiles_db(self):
        """Read N5/data/profiles.db profiles table."""
        logger.info(f"Reading source 3: {self.source3_db}")
        
        if not self.source3_db.exists():
            logger.error(f"Source 3 not found: {self.source3_db}")
            return
        
        conn = sqlite3.connect(self.source3_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM profiles")
        rows = cursor.fetchall()
        
        for row in rows:
            organization = row["organization"] if "organization" in row.keys() else None
            meeting_date = row["meeting_date"] if "meeting_date" in row.keys() else None
            
            record = {
                "email": row["email"],
                "name": row["name"],
                "category": "NETWORKING",
                "organization": organization,
                "meeting_count": 1,
                "last_contact_date": meeting_date,
            }
            self.deduplicator.add_record("profiles.db", record)
            self.stats["source3_count"] += 1
        
        conn.close()
        logger.info(f"✓ Loaded {self.stats['source3_count']} records from source 3")
    
    def analyze_deduplication(self):
        """Analyze deduplication results."""
        logger.info("Analyzing deduplication...")
        
        dedup_stats = self.deduplicator.get_statistics()
        self.stats.update(dedup_stats)
        
        logger.info(f"Total records: {self.stats['total_records']}")
        logger.info(f"Unique profiles: {self.stats['unique_profiles']}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']}")
        logger.info(f"Deduplication rate: {self.stats['deduplication_rate']}")
    
    def generate_yaml_profiles(self):
        """Generate YAML profile files."""
        logger.info("Generating YAML profiles...")
        
        if self.dry_run:
            logger.info("(DRY-RUN: Would create profiles, skipping)")
            return []
        
        generator = YAMLProfileGenerator(self.target_profiles_dir)
        profiles = self.deduplicator.get_unique_profiles()
        
        entities = [p.to_dict() for p in profiles]
        paths = generator.generate_batch(entities)
        
        self.stats["profiles_created"] = len(paths)
        logger.info(f"✓ Created {self.stats['profiles_created']} YAML profiles")
        
        return paths
    
    def insert_database_records(self, profile_paths: List[Path]):
        """Insert records into crm_v3.db profiles table."""
        logger.info("Inserting database records...")
        
        if self.dry_run:
            logger.info("(DRY-RUN: Would insert records, skipping)")
            return
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        profiles = self.deduplicator.get_unique_profiles()
        
        profile_id = 1
        for profile, path in zip(profiles, profile_paths):
            entity = profile.to_dict()
            now = datetime.now().isoformat()
            
            search_text = f"{entity['name']} {entity['email']} {entity.get('organization', '')}".lower()
            
            cursor.execute("""
                INSERT INTO profiles (
                    id, email, name, yaml_path, source, created_at,
                    last_enriched_at, last_contact_at, category, relationship_strength,
                    enrichment_status, profile_quality, meeting_count,
                    intelligence_block_count, last_intelligence_at, search_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                entity["email"],
                entity["name"],
                str(path.relative_to(self.workspace)),
                "migration_v3",
                now,
                None,
                entity["last_contact_date"],
                entity["category"],
                "moderate",
                "pending",
                "enriched" if entity["source_count"] > 1 else "stub",
                entity["total_meetings"],
                0,
                None,
                search_text,
            ))
            
            profile_id += 1
            self.stats["db_records_inserted"] += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Inserted {self.stats['db_records_inserted']} database records")
    
    def validate_migration(self):
        """Validate migration results."""
        logger.info("Validating migration...")
        
        profiles_count = len(list(self.target_profiles_dir.glob("*.yaml"))) if self.target_profiles_dir.exists() else 0
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM profiles")
        db_count = cursor.fetchone()[0]
        conn.close()
        
        logger.info(f"YAML profiles created: {profiles_count}")
        logger.info(f"Database records: {db_count}")
        
        if profiles_count == db_count == self.stats["unique_profiles"]:
            logger.info("✓ Validation PASSED - Counts match")
            return True
        else:
            logger.error("✗ Validation FAILED - Count mismatch")
            return False
    
    def rollback(self):
        """Delete all migrated data."""
        logger.info("Rolling back migration...")
        
        if self.target_profiles_dir.exists():
            import shutil
            shutil.rmtree(self.target_profiles_dir)
            logger.info(f"✓ Deleted {self.target_profiles_dir}")
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM profiles")
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Deleted {deleted} database records")
        logger.info("Rollback complete")
    
    def run(self):
        """Execute migration."""
        logger.info("=" * 60)
        logger.info(f"CRM V3 Migration {'(DRY-RUN)' if self.dry_run else '(EXECUTE)'}")
        logger.info("=" * 60)
        
        self.read_source1_crm_db()
        self.read_source2_stakeholders()
        self.read_source3_profiles_db()
        
        self.analyze_deduplication()
        
        profile_paths = self.generate_yaml_profiles()
        
        if not self.dry_run and profile_paths:
            self.insert_database_records(profile_paths)
        
        self.print_summary()
    
    def print_summary(self):
        """Print migration summary."""
        logger.info("\n" + "=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Source 1 (crm.db): {self.stats['source1_count']} records")
        logger.info(f"Source 2 (stakeholders): {self.stats['source2_count']} records")
        logger.info(f"Source 3 (profiles.db): {self.stats['source3_count']} records")
        logger.info(f"Total: {self.stats['total_records']} records")
        logger.info("")
        logger.info(f"Unique profiles identified: {self.stats['unique_profiles']}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']}")
        logger.info(f"Deduplication rate: {self.stats['deduplication_rate']}")
        logger.info("")
        
        if not self.dry_run:
            logger.info(f"YAML profiles created: {self.stats['profiles_created']}")
            logger.info(f"Database records inserted: {self.stats['db_records_inserted']}")
            logger.info("")
            logger.info(f"Output location: {self.target_profiles_dir}")
        else:
            logger.info("(DRY-RUN: No files created)")
            logger.info(f"Would create {self.stats['unique_profiles']} YAML profiles")
            logger.info(f"Would insert {self.stats['unique_profiles']} database records")
        
        logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="CRM V3 Migration Script")
    parser.add_argument("--dry-run", action="store_true", help="Preview migration without making changes")
    parser.add_argument("--execute", action="store_true", help="Perform actual migration")
    parser.add_argument("--validate", action="store_true", help="Validate migration results")
    parser.add_argument("--rollback", action="store_true", help="Delete all migrated data")
    
    args = parser.parse_args()
    
    if args.validate:
        migrator = CRMv3Migrator(dry_run=True)
        migrator.validate_migration()
    elif args.rollback:
        migrator = CRMv3Migrator(dry_run=False)
        confirm = input("Are you sure you want to rollback? (yes/no): ")
        if confirm.lower() == "yes":
            migrator.rollback()
        else:
            logger.info("Rollback cancelled")
    else:
        dry_run = not args.execute
        migrator = CRMv3Migrator(dry_run=dry_run)
        migrator.run()
        
        if not dry_run:
            migrator.validate_migration()


if __name__ == "__main__":
    main()




