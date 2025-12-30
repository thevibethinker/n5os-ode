#!/usr/bin/env python3
"""
CRM Reconciliation Script - Merges Legacy CRM into V3

This script:
1. Reads all Legacy profiles from Personal/Knowledge/CRM/individuals/
2. Reads all V3 profiles from N5/crm_v3/profiles/
3. Merges the rich content from Legacy into V3 format
4. Adds the new Interaction Timeline section
5. Outputs to N5/crm_v3/profiles/ (canonical location)

Usage:
    python3 N5/scripts/crm_reconciliation.py --dry-run     # Preview changes
    python3 N5/scripts/crm_reconciliation.py               # Execute merge
    python3 N5/scripts/crm_reconciliation.py --profile alex-caveny  # Single profile
"""

import argparse
import logging
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
LEGACY_CRM = WORKSPACE / "Personal/Knowledge/CRM/individuals"
V3_CRM = WORKSPACE / "N5/crm_v3/profiles"
BACKUP_DIR = WORKSPACE / "N5/crm_v3/backups"

# Enhanced V3 profile template with Interaction Timeline
V3_TEMPLATE = """---
created: {created}
last_edited: {last_edited}
version: {version}
source: {source}
person_id: {person_id}
email: {email}
linkedin_url: {linkedin_url}
category: {category}
relationship_strength: {relationship_strength}
enrichment_status: {enrichment_status}
---

# {display_name}

## Quick Reference
**Status:** {status}
**Organization:** {organization}
**Role:** {role}
**Location:** {location}
**Last Contact:** {last_contact}
**Relationship Strength:** {relationship_strength}

## Contact Information
- **Email:** {email}
- **LinkedIn:** {linkedin_url}
- **Phone:** {phone}

## Professional Background
{professional_background}

## Relationship Context
{relationship_context}

## Value Exchange
{value_exchange}

## Key Insights & Communication Style
{key_insights}

## Topics of Expertise
{topics_of_expertise}

---

## Interaction Timeline

{interaction_timeline}

---

## Enrichment Data

### Aviato Intelligence
{aviato_intel}

### Gmail Intelligence
{gmail_intel}

---

## Action Items & Follow-Ups
{action_items}

## Notes
{notes}
"""


def normalize_person_id(filename: str) -> str:
    """Normalize filename to person_id format."""
    name = filename.replace('.md', '').replace('.yaml', '')
    # Handle V3 naming: FirstName_LastName_handle.yaml -> firstname-lastname
    if '_' in name:
        parts = name.split('_')
        if len(parts) >= 2:
            return f"{parts[0].lower()}-{parts[1].lower()}"
    return name.lower().replace('_', '-')


def load_legacy_profile(path: Path) -> Dict[str, Any]:
    """Load and parse a Legacy CRM markdown profile."""
    content = path.read_text()
    
    # Extract YAML frontmatter
    frontmatter = {}
    if content.startswith('---'):
        end_idx = content.find('---', 3)
        if end_idx > 0:
            try:
                frontmatter = yaml.safe_load(content[3:end_idx]) or {}
            except yaml.YAMLError:
                pass
            content = content[end_idx + 3:].strip()
    
    # Parse sections
    sections = {}
    current_section = "header"
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith('## '):
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[3:].strip().lower()
            current_content = []
        else:
            current_content.append(line)
    
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return {
        'frontmatter': frontmatter,
        'sections': sections,
        'raw_content': path.read_text()
    }


def load_v3_profile(path: Path) -> Dict[str, Any]:
    """Load and parse a V3 CRM YAML/markdown profile."""
    content = path.read_text()
    
    # Extract YAML frontmatter
    frontmatter = {}
    if content.startswith('---'):
        end_idx = content.find('---', 3)
        if end_idx > 0:
            try:
                frontmatter = yaml.safe_load(content[3:end_idx]) or {}
            except yaml.YAMLError:
                pass
            content = content[end_idx + 3:].strip()
    
    return {
        'frontmatter': frontmatter,
        'content': content,
        'raw': path.read_text()
    }


def extract_field(sections: Dict, field_names: List[str], default: str = "*Not yet enriched*") -> str:
    """Extract a field from sections, trying multiple possible names."""
    for name in field_names:
        if name in sections:
            return sections[name]
    return default


