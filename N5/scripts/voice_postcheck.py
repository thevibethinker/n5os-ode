#!/usr/bin/env python3
"""
Voice Post-Check with Primitive Injection

Part of Voice Library V2 (Phase 3.4: Pangram Post-Check Flow).

Analyzes generated content with Pangram and suggests primitive injection
for AI-heavy segments.

Usage:
  python3 voice_postcheck.py --text "Your generated content here"
  python3 voice_postcheck.py --file path/to/draft.md
  python3 voice_postcheck.py --file draft.md --threshold 0.5 --auto-inject

Process:
1. Run Pangram on the full draft
2. If fraction_ai > threshold (default 0.5):
   a. Identify which paragraphs are most AI-like
   b. Retrieve high-distinctiveness primitives (≥ 0.8)
   c. Suggest specific injections for each problematic paragraph
3. Output suggestions (or auto-inject if --auto-inject)
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))

from N5.scripts.retrieve_primitives import get_connection, get_primitives, mark_as_used

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
LOG = logging.getLogger("voice_postcheck")


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_THRESHOLD = 0.5  # fraction_ai above this triggers injection suggestions
HIGH_DISTINCTIVENESS = 0.8  # Only use highly distinctive primitives for injection
MAX_ITERATIONS = 2  # Max injection attempts per segment


# ─────────────────────────────────────────────────────────────────────────────
# Pangram Integration
# ─────────────────────────────────────────────────────────────────────────────

def check_pangram(text: str) -> Optional[Dict[str, Any]]:
    """
    Check text with Pangram API.
    Returns analysis dict or None if API unavailable.
    """
    try:
        import requests
    except ImportError:
        LOG.warning("requests not installed, skipping Pangram check")
        return None
    
    api_key = os.environ.get("PANGRAM_API_KEY")
    if not api_key:
        LOG.warning("PANGRAM_API_KEY not set, skipping Pangram check")
        return None
    
    if len(text.strip()) < 50:
        LOG.warning("Text too short for reliable Pangram detection")
        return None
    
    try:
        response = requests.post(
            "https://text.api.pangram.com/v3",
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json"
            },
            json={"text": text},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            LOG.error(f"Pangram API error: {response.status_code}")
            return None
    except Exception as e:
        LOG.error(f"Pangram request failed: {e}")
        return None


def get_ai_score(text: str) -> Optional[float]:
    """Get fraction_ai score for text."""
    result = check_pangram(text)
    if result and "fraction_ai" in result:
        return result["fraction_ai"]
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Text Analysis
# ─────────────────────────────────────────────────────────────────────────────

def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs for segment analysis."""
    # Split on double newlines or horizontal rules
    paragraphs = re.split(r'\n\n+|\n---+\n', text)
    # Filter out empty paragraphs and very short ones
    return [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 50]


def analyze_segments(text: str) -> List[Dict[str, Any]]:
    """
    Analyze each paragraph for AI-likeness.
    Returns list of segments with scores.
    """
    paragraphs = split_into_paragraphs(text)
    segments = []
    
    for i, para in enumerate(paragraphs):
        score = get_ai_score(para)
        segments.append({
            "index": i,
            "text": para[:200] + "..." if len(para) > 200 else para,
            "full_text": para,
            "ai_score": score,
            "word_count": len(para.split()),
        })
    
    return segments


