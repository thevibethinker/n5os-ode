#!/usr/bin/env python3
"""
N5 Placeholder Scanner
Scans conversation workspace for placeholders, stubs, and incomplete code

Enforces P16 (Accuracy) and P21 (Document Assumptions) at conversation-end
"""

import os
import re
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
CONFIG_FILE = WORKSPACE / "N5/config/placeholder_patterns.json"

# Detect conversation workspace
CONVERSATION_WS_ENV = os.getenv("CONVERSATION_WORKSPACE")
if CONVERSATION_WS_ENV:
    CONVERSATION_WS = Path(CONVERSATION_WS_ENV)
else:
    workspaces_dir = Path("/home/.z/workspaces")
    if workspaces_dir.exists():
        workspaces = [d for d in workspaces_dir.iterdir() if d.is_dir() and d.name.startswith("con_")]
        if workspaces:
            CONVERSATION_WS = max(workspaces, key=lambda d: d.stat().st_mtime)
        else:
            CONVERSATION_WS = None
    else:
        CONVERSATION_WS = None


def load_patterns() -> Dict:
    """Load detection patterns from config file"""
    if not CONFIG_FILE.exists():
        logger.error(f"Patterns config not found: {CONFIG_FILE}")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def get_file_type(filepath: Path, config: Dict) -> str:
    """Determine file type from extension"""
    ext = filepath.suffix.lower()
    
    for file_type, rules in config['file_type_rules'].items():
        if ext in rules['extensions']:
            return file_type
    
    return None


def is_excluded_line(line: str, exclusions: List[str]) -> bool:
    """Check if line should be excluded from scanning"""
    line_stripped = line.strip()
    for pattern in exclusions:
        if pattern in line_stripped:
            return True
    return False


def check_function_stub(lines: List[str], line_idx: int, pattern_name: str) -> Tuple[bool, str]:
    """
    Check if a function stub has a docstring
    Returns: (is_violation, context)
    """
    if line_idx == 0:
        return True, ""
    
    line = lines[line_idx].strip()
    
    # Check if previous lines contain docstring
    for i in range(max(0, line_idx - 5), line_idx):
        prev_line = lines[i].strip()
        if '"""' in prev_line or "'''" in prev_line or 'docstring' in prev_line.lower():
            return False, ""
    
    # Get context (function signature)
    context = line
    if line_idx > 0:
        context = lines[line_idx - 1].strip() + " " + context
    
    return True, context


def scan_file(filepath: Path, config: Dict) -> List[Dict]:
    """
    Scan a single file for placeholder patterns
    Returns list of issues found
    """
    file_type = get_file_type(filepath, config)
    if not file_type:
        return []
    
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        logger.warning(f"Failed to read {filepath.name}: {e}")
        return []
    
    # Get patterns to check for this file type
    patterns_to_check = config['file_type_rules'][file_type]['check_patterns']
    exclusion_patterns = config['exclusions']['patterns']
    
    for pattern_name in patterns_to_check:
        pattern_config = config['patterns'][pattern_name]
        if not pattern_config['enabled']:
            continue
        
        for pattern_str in pattern_config['patterns']:
            try:
                pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern_str}': {e}")
                continue
            
            # Search line by line for better context
            for line_idx, line in enumerate(lines, start=1):
                if is_excluded_line(line, exclusion_patterns):
                    continue
                
                match = pattern.search(line)
                if match:
                    # Special handling for function stubs
                    if pattern_name == "function_stubs":
                        is_violation, context = check_function_stub(lines, line_idx - 1, pattern_name)
                        if not is_violation:
                            continue
                    
                    issues.append({
                        'file': str(filepath.relative_to(CONVERSATION_WS)),
                        'line': line_idx,
                        'pattern': pattern_name,
                        'severity': pattern_config['severity'],
                        'message': pattern_config['message'],
                        'context': line.strip()[:80]
                    })
    
    return issues


