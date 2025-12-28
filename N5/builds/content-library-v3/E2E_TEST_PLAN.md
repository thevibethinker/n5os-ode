---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
---

# Content Library v3 – End-to-End Test Plan

**Purpose:** Validate the v3 system works correctly before and after cutover.  
**Orchestrator:** con_jYGYNfcv76UTmolk

---

## Test Phases

| Phase | Name | When | Purpose |
|-------|------|------|---------|
| 1 | Pre-Cutover Validation | Before `--execute` | Confirm v3 DB + CLI work with `.new` scripts |
| 2 | Cutover Execution | Run `--execute --force` | Swap `.new` → live, create `.bak` |
| 3 | Post-Cutover Smoke | Immediately after cutover | Confirm live scripts import and run |
| 4 | Integration Tests | After smoke passes | Test real workflows end-to-end |
| 5 | Rollback Test (optional) | After integration passes | Verify `.bak` rollback works |

---

## Phase 1: Pre-Cutover Validation

**Goal:** Confirm v3 database, CLI, and `.new` scripts work before making any destructive changes.

### 1.1 Database Integrity

```bash
# Check DB exists and has expected structure
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db '.tables'
# Expected: items tags topics item_topics blocks block_topics knowledge_refs schema_version

# Check item counts
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db \
  "SELECT COUNT(*) as total, source FROM items GROUP BY source;"
# Expected: ~67 n5_links, ~16 personal_cl, some 'new'

# Check tag counts
sqlite3 /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db \
  "SELECT COUNT(*) FROM tags;"
# Expected: ~362+
```

### 1.2 CLI Basic Operations

```bash
CLI="/home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py"

# Stats
python3 "$CLI" stats

# Search by query
python3 "$CLI" search --query "calendly"

# Search by type
python3 "$CLI" search --type link --limit 5

# Search by tag
python3 "$CLI" search --tag "category=scheduling"

# Get by ID
python3 "$CLI" get trial_code_general

# Lint
python3 "$CLI" lint
```

### 1.3 N5 Consumer Scripts (import test only)

```bash
# Test that .new scripts can be imported without error
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')

# Rename .new to temp .py for import test
from pathlib import Path

scripts = [
    'email_composer',
    'auto_populate_content', 
    'b_block_parser',
    'email_corrections',
]

# Just test that the .new files are syntactically valid
import py_compile
for s in scripts:
    path = Path(f'/home/workspace/N5/scripts/{s}.py.new')
    if path.exists():
        py_compile.compile(str(path), doraise=True)
        print(f'✓ {s}.py.new compiles OK')
"
```

### 1.4 Ingest Scripts (syntax check)

```bash
python3 -c "
import py_compile
from pathlib import Path

scripts = [
    '/home/workspace/Personal/Knowledge/ContentLibrary/scripts/ingest.py.new',
    '/home/workspace/Personal/Knowledge/ContentLibrary/scripts/enhance.py.new',
    '/home/workspace/Personal/Knowledge/ContentLibrary/scripts/summarize.py.new',
    '/home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_to_knowledge.py.new',
]

for s in scripts:
    if Path(s).exists():
        py_compile.compile(s, doraise=True)
        print(f'✓ {Path(s).name} compiles OK')
"
```

---

## Phase 2: Cutover Execution

**Goal:** Swap `.new` files to live, creating `.bak` backups.

### 2.1 Dry Run (final check)

```bash
python3 /home/workspace/N5/scripts/content_library_v3_cutover.py --force
# Review output - should list 10 planned moves
```

### 2.2 Execute

```bash
python3 /home/workspace/N5/scripts/content_library_v3_cutover.py --execute --force
```

### 2.3 Verify Files Moved

```bash
# Check .new files are gone
ls /home/workspace/N5/scripts/*.new 2>/dev/null || echo "No .new files in N5/scripts (good)"
ls /home/workspace/Personal/Knowledge/ContentLibrary/scripts/*.new 2>/dev/null || echo "No .new files in PCL/scripts (good)"

# Check .bak files exist
ls /home/workspace/N5/scripts/*.bak
ls /home/workspace/Personal/Knowledge/ContentLibrary/scripts/*.bak
```

---

## Phase 3: Post-Cutover Smoke Tests

**Goal:** Confirm live scripts import and basic operations work.

### 3.1 Import Tests

```bash
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')

from content_library_v3 import ContentLibraryV3
from content_library import ContentLibrary  # backwards compat wrapper

# N5 consumers
import email_composer
import auto_populate_content
import b_block_parser
import email_corrections

# PCL scripts
import ingest
import enhance
import summarize
import content_to_knowledge

print('✓ All imports successful')
"
```

### 3.2 CLI Smoke

```bash
CLI="/home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py"

python3 "$CLI" stats
python3 "$CLI" search --query "trial" --type link
python3 "$CLI" get trial_code_general
python3 "$CLI" lint
```

