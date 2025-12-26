---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
status: IMPACT MAP
author: Vibe Architect
---

# Content Library v3: Impact Map

This document lists **every file** that the v3 migration touches, organized by action type.

---

## 1. NEW FILES TO CREATE

These are net-new files. No existing file is modified.

| New File Path | Purpose |
|---------------|---------|
| `Personal/Knowledge/ContentLibrary/content-library-v3.db` | Unified database |
| `Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py` | Unified CLI + API |
| `Personal/Knowledge/ContentLibrary/scripts/migrate_to_v3.py` | Migration script |
| `Personal/schemas/content-library-v3.schema.json` | JSON schema for v3 |
| `N5/scripts/lint_content_library.py` | Lint/validation for unified CL (rename from lint_js_shell_tweets.py) |

---

## 2. FILES TO REPLACE WHOLESALE (Copy-Not-Edit)

For each file below: create a `.new` version → test → swap at cutover.

### 2.1 Scripts (Core)

| Current File | New File | What Changes |
|--------------|----------|--------------|
| `N5/scripts/content_library.py` | `N5/scripts/content_library.py.new` | Thin wrapper pointing to v3 CLI, or full rewrite |
| `N5/scripts/content_library_db.py` | `N5/scripts/content_library_db.py.new` | Thin wrapper or delete (functions moved to v3) |
| `Personal/Knowledge/ContentLibrary/scripts/ingest.py` | `...ingest.py.new` | Update to write to v3 schema |
| `Personal/Knowledge/ContentLibrary/scripts/enhance.py` | `...enhance.py.new` | Update to read/write v3 schema |
| `Personal/Knowledge/ContentLibrary/scripts/summarize.py` | `...summarize.py.new` | Update to read/write v3 schema |
| `Personal/Knowledge/ContentLibrary/scripts/content_to_knowledge.py` | `...content_to_knowledge.py.new` | Update to read v3 schema |
| `Personal/Knowledge/ContentLibrary/query/cli.py` | `...query/cli.py.new` | Update to query v3 schema |
| `Personal/Knowledge/ContentLibrary/query/search.py` | `...query/search.py.new` | Update to query v3 schema |
| `Personal/Knowledge/ContentLibrary/cli.py` | `...cli.py.new` | Update to use v3 |

### 2.2 Documentation

| Current File | New File | What Changes |
|--------------|----------|--------------|
| `Personal/Knowledge/ContentLibrary/README.md` | `...README.md.new` | Full rewrite for v3 |
| `Documents/System/guides/content-library-system.md` | `...content-library-system.md.new` | Full rewrite for v3 |
| `Documents/System/guides/content-library-quickstart.md` | `...content-library-quickstart.md.new` | Full rewrite for v3 |
| `Personal/Knowledge/Architecture/specs/systems/content_library_integration.md` | `...content_library_integration.md.new` | Full rewrite for v3 |

---

## 3. FILES TO EDIT (After Cutover)

These files have small changes (import paths, references). Edit in place after v3 is live.

### 3.1 N5 Scripts (Import Path Updates)

| File | Line(s) | Current | New |
|------|---------|---------|-----|
| `N5/scripts/email_composer.py` | ~imports | `from content_library...` | `from Personal.Knowledge.ContentLibrary.scripts.content_library_v3 import ContentLibraryV3` or adjusted path |
| `N5/scripts/knowledge_integrator.py` | ~imports | `content_library` imports | Update to v3 |
| `N5/scripts/auto_populate_content.py` | ~imports | `content_library` imports | Update to v3 |
| `N5/scripts/voice_transformer.py` | ~imports | `content_library` imports | Update to v3 |
| `N5/scripts/email_corrections.py` | ~imports | `content_library` imports | Update to v3 |
| `N5/scripts/document_media_curator.py` | ~imports | `content_library` imports | Update to v3 |
| `N5/scripts/knowledge_preflight.py` | ~imports (if any) | Check for CL imports | Update to v3 |
| `N5/scripts/b_block_parser.py` | ~imports (if any) | Check for CL imports | Update to v3 |
| `N5/scripts/knowledge_import_canon_contentlibrary.py` | ~imports | CL imports | Update to v3 |

### 3.2 Preference/Config Files

| File | Section | Change |
|------|---------|--------|
| `N5/prefs/knowledge/lookup.md` | Content Library references | Update paths |

### 3.3 Prompts

