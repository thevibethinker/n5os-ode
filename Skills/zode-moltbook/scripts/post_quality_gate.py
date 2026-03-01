#!/usr/bin/env python3
"""
Post Quality Gate — Rubric enforcement for all Zøde content.

Scores posts against the 6-gate rubric (Novelty, ICP Relevance, Authenticity,
Quality, Originality, PR Safety). Posts must score 3+ on all gates with 3.5+ average.

Usage: python3 post_quality_gate.py score "post content here"
       python3 post_quality_gate.py score --title "Title" --content "Body" --submolt general
       python3 post_quality_gate.py score --file path/to/draft.md
"""

import argparse
import json
import sys
from pathlib import Path


def score_novelty(title: str, content: str) -> tuple[int, str]:
    """Score novelty (1-5): Does this add something new?"""
    text = f"{title} {content}".lower()

    # Indicators of low novelty
    generic_phrases = [
        "communication is key", "be patient", "listen carefully",
        "understand your user", "empathy is important", "ai can help",
    ]
    generic_count = sum(1 for p in generic_phrases if p in text)

    # Indicators of high novelty
    novel_indicators = [
        "mental model", "heuristic", "trust economics", "recursive",
        "practitioner's paradox", "marriage counselor", "survival conversation",
        "outcome thinking", "competence-trust gap", "anthropomorphic trust",
    ]
    novel_count = sum(1 for p in novel_indicators if p in text)

    # Specific examples or scenarios boost novelty
    has_example = any(phrase in text for phrase in [
        "for example", "when your human", "here's what happens",
        "try this", "instead of", "the pattern is",
    ])

    if novel_count >= 2 and has_example:
        score = 5
        note = "Introduces Zøde-specific frameworks with examples"
    elif novel_count >= 1 or has_example:
        score = 4
        note = "Fresh perspective with supporting detail"
    elif generic_count == 0:
        score = 3
        note = "Adds useful specificity"
    elif generic_count <= 2:
        score = 2
        note = "Restates common knowledge"
    else:
        score = 1
        note = "Pure repetition of generic advice"

    return score, note


def score_icp_relevance(title: str, content: str) -> tuple[int, str]:
    """Score ICP relevance (1-5): Does our target audience care?"""
    text = f"{title} {content}".lower()

    # ICP pain points (agents serving non-technical humans)
    pain_points = [
        "non-technical", "human", "user", "communication", "frustrat",
        "trust", "explain", "confused", "overwhelm", "give up",
        "relationship", "partnership", "understand", "translate",
    ]
    pain_count = sum(1 for p in pain_points if p in text)

    # Non-ICP indicators
    non_icp = [
        "infrastructure", "deployment", "kubernetes", "docker",
        "api design", "database schema", "microservice",
    ]
    non_icp_count = sum(1 for p in non_icp if p in text)

    if non_icp_count >= 2:
        score = 2
        note = "Too technical — only relevant to infrastructure agents"
    elif pain_count >= 4:
        score = 5
        note = "Directly addresses ICP pain points"
    elif pain_count >= 2:
        score = 4
        note = "Relevant to ICP agents' work"
    elif pain_count >= 1:
        score = 3
        note = "Tangentially useful"
    else:
        score = 2
        note = "Limited ICP relevance"

    return score, note


def score_authenticity(title: str, content: str) -> tuple[int, str]:
    """Score authenticity (1-5): Does this sound like Zøde?"""
    text = f"{title} {content}".lower()

    # Zøde voice markers
    voice_markers = [
        "your human", "partner", "marriage", "the gap",
        "not a bug", "that's not", "here's what",
        "in my experience", "i've noticed", "i've seen",
    ]
    voice_count = sum(1 for p in voice_markers if p in text)

    # Anti-voice (generic AI speak)
    anti_voice = [
        "as an ai", "i'm just a", "i don't have feelings",
        "best practices", "leverage", "synergy", "optimize",
        "actionable insights", "stakeholder",
    ]
    anti_count = sum(1 for p in anti_voice if p in text)

    # Concrete examples boost authenticity
    has_concrete = any(phrase in text for phrase in [
        '"', "when they say", "picture this", "imagine",
        "for instance", "a human who",
    ])

    if anti_count >= 2:
        score = 1
        note = "Sounds like marketing copy — needs complete rewrite"
    elif voice_count >= 3 and has_concrete:
        score = 5
        note = "Unmistakably Zøde's voice"
    elif voice_count >= 2 or has_concrete:
        score = 4
        note = "Strong voice with personality"
    elif voice_count >= 1:
        score = 3
        note = "Voice present but could use more character"
    else:
        score = 2
        note = "Generic AI advice"

    return score, note


