#!/usr/bin/env python3
"""
Pangram AI Detection CLI

Tests text against Pangram's AI detection API.
Target threshold: fraction_ai < 0.3 to pass.

Usage:
    pangram check "Your text here"
    pangram check --file path/to/file.md
    pangram analyze "Text" --verbose         # Show segment breakdown
    pangram iterate "Text" --target 0.3      # Show what needs work
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip install requests -q")
    import requests


API_URL = "https://text.api.pangram.com/v3"
DEFAULT_THRESHOLD = 0.3


def get_api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("PANGRAM_API_KEY")
    if not key:
        print("Error: PANGRAM_API_KEY not set in environment")
        print("Add it at: Settings > Developers")
        sys.exit(1)
    return key


def analyze_text(text: str) -> dict:
    """Send text to Pangram API and return analysis."""
    headers = {
        "x-api-key": get_api_key(),
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        API_URL,
        headers=headers,
        json={"text": text},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"API Error: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    return response.json()


def format_score(score: float, threshold: float = DEFAULT_THRESHOLD) -> str:
    """Format score with pass/fail indicator."""
    status = "✓ PASS" if score < threshold else "✗ FAIL"
    return f"{score:.1%} AI | {status}"


def cmd_check(args):
    """Basic check - pass/fail against threshold."""
    text = args.text
    if args.file:
        text = Path(args.file).read_text()
    
    if not text or len(text.strip()) < 50:
        print("Error: Text too short (minimum ~50 chars for reliable detection)")
        sys.exit(1)
    
    result = analyze_text(text)
    
    fraction_ai = result.get("fraction_ai", 0)
    fraction_human = result.get("fraction_human", 0)
    
    print(f"\n{'='*50}")
    print(f"PANGRAM ANALYSIS")
    print(f"{'='*50}")
    print(f"AI Score:     {format_score(fraction_ai, args.threshold)}")
    print(f"Human Score:  {fraction_human:.1%}")
    print(f"Threshold:    < {args.threshold:.0%} to pass")
    print(f"{'='*50}")
    
    # Return exit code based on pass/fail
    sys.exit(0 if fraction_ai < args.threshold else 1)


def cmd_analyze(args):
    """Detailed analysis with segment breakdown."""
    text = args.text
    if args.file:
        text = Path(args.file).read_text()
    
    result = analyze_text(text)
    
    fraction_ai = result.get("fraction_ai", 0)
    fraction_human = result.get("fraction_human", 0)
    
    print(f"\n{'='*60}")
    print(f"PANGRAM DETAILED ANALYSIS")
    print(f"{'='*60}")
    print(f"Overall AI:     {format_score(fraction_ai, args.threshold)}")
    print(f"Overall Human:  {fraction_human:.1%}")
    print(f"{'='*60}")
    
    # Segment breakdown
    segments = result.get("segments", [])
    if segments and args.verbose:
        print(f"\nSEGMENT BREAKDOWN ({len(segments)} segments):")
        print("-" * 60)
        
        flagged = []
        for i, seg in enumerate(segments):
            score = seg.get("ai_assistance_score", 0)
            text_preview = seg.get("text", "")[:80].replace("\n", " ")
            if len(seg.get("text", "")) > 80:
                text_preview += "..."
            
            status = "🔴" if score > 0.5 else "🟡" if score > 0.3 else "🟢"
            print(f"{status} [{i+1}] {score:.0%} AI: \"{text_preview}\"")
            
            if score > args.threshold:
                flagged.append({
                    "index": i + 1,
                    "score": score,
                    "text": seg.get("text", "")
                })
        
        if flagged:
            print(f"\n{'='*60}")
            print(f"FLAGGED SEGMENTS (score > {args.threshold:.0%}):")
            print("-" * 60)
            for seg in flagged:
                print(f"\n[Segment {seg['index']}] Score: {seg['score']:.0%}")
                print(f"Text: \"{seg['text']}\"")
    
    # Output JSON if requested
    if args.json:
        print(f"\n{'='*60}")
        print("RAW JSON:")
        print(json.dumps(result, indent=2))
    
    sys.exit(0 if fraction_ai < args.threshold else 1)


def cmd_iterate(args):
    """Analysis focused on iteration - what needs to change."""
    text = args.text
    if args.file:
        text = Path(args.file).read_text()
    
    result = analyze_text(text)
    
    fraction_ai = result.get("fraction_ai", 0)
    segments = result.get("segments", [])
    
    print(f"\n{'='*60}")
    print(f"ITERATION ANALYSIS")
    print(f"{'='*60}")
    print(f"Current Score: {fraction_ai:.1%} AI")
    print(f"Target:        < {args.target:.0%} AI")
    print(f"Gap:           {max(0, fraction_ai - args.target):.1%}")
    print(f"{'='*60}")
    
    if fraction_ai < args.target:
        print("\n✓ TEXT PASSES - No iteration needed")
        sys.exit(0)
    
    # Find problem segments
    problem_segments = []
    for i, seg in enumerate(segments):
        score = seg.get("ai_assistance_score", 0)
        if score > args.target:
            problem_segments.append({
                "index": i + 1,
                "score": score,
                "text": seg.get("text", "")
            })
    
    if problem_segments:
        print(f"\n🔧 SEGMENTS NEEDING WORK ({len(problem_segments)}):")
        print("-" * 60)
        
        # Sort by score (worst first)
        problem_segments.sort(key=lambda x: x["score"], reverse=True)
        
        for seg in problem_segments:
            print(f"\n[Segment {seg['index']}] Score: {seg['score']:.0%}")
            print(f"Text:\n\"{seg['text']}\"")
            print()
            
            # Provide iteration hints based on common AI patterns
            hints = get_iteration_hints(seg["text"])
            if hints:
                print("Suggestions:")
                for hint in hints:
                    print(f"  • {hint}")
    
    print(f"\n{'='*60}")
    print("ITERATION STRATEGY:")
    print("-" * 60)
    print("1. Focus on highest-scoring segments first")
    print("2. Apply voice transformation pairs")
    print("3. Re-test after each change")
    print("4. Target: All segments < 30% AI")
    print(f"{'='*60}")
    
    sys.exit(1)


def get_iteration_hints(text: str) -> list:
    """Generate hints for making text more natural."""
    hints = []
    text_lower = text.lower()
    
    # Common AI patterns to flag
    patterns = {
        "it's important to": "State the importance directly without announcing it",
        "it is essential": "Show why it matters through specifics, not labels",
        "in conclusion": "End naturally without signposting",
        "furthermore": "Use 'and' or start new sentence",
        "moreover": "Cut or use simpler connector",
        "in order to": "Replace with 'to'",
        "utilize": "Replace with 'use'",
        "leverage": "Replace with specific verb",
        "facilitate": "Replace with 'help' or 'enable'",
        "comprehensive": "Be specific about what it covers",
        "robust": "Describe the actual strength",
        "innovative": "Show the innovation, don't label it",
        "cutting-edge": "Describe what makes it advanced",
        "synergy": "Describe the actual benefit",
        "paradigm": "Use plain language",
        "holistic": "Be specific",
        "streamline": "Say what you're simplifying",
        "empower": "Say what capability you're giving",
        "delve into": "Replace with 'explore' or 'look at'",
        "dive into": "Often unnecessary - just start",
        "let's explore": "Just start exploring",
        "i hope this helps": "End with confidence",
        "feel free to": "Make direct offer or ask",
        "don't hesitate to": "Direct: 'Ask me' or 'Let me know'",
    }
    
    for pattern, suggestion in patterns.items():
        if pattern in text_lower:
            hints.append(f"'{pattern}' → {suggestion}")
    
    # Structural hints
    if text.count(",") > 3 and len(text) < 200:
        hints.append("Long comma chains feel mechanical - break into shorter sentences")
    
    if text.startswith(("This ", "It ", "There ")):
        hints.append("Weak opener - start with subject or action")
    
    return hints[:5]  # Limit to top 5 hints


def main():
    parser = argparse.ArgumentParser(
        description="Pangram AI Detection CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pangram check "Your text here"
  pangram check --file draft.md --threshold 0.25
  pangram analyze "Text" --verbose
  pangram iterate "Text" --target 0.3
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Quick pass/fail check")
    check_parser.add_argument("text", nargs="?", help="Text to analyze")
    check_parser.add_argument("--file", "-f", help="Read text from file")
    check_parser.add_argument("--threshold", "-t", type=float, default=DEFAULT_THRESHOLD,
                             help=f"Pass threshold (default: {DEFAULT_THRESHOLD})")
    check_parser.set_defaults(func=cmd_check)
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Detailed analysis")
    analyze_parser.add_argument("text", nargs="?", help="Text to analyze")
    analyze_parser.add_argument("--file", "-f", help="Read text from file")
    analyze_parser.add_argument("--verbose", "-v", action="store_true",
                               help="Show segment breakdown")
    analyze_parser.add_argument("--json", action="store_true", help="Output raw JSON")
    analyze_parser.add_argument("--threshold", "-t", type=float, default=DEFAULT_THRESHOLD,
                               help=f"Flag threshold (default: {DEFAULT_THRESHOLD})")
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Iterate command
    iterate_parser = subparsers.add_parser("iterate", help="Iteration-focused analysis")
    iterate_parser.add_argument("text", nargs="?", help="Text to analyze")
    iterate_parser.add_argument("--file", "-f", help="Read text from file")
    iterate_parser.add_argument("--target", type=float, default=DEFAULT_THRESHOLD,
                               help=f"Target score (default: {DEFAULT_THRESHOLD})")
    iterate_parser.set_defaults(func=cmd_iterate)
    
    args = parser.parse_args()
    
    # Validate input
    if not args.text and not getattr(args, 'file', None):
        parser.error("Either text or --file is required")
    
    args.func(args)


if __name__ == "__main__":
    main()

