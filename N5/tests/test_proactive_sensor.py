#!/usr/bin/env python3
"""
Tests for Worker 6: Proactive Deal Sensor

Tests:
- Broker pattern detection
- Leadership pattern detection
- Deal pattern detection
- Known entity checking
- Approval queue operations
- Approval response processing (Y/N/Info)
- SMS formatting
"""

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from deal_proactive_sensor import (
    DealProactiveSensor,
    DetectedEntity,
    ApprovalRequest,
    ApprovalResult,
    BROKER_PATTERNS,
    LEADERSHIP_PATTERNS,
    DEAL_PATTERNS,
)


class TestProactiveSensorPatterns(unittest.TestCase):
    """Test pattern matching for entity detection."""

    def setUp(self):
        # Create temp database
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.sensor = DealProactiveSensor(db_path=self.temp_db.name)
        
        # Initialize tables
        conn = sqlite3.connect(self.temp_db.name)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id TEXT PRIMARY KEY,
                deal_type TEXT,
                company TEXT,
                pipeline TEXT,
                stage TEXT,
                first_identified TEXT,
                last_touched TEXT,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS deal_contacts (
                id TEXT PRIMARY KEY,
                contact_type TEXT,
                pipeline TEXT,
                full_name TEXT,
                company TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def test_broker_pattern_introduce(self):
        """Test broker detection: 'can introduce you to'"""
        text = "John said he can introduce you to the CEO of Workday."
        entities = self.sensor._detect_entities_heuristic(text, "meeting")
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, "broker")

    def test_broker_pattern_connect(self):
        """Test broker detection: 'let me connect you with'"""
        text = "Sarah mentioned she'll let me connect you with her network at Google."
        entities = self.sensor._detect_entities_heuristic(text, "email")
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, "broker")

    def test_broker_pattern_intro(self):
        """Test broker detection: 'I'll make an intro'"""
        text = "Marcus said I'll make an intro to some HR tech founders next week."
        entities = self.sensor._detect_entities_heuristic(text, "meeting")
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, "broker")

    def test_broker_pattern_know_someone(self):
        """Test broker detection: 'I know someone at'"""
        text = "She said I know someone at Deel who might be interested."
        entities = self.sensor._detect_entities_heuristic(text, "email")
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, "broker")

    def test_leadership_pattern_ceo(self):
        """Test leadership detection: CEO title"""
        text = "Meeting with David Chen, CEO of TalentTech, scheduled for Friday."
        entities = self.sensor._detect_entities_heuristic(text, "meeting")
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, "leadership")

    def test_leadership_pattern_vp(self):
        """Test leadership detection: VP title"""
        text = "Lisa Wang, VP of Engineering at Gusto, wants to discuss integration."
        entities = self.sensor._detect_entities_heuristic(text, "email")
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, "leadership")

    def test_leadership_pattern_founder(self):
        """Test leadership detection: founder"""
        text = "The founder of Lattice reached out about partnership opportunities."
        entities = self.sensor._detect_entities_heuristic(text, "email")
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, "leadership")

    def test_deal_pattern_acquisition(self):
        """Test deal detection: acquisition language"""
        text = "Acme Corp is looking to acquire HR tech companies in our space."
        entities = self.sensor._detect_entities_heuristic(text, "email")
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, "deal")

    def test_deal_pattern_interested(self):
        """Test deal detection: interested in partnering"""
        text = "They're interested in partnering with us on distribution."
        entities = self.sensor._detect_entities_heuristic(text, "meeting")
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].entity_type, "deal")

    def test_no_pattern_match(self):
        """Test that plain text doesn't trigger detection"""
        text = "The quarterly meeting went well. Revenue is up 20%."
        entities = self.sensor._detect_entities_heuristic(text, "meeting")
        
        self.assertEqual(len(entities), 0)


