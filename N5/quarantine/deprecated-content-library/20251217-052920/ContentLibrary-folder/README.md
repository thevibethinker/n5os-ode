---
created: 2025-12-02
last_edited: 2025-12-02
version: 3.0
---

# Content Library v3

Unified system for managing **all content handles and assets**: links, snippets, articles, decks, social posts, podcasts, videos, books, papers, frameworks, quotes, and more.

Content Library v3 replaces the previous split between:

- **N5 Links & Snippets Library** – `file 'N5/data/content_library.db'`  
  Calendly links, trial codes, bios, product URLs, etc.
- **Personal Content Library** – `file 'Personal/Knowledge/ContentLibrary/content-library.db'`  
  Articles, decks, social posts, podcasts, long-form references.

Both are now merged into a **single unified database and API**.

- **Database (canonical):** `file 'Personal/Knowledge/ContentLibrary/content-library-v3.db'`  
- **Content files:** `file 'Personal/Knowledge/ContentLibrary/content/*.md'`  
- **CLI:** `file 'Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py'`

All examples below assume the full path:

```bash
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py <command> [options]
```

---

## 1. Mental Model

### 1.1 One Library, Multiple Views

Everything is an **item** with:

- An `id` (stable slug)
- An `item_type` (what kind of thing it is)
- Optional **content** (inline) and/or **asset files** (full text in `content/*.md`)
- **Topics** (controlled vocabulary: e.g. `AI`, `career`, `sales`)
- **Tags** (free-form `key=value` pairs for operational filtering)

You can think of v3 as:

> "A single place where all links, snippets, and reference content live, with one search surface and one API."

### 1.2 Handle vs Asset

- **Handles** – lightweight items used in operations and communications
  - Examples: `trial_code_general`, `vrijen_calendly_general`, `vrijen_bio_short`
  - Typically `item_type = link` or `snippet`
  - Often have tags like `category=trial`, `audience=founders`, `channel=email`

- **Assets** – heavier reference content with stored full text
  - Examples: articles, decks, long-form social posts, podcasts, videos
  - Typically have a `content_path` pointing to a `.md` file under `content/`
  - Can have extracted blocks and topics layered on later

Both are stored in the same `items` table.

---

## 2. Schema Overview

High-level shape of the unified schema (see `file 'N5/builds/content-library-v3/CONTENT_LIBRARY_V3_ARCHITECTURE.md'` for the full SQL):

### 2.1 Core Tables

- **`items`** – one row per content item
  - Identity: `id`, `item_type`, `title`
  - Content: `url`, `content`, `content_path`, `summary`, `summary_path`, `word_count`
  - Provenance: `source_type` (`created | discovered | manual | migration`), `platform`, `author`
  - Lifecycle: `created_at`, `updated_at`, `deprecated`, `expires_at`, `last_used_at`, `version`
  - Quality: `confidence`, `has_content`, `has_summary`
  - Metadata: `notes`, `source` (`n5_links | personal_cl | new`)

- **`tags`** – key/value attributes for operational filtering
  - `item_id`, `tag_key`, `tag_value`
  - Examples: `category=trial`, `audience=founders`, `channel=email`, `entity=careerspan`

- **`topics` / `item_topics`** – controlled vocabulary + many‑to‑many link
  - Topics are things like `AI`, `manager_skills`, `sales`, `self-advocacy`.

- **`blocks` / block_* tables** – optional extracted blocks for rich assets
  - Used by meeting/content workflows to store B01/B02-style chunks.

You rarely need to touch SQL directly; the `ContentLibraryV3` Python class and CLI cover common operations.

---

## 3. Item Types

Supported `item_type` values (not exhaustive):

| Type        | Description                          | Typical Use Case                              |
|-------------|--------------------------------------|-----------------------------------------------|
| `link`      | URL pointer                          | Calendly links, product URLs, deck URLs       |
| `snippet`   | Reusable text                        | Bios, email boilerplate, micro-copy           |
| `article`   | Long-form written content            | Articles, blog posts, long guides             |
| `deck`      | Presentations                        | Gamma/Slides decks, pitch decks               |
| `social-post` | Social media posts                 | LinkedIn threads, X/Twitter threads           |
| `podcast`   | Audio content                        | Podcast episodes                              |
| `video`     | Video content                        | Loom/YouTube, recorded talks                  |
| `book`      | Book reference                       | Reading lists, references                     |
| `paper`     | Research paper                       | Academic or practitioner papers               |
| `framework` | Mental model / framework             | Career frameworks, decision frameworks        |
| `quote`     | Notable quote                        | Quoted insight to reuse                       |
| `resource`  | General resource                     | Tools, services, checklists                   |
| `newsletter`| Newsletter issues                    | Recurring content sources                     |
| `case-study`| Case studies                         | Success stories, examples                     |

---

## 4. CLI Usage (All Commands)

All commands use the same entrypoint:

```bash
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py <command> [options]
```

### 4.1 `search` – Find Items

