#!/usr/bin/env python3
"""
Unit tests for B33 pipeline integration.

Run: python3 N5/tests/test_b33_pipeline.py
"""

import json
import sys
import tempfile
from pathlib import Path

WORKSPACE = Path("/home/workspace")
sys.path.insert(0, str(WORKSPACE / "N5/scripts"))

from meeting_b33_hook import should_generate_b33
from generate_b33_edges import extract_meeting_id, extract_jsonl_from_response


def test_should_generate_b33_ready_meeting():
    """Test detection of meetings ready for B33 generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        folder = Path(tmpdir) / "2025-12-26_Test-Meeting_[P]"
        folder.mkdir()
        
        # Create prerequisites
        (folder / "B01_DETAILED_RECAP.md").write_text("# Recap\nTest content")
        (folder / "manifest.json").write_text(json.dumps({
            "blocks_generated": {"stakeholder_intelligence": True}
        }))
        
        assert should_generate_b33(folder) == True
        print("✓ test_should_generate_b33_ready_meeting")


def test_should_generate_b33_missing_b01():
    """Test that meetings without B01 are not eligible."""
    with tempfile.TemporaryDirectory() as tmpdir:
        folder = Path(tmpdir) / "2025-12-26_Test-Meeting_[P]"
        folder.mkdir()
        
        # No B01 file
        (folder / "manifest.json").write_text(json.dumps({
            "blocks_generated": {"stakeholder_intelligence": True}
        }))
        
        assert should_generate_b33(folder) == False
        print("✓ test_should_generate_b33_missing_b01")


def test_should_generate_b33_already_has_b33():
    """Test that meetings with existing B33 are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        folder = Path(tmpdir) / "2025-12-26_Test-Meeting_[P]"
        folder.mkdir()
        
        (folder / "B01_DETAILED_RECAP.md").write_text("# Recap\nTest content")
        (folder / "B33_DECISION_EDGES.jsonl").write_text("{}")
        (folder / "manifest.json").write_text(json.dumps({
            "blocks_generated": {"stakeholder_intelligence": True}
        }))
        
        assert should_generate_b33(folder) == False
        print("✓ test_should_generate_b33_already_has_b33")


def test_extract_meeting_id():
    """Test meeting ID extraction from folder names."""
    p1 = Path("/workspace/2025-12-26_Test-Meeting_[P]")
    assert extract_meeting_id(p1) == "mtg_2025-12-26_Test-Meeting"
    
    p2 = Path("/workspace/2025-12-26_Another-Meeting_[M]")
    assert extract_meeting_id(p2) == "mtg_2025-12-26_Another-Meeting"
    
    p3 = Path("/workspace/2025-12-26_Plain-Meeting")
    assert extract_meeting_id(p3) == "mtg_2025-12-26_Plain-Meeting"
    
    print("✓ test_extract_meeting_id")


def test_extract_jsonl_from_response():
    """Test JSONL extraction from LLM response."""
    # Clean JSONL
    clean = '{"a": 1}\n{"b": 2}'
    assert extract_jsonl_from_response(clean) == '{"a": 1}\n{"b": 2}'
    
    # Markdown fenced
    fenced = '```jsonl\n{"a": 1}\n{"b": 2}\n```'
    assert extract_jsonl_from_response(fenced) == '{"a": 1}\n{"b": 2}'
    
    # Mixed content
    mixed = 'Here are the edges:\n\n{"a": 1}\n\nAnd more:\n{"b": 2}'
    assert extract_jsonl_from_response(mixed) == '{"a": 1}\n{"b": 2}'
    
    print("✓ test_extract_jsonl_from_response")


def test_real_b33_file_structure():
    """Test that real B33 files have expected structure."""
    b33_path = WORKSPACE / "Personal/Meetings/Week-of-2025-12-22/2025-12-26_Careerspan-demo_[P]/B33_DECISION_EDGES.jsonl"
    
    if not b33_path.exists():
        print("⊘ test_real_b33_file_structure (file not found, skipping)")
        return
    
    lines = b33_path.read_text().strip().split('\n')
    
    # First line should be meta
    meta = json.loads(lines[0])
    assert meta.get("_meta") == True
    assert "meeting_id" in meta
    assert "generated_at" in meta
    
    # Remaining lines should be edges
    for line in lines[1:]:
        edge = json.loads(line)
        assert "source_type" in edge
        assert "source_id" in edge
        assert "relation" in edge
        assert "target_type" in edge
        assert "target_id" in edge
        assert "evidence" in edge
    
    print(f"✓ test_real_b33_file_structure ({len(lines)-1} edges)")


if __name__ == "__main__":
    print("=== B33 Pipeline Tests ===\n")
    
    test_should_generate_b33_ready_meeting()
    test_should_generate_b33_missing_b01()
    test_should_generate_b33_already_has_b33()
    test_extract_meeting_id()
    test_extract_jsonl_from_response()
    test_real_b33_file_structure()
    
    print("\n=== All tests passed ===")


