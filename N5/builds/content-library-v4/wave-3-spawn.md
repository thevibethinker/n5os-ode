---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_5tYCDyhaRiYR0EGI
build: content-library-v4
wave: 3
---

# Content Library v4 — Wave 3 Worker Assignment

## Context

You are executing Wave 3 of the Content Library v4 redesign.

**Completed:**
- ✅ Wave 1: Schema migrated, files consolidated to `Knowledge/content-library/`
- ✅ Wave 2: Ingest pipeline created, 9 articles backfilled, CLI upgraded
- ✅ Debug: Fixed CLI `--type` argument to use `content_type` column

**Current state:**
- 136 items in DB (114 links, 13 snippets, 9 articles)
- All articles have `source_file_path` set
- V's 3 Medium articles tagged `vrijen-authored`
- CLI commands working: `list-types`, `search --type article`, `ingest`, `sync`

**Build workspace:** `file 'N5/builds/content-library-v4/'`  
**Orchestrator:** `python3 N5/scripts/build_orchestrator_v2.py`

---

## Your Assignment: Execute Wave 3 Workers (2 total)

Both workers can run in parallel.

---

### Worker 1: `worker_semantic_memory` (Memory Integration)

**Component:** memory_integration  
**Estimated time:** 1 hour  
**Output:** `N5/cognition/n5_memory_client.py` (updated)

**Task:**
Fix the semantic memory client to use correct paths for content library:

**Current problem (line 76-79 of n5_memory_client.py):**
```python
"content-library": {
    "path_prefixes": [
        "/home/workspace/Knowledge/content-library/",
        "/home/workspace/Personal/Knowledge/ContentLibrary/",  # ← STALE PATH (doesn't exist)
```

**Required changes:**
1. Remove the stale `Personal/Knowledge/ContentLibrary/` path
2. Keep `Knowledge/content-library/` as the only path
3. Verify semantic search works for content library articles

**Test after fix:**
```bash
# This should find the RLM article
python3 -c "
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()
results = client.search('recursive language models', domain='content-library', limit=5)
for r in results:
    print(r.get('path') or r.get('title'))
"
```

**Acceptance criteria:**
- [ ] No references to `Personal/Knowledge/ContentLibrary/` in memory client
- [ ] `content-library` profile points only to `Knowledge/content-library/`
- [ ] Semantic search for "RLM" or "recursive language" finds the article
- [ ] No errors on memory client initialization

**When complete:**
```bash
python3 N5/scripts/build_orchestrator_v2.py complete --project content-library-v4 --worker worker_semantic_memory
```

---

### Worker 2: `worker_auto_ingest_hook` (Automation)

**Component:** automation  
**Estimated time:** 1 hour  
**Output:** Zo rule + optional helper script

**Task:**
Create automation so that when `save_webpage` saves an article, it gets ingested into the Content Library system automatically.

**Problem:**
- Zo's `save_webpage` tool saves to `Articles/` by default
- But our canonical location is `Knowledge/content-library/articles/`
- We need to bridge this gap

**Recommended approach (Zo Rule):**
Create a Zo rule that triggers after `save_webpage`:

```markdown
# Rule: Auto-ingest saved articles

**Condition:** After save_webpage saves a file to Articles/

**Instruction:** 
After using save_webpage, automatically:
1. Run `python3 N5/scripts/content_ingest.py <saved_file> --type article --move`
2. This moves the file to `Knowledge/content-library/articles/` and creates a DB record
3. Confirm: "Article ingested to Content Library"
```

**Alternative approach (Watcher script):**
If a rule doesn't work reliably, create a simple watcher:
```bash
# N5/scripts/article_watcher.py
# Watches Articles/ and auto-ingests new files
```

**Test the flow:**
1. Run `save_webpage` on any article URL
2. Verify file appears in `Knowledge/content-library/articles/`
3. Verify DB record exists: `python3 N5/scripts/content_library.py search --type article`

**Acceptance criteria:**
- [ ] Zo rule created at `N5/rules/auto_ingest_articles.md` OR watcher script works
- [ ] After `save_webpage`, content appears in DB within same conversation
- [ ] File ends up in canonical location `Knowledge/content-library/articles/`
- [ ] No manual intervention required

**When complete:**
```bash
python3 N5/scripts/build_orchestrator_v2.py complete --project content-library-v4 --worker worker_auto_ingest_hook
```

---

## Execution Notes

Both workers are independent and can run in parallel or sequence.

**Worker 1** is a straightforward code fix—just remove the stale path.

**Worker 2** requires a design decision:
- **Option A (Rule):** Simpler, but depends on Zo reliably executing post-action rules
- **Option B (Watcher):** More robust, but adds a background process

Recommend trying Option A first. If it doesn't work reliably, fall back to Option B.

---

## After Wave 3

Wave 4 workers are:
- `worker_docs_update` — Update all documentation
- `worker_cleanup` — Final cleanup and verification

These depend on Wave 3 completion.

---

## Completion Checklist

After both workers are done:

1. [ ] Run `python3 N5/scripts/build_orchestrator_v2.py status --project content-library-v4` to verify Wave 3 complete
2. [ ] Test semantic search: search for "recursive language models" in content-library domain
3. [ ] Test auto-ingest: use `save_webpage` on a new article and verify it appears in DB
4. [ ] Report back: "Wave 3 complete. Ready for Wave 4."

---

## Reference Files

- **Build plan:** `file 'N5/builds/content-library-v4/plan.json'`
- **Memory client:** `file 'N5/cognition/n5_memory_client.py'`
- **Ingest script:** `file 'N5/scripts/content_ingest.py'`
- **CLI:** `file 'N5/scripts/content_library.py'`
- **Database:** `file 'N5/data/content_library.db'`
- **Content location:** `file 'Knowledge/content-library/'`

