#!/usr/bin/env python3
"""
Query Stakeholder Tags
Load verified tags from stakeholder profile for email generation

Author: Zo Computer
Version: 1.0.0
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('query_stakeholder_tags')


def find_stakeholder_profile(email: str, meeting_folder: Optional[Path] = None) -> Optional[Path]:
    """Find stakeholder profile by email address"""
    
    # If meeting folder provided, check there first
    if meeting_folder:
        profile_path = meeting_folder / "stakeholder_profile.md"
        if profile_path.exists():
            content = profile_path.read_text()
            if email.lower() in content.lower():
                return profile_path
    
    # Search all meeting folders
    records_dir = Path("/home/workspace/N5/records/meetings")
    if not records_dir.exists():
        records_dir = Path("/home/workspace/N5_mirror/records/meetings")
    
    if records_dir.exists():
        for profile_path in records_dir.rglob("stakeholder_profile.md"):
            try:
                content = profile_path.read_text()
                if email.lower() in content.lower():
                    return profile_path
            except Exception as e:
                logger.debug(f"Error reading {profile_path}: {e}")
                continue
    
    return None


def extract_verified_tags(profile_path: Path) -> List[str]:
    """Extract verified tags from stakeholder profile"""
    
    try:
        content = profile_path.read_text()
        
        # Find the verified tags section
        tags_section_match = re.search(
            r'##\s+Tags.*?###\s+Verified[^\n]*\n(.*?)(?=###|##|$)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        if not tags_section_match:
            logger.warning(f"No verified tags section found in {profile_path}")
            return []
        
        tags_text = tags_section_match.group(1)
        
        # Extract all hashtags
        tag_pattern = r'#[\w:]+(?::[\w]+)*'
        tags = re.findall(tag_pattern, tags_text)
        
        logger.info(f"Found {len(tags)} verified tags in profile")
        return tags
        
    except Exception as e:
        logger.error(f"Error extracting tags from {profile_path}: {e}")
        return []


def query_stakeholder_tags(email: str, meeting_folder: Optional[str] = None) -> Dict:
    """
    Query stakeholder profile and return verified tags
    
    Args:
        email: Stakeholder email address
        meeting_folder: Optional meeting folder path
        
    Returns:
        Dict with profile_path, tags, and metadata
    """
    
    folder_path = Path(meeting_folder) if meeting_folder else None
    
    # Find profile
    profile_path = find_stakeholder_profile(email, folder_path)
    
    if not profile_path:
        logger.info(f"No stakeholder profile found for {email}")
        return {
            "profile_found": False,
            "profile_path": None,
            "tags": [],
            "email": email
        }
    
    # Extract tags
    tags = extract_verified_tags(profile_path)
    
    return {
        "profile_found": True,
        "profile_path": str(profile_path),
        "tags": tags,
        "email": email,
        "tag_count": len(tags)
    }


if __name__ == "__main__":
    # Test with Hamoon
    result = query_stakeholder_tags("hamoon@futurefit.com")
    print(json.dumps(result, indent=2))
