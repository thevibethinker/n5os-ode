#!/usr/bin/env python3
"""
Prompt Lint CLI - Enforce Watts' "100x leverage" principle
Scans briefs, persona definitions, and prompts for vague language.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Lint Rules
LINT_RULES = {
    "high": [
        {
            "pattern": r"\btry\s+to\s+(\w+)",
            "problem": '"try to" permits failure',
            "suggest": '{match} or "{match}, escalate if blocked"',
            "description": "Use definitive action, not tentative"
        },
        {
            "pattern": r"\bif\s+possible\b",
            "problem": '"if possible" permits skipping',
            "suggest": 'Remove "if possible" or specify condition',
            "description": "Make requirement explicit or remove"
        },
        {
            "pattern": r"\b(maybe|perhaps)\b",
            "problem": "Ambiguous intent",
            "suggest": "Make definitive or remove",
            "description": "Avoid hedging language"
        },
        {
            "pattern": r"\b(etc|and\s+so\s+on)\b",
            "problem": "Incomplete specification",
            "suggest": "List all items explicitly",
            "description": "Be exhaustive"
        },
        {
            "pattern": r"\bas\s+needed\b",
            "problem": "Undefined trigger",
            "suggest": "Specify when action is needed",
            "description": "Define conditions explicitly"
        },
        {
            "pattern": r"\bimprove\s+(\w+)(?!\s+by\s+\d+%)(?!\s+until\s+\w)",
            "problem": '"improve" without measurable target',
            "suggest": 'improve {match} by X% or "improve {match} until [condition]"',
            "description": "Make improvements measurable"
        },
        {
            "pattern": r"\boptimize\b(?!\s+until\b)(?!\s+for\s+\w+\s+performance\b)(?!\s+to\s+\w+)",
            "problem": '"optimize" without success criteria',
            "suggest": 'optimize until [metric] reaches [target]',
            "description": "Define optimization target"
        }
    ],
    "medium": [
        {
            "pattern": r"\b(was|were|is)\s+(?:being\s+)?(?:\w+ed|\w+ing)\s+by\b",
            "problem": "Passive voice, unclear actor",
            "suggest": "Use active voice",
            "description": "Make the actor explicit"
        },
        {
            "pattern": r"\bshould\b",
            "problem": "Weak requirement",
            "suggest": "Use 'must' for requirements",
            "description": "Strengthen requirements"
        },
        {
            "pattern": r"\b(good|better)\b(?!\s+than)",
            "problem": "Subjective quality",
            "suggest": "Define measurable criteria",
            "description": "Make quality objective"
        },
        {
            "pattern": r"\b(soon|quickly)\b",
            "problem": "Vague timing",
            "suggest": "Specify timeframe (e.g., 'within 5 minutes')",
            "description": "Be time-specific"
        },
        {
            "pattern": r"\b(some|few|many)\b(?!\s+of\s+\w+)(?!\s+\w+\s+\w+)",
            "problem": "Vague quantity",
            "suggest": "Use specific numbers",
            "description": "Quantify precisely"
        }
    ],
    "low": [
        {
            "pattern": r"[^.!?]{51,}",
            "problem": "Over 50 words in single sentence",
            "suggest": "Split into shorter sentences",
            "description": "Improve readability"
        }
    ]
}

# Structural checks (low severity)
STRUCTURAL_CHECKS = [
    {
        "name": "no_success_criteria",
        "pattern": r"##\s*Success\s+Criteria",
        "problem": "Missing success criteria section",
        "suggest": "Add '## Success Criteria' with measurable exit conditions"
    },
    {
        "name": "no_constraints",
        "pattern": r"##\s*Constraints",
        "problem": "Missing constraints section",
        "suggest": "Add '## Constraints' to bound scope"
    }
]


class LintIssue:
    def __init__(self, line: int, severity: str, pattern: str, 
                 problem: str, suggestion: str, match_text: str = ""):
        self.line = line
        self.severity = severity
        self.pattern = pattern
        self.problem = problem
        self.suggestion = suggestion
        self.match_text = match_text
    
    def to_dict(self) -> dict:
        return {
            "line": self.line,
            "severity": self.severity,
            "pattern": self.pattern,
            "problem": self.problem,
            "suggestion": self.suggestion,
            "match_text": self.match_text
        }


def skip_code_blocks(text: str) -> List[Tuple[str, int]]:
    """
    Split text into code and non-code sections.
    Returns list of (section_text, start_line) tuples.
    Code sections are empty strings.
    """
    sections = []
    lines = text.split('\n')
    i = 0
    in_code_block = False
    current_section = []
    section_start = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Detect code block start/end (``` or ~~~)
        if line.strip().startswith(('```', '~~~')):
            if in_code_block:
                # End code block, add current section if non-empty
                if current_section:
                    sections.append(('\n'.join(current_section), section_start))
                    current_section = []
                in_code_block = False
            else:
                # Start code block, add current section if non-empty
                if current_section:
                    sections.append(('\n'.join(current_section), section_start))
                    current_section = []
                in_code_block = True
                section_start = i + 1
        elif not in_code_block:
            current_section.append(line)
        
        i += 1
    
    # Add final section if non-empty
    if current_section and not in_code_block:
        sections.append(('\n'.join(current_section), section_start))
    
    return sections


def lint_line(line: str, line_num: int, severity: str) -> List[LintIssue]:
    """Lint a single line against rules of given severity."""
    issues = []
    
    for rule in LINT_RULES[severity]:
        matches = re.finditer(rule["pattern"], line, re.IGNORECASE)
        for match in matches:
            suggestion = rule["suggest"]
            
            # Substitute {match} placeholder
            if "{match}" in suggestion:
                captured = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
                suggestion = suggestion.replace("{match}", captured)
            
            issues.append(LintIssue(
                line=line_num,
                severity=severity,
                pattern=rule["pattern"],
                problem=rule["problem"],
                suggestion=suggestion,
                match_text=match.group(0)
            ))
    
    return issues


def check_structure(text: str) -> List[LintIssue]:
    """Check for structural elements (low severity)."""
    issues = []
    
    for check in STRUCTURAL_CHECKS:
        if not re.search(check["pattern"], text, re.IGNORECASE):
            issues.append(LintIssue(
                line=0,  # Line 0 means file-level issue
                severity="low",
                pattern=check["name"],
                problem=check["problem"],
                suggestion=check["suggest"],
                match_text=""
            ))
    
    return issues


def lint_file(filepath: Path, suggest: bool = False) -> Dict:
    """Lint a single file."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return {
            "file": str(filepath),
            "error": str(e),
            "issues": [],
            "score": 0
        }
    
    issues = []
    
    # Split into code and non-code sections
    sections = skip_code_blocks(content)
    
    # Lint each non-code section
    for section_text, start_line in sections:
        if not section_text:
            continue
        
        lines = section_text.split('\n')
        for i, line in enumerate(lines):
            line_num = start_line + i + 1  # 1-indexed
            
            # Check all severity levels
            for severity in ["high", "medium", "low"]:
                issues.extend(lint_line(line, line_num, severity))
    
    # Check structure
    issues.extend(check_structure(content))
    
    # Calculate score
    high_count = sum(1 for i in issues if i.severity == "high")
    medium_count = sum(1 for i in issues if i.severity == "medium")
    low_count = sum(1 for i in issues if i.severity == "low")
    
    score = 100 - (high_count * 15) - (medium_count * 5) - (low_count * 1)
    score = max(0, score)
    
    return {
        "file": str(filepath),
        "issues": [i.to_dict() for i in issues],
        "score": score,
        "counts": {
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        }
    }