def merge_profiles(legacy: Dict, v3: Optional[Dict], person_id: str) -> str:
    """Merge Legacy and V3 profiles into enhanced V3 format."""
    
    legacy_fm = legacy.get('frontmatter', {})
    legacy_sections = legacy.get('sections', {})
    
    v3_fm = v3.get('frontmatter', {}) if v3 else {}
    
    # Determine best values from both sources
    email = v3_fm.get('email') or legacy_fm.get('email', '*Not yet enriched*')
    linkedin = v3_fm.get('linkedin_url') or legacy_fm.get('linkedin', '*Not yet enriched*')
    category = v3_fm.get('category') or legacy_fm.get('stakeholder_type', 'CONTACT')
    
    # Extract name from header or person_id
    display_name = person_id.replace('-', ' ').title()
    header = legacy_sections.get('header', '')
    if header:
        name_match = re.search(r'#\s*(.+)', header)
        if name_match:
            display_name = name_match.group(1).strip()
    
    # Extract fields from Legacy sections
    basic_info = legacy_sections.get('basic information', '')
    org_match = re.search(r'\*\*Organization\*\*:\s*(.+)', basic_info)
    role_match = re.search(r'\*\*Role\*\*:\s*(.+)', basic_info)
    location_match = re.search(r'\*\*Location\*\*:\s*(.+)', basic_info)
    
    organization = org_match.group(1).strip() if org_match else '*Not yet enriched*'
    role = role_match.group(1).strip() if role_match else '*Not yet enriched*'
    location = location_match.group(1).strip() if location_match else '*Not yet enriched*'
    
    # Relationship context
    rel_context = legacy_sections.get('relationship context', '')
    status_match = re.search(r'\*\*Relationship Status\*\*:\s*(.+)', rel_context)
    status = status_match.group(1).strip() if status_match else category
    
    # Last contact from V3 or Legacy
    last_contact = v3_fm.get('last_contact', '')
    if not last_contact:
        contact_match = re.search(r'\*\*(?:Most Recent Meeting|Last Contact)\*\*:\s*([\d-]+)', legacy.get('raw_content', ''))
        last_contact = contact_match.group(1) if contact_match else '*Unknown*'
    
    # Build interaction timeline from meeting history
    meeting_history = legacy_sections.get('meeting history', '')
    interaction_timeline = "*No interactions recorded yet.*"
    if meeting_history and meeting_history.strip():
        # Convert meeting history to timeline format
        timeline_entries = []
        meetings = re.findall(r'###\s*([\d-]+):\s*(.+?)(?=###|\Z)', meeting_history, re.DOTALL)
        for date, details in meetings:
            summary = details.strip()[:200] + "..." if len(details.strip()) > 200 else details.strip()
            timeline_entries.append(f"### {date} | Meeting\n{summary}")
        
        if timeline_entries:
            interaction_timeline = '\n\n'.join(timeline_entries)
    
    # Fill template
    merged = V3_TEMPLATE.format(
        created=legacy_fm.get('created', v3_fm.get('created', datetime.now().strftime('%Y-%m-%d'))),
        last_edited=datetime.now().strftime('%Y-%m-%d'),
        version='2.0',  # Reconciled version
        source='reconciled_v3',
        person_id=person_id,
        email=email,
        linkedin_url=linkedin,
        category=category.upper() if isinstance(category, str) else 'CONTACT',
        relationship_strength=v3_fm.get('relationship_strength', 'moderate'),
        enrichment_status='legacy_imported',
        display_name=display_name,
        status=status,
        organization=organization,
        role=role,
        location=location,
        last_contact=last_contact,
        phone=legacy_fm.get('phone', '*Not yet enriched*'),
        professional_background=extract_field(legacy_sections, ['professional background'], '*Needs enrichment from Aviato/LinkedIn*'),
        relationship_context=extract_field(legacy_sections, ['relationship context'], '*Not yet documented*'),
        value_exchange=extract_field(legacy_sections, ['value exchange'], '*Not yet documented*'),
        key_insights=extract_field(legacy_sections, ['key insights & patterns', 'key insights', 'communication style'], '*Not yet documented*'),
        topics_of_expertise=extract_field(legacy_sections, ['topics of expertise', 'expertise'], '*Not yet documented*'),
        interaction_timeline=interaction_timeline,
        aviato_intel='*Not yet enriched - run enrichment worker*',
        gmail_intel='*Not yet enriched - run gmail sync*',
        action_items=extract_field(legacy_sections, ['action items & follow-ups', 'action items'], '*None pending*'),
        notes=extract_field(legacy_sections, ['notes'], '*No additional notes*')
    )
    
    return merged


