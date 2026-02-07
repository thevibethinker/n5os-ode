#!/usr/bin/env python3
"""
Careerspan JD Intake Processor

Processes [JD] tagged emails from Shivam:
1. Extracts company, role, JD content via LLM
2. Creates Job Opening in Airtable
3. Generates Hiring POV
4. Uploads to shared Drive
5. Emails Shivam with POV link + missing Core Questions

Architecture:
- Python: orchestration, file handling, output
- LLM (/zo/ask): ALL semantic extraction and generation
- Zo tools: Airtable, Drive, Gmail (called by orchestrator, not this script)

Usage:
    python3 process_jd.py --email-subject "..." --email-body "..." --email-from "..."
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import requests

# Import shared Hiring POV generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from careerspan_hiring_intel.scripts.hiring_pov import generate_hiring_pov_with_markdown

# For PDF text extraction
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Installing PyMuPDF...", file=sys.stderr)
    subprocess.run([sys.executable, "-m", "pip", "install", "PyMuPDF", "-q"])
    import fitz

# Configuration
CONFIG = {
    "airtable": {
        "base_id": "appd12asvg42woz9I",
        "job_openings_table": "tblHgSEOsoegYnJl7",
        "employers_table": "tblvIfVUHxzuBQ2WB",
        "activity_log_table": "tblGpSaOO5mEBXMU8",
        "account": "vrijen@mycareerspan.com"
    },
    "drive": {
        "shared_folder_id": "1UVNExCjlCEclCG6x7gj06ChUxP-e9GnM",
        "account": "vrijen@mycareerspan.com"
    },
    "gmail": {
        "account": "vrijen@mycareerspan.com",
        "cc": ["attawar.v@gmail.com", "me@vrijenattawar.com"]
    },
    "permitted_senders": ["shivam@corridorx.io"],
    "core_questions": [
        {"id": "salary_range", "label": "Salary Range"},
        {"id": "location", "label": "Location/Geography"},
        {"id": "visa_sponsorship", "label": "Visa Sponsorship"},
        {"id": "ninety_day_success", "label": "90-Day Success"},
        {"id": "anti_pattern", "label": "Anti-Pattern"}
    ]
}

JOB_LINK_DOMAINS = ("jobs.ashbyhq.com", "greenhouse.io", "lever.co")


def extract_urls(text: str) -> list[str]:
    if not text:
        return []
    urls = re.findall(r"https?://[^\s)\]]+", text)
    # strip trailing punctuation
    cleaned = []
    for u in urls:
        cleaned.append(u.rstrip(".,;!"))
    return list(dict.fromkeys(cleaned))


def extract_job_links(text: str) -> list[str]:
    urls = extract_urls(text)
    job_urls = []
    for u in urls:
        lu = u.lower()
        if any(dom in lu for dom in JOB_LINK_DOMAINS):
            job_urls.append(u)
    return job_urls


def email_looks_like_jd(subject: str, body: str) -> bool:
    subj = (subject or "").strip().upper()
    b = (body or "").lower()
    if "[JD]" in subj:
        return True
    if subj == "JD":
        return True
    if any(dom in b for dom in JOB_LINK_DOMAINS):
        return True
    return False


def fetch_url_text(url: str, timeout: int = 20, max_chars: int = 120_000) -> str:
    """Fetch raw HTML/text from a URL for LLM parsing. Best-effort, no JS rendering."""
    try:
        resp = requests.get(
            url,
            headers={"user-agent": "Mozilla/5.0 (Zo Careerspan JD Intake)"},
            timeout=timeout,
        )
        resp.raise_for_status()
        text = resp.text or ""
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[truncated]"
        return text
    except Exception as e:
        return f"[URL FETCH FAILED] {url}\nERROR: {e}"


def map_location_choice(location_str: str) -> str | None:
    s = (location_str or "").lower()
    if "remote" in s:
        return "Remote"
    if "new york" in s or "nyc" in s or "ny" in s:
        return "NY"
    if "san francisco" in s or "sf" in s:
        return "SF"
    if "bangalore" in s:
        return "Bangalore"
    if "hyderabad" in s:
        return "Hyderabad"
    return None


def map_employment_type(text: str) -> str:
    s = (text or "").lower()
    if "part" in s and "time" in s:
        return "Part-time"
    if "contract" in s:
        return "Contract"
    if "intern" in s:
        return "Internship"
    return "Full-time"


def call_zo(prompt: str, output_schema: dict = None, timeout: int = 120) -> str | dict:
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
        timeout=timeout
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


def extract_jd_details(jd_text: str, email_subject: str) -> dict:
    """Use LLM to extract structured details from JD text."""
    
    json_template = '''{
  "company": "Company name string",
  "role": "Role/position title string",
  "location": "Location mentioned or 'Not specified'",
  "employment_type": "Full-time / Part-time / Contract / Internship / Temporary / Not specified",
  "requirements": ["requirement 1", "requirement 2"],
  "responsibilities": ["responsibility 1"],
  "compensation": "Any compensation info or null",
  "core_questions_answered": {
    "salary_range": true,
    "location": true,
    "visa_sponsorship": false,
    "ninety_day_success": false,
    "anti_pattern": false
  }
}'''
    
    prompt = f"""Extract details from this job description email and return as valid JSON only.

