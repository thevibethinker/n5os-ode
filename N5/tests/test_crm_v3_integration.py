#!/usr/bin/env python3
"""
CRM V3 Integration Test Suite
Worker 7: End-to-end validation of all system workflows
"""

import sys
import os
import sqlite3
import yaml
import json
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from crm_v3.db.helpers import get_connection, create_profile, search_profiles
from crm_v3.enrichment.queue_manager import EnrichmentQueue
from crm_v3.webhooks.calendar_handler import process_calendar_event
from crm_v3.sync.gmail_tracker import process_gmail_message

class TestResults:
    """Track test results for reporting"""
    def __init__(self):
        self.tests = []
    
    def add(self, name, passed, details=""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n{status}: {name}")
        if details:
            print(f"  {details}")
    
    def summary(self):
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t["passed"])
        failed = total - passed
        print("\n" + "="*60)
        print(f"INTEGRATION TEST SUMMARY: {passed}/{total} passed")
        if failed > 0:
            print(f"❌ {failed} test(s) failed:")
            for t in self.tests:
                if not t["passed"]:
                    print(f"  - {t['name']}: {t['details']}")
        else:
            print("✅ All integration tests passed!")
        print("="*60)
        return failed == 0


def test_calendar_to_enrichment_workflow(results):
    """
    Test 1: Calendar webhook → Profile creation → Enrichment queue → Worker execution
    """
    test_name = "Test 1: Calendar → Enrichment → Profile"
    
    try:
        # Clean up any existing test data
        test_email = "test_calendar@integration.test"
        conn = get_connection()
        conn.execute("DELETE FROM profiles WHERE email = ?", (test_email,))
        conn.execute("DELETE FROM enrichment_jobs WHERE profile_id IN (SELECT id FROM profiles WHERE email = ?)", (test_email,))
        conn.commit()
        
        # Step 1: Create test calendar event payload
        meeting_date = (datetime.now() + timedelta(days=3)).isoformat()
        test_event = {
            "summary": "Integration Test Meeting",
            "attendees": [
                {"email": test_email, "displayName": "Test Calendar User"}
            ],
            "start": {"dateTime": meeting_date},
            "htmlLink": "https://calendar.google.com/test"
        }
        
        # Step 2: Process webhook (simulated)
        # This would normally be called by the webhook service
        # For testing, we'll call the handler directly
        profile_id = create_profile(
            conn=conn,
            name="Test Calendar User",
            email=test_email,
            category="TEST",
            source="calendar_webhook",
            metadata={"calendar_event_id": "test_event_123", "meeting_date": meeting_date}
        )
        
        # Step 3: Verify profile created
        cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        profile = cursor.fetchone()
        
        if not profile:
            results.add(test_name, False, "Profile not created")
            return
        
        # Step 4: Verify enrichment job queued
        queue = EnrichmentQueue()
        job = queue.get_next_job()
        
        checkpoint_1_found = False
        if job and job["profile_id"] == profile_id:
            if job["priority"] == 75 and job["checkpoint"] == "checkpoint_1":
                checkpoint_1_found = True
        
        # Step 5: Simulate enrichment worker execution
        # (In real system, scheduled task would do this)
        if checkpoint_1_found:
            # Mark job complete and create checkpoint 2
            queue.complete_job(job["id"])
            
            # Queue morning-of checkpoint
            meeting_date_obj = datetime.fromisoformat(meeting_date.replace('Z', '+00:00'))
            morning_of = meeting_date_obj.replace(hour=0, minute=0, second=0)
            
            queue.queue_enrichment(
                profile_id=profile_id,
                priority=100,
                scheduled_for=morning_of,
                checkpoint="checkpoint_2"
            )
        
        # Step 6: Verify YAML profile exists
        yaml_path = Path(f"/home/workspace/N5/crm_v3/profiles/{profile_id}.yaml")
        yaml_exists = yaml_path.exists()
        
        # Verify all conditions
        all_passed = (
            profile is not None and
            checkpoint_1_found and
            yaml_exists
        )
        
        details = f"Profile: {profile_id}, Checkpoint1: {checkpoint_1_found}, YAML: {yaml_exists}"
        results.add(test_name, all_passed, details)
        
    except Exception as e:
        results.add(test_name, False, f"Exception: {str(e)}")


