#!/usr/bin/env python3
"""
Impossibility Audit CLI - Scan N5 artifacts for ceiling beliefs and impossibility conclusions.

Part of Watts Principles: Operational tool that scans learnings, deposits, and build artifacts
to flag contamination before it spreads through the system.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

# Import detection logic from impossibility_detector
sys.path.insert(0, str(Path(__file__).parent))
from impossibility_detector import detect_impossibility


# Paths to scan
SYSTEM_LEARNINGS = Path("/home/workspace/N5/learnings/SYSTEM_LEARNINGS.json")
BUILDS_DIR = Path("/home/workspace/N5/builds")


class AuditResult:
    """Container for audit scan results."""
    
    def __init__(self):
        self.high_severity = []
        self.medium_severity = []
        self.low_severity = []
    
    def add_result(self, source: str, text: str, match: Dict[str, Any]):
        """Add a detected match to the appropriate severity bucket."""
        severity = match.get("severity", "low")
        result = {
            "source": source,
            "text": text,
            "match": match["phrase"],
            "pattern": match["pattern"],
            "severity": severity,
            "context": match.get("context", "")
        }
        
        if severity == "high":
            self.high_severity.append(result)
        elif severity == "medium":
            self.medium_severity.append(result)
        else:
            self.low_severity.append(result)
    
    def has_blocking_issues(self) -> bool:
        """Return True if any high-severity issues found."""
        return len(self.high_severity) > 0
    
    def total_count(self) -> int:
        """Total number of issues found."""
        return len(self.high_severity) + len(self.medium_severity) + len(self.low_severity)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary for JSON output."""
        return {
            "high_severity": self.high_severity,
            "medium_severity": self.medium_severity,
            "low_severity": self.low_severity,
            "summary": {
                "high": len(self.high_severity),
                "medium": len(self.medium_severity),
                "low": len(self.low_severity)
            }
        }


def truncate_text(text: str, max_length: int = 80) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def scan_learnings(result: AuditResult):
    """Scan SYSTEM_LEARNINGS.json for impossibility claims."""
    if not SYSTEM_LEARNINGS.exists():
        return
    
    try:
        with open(SYSTEM_LEARNINGS, 'r') as f:
            learnings = json.load(f)
        
        # Learnings is a dict with learning_id keys
        for learning_id, learning_data in learnings.items():
            if not isinstance(learning_data, dict):
                continue
            
            # Get the learning text from various possible fields
            learning_text = ""
            for field in ['content', 'text', 'learning', 'description', 'summary']:
                if field in learning_data and isinstance(learning_data[field], str):
                    learning_text = learning_data[field]
                    break
            
            if not learning_text:
                continue
            
            detection = detect_impossibility(learning_text)
            if detection["has_ceiling_belief"]:
                for match in detection["matches"]:
                    result.add_result(
                        f"SYSTEM_LEARNINGS.json ({learning_id})",
                        truncate_text(learning_text),
                        match
                    )
    except Exception as e:
        print(f"Warning: Could not scan SYSTEM_LEARNINGS.json: {e}", file=sys.stderr)


def scan_deposits(build_slug: str = None, result: AuditResult = None):
    """Scan build deposits for impossibility claims."""
    if result is None:
        result = AuditResult()
    
    if not BUILDS_DIR.exists():
        return result
    
    # Filter builds by slug if provided
    build_dirs = [BUILDS_DIR / build_slug] if build_slug else BUILDS_DIR.iterdir()
    
    for build_dir in build_dirs:
        if not build_dir.is_dir():
            continue
        
        deposits_dir = build_dir / "deposits"
        if not deposits_dir.exists():
            continue
        
        for deposit_file in deposits_dir.glob("*.json"):
            try:
                with open(deposit_file, 'r') as f:
                    deposit = json.load(f)
                
                # Scan various fields that might contain conclusions
                texts_to_scan = []
                for field in ['summary', 'notes_for_orchestrator', 'decisions', 'artifacts', 'notes']:
                    if field in deposit:
                        if isinstance(deposit[field], str):
                            texts_to_scan.append(deposit[field])
                        elif isinstance(deposit[field], list):
                            texts_to_scan.extend([str(t) for t in deposit[field]])
                
                for text in texts_to_scan:
                    if not text.strip():
                        continue
                    
                    detection = detect_impossibility(text)
                    if detection["has_ceiling_belief"]:
                        for match in detection["matches"]:
                            result.add_result(
                                f"{deposit_file.relative_to(BUILDS_DIR.parent)}",
                                truncate_text(text),
                                match
                            )
            except Exception as e:
                print(f"Warning: Could not scan {deposit_file}: {e}", file=sys.stderr)
    
    return result


