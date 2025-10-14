#!/usr/bin/env python3
"""
CRM Profile Consolidation Script

Consolidates profiles from Knowledge/crm/profiles/ → Knowledge/crm/individuals/
and updates all scripts to reference the canonical individuals/ directory.

Phase 1: Update scripts to use individuals/
Phase 2: Migrate existing profiles
Phase 3: Update database records
"""
import logging
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
CRM_BASE = WORKSPACE / "Knowledge" / "crm"
INDIVIDUALS_DIR = CRM_BASE / "individuals"
PROFILES_DIR = CRM_BASE / "profiles"
PROFILES_ARCHIVE = CRM_BASE / ".archived_profiles_20251014"
DB_PATH = CRM_BASE / "crm.db"

# Scripts to update
SCRIPTS_TO_UPDATE = [
    WORKSPACE / "N5/scripts/crm_query.py",
    WORKSPACE / "N5/scripts/sync_b08_to_crm.py",
]


def phase1_update_scripts(dry_run: bool = True) -> int:
    """Update scripts to reference individuals/ instead of profiles/"""
    logger.info("=== PHASE 1: Update Script References ===")
    
    updates = {
        "N5/scripts/crm_query.py": {
            "line_165": {
                "old": "f'Knowledge/crm/profiles/{args.name",
                "new": "f'Knowledge/crm/individuals/{args.name"
            },
            "line_130": {
                "old": "md_path = f'Knowledge/crm/profiles/",
                "new": "md_path = f'Knowledge/crm/individuals/"
            }
        },
        "N5/scripts/sync_b08_to_crm.py": {
            "line_21": {
                "old": 'CRM_DIR = WORKSPACE / "Knowledge/crm/profiles"',
                "new": 'CRM_DIR = WORKSPACE / "Knowledge/crm/individuals"'
            }
        }
    }
    
    for script_rel, changes in updates.items():
        script_path = WORKSPACE / script_rel
        if not script_path.exists():
            logger.warning(f"Script not found: {script_path}")
            continue
            
        content = script_path.read_text()
        modified = False
        
        for location, change in changes.items():
            if change["old"] in content:
                if not dry_run:
                    content = content.replace(change["old"], change["new"])
                modified = True
                logger.info(f"  {'[DRY RUN] Would update' if dry_run else 'Updated'} {script_rel} ({location})")
        
        if modified and not dry_run:
            # Backup
            backup_path = script_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
            shutil.copy2(script_path, backup_path)
            logger.info(f"  Created backup: {backup_path}")
            
            # Write updated content
            script_path.write_text(content)
            logger.info(f"  ✓ Updated {script_rel}")
    
    return 0


def phase2_migrate_profiles(dry_run: bool = True) -> int:
    """Migrate profiles from profiles/ to individuals/"""
    logger.info("=== PHASE 2: Migrate Profiles ===")
    
    if not PROFILES_DIR.exists():
        logger.warning(f"Profiles directory not found: {PROFILES_DIR}")
        return 0
    
    profiles = list(PROFILES_DIR.glob("*.md"))
    profiles = [p for p in profiles if p.name != "_template.md"]
    
    logger.info(f"Found {len(profiles)} profiles to migrate")
    
    # Check for conflicts
    conflicts = []
    for profile in profiles:
        target = INDIVIDUALS_DIR / profile.name
        if target.exists():
            conflicts.append((profile.name, profile, target))
    
    if conflicts:
        logger.warning(f"Found {len(conflicts)} naming conflicts:")
        for name, src, dest in conflicts:
            logger.warning(f"  {name}: exists in both profiles/ and individuals/")
            logger.info(f"    profiles/ size: {src.stat().st_size} bytes, modified: {datetime.fromtimestamp(src.stat().st_mtime)}")
            logger.info(f"    individuals/ size: {dest.stat().st_size} bytes, modified: {datetime.fromtimestamp(dest.stat().st_mtime)}")
        
        if not dry_run:
            logger.info("  Strategy: Keep individuals/ version (newer system), archive profiles/ version")
    
    # Migrate non-conflicting profiles
    migrated = 0
    skipped = 0
    
    for profile in profiles:
        target = INDIVIDUALS_DIR / profile.name
        
        if target.exists():
            logger.info(f"  {'[DRY RUN] Would skip' if dry_run else 'Skipping'} {profile.name} (already exists in individuals/)")
            skipped += 1
        else:
            if not dry_run:
                shutil.copy2(profile, target)
            logger.info(f"  {'[DRY RUN] Would migrate' if dry_run else 'Migrated'} {profile.name}")
            migrated += 1
    
    logger.info(f"Summary: {migrated} migrated, {skipped} skipped (conflicts)")
    
    return 0


