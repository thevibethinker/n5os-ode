import pytest
from unittest.mock import Mock, patch
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fireflies_webhook.fireflies_client import FirefliesClient

def test_convert_to_zo_format():
    """Test Fireflies → Zo format conversion"""
    client = FirefliesClient(api_key="test-key")
    
    fireflies_data = {
        "id": "test-transcript-123",
        "title": "Test Meeting",
        "date": "2025-11-15T10:00:00Z",
        "duration": 3600,
        "sentences": [
            {
                "text": "Hello world",
                "speaker_name": "John Doe",
                "start_time": 0.0,
                "end_time": 2.5
            },
            {
                "text": "How are you?",
                "speaker_name": "Jane Smith",
                "start_time": 2.5,
                "end_time": 5.0
            }
        ],
        "participants": ["John Doe", "Jane Smith"],
        "organizer": {"name": "John Doe", "email": "john@example.com"},
        "summary": {"action_items": ["Follow up"], "keywords": ["test"]}
    }
    
    zo_transcript = client.convert_to_zo_format(fireflies_data)
    
    # Verify structure
    assert "text" in zo_transcript
    assert "utterances" in zo_transcript
    assert "fireflies_id" in zo_transcript
    
    # Verify content
    assert zo_transcript["text"] == "Hello world How are you?"
    assert len(zo_transcript["utterances"]) == 2
    assert zo_transcript["utterances"][0]["speaker"] == "John Doe"
    assert zo_transcript["utterances"][0]["start"] == 0
    assert zo_transcript["utterances"][0]["end"] == 2500  # Converted to ms
    assert zo_transcript["fireflies_id"] == "test-transcript-123"
    assert zo_transcript["duration_seconds"] == 3600

def test_convert_empty_sentences():
    """Test conversion with no sentences"""
    client = FirefliesClient(api_key="test-key")
    
    fireflies_data = {
        "id": "test-empty",
        "title": "Empty Meeting",
        "date": "2025-11-15T10:00:00Z",
        "duration": 0,
        "sentences": []
    }
    
    zo_transcript = client.convert_to_zo_format(fireflies_data)
    
    assert zo_transcript["text"] == ""
    assert zo_transcript["utterances"] == []
    assert zo_transcript["fireflies_id"] == "test-empty"

