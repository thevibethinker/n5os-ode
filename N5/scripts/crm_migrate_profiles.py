#!/usr/bin/env python3
"""
CRM Profile Migration: One-shot migration of all markdown profiles to SQLite

Purpose: Populate database with existing 57 profiles + backfill interactions/orgs
Principles: P5 (backup), P7 (dry-run), P15 (complete), P18 (verify), P19 (errors)
"""

import argparse
import json
import logging
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
CRM_DB = WORKSPACE / "Knowledge/crm/crm.db"
PROFILES_DIR = WORKSPACE / "Knowledge/crm/profiles"
SCHEMA_FILE = WORKSPACE / "N5/schemas/crm_schema.sql"
MEETINGS_DIR = WORKSPACE / "N5/records/meetings"


class CRMProfileMigrator:
    def __init__(self, db_path: Path, dry_run: bool = False):
        self.db_path = db_path
        self.dry_run = dry_run
        self.conn = None
        self.stats = {
            "profiles_processed": 0,
            "profiles_migrated": 0,
            "interactions_created": 0,
            "organizations_created": 0,
            "relationships_created": 0,
            "errors": []
        }
    
    def __enter__(self):
        if not self.dry_run:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
    
    def initialize_schema(self) -> bool:
        """Apply schema to database"""
        try:
            if not SCHEMA_FILE.exists():
                logger.error(f"Schema file not found: {SCHEMA_FILE}")
                return False
            
            schema_sql = SCHEMA_FILE.read_text()
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would drop existing tables and apply schema from {SCHEMA_FILE}")
                return True
            
            # Drop existing tables to ensure clean slate
            logger.info("Dropping existing tables for clean migration...")
            drop_tables = [
                "DROP TABLE IF EXISTS active_prospects",
                "DROP TABLE IF EXISTS stale_contacts",
                "DROP TABLE IF EXISTS recent_activity",
                "DROP TABLE IF EXISTS priority_follow_ups",
                "DROP TABLE IF EXISTS network_by_organization",
                "DROP VIEW IF EXISTS active_prospects",
                "DROP VIEW IF EXISTS stale_contacts", 
                "DROP VIEW IF EXISTS recent_activity",
                "DROP VIEW IF EXISTS priority_follow_ups",
                "DROP VIEW IF EXISTS network_by_organization",
                "DROP TRIGGER IF EXISTS update_last_interaction_date",
                "DROP TRIGGER IF EXISTS update_individuals_timestamp",
                "DROP TRIGGER IF EXISTS update_organizations_timestamp",
                "DROP TABLE IF EXISTS individual_organizations",
                "DROP TABLE IF EXISTS relationships",
                "DROP TABLE IF EXISTS interactions",
                "DROP TABLE IF EXISTS organizations",
                "DROP TABLE IF EXISTS individuals"
            ]
            
            for drop_sql in drop_tables:
                try:
                    self.conn.execute(drop_sql)
                except:
                    pass  # Ignore if table doesn't exist
            
            self.conn.commit()
            logger.info("✓ Old schema cleared")
            
            # Apply new schema
            self.conn.executescript(schema_sql)
            self.conn.commit()
            logger.info(f"✓ New schema applied from {SCHEMA_FILE}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to apply schema: {e}", exc_info=True)
            return False
    
    def parse_profile(self, profile_path: Path) -> Optional[Dict]:
        """Parse markdown profile and extract structured data"""
        try:
            content = profile_path.read_text()
            
            # Extract frontmatter
            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not frontmatter_match:
                logger.warning(f"No frontmatter in {profile_path.name}")
                return None
            
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            
            # Map lead_type to category
            lead_type_map = {
                "LD-FND": "FOUNDER",
                "LD-INV": "INVESTOR",
                "LD-CUS": "CUSTOMER",
                "LD-COM": "COMMUNITY",
                "LD-NET": "NETWORKING",
                "LD-ADV": "ADVISOR",
                "LD-HIR": "ADVISOR",  # Hiring advisor
                "LD-PAR": "PARTNER",
            }
            
            category = lead_type_map.get(frontmatter.get("lead_type", ""), "OTHER")
            
            # Extract interactions from content
            interactions = self._extract_interactions(content, frontmatter)
            
            # Extract organization
            organization = frontmatter.get("organization") or self._extract_company_from_content(content)
            
            # Handle list values (convert to string)
            if isinstance(organization, list):
                organization = organization[0] if organization else ""
            
            role = frontmatter.get("role", "")
            if isinstance(role, list):
                role = role[0] if role else ""
            
            return {
                "full_name": frontmatter.get("name", ""),
                "email": frontmatter.get("email_primary", ""),
                "linkedin_url": self._extract_linkedin(content),
                "company": organization,
                "title": role,
                "category": category,
                "status": frontmatter.get("status", "active"),
                "priority": self._infer_priority(frontmatter, content),
                "tags": json.dumps(self._extract_tags(content)),
                "first_contact_date": frontmatter.get("first_contact", ""),
                "last_contact_date": frontmatter.get("last_interaction", ""),
                "markdown_path": f"Knowledge/crm/profiles/{profile_path.name}",
                "interactions": interactions,
                "organization_name": organization
            }
        
        except Exception as e:
            logger.error(f"Failed to parse {profile_path.name}: {e}")
            self.stats["errors"].append({"file": profile_path.name, "error": str(e)})
            return None
    
    def _extract_interactions(self, content: str, frontmatter: Dict) -> List[Dict]:
        """Extract interaction history from profile content"""
        interactions = []
        
        # Check for meeting references
        meeting_pattern = r'Meeting \((\d{4}-\d{2}-\d{2})\) — ["\'](.+?)["\']'
        for match in re.finditer(meeting_pattern, content):
            date_str, context = match.groups()
            interactions.append({
                "type": "meeting",
                "date": date_str,
                "context": context[:200]  # Truncate long contexts
            })
        
        # Add first contact as interaction if not already captured
        first_contact = frontmatter.get("first_contact")
        if first_contact and not any(i["date"] == first_contact for i in interactions):
            interactions.append({
                "type": "meeting",
                "date": first_contact,
                "context": "Initial contact"
            })
        
        return interactions
    
    def _extract_linkedin(self, content: str) -> str:
        """Extract LinkedIn URL from content"""
        linkedin_match = re.search(r'- LinkedIn:\s*\[?([^\]\n]+)\]?', content)
        if linkedin_match:
            url = linkedin_match.group(1).strip()
            if url.startswith("http"):
                return url
        return ""
    
    def _extract_company_from_content(self, content: str) -> str:
        """Extract company name from content if not in frontmatter"""
        company_match = re.search(r'- Company:\s*\*?\*?([^\n*]+)\*?\*?', content)
        if company_match:
            return company_match.group(1).strip()
        return ""
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        tags = []
        
        # Look for common patterns
        if "series-a" in content.lower() or "series a" in content.lower():
            tags.append("series-a")
        if "enterprise" in content.lower():
            tags.append("enterprise")
        if "saas" in content.lower():
            tags.append("saas")
        if "founder" in content.lower():
            tags.append("founder")
        
        return tags
    
    def _infer_priority(self, frontmatter: Dict, content: str) -> str:
        """Infer priority based on activity and context"""
        # High priority if recent interaction
        last_interaction = frontmatter.get("last_interaction", "")
        if last_interaction:
            try:
                from datetime import datetime
                last_date = datetime.fromisoformat(last_interaction)
                days_ago = (datetime.now() - last_date).days
                if days_ago < 30:
                    return "high"
            except:
                pass
        
        # Check for priority indicators in content
        if "high priority" in content.lower() or "urgent" in content.lower():
            return "high"
        
        return "medium"
    
    def migrate_profile(self, profile_data: Dict) -> bool:
        """Migrate single profile to database"""
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would migrate: {profile_data['full_name']} ({profile_data['category']})")
                return True
            
            # Insert individual
            cursor = self.conn.execute("""
                INSERT INTO individuals (
                    full_name, email, linkedin_url, company, title,
                    category, status, priority, tags,
                    first_contact_date, last_contact_date, markdown_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_data["full_name"],
                profile_data["email"],
                profile_data["linkedin_url"],
                profile_data["company"],
                profile_data["title"],
                profile_data["category"],
                profile_data["status"],
                profile_data["priority"],
                profile_data["tags"],
                profile_data["first_contact_date"],
                profile_data["last_contact_date"],
                profile_data["markdown_path"]
            ))
            
            individual_id = cursor.lastrowid
            
            # Insert interactions
            for interaction in profile_data.get("interactions", []):
                self.conn.execute("""
                    INSERT INTO interactions (
                        individual_id, interaction_type, interaction_date, context
                    ) VALUES (?, ?, ?, ?)
                """, (
                    individual_id,
                    interaction["type"],
                    interaction["date"],
                    interaction["context"]
                ))
                self.stats["interactions_created"] += 1
            
            # Handle organization
            if profile_data.get("organization_name"):
                org_id = self._get_or_create_organization(profile_data["organization_name"])
                if org_id:
                    self.conn.execute("""
                        INSERT OR IGNORE INTO individual_organizations (
                            individual_id, organization_id, role, is_current
                        ) VALUES (?, ?, ?, 1)
                    """, (individual_id, org_id, profile_data["title"]))
            
            self.conn.commit()
            self.stats["profiles_migrated"] += 1
            logger.info(f"✓ Migrated: {profile_data['full_name']}")
            return True
        
        except sqlite3.IntegrityError as e:
            logger.warning(f"Duplicate or constraint violation for {profile_data['full_name']}: {e}")
            self.stats["errors"].append({
                "profile": profile_data["full_name"],
                "error": f"Integrity error: {e}"
            })
            return False
        
        except Exception as e:
            logger.error(f"Failed to migrate {profile_data['full_name']}: {e}", exc_info=True)
            self.stats["errors"].append({
                "profile": profile_data["full_name"],
                "error": str(e)
            })
            return False
    
    def _get_or_create_organization(self, org_name: str) -> Optional[int]:
        """Get or create organization, return ID"""
        try:
            cursor = self.conn.execute(
                "SELECT id FROM organizations WHERE name = ?", (org_name,)
            )
            row = cursor.fetchone()
            
            if row:
                return row[0]
            
            cursor = self.conn.execute(
                "INSERT INTO organizations (name) VALUES (?)", (org_name,)
            )
            self.stats["organizations_created"] += 1
            return cursor.lastrowid
        
        except Exception as e:
            logger.error(f"Failed to handle organization {org_name}: {e}")
            return None
    
    def migrate_all_profiles(self) -> bool:
        """Migrate all profiles from directory"""
        if not PROFILES_DIR.exists():
            logger.error(f"Profiles directory not found: {PROFILES_DIR}")
            return False
        
        profile_files = sorted(PROFILES_DIR.glob("*.md"))
        profile_files = [f for f in profile_files if f.name != "_template.md"]
        
        logger.info(f"Found {len(profile_files)} profiles to migrate")
        
        for profile_path in profile_files:
            self.stats["profiles_processed"] += 1
            
            profile_data = self.parse_profile(profile_path)
            if profile_data:
                self.migrate_profile(profile_data)
        
        return True
    
    def verify_migration(self) -> bool:
        """Verify migration completeness"""
        if self.dry_run:
            logger.info("[DRY RUN] Skipping verification")
            return True
        
        try:
            cursor = self.conn.execute("SELECT COUNT(*) FROM individuals")
            db_count = cursor.fetchone()[0]
            
            profile_files = [f for f in PROFILES_DIR.glob("*.md") if f.name != "_template.md"]
            file_count = len(profile_files)
            
            logger.info(f"Verification: {db_count} in DB, {file_count} files")
            
            if db_count != file_count:
                logger.warning(f"Count mismatch: {db_count} vs {file_count}")
                return False
            
            logger.info("✓ Verification passed")
            return True
        
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    def generate_report(self) -> Dict:
        """Generate migration report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "stats": self.stats,
            "success": self.stats["profiles_migrated"] == self.stats["profiles_processed"] - len(self.stats["errors"])
        }


