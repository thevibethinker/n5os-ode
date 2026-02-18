from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from svix.webhooks import Webhook, WebhookVerificationError

from .config import Config, safe_json
from .models import HealthResponse, RoutingDecision, SecurityAssessment, WebhookAck
from .security import assess_message
from .storage import append_audit, init_db, is_duplicate, record_event, write_queue_file


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("agentmail_webhook")

cfg = Config()
CONFIG_ERROR: str | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global CONFIG_ERROR
    init_db(cfg.data_db_path)

    ok, err = Config.validate()
    if not ok:
        CONFIG_ERROR = err or "Unknown configuration error"
        logger.error("Config validation failed: %s", CONFIG_ERROR)
    else:
        CONFIG_ERROR = None
        logger.info("AgentMail webhook receiver ready on %s:%s", cfg.host, cfg.port)
    yield


app = FastAPI(
    title="AgentMail Webhook Receiver",
    description="Receives AgentMail events for Careerspan, Hotline, and N5 OS inboxes",
    version="1.0.0",
    lifespan=lifespan,
)


def _verify_svix(headers: dict[str, str], raw_body: bytes) -> dict[str, Any]:
    if not cfg.webhook_secret:
        if cfg.allow_insecure:
            return json.loads(raw_body.decode("utf-8"))
        raise HTTPException(status_code=500, detail="Webhook secret is not configured")

    try:
        webhook = Webhook(cfg.webhook_secret)
        return webhook.verify(raw_body, headers)
    except WebhookVerificationError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid webhook signature: {exc}") from exc


def _extract_sender_email(message: dict[str, Any]) -> str | None:
    from_block = message.get("from")
    if isinstance(from_block, list) and from_block:
        first = from_block[0]
        if isinstance(first, dict):
            email = first.get("email")
            if isinstance(email, str):
                return email.strip().lower()
    return None


def _extract_sender_domain(sender_email: str | None) -> str | None:
    if not sender_email or "@" not in sender_email:
        return None
    return sender_email.rsplit("@", 1)[-1].lower()


def _match_inbox_role(message: dict[str, Any]) -> tuple[str | None, str | None]:
    role_map = Config.inbox_role_map()

    candidate_keys: list[str] = []

    inbox_id = message.get("inbox_id")
    if isinstance(inbox_id, str) and inbox_id.strip():
        candidate_keys.append(inbox_id.strip().lower())

    to_block = message.get("to")
    if isinstance(to_block, list):
        for item in to_block:
            if isinstance(item, dict):
                email = item.get("email")
                if isinstance(email, str) and email.strip():
                    candidate_keys.append(email.strip().lower())

    for key in candidate_keys:
        role = role_map.get(key)
        if role:
            return role, key

    return None, None


def _route_queue(assessment: SecurityAssessment) -> str:
    if assessment.decision == "quarantine":
        return "quarantine"
    if assessment.decision == "review_required":
        return "review"
    return "auto"


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="agentmail-webhook",
        timestamp=datetime.now(UTC).isoformat(),
        webhook_secret_configured=bool(cfg.webhook_secret),
        insecure_mode=cfg.allow_insecure,
    )


@app.post("/webhook/agentmail", response_model=WebhookAck)
async def receive_agentmail_webhook(
    request: Request,
    svix_id: str | None = Header(default=None, alias="svix-id"),
    svix_timestamp: str | None = Header(default=None, alias="svix-timestamp"),
    svix_signature: str | None = Header(default=None, alias="svix-signature"),
) -> WebhookAck:
    if CONFIG_ERROR:
        raise HTTPException(status_code=500, detail=CONFIG_ERROR)

    raw_body = await request.body()
    if len(raw_body) > cfg.max_request_size_bytes:
        raise HTTPException(status_code=413, detail="Payload too large")

    headers = {
        "svix-id": svix_id or "",
        "svix-timestamp": svix_timestamp or "",
        "svix-signature": svix_signature or "",
    }

    if not cfg.allow_insecure and (not svix_id or not svix_timestamp or not svix_signature):
        raise HTTPException(status_code=400, detail="Missing required Svix headers")

    verified_payload = _verify_svix(headers, raw_body)

    if is_duplicate(cfg.data_db_path, svix_id):
        return WebhookAck(status="duplicate", reason="Already processed")

    event_type = verified_payload.get("event_type")
    event_id = str(verified_payload.get("event_id") or "")

    if event_type != "message.received":
        append_audit(
            cfg,
            {
                "ts": datetime.now(UTC).isoformat(),
                "kind": "ignored_event",
                "svix_id": svix_id,
                "event_id": event_id,
                "event_type": event_type,
            },
        )
        return WebhookAck(status="ignored", event_id=event_id, reason="Unsupported event type")

    message = verified_payload.get("message")
    if not isinstance(message, dict):
        raise HTTPException(status_code=400, detail="Missing message payload")

    inbox_role, inbox_key = _match_inbox_role(message)
    if not inbox_role or not inbox_key:
        append_audit(
            cfg,
            {
                "ts": datetime.now(UTC).isoformat(),
                "kind": "ignored_inbox",
                "svix_id": svix_id,
                "event_id": event_id,
                "event_type": event_type,
                "message_inbox_id": message.get("inbox_id"),
            },
        )
        return WebhookAck(status="ignored", event_id=event_id, reason="Inbox not configured")

    sender_email = _extract_sender_email(message)
    sender_domain = _extract_sender_domain(sender_email)

    subject = str(message.get("subject") or "")
    body_text = str(message.get("text") or message.get("preview") or "")

    security = assess_message(
        subject=subject,
        body_text=body_text,
        sender_email=sender_email,
        trusted_senders=Config.trusted_senders(),
        trusted_domains=Config.trusted_sender_domains(),
        unknown_senders_review=cfg.unknown_senders_review,
    )

    route_queue = _route_queue(security)

    decision = RoutingDecision(
        inbox_role=inbox_role,
        inbox_key=inbox_key,
        route_queue=route_queue,
        event_id=event_id,
        message_id=message.get("message_id"),
        sender_email=sender_email,
        sender_domain=sender_domain,
        subject=subject,
        timestamp=datetime.now(UTC),
        security=security,
        payload=verified_payload,
    )

    queue_file = write_queue_file(cfg, decision)
    record_event(cfg.data_db_path, svix_id=svix_id, event_type=event_type, decision=decision)

    append_audit(
        cfg,
        {
            "ts": datetime.now(UTC).isoformat(),
            "kind": "received",
            "svix_id": svix_id,
            "event_id": event_id,
            "event_type": event_type,
            "inbox_role": inbox_role,
            "inbox_key": inbox_key,
            "route_queue": route_queue,
            "security": {
                "risk_level": security.risk_level,
                "decision": security.decision,
                "sender_tier": security.sender_tier,
                "confidence": security.confidence,
                "flags": security.flags,
            },
            "sender_email": sender_email,
            "sender_domain": sender_domain,
            "subject": subject,
            "queue_file": str(queue_file),
        },
    )

    logger.info(
        "Accepted AgentMail event=%s route=%s inbox=%s risk=%s flags=%s",
        event_id,
        route_queue,
        inbox_role,
        security.risk_level,
        safe_json(security.flags),
    )

    return WebhookAck(
        status="accepted",
        event_id=event_id,
        decision=route_queue,
        queue_file=str(queue_file),
    )


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "service": "agentmail-webhook",
        "status": "running",
        "webhook_path": "/webhook/agentmail",
        "health_path": "/health",
        "configured_inboxes": Config.inbox_role_map(),
    }
