#!/usr/bin/env python3
"""
CRM Gmail Enrichment Script

Enriches CRM V3 profiles with Gmail thread intelligence.
Called manually or as part of enrichment pipeline.

Usage:
    python3 N5/scripts/crm_gmail_enrichment.py --profile <profile_slug_or_email>
    python3 N5/scripts/crm_gmail_enrichment.py --batch  # Process all profiles needing Gmail enrichment
"""

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = '/home/workspace/N5/data/crm_v3.db'
PROFILES_DIR = Path('/home/workspace/N5/crm_v3/profiles')


def find_profile_by_identifier(identifier: str) -> dict | None:
    """Find a profile by email, slug, or partial name match."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Try exact email match first
    c.execute("SELECT * FROM profiles WHERE email = ? OR primary_email = ?", 
              (identifier, identifier))
    row = c.fetchone()
    
    if not row:
        # Try slug/name match
        c.execute("""
            SELECT * FROM profiles 
            WHERE LOWER(yaml_path) LIKE ? 
            LIMIT 1
        """, (f"%{identifier.lower()}%",))
        row = c.fetchone()
    
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_email_from_profile(profile: dict) -> str | None:
    """Extract email from profile dict."""
    return profile.get('primary_email') or profile.get('email')


def update_profile_gmail_intel(profile_slug: str, gmail_intel: str) -> bool:
    """Update CRM profile with Gmail intelligence markdown block."""
    
    # Find the YAML profile
    yaml_files = list(PROFILES_DIR.glob(f"*{profile_slug}*.yaml"))
    if not yaml_files:
        # Try more aggressive matching
        yaml_files = list(PROFILES_DIR.glob("*.yaml"))
        yaml_files = [f for f in yaml_files if profile_slug.lower() in f.name.lower()]
    
    if not yaml_files:
        print(f"  ⚠ No YAML profile found for {profile_slug}")
        return False
    
    profile_path = yaml_files[0]
    content = profile_path.read_text()
    
    # Find the Gmail Intelligence section and update it
    gmail_marker = "### Gmail Intelligence"
    new_gmail_section = f"### Gmail Intelligence\n{gmail_intel}\n"
    
    if gmail_marker in content:
        # Replace existing section (up to next ### or ## or ---)
        pattern = r'### Gmail Intelligence\n.*?(?=\n###|\n##|\n---|\Z)'
        content = re.sub(pattern, new_gmail_section.rstrip(), content, flags=re.DOTALL)
    else:
        # Find Enrichment Data section and add Gmail intel
        enrichment_marker = "## Enrichment Data"
        if enrichment_marker in content:
            # Insert after Aviato section or at end of Enrichment Data
            aviato_marker = "### Aviato Intelligence"
            if aviato_marker in content:
                # Find end of Aviato section
                aviato_idx = content.find(aviato_marker)
                # Find next section header after Aviato
                rest = content[aviato_idx + len(aviato_marker):]
                next_section = re.search(r'\n(###|##|---)', rest)
                if next_section:
                    insert_pos = aviato_idx + len(aviato_marker) + next_section.start()
                    content = content[:insert_pos] + "\n\n" + new_gmail_section + content[insert_pos:]
                else:
                    # Append at end
                    content = content.rstrip() + "\n\n" + new_gmail_section
            else:
                # Insert after Enrichment Data header
                idx = content.find(enrichment_marker) + len(enrichment_marker)
                content = content[:idx] + "\n\n" + new_gmail_section + content[idx:]
        else:
            # No Enrichment Data section - add at end
            content = content.rstrip() + "\n\n## Enrichment Data\n\n" + new_gmail_section
    
    profile_path.write_text(content)
    return True


def generate_gmail_enrichment_prompt(email: str) -> str:
    """Generate the prompt for Gmail thread analysis."""
    return f"""Analyze Gmail threads with {email} to extract relationship intelligence.

Search Gmail for threads with this contact:
- Query: from:{email} OR to:{email}
- Max results: 20

For each thread, extract:
- Thread subject
- Date
- Key topics discussed

Then synthesize into this exact format:

**Gmail Thread Intelligence:**