def phase3_update_database(dry_run: bool = True) -> int:
    """Update database markdown_path references"""
    logger.info("=== PHASE 3: Update Database Records ===")
    
    if not DB_PATH.exists():
        logger.warning(f"Database not found: {DB_PATH}")
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find all records pointing to profiles/
    cursor.execute("""
        SELECT id, full_name, markdown_path 
        FROM individuals 
        WHERE markdown_path LIKE '%/profiles/%'
    """)
    
    records = cursor.fetchall()
    logger.info(f"Found {len(records)} database records pointing to profiles/")
    
    if not dry_run:
        for record_id, name, old_path in records:
            new_path = old_path.replace("/profiles/", "/individuals/")
            cursor.execute(
                "UPDATE individuals SET markdown_path = ? WHERE id = ?",
                (new_path, record_id)
            )
            logger.info(f"  Updated {name}: {old_path} → {new_path}")
        
        conn.commit()
        logger.info("✓ Database records updated")
    else:
        for record_id, name, old_path in records[:5]:  # Show first 5
            new_path = old_path.replace("/profiles/", "/individuals/")
            logger.info(f"  [DRY RUN] Would update {name}: {old_path} → {new_path}")
        if len(records) > 5:
            logger.info(f"  ... and {len(records) - 5} more")
    
    conn.close()
    return 0


def phase4_archive_profiles(dry_run: bool = True) -> int:
    """Archive old profiles/ directory"""
    logger.info("=== PHASE 4: Archive profiles/ Directory ===")
    
    if not PROFILES_DIR.exists():
        logger.warning(f"Profiles directory not found: {PROFILES_DIR}")
        return 0
    
    if not dry_run:
        shutil.move(str(PROFILES_DIR), str(PROFILES_ARCHIVE))
        
        # Create README in archive
        readme = PROFILES_ARCHIVE / "README_ARCHIVE.md"
        readme.write_text(f"""# Archived Profiles Directory

**Archived:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Reason:** Consolidation to canonical `individuals/` directory

This directory contains profiles from the legacy `profiles/` system.
All active profiles have been migrated to `Knowledge/crm/individuals/`.

See consolidation analysis: `/home/.z/workspaces/con_9hza8oR18GLpOIVq/crm-profile-consolidation-analysis.md`
""")
        
        logger.info(f"✓ Archived profiles/ → {PROFILES_ARCHIVE}")
    else:
        logger.info(f"[DRY RUN] Would move profiles/ → {PROFILES_ARCHIVE}")
    
    return 0


def main(dry_run: bool = True) -> int:
    """Run all phases"""
    logger.info(f"Starting CRM profile consolidation {'[DRY RUN MODE]' if dry_run else '[LIVE MODE]'}")
    logger.info(f"Canonical directory: {INDIVIDUALS_DIR}")
    
    try:
        phase1_update_scripts(dry_run)
        phase2_migrate_profiles(dry_run)
        phase3_update_database(dry_run)
        phase4_archive_profiles(dry_run)
        
        logger.info("=" * 60)
        logger.info(f"{'DRY RUN COMPLETE' if dry_run else 'CONSOLIDATION COMPLETE'}")
        logger.info("=" * 60)
        
        if dry_run:
            logger.info("Run with --execute to apply changes")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during consolidation: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Consolidate CRM profiles to individuals/")
    parser.add_argument("--execute", action="store_true", help="Execute changes (default is dry-run)")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4], help="Run specific phase only")
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    if args.phase:
        phases = {
            1: phase1_update_scripts,
            2: phase2_migrate_profiles,
            3: phase3_update_database,
            4: phase4_archive_profiles
        }
        exit(phases[args.phase](dry_run))
    else:
        exit(main(dry_run))
