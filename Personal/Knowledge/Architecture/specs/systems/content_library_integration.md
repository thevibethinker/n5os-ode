---
created: 2025-12-02
last_edited: 2025-12-02
version: 3.0
grade: knowledge
domain: systems
stability: time_bound
form: spec
---

# Content Library v3 Integration

## 1. Overview

Content Library v3 is the **single, unified content database** for:

- Operational handles (links + snippets) used by N5 workflows.
- Curated reference content (articles, decks, social posts, podcasts, videos, books, papers, frameworks, quotes) in the personal knowledge layer.

This spec describes how other systems integrate with v3.

- **Canonical DB:** `file 'Personal/Knowledge/ContentLibrary/content-library-v3.db'`  
- **Primary CLI/API:** `file 'Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py'`  
- **Architecture:** `file 'N5/builds/content-library-v3/CONTENT_LIBRARY_V3_ARCHITECTURE.md'`

Old systems (JSON files and split SQLite DBs) are considered migration artifacts only.

---

## 2. Database Location & Shape

### 2.1 Location

```text
/home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db
```

This path is treated as **canonical**. N5 scripts and personal tools should depend on it directly or through v3-aware helpers.

### 2.2 High-Level Schema

The full schema is defined in `CONTENT_LIBRARY_V3_ARCHITECTURE.md`. At a high level:

- **`items`** — core content items
  - Identity: `id`, `item_type`, `title`
  - Content: `url`, `content`, `content_path`, `summary`, `summary_path`, `word_count`
  - Provenance: `source_type` (`created | discovered | manual | migration`), `platform`, `author`
  - Lifecycle: `created_at`, `updated_at`, `deprecated`, `expires_at`, `last_used_at`, `version`
  - Quality: `confidence`, `has_content`, `has_summary`
  - Metadata: `notes`, `source` (`n5_links | personal_cl | new`)

- **`tags`** — key/value attributes for operational selectors (`category`, `audience`, `entity`, `channel`, etc.).
- **`topics` / `item_topics`** — controlled vocabulary and junction table.
- **`blocks` / `block_topics` / `knowledge_refs` / `relationships`** — used by richer content/knowledge flows (optional for basic integrations).

Most integrations should use the **Python class** rather than touching SQL directly.

---

## 3. Integration Points

### 3.1 N5 Communication & CRM Workflows

Examples (non-exhaustive):

- Follow-up email generation (trial links, calendars, decks).
- Email composer and corrections pipelines.
- Meeting intelligence pipelines that resolve commitments ("I'll send you X") into concrete resources.
- Voice/transcript-driven flows that insert links or references into generated text.

Typical pattern:

```python
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')

from content_library_v3 import ContentLibraryV3

lib = ContentLibraryV3()

# Example: resolve a trial link
trial_candidates = lib.search(tags={"category": "trial", "audience": "founders"})
trial_link = choose_best(trial_candidates)  # selection logic in caller
```

Downstream helpers in `N5/scripts/content_library.py` and `N5/scripts/content_library_db.py` (after v3 cutover) wrap this API for convenience.

### 3.2 Personal Knowledge Workflows

Scripts under `Personal/Knowledge/ContentLibrary/scripts/` (ingest, enhance, summarize, content_to_knowledge) integrate with v3 by:

- Using `content_library_v3.py` as the **single** API surface.
- Storing full-text assets under `content/*.md` and registering them in `items.content_path`.
- Using `topics`/`tags` for retrieval across reflections, documents & media, and follow-up systems.

### 3.3 Documents & Media / Knowledge Systems

Richer pipelines may:

- Extract blocks from assets (e.g., B01/B02-style chunks) into `blocks`.
- Attach topics at the block level via `block_topics`.
- Track promotion of blocks into other knowledge systems via `knowledge_refs` (e.g., when a block becomes a knowledge card).
- Record relationships between items (e.g., a deck derived from an article) in `relationships`.

These integrations should treat v3 as the **central hub** for content handles and assets.

---

## 4. Query Patterns

Common query patterns from the perspective of other systems:

