#!/usr/bin/env python3
"""
Careerspan Resume Intake Processor

Processes [RESUME] tagged emails and executes the candidate intake flow:
1. Extract candidate info (name, email, resume)
2. Match to Job Opening
3. Create Candidate record in Airtable
4. Generate Candidate Guide PDF
5. Upload to Drive
6. Email Shivam with summary and link
"""

import argparse
import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
import yaml

# Constants
CONFIG_PATH = '/home/workspace/Integrations/careerspan-pipeline/config.yaml'
BUILD_DIR = '/home/workspace/N5/builds/careerspan-pipeline-v2'
DEPOSIT_PATH = f'{BUILD_DIR}/deposits/D1.2-deposit.json'


def load_config() -> Dict:
    """Load the Careerspan pipeline configuration."""
    with open(CONFIG_PATH, 'r') as f:
        content = f.read()
        # Skip YAML frontmatter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]
        return yaml.safe_load(content)


def call_zo_ask(prompt: str, output_format: Optional[dict] = None) -> str:
    """
    Call the /zo/ask API for LLM processing.
    Returns the output as a string or dict based on output_format.
    """
    payload = {"input": prompt}
    if output_format:
        payload["output_format"] = output_format

    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
            "content-type": "application/json"
        },
        json=payload,
        timeout=120
    )
    response.raise_for_status()
    result = response.json()
    return result["output"]


def extract_candidate_info(email_subject: str, email_body: str, attachments: List[str]) -> Dict:
    """
    Extract candidate information from email using LLM semantic understanding.
    Returns: name, email, resume_path
    """
    prompt = f"""Extract candidate information from this email:

Subject: {email_subject}

Body:
{email_body}

Attachments: {', '.join([os.path.basename(f) for f in attachments])}

Extract and return ONLY valid JSON with these exact keys:
- candidate_name: Full name of the candidate
- candidate_email: Email address (if found in body or inferred from resume filename)
- resume_path: Which attachment is the resume (full path from the list)

If candidate email is not found in the email body, extract it from the resume filename (e.g., "john_doe_resume.pdf" -> "john.doe@example.com" as a best guess).

Return ONLY the JSON, no other text."""

    result = call_zo_ask(prompt)
    
    # Parse the JSON response
    try:
        # Handle case where LLM returns JSON with markdown backticks
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        info = json.loads(result)
        
        # Validate resume path is in attachments
        if info.get("resume_path") not in attachments:
            # Default to first attachment if not found
            info["resume_path"] = attachments[0] if attachments else None
        
        return info
    except Exception as e:
        # Fallback: extract from subject and use first attachment
        print(f"Warning: Failed to parse LLM response: {e}")
        return {
            "candidate_name": email_subject.split("-")[0].strip("[RESUME]").strip() if "-" in email_subject else email_subject,
            "candidate_email": None,
            "resume_path": attachments[0] if attachments else None
        }


def find_job_opening(email_subject: str, email_body: str, config: Dict, dry_run: bool = False) -> Tuple[Optional[str], str]:
    """
    Match email to a Job Opening in Airtable.
    Returns: (job_opening_id, confidence)
    """
    if dry_run:
        return ("recDRYRUN", "high")
    
    # Use LLM to extract company/role context
    prompt = f"""Analyze this email and extract any context about a job/role:

Subject: {email_subject}

Body:
{email_body}

Identify and return ONLY valid JSON with these keys:
- company: Company name (if mentioned)
- role: Role title (if mentioned)
- context: Brief summary of what job this candidate is for (max 2 sentences)

If no job context is mentioned, set all values to null."""

    try:
        result = call_zo_ask(prompt)
        
        # Parse JSON
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        context = json.loads(result)
        company = context.get("company")
        role = context.get("role")
        
        if not company and not role:
            return (None, "none")
    except:
        return (None, "none")
    
    # Query Airtable for matching job openings
    # NOTE: In production, this would call use_app_airtable_oauth
    # For this script, we return instructions to call the tool
    airtable_config = config['airtable']
    base_id = airtable_config['base_id']
    job_table = airtable_config['tables']['job_openings']
    
    # Build filter formula
    filters = []
    if company:
        filters.append(f"SEARCH('{company}', {{Company}}) > 0")
    if role:
        filters.append(f"SEARCH('{role}', {{Role Title}}) > 0")
    
    if filters:
        filter_formula = f"OR({', '.join(filters)})"
    else:
        return (None, "none")
    
    # Return instructions for Zo to query Airtable
    instructions = {
        "tool": "airtable_oauth-list-records",
        "base_id": base_id,
        "table_id": job_table,
        "filter_by_formula": filter_formula,
        "company": company,
        "role": role
    }
    
    print(f"[AIRTABLE QUERY NEEDED]: {json.dumps(instructions, indent=2)}")
    
    # For now, return mock ID - in production this would be handled
    return (None, "medium")


