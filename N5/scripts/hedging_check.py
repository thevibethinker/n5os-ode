#!/usr/bin/env python3
"""
Hedging Pattern Checker

Scans text for hedging anti-patterns defined in the directness calibration system.
Can be used as validation step in any communications workflow.

Usage:
  python3 N5/scripts/hedging_check.py "text to check"
  python3 N5/scripts/hedging_check.py --file path/to/file.md
  python3 N5/scripts/hedging_check.py --stdin < file.txt
  
Output:
  JSON with hedging violations found and directness score estimate.
"""

import sys
import re
import json
import argparse
from pathlib import Path

HEDGING_PATTERNS = [
    # Category 1: Qualifier Hedges
    {"pattern": r"\bjust\s+wanted\b", "category": "qualifier", "severity": "high", "fix": "Delete 'just', make the point"},
    {"pattern": r"\bjust\s+checking\b", "category": "qualifier", "severity": "high", "fix": "Delete 'just'"},
    {"pattern": r"\bjust\s+following\b", "category": "qualifier", "severity": "medium", "fix": "Delete 'just'"},
    {"pattern": r"\bmaybe\s+we\s+could\b", "category": "qualifier", "severity": "high", "fix": "Make the recommendation"},
    {"pattern": r"\bperhaps\s+(we|you|it)\b", "category": "qualifier", "severity": "medium", "fix": "Be direct"},
    {"pattern": r"\bmight\s+be\s+good\b", "category": "qualifier", "severity": "medium", "fix": "State directly"},
    {"pattern": r"\bkind\s+of\b", "category": "qualifier", "severity": "medium", "fix": "Be specific"},
    {"pattern": r"\bsort\s+of\b", "category": "qualifier", "severity": "medium", "fix": "Be specific"},
    {"pattern": r"\ba\s+little\s+bit\b", "category": "qualifier", "severity": "low", "fix": "Quantify or remove"},
    {"pattern": r"\bsomewhat\b", "category": "qualifier", "severity": "low", "fix": "Be specific"},
    
    # Category 2: Uncertainty Hedges (when you actually know)
    {"pattern": r"\bi\s+think\s+maybe\b", "category": "uncertainty", "severity": "high", "fix": "Pick one or neither"},
    {"pattern": r"\bi\s+was\s+wondering\s+if\b", "category": "uncertainty", "severity": "high", "fix": "Ask the question directly"},
    {"pattern": r"\bi\s+believe\s+that\s+perhaps\b", "category": "uncertainty", "severity": "high", "fix": "Assert or don't"},
    {"pattern": r"\bit\s+seems\s+like\s+maybe\b", "category": "uncertainty", "severity": "high", "fix": "State observation directly"},
    
    # Category 3: Permission-Seeking
    {"pattern": r"\bfeel\s+free\s+to\b", "category": "permission", "severity": "high", "fix": "Make the ask directly"},
    {"pattern": r"\bif\s+you\s+have\s+time\b", "category": "permission", "severity": "high", "fix": "Propose a time or don't"},
    {"pattern": r"\bif\s+you\s+don't\s+mind\b", "category": "permission", "severity": "medium", "fix": "Make the request"},
    {"pattern": r"\bwhenever\s+you\s+(have|get)\s+(a\s+)?chance\b", "category": "permission", "severity": "high", "fix": "Name timeline"},
    {"pattern": r"\bif\s+it's\s+not\s+too\s+much\s+trouble\b", "category": "permission", "severity": "medium", "fix": "Just ask"},
    {"pattern": r"\bonly\s+if\s+you\s+want\b", "category": "permission", "severity": "medium", "fix": "Make the ask"},
    
    # Category 4: Pressure Deferrers
    {"pattern": r"\bno\s+rush\b", "category": "pressure", "severity": "high", "fix": "Name timeline or stay silent"},
    {"pattern": r"\bno\s+pressure\b", "category": "pressure", "severity": "medium", "fix": "There usually is; be honest"},
    {"pattern": r"\btake\s+your\s+time\b", "category": "pressure", "severity": "medium", "fix": "Unless you mean it"},
    {"pattern": r"\bwhenever\s+you\s+have\s+time\b", "category": "pressure", "severity": "high", "fix": "Name the timeline"},
    {"pattern": r"\bwhen\s+you\s+get\s+a\s+chance\b", "category": "pressure", "severity": "medium", "fix": "Propose specific time"},
    
    # Category 5: Self-Diminishing
    {"pattern": r"\bsorry\s+to\s+bother\b", "category": "diminishing", "severity": "high", "fix": "Don't apologize for existing"},
    {"pattern": r"\bi\s+don't\s+want\s+to\s+take\s+too\s+much\b", "category": "diminishing", "severity": "medium", "fix": "Get to the point"},
    {"pattern": r"\bthis\s+is\s+probably\s+a\s+dumb\s+question\b", "category": "diminishing", "severity": "high", "fix": "Ask the question"},
    {"pattern": r"\bi\s+could\s+be\s+wrong\s+but\b", "category": "diminishing", "severity": "medium", "fix": "State your view"},
    {"pattern": r"\bi'm\s+not\s+sure\s+if\s+this\s+is\s+right\b", "category": "diminishing", "severity": "medium", "fix": "State your view or ask directly"},
    
    # Category 6: Validation-Seeking
    {"pattern": r"\bdoes\s+that\s+make\s+sense\b", "category": "validation", "severity": "high", "fix": "Assume it does"},
    {"pattern": r"\bif\s+that\s+makes\s+sense\b", "category": "validation", "severity": "medium", "fix": "Assume it does"},
    {"pattern": r"\bam\s+i\s+making\s+sense\b", "category": "validation", "severity": "medium", "fix": "Trust your communication"},
    {"pattern": r"\blet\s+me\s+know\s+if\s+that\s+makes\s+sense\b", "category": "validation", "severity": "medium", "fix": "Assume clarity"},
]

