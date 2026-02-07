#!/usr/bin/env python3
"""
JD Decomposition Script

Analyzes a job description to extract:
- Explicit requirements (what they say they want)
- Implicit signals (what they actually want)
- Employer psychology (founder/hiring manager mindset)
- Red flags they're screening for
"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path


def call_zo(prompt: str) -> str:
    """Call Zo API for LLM analysis."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": token,
            "content-type": "application/json"
        },
        json={"input": prompt}
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"Zo API error: {response.status_code} - {response.text}")
    
    return response.json()["output"]


def read_jd(jd_source: str) -> str:
    """Read JD from URL or file path."""
    if jd_source.startswith("http"):
        # Use Zo to fetch and extract the JD content
        prompt = f"""Fetch and extract the job description from this URL: {jd_source}

Return ONLY the job description content as plain text. Include:
- Job title
- Company name
- All requirements and qualifications
- Responsibilities
- Any other relevant details about the role

Do not include navigation, headers, footers, or other page chrome."""
        return call_zo(prompt)
    else:
        # Read from file
        return Path(jd_source).read_text()


def read_form(form_url: str) -> str:
    """Read screening form content."""
    prompt = f"""Fetch and extract all questions from this screening form: {form_url}

Return a structured list of every question, including:
- The question text
- Whether it's required or optional
- The answer options (if multiple choice)

Format as a clear list."""
    return call_zo(prompt)


def decompose_jd(jd_text: str, form_text: str = None) -> dict:
    """Decompose JD into structured analysis."""
    
    form_context = ""
    if form_text:
        form_context = f"""

SCREENING FORM:
{form_text}

Analyze the form questions to understand what they're filtering for. What do the questions reveal about the employer's priorities and concerns?"""

    prompt = f"""Analyze this job description and extract structured insights.

JOB DESCRIPTION:
{jd_text}
{form_context}

Return your analysis as JSON with these exact keys:

{{
  "role_title": "The job title",
  "company_name": "Company name",
  "explicit_requirements": [
    "List each stated requirement"
  ],
  "implicit_signals": [
    {{
      "signal": "What they actually want but didn't explicitly say",
      "evidence": "What in the JD suggests this"
    }}
  ],
  "employer_psychology": {{
    "what_they_fear": "What kind of candidate are they trying to avoid?",
    "what_excites_them": "What would make them say 'this is the one'?",
    "decision_style": "How do they seem to make decisions? (fast/slow, intuition/data, etc.)",
    "culture_signals": "What does the JD reveal about company culture?"
  }},
  "screening_priorities": [
    {{
      "priority": "What they're filtering for",
      "how_tested": "How they assess this (form question, interview, etc.)"
    }}
  ],
  "red_flags_for_them": [
    "Candidate traits that would disqualify someone"
  ],
  "form_insights": {{
    "trick_questions": ["Questions designed to filter out certain candidates"],
    "optimal_answers": {{"question_summary": "best answer approach"}}
  }}
}}

Return ONLY valid JSON, no other text."""

    response = call_zo(prompt)
    
    # Parse JSON from response (handle potential markdown wrapping)
    json_text = response
    if "```json" in response:
        json_text = response.split("```json")[1].split("```")[0]
    elif "```" in response:
        json_text = response.split("```")[1].split("```")[0]
    
    return json.loads(json_text.strip())


def main():
    parser = argparse.ArgumentParser(description="Decompose a job description")
    parser.add_argument("--jd", required=True, help="JD URL or file path")
    parser.add_argument("--form", help="Screening form URL (optional)")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()
    
    print(f"Reading JD from: {args.jd}")
    jd_text = read_jd(args.jd)
    
    form_text = None
    if args.form:
        print(f"Reading form from: {args.form}")
        form_text = read_form(args.form)
    
    print("Decomposing JD...")
    analysis = decompose_jd(jd_text, form_text)
    
    if args.output:
        Path(args.output).write_text(json.dumps(analysis, indent=2))
        print(f"Analysis saved to: {args.output}")
    else:
        print(json.dumps(analysis, indent=2))
    
    return analysis


if __name__ == "__main__":
    main()
