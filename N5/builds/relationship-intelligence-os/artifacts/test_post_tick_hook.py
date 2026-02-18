#!/usr/bin/env python3
"""
Test suite for Post-Tick Hook functionality

Tests the promotion processing pipeline end-to-end with sample data.
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
import sys

# Add build artifacts to path
BUILD_DIR = Path(__file__).parent
sys.path.insert(0, str(BUILD_DIR))

from post_tick_hook import PostTickHook
from promotion_cli import PromotionCLI

def create_sample_meeting(temp_dir: Path, meeting_id: str) -> Path:
    """Create a sample meeting folder for testing."""
    
    meeting_folder = temp_dir / meeting_id
    meeting_folder.mkdir()
    
    # Create manifest
    manifest = {
        "manifest_version": "3.0",
        "meeting_id": meeting_id,
        "date": "2026-02-16",
        "participants": [
            {"name": "John Smith", "role": "external", "confidence": 0.95},
            {"name": "V", "role": "host", "confidence": 1.0}
        ],
        "meeting_type": "external",
        "status": "processed",
        "timestamps": {
            "created_at": "2026-02-16T10:30:00Z",
            "processed_at": "2026-02-16T11:15:00Z"
        }
    }
    
    (meeting_folder / "manifest.json").write_text(json.dumps(manifest, indent=2))
    
    # Create sample intelligence blocks
    
    # B02_B05 - Commitments and Actions
    commitments_content = """---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: meeting_processing
---

# Commitments & Actions

## V's Commitments
- [ ] Send partnership proposal by Friday
- [ ] Schedule follow-up meeting with John next week
- [ ] Research John's company background

## John's Commitments
- [x] Review our previous proposal
- [ ] Connect V with his CTO Sarah
- [ ] Provide feedback on timeline requirements

## Mutual Actions
- [ ] Finalize contract terms by end of month
"""
    
    (meeting_folder / "B02_B05_COMMITMENTS_ACTIONS.md").write_text(commitments_content)
    
    # B08 - Stakeholder Intelligence
    stakeholder_content = """---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: meeting_processing
---

# Stakeholder Intelligence

## John Smith - InvestCorp Partner

John demonstrated strong interest in our partnership proposal. His trust level has increased significantly since our last interaction. He's now positioned as a key advocate within InvestCorp and has the authority to make partnership decisions.

Key relationship insights:
- Built stronger rapport through shared interests in sustainable tech
- John appreciates our transparent communication style
- He has influence over technical decisions at InvestCorp

## Sarah Chen - InvestCorp CTO

John mentioned Sarah as the technical decision-maker. She will be critical for technical approval of our partnership.
"""
    
    (meeting_folder / "B08_STAKEHOLDER_INTELLIGENCE.md").write_text(stakeholder_content)
    
    # B06 - Business Context
    business_content = """---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: meeting_processing
---

# Business Context

## InvestCorp Strategic Priorities

InvestCorp is focusing heavily on sustainable technology investments this quarter. They have allocated $50M for new partnerships and are looking for innovative solutions in the cleantech space.

The company is undergoing organizational changes:
- New focus on environmental impact metrics
- Streamlined decision-making processes
- Emphasis on long-term partnerships over transactional relationships

## Market Context

