#!/usr/bin/env python3
"""
Conversation PII Audit - Check for PII in files created/modified during a conversation

Called during conversation close to ensure any PII created in USER workspace
is properly marked for protection.

Usage:
    conversation_pii_audit.py --convo-id <id> [--dry-run] [--auto-mark]
    
Process:
1. Read SESSION_STATE.md to get list of artifacts
2. Scan git diff to find files changed during conversation
3. Run PII scanner on those files
4. Auto-mark directories containing PII (if --auto-mark)
5. Report findings for human review

Returns JSON with:
- files_scanned: list of files checked
- pii_found: list of {file, types, lines} 
- directories_marked: list of paths marked as PII
- requires_attention: bool
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Set, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
USER_WORKSPACE = Path("/home/workspace")
CONVO_WORKSPACE_BASE = Path("/home/.z/workspaces")

# Import PII scanner
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from pii_scanner import scan_file, PII_PATTERNS
except ImportError:
    logger.warning("pii_scanner not available, using fallback patterns")
    PII_PATTERNS = None


def get_convo_path(convo_id: str) -> Path:
    """Get conversation workspace path."""
    if not convo_id.startswith("con_"):
        convo_id = f"con_{convo_id}"
    return CONVO_WORKSPACE_BASE / convo_id


def read_session_state(convo_path: Path) -> Dict[str, Any]:
    """Read SESSION_STATE.md and extract artifact paths."""
    state_file = convo_path / "SESSION_STATE.md"
    artifacts = []
    
    if not state_file.exists():
        return {"artifacts": []}
    
    content = state_file.read_text()
    
    # Extract artifact paths from markdown
    # Look for patterns like `file 'path/to/file'` or paths in artifact sections
    import re
    
    # Pattern 1: file mentions
    file_mentions = re.findall(r"`file '([^']+)'`", content)
    artifacts.extend(file_mentions)
    
    # Pattern 2: paths in lists (- path/to/file or * path/to/file)
    list_paths = re.findall(r"^[\-\*]\s+([/\w\-\.]+\.(?:py|md|json|yaml|yml|txt|csv))", content, re.MULTILINE)
    artifacts.extend(list_paths)
    
    # Pattern 3: Artifacts section
    if "## Artifacts" in content or "### Artifacts" in content:
        artifact_section = re.search(r"#{2,3}\s*Artifacts.*?(?=#{2,3}|\Z)", content, re.DOTALL)
        if artifact_section:
            section_paths = re.findall(r"([/\w\-\.]+\.(?:py|md|json|yaml|yml|txt|csv))", artifact_section.group())
            artifacts.extend(section_paths)
    
    # Resolve to absolute paths
    resolved = []
    for artifact in set(artifacts):
        if artifact.startswith("/"):
            path = Path(artifact)
        else:
            path = USER_WORKSPACE / artifact
        if path.exists() and path.is_file():
            resolved.append(str(path))
    
    return {"artifacts": resolved}


def get_git_changed_files() -> List[str]:
    """Get files changed in git (staged + unstaged + untracked)."""
    files = []
    
    try:
        # Staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=USER_WORKSPACE, timeout=10
        )
        if result.returncode == 0:
            files.extend(result.stdout.strip().split("\n"))
        
        # Unstaged changes
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True, text=True, cwd=USER_WORKSPACE, timeout=10
        )
        if result.returncode == 0:
            files.extend(result.stdout.strip().split("\n"))
        
        # Untracked files
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, cwd=USER_WORKSPACE, timeout=10
        )
        if result.returncode == 0:
            files.extend(result.stdout.strip().split("\n"))
            
    except Exception as e:
        logger.warning(f"Git scan failed: {e}")
    
    # Filter and resolve
    resolved = []
    for f in files:
        if not f.strip():
            continue
        path = USER_WORKSPACE / f
        if path.exists() and path.is_file():
            resolved.append(str(path))
    
    return list(set(resolved))


def scan_file_for_pii(filepath: str) -> Dict[str, Any]:
    """Scan a single file for PII. Returns dict with types found."""
    import re
    
    result = {
        "file": filepath,
        "has_pii": False,
        "types": [],
        "sample_lines": []
    }
    
    path = Path(filepath)
    
    # Skip directories that shouldn't contain user PII
    skip_dirs = {'site-packages', '__pycache__', 'node_modules', '.git', '.venv', 
                 'venv', 'env', '.tox', 'dist', 'build', '.eggs', 'vendor'}
    if any(d in path.parts for d in skip_dirs):
        return result
    
    # Skip binary and non-text files
    skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.gz', '.tar',
                       '.db', '.sqlite', '.pyc', '.pyo', '.so', '.dylib', '.dll',
                       '.exe', '.bin', '.whl', '.egg', '.ico', '.woff', '.woff2',
                       '.ttf', '.eot', '.mp3', '.mp4', '.wav', '.avi', '.mov',
                       '.pem', '.crt', '.key'}  # cert files have false positives
    if path.suffix.lower() in skip_extensions:
        return result
    
    # Skip common non-user files
    skip_filenames = {'METADATA', 'AUTHORS', 'AUTHORS.txt', 'CONTRIBUTORS', 
                      'LICENSE', 'LICENSE.txt', 'COPYING', 'COPYING.rst',
                      'PKG-INFO', 'RECORD', 'WHEEL', 'entry_points.txt',
                      'cacert.pem', 'top_level.txt'}
    if path.name in skip_filenames:
        return result
    
    try:
        if path.stat().st_size > 500_000:  # 500KB limit (reduced)
            return result
    except:
        return result
    
    # PII patterns (simplified from pii_scanner.py)
    patterns = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        "ssn": r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
        "credit_card": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b',
    }
    
    # Exclude patterns (false positives)
    exclude_patterns = [
        r'example\.com',
        r'test@',
        r'placeholder',
        r'xxx-xx-xxxx',
        r'000-00-0000',
        r'Copyright',
        r'__author__',
        r'Author:',
        r'Maintainer',
        r'@.*\.org',  # Often project emails
        r'@github\.com',
        r'@python\.org',
        r'@gmail\.com',  # Too common, not V's PII
        r'Created by',
        r'Contributed by',
        r'version.*\d{3}[-\s]?\d{2}[-\s]?\d{4}',  # Version strings
        r'http://.*\d{3}[-\s]?\d{2}[-\s]?\d{4}',  # URLs with numbers
        r'https://.*\d{3}[-\s]?\d{2}[-\s]?\d{4}', # URLs with numbers
        r'doi\.org',  # DOI links
        r'Serial:',  # Certificate serial numbers
        r'Issuer:',  # Certificate issuers
        r'\[\d+\]',  # Array indices
        r'seed\s*=',  # Random seeds
        r'0\.[0-9]{12,}',  # Decimal numbers (credit card false positives)
    ]
    
    try:
        content = path.read_text(errors='ignore')
    except Exception as e:
        return result
    
    types_found = set()
    samples = []
    
    for line_num, line in enumerate(content.split('\n'), 1):
        # Skip if line matches exclusion pattern
        if any(re.search(p, line, re.I) for p in exclude_patterns):
            continue
        
        # Skip lines that look like code/config, not user data
        if line.strip().startswith(('#', '//', '/*', '*', 'import ', 'from ', 'def ', 'class ')):
            continue
            
        for pii_type, pattern in patterns.items():
            if re.search(pattern, line):
                types_found.add(pii_type)
                if len(samples) < 3:
                    # Redact the actual PII
                    redacted = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', line[:100])
                    samples.append(f"Line {line_num}: {redacted}")
    
    if types_found:
        result["has_pii"] = True
        result["types"] = list(types_found)
        result["sample_lines"] = samples
    
    return result


def mark_directory_pii(directory: str, pii_types: List[str], note: str, dry_run: bool = False) -> bool:
    """Mark a directory as containing PII using n5_protect.py."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would mark {directory} as PII: {pii_types}")
        return True
    
    # Map PII types to categories
    category_map = {
        "email": "email",
        "phone": "phone",
        "ssn": "ssn",
        "credit_card": "financial",
        "name": "name",
        "address": "address",
    }
    
    categories = [category_map.get(t, t) for t in pii_types]
    categories_str = ",".join(set(categories))
    
    try:
        # First check if already protected
        check_result = subprocess.run(
            ["python3", str(SCRIPT_DIR / "n5_protect.py"), "check", directory],
            capture_output=True, text=True, timeout=10
        )
        
        if "Not protected" in check_result.stdout:
            # Protect with PII flags
            result = subprocess.run(
                ["python3", str(SCRIPT_DIR / "n5_protect.py"), "protect", directory,
                 "--reason", f"Contains PII detected during conversation close",
                 "--pii", "--pii-categories", categories_str,
                 "--pii-note", note],
                capture_output=True, text=True, timeout=10
            )
        else:
            # Already protected, just mark PII
            result = subprocess.run(
                ["python3", str(SCRIPT_DIR / "n5_protect.py"), "mark-pii", directory,
                 "--categories", categories_str, "--note", note],
                capture_output=True, text=True, timeout=10
            )
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Failed to mark {directory}: {e}")
        return False


