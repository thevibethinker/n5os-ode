from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    webhook_secret_configured: bool
    insecure_mode: bool


class WebhookAck(BaseModel):
    status: str
    event_id: str | None = None
    decision: str | None = None
    queue_file: str | None = None
    reason: str | None = None


class SenderIdentity(BaseModel):
    name: str | None = None
    email: str | None = None


class MessageEnvelope(BaseModel):
    inbox_id: str | None = None
    thread_id: str | None = None
    message_id: str | None = None
    subject: str | None = None
    preview: str | None = None
    text: str | None = None
    html: str | None = None
    from_: list[SenderIdentity] | None = Field(default=None, alias="from")
    to: list[SenderIdentity] | None = None
    created_at: str | None = None


@dataclass(frozen=True)
class SecurityAssessment:
    risk_level: str
    decision: str
    sender_tier: str
    confidence: float
    flags: list[str]
    rationale: str


@dataclass(frozen=True)
class RoutingDecision:
    inbox_role: str
    inbox_key: str
    route_queue: str
    event_id: str
    message_id: str | None
    sender_email: str | None
    sender_domain: str | None
    subject: str
    timestamp: datetime
    security: SecurityAssessment
    payload: dict[str, Any]
