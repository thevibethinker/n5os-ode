#!/usr/bin/env python3
"""
Post-Meeting Profile Enrichment Watcher

Watches for new meeting transcript.jsonl files and triggers stakeholder profile enrichment.
Separate from meeting_processor_v3.py - this handles post-meeting profile updates.

Pattern: Generate NEW documents each time (never edit existing).
"""

import argparse
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
PROFILES_DB = Path("/home/workspace/N5/data/profiles.db")


def get_db_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(PROFILES_DB)
    conn.row_factory = sqlite3.Row
    return conn


def find_new_meetings_with_transcripts() -> List[Path]:
    """
    Find meeting folders with transcript.jsonl files that haven't been enriched yet.
    
    Returns:
        List of meeting folder paths
    """
    new_meetings = []
    
    if not MEETINGS_DIR.exists():
        logging.warning(f"Meetings directory not found: {MEETINGS_DIR}")
        return new_meetings
    
    for meeting_folder in MEETINGS_DIR.iterdir():
        if not meeting_folder.is_dir():
            continue
        
        # Look for transcript.jsonl file
        transcript_files = list(meeting_folder.glob("*.transcript.jsonl"))
        if not transcript_files:
            continue
        
        # Check if this meeting has been enriched
        if not needs_enrichment(meeting_folder):
            continue
        
        new_meetings.append(meeting_folder)
        logging.info(f"Found new meeting for enrichment: {meeting_folder.name}")
    
    return new_meetings