EMAIL SUBJECT: {email_subject}

JD CONTENT:
{jd_text[:8000]}

Return ONLY a JSON object with these fields (no markdown, no explanation, just JSON):

{json_template}

For core_questions_answered, set true only if the JD EXPLICITLY answers that question:
- salary_range: Is salary/compensation range specified?
- location: Are location/geo constraints clearly defined?
- visa_sponsorship: Is visa policy mentioned?
- ninety_day_success: Are 90-day goals or first deliverables mentioned?
- anti_pattern: Is there info about who shouldn't apply?

Be precise. Extract exactly what's stated. Return ONLY valid JSON."""

    response = call_zo(prompt)
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        start = response.find('{')
        if start != -1:
            depth = 0
            for i, c in enumerate(response[start:], start):
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        return json.loads(response[start:i+1])
        raise ValueError(f"Could not parse JSON from LLM response: {response[:500]}")


def generate_hiring_pov(jd_details: dict, jd_text: str) -> str:
    """Generate Hiring POV markdown document using shared careerspan-core module."""
    _, markdown = generate_hiring_pov_with_markdown(
        jd_text=jd_text,
        employer_name=jd_details['company'],
        role_title=jd_details['role'],
        company_context=f"Location: {jd_details.get('location', 'Not specified')}"
    )
    return markdown


def generate_branded_pdf(md_path: Path, title: str) -> Path | None:
    branded_script = Path("/home/workspace/Skills/branded-pdf/scripts/generate_pdf.py")
    logo_path = Path("/home/workspace/Sites/interview-reviewer/public/careerspan-logo.png")
    if not branded_script.exists():
        return None

    out_pdf = md_path.with_suffix(".pdf")
    cmd = [
        sys.executable,
        str(branded_script),
        "--input",
        str(md_path),
        "--output",
        str(out_pdf),
        "--title",
        title,
    ]
    if logo_path.exists():
        cmd.extend(["--logo", str(logo_path)])

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        if out_pdf.exists() and out_pdf.stat().st_size > 0:
            return out_pdf
    except Exception:
        return None
    return None


def generate_shivam_email(jd_details: dict, hiring_pov_link: str, missing_questions: list) -> dict:
    """Generate email content for Shivam."""
    
    company = jd_details["company"]
    role = jd_details["role"]
    
    question_labels = {
        "salary_range": "Salary range (and whether it should be visible to candidates)",
        "location": "Location constraints (geo/remote/hybrid/timezone)",
        "visa_sponsorship": "Visa sponsorship policy",
        "ninety_day_success": "Top 3 deliverables / 90-day success criteria",
        "anti_pattern": "Anti-pattern (who should NOT apply)"
    }
    
    if missing_questions:
        questions_text = "\n".join(f"- {question_labels.get(q, q)}" for q in missing_questions)
        questions_section = f"""Before we match candidates, we need:
{questions_text}
"""
    else:
        questions_section = "All 5 Core Questions appear to be answered in the JD."
    
    body = f"""Hiring POV for {role} @ {company} is ready.

Drive link: {hiring_pov_link}

{questions_section}

— Zo (on V’s behalf)"""
    
    subject = f"Hiring POV for {role} @ {company}"
    
    return {
        "subject": subject,
        "body": body
    }


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50]


