---
description: |
  Add link or snippet to content library with auto-classification.
  Automatically tags by purpose, audience, and tone.
tags:
  - content
  - knowledge
  - productivity
---

# content-add

Add a new item (link or snippet) to the content library.

## Usage

```bash
# Add a link
python3 N5/scripts/n5_content_library.py add link "Title" --url "https://example.com" --content "Description"

# Add a snippet
python3 N5/scripts/n5_content_library.py add snippet "Bio - Concise" --content "Your bio text here"
```

## Arguments

- `type`: "link" or "snippet"
- `title`: Item title
- `--url`: URL (required for links)
- `--content`: Description or text content
- `--notes`: Optional notes
- `--deprecate`: Mark as deprecated

## Auto-Classification

System automatically tags by:
- **Purpose**: bio, pitch, resource, education, scheduling, etc.
- **Audience**: founders, investors, customers, team, etc.
- **Tone**: concise, detailed, formal, casual, etc.

See: file 'Documents/CONTENT_LIBRARY.md'