def needs_enrichment(meeting_folder: Path) -> bool:
    """
    Check if meeting needs enrichment.
    
    Logic:
    - Has transcript.jsonl
    - Has NOT been enriched yet (no post_meeting_enrichments record)
    
    Args:
        meeting_folder: Path to meeting folder
        
    Returns:
        True if needs enrichment
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get stakeholder email from meeting folder
        stakeholder_email = extract_stakeholder_email(meeting_folder)
        if not stakeholder_email:
            return False
        
        # Check if profile exists
        cursor.execute(
            "SELECT id FROM profiles WHERE email = ?",
            (stakeholder_email,)
        )
        profile = cursor.fetchone()
        
        if not profile:
            logging.info(f"No profile found for {stakeholder_email}, skipping enrichment")
            return False
        
        profile_id = profile[0]
        
        # Check if already enriched
        cursor.execute(
            """
            SELECT COUNT(*) as count 
            FROM post_meeting_enrichments 
            WHERE profile_id = ? AND meeting_folder = ?
            """,
            (profile_id, str(meeting_folder))
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] == 0
        
    except Exception as e:
        logging.error(f"Error checking enrichment status: {e}", exc_info=True)
        return False


def extract_stakeholder_email(meeting_folder: Path) -> Optional[str]:
    """
    Extract stakeholder email from meeting folder name or metadata.
    
    Meeting folder pattern: YYYY-MM-DD_type-name-x-name
    
    Args:
        meeting_folder: Path to meeting folder
        
    Returns:
        Email if found, None otherwise
    """
    try:
        # Check for _metadata.json first
        metadata_file = meeting_folder / "_metadata.json"
        if metadata_file.exists():
            import json
            with open(metadata_file) as f:
                metadata = json.load(f)
                participants = metadata.get("participants", [])
                # Find external stakeholder (not V)
                for participant in participants:
                    email = participant.get("email", "")
                    if email and "vrijen" not in email.lower():
                        return email
        
        # Fallback: derive from folder name
        # Pattern: YYYY-MM-DD_external-firstname-lastname-x-vrijen-attawar
        folder_name = meeting_folder.name
        parts = folder_name.split("_")
        if len(parts) >= 2:
            name_part = parts[1]
            if "external" in name_part:
                # Extract name components
                name_components = name_part.split("-")
                if len(name_components) >= 3:
                    # external-firstname-lastname-x-...
                    first = name_components[1]
                    last = name_components[2]
                    # Construct email (assumption: firstname.lastname@company.com)
                    # This is a fallback - real data should come from metadata
                    logging.warning(f"Could not determine email from metadata for {folder_name}")
                    return None
        
        return None
        
    except Exception as e:
        logging.error(f"Error extracting stakeholder email: {e}", exc_info=True)
        return None


def enrich_profile_post_meeting(meeting_folder: Path, dry_run: bool = False) -> bool:
    """
    Enrich stakeholder profile after meeting completion.
    
    Steps:
    1. Identify stakeholder from meeting folder
    2. Read intelligence blocks: key_insights.md, relationship_notes.md, action_items.md
    3. Generate NEW relationship_delta_YYYY-MM-DD.md
    4. Regenerate relationship_context.md (synthesis of old + new)
    5. Update profiles.db tracking
    
    Args:
        meeting_folder: Path to meeting folder
        dry_run: If True, don't write files or database
        
    Returns:
        True if successful
    """
    try:
        logging.info(f"{'[DRY-RUN] ' if dry_run else ''}Enriching profile for meeting: {meeting_folder.name}")
        
        # Step 1: Identify stakeholder
        stakeholder_email = extract_stakeholder_email(meeting_folder)
        if not stakeholder_email:
            logging.error(f"Could not identify stakeholder for {meeting_folder.name}")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, name, profile_path FROM profiles WHERE email = ?",
            (stakeholder_email,)
        )
        profile = cursor.fetchone()
        
        if not profile:
            logging.error(f"No profile found for {stakeholder_email}")
            conn.close()
            return False
        
        profile_id = profile["id"]
        profile_name = profile["name"]
        profile_path = Path(profile["profile_path"])
        
        logging.info(f"Found profile: {profile_name} at {profile_path}")
        
        # Step 2: Read intelligence blocks
        intelligence_blocks = read_intelligence_blocks(meeting_folder)
        if not intelligence_blocks:
            logging.warning(f"No intelligence blocks found in {meeting_folder.name}")
            # Still record the enrichment attempt
        
        # Step 3: Generate NEW relationship_delta
        meeting_date = extract_meeting_date(meeting_folder)
        delta_filename = f"relationship_delta_{meeting_date}.md"
        delta_path = profile_path / delta_filename
        
        if not dry_run:
            generate_relationship_delta(
                delta_path, 
                meeting_folder, 
                intelligence_blocks
            )
            logging.info(f"✓ Generated {delta_filename}")
        else:
            logging.info(f"[DRY-RUN] Would generate {delta_filename}")
        
        # Step 4: Regenerate relationship_context.md
        context_path = profile_path / "relationship_context.md"
        
        if not dry_run:
            regenerate_relationship_context(profile_path, context_path)
            logging.info(f"✓ Regenerated relationship_context.md")
        else:
            logging.info(f"[DRY-RUN] Would regenerate relationship_context.md")
        
        # Step 5: Update profiles.db
        if not dry_run:
            now = datetime.utcnow().isoformat()
            
            # Update profiles table
            cursor.execute(
                """
                UPDATE profiles 
                SET last_enriched_at = ?, enrichment_count = enrichment_count + 1
                WHERE id = ?
                """,
                (now, profile_id)
            )
            
            # Insert enrichment record
            cursor.execute(
                """
                INSERT INTO post_meeting_enrichments 
                (profile_id, meeting_folder, meeting_date, enriched_at, 
                 blocks_found, delta_file, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile_id,
                    str(meeting_folder),
                    meeting_date,
                    now,
                    len(intelligence_blocks),
                    str(delta_path),
                    True
                )
            )
            
            conn.commit()
            logging.info(f"✓ Updated profiles.db")
        else:
            logging.info(f"[DRY-RUN] Would update profiles.db")
        
        conn.close()
        return True
        
    except Exception as e:
        logging.error(f"Error enriching profile: {e}", exc_info=True)
        return False


def extract_meeting_date(meeting_folder: Path) -> str:
    """Extract meeting date from folder name (YYYY-MM-DD_...)."""
    folder_name = meeting_folder.name
    return folder_name.split("_")[0]


def read_intelligence_blocks(meeting_folder: Path) -> Dict[str, str]:
    """
    Read intelligence blocks from meeting folder.
    
    Looks for:
    - key_insights.md
    - relationship_notes.md  
    - action_items.md
    
    Returns:
        Dict of {block_name: content}
    """
    blocks = {}
    
    block_files = [
        "key_insights.md",
        "relationship_notes.md",
        "action_items.md"
    ]
    
    for block_file in block_files:
        block_path = meeting_folder / block_file
        if block_path.exists():
            try:
                with open(block_path, 'r') as f:
                    content = f.read().strip()
                    if content and content != "<!-- Placeholder -->":
                        blocks[block_file] = content
                        logging.info(f"Read {block_file} ({len(content)} chars)")
            except Exception as e:
                logging.warning(f"Could not read {block_file}: {e}")
    
    return blocks