def extract_job_opening_insights(jd_text, hiring_pov_md, company, role):
    prompt = f"""Extract insights from this job description and hiring POV to populate Airtable Job Opening fields.

Company: {company}
Role: {role}

JD CONTENT:
{jd_text[:8000]}

Hiring POV:
{hiring_pov_md[:8000]}

Return ONLY a JSON object with these fields (no markdown, no explanation, just JSON):

{
  "technical_stack": "string, bullet list",
  "cultural_preferences": "string, bullet list",
  "implicit_signals": "string, bullet list",
  "employer_psychology": "string, 2-4 sentences",
  "anti_pattern_description": "string, bullet list",
  "location_notes": "string",
  "work_authorization_notes": "string",
  "ninety_day_success_criteria": "string"
}

These are internal analysis fields. Quote explicit facts when present, but you may infer likely signals and expectations when the JD implies them. If something is unknowable from the inputs, use "Unknown". Return ONLY valid JSON."""

    response = call_zo(prompt)
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        start = response.find('{')
        if start != -1:
            depth = 0
            for i, c in enumerate(response[start:], start):
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        return json.loads(response[start:i+1])
        raise ValueError(f"Could not parse JSON from LLM response: {response[:500]}")


def main():
    parser = argparse.ArgumentParser(description="Process [JD] tagged emails for Careerspan pipeline")
    parser.add_argument("--email-subject", required=True, help="Email subject line")
    parser.add_argument("--email-body", required=True, help="Email body content")
    parser.add_argument("--email-from", required=True, help="Sender email address")
    parser.add_argument("--email-thread-id", default="", help="Gmail thread ID (optional)")
    parser.add_argument("--attachments", nargs="*", help="Paths to attachment files")
    parser.add_argument("--dry-run", action="store_true", help="Process without creating records or sending emails")
    
    args = parser.parse_args()
    
    if args.email_from.lower() not in [s.lower() for s in CONFIG["permitted_senders"]]:
        print(json.dumps({
            "error": "Sender not permitted",
            "sender": args.email_from,
            "permitted": CONFIG["permitted_senders"]
        }))
        sys.exit(1)

    if not email_looks_like_jd(args.email_subject, args.email_body):
        print(json.dumps({
            "error": "Email does not look like a JD (missing [JD] tag and no supported job link)",
            "subject": args.email_subject
        }))
        sys.exit(1)
    
    print("=" * 60, file=sys.stderr)
    print("CAREERSPAN JD INTAKE PROCESSOR", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    print("\n[1/5] Gathering JD content...", file=sys.stderr)
    jd_text = args.email_body or ""

    # Fetch job board links if present
    links = extract_job_links(args.email_body)
    if links:
        print(f"  Found {len(links)} job link(s)", file=sys.stderr)
        for url in links:
            print(f"  Fetching: {url}", file=sys.stderr)
            fetched = fetch_url_text(url)
            jd_text += f"\n\n--- LINK: {url} ---\n\n" + fetched

    if args.attachments:
        for attachment_path in args.attachments:
            path = Path(attachment_path)
            if path.exists():
                if path.suffix.lower() == ".pdf":
                    print(f"  Extracting text from {path.name}...", file=sys.stderr)
                    jd_text += "\n\n--- ATTACHMENT: " + path.name + " ---\n\n"
                    jd_text += extract_pdf_text(str(path))
                elif path.suffix.lower() in [".txt", ".md"]:
                    print(f"  Reading {path.name}...", file=sys.stderr)
                    jd_text += "\n\n--- ATTACHMENT: " + path.name + " ---\n\n"
                    jd_text += path.read_text()
    
    print(f"  Total content: {len(jd_text)} characters", file=sys.stderr)
    
    print("\n[2/5] Extracting JD details...", file=sys.stderr)
    jd_details = extract_jd_details(jd_text, args.email_subject)
    print(f"  Company: {jd_details['company']}", file=sys.stderr)
    print(f"  Role: {jd_details['role']}", file=sys.stderr)
    print(f"  Location: {jd_details.get('location', 'Not specified')}", file=sys.stderr)

    answered = jd_details.get("core_questions_answered", {})
    missing_questions = [q["id"] for q in CONFIG["core_questions"] if not answered.get(q["id"], False)]
    print(f"  Missing core questions: {missing_questions}", file=sys.stderr)
    
    print("\n[3/5] Generating Hiring POV...", file=sys.stderr)
    hiring_pov_content = generate_hiring_pov(jd_details, jd_text)

    company_slug = slugify(jd_details["company"])
    role_slug = slugify(jd_details["role"])
    pov_filename = f"{role_slug}_hiring-pov.md"
    jd_filename = f"{role_slug}_jd.txt"

    temp_dir = Path(tempfile.gettempdir())
    pov_path = temp_dir / pov_filename
    pov_path.write_text(hiring_pov_content)

    jd_path = temp_dir / jd_filename
    jd_path.write_text(jd_text[:200000])

    pov_pdf_path = generate_branded_pdf(
        pov_path,
        title=f"Hiring POV: {jd_details['role']} @ {jd_details['company']}"
    )

    print(f"  Saved POV to: {pov_path}", file=sys.stderr)
    if pov_pdf_path:
        print(f"  Saved POV PDF to: {pov_pdf_path}", file=sys.stderr)

    if args.dry_run:
        result = {
            "dry_run": True,
            "company": jd_details["company"],
            "role": jd_details["role"],
            "location": jd_details.get("location"),
            "hiring_pov_path": str(pov_path),
            "hiring_pov_pdf_path": str(pov_pdf_path) if pov_pdf_path else None,
            "jd_path": str(jd_path),
            "missing_core_questions": missing_questions,
            "jd_details": jd_details,
            "email_thread_id": args.email_thread_id,
        }
        print(json.dumps(result, indent=2))
        return

    print("\n[4/5] Preparing Airtable record...", file=sys.stderr)
    print("\n[5/5] Preparing Drive upload and email...", file=sys.stderr)

    # Airtable field mapping
    location_choice = map_location_choice(jd_details.get("location", ""))
    employment_type = map_employment_type(jd_details.get("employment_type") or jd_details.get("role") or "")

    email_content = generate_shivam_email(jd_details, "{{POV_PDF_LINK}}", missing_questions)

    employer_name = jd_details["company"]
    employer_name_lower = employer_name.lower().replace("'", "\\'")

    insights_defaults = {
        'technical_stack': 'Not specified.',
        'cultural_preferences': 'Not specified.',
        'implicit_signals': 'Not specified.',
        'employer_psychology': 'Not specified.',
        'anti_pattern_description': 'Not specified.',
        'location_notes': jd_details.get('location','Not specified'),
        'work_authorization_notes': 'Not specified in JD. Need employer policy on sponsorship / required authorization.',
        'ninety_day_success_criteria': 'Not specified in JD. Need clarity on first 90 days deliverables / success metrics.'
    }
    try: insights = extract_job_opening_insights(jd_text, hiring_pov_content, employer_name, jd_details["role"])
    except: insights = {}
    merged = {**insights_defaults, **(insights or {})}

    result = {
        "status": "ready_for_orchestration",
        "company": jd_details["company"],
        "company_slug": company_slug,
        "role": jd_details["role"],
        "role_slug": role_slug,
        "location": jd_details.get("location"),
        "missing_core_questions": missing_questions,
        "core_questions_answered": answered,
        "hiring_pov_path": str(pov_path),
        "hiring_pov_pdf_path": str(pov_pdf_path) if pov_pdf_path else None,
        "jd_path": str(jd_path),
        "email_thread_id": args.email_thread_id,
        "email_to_shivam": email_content,
        "orchestrator_instructions": {
            "step_0_find_employer": {
                "action": "find_employer",
                "tool": "airtable_oauth-list-records",
                "account": CONFIG["airtable"]["account"],
                "baseId": CONFIG["airtable"]["base_id"],
                "tableId": CONFIG["airtable"]["employers_table"],
                "filterByFormula": f"LOWER({{Employer Name}})='{employer_name_lower}'",
                "maxRecords": 1
            },
            "step_0b_create_employer_if_missing": {
                "action": "create_employer_if_missing",
                "tool": "airtable_oauth-create-single-record",
                "account": CONFIG["airtable"]["account"],
                "baseId": CONFIG["airtable"]["base_id"],
                "tableId": CONFIG["airtable"]["employers_table"],
                "fields": {
                    "Employer Name": employer_name
                },
                "note": "Only run if step_0_find_employer returns 0 records"
            },
            "step_1_create_job_opening": {
                "action": "create_job_opening",
                "tool": "airtable_oauth-create-single-record",
                "account": CONFIG["airtable"]["account"],
                "baseId": CONFIG["airtable"]["base_id"],
                "tableId": CONFIG["airtable"]["job_openings_table"],
                "fields": {
                    "Job Title": jd_details["role"],
                    "Employer": ["{{EMPLOYER_RECORD_ID}}"],
                    "Location": location_choice,
                    "Employment Type": employment_type,
                    "Status": "Open",
                    "Role Source": "Shivam",
                    "Intake Status": "New",
                    "Ball In Court": "Zo",
                    "Source Tag": "[JD]",
                    "Visa Sponsorship": "Unknown",
                    "Work Authorization Notes": merged['work_authorization_notes'],
                    "90-Day Success Criteria": merged['ninety_day_success_criteria'],
                    "Anti-Pattern Description": merged['anti_pattern_description'],
                    "Cultural Preferences": merged['cultural_preferences'],
                    "Technical Stack": merged['technical_stack'],
                    "Implicit Signals": merged['implicit_signals'],
                    "Employer Psychology": merged['employer_psychology'],
                    "Location Notes": merged['location_notes'],
                    "Job Description": jd_text[:90000],
                    "Intake Email Thread ID": args.email_thread_id or None,
                    "Salary Range (Checkbox)": bool(answered.get("salary_range")),
                    "Location/Geo (Checkbox)": bool(answered.get("location")),
                    "Visa/Sponsorship (Checkbox)": bool(answered.get("visa_sponsorship")),
                    "90-Day Success (Checkbox)": bool(answered.get("ninety_day_success")),
                    "Anti-Pattern (Checkbox)": bool(answered.get("anti_pattern")),
                },
                "note": "Set Employer to the record id from step_0_find_employer or step_0b_create_employer_if_missing"
            },
            "step_2a_find_employer_folder": {
                "action": "find_employer_folder",
                "tool": "google_drive-find-folder",
                "account": CONFIG["drive"]["account"],
                "nameSearchTerm": company_slug
            },
            "step_2b_create_employer_folder_if_missing": {
                "action": "create_employer_folder_if_missing",
                "tool": "google_drive-create-folder",
                "account": CONFIG["drive"]["account"],
                "parentId": CONFIG["drive"]["shared_folder_id"],
                "name": company_slug,
                "createIfUnique": True
            },
            "step_3_create_hiring_povs_subfolder": {
                "action": "create_hiring_povs_subfolder",
                "tool": "google_drive-create-folder",
                "account": CONFIG["drive"]["account"],
                "parentId": "{{EMPLOYER_FOLDER_ID}}",
                "name": "hiring-povs",
                "createIfUnique": True
            },
            "step_4_drive_upload_pov_md": {
                "action": "upload_hiring_pov_md",
                "tool": "google_drive-upload-file",
                "account": CONFIG["drive"]["account"],
                "parentId": "{{HIRING_POVS_FOLDER_ID}}",
                "filePath": str(pov_path),
                "name": pov_filename
            },
            "step_4b_drive_upload_pov_pdf": {
                "action": "upload_hiring_pov_pdf",
                "tool": "google_drive-upload-file",
                "account": CONFIG["drive"]["account"],
                "parentId": "{{HIRING_POVS_FOLDER_ID}}",
                "filePath": str(pov_pdf_path) if pov_pdf_path else None,
                "name": pov_filename.replace('.md', '.pdf'),
                "note": "Skip if filePath is null"
            },
            "step_4c_drive_upload_jd": {
                "action": "upload_cleaned_jd_text",
                "tool": "google_drive-upload-file",
                "account": CONFIG["drive"]["account"],
                "parentId": "{{HIRING_POVS_FOLDER_ID}}",
                "filePath": str(jd_path),
                "name": jd_filename
            },
            "step_5_email": {
                "action": "email_shivam",
                "tool": "gmail-send-email",
                "account": CONFIG["gmail"]["account"],
                "to": "shivam@corridorx.io",
                "cc": CONFIG["gmail"]["cc"],
                "subject": email_content["subject"],
                "body": email_content["body"],
                "bodyType": "plaintext",
                "note": "Replace {{POV_PDF_LINK}} with the uploaded PDF link"
            }
        }
    }

    result['insights'] = merged

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
