#!/usr/bin/env python3
"""Tests for extract_signals.py — relationship signal extractors."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from extract_signals import (
    RelationshipSignal,
    adapt_raw_activity,
    extract_company_intelligence,
    extract_follow_up_commitment,
    extract_introduction,
    extract_meeting_scheduled,
    extract_new_contact,
    extract_renewed_contact,
    extract_signals,
    extract_signals_batch,
)


def _make_event(
    *,
    event_id: str = "test-001",
    source_type: str = "desktop",
    timestamp: str = "2026-04-07T18:30:00Z",
    app: str | None = "Zo",
    title: str = "",
    summary: str = "",
    people: list[str] | None = None,
    companies: list[str] | None = None,
    tools: list[str] | None = None,
    urls: list[str] | None = None,
    actions: list[dict] | None = None,
    significance: float = 0.5,
    sentiment: str | None = None,
) -> dict:
    return {
        "event_id": event_id,
        "source_type": source_type,
        "source_memory_id": event_id,
        "timestamp": timestamp,
        "app": app,
        "window_title": None,
        "title": title,
        "summary": summary,
        "category": None,
        "significance": significance,
        "entities": {
            "people": people or [],
            "companies": companies or [],
            "tools": tools or [],
            "urls": urls or [],
        },
        "actions": actions or [],
        "sentiment": sentiment,
        "raw_content_hash": "",
    }


class TestNewContact:
    def test_s2_conference_meeting(self):
        """S2: Conference meeting produces new_contact signal."""
        event = _make_event(
            summary="Met someone new at the VentureConnect conference. Great conversation about robotics data.",
            title="Meeting new contact at conference",
            people=["Sarah Chen"],
            companies=["RoboData Inc"],
            actions=[
                {"subject": "user", "verb": "meeting", "object": "Sarah Chen at VentureConnect"}
            ],
        )
        signals = extract_new_contact(event)
        assert len(signals) == 1
        s = signals[0]
        assert s.signal_type == "new_contact"
        assert s.details["person_name"] == "Sarah Chen"
        assert "RoboData Inc" in s.details.get("company", "")
        assert event["event_id"] in s.source_event_ids

    def test_humanx_conference(self):
        """HumanX conference context triggers new_contact."""
        event = _make_event(
            summary="Logging Daniela Braga from HumanX roundtable for CRM intel",
            title="Logging conference contact",
            people=["Daniela Braga"],
            companies=["HumanX"],
            actions=[
                {"subject": "user", "verb": "reviewing", "object": "chat about logging Daniela Braga from HumanX roundtable for CRM intel"},
                {"subject": "user", "verb": "sending", "object": "CRM logging message"},
            ],
        )
        signals = extract_new_contact(event)
        assert len(signals) == 1
        assert signals[0].details["person_name"] == "Daniela Braga"

    def test_no_people_no_signal(self):
        """No people = no new_contact signal even with conference language."""
        event = _make_event(
            summary="Attended a great conference networking event",
            people=[],
            actions=[{"subject": "user", "verb": "attending", "object": "networking event"}],
        )
        signals = extract_new_contact(event)
        assert len(signals) == 0

    def test_self_filtered_out(self):
        """Self-references don't produce new_contact."""
        event = _make_event(
            summary="Met Primary User at the conference",
            people=["Primary User"],
            actions=[{"subject": "user", "verb": "meeting", "object": "contact at conference"}],
        )
        signals = extract_new_contact(event)
        assert len(signals) == 0

    def test_passive_browsing_no_signal(self):
        """Inbox browsing with visible names does NOT produce new_contact."""
        event = _make_event(
            summary="Scrolling through inbox, saw messages from several people",
            people=["Alice", "Bob", "Charlie"],
            actions=[
                {"subject": "user", "verb": "reviewing", "object": "WhatsApp chats"}
            ],
        )
        signals = extract_new_contact(event)
        assert len(signals) == 0