def check_text(text: str) -> dict:
    """Check text for hedging patterns and return analysis."""
    text_lower = text.lower()
    violations = []
    
    for pattern_def in HEDGING_PATTERNS:
        matches = list(re.finditer(pattern_def["pattern"], text_lower))
        for match in matches:
            # Find the line number
            line_start = text_lower.rfind('\n', 0, match.start()) + 1
            line_num = text_lower[:match.start()].count('\n') + 1
            
            violations.append({
                "match": match.group(),
                "line": line_num,
                "category": pattern_def["category"],
                "severity": pattern_def["severity"],
                "fix": pattern_def["fix"],
                "context": text[max(0, match.start()-30):min(len(text), match.end()+30)]
            })
    
    # Calculate directness score estimate
    word_count = len(text.split())
    high_severity = sum(1 for v in violations if v["severity"] == "high")
    medium_severity = sum(1 for v in violations if v["severity"] == "medium")
    low_severity = sum(1 for v in violations if v["severity"] == "low")
    
    # Penalty calculation (per 100 words)
    penalty = (high_severity * 0.15 + medium_severity * 0.08 + low_severity * 0.03)
    words_factor = max(1, word_count / 100)
    adjusted_penalty = penalty / words_factor
    
    directness_score = max(0, min(1, 1.0 - adjusted_penalty))
    
    return {
        "violations": violations,
        "violation_count": len(violations),
        "by_severity": {
            "high": high_severity,
            "medium": medium_severity,
            "low": low_severity
        },
        "by_category": {
            cat: sum(1 for v in violations if v["category"] == cat)
            for cat in set(v["category"] for v in violations)
        },
        "word_count": word_count,
        "directness_score": round(directness_score, 2),
        "pass": directness_score >= 0.7 and high_severity == 0,
        "recommendation": get_recommendation(directness_score, violations)
    }

def get_recommendation(score: float, violations: list) -> str:
    """Get actionable recommendation based on analysis."""
    high_count = sum(1 for v in violations if v["severity"] == "high")
    
    if score >= 0.85 and high_count == 0:
        return "✓ Text passes directness check. Ready to send."
    elif score >= 0.7 and high_count <= 1:
        return f"⚠️ Minor hedging detected. Fix {high_count} high-severity issue(s) before sending."
    elif score >= 0.5:
        return f"⚠️ Moderate hedging. Review {high_count} high-severity patterns and tighten language."
    else:
        return f"✗ Significant hedging detected. Rewrite with more direct language. {high_count} high-severity issues."

def main():
    parser = argparse.ArgumentParser(description="Check text for hedging patterns")
    parser.add_argument("text", nargs="?", help="Text to check")
    parser.add_argument("--file", "-f", help="File to check")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed violations")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    # Get text to check
    if args.stdin:
        text = sys.stdin.read()
    elif args.file:
        text = Path(args.file).read_text()
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        sys.exit(1)
    
    # Run analysis
    result = check_text(text)
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n📊 Hedging Analysis")
        print(f"{'='*50}")
        print(f"Word count: {result['word_count']}")
        print(f"Directness score: {result['directness_score']:.0%}")
        print(f"Violations: {result['violation_count']} ({result['by_severity']['high']} high, {result['by_severity']['medium']} medium, {result['by_severity']['low']} low)")
        print(f"\n{result['recommendation']}")
        
        if args.verbose and result['violations']:
            print(f"\n📋 Violations:")
            for v in result['violations']:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "⚪"}[v['severity']]
                print(f"  {severity_icon} Line {v['line']}: \"{v['match']}\" ({v['category']})")
                print(f"     Fix: {v['fix']}")
    
    # Exit code based on pass/fail
    sys.exit(0 if result['pass'] else 1)

if __name__ == "__main__":
    main()

