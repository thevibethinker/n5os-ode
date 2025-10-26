#!/usr/bin/env python3
"""
Fix Meeting Storage Duplication Issue
Consolidates meetings from Careerspan/Meetings/ to N5/records/meetings/
Merges .processed.json registries and prevents future duplication.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
CAREERSPAN_MEETINGS = Path("/home/workspace/Careerspan/Meetings")
N5_MEETINGS = Path("/home/workspace/N5/records/meetings")
CAREERSPAN_REGISTRY = CAREERSPAN_MEETINGS / ".processed.json"
N5_REGISTRY = N5_MEETINGS / ".processed.json"
BACKUP_DIR = Path("/home/workspace/N5/backups")

def load_registry(path: Path) -> dict:
    """Load a .processed.json registry file."""
    if not path.exists():
        return {"last_poll": None, "processed_events": {}}
    
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load registry {path}: {e}")
        return {"last_poll": None, "processed_events": {}}

def backup_before_changes():
    """Backup both registries before making changes."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if CAREERSPAN_REGISTRY.exists():
        backup_path = BACKUP_DIR / f"careerspan_processed_{timestamp}.json"
        shutil.copy2(CAREERSPAN_REGISTRY, backup_path)
        logger.info(f"✓ Backed up Careerspan registry to {backup_path}")
    
    if N5_REGISTRY.exists():
        backup_path = BACKUP_DIR / f"n5_processed_{timestamp}.json"
        shutil.copy2(N5_REGISTRY, backup_path)
        logger.info(f"✓ Backed up N5 registry to {backup_path}")

def get_meeting_folders(base_path: Path) -> list:
    """Get list of meeting folders (exclude .processed.json and other files)."""
    if not base_path.exists():
        return []
    
    folders = []
    for item in base_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            folders.append(item)
    return sorted(folders)

def analyze_duplication():
    """Analyze the duplication situation."""
    logger.info("\n" + "="*60)
    logger.info("ANALYZING MEETING DUPLICATION")
    logger.info("="*60 + "\n")
    
    careerspan_folders = get_meeting_folders(CAREERSPAN_MEETINGS)
    n5_folders = get_meeting_folders(N5_MEETINGS)
    
    logger.info(f"Careerspan/Meetings: {len(careerspan_folders)} folders")
    logger.info(f"N5/records/meetings: {len(n5_folders)} folders")
    
    # Find duplicates
    careerspan_names = {f.name for f in careerspan_folders}
    n5_names = {f.name for f in n5_folders}
    
    duplicates = careerspan_names & n5_names
    careerspan_only = careerspan_names - n5_names
    n5_only = n5_names - careerspan_names
    
    logger.info(f"\nDuplicated meetings: {len(duplicates)}")
    logger.info(f"Careerspan-only meetings: {len(careerspan_only)}")
    logger.info(f"N5-only meetings: {len(n5_only)}")
    
    # Load registries
    careerspan_reg = load_registry(CAREERSPAN_REGISTRY)
    n5_reg = load_registry(N5_REGISTRY)
    
    logger.info(f"\nCareerspan registry: {len(careerspan_reg.get('processed_events', {}))} events")
    logger.info(f"N5 registry: {len(n5_reg.get('processed_events', {}))} events")
    
    return {
        "careerspan_folders": careerspan_folders,
        "n5_folders": n5_folders,
        "duplicates": duplicates,
        "careerspan_only": careerspan_only,
        "n5_only": n5_only,
        "careerspan_registry": careerspan_reg,
        "n5_registry": n5_reg
    }

def consolidate_meetings(analysis: dict, dry_run: bool = True):
    """Consolidate meetings to N5 location."""
    logger.info("\n" + "="*60)
    logger.info(f"CONSOLIDATING MEETINGS {'(DRY RUN)' if dry_run else ''}")
    logger.info("="*60 + "\n")
    
    moved = 0
    skipped = 0
    
    # Move Careerspan-only folders to N5
    for folder_name in analysis["careerspan_only"]:
        src = CAREERSPAN_MEETINGS / folder_name
        dst = N5_MEETINGS / folder_name
        
        if dry_run:
            logger.info(f"[DRY RUN] Would move: {src} → {dst}")
            moved += 1
        else:
            try:
                shutil.move(str(src), str(dst))
                logger.info(f"✓ Moved: {folder_name}")
                moved += 1
            except Exception as e:
                logger.error(f"✗ Failed to move {folder_name}: {e}")
    
    # For duplicates, verify N5 has the content, then remove from Careerspan
    for folder_name in analysis["duplicates"]:
        n5_path = N5_MEETINGS / folder_name
        cs_path = CAREERSPAN_MEETINGS / folder_name
        
        # Check if N5 has content
        n5_files = list(n5_path.glob("*.md"))
        cs_files = list(cs_path.glob("*.md"))
        
        if len(n5_files) >= len(cs_files):
            if dry_run:
                logger.info(f"[DRY RUN] Would remove duplicate: {cs_path}")
                skipped += 1
            else:
                try:
                    shutil.rmtree(cs_path)
                    logger.info(f"✓ Removed duplicate: {folder_name}")
                    skipped += 1
                except Exception as e:
                    logger.error(f"✗ Failed to remove {folder_name}: {e}")
        else:
            logger.warning(f"⚠ Skipping {folder_name}: N5 has fewer files ({len(n5_files)} vs {len(cs_files)})")
    
    logger.info(f"\nSummary: {moved} moved, {skipped} duplicates removed")
    return moved, skipped

