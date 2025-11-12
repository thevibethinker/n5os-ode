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

# Marker prefix for processed transcripts in Google Drive
PROCESSED_MARKER = '[ZO-V2]'

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
MEETINGS_DIR = Path('/home/workspace/Personal/Meetings')
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


def parse_transcript_filename(filename: str) -> dict:
    """Extract meeting info from Fireflies transcript filename."""
    # Remove processed marker prefix if present
    clean_name = filename.replace(f'{PROCESSED_MARKER} ', '')
    
    # Pattern: "Name x Name-transcript-2025-09-23T21-04-28.138Z.docx"
    match = re.search(r'(.+?)-transcript-(\d{4}-\d{2}-\d{2})', clean_name)
    
    if match:
        participants = match.group(1).strip()
        date_str = match.group(2)
        
        # Create clean ID
        participants_clean = participants.replace(' x ', '-').replace(' ', '-').lower()
        participants_clean = re.sub(r'[^a-z0-9-]', '', participants_clean)[:50]
        
        meeting_id = f"{date_str}_{participants_clean}"
        
        return {
            "meeting_id": meeting_id,
            "participants": participants,
            "date": date_str,
            "original_filename": filename,
            "is_processed": filename.startswith(PROCESSED_MARKER)
        }
    
    # Fallback for non-standard names (e.g., GRANOLA VERSION files)
    return {
        "meeting_id": f"meeting-{clean_name[:40]}",
        "participants": "unknown",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "original_filename": filename,
        "is_processed": filename.startswith(PROCESSED_MARKER)
    }


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


def filter_unprocessed(files_list: list) -> list:
    """
    Filter out processed transcripts.
    
    Args:
        files_list: List of dicts with 'name' and 'id' keys from Google Drive
    
    Returns:
        List of unprocessed file dicts with parsed metadata
    """
    unprocessed = []
    
    for file_info in files_list:
        filename = file_info.get('name', '')
        
        # Skip if already processed
        # ALL files in Fireflies/Transcripts folder are transcripts—no additional filtering needed
        if filename.startswith(PROCESSED_MARKER):
            continue
        
        # Parse and add metadata
        parsed = parse_transcript_filename(filename)
        parsed['gdrive_id'] = file_info.get('id')
        parsed['gdrive_link'] = file_info.get('webViewLink')
        parsed['modified_time'] = file_info.get('modifiedTime')
        
        unprocessed.append(parsed)
    
    return unprocessed


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
