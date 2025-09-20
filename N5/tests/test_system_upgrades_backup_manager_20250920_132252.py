import unittest
import tempfile
import os
from pathlib import Path
from N5.scripts.system_upgrades_backup_manager import BackupManager

class TestBackupManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.backup_dir = Path(self.test_dir.name) / "backups" / "system-upgrades"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.manager = BackupManager(backup_dir=self.backup_dir)
       
        # Create dummy original files
        self.orig_md = self.backup_dir.parent.parent / "lists" / "system-upgrades.md"
        self.orig_jsonl = self.backup_dir.parent.parent / "lists" / "system-upgrades.jsonl"
        self.orig_md.parent.mkdir(parents=True, exist_ok=True)
        self.orig_md.write_text("original markdown data")
        self.orig_jsonl.write_text('{"id": "test1", "title": "Test Item"}\n')

    def tearDown(self):
        self.test_dir.cleanup()

    def test_create_backup_success(self):
        backup_md, backup_jsonl, metadata = self.manager.create_backup(operation_type="test")
        self.assertTrue(backup_md.exists())
        self.assertTrue(backup_jsonl.exists())
        self.assertTrue(metadata.success)

    def test_list_backups(self):
        self.manager.create_backup(operation_type="test")
        backups = self.manager.list_backups()
        self.assertTrue(len(backups) >= 1)

    def test_restore_and_prune(self):
        backup_md, backup_jsonl, metadata = self.manager.create_backup(operation_type="test")
        result = self.manager.restore_from_backup(timestamp=metadata.timestamp)
        self.assertTrue(result)

        # Test pruning doesn't error
        prune_result = self.manager.prune_backups(max_backups=1, max_age_days=1)
        self.assertIn("retained", prune_result)

if __name__ == '__main__':
    unittest.main()
