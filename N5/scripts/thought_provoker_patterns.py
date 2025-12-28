#!/usr/bin/env python3
"""
Thought Provoker Pattern Detector

Analyzes B32 ideas across all meetings to identify:
- Recurring themes (same topic, multiple meetings)
- Contradictions (opposing stances on same topic)
- Evolutions (how thinking has shifted over time)

Usage:
    python3 thought_provoker_patterns.py [--input PATH] [--output PATH]
"""

import argparse
import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

DEFAULT_INPUT = Path("/home/workspace/N5/data/provocation_candidates_v2.json")
DEFAULT_OUTPUT = Path("/home/workspace/N5/data/thought_patterns.json")

# Theme keywords for simple clustering
THEME_KEYWORDS = {
    "ai_replacement": ["replace", "automat", "headcount", "payroll", "ai tool", "llm", "agent"],
    "recruiting_future": ["recruit", "hiring", "talent", "candidate", "sourcing", "careerspan"],
    "founder_life": ["founder", "burnout", "fundrais", "runway", "pivot", "bootstrap"],
    "community_network": ["community", "network", "linkedin", "connection", "relationship"],
    "pricing_business": ["pricing", "revenue", "arpu", "monetiz", "business model", "margin"],
    "product_strategy": ["product", "feature", "mvp", "roadmap", "user", "customer"],
    "ai_philosophy": ["consciousness", "agi", "alignment", "reasoning", "intelligence"],
    "personal_growth": ["productivity", "system", "workflow", "habit", "discipline"],
}


def extract_themes(idea: dict) -> list[str]:
    """Extract theme tags from an idea based on keyword matching."""
    text = f"{idea.get('title', '')} {idea.get('idea', '')}".lower()
    themes = []
    
    for theme, keywords in THEME_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                themes.append(theme)
                break
    
    return themes if themes else ["uncategorized"]


def detect_patterns(data: dict) -> dict:
    """
    Analyze ideas to detect patterns.
    
    Returns dict with:
    - recurring_themes: Topics that appear in 3+ meetings
    - potential_contradictions: Ideas that may conflict
    - evolution_candidates: Same theme across time
    """
    # Build theme -> ideas mapping
    theme_ideas = defaultdict(list)
    
    for meeting in data.get("candidates", []):
        meeting_date = meeting["meeting_date"]
        meeting_name = meeting["meeting_name"]
        
        for idea in meeting.get("ideas", []):
            themes = extract_themes(idea)
            for theme in themes:
                theme_ideas[theme].append({
                    "title": idea["title"],
                    "idea": idea["idea"][:200] + "..." if len(idea.get("idea", "")) > 200 else idea.get("idea", ""),
                    "meeting": meeting_name,
                    "date": meeting_date
                })
    
    # Find recurring themes (3+ meetings)
    recurring_themes = []
    for theme, ideas in theme_ideas.items():
        # Count unique meetings
        unique_meetings = set(i["meeting"] for i in ideas)
        if len(unique_meetings) >= 3:
            # Sort by date
            ideas_sorted = sorted(ideas, key=lambda x: x["date"], reverse=True)
            recurring_themes.append({
                "theme": theme,
                "meeting_count": len(unique_meetings),
                "idea_count": len(ideas),
                "recent_examples": ideas_sorted[:5],
                "date_range": {
                    "earliest": min(i["date"] for i in ideas),
                    "latest": max(i["date"] for i in ideas)
                }
            })
    
    # Sort by meeting count
    recurring_themes.sort(key=lambda x: x["meeting_count"], reverse=True)
    
    # Find evolution candidates (same theme, chronological spread)
    evolution_candidates = []
    for theme_data in recurring_themes:
        if theme_data["meeting_count"] >= 4:
            evolution_candidates.append({
                "theme": theme_data["theme"],
                "trajectory": theme_data["recent_examples"],
                "span_days": (
                    datetime.strptime(theme_data["date_range"]["latest"], "%Y-%m-%d") -
                    datetime.strptime(theme_data["date_range"]["earliest"], "%Y-%m-%d")
                ).days
            })
    
    result = {
        "analysis_date": datetime.now(timezone.utc).isoformat(),
        "total_ideas_analyzed": data.get("total_ideas", 0),
        "total_meetings": data.get("meetings_scanned", 0),
        "recurring_themes": recurring_themes[:10],  # Top 10
        "evolution_candidates": evolution_candidates[:5],  # Top 5 with enough history
        "theme_distribution": {
            theme: len(ideas) for theme, ideas in theme_ideas.items()
        }
    }
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Detect patterns in B32 thought-provoking ideas")
    parser.add_argument("--input", type=str, default=str(DEFAULT_INPUT), help="Input JSON from scanner")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="Output patterns JSON")
    args = parser.parse_args()
    
    # Load scanned data
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        logger.info("Run thought_provoker_scan_v2.py --all first")
        return
    
    with open(input_path) as f:
        data = json.load(f)
    
    logger.info(f"Loaded {data.get('total_ideas', 0)} ideas from {data.get('meetings_scanned', 0)} meetings")
    
    # Detect patterns
    patterns = detect_patterns(data)
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved patterns to {output_path}")
    
    # Print summary
    print(f"Patterns detected:")
    print(f"  Recurring themes: {len(patterns['recurring_themes'])}")
    print(f"  Evolution candidates: {len(patterns['evolution_candidates'])}")
    
    if patterns['recurring_themes']:
        top = patterns['recurring_themes'][0]
        print(f"  Top theme: {top['theme']} ({top['meeting_count']} meetings, {top['idea_count']} ideas)")


if __name__ == "__main__":
    main()

