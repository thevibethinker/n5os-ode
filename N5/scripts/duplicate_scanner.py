#!/usr/bin/env python3
"""
Duplicate Scanner - Detect duplicate files and vestigial artifacts

Uses multiple strategies:
1. Exact duplicates (same hash)
2. Similar names (case variants, version suffixes)
3. Empty/tiny files
4. Orphaned artifacts (conversation workspaces, temp files)

Usage:
    python3 duplicate_scanner.py --scan /home/workspace
    python3 duplicate_scanner.py --scan /home/workspace --report
    python3 duplicate_scanner.py --fdupes /home/workspace  # Use fdupes if available
"""

import argparse
import hashlib
import json
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import subprocess
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WS = Path('/home/workspace')

# Protected paths - never suggest deleting these
PROTECTED_PATHS = [
    'N5/', 'Knowledge/', 'Lists/', 'Documents/', 'Careerspan/', 'Personal/',
    'Projects/', 'Records/', '.git/'
]

# Vestigial patterns
VESTIGIAL_PATTERNS = [
    r'copy( of)?',
    r'final(_final)?',
    r'draft',
    r'backup',
    r'old',
    r'temp',
    r'untitled',
    r'\(\d+\)',  # (1), (2), etc
    r'_v\d+',    # _v1, _v2
    r'#\d+',     # #2, #3
]

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
    """Find files with identical content"""
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
    """Find files with suspiciously similar names"""
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

def find_vestigial_files(root: Path) -> list:
    """Find files with vestigial naming patterns"""
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
    """Find suspiciously tiny or empty files"""
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

def use_fdupes(root: Path) -> dict:
    """Use fdupes if available (faster for large scans)"""
    try:
        result = subprocess.run(
            ['fdupes', '-r', str(root)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            # Parse fdupes output (groups separated by blank lines)
            groups = result.stdout.strip().split('\n\n')
            duplicates = {}
            for i, group in enumerate(groups):
                files = [Path(line) for line in group.split('\n') if line]
                if len(files) > 1:
                    duplicates[f"group_{i}"] = files
            return duplicates
        else:
            logger.warning("fdupes failed, falling back to Python implementation")
            return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

def generate_report(duplicates, similar, vestigial, tiny) -> str:
    """Generate human-readable report"""
    report = []
    report.append("# Duplicate & Vestigial File Report")
    report.append(f"\nGenerated: {datetime.utcnow().isoformat()}Z")
    report.append("\n---\n")
    
    # Exact duplicates
    report.append(f"## Exact Duplicates ({len(duplicates)} sets)\n")
    if duplicates:
        for hash_val, files in list(duplicates.items())[:10]:  # Show first 10
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
    report.append(f"\n\n## Similar Filenames ({len(similar)} groups)\n")
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
    report.append(f"\n\n## Vestigial Files ({len(vestigial)})\n")
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
    report.append(f"\n\n## Tiny/Empty Files ({len(tiny)})\n")
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

def main(scan_path: str, use_fdupes_flag: bool = False, report_only: bool = False) -> int:
    """Main entry point"""
    root = Path(scan_path)
    
    if not root.exists():
        logger.error(f"Path does not exist: {root}")
        return 1
    
    # Use fdupes if requested and available
    if use_fdupes_flag:
        duplicates = use_fdupes(root)
        if duplicates is None:
            duplicates = find_exact_duplicates(root)
    else:
        duplicates = find_exact_duplicates(root)
    
    similar = find_similar_names(root)
    vestigial = find_vestigial_files(root)
    tiny = find_tiny_files(root)
    
    # Generate report
    report_text = generate_report(duplicates, similar, vestigial, tiny)
    
    # Save report
    report_path = WS / 'N5/data/duplicate_scan_report.md'
    report_path.write_text(report_text)
    logger.info(f"✓ Report saved to {report_path}")
    
    # Also save JSON for programmatic access
    json_data = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'exact_duplicates': {h: [str(f) for f in files] for h, files in duplicates.items()},
        'similar_names': [[str(f) for f in group] for group in similar],
        'vestigial_count': len(vestigial),
        'tiny_count': len(tiny)
    }
    json_path = WS / 'N5/data/duplicate_scan.json'
    json_path.write_text(json.dumps(json_data, indent=2))
    logger.info(f"✓ JSON saved to {json_path}")
    
    if report_only:
        print(report_text)
    
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for duplicates and vestigial files")
    parser.add_argument("--scan", required=True, help="Path to scan")
    parser.add_argument("--fdupes", action="store_true", help="Use fdupes if available")
    parser.add_argument("--report", action="store_true", help="Print report to stdout")
    
    args = parser.parse_args()
    exit(main(scan_path=args.scan, use_fdupes_flag=args.fdupes, report_only=args.report))