def identify_problem_segments(segments: List[Dict], threshold: float = DEFAULT_THRESHOLD) -> List[Dict]:
    """Find segments with AI scores above threshold."""
    problems = []
    for seg in segments:
        if seg["ai_score"] is not None and seg["ai_score"] > threshold:
            problems.append(seg)
    
    # Sort by AI score (highest first)
    return sorted(problems, key=lambda x: x["ai_score"] or 0, reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# Primitive Selection
# ─────────────────────────────────────────────────────────────────────────────

def extract_topic_keywords(text: str) -> str:
    """Extract simple topic keywords from text for primitive matching."""
    # Remove common words and extract key nouns/phrases
    words = text.lower().split()
    # Simple stop words
    stop = {"the", "a", "an", "is", "are", "was", "were", "be", "been", 
            "to", "of", "and", "in", "that", "it", "for", "on", "with",
            "as", "at", "by", "from", "or", "this", "but", "not", "you",
            "your", "i", "we", "they", "he", "she", "my", "our", "their"}
    keywords = [w for w in words if w not in stop and len(w) > 3]
    return " ".join(keywords[:10])


def get_injection_primitives(segment: Dict, used_ids: set) -> List[Dict]:
    """
    Get high-distinctiveness primitives suitable for injecting into segment.
    """
    topic = extract_topic_keywords(segment["full_text"])
    
    conn = get_connection()
    primitives = get_primitives(
        conn,
        count=5,
        min_distinctiveness=HIGH_DISTINCTIVENESS,
        topic=topic if topic else None,
        exclude_recently_used=True,
    )
    conn.close()
    
    # Filter out already-used primitives in this session
    return [p for p in primitives if p["id"] not in used_ids]


# ─────────────────────────────────────────────────────────────────────────────
# Injection Suggestions
# ─────────────────────────────────────────────────────────────────────────────

def generate_injection_prompt(segment: Dict, primitives: List[Dict]) -> str:
    """Generate a prompt for rewriting a segment with primitive injection."""
    primitive_list = "\n".join([
        f"- [{p['primitive_type']}] \"{p['exact_text']}\"" 
        for p in primitives[:3]
    ])
    
    return f"""Rewrite this paragraph incorporating at least ONE of these voice primitives naturally:

PRIMITIVES AVAILABLE:
{primitive_list}

ORIGINAL PARAGRAPH:
{segment['full_text']}

GUIDELINES:
- Integrate the primitive naturally (don't force it)
- Maintain the original meaning and information
- Signature phrases can be used verbatim
- Metaphors/analogies should be adapted to context
- If no primitive fits, return the original unchanged

REWRITTEN:"""


def create_suggestions(problem_segments: List[Dict], used_ids: set) -> List[Dict]:
    """
    Create injection suggestions for problem segments.
    """
    suggestions = []
    
    for seg in problem_segments[:3]:  # Limit to top 3 problem areas
        primitives = get_injection_primitives(seg, used_ids)
        
        if primitives:
            # Track used primitives
            for p in primitives[:3]:
                used_ids.add(p["id"])
            
            suggestions.append({
                "segment_index": seg["index"],
                "ai_score": seg["ai_score"],
                "segment_preview": seg["text"],
                "suggested_primitives": [
                    {"id": p["id"], "text": p["exact_text"], "type": p["primitive_type"]}
                    for p in primitives[:3]
                ],
                "injection_prompt": generate_injection_prompt(seg, primitives),
            })
    
    return suggestions


# ─────────────────────────────────────────────────────────────────────────────
# Main Analysis
# ─────────────────────────────────────────────────────────────────────────────

def analyze_draft(text: str, threshold: float = DEFAULT_THRESHOLD) -> Dict[str, Any]:
    """
    Full analysis of draft with injection suggestions.
    """
    result = {
        "overall_score": None,
        "needs_injection": False,
        "problem_segments": [],
        "suggestions": [],
        "status": "unknown",
    }
    
    # Overall score
    overall = get_ai_score(text)
    result["overall_score"] = overall
    
    if overall is None:
        result["status"] = "pangram_unavailable"
        return result
    
    if overall <= threshold:
        result["status"] = "pass"
        result["needs_injection"] = False
        return result
    
    # Need to analyze segments
    result["status"] = "needs_work"
    result["needs_injection"] = True
    
    LOG.info(f"Overall AI score: {overall:.1%} (threshold: {threshold:.1%})")
    LOG.info("Analyzing segments...")
    
    segments = analyze_segments(text)
    problems = identify_problem_segments(segments, threshold)
    result["problem_segments"] = problems
    
    if not problems:
        # Overall high but no single segment stands out
        result["suggestions"] = [{
            "note": "Overall score is high but no single segment dominates. Consider adding distinctive voice elements throughout.",
            "general_primitives": get_injection_primitives({"full_text": text}, set())[:5]
        }]
        return result
    
    # Generate specific suggestions
    used_ids = set()
    suggestions = create_suggestions(problems, used_ids)
    result["suggestions"] = suggestions
    
    # Mark primitives as used
    if used_ids:
        conn = get_connection()
        mark_as_used(conn, list(used_ids))
        conn.close()
    
    return result


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Voice post-check with primitive injection suggestions"
    )
    
    # Input
    parser.add_argument("--text", "-t", type=str,
                        help="Text to analyze")
    parser.add_argument("--file", "-f", type=str,
                        help="File to analyze")
    
    # Configuration
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help=f"AI score threshold (default: {DEFAULT_THRESHOLD})")
    
    # Output
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Only output pass/fail")
    
    args = parser.parse_args()
    
    # Get text
    text = args.text
    if args.file:
        path = Path(args.file)
        if not path.exists():
            LOG.error(f"File not found: {args.file}")
            sys.exit(1)
        text = path.read_text()
    
    if not text:
        LOG.error("No text provided. Use --text or --file")
        sys.exit(1)
    
    # Analyze
    result = analyze_draft(text, args.threshold)
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return
    
    if args.quiet:
        if result["status"] == "pass":
            print("✓ PASS")
            sys.exit(0)
        elif result["status"] == "pangram_unavailable":
            print("? UNKNOWN (Pangram unavailable)")
            sys.exit(2)
        else:
            print(f"✗ FAIL ({result['overall_score']:.1%} AI)")
            sys.exit(1)
    
    # Verbose output
    print("\n=== Voice Post-Check Results ===\n")
    
    if result["overall_score"] is not None:
        status_emoji = "✓" if result["status"] == "pass" else "✗"
        print(f"Overall AI Score: {result['overall_score']:.1%} {status_emoji}")
        print(f"Threshold: {args.threshold:.1%}")
        print(f"Status: {result['status'].upper()}")
    else:
        print("Status: Pangram unavailable")
        return
    
    if not result["needs_injection"]:
        print("\n✓ Content passes voice check. No injection needed.")
        return
    
    print(f"\n{len(result['problem_segments'])} segment(s) detected as AI-heavy:\n")
    
    for seg in result["problem_segments"]:
        print(f"  Segment {seg['index'] + 1}: {seg['ai_score']:.1%} AI")
        print(f"  Preview: {seg['text'][:100]}...")
        print()
    
    if result["suggestions"]:
        print("=== Injection Suggestions ===\n")
        
        for i, sug in enumerate(result["suggestions"], 1):
            print(f"Suggestion {i} (for segment with {sug['ai_score']:.1%} AI):")
            print("\nPrimitives to inject:")
            for p in sug["suggested_primitives"]:
                print(f"  - [{p['type']}] \"{p['text']}\"")
            print("\n" + "-" * 40)
            print("REWRITE PROMPT:")
            print(sug["injection_prompt"])
            print("-" * 40 + "\n")


if __name__ == "__main__":
    main()

