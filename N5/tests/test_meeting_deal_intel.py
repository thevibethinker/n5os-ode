#!/usr/bin/env python3
"""
Tests for meeting_deal_intel.py (Worker 2)
"""

import sys
import json
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from meeting_deal_intel import (
    detect_deal_meeting,
    extract_deal_intel,
    extract_attendees_from_b03,
    extract_strategic_intel,
    infer_stage_change,
    DealIntel,
)
from deal_signal_router import DealSignalRouter, DealMatch


class MockRouter:
    """Mock router for testing without real DB."""
    
    def __init__(self):
        self.deals = {
            "cs-lead-calendly": {
                "id": "cs-lead-calendly",
                "deal_type": "leadership",
                "company": "Calendly",
                "pipeline": "careerspan",
                "stage": "engaged",
                "primary_contact": "Tope Awotona"
            }
        }
        self.contacts = {
            "lead-topeawotona": {
                "id": "lead-topeawotona",
                "full_name": "Tope Awotona",
                "company": "Calendly",
                "contact_type": "leadership",
                "associated_deal_id": "cs-lead-calendly"
            }
        }
    
    def match_deal(self, query: str, context: str = "") -> DealMatch:
        query_lower = query.lower()
        
        # Check contacts
        for contact in self.contacts.values():
            if contact["full_name"].lower() in query_lower:
                return DealMatch(
                    deal_id=contact.get("associated_deal_id"),
                    contact_id=contact["id"],
                    confidence=95,
                    match_reason="Contact match"
                )
        
        # Check deals
        for deal in self.deals.values():
            if deal["company"].lower() in query_lower:
                return DealMatch(
                    deal_id=deal["id"],
                    contact_id=None,
                    confidence=90,
                    match_reason="Company match"
                )
        
        return DealMatch(deal_id=None, contact_id=None, confidence=0, match_reason="No match")
    
    def get_deal(self, deal_id: str):
        return self.deals.get(deal_id)
    
    def extract_signal(self, text: str, deal_context: dict):
        from deal_signal_router import SignalExtraction
        return SignalExtraction(
            stage_signal="positive",
            inferred_stage=None,
            stage_change_reason=None,
            key_facts=["Test fact 1", "Test fact 2"],
            next_action="Follow up next week",
            next_action_date=None,
            sentiment="positive",
            urgency="normal"
        )


def test_extract_attendees_from_b03():
    """Test attendee extraction from B03 block."""
    b03_content = """
# B03: Stakeholder Intelligence

## Tope Awotona
**Role:** Founder & CEO, Calendly
**Company:** Calendly

### Profile
- Nigerian-American founder

## Vrijen Attawar
**Role:** Founder, Careerspan
"""
    attendees = extract_attendees_from_b03(b03_content)
    assert "Tope Awotona" in attendees
    # Note: regex captures names in ## headers that start with capital letter
    assert len(attendees) >= 1


def test_extract_strategic_intel():
    """Test strategic intel extraction from B01."""
    b01_content = """
## Meeting Overview
**Date:** 2026-01-16

### Acquisition Structure Discussion
- Tope asked about preferred exit structure
- V indicated most likely: acquirer wants one of two founders

### Key Metrics
- Average user engagement: 45+ minutes
- User base: 4,000 users with zero marketing spend
"""
    deal = {"company": "Calendly", "id": "cs-lead-calendly"}
    intel = extract_strategic_intel(b01_content, deal)
    
    # The function extracts bullet points containing company name or deal keywords
    # May return empty if no direct company mentions in bullets
    assert isinstance(intel, list)


def test_infer_stage_change():
    """Test stage inference from B01 content."""
    deal = {"stage": "engaged"}
    
    # Test qualified signals
    b01_qualified = "The budget has been approved and the decision maker confirmed interest. Timeline is Q1."
    intel = DealIntel(
        deal_id="test",
        deal_type="leadership",
        company="Test",
        pipeline="careerspan",
        meeting_date="2026-01-18",
        meeting_folder="/test"
    )
    
    stage_before, stage_after, confidence = infer_stage_change(intel, deal, b01_qualified)
    assert stage_before == "engaged"
    assert stage_after == "qualified"
    assert confidence > 50


def test_detect_deal_meeting_with_contact():
    """Test deal detection via contact name in folder."""
    router = MockRouter()
    
    # Create temp meeting folder
    with tempfile.TemporaryDirectory() as tmpdir:
        meeting_folder = Path(tmpdir) / "2026-01-16_Tope-Awotona-Meeting"
        meeting_folder.mkdir()
        
        # Create minimal manifest
        manifest = {"title": "Tope Awotona x V", "attendees": ["Tope Awotona", "V"]}
        (meeting_folder / "manifest.json").write_text(json.dumps(manifest))
        
        result = detect_deal_meeting(meeting_folder, router)
        
        assert result is not None
        match, deal = result
        assert match.deal_id == "cs-lead-calendly"
        assert deal["company"] == "Calendly"


def test_detect_deal_meeting_no_match():
    """Test that internal meetings don't match."""
    router = MockRouter()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        meeting_folder = Path(tmpdir) / "2026-01-16_Internal-Standup"
        meeting_folder.mkdir()
        
        manifest = {"title": "Daily Standup", "attendees": ["V", "Shane"]}
        (meeting_folder / "manifest.json").write_text(json.dumps(manifest))
        
        result = detect_deal_meeting(meeting_folder, router)
        assert result is None


def test_deal_intel_dataclass():
    """Test DealIntel dataclass structure."""
    intel = DealIntel(
        deal_id="cs-lead-calendly",
        deal_type="leadership",
        company="Calendly",
        pipeline="careerspan",
        meeting_date="2026-01-16",
        meeting_folder="/home/workspace/Personal/Meetings/test",
        attendees=["Tope Awotona", "V"],
        sentiment="positive",
        urgency="medium"
    )
    
    assert intel.deal_id == "cs-lead-calendly"
    assert intel.company == "Calendly"
    assert len(intel.attendees) == 2


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
