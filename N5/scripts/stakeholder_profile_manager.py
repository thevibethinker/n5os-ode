#!/usr/bin/env python3
"""
Stakeholder Profile Manager
Creates and manages stakeholder profiles for meeting attendees
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytz

MEETINGS_DIR = Path("/home/workspace/N5/records/meetings")
TIMEZONE = pytz.timezone('America/New_York')

STAKEHOLDER_TYPE_MAP = {
    'LD-INV': 'Investor',
    'LD-HIR': 'Candidate',
    'LD-COM': 'Community',
    'LD-NET': 'Partner',
    'LD-GEN': 'General'
}


def _sanitize_name(name: str) -> str:
    """Convert name to filesystem-safe format"""
    # Lowercase, replace spaces with hyphens
    name = name.lower().strip()
    # Remove or replace special characters
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    return name


def _format_datetime(dt_str: str) -> str:
    """Format datetime for display in profile"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        dt_et = dt.astimezone(TIMEZONE)
        return dt_et.strftime('%Y-%m-%d %I:%M %p ET')
    except Exception:
        return dt_str


def _get_timestamp() -> str:
    """Get current timestamp in ET timezone"""
    return datetime.now(TIMEZONE).strftime('%Y-%m-%d')


def _extract_organization_type(organization: str) -> str:
    """Try to infer organization type"""
    org_lower = organization.lower()
    if any(keyword in org_lower for keyword in ['ventures', 'capital', 'partners', 'fund']):
        return 'Investment Firm'
    elif any(keyword in org_lower for keyword in ['university', 'college', 'school']):
        return 'Educational Institution'
    elif any(keyword in org_lower for keyword in ['inc', 'corp', 'llc', 'ltd']):
        return 'Company'
    else:
        return 'Organization'


def _determine_stakeholder_type(tags: dict) -> str:
    """Determine stakeholder type from tags"""
    stakeholder_tag = tags.get('stakeholder', '')
    return STAKEHOLDER_TYPE_MAP.get(stakeholder_tag, 'General')


def _format_tags_display(tags: dict) -> str:
    """Format tags for display in Context section"""
    tag_parts = []
    if tags.get('stakeholder'):
        tag_parts.append(f"[{tags['stakeholder']}]")
    if tags.get('timing'):
        tag_parts.append(f"[{tags['timing']}]")
    if tags.get('priority'):
        tag_parts.append('*' if tags['priority'] == 'critical' else '')
    
    return ' '.join(tag_parts)


def _create_profile_template(
    name: str,
    email: str,
    organization: str,
    stakeholder_type: str,
    meeting: dict,
    tags: dict,
    email_context: dict
) -> str:
    """Generate profile markdown content"""
    
    org_type = _extract_organization_type(organization)
    meeting_date = _format_datetime(meeting['start']['dateTime'])
    tags_display = _format_tags_display(tags)
    today = _get_timestamp()
    
    # Extract purpose and context from meeting description
    description = meeting.get('description', '')
    purpose = "TBD"
    context = "TBD"
    
    # Simple extraction of Purpose and Context
    lines = description.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('Purpose:'):
            purpose = line.replace('Purpose:', '').strip()
        elif line.startswith('Context:'):
            # Context might span multiple lines
            context_lines = [line.replace('Context:', '').strip()]
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].startswith('---'):
                context_lines.append(lines[j].strip())
                j += 1
            context = ' '.join(context_lines)
    
    # Email interaction section
    email_section = ""
    if email_context and email_context.get('threads'):
        for thread in email_context['threads']:
            email_section += f"\n### {thread['date']} — {thread['subject']}\n"
            email_section += f"{thread['snippet']}\n"
    else:
        email_section = "\n*No prior email interactions found*\n"
    
    # Stakeholder-specific section name
    section_map = {
        'Investor': 'Investment Focus',
        'Candidate': 'Skills & Experience',
        'Partner': 'Partnership Details',
        'Community': 'Community Involvement',
        'General': 'Additional Context'
    }
    specific_section = section_map.get(stakeholder_type, 'Additional Context')
    
    # Priority extraction
    priority = "Critical" if tags.get('priority') == 'critical' else "Normal"
    
    # Accommodation extraction (A-0, A-1, A-2)
    accommodation = tags.get('accommodation', 'A-0')
    
    template = f"""# {name} — {organization}

**Role:** TBD  
**Email:** {email}  
**Organization:** {organization} ({org_type})  
**Stakeholder Type:** {stakeholder_type}  
**First Meeting:** {meeting_date}  
**Status:** Active

---

## Context from Howie

Howie scheduled this meeting with N5OS tags: {tags_display}

Purpose: {purpose}

Context: {context}

---

## Email Interaction History
{email_section}

---

## Research Notes

### Background
- *Research to be added*

### {specific_section}
- *Research to be added*

### Recent Activity
- *Research to be added*

---

## Meeting History

### {meeting_date} — {meeting['summary']} (Scheduled)
- **Type:** Discovery
- **Accommodation:** {accommodation}
- **Priority:** {priority}
- **Prep Status:** Research in progress

---

## Relationship Notes

- First touchpoint via calendar scheduling
- *Relationship tracking to be added*

---

**Last Updated:** {today} by Zo (stakeholder_profile_manager.py)
"""
    
    return template


