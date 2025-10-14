#!/usr/bin/env python3
"""
Phase 5: Legacy Profile Conversion
Converts legacy markdown profiles to YAML frontmatter format
"""
import argparse
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
PROFILES_DIR = WORKSPACE / "Knowledge/crm/profiles"
BACKUP_DIR = WORKSPACE / ".migration_backups" / f"phase5_legacy_conversion_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def has_frontmatter(content: str) -> bool:
    """Check if file already has YAML frontmatter"""
    return content.strip().startswith('---\n') and '\n---\n' in content[4:]

def extract_name_from_h1(content: str) -> Optional[str]:
    """Extract name from first H1 header"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else None

def extract_email(content: str) -> str:
    """Extract email from various formats in content"""
    # Pattern 1: Email: [Unknown]
    # Pattern 2: email@domain.com
    # Pattern 3: **Email:** something
    
    # Try explicit email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, content)
    if match:
        return match.group(0)
    
    return ""

def extract_organization(content: str) -> str:
    """Extract organization from content"""
    patterns = [
        r'\*\*Organization:\*\*\s*(.+?)(?:\n|$)',
        r'- \*\*Organization:\*\*\s*(.+?)(?:\n|$)',
        r'Organization:\s*(.+?)(?:\n|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            org = match.group(1).strip()
            # Filter out placeholders
            if not any(x in org.lower() for x in ['unknown', 'needs enrichment', '[', 'exact org']):
                return org
    
    return ""

def extract_role(content: str) -> str:
    """Extract role/title from content"""
    patterns = [
        r'\*\*Role:\*\*\s*(.+?)(?:\n|$)',
        r'- \*\*Role:\*\*\s*(.+?)(?:\n|$)',
        r'- Role:\s*(.+?)(?:\n|$)',
        r'Role:\s*(.+?)(?:\n|$)',
        r'\*\*Inferred role:\*\*\s*(.+?)(?:\n|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            role = match.group(1).strip()
            if not any(x in role.lower() for x in ['unknown', 'needs enrichment', '[']):
                return role
    
    return ""

def extract_first_contact(content: str) -> str:
    """Extract first contact date"""
    patterns = [
        r'Source.*?(\d{4}-\d{2}-\d{2})',
        r'meeting.*?(\d{4}-\d{2}-\d{2})',
        r'Last contact:\s*(\d{4}-\d{2}-\d{2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Try to extract any date
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        return date_match.group(1)
    
    return datetime.now().strftime('%Y-%m-%d')

def infer_lead_type(content: str) -> str:
    """Infer lead type from content"""
    content_lower = content.lower()
    
    if any(x in content_lower for x in ['investor', 'vc', 'funding']):
        return 'LD-INV'
    elif any(x in content_lower for x in ['hiring', 'recruit', 'candidate']):
        return 'LD-HIR'
    elif any(x in content_lower for x in ['advisor', 'coach', 'mentor', 'community']):
        return 'LD-COM'
    elif any(x in content_lower for x in ['partner', 'founder', 'operator']):
        return 'LD-NET'
    
    return 'LD-GEN'

def convert_profile(filepath: Path, dry_run: bool = False) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Convert a single profile to frontmatter format
    Returns: (success, error_message, preview_text)
    """
    try:
        content = filepath.read_text()
        
        # Check if already has frontmatter
        if has_frontmatter(content):
            return (True, "Already has frontmatter", None)
        
        # Extract metadata
        name = extract_name_from_h1(content) or filepath.stem.replace('-', ' ').title()
        email = extract_email(content)
        organization = extract_organization(content)
        role = extract_role(content)
        first_contact = extract_first_contact(content)
        lead_type = infer_lead_type(content)
        last_updated = datetime.now().strftime('%Y-%m-%d')
        
        # Build frontmatter
        frontmatter = f"""---
name: "{name}"
email_primary: "{email}"
email_aliases: []
organization: "{organization}"
role: "{role}"
first_contact: "{first_contact}"
last_updated: "{last_updated}"
lead_type: "{lead_type}"
status: "active"
interaction_count: 0
last_interaction: "{first_contact}"
---

"""
        
        new_content = frontmatter + content
        
        if dry_run:
            preview = f"\n{'='*60}\nFile: {filepath.name}\n{'='*60}\n"
            preview += frontmatter
            preview += f"\n[... {len(content)} bytes of original content preserved ...]\n"
            return (True, None, preview)
        
        # Write the new content
        filepath.write_text(new_content)
        logger.info(f"✓ Converted: {filepath.name}")
        return (True, None, None)
        
    except Exception as e:
        logger.error(f"✗ Error converting {filepath.name}: {e}")
        return (False, str(e), None)

