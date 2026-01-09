---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_MWo2XMditqNfnjBM
---

# Auto-Ingest Saved Articles

## Rule Purpose

Automatically ingest articles saved via `save_webpage` into the Content Library system.

## Trigger

After using `save_webpage` to save an article.

## Instruction

After using `save_webpage` to save an article:

1. Run the content ingest script with `--move` to relocate the file:
   ```bash
   python3 N5/scripts/content_ingest.py "<saved_file_path>" --type article --move
   ```

2. This will:
   - Create a database record in `N5/data/content_library.db`
   - Move the file to `Knowledge/content-library/articles/`
   - Extract and store metadata (title, URL, tags)

3. Confirm to user: "Article ingested to Content Library and moved to `Knowledge/content-library/articles/`"

## Notes

- The `--move` flag handles relocation to the canonical path
- The ingest script is idempotent (won't duplicate if already exists)
- Source URL is preserved in the database record
- For V's authored content, add `--tags vrijen-authored`

## Manual Alternative

If the rule doesn't trigger automatically, users can manually run:
```bash
python3 N5/scripts/content_library.py ingest "<path_to_article.md>" --type article --move
```

