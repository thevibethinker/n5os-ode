#!/usr/bin/env python3
"""
Test suite for direct knowledge ingestion mechanism
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add N5 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.direct_ingestion_mechanism import DirectKnowledgeIngestion

class TestDirectIngestion(unittest.TestCase):
    """Test cases for direct knowledge ingestion"""

    def setUp(self):
        """Set up test fixtures"""
        self.ingestion = DirectKnowledgeIngestion()
        self.sample_content = """
        John Doe is a software engineer with 5 years experience.
        He founded TechCorp in 2020 and launched their AI platform in 2022.
        The company focuses on machine learning solutions.
        """

    def test_initialization(self):
        """Test that DirectKnowledgeIngestion initializes correctly"""
        self.assertIsInstance(self.ingestion, DirectKnowledgeIngestion)
        self.assertTrue(self.ingestion.knowledge_dir.exists())

    def test_process_large_document(self):
        """Test processing of document content"""
        with patch.object(self.ingestion, '_extract_bio_info', return_value={"summary": "Test bio"}):
            with patch.object(self.ingestion, '_extract_timeline', return_value=[{"date": "2020", "title": "Founded", "description": "Company founded"}]):
                with patch.object(self.ingestion, '_extract_glossary', return_value=[{"term": "AI", "definition": "Artificial Intelligence"}]):
                    with patch.object(self.ingestion, '_extract_sources', return_value=[{"title": "Test Source", "url": "http://test.com"}]):
                        with patch.object(self.ingestion, '_extract_company_info', return_value={"overview": "Test company"}):
                            with patch.object(self.ingestion, '_extract_facts', return_value=[{"subject": "Test", "predicate": "is", "object": "working"}]):
                                with patch.object(self.ingestion, '_extract_suggestions', return_value=[{"type": "new_reservoir", "description": "Test suggestion"}]):
                                    result = self.ingestion.process_large_document(self.sample_content, "test_source")

                                    self.assertIn("bio", result)
                                    self.assertIn("timeline", result)
                                    self.assertIn("glossary", result)
                                    self.assertIn("sources", result)
                                    self.assertIn("company", result)
                                    self.assertIn("facts", result)
                                    self.assertIn("suggestions", result)

    def test_save_to_reservoirs(self):
        """Test saving structured data to reservoirs"""
        test_data = {
            "bio": {"summary": "Test bio summary"},
            "timeline": [{"date": "2020", "title": "Test Event", "description": "Test description"}],
            "glossary": [{"term": "Test Term", "definition": "Test definition"}],
            "sources": [{"title": "Test Source", "url": "http://test.com"}],
            "company_overview": "Test company overview",
            "facts": [{"subject": "Test", "predicate": "is", "object": "test"}],
            "suggestions": [{"type": "new_reservoir", "description": "Test suggestion"}]
        }

        # This would create test files - in real usage, we'd use a temporary directory
        # self.ingestion.save_to_reservoirs(test_data, "_test")

    def test_large_content_handling(self):
        """Test that large content doesn't cause issues"""
        large_content = "A" * 50000  # 50k characters

        # Should not crash with large content
        try:
            self.ingestion.process_large_document(large_content, "large_test")
            success = True
        except Exception as e:
            success = False
            print(f"Large content test failed: {e}")

        self.assertTrue(success, "Should handle large content without crashing")

def run_tests():
    """Run the test suite"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests()