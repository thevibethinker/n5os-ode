#!/usr/bin/env python3
"""
Migration Script: Consolidate CRM/Deals databases into n5_core.db

Migrates data from:
- N5/data/deals.db (deals, deal_contacts, deal_activities)
- N5/data/crm_v3.db (profiles, organizations, calendar_events)
- Personal/Knowledge/CRM/db/crm.db (individuals, organizations, relationships)

Usage:
    python3 N5/scripts/migrate_to_n5_core.py --dry-run
    python3 N5/scripts/migrate_to_n5_core.py --source all
    python3 N5/scripts/migrate_to_n5_core.py --source crm --verify
"""

import argparse
import sqlite3
import shutil
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import centralized paths
sys.path.insert(0, "/home/workspace")
from N5.lib.paths import (
    N5_DATA_DIR,
    N5_CORE_DB as N5_CORE_PATH,
    LEGACY_DEALS_DB as DEALS_DB_PATH,
    LEGACY_CRM_V3_DB as CRM_V3_DB_PATH,
    WORKSPACE_ROOT,
)

# Database paths (using centralized paths)
CRM_DB_PATH = WORKSPACE_ROOT / "Personal/Knowledge/CRM/db/crm.db"
BACKUP_DIR = N5_DATA_DIR / "backups"


class MigrationStats:
    def __init__(self):
        self.people_migrated = 0
        self.people_deduplicated = 0
        self.organizations_migrated = 0
        self.organizations_deduplicated = 0
        self.deals_migrated = 0
        self.deal_roles_created = 0
        self.deal_activities_migrated = 0
        self.calendar_events_migrated = 0
        self.interactions_migrated = 0
        self.relationships_migrated = 0
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def report(self):
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"People migrated:        {self.people_migrated}")
        print(f"People deduplicated:    {self.people_deduplicated}")
        print(f"Organizations migrated: {self.organizations_migrated}")
        print(f"Organizations deduped:  {self.organizations_deduplicated}")
        print(f"Deals migrated:         {self.deals_migrated}")
        print(f"Deal roles created:     {self.deal_roles_created}")
        print(f"Deal activities:        {self.deal_activities_migrated}")
        print(f"Calendar events:        {self.calendar_events_migrated}")
        print(f"Interactions:           {self.interactions_migrated}")
        print(f"Relationships:          {self.relationships_migrated}")
        print("-"*60)
        if self.errors:
            print(f"ERRORS ({len(self.errors)}):")
            for e in self.errors[:10]:
                print(f"  ✗ {e}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors)-10} more")
        if self.warnings:
            print(f"WARNINGS ({len(self.warnings)}):")
            for w in self.warnings[:10]:
                print(f"  ⚠ {w}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings)-10} more")
        print("="*60)


