#!/usr/bin/env python3
"""
Step 1: Gather Inputs
---------------------
Collects all data needed for synthesis:
- Candidate info (from Airtable or decomposer)
- Employer info (from Airtable)
- Job Opening + JD text (from Airtable)
- Decomposer output (skills, scores, stories)
- Resume text (downloaded from Airtable attachment)
- Existing Hiring POV (from GDrive if exists)
"""

import json
import os
import sys
import re
from pathlib import Path
import subprocess
import tempfile

import yaml
import requests

# Constants
AIRTABLE_BASE_ID = "appd12asvg42woz9I"
EMPLOYERS_TABLE = "tblvIfVUHxzuBQ2WB"
JOB_OPENINGS_TABLE = "tblHgSEOsoegYnJl7"
CANDIDATES_TABLE = "tblWB2mGbioA8pLBL"

GDRIVE_PIPELINE_FOLDER = "1UVNExCjlCEclCG6x7gj06ChUxP-e9GnM"


def call_zo_airtable(tool_name: str, props: dict, email: str = "vrijen@mycareerspan.com") -> dict:
    """Call Zo's Airtable integration via /zo/ask."""
    prompt = f"""Use the Airtable tool to execute this action.

Tool: {tool_name}
Email: {email}
Props: {json.dumps(props)}

Return ONLY the raw JSON result, no explanation."""

    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
            "content-type": "application/json"
        },
        json={"input": prompt}
    )
    
    result = response.json()
    output = result.get("output", "")
    
    # Parse JSON from response
    try:
        # Try to extract JSON from the response
        if isinstance(output, dict):
            return output
        json_match = re.search(r'\{.*\}|\[.*\]', output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"raw": output}
    except:
        return {"raw": output}


def load_decomposer_output(decomposer_dir: str) -> dict:
    """Load all decomposer output files from a directory."""
    dir_path = Path(decomposer_dir)
    
    result = {
        "skills": [],
        "scores": {},
        "overview": {},
        "jd": {},
        "profile": {},
        "stories": {}
    }
    
    # scores_complete.json
    scores_path = dir_path / "scores_complete.json"
    if scores_path.exists():
        with open(scores_path) as f:
            scores_data = json.load(f)
            result["skills"] = scores_data.get("skills", [])
            result["scores"] = {
                "overall": scores_data.get("overall_score"),
                "signal_strength": scores_data.get("signal_strength", {}),
                "category_scores": scores_data.get("category_scores", {})
            }
    
    # overview.yaml
    overview_path = dir_path / "overview.yaml"
    if overview_path.exists():
        with open(overview_path) as f:
            result["overview"] = yaml.safe_load(f) or {}
    
    # jd.yaml
    jd_path = dir_path / "jd.yaml"
    if jd_path.exists():
        with open(jd_path) as f:
            result["jd"] = yaml.safe_load(f) or {}
    
    # profile.yaml
    profile_path = dir_path / "profile.yaml"
    if profile_path.exists():
        with open(profile_path) as f:
            result["profile"] = yaml.safe_load(f) or {}
    
    # stories.yaml (if exists)
    stories_path = dir_path / "stories.yaml"
    if stories_path.exists():
        with open(stories_path) as f:
            result["stories"] = yaml.safe_load(f) or {}
    
    # careerspan_cleaned.md (raw document for story extraction)
    cleaned_path = dir_path / "careerspan_cleaned.md"
    if cleaned_path.exists():
        with open(cleaned_path) as f:
            result["raw_document"] = f.read()
    
    return result


def download_resume(url: str) -> str:
    """Download resume PDF and extract text."""
    try:
        # Download to temp file
        response = requests.get(url)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(response.content)
            temp_path = f.name
        
        # Use pdftotext to extract
        result = subprocess.run(
            ["pdftotext", "-layout", temp_path, "-"],
            capture_output=True,
            text=True
        )
        
        os.unlink(temp_path)
        return result.stdout
        
    except Exception as e:
        print(f"[WARN] Could not extract resume text: {e}")
        return ""


def gather_inputs(
    candidate_id: str = None,
    decomposer_dir: str = None,
    employer_name: str = None
) -> dict:
    """
    Gather all inputs for synthesis.
    
    Args:
        candidate_id: Airtable candidate record ID
        decomposer_dir: Path to decomposer output (alternative to candidate_id)
        employer_name: Employer name (required with decomposer_dir)
    
    Returns:
        Gathered inputs dict
    """
    
    result = {
        "candidate": {},
        "employer": {},
        "job_opening": {},
        "decomposer": {},
        "resume_text": "",
        "existing_hiring_pov": None
    }
    
    # =========================================================================
    # Path A: From Airtable candidate ID
    # =========================================================================
    if candidate_id:
        # Get candidate record
        # Note: In practice, we'd use Zo's app tools. For now, simulate structure.
        # This will be called via the pipeline which has access to Zo tools.
        
        result["candidate"] = {
            "id": candidate_id,
            "name": "Unknown",  # Will be populated by caller
            "email": ""
        }
        
        # The actual Airtable calls happen in run_pipeline.py which has Zo access
        # This function is called from there with pre-fetched data
        
        raise NotImplementedError(
            "Direct Airtable lookup not implemented. "
            "Use --decomposer-dir or call from run_pipeline.py with Zo access."
        )
    
    # =========================================================================
    # Path B: From decomposer directory + employer name
    # =========================================================================
    if decomposer_dir:
        decomposer_data = load_decomposer_output(decomposer_dir)
        result["decomposer"] = decomposer_data
        
        # Extract candidate info from decomposer output
        overview = decomposer_data.get("overview", {})
        profile = decomposer_data.get("profile", {})
        jd = decomposer_data.get("jd", {})
        
        candidate_info = overview.get("candidate", {}) or profile.get("candidate", {})
        
        result["candidate"] = {
            "name": candidate_info.get("name", "Unknown"),
            "email": candidate_info.get("email", ""),
            "current_role": candidate_info.get("position_applied", ""),
            "current_company": candidate_info.get("company", "")
        }
        
        result["employer"] = {
            "name": employer_name or candidate_info.get("company", "Unknown"),
            "id": None  # No Airtable ID when using local files
        }
        
        result["job_opening"] = {
            "title": jd.get("title") or jd.get("position") or candidate_info.get("position_applied", ""),
            "jd_text": jd.get("full_text") or jd.get("description", ""),
            "id": None
        }
        
        # Try to find resume in decomposer dir or parent
        decomposer_path = Path(decomposer_dir)
        possible_resume_paths = [
            decomposer_path / "resume.pdf",
            decomposer_path / "resume.txt",
            decomposer_path.parent / f"{result['candidate']['name'].lower()}_resume.pdf"
        ]
        
        for resume_path in possible_resume_paths:
            if resume_path.exists():
                if resume_path.suffix == ".pdf":
                    result["resume_text"] = download_resume(f"file://{resume_path}")
                else:
                    result["resume_text"] = resume_path.read_text()
                break
    
    return result


def main():
    """CLI for testing gather step."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--decomposer-dir", required=True)
    parser.add_argument("--employer-name", required=True)
    parser.add_argument("--output", default="gathered.json")
    
    args = parser.parse_args()
    
    result = gather_inputs(
        decomposer_dir=args.decomposer_dir,
        employer_name=args.employer_name
    )
    
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"Gathered inputs saved to {args.output}")


if __name__ == "__main__":
    main()
