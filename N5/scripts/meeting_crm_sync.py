#!/usr/bin/env python3
"""
Meeting → CRM Sync Script

Syncs meeting intelligence (B03 Stakeholder Intelligence) to CRM V3 profiles.
Called during MG-6 state transition when meetings move to 'processed' status.

Features:
- Extracts stakeholder insights from B03 blocks
- Appends to Interaction Timeline in CRM profiles
- Queues new stakeholders for enrichment

Usage:
    python3 meeting_crm_sync.py --meeting-folder <path>
    python3 meeting_crm_sync.py --sync-all-processed
"""

import argparse
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
MEETINGS_INBOX = WORKSPACE / "Personal/Meetings/Inbox"
CRM_V3 = WORKSPACE / "Personal/Knowledge/CRM/individuals"
SKIP_FLAG = "_skip_crm.flag"


def normalize_person_id(name: str) -> str:
    """Convert name to person_id format."""
    # Remove special chars, lowercase, replace spaces with hyphens
    clean = re.sub(r'[^\w\s-]', '', name.lower())
    return re.sub(r'\s+', '-', clean.strip())


def find_crm_profile(person_id: str) -> Optional[Path]:
    """Find CRM profile by person_id."""
    # Try exact match first
    for profile in CRM_V3.glob("*.md"):
        content = profile.read_text()
        if person_id in profile.name.lower():
            return profile
    return None


def extract_stakeholder_from_b03(b03_path: Path) -> List[Dict[str, Any]]:
    """Extract stakeholder intelligence from B03 block."""
    content = b03_path.read_text()
    stakeholders = []
    
    # Skip these section headers (not actual people)
    skip_headers = {'participants', 'group dynamics', 'meeting context', 'relationship', 
                    'process stage', 'b03', 'stakeholder intelligence'}
    
    # Look for ## or ### Name patterns (individual stakeholders)
    # Format: ## Name or ### Name or ### 1. Name
    stakeholder_pattern = r'##{1,2}\s+(?:\d+\.\s*)?([^\n]+)\n((?:(?!##{1,2})[\s\S])*?)(?=##{1,2}|\Z)'
    matches = re.findall(stakeholder_pattern, content, re.MULTILINE)
    
    for name_line, section_content in matches:
        # Clean name - remove parenthetical notes like "(V)"
        name = re.sub(r'\s*\([^)]*\)\s*$', '', name_line).strip()
        
        # Skip section headers and self (Vrijen)
        if name.lower() in skip_headers:
            continue
        if 'vrijen' in name.lower():
            continue
        # Skip multi-person entries like "Victoria & Chase"
        if ' & ' in name or ' and ' in name.lower():
            continue
            
        stakeholder = {
            'name': name,
            'person_id': normalize_person_id(name),
            'raw_section': section_content,
        }
        
        # Extract specific fields from section content
        for line in section_content.split('\n'):
            line_lower = line.lower()
            if '**role**:' in line_lower or '**title**:' in line_lower:
                stakeholder['role'] = line.split(':', 1)[1].strip().strip('*')
            elif '**organization**:' in line_lower or '**company**:' in line_lower:
                stakeholder['organization'] = line.split(':', 1)[1].strip().strip('*')
            elif '**sentiment**:' in line_lower:
                stakeholder['sentiment'] = line.split(':', 1)[1].strip().strip('*')
            elif '**key signals**:' in line_lower or '**key interests**:' in line_lower:
                stakeholder['signals'] = line.split(':', 1)[1].strip().strip('*')
            elif '**skepticism**:' in line_lower or '**inquiry**:' in line_lower:
                stakeholder['skepticism'] = line.split(':', 1)[1].strip().strip('*')
            elif '**leverage**:' in line_lower:
                stakeholder['leverage'] = line.split(':', 1)[1].strip().strip('*')
        
        stakeholders.append(stakeholder)
    
    return stakeholders


