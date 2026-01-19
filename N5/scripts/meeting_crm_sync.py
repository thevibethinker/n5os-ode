#!/usr/bin/env python3
"""
Meeting → CRM Sync Script

Syncs meeting intelligence (B03 Stakeholder Intelligence) to CRM profiles.
Called during MG-6 state transition when meetings move to 'processed' status.

Features:
- Extracts stakeholder insights from B03 blocks
- Creates interaction records in unified n5_core.db
- Updates markdown CRM profiles with interaction timeline
- Queues new stakeholders for enrichment

UPDATED 2026-01-19: Now uses unified n5_core.db for all database operations.

Usage:
    python3 meeting_crm_sync.py --meeting-folder <path>
    python3 meeting_crm_sync.py --scan
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from db_paths import get_db_connection, PEOPLE_TABLE, INTERACTIONS_TABLE
from crm_paths import CRM_INDIVIDUALS, MEETINGS_ROOT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
MEETINGS_INBOX = MEETINGS_ROOT / "Inbox"
CRM_V3 = CRM_INDIVIDUALS
SKIP_FLAG = "_skip_crm.flag"


def normalize_person_id(name: str) -> str:
    """Convert name to person_id format (slug)."""
    clean = re.sub(r'[^\w\s-]', '', name.lower())
    return re.sub(r'\s+', '-', clean.strip())


def find_person_by_name(name: str) -> Optional[Dict]:
    """Find person in unified database by name.
    
    Returns dict with id, full_name, email, markdown_path or None.
    """
    conn = get_db_connection(readonly=True)
    try:
        # Try exact match
        row = conn.execute(
            f"SELECT id, full_name, email, markdown_path, company FROM {PEOPLE_TABLE} WHERE full_name = ?",
            (name,)
        ).fetchone()
        if row:
            return dict(row)
        
        # Try case-insensitive
        row = conn.execute(
            f"SELECT id, full_name, email, markdown_path, company FROM {PEOPLE_TABLE} WHERE LOWER(full_name) = LOWER(?)",
            (name,)
        ).fetchone()
        if row:
            return dict(row)
        
        return None
    finally:
        conn.close()


def find_person_with_deals(name: str) -> Optional[Dict]:
    """Find person with their deal involvement.
    
    Returns person info plus deal_involvement string.
    """
    conn = get_db_connection(readonly=True)
    try:
        row = conn.execute(
            f"""
            SELECT 
                p.id, p.full_name, p.email, p.markdown_path, p.company,
                GROUP_CONCAT(d.company || ' (' || dr.role || ')') as deal_involvement
            FROM {PEOPLE_TABLE} p
            LEFT JOIN deal_roles dr ON p.id = dr.person_id
            LEFT JOIN deals d ON dr.deal_id = d.id
            WHERE LOWER(p.full_name) = LOWER(?)
            GROUP BY p.id
            """,
            (name,)
        ).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def create_interaction(person_id: int, meeting_folder: str, meeting_id: str, 
                       meeting_date: str, summary: str = None) -> int:
    """Create an interaction record for a meeting.
    
    Returns the interaction id.
    """
    conn = get_db_connection()
    try:
        # Check if already exists
        existing = conn.execute(
            f"SELECT id FROM {INTERACTIONS_TABLE} WHERE person_id = ? AND source_ref = ?",
            (person_id, meeting_folder)
        ).fetchone()
        
        if existing:
            return existing['id']
        
        cursor = conn.execute(
            f"""INSERT INTO {INTERACTIONS_TABLE} 
               (person_id, type, direction, summary, source_ref, occurred_at)
               VALUES (?, 'meeting', 'bidirectional', ?, ?, ?)""",
            (person_id, summary or f"Meeting: {meeting_id}", meeting_folder, meeting_date)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def find_crm_profile(person_id: str) -> Optional[Path]:
    """Find CRM profile by person_id (slug)."""
    # Direct path match
    direct = CRM_V3 / f"{person_id}.md"
    if direct.exists():
        return direct
    
    # Fallback: scan for partial match
    for profile in CRM_V3.glob("*.md"):
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
        # Skip multi-person entries
        if ' & ' in name or ' and ' in name.lower():
            continue
            
        stakeholder = {
            'name': name,
            'person_id': normalize_person_id(name),
            'raw_section': section_content,
        }
        
        # Extract specific fields
        for line in section_content.split('\n'):
            line_lower = line.lower()
            if '**role**:' in line_lower or '**title**:' in line_lower:
                stakeholder['role'] = line.split(':', 1)[1].strip().strip('*')
            elif '**organization**:' in line_lower or '**company**:' in line_lower:
                stakeholder['organization'] = line.split(':', 1)[1].strip().strip('*')
            elif '**sentiment**:' in line_lower:
                stakeholder['sentiment'] = line.split(':', 1)[1].strip().strip('*')
            elif '**signals**:' in line_lower or '**key signals**:' in line_lower:
                stakeholder['signals'] = line.split(':', 1)[1].strip().strip('*')
        
        stakeholders.append(stakeholder)
    
    return stakeholders


def update_crm_profile_timeline(profile_path: Path, meeting_metadata: Dict, 
                                 stakeholder_intel: Dict, dry_run: bool = False) -> bool:
    """Append meeting interaction to CRM profile's Interaction History section."""
    content = profile_path.read_text()
    
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
    
    # Find where to insert
    insert_point = after.find('\n\n')
    if insert_point == -1:
        insert_point = 0
    
    # Handle "No interactions recorded" placeholder
    placeholder_pattern = r'\*No interactions recorded yet\.?\*'
    after_cleaned = re.sub(placeholder_pattern, '', after)
    
    # Insert new entry
    new_after = after_cleaned[:insert_point] + '\n\n' + new_entry + after_cleaned[insert_point:]
    new_content = before + timeline_marker + new_after
    
    if not dry_run:
        profile_path.write_text(new_content)
        logger.info(f"Updated timeline in {profile_path.name}")
    else:
        logger.info(f"[DRY-RUN] Would update timeline in {profile_path.name}")
    
    return True