class TestRenewedContact:
    def test_reconnection_language(self):
        event = _make_event(
            summary="Reconnecting with Ahmed after the conference. Haven't spoken since last year.",
            people=["Ahmed"],
            actions=[{"subject": "user", "verb": "messaging", "object": "Ahmed about reconnecting"}],
        )
        signals = extract_renewed_contact(event)
        assert len(signals) == 1
        assert signals[0].signal_type == "renewed_contact"
        assert signals[0].details["person_name"] == "Ahmed"

    def test_no_renewed_language_no_signal(self):
        event = _make_event(
            summary="Chatting with Ahmed about the project update.",
            people=["Ahmed"],
            actions=[{"subject": "user", "verb": "messaging", "object": "Ahmed"}],
        )
        signals = extract_renewed_contact(event)
        assert len(signals) == 0

    def test_passive_browsing_no_signal(self):
        event = _make_event(
            summary="Reviewing old messages, reconnecting with contacts",
            people=["Alice", "Bob"],
            actions=[{"subject": "user", "verb": "reviewing", "object": "WhatsApp chats"}],
        )
        signals = extract_renewed_contact(event)
        assert len(signals) == 0


class TestIntroduction:
    def test_s1_intro_email(self):
        """S1: Intro email produces introduction signal."""
        event = _make_event(
            summary="Drafting email to introduce Yakaira to Ahmed",
            title="Writing introduction email",
            people=["Yakaira", "Ahmed"],
            actions=[
                {"subject": "user", "verb": "drafting", "object": "email to introduce Yakaira to Ahmed"}
            ],
        )
        signals = extract_introduction(event)
        assert len(signals) == 1
        s = signals[0]
        assert s.signal_type == "introduction"
        assert "Yakaira" in s.details["introduced_parties"]
        assert "Ahmed" in s.details["introduced_parties"]
        assert s.details["introducer"] == "V"

    def test_needs_two_people(self):
        """Introduction needs at least 2 people."""
        event = _make_event(
            summary="Introducing Yakaira to the team",
            people=["Yakaira"],
            actions=[{"subject": "user", "verb": "introducing", "object": "Yakaira"}],
        )
        signals = extract_introduction(event)
        assert len(signals) == 0

    def test_connect_language(self):
        event = _make_event(
            summary="Putting Sarah in touch with Raj about the data partnership",
            people=["Sarah", "Raj"],
            actions=[{"subject": "user", "verb": "connecting", "object": "Sarah and Raj"}],
        )
        signals = extract_introduction(event)
        assert len(signals) == 1


class TestFollowUpCommitment:
    def test_s1_follow_up_from_intro(self):
        """S1: Intro email with follow-up commitment language."""
        event = _make_event(
            summary="Need to follow up with Ahmed about the data partnership after our intro email",
            people=["Ahmed"],
            actions=[{"subject": "user", "verb": "drafting", "object": "follow-up email to Ahmed"}],
        )
        signals = extract_follow_up_commitment(event)
        assert len(signals) == 1
        s = signals[0]
        assert s.signal_type == "follow_up_commitment"
        assert s.details["person_name"] == "Ahmed"
        assert "follow" in s.details["commitment_text"].lower()

    def test_with_deadline(self):
        event = _make_event(
            summary="Promised to send the deck to Raj by tomorrow",
            people=["Raj"],
            actions=[{"subject": "user", "verb": "sending", "object": "deck to Raj"}],
        )
        signals = extract_follow_up_commitment(event)
        assert len(signals) == 1
        assert signals[0].details["implied_deadline"] is not None
        assert "tomorrow" in signals[0].details["implied_deadline"].lower()

    def test_no_commitment_language(self):
        event = _make_event(
            summary="Had a great meeting with Ahmed about the project",
            people=["Ahmed"],
            actions=[{"subject": "user", "verb": "discussing", "object": "project with Ahmed"}],
        )
        signals = extract_follow_up_commitment(event)
        assert len(signals) == 0

    def test_passive_browsing_no_signal(self):
        event = _make_event(
            summary="Reviewing follow up commitments in the project tracker",
            people=["Ahmed"],
            actions=[{"subject": "user", "verb": "reviewing", "object": "project task entries"}],
        )
        signals = extract_follow_up_commitment(event)
        assert len(signals) == 0


