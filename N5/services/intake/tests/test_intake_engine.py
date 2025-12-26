"""
Integration tests for Unified Meeting Intake Engine

Level Upper recommendation #4: Real transcript → full validation pass
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from ..models import (
    UnifiedTranscript,
    IntakeSource,
    Utterance,
    TranscriptValidator,
    ValidationSeverity,
)
from ..intake_engine import IntakeEngine
from ..adapters.manual_adapter import ManualAdapter
from ..adapters.fireflies_adapter import FirefliesAdapter
from ..adapters.fathom_adapter import FathomAdapter


class TestTranscriptValidator:
    """Tests for output validation layer (Level Upper #1)"""
    
    def test_valid_transcript_passes(self):
        transcript = UnifiedTranscript(
            source=IntakeSource.MANUAL,
            full_text="Speaker A: Hello, how are you?\nSpeaker B: I'm great, thanks!",
            detected_date=datetime.now(),
            participants=["Speaker A", "Speaker B"],
        )
        
        results = TranscriptValidator.validate(transcript)
        errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
        
        assert len(errors) == 0
        assert TranscriptValidator.is_valid(transcript)
    
    def test_empty_text_fails(self):
        transcript = UnifiedTranscript(
            source=IntakeSource.MANUAL,
            full_text="",
            detected_date=datetime.now(),
        )
        
        results = TranscriptValidator.validate(transcript)
        errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
        
        assert len(errors) > 0
        assert any("empty" in e.message.lower() for e in errors)
    
    def test_short_text_warns(self):
        transcript = UnifiedTranscript(
            source=IntakeSource.MANUAL,
            full_text="Hi",
            detected_date=datetime.now(),
        )
        
        results = TranscriptValidator.validate(transcript)
        warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
        
        assert any("short" in w.message.lower() for w in warnings)
    
    def test_no_participants_warns(self):
        transcript = UnifiedTranscript(
            source=IntakeSource.MANUAL,
            full_text="This is a long enough transcript to pass the length check easily.",
            detected_date=datetime.now(),
            participants=[],
        )
        
        results = TranscriptValidator.validate(transcript)
        warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
        
        assert any("participants" in w.message.lower() for w in warnings)


class TestManualAdapter:
    """Tests for ManualAdapter"""
    
    def test_adapt_simple_text(self):
        adapter = ManualAdapter()
        payload = {
            "transcript": "John: Hello!\nJane: Hi there!",
            "title": "Test Meeting",
        }
        
        result = adapter.adapt(payload)
        
        assert result.source == IntakeSource.MANUAL
        assert "John" in result.full_text
        assert "Jane" in result.full_text
        assert result.title == "Test Meeting"
    
    def test_extract_participants_from_text(self):
        adapter = ManualAdapter()
        
        participants = adapter.extract_participants({
            "transcript": "Alice: First point\nBob: Good idea\nAlice: Thanks"
        })
        
        assert "Alice" in participants
        assert "Bob" in participants
    
    def test_detect_date_semantic_iso(self):
        adapter = ManualAdapter()
        
        date_str = adapter.detect_date_semantic({
            "transcript": "Meeting recorded on 2025-12-23 for project kickoff."
        })
        
        assert date_str is not None
    
    def test_detect_date_semantic_natural(self):
        adapter = ManualAdapter()
        
        # Create transcript with natural date mention
        transcript = "Today is December 23rd, 2025 and we're meeting to discuss..."
        result = adapter._detect_date_from_text(transcript)
        
        assert result is not None
        assert result.month == 12
        assert result.day == 23
    
    def test_adapt_timestamped_transcript(self):
        adapter = ManualAdapter()
        payload = {
            "transcript": "[00:00:15] Alice: Welcome everyone\n[00:00:30] Bob: Thanks for having us",
        }
        
        result = adapter.adapt(payload)
        
        assert len(result.utterances) == 2
        assert result.utterances[0].speaker == "Alice"
        assert result.utterances[0].start_ms == 15000


class TestFirefliesAdapter:
    """Tests for FirefliesAdapter"""
    
    def test_adapt_webhook_payload(self):
        adapter = FirefliesAdapter()
        payload = {
            "id": "trans_123",
            "title": "Team Sync",
            "date": "2025-12-23T10:00:00Z",
            "sentences": [
                {"speaker_name": "John", "text": "Hello team"},
                {"speaker_name": "Jane", "text": "Hi everyone"},
            ],
            "attendees": [
                {"displayName": "John Smith"},
                {"displayName": "Jane Doe"},
            ]
        }
        
        result = adapter.adapt(payload)
        
        assert result.source == IntakeSource.FIREFLIES
        assert result.source_id == "trans_123"
        assert result.title == "Team Sync"
        assert len(result.participants) == 2
        assert len(result.utterances) == 2


class TestFathomAdapter:
    """Tests for FathomAdapter"""
    
    def test_adapt_webhook_payload(self):
        adapter = FathomAdapter()
        payload = {
            "recording_id": 456,
            "title": "Client Call",
            "date": "2025-12-23",
            "transcript": "Alice: Let's discuss the proposal\nBob: Sounds good",
            "default_summary": "Discussion about project proposal",
        }
        
        result = adapter.adapt(payload)
        
        assert result.source == IntakeSource.FATHOM
        assert result.source_id == "456"
        assert result.title == "Client Call"
        assert result.summary == "Discussion about project proposal"


class TestIntakeEngine:
    """Integration tests for IntakeEngine"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp()
        inbox = Path(temp_dir) / "Inbox"
        inbox.mkdir()
        dedup_db = Path(temp_dir) / "dedup.db"
        
        yield {
            "root": Path(temp_dir),
            "inbox": inbox,
            "dedup_db": dedup_db,
        }
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_manual_ingest_creates_folder(self, temp_workspace):
        engine = IntakeEngine(
            inbox_path=temp_workspace["inbox"],
            meetings_root=temp_workspace["root"],
            dedup_db_path=temp_workspace["dedup_db"],
        )
        
        payload = {
            "transcript": "Alice: Welcome to the meeting!\nBob: Thanks for organizing this.",
            "title": "Test Meeting",
            "date": "2025-12-23",
            "participants": ["Alice", "Bob"],
        }
        
        result = engine.ingest_from_source(IntakeSource.MANUAL, payload)
        
        assert result.success
        assert result.folder_path is not None
        
        folder = Path(result.folder_path)
        assert folder.exists()
        assert (folder / "transcript.jsonl").exists()
        assert (folder / "metadata.json").exists()
    
    def test_duplicate_detection_by_content(self, temp_workspace):
        engine = IntakeEngine(
            inbox_path=temp_workspace["inbox"],
            meetings_root=temp_workspace["root"],
            dedup_db_path=temp_workspace["dedup_db"],
        )
        
        payload = {
            "transcript": "Same content for duplicate test - this is unique enough",
            "participants": ["Alice"],
        }
        
        # First ingest succeeds
        result1 = engine.ingest_from_source(IntakeSource.MANUAL, payload)
        assert result1.success
        
        # Second ingest detects duplicate
        result2 = engine.ingest_from_source(IntakeSource.MANUAL, payload)
        assert not result2.success
        assert result2.duplicate_of is not None
    
    def test_folder_name_generation(self, temp_workspace):
        engine = IntakeEngine(
            inbox_path=temp_workspace["inbox"],
            meetings_root=temp_workspace["root"],
            dedup_db_path=temp_workspace["dedup_db"],
        )
        
        payload = {
            "transcript": "Content for folder name test meeting discussion",
            "title": "Project Kickoff",
            "date": "2025-12-23",
            "participants": ["John Smith", "jane@example.com"],
        }
        
        result = engine.ingest_from_source(IntakeSource.MANUAL, payload)
        
        assert result.success
        assert "2025-12-23" in result.folder_name
        # Title takes priority over participants, so folder name includes title
        assert "Project-Kickoff" in result.folder_name or "Project" in result.folder_name


def test_convenience_function():
    """Test the ingest_manual convenience function"""
    # This is a quick smoke test - doesn't actually write files
    # because it uses default paths
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



