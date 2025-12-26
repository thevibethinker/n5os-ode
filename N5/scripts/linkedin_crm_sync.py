#!/usr/bin/env python3
"""
LinkedIn → CRM Profile Sync

Enriches CRM profiles with LinkedIn data from Kondo webhook database.
ADDITIVE ONLY - never deletes existing profile data.

Version: 1.0.0
Created: 2025-12-10

Usage:
  python3 linkedin_crm_sync.py              # Sync all with LinkedIn data
  python3 linkedin_crm_sync.py --dry-run    # Preview changes
  python3 linkedin_crm_sync.py --name "John" # Sync specific person
"""

import argparse
import sqlite3
import json
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

LINKEDIN_DB = Path("/home/workspace/Knowledge/linkedin/linkedin.db")
CRM_PROFILES_DIR = Path("/home/workspace/N5/crm_v3/profiles")

def slugify(name: str) -> str:
    """Convert name to slug format."""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '_', slug)
    return slug.strip('_')

def get_linkedin_data(conn: sqlite3.Connection, name_filter: Optional[str] = None) -> list[dict]:
    """Fetch enriched LinkedIn conversation data."""
    query = """
        SELECT 
            id,
            participant_name,
            participant_email,
            linkedin_profile_url,
            connected_at,
            kondo_note,
            starred,
            contact_headline,
            contact_location,
            contact_picture_url,
            first_message_at,
            last_message_at,
            message_count,
            status,
            metadata
        FROM conversations
        WHERE participant_name IS NOT NULL
    """
    params = []
    if name_filter:
        query += " AND participant_name LIKE ?"
        params.append(f"%{name_filter}%")
    
    cursor = conn.execute(query, params)
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def find_matching_profile(name: str) -> Optional[Path]:
    """Find CRM profile matching the name. Requires first AND last name match."""
    if not name or name == 'Unknown':
        return None
    
    # Clean up name (remove emojis, special chars)
    clean_name = re.sub(r'[^\w\s]', '', name).strip()
    name_parts = clean_name.lower().split()
    
    if len(name_parts) < 2:
        return None  # Need at least first and last name
    
    first_name = name_parts[0]
    last_name = name_parts[-1]  # Use last part as last name
    
    # Try to find profile with both first AND last name in filename
    for profile in CRM_PROFILES_DIR.glob("*.yaml"):
        stem_lower = profile.stem.lower()
        # Both first and last name must be present
        if first_name in stem_lower and last_name in stem_lower:
            return profile
    
    # Try exact full name slug match
    full_slug = slugify(clean_name)
    for profile in CRM_PROFILES_DIR.glob("*.yaml"):
        if full_slug == profile.stem.lower().replace('_', ''):
            return profile
    
    return None

def calculate_relationship_age(connected_at: Optional[int]) -> Optional[str]:
    """Calculate human-readable relationship age."""
    if not connected_at:
        return None
    
    connected_date = datetime.fromtimestamp(connected_at / 1000)
    now = datetime.now()
    delta = now - connected_date
    
    if delta.days < 30:
        return f"{delta.days} days"
    elif delta.days < 365:
        months = delta.days // 30
        return f"{months} month{'s' if months > 1 else ''}"
    else:
        years = delta.days // 365
        months = (delta.days % 365) // 30
        if months > 0:
            return f"{years} year{'s' if years > 1 else ''}, {months} month{'s' if months > 1 else ''}"
        return f"{years} year{'s' if years > 1 else ''}"

