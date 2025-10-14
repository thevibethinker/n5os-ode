#!/usr/bin/env python3
"""
Stakeholder Profile Management System
Auto-creates and updates stakeholder profiles from calendar events and emails.
"""

# ======================================================================
# DEPRECATED - Use Knowledge/crm/profiles/ and crm_query.py instead
# This script is part of the legacy stakeholder system.
# Retained for historical reference only.
# ======================================================================


import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
CRM_PROFILES_DIR = WORKSPACE / "Knowledge/crm/individuals"
INDEX_FILE = CRM_PROFILES_DIR / "index.jsonl"
TEMPLATE_FILE = CRM_PROFILES_DIR / "_template.md"

# Domain patterns for external detection
CAREERSPAN_DOMAINS = ["mycareerspan.com", "theapply.ai"]
COMMON_SERVICES = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]


class StakeholderIndex:
    """Manages the stakeholder index file."""
    
    def __init__(self, index_path: Path = INDEX_FILE):
        self.index_path = index_path
        self.entries = {}
        self.load()
    
    def load(self):
        """Load index from JSONL file."""
        if not self.index_path.exists():
            logger.warning(f"Index file not found: {self.index_path}")
            return
        
        self.entries = {}
        with open(self.index_path, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    # Index by email (lowercase)
                    email = entry.get('email', '').lower()
                    if email:
                        self.entries[email] = entry
        
        logger.info(f"Loaded {len(self.entries)} stakeholder profiles")
    
    def save(self):
        """Save index to JSONL file."""
        with open(self.index_path, 'w') as f:
            for entry in self.entries.values():
                f.write(json.dumps(entry) + '\n')
        logger.info(f"Saved {len(self.entries)} entries to index")
    
    def find_by_email(self, email: str) -> Optional[Dict]:
        """Find stakeholder by email."""
        return self.entries.get(email.lower())
    
    def add_entry(self, email: str, slug: str, name: str, 
                  organization: str, lead_type: str, status: str = "active"):
        """Add new stakeholder entry to index."""
        entry = {
            "email": email.lower(),
            "slug": slug,
            "name": name,
            "organization": organization,
            "lead_type": lead_type,
            "status": status,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "file": f"Knowledge/crm/individuals/{slug}.md"
        }
        self.entries[email.lower()] = entry
        self.save()
        return entry
    
    def update_entry(self, email: str, **updates):
        """Update an existing entry."""
        email = email.lower()
        if email in self.entries:
            self.entries[email].update(updates)
            self.entries[email]['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            self.save()


def is_external_email(email: str) -> bool:
    """Check if email is external (not Careerspan team)."""
    email_lower = email.lower()
    
    # Check if it's a Careerspan/team domain
    for domain in CAREERSPAN_DOMAINS:
        if domain in email_lower:
            return False
    
    return True


def generate_slug(name: str) -> str:
    """Generate URL-safe slug from name."""
    # Remove special chars, lowercase, replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def extract_domain(email: str) -> str:
    """Extract domain from email address."""
    return email.split('@')[-1] if '@' in email else ''


def infer_organization_from_email(email: str) -> str:
    """Infer organization from email domain."""
    domain = extract_domain(email)
    
    # Common email services -> use domain as-is
    if domain in COMMON_SERVICES:
        return f"Personal ({domain})"
    
    # Try to clean up domain into company name
    # e.g., "cornell.edu" -> "Cornell", "withnira.com" -> "Nira"
    org = domain.replace('.edu', '').replace('.com', '').replace('.org', '')
    org = org.replace('with', '').strip()  # "withnira" -> "nira"
    
    if org:
        return org.title()
    
    return domain


def create_profile_content(
    name: str,
    email: str,
    organization: str,
    role: str,
    lead_type: str,
    relationship_context: str,
    interaction_summary: str,
    email_threads: List[str] = None,
    calendar_ids: List[str] = None,
    first_contact_date: str = None
) -> str:
    """Generate profile markdown content."""
    
    today = datetime.now().strftime("%Y-%m-%d")
    first_contact = first_contact_date or today
    slug = generate_slug(name)
    email_threads = email_threads or []
    calendar_ids = calendar_ids or []
    
    content = f"""---
name: "{name}"
email_primary: "{email}"
email_aliases: []
organization: "{organization}"
role: "{role}"
first_contact: "{first_contact}"
last_updated: "{today}"
lead_type: "{lead_type}"
status: "active"
interaction_count: 1
last_interaction: "{today}"
---

# {name}

**Organization:** {organization}  
**Role:** {role}  
**Email:** {email}  
**Lead Type:** {lead_type}  
**Status:** Active  
**First Contact:** {first_contact}  
**Last Updated:** {today}

---

## Relationship Context

### How We Met
{relationship_context}

### Key Objectives
**Their asks:**
- [To be determined from interactions]

**V's asks:**
- [To be determined from interactions]

**Open loops:**
- [To be tracked over time]

---

## Interaction History

{interaction_summary}

---

## Quick Reference

**Contact Preferences:** [To be determined]  
**Timezone:** [To be determined]  
**LinkedIn:** [To be added]  
**Company Website:** [To be added]  

**Notable Context:**
- [To be added as learned]

---

## Auto-Generated Metadata

**Email thread IDs:** {', '.join(email_threads) if email_threads else '[None yet]'}  
**Meeting IDs:** {', '.join(calendar_ids) if calendar_ids else '[None yet]'}  
**Last email:** {today}  
**Last meeting:** [Pending]  
**Response rate:** [To be tracked]
"""
    
    return content


def create_profile_file(
    email: str,
    name: str,
    organization: str,
    role: str,
    lead_type: str,
    relationship_context: str,
    interaction_summary: str,
    **kwargs
) -> Path:
    """Create a new stakeholder profile file."""
    
    slug = generate_slug(name)
    profile_path = CRM_PROFILES_DIR / f"{slug}.md"
    
    # Check if already exists
    if profile_path.exists():
        logger.info(f"Profile already exists: {profile_path}")
        return profile_path
    
    # Generate content
    content = create_profile_content(
        name=name,
        email=email,
        organization=organization,
        role=role,
        lead_type=lead_type,
        relationship_context=relationship_context,
        interaction_summary=interaction_summary,
        **kwargs
    )
    
    # Write file
    profile_path.write_text(content)
    logger.info(f"Created profile: {profile_path}")
    
    # Update index
    index = StakeholderIndex()
    index.add_entry(
        email=email,
        slug=slug,
        name=name,
        organization=organization,
        lead_type=lead_type
    )
    
    return profile_path


def update_profile_with_interaction(
    email: str,
    interaction_date: str,
    interaction_type: str,
    summary: str,
    linked_artifact: Optional[str] = None
):
    """Append new interaction to existing profile."""
    
    index = StakeholderIndex()
    entry = index.find_by_email(email)
    
    if not entry:
        logger.warning(f"No profile found for {email}")
        return None
    
    profile_path = WORKSPACE / entry['file']
    
    if not profile_path.exists():
        logger.error(f"Profile file missing: {profile_path}")
        return None
    
    # Read existing content
    content = profile_path.read_text()
    
    # Create new interaction entry
    artifact_line = f"\n**Linked artifact:** `file '{linked_artifact}'`" if linked_artifact else ""
    
    new_interaction = f"""
### {interaction_date}: {interaction_type}
**Type:** {interaction_type}  
**Summary:** {summary}{artifact_line}

---
"""
    
    # Insert before "## Quick Reference" section
    if "## Quick Reference" in content:
        parts = content.split("## Quick Reference")
        updated_content = parts[0] + new_interaction + "\n## Quick Reference" + parts[1]
    else:
        # Fallback: append before metadata section
        parts = content.split("## Auto-Generated Metadata")
        updated_content = parts[0] + new_interaction + "\n## Auto-Generated Metadata" + parts[1]
    
    # Update last_updated in frontmatter
    today = datetime.now().strftime("%Y-%m-%d")
    updated_content = re.sub(
        r'last_updated: "[^"]*"',
        f'last_updated: "{today}"',
        updated_content
    )
    updated_content = re.sub(
        r'last_interaction: "[^"]*"',
        f'last_interaction: "{interaction_date}"',
        updated_content
    )
    
    # Increment interaction_count
    match = re.search(r'interaction_count: (\d+)', updated_content)
    if match:
        count = int(match.group(1)) + 1
        updated_content = re.sub(
            r'interaction_count: \d+',
            f'interaction_count: {count}',
            updated_content
        )
    
    # Write back
    profile_path.write_text(updated_content)
    logger.info(f"Updated profile: {profile_path}")
    
    # Update index
    index.update_entry(email, last_interaction=interaction_date)
    
    return profile_path


def update_profile_from_transcript(
    email: str,
    meeting_date: str,
    meeting_title: str,
    transcript_summary: str,
    key_points: List[str],
    outcomes: List[str],
    linked_artifact: str,
    dry_run: bool = False
) -> Optional[Path]:
    """
    Update stakeholder profile after meeting transcript is processed.
    Uses safe updater to append interaction without overwriting.
    
    Args:
        email: Stakeholder email
        meeting_date: Meeting date (YYYY-MM-DD)
        meeting_title: Meeting title
        transcript_summary: LLM-generated summary
        key_points: List of key discussion points
        outcomes: List of action items/decisions
        linked_artifact: Path to meeting note (relative to workspace)
        dry_run: If True, preview changes without applying
    
    Returns:
        Path to updated profile, or None if profile not found
    """
    
    # Import safe updater
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from safe_stakeholder_updater import append_interaction
    
    # Find profile
    index = StakeholderIndex()
    entry = index.find_by_email(email)
    
    if not entry:
        logger.warning(f"No profile found for {email} - skipping update")
        return None
    
    profile_path = WORKSPACE / entry['file']
    
    if not profile_path.exists():
        logger.error(f"Profile file missing: {profile_path}")
        return None
    
    # Append interaction safely
    try:
        updated_path, diff = append_interaction(
            profile_path=profile_path,
            interaction_date=meeting_date,
            interaction_title=meeting_title,
            summary=transcript_summary,
            key_points=key_points,
            outcomes=outcomes,
            linked_artifact=linked_artifact,
            dry_run=dry_run
        )
        
        if not dry_run:
            logger.info(f"Profile updated: {updated_path}")
            
            # Update index last_interaction date
            index.update_entry(email, last_interaction=meeting_date)
        else:
            logger.info(f"[DRY RUN] Would update profile: {profile_path}")
        
        return updated_path
    
    except Exception as e:
        logger.error(f"Failed to update profile for {email}: {e}")
        return None


if __name__ == "__main__":
    # Test functionality
    logger.info("Stakeholder Manager initialized")
    
    # Example: Create a test profile
    # create_profile_file(
    #     email="test@example.com",
    #     name="Test Person",
    #     organization="Example Corp",
    #     role="VP of Testing",
    #     lead_type="LD-COM",
    #     relationship_context="Met through mutual connection at conference",
    #     interaction_summary="Initial email exchange about partnership opportunity"
    # )
    
    # Example: Update profile from meeting
    # update_profile_from_transcript(
    #     email="hamoon@futurefit.ai",
    #     meeting_date="2025-10-15",
    #     meeting_title="Follow-up: Partnership Discussion",
    #     transcript_summary="Discussed specific use cases for integration",
    #     key_points=["Agreed on embedded widget approach", "Reviewed technical requirements"],
    #     outcomes=["V to send technical spec", "Hamoon to review internally"],
    #     linked_artifact="N5/records/meetings/2025-10-15_hamoon-ekhtiari/meeting_note.md",
    #     dry_run=True
    # )
