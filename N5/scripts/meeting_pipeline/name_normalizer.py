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

# Import LLM naming module (with fallback to pattern-based naming)
try:
    from llm_naming import generate_folder_name_llm
    LLM_NAMING_AVAILABLE = True
except ImportError:
    LLM_NAMING_AVAILABLE = False
    logging.warning("LLM naming module not available, using pattern-based naming only")

# === NEW: Helpers for safer metadata extraction and naming ===
NAME_TOKEN_RE = re.compile(r"^[A-Z][a-zA-Z\-']+$")
PARENS_ORG_RE = re.compile(r"\(([^)]+)\)")
ATTENDEES_LINE_RE = re.compile(r"^\*\*Attendees:\*\*\s*(.+)$|^Attendees:\s*(.+)$", re.IGNORECASE)

def _normalize_person_name(raw: str) -> str:
    """Return First-Last form with hyphen, stripping extra notes."""
    # Remove extra commas/notes
    raw = raw.strip().replace("  ", " ")
    # Remove trailing roles in brackets e.g., "John Doe [Host]"
    raw = re.sub(r"\s*\[[^\]]+\]$", "", raw)
    # Remove email angle brackets
    raw = re.sub(r"<[^>]+>", "", raw)
    parts = [p for p in re.split(r"\s+", raw) if p]
    if len(parts) >= 2 and all(NAME_TOKEN_RE.match(p.split('-')[0]) for p in parts[:2]):
        first, last = parts[0], parts[1]
        return f"{first}-{last}"
    # Fallback: return tokenized single
    return parts[0] if parts else "unknown"

def _normalize_org(raw: str) -> str:
    raw = raw.strip()
    # Common suffix removal
    raw = re.sub(r",?\s+(Inc\.|LLC|Ltd\.|Corp\.|Corporation)$", "", raw, flags=re.IGNORECASE)
    # Lowercase hyphenated
    return re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip('-') or "unknown"

def _extract_attendees_from_b26_text(text: str) -> list[dict]:
    """Parse 'Attendees:' line from B26 freeform markdown and return [{'name':..., 'organization':..., 'is_internal': bool}]"""
    attendees = []
    # Find a line that starts with Attendees:
    for line in text.splitlines():
        m = ATTENDEES_LINE_RE.match(line.strip())
        if not m:
            continue
        payload = m.group(1) or m.group(2) or ""
        # Split on commas, then parse "Name (Org)"
        for chunk in [c.strip() for c in payload.split(',') if c.strip()]:
            # Extract org in parentheses if present
            org_match = PARENS_ORG_RE.search(chunk)
            org = org_match.group(1).strip() if org_match else None
            name = PARENS_ORG_RE.sub("", chunk).strip()
            if not name:
                continue
            norm_name = _normalize_person_name(name)
            norm_org = _normalize_org(org) if org else None
            is_internal = (norm_org == "careerspan") or ("vrijen" in name.lower())
            attendees.append({
                "name": norm_name,
                "organization": norm_org,
                "is_internal": is_internal,
            })
        break
    return attendees

def _pick_topic_from_b28_text(text: str) -> str:
    """Very light topic extractor from B28 when multiple orgs."""
    # Look for Meeting Type or Strategic Context lines
    for key in ("Meeting Type", "Strategic Context", "Topic"):
        m = re.search(rf"\*\*{key}\*\*:\s*(.+)$", text, flags=re.IGNORECASE | re.MULTILINE)
        if m:
            val = m.group(1).strip()
            # pick last significant word
            tokens = re.split(r"\W+", val.lower())
            tokens = [t for t in tokens if t and t not in {"call","meeting","sync","discussion","chat","review","weekly"}]
            if tokens:
                return tokens[-1]
    return "external"

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