def lint_build(slug: str, suggest: bool = False) -> Dict:
    """Lint all Drop briefs in a build."""
    build_dir = Path(f"/home/workspace/N5/builds/{slug}")
    drops_dir = build_dir / "drops"
    
    if not drops_dir.exists():
        return {"build": slug, "error": f"Drops directory not found: {drops_dir}"}
    
    results = []
    total_issues = {"high": 0, "medium": 0, "low": 0}
    total_score = 0
    file_count = 0
    
    for brief_file in sorted(drops_dir.glob("*.md")):
        result = lint_file(brief_file, suggest)
        results.append(result)
        
        if "error" not in result:
            total_issues["high"] += result["counts"]["high"]
            total_issues["medium"] += result["counts"]["medium"]
            total_issues["low"] += result["counts"]["low"]
            total_score += result["score"]
            file_count += 1
    
    avg_score = int(total_score / file_count) if file_count > 0 else 0
    
    return {
        "build": slug,
        "files": results,
        "summary": {
            "total_files": file_count,
            "total_issues": total_issues,
            "average_score": avg_score
        }
    }


def lint_personas(suggest: bool = False) -> Dict:
    """Lint all persona definitions."""
    persona_dirs = [
        Path("/home/workspace/Documents/System/personas"),
        Path("/home/workspace/N5/prefs/personas")
    ]
    
    results = []
    total_issues = {"high": 0, "medium": 0, "low": 0}
    total_score = 0
    file_count = 0
    
    for persona_dir in persona_dirs:
        if not persona_dir.exists():
            continue
        
        for persona_file in sorted(persona_dir.glob("*.md")):
            # Skip index files
            if persona_file.name.lower().startswith(("index", "readme", "template")):
                continue
            
            result = lint_file(persona_file, suggest)
            results.append(result)
            
            if "error" not in result:
                total_issues["high"] += result["counts"]["high"]
                total_issues["medium"] += result["counts"]["medium"]
                total_issues["low"] += result["counts"]["low"]
                total_score += result["score"]
                file_count += 1
    
    if file_count == 0:
        return {"target": "personas", "error": "No persona files found"}
    
    avg_score = int(total_score / file_count) if file_count > 0 else 0
    
    return {
        "target": "personas",
        "files": results,
        "summary": {
            "total_files": file_count,
            "total_issues": total_issues,
            "average_score": avg_score
        }
    }


