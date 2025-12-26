---
created: 2025-12-02
last_edited: 2025-12-02
version: 1
---
# Worker 5: Documentation Updates

**Orchestrator:** con_jYGYNfcv76UTmolk  
**Task ID:** W5-DOCS  
**Estimated Time:** 30 minutes  
**Dependencies:** Workers 1-4 (all implementation complete)

---

## Mission

Create updated documentation for the unified Content Library v3, replacing the old fragmented docs.

---

## Context

Documentation is currently split between:
- `Documents/System/guides/content-library-system.md` – N5 links/snippets
- `Documents/System/guides/content-library-quickstart.md` – Quick reference
- `Personal/Knowledge/ContentLibrary/README.md` – Personal CL
- `Personal/Knowledge/Architecture/specs/systems/content_library_integration.md` – Architecture spec

All need to be unified into coherent v3 documentation.

---

## Dependencies

- All implementation workers complete (W1-W4)
- Verified working system

---

## Deliverables

1. `Personal/Knowledge/ContentLibrary/README.md.new` – Main v3 documentation
2. `Documents/System/guides/content-library-system.md.new` – System guide (v3)
3. `Documents/System/guides/content-library-quickstart.md.new` – Quick reference (v3)
4. `Personal/Knowledge/Architecture/specs/systems/content_library_integration.md.new` – Architecture spec (v3)
5. `N5/scripts/content_library_v3_cutover.py` usage + rollback procedure documented in the above where relevant

---

## Requirements

### README.md.new (Main Docs)

Should include:
- Overview of unified Content Library v3
- Database location and schema overview
- CLI usage examples for ALL commands
- Python API examples
- Item types reference table
- Ingest workflow for new content
- Migration notes (what was merged)
- Maintenance (lint, stats)
- Related files and scripts

### content-library-system.md.new (System Guide)

Should include:
- Full architecture explanation
- Schema documentation
- CLI reference (all commands)
- Integration patterns for workflows
- Tag and topic conventions
- Best practices
- **Cutover + rollback instructions using `N5/scripts/content_library_v3_cutover.py`**

### content-library-quickstart.md.new (Quick Reference)

Should include:
- One-liner examples for common tasks
- Search patterns
- Add item patterns
- Ingest patterns
- Lookup patterns

### Architecture Spec Update

Should include:
- Database location
- Integration points
- Query patterns table
- Migration history

---

## Implementation Guide

### README.md.new Template

```markdown
---
created: 2025-12-02
last_edited: 2025-12-02
version: 3.0
---

# Content Library v3

Unified system for managing ALL content: links, snippets, articles, decks, social posts, and more.

## Overview

Content Library v3 merges the previous two systems:
- **N5 Links & Snippets** (67 items) – Calendly links, trial codes, bio snippets
- **Personal Content Library** (16 items) – Articles, decks, social posts

**Database:** `Personal/Knowledge/ContentLibrary/content-library-v3.db`
**CLI:** `Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py`

## Item Types

| Type | Description | Example |
|------|-------------|---------|
| link | URL pointer | Calendly scheduling link |
| snippet | Reusable text | Bio, marketing copy |
| article | Written content | Blog post, news article |
| deck | Presentation | Gamma deck, slides |
| social-post | Social media | Twitter thread |
| podcast | Audio content | Episode reference |
| video | Video content | YouTube, Loom |
| book | Book reference | Reading list item |
| paper | Research paper | Academic reference |
| framework | Mental model | Decision framework |
| quote | Notable quote | Extracted insight |
| resource | General resource | Tool, service |

## Quick Start

### Search
\`\`\`bash
# Text search
python3 content_library_v3.py search --query "calendly"

# By type
python3 content_library_v3.py search --type article

# By topic
python3 content_library_v3.py search --topic "AI"

# By tag
python3 content_library_v3.py search --tag category=scheduling
\`\`\`

### Add Items
\`\`\`bash
# Add link
python3 content_library_v3.py add --id my_link --type link --title "My Link" --url "https://..."

# Add snippet
python3 content_library_v3.py add --id my_bio --type snippet --title "Bio" --content "..."
\`\`\`

### Ingest Content
\`\`\`bash
# Ingest article
python3 ingest.py "https://url.com" "Title" --type article --source discovered --topics AI productivity
\`\`\`

### Get Item
\`\`\`bash
python3 content_library_v3.py get trial_code_general
\`\`\`

### Stats
\`\`\`bash
python3 content_library_v3.py stats
\`\`\`

### Lint (Quality Check)
\`\`\`bash
python3 content_library_v3.py lint
\`\`\`

## Python API

\`\`\`python
import sys
sys.path.insert(0, '/home/workspace/Personal/Knowledge/ContentLibrary/scripts')
from content_library_v3 import ContentLibraryV3

lib = ContentLibraryV3()

# Search
items = lib.search(query="calendly")
items = lib.search(item_type="article", topics=["AI"])

# Get
item = lib.get("trial_code_general")

# Add
lib.add(id="new_link", item_type="link", title="New", url="https://...")

# Stats
stats = lib.stats()
\`\`\`

## X/Twitter Content Protocol

When ingesting X/Twitter content:
1. Use `x_search` tool to get actual tweet text (not webpage capture)
2. Create item with `item_type="social-post"` and `platform="twitter"`
3. Store actual content, not JS fallback shell
4. Run `lint` to detect any JS shell content

## Migration Notes

- **Source tracking:** Items have `source` field indicating origin:
  - `n5_links` – Migrated from N5/data/content_library.db
  - `personal_cl` – Migrated from Personal CL
  - `new` – Added after v3 migration
- **ID collisions:** Prefixed with `n5_` or `pcl_` if collision detected

## File Locations

- Database: `Personal/Knowledge/ContentLibrary/content-library-v3.db`
- CLI: `Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py`
- Ingest: `Personal/Knowledge/ContentLibrary/scripts/ingest.py`
- Content files: `Personal/Knowledge/ContentLibrary/content/*.md`
- Lint: `N5/scripts/lint_content_library.py`

## See Also

- `file 'Documents/System/guides/content-library-system.md'` – Full system guide
- `file 'Documents/System/guides/content-library-quickstart.md'` – Quick reference
- `file 'Personal/Knowledge/Architecture/specs/systems/content_library_integration.md'` – Architecture

---
*Content Library v3 | Unified 2025-12-02*
```

---

## Testing

After creating docs:

```bash
# Verify all referenced commands work
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py stats
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py lint
python3 /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py search --query test

# Verify file paths in docs are correct
ls /home/workspace/Personal/Knowledge/ContentLibrary/content-library-v3.db
ls /home/workspace/Personal/Knowledge/ContentLibrary/scripts/content_library_v3.py
```

---

## Report Back

When complete, report:
1. ✅ List of `.new` doc files created
2. ✅ All example commands verified working
3. ✅ All file paths verified correct
4. ✅ Docs are internally consistent
5. ✅ Ready for cutover

---

**Orchestrator Contact:** con_jYGYNfcv76UTmolk  
**Created:** 2025-12-02 22:06 ET