def sync_meeting_to_crm(meeting_folder: Path, dry_run: bool = False) -> Dict[str, Any]:
    """Sync a single meeting to CRM profiles and database."""
    result = {
        'meeting_folder': str(meeting_folder),
        'synced': [],
        'not_found': [],
        'errors': [],
        'db_interactions': []
    }
    
    # Check for skip flag
    if (meeting_folder / SKIP_FLAG).exists():
        logger.info(f"Skipping {meeting_folder.name} - has skip flag")
        return result
    
    # Load manifest
    manifest_path = meeting_folder / "manifest.json"
    if not manifest_path.exists():
        result['errors'].append("No manifest.json found")
        return result
    
    manifest = json.loads(manifest_path.read_text())
    meeting_metadata = {
        'meeting_id': manifest.get('meeting_id', meeting_folder.name),
        'title': manifest.get('title', manifest.get('summary', 'Meeting')),
        'date': manifest.get('start_time', manifest.get('date', datetime.now().strftime('%Y-%m-%d'))),
        'type': manifest.get('meeting_type', 'External')
    }
    
    # Find B03 block
    b03_paths = [
        meeting_folder / "B03_STAKEHOLDER_INTELLIGENCE.md",
        meeting_folder / "B03_STAKE_HOLDER_INTELLIGENCE.md",
        meeting_folder / "B08_STAKEHOLDER_INTELLIGENCE.md",
    ]
    
    b03_path = None
    for path in b03_paths:
        if path.exists():
            b03_path = path
            break
    
    if not b03_path:
        result['errors'].append("No B03 stakeholder intelligence found")
        return result
    
    # Extract stakeholders
    stakeholders = extract_stakeholder_from_b03(b03_path)
    logger.info(f"Found {len(stakeholders)} stakeholders in {meeting_folder.name}")
    
    for stakeholder in stakeholders:
        name = stakeholder['name']
        person_id = stakeholder['person_id']
        
        # Check database for person (with deal info)
        db_person = find_person_with_deals(name)
        
        if db_person:
            # Create interaction record in database
            if not dry_run:
                interaction_id = create_interaction(
                    person_id=db_person['id'],
                    meeting_folder=str(meeting_folder),
                    meeting_id=meeting_metadata['meeting_id'],
                    meeting_date=meeting_metadata['date'],
                    summary=f"Meeting: {meeting_metadata['title']}"
                )
                result['db_interactions'].append({
                    'person_id': db_person['id'],
                    'interaction_id': interaction_id,
                    'name': name
                })
            
            # Also update markdown profile if it exists
            if db_person.get('markdown_path'):
                profile_path = WORKSPACE / db_person['markdown_path']
                if profile_path.exists():
                    success = update_crm_profile_timeline(
                        profile_path, meeting_metadata, stakeholder, dry_run
                    )
                    if success:
                        result['synced'].append(name)
                    else:
                        result['errors'].append(f"Failed to update timeline for {name}")
                else:
                    result['synced'].append(f"{name} (DB only)")
            else:
                result['synced'].append(f"{name} (DB only)")
        else:
            # Fallback: Try markdown-only lookup
            profile_path = find_crm_profile(person_id)
            if profile_path:
                success = update_crm_profile_timeline(
                    profile_path, meeting_metadata, stakeholder, dry_run
                )
                if success:
                    result['synced'].append(name)
                else:
                    result['errors'].append(f"Failed to update timeline for {name}")
            else:
                result['not_found'].append(name)
                logger.warning(f"No CRM profile or DB entry found for: {name}")
    
    return result


def scan_for_ready_meetings() -> List[Path]:
    """Scan for meetings ready for CRM sync."""
    ready = []
    
    for folder in MEETINGS_INBOX.iterdir():
        if not folder.is_dir():
            continue
        
        manifest_path = folder / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            status = manifest.get('status', '')
            
            # Check if processed and has B03
            if 'processed' in status.lower() or manifest.get('crm_synced') is False:
                b03 = folder / "B03_STAKEHOLDER_INTELLIGENCE.md"
                if b03.exists():
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
    parser.add_argument('--help-extended', action='store_true', help='Show extended help')
    
    args = parser.parse_args()
    
    if args.help_extended:
        print(__doc__)
        return
    
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
        total_db = sum(len(r['db_interactions']) for r in all_results)
        
        print("\n" + "="*50)
        print("CRM SYNC SUMMARY")
        print("="*50)
        print(f"Meetings processed:    {len(all_results)}")
        print(f"Profiles updated:      {total_synced}")
        print(f"DB interactions:       {total_db}")
        print(f"Profiles not found:    {total_not_found}")
        print(f"Errors:                {total_errors}")
        
        if args.dry_run:
            print("\n[DRY-RUN MODE] No files were modified.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
