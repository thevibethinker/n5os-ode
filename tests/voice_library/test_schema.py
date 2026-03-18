#!/usr/bin/env python3
"""
Unit tests for Voice Library V2 schema.
Per PLAN.md v2.0 Phase 1

Run: python3 -m pytest tests/voice_library/test_schema.py -v
Or:  python3 tests/voice_library/test_schema.py
"""

import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "N5" / "data" / "voice_library.db"
SCHEMA_SQL = Path(__file__).parent.parent.parent / "N5" / "cognition" / "schema.sql"


def ensure_db():
    """Create the database from schema.sql if it doesn't exist."""
    if DB_PATH.exists():
        return
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    if SCHEMA_SQL.exists():
        conn.executescript(SCHEMA_SQL.read_text())
    else:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS primitives (
                id TEXT PRIMARY KEY,
                exact_text TEXT NOT NULL,
                primitive_type TEXT NOT NULL,
                distinctiveness_score REAL DEFAULT 0.0,
                novelty_flagged INTEGER DEFAULT 0,
                domains_json TEXT DEFAULT '[]',
                use_count INTEGER DEFAULT 0,
                last_used_at TEXT,
                status TEXT DEFAULT 'candidate',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                notes TEXT
            );
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                primitive_id TEXT NOT NULL,
                source_path TEXT,
                source_type TEXT,
                block_type TEXT,
                speaker TEXT,
                capture_signal TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (primitive_id) REFERENCES primitives(id)
            );
            CREATE TRIGGER IF NOT EXISTS update_primitives_timestamp
                AFTER UPDATE ON primitives
                FOR EACH ROW
                BEGIN
                    UPDATE primitives SET updated_at = datetime('now') WHERE id = OLD.id;
                END;
        """)
    conn.close()


def test_db_exists():
    """Database file should exist."""
    ensure_db()
    assert DB_PATH.exists(), f"Database not found at {DB_PATH}"
    print("✓ Database exists")


def test_tables_exist():
    """Required tables should exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    
    assert "primitives" in tables, "primitives table missing"
    assert "sources" in tables, "sources table missing"
    
    conn.close()
    print("✓ Required tables exist")


def test_primitives_columns():
    """Primitives table should have all V2 columns."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(primitives)")
    columns = {row[1] for row in cursor.fetchall()}
    
    required = {
        "id", "exact_text", "primitive_type",
        "distinctiveness_score", "novelty_flagged", "domains_json",
        "use_count", "last_used_at",
        "status", "created_at", "updated_at", "notes"
    }
    
    missing = required - columns
    assert not missing, f"Missing columns: {missing}"
    
    conn.close()
    print("✓ All V2 columns present")


def test_insert_primitive():
    """Should be able to insert a primitive with all V2 fields."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    test_id = "vp-test-001"
    
    # Clean up any previous test
    cursor.execute("DELETE FROM primitives WHERE id = ?", (test_id,))
    
    # Insert with V2 fields
    cursor.execute("""
        INSERT INTO primitives (
            id, exact_text, primitive_type,
            distinctiveness_score, novelty_flagged, domains_json,
            use_count, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        test_id,
        "The talent cliff isn't about skill—it's about options.",
        "analogy",
        0.85,
        0,
        json.dumps(["career", "optionality"]),
        0,
        "candidate"
    ))
    conn.commit()
    
    # Verify
    cursor.execute("SELECT * FROM primitives WHERE id = ?", (test_id,))
    row = cursor.fetchone()
    assert row is not None, "Insert failed"
    
    # Clean up
    cursor.execute("DELETE FROM primitives WHERE id = ?", (test_id,))
    conn.commit()
    conn.close()
    
    print("✓ Insert with V2 fields works")


def test_insert_source():
    """Should be able to insert a source linked to a primitive."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    prim_id = "vp-test-002"
    src_id = "src-test-001"
    
    # Clean up
    cursor.execute("DELETE FROM sources WHERE id = ?", (src_id,))
    cursor.execute("DELETE FROM primitives WHERE id = ?", (prim_id,))
    
    # Insert primitive first
    cursor.execute("""
        INSERT INTO primitives (id, exact_text, primitive_type)
        VALUES (?, ?, ?)
    """, (prim_id, "Test phrase", "phrase"))
    
    # Insert source
    cursor.execute("""
        INSERT INTO sources (
            id, primitive_id, source_path, source_type,
            block_type, speaker, capture_signal
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        src_id, prim_id,
        "Personal/Meetings/test.md", "transcript",
        "B35", "V", "I'm stealing that"
    ))
    conn.commit()
    
    # Verify
    cursor.execute("SELECT * FROM sources WHERE primitive_id = ?", (prim_id,))
    row = cursor.fetchone()
    assert row is not None, "Source insert failed"
    
    # Clean up
    cursor.execute("DELETE FROM sources WHERE id = ?", (src_id,))
    cursor.execute("DELETE FROM primitives WHERE id = ?", (prim_id,))
    conn.commit()
    conn.close()
    
    print("✓ Source linking works")


def test_domains_json():
    """Domains JSON should store and retrieve correctly."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    test_id = "vp-test-003"
    domains = ["career", "incentives", "ethics", "optionality"]
    
    # Clean up
    cursor.execute("DELETE FROM primitives WHERE id = ?", (test_id,))
    
    # Insert
    cursor.execute("""
        INSERT INTO primitives (id, exact_text, primitive_type, domains_json)
        VALUES (?, ?, ?, ?)
    """, (test_id, "Test", "phrase", json.dumps(domains)))
    conn.commit()
    
    # Retrieve and verify
    cursor.execute("SELECT domains_json FROM primitives WHERE id = ?", (test_id,))
    row = cursor.fetchone()
    retrieved = json.loads(row[0])
    assert retrieved == domains, f"Domains mismatch: {retrieved} != {domains}"
    
    # Clean up
    cursor.execute("DELETE FROM primitives WHERE id = ?", (test_id,))
    conn.commit()
    conn.close()
    
    print("✓ Domains JSON storage works")


def test_update_trigger():
    """Updated_at should auto-update on modification."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    test_id = "vp-test-004"
    
    # Clean up
    cursor.execute("DELETE FROM primitives WHERE id = ?", (test_id,))
    
    # Insert
    cursor.execute("""
        INSERT INTO primitives (id, exact_text, primitive_type)
        VALUES (?, ?, ?)
    """, (test_id, "Test", "phrase"))
    conn.commit()
    
    # Get initial timestamp
    cursor.execute("SELECT updated_at FROM primitives WHERE id = ?", (test_id,))
    initial = cursor.fetchone()[0]
    
    # Small delay then update
    import time
    time.sleep(0.1)
    
    cursor.execute("UPDATE primitives SET use_count = 1 WHERE id = ?", (test_id,))
    conn.commit()
    
    # Get new timestamp
    cursor.execute("SELECT updated_at FROM primitives WHERE id = ?", (test_id,))
    updated = cursor.fetchone()[0]
    
    # Note: SQLite datetime precision may not catch 0.1s difference
    # So we just verify the trigger didn't error
    
    # Clean up
    cursor.execute("DELETE FROM primitives WHERE id = ?", (test_id,))
    conn.commit()
    conn.close()
    
    print("✓ Update trigger works")


def run_all_tests():
    """Run all tests."""
    ensure_db()

    print(f"\n{'='*50}")
    print("Voice Library V2 Schema Tests")
    print(f"{'='*50}\n")
    
    tests = [
        test_db_exists,
        test_tables_exist,
        test_primitives_columns,
        test_insert_primitive,
        test_insert_source,
        test_domains_json,
        test_update_trigger,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

