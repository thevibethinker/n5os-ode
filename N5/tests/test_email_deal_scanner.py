#!/usr/bin/env python3
"""
Tests for Email Deal Scanner — Worker 5

Tests:
1. Query building from contacts/deals
2. Duplicate detection
3. Gmail response parsing
4. Email processing through signal router
5. Statistics tracking
"""

import json
import sqlite3
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from email_deal_scanner import (
    SearchQuery,
    EmailResult,
    ScanResult,
    build_search_queries,
    is_email_processed,
    mark_email_processed,
    parse_gmail_response,
    get_scan_stats,
    process_email,
    DB_PATH,
)


class TestQueryBuilding(unittest.TestCase):
    """Test search query generation."""
    
    def test_build_queries_returns_list(self):
        """Should return a list of SearchQuery objects."""
        queries = build_search_queries(days=7, max_queries=10)
        self.assertIsInstance(queries, list)
        for q in queries:
            self.assertIsInstance(q, SearchQuery)
    
    def test_queries_have_required_fields(self):
        """Each query should have all required fields."""
        queries = build_search_queries(days=7, max_queries=5)
        for q in queries:
            self.assertIsNotNone(q.query)
            self.assertIn(q.context_type, ["contact", "deal", "company", "custom"])
            self.assertIsNotNone(q.context_name)
    
    def test_queries_include_date_filter(self):
        """Queries should include after: date filter."""
        queries = build_search_queries(days=7, max_queries=5)
        for q in queries:
            self.assertIn("after:", q.query)
    
    def test_max_queries_respected(self):
        """Should not exceed max_queries limit."""
        queries = build_search_queries(days=7, max_queries=5)
        self.assertLessEqual(len(queries), 5)
    
    def test_priority_hot_filter(self):
        """Priority 'hot' should filter appropriately."""
        queries = build_search_queries(days=7, max_queries=50, priority="hot")
        # This is a behavioral test - hot deals should be prioritized
        self.assertIsInstance(queries, list)