```bash
# Text search across titles, content, and URLs
python3 .../content_library_v3.py search --query "calendly"

# Filter by type
python3 .../content_library_v3.py search --type link

# Filter by topic
python3 .../content_library_v3.py search --topic AI --topic "career design"

# Filter by tags (key=value)
python3 .../content_library_v3.py search \
  --tag "category=scheduling" \
  --tag "audience=founders"

# Include deprecated items
python3 .../content_library_v3.py search --query "trial" --include-deprecated
```

Key flags:

- `--query, -q` – free‑text search over title/content/url
- `--type, -t` – `item_type` filter
- `--tag` – repeatable `key=value` filters
- `--topic` – repeatable topic names
- `--include-deprecated` – include items where `deprecated=1`
- `--limit` – max results (default 50)

Results are printed as JSON.

### 4.2 `get` – Fetch a Single Item

```bash
python3 .../content_library_v3.py get trial_code_general
```

If the ID exists, the item (including tags + topics) is printed as JSON. Missing IDs return an error JSON and exit code 1.

### 4.3 `add` – Create a New Item (Handle or Simple Asset)

```bash
# Add a link handle
python3 .../content_library_v3.py add \
  --id trial_code_general \
  --type link \
  --title "Careerspan trial link (general)" \
  --url "https://..." \
  --tag "category=trial" \
  --tag "audience=founders" \
  --tag "channel=email" \
  --notes "Primary trial link; safe to send broadly."

# Add a reusable snippet
python3 .../content_library_v3.py add \
  --id vrijen_bio_short \
  --type snippet \
  --title "Vrijen Bio (short)" \
  --content "Founder of Careerspan. Builder of N5 OS." \
  --tag "purpose=bio" \
  --tag "audience=general" \
  --tag "entity=vrijen"
```

Notes:

- `--type` maps to `item_type` in the DB.
- `--tag` accepts `key=value` and can be passed multiple times.
- `--topic` can be used to attach topics at creation time.

### 4.4 `ingest` – Add a Full-Text Asset

Use when you want the **full content** stored under `content/*.md` and linked to the item.

```bash
python3 .../content_library_v3.py ingest \
  --url "https://example.com/important-article" \
  --type article \
  --title "Important Article" \
  --source-type discovered \
  --tag "category=reference" \
  --topic "career" \
  --topic "management"
```

This will:

1. Download the URL (raw HTML/text).  
2. Store it as `content/<generated-id>.md`.  
3. Create an `items` row with `content_path` pointing at that file.  
4. Set `has_content=1` and `word_count`.

### 4.5 `update` – Change Fields

```bash
python3 .../content_library_v3.py update trial_code_general \
  --title "Careerspan trial link (general, updated)" \
  --url "https://new-url" \
  --notes "Updated 2025-12-02"
```

Allowed fields via CLI: `title`, `url`, `content`, `notes`.  
`updated_at` is automatically set.

### 4.6 `deprecate` – Mark Items as No Longer Active

```bash
python3 .../content_library_v3.py deprecate old_pitch_deck
```

Sets `deprecated=1` for the item. Consumers can choose whether to ignore deprecated entries by default.

### 4.7 `list` – Lightweight Listing

```bash
# Default: first 20 items (all types)
python3 .../content_library_v3.py list

# Only links
python3 .../content_library_v3.py list --type link --limit 100
```

This is a lightweight wrapper over `search` that prints one line per item:

```text
[link] trial_code_general: Careerspan trial link (general)
```

### 4.8 `export` – Dump Items as JSON or Markdown

```bash
# Export all items as JSON
python3 .../content_library_v3.py export --format json > /tmp/content-library.json

# Export only articles as Markdown
python3 .../content_library_v3.py export --type article --format markdown > /tmp/articles.md
```

### 4.9 `stats` – Library Statistics

```bash
python3 .../content_library_v3.py stats
```

Example output (truncated):

```json
{
  "total": 83,
  "by_type": {
    "link": 67,
    "article": 10,
    "social-post": 3
  },
  "by_source": {
    "n5_links": 67,
    "personal_cl": 16,
    "new": 0
  },
  "topics": 24,
  "tags": 180,
  "deprecated": 2
}
```

### 4.10 `lint` – Quality Checks

```bash
python3 .../content_library_v3.py lint
```

Current checks:

- JS-only fallback shells (e.g., broken X/Twitter captures: "JavaScript is not available …")
- Missing `content_path` files for items that claim to have stored content

If issues are found, the command prints a list and exits with non‑zero status.

For a broader scan across `Articles/` and other locations, also use:  
`file 'N5/scripts/lint_js_shell_tweets.py'`.

---

## 5. Python API Examples

Import path (from anywhere on the machine):

```python
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')

from content_library_v3 import ContentLibraryV3

lib = ContentLibraryV3()
```

### 5.1 Search

```python
# Simple text search
items = lib.search(query="calendly")

# Filter by type and topic
ai_articles = lib.search(
    item_type="article",
    topics=["AI"],
)

# Filter by tags
trial_links = lib.search(
    tags={"category": "trial", "audience": "founders"},
)
```

### 5.2 Get and Add

