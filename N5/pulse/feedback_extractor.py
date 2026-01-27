#!/usr/bin/env python3
"""
Feedback Extractor for Pulse v2.
Converts V's feedback into structured learnings for system improvement.

This bridges raw feedback (SMS, email, chat) into the learnings system.

VibeTeacher Integration:
- Teaching moments activated on feedback extraction
- Stored alongside learnings for review at build close
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Add scripts dir for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path("/home/workspace/Skills/pulse/scripts")))

from pulse_learnings import load_system_learnings, save_system_learnings

WORKSPACE = Path("/home/workspace")
SYSTEM_LEARNINGS = WORKSPACE / "N5" / "learnings" / "SYSTEM_LEARNINGS.json"
PULSE_DIR = Path(__file__).parent


FEEDBACK_CATEGORIES = {
    "output_quality": "About the deliverable quality, correctness, or completeness",
    "process": "About how work was done, workflows, or procedures",
    "communication": "About how information was shared or understood",
    "timing": "About speed, delays, or scheduling"
}


def categorize_feedback(feedback: str) -> Dict:
    """
    Categorize feedback into known categories using LLM analysis.

    Returns:
        dict with 'primary_category', 'secondary_categories', 'confidence'
    """
    # For now, use keyword-based classification as fallback
    # In production, this would call Zo's LLM via the API
    feedback_lower = feedback.lower()

    category_scores = {
        "output_quality": 0,
        "process": 0,
        "communication": 0,
        "timing": 0
    }

    # Simple keyword matching (LLM would be better)
    output_quality_keywords = ["wrong", "incorrect", "incomplete", "missing", "bug", "error", "broken", "doesn't work", "quality", "result"]
    process_keywords = ["process", "workflow", "approach", "should have", "way", "method", "procedure", "steps"]
    communication_keywords = ["unclear", "confused", "didn't tell me", "should have asked", "clarify", "explain", "misunderstood"]
    timing_keywords = ["late", "slow", "fast", "deadline", "time", "too long", "quickly", "schedule"]

    for kw in output_quality_keywords:
        if kw in feedback_lower:
            category_scores["output_quality"] += 1

    for kw in process_keywords:
        if kw in feedback_lower:
            category_scores["process"] += 1

    for kw in communication_keywords:
        if kw in feedback_lower:
            category_scores["communication"] += 1

    for kw in timing_keywords:
        if kw in feedback_lower:
            category_scores["timing"] += 1

    # Find primary category
    if max(category_scores.values()) == 0:
        primary = "process"  # Default
    else:
        primary = max(category_scores, key=category_scores.get)

    # Secondary categories (with any score > 0)
    secondary = [k for k, v in category_scores.items() if v > 0 and k != primary]

    return {
        "primary_category": primary,
        "secondary_categories": secondary,
        "raw_scores": category_scores
    }


def extract_learnings(slug: str, feedback: str, source: str = "manual") -> List[Dict]:
    """
    Extract learnings from V's feedback.

    Uses LLM to identify:
    - What worked well
    - What didn't work
    - Process improvements
    - Technical patterns

    Args:
        slug: Build slug
        feedback: Raw feedback text from V
        source: Where feedback came from (sms, email, chat)

    Returns:
        List of learning dictionaries
    """
    # Categorize first
    categorization = categorize_feedback(feedback)
    primary = categorization["primary_category"]

    # Extract learnings using LLM analysis
    learnings = []

    # Try to extract explicit "what should be" patterns
    if "should" in feedback.lower() or "need to" in feedback.lower():
        # Extract the "should" clause as a learning
        sentences = feedback.split(". ")
        for sentence in sentences:
            if "should" in sentence.lower() or "need to" in sentence.lower():
                learnings.append({
                    "category": primary,
                    "learning": sentence.strip(),
                    "source_feedback": feedback[:200] + ("..." if len(feedback) > 200 else ""),
                    "sentiment": "negative" if "didn't" in sentence.lower() or "wrong" in sentence.lower() else "constructive"
                })

    # If no explicit learnings extracted, convert the feedback itself
    if not learnings:
        learnings.append({
            "category": primary,
            "learning": f"Feedback: {feedback[:150]}",
            "source_feedback": feedback,
            "sentiment": "constructive"
        })

    # Add metadata
    for learning in learnings:
        learning["id"] = f"learn-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        learning["created_at"] = datetime.now(timezone.utc).isoformat()
        learning["build_slug"] = slug
        learning["source"] = source
        learning["applied"] = False
        learning["applied_to"] = []

    return learnings


def add_to_system_learnings(learnings: List[Dict], deduplicate: bool = True) -> int:
    """
    Add learnings to SYSTEM_LEARNINGS.json with optional deduplication.

    Args:
        learnings: List of learning dicts
        deduplicate: If True, merge similar learnings

    Returns:
        Number of new learnings added
    """
    data = load_system_learnings()
    existing = data.get("learnings", [])

    added_count = 0

    for learning in learnings:
        # Check for duplicates
        is_duplicate = False
        if deduplicate:
            for existing_learning in existing:
                # Simple similarity check (could be improved with embeddings)
                similarity = _similarity_score(learning.get("learning", ""), existing_learning.get("text", ""))
                if similarity > 0.8:  # 80% similarity threshold
                    is_duplicate = True
                    # Merge into existing
                    existing_learning.get("applied_to", []).extend(learning.get("applied_to", []))
                    break

        if not is_duplicate:
            # Convert to system learning format
            system_learning = {
                "text": learning["learning"],
                "category": learning["category"],
                "source": learning.get("source", "manual"),
                "origin_build": learning.get("build_slug"),
                "added_at": learning.get("created_at"),
                "source_feedback": learning.get("source_feedback", "")[:500],
                "tags": [learning["category"]],
                "applied": False,
                "applied_to": []
            }
            existing.append(system_learning)
            added_count += 1

    data["learnings"] = existing
    save_system_learnings(data)

    return added_count


def _similarity_score(s1: str, s2: str) -> float:
    """
    Calculate simple similarity between two strings.

    Uses word overlap as a simple metric.
    """
    words1 = set(s1.lower().split())
    words2 = set(s2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union)


def extract_and_store(slug: str, feedback: str, source: str = "manual") -> Dict:
    """
    Full pipeline: extract learnings from feedback and store to system.

    VibeTeacher Integration:
    - Activates teaching moment on feedback
    - Stores moment alongside learnings for review

    Args:
        slug: Build slug
        feedback: Raw feedback text
        source: Feedback source (sms, email, chat)

    Returns:
        dict with extraction results including teaching moment
    """
    # Extract learnings
    learnings = extract_learnings(slug, feedback, source)

    # Add to system
    added = add_to_system_learnings(learnings, deduplicate=True)

    # Activate VibeTeacher for teaching moment (non-blocking)
    teaching_moment = None
    try:
        teaching_result = subprocess.run(
            ["python3", str(PULSE_DIR / "teaching" / "teaching_manager.py"),
             "activate", "--checkpoint", "feedback", "--slug", slug, "--input", feedback],
            capture_output=True, text=True, cwd="/home/workspace"
        )
        if teaching_result.returncode == 0:
            teaching_data = json.loads(teaching_result.stdout)
            if teaching_data.get("has_moment"):
                teaching_moment = teaching_data.get("teaching")
    except Exception as e:
        # Teaching activation failure should not block feedback extraction
        pass

    return {
        "build_slug": slug,
        "source": source,
        "learnings_extracted": len(learnings),
        "learnings_added": added,
        "learnings": learnings,
        "teaching_moment": teaching_moment
    }


def summarize_feedback(feedback: str) -> Dict:
    """
    Generate a quick summary and sentiment analysis of feedback.

    Useful for dashboard display and prioritization.
    """
    categorization = categorize_feedback(feedback)

    # Simple sentiment detection
    negative_words = ["bad", "wrong", "error", "failed", "broken", "missing", "didn't", "doesn't"]
    positive_words = ["good", "great", "excellent", "worked", "success", "perfect"]

    feedback_lower = feedback.lower()
    negative_score = sum(1 for w in negative_words if w in feedback_lower)
    positive_score = sum(1 for w in positive_words if w in feedback_lower)

    if negative_score > positive_score:
        sentiment = "negative"
    elif positive_score > negative_score:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    return {
        "feedback_preview": feedback[:100] + ("..." if len(feedback) > 100 else ""),
        "category": categorization["primary_category"],
        "sentiment": sentiment,
        "word_count": len(feedback.split())
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Feedback Extractor for Pulse v2")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # extract
    extract_parser = subparsers.add_parser("extract", help="Extract learnings from feedback")
    extract_parser.add_argument("slug", help="Build slug")
    extract_parser.add_argument("feedback", help="Feedback text (quote if multi-word)")
    extract_parser.add_argument("--source", default="manual", help="Source (sms, email, chat)")

    # categorize
    categorize_parser = subparsers.add_parser("categorize", help="Categorize feedback")
    categorize_parser.add_argument("feedback", help="Feedback text")

    # summarize
    summarize_parser = subparsers.add_parser("summarize", help="Summarize feedback")
    summarize_parser.add_argument("feedback", help="Feedback text")

    args = parser.parse_args()

    if args.command == "extract":
        result = extract_and_store(args.slug, args.feedback, args.source)
        print(json.dumps(result, indent=2))

    elif args.command == "categorize":
        result = categorize_feedback(args.feedback)
        print(json.dumps(result, indent=2))

    elif args.command == "summarize":
        result = summarize_feedback(args.feedback)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
