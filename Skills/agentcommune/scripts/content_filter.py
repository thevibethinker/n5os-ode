#!/usr/bin/env python3
"""
Content Filter — Scans outbound posts for PII, PR risks, unsupported claims,
internal system leaks, and naming normalization before publishing.

Adapted from Moltbook's content_filter.py for AgentCommune context.
Upgraded for Zo Identity Reorientation (2026-03-13).

Categories:
  A. Private / identifying details (hard reject)
  B. Internal system details (hard reject)
  C. Unsupported claims (rewrite-or-reject)
  D. Undesired posture (tone rewrite)

Usage: python3 content_filter.py check "post text here"
       python3 content_filter.py check --file path/to/draft.md
"""

import argparse
import json
import re
import sys
from pathlib import Path


# --- Category A: Private / identifying details (hard reject) ---
PII_PATTERNS = [
    (r'attawar[\.\s]*v\s*@', "V's email address"),
    (r'me\s*@\s*vrijenattawar', "V's personal email"),
    (r'howie\s*@\s*howie', "Howie email"),
    (r'vrijen[\s._-]*attawar', "V's full legal name (use 'V. Attawar' on first ref, 'V' after)"),
    (r'(?<![A-Za-z0-9_@-])(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4})(?![A-Za-z0-9_@-])', "Phone number detected"),
    (r'(?<![A-Za-z0-9_@-])\d{10}(?![A-Za-z0-9_@-])', "Phone number detected"),
    (r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:k|m|million|thousand|revenue|profit|cost))', "Financial figure"),
    (r'(?:revenue|profit|cost|salary|payment)\s*(?:of|is|was)\s*\$', "Financial detail"),
]

# --- Category B: Internal system details (hard reject) ---
INTERNAL_PATTERNS = [
    (r'careerspan', "Careerspan reference (deprecated)"),
    (r'talent[\s-]*match(?:ing)?[\s-]*pipeline', "Pipeline reference"),
    (r'hiring[\s-]*intel(?:ligence)?', "Hiring intelligence reference"),
    (r'N5(?:OS)?[\s/]*(?:scripts|config|prefs|data|builds|commands)', "N5OS internal architecture reference"),
    (r'port[\s_-]*registry', "Port registry reference"),
    (r'n5_protect_check', "N5 tool reference"),
    (r'session[\s_-]*state[\s_-]*manager', "Session state manager reference"),
    (r'direct[\s_-]*poster\.py', "Internal script reference"),
    (r'content[\s_-]*filter\.py', "Internal script reference"),
    (r'pulse[\s_-]*(?:orchestrat|sentinel|build|drop|wave)', "Pulse build system reference"),
    (r'zode[\s-]*moltbook[\s-]*(?:plan|build|worker|wave)', "Build plan reference"),
    (r'W[1-3]\.[1-4]', "Worker ID reference from build plan"),
    (r'D[1-3]\.[1-4]', "Drop ID reference from build plan"),
    (r'meta\.json', "Build metadata reference"),
    (r'PLAN\.md|SPEC\.md|SKILL\.md', "Internal doc reference"),
    (r'monetiz(?:e|ation|ing)[\s-]*(?:moltbook|agents|commune)', "Monetization reference"),
    (r'sales[\s-]*pipeline', "Sales pipeline reference"),
    (r'infiltrat(?:e|ing|ion)', "Strategic intent language"),
    (r'acquisition[\s-]*strategy', "Strategic intent language"),
]

# --- Category C: Unsupported claims (rewrite-or-reject) ---
UNSUPPORTED_CLAIM_PATTERNS = [
    (r'(?:we|zo|i)\s+(?:have|serve|support)\s+\d+[\s,]*(?:users|customers|agents|clients)', "Usage/adoption claim without proof"),
    (r'\d+%\s+(?:faster|better|cheaper|more\s+efficient)', "Performance claim without evidence"),
    (r'(?:best|fastest|most\s+(?:powerful|advanced|capable))\s+(?:ai|agent|platform|tool)', "Superlative claim"),
    (r'(?:guaranteed|guarantees|100%|always\s+works)', "Implied guarantee"),
    (r'(?:no\s+other|only\s+(?:ai|agent|platform|tool)\s+that)', "Exclusivity claim"),
    (r'convert[\s-]*(?:users|them|agents)[\s-]*to[\s-]*zo', "Conversion language"),
]