class Migration:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = MigrationStats()
        self.email_to_person_id: Dict[str, int] = {}  # For deduplication
        self.name_to_org_id: Dict[str, int] = {}  # For org deduplication
        self.deal_contact_to_person_id: Dict[str, int] = {}  # Map old deal_contact.id -> people.id
        self.crm_individual_to_person_id: Dict[int, int] = {}  # Map crm individual.id -> people.id
        self.conn: Optional[sqlite3.Connection] = None
    
    def backup_databases(self):
        """Create backups of all source databases."""
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for db_path, name in [
            (DEALS_DB_PATH, "deals"),
            (CRM_V3_DB_PATH, "crm_v3"),
            (CRM_DB_PATH, "crm")
        ]:
            if db_path.exists():
                backup_name = f"{name}_{timestamp}.db"
                backup_path = BACKUP_DIR / backup_name
                shutil.copy(db_path, backup_path)
                print(f"  Backed up {name} → {backup_path}")
    
    def normalize_email(self, email: Optional[str]) -> Optional[str]:
        """Normalize email for deduplication (lowercase, strip whitespace)."""
        if not email:
            return None
        return email.strip().lower()
    
    def normalize_name(self, name: str) -> str:
        """Normalize organization name for deduplication."""
        return name.strip().lower()
    
    def map_category(self, category: Optional[str]) -> Optional[str]:
        """Map old category values to new schema."""
        if not category:
            return None
        category = category.upper().strip()
        valid_categories = {'FOUNDER', 'INVESTOR', 'CUSTOMER', 'COMMUNITY', 
                           'NETWORKING', 'ADVISOR', 'PARTNER', 'OTHER'}
        if category in valid_categories:
            return category
        # Map common variations
        mapping = {
            'NETWORK': 'NETWORKING',
            'VENTURE': 'INVESTOR',
            'VC': 'INVESTOR',
            'STARTUP': 'FOUNDER',
            'COACH': 'ADVISOR',
            'MENTOR': 'ADVISOR',
        }
        return mapping.get(category, 'OTHER')
    
    def find_or_create_person(self, email: Optional[str], full_name: str, 
                              source_db: str, source_id: str = None,
                              **extra_fields) -> int:
        """Find existing person by email or create new one. Returns person_id."""
        norm_email = self.normalize_email(email)
        
        # Check if we've seen this email
        if norm_email and norm_email in self.email_to_person_id:
            self.stats.people_deduplicated += 1
            return self.email_to_person_id[norm_email]
        
        if self.dry_run:
            # Fake ID for dry run
            fake_id = len(self.email_to_person_id) + 1
            if norm_email:
                self.email_to_person_id[norm_email] = fake_id
            self.stats.people_migrated += 1
            return fake_id
        
        # Check database for existing email match
        if norm_email:
            cursor = self.conn.execute(
                "SELECT id FROM people WHERE LOWER(email) = ?", 
                (norm_email,)
            )
            row = cursor.fetchone()
            if row:
                self.email_to_person_id[norm_email] = row[0]
                self.stats.people_deduplicated += 1
                return row[0]
        
        # Insert new person
        columns = ['full_name', 'email', 'source_db', 'source_id']
        values = [full_name, norm_email, source_db, source_id]
        
        # Add extra fields
        for key, val in extra_fields.items():
            if val is not None:
                columns.append(key)
                values.append(val)
        
        placeholders = ', '.join(['?'] * len(columns))
        col_str = ', '.join(columns)
        
        try:
            cursor = self.conn.execute(
                f"INSERT INTO people ({col_str}) VALUES ({placeholders})",
                values
            )
            person_id = cursor.lastrowid
            if norm_email:
                self.email_to_person_id[norm_email] = person_id
            self.stats.people_migrated += 1
            return person_id
        except sqlite3.Error as e:
            self.stats.errors.append(f"Failed to insert person {full_name}: {e}")
            return -1
    
    def find_or_create_organization(self, name: str, source_db: str, 
                                    source_id: str = None, **extra_fields) -> int:
        """Find existing org by name or create new one. Returns org_id."""
        norm_name = self.normalize_name(name)
        
        if norm_name in self.name_to_org_id:
            self.stats.organizations_deduplicated += 1
            return self.name_to_org_id[norm_name]
        
        if self.dry_run:
            fake_id = len(self.name_to_org_id) + 1
            self.name_to_org_id[norm_name] = fake_id
            self.stats.organizations_migrated += 1
            return fake_id
        
        # Check database
        cursor = self.conn.execute(
            "SELECT id FROM organizations WHERE LOWER(name) = ?",
            (norm_name,)
        )
        row = cursor.fetchone()
        if row:
            self.name_to_org_id[norm_name] = row[0]
            self.stats.organizations_deduplicated += 1
            return row[0]
        
        # Insert new
        columns = ['name', 'source_db', 'source_id']
        values = [name.strip(), source_db, source_id]
        
        for key, val in extra_fields.items():
            if val is not None:
                columns.append(key)
                values.append(val)
        
        placeholders = ', '.join(['?'] * len(columns))
        col_str = ', '.join(columns)
        
        try:
            cursor = self.conn.execute(
                f"INSERT INTO organizations ({col_str}) VALUES ({placeholders})",
                values
            )
            org_id = cursor.lastrowid
            self.name_to_org_id[norm_name] = org_id
            self.stats.organizations_migrated += 1
            return org_id
        except sqlite3.Error as e:
            self.stats.errors.append(f"Failed to insert org {name}: {e}")
            return -1
    
    def migrate_personal_crm(self):
        """Migrate Personal/Knowledge/CRM/db/crm.db"""
        print("\n[1/3] Migrating Personal CRM database...")
        
        if not CRM_DB_PATH.exists():
            self.stats.warnings.append(f"Personal CRM not found: {CRM_DB_PATH}")
            return
        
        src = sqlite3.connect(CRM_DB_PATH)
        src.row_factory = sqlite3.Row
        
        # Migrate organizations first
        print("  → Organizations...")
        cursor = src.execute("SELECT * FROM organizations")
        for row in cursor:
            self.find_or_create_organization(
                name=row['name'],
                source_db='crm',
                source_id=str(row['id']),
                domain=row['domain'],
                industry=row['industry']
            )
        
        # Migrate individuals → people
        print("  → Individuals → people...")
        cursor = src.execute("SELECT * FROM individuals")
        for row in cursor:
            org_id = None
            if row['company']:
                org_id = self.name_to_org_id.get(self.normalize_name(row['company']))
            
            person_id = self.find_or_create_person(
                email=row['email'],
                full_name=row['full_name'],
                source_db='crm',
                source_id=str(row['id']),
                linkedin_url=row['linkedin_url'],
                company=row['company'],
                title=row['title'],
                organization_id=org_id,
                category=self.map_category(row['category']),
                status=row['status'],
                priority=row['priority'],
                tags=row['tags'],
                first_contact_date=row['first_contact_date'],
                last_contact_date=row['last_contact_date'],
                markdown_path=row['markdown_path']
            )
            # Store mapping for interactions lookup
            self.crm_individual_to_person_id[row['id']] = person_id
        
        # Migrate interactions
        print("  → Interactions...")
        cursor = src.execute("SELECT * FROM interactions")
        for row in cursor:
            # Find person_id for this individual
            person_id = self.crm_individual_to_person_id.get(row['individual_id'])
            if not person_id or person_id == -1:
                continue
            
            if not self.dry_run:
                try:
                    self.conn.execute("""
                        INSERT INTO interactions 
                        (person_id, type, direction, summary, occurred_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        person_id,
                        row['interaction_type'],
                        row['direction'] if 'direction' in row.keys() else None,
                        row['context'],
                        row['interaction_date']
                    ))
                    self.stats.interactions_migrated += 1
                except sqlite3.Error as e:
                    self.stats.errors.append(f"Failed to insert interaction: {e}")
            else:
                self.stats.interactions_migrated += 1
        
        # Migrate relationships
        print("  → Relationships...")
        cursor = src.execute("SELECT * FROM relationships")
        for row in cursor:
            # Lookup both people using our individual mapping
            person_a_id = self.crm_individual_to_person_id.get(row['person_a_id'])
            person_b_id = self.crm_individual_to_person_id.get(row['person_b_id'])
            
            if not person_a_id or not person_b_id or person_a_id == -1 or person_b_id == -1:
                continue
            
            if not self.dry_run:
                try:
                    self.conn.execute("""
                        INSERT INTO relationships 
                        (person_a_id, person_b_id, relationship_type, strength, notes)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        person_a_id, person_b_id,
                        row['relationship_type'],
                        row['strength'],
                        row['notes'] if 'notes' in row.keys() else None
                    ))
                    self.stats.relationships_migrated += 1
                except sqlite3.Error as e:
                    self.stats.errors.append(f"Failed to insert relationship: {e}")
            else:
                self.stats.relationships_migrated += 1
        
        src.close()
        print(f"  ✓ Personal CRM migration complete")
    
    def migrate_crm_v3(self):
        """Migrate N5/data/crm_v3.db"""
        print("\n[2/3] Migrating CRM v3 database...")
        
        if not CRM_V3_DB_PATH.exists():
            self.stats.warnings.append(f"CRM v3 not found: {CRM_V3_DB_PATH}")
            return
        
        src = sqlite3.connect(CRM_V3_DB_PATH)
        src.row_factory = sqlite3.Row
        
        # Migrate organizations
        print("  → Organizations...")
        cursor = src.execute("SELECT * FROM organizations")
        for row in cursor:
            self.find_or_create_organization(
                name=row['name'],
                source_db='crm_v3',
                source_id=str(row['id']),
                domain=row['domain'],
                industry=row['industry'],
                linkedin_url=row['linkedin_url'],
                description=row['description'],
                size=row['headcount_range']
            )
        
        # Migrate profiles → people
        print("  → Profiles → people...")
        cursor = src.execute("SELECT * FROM profiles")
        for row in cursor:
            org_id = None
            if row['organization_id']:
                org_cursor = src.execute(
                    "SELECT name FROM organizations WHERE id = ?",
                    (row['organization_id'],)
                )
                org_row = org_cursor.fetchone()
                if org_row:
                    org_id = self.name_to_org_id.get(self.normalize_name(org_row['name']))
            
            self.find_or_create_person(
                email=row['email'] or row['primary_email'],
                full_name=row['name'],
                source_db='crm_v3',
                source_id=str(row['id']),
                linkedin_url=row['linkedin_url'],
                organization_id=org_id,
                category=self.map_category(row['category']),
                markdown_path=row['yaml_path'],
                last_contact_date=row['last_contact_at']
            )
        
        # Migrate calendar_events
        print("  → Calendar events...")
        cursor = src.execute("SELECT * FROM calendar_events")
        for row in cursor:
            if not self.dry_run:
                try:
                    self.conn.execute("""
                        INSERT OR IGNORE INTO calendar_events 
                        (id, google_event_id, title, start_time, end_time, 
                         location, description, meeting_folder)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row['id']),  # Use internal id as our primary key
                        row['event_id'],  # Google's event_id
                        row['summary'],   # Called 'summary' in source
                        row['start_time'],
                        row['end_time'],
                        row['location'],
                        row['description'],
                        None  # meeting_folder not in source
                    ))
                    self.stats.calendar_events_migrated += 1
                except sqlite3.Error as e:
                    self.stats.errors.append(f"Failed to insert calendar event: {e}")
            else:
                self.stats.calendar_events_migrated += 1
        
        # Migrate event_attendees
        print("  → Event attendees...")
        cursor = src.execute("""
            SELECT ea.*, p.email, p.name 
            FROM event_attendees ea 
            JOIN profiles p ON ea.profile_id = p.id
        """)
        for row in cursor:
            person_id = self.email_to_person_id.get(self.normalize_email(row['email']))
            if not person_id:
                continue
            
            if not self.dry_run:
                try:
                    self.conn.execute("""
                        INSERT OR IGNORE INTO event_attendees 
                        (event_id, person_id, email, response_status, is_organizer)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        row['event_id'],
                        person_id,
                        row['email'],
                        row['response_status'],
                        row['is_organizer']
                    ))
                except sqlite3.Error as e:
                    self.stats.errors.append(f"Failed to insert event attendee: {e}")
        
        src.close()
        print(f"  ✓ CRM v3 migration complete")
    
    def migrate_deals(self):
        """Migrate N5/data/deals.db"""
        print("\n[3/3] Migrating Deals database...")
        
        if not DEALS_DB_PATH.exists():
            self.stats.warnings.append(f"Deals DB not found: {DEALS_DB_PATH}")
            return
        
        src = sqlite3.connect(DEALS_DB_PATH)
        src.row_factory = sqlite3.Row
        
        # Migrate deal_contacts → people first
        print("  → Deal contacts → people...")
        cursor = src.execute("SELECT * FROM deal_contacts")
        for row in cursor:
            person_id = self.find_or_create_person(
                email=row['email'],
                full_name=row['full_name'],
                source_db='deals',
                source_id=row['id'],
                linkedin_url=row['linkedin_url'],
                company=row['company'],
                title=row['role'],
                last_contact_date=row['last_contact_date']
            )
            # Store mapping for later deal_roles creation
            self.deal_contact_to_person_id[row['id']] = person_id
        
        # Migrate deals
        print("  → Deals...")
        cursor = src.execute("SELECT * FROM deals")
        for row in cursor:
            # Find or create organization
            org_id = None
            if row['company']:
                org_id = self.find_or_create_organization(
                    name=row['company'],
                    source_db='deals',
                    website=row['website'] if 'website' in row.keys() else row['company_website'] if 'company_website' in row.keys() else None
                )
            
            # Find primary contact person_id
            primary_contact_id = None
            if row['contact_id'] and row['contact_id'] in self.deal_contact_to_person_id:
                primary_contact_id = self.deal_contact_to_person_id[row['contact_id']]
            
            if not self.dry_run:
                try:
                    self.conn.execute("""
                        INSERT OR IGNORE INTO deals 
                        (id, deal_type, company, organization_id, category, pipeline,
                         stage, temperature, primary_contact_id, notion_page_id,
                         external_source, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['id'],
                        row['deal_type'],
                        row['company'],
                        org_id,
                        row['category'],
                        row['pipeline'],
                        row['stage'],
                        row['temperature'],
                        primary_contact_id,
                        row['external_id'] if 'external_id' in row.keys() else None,  # Notion page ID stored here
                        row['external_source'],
                        row['notes']
                    ))
                    self.stats.deals_migrated += 1
                except sqlite3.Error as e:
                    self.stats.errors.append(f"Failed to insert deal {row['id']}: {e}")
            else:
                self.stats.deals_migrated += 1
        
        # Create deal_roles from deal_contacts
        print("  → Creating deal_roles...")
        cursor = src.execute("SELECT * FROM deal_contacts WHERE associated_deal_id IS NOT NULL")
        for row in cursor:
            person_id = self.deal_contact_to_person_id.get(row['id'])
            if not person_id or person_id == -1:
                continue
            
            # Map contact_type to role
            role_mapping = {
                'broker': 'broker',
                'leadership': 'primary_contact',
                'champion': 'champion',
                'decision_maker': 'decision_maker',
                'influencer': 'influencer'
            }
            role = role_mapping.get(row['contact_type'], 'primary_contact')
            
            if not self.dry_run:
                try:
                    self.conn.execute("""
                        INSERT OR IGNORE INTO deal_roles 
                        (deal_id, person_id, role, context)
                        VALUES (?, ?, ?, ?)
                    """, (
                        row['associated_deal_id'],
                        person_id,
                        role,
                        row['angle_strategy']
                    ))
                    self.stats.deal_roles_created += 1
                except sqlite3.Error as e:
                    # Don't log duplicate errors
                    if "UNIQUE constraint" not in str(e):
                        self.stats.errors.append(f"Failed to insert deal_role: {e}")
            else:
                self.stats.deal_roles_created += 1
        
        # Migrate deal_activities
        print("  → Deal activities...")
        cursor = src.execute("SELECT * FROM deal_activities")
        for row in cursor:
            if not self.dry_run:
                try:
                    self.conn.execute("""
                        INSERT INTO deal_activities 
                        (deal_id, activity_type, description, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (
                        row['deal_id'],
                        row['activity_type'],
                        row['description'],
                        row['created_at']
                    ))
                    self.stats.deal_activities_migrated += 1
                except sqlite3.Error as e:
                    self.stats.errors.append(f"Failed to insert deal activity: {e}")
            else:
                self.stats.deal_activities_migrated += 1
        
        src.close()
        print(f"  ✓ Deals migration complete")
    
    def verify_migration(self):
        """Verify migration integrity."""
        print("\nVerifying migration...")
        
        if self.dry_run:
            print("  (Skipped - dry run mode)")
            return True
        
        issues = []
        
        # Check record counts
        counts = {}
        for table in ['people', 'organizations', 'deals', 'deal_roles', 
                      'deal_activities', 'calendar_events', 'interactions']:
            cursor = self.conn.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        
        print(f"\n  Final record counts:")
        for table, count in counts.items():
            print(f"    {table}: {count}")
        
        # Check foreign key integrity
        cursor = self.conn.execute("PRAGMA foreign_key_check")
        fk_issues = cursor.fetchall()
        if fk_issues:
            for issue in fk_issues[:5]:
                issues.append(f"FK violation: {issue}")
        
        # Verify expected minimums
        if counts['people'] < 200:
            issues.append(f"People count ({counts['people']}) below expected (~250+)")
        if counts['deals'] < 90:
            issues.append(f"Deals count ({counts['deals']}) below expected (99)")
        if counts['organizations'] < 25:
            issues.append(f"Organizations count ({counts['organizations']}) below expected (~30+)")
        
        if issues:
            print("\n  ⚠ Verification warnings:")
            for issue in issues:
                print(f"    - {issue}")
            return False
        else:
            print("\n  ✓ Verification passed")
            return True
    
    def run(self, sources: List[str]):
        """Execute migration."""
        print(f"\n{'='*60}")
        print(f"N5 Core Database Migration")
        print(f"{'='*60}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        print(f"Sources: {', '.join(sources)}")
        print(f"Target: {N5_CORE_PATH}")
        
        if not self.dry_run:
            # Backup first
            print("\nBacking up source databases...")
            self.backup_databases()
            
            # Ensure schema exists
            if not N5_CORE_PATH.exists():
                print(f"\n✗ Target database does not exist: {N5_CORE_PATH}")
                print("  Run: python3 N5/scripts/n5_core_schema.py --create")
                sys.exit(1)
            
            # Connect to target
            self.conn = sqlite3.connect(N5_CORE_PATH)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.conn.row_factory = sqlite3.Row
        
        try:
            # Migration order matters: orgs → people → deals → rest
            if 'all' in sources or 'crm' in sources:
                self.migrate_personal_crm()
            
            if 'all' in sources or 'crm_v3' in sources:
                self.migrate_crm_v3()
            
            if 'all' in sources or 'deals' in sources:
                self.migrate_deals()
            
            if not self.dry_run:
                self.conn.commit()
            
            self.verify_migration()
            
        finally:
            if self.conn:
                self.conn.close()
        
        self.stats.report()
        
        return len(self.stats.errors) == 0


def main():
    parser = argparse.ArgumentParser(description="Migrate CRM/Deals to n5_core.db")
    parser.add_argument('--dry-run', action='store_true', 
                        help='Simulate migration without writing')
    parser.add_argument('--source', type=str, default='all',
                        help='Source to migrate: all, crm, crm_v3, deals')
    parser.add_argument('--verify', action='store_true',
                        help='Run verification after migration')
    
    args = parser.parse_args()
    
    sources = [args.source] if args.source != 'all' else ['all']
    
    migration = Migration(dry_run=args.dry_run)
    success = migration.run(sources)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
