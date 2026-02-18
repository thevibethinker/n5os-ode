#!/usr/bin/env python3
"""
CRM Review Flagging Script

Identifies profiles needing manual review and generates digest sections.
Called by morning_digest.py to include CRM review items in the daily briefing.

Flags:
- Profiles missing email addresses (can't be enriched via Aviato/Gmail)
- Profiles with stale data (no interaction in 90+ days)
- Profiles queued for enrichment but failing
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

CRM_DB = Path("/home/workspace/N5/data/n5_core.db")
CRM_PROFILES = Path("/home/workspace/N5/crm_v3/profiles")

def get_profiles_missing_email():
    """Find profiles that need email addresses for enrichment."""
    missing = []
    
    for yaml_file in CRM_PROFILES.glob("*.yaml"):
        content = yaml_file.read_text()
        
        # Check if email is missing or placeholder
        has_valid_email = False
        for line in content.split('\n'):
            if line.startswith('email:'):
                email_value = line.replace('email:', '').strip().strip("'\"")
                if email_value and '@' in email_value and 'placeholder' not in email_value.lower() and 'not yet' not in email_value.lower():
                    has_valid_email = True
                    break
        
        if not has_valid_email:
            # Extract name from file
            name = yaml_file.stem.replace('_', ' ').rsplit(' ', 1)[0]
            missing.append({
                'name': name,
                'file': yaml_file.name,
                'reason': 'missing_email'
            })
    
    return missing

def get_enrichment_failures():
    """Find profiles that failed enrichment."""
    if not CRM_DB.exists():
        return []
    
    conn = sqlite3.connect(CRM_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("""
            SELECT profile_id, priority, status, error_message, context
            FROM enrichment_queue
            WHERE status = 'failed'
            ORDER BY priority DESC
            LIMIT 10
        """)
        
        failures = []
        for row in c.fetchall():
            failures.append({
                'profile_id': row['profile_id'],
                'error': row['error_message'] or 'Unknown error',
                'reason': 'enrichment_failed'
            })
        
        return failures
    except Exception as e:
        logger.warning(f"Could not query enrichment queue: {e}")
        return []
    finally:
        conn.close()

def get_stale_profiles(days=90):
    """Find profiles with no recent interactions."""
    cutoff = datetime.now() - timedelta(days=days)
    stale = []
    
    for yaml_file in CRM_PROFILES.glob("*.yaml"):
        content = yaml_file.read_text()
        
        # Look for last_edited or last interaction date
        last_date = None
        for line in content.split('\n'):
            if 'last_edited:' in line:
                try:
                    date_str = line.split(':', 1)[1].strip().strip("'\"")
                    last_date = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    pass
                break
        
        if last_date and last_date < cutoff:
            name = yaml_file.stem.replace('_', ' ').rsplit(' ', 1)[0]
            stale.append({
                'name': name,
                'file': yaml_file.name,
                'last_updated': last_date.strftime('%Y-%m-%d'),
                'reason': 'stale_profile'
            })
    
    # Only return top 5 stalest
    stale.sort(key=lambda x: x['last_updated'])
    return stale[:5]

def generate_digest_section():
    """Generate the CRM Review section for morning digest."""
    missing_email = get_profiles_missing_email()
    failures = get_enrichment_failures()
    stale = get_stale_profiles()
    
    lines = []
    
    # Only include section if there are items to review
    total_items = len(missing_email) + len(failures) + len(stale)
    if total_items == 0:
        return ""
    
    lines.append("## 📇 CRM Review")
    lines.append("")
    
    if missing_email:
        # Only show top 5
        lines.append(f"**Missing Email ({len(missing_email)} profiles):**")
        for item in missing_email[:5]:
            lines.append(f"- {item['name']}")
        if len(missing_email) > 5:
            lines.append(f"- ...and {len(missing_email) - 5} more")
        lines.append("")
    
    if failures:
        lines.append(f"**Enrichment Failures ({len(failures)}):**")
        for item in failures[:3]:
            lines.append(f"- Profile #{item['profile_id']}: {item['error'][:50]}...")
        lines.append("")
    
    if stale:
        lines.append(f"**Stale Profiles (90+ days):**")
        for item in stale:
            lines.append(f"- {item['name']} (last: {item['last_updated']})")
        lines.append("")
    
    lines.append(f"*Run `@CRM Profile Enrichment` to address these items.*")
    lines.append("")
    
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='CRM Review Flagging')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--digest', action='store_true', help='Output digest section markdown')
    parser.add_argument('--stats', action='store_true', help='Output summary stats only')
    args = parser.parse_args()
    
    if args.digest:
        print(generate_digest_section())
    elif args.json:
        data = {
            'missing_email': get_profiles_missing_email(),
            'enrichment_failures': get_enrichment_failures(),
            'stale_profiles': get_stale_profiles()
        }
        print(json.dumps(data, indent=2))
    elif args.stats:
        missing = len(get_profiles_missing_email())
        failures = len(get_enrichment_failures())
        stale = len(get_stale_profiles())
        print(f"Missing email: {missing}")
        print(f"Enrichment failures: {failures}")
        print(f"Stale profiles: {stale}")
        print(f"Total items needing review: {missing + failures + stale}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