def create_backup(profiles: List[Path]) -> bool:
    """Create backup of profiles before conversion"""
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        for profile in profiles:
            backup_file = BACKUP_DIR / profile.name
            shutil.copy2(profile, backup_file)
        
        logger.info(f"✓ Backup created: {BACKUP_DIR}")
        logger.info(f"  {len(profiles)} files backed up")
        return True
        
    except Exception as e:
        logger.error(f"✗ Backup failed: {e}")
        return False

def get_legacy_profiles() -> List[Path]:
    """Get list of profiles without frontmatter"""
    legacy_profiles = []
    
    for filepath in sorted(PROFILES_DIR.glob("*.md")):
        if filepath.name == "_template.md":
            continue
        
        content = filepath.read_text()
        if not has_frontmatter(content):
            legacy_profiles.append(filepath)
    
    return legacy_profiles

def main(dry_run: bool = False) -> int:
    try:
        logger.info("=== Phase 5: Legacy Profile Conversion ===")
        logger.info(f"Scanning: {PROFILES_DIR}")
        
        # Get legacy profiles
        legacy_profiles = get_legacy_profiles()
        total = len(legacy_profiles)
        
        if total == 0:
            logger.info("✓ No legacy profiles found - all profiles already have frontmatter")
            return 0
        
        logger.info(f"Found {total} legacy profiles to convert")
        
        if dry_run:
            logger.info("\n[DRY RUN MODE] - No files will be modified\n")
            
            previews = []
            for filepath in legacy_profiles[:3]:  # Show first 3 as preview
                success, error, preview = convert_profile(filepath, dry_run=True)
                if preview:
                    previews.append(preview)
            
            for preview in previews:
                print(preview)
            
            logger.info(f"\n[DRY RUN] Would convert {total} profiles")
            logger.info(f"Showing preview of first {len(previews)} conversions above")
            return 0
        
        # Create backup
        logger.info("\nCreating backup before conversion...")
        if not create_backup(legacy_profiles):
            logger.error("Backup failed - aborting conversion")
            return 1
        
        # Convert profiles
        logger.info("\nConverting profiles...")
        success_count = 0
        skip_count = 0
        errors = []
        
        for filepath in legacy_profiles:
            success, error, _ = convert_profile(filepath, dry_run=False)
            if success:
                if error and "Already has frontmatter" in error:
                    skip_count += 1
                else:
                    success_count += 1
            else:
                errors.append({"file": filepath.name, "error": error})
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("CONVERSION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total processed: {total}")
        logger.info(f"✓ Converted: {success_count}")
        logger.info(f"⊘ Skipped (already converted): {skip_count}")
        logger.info(f"✗ Errors: {len(errors)}")
        
        if errors:
            logger.warning("\nErrors encountered:")
            for err in errors:
                logger.warning(f"  - {err['file']}: {err['error']}")
        
        logger.info(f"\n✓ Backup location: {BACKUP_DIR}")
        logger.info(f"\n✓ Phase 5 Complete: {success_count}/{total} profiles converted")
        
        return 0 if len(errors) == 0 else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert legacy CRM profiles to frontmatter format")
    parser.add_argument("--dry-run", action="store_true", help="Preview conversion without modifying files")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run))
