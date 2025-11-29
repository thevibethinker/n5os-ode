from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Header, HTTPException, Request


app = FastAPI(title="Fillout Webhook Receiver")


# Base directory for event logs (JSONL)
BASE_DIR = Path("/home/workspace/Personal/Integrations/fillout").resolve()
EVENTS_BASE_DIR = BASE_DIR / "events"
FORM_INDEX_PATH = BASE_DIR / "form_index.json"

EVENTS_BASE_DIR.mkdir(parents=True, exist_ok=True)


def _get_events_file() -> Path:
    """Return the JSONL file path for today's events (UTC date).

    Example: /home/workspace/Personal/Integrations/fillout/events/2025-11-29.jsonl
    """
    today = datetime.now(timezone.utc).date()
    return EVENTS_BASE_DIR / f"{today.isoformat()}.jsonl"


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

    Also mirrors to a debug file and updates the form index for fast
    lookup of known forms.
    """
    events_file = _get_events_file()
    debug_file = EVENTS_BASE_DIR / "debug_from_service.jsonl"

    line = json.dumps(event, separators=(",", ":"), ensure_ascii=False)

    # Primary event log
    with events_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    # Mirror in debug file for verification
    with debug_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    # Maintain form index incrementally
    _update_form_index_from_event(event)


@app.post("/webhooks/fillout")
async def fillout_webhook(
    request: Request,
    x_fillout_signature: str | None = Header(default=None),
) -> Dict[str, str]:
    """Receive Fillout webhook submissions and store them as JSONL events.

    Notes:
    - Signature verification is not yet implemented; `x_fillout_signature` is
      accepted so we can add verification later without breaking the interface.
    - The raw JSON payload from Fillout is stored under the `payload` key.
    - A lightweight form index is maintained in form_index.json for quick
      discovery of known forms.
    """
    try:
        payload: Dict[str, Any] = await request.json()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}") from exc

    received_at = datetime.now(timezone.utc).isoformat()

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

    return {"status": "ok"}


@app.get("/health")
async def health() -> Dict[str, str]:
    """Simple health-check endpoint for monitoring the service."""
    return {"status": "healthy"}