class TestKnownEntityCheck(unittest.TestCase):
    """Test checking if entity already exists in database."""

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.sensor = DealProactiveSensor(db_path=self.temp_db.name)
        
        # Set up tables with test data
        conn = sqlite3.connect(self.temp_db.name)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id TEXT PRIMARY KEY,
                deal_type TEXT,
                company TEXT,
                pipeline TEXT,
                stage TEXT,
                first_identified TEXT,
                last_touched TEXT,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS deal_contacts (
                id TEXT PRIMARY KEY,
                contact_type TEXT,
                pipeline TEXT,
                full_name TEXT,
                company TEXT,
                created_at TEXT
            )
        """)
        
        # Insert test data
        c.execute("INSERT INTO deals VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  ("cs-acq-workday", "acquisition", "Workday", "careerspan", "researched", 
                   "2026-01-01", "2026-01-15", "2026-01-01"))
        c.execute("INSERT INTO deal_contacts VALUES (?, ?, ?, ?, ?, ?)",
                  ("brok-john-smith", "broker", "careerspan", "John Smith", "Acme Corp", "2026-01-01"))
        
        conn.commit()
        conn.close()

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def test_known_deal(self):
        """Test that known deal is detected"""
        entity = DetectedEntity(
            entity_type="deal",
            name="Workday",
            company="Workday",
            context="Test",
            signal_strength="medium",
            source="meeting",
            source_text="Test",
            recommended_action="create_deal",
        )
        
        self.assertTrue(self.sensor.is_entity_known(entity))

    def test_known_contact(self):
        """Test that known contact is detected"""
        entity = DetectedEntity(
            entity_type="broker",
            name="John Smith",
            company="Acme Corp",
            context="Test",
            signal_strength="medium",
            source="meeting",
            source_text="Test",
            recommended_action="track_contact",
        )
        
        self.assertTrue(self.sensor.is_entity_known(entity))

    def test_unknown_entity(self):
        """Test that unknown entity is not flagged as known"""
        entity = DetectedEntity(
            entity_type="broker",
            name="Jane Doe",
            company="NewCo",
            context="Test",
            signal_strength="medium",
            source="meeting",
            source_text="Test",
            recommended_action="track_contact",
        )
        
        self.assertFalse(self.sensor.is_entity_known(entity))

    def test_partial_match_known(self):
        """Test partial name matching for known entities"""
        entity = DetectedEntity(
            entity_type="broker",
            name="Smith",  # Partial match
            company=None,
            context="Test",
            signal_strength="medium",
            source="meeting",
            source_text="Test",
            recommended_action="track_contact",
        )
        
        # Should match "John Smith"
        self.assertTrue(self.sensor.is_entity_known(entity))


class TestApprovalQueue(unittest.TestCase):
    """Test approval queue operations."""

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.sensor = DealProactiveSensor(db_path=self.temp_db.name)
        
        # Create required tables
        conn = sqlite3.connect(self.temp_db.name)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id TEXT PRIMARY KEY,
                deal_type TEXT,
                company TEXT,
                pipeline TEXT,
                stage TEXT,
                first_identified TEXT,
                last_touched TEXT,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS deal_contacts (
                id TEXT PRIMARY KEY,
                contact_type TEXT,
                pipeline TEXT,
                full_name TEXT,
                company TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def test_queue_approval(self):
        """Test queueing an entity for approval"""
        entity = DetectedEntity(
            entity_type="broker",
            name="Test Person",
            company="Test Corp",
            context="Can introduce you to folks",
            signal_strength="medium",
            source="meeting",
            source_text="Full meeting text here",
            recommended_action="track_contact",
            pipeline="careerspan",
        )
        
        approval_id = self.sensor.queue_approval(entity)
        
        self.assertIsNotNone(approval_id)
        self.assertEqual(len(approval_id), 8)  # UUID[:8]
        
        # Verify it's in database
        pending = self.sensor.get_pending(approval_id)
        self.assertIsNotNone(pending)
        self.assertEqual(pending.name, "Test Person")
        self.assertEqual(pending.status, "pending")

    def test_list_pending(self):
        """Test listing pending approvals"""
        # Queue two entities
        for i in range(2):
            entity = DetectedEntity(
                entity_type="broker",
                name=f"Person {i}",
                company=f"Company {i}",
                context="Test context",
                signal_strength="medium",
                source="meeting",
                source_text="Test",
                recommended_action="track_contact",
            )
            self.sensor.queue_approval(entity)
        
        pending = self.sensor.list_pending()
        self.assertEqual(len(pending), 2)

    def test_get_nonexistent_pending(self):
        """Test getting a non-existent approval"""
        pending = self.sensor.get_pending("nonexistent")
        self.assertIsNone(pending)


class TestApprovalProcessing(unittest.TestCase):
    """Test processing approval responses."""

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.sensor = DealProactiveSensor(db_path=self.temp_db.name)
        
        # Create required tables
        conn = sqlite3.connect(self.temp_db.name)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id TEXT PRIMARY KEY,
                deal_type TEXT,
                company TEXT,
                pipeline TEXT,
                stage TEXT,
                first_identified TEXT,
                last_touched TEXT,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS deal_contacts (
                id TEXT PRIMARY KEY,
                contact_type TEXT,
                pipeline TEXT,
                full_name TEXT,
                company TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def _queue_test_entity(self, entity_type="broker"):
        """Helper to queue a test entity."""
        entity = DetectedEntity(
            entity_type=entity_type,
            name="Jane Doe",
            company="NewCo Inc",
            context="She can connect you with decision makers",
            signal_strength="strong",
            source="email",
            source_text="Full email text about introductions",
            recommended_action="track_contact",
            pipeline="careerspan",
        )
        return self.sensor.queue_approval(entity)

    def test_approve_broker(self):
        """Test approving a broker creates contact"""
        approval_id = self._queue_test_entity("broker")
        
        result = self.sensor.process_approval(approval_id, "Y")
        
        self.assertTrue(result.success)
        self.assertEqual(result.action, "created")
        self.assertIn("Jane Doe", result.message)
        self.assertIsNotNone(result.created_id)
        
        # Verify contact was created
        conn = sqlite3.connect(self.temp_db.name)
        c = conn.cursor()
        c.execute("SELECT * FROM deal_contacts WHERE full_name = 'Jane Doe'")
        contact = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(contact)

    def test_approve_deal(self):
        """Test approving a deal creates deal record"""
        entity = DetectedEntity(
            entity_type="deal",
            name="AcquireCo",
            company="AcquireCo",
            context="Looking to acquire HR tech",
            signal_strength="strong",
            source="email",
            source_text="Full email about acquisition interest",
            recommended_action="create_deal",
            pipeline="careerspan",
        )
        approval_id = self.sensor.queue_approval(entity)
        
        result = self.sensor.process_approval(approval_id, "Y")
        
        self.assertTrue(result.success)
        self.assertEqual(result.action, "created")
        
        # Verify deal was created
        conn = sqlite3.connect(self.temp_db.name)
        c = conn.cursor()
        c.execute("SELECT * FROM deals WHERE company = 'AcquireCo'")
        deal = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(deal)

    def test_decline_approval(self):
        """Test declining an approval"""
        approval_id = self._queue_test_entity()
        
        result = self.sensor.process_approval(approval_id, "N")
        
        self.assertTrue(result.success)
        self.assertEqual(result.action, "declined")
        
        # Verify status updated
        pending = self.sensor.get_pending(approval_id)
        # After declining, status should be 'declined'
        conn = sqlite3.connect(self.temp_db.name)
        c = conn.cursor()
        c.execute("SELECT status FROM pending_approvals WHERE id = ?", (approval_id,))
        row = c.fetchone()
        conn.close()
        
        self.assertEqual(row[0], "declined")

    def test_info_request(self):
        """Test requesting more info"""
        approval_id = self._queue_test_entity()
        
        result = self.sensor.process_approval(approval_id, "Info")
        
        self.assertTrue(result.success)
        self.assertEqual(result.action, "info")
        self.assertIn("Full context", result.message)
        self.assertIn(approval_id, result.message)

    def test_invalid_response(self):
        """Test invalid response handling"""
        approval_id = self._queue_test_entity()
        
        result = self.sensor.process_approval(approval_id, "Maybe")
        
        self.assertFalse(result.success)
        self.assertEqual(result.action, "error")
        self.assertIn("Unknown response", result.message)

    def test_nonexistent_approval(self):
        """Test processing non-existent approval"""
        result = self.sensor.process_approval("badid123", "Y")
        
        self.assertFalse(result.success)
        self.assertEqual(result.action, "not_found")

    def test_case_insensitive_response(self):
        """Test that Y/N/Info are case-insensitive"""
        approval_id = self._queue_test_entity()
        
        # Test lowercase
        result = self.sensor.process_approval(approval_id, "y")
        self.assertTrue(result.success)
        self.assertEqual(result.action, "created")


class TestSMSFormatting(unittest.TestCase):
    """Test SMS message formatting."""

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.sensor = DealProactiveSensor(db_path=self.temp_db.name)

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def test_broker_sms_format(self):
        """Test SMS format for broker detection"""
        entity = DetectedEntity(
            entity_type="broker",
            name="John Smith",
            company="Acme Corp",
            context="He can introduce you to several HR tech CEOs",
            signal_strength="strong",
            source="meeting",
            source_text="Full text",
            recommended_action="track_contact",
        )
        
        sms = self.sensor.format_approval_sms(entity, "abc12345")
        
        self.assertIn("🤝", sms)  # Broker emoji
        self.assertIn("broker", sms)
        self.assertIn("John Smith", sms)
        self.assertIn("Acme Corp", sms)
        self.assertIn("abc12345", sms)
        self.assertIn("Y - Add", sms)
        self.assertIn("N - Skip", sms)

    def test_deal_sms_format(self):
        """Test SMS format for deal detection"""
        entity = DetectedEntity(
            entity_type="deal",
            name="TechCorp",
            company="TechCorp",
            context="Looking to acquire career tech companies",
            signal_strength="medium",
            source="email",
            source_text="Full text",
            recommended_action="create_deal",
        )
        
        sms = self.sensor.format_approval_sms(entity, "def67890")
        
        self.assertIn("🏢", sms)  # Deal emoji
        self.assertIn("deal target", sms)
        self.assertIn("TechCorp", sms)
        self.assertIn("def67890", sms)

    def test_leadership_sms_format(self):
        """Test SMS format for leadership detection"""
        entity = DetectedEntity(
            entity_type="leadership",
            name="Sarah Chen",
            company="BigCo",
            context="CEO interested in discussing partnerships",
            signal_strength="strong",
            source="meeting",
            source_text="Full text",
            recommended_action="track_contact",
        )
        
        sms = self.sensor.format_approval_sms(entity, "ghi11111")
        
        self.assertIn("👔", sms)  # Leadership emoji
        self.assertIn("leadership contact", sms)
        self.assertIn("Sarah Chen", sms)
        self.assertIn("BigCo", sms)

    def test_context_truncation(self):
        """Test that long context is truncated"""
        entity = DetectedEntity(
            entity_type="broker",
            name="Test Person",
            company=None,
            context="x" * 200,  # Long context
            signal_strength="medium",
            source="meeting",
            source_text="Full text",
            recommended_action="track_contact",
        )
        
        sms = self.sensor.format_approval_sms(entity, "abc12345")
        
        # Context should be truncated to ~100 chars + "..."
        self.assertIn("...", sms)


class TestEndToEndFlow(unittest.TestCase):
    """Test end-to-end detection and approval flow."""

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.sensor = DealProactiveSensor(db_path=self.temp_db.name)
        
        # Create required tables
        conn = sqlite3.connect(self.temp_db.name)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS deals (
                id TEXT PRIMARY KEY,
                deal_type TEXT,
                company TEXT,
                pipeline TEXT,
                stage TEXT,
                first_identified TEXT,
                last_touched TEXT,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS deal_contacts (
                id TEXT PRIMARY KEY,
                contact_type TEXT,
                pipeline TEXT,
                full_name TEXT,
                company TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        os.unlink(self.temp_db.name)

    def test_full_broker_flow(self):
        """Test: detect broker → queue → approve → create"""
        # Step 1: Detect
        text = "Mark Johnson said he can introduce you to the CEO of Rippling."
        result = self.sensor.process_text(text, "meeting", dry_run=False, send_sms=False)
        
        self.assertEqual(len(result.entities_detected), 1)
        self.assertEqual(result.entities_queued, 1)
        self.assertEqual(len(result.sms_formatted), 1)
        
        # Step 2: Get the approval ID from the SMS
        sms = result.sms_formatted[0]
        import re
        match = re.search(r'\[([a-f0-9]{8})\]', sms)
        self.assertIsNotNone(match)
        approval_id = match.group(1)
        
        # Step 3: Approve
        approval_result = self.sensor.process_approval(approval_id, "Y")
        
        self.assertTrue(approval_result.success)
        self.assertEqual(approval_result.action, "created")
        
        # Step 4: Verify contact exists
        conn = sqlite3.connect(self.temp_db.name)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM deal_contacts WHERE contact_type = 'broker'")
        count = c.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 1)

    def test_dry_run_no_db_changes(self):
        """Test that dry run doesn't modify database"""
        text = "Lisa Wang can introduce you to folks at Workday."
        result = self.sensor.process_text(text, "meeting", dry_run=True, send_sms=False)
        
        self.assertEqual(result.entities_queued, 0)
        self.assertTrue(result.dry_run)
        
        # Verify nothing was queued
        pending = self.sensor.list_pending()
        self.assertEqual(len(pending), 0)

    def test_known_entity_not_queued(self):
        """Test that known entities are not queued"""
        # Add known contact
        conn = sqlite3.connect(self.temp_db.name)
        c = conn.cursor()
        c.execute("INSERT INTO deal_contacts VALUES (?, ?, ?, ?, ?, ?)",
                  ("brok-john-smith", "broker", "careerspan", "John Smith", "Acme", "2026-01-01"))
        conn.commit()
        conn.close()
        
        # Try to detect same person
        text = "John Smith can introduce you to some HR tech leaders."
        result = self.sensor.process_text(text, "meeting", dry_run=False, send_sms=False)
        
        # Should detect but not queue (known entity)
        self.assertEqual(result.entities_queued, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
