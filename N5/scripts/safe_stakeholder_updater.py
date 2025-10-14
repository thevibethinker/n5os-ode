#!/usr/bin/env python3
"""
Safe Stakeholder Profile Updater
Implements append-only updates with conflict detection, backups, and review workflow.
"""

# ======================================================================
# DEPRECATED - Use Knowledge/crm/profiles/ and crm_query.py instead
# This script is part of the legacy stakeholder system.
# Retained for historical reference only.
# ======================================================================


import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import difflib
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
CRM_PROFILES_DIR = WORKSPACE / "Knowledge/crm/individuals"
BACKUPS_DIR = WORKSPACE / "Knowledge/crm/individuals/.backups"
REVIEW_DIR = WORKSPACE / "Knowledge/crm/individuals/.pending_updates"

# Ensure directories exist
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
REVIEW_DIR.mkdir(parents=True, exist_ok=True)


class StakeholderUpdateConflict(Exception):
    """Raised when update would overwrite existing content"""
    pass


def _create_backup(profile_path: Path) -> Path:
    """Create timestamped backup of profile before any modifications."""
    if not profile_path.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{profile_path.stem}_{timestamp}.md"
    backup_path = BACKUPS_DIR / backup_name
    
    shutil.copy2(profile_path, backup_path)
    logger.info(f"Backup created: {backup_path}")
    
    return backup_path


def _compute_file_hash(content: str) -> str:
    """Compute SHA256 hash of file content for change detection."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]


def _parse_profile_sections(content: str) -> Dict[str, str]:
    """
    Parse profile into sections for safe merging.
    Returns dict mapping section headers to content.
    """
    sections = {}
    current_section = "frontmatter"
    current_content = []
    
    lines = content.split('\n')
    
    for line in lines:
        # Detect section headers (## Section Name)
        if line.startswith('## '):
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = line[3:].strip()
            current_content = [line]
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections


def _extract_interaction_entries(section_content: str) -> List[Dict]:
    """
    Parse Interaction History section into individual entries.
    Returns list of {date, heading, content} dicts.
    """
    entries = []
    current_entry = None
    
    lines = section_content.split('\n')
    
    for line in lines:
        # Detect entry headers (### YYYY-MM-DD: Title)
        if line.startswith('### '):
            if current_entry:
                entries.append(current_entry)
            
            # Parse date from header
            heading = line[4:].strip()
            date_str = heading.split(':')[0] if ':' in heading else ''
            
            current_entry = {
                'date': date_str,
                'heading': heading,
                'content': [line]
            }
        elif current_entry:
            current_entry['content'].append(line)
    
    if current_entry:
        entries.append(current_entry)
    
    return entries


def append_interaction(
    profile_path: Path,
    interaction_date: str,
    interaction_title: str,
    summary: str,
    key_points: List[str],
    outcomes: List[str],
    linked_artifact: Optional[str] = None,
    dry_run: bool = False
) -> Tuple[Path, str]:
    """
    Safely append new interaction to profile's Interaction History.
    
    Returns: (updated_profile_path, diff_summary)
    """
    
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")
    
    # Create backup
    if not dry_run:
        _create_backup(profile_path)
    
    # Read current content
    original_content = profile_path.read_text()
    sections = _parse_profile_sections(original_content)
    
    # Check if Interaction History exists
    if "Interaction History" not in sections:
        raise StakeholderUpdateConflict(
            "Profile missing 'Interaction History' section - manual review required"
        )
    
    # Parse existing interactions
    existing_interactions = _extract_interaction_entries(sections["Interaction History"])
    
    # Check for duplicate date (warn but allow)
    duplicate_dates = [e for e in existing_interactions if e['date'] == interaction_date]
    if duplicate_dates:
        logger.warning(f"Interaction already exists for {interaction_date} - adding anyway")
    
    # Build new interaction entry
    artifact_line = f"\n**Linked artifact:** `file '{linked_artifact}'`" if linked_artifact else ""
    
    key_points_md = "\n".join([f"- {point}" for point in key_points])
    outcomes_md = "\n".join([f"- {outcome}" for outcome in outcomes])
    
    new_entry = f"""
### {interaction_date}: {interaction_title}
**Type:** Meeting  
**Summary:** {summary}

**Key Points:**
{key_points_md}

**Outcomes:**
{outcomes_md}{artifact_line}