def main(dry_run: bool = False) -> int:
    """Main migration function"""
    try:
        logger.info("=" * 60)
        logger.info("CRM Profile Migration - One-Shot Population")
        logger.info("=" * 60)
        
        if dry_run:
            logger.info("[DRY RUN MODE] No changes will be made")
        
        # Backup existing database
        if CRM_DB.exists() and not dry_run:
            backup_path = CRM_DB.parent / f"crm_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            import shutil
            shutil.copy2(CRM_DB, backup_path)
            logger.info(f"✓ Backup created: {backup_path}")
        
        # Run migration
        with CRMProfileMigrator(CRM_DB, dry_run=dry_run) as migrator:
            # Initialize schema
            if not migrator.initialize_schema():
                return 1
            
            # Migrate profiles
            if not migrator.migrate_all_profiles():
                return 1
            
            # Verify
            if not migrator.verify_migration():
                logger.warning("Verification failed, but migration may be partial success")
            
            # Report
            report = migrator.generate_report()
            
            logger.info("=" * 60)
            logger.info("MIGRATION COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Profiles processed: {report['stats']['profiles_processed']}")
            logger.info(f"Profiles migrated: {report['stats']['profiles_migrated']}")
            logger.info(f"Interactions created: {report['stats']['interactions_created']}")
            logger.info(f"Organizations created: {report['stats']['organizations_created']}")
            logger.info(f"Errors: {len(report['stats']['errors'])}")
            
            if report['stats']['errors']:
                logger.warning("Errors encountered:")
                for error in report['stats']['errors'][:10]:  # Show first 10
                    logger.warning(f"  - {error}")
            
            return 0 if report['success'] else 1
    
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate CRM profiles to SQLite")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run))
