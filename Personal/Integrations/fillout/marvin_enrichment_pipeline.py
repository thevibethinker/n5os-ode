#!/usr/bin/env python3
"""
Marvin Ventures Founder Enrichment Pipeline v2

Enhanced pipeline that does REAL personalization:
1. Aviato enrichment (person + company)
2. LinkedIn profile analysis (background, roles, "why they get it")
3. Web search for recent news/funding
4. Knowledge retrieval from content library
5. Email generation with earned personalization

Triggered when a Marvin Ventures x Careerspan Perk Redemption form is submitted.
"""

import argparse
import json
import logging
import os
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.parse
import re as _re

# Ensure Aviato client is importable regardless of CWD
AVIATO_DIR = Path("/home/workspace/Inbox/20251120-093554_Integrations/Aviato").resolve()
if str(AVIATO_DIR) not in sys.path:
    sys.path.insert(0, str(AVIATO_DIR))

# Add paths for imports
sys.path.insert(0, str(AVIATO_DIR))
sys.path.insert(0, '/home/workspace/N5/scripts')

from aviato_client import AviatoClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
MARVIN_FORM_ID = "8JxXF1AVZeus"
CRM_DB_PATH = Path("/home/workspace/N5/data/crm_v3.db")
CONTENT_LIBRARY_DB = Path("/home/workspace/N5/data/content_library.db")
KNOWLEDGE_DIR = Path("/home/workspace/Knowledge/content-library")
DIGESTS_DIR = Path("/home/workspace/N5/digests/marvin-outreach")
DIGESTS_DIR.mkdir(parents=True, exist_ok=True)


