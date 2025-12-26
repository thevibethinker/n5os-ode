---
created: 2025-12-17
last_edited: 2025-12-17
version: 1.0
provenance: con_ZnWsOR2cLwCrW6e6
---

# Build Plan: Content Library System Consolidation

## Open Questions
- [ ] ~Do we need to preserve the cutover/patch scripts?~ NO - quarantine them

## Summary
Consolidate fragmented content library system. The canonical DB at `N5/data/content_library.db` is healthy with 121 items. The main script `N5/scripts/content_library_v3.py` works but is missing the `mark_used()` method that `email_composer.py` calls.

## Checklist

### Phase 1: Fix Missing Method
- [x] Add `mark_used()` method to `content_library_v3.py`
- [x] Test email_composer import

### Phase 2: Create Clean Interface
- [x] Rename `content_library_v3.py` → `content_library.py` (canonical name)
- [x] Update all importers to use new name
- [x] Verify all scripts still work

### Phase 3: Quarantine Legacy
- [x] Move cutover/patch scripts to quarantine
- [x] Document what was quarantined
- [x] Clean up pycache references

### Phase 4: Validation
- [x] Test email_composer signature lookup
- [x] Test search functionality
- [x] Test add functionality

## Phase 1: Fix Missing Method

**Affected Files:**
- `N5/scripts/content_library_v3.py`

**Changes:**
Add `mark_used(item_id)` method that updates `last_used_at` timestamp in the database.

**Unit Tests:**
```bash
python3 -c "from content_library_v3 import ContentLibraryV3; lib = ContentLibraryV3(); lib.mark_used('test-id'); print('OK')"
```

## Phase 2: Create Clean Interface

**Affected Files:**
- `N5/scripts/content_library_v3.py` → `N5/scripts/content_library.py`
- `N5/scripts/email_composer.py`
- `N5/scripts/auto_populate_content.py`
- `N5/scripts/b_block_parser.py`
- `N5/scripts/email_corrections.py`
- `N5/scripts/exa_research.py`
- `N5/scripts/knowledge_integrator.py`
- `N5/scripts/knowledge_preflight.py`
- `N5/scripts/luma_register.py`

**Changes:**
1. Rename main file to `content_library.py`
2. Update imports from `from content_library_v3 import ContentLibraryV3` to `from content_library import ContentLibrary`
3. Rename class from `ContentLibraryV3` to `ContentLibrary`

**Unit Tests:**
```bash
python3 -c "from content_library import ContentLibrary; lib = ContentLibrary(); print(lib.stats())"
```

## Phase 3: Quarantine Legacy

**Affected Files:**
- `N5/scripts/content_library_v3_cutover.py` → quarantine
- `N5/scripts/content_library_v3_patch_001.py` → quarantine
- `N5/scripts/migrate_content_library_to_db.py` → quarantine
- `N5/scripts/knowledge_import_canon_contentlibrary.py` → quarantine

**Changes:**
Move to `N5/quarantine/deprecated-content-library/YYYYMMDD-HHMMSS/`

## Phase 4: Validation

**Test Commands:**
```bash
# Test import
python3 -c "import sys; sys.path.insert(0, '/home/workspace/N5/scripts'); from content_library import ContentLibrary; lib = ContentLibrary(); print('Stats:', lib.stats())"

# Test search
python3 /home/workspace/N5/scripts/content_library.py search --query "signature" --limit 5

# Test email_composer import
python3 -c "import sys; sys.path.insert(0, '/home/workspace/N5/scripts'); from email_composer import EmailComposer; print('EmailComposer OK')"
```

## Success Criteria
- [x] `content_library.db` has 121+ items
- [x] `mark_used()` method works
- [x] Single canonical `content_library.py` in `N5/scripts/`
- [x] All 9 dependent scripts import successfully
- [x] email_composer can look up signatures
- [x] Legacy files quarantined

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Breaking existing scripts | Keep v3 as symlink during transition |
| Missing methods | Audit all callers before renaming |
| Lost functionality | Quarantine instead of delete |


