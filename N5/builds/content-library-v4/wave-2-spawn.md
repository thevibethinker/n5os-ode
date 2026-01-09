---
created: 2026-01-09
last_edited: 2026-01-09
version: 1
provenance: con_5tYCDyhaRiYR0EGI
build: content-library-v4
wave: 2
---
# Content Library v4 — Wave 2 Worker Assignment

## Context

You are executing Wave 2 of the Content Library v4 redesign. Wave 1 is complete:
- ✅ Schema migrated: `type` → `content_type`, new columns added
- ✅ Files consolidated: All articles now in `Knowledge/content-library/articles/`
- ✅ Protection: `.n5protected` in place

**Build workspace:** `file 'N5/builds/content-library-v4/'`  
**Orchestrator:** `python3 N5/scripts/build_orchestrator_v2.py`

---

## Your Assignment: Execute Wave 2 Workers (3 total)

Wave 2 has dependencies on Wave 1 (complete). Execute in order:
1. `worker_ingest_script` — Create the ingest pipeline
2. `worker_backfill` — Backfill existing content (depends on ingest script)
3. `worker_cli_upgrade` — Upgrade CLI (depends on ingest script)

Workers 2 and 3 can run in parallel after worker 1 is done.

---

### Worker 1: `worker_ingest_script` (Ingest Pipeline)

**Component:** ingest_pipeline  
**Estimated time:** 2 hours  
**Output:** `N5/scripts/content_ingest.py`

**Task:**
Create a script that ingests content files into the Content Library:

```bash
# Example usage
python3 N5/scripts/content_ingest.py /path/to/article.md --type article
python3 N5/scripts/content_ingest.py /path/to/deck.pdf --type deck --dry-run
python3 N5/scripts/content_ingest.py /path/to/file.md --move  # Moves to canonical location
```

**Requirements:**
1. Takes a file path as input
2. Extracts metadata from YAML frontmatter if present (title, tags, created date)
3. Auto-generates title from filename if no frontmatter
4. Creates DB record in `N5/data/content_library.db` with:
   - `id`: UUID
   - `title`: From frontmatter or filename
   - `content_type`: From `--type` flag or auto-detect from path
   - `source_file_path`: Relative path from workspace root
   - `ingested_at`: Current timestamp
   - `word_count`: Count words in file (for text files)
   - `tags`: From frontmatter or empty
5. `--dry-run` flag shows what would happen without writing
6. `--move` flag relocates file to canonical path (`Knowledge/content-library/<type>/`)
7. Logs to `N5/runtime/runs/content-ingest/YYYY-MM-DD/`

**Auto-detect logic:**
- Path contains `/articles/` → type = `article`
- Path contains `/decks/` → type = `deck`
- Path contains `/papers/` → type = `paper`
- File extension `.pdf` in decks/ → type = `deck`
- Default: `article`

**Current schema (for reference):**
```sql
CREATE TABLE items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL,
    content TEXT,
    url TEXT,
    source TEXT,
    source_url TEXT,
    source_file_path TEXT,
    tags TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    ingested_at TEXT,
    deprecated INTEGER DEFAULT 0,
    expires_at TEXT,
    version INTEGER DEFAULT 1,
    last_used_at TEXT,
    confidence INTEGER DEFAULT 3,
    has_content INTEGER DEFAULT 0,
    has_summary INTEGER DEFAULT 0,
    word_count INTEGER,
    has_embedding INTEGER DEFAULT 0
);
```

**Acceptance criteria:**
- [ ] `python3 N5/scripts/content_ingest.py /path/to/article.md --type article` creates DB record
- [ ] Script auto-detects type from file location if `--type` not specified
- [ ] `--dry-run` shows what would happen without DB write
- [ ] `--move` relocates file to canonical path
- [ ] Logs to `N5/runtime/runs/content-ingest/`
- [ ] Handles duplicate detection (same `source_file_path` = skip or update)

**When complete:**
```bash
python3 N5/scripts/build_orchestrator_v2.py complete --project content-library-v4 --worker worker_ingest_script
```

---

### Worker 2: `worker_backfill` (Data Migration)

**Component:** data_migration  
**Estimated time:** 1 hour  
**Output:** `N5/scripts/content_backfill.py`
**Depends on:** `worker_ingest_script`

**Task:**
Create and run a backfill script that registers all existing content files in the database:

```bash
python3 N5/scripts/content_backfill.py --dry-run  # Preview
python3 N5/scripts/content_backfill.py            # Execute
```

**Requirements:**
1. Scan `Knowledge/content-library/` recursively for all content files
2. For each file, check if a DB record exists (by `source_file_path`)
3. If missing, call ingest logic to create record
4. Special handling for V's authored content:
   - Files in `Knowledge/content-library/articles/vrijen/` get tag `vrijen-authored`