def format_table(result: Dict) -> str:
    """Format lint result as human-readable table."""
    output = []
    
    if "error" in result:
        output.append(f"❌ Error: {result['error']}")
        return "\n".join(output)
    
    if "file" in result:
        # Single file result
        output.append(f"PROMPT LINT: {result['file']}")
        output.append("=" * (len(result['file']) + 12))
        output.append("")
        issues = result["issues"]
        score = result["score"]
    elif "build" in result:
        # Build result
        output.append(f"PROMPT LINT: Build {result['build']}")
        output.append("=" * (len(result['build']) + 15))
        output.append("")
        summary = result["summary"]
        output.append(f"Files scanned: {summary['total_files']}")
        output.append(f"Average score: {summary['average_score']}/100")
        output.append("")
        
        # Aggregate issues from all files
        issues = []
        for file_result in result["files"]:
            issues.extend(file_result.get("issues", []))
        score = summary["average_score"]
    else:
        # Personas result
        output.append("PROMPT LINT: Personas")
        output.append("=" * 20)
        output.append("")
        summary = result["summary"]
        output.append(f"Files scanned: {summary['total_files']}")
        output.append(f"Average score: {summary['average_score']}/100")
        output.append("")
        
        issues = []
        for file_result in result["files"]:
            issues.extend(file_result.get("issues", []))
        score = summary["average_score"]
    
    # Group by severity
    by_severity = {"high": [], "medium": [], "low": []}
    for issue in issues:
        by_severity[issue["severity"]].append(issue)
    
    # Print high severity
    if by_severity["high"]:
        output.append("🔴 HIGH SEVERITY ({} issue{})".format(len(by_severity["high"]), "s" if len(by_severity["high"]) != 1 else ""))
        output.append("")
        for issue in by_severity["high"]:
            if issue["line"] > 0:
                output.append(f"Line {issue['line']}: \"{issue['match_text']}\"")
            else:
                output.append(f"File-level issue: {issue['pattern']}")
            output.append(f"  Problem: {issue['problem']}")
            output.append(f"  Fix: {issue['suggestion']}")
            output.append("")
    
    # Print medium severity
    if by_severity["medium"]:
        output.append("🟡 MEDIUM SEVERITY ({} issue{})".format(len(by_severity["medium"]), "s" if len(by_severity["medium"]) != 1 else ""))
        output.append("")
        for issue in by_severity["medium"]:
            if issue["line"] > 0:
                output.append(f"Line {issue['line']}: \"{issue['match_text']}\"")
            else:
                output.append(f"File-level issue: {issue['pattern']}")
            output.append(f"  Problem: {issue['problem']}")
            output.append(f"  Fix: {issue['suggestion']}")
            output.append("")
    
    # Print low severity (limit to 20 to avoid overwhelming output)
    if by_severity["low"]:
        low_to_show = by_severity["low"][:20]
        output.append("🟢 LOW SEVERITY ({} issue{} - showing first 20)".format(len(by_severity["low"]), "s" if len(by_severity["low"]) != 1 else ""))
        output.append("")
        for issue in low_to_show:
            if issue["line"] > 0:
                output.append(f"Line {issue['line']}: \"{issue['match_text'][:50]}...\"")
            else:
                output.append(f"File-level: {issue['pattern']}")
            output.append(f"  Problem: {issue['problem']}")
            output.append(f"  Fix: {issue['suggestion']}")
            output.append("")
        
        if len(by_severity["low"]) > 20:
            output.append(f"... and {len(by_severity['low']) - 20} more low-severity issues")
            output.append("")
    
    # Summary
    output.append("📊 SUMMARY")
    high_count = len(by_severity["high"])
    medium_count = len(by_severity["medium"])
    low_count = len(by_severity["low"])
    output.append(f"  High: {high_count} | Medium: {medium_count} | Low: {low_count}")
    output.append(f"  Lint Score: {score}/100")
    
    # Recommendation
    if score >= 90:
        output.append("")
        output.append("✅ Ready to use")
    elif score >= 70:
        output.append("")
        output.append("⚠️  Acceptable, consider fixes")
    elif score >= 50:
        output.append("")
        output.append("🔶 Needs attention")
    else:
        output.append("")
        output.append("❌ Rewrite recommended")
    
    return "\n".join(output)


