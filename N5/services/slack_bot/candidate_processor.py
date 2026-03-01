#!/usr/bin/env python3
"""
Candidate Processor — LLM-powered extraction from Slack messages → Airtable.

Handles two known Divyansh formats:
1. Plain text: Company / Name / LinkedIn / Location / Comp lines + PDF attachment
2. Slack table: structured table block with columns (Date, Source, Name, etc.) + PDF attachments

Uses /zo/ask for semantic extraction so new formats work without code changes.
"""
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

logger = logging.getLogger(__name__)

# Airtable constants
AIRTABLE_BASE_ID = "appd12asvg42woz9I"
AIRTABLE_JOB_OPENINGS_TABLE = "tblHgSEOsoegYnJl7"
AIRTABLE_EMPLOYERS_TABLE = "tblvIfVUHxzuBQ2WB"
AIRTABLE_CANDIDATES_TABLE = "tblWB2mGbioA8pLBL"
AIRTABLE_CANDIDACIES_TABLE = "tblYCpNiRzoH9IYzY"
AIRTABLE_ACTIVITY_LOG_TABLE = "tblGpSaOO5mEBXMU8"

AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN", "")

EVENTS_LOG_PATH = Path("/home/workspace/N5/logs/cspan_slack_events.jsonl")

LPA_TO_USD_RATE = 90  # 1 USD = 90 INR; 1 LPA = 100000 INR

GEO_MAP = {
    "bangalore": "Bangalore",
    "bengaluru": "Bangalore",
    "hyderabad": "Hyderabad",
    "new york": "NY",
    "nyc": "NY",
    "san francisco": "SF",
    "sf": "SF",
    "remote": "Remote",
}

LOCATION_CHOICES = {"NY", "SF", "Bangalore", "Hyderabad", "Remote"}


def log_event(event_type: str, data: Dict[str, Any]):
    """Append event to JSONL log."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **data,
    }
    EVENTS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def extract_table_from_attachments(attachments: List[Dict]) -> Optional[List[Dict[str, str]]]:
    """Extract structured rows from Slack table attachments."""
    for att in attachments:
        for block in att.get("blocks", []):
            if block.get("type") != "table":
                continue
            rows = block.get("rows", [])
            if len(rows) < 2:
                continue
            # First row is headers
            headers = []
            for cell in rows[0]:
                text = _extract_cell_text(cell)
                headers.append(text.strip())

            data_rows = []
            for row in rows[1:]:
                row_dict = {}
                for i, cell in enumerate(row):
                    key = headers[i] if i < len(headers) else f"col_{i}"
                    row_dict[key] = _extract_cell_text(cell).strip()
                data_rows.append(row_dict)
            return data_rows
    return None


def _extract_cell_text(cell: Dict) -> str:
    """Pull plain text from a Slack block cell."""
    if cell.get("type") == "raw_text":
        return cell.get("text", "")
    # rich_text blocks
    parts = []
    for el in cell.get("elements", []):
        for section in el.get("elements", []):
            parts.append(section.get("text", ""))
    return " ".join(parts)


def parse_lpa_to_usd(comp_str: str) -> Optional[int]:
    """Convert an LPA string like '60 LPA' or '26 Lpa - Fixed + 23 lpa as variable' to annual USD."""
    if not comp_str:
        return None
    comp_lower = comp_str.lower().replace(",", "")
    # Find all numeric values (could be "26 Lpa - Fixed + 23 lpa as variable")
    numbers = re.findall(r"([\d.]+)\s*(?:lpa|lakh|lac|l)", comp_lower)
    if numbers:
        total_lpa = sum(float(n) for n in numbers)
        inr = total_lpa * 100_000
        return int(inr / LPA_TO_USD_RATE)
    # Try plain number (might already be in LPA context)
    numbers = re.findall(r"([\d.]+)", comp_lower)
    if numbers and ("lpa" in comp_lower or "lakh" in comp_lower or "lac" in comp_lower):
        total_lpa = sum(float(n) for n in numbers)
        inr = total_lpa * 100_000
        return int(inr / LPA_TO_USD_RATE)
    # If just a number with no currency hint, try LPA if >= 10 and <= 500 (typical LPA range)
    if numbers:
        val = float(numbers[0])
        if 5 <= val <= 500:
            inr = val * 100_000
            return int(inr / LPA_TO_USD_RATE)
    return None


def map_geo(location_str: str) -> List[str]:
    """Map a location string to allowed Airtable geography values."""
    if not location_str:
        return []
    loc_lower = location_str.lower().strip()
    for key, val in GEO_MAP.items():
        if key in loc_lower:
            return [val]
    # Do not guess geographies when ambiguous.
    return []


def _normalize_header_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def _get_row_value(row: Dict[str, str], aliases: List[str]) -> str:
    alias_norm = {_normalize_header_key(a) for a in aliases}
    for key, value in row.items():
        if _normalize_header_key(key) in alias_norm:
            return value
    return ""


def parse_allowed_geographies(raw_value: str) -> List[str]:
    """Parse explicit allowed/permitted geographies from free text."""
    if not raw_value:
        return []
    text = _normalize_header_key(raw_value)
    geos: List[str] = []
    checks = [
        ("new york", "NY"),
        (" ny ", "NY"),
        ("san francisco", "SF"),
        (" sf ", "SF"),
        ("bangalore", "Bangalore"),
        ("bengaluru", "Bangalore"),
        ("hyderabad", "Hyderabad"),
        ("remote", "Remote"),
    ]
    padded = f" {text} "
    for key, val in checks:
        if key in padded and val not in geos:
            geos.append(val)
    return geos


async def airtable_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
    """Make authenticated Airtable API request."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, headers=headers, json=data) as resp:
            result = await resp.json()
            if resp.status >= 400:
                logger.error(f"Airtable error {resp.status}: {result}")
            return result


