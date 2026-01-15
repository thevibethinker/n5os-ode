#!/usr/bin/env python3
"""
PII Scanner - Detect personally identifiable information in files

Usage:
    pii_scanner.py scan <path> [--recursive] [--auto-mark]
    pii_scanner.py report <path>
    pii_scanner.py patterns

Detects: email addresses, phone numbers, SSN-like patterns, and common name patterns.
Can optionally auto-mark directories containing PII with .n5protected markers.
"""

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Import centralized paths
try:
    from N5.lib.paths import N5_SCRIPTS_DIR, WORKSPACE_ROOT
except ImportError:
    N5_SCRIPTS_DIR = Path("/home/workspace/N5/scripts")
    WORKSPACE_ROOT = Path("/home/workspace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")

# PII detection patterns
PII_PATTERNS = {
    "email": re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    ),
    "phone": re.compile(
        r'\b(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b'
    ),
    "ssn": re.compile(
        r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'
    ),
    "credit_card": re.compile(
        r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'
    ),
    "ip_address": re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    ),
}

# File extensions to scan (text-based)
SCANNABLE_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yaml', '.yml',
    '.md', '.txt', '.csv', '.html', '.xml', '.env', '.sh', '.bash',
    '.conf', '.cfg', '.ini', '.toml', '.sql', '.log'
}

# Directories to skip
SKIP_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv',
    '.next', 'dist', 'build', '.cache'
}


@dataclass
class PIIFinding:
    """A single PII finding in a file"""
    file_path: Path
    line_number: int
    pii_type: str
    matched_text: str
    context: str  # surrounding text for context


@dataclass
class ScanResult:
    """Results from scanning a path"""
    scanned_files: int = 0
    skipped_files: int = 0
    findings: list[PIIFinding] = field(default_factory=list)
    files_with_pii: set[Path] = field(default_factory=set)
    pii_by_type: dict[str, int] = field(default_factory=dict)
    
    def add_finding(self, finding: PIIFinding):
        self.findings.append(finding)
        self.files_with_pii.add(finding.file_path)
        self.pii_by_type[finding.pii_type] = self.pii_by_type.get(finding.pii_type, 0) + 1


def should_scan_file(file_path: Path) -> bool:
    """Check if file should be scanned based on extension"""
    return file_path.suffix.lower() in SCANNABLE_EXTENSIONS


def should_skip_dir(dir_path: Path) -> bool:
    """Check if directory should be skipped"""
    return dir_path.name in SKIP_DIRS


def mask_pii(text: str, pii_type: str) -> str:
    """Mask PII for safe display"""
    if pii_type == "email":
        parts = text.split("@")
        if len(parts) == 2:
            return f"{parts[0][:2]}***@{parts[1]}"
    elif pii_type == "phone":
        return re.sub(r'\d', '*', text)
    elif pii_type == "ssn":
        return "***-**-" + text[-4:]
    elif pii_type == "credit_card":
        return "*" * (len(text) - 4) + text[-4:]
    return text[:3] + "***"


def scan_file(file_path: Path) -> list[PIIFinding]:
    """Scan a single file for PII"""
    findings = []
    
    try:
        content = file_path.read_text(errors='ignore')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pii_type, pattern in PII_PATTERNS.items():
                for match in pattern.finditer(line):
                    # Get context (surrounding characters)
                    start = max(0, match.start() - 20)
                    end = min(len(line), match.end() + 20)
                    context = line[start:end]
                    
                    finding = PIIFinding(
                        file_path=file_path,
                        line_number=line_num,
                        pii_type=pii_type,
                        matched_text=match.group(),
                        context=context
                    )
                    findings.append(finding)
                    
    except Exception as e:
        logger.warning(f"Failed to scan {file_path}: {e}")
    
    return findings


def scan_path(target: Path, recursive: bool = True) -> ScanResult:
    """Scan a file or directory for PII"""
    result = ScanResult()
    
    if target.is_file():
        if should_scan_file(target):
            findings = scan_file(target)
            result.scanned_files = 1
            for f in findings:
                result.add_finding(f)
        else:
            result.skipped_files = 1
    elif target.is_dir():
        if recursive:
            files = list(target.rglob('*'))
        else:
            files = list(target.glob('*'))
        
        for file_path in files:
            if file_path.is_dir():
                if should_skip_dir(file_path):
                    continue
            elif file_path.is_file():
                # Check if any parent is a skip dir
                skip = False
                for parent in file_path.parents:
                    if parent.name in SKIP_DIRS:
                        skip = True
                        break
                    if parent == target:
                        break
                
                if skip:
                    result.skipped_files += 1
                    continue
                    
                if should_scan_file(file_path):
                    findings = scan_file(file_path)
                    result.scanned_files += 1
                    for f in findings:
                        result.add_finding(f)
                else:
                    result.skipped_files += 1
    
    return result


def auto_mark_pii(result: ScanResult) -> int:
    """Auto-mark directories containing PII with .n5protected"""
    import subprocess
    
    marked = 0
    dirs_to_mark = set()
    
    # Group findings by directory
    for file_path in result.files_with_pii:
        dirs_to_mark.add(file_path.parent)
    
    for dir_path in dirs_to_mark:
        # Get PII types found in this directory
        pii_types = set()
        for finding in result.findings:
            if finding.file_path.parent == dir_path:
                pii_types.add(finding.pii_type)
        
        # Map scanner types to n5_protect categories
        category_map = {
            "email": "email",
            "phone": "phone", 
            "ssn": "ssn",
            "credit_card": "financial",
            "ip_address": "address"
        }
        categories = [category_map.get(t, t) for t in pii_types]
        
        # Check if already protected
        marker = dir_path / ".n5protected"
        if marker.exists():
            # Mark as PII if not already
            cmd = [
                "python3", str(N5_SCRIPTS_DIR / "n5_protect.py"),
                "mark-pii", str(dir_path),
                "--categories", ",".join(categories),
                "--note", "Auto-detected by pii_scanner.py"
            ]
        else:
            # Protect and mark PII
            cmd = [
                "python3", str(N5_SCRIPTS_DIR / "n5_protect.py"),
                "protect", str(dir_path),
                "--reason", "Contains PII (auto-detected)",
                "--pii",
                "--pii-categories", ",".join(categories),
                "--pii-note", "Auto-detected by pii_scanner.py"
            ]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=10)
            marked += 1
        except Exception as e:
            logger.warning(f"Failed to mark {dir_path}: {e}")
    
    return marked


def print_report(result: ScanResult, show_findings: bool = True):
    """Print scan results"""
    print("\n" + "=" * 60)
    print("PII SCAN REPORT")
    print("=" * 60)
    
    print(f"\nScanned: {result.scanned_files} files")
    print(f"Skipped: {result.skipped_files} files")
    print(f"Files with PII: {len(result.files_with_pii)}")
    print(f"Total findings: {len(result.findings)}")
    
    if result.pii_by_type:
        print("\nFindings by type:")
        for pii_type, count in sorted(result.pii_by_type.items()):
            print(f"  {pii_type}: {count}")
    
    if show_findings and result.findings:
        print("\n" + "-" * 60)
        print("DETAILED FINDINGS")
        print("-" * 60)
        
        # Group by file
        by_file = {}
        for f in result.findings:
            if f.file_path not in by_file:
                by_file[f.file_path] = []
            by_file[f.file_path].append(f)
        
        for file_path, findings in sorted(by_file.items()):
            rel_path = file_path.relative_to(WORKSPACE) if file_path.is_relative_to(WORKSPACE) else file_path
            print(f"\n📄 {rel_path}")
            
            for f in findings[:5]:  # Limit to 5 per file
                masked = mask_pii(f.matched_text, f.pii_type)
                print(f"   Line {f.line_number}: [{f.pii_type}] {masked}")
            
            if len(findings) > 5:
                print(f"   ... and {len(findings) - 5} more findings")
    
    print("\n" + "=" * 60)


def print_patterns():
    """Print all PII detection patterns"""
    print("\nPII Detection Patterns:")
    print("-" * 40)
    for name, pattern in PII_PATTERNS.items():
        print(f"  {name}: {pattern.pattern}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PII Scanner - Detect personally identifiable information in files"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for PII")
    scan_parser.add_argument("path", type=Path, help="File or directory to scan")
    scan_parser.add_argument("--recursive", "-r", action="store_true", default=True,
                            help="Scan directories recursively (default: True)")
    scan_parser.add_argument("--no-recursive", dest="recursive", action="store_false",
                            help="Don't scan recursively")
    scan_parser.add_argument("--auto-mark", "-a", action="store_true",
                            help="Auto-mark directories with .n5protected")
    scan_parser.add_argument("--json", "-j", action="store_true",
                            help="Output results as JSON")
    
    # report command
    report_parser = subparsers.add_parser("report", help="Generate detailed report")
    report_parser.add_argument("path", type=Path, help="File or directory to report on")
    
    # patterns command
    subparsers.add_parser("patterns", help="Show PII detection patterns")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "scan":
            target = args.path.resolve()
            if not target.exists():
                logger.error(f"Path does not exist: {target}")
                return 1
            
            logger.info(f"Scanning {target}...")
            result = scan_path(target, args.recursive)
            
            if args.json:
                output = {
                    "scanned_files": result.scanned_files,
                    "skipped_files": result.skipped_files,
                    "files_with_pii": [str(p) for p in result.files_with_pii],
                    "pii_by_type": result.pii_by_type,
                    "findings": [
                        {
                            "file": str(f.file_path),
                            "line": f.line_number,
                            "type": f.pii_type,
                            "masked": mask_pii(f.matched_text, f.pii_type)
                        }
                        for f in result.findings
                    ]
                }
                print(json.dumps(output, indent=2))
            else:
                print_report(result)
            
            if args.auto_mark and result.files_with_pii:
                marked = auto_mark_pii(result)
                logger.info(f"✓ Auto-marked {marked} directories with PII")
            
            return 0 if not result.findings else 2  # Return 2 if PII found
            
        elif args.command == "report":
            target = args.path.resolve()
            if not target.exists():
                logger.error(f"Path does not exist: {target}")
                return 1
            
            result = scan_path(target, recursive=True)
            print_report(result, show_findings=True)
            return 0
            
        elif args.command == "patterns":
            print_patterns()
            return 0
            
        else:
            parser.print_help()
            return 1
            
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())


