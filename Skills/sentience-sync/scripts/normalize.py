#!/usr/bin/env python3
"""
Normalize Sentience memories into the canonical CRM event schema.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from email.utils import getaddresses
from hashlib import sha256
from typing import Any

ZO_CONTENT_MARKERS = [
    "[Zo Journal:",
    "[Zo Learning:",
    "[V's Framework",
    "[External Insight",
    "[Communication Style:",
    "[Building Principle:",
    "[Zo's Self-Model:",
]

SOURCE_TYPE_MAP = {
    "Sentience Desktop App": "desktop",
    "Gmail": "gmail",
    "Google Calendar": "calendar",
}

PUBLIC_EMAIL_DOMAINS = {
    "gmail.com",
    "googlemail.com",
    "icloud.com",
    "me.com",
    "mac.com",
    "outlook.com",
    "hotmail.com",
    "live.com",
    "msn.com",
    "yahoo.com",
    "ymail.com",
    "proton.me",
    "protonmail.com",
    "pm.me",
    "example.com",
    "example.net",
    "example.org",
}

HEADER_KEYS = {"from", "to", "cc", "bcc", "subject", "date"}
URL_RE = re.compile(r"https?://[^\s>]+", re.I)


def is_zo_originated(memory: dict[str, Any]) -> bool:
    if memory.get("source") == "api":
        return True
    content = memory.get("content") or ""
    if isinstance(content, (dict, list)):
        content = json.dumps(content, sort_keys=True)
    text = str(content)
    return any(marker in text for marker in ZO_CONTENT_MARKERS)


def normalize(memory: dict[str, Any]) -> dict[str, Any] | None:
    if is_zo_originated(memory):
        return None

    source_label = _clean_text(memory.get("source"))
    source_type = SOURCE_TYPE_MAP.get(source_label)
    if not source_type:
        return None

    source_memory_id = _clean_text(memory.get("id") or memory.get("memory_id"))
    raw_content = memory.get("content")

    if source_type == "desktop":
        event = _normalize_desktop(raw_content)
    elif source_type == "gmail":
        event = _normalize_gmail(raw_content)
    else:
        event = _normalize_calendar(raw_content)

    if event is None:
        return None

    return {
        "event_id": _build_event_id(source_type, source_memory_id),
        "source_type": source_type,
        "source_memory_id": source_memory_id,
        "timestamp": _normalize_timestamp(memory.get("timestamp")),
        "app": event["app"],
        "window_title": event["window_title"],
        "title": event["title"],
        "summary": event["summary"],
        "category": event["category"],
        "significance": _clamp_significance(event["significance"]),
        "entities": event["entities"],
        "actions": event["actions"],
        "sentiment": event["sentiment"],
        "raw_content_hash": _content_hash(raw_content),
    }


def normalize_many(memories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events = []
    for memory in memories:
        event = normalize(memory)
        if event is not None:
            events.append(event)
    return events


def _normalize_desktop(raw_content: Any) -> dict[str, Any] | None:
    content = _parse_json_object(raw_content)
    if content is None:
        return None

    facts = content.get("facts") if isinstance(content.get("facts"), dict) else {}
    app = _nullable_text(content.get("appName"))
    window_title = _nullable_text(content.get("windowTitle"))
    title = _nullable_text(content.get("title")) or window_title or "Desktop activity"
    summary = _nullable_text(content.get("summary")) or title
    urls = _ordered_strings(_listify(facts.get("urls")))

    return {
        "app": app,
        "window_title": window_title,
        "title": title,
        "summary": _truncate(summary, 500),
        "category": _nullable_text(content.get("category")),
        "significance": content.get("significance_score", content.get("significance", 0.0)),
        "entities": {
            "people": _ordered_strings(_listify(facts.get("people"))),
            "companies": _ordered_strings(_listify(facts.get("companies"))),
            "tools": _ordered_strings(_listify(facts.get("tools"))),
            "urls": urls,
        },
        "actions": _normalize_actions(facts.get("actions")),
        "sentiment": _extract_sentiment(content.get("sentiment")),
    }


def _normalize_gmail(raw_content: Any) -> dict[str, Any]:
    content = "" if raw_content is None else str(raw_content).strip()
    headers = _extract_headers(content)
    sender = _first_address(headers.get("from"))
    recipients = _parse_addresses(headers.get("to")) + _parse_addresses(headers.get("cc"))
    subject = _nullable_text(headers.get("subject")) or _first_nonempty_line(content) or "Email activity"
    body_preview = _extract_gmail_body_preview(content)

    people = []
    for address in [sender, *recipients]:
        name = _nullable_text(address.get("name")) or _nullable_text(address.get("email"))
        if name:
            people.append(name)

    companies = []
    for address in [sender, *recipients]:
        domain = _domain_from_email(address.get("email"))
        if domain and domain not in PUBLIC_EMAIL_DOMAINS:
            companies.append(domain)

    summary = subject if not body_preview else f"{subject}: {body_preview}"
    action_subject = _nullable_text(sender.get("name")) or _nullable_text(sender.get("email")) or "email_sender"

    return {
        "app": None,
        "window_title": None,
        "title": subject,
        "summary": _truncate(summary, 500),
        "category": None,
        "significance": _infer_email_significance(content),
        "entities": {
            "people": _ordered_strings(people),
            "companies": _ordered_strings(companies),
            "tools": ["Gmail"],
            "urls": _ordered_strings(URL_RE.findall(content)),
        },
        "actions": [
            {
                "subject": action_subject,
                "verb": "emailed",
                "object": subject,
            }
        ],
        "sentiment": None,
    }


def _normalize_calendar(raw_content: Any) -> dict[str, Any]:
    content = "" if raw_content is None else str(raw_content).strip()
    attendees = _parse_calendar_attendees(content)
    title = _calendar_title(content)

    people = []
    companies = []
    for attendee in attendees:
        name = _nullable_text(attendee.get("name")) or _nullable_text(attendee.get("email"))
        if name:
            people.append(name)
        domain = _domain_from_email(attendee.get("email"))
        if domain and domain not in PUBLIC_EMAIL_DOMAINS:
            companies.append(domain)

    return {
        "app": None,
        "window_title": None,
        "title": title,
        "summary": _truncate(content or title, 500),
        "category": None,
        "significance": 0.6 if attendees else 0.45,
        "entities": {
            "people": _ordered_strings(people),
            "companies": _ordered_strings(companies),
            "tools": ["Google Calendar"],
            "urls": _ordered_strings(URL_RE.findall(content)),
        },
        "actions": [
            {
                "subject": "calendar",
                "verb": "scheduled",
                "object": title,
            }
        ],
        "sentiment": None,
    }


def _build_event_id(source_type: str, source_memory_id: str) -> str:
    return sha256(f"{source_type}|{source_memory_id}".encode("utf-8")).hexdigest()


def _content_hash(content: Any) -> str:
    if isinstance(content, (dict, list)):
        payload = json.dumps(content, sort_keys=True, separators=(",", ":"))
    else:
        payload = "" if content is None else str(content)
    return sha256(payload.encode("utf-8")).hexdigest()


def _parse_json_object(raw_content: Any) -> dict[str, Any] | None:
    if isinstance(raw_content, dict):
        return raw_content
    if isinstance(raw_content, str):
        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, dict):
            return parsed
    return None


def _extract_headers(content: str) -> dict[str, str]:
    headers: dict[str, str] = {}
    for line in content.splitlines()[:40]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        if key in HEADER_KEYS and key not in headers:
            headers[key] = value.strip()
    return headers


def _extract_gmail_body_preview(content: str) -> str:
    lines = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("--- Message "):
            continue
        if ":" in line:
            key = line.split(":", 1)[0].strip().lower()
            if key in HEADER_KEYS:
                continue
        lines.append(line)
    if not lines:
        return ""
    preview = " ".join(lines[1:]) if len(lines) > 1 else lines[0]
    return _truncate(preview, 320)


def _parse_calendar_attendees(content: str) -> list[dict[str, str]]:
    attendees: list[dict[str, str]] = []
    for line in content.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip().lower() in {"attendees", "guests", "invitees"}:
            attendees.extend(_parse_addresses(value.strip()))
    return attendees


def _calendar_title(content: str) -> str:
    first_line = _first_nonempty_line(content)
    if first_line.lower().startswith("calendar event:"):
        first_line = first_line.split(":", 1)[1].strip()
    if " - " in first_line:
        first_line = first_line.split(" - ", 1)[0].strip()
    return first_line or "Calendar event"


def _normalize_actions(value: Any) -> list[dict[str, str]]:
    actions = []
    for action in _listify(value):
        normalized = _normalize_action(action)
        if normalized:
            actions.append(normalized)
    return actions


def _normalize_action(action: Any) -> dict[str, str] | None:
    if isinstance(action, dict):
        subject = _clean_text(action.get("subject"))
        verb = _clean_text(action.get("verb"))
        obj = _clean_text(action.get("object"))
        if subject or verb or obj:
            return {"subject": subject, "verb": verb, "object": obj}
        return None
    if isinstance(action, str) and action.strip():
        return {"subject": "", "verb": "described", "object": _clean_text(action)}
    return None


def _parse_addresses(raw: str | None) -> list[dict[str, str]]:
    if not raw:
        return []
    results = []
    for name, email in getaddresses([raw]):
        results.append(
            {
                "name": _clean_text(name),
                "email": _clean_text(email).lower(),
            }
        )
    return results


def _first_address(raw: str | None) -> dict[str, str]:
    addresses = _parse_addresses(raw)
    if addresses:
        return addresses[0]
    return {"name": "", "email": ""}


def _domain_from_email(email: str | None) -> str | None:
    text = _nullable_text(email)
    if not text or "@" not in text:
        return None
    return text.rsplit("@", 1)[1].lower()


def _extract_sentiment(value: Any) -> str | None:
    if isinstance(value, dict):
        return _nullable_text(value.get("overall"))
    return _nullable_text(value)


def _infer_email_significance(content: str) -> float:
    count = _extract_message_count(content) or 1
    significance = 0.45 + min(0.25, (count - 1) * 0.05)
    if re.search(r"\b(intro|introduction|follow[- ]?up|meeting|schedule|scheduled|connect)\b", content, re.I):
        significance += 0.15
    return min(significance, 1.0)


def _extract_message_count(content: str) -> int | None:
    match = re.search(r"\((\d+) messages?\)", content)
    if match:
        return int(match.group(1))
    return None


def _normalize_timestamp(value: Any) -> str:
    if not value:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    text = str(value).strip()
    if text.endswith("+00:00Z"):
        text = text[:-1]
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _ordered_strings(values: list[Any]) -> list[str]:
    ordered = []
    seen = set()
    for value in values:
        text = _clean_text(value)
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(text)
    return ordered


def _first_nonempty_line(content: str) -> str:
    for line in content.splitlines():
        text = line.strip()
        if text:
            return text
    return ""


def _truncate(value: str, max_len: int) -> str:
    text = _clean_text(value)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "..."


def _nullable_text(value: Any) -> str | None:
    text = _clean_text(value)
    return text or None


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _clamp_significance(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    if numeric < 0:
        return 0.0
    if numeric > 1:
        return 1.0
    return numeric