def generate_relationship_delta(
    delta_path: Path,
    meeting_folder: Path,
    intelligence_blocks: Dict[str, str]
) -> None:
    """
    Generate NEW relationship delta document.
    
    Args:
        delta_path: Where to write delta file
        meeting_folder: Meeting folder path
        intelligence_blocks: Dict of intelligence block content
    """
    meeting_date = extract_meeting_date(meeting_folder)
    
    content = f"""# Relationship Delta - {meeting_date}

**Meeting:** {meeting_folder.name}
**Generated:** {datetime.utcnow().isoformat()}Z

## Key Insights

{intelligence_blocks.get('key_insights.md', '_No key insights recorded_')}

## Relationship Notes

{intelligence_blocks.get('relationship_notes.md', '_No relationship notes recorded_')}

## Action Items

{intelligence_blocks.get('action_items.md', '_No action items recorded_')}

---
_This delta was automatically generated from meeting intelligence blocks._
"""
    
    delta_path.parent.mkdir(parents=True, exist_ok=True)
    with open(delta_path, 'w') as f:
        f.write(content)


def regenerate_relationship_context(profile_path: Path, context_path: Path) -> None:
    """
    Regenerate relationship_context.md by synthesizing all deltas.
    
    Pattern: Read all relationship_delta_*.md files, synthesize into context.
    
    Args:
        profile_path: Path to profile directory
        context_path: Path to relationship_context.md
    """
    # Find all delta files
    delta_files = sorted(profile_path.glob("relationship_delta_*.md"))
    
    if not delta_files:
        logging.warning(f"No delta files found in {profile_path}")
        return
    
    # Synthesize content
    content = f"""# Relationship Context

**Profile:** {profile_path.name}
**Last Updated:** {datetime.utcnow().isoformat()}Z
**Total Deltas:** {len(delta_files)}

## Evolution

"""
    
    for delta_file in delta_files:
        delta_date = delta_file.stem.replace("relationship_delta_", "")
        content += f"\n### {delta_date}\n\n"
        
        try:
            with open(delta_file, 'r') as f:
                delta_content = f.read()
                # Extract just the key sections (skip header)
                lines = delta_content.split('\n')
                in_section = False
                for line in lines:
                    if line.startswith('## '):
                        in_section = True
                    if in_section and not line.startswith('**Meeting:') and not line.startswith('**Generated:'):
                        content += line + '\n'
        except Exception as e:
            logging.warning(f"Could not read {delta_file.name}: {e}")
            content += f"_Error reading delta: {e}_\n\n"
    
    # Write synthesized context
    with open(context_path, 'w') as f:
        f.write(content)
    
    logging.info(f"Synthesized {len(delta_files)} deltas into relationship_context.md")


def main(dry_run: bool = False) -> int:
    """
    Main watcher function.
    
    Args:
        dry_run: If True, report findings without changes
        
    Returns:
        0 on success, 1 on error
    """
    try:
        logging.info(f"{'[DRY-RUN] ' if dry_run else ''}Starting profile enrichment watcher")
        
        # Check if profiles database exists
        if not PROFILES_DB.exists():
            logging.error(f"Profiles database not found: {PROFILES_DB}")
            return 1
        
        # Find new meetings with transcripts
        new_meetings = find_new_meetings_with_transcripts()
        
        if not new_meetings:
            logging.info("No new meetings to enrich")
            return 0
        
        logging.info(f"Found {len(new_meetings)} meeting(s) to enrich")
        
        # Enrich each meeting
        success_count = 0
        for meeting_folder in new_meetings:
            if enrich_profile_post_meeting(meeting_folder, dry_run):
                success_count += 1
        
        logging.info(f"✓ Enriched {success_count}/{len(new_meetings)} profiles")
        return 0
        
    except Exception as e:
        logging.error(f"Fatal error in watcher: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Watch for new meeting transcripts and enrich stakeholder profiles"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be done without making changes"
    )
    
    args = parser.parse_args()
    exit(main(args.dry_run))
