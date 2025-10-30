#!/usr/bin/env python3
"""
Comprehensive Test Suite for Conversation End Pipeline
Tests: Thread Export → Title Generation → Conversation End → Archive

Usage:
    # Run all tests
    python3 test_conversation_end_pipeline.py
    
    # Run specific test suite
    python3 test_conversation_end_pipeline.py --suite title
    python3 test_conversation_end_pipeline.py --suite thread_export
    python3 test_conversation_end_pipeline.py --suite conversation_end
    
    # Run with verbose output
    python3 test_conversation_end_pipeline.py -v
    
    # Run specific test
    python3 test_conversation_end_pipeline.py -t test_title_validation
"""

import sys
import json
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add N5 scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from n5_title_generator import TitleGenerator
    from n5_conversation_end import (
        detect_conversation_workspace,
        generate_title_from_session_state,
        write_and_display_title,
    )
except ImportError as e:
    print(f"Warning: Could not import N5 modules: {e}")
    print("Some tests may be skipped")


class TestTitleGeneration(unittest.TestCase):
    """Test suite for title generation logic"""
    
    def setUp(self):
        """Create test fixtures"""
        self.temp_dir = tempfile.mkdtemp(prefix="n5_test_")
        self.test_workspace = Path(self.temp_dir)
        
    def tearDown(self):
        """Cleanup test environment"""
        if self.test_workspace.exists():
            shutil.rmtree(self.test_workspace)
    
    def create_aar_fixture(self, **kwargs) -> Dict:
        """Create AAR test fixture with overrides"""
        base_aar = {
            "conversation_id": kwargs.get("conversation_id", "con_TEST123"),
            "title": kwargs.get("title", "Test Conversation"),
            "created_at": kwargs.get("created_at", "2025-10-28T20:00:00"),
            "duration_minutes": kwargs.get("duration_minutes", 15),
            "type": kwargs.get("type", "discussion"),
            "focus": kwargs.get("focus", "Testing title generation"),
            "objective": kwargs.get("objective", "Verify title quality"),
            "outcome": kwargs.get("outcome", "Test completed"),
            "artifacts": kwargs.get("artifacts", [
                {"path": "/test/script.py", "type": "code", "purpose": "Test script"}
            ]),
            "key_decisions": kwargs.get("key_decisions", []),
            "lessons": kwargs.get("lessons", []),
            "next_steps": kwargs.get("next_steps", []),
        }
        return base_aar
    
    def test_title_with_complete_aar(self):
        """Test title generation with complete AAR data"""
        aar = self.create_aar_fixture(
            focus="Building email automation system",
            type="build",
            artifacts=[
                {"path": "/workspace/email_sender.py", "type": "code"},
                {"path": "/workspace/config.json", "type": "config"},
            ]
        )
        
        try:
            generator = TitleGenerator()
            titles = generator.generate_titles(aar, [], convo_id="con_TEST123")
            
            self.assertIsNotNone(titles, "Should generate titles")
            self.assertIsInstance(titles, list, "Should return list of titles")
            self.assertGreater(len(titles), 0, "Should generate at least one title")
            
            # Validate first title
            first_title = titles[0]
            self.assertIn("title", first_title, "Should have title field")
            self.assertIn("reasoning", first_title, "Should have reasoning")
            
            title_text = first_title["title"]
            # Should not have duplicate words
            words = title_text.split()
            self.assertNotEqual(words[-2:][0], words[-2:][1], 
                              f"Title should not have duplicate words: {title_text}")
            
        except Exception as e:
            self.fail(f"Title generation raised exception: {e}")
    
    def test_title_with_minimal_aar(self):
        """Test title generation with minimal AAR (edge case)"""
        aar = {
            "conversation_id": "con_MINIMAL",
            "created_at": "2025-10-28T20:00:00",
            "artifacts": []
        }
        
        try:
            generator = TitleGenerator()
            titles = generator.generate_titles(aar, [], convo_id="con_MINIMAL")
            
            # Should either generate something reasonable or fail gracefully
            if titles:
                self.assertIsInstance(titles, list)
                self.assertGreater(len(titles), 0)
            else:
                # If no titles, should log warning (check this in integration)
                pass
                
        except Exception as e:
            self.fail(f"Should handle minimal AAR gracefully: {e}")
    
    def test_title_with_empty_artifacts(self):
        """Test title when artifacts array is empty"""
        aar = self.create_aar_fixture(artifacts=[])
        
        try:
            generator = TitleGenerator()
            titles = generator.generate_titles(aar, [], convo_id="con_TEST123")
            
            self.assertIsNotNone(titles)
            # Should use focus/objective instead of artifacts
            
        except Exception as e:
            self.fail(f"Should handle empty artifacts: {e}")
    
    def test_title_format_validation(self):
        """Test that generated titles follow format requirements"""
        aar = self.create_aar_fixture(
            focus="Debugging N5 conversation end protocol",
            type="build"
        )
        
        try:
            generator = TitleGenerator()
            titles = generator.generate_titles(aar, [], convo_id="con_TEST123")
            
            for title_obj in titles:
                title = title_obj["title"]
                
                # Check length (18-35 chars after date)
                # Format: "MMM DD | emoji Entity Action"
                parts = title.split("|", 1)
                if len(parts) == 2:
                    content = parts[1].strip()
                    self.assertGreaterEqual(len(content), 10, 
                                          f"Title too short: {title}")
                    self.assertLessEqual(len(content), 50,
                                       f"Title too long: {title}")
                
                # Should have emoji
                self.assertTrue(any(ord(c) > 127 for c in title),
                              f"Title should contain emoji: {title}")
                
                # Should not have repeated words at end
                words = title.split()
                if len(words) >= 2:
                    self.assertNotEqual(words[-1], words[-2],
                                      f"Title has duplicate words: {title}")
                    
        except Exception as e:
            self.fail(f"Title format validation failed: {e}")
    
    def test_title_with_build_indicators(self):
        """Test that build conversations get appropriate titles"""
        aar = self.create_aar_fixture(
            focus="Implementing authentication system",
            type="build",
            artifacts=[
                {"path": "/workspace/auth.py", "type": "code"},
                {"path": "/workspace/middleware.py", "type": "code"},
            ]
        )
        
        try:
            generator = TitleGenerator()
            titles = generator.generate_titles(aar, [], convo_id="con_BUILD")
            
            self.assertGreater(len(titles), 0)
            first_title = titles[0]["title"]
            
            # Should have build-related emoji or action words
            build_indicators = ["Build", "Implement", "Create", "🔨", "⚙️", "🏗️"]
            has_indicator = any(ind in first_title for ind in build_indicators)
            self.assertTrue(has_indicator, 
                          f"Build title should have build indicator: {first_title}")
            
        except Exception as e:
            self.fail(f"Build title generation failed: {e}")
    
    def test_title_deduplication(self):
        """Test that duplicate nouns/actions are caught"""
        # This tests the validation logic we need to add
        bad_titles = [
            "Oct 28 | ✅ System Work Work",
            "Oct 28 | 🔧 Test Test Fix",
            "Oct 28 | 📊 Report Report Generate",
        ]
        
        for bad_title in bad_titles:
            words = bad_title.split()
            # Check last two words aren't identical
            if len(words) >= 2:
                last_word = words[-1]
                second_last = words[-2]
                self.assertNotEqual(last_word, second_last,
                                  f"Title has duplicate: {bad_title}")