| Scenario / Promise | Query Pattern (CLI) | Notes |
|--------------------|---------------------|-------|
| "I'll send you a trial link" | `search --type link --tag "category=trial" --tag "audience=founders"` | Returns one or more trial link handles; caller picks best. |
| "Here's my calendar" | `search --type link --tag "category=scheduling" --tag "entity=vrijen"` | Used by follow-up email generator and scheduling helpers. |
| "I'll send the pitch deck" | `search --type deck --tag "category=pitch"` | Decks may be links or assets with `content_path`. |
| "I'll share the article" | `search --type article --topic "career"` | Assets likely have `content_path` for downstream processing. |
| "Send the short bio" | `search --type snippet --tag "purpose=bio" --tag "entity=vrijen"` | Multiple bios may exist; caller chooses variant. |

CLI form (absolute path):

```bash
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py search ...
```

Programmatic form (Python):

```python
lib.search(item_type="link", tags={"category": "scheduling", "entity": "vrijen"})
```

Use **tags** for precise selectors and **topics** for thematic grouping.

---

## 5. Migration History

### 5.1 Pre-v2: JSON

Two independent JSON-based systems:

- `N5/prefs/communication/content-library.json` – links/snippets for communication workflows.
- `Personal/Knowledge/ContentLibrary/content-library.json` – early personal reference library.

### 5.2 v2: Split SQLite DBs

1. **N5 Links & Snippets DB**  
   - **Location:** `file 'N5/data/content_library.db'`  
   - Used by: email composer, follow-up generator, meeting intelligence.
   - Tables: `items`, `tags`.

2. **Personal Content Library DB**  
   - **Location:** `file 'Personal/Knowledge/ContentLibrary/content-library.db'`  
   - Used by: personal content curation and reference workflows.

These DBs coexisted but caused naming confusion (both called "Content Library").

### 5.3 v3: Unified Superset Schema

- **Location:** `file 'Personal/Knowledge/ContentLibrary/content-library-v3.db'`.
- **Schema:** Superset schema defined in `CONTENT_LIBRARY_V3_ARCHITECTURE.md` with:
  - Extended `items` table.
  - Shared `tags` and `topics` taxonomy.
  - Optional `blocks`, `knowledge_refs`, and `relationships` for rich assets.
- **Migration approach:** copy‑based, not in‑place.
  - Items from `N5/data/content_library.db` are inserted with `source='n5_links'`.
  - Items from `Personal/Knowledge/ContentLibrary/content-library.db` are inserted with `source='personal_cl'`.
  - New items created directly in v3 carry `source='new'`.
  - ID collisions are resolved by prefixing (`n5_` / `pcl_`) when necessary.

Old DBs remain available for inspection and rollback but are **not** considered canonical once v3 is fully validated.

---

## 6. Cutover Strategy

Cutover of N5 and personal scripts to v3 is handled by:

- `file 'N5/scripts/content_library_v3_cutover.py'` — promotes `.py.new` v3-aware scripts into place (with `.bak` backups) after migration is validated.

Recommended integration posture:

1. Develop and test new v3-aware scripts as `*.py.new` alongside existing ones.
2. Use `content_library_v3_cutover.py` in dry-run mode to verify planned moves.
3. Run with `--execute` when ready for cutover.
4. Use `.bak` backups or git to roll back if needed.

This keeps migration copy‑based and minimizes the risk of accidental data loss.

---

## 7. Tag & Topic Conventions (Integration Contract)

To keep integrations stable:

- Treat the following **tag keys** as stable:
  - `category`, `audience`, `entity`, `channel`, `status`.
- Treat **topics** as a curated vocabulary; integrations should not rely on any single topic name but can filter on broad themes (e.g. `AI`, `career`, `sales`).

Example contract for a follow-up generator:

- To find trial links, use: `tags={"category": "trial"}` plus `audience` where relevant.
- To find scheduling links, use: `tags={"category": "scheduling"}` and optionally `entity`.
- To find short bios, use: `tags={"purpose": "bio", "entity": "vrijen"}`.

If tag conventions change, this spec and the v3 README should be updated first, then dependent workflows.

---

## 8. Implementation Notes

- Prefer using the **Python class** (`ContentLibraryV3`) or N5 wrapper helpers instead of writing SQL.
- Avoid direct writes to the DB outside of controlled paths (`add`, `ingest`, `update`, `deprecate`).
- Use `stats` and `lint` in system health checks and CI where possible.
- Treat `content/*.md` as human-readable, git-tracked SSOT for full-text assets.

---

*Content Library v3 Integration Spec · 2025-12-02*

