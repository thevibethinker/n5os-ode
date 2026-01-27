#!/usr/bin/env python3
"""
Impossibility Detector - Core detection logic for ceiling beliefs and impossibility conclusions.

Part of Watts Principles: Anti-contamination layer that detects when agents conclude
something is "impossible" or "optimized to the limit" before these beliefs propagate.
"""

import re
import json
import argparse
import sys
from typing import List, Dict, Tuple
from pathlib import Path


# Pattern definitions with severity levels
PATTERNS = {
    "high": [
        r"impossible to",
        r"cannot be done",
        r"mathematically impossible",
        r"proven to be impossible",
        r"fundamentally impossible",
        r"no way to",
        r"will never work",
        r"physically impossible",
        r"theoretically impossible",
        r"logically impossible",
        r"cannot achieve",
        r"can't be done",
        r"won't work",
    ],
    "medium": [
        r"hit the ceiling",
        r"reached the limit",
        r"maximum possible",
        r"no further optimization",
        r"fully optimized",
        r"at the theoretical limit",
        r"cannot improve beyond",
        r"best possible",
        r"optimal solution found",
        r"diminishing returns",
        r"law of diminishing",
        r"maximum achievable",
        r"reached maximum",
    ],
    "low": [
        r"unlikely to work",
        r"probably won't",
        r"doubt it's possible",
        r"seems impossible",
        r"appears to be the limit",
        r"I don't see how",
        r"can't imagine a way",
        r"seems unlikely",
        r"appears impossible",
    ]
}

# Recommendations based on severity and confidence
RECOMMENDATIONS = {
    "high": {
        "high": "CRITICAL: Definitive impossibility claim detected. Flag for human review and prevent propagation.",
        "medium": "WARNING: Strong impossibility claim. Recommend human verification before accepting.",
        "low": "CAUTION: Possible impossibility claim. Verify with additional context."
    },
    "medium": {
        "high": "WARNING: Ceiling/limit claim. Confirm if this is a genuine constraint or premature conclusion.",
        "medium": "NOTE: Optimization limit stated. Verify if alternative approaches exist.",
        "low": "INFO: Limit mentioned. Worth exploring alternatives."
    },
    "low": {
        "high": "INFO: Pessimistic speculation. Consider alternative perspectives.",
        "medium": "INFO: Doubt expressed. Not a firm conclusion.",
        "low": "INFO: Subjective uncertainty. Not a blocker."
    }
}


def extract_context(text: str, match_start: int, match_end: int, window: int = 50) -> str:
    """Extract surrounding context for a match."""
    start = max(0, match_start - window)
    end = min(len(text), match_end + window)
    return text[start:end]


def detect_impossibility(text: str) -> Dict:
    """
    Analyze text for ceiling beliefs and impossibility conclusions.

    Args:
        text: The text to analyze

    Returns:
        {
            "has_ceiling_belief": bool,
            "confidence": float,  # 0.0-1.0
            "matches": [
                {
                    "phrase": "matched text",
                    "pattern": "which pattern matched",
                    "severity": "high|medium|low",
                    "context": "surrounding text"
                }
            ],
            "recommendation": "string"  # what to do about it
        }
    """
    text_lower = text.lower()
    matches = []
    max_severity_score = 0

    for severity, patterns in PATTERNS.items():
        for pattern in patterns:
            # Find all matches for this pattern
            regex = re.compile(re.escape(pattern), re.IGNORECASE)
            for match in regex.finditer(text):
                # Skip if already captured by a higher severity pattern
                match_start = match.start()
                match_end = match.end()
                already_captured = False

                for existing_match in matches:
                    existing_start = existing_match["start_pos"]
                    existing_end = existing_start + len(existing_match["phrase"])
                    # Check if this match overlaps with an existing higher-severity match
                    if match_start < existing_end and match_end > existing_start:
                        already_captured = True
                        break

                if already_captured:
                    continue

                context = extract_context(text, match_start, match_end)
                matches.append({
                    "phrase": match.group(),
                    "pattern": pattern,
                    "severity": severity,
                    "context": context,
                    "start_pos": match_start
                })

    # Calculate overall confidence based on number and severity of matches
    if not matches:
        return {
            "has_ceiling_belief": False,
            "confidence": 0.0,
            "matches": [],
            "recommendation": "No ceiling beliefs or impossibility claims detected."
        }

    # Calculate severity score
    severity_weights = {"high": 1.0, "medium": 0.6, "low": 0.3}
    for match in matches:
        severity_score = severity_weights.get(match["severity"], 0)
        if severity_score > max_severity_score:
            max_severity_score = severity_score

    # Confidence increases with more matches
    match_count = len(matches)
    base_confidence = min(0.9, 0.4 + (match_count * 0.1))
    confidence = min(1.0, base_confidence * (0.5 + max_severity_score))

    # Determine primary severity for recommendation
    primary_severity = max(m["severity"] for m in matches)
    confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
    recommendation = RECOMMENDATIONS.get(primary_severity, {}).get(confidence_level, "Review for ceiling beliefs.")

    # Remove start_pos from output (internal only)
    for match in matches:
        del match["start_pos"]

    return {
        "has_ceiling_belief": True,
        "confidence": round(confidence, 2),
        "matches": matches,
        "recommendation": recommendation
    }


