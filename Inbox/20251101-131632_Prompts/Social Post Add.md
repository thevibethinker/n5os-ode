---
description: 'Command: social-post-add'
tags:
- social-media
- content
- linkedin
tool: true
---
# Social Post: Add

Add new social media post to the tracking system.

## Quick Start

```bash
# Add post from file (auto-extracts title)
python3 N5/scripts/n5_social_post.py add /path/to/post.md \
    --platform linkedin \
    --status draft

# With custom title and tags
python3 N5/scripts/n5_social_post.py add /path/to/post.md \
    --platform linkedin \
    --status pending \
    --title "My Custom Title" \
    --tags "founder,startup,growth"

# Dry-run first
python3 N5/scripts/n5_social_post.py add /path/to/post.md \
    --platform linkedin \
    --dry-run
```

## Parameters

- `file` - Path to markdown file with post content
- `--platform` - Platform: linkedin, twitter, facebook, instagram
- `--status` - Initial status (default: draft) 
  - `draft` - Work in progress
  - `pending` - Ready for review
  - `submitted` - Already published
  - `archived` - Old content
  - `declined` - Rejected, won't publish
- `--title` - Custom title (auto-extracted if omitted)
- `--tags` - Comma-separated tags
- `--conversation-id` - Link to conversation where created
- `--source` - Source type (manual, generated, imported)
- `--dry-run` - Preview without making changes

## What it Does

1. Reads content from file
2. Generates unique ID and slug
3. Extracts/uses title
4. Counts words and characters
5. Creates file with 🔗 emoji prefix
6. Moves to correct platform/status folder
7. Adds record to registry (JSONL)

## File Naming

Format: `file 🔗_{YYYY-MM-DD-HHMM}_{platform}_{slug}.md`

Example: `file 🔗_2025-10-22-1630_linkedin_vulnerable-founder.md`

## See Also

- `file N5/commands/social-post-list.md` - List posts
- `file N5/commands/social-post-status.md` - Update status
- `file N5/docs/social-media-tracking-quickstart.md` - Full guide