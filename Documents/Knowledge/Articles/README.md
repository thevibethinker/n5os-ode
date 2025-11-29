---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Articles Folder – Legacy (Non-SSOT)

This `Documents/Knowledge/Articles/` folder is no longer the system of record (SSOT) for article-like content.

Canonical locations:
- **Canon (durable narratives):** `Personal/Knowledge/Canon/**`
- **Content Library (reference material):** `Personal/Knowledge/ContentLibrary/content/`

## Migration

Existing files in this folder have been imported using:

```bash
python3 N5/scripts/knowledge_import_canon_contentlibrary.py --execute
```

Going forward, new article-like content should be stored directly in:
- `Personal/Knowledge/Canon/**` for core narratives, or
- `Personal/Knowledge/ContentLibrary/content/` for reference articles.

If a new file is temporarily placed here, re-run the import script above to normalize it into the new knowledge architecture.

