---
description: |
  Search content library by keyword or tags.
  Returns matching links and snippets.
tags:
  - content
  - search
  - knowledge
---

# content-search

Search the content library for links and snippets.

## Usage

```bash
# Search by keyword
python3 N5/scripts/n5_content_library.py search --query "bio"

# Search by type
python3 N5/scripts/n5_content_library.py search --type link

# Search by tags
python3 N5/scripts/n5_content_library.py search --tags '{"purpose": ["bio"], "audience": ["investors"]}'
```

## Search Options

- `--query`: Text search in title/content
- `--type`: Filter by "link" or "snippet"
- `--tags`: JSON object with tag filters
- `--include-deprecated`: Include deprecated items

See: file 'Documents/CONTENT_LIBRARY.md'
