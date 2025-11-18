"""Tests for Phase 2: Transcript Fetcher & Processor"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Set test API key before imports
os.environ["FIREFLIES_API_KEY"] = "test-api-key-for-testing"

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fireflies_webhook.fireflies_client import FirefliesClient
from fireflies_webhook.transcript_processor import TranscriptProcessor

# Sample Fireflies transcript data
SAMPLE_TRANSCRIPT = {
    "id": "test-transcript-001",
    "title": "Team Standup",
    "date": "2025-11-15T09:00:00Z",
    "duration": 1800,  # 30 minutes
    "participants": ["Alice", "Bob", "Charlie"],
    "transcript_url": "https://example.com/transcript",
    "audio_url": "https://example.com/audio.mp3",
    "sentences": [
        {
            "index": 0,
            "text": "Hello everyone, welcome to the standup.",
            "start_time": 0.0,
            "end_time": 3.5,
            "speaker_name": "Alice",
            "speaker_id": "speaker_1"
        },
        {
            "index": 1,
            "text": "Thanks Alice. I'll start with my updates.",
            "start_time": 3.5,
            "end_time": 7.0,
            "speaker_name": "Bob",
            "speaker_id": "speaker_2"
        }
    ],
    "summary": {
        "keywords": ["standup", "updates", "team"],
        "action_items": ["Complete feature X", "Review PR Y"],
        "overview": "Team standup meeting discussing progress"
    }
}

def test_fireflies_client_initialization():
    """Test FirefliesClient can be initialized"""
    with patch('fireflies_webhook.config.Config.get_api_key', return_value="test-key"):
        client = FirefliesClient()
        assert client.api_key == "test-key"

def test_transcript_processor_format_participant_names():
    """Test participant name formatting"""
    with patch('fireflies_webhook.transcript_processor.FirefliesClient'):
        with patch('fireflies_webhook.transcript_processor.WebhookProcessor'):
            processor = TranscriptProcessor()
            
            # Test with list of strings
            names = processor._format_participant_names(["Alice Smith", "Bob Jones"], "Meeting")
            assert "Alice" in names
            assert "Bob" in names
            
            # Test with dict participants
            participants = [
                {"name": "Alice Smith"},
                {"displayName": "Bob Jones"}
            ]
            names = processor._format_participant_names(participants, "Meeting")
            assert "Alice" in names
            assert "Bob" in names
            
            # Test with no participants
            names = processor._format_participant_names([], "Weekly Team Meeting")
            assert len(names) > 0

def test_convert_to_zo_format():
    """Test Fireflies to Zo transcript conversion"""
    with patch('fireflies_webhook.transcript_processor.FirefliesClient'):
        with patch('fireflies_webhook.transcript_processor.WebhookProcessor'):
            processor = TranscriptProcessor()
            
            zo_transcript = processor._convert_to_zo_format(SAMPLE_TRANSCRIPT)
            
            assert "text" in zo_transcript
            assert "utterances" in zo_transcript
            assert "chunks" in zo_transcript
            assert "duration_seconds" in zo_transcript
            
            # Check utterances
            assert len(zo_transcript["utterances"]) == 2
            assert zo_transcript["utterances"][0]["speaker"] == "Alice"
            assert zo_transcript["utterances"][1]["speaker"] == "Bob"
            
            # Check timing is in milliseconds
            assert zo_transcript["utterances"][0]["start"] == 0
            assert zo_transcript["utterances"][0]["end"] == 3500  # 3.5 seconds

def test_group_into_chunks():
    """Test utterance chunking by speaker"""
    with patch('fireflies_webhook.transcript_processor.FirefliesClient'):
        with patch('fireflies_webhook.transcript_processor.WebhookProcessor'):
            processor = TranscriptProcessor()
            
            utterances = [
                {"speaker": "Alice", "start": 0, "end": 1000, "text": "Hello"},
                {"speaker": "Alice", "start": 1000, "end": 2000, "text": "everyone"},
                {"speaker": "Bob", "start": 2000, "end": 3000, "text": "Hi Alice"},
                {"speaker": "Bob", "start": 3000, "end": 4000, "text": "Nice to see you"}
            ]
            
            chunks = processor._group_into_chunks(utterances)
            
            assert len(chunks) == 2
            assert chunks[0]["speaker"] == "Alice"
            assert chunks[0]["text"] == "Hello everyone"
            assert chunks[1]["speaker"] == "Bob"
            assert chunks[1]["text"] == "Hi Alice Nice to see you"

@patch('fireflies_webhook.transcript_processor.FirefliesClient')
@patch('fireflies_webhook.transcript_processor.WebhookProcessor')
def test_save_transcript_to_inbox(mock_webhook_processor, mock_fireflies_client):
    """Test saving transcript to Inbox folder"""
    with tempfile.TemporaryDirectory() as tmpdir:
        inbox_path = Path(tmpdir)
        processor = TranscriptProcessor(inbox_path=inbox_path)
        
        folder_name = processor.save_transcript_to_inbox(SAMPLE_TRANSCRIPT)
        
        assert folder_name is not None
        assert folder_name.startswith("2025-11-15")
        
        # Check files were created
        meeting_folder = inbox_path / folder_name
        assert meeting_folder.exists()
        assert (meeting_folder / "transcript.jsonl").exists()
        assert (meeting_folder / "metadata.json").exists()
        
        # Verify transcript content
        with open(meeting_folder / "transcript.jsonl") as f:
            transcript = json.load(f)
            assert "text" in transcript
            assert "utterances" in transcript
        
        # Verify metadata
        with open(meeting_folder / "metadata.json") as f:
            metadata = json.load(f)
            assert metadata["source"] == "fireflies"
            assert metadata["transcript_id"] == "test-transcript-001"

@patch('fireflies_webhook.transcript_processor.FirefliesClient')
@patch('fireflies_webhook.transcript_processor.WebhookProcessor')
def test_process_pending_webhooks(mock_webhook_processor, mock_fireflies_client):
    """Test processing pending webhooks"""
    # Setup mocks
    mock_webhook_instance = mock_webhook_processor.return_value
    mock_webhook_instance.get_pending_webhooks.return_value = [
        {
            "webhook_id": "webhook-001",
            "transcript_id": "test-transcript-001",
            "status": "pending"
        }
    ]
    
    mock_fireflies_instance = mock_fireflies_client.return_value
    mock_fireflies_instance.get_transcript.return_value = SAMPLE_TRANSCRIPT
    
    with tempfile.TemporaryDirectory() as tmpdir:
        processor = TranscriptProcessor(
            fireflies_client=mock_fireflies_instance,
            webhook_processor=mock_webhook_instance,
            inbox_path=Path(tmpdir)
        )
        
        stats = processor.process_pending_webhooks(limit=10)
        
        assert stats["processed"] == 1
        assert stats["success"] == 1
        assert stats["failed"] == 0
        
        # Verify webhook status was updated
        mock_webhook_instance.update_webhook_status.assert_called()