async def find_employer_by_name(name: str) -> Optional[Dict]:
    """Search for an employer by name."""
    safe_name = name.replace("'", "")
    formula = f"SEARCH(LOWER('{safe_name}'), LOWER({{Employer Name}}))"
    encoded = aiohttp.helpers.quote(formula)
    endpoint = f"{AIRTABLE_EMPLOYERS_TABLE}?filterByFormula={encoded}&maxRecords=3"
    result = await airtable_request("GET", endpoint)
    records = result.get("records", [])
    if records:
        return records[0]
    return None


async def find_job_openings_for_employer(employer_record_id: str) -> List[Dict]:
    """Get open job openings linked to an employer."""
    filter_formula = "{Status} = 'Open'"
    encoded_formula = aiohttp.helpers.quote(filter_formula)
    endpoint = f"{AIRTABLE_JOB_OPENINGS_TABLE}?filterByFormula={encoded_formula}&maxRecords=50"
    result = await airtable_request("GET", endpoint)
    records = result.get("records", [])
    # Filter to ones linked to this employer
    matching = []
    for r in records:
        company_links = r.get("fields", {}).get("Company Name", [])
        if employer_record_id in company_links:
            matching.append(r)
    return matching


async def find_candidate_by_name(name: str) -> Optional[Dict]:
    """Check if candidate already exists."""
    safe_name = name.replace("'", "")
    formula = f"LOWER({{Full Name}}) = LOWER('{safe_name}')"
    encoded = aiohttp.helpers.quote(formula)
    endpoint = f"{AIRTABLE_CANDIDATES_TABLE}?filterByFormula={encoded}&maxRecords=1"
    result = await airtable_request("GET", endpoint)
    records = result.get("records", [])
    if records:
        return records[0]
    return None


async def create_candidate(fields: Dict) -> Dict:
    """Create a new candidate record."""
    endpoint = AIRTABLE_CANDIDATES_TABLE
    data = {"fields": fields, "typecast": True}
    return await airtable_request("POST", endpoint, data)


