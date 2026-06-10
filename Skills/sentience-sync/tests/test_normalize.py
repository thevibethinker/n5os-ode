import json
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from normalize import normalize


def test_desktop_memory_normalizes_to_canonical_contract():
    memory = {
        "id": "screenshot_123",
        "timestamp": "2026-04-06T15:30:36.927000Z",
        "source": "Sentience Desktop App",
        "content": json.dumps(
            {
                "appName": "Superhuman",
                "windowTitle": "Drafting intro email",
                "title": "Drafting intro email for Ahmed",
                "summary": "Preparing an intro email connecting Ahmed and Yakaira about dance archive data.",
                "significance_score": 0.81,
                "category": "Work",
                "sentiment": {"overall": "focused"},
                "facts": {
                    "people": ["Ahmed Rashad", "Yakaira Nunez"],
                    "companies": ["Perle.ai"],
                    "tools": ["Superhuman"],
                    "actions": [
                        {"subject": "V", "verb": "drafting", "object": "intro email"}
                    ],
                    "urls": ["https://perle.ai"],
                },
            }
        ),
    }

    first = normalize(memory)
    second = normalize(memory)

    assert first is not None
    assert first == second
    assert first["event_id"] == sha256(b"desktop|screenshot_123").hexdigest()
    assert first["source_type"] == "desktop"
    assert first["app"] == "Superhuman"
    assert first["window_title"] == "Drafting intro email"
    assert first["category"] == "Work"
    assert first["sentiment"] == "focused"
    assert first["entities"] == {
        "people": ["Ahmed Rashad", "Yakaira Nunez"],
        "companies": ["Perle.ai"],
        "tools": ["Superhuman"],
        "urls": ["https://perle.ai"],
    }


def test_gmail_memory_extracts_subject_people_and_company_domains():
    memory = {
        "id": "gmail_123",
        "timestamp": "2026-04-06T10:24:31Z",
        "source": "Gmail",
        "content": "\n".join(
            [
                "Intro: Dev & Primary (4 messages)",
                "",
                "--- Message 1 of 4 ---",
                "From: Dev Chandra <dev@startupintros.com>",
                "To: Primary User <primary@example.com>",
                "Cc: Alex Caveny <alex@contextventures.com>",
                "Date: Thu, 26 Mar 2026 14:35:16 +0000",
                "Subject: Intro: Dev & Primary",
                "",
                "Great to meet. I added you on LinkedIn and would love to set something up next week.",
            ]
        ),
    }

    event = normalize(memory)

    assert event is not None
    assert event["event_id"] == sha256(b"gmail|gmail_123").hexdigest()
    assert event["source_type"] == "gmail"
    assert event["app"] is None
    assert event["title"] == "Intro: Dev & Primary"
    assert event["summary"].startswith("Intro: Dev & Primary:")
    assert event["entities"]["people"] == [
        "Dev Chandra",
        "Primary User",
        "Alex Caveny",
    ]
    assert event["entities"]["companies"] == [
        "startupintros.com",
        "contextventures.com",
    ]
    assert event["entities"]["tools"] == ["Gmail"]
    assert event["actions"] == [
        {
            "subject": "Dev Chandra",
            "verb": "emailed",
            "object": "Intro: Dev & Primary",
        }
    ]


def test_calendar_memory_extracts_attendees_and_urls():
    memory = {
        "id": "calendar_123",
        "timestamp": "2026-04-06T16:00:00+00:00Z",
        "source": "Google Calendar",
        "content": "\n".join(
            [
                "Calendar Event: Sentience Private Beta Onboarding - Walk through onboarding flow",
                "Attendees: Teddy Schoenfeld <teddy@sentience.ai>, Jerry Lu <jerry@sentience.ai>",
                "Location: https://meet.google.com/example",
            ]
        ),
    }

    event = normalize(memory)

    assert event is not None
    assert event["event_id"] == sha256(b"calendar|calendar_123").hexdigest()
    assert event["source_type"] == "calendar"
    assert event["title"] == "Sentience Private Beta Onboarding"
    assert event["entities"]["people"] == ["Teddy Schoenfeld", "Jerry Lu"]
    assert event["entities"]["companies"] == ["sentience.ai"]
    assert event["entities"]["tools"] == ["Google Calendar"]
    assert event["entities"]["urls"] == ["https://meet.google.com/example"]
    assert event["actions"] == [
        {
            "subject": "calendar",
            "verb": "scheduled",
            "object": "Sentience Private Beta Onboarding",
        }
    ]


def test_zo_originated_memory_is_excluded():
    memory = {
        "id": "api_123",
        "timestamp": "2026-04-06T10:24:31Z",
        "source": "api",
        "content": "[Zo Journal: testing]",
    }

    assert normalize(memory) is None
