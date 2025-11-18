import pytest
import sqlite3
import json
from pathlib import Path
import tempfile

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fireflies_webhook.webhook_processor import WebhookProcessor
from fireflies_webhook.models import FirefliesWebhookPayload
from fireflies_webhook.config import Config

@pytest.fixture
def test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    yield db_path
    
    db_path.unlink(missing_ok=True)

@pytest.fixture
def processor(test_db):
    return WebhookProcessor(db_path=test_db)

def test_ensure_schema(processor):
    with sqlite3.connect(processor.db_path) as conn:
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='fireflies_webhooks'
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        assert "fireflies_webhooks" in tables

def test_log_webhook(processor):
    payload = FirefliesWebhookPayload(
        meetingId="test-123",
        eventType="Transcription completed",
        clientReferenceId="ref-456"
    )
    
    webhook_id = "webhook-test-001"
    raw_payload = json.dumps(payload.model_dump())
    
    success = processor.log_webhook(webhook_id, payload, raw_payload)
    assert success
    
    with sqlite3.connect(processor.db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM fireflies_webhooks WHERE webhook_id = ?",
            (webhook_id,)
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == "Transcription completed"
        assert row[2] == "test-123"

def test_get_pending_webhooks(processor):
    payload1 = FirefliesWebhookPayload(
        meetingId="meeting-1",
        eventType="Transcription completed"
    )
    
    payload2 = FirefliesWebhookPayload(
        meetingId="meeting-2",
        eventType="Transcription completed"
    )
    
    processor.log_webhook("webhook-1", payload1, json.dumps(payload1.model_dump()))
    processor.log_webhook("webhook-2", payload2, json.dumps(payload2.model_dump()))
    
    pending = processor.get_pending_webhooks()
    assert len(pending) == 2
    assert all(w["status"] == "pending" for w in pending)

def test_update_webhook_status(processor):
    payload = FirefliesWebhookPayload(
        meetingId="meeting-3",
        eventType="Transcription completed"
    )
    
    webhook_id = "webhook-3"
    processor.log_webhook(webhook_id, payload, json.dumps(payload.model_dump()))
    
    success = processor.update_webhook_status(webhook_id, "completed")
    assert success
    
    with sqlite3.connect(processor.db_path) as conn:
        cursor = conn.execute(
            "SELECT status, processed_at FROM fireflies_webhooks WHERE webhook_id = ?",
            (webhook_id,)
        )
        row = cursor.fetchone()
        assert row[0] == "completed"
        assert row[1] is not None

def test_update_webhook_status_with_error(processor):
    payload = FirefliesWebhookPayload(
        meetingId="meeting-4",
        eventType="Transcription completed"
    )
    
    webhook_id = "webhook-4"
    processor.log_webhook(webhook_id, payload, json.dumps(payload.model_dump()))
    
    success = processor.update_webhook_status(
        webhook_id, 
        "failed", 
        "Test error message"
    )
    assert success
    
    with sqlite3.connect(processor.db_path) as conn:
        cursor = conn.execute(
            "SELECT status, error_message FROM fireflies_webhooks WHERE webhook_id = ?",
            (webhook_id,)
        )
        row = cursor.fetchone()
        assert row[0] == "failed"
        assert row[1] == "Test error message"

def test_verify_hmac_signature_no_secret(processor):
    Config.WEBHOOK_SECRET = ""
    is_valid = processor.verify_hmac_signature("payload", None)
    assert is_valid

def test_verify_hmac_signature_valid(processor):
    import hmac
    import hashlib
    
    Config.WEBHOOK_SECRET = "test-secret"
    payload = "test payload"
    
    signature = hmac.new(
        Config.WEBHOOK_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    is_valid = processor.verify_hmac_signature(payload, f"sha256={signature}")
    assert is_valid
    
    Config.WEBHOOK_SECRET = ""

def test_verify_hmac_signature_invalid(processor):
    Config.WEBHOOK_SECRET = "test-secret"
    
    is_valid = processor.verify_hmac_signature("payload", "sha256=invalid")
    assert not is_valid
    
    Config.WEBHOOK_SECRET = ""




