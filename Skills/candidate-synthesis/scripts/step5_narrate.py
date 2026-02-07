#!/usr/bin/env python3
"""
Step 5: Narrative Generation
----------------------------
Generates the final employer-focused narrative ready for meta-resume-generator.
"""

import json
import os
import re
from pathlib import Path

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


def get_verdict_action(score: int) -> str:
    """Map score to action recommendation."""
    if score >= 85:
        return "Take This Meeting"
    elif score >= 70:
        return "Worth Considering"
    elif score >= 55:
        return "Proceed with Caution"
    else:
        return "Skip This One"


def get_verdict_emoji(score: int) -> str:
    """Map score to emoji."""
    if score >= 85:
        return "👍"
    elif score >= 70:
        return "🤔"
    elif score >= 55:
        return "⚠️"
    else:
        return "👎"


def generate_narrative(
    candidate: dict,
    employer: dict,
    job_opening: dict,
    hiring_pov: dict,
    clusters: dict,
    resume_diff: dict,
    scores: dict
) -> dict:
    """
    Generate the final synthesized narrative.
    
    Returns:
        SynthesizedNarrative dict ready for meta-resume-generator
    """
    
    overall_score = scores.get("overall", 0)
    signal_strength = scores.get("signal_strength", {})
    
    # Prepare context for LLM
    prompt_template = load_prompt("narrate")
    
    # Fill in template
    prompt = prompt_template.replace("{{candidate_name}}", candidate.get("name", "Unknown"))
    prompt = prompt.replace("{{role}}", job_opening.get("title", "Unknown Role"))
    prompt = prompt.replace("{{company}}", employer.get("name", "Unknown"))
    prompt = prompt.replace("{{hiring_pov}}", json.dumps(hiring_pov, indent=2)[:3000])
    prompt = prompt.replace("{{story_clusters}}", json.dumps(clusters.get("story_clusters", [])[:5], indent=2))
    prompt = prompt.replace("{{resume_diff}}", json.dumps(resume_diff, indent=2)[:2000])
    prompt = prompt.replace("{{overall_score}}", str(overall_score))
    prompt = prompt.replace("{{signal_strength}}", json.dumps(signal_strength))
    
    # Call LLM for narrative generation
    llm_result = call_llm(prompt)
    
    # Build final structure, using LLM result where available
    narrative = {
        "candidate": {
            "name": candidate.get("name", "Unknown"),
            "role": f"{job_opening.get('title', 'Candidate')} Candidate",
            "context": f"{candidate.get('current_role', '')} · {candidate.get('current_company', '')}".strip(" ·")
        },
        
        "verdict": {
            "score": overall_score,
            "emoji": get_verdict_emoji(overall_score),
            "action": llm_result.get("verdict", {}).get("action") or get_verdict_action(overall_score),
            "summary": llm_result.get("verdict", {}).get("summary", ""),
            "reasoning": llm_result.get("verdict", {}).get("reasoning", "")
        },
        
        "spikes": llm_result.get("spikes", {
            "up": [],
            "down": []
        }),
        
        "what_they_bring": llm_result.get("what_they_bring", []),
        
        "risks_to_probe": llm_result.get("risks_to_probe", []),
        
        "unveiled_potential": llm_result.get("unveiled_potential", {
            "substantiated": resume_diff.get("substantiated_beyond_resume", []),
            "revealed": resume_diff.get("revealed_beyond_resume", []),
            "transferable": resume_diff.get("transferable_potential", [])
        }),
        
        "interview_questions": llm_result.get("interview_questions", []),
        
        "signal_strength": {
            "story_verified": signal_strength.get("story_verified_pct", 0),
            "resume_only": signal_strength.get("resume_only_pct", 0),
            "inferred": signal_strength.get("inferred_pct", 0)
        },
        
        "methodology": f"{len(clusters.get('story_clusters', []))} story clusters · {sum(c.get('skill_count', 0) for c in clusters.get('story_clusters', []))} skills assessed · Hiring POV alignment scoring",
        
        # Metadata
        "meta": {
            "employer": employer.get("name"),
            "job_opening": job_opening.get("title"),
            "hiring_pov_source": hiring_pov.get("source", "unknown"),
            "clusters_count": len(clusters.get("story_clusters", [])),
            "patterns_count": len(clusters.get("cross_cutting_patterns", []))
        }
    }
    
    # Ensure spikes have required fields
    for spike in narrative["spikes"].get("up", []):
        if "verified" not in spike:
            spike["verified"] = "✓"
        if "importance" not in spike:
            spike["importance"] = 7
    
    for spike in narrative["spikes"].get("down", []):
        if "verified" not in spike:
            spike["verified"] = "✓"
        if "importance" not in spike:
            spike["importance"] = 5
    
    return narrative


def main():
    """CLI for testing narrative generation."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to gathered.json")
    parser.add_argument("--pov", required=True, help="Path to hiring_pov.json")
    parser.add_argument("--clusters", required=True, help="Path to clusters.json")
    parser.add_argument("--diff", required=True, help="Path to resume_diff.json")
    parser.add_argument("--output", default="narrative.json")
    
    args = parser.parse_args()
    
    with open(args.input) as f:
        gathered = json.load(f)
    
    with open(args.pov) as f:
        pov = json.load(f)
    
    with open(args.clusters) as f:
        clusters = json.load(f)
    
    with open(args.diff) as f:
        diff = json.load(f)
    
    narrative = generate_narrative(
        candidate=gathered.get("candidate", {}),
        employer=gathered.get("employer", {}),
        job_opening=gathered.get("job_opening", {}),
        hiring_pov=pov,
        clusters=clusters,
        resume_diff=diff,
        scores=gathered.get("decomposer", {}).get("scores", {})
    )
    
    with open(args.output, "w") as f:
        json.dump(narrative, f, indent=2)
    
    print(f"Narrative saved to {args.output}")
    print(f"  Verdict: {narrative['verdict']['action']} ({narrative['verdict']['score']}/100)")


if __name__ == "__main__":
    main()
