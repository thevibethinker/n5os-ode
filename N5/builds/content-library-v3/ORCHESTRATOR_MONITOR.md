---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
---

# Content Library v3 – Orchestrator Monitor

**Project:** Content Library v3 Migration  
**Orchestrator Conversation:** con_jYGYNfcv76UTmolk  
**Start Time:** 2025-12-02 21:55 ET  
**Target Completion:** 2025-12-02 24:00 ET (~2 hours)

---

## Worker Status Tracker

| Worker | Task | Status | Conversation | Started | Completed | Notes |
|--------|------|--------|--------------|---------|-----------|-------|
| W1 | Schema + Migration | ✅ Complete | con_8pWsNkOn0aQvkdtN | | 22:19 | 83 items, 0 collisions |
| W2 | Unified CLI/API | ✅ Complete | (this convo) | | | CLI + API + wrapper ready |
| W3 | Consumer Updates | ✅ Complete | | | | 6 N5 scripts updated to .new |
| W4 | Ingest Scripts | ✅ Complete | con_oElk3w1YC1r8JUmH | | | 4 PCL scripts updated to .new |
| W5 | Documentation | ✅ Complete | | | 23:47 | 4 .new docs + reasoning pattern |

---

## Dependency Graph

```
W1 (Schema/Migration)
    │
    ▼
W2 (CLI/API)
    │
    ├──────────┐
    ▼          ▼
W3 (Consumers) W4 (Ingest)
    │          │
    └────┬─────┘
         ▼
    W5 (Documentation)
```

**Parallel Execution:**
- W1 → W2: Sequential (W2 needs schema)
- W2 → W3, W4: Parallel (both need CLI)
- W3, W4 → W5: Sequential (docs need everything)

---

## Launch Sequence

### Phase 1: Foundation (Sequential)
1. **Launch W1** – Schema & Migration
2. **Validate W1** – Check DB exists, counts correct
3. **Launch W2** – CLI/API
4. **Validate W2** – Check CLI commands work

### Phase 2: Implementation (Parallel)
5. **Launch W3 + W4** simultaneously
6. **Validate W3** – Check consumer scripts import correctly
7. **Validate W4** – Check ingest/enhance work

### Phase 3: Documentation
8. **Launch W5** – Documentation
9. **Validate W5** – Check all docs created

### Phase 4: Cutover
10. **Backup old files**
11. **Swap .new files**
12. **Update any remaining paths**
13. **Final validation**
14. **Archive old files**

---

## Deliverables Checklist

### W1: Schema + Migration
- [ ] `Personal/Knowledge/ContentLibrary/content-library-v3.db`
- [ ] `Personal/Knowledge/ContentLibrary/scripts/migrate_to_v3.py`
- [ ] `Personal/schemas/content-library-v3.schema.json`
- [ ] Migration report: 83 items (67 N5 + 16 Personal)

### W2: CLI/API
- [ ] `Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py`
- [ ] `N5/scripts/content_library.py.new` (wrapper)
- [ ] All CLI commands working

### W3: Consumer Updates
- [ ] `N5/scripts/email_composer.py.new`
- [ ] `N5/scripts/content_library_db.py.new`
- [ ] Other affected scripts identified and updated

### W4: Ingest Scripts
- [ ] `Personal/Knowledge/ContentLibrary/scripts/ingest.py.new`
- [ ] `Personal/Knowledge/ContentLibrary/scripts/enhance.py.new`
- [ ] `Personal/Knowledge/ContentLibrary/scripts/summarize.py.new`

### W5: Documentation
- [ ] `Personal/Knowledge/ContentLibrary/README.md.new`
- [ ] `Documents/System/guides/content-library-system.md.new`
- [ ] `Documents/System/guides/content-library-quickstart.md.new`
- [ ] `Personal/Knowledge/Architecture/specs/systems/content_library_integration.md.new`

---

## Validation Commands

### After W1 (Schema + Migration)
```bash
# Check database exists
ls -lh /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db

# Check item count
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db "SELECT COUNT(*) FROM items;"
# Expected: 83

# Check by source
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db "SELECT source, COUNT(*) FROM items GROUP BY source;"
# Expected: n5_links: 67, personal_cl: 16

# Check types
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db "SELECT item_type, COUNT(*) FROM items GROUP BY item_type;"
```

### After W2 (CLI/API)
```bash
# Test search
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py search --query "calendly"

# Test stats
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py stats

# Test get
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py get trial_code_general

# Test lint
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py lint
```

### After W3 (Consumer Updates)
```bash
# Test wrapper import
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
# Test the .new wrapper
"

# Verify no import errors in updated scripts
```

### After W4 (Ingest Scripts)
```bash
# Test ingest (dry run with test item)
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/ingest.py.new \
  "https://test.com" "Test Item" --type article --source discovered --topics test

# Verify item was added
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db \
  "SELECT id, title FROM items WHERE title LIKE '%Test Item%';"
```

