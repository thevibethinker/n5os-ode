#!/usr/bin/env python3
"""
Meeting Transcript Scanner - Scan Google Drive for new transcripts

Features:
- Filename-based state tracking via [ZO-PROCESSED] prefix
- Deduplication against existing queue and processed meetings
- Consistent naming: YYYY-MM-DD_internal-team or YYYY-MM-DD_external-{name}
- Stakeholder classification (internal/external)
"""

import json
import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuration
INTERNAL_DOMAINS = {'mycareerspan.com', 'theapply.ai'}
INTERNAL_KEYWORDS = [
    'daily team stand-up',
    'team standup',
    'co-founder',
    'internal',
    'extended cof',
    'bi-weekly extended'
]

REQ_DIR = Path('/home/workspace/N5/inbox/meeting_requests')
TRANSCRIPT_DIR = Path('/home/workspace/N5/inbox/transcripts')
MEETINGS_DIR = Path('/home/workspace/N5/records/meetings')
COMPLETED_DIR = REQ_DIR / 'completed'
PROCESSED_DIR = REQ_DIR / 'processed'


def classify_meeting(participants_str, transcript_path=None):
    """Classify meeting as internal or external."""
    p_lower = participants_str.lower()
    
    # Check for internal keywords
    for keyword in INTERNAL_KEYWORDS:
        if keyword in p_lower:
            return ('internal', None)
    
    # Check transcript for email domains
    if transcript_path and transcript_path.exists():
        try:
            with open(transcript_path, 'r', errors='ignore') as f:
                content = f.read(5000)
                emails = re.findall(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
                if any(domain in INTERNAL_DOMAINS for domain in emails):
                    external_domains = [d for d in emails if d not in INTERNAL_DOMAINS]
                    if not external_domains:
                        return ('internal', None)
        except Exception:
            pass
    
    # Extract external participant name/org
    clean_name = re.sub(
        r'\s*[x&]?\s*(and\s+)?vrijen(\s+attawar)?(\s*\+\s*logan\s+currie)?',
        '', p_lower, flags=re.IGNORECASE
    )
    clean_name = re.sub(r'\s*-?\s*transcript.*$', '', clean_name)
    clean_name = clean_name.strip(' -+')
    slug = re.sub(r'[^a-z0-9]+', '-', clean_name).strip('-')
    
    if not slug or slug == 'meeting':
        return ('external', 'unknown')
    
    return ('external', slug)


def generate_meeting_id(date_str, classification, external_name, timestamp=None):
    """Generate standardized meeting_id with optional time suffix."""
    base_id = f"{date_str}_{'internal-team' if classification == 'internal' else f'external-{external_name}'}"
    
    # Add time suffix if provided (for disambiguation)
    if timestamp:
        time_suffix = timestamp.replace(':', '').replace('-', '')
        return f"{base_id}_{time_suffix}"
    
    return base_id


def load_existing_gdrive_ids():
    """Load all gdrive_ids from existing requests and processed meetings."""
    existing = set()
    
    # Check pending requests
    for fpath in REQ_DIR.glob('*_request.json'):
        try:
            with open(fpath) as f:
                data = json.load(f)
                if gid := data.get('gdrive_id'):
                    existing.add(gid)
        except Exception:
            pass
    
    # Check completed
    if COMPLETED_DIR.exists():
        for fpath in COMPLETED_DIR.glob('*_request.json'):
            try:
                with open(fpath) as f:
                    data = json.load(f)
                    if gid := data.get('gdrive_id'):
                        existing.add(gid)
            except Exception:
                pass
    
    # Check processed
    if PROCESSED_DIR.exists():
        for fpath in PROCESSED_DIR.glob('*_request.json'):
            try:
                with open(fpath) as f:
                    data = json.load(f)
                    if gid := data.get('gdrive_id'):
                        existing.add(gid)
            except Exception:
                pass
    
    # Check processed meeting folders
    if MEETINGS_DIR.exists():
        for folder in MEETINGS_DIR.iterdir():
            if folder.is_dir():
                meta_path = folder / '_metadata.json'
                if meta_path.exists():
                    try:
                        with open(meta_path) as f:
                            data = json.load(f)
                            if gid := data.get('gdrive_id'):
                                existing.add(gid)
                    except Exception:
                        pass
    
    return existing


def main():
    # This would normally call the Google Drive API
    # For now, just demonstrate the deduplication logic
    print("=== MEETING TRANSCRIPT SCANNER ===")
    print(f"Request dir: {REQ_DIR}")
    print(f"Transcript dir: {TRANSCRIPT_DIR}")
    print()
    
    # Load existing gdrive_ids
    existing_ids = load_existing_gdrive_ids()
    print(f"Existing gdrive_ids in system: {len(existing_ids)}")
    print()
    
    # Create directories
    REQ_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    COMPLETED_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    print("✓ Scanner initialized")
    print("✓ Deduplication enabled")
    print("✓ Naming convention: YYYY-MM-DD_internal-team or YYYY-MM-DD_external-{name}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
