#!/usr/bin/env python3
"""Career Coaching Hotline — Resume Ingestion Pipeline.

Lightweight, hotline-specific resume preprocessing:
  1. Accept a resume file (PDF or DOCX) — from local path or download URL
  2. Extract raw text
  3. Run a focused LLM decomposition via Zo API (NOT the Careerspan decomposer)
  4. Store processed data in the caller_resumes DuckDB table

Usage:
  # Ingest from a local file
  python3 resume_ingest.py --file /path/to/resume.pdf --phone "+12125551234"

  # Ingest from a URL (e.g. Fillout file upload)
  python3 resume_ingest.py --url "https://..." --phone "+12125551234"

  # Dry run (extract + decompose but don't store)
  python3 resume_ingest.py --file /path/to/resume.pdf --phone "+12125551234" --dry-run

  # Ingest from Fillout webhook payload (stdin)
  echo '{"questions": [...]}' | python3 resume_ingest.py --fillout-payload --phone-field "phone_number_field_id"
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    import duckdb
except ImportError:
    print("Error: duckdb library required. Install with: pip install duckdb", file=sys.stderr)
    sys.exit(1)


# ── Configuration ──

DB_PATH = os.environ.get(
    "CAREER_HOTLINE_DB",
    "/home/workspace/Datasets/career-hotline-calls/data.duckdb"
)
RESUME_STORAGE = os.environ.get(
    "CAREER_HOTLINE_RESUME_STORAGE",
    "/home/workspace/Datasets/career-hotline-calls/resumes"
)
ZO_TOKEN = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
ZO_ASK_URL = "https://api.zo.computer/zo/ask"

# Supported file types
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_FILE_SIZE_MB = 10


# ── Text Extraction ──

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pdftotext (poppler)."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", file_path, "-"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback: try without -layout flag
    try:
        result = subprocess.run(
            ["pdftotext", file_path, "-"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"Warning: DOCX extraction failed: {e}", file=sys.stderr)
        return ""


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from plain text file."""
    try:
        return Path(file_path).read_text(encoding="utf-8").strip()
    except Exception:
        try:
            return Path(file_path).read_text(encoding="latin-1").strip()
        except Exception:
            return ""


def extract_text(file_path: str) -> str:
    """Extract text from a resume file based on extension."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        print(f"Unsupported file type: {ext}", file=sys.stderr)
        return ""


# ── File Download ──

def download_file(url: str, dest_dir: str) -> Tuple[Optional[str], Optional[str]]:
    """Download a file from URL to dest_dir. Returns (local_path, original_filename)."""
    try:
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()

        # Try to get filename from Content-Disposition header
        content_disp = resp.headers.get("Content-Disposition", "")
        filename = None
        if "filename=" in content_disp:
            parts = content_disp.split("filename=")
            if len(parts) > 1:
                filename = parts[1].strip().strip('"').strip("'")

        # Fallback: extract from URL
        if not filename:
            from urllib.parse import urlparse, unquote
            parsed = urlparse(url)
            filename = unquote(parsed.path.split("/")[-1]) or "resume_download"

        # Sanitize filename
        filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        if not filename:
            filename = "resume_download"

        # Check extension
        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            # Try to infer from content type
            content_type = resp.headers.get("Content-Type", "")
            if "pdf" in content_type:
                filename = filename + ".pdf"
            elif "docx" in content_type or "openxmlformats" in content_type:
                filename = filename + ".docx"
            elif "msword" in content_type:
                filename = filename + ".doc"

        dest_path = os.path.join(dest_dir, filename)

        # Check file size
        content_length = resp.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_FILE_SIZE_MB * 1024 * 1024:
            print(f"File too large: {int(content_length) / 1024 / 1024:.1f}MB (max {MAX_FILE_SIZE_MB}MB)", file=sys.stderr)
            return None, None

        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return dest_path, filename

    except Exception as e:
        print(f"Download failed: {e}", file=sys.stderr)
        return None, None


# ── LLM Decomposition ──

def zo_ask(prompt: str) -> Optional[Any]:
    """Call Zo API for LLM processing. Never sends output_format — prompt
    instructs the LLM to return JSON directly, which we parse ourselves."""
    token = ZO_TOKEN
    if not token:
        print("Warning: ZO_CLIENT_IDENTITY_TOKEN not set, skipping LLM decomposition", file=sys.stderr)
        return None

    auth = token if token.startswith("Bearer") else f"Bearer {token}"
    body: Dict[str, Any] = {"input": prompt}

    try:
        resp = requests.post(
            ZO_ASK_URL,
            headers={"authorization": auth, "content-type": "application/json"},
            json=body,
            timeout=120
        )
        if resp.status_code != 200:
            print(f"Zo API returned {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
            return None
        result = resp.json()
        output = result.get("output")
        if isinstance(output, dict):
            return output
        if isinstance(output, str):
            return _parse_json_from_text(output)
        return output
    except Exception as e:
        print(f"Zo API call failed: {e}", file=sys.stderr)
        return None


def _parse_json_from_text(text: str) -> Optional[Any]:
    """Extract JSON from LLM text output, handling markdown code blocks."""
    text = text.strip()
    if not text:
        return None

    # Strip markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        start = 1
        end = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "```":
                end = i
                break
        text = "\n".join(lines[start:end])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start >= 0 and brace_end > brace_start:
            try:
                return json.loads(text[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass
        print(f"Could not parse LLM output as JSON ({len(text)} chars)", file=sys.stderr)
        return None


def decompose_resume(raw_text: str) -> Optional[Dict[str, Any]]:
    """Run lightweight LLM decomposition on resume text.

    This is NOT the Careerspan decomposer. It's a focused extraction
    for the hotline's coaching tools (AISS bullet analysis, section scoring,
    search diagnostic, etc).
    """
    if not raw_text or len(raw_text) < 50:
        return None

    # Truncate very long resumes to stay within context limits
    text_for_analysis = raw_text[:8000]

    raw_output = zo_ask(
        f"""You are a resume data extractor for a career coaching hotline. Extract structured data from this resume text.

