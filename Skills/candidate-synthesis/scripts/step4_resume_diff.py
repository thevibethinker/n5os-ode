#!/usr/bin/env python3
"""
Step 4: Resume Diff
-------------------
Compares resume vs Careerspan findings to identify:
- Substantiated: Resume claimed it, Careerspan verified
- Revealed: Careerspan found it, resume didn't mention
- Unverified: Resume claimed it, Careerspan couldn't verify
- Transferable: Abilities that transfer to target role
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


def diff_resume(resume_text: str, skills: list, clusters: dict) -> dict:
    """
    Compare resume against Careerspan findings.
    
    Args:
        resume_text: Extracted text from resume
        skills: List of skill dicts from decomposer
        clusters: Story clusters from step 3
    
    Returns:
        Resume diff dict
    """
    
    # If no resume text, return based on evidence types alone
    if not resume_text or len(resume_text.strip()) < 100:
        print("[WARN] No resume text available. Using evidence-type-based diff.")
        return diff_by_evidence_type(skills, clusters)
    
    # Prepare skills summary for LLM
    skills_summary = []
    for s in skills[:30]:  # Limit to avoid token overflow
        skills_summary.append({
            "skill": s.get("skill_name"),
            "rating": s.get("rating"),
            "evidence_type": s.get("evidence_type"),
            "our_take": (s.get("our_take") or "")[:300]
        })
    
    # Prepare clusters summary
    clusters_summary = []
    for c in clusters.get("story_clusters", [])[:5]:
        clusters_summary.append({
            "theme": c.get("theme"),
            "narrative": c.get("narrative"),
            "evidence_strength": c.get("evidence_strength")
        })
    
    prompt_template = load_prompt("diff_resume")
    prompt = prompt_template.replace("{{resume_text}}", resume_text[:5000])  # Truncate
    prompt = prompt.replace("{{skills_json}}", json.dumps(skills_summary, indent=2))
    prompt = prompt.replace("{{story_clusters}}", json.dumps(clusters_summary, indent=2))
    
    result = call_llm(prompt)
    
    # Ensure all required fields exist
    return {
        "substantiated_beyond_resume": result.get("substantiated_beyond_resume", []),
        "revealed_beyond_resume": result.get("revealed_beyond_resume", []),
        "unverified_claims": result.get("unverified_claims", []),
        "transferable_potential": result.get("transferable_potential", [])
    }


def diff_by_evidence_type(skills: list, clusters: dict) -> dict:
    """
    Fallback diff based on evidence types when no resume text available.
    """
    
    substantiated = []
    revealed = []
    
    for skill in skills:
        evidence = skill.get("evidence_type", "")
        rating = skill.get("rating")
        
        if not evidence:
            continue
        
        evidence_lower = evidence.lower()
        
        # Story+profile = substantiated
        if "story" in evidence_lower and "profile" in evidence_lower:
            if rating == "Excellent":
                substantiated.append({
                    "resume_claim": skill.get("skill_name"),
                    "careerspan_evidence": f"Verified with story evidence. Rating: {rating}",
                    "confidence_boost": "Resume claim backed by behavioral evidence"
                })
        
        # Story only (not profile) = revealed beyond resume
        elif "story" in evidence_lower:
            revealed.append({
                "finding": skill.get("skill_name"),
                "resume_gap": "Not explicitly mentioned on resume",
                "why_it_matters": skill.get("our_take", "")[:200]
            })
    
    # Add cross-cutting patterns as revealed insights
    for pattern in clusters.get("cross_cutting_patterns", []):
        revealed.append({
            "finding": pattern.get("pattern"),
            "resume_gap": pattern.get("description"),
            "why_it_matters": pattern.get("employer_relevance")
        })
    
    return {
        "substantiated_beyond_resume": substantiated[:5],
        "revealed_beyond_resume": revealed[:5],
        "unverified_claims": [],
        "transferable_potential": []
    }


def main():
    """CLI for testing resume diff."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to gathered.json")
    parser.add_argument("--clusters", required=True, help="Path to clusters.json")
    parser.add_argument("--output", default="resume_diff.json")
    
    args = parser.parse_args()
    
    with open(args.input) as f:
        gathered = json.load(f)
    
    with open(args.clusters) as f:
        clusters = json.load(f)
    
    skills = gathered.get("decomposer", {}).get("skills", [])
    resume_text = gathered.get("resume_text", "")
    
    diff = diff_resume(resume_text, skills, clusters)
    
    with open(args.output, "w") as f:
        json.dump(diff, f, indent=2)
    
    print(f"Resume diff saved to {args.output}")
    print(f"  Substantiated: {len(diff.get('substantiated_beyond_resume', []))}")
    print(f"  Revealed: {len(diff.get('revealed_beyond_resume', []))}")


if __name__ == "__main__":
    main()