def scan_build_lessons(build_slug: str = None, result: AuditResult = None):
    """Scan BUILD_LESSONS.json files for impossibility claims."""
    if result is None:
        result = AuditResult()
    
    if not BUILDS_DIR.exists():
        return result
    
    build_dirs = [BUILDS_DIR / build_slug] if build_slug else BUILDS_DIR.iterdir()
    
    for build_dir in build_dirs:
        if not build_dir.is_dir():
            continue
        
        lessons_file = build_dir / "BUILD_LESSONS.json"
        if not lessons_file.exists():
            continue
        
        try:
            with open(lessons_file, 'r') as f:
                lessons = json.load(f)
            
            # Lessons is a dict with lesson_id keys
            for lesson_id, lesson_data in lessons.items():
                if not isinstance(lesson_data, dict):
                    continue
                
                # Scan lesson text
                lesson_text = ""
                for field in ['content', 'text', 'lesson', 'description', 'finding']:
                    if field in lesson_data and isinstance(lesson_data[field], str):
                        lesson_text = lesson_data[field]
                        break
                
                if not lesson_text:
                    continue
                
                detection = detect_impossibility(lesson_text)
                if detection["has_ceiling_belief"]:
                    for match in detection["matches"]:
                        result.add_result(
                            f"{lessons_file.relative_to(BUILDS_DIR.parent)} ({lesson_id})",
                            truncate_text(lesson_text),
                            match
                        )
        except Exception as e:
            print(f"Warning: Could not scan {lessons_file}: {e}", file=sys.stderr)
    
    return result


def scan_file_or_path(path: str, result: AuditResult = None):
    """Scan arbitrary file or directory."""
    if result is None:
        result = AuditResult()
    
    path_obj = Path(path)
    
    if not path_obj.exists():
        print(f"Error: Path not found: {path}", file=sys.stderr)
        return result
    
    if path_obj.is_file():
        # Scan single file
        try:
            with open(path_obj, 'r') as f:
                content = f.read()
            
            detection = detect_impossibility(content)
            if detection["has_ceiling_belief"]:
                for match in detection["matches"]:
                    result.add_result(
                        str(path_obj.relative_to(BUILDS_DIR.parent) if path_obj.is_relative_to(BUILDS_DIR.parent) else str(path_obj)),
                        truncate_text(content),
                        match
                    )
        except Exception as e:
            print(f"Warning: Could not scan {path}: {e}", file=sys.stderr)
    
    elif path_obj.is_dir():
        # Scan directory recursively
        for file_path in path_obj.rglob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                detection = detect_impossibility(content)
                if detection["has_ceiling_belief"]:
                    for match in detection["matches"]:
                        result.add_result(
                            str(file_path.relative_to(BUILDS_DIR.parent) if file_path.is_relative_to(BUILDS_DIR.parent) else str(file_path)),
                            truncate_text(content),
                            match
                        )
            except Exception as e:
                print(f"Warning: Could not scan {file_path}: {e}", file=sys.stderr)
    
    return result