def extract_meeting_metadata(meeting_folder: Path) -> Dict[str, Any]:
    """Extract meeting metadata from manifest.json or B26."""
    metadata = {
        'meeting_id': meeting_folder.name,
        'date': None,
        'title': None,
        'type': None,
    }
    
    # Try manifest.json first
    manifest = meeting_folder / "manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text())
        metadata['date'] = data.get('date', data.get('meeting_date'))
        metadata['title'] = data.get('title', data.get('meeting_title'))
        metadata['type'] = data.get('meeting_type')
    
    # Fallback to B26
    b26 = meeting_folder / "B26_MEETING_METADATA.md"
    if b26.exists():
        content = b26.read_text()
        # Handle both "**Field:**" and "- **Field:**" formats
        date_match = re.search(r'-?\s*\*\*Date\*\*:\s*([\d-]+)', content)
        title_match = re.search(r'-?\s*\*\*Title\*\*:\s*(.+)', content)
        type_match = re.search(r'-?\s*\*\*Meeting Type\*\*:\s*(.+)', content)
        
        if date_match and not metadata['date']:
            metadata['date'] = date_match.group(1).strip()
        if title_match and not metadata['title']:
            metadata['title'] = title_match.group(1).strip()
        if type_match and not metadata['type']:
            metadata['type'] = type_match.group(1).strip()
    
    # Extract date from folder name if needed
    if not metadata['date']:
        date_match = re.match(r'(\d{8})', meeting_folder.name)
        if date_match:
            d = date_match.group(1)
            metadata['date'] = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    
    return metadata


def append_to_interaction_timeline(profile_path: Path, meeting_metadata: Dict, stakeholder_intel: Dict) -> bool:
    """Append meeting to the Interaction Timeline section of a CRM profile."""
    content = profile_path.read_text()
    
    # Build timeline entry
    date = meeting_metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
    title = meeting_metadata.get('title', 'Meeting')
    meeting_type = meeting_metadata.get('type', 'External')
    
    entry_lines = [
        f"### {date} | {meeting_type}: {title}",
    ]
    
    if stakeholder_intel.get('role'):
        entry_lines.append(f"- **Their Role:** {stakeholder_intel['role']}")
    if stakeholder_intel.get('sentiment'):
        entry_lines.append(f"- **Sentiment:** {stakeholder_intel['sentiment']}")
    if stakeholder_intel.get('signals'):
        entry_lines.append(f"- **Key Signals:** {stakeholder_intel['signals']}")
    
    entry_lines.append(f"- **Source:** {meeting_metadata['meeting_id']}/B03_STAKEHOLDER_INTELLIGENCE.md")
    
    new_entry = '\n'.join(entry_lines)
    
    # Find Interaction Timeline section
    timeline_marker = "## Interaction History"
    if timeline_marker not in content:
        logger.warning(f"No Interaction History section in {profile_path.name}")
        return False
    
    # Insert new entry after the header
    parts = content.split(timeline_marker)
    if len(parts) != 2:
        logger.warning(f"Malformed Interaction Timeline in {profile_path.name}")
        return False
    
    before = parts[0]
    after = parts[1]
    
    # Check if this meeting is already recorded
    if meeting_metadata['meeting_id'] in after:
        logger.info(f"Meeting {meeting_metadata['meeting_id']} already in timeline for {profile_path.name}")
        return True
    
    # Find where to insert (after header, before first entry or ----)
    insert_point = after.find('\n\n')
    if insert_point == -1:
        insert_point = 0
    
    # Handle "No interactions recorded" placeholder
    if "*No interactions recorded yet.*" in after:
        after = after.replace("*No interactions recorded yet.*", "")
    
    new_content = (
        before + 
        timeline_marker + 
        after[:insert_point + 2] + 
        new_entry + "\n\n" +
        after[insert_point + 2:]
    )
    
    # Update last_edited in frontmatter
    new_content = re.sub(
        r'last_edited: [\d-]+',
        f'last_edited: {datetime.now().strftime("%Y-%m-%d")}',
        new_content
    )
    
    profile_path.write_text(new_content)
    return True