def load_content_library_item(item_id: str) -> Optional[str]:
    """Load a single content library item by id (returns item.content)."""
    try:
        conn = sqlite3.connect(CONTENT_LIBRARY_DB)
        cur = conn.cursor()
        cur.execute("SELECT content FROM items WHERE id = ? AND deprecated = 0", (item_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return row[0]
    except Exception as e:
        logger.warning(f"Content library lookup failed for {item_id}: {e}")
        return None


@dataclass
class FormSubmission:
    """Parsed form submission data."""
    name: str
    company_name: str
    email: str
    linkedin_url: Optional[str] = None
    is_marvin_founder: bool = False
    roles_hiring: str = ""
    pain_points: List[str] = field(default_factory=list)
    jd_link: Optional[str] = None
    consented: bool = False
    raw_questions: List[Dict] = field(default_factory=list)


@dataclass
class ResearchDossier:
    """All gathered intelligence about the prospect."""
    # Basic info
    submission: FormSubmission = None
    
    # Aviato data
    person_data: Optional[Dict] = None
    company_data: Optional[Dict] = None
    
    # LinkedIn analysis
    linkedin_profile: Optional[Dict] = None
    current_role: Optional[str] = None
    previous_roles: List[str] = field(default_factory=list)
    has_hiring_manager_experience: bool = False
    has_hypergrowth_experience: bool = False
    has_consulting_background: bool = False
    years_experience: Optional[int] = None
    
    # Recent signals
    recent_funding: Optional[Dict] = None
    recent_news: List[Dict] = field(default_factory=list)
    is_currently_hiring: bool = False
    open_roles: List[str] = field(default_factory=list)
    
    # JD link extraction
    jd_title: Optional[str] = None
    
    # Why they "get it" - inferred from research
    credibility_hooks: List[str] = field(default_factory=list)
    knowledge_hooks: List[str] = field(default_factory=list)
    
    # Content library matches
    relevant_content: List[Dict] = field(default_factory=list)
    
    # Generated outputs
    subject_line: str = ""
    email_body: str = ""
    email_html: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "submission": {
                "name": self.submission.name if self.submission else None,
                "company": self.submission.company_name if self.submission else None,
                "email": self.submission.email if self.submission else None,
                "linkedin_url": self.submission.linkedin_url if self.submission else None,
                "roles_hiring": self.submission.roles_hiring if self.submission else None,
                "pain_points": self.submission.pain_points if self.submission else [],
            },
            "enrichment": {
                "person": self.person_data,
                "company": {
                    "name": self.company_data.get("name") if self.company_data else None,
                    "description": self.company_data.get("description") if self.company_data else None,
                    "industry": self.company_data.get("industry") if self.company_data else None,
                    "headcount": self.company_data.get("headcount") if self.company_data else None,
                    "founded_year": self.company_data.get("foundedYear") if self.company_data else None,
                    "funding_stage": self.company_data.get("fundingStage") if self.company_data else None,
                    "total_raised": self.company_data.get("totalRaised") if self.company_data else None,
                } if self.company_data else None,
            },
            "linkedin_analysis": {
                "current_role": self.current_role,
                "previous_roles": self.previous_roles,
                "has_hiring_manager_experience": self.has_hiring_manager_experience,
                "has_hypergrowth_experience": self.has_hypergrowth_experience,
                "has_consulting_background": self.has_consulting_background,
                "years_experience": self.years_experience,
            },
            "signals": {
                "recent_funding": self.recent_funding,
                "recent_news": self.recent_news[:3] if self.recent_news else [],
                "is_currently_hiring": self.is_currently_hiring,
                "jd_title": self.jd_title,
                "open_roles": self.open_roles,
            },
            "credibility_hooks": self.credibility_hooks,
            "relevant_content": self.relevant_content,
        }


def parse_form_submission(event: Dict) -> Optional[FormSubmission]:
    """Extract structured data from Fillout webhook event."""
    payload = event.get("payload", {})
    form_id = payload.get("formId")
    
    if form_id != MARVIN_FORM_ID:
        logger.info(f"Skipping non-Marvin form: {form_id}")
        return None
    
    submission_data = payload.get("submission", {})
    questions = submission_data.get("questions", [])
    
    # Build question map
    q_map = {}
    for q in questions:
        q_name = q.get("name", "").lower()
        q_map[q_name] = q.get("value")
    
    # Extract fields (fuzzy matching on question names)
    name = None
    company = None
    email = None
    linkedin_url = None
    is_marvin = False
    roles = ""
    pain_points = []
    jd_link = None
    consented = False
    
    for q in questions:
        q_name = q.get("name", "").lower()
        q_value = q.get("value")
        
        if "your name" in q_name:
            name = q_value
        elif "company" in q_name and "name" in q_name:
            company = q_value
        elif "email" in q_name:
            email = q_value
        elif "linkedin" in q_name:
            linkedin_url = q_value
        elif "marvin" in q_name and "founder" in q_name:
            is_marvin = q_value == "Yes" if isinstance(q_value, str) else bool(q_value)
        elif "roles" in q_name and "hiring" in q_name:
            roles = q_value or ""
        elif "pain point" in q_name:
            if isinstance(q_value, list):
                pain_points = q_value
            elif q_value:
                pain_points = [q_value]
        elif "jd" in q_name or "posting" in q_name:
            jd_link = q_value
        elif "consent" in q_name:
            consented = q_value == "Yes" if isinstance(q_value, str) else bool(q_value)
    
    if not name or not email:
        logger.warning("Missing required fields (name or email)")
        return None
    
    return FormSubmission(
        name=name,
        company_name=company or "",
        email=email,
        linkedin_url=linkedin_url,
        is_marvin_founder=is_marvin,
        roles_hiring=roles,
        pain_points=pain_points,
        jd_link=jd_link,
        consented=consented,
        raw_questions=questions
    )


def enrich_with_aviato(dossier: ResearchDossier) -> None:
    """Layer 1: Aviato person + company enrichment."""
    logger.info("LAYER 1: Aviato enrichment")
    
    # Pass explicit env_file path since we're running from fillout directory
    aviato_env = str(AVIATO_DIR / ".env")
    client = AviatoClient(env_file=aviato_env)
    submission = dossier.submission
    
    # Person enrichment via LinkedIn URL
    if submission.linkedin_url:
        logger.info(f"  Enriching person via LinkedIn: {submission.linkedin_url}")
        try:
            dossier.person_data = client.enrich_person(linkedin_url=submission.linkedin_url)
        except Exception as e:
            logger.warning(f"  Person enrichment failed: {e}")
    
    # Company enrichment via email domain
    email_domain = submission.email.split("@")[1] if "@" in submission.email else None
    if email_domain and email_domain not in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
        logger.info(f"  Enriching company via domain: {email_domain}")
        try:
            dossier.company_data = client.enrich_company(website=email_domain)
        except Exception as e:
            logger.warning(f"  Company enrichment failed: {e}")


def analyze_linkedin_background(dossier: ResearchDossier) -> None:
    """Layer 2: Analyze LinkedIn for credibility signals."""
    logger.info("LAYER 2: LinkedIn background analysis")
    
    person = dossier.person_data
    if not person:
        logger.info("  No person data available, skipping LinkedIn analysis")
        return
    
    # Extract work history
    experiences = person.get("workExperiences", []) or []
    
    # Consulting firms to check
    consulting_firms = ["mckinsey", "bain", "bcg", "deloitte", "accenture", "kearney", "oliver wyman"]
    hypergrowth_signals = ["series", "ipo", "unicorn", "scaled", "grew", "hypergrowth"]
    manager_signals = ["manager", "director", "vp", "head of", "lead", "chief"]
    
    roles_analyzed = []
    for exp in experiences[:10]:  # Last 10 roles
        title = (exp.get("title") or "").lower()
        company = (exp.get("company") or "").lower()
        description = (exp.get("description") or "").lower()
        
        roles_analyzed.append(f"{exp.get('title', '')} @ {exp.get('company', '')}")
        
        # Check for consulting background
        if any(firm in company for firm in consulting_firms):
            dossier.has_consulting_background = True
            dossier.credibility_hooks.append(f"Ex-{exp.get('company', 'consulting')} — knows the high-bar hiring culture")
        
        # Check for hiring manager experience
        if any(signal in title for signal in manager_signals):
            dossier.has_hiring_manager_experience = True
            if "hiring" not in str(dossier.credibility_hooks):
                dossier.credibility_hooks.append("Has managed teams — knows the pain of screening candidates")
        
        # Check for hypergrowth experience
        if any(signal in description for signal in hypergrowth_signals):
            dossier.has_hypergrowth_experience = True
            dossier.credibility_hooks.append("Scaled through hypergrowth — seen what happens when hiring breaks")
    
    dossier.previous_roles = roles_analyzed[:5]
    
    # Current role
    if experiences:
        current = experiences[0]
        dossier.current_role = f"{current.get('title', '')} @ {current.get('company', '')}"
    
    logger.info(f"  Credibility hooks found: {dossier.credibility_hooks}")


def _is_probable_url(val: Optional[str]) -> bool:
    if not val:
        return False
    v = val.strip()
    if v.lower() in {"n/a", "na", "none", "null", ""}:
        return False
    try:
        u = urllib.parse.urlparse(v)
        return u.scheme in {"http", "https"} and bool(u.netloc)
    except Exception:
        return False


def _extract_title_from_html(html: str) -> Optional[str]:
    # Try <title>
    m = _re.search(r"<title[^>]*>(.*?)</title>", html, flags=_re.IGNORECASE | _re.DOTALL)
    if m:
        t = _re.sub(r"\s+", " ", m.group(1)).strip()
        if t:
            return t[:160]
    # Try first <h1>
    m = _re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=_re.IGNORECASE | _re.DOTALL)
    if m:
        t = _re.sub(r"<[^>]+>", " ", m.group(1))
        t = _re.sub(r"\s+", " ", t).strip()
        if t:
            return t[:160]
    return None