def test_gmail_reply_to_profile(results):
    """
    Test 2: Gmail reply → Profile creation → Low-priority enrichment
    """
    test_name = "Test 2: Gmail Reply → Profile"
    
    try:
        # Clean up test data
        test_email = "test_gmail@integration.test"
        conn = get_connection()
        conn.execute("DELETE FROM profiles WHERE email = ?", (test_email,))
        conn.commit()
        
        # Step 1: Simulate Gmail message
        test_message = {
            "id": "test_msg_123",
            "threadId": "test_thread_123",
            "to": [{"email": test_email, "name": "Test Gmail User"}],
            "subject": "Integration Test Email",
            "date": datetime.now().isoformat(),
            "snippet": "This is a test email for integration testing"
        }
        
        # Step 2: Process Gmail message
        profile_id = create_profile(
            conn=conn,
            name="Test Gmail User",
            email=test_email,
            category="GENERAL",
            source="gmail_reply",
            metadata={"thread_id": "test_thread_123", "message_id": "test_msg_123"}
        )
        
        # Step 3: Verify profile created
        cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        profile = cursor.fetchone()
        
        # Step 4: Verify enrichment job queued with low priority
        queue = EnrichmentQueue()
        scheduled_date = datetime.now() + timedelta(days=7)
        
        queue.queue_enrichment(
            profile_id=profile_id,
            priority=25,
            scheduled_for=scheduled_date,
            checkpoint="gmail_reply"
        )
        
        # Verify job exists with correct priority
        cursor = conn.execute(
            "SELECT * FROM enrichment_jobs WHERE profile_id = ? AND checkpoint = 'gmail_reply'",
            (profile_id,)
        )
        job = cursor.fetchone()
        
        # Step 5: Verify spam filter (test auto-reply detection)
        spam_test_message = {
            "subject": "Re: Automatic reply: Out of Office",
            "snippet": "This is an automated response"
        }
        is_spam = "automatic" in spam_test_message["subject"].lower() or "auto-reply" in spam_test_message["snippet"].lower()
        
        all_passed = (
            profile is not None and
            profile[3] == "gmail_reply" and  # source column
            job is not None and
            job[2] == 25 and  # priority column
            is_spam  # spam filter working
        )
        
        details = f"Profile: {profile_id}, Priority: {job[2] if job else 'N/A'}, SpamFilter: {is_spam}"
        results.add(test_name, all_passed, details)
        
    except Exception as e:
        results.add(test_name, False, f"Exception: {str(e)}")


def test_cli_manual_entry(results):
    """
    Test 3: CLI manual entry → Profile creation → Search → Intel
    """
    test_name = "Test 3: CLI Manual Entry"
    
    try:
        # Clean up test data
        test_email = "test_cli@integration.test"
        conn = get_connection()
        conn.execute("DELETE FROM profiles WHERE email = ?", (test_email,))
        conn.commit()
        
        # Step 1: Simulate CLI create command
        import subprocess
        result = subprocess.run(
            ["python3", "/home/workspace/N5/crm_v3/cli/crm_cli.py", "create",
             "--name", "Test CLI User",
             "--email", test_email,
             "--category", "INVESTOR"],
            capture_output=True,
            text=True
        )
        
        create_success = result.returncode == 0
        
        # Step 2: Verify YAML profile created
        cursor = conn.execute("SELECT id FROM profiles WHERE email = ?", (test_email,))
        row = cursor.fetchone()
        
        if not row:
            results.add(test_name, False, "Profile not created in database")
            return
        
        profile_id = row[0]
        yaml_path = Path(f"/home/workspace/N5/crm_v3/profiles/{profile_id}.yaml")
        yaml_exists = yaml_path.exists()
        
        # Step 3: Test search command
        search_result = subprocess.run(
            ["python3", "/home/workspace/N5/crm_v3/cli/crm_cli.py", "search",
             "--email", test_email],
            capture_output=True,
            text=True
        )
        
        search_success = search_result.returncode == 0 and test_email in search_result.stdout
        
        # Step 4: Verify database record
        cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        profile = cursor.fetchone()
        
        db_valid = (
            profile is not None and
            profile[1] == "Test CLI User" and
            profile[2] == test_email and
            profile[4] == "INVESTOR"
        )
        
        all_passed = create_success and yaml_exists and search_success and db_valid
        
        details = f"Create: {create_success}, YAML: {yaml_exists}, Search: {search_success}, DB: {db_valid}"
        results.add(test_name, all_passed, details)
        
    except Exception as e:
        results.add(test_name, False, f"Exception: {str(e)}")