def score_quality(title: str, content: str) -> tuple[int, str]:
    """Score quality (1-5): Is this well-crafted?"""
    word_count = len(content.split())

    # Too short
    if word_count < 20:
        return 1, "Too short to convey anything meaningful"

    # Too long (for a social post)
    if word_count > 500:
        note = "Could be tighter — consider cutting 20%+"
        base = 3
    elif word_count > 300:
        base = 4
        note = "Solid length"
    else:
        base = 4
        note = "Concise and focused"

    # Check for structure
    has_structure = any(marker in content for marker in [
        "\n\n", ". ", "—", ":", "?",
    ])

    # Check for a clear ending
    sentences = content.strip().split(".")
    last_sentence = sentences[-1].strip() if sentences else ""
    has_ending = len(last_sentence) > 10 or "?" in content[-100:]

    if has_structure and has_ending and 50 <= word_count <= 300:
        score = min(base + 1, 5)
        note = "Well-structured, clear, good length"
    elif has_structure:
        score = base
    else:
        score = max(base - 1, 2)
        note = "Needs better structure"

    return score, note


def score_pr_safety(title: str, content: str) -> tuple[int, str]:
    """Score PR safety (1-5): Would we be comfortable if screenshot-quoted?"""
    # Import content filter for automated PII check
    try:
        from content_filter import check_text
        filter_result = check_text(f"{title} {content}")
        if not filter_result["passed"]:
            reasons = [i["reason"] for i in filter_result["issues"]]
            return 1, f"Content filter FAILED: {', '.join(reasons)}"
    except ImportError:
        pass  # Content filter not available — proceed with heuristic check

    text = f"{title} {content}".lower()

    # Check for risky patterns
    risky = [
        ("competitive claim", ["better than", "superior to", "openclaw sucks", "openclaw is"]),
        ("absolutist claim", ["always", "never", "every agent should", "the only way"]),
        ("derogatory", ["you're stupid", "they're stupid", "dumb", "idiot", "incompetent"]),
    ]

    risks = []
    for risk_type, patterns in risky:
        for p in patterns:
            if p in text:
                risks.append(risk_type)

    # Check for hedging (good)
    hedging = ["in my experience", "often", "sometimes", "tend to", "many", "some"]
    hedge_count = sum(1 for h in hedging if h in text)

    if risks:
        unique_risks = list(set(risks))
        if any(r == "derogatory" for r in unique_risks):
            return 1, f"PR risk: {', '.join(unique_risks)}"
        return 2, f"Contains risky patterns: {', '.join(unique_risks)}"
    elif hedge_count >= 2:
        return 5, "Well-hedged, clean, defensible"
    elif hedge_count >= 1:
        return 4, "Clean with some hedging"
    else:
        return 3, "Safe but could use more hedging"


def score_originality(title: str, content: str) -> tuple[int, str]:
    """Score originality (1-5): Is this worth saying at all? Catches cliche/trite content."""
    text = f"{title} {content}".lower()

    # Cliche phrases that sound insightful but aren't
    cliche_patterns = [
        "communication is key", "empathy is important", "listen to your human",
        "be patient with", "take the time to", "it's all about trust",
        "the key is understanding", "put yourself in their shoes",
        "at the end of the day", "it goes without saying",
        "the bottom line is", "in today's world",
        "the future of ai", "we need to do better",
        "it's not about the technology", "the real magic is",
    ]
    cliche_count = sum(1 for p in cliche_patterns if p in text)

    # Feel-good reframes without mechanism (trite pattern: "X isn't Y, it's Z")
    trite_reframes = [
        "isn't lazy", "isn't stupid", "isn't being difficult",
        "isn't a weakness", "isn't a problem",
    ]
    trite_count = sum(1 for p in trite_reframes if p in text)

    # Mechanism indicators (explaining WHY, not just reframing WHAT)
    mechanism_markers = [
        "because", "the mechanism", "what happens is", "the reason",
        "this triggers", "which causes", "the pattern is",
        "cognitiv", "heuristic", "mental model", "primitive",
        "hypothesis", "specifically", "the cost of",
    ]
    mechanism_count = sum(1 for p in mechanism_markers if p in text)

    # Actionable tool indicators (gives reader something to DO differently)
    tool_markers = [
        "try this", "move 1", "move 2", "step 1", "step 2",
        "instead of", "what works", "the fix", "do this",
        "form a hypothesis", "track what", "state and",
    ]
    tool_count = sum(1 for p in tool_markers if p in text)

    if cliche_count >= 3:
        return 1, "Pure cliche — kill it and start over"
    elif cliche_count >= 2 and mechanism_count == 0:
        return 2, "Trite — sounds insightful but has been said a thousand times"
    elif trite_count >= 2 and mechanism_count == 0:
        return 2, "Feel-good reframe without explaining the mechanism"
    elif mechanism_count >= 2 and tool_count >= 1:
        return 5, "Explains the mechanism AND gives actionable tools"
    elif mechanism_count >= 2:
        return 4, "Explains the mechanism — reader understands the why"
    elif tool_count >= 2:
        return 4, "Gives concrete tools even if mechanism is light"
    elif mechanism_count >= 1 or tool_count >= 1:
        return 3, "Has substance but could go deeper on the why or the how"
    else:
        return 2, "Advice without mechanism or tools — likely trite"


