#!/usr/bin/env python3
"""
Test script for D2.1: Beliefs Store + Surprisal Detection
Verifies all acceptance criteria.
"""

import os
import sys
import json
import sqlite3

# Add parent directory to path
sys.path.insert(0, '/home/workspace')

from N5.cognition.belief_store import N5BeliefStore, HITL_THRESHOLD
from N5.cognition.surprisal_detector import SurprisalDetector, SurprisalEvent

DB_PATH = "/home/workspace/N5/cognition/reasoning.db"
SNAPSHOT_PATH = "/home/workspace/N5/cognition/beliefs_snapshot.json"


def test_db_schema():
    """Test 1: Verify reasoning.db exists with correct schema."""
    print("Test: Database Schema...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        required_tables = {'beliefs', 'reasoning_traces', 'review_queue'}
        missing = required_tables - tables

        if missing:
            print(f"  ✗ FAIL: Missing tables: {missing}")
            return False

        # Check indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}

        required_indexes = {
            'idx_beliefs_domain',
            'idx_beliefs_confidence',
            'idx_beliefs_status',
            'idx_review_status',
            'idx_traces_timestamp'
        }
        missing_indexes = required_indexes - indexes

        if missing_indexes:
            print(f"  ✗ FAIL: Missing indexes: {missing_indexes}")
            return False

        # Check belief columns
        cursor.execute("PRAGMA table_info(beliefs)")
        columns = {row[1] for row in cursor.fetchall()}
        required_columns = {
            'id', 'content', 'confidence', 'domain', 'source',
            'evidence_json', 'created_at', 'updated_at',
            'validation_count', 'status'
        }
        missing_columns = required_columns - columns

        if missing_columns:
            print(f"  ✗ FAIL: Missing belief columns: {missing_columns}")
            return False

        conn.close()
        print("  ✓ PASS: Schema correct")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        return False


def test_belief_crud():
    """Test 2: Can add/retrieve/update beliefs via BeliefStore."""
    print("\nTest: Belief CRUD Operations...")
    try:
        store = N5BeliefStore(DB_PATH)

        # Test ADD
        belief_id = store.add_belief(
            content="User prefers dark mode interfaces",
            confidence=0.8,
            domain="preference",
            source="inferred",
            evidence=["block_001", "block_002"]
        )

        if not belief_id:
            print("  ✗ FAIL: Could not add belief")
            return False

        # Test GET
        beliefs = store.get_beliefs(domain="preference")
        if len(beliefs) < 1 or not any(b['id'] == belief_id for b in beliefs):
            print(f"  ✗ FAIL: Could not retrieve belief correctly")
            return False

        # Test GET by ID
        belief = store.get_belief_by_id(belief_id)
        if not belief or belief['content'] != "User prefers dark mode interfaces":
            print("  ✗ FAIL: Could not get belief by ID")
            return False

        # Test UPDATE confidence
        new_conf = store.update_confidence(belief_id, -0.1)
        if not (0.69 <= new_conf <= 0.71):  # 0.8 - 0.1 = 0.7
            print(f"  ✗ FAIL: Confidence update failed. Got {new_conf}")
            return False

        # Verify evidence
        if set(belief['evidence']) != {"block_001", "block_002"}:
            print(f"  ✗ FAIL: Evidence not stored correctly: {belief['evidence']}")
            return False

        store.close()
        print("  ✓ PASS: CRUD operations work")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hitl_queue():
    """Test 3: Low-confidence beliefs (<0.6) auto-queue for review."""
    print("\nTest: HITL Review Queue...")
    try:
        store = N5BeliefStore(DB_PATH)

        # Add high-confidence belief (should NOT queue)
        high_id = store.add_belief(
            content="User is a software engineer",
            confidence=0.9,
            domain="identity",
            source="explicit"
        )

        # Add low-confidence belief (should queue)
        low_id = store.add_belief(
            content="User lives in New York",
            confidence=0.4,
            domain="identity",
            source="inferred"
        )

        # Check review queue
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*), belief_id, reason
            FROM review_queue
            WHERE status = 'pending'
            GROUP BY belief_id
        """)

        queued = cursor.fetchall()

        if len(queued) != 1:
            print(f"  ✗ FAIL: Expected 1 queued item, got {len(queued)}")
            return False

        if queued[0][1] != low_id or queued[0][2] != "low_confidence":
            print(f"  ✗ FAIL: Wrong belief queued or wrong reason: {queued}")
            return False

        conn.close()
        store.close()
        print("  ✓ PASS: Low-confidence beliefs auto-queued")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_surprisal_detection():
    """Test 4: SurprisalDetector correctly triggers on similarity < 0.3."""
    print("\nTest: Surprisal Detection...")
    try:
        detector = SurprisalDetector(threshold=0.3)

        # Test NO RESULTS
        event = detector.detect("What is the meaning of life?", [])
        if not event or event.reason != "no_results":
            print(f"  ✗ FAIL: Should trigger on no results")
            return False

        # Test LOW SIMILARITY
        low_sim_results = [{"score": 0.2, "content": "irrelevant content"}]
        event = detector.detect("complex query", low_sim_results)
        if not event or event.reason != "low_similarity":
            print(f"  ✗ FAIL: Should trigger on low similarity")
            return False

        # Test HIGH SIMILARITY (no surprisal)
        high_sim_results = [{"score": 0.8, "content": "relevant content"}]
        event = detector.detect("similar query", high_sim_results)
        if event is not None:
            print(f"  ✗ FAIL: Should NOT trigger on high similarity")
            return False

        # Test boundary case
        boundary_results = [{"score": 0.3, "content": "borderline"}]
        event = detector.detect("boundary query", boundary_results)
        if event is not None:  # 0.3 is NOT < 0.3
            print(f"  ✗ FAIL: Should NOT trigger at threshold boundary")
            return False

        print("  ✓ PASS: Surprisal detection works correctly")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trace_logging():
    """Test 5: Traces can be logged and queried."""
    print("\nTest: Trace Logging...")
    try:
        detector = SurprisalDetector(db_path=DB_PATH)

        # Log a trace with surprisal
        surprisal_event = SurprisalEvent(
            query="unusual query",
            reason="low_similarity",
            similarity=0.2,
            needs_reasoning=True
        )

        reasoning_result = {
            "decision": "escalate",
            "belief_updates": [
                {"belief_id": "belief_xxx", "delta": +0.1}
            ]
        }

        detector.log_trace(
            query="unusual query",
            results=[{"score": 0.2}],
            surprisal=surprisal_event,
            reasoning_result=reasoning_result
        )

        # Verify trace was logged
        traces = detector.get_recent_traces(limit=10)

        if len(traces) < 1:
            print(f"  ✗ FAIL: Expected at least 1 trace, got {len(traces)}")
            return False

        trace = traces[0]

        if trace['query'] != "unusual query":
            print(f"  ✗ FAIL: Query not logged correctly: {trace['query']}")
            return False

        if not trace['surprisal_triggered']:
            print("  ✗ FAIL: Surprisal flag not set")
            return False

        if trace['top_similarity'] != 0.2:
            print(f"  ✗ FAIL: Similarity not logged: {trace['top_similarity']}")
            return False

        # Check belief updates were parsed
        if not trace['belief_updates'] or len(trace['belief_updates']) != 1:
            print(f"  ✗ FAIL: Belief updates not parsed: {trace['belief_updates']}")
            return False

        detector.close()
        print("  ✓ PASS: Trace logging works")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export_snapshot():
    """Test 6: Export snapshot works."""
    print("\nTest: Export Snapshot...")
    try:
        # Remove existing snapshot
        if os.path.exists(SNAPSHOT_PATH):
            os.remove(SNAPSHOT_PATH)

        store = N5BeliefStore(DB_PATH)

        # Add some beliefs
        store.add_belief(
            content="User likes Python",
            confidence=0.9,
            domain="preference",
            source="explicit"
        )

        store.add_belief(
            content="User works at TechCorp",
            confidence=0.7,
            domain="identity",
            source="inferred"
        )

        # Export
        snapshot = store.export_snapshot(SNAPSHOT_PATH)

        # Verify file exists
        if not os.path.exists(SNAPSHOT_PATH):
            print("  ✗ FAIL: Snapshot file not created")
            return False

        # Load and verify
        with open(SNAPSHOT_PATH, 'r') as f:
            loaded = json.load(f)

        if loaded['count'] < 2:
            print(f"  ✗ FAIL: Expected at least 2 beliefs, got {loaded['count']}")
            return False

        if len(loaded['beliefs']) < 2:
            print(f"  ✗ FAIL: Wrong number of beliefs in snapshot")
            return False

        store.close()
        print("  ✓ PASS: Export snapshot works")
        return True

    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("D2.1: Beliefs Store + Surprisal Detection - Test Suite")
    print("=" * 60)

    results = {
        "db_schema": test_db_schema(),
        "belief_crud": test_belief_crud(),
        "hitl_queue": test_hitl_queue(),
        "surprisal_detection": test_surprisal_detection(),
        "trace_logging": test_trace_logging(),
        "export_snapshot": test_export_snapshot()
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
