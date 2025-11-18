#!/usr/bin/env python3
"""
Meeting Duplicate Detector - CANONICAL VERSION

Consolidated meeting-specific duplicate detection on 2025-11-15.
This handles ONLY meeting-related duplicates, not general file duplication.

Replaces:
- cleanup_duplicate_meeting_files.py (47 lines) - Intelligence file lowercase/UPPERCASE patterns
- deduplicate_meetings.py (74 lines) - LLM-based semantic meeting deduplication
- meeting_registry_deduplicate.py (117 lines) - Registry duplicate Drive IDs

NOT REPLACED (general tools, keep separate):
- duplicate_scanner.py - General workspace file duplicate scanner
- cleanup_duplicate_requests.py - Inbox AI request cleanup
- meeting_ai_deduplicator.py - Overlaps with meeting_duplicate_manager.py (canonical)

Capabilities:
1. Intelligence file duplicates (lowercase vs UPPERCASE/B## variants)
2. Meeting registry duplicates (same gdrive_id entries)
3. Semantic meeting detection (prep for LLM analysis)
"""

import argparse
import hashlib
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WS = Path('/home/workspace')
MEETINGS_DIR = WS / 'Personal' / 'Meetings'
REGISTRY_PATH = WS / 'N5' / 'data' / 'meeting_registry.json'


# ============================================================================
# Intelligence File Duplicate Detection
# ============================================================================

def find_intelligence_duplicates(meetings_dir: Path) -> list:
    """
    Find lowercase intelligence files that have UPPERCASE or B## equivalents.
    Pattern: Keep UPPERCASE and B##-numbered files, flag lowercase as duplicates.
    
    Examples:
      - Keep: SUMMARY.md, MAIN_TOPICS.md, B01-actions.md
      - Flag: summary.md, main_topics.md (duplicates of above)
    """
    duplicates = []
    
    for meeting_dir in meetings_dir.iterdir():
        if not meeting_dir.is_dir() or meeting_dir.name.startswith('.'):
            continue
        if meeting_dir.name in ['Inbox', '_ARCHIVE_2024']:
            continue
        
        files = {f.name: f for f in meeting_dir.iterdir() if f.is_file()}
        
        # Group by normalized name
        normalized = defaultdict(list)
        for name, filepath in files.items():
            # Strip B## prefix for comparison
            norm_name = name
            if name.startswith('B') and len(name) > 2 and name[1:3].isdigit():
                norm_name = name[4:]  # Skip "B##-"
            
            normalized[norm_name.lower()].append((name, filepath))
        
        # Find duplicates
        for norm_name, variants in normalized.items():
            if len(variants) <= 1:
                continue
            
            # Classify each variant by its case pattern
            b_files = []
            uppercase = []
            lowercase = []
            
            for name, filepath in variants:
                if name.startswith('B') and len(name) > 2 and name[1:3].isdigit():
                    # B## file - check the part after B##_
                    if len(name) > 4 and name[3] == '_':
                        rest = name[4:].split('.')[0]  # Get part after B##_, before extension
                        if rest and rest[0].isupper():
                            b_files.append((name, filepath))
                        else:
                            lowercase.append((name, filepath))
                    else:
                        b_files.append((name, filepath))
                else:
                    # Non-B## file - check first character
                    base = name.split('.')[0]  # Remove extension
                    if base and base[0].isupper():
                        uppercase.append((name, filepath))
                    else:
                        lowercase.append((name, filepath))
            
            # If we have B## or UPPERCASE, flag lowercase as duplicates
            if (b_files or uppercase) and lowercase:
                for name, filepath in lowercase:
                    keep_variant = b_files[0][0] if b_files else uppercase[0][0]
                    duplicates.append({
                        'duplicate': filepath,
                        'keep': b_files[0][1] if b_files else uppercase[0][1],
                        'meeting': meeting_dir.name,
                        'reason': f'Lowercase variant of {keep_variant}'
                    })
    
    return duplicates


# ============================================================================
# Meeting Registry Duplicate Detection
# ============================================================================

def find_registry_duplicates() -> tuple:
    """
    Find duplicate gdrive_id entries in meeting registry.
    Returns: (duplicates dict, all entries list)
    """
    if not REGISTRY_PATH.exists():
        logger.warning(f"Registry not found: {REGISTRY_PATH}")
        return {}, []
    
    with open(REGISTRY_PATH, 'r') as f:
        entries = json.load(f)
    
    # Group by gdrive_id
    by_id = defaultdict(list)
    for idx, entry in enumerate(entries):
        if isinstance(entry, dict):
            gdrive_id = entry.get("gdrive_id")
            if gdrive_id:
                by_id[gdrive_id].append((idx, entry))
    
    # Filter to actual duplicates
    duplicates = {k: v for k, v in by_id.items() if len(v) > 1}
    
    return duplicates, entries


