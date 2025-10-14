#!/usr/bin/env python3
"""
B08 → CRM Profile Sync Script

Syncs Domain Authority & Track Record data from B08 blocks to permanent CRM profiles.
Run after B31 generation to update CRM with credibility assessments.
"""

import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
B08_PATTERN = WORKSPACE / "N5/records/meetings/*/B08_STAKEHOLDER_INTELLIGENCE.md"
CRM_DIR = WORKSPACE / "Knowledge/crm/individuals"

def extract_stakeholder_name(b08_path: Path) -> Optional[str]:
    """Extract stakeholder name from B08 content."""
    try:
        content = b08_path.read_text()
        
        # Look for CRM Integration section with profile path (supports both old profiles/ and new individuals/)
        crm_match = re.search(r'Knowledge/crm/(?:profiles|individuals)/([a-z-]+)\.md', content)
        if crm_match:
            return crm_match.group(1)
        
        logger.warning(f"Could not extract stakeholder name from {b08_path}")
        return None
    except Exception as e:
        logger.error(f"Error extracting name from {b08_path}: {e}")
        return None

def extract_domain_authority(b08_content: str) -> Optional[str]:
    """Extract Domain Authority section from B08 if present."""
    try:
        # Look for Domain Authority section
        match = re.search(
            r'## (?:SECTION 3: )?DOMAIN AUTHORITY & SOURCE CREDIBILITY(.*?)(?=## |\Z)',
            b08_content,
            re.DOTALL | re.IGNORECASE
        )
        
        if match:
            return match.group(1).strip()
        return None
    except Exception as e:
        logger.error(f"Error extracting domain authority: {e}")
        return None

def create_or_update_crm_profile(name: str, b08_path: Path, domain_authority_section: str):
    """Create or update CRM profile with B08 data."""
    
    crm_path = CRM_DIR / f"{name}.md"
    meeting_id = b08_path.parent.name
    timestamp = datetime.now().isoformat()
    
    # Read existing profile if it exists
    if crm_path.exists():
        logger.info(f"Updating existing CRM profile: {crm_path}")
        content = crm_path.read_text()
        
        # Update Domain Authority section
        if domain_authority_section:
            # Replace existing section or append if not present
            if "## Domain Authority & Source Credibility" in content:
                content = re.sub(
                    r'## Domain Authority & Source Credibility.*?(?=## |\Z)',
                    f"## Domain Authority & Source Credibility\n\n{domain_authority_section}\n\n",
                    content,
                    flags=re.DOTALL
                )
                logger.info(f"Updated Domain Authority section in {crm_path}")
            else:
                # Insert after Relationship Summary section
                insert_point = content.find("---\n\n## Meeting History")
                if insert_point == -1:
                    insert_point = content.find("## Notes")
                
                if insert_point > -1:
                    content = (
                        content[:insert_point] +
                        f"---\n\n## Domain Authority & Source Credibility\n\n{domain_authority_section}\n\n" +
                        content[insert_point:]
                    )
                    logger.info(f"Added Domain Authority section to {crm_path}")
                else:
                    # Append at end
                    content += f"\n\n---\n\n## Domain Authority & Source Credibility\n\n{domain_authority_section}\n"
        
        # Update Last Sync timestamp
        content = re.sub(
            r'\*\*Last Sync:\*\* \[Timestamp\]',
            f'**Last Sync:** {timestamp}',
            content
        )
        
        crm_path.write_text(content)
        logger.info(f"✅ Updated CRM profile: {crm_path}")
    
    else:
        logger.info(f"CRM profile doesn't exist yet: {crm_path}")
        logger.info(f"This should be created during meeting processing. Skipping for now.")

def sync_b08_to_crm(meeting_id: Optional[str] = None):
    """
    Sync B08 blocks to CRM profiles.
    
    Args:
        meeting_id: If provided, sync only this meeting. Otherwise sync all.
    """
    
    if not CRM_DIR.exists():
        CRM_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created CRM directory: {CRM_DIR}")
    
    # Find B08 files
    if meeting_id:
        b08_files = list((WORKSPACE / "N5/records/meetings").glob(f"{meeting_id}/B08_STAKEHOLDER_INTELLIGENCE.md"))
    else:
        b08_files = list((WORKSPACE / "N5/records/meetings").glob("*/B08_STAKEHOLDER_INTELLIGENCE.md"))
    
    logger.info(f"Found {len(b08_files)} B08 files to process")
    
    synced_count = 0
    skipped_count = 0
    
    for b08_path in b08_files:
        try:
            # Extract stakeholder name
            name = extract_stakeholder_name(b08_path)
            if not name:
                logger.warning(f"Skipping {b08_path} - could not extract name")
                skipped_count += 1
                continue
            
            # Read B08 content
            b08_content = b08_path.read_text()
            
            # Extract Domain Authority section
            domain_authority = extract_domain_authority(b08_content)
            
            if domain_authority:
                # Update CRM profile
                create_or_update_crm_profile(name, b08_path, domain_authority)
                synced_count += 1
            else:
                logger.info(f"No Domain Authority section in {b08_path} yet - skipping")
                skipped_count += 1
        
        except Exception as e:
            logger.error(f"Error processing {b08_path}: {e}", exc_info=True)
            skipped_count += 1
    
    logger.info(f"✅ Sync complete: {synced_count} updated, {skipped_count} skipped")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync B08 blocks to CRM profiles')
    parser.add_argument('--meeting-id', help='Sync only this meeting (optional)')
    
    args = parser.parse_args()
    
    sync_b08_to_crm(args.meeting_id)
