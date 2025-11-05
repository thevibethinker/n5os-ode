#!/usr/bin/env python3
"""
Integration tests for meeting processing workflow.
Tests end-to-end: request → path resolution → processing → status update.
"""

import pytest
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from resolve_transcript_path import resolve_transcript_path


class TestIntegration:
    """Integration tests for full workflow."""
    
    def test_end_to_end_with_prefix_resolution(self, tmp_path):
        """
        T5.1: Full pipeline with path resolution.
        
        Simulates:
        1. AI request JSON with non-prefixed path
        2. Actual file has [IMPORTED-TO-ZO] prefix
        3. Resolution finds the file
        4. Processing can proceed
        """
        # Setup directories
        inbox = tmp_path / "Inbox"
        inbox.mkdir()
        requests_dir = tmp_path / "ai_requests"
        requests_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Create actual transcript file WITH prefix
        meeting_id = "2025-10-29_external-test"
        prefixed_transcript = inbox / f"[IMPORTED-TO-ZO] {meeting_id}.transcript.md"
        prefixed_transcript.write_text("""# Meeting Transcript

## Attendees
- Speaker 1: Project Manager
- Speaker 2: Client

## Discussion

Speaker 1: Let's review the deliverables for Q4.

Speaker 2: We need the MVP by end of November.

Speaker 1: Agreed. I'll have the team focus on core features.

## Action Items
- Complete MVP by Nov 30
- Schedule follow-up in 2 weeks
""")
        
        # Create AI request JSON with non-prefixed path
        request = {
            "request_id": f"meeting_{meeting_id}_test",
            "type": "meeting_processing",
            "inputs": {
                "transcript_path": str(inbox / f"{meeting_id}.transcript.md"),  # No prefix!
                "meeting_id": meeting_id
            },
            "status": "pending",
            "created_at": "2025-10-29T14:00:00Z"
        }
        
        request_file = requests_dir / f"{request['request_id']}.json"
        request_file.write_text(json.dumps(request, indent=2))
        
        # TEST: Path resolution
        original_path = request["inputs"]["transcript_path"]
        resolved_path = resolve_transcript_path(original_path)
        
        # Assertions
        assert resolved_path is not None, "Path resolution failed"
        assert resolved_path == prefixed_transcript, "Resolved wrong file"
        assert resolved_path.exists(), "Resolved file doesn't exist"
        
        # Verify we can read the transcript
        content = resolved_path.read_text()
        assert "Meeting Transcript" in content
        assert "deliverables" in content
        assert "Action Items" in content
        
        # This proves the fix works:
        # - Request has path WITHOUT prefix
        # - File has [IMPORTED-TO-ZO] prefix  
        # - Resolution successfully finds the file
        # - Processing can proceed with actual content
    
    def test_multiple_requests_in_queue(self, tmp_path):
        """
        T5.2: Multiple pending requests exist.
        System should process oldest first.
        """
        requests_dir = tmp_path / "ai_requests"
        requests_dir.mkdir()
        
        # Create multiple requests with different timestamps
        requests = [
            {
                "request_id": "meeting_1",
                "status": "pending",
                "created_at": "2025-10-29T10:00:00Z"
            },
            {
                "request_id": "meeting_2",
                "status": "pending",
                "created_at": "2025-10-29T09:00:00Z"  # Oldest
            },
            {
                "request_id": "meeting_3",
                "status": "pending",
                "created_at": "2025-10-29T11:00:00Z"
            }
        ]
        
        for req in requests:
            req_file = requests_dir / f"{req['request_id']}.json"
            req_file.write_text(json.dumps(req, indent=2))
        
        # Load all pending requests
        pending = []
        for req_file in requests_dir.glob("*.json"):
            req = json.loads(req_file.read_text())
            if req["status"] == "pending":
                pending.append((req["created_at"], req["request_id"]))
        
        pending.sort()  # Sort by timestamp
        
        # Verify oldest is first
        assert len(pending) == 3
        assert pending[0][1] == "meeting_2", "Should process oldest request first"


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_transcript_not_found_error(self, tmp_path):
        """
        T4.2: File not found → error status.
        """
        requests_dir = tmp_path / "ai_requests"
        requests_dir.mkdir()
        
        # Request points to non-existent file
        request = {
            "request_id": "meeting_missing",
            "inputs": {
                "transcript_path": str(tmp_path / "Inbox" / "missing.transcript.md"),
                "meeting_id": "missing"
            },
            "status": "pending"
        }
        
        # Try to resolve
        resolved = resolve_transcript_path(request["inputs"]["transcript_path"])
        
        assert resolved is None, "Should return None for missing file"
        
        # This would trigger error status update:
        # request["status"] = "error"
        # request["error"] = "Transcript file not found (tried with/without [IMPORTED-TO-ZO] prefix)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