async def create_candidacy(candidate_id: str, job_opening_id: str, candidate_name: str, job_title: str) -> Dict:
    """Create a candidacy linking candidate to job opening."""
    endpoint = AIRTABLE_CANDIDACIES_TABLE
    fields = {
        "Candidacy Name": f"{candidate_name} → {job_title}",
        "Candidate": [candidate_id],
        "Job Opening": [job_opening_id],
        "Status": "Pipeline Accepted",
        "Acceptance Date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    return await airtable_request("POST", endpoint, {"fields": fields, "typecast": True})


async def log_activity(action_type: str, details: str, job_id: Optional[str] = None, candidate_id: Optional[str] = None, status: str = "Success") -> Dict:
    """Log to Activity Log table."""
    endpoint = AIRTABLE_ACTIVITY_LOG_TABLE
    fields = {
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "Action Type": action_type,
        "Details": details,
        "Triggered By": "Webhook",
        "Status": status,
    }
    if job_id:
        fields["Job Opening"] = [job_id]
    if candidate_id:
        fields["Candidate"] = [candidate_id]
    return await airtable_request("POST", endpoint, {"fields": fields, "typecast": True})


async def update_candidate_considered_for(candidate_id: str, employer_id: str) -> bool:
    """Add an employer to a candidate's 'Considered For' field if not already present."""
    endpoint = f"{AIRTABLE_CANDIDATES_TABLE}/{candidate_id}"
    result = await airtable_request("GET", endpoint)
    existing = result.get("fields", {}).get("Considered For", [])
    if employer_id in existing:
        return False
    existing.append(employer_id)
    await airtable_request("PATCH", endpoint, {"fields": {"Considered For": existing}})
    return True


async def update_candidate_interviewing_for(candidate_id: str, job_opening_ids: List[str]) -> Tuple[bool, List[str]]:
    """Merge job opening IDs into candidate's 'Interviewing For' field."""
    if not job_opening_ids:
        return False, []
    endpoint = f"{AIRTABLE_CANDIDATES_TABLE}/{candidate_id}"
    result = await airtable_request("GET", endpoint)
    existing = result.get("fields", {}).get("Interviewing For", [])
    before = set(existing)
    merged = list(before.union(set(job_opening_ids)))
    if set(merged) == before:
        return False, merged
    await airtable_request("PATCH", endpoint, {"fields": {"Interviewing For": merged}})
    return True, merged


def _normalize_role_text(s: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]+", " ", (s or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _tokenize_role(s: str) -> List[str]:
    stop = {"role", "position", "opening", "hiring", "for", "the", "at", "to", "and"}
    return [t for t in _normalize_role_text(s).split() if t and t not in stop]


def extract_role_hints(text: str) -> List[str]:
    """Heuristic role extraction from message text."""
    if not text:
        return []
    hints: List[str] = []
    patterns = [
        r"(?:^|\n)\s*role\s*[:\-]\s*([^\n,]+)",
        r"(?:^|\n)\s*position\s*[:\-]\s*([^\n,]+)",
        r"(?:^|\n)\s*for\s+[^\n,]*?\b((?:staff|senior|principal|lead|founding)?\s*[a-z][a-z\s/-]{3,60}?)\s+(?:role|position)\b",
    ]
    for pattern in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            role = m.group(1).strip().rstrip(".")
            if role and len(role) >= 4:
                hints.append(role)
    # de-dup preserve order
    seen = set()
    ordered = []
    for h in hints:
        k = h.lower()
        if k not in seen:
            seen.add(k)
            ordered.append(h)
    return ordered


def select_job_openings_by_role(job_openings: List[Dict], role_hints: List[str]) -> List[Dict]:
    """Match role hints to specific job openings for an employer."""
    if not job_openings:
        return []
    if not role_hints:
        return job_openings[:1] if len(job_openings) == 1 else []

    scored: List[Tuple[int, Dict]] = []
    for rec in job_openings:
        title = rec.get("fields", {}).get("Job Title", "")
        title_norm = _normalize_role_text(title)
        title_tokens = set(_tokenize_role(title))
        best = 0
        for hint in role_hints:
            hint_norm = _normalize_role_text(hint)
            hint_tokens = set(_tokenize_role(hint))
            overlap = len(title_tokens.intersection(hint_tokens))
            contains = 2 if (hint_norm in title_norm or title_norm in hint_norm) and hint_norm else 0
            score = overlap + contains
            best = max(best, score)
        if best > 0:
            scored.append((best, rec))

    if not scored:
        return job_openings[:1] if len(job_openings) == 1 else []
    top = max(s for s, _ in scored)
    return [r for s, r in scored if s == top]


def build_candidate_fields(
    name: str,
    linkedin: Optional[str],
    email: Optional[str],
    location: Optional[str],
    current_comp: Optional[str],
    expected_comp: Optional[str],
    notice_period: Optional[str],
    resume_url: Optional[str],
    job_opening_ids: List[str],
    considered_for_ids: Optional[List[str]] = None,
    explicit_allowed_geographies: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build Airtable candidate fields dict."""
    clean_location = _clean_location_field(location or "")
    fields: Dict[str, Any] = {
        "Full Name": name.strip().title(),
        "Current Status": "Applied",
        "Source Tag": "[RESUME]",
    }
    if linkedin:
        fields["LinkedIn"] = linkedin.strip()
    if email:
        fields["Email Address"] = email.strip()
    if resume_url:
        fields["Resume Link"] = resume_url
    if job_opening_ids:
        fields["Interviewing For"] = job_opening_ids
    if considered_for_ids:
        fields["Considered For"] = considered_for_ids
    if notice_period:
        fields["Notice Period"] = notice_period.strip()

    # Salary conversion
    min_usd = parse_lpa_to_usd(current_comp) if current_comp else None
    max_usd = parse_lpa_to_usd(expected_comp) if expected_comp else None
    if min_usd:
        fields["Salary Expectation Min"] = min_usd
    if max_usd:
        fields["Salary Expectation Max"] = max_usd

    # Geography
    geo = [g for g in (explicit_allowed_geographies or []) if g in LOCATION_CHOICES]
    if not geo and clean_location:
        geo = map_geo(clean_location)
    if geo:
        fields["Allowed Geographies"] = geo

    # Visa — India-based candidates
    if clean_location:
        loc_lower = clean_location.lower()
        india_cities = ["bangalore", "bengaluru", "hyderabad", "kolkata", "pune", "chennai",
                        "mumbai", "delhi", "noida", "gurgaon", "bhubaneswar", "bhubneshwar", "india"]
        if any(c in loc_lower for c in india_cities):
            fields["Visa Status"] = "India-based"

    return fields


# Known sourcing agencies — these should NOT be treated as target employers
KNOWN_SOURCING_AGENCIES = {
    "emb global", "emb", "corridorx", "corridor x",
    "turing", "toptal", "andela", "remote.com",
}

ROLE_WORDS = (
    "staff", "senior", "principal", "lead", "founding", "junior", "intern",
    "engineer", "developer", "consultant", "manager", "director", "analyst", "sde",
)


def _strip_slack_markup(value: str) -> str:
    s = (value or "").strip()
    # Convert Slack link markup to display text, if present.
    s = re.sub(r"<([^>|]+)\|([^>]+)>", r"\2", s)
    s = re.sub(r"[*_`~]+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _clean_candidate_name(value: str) -> str:
    s = _strip_slack_markup(value)
    # Remove leading bullets/markers.
    s = re.sub(r"^[\-\u2022]+\s*", "", s).strip()
    # If the line includes role text after a dash, keep only the name portion.
    s = re.split(r"\s+[—-]\s+", s, maxsplit=1)[0].strip()
    # Drop context-like prefixes that are not names.
    if re.match(r"^(for|target|company|employer|client|source|role|position)\b", s, re.IGNORECASE):
        return ""
    return s


def _clean_location_field(value: str) -> str:
    s = _strip_slack_markup(value)
    s = re.sub(r"^[\-\u2022]+\s*", "", s).strip()
    if not s:
        return ""
    if re.match(r"^(for|target|company|employer|client|source|role|position)\b", s, re.IGNORECASE):
        return ""
    if re.search(r"\b(availability|available|notice|join|joining|immediate|days?)\b", s, re.IGNORECASE):
        return ""
    if "linkedin.com" in s.lower():
        return ""
    if len(s) > 80:
        return ""
    return s


def _clean_target_company(value: str) -> Optional[str]:
    company = _strip_slack_markup(value).rstrip(".").strip()
    if not company:
        return None
    # Handle strings like "cobaltid staff eng role" -> "cobaltid".
    m = re.match(
        rf"^(.+?)\s+(?:{'|'.join(ROLE_WORDS)})\b.*\b(?:role|position)\b",
        company,
        re.IGNORECASE,
    )
    if m:
        company = m.group(1).strip()
    return company or None


def extract_target_company(text: str) -> Optional[str]:
    """Extract target employer from message text using heuristics.
    The 'Source' column in Divyansh's tables = sourcing agency, NOT the target company.
    Look for patterns like 'For Docsum', 'Company: Docsum', 'Target: Docsum'.
    """
    if not text:
        return None
    patterns = [
        r"(?:^|\n)\s*(?:for|target|company|employer|client)[:\s]+([^\n,]+)",
        r"(?:^|\n)\s*submitting\s+(?:for|to)\s+([^\n,]+)",
        r"(?:^|\n)\s*candidates?\s+for\s+([^\n,]+)",
        r"(?:^|\n)\s*role\s+at\s+([^\n,]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            company = _clean_target_company(match.group(1))
            if not company:
                continue
            if company.lower() not in KNOWN_SOURCING_AGENCIES:
                return company
    return None


async def extract_target_company_llm(text: str, channel: str) -> Optional[str]:
    """Use /zo/ask to extract target company from message context when heuristics fail."""
    try:
        zo_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
        if not zo_token:
            logger.warning("No ZO_CLIENT_IDENTITY_TOKEN for LLM extraction")
            return None
        prompt = (
            "Extract the TARGET EMPLOYER company name from this Slack message. "
            "IMPORTANT: The 'Source' column (e.g. 'EMB Global') is the SOURCING AGENCY, not the target employer. "
            "Known sourcing agencies to IGNORE: EMB Global, EMB, CorridorX. "
            "Look for the company the candidates are being submitted TO (the hiring company). "
            "If you cannot determine the target employer, respond with just: UNKNOWN\n\n"
            f"Message:\n{text[:1000]}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.zo.computer/zo/ask",
                headers={
                    "authorization": zo_token,
                    "content-type": "application/json",
                },
                json={
                    "input": prompt,
                    "model_name": "anthropic:claude-sonnet-4-20250514",
                },
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    answer = data.get("output", "").strip()
                    if answer and answer.upper() != "UNKNOWN":
                        answer = answer.strip('"\' ')
                        if answer.lower() not in KNOWN_SOURCING_AGENCIES:
                            logger.info(f"LLM extracted target company: {answer}")
                            return answer
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
    return None


async def extract_target_context_llm(text: str, channel: str) -> Tuple[Optional[str], List[str]]:
    """Extract both employer and role hints via LLM as JSON."""
    try:
        zo_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")
        if not zo_token:
            return None, []
        prompt = (
            "Extract hiring context from this Slack message.\n"
            "Rules:\n"
            "1) SOURCE is a sourcing agency (e.g., EMB Global, CorridorX), not employer.\n"
            "2) target_employer must be the hiring company.\n"
            "3) target_roles are roles at that employer (list, can be empty).\n"
            "Return ONLY valid JSON with this schema:\n"
            "{\"target_employer\":\"<name or UNKNOWN>\",\"target_roles\":[\"role1\",\"role2\"]}\n\n"
            f"Message:\n{text[:1500]}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.zo.computer/zo/ask",
                headers={
                    "authorization": zo_token,
                    "content-type": "application/json",
                },
                json={
                    "input": prompt,
                    "model_name": "anthropic:claude-sonnet-4-20250514",
                },
                timeout=aiohttp.ClientTimeout(total=18),
            ) as resp:
                if resp.status != 200:
                    return None, []
                data = await resp.json()
                raw = (data.get("output") or "").strip()
                m = re.search(r"\{[\s\S]*\}", raw)
                if not m:
                    return None, []
                payload = json.loads(m.group(0))
                company = (payload.get("target_employer") or "").strip()
                roles = payload.get("target_roles") or []
                if not isinstance(roles, list):
                    roles = []
                roles = [str(r).strip() for r in roles if str(r).strip()]
                if not company or company.upper() == "UNKNOWN":
                    company = None
                return company, roles
    except Exception as e:
        logger.error(f"Target context extraction failed: {e}")
    return None, []


async def extract_linkedin_from_resume(file_url: str, bot_token: str) -> Optional[str]:
    """Download a Slack-hosted resume PDF and extract LinkedIn URL from its text."""
    try:
        import pdfplumber
        import tempfile

        headers = {"Authorization": f"Bearer {bot_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to download resume: HTTP {resp.status}")
                    return None
                pdf_bytes = await resp.read()

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            with pdfplumber.open(tmp.name) as pdf:
                text = ""
                for page in pdf.pages[:5]:  # First 5 pages max
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

        # Search for LinkedIn URL patterns
        linkedin_patterns = [
            r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-%.]+",
        ]
        for pattern in linkedin_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(0)
                if not url.startswith("http"):
                    url = "https://" + url
                logger.info(f"Extracted LinkedIn from resume: {url}")
                return url
    except ImportError:
        logger.warning("pdfplumber not installed — cannot extract LinkedIn from resume")
    except Exception as e:
        logger.error(f"LinkedIn extraction from resume failed: {e}")
    return None

async def process_candidate_submission(
    event: Dict[str, Any],
    slack_client,
    channel: str,
    bot_token: str,
) -> str:
    """
    Main entry point: given a Slack event with candidate data,
    extract candidates, populate Airtable, and return a summary message.
    """
    text = event.get("text", "")
    files = event.get("files", [])
    attachments = event.get("attachments", [])
    user_id = event.get("user", "")
    ts = event.get("ts", "")

    # Strip @mentions from text
    clean_text = re.sub(r"<@[A-Z0-9]+>", "", text).strip()

    # --- Extract target employer (NOT the sourcing agency) ---
    target_company = extract_target_company(clean_text)
    role_hints = extract_role_hints(clean_text)

    # Try table extraction first
    table_rows = extract_table_from_attachments(attachments)

    candidates_to_process = []

    if table_rows:
        for row in table_rows:
            name = _clean_candidate_name(
                _get_row_value(row, ["Name of the Candidate", "Name", "Candidate Name"])
            )
            email = _get_row_value(row, ["Email ID", "Email", "Email Address"])
            location = _clean_location_field(_get_row_value(
                row,
                [
                    "Preferred Location",
                    "Current Location",
                    "Location",
                    "Candidate Location",
                    "Most Recent City",
                    "Current City",
                    "City",
                ],
            ))
            explicit_allowed_geographies = parse_allowed_geographies(
                _get_row_value(
                    row,
                    [
                        "Allowed Geographies",
                        "Permitted Geographies",
                        "Permitted Geography",
                        "Geography",
                        "Preferred Geography",
                    ],
                )
            )
            current_comp = _get_row_value(
                row, ["Current CTC", "Current Comp", "Current Compensation", "Current Salary"]
            )
            expected_comp = _get_row_value(
                row, ["Expected CTC", "Expected Comp", "Expected Compensation", "Expected Salary"]
            )
            notice_period = _get_row_value(
                row, ["Notice Period", "Notice", "Notice Duration", "Joining Timeline", "Availability to Join"]
            )
            candidates_to_process.append({
                "name": name,
                "linkedin": None,
                "email": email.strip(),
                "location": location.strip(),
                "current_comp": current_comp.strip(),
                "expected_comp": expected_comp.strip(),
                "notice_period": notice_period.strip(),
                "explicit_allowed_geographies": explicit_allowed_geographies,
                "sourcing_agency": _get_row_value(row, ["Source", "Sourcer", "Vendor", "Agency"]).strip(),
                "total_exp": _get_row_value(row, ["Total Exp", "Total Experience"]).strip(),
                "relevant_exp": _get_row_value(row, ["Relevant Exp", "Relevant Experience"]).strip(),
            })
    else:
        lines = [l.strip() for l in clean_text.split("\n") if l.strip()]
        if len(lines) >= 3:
            candidate = {"sourcing_agency": "", "name": "", "linkedin": None, "email": None,
                         "location": None, "current_comp": None, "expected_comp": None, "notice_period": None,
                         "explicit_allowed_geographies": []}
            for line in lines:
                line_lower = line.lower()
                if "linkedin.com" in line_lower:
                    url_match = re.search(r"<(https?://[^|>]+)", line)
                    candidate["linkedin"] = url_match.group(1) if url_match else line
                elif re.match(r"^(allowed geographies|permitted geographies|permitted geography|geography)\b", line_lower):
                    candidate["explicit_allowed_geographies"] = parse_allowed_geographies(line)
                elif "/" in line and ("lpa" in line_lower or "lac" in line_lower or any(c.isdigit() for c in line)):
                    parts = line.split("/")
                    if len(parts) == 2:
                        candidate["current_comp"] = parts[0].strip()
                        candidate["expected_comp"] = parts[1].strip()
                elif re.match(r"^(for|target|company|employer|client|source|role|position)\b", line_lower):
                    # Context line, not candidate identity.
                    continue
                elif not candidate["name"]:
                    candidate["name"] = _clean_candidate_name(line)
                elif not candidate["location"]:
                    candidate["location"] = _clean_location_field(line)
            if candidate["name"]:
                candidates_to_process.append(candidate)

    if not candidates_to_process:
        log_event("parse_failed", {"channel": channel, "user": user_id, "text": clean_text[:500]})
        return "I couldn't identify any candidate information in that message. Please use the standard format (Company, Name, LinkedIn, Location, Comp) or a table."

    # Build file map: match resume PDFs to candidate names
    file_map = {}
    for f in files:
        fname = f.get("name", "").lower()
        furl = f.get("url_private", "")
        for cand in candidates_to_process:
            cname = cand["name"].lower()
            name_parts = cname.split()
            if any(part in fname for part in name_parts if len(part) > 2):
                file_map[cname] = furl
                break

    # --- Extract LinkedIn from resume PDFs for candidates missing it ---
    for cand in candidates_to_process:
        if not cand.get("linkedin"):
            resume_url = file_map.get(cand["name"].lower())
            if resume_url:
                linkedin = await extract_linkedin_from_resume(resume_url, bot_token)
                if linkedin:
                    cand["linkedin"] = linkedin

    results = []
    errors = []

    # If no target company found via heuristics, try LLM extraction
    if not target_company:
        target_company = await extract_target_company_llm(clean_text, channel)

    # Extract sourcing agency name for logging (from first candidate row)
    sourcing_agency = ""
    if candidates_to_process:
        sourcing_agency = candidates_to_process[0].get("sourcing_agency", "")

    # Look up the TARGET employer in Airtable (not the sourcing agency)
    employer = await find_employer_by_name(target_company) if target_company else None
    # If heuristic company parse failed lookup, retry with richer LLM extraction
    if target_company and not employer:
        llm_company, llm_roles = await extract_target_context_llm(clean_text, channel)
        if llm_company:
            retry_employer = await find_employer_by_name(llm_company)
            if retry_employer:
                target_company = llm_company
                employer = retry_employer
        if llm_roles:
            role_hints = list(dict.fromkeys(role_hints + llm_roles))
    # If still no company, attempt full context extraction once
    if not target_company:
        llm_company, llm_roles = await extract_target_context_llm(clean_text, channel)
        if llm_company:
            target_company = llm_company
            employer = await find_employer_by_name(target_company)
        if llm_roles:
            role_hints = list(dict.fromkeys(role_hints + llm_roles))

    job_openings = []
    if employer:
        job_openings = await find_job_openings_for_employer(employer["id"])
    matched_job_openings = select_job_openings_by_role(job_openings, role_hints)
    matched_job_opening_ids = [j["id"] for j in matched_job_openings]
    matched_job_titles = [j.get("fields", {}).get("Job Title", "Unknown") for j in matched_job_openings]

    for cand in candidates_to_process:
        name = _clean_candidate_name(cand["name"])
        if not name:
            errors.append("Skipped a row with no candidate name")
            continue

        existing = await find_candidate_by_name(name)
        if existing:
            # Existing candidate: update role-level routing first, then employer-level context.
            if employer:
                role_updated = False
                if matched_job_opening_ids:
                    role_updated, _ = await update_candidate_interviewing_for(existing["id"], matched_job_opening_ids)
                updated = await update_candidate_considered_for(existing["id"], employer["id"])
                if updated:
                    employer_name = employer.get("fields", {}).get("Employer Name", target_company)
                    role_suffix = f" and linked role(s): {', '.join(matched_job_titles)}" if role_updated and matched_job_titles else ""
                    results.append(f"*{name.title()}* — already in Airtable, added *{employer_name}* to Considered For{role_suffix}")
                    log_event("candidate_considered_for_updated", {"name": name, "employer": target_company, "roles": matched_job_titles, "channel": channel})
                elif role_updated:
                    results.append(f"*{name.title()}* — already in Airtable, updated role link(s): {', '.join(matched_job_titles)}")
                    log_event("candidate_role_links_updated", {"name": name, "roles": matched_job_titles, "channel": channel})
                else:
                    results.append(f"*{name.title()}* — already in Airtable and already linked for *{target_company}*")
                    log_event("candidate_duplicate", {"name": name, "channel": channel})
            else:
                results.append(f"*{name.title()}* — already exists in Airtable, skipped")
                log_event("candidate_duplicate", {"name": name, "channel": channel})
            continue

        resume_url = file_map.get(name.lower())

        fields = build_candidate_fields(
            name=name,
            linkedin=cand.get("linkedin"),
            email=cand.get("email"),
            location=cand.get("location"),
            current_comp=cand.get("current_comp"),
            expected_comp=cand.get("expected_comp"),
            notice_period=cand.get("notice_period"),
            resume_url=resume_url,
            job_opening_ids=matched_job_opening_ids,
            considered_for_ids=[employer["id"]] if employer else None,
            explicit_allowed_geographies=cand.get("explicit_allowed_geographies") or [],
        )

        created = await create_candidate(fields)
        if "error" in created:
            err_msg = created.get("error", {}).get("message", str(created))
            errors.append(f"*{name.title()}* — Airtable error: {err_msg}")
            log_event("candidate_error", {"name": name, "error": err_msg, "channel": channel})
            continue

        candidate_id = created.get("id")

        await log_activity(
            "Resume Intake",
            f"Candidate {name.title()} added via Slack ({channel}). "
            f"Sourcing agency: {sourcing_agency or 'unknown'}. "
            f"Target employer: {target_company or 'unspecified'}. "
            f"Considered for {target_company or 'unspecified'}. "
            f"{len(matched_job_opening_ids)} role(s) linked.",
            job_id=matched_job_opening_ids[0] if matched_job_opening_ids else None,
            candidate_id=candidate_id,
        )

        missing = []
        if not cand.get("linkedin"):
            missing.append("LinkedIn")
        if not cand.get("email"):
            missing.append("Email")
        if not resume_url:
            missing.append("Resume PDF")
        if "Allowed Geographies" not in fields:
            missing.append("Allowed Geographies (permitted geography)")

        status = f"*{name.title()}* — added to Airtable"
        if matched_job_titles:
            status += f" → {', '.join(matched_job_titles)}"
        if missing:
            status += f" (missing: {', '.join(missing)} — please provide)"
        results.append(status)

        log_event("candidate_created", {
            "name": name.title(),
            "candidate_id": candidate_id,
            "target_employer": target_company or "unspecified",
            "sourcing_agency": sourcing_agency,
            "job_openings": matched_job_opening_ids,
            "channel": channel,
            "missing_fields": missing,
        })

    # Build summary
    summary_parts = []
    if results:
        summary_parts.append("*Candidate Processing Results:*")
        for r in results:
            summary_parts.append(f"• {r}")
    if errors:
        summary_parts.append("\n*Issues:*")
        for e in errors:
            summary_parts.append(f"• {e}")
    if not employer and target_company:
        summary_parts.append(f"\n⚠️ Could not find employer \"{target_company}\" in Airtable — candidates added without job linking. Please verify the company name.")
    elif employer and len(job_openings) > 1 and not matched_job_openings:
        if len(job_openings) > 1:
            available = ", ".join([j.get("fields", {}).get("Job Title", "Unknown") for j in job_openings])
            summary_parts.append(f"\n⚠️ Found employer *{target_company}* but role was ambiguous. Please reply with one or more role titles. Open roles: {available}")
    elif not target_company:
        summary_parts.append("\n⚠️ No target employer identified. Please reply with the company these candidates are being submitted for (e.g. \"For Docsum\").")

    return "\n".join(summary_parts)


def is_candidate_submission(event: Dict[str, Any]) -> bool:
    """Heuristic: does this event look like a candidate submission?"""
    text = (event.get("text", "") or "").lower()
    files = event.get("files", [])
    attachments = event.get("attachments", [])

    # Has a table attachment
    for att in attachments:
        for block in att.get("blocks", []):
            if block.get("type") == "table":
                return True

    # Has resume PDFs
    has_resume = any("resume" in (f.get("name", "") or "").lower() for f in files)
    if has_resume:
        return True

    # Has LinkedIn URL
    if "linkedin.com/in/" in text:
        return True

    # Has LPA/salary info
    if any(kw in text for kw in ["lpa", "ctc", "salary", "comp"]):
        return True

    # Has candidate format indicators
    clean = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
    lines = [l.strip() for l in clean.split("\n") if l.strip()]
    if len(lines) >= 3:
        # Check if second line looks like a person's name (2-4 words, no URLs)
        if len(lines) >= 2:
            name_line = lines[1]
            words = name_line.split()
            if 1 <= len(words) <= 4 and not any(c in name_line for c in ["http", "@", "/"]):
                return True

    return False
