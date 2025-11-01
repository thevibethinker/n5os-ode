# Executable System Test Plan

**System Under Test:** executables.db + executable_manager.py  
**Version:** 1.0  
**Created:** 2025-11-01  
**Status:** Draft

---

## Test Philosophy

### Principles (from P33)
- **Tests first, code second** (we're retrofitting, acknowledge debt)
- **Test what matters** (focus on failure modes, not happy paths)
- **Fast feedback** (tests run in < 1 minute)
- **Reproducible** (deterministic, no flaky tests)

### Test Pyramid
```
     /\
    /E2E\       End-to-end (5 tests) - Full workflows
   /------\
  /Integration\  Integration (15 tests) - DB + filesystem
 /------------\
/    Unit      \ Unit (30 tests) - Individual functions
----------------
```

---

## Test Categories

### 1. Data Integrity Tests (Critical)

#### T1.1: Schema Validation
```sql
-- Verify schema matches spec
PRAGMA table_info(executables);
PRAGMA table_info(invocations);
-- Check constraints exist
-- Check indexes exist
```

**Pass criteria:** All columns, types, constraints present

#### T1.2: Referential Integrity
```sql
-- No orphaned invocations
SELECT COUNT(*) FROM invocations i
LEFT JOIN executables e ON i.executable_id = e.id
WHERE e.id IS NULL;
```

**Pass criteria:** COUNT = 0 (no orphans)

#### T1.3: File Path Validity
```python
# All file_path entries point to existing files
for record in executables:
    assert Path(record.file_path).exists(), f"Missing: {record.file_path}"
```

**Pass criteria:** 100% of paths exist

#### T1.4: Unique Constraints
```sql
-- No duplicate IDs
SELECT id, COUNT(*) FROM executables GROUP BY id HAVING COUNT(*) > 1;
-- No duplicate file paths
SELECT file_path, COUNT(*) FROM executables GROUP BY file_path HAVING COUNT(*) > 1;
```

**Pass criteria:** Both return 0 rows

#### T1.5: JSON Field Validity
```python
# All JSON fields are valid JSON
for record in executables:
    if record.tags: json.loads(record.tags)
    if record.dependencies: json.loads(record.dependencies)
    if record.frontmatter: json.loads(record.frontmatter)
```

**Pass criteria:** No JSON decode errors

---

### 2. CRUD Operations Tests (Functional)

#### T2.1: Register New Executable
```python
# Create test file
test_file = "/tmp/test-prompt.md"
Path(test_file).write_text("# Test")

# Register
result = register_executable(
    file_path=test_file,
    exec_type="prompt",
    exec_id="test-001",
    description="Test prompt"
)

assert result.id == "test-001"
assert result.type == "prompt"
```

**Pass criteria:** Record created, queryable immediately

#### T2.2: Register Duplicate ID
```python
# Try to register same ID twice
try:
    register_executable(file_path=test_file, exec_id="test-001")
    assert False, "Should have raised error"
except sqlite3.IntegrityError:
    pass  # Expected
```

**Pass criteria:** Raises IntegrityError

#### T2.3: Update Metadata
```python
update_executable("test-001", description="Updated description")
result = get_executable("test-001")
assert result.description == "Updated description"
```

**Pass criteria:** Changes persisted

#### T2.4: Delete Executable
```python
delete_executable("test-001")
result = get_executable("test-001")
assert result is None
```

**Pass criteria:** Record removed, FTS cleaned up

#### T2.5: Delete With Invocations
```python
# Create invocation
log_invocation("test-001", "con_test")
# Delete executable
delete_executable("test-001")
# Verify invocations also deleted (cascade) OR remain (audit trail)
```

**Pass criteria:** Defined behavior (document which)

---

### 3. Search & Query Tests (Effectiveness)

#### T3.1: FTS Search Precision
```python
results = search_executables("meeting")
meeting_names = [r.name for r in results]
assert "Analyze Meeting" in meeting_names
assert "Meeting Prep Digest" in meeting_names
assert "Unrelated Command" not in meeting_names
```

**Pass criteria:** Relevant results returned

#### T3.2: FTS Search Recall
```python
# Search for known term
results = search_executables("digest")
ids = [r.id for r in results]
assert "add-digest" in ids  # Known to exist
```

**Pass criteria:** Known matches found

#### T3.3: FTS Ranking
```python
results = search_executables("conversation")
# Name match should rank higher than description match
first_result = results[0]
assert "conversation" in first_result.name.lower()
```

**Pass criteria:** Name matches rank higher

#### T3.4: Empty Search
```python
results = search_executables("")
assert len(results) == 0  # Or all results? Document behavior
```

**Pass criteria:** Defined behavior

#### T3.5: Special Characters
```python
results = search_executables("@#$%")
# Should not crash
assert isinstance(results, list)
```

**Pass criteria:** No crashes

#### T3.6: Case Insensitivity
```python
results_lower = search_executables("meeting")
results_upper = search_executables("MEETING")
results_mixed = search_executables("MeEtInG")
assert results_lower == results_upper == results_mixed
```

**Pass criteria:** Case-insensitive

#### T3.7: Filter by Type
```python
prompts = list_executables(exec_type="prompt")
assert all(e.type == "prompt" for e in prompts)
```

**Pass criteria:** Filter works

#### T3.8: Filter by Status
```python
active = list_executables(status="active")
assert all(e.status == "active" for e in active)
```

**Pass criteria:** Filter works

---

### 4. Analytics Tests (Accuracy)

#### T4.1: Invocation Logging
```python
# Log invocation
before_count = get_invocation_count("test-001")
log_invocation("test-001", "con_test_123")
after_count = get_invocation_count("test-001")
assert after_count == before_count + 1
```

**Pass criteria:** Count increments

#### T4.2: Stats Accuracy
```python
# Log multiple invocations
for i in range(5):
    log_invocation("test-001", f"con_{i}")

stats = get_stats(days=30)
assert stats["test-001"]["count"] >= 5
```

**Pass criteria:** Stats reflect reality

#### T4.3: Time Range Filtering
```python
# Log invocations with different timestamps
# Query last 7 days
stats = get_stats(days=7)
# Verify only recent invocations counted
```

**Pass criteria:** Time filter works

#### T4.4: Conversation Attribution
```python
log_invocation("test-001", "con_ABC")
invocations = get_invocations_by_conversation("con_ABC")
assert any(i.executable_id == "test-001" for i in invocations)
```

**Pass criteria:** Can trace invocations by conversation

---

### 5. Resilience Tests (Recovery)

#### T5.1: Missing File Graceful Degradation
```python
# Register executable
register_executable("/tmp/test.md", "prompt", "test-missing")
# Delete file
Path("/tmp/test.md").unlink()
# Query should not crash
result = get_executable("test-missing")
assert result is not None  # DB record exists
assert not Path(result.file_path).exists()  # File missing
```

**Pass criteria:** System continues, reports missing file

#### T5.2: DB Corruption Recovery
```bash
# Backup DB
cp executables.db executables.db.backup
# Corrupt DB (truncate mid-transaction)
dd if=/dev/zero of=executables.db bs=1 count=100 seek=5000
# Attempt operation
python3 executable_manager.py list
# Should detect corruption, offer recovery
```

**Pass criteria:** Detects corruption, suggests restore

#### T5.3: FTS Index Rebuild
```sql
-- Drop FTS index
DROP TABLE executables_fts;
-- Rebuild
-- Verify search still works
```

**Pass criteria:** Index rebuilds successfully

#### T5.4: Concurrent Access (if applicable)
```python
# Spawn 10 threads
# Each registers different executable simultaneously
# Verify all 10 registered without corruption
```

**Pass criteria:** No lost writes, no corruption

#### T5.5: Large Dataset Performance
```python
# Register 10,000 executables
for i in range(10000):
    register_executable(f"/tmp/test_{i}.md", "prompt", f"test-{i}")

# Verify search still fast
import time
start = time.time()
results = search_executables("test")
duration = time.time() - start
assert duration < 1.0  # Should be sub-second
```

**Pass criteria:** Performance acceptable at scale

---

### 6. Edge Cases Tests (Robustness)

#### T6.1: Empty Database
```python
# Start with empty DB
conn = get_connection()
conn.execute("DELETE FROM executables")
conn.commit()

# All operations should handle gracefully
assert list_executables() == []
assert search_executables("anything") == []
assert get_stats() == {}
```

**Pass criteria:** No crashes on empty DB

#### T6.2: Very Long Strings
```python
long_description = "A" * 10000
register_executable("/tmp/test.md", "prompt", "test-long", description=long_description)
result = get_executable("test-long")
assert result.description == long_description
```

**Pass criteria:** Handles long text

#### T6.3: Unicode & Special Characters
```python
register_executable(
    "/tmp/test.md", 
    "prompt", 
    "test-unicode",
    name="Test 测试 🚀",
    description="Émojis: 😀 Kanji: 日本語"
)
result = get_executable("test-unicode")
assert "🚀" in result.name
```

**Pass criteria:** Unicode preserved

#### T6.4: Null/None Values
```python
register_executable(
    "/tmp/test.md",
    "prompt",
    "test-nulls",
    description=None,
    category=None,
    tags=None
)
result = get_executable("test-nulls")
assert result.description is None
```

**Pass criteria:** Nulls handled correctly

#### T6.5: Path Edge Cases
```python
# Relative path
# Path with spaces
# Path with special chars
# Symlink
# Non-existent directory
```

**Pass criteria:** All handled gracefully

---

### 7. Integration Tests (End-to-End)

#### T7.1: Full Lifecycle
```python
# Register → Search → Update → Get → Delete
test_id = "lifecycle-test"
register_executable("/tmp/test.md", "prompt", test_id)
results = search_executables("test")
assert any(r.id == test_id for r in results)
update_executable(test_id, status="deprecated")
result = get_executable(test_id)
assert result.status == "deprecated"
delete_executable(test_id)
assert get_executable(test_id) is None
```

**Pass criteria:** Complete workflow succeeds

#### T7.2: Migration Validation
```python
# Verify all 143 prompts from original recipes.jsonl
# are present in executables.db with correct metadata
backup_jsonl = load_jsonl("/path/to/recipes.jsonl.backup")
for entry in backup_jsonl:
    db_entry = get_executable(entry['id'])
    assert db_entry is not None
    assert db_entry.name == entry['name']
    # etc.
```

**Pass criteria:** 100% migration fidelity

#### T7.3: Filesystem Sync
```python
# Add new .md file to Prompts/
new_file = Path("/home/workspace/Prompts/New-Test.md")
new_file.write_text("---\ndescription: Test\n---\n# Test")

# Run sync/reindex
sync_prompts_to_db()

# Verify in DB
result = get_executable("new-test")
assert result is not None
```

**Pass criteria:** New files detected and indexed

---

## Test Execution Strategy

### Phase 1: Smoke Tests (P0 - Run Always)
```bash
# 5 tests, < 30 seconds
- T1.3: File path validity
- T1.4: Unique constraints
- T2.1: Register new
- T3.1: Search precision
- T7.1: Full lifecycle
```

### Phase 2: Core Suite (P1 - Run Before Deploy)
```bash
# All data integrity + CRUD + search tests
# ~20 tests, < 2 minutes
```

### Phase 3: Full Suite (P2 - Run Weekly)
```bash
# All tests including resilience and edge cases
# ~50 tests, < 5 minutes
```

### Phase 4: Continuous Monitoring (Production)
```bash
# Run hourly or after each operation
- DB integrity check
- File path validation
- Stats sanity check
```

---

## Test Implementation

### Option A: pytest Suite
```python
# tests/test_executables.py
import pytest
from N5.scripts.executable_manager import *

@pytest.fixture
def test_db():
    # Setup test database
    yield
    # Teardown

def test_register_executable(test_db):
    # ...
```

### Option B: Shell Script
```bash
#!/bin/bash
# tests/run_tests.sh

echo "=== Executable System Tests ==="
failed=0

# T1.3: File path validity
if python3 -c "from check_paths import validate; validate()"; then
    echo "✓ T1.3: File paths valid"
else
    echo "✗ T1.3: FAILED"
    ((failed++))
fi

# ...

exit $failed
```

### Option C: Inline Validation Script
```python
# N5/scripts/validate_executables.py
# Single-file test runner
```

---

## Success Criteria

### Minimum Viable Testing (MVP)
- [ ] 10 smoke tests pass
- [ ] No data integrity issues
- [ ] Search returns expected results
- [ ] Can register/delete without corruption

### Production Ready
- [ ] 30+ tests passing
- [ ] < 1% false positive rate
- [ ] Runs in < 2 minutes
- [ ] CI/CD integration

### Mature System
- [ ] 50+ tests including edge cases
- [ ] Property-based testing (hypothesis)
- [ ] Performance benchmarks
- [ ] Mutation testing (validates test quality)

---

## Next Steps

1. **Immediate:** Implement smoke tests (T1.3, T1.4, T2.1, T3.1, T7.1)
2. **Short-term:** Core suite (data integrity + CRUD)
3. **Medium-term:** Resilience tests
4. **Long-term:** Continuous monitoring

---

*Test plan by: Vibe Debugger*  
*2025-11-01 02:15 ET*
