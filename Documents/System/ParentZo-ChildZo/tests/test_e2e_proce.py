#!/usr/bin/env python3
"""
E2E Tests for ParentZo-ChildZo Message Processing
Test IDs: E2E-001 through E2E-007
"""
import pytest
import json
import time
from pathlib import Path
from typing import Dict, List
from .test_helpers import MetricsChecker, LogValidator, MessagePublisher, DLQManager


@pytest.mark.e2e_proce
class TestE2EProcessing:
    """End-to-end processing tests with idempotency, retries, DLQ, and visibility."""

    @pytest.fixture(autouse=True)
    def setup(self, metrics_checker, log_validator, message_publisher, dlq_manager):
        """Setup test dependencies."""
        self.metrics = metrics_checker
        self.logs = log_validator
        self.publisher = message_publisher
        self.dlq = dlq_manager
        
        # Reset metrics baseline before each test
        self.metrics.reset_baseline()
        self.logs.clear()
        
        yield
        
        # Cleanup after test
        self.publisher.purge_all()
        self.dlq.purge()

    def test_e2e_001_happy_path_current_and_n1_schema(self, fixtures_dir):
        """
        E2E-001: Happy path (current + N-1 schema)
        
        Given: producer publishes valid_current.json and valid_n1.json
        When: consumer processes messages
        Then:
          - Exactly one successful effect per message (idempotent apply)
          - [MI: processed_success_total += 2]
          - [LG: level=info event=processed message_id=<id> schema_version in {current, n-1}]
          - No DLQ entries [MI: dlq_total unchanged]
        """
        # Arrange
        current_msg = json.loads((fixtures_dir / "valid_current.json").read_text())
        n1_msg = json.loads((fixtures_dir / "valid_n1.json").read_text())
        
        # Act
        msg_id_1 = self.publisher.publish(current_msg)
        msg_id_2 = self.publisher.publish(n1_msg)
        
        # Wait for processing
        time.sleep(2)
        
        # Assert
        assert self.metrics.get_delta("processed_success_total") == 2, \
            "Expected 2 successful processings"
        
        assert self.logs.contains_event("processed", message_id=msg_id_1, level="info")
        assert self.logs.contains_event("processed", message_id=msg_id_2, level="info")
        
        assert self.metrics.get_delta("dlq_total") == 0, \
            "No DLQ entries expected"

    def test_e2e_002_duplicate_delivery_suppression(self, fixtures_dir):
        """
        E2E-002: Duplicate delivery (same message_id)
        
        Given: two messages with identical message_id and payload
        When: both are delivered (in any order)
        Then:
          - Exactly one effect applied [MI: processed_success_total += 1]
          - Second delivery suppressed [MI: duplicates_suppressed_total += 1]
          - [LG: event=duplicate_suppressed message_id=<id>]
        """
        # Arrange
        msg = json.loads((fixtures_dir / "valid_current.json").read_text())
        
        # Act - publish same message twice
        msg_id = self.publisher.publish(msg)
        self.publisher.publish(msg, force_message_id=msg_id)  # Same ID
        
        time.sleep(2)
        
        # Assert
        assert self.metrics.get_delta("processed_success_total") == 1, \
            "Only one successful processing expected"
        
        assert self.metrics.get_delta("duplicates_suppressed_total") == 1, \
            "One duplicate should be suppressed"
        
        assert self.logs.contains_event("duplicate_suppressed", message_id=msg_id)

    def test_e2e_003_transient_failure_retries_with_backoff(self, fixtures_dir):
        """
        E2E-003: Transient failure → retries then success
        
        Given: transient_fail.json causes first N attempts to fail
        When: consumer retries with backoff
        Then:
          - [LG: event=retry attempt=1..N backoff_ms within bounds]
          - Final attempt succeeds [MI: processed_success_total += 1]
          - [MI: processed_retry_total += N]
        """
        # Arrange
        msg = json.loads((fixtures_dir / "transient_fail.json").read_text())
        expected_retries = msg.get("_test_config", {}).get("fail_attempts", 3)
        
        # Act
        msg_id = self.publisher.publish(msg)
        
        # Wait for retries + success
        time.sleep(expected_retries * 2 + 2)
        
        # Assert
        assert self.metrics.get_delta("processed_success_total") == 1, \
            "Should eventually succeed"
        
        assert self.metrics.get_delta("processed_retry_total") == expected_retries, \
            f"Expected {expected_retries} retries"
        
        # Verify backoff within bounds
        retry_logs = self.logs.filter_events("retry", message_id=msg_id)
        for log in retry_logs:
            backoff_ms = log.get("backoff_ms", 0)
            assert 100 <= backoff_ms <= 5000, \
                f"Backoff {backoff_ms}ms outside bounds [100, 5000]"

    def test_e2e_004_permanent_failure_to_dlq(self, fixtures_dir):
        """
        E2E-004: Permanent failure → DLQ
        
        Given: permanent_fail.json triggers non-retriable error
        When: processed once
        Then:
          - Message moved to DLQ with reason and metadata [MI: dlq_total += 1]
          - [LG: event=dlq message_id=<id> reason=<code> metadata.contains(...)]
        """
        # Arrange
        msg = json.loads((fixtures_dir / "permanent_fail.json").read_text())
        
        # Act
        msg_id = self.publisher.publish(msg)
        
        time.sleep(2)
        
        # Assert
        assert self.metrics.get_delta("dlq_total") == 1, \
            "One DLQ entry expected"
        
        assert self.metrics.get_delta("processed_success_total") == 0, \
            "No successful processing expected"
        
        dlq_log = self.logs.find_event("dlq", message_id=msg_id)
        assert dlq_log is not None, "DLQ log entry expected"
        assert "reason" in dlq_log, "DLQ log must contain reason"
        assert "metadata" in dlq_log, "DLQ log must contain metadata"
        
        # Verify DLQ message
        dlq_msg = self.dlq.get_message(msg_id)
        assert dlq_msg is not None, "Message should be in DLQ"
        assert "schema_version" in dlq_msg.get("metadata", {})
        assert "first_seen_at" in dlq_msg.get("metadata", {})

    def test_e2e_005_slow_handler_visibility_extension(self, fixtures_dir):
        """
        E2E-005: Slow downstream → visibility extension; no double-processing
        
        Given: handler sleeps > initial_visibility_timeout
        When: processing in-flight
        Then:
          - Visibility extended at least once [MI: visibility_extensions_total += 1]
          - No concurrent second consumer processes same message
        """
        # Arrange
        msg = json.loads((fixtures_dir / "valid_current.json").read_text())
        msg["_test_config"] = {"sleep_seconds": 10}  # Longer than visibility timeout
        
        # Act
        msg_id = self.publisher.publish(msg)
        
        # Wait for processing to complete
        time.sleep(12)
        
        # Assert
        assert self.metrics.get_delta("visibility_extensions_total") >= 1, \
            "At least one visibility extension expected"
        
        assert self.metrics.get_delta("processed_success_total") == 1, \
            "Exactly one successful processing (no double-processing)"
        
        # Verify no duplicate processing logs
        processing_logs = self.logs.filter_events("processed", message_id=msg_id)
        assert len(processing_logs) == 1, \
            "Should only have one processing log (no concurrent processing)"

    def test_e2e_006_restart_mid_flight_safe_reprocessing(self, fixtures_dir, consumer_manager):
        """
        E2E-006: Restart mid-flight → safe reprocessing; no lost ACKs
        
        Given: consumer is terminated mid-processing (SIGTERM)
        When: service restarts
        Then:
          - In-flight message becomes available again after visibility timeout
          - Exactly one final successful effect [MI: processed_success_total += 1]
          - No lost ACKs [LG: event=ack_success appears exactly once]
        """
        # Arrange
        msg = json.loads((fixtures_dir / "valid_current.json").read_text())
        msg["_test_config"] = {"sleep_seconds": 5}
        
        # Act
        msg_id = self.publisher.publish(msg)
        
        # Let processing start
        time.sleep(1)
        
        # Kill consumer mid-processing
        consumer_manager.stop(graceful=False)
        
        # Wait for visibility timeout + restart
        time.sleep(3)
        consumer_manager.start()
        
        # Wait for reprocessing
        time.sleep(7)
        
        # Assert
        assert self.metrics.get_delta("processed_success_total") == 1, \
            "Exactly one successful effect after restart"
        
        ack_logs = self.logs.filter_events("ack_success", message_id=msg_id)
        assert len(ack_logs) == 1, \
            "Exactly one ack_success log expected"

    def test_e2e_007_dlq_replay_idempotent(self, fixtures_dir):
        """
        E2E-007: Replay from DLQ → idempotent re-apply; no duplicates
        
        Given: one message in DLQ (from previous failure)
        When: DLQ replay tool republishes to main topic
        Then:
          - Exactly one effect; no duplicate side-effects
          - [MI: dlq_replayed_total += 1] and [MI: processed_success_total += 1]
          - [LG: event=dlq_replay_success message_id=<id>]
        """
        # Arrange - first cause a DLQ entry
        msg = json.loads((fixtures_dir / "permanent_fail.json").read_text())
        msg_id = self.publisher.publish(msg)
        time.sleep(2)
        
        assert self.dlq.count() == 1, "Setup: message should be in DLQ"
        
        # Fix the message (simulate root cause fix)
        dlq_msg = self.dlq.get_message(msg_id)
        dlq_msg["payload"]["_test_config"] = {"should_fail": False}
        
        # Reset metrics for replay phase
        self.metrics.reset_baseline()
        
        # Act - replay from DLQ
        self.dlq.replay(msg_id)
        
        time.sleep(2)
        
        # Assert
        assert self.metrics.get_delta("dlq_replayed_total") == 1, \
            "One replay expected"
        
        assert self.metrics.get_delta("processed_success_total") == 1, \
            "One successful processing after replay"
        
        assert self.logs.contains_event("dlq_replay_success", message_id=msg_id)
        
        # Verify idempotency - replay again shouldn't duplicate effect
        self.dlq.replay(msg_id)
        time.sleep(2)
        
        assert self.metrics.get_delta("duplicates_suppressed_total") >= 1, \
            "Second replay should be suppressed"


# Test configuration
@pytest.fixture(scope="session")
def fixtures_dir():
    """Return path to test fixtures."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="function")
def metrics_checker():
    """Provide metrics checker utility."""
    return MetricsChecker(endpoint="http://localhost:9090/metrics")


@pytest.fixture(scope="function")
def log_validator():
    """Provide log validator utility."""
    return LogValidator(log_file="/var/log/proce/consumer.log")


@pytest.fixture(scope="function")
def message_publisher():
    """Provide message publisher."""
    return MessagePublisher(queue_url="http://localhost:4566/000000000000/proce-main")


@pytest.fixture(scope="function")
def dlq_manager():
    """Provide DLQ manager."""
    return DLQManager(
        dlq_url="http://localhost:4566/000000000000/proce-dlq",
        main_queue_url="http://localhost:4566/000000000000/proce-main"
    )


@pytest.fixture(scope="function")
def consumer_manager():
    """Provide consumer process manager."""
    from .test_helpers import ConsumerManager
    return ConsumerManager(
        start_cmd="python3 Documents/System/ParentZo-ChildZo/scripts/consumer.py",
        health_check_url="http://localhost:8080/health"
    )