class TestCompanyIntelligence:
    def test_strategy_intel(self):
        event = _make_event(
            summary="Reviewing Physical Intelligence Stealth Strategy and hospital negotiations, MOU with KIMS group",
            people=["Dr. Attawar"],
            companies=["KIMS group of hospitals"],
            actions=[
                {"subject": "user", "verb": "reviewing", "object": "notes on an MOU with KIMS group"}
            ],
            significance=0.7,
        )
        signals = extract_company_intelligence(event)
        assert len(signals) == 1
        s = signals[0]
        assert s.signal_type == "company_intelligence"
        assert s.details["company_name"] == "KIMS group of hospitals"
        assert s.details["intelligence_type"] in ("partnership_deal", "data_operations", "funding_strategy")

    def test_low_significance_only_reviewing_skipped(self):
        """Low-significance passive review = no company intel signal."""
        event = _make_event(
            summary="Reviewing company strategy notes about fundraising",
            companies=["SomeCo"],
            actions=[{"subject": "user", "verb": "reviewing", "object": "notes"}],
            significance=0.3,
        )
        signals = extract_company_intelligence(event)
        assert len(signals) == 0

    def test_no_companies_no_signal(self):
        event = _make_event(
            summary="Interesting strategy discussion about fundraising",
            companies=[],
            actions=[{"subject": "user", "verb": "discussing", "object": "fundraising"}],
        )
        signals = extract_company_intelligence(event)
        assert len(signals) == 0

    def test_data_licensing_intel(self):
        event = _make_event(
            summary="KIMS Hospital Group has to license medical data, discussing their data operations pipeline",
            companies=["KIMS Hospital Group"],
            actions=[{"subject": "user", "verb": "discussing", "object": "medical data licensing"}],
            significance=0.7,
        )
        signals = extract_company_intelligence(event)
        assert len(signals) == 1
        assert signals[0].details["intelligence_type"] == "data_operations"


class TestMeetingScheduled:
    def test_calendar_event(self):
        event = _make_event(
            source_type="calendar",
            title="Sync with Ahmed Rashad",
            summary="Calendar event: Sync with Ahmed Rashad",
            people=["Ahmed Rashad"],
            companies=[],
            actions=[{"subject": "calendar", "verb": "scheduled", "object": "Sync with Ahmed Rashad"}],
        )
        signals = extract_meeting_scheduled(event)
        assert len(signals) == 1
        s = signals[0]
        assert s.signal_type == "meeting_scheduled"
        assert s.details["person_name"] == "Ahmed Rashad"
        assert s.confidence >= 0.8

    def test_google_meet_link_shared(self):
        event = _make_event(
            summary="Sending a Google Meet link to 'TAM too big, wallet too tight' chat",
            people=["Shivam Desai", "Anna M"],
            actions=[
                {"subject": "user", "verb": "sending", "object": "Google Meet link to 'TAM too big, wallet too tight' chat"}
            ],
        )
        signals = extract_meeting_scheduled(event)
        assert len(signals) == 1
        assert signals[0].signal_type == "meeting_scheduled"

    def test_no_meeting_language(self):
        event = _make_event(
            summary="Chatting with Ahmed about the project",
            people=["Ahmed"],
            actions=[{"subject": "user", "verb": "messaging", "object": "Ahmed"}],
        )
        signals = extract_meeting_scheduled(event)
        assert len(signals) == 0

    def test_calendar_no_people(self):
        """Calendar event without people = no signal."""
        event = _make_event(
            source_type="calendar",
            title="Lunch break",
            summary="Calendar event: Lunch break",
            people=[],
        )
        signals = extract_meeting_scheduled(event)
        assert len(signals) == 0


class TestS3RoutineScanningNoSignals:
    """S3: Routine email scanning produces no signals."""

    def test_inbox_browsing_many_names(self):
        event = _make_event(
            summary="Scrolling through Superhuman inbox, reviewing 20+ messages from various contacts",
            people=[
                "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank",
                "Grace", "Heidi", "Ivan", "Judy", "Karl", "Liam",
                "Mia", "Noah", "Olivia", "Pete", "Quinn", "Ruth",
                "Sam", "Tina",
            ],
            actions=[
                {"subject": "user", "verb": "browsing", "object": "inbox"},
                {"subject": "user", "verb": "scrolling", "object": "email list"},
            ],
        )
        signals = extract_signals(event)
        assert len(signals) == 0, f"Expected 0 signals for routine scanning, got {len(signals)}: {[s.signal_type for s in signals]}"

    def test_whatsapp_chat_list_reviewing(self):
        event = _make_event(
            summary="Reviewing WhatsApp chats and new messages",
            people=[
                "Family Member", "Shivam Desai", "Anna M",
                "Amanda Sachs", "Logan", "Nina",
            ],
            actions=[
                {"subject": "user", "verb": "reviewing", "object": "WhatsApp chats"},
            ],
        )
        signals = extract_signals(event)
        assert len(signals) == 0, f"Expected 0 signals for chat reviewing, got {len(signals)}: {[s.signal_type for s in signals]}"


