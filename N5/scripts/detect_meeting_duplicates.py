#!/usr/bin/env python3
"""
Meeting Duplicate Detection - CANONICAL VERSION

Consolidated from 5 scripts on 2025-11-15.
This is the single authoritative tool for detecting duplicate meeting artifacts.

Replaces:
- cleanup_duplicate_meeting_files.py (47 lines) - Intelligence file patterns
- duplicate_scanner.py (325 lines) - Base scanner logic
- meeting_registry_deduplicate.py (117 lines) - Registry deduplication
- deduplicate_meetings.py (74 lines) - Incomplete LLM-based scanner
- cleanup_duplicate_requests.py (63 lines) - Request queue cleanup

NOT REPLACED:
- meeting_ai_deduplicator.py - Archived (overlaps with meeting_duplicate_manager.py)
- meeting_duplicate_manager.py - CANONICAL for semantic meeting duplicates (different scope)

Scope: Detects duplicate meeting FOLDERS/FILES/RECORDS (not duplicate meetings themselves)

Features:
- Filesystem scan for duplicate folders
- Exact duplicates (same hash)
- Similar filenames (case variants, version suffixes)
- Intelligence file duplicates (lowercase vs UPPERCASE/B## versions)
- Registry duplicate detection
- Vestigial files (copy, draft, backup patterns)
- Tiny/empty files
- Actionable report with recommendations

Usage:
  python3 detect_meeting_duplicates.py scan                     # Report only
  python3 detect_meeting_duplicates.py scan --json              # JSON output
  python3 detect_meeting_duplicates.py scan --intelligence      # Intelligence file focus
  python3 detect_meeting_duplicates.py scan --registry          # Registry focus
  python3 detect_meeting_duplicates.py cleanup --dry-run        # Preview cleanup
  python3 detect_meeting_duplicates.py cleanup                  # Execute cleanup

Created: 2025-11-15 (Worker 02, Phase B consolidation)
"""

import argparse
import hashlib
import json
import logging
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Paths
WS = Path('/home/workspace')
MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")
REGISTRY_PATH = Path("/home/workspace/N5/data/meeting_gdrive_registry.jsonl")
BACKUP_DIR = Path("/home/workspace/N5/data/backups")

# Protected paths - never suggest deleting these
PROTECTED_PATHS = [
    'N5/', 'Knowledge/', 'Lists/', 'Documents/', 'Careerspan/', 'Personal/',
    'Projects/', 'Records/', '.git/'
]

# Intelligence file patterns (from cleanup_duplicate_meeting_files.py)
INTELLIGENCE_FILE_PATTERNS = [
    "action_items.md",
    "key_insights.md",
    "metadata.md",
    "relationship_intel.md",
    "strategic_analysis.md",
    "talking_points.md"
]

# Vestigial patterns (from duplicate_scanner.py)
VESTIGIAL_PATTERNS = [
    r'copy( of)?',
    r'final(_final)?',
    r'draft',
    r'backup',
    r'old',
    r'temp',
    r'untitled',
    r'\\(\\d+\\)',  # (1), (2), etc
    r'_v\\d+',    # _v1, _v2
    r'#\\d+',     # #2, #3
]


# ============================================================================
# Core Detection Functions
# ============================================================================

def is_protected(filepath: Path) -> bool:
    """Check if file is in protected path"""
    try:
        rel = filepath.relative_to(WS)
        return any(str(rel).startswith(p) for p in PROTECTED_PATHS)
    except ValueError:
        return True


def compute_hash(filepath: Path) -> str:
    """Compute MD5 hash of file"""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.warning(f"Cannot hash {filepath}: {e}")
        return None


def find_exact_duplicates(root: Path) -> dict:
    """Find files with identical content (from duplicate_scanner.py)"""
    logger.info("Scanning for exact duplicates (by hash)...")
    hash_map = defaultdict(list)
    
    for filepath in root.rglob('*'):
        if not filepath.is_file():
            continue
        if filepath.name.startswith('.'):
            continue
        if is_protected(filepath):
            continue
            
        file_hash = compute_hash(filepath)
        if file_hash:
            hash_map[file_hash].append(filepath)
    
    # Filter to only duplicates
    duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
    logger.info(f"Found {len(duplicates)} sets of exact duplicates")
    return duplicates


