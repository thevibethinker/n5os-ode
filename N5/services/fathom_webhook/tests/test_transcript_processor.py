import pytest
import json
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fireflies_webhook.transcript_processor import TranscriptProcessor

@pytest.fixture
def test_db():
    """Create temporary test database"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    # Create schema
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE fireflies_webhooks (
                webhook_id TEXT PRIMARY KEY,
                transcript_id TEXT,
                event_type TEXT,
                received_at TEXT,
                processed_at TEXT,
                status TEXT DEFAULT 'pending',
                error_message TEXT
            )
        """)
        
        # Insert test data
        conn.execute("""
            INSERT INTO fireflies_webhooks (webhook_id, transcript_id, event_type, received_at, status)
            VALUES ('webhook-1', 'transcript-1', 'Transcription completed', '2025-11-15T10:00:00Z', 'pending')
        """)
        conn.commit()
    
    yield db_path
    
    db_path.unlink(missing_ok=True)

@pytest.fixture
def test_inbox(tmp_path):
    """Create temporary inbox directory"""
    inbox = tmp_path / "Inbox"
    inbox.mkdir()
    return inbox

def test_generate_meeting_folder_path(test_db, test_inbox):
    """Test meeting folder path generation"""
    processor = TranscriptProcessor(api_key="test-key", db_path=test_db)
    processor.inbox_base = test_inbox
    
    fireflies_data = {
        "date": "2025-11-15T14:30:00Z",
        "title": "Test Meeting: Project Update"
    }
    
    folder_path = processor._generate_meeting_folder_path(fireflies_data)
    
    assert folder_path.exists()
    assert folder_path.is_dir()
    assert "2025-11-15" in folder_path.name
    assert "Test Meeting" in folder_path.name

def test_save_transcript(test_db, test_inbox):
    """Test transcript saving"""
    processor = TranscriptProcessor(api_key="test-key", db_path=test_db)
    processor.inbox_base = test_inbox
    
    meeting_folder = test_inbox / "2025-11-15_Test"
    meeting_folder.mkdir()
    
    zo_transcript = {
        "text": "Hello world",
        "utterances": [{"speaker": "John", "start": 0, "end": 2000, "text": "Hello world"}],
        "fireflies_title": "Test Meeting",
        "fireflies_id": "test-123"
    }
    
    transcript_path = processor._save_transcript(meeting_folder, zo_transcript)
    
    assert transcript_path is not None
    assert transcript_path.exists()
    assert transcript_path.suffix == ".jsonl"
    
    # Verify content
    with open(transcript_path, 'r') as f:
        saved_data = json.load(f)
    
    assert saved_data["text"] == "Hello world"
    assert saved_data["fireflies_id"] == "test-123"

def test_get_pending_webhooks(test_db):
    """Test fetching pending webhooks"""
    processor = TranscriptProcessor(api_key="test-key", db_path=test_db)
    
    pending = processor._get_pending_webhooks(limit=10)
    
    assert len(pending) == 1
    assert pending[0]["webhook_id"] == "webhook-1"
    assert pending[0]["transcript_id"] == "transcript-1"
    assert pending[0]["status"] == "pending"

def test_mark_completed(test_db):
    """Test marking webhook as completed"""
    processor = TranscriptProcessor(api_key="test-key", db_path=test_db)
    
    processor._mark_completed("webhook-1", "/path/to/transcript.jsonl")
    
    with sqlite3.connect(test_db) as conn:
        cursor = conn.execute("SELECT status, error_message FROM fireflies_webhooks WHERE webhook_id = 'webhook-1'")
        row = cursor.fetchone()
    
    assert row[0] == "completed"
    assert "/path/to/transcript.jsonl" in row[1]

def test_mark_failed(test_db):
    """Test marking webhook as failed"""
    processor = TranscriptProcessor(api_key="test-key", db_path=test_db)
    
    processor._mark_failed("webhook-1", "API error")
    
    with sqlite3.connect(test_db) as conn:
        cursor = conn.execute("SELECT status, error_message FROM fireflies_webhooks WHERE webhook_id = 'webhook-1'")
        row = cursor.fetchone()
    
    assert row[0] == "failed"
    assert row[1] == "API error"