**Communication Pattern:**
- Total threads: [count]
- Date range: [first] to [last]  
- Last exchange: [date]
- Frequency: [weekly/monthly/occasional/single]

**Relationship Context:**
[2-3 sentence summary]

**Recent Topics:**
- [topic 1]
- [topic 2]

**Notable Mentions:**
- [significant items: intros, projects, shared connections]

**Follow-up Items:**
- [open loops or action items if any]

Return ONLY the markdown block, nothing else."""


def get_pending_gmail_enrichment(limit=20):
    """Find profiles with email but no Gmail intelligence."""
    pending = []
    
    for yaml_file in PROFILES_DIR.glob("*.yaml"):
        if len(pending) >= limit:
            break
            
        content = yaml_file.read_text()
        
        # Check if has valid email
        has_email = False
        email = None
        for line in content.split('\n'):
            if line.startswith('email:'):
                email_value = line.replace('email:', '').strip().strip("'\"")
                if email_value and '@' in email_value and 'placeholder' not in email_value.lower() and 'not yet' not in email_value.lower():
                    has_email = True
                    email = email_value
                    break
        
        if not has_email:
            continue
            
        # Check if already has Gmail intelligence
        if '### Gmail Intelligence' in content or '## Gmail Intelligence' in content:
            continue
            
        # Extract person_id
        person_id = None
        for line in content.split('\n'):
            if line.startswith('person_id:'):
                person_id = line.replace('person_id:', '').strip().strip("'\"")
                break
        
        if not person_id:
            person_id = yaml_file.stem
            
        pending.append({
            'person_id': person_id,
            'email': email,
            'file': yaml_file.name
        })
    
    return pending

def update_gmail_intelligence(profile_path, summary):
    """Update a profile with Gmail intelligence summary."""
    content = profile_path.read_text()
    
    # Build the intelligence block
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    intel_block = f"""

### Gmail Intelligence
**Last Sync:** {timestamp}

{summary}
"""
    
    # Find insertion point - before "## Action Items" or at end before last "---"
    if '## Action Items' in content:
        content = content.replace('## Action Items', intel_block + '\n## Action Items')
    elif '## Enrichment Data' in content:
        content = content.replace('## Enrichment Data', intel_block + '\n## Enrichment Data')
    else:
        # Append before final section
        content = content.rstrip() + intel_block
    
    profile_path.write_text(content)
    return True


def main():
    parser = argparse.ArgumentParser(description='CRM Gmail Enrichment')
    parser.add_argument('--profile', help='Profile person_id to enrich')
    parser.add_argument('--list-pending', action='store_true', help='List profiles needing Gmail enrichment')
    parser.add_argument('--limit', type=int, default=20, help='Max profiles to list (default 20)')
    parser.add_argument('--summary', help='Gmail intelligence summary to write to profile')
    args = parser.parse_args()
    
    if args.list_pending:
        pending = get_pending_gmail_enrichment(args.limit)
        print(json.dumps(pending, indent=2))
    elif args.profile and args.summary:
        # Find the profile
        profile_path = None
        for yaml_file in PROFILES_DIR.glob("*.yaml"):
            content = yaml_file.read_text()
            if f"person_id: {args.profile}" in content or f"person_id: '{args.profile}'" in content:
                profile_path = yaml_file
                break
        
        if not profile_path:
            print(f"✗ Profile not found: {args.profile}")
            return
            
        if update_gmail_intelligence(profile_path, args.summary):
            print(f"✓ Updated Gmail intelligence for {args.profile}")
        else:
            print(f"✗ Failed to update {args.profile}")
    elif args.profile:
        profile = find_profile_by_identifier(args.profile)
        if not profile:
            print(f"✗ Profile not found: {args.profile}")
            return
        
        email = get_email_from_profile(profile)
        if not email:
            print(f"✗ No email found for profile: {args.profile}")
            return
        
        print(f"📧 Gmail Enrichment for: {email}")
        print(f"   Profile: {profile.get('yaml_path')}")
        print()
        print("To enrich this profile, run the Gmail enrichment workflow:")
        print(f"   @crm-gmail-enrichment {email}")
        print()
        print("Or use the prompt directly:")
        print("-" * 50)
        print(generate_gmail_enrichment_prompt(email))
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()


