#!/usr/bin/env python3
"""
Step 2: Ensure Hiring POV
-------------------------
Generates Hiring POV from JD if not found, stores in GDrive, links to Airtable.
Uses shared careerspan_hiring_intel module for canonical POV generation.
"""

import json
import os
import sys
from pathlib import Path

# Import shared Hiring POV generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from careerspan_hiring_intel.scripts.hiring_pov import (
    generate_hiring_pov as core_generate_hiring_pov,
    format_pov_markdown as core_format_pov_markdown
)


def generate_hiring_pov(jd_text: str, company_context: str = "") -> dict:
    """
    Generate Hiring POV from JD text using shared careerspan-core module.
    
    Args:
        jd_text: The job description text
        company_context: Additional context about the company
        
    Returns:
        Structured POV dict matching canonical schema
    """
    # Extract employer/role from company_context if available
    employer_name = "Unknown"
    role_title = "Unknown Role"
    
    if company_context:
        if "Company:" in company_context:
            employer_name = company_context.split("Company:")[1].strip().split()[0]
    
    return core_generate_hiring_pov(
        jd_text=jd_text,
        employer_name=employer_name,
        role_title=role_title,
        company_context=company_context
    )


def format_pov_markdown(pov: dict, employer_name: str, role_title: str) -> str:
    """Format Hiring POV as markdown for GDrive storage using shared module."""
    return core_format_pov_markdown(pov, employer_name, role_title)


def ensure_hiring_pov(gathered: dict, skip_generation: bool = False) -> dict:
    """
    Ensure Hiring POV exists, generating if needed.
    
    Args:
        gathered: Output from step1_gather
        skip_generation: If True, return empty POV instead of generating
    
    Returns:
        Hiring POV dict with structured fields
    """
    
    employer = gathered.get("employer", {})
    job_opening = gathered.get("job_opening", {})
    
    employer_name = employer.get('name', 'Unknown')
    role_title = job_opening.get('title', 'Unknown Role')
    
    # Check if existing POV was found in gather step
    existing_pov = gathered.get("existing_hiring_pov")
    if existing_pov:
        return {
            **existing_pov,
            "generated": False,
            "source": "gdrive"
        }
    
    # Check local files (for decomposer-dir workflow)
    decomposer = gathered.get("decomposer", {})
    if decomposer:
        pass
    
    if skip_generation:
        return {
            "explicit_requirements": [],
            "implicit_filters": [],
            "trait_signals": [],
            "red_flags": [],
            "story_types_valued": [],
            "validation_questions": [],
            "culture_markers": [],
            "role_summary": "",
            "missing_info": [],
            "generated": False,
            "source": "none"
        }
    
    # Generate from JD
    jd_text = job_opening.get("jd_text", "")
    
    if not jd_text:
        print("[WARN] No JD text available. Using minimal POV.")
        return {
            "explicit_requirements": [],
            "implicit_filters": [],
            "trait_signals": [],
            "red_flags": [],
            "story_types_valued": [],
            "validation_questions": [],
            "culture_markers": [],
            "role_summary": "",
            "missing_info": [],
            "generated": False,
            "source": "none",
            "warning": "No JD text available"
        }
    
    print(f"[POV] Generating Hiring POV for {role_title} @ {employer_name}...")
    
    pov = core_generate_hiring_pov(
        jd_text=jd_text,
        employer_name=employer_name,
        role_title=role_title,
        company_context=f"Company: {employer_name}"
    )
    
    pov["generated"] = True
    pov["source"] = "llm"
    
    # TODO: In production, also:
    # 1. Save to GDrive: Careerspan Pipeline Outputs/{Employer}/hiring-povs/{Role}_Hiring-POV.md
    # 2. Update Airtable Employer record: Hiring POV (Gdrive) field
    # These require Zo app tools which are called from the orchestrator
    
    return pov


def main():
    """CLI for testing POV generation."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to gathered.json from step 1")
    parser.add_argument("--output", default="hiring_pov.json")
    parser.add_argument("--skip-generation", action="store_true")
    
    args = parser.parse_args()
    
    with open(args.input) as f:
        gathered = json.load(f)
    
    pov = ensure_hiring_pov(gathered, skip_generation=args.skip_generation)
    
    with open(args.output, "w") as f:
        json.dump(pov, f, indent=2)
    
    print(f"Hiring POV saved to {args.output}")
    print(f"  Generated: {pov.get('generated', False)}")
    print(f"  Source: {pov.get('source', 'unknown')}")


if __name__ == "__main__":
    main()