def run_pii_audit(convo_id: str, dry_run: bool = False, auto_mark: bool = False) -> Dict[str, Any]:
    """Main audit function."""
    start_time = datetime.now(timezone.utc)
    
    result = {
        "convo_id": convo_id,
        "timestamp": start_time.isoformat(),
        "files_scanned": [],
        "pii_found": [],
        "directories_marked": [],
        "requires_attention": False,
        "dry_run": dry_run,
        "errors": []
    }
    
    # Normalize convo_id
    if not convo_id.startswith("con_"):
        convo_id = f"con_{convo_id}"
    
    convo_path = get_convo_path(convo_id)
    
    # Collect files to scan
    files_to_scan = set()
    
    # Source 1: SESSION_STATE artifacts
    session_data = read_session_state(convo_path)
    for artifact in session_data.get("artifacts", []):
        files_to_scan.add(artifact)
    
    # Source 2: Git changed files
    git_files = get_git_changed_files()
    files_to_scan.update(git_files)
    
    logger.info(f"Scanning {len(files_to_scan)} files for PII")
    
    # Scan each file
    directories_with_pii: Dict[str, Set[str]] = {}  # dir -> set of PII types
    
    for filepath in files_to_scan:
        result["files_scanned"].append(filepath)
        
        scan_result = scan_file_for_pii(filepath)
        
        if scan_result["has_pii"]:
            result["pii_found"].append(scan_result)
            result["requires_attention"] = True
            
            # Track directory
            parent_dir = str(Path(filepath).parent)
            if parent_dir not in directories_with_pii:
                directories_with_pii[parent_dir] = set()
            directories_with_pii[parent_dir].update(scan_result["types"])
    
    # Auto-mark directories if requested
    if auto_mark and directories_with_pii:
        for directory, pii_types in directories_with_pii.items():
            # Only mark USER workspace directories
            if not directory.startswith(str(USER_WORKSPACE)):
                continue
            
            note = f"PII detected during conversation close ({convo_id})"
            success = mark_directory_pii(directory, list(pii_types), note, dry_run)
            
            if success:
                result["directories_marked"].append({
                    "path": directory,
                    "types": list(pii_types)
                })
    
    return result


