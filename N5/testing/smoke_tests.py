#!/usr/bin/env python3
"""
Executable System Smoke Tests
Quick validation of core functionality (runs in ~30 seconds)
"""

import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

DB_PATH = Path("/home/workspace/N5/data/executables.db")
PROMPTS_DIR = Path("/home/workspace/Prompts")

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test(self, name, func):
        """Run a single test"""
        try:
            func()
            print(f"✓ {name}")
            self.passed += 1
        except AssertionError as e:
            print(f"✗ {name}: {e}")
            self.failed += 1
            self.errors.append((name, str(e)))
        except Exception as e:
            print(f"✗ {name}: ERROR - {e}")
            self.failed += 1
            self.errors.append((name, f"ERROR: {e}"))
    
    def summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Tests: {total} | Passed: {self.passed} | Failed: {self.failed}")
        
        if self.failed > 0:
            print(f"\nFailed tests:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
            return 1
        else:
            print(f"\n🎉 All smoke tests passed!")
            return 0

def get_conn():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# SMOKE TESTS
# ============================================================================

def test_db_exists():
    """T0.1: Database file exists"""
    assert DB_PATH.exists(), f"Database not found at {DB_PATH}"

def test_db_integrity():
    """T0.2: Database integrity check passes"""
    conn = get_conn()
    result = conn.execute("PRAGMA integrity_check").fetchone()
    conn.close()
    assert result[0] == "ok", f"Integrity check failed: {result[0]}"

def test_schema_tables():
    """T1.1: Required tables exist"""
    conn = get_conn()
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name IN ('executables', 'invocations', 'executables_fts')
    """)
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    required = {'executables', 'invocations', 'executables_fts'}
    missing = required - tables
    assert not missing, f"Missing tables: {missing}"

def test_has_records():
    """T1.2: Database has executables"""
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM executables").fetchone()[0]
    conn.close()
    assert count > 0, f"No executables found (expected > 0)"

def test_no_orphaned_invocations():
    """T1.3: No orphaned invocations"""
    conn = get_conn()
    orphans = conn.execute("""
        SELECT COUNT(*) FROM invocations i
        LEFT JOIN executables e ON i.executable_id = e.id
        WHERE e.id IS NULL
    """).fetchone()[0]
    conn.close()
    assert orphans == 0, f"Found {orphans} orphaned invocations"

def test_no_duplicate_ids():
    """T1.4: No duplicate IDs"""
    conn = get_conn()
    dupes = conn.execute("""
        SELECT id, COUNT(*) as cnt FROM executables 
        GROUP BY id HAVING cnt > 1
    """).fetchall()
    conn.close()
    assert len(dupes) == 0, f"Found duplicate IDs: {[d[0] for d in dupes]}"

def test_no_duplicate_paths():
    """T1.5: No duplicate file paths"""
    conn = get_conn()
    dupes = conn.execute("""
        SELECT file_path, COUNT(*) as cnt FROM executables 
        GROUP BY file_path HAVING cnt > 1
    """).fetchall()
    conn.close()
    assert len(dupes) == 0, f"Found duplicate paths: {[d[0] for d in dupes]}"

def test_file_paths_valid():
    """T1.6: All file paths point to existing files"""
    conn = get_conn()
    records = conn.execute("SELECT id, file_path FROM executables").fetchall()
    conn.close()
    
    missing = []
    for record in records:
        exec_id, file_path = record
        if not Path(file_path).exists():
            missing.append((exec_id, file_path))
    
    assert len(missing) == 0, f"Missing files for {len(missing)} executables: {missing[:3]}"

def test_json_fields_valid():
    """T1.7: All JSON fields are valid JSON"""
    conn = get_conn()
    records = conn.execute("""
        SELECT id, tags, dependencies, frontmatter FROM executables
        WHERE tags IS NOT NULL OR dependencies IS NOT NULL OR frontmatter IS NOT NULL
    """).fetchall()
    conn.close()
    
    errors = []
    for record in records:
        exec_id, tags, deps, frontmatter = record
        try:
            if tags:
                json.loads(tags)
            if deps:
                json.loads(deps)
            if frontmatter:
                json.loads(frontmatter)
        except json.JSONDecodeError as e:
            errors.append((exec_id, str(e)))
    
    assert len(errors) == 0, f"Invalid JSON in {len(errors)} records: {errors[:3]}"

def test_search_works():
    """T3.1: FTS search returns results"""
    conn = get_conn()
    results = conn.execute("""
        SELECT id FROM executables_fts 
        WHERE executables_fts MATCH 'meeting'
    """).fetchall()
    conn.close()
    
    assert len(results) > 0, "FTS search for 'meeting' returned no results"

def test_type_constraint():
    """T2.1: Type column has valid values"""
    conn = get_conn()
    invalid = conn.execute("""
        SELECT id, type FROM executables 
        WHERE type NOT IN ('prompt', 'script', 'tool')
    """).fetchall()
    conn.close()
    
    assert len(invalid) == 0, f"Invalid type values: {invalid}"

def test_status_constraint():
    """T2.2: Status column has valid values"""
    conn = get_conn()
    invalid = conn.execute("""
        SELECT id, status FROM executables 
        WHERE status NOT IN ('active', 'deprecated', 'experimental')
    """).fetchall()
    conn.close()
    
    assert len(invalid) == 0, f"Invalid status values: {invalid}"

def test_timestamps_valid():
    """T2.3: Timestamps are valid ISO8601"""
    conn = get_conn()
    records = conn.execute("""
        SELECT id, created_at, updated_at FROM executables LIMIT 10
    """).fetchall()
    conn.close()
    
    errors = []
    for record in records:
        exec_id, created, updated = record
        try:
            if created:
                datetime.fromisoformat(created.replace('Z', '+00:00'))
            if updated:
                datetime.fromisoformat(updated.replace('Z', '+00:00'))
        except ValueError as e:
            errors.append((exec_id, str(e)))
    
    assert len(errors) == 0, f"Invalid timestamps: {errors}"

def test_fts_triggers_exist():
    """T3.2: FTS triggers exist"""
    conn = get_conn()
    triggers = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='trigger' AND name LIKE 'executables_a%'
    """).fetchall()
    conn.close()
    
    trigger_names = {t[0] for t in triggers}
    required = {'executables_ai', 'executables_au', 'executables_ad'}
    missing = required - trigger_names
    assert not missing, f"Missing FTS triggers: {missing}"