def format_table(result: AuditResult) -> str:
    """Format results as ASCII table."""
    output = []
    
    output.append("IMPOSSIBILITY AUDIT RESULTS")
    output.append("=" * 60)
    output.append("")
    
    if result.total_count() == 0:
        output.append("✅ No ceiling beliefs or impossibility claims detected.")
        output.append("")
        output.append("=" * 60)
        return "\n".join(output)
    
    # High severity
    if result.high_severity:
        output.append(f"🔴 HIGH SEVERITY ({len(result.high_severity)} found)")
        for i, r in enumerate(result.high_severity, 1):
            output.append("┌" + "─" * 63 + "┐")
            output.append(f"│ Source: {r['source'][:58]:<58} │")
            output.append(f"│ Text: \"{r['text'][:55]}\"... │")
            output.append(f"│ Match: \"{r['match']}\" │")
            output.append(f"│ Action: REVIEW REQUIRED - Consider invalidating or disputing │")
            output.append("└" + "─" * 63 + "┘")
            output.append("")
    
    # Medium severity
    if result.medium_severity:
        output.append(f"🟡 MEDIUM SEVERITY ({len(result.medium_severity)} found)")
        for i, r in enumerate(result.medium_severity, 1):
            output.append("┌" + "─" * 63 + "┐")
            output.append(f"│ Source: {r['source'][:58]:<58} │")
            output.append(f"│ Text: \"{r['text'][:55]}\"... │")
            output.append(f"│ Match: \"{r['match']}\" │")
            output.append(f"│ Action: VERIFY - May be accurate, but confirm with fresh context │")
            output.append("└" + "─" * 63 + "┘")
            output.append("")
    
    # Low severity
    if result.low_severity:
        output.append(f"🟢 LOW SEVERITY ({len(result.low_severity)} found)")
        for i, r in enumerate(result.low_severity, 1):
            output.append("┌" + "─" * 63 + "┐")
            output.append(f"│ Source: {r['source'][:58]:<58} │")
            output.append(f"│ Text: \"{r['text'][:55]}\"... │")
            output.append(f"│ Match: \"{r['match']}\" │")
            output.append(f"│ Action: NOTE - Low confidence, may be worth exploring │")
            output.append("└" + "─" * 63 + "┘")
            output.append("")
    
    # Summary
    summary = result.to_dict()["summary"]
    output.append(f"Summary: {summary['high']} high, {summary['medium']} medium, {summary['low']} low")
    
    if summary['high'] > 0:
        output.append("Recommendation: Review high-severity items before next build")
    else:
        output.append("Recommendation: No blocking issues, but review medium/low for learning")
    
    output.append("")
    output.append("=" * 60)
    
    return "\n".join(output)


def format_markdown(result: AuditResult) -> str:
    """Format results as Markdown."""
    output = []
    
    output.append("# Impossibility Audit Results")
    output.append("")
    
    if result.total_count() == 0:
        output.append("✅ No ceiling beliefs or impossibility claims detected.")
        return "\n".join(output)
    
    # High severity
    if result.high_severity:
        output.append("## 🔴 High Severity")
        for i, r in enumerate(result.high_severity, 1):
            output.append(f"### {i}. {r['source']}")
            output.append(f"- **Match:** \"{r['match']}\"")
            output.append(f"- **Text:** \"{r['text']}...\"")
            output.append(f"- **Action:** REVIEW REQUIRED - Consider invalidating or disputing")
            output.append("")
    
    # Medium severity
    if result.medium_severity:
        output.append("## 🟡 Medium Severity")
        for i, r in enumerate(result.medium_severity, 1):
            output.append(f"### {i}. {r['source']}")
            output.append(f"- **Match:** \"{r['match']}\"")
            output.append(f"- **Text:** \"{r['text']}...\"")
            output.append(f"- **Action:** VERIFY - May be accurate, but confirm with fresh context")
            output.append("")
    
    # Low severity
    if result.low_severity:
        output.append("## 🟢 Low Severity")
        for i, r in enumerate(result.low_severity, 1):
            output.append(f"### {i}. {r['source']}")
            output.append(f"- **Match:** \"{r['match']}\"")
            output.append(f"- **Text:** \"{r['text']}...\"")
            output.append(f"- **Action:** NOTE - Low confidence, may be worth exploring")
            output.append("")
    
    # Summary
    summary = result.to_dict()["summary"]
    output.append("## Summary")
    output.append(f"- High: {summary['high']}")
    output.append(f"- Medium: {summary['medium']}")
    output.append(f"- Low: {summary['low']}")
    output.append("")
    
    if summary['high'] > 0:
        output.append("**Recommendation:** Review high-severity items before next build")
    else:
        output.append("**Recommendation:** No blocking issues, but review medium/low for learning")
    
    return "\n".join(output)