def create_stakeholder_profile(
    name: str,
    email: str,
    organization: str,
    stakeholder_type: str,
    meeting: dict,
    tags: dict,
    email_context: dict
) -> str:
    """
    Create new stakeholder profile
    
    Args:
        name: Full name
        email: Email address
        organization: Organization name
        stakeholder_type: investor/candidate/partner/community/general
        meeting: dict with meeting details (title, date, time, description)
        tags: dict with N5OS tags extracted from meeting
        email_context: dict with Gmail thread summaries
    
    Returns:
        str: Path to created profile.md
    """
    
    # Generate directory name
    meeting_date = datetime.fromisoformat(meeting['start']['dateTime'].replace('Z', '+00:00'))
    date_str = meeting_date.strftime('%Y-%m-%d')
    name_sanitized = _sanitize_name(name)
    org_sanitized = _sanitize_name(organization) if organization else ""
    
    if org_sanitized:
        dir_name = f"{date_str}-{name_sanitized}-{org_sanitized}"
    else:
        dir_name = f"{date_str}-{name_sanitized}"
    
    profile_dir = MEETINGS_DIR / dir_name
    
    # Handle naming collisions
    if profile_dir.exists():
        counter = 2
        while profile_dir.exists():
            if org_sanitized:
                dir_name = f"{date_str}-{name_sanitized}-{org_sanitized}-{counter}"
            else:
                dir_name = f"{date_str}-{name_sanitized}-{counter}"
            profile_dir = MEETINGS_DIR / dir_name
            counter += 1
    
    # Create directory
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    # Create profile.md
    profile_path = profile_dir / "profile.md"
    profile_content = _create_profile_template(
        name, email, organization, stakeholder_type, meeting, tags, email_context
    )
    
    with open(profile_path, 'w') as f:
        f.write(profile_content)
    
    print(f"✅ Created stakeholder profile: {profile_path}")
    
    # Return relative path from workspace root
    return str(profile_path.relative_to('/home/workspace'))


def find_stakeholder_profile(email: str) -> Optional[str]:
    """
    Search for existing profile by email
    
    Args:
        email: Stakeholder email to search for
    
    Returns:
        str: Path to profile.md if found, None otherwise
    """
    
    if not MEETINGS_DIR.exists():
        return None
    
    # Case-insensitive search through all profile.md files
    email_lower = email.lower()
    
    for profile_file in MEETINGS_DIR.glob("*/profile.md"):
        try:
            with open(profile_file, 'r') as f:
                content = f.read()
                # Look for email in the header section
                if f"**Email:** {email}" in content or email_lower in content.lower():
                    # Return relative path from workspace root
                    return str(profile_file.relative_to('/home/workspace'))
        except Exception as e:
            print(f"⚠️  Error reading {profile_file}: {e}")
            continue
    
    return None