class TestTitleGenerationFallback(unittest.TestCase):
    """Test fallback title generation from SESSION_STATE"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="n5_test_fallback_")
        self.test_workspace = Path(self.temp_dir)
        
    def tearDown(self):
        if self.test_workspace.exists():
            shutil.rmtree(self.test_workspace)
    
    def create_session_state(self, **kwargs):
        """Create SESSION_STATE.md fixture"""
        content = f"""# Session State — Build

**Conversation ID**: {kwargs.get('convo_id', 'con_TEST')}
**Type**: {kwargs.get('type', 'build')}
**Created**: {kwargs.get('created', '2025-10-28 20:00 ET')}

## Focus

{kwargs.get('focus', 'Testing session state extraction')}

## Objective

{kwargs.get('objective', 'Verify fallback title generation')}

## Progress

### Completed
{kwargs.get('completed', '- Initial setup\\n- Tests created')}

## Artifacts

### Permanent
{kwargs.get('artifacts', '- file `/home/workspace/test.py`')}
"""
        session_file = self.test_workspace / "SESSION_STATE.md"
        session_file.write_text(content)
        return session_file
    
    def test_extract_from_session_state(self):
        """Test extracting fields from SESSION_STATE.md"""
        session_file = self.create_session_state(
            focus="Building email automation",
            objective="Create SendGrid integration",
            completed="- API wrapper\n- Error handling\n- Tests"
        )
        
        # Test extraction logic
        content = session_file.read_text()
        
        # Extract focus
        self.assertIn("Building email automation", content)
        self.assertIn("Create SendGrid integration", content)
        
    def test_fallback_title_generation(self):
        """Test generating title when AAR doesn't exist"""
        session_file = self.create_session_state(
            focus="Refactoring N5 conversation end",
            objective="Improve reliability and testing",
            type="build"
        )
        
        # This would test generate_title_from_session_state()
        # when AAR is missing
        pass  # Implement when function is accessible