The sustainable tech market is experiencing significant growth, with regulatory pressures driving increased investment.
"""
    
    (meeting_folder / "B06_BUSINESS_CONTEXT.md").write_text(business_content)
    
    return meeting_folder


def test_basic_promotion_processing():
    """Test basic promotion processing on sample meeting."""
    
    print("=== Test: Basic Promotion Processing ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample meeting
        meeting_folder = create_sample_meeting(temp_path, "2026-02-16_John-Smith-Partnership")
        
        # Create hook and process
        hook = PostTickHook()
        result = hook.process_single_meeting(meeting_folder, dry_run=True)
        
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Verify results
        assert result['meeting_id'] == "2026-02-16_John-Smith-Partnership"
        assert result['status'] == 'dry_run_completed'
        assert result['promoted_events'] > 0
        
        print("✅ Basic promotion processing test passed")


def test_idempotency():
    """Test idempotency - processing same meeting multiple times."""
    
    print("\n=== Test: Idempotency ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample meeting
        meeting_folder = create_sample_meeting(temp_path, "2026-02-16_Idempotency-Test")
        
        hook = PostTickHook()
        
        # Process first time
        result1 = hook.process_single_meeting(meeting_folder, dry_run=False)
        print(f"First run: {result1['status']}, events: {result1['promoted_events']}")
        
        # Process second time - should be skipped due to idempotency
        result2 = hook.process_single_meeting(meeting_folder, dry_run=False)
        print(f"Second run: {result2['status']}")
        
        # Verify second run was skipped
        assert result2['status'] == 'already_processed'
        
        print("✅ Idempotency test passed")


def test_promotion_gate_integration():
    """Test integration with promotion gate engine."""
    
    print("\n=== Test: Promotion Gate Integration ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create meeting with high-value content that should promote
        meeting_folder = create_sample_meeting(temp_path, "2026-02-16_High-Value-Meeting")
        
        # Add more strategic content to increase promotion likelihood
        strategic_content = """---
created: 2026-02-16
last_edited: 2026-02-16
version: 1.0
provenance: meeting_processing
---

# Strategic Intelligence

## Key Strategic Decision

John committed to a $2M partnership investment, pending technical approval. This represents InvestCorp's largest cleantech partnership to date.

Critical timeline:
- Technical review: 2 weeks
- Executive approval: 1 week following technical sign-off
- Contract execution: End of quarter

## Competitive Advantage

Our solution offers unique advantages:
- 40% cost reduction over competitors
- Proven sustainability metrics
- Strong regulatory compliance
"""
        
        (meeting_folder / "B28_STRATEGIC_INTELLIGENCE.md").write_text(strategic_content)
        
        # Process through promotion pipeline
        hook = PostTickHook()
        result = hook.process_single_meeting(meeting_folder, dry_run=True)
        
        print(f"Strategic meeting result: {json.dumps(result, indent=2)}")
        
        # Should have high promotion potential
        assert result['promoted_events'] > 0
        
        print("✅ Promotion gate integration test passed")


def test_cli_interface():
    """Test CLI interface functionality."""
    
    print("\n=== Test: CLI Interface ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample meetings
        meeting1 = create_sample_meeting(temp_path, "2026-02-16_CLI-Test-Meeting-1")
        meeting2 = create_sample_meeting(temp_path, "2026-02-16_CLI-Test-Meeting-2")
        
        cli = PromotionCLI()
        
        # Create mock args for processing
        class MockArgs:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        
        args = MockArgs(
            meetings=[str(meeting1), str(meeting2)],
            dry_run=True,
            json=False
        )
        
        # Test process command
        exit_code = cli.cmd_process(args)
        assert exit_code == 0
        
        # Test status command
        status_args = MockArgs(
            meetings=[str(meeting1)],
            verbose=False
        )
        
        exit_code = cli.cmd_status(status_args)
        assert exit_code == 0
        
        print("✅ CLI interface test passed")


def test_error_handling():
    """Test error handling and recovery."""
    
    print("\n=== Test: Error Handling ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create meeting folder without manifest
        bad_meeting = temp_path / "2026-02-16_Bad-Meeting"
        bad_meeting.mkdir()
        
        hook = PostTickHook()
        
        try:
            result = hook.process_single_meeting(bad_meeting, dry_run=True)
            assert False, "Should have raised exception for missing manifest"
        except Exception as e:
            print(f"Expected error caught: {e}")
            assert "No manifest.json" in str(e)
        
        # Create meeting with invalid manifest
        invalid_meeting = temp_path / "2026-02-16_Invalid-Meeting"
        invalid_meeting.mkdir()
        (invalid_meeting / "manifest.json").write_text("invalid json")
        
        try:
            result = hook.process_single_meeting(invalid_meeting, dry_run=True)
            assert False, "Should have raised exception for invalid manifest"
        except Exception:
            print("Expected error caught for invalid JSON")
        
        print("✅ Error handling test passed")


def run_all_tests():
    """Run all test functions."""
    
    print("Running Post-Tick Hook Tests")
    print("=" * 50)
    
    try:
        test_basic_promotion_processing()
        test_idempotency()
        test_promotion_gate_integration()
        test_cli_interface()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())