def find_similar_names(root: Path) -> list:
    """Find files with suspiciously similar names (from duplicate_scanner.py)"""
    logger.info("Scanning for similar filenames...")
    files = [f for f in root.rglob('*') if f.is_file() and not f.name.startswith('.')]
    
    similar_groups = []
    seen = set()
    
    for f1 in files:
        if f1 in seen or is_protected(f1):
            continue
            
        # Normalize name for comparison
        norm1 = re.sub(r'[_\-\s]+', '', f1.stem.lower())
        norm1 = re.sub(r'(copy|final|draft|v\d+|\(\d+\))', '', norm1)
        
        group = [f1]
        for f2 in files:
            if f2 == f1 or f2 in seen or is_protected(f2):
                continue
                
            norm2 = re.sub(r'[_\-\s]+', '', f2.stem.lower())
            norm2 = re.sub(r'(copy|final|draft|v\d+|\(\d+\))', '', norm2)
            
            # Same normalized name + same extension = likely duplicates
            if norm1 == norm2 and f1.suffix == f2.suffix:
                group.append(f2)
                seen.add(f2)
        
        if len(group) > 1:
            similar_groups.append(group)
            seen.add(f1)
    
    logger.info(f"Found {len(similar_groups)} groups of similar names")
    return similar_groups


def find_intelligence_file_duplicates() -> list:
    """Find duplicate intelligence files (lowercase vs UPPERCASE/B##)
    
    From cleanup_duplicate_meeting_files.py
    Keep UPPERCASE or B## versions, flag lowercase duplicates
    """
    logger.info("Scanning for intelligence file duplicates...")
    duplicates = []
    
    if not MEETINGS_DIR.exists():
        logger.warning(f"Meetings directory not found: {MEETINGS_DIR}")
        return duplicates
    
    for meeting_dir in MEETINGS_DIR.iterdir():
        if not meeting_dir.is_dir():
            continue
        if meeting_dir.name.startswith('.'):
            continue
        if meeting_dir.name in ['Inbox', '_ARCHIVE_2024', '.EXPUNGED']:
            continue
        
        for pattern in INTELLIGENCE_FILE_PATTERNS:
            lowercase_file = meeting_dir / pattern
            if not lowercase_file.exists():
                continue
            
            # Check if UPPERCASE or B## equivalent exists
            uppercase = meeting_dir / pattern.upper()
            
            # Generate B## format (e.g., action_items.md -> BAC_ACTION_ITEMS.md)
            if '_' in pattern:
                prefix = pattern.split('_')[0][:2].upper()
                stem = pattern.split('.')[0].upper()
                b_format = meeting_dir / f"B{prefix}_{stem}.md"
            else:
                b_format = None
            
            # If uppercase or B## version exists, lowercase is a duplicate
            if uppercase.exists() or (b_format and b_format.exists()):
                duplicates.append({
                    'lowercase': lowercase_file,
                    'canonical': uppercase if uppercase.exists() else b_format,
                    'meeting': meeting_dir.name
                })
    
    logger.info(f"Found {len(duplicates)} intelligence file duplicates")
    return duplicates


def find_registry_duplicates() -> dict:
    """Find duplicate entries in meeting registry
    
    From meeting_registry_deduplicate.py
    """
    logger.info("Scanning for registry duplicates...")
    
    if not REGISTRY_PATH.exists():
        logger.warning(f"Registry not found: {REGISTRY_PATH}")
        return {}
    
    by_id = defaultdict(list)
    entries = []
    
    try:
        with open(REGISTRY_PATH) as f:
            for idx, line in enumerate(f):
                entry = json.loads(line.strip())
                entries.append((idx, entry))
                gdrive_id = entry.get("gdrive_id")
                if gdrive_id:
                    by_id[gdrive_id].append((idx, entry))
    except Exception as e:
        logger.error(f"Error reading registry: {e}")
        return {}
    
    duplicates = {k: v for k, v in by_id.items() if len(v) > 1}
    logger.info(f"Found {len(duplicates)} duplicate Drive IDs in registry")
    
    return {
        'duplicates': duplicates,
        'all_entries': entries,
        'total_entries': len(entries),
        'duplicate_count': sum(len(v) - 1 for v in duplicates.values())
    }