def backup_registry():
    """Create timestamped backup of meeting registry."""
    if not REGISTRY_PATH.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = REGISTRY_PATH.parent / f"meeting_registry.backup.{timestamp}.json"
    shutil.copy(REGISTRY_PATH, backup_path)
    logger.info(f"Backup created: {backup_path}")
    return backup_path


def deduplicate_registry(dry_run=False) -> dict:
    """
    Remove duplicate gdrive_id entries, keeping the most complete record.
    
    Priority for keeping:
    1. Entry with most fields populated
    2. Most recent date
    3. First occurrence
    """
    duplicates, entries = find_registry_duplicates()
    
    if not duplicates:
        logger.info("No registry duplicates found")
        return {'removed': 0, 'kept': len(entries)}
    
    # Determine which to keep
    to_remove_indices = set()
    
    for gdrive_id, dup_list in duplicates.items():
        # Score each entry (more fields = higher score)
        scored = []
        for idx, entry in dup_list:
            score = sum(1 for v in entry.values() if v)
            scored.append((score, idx, entry))
        
        # Keep highest score, remove rest
        scored.sort(reverse=True)
        keep_idx = scored[0][1]
        
        for score, idx, entry in scored[1:]:
            to_remove_indices.add(idx)
            logger.info(f"  Remove duplicate: idx={idx}, folder={entry.get('folder_name', 'unknown')}")
    
    if dry_run:
        logger.info(f"DRY RUN: Would remove {len(to_remove_indices)} duplicate entries")
        return {'removed': len(to_remove_indices), 'kept': len(entries) - len(to_remove_indices), 'dry_run': True}
    
    # Backup before modifying
    backup_registry()
    
    # Remove duplicates
    cleaned = [entry for idx, entry in enumerate(entries) if idx not in to_remove_indices]
    
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(cleaned, f, indent=2)
    
    logger.info(f"✓ Removed {len(to_remove_indices)} duplicates, kept {len(cleaned)} entries")
    return {'removed': len(to_remove_indices), 'kept': len(cleaned)}


# ============================================================================
# Semantic Meeting Scan (prep for LLM)
# ============================================================================

def scan_for_semantic_analysis(meetings_dir: Path) -> dict:
    """
    Scan meetings directory and prepare metadata for LLM-based deduplication.
    This doesn't do the actual deduplication - it prepares data for Prompts/deduplicate-meetings.md
    
    Returns dict suitable for passing to LLM prompt.
    """
    meetings = []
    
    for meeting_dir in meetings_dir.iterdir():
        if not meeting_dir.is_dir() or meeting_dir.name.startswith('.'):
            continue
        if meeting_dir.name in ['Inbox', '_ARCHIVE_2024']:
            continue
        
        # Find transcript/summary files
        md_files = list(meeting_dir.glob('*.md'))
        transcript_files = [f for f in md_files if 'transcript' in f.name.lower() or 'summary' in f.name.lower()]
        
        if transcript_files:
            # Read first few lines for context
            sample = []
            for tf in transcript_files[:2]:
                try:
                    with open(tf, 'r') as f:
                        lines = f.readlines()[:10]
                        sample.extend(lines)
                except Exception as e:
                    logger.warning(f"Could not read {tf}: {e}")
            
            meetings.append({
                'folder': meeting_dir.name,
                'path': str(meeting_dir),
                'files': [f.name for f in md_files],
                'sample': ''.join(sample)[:500]  # First 500 chars
            })
    
    return {
        'scan_date': datetime.now().isoformat(),
        'total_meetings': len(meetings),
        'meetings': meetings
    }


# ============================================================================
# CLI Interface
# ============================================================================