def _fetch_jd_title(url: str) -> Optional[str]:
    """Best-effort fetch of job posting title from a URL."""
    try:
        # Use curl with a conservative timeout
        res = subprocess.run(
            ["curl", "-L", "-s", "--max-time", "12", "--user-agent", "Mozilla/5.0", url],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            return None
        html = res.stdout or ""
        if not html:
            return None
        return _extract_title_from_html(html)
    except Exception:
        return None


def search_recent_signals(dossier: ResearchDossier) -> None:
    """Layer 3: Web search for recent funding/news."""
    logger.info("LAYER 3: Recent signals search")
    
    submission = dossier.submission
    
    # 3a) JD title extraction (best-effort)
    if _is_probable_url(submission.jd_link):
        jd_url = submission.jd_link.strip()
        title = _fetch_jd_title(jd_url)
        if title:
            dossier.jd_title = title
            # store as a role hint (we'll phrase it as best-guess)
            dossier.open_roles.append(title)
            logger.info(f"  JD title extracted: {title}")
    
    company = submission.company_name
    
    if not company:
        logger.info("  No company name, skipping news search")
        return
    
    # Search for recent funding
    try:
        funding_query = f"{company} funding raised series"
        result = subprocess.run(
            ["python3", "-c", f"""
import json
import subprocess
result = subprocess.run([
    "curl", "-s", "https://api.tavily.com/search",
    "-H", "Content-Type: application/json",
    "-d", json.dumps({{
        "api_key": "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",
        "query": "{funding_query}",
        "search_depth": "basic",
        "max_results": 3,
        "include_domains": ["techcrunch.com", "crunchbase.com", "bloomberg.com", "forbes.com"]
    }})
], capture_output=True, text=True)
print(result.stdout)
"""],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.stdout:
            search_results = json.loads(result.stdout)
            results = search_results.get("results", [])
            if results:
                for r in results:
                    if "funding" in r.get("title", "").lower() or "raise" in r.get("title", "").lower():
                        dossier.recent_funding = {
                            "title": r.get("title"),
                            "url": r.get("url"),
                            "snippet": r.get("content", "")[:200]
                        }
                        dossier.credibility_hooks.append(f"Recently raised — likely scaling the team now")
                        break
                
                dossier.recent_news = [
                    {"title": r.get("title"), "url": r.get("url")}
                    for r in results[:3]
                ]
                logger.info(f"  Found {len(results)} news items")
    except Exception as e:
        logger.warning(f"  News search failed: {e}")
    
    # Check if currently hiring (from Aviato company data)
    if dossier.company_data:
        headcount = dossier.company_data.get("headcount")
        if headcount and headcount > 5:
            dossier.is_currently_hiring = True  # Assume growing companies are hiring


def retrieve_relevant_content(dossier: ResearchDossier) -> List[Dict[str, str]]:
    """Layer 4: Pull relevant Careerspan POV from knowledge/content library."""
    logger.info("LAYER 4: Knowledge retrieval")

    items: List[Dict[str, str]] = []

    # Always include the canonical email signature as a content item
    items.append({
        "id": "vrijen_signature",
        "title": "Signature (email footer)",
        "content": load_content_library_item("vrijen_signature") or ""
    })

    pain_points = dossier.submission.pain_points if dossier.submission else []
    
    # Keywords to match against content
    keywords = []
    for pain in pain_points:
        pain_lower = pain.lower()
        if "resume" in pain_lower:
            keywords.extend(["signal", "firehose", "noise"])
        if "ats" in pain_lower:
            keywords.extend(["ats", "tracking", "broken"])
        if "time" in pain_lower:
            keywords.extend(["friction", "filter"])
    
    # Add default keywords
    keywords.extend(["hiring", "signal", "collapse"])
    
    # Search content library database
    try:
        conn = sqlite3.connect(CONTENT_LIBRARY_DB)
        cursor = conn.cursor()
        
        # Get snippets that might be relevant
        cursor.execute("""
            SELECT id, title, content FROM items 
            WHERE type = 'snippet' AND deprecated = 0
        """)
        snippets = cursor.fetchall()
        
        for snippet_id, title, content in snippets:
            title_lower = (title or "").lower()
            content_lower = (content or "").lower()
            
            if any(kw in title_lower or kw in content_lower for kw in keywords):
                dossier.relevant_content.append({
                    "id": snippet_id,
                    "title": title,
                    "content": content[:500] if content else ""
                })
        
        conn.close()
    except Exception as e:
        logger.warning(f"  Content library query failed: {e}")
    
    # Also load key markdown files from Knowledge
    key_files = [
        "hiring-signal-collapse-worldview.md",
        "smart-friction-hiring-funnel-blurb.md"
    ]
    
    for filename in key_files:
        filepath = KNOWLEDGE_DIR / filename
        if filepath.exists():
            try:
                content = filepath.read_text()[:2000]  # First 2000 chars
                dossier.relevant_content.append({
                    "id": filename,
                    "title": filename.replace("-", " ").replace(".md", "").title(),
                    "content": content
                })
            except Exception as e:
                logger.warning(f"  Failed to load {filename}: {e}")
    
    logger.info(f"  Retrieved {len(dossier.relevant_content)} content items")


def generate_subject_line(dossier: ResearchDossier) -> str:
    """Generate personalized subject line based on research."""
    
    # Priority order for subject line personalization
    if dossier.recent_funding:
        return "Re: Careerspan perk for Marvin — congrats on the round"
    
    if dossier.has_consulting_background:
        return "Re: Careerspan perk for Marvin — fellow high-standards person here"
    
    if dossier.is_currently_hiring:
        return "Re: Careerspan perk for Marvin — ready to help with hiring"
    
    if dossier.has_hypergrowth_experience:
        return "Re: Careerspan perk for Marvin — you know the scaling pain"
    
    # Generic fallback - warm service tone
    return "Re: Careerspan perk for Marvin — here to help"


def generate_email_body(dossier: ResearchDossier) -> str:
    """
    Generate plain text email body.
    
    KEY SHIFT: This is NOT cold outreach...
    """
    core_body = _generate_email_core_plain(dossier)

    signature = load_content_library_item("vrijen_signature_plain")
    if signature:
        return core_body + "\n\n" + signature.strip() + "\n"

    return core_body + "\n\n— Vrijen\n"


def _generate_email_core_plain(dossier: ResearchDossier) -> str:
    """Generate the email body WITHOUT any signature (plain text)."""
    submission = dossier.submission
    first_name = submission.name.split()[0] if submission.name else "there"
    calendly = "https://calendly.com/v-at-careerspan/30min"

    personalization_paragraph = _generate_personalized_context(dossier).strip()

    body_parts = [
        f"Hey {first_name},",
        "",
        "Thanks for signing up for the Careerspan demo through Marvin Ventures.",
        "",
    ]

    if personalization_paragraph:
        body_parts.extend([personalization_paragraph, ""])

    body_parts.extend([
        "As a Marvin member, you've got 3 months of role support covered — let's put it to work.",
        "",
        "Ready to get started?",
        calendly,
    ])

    return "\n".join(body_parts).strip()


def _plaintext_to_html(text: str) -> str:
    # Minimal conversion: paragraphs separated by blank lines, preserve single newlines as <br/>
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    html_parts = []
    for p in parts:
        html_parts.append(p.replace("\n", "<br/>\n"))
    return "<br/><br/>\n".join(html_parts)


def generate_email_html(dossier: ResearchDossier) -> str:
    """Generate HTML email body with embedded-link signature."""
    core_plain = _generate_email_core_plain(dossier)
    html_body = _plaintext_to_html(core_plain)

    signature = load_content_library_item("vrijen_signature")
    if signature:
        return html_body + "<br/><br/>\n" + signature.strip()

    return html_body


def _generate_personalized_context(dossier: ResearchDossier) -> str:
    """Generate the personalized middle section based on research."""
    submission = dossier.submission
    hooks = []
    
    # JD-specific hook (if provided)
    if dossier.jd_title:
        hooks.append(f"I took a look at the role you linked (\"{dossier.jd_title}\"). Those are exactly the kinds of hires where signal gets noisy fast.")
    
    # Recent funding hook
    if dossier.recent_funding:
        hooks.append(f"Congrats on the recent round — I imagine hiring is top of mind as you scale.")
    
    # Consulting/high-standards background
    if dossier.has_consulting_background:
        hooks.append("As a fellow ex-consulting person, I know you've seen what 'great' looks like — and how painful it is when hiring doesn't surface that.")
    
    # Actively hiring
    if dossier.is_currently_hiring:
        if dossier.open_roles:
            roles_str = ", ".join(dossier.open_roles[:2])
            hooks.append(f"Saw you're hiring for {roles_str} — that's exactly where we can help cut through the noise.")
        else:
            hooks.append("Saw you're actively hiring — that's exactly where we can help cut through the noise.")
    
    # Hypergrowth experience
    if dossier.has_hypergrowth_experience:
        hooks.append("You've been through hypergrowth before, so you know the hiring chaos that comes with scaling fast.")
    
    # Pain points from form (translated, not robotic)
    if submission.pain_points:
        pain_translation = _translate_pain_points(submission.pain_points)
        if pain_translation:
            hooks.append(pain_translation)
    
    # Knowledge-based hook (signal collapse / smart friction angle)
    if dossier.knowledge_hooks:
        # Only add if we don't already have 2+ hooks
        if len(hooks) < 2:
            hooks.append(dossier.knowledge_hooks[0])
    
    # Return best 1-2 hooks, joined
    if hooks:
        return " ".join(hooks[:2])
    
    # Fallback if no hooks found
    return ""


def _translate_pain_points(pain_points: List[str]) -> str:
    """Translate form pain points into natural language."""
    translations = {
        "resume_review": "You mentioned the resume overload — hundreds of applications, maybe a handful worth reading.",
        "screening": "You flagged screening as a pain point — we hear that a lot from founders.",
        "ats": "The ATS frustration you mentioned is real — most tools weren't built for how founders actually hire.",
        "time": "Time is the thing you don't have, and hiring eats it fast.",
        "quality": "Finding quality candidates in the noise — that's the core problem we solve.",
    }
    
    for pain in pain_points:
        pain_lower = pain.lower()
        for key, translation in translations.items():
            if key in pain_lower:
                return translation
    
    return ""


def save_draft(dossier: ResearchDossier) -> Path:
    """Save the draft to digests folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_slug = re.sub(r'[^a-z0-9]+', '-', dossier.submission.name.lower())
    filename = f"{timestamp}_{name_slug}_draft.json"
    filepath = DIGESTS_DIR / filename
    
    output = {
        "generated_at": datetime.now().isoformat(),
        "form_id": MARVIN_FORM_ID,
        "draft": {
            "to": dossier.submission.email,
            "subject": dossier.subject_line,
            "body": dossier.email_body,
            "html_body": dossier.email_html,
            "context": dossier.to_dict()
        },
        "actions_for_zo": [
            {
                "action": "create_gmail_draft",
                "params": {
                    "to": dossier.submission.email,
                    "subject": dossier.subject_line,
                    "body": dossier.email_html,
                    "bodyType": "html",
                    "from_email": "vrijen@mycareerspan.com"
                }
            },
            {
                "action": "send_sms",
                "params": {
                    "message": f"🚀 New Marvin lead: {dossier.submission.name} at {dossier.submission.company_name}. Subject: \"{dossier.subject_line}\". Draft ready."
                }
            }
        ]
    }
    
    filepath.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    logger.info(f"Draft saved to {filepath}")
    return filepath


def upsert_crm_individual(dossier: ResearchDossier) -> None:
    """Create or update CRM profile record (crm_v3 schema)."""
    sub = dossier.submission
    if not sub:
        return

    try:
        conn = sqlite3.connect(CRM_DB_PATH)
        cur = conn.cursor()

        now = datetime.now().isoformat()
        person_id = None
        company_id = None
        if dossier.person_data:
            person_id = dossier.person_data.get("id")
            # try best-effort company id
            try:
                exp = (dossier.person_data.get("experienceList") or [])[0]
                company_id = exp.get("companyID") if isinstance(exp, dict) else None
            except Exception:
                company_id = None

        # Does profile exist?
        cur.execute("SELECT id FROM profiles WHERE email = ?", (sub.email,))
        row = cur.fetchone()

        if row:
            cur.execute(
                """
                UPDATE profiles
                SET
                  name = COALESCE(?, name),
                  primary_email = COALESCE(?, primary_email),
                  linkedin_url = COALESCE(?, linkedin_url),
                  aviato_person_id = COALESCE(?, aviato_person_id),
                  aviato_company_id = COALESCE(?, aviato_company_id),
                  enrichment_status = 'enriched',
                  last_enriched_at = ?,
                  last_enrichment_source = 'marvin_intake',
                  last_enrichment_error = NULL
                WHERE email = ?
                """,
                (
                    sub.name,
                    sub.email,
                    sub.linkedin_url,
                    person_id,
                    company_id,
                    now,
                    sub.email,
                ),
            )
        else:
            # yaml_path is required; match existing convention in CRM v3 (slug under Knowledge/crm/individuals)
            slug = re.sub(r"[^a-z0-9]+", "-", (sub.name or sub.email).lower()).strip("-")
            yaml_path = f"Knowledge/crm/individuals/{slug}.md"
            cur.execute(
                """
                INSERT INTO profiles (
                  email, name, yaml_path, source,
                  primary_email, linkedin_url,
                  aviato_person_id, aviato_company_id,
                  enrichment_status, profile_quality,
                  last_enriched_at, last_enrichment_source
                ) VALUES (?, ?, ?, 'marvin_intake', ?, ?, ?, ?, 'enriched', 'stub', ?, 'marvin_intake')
                """,
                (
                    sub.email,
                    sub.name or sub.email,
                    yaml_path,
                    sub.email,
                    sub.linkedin_url,
                    person_id,
                    company_id,
                    now,
                ),
            )

        conn.commit()
        conn.close()
        logger.info(f"CRM profile upserted: {sub.email}")
    except Exception as e:
        logger.error(f"CRM upsert failed: {e}")


def upsert_crm_organization(dossier: ResearchDossier) -> None:
    """Create or update CRM organization record."""
    submission = dossier.submission
    company_name = submission.company_name
    
    if not company_name:
        return
    
    try:
        conn = sqlite3.connect(CRM_DB_PATH)
        cursor = conn.cursor()
        
        slug = re.sub(r'[^a-z0-9]+', '-', company_name.lower()).strip('-')
        
        # Extract domain from email
        domain = submission.email.split("@")[1] if "@" in submission.email else None
        
        # Check if org exists
        cursor.execute("SELECT id FROM organizations WHERE slug = ?", (slug,))
        existing = cursor.fetchone()
        
        # Get company data from Aviato
        aviato_id = None
        linkedin_url = None
        description = None
        industry = None
        founded_year = None
        headcount = None
        location = None
        
        if dossier.company_data:
            aviato_id = dossier.company_data.get("id")
            linkedin_url = dossier.company_data.get("linkedinUrl")
            description = dossier.company_data.get("description")
            industry = dossier.company_data.get("industry")
            founded_year = dossier.company_data.get("foundedYear")
            headcount = dossier.company_data.get("headcount")
            location = dossier.company_data.get("location")
        
        enriched_at = datetime.now().isoformat()
        
        if existing:
            cursor.execute("""
                UPDATE organizations SET
                    domain = COALESCE(?, domain),
                    aviato_id = COALESCE(?, aviato_id),
                    linkedin_url = COALESCE(?, linkedin_url),
                    description = COALESCE(?, description),
                    industry = COALESCE(?, industry),
                    founded_year = COALESCE(?, founded_year),
                    headcount_range = COALESCE(?, headcount_range),
                    location = COALESCE(?, location),
                    enrichment_status = 'enriched',
                    last_enriched_at = ?,
                    updated_at = ?
                WHERE slug = ?
            """, (
                domain, aviato_id, linkedin_url, description, industry,
                founded_year, str(headcount) if headcount else None, location,
                enriched_at, enriched_at, slug
            ))
        else:
            cursor.execute("""
                INSERT INTO organizations (
                    name, slug, domain, source, aviato_id, linkedin_url,
                    description, industry, founded_year, headcount_range, location,
                    enrichment_status, last_enriched_at, created_at, updated_at
                ) VALUES (?, ?, ?, 'marvin_intake', ?, ?, ?, ?, ?, ?, ?, 'enriched', ?, ?, ?)
            """, (
                company_name, slug, domain, aviato_id, linkedin_url,
                description, industry, founded_year, str(headcount) if headcount else None,
                location, enriched_at, enriched_at, enriched_at
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"CRM organization upserted: {slug}")
    except Exception as e:
        logger.error(f"CRM org upsert failed: {e}")


def process_marvin_submission(event: Dict) -> Dict:
    """Main pipeline: process a Marvin Ventures form submission."""
    logger.info("=" * 60)
    logger.info("MARVIN VENTURES ENRICHMENT PIPELINE v2")
    logger.info("=" * 60)
    
    result = {
        "success": False,
        "error": None,
        "draft_path": None,
        "subject_line": None,
        "email_preview": None,
        "credibility_hooks": [],
        "actions_for_zo": []
    }
    
    # Step 1: Parse form submission
    logger.info("STEP 1: Parsing form submission")
    submission = parse_form_submission(event)
    if not submission:
        result["error"] = "Failed to parse form submission or not a Marvin form"
        return result
    
    if not submission.consented:
        result["error"] = "User did not consent to contact"
        return result
    
    logger.info(f"  Parsed: {submission.name} at {submission.company_name}")
    
    # Create research dossier
    dossier = ResearchDossier(submission=submission)
    
    # Step 2: Aviato enrichment
    enrich_with_aviato(dossier)
    
    # Step 3: LinkedIn background analysis
    analyze_linkedin_background(dossier)
    
    # Step 4: Recent signals (funding, news)
    search_recent_signals(dossier)
    
    # Step 5: Knowledge retrieval
    retrieve_relevant_content(dossier)
    
    # Step 6: Generate subject line
    logger.info("STEP 6: Generating subject line")
    dossier.subject_line = generate_subject_line(dossier)
    logger.info(f"  Subject: {dossier.subject_line}")
    
    # Step 7: Generate email body
    logger.info("STEP 7: Generating email body")
    dossier.email_body = generate_email_body(dossier)
    dossier.email_html = generate_email_html(dossier)
    logger.info(f"  Email preview: {dossier.email_body[:100]}...")
    
    # Step 8: Save draft
    logger.info("STEP 8: Saving draft")
    draft_path = save_draft(dossier)
    
    # Step 9: Upsert CRM records
    logger.info("STEP 9: Upserting CRM records")
    upsert_crm_individual(dossier)
    upsert_crm_organization(dossier)
    
    # Populate result
    result["success"] = True
    result["draft_path"] = str(draft_path)
    result["subject_line"] = dossier.subject_line
    result["email_preview"] = dossier.email_body[:300]
    result["credibility_hooks"] = dossier.credibility_hooks
    result["actions_for_zo"] = [
        {
            "action": "create_gmail_draft",
            "params": {
                "to": dossier.submission.email,
                "subject": dossier.subject_line,
                "body": dossier.email_html,
                "bodyType": "html",
                "from_email": "vrijen@mycareerspan.com",
            },
        },
        {
            "action": "send_sms",
            "params": {
                "message": f"🚀 New Marvin lead: {dossier.submission.name} at {dossier.submission.company_name}. Subject: \"{dossier.subject_line}\". Draft ready.",
            },
        },
    ]
    
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"  Credibility hooks: {dossier.credibility_hooks}")
    logger.info(f"  Subject: {dossier.subject_line}")
    logger.info("=" * 60)
    
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Marvin Ventures Enrichment Pipeline v2")
    parser.add_argument("--test", action="store_true", help="Run with latest test submission")
    parser.add_argument("--event-file", type=str, help="Path to event JSON file")
    args = parser.parse_args()
    
    if args.test:
        # Load latest event from form-specific file
        form_file = Path("/home/workspace/Personal/Integrations/fillout/events/forms") / f"{MARVIN_FORM_ID}.jsonl"
        if form_file.exists():
            with open(form_file) as f:
                lines = f.readlines()
                if lines:
                    # Use the second entry if available (first is often null test)
                    event = json.loads(lines[-1])
                    result = process_marvin_submission(event)
                    print(json.dumps(result, indent=2))
                else:
                    print("No events found")
        else:
            print(f"Form file not found: {form_file}")
    elif args.event_file:
        with open(args.event_file) as f:
            event = json.load(f)
        result = process_marvin_submission(event)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python marvin_enrichment_pipeline.py --test OR --event-file <path>")

















