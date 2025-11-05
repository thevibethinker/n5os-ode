#!/usr/bin/env python3
"""
Standardize a single meeting folder:
1. Infer taxonomy (type + subtype)
2. Add frontmatter to all B*.md files
3. Rename folder to standard format

Format: YYYY-MM-DD_lead-participant_subtype
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from infer_meeting_taxonomy import infer_from_folder


def extract_meeting_date(folder_path: Path) -> Optional[str]:
    """Extract meeting date from B26 metadata (YYYY-MM-DD)."""
    b26 = folder_path / "B26_metadata.md"
    
    if not b26.exists():
        return None
    
    content = b26.read_text()
    
    # Look for date field
    date_patterns = [
        r'\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})',
        r'\*\*Meeting Date:\*\*\s*(\d{4}-\d{2}-\d{2})',
        r'meeting_date:\s*(\d{4}-\d{2}-\d{2})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1)
    
    # Fallback: try to parse from folder name
    folder_name = folder_path.name
    date_match = re.search(r'202[45]-\d{2}-\d{2}', folder_name)
    if date_match:
        return date_match.group(0)
    
    # Last resort: try transcript timestamp
    timestamp_match = re.search(r'transcript-(\d{4}-\d{2}-\d{2})', folder_name)
    if timestamp_match:
        return timestamp_match.group(1)
    
    return None


def extract_lead_participant(folder_path: Path, meeting_type: str) -> str:
    """Extract lead participant/org name."""
    b26 = folder_path / "B26_metadata.md"
    
    if not b26.exists():
        return "unknown"
    
    content = b26.read_text()
    
    # For external meetings, look for org/company name
    if meeting_type == "external":
        # Check Stakeholder Classification
        stakeholder_match = re.search(r'\*\*Primary:\*\*\s*([^(\n]+)', content)
        if stakeholder_match:
            primary = stakeholder_match.group(1).strip()
            # Extract company/org name
            org_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', primary)
            if org_match:
                org = org_match.group(1).lower().replace(' ', '-')
                return org
        
        # Check attendees for external org
        attendees_section = re.search(r'\*\*Attendees:\*\*\s*([^\n]+)', content)
        if attendees_section:
            attendees = attendees_section.group(1)
            # Look for company in parentheses
            companies = re.findall(r'\(([^)]+)\)', attendees)
            if companies:
                # Get first non-Careerspan company
                for company in companies:
                    if 'careerspan' not in company.lower():
                        return company.lower().replace(' ', '-')
    
    # For internal meetings, use descriptor from folder name or default
    if meeting_type == "internal":
        folder_name = folder_path.name.lower()
        if 'standup' in folder_name or 'stand-up' in folder_name or 'daily' in folder_name:
            return "team-standup"
        if 'war-room' in folder_name or 'acquisition' in folder_name:
            return "war-room"
        if 'planning' in folder_name:
            return "planning"
        return "team"
    
    return "unknown"


def generate_folder_name(meeting_date: str, lead_participant: str, subtype: str) -> str:
    """Generate standardized folder name."""
    # Clean participant name
    participant = lead_participant.lower().replace('_', '-').replace(' ', '-')
    participant = re.sub(r'[^a-z0-9-]', '', participant)
    
    # Clean subtype
    subtype = subtype.lower().replace('_', '-')
    
    return f"{meeting_date}_{participant}_{subtype}"


def add_frontmatter(file_path: Path, metadata: Dict):
    """Add or update YAML frontmatter in a B*.md file."""
    content = file_path.read_text()
    
    # Check if frontmatter already exists
    if content.startswith('---\n'):
        # Update existing frontmatter
        end_idx = content.find('\n---\n', 4)
        if end_idx > 0:
            existing_fm = content[4:end_idx]
            body = content[end_idx + 5:]
            
            # Parse existing frontmatter
            fm_dict = {}
            for line in existing_fm.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    fm_dict[key.strip()] = val.strip()
            
            # Update with new metadata
            fm_dict.update(metadata)
            
            # Regenerate
            new_fm = '\n'.join([f"{k}: {v}" for k, v in fm_dict.items()])
            new_content = f"---\n{new_fm}\n---\n{body}"
            file_path.write_text(new_content)
            return
    
    # No frontmatter exists, add it
    fm_lines = [f"{k}: {v}" for k, v in metadata.items()]
    frontmatter = "---\n" + "\n".join(fm_lines) + "\n---\n\n"
    new_content = frontmatter + content
    file_path.write_text(new_content)


def standardize_meeting_folder(folder_path: Path, dry_run: bool = False) -> Dict:
    """
    Standardize a meeting folder.
    
    Returns dict with: {
        'success': bool,
        'old_name': str,
        'new_name': str,
        'meeting_type': str,
        'meeting_subtype': str,
        'error': str (if failed)
    }
    """
    result = {
        'success': False,
        'old_name': folder_path.name,
        'new_name': None,
        'meeting_type': None,
        'meeting_subtype': None,
        'error': None
    }
    
    try:
        # Step 1: Infer taxonomy
        taxonomy = infer_from_folder(folder_path)
        if not taxonomy:
            result['error'] = "Could not infer taxonomy (missing or invalid B26)"
            return result
        
        meeting_type, meeting_subtype = taxonomy
        result['meeting_type'] = meeting_type
        result['meeting_subtype'] = meeting_subtype
        
        # Step 2: Extract meeting date
        meeting_date = extract_meeting_date(folder_path)
        if not meeting_date:
            result['error'] = "Could not extract meeting date"
            return result
        
        # Step 3: Extract lead participant
        lead_participant = extract_lead_participant(folder_path, meeting_type)
        
        # Step 4: Generate new folder name
        new_folder_name = generate_folder_name(meeting_date, lead_participant, meeting_subtype)
        result['new_name'] = new_folder_name
        
        # Check if name already matches
        if folder_path.name == new_folder_name:
            result['success'] = True
            result['error'] = "Already standardized"
            return result
        
        # Step 5: Add frontmatter to all B*.md files
        b_files = list(folder_path.glob("B*.md"))
        
        frontmatter_metadata = {
            'processing_version': '1.0',
            'meeting_date': meeting_date,
            'meeting_type': meeting_type,
            'meeting_subtype': meeting_subtype,
            'lead_participant': lead_participant,
            'created': datetime.now().strftime('%Y-%m-%d'),
            'last_edited': datetime.now().strftime('%Y-%m-%d'),
        }
        
        if not dry_run:
            for b_file in b_files:
                add_frontmatter(b_file, frontmatter_metadata)
        
        # Step 6: Rename folder (check for collisions)
        new_path = folder_path.parent / new_folder_name
        
        if new_path.exists() and new_path != folder_path:
            # Collision - append numeric suffix
            counter = 2
            while True:
                collision_name = f"{new_folder_name}-{counter}"
                new_path = folder_path.parent / collision_name
                if not new_path.exists():
                    new_folder_name = collision_name
                    result['new_name'] = new_folder_name
                    break
                counter += 1
        
        if not dry_run:
            folder_path.rename(new_path)
        
        result['success'] = True
        return result
        
    except Exception as e:
        result['error'] = str(e)
        return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 standardize_meeting_folder.py <folder-path> [--dry-run]")
        sys.exit(1)
    
    folder_path = Path(sys.argv[1])
    dry_run = '--dry-run' in sys.argv
    
    if not folder_path.is_dir():
        print(f"ERROR: Not a directory: {folder_path}")
        sys.exit(1)
    
    result = standardize_meeting_folder(folder_path, dry_run=dry_run)
    
    if result['success']:
        print(f"✅ SUCCESS")
        print(f"   Old: {result['old_name']}")
        print(f"   New: {result['new_name']}")
        print(f"   Type: {result['meeting_type']}")
        print(f"   Subtype: {result['meeting_subtype']}")
        if dry_run:
            print("   (DRY RUN - no changes made)")
    else:
        print(f"❌ FAILED: {result['error']}")
        sys.exit(1)