def find_vestigial_files(root: Path) -> list:
    """Find files with vestigial naming patterns (from duplicate_scanner.py)"""
    logger.info("Scanning for vestigial files...")
    vestigial = []
    
    for filepath in root.rglob('*'):
        if not filepath.is_file() or filepath.name.startswith('.'):
            continue
        if is_protected(filepath):
            continue
            
        name_lower = filepath.name.lower()
        for pattern in VESTIGIAL_PATTERNS:
            if re.search(pattern, name_lower):
                vestigial.append({
                    'path': filepath,
                    'pattern': pattern,
                    'size': filepath.stat().st_size,
                    'modified': datetime.fromtimestamp(filepath.stat().st_mtime)
                })
                break
    
    logger.info(f"Found {len(vestigial)} vestigial files")
    return vestigial


def find_tiny_files(root: Path, size_threshold: int = 100) -> list:
    """Find suspiciously tiny or empty files (from duplicate_scanner.py)"""
    logger.info("Scanning for tiny/empty files...")
    tiny = []
    
    for filepath in root.rglob('*'):
        if not filepath.is_file():
            continue
        if is_protected(filepath):
            continue
            
        size = filepath.stat().st_size
        if size < size_threshold:
            tiny.append({
                'path': filepath,
                'size': size,
                'modified': datetime.fromtimestamp(filepath.stat().st_mtime)
            })
    
    logger.info(f"Found {len(tiny)} tiny files (< {size_threshold} bytes)")
    return tiny


# ============================================================================
# Reporting Functions
# ============================================================================

def generate_report(duplicates, similar, intelligence_dupes, registry_dupes, vestigial, tiny) -> str:
    """Generate human-readable report"""
    report = []
    report.append("# Meeting Duplicate Detection Report")
    report.append(f"\nGenerated: {datetime.utcnow().isoformat()}Z")
    report.append(f"Tool: detect_meeting_duplicates.py (CANONICAL)")
    report.append("\n---\n")
    
    # Intelligence file duplicates (meeting-specific)
    report.append(f"## Intelligence File Duplicates ({len(intelligence_dupes)})\\n")
    report.append("Lowercase files that have UPPERCASE or B## equivalents:\\n")
    if intelligence_dupes:
        for dup in intelligence_dupes[:20]:
            try:
                rel_lower = dup['lowercase'].relative_to(WS)
                rel_canon = dup['canonical'].relative_to(WS)
                report.append(f"  - **Meeting**: {dup['meeting']}")
                report.append(f"    - Duplicate: `{rel_lower.name}`")
                report.append(f"    - Canonical: `{rel_canon.name}`")
            except:
                pass
        if len(intelligence_dupes) > 20:
            report.append(f"\n... and {len(intelligence_dupes) - 20} more")
    else:
        report.append("None found ✓")
    
    # Registry duplicates (meeting-specific)
    report.append(f"\\n\\n## Registry Duplicates\\n")
    if registry_dupes and registry_dupes.get('duplicates'):
        reg_dups = registry_dupes['duplicates']
        total_dup_entries = registry_dupes['duplicate_count']
        report.append(f"Found {len(reg_dups)} duplicate Drive IDs ({total_dup_entries} duplicate entries):\\n")
        for gdrive_id, occurrences in list(reg_dups.items())[:10]:
            report.append(f"  - `{gdrive_id}`: {len(occurrences)} occurrences")
        if len(reg_dups) > 10:
            report.append(f"\n... and {len(reg_dups) - 10} more")
    else:
        report.append("None found ✓")
    
    # Exact duplicates
    report.append(f"\\n\\n## Exact Duplicates ({len(duplicates)} sets)\\n")
    if duplicates:
        for hash_val, files in list(duplicates.items())[:10]:
            report.append(f"\n**Set {hash_val[:8]}...** ({len(files)} files):")
            for f in files:
                try:
                    rel = f.relative_to(WS)
                    size_mb = f.stat().st_size / (1024 * 1024)
                    report.append(f"  - `{rel}` ({size_mb:.2f} MB)")
                except:
                    pass
        if len(duplicates) > 10:
            report.append(f"\n... and {len(duplicates) - 10} more sets")
    else:
        report.append("None found ✓")
    
    # Similar names
    report.append(f"\n\n## Similar Filenames ({len(similar)} groups)\\n")
    if similar:
        for group in similar[:10]:
            report.append(f"\n**Group**:")
            for f in group:
                try:
                    rel = f.relative_to(WS)
                    report.append(f"  - `{rel}`")
                except:
                    pass
        if len(similar) > 10:
            report.append(f"\n... and {len(similar) - 10} more groups")
    else:
        report.append("None found ✓")
    
    # Vestigial
    report.append(f"\n\n## Vestigial Files ({len(vestigial)})\\n")
    if vestigial:
        for item in vestigial[:20]:
            try:
                rel = item['path'].relative_to(WS)
                age = datetime.now() - item['modified']
                report.append(f"  - `{rel}` (pattern: `{item['pattern']}`, {age.days} days old)")
            except:
                pass
        if len(vestigial) > 20:
            report.append(f"\n... and {len(vestigial) - 20} more files")
    else:
        report.append("None found ✓")
    
    # Tiny files
    report.append(f"\n\n## Tiny/Empty Files ({len(tiny)})\\n")
    if tiny:
        for item in tiny[:20]:
            try:
                rel = item['path'].relative_to(WS)
                report.append(f"  - `{rel}` ({item['size']} bytes)")
            except:
                pass
        if len(tiny) > 20:
            report.append(f"\n... and {len(tiny) - 20} more files")
    else:
        report.append("None found ✓")
    
    return '\n'.join(report)