def enrich_profile(profile_path: Path, linkedin_data: dict, dry_run: bool = False) -> dict:
    """Enrich a CRM profile with LinkedIn data. Returns changes made."""
    changes = {}
    
    # Load existing profile
    content = profile_path.read_text()
    
    # Parse YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body = parts[2]
        else:
            frontmatter = {}
            body = content
    else:
        frontmatter = {}
        body = content
    
    # Prepare LinkedIn intelligence section
    linkedin_section = "\n\n## LinkedIn Intelligence (via Kondo)\n"
    linkedin_section += f"*Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
    
    if linkedin_data.get('linkedin_profile_url'):
        linkedin_section += f"- **LinkedIn:** [{linkedin_data['participant_name']}]({linkedin_data['linkedin_profile_url']})\n"
        changes['linkedin_url'] = linkedin_data['linkedin_profile_url']
    
    if linkedin_data.get('contact_headline'):
        linkedin_section += f"- **Headline:** {linkedin_data['contact_headline']}\n"
        changes['headline'] = linkedin_data['contact_headline']
    
    if linkedin_data.get('contact_location'):
        linkedin_section += f"- **Location:** {linkedin_data['contact_location']}\n"
        changes['location'] = linkedin_data['contact_location']
    
    if linkedin_data.get('connected_at'):
        connected_date = datetime.fromtimestamp(linkedin_data['connected_at'] / 1000)
        age = calculate_relationship_age(linkedin_data['connected_at'])
        linkedin_section += f"- **Connected:** {connected_date.strftime('%Y-%m-%d')} ({age})\n"
        changes['connected_at'] = connected_date.isoformat()
        changes['relationship_age'] = age
    
    if linkedin_data.get('kondo_note'):
        linkedin_section += f"\n### Kondo Note\n{linkedin_data['kondo_note']}\n"
        changes['kondo_note'] = linkedin_data['kondo_note']
    
    if linkedin_data.get('starred'):
        linkedin_section += f"- **⭐ Starred in Kondo**\n"
        changes['starred'] = True
    
    # Conversation stats
    linkedin_section += f"\n### Conversation Stats\n"
    linkedin_section += f"- **Total Messages:** {linkedin_data.get('message_count', 0)}\n"
    if linkedin_data.get('first_message_at'):
        first_msg = datetime.fromtimestamp(linkedin_data['first_message_at'] / 1000)
        linkedin_section += f"- **First Message:** {first_msg.strftime('%Y-%m-%d')}\n"
    if linkedin_data.get('last_message_at'):
        last_msg = datetime.fromtimestamp(linkedin_data['last_message_at'] / 1000)
        linkedin_section += f"- **Last Message:** {last_msg.strftime('%Y-%m-%d')}\n"
    linkedin_section += f"- **Status:** {linkedin_data.get('status', 'UNKNOWN')}\n"
    
    # Check if LinkedIn section already exists
    linkedin_marker = "## LinkedIn Intelligence (via Kondo)"
    if linkedin_marker in body:
        # Replace existing section
        pattern = r'## LinkedIn Intelligence \(via Kondo\).*?(?=\n## |\Z)'
        new_body = re.sub(pattern, linkedin_section.strip() + "\n", body, flags=re.DOTALL)
    else:
        # Add new section before Intelligence Log if exists, otherwise at end
        if "## Intelligence Log" in body:
            new_body = body.replace("## Intelligence Log", linkedin_section + "\n## Intelligence Log")
        else:
            new_body = body.rstrip() + linkedin_section
    
    # Update frontmatter
    frontmatter['last_edited'] = datetime.now().strftime('%Y-%m-%d')
    if 'version' in frontmatter:
        try:
            major, minor = str(frontmatter['version']).split('.')
            frontmatter['version'] = f"{major}.{int(minor) + 1}"
        except:
            frontmatter['version'] = '1.1'
    
    # Add LinkedIn metadata to frontmatter
    if linkedin_data.get('linkedin_profile_url'):
        frontmatter['linkedin_url'] = linkedin_data['linkedin_profile_url']
    if linkedin_data.get('connected_at'):
        frontmatter['linkedin_connected_at'] = datetime.fromtimestamp(
            linkedin_data['connected_at'] / 1000
        ).strftime('%Y-%m-%d')
    
    # Reconstruct file
    new_content = "---\n"
    new_content += yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    new_content += "---"
    new_content += new_body
    
    if not dry_run:
        profile_path.write_text(new_content)
    
    return changes

def main():
    parser = argparse.ArgumentParser(description="Sync LinkedIn data to CRM profiles")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--name", type=str, help="Filter by name")
    args = parser.parse_args()
    
    if not LINKEDIN_DB.exists():
        print(f"❌ LinkedIn database not found: {LINKEDIN_DB}")
        return 1
    
    if not CRM_PROFILES_DIR.exists():
        print(f"❌ CRM profiles directory not found: {CRM_PROFILES_DIR}")
        return 1
    
    conn = sqlite3.connect(LINKEDIN_DB)
    
    try:
        linkedin_records = get_linkedin_data(conn, args.name)
        print(f"📊 Found {len(linkedin_records)} LinkedIn conversations")
        
        synced = 0
        created = 0
        skipped = 0
        
        for record in linkedin_records:
            name = record['participant_name']
            profile_path = find_matching_profile(name)
            
            if profile_path:
                if args.dry_run:
                    print(f"  [DRY-RUN] Would enrich: {profile_path.name} ← {name}")
                else:
                    changes = enrich_profile(profile_path, record, dry_run=args.dry_run)
                    if changes:
                        print(f"  ✅ Enriched: {profile_path.name}")
                        if record.get('contact_headline'):
                            print(f"     └─ Headline: {record['contact_headline'][:50]}...")
                        if record.get('connected_at'):
                            age = calculate_relationship_age(record['connected_at'])
                            print(f"     └─ Connected: {age} ago")
                synced += 1
            else:
                # No matching profile - could create one
                skipped += 1
                if args.name or len(linkedin_records) < 20:  # Only show for filtered or small sets
                    print(f"  ⚠️  No profile match: {name}")
        
        print(f"\n📈 Summary:")
        print(f"   Synced: {synced}")
        print(f"   Skipped (no match): {skipped}")
        if args.dry_run:
            print(f"   (Dry run - no files modified)")
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    exit(main())