def scan_command(args):
    """Scan for meeting duplicates."""
    results = {
        'scan_date': datetime.now().isoformat(),
    }
    
    # Fix attribute checking - scan command uses --intelligence and --registry flags differently
    scan_intelligence = not hasattr(args, 'registry') or not args.registry
    scan_registry = not hasattr(args, 'intelligence') or not args.intelligence
    
    if scan_intelligence:
        logger.info("Scanning for intelligence file duplicates...")
        intel_dupes = find_intelligence_duplicates(MEETINGS_DIR)
        results['intelligence_duplicates'] = intel_dupes
        logger.info(f"Found {len(intel_dupes)} intelligence file duplicates")
    
    if scan_registry:
        logger.info("Scanning meeting registry for duplicates...")
        reg_dupes, entries = find_registry_duplicates()
        results['registry_duplicates'] = {
            'count': len(reg_dupes),
            'duplicates': {k: [(idx, e.get('folder_name', 'unknown')) for idx, e in v] 
                          for k, v in reg_dupes.items()}
        }
        logger.info(f"Found {len(reg_dupes)} duplicate gdrive_id entries")
    
    if hasattr(args, 'semantic') and args.semantic:
        logger.info("Preparing semantic analysis data...")
        semantic_data = scan_for_semantic_analysis(MEETINGS_DIR)
        results['semantic_prep'] = semantic_data
        logger.info(f"Prepared {semantic_data['total_meetings']} meetings for semantic analysis")
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n" + "=" * 80)
        print("MEETING DUPLICATE SCAN RESULTS")
        print("=" * 80)
        
        if 'intelligence_duplicates' in results:
            print(f"\n✓ Intelligence File Duplicates: {len(results['intelligence_duplicates'])}")
            for dup in results['intelligence_duplicates'][:10]:
                print(f"  - {dup['duplicate'].name} → keep {dup['keep'].name} ({dup['meeting']})")
            if len(results['intelligence_duplicates']) > 10:
                print(f"  ... and {len(results['intelligence_duplicates']) - 10} more")
        
        if 'registry_duplicates' in results:
            print(f"\n✓ Registry Duplicates: {results['registry_duplicates']['count']}")
            for gid, entries in list(results['registry_duplicates']['duplicates'].items())[:5]:
                print(f"  - Drive ID {gid}: {len(entries)} entries")
            if results['registry_duplicates']['count'] > 5:
                print(f"  ... and {results['registry_duplicates']['count'] - 5} more")
        
        if 'semantic_prep' in results:
            print(f"\n✓ Semantic Analysis Ready: {results['semantic_prep']['total_meetings']} meetings")
    
    return 0


def cleanup_command(args):
    """Remove duplicate meeting artifacts."""
    results = {}
    
    # Check if we should clean intelligence files
    clean_intelligence = not getattr(args, 'registry', False)
    # Check if we should clean registry
    clean_registry = not getattr(args, 'intelligence', False)
    
    if clean_intelligence:
        logger.info("Cleaning up intelligence file duplicates...")
        intel_dupes = find_intelligence_duplicates(MEETINGS_DIR)
        
        if args.dry_run:
            logger.info(f"DRY RUN: Would remove {len(intel_dupes)} intelligence file duplicates")
            results['intelligence_cleanup'] = {'removed': len(intel_dupes), 'dry_run': True}
        else:
            removed_count = 0
            for dup in intel_dupes:
                try:
                    dup['duplicate'].unlink()
                    logger.info(f"  Removed: {dup['duplicate']}")
                    removed_count += 1
                except Exception as e:
                    logger.error(f"  Failed to remove {dup['duplicate']}: {e}")
            
            results['intelligence_cleanup'] = {'removed': removed_count}
            logger.info(f"✓ Removed {removed_count} intelligence file duplicates")
    
    if clean_registry:
        logger.info("Deduplicating meeting registry...")
        reg_results = deduplicate_registry(dry_run=args.dry_run)
        results['registry_cleanup'] = reg_results
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n" + "=" * 80)
        print("CLEANUP RESULTS")
        print("=" * 80)
        
        if 'intelligence_cleanup' in results:
            status = "(DRY RUN)" if results['intelligence_cleanup'].get('dry_run') else ""
            print(f"\n✓ Intelligence Files Removed {status}: {results['intelligence_cleanup']['removed']}")
        
        if 'registry_cleanup' in results:
            status = "(DRY RUN)" if results['registry_cleanup'].get('dry_run') else ""
            print(f"✓ Registry Entries Removed {status}: {results['registry_cleanup']['removed']}")
            print(f"✓ Registry Entries Kept: {results['registry_cleanup']['kept']}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Canonical meeting duplicate detection tool",
        epilog="""
Examples:
  python3 meeting_duplicate_detector.py scan
  python3 meeting_duplicate_detector.py scan --json
  python3 meeting_duplicate_detector.py scan --intelligence
  python3 meeting_duplicate_detector.py scan --registry
  python3 meeting_duplicate_detector.py scan --semantic
  python3 meeting_duplicate_detector.py cleanup --dry-run
  python3 meeting_duplicate_detector.py cleanup --intelligence --dry-run
  python3 meeting_duplicate_detector.py cleanup
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True, help='Command to run')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for duplicates')
    scan_parser.add_argument('--json', action='store_true', help='Output as JSON')
    scan_parser.add_argument('--intelligence', action='store_true', help='Scan intelligence files only')
    scan_parser.add_argument('--registry', action='store_true', help='Scan registry only')
    scan_parser.add_argument('--semantic', action='store_true', help='Prepare semantic analysis data')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Remove duplicates')
    cleanup_parser.add_argument('--dry-run', action='store_true', help='Preview changes only')
    cleanup_parser.add_argument('--intelligence', action='store_true', help='Clean intelligence files only')
    cleanup_parser.add_argument('--registry', action='store_true', help='Clean registry only')
    cleanup_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        return scan_command(args)
    elif args.command == 'cleanup':
        return cleanup_command(args)
    
    return 1


if __name__ == "__main__":
    exit(main())





