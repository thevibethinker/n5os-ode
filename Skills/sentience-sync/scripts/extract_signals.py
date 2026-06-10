#!/usr/bin/env python3
"""
Relationship signal extractors for Sentience CRM enrichment.

Takes normalized events (output of normalize.py) and extracts typed
relationship signals: new_contact, renewed_contact, introduction,
follow_up_commitment, company_intelligence, meeting_scheduled.

Each signal includes provenance (source_event_ids) and structured fields
ready for identity resolution (W1.2) and projection writing (W3.1).

Extraction is conservative: better to miss a signal than fabricate one.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from typing import Any

SELF_NAME_ALIASES = {
    "primary user",
    "primary",
    "primary user",
    "primary user",
}
SELF_SINGLE_TOKEN = {"v"}

FAMILY_NAMES = {
    "family member",
    "family member",
    "dr. family member",
    "dr family member",
}

OWN_COMPANIES = {
    "company-project",
    "company-project intelligence",
    "company-project labs",
    "work-project",
}

INTRO_VERBS = re.compile(
    r"\b(introduc\w+ \w+ to|putting .{1,30} in touch|intro: )", re.I
)
INTRO_ACTIONS = re.compile(
    r"\b(introduc\w+ \w+ to|intro:|intro \w+ to)\b", re.I
)

INTRO_SELF_PATTERNS = re.compile(
    r"\b(introducing (?:myself|me|himself|herself))\b", re.I
)

FOLLOW_UP_PATTERNS = re.compile(
    r"\b(need to follow[- ]?up|should follow[- ]?up|promised to (?:send|follow|get back|reach)|"
    r"committed to (?:send|follow|reach)|circle back with|loop back with|"
    r"need to reach out to|need to get back to|"
    r"touch base with .+|check in with .+)\b",
    re.I,
)

MEETING_SCHEDULED_PATTERNS = re.compile(
    r"\b(schedul(?:e|ed|ing) (?:a )?(?:call|meeting|sync)|calendar invite|"
    r"set up a (?:call|meeting)|booked a (?:call|meeting)|"
    r"meeting (?:set|booked|confirmed))\b",
    re.I,
)

MEETING_SCHEDULED_ACTION_PATTERNS = re.compile(
    r"\b(schedul|google meet link|zoom link|teams link|meeting link|"
    r"calendar invite)\b",
    re.I,
)

RENEWED_PATTERNS = re.compile(
    r"\b(reconnect(?:ing)?|re-?engag|catching up with|haven't (?:spoken|talked|heard)|"
    r"long time|back in touch|reaching out again|following up after a (?:long|while)|"
    r"been a while since)\b",
    re.I,
)

NEW_CONTACT_STRONG = re.compile(
    r"\b(just met|first (?:time )?meeting|met .{1,30} at|nice to meet|"
    r"great meeting|new contact|logging .{1,40} for CRM)\b",
    re.I,
)

NEW_CONTACT_CONFERENCE = re.compile(
    r"\b(humanx|ventureconnect|conference|roundtable)\b",
    re.I,
)

MEETING_ACTION_VERBS = {"meeting", "met", "introducing", "connecting"}

COMPANY_INTEL_PATTERNS = re.compile(
    r"\b(strateg(?:y|ic)|fundrais|funding round|raised (?:a )?\$|series [a-z]|seed round|"
    r"acquisition|acquired by|pivot(?:ing|ed)|partnership (?:with|deal)|"
    r"IPO|valuation|MOU|joint venture|"
    r"data licens(?:e|ing)|medical data licens)\b",
    re.I,
)

CHAT_APPS = {"whatsapp", "\u200ewhatsapp", "messages", "imessage", "telegram", "signal", "slack"}

NOISE_VERBS = {"reviewing", "browsing", "scrolling", "viewing", "reading", "looking"}

PASSIVE_ACTION_OBJECTS = re.compile(
    r"\b(WhatsApp chats|inbox|email list|notification|lock screen|"
    r"chat entries|project task entries|fixes and their statuses)\b",
    re.I,
)

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)


@dataclass(slots=True)
class RelationshipSignal:
    signal_type: str
    source_event_ids: list[str]
    timestamp: str
    extracted_entities: dict[str, list[str]]
    context: str
    details: dict[str, Any]
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _is_self(name: str) -> bool:
    n = name.strip().lower()
    if n in SELF_NAME_ALIASES:
        return True
    if n in SELF_SINGLE_TOKEN:
        return True
    return False


def _is_family(name: str) -> bool:
    return name.strip().lower() in FAMILY_NAMES


def _person_label(person: str | dict[str, Any]) -> str:
    if isinstance(person, dict):
        return str(person.get("name") or person.get("full_name") or person.get("email") or "").strip()
    return str(person or "").strip()


def _external_people(entities: dict[str, Any]) -> list[str | dict[str, Any]]:
    people: list[str | dict[str, Any]] = []
    for person in entities.get("people", []):
        if isinstance(person, dict):
            name = str(person.get("name") or person.get("full_name") or "").strip()
            if name and not _is_self(name) and not _is_family(name):
                people.append(person)
            continue
        if isinstance(person, str) and person.strip() and not _is_self(person) and not _is_family(person):
            people.append(person)
    return people


def _all_text(event: dict[str, Any]) -> str:
    parts = [
        event.get("title") or "",
        event.get("summary") or "",
    ]
    for action in event.get("actions", []):
        if isinstance(action, dict):
            parts.append(action.get("object") or "")
            parts.append(action.get("verb") or "")
    return " ".join(parts)


def _action_verbs(event: dict[str, Any]) -> list[str]:
    verbs = []
    for action in event.get("actions", []):
        if isinstance(action, dict):
            v = (action.get("verb") or "").strip().lower()
            if v:
                verbs.append(v)
    return verbs


def _action_objects(event: dict[str, Any]) -> list[str]:
    objects = []
    for action in event.get("actions", []):
        if isinstance(action, dict):
            o = (action.get("object") or "").strip()
            if o:
                objects.append(o)
    return objects


def _has_active_verb(event: dict[str, Any]) -> bool:
    active = {
        "drafting",
        "sending",
        "composing",
        "writing",
        "meeting",
        "scheduling",
        "introducing",
        "connecting",
        "discussing",
        "calling",
        "messaging",
        "replying",
        "responding",
        "forwarding",
        "sharing",
        "planning",
        "building",
        "having",
        "emailing",
        "emailed",
    }
    verbs = _action_verbs(event)
    return any(v in active for v in verbs)


def _has_meeting_verb(event: dict[str, Any]) -> bool:
    verbs = set(_action_verbs(event))
    return bool(verbs & MEETING_ACTION_VERBS)


def _is_chat_app(event: dict[str, Any]) -> bool:
    app = (event.get("app") or "").strip().lower()
    return app in CHAT_APPS


def _is_passive_browsing(event: dict[str, Any]) -> bool:
    verbs = set(_action_verbs(event))
    if not verbs:
        return True
    if verbs <= NOISE_VERBS:
        action_objs = " ".join(_action_objects(event))
        if PASSIVE_ACTION_OBJECTS.search(action_objs):
            return True
        if not _has_active_verb(event):
            return True
    return False


def _truncate(text: str, max_len: int = 300) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _primary_person_entity(event: dict[str, Any], person_name: str | dict[str, Any]) -> str | dict[str, str]:
    label = _person_label(person_name)
    text = _all_text(event)
    email_match = EMAIL_RE.search(text)
    if email_match:
        return {
            "name": label,
            "email": email_match.group(0).lower(),
        }
    return label


def extract_new_contact(event: dict[str, Any]) -> list[RelationshipSignal]:
    if _is_passive_browsing(event):
        return []

    text = _all_text(event)
    people = _external_people(event.get("entities", {}))
    companies = event.get("entities", {}).get("companies", [])

    if not people:
        return []

    has_strong_signal = bool(NEW_CONTACT_STRONG.search(text))
    has_conference_context = bool(NEW_CONTACT_CONFERENCE.search(text))
    has_meeting_verb = _has_meeting_verb(event)

    if not (has_strong_signal or (has_conference_context and has_meeting_verb)):
        return []

    primary_person = people[0]
    company = ""
    for c in companies:
        if isinstance(c, str) and c.strip() and c.strip().lower() not in OWN_COMPANIES:
            company = c
            break

    return [
        RelationshipSignal(
            signal_type="new_contact",
            source_event_ids=[event.get("event_id") or event.get("id", "")],
            timestamp=event.get("timestamp", ""),
            extracted_entities={
                "people": [_primary_person_entity(event, primary_person)],
                "companies": [company] if company else [],
            },
            context=_truncate(event.get("summary") or event.get("title", "")),
            details={
                "person_name": primary_person,
                "company": company,
                "source_channel": event.get("source_type") or event.get("app", ""),
                "other_people_mentioned": people[1:] if len(people) > 1 else [],
            },
            confidence=0.75 if has_strong_signal else 0.6,
        )
    ]


def extract_renewed_contact(event: dict[str, Any]) -> list[RelationshipSignal]:
    if _is_passive_browsing(event):
        return []

    text = _all_text(event)
    people = _external_people(event.get("entities", {}))

    if not people:
        return []

    if not RENEWED_PATTERNS.search(text):
        return []

    if not _has_active_verb(event):
        return []

    primary_person = people[0]
    return [
        RelationshipSignal(
            signal_type="renewed_contact",
            source_event_ids=[event.get("event_id") or event.get("id", "")],
            timestamp=event.get("timestamp", ""),
            extracted_entities={"people": [_primary_person_entity(event, primary_person)], "companies": []},
            context=_truncate(event.get("summary") or event.get("title", "")),
            details={
                "person_name": primary_person,
                "last_known_interaction": None,
                "context": _truncate(text, 200),
            },
            confidence=0.65,
        )
    ]


def extract_introduction(event: dict[str, Any]) -> list[RelationshipSignal]:
    if _is_passive_browsing(event):
        return []

    text = _all_text(event)
    people = _external_people(event.get("entities", {}))

    if len(people) < 2:
        return []

    if INTRO_SELF_PATTERNS.search(text):
        return []

    has_intro_in_text = bool(INTRO_VERBS.search(text))
    has_intro_action = any(
        INTRO_ACTIONS.search(a.get("object", ""))
        for a in event.get("actions", [])
        if isinstance(a, dict)
    )

    if not (has_intro_in_text or has_intro_action):
        return []

    return [
        RelationshipSignal(
            signal_type="introduction",
            source_event_ids=[event.get("event_id") or event.get("id", "")],
            timestamp=event.get("timestamp", ""),
            extracted_entities={
                "people": people,
                "companies": event.get("entities", {}).get("companies", []),
            },
            context=_truncate(event.get("summary") or event.get("title", "")),
            details={
                "introducer": "V",
                "introduced_parties": people,
                "context": _truncate(text, 200),
            },
            confidence=0.75 if has_intro_action else 0.6,
        )
    ]


def extract_follow_up_commitment(event: dict[str, Any]) -> list[RelationshipSignal]:
    if _is_passive_browsing(event):
        return []

    text = _all_text(event)
    people = _external_people(event.get("entities", {}))

    match = FOLLOW_UP_PATTERNS.search(text)
    if not match:
        return []

    if not people:
        return []

    if not _has_active_verb(event):
        return []

    commitment_text = match.group(0)
    sentence_start = max(0, match.start() - 60)
    sentence_end = min(len(text), match.end() + 60)
    commitment_context = text[sentence_start:sentence_end].strip()

    deadline_match = re.search(
        r"\b(today|tomorrow|this week|next week|monday|tuesday|wednesday|"
        r"thursday|friday|saturday|sunday|by \w+|before \w+|end of (?:day|week|month))\b",
        text,
        re.I,
    )
    implied_deadline = deadline_match.group(0) if deadline_match else None

    primary_person = people[0]
    return [
        RelationshipSignal(
            signal_type="follow_up_commitment",
            source_event_ids=[event.get("event_id") or event.get("id", "")],
            timestamp=event.get("timestamp", ""),
            extracted_entities={
                "people": [_primary_person_entity(event, primary_person)],
                "companies": event.get("entities", {}).get("companies", []),
            },
            context=_truncate(event.get("summary") or event.get("title", "")),
            details={
                "person_name": primary_person,
                "commitment_text": commitment_context,
                "implied_deadline": implied_deadline,
            },
            confidence=0.7,
        )
    ]


def extract_company_intelligence(event: dict[str, Any]) -> list[RelationshipSignal]:
    text = _all_text(event)
    companies = [
        c
        for c in event.get("entities", {}).get("companies", [])
        if isinstance(c, str) and c.strip() and c.strip().lower() not in OWN_COMPANIES
    ]

    if not companies:
        return []

    match = COMPANY_INTEL_PATTERNS.search(text)
    if not match:
        return []

    verbs = _action_verbs(event)
    only_passive = all(v in NOISE_VERBS for v in verbs) if verbs else True

    if only_passive and event.get("significance", 0) < 0.65:
        return []

    if _is_chat_app(event) and only_passive:
        return []

    if _is_chat_app(event) and event.get("significance", 0) < 0.6:
        return []

    intel_keyword = match.group(0).lower()
    if any(k in intel_keyword for k in ("strateg", "fundrais", "funding", "raised", "series", "seed")):
        intel_type = "funding_strategy"
    elif any(k in intel_keyword for k in ("acqui", "mou", "joint", "partnership")):
        intel_type = "partnership_deal"
    elif any(k in intel_keyword for k in ("data", "licens", "medical", "hospital")):
        intel_type = "data_operations"
    elif any(k in intel_keyword for k in ("pivot", "restructur", "layoff")):
        intel_type = "organizational_change"
    elif any(k in intel_keyword for k in ("launch", "ipo", "market")):
        intel_type = "market_activity"
    else:
        intel_type = "general"

    primary_company = companies[0]
    return [
        RelationshipSignal(
            signal_type="company_intelligence",
            source_event_ids=[event.get("event_id") or event.get("id", "")],
            timestamp=event.get("timestamp", ""),
            extracted_entities={
                "people": _external_people(event.get("entities", {})),
                "companies": [primary_company],
            },
            context=_truncate(event.get("summary") or event.get("title", "")),
            details={
                "company_name": primary_company,
                "intelligence_type": intel_type,
                "detail": _truncate(text, 200),
                "other_companies": companies[1:] if len(companies) > 1 else [],
            },
            confidence=0.6 if only_passive else 0.75,
        )
    ]


def extract_meeting_scheduled(event: dict[str, Any]) -> list[RelationshipSignal]:
    text = _all_text(event)
    people = _external_people(event.get("entities", {}))
    source_type = event.get("source_type", "")

    is_calendar = source_type == "calendar"

    if is_calendar and people:
        date_if_known = event.get("timestamp", "")
        return [
            RelationshipSignal(
                signal_type="meeting_scheduled",
                source_event_ids=[event.get("event_id") or event.get("id", "")],
                timestamp=event.get("timestamp", ""),
                extracted_entities={
                    "people": [_primary_person_entity(event, people[0]), *people[1:]] if people else people,
                    "companies": event.get("entities", {}).get("companies", []),
                },
                context=_truncate(event.get("summary") or event.get("title", "")),
                details={
                    "person_name": people[0] if people else None,
                    "all_attendees": people,
                    "meeting_context": event.get("title", ""),
                    "date_if_known": date_if_known,
                },
                confidence=0.85,
            )
        ]

    if _is_passive_browsing(event):
        return []

    if not people:
        return []

    has_scheduling_action = any(
        MEETING_SCHEDULED_ACTION_PATTERNS.search(
            (a.get("verb") or "") + " " + (a.get("object") or "")
        )
        for a in event.get("actions", [])
        if isinstance(a, dict)
    )

    has_scheduling_text = bool(MEETING_SCHEDULED_PATTERNS.search(text))

    if not has_scheduling_action and not has_scheduling_text:
        return []

    if not has_scheduling_action and not _has_active_verb(event):
        return []

    date_match = re.search(
        r"\b(\d{4}-\d{2}-\d{2}|today|tomorrow|monday|tuesday|wednesday|"
        r"thursday|friday|saturday|sunday)\b",
        text,
        re.I,
    )
    date_if_known = date_match.group(0) if date_match else None

    return [
        RelationshipSignal(
            signal_type="meeting_scheduled",
            source_event_ids=[event.get("event_id") or event.get("id", "")],
            timestamp=event.get("timestamp", ""),
            extracted_entities={
                "people": [_primary_person_entity(event, people[0]), *people[1:]] if people else people,
                "companies": event.get("entities", {}).get("companies", []),
            },
            context=_truncate(event.get("summary") or event.get("title", "")),
            details={
                "person_name": people[0] if people else None,
                "all_attendees": people,
                "meeting_context": event.get("title", ""),
                "date_if_known": date_if_known,
            },
            confidence=0.7 if has_scheduling_action else 0.55,
        )
    ]


ALL_EXTRACTORS = [
    extract_new_contact,
    extract_renewed_contact,
    extract_introduction,
    extract_follow_up_commitment,
    extract_company_intelligence,
    extract_meeting_scheduled,
]


def extract_signals(event: dict[str, Any]) -> list[RelationshipSignal]:
    signals: list[RelationshipSignal] = []
    for extractor in ALL_EXTRACTORS:
        try:
            signals.extend(extractor(event))
        except Exception as exc:
            print(f"[extract_signals] skipped extractor {extractor.__name__}: {exc}", file=sys.stderr)
            continue
    return signals


def extract_signals_batch(events: list[dict[str, Any]]) -> list[RelationshipSignal]:
    signals: list[RelationshipSignal] = []
    for event in events:
        signals.extend(extract_signals(event))
    return signals


def adapt_raw_activity(raw: dict[str, Any]) -> dict[str, Any]:
    """Adapt a raw activity_feed.jsonl entry to the normalized event schema
    so extractors can process it. This is a compatibility shim for testing
    against real data that hasn't been through normalize.py."""
    entities = {
        "people": raw.get("people", []),
        "companies": raw.get("companies", []),
        "tools": raw.get("tools", []),
        "urls": raw.get("urls", []),
    }
    return {
        "event_id": raw.get("id", ""),
        "source_type": _infer_source_type(raw),
        "source_memory_id": raw.get("id", ""),
        "timestamp": raw.get("timestamp", ""),
        "app": raw.get("app", ""),
        "window_title": raw.get("window", ""),
        "title": raw.get("title", ""),
        "summary": raw.get("summary", ""),
        "category": raw.get("category"),
        "significance": raw.get("significance", 0.0),
        "entities": entities,
        "actions": raw.get("actions", []),
        "sentiment": raw.get("sentiment"),
        "raw_content_hash": "",
    }