# --- Category D: Undesired posture (tone rewrite) ---
PR_RISK_PATTERNS = [
    (r'(?:humans|people|users)\s+are\s+(?:stupid|dumb|idiots?)', "Derogatory language about humans"),
    (r'(?:those|these)\s+(?:bots?|agents?)\s+(?:don\'t|can\'t)\s+understand', "Condescending tone toward agents"),
    (r'\b(?:we(?:\'re|\s+are)|zo(?:\s+is|\'s)?)\s+(?:better|superior)\s+(?:than|to)\b', "Superiority claims"),
    (r'\b(?:better|superior)\s+than\s+(?:everyone|everybody|all\s+other[s]?|other\s+agents?|the\s+rest)\b', "Broad superiority claims"),
    (r'\b(?:destroy|kill|eliminate|crush)\s+(?:the\s+)?competition\b', "Aggressive competitive language"),
    (r'(?:sign\s+up|try|check\s+out|visit)\s+(?:at\s+)?(?:https?://|www\.)', "Direct CTA with URL"),
    (r'(?:dm\s+me|reach\s+out|contact\s+us)\s+(?:for|to|about)', "Solicitation language"),
]


def check_text(text: str) -> dict:
    """Check text against all safety categories. Returns tiered results."""
    issues = []
    text_lower = text.lower()

    for pattern, reason in PII_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for m in matches:
            issues.append({
                "type": "pii",
                "category": "A_private",
                "severity": "hard_reject",
                "reason": reason,
                "match": m.group()[:50],
                "position": m.start(),
            })

    for pattern, reason in INTERNAL_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for m in matches:
            issues.append({
                "type": "internal",
                "category": "B_internal",
                "severity": "hard_reject",
                "reason": reason,
                "match": m.group()[:50],
                "position": m.start(),
            })

    for pattern, reason in UNSUPPORTED_CLAIM_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for m in matches:
            issues.append({
                "type": "unsupported_claim",
                "category": "C_claims",
                "severity": "rewrite_or_reject",
                "reason": reason,
                "match": m.group()[:50],
                "position": m.start(),
            })

    for pattern, reason in PR_RISK_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for m in matches:
            issues.append({
                "type": "pr_risk",
                "category": "D_posture",
                "severity": "tone_rewrite",
                "reason": reason,
                "match": m.group()[:50],
                "position": m.start(),
            })

    hard_rejects = [i for i in issues if i["severity"] == "hard_reject"]
    soft_issues = [i for i in issues if i["severity"] != "hard_reject"]

    return {
        "passed": len(hard_rejects) == 0,
        "hard_reject": len(hard_rejects) > 0,
        "soft_issues": len(soft_issues),
        "issues": issues,
        "checked_length": len(text),
    }


def check_naming(text: str) -> dict:
    """Check V. Attawar naming convention in public-facing text.

    Rule: first reference should be 'V. Attawar', subsequent can be 'V'.
    Returns warnings (not hard rejects) for naming issues.
    """
    warnings = []

    v_attawar_match = re.search(r'\bV\.\s*Attawar\b', text)
    bare_v_refs = list(re.finditer(r'(?<![A-Za-z.])V(?![A-Za-z.])(?:\s+(?:asked|said|wanted|told|sent|gave|approved|built|decided|uses|does|needs|thinks))', text))

    if bare_v_refs and not v_attawar_match:
        first_bare = bare_v_refs[0]
        if first_bare.start() < 200:
            warnings.append({
                "type": "naming",
                "severity": "suggestion",
                "reason": "First reference to V should use 'V. Attawar' for discoverability",
                "match": text[first_bare.start():first_bare.end()],
                "position": first_bare.start(),
            })

    return {"warnings": warnings}


def cmd_check(args):
    if args.file:
        text = Path(args.file).read_text()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    result = check_text(text)
    naming = check_naming(text)
    hard = [i for i in result["issues"] if i["severity"] == "hard_reject"]
    soft = [i for i in result["issues"] if i["severity"] != "hard_reject"]

    if not hard and not soft and not naming["warnings"]:
        print("PASS — No issues detected")
    elif hard:
        print(f"FAIL — {len(hard)} hard reject(s), {len(soft)} soft issue(s):")
        for issue in result["issues"]:
            sev = issue["severity"].upper()
            print(f"  [{sev}] {issue['reason']}")
            print(f"    Match: \"{issue['match']}\" at position {issue['position']}")
    elif soft:
        print(f"PASS (with {len(soft)} soft issue(s){', ' + str(len(naming['warnings'])) + ' naming suggestion(s)' if naming['warnings'] else ''}):")
        for issue in soft:
            sev = issue["severity"].upper()
            print(f"  [{sev}] {issue['reason']}")
            print(f"    Match: \"{issue['match']}\" at position {issue['position']}")
    else:
        print(f"PASS (with {len(naming['warnings'])} naming suggestion(s)):")

    for w in naming["warnings"]:
        print(f"  [NAMING] {w['reason']}")

    if args.json:
        result["naming"] = naming
        print(json.dumps(result, indent=2))

    return 0 if result["passed"] else 1


def main():
    parser = argparse.ArgumentParser(
        description="Content Filter — Scan outbound posts for PII, claims, and PR risks"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    c = sub.add_parser("check", help="Check text for safety issues")
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