def detect_impossibility_semantic(text: str) -> Dict:
    """
    Use LLM to detect subtle ceiling beliefs not caught by patterns.

    This is a fallback for ambiguous cases where pattern matching is insufficient.

    Args:
        text: The text to analyze

    Returns:
        Same structure as detect_impossibility()
    """
    import os
    import requests

    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", ""),
                "content-type": "application/json"
            },
            json={
                "input": f"""Analyze this text for ceiling beliefs or impossibility conclusions:

{text}

Respond with a JSON object in this format:
{{
    "has_ceiling_belief": boolean,
    "confidence": number (0.0-1.0),
    "matches": [
        {{
            "phrase": "exact quote of problematic phrase",
            "pattern": "description of why this is a ceiling belief",
            "severity": "high|medium|low",
            "context": "brief context"
        }}
    ],
    "recommendation": "brief recommendation"
}}

Focus on:
1. Definitive impossibility claims (high severity)
2. Optimization ceiling or limit claims (medium severity)
3. Pessimistic speculation (low severity)"""
            },
            timeout=30
        )

        result = response.json()
        output = result.get("output", {})

        # Try to parse JSON from LLM response
        if isinstance(output, str):
            # Try to extract JSON from the response
            json_match = re.search(r'\{[^}]+\}', output, re.DOTALL)
            if json_match:
                try:
                    output = json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

        return output if isinstance(output, dict) else {
            "has_ceiling_belief": False,
            "confidence": 0.0,
            "matches": [],
            "recommendation": "Semantic analysis failed or returned invalid format."
        }

    except Exception as e:
        return {
            "has_ceiling_belief": False,
            "confidence": 0.0,
            "matches": [],
            "recommendation": f"Semantic analysis error: {str(e)}"
        }


def print_patterns():
    """Print all detection patterns organized by severity."""
    print("Impossibility Detection Patterns")
    print("=" * 50)
    for severity, patterns in PATTERNS.items():
        print(f"\n{severity.upper()} SEVERITY:")
        for pattern in patterns:
            print(f"  - {pattern}")


def cmd_check(args):
    """Handle the 'check' subcommand."""
    text = args.text

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        text = file_path.read_text()

    if not text.strip():
        print("Error: No text to analyze", file=sys.stderr)
        sys.exit(1)

    # Use semantic analysis if requested
    if args.semantic:
        result = detect_impossibility_semantic(text)
    else:
        result = detect_impossibility(text)

    # Output
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 60)
        print("IMPOSSIBILITY DETECTION RESULTS")
        print("=" * 60)

        if result["has_ceiling_belief"]:
            print(f"\n🚨 CEILING BELIEF DETECTED")
            print(f"Confidence: {result['confidence']:.0%}")
            print(f"\nRecommendation: {result['recommendation']}\n")

            if result["matches"]:
                print(f"Found {len(result['matches'])} match(es):")
                print("-" * 60)
                for i, match in enumerate(result["matches"], 1):
                    severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[match["severity"]]
                    print(f"\n{i}. {severity_icon} {match['severity'].upper()}")
                    print(f"   Phrase: \"{match['phrase']}\"")
                    print(f"   Pattern: {match['pattern']}")
                    print(f"   Context: ...{match['context']}...")
        else:
            print(f"\n✅ No ceiling beliefs or impossibility claims detected.")
            print(f"   {result['recommendation']}\n")

        print("=" * 60)


def cmd_patterns(args):
    """Handle the 'patterns' subcommand."""
    print_patterns()


def main():
    parser = argparse.ArgumentParser(
        description="Detect ceiling beliefs and impossibility conclusions in text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check "This is mathematically impossible to solve"
  %(prog)s check --file report.md
  %(prog)s check "This approach won't work" --json
  %(prog)s check "Seems unlikely" --semantic
  %(prog)s patterns
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check command
    check_parser = subparsers.add_parser("check", help="Analyze text for impossibility claims")
    check_parser.add_argument("text", nargs="?", help="Text to analyze")
    check_parser.add_argument("--file", "-f", help="Read text from file")
    check_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    check_parser.add_argument("--semantic", "-s", action="store_true", help="Use LLM semantic analysis")
    check_parser.set_defaults(func=cmd_check)

    # Patterns command
    patterns_parser = subparsers.add_parser("patterns", help="List all detection patterns")
    patterns_parser.set_defaults(func=cmd_patterns)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