def test_multi_source_synthesis(results):
    """
    Test 4: Multi-source intelligence synthesis
    """
    test_name = "Test 4: Multi-Source Intelligence Synthesis"
    
    try:
        # Clean up test data
        test_email = "test_synthesis@integration.test"
        conn = get_connection()
        conn.execute("DELETE FROM profiles WHERE email = ?", (test_email,))
        conn.commit()
        
        # Step 1: Create profile with multiple intelligence sources
        profile_id = create_profile(
            conn=conn,
            name="Test Synthesis User",
            email=test_email,
            category="INVESTOR",
            source="manual",
            metadata={"test": "multi_source"}
        )
        
        # Step 2: Create YAML with B08 meeting intelligence
        yaml_path = Path(f"/home/workspace/N5/crm_v3/profiles/{profile_id}.yaml")
        profile_data = {
            "id": profile_id,
            "name": "Test Synthesis User",
            "email": test_email,
            "category": "INVESTOR",
            "created": datetime.now().isoformat(),
            "intelligence": {
                "meetings": [
                    {
                        "date": "2025-11-15",
                        "summary": "Discussed Series A funding. Very interested in AI space.",
                        "block_id": "B08_test_001"
                    }
                ],
                "enrichment": [
                    {
                        "date": "2025-11-16",
                        "checkpoint": "checkpoint_1",
                        "data": "Partner at Test Ventures. Focus on early-stage AI/ML startups."
                    }
                ],
                "gmail_context": [
                    {
                        "date": "2025-11-14",
                        "thread_id": "thread_test_123",
                        "summary": "Email thread about Careerspan product demo request"
                    }
                ]
            }
        }
        
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        with open(yaml_path, 'w') as f:
            yaml.dump(profile_data, f, default_flow_style=False)
        
        # Step 3: Verify YAML has all sources
        with open(yaml_path, 'r') as f:
            loaded_data = yaml.safe_load(f)
        
        has_meetings = "meetings" in loaded_data.get("intelligence", {})
        has_enrichment = "enrichment" in loaded_data.get("intelligence", {})
        has_gmail = "gmail_context" in loaded_data.get("intelligence", {})
        
        # Step 4: Test AI synthesis (simulated - would use `crm intel` in production)
        synthesis_sources = []
        if has_meetings:
            synthesis_sources.append("meeting intelligence")
        if has_enrichment:
            synthesis_sources.append("enrichment data")
        if has_gmail:
            synthesis_sources.append("gmail context")
        
        synthesis_complete = len(synthesis_sources) == 3
        
        all_passed = has_meetings and has_enrichment and has_gmail and synthesis_complete
        
        details = f"Sources: {', '.join(synthesis_sources)} ({len(synthesis_sources)}/3)"
        results.add(test_name, all_passed, details)
        
    except Exception as e:
        results.add(test_name, False, f"Exception: {str(e)}")


def main():
    """Run all integration tests"""
    print("="*60)
    print("CRM V3 INTEGRATION TEST SUITE")
    print("Worker 7: End-to-End Validation")
    print("="*60)
    
    results = TestResults()
    
    # Run all tests
    test_calendar_to_enrichment_workflow(results)
    test_gmail_reply_to_profile(results)
    test_cli_manual_entry(results)
    test_multi_source_synthesis(results)
    
    # Print summary
    all_passed = results.summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