---
"""
    
    # Find insertion point (before "## Quick Reference" or at end of section)
    interaction_section = sections["Interaction History"]
    
    if "## Quick Reference" in original_content:
        # Insert before Quick Reference
        parts = original_content.split("## Quick Reference")
        updated_content = parts[0].rstrip() + "\n" + new_entry + "\n## Quick Reference" + parts[1]
    else:
        # Append to end of Interaction History section
        # Find where this section ends (next ## header or end of file)
        section_end_marker = None
        for section_name in sections:
            if section_name != "Interaction History" and sections[section_name].startswith("## "):
                section_end_marker = f"## {section_name}"
                break
        
        if section_end_marker:
            parts = original_content.split(section_end_marker)
            updated_content = parts[0].rstrip() + "\n" + new_entry + "\n" + section_end_marker + parts[1]
        else:
            updated_content = original_content.rstrip() + "\n" + new_entry
    
    # Update metadata in frontmatter
    today = datetime.now().strftime("%Y-%m-%d")
    updated_content = _update_frontmatter_date(updated_content, today)
    
    # Generate diff
    diff = _generate_diff(original_content, updated_content, profile_path.name)
    
    if dry_run:
        logger.info("[DRY RUN] Would append interaction:")
        logger.info(new_entry)
        return profile_path, diff
    
    # Write updated content
    profile_path.write_text(updated_content)
    logger.info(f"Updated profile: {profile_path}")
    
    return profile_path, diff


def _update_frontmatter_date(content: str, date: str) -> str:
    """Update last_updated date in YAML frontmatter."""
    import re
    
    # Update last_updated
    content = re.sub(
        r'last_updated: "[^"]*"',
        f'last_updated: "{date}"',
        content
    )
    
    # Update Last Updated in body
    content = re.sub(
        r'\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}',
        f'**Last Updated:** {date}',
        content
    )
    
    return content


def add_tag_safely(
    profile_path: Path,
    tag: str,
    tag_category: str,
    verification_source: str,
    dry_run: bool = False
) -> Tuple[Path, str]:
    """
    Add tag to verified tags section without removing existing tags.
    
    Args:
        tag: Tag to add (e.g., "#stakeholder:advisor")
        tag_category: Category for organization (e.g., "Verified")
        verification_source: How this tag was verified
    """
    
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")
    
    # Create backup
    if not dry_run:
        _create_backup(profile_path)
    
    # Read current content
    original_content = profile_path.read_text()
    
    # Check if tag already exists
    if tag in original_content:
        logger.info(f"Tag already exists: {tag}")
        return profile_path, "No changes (tag already present)"
    
    # Find the verified tags section
    sections = _parse_profile_sections(original_content)
    
    if "Tags" not in sections:
        raise StakeholderUpdateConflict(
            "Profile missing 'Tags' section - manual review required"
        )
    
    # Insert tag in the appropriate subsection
    today = datetime.now().strftime("%Y-%m-%d")
    tag_line = f"- `{tag}` — {verification_source}\n"
    
    # Find insertion point (after "### Verified" header)
    verified_marker = "### Verified (Last reviewed:"
    
    if verified_marker in original_content:
        # Update last reviewed date
        import re
        updated_content = re.sub(
            r'### Verified \(Last reviewed: \d{4}-\d{2}-\d{2}\)',
            f'### Verified (Last reviewed: {today})',
            original_content
        )
        
        # Find first tag line after marker
        lines = updated_content.split('\n')
        insert_idx = None
        
        for idx, line in enumerate(lines):
            if verified_marker in line:
                # Find first '- `' after this line
                for j in range(idx + 1, len(lines)):
                    if lines[j].strip().startswith('- `'):
                        # Insert before the next subsection or blank line
                        for k in range(j, len(lines)):
                            if lines[k].strip() == '' or lines[k].startswith('###'):
                                insert_idx = k
                                break
                        if insert_idx:
                            break
                break
        
        if insert_idx:
            lines.insert(insert_idx, tag_line.rstrip())
            updated_content = '\n'.join(lines)
        else:
            raise StakeholderUpdateConflict(
                "Could not find safe insertion point for tag"
            )
    else:
        raise StakeholderUpdateConflict(
            "Profile format unexpected - manual review required"
        )
    
    # Generate diff
    diff = _generate_diff(original_content, updated_content, profile_path.name)
    
    if dry_run:
        logger.info(f"[DRY RUN] Would add tag: {tag}")
        return profile_path, diff
    
    # Write updated content
    profile_path.write_text(updated_content)
    logger.info(f"Added tag to profile: {profile_path}")
    
    return profile_path, diff


def _generate_diff(original: str, updated: str, filename: str) -> str:
    """Generate unified diff for review."""
    diff_lines = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        updated.splitlines(keepends=True),
        fromfile=f"{filename} (original)",
        tofile=f"{filename} (updated)",
        lineterm=''
    ))
    
    return ''.join(diff_lines)


def enrich_section_safely(
    profile_path: Path,
    section_name: str,
    new_content: str,
    merge_strategy: str = "append",
    dry_run: bool = False
) -> Tuple[Path, str]:
    """
    Add content to a section without overwriting existing content.
    
    Args:
        section_name: Name of section (e.g., "Product & Mission")
        new_content: Content to add
        merge_strategy: "append" (add to end) | "prepend" (add to start) | "conflict" (raise error if exists)
    
    Raises:
        StakeholderUpdateConflict: If merge_strategy="conflict" and section has content
    """
    
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")
    
    # Create backup
    if not dry_run:
        _create_backup(profile_path)
    
    # Read current content
    original_content = profile_path.read_text()
    sections = _parse_profile_sections(original_content)
    
    if section_name not in sections:
        raise StakeholderUpdateConflict(
            f"Section '{section_name}' not found in profile"
        )
    
    current_section = sections[section_name]
    
    # Check if section has substantial content (more than just header)
    substantial_content = len(current_section.split('\n')) > 3
    
    if substantial_content and merge_strategy == "conflict":
        raise StakeholderUpdateConflict(
            f"Section '{section_name}' already has content. Manual merge required."
        )
    
    # Merge content
    if merge_strategy == "append":
        merged_section = current_section.rstrip() + "\n\n" + new_content
    elif merge_strategy == "prepend":
        section_lines = current_section.split('\n')
        # Keep header, prepend content after
        header = section_lines[0]
        rest = '\n'.join(section_lines[1:])
        merged_section = f"{header}\n\n{new_content}\n\n{rest}"
    else:
        raise ValueError(f"Unknown merge strategy: {merge_strategy}")
    
    # Replace section in full content
    updated_content = original_content.replace(current_section, merged_section)
    
    # Update metadata
    today = datetime.now().strftime("%Y-%m-%d")
    updated_content = _update_frontmatter_date(updated_content, today)
    
    # Generate diff
    diff = _generate_diff(original_content, updated_content, profile_path.name)
    
    if dry_run:
        logger.info(f"[DRY RUN] Would enrich section '{section_name}'")
        return profile_path, diff
    
    # Write updated content
    profile_path.write_text(updated_content)
    logger.info(f"Enriched section '{section_name}' in profile: {profile_path}")
    
    return profile_path, diff


def preview_update(
    profile_path: Path,
    update_operations: List[Dict],
    output_path: Optional[Path] = None
) -> Path:
    """
    Generate preview of proposed updates without applying them.
    
    Args:
        profile_path: Path to profile
        update_operations: List of operations, each with:
            - type: "append_interaction" | "add_tag" | "enrich_section"
            - params: dict of parameters for that operation
    
    Returns:
        Path to preview file with diff
    """
    
    preview_lines = [
        f"# Update Preview: {profile_path.name}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Profile:** `{profile_path}`",
        "",
        "## Proposed Changes",
        ""
    ]
    
    for idx, op in enumerate(update_operations, 1):
        op_type = op['type']
        params = op['params']
        
        preview_lines.append(f"### Change {idx}: {op_type}")
        preview_lines.append(f"**Parameters:** {json.dumps(params, indent=2)}")
        preview_lines.append("")
        
        # Execute dry-run to get diff
        try:
            if op_type == "append_interaction":
                _, diff = append_interaction(profile_path, dry_run=True, **params)
            elif op_type == "add_tag":
                _, diff = add_tag_safely(profile_path, dry_run=True, **params)
            elif op_type == "enrich_section":
                _, diff = enrich_section_safely(profile_path, dry_run=True, **params)
            else:
                diff = f"Unknown operation type: {op_type}"
            
            preview_lines.append("**Diff:**")
            preview_lines.append("```diff")
            preview_lines.append(diff)
            preview_lines.append("```")
            preview_lines.append("")
        
        except Exception as e:
            preview_lines.append(f"**Error:** {str(e)}")
            preview_lines.append("")
    
    # Write preview
    if output_path is None:
        output_path = REVIEW_DIR / f"{profile_path.stem}_update_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    output_path.write_text('\n'.join(preview_lines))
    logger.info(f"Update preview generated: {output_path}")
    
    return output_path


if __name__ == "__main__":
    # Test with sample operations
    logger.info("Safe Stakeholder Updater initialized")
    logger.info(f"Backups directory: {BACKUPS_DIR}")
    logger.info(f"Review directory: {REVIEW_DIR}")