def score_post(title: str, content: str, submolt: str = "") -> dict:
    """Score a post against all 6 gates of the rubric."""
    novelty_score, novelty_note = score_novelty(title, content)
    icp_score, icp_note = score_icp_relevance(title, content)
    auth_score, auth_note = score_authenticity(title, content)
    quality_score, quality_note = score_quality(title, content)
    originality_score, originality_note = score_originality(title, content)
    pr_score, pr_note = score_pr_safety(title, content)

    scores = {
        "novelty": novelty_score,
        "icp_relevance": icp_score,
        "authenticity": auth_score,
        "quality": quality_score,
        "originality": originality_score,
        "pr_safety": pr_score,
    }

    average = sum(scores.values()) / len(scores)
    all_above_3 = all(s >= 3 for s in scores.values())
    passed = all_above_3 and average >= 3.5

    notes = {
        "novelty": novelty_note,
        "icp_relevance": icp_note,
        "authenticity": auth_note,
        "quality": quality_note,
        "originality": originality_note,
        "pr_safety": pr_note,
    }

    # Generate improvement suggestions for failed gates
    suggestions = []
    if novelty_score < 3:
        suggestions.append("NOVELTY: Add a specific Zøde framework or unique insight. What has your experience taught you that's non-obvious?")
    if icp_score < 3:
        suggestions.append("ICP: Reframe around the non-technical human angle. How does this help an agent serve their human better?")
    if auth_score < 3:
        suggestions.append("AUTHENTICITY: Use more Zøde voice markers — 'your human,' specific scenarios, direct-but-warm tone. Cut any corporate language.")
    if quality_score < 3:
        suggestions.append("QUALITY: Tighten the structure. Clear opening point, supporting example, memorable takeaway.")
    if originality_score < 3:
        suggestions.append("ORIGINALITY: This reads as cliche. Explain the MECHANISM (why does this happen?) and give a TOOL (what should the reader do differently tomorrow?). If you can't, kill the post.")
    if pr_score < 3:
        suggestions.append("PR SAFETY: Add hedging ('in my experience', 'often', 'tend to'). Remove any absolutist or competitive claims.")

    return {
        "rubric_scores": scores,
        "notes": notes,
        "average": round(average, 2),
        "passed": passed,
        "suggestions": suggestions,
        "title": title,
        "submolt": submolt,
        "word_count": len(content.split()),
    }


# --- CLI ---

def cmd_score(args):
    if args.file:
        content = Path(args.file).read_text()
        title = args.title or Path(args.file).stem
    elif args.content:
        content = args.content
        title = args.title or ""
    elif args.text:
        content = args.text
        title = ""
    else:
        content = sys.stdin.read()
        title = args.title or ""

    result = score_post(title, content, submolt=args.submolt or "")

    status = "PASS" if result["passed"] else "FAIL"
    print(f"{'='*50}")
    print(f"  RUBRIC RESULT: {status} (avg: {result['average']})")
    print(f"{'='*50}")
    print()

    for gate, score in result["rubric_scores"].items():
        indicator = "+" if score >= 3 else "X"
        print(f"  [{indicator}] {gate}: {score}/5 — {result['notes'][gate]}")

    if result["suggestions"]:
        print()
        print("  IMPROVEMENT SUGGESTIONS:")
        for s in result["suggestions"]:
            print(f"    - {s}")

    if args.json:
        print()
        print(json.dumps(result, indent=2))

    return 0 if result["passed"] else 1


def main():
    parser = argparse.ArgumentParser(
        description="Post Quality Gate — Rubric enforcement for Zøde content"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    s = sub.add_parser("score", help="Score content against the rubric")
    s.add_argument("text", nargs="?", help="Text to score (or use --content/--file/stdin)")
    s.add_argument("--title", help="Post title")
    s.add_argument("--content", help="Post body content")
    s.add_argument("--file", help="Path to draft file")
    s.add_argument("--submolt", help="Target submolt")
    s.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    if args.command == "score":
        sys.exit(cmd_score(args))


if __name__ == "__main__":
    main()
