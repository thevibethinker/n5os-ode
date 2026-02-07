#!/usr/bin/env python3
"""
Step 3: Story Clustering
------------------------
Groups skills by story dimension, synthesizes into coherent themes,
ranks by employer priorities.
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

import requests


def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from assets/prompts/."""
    prompt_path = Path(__file__).parent.parent / "assets" / "prompts" / f"{prompt_name}.md"
    return prompt_path.read_text()


def call_llm(prompt: str, output_schema: dict = None) -> dict:
    """Call /zo/ask API for LLM inference."""
    payload = {"input": prompt}
    if output_schema:
        payload["output_format"] = output_schema
    
    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
            "content-type": "application/json"
        },
        json=payload
    )
    
    result = response.json()
    output = result.get("output", "")
    
    if isinstance(output, dict):
        return output
    
    try:
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    
    return {"raw": output}


def group_skills_by_story(skills: list) -> dict:
    """
    Group skills by their supporting story ID.
    
    Returns:
        {story_id: [skill1, skill2, ...]}
    """
    groups = defaultdict(list)
    no_story = []
    
    for skill in skills:
        support = skill.get("support", [])
        if support:
            # Take the first (best) supporting story
            story_id = support[0].get("source")
            if story_id:
                groups[story_id].append(skill)
            else:
                no_story.append(skill)
        else:
            no_story.append(skill)
    
    if no_story:
        groups["__resume_only__"] = no_story
    
    return dict(groups)


def synthesize_cluster(story_id: str, skills: list, hiring_pov: dict) -> dict:
    """
    Synthesize a cluster of skills into a coherent narrative.
    Uses LLM to deduplicate and create unified theme.
    """
    
    # Gather all our_take fields
    our_takes = [s.get("our_take", "") for s in skills if s.get("our_take")]
    skill_names = [s.get("skill_name", "") for s in skills]
    ratings = [s.get("rating") for s in skills]
    importances = [s.get("importance", 0) for s in skills]
    evidence_types = [s.get("evidence_type") for s in skills]
    
    # Determine evidence strength
    has_story = any("story" in (e or "").lower() for e in evidence_types)
    evidence_strength = "story_verified" if has_story else "resume_only"
    
    # Average importance
    avg_importance = sum(importances) / len(importances) if importances else 5
    
    # Check if mostly excellent
    excellent_count = sum(1 for r in ratings if r == "Excellent")
    mostly_excellent = excellent_count > len(ratings) / 2
    
    prompt = f"""Synthesize these skill assessments into ONE coherent narrative about what this story demonstrates.

SKILLS IN THIS CLUSTER:
{json.dumps([{"skill": s.get("skill_name"), "rating": s.get("rating"), "our_take": s.get("our_take", "")[:500]} for s in skills], indent=2)}

EMPLOYER VALUES (from Hiring POV):
- Trait signals: {hiring_pov.get("trait_signals", [])[:5]}
- Story types valued: {hiring_pov.get("story_types_valued", [])[:5]}

YOUR TASK:
1. Identify the THEME - what dimension of capability does this story demonstrate?
2. Write a 2-3 sentence NARRATIVE that captures the story without repeating details
3. List the top 3-4 SKILLS DEMONSTRATED (deduplicated)
4. Assess EMPLOYER RELEVANCE - how does this map to what they care about?

Return JSON:
{{
  "theme": "Building from Zero",
  "narrative": "Led ML SaaS platform from founding stage...",
  "skills_demonstrated": ["End-to-end delivery", "Architecture"],
  "employer_relevance": "Directly maps to '0→1 experience' requirement"
}}
"""

    result = call_llm(prompt)
    
    return {
        "story_id": story_id,
        "theme": result.get("theme", "Unknown Theme"),
        "narrative": result.get("narrative", ""),
        "skills_demonstrated": result.get("skills_demonstrated", skill_names[:4]),
        "evidence_strength": evidence_strength,
        "employer_relevance": result.get("employer_relevance", ""),
        "relevance_score": int(avg_importance),
        "skill_count": len(skills),
        "excellent_count": excellent_count
    }