def merge_registries(analysis: dict, dry_run: bool = True):
    """Merge the two .processed.json registries."""
    logger.info("\n" + "="*60)
    logger.info(f"MERGING REGISTRIES {'(DRY RUN)' if dry_run else ''}")
    logger.info("="*60 + "\n")
    
    cs_reg = analysis["careerspan_registry"]
    n5_reg = analysis["n5_registry"]
    
    # Merge processed_events
    merged_events = {}
    
    # Start with N5 events (authoritative source)
    if "processed_events" in n5_reg:
        merged_events.update(n5_reg["processed_events"])
    
    # Add Careerspan events that don't exist in N5
    if "processed_events" in cs_reg:
        for event_id, event_data in cs_reg["processed_events"].items():
            if event_id not in merged_events:
                merged_events[event_id] = event_data
                logger.info(f"+ Added from Careerspan: {event_id}")
    
    # Use latest last_poll
    last_polls = []
    if cs_reg.get("last_poll"):
        last_polls.append(datetime.fromisoformat(cs_reg["last_poll"]))
    if n5_reg.get("last_poll"):
        last_polls.append(datetime.fromisoformat(n5_reg["last_poll"]))
    
    last_poll = max(last_polls).isoformat() if last_polls else datetime.now().isoformat()
    
    merged_registry = {
        "last_poll": last_poll,
        "processed_events": merged_events
    }
    
    logger.info(f"\nMerged registry: {len(merged_events)} total events")
    
    if not dry_run:
        # Write merged registry to N5
        with open(N5_REGISTRY, 'w') as f:
            json.dump(merged_registry, f, indent=2)
        logger.info(f"✓ Wrote merged registry to {N5_REGISTRY}")
        
        # Remove Careerspan registry
        if CAREERSPAN_REGISTRY.exists():
            CAREERSPAN_REGISTRY.unlink()
            logger.info(f"✓ Removed Careerspan registry")
    else:
        logger.info(f"[DRY RUN] Would write merged registry to {N5_REGISTRY}")
    
    return len(merged_events)

def update_command_documentation():
    """Add explicit output path to meeting-process command."""
    logger.info("\n" + "="*60)
    logger.info("UPDATING COMMAND DOCUMENTATION")
    logger.info("="*60 + "\n")
    
    command_path = Path("/home/workspace/N5/commands/meeting-process.md")
    
    if not command_path.exists():
        logger.error(f"Command file not found: {command_path}")
        return False
    
    content = command_path.read_text()
    
    # Check if already has explicit output path
    if "N5/records/meetings/" in content and "meeting_folder/" in content:
        logger.info("✓ Command already specifies output path")
        return True
    
    # Add output path specification after "Output Format" section
    output_section = "## Output Format\n\n### File Structure\n```\nmeeting_folder/"
    new_output_section = """## Output Format

### Output Location
**All meetings MUST be stored in:** `N5/records/meetings/{meeting_id}/`

Example: `N5/records/meetings/2025-10-14_external-jane-smith/`

### File Structure
```
N5/records/meetings/{meeting_id}/"""
    
    updated_content = content.replace(output_section, new_output_section)
    
    if updated_content != content:
        command_path.write_text(updated_content)
        logger.info(f"✓ Updated command documentation with explicit output path")
        return True
    else:
        logger.warning("⚠ Could not find section to update")
        return False

def main(dry_run: bool = True):
    """Main execution function."""
    logger.info(f"\nStarting meeting duplication fix {'(DRY RUN)' if dry_run else '(LIVE RUN)'}")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # 1. Backup
        if not dry_run:
            backup_before_changes()
        
        # 2. Analyze
        analysis = analyze_duplication()
        
        # 3. Consolidate meetings
        moved, removed = consolidate_meetings(analysis, dry_run=dry_run)
        
        # 4. Merge registries
        events = merge_registries(analysis, dry_run=dry_run)
        
        # 5. Update documentation
        if not dry_run:
            update_command_documentation()
        
        logger.info("\n" + "="*60)
        logger.info("COMPLETION SUMMARY")
        logger.info("="*60)
        logger.info(f"Meetings moved: {moved}")
        logger.info(f"Duplicates removed: {removed}")
        logger.info(f"Registry events: {events}")
        logger.info(f"Mode: {'DRY RUN - no changes made' if dry_run else 'LIVE - changes applied'}")
        logger.info("="*60 + "\n")
        
        if dry_run:
            logger.info("ℹ️  This was a DRY RUN. Run with --live to apply changes.")
        else:
            logger.info("✅ Meeting consolidation complete!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during consolidation: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix meeting storage duplication")
    parser.add_argument("--live", action="store_true", help="Apply changes (default is dry-run)")
    args = parser.parse_args()
    
    exit(main(dry_run=not args.live))