This data will be used by an AI career coach (Zozie) to give personalized, specific coaching feedback over the phone.

Evaluation frameworks to apply:
- AISS bullet analysis (Action, Impact, Scale, Skill — each scored 1-5)
  - Action: Strong past-tense verb (not "responsible for" — YES "led," "designed," "reduced")
  - Impact: Quantified result (revenue, costs, time saved, users served)
  - Scale: Scope context (team size, budget, user base, geographic reach)
  - Skill: Demonstrated capability that maps to target role requirements
- ATS compatibility: Standard headers, simple formatting, standard date formats
- The "So What?" test: Can you articulate why each bullet matters to a hiring manager?

Resume text:
---
{text_for_analysis}
---

Return a single JSON object with these fields:
- "name": string (candidate's full name)
- "current_title": string (most recent job title)
- "current_company": string (most recent employer)
- "years_experience": number (approximate total years)
- "education": array of {{"degree": str, "institution": str, "year": str}}
- "experience": array of {{"title": str, "company": str, "duration": str, "bullets": [str]}}
- "skills": array of strings
- "summary_text": string (resume summary if present, else "")
- "aiss_quick_scan": {{
    "strongest_bullets": [top 3 strongest bullets with good AISS],
    "weakest_bullets": [top 3 weakest bullets with poor AISS],
    "overall_bullet_quality": "weak"|"mixed"|"solid"|"strong",
    "common_weakness": string describing most common issue
  }}
- "rubric_evaluation": {{
    "ats_compatibility": 1-5 (ATS-friendly formatting),
    "summary_quality": 1-5 (professional summary quality),
    "experience_quality": 1-5 (AISS compliance, progression),
    "skills_presentation": 1-5 (hard/soft balance, specificity),
    "overall_signal_strength": 1-5 (how clearly value is communicated),
    "tailoring_readiness": 1-5 (how easily tailored to specific roles)
  }}
- "ats_risks": [specific ATS formatting risks found]
- "so_what_failures": [bullets that fail the "so what?" test — duties without impact]
- "coaching_hooks": [3-5 specific coaching conversation starters referencing actual resume content]
- "estimated_career_stage": "groundwork"|"materials"|"outreach"|"performance"|"transition"

Return ONLY the JSON object, no markdown formatting or explanation."""
    )

    if not raw_output:
        return None

    # zo_ask now handles JSON parsing internally — returns dict or None
    if isinstance(raw_output, dict):
        return raw_output

    print(f"Unexpected decomposition output type: {type(raw_output)}", file=sys.stderr)
    return None


# ── Database Storage ──

def store_resume(
    phone: str,
    file_path: str,
    processed_data: Optional[Dict[str, Any]],
    dry_run: bool = False
) -> bool:
    """Store resume data in caller_resumes DuckDB table."""
    if dry_run:
        print("\n[DRY RUN] Would store:")
        print(f"  Phone: {phone}")
        print(f"  File: {file_path}")
        print(f"  Processed: {'Yes' if processed_data else 'No'}")
        if processed_data:
            print(f"  Name: {processed_data.get('name', 'unknown')}")
            print(f"  Stage: {processed_data.get('estimated_career_stage', 'unknown')}")
            print(f"  Bullets quality: {processed_data.get('aiss_quick_scan', {}).get('overall_bullet_quality', 'unknown')}")
        return True

    try:
        con = duckdb.connect(DB_PATH)

        # Ensure table exists
        con.execute("""
            CREATE TABLE IF NOT EXISTS caller_resumes (
                id VARCHAR PRIMARY KEY,
                phone_number VARCHAR,
                file_path VARCHAR,
                processed_data JSON,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
        """)

        resume_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        processed_json = json.dumps(processed_data) if processed_data else None
        processed_at = now if processed_data else None

        con.execute("""
            INSERT INTO caller_resumes (id, phone_number, file_path, processed_data, submitted_at, processed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [resume_id, phone, file_path, processed_json, now, processed_at])

        con.close()
        print(f"Stored resume: {resume_id[:8]} for {phone[-4:]}")
        return True
    except Exception as e:
        print(f"Database storage failed: {e}", file=sys.stderr)
        return False


# ── Phone Normalization ──

def normalize_phone(raw: str) -> str:
    """Normalize phone number to E.164 format."""
    if not raw:
        return ""

    # Strip non-numeric except leading +
    cleaned = raw.strip()
    if cleaned.startswith("+"):
        digits = "+" + "".join(c for c in cleaned[1:] if c.isdigit())
    else:
        digits = "".join(c for c in cleaned if c.isdigit())

    # If 10 digits, assume US
    if len(digits) == 10:
        digits = "+1" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        digits = "+" + digits
    elif not digits.startswith("+"):
        digits = "+" + digits

    return digits


# ── Fillout Payload Parsing ──

def parse_fillout_payload(
    payload: Dict[str, Any],
    phone_field_id: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """Parse a Fillout webhook payload to extract phone number and file upload URL.

    Fillout webhook payloads have a 'questions' array where each question has:
    - id: question field ID
    - name: question label
    - type: question type (e.g. 'FileUpload', 'PhoneNumber', 'ShortAnswer')
    - value: the answer value

    For FileUpload, value is typically a list of objects with:
    - url: download URL for the file
    - name: original filename
    - type/mimeType: MIME type

    Returns: (phone_number, file_url)
    """
    questions = payload.get("questions", [])
    phone = None
    file_url = None

    for q in questions:
        q_type = (q.get("type") or "").lower()
        q_id = q.get("id", "")
        q_name = (q.get("name") or "").lower()
        value = q.get("value")

        # Detect phone number
        if phone_field_id and q_id == phone_field_id:
            phone = str(value) if value else None
        elif not phone and q_type in ("phonenumber", "phone"):
            phone = str(value) if value else None
        elif not phone and any(kw in q_name for kw in ("phone", "mobile", "cell", "number")):
            if value and isinstance(value, str) and any(c.isdigit() for c in value):
                phone = value

        # Detect file upload
        if q_type in ("fileupload", "file_upload", "file"):
            if isinstance(value, list) and value:
                # Take the first file (typically the resume)
                first_file = value[0]
                if isinstance(first_file, dict):
                    file_url = first_file.get("url") or first_file.get("fileUrl")
                elif isinstance(first_file, str):
                    file_url = first_file
            elif isinstance(value, str) and value.startswith("http"):
                file_url = value

    return phone, file_url


# ── Main Pipeline ──

def ingest_resume(
    file_path: Optional[str] = None,
    file_url: Optional[str] = None,
    phone: str = "",
    dry_run: bool = False,
    verbose: bool = False
) -> Dict[str, Any]:
    """Run the full resume ingestion pipeline.

    Returns a result dict with status, details, and any errors.
    """
    result: Dict[str, Any] = {
        "status": "error",
        "phone": phone,
        "file_path": None,
        "processed": False,
        "decomposition": None
    }

    phone = normalize_phone(phone)
    if not phone:
        result["error"] = "No phone number provided"
        return result

    result["phone"] = phone

    # Step 1: Get the file
    local_path = file_path
    original_filename = Path(file_path).name if file_path else None

    if file_url and not file_path:
        if verbose:
            print(f"Downloading from: {file_url[:80]}...")
        local_path, original_filename = download_file(file_url, RESUME_STORAGE)
        if not local_path:
            result["error"] = "Failed to download file"
            return result
    elif file_path:
        if not os.path.exists(file_path):
            result["error"] = f"File not found: {file_path}"
            return result

        # Copy to resume storage
        ext = Path(file_path).suffix
        safe_phone = phone.replace("+", "").replace(" ", "")
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dest_filename = f"{safe_phone}_{ts}{ext}"
        dest_path = os.path.join(RESUME_STORAGE, dest_filename)

        if not dry_run:
            os.makedirs(RESUME_STORAGE, exist_ok=True)
            shutil.copy2(file_path, dest_path)
            local_path = dest_path
            if verbose:
                print(f"Copied to: {dest_path}")
        else:
            local_path = file_path

    if not local_path:
        result["error"] = "No file provided (use --file or --url)"
        return result

    result["file_path"] = local_path

    # Step 2: Extract text
    if verbose:
        print(f"Extracting text from: {local_path}")
    raw_text = extract_text(local_path)

    if not raw_text or len(raw_text) < 50:
        result["error"] = f"Could not extract meaningful text from file ({len(raw_text)} chars)"
        result["status"] = "partial"
        # Still store the file reference even without text
        if not dry_run:
            store_resume(phone, local_path, None, dry_run=False)
        return result

    if verbose:
        print(f"Extracted {len(raw_text)} characters")

    # Step 3: LLM decomposition
    if verbose:
        print("Running LLM decomposition...")
    decomposition = decompose_resume(raw_text)

    if decomposition:
        result["processed"] = True
        result["decomposition"] = decomposition
        if verbose:
            print(f"Decomposition complete: {decomposition.get('name', 'unknown')}")
            print(f"  Career stage: {decomposition.get('estimated_career_stage', 'unknown')}")
            print(f"  Bullet quality: {decomposition.get('aiss_quick_scan', {}).get('overall_bullet_quality', 'unknown')}")
            hooks = decomposition.get("coaching_hooks", [])
            if hooks:
                print(f"  Coaching hooks: {len(hooks)}")
                for h in hooks[:3]:
                    print(f"    - {h[:100]}")
    else:
        if verbose:
            print("LLM decomposition failed or unavailable — storing raw file reference")

    # Step 4: Store
    if verbose:
        print("Storing to database...")
    stored = store_resume(phone, local_path, decomposition, dry_run=dry_run)

    if stored:
        result["status"] = "ok"
    else:
        result["status"] = "partial"
        result["error"] = "Database storage failed"

    return result


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(
        description="Career Coaching Hotline — Resume Ingestion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest from local file
  python3 resume_ingest.py --file resume.pdf --phone "+12125551234"

  # Ingest from URL
  python3 resume_ingest.py --url "https://example.com/resume.pdf" --phone "+12125551234"

  # Dry run
  python3 resume_ingest.py --file resume.pdf --phone "+12125551234" --dry-run

  # From Fillout webhook payload via stdin
  echo '{"questions":[...]}' | python3 resume_ingest.py --fillout-payload
        """
    )

    parser.add_argument("--file", "-f", help="Local file path to resume")
    parser.add_argument("--url", "-u", help="URL to download resume from")
    parser.add_argument("--phone", "-p", help="Caller's phone number (E.164 or raw)")
    parser.add_argument("--fillout-payload", action="store_true",
                        help="Read Fillout webhook JSON from stdin")
    parser.add_argument("--phone-field", help="Fillout question ID for phone number field")
    parser.add_argument("--dry-run", action="store_true", help="Extract and decompose without storing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    # Handle Fillout payload mode
    if args.fillout_payload:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON on stdin: {e}", file=sys.stderr)
            sys.exit(1)

        phone, file_url = parse_fillout_payload(payload, args.phone_field)

        if not phone and args.phone:
            phone = args.phone

        if not phone:
            print("Error: Could not extract phone number from Fillout payload. Use --phone or --phone-field.", file=sys.stderr)
            sys.exit(1)

        if not file_url:
            print("Error: No file upload found in Fillout payload.", file=sys.stderr)
            sys.exit(1)

        result = ingest_resume(
            file_url=file_url,
            phone=phone,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
    else:
        if not args.phone:
            print("Error: --phone is required", file=sys.stderr)
            sys.exit(1)

        if not args.file and not args.url:
            print("Error: provide --file or --url", file=sys.stderr)
            sys.exit(1)

        result = ingest_resume(
            file_path=args.file,
            file_url=args.url,
            phone=args.phone,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["status"] == "ok":
            print(f"\nResume ingested successfully for {result['phone']}")
            if result.get("decomposition"):
                d = result["decomposition"]
                print(f"  Name: {d.get('name', 'unknown')}")
                print(f"  Stage: {d.get('estimated_career_stage', 'unknown')}")
                quality = d.get("aiss_quick_scan", {}).get("overall_bullet_quality", "unknown")
                print(f"  Bullet quality: {quality}")
        elif result["status"] == "partial":
            print(f"\nPartially ingested: {result.get('error', 'unknown issue')}")
        else:
            print(f"\nFailed: {result.get('error', 'unknown error')}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
