from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request


app = FastAPI(title="Fillout Webhook Receiver")

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


# Base directory for event logs (JSONL)
BASE_DIR = Path("/home/workspace/Personal/Integrations/fillout").resolve()
EVENTS_BASE_DIR = BASE_DIR / "events"
EVENTS_BY_FORM_DIR = EVENTS_BASE_DIR / "forms"
FORM_INDEX_PATH = BASE_DIR / "form_index.json"

EVENTS_BASE_DIR.mkdir(parents=True, exist_ok=True)
EVENTS_BY_FORM_DIR.mkdir(parents=True, exist_ok=True)

# Form-specific pipeline triggers
MARVIN_FORM_ID = "8JxXF1AVZeus"
PIPELINE_SCRIPT = Path("/home/workspace/Personal/Integrations/fillout/marvin_enrichment_pipeline.py")


def _trigger_marvin_pipeline(event: Dict[str, Any]) -> None:
    """Trigger the Marvin Ventures enrichment pipeline for qualifying submissions."""
    payload = event.get("payload", {})
    form_id = payload.get("formId")
    
    if form_id != MARVIN_FORM_ID:
        return
    
    # Check consent
    submission = payload.get("submission", {})
    questions = {q["name"]: q.get("value") for q in submission.get("questions", [])}
    consent = questions.get("Do you consent to being contacted by Careerspan to redeem your Marvin Ventures perk")
    
    if consent != "Yes":
        logger.info(f"Marvin submission without consent, skipping pipeline")
        return
    
    name = questions.get("What is your name?", "Unknown")
    company = questions.get("What is your company's name?", "Unknown")
    
    logger.info(f"Triggering Marvin pipeline for {name} at {company}")
    
    # Write event to temp file for pipeline to process
    temp_event_file = Path("/tmp/marvin_event_latest.json")
    with open(temp_event_file, "w") as f:
        json.dump(event, f)
    
    try:
        # Run pipeline script
        result = subprocess.run(
            ["python3", str(PIPELINE_SCRIPT), "--event-file", str(temp_event_file)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd="/home/workspace/Personal/Integrations/fillout"
        )
        
        if result.returncode == 0:
            logger.info(f"Marvin pipeline completed successfully")
            try:
                pipeline_result = json.loads(result.stdout)
                
                # Execute the actions
                for action in pipeline_result.get("actions_for_zo", []):
                    _execute_zo_action(action)
                    
            except json.JSONDecodeError:
                logger.warning(f"Could not parse pipeline output: {result.stdout[:500]}")
        else:
            logger.error(f"Marvin pipeline failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("Marvin pipeline timed out after 120s")
    except Exception as e:
        logger.error(f"Failed to run Marvin pipeline: {e}")


def _execute_zo_action(action: Dict[str, Any]) -> None:
    """Execute an action from the pipeline (Gmail draft, SMS, etc)."""
    action_type = action.get("action")
    params = action.get("params", {})
    
    if action_type == "create_gmail_draft":
        _create_gmail_draft(params)
    elif action_type == "send_sms":
        _send_sms(params.get("message", ""))
    else:
        logger.warning(f"Unknown action type: {action_type}")


def _create_gmail_draft(params: Dict[str, Any]) -> None:
    """Create Gmail draft via zo-cli or direct API call."""
    try:
        # Write a small Python script to create the draft using pipedream
        draft_script = f'''
import subprocess
import json

result = subprocess.run(
    ["zo", "app", "gmail", "gmail-create-draft",
     "--email", "vrijen@mycareerspan.com",
     "--to", {json.dumps(params.get("to", ""))},
     "--subject", {json.dumps(params.get("subject", ""))},
     "--body", {json.dumps(params.get("body", ""))},
     "--bodyType", "html",
     "--fromEmail", "vrijen@mycareerspan.com"],
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.stderr)
'''
        # For now, save the draft params to a queue file for manual processing
        # The webhook service doesn't have direct access to Zo's app tools
        queue_file = Path("/home/workspace/Personal/Integrations/fillout/draft_queue.jsonl")
        with open(queue_file, "a") as f:
            f.write(json.dumps({
                "type": "gmail_draft",
                "params": params,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }) + "\n")
        logger.info(f"Gmail draft queued for: {params.get('to')}")
        
    except Exception as e:
        logger.error(f"Failed to queue Gmail draft: {e}")


def _send_sms(message: str) -> None:
    """Send SMS notification via Zo's SMS endpoint."""
    try:
        # Queue the SMS for processing
        queue_file = Path("/home/workspace/Personal/Integrations/fillout/sms_queue.jsonl")
        with open(queue_file, "a") as f:
            f.write(json.dumps({
                "type": "sms",
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }) + "\n")
        logger.info(f"SMS queued: {message[:50]}...")
        
    except Exception as e:
        logger.error(f"Failed to queue SMS: {e}")


def _get_events_file() -> Path:
    """Return the JSONL file path for today's events (UTC date).

    Example: /home/workspace/Personal/Integrations/fillout/events/2025-11-29.jsonl
    """
    today = datetime.now(timezone.utc).date()
    return EVENTS_BASE_DIR / f"{today.isoformat()}.jsonl"


def _get_form_events_file(form_id: str) -> Path:
    """Return the JSONL file path for a specific form.

    Example: /home/workspace/Personal/Integrations/fillout/events/forms/8JxXF1AVZeus.jsonl
    """
    # Sanitize form_id to prevent path traversal
    safe_form_id = "".join(c for c in form_id if c.isalnum() or c in "-_")
    return EVENTS_BY_FORM_DIR / f"{safe_form_id}.jsonl"


def _load_form_index() -> Dict[str, Any]:
    if not FORM_INDEX_PATH.exists():
        return {"forms": {}}
    try:
        with FORM_INDEX_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If index is corrupted, start fresh but do not crash webhook ingestion
        return {"forms": {}}


def _save_form_index(index: Dict[str, Any]) -> None:
    tmp = FORM_INDEX_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    tmp.replace(FORM_INDEX_PATH)


def _update_form_index_from_event(event: Dict[str, Any]) -> None:
    """Update form_index.json based on a single event.

    This keeps a lightweight, incremental index of known forms and
    approximate submission counts for fast lookups.
    """
    payload = event.get("payload", {})
    form_id = payload.get("formId")
    form_name = payload.get("formName")
    received_at = event.get("received_at")

    if not form_id:
        return

    index = _load_form_index()
    forms = index.setdefault("forms", {})

    entry = forms.get(form_id, {
        "formId": form_id,
        "formName": form_name,
        "firstSeen": received_at,
        "lastSeen": received_at,
        "submissionCount": 0,
    })

    # Keep the latest known name if provided
    if form_name:
        entry["formName"] = form_name

    # Update timestamps
    if not entry.get("firstSeen"):
        entry["firstSeen"] = received_at
    entry["lastSeen"] = received_at

    # Increment count
    entry["submissionCount"] = int(entry.get("submissionCount", 0)) + 1

    forms[form_id] = entry
    index["forms"] = forms
    _save_form_index(index)


def _append_event(event: Dict[str, Any]) -> None:
    """Append a single JSON event to the current day's JSONL file.

    Also mirrors to a debug file, writes to form-specific JSONL, and updates
    the form index for fast lookup of known forms.
    """
    events_file = _get_events_file()
    debug_file = EVENTS_BASE_DIR / "debug_from_service.jsonl"

    line = json.dumps(event, separators=(",", ":"), ensure_ascii=False)

    # Primary event log (by date)
    with events_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    # Mirror in debug file for verification
    with debug_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    # Write to form-specific JSONL file
    form_id = event.get("payload", {}).get("formId")
    if form_id:
        form_events_file = _get_form_events_file(form_id)
        with form_events_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    # Maintain form index incrementally
    _update_form_index_from_event(event)


@app.post("/webhooks/fillout")
async def fillout_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_fillout_signature: str | None = Header(default=None),
) -> Dict[str, str]:
    """Receive Fillout webhook submissions and store them as JSONL events.

    Notes:
    - Signature verification is not yet implemented; `x_fillout_signature` is
      accepted so we can add verification later without breaking the interface.
    - The raw JSON payload from Fillout is stored under the `payload` key.
    - A lightweight form index is maintained in form_index.json for quick
      discovery of known forms.
    - Form-specific pipelines are triggered in the background for configured forms.
    """
    try:
        payload: Dict[str, Any] = await request.json()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}") from exc

    received_at = datetime.now(timezone.utc).isoformat()

    event: Dict[str, Any] = {
        "source": "fillout",
        "type": "submission_created",
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

    # Trigger form-specific pipelines in background (non-blocking)
    background_tasks.add_task(_trigger_marvin_pipeline, event)

    return {"status": "ok"}


@app.get("/health")
async def health() -> Dict[str, str]:
    """Simple health-check endpoint for monitoring the service."""
    return {"status": "healthy"}