def test_indexes_exist():
    """T1.8: Performance indexes exist"""
    conn = get_conn()
    indexes = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND tbl_name='executables'
    """).fetchall()
    conn.close()
    
    index_names = {idx[0] for idx in indexes}
    required = {'idx_type', 'idx_category', 'idx_status'}
    missing = required - index_names
    assert not missing, f"Missing indexes: {missing}"

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*60)
    print("Executable System - Smoke Tests")
    print("="*60)
    print(f"Database: {DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print()
    
    runner = TestRunner()
    
    # Run tests
    runner.test("T0.1: Database file exists", test_db_exists)
    runner.test("T0.2: Database integrity check", test_db_integrity)
    runner.test("T1.1: Required tables exist", test_schema_tables)
    runner.test("T1.2: Database has records", test_has_records)
    runner.test("T1.3: No orphaned invocations", test_no_orphaned_invocations)
    runner.test("T1.4: No duplicate IDs", test_no_duplicate_ids)
    runner.test("T1.5: No duplicate file paths", test_no_duplicate_paths)
    runner.test("T1.6: All file paths valid", test_file_paths_valid)
    runner.test("T1.7: JSON fields valid", test_json_fields_valid)
    runner.test("T1.8: Performance indexes exist", test_indexes_exist)
    runner.test("T2.1: Type constraint valid", test_type_constraint)
    runner.test("T2.2: Status constraint valid", test_status_constraint)
    runner.test("T2.3: Timestamps valid", test_timestamps_valid)
    runner.test("T3.1: FTS search works", test_search_works)
    runner.test("T3.2: FTS triggers exist", test_fts_triggers_exist)
    
    return runner.summary()

if __name__ == "__main__":
    sys.exit(main())
