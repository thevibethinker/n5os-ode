---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Content Library & Block System v1

```yaml
capability_id: content-library-v1
name: "Content Library & Block System"
category: internal
status: active
confidence: high
last_verified: 2025-11-29
tags:
  - content
  - snippets
  - links
  - blocks
entry_points:
  - type: script
    id: "N5/scripts/content_library.py"
  - type: script
    id: "N5/scripts/content_library_db.py"
  - type: script
    id: "N5/scripts/b_block_parser.py"
  - type: script
    id: "N5/scripts/email_composer.py"
  - type: script
    id: "N5/scripts/auto_populate_content.py"
owner: "V"
```

## What This Does

The Content Library is the **central store for reusable links and text snippets** used across emails, documents, and social content. The block system (B‑blocks) provides a structured way to represent meeting and reflection outputs that can feed into those communication workflows.

Together they form a self‑feeding flywheel: blocks and meeting outputs are mined for reusable content, promoted into the content library, and then reused in follow‑ups, proposals, and other artifacts.

## How to Use It

### Manage content directly

From `/home/workspace`:

```bash
# Quick-add (auto-categorize)
python3 N5/scripts/content_library.py quick-add \
  --text "https://www.zo.computer/?promo=VATT50" \
  --title "Zo referral link"

# Manual add with tags
python3 N5/scripts/content_library.py add \
  --type link \
  --title "Zo Referral" \
  --url "https://www.zo.computer/?promo=VATT50" \
  --tags "purpose=referral,audience=founders"

# Search
python3 N5/scripts/content_library.py search --query "bio"
python3 N5/scripts/content_library.py search --tag "purpose=referral" --tag "audience=founders"

# Deprecate
python3 N5/scripts/content_library.py deprecate --id old_pitch --expires-at 2025-12-31
```

### Use in downstream workflows

Typical meeting‑to‑content flow:

```bash
# 1. Parse meeting transcript into B-blocks
python3 N5/scripts/b_block_parser.py /path/to/transcript.txt --output blocks.json

# 2. Generate follow-up email draft
python3 N5/scripts/email_composer.py \
  blocks.json \
  --recipient "Name" \
  --summary "Brief summary" \
  --output draft.txt

# 3. Auto-discover candidate snippets and links (dry-run)
python3 N5/scripts/auto_populate_content.py blocks.json --dry-run

# 4. If results look good, actually add them to the library
python3 N5/scripts/auto_populate_content.py blocks.json
```

The Follow‑Up Email Generator prompt and associated scripts query `content_library.db` to pull the correct scheduling links, bios, and resources into outgoing messages.

## Associated Files & Assets

### Databases & config

- `file 'N5/data/content_library.db'` – SQLite SSOT for content items (current implementation).
- `file 'N5/schemas/content_library.sql'` – Database schema.
- `file 'N5/prefs/communication/content-library.json'` – Earlier JSON‑based SSOT (now largely superseded but still relevant in docs/migration).
- `file 'N5/prefs/paths/knowledge_paths.yaml'` – Declares `content_library` root under `Personal/Knowledge/ContentLibrary`.

### Core scripts (library)

- `file 'N5/scripts/content_library_db.py'` – Low‑level DB CLI/API (add/get/list/search/deprecate).
- `file 'N5/scripts/content_library.py'` – Higher‑level CLI + helper routines, including `quick-add`, tagging, and touch‑tracking.
- `file 'N5/scripts/auto_populate_content.py'` – Mines B‑blocks and other sources for candidate entries and upserts them into the library.
- `file 'N5/scripts/email_composer.py'` – Uses `ContentLibrary` to assemble follow‑up emails with correct links and snippets.
- `file 'N5/scripts/n5_follow_up_email_generator.py'` – Higher‑level follow‑up generator that integrates content library lookups.

### Block system (B‑blocks)

- `file 'N5/prompts/blocks'` – Prompt files B01/B02/… that define block semantics (recap, commitments, action items, business context, etc.).
- `file 'N5/config/canonical_blocks.yaml'` – Canonical block registry, including references to `content_library` for certain flows.
- `file 'N5/scripts/b_block_parser.py'` – Parses meeting transcripts into structured B‑block JSON.
- `file 'N5/scripts/blocks/deliverables/blurb_generator.py'` – Uses block content and knowledge base to generate blurbs.

### System & docs

- `file 'Documents/System/guides/content-library-system.md'` – Primary system design guide.
- `file 'Documents/System/guides/content-library-quickstart.md'` – Quickstart and command cheatsheet.
- `file 'Documents/CONTENT_LIBRARY_SUMMARY.md'` – High‑level summary of capabilities.
- `file 'Personal/Knowledge/Architecture/specs/systems/content_library_integration.md'` – Architecture notes and integration patterns.

## Workflow

### Library lifecycle

```mermaid
flowchart TD
  A[Sources
  - Meetings (B-blocks)
  - Reflections
  - Manual entries] --> B[auto_populate_content.py
  + content_library.py quick-add]

  B --> C[content_library.db
  - items + tags + notes]

  C --> D[Downstream systems
  - follow-up email generator
  - deliverable generators
  - voice/knowledge tools]

  D --> E[Usage telemetry
  - mark_used
  - touch_count
  - last_used]

  E --> C
```

### B‑blocks interaction

1. Meeting and reflection transcripts are parsed into B‑blocks (e.g. recap, decisions, commitments, intel).
2. `auto_populate_content.py` scans blocks and suggests/creates content items (links/snippets) for the library.
3. Email and document generators (e.g. follow‑up generator, blurb generator) query `content_library.db` using tag filters and text search to pull relevant content.
4. `mark_used` / touch‑tracking updates help identify high‑value items and stale content.

## Notes / Gotchas

- **JSON vs DB:** Historical docs reference `content-library.json` as SSOT; the current production system uses `content_library.db` behind both `content_library.py` and `content_library_db.py`. When in doubt, inspect the DB.
- **Schema migrations:** The migration from JSON → DB is documented in `CONTENT_LIBRARY_MIGRATION_SUMMARY.md`; rerunning migration scripts or editing the DB schema directly should be treated as a trap‑door change.
- **Tag discipline is critical.** Retrieval quality depends heavily on consistent tags (`purpose`, `audience`, `tone`, `entity`, etc.); ad‑hoc tag values reduce the value of search.
- **Block registry coupling:** Changes to B‑block definitions (in prompts or canonical_blocks.yaml) can affect how auto‑populate and downstream workflows interpret content. Coordinate changes with meeting/reflection pipeline owners.