def format_output(result: Dict[str, Any]) -> str:
    """Format audit result for display."""
    output = []
    
    output.append("## PII Audit Results\n")
    output.append(f"**Conversation:** {result['convo_id']}")
    output.append(f"**Files Scanned:** {len(result['files_scanned'])}")
    output.append(f"**PII Detected:** {'Yes ⚠️' if result['requires_attention'] else 'No ✓'}")
    
    if result["dry_run"]:
        output.append("\n*[DRY-RUN MODE - No changes made]*\n")
    
    if result["pii_found"]:
        output.append("\n### PII Found\n")
        output.append("| File | Types | Sample |")
        output.append("|------|-------|--------|")
        
        for item in result["pii_found"]:
            filename = Path(item["file"]).name
            types = ", ".join(item["types"])
            sample = item["sample_lines"][0] if item["sample_lines"] else "-"
            # Truncate sample
            sample = sample[:50] + "..." if len(sample) > 50 else sample
            output.append(f"| `{filename}` | {types} | {sample} |")
    
    if result["directories_marked"]:
        output.append("\n### Directories Marked as PII\n")
        for item in result["directories_marked"]:
            rel_path = Path(item["path"]).relative_to(USER_WORKSPACE)
            types = ", ".join(item["types"])
            output.append(f"- `{rel_path}/` ({types})")
    
    if result["requires_attention"] and not result["directories_marked"]:
        output.append("\n### ⚠️ Action Required\n")
        output.append("PII was detected but directories were not auto-marked.")
        output.append("Review findings and manually protect sensitive directories:")
        output.append("```bash")
        output.append("python3 N5/scripts/n5_protect.py protect <path> --reason 'description' --pii --pii-categories <types>")
        output.append("```")
    
    if result["errors"]:
        output.append("\n### Errors\n")
        for error in result["errors"]:
            output.append(f"- {error}")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Audit conversation for PII and optionally mark directories"
    )
    parser.add_argument("--convo-id", required=True, help="Conversation ID")
    parser.add_argument("--dry-run", action="store_true", help="Preview without marking")
    parser.add_argument("--auto-mark", action="store_true", help="Auto-mark directories with PII")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    
    args = parser.parse_args()
    
    result = run_pii_audit(args.convo_id, args.dry_run, args.auto_mark)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result))
    
    # Exit code: 0 if no PII or all handled, 1 if requires attention
    return 1 if (result["requires_attention"] and not result["directories_marked"]) else 0


if __name__ == "__main__":
    sys.exit(main())