# ============================================================================
# Cleanup Functions
# ============================================================================

def cleanup_intelligence_duplicates(dry_run: bool = True) -> int:
    """Clean up intelligence file duplicates"""
    duplicates = find_intelligence_file_duplicates()
    
    if not duplicates:
        logger.info("No intelligence file duplicates to clean")
        return 0
    
    logger.info(f"Cleaning {len(duplicates)} intelligence file duplicates...")
    
    if dry_run:
        logger.info("DRY RUN - no files will be deleted")
        for dup in duplicates[:10]:
            logger.info(f"  Would delete: {dup['lowercase']}")
        if len(duplicates) > 10:
            logger.info(f"  ... and {len(duplicates) - 10} more")
        return len(duplicates)
    
    # Actual cleanup
    cleaned = 0
    for dup in duplicates:
        try:
            dup['lowercase'].unlink()
            cleaned += 1
            logger.info(f"Deleted: {dup['lowercase']}")
        except Exception as e:
            logger.error(f"Failed to delete {dup['lowercase']}: {e}")
    
    logger.info(f"✓ Cleaned {cleaned} intelligence file duplicates")
    return cleaned


def cleanup_registry_duplicates(dry_run: bool = True) -> int:
    """Clean up registry duplicates"""
    result = find_registry_duplicates()
    
    if not result or not result.get('duplicates'):
        logger.info("No registry duplicates to clean")
        return 0
    
    duplicates = result['duplicates']
    all_entries = result['all_entries']
    
    # Identify entries to keep (first occurrence of each ID)
    seen_ids = set()
    keep_indices = set()
    
    for idx, entry in all_entries:
        gdrive_id = entry.get("gdrive_id")
        if gdrive_id not in seen_ids:
            seen_ids.add(gdrive_id)
            keep_indices.add(idx)
    
    removed_count = len(all_entries) - len(keep_indices)
    
    logger.info(f"Found {len(duplicates)} duplicate Drive IDs")
    logger.info(f"Will remove {removed_count} duplicate entries")
    
    if dry_run:
        logger.info("DRY RUN - no changes made to registry")
        return removed_count
    
    # Backup first
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"meeting_gdrive_registry_{timestamp}.jsonl"
    shutil.copy(REGISTRY_PATH, backup_path)
    logger.info(f"✓ Backup created: {backup_path}")
    
    # Write deduplicated registry
    with open(REGISTRY_PATH, 'w') as f:
        for idx, entry in all_entries:
            if idx in keep_indices:
                f.write(json.dumps(entry) + "\n")
    
    logger.info(f"✓ Removed {removed_count} duplicate registry entries")
    return removed_count