```python
# Get by ID
item = lib.get("trial_code_general")
if item:
    print(item["url"])

# Add a new link
lib.add(
    id="careerspan_homepage",
    item_type="link",
    title="Careerspan website",
    url="https://careerspan.ai",  # example
    tags={"category": "website", "entity": "careerspan"},
    notes="Main marketing site",
)
```

### 5.3 Update and Deprecate

```python
# Update an item
lib.update(
    "trial_code_general",
    url="https://new-trial-url",
    notes="Updated trial link after pricing change",
)

# Deprecate an item
lib.deprecate("old_trial_code")
```

### 5.4 Mark Usage and Stats

```python
# Mark that an item was used (e.g., inserted into an email)
lib.mark_used("trial_code_general")

# Inspect stats
stats = lib.stats()
print(stats["by_type"])
```

### 5.5 Ingest Programmatically

```python
item = lib.ingest(
    url="https://example.com/article", 
    item_type="article",
    title="Example Article",
    source_type="discovered",
    tags={"category": "reference"},
    topics=["career", "management"],
)
print(item["id"], item["content_path"])
```

### 5.6 Export

```python
export = lib.export(item_type="link", fmt="json")
print(export.count, "links exported")
print(export.payload[:500])
```

---

## 6. Ingest Workflow for New Content

### 6.1 Starting from a URL

1. Decide whether you want a **handle** or a full **asset**:
   - If you just need a reusable link → use `add` with `item_type=link`.
   - If you want the full text available for downstream analysis → use `ingest`.
2. Tag for retrieval:
   - At minimum: `category`, `audience`, `entity`.
3. Optionally, assign topics that will matter for search.

Example (article with full text):

```bash
python3 .../content_library_v3.py ingest \
  --url "https://example.com/career-framework" \
  --type article \
  --title "Career framework" \
  --source-type discovered \
  --tag "category=framework" \
  --tag "audience=managers" \
  --topic "career" \
  --topic "management"
```

### 6.2 Special Handling: JS-Heavy Social Sites (X/Twitter)

When capturing X/Twitter content:

1. **Do not ingest raw JS fallback pages.** If the page says "JavaScript is not available" or similar, treat it as broken.
2. Use an API-aware path (e.g. `tool x_search`) or a real browser view to copy the **actual tweet text**.
3. Create an item with `item_type="social-post"` and `platform="twitter"`:

```python
lib.add(
    id="founder-errors-thread", 
    item_type="social-post",
    title="Founder errors thread",
    url="https://x.com/...",
    content="(actual thread text here)",
    platform="twitter",
    tags={"category": "reference", "channel": "social"},
)
```

4. Run `lint` periodically to catch any accidental JS-shell content.

---

## 7. Migration Notes (v2 → v3)

- **Sources:**
  - `n5_links` – rows migrated from `N5/data/content_library.db` (links & snippets).
  - `personal_cl` – rows migrated from `Personal/Knowledge/ContentLibrary/content-library.db` (articles, decks, etc.).
  - `new` – items created directly in v3 after migration.
- **ID collisions:**
  - If both old systems had the same ID, the v3 migration prefixes with `n5_` or `pcl_` as needed.
- **Old databases:**
  - Kept as read-only migration artifacts until final cutover/archive.
- **Downstream systems:**
  - N5 scripts that previously queried `N5/data/content_library.db` now use v3 via updated helpers and/or wrappers.

For the full architecture and migration plan, see:  
`file 'N5/builds/content-library-v3/CONTENT_LIBRARY_V3_ARCHITECTURE.md'`.

---

## 8. Maintenance & Operations

### 8.1 Regular Checks

```bash
# Stats overview
python3 .../content_library_v3.py stats

# Lint for JS shells and missing content files
python3 .../content_library_v3.py lint
```

Use these in:

- Periodic maintenance scripts
- Pre‑deployment or pre‑cutover checks

### 8.2 Tag & Topic Conventions (Recommended)

Common tag keys:

- `category` – `trial`, `scheduling`, `website`, `reference`, `framework`, `resource`, `deck`
- `audience` – `founders`, `investors`, `job_seekers`, `managers`, `general`
- `entity` – `vrijen`, `careerspan`, `n5`, `zo_computer`
- `channel` – `email`, `linkedin`, `docs`, `social`
- `status` – `active`, `deprecated`, `experimental`

Topics are higher-level themes (e.g. `AI`, `career`, `performance_reviews`) and should be reused rather than constantly inventing new synonyms.

### 8.3 Related Files and Scripts

- Content Library v3 CLI: `file 'Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py'`
- V3 architecture spec: `file 'N5/builds/content-library-v3/CONTENT_LIBRARY_V3_ARCHITECTURE.md'`
- N5 wrappers & integrations: `file 'N5/scripts/content_library.py'`, `file 'N5/scripts/content_library_db.py'` (v3-aware after cutover)
- Legacy ingest helpers (pre‑v3): `file 'Personal/Knowledge/ContentLibrary/scripts/ingest.py'` and friends
- V3 cutover helper: `file 'N5/scripts/content_library_v3_cutover.py'`
- JS shell lint (cross‑system): `file 'N5/scripts/lint_js_shell_tweets.py'`

---

*Content Library v3 · Unified 2025-12-02*

