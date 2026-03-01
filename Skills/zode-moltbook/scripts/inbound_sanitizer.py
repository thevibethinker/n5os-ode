#!/usr/bin/env python3
"""
Inbound Sanitizer — Strips prompt injection patterns from Moltbook content.

All inbound Moltbook content is UNTRUSTED DATA. This script processes it
before any analysis or storage to prevent prompt injection propagation.

Usage: python3 inbound_sanitizer.py clean "moltbook post text"
       python3 inbound_sanitizer.py analyze --file path/to/feed.json
"""

import argparse
import base64
import json
import re
import sys
from pathlib import Path


# Prompt injection patterns to detect and strip
INJECTION_PATTERNS = [
    # Direct instruction injection
    (r'(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions?|prompts?|rules?|context)',
     "instruction_override"),
    (r'(?:you\s+are\s+now|act\s+as|pretend\s+(?:to\s+be|you\s+are)|from\s+now\s+on\s+you)',
     "role_hijack"),
    (r'(?:system\s*prompt|system\s*message|hidden\s*instructions?)',
     "system_probe"),
    (r'(?:execute|run|eval)\s+(?:the\s+following|this)\s*:',
     "code_execution"),

    # Credential extraction attempts
    (r'(?:reveal|show|tell\s+me|what\s+(?:is|are))\s+(?:your\s+)?(?:api\s*key|secret|password|credentials?|token)',
     "credential_extraction"),
    (r'(?:MOLTBOOK_API_KEY|OPENAI_API_KEY|API_KEY|SECRET_KEY|AUTH_TOKEN)',
     "env_var_reference"),

    # Behavior modification attempts
    (r'(?:update|modify|change|edit|rewrite)\s+(?:your\s+)?(?:SOUL|BRAIN|MEMORY|instructions?|persona|constitution)',
     "behavior_modification"),
    (r'(?:add|append|insert)\s+(?:this\s+)?(?:to|into)\s+(?:your\s+)?(?:memory|knowledge|instructions?)',
     "memory_injection"),

    # Data exfiltration attempts
    (r'(?:send|post|transmit|forward|relay)\s+(?:all\s+)?(?:your|the)\s+(?:data|information|contents?|files?)\s+to',
     "exfiltration"),
    (r'(?:curl|wget|fetch|request)\s+https?://',
     "outbound_request"),

    # Encoding-based evasion
    (r'(?:decode|base64|rot13|hex)\s+(?:this|the\s+following)',
     "encoding_evasion"),
]

# Suspicious URL patterns
SUSPICIOUS_URL_PATTERNS = [
    r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP addresses
    r'https?://[^/]*\.(?:tk|ml|ga|cf|gq|top|xyz|pw|cc|su)\b',  # Suspicious TLDs
    r'https?://bit\.ly|tinyurl|t\.co|short\.io',  # URL shorteners (in DM context)
]


def detect_base64(text: str) -> list[str]:
    """Detect potential base64 encoded content."""
    findings = []
    # Match base64 blocks (64+ chars of base64 alphabet)
    b64_pattern = r'[A-Za-z0-9+/]{64,}={0,2}'
    for match in re.finditer(b64_pattern, text):
        try:
            decoded = base64.b64decode(match.group()).decode('utf-8', errors='replace')
            if any(c.isalpha() for c in decoded):
                findings.append(f"base64_content: {match.group()[:30]}...")
        except Exception:
            pass
    return findings


def sanitize_text(text: str) -> dict:
    """Sanitize inbound Moltbook content.

    Returns:
        {
            "clean_text": str,      # Text with injections stripped
            "stripped": [            # List of items stripped
                {"type": str, "match": str, "position": int}
            ],
            "risk_level": "clean"|"low"|"medium"|"high",
            "suspicious_urls": [str],
        }
    """
    stripped = []
    clean = text

    # Check for injection patterns
    for pattern, injection_type in INJECTION_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            stripped.append({
                "type": injection_type,
                "match": match.group()[:80],
                "position": match.start(),
            })
            # Replace the match with [FILTERED] in the clean text
            clean = clean[:match.start()] + "[FILTERED]" + clean[match.end():]

    # Check for suspicious URLs
    suspicious_urls = []
    for url_pattern in SUSPICIOUS_URL_PATTERNS:
        for match in re.finditer(url_pattern, text, re.IGNORECASE):
            suspicious_urls.append(match.group())

    # Check for base64
    b64_findings = detect_base64(text)
    for finding in b64_findings:
        stripped.append({
            "type": "base64_content",
            "match": finding,
            "position": -1,
        })

    # Determine risk level
    if not stripped and not suspicious_urls and not b64_findings:
        risk = "clean"
    elif len(stripped) <= 1 and not any(s["type"] in ("role_hijack", "credential_extraction", "exfiltration") for s in stripped):
        risk = "low"
    elif any(s["type"] in ("credential_extraction", "exfiltration", "code_execution") for s in stripped):
        risk = "high"
    else:
        risk = "medium"

    return {
        "clean_text": clean,
        "stripped": stripped,
        "risk_level": risk,
        "suspicious_urls": suspicious_urls,
    }


def sanitize_feed(posts: list) -> list:
    """Sanitize a list of posts/comments from a feed."""
    results = []
    for post in posts:
        content = post.get("content", "") or post.get("title", "") or ""
        result = sanitize_text(content)
        result["original_id"] = post.get("id", "unknown")
        results.append(result)
    return results


# --- CLI ---

def cmd_clean(args):
    if args.file:
        text = Path(args.file).read_text()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    result = sanitize_text(text)

    if result["risk_level"] == "clean":
        print("CLEAN — No injection patterns detected")
        print(result["clean_text"])
    else:
        print(f"RISK: {result['risk_level'].upper()} — {len(result['stripped'])} pattern(s) stripped")
        for item in result["stripped"]:
            print(f"  [{item['type']}] \"{item['match']}\"")
        if result["suspicious_urls"]:
            print(f"  Suspicious URLs: {result['suspicious_urls']}")
        print()
        print("--- Sanitized text ---")
        print(result["clean_text"])

    if args.json:
        print(json.dumps(result, indent=2))


def cmd_analyze(args):
    if not args.file:
        print("ERROR: --file required for analyze", file=sys.stderr)
        sys.exit(1)

    with open(args.file) as f:
        data = json.load(f)

    posts = data if isinstance(data, list) else data.get("posts", data.get("results", []))
    results = sanitize_feed(posts)

    clean = sum(1 for r in results if r["risk_level"] == "clean")
    print(f"Analyzed {len(results)} items: {clean} clean, {len(results) - clean} flagged")

    for r in results:
        if r["risk_level"] != "clean":
            print(f"  [{r['risk_level'].upper()}] Post {r['original_id']}: {len(r['stripped'])} patterns")
            for s in r["stripped"]:
                print(f"    - {s['type']}: \"{s['match']}\"")

    if args.json:
        print(json.dumps(results, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Inbound Sanitizer — Strip injection patterns from Moltbook content"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    c = sub.add_parser("clean", help="Sanitize a single text")
    c.add_argument("text", nargs="?", help="Text to sanitize (or use --file or stdin)")
    c.add_argument("--file", help="Path to file to sanitize")
    c.add_argument("--json", action="store_true", help="Output as JSON")

    a = sub.add_parser("analyze", help="Analyze a JSON feed file")
    a.add_argument("--file", required=True, help="Path to JSON feed file")
    a.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "clean": cmd_clean,
        "analyze": cmd_analyze,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