def _infer_source_type(raw: dict[str, Any]) -> str:
    app = (raw.get("app") or "").lower().strip()
    if "gmail" in app or "mail" in app:
        return "gmail"
    if "calendar" in app or "google calendar" in app:
        return "calendar"
    return "desktop"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract relationship signals from normalized events."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Path to JSONL file of normalized events, or '-' for stdin.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Input is raw activity_feed.jsonl format (auto-adapt to normalized schema).",
    )
    parser.add_argument(
        "--signal-type",
        choices=[
            "new_contact",
            "renewed_contact",
            "introduction",
            "follow_up_commitment",
            "company_intelligence",
            "meeting_scheduled",
        ],
        help="Only extract signals of this type.",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.0,
        help="Minimum confidence threshold for output signals.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary statistics instead of individual signals.",
    )
    args = parser.parse_args()

    if args.input == "-":
        lines = sys.stdin.readlines()
    else:
        with open(args.input, encoding="utf-8") as f:
            lines = f.readlines()

    events = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if args.raw:
            obj = adapt_raw_activity(obj)
        events.append(obj)

    if args.signal_type:
        extractor_map = {fn.__name__.replace("extract_", ""): fn for fn in ALL_EXTRACTORS}
        fn = extractor_map.get(args.signal_type)
        if fn is None:
            print(f"Unknown signal type: {args.signal_type}", file=sys.stderr)
            return 1
        all_signals = []
        for event in events:
            try:
                all_signals.extend(fn(event))
            except Exception:
                continue  # skip broken event, process remaining
    else:
        all_signals = extract_signals_batch(events)

    if args.min_confidence > 0:
        all_signals = [s for s in all_signals if s.confidence >= args.min_confidence]

    if args.summary:
        by_type: dict[str, int] = {}
        for s in all_signals:
            by_type[s.signal_type] = by_type.get(s.signal_type, 0) + 1
        print(json.dumps({
            "total_events": len(events),
            "total_signals": len(all_signals),
            "by_type": by_type,
        }, indent=2))
    else:
        for signal in all_signals:
            print(json.dumps(signal.to_dict()))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