def rename_meeting_folder(old_path: Path, dry_run: bool = False) -> Optional[str]:
    """Compute new name and perform guarded rename. Returns new path string or None if skipped."""
    # Skip if idempotency marker present
    if (old_path / ".standardized").exists():
        logging.info("Skip: already standardized → %s", old_path.name)
        return None

    # Load B26/B28
    b26_meta = extract_metadata_from_b26(old_path)
    b28_path = old_path / "B28_strategic_intelligence.md"
    b28_text = b28_path.read_text(errors="ignore") if b28_path.exists() else ""

    # Try LLM naming first if available
    new_name = None
    try:
        from llm_naming import call_b99_prompt  # optional
        b26_text = (old_path / "B26_metadata.md").read_text(errors="ignore") if (old_path / "B26_metadata.md").exists() else ""
        suggested = call_b99_prompt(b26_text, b28_text, current_name=old_path.name)
        if suggested:
            new_name = suggested
    except Exception as e:
        logging.debug("LLM naming not available or failed: %s", e)

    # Fallback to safer B26-based naming
    if not new_name:
        new_name = generate_folder_name_from_b26(old_path, b26_meta, b28_text)

    # Gating: do not downgrade to unknown_* if current looks specific
    if "unknown_" in new_name and "unknown_" not in old_path.name:
        logging.info("Skip downgrade to unknown: %s → %s", old_path.name, new_name)
        return None

    if new_name == old_path.name:
        logging.info("Already normalized: %s", old_path.name)
        return None

    new_path = old_path.parent / new_name

    action_msg = f"Would rename: {old_path.name} → {new_name}" if dry_run else f"Renaming: {old_path.name} → {new_name}"
    print(action_msg)

    if dry_run:
        return new_name

    if new_path.exists():
        logging.warning("Target exists, appending -2: %s", new_path)
        new_path = old_path.parent / f"{new_name}-2"

    old_path.rename(new_path)
    # Write idempotency marker
    (new_path / ".standardized").write_text("named-by:name_normalizer v1\n")
    return str(new_path)

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

def extract_metadata_from_b26(meeting_dir: Path) -> dict:
    """Augment existing extractor with Attendees fallback."""
    b26 = meeting_dir / "B26_metadata.md"
    meta = {"stakeholders": []}
    if b26.exists():
        text = b26.read_text(errors="ignore")
        # Existing logic (kept)
        try:
            content = b26.read_text()
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
            logging.debug("Existing B26 parse failed; will try attendees fallback")
        # NEW: Attendees fallback if stakeholders empty
        if not meta.get("stakeholders"):
            attendees = _extract_attendees_from_b26_text(text)
            if attendees:
                meta["stakeholders"] = attendees
        # Capture date if present
        m = re.search(r"^\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", text, flags=re.MULTILINE)
        if m:
            meta["date"] = m.group(1)
    return meta

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

def generate_folder_name_from_b26(meeting_dir: Path, metadata: dict, b28_text: str | None = None) -> str:
    """Safer decision logic using stakeholders from B26 or attendees fallback."""
    date_str = metadata.get("date") or datetime.now().strftime("%Y-%m-%d")
    stakeholders = metadata.get("stakeholders") or []
    externals = [s for s in stakeholders if not s.get("is_internal")]
    meeting_type = metadata.get("meeting_type", "external")

    # Priority 1: Single external stakeholder ⇒ First-Last
    if len(externals) == 1:
        ident = externals[0]["name"]  # already First-Last
        return f"{date_str}_{ident}_{meeting_type}"

    # Priority 2: Multiple externals, same org ⇒ org
    if len(externals) >= 2:
        orgs = {s.get("organization") for s in externals if s.get("organization")}
        if len(orgs) == 1 and orgs:
            org = list(orgs)[0]
            return f"{date_str}_{org}_{meeting_type}"

    # Priority 3: Different orgs ⇒ topic
    topic = _pick_topic_from_b28_text(b28_text or "")
    return f"{date_str}_{topic}_{meeting_type}"

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