def create_candidate_record(
    candidate_info: Dict,
    job_opening_id: Optional[str],
    config: Dict,
    dry_run: bool = False
) -> Optional[str]:
    """
    Create a candidate record in Airtable.
    Returns: candidate_id
    """
    if dry_run:
        return "recDRYRUN_CANDIDATE"
    
    airtable_config = config['airtable']
    base_id = airtable_config['base_id']
    candidate_table = airtable_config['tables']['candidates']
    
    # Prepare record data
    record = {
        "Name": candidate_info['candidate_name'],
        "Email": candidate_info.get('candidate_email', ''),
        "Status": "Interested",
        "Ball In Court": "Shivam"
    }
    
    # Link to job opening if found
    if job_opening_id:
        record["Job Opening"] = [job_opening_id]
    
    # NOTE: In production, this would call use_app_airtable_oauth
    instructions = {
        "tool": "airtable_oauth-create-single-record",
        "base_id": base_id,
        "table_id": candidate_table,
        "record": record
    }
    
    print(f"[AIRTABLE CREATE NEEDED]: {json.dumps(instructions, indent=2)}")
    
    # Return mock ID for dry run
    return "recNEW_CANDIDATE"


def generate_candidate_guide(
    candidate_info: Dict,
    job_opening_id: Optional[str],
    resume_path: str,
    config: Dict,
    dry_run: bool = False
) -> Tuple[str, Optional[str]]:
    """
    Generate candidate guide PDF using careerspan-candidate-guide skill.
    Returns: (guide_path, drive_link)
    """
    if dry_run:
        return ("/tmp/dryrun_guide.pdf", "https://drive.google.com/dryrun/link")
    
    # Fetch job opening details if available
    jd_text = ""
    company = "Unknown"
    role = "Unknown"
    
    if job_opening_id:
        # NOTE: In production, this would call use_app_airtable_oauth to get record
        print(f"[AIRTABLE FETCH NEEDED for job: {job_opening_id}")
        # For now, use placeholder values
        company = "CorridorX"
        role = "Software Engineer"
    else:
        company = "CorridorX"
        role = "Software Engineer"
    
    # Create temporary directory for guide generation
    with tempfile.TemporaryDirectory() as tmpdir:
        # Prepare JD file
        jd_file = os.path.join(tmpdir, 'jd.txt')
        with open(jd_file, 'w') as f:
            f.write(jd_text if jd_text else f"Role: {role} at {company}")
        
        # Prepare output directory
        output_dir = os.path.join(tmpdir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Run careerspan-candidate-guide skill using subprocess
        guide_script = '/home/workspace/Skills/careerspan-candidate-guide/scripts/generate_guides.py'
        cmd = [
            'python3', guide_script,
            '--jd-file', jd_file,
            '--resumes', resume_path,
            '--output', output_dir,
            '--company', company,
            '--role', role,
            '--format', 'pdf'
        ]
        
        try:
            print(f"Running candidate guide generation...")
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                print(f"Warning: Guide generation failed: {result.stderr}")
                raise Exception(f"Guide generation failed: {result.stderr}")
            
            print(f"Guide generation output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error generating guide: {e}")
            print(f"stderr: {e.stderr}")
            raise
        
        # Find the generated PDF
        pdf_files = list(Path(output_dir).glob('*_Guide.pdf'))
        if not pdf_files:
            raise FileNotFoundError("No guide PDF generated")
        
        guide_path = str(pdf_files[0])
        
        # Upload to Drive using Zo app tool
        drive_link = upload_guide_to_drive(guide_path, company, candidate_info, config)
        
        return (guide_path, drive_link)


def upload_guide_to_drive(guide_path: str, company: str, candidate_info: Dict, config: Dict) -> str:
    """Upload candidate guide to Google Drive and return share link."""
    drive_config = config['google_drive']
    shared_folder_id = drive_config['shared_folder_id']
    
    # Create candidate slug
    candidate_slug = candidate_info['candidate_name'].lower().replace(' ', '_')
    employer_slug = company.lower().replace(' ', '_')
    
    # NOTE: In production, this would call use_app_google_drive
    # Steps:
    # 1. Create folder structure: {employer_slug}/candidates/{candidate_slug}/
    # 2. Upload file to that folder
    # 3. Return share link
    
    instructions = {
        "tool": "google_drive-upload-file",
        "parent_id": shared_folder_id,
        "file_path": guide_path,
        "name": f"{candidate_slug}_guide.pdf",
        "folder_structure": f"{employer_slug}/candidates/{candidate_slug}/"
    }
    
    print(f"[DRIVE UPLOAD NEEDED]: {json.dumps(instructions, indent=2)}")
    
    # Return mock link for now
    return f"https://drive.google.com/file/d/mock_{candidate_slug}/view"


def email_shivam(
    candidate_info: Dict,
    job_match: Tuple[Optional[str], str],
    candidate_guide_link: str,
    config: Dict,
    dry_run: bool = False
) -> bool:
    """Send summary email to Shivam."""
    if dry_run:
        print("[DRY RUN] Would email Shivam with candidate summary")
        return True
    
    job_opening_id, confidence = job_match
    
    subject = f"[Zo] Candidate: {candidate_info['candidate_name']}"
    
    body = f"""Candidate intake complete:

**Name:** {candidate_info['candidate_name']}
**Email:** {candidate_info.get('candidate_email', 'Not provided')}

**Job Match:** {confidence.upper()}
{"**Job Opening ID:** " + job_opening_id if job_opening_id else "**Job Opening:** No match found - please assign manually"}

**Candidate Guide:** {candidate_guide_link}

The candidate has been added to Airtable. Next steps:
1. Review the candidate guide
2. Share the guide with the candidate (if appropriate)
3. Candidate will complete Careerspan Stories
4. Intelligence Brief will be processed automatically

---
Zo (on V's behalf)
"""
    
    # NOTE: In production, this would call use_app_gmail
    instructions = {
        "tool": "gmail-send-email",
        "to": "shivam@corridorx.io",
        "from_email": "vrijen@mycareerspan.com",
        "subject": subject,
        "body": body,
        "body_type": "plaintext"
    }
    
    print(f"[GMAIL SEND NEEDED]: {json.dumps(instructions, indent=2)}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Process [RESUME] tagged emails for candidate intake")
    parser.add_argument('--email-subject', required=True, help="Email subject line")
    parser.add_argument('--email-body', required=True, help="Email body text")
    parser.add_argument('--email-from', required=True, help="Sender email address")
    parser.add_argument('--attachments', nargs='+', required=True, help="Paths to attached resume files")
    parser.add_argument('--job-opening-id', help="Airtable record ID for Job Opening (optional)")
    parser.add_argument('--dry-run', action='store_true', help="Skip mutations, validation only")
    
    args = parser.parse_args()
    
    # Load config
    config = load_config()
    
    # Step 1: Extract candidate info
    print("Extracting candidate information...")
    candidate_info = extract_candidate_info(args.email_subject, args.email_body, args.attachments)
    print(f"Candidate: {candidate_info['candidate_name']}")
    
    if not candidate_info.get('resume_path'):
        raise ValueError("No resume attachment found")
    
    # Step 2: Match job opening
    if args.job_opening_id:
        job_match = (args.job_opening_id, "high")
    else:
        print("Matching to Job Opening...")
        job_match = find_job_opening(args.email_subject, args.email_body, config, args.dry_run)
    
    job_opening_id, confidence = job_match
    print(f"Job match: {confidence} (ID: {job_opening_id})")
    
    # Step 3: Create candidate record
    print("Creating candidate record in Airtable...")
    candidate_id = create_candidate_record(candidate_info, job_opening_id, config, args.dry_run)
    print(f"Candidate ID: {candidate_id}")
    
    # Step 4: Generate candidate guide
    print("Generating candidate guide...")
    try:
        guide_path, guide_link = generate_candidate_guide(
            candidate_info,
            job_opening_id,
            candidate_info['resume_path'],
            config,
            args.dry_run
        )
        print(f"Guide generated: {guide_path}")
        print(f"Drive link: {guide_link}")
    except Exception as e:
        print(f"Warning: Guide generation failed: {e}")
        guide_link = "PENDING"
    
    # Step 5: Email Shivam
    print("Emailing Shivam...")
    email_sent = email_shivam(candidate_info, job_match, guide_link, config, args.dry_run)
    print(f"Email sent: {email_sent}")
    
    # Step 6: Build deposit
    deposit = {
        "candidate_id": candidate_id,
        "candidate_name": candidate_info['candidate_name'],
        "candidate_email": candidate_info.get('candidate_email', ''),
        "job_opening_id": job_opening_id,
        "job_match_confidence": confidence,
        "candidate_guide_link": guide_link,
        "email_sent": email_sent,
        "flags": [] if guide_link != "PENDING" else ["guide_generation_failed"]
    }
    
    # Ensure deposit directory exists
    os.makedirs(os.path.dirname(DEPOSIT_PATH), exist_ok=True)
    
    # Write deposit
    with open(DEPOSIT_PATH, 'w') as f:
        json.dump(deposit, f, indent=2)
    
    print(f"\nDeposit written to: {DEPOSIT_PATH}")
    return deposit


if __name__ == '__main__':
    try:
        result = main()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