def sync_meeting_to_crm(meeting_folder: Path, dry_run: bool = False) -> dict:
    """Sync a single meeting's B03 stakeholder intelligence to CRM profiles."""
    result = {
        'meeting': meeting_folder.name,
        'synced': [],
        'skipped': [],
        'not_found': [],
        'errors': []
    }
    
    b03_path = meeting_folder / "B03_STAKEHOLDER_INTELLIGENCE.md"
    if not b03_path.exists():
        result['errors'].append("No B03_STAKEHOLDER_INTELLIGENCE.md found")
        return result
    
    # Extract metadata and stakeholders
    metadata = extract_meeting_metadata(meeting_folder)
    stakeholders = extract_stakeholder_from_b03(b03_path)
    
    logger.info(f"Processing {meeting_folder.name}: {len(stakeholders)} stakeholders found")
    
    for stakeholder in stakeholders:
        person_id = stakeholder['person_id']
        
        # Skip "Vrijen" (that's you)
        if 'vrijen' in person_id.lower():
            result['skipped'].append(f"{stakeholder['name']} (self)")
            continue
        
        # Find CRM profile
        profile_path = find_crm_profile(person_id)
        
        if not profile_path:
            result['not_found'].append(stakeholder['name'])
            logger.warning(f"No CRM profile found for {stakeholder['name']} ({person_id})")
            continue
        
        if dry_run:
            result['synced'].append(f"{stakeholder['name']} -> {profile_path.name}")
            logger.info(f"[DRY-RUN] Would sync {stakeholder['name']} to {profile_path.name}")
        else:
            try:
                success = append_to_interaction_timeline(profile_path, metadata, stakeholder)
                if success:
                    result['synced'].append(f"{stakeholder['name']} -> {profile_path.name}")
                    logger.info(f"Synced {stakeholder['name']} to {profile_path.name}")
                else:
                    result['errors'].append(f"Failed to update {profile_path.name}")
            except Exception as e:
                result['errors'].append(f"{stakeholder['name']}: {str(e)}")
                logger.error(f"Error syncing {stakeholder['name']}: {e}")
    
    return result


def scan_for_ready_meetings() -> List[Path]:
    """Find meetings ready for CRM sync (processed status, has B03)."""
    ready = []
    
    for folder in MEETINGS_INBOX.iterdir():
        if not folder.is_dir():
            continue
        
        # Check manifest for processed status
        manifest_path = folder / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            status = manifest.get('status', '')
            
            # Check if processed and has B03
            if 'processed' in status.lower() or manifest.get('crm_synced') is False:
                b03 = folder / "B03_STAKEHOLDER_INTELLIGENCE.md"
                if b03.exists():
                    # Check if not already synced
                    if not manifest.get('crm_synced', False):
                        ready.append(folder)
    
    return ready


def mark_meeting_synced(meeting_folder: Path):
    """Mark meeting as CRM-synced in manifest."""
    manifest_path = meeting_folder / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        manifest['crm_synced'] = True
        manifest['crm_sync_timestamp'] = datetime.now().isoformat()
        manifest_path.write_text(json.dumps(manifest, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Sync meeting intelligence to CRM')
    parser.add_argument('--meeting-folder', type=str, help='Path to specific meeting folder')
    parser.add_argument('--scan', action='store_true', help='Scan for all ready meetings')
    parser.add_argument('--dry-run', action='store_true', help='Preview without changes')
    
    args = parser.parse_args()
    
    if args.meeting_folder:
        folder = Path(args.meeting_folder)
        if not folder.exists():
            logger.error(f"Meeting folder not found: {folder}")
            return
        
        result = sync_meeting_to_crm(folder, dry_run=args.dry_run)
        
        if not args.dry_run and result['synced']:
            mark_meeting_synced(folder)
        
        print(json.dumps(result, indent=2))
        
    elif args.scan:
        ready_meetings = scan_for_ready_meetings()
        logger.info(f"Found {len(ready_meetings)} meetings ready for CRM sync")
        
        all_results = []
        for folder in ready_meetings:
            result = sync_meeting_to_crm(folder, dry_run=args.dry_run)
            all_results.append(result)
            
            if not args.dry_run and result['synced']:
                mark_meeting_synced(folder)
        
        # Summary
        total_synced = sum(len(r['synced']) for r in all_results)
        total_not_found = sum(len(r['not_found']) for r in all_results)
        total_errors = sum(len(r['errors']) for r in all_results)
        
        print("\n" + "="*50)
        print("CRM SYNC SUMMARY")
        print("="*50)
        print(f"Meetings processed: {len(all_results)}")
        print(f"Profiles updated:   {total_synced}")
        print(f"Profiles not found: {total_not_found}")
        print(f"Errors:             {total_errors}")
        
        if args.dry_run:
            print("\n[DRY-RUN MODE] No files were modified.")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()





