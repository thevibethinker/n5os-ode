from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException, Request

import os
import subprocess
import threading
import requests as http_requests  # Renamed to avoid conflict with FastAPI Request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fillout Webhook Receiver")

# Base directory for event logs (JSONL)
EVENTS_BASE_DIR = Path("/home/workspace/N5/Integrations/fillout/events").resolve()
EVENTS_BASE_DIR.mkdir(parents=True, exist_ok=True)

# Known forms tracking
KNOWN_FORMS_PATH = Path("/home/workspace/N5/Integrations/fillout/known_forms.json").resolve()

# Career Hotline resume ingestion config
# Map Fillout form IDs to career hotline intake forms
# When a submission comes from one of these forms, trigger resume ingestion
CAREER_HOTLINE_FORM_IDS: set[str] = set(
    filter(None, os.environ.get("CAREER_HOTLINE_FILLOUT_FORMS", "").split(","))
)
RESUME_INGEST_SCRIPT = Path("/home/workspace/Skills/career-coaching-hotline/scripts/resume_ingest.py")
CAREER_HOTLINE_PHONE_FIELD = os.environ.get("CAREER_HOTLINE_PHONE_FIELD", "")


def _load_known_forms() -> set[str]:
    """Load set of known form IDs from known_forms.json."""
    if KNOWN_FORMS_PATH.exists():
        try:
            with KNOWN_FORMS_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("forms", []))
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Could not parse {KNOWN_FORMS_PATH}, starting fresh")
    return set()


def _save_known_forms(forms: set[str]) -> None:
    """Save set of known form IDs to known_forms.json."""
    data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_forms": len(forms),
        "forms": sorted(list(forms))
    }
    with KNOWN_FORMS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _check_new_form(form_id: str) -> bool:
    """Check if form_id is new and update tracking if so.

    Returns:
        True if the form is newly detected, False otherwise.
    """
    known_forms = _load_known_forms()

    if form_id not in known_forms:
        known_forms.add(form_id)
        _save_known_forms(known_forms)
        logger.info(f"NEW_FORM_DETECTED: {form_id}")
        return True

    return False