| File | Section | Change |
|------|---------|--------|
| `Prompts/Follow-Up Email Generator.prompt.md` | Content Library lookup instructions | Update path + CLI syntax |

### 3.4 System Docs

| File | Section | Change |
|------|---------|--------|
| `Documents/System/DOCUMENTS_MEDIA_SYSTEM.md` | Content Library mentions | Update to v3 paths |

---

## 4. FILES TO ARCHIVE

Move to archive after cutover is confirmed stable.

| Current Location | Archive Location |
|------------------|------------------|
| `N5/data/content_library.db` | `N5/data/archive/content_library.db.pre_v3` |
| `Personal/Knowledge/ContentLibrary/content-library.db` | `Personal/Knowledge/ContentLibrary/archive/content-library.db.pre_v3` |
| `Personal/Knowledge/ContentLibrary/content-library.json` | `Personal/Knowledge/ContentLibrary/archive/content-library.json.pre_v3` |
| `N5/scripts/migrate_content_library_to_db.py` | `N5/scripts/archive/migrate_content_library_to_db.py` |
| `N5/prefs/communication/content-library.json` (if exists) | `N5/prefs/communication/archive/content-library.json` |
| `N5/prefs/communication/essential-links.json` (if exists) | `N5/prefs/communication/archive/essential-links.json` |

---

## 5. FILES TO DELETE (Eventually)

After 30 days of stable operation:

- All `.pre_v3` backup files
- Any `.new` files that were swapped in

---

## 6. SPECIAL HANDLING

### 6.1 Content Files

The `Personal/Knowledge/ContentLibrary/content/*.md` files **do not change**. They are referenced by `content_path` in the new schema exactly as before.

### 6.2 Duplicate ID Resolution

If migration detects ID collision:

| Collision Type | Resolution |
|----------------|------------|
| N5 `link` with same ID as Personal `article` | Prefix N5 item: `n5_<id>` |
| Both have same title but different IDs | No action needed |
| True duplicate (same URL in both) | Keep one, note the other as deprecated |

### 6.3 JSON Schema Files

| File | Action |
|------|--------|
| `Personal/schemas/content-library-entry.schema.json` | Keep as v1 reference |
| `Personal/schemas/content-library-v2.schema.json` | Keep as v2 reference |
| `Personal/schemas/content-library-v3.schema.json` | NEW (create) |

---

## 7. EXECUTION ORDER

### Phase 1: Create (No Risk)
1. Create `content-library-v3.db` with empty schema
2. Create `content_library_v3.py` CLI
3. Create `migrate_to_v3.py` script
4. Create `content-library-v3.schema.json`

### Phase 2: Migrate Data (No Risk)
1. Run migration script (reads old DBs, writes to new)
2. Validate counts
3. Validate search works

### Phase 3: Create .new Versions (No Risk)
1. For each script in Section 2.1: create `.new` version
2. For each doc in Section 2.2: create `.new` version
3. Test all `.new` versions against v3 DB

### Phase 4: Cutover (Reversible)
1. Backup old DBs to archive locations
2. For each `.new` file: `mv file.new file`
3. Update import paths in Section 3 files
4. Test everything

### Phase 5: Cleanup
1. Delete `.new` files (already swapped)
2. Archive old files per Section 4
3. Update SESSION_STATE

---

## 8. ROLLBACK PROCEDURE

At any point before Phase 5:

```bash
# If v3 is broken, restore old system:
# 1. Delete or rename v3 files
rm Personal/Knowledge/ContentLibrary/content-library-v3.db
mv Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py.broken

# 2. Restore any .new files that were swapped
# (If cutover happened, restore from archive)
mv N5/data/archive/content_library.db.pre_v3 N5/data/content_library.db

# 3. Revert import path changes in Section 3 files
# (git checkout or manual revert)

# Old system is now live again. No data loss.
```

---

## 9. SUCCESS CRITERIA

Before declaring migration complete:

- [ ] `content-library-v3.db` contains 83 items (67 + 16)
- [ ] `python3 .../content_library_v3.py search --query "calendly"` returns expected links
- [ ] `python3 .../content_library_v3.py search --type article` returns articles
- [ ] `python3 .../content_library_v3.py ingest --url <new_url> --type social-post --title "test"` works
- [ ] Email composer successfully queries v3 for links
- [ ] Follow-up generator successfully queries v3 for links
- [ ] No errors in logs for 1 hour after cutover
- [ ] V confirms: "I can add articles and look up links from one place"

---

*Impact Map by Vibe Architect | 2025-12-02*

