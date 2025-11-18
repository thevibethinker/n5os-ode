#!/usr/bin/env python3
"""
Comprehensive tests for meeting orchestrator system
Tests registry, normalizer, and orchestrator integration
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from meeting_registry import MeetingRegistry
from meeting_normalizer import (
    normalize_date,
    normalize_participants,
    generate_meeting_id,
    parse_folder_name
)
from meeting_orchestrator import MeetingOrchestrator


class TestMeetingNormalizer(unittest.TestCase):
    """Test normalization functions"""
    
    def test_normalize_date_canonical(self):
        """Test already canonical date format"""
        self.assertEqual(normalize_date('2025-11-14'), '2025-11-14')
    
    def test_normalize_date_compact(self):
        """Test compact date format (YYYYMMDD)"""
        self.assertEqual(normalize_date('20251114'), '2025-11-14')
    
    def test_normalize_date_us_format(self):
        """Test US date format (MM/DD/YYYY)"""
        self.assertEqual(normalize_date('11/14/2025'), '2025-11-14')
    
    def test_normalize_date_invalid(self):
        """Test invalid date format raises ValueError"""
        with self.assertRaises(ValueError):
            normalize_date('invalid-date')
    
    def test_normalize_participants_hyphen(self):
        """Test name normalization with hyphens"""
        result = normalize_participants(['Ayush-Jain', 'Vrijen-Attawar'])
        self.assertEqual(result, ['ayushjain', 'vrijenattawar'])
    
    def test_normalize_participants_underscore(self):
        """Test name normalization with underscores"""
        result = normalize_participants(['Ayush_Jain', 'Vrijen_Attawar'])
        self.assertEqual(result, ['ayushjain', 'vrijenattawar'])
    
    def test_normalize_participants_space(self):
        """Test name normalization with spaces"""
        result = normalize_participants(['Ayush Jain', 'Vrijen Attawar'])
        self.assertEqual(result, ['ayushjain', 'vrijenattawar'])
    
    def test_normalize_participants_sorted(self):
        """Test participants are sorted alphabetically"""
        result = normalize_participants(['Zoe', 'Bob', 'Alice'])
        self.assertEqual(result, ['alice', 'bob', 'zoe'])
    
    def test_normalize_participants_deduped(self):
        """Test duplicate participants are removed"""
        result = normalize_participants(['Alice', 'alice', 'ALICE'])
        self.assertEqual(result, ['alice'])
    
    def test_generate_meeting_id(self):
        """Test meeting ID generation"""
        meeting_id = generate_meeting_id('2025-11-14', ['ayushjain', 'vrijenattawar'])
        self.assertEqual(meeting_id, '2025-11-14_ayushjain-vrijenattawar')
    
    def test_parse_folder_name_standard(self):
        """Test parsing standard folder name format"""
        result = parse_folder_name('2025-11-14_Ayush-Jain_Vrijen-Attawar')
        self.assertEqual(result['date'], '2025-11-14')
        self.assertEqual(result['participants'], ['ayushjain', 'vrijenattawar'])
    
    def test_parse_folder_name_invalid(self):
        """Test parsing invalid folder name returns None"""
        result = parse_folder_name('invalid-folder-name')
        self.assertIsNone(result)


class TestMeetingRegistry(unittest.TestCase):
    """Test registry operations"""
    
    def setUp(self):
        """Create temporary database for each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.registry = MeetingRegistry(db_path=self.temp_db.name)
    
    def tearDown(self):
        """Clean up temporary database"""
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    def test_add_meeting(self):
        """Test adding meeting to registry"""
        metadata = {
            'meeting_id': 'test-2025-01-01-alice-bob',
            'date': '2025-01-01',
            'participants_normalized': ['alice', 'bob'],
            'folder_name': 'test_folder',
            'source': 'test'
        }
        meeting_id = self.registry.add_meeting(metadata)
        self.assertEqual(meeting_id, 'test-2025-01-01-alice-bob')
    
    def test_find_exact_duplicate(self):
        """Test finding exact duplicate"""
        metadata = {
            'meeting_id': 'test-2025-01-01-alice-bob',
            'date': '2025-01-01',
            'participants_normalized': ['alice', 'bob'],
            'folder_name': 'test_folder',
            'source': 'test'
        }
        self.registry.add_meeting(metadata)
        
        found = self.registry.find_duplicate('2025-01-01', ['alice', 'bob'])
        self.assertIsNotNone(found)
        self.assertEqual(found['meeting_id'], 'test-2025-01-01-alice-bob')
    
    def test_find_no_duplicate(self):
        """Test no duplicate found for different meeting"""
        metadata = {
            'meeting_id': 'test-2025-01-01-alice-bob',
            'date': '2025-01-01',
            'participants_normalized': ['alice', 'bob'],
            'folder_name': 'test_folder',
            'source': 'test'
        }
        self.registry.add_meeting(metadata)
        
        found = self.registry.find_duplicate('2025-01-01', ['charlie', 'dave'])
        self.assertIsNone(found)
    
    def test_find_fuzzy_duplicate_high_similarity(self):
        """Test fuzzy matching with high similarity"""
        metadata = {
            'meeting_id': 'test-2025-01-01-alice-bob',
            'date': '2025-01-01',
            'participants_normalized': ['alice', 'bob'],
            'folder_name': 'test_folder',
            'source': 'test'
        }
        self.registry.add_meeting(metadata)
        
        # Use very similar names that will score >90%
        fuzzy = self.registry.find_fuzzy_duplicates('2025-01-01', ['alice', 'bob1'])
        self.assertEqual(len(fuzzy), 1)
        self.assertGreater(fuzzy[0]['similarity_score'], 0.90)
    
    def test_find_fuzzy_duplicate_low_similarity(self):
        """Test fuzzy matching with low similarity (no match)"""
        metadata = {
            'meeting_id': 'test-2025-01-01-alice-bob',
            'date': '2025-01-01',
            'participants_normalized': ['alice', 'bob'],
            'folder_name': 'test_folder',
            'source': 'test'
        }
        self.registry.add_meeting(metadata)
        
        fuzzy = self.registry.find_fuzzy_duplicates('2025-01-01', ['charlie', 'dave'])
        self.assertEqual(len(fuzzy), 0)
    
    def test_update_meeting(self):
        """Test updating meeting record"""
        metadata = {
            'meeting_id': 'test-2025-01-01-alice-bob',
            'date': '2025-01-01',
            'participants_normalized': ['alice', 'bob'],
            'folder_name': 'test_folder',
            'source': 'test'
        }
        self.registry.add_meeting(metadata)
        
        updated = self.registry.update_meeting('test-2025-01-01-alice-bob', {
            'file_count': 5,
            'status': 'processed'
        })
        self.assertTrue(updated)
        
        meeting = self.registry.get_meeting('test-2025-01-01-alice-bob')
        self.assertEqual(meeting['file_count'], 5)
        self.assertEqual(meeting['status'], 'processed')
    
    def test_get_stats(self):
        """Test registry statistics"""
        metadata1 = {
            'meeting_id': 'test-2025-01-01-alice-bob',
            'date': '2025-01-01',
            'participants_normalized': ['alice', 'bob'],
            'folder_name': 'test_folder_1',
            'source': 'test',
            'file_count': 3
        }
        metadata2 = {
            'meeting_id': 'test-2025-01-02-charlie-dave',
            'date': '2025-01-02',
            'participants_normalized': ['charlie', 'dave'],
            'folder_name': 'test_folder_2',
            'source': 'test',
            'file_count': 5
        }
        self.registry.add_meeting(metadata1)
        self.registry.add_meeting(metadata2)
        
        stats = self.registry.get_stats()
        self.assertEqual(stats['total_meetings'], 2)
        self.assertEqual(stats['total_files'], 8)
        self.assertEqual(stats['unique_dates'], 2)