def _trigger_survey_analysis(form_id: str, form_name: str) -> None:
    """Trigger the Dynamic Survey Analyzer skill via Zo API.
    
    This runs in a background thread to not block the webhook response.
    """
    zo_token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not zo_token:
        logger.warning("ZO_CLIENT_IDENTITY_TOKEN not set, cannot trigger analysis")
        return
    
    prompt = f"""A new Fillout form just received its first submission. Run the dynamic-survey-analyzer skill to analyze it.

Form ID: {form_id}
Form Name: {form_name}

Steps:
1. Use the fillout_client.py to fetch submissions for this form
2. Run the analysis pipeline (context, quantitative, level upper)
3. Generate the dashboard and analysis document
4. Save outputs to Datasets/survey-analyses/{form_id}/
5. Text V a brief summary when complete

This is an automated trigger - proceed without asking for confirmation."""

    try:
        response = http_requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": zo_token,
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=300  # 5 min timeout for analysis
        )
        if response.status_code == 200:
            logger.info(f"Survey analysis triggered successfully for form {form_id}")
        else:
            logger.error(f"Failed to trigger analysis: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        logger.error(f"Error triggering survey analysis: {e}")


def _trigger_resume_ingestion(payload: Dict[str, Any]) -> None:
    """Trigger career hotline resume ingestion in a background thread.

    Detects phone number and file upload from the Fillout submission,
    then runs the resume_ingest.py script via subprocess.
    """
    if not RESUME_INGEST_SCRIPT.exists():
        logger.warning(f"Resume ingest script not found: {RESUME_INGEST_SCRIPT}")
        return

    questions = payload.get("questions", [])
    phone = None
    file_url = None

    for q in questions:
        q_type = (q.get("type") or "").lower()
        q_id = q.get("id", "")
        q_name = (q.get("name") or "").lower()
        value = q.get("value")

        # Detect phone number
        if CAREER_HOTLINE_PHONE_FIELD and q_id == CAREER_HOTLINE_PHONE_FIELD:
            phone = str(value) if value else None
        elif not phone and q_type in ("phonenumber", "phone"):
            phone = str(value) if value else None
        elif not phone and any(kw in q_name for kw in ("phone", "mobile", "cell")):
            if value and isinstance(value, str) and any(c.isdigit() for c in str(value)):
                phone = str(value)

        # Detect file upload
        if q_type in ("fileupload", "file_upload", "file"):
            if isinstance(value, list) and value:
                first_file = value[0]
                if isinstance(first_file, dict):
                    file_url = first_file.get("url") or first_file.get("fileUrl")
                elif isinstance(first_file, str):
                    file_url = first_file
            elif isinstance(value, str) and str(value).startswith("http"):
                file_url = value

    if not phone:
        logger.warning("Resume ingestion skipped: no phone number found in submission")
        return

    if not file_url:
        logger.info(f"No file upload in submission for {phone[-4:] if phone else '???'} — skipping resume ingestion")
        return

    logger.info(f"Triggering resume ingestion for {phone[-4:]} from {file_url[:60]}...")

    try:
        result = subprocess.run(
            [
                "python3", str(RESUME_INGEST_SCRIPT),
                "--url", file_url,
                "--phone", phone,
                "--verbose", "--json"
            ],
            capture_output=True, text=True, timeout=180,
            env={**os.environ}
        )
        if result.returncode == 0:
            logger.info(f"Resume ingestion completed for {phone[-4:]}: {result.stdout[:200]}")
        else:
            logger.error(f"Resume ingestion failed for {phone[-4:]}: {result.stderr[:300]}")
    except subprocess.TimeoutExpired:
        logger.error(f"Resume ingestion timed out for {phone[-4:]}")
    except Exception as e:
        logger.error(f"Resume ingestion error for {phone[-4:]}: {e}")


def _is_career_hotline_form(form_id: str, payload: Dict[str, Any]) -> bool:
    """Check if this submission is from a career hotline intake form.

    Detection strategy (in order):
    1. Explicit form ID match from CAREER_HOTLINE_FORM_IDS env var
    2. Heuristic: form name contains career/coaching/hotline keywords
    3. Heuristic: questions contain phone + file upload fields
    """
    # Explicit match
    if form_id and form_id in CAREER_HOTLINE_FORM_IDS:
        return True

    # Name heuristic
    form_name = (payload.get("formName") or payload.get("form_name") or "").lower()
    career_keywords = ["career", "coaching", "hotline", "careerspan", "intake"]
    if form_name and any(kw in form_name for kw in career_keywords):
        return True

    # Structure heuristic: has both a phone field and a file upload field
    questions = payload.get("questions", [])
    has_phone = False
    has_file = False
    for q in questions:
        q_type = (q.get("type") or "").lower()
        q_name = (q.get("name") or "").lower()
        if q_type in ("phonenumber", "phone") or any(kw in q_name for kw in ("phone", "mobile")):
            has_phone = True
        if q_type in ("fileupload", "file_upload", "file"):
            has_file = True
    if has_phone and has_file:
        return True

    return False


def _get_events_file() -> Path:
    """Return the JSONL file path for today's events.

    Example: /home/workspace/N5/Integrations/fillout/events/2025-11-27.jsonl
    """
    today = datetime.now(timezone.utc).date()
    return EVENTS_BASE_DIR / f"{today.isoformat()}.jsonl"


def _append_event(event: Dict[str, Any]) -> None:
    """Append a single JSON event to the current day's JSONL file."""
    events_file = _get_events_file()
    line = json.dumps(event, separators=(",", ":"), ensure_ascii=False)
    with events_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


@app.post("/webhooks/fillout")
async def fillout_webhook(
    request: Request,
    x_fillout_signature: Optional[str] = Header(default=None),
) -> Dict[str, str]:
    """Receive Fillout webhook submissions and store them as JSONL events.

    Notes:
    - Signature verification is not yet implemented; `x_fillout_signature` is
      accepted so we can add verification later without breaking the interface.
    - The raw JSON payload from Fillout is stored under the `payload` key.
    - New form detection is performed and logged as separate events.
    """
    try:
        payload: Dict[str, Any] = await request.json()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}") from exc

    received_at = datetime.now(timezone.utc).isoformat()
    form_id = payload.get("formId")

    # Check for new form and log if detected
    if form_id and _check_new_form(form_id):
        form_name = payload.get("formName", payload.get("form_name", "Unknown Form"))
        new_form_event: Dict[str, Any] = {
            "source": "fillout",
            "type": "new_form_detected",
            "received_at": received_at,
            "form_id": form_id,
            "form_name": form_name,
            "payload": payload,
        }
        _append_event(new_form_event)
        
        # Trigger analysis in background thread
        thread = threading.Thread(
            target=_trigger_survey_analysis,
            args=(form_id, form_name),
            daemon=True
        )
        thread.start()
        logger.info(f"Spawned analysis thread for new form: {form_id}")

    event: Dict[str, Any] = {
        "source": "fillout",
        "type": "submission_created",  # can be extended if Fillout sends multiple event types
        "received_at": received_at,
        "headers": {
            "x_fillout_signature": x_fillout_signature,
        },
        "payload": payload,
    }

    try:
        _append_event(event)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to write event: {exc}") from exc

    # Check if this is a career hotline intake form with a resume upload
    if _is_career_hotline_form(form_id or "", payload):
        logger.info(f"Career hotline intake form detected (form: {form_id})")
        thread = threading.Thread(
            target=_trigger_resume_ingestion,
            args=(payload,),
            daemon=True
        )
        thread.start()

    return {"status": "ok"}


@app.get("/health")
async def health() -> Dict[str, str]:
    """Simple health-check endpoint for monitoring the service."""
    return {"status": "healthy"}