def audit_before_build(slug: str) -> Dict[str, Any]:
    """
    Run audit and return blocking issues for Pulse integration.
    
    Args:
        slug: Build slug to audit
        
    Returns:
        {
            "can_proceed": bool,
            "blocking_issues": list of high-severity findings,
            "warnings": list of medium-severity findings
        }
    """
    result = AuditResult()
    
    # Scan learnings
    scan_learnings(result)
    
    # Scan build deposits and lessons
    scan_deposits(slug, result)
    scan_build_lessons(slug, result)
    
    return {
        "can_proceed": len(result.high_severity) == 0,
        "blocking_issues": result.high_severity,
        "warnings": result.medium_severity,
        "summary": {
            "high": len(result.high_severity),
            "medium": len(result.medium_severity),
            "low": len(result.low_severity)
        }
    }


def cmd_learnings(args):
    """Handle the 'learnings' subcommand."""
    result = AuditResult()
    scan_learnings(result)
    output_and_exit(result, args.format)


def cmd_build(args):
    """Handle the 'build' subcommand."""
    if not args.slug:
        print("Error: build subcommand requires a slug", file=sys.stderr)
        sys.exit(1)
    
    result = AuditResult()
    scan_deposits(args.slug, result)
    scan_build_lessons(args.slug, result)
    output_and_exit(result, args.format)


def cmd_builds(args):
    """Handle the 'builds' subcommand."""
    result = AuditResult()
    scan_deposits(result=result)
    scan_build_lessons(result=result)
    output_and_exit(result, args.format)


def cmd_file(args):
    """Handle the 'file' subcommand."""
    if not args.path:
        print("Error: file subcommand requires a path", file=sys.stderr)
        sys.exit(1)
    
    result = AuditResult()
    scan_file_or_path(args.path, result)
    output_and_exit(result, args.format)


def cmd_all(args):
    """Handle the 'all' subcommand."""
    result = AuditResult()
    scan_learnings(result)
    scan_deposits(result=result)
    scan_build_lessons(result=result)
    output_and_exit(result, args.format)


def output_and_exit(result: AuditResult, format_type: str):
    """Output results and exit with appropriate code."""
    if format_type == "json":
        print(json.dumps(result.to_dict(), indent=2))
    elif format_type == "markdown":
        print(format_markdown(result))
    else:  # table (default)
        print(format_table(result))
    
    # Exit code: 0 if no high-severity, 1 if high-severity found
    sys.exit(1 if result.has_blocking_issues() else 0)


def main():
    parser = argparse.ArgumentParser(
        description="Impossibility Audit - Scan N5 artifacts for ceiling beliefs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s learnings                           # Scan all learnings
  %(prog)s build pulse-v2                     # Scan specific build deposits
  %(prog)s builds                             # Scan all builds
  %(prog)s file path/to/file.json             # Scan arbitrary file
  %(prog)s all                                # Full system scan
  %(prog)s all --format json                  # Output as JSON
  %(prog)s all --format markdown              # Output as Markdown
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Scan target")
    
    # Common arguments for all subcommands
    def add_format_arg(subparser):
        subparser.add_argument(
            "--format", "-f",
            choices=["table", "json", "markdown"],
            default="table",
            help="Output format (default: table)"
        )
    
    # Learnings subcommand
    learnings_parser = subparsers.add_parser("learnings", help="Scan SYSTEM_LEARNINGS.json")
    add_format_arg(learnings_parser)
    learnings_parser.set_defaults(func=cmd_learnings)
    
    # Build subcommand
    build_parser = subparsers.add_parser("build", help="Scan specific build deposits")
    add_format_arg(build_parser)
    build_parser.add_argument("slug", help="Build slug to scan")
    build_parser.set_defaults(func=cmd_build)
    
    # Builds subcommand
    builds_parser = subparsers.add_parser("builds", help="Scan all build deposits")
    add_format_arg(builds_parser)
    builds_parser.set_defaults(func=cmd_builds)
    
    # File subcommand
    file_parser = subparsers.add_parser("file", help="Scan arbitrary file or directory")
    add_format_arg(file_parser)
    file_parser.add_argument("path", help="Path to file or directory")
    file_parser.set_defaults(func=cmd_file)
    
    # All subcommand
    all_parser = subparsers.add_parser("all", help="Full system scan")
    add_format_arg(all_parser)
    all_parser.set_defaults(func=cmd_all)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