---

## Phase 4: Integration Tests

**Goal:** Test real workflows that depend on Content Library.

### 4.1 Lookup Resolution (simulate follow-up email)

```bash
# Simulate: "I promised to send a trial link"
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')
from content_library_v3 import ContentLibraryV3

lib = ContentLibraryV3()

# Search for trial link
results = lib.search(query='trial', item_type='link')
assert len(results) > 0, 'Should find trial links'

# Get specific item
item = lib.get('trial_code_general')
assert item is not None, 'trial_code_general should exist'
assert item.get('url'), 'Should have URL'

print(f'✓ Found trial link: {item[\"title\"]}')
print(f'  URL: {item[\"url\"]}')
"
```

### 4.2 Bio Snippet Lookup

```bash
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')
from content_library_v3 import ContentLibraryV3

lib = ContentLibraryV3()

# Search for bio
results = lib.search(query='bio', item_type='snippet')
print(f'Found {len(results)} bio snippets')

for r in results[:3]:
    print(f'  - {r[\"id\"]}: {r[\"title\"][:50]}...')
"
```

### 4.3 Ingest New Item (dry run)

```bash
# Create a test markdown file
cat > /tmp/test_article.md << 'EOF'
---
title: Test Article for E2E
---

This is a test article for Content Library v3 E2E testing.
EOF

# Test ingest (if ingest.py supports dry-run or we can just test the import)
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')
from content_library_v3 import ContentLibraryV3

lib = ContentLibraryV3()

# Add a test item
lib.add(
    id='e2e_test_article',
    item_type='article',
    title='E2E Test Article',
    url='https://example.com/test',
    content='This is a test article for E2E validation.',
    source='new',
)

# Verify it exists
item = lib.get('e2e_test_article')
assert item is not None, 'Test item should exist'
print(f'✓ Added and retrieved test item: {item[\"id\"]}')

# Clean up (deprecate, don't delete)
lib.deprecate('e2e_test_article')
print('✓ Deprecated test item')
"
```

### 4.4 N5 Wrapper Compatibility

```bash
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
from content_library import ContentLibrary

# This should use v3 under the hood
lib = ContentLibrary()

# Basic operations should still work
items = lib.search(item_type='link', limit=5)
print(f'✓ N5 wrapper found {len(items)} links via v3 backend')
"
```

---

## Phase 5: Rollback Test (Optional)

**Goal:** Verify we can restore from `.bak` if needed.

### 5.1 Manual Rollback Procedure

```bash
# To rollback a single script:
# mv /home/workspace/N5/scripts/email_composer.py /home/workspace/N5/scripts/email_composer.py.v3
# mv /home/workspace/N5/scripts/email_composer.py.bak /home/workspace/N5/scripts/email_composer.py

# To rollback all:
for f in /home/workspace/N5/scripts/*.bak; do
    target="${f%.bak}"
    if [ -f "$target" ]; then
        mv "$target" "${target}.v3"
    fi
    mv "$f" "$target"
done

for f in /home/workspace/Personal/Knowledge/ContentLibrary/scripts/*.bak; do
    target="${f%.bak}"
    if [ -f "$target" ]; then
        mv "$target" "${target}.v3"
    fi
    mv "$f" "$target"
done
```

### 5.2 Verify Rollback

```bash
# After rollback, old imports should work
python3 -c "
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
from content_library import ContentLibrary
lib = ContentLibrary()
print('✓ Old ContentLibrary import works after rollback')
"
```

---

## Test Results Checklist

### Phase 1: Pre-Cutover
- [ ] DB tables exist (items, tags, topics, etc.)
- [ ] Item counts match expected (~83 total)
- [ ] CLI stats runs
- [ ] CLI search returns results
- [ ] CLI get returns specific item
- [ ] CLI lint runs (may report data issues, not script issues)
- [ ] `.new` scripts compile without syntax errors

### Phase 2: Cutover
- [ ] Dry run shows 10 planned moves
- [ ] Execute completes without error
- [ ] `.new` files removed
- [ ] `.bak` files created

### Phase 3: Post-Cutover Smoke
- [ ] All imports succeed
- [ ] CLI operations work

### Phase 4: Integration
- [ ] Trial link lookup works
- [ ] Bio snippet lookup works
- [ ] Add/deprecate item works
- [ ] N5 wrapper compatibility works

### Phase 5: Rollback (Optional)
- [ ] Rollback procedure documented
- [ ] Rollback verified working (if tested)

---

## Known Issues to Track

From W5 lint output:
- 2 `meeting_*` items have `content_path` pointing to missing files
- These are **data issues**, not v3 migration issues
- Clean up separately after cutover succeeds

---

*E2E Test Plan by Vibe Debugger | 2025-12-02*