def identify_cross_cutting_patterns(clusters: list, hiring_pov: dict) -> list:
    """
    Identify behavioral patterns that appear across multiple stories.
    """
    
    # Gather all narratives and themes
    narratives = [c.get("narrative", "") for c in clusters]
    themes = [c.get("theme", "") for c in clusters]
    
    prompt = f"""Identify behavioral patterns that appear across multiple story clusters.

STORY CLUSTERS:
{json.dumps([{"theme": c.get("theme"), "narrative": c.get("narrative")} for c in clusters], indent=2)}

EMPLOYER VALUES:
- Implicit filters: {hiring_pov.get("implicit_filters", [])[:5]}
- Trait signals: {hiring_pov.get("trait_signals", [])[:5]}

Look for patterns like:
- "Problem-finding" behavior (identifies issues without being told)
- "Ownership" pattern (fixes things outside their scope)
- "Shipping" pattern (bias toward action)

Return JSON array:
[
  {{
    "pattern": "Problem-Finding Instinct",
    "description": "Both stories start with self-identified problems, not tickets",
    "stories_supporting": ["story_id_1", "story_id_2"],
    "employer_relevance": "Strong match for 'self-starter' filter"
  }}
]
"""

    result = call_llm(prompt)
    
    if isinstance(result, list):
        return result
    if isinstance(result, dict) and "patterns" in result:
        return result["patterns"]
    if isinstance(result, dict) and "raw" in result:
        return []
    
    return []


def cluster_stories(skills: list, hiring_pov: dict) -> dict:
    """
    Main clustering function.
    
    Args:
        skills: List of skill dicts from decomposer
        hiring_pov: Hiring POV dict
    
    Returns:
        {
            "story_clusters": [...],
            "cross_cutting_patterns": [...]
        }
    """
    
    # Group by story
    grouped = group_skills_by_story(skills)
    
    # Synthesize each cluster
    clusters = []
    for story_id, story_skills in grouped.items():
        if story_id == "__resume_only__":
            # Handle resume-only skills differently
            cluster = {
                "story_id": "__resume_only__",
                "theme": "Resume Claims (Not Story-Verified)",
                "narrative": "These skills appear on the resume but were not verified through story evidence.",
                "skills_demonstrated": [s.get("skill_name") for s in story_skills[:5]],
                "evidence_strength": "resume_only",
                "employer_relevance": "Treat as claims, not verified capabilities.",
                "relevance_score": 3,
                "skill_count": len(story_skills),
                "excellent_count": sum(1 for s in story_skills if s.get("rating") == "Excellent")
            }
        else:
            cluster = synthesize_cluster(story_id, story_skills, hiring_pov)
        
        clusters.append(cluster)
    
    # Sort by relevance score
    clusters.sort(key=lambda c: c.get("relevance_score", 0), reverse=True)
    
    # Identify cross-cutting patterns (only for story-verified clusters)
    story_clusters = [c for c in clusters if c.get("evidence_strength") == "story_verified"]
    patterns = identify_cross_cutting_patterns(story_clusters, hiring_pov) if len(story_clusters) > 1 else []
    
    return {
        "story_clusters": clusters,
        "cross_cutting_patterns": patterns
    }


def main():
    """CLI for testing clustering."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to gathered.json")
    parser.add_argument("--pov", required=True, help="Path to hiring_pov.json")
    parser.add_argument("--output", default="clusters.json")
    
    args = parser.parse_args()
    
    with open(args.input) as f:
        gathered = json.load(f)
    
    with open(args.pov) as f:
        pov = json.load(f)
    
    skills = gathered.get("decomposer", {}).get("skills", [])
    clusters = cluster_stories(skills, pov)
    
    with open(args.output, "w") as f:
        json.dump(clusters, f, indent=2)
    
    print(f"Clusters saved to {args.output}")
    print(f"  Story clusters: {len(clusters.get('story_clusters', []))}")
    print(f"  Cross-cutting patterns: {len(clusters.get('cross_cutting_patterns', []))}")


if __name__ == "__main__":
    main()