def append_meeting_to_profile(
    profile_path: str,
    meeting: dict,
    tags: dict
) -> None:
    """
    Add new meeting to existing profile's meeting history
    
    Args:
        profile_path: Path to profile.md (relative or absolute)
        meeting: dict with meeting details
        tags: dict with N5OS tags
    """
    
    # Convert to absolute path if needed
    if not profile_path.startswith('/'):
        profile_path = f"/home/workspace/{profile_path}"
    
    profile_file = Path(profile_path)
    
    if not profile_file.exists():
        print(f"⚠️  Profile not found: {profile_path}")
        return
    
    # Read existing content
    with open(profile_file, 'r') as f:
        content = f.read()
    
    # Format new meeting entry
    meeting_date = _format_datetime(meeting['start']['dateTime'])
    priority = "Critical" if tags.get('priority') == 'critical' else "Normal"
    accommodation = tags.get('accommodation', 'A-0')
    
    new_meeting_entry = f"""
### {meeting_date} — {meeting['summary']} (Scheduled)
- **Type:** Follow-up
- **Accommodation:** {accommodation}
- **Priority:** {priority}
- **Prep Status:** Research in progress
"""
    
    # Find the Meeting History section and append
    meeting_history_marker = "## Meeting History"
    if meeting_history_marker in content:
        # Insert after the section header
        parts = content.split(meeting_history_marker)
        # Find the next section (starts with ##)
        after_section = parts[1]
        next_section_match = re.search(r'\n## ', after_section)
        
        if next_section_match:
            # Insert before next section
            insert_pos = next_section_match.start()
            new_content = (
                parts[0] + meeting_history_marker + 
                after_section[:insert_pos] + 
                new_meeting_entry +
                after_section[insert_pos:]
            )
        else:
            # Append to end of Meeting History section
            new_content = (
                parts[0] + meeting_history_marker + 
                after_section + new_meeting_entry
            )
    else:
        # Meeting History section doesn't exist - shouldn't happen with template
        print(f"⚠️  Meeting History section not found in {profile_path}")
        return
    
    # Update Last Updated footer
    today = _get_timestamp()
    new_content = re.sub(
        r'\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}',
        f'**Last Updated:** {today}',
        new_content
    )
    
    # Write back
    with open(profile_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Appended meeting to profile: {profile_file.name}")


def update_stakeholder_profile(
    profile_path: str,
    meeting: dict,
    tags: dict
) -> None:
    """
    Update existing profile with new meeting
    
    Args:
        profile_path: Path to existing profile.md
        meeting: dict with new meeting details
        tags: dict with N5OS tags
    """
    
    # For now, this is the same as appending a meeting
    # In the future, could add logic to update other sections
    append_meeting_to_profile(profile_path, meeting, tags)


if __name__ == "__main__":
    print("Testing stakeholder_profile_manager...")
    
    # Mock data
    mock_meeting = {
        'id': 'test123abc',
        'summary': 'Series A Discussion - Jane Smith',
        'description': '''[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline

Context: Jane replied to Mike's intro, expressed strong interest in Careerspan's ed-tech traction, wants to discuss funding terms and timeline.''',
        'start': {
            'dateTime': '2025-10-15T14:00:00-04:00'
        }
    }
    
    mock_tags = {
        'stakeholder': 'LD-INV',
        'timing': 'D5+',
        'priority': 'critical',
        'accommodation': 'A-0'
    }
    
    mock_email_context = {
        'threads': [
            {
                'date': '2025-10-10',
                'subject': 'Introduction - Vrijen Attawar (Careerspan)',
                'snippet': 'Jane replied to intro, expressed interest in ed-tech traction'
            }
        ]
    }
    
    # Test create profile
    profile_path = create_stakeholder_profile(
        name='Jane Smith',
        email='jane@acmeventures.com',
        organization='Acme Ventures',
        stakeholder_type='Investor',
        meeting=mock_meeting,
        tags=mock_tags,
        email_context=mock_email_context
    )
    
    print(f"✓ Profile created: {profile_path}")
    
    # Test find profile
    found_path = find_stakeholder_profile('jane@acmeventures.com')
    assert found_path == profile_path, "Profile should be found"
    print(f"✓ Profile found: {found_path}")
    
    print("\n✅ Basic tests passed!")
