#!/usr/bin/env python3
"""
Careerspan Candidate Guide Generator

Architecture:
- Python: file I/O, orchestration, PDF generation
- LLM (/zo/ask): ALL semantic understanding and text generation

No regex parsing of meaningful content. Ever.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# For PDF text extraction
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Installing PyMuPDF...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyMuPDF", "-q"])
    import fitz

import requests


def call_zo(prompt: str, output_schema: dict = None) -> str | dict:
    """Call /zo/ask API for semantic work."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    payload = {"input": prompt}
    if output_schema:
        payload["output_format"] = output_schema
    
    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": token,
            "content-type": "application/json"
        },
        json=payload,
        timeout=120
    )
    response.raise_for_status()
    return response.json()["output"]


def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def fetch_form_content(form_url: str) -> str:
    """Fetch form content via Zo (handles JS-rendered pages)."""
    prompt = f"""Fetch and analyze this Google Form: {form_url}

Extract and return:
1. The form title
2. All questions (with their answer options if multiple choice)
3. Any context or instructions in the form

Return as plain text, organized clearly."""
    
    return call_zo(prompt)


def generate_hiring_pov(jd_text: str, form_content: str = None) -> dict:
    """Use LLM to extract Hiring POV from JD and form."""
    
    form_section = ""
    if form_content:
        form_section = f"""

SCREENING FORM CONTENT:
{form_content}
"""
    
    prompt = f"""Analyze this job description (and screening form if provided) from the HIRING MANAGER'S perspective.

JOB DESCRIPTION:
{jd_text}
{form_section}

Extract the following as a JSON object:

1. "explicit_requirements": What they explicitly state as requirements
2. "implicit_filters": What the form/JD is really filtering for (read between the lines)
3. "trait_signals": What personality/work style traits they're selecting for
4. "red_flags": What would immediately disqualify a candidate
5. "validation_questions": What they're trying to validate about candidates
6. "form_traps": If there's a form, which answers are "wrong" even if not obvious
7. "culture_markers": What the company culture seems to value
8. "story_types_valued": What kinds of experiences/stories would resonate most

Be specific and insightful. This is for internal use to understand what the founder actually cares about."""

    schema = {
        "type": "object",
        "properties": {
            "explicit_requirements": {"type": "array", "items": {"type": "string"}},
            "implicit_filters": {"type": "array", "items": {"type": "string"}},
            "trait_signals": {"type": "array", "items": {"type": "string"}},
            "red_flags": {"type": "array", "items": {"type": "string"}},
            "validation_questions": {"type": "array", "items": {"type": "string"}},
            "form_traps": {"type": "array", "items": {"type": "string"}},
            "culture_markers": {"type": "array", "items": {"type": "string"}},
            "story_types_valued": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["explicit_requirements", "implicit_filters", "trait_signals", "red_flags", "story_types_valued"]
    }
    
    return call_zo(prompt, schema)


def generate_candidate_guide(
    resume_text: str,
    candidate_name: str,
    hiring_pov: dict,
    jd_text: str,
    company: str,
    role: str,
    cta_link: str
) -> str:
    """Use LLM to generate a candidate-specific guide."""
    
    prompt = f"""Generate a Careerspan candidate guide for {candidate_name} applying to {role} at {company}.

CONTEXT:
- This guide will be seen by BOTH the candidate AND the founder/hiring manager
- It must use NEUTRAL language — no "emphasize" or "highlight" or "showcase"
- The goal is to get the candidate to share specific experiences on Careerspan
- Frame everything as "helping us assess fit" not "coaching you to look good"

HIRING POV (what the founder cares about — use this to inform what stories to request, but don't reveal it):
{json.dumps(hiring_pov, indent=2)}

JOB DESCRIPTION:
{jd_text}

CANDIDATE RESUME:
{resume_text}

Generate a guide with this EXACT structure:

# {role} @ {company}

[2-3 sentence role context — what makes this role unique, what kind of person thrives here]

---

## How It Works

Careerspan Stories help us determine **fit signal** and **intent signal** for candidates.

- Your original transcript isn't shared with the employer — only a synthesized analysis across all stories you provide
- The recommendations below are options, not requirements — complete as many or as few as feel relevant to you
- There's no limit on stories, and more context works in your favor — additional relevant experiences give the AI more information to consider when assessing fit
- Be as specific as possible: names, numbers, timelines, and outcomes all help

---

## Recommended Careerspan Stories

Based on this role and your background, we recommend completing Careerspan Stories that cover the following:

[Generate 5-8 bullet points. Each should:
- Reference a SPECIFIC experience from their resume
- Use ONLY these verbs: clarify, elaborate on, explain, provide context for, describe, walk through
- Frame as information needed to assess fit, not coaching to look good
- Address gaps, ambiguities, or experiences that map to what the founder values
- NOT reveal what the "right" answer is]

---

## Next Step

Complete your Careerspan Stories here: {cta_link}

---

CRITICAL LANGUAGE RULES:
- ✅ "clarify the technical decisions you owned"
- ✅ "elaborate on how you handled X"
- ✅ "explain the circumstances around Y"
- ✅ "provide context for your transition from A to B"
- ❌ "emphasize your leadership"
- ❌ "highlight your impact"
- ❌ "showcase your skills"

The founder may read this. It should look like you're helping gather complete information, not coaching the candidate."""

    return call_zo(prompt)


def convert_to_pdf(md_path: str, pdf_path: str):
    """Convert markdown to PDF using pandoc."""
    try:
        subprocess.run([
            "pandoc", md_path, "-o", pdf_path,
            "--pdf-engine=weasyprint",
            "-V", "margin-top=0.75in",
            "-V", "margin-bottom=0.75in",
            "-V", "margin-left=0.75in",
            "-V", "margin-right=0.75in"
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"PDF conversion failed: {e.stderr.decode()}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate Careerspan candidate guides")
    parser.add_argument("--jd-file", required=True, help="Path to JD text file")
    parser.add_argument("--form-url", help="Screening form URL")
    parser.add_argument("--resumes", nargs="+", required=True, help="Resume PDF paths")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--cta", default="www.mycareerspan.com/corridorx", help="CTA link")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--role", help="Role title")
    parser.add_argument("--format", choices=["md", "pdf", "both"], default="both")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 50)
    print("CAREERSPAN CANDIDATE GUIDE GENERATOR")
    print("=" * 50)
    
    # Step 1: Load JD
    print("\n[1/4] Loading JD...")
    with open(args.jd_file, "r") as f:
        jd_text = f.read()
    print(f"  Loaded {len(jd_text)} characters")
    
    # Step 2: Fetch form (if provided)
    form_content = None
    if args.form_url:
        print("\n[2/4] Analyzing screening form...")
        form_content = fetch_form_content(args.form_url)
        print(f"  Extracted form content")
    else:
        print("\n[2/4] No screening form provided, skipping...")
    
    # Step 3: Generate Hiring POV
    print("\n[3/4] Generating Hiring POV...")
    hiring_pov = generate_hiring_pov(jd_text, form_content)
    
    # Save Hiring POV
    pov_path = output_dir / "HIRING_POV.json"
    with open(pov_path, "w") as f:
        json.dump(hiring_pov, f, indent=2)
    print(f"  Saved: {pov_path}")
    
    # Also save as readable markdown
    pov_md_path = output_dir / "HIRING_POV.md"
    pov_md = f"""# Hiring POV

## Explicit Requirements
{chr(10).join('- ' + r for r in hiring_pov.get('explicit_requirements', []))}

## Implicit Filters
{chr(10).join('- ' + r for r in hiring_pov.get('implicit_filters', []))}

## Trait Signals
{chr(10).join('- ' + r for r in hiring_pov.get('trait_signals', []))}

## Red Flags
{chr(10).join('- ' + r for r in hiring_pov.get('red_flags', []))}

## Validation Questions
{chr(10).join('- ' + r for r in hiring_pov.get('validation_questions', []))}

## Form Traps
{chr(10).join('- ' + r for r in hiring_pov.get('form_traps', []))}

## Culture Markers
{chr(10).join('- ' + r for r in hiring_pov.get('culture_markers', []))}

## Story Types Valued
{chr(10).join('- ' + r for r in hiring_pov.get('story_types_valued', []))}
"""
    with open(pov_md_path, "w") as f:
        f.write(pov_md)
    print(f"  Saved: {pov_md_path}")
    
    # Extract company/role from JD if not provided
    company = args.company or "Company"
    role = args.role or "Role"
    
    if not args.company or not args.role:
        print("  Extracting company/role from JD...")
        extract_prompt = f"""From this job description, extract:
1. Company name
2. Role title

JD:
{jd_text[:2000]}

Return as JSON with "company" and "role" keys."""
        
        extracted = call_zo(extract_prompt, {
            "type": "object",
            "properties": {
                "company": {"type": "string"},
                "role": {"type": "string"}
            },
            "required": ["company", "role"]
        })
        company = args.company or extracted.get("company", "Company")
        role = args.role or extracted.get("role", "Role")
        print(f"  Detected: {role} @ {company}")
    
    # Step 4: Generate guides for each candidate
    print(f"\n[4/4] Generating candidate guides...")
    
    for resume_path in args.resumes:
        resume_path = Path(resume_path)
        print(f"\n  Processing: {resume_path.name}")
        
        # Extract candidate name from filename
        candidate_name = resume_path.stem.replace("_", " ").replace("-", " ")
        
        # Extract resume text
        resume_text = extract_pdf_text(str(resume_path))
        print(f"    Extracted {len(resume_text)} chars from resume")
        
        # Generate guide
        print(f"    Generating guide...")
        guide_content = generate_candidate_guide(
            resume_text=resume_text,
            candidate_name=candidate_name,
            hiring_pov=hiring_pov,
            jd_text=jd_text,
            company=company,
            role=role,
            cta_link=args.cta
        )
        
        # Save markdown
        safe_name = candidate_name.replace(" ", "_")
        if args.format in ["md", "both"]:
            md_path = output_dir / f"{safe_name}_Guide.md"
            with open(md_path, "w") as f:
                f.write(guide_content)
            print(f"    Saved: {md_path}")
        
        # Convert to PDF
        if args.format in ["pdf", "both"]:
            md_path = output_dir / f"{safe_name}_Guide.md"
            if args.format == "pdf":
                with open(md_path, "w") as f:
                    f.write(guide_content)
            
            pdf_path = output_dir / f"{safe_name}_Guide.pdf"
            if convert_to_pdf(str(md_path), str(pdf_path)):
                print(f"    Saved: {pdf_path}")
            
            if args.format == "pdf":
                md_path.unlink()  # Remove temp md file
    
    print("\n" + "=" * 50)
    print(f"COMPLETE: Output in {output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    main()