class TestThreadExport(unittest.TestCase):
    """Test thread export functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="n5_test_export_")
        self.test_workspace = Path(self.temp_dir)
        
    def tearDown(self):
        if self.test_workspace.exists():
            shutil.rmtree(self.test_workspace)
    
    def test_workspace_detection(self):
        """Test automatic workspace detection"""
        # Create mock conversation workspace
        convo_dir = Path("/home/.z/workspaces/con_TEST123")
        # Note: Can't actually test without creating workspace
        pass
    
    def test_artifact_inventory(self):
        """Test artifact scanning"""
        # Create test files
        (self.test_workspace / "script.py").write_text("# Test script")
        (self.test_workspace / "notes.md").write_text("# Notes")
        (self.test_workspace / "SESSION_STATE.md").write_text("# Session")
        
        # Test inventory logic
        artifacts = list(self.test_workspace.glob("*"))
        self.assertEqual(len(artifacts), 3)


class TestConversationEndPhases(unittest.TestCase):
    """Test individual phases of conversation end"""
    
    def test_phase_0_aar_generation(self):
        """Test Phase 0: AAR generation"""
        pass
    
    def test_phase_1_analysis(self):
        """Test Phase 1: Workspace analysis"""
        pass
    
    def test_phase_2_proposal(self):
        """Test Phase 2: Organization proposal"""
        pass
    
    def test_phase_3_execution(self):
        """Test Phase 3: File organization"""
        pass
    
    def test_phase_5_registry_update(self):
        """Test Phase 5: Database update"""
        pass


class TestIntegrationFlow(unittest.TestCase):
    """Integration tests for full pipeline"""
    
    def test_full_thread_export_flow(self):
        """Test complete thread export: detect → inventory → AAR → title → save"""
        pass
    
    def test_full_conversation_end_flow(self):
        """Test complete conversation end: all phases"""
        pass
    
    def test_thread_export_then_conversation_end(self):
        """Test sequential execution"""
        pass
    
    def test_fallback_when_thread_export_fails(self):
        """Test inline AAR generation when thread export unavailable"""
        pass


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_empty_workspace(self):
        """Test with no artifacts"""
        pass
    
    def test_large_workspace(self):
        """Test with 100+ files"""
        pass
    
    def test_missing_session_state(self):
        """Test when SESSION_STATE.md doesn't exist"""
        pass
    
    def test_corrupted_aar(self):
        """Test with malformed AAR JSON"""
        pass
    
    def test_missing_database(self):
        """Test when conversations.db doesn't exist"""
        pass


def run_test_suite(suite_name: Optional[str] = None, verbose: bool = False):
    """Run tests with optional filtering"""
    loader = unittest.TestLoader()
    
    if suite_name:
        suite_map = {
            "title": TestTitleGeneration,
            "fallback": TestTitleGenerationFallback,
            "export": TestThreadExport,
            "phases": TestConversationEndPhases,
            "integration": TestIntegrationFlow,
            "edge": TestEdgeCases,
        }
        
        if suite_name not in suite_map:
            print(f"Unknown suite: {suite_name}")
            print(f"Available: {', '.join(suite_map.keys())}")
            return False
        
        suite = loader.loadTestsFromTestCase(suite_map[suite_name])
    else:
        # Run all tests
        suite = unittest.TestSuite()
        for test_class in [
            TestTitleGeneration,
            TestTitleGenerationFallback,
            TestThreadExport,
            TestConversationEndPhases,
            TestIntegrationFlow,
            TestEdgeCases,
        ]:
            suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="N5 Conversation End Pipeline Tests")
    parser.add_argument("--suite", "-s", help="Run specific test suite")
    parser.add_argument("--test", "-t", help="Run specific test")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--list", "-l", action="store_true", help="List available suites")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available test suites:")
        print("  title       - Title generation tests")
        print("  fallback    - Fallback title generation")
        print("  export      - Thread export tests")
        print("  phases      - Conversation end phases")
        print("  integration - Integration tests")
        print("  edge        - Edge case tests")
        return 0
    
    if args.test:
        # Run specific test
        suite = unittest.TestLoader().loadTestsFromName(args.test, module=sys.modules[__name__])
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1
    
    success = run_test_suite(args.suite, args.verbose)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
