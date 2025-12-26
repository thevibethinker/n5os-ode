import pytest
import json
import hmac
import hashlib
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import sqlite3

from fireflies_webhook.webhook_receiver import app
from fireflies_webhook.config import Config

@pytest.fixture
def test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    original_db = Config.DATABASE_PATH
    Config.DATABASE_PATH = db_path
    
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fireflies_webhooks (
                webhook_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                transcript_id TEXT NOT NULL,
                received_at TEXT NOT NULL,
                processed_at TEXT,
                status TEXT DEFAULT 'pending',
                payload TEXT,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    
    yield db_path
    
    Config.DATABASE_PATH = original_db
    db_path.unlink(missing_ok=True)

@pytest.fixture
def client(test_db):
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "fireflies_webhook"
    assert "timestamp" in data

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["service"] == "Fireflies Webhook Receiver"
    assert data["status"] == "running"

def test_webhook_valid_payload(client):
    payload = {
        "meetingId": "test-meeting-123",
        "eventType": "Transcription completed",
        "clientReferenceId": "test-ref"
    }
    
    response = client.post(
        "/webhook/fireflies",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"
    assert "webhook_id" in data

def test_webhook_missing_required_field(client):
    payload = {
        "eventType": "Transcription completed"
    }
    
    response = client.post(
        "/webhook/fireflies",
        json=payload
    )
    
    assert response.status_code == 400

def test_webhook_malformed_json(client):
    response = client.post(
        "/webhook/fireflies",
        data="not-valid-json",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 400

def test_webhook_hmac_verification_with_secret(client):
    Config.WEBHOOK_SECRET = "test-secret"
    
    payload = {
        "meetingId": "test-meeting-456",
        "eventType": "Transcription completed"
    }
    
    payload_str = json.dumps(payload)
    signature = hmac.new(
        Config.WEBHOOK_SECRET.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    response = client.post(
        "/webhook/fireflies",
        data=payload_str,
        headers={
            "Content-Type": "application/json",
            "X-Fireflies-Signature": f"sha256={signature}"
        }
    )
    
    assert response.status_code == 200
    
    Config.WEBHOOK_SECRET = ""

def test_webhook_hmac_verification_invalid_signature(client):
    Config.WEBHOOK_SECRET = "test-secret"
    
    payload = {
        "meetingId": "test-meeting-789",
        "eventType": "Transcription completed"
    }
    
    response = client.post(
        "/webhook/fireflies",
        json=payload,
        headers={"X-Fireflies-Signature": "sha256=invalid-signature"}
    )
    
    assert response.status_code == 401
    
    Config.WEBHOOK_SECRET = ""

def test_webhook_too_large(client):
    large_payload = {
        "meetingId": "test",
        "eventType": "Transcription completed",
        "data": "x" * (Config.MAX_REQUEST_SIZE_BYTES + 1)
    }
    
    response = client.post(
        "/webhook/fireflies",
        json=large_payload
    )
    
    assert response.status_code == 413