class TestMultiSignalExtraction:
    def test_intro_plus_follow_up(self):
        """One event can produce both introduction and follow_up_commitment."""
        event = _make_event(
            summary="Drafting email to introduce Yakaira to Ahmed. Need to follow up with both about the data partnership.",
            people=["Yakaira", "Ahmed"],
            actions=[
                {"subject": "user", "verb": "drafting", "object": "email to introduce Yakaira to Ahmed"}
            ],
        )
        signals = extract_signals(event)
        types = {s.signal_type for s in signals}
        assert "introduction" in types
        assert "follow_up_commitment" in types

    def test_new_contact_plus_company_intel(self):
        """Conference meeting can produce both new_contact and company_intelligence."""
        event = _make_event(
            summary="Met Arunabh from Humyn Labs at the HumanX conference. They just raised a Series A for their data partnership deal.",
            people=["Arunabh"],
            companies=["Humyn Labs"],
            actions=[
                {"subject": "user", "verb": "meeting", "object": "Arunabh from Humyn Labs at conference"}
            ],
            significance=0.7,
        )
        signals = extract_signals(event)
        types = {s.signal_type for s in signals}
        assert "new_contact" in types
        assert "company_intelligence" in types


class TestProvenance:
    def test_all_signals_have_event_ids(self):
        event = _make_event(
            event_id="provenance-test-001",
            summary="Drafting email to introduce Yakaira to Ahmed. Need to follow up by tomorrow.",
            people=["Yakaira", "Ahmed"],
            actions=[
                {"subject": "user", "verb": "drafting", "object": "email to introduce Yakaira to Ahmed"}
            ],
        )
        signals = extract_signals(event)
        assert len(signals) > 0
        for s in signals:
            assert "provenance-test-001" in s.source_event_ids
            assert s.timestamp == event["timestamp"]


class TestAdaptRawActivity:
    def test_raw_desktop_adaptation(self):
        raw = {
            "id": "screenshot_75608",
            "timestamp": "2026-04-07T18:24:05.229000Z",
            "app": "Zo",
            "window": "Zo",
            "title": "Drafting content",
            "summary": "Drafting content for networking",
            "category": "Communication",
            "significance": 0.5,
            "sentiment": "neutral",
            "people": ["Ahmed"],
            "companies": ["HumanX"],
            "tools": ["Zo"],
            "actions": [{"subject": "user", "verb": "drafting", "object": "content"}],
            "urls": [],
            "emails": [],
            "dates": [],
        }
        adapted = adapt_raw_activity(raw)
        assert adapted["event_id"] == "screenshot_75608"
        assert adapted["source_type"] == "desktop"
        assert adapted["entities"]["people"] == ["Ahmed"]
        assert adapted["entities"]["companies"] == ["HumanX"]

    def test_gmail_inference(self):
        raw = {"id": "gmail_001", "app": "Gmail", "people": [], "companies": [], "tools": [], "actions": []}
        adapted = adapt_raw_activity(raw)
        assert adapted["source_type"] == "gmail"


class TestRealDataSmoke:
    """Smoke test against real activity_feed.jsonl entries."""

    def test_real_data_extraction(self):
        feed_path = Path(__file__).resolve().parent.parent / "data" / "activity_feed.jsonl"
        if not feed_path.exists():
            return

        events = []
        with open(feed_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError:
                    continue
                events.append(adapt_raw_activity(raw))

        all_signals = extract_signals_batch(events)

        by_type: dict[str, int] = {}
        for s in all_signals:
            by_type[s.signal_type] = by_type.get(s.signal_type, 0) + 1

        print(f"\nSmoke test: {len(events)} events → {len(all_signals)} signals")
        for t, c in sorted(by_type.items()):
            print(f"  {t}: {c}")

        for s in all_signals:
            assert s.source_event_ids, f"Signal {s.signal_type} missing provenance"
            assert s.timestamp, f"Signal {s.signal_type} missing timestamp"
            assert s.signal_type in {
                "new_contact",
                "renewed_contact",
                "introduction",
                "follow_up_commitment",
                "company_intelligence",
                "meeting_scheduled",
            }
            assert 0 < s.confidence <= 1.0

        signal_rate = len(all_signals) / max(len(events), 1)
        assert signal_rate < 0.5, (
            f"Signal rate {signal_rate:.2%} is suspiciously high — "
            f"extractors may not be conservative enough"
        )


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v", "--tb=short"]))
