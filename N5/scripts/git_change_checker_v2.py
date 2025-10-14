#!/usr/bin/env python3
"""
Git Change Checker v2: Comprehensive audit for staged Git changes

Exit codes:
  0 = Clean, safe to commit
  1 = Issues found, review required
  2 = Git error, cannot audit
  3 = Invalid repository state

Version: 2.0.0
"""

import subprocess
import sys
import re
import argparse
import logging
from pathlib import Path
from fnmatch import fnmatch
from typing import List, Dict, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Configuration
DELETION_THRESHOLD = {
    'min_lines': 50,
    'min_ratio': 0.7  # 70% of changes must be deletions
}

LARGE_FILE_THRESHOLD_MB = 1

PROTECTED_PATTERNS = [
    # Core system configs
    'N5/config/commands.jsonl',
    'N5/config/*.json',
    'N5/schemas/*.json',
    'N5/prefs/**/*.json',
    'N5/prefs/**/*.md',
    
    # Architectural knowledge
    'Knowledge/architectural/**/*.md',
    'Knowledge/architectural/principles/*.md',
    
    # Action lists and registry
    'Lists/index.jsonl',
    'Lists/schemas/*.json',
    'Lists/*.jsonl',
    
    # Git internals
    '.git/**',
    
    # Secrets and credentials
    '**/.env*',
    '**/secrets/**',
    'N5/config/credentials/**',
    '**/credentials.json',
    '**/*_credentials.json',
    
    # Critical N5 components
    'N5/intelligence/*.json',
    'Knowledge/crm/profiles/index.jsonl'
]

SENSITIVE_PATTERNS = [
    (r'-----BEGIN .* PRIVATE KEY-----', 'Private key'),
    (r'api[_-]?key[\s:=]+["\']?[A-Za-z0-9/+]{20,}', 'API key'),
    (r'password[\s:=]+["\']?.{8,}', 'Password'),
    (r'token[\s:=]+["\']?[A-Za-z0-9_\-\.]{20,}', 'Token'),
    (r'secret[\s:=]+["\']?[A-Za-z0-9_\-\.]{16,}', 'Secret'),
    (r'sk-[A-Za-z0-9]{20,}', 'OpenAI key'),
    (r'AKIA[0-9A-Z]{16}', 'AWS access key'),
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub token'),
]


def run_git(args: List[str], cwd: Path = None) -> subprocess.CompletedProcess:
    """Run git command and return result"""
    try:
        git_root = cwd or Path('/home/workspace')
        return subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            cwd=git_root,
            check=False
        )
    except Exception as e:
        logger.error(f"Failed to run git: {e}")
        return subprocess.CompletedProcess(args, 2, '', str(e))


def find_git_root() -> Optional[Path]:
    """Find git repository root by walking up from CWD"""
    # Start from /home/workspace since that's where our git repo lives
    git_root = Path('/home/workspace')
    if (git_root / '.git').exists():
        return git_root
    
    # Fall back to searching from CWD
    cwd = Path.cwd()
    while cwd != cwd.parent:
        if (cwd / '.git').exists():
            return cwd
        cwd = cwd.parent
    return None


def verify_git_state() -> bool:
    """Ensure we're in a valid repo with no conflicts"""
    git_root = find_git_root()
    if not git_root:
        logger.error("Not in a git repository")
        return False
    
    logger.info(f"Git repository root: {git_root}")
    
    # Check for merge conflicts
    result = run_git(['ls-files', '-u'])
    if result.returncode != 0:
        logger.error(f"Git error checking unmerged files: {result.stderr}")
        return False
    
    if result.stdout.strip():
        logger.error("Unmerged files detected - resolve conflicts first")
        return False
    
    return True


def get_staged_files() -> List[Tuple[str, str]]:
    """Get list of staged files with their status (M/A/D/etc)"""
    result = run_git(['diff', '--staged', '--name-status'])
    if result.returncode != 0:
        logger.error(f"Git diff error: {result.stderr}")
        return []
    
    files = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split('\t', 1)
        if len(parts) == 2:
            status, filepath = parts
            files.append((status, filepath))
    
    return files