class TestDuplicateDetection(unittest.TestCase):
    """Test email duplicate tracking."""
    
    def setUp(self):
        """Set up test database state."""
        self.test_message_id = f"test_msg_{datetime.now().timestamp()}"
    
    def test_new_email_not_processed(self):
        """New email should not be marked as processed."""
        unique_id = f"unique_{datetime.now().timestamp()}"
        self.assertFalse(is_email_processed(unique_id))
    
    def test_mark_and_check_processed(self):
        """Email should be marked as processed after marking."""
        test_id = f"test_mark_{datetime.now().timestamp()}"
        
        # Initially not processed
        self.assertFalse(is_email_processed(test_id))
        
        # Mark it
        mark_email_processed(
            message_id=test_id,
            thread_id="thread_123",
            subject="Test Subject",
            sender="test@example.com"
        )
        
        # Now should be processed
        self.assertTrue(is_email_processed(test_id))
    
    def tearDown(self):
        """Clean up test data."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM processed_emails WHERE message_id LIKE 'test_%'")
        c.execute("DELETE FROM processed_emails WHERE message_id LIKE 'unique_%'")
        conn.commit()
        conn.close()


class TestGmailParsing(unittest.TestCase):
    """Test Gmail API response parsing."""
    
    def test_parse_empty_response(self):
        """Empty response should return empty list."""
        result = parse_gmail_response({})
        self.assertEqual(result, [])
    
    def test_parse_no_messages(self):
        """Response with no messages should return empty list."""
        result = parse_gmail_response({"messages": []})
        self.assertEqual(result, [])
    
    def test_parse_single_message(self):
        """Should parse a single message correctly."""
        gmail_response = {
            "messages": [{
                "id": "msg_123",
                "threadId": "thread_456",
                "snippet": "This is a test email about the deal",
                "payload": {
                    "headers": [
                        {"name": "Subject", "value": "Re: Partnership Discussion"},
                        {"name": "From", "value": "alice@company.com"},
                        {"name": "Date", "value": "Mon, 15 Jan 2026 10:30:00 -0500"}
                    ]
                }
            }]
        }
        
        results = parse_gmail_response(gmail_response)
        self.assertEqual(len(results), 1)
        
        email = results[0]
        self.assertEqual(email.message_id, "msg_123")
        self.assertEqual(email.thread_id, "thread_456")
        self.assertEqual(email.subject, "Re: Partnership Discussion")
        self.assertEqual(email.sender, "alice@company.com")
        self.assertIn("test email about the deal", email.snippet)
    
    def test_parse_multiple_messages(self):
        """Should parse multiple messages."""
        gmail_response = {
            "messages": [
                {
                    "id": "msg_1",
                    "threadId": "thread_1",
                    "snippet": "First email",
                    "payload": {"headers": [
                        {"name": "Subject", "value": "Subject 1"},
                        {"name": "From", "value": "a@test.com"}
                    ]}
                },
                {
                    "id": "msg_2",
                    "threadId": "thread_2",
                    "snippet": "Second email",
                    "payload": {"headers": [
                        {"name": "Subject", "value": "Subject 2"},
                        {"name": "From", "value": "b@test.com"}
                    ]}
                }
            ]
        }
        
        results = parse_gmail_response(gmail_response)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].message_id, "msg_1")
        self.assertEqual(results[1].message_id, "msg_2")
    
    def test_parse_with_text_payload(self):
        """Should capture textPayload if present."""
        gmail_response = {
            "messages": [{
                "id": "msg_with_body",
                "threadId": "thread_body",
                "snippet": "Preview text",
                "textPayload": "Full email body content here...",
                "payload": {"headers": [
                    {"name": "Subject", "value": "Full Body Test"},
                    {"name": "From", "value": "test@test.com"}
                ]}
            }]
        }
        
        results = parse_gmail_response(gmail_response)
        self.assertEqual(results[0].body_preview, "Full email body content here...")


class TestEmailProcessing(unittest.TestCase):
    """Test email processing through signal router."""
    
    def test_process_already_processed_email(self):
        """Should skip already processed emails."""
        # First, mark an email as processed
        test_id = f"processed_test_{datetime.now().timestamp()}"
        mark_email_processed(message_id=test_id)
        
        email = EmailResult(
            message_id=test_id,
            thread_id="thread_x",
            subject="Test",
            sender="test@test.com",
            snippet="Test content",
            date="2026-01-18"
        )
        
        result = process_email(email, dry_run=True)
        self.assertFalse(result.matched)
        self.assertEqual(result.extraction_summary, "Already processed")
        
        # Clean up
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM processed_emails WHERE message_id = ?", (test_id,))
        conn.commit()
        conn.close()
    
    def test_process_new_email_dry_run(self):
        """Should process new email in dry run mode without DB writes."""
        email = EmailResult(
            message_id=f"new_email_{datetime.now().timestamp()}",
            thread_id="thread_new",
            subject="Exciting Partnership Opportunity",
            sender="partner@darwinbox.com",
            snippet="We're ready to move forward with the integration",
            date="2026-01-18"
        )
        
        context = SearchQuery(
            query="darwinbox",
            context_type="deal",
            context_id="cs-acq-darwinbox",
            context_name="Darwinbox",
            pipeline="careerspan"
        )
        
        result = process_email(email, search_context=context, dry_run=True)
        
        # Should return a valid ScanResult
        self.assertIsInstance(result, ScanResult)
        self.assertEqual(result.email.message_id, email.message_id)


class TestStatistics(unittest.TestCase):
    """Test statistics tracking."""
    
    def test_get_stats_structure(self):
        """Stats should return expected structure."""
        stats = get_scan_stats()
        
        self.assertIn("total_processed", stats)
        self.assertIn("with_signals", stats)
        self.assertIn("unique_deals", stats)
        self.assertIn("daily_counts", stats)
        
        self.assertIsInstance(stats["total_processed"], int)
        self.assertIsInstance(stats["with_signals"], int)
        self.assertIsInstance(stats["unique_deals"], int)
        self.assertIsInstance(stats["daily_counts"], list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
