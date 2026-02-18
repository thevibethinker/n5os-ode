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

# Import canonical paths
import sys
sys.path.insert(0, str(Path(__file__).parent))
from crm_paths import CRM_DB, CRM_INDIVIDUALS
from crm_identity_resolver import CRMIdentityResolver

DB_PATH = str(CRM_DB)
PROFILES_DIR = CRM_INDIVIDUALS  # Now uses canonical markdown profiles
_identity_resolver = CRMIdentityResolver(auto_link_threshold=0.99)


def find_profile_by_identifier(identifier: str) -> dict | None:
    """Find a profile by email, slug, or partial name match."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Precision-first shared resolver
    resolver_result = _identity_resolver.auto_link(
        email=identifier if '@' in identifier else None,
        name=identifier if '@' not in identifier else None,
    )
    if resolver_result.person_id:
        row = c.execute(
            "SELECT * FROM people WHERE id = ?",
            (resolver_result.person_id,),
        ).fetchone()
        conn.close()
        if row:
            return dict(row)

    c.execute("SELECT * FROM people WHERE lower(email)=lower(?)", (identifier,))
    row = c.fetchone()

    if not row:
        c.execute(
            """
            SELECT * FROM people
            WHERE LOWER(markdown_path) LIKE ? OR LOWER(full_name) LIKE ?
            LIMIT 1
            """,
            (f"%{identifier.lower()}%", f"%{identifier.lower()}%"),
        )
        row = c.fetchone()

    conn.close()

    if row:
        return dict(row)

    for md_file in PROFILES_DIR.glob("*.md"):
        if identifier.lower() in md_file.stem.lower():
            content = md_file.read_text()
            email = None
            email_match = re.search(r'\*\*Email:\*\*\s*(\S+@\S+)', content)
            if email_match:
                email = email_match.group(1)
            return {
                'person_id': md_file.stem,
                'email': email,
                'markdown_path': str(md_file)
            }

    return None

def get_email_from_profile(profile: dict) -> str | None:
    """Extract email from profile dict."""
    return profile.get('email') or profile.get('primary_email')


def update_profile_gmail_intel(profile_slug: str, gmail_intel: str) -> bool:
    """Update CRM profile with Gmail intelligence markdown block."""

    # Find the markdown profile (canonical location)
    md_files = list(PROFILES_DIR.glob(f"*{profile_slug}*.md"))
    if not md_files:
        # Try more aggressive matching
        md_files = list(PROFILES_DIR.glob("*.md"))
        md_files = [f for f in md_files if profile_slug.lower() in f.name.lower()]

    if not md_files:
        print(f"  ⚠ No profile found for {profile_slug}")
        return False

    profile_path = md_files[0]
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

    for md_file in PROFILES_DIR.glob("*.md"):
        if len(pending) >= limit:
            break

        if md_file.name.startswith('_'):
            continue

        content = md_file.read_text()

        # Check if has valid email - look in frontmatter or body
        has_email = False
        email = None

        # Check frontmatter (YAML between ---)
        if content.startswith('---'):
            end_idx = content.find('---', 3)
            if end_idx > 0:
                frontmatter = content[3:end_idx]
                for line in frontmatter.split('\n'):
                    if 'email' in line.lower() and ':' in line:
                        email_value = line.split(':', 1)[1].strip().strip("'\"")
                        if email_value and '@' in email_value and 'placeholder' not in email_value.lower() and 'not yet' not in email_value.lower():
                            has_email = True
                            email = email_value
                            break

        # Also check body for **Email:** pattern
        if not has_email:
            import re
            email_match = re.search(r'\*\*Email:\*\*\s*(\S+@\S+)', content)
            if email_match:
                email_value = email_match.group(1).strip()
                if 'placeholder' not in email_value.lower():
                    has_email = True
                    email = email_value

        if not has_email:
            continue

        # Check if already has Gmail intelligence
        if '### Gmail Intelligence' in content or '## Gmail Intelligence' in content:
            continue

        # Extract person_id from frontmatter or use filename
        person_id = md_file.stem

        pending.append({
            'person_id': person_id,
            'email': email,
            'file': md_file.name
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
        # Find the profile (try exact match first, then search)
        profile_path = PROFILES_DIR / f"{args.profile}.md"
        if not profile_path.exists():
            # Search for matching profile
            for md_file in PROFILES_DIR.glob("*.md"):
                if args.profile.lower() in md_file.stem.lower():
                    profile_path = md_file
                    break
            else:
                profile_path = None

        if not profile_path or not profile_path.exists():
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
        print(f"   Profile: {profile.get('markdown_path')}")
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

