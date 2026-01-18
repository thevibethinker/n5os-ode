#!/usr/bin/env python3
""" 
Unit tests for Deal Signal Router (Worker 1)

Pattern: tests insert /home/workspace/N5/scripts into sys.path.
"""

import sys
import sqlite3
import json
from pathlib import Path

sys.path.insert(0, '/home/workspace/N5/scripts')

from deal_signal_router import DealSignalRouter


def _create_test_db(tmp_path: Path) -> str:
    db_path = str(tmp_path / "deals_test.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE deals (
            id TEXT PRIMARY KEY,
            deal_type TEXT NOT NULL,
            company TEXT NOT NULL,
            primary_contact TEXT,
            temperature TEXT,
            stage TEXT,
            pipeline TEXT,
            next_action TEXT,
            next_action_date TEXT,
            last_touched TEXT,
            updated_at TEXT
        );
        """
    )

    c.execute(
        """
        CREATE TABLE deal_contacts (
            id TEXT PRIMARY KEY,
            contact_type TEXT NOT NULL,
            pipeline TEXT NOT NULL,
            full_name TEXT NOT NULL,
            company TEXT,
            associated_deal_id TEXT
        );
        """
    )

    c.execute(
        """
        CREATE TABLE deal_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            description TEXT,
            channel TEXT,
            created_at TEXT
        );
        """
    )

    # Seed deals
    c.execute(
        """
        INSERT INTO deals (id, deal_type, company, primary_contact, temperature, stage, pipeline, last_touched, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "cs-acq-darwinbox",
            "careerspan_acquirer",
            "Darwinbox",
            "Christine Song",
            "warm",
            "qualified",
            "careerspan",
            "2026-01-01T00:00:00",
            "2026-01-01T00:00:00",
        ),
    )

    c.execute(
        """
        INSERT INTO deals (id, deal_type, company, primary_contact, temperature, stage, pipeline, last_touched, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "zo-dp-aviato",
            "zo_partnership",
            "Aviato",
            None,
            None,
            "identified",
            "zo",
            "2026-01-01T00:00:00",
            "2026-01-01T00:00:00",
        ),
    )

    # Seed contact linked to a deal
    c.execute(
        """
        INSERT INTO deal_contacts (id, contact_type, pipeline, full_name, company, associated_deal_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "lead-christinesong",
            "leadership",
            "careerspan",
            "Christine Song",
            "Ribbon",
            "cs-acq-darwinbox",
        ),
    )

    conn.commit()
    conn.close()
    return db_path


def test_match_deal_heuristic_exact_company(tmp_path):
    db_path = _create_test_db(tmp_path)

    router = DealSignalRouter(
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        llm_callable=lambda prompt: "",  # force heuristic
    )

    m = router.match_deal("Darwinbox")
    assert m.deal_id == "cs-acq-darwinbox"
    assert m.confidence >= 95


def test_match_deal_heuristic_fuzzy_company(tmp_path):
    db_path = _create_test_db(tmp_path)

    router = DealSignalRouter(
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        llm_callable=lambda prompt: "",  # force heuristic
    )

    m = router.match_deal("darwnibox")
    assert m.deal_id == "cs-acq-darwinbox"
    assert m.confidence >= 70


def test_match_deal_via_contact_associated_deal_id(tmp_path):
    db_path = _create_test_db(tmp_path)

    # Force LLM path: return a contact match, no deal_id
    def fake_llm(prompt: str) -> str:
        if "Return ONLY valid JSON" in prompt:
            return json.dumps(
                {
                    "deal_id": None,
                    "contact_id": "lead-christinesong",
                    "confidence": 82,
                    "match_reason": "Matched contact name",
                }
            )
        return ""

    router = DealSignalRouter(
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        llm_callable=fake_llm,
    )

    m = router.match_deal("Christine")
    assert m.deal_id == "cs-acq-darwinbox"
    assert m.confidence >= 82


def test_extract_signal_llm_coerce(tmp_path):
    db_path = _create_test_db(tmp_path)

    def fake_llm(prompt: str) -> str:
        if "Extract deal intelligence" in prompt:
            return json.dumps(
                {
                    "stage_signal": "stage_change",
                    "inferred_stage": "negotiating",
                    "stage_change_reason": "They are discussing pricing",
                    "key_facts": ["Call next week"],
                    "next_action": "Schedule call",
                    "next_action_date": None,
                    "sentiment": "positive",
                    "urgency": "high",
                }
            )
        return "{}"

    router = DealSignalRouter(
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        llm_callable=fake_llm,
    )

    deal = router.get_deal("cs-acq-darwinbox")
    extraction = router.extract_signal("They are discussing pricing and want a call next week", deal)
    assert extraction.inferred_stage == "negotiating"
    assert extraction.stage_signal == "stage_change"


def test_process_signal_updates_db(tmp_path):
    db_path = _create_test_db(tmp_path)

    def fake_llm(prompt: str) -> str:
        # Deal match prompt
        if "matching a user query" in prompt:
            return json.dumps(
                {
                    "deal_id": "cs-acq-darwinbox",
                    "contact_id": None,
                    "confidence": 95,
                    "match_reason": "Exact deal match",
                }
            )

        # Extraction prompt
        if "Extract deal intelligence" in prompt:
            return json.dumps(
                {
                    "stage_signal": "stage_change",
                    "inferred_stage": "negotiating",
                    "stage_change_reason": "Ready to discuss terms",
                    "key_facts": ["Ready to move forward"],
                    "next_action": "Set up call next week",
                    "next_action_date": None,
                    "sentiment": "positive",
                    "urgency": "medium",
                }
            )

        return "{}"

    router = DealSignalRouter(
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        llm_callable=fake_llm,
    )

    res = router.process_signal(
        source="sms",
        content="n5 deal darwinbox Ready to move forward, setting up call next week",
        context="careerspan",
        dry_run=False,
    )

    assert res.success is True
    assert res.matched is True
    assert res.action_taken == "updated"

    # Verify deal updated
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT stage, next_action FROM deals WHERE id = ?", ("cs-acq-darwinbox",))
    stage, next_action = c.fetchone()
    assert stage == "negotiating"
    assert next_action == "Set up call next week"

    # Verify activity logged
    c.execute("SELECT COUNT(*) FROM deal_activities WHERE deal_id = ?", ("cs-acq-darwinbox",))
    count = c.fetchone()[0]
    assert count >= 1
    conn.close()
