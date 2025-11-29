from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Header, HTTPException, Request


app = FastAPI(title="Fillout Webhook Receiver")


# Base directory for event logs (JSONL)
EVENTS_BASE_DIR = Path("/home/workspace/N5/Integrations/fillout/events").resolve()
EVENTS_BASE_DIR.mkdir(parents=True, exist_ok=True)


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
    x_fillout_signature: str | None = Header(default=None),
) -> Dict[str, str]:
    """Receive Fillout webhook submissions and store them as JSONL events.

    Notes:
    - Signature verification is not yet implemented; `x_fillout_signature` is
      accepted so we can add verification later without breaking the interface.
    - The raw JSON payload from Fillout is stored under the `payload` key.
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