### After W5 (Documentation)
```bash
# Verify all .new doc files exist
ls /home/workspace/Personal/Knowledge/ContentLibrary/README.md.new
ls /home/workspace/Documents/System/guides/content-library-system.md.new
ls /home/workspace/Documents/System/guides/content-library-quickstart.md.new
ls /home/workspace/Personal/Knowledge/Architecture/specs/systems/content_library_integration.md.new
```

---

## Final Integration Test

After all workers complete, before cutover:

```bash
# Full workflow test
# 1. Search for existing link
python3 content_library_v3.py search --type link --query "calendly" | head -5

# 2. Search for existing article
python3 content_library_v3.py search --type article | head -5

# 3. Add new test item
python3 content_library_v3.py add --id integration_test_link --type link --title "Integration Test" --url "https://test.integration"

# 4. Verify added
python3 content_library_v3.py get integration_test_link

# 5. Deprecate test item
python3 content_library_v3.py deprecate integration_test_link

# 6. Stats
python3 content_library_v3.py stats

# 7. Lint
python3 content_library_v3.py lint
```

---

## Cutover Procedure

### Step 1: Backup Old Files
```bash
mkdir -p /home/workspace/N5/data/archive
mkdir -p /home/workspace/Personal/Knowledge/ContentLibrary/archive

cp /home/workspace/N5/data/content_library.db /home/workspace/N5/data/archive/content_library.db.pre_v3
cp /home/workspace/Personal/Knowledge/ContentLibrary/content-library.db /home/workspace/Personal/Knowledge/ContentLibrary/archive/content-library.db.pre_v3
```

### Step 2: Swap .new Files
```bash
# Scripts
mv /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py.new /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py 2>/dev/null || true
mv /home/workspace/Personal/Knowledge/ContentLibrary/scripts/ingest.py.new /home/workspace/Personal/Knowledge/ContentLibrary/scripts/ingest.py
mv /home/workspace/Personal/Knowledge/ContentLibrary/scripts/enhance.py.new /home/workspace/Personal/Knowledge/ContentLibrary/scripts/enhance.py

# N5 scripts
mv /home/workspace/N5/scripts/content_library.py.new /home/workspace/N5/scripts/content_library.py

# Documentation
mv /home/workspace/Personal/Knowledge/ContentLibrary/README.md.new /home/workspace/Personal/Knowledge/ContentLibrary/README.md
mv /home/workspace/Documents/System/guides/content-library-system.md.new /home/workspace/Documents/System/guides/content-library-system.md
mv /home/workspace/Documents/System/guides/content-library-quickstart.md.new /home/workspace/Documents/System/guides/content-library-quickstart.md
mv /home/workspace/Personal/Knowledge/Architecture/specs/systems/content_library_integration.md.new /home/workspace/Personal/Knowledge/Architecture/specs/systems/content_library_integration.md
```

### Step 3: Final Validation
```bash
# Run integration test again
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py stats
```

---

## Blocker Resolution

If any worker encounters issues:

1. **Worker reports** in their conversation
2. **V notifies orchestrator** with details
3. **Orchestrator analyzes** – check worker brief, validate assumptions
4. **Create patch brief** if needed
5. **Re-run affected worker**
6. **Re-validate**

---

## Rollback Procedure

If migration fails at any point:

```bash
# Delete v3 database
rm /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db

# Remove any .new files
find /home/workspace -name "*.new" -delete

# Old system is still intact – no data loss
```

---

## Success Criteria

Before declaring COMPLETE:

- [ ] 83 items in v3 database (67 + 16)
- [ ] All CLI commands working
- [ ] Ingest workflow working
- [ ] Consumer scripts updated
- [ ] Documentation complete
- [ ] Integration test passed
- [ ] V confirms: "I can add articles and look up links from one place"

---

## Completion Checklist

- [x] Migration script created and tested
- [x] Unified CLI/API created
- [x] Consumer scripts updated (.new)
- [x] Ingest scripts updated (.new)
- [x] Documentation complete (.new)
- [x] Cutover script created and tested (dry-run)
- [x] E2E Test Plan created
- [ ] Pre-cutover validation (Phase 1)
- [ ] Cutover execution (Phase 2)
- [ ] Post-cutover smoke (Phase 3)
- [ ] Integration tests (Phase 4)
- [ ] V confirms: "I can add articles and look up links from one place"

---

## E2E Test Plan

See `file 'N5/builds/content-library-v3/E2E_TEST_PLAN.md'` for full test plan.

**Summary:**
1. Phase 1: Pre-cutover validation (DB, CLI, syntax checks)
2. Phase 2: Cutover execution (`--execute --force`)
3. Phase 3: Post-cutover smoke (imports, CLI)
4. Phase 4: Integration tests (lookup, ingest, wrapper compat)
5. Phase 5: Rollback test (optional)

---

## Notes

_Space for runtime notes during orchestration_

---

**Orchestrator:** con_jYGYNfcv76UTmolk  
**Created:** 2025-12-02 22:08 ET