5. Generate report showing:
   - Files scanned
   - Records created
   - Records skipped (already exist)
   - Counts by `content_type`
6. Idempotent: Running twice should produce no duplicates

**Current content to backfill:**
```
Knowledge/content-library/
├── articles/
│   ├── Capital in the 22nd Century :: philiptrammell.substack.com.md
│   ├── Recursive Language Models :: www.k-a.in.md
│   ├── Secret History #1- How Power Works...md
│   ├── gamma.app :: gamma.app.md
│   ├── x.com :: x.com.md
│   └── vrijen/
│       ├── corporate-resume-windmills.md      # Tag: vrijen-authored
│       ├── moneyball-for-hiring.md            # Tag: vrijen-authored (stub file)
│       └── talent-agent-economy.md            # Tag: vrijen-authored
├── decks/     (empty)
├── papers/    (empty)
├── books/     (empty)
└── frameworks/ (empty)
```

**Acceptance criteria:**
- [ ] All 8 articles have DB records after running
- [ ] V's Medium articles have tag `vrijen-authored`
- [ ] Backfill report shows: 8 scanned, 8 created (or 0 if re-run)
- [ ] Running twice produces no duplicates
- [ ] Report saved to `N5/builds/content-library-v4/backfill_report.json`

**When complete:**
```bash
python3 N5/scripts/build_orchestrator_v2.py complete --project content-library-v4 --worker worker_backfill
```

---

### Worker 3: `worker_cli_upgrade` (CLI Interface)

**Component:** cli_interface  
**Estimated time:** 2 hours  
**Output:** `N5/scripts/content_library.py` (upgrade existing)
**Depends on:** `worker_ingest_script`

**Task:**
Upgrade the existing CLI at `N5/scripts/content_library.py` to support new functionality:

**New subcommands to add:**
```bash
# Ingest a file
python3 N5/scripts/content_library.py ingest /path/to/file.md --type article

# Run backfill sync
python3 N5/scripts/content_library.py sync

# List content types with counts
python3 N5/scripts/content_library.py list-types

# Search with type filter
python3 N5/scripts/content_library.py search --query "RLM" --type article
```

**Existing commands to preserve:**
- `add` — Add a link/snippet (keep working)
- `quick-add` — Quick add (keep working)
- `stats` — Show stats (upgrade to show new content_type breakdown)
- `search` — Search (add `--type` filter)

**Implementation notes:**
1. `ingest` subcommand should call `content_ingest.py` (don't duplicate logic)
2. `sync` subcommand should call `content_backfill.py`
3. `list-types` is a simple query: `SELECT content_type, COUNT(*) FROM items GROUP BY content_type`
4. `search --type X` adds `WHERE content_type = ?` to existing search query

**Current CLI for reference:** `file 'N5/scripts/content_library.py'`

**Acceptance criteria:**
- [ ] `python3 N5/scripts/content_library.py list-types` shows all content_type counts
- [ ] `python3 N5/scripts/content_library.py search --type article` filters correctly
- [ ] `python3 N5/scripts/content_library.py ingest /path/to/file.md` works
- [ ] `python3 N5/scripts/content_library.py sync` runs backfill
- [ ] Existing `add`, `quick-add`, `stats` commands still work
- [ ] `--help` updated with new commands

**When complete:**
```bash
python3 N5/scripts/build_orchestrator_v2.py complete --project content-library-v4 --worker worker_cli_upgrade
```

---

## Execution Order

```
worker_ingest_script (2h)
         │
         ├──────────────┬──────────────┐
         ▼              ▼              │
worker_backfill (1h)  worker_cli_upgrade (2h)
```

Execute `worker_ingest_script` first. Then `worker_backfill` and `worker_cli_upgrade` can run in parallel (or sequence, your choice).

---

## Completion Checklist

After all three workers are done:

1. [ ] Run `python3 N5/scripts/build_orchestrator_v2.py status --project content-library-v4` to verify Wave 2 complete
2. [ ] Test the full flow: `python3 N5/scripts/content_library.py list-types` should show articles
3. [ ] Report back: "Wave 2 complete. Ready for Wave 3."

Wave 3 workers (`worker_semantic_memory`, `worker_auto_ingest_hook`) will be spawned separately.

---

## Reference Files

- **Build plan:** `file 'N5/builds/content-library-v4/plan.json'`
- **Wave 1 manifest:** `file 'N5/builds/content-library-v4/move_manifest.json'`
- **Migration script:** `file 'N5/scripts/migrations/content_library_v4_schema.py'`
- **Current CLI:** `file 'N5/scripts/content_library.py'`
- **Database:** `file 'N5/data/content_library.db'`
- **Content location:** `file 'Knowledge/content-library/'`