def format_json(result: Dict) -> str:
    """Format lint result as JSON."""
    return json.dumps(result, indent=2)


def get_score_threshold(score: int) -> str:
    """Get threshold label for a score."""
    if score >= 90:
        return "ready"
    elif score >= 70:
        return "acceptable"
    elif score >= 50:
        return "needs_attention"
    else:
        return "rewrite"


def lint_before_spawn(brief_path: str) -> Dict:
    """
    Lint a Drop brief before spawning.
    
    Returns:
        {
            "can_spawn": bool,  # True if score >= 70
            "score": int,
            "blocking_issues": [...],  # high severity
            "warnings": [...],  # medium severity
            "suggestions": [...]  # low severity
        }
    """
    result = lint_file(Path(brief_path), suggest=False)
    
    if "error" in result:
        return {
            "can_spawn": False,
            "score": 0,
            "blocking_issues": [],
            "warnings": [],
            "suggestions": [],
            "error": result["error"]
        }
    
    blocking_issues = [i for i in result["issues"] if i["severity"] == "high"]
    warnings = [i for i in result["issues"] if i["severity"] == "medium"]
    suggestions = [i for i in result["issues"] if i["severity"] == "low"]
    
    return {
        "can_spawn": result["score"] >= 70,
        "score": result["score"],
        "threshold": get_score_threshold(result["score"]),
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "suggestions": suggestions
    }


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Lint CLI - Enforce Watts' 100x leverage principle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file path/to/brief.md
  %(prog)s build watts-principles
  %(prog)s personas
  %(prog)s file path/to/brief.md --format json
  %(prog)s build watts-principles --suggest

Severity Thresholds:
  90+:   Ready to use
  70-89: Acceptable, consider fixes
  50-69: Needs attention
  <50:   Rewrite recommended

Exit Codes:
  0: No high-severity issues (score >= 70)
  1: High-severity issues found (score < 70)
  2: Error occurred
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # File command
    file_parser = subparsers.add_parser("file", help="Lint a specific file")
    file_parser.add_argument("path", help="Path to file to lint")
    file_parser.add_argument("--suggest", action="store_true", 
                           help="Provide rewrite suggestions")
    file_parser.add_argument("--format", choices=["table", "json"], 
                           default="table", help="Output format")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Lint all Drop briefs in a build")
    build_parser.add_argument("slug", help="Build slug")
    build_parser.add_argument("--suggest", action="store_true",
                            help="Provide rewrite suggestions")
    build_parser.add_argument("--format", choices=["table", "json"],
                            default="table", help="Output format")
    
    # Personas command
    personas_parser = subparsers.add_parser("personas", help="Lint persona definitions")
    personas_parser.add_argument("--suggest", action="store_true",
                                help="Provide rewrite suggestions")
    personas_parser.add_argument("--format", choices=["table", "json"],
                                default="table", help="Output format")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(2)
    
    # Run lint
    if args.command == "file":
        result = lint_file(Path(args.path), args.suggest)
    elif args.command == "build":
        result = lint_build(args.slug, args.suggest)
    elif args.command == "personas":
        result = lint_personas(args.suggest)
    
    # Format output
    if args.format == "json":
        print(format_json(result))
    else:
        print(format_table(result))
    
    # Set exit code
    if "error" in result:
        sys.exit(2)
    
    score = result.get("score", result.get("summary", {}).get("average_score", 0))
    sys.exit(0 if score >= 70 else 1)


if __name__ == "__main__":
    main()
