#!/usr/bin/env python3
"""
Meeting Folder Name Normalizer
Converts cryptic Fireflies codes to readable meeting folder names
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import unicodedata
import logging

def slugify(text: str) -> str:
    """Convert text to URL-safe slug"""
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Convert to lowercase and replace spaces with hyphens
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def extract_participants_from_transcript(transcript_path: Path) -> Optional[List[str]]:
    """Extract participant names from transcript metadata"""
    try:
        with open(transcript_path, 'r') as f:
            content = f.read()
            
        # Try to find participants in metadata
        # Pattern 1: Look for "Participants:" section
        if 'Participants:' in content or 'participants:' in content:
            match = re.search(r'[Pp]articipants?:\s*([^\n]+)', content)
            if match:
                participants_line = match.group(1)
                # Split by common separators
                participants = re.split(r'[,;]|\sand\s', participants_line)
                return [p.strip() for p in participants if p.strip()]
        
        # Pattern 2: Look for speaker labels in utterances
        speakers = set()
        speaker_pattern = r'"speaker":\s*"([^"]+)"'
        for match in re.finditer(speaker_pattern, content):
            speaker = match.group(1)
            if speaker and speaker != "Unknown":
                speakers.add(speaker)
        
        if speakers:
            return list(speakers)
            
    except Exception as e:
        print(f"Error extracting participants: {e}")
    
    return None

def extract_meeting_title_from_transcript(transcript_path: Path) -> Optional[str]:
    """Extract meeting title from transcript"""
    try:
        with open(transcript_path, 'r') as f:
            content = f.read()
        
        # Look for title in metadata
        patterns = [
            r'"title":\s*"([^"]+)"',
            r'Title:\s*([^\n]+)',
            r'Meeting:\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(1).strip()
                if title and title != "Untitled":
                    return title
                    
    except Exception as e:
        print(f"Error extracting title: {e}")
    
    return None

def extract_date_from_folder_name(folder_name: str) -> Optional[str]:
    """Extract date from existing folder name"""
    # Pattern: YYYY-MM-DDTHH-MM-SS or YYYY-MM-DD
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    match = re.search(date_pattern, folder_name)
    if match:
        return match.group(1)
    return None

def determine_meeting_type(transcript_path: Path, participants: List[str]) -> str:
    """Determine meeting type from context"""
    try:
        with open(transcript_path, 'r') as f:
            content = f.read().lower()
        
        # Check for internal meeting indicators
        internal_indicators = [
            'stand-up', 'standup', 'daily team', 'weekly team',
            'sprint', 'retrospective', 'planning', 'all-hands'
        ]
        
        for indicator in internal_indicators:
            if indicator in content:
                return 'internal'
        
        # Check participant names for internal team members
        internal_names = ['rochel', 'alexis', 'mishu', 'team']
        if participants:
            for participant in participants:
                for internal_name in internal_names:
                    if internal_name.lower() in participant.lower():
                        return 'internal'
        
        # Default to external
        return 'external'
        
    except Exception:
        return 'external'

def normalize_meeting_name(
    folder_path: Path,
    transcript_path: Path,
    meeting_type: Optional[str] = None
) -> str:
    """
    Generate normalized meeting folder name
    
    Format: YYYY-MM-DD_FirstLast_meeting-type
    Example: 2025-11-03_MihirMakwana_external
    """
    folder_name = folder_path.name
    
    # Extract date
    date_str = extract_date_from_folder_name(folder_name)
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Extract participants
    participants = extract_participants_from_transcript(transcript_path)
    
    # Try to get meeting title if no participants
    if not participants:
        title = extract_meeting_title_from_transcript(transcript_path)
        if title:
            slug = slugify(title)
            if meeting_type is None:
                meeting_type = 'external'
            return f"{date_str}_{slug}_{meeting_type}"
    
    # Generate participant slug
    if participants:
        # Filter out "Vrijen" or common self-references
        external_participants = [
            p for p in participants 
            if 'vrijen' not in p.lower() and 'attawar' not in p.lower()
        ]
        
        if external_participants:
            # Use first external participant
            primary = external_participants[0]
            # Remove titles, get first and last name
            name_parts = re.findall(r'[A-Z][a-z]+', primary)
            if name_parts:
                participant_slug = ''.join(name_parts)
            else:
                participant_slug = slugify(primary).replace('-', '')
        else:
            participant_slug = 'meeting'
    else:
        participant_slug = 'meeting'
    
    # Determine meeting type if not provided
    if meeting_type is None:
        meeting_type = determine_meeting_type(transcript_path, participants or [])
    
    # Construct normalized name
    normalized = f"{date_str}_{participant_slug}_{meeting_type}"
    
    return normalized

def rename_meeting_folder(old_path: Path, dry_run: bool = True) -> Optional[Path]:
    """
    Rename meeting folder to normalized format
    
    Returns:
        New path if renamed, None if no change needed
    """
    # Try to extract metadata from B26 first
    b26_metadata = extract_metadata_from_b26(old_path)
    
    if b26_metadata:
        # Use new priority-based naming function
        new_name = generate_folder_name_from_b26(old_path, b26_metadata)
    else:
        # Fall back to transcript-based naming
        transcript_files = list(old_path.glob('*.transcript.md')) + list(old_path.glob('*.transcript.jsonl'))
        
        if not transcript_files:
            print(f"⚠️  No B26 or transcript found in {old_path.name}")
            return None
        
        transcript_path = transcript_files[0]
        new_name = normalize_meeting_name(old_path, transcript_path)
    
    # Check if already normalized
    if old_path.name == new_name:
        print(f"✓ Already normalized: {old_path.name}")
        return None
    
    new_path = old_path.parent / new_name
    
    # Check for conflicts
    if new_path.exists():
        print(f"⚠️  Conflict: {new_name} already exists")
        return None
    
    if dry_run:
        print(f"Would rename: {old_path.name} → {new_name}")
        return new_path
    else:
        old_path.rename(new_path)
        print(f"✓ Renamed: {old_path.name} → {new_name}")
        return new_path

def scan_and_normalize_meetings(
    meetings_dir: Path,
    dry_run: bool = True,
    filter_pattern: Optional[str] = None
) -> Dict[str, int]:
    """
    Scan meetings directory and normalize folder names
    
    Returns:
        Stats dict with renamed/skipped/error counts
    """
    stats = {'renamed': 0, 'skipped': 0, 'errors': 0, 'already_normalized': 0}
    
    for folder in meetings_dir.iterdir():
        if not folder.is_dir():
            continue
        
        # Skip special folders
        if folder.name.startswith(('BACKUP_', 'CURRENT_', 'Inbox', '.')):
            continue
        
        # Apply filter if provided
        if filter_pattern and not re.search(filter_pattern, folder.name):
            continue
        
        try:
            result = rename_meeting_folder(folder, dry_run=dry_run)
            if result is None:
                if "Already normalized" in str(result):
                    stats['already_normalized'] += 1
                else:
                    stats['skipped'] += 1
            else:
                stats['renamed'] += 1
        except Exception as e:
            print(f"❌ Error processing {folder.name}: {e}")
            stats['errors'] += 1
    
    return stats

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Normalize meeting folder names')
    parser.add_argument(
        '--meetings-dir',
        type=Path,
        default=Path('/home/workspace/Personal/Meetings'),
        help='Meetings directory path'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without renaming'
    )
    parser.add_argument(
        '--filter',
        type=str,
        help='Only process folders matching regex pattern'
    )
    parser.add_argument(
        '--single',
        type=str,
        help='Process single folder by name'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Meeting Folder Name Normalizer")
    print("=" * 60)
    print()
    
    if args.single:
        folder = args.meetings_dir / args.single
        if not folder.exists():
            print(f"❌ Folder not found: {args.single}")
            return 1
        
        rename_meeting_folder(folder, dry_run=args.dry_run)
    else:
        stats = scan_and_normalize_meetings(
            args.meetings_dir,
            dry_run=args.dry_run,
            filter_pattern=args.filter
        )
        
        print()
        print("=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Renamed: {stats['renamed']}")
        print(f"Already normalized: {stats['already_normalized']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        
        if args.dry_run and stats['renamed'] > 0:
            print()
            print("Run without --dry-run to apply changes")
    
    return 0

def extract_metadata_from_b26(meeting_dir: Path) -> Optional[Dict]:
    """Extract structured metadata from B26_metadata.md file
    
    Returns metadata with stakeholders list containing:
        - name: str
        - organization: str | None
        - is_internal: bool
    """
    b26_path = meeting_dir / "B26_metadata.md"
    
    if not b26_path.exists():
        return None
    
    try:
        content = b26_path.read_text()
        metadata = {}
        
        # Extract Meeting ID
        mid_match = re.search(r'\*\*Meeting ID:\*\*\s*(.+?)(?:\n|$)', content)
        if mid_match:
            metadata['meeting_id'] = mid_match.group(1).strip()
        
        # Extract Date
        date_match = re.search(r'\*\*Date:?\*\*\s*(.+?)(?:\n|$)', content)
        if date_match:
            date_str = date_match.group(1).strip()
            # Try to parse and normalize date format
            try:
                # Handle "November 3, 2025" format
                from dateutil.parser import parse as parse_date
                parsed_date = parse_date(date_str)
                metadata['date'] = parsed_date.strftime('%Y-%m-%d')
            except:
                # Fallback: extract from meeting_id or folder name
                if 'meeting_id' in metadata:
                    folder_date = extract_date_from_folder_name(metadata['meeting_id'])
                    if folder_date:
                        metadata['date'] = folder_date
                else:
                    folder_date = extract_date_from_folder_name(meeting_dir.name)
                    if folder_date:
                        metadata['date'] = folder_date
        
        # Extract Meeting Type
        type_match = re.search(r'\*\*Meeting Type\*\*:?\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if type_match:
            meeting_type = type_match.group(1).strip()
            # Remove leading colon if present
            if meeting_type.startswith(':'):
                meeting_type = meeting_type[1:].strip()
            # Extract first word only (e.g., "Internal team coordination" → "internal")
            if meeting_type:
                metadata['meeting_type'] = meeting_type.split()[0].lower()
        
        # Extract Purpose for topic extraction
        purpose_match = re.search(r'\*\*Purpose:?\*\*\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if purpose_match:
            metadata['purpose'] = purpose_match.group(1).strip()
        
        # Extract structured stakeholder data
        stakeholders = _extract_stakeholders(content)
        metadata['stakeholders'] = stakeholders
        
        # Fallback: Extract from Participants section if no stakeholders found
        if not stakeholders:
            participants_section = re.search(r'^## Participants.*?(?=^## |\Z)', content, re.DOTALL | re.MULTILINE)
            if participants_section:
                participants_text = participants_section.group(0)
                
                # Try H3 headers first
                h3_names = re.findall(r'###\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', participants_text)
                
                # Also try bullet-point format: - **Name** - Role
                bullet_names = re.findall(r'-\s+\*\*([A-Z][a-zA-Z\s]+?)\*\*\s*[-–]', participants_text)
                
                all_names = h3_names + bullet_names
                
                # Remove duplicates while preserving order
                seen = set()
                unique_names = []
                for name in all_names:
                    # Clean up name (remove trailing whitespace, parenthetical notes)
                    clean_name = re.sub(r'\s*\([^)]+\).*$', '', name).strip()
                    if clean_name not in seen:
                        seen.add(clean_name)
                        unique_names.append(clean_name)
                
                metadata['participants'] = unique_names
                
                # Convert to stakeholder format without org info
                stakeholders = []
                for name in unique_names:
                    is_internal = _is_internal_name(name)
                    stakeholders.append({
                        'name': name,
                        'organization': None,
                        'is_internal': is_internal
                    })
                metadata['stakeholders'] = stakeholders
        
        return metadata if metadata else None
        
    except Exception as e:
        logging.warning(f"Error parsing B26: {e}")
        return None

def _extract_stakeholders(content: str) -> List[Dict]:
    """Extract stakeholders with organizations from B26 content
    
    Looks for Stakeholders section with formats:
    - **Name** - Organization
    - **Name** (Organization)
    - **Name** - [Organization Unknown]
    """
    stakeholders = []
    
    # Look for Stakeholders section
    stakeholders_section = re.search(r'## Stakeholders.*?(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if not stakeholders_section:
        return stakeholders
    
    stakeholders_text = stakeholders_section.group(0)
    
    # Pattern 1: "**Name** - Organization" or "**Name** – Organization" (em dash)
    pattern1 = r'\*\*([A-Z][a-zA-Z\s]+?)\*\*\s*[-–—]\s*([^\n]+)'
    for match in re.finditer(pattern1, stakeholders_text):
        name = match.group(1).strip()
        org_raw = match.group(2).strip()
        
        # Check if org is unknown marker
        org = None if _is_unknown_org(org_raw) else org_raw
        
        is_internal = _is_internal_name(name)
        
        stakeholders.append({
            'name': name,
            'organization': org,
            'is_internal': is_internal
        })
    
    # Pattern 2: "**Name** (Organization)"
    pattern2 = r'\*\*([A-Z][a-zA-Z\s]+?)\*\*\s*\(([^)]+)\)'
    for match in re.finditer(pattern2, stakeholders_text):
        name = match.group(1).strip()
        org_raw = match.group(2).strip()
        
        org = None if _is_unknown_org(org_raw) else org_raw
        is_internal = _is_internal_name(name)
        
        # Avoid duplicates
        if not any(s['name'] == name for s in stakeholders):
            stakeholders.append({
                'name': name,
                'organization': org,
                'is_internal': is_internal
            })
    
    return stakeholders

def _is_internal_name(name: str) -> bool:
    """Check if name belongs to internal team member"""
    internal_markers = [
        'vrijen', 'attawar', 'careerspan',
        'tiffany', 'ben', 'rob', 'rochel', 'alexis'
        # Note: nafisa is external collaborator, not internal
    ]
    name_lower = name.lower()
    return any(marker in name_lower for marker in internal_markers)

def _is_unknown_org(org: str) -> bool:
    """Check if organization string indicates unknown/needs research"""
    unknown_markers = ['unknown', 'needs research', '[', 'tbd', 'n/a']
    org_lower = org.lower()
    return any(marker in org_lower for marker in unknown_markers)

def generate_folder_name_from_b26(meeting_dir: Path, metadata: Dict) -> str:
    """Generate folder name using priority-based fallback logic
    
    Priority hierarchy:
    1. Single external + org: {date}_FirstLast-OrgName_{type}
    2. Single external no org: {date}_FirstLast_{type}
    3. Multiple same org: {date}_OrgName-meeting_{type}
    4. Multiple different orgs: {date}_multiple-stakeholders_{type}
    5. Unknown: {date}_unknown_{type}
    6. Internal: {date}_team-{topic}_{type}
    """
    date_str = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
    meeting_type = metadata.get('meeting_type', 'external')
    stakeholders = metadata.get('stakeholders', [])
    
    # Priority 5: Unknown (no stakeholders at all)
    if len(stakeholders) == 0:
        return f"{date_str}_unknown_{meeting_type}"
    
    # Filter to external stakeholders only
    external = [s for s in stakeholders if not s['is_internal']]
    
    # Priority 6: Internal meeting (has stakeholders but all internal)
    if len(external) == 0:
        # Try to extract topic from purpose field first
        if 'purpose' in metadata and metadata['purpose']:
            topic = _extract_topic_from_purpose(metadata['purpose'])
        else:
            topic = _extract_topic_from_type(metadata.get('meeting_type', 'team-meeting'))
        return f"{date_str}_team-{topic}_internal"
    
    # Priority 1 & 2: Single external stakeholder
    if len(external) == 1:
        stakeholder = external[0]
        name_slug = _generate_name_slug(stakeholder['name'])
        
        # Priority 1: Has valid organization
        if stakeholder['organization']:
            org_slug = slugify(stakeholder['organization'])
            return f"{date_str}_{name_slug}-{org_slug}_{meeting_type}"
        
        # Priority 2: No organization
        return f"{date_str}_{name_slug}_{meeting_type}"
    
    # Multiple external stakeholders
    if len(external) > 1:
        # Group by organization
        orgs = set()
        for s in external:
            if s['organization']:
                orgs.add(s['organization'])
        
        # Priority 3: All from same organization
        if len(orgs) == 1:
            org_slug = slugify(list(orgs)[0])
            return f"{date_str}_{org_slug}-meeting_{meeting_type}"
        
        # Priority 4: Multiple different organizations (or mixed known/unknown)
        return f"{date_str}_multiple-stakeholders_{meeting_type}"
    
    # Should never reach here, but fallback to unknown
    return f"{date_str}_unknown_{meeting_type}"

def _generate_name_slug(name: str) -> str:
    """Generate FirstLast slug from name
    
    Examples:
        "John Smith" → "JohnSmith"
        "Maria Garcia Lopez" → "MariaGarcia"  (first two parts)
    """
    # Extract capitalized words (proper names)
    name_parts = re.findall(r'[A-Z][a-z]+', name)
    
    if len(name_parts) >= 2:
        # Use first and last name
        return f"{name_parts[0]}{name_parts[-1]}"
    elif len(name_parts) == 1:
        # Only one name part
        return name_parts[0]
    else:
        # Fallback to slugified version
        return slugify(name).replace('-', '')

def _extract_topic_from_type(meeting_type: str) -> str:
    """Extract topic from meeting type string
    
    Examples:
        "Internal team coordination" → "coordination"
        "internal" → "meeting"
    """
    if not meeting_type:
        return "meeting"
    
    parts = meeting_type.lower().split()
    
    # If multi-word, use last significant word
    if len(parts) > 1:
        # Skip common words
        skip_words = {'team', 'internal', 'meeting', 'the', 'a', 'an'}
        significant = [p for p in parts if p not in skip_words]
        if significant:
            return significant[-1]
    
    # Single word or all skipped
    return parts[0] if parts else "meeting"

def _extract_topic_from_purpose(purpose: str) -> str:
    """Extract key topic from purpose statement
    
    Examples:
        "Coordinate and finalize presentation content" → "presentation"
        "Demo prep for AI Circle" → "demo-prep"
        "Weekly standup" → "standup"
    """
    if not purpose:
        return "meeting"
    
    purpose_lower = purpose.lower()
    
    # Common topic keywords to extract
    keywords = [
        'presentation', 'demo', 'prep', 'standup', 'sync', 'planning',
        'retrospective', 'review', 'coordination', 'strategy', 'kickoff',
        'debrief', 'brainstorm', 'workshop', 'training'
    ]
    
    # Check for keyword matches
    for keyword in keywords:
        if keyword in purpose_lower:
            return keyword
    
    # Extract first meaningful noun (capitalized words or action words)
    words = purpose.split()
    for word in words[:5]:  # Only check first 5 words
        word_lower = word.lower().strip('.,;:!?')
        # Skip common filler words
        skip = {'coordinate', 'finalize', 'discuss', 'and', 'the', 'for', 'with', 'about', 'on', 'to', 'a', 'an'}
        if word_lower not in skip and len(word_lower) > 3:
            return slugify(word_lower)
    
    return "meeting"

def test_naming_scenarios():
    """Test naming fallback logic with all priority scenarios"""
    test_cases = [
        {
            'name': 'Priority 1: Single external + org',
            'metadata': {
                'date': '2025-11-03',
                'meeting_type': 'external',
                'stakeholders': [
                    {'name': 'Mihir Makwana', 'organization': 'Northwell', 'is_internal': False}
                ]
            },
            'expected': '2025-11-03_MihirMakwana-northwell_external'
        },
        {
            'name': 'Priority 2: Single external no org',
            'metadata': {
                'date': '2025-11-03',
                'meeting_type': 'external',
                'stakeholders': [
                    {'name': 'Mihir Makwana', 'organization': None, 'is_internal': False}
                ]
            },
            'expected': '2025-11-03_MihirMakwana_external'
        },
        {
            'name': 'Priority 3: Multiple same org',
            'metadata': {
                'date': '2025-11-03',
                'meeting_type': 'external',
                'stakeholders': [
                    {'name': 'John Smith', 'organization': 'Northwell', 'is_internal': False},
                    {'name': 'Jane Doe', 'organization': 'Northwell', 'is_internal': False}
                ]
            },
            'expected': '2025-11-03_northwell-meeting_external'
        },
        {
            'name': 'Priority 4: Multiple different orgs',
            'metadata': {
                'date': '2025-11-03',
                'meeting_type': 'external',
                'stakeholders': [
                    {'name': 'John Smith', 'organization': 'Northwell', 'is_internal': False},
                    {'name': 'Jane Doe', 'organization': 'Mayo Clinic', 'is_internal': False}
                ]
            },
            'expected': '2025-11-03_multiple-stakeholders_external'
        },
        {
            'name': 'Priority 5: Unknown stakeholder',
            'metadata': {
                'date': '2025-11-03',
                'meeting_type': 'external',
                'stakeholders': []
            },
            'expected': '2025-11-03_unknown_external'
        },
        {
            'name': 'Priority 6: Internal meeting',
            'metadata': {
                'date': '2025-11-03',
                'meeting_type': 'internal team coordination',
                'stakeholders': [
                    {'name': 'Vrijen Attawar', 'organization': 'Careerspan', 'is_internal': True},
                    {'name': 'Tiffany Huang', 'organization': 'Careerspan', 'is_internal': True}
                ]
            },
            'expected': '2025-11-03_team-coordination_internal'
        },
        {
            'name': 'Edge case: Single name',
            'metadata': {
                'date': '2025-11-03',
                'meeting_type': 'external',
                'stakeholders': [
                    {'name': 'Nafisa', 'organization': None, 'is_internal': False}
                ]
            },
            'expected': '2025-11-03_Nafisa_external'
        },
        {
            'name': 'Edge case: Org with spaces',
            'metadata': {
                'date': '2025-11-03',
                'meeting_type': 'external',
                'stakeholders': [
                    {'name': 'Sarah Johnson', 'organization': 'Mayo Clinic', 'is_internal': False}
                ]
            },
            'expected': '2025-11-03_SarahJohnson-mayo-clinic_external'
        }
    ]
    
    print("\n" + "=" * 70)
    print("TESTING NAMING SCENARIOS")
    print("=" * 70 + "\n")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        result = generate_folder_name_from_b26(Path('.'), test['metadata'])
        
        if result == test['expected']:
            print(f"✓ Test {i}: {test['name']}")
            print(f"  Result: {result}")
            passed += 1
        else:
            print(f"✗ Test {i}: {test['name']}")
            print(f"  Expected: {test['expected']}")
            print(f"  Got:      {result}")
            failed += 1
        print()
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} total")
    print("=" * 70)
    
    return failed == 0

def enrich_with_calendar_data(meeting_dir: Path, metadata: Dict) -> Dict:
    """Cross-reference with calendar invite metadata"""
    calendar_file = meeting_dir / "_calendar_metadata.json"
    
    if not calendar_file.exists():
        return metadata
    
    try:
        with open(calendar_file) as f:
            cal_data = json.load(f)
        
        # Extract attendees from calendar
        if 'attendees' in cal_data:
            attendees = cal_data['attendees']
            for attendee in attendees:
                email = attendee.get('email', '')
                name = attendee.get('displayName', attendee.get('email', '').split('@')[0])
                
                # Skip internal Careerspan emails
                if 'careerspan' in email.lower() or 'vrijen' in email.lower():
                    continue
                
                # Try to match with existing stakeholders
                if 'stakeholders' in metadata:
                    # Add organization from email domain if missing
                    for stakeholder in metadata['stakeholders']:
                        if stakeholder['name'].lower() in name.lower():
                            if not stakeholder.get('organization') or 'unknown' in stakeholder.get('organization', '').lower():
                                domain = email.split('@')[-1]
                                org_name = domain.split('.')[0].title()
                                stakeholder['organization'] = org_name
                
    except Exception as e:
        logging.debug(f"Could not enrich with calendar data: {e}")
    
    return metadata

def enrich_with_email_data(meeting_dir: Path, metadata: Dict) -> Dict:
    """Cross-reference with email thread metadata"""
    email_file = meeting_dir / "_email_metadata.json"
    
    if not email_file.exists():
        return metadata
    
    try:
        with open(email_file) as f:
            email_data = json.load(f)
        
        # Extract sender/recipients
        if 'from' in email_data:
            sender = email_data['from']
            # Parse and enrich stakeholders
            # Similar logic to calendar enrichment
            
    except Exception as e:
        logging.debug(f"Could not enrich with email data: {e}")
    
    return metadata

if __name__ == '__main__':
    exit(main())
