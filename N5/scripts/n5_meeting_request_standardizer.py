#!/usr/bin/env python3
"""
Meeting Request Standardizer - Apply consistent naming convention

Naming Convention:
- Internal: YYYY-MM-DD_internal-team
- External: YYYY-MM-DD_external-{name/org}

Examples:
- 2025-10-10_internal-team
- 2025-10-09_external-alex-wisdom-partners
- 2025-09-23_external-stephanie
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Internal email domains (Careerspan)
INTERNAL_DOMAINS = {'mycareerspan.com', 'theapply.ai'}

# Internal meeting keywords
INTERNAL_KEYWORDS = [
    'daily team stand-up',
    'team standup',
    'co-founder',
    'internal',
    'extended cof',
    'bi-weekly extended'
]


def classify_meeting(participants_str, transcript_path=None):
    """
    Classify meeting as internal or external.
    Returns: ('internal', None) or ('external', 'name/org')
    """
    p_lower = participants_str.lower()
    
    # Check for internal keywords
    for keyword in INTERNAL_KEYWORDS:
        if keyword in p_lower:
            return ('internal', None)
    
    # Check transcript for email domains if available
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, 'r', errors='ignore') as f:
                content = f.read(5000)  # First 5k chars
                emails = re.findall(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
                # If we find internal domain, it's internal
                if any(domain in INTERNAL_DOMAINS for domain in emails):
                    # But only if no external domains
                    external_domains = [d for d in emails if d not in INTERNAL_DOMAINS]
                    if not external_domains:
                        return ('internal', None)
        except Exception:
            pass
    
    # Extract external participant name/org
    # Remove "x Vrijen", "and Vrijen Attawar", etc.
    clean_name = re.sub(r'\s*[x&]?\s*(and\s+)?vrijen(\s+attawar)?(\s*\+\s*logan\s+currie)?', '', p_lower, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s*-?\s*transcript.*$', '', clean_name)
    clean_name = clean_name.strip(' -+')
    
    # Make slug
    slug = re.sub(r'[^a-z0-9]+', '-', clean_name).strip('-')
    
    if not slug or slug == 'meeting':
        return ('external', 'unknown')
    
    return ('external', slug)


def standardize_meeting_id(date_str, classification, external_name):
    """
    Generate standardized meeting_id.
    
    Args:
        date_str: YYYY-MM-DD format
        classification: 'internal' or 'external'
        external_name: name/org slug (only if external)
    
    Returns:
        meeting_id: YYYY-MM-DD_internal-team or YYYY-MM-DD_external-{name}
    """
    if classification == 'internal':
        return f"{date_str}_internal-team"
    else:
        return f"{date_str}_external-{external_name}"


def main():
    req_dir = Path('/home/workspace/N5/inbox/meeting_requests')
    transcript_dir = Path('/home/workspace/N5/inbox/transcripts')
    
    # Load all pending requests
    requests = []
    for fpath in req_dir.glob('*_request.json'):
        with open(fpath) as f:
            data = json.load(f)
            data['_filepath'] = fpath
            data['_filename'] = fpath.name
            requests.append(data)
    
    print(f"Found {len(requests)} pending requests")
    print()
    
    # Standardize each request
    changes = []
    
    for req in requests:
        old_id = req.get('meeting_id')
        date = req.get('date')
        participants = req.get('participants', '')
        gdrive_id = req.get('gdrive_id')
        
        # Find transcript
        transcript_files = list(transcript_dir.glob('*.txt'))
        transcript_path = None
        for tf in transcript_files:
            if gdrive_id and gdrive_id in tf.name:
                transcript_path = tf
                break
        
        # Classify
        classification, external_name = classify_meeting(participants, transcript_path)
        
        # Generate new ID
        new_id = standardize_meeting_id(date, classification, external_name)
        
        # Check if needs update
        if old_id != new_id:
            changes.append({
                'old_id': old_id,
                'new_id': new_id,
                'classification': classification,
                'external_name': external_name,
                'filepath': req['_filepath'],
                'request': req
            })
    
    print(f"=== STANDARDIZATION PLAN ===")
    print(f"Changes needed: {len(changes)}")
    print()
    
    if not changes:
        print("✓ All requests already standardized!")
        return 0
    
    # Show changes
    for change in changes:
        print(f"{change['old_id']}")
        print(f"  → {change['new_id']} ({change['classification']})")
        print()
    
    # Apply changes
    print(f"=== APPLYING CHANGES ===")
    for change in changes:
        req = change['request']
        old_path = change['filepath']
        new_filename = f"{change['new_id']}_request.json"
        new_path = req_dir / new_filename
        
        # Update request data
        req['meeting_id'] = change['new_id']
        req['classification'] = change['classification']
        if change['external_name']:
            req['external_participant'] = change['external_name']
        
        # Remove internal fields
        req.pop('_filepath', None)
        req.pop('_filename', None)
        
        # Write to new file
        with open(new_path, 'w') as f:
            json.dump(req, f, indent=2)
        
        # Delete old file if different
        if old_path != new_path:
            old_path.unlink()
            print(f"✓ {change['old_id']} → {change['new_id']}")
        else:
            print(f"✓ Updated: {change['new_id']}")
    
    print()
    print(f"✓ Standardized {len(changes)} requests")
    return 0


if __name__ == '__main__':
    sys.exit(main())
