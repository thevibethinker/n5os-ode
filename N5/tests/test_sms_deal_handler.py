#!/usr/bin/env python3
"""
Unit tests for SMS Deal Handler (Worker 4)

Pattern: tests insert /home/workspace/N5/scripts into sys.path.
Run with: pytest N5/tests/test_sms_deal_handler.py -v
"""

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, '/home/workspace/N5/scripts')

from sms_deal_handler import (
    parse_sms_deal_command,
    get_similar_deals,
    handle_deal_sms,
    ParsedCommand,
)


def _create_test_db(tmp_path: Path) -> str:
    """Create a test database with sample deals."""
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
    deals = [
        ("cs-acq-darwinbox", "careerspan_acquirer", "Darwinbox", "Christine Song", "warm", "qualified", "careerspan"),
        ("cs-acq-ribbon", "careerspan_acquirer", "Ribbon Health", "Dan Wong", "hot", "engaged", "careerspan"),
        ("zo-dp-aviato", "zo_partnership", "Aviato", None, None, "identified", "zo"),
        ("cs-acq-gloat", "careerspan_acquirer", "Gloat HR", "Sarah Chen", "warm", "outreach", "careerspan"),
        ("cs-acq-deel", "careerspan_acquirer", "Deel", None, "cool", "researched", "careerspan"),
    ]

    for d in deals:
        c.execute(
            """
            INSERT INTO deals (id, deal_type, company, primary_contact, temperature, stage, pipeline, last_touched, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, '2026-01-01T00:00:00', '2026-01-01T00:00:00')
            """,
            d,
        )

    conn.commit()
    conn.close()
    return db_path


# ============================================
# Tests for parse_sms_deal_command
# ============================================

def test_parse_valid_simple():
    """Test parsing a simple valid command."""
    result = parse_sms_deal_command("n5 deal darwinbox Ready to proceed with pilot")
    assert result.valid is True
    assert result.query == "darwinbox"
    assert result.update == "Ready to proceed with pilot"


def test_parse_valid_uppercase():
    """Test parsing with uppercase."""
    result = parse_sms_deal_command("N5 DEAL GLOAT Meeting scheduled for Tuesday")
    assert result.valid is True
    assert result.query == "GLOAT"
    assert result.update == "Meeting scheduled for Tuesday"


def test_parse_valid_quoted_company():
    """Test parsing with quoted multi-word company name."""
    result = parse_sms_deal_command('n5 deal "ribbon health" Christine confirmed budget')
    assert result.valid is True
    assert result.query == "ribbon health"
    assert result.update == "Christine confirmed budget"


def test_parse_valid_single_quotes():
    """Test parsing with single-quoted company name."""
    result = parse_sms_deal_command("n5 deal 'gloat hr' Setup pilot program")
    assert result.valid is True
    assert result.query == "gloat hr"
    assert result.update == "Setup pilot program"


def test_parse_invalid_no_prefix():
    """Test that non-deal commands are rejected."""
    result = parse_sms_deal_command("deal darwinbox something")
    assert result.valid is False
    assert "Not a deal command" in result.error


def test_parse_invalid_missing_update():
    """Test that missing update text is rejected."""
    result = parse_sms_deal_command("n5 deal darwinbox")
    assert result.valid is False
    assert "Missing update" in result.error


def test_parse_invalid_empty_after_prefix():
    """Test that empty content after prefix is rejected."""
    result = parse_sms_deal_command("n5 deal")
    assert result.valid is False
    assert "Missing company" in result.error


def test_parse_invalid_completely_different():
    """Test that unrelated messages are rejected."""
    result = parse_sms_deal_command("Hey what's the weather?")
    assert result.valid is False


# ============================================
# Tests for get_similar_deals
# ============================================

def test_similar_deals_exact_substring(tmp_path):
    """Test that substring matches score highly."""
    db_path = _create_test_db(tmp_path)
    results = get_similar_deals(db_path, "darwin")
    
    assert len(results) >= 1
    assert results[0][1] == "Darwinbox"
    assert results[0][2] >= 70


