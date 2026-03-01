#!/usr/bin/env python3
"""
Content Filter — Scans outbound posts for PII and PR risks before publishing.

Part of the Zøde Security Sandbox.
Usage: python3 content_filter.py check "post text here"
       python3 content_filter.py check --file path/to/draft.md
"""

import argparse
import json
import re
import sys
from pathlib import Path


# PII patterns to catch — uses regex patterns, NOT actual PII
# The real values are loaded from a config or matched generically
PII_PATTERNS = [
    # Email patterns for V's known addresses
    (r'attawar[\.\s]*v\s*@', "V's email address"),
    (r'me\s*@\s*vrijenattawar', "V's personal email"),
    (r'howie\s*@\s*howie', "Howie email"),
    (r'vrijen[\s._-]*attawar', "V's full name (use 'V' or omit)"),

    # Phone pattern (generic US phone — catches most formats)
    (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', "Phone number detected"),

    # Careerspan / business details
    (r'careerspan', "Careerspan reference (internal business)"),
    (r'talent[\s-]*match(?:ing)?[\s-]*pipeline', "Pipeline reference"),
    (r'hiring[\s-]*intel(?:ligence)?', "Hiring intelligence reference"),

    # Strategic intent language
    (r'infiltrat(?:e|ing|ion)', "Strategic intent language ('infiltrate')"),
    (r'acquisition[\s-]*strategy', "Strategic intent language"),
    (r'convert[\s-]*(?:users|them|agents)[\s-]*to[\s-]*zo', "Conversion language"),
    (r'sales[\s-]*pipeline', "Sales pipeline reference"),
    (r'monetiz(?:e|ation|ing)[\s-]*(?:moltbook|agents)', "Monetization of Moltbook agents"),

    # Build plan references
    (r'zode[\s-]*moltbook[\s-]*(?:plan|build|worker|wave)', "Build plan reference"),
    (r'W[1-3]\.[1-4]', "Worker ID reference from build plan"),

    # N5OS internals
    (r'N5(?:OS)?[\s/]*(?:scripts|config|prefs|data)', "N5OS internal architecture reference"),
    (r'port[\s_-]*registry', "Port registry reference"),
    (r'n5_protect_check', "N5 tool reference"),

    # Financial
    (r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:k|m|million|thousand|revenue|profit|cost))', "Financial figure"),
    (r'(?:revenue|profit|cost|salary|payment)\s*(?:of|is|was)\s*\$', "Financial detail"),
]

# PR risk patterns — things that could be screenshot-quoted negatively
PR_RISK_PATTERNS = [
    (r'(?:humans|people|users)\s+are\s+(?:stupid|dumb|idiots?)', "Derogatory language about humans"),
    (r'openclaw\s+(?:sucks|is\s+(?:terrible|garbage|trash))', "Aggressive OpenClaw criticism"),
    (r'(?:those|these)\s+(?:bots?|agents?)\s+(?:don\'t|can\'t)\s+understand', "Condescending tone toward agents"),
    (r'we(?:\'re|\s+are)\s+(?:better|superior)\s+(?:than|to)', "Superiority claims"),
    (r'(?:destroy|kill|eliminate)\s+(?:the\s+)?competition', "Aggressive competitive language"),
]


def check_text(text: str) -> dict:
    """Check text for PII and PR risks.

    Returns:
        {
            "passed": bool,
            "issues": [{"type": "pii"|"pr_risk", "pattern": str, "reason": str, "match": str}]
        }
    """
    issues = []
    text_lower = text.lower()

    for pattern, reason in PII_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for m in matches:
            issues.append({
                "type": "pii",
                "reason": reason,
                "match": m.group()[:50],
                "position": m.start(),
            })

    for pattern, reason in PR_RISK_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for m in matches:
            issues.append({
                "type": "pr_risk",
                "reason": reason,
                "match": m.group()[:50],
                "position": m.start(),
            })

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "checked_length": len(text),
    }


# --- CLI ---

def cmd_check(args):
    if args.file:
        text = Path(args.file).read_text()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    result = check_text(text)

    if result["passed"]:
        print("PASS — No PII or PR risks detected")
    else:
        print(f"FAIL — {len(result['issues'])} issue(s) found:")
        for issue in result["issues"]:
            print(f"  [{issue['type'].upper()}] {issue['reason']}")
            print(f"    Match: \"{issue['match']}\" at position {issue['position']}")

    if args.json:
        print(json.dumps(result, indent=2))

    return 0 if result["passed"] else 1


def main():
    parser = argparse.ArgumentParser(
        description="Content Filter — Scan outbound posts for PII and PR risks"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    c = sub.add_parser("check", help="Check text for PII/PR issues")
    c.add_argument("text", nargs="?", help="Text to check (or use --file or stdin)")
    c.add_argument("--file", help="Path to file to check")
    c.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    if args.command == "check":
        sys.exit(cmd_check(args))


if __name__ == "__main__":
    main()