def create_new_v3_from_legacy(legacy: Dict, person_id: str) -> str:
    """Create a new V3 profile from Legacy-only data."""
    return merge_profiles(legacy, None, person_id)


def reconcile_profiles(dry_run: bool = True, single_profile: Optional[str] = None):
    """Main reconciliation logic."""
    
    # Create backup directory
    if not dry_run:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Index Legacy profiles
    legacy_profiles = {}
    for path in LEGACY_CRM.glob('*.md'):
        # Skip stub files
        content = path.read_text()
        if 'This CRM profile now lives at' in content:
            continue
        
        person_id = normalize_person_id(path.name)
        legacy_profiles[person_id] = path
    
    # Index V3 profiles
    v3_profiles = {}
    for path in V3_CRM.glob('*.yaml'):
        person_id = normalize_person_id(path.name)
        v3_profiles[person_id] = path
    
    logger.info(f"Found {len(legacy_profiles)} Legacy profiles")
    logger.info(f"Found {len(v3_profiles)} V3 profiles")
    
    # Filter if single profile requested
    if single_profile:
        single_id = normalize_person_id(single_profile)
        if single_id in legacy_profiles:
            legacy_profiles = {single_id: legacy_profiles[single_id]}
        else:
            logger.error(f"Profile {single_profile} not found in Legacy CRM")
            return
        v3_profiles = {k: v for k, v in v3_profiles.items() if k == single_id}
    
    stats = {
        'merged': 0,
        'created': 0,
        'skipped': 0,
        'errors': 0
    }
    
    # Process all Legacy profiles
    for person_id, legacy_path in legacy_profiles.items():
        try:
            legacy_data = load_legacy_profile(legacy_path)
            
            # Check if V3 exists
            v3_data = None
            v3_filename = None
            
            for v3_id, v3_path in v3_profiles.items():
                if v3_id == person_id:
                    v3_data = load_v3_profile(v3_path)
                    v3_filename = v3_path.name
                    break
            
            # Generate output filename
            if v3_filename:
                output_filename = v3_filename
            else:
                # Create new filename in V3 format
                name_parts = person_id.split('-')
                if len(name_parts) >= 2:
                    output_filename = f"{name_parts[0].title()}_{name_parts[1].title()}_{person_id.replace('-', '')}.yaml"
                else:
                    output_filename = f"{person_id.replace('-', '_')}.yaml"
            
            output_path = V3_CRM / output_filename
            
            # Merge or create
            if v3_data:
                merged_content = merge_profiles(legacy_data, v3_data, person_id)
                action = "MERGE"
                stats['merged'] += 1
            else:
                merged_content = create_new_v3_from_legacy(legacy_data, person_id)
                action = "CREATE"
                stats['created'] += 1
            
            if dry_run:
                logger.info(f"[DRY-RUN] {action}: {person_id} -> {output_filename}")
            else:
                # Backup existing V3 if it exists
                if output_path.exists():
                    backup_path = BACKUP_DIR / f"{backup_time}_{output_filename}"
                    backup_path.write_text(output_path.read_text())
                
                # Write merged content
                output_path.write_text(merged_content)
                logger.info(f"{action}: {person_id} -> {output_filename}")
                
        except Exception as e:
            logger.error(f"Error processing {person_id}: {e}")
            stats['errors'] += 1
    
    # Summary
    print("\n" + "="*50)
    print("RECONCILIATION SUMMARY")
    print("="*50)
    print(f"Merged (Legacy + V3):  {stats['merged']}")
    print(f"Created (Legacy only): {stats['created']}")
    print(f"Skipped:               {stats['skipped']}")
    print(f"Errors:                {stats['errors']}")
    print(f"Total processed:       {stats['merged'] + stats['created']}")
    
    if dry_run:
        print("\n[DRY-RUN MODE] No files were modified.")
        print("Run without --dry-run to execute reconciliation.")


def main():
    parser = argparse.ArgumentParser(description='Reconcile Legacy CRM into V3')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--profile', type=str, help='Process single profile by person-id')
    
    args = parser.parse_args()
    
    reconcile_profiles(dry_run=args.dry_run, single_profile=args.profile)


if __name__ == '__main__':
    main()