def scan_workspace(config: Dict) -> Dict:
    """
    Scan entire conversation workspace
    Returns dict of {severity: [issues]}
    """
    if not CONVERSATION_WS or not CONVERSATION_WS.exists():
        logger.error(f"Conversation workspace not found: {CONVERSATION_WS}")
        return {}
    
    logger.info(f"Scanning workspace: {CONVERSATION_WS}")
    
    all_issues = []
    files_scanned = 0
    
    for filepath in CONVERSATION_WS.rglob("*"):
        if not filepath.is_file():
            continue
        
        # Skip certain directories
        if any(part in filepath.parts for part in ['.git', '__pycache__', 'node_modules']):
            continue
        
        issues = scan_file(filepath, config)
        all_issues.extend(issues)
        files_scanned += 1
    
    logger.info(f"Scanned {files_scanned} files")
    
    # Group by severity
    by_severity = defaultdict(list)
    for issue in all_issues:
        by_severity[issue['severity']].append(issue)
    
    return dict(by_severity)


def format_report(issues_by_severity: Dict) -> str:
    """Format scan results as human-readable report"""
    if not issues_by_severity:
        return """
╔══════════════════════════════════════════════════════════════════════╗
║              PLACEHOLDER SCAN: ✅ NO ISSUES FOUND                    ║
╚══════════════════════════════════════════════════════════════════════╝

All files are clean. No placeholders, stubs, or fake data detected.
"""
    
    total_issues = sum(len(issues) for issues in issues_by_severity.values())
    
    lines = []
    lines.append("\n" + "="*70)
    lines.append("⚠️  PLACEHOLDER SCAN: ISSUES DETECTED")
    lines.append("="*70)
    lines.append(f"\nTotal issues: {total_issues}\n")
    
    # Report by severity
    severity_order = ['critical', 'high', 'medium', 'low']
    severity_icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🔵'
    }
    
    for severity in severity_order:
        if severity not in issues_by_severity:
            continue
        
        issues = issues_by_severity[severity]
        icon = severity_icons.get(severity, '⚠️')
        
        lines.append(f"\n{icon} {severity.upper()} SEVERITY ({len(issues)} issues)")
        lines.append("-"*70)
        
        # Group by file
        by_file = defaultdict(list)
        for issue in issues:
            by_file[issue['file']].append(issue)
        
        for filepath in sorted(by_file.keys()):
            lines.append(f"\n📄 {filepath}")
            
            for issue in sorted(by_file[filepath], key=lambda x: x['line']):
                lines.append(f"   Line {issue['line']:4d}: {issue['message']}")
                lines.append(f"              {issue['context']}")
    
    lines.append("\n" + "="*70)
    lines.append("RESOLUTION REQUIRED")
    lines.append("="*70)
    lines.append("\nOptions:")
    lines.append("  1. Fix issues now (return to conversation)")
    lines.append("  2. Document as intentional (add # DOCUMENTED: prefix)")
    lines.append("  3. Acknowledge & continue (log to tracking file)")
    lines.append("")
    
    return "\n".join(lines)


def save_report(issues_by_severity: Dict, output_file: Path):
    """Save detailed JSON report"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': str(Path.cwd()),
            'total_issues': sum(len(issues) for issues in issues_by_severity.values()),
            'by_severity': issues_by_severity
        }, f, indent=2)
    
    logger.info(f"Report saved: {output_file}")


def main(dry_run: bool = False) -> int:
    """
    Main scan function
    Returns: 0 if clean, 1 if issues found
    """
    try:
        config = load_patterns()
        
        if dry_run:
            logger.info("[DRY RUN MODE]")
        
        issues_by_severity = scan_workspace(config)
        
        # Print report
        report = format_report(issues_by_severity)
        print(report)
        
        # Save detailed report if issues found
        if issues_by_severity:
            report_file = CONVERSATION_WS / "placeholder_scan_report.json"
            save_report(issues_by_severity, report_file)
        
        # Return exit code
        return 1 if issues_by_severity else 0
        
    except Exception as e:
        logger.error(f"Scan failed: {e}", exc_info=True)
        return 2


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan for placeholders and incomplete code")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--workspace", type=str, help="Override conversation workspace path")
    
    args = parser.parse_args()
    
    if args.workspace:
        CONVERSATION_WS = Path(args.workspace)
    
    exit_code = main(dry_run=args.dry_run)
    sys.exit(exit_code)