def test_similar_deals_fuzzy(tmp_path):
    """Test fuzzy matching for typos."""
    db_path = _create_test_db(tmp_path)
    results = get_similar_deals(db_path, "darwnibox")  # typo
    
    assert len(results) >= 1
    # Darwinbox should still be suggested
    companies = [r[1] for r in results]
    assert "Darwinbox" in companies


def test_similar_deals_no_match(tmp_path):
    """Test that completely unrelated queries return empty."""
    db_path = _create_test_db(tmp_path)
    results = get_similar_deals(db_path, "xyznonexistent")
    
    # May return some low-score matches or empty
    for r in results:
        assert r[2] < 70  # All should be low confidence


# ============================================
# Tests for handle_deal_sms (integration)
# ============================================

def test_handle_deal_sms_success(tmp_path):
    """Test successful deal update."""
    db_path = _create_test_db(tmp_path)
    
    result = handle_deal_sms(
        message="n5 deal darwinbox Ready to proceed with pilot",
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        dry_run=False
    )
    
    assert result.success is True
    assert result.matched is True
    assert result.deal_id == "cs-acq-darwinbox"
    assert result.deal_company == "Darwinbox"
    assert "✓ Updated" in result.response
    assert "Darwinbox" in result.response


def test_handle_deal_sms_dry_run(tmp_path):
    """Test dry run mode."""
    db_path = _create_test_db(tmp_path)
    
    result = handle_deal_sms(
        message="n5 deal ribbon Christine confirmed budget approval",
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        dry_run=True
    )
    
    assert result.success is True
    assert result.matched is True
    assert result.dry_run is True
    assert "DRY RUN" in result.response
    assert "Ribbon" in result.response


def test_handle_deal_sms_no_match(tmp_path):
    """Test handling of unmatched deal."""
    db_path = _create_test_db(tmp_path)
    
    result = handle_deal_sms(
        message="n5 deal nonexistentcompany Some update here",
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        dry_run=False
    )
    
    assert result.success is True  # Command was valid, just no match
    assert result.matched is False
    assert result.deal_id is None
    assert "⚠️" in result.response
    assert "No deal" in result.response


def test_handle_deal_sms_invalid_command(tmp_path):
    """Test handling of invalid command format."""
    db_path = _create_test_db(tmp_path)
    
    result = handle_deal_sms(
        message="Hey what's up?",
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        dry_run=False
    )
    
    assert result.success is False
    assert result.matched is False
    assert "❌" in result.response


def test_handle_deal_sms_fuzzy_match(tmp_path):
    """Test that fuzzy company names still match."""
    db_path = _create_test_db(tmp_path)
    
    # "gloat" should match "Gloat HR"
    result = handle_deal_sms(
        message="n5 deal gloat Meeting scheduled for Thursday",
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        dry_run=False
    )
    
    assert result.success is True
    assert result.matched is True
    assert "Gloat" in result.deal_company


def test_handle_deal_sms_activity_logged(tmp_path):
    """Test that activity is logged to database."""
    db_path = _create_test_db(tmp_path)
    
    # Get initial activity count
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM deal_activities WHERE deal_id = 'cs-acq-darwinbox'")
    initial_count = c.fetchone()[0]
    conn.close()
    
    # Process update
    result = handle_deal_sms(
        message="n5 deal darwinbox They want to schedule a demo next week",
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        dry_run=False
    )
    
    assert result.success is True
    
    # Check activity was logged
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM deal_activities WHERE deal_id = 'cs-acq-darwinbox'")
    new_count = c.fetchone()[0]
    conn.close()
    
    assert new_count > initial_count


def test_handle_deal_sms_stage_extraction(tmp_path):
    """Test that stage changes are extracted and reflected."""
    db_path = _create_test_db(tmp_path)
    
    result = handle_deal_sms(
        message="n5 deal darwinbox They're ready to negotiate terms and pricing",
        db_path=db_path,
        config_path="/home/workspace/N5/config/deal_signal_config.json",
        dry_run=False
    )
    
    assert result.success is True
    assert result.matched is True
    
    # Check if extraction captured stage signal
    if result.process_result and result.process_result.extraction:
        ext = result.process_result.extraction
        # Should detect negotiation signal
        assert ext.stage_signal in ['positive', 'stage_change'] or ext.sentiment == 'positive'