# ============================================================================
# Main Entry Points
# ============================================================================

def scan(scan_path: str = None, output_json: bool = False, 
         intelligence_only: bool = False, registry_only: bool = False) -> int:
    """Scan for duplicates and generate report"""
    
    root = Path(scan_path) if scan_path else MEETINGS_DIR
    
    if not root.exists():
        logger.error(f"Path does not exist: {root}")
        return 1
    
    # Run scans based on flags
    if intelligence_only:
        intelligence_dupes = find_intelligence_file_duplicates()
        duplicates = {}
        similar = []
        registry_dupes = {}
        vestigial = []
        tiny = []
    elif registry_only:
        registry_dupes = find_registry_duplicates()
        duplicates = {}
        similar = []
        intelligence_dupes = []
        vestigial = []
        tiny = []
    else:
        # Full scan
        intelligence_dupes = find_intelligence_file_duplicates()
        registry_dupes = find_registry_duplicates()
        duplicates = find_exact_duplicates(root)
        similar = find_similar_names(root)
        vestigial = find_vestigial_files(root)
        tiny = find_tiny_files(root)
    
    # Generate output
    if output_json:
        json_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'intelligence_duplicates': [
                {
                    'lowercase': str(d['lowercase']),
                    'canonical': str(d['canonical']),
                    'meeting': d['meeting']
                } for d in intelligence_dupes
            ],
            'registry_duplicates': {
                'count': len(registry_dupes.get('duplicates', {})),
                'duplicate_entries': registry_dupes.get('duplicate_count', 0)
            },
            'exact_duplicates': {h: [str(f) for f in files] for h, files in duplicates.items()},
            'similar_names': [[str(f) for f in group] for group in similar],
            'vestigial_count': len(vestigial),
            'tiny_count': len(tiny)
        }
        print(json.dumps(json_data, indent=2))
    else:
        report_text = generate_report(duplicates, similar, intelligence_dupes, 
                                      registry_dupes, vestigial, tiny)
        print(report_text)
    
    return 0


def cleanup(dry_run: bool = True, intelligence_only: bool = False, 
            registry_only: bool = False) -> int:
    """Clean up detected duplicates"""
    
    if intelligence_only:
        return cleanup_intelligence_duplicates(dry_run=dry_run)
    elif registry_only:
        return cleanup_registry_duplicates(dry_run=dry_run)
    else:
        # Clean both
        intel_cleaned = cleanup_intelligence_duplicates(dry_run=dry_run)
        reg_cleaned = cleanup_registry_duplicates(dry_run=dry_run)
        logger.info(f"Total cleaned: {intel_cleaned} intelligence files, {reg_cleaned} registry entries")
        return intel_cleaned + reg_cleaned


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Canonical meeting duplicate detection tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 detect_meeting_duplicates.py scan
  python3 detect_meeting_duplicates.py scan --json
  python3 detect_meeting_duplicates.py scan --intelligence
  python3 detect_meeting_duplicates.py scan --registry
  python3 detect_meeting_duplicates.py cleanup --dry-run
  python3 detect_meeting_duplicates.py cleanup --intelligence --dry-run
  python3 detect_meeting_duplicates.py cleanup
        """
    )
    
    parser.add_argument("command", choices=["scan", "cleanup"], 
                       help="Command to run")
    parser.add_argument("--path", default=None,
                       help="Path to scan (default: Personal/Meetings)")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes only (cleanup mode)")
    parser.add_argument("--intelligence", action="store_true",
                       help="Focus on intelligence files only")
    parser.add_argument("--registry", action="store_true",
                       help="Focus on registry only")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        return scan(
            scan_path=args.path,
            output_json=args.json,
            intelligence_only=args.intelligence,
            registry_only=args.registry
        )
    elif args.command == "cleanup":
        return cleanup(
            dry_run=args.dry_run,
            intelligence_only=args.intelligence,
            registry_only=args.registry
        )
    
    return 1


if __name__ == "__main__":
    exit(main())