class TestMeetingOrchestrator(unittest.TestCase):
    """Test orchestrator integration"""
    
    def setUp(self):
        """Create temporary directories and registry"""
        self.temp_dir = tempfile.mkdtemp()
        self.meetings_dir = Path(self.temp_dir) / "meetings"
        self.meetings_dir.mkdir()
        
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.registry = MeetingRegistry(db_path=self.temp_db.name)
        
        self.orchestrator = MeetingOrchestrator(
            registry=self.registry,
            meetings_dir=self.meetings_dir
        )
    
    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    def test_ingest_new_meeting(self):
        """Test ingesting new meeting (CREATE action)"""
        result = self.orchestrator.ingest_meeting(
            date='2025-11-14',
            participants=['Ayush Jain', 'Vrijen Attawar'],
            source='test'
        )
        
        self.assertEqual(result['action'], 'created')
        self.assertEqual(result['meeting_id'], '2025-11-14_ayushjain-vrijenattawar')
        self.assertTrue(Path(result['folder_path']).exists())
    
    def test_ingest_exact_duplicate(self):
        """Test ingesting exact duplicate (SKIP action)"""
        self.orchestrator.ingest_meeting(
            date='2025-11-14',
            participants=['Ayush Jain', 'Vrijen Attawar'],
            source='test'
        )
        
        result = self.orchestrator.ingest_meeting(
            date='2025-11-14',
            participants=['Ayush-Jain', 'Vrijen_Attawar'],
            source='test'
        )
        
        self.assertEqual(result['action'], 'skipped')
        self.assertIn('duplicate', result['reason'].lower())
    
    def test_ingest_fuzzy_duplicate(self):
        """Test ingesting fuzzy duplicate (MERGE action)"""
        self.orchestrator.ingest_meeting(
            date='2025-11-14',
            participants=['Ayush Jain', 'Vrijen Attawar'],
            source='test'
        )
        
        result = self.orchestrator.ingest_meeting(
            date='2025-11-14',
            participants=['Ayush Jayn', 'Vrijen Attawar'],
            source='test'
        )
        
        self.assertEqual(result['action'], 'merged')
        self.assertIn('similarity_score', result)
        self.assertGreater(result['similarity_score'], 0.9)
    
    def test_dry_run_mode(self):
        """Test dry-run mode doesn't create folders"""
        result = self.orchestrator.ingest_meeting(
            date='2025-11-14',
            participants=['Ayush Jain'],
            source='test',
            dry_run=True
        )
        
        self.assertEqual(result['action'], 'checked')
        self.assertEqual(len(list(self.meetings_dir.iterdir())), 0)
    
    def test_backfill_from_filesystem(self):
        """Test backfilling registry from existing folders"""
        (self.meetings_dir / "2025-11-14_Alice_Bob").mkdir()
        (self.meetings_dir / "2025-11-15_Charlie_Dave").mkdir()
        (self.meetings_dir / "invalid-folder").mkdir()
        
        stats = self.orchestrator.backfill_from_filesystem()
        
        self.assertEqual(stats['added'], 2)
        self.assertEqual(stats['errors'], 1)
        self.assertEqual(stats['skipped'], 0)
    
    def test_backfill_lifo_ordering(self):
        """Test LIFO backfill processes newest first"""
        folder1 = self.meetings_dir / "2025-11-14_Alice_Bob"
        folder2 = self.meetings_dir / "2025-11-15_Charlie_Dave"
        folder1.mkdir()
        folder2.mkdir()
        
        folder2.touch()
        
        stats = self.orchestrator.backfill_from_filesystem(limit=1, lifo=True)
        
        self.assertEqual(stats['processed'], 1)
        
        meetings = self.registry.list_meetings()
        self.assertTrue(any('charlie' in str(m['participants_normalized']) for m in meetings))


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestMeetingNormalizer))
    suite.addTests(loader.loadTestsFromTestCase(TestMeetingRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestMeetingOrchestrator))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())