def check_protected_files(staged_files: List[Tuple[str, str]]) -> List[str]:
    """Check if any protected files are being modified"""
    issues = []
    
    for status, filepath in staged_files:
        for pattern in PROTECTED_PATTERNS:
            # Match pattern against filepath
            if fnmatch(filepath, pattern) or fnmatch(f"**/{filepath}", pattern):
                severity = "🚨 CRITICAL" if any(x in pattern for x in ['.git', 'secrets', 'credentials', '.env']) else "⚠️  WARNING"
                issues.append(f"{severity}: Protected file staged: {filepath} (matches pattern: {pattern})")
                break
    
    return issues


def is_significant_deletion(filepath: str) -> Optional[str]:
    """Check if file has significant deletions using quantitative threshold"""
    result = run_git(['diff', '--staged', '--numstat', filepath])
    if result.returncode != 0:
        return None
    
    # Format: additions deletions filename
    # Example: 5  150  file.md
    line = result.stdout.strip()
    if not line:
        return None
    
    parts = line.split()
    if len(parts) < 2:
        return None
    
    try:
        adds = int(parts[0]) if parts[0] != '-' else 0
        dels = int(parts[1]) if parts[1] != '-' else 0
    except ValueError:
        return None
    
    total_changes = adds + dels
    if total_changes == 0:
        return None
    
    deletion_ratio = dels / total_changes
    
    # Flag if: >50 lines deleted AND >70% of changes are deletions
    if dels > DELETION_THRESHOLD['min_lines'] and deletion_ratio > DELETION_THRESHOLD['min_ratio']:
        return f"⚠️  {filepath}: Significant deletions detected ({dels} lines, {deletion_ratio:.0%} of changes)"
    
    return None


def check_large_files(staged_files: List[Tuple[str, str]]) -> List[str]:
    """Detect large files being added"""
    issues = []
    git_root = find_git_root()
    
    for status, filepath in staged_files:
        if status in ['M', 'A']:  # Modified or Added
            full_path = git_root / filepath
            if full_path.exists():
                size_bytes = full_path.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                
                if size_mb > LARGE_FILE_THRESHOLD_MB:
                    issues.append(f"⚠️  {filepath}: Large file ({size_mb:.1f}MB)")
    
    return issues


def check_empty_files(staged_files: List[Tuple[str, str]]) -> List[str]:
    """Check for empty files (potential overwrites)"""
    issues = []
    git_root = find_git_root()
    
    for status, filepath in staged_files:
        if status in ['M', 'A']:
            full_path = git_root / filepath
            if full_path.exists():
                if full_path.stat().st_size == 0:
                    issues.append(f"🚨 CRITICAL: {filepath} is now empty (potential data loss)")
    
    return issues


def is_binary_file(filepath: Path) -> bool:
    """Check if file is binary by reading first 8KB"""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(8192)
            return b'\x00' in chunk
    except:
        return False


def check_binary_overwrites(staged_files: List[Tuple[str, str]]) -> List[str]:
    """Detect complete binary file rewrites"""
    issues = []
    git_root = find_git_root()
    
    for status, filepath in staged_files:
        if status == 'M':  # Modified only
            full_path = git_root / filepath
            if full_path.exists() and is_binary_file(full_path):
                # Check if this is a complete binary rewrite
                result = run_git(['diff', '--staged', '--numstat', filepath])
                if result.returncode == 0:
                    line = result.stdout.strip()
                    # Binary files show as: - - filename
                    if line.startswith('- -'):
                        issues.append(f"⚠️  {filepath}: Binary file completely rewritten")
    
    return issues


def scan_for_secrets(staged_files: List[Tuple[str, str]]) -> List[str]:
    """Scan file contents for sensitive data patterns"""
    issues = []
    git_root = find_git_root()
    
    # Skip files that are pattern definitions themselves or security documentation
    skip_files = {
        'git_change_checker_v2.py',
        'git_change_checker.py',
        'README_git_check_v2.md',  # Contains example patterns for documentation
        'detection_rules.md'
    }
    
    for status, filepath in staged_files:
        if status in ['M', 'A']:
            full_path = git_root / filepath
            
            # Skip binary files
            if full_path.exists() and is_binary_file(full_path):
                continue
            
            # Skip large files (>1MB)
            if full_path.exists() and full_path.stat().st_size > 1_000_000:
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Skip files that appear to be pattern definition files
                # (check if they have SENSITIVE_PATTERNS variable or tuple definitions)
                if 'SENSITIVE_PATTERNS' in content or 'pattern' in content.lower():
                    # Do basic check: if many patterns are defined, likely a config file
                    pattern_count = content.count('-----BEGIN') + content.count('api[_-]?key')
                    if pattern_count > 3:  # More than 3 pattern definitions
                        logger.debug(f"Skipping {filepath}: appears to be pattern definition file")
                        continue
                
                for pattern, name in SENSITIVE_PATTERNS:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        # Additional check: is this in a comment, string literal, or markdown code?
                        for match in matches:
                            # Find the line containing this match
                            lines = content.split('\n')
                            for line in lines:
                                if match in line:
                                    # Skip if it's in a markdown code block (backticks)
                                    if '`' in line:
                                        # Count backticks before and after match position
                                        match_pos = line.index(match)
                                        before_backticks = line[:match_pos].count('`')
                                        if before_backticks % 2 == 1:  # Odd number = inside code span
                                            continue
                                    
                                    # Skip if it's in a comment
                                    if '#' in line:
                                        comment_pos = line.find('#')
                                        match_pos = line.find(match)
                                        if comment_pos < match_pos:
                                            continue
                                    
                                    # Skip if it's a regex pattern definition
                                    if "r'" in line or 'r"' in line:
                                        continue
                                    
                                    # Real match found
                                    issues.append(f"🚨 CRITICAL: {filepath} contains potential {name}")
                                    break
                            break  # Only report once per file
                        break
            
            except Exception as e:
                logger.debug(f"Could not scan {filepath}: {e}")
    
    return issues


def main(dry_run: bool = False) -> int:
    """Main audit function"""
    
    # Step 1: Verify git state
    logger.info("Verifying git repository state...")
    if not verify_git_state():
        return 3  # Invalid state
    
    # Step 2: Get staged files
    logger.info("Retrieving staged files...")
    staged_files = get_staged_files()
    
    if not staged_files:
        logger.info("✅ No staged files to audit")
        return 0
    
    logger.info(f"Found {len(staged_files)} staged files")
    
    if dry_run:
        logger.info("[DRY RUN] Would check:")
        logger.info(f"  - Protected patterns: {len(PROTECTED_PATTERNS)}")
        logger.info(f"  - Deletion threshold: {DELETION_THRESHOLD['min_lines']} lines, {DELETION_THRESHOLD['min_ratio']:.0%} ratio")
        logger.info(f"  - Large file threshold: {LARGE_FILE_THRESHOLD_MB}MB")
        logger.info(f"  - Sensitive patterns: {len(SENSITIVE_PATTERNS)}")
        logger.info(f"  - Binary overwrites: Yes")
        logger.info(f"  - Empty files: Yes")
        return 0
    
    # Step 3: Run all checks
    all_issues = []
    
    logger.info("Checking protected files...")
    all_issues.extend(check_protected_files(staged_files))
    
    logger.info("Checking for empty files...")
    all_issues.extend(check_empty_files(staged_files))
    
    logger.info("Scanning for sensitive data...")
    all_issues.extend(scan_for_secrets(staged_files))
    
    logger.info("Checking large files...")
    all_issues.extend(check_large_files(staged_files))
    
    logger.info("Checking binary overwrites...")
    all_issues.extend(check_binary_overwrites(staged_files))
    
    logger.info("Checking for significant deletions...")
    for status, filepath in staged_files:
        if status == 'M':  # Only modified files
            issue = is_significant_deletion(filepath)
            if issue:
                all_issues.append(issue)
    
    # Step 4: Report results
    if not all_issues:
        logger.info("✅ No issues detected - safe to commit")
        return 0
    else:
        logger.warning(f"❌ Found {len(all_issues)} issue(s) - REVIEW REQUIRED")
        print("\n" + "="*60)
        print("GIT CHECK FAILED - Issues detected:")
        print("="*60)
        for issue in all_issues:
            print(issue)
        print("="*60)
        print("\nReview these changes before committing.")
        print("To commit anyway: git commit --no-verify")
        return 1  # Issues found, block commit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Audit staged Git changes for potential issues"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be checked without actually checking'
    )
    
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))